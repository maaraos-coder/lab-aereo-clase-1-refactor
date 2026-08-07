"""Vista de desempeño y retroalimentación del alumno.

Separa deliberadamente dos conceptos académicos:

* progreso formativo: ejercicios y actividades que preparan al estudiante;
* calificaciones oficiales: exclusivamente Laboratorio 2, etapas 9 y 10.

``app.py`` inyecta las dependencias compartidas antes de ejecutar cada vista.
"""

_LOCAL_NAMES = {
    "run_view", "_bind_runtime", "_VIEWS", "_LOCAL_NAMES",
    "_results_catalog", "_student_result_payload", "_result_date",
    "_friendly_result_label", "_clean_result_rows", "_effective_row_score",
    "_grade", "_answer_release_allowed",
    "_render_stage9_comparison", "_render_stage10_comparison",
    "_formative_progress_data", "_render_formative_progress", "_official_rows", "_official_summary",
    "student_sidebar_summary", "results_view",
}


def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value


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
    """Resume respuestas formativas guardadas, incluidas las preguntas de comprensión."""
    definitions = {
        1: {
            "title": "Laboratorio 1 · Fundamentos y aplicación",
            "subtitle": "Preguntas, ejercicios y actividades de práctica",
            "keys_by_stage": FORMATIVE_PROGRESS_KEYS[1],
        },
        2: {
            "title": "Laboratorio 2 · Preparación para la evaluación",
            "subtitle": "Preguntas de comprensión y actividades previas a las evaluaciones oficiales",
            "keys_by_stage": FORMATIVE_PROGRESS_KEYS[2],
        },
    }

    result = {}
    for lab_number, definition in definitions.items():
        lab_id = LABORATORIES[lab_number]["id"]
        keys_by_stage = definition["keys_by_stage"]
        valid_pairs = {
            (int(stage), str(key))
            for stage, keys in keys_by_stage.items()
            for key in keys
        }
        saved_pairs = {
            (int(row.get("stage") or -1), str(row.get("question_key") or ""))
            for row in rows
            if row.get("class_id") == lab_id
            and (int(row.get("stage") or -1), str(row.get("question_key") or "")) in valid_pairs
        }
        expected = len(valid_pairs)
        completed = len(saved_pairs)
        stage_rows = []
        for stage, keys in sorted(keys_by_stage.items()):
            expected_keys = {str(key) for key in keys}
            completed_keys = {
                key for saved_stage, key in saved_pairs
                if saved_stage == int(stage) and key in expected_keys
            }
            stage_expected = len(expected_keys)
            stage_completed = len(completed_keys)
            stage_rows.append({
                "stage": int(stage),
                "completed": stage_completed,
                "expected": stage_expected,
                "percent": (100.0 * stage_completed / stage_expected) if stage_expected else 0.0,
            })
        result[lab_number] = {
            "title": definition["title"],
            "subtitle": definition["subtitle"],
            "stages": sorted(keys_by_stage),
            "expected": expected,
            "completed": completed,
            "percent": (100.0 * completed / expected) if expected else 0.0,
            "stage_rows": stage_rows,
        }
    return result


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
                    st.write(
                        f"{stage_status} Etapa {item['stage']}: "
                        f"{item['completed']} de {item['expected']} actividades"
                    )


