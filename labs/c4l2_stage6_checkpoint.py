"""Isolated, verified Supabase recovery copy for C4L2 Stage 6.

Use the existing `responses` table (already present in supabase_schema.sql)
instead of resending a student's entire user_progress JSONB, including huge
maps and earlier stages. This reserved draft is NOT an evaluation response.
No schema migration or credentials in the client are required.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import logging

_LOG=logging.getLogger(__name__)

QUESTION_KEY="__internal_c4l2_stage6_checkpoint_v1"
FIELDS=(
    "c4l2_s6_control_design",
    "c4l2_s6_measure_config",
    "c4l2_s6_checks",
    "c4l2_s6_tl_calculator",
    "c4l2_s6_treatment_study",
    "c4l2_s6_treatment_study_results",
    "c4l2_updated_6",
    "done_6",
)
SCHEMA=1
MAX_BYTES=800_000


def _json_safe(value):
    # Streamlit, pandas and acoustic calculations sometimes return numpy
    # scalar/array objects. Convert them before constructing JSONB.
    if hasattr(value,"item") and callable(value.item):
        return _json_safe(value.item())
    if isinstance(value,dict):
        return {str(k):_json_safe(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [_json_safe(v) for v in value]
    if hasattr(value,"tolist") and callable(value.tolist):
        return _json_safe(value.tolist())
    # Missing values from the Stage 6 strategy data editor arrive as
    # numpy.nan / pandas.NA even when the editor visually shows blanks.
    # Encode blank optional fields as JSON null, never NaN or pd.NA.
    if type(value).__name__ in ("NAType", "NaTType"):
        return None
    if isinstance(value,float):
        import math
        if math.isnan(value):
            return None
        if not math.isfinite(value):
            raise ValueError("No se pueden guardar valores infinitos en Etapa 6.")
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    raise TypeError("Valor no serializable en Etapa 6: "+type(value).__name__)


def _snapshot(state):
    if not isinstance(state,dict):
        raise TypeError("El avance de la Etapa 6 no es un diccionario.")
    selected={key:_json_safe(state[key]) for key in FIELDS if key in state}
    # Explicit JSON round trip prevents mutable references to Streamlit state.
    serialized=json.dumps(selected,ensure_ascii=False,allow_nan=False,sort_keys=True)
    if len(serialized.encode("utf-8"))>MAX_BYTES:
        raise ValueError("El diseño de la Etapa 6 supera el tamaño máximo del respaldo independiente.")
    return json.loads(serialized)


def _fingerprint(payload):
    blob=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def save_stage6_checkpoint(client,*,course_id,class_id,user_key,state):
    """Write and read back *only* Stage 6 fields. Raises on nonconfirmation."""
    if client is None or not user_key:
        raise RuntimeError("No hay conexión de Supabase o usuario autenticado.")
    payload={"schema_version":SCHEMA,"fields":_snapshot(state)}
    row={
        "course_id":course_id,
        "class_id":class_id,
        "user_key":user_key,
        "stage":6,
        "question_key":QUESTION_KEY,
        "question_text":"Respaldo técnico interno de la Etapa 6 (sin calificación)",
        "answer":payload,
        "auto_score":0,
        "max_score":0,
        "status":"draft",
    }
    client.table("responses").upsert(
        row,on_conflict="class_id,user_key,question_key",returning="minimal"
    ).execute()
    verified=(client.table("responses").select("answer")
              .eq("class_id",class_id)
              .eq("user_key",user_key)
              .eq("question_key",QUESTION_KEY)
              .limit(1).execute().data or [])
    if not verified:
        raise RuntimeError("Supabase no devolvió el respaldo de la Etapa 6.")
    response=verified[0].get("answer")
    if isinstance(response,str):
        response=json.loads(response)
    if not isinstance(response,dict) or response.get("schema_version")!=SCHEMA:
        raise RuntimeError("El respaldo verificado no coincide con el esquema.")
    if _fingerprint(response.get("fields")) != _fingerprint(payload["fields"]):
        raise RuntimeError("El respaldo de la Etapa 6 no coincide con los datos enviados.")
    return True


def _timestamp(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z","+00:00")).timestamp()
    except (ValueError,TypeError,OverflowError):
        return -1


def load_stage6_checkpoint(client,*,class_id,user_key,state):
    """Merge isolated Stage 6 copy with older progress. Never touch stages 3–5."""
    if not isinstance(state,dict):
        raise TypeError("El progreso recuperado no es un diccionario.")
    if client is None or not user_key:
        return False
    response=(client.table("responses").select("answer")
              .eq("class_id",class_id)
              .eq("user_key",user_key)
              .eq("question_key",QUESTION_KEY)
              .limit(1).execute().data or [])
    if not response:
        return False
    checkpoint=response[0].get("answer")
    if isinstance(checkpoint,str):
        checkpoint=json.loads(checkpoint)
    if not isinstance(checkpoint,dict) or checkpoint.get("schema_version")!=SCHEMA:
        raise ValueError("El respaldo de la Etapa 6 tiene una versión no compatible.")
    fields=checkpoint.get("fields")
    if not isinstance(fields,dict) or any(k not in FIELDS for k in fields):
        raise ValueError("El respaldo de la Etapa 6 contiene campos ajenos a la etapa.")
    # Do not overwrite a newer primary save with an older checkpoint.
    if _timestamp(state.get("c4l2_updated_6")) > _timestamp(fields.get("c4l2_updated_6")):
        return False
    state.update(deepcopy(fields))
    return True


def reset_stage6_widgets(session, prefix):
    """Clear stale widgets after restoring JSON, preserve the upload control."""
    removed=[]
    for key in list(session):
        if (isinstance(key,str) and key.startswith(prefix+"_")
            and key != prefix+"_work"
            and key != prefix+"_restore"
            and not key.startswith(prefix+"_backup_")):
            removed.append(key)
            del session[key]
    return removed


def reconcile_machine_ids(applications, entries, fingerprint):
    """Safely remap legacy source IDs after reordering Stage 3 rows.

    Do not guess when source signatures are missing or ambiguous.
    """
    if not isinstance(applications,dict):
        raise ValueError("El respaldo no contiene aplicaciones de máquina.")
    by_id={entry["id"]:entry["source"] for entry in entries}
    signatures={key:fingerprint([value]) for key,value in by_id.items()}
    mapped={}
    unresolved=[]
    for old_id,application in applications.items():
        signature=application.get("source_signature") if isinstance(application,dict) else None
        target=None
        if old_id in by_id and (not signature or signatures[old_id]==signature):
            target=old_id
        elif signature:
            matches=[key for key,value in signatures.items()
                     if value==signature and key not in mapped]
            if len(matches)==1:
                target=matches[0]
        if target is None or target in mapped:
            unresolved.append(old_id)
        else:
            mapped[target]=deepcopy(application)
    return mapped,unresolved
