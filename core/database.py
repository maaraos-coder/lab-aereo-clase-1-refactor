"""Infraestructura de datos y persistencia de la aplicación.

Este módulo conserva las consultas y estructuras existentes. La lógica académica
permanece en app.py y en los módulos de laboratorios.
"""
import datetime as dt
import hashlib
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
try:
    from supabase import create_client
except ImportError:
    create_client = None

from config.laboratorios import ACADEMIC_COURSES, COURSE_ID

ROOT = Path(__file__).resolve().parents[1]
ACTIVITY_DB = ROOT / "formative_responses.sqlite3"
SANTIAGO_TZ = ZoneInfo("America/Santiago")

def _activity_db():
    con=sqlite3.connect(ACTIVITY_DB)
    con.execute(
        """CREATE TABLE IF NOT EXISTS formative_responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
        student TEXT NOT NULL, stage INTEGER NOT NULL, question_key TEXT NOT NULL,
        question TEXT NOT NULL, answer TEXT NOT NULL, auto_level TEXT,
        feedback TEXT, teacher_level TEXT, auto_score REAL DEFAULT 0,
        max_score REAL DEFAULT 0, teacher_score REAL,
        teacher_note TEXT, UNIQUE(student,stage,question_key))"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS projection_state(
        id INTEGER PRIMARY KEY CHECK(id=1), stage INTEGER, question TEXT,
        answer TEXT, solution TEXT, show_answer INTEGER DEFAULT 0,
        show_solution INTEGER DEFAULT 0, updated_at TEXT)"""
    )
    con.execute(
        """INSERT OR IGNORE INTO projection_state
        (id,stage,question,answer,solution,show_answer,show_solution,updated_at)
        VALUES(1,NULL,'','','',0,0,'')"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS user_progress(
        user_key TEXT PRIMARY KEY, role TEXT NOT NULL, display_name TEXT NOT NULL,
        state_json TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL)"""
    )
    existing={row[1] for row in con.execute("PRAGMA table_info(formative_responses)")}
    for column,definition in (
        ("auto_score","REAL DEFAULT 0"),("max_score","REAL DEFAULT 0"),
        ("teacher_score","REAL"),("teacher_note","TEXT"),
    ):
        if column not in existing:
            con.execute(f"ALTER TABLE formative_responses ADD COLUMN {column} {definition}")
    con.commit()
    return con

@st.cache_resource
def _supabase():
    """Server-side Supabase client. The service key never reaches the browser."""
    if create_client is None:
        return None
    try:
        config=st.secrets["supabase"]
        # Supabase accepts both the legacy service_role JWT and the newer
        # server-side secret key. Keep backwards compatibility with existing
        # Streamlit Secrets without ever embedding a credential in the app.
        server_key=(
            config.get("service_role_key")
            or config.get("secret_key")
        )
        if not server_key:
            return None
        return create_client(
            str(config["url"]),
            str(server_key),
        )
    except (KeyError, FileNotFoundError, TypeError, ValueError):
        return None

def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def _parse_opening(value):
    if not value:
        return None
    return dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))

def _opening_label(value):
    opening=_parse_opening(value)
    if opening is None:
        return "Fecha por definir"
    return opening.astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y")

def _is_open(value):
    opening=_parse_opening(value)
    return opening is None or dt.datetime.now(dt.timezone.utc) >= opening.astimezone(dt.timezone.utc)

def _effective_opening(class_number, remote_value=None, fallback_value=None):
    """Use the corrected Lab 2 release date even if Supabase still has the old value."""
    if int(class_number or 0) == 2:
        return ACADEMIC_COURSES[0]["labs"][1]["opens_at"]
    return remote_value or fallback_value

def _remote_rows(table, **filters):
    client=_supabase()
    if client is None:
        return None
    query=client.table(table).select("*")
    for key,value in filters.items():
        query=query.eq(key,value)
    return query.execute().data or []

@st.cache_data(ttl=45, show_spinner=False)
def _course_classes(_client):
    """One shared publication query instead of repeating it throughout each rerun."""
    if _client is None:
        return []
    try:
        return (
            _client.table("classes").select("*")
            .eq("course_id", COURSE_ID).order("class_number").execute().data or []
        )
    except Exception:
        return []

def _clear_course_cache():
    _course_classes.clear()

def _class_row(class_id):
    return next((row for row in _course_classes(_supabase()) if row.get("id") == class_id), {})

def _register_user(user_key, role, name, rut="", email=""):
    client=_supabase()
    if client is None:
        return
    client.table("users").upsert({
        "user_key":user_key,"role":role,"display_name":name,
        "rut":rut or None,"email":email or None,"last_login_at":_now(),
    },on_conflict="user_key").execute()
    client.table("enrollments").upsert({
        "course_id":COURSE_ID,"user_key":user_key,"active":True,
    },on_conflict="course_id,user_key").execute()

def _make_user_key(role, name, identification=""):
    """Stable private identifier: responses do not depend only on the visible name."""
    source=f"{role}|{identification.strip().lower() or name.strip().lower()}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()

def _normalize_name(value):
    """Normalize names for a strict but accent/case-insensitive roster match."""
    value=unicodedata.normalize("NFKD",str(value or ""))
    value="".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(value.casefold().split())

