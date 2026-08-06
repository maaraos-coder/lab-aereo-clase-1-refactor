"""Student results and teacher-controlled answer release."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st


def _decode_answer(value):
    if isinstance(value, dict):
        if set(value) == {"value"}:
            return str(value["value"])
        return json.dumps(value, ensure_ascii=False, indent=2)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False, indent=2)
    if value is None:
        return "Sin respuesta registrada"
    try:
        parsed = json.loads(str(value))
        return _decode_answer(parsed)
    except (TypeError, json.JSONDecodeError):
        return str(value)


def _release_map(client) -> dict[str, dict]:
    try:
        rows = client.table("result_release_settings").select("*").execute().data or []
        return {row["class_id"]: row for row in rows}
    except Exception:
        return {}


def _class_labels(classes: list[dict]) -> dict[str, str]:
    return {
        item["id"]: f"{item.get('course', 'Curso')} · Laboratorio {item.get('lab', '')}"
        for item in classes
    }


def results_view(client, classes: list[dict], user_key: str) -> None:
    st.markdown("## Mis resultados")
    st.caption("Aquí puedes comprobar tu avance, puntajes y las revisiones que el docente haya liberado.")
    if client is None:
        st.warning("Esta sección necesita la conexión permanente con Supabase.")
        return
    labels = _class_labels(classes)
    rows = (
        client.table("responses")
        .select("*")
        .eq("user_key", user_key)
        .order("class_id")
        .order("stage")
        .execute()
        .data
        or []
    )
    releases = _release_map(client)
    if not rows:
        st.info("Todavía no tienes actividades enviadas.")
        return

    for class_id in dict.fromkeys(row.get("class_id") for row in rows):
        lab_rows = [row for row in rows if row.get("class_id") == class_id]
        maximum = sum(float(row.get("max_score") or 0) for row in lab_rows)
        earned = sum(
            float(row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score") or 0)
            for row in lab_rows
        )
        setting = releases.get(class_id, {})
        expected = int(setting.get("expected_activities") or 0)
        completed = len({row.get("question_key") for row in lab_rows})
        status = "Completado" if expected and completed >= expected else "En progreso"
        if completed == 0:
            status = "Pendiente"
        st.markdown(f"### {labels.get(class_id, class_id)}")
        a, b, c = st.columns(3)
        a.metric("Estado", status)
        b.metric("Actividades enviadas", f"{completed}" + (f"/{expected}" if expected else ""))
        c.metric("Puntaje", f"{earned:g}/{maximum:g}")

        for row in lab_rows:
            title = f"Etapa {row.get('stage')} · {row.get('question_text') or row.get('question_key')}"
            with st.expander(title):
                st.markdown("**Tu respuesta**")
                st.code(_decode_answer(row.get("answer")), language=None)
                score = row.get("teacher_score")
                effective = float(score if score is not None else row.get("auto_score") or 0)
                st.write(f"**Puntaje:** {effective:g}/{float(row.get('max_score') or 0):g}")
                if row.get("teacher_note"):
                    st.info(f"Comentario docente: {row['teacher_note']}")
                if bool(setting.get("release_activity_feedback")) and row.get("feedback"):
                    st.write(f"**Retroalimentación:** {row['feedback']}")
                is_final = row.get("question_key") == "final_exam" or int(row.get("stage") or -1) == 10
                released = (
                    bool(setting.get("release_final_answers"))
                    if is_final
                    else bool(setting.get("release_correct_answers"))
                )
                if released:
                    st.success(f"Respuesta correcta o pauta: {row.get('correct_answer') or 'Pauta no registrada.'}")
                else:
                    st.caption("La respuesta correcta todavía no ha sido liberada por el docente.")


def release_controls(client, classes: list[dict], now_fn, teacher_name: str) -> None:
    if client is None:
        st.warning("La liberación de resultados necesita Supabase.")
        return
    labels = _class_labels(classes)
    class_id = st.selectbox(
        "Laboratorio",
        list(labels),
        format_func=lambda value: labels[value],
        key="release_class",
    )
    rows = (
        client.table("result_release_settings")
        .select("*")
        .eq("class_id", class_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    current = rows[0] if rows else {}
    expected = st.number_input(
        "Cantidad esperada de actividades",
        min_value=0,
        max_value=100,
        value=int(current.get("expected_activities") or 0),
        help="Permite determinar si el alumno terminó el laboratorio.",
    )
    feedback = st.toggle(
        "Liberar retroalimentación de actividades",
        value=bool(current.get("release_activity_feedback")),
    )
    correct = st.toggle(
        "Liberar respuestas correctas de actividades",
        value=bool(current.get("release_correct_answers")),
    )
    final = st.toggle(
        "Liberar pauta de evaluación final",
        value=bool(current.get("release_final_answers")),
        help="Actívalo solo cuando corresponda entregar la pauta completa.",
    )
    if st.button("Guardar liberación", type="primary", use_container_width=True):
        client.table("result_release_settings").upsert(
            {
                "class_id": class_id,
                "expected_activities": int(expected),
                "release_activity_feedback": bool(feedback),
                "release_correct_answers": bool(correct),
                "release_final_answers": bool(final),
                "updated_at": now_fn(),
                "updated_by": teacher_name,
            },
            on_conflict="class_id",
        ).execute()
        st.success("Configuración guardada.")

