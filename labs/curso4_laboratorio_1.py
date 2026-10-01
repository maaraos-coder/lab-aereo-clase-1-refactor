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

BSI_REFERENCE_URL = "https://knowledge.bsigroup.com/products/code-of-practice-for-noise-and-vibration-control-on-construction-and-open-sites-noise"
_MACHINE_SPRITE_B64 = "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"
_MACHINE_SPRITE_COLS = 5
_MACHINE_TILE_W = 80
_MACHINE_TILE_H = 55

BS_PLANT = {
    "Excavadora hidráulica": {
        "en":"Tracked excavator","phase":"Movimiento de tierras","table":"C.2","ref":"19","page":"47 BS / 53 PDF",
        "power":"125 kW","size":"25 t","activity":"Excavación / movimiento de tierras","laeq10":77.0,
        "bands":[95,84,79,73,70,68,64,57],"sprite":0,
    },
    "Retroexcavadora": {
        "en":"Wheeled backhoe loader","phase":"Movimiento de tierras","table":"C.2","ref":"8","page":"46 BS / 52 PDF",
        "power":"62 kW","size":"8 t","activity":"Preparación de terreno","laeq10":68.0,
        "bands":[74,66,64,64,63,60,59,50],"sprite":1,
    },
    "Cargador frontal": {
        "en":"Wheeled loader","phase":"Movimiento de tierras","table":"C.2","ref":"27","page":"47 BS / 53 PDF",
        "power":"193 kW","size":"—","activity":"Carga de camiones","laeq10":80.0,
        "bands":[85,83,76,75,75,72,72,61],"sprite":2,
    },
    "Camión tolva articulado": {
        "en":"Articulated dump truck","phase":"Movimiento de tierras","table":"C.2","ref":"32","page":"47 BS / 53 PDF",
        "power":"187 kW","size":"23 t","activity":"Descarga de material de relleno","laeq10":74.0,
        "bands":[80,76,73,70,69,66,63,58],"sprite":3,
    },
    "Rodillo vibratorio": {
        "en":"Vibratory roller","phase":"Movimiento de tierras","table":"C.2","ref":"39","page":"47 BS / 53 PDF",
        "power":"29 kW","size":"4 t","activity":"Compactación / pasada","laeq10":74.0,
        "metric":"LAmax","driveby":True,"bands":[88,83,69,68,67,65,62,59],"sprite":4,
    },
    "Camión mixer": {
        "en":"Concrete mixer truck","phase":"Estructura y hormigón","table":"C.4","ref":"20","page":"50 BS / 56 PDF",
        "power":"—","size":"—","activity":"Mezcla / operación de camión mixer","laeq10":80.0,
        "bands":[83,74,66,69,70,78,60,55],"sprite":5,
    },
    "Bomba de hormigón": {
        "en":"Truck mounted concrete pump + boom arm","phase":"Estructura y hormigón","table":"C.4","ref":"29","page":"51 BS / 57 PDF",
        "power":"—","size":"26 t","activity":"Bombeo de hormigón","laeq10":80.0,
        "bands":[83,77,75,75,74,75,67,63],"sprite":6,
    },
    "Grúa torre": {
        "en":"Tower crane","phase":"Estructura y hormigón","table":"C.4","ref":"48","page":"52 BS / 58 PDF",
        "power":"88 kW","size":"22 t","activity":"Izaje","laeq10":76.0,
        "bands":[82,77,80,76,66,66,56,50],"sprite":7,
    },
    "Manipulador telescópico": {
        "en":"Telescopic handler","phase":"Estructura y hormigón","table":"C.4","ref":"54","page":"52 BS / 58 PDF",
        "power":"76 kW","size":"4 t","activity":"Manipulación / izaje de materiales","laeq10":79.0,
        "bands":[79,73,66,65,78,66,54,47],"sprite":8,
    },
    "Martillo hidráulico": {
        "en":"Breaker mounted on wheeled backhoe","phase":"Demolición y faenas ruidosas","table":"C.1","ref":"1","page":"45 BS / 51 PDF",
        "power":"59 kW","size":"7,4 t + rompedor 380 kg","activity":"Rotura de hormigón","laeq10":92.0,
        "bands":[79,82,81,82,86,86,86,85],"sprite":9,
    },
    "Martillo neumático": {
        "en":"Hand-held pneumatic breaker","phase":"Demolición y faenas ruidosas","table":"C.1","ref":"6","page":"45 BS / 51 PDF",
        "power":"—","size":"Manual","activity":"Rotura de hormigón","laeq10":83.0,
        "bands":[83,83,81,74,73,76,78,77],"sprite":10,
    },
    "Sierra de corte de hormigón": {
        "en":"Petrol hand-held circular saw","phase":"Demolición y faenas ruidosas","table":"C.4","ref":"70","page":"53 BS / 59 PDF",
        "power":"3 kW","size":"9 kg · disco 300 mm","activity":"Corte de losa de hormigón","laeq10":91.0,
        "bands":[72,89,81,80,80,82,86,85],"sprite":11,
    },
    "Generador diésel": {
        "en":"Diesel generator","phase":"Equipos auxiliares","table":"C.4","ref":"76","page":"53 BS / 59 PDF",
        "power":"6,5 kW","size":"—","activity":"Alimentación de instalaciones de faena","laeq10":61.0,
        "bands":[80,74,57,54,53,48,45,37],"sprite":12,
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

def _machine_sprite_crop(index, large=False):
    import base64
    import io
    from PIL import Image
    raw = base64.b64decode(_MACHINE_SPRITE_B64)
    sheet = Image.open(io.BytesIO(raw)).convert("RGB")
    col = index % _MACHINE_SPRITE_COLS
    row = index // _MACHINE_SPRITE_COLS
    box = (
        col * _MACHINE_TILE_W,
        row * _MACHINE_TILE_H,
        (col + 1) * _MACHINE_TILE_W,
        (row + 1) * _MACHINE_TILE_H,
    )
    image = sheet.crop(box)
    if large:
        image = image.resize((480,330), Image.Resampling.LANCZOS)
    else:
        image = image.resize((240,165), Image.Resampling.LANCZOS)
    return image

def _stage1(lab, saved):
    _header(
        1,
        "Maquinaria de construcción y datos acústicos de referencia",
        "Reconocer las máquinas más habituales de una obra y aprender a leer sus datos acústicos desde BS 5228-1:2009.",
    )

    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:18px;padding:18px 20px;
        background:linear-gradient(135deg,#f7fbff,#eef7ff);margin-bottom:1rem">
          <div style="font-size:.75rem;font-weight:850;letter-spacing:.08em;color:#0b6ea8">IDEA CENTRAL</div>
          <div style="font-size:1.2rem;font-weight:850;color:#10243b;margin:.35rem 0 .5rem">
            Primero reconoce la máquina; después interpreta el dato acústico.
          </div>
          <div style="color:#4b6074;line-height:1.55">
            BS 5228 no asigna un único número a “una excavadora” o “un camión”.
            Cada registro corresponde a un equipo, tamaño y actividad concretos.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top1, top2 = st.columns([1.7,1])
    with top1:
        st.markdown("### Biblioteca visual de maquinaria")
        st.caption("Equipos frecuentes en obras de edificación. Selecciona uno para abrir su ficha acústica.")
    with top2:
        st.link_button("📘 Ficha oficial BS 5228-1", BSI_REFERENCE_URL, use_container_width=True)
        st.caption("En cada ficha se indica la tabla, referencia y página del PDF del curso.")

    phases=["Todas","Movimiento de tierras","Estructura y hormigón","Demolición y faenas ruidosas","Equipos auxiliares"]
    phase=st.segmented_control("Filtrar por fase",phases,default="Todas",key="c4l1_s1_phase")
    names=[n for n,v in BS_PLANT.items() if phase=="Todas" or v["phase"]==phase]

    cols=st.columns(4)
    for i,name in enumerate(names):
        item=BS_PLANT[name]
        with cols[i%4]:
            with st.container(border=True):
                st.image(_machine_sprite_crop(item["sprite"]),use_container_width=True)
                st.markdown(f"**{name}**")
                st.caption(f"{item['en']} · {item['phase']}")
                if st.button("Ver ficha",key=f"c4l1_machine_{item['sprite']}",use_container_width=True):
                    st.session_state["c4l1_selected_machine"]=name

    selected=st.session_state.get("c4l1_selected_machine", names[0] if names else list(BS_PLANT)[0])
    if selected not in BS_PLANT:
        selected=list(BS_PLANT)[0]
    item=BS_PLANT[selected]

    st.markdown("---")
    left,right=st.columns([1.05,1.35],gap="large")
    with left:
        st.image(_machine_sprite_crop(item["sprite"],large=True),use_container_width=True)
        st.markdown(f"## {selected}")
        st.caption(item["en"])
        st.markdown(f"**Fase típica:** {item['phase']}")
        st.markdown(f"**Actividad del registro:** {item['activity']}")
        st.markdown(f"**Potencia:** {item['power']}  ·  **Tamaño/capacidad:** {item['size']}")
        st.info(
            "La imagen es una referencia visual didáctica. El dato acústico corresponde al registro BS 5228 indicado, "
            "no necesariamente al modelo exacto representado en la imagen."
        )

    with right:
        st.markdown("### Datos de referencia · BS 5228-1:2009")
        metric=item.get("metric","LAeq,T")
        a,b,c1=st.columns(3)
        a.metric(f"{metric} a 10 m",f"{item['laeq10']:.0f} dB(A)")
        b.metric("LWA equivalente*",f"{item['laeq10']+28:.0f} dB(A)")
        c1.metric("Fuente",f"Tabla {item['table']} · Ref. {item['ref']}")
        if item.get("driveby"):
            st.warning(
                "Este registro está marcado con asterisco en BS 5228: corresponde a LAmax de pasada de maquinaria móvil, "
                "no a un LAeq,T de actividad estacionaria."
            )
        st.caption(
            "* En las Tablas C.1–C.11, BS 5228 indica que, salvo excepciones, el LWA utilizado en ciertos procedimientos "
            "puede obtenerse sumando 28 dB(A) al dato broadband a 10 m."
        )

        st.markdown("#### Espectro por bandas de octava a 10 m")
        bands=[63,125,250,500,1000,2000,4000,8000]
        df=pd.DataFrame({
            "Frecuencia [Hz]":[str(x) if x<1000 else f"{int(x/1000)}k" for x in bands],
            "Nivel [dB]":item["bands"],
        })
        st.dataframe(df.T,use_container_width=True,hide_index=True)

        st.markdown("#### Dónde encontrar el dato en el documento")
        st.markdown(
            f"**Anexo C · Tabla {item['table']} · referencia {item['ref']} · {item['page']}**"
        )
        st.code(f"Buscar en el PDF: Table {item['table']}  Ref {item['ref']}  {item['en']}",language=None)

    st.markdown("### Cómo leer correctamente estos valores")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown("**1 · Equipo**\n\nNo basta el nombre genérico.")
    with c2:
        st.markdown("**2 · Actividad**\n\nExcavar, romper, cargar o circular cambian el ruido.")
    with c3:
        st.markdown("**3 · Tamaño**\n\nPotencia, masa y capacidad ayudan a elegir un registro comparable.")
    with c4:
        st.markdown("**4 · Magnitud**\n\nDistingue LAeq,T, LAmax, bandas y LWA.")

    st.warning(
        "Los registros del Anexo C son mediciones de equipos específicos. La propia norma advierte que los valores pueden "
        "ser mayores o menores según marca, mantenimiento, operación y procedimiento de trabajo."
    )

    st.markdown("### Actividad de lectura crítica")
    scenario=st.selectbox(
        "Situación de obra",
        [
            "Excavación de terreno con excavadora de aproximadamente 25 t",
            "Hormigonado de estructura con camión mixer y bomba",
            "Demolición localizada de hormigón con martillo hidráulico",
            "Compactación de terreno con rodillo vibratorio",
        ],
        key="c4l1_s1_scenario",
    )
    expected={
        "Excavación de terreno con excavadora de aproximadamente 25 t":"Excavadora hidráulica",
        "Hormigonado de estructura con camión mixer y bomba":"Camión mixer",
        "Demolición localizada de hormigón con martillo hidráulico":"Martillo hidráulico",
        "Compactación de terreno con rodillo vibratorio":"Rodillo vibratorio",
    }[scenario]
    answer=st.selectbox(
        "¿Qué criterio usarías para seleccionar el dato acústico?",
        [
            "Tomaría cualquier valor de una máquina con nombre parecido.",
            "Escogería siempre el valor más alto de la tabla.",
            "Buscaría equipo, tamaño y actividad comparables y documentaría la referencia.",
        ],
        key="c4l1_s1_answer",
    )
    if st.button("Comprobar criterio",key="c4l1_s1_check",type="primary",use_container_width=True):
        if answer.startswith("Buscaría"):
            st.success(f"Correcto. Para este ejercicio, comienza revisando **{expected}** y su registro BS 5228.")
        else:
            st.warning("El dato debe ser representativo y trazable; el nombre genérico o el valor máximo por sí solos no bastan.")

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
