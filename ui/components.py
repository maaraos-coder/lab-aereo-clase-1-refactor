"""Componentes visuales reutilizables de la aplicación.

Las dependencias compartidas se inyectan desde ``app.py`` para conservar
el comportamiento, el estado de Streamlit y las rutas existentes.
"""

_PROTECTED = {'image_data_uri', '_institutional_header_impl', '_line_chart_impl', '_student_card_body', '_image_data_uri_impl', '_PROTECTED', 'student_lesson', '_visual_path', '_student_lesson_impl', 'run_component', 'development_answer', 'formula_card', 'header', 'check', '_development_answer_impl', '__student_card_body_impl', '_check_impl', '_full_matter_impl', '__visual_path_impl', '_COMPONENTS', 'line_chart', '__academic_blocks_impl', '_fallback_figure', '_stage_overview_impl', '_lesson_impl', '_bind_runtime', '_academic_blocks', '_formula_card_impl', '_header_impl', '__fallback_figure_impl', 'lesson', 'institutional_header', 'stage_overview', 'full_matter'}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _PROTECTED and name not in _COMPONENTS:
            module_globals[name] = value

def _stage_overview_impl(stage_number):
    items=STAGE_GUIDE[stage_number]
    cards=[items[0:3],items[3:6],items[6:9]]
    html='<div class="overview">'
    for icon,title,text in cards:
        html+=f'<div class="overview-card"><div class="overview-icon">{icon}</div><div class="overview-title">{title}</div><div class="overview-text">{text}</div></div>'
    st.markdown(html+'</div>',unsafe_allow_html=True)

def _header_impl(kicker,title,desc,show_overview=True,duration_minutes=None):
    match=re.search(r"ETAPA\s+(\d+)",kicker)
    stage_number=int(match.group(1)) if match else None
    minutes = duration_minutes if duration_minutes is not None else STAGE_MINUTES.get(stage_number)
    duration=(f'<div class="time-badge">⏱️ Tiempo de aplicación: {minutes} minutos</div>'
              if minutes is not None else "")
    st.markdown(f'<div class="hero"><span class="tag">{kicker}</span><h1>{title}</h1><p>{desc}</p>{duration}</div>',unsafe_allow_html=True)
    if match and show_overview:
        stage_overview(stage_number)

def _image_data_uri_impl(path):
    if not path.exists():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def _institutional_header_impl():
    uc = ROOT/"assets/logos/logo_uc.png"
    decon = ROOT/"assets/logos/logo_decon_uc.png"
    st.markdown(
        f"""
        <div class="institutional">
          <div class="institutional-left">
            <img class="institutional-uc" src="{image_data_uri(uc)}" alt="Pontificia Universidad Católica de Chile">
            <div class="institutional-copy">
              <div class="institutional-title">Diplomado en Acústica en la Edificación</div>
              <div class="institutional-sub">Escuela de Construcción Civil · Facultad de Ingeniería</div>
            </div>
          </div>
          <img class="institutional-decon" src="{image_data_uri(decon)}" alt="DECON UC">
        </div>
        """,
        unsafe_allow_html=True,
    )

def __academic_blocks_impl(content):
    """Transform the approved Word text into short, readable teaching cards."""
    hidden_phrases=(
        "Puede presentarse","No colocaría","Imagen interactiva propuesta",
        "Visual interactivo principal","Propongo una","La aplicación mostrará",
        "La aplicación podrá","La animación debe","Funcionamiento de la aplicación",
        "También cambiaría","Esta modificación mejora"
    )
    paragraphs=[
        p.strip() for p in content.split("\n\n") if p.strip()
        and not any(phrase.lower() in p.lower() for phrase in hidden_phrases)
    ]
    duration=""
    useful=[]
    for paragraph in paragraphs:
        if paragraph.startswith("## Etapa"):
            continue
        if paragraph.lower().startswith(("duración propuesta:", "tiempo:")) and not duration:
            duration=paragraph
            continue
        useful.append(paragraph)

    heading_pattern=re.compile(
        r"^(?:\d+\.\s+|#{1,4}\s+|Ejercicio(?:\s+\d+)?|Ejemplo(?:\s+sencillo)?|"
        r"Problema|Caso\s+[A-Z0-9]|Idea central|Resultado final|Distribución temática)",
        re.IGNORECASE,
    )
    blocks=[]
    title=""
    body=[]

    def flush():
        nonlocal title,body
        if title or body:
            blocks.append((title or f"Fundamento para la explicación {len(blocks)+1}", "\n\n".join(body)))
        title,body="",[]

    for paragraph in useful:
        first_line=paragraph.splitlines()[0].strip()
        is_short_heading=len(paragraph)<95 and not paragraph.rstrip().endswith((".",":",";"))
        if heading_pattern.match(first_line) or is_short_heading:
            flush()
            title=re.sub(r"^#{1,4}\s*","",paragraph).strip()
        else:
            body.append(paragraph)
            if sum(len(p) for p in body)>1250:
                flush()
    flush()
    return duration,[(t,b) for t,b in blocks if t or b]