def student_sidebar_summary(client, user_key):
    """Tarjeta lateral compacta: avance formativo y calificaciones oficiales."""
    if not user_key or client is None:
        return
    try:
        rows = (
            client.table("responses").select("*")
            .eq("user_key", user_key)
            .in_("class_id", [LABORATORIES[1]["id"], LABORATORIES[2]["id"]])
            .execute().data or []
        )
    except Exception:
        return

    official = _official_summary(rows)
    progress_data = _formative_progress_data(rows)
    expected = sum(item["expected"] for item in progress_data.values())
    completed = sum(item["completed"] for item in progress_data.values())
    formative_percent = 100.0 * completed / expected if expected else 0
    grade_text = f"{official['grade']:.1f}" if official["grade"] is not None else "—"

    st.markdown(
        f"""
        <div style="background:linear-gradient(145deg,#0b5b91,#0e91c7);border:1px solid #59d4ef;
                    border-radius:14px;padding:.85rem;margin:.8rem 0;color:white">
          <div style="font-weight:800;font-size:.95rem;margin-bottom:.55rem">📘 PROGRESO DEL CURSO</div>
          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem">
            <span>Evaluaciones oficiales</span><b>{official['completed']}/2</b>
          </div>
          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem;margin-top:.35rem">
            <span>Nota del curso</span><b>{grade_text}</b>
          </div>
          <hr style="border:0;border-top:1px solid rgba(255,255,255,.25);margin:.6rem 0">
          <div style="display:flex;justify-content:space-between;gap:.5rem;font-size:.82rem">
            <span>Actividades formativas</span><b>{completed}/{expected}</b>
          </div>
          <div style="height:7px;background:rgba(255,255,255,.22);border-radius:99px;margin-top:.45rem;overflow:hidden">
            <div style="width:{min(100, formative_percent):.1f}%;height:100%;background:#8de7ff"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def results_view(client, catalog, user_key):
    """Expediente del alumno con progreso y revisión publicada al finalizar la corrección docente."""
    header(
        "MI DESEMPEÑO",
        "Tu aprendizaje y calificaciones",
        "Revisa tu progreso formativo y compara tus evaluaciones oficiales con la pauta y la rúbrica.",
    )
    if client is None:
        st.info("Los resultados estarán disponibles cuando la aplicación recupere la conexión permanente.")
        return
    try:
        rows = (
            client.table("responses").select("*")
            .eq("user_key", user_key)
            .in_("class_id", [LABORATORIES[1]["id"], LABORATORIES[2]["id"]])
            .order("updated_at", desc=True).execute().data or []
        )
    except Exception as exc:
        st.warning(f"No fue posible cargar tu desempeño en este momento: {exc}")
        return

    official = _official_summary(rows)
    grade_text = f"{official['grade']:.1f}" if official["grade"] is not None else "Pendiente"
    total_text = f"{official['total']:.1f}/100" if official["total"] is not None else "Pendiente"
    status_text = "Calificación completa" if official["completed"] == 2 else "Evaluación incompleta"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Evaluaciones oficiales", f"{official['completed']} de 2")
    c2.metric("Revisadas por docente", f"{official['reviewed']} de {official['completed']}")
    c3.metric("Puntaje del curso", total_text)
    c4.metric("Nota del curso", grade_text)
    st.caption(status_text)

    st.markdown("## Evaluaciones oficiales · Curso 1")
    st.caption(
        "La calificación del curso se obtiene exclusivamente con el Laboratorio 2: "
        "Etapa 9 (40 puntos) y Etapa 10 (60 puntos)."
    )

    evaluations = [
        ("stage9", "Etapa 9 · Evaluación de comprensión", official["stage9"], 40),
        ("stage10", "Etapa 10 · Aplicación integradora", official["stage10"], 60),
    ]
    for kind, title, row, maximum in evaluations:
        if row is None:
            with st.expander(f"⏳ {title} · Pendiente"):
                st.caption("Todavía no existe una entrega registrada para esta evaluación.")
            continue

        reviewed = row.get("status") == "reviewed" or row.get("teacher_score") is not None
        score = _effective_row_score(row) if reviewed else None
        grade = _grade(score, maximum) if reviewed else None
        icon = "✅" if reviewed else "🕒"
        summary_text = (
            f"{icon} {title} · {score:g}/{maximum} puntos · Nota {grade:.1f}"
            if reviewed
            else f"{icon} {title} · Entregada · Pendiente de revisión"
        )
        with st.expander(summary_text, expanded=False):
            a, b, c = st.columns(3)
            a.metric("Puntaje oficial", f"{score:g}/{maximum}" if reviewed else "Pendiente")
            b.metric("Nota", f"{grade:.1f}" if reviewed else "Pendiente")
            c.metric("Estado", "Revisada" if reviewed else "Pendiente de revisión")
            st.caption(f"Entrega: {_result_date(row.get('submitted_at') or row.get('updated_at'))}")
            if not reviewed:
                st.info(
                    "⏳ **Evaluación pendiente de revisión docente.**  "
                    "Tu entrega está registrada. Cuando el docente finalice la corrección, "
                    "se habilitarán automáticamente la pauta, la rúbrica, el puntaje por criterio "
                    "y los comentarios."
                )

            payload = _student_result_payload(row.get("answer"))
            if not isinstance(payload, dict):
                payload = {}
            allow_answers = _answer_release_allowed(row)
            response_tab, rubric_tab, feedback_tab = st.tabs([
                "Tus respuestas y pauta", "Rúbrica", "Retroalimentación docente",
            ])
            with response_tab:
                if kind == "stage9":
                    _render_stage9_comparison(row, payload, allow_answers)
                else:
                    _render_stage10_comparison(row, payload, allow_answers)
            with rubric_tab:
                if not reviewed:
                    st.info(
                        "⏳ La rúbrica estará disponible cuando el docente finalice la revisión. "
                        "Hasta entonces, tu entrega permanece registrada sin publicar criterios ni puntajes ajustados."
                    )
                elif kind == "stage9":
                    rubric = payload.get("rubric_scores", [])
                    answers = payload.get("answers", {})
                    rows_rubric = []
                    for i, item in enumerate(STAGE9_QUESTIONS):
                        chosen = answers.get(str(i)) if isinstance(answers, dict) else None
                        correct = item["options"][item["correct"]]
                        points = float(rubric[i]) if isinstance(rubric, list) and i < len(rubric) else (4.0 if chosen == correct else 0.0)
                        rows_rubric.append({
                            "Criterio": f"Pregunta {i + 1} · {item['title']}",
                            "Puntaje": f"{points:g}/4",
                            "Nivel alcanzado": "Logrado" if points >= 4 else ("En desarrollo" if points > 0 else "No logrado"),
                        })
                    st.dataframe(pd.DataFrame(rows_rubric), hide_index=True, width="stretch")
                else:
                    rubric = payload.get("rubric_scores", {})
                    if not isinstance(rubric, dict):
                        rubric = {}
                    st.dataframe(pd.DataFrame([
                        {
                            "Criterio": "Diseño técnico del paramento",
                            "Puntaje": f"{float(rubric.get('design', payload.get('design_score', 0) or 0)):g}/40",
                        },
                        {
                            "Criterio": "Comprensión e interpretación",
                            "Puntaje": f"{float(rubric.get('comprehension', payload.get('comprehension_score', 0) or 0)):g}/20",
                        },
                    ]), hide_index=True, width="stretch")
            with feedback_tab:
                note = row.get("teacher_note")
                if note:
                    st.info(note)
                elif reviewed:
                    st.caption("La evaluación fue revisada, pero el docente no dejó una observación general.")
                else:
                    st.info(
                        "⏳ La retroalimentación docente estará disponible cuando la revisión haya finalizado."
                    )
                if reviewed and row.get("feedback"):
                    st.markdown("**Retroalimentación automática**")
                    st.write(row.get("feedback"))

    _render_formative_progress(rows)


_VIEWS = {
    "_results_catalog": _results_catalog,
    "student_sidebar_summary": student_sidebar_summary,
    "results_view": results_view,
}


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
