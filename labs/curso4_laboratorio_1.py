"""Curso 4 · Laboratorio 1 · Ruido en construcción.

Renderer específico reutilizando la infraestructura general del diplomado.
Noise Map Lab permanece como aplicación externa; esta vista conserva guía,
actividades y progreso.
"""

_RUNTIME_PROTECTED = {"run_stage", "_bind_runtime", "_RUNTIME_PROTECTED"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED:
            module_globals[name] = value

CLASS_ID = "clase-07-construccion-lab-1"
NOISEMAP_URL = "https://noisemap-akuzoft.vercel.app/"
STAGE_MINUTES = [10,20,20,20,20,20,20,25,30,25,30]

BS_PLANT = {
    "Rompedor hidráulico montado en retroexcavadora": {
        "laeq10": 88.0,
        "activity": "Rotura de superficie de camino",
        "detail": "Registro BS 5228-1 asociado a equipo de 67 kW.",
    },
    "Mini excavadora con rompedor hidráulico": {
        "laeq10": 83.0,
        "activity": "Rotura de superficie de camino",
        "detail": "Registro asociado a mini excavadora de 1,5 t.",
    },
    "Rompedor neumático manual": {
        "laeq10": 86.0,
        "activity": "Rotura de superficie de camino",
        "detail": "Registro de actividad de rompimiento; revisar siempre la condición del equipo.",
    },
    "Excavadora sobre ruedas": {
        "laeq10": 73.0,
        "activity": "Movimiento de tierras",
        "detail": "Registro de referencia: excavadora de 112 kW / 17 t.",
    },
    "Excavadora sobre orugas": {
        "laeq10": 80.0,
        "activity": "Movimiento de tierras",
        "detail": "Registro de referencia: excavadora de 172 kW / 35 t.",
    },
    "Camión articulado": {
        "laeq10": 81.0,
        "activity": "Movimiento de tierras",
        "detail": "Registro de referencia: camión articulado de aproximadamente 25 t.",
    },
}

def _header(stage, title, purpose):
    header(
        f"ETAPA {stage} · LABORATORIO 1",
        title,
        purpose,
        show_overview=False,
        duration_minutes=STAGE_MINUTES[stage],
    )

def _save_stage_state(lab, saved, stage):
    saved[f"c4l1_updated_{stage}"] = _now()
    _save_future_state(lab["id"], saved)

def _model_button():
    st.link_button(
        "🗺️ Abrir Noise Map Lab",
        NOISEMAP_URL,
        use_container_width=True,
        help="Abre el modelador en otra pestaña y conserva esta guía visible.",
    )
    st.caption(
        "Herramienta educativa de modelación. No se presenta como una cadena normativa validada completa."
    )

def _bs_selector(suffix):
    name = st.selectbox(
        "Equipo / actividad de referencia",
        list(BS_PLANT),
        key=f"c4l1_bs_{suffix}",
    )
    item = BS_PLANT[name]
    c1, c2 = st.columns([0.35, 0.65])
    c1.metric("LAeq,T a 10 m", f"{item['laeq10']:.0f} dB(A)")
    with c2:
        st.markdown(f"**Actividad:** {item['activity']}")
        st.caption(item["detail"])
    st.info(
        "El valor pertenece a un registro de actividad y condición concretos. "
        "No debe transformarse en un nivel universal de toda máquina con el mismo nombre."
    )
    return name, item

def _stage0(lab, saved):
    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 1 · Ruido en el proceso de construcción",
        "Una ruta aplicada para pasar desde datos de maquinaria y actividades de obra hasta una predicción espacial y el diseño verificable de medidas de control.",
        show_overview=False,
        duration_minutes=10,
    )
    active = sum(STAGE_MINUTES)
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Ruta guiada del Laboratorio 1</strong>'
        f'<br><span>{active} min de trabajo activo aproximado</span>'
        f'</div><div><strong>{active} min</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )
    descriptions = [
        "Lee datos acústicos de maquinaria y actividad con trazabilidad BS 5228.",
        "Recupera Lp/Lw y convierte un dato de referencia en una entrada de modelación declarando supuestos.",
        "Comprueba propagación por distancia y empieza a trabajar con el modelador.",
        "Explora altura, factor de suelo G, topografía y receptores en altura.",
        "Combina varias máquinas mediante suma energética y reconoce la fuente dominante.",
        "Introduce ciclos de operación y simultaneidad sin confundir nivel operativo con equivalente.",
        "Evalúa barreras, encierros y controles aplicados en la fuente.",
        "Construye el escenario completo de una obra y agrega tránsito de obra cuando corresponda.",
        "Compara cuantitativamente medidas de control antes/después.",
        "Integra caracterización, modelación, diagnóstico, control y limitaciones.",
    ]
    html = '<div class="route-grid">'
    for stage in range(1, 11):
        title = lab["stages"][stage][0]
        html += (
            f'<div class="route-card"><span class="step">{stage}</span><div>'
            f'<b>{title}</b><p>{descriptions[stage-1]}</p>'
            f'<span class="route-time">⏱️ {STAGE_MINUTES[stage]} min</span></div></div>'
        )
    st.markdown(html + "</div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="good" style="margin-top:1rem"><b>Continuidad con el Curso 3:</b> '
        'no volverás a aprender Lp, Lw o suma energética desde cero. Aquí los aplicarás a ruido de construcción.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warn" style="margin-top:.8rem"><b>Herramienta central:</b> '
        'Noise Map Lab se utiliza desde las etapas aplicadas; Streamlit conserva la guía, actividades y progreso.</div>',
        unsafe_allow_html=True,
    )

