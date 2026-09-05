"""Vista de desempeño y retroalimentación del alumno.

import re
Separa deliberadamente dos conceptos académicos:

* progreso formativo: ejercicios y actividades que preparan al estudiante;
* calificaciones oficiales: exclusivamente Laboratorio 2, etapas 9 y 10.

``app.py`` inyecta las dependencias compartidas antes de ejecutar cada vista.
"""

from core.activities import formative_progress_snapshot

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
    "_render_course1_block", "_render_course2_block", "_course2_lab2_official_summary",
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
    """Entregas formativas oficiales del Curso 2 · Laboratorio 1.

    Etapa 9  -> final_comprehension
    Etapa 10 -> final_exam
    """
    return _latest_response_by_key(
        rows,
        "clase-03-impacto-instalaciones-lab-1",
        {
            "final_comprehension": (9, "final_comprehension"),
            "final_exam": (10, "final_exam"),
        },
    )


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

    # Curso 2 · Lab 1: dos entregas formativas con puntaje.
    course2_lab1=_course2_lab1_rows(rows)
    c2_lab1_delivered=sum(
        course2_lab1.get(k) is not None
        for k in ("final_comprehension","final_exam")
    )

    # Avance formativo de Curso 2 = progreso real del Laboratorio 1 (Etapas 0–10).
    # La app ya persiste este progreso en user_progress.state_json.
    # Usamos la misma fuente que el resto de la vista de resultados y evitamos
    # consultar una tabla inexistente llamada "progress".
    try:
        c2_progress_rows=_future_progress_rows(client,user_key)
        c2_lab1_state=_future_progress_state(
            c2_progress_rows,
            "clase-03-impacto-instalaciones-lab-1",
        )
        c2_total_stages=11
        c2_completed_stages=sum(
            1 for stage in range(c2_total_stages)
            if bool(c2_lab1_state.get(f"done_{stage}"))
        )
        c2_lab1_progress_pct=(
            100.0*c2_completed_stages/c2_total_stages
            if c2_total_stages else 0.0
        )
    except Exception:
        # El panel lateral nunca debe impedir cargar la aplicación.
        c2_lab1_progress_pct=0.0

    # Curso 2 · Lab 2: dos evaluaciones oficiales.
    course2_lab2=_course2_lab2_delivery_rows(rows)
    c2_lab2_delivered=sum(
        course2_lab2.get(k) is not None
        for k in ("final_comprehension","final_integrated_design")
    )

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
    overall_expected=p1["expected"]+p2["expected"]
    overall_completed=p1["completed"]+p2["completed"]
    overall_pct=(100*overall_completed/overall_expected) if overall_expected else 0.0

    label=(
        f"Curso 2 · Control de ruido de impacto y ruido de instalaciones · "
        f"{overall_pct:.0f}% de avance · Nota {official_grade}"
    )
    with st.expander(label,expanded=True):
        a,b,c=st.columns(3)
        a.metric("Avance del curso",f"{overall_pct:.0f} %")
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
                    if row.get("teacher_note"):
                        st.info(f"Comentario docente: {row.get('teacher_note')}")

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
                    c1.metric("Puntaje oficial",f"{score:g}/{maximum}" if reviewed else "Pendiente")
                    c2.metric("Nota",f"{grade:.1f}" if reviewed else "Pendiente")
                    c3.metric("Estado","Revisada" if reviewed else "Pendiente")
                    payload=_student_result_payload(row.get("answer"))
                    if isinstance(payload,dict):
                        if row.get("question_key")=="final_comprehension":
                            answers=payload.get("answers",{})
                            st.write(f"Respuestas registradas: {sum(v not in (None,'') for v in answers.values())}/10")
                        else:
                            st.write(f"Desarrollo técnico: {payload.get('design_score',0)}/40")
                            st.write(f"Comprensión: {payload.get('comprehension_score',0)}/20")
                            st.write(payload.get("conclusion") or "")
                    if row.get("teacher_note"):
                        st.info(f"Comentario docente: {row.get('teacher_note')}")

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

    courses_with_progress=0
    if c1_completed or official["completed"]:
        courses_with_progress+=1
    if c2_prog["completed"] or c2_delivered:
        courses_with_progress+=1

    labs_with_progress=sum(1 for item in course1_progress.values() if item["completed"])
    if c2_prog["completed"]:
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



_VIEWS = {
    "_results_catalog": _results_catalog,
    "student_sidebar_summary": student_sidebar_summary,
    "results_view": results_view,
}


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)