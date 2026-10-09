"""Aviso personal de evaluaciones oficiales pendientes, al entrar al laboratorio."""
import streamlit as st

OFFICIAL_CLASSES = {
    "clase-02-aislamiento-ruido-aereo-minvu",
    "clase-04-impacto-instalaciones-lab-2",
    "clase-06-ruido-ambiental-lab-2",
}


def pending_items(catalog, classes, responses, is_open, fallback_openings):
    delivered = {(r.get("class_id"), r.get("stage"), r.get("question_key"))
                 for r in responses if r.get("status") in
                 ("submitted", "submitted_incomplete", "reviewed", "completed")
                 or r.get("submitted_at") or r.get("teacher_score") is not None}
    available = {r["id"] for r in classes
                 if r.get("status") == "published"
                 and is_open(r.get("opens_at") or fallback_openings.get(r["id"]))}
    items = []
    for lab in catalog:
        class_id = lab["id"]
        if class_id not in OFFICIAL_CLASSES or class_id not in available:
            continue
        for stage, question_key in ((9, "final_comprehension"), (10, "final_integrated_design")):
            if (class_id, stage, question_key) not in delivered:
                items.append(f"{lab['course']} · Laboratorio {lab['lab']} · Etapa {stage}: {lab['stages'][stage]['title']}")
    return items


@st.dialog("Evaluaciones pendientes")
def _dialog(name, items):
    st.write(f"Hola, {name}. Tienes las siguientes evaluaciones pendientes de entrega:")
    for item in items:
        st.write(f"• {item}")
    if st.button("Cerrar", type="primary", key="close_pending_evaluations"):
        st.rerun()


def show_on_entry(runtime, class_id):
    if st.session_state.get("role") != "Alumno":
        return
    if st.session_state.get("_pending_popup_lab") == class_id:
        return
    st.session_state["_pending_popup_lab"] = class_id
    client = runtime["_supabase"]()
    user_key = st.session_state.get("user_key")
    if client is None or not user_key:
        return
    try:
        catalog = runtime["_results_catalog"]()
        classes = runtime["_course_classes"](client)
        responses = (client.table("responses")
                     .select("class_id,stage,question_key,status,submitted_at,teacher_score")
                     .eq("user_key", user_key).in_("class_id", sorted(OFFICIAL_CLASSES))
                     .execute().data or [])
        openings = {lab["id"]: lab.get("opens_at")
                    for course in runtime["ACADEMIC_COURSES"] for lab in course["labs"]}
        openings.update({lab["id"]: lab.get("opens_at") for lab in runtime["FUTURE_LABS"].values()})
        items = pending_items(catalog, classes, responses, runtime["_is_open"], openings)
    except Exception:
        # Una consulta fallida no debe impedir entrar a los contenidos.
        return
    if items:
        _dialog(st.session_state.get("name") or "alumno", items)
