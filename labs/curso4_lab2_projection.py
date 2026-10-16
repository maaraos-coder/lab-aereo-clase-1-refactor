"""Borrador persistente compartido de la clase proyectada, separado de alumnos."""
from copy import deepcopy
import json

CLASS_ID = "clase-08-construccion-lab-2"


def is_projection(st):
    return bool(st.session_state.get("projection_mode") or st.session_state.get("role") == "Proyección")


def cache_key(class_id):
    return f"projection_draft_{class_id}"


def load_draft(st, client, course_id, class_id):
    key = cache_key(class_id)
    if key in st.session_state:
        return st.session_state[key]
    if client is None:
        raise RuntimeError("No hay conexión con el almacenamiento de la clase.")
    rows = (client.table("projection_state").select("draft_state")
            .eq("course_id", course_id).eq("class_id", class_id).limit(1).execute().data or [])
    state = rows[0].get("draft_state") if rows else {}
    state = json.loads(state) if isinstance(state, str) else state
    state = state or {}
    if not isinstance(state, dict):
        raise ValueError("El borrador de clase no tiene un formato válido.")
    st.session_state[key] = deepcopy(state)
    st.session_state[key + "_persisted"] = deepcopy(state)
    return st.session_state[key]


def save_draft(st, client, course_id, class_id, state):
    if client is None:
        raise RuntimeError("No hay conexión con el almacenamiento de la clase.")
    # Solo actualiza el borrador: conserva la etapa y el contenido enviado a Zoom.
    rows = (client.table("projection_state").update({"draft_state": state})
            .eq("course_id", course_id).eq("class_id", class_id).execute().data or [])
    if not rows:
        raise RuntimeError("No se pudo confirmar el guardado del borrador de clase.")
    key = cache_key(class_id)
    st.session_state[key] = deepcopy(state)
    st.session_state[key + "_persisted"] = deepcopy(state)
