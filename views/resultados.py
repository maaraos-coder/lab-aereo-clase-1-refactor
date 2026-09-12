import math
"""Vista de desempeño y retroalimentación del alumno.

import re
Separa deliberadamente dos conceptos académicos:

* progreso formativo: ejercicios y actividades que preparan al estudiante;
* calificaciones oficiales: exclusivamente Laboratorio 2, etapas 9 y 10.

``app.py`` inyecta las dependencias compartidas antes de ejecutar cada vista.
"""

from core.activities import formative_progress_snapshot
import json

_LOCAL_NAMES = {
    "run_view", "_bind_runtime", "_VIEWS", "_LOCAL_NAMES",
    "_results_catalog", "_student_result_payload", "_result_date",
    "_friendly_result_label", "_clean_result_rows", "_effective_row_score",
    "_grade", "_answer_release_allowed",
    "_render_stage9_comparison", "_render_stage10_comparison",
    "_formative_progress_data", "_render_formative_progress", "_official_rows", "_official_summary",
    "_latest_response_by_key", "_course2_lab1_rows", "_course2_lab2_delivery_rows", "_render_course2_lab1_scores",
    "_future_progress_rows", "_future_progress_state", "_future_lab_progress",
    "_render_lab_progress_card", "_render_course1_official_evaluations",
    "_render_course1_block", "_render_course2_block", "_render_course3_block", "_course2_lab2_official_summary",
    "_c2_answer_tabs_header", "_c2_render_mcq_comparison", "_c2_render_feedback_tab",
    "_c2_render_lab1_stage9_tabs", "_c2_render_lab1_stage10_tabs",
    "_c2_render_lab2_stage9_tabs", "_c2_render_lab2_stage10_tabs",
    "_render_readonly_answers_block", "_render_course2_lab1_submission",
    "_render_course2_lab2_stage9_submission", "_render_course2_lab2_stage10_submission",
    "_render_teacher_feedback",
    "student_sidebar_summary", "results_view",
}


def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value


def _latest_response_by_key(rows, class_id, specs):
    """Devuelve la entrega más reciente para cada (stage, question_key).

    specs: dict {alias: (stage, question_key)}
    """
    out = {alias: None for alias in specs}

    def _stamp(row):
        return str(
            row.get("updated_at")
            or row.get("submitted_at")
            or row.get("created_at")
            or ""
        )

    for alias, (stage, question_key) in specs.items():
        candidates = [
            r for r in rows
            if r.get("class_id") == class_id
            and int(r.get("stage") or -1) == int(stage)
            and r.get("question_key") == question_key
        ]
        if candidates:
            out[alias] = max(candidates, key=_stamp)
    return out


def _course2_lab1_rows(rows):
    """Entregas formativas del Curso 2 · Laboratorio 1.

    También reconoce la Etapa 9 de versiones antiguas que pudo quedar
    asociada a otro class_id, identificándola por su payload canónico.
    """
    out=_latest_response_by_key(
        rows,
        "clase-03-impacto-instalaciones-lab-1",
        {
            "final_comprehension": (9, "final_comprehension"),
            "final_exam": (10, "final_exam"),
        },
    )

    if out.get("final_comprehension") is None:
        legacy=[]
        for row in rows:
            if int(row.get("stage") or -1)!=9 or row.get("question_key")!="final_comprehension":
                continue
            payload=_student_result_payload(row.get("answer"))
            if (
                isinstance(payload,dict)
                and str(payload.get("version") or "").startswith("etapas_1_a_8")
                and int(payload.get("question_count") or 0)==25
                and int(payload.get("max_score") or 0)==100
                and payload.get("evaluation_mode")=="points_only"
            ):
                legacy.append(row)
        if legacy:
            def _stamp(row):
                return str(row.get("updated_at") or row.get("submitted_at") or row.get("created_at") or "")
            out["final_comprehension"]=max(legacy,key=_stamp)
    return out


def _course2_lab2_delivery_rows(rows):
    """Entregas evaluativas oficiales del Curso 2 · Laboratorio 2.

    Etapa 9  -> final_comprehension
    Etapa 10 -> final_integrated_design
    """
    return _latest_response_by_key(
        rows,
        "clase-04-impacto-instalaciones-lab-2",
        {
            "final_comprehension": (9, "final_comprehension"),
            "final_integrated_design": (10, "final_integrated_design"),
        },
    )


def _results_catalog():
    """Describe los laboratorios disponibles sin alterar la configuración central."""
    first_course = []
    for lab_number in (1, 2):
        minutes = STAGE_MINUTES if lab_number == 1 else dict(enumerate(LAB2_MINUTES))
        stages = []
        for stage, (prefix, title) in enumerate(LAB_STAGE_TITLES[lab_number]):
            stages.append({
                "title": title,
                "objective": f"{prefix} del Laboratorio {lab_number}.",
                "content_markdown": "",
                "activity_markdown": "",
                "teacher_solution": "",
                "minutes": int(minutes.get(stage, 20)),
            })
        first_course.append({
            "id": LABORATORIES[lab_number]["id"],
            "course": "Aislamiento acústico al ruido aéreo",
            "lab": lab_number,
            "stages": stages,
        })
    later = []
    for lab in FUTURE_LABS.values():
        stages = []
        for stage, (title, objective, concept, activity) in enumerate(lab["stages"]):
            stages.append({
                "title": title,
                "objective": objective,
                "content_markdown": concept,
                "activity_markdown": activity,
                "teacher_solution": "",
                "minutes": 20 if stage not in (9, 10) else 35,
            })
        later.append({
            "id": lab["id"],
            "course": lab["course"],
            "lab": lab["number"],
            "stages": stages,
        })
    return first_course + later


def _student_result_payload(value):
    payload = value
    for _ in range(3):
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                return payload
        elif isinstance(payload, dict) and set(payload) == {"value"}:
            payload = payload.get("value")
        else:
            break
    return payload


def _result_date(value):
    if not value:
        return "Fecha no registrada"
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y · %H:%M h")
    except (TypeError, ValueError):
        return str(value).replace("T", " ")[:16]


def _friendly_result_label(key):
    labels = {
        "t60": "Tiempo de reverberación", "volumen": "Volumen",
        "absorcion": "Absorción equivalente", "diferencia_costo": "Diferencia de costo",
        "incremento_porcentual": "Incremento porcentual", "bandas_criticas": "Bandas críticas",
        "recomendacion": "Recomendación", "justificacion": "Justificación",
        "rw": "Rw", "c": "C", "ctr": "Ctr", "description": "Descripción",
        "design_score": "Diseño técnico", "comprehension_score": "Comprensión",
        "wall": "Muro o tabique", "window": "Ventana", "door": "Puerta",
    }
    return labels.get(str(key), str(key).replace("_", " ").strip().capitalize())


def _clean_result_rows(payload, prefix=""):
    hidden = {
        "reason", "finished_at", "rubric_scores", "verification_signature",
        "curve", "tl", "frequencies", "combined_curve",
    }
    rows = []
    if not isinstance(payload, dict):
        return [(prefix or "Respuesta", payload)]
    for key, value in payload.items():
        if key in hidden or key in {
            "answers", "respuestas_teoricas", "caso_integrador",
            "calculated_result", "student_result",
        }:
            continue
        label = f"{prefix} · {_friendly_result_label(key)}" if prefix else _friendly_result_label(key)
        if isinstance(value, dict):
            rows.extend(_clean_result_rows(value, label))
        elif isinstance(value, list):
            rows.append((label, ", ".join(map(str, value)) if value else "Sin selección"))
        elif value not in (None, ""):
            rows.append((label, value))
    return rows


def _effective_row_score(row):
    value = row.get("teacher_score")
    if value is None:
        value = row.get("auto_score")
    return float(value or 0)


def _grade(score, maximum):
    if not maximum:
        return None
    return float(_grade_from_percent(100.0 * float(score) / float(maximum)))


def _answer_release_allowed(row):
    """La pauta, rúbrica y retroalimentación se muestran solo tras la revisión docente."""
    return bool(
        row.get("status") == "reviewed"
        or row.get("teacher_score") is not None
    )


def _official_rows(rows):
    lab2_id = LABORATORIES[2]["id"]
    allowed = {"final_comprehension", "final_integrated_design"}
    return [
        row for row in rows
        if row.get("class_id") == lab2_id and row.get("question_key") in allowed
    ]


def _official_summary(rows):
    by_key = {row.get("question_key"): row for row in _official_rows(rows)}
    stage9 = by_key.get("final_comprehension")
    stage10 = by_key.get("final_integrated_design")
    completed = sum(item is not None for item in (stage9, stage10))
    reviewed = sum(
        bool(item and (item.get("status") == "reviewed" or item.get("teacher_score") is not None))
        for item in (stage9, stage10)
    )
    total = None
    grade = None
    stage9_reviewed = bool(stage9 and _answer_release_allowed(stage9))
    stage10_reviewed = bool(stage10 and _answer_release_allowed(stage10))
    if stage9_reviewed and stage10_reviewed:
        total = _effective_row_score(stage9) + _effective_row_score(stage10)
        grade = _grade(total, 100)
    return {
        "stage9": stage9, "stage10": stage10, "completed": completed,
        "reviewed": reviewed, "total": total, "grade": grade,
    }


def _render_stage9_comparison(row, payload, allow_answers):
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    rubric = payload.get("rubric_scores", []) if isinstance(payload, dict) else []
    if not isinstance(answers, dict):
        answers = {}
    if not isinstance(rubric, list):
        rubric = []

    st.markdown("#### Comparación pregunta por pregunta")
    st.caption("Tu respuesta se conserva exactamente como fue enviada. La pauta permite identificar qué concepto debes reforzar.")
    for i, item in enumerate(STAGE9_QUESTIONS):
        chosen = answers.get(str(i)) or "Sin respuesta"
        correct = item["options"][item["correct"]]
        is_correct = chosen == correct
        points = float(rubric[i]) if i < len(rubric) else (4.0 if is_correct else 0.0)
        header_text = (
            f"{'✅' if is_correct else '❌'} Pregunta {i + 1} · {points:g}/4 puntos · {item['title']}"
            if allow_answers
            else f"🕒 Pregunta {i + 1} · {item['title']} · Pendiente de revisión"
        )
        with st.expander(header_text, expanded=(i == 0)):
            st.markdown(f"**Pregunta:** {item['question']}")
            left, right = st.columns(2)
            with left:
                st.markdown("**Tu respuesta**")
                (st.success if is_correct else st.error)(chosen)
            with right:
                st.markdown("**Pauta o respuesta esperada**")
                if allow_answers:
                    st.info(correct)
                else:
                    st.info(
                        "⏳ Evaluación pendiente de revisión docente. "
                        "La respuesta esperada, la rúbrica y la retroalimentación se mostrarán "
                        "automáticamente cuando el docente finalice la corrección."
                    )
            if allow_answers:
                st.markdown("**Criterio de la rúbrica**")
                st.progress(max(0.0, min(1.0, points / 4.0)))
                st.caption(f"Puntaje otorgado: {points:g} de 4 puntos")
                st.markdown("**Retroalimentación técnica**")
                st.write(item["explanation"])