def _normalize_identification(value):
    """Keep only letters and digits so formatted and unformatted RUTs match."""
    return re.sub(r"[^0-9a-z]","",str(value or "").casefold())

def _authorized_student(name, identification):
    client=_supabase()
    if client is None:
        return False,(
            "La conexión permanente no está configurada. Revisa en Streamlit "
            "los Secrets «supabase.url» y «supabase.service_role_key» "
            "(o «supabase.secret_key»)."
        )
    normalized_name=_normalize_name(name)
    normalized_id=_normalize_identification(identification)
    try:
        rows=(client.table("authorized_students").select("*")
              .eq("course_id",COURSE_ID)
              .eq("normalized_identification",normalized_id)
              .eq("active",True).limit(1).execute().data or [])
    except Exception as exc:
        message=str(exc).casefold()
        if "authorized_students" in message and (
            "does not exist" in message or "schema cache" in message
        ):
            return False,(
                "La tabla de acceso todavía no existe en Supabase. Ejecuta una "
                "sola vez el archivo «REPARACION_ACCESO_V29.sql»."
            )
        if "permission" in message or "row-level security" in message or "rls" in message:
            return False,(
                "Supabase rechazó la consulta de acceso. El Secret configurado "
                "debe ser la clave privada «service_role» o «secret», no la "
                "clave pública «anon» o «publishable»."
            )
        return False,(
            "No fue posible consultar la nómina autorizada. Revisa la conexión "
            "a Supabase y ejecuta «REPARACION_ACCESO_V29.sql» una sola vez."
        )
    if not rows:
        return False,"El nombre y el RUT o cédula no coinciden con la nómina autorizada."
    row=rows[0]
    accepted_names={
        _normalize_name(row.get("display_name")),
        _normalize_name(row.get("email")),
    }
    if normalized_name not in accepted_names:
        return False,"El nombre o correo y el RUT o cédula no coinciden con la nómina autorizada."
    return True,row

def _progress_value(value):
    """Return a JSON-safe widget value, or None when it should not be persisted."""
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    if isinstance(value,(list,tuple)):
        return [_progress_value(v) for v in value]
    if isinstance(value,dict):
        return {str(k):_progress_value(v) for k,v in value.items()}
    return None

def _is_answer_state(key):
    key=str(key)
    blocked=("access","role","name","user_key","projection_mode","manage_",
             "projection_","review_","anon_","reveal_","teacher_")
    if key.startswith(blocked):
        return False
    return (
        key.startswith(("ans_","checked_","sent_","exam_","q","lab1_","l2s10_","s3","s5","s7","s9","e9_","final_"))
        or key in {"case_V","case_A","case_calc","case_diff","case_pct",
                   "case_bands","case_choice","case_justification"}
    )

def save_user_progress(class_id):
    if not st.session_state.get("access") or st.session_state.get("projection_mode"):
        return
    user_key=st.session_state.get("user_key")
    if not user_key:
        return
    state={str(k):_progress_value(v) for k,v in st.session_state.items() if _is_answer_state(k)}
    serialized=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    state_hash=hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    hash_key=f"_last_saved_progress_hash_{class_id}"
    if st.session_state.get(hash_key)==state_hash:
        return
    client=_supabase()
    if client is not None:
        client.table("user_progress").upsert({
            "course_id":COURSE_ID,"class_id":class_id,"user_key":user_key,
            "role":st.session_state.get("role","Alumno"),
            "display_name":st.session_state.get("name",""),
            "state_json":state,"updated_at":_now(),
        },on_conflict="class_id,user_key").execute()
        st.session_state[hash_key]=state_hash
    else:
        with _activity_db() as con:
            con.execute(
            """INSERT INTO user_progress(user_key,role,display_name,state_json,updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(user_key) DO UPDATE SET role=excluded.role,
            display_name=excluded.display_name,state_json=excluded.state_json,
            updated_at=excluded.updated_at""",
            (user_key,st.session_state.get("role","Alumno"),
             st.session_state.get("name",""),serialized,
             dt.datetime.now().isoformat(timespec="seconds")),
            )
        st.session_state[hash_key]=state_hash

def load_user_progress(user_key, class_id):
    client=_supabase()
    if client is not None:
        rows=_remote_rows("user_progress",class_id=class_id,user_key=user_key)
        if not rows: return
        saved=rows[0].get("state_json") or {}
    else:
        with _activity_db() as con:
            row=con.execute("SELECT state_json FROM user_progress WHERE user_key=?",(user_key,)).fetchone()
        if not row: return
        try:
            saved=json.loads(row[0])
        except (TypeError,json.JSONDecodeError):
            return
    try:
        if isinstance(saved,str): saved=json.loads(saved)
    except json.JSONDecodeError:
        return
    for key,value in saved.items():
        if key=="exam_answers" and isinstance(value,dict):
            value={int(k):v for k,v in value.items()}
        if _is_answer_state(key) and key not in st.session_state:
            st.session_state[key]=value
    serialized=json.dumps(
        {str(k):_progress_value(v) for k,v in st.session_state.items() if _is_answer_state(k)},
        ensure_ascii=False,sort_keys=True,separators=(",",":"),
    )
    st.session_state[f"_last_saved_progress_hash_{class_id}"]=hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()