def _stage1(lab, saved):
    _header(
        1,
        "Maquinaria de construcción y datos acústicos de referencia",
        "Aprender a leer correctamente los datos de ruido de maquinaria de construcción antes de utilizarlos en una predicción.",
    )

    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:18px;padding:18px 20px;
        background:linear-gradient(135deg,#f7fbff,#eef7ff);margin-bottom:1rem">
          <div style="font-size:.75rem;font-weight:850;letter-spacing:.08em;color:#0b6ea8">
            IDEA CENTRAL
          </div>
          <div style="font-size:1.2rem;font-weight:850;color:#10243b;margin:.35rem 0 .5rem">
            Una “excavadora” no tiene un único nivel de ruido.
          </div>
          <div style="color:#4b6074;line-height:1.55">
            El nivel depende del tamaño de la máquina, potencia, actividad que realiza, carga,
            estado de mantenimiento y forma de operación. Por eso BS 5228 entrega
            <b>registros de equipos en actividades concretas</b>, no un número universal por nombre.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · ¿Qué es BS 5228-1?")
    st.write(
        "BS 5228-1 es una referencia para la predicción, medición y control del ruido "
        "en obras de construcción y sitios abiertos. Su Anexo C reúne datos acústicos "
        "de maquinaria y actividades de obra obtenidos en terreno."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div style="border:1px solid #dbe7f0;border-radius:15px;padding:15px;height:150px;background:#fff">
              <div style="font-weight:850;color:#0b5f98">¿QUÉ ENTREGA?</div>
              <div style="font-size:1.45rem;font-weight:900;color:#172b3f;margin:.3rem 0">LAeq,T a 10 m</div>
              <div style="color:#5f7080;line-height:1.4">Nivel A-ponderado medido durante una actividad representativa.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div style="border:1px solid #dbe7f0;border-radius:15px;padding:15px;height:150px;background:#fff">
              <div style="font-weight:850;color:#0b5f98">¿QUÉ MÁS?</div>
              <div style="font-size:1.45rem;font-weight:900;color:#172b3f;margin:.3rem 0">63 Hz → 8 kHz</div>
              <div style="color:#5f7080;line-height:1.4">Muchas tablas incluyen niveles por bandas de octava a 10 m.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div style="border:1px solid #dbe7f0;border-radius:15px;padding:15px;height:150px;background:#fff">
              <div style="font-weight:850;color:#0b5f98">¿QUÉ DEBES LEER?</div>
              <div style="font-size:1.45rem;font-weight:900;color:#172b3f;margin:.3rem 0">Equipo + actividad</div>
              <div style="color:#5f7080;line-height:1.4">Potencia, masa/capacidad y condición operacional forman parte del dato.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 2 · Cómo leer una fila de la norma")
    st.markdown(
        """
        Antes de usar un valor debes identificar, en este orden:

        1. **Actividad** que se estaba realizando.
        2. **Tipo de equipo**.
        3. **Potencia o tamaño** del equipo.
        4. **Magnitud reportada**: normalmente LAeq,T a 10 m.
        5. **Si es un equipo móvil marcado con asterisco**, el dato puede corresponder a LAmax de paso.
        6. **Espectro por octavas**, cuando está disponible.
        """
    )
    st.warning(
        "No copies solo la última columna de la tabla. Si ignoras la actividad y el tamaño, "
        "puedes asignar a tu proyecto un dato que no representa la maquinaria real."
    )

    st.markdown("### 3 · Explora registros reales de referencia")
    selected_name = st.selectbox(
        "Selecciona una máquina / actividad",
        list(BS_PLANT),
        key="c4l1_bs_stage1",
    )
    item = BS_PLANT[selected_name]

    equipment_meta = {
        "Rompedor hidráulico montado en retroexcavadora": ("67 kW", "Rotura de superficie de camino", "C.5 · ref. 1"),
        "Mini excavadora con rompedor hidráulico": ("1,5 t", "Rotura de superficie de camino", "C.5 · ref. 2"),
        "Rompedor neumático manual": ("Manual", "Rotura de superficie de camino", "C.5 · ref. 4"),
        "Excavadora sobre ruedas": ("112 kW · 17 t", "Retiro de superficie rota", "C.5 · ref. 11"),
        "Excavadora sobre orugas": ("172 kW · 35 t", "Movimiento de tierras", "C.5 · ref. 18"),
        "Camión articulado": ("194 kW · 25 t", "Movimiento de tierras / circulación", "C.5 · ref. 16"),
    }
    power_size, activity, reference = equipment_meta[selected_name]

    a, b, ccol, d = st.columns(4)
    a.metric("LAeq,T / LAmax a 10 m", f"{item['laeq10']:.0f} dB(A)")
    b.metric("Equipo / tamaño", power_size)
    ccol.metric("Referencia", reference)
    d.metric("LWA de trabajo*", f"{item['laeq10'] + 28:.0f} dB(A)")
    st.caption(
        "* Para las tablas C.1–C.11, BS 5228 indica que, salvo excepciones, "
        "el LWA usado en ciertos métodos de predicción puede obtenerse sumando 28 dB(A) "
        "al LAeq,T o LAmax a 10 m."
    )

    with st.container(border=True):
        st.markdown(f"#### {selected_name}")
        st.markdown(f"**Actividad representada:** {activity}")
        st.write(item["detail"])
        st.info(
            "Este registro sirve como **dato de referencia**. Para un estudio real se debe "
            "comprobar que la máquina, potencia/capacidad y modo de trabajo sean comparables."
        )

    st.markdown("### 4 · Una misma familia puede variar bastante")
    comparison = pd.DataFrame([
        ["Excavadora sobre ruedas", "112 kW · 17 t", 73],
        ["Excavadora sobre orugas", "172 kW · 35 t", 80],
        ["Mini excavadora con rompedor", "1,5 t", 83],
        ["Retroexcavadora + rompedor hidráulico", "67 kW", 88],
    ], columns=["Equipo / condición", "Tamaño o potencia", "Nivel a 10 m [dB(A)]"])
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.markdown(
        """
        La diferencia no se explica solo por el tamaño. Cambia también **la actividad**:
        excavar, circular, romper pavimento o trabajar en vacío no representan el mismo estado acústico.
        """
    )

    st.markdown("### 5 · ¿De dónde conviene obtener el dato de una máquina?")
    st.markdown(
        """
        BS 5228 plantea una jerarquía práctica:

        **1. Mejor opción:** medir un equipo similar, operando de forma comparable y durante un período representativo.  
        **2. Si no existe medición:** usar datos de los anexos de BS 5228 para equipos y actividades equivalentes.  
        **3. Otra posibilidad:** utilizar un nivel de potencia sonora declarado o reglamentario, ajustándolo al modo real de operación.
        """
    )

    st.markdown("### 6 · Actividad de lectura crítica")
    scenario = st.selectbox(
        "Escenario",
        [
            "Obra con excavadora de 35 t realizando movimiento de tierras",
            "Demolición de pavimento con rompedor hidráulico",
            "Generador pequeño para iluminación de faena",
        ],
        key="c4l1_s1_scenario",
    )
    options = {
        "Obra con excavadora de 35 t realizando movimiento de tierras": "Excavadora sobre orugas",
        "Demolición de pavimento con rompedor hidráulico": "Rompedor hidráulico montado en retroexcavadora",
        "Generador pequeño para iluminación de faena": None,
    }
    expected = options[scenario]

    candidate = st.selectbox(
        "¿Qué harías primero?",
        [
            "Usaría el valor más alto de toda la tabla para ser conservador.",
            "Buscaría un registro con actividad, tipo y tamaño comparables.",
            "Usaría cualquier valor del mismo nombre de máquina.",
            "Convertiría directamente el dato a Lw sin revisar qué magnitud es.",
        ],
        key="c4l1_s1_action",
    )
    if st.button("Comprobar criterio", key="c4l1_s1_check", type="primary", use_container_width=True):
        if candidate.startswith("Buscaría un registro"):
            st.success(
                "Correcto. Primero se busca representatividad del dato; después se realiza la conversión o predicción."
            )
            if expected:
                st.caption(f"En la biblioteca de esta etapa, el registro más cercano sería: **{expected}**.")
            else:
                st.caption(
                    "Para este caso convendría buscar específicamente los registros de generadores del Anexo C, "
                    "porque la biblioteca resumida de esta etapa no contiene todos los equipos de la norma."
                )
        else:
            st.warning(
                "No es suficiente coincidir en el nombre de la máquina ni escoger el valor mayor. "
                "Debes justificar actividad, tamaño y magnitud."
            )

    st.markdown("### 7 · Qué debes llevarte de esta etapa")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.success("**Dato acústico ≠ nombre de máquina**\n\nLa condición de operación es parte del dato.")
    with q2:
        st.success("**10 m es una referencia**\n\nNo confundas LAeq,T a 10 m con LWA.")
    with q3:
        st.success("**Trazabilidad primero**\n\nRegistra tabla, referencia, equipo y actividad.")


def _stage2(lab, saved):
    _header(
        2,
        "Del dato de referencia al modelo acústico",
        "Recuperar Lp y Lw del Curso 3 y convertir un nivel a distancia en una fuente equivalente bajo hipótesis explícitas.",
    )
    name, item = _bs_selector("stage2")
    st.markdown("### Conversión didáctica a potencia sonora equivalente")
    st.latex(r"L_W \\approx L_p + 20\\log_{10}(r)+11-D_c")
    st.caption(
        "Para radiación hemisférica ideal, Q=2 implica Dc≈+3 dB. "
        "La conversión es una aproximación educativa y debe declararse como tal."
    )
    c1, c2 = st.columns(2)
    r = c1.number_input("Distancia del dato [m]", min_value=1.0, value=10.0, step=1.0, key="c4l1_s2_r")
    q = c2.selectbox("Directividad Q", options=[1,2,4,8], index=1, key="c4l1_s2_q")
    dc = 10 * math.log10(float(q))
    lw = item["laeq10"] + 20 * math.log10(float(r)) + 11 - dc
    st.metric("LwA equivalente estimado", f"{lw:.1f} dB(A)")
    st.markdown(
        f"Para **{name}**, usando {item['laeq10']:.0f} dB(A) a {r:.0f} m y Q={q}, "
        f"el valor equivalente estimado es **{lw:.1f} dB(A)**."
    )
    st.warning(
        "Q y G no son lo mismo: Q/Dc describe directividad o espacio de radiación; "
        "G caracteriza el efecto acústico del suelo."
    )

def _stage3(lab, saved):
    _header(
        3,
        "Propagación de maquinaria en aire libre",
        "Comprobar la divergencia geométrica y usar Noise Map Lab para observar cómo cambia el nivel en distintos receptores.",
    )
    st.latex(r"A_{div}=20\\log_{10}(r)+11")
    lw = st.slider("Lw de la fuente [dB(A)]", 80, 125, 105, key="c4l1_s3_lw")
    distances = [5,10,20,40]
    values = [lw - (20 * math.log10(d) + 11) for d in distances]
    st.dataframe(
        pd.DataFrame({"Distancia [m]": distances, "Lp ideal [dB]": [round(v,1) for v in values]}),
        use_container_width=True,
        hide_index=True,
    )
    st.info("En este escenario ideal, duplicar la distancia reduce aproximadamente 6 dB.")
    st.markdown("### Compruébalo en el modelador")
    st.write(
        "Crea una fuente puntual, renómbrala y coloca receptores a 5, 10, 20 y 40 m. "
        "Compara el resultado del motor con la tabla ideal."
    )
    _model_button()

def _stage4(lab, saved):
    _header(
        4,
        "Suelo, topografía y receptores en altura",
        "Separar correctamente el efecto de suelo de la directividad y analizar la geometría tridimensional del receptor.",
    )
    c1, c2, c3 = st.columns(3)
    g = c1.slider("Factor de suelo G", 0.0, 1.0, 0.0, 0.1, key="c4l1_s4_g")
    hs = c2.slider("Altura fuente [m]", 0.1, 6.0, 1.5, 0.1, key="c4l1_s4_hs")
    hr = c3.slider("Altura receptor [m]", 1.0, 12.0, 1.5, 0.5, key="c4l1_s4_hr")
    st.markdown(
        f"**Escenario:** G={g:.1f}, fuente a {hs:.1f} m y receptor a {hr:.1f} m. "
        "Las alturas se consideran respecto de la cota local del terreno."
    )
    st.markdown(
        "### Ensayo guiado\n"
        "1. Compara G=0 y G=1.\n"
        "2. Cambia el receptor de 1,5 m a un piso superior.\n"
        "3. Agrega curvas de nivel.\n"
        "4. Mantén la fuente fija para comparar una sola variable cada vez."
    )
    _model_button()

def _stage5(lab, saved):
    _header(
        5,
        "Múltiples máquinas y suma energética",
        "Combinar fuentes simultáneas, identificar sus aportes y reconocer cuál domina en cada receptor.",
    )
    st.latex(r"L_{\\Sigma}=10\\log_{10}\\left(\\sum_i10^{L_i/10}\\right)")
    c1, c2, c3 = st.columns(3)
    a = c1.slider("Retroexcavadora [dB]", 50, 100, 72, key="c4l1_s5_a")
    b = c2.slider("Generador [dB]", 50, 100, 68, key="c4l1_s5_b")
    d = c3.slider("Martillo [dB]", 50, 100, 78, key="c4l1_s5_c")
    total = 10 * math.log10(sum(10 ** (x / 10) for x in (a,b,d)))
    dominant = max([("Retroexcavadora",a),("Generador",b),("Martillo",d)], key=lambda x:x[1])
    m1, m2 = st.columns(2)
    m1.metric("Nivel combinado", f"{total:.1f} dB")
    m2.metric("Aporte mayor", f"{dominant[0]} · {dominant[1]} dB")
    st.write(
        "En Noise Map Lab revisa la contribución de cada fuente en el receptor. "
        "La fuente dominante no tiene por qué ser la de mayor Lw si la geometría cambia."
    )
    _model_button()

def _stage6(lab, saved):
    _header(
        6,
        "Ciclos de operación y simultaneidad",
        "Incorporar la fracción de tiempo de funcionamiento sin confundir nivel operativo con nivel equivalente del período.",
    )
    st.latex(r"\\Delta L_t=10\\log_{10}(t/T)")
    c1, c2 = st.columns(2)
    base = c1.slider("Nivel durante operación [dB]", 80, 125, 110, key="c4l1_s6_base")
    pct = c2.slider("Tiempo activo [%]", 1, 100, 25, key="c4l1_s6_pct")
    corr = 10 * math.log10(pct / 100)
    eq = base + corr
    m1, m2, m3 = st.columns(3)
    m1.metric("Corrección temporal", f"{corr:.1f} dB")
    m2.metric("Nivel equivalente", f"{eq:.1f} dB")
    m3.metric("Operación", f"{pct}%")
    st.markdown(
        "Prueba en Noise Map Lab el mismo martillo al 100 %, 50 %, 25 % y 10 %. "
        "Después combínalo con una fuente continua."
    )
    _model_button()

def _stage7(lab, saved):
    _header(
        7,
        "Barreras, encierros y control en la fuente",
        "Comprobar cuantitativamente cómo la geometría y la reducción de emisión modifican el nivel receptor.",
    )
    st.markdown("### Barrera · geometría F–B–R")
    c1, c2, c3 = st.columns(3)
    hs = c1.number_input("Altura fuente [m]", 0.1, 20.0, 1.5, 0.1, key="c4l1_s7_hs")
    hb = c2.number_input("Altura barrera [m]", 0.1, 20.0, 2.0, 0.1, key="c4l1_s7_hb")
    hr = c3.number_input("Altura receptor [m]", 0.1, 30.0, 1.5, 0.1, key="c4l1_s7_hr")
    st.write(
        f"Fuente {hs:.1f} m · barrera {hb:.1f} m · receptor {hr:.1f} m. "
        "Primero comprueba línea de visión y después analiza el efecto de la frecuencia."
    )
    st.markdown("### Control en la fuente")
    st.write(
        "El modelador permite representar encierro, semiencierro, silenciador y combinaciones. "
        "La reducción debe proceder de un desempeño declarado o de una hipótesis explícita."
    )
    st.markdown(
        "- compara sin barrera / con barrera;\n"
        "- repite a 125, 500, 1000 y 4000 Hz;\n"
        "- aplica un control de fuente;\n"
        "- registra el receptor antes y después."
    )
    _model_button()

def _stage8(lab, saved):
    _header(
        8,
        "Modelo completo de una obra",
        "Construir el escenario 50 × 40 m del material del curso y obtener un mapa con receptores y contribuciones.",
    )
    st.markdown("### Escenario base")
    st.dataframe(
        pd.DataFrame([
            ["Retroexcavadora",10,20,5,88],
            ["Generador diésel",25,25,5,82],
            ["Martillo neumático",35,10,5,96],
        ], columns=["Fuente","X [m]","Y [m]","Distancia referencia [m]","Lp [dB(A)]"]),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        "1. Estima o define Lw de cada fuente.\n"
        "2. Crea y renombra las tres fuentes.\n"
        "3. Ubica receptores al norte del predio.\n"
        "4. Define área de cálculo y factor G.\n"
        "5. Calcula el mapa y revisa contribuciones.\n"
        "6. Identifica receptor crítico y fuente dominante."
    )
    st.markdown("### Extensión · tránsito de obra")
    st.write(
        "Puedes agregar una Fuente vial para el acceso de camiones e ingresar flujo y velocidad. "
        "El tránsito queda separado de la maquinaria estacionaria."
    )
    _model_button()
    note = st.text_area(
        "Registro técnico del escenario",
        value=saved.get("c4l1_stage8_note", ""),
        key="c4l1_s8_note",
        placeholder="Receptor crítico, fuente dominante, nivel obtenido y supuestos principales.",
    )
    if st.button("Guardar registro del modelo", key="c4l1_s8_save", type="primary"):
        saved["c4l1_stage8_note"] = note
        _save_stage_state(lab, saved, 8)
        st.success("Registro guardado.")

def _stage9(lab, saved):
    _header(
        9,
        "Diseño y comparación de medidas de control",
        "Seleccionar controles desde la fuente dominante y demostrar su reducción mediante comparación antes/después.",
    )
    before = st.number_input("Nivel receptor antes [dB(A)]", 40.0, 120.0, 72.0, 0.1, key="c4l1_s9_before")
    after = st.number_input("Nivel receptor después [dB(A)]", 30.0, 120.0, 64.0, 0.1, key="c4l1_s9_after")
    reduction = before - after
    st.metric("Reducción obtenida", f"{reduction:.1f} dB")
    measures = st.multiselect(
        "Medidas aplicadas",
        ["Reubicación","Reducción del tiempo activo","Barrera","Encierro","Silenciador","Cambio de equipo","Combinación"],
        key="c4l1_s9_measures",
    )
    justification = st.text_area(
        "Justificación técnica",
        value=saved.get("c4l1_stage9_justification", ""),
        key="c4l1_s9_justification",
        placeholder="Indica fuente dominante, por qué seleccionaste la medida y qué cambió en el receptor.",
    )
    _model_button()
    if st.button("Guardar comparación", key="c4l1_s9_save", type="primary"):
        saved["c4l1_stage9_justification"] = justification
        saved["c4l1_stage9_result"] = {
            "before": before,
            "after": after,
            "reduction": reduction,
            "measures": measures,
        }
        _save_stage_state(lab, saved, 9)
        st.success("Comparación guardada.")

def _stage10(lab, saved):
    _header(
        10,
        "Caso integrador · predicción de ruido de construcción",
        "Cerrar el laboratorio construyendo un escenario completo, diagnosticando el problema y justificando una medida de control.",
    )
    checklist = [
        "Caractericé las fuentes y su procedencia acústica",
        "Definí receptores y geometría",
        "Documenté suelo/topografía y alturas",
        "Consideré simultaneidad y ciclos de operación",
        "Calculé el escenario inicial",
        "Identifiqué receptor crítico y fuente dominante",
        "Apliqué una medida de control",
        "Recalculé el escenario",
        "Comparé antes/después",
        "Declaré supuestos y limitaciones",
    ]
    checked = [st.checkbox(item, key=f"c4l1_s10_check_{i}") for i, item in enumerate(checklist)]
    conclusion = st.text_area(
        "Conclusión técnica",
        value=saved.get("c4l1_stage10_conclusion", ""),
        height=220,
        key="c4l1_s10_conclusion",
        placeholder=(
            "Describe fuente dominante, receptor crítico, medida aplicada, reducción obtenida, "
            "supuestos del modelo y antecedentes necesarios para una evaluación formal."
        ),
    )
    _model_button()
    if st.button("Guardar caso integrador", key="c4l1_s10_save", type="primary", use_container_width=True):
        if not all(checked):
            st.warning("Completa la lista de verificación antes de cerrar el caso.")
        elif len(conclusion.strip()) < 180:
            st.warning("Desarrolla una conclusión técnica de al menos 180 caracteres.")
        else:
            saved["c4l1_stage10_conclusion"] = conclusion
            saved["c4l1_stage10_checklist"] = checked
            _save_stage_state(lab, saved, 10)
            st.success("Caso integrador guardado. Por ahora permanece como actividad formativa.")

_STAGES = [
    _stage0, _stage1, _stage2, _stage3, _stage4, _stage5,
    _stage6, _stage7, _stage8, _stage9, _stage10,
]

def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage = max(0, min(int(stage), 10))
    return _STAGES[stage](lab, saved)