def __student_card_body_impl(body):
    """Keep the learner-facing card focused while preserving complete tables."""
    if not body:
        return ""
    if "| ---" in body:
        return body
    paragraphs=[p for p in body.split("\n\n") if p.strip()]
    selected=[]
    length=0
    for paragraph in paragraphs:
        if length+len(paragraph)>720 and selected:
            break
        selected.append(paragraph)
        length+=len(paragraph)
    summary="\n\n".join(selected)
    if len(selected)<len(paragraphs):
        summary+="\n\n> **Idea para recordar:** identifica el fenómeno, la variable que cambia y el efecto esperado antes de aplicar una fórmula."
    return summary

def __visual_path_impl(filename):
    if not filename:
        return None
    candidates=[ROOT/"assets/course_visuals"/filename,ROOT/"LAB_AEREO_CLASE_1/assets/course_visuals"/filename]
    return next((p for p in candidates if p.exists()),None)

def __fallback_figure_impl(symbol):
    if "━━━" in (symbol or ""):
        return '<div class="mini-scene"><div class="mini-source">🏭</div><div class="mini-wave">))) )))</div><div class="mini-receiver">🧑</div><div class="mini-floorwave"></div></div>'
    return f'<div style="font-size:4rem;text-align:center">{symbol or "🔎"}</div>'

def _student_lesson_impl(stage_number):
    lessons=STUDENT_LESSONS.get(stage_number,[])
    if lessons:
        st.markdown('<div class="section-band"><span>🖼️</span><h3>Conceptualización</h3></div>',unsafe_allow_html=True)
        st.caption("Avanza como en una presentación: revisa una figura y su explicación antes de pasar a la siguiente.")
        key=f"lesson_slide_{stage_number}"
        if key not in st.session_state:
            st.session_state[key]=0
        index=max(0,min(st.session_state[key],len(lessons)-1))
        title,definition,observe,image_name,symbol=lessons[index]
        path=_visual_path(image_name)
        visual=f'<img src="{image_data_uri(path)}" alt="{title}">' if path else _fallback_figure(symbol)
        st.markdown(
            f'<div class="learning-grid"><article class="learning-card"><div class="learning-figure">{visual}</div>'
            f'<div class="learning-copy"><div class="learning-kicker">DIAPOSITIVA {index+1} DE {len(lessons)} · DEFINICIÓN ILUSTRADA</div>'
            f'<h3>{title}</h3><p>{definition}</p><div class="observe"><b>Qué observar:</b> {observe}</div></div></article></div>',
            unsafe_allow_html=True,
        )
        dots="".join(f'<span class="{"active" if i==index else ""}">●</span>' for i in range(len(lessons)))
        st.markdown(f'<div class="slide-status">{index+1} / {len(lessons)}</div><div class="slide-dots">{dots}</div>',unsafe_allow_html=True)
        previous,next_col=st.columns(2)
        if previous.button("← Anterior",key=f"prev_slide_{stage_number}",use_container_width=True,disabled=index==0):
            st.session_state[key]=index-1
            st.rerun()
        if next_col.button("Siguiente →",key=f"next_slide_{stage_number}",use_container_width=True,disabled=index==len(lessons)-1):
            st.session_state[key]=index+1
            st.rerun()
    elif stage_number in STAGE_INTROS:
        title,text=STAGE_INTROS[stage_number]
        st.markdown(f'<div class="lesson"><div class="overview-title">ANTES DE COMENZAR</div><h3>{title}</h3><span class="muted">{text}</span></div>',unsafe_allow_html=True)

