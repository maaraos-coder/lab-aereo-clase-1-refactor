"""Vistas de cursos, selección de laboratorios y laboratorios futuros.

La lógica se conserva sin cambios. ``app.py`` inyecta las dependencias
compartidas antes de ejecutar cada vista para evitar acoplamientos circulares.
"""

_RUNTIME_PROTECTED = {"run_view", "_bind_runtime", "_VIEWS", "_RUNTIME_PROTECTED"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and name not in _VIEWS:
            module_globals[name] = value

def course_dashboard_impl():
    header("MIS CLASES","Diplomado en Acústica en la Edificación",
           "Selecciona un curso y abre el laboratorio habilitado en la fecha programada.")
    client=_supabase()
    if client is None:
        st.warning("Supabase todavía no está configurado. La aplicación está usando almacenamiento local de prueba.")
        classes=[
            {"id":"clase-01-aislamiento-ruido-aereo","class_number":1,
             "title":"Laboratorio 1",
             "description":"","status":"published","due_at":None},
            {"id":"clase-02-aislamiento-ruido-aereo-minvu","class_number":2,
             "title":"Laboratorio 2",
             "description":"","status":"draft","due_at":None},
        ]
    else:
        classes=_course_classes(client)
    class_by_number={item.get("class_number"):item for item in classes}
    summaries,course_result=_result_summary()
    first_course=ACADEMIC_COURSES[0]
    st.markdown(f"### {first_course['title']}")
    for lab in first_course["labs"]:
        number=lab["number"]
        item=class_by_number.get(number,{})
        opening=_effective_opening(number,item.get("opens_at"),lab["opens_at"])
        released=item.get("status") in ("published","archived")
        if st.session_state.get("role")=="Alumno" and not released:
            continue
        available=released and _is_open(opening)
        if st.session_state.get("role")=="Docente":
            available=True
        summary=summaries[number]
        progress_status=("Pendiente" if summary["answered"]==0 else
                         "Completado" if summary["answered"]>=summary["expected"] else "En progreso")
        if st.session_state.get("role")=="Docente":
            availability=("Publicado para alumnos" if released else
                          "Borrador · oculto para alumnos")
        else:
            availability="Disponible" if available else f"Habilitación: {_opening_label(opening)}"
        st.markdown(
            f'<div class="lesson"><div class="overview-title">LABORATORIO {number}</div>'
            f'<span class="muted">{availability}</span><hr>'
            f'<b>{summary["earned"]:g}/{summary["maximum"]:g} puntos</b><br>'
            f'<span class="muted">Estado: {progress_status} · '
            f'{summary["answered"]} de {summary["expected"]} actividades realizadas</span></div>',
            unsafe_allow_html=True)
        if available and st.button(
            "Continuar laboratorio" if number==ACTIVE_LAB else "Abrir laboratorio",
            key=f"open_lab_{number}",type="primary" if number==ACTIVE_LAB else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_lab=number
            st.session_state["_open_lab_requested"]=True
            st.rerun()

    lab2_released=class_by_number.get(2,{}).get("status") in ("published","archived")
    st.markdown("#### Resultado del curso")
    if st.session_state.get("role")=="Alumno" and not lab2_released:
        st.info("El curso continúa en desarrollo. Tu avance del laboratorio publicado se conserva.")
    elif not course_result["final_done"]:
        st.warning(
            f'**Evaluación final: Pendiente.** Puntaje acumulado actual: '
            f'{course_result["earned"]:g}/{course_result["maximum"]:g} puntos. '
            'La nota final se calculará cuando envíes la evaluación final del Laboratorio 2.'
        )
    else:
        state="Aprobado" if course_result["grade"]>=4.0 else "Reprobado"
        st.success(
            f'**{state}.** Puntaje final: {course_result["earned"]:g}/'
            f'{course_result["maximum"]:g} puntos ({course_result["percent"]:.1f}%). '
            f'Nota final: **{course_result["grade"]:.1f}**.'
        )

    st.markdown("---")
    for course in COURSE_LABS:
        visible_labs=[]
        for lab in course["labs"]:
            row=next((r for r in classes if r.get("id")==lab["id"]),{})
            published=row.get("status") in ("published","archived")
            if st.session_state.get("role")=="Docente" or (published and _is_open(row.get("opens_at") or lab["opens_at"])):
                visible_labs.append((lab,row,published))
        if not visible_labs:
            continue
        st.markdown(f"### {course['course']}")
        columns=st.columns(2)
        for column,(lab,row,published) in zip(columns,visible_labs):
            with column:
                state=("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                st.markdown(
                    f'<div class="lesson"><div class="overview-title">LABORATORIO {lab["number"]}</div>'
                    f'<span class="muted">Programado: {_opening_label(row.get("opens_at") or lab["opens_at"])}</span><hr>'
                    f'<b>{state}</b><br><span class="muted">{lab["focus"]}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abrir laboratorio",key=f'open_{lab["id"]}',use_container_width=True):
                    st.session_state["future_lab_id"]=lab["id"]
                    st.rerun()

def _future_saved_impl(class_id):
    """Return the saved state for the selected student and future class."""
    cache_key=f"future_saved_{class_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    client=_supabase()
    if client is None:
        return {}
    try:
        rows=(client.table("user_progress").select("state_json")
              .eq("class_id",class_id).eq("user_key",st.session_state.user_key)
              .limit(1).execute().data or [])
        state=rows[0].get("state_json",{}) if rows else {}
        state=json.loads(state) if isinstance(state,str) else state
        st.session_state[cache_key]=state
        return state
    except Exception:
        return {}

def _save_future_state_impl(class_id,state):
    client=_supabase()
    st.session_state[f"future_saved_{class_id}"]=state
    if client is None:
        return
    client.table("user_progress").upsert({
        "course_id":COURSE_ID,"class_id":class_id,
        "user_key":st.session_state.user_key,
        "role":st.session_state.get("role","Alumno"),
        "display_name":st.session_state.get("name",""),
        "state_json":state,"updated_at":_now(),
    },on_conflict="class_id,user_key").execute()

def _course2_lab1_stage0_asset(filename, caption):
    """Muestra el asset oficial si existe; de lo contrario deja su espacio identificado."""
    path = ROOT / "assets" / filename
    if path.exists():
        st.image(str(path), width="stretch")
        if caption:
            st.caption(caption)
    else:
        st.info(
            f"Asset pendiente: `{filename}`. "
            "Sube el render definitivo a la carpeta `assets/` conservando exactamente este nombre."
        )


def _course2_lab1_stage0_energy_interactive(class_id, saved):
    """Interactivo táctil del render vibroacústico. No asigna puntaje ni nota."""
    sources = {
        "Pisada": {
            "asset": "curso2_lab1_etapa0_highlight_pisada.webp",
            "title": "Pisada · impacto directo sobre la estructura",
            "chain": r"\text{PIE}\rightarrow F(t)\rightarrow\text{LOSA}\rightarrow\text{PROPAGACIÓN ESTRUCTURAL}\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}",
            "explanation": (
                "La fuerza de impacto entra directamente a la losa. La vibración se propaga por el elemento estructural "
                "y el cielo del dormitorio inmediatamente inferior puede radiar sonido hacia la pareja receptora."
            ),
            "focus": "Primero la estructura: la excitación mecánica ocurre antes de que aparezca el sonido en el aire.",
        },
        "Bomba": {
            "asset": "curso2_lab1_etapa0_highlight_bomba.webp",
            "title": "Bomba centrífuga · dos caminos estructurales simultáneos",
            "chain": r"\text{BOMBA}\rightarrow\begin{cases}\text{BASE}\rightarrow\text{LOSA}\rightarrow\text{ESTRUCTURA}\\\text{TUBERÍA}\rightarrow\text{SOPORTES}\rightarrow\text{ESTRUCTURA}\end{cases}",
            "explanation": (
                "La bomba puede excitar la losa por su base y, al mismo tiempo, introducir vibración en la tubería de impulsión. "
                "La montante y sus soportes pueden transportar esa energía hacia otros pisos, aunque la máquina esté lejos del receptor."
            ),
            "focus": "Aislar solo la base no garantiza controlar el sistema si la tubería crea un puente rígido.",
        },
        "Descarga sanitaria": {
            "asset": "curso2_lab1_etapa0_highlight_sanitaria.webp",
            "title": "Descarga sanitaria · tubería, fijaciones y estructura",
            "chain": r"\text{DESCARGA}\rightarrow\text{RAMAL}\rightarrow\text{BAJANTE}\rightarrow\text{ABRAZADERAS}\rightarrow\text{ESTRUCTURA}\rightarrow\text{RADIACIÓN}",
            "explanation": (
                "El flujo y los cambios de dirección generan fuerzas fluctuantes en la tubería. Las abrazaderas transmiten parte de esa vibración "
                "a muros o losas y, posteriormente, una superficie conectada puede radiar sonido hacia otro recinto."
            ),
            "focus": "La bajante sanitaria es un camino mecánico: el punto crítico puede estar en sus fijaciones y no en el recinto donde se escucha el ruido.",
        },
    }

    selected_key = f"{class_id}_stage0_energy_source"
    selected = st.session_state.get(selected_key)
    if selected not in sources:
        saved_source = saved.get("stage0_energy_source")
        selected = saved_source if saved_source in sources else None
        if selected:
            st.session_state[selected_key] = selected

    explored = saved.get("stage0_energy_explored", [])
    if not isinstance(explored, list):
        explored = []
    explored = [item for item in explored if item in sources]
    if saved.get("stage0_energy_source") in sources and saved.get("stage0_energy_source") not in explored:
        explored.append(saved.get("stage0_energy_source"))

    cols = st.columns(3)
    for col, source in zip(cols, sources):
        with col:
            active = selected == source
            label = f"{'✓ ' if source in explored else ''}{source}"
            if st.button(
                label,
                key=f"stage0_energy_btn_{class_id}_{source}",
                type="primary" if active else "secondary",
                width="stretch",
            ):
                st.session_state[selected_key] = source
                saved["stage0_energy_source"] = source
                if source not in explored:
                    explored.append(source)
                saved["stage0_energy_explored"] = explored
                saved["stage0_energy_path"] = sources[source]["chain"]
                saved["stage0_energy_updated_at"] = _now()
                _save_future_state_impl(class_id, saved)
                st.rerun()

    if selected:
        data = sources[selected]
        image_path = ROOT / "assets" / data["asset"]
        if image_path.exists():
            st.image(str(image_path), width="stretch")
        else:
            _course2_lab1_stage0_asset(
                "curso2_lab1_etapa0_edificio_vibroacustico.webp",
                "Render base del edificio como sistema vibroacústico.",
            )
        with st.container(border=True):
            st.markdown(f"#### {data['title']}")
            st.latex(data["chain"])
            st.write(data["explanation"])
            st.info(data["focus"])
    else:
        _course2_lab1_stage0_asset(
            "curso2_lab1_etapa0_edificio_vibroacustico.webp",
            "Selecciona una fuente para destacar su recorrido de energía en el edificio.",
        )
        st.caption("Toca una de las tres fuentes para comenzar. En móvil no se requiere hover.")

    st.progress(len(explored) / len(sources))
    st.caption(f"Fuentes exploradas: {len(explored)} de {len(sources)} · actividad formativa sin nota.")
    return len(explored), len(sources)


def _future_stage0_mcq(class_id, saved, key, question, options, correct, feedback):
    """Pregunta formativa persistente para la Etapa 0; no asigna puntaje ni nota."""
    state_key = f"{class_id}_{key}"
    record = saved.get(key) if isinstance(saved.get(key), dict) else {}
    previous = record.get("choice")
    if state_key not in st.session_state and previous in options:
        st.session_state[state_key] = previous

    st.markdown(f"**{question}**")
    choice = st.radio(
        "Selecciona una respuesta",
        options,
        index=None,
        key=state_key,
        label_visibility="collapsed",
    )

    if record.get("completed"):
        if record.get("correct"):
            st.success(feedback)
        else:
            st.error("Respuesta incorrecta. Revisa el mecanismo de transmisión y vuelve a intentarlo si lo necesitas.")
        st.caption(f"Respuesta guardada: {record.get('choice', '—')}")

    label = "Actualizar respuesta" if record.get("completed") else "Comprobar y guardar"
    if st.button(label, key=f"save_{state_key}"):
        if choice is None:
            st.warning("Selecciona una alternativa antes de comprobar.")
        else:
            is_correct = choice == correct
            saved[key] = {
                "choice": choice,
                "correct": is_correct,
                "completed": True,
                "updated_at": _now(),
            }
            _save_future_state_impl(class_id, saved)
            st.rerun()


def _render_course2_lab1_stage0(lab, saved):
    """Etapa 0 real del Curso 2 · Laboratorio 1, integrada al flujo futuro existente."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"

    header(
        "ETAPA 0 · LABORATORIO 1",
        "El edificio como sistema vibroacústico",
        "Reconocer cómo la energía puede ingresar al edificio, propagarse por su estructura y radiarse posteriormente como sonido.",
        show_overview=False,
        duration_minutes=20,
    )
    st.caption(f"{lab['course']} · Laboratorio 1")

    st.markdown("### Objetivo de aprendizaje")
    st.markdown(
        """
- Reconocer el edificio como medio de transmisión de energía vibratoria.
- Diferenciar conceptualmente transmisión aérea y estructural.
- Identificar fuente, excitación, propagación, radiación y receptor.
- Reconocer que una misma fuente puede generar simultáneamente ruido aéreo y estructural.
- Comprender que una superficie estructural vibrante puede radiar posteriormente sonido hacia el aire.
        """
    )

    st.markdown("### Apertura")
    st.info(
        "En acústica de edificios no basta con identificar dónde se escucha el ruido. "
        "Para controlarlo necesitamos descubrir dónde se genera la energía, cómo ingresa a la estructura, "
        "por dónde se propaga y qué elemento termina radiándola hacia el receptor."
    )
    st.latex(
        r"\text{FUENTE}\rightarrow\text{EXCITACIÓN}\rightarrow\text{RESPUESTA}"
        r"\rightarrow\text{PROPAGACIÓN}\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
    )

    # La imagen principal se renderiza dentro del interactivo para evitar duplicarla.
    # Antes de elegir una fuente se muestra el render base; después, la misma zona
    # visual cambia a la versión resaltada correspondiente.

    # El interactivo debe quedar inmediatamente asociado al render principal.
    # En móvil los botones son táctiles y se apilan automáticamente si falta ancho.
    st.markdown("### Sigue la energía")
    st.write(
        "Selecciona una fuente para destacar su recorrido y revisar cómo la energía pasa "
        "desde la fuente hacia la estructura y el receptor."
    )
    explored_count, explored_total = _course2_lab1_stage0_energy_interactive(class_id, saved)
    st.caption(f"Fuentes exploradas: {explored_count} de {explored_total}.")

    st.markdown("### 1 · Situación inicial")
    st.write("Observa un edificio residencial en el que pueden coexistir una pisada, una bomba centrífuga, una descarga sanitaria y un ventilador.")
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q1",
        "¿Cuál de estas fuentes puede producir ruido estructural?",
        [
            "A. Solo la pisada",
            "B. La pisada y la bomba",
            "C. Solo la bomba",
            "D. Todas pueden hacerlo dependiendo de cómo estén conectadas al edificio",
        ],
        "D. Todas pueden hacerlo dependiendo de cómo estén conectadas al edificio",
        "Todas pueden introducir energía mecánica en elementos constructivos. Esa energía puede propagarse por losas, muros, pilares, tuberías, soportes u otros elementos y posteriormente producir sonido en otro recinto.",
    )

    st.markdown("### 2 · Ruido aéreo y ruido estructural")
    aerial, structural = st.columns(2)
    with aerial:
        with st.container(border=True):
            st.markdown("#### Ruido aéreo")
            st.latex(r"p\rightarrow v\rightarrow p")
            st.write(
                "La fuente genera primero fluctuaciones de presión en el aire. Esa presión puede hacer vibrar un cerramiento y éste radiar nuevamente al otro lado."
            )
            st.markdown("**Ruido aéreo: primero el aire.**")
    with structural:
        with st.container(border=True):
            st.markdown("#### Ruido estructural")
            st.latex(r"F\rightarrow v\rightarrow p")
            st.write(
                "La fuente introduce primero una fuerza mecánica en la estructura. La vibración se propaga por elementos sólidos y posteriormente una superficie puede radiar sonido al aire."
            )
            st.markdown("**Ruido estructural: primero la estructura.**")

    st.markdown("### 3 · De la vibración al sonido")
    st.latex(r"F(t)\rightarrow v(t)\rightarrow v_n(t)\rightarrow p(t)")
    terms = [
        ("F(t)", "fuerza dinámica"),
        ("v(t)", "velocidad vibratoria"),
        ("vₙ(t)", "componente normal de la vibración de la superficie radiante"),
        ("p(t)", "presión sonora en el aire"),
    ]
    for symbol, meaning in terms:
        st.markdown(f"- **{symbol}:** {meaning}.")
    st.info(
        "En palabras simples: una losa o muro no necesita moverse de manera visible para producir ruido. "
        "Puede vibrar una cantidad extremadamente pequeña y aun así mover suficiente aire para generar sonido audible."
    )

    st.markdown("### 4 · Vibración no es igual a radiación")
    st.latex(r"\text{VIBRACIÓN}\neq\text{RADIACIÓN ACÚSTICA}")
    st.write(
        "Una superficie puede presentar vibración medible y no ser necesariamente un radiador acústico eficiente. "
        "La radiación depende de la frecuencia, la distribución de la vibración, la superficie involucrada y el acoplamiento con el aire. "
        "Más adelante se introducirá la eficiencia de radiación σ."
    )
    _course2_lab1_stage0_asset(
        "curso2_lab1_etapa0_vibracion_radiacion.webp",
        "Relación conceptual entre vibración de una superficie y radiación acústica al aire.",
    )

    st.markdown("### 5 · Ejemplo: pisada")
    st.latex(
        r"\text{PIE}\rightarrow F(t)\rightarrow\text{LOSA}\rightarrow\text{VIBRACIÓN}"
        r"\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
    )

    st.markdown("### 6 · Ejemplo: bomba")
    st.write("Una bomba puede excitar varios caminos simultáneamente:")
    st.latex(r"\text{BOMBA}\rightarrow\text{BASE}\rightarrow\text{LOSA}")
    st.latex(r"\text{BOMBA}\rightarrow\text{TUBERÍA}\rightarrow\text{SOPORTE}\rightarrow\text{ESTRUCTURA}")
    st.latex(r"\text{CARCASA}\rightarrow\text{AIRE}")
    st.warning("Una misma fuente puede utilizar varios caminos simultáneamente.")

    st.markdown("### 7 · Principio profesional")
    st.latex(r"\text{CONTROL EFECTIVO}=\text{CONTROL DEL CAMINO RELEVANTE}")
    with st.container(border=True):
        st.markdown("**Ejemplo 1**")
        st.write("Material absorbente en una sala no necesariamente controla vibración transmitida por una tubería.")
        st.markdown("**Ejemplo 2**")
        st.write("Un aislador bajo un ventilador no necesariamente controla el ruido que viaja por el ducto.")

    st.markdown("### Preguntas de comprensión")
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q2",
        "Una persona escucha una bomba ubicada dos pisos más abajo. ¿Podemos concluir que el sonido viajó solamente por el aire?",
        [
            "A. Sí",
            "B. No, también puede existir transmisión estructural",
            "C. Sí, porque las vibraciones no producen sonido",
            "D. Solo si la bomba trabaja bajo 100 Hz",
        ],
        "B. No, también puede existir transmisión estructural",
        "Correcto. La distancia vertical no permite concluir el camino de transmisión: pueden coexistir radiación aérea y propagación estructural por losas, muros, tuberías o soportes.",
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q3",
        "Una pared presenta vibración medible. ¿Podemos concluir que necesariamente es un radiador acústico eficiente?",
        ["A. Sí", "B. No"],
        "B. No",
        "Correcto. Vibración medible no implica radiación acústica eficiente; la eficiencia depende de frecuencia, patrón vibratorio, superficie y acoplamiento con el aire.",
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q4",
        "¿Cuál secuencia representa mejor un fenómeno de ruido de origen estructural?",
        ["A. p → p", "B. F → v → p", "C. v → F → p", "D. p → F"],
        "B. F → v → p",
        "Correcto. En el ruido de origen estructural una fuerza excita primero la estructura, ésta vibra y luego una superficie puede radiar presión sonora al aire.",
    )

    st.markdown("### Mini caso profesional")
    st.write(
        "Una bomba está instalada sobre aisladores, pero una tubería sale rígidamente desde la bomba y está fijada mediante abrazaderas metálicas directamente al muro."
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_case",
        "¿Cuál es la hipótesis técnica más razonable?",
        [
            "A. Los aisladores necesariamente están defectuosos",
            "B. Debe colocarse material absorbente en el dormitorio",
            "C. Puede existir un camino estructural paralelo por tubería y soportes",
            "D. El problema debe ser exclusivamente aéreo",
        ],
        "C. Puede existir un camino estructural paralelo por tubería y soportes",
        "Un buen aislador bajo la máquina no garantiza el aislamiento del sistema completo si existe otra conexión rígida capaz de puentearlo.",
    )

    st.markdown("### Cierre")
    st.latex(
        r"\text{FUENTE}\rightarrow\text{EXCITACIÓN}\rightarrow\text{RESPUESTA ESTRUCTURAL}"
        r"\rightarrow\text{PROPAGACIÓN}\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
        r"\rightarrow\text{CONTROL}"
    )
    st.success(
        "En las siguientes etapas aprenderemos a cuantificar cada parte de esta cadena. "
        "La primera pregunta será: si dos estructuras reciben exactamente la misma fuerza, ¿vibran necesariamente igual?"
    )

    required = ["stage0_q1", "stage0_q2", "stage0_q3", "stage0_q4", "stage0_case"]
    completed_questions = sum(
        1 for key in required
        if isinstance(saved.get(key), dict) and saved[key].get("completed")
    )
    st.caption(f"Respuestas formativas guardadas: {completed_questions} de {len(required)}")

    if saved.get("done_0"):
        st.success("Etapa 0 completada y guardada en tu progreso.")
    else:
        if st.button("Completar Etapa 0", type="primary", key=f"complete_stage0_{class_id}"):
            if completed_questions < len(required):
                st.warning("Guarda las cinco respuestas formativas antes de completar la etapa.")
            elif explored_count < explored_total:
                st.warning("Explora Pisada, Bomba y Descarga sanitaria en ‘Sigue la energía’ antes de completar la etapa.")
            else:
                saved["done_0"] = True
                saved["updated_0"] = _now()
                _save_future_state_impl(class_id, saved)
                st.rerun()

    nav_left, nav_right = st.columns(2)
    with nav_left:
        st.button("← Anterior", disabled=True, key=f"stage0_prev_{class_id}", width="stretch")
    with nav_right:
        if st.button("Etapa 1 →", key=f"stage0_next_{class_id}", width="stretch"):
            st.session_state[stage_selector_key] = 1
            st.rerun()


def future_lab_view_impl(lab):
    """Renderer de los laboratorios posteriores manteniendo la navegación institucional."""
    class_id=lab["id"]
    saved=_future_saved(class_id)
    current_lab_label=f"📚 Laboratorio {lab['number']} y actividades"
    results_view_label=(
        "📝 Evaluaciones entregadas"
        if st.session_state.get("role")=="Docente"
        else "🎓 Mi desempeño"
    )

    with st.sidebar:
        uc=ROOT/"assets/logos/logo_uc.png"; decon=ROOT/"assets/logos/logo_decon_uc.png"
        if uc.exists(): st.image(str(uc),width=75)
        if decon.exists(): st.image(str(decon),width=130)
        st.markdown("## ◉ LABORATORIO")
        st.markdown(
            f'<div style="background:#0b4f83;border:1px solid #59d4ef;border-radius:12px;'
            f'padding:.75rem .85rem;margin:.35rem 0 .8rem"><b>LABORATORIO {lab["number"]}</b><br>'
            f'<span style="font-size:.78rem;color:#d9f5ff">{lab["course_short"]}</span></div>',
            unsafe_allow_html=True)
        st.caption("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN")
        st.markdown(f"**{st.session_state.name}**  \n{st.session_state.role}")

        # Misma navegación principal utilizada en los laboratorios del Curso 1.
        future_view_key=f"future_main_view_{class_id}"
        future_options=["🏠 Mis clases", results_view_label, current_lab_label]
        if st.session_state.get(future_view_key) not in future_options:
            st.session_state[future_view_key]=current_lab_label
        future_view=st.radio(
            "Vista",
            future_options,
            key=future_view_key,
            help="Selecciona Mis clases, tu desempeño/evaluaciones o la ruta del laboratorio.",
        )
        if future_view != current_lab_label:
            st.session_state.pop("future_lab_id",None)
            st.session_state["main_view"]=future_view
            st.rerun()

        answered=sum(1 for i in range(11) if saved.get(f"done_{i}"))
        st.progress(answered/11)
        st.caption(f"Avance: {answered}/11 etapas · {answered*10}/110 puntos formativos")

        # Herramientas comunes del diplomado.
        formula_popup_button()
        st.button(
            "📕 Generar apunte visual (PDF)",
            key=f"future_pdf_pending_{class_id}",
            width="stretch",
            disabled=True,
            help="La exportación visual de este nuevo laboratorio se habilitará cuando sus etapas estén completamente integradas.",
        )

        selected=st.radio(
            "Ruta de aprendizaje",
            list(range(11)),
            format_func=lambda i:f"Etapa {i} · {lab['stages'][i][0]}",
            key=f"future_stage_{class_id}",
        )

        if st.session_state.get("role")=="Docente":
            # Mantiene los controles docentes con la misma organización visual del Curso 1.
            if "teacher_student_management" in globals():
                with st.expander("⚙️ Gestión de alumnos"):
                    teacher_student_management()
            with st.expander("🔒 Publicación de laboratorios"):
                client=_supabase()
                if client is not None:
                    row=_class_row(class_id)
                    published=row.get("status")=="published"
                    st.caption("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                    if st.button(
                        "Ocultar laboratorio" if published else "Publicar laboratorio",
                        key=f"future_publish_{class_id}",
                        width="stretch",
                    ):
                        client.table("classes").update({
                            "status":"draft" if published else "published","updated_at":_now()
                        }).eq("id",class_id).execute()
                        _clear_course_cache()
                        st.rerun()
            st.caption("Las evaluaciones de los alumnos se revisan en la vista ‘Evaluaciones entregadas’.")

        if st.button("Cerrar sesión",width="stretch"):
            st.session_state.clear(); st.rerun()
        st.caption("Docente: Marco Araos Barría")

    if class_id == "clase-03-impacto-instalaciones-lab-1" and selected == 0:
        _render_course2_lab1_stage0(lab, saved)
        return

    title,objective,concept,activity=lab["stages"][selected]
    stage_minutes=20 if selected not in (9,10) else 35
    header(f"ETAPA {selected} · LABORATORIO {lab['number']}",title,objective)
    st.caption(f"{lab['course']} · Fuente base: {lab['source']} · 4 horas totales")
    left,right=st.columns([1.25,.75])
    with left:
        st.markdown("### Desarrollo técnico")
        st.markdown(concept)
        if selected in (2,3,4,5,8):
            st.markdown("#### Regla de trabajo")
            if "ambiental" in lab["id"]:
                st.latex(r"L_{eq}=10\log_{10}\left(\frac{1}{T}\sum_i t_i\,10^{L_i/10}\right)")
            elif "construccion" in lab["id"]:
                st.latex(r"L_p(r_2)=L_p(r_1)-20\log_{10}(r_2/r_1)")
            elif "impacto" in lab["id"]:
                st.latex(r"L'_{nT}=L_i-10\log_{10}(T/T_0)")
            else:
                st.latex(r"D_{nT}=L_1-L_2+10\log_{10}(T/T_0)")
        st.info("Criterio profesional: registra dato, método, unidad, supuesto e interpretación. Un resultado sin trazabilidad no es verificable.")
    with right:
        st.markdown("### Mapa de decisión")
        st.markdown(f"""
        1. **Fenómeno:** {title}  
        2. **Magnitud:** elegir el indicador correcto.  
        3. **Método:** separar cálculo, medición y estimación.  
        4. **Decisión:** comparar con el criterio aplicable.  
        5. **Verificación:** definir cómo comprobar la medida.
        """)
        st.metric("Tiempo de etapa",f"{stage_minutes} min")

    st.markdown("### Actividad interactiva")
    st.write(activity)
    answer=st.text_area(
        "Desarrollo del alumno",
        value=saved.get(f"answer_{selected}",""),
        height=150,key=f"future_answer_{class_id}_{selected}",
        placeholder="Describe datos, procedimiento, resultado e interpretación.",
    )
    c1,c2,c3=st.columns(3)
    magnitude=c1.selectbox("Magnitud principal",["Seleccionar","Nivel por bandas","Índice único","Tiempo / duración","Vibración","Clase / cumplimiento"],key=f"mag_{class_id}_{selected}")
    method=c2.selectbox("Tipo de evidencia",["Seleccionar","Cálculo","Medición","Modelación","Inspección","Combinación"],key=f"method_{class_id}_{selected}")
    confidence=c3.slider("Confianza en la respuesta",1,5,3,key=f"conf_{class_id}_{selected}")
    if st.button("Guardar y completar etapa",type="primary",key=f"complete_{class_id}_{selected}"):
        if len(answer.strip())<40 or magnitude=="Seleccionar" or method=="Seleccionar":
            st.warning("Completa un desarrollo de al menos 40 caracteres y selecciona magnitud y evidencia.")
        else:
            saved.update({
                f"answer_{selected}":answer,f"magnitude_{selected}":magnitude,
                f"method_{selected}":method,f"confidence_{selected}":confidence,
                f"done_{selected}":True,f"updated_{selected}":_now(),
            })
            _save_future_state(class_id,saved)
            st.success("Etapa guardada. El avance pertenece únicamente a este laboratorio.")
            st.rerun()

    if st.session_state.get("role")=="Docente":
        # Las etapas futuras no siempre incluyen un bloque editable/teacher_solution.
        # No se debe abortar el render por una variable opcional inexistente.
        editable = {}
        with st.expander("🔐 Orientación docente y respuesta esperada"):
            if editable.get("teacher_solution"):
                st.markdown(editable["teacher_solution"])
            st.markdown(f"""
            **Evidencia mínima:** identificación correcta del fenómeno; selección coherente
            de magnitud y método; procedimiento trazable; resultado con unidad; decisión
            vinculada al criterio; medida verificable.

            **Retroalimentación sugerida:** revisar si la respuesta distingue propiedad de
            elemento, desempeño en terreno, exposición y percepción. Penalizar promedios
            aritméticos de decibeles, símbolos intercambiados y conclusiones normativas sin fuente.
            """)

# Enlaces internos para que la vista futura use las implementaciones locales.
def _future_saved(class_id):
    return _future_saved_impl(class_id)

def _save_future_state(class_id, state):
    return _save_future_state_impl(class_id, state)


_VIEWS = {
    "course_dashboard": course_dashboard_impl,
    "_future_saved": _future_saved_impl,
    "_save_future_state": _save_future_state_impl,
    "future_lab_view": future_lab_view_impl,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