def _render_stage10_comparison(row, payload, allow_answers):
    calculated = payload.get("calculated_result", {}) if isinstance(payload, dict) else {}
    student = payload.get("student_result", {}) if isinstance(payload, dict) else {}
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    rubric = payload.get("rubric_scores", {}) if isinstance(payload, dict) else {}
    if not isinstance(rubric, dict):
        rubric = {}

    design_points = float(rubric.get("design", payload.get("design_score", 0) or 0))
    comprehension_points = float(rubric.get("comprehension", payload.get("comprehension_score", 0) or 0))

    st.markdown("#### Tu desarrollo y el resultado verificado")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rw ingresado", f"{student.get('rw', '—')} dB")
    c2.metric("C ingresado", f"{student.get('c', '—')} dB")
    c3.metric("Ctr ingresado", f"{student.get('ctr', '—')} dB")
    if allow_answers:
        st.info(
            "Resultado verificado por la aplicación: "
            f"Rw(C; Ctr) = {calculated.get('rw', '—')} "
            f"({calculated.get('c', '—')}; {calculated.get('ctr', '—')}) dB."
        )
    else:
        st.info(
            "⏳ Evaluación pendiente de revisión docente. "
            "El resultado verificado, la pauta y la rúbrica se mostrarán "
            "automáticamente cuando el docente finalice la corrección."
        )

    components = []
    for key, label in (("wall", "Muro o tabique"), ("window", "Ventana"), ("door", "Puerta")):
        data = payload.get(key, {}) if isinstance(payload, dict) else {}
        if isinstance(data, dict):
            components.append({
                "Elemento": label,
                "Solución seleccionada": data.get("description", "Sin información"),
                "Rw": data.get("rw", "—"),
            })
    if components:
        st.dataframe(pd.DataFrame(components), hide_index=True, width="stretch")

    if allow_answers:
        st.markdown("#### Rúbrica de la evaluación")
        rubric_table = pd.DataFrame([
            {
                "Criterio": "Diseño técnico del paramento",
                "Qué se evalúa": "Selección de muro, ventana y puerta; cálculo de Rw, C y Ctr; cumplimiento de la meta.",
                "Puntaje": f"{design_points:g}/40",
            },
            {
                "Criterio": "Comprensión e interpretación",
                "Qué se evalúa": "Cinco preguntas sobre transmisión, elemento débil, adaptación espectral y decisiones de diseño.",
                "Puntaje": f"{comprehension_points:g}/20",
            },
        ])
        st.dataframe(rubric_table, hide_index=True, width="stretch")

    st.markdown("#### Tus respuestas de comprensión" if not allow_answers else "#### Comparación de las respuestas de comprensión")
    for i, (question, options, correct_index) in enumerate(LAB2_S10_QUESTIONS):
        raw = answers.get(str(i), answers.get(i)) if isinstance(answers, dict) else None
        chosen_index = None
        if raw in options:
            chosen_index = options.index(raw)
        else:
            try:
                parsed_index = int(raw) if raw is not None else None
                if parsed_index is not None and 0 <= parsed_index < len(options):
                    chosen_index = parsed_index
            except (TypeError, ValueError):
                chosen_index = None
        chosen = options[chosen_index] if chosen_index is not None else "Sin respuesta"
        correct = options[correct_index]
        is_correct = chosen_index == correct_index
        question_header = (
            f"{'✅' if is_correct else '❌'} Pregunta {i + 1} · {question}"
            if allow_answers
            else f"🕒 Pregunta {i + 1} · {question} · Pendiente de revisión"
        )
        with st.expander(question_header):
            left, right = st.columns(2)
            with left:
                st.markdown("**Tu respuesta**")
                (st.success if is_correct else st.error)(chosen)
            with right:
                st.markdown("**Pauta o respuesta esperada**")
                if allow_answers:
                    st.info(correct)
                else:
                    st.info(
                        "⏳ Evaluación pendiente de revisión docente. "
                        "La respuesta esperada, la rúbrica y la retroalimentación se mostrarán "
                        "automáticamente cuando el docente finalice la corrección."
                    )
            if allow_answers:
                st.markdown("**Retroalimentación técnica**")
                st.write(LAB2_S10_EXPLANATIONS[i])


def _formative_progress_data(rows):
    """Build the student progress from the unified activity catalog."""
    snapshot = formative_progress_snapshot(rows, course_id=COURSE_ID)
    labels = {
        1: {
            "title": "Laboratorio 1 · Fundamentos y aplicación",
            "subtitle": "Preguntas, cálculos y actividades de práctica",
        },
        2: {
            "title": "Laboratorio 2 · Preparación para la evaluación",
            "subtitle": "Actividades previas a las evaluaciones oficiales",
        },
    }
    for lab_number, item in snapshot.items():
        item.update(labels.get(lab_number, {
            "title": f"Laboratorio {lab_number}",
            "subtitle": "Actividades formativas",
        }))
    return snapshot


def _render_formative_progress(rows):
    progress_data = _formative_progress_data(rows)
    total_completed = sum(item["completed"] for item in progress_data.values())
    total_expected = sum(item["expected"] for item in progress_data.values())
    total_percent = 100.0 * total_completed / total_expected if total_expected else 0.0

    st.markdown("## Progreso del curso")
    st.caption(
        "Aquí se muestra cuánto has avanzado en las actividades de práctica. "
        "Estas actividades entregan retroalimentación, pero no generan una nota oficial."
    )

    a, b, c = st.columns(3)
    a.metric("Actividades completadas", f"{total_completed} de {total_expected}")
    b.metric("Avance formativo", f"{total_percent:.0f} %")
    completed_labs = sum(1 for item in progress_data.values() if item["expected"] and item["completed"] >= item["expected"])
    c.metric("Laboratorios formativos completos", f"{completed_labs} de {len(progress_data)}")
    st.progress(max(0.0, min(1.0, total_percent / 100.0)))

    cols = st.columns(2)
    for col, (lab_number, definition) in zip(cols, progress_data.items()):
        completed = definition["completed"]
        expected = definition["expected"]
        percent = definition["percent"]
        if expected and completed >= expected:
            status = "✅ Completado"
        elif completed:
            status = "🟡 En desarrollo"
        else:
            status = "⚪ Sin iniciar"

        with col:
            st.markdown(f"### {definition['title']}")
            st.caption(definition["subtitle"])
            st.metric("Actividades realizadas", f"{completed} de {expected}")
            st.progress(max(0.0, min(1.0, percent / 100.0)))
            st.caption(f"{status} · {percent:.0f} % de avance")
            with st.expander("Ver detalle por etapa"):
                for item in definition["stage_rows"]:
                    stage_status = "✅" if item["expected"] and item["completed"] >= item["expected"] else ("🟡" if item["completed"] else "⚪")
                    st.markdown(
                        f"**{stage_status} Etapa {item['stage']}: "
                        f"{item['completed']} de {item['expected']} actividades**"
                    )
                    for activity in item.get("activity_details", []):
                        mark = "✅" if activity.get("completed") else "○"
                        st.caption(f"{mark} {activity.get('label')}")