def _full_matter_impl(stage_number):
    """Render curated learner content and a separate, role-protected teacher guide."""
    student_lesson(stage_number)
    if stage_number==0 or st.session_state.get("role")!="Docente":
        return
    guide=TEACHER_GUIDES.get(stage_number)
    if not guide:
        return
    explanation,questions=guide
    slide_support=TEACHER_SLIDE_SUPPORT.get(stage_number)
    if slide_support:
        slide_index=max(0,min(st.session_state.get(f"lesson_slide_{stage_number}",0),len(slide_support)-1))
        slide_title=STUDENT_LESSONS[stage_number][slide_index][0]
        explanation,question,answer,tip=slide_support[slide_index]
    st.markdown(
        '<div class="teacher-only"><b>🔐 Profundización técnica exclusiva para el docente</b>'
        '<span>La orientación cambia junto con la figura que está visible para el alumno.</span></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Abrir guía docente de esta etapa",expanded=False):
        st.markdown('<div class="teacher-grid">',unsafe_allow_html=True)
        if slide_support:
            st.markdown(f'<div class="teacher-card"><b>Figura visible · {slide_title}</b><p>{explanation}</p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Pregunta vinculada a esta figura</b><p><strong>{question}</strong></p><p><span>Respuesta esperada: {answer}</span></p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Tip técnico para explicarla</b><p>{tip}</p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Conexión con el laboratorio</b><p>{TEACHER_GUIDES[stage_number][0]}</p></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="teacher-card"><b>Cómo conducir la actividad o laboratorio</b><p>{explanation}</p></div>',unsafe_allow_html=True)
            qhtml="".join(f"<li><strong>{q}</strong><br><span>Respuesta esperada: {answer}</span></li>" for q,answer in questions)
            st.markdown(f'<div class="teacher-card"><b>Preguntas y soluciones para el docente</b><ol>{qhtml}</ol></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

def _lesson_impl(title, text):
    st.markdown(f'<div class="lesson"><div class="overview-title">CONCEPTO CLAVE</div><h3>{title}</h3><span class="muted">{text}</span></div>',unsafe_allow_html=True)

def _formula_card_impl(title, latex, variables, use):
    st.markdown(f'<div class="formula"><div style="font-size:.75rem;letter-spacing:.12em;color:#8ee9ff;font-weight:900">ECUACIÓN VISUAL</div><h3 style="color:white;margin:.35rem 0">{title}</h3></div>',unsafe_allow_html=True)
    st.latex(latex)
    c1,c2=st.columns(2)
    c1.markdown(f'<div class="card"><div class="overview-title">VARIABLES Y UNIDADES</div>{variables}</div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="overview-title">CUÁNDO SE UTILIZA</div>{use}</div>',unsafe_allow_html=True)

def _check_impl(key,q,options,correct,explanation):
    st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA DE COMPRENSIÓN</div><div class="question-text">{q}</div></div>',unsafe_allow_html=True)
    choice=st.radio("Selecciona tu respuesta",options,index=None,key=key,label_visibility="collapsed")
    if st.button("Comprobar",key=f"b_{key}"):
        if choice==correct: st.success(f"Correcto. {explanation}")
        elif choice is None: st.warning("Selecciona una respuesta.")
        else: st.error(f"No es correcto. {explanation}")

def _development_answer_impl(key,q,guide):
    """Visible written response with explicit submission and formative guidance."""
    st.markdown(
        f'<div class="question-box"><div class="question-label">EJERCICIO DE DESARROLLO</div>'
        f'<div class="question-text">{q}</div></div>',
        unsafe_allow_html=True,
    )
    answer=st.text_area(
        "Escribe tu respuesta y justificación",
        key=key,
        placeholder="Explica tu decisión utilizando los conceptos estudiados…",
    )
    if st.button("Enviar desarrollo",key=f"b_{key}"):
        if len(answer.strip())<20:
            st.warning("Desarrolla un poco más tu respuesta antes de enviarla.")
        else:
            st.session_state[f"sent_{key}"]=True
            st.success("Respuesta enviada. Compárala con la pauta formativa.")
    if st.session_state.get(f"sent_{key}"):
        st.markdown(
            f'<div class="good"><b>Pauta de comparación:</b> {guide}</div>',
            unsafe_allow_html=True,
        )

def _line_chart_impl(x, series, title, ytitle):
    fig=go.Figure()
    for name,y in series: fig.add_trace(go.Scatter(x=x,y=y,name=name,mode="lines+markers"))
    fig.update_layout(title=title,xaxis_title="Frecuencia (Hz)",yaxis_title=ytitle,height=390,
                      template="plotly_white",margin=dict(l=20,r=20,t=55,b=20))
    fig.update_xaxes(type="log",tickvals=x)
    st.plotly_chart(fig,use_container_width=True)
# Alias locales para que los componentes extraídos conserven sus llamadas internas.
stage_overview = _stage_overview_impl
header = _header_impl
image_data_uri = _image_data_uri_impl
institutional_header = _institutional_header_impl
_academic_blocks = __academic_blocks_impl
_student_card_body = __student_card_body_impl
_visual_path = __visual_path_impl
_fallback_figure = __fallback_figure_impl
student_lesson = _student_lesson_impl
full_matter = _full_matter_impl
lesson = _lesson_impl
formula_card = _formula_card_impl
check = _check_impl
development_answer = _development_answer_impl
line_chart = _line_chart_impl


_COMPONENTS = {
    'stage_overview': _stage_overview_impl,
    'header': _header_impl,
    'image_data_uri': _image_data_uri_impl,
    'institutional_header': _institutional_header_impl,
    '_academic_blocks': __academic_blocks_impl,
    '_student_card_body': __student_card_body_impl,
    '_visual_path': __visual_path_impl,
    '_fallback_figure': __fallback_figure_impl,
    'student_lesson': _student_lesson_impl,
    'full_matter': _full_matter_impl,
    'lesson': _lesson_impl,
    'formula_card': _formula_card_impl,
    'check': _check_impl,
    'development_answer': _development_answer_impl,
    'line_chart': _line_chart_impl,
}

def run_component(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _COMPONENTS[name](*args, **kwargs)