def student_sidebar_summary(client, user_key):
    """Tarjeta lateral compacta del diplomado, separando el avance por curso."""
    if not user_key or client is None:
        return

    class_ids=[
        LABORATORIES[1]["id"],
        LABORATORIES[2]["id"],
        "clase-03-impacto-instalaciones-lab-1",
        "clase-04-impacto-instalaciones-lab-2",
    ]
    try:
        rows=(
            client.table("responses").select("*")
            .eq("user_key",user_key)
            .in_("class_id",class_ids)
            .execute().data or []
        )
    except Exception:
        return

    official=_official_summary(rows)
    progress_data=_formative_progress_data(rows)
    expected=sum(item["expected"] for item in progress_data.values())
    completed=sum(item["completed"] for item in progress_data.values())
    formative_percent=100.0*completed/expected if expected else 0.0

    # Curso 2 · avance formativo: EXCLUSIVAMENTE las Etapas 9 y 10
    # del Laboratorio 1. Cada etapa aporta hasta 100 puntos formativos,
    # por lo que el indicador corresponde a puntaje obtenido / 200.
    # Las Etapas 0–8 no intervienen en este porcentaje.
    course2_lab1=_course2_lab1_rows(rows)
    c2_lab1_score=sum(
        _effective_row_score(course2_lab1.get(k))
        if course2_lab1.get(k) is not None else 0.0
        for k in ("final_comprehension","final_exam")
    )
    c2_lab1_progress_pct=max(0.0,min(100.0,100.0*c2_lab1_score/200.0))

    # Curso 2 · Lab 2: dos evaluaciones oficiales.
    course2_lab2=_course2_lab2_delivery_rows(rows)
    c2_lab2_delivered=sum(
        course2_lab2.get(k) is not None
        for k in ("final_comprehension","final_integrated_design")
    )

    # Curso 3 · Laboratorio 1: las 11 etapas (0–10) son formativas.
    # Su progreso se guarda en user_progress, no en responses.
    future_progress=_future_progress_rows(client,user_key)
    course3_labs=[
        lab for lab in FUTURE_LABS.values()
        if lab.get("course")=="Control de ruido ambiental"
    ]
    c3_lab1=next(
        (lab for lab in course3_labs if int(lab.get("number") or 0)==1),
        None,
    )
    c3_prog=_future_lab_progress(c3_lab1,future_progress) if c3_lab1 else {
        "completed":0,"expected":11,"percent":0.0
    }
    c3_formative_pct=float(c3_prog.get("percent") or 0.0)

    st.markdown(
        f"""
        <div style="background:linear-gradient(145deg,#0b5b91,#0e91c7);border:1px solid #59d4ef;
                    border-radius:14px;padding:.85rem;margin:.8rem 0;color:white">
          <div style="font-weight:800;font-size:.95rem;margin-bottom:.55rem">📘 PROGRESO DEL DIPLOMADO</div>

          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem">
            <span>Curso 1 · evaluaciones</span><b>{official['completed']}/2</b>
          </div>

          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem;margin-top:.35rem">
            <span>Curso 1 · avance formativo</span><b>{formative_percent:.0f}%</b>
          </div>

          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem;margin-top:.35rem">
            <span>Curso 2 · avance formativo</span><b>{c2_lab1_progress_pct:.0f}%</b>
          </div>

          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem;margin-top:.35rem">
            <span>Curso 2 · evaluaciones</span><b>{c2_lab2_delivered}/2</b>
          </div>

          <div style="height:1px;background:rgba(255,255,255,.22);margin:.55rem 0 .45rem"></div>

          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem">
            <span>Curso 3 · avance formativo</span><b>{c3_formative_pct:.0f}%</b>
          </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def _future_progress_rows(client, user_key):
    """Recupera progreso persistido de laboratorios posteriores por class_id."""
    if client is None or not user_key:
        return {}
    class_ids=[lab["id"] for lab in FUTURE_LABS.values()]
    if not class_ids:
        return {}
    try:
        raw=(
            client.table("user_progress")
            .select("class_id,state_json,updated_at")
            .eq("user_key",user_key)
            .in_("class_id",class_ids)
            .execute().data or []
        )
    except Exception:
        return {}

    result={}
    for row in raw:
        state=row.get("state_json") or {}
        if isinstance(state,str):
            try:
                state=json.loads(state)
            except Exception:
                state={}
        if not isinstance(state,dict):
            state={}
        result[str(row.get("class_id"))]={
            "state":state,
            "updated_at":row.get("updated_at"),
        }
    return result


def _future_progress_state(progress_rows, class_id):
    item=(progress_rows or {}).get(class_id) or {}
    state=item.get("state") or {}
    return state if isinstance(state,dict) else {}


def _future_lab_progress(lab, progress_rows):
    """Resumen por etapas para laboratorios futuros sin mezclarlo con el catálogo del Curso 1."""
    state=_future_progress_state(progress_rows,lab["id"])
    total=len(lab.get("stages") or [])
    stage_rows=[]
    completed=0
    for stage in range(total):
        done=bool(state.get(f"done_{stage}"))
        completed+=int(done)
        stage_rows.append({
            "stage":stage,
            "title":lab["stages"][stage][0] if stage < len(lab["stages"]) else f"Etapa {stage}",
            "completed":done,
        })
    percent=(100.0*completed/total) if total else 0.0
    return {
        "completed":completed,
        "expected":total,
        "percent":percent,
        "stage_rows":stage_rows,
        "state":state,
        "updated_at":(progress_rows.get(lab["id"]) or {}).get("updated_at") if progress_rows else None,
    }


def _render_lab_progress_card(title, subtitle, completed, expected, percent, stage_rows=None):
    """Tarjeta visual reutilizable para cualquier laboratorio."""
    if expected and completed >= expected:
        status="✅ Completado"
    elif completed:
        status="🟡 En desarrollo"
    else:
        status="⚪ Sin iniciar"

    with st.container(border=True):
        st.markdown(f"### {title}")
        if subtitle:
            st.caption(subtitle)
        a,b=st.columns([1,1])
        a.metric("Avance",f"{completed} de {expected}")
        b.metric("Progreso",f"{percent:.0f} %")
        st.progress(max(0.0,min(1.0,percent/100.0)))
        st.caption(f"{status}")

        if stage_rows:
            with st.popover("Ver detalle por etapa",use_container_width=True):
                for item in stage_rows:
                    if "expected" in item:
                        mark="✅" if item["expected"] and item["completed"]>=item["expected"] else ("🟡" if item["completed"] else "⚪")
                        st.markdown(
                            f"**{mark} Etapa {item['stage']} · "
                            f"{item['completed']} de {item['expected']} actividades**"
                        )
                        for activity in item.get("activity_details",[]):
                            amark="✅" if activity.get("completed") else "○"
                            st.caption(f"{amark} {activity.get('label')}")
                    else:
                        mark="✅" if item.get("completed") else "⚪"
                        st.markdown(
                            f"**{mark} Etapa {item.get('stage')} · {item.get('title','')}**"
                        )


def _render_course1_official_evaluations(official):
    st.markdown("### Evaluaciones oficiales")
    st.caption(
        "La nota del Curso 1 se obtiene exclusivamente con el Laboratorio 2: "
        "Etapa 9 (40 puntos) y Etapa 10 (60 puntos)."
    )

    evaluations=[
        ("stage9","Etapa 9 · Evaluación de comprensión",official["stage9"],40),
        ("stage10","Etapa 10 · Aplicación integradora",official["stage10"],60),
    ]
    for kind,title,row,maximum in evaluations:
        if row is None:
            with st.expander(f"⏳ {title} · Pendiente"):
                st.caption("Todavía no existe una entrega registrada para esta evaluación.")
            continue

        reviewed=row.get("status")=="reviewed" or row.get("teacher_score") is not None
        score=_effective_row_score(row) if reviewed else None
        grade=_grade(score,maximum) if reviewed else None
        icon="✅" if reviewed else "🕒"
        summary=(
            f"{icon} {title} · {score:g}/{maximum} puntos · Nota {grade:.1f}"
            if reviewed
            else f"{icon} {title} · Entregada · Pendiente de revisión"
        )

        with st.expander(summary,expanded=False):
            a,b,c=st.columns(3)
            a.metric("Puntaje oficial",f"{score:g}/{maximum}" if reviewed else "Pendiente")
            b.metric("Nota",f"{grade:.1f}" if reviewed else "Pendiente")
            c.metric("Estado","Revisada" if reviewed else "Pendiente de revisión")
            st.caption(f"Entrega: {_result_date(row.get('submitted_at') or row.get('updated_at'))}")

            if not reviewed:
                st.info(
                    "Tu entrega está registrada. La pauta, la rúbrica y la retroalimentación "
                    "se publicarán cuando el docente termine la revisión."
                )

            payload=_student_result_payload(row.get("answer"))
            if not isinstance(payload,dict):
                payload={}
            allow_answers=_answer_release_allowed(row)
            response_tab,rubric_tab,feedback_tab=st.tabs([
                "Tus respuestas y pauta","Rúbrica","Retroalimentación docente",
            ])
            with response_tab:
                if kind=="stage9":
                    _render_stage9_comparison(row,payload,allow_answers)
                else:
                    _render_stage10_comparison(row,payload,allow_answers)
            with rubric_tab:
                if not reviewed:
                    st.info("La rúbrica se habilitará cuando finalice la revisión docente.")
                elif kind=="stage9":
                    rubric=payload.get("rubric_scores",[])
                    answers=payload.get("answers",{})
                    rows_rubric=[]
                    for i,item in enumerate(STAGE9_QUESTIONS):
                        chosen=answers.get(str(i)) if isinstance(answers,dict) else None
                        correct=item["options"][item["correct"]]
                        points=float(rubric[i]) if isinstance(rubric,list) and i<len(rubric) else (4.0 if chosen==correct else 0.0)
                        rows_rubric.append({
                            "Criterio":f"Pregunta {i+1} · {item['title']}",
                            "Puntaje":f"{points:g}/4",
                            "Nivel":"Logrado" if points>=4 else ("En desarrollo" if points>0 else "No logrado"),
                        })
                    st.dataframe(pd.DataFrame(rows_rubric),hide_index=True,width="stretch")
                else:
                    rubric=payload.get("rubric_scores",{})
                    if not isinstance(rubric,dict):
                        rubric={}
                    st.dataframe(pd.DataFrame([
                        {
                            "Criterio":"Diseño técnico del paramento",
                            "Puntaje":f"{float(rubric.get('design',payload.get('design_score',0) or 0)):g}/40",
                        },
                        {
                            "Criterio":"Comprensión e interpretación",
                            "Puntaje":f"{float(rubric.get('comprehension',payload.get('comprehension_score',0) or 0)):g}/20",
                        },
                    ]),hide_index=True,width="stretch")
            with feedback_tab:
                note=row.get("teacher_note")
                if note:
                    st.info(note)
                elif reviewed:
                    st.caption("El docente no dejó una observación general.")
                else:
                    st.info("La retroalimentación estará disponible cuando termine la revisión.")
                if reviewed and row.get("feedback"):
                    st.markdown("**Retroalimentación automática**")
                    st.write(row.get("feedback"))


def _render_course1_block(rows):
    official=_official_summary(rows)
    progress_data=_formative_progress_data(rows)

    total_completed=sum(item["completed"] for item in progress_data.values())
    total_expected=sum(item["expected"] for item in progress_data.values())
    progress_pct=(100.0*total_completed/total_expected) if total_expected else 0.0
    grade_text=f"{official['grade']:.1f}" if official["grade"] is not None else "Pendiente"

    label=(
        f"Curso 1 · Aislamiento acústico al ruido aéreo · "
        f"{progress_pct:.0f}% formativo · Nota {grade_text}"
    )
    with st.expander(label,expanded=True):
        a,b,c=st.columns(3)
        a.metric("Avance formativo",f"{progress_pct:.0f} %")
        b.metric("Evaluaciones oficiales",f"{official['completed']} de 2")
        c.metric("Nota del curso",grade_text)

        tabs=st.tabs(["Laboratorios","Evaluaciones oficiales"])
        with tabs[0]:
            items=list(progress_data.items())
            cols=st.columns(2)
            for col,(lab_number,definition) in zip(cols,items):
                with col:
                    _render_lab_progress_card(
                        definition["title"],
                        definition["subtitle"],
                        definition["completed"],
                        definition["expected"],
                        definition["percent"],
                        definition.get("stage_rows"),
                    )
        with tabs[1]:
            _render_course1_official_evaluations(official)


def _course2_lab2_official_summary(rows):
    by_key=_course2_lab2_delivery_rows(rows)
    stage9=by_key.get("final_comprehension")
    stage10=by_key.get("final_integrated_design")
    completed=sum(x is not None for x in (stage9,stage10))
    reviewed=sum(
        bool(x and (x.get("teacher_score") is not None or x.get("status")=="reviewed"))
        for x in (stage9,stage10)
    )
    total=None; grade=None
    if stage9 and stage10 and all(
        x.get("teacher_score") is not None or x.get("status")=="reviewed"
        for x in (stage9,stage10)
    ):
        total=_effective_row_score(stage9)+_effective_row_score(stage10)
        grade=_grade(total,100)
    return {
        "stage9":stage9,"stage10":stage10,
        "completed":completed,"reviewed":reviewed,
        "total":total,"grade":grade,
    }




# Pautas canónicas del Curso 2, copiadas desde views/cursos.py al generar este parche.
_C2L1_STAGE9_QUESTIONS_RESULTS = [{'stage': 1,
  'title': 'Cadena vibroacústica',
  'question': 'Una fuerza dinámica actúa sobre un elemento del edificio. ¿Cuál representa mejor la secuencia '
              'física estudiada?',
  'options': ['Fuerza → vibración de la estructura → propagación mecánica → radiación de sonido.',
              'Sonido → masa → fuerza → desaparición de la vibración.',
              'Vibración → fuerza estática → absorción → frecuencia.',
              'Fuerza → sonido aéreo únicamente, sin participación de la estructura.'],
  'correct': 0,
  'explanation': 'Una excitación mecánica puede hacer vibrar la estructura; esa vibración se propaga por '
                 'elementos sólidos y determinadas superficies pueden luego radiar sonido.'},
 {'stage': 1,
  'title': 'Fuente, mecanismo y camino',
  'question': 'Al diagnosticar ruido producido por una bomba, ¿por qué no basta con identificar solamente la '
              'bomba como fuente?',
  'options': ['Porque toda bomba produce exactamente el mismo ruido.',
              'Porque también debemos identificar qué mecanismo genera la excitación y por qué caminos llega '
              'la energía al receptor.',
              'Porque la fuente nunca participa en el problema.',
              'Porque solo interesa medir el nivel acústico del dormitorio.'],
  'correct': 1,
  'explanation': 'El enfoque del laboratorio distingue fuente, mecanismo y caminos de transmisión. Una misma '
                 'bomba puede transmitir energía por apoyos, tuberías y radiación aérea.'},
 {'stage': 2,
  'title': 'Movilidad mecánica',
  'question': 'Dos estructuras reciben la misma fuerza dinámica F(f). Si la estructura A posee mayor '
              'movilidad Y(f), ¿qué esperamos para su velocidad vibratoria v(f)?',
  'options': ['Será menor, porque una mayor movilidad frena la vibración.',
              'Será mayor, porque v(f) = Y(f) · F(f).',
              'Será necesariamente cero.',
              'No puede relacionarse con la movilidad.'],
  'correct': 1,
  'explanation': 'Para una misma fuerza, una mayor movilidad implica una mayor velocidad vibratoria. La '
                 'movilidad es una propiedad dependiente de la estructura y de la frecuencia.'},
 {'stage': 2,
  'title': 'Frecuencia natural',
  'question': 'En el modelo masa–resorte ideal, ¿qué ocurre generalmente con la frecuencia natural si '
              'aumenta la rigidez k y la masa permanece constante?',
  'options': ['Disminuye.',
              'Aumenta.',
              'Permanece siempre igual.',
              'Se convierte en una frecuencia acústica de sala.'],
  'correct': 1,
  'explanation': 'En f₀ = (1/2π)√(k/m), aumentar la rigidez manteniendo la masa eleva la frecuencia '
                 'natural.'},
 {'stage': 2,
  'title': 'Vibración y radiación',
  'question': 'Una superficie presenta una velocidad vibratoria elevada. ¿Podemos concluir solamente con ese '
              'dato que radiará mucho sonido?',
  'options': ['Sí, siempre.',
              'No. También intervienen el área, la frecuencia y la eficiencia de radiación, entre otros '
              'factores.',
              'Sí, pero únicamente bajo 100 Hz.',
              'No, porque una superficie vibrante nunca puede radiar sonido.'],
  'correct': 1,
  'explanation': 'Vibrar mucho no equivale automáticamente a radiar mucho sonido. La potencia radiada '
                 'depende también de la superficie y de su eficiencia de radiación.'},
 {'stage': 3,
  'title': 'Diseño de campaña',
  'question': 'Antes de decidir una medida de control, ¿qué estrategia corresponde al enfoque de diagnóstico '
              'de la Etapa 3?',
  'options': ['Medir únicamente en el receptor y comprar la solución con mayor aislamiento.',
              'Formular hipótesis, medir fuente y caminos candidatos, comparar resultados y realizar una '
              'prueba de confirmación.',
              'Instalar primero el tratamiento y medir solamente después.',
              'Elegir el camino de transmisión solo por inspección visual.'],
  'correct': 1,
  'explanation': 'La Etapa 3 construye el diagnóstico mediante hipótesis, campaña de medición, comparación '
                 'de caminos y pruebas de confirmación.'},
 {'stage': 3,
  'title': 'Comparación de caminos',
  'question': 'Si dos caminos reciben una fuerza dinámica comparable y uno presenta mayor movilidad en la '
              'frecuencia investigada, ¿qué indica el modelo v = Y·F?',
  'options': ['Ese camino tenderá a desarrollar mayor velocidad vibratoria.',
              'Ese camino necesariamente tendrá menor vibración.',
              'La movilidad deja de ser relevante.',
              'Ambos caminos tendrán siempre la misma respuesta.'],
  'correct': 0,
  'explanation': 'Con fuerzas comparables, el camino de mayor movilidad desarrolla mayor velocidad '
                 'vibratoria y puede constituir un camino de transmisión relevante.'},
 {'stage': 3,
  'title': 'Prueba de confirmación',
  'question': '¿Para qué sirve modificar temporalmente un camino sospechoso y observar qué ocurre en el '
              'receptor?',
  'options': ['Para demostrar que cualquier cambio de nivel es una coincidencia.',
              'Para obtener evidencia adicional de si ese camino participa realmente en la transmisión.',
              'Para reemplazar todas las demás mediciones.',
              'Para determinar automáticamente la normativa aplicable.'],
  'correct': 1,
  'explanation': 'Una prueba de confirmación fortalece o debilita la hipótesis causal sobre un camino de '
                 'transmisión.'},
 {'stage': 4,
  'title': 'Del tiempo a la frecuencia',
  'question': '¿Por qué transformamos conceptualmente una fuerza de impacto F(t) a su representación F(f)?',
  'options': ['Porque el impacto contiene energía distribuida en distintas frecuencias y queremos estudiar '
              'cómo responde el piso en cada una.',
              'Porque F(t) y F(f) son dos fuerzas físicas independientes.',
              'Porque la representación temporal no contiene información.',
              'Para eliminar la participación de la estructura.'],
  'correct': 0,
  'explanation': 'El impacto es transitorio y contiene contenido frecuencial. La representación F(f) permite '
                 'relacionar la excitación con la respuesta dinámica del piso por frecuencia.'},
 {'stage': 4,
  'title': 'Mismo impacto, distinto piso',
  'question': 'Dos pisos reciben la misma excitación F(f), pero poseen movilidades diferentes. ¿Qué explica '
              'que sus respuestas vibratorias sean distintas?',
  'options': ['La relación v(f) = Y(f) · F(f).',
              'La fuerza cambia automáticamente de valor al tocar cada piso.',
              'La movilidad solo sirve para ruido aéreo.',
              'Todos los pisos deben responder igual a la misma excitación.'],
  'correct': 0,
  'explanation': 'Con la misma excitación, diferencias en Y(f) producen diferencias en v(f). Esa es la base '
                 'de la comparación realizada en la Etapa 4.'},
 {'stage': 4,
  'title': 'De vibración a sonido',
  'question': 'Después de calcular la velocidad vibratoria v(f), ¿qué idea adicional necesitamos antes de '
              'interpretar el sonido radiado?',
  'options': ['La capacidad de la superficie vibrante para radiar acústicamente.',
              'Solo la temperatura interior del edificio.',
              'La cantidad de preguntas del laboratorio.',
              'Ninguna: v(f) es directamente Lₙ(f).'],
  'correct': 0,
  'explanation': 'La cadena continúa desde v(f) hacia potencia radiada y finalmente nivel de ruido de '
                 'impacto. La respuesta vibratoria no es directamente un nivel acústico.'},
 {'stage': 5,
  'title': 'Curva base Lₙ,₀(f)',
  'question': '¿Qué representa Lₙ,₀(f) en la Etapa 5?',
  'options': ['La mejora del piso flotante.',
              'La predicción por bandas del nivel de ruido de impacto de la losa base antes del tratamiento.',
              'La frecuencia natural del elemento resiliente.',
              'La transmisibilidad de una bomba.'],
  'correct': 1,
  'explanation': 'Lₙ,₀(f) es la referencia espectral de la losa sin el tratamiento que posteriormente se '
                 'diseñará.'},
 {'stage': 5,
  'title': 'Frecuencia crítica',
  'question': '¿Qué papel cumple la frecuencia crítica f_c en el modelo de predicción de la losa?',
  'options': ['Separa dos regímenes de comportamiento/radiación que utilizan expresiones de cálculo '
              'diferentes.',
              'Es siempre igual a la frecuencia natural de un resorte.',
              'Es el único nivel de ruido que debe calcularse.',
              'Indica la masa total de la losa.'],
  'correct': 0,
  'explanation': 'La posición de cada banda respecto de f_c determina el régimen utilizado por el modelo y '
                 'está vinculada al acoplamiento de las ondas de flexión con el aire.'},
 {'stage': 5,
  'title': 'Predicción por bandas',
  'question': '¿Por qué la Etapa 5 construye Lₙ,₀(f) banda por banda en vez de entregar directamente un '
              'único valor?',
  'options': ['Porque el comportamiento de la losa cambia con la frecuencia y el modelo es espectral.',
              'Porque todos los valores de las bandas son idénticos.',
              'Porque la frecuencia no interviene en la respuesta de una placa.',
              'Solo para aumentar la cantidad de cálculos.'],
  'correct': 0,
  'explanation': 'La respuesta y la radiación de la losa dependen de la frecuencia; por eso se construye una '
                 'curva espectral.'},
 {'stage': 6,
  'title': 'Principio del piso flotante',
  'question': '¿Cuál describe mejor el sistema físico estudiado como piso flotante?',
  'options': ['Una masa superior desacoplada de la losa base mediante un elemento resiliente.',
              'Una capa absorbente colocada únicamente en el cielo del recinto.',
              'Una losa más gruesa sin ningún elemento resiliente.',
              'Un sistema que elimina completamente cualquier vibración.'],
  'correct': 0,
  'explanation': 'El piso flotante introduce una masa desacoplada mediante una capa o apoyos resilientes, '
                 'formando un sistema dinámico masa–resorte.'},
 {'stage': 6,
  'title': 'Rigidez dinámica y f₀',
  'question': 'Manteniendo las masas, si el elemento resiliente es más flexible y disminuye su rigidez '
              'dinámica superficial s′, ¿qué tendencia esperamos para f₀?',
  'options': ['f₀ tiende a disminuir.',
              'f₀ tiende a aumentar.',
              'f₀ se hace necesariamente igual a f_c.',
              'La rigidez no influye en f₀.'],
  'correct': 0,
  'explanation': 'En el modelo estudiado una menor rigidez dinámica, manteniendo las masas, reduce la '
                 'frecuencia natural del sistema.'},
 {'stage': 6,
  'title': 'Mejora ΔLₙ(f)',
  'question': '¿Qué representa ΔLₙ(f) en la Etapa 6?',
  'options': ['El nivel final absoluto del piso terminado.',
              'La mejora acústica por banda introducida por la solución respecto de la losa base.',
              'La frecuencia crítica de la losa.',
              'El ruido aéreo de la sala.'],
  'correct': 1,
  'explanation': 'ΔLₙ(f) es una diferencia de niveles que expresa la mejora del tratamiento por banda. '
                 'Todavía no es Lₙ,final(f).'},
 {'stage': 6,
  'title': 'Puentes rígidos',
  'question': '¿Qué efecto puede tener un contacto rígido accidental que puentea el elemento resiliente de '
              'un piso flotante?',
  'options': ['Puede crear un camino mecánico paralelo, aumentar la rigidez equivalente y degradar el '
              'desacoplamiento.',
              'Siempre mejora el aislamiento.',
              'Solo modifica el color del acabado.',
              'No tiene ningún efecto en la transmisión.'],
  'correct': 0,
  'explanation': 'Los puentes rígidos alteran el sistema ideal y pueden degradar fuertemente el desempeño '
                 'previsto del piso flotante.'},
 {'stage': 7,
  'title': 'Curva final',
  'question': 'Si ya conocemos Lₙ,₀(f) y la mejora ΔLₙ(f), ¿cómo construimos la predicción del piso '
              'terminado?',
  'options': ['Lₙ,final(f) = Lₙ,₀(f) − ΔLₙ(f).',
              'Lₙ,final(f) = Lₙ,₀(f) + ΔLₙ(f).',
              'Lₙ,final(f) = ΔLₙ(f) únicamente.',
              'No existe relación entre las tres curvas.'],
  'correct': 0,
  'explanation': 'Como ΔLₙ(f) está definida como mejora en dB respecto de la condición base, se resta banda '
                 'por banda de Lₙ,₀(f).'},
 {'stage': 7,
  'title': 'Selección profesional',
  'question': 'Al seleccionar un sistema real desde catálogo, ¿por qué no basta con escoger el producto con '
              'mayor ΔLw declarado?',
  'options': ['Porque la decisión también debe considerar el desempeño espectral, masa añadida, carga '
              'admisible, espesor y restricciones constructivas.',
              'Porque ΔLw nunca entrega información acústica.',
              'Porque el producto más pesado es siempre mejor.',
              'Porque los catálogos no pueden utilizarse en ingeniería.'],
  'correct': 0,
  'explanation': 'La Etapa 7 combina desempeño acústico y viabilidad constructiva. Un índice ponderado no '
                 'sustituye la evaluación espectral ni las restricciones del proyecto.'},
 {'stage': 8,
  'title': 'NPSH y cavitación',
  'question': 'En el caso de la bomba, NPSH_A ≈ 3,41 m y NPSH_R ≈ 3,8 m. ¿Cuál es la interpretación más '
              'correcta?',
  'options': ['Existe un margen hidráulico negativo y una condición desfavorable compatible con riesgo de '
              'cavitación; por sí sola no demuestra acústicamente que exista cavitación.',
              'La bomba necesariamente produce exactamente 3,8 dB de ruido.',
              'NPSH_A y NPSH_R son niveles acústicos que deben restarse en dB.',
              'Un margen negativo demuestra que el problema es únicamente radiación aérea.'],
  'correct': 0,
  'explanation': 'NPSH_A pertenece a la instalación y NPSH_R a la bomba/catálogo. Un margen negativo es '
                 'evidencia hidráulica desfavorable, pero el diagnóstico de cavitación se fortalece con '
                 'evidencia vibroacústica y operacional.'},
 {'stage': 8,
  'title': 'RPM, Hz y banda de medición',
  'question': 'La bomba gira a 2900 RPM. ¿Cuál relación es correcta para la componente 1×RPM estudiada?',
  'options': ['2900 RPM → 48,33 Hz de frecuencia física → se representa principalmente en la banda de 50 Hz.',
              '2900 RPM → 2900 Hz → banda de 3000 Hz.',
              '2900 RPM → 50 Hz exactos de giro.',
              '2900 RPM no puede convertirse a hertz.'],
  'correct': 0,
  'explanation': 'La frecuencia de giro es 2900/60 ≈ 48,33 Hz. En el espectro por bandas del laboratorio esa '
                 'componente aparece representada principalmente en la banda central de 50 Hz.'},
 {'stage': 8,
  'title': 'Carga por aislador',
  'question': 'La bomba considerada tiene una masa de 79 kg y se reparte uniformemente en 4 apoyos. ¿Cuál es '
              'aproximadamente la carga que llevamos al catálogo por aislador?',
  'options': ['19,75 kg de masa por apoyo, equivalentes a unos 194 N o 43,6 lb de carga.',
              '79 kg y 194 lb por apoyo.',
              '4 kg por apoyo.',
              '2900 lb por apoyo.'],
  'correct': 0,
  'explanation': '79/4 = 19,75 kg por apoyo. El peso correspondiente es aproximadamente 194 N, equivalente a '
                 'unos 43,6 lbf.'},
 {'stage': 8,
  'title': 'Deflexión y frecuencia natural',
  'question': 'Para el ejercicio se adopta una deflexión estática mínima de 19 mm. ¿Qué significa '
              'aproximadamente ese criterio?',
  'options': ['19 mm ≈ 0,75 in y corresponde a una frecuencia natural de aproximadamente 3,62 Hz en el '
              'modelo vertical idealizado.',
              '19 mm = 19 in y corresponde a 48,33 Hz.',
              '19 mm es la carga nominal del resorte.',
              '19 mm es un nivel acústico.'],
  'correct': 0,
  'explanation': '19 mm = 0,019 m ≈ 0,75 in. Aplicando f_n = (1/2π)√(g/δ), se obtiene aproximadamente 3,62 '
                 'Hz.'},
 {'stage': 8,
  'title': 'Catálogo y deflexión de operación',
  'question': 'Un FDS 1-50 declara 50 lb y 0,97 in nominales. Si nuestra carga real es aproximadamente 43,6 '
              'lb, ¿qué debemos comparar con el criterio de 19 mm?',
  'options': ['La deflexión de operación estimada: aproximadamente 0,85 in ≈ 21,5 mm, que supera el criterio '
              'de 19 mm.',
              "Directamente el nombre 'familia de 1 pulgada', sin considerar la carga real.",
              'Solo las 50 lb nominales, ignorando la deflexión.',
              'La frecuencia de 50 Hz del espectro acústico.'],
  'correct': 0,
  'explanation': 'La denominación nominal no basta. Con la aproximación lineal δ_op ≈ δ_nom(F_op/F_nom), la '
                 'carga real entrega alrededor de 0,85 in ≈ 21,5 mm de deflexión de operación.'}]

_C2L2_STAGE9_QUESTIONS_RESULTS = [('Magnitudes de terreno',
  'En una medición en edificio terminado, ¿qué descriptor corresponde cuando el resultado se normaliza '
  'mediante el área de absorción equivalente?',
  ['Lₙ(f)', "L'ₙ(f)", "L'ₙT(f)", 'ΔLw'],
  1,
  "L'ₙ(f) corresponde al nivel normalizado de impactos en terreno cuando la referencia se expresa mediante "
  'absorción equivalente.'),
 ('Curva ISO 717-2',
  'Durante la ponderación de ruido de impacto, una banda presenta Lₙ,i mayor que la referencia. ¿Cómo se '
  'trata esa diferencia?',
  ['Se resta a otra banda favorable.',
   'Se considera una desviación desfavorable dᵢ.',
   'Se elimina del cálculo.',
   'Se promedia con las demás bandas.'],
  1,
  'Para ruido de impacto, solo los excesos positivos sobre la referencia aportan a las desviaciones '
  'desfavorables.'),
 ('Posición límite',
  '¿Cuándo se ha encontrado correctamente la posición límite de la curva de referencia?',
  ['Cuando Σdᵢ=0 dB.',
   'Cuando la posición actual cumple Σdᵢ≤32 dB y 1 dB más abajo ya supera 32 dB.',
   'Cuando la referencia coincide con el espectro en 500 Hz.',
   'Cuando todas las bandas quedan bajo la referencia.'],
  1,
  'La posición límite es el último desplazamiento entero que cumple; un paso adicional de −1 dB debe dejar '
  'de cumplir.'),
 ('Lectura de Lₙ,w',
  'Una vez encontrada la posición límite, ¿dónde se lee Lₙ,w?',
  ['En el máximo del espectro.',
   'En la referencia desplazada a 500 Hz.',
   'En la banda de 100 Hz.',
   'En el promedio de todas las bandas.'],
  1,
  'Lₙ,w se obtiene leyendo la curva de referencia desplazada en 500 Hz.'),
 ('Término Cᵢ',
  '¿Qué función cumple Cᵢ respecto de Lₙ,w?',
  ['Es una reducción física adicional del revestimiento.',
   'Aporta información espectral complementaria al número único.',
   'Sustituye siempre a Lₙ,w.',
   'Indica la masa del piso.'],
  1,
  'Cᵢ complementa Lₙ,w con información sobre la forma espectral; no representa una mejora física adicional.'),
 ('Bajas frecuencias',
  '¿Qué añade Cᵢ,50–2500 frente a Cᵢ?',
  ['Elimina las bandas de 100–2500 Hz.',
   'Incorpora además 50, 63 y 80 Hz a la suma energética.',
   'Cambia el valor normativo de Lₙ,w.',
   'Convierte el resultado en ΔLw.'],
  1,
  'Cᵢ,50–2500 amplía la suma energética hacia 50 Hz para hacer visible información grave adicional.'),
 ('Reducción de revestimiento',
  '¿Cómo se obtiene ΔLw según el procedimiento con piso pesado de referencia?',
  ['Promediando ΔL(f).',
   'Aplicando ΔL(f) al piso de referencia, ponderando la curva tratada y calculando 78−Lₙ,r,w.',
   'Restando Cᵢ a Lₙ,w.',
   'Sumando todas las bandas de ΔL(f).'],
  1,
  'ΔLw no es el promedio de ΔL(f): requiere construir y ponderar el piso de referencia tratado.'),
 ('Mismo ΔLw',
  'Dos revestimientos tienen el mismo ΔLw. ¿Qué conclusión es correcta?',
  ['Tienen necesariamente la misma curva ΔL(f).',
   'Pueden tener formas espectrales de reducción diferentes.',
   'Son idénticos en cualquier piso real.',
   'Tienen el mismo Cᵢ obligatoriamente.'],
  1,
  'Un mismo número único puede resumir curvas espectrales distintas.'),
 ('Ficha técnica',
  'Una ficha de revestimiento declara ΔLw=19 dB. ¿Qué significa?',
  ['Que cualquier piso real reducirá exactamente 19 dB.',
   'Que el revestimiento obtuvo una reducción ponderada de 19 dB bajo el procedimiento/ensayo declarado.',
   'Que el piso final tendrá Lₙ,w=19 dB.',
   'Que Cᵢ=19 dB.'],
  1,
  'ΔLw es una propiedad declarada bajo un procedimiento de referencia y no una promesa de mejora universal '
  'en cualquier sistema.'),
 ('Interpretación profesional',
  '¿Cuál es la forma más correcta de reportar Lₙ,w y Cᵢ?',
  ['Sumarlos siempre y reportar un único valor.',
   'Informar Lₙ,w como descriptor principal y Cᵢ como término espectral asociado, usando la suma solo si el '
   'criterio aplicable lo exige.',
   'Reportar solo Cᵢ.',
   'Reemplazar Lₙ,w por ΔLw.'],
  1,
  'Lₙ,w sigue siendo el descriptor principal; Cᵢ se informa asociado y no se suma automáticamente.')]

_C2L2_S10_Q_RESULTS = [('¿Qué información añade C_I frente a Lₙ,w?',
  ['Una reducción física adicional.',
   'Información sobre la distribución espectral.',
   'La velocidad de giro de la bomba.',
   'La carga del resorte.'],
  1),
 ('Si dos pisos tienen Lₙ,w parecido y C_I distinto, ¿son acústicamente idénticos?',
  ['Sí.',
   'No; la distribución espectral puede ser distinta.',
   'Solo si pesan igual.',
   'Siempre que tengan el mismo revestimiento.'],
  1),
 ('Una coincidencia de 24 Hz en bomba, tubería y estructura significa:',
  ['Causalidad absoluta demostrada.',
   'Evidencia para investigar un camino común, no prueba única de causalidad.',
   'Que existe cavitación obligatoriamente.',
   'Que el piso tiene Lₙ,w=24.'],
  1),
 ('Si la base está aislada pero la tubería es rígida, ¿está resuelto?',
  ['Sí.', 'No; existe un camino paralelo.', 'Sí, si r>1.', 'Solo depende de C_I.'],
  1),
 ('Si existe cavitación, la primera prioridad es:',
  ['Aislar solamente la base.',
   'Investigar/corregir la condición hidráulica en la fuente.',
   'Agregar absorbente al dormitorio.',
   'Bajar Lₙ,w.'],
  1)]


def _render_readonly_answers_block(payload, expected_count=None):
    """Muestra exactamente las respuestas enviadas, sin permitir edición ni revelar pauta."""
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    if not isinstance(answers, dict):
        answers = {}
    if expected_count is None:
        keys = sorted(
            answers.keys(),
            key=lambda x: int(x) if str(x).isdigit() else str(x),
        )
    else:
        keys = [str(i) for i in range(int(expected_count))]

    if not keys:
        st.caption("No hay respuestas individuales registradas en esta entrega.")
        return

    for pos, key in enumerate(keys, start=1):
        value = answers.get(key)
        with st.container(border=True):
            st.markdown(f"**Pregunta {pos}**")
            st.write(value if value not in (None, "") else "Sin respuesta registrada")


def _render_course2_lab1_submission(row, question_key):
    """Detalle formativo del Lab 1 del Curso 2. No genera nota."""
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}

    st.info("Actividad formativa · **sin nota**. Se muestra en modo solo lectura.")

    if question_key == "final_comprehension":
        if payload.get("answers"):
            _render_readonly_answers_block(payload)
        elif payload.get("response"):
            st.write(payload.get("response"))
        else:
            st.caption("La entrega no contiene un desglose individual de respuestas.")
    else:
        shown = False
        for key, label in (
            ("diagnosis", "Diagnóstico"),
            ("analysis", "Análisis"),
            ("solution", "Solución propuesta"),
            ("conclusion", "Conclusión"),
            ("response", "Respuesta enviada"),
        ):
            value = payload.get(key)
            if value not in (None, "", [], {}):
                st.markdown(f"**{label}**")
                st.write(value)
                shown = True
        if not shown:
            # Fallback seguro: mostrar campos simples realmente guardados.
            simple = {
                str(k): v for k, v in payload.items()
                if k not in {"version", "score", "max_score", "finished_at", "rubric_scores"}
                and isinstance(v, (str, int, float, bool))
                and v not in ("", None)
            }
            if simple:
                st.json(simple, expanded=False)
            else:
                st.caption("No hay más detalle legible almacenado en esta entrega.")


def _render_course2_lab2_stage9_submission(row):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}
    st.markdown("#### Mi evaluación enviada")
    st.caption(
        "Tus respuestas se muestran exactamente como quedaron registradas. "
        "Esta vista es solo lectura."
    )
    _render_readonly_answers_block(payload, expected_count=10)
    if payload.get("score") is not None:
        st.caption(f"Puntaje automático registrado al enviar: {payload.get('score')}/40")


def _render_course2_lab2_stage10_submission(row):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}

    st.markdown("#### Mi evaluación enviada")
    st.caption(
        "Se muestra el desarrollo registrado en tu entrega. "
        "No es posible modificarlo desde Mi desempeño."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Lₙ,w enviado", f"{payload.get('lnw', '—')} dB")
    ci = payload.get("ci", "—")
    c2.metric("C_I enviado", f"{ci} dB" if ci != "—" else "—")
    c3.metric(
        "Desarrollo / Comprensión",
        f"{payload.get('design_score', 0)}/40 · {payload.get('comprehension_score', 0)}/20",
    )

    if payload.get("interpretation"):
        st.markdown("**Interpretación del piso**")
        st.write(payload.get("interpretation"))

    pump = payload.get("pump", {}) if isinstance(payload.get("pump"), dict) else {}
    if pump:
        st.markdown("**Bomba y transmisión**")
        st.write(
            f"Frecuencia de excitación: **{pump.get('fe_hz', '—')} Hz** · "
            f"Montaje: **{pump.get('isolator') or '—'}** · "
            f"r: **{pump.get('r', '—')}**"
        )
        if pump.get("path"):
            st.write(f"Camino analizado: {pump.get('path')}")
        if pump.get("parallel_path"):
            st.write(f"Camino paralelo: {pump.get('parallel_path')}")
        controls = pump.get("controls")
        if isinstance(controls, list) and controls:
            st.markdown("**Medidas seleccionadas**")
            for item in controls:
                st.write("• " + str(item))

    st.markdown("**Respuestas de comprensión**")
    _render_readonly_answers_block(payload, expected_count=5)

    st.markdown("**Conclusión profesional**")
    st.write(payload.get("conclusion") or "Sin conclusión registrada.")


def _render_teacher_feedback(row, maximum):
    auto_score = row.get("auto_score")
    teacher_score = row.get("teacher_score")
    if teacher_score is not None:
        cols = st.columns(2)
        cols[0].metric(
            "Puntaje automático",
            f"{float(auto_score or 0):g}/{maximum}",
        )
        cols[1].metric(
            "Puntaje vigente / docente",
            f"{float(teacher_score):g}/{maximum}",
        )
    if row.get("teacher_note"):
        st.info(f"Comentario docente: {row.get('teacher_note')}")


def _c2_answer_tabs_header(row, formative=False):
    reviewed = row.get("teacher_score") is not None or row.get("status") == "reviewed"
    if formative:
        return True
    return bool(reviewed)


def _c2_render_mcq_comparison(payload, questions, release_pauta):
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    if not isinstance(answers, dict):
        answers = {}

    for i, item in enumerate(questions):
        if isinstance(item, dict):
            title = item.get("title") or f"Pregunta {i+1}"
            question = item.get("question") or ""
            options = item.get("options") or []
            correct_idx = int(item.get("correct", 0))
            explanation = item.get("explanation") or ""
        else:
            # Los bancos del Curso 2 utilizan dos formatos históricos:
            # Etapa 9: (titulo, pregunta, opciones, indice_correcto, explicacion)
            # Otros bloques: (pregunta, opciones, indice_correcto[, explicacion])
            if len(item) >= 5 and isinstance(item[2], (list, tuple)):
                title = str(item[0])
                question = str(item[1])
                options = list(item[2])
                correct_idx = int(item[3])
                explanation = str(item[4] or "")
            else:
                title = f"Pregunta {i+1}"
                question = str(item[0]) if len(item) > 0 else ""
                options = list(item[1]) if len(item) > 1 and isinstance(item[1], (list, tuple)) else []
                correct_idx = int(item[2]) if len(item) > 2 else 0
                explanation = str(item[3] or "") if len(item) > 3 else ""

        chosen = answers.get(str(i))
        correct = options[correct_idx] if 0 <= correct_idx < len(options) else "—"

        with st.container(border=True):
            st.markdown(f"**{i+1}. {title}**")
            if question:
                st.write(question)
            st.markdown("**Tu respuesta**")
            st.write(chosen if chosen not in (None, "") else "Sin respuesta registrada")

            if release_pauta:
                st.markdown("**Pauta**")
                st.success(correct)
                if explanation:
                    st.caption(explanation)


def _c2_render_feedback_tab(row, reviewed, formative=False):
    note = row.get("teacher_note")
    if note:
        st.info(note)
    elif reviewed:
        st.caption("El docente no dejó una observación general.")
    elif formative:
        st.caption("Actividad formativa sin nota. No hay observación docente registrada.")
    else:
        st.info("La retroalimentación docente estará disponible cuando termine la revisión.")

    if row.get("feedback"):
        st.markdown("**Retroalimentación automática**")
        st.write(row.get("feedback"))


def _c2_render_lab1_stage9_tabs(row):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}
    tabs = st.tabs(["Tus respuestas y pauta", "Rúbrica", "Retroalimentación docente"])

    with tabs[0]:
        st.info("Actividad formativa · sin nota. La pauta se muestra después del envío.")
        _c2_render_mcq_comparison(
            payload,
            _C2L1_STAGE9_QUESTIONS_RESULTS,
            release_pauta=True,
        )

    with tabs[1]:
        rubric = payload.get("rubric_scores", [])
        answers = payload.get("answers", {})
        rows_rubric = []
        for i, item in enumerate(_C2L1_STAGE9_QUESTIONS_RESULTS):
            chosen = answers.get(str(i)) if isinstance(answers, dict) else None
            correct = item["options"][item["correct"]]
            points = (
                float(rubric[i])
                if isinstance(rubric, list) and i < len(rubric)
                else (4.0 if chosen == correct else 0.0)
            )
            rows_rubric.append({
                "Criterio": f"Pregunta {i+1} · {item['title']}",
                "Puntaje": f"{points:g}/4",
                "Nivel": "Logrado" if points >= 4 else ("En desarrollo" if points > 0 else "No logrado"),
            })
        st.dataframe(pd.DataFrame(rows_rubric), hide_index=True, width="stretch")

    with tabs[2]:
        _c2_render_feedback_tab(row, reviewed=True, formative=True)


def _c2_render_lab1_stage10_tabs(row):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}
    tabs = st.tabs(["Tus respuestas y pauta", "Rúbrica", "Retroalimentación docente"])

    with tabs[0]:
        st.info("Actividad formativa · sin nota. La pauta se muestra después del envío.")

        impacto = payload.get("impacto", {}) if isinstance(payload.get("impacto"), dict) else {}
        inst = payload.get("instalaciones", {}) if isinstance(payload.get("instalaciones"), dict) else {}
        informe = payload.get("informe", {}) if isinstance(payload.get("informe"), dict) else {}

        st.markdown("#### Tu desarrollo · ruido de impacto")
        st.write(f"Secuencia: {' → '.join([x for x in impacto.get('secuencia', []) if x]) or 'Sin completar'}")
        st.write(f"Lₙ,₀(500): {impacto.get('ln0_500','—')} dB")
        st.write(f"m’ᵣ: {impacto.get('mr','—')} kg/m² · f₀: {impacto.get('f0','—')} Hz")
        st.write(f"Solución seleccionada: {impacto.get('solucion') or '—'}")
        if impacto.get("justificacion"):
            st.write(f"Justificación: {impacto.get('justificacion')}")

        st.markdown("#### Tu desarrollo · bomba e instalaciones")
        st.write(f"fₑ: {inst.get('fe','—')} Hz")
        st.write(f"NPSHₐ: {inst.get('npsha','—')} m · NPSHᵣ: {inst.get('npshr','—')} m")
        st.write(f"Diagnóstico NPSH: {inst.get('diagnostico_npsh') or '—'}")
        st.write(f"Aislador: {inst.get('aislador') or '—'}")
        st.write(f"fₙ: {inst.get('fn_hz','—')} Hz · T_F: {inst.get('tf','—')}")
        if inst.get("caminos"):
            st.write(f"Caminos: {inst.get('caminos')}")
        if inst.get("medidas"):
            st.write(f"Medidas: {inst.get('medidas')}")

        st.markdown("#### Tu informe")
        st.write(f"Limitación: {informe.get('limitacion') or '—'}")
        st.write(f"Conclusión: {informe.get('conclusion') or '—'}")

        st.markdown("#### Pauta esperada")
        st.success(
            "Impacto: identificar la cadena física, estimar Lₙ,₀, masa reducida y frecuencia natural, "
            "seleccionar una solución compatible con las restricciones y controlar puentes rígidos."
        )
        st.success(
            "Instalaciones: usar 1×RPM como referencia, evaluar NPSH como evidencia hidráulica, "
            "calcular la carga por apoyo, seleccionar el aislador por carga/deflexión y revisar "
            "caminos paralelos por tuberías y soportes."
        )
        st.success(
            "Cierre profesional: las predicciones deben verificarse con cargas reales, especificaciones, "
            "montaje, continuidad resiliente y mediciones cuando corresponda."
        )

    with tabs[1]:
        tech = float(payload.get("puntaje_tecnico", 0) or 0)
        report = float(payload.get("puntaje_informe", 0) or 0)
        st.dataframe(pd.DataFrame([
            {"Criterio": "Desarrollo técnico integrado", "Puntaje": f"{tech:g}/80"},
            {"Criterio": "Informe integrador", "Puntaje": f"{report:g}/20"},
        ]), hide_index=True, width="stretch")

    with tabs[2]:
        _c2_render_feedback_tab(row, reviewed=True, formative=True)


def _c2_render_lab2_stage9_tabs(row, reviewed):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}
    tabs = st.tabs(["Tus respuestas y pauta", "Rúbrica", "Retroalimentación docente"])

    with tabs[0]:
        if not reviewed:
            st.info(
                "Tu entrega está registrada. La pauta se publicará cuando el docente termine la revisión."
            )
        _c2_render_mcq_comparison(
            payload,
            _C2L2_STAGE9_QUESTIONS_RESULTS,
            release_pauta=reviewed,
        )

    with tabs[1]:
        if not reviewed:
            st.info("La rúbrica se habilitará cuando finalice la revisión docente.")
        else:
            answers = payload.get("answers", {})
            rows_rubric = []
            for i, item in enumerate(_C2L2_STAGE9_QUESTIONS_RESULTS):
                chosen = answers.get(str(i)) if isinstance(answers, dict) else None
                if isinstance(item, dict):
                    options = item.get("options") or []
                    correct_idx = int(item.get("correct", 0))
                    title = item.get("title") or f"Pregunta {i+1}"
                elif len(item) >= 5 and isinstance(item[2], (list, tuple)):
                    title = str(item[0])
                    options = list(item[2])
                    correct_idx = int(item[3])
                else:
                    title = f"Pregunta {i+1}"
                    options = list(item[1]) if len(item) > 1 and isinstance(item[1], (list, tuple)) else []
                    correct_idx = int(item[2]) if len(item) > 2 else 0
                correct = options[correct_idx] if 0 <= correct_idx < len(options) else None
                points = 4.0 if chosen == correct else 0.0
                rows_rubric.append({
                    "Criterio": f"Pregunta {i+1} · {title}",
                    "Puntaje": f"{points:g}/4",
                    "Nivel": "Logrado" if points >= 4 else "No logrado",
                })
            st.dataframe(pd.DataFrame(rows_rubric), hide_index=True, width="stretch")

    with tabs[2]:
        _c2_render_feedback_tab(row, reviewed=reviewed, formative=False)



def _c2_render_lab2_stage10_tabs(row, reviewed, progress_rows=None):
    payload = _student_result_payload(row.get("answer"))
    if not isinstance(payload, dict):
        payload = {}

    # Recuperar la curva Lₙ asociada al alumno desde el Laboratorio 1.
    _curve = None
    _ref_freqs = [100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150]
    _ref_vals = [62,62,62,62,62,62,61,60,59,58,57,54,51,48,45,42]

    def _find_curve(value):
        if isinstance(value, dict):
            preferred = (
                "curve", "ln_curve", "ln_values", "spectrum",
                "spectral_curve", "normalized_curve", "impact_curve",
            )
            for key in preferred:
                if key in value:
                    found = _find_curve(value.get(key))
                    if found is not None:
                        return found
            for candidate in value.values():
                found = _find_curve(candidate)
                if found is not None:
                    return found
        elif isinstance(value, (list, tuple)) and len(value) == 16:
            try:
                vals = [float(x) for x in value]
                if all(math.isfinite(x) for x in vals):
                    return vals
            except Exception:
                return None
        return None

    lab1_state = _future_progress_state(
        progress_rows or {},
        "clase-03-impacto-instalaciones-lab-1",
    )
    _curve = _find_curve(lab1_state)

    # Reconstrucción del valor esperado, pero se mostrará SOLO en Rúbrica.
    exp_lnw = None
    exp_ci = None
    exp_shift = None
    ref_shifted = None
    deviations = None
    dev_sum = None
    next_dev_sum = None
    lsum = None

    if _curve is not None:
        def _dev_sum(shift):
            return sum(
                max(0.0, float(y) - (float(r) + float(shift)))
                for y, r in zip(_curve, _ref_vals)
            )

        for sh in range(-40, 61):
            if _dev_sum(sh) <= 32.0 + 1e-9 and _dev_sum(sh - 1) > 32.0 + 1e-9:
                exp_shift = int(sh)
                break

        if exp_shift is not None:
            ref_shifted = [float(r) + exp_shift for r in _ref_vals]
            deviations = [
                max(0.0, float(y) - float(rs))
                for y, rs in zip(_curve, ref_shifted)
            ]
            dev_sum = sum(deviations)
            next_dev_sum = _dev_sum(exp_shift - 1)
            exp_lnw = int(round(_ref_vals[_ref_freqs.index(500)] + exp_shift))
            lsum = 10.0 * math.log10(
                sum(10.0 ** (float(v) / 10.0) for v in _curve[:15])
            )
            exp_ci = int(round(lsum)) - 15 - exp_lnw

    tabs = st.tabs(["Tus respuestas y desarrollo", "Rúbrica y pauta", "Retroalimentación docente"])

    # ============================================================
    # TAB 1 · SOLO LO QUE HIZO / ENVIÓ EL ALUMNO
    # ============================================================
    with tabs[0]:
        st.markdown("### Mi evaluación enviada")
        st.caption(
            "Aquí se muestra lo que quedó registrado en tu entrega. "
            "Esta vista es solo lectura y no modifica tus respuestas ni tu puntaje."
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Lₙ,w enviado", f"{payload.get('lnw', '—')} dB")
        ci_sent = payload.get("ci", "—")
        c2.metric("C_I enviado", f"{ci_sent} dB" if ci_sent != "—" else "—")
        c3.metric(
            "Desarrollo / Comprensión",
            f"{payload.get('design_score', 0)}/40 · {payload.get('comprehension_score', 0)}/20",
        )

        if _curve is not None:
            st.markdown("#### Curva Lₙ utilizada en tu ejercicio")
            st.caption(
                "Esta es la curva que quedó guardada en tu Laboratorio 1 y que se utilizó como base "
                "para el desarrollo de la evaluación integradora."
            )
            st.dataframe(
                pd.DataFrame({
                    "Frecuencia [Hz]": _ref_freqs,
                    "Tu Lₙ [dB]": [round(float(v), 2) for v in _curve],
                }),
                hide_index=True,
                width="stretch",
            )
        else:
            st.warning(
                "No fue posible recuperar automáticamente la curva Lₙ previa. "
                "El resto de tu entrega sí se mantiene disponible."
            )

        if payload.get("reference_shift") is not None:
            st.markdown("#### Ajuste de la curva")
            st.write(f"**Desplazamiento que quedó registrado:** {payload.get('reference_shift')} dB")

        if payload.get("interpretation"):
            st.markdown("#### Interpretación del piso")
            st.write(payload.get("interpretation"))

        pump = payload.get("pump", {}) if isinstance(payload.get("pump"), dict) else {}
        if pump:
            st.markdown("#### Bomba y transmisión")
            st.write(
                f"**RPM:** {pump.get('rpm','—')}  ·  "
                f"**fₑ:** {pump.get('fe_hz','—')} Hz  ·  "
                f"**Montaje:** {pump.get('isolator') or '—'}  ·  "
                f"**fₙ:** {pump.get('fn_hz','—')} Hz  ·  "
                f"**r:** {pump.get('r','—')}"
            )
            if pump.get("path"):
                st.write(f"**Camino analizado:** {pump.get('path')}")
            if pump.get("parallel_path"):
                st.write(f"**Camino paralelo:** {pump.get('parallel_path')}")
            controls = pump.get("controls")
            if isinstance(controls, list) and controls:
                st.markdown("**Medidas seleccionadas**")
                for item in controls:
                    st.write("• " + str(item))

        st.markdown("#### Respuestas de comprensión")
        _render_readonly_answers_block(payload, expected_count=5)

        st.markdown("#### Conclusión profesional")
        st.write(payload.get("conclusion") or "Sin conclusión registrada.")

    # ============================================================
    # TAB 2 · PAUTA / VALORES ESPERADOS / COMPARACIÓN
    # ============================================================
    with tabs[1]:
        if not reviewed:
            st.info(
                "La pauta completa se habilitará cuando finalice la revisión docente. "
                "Mientras tanto puedes revisar íntegramente lo que enviaste en la pestaña anterior."
            )
        else:
            st.markdown("### Pauta y verificación")

            if _curve is not None and exp_lnw is not None:
                st.markdown("#### Verificación de Lₙ,w")
                st.dataframe(
                    pd.DataFrame({
                        "Frecuencia [Hz]": _ref_freqs,
                        "Lₙ alumno [dB]": [round(float(v),2) for v in _curve],
                        "Curva ref. base [dB]": _ref_vals,
                        "Curva ref. desplazada [dB]": [round(float(v),2) for v in ref_shifted],
                        "Desviación desfavorable [dB]": [round(float(v),2) for v in deviations],
                    }),
                    hide_index=True,
                    width="stretch",
                )
                st.write(
                    f"**Desplazamiento válido:** {exp_shift:+d} dB  ·  "
                    f"**Suma de desviaciones:** {dev_sum:.1f} dB  ·  "
                    f"**Con 1 dB adicional:** {next_dev_sum:.1f} dB"
                )
                st.latex(
                    r"\sum_i \max\left[0,\;L_{n,i}-L_{ref,i}^{(desplazada)}\right]\leq 32\ \mathrm{dB}"
                )
                st.success(f"**Lₙ,w esperado = {exp_lnw} dB**")

                st.markdown("#### Verificación de C_I")
                st.write(
                    "Se realiza la suma energética de los valores Lₙ entre 100 y 2500 Hz:"
                )
                st.latex(
                    r"L_{n,\mathrm{sum}}="
                    r"10\log_{10}\left(\sum_{i=100\,Hz}^{2500\,Hz}10^{L_{n,i}/10}\right)"
                )
                st.write(
                    f"Con esta curva: **Lₙ,sum = {lsum:.2f} dB ≈ {int(round(lsum))} dB**."
                )
                st.latex(r"C_I=L_{n,\mathrm{sum}}-15-L_{n,w}")
                st.latex(
                    rf"C_I={int(round(lsum))}-15-{exp_lnw}={exp_ci}\ \mathrm{{dB}}"
                )

                sent_lnw = payload.get("lnw")
                sent_ci = payload.get("ci")
                a,b = st.columns(2)
                a.metric(
                    "Lₙ,w · enviado / esperado",
                    f"{sent_lnw if sent_lnw is not None else '—'} / {exp_lnw} dB",
                )
                b.metric(
                    "C_I · enviado / esperado",
                    f"{sent_ci if sent_ci is not None else '—'} / {exp_ci:+d} dB",
                )

            st.markdown("#### Rúbrica técnica")
            design = float(payload.get("design_score", 0) or 0)
            comprehension = float(payload.get("comprehension_score", 0) or 0)
            st.dataframe(
                pd.DataFrame([
                    {"Criterio": "Desarrollo técnico", "Puntaje": f"{design:g}/40"},
                    {"Criterio": "Comprensión e interpretación", "Puntaje": f"{comprehension:g}/20"},
                ]),
                hide_index=True,
                width="stretch",
            )

            st.markdown("#### Respuestas esperadas de comprensión")
            answers = payload.get("answers", {}) if isinstance(payload.get("answers"), dict) else {}
            for i, item in enumerate(_C2L2_S10_Q_RESULTS):
                correct = item[1][item[2]]
                with st.container(border=True):
                    st.markdown(f"**Pregunta {i+1}**")
                    st.write(item[0])
                    st.markdown("**Tu respuesta**")
                    st.write(answers.get(str(i)) or "Sin respuesta registrada")
                    st.markdown("**Pauta**")
                    st.success(correct)

    # ============================================================
    # TAB 3 · FEEDBACK DOCENTE
    # ============================================================
    with tabs[2]:
        _c2_render_feedback_tab(row, reviewed=reviewed, formative=False)



def _c3_extract_saved_payload(progress_rows):
    """Obtiene el objeto saved del Curso 3 desde las filas de progreso disponibles.

    Tolera distintas formas históricas de almacenamiento del registro.
    """
    candidates = []
    for row in progress_rows or []:
        if not isinstance(row, dict):
            continue
        # Filtrar Curso 3 cuando hay identificadores disponibles.
        blob = " ".join(str(row.get(k, "")) for k in (
            "class_id", "lab_id", "course", "course_name", "lab_name", "title"
        )).lower()
        if blob and not any(x in blob for x in ("curso3", "curso 3", "control de ruido ambiental", "c3")):
            # No descartar si no hay ninguna señal identificadora.
            if any(row.get(k) for k in ("class_id", "lab_id", "course", "course_name", "lab_name")):
                continue

        for key in ("saved", "payload", "data", "progress", "state", "answers", "value"):
            val = row.get(key)
            if isinstance(val, dict):
                candidates.append(val)
            elif isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        candidates.append(parsed)
                except Exception:
                    pass

        # A veces la propia fila ya contiene las claves saved.
        if any(k in row for k in ("c3_s9_formative", "c3_s10_formative", "c3_formative")):
            candidates.append(row)

    # Preferir el candidato que realmente tenga datos de etapas 9/10.
    for obj in reversed(candidates):
        if any(k in obj for k in ("c3_s9_formative", "c3_s10_formative", "c3_formative")):
            return obj
    return candidates[-1] if candidates else {}


def _render_c3_stage_work(saved_obj, stage):
    """Muestra al alumno su propio borrador/trabajo formativo guardado."""
    if not isinstance(saved_obj, dict):
        saved_obj = {}

    formative = saved_obj.get("c3_formative", {}) if isinstance(saved_obj.get("c3_formative"), dict) else {}

    if stage == 9:
        payload = saved_obj.get("c3_s9_formative")
        if not isinstance(payload, dict) or not payload:
            payload = formative.get("s9_comprehension_draft") or formative.get("s9_comprehension") or {}
        st.markdown("#### Mi trabajo · Etapa 9")
        if not payload:
            st.caption("Aún no hay respuestas guardadas en esta etapa.")
            return
        answers = payload.get("answers", {}) if isinstance(payload.get("answers"), dict) else {}
        checked = payload.get("checked", {}) if isinstance(payload.get("checked"), dict) else {}
        total = int(payload.get("total_questions") or max(len(answers), 10))
        completed = int(payload.get("completed_questions") or sum(1 for v in checked.values() if v))
        st.caption(f"{completed} de {total} preguntas comprobadas.")
        for i in range(total):
            with st.container(border=True):
                st.markdown(f"**Pregunta {i+1}**")
                ans = answers.get(str(i))
                st.write(ans if ans not in (None, "") else "Sin respuesta todavía.")
                if checked.get(str(i)):
                    st.caption("Respuesta comprobada.")
        return

    if stage == 10:
        payload = saved_obj.get("c3_s10_formative")
        if not isinstance(payload, dict) or not payload:
            payload = formative.get("s10_integrated_case_draft") or formative.get("s10_integrated_case") or {}
        st.markdown("#### Mi trabajo · Etapa 10")
        if not payload:
            st.caption("Aún no hay trabajo guardado en esta etapa.")
            return

        summary = [
            ("Fuente principal", payload.get("main_source")),
            ("Receptor crítico", payload.get("receptor")),
            ("Punto adicional", payload.get("extra_point")),
            ("Cobertura temporal", payload.get("periods")),
            ("Instrumentación", payload.get("instrument")),
            ("Configuración", payload.get("weighting")),
            ("LAeq P1", payload.get("ans_laeq")),
            ("L10", payload.get("ans_l10")),
            ("L90", payload.get("ans_l90")),
            ("SEL", payload.get("ans_sel")),
            ("Lden", payload.get("ans_lden")),
        ]
        for label, value in summary:
            if value not in (None, "", "Seleccionar"):
                st.markdown(f"**{label}:** {value}")

        if payload.get("variability"):
            st.markdown("**Interpretación L10−L90**")
            st.write(payload.get("variability"))
        if payload.get("limitations"):
            st.markdown("**Limitaciones**")
            st.write(payload.get("limitations"))
        if payload.get("missing"):
            st.markdown("**Información faltante**")
            st.write(payload.get("missing"))
        if payload.get("conclusion"):
            st.markdown("**Conclusión profesional**")
            st.write(payload.get("conclusion"))

        answers = payload.get("answers", {}) if isinstance(payload.get("answers"), dict) else {}
        if answers:
            st.markdown("**Preguntas de comprensión**")
            for key in sorted(answers, key=lambda x: int(x) if str(x).isdigit() else 999):
                with st.container(border=True):
                    st.markdown(f"Pregunta {int(key)+1 if str(key).isdigit() else key}")
                    st.write(answers.get(key) or "Sin respuesta todavía.")
        return

_C3_LAB1_STAGE_TITLES_RESULTS = {
    0: "Introducción al laboratorio",
    1: "Ruido ambiental: fuentes, caminos y receptores",
    2: "Del campo sonoro al sonómetro",
    3: "Del registro temporal a los descriptores",
    4: "Del evento sonoro a su exposición · SEL / LAE",
    5: "Del monitoreo continuo al ciclo diario · LD, LE, LN y Lden",
    6: "Del monitoreo a las fuentes de ruido ambiental",
    7: "Diseño de campañas · HVAC y autopista",
    8: "Medición real con sonómetro online",
    9: "Preguntas de comprensión",
    10: "Diagnóstico acústico de un barrio",
}


def _render_course3_block(rows, progress_rows):
    """Curso 3 con la misma arquitectura visual del Curso 2.

    Laboratorio 1:
    - etapas 0–10 formativas;
    - sin puntaje;
    - sin nota;
    - no alimenta evaluaciones oficiales.
    """
    course3_labs = [
        lab for lab in FUTURE_LABS.values()
        if lab.get("course") == "Control de ruido ambiental"
    ]
    lab1 = next(
        (lab for lab in course3_labs if int(lab.get("number") or 0) == 1),
        None,
    )

    if lab1:
        p1 = _future_lab_progress(lab1, progress_rows)
        # El catálogo futuro todavía conserva títulos antiguos.
        # Para Mi desempeño mostramos los títulos reales vigentes del laboratorio.
        for item in p1.get("stage_rows", []):
            stage = int(item.get("stage") or 0)
            item["title"] = _C3_LAB1_STAGE_TITLES_RESULTS.get(
                stage,
                item.get("title", f"Etapa {stage}"),
            )
    else:
        p1 = {
            "completed": 0,
            "expected": 11,
            "percent": 0.0,
            "stage_rows": [],
        }

    formative_pct = float(p1.get("percent") or 0.0)

    # Las etapas de este laboratorio no crean evaluaciones oficiales.
    official_completed = 0
    official_expected = 2
    official_grade = "Pendiente"

    label = (
        f"Curso 3 · Control de ruido ambiental · "
        f"{formative_pct:.0f}% de avance formativo · Nota {official_grade}"
    )

    with st.expander(label, expanded=True):
        a, b, c = st.columns(3)
        a.metric("Avance formativo", f"{formative_pct:.0f} %")
        b.metric(
            "Evaluaciones oficiales",
            f"{official_completed} de {official_expected}",
        )
        c.metric("Nota del curso", official_grade)

        tabs = st.tabs(["Laboratorios", "Evaluaciones oficiales"])

        with tabs[0]:
            # Igual arquitectura visual que Curso 2:
            # tarjeta de laboratorio + avance + porcentaje + estado + detalle.
            if lab1:
                cols = st.columns(2)
                with cols[0]:
                    _render_lab_progress_card(
                        "Laboratorio 1 · Medición y diagnóstico del ruido ambiental",
                        "Práctica y aplicación · Etapas 0–10 formativas · Laboratorio sin nota",
                        p1["completed"],
                        p1["expected"],
                        p1["percent"],
                        p1.get("stage_rows"),
                    )

                    _c3_saved = _c3_extract_saved_payload(progress_rows)
                    with st.expander("Revisar mi trabajo guardado · Etapas 9 y 10", expanded=False):
                        _work_tab9, _work_tab10 = st.tabs([
                            "Etapa 9 · Comprensión",
                            "Etapa 10 · Integrador",
                        ])
                        with _work_tab9:
                            _render_c3_stage_work(_c3_saved, 9)
                        with _work_tab10:
                            _render_c3_stage_work(_c3_saved, 10)
                # Mantener la segunda columna libre permite incorporar Lab 2
                # posteriormente sin alterar la arquitectura del curso.
                with cols[1]:
                    st.empty()
            else:
                st.info("El Laboratorio 1 todavía no está disponible en el catálogo.")

        with tabs[1]:
            st.caption(
                "El Laboratorio 1 no genera evaluaciones oficiales ni calificación. "
                "Las Etapas 0–10 son actividades formativas y solo alimentan el avance del laboratorio."
            )
            st.info(
                "Las evaluaciones oficiales del Curso 3 aparecerán aquí cuando sean definidas "
                "fuera del Laboratorio 1."
            )


def _render_course2_block(rows, progress_rows):
    lab1_scores=_course2_lab1_rows(rows)
    lab2_official=_course2_lab2_official_summary(rows)

    course2_labs=[
        lab for lab in FUTURE_LABS.values()
        if lab.get("course")=="Control de ruido de impacto y ruido de instalaciones"
    ]
    lab1=next((lab for lab in course2_labs if int(lab.get("number") or 0)==1),None)
    lab2=next((lab for lab in course2_labs if int(lab.get("number") or 0)==2),None)
    p1=_future_lab_progress(lab1,progress_rows) if lab1 else {"completed":0,"expected":0,"percent":0.0,"stage_rows":[]}
    p2=_future_lab_progress(lab2,progress_rows) if lab2 else {"completed":0,"expected":0,"percent":0.0,"stage_rows":[]}

    lab1_delivered=sum(lab1_scores.get(k) is not None for k in ("final_comprehension","final_exam"))
    official_grade=(
        f"{lab2_official['grade']:.1f}"
        if lab2_official["grade"] is not None else "Pendiente"
    )
    # El avance formativo del Curso 2 no es el recorrido de todas las etapas.
    # Se construye únicamente con los puntajes de las Etapas 9 y 10 del Lab 1.
    lab1_formative_score=sum(
        _effective_row_score(lab1_scores.get(k))
        if lab1_scores.get(k) is not None else 0.0
        for k in ("final_comprehension","final_exam")
    )
    formative_pct=max(0.0,min(100.0,100.0*lab1_formative_score/200.0))

    label=(
        f"Curso 2 · Control de ruido de impacto y ruido de instalaciones · "
        f"{formative_pct:.0f}% de avance formativo · Nota {official_grade}"
    )
    with st.expander(label,expanded=True):
        a,b,c=st.columns(3)
        a.metric("Avance formativo",f"{formative_pct:.0f} %")
        b.metric("Evaluaciones oficiales",f"{lab2_official['completed']} de 2")
        c.metric("Nota del curso",official_grade)

        tabs=st.tabs(["Laboratorios","Lab 1 · puntajes formativos","Lab 2 · evaluaciones oficiales"])
        with tabs[0]:
            cols=st.columns(2)
            if lab1:
                with cols[0]:
                    _render_lab_progress_card(
                        "Laboratorio 1 · Ruido de impacto e instalaciones",
                        "Práctica y aplicación · Etapas 9 y 10 con puntaje sin nota",
                        p1["completed"],p1["expected"],p1["percent"],p1.get("stage_rows"),
                    )
            if lab2:
                with cols[1]:
                    _render_lab_progress_card(
                        "Laboratorio 2 · Del espectro al número único",
                        "Evaluación oficial del Curso 2 · ISO 717-2 + instalaciones",
                        p2["completed"],p2["expected"],p2["percent"],p2.get("stage_rows"),
                    )

        with tabs[1]:
            st.caption(
                "Etapas 9 y 10 del Laboratorio 1: puntajes formativos sobre 100, sin nota."
            )
            evaluations=[
                ("Etapa 9 · Preguntas de comprensión",lab1_scores.get("final_comprehension"),100),
                ("Etapa 10 · Desafío integrador",lab1_scores.get("final_exam"),100),
            ]
            for title,row,maximum in evaluations:
                if row is None:
                    with st.expander(f"⏳ {title} · Pendiente"):
                        st.caption("Todavía no existe una entrega registrada.")
                    continue
                reviewed=row.get("teacher_score") is not None or row.get("status")=="reviewed"
                score=_effective_row_score(row)
                with st.expander(f"{'✅' if reviewed else '🕒'} {title} · {score:g}/{maximum} puntos"):
                    c1,c2,c3=st.columns(3)
                    c1.metric("Puntaje",f"{score:g}/{maximum}")
                    c2.metric("Estado","Revisada" if reviewed else "Entregada")
                    c3.metric("Nota","No aplica")
                    st.caption(f"Actividad formativa · sin nota · Entrega: {_result_date(row.get('submitted_at') or row.get('updated_at'))}")
                    if row.get("question_key")=="final_comprehension":
                        _c2_render_lab1_stage9_tabs(row)
                    else:
                        _c2_render_lab1_stage10_tabs(row)

        with tabs[2]:
            st.caption(
                "La calificación oficial del Curso 2 se obtiene con el Laboratorio 2: "
                "Etapa 9 (40 puntos) + Etapa 10 (60 puntos)."
            )
            evals=[
                ("Etapa 9 · Evaluación de comprensión",lab2_official["stage9"],40),
                ("Etapa 10 · Evaluación integradora",lab2_official["stage10"],60),
            ]
            for title,row,maximum in evals:
                if row is None:
                    with st.expander(f"⏳ {title} · Pendiente"):
                        st.caption("Aún no existe una entrega.")
                    continue
                reviewed=row.get("teacher_score") is not None or row.get("status")=="reviewed"
                score=_effective_row_score(row) if reviewed else None
                grade=_grade(score,maximum) if reviewed else None
                summary=(
                    f"✅ {title} · {score:g}/{maximum} · Nota {grade:.1f}"
                    if reviewed else f"🕒 {title} · Entregada · Pendiente de revisión"
                )
                with st.expander(summary):
                    c1,c2,c3=st.columns(3)
                    c1.metric("Puntaje oficial",f"{score:g}/{maximum}" if reviewed else "Pendiente de revisión")
                    c2.metric("Nota",f"{grade:.1f}" if reviewed else "Pendiente")
                    c3.metric("Estado","Revisada" if reviewed else "Entregada")

                    payload=_student_result_payload(row.get("answer"))
                    if isinstance(payload,dict):
                        if row.get("question_key")=="final_comprehension":
                            answers=payload.get("answers",{})
                            st.write(f"Respuestas registradas: {sum(v not in (None,'') for v in answers.values())}/10")
                            _c2_render_lab2_stage9_tabs(row, reviewed)
                        else:
                            st.write(f"Desarrollo técnico: {payload.get('design_score',0)}/40")
                            st.write(f"Comprensión: {payload.get('comprehension_score',0)}/20")
                            _c2_render_lab2_stage10_tabs(row, reviewed, progress_rows)

            if lab2_official["total"] is not None:
                st.success(
                    f"Curso 2 · Puntaje final: {lab2_official['total']:.1f}/100 · "
                    f"Nota final: {lab2_official['grade']:.1f}"
                )



def results_view(client, catalog, user_key):
    """Mi desempeño organizado por curso y preparado para incorporar nuevos laboratorios."""
    header(
        "MI DESEMPEÑO",
        "Tu aprendizaje y calificaciones",
        "Revisa el avance de cada curso, sus laboratorios, puntajes formativos y evaluaciones oficiales.",
    )
    if client is None:
        st.info("Los resultados estarán disponibles cuando la aplicación recupere la conexión permanente.")
        return

    response_class_ids=[
        LABORATORIES[1]["id"],
        LABORATORIES[2]["id"],
        "clase-03-impacto-instalaciones-lab-1",
        "clase-04-impacto-instalaciones-lab-2",
    ]
    try:
        rows=(
            client.table("responses").select("*")
            .eq("user_key",user_key)
            .in_("class_id",response_class_ids)
            .order("updated_at",desc=True)
            .execute().data or []
        )
    except Exception as exc:
        st.warning(f"No fue posible cargar tu desempeño en este momento: {exc}")
        return

    progress_rows=_future_progress_rows(client,user_key)

    official=_official_summary(rows)
    course1_progress=_formative_progress_data(rows)
    c1_expected=sum(item["expected"] for item in course1_progress.values())
    c1_completed=sum(item["completed"] for item in course1_progress.values())

    course2_current=_course2_lab1_rows(rows)
    c2_delivered=sum(
        course2_current.get(k) is not None
        for k in ("final_comprehension","final_exam")
    )

    course2_labs=[
        lab for lab in FUTURE_LABS.values()
        if lab.get("course")=="Control de ruido de impacto y ruido de instalaciones"
    ]
    c2_lab1=next((lab for lab in course2_labs if int(lab.get("number") or 0)==1),None)
    c2_prog=_future_lab_progress(c2_lab1,progress_rows) if c2_lab1 else {
        "completed":0,"expected":0,"percent":0.0
    }

    course3_labs=[
        lab for lab in FUTURE_LABS.values()
        if lab.get("course")=="Control de ruido ambiental"
    ]
    c3_lab1=next((lab for lab in course3_labs if int(lab.get("number") or 0)==1),None)
    c3_prog=_future_lab_progress(c3_lab1,progress_rows) if c3_lab1 else {
        "completed":0,"expected":0,"percent":0.0
    }

    courses_with_progress=0
    if c1_completed or official["completed"]:
        courses_with_progress+=1
    if c2_prog["completed"] or c2_delivered:
        courses_with_progress+=1
    if c3_prog["completed"]:
        courses_with_progress+=1

    labs_with_progress=sum(1 for item in course1_progress.values() if item["completed"])
    if c2_prog["completed"]:
        labs_with_progress+=1
    if c3_prog["completed"]:
        labs_with_progress+=1

    st.markdown("## Resumen del Diplomado")
    st.caption(
        "Este resumen no mezcla notas de cursos distintos. "
        "Cada curso mantiene debajo su propio progreso, evaluaciones y calificación."
    )
    a,b,c,d=st.columns(4)
    a.metric("Cursos con avance",str(courses_with_progress))
    b.metric("Laboratorios con avance",str(labs_with_progress))
    c.metric("Evaluaciones oficiales entregadas",f"{official['completed']}")
    d.metric("Puntajes formativos Curso 2",f"{c2_delivered}/2")

    st.markdown("## Cursos")
    st.caption(
        "Abre cada curso para revisar sus laboratorios. "
        "Esta estructura permite incorporar nuevos cursos y laboratorios sin alargar innecesariamente la página."
    )

    _render_course1_block(rows)
    _render_course2_block(rows,progress_rows)
    _render_course3_block(rows,progress_rows)



_VIEWS = {
    "_results_catalog": _results_catalog,
    "student_sidebar_summary": student_sidebar_summary,
    "results_view": results_view,
}


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)