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
STAGE_MINUTES = [10,20,20,20,20,20,20,25,60,25,30]

BS5228_PDF_FILENAME = "BS-5228 Code of Practice for Noise and Vibration Control on Open Sites - Part 1 - Noise (2009)+A1-2014.pdf"
BS_PLANT = {
    "Excavadora hidráulica": {
        "en":"Tracked excavator","phase":"Movimiento de tierras","table":"C.2","ref":"19","page":"47 BS / 53 PDF",
        "power":"125 kW","size":"25 t","activity":"Excavación / movimiento de tierras","laeq10":77.0,
        "bands":[95,84,79,73,70,68,64,57],"image":"excavadora_hidraulica.webp",
    },
    "Retroexcavadora": {
        "en":"Wheeled backhoe loader","phase":"Movimiento de tierras","table":"C.2","ref":"8","page":"46 BS / 52 PDF",
        "power":"62 kW","size":"8 t","activity":"Preparación de terreno","laeq10":68.0,
        "bands":[74,66,64,64,63,60,59,50],"image":"retroexcavadora.webp",
    },
    "Cargador frontal": {
        "en":"Wheeled loader","phase":"Movimiento de tierras","table":"C.2","ref":"27","page":"47 BS / 53 PDF",
        "power":"193 kW","size":"—","activity":"Carga de camiones","laeq10":80.0,
        "bands":[85,83,76,75,75,72,72,61],"image":"cargador_frontal.webp",
    },
    "Camión tolva articulado": {
        "en":"Articulated dump truck","phase":"Movimiento de tierras","table":"C.2","ref":"32","page":"47 BS / 53 PDF",
        "power":"187 kW","size":"23 t","activity":"Descarga de material de relleno","laeq10":74.0,
        "bands":[80,76,73,70,69,66,63,58],"image":"camion_tolva_articulado.webp",
    },
    "Rodillo vibratorio": {
        "en":"Vibratory roller","phase":"Movimiento de tierras","table":"C.2","ref":"39","page":"47 BS / 53 PDF",
        "power":"29 kW","size":"4 t","activity":"Compactación / pasada","laeq10":74.0,
        "metric":"LAmax","driveby":True,"bands":[88,83,69,68,67,65,62,59],"image":"rodillo_vibratorio.webp",
    },
    "Camión mixer": {
        "en":"Concrete mixer truck","phase":"Estructura y hormigón","table":"C.4","ref":"20","page":"50 BS / 56 PDF",
        "power":"—","size":"—","activity":"Mezcla / operación de camión mixer","laeq10":80.0,
        "bands":[83,74,66,69,70,78,60,55],"image":"camion_mixer.webp",
    },
    "Bomba de hormigón": {
        "en":"Truck mounted concrete pump + boom arm","phase":"Estructura y hormigón","table":"C.4","ref":"29","page":"51 BS / 57 PDF",
        "power":"—","size":"26 t","activity":"Bombeo de hormigón","laeq10":80.0,
        "bands":[83,77,75,75,74,75,67,63],"image":"bomba_hormigon.webp",
    },
    "Grúa torre": {
        "en":"Tower crane","phase":"Estructura y hormigón","table":"C.4","ref":"48","page":"52 BS / 58 PDF",
        "power":"88 kW","size":"22 t","activity":"Izaje","laeq10":76.0,
        "bands":[82,77,80,76,66,66,56,50],"image":"grua_torre.webp",
    },
    "Vibrador de inmersión": {
        "en":"Poker vibrator","phase":"Estructura y hormigón","table":"C.4","ref":"33","page":"51 BS / 57 PDF",
        "power":"—","size":"—","activity":"Vibrado de hormigón","laeq10":78.0,
        "bands":[82,80,80,73,69,72,70,65],"image":"vibrador_inmersion.webp",
    },
    "Bomba + mixer a 5° piso": {
        "en":"Concrete pump + cement mixer truck","phase":"Estructura y hormigón","table":"C.4","ref":"25","page":"51 BS / 57 PDF",
        "power":"171 kW","size":"6 t / 350 bar / 150 mm","activity":"Bombeo de hormigón al 5° piso","laeq10":82.0,
        "bands":[83,81,78,79,77,74,71,66],"image":"bomba_hormigon.webp",
    },
    "Manipulador telescópico": {
        "en":"Telescopic handler","phase":"Estructura y hormigón","table":"C.4","ref":"54","page":"52 BS / 58 PDF",
        "power":"76 kW","size":"4 t","activity":"Manipulación / izaje de materiales","laeq10":79.0,
        "bands":[79,73,66,65,78,66,54,47],"image":"manipulador_telescopico.webp",
    },
    "Martillo hidráulico": {
        "en":"Breaker mounted on wheeled backhoe","phase":"Demolición y faenas ruidosas","table":"C.1","ref":"1","page":"45 BS / 51 PDF",
        "power":"59 kW","size":"7,4 t + rompedor 380 kg","activity":"Rotura de hormigón","laeq10":92.0,
        "bands":[79,82,81,82,86,86,86,85],"image":"martillo_hidraulico.webp",
    },
    "Martillo neumático": {
        "en":"Hand-held pneumatic breaker","phase":"Demolición y faenas ruidosas","table":"C.1","ref":"6","page":"45 BS / 51 PDF",
        "power":"—","size":"Manual","activity":"Rotura de hormigón","laeq10":83.0,
        "bands":[83,83,81,74,73,76,78,77],"image":"martillo_neumatico.webp",
    },
    "Sierra de corte de hormigón": {
        "en":"Petrol hand-held circular saw","phase":"Demolición y faenas ruidosas","table":"C.4","ref":"70","page":"53 BS / 59 PDF",
        "power":"3 kW","size":"9 kg · disco 300 mm","activity":"Corte de losa de hormigón","laeq10":91.0,
        "bands":[72,89,81,80,80,82,86,85],"image":"sierra_corte_hormigon.webp",
    },
    "Generador diésel": {
        "en":"Diesel generator","phase":"Equipos auxiliares","table":"C.4","ref":"76","page":"53 BS / 59 PDF",
        "power":"6,5 kW","size":"—","activity":"Alimentación de instalaciones de faena","laeq10":61.0,
        "bands":[80,74,57,54,53,48,45,37],"image":"generador_diesel.webp",
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
    metric = item.get("metric", "LAeq,T")
    c1, c2 = st.columns([0.35, 0.65])
    c1.metric(f"{metric} a 10 m", f"{item['laeq10']:.0f} dB(A)")
    with c2:
        st.markdown(f"**Actividad:** {item['activity']}")
        st.caption(
            f"BS 5228-1:2009 · Tabla {item['table']} · Ref. {item['ref']} · "
            f"{item['power']} · {item['size']}"
        )
    if item.get("driveby"):
        st.warning("Registro móvil: el valor corresponde a LAmax de pasada a 10 m.")
    else:
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
        "Analiza alternativas de control técnicamente aplicables a fuentes y trayectorias.",
        "Introduce ciclos de operación y simultaneidad sin confundir nivel operativo con equivalente.",
        "Modela excavación, obra gruesa en piso y obra gruesa en altura; compara niveles en receptores.",
        "Comprueba conceptos clave mediante un cuestionario formativo.",
        "Resuelve un caso abierto: busca referencias BS, define la estrategia de modelación y evalúa cumplimiento.",
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

def _machine_image_path(item):
    image_name = item.get("image")
    if not image_name:
        return None
    path = PROJECT_ROOT / "assets" / "curso4_lab1" / image_name
    return path if path.exists() else None

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
        bs_pdf_path = PROJECT_ROOT / "assets" / "curso4_lab1" / BS5228_PDF_FILENAME
        if bs_pdf_path.exists():
            st.download_button(
                "📘 Abrir / descargar norma BS 5228-1:2009 · PDF",
                data=bs_pdf_path.read_bytes(),
                file_name=BS5228_PDF_FILENAME,
                mime="application/pdf",
                use_container_width=True,
                key="c4l1_bs5228_pdf",
            )
        else:
            st.info(
                "La norma BS 5228-1:2009 debe estar disponible en los materiales locales del curso. "
                "No se utiliza ningún enlace externo de terceros."
            )
        st.caption(
            "Documento base del curso. En cada ficha se indica la tabla, referencia y página "
            "para localizar el registro en la norma."
        )

    phases=["Todas","Movimiento de tierras","Estructura y hormigón","Demolición y faenas ruidosas","Equipos auxiliares"]
    phase=st.segmented_control("Filtrar por fase",phases,default="Todas",key="c4l1_s1_phase")
    names=[n for n,v in BS_PLANT.items() if phase=="Todas" or v["phase"]==phase]

    cols=st.columns(4)
    for i,name in enumerate(names):
        item=BS_PLANT[name]
        with cols[i%4]:
            with st.container(border=True):
                machine_image = _machine_image_path(item)
                if machine_image:
                    st.image(str(machine_image), use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:150px;border:1px dashed #c8d7e5;border-radius:12px;"
                        "display:flex;align-items:center;justify-content:center;background:#f7fafc;"
                        "color:#7b8da0;font-size:.82rem'>Imagen en preparación</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(f"**{name}**")
                st.caption(f"{item['en']} · {item['phase']}")
                if st.button("Ver ficha",key=f"c4l1_machine_{item['image']}",use_container_width=True):
                    st.session_state["c4l1_selected_machine"]=name

    selected=st.session_state.get("c4l1_selected_machine", names[0] if names else list(BS_PLANT)[0])
    if selected not in BS_PLANT:
        selected=list(BS_PLANT)[0]
    item=BS_PLANT[selected]

    st.markdown("---")
    left,right=st.columns([1.05,1.35],gap="large")
    with left:
        machine_image = _machine_image_path(item)
        if machine_image:
            st.image(str(machine_image), use_container_width=True)
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
        band_labels=[str(x) if x<1000 else f"{int(x/1000)}k" for x in bands]
        descriptor = "Lmax por banda [dB]" if item.get("driveby") else "Lp,eq,T por banda [dB]"
        df=pd.DataFrame(
            [band_labels, item["bands"]],
            index=["Frecuencia central [Hz]", descriptor],
            columns=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"],
        )
        st.dataframe(df,use_container_width=True)
        if item.get("driveby"):
            st.caption(
                "Descriptor espectral: niveles máximos de presión sonora Lmax por banda de octava, "
                "medidos a 10 m durante la pasada. El valor global de la ficha corresponde a LAmax."
            )
        else:
            st.caption(
                "Descriptor espectral: niveles equivalentes de presión sonora Lp,eq,T por banda de octava "
                "a 10 m durante la actividad. El valor global A-ponderado de la ficha corresponde a LAeq,T."
            )

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

    st.markdown("---")
    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:20px;padding:20px 22px;
        background:linear-gradient(135deg,#fbfdff 0%,#f2f8fc 55%,#eef6ff 100%);
        box-shadow:0 6px 18px rgba(30,70,110,.06);margin:8px 0 18px 0">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.12em;color:#0b6ea8">
            DESAFÍO APLICADO · CIERRE DE ETAPA 1
          </div>
          <div style="font-size:1.35rem;font-weight:900;color:#10243b;margin:.35rem 0 .45rem">
            Interpreta la situación de obra y selecciona el registro
          </div>
          <div style="color:#4b6074;line-height:1.55">
            El escenario no te dirá directamente la etapa ni la máquina.
            Primero identifica dónde ocurre la actividad, luego elige la maquinaria
            y finalmente verifica el registro acústico BS 5228.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    scenarios = {
        "Caso A": {
            "title":"Situación de obra A",
            "text":(
                "En un proyecto de edificación se debe retirar material desde una zona previamente despejada, "
                "conformar una excavación y depositar el material extraído sobre vehículos para su retiro. "
                "La faena se realiza a nivel de terreno y requiere un equipo capaz de excavar, girar y descargar."
            ),
            "phase":"Movimiento de tierras",
            "activity":"Excavación / movimiento de tierras",
            "target":"Excavadora hidráulica",
            "options":["Excavadora hidráulica","Retroexcavadora","Cargador frontal","Camión tolva articulado"],
        },
        "Caso B": {
            "title":"Situación de obra B",
            "text":(
                "Durante una jornada se debe mantener una mezcla fresca en movimiento mientras es trasladada dentro "
                "del proyecto hasta el punto de descarga. El vehículo permanece algunos minutos en espera, realiza "
                "maniobras en el recinto y descarga el material antes de abandonar la obra."
            ),
            "phase":"Estructura y hormigón",
            "activity":"Mezcla / suministro de hormigón",
            "target":"Camión mixer",
            "options":["Camión mixer","Bomba de hormigón","Manipulador telescópico","Generador diésel"],
        },
        "Caso C": {
            "title":"Situación de obra C",
            "text":(
                "En una remodelación se deben retirar parcialmente elementos resistentes de hormigón. "
                "El trabajo se ejecuta desde el exterior mediante un implemento acoplado a una máquina portadora, "
                "produciendo impactos repetitivos de alta energía sobre el elemento a remover."
            ),
            "phase":"Demolición y faenas ruidosas",
            "activity":"Rotura de hormigón",
            "target":"Martillo hidráulico",
            "options":["Martillo hidráulico","Martillo neumático","Sierra de corte de hormigón","Excavadora hidráulica"],
        },
        "Caso D": {
            "title":"Situación de obra D",
            "text":(
                "Luego de extender material granular en capas, se debe alcanzar una densificación uniforme antes "
                "de continuar con la siguiente actividad. Un equipo recorre repetidamente la misma superficie y "
                "transmite energía mecánica al terreno durante cada pasada."
            ),
            "phase":"Movimiento de tierras",
            "activity":"Compactación / pasada",
            "target":"Rodillo vibratorio",
            "options":["Rodillo vibratorio","Cargador frontal","Camión tolva articulado","Retroexcavadora"],
        },
    }

    scenario_key = st.segmented_control(
        "Selecciona un caso",
        list(scenarios.keys()),
        default="Caso A",
        key="c4l1_s1_challenge_scenario",
    )
    sc = scenarios[scenario_key]

    with st.container(border=True):
        st.markdown(f"### 🏗️ {sc['title']}")
        st.markdown(sc["text"])
        st.caption(
            "No busques una palabra clave: interpreta la secuencia de trabajo, la función del equipo "
            "y la forma en que opera dentro de la obra."
        )

    st.markdown("#### 1 · ¿En qué etapa de la obra ubicarías principalmente esta actividad?")
    phase_options=[
        "Movimiento de tierras",
        "Estructura y hormigón",
        "Demolición y faenas ruidosas",
        "Equipos auxiliares",
    ]
    phase_answer=st.radio(
        "Selecciona la etapa más representativa",
        phase_options,
        horizontal=True,
        key=f"c4l1_s1_phase_answer_{scenario_key}",
    )

    st.markdown("#### 2 · ¿Qué maquinaria representa mejor la situación?")
    st.caption(
        "Ahora selecciona el equipo cuya función y forma de operación sean más coherentes con el escenario."
    )
    option_cols = st.columns(4)
    pick_key=f"c4l1_s1_machine_pick_{scenario_key}"
    for i,opt_name in enumerate(sc["options"]):
        opt_item = BS_PLANT[opt_name]
        with option_cols[i]:
            with st.container(border=True):
                opt_image = _machine_image_path(opt_item)
                if opt_image:
                    st.image(str(opt_image), use_container_width=True)
                st.markdown(f"**{opt_name}**")
                st.caption(f"{opt_item['power']} · {opt_item['size']}")
                if st.button(
                    "Seleccionar",
                    key=f"c4l1_s1_pick_{scenario_key}_{i}",
                    use_container_width=True,
                    type="primary" if st.session_state.get(pick_key)==opt_name else "secondary",
                ):
                    st.session_state[pick_key] = opt_name

    picked = st.session_state.get(pick_key)
    if picked:
        picked_item = BS_PLANT[picked]
        st.markdown("#### 3 · Revisa el registro acústico elegido")
        with st.container(border=True):
            q1,q2,q3,q4 = st.columns(4)
            q1.metric("Equipo", picked)
            q2.metric("Descriptor global", picked_item.get("metric","LAeq,T"))
            q3.metric("Nivel a 10 m", f"{picked_item['laeq10']:.0f} dB(A)")
            q4.metric("Referencia", f"{picked_item['table']} · Ref. {picked_item['ref']}")
            st.caption(
                f"Actividad del registro: {picked_item['activity']} · "
                f"Potencia/tamaño: {picked_item['power']} · {picked_item['size']}"
            )

        descriptor_options = (
            ["LAmax global + Lmax por bandas", "LAeq,T global + Lp,eq,T por bandas"]
            if picked_item.get("driveby")
            else ["LAeq,T global + Lp,eq,T por bandas", "LAmax global + Lmax por bandas"]
        )
        descriptor_answer = st.radio(
            "¿Qué descriptor corresponde a este registro?",
            descriptor_options,
            horizontal=True,
            key=f"c4l1_s1_descriptor_{scenario_key}_{picked}",
        )

        st.markdown("#### 4 · Justifica tu decisión")
        justification = st.text_area(
            "Explica por qué ubicaste la actividad en esa etapa y por qué el registro seleccionado es representativo.",
            placeholder=(
                "Relaciona la situación de obra con la etapa, la función de la maquinaria, "
                "su forma de operación y el descriptor acústico del registro."
            ),
            height=120,
            key=f"c4l1_s1_justification_{scenario_key}",
        )

        if st.button(
            "Validar análisis",
            key=f"c4l1_s1_validate_{scenario_key}",
            type="primary",
            use_container_width=True,
        ):
            phase_ok = phase_answer == sc["phase"]
            machine_ok = picked == sc["target"]
            expected_descriptor = (
                "LAmax global + Lmax por bandas"
                if BS_PLANT[sc["target"]].get("driveby")
                else "LAeq,T global + Lp,eq,T por bandas"
            )
            descriptor_ok = descriptor_answer == expected_descriptor
            justification_ok = len(justification.strip()) >= 90

            if phase_ok and machine_ok and descriptor_ok and justification_ok:
                st.success(
                    "Análisis correcto. Identificaste la etapa de obra, seleccionaste una maquinaria coherente con "
                    "la función descrita y verificaste correctamente el descriptor del registro BS 5228. "
                    "La justificación entrega trazabilidad suficiente para sustentar la elección."
                )
            elif not phase_ok:
                st.warning(
                    f"Revisa primero la etapa de obra. Para este caso, la clasificación más representativa es "
                    f"**{sc['phase']}**. Fíjate en qué parte de la secuencia constructiva ocurre la actividad."
                )
            elif not machine_ok:
                st.warning(
                    f"La etapa está bien identificada, pero revisa la función del equipo. "
                    f"Para este escenario, el registro de partida más coherente es **{sc['target']}**."
                )
            elif not descriptor_ok:
                st.warning(
                    f"Etapa y maquinaria correctas. Falta interpretar bien el descriptor: "
                    f"para este registro corresponde **{expected_descriptor}**."
                )
            else:
                st.info(
                    "La selección técnica es correcta. Amplía la justificación relacionando explícitamente "
                    "la etapa de obra, la función del equipo, la forma de operación y el descriptor acústico."
                )

        st.caption(
            "Criterio profesional: la selección de un registro BS 5228 debe surgir de la actividad real, "
            "la maquinaria que la ejecuta y sus condiciones de operación; no de una palabra contenida en el enunciado."
        )


    if st.session_state.get("role") == "Docente":
        with st.expander("👩‍🏫 Pauta docente · soluciones del desafío aplicado", expanded=False):
            st.markdown(
                "Use esta pauta después de que el curso haya discutido los casos. "
                "La respuesta esperada combina **etapa de obra + maquinaria + descriptor + trazabilidad BS 5228**."
            )

            teacher_rows = []
            for case_name, case_data in scenarios.items():
                target_item = BS_PLANT[case_data["target"]]
                expected_descriptor = (
                    "LAmax global + Lmax por bandas"
                    if target_item.get("driveby")
                    else "LAeq,T global + Lp,eq,T por bandas"
                )
                teacher_rows.append({
                    "Caso": case_name,
                    "Etapa correcta": case_data["phase"],
                    "Maquinaria": case_data["target"],
                    "Descriptor": expected_descriptor,
                    "BS 5228": f"Tabla {target_item['table']} · Ref. {target_item['ref']}",
                })

            st.dataframe(
                pd.DataFrame(teacher_rows),
                hide_index=True,
                use_container_width=True,
            )

            teacher_notes = {
                "Caso A": (
                    "La secuencia describe excavación, giro y descarga de material sobre vehículos. "
                    "La etapa principal es **Movimiento de tierras** y el equipo más representativo es la "
                    "**Excavadora hidráulica**. Registro de referencia: BS 5228, Tabla C.2, Ref. 19; "
                    "125 kW, 25 t, LAeq,T = 77 dB(A) a 10 m."
                ),
                "Caso B": (
                    "La mezcla se mantiene en movimiento durante el traslado y luego se descarga dentro de la obra. "
                    "Corresponde principalmente a **Estructura y hormigón** y la maquinaria es el **Camión mixer**. "
                    "Registro de referencia: BS 5228, Tabla C.4, Ref. 20; LAeq,T = 80 dB(A) a 10 m."
                ),
                "Caso C": (
                    "La clave es un implemento acoplado a una máquina portadora que produce impactos repetitivos "
                    "para retirar hormigón. La etapa es **Demolición y faenas ruidosas** y el equipo es el "
                    "**Martillo hidráulico**. Registro de referencia: BS 5228, Tabla C.1, Ref. 1; "
                    "LAeq,T = 92 dB(A) a 10 m."
                ),
                "Caso D": (
                    "La actividad consiste en densificar capas mediante pasadas repetidas que transmiten energía "
                    "mecánica al terreno. Se clasifica en **Movimiento de tierras** y corresponde al "
                    "**Rodillo vibratorio**. Registro de referencia: BS 5228, Tabla C.2, Ref. 39. "
                    "Este registro está marcado como pasada móvil: LAmax = 74 dB(A) a 10 m y Lmax por bandas."
                ),
            }

            for case_name in scenarios:
                with st.container(border=True):
                    st.markdown(f"#### {case_name} · solución comentada")
                    st.markdown(teacher_notes[case_name])

            st.info(
                "Criterio de corrección sugerido: no exigir que la justificación reproduzca estas frases literalmente. "
                "Considere correcta una respuesta que identifique coherentemente la etapa, la función del equipo, "
                "la maquinaria seleccionada y el descriptor acústico correspondiente."
            )

def _stage2(lab, saved):
    _header(
        2,
        "Del registro BS 5228 a una fuente para modelar",
        "Transformar el dato acústico de referencia de la Etapa 1 en una entrada de modelación trazable, sin volver a desarrollar Lp y Lw desde cero.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:22px;padding:22px 24px;
        background:linear-gradient(135deg,#fbfdff 0%,#f3f8fd 52%,#edf6ff 100%);
        box-shadow:0 8px 22px rgba(30,70,110,.07);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.12em;color:#0b6ea8">
            IDEA CENTRAL
          </div>
          <div style="font-size:1.32rem;font-weight:900;color:#10243b;margin:.4rem 0 .45rem">
            Del dato medido a 10 m al nivel de potencia sonora de entrada
          </div>
          <div style="color:#4b6074;line-height:1.6">
            En esta etapa no se vuelve a enseñar Lp y Lw desde cero.
            El objetivo es aprender a tomar un registro BS 5228, reconocer su descriptor,
            convertirlo a un dato de entrada y mantener siempre la trazabilidad de la fuente.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Ruta de trabajo")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:.25rem 0 1.15rem">
          <div style="border:1px solid #dce7f0;border-radius:18px;padding:16px;background:#ffffff;
          box-shadow:0 3px 10px rgba(30,70,110,.04)">
            <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.08em">PASO 1</div>
            <div style="font-size:1.03rem;font-weight:850;color:#16314b;margin:.35rem 0">Registro</div>
            <div style="font-size:.88rem;color:#5a6c7e;line-height:1.45">Selecciona el equipo y revisa su actividad de referencia.</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:18px;padding:16px;background:#ffffff;
          box-shadow:0 3px 10px rgba(30,70,110,.04)">
            <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.08em">PASO 2</div>
            <div style="font-size:1.03rem;font-weight:850;color:#16314b;margin:.35rem 0">Descriptor</div>
            <div style="font-size:.88rem;color:#5a6c7e;line-height:1.45">Distingue LAeq,T de LAmax antes de modelar.</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:18px;padding:16px;background:#ffffff;
          box-shadow:0 3px 10px rgba(30,70,110,.04)">
            <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.08em">PASO 3</div>
            <div style="font-size:1.03rem;font-weight:850;color:#16314b;margin:.35rem 0">Conversión</div>
            <div style="font-size:.88rem;color:#5a6c7e;line-height:1.45">Aplica la relación de referencia indicada por BS 5228.</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:18px;padding:16px;background:#ffffff;
          box-shadow:0 3px 10px rgba(30,70,110,.04)">
            <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.08em">PASO 4</div>
            <div style="font-size:1.03rem;font-weight:850;color:#16314b;margin:.35rem 0">Modelo</div>
            <div style="font-size:.88rem;color:#5a6c7e;line-height:1.45">Define si trabajarás con broadband o por bandas.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Selecciona una maquinaria de referencia")
    st.caption("Se utiliza la misma biblioteca visual de la Etapa 1 para mantener continuidad entre reconocimiento, dato acústico y modelación.")

    machine_names = list(BS_PLANT)
    selected_name = st.selectbox(
        "Maquinaria / actividad",
        machine_names,
        key="c4l1_s2_machine",
        label_visibility="collapsed",
    )
    item = BS_PLANT[selected_name]
    name = selected_name
    metric = item.get("metric", "LAeq,T")
    lwa = item["laeq10"] + 28.0

    visual_col, data_col = st.columns([1.0,1.45], gap="large")
    with visual_col:
        with st.container(border=True):
            machine_image = _machine_image_path(item)
            if machine_image:
                st.image(str(machine_image), use_container_width=True)
            st.markdown(f"### {name}")
            st.caption(item["en"])
            st.markdown(f"**Fase típica:** {item['phase']}")
            st.markdown(f"**Actividad:** {item['activity']}")
            st.markdown(f"**Potencia:** {item['power']}  ·  **Tamaño:** {item['size']}")
    with data_col:
        st.markdown("### 1 · Identifica correctamente el dato de partida")
        a,b = st.columns(2)
        a.metric("Descriptor original", metric)
        b.metric("Nivel a 10 m", f"{item['laeq10']:.0f} dB(A)")
        c1,d = st.columns(2)
        c1.metric("Tabla", item["table"])
        d.metric("Referencia", f"Ref. {item['ref']}")
        st.caption(f"{item['page']} · Registro específico de la actividad indicada.")

        if item.get("driveby"):
            st.warning(
                "Registro móvil: el valor global corresponde a LAmax de pasada y las bandas corresponden a Lmax. "
                "No debe tratarse como si fuese un LAeq,T estacionario."
            )
        else:
            st.info(
                "Registro de actividad: el valor global corresponde a LAeq,T medido a 10 m durante la condición indicada."
            )

    st.markdown("### 2 · Conversión práctica indicada por BS 5228")
    conv_left, conv_right = st.columns([1.15,1], gap="large")
    with conv_left:
        with st.container(border=True):
            st.latex(r"L_{WA} \approx L_{A,10\,m} + 28\ \mathrm{dB}")
            st.caption(
                "Para los registros de las Tablas C.1–C.11, BS 5228 indica que, salvo excepciones, "
                "el nivel de potencia sonora A-ponderado utilizado en ciertos procedimientos de predicción "
                "puede obtenerse sumando 28 dB(A) al nivel broadband a 10 m."
            )
    with conv_right:
        st.markdown(
            f"""
            <div style="border:1px solid #cfe3d6;border-radius:18px;padding:18px 20px;
            background:linear-gradient(135deg,#f8fcf9,#f1f9f4)">
              <div style="font-size:.72rem;font-weight:900;color:#2f7a49;letter-spacing:.08em">RESULTADO</div>
              <div style="font-size:1rem;color:#385444;margin:.45rem 0">{metric} a 10 m = <b>{item['laeq10']:.0f} dB(A)</b></div>
              <div style="font-size:1rem;color:#385444">{item['laeq10']:.0f} + 28</div>
              <div style="font-size:1.55rem;font-weight:900;color:#183625;margin-top:.35rem">LWA ≈ {lwa:.0f} dB(A)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 3 · ¿Qué dato debes ingresar al modelo?")
    m1,m2,m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.markdown("#### 🔊 Broadband")
            st.markdown(f"Usa **LWA ≈ {lwa:.0f} dB(A)** cuando el ejercicio trabaje con un único valor global.")
            st.caption("Útil para comparaciones globales e introducción al modelo.")
    with m2:
        with st.container(border=True):
            st.markdown("#### 🎚️ Por bandas")
            st.markdown("Conserva el espectro de octavas cuando el cálculo necesite dependencia con la frecuencia.")
            st.caption("Clave para barreras, controles y análisis espectral.")
    with m3:
        with st.container(border=True):
            st.markdown("#### 🧾 Trazabilidad")
            st.markdown(f"Conserva **Tabla {item['table']} · Ref. {item['ref']}**, actividad, tamaño y descriptor original.")
            st.caption("El LWA nunca debe quedar separado de su fuente documental.")

    st.markdown("### 4 · Del espectro de presión al espectro de potencia")
    st.markdown(
        "BS 5228 entrega en estas tablas **niveles de presión sonora por banda de octava a 10 m**. "
        "Para utilizarlos como espectro de una fuente puntual en el modelador necesitamos expresar cada banda "
        "como nivel de potencia sonora."
    )

    spec_a,spec_b = st.columns([1.1,1], gap="large")
    with spec_a:
        with st.container(border=True):
            st.markdown("#### Conversión por banda")
            st.latex(r"L_{W,f} \approx L_{p,f}(r)+10\log_{10}(2\pi r^2)")
            st.markdown("Para **r = 10 m**:")
            st.latex(r"10\log_{10}(2\pi\cdot10^2)=27.98\approx28\ \mathrm{dB}")
            st.latex(r"\boxed{L_{W,f}\approx L_{p,f}(10\,m)+28}")
            st.caption(
                "Esta extensión por banda es una derivación geométrica para una fuente puntual radiando "
                "sobre un plano reflectante (hemiespacio). La norma explicita el +28 dB(A) para el valor "
                "broadband; aquí se aplica la misma relación geométrica a cada banda con finalidad didáctica."
            )
    with spec_b:
        with st.container(border=True):
            st.markdown("#### Qué significa")
            st.markdown(
                "El **+28 dB no cambia la forma del espectro**: todas las bandas se desplazan la misma cantidad. "
                "Lo que cambia es la magnitud: pasamos de presión sonora medida a 10 m a potencia sonora equivalente de la fuente."
            )
            st.info(
                "No se aplica ponderación A antes de esta conversión. Las bandas de la tabla se conservan como niveles "
                "por octava; la ponderación A solo se usa después si queremos recomponer un LWA global."
            )

    octave_labels=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"]
    lw_bands=[float(v)+28.0 for v in item["bands"]]
    source_band_descriptor = "Lmax a 10 m [dB]" if item.get("driveby") else "Lp,eq,T a 10 m [dB]"
    power_band_descriptor = "Lw,max equivalente [dB]" if item.get("driveby") else "Lw,eq,T equivalente [dB]"
    st.markdown("#### Matriz espectral · presión → potencia")
    st.caption("Cada columna representa una banda de octava. La fila inferior es el dato que utilizarás como potencia sonora equivalente.")

    spectral_cards = '<div style="overflow-x:auto;padding-bottom:4px"><div style="min-width:860px">'
    spectral_cards += '<div style="display:grid;grid-template-columns:180px repeat(8,1fr);gap:7px;align-items:stretch">'
    spectral_cards += (
        '<div style="border-radius:13px;padding:11px 12px;background:#16324a;color:#fff;'
        'font-size:.78rem;font-weight:850;display:flex;align-items:center">Magnitud</div>'
    )
    for label in octave_labels:
        spectral_cards += (
            f'<div style="border-radius:13px;padding:11px 6px;background:#16324a;color:#fff;'
            f'text-align:center;font-size:.78rem;font-weight:850">{label}</div>'
        )

    spectral_rows = [
        (source_band_descriptor, [float(v) for v in item["bands"]], "#f5f8fb", "#31495f", ""),
        ("+ corrección geométrica", [28.0]*8, "#fff8e9", "#8a5b12", "+"),
        (power_band_descriptor, lw_bands, "#eef8f1", "#23633b", ""),
    ]
    for row_name,row_values,row_bg,row_color,prefix in spectral_rows:
        spectral_cards += (
            f'<div style="border:1px solid #dce6ee;border-radius:13px;padding:11px 12px;'
            f'background:{row_bg};color:{row_color};font-size:.76rem;font-weight:850;'
            f'display:flex;align-items:center">{row_name}</div>'
        )
        for value in row_values:
            value_text = f"{prefix}{value:.0f}" if prefix else f"{value:.0f}"
            spectral_cards += (
                f'<div style="border:1px solid #dce6ee;border-radius:13px;padding:11px 5px;'
                f'background:{row_bg};color:{row_color};text-align:center;font-size:.92rem;'
                f'font-weight:900">{value_text}</div>'
            )
    spectral_cards += '</div></div></div>'
    st.markdown(spectral_cards, unsafe_allow_html=True)

    st.markdown("#### Ejemplo con una banda")
    example_idx=3
    example_freq=octave_labels[example_idx]
    e1,e2,e3=st.columns(3)
    e1.metric(f"{example_freq} · presión a 10 m", f"{item['bands'][example_idx]:.0f} dB")
    e2.metric("Corrección geométrica", "+28 dB")
    e3.metric(f"{example_freq} · potencia", f"{lw_bands[example_idx]:.0f} dB")
    st.markdown(
        f"Para **{name}**, en {example_freq}: "
        f"**{item['bands'][example_idx]:.0f} + 28 = {lw_bands[example_idx]:.0f} dB** de potencia sonora equivalente en esa banda."
    )

    st.markdown("### 5 · Comprobación: recomponer el LWA desde las bandas")
    a_corr=[-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0,-1.1]
    lwa_band=[lw+a for lw,a in zip(lw_bands,a_corr)]
    lwa_from_spectrum=10*math.log10(sum(10**(v/10) for v in lwa_band))
    diff=lwa_from_spectrum-lwa
    st.markdown("#### Matriz de ponderación A")
    st.caption("Primero se conserva Lw por banda, luego se aplica la corrección A y finalmente se obtiene el aporte A-ponderado de cada banda.")

    a_cards = '<div style="overflow-x:auto;padding-bottom:4px"><div style="min-width:860px">'
    a_cards += '<div style="display:grid;grid-template-columns:180px repeat(8,1fr);gap:7px;align-items:stretch">'
    a_cards += (
        '<div style="border-radius:13px;padding:11px 12px;background:#24374a;color:#fff;'
        'font-size:.78rem;font-weight:850;display:flex;align-items:center">Magnitud</div>'
    )
    for label in octave_labels:
        a_cards += (
            f'<div style="border-radius:13px;padding:11px 6px;background:#24374a;color:#fff;'
            f'text-align:center;font-size:.78rem;font-weight:850">{label}</div>'
        )

    a_rows = [
        ("Lw por banda [dB]", lw_bands, "#f5f8fb", "#31495f"),
        ("Corrección A [dB]", a_corr, "#f4f0fb", "#614a7d"),
        ("LwA por banda [dB(A)]", lwa_band, "#eef6ff", "#1d5d8d"),
    ]
    for row_name,row_values,row_bg,row_color in a_rows:
        a_cards += (
            f'<div style="border:1px solid #dce6ee;border-radius:13px;padding:11px 12px;'
            f'background:{row_bg};color:{row_color};font-size:.76rem;font-weight:850;'
            f'display:flex;align-items:center">{row_name}</div>'
        )
        for value in row_values:
            a_cards += (
                f'<div style="border:1px solid #dce6ee;border-radius:13px;padding:11px 5px;'
                f'background:{row_bg};color:{row_color};text-align:center;font-size:.92rem;'
                f'font-weight:900">{value:+.1f}</div>'
            )
    a_cards += '</div></div></div>'
    st.markdown(a_cards, unsafe_allow_html=True)

    st.markdown("#### Resultado de la comprobación")
    st.latex(r"L_{WA}=10\log_{10}\left(\sum_f10^{(L_{W,f}+A_f)/10}\right)")

    result_cards = f"""
    <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 .8rem">
      <div style="border:1px solid #dce7f0;border-radius:17px;padding:16px;background:#ffffff">
        <div style="font-size:.72rem;font-weight:850;color:#64788b">BROADBAND + 28</div>
        <div style="font-size:1.55rem;font-weight:900;color:#17324a;margin-top:.25rem">{lwa:.1f} dB(A)</div>
        <div style="font-size:.78rem;color:#708294;margin-top:.2rem">Referencia global</div>
      </div>
      <div style="border:1px solid #cfe2f1;border-radius:17px;padding:16px;background:#f5faff">
        <div style="font-size:.72rem;font-weight:850;color:#4d728f">DESDE LAS BANDAS</div>
        <div style="font-size:1.55rem;font-weight:900;color:#14537d;margin-top:.25rem">{lwa_from_spectrum:.1f} dB(A)</div>
        <div style="font-size:.78rem;color:#708294;margin-top:.2rem">Suma energética A-ponderada</div>
      </div>
      <div style="border:1px solid #d7eadc;border-radius:17px;padding:16px;background:#f5fbf6">
        <div style="font-size:.72rem;font-weight:850;color:#4b7b59">DIFERENCIA</div>
        <div style="font-size:1.55rem;font-weight:900;color:#2e6840;margin-top:.25rem">{diff:+.1f} dB</div>
        <div style="font-size:.78rem;color:#708294;margin-top:.2rem">Control de coherencia</div>
      </div>
    </div>
    """
    st.markdown(result_cards, unsafe_allow_html=True)
    st.caption(
        "Es normal obtener una pequeña diferencia porque los valores tabulados por banda están redondeados. "
        "Esta comprobación permite verificar que el espectro convertido es coherente con el valor global."
    )

    if item.get("driveby"):
        st.warning(
            "En registros de pasada móvil, las bandas originales corresponden a Lmax. La conversión mostrada produce "
            "un espectro de potencia máxima equivalente para fines didácticos; no convierte automáticamente esa pasada "
            "en una fuente estacionaria ni sustituye el tratamiento específico de fuentes móviles."
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="border:1px solid #d8e6f0;border-radius:20px;padding:20px 22px;
        background:linear-gradient(135deg,#f8fbfe,#eef6fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">
            EJERCICIO DE CONVERSIÓN
          </div>
          <div style="font-size:1.25rem;font-weight:850;color:#16314b;margin:.35rem 0">
            Completa el espectro de potencia sonora
          </div>
          <div style="color:#536b80;line-height:1.55">
            A partir de los niveles de presión sonora por banda medidos a 10 m,
            calcula primero <b>Lw por banda</b>, luego aplica la <b>corrección A</b>
            para obtener <b>LwA por banda</b> y finalmente realiza la suma energética total.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    practice_cases = {
        "Caso 1": "Excavadora hidráulica",
        "Caso 2": "Camión mixer",
        "Caso 3": "Martillo hidráulico",
        "Caso 4": "Rodillo vibratorio",
    }
    practice_case = st.segmented_control(
        "Selecciona un caso de práctica",
        list(practice_cases.keys()),
        default="Caso 1",
        key="c4l1_s2_practice_case",
    )
    practice_name = practice_cases[practice_case]
    practice_item = BS_PLANT[practice_name]
    practice_metric = practice_item.get("metric","LAeq,T")
    practice_lw = [float(v)+28.0 for v in practice_item["bands"]]
    practice_a = [-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0,-1.1]
    practice_lwa_bands = [lw+a for lw,a in zip(practice_lw,practice_a)]
    practice_total = 10*math.log10(sum(10**(v/10) for v in practice_lwa_bands))

    pc1,pc2 = st.columns([1,1.5],gap="large")
    with pc1:
        with st.container(border=True):
            practice_image = _machine_image_path(practice_item)
            if practice_image:
                st.image(str(practice_image), use_container_width=True)
            st.markdown(f"### {practice_name}")
            st.caption(practice_item["en"])
            st.markdown(f"**Actividad:** {practice_item['activity']}")
            st.markdown(f"**Descriptor original:** {practice_metric}")
            st.markdown(f"**Fuente:** Tabla {practice_item['table']} · Ref. {practice_item['ref']}")
    with pc2:
        st.markdown("#### Instrucciones")
        st.markdown(
            "1. Para cada banda, calcula **Lw = Lp(10 m) + 28 dB**.\n"
            "2. Luego calcula **LwA = Lw + corrección A**.\n"
            "3. Finalmente suma energéticamente todos los LwA por banda para obtener el **LWA total**."
        )
        st.latex(r"L_{WA}=10\log_{10}\left(\sum_f10^{L_{WA,f}/10}\right)")
        if practice_item.get("driveby"):
            st.warning(
                "Este caso corresponde a una pasada móvil: las bandas de origen son Lmax. "
                "La mecánica matemática del ejercicio es la misma, pero el descriptor debe conservarse."
            )

    st.markdown("#### Completa la tabla")
    h1,h2,h3,h4,h5 = st.columns([.75,1.05,1.05,1.0,1.05])
    h1.markdown("**Banda**")
    h2.markdown("**Lp a 10 m**")
    h3.markdown("**Lw**")
    h4.markdown("**Corr. A**")
    h5.markdown("**LwA**")

    student_lw=[]
    student_lwa=[]
    for i,label in enumerate(octave_labels):
        c1,c2,c3,c4,c5=st.columns([.75,1.05,1.05,1.0,1.05])
        c1.markdown(f"**{label}**")
        c2.markdown(f"{practice_item['bands'][i]:.0f} dB")
        lw_txt=c3.text_input(
            f"Lw {label}",
            value="",
            key=f"c4l1_s2_ex_lw_{practice_case}_{i}",
            label_visibility="collapsed",
            placeholder="dB",
        )
        c4.markdown(f"{practice_a[i]:+.1f} dB")
        lwa_txt=c5.text_input(
            f"LwA {label}",
            value="",
            key=f"c4l1_s2_ex_lwa_{practice_case}_{i}",
            label_visibility="collapsed",
            placeholder="dB(A)",
        )
        student_lw.append(lw_txt)
        student_lwa.append(lwa_txt)

    st.markdown("#### Suma energética final")
    total_answer = st.text_input(
        "LWA total [dB(A)]",
        value="",
        key=f"c4l1_s2_ex_total_{practice_case}",
        placeholder="Ingresa el resultado total, por ejemplo 105.3",
    )

    if st.button(
        "Comprobar ejercicio",
        key=f"c4l1_s2_ex_check_{practice_case}",
        type="primary",
        use_container_width=True,
    ):
        def _parse_num(value):
            try:
                return float(str(value).strip().replace(",","."))
            except Exception:
                return None

        parsed_lw=[_parse_num(v) for v in student_lw]
        parsed_lwa=[_parse_num(v) for v in student_lwa]
        parsed_total=_parse_num(total_answer)

        if any(v is None for v in parsed_lw+parsed_lwa) or parsed_total is None:
            st.warning("Completa todos los valores de Lw, LwA y el LWA total antes de comprobar.")
        else:
            lw_ok=[abs(a-b)<=0.2 for a,b in zip(parsed_lw,practice_lw)]
            lwa_ok=[abs(a-b)<=0.2 for a,b in zip(parsed_lwa,practice_lwa_bands)]
            total_ok=abs(parsed_total-practice_total)<=0.3

            correct_cells=sum(lw_ok)+sum(lwa_ok)+(1 if total_ok else 0)
            total_cells=17
            if correct_cells==total_cells:
                st.success(
                    f"Ejercicio correcto. Convertiste las 8 bandas a Lw, aplicaste la ponderación A "
                    f"y obtuviste correctamente el LWA total de **{practice_total:.1f} dB(A)**."
                )
            else:
                bad_lw=[octave_labels[i] for i,ok in enumerate(lw_ok) if not ok]
                bad_lwa=[octave_labels[i] for i,ok in enumerate(lwa_ok) if not ok]
                st.warning(f"Tienes **{correct_cells}/{total_cells}** resultados correctos.")
                if bad_lw:
                    st.write("Revisa **Lw** en: " + ", ".join(bad_lw) + ". Recuerda: Lw = Lp + 28.")
                if bad_lwa:
                    st.write("Revisa **LwA** en: " + ", ".join(bad_lwa) + ". Recuerda sumar algebraicamente la corrección A.")
                if not total_ok:
                    st.write("Revisa la **suma energética final**: no se suman los dB aritméticamente.")

    if st.session_state.get("role") == "Docente":
        with st.expander("👩‍🏫 Pauta docente · Etapa 2", expanded=False):
            st.markdown(
                f"""
                **Ejercicio activo:** {practice_case} · {practice_name}  
                **Descriptor original:** {practice_metric}  
                **Regla por banda:** Lw = Lp(10 m) + 28 dB  
                **Resultado total esperado:** **{practice_total:.1f} dB(A)**
                """
            )
            teacher_solution = '<div style="overflow-x:auto"><div style="min-width:820px">'
            teacher_solution += '<div style="display:grid;grid-template-columns:110px repeat(4,1fr);gap:7px">'
            for head in ["Banda","Lp 10 m","Lw","Corr. A","LwA"]:
                teacher_solution += (
                    f'<div style="background:#20384e;color:#fff;border-radius:11px;padding:9px;'
                    f'text-align:center;font-size:.78rem;font-weight:850">{head}</div>'
                )
            for i,label in enumerate(octave_labels):
                vals=[
                    label,
                    f"{practice_item['bands'][i]:.0f}",
                    f"{practice_lw[i]:.0f}",
                    f"{practice_a[i]:+.1f}",
                    f"{practice_lwa_bands[i]:.1f}",
                ]
                for j,val in enumerate(vals):
                    bg="#eef8f1" if j in (2,4) else "#f7f9fb"
                    col="#245f3a" if j in (2,4) else "#334c61"
                    teacher_solution += (
                        f'<div style="border:1px solid #dce6ee;border-radius:11px;padding:9px;'
                        f'background:{bg};color:{col};text-align:center;font-size:.82rem;'
                        f'font-weight:{850 if j in (2,4) else 650}">{val}</div>'
                    )
            teacher_solution += '</div></div></div>'
            st.markdown(teacher_solution, unsafe_allow_html=True)
            st.success(f"LWA total por suma energética = **{practice_total:.1f} dB(A)**")
            st.caption(
                "Tolerancia usada por la app: ±0,2 dB en cada celda de Lw y LwA, y ±0,3 dB en el resultado total."
            )
            if practice_item.get("driveby"):
                st.warning(
                    "Punto docente clave: este caso proviene de Lmax de pasada móvil. "
                    "La conversión matemática no cambia el descriptor original ni convierte el caso en estacionario."
                )
            else:
                st.info(
                    "Punto docente clave: el alumno debe distinguir entre la conversión geométrica por banda "
                    "y la ponderación A posterior, y realizar la suma final energéticamente."
                )

def _stage3(lab, saved):
    _header(
        3,
        "Propagación de maquinaria en aire libre",
        "Comprender cómo Noise Map Lab transforma el nivel de potencia sonora de una fuente en nivel de presión sonora en el receptor mediante los términos principales de propagación.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:22px;padding:22px 24px;
        background:linear-gradient(135deg,#fbfdff 0%,#f3f8fd 55%,#eef6ff 100%);
        box-shadow:0 8px 22px rgba(30,70,110,.06);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.12em;color:#0b6ea8">IDEA CENTRAL</div>
          <div style="font-size:1.3rem;font-weight:900;color:#10243b;margin:.4rem 0 .5rem">
            Del Lw de la máquina al Lp que recibe una persona
          </div>
          <div style="color:#4b6074;line-height:1.6">
            Noise Map Lab calcula la propagación término por término. En esta etapa se desarrollan
            directividad, divergencia geométrica y absorción atmosférica; suelo, barreras y meteorología
            de largo plazo se profundizan más adelante.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #cfddea;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#f7fbff,#eef5fb);box-shadow:0 8px 20px rgba(31,63,92,.06);
        margin:.25rem 0 1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">
            ECUACIÓN GENERAL DE PROPAGACIÓN
          </div>
          <div style="font-size:.88rem;color:#607386;margin-top:.25rem">
            Esquema usado por el modelador para seguir la energía desde la fuente hasta el receptor.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.latex(r"L_p = L_W + D_c - A_{div} - A_{atm} - A_{gr} - A_{bar} - C_{met}")
        st.markdown(
            "**Referencia normativa:** este esquema corresponde al enfoque de propagación exterior de "
            "**ISO 9613-2:2024 · Acoustics — Attenuation of sound during propagation outdoors — Part 2: Engineering method**. "
            "La absorción atmosférica se determina mediante la formulación de **ISO 9613-1**."
        )
        st.caption(
            "La ecuación resume los principales mecanismos considerados en la propagación exterior: "
            "potencia sonora, directividad, divergencia geométrica, absorción atmosférica, efecto de suelo, "
            "difracción por barreras y corrección meteorológica de largo plazo."
        )

    cards = [
        ("Lw","Fuente","Potencia acústica emitida por la maquinaria; no depende de la distancia al receptor."),
        ("Dc","Directividad","Corrige la emisión cuando la fuente no radia con la misma intensidad en todas las direcciones."),
        ("Adiv","Divergencia","Pérdida por expansión geométrica del frente de onda con la distancia."),
        ("Aatm","Atmósfera","Pérdida por absorción molecular del aire; depende de frecuencia, temperatura, humedad y distancia."),
        ("Agr","Suelo","Efecto de interferencia entre la onda directa y la reflejada por el terreno."),
        ("Abar","Difracción","Reducción por obstáculos que interrumpen la línea de visión y obligan al sonido a rodearlos."),
        ("Cmet","Meteorología","Ajuste de largo plazo por condiciones de propagación favorables o desfavorables."),
    ]
    html='<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:.3rem 0 1.2rem">'
    for symbol,title,desc in cards:
        html += (
            f'<div style="border:1px solid #dce7f0;border-radius:17px;padding:14px;background:#fff">'
            f'<div style="font-size:.72rem;font-weight:900;color:#0b6ea8">{symbol}</div>'
            f'<div style="font-size:1rem;font-weight:850;color:#18324a;margin:.25rem 0">{title}</div>'
            f'<div style="font-size:.82rem;color:#607386;line-height:1.4">{desc}</div></div>'
        )
    html+='</div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("### Selecciona una máquina")
    name=st.selectbox(
        "Maquinaria de referencia",
        list(BS_PLANT),
        key="c4l1_s3_machine",
        label_visibility="collapsed",
    )
    item=BS_PLANT[name]
    lwa=item["laeq10"]+28.0

    left,right=st.columns([1,1.45],gap="large")
    with left:
        with st.container(border=True):
            img=_machine_image_path(item)
            if img:
                st.image(str(img),use_container_width=True)
            st.markdown(f"### {name}")
            st.caption(item["en"])
            st.markdown(f"**Actividad:** {item['activity']}")
            st.markdown(f"**LWA de referencia:** {lwa:.1f} dB(A)")
            st.caption(f"Tabla {item['table']} · Ref. {item['ref']}")
    with right:
        st.markdown("### 1 · Directividad · Q y Dc")
        st.markdown(
            "La **directividad** indica si el sonido se reparte en todas las direcciones o si queda concentrado hacia una zona. "
            "Para una explicación simple podemos usar el **factor de directividad Q**. Cuanto mayor es Q, menor es el espacio "
            "hacia el que se reparte la misma potencia acústica y, por lo tanto, mayor es el nivel en esa dirección."
        )

        st.markdown(
            """
            <div style="border:1px solid #dbe7f0;border-radius:16px;padding:14px 16px;background:#f8fbfe;margin:.4rem 0 .8rem">
              <div style="font-size:.78rem;font-weight:900;color:#0b6ea8">EN PALABRAS SIMPLES</div>
              <div style="font-size:.9rem;color:#526b80;line-height:1.5;margin-top:.25rem">
                Imagina una ampolleta: si ilumina hacia todos lados, la energía se reparte mucho.
                Si colocas superficies que la obligan a radiar solo hacia una parte del espacio,
                la misma energía queda más concentrada. Con el sonido ocurre algo parecido.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        q_cards=[
            ("Q = 1","Espacio libre","La fuente ideal radia en todas direcciones.","Dc = 0 dB"),
            ("Q = 2","Sobre un plano","La radiación queda aproximadamente en medio espacio.","Dc ≈ +3 dB"),
            ("Q = 4","Encuentro de 2 planos","La radiación se concentra aproximadamente en un cuarto de espacio.","Dc ≈ +6 dB"),
            ("Q = 8","Esquina de 3 planos","La radiación se concentra aproximadamente en un octavo de espacio.","Dc ≈ +9 dB"),
        ]
        q_html='<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:.35rem 0 .8rem">'
        for qv,title,desc,dc_txt in q_cards:
            q_html+=(
                f'<div style="border:1px solid #dce7f0;border-radius:15px;padding:12px;background:#fff">'
                f'<div style="font-size:.78rem;font-weight:900;color:#0b6ea8">{qv}</div>'
                f'<div style="font-size:.92rem;font-weight:850;color:#18324a;margin:.2rem 0">{title}</div>'
                f'<div style="font-size:.78rem;color:#64788b;line-height:1.35">{desc}</div>'
                f'<div style="font-size:.78rem;font-weight:850;color:#2c6b45;margin-top:.35rem">{dc_txt}</div>'
                f'</div>'
            )
        q_html+='</div>'
        st.markdown(q_html,unsafe_allow_html=True)

        q=st.segmented_control(
            "Factor de directividad Q",
            [1,2,4,8],
            default=1,
            key="c4l1_s3_q",
        )
        dc=10*math.log10(float(q))
        q1,q2=st.columns(2)
        q1.metric("Q seleccionado",f"{q}")
        q2.metric("Dc equivalente",f"{dc:+.1f} dB")
        st.latex(r"D_c = 10\log_{10}(Q)")
        st.caption(
            "Los casos Q=1, 2, 4 y 8 son aproximaciones geométricas ideales para comprender la directividad. "
            "En una máquina real, la directividad depende de su geometría, aberturas, superficies cercanas y orientación; "
            "Noise Map Lab utiliza directamente Dc como corrección en dB."
        )

    st.markdown("### 2 · Divergencia geométrica · Adiv")
    st.markdown(
        "La divergencia representa la **expansión espacial de la energía sonora**. A medida que el frente de onda "
        "se aleja de una fuente puntual, la misma energía se distribuye sobre una superficie cada vez mayor. "
        "Por eso el nivel disminuye incluso si no existe absorción atmosférica, suelo ni barreras."
    )
    with st.container(border=True):
        st.latex(r"A_{div}=20\log_{10}(d)+11")
        st.caption(
            "d es la distancia tridimensional fuente–receptor en metros. El término +11 corresponde a la referencia "
            "geométrica de propagación esférica utilizada en este tipo de cálculo."
        )
    d=st.slider(
        "Distancia fuente–receptor [m]",
        5,200,40,5,
        key="c4l1_s3_distance",
    )
    a_div=20*math.log10(float(d))+11.0
    dv1,dv2,dv3=st.columns(3)
    dv1.metric("Distancia",f"{d} m")
    dv2.metric("Adiv",f"{a_div:.1f} dB")
    dv3.metric("Lw + Dc - Adiv",f"{lwa+dc-a_div:.1f} dB")

    st.markdown("#### ¿Qué ocurre al duplicar la distancia?")
    dist_set=[5,10,20,40,80]
    levels=[lwa+dc-(20*math.log10(x)+11.0) for x in dist_set]
    rows='<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:.3rem 0 1rem">'
    for dist,lev in zip(dist_set,levels):
        rows += (
            f'<div style="border:1px solid #dce7f0;border-radius:16px;padding:14px;background:#fff;text-align:center">'
            f'<div style="font-size:.74rem;color:#6d8092">{dist} m</div>'
            f'<div style="font-size:1.35rem;font-weight:900;color:#18324a;margin:.2rem 0">{lev:.1f} dB</div>'
            f'<div style="font-size:.72rem;color:#8090a0">solo divergencia</div></div>'
        )
    rows+='</div>'
    st.markdown(rows, unsafe_allow_html=True)
    st.info("En campo libre ideal, cada duplicación de distancia reduce aproximadamente 6 dB por divergencia geométrica.")

    st.markdown("### 3 · Absorción atmosférica · Aatm")
    st.markdown(
        "El aire no es un medio perfectamente transparente al sonido. Parte de la energía acústica se transforma "
        "en calor mediante procesos de relajación molecular, principalmente asociados al oxígeno y al nitrógeno. "
        "Este efecto se vuelve más importante a **frecuencias altas** y a **distancias largas**."
    )
    st.markdown(
        "El término se calcula como **Aatm = α · d**, donde α es el coeficiente de absorción atmosférica. "
        "Ese coeficiente cambia con la **frecuencia**, la **temperatura**, la **humedad relativa** y, en una formulación completa, "
        "también con la presión atmosférica."
    )

    def _alpha_iso_style_db_per_m(frequency_hz, temperature_c, humidity_pct, pressure_kpa=101.325):
        f=max(float(frequency_hz),1.0)
        t=float(temperature_c)+273.15
        t0=293.15
        t01=273.16
        p=max(float(pressure_kpa),1e-6)
        p0=101.325
        rh=min(100.0,max(0.0,float(humidity_pct)))
        h=rh*(10.0**(-6.8346*((t01/t)**1.261)+4.6151))*(p0/p)
        fr_o=(p/p0)*(24.0+4.04e4*h*(0.02+h)/max(0.391+h,1e-12))
        fr_n=(p/p0)*((t/t0)**-0.5)*(9.0+280.0*h*math.exp(-4.17*(((t/t0)**(-1.0/3.0))-1.0)))
        classical=1.84e-11*(p0/p)*math.sqrt(t/t0)
        oxygen=0.01275*math.exp(-2239.1/t)/max(fr_o+(f*f/max(fr_o,1e-12)),1e-12)
        nitrogen=0.1068*math.exp(-3352.0/t)/max(fr_n+(f*f/max(fr_n,1e-12)),1e-12)
        molecular=((t/t0)**-2.5)*(oxygen+nitrogen)
        return 8.686*(f*f)*(classical+molecular)

    ac1,ac2,ac3=st.columns(3)
    freq=ac1.selectbox(
        "Frecuencia [Hz]",
        [63,125,250,500,1000,2000,4000,8000],
        index=3,
        key="c4l1_s3_freq",
    )
    temp=ac2.slider("Temperatura [°C]",0,35,15,1,key="c4l1_s3_temp")
    rh=ac3.slider("Humedad relativa [%]",20,100,70,5,key="c4l1_s3_rh")
    alpha_m=_alpha_iso_style_db_per_m(freq,temp,rh)
    alpha_km=alpha_m*1000.0
    a_atm=alpha_m*float(d)
    at1,at2,at3=st.columns(3)
    at1.metric("Coeficiente α",f"{alpha_km:.2f} dB/km")
    at2.metric("Aatm",f"{a_atm:.2f} dB")
    at3.metric("Frecuencia analizada",f"{freq} Hz")
    st.caption(
        "Este cálculo replica la formulación educativa ISO 9613-1-style usada por el motor para la absorción atmosférica. "
        "Su efecto aumenta con distancia y frecuencia."
    )

    st.markdown("### 4 · Otros mecanismos de propagación")
    st.markdown(
        "Estos términos forman parte de la misma ecuación, pero se desarrollan con más detalle en las etapas siguientes. "
        "Aquí interesa reconocer qué fenómeno físico representa cada uno y por qué no deben confundirse."
    )
    p1,p2,p3=st.columns(3)
    with p1:
        with st.container(border=True):
            st.markdown("#### 🌱 Agr · efecto de suelo")
            st.markdown(
                "Surge de la **interferencia entre la onda directa y la onda reflejada por el terreno**. "
                "Depende del tipo de suelo, frecuencia, distancia y alturas de fuente y receptor."
            )
            st.markdown("En este ejercicio: **Agr = 0 dB**.")
            st.caption("Se desarrolla en la Etapa 4 con G, alturas y geometría.")
    with p2:
        with st.container(border=True):
            st.markdown("#### 🧱 Abar · difracción")
            st.markdown(
                "Cuando un obstáculo corta la línea de visión, el sonido debe **difractarse alrededor de bordes y extremos**. "
                "La reducción depende de la geometría fuente–barrera–receptor y de la frecuencia."
            )
            st.markdown("En este ejercicio: **Abar = 0 dB**.")
            st.caption("Se desarrolla en la Etapa 7 con difracción y perfil F–B–R.")
    with p3:
        with st.container(border=True):
            st.markdown("#### 🌦️ Cmet · meteorología")
            st.markdown(
                "Representa una **corrección de largo plazo** asociada a condiciones meteorológicas que modifican "
                "la propagación, como perfiles de viento y temperatura. No es lo mismo que Aatm."
            )
            st.markdown("En este ejercicio: **Cmet = 0 dB**.")
            st.caption("Noise Map Lab permite representar esta corrección de forma separada.")

    lp_partial=lwa+dc-a_div-a_atm

    st.markdown("---")
    st.markdown(
        """
        <div style="border:1px solid #d8e6f0;border-radius:20px;padding:20px 22px;
        background:linear-gradient(135deg,#f8fbfe,#eef6fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">EJERCICIO ACUMULATIVO</div>
          <div style="font-size:1.2rem;font-weight:850;color:#16314b;margin:.35rem 0">
            Resuelve la propagación sin ver el resultado
          </div>
          <div style="color:#536b80">
            Este caso es independiente del ejemplo guiado anterior. Se entregan solo los datos de entrada:
            tú debes obtener Lw, Dc, Adiv, Aatm y finalmente Lp en el receptor.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    exercise_cases={
        "Caso A · Excavadora":"Excavadora hidráulica",
        "Caso B · Camión mixer":"Camión mixer",
        "Caso C · Martillo hidráulico":"Martillo hidráulico",
        "Caso D · Bomba de hormigón":"Bomba de hormigón",
    }
    ex_case=st.segmented_control(
        "Selecciona un caso",
        list(exercise_cases.keys()),
        default="Caso A · Excavadora",
        key="c4l1_s3_ex_case",
    )
    ex_name=exercise_cases[ex_case]
    ex_item=BS_PLANT[ex_name]

    exercise_settings={
        "Caso A · Excavadora":{"distance":65,"q":2,"freq":1000,"temp":15,"rh":70},
        "Caso B · Camión mixer":{"distance":90,"q":1,"freq":500,"temp":20,"rh":60},
        "Caso C · Martillo hidráulico":{"distance":45,"q":4,"freq":2000,"temp":10,"rh":80},
        "Caso D · Bomba de hormigón":{"distance":120,"q":2,"freq":1000,"temp":25,"rh":50},
    }
    exs=exercise_settings[ex_case]
    ex_lw=float(ex_item["laeq10"])+28.0
    ex_dc=10*math.log10(float(exs["q"]))
    ex_div=20*math.log10(float(exs["distance"]))+11.0
    ex_alpha=_alpha_iso_style_db_per_m(exs["freq"],exs["temp"],exs["rh"])
    ex_atm=ex_alpha*float(exs["distance"])
    ex_lp=ex_lw+ex_dc-ex_div-ex_atm

    ex_img,ex_data=st.columns([.9,1.6],gap="large")
    with ex_img:
        with st.container(border=True):
            pimg=_machine_image_path(ex_item)
            if pimg:
                st.image(str(pimg),use_container_width=True)
            st.markdown(f"#### {ex_name}")
            st.caption(ex_item["en"])
    with ex_data:
        st.markdown("#### Datos entregados")
        data_html=f"""
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px">
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Nivel a 10 m</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">{ex_item['laeq10']:.0f} dB(A)</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Distancia F–R</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">{exs['distance']} m</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Directividad</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">Q = {exs['q']}</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Frecuencia</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">{exs['freq']} Hz</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Temperatura</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">{exs['temp']} °C</div>
          </div>
          <div style="border:1px solid #dce7f0;border-radius:14px;padding:12px;background:#fff">
            <div style="font-size:.72rem;color:#6a7e90">Humedad relativa</div>
            <div style="font-size:1.15rem;font-weight:900;color:#18324a">{exs['rh']} %</div>
          </div>
        </div>
        """
        st.markdown(data_html,unsafe_allow_html=True)
        st.caption("Para este ejercicio considera Agr = 0 dB, Abar = 0 dB y Cmet = 0 dB.")

    st.markdown("#### Completa la cadena de cálculo")
    x1,x2,x3,x4,x5=st.columns(5)
    ans_lw=x1.text_input("Lw [dB]",key=f"c4l1_s3_ex_lw_{ex_case}",placeholder="Calcula")
    ans_dc=x2.text_input("Dc [dB]",key=f"c4l1_s3_ex_dc_{ex_case}",placeholder="Calcula")
    ans_div=x3.text_input("Adiv [dB]",key=f"c4l1_s3_ex_div_{ex_case}",placeholder="Calcula")
    ans_atm=x4.text_input("Aatm [dB]",key=f"c4l1_s3_ex_atm_{ex_case}",placeholder="Calcula")
    ans_lp=x5.text_input("Lp final [dB]",key=f"c4l1_s3_ex_lp_{ex_case}",placeholder="Calcula")

    if st.button("Comprobar ejercicio",key=f"c4l1_s3_check_{ex_case}",type="primary",use_container_width=True):
        def _num(v):
            try:
                return float(str(v).strip().replace(",","."))
            except Exception:
                return None
        vals=[_num(v) for v in [ans_lw,ans_dc,ans_div,ans_atm,ans_lp]]
        if any(v is None for v in vals):
            st.warning("Completa los cinco valores antes de comprobar.")
        else:
            exp=[ex_lw,ex_dc,ex_div,ex_atm,ex_lp]
            tol=[0.2,0.2,0.2,0.05,0.3]
            ok=[abs(a-b)<=t for a,b,t in zip(vals,exp,tol)]
            labels=["Lw","Dc","Adiv","Aatm","Lp final"]
            if all(ok):
                st.success("Correcto. La cadena de propagación está bien resuelta.")
                st.markdown("#### Solución del caso")
                r1,r2,r3,r4,r5=st.columns(5)
                r1.metric("Lw",f"{ex_lw:.1f} dB")
                r2.metric("+ Dc",f"{ex_dc:+.1f} dB")
                r3.metric("- Adiv",f"{ex_div:.1f} dB")
                r4.metric("- Aatm",f"{ex_atm:.2f} dB")
                r5.metric("Lp receptor",f"{ex_lp:.1f} dB")
            else:
                st.warning("Revisa: " + ", ".join(labels[i] for i,v in enumerate(ok) if not v) + ".")
                st.caption("La app no muestra la solución completa mientras existan resultados incorrectos.")

    if st.session_state.get("role")=="Docente":
        with st.expander("👩‍🏫 Pauta docente · Etapa 3",expanded=False):
            st.markdown(
                f"""
                **Caso de ejercicio:** {ex_case} · {ex_name}  
                **Nivel entregado a 10 m:** {ex_item['laeq10']:.1f} dB(A)  
                **Lw esperado:** {ex_lw:.1f} dB  
                **Q:** {exs['q']} → **Dc:** {ex_dc:.1f} dB  
                **Distancia:** {exs['distance']} m → **Adiv:** {ex_div:.1f} dB  
                **Frecuencia:** {exs['freq']} Hz · **T:** {exs['temp']} °C · **HR:** {exs['rh']} %  
                **Aatm:** {ex_atm:.2f} dB  
                **Agr = Abar = Cmet = 0 dB** en este ejercicio  
                **Lp esperado:** **{ex_lp:.1f} dB**
                """
            )
            st.info(
                "Conducción sugerida: haga que el alumno explique primero qué término cambia al mover el receptor, "
                "cuál cambia al modificar la frecuencia y cuál depende de la orientación de la fuente."
            )

def _stage4(lab, saved):
    _header(
        4,
        "Propagación exterior completa · Agr, Abar y Cmet",
        "Cerrar la ecuación de propagación exterior incorporando efecto de suelo, difracción por barreras y corrección meteorológica.",
    )

    st.markdown(
        """
        <div style="border:1px solid #cfddea;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#f7fbff,#eef5fb);box-shadow:0 8px 20px rgba(31,63,92,.06);
        margin:.25rem 0 1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">CERRAMOS LA ECUACIÓN DE PROPAGACIÓN</div>
          <div style="font-size:.9rem;color:#607386;margin-top:.3rem">
            Ya revisamos <b>Dc</b>, <b>Adiv</b> y <b>Aatm</b>. En esta etapa incorporamos los tres términos que faltan:
            <b>Agr</b>, <b>Abar</b> y <b>Cmet</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.latex(r"L_p = L_W + D_c - A_{div} - A_{atm} - \mathbf{A_{gr}} - \mathbf{A_{bar}} - \mathbf{C_{met}}")
        st.markdown(
            "**Referencia:** enfoque de propagación exterior de **ISO 9613-2:2024**. "
            "Los tres términos resaltados se trabajan en esta etapa."
        )
        progress_html = """
        <div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:.5rem">
          <div style="border-radius:12px;padding:9px;background:#edf6ff;color:#1d5e8a;text-align:center;font-size:.75rem;font-weight:850">✓ Dc</div>
          <div style="border-radius:12px;padding:9px;background:#edf6ff;color:#1d5e8a;text-align:center;font-size:.75rem;font-weight:850">✓ Adiv</div>
          <div style="border-radius:12px;padding:9px;background:#edf6ff;color:#1d5e8a;text-align:center;font-size:.75rem;font-weight:850">✓ Aatm</div>
          <div style="border:2px solid #58a66e;border-radius:12px;padding:8px;background:#eef9f1;color:#2c6c3e;text-align:center;font-size:.75rem;font-weight:900">AHORA · Agr</div>
          <div style="border:2px solid #d59a3c;border-radius:12px;padding:8px;background:#fff7e8;color:#8b5e16;text-align:center;font-size:.75rem;font-weight:900">AHORA · Abar</div>
          <div style="border:2px solid #7c72b8;border-radius:12px;padding:8px;background:#f5f2fb;color:#5c4d8d;text-align:center;font-size:.75rem;font-weight:900">AHORA · Cmet</div>
        </div>
        """
        st.markdown(progress_html,unsafe_allow_html=True)

    st.markdown("### 1 · Agr · efecto de suelo")

    st.markdown(
        """
        <div style="border:1px solid #cfe3d5;border-radius:22px;padding:19px 21px;
        background:linear-gradient(135deg,#f7fcf8,#eef8f1);
        box-shadow:0 8px 22px rgba(45,105,65,.06);margin:.2rem 0 1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.10em;color:#2d7a4a">
            EFECTO DE SUELO · INTERFERENCIA DIRECTA + REFLEJADA
          </div>
          <div style="font-size:.94rem;color:#496756;line-height:1.6;margin-top:.35rem">
            <b>Agr</b> representa la modificación del nivel sonoro producida por la interacción entre
            la onda que llega directamente al receptor y la onda reflejada por el terreno.
            No corresponde a una absorción fija del suelo: depende de la <b>frecuencia</b>,
            del <b>tipo de terreno</b> y de la <b>geometría fuente–receptor</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### Estructura del término de suelo")
        st.latex(r"A_{gr}=A_s+A_m+A_r")
        st.caption(
            "El efecto total de suelo se construye a partir de tres contribuciones espaciales: "
            "región de fuente, región intermedia y región de receptor."
        )

        agr_cards = [
            (
                "Aₛ · región de fuente",
                "Contribución asociada al tramo de terreno próximo a la fuente sonora.",
                "Representa cómo la interferencia entre el camino directo y el reflejado se modifica "
                "en la zona donde se origina la propagación. Depende principalmente del factor de suelo "
                "Gₛ, la frecuencia f, la altura de fuente hₛ y la geometría de propagación.",
                "#edf8f0","#2d7a4a"
            ),
            (
                "Aₘ · región intermedia",
                "Contribución asociada al tramo central del recorrido entre fuente y receptor.",
                "Representa el efecto acumulado del terreno situado entre las regiones extremas. "
                "Su participación depende de la longitud de propagación, de las alturas de fuente y receptor, "
                "del factor de suelo Gₘ y de la condición geométrica del trayecto.",
                "#f4f8ed","#667d2e"
            ),
            (
                "Aᵣ · región de receptor",
                "Contribución asociada al tramo de terreno próximo al receptor.",
                "Describe la influencia del terreno en la zona final de propagación, donde la onda directa "
                "y la reflejada vuelven a combinarse antes de alcanzar el receptor. Depende principalmente "
                "de Gᵣ, la frecuencia f, la altura de receptor hᵣ y la geometría.",
                "#eef6fb","#286b91"
            ),
        ]
        cards_html='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.75rem 0 .45rem">'
        for title,subtitle,desc,bg,color in agr_cards:
            cards_html+=(
                f'<div style="border:1px solid #d9e5dd;border-radius:18px;padding:16px;background:{bg}">'
                f'<div style="font-size:.9rem;font-weight:900;color:{color}">{title}</div>'
                f'<div style="font-size:.79rem;font-weight:750;color:#4e6256;margin:.35rem 0 .45rem">{subtitle}</div>'
                f'<div style="font-size:.79rem;line-height:1.52;color:#627267">{desc}</div>'
                f'</div>'
            )
        cards_html+='</div>'
        st.markdown(cards_html,unsafe_allow_html=True)

        st.info(
            "As, Am y Ar no son materiales ni coeficientes de absorción independientes. "
            "Son contribuciones acústicas del terreno dentro del modelo de propagación."
        )

    st.markdown("#### ¿Cómo se relaciona G con Agr?")
    st.markdown(
        """
        <div style="border-left:4px solid #4d9b68;padding:12px 15px;background:#f7fbf8;
        border-radius:0 14px 14px 0;margin:.25rem 0 .8rem">
          <div style="font-size:.89rem;color:#4a6252;line-height:1.55">
            El factor <b>G</b> caracteriza el comportamiento acústico del terreno.
            <b>No se suma directamente a Agr</b> y tampoco representa un porcentaje de absorción.
            G interviene en el cálculo de las tres contribuciones del suelo y, a través de ellas,
            modifica el valor final de Agr.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.latex(r"G \;\longrightarrow\; A_s,\;A_m,\;A_r \;\longrightarrow\; A_{gr}")
    eq1,eq2,eq3=st.columns(3)
    with eq1:
        st.latex(r"A_s=F_s(G_s,f,h_s,d_p)")
    with eq2:
        st.latex(r"A_m=F_m(G_m,f,h_s,h_r,d_p)")
    with eq3:
        st.latex(r"A_r=F_r(G_r,f,h_r,d_p)")

    st.caption(
        "En este laboratorio se utiliza un único valor G para simplificar la exploración. "
        "En una modelación detallada pueden existir Gs, Gm y Gr diferentes si cambia el tipo de terreno a lo largo del trayecto."
    )

    st.markdown("#### Geometría que controla el efecto de suelo")
    geo1,geo2=st.columns([1.05,1])
    with geo1:
        geo_html="""
        <div style="border:1px solid #d9e4ec;border-radius:18px;padding:15px 17px;background:#fbfdff">
          <div style="font-size:.78rem;font-weight:900;color:#315f7c;margin-bottom:.55rem">VARIABLES GEOMÉTRICAS</div>
          <div style="font-size:.84rem;line-height:1.75;color:#536978">
            <b>h<sub>s</sub> [m]</b> · altura acústica de la fuente respecto del terreno local.<br>
            <b>h<sub>r</sub> [m]</b> · altura acústica del receptor respecto del terreno local.<br>
            <b>d<sub>p</sub> [m]</b> · distancia horizontal o proyectada entre fuente y receptor.<br>
            <b>f [Hz]</b> · frecuencia central de la banda evaluada.
          </div>
        </div>
        """
        st.markdown(geo_html,unsafe_allow_html=True)
        st.info(
            "Un mismo valor de G puede entregar un Agr diferente al cambiar hs, hr, dp o la frecuencia."
        )
    with geo2:
        st.code(
            "                trayectoria directa\n"
            "        Fuente -------------------------- Receptor\n"
            "          ● hs                        hr ●\n"
            "          |                              |\n"
            "__________|______________________________|________ terreno\n"
            "           \\_____ reflexión suelo _____/\n"
            "          <-----------  dp  ------------>",
            language=None,
        )

    st.markdown("#### Factor de suelo G")
    g_cards=[
        ("G = 0","Suelo duro","Hormigón, pavimento, agua o superficie compacta.","#f6f7f8","#59636b"),
        ("G = 0,5","Terreno mixto","Combinación aproximada de sectores duros y porosos.","#fff8eb","#98651c"),
        ("G = 1","Suelo poroso","Pasto, suelo vegetal o tierra porosa.","#eef9f1","#2d7a4a"),
    ]
    gh='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 .85rem">'
    for gv,title,desc,bg,color in g_cards:
        gh+=(
            f'<div style="border:1px solid #d8e2dc;border-radius:18px;padding:16px;background:{bg}">'
            f'<div style="font-size:.76rem;font-weight:900;color:{color};letter-spacing:.04em">{gv}</div>'
            f'<div style="font-size:1rem;font-weight:850;color:#283e32;margin:.3rem 0">{title}</div>'
            f'<div style="font-size:.81rem;color:#65736a;line-height:1.45">{desc}</div></div>'
        )
    gh+='</div>'
    st.markdown(gh,unsafe_allow_html=True)

    st.warning(
        "G = 0,5 no significa que el terreno absorba el 50 % del sonido. "
        "G es un parámetro adimensional utilizado por el modelo para representar el comportamiento acústico del suelo."
    )

    def _ground_att_iso_edu(distance_m, source_height_m, receiver_height_m, ground_factor, frequency_hz):
        dp=max(float(distance_m),1e-6)
        hss=max(float(source_height_m),0.0)
        hrr=max(float(receiver_height_m),0.0)
        gg=min(1.0,max(0.0,float(ground_factor)))
        bands=(63,125,250,500,1000,2000,4000,8000)
        ff=min(bands,key=lambda b:abs(math.log(max(float(frequency_hz),1.0)/b)))

        def aprime(h):
            return 1.5+3.0*math.exp(-0.12*(h-5.0)**2)*(1.0-math.exp(-dp/50.0))+5.7*math.exp(-0.09*h*h)*(1.0-math.exp(-2.8e-6*dp*dp))
        def bprime(h):
            return 1.5+8.6*math.exp(-0.09*h*h)*(1.0-math.exp(-dp/50.0))
        def cprime(h):
            return 1.5+14.0*math.exp(-0.46*h*h)*(1.0-math.exp(-dp/50.0))
        def dprime(h):
            return 1.5+5.0*math.exp(-0.9*h*h)*(1.0-math.exp(-dp/50.0))

        def end_region(h):
            if ff==63:
                return -1.5
            if ff==125:
                return -1.5+gg*aprime(h)
            if ff==250:
                return -1.5+gg*bprime(h)
            if ff==500:
                return -1.5+gg*cprime(h)
            if ff==1000:
                return -1.5+gg*dprime(h)
            return -1.5*(1.0-gg)

        q=0.0
        if dp>30.0*(hss+hrr):
            q=1.0-30.0*(hss+hrr)/dp

        a_s=end_region(hss)
        a_r=end_region(hrr)
        a_m=-3.0*q if ff==63 else -3.0*q*(1.0-gg)

        # Suma estructural de las tres regiones del método.
        a_sum=a_s+a_r+a_m

        # Ajuste geométrico/energético usado por el simulador educativo.
        k_geo=(dp*dp+(hss-hrr)**2)/max(dp*dp+(hss+hrr)**2,1e-12)
        energy_factor=1.0+(10.0**(-a_sum/10.0)-1.0)*k_geo
        agr=-10.0*math.log10(max(energy_factor,1e-12))
        return agr,a_s,a_m,a_r,a_sum,q,k_geo,ff

    st.markdown("#### Explora cómo G y la geometría modifican Agr")
    agr1,agr2,agr3,agr4,agr5=st.columns(5)
    g=agr1.slider("G",0.0,1.0,0.5,0.1,key="c4l1_s4_g")
    freq=agr2.selectbox("Frecuencia [Hz]",[63,125,250,500,1000,2000,4000,8000],index=3,key="c4l1_s4_freq")
    distance=agr3.slider("dp · distancia [m]",10,250,80,5,key="c4l1_s4_distance")
    hs=agr4.slider("hs · fuente [m]",0.5,8.0,1.5,0.5,key="c4l1_s4_hs")
    hr=agr5.slider("hr · receptor [m]",1.0,20.0,1.5,0.5,key="c4l1_s4_hr")

    agr,a_s,a_m,a_r,a_sum,q,k_geo,ff=_ground_att_iso_edu(distance,hs,hr,g,freq)

    st.markdown("##### De los parámetros al resultado")
    st.latex(
        rf"G={g:.2f},\quad f={ff}\,\mathrm{{Hz}},\quad "
        rf"d_p={distance}\,\mathrm{{m}},\quad h_s={hs:.1f}\,\mathrm{{m}},\quad h_r={hr:.1f}\,\mathrm{{m}}"
    )
    r1,r2,r3,r4=st.columns(4)
    r1.metric("As · zona fuente",f"{a_s:+.2f} dB")
    r2.metric("Am · zona intermedia",f"{a_m:+.2f} dB")
    r3.metric("Ar · zona receptor",f"{a_r:+.2f} dB")
    r4.metric("As + Am + Ar",f"{a_sum:+.2f} dB")

    st.latex(
        rf"A_s + A_m + A_r = ({a_s:+.2f}) + ({a_m:+.2f}) + ({a_r:+.2f}) = {a_sum:+.2f}\;\mathrm{{dB}}"
    )
    st.markdown(
        "El simulador aplica después el ajuste geométrico/energético de la formulación implementada para representar "
        "la interferencia entre camino directo y reflejado."
    )
    g1,g2,g3=st.columns(3)
    g1.metric("q geométrico",f"{q:.3f}")
    g2.metric("Factor geométrico",f"{k_geo:.3f}")
    g3.metric("Agr del escenario",f"{agr:+.2f} dB")

    st.caption(
        "Así se puede seguir la cadena completa: G, frecuencia y geometría → As/Am/Ar → suma de contribuciones "
        "→ ajuste geométrico → Agr. El signo puede resultar contraintuitivo porque Agr representa interferencia "
        "de caminos, no una absorción simple."
    )

    st.markdown("### 2 · Abar · barreras y difracción")
    st.markdown(
        "Una barrera es efectiva cuando **interrumpe la línea de visión acústica** entre la fuente y el receptor. "
        "El sonido no se detiene en el borde: se difracta por sobre la barrera y alrededor de sus extremos. "
        "Por eso el parámetro clave es cuánto más largo resulta el camino difractado respecto del camino directo."
    )
    st.markdown(
        """
        <div style="border:1px solid #eadfc8;border-radius:18px;padding:16px 18px;background:#fffaf2;margin:.45rem 0 1rem">
          <div style="font-size:.75rem;font-weight:900;color:#9a6617;letter-spacing:.08em">ZONA DE SOMBRA ACÚSTICA</div>
          <div style="font-size:.9rem;color:#6d5a3b;line-height:1.55;margin-top:.25rem">
            Cuando la barrera corta la línea directa entre fuente y receptor se forma detrás de ella una
            <b>zona de sombra acústica</b>. En esa región el receptor ya no recibe el camino directo dominante;
            el sonido que llega lo hace principalmente por <b>difracción sobre el borde superior y alrededor de los extremos</b>.
            La sombra no significa silencio: significa que el nivel queda reducido respecto del campo directo.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    shadow_cards=[
        ("Dentro de la sombra","La línea directa está bloqueada y la contribución difractada pasa a ser dominante."),
        ("Cerca del borde","La reducción puede ser menor porque el receptor está próximo a la frontera entre zona iluminada y sombra."),
        ("Más profundo en la sombra","A igualdad de frecuencia y geometría lateral, suele aumentar la diferencia de camino y puede aumentar Abar."),
    ]
    sh='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 1rem">'
    for title,desc in shadow_cards:
        sh+=(
            f'<div style="border:1px solid #eadfc8;border-radius:16px;padding:14px;background:#fff">'
            f'<div style="font-size:.9rem;font-weight:850;color:#5d431d">{title}</div>'
            f'<div style="font-size:.8rem;color:#746247;line-height:1.4;margin-top:.3rem">{desc}</div></div>'
        )
    sh+='</div>'
    st.markdown(sh,unsafe_allow_html=True)


    with st.container(border=True):
        st.markdown("#### Geometría básica de la barrera")
        st.latex(r"z=(d_{FB}+d_{BR})-d_{FR}")
        st.markdown(
            "**z** es la diferencia de camino. Si la barrera sobresale claramente sobre la línea directa, "
            "el recorrido F–B–R aumenta y también puede aumentar la atenuación por difracción."
        )
        st.latex(r"A_{bar}=10\log_{10}\left[1+\left(2+\frac{20}{\lambda}z\right)K_{met}\right]")
        st.caption(
            "Esta expresión reproduce el esquema didáctico usado aquí para la difracción superior. "
            "λ es la longitud de onda y Kmet es un factor geométrico/meteorológico de la formulación."
        )

    simple_cards=[
        ("1 · ¿La barrera tapa la visual?","Primero se compara la altura del borde con la línea recta fuente–receptor."),
        ("2 · ¿Cuánto se alarga el camino?","Se calcula z comparando la ruta F–B–R con la ruta directa F–R."),
        ("3 · ¿Qué frecuencia analizamos?","La longitud de onda cambia con la frecuencia y modifica la difracción."),
    ]
    bh='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 1rem">'
    for title,desc in simple_cards:
        bh+=(f'<div style="border:1px solid #eadfc8;border-radius:17px;padding:15px;background:#fff">'
             f'<div style="font-size:.95rem;font-weight:850;color:#5b421e">{title}</div>'
             f'<div style="font-size:.82rem;color:#746247;line-height:1.4;margin-top:.3rem">{desc}</div></div>')
    bh+='</div>'
    st.markdown(bh,unsafe_allow_html=True)

    def _barrier_dz_edu(ds,dr,direct,frequency_hz,max_db=20.0):
        wavelength=343.0/max(float(frequency_hz),1.0)
        z=(float(ds)+float(dr))-float(direct)
        z_min=-2.0*wavelength/20.0
        if z<=z_min:
            return 0.0
        denom=max(2.0*(z-z_min),1e-12)
        geometric=(max(ds,dr)*min(ds,dr)*max(direct,0.0))/denom
        k_met=math.exp(-(1.0/2000.0)*math.sqrt(max(geometric,0.0)))
        argument=1.0+(2.0+(20.0/wavelength)*z)*k_met
        return min(max_db,max(0.0,10.0*math.log10(max(argument,1.0))))

    st.markdown("#### Perfil fuente – barrera – receptor")
    p1,p2,p3,p4,p5,p6=st.columns(6)
    hs_bar=p1.slider("Altura fuente [m]",0.5,6.0,1.5,0.5,key="c4l1_s4_bar_hs")
    hb_bar=p2.slider("Altura barrera [m]",0.5,8.0,3.0,0.5,key="c4l1_s4_bar_hb")
    hr_bar=p3.slider("Altura receptor [m]",0.5,12.0,1.5,0.5,key="c4l1_s4_bar_hr")
    d_fb=p4.slider("F → B [m]",5,100,25,5,key="c4l1_s4_dfb")
    d_br=p5.slider("B → R [m]",5,150,35,5,key="c4l1_s4_dbr")
    freq_bar=p6.selectbox("Frecuencia [Hz]",[125,250,500,1000,2000,4000],index=2,key="c4l1_s4_bar_freq")

    total_h=float(d_fb+d_br)
    los_at_bar=float(hs_bar)+(float(hr_bar)-float(hs_bar))*(float(d_fb)/max(total_h,1e-9))
    screens=float(hb_bar)>los_at_bar
    d_fr=math.sqrt(total_h**2+(float(hr_bar)-float(hs_bar))**2)
    d_sb=math.sqrt(float(d_fb)**2+(float(hb_bar)-float(hs_bar))**2)
    d_br_path=math.sqrt(float(d_br)**2+(float(hb_bar)-float(hr_bar))**2)
    z_path=(d_sb+d_br_path)-d_fr
    abar=_barrier_dz_edu(d_sb,d_br_path,d_fr,freq_bar) if screens else 0.0

    max_h=max(float(hs_bar),float(hb_bar),float(hr_bar),2.0)+1.5
    x_s=90.0
    x_r=810.0
    x_b=x_s+(x_r-x_s)*(float(d_fb)/max(total_h,1e-9))
    ground_y=285.0
    top_y=55.0
    scale_y=(ground_y-top_y)/max_h
    y_s=ground_y-float(hs_bar)*scale_y
    y_b=ground_y-float(hb_bar)*scale_y
    y_r=ground_y-float(hr_bar)*scale_y
    los_color="#d9534f" if screens else "#5f768a"
    status_text="Barrera intercepta la línea de visión" if screens else "Barrera no intercepta la línea de visión"
    status_bg="#eef8f1" if screens else "#fff6e8"
    status_color="#2d6d42" if screens else "#8b5c13"

    profile_svg=f"""
    <div style="border:1px solid #d9e4ec;border-radius:20px;background:#fbfdff;padding:12px 14px;margin:.4rem 0 1rem">
      <div style="font-size:.74rem;font-weight:900;color:#526a7e;letter-spacing:.08em;margin:2px 0 8px">
        PERFIL F–B–R · CORTE LATERAL SIMPLIFICADO
      </div>
      <svg viewBox="0 0 900 340" width="100%" style="display:block;max-height:390px">
        <rect x="0" y="0" width="900" height="340" rx="18" fill="#f8fbfd"/>
        <line x1="55" y1="{ground_y}" x2="845" y2="{ground_y}" stroke="#8c9a88" stroke-width="4"/>
        <rect x="{x_b-8:.1f}" y="{y_b:.1f}" width="16" height="{ground_y-y_b:.1f}" rx="3" fill="#485b68"/>
        {'<polygon points="' + f'{x_b:.1f},{y_b:.1f} {x_r},{y_r:.1f} {x_r},{ground_y} {x_b:.1f},{ground_y}' + '" fill="rgba(226,139,45,0.10)"/>' if screens else ''}
        <line x1="{x_s}" y1="{y_s:.1f}" x2="{x_r}" y2="{y_r:.1f}" stroke="{los_color}" stroke-width="3" stroke-dasharray="9 7"/>
        <polyline points="{x_s},{y_s:.1f} {x_b:.1f},{y_b:.1f} {x_r},{y_r:.1f}" fill="none" stroke="#e28b2d" stroke-width="4"/>
        {'<text x="' + f'{(x_b+x_r)/2-70:.1f}' + '" y="' + f'{ground_y-24:.1f}' + '" font-size="14" font-weight="800" fill="#9a6617">ZONA DE SOMBRA</text>' if screens else ''}
        <circle cx="{x_s}" cy="{y_s:.1f}" r="12" fill="#176b9b"/>
        <circle cx="{x_r}" cy="{y_r:.1f}" r="12" fill="#2f7d4b"/>
        <circle cx="{x_b:.1f}" cy="{y_b:.1f}" r="7" fill="#e28b2d"/>
        <text x="{x_s-18}" y="{y_s-20:.1f}" font-size="18" font-weight="800" fill="#176b9b">F</text>
        <text x="{x_b-7:.1f}" y="{y_b-16:.1f}" font-size="18" font-weight="800" fill="#7c4d12">B</text>
        <text x="{x_r-2}" y="{y_r-20:.1f}" font-size="18" font-weight="800" fill="#2f7d4b">R</text>
        <text x="{(x_s+x_b)/2-30:.1f}" y="{min(y_s,y_b)-12:.1f}" font-size="14" fill="#8a5c1c">dFB</text>
        <text x="{(x_b+x_r)/2-30:.1f}" y="{min(y_b,y_r)-12:.1f}" font-size="14" fill="#8a5c1c">dBR</text>
        <text x="{(x_s+x_r)/2-35:.1f}" y="{(y_s+y_r)/2+28:.1f}" font-size="14" fill="#5f768a">dFR directo</text>
        <line x1="{x_s}" y1="{ground_y+18}" x2="{x_b:.1f}" y2="{ground_y+18}" stroke="#9fb0bd" stroke-width="2"/>
        <line x1="{x_b:.1f}" y1="{ground_y+18}" x2="{x_r}" y2="{ground_y+18}" stroke="#9fb0bd" stroke-width="2"/>
        <text x="{(x_s+x_b)/2-28:.1f}" y="{ground_y+38}" font-size="13" fill="#6a7d8e">{d_fb} m</text>
        <text x="{(x_b+x_r)/2-28:.1f}" y="{ground_y+38}" font-size="13" fill="#6a7d8e">{d_br} m</text>
      </svg>
      <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-top:4px">
        <div style="border-radius:13px;padding:11px;background:{status_bg};color:{status_color};font-size:.78rem;font-weight:850">{status_text}</div>
        <div style="border-radius:13px;padding:11px;background:#f2f6f9;color:#334f63;font-size:.78rem"><b>Altura LOS en B</b><br>{los_at_bar:.2f} m</div>
        <div style="border-radius:13px;padding:11px;background:#fff7e9;color:#80571b;font-size:.78rem"><b>z</b><br>{z_path:.3f} m</div>
        <div style="border-radius:13px;padding:11px;background:#eef5fb;color:#1b5b86;font-size:.78rem"><b>Abar</b><br>{abar:.1f} dB</div>
      </div>
    </div>
    """
    st.markdown(profile_svg,unsafe_allow_html=True)

    st.markdown(
        f"Para este perfil, la línea directa pasa a **{los_at_bar:.2f} m** en la posición de la barrera. "
        f"La barrera mide **{hb_bar:.1f} m**, por lo que **{'sí' if screens else 'no'}** interrumpe la línea de visión."
    )
    bb1,bb2,bb3,bb4=st.columns(4)
    bb1.metric("dFR directo",f"{d_fr:.2f} m")
    bb2.metric("dFB + dBR",f"{d_sb+d_br_path:.2f} m")
    bb3.metric("z",f"{z_path:.3f} m")
    bb4.metric("Abar",f"{abar:.1f} dB")

    st.caption(
        "Este perfil es una versión docente simplificada del perfil fuente–barrera–receptor que se utilizará más adelante. "
        "Cuando la barrera bloquea la línea directa, el sombreado indica de forma conceptual la zona de sombra acústica; "
        "el límite real de esa zona depende también de la geometría lateral y de la difracción por los extremos."
    )

    st.markdown("### 3 · Cmet · corrección meteorológica de largo plazo")
    st.markdown(
        "Hasta ahora hemos calculado pérdidas asociadas a la **distancia, el aire, el suelo y las barreras**. "
        "Pero la propagación exterior también cambia con las condiciones meteorológicas: el viento y los gradientes "
        "de temperatura pueden curvar las trayectorias del sonido y hacer que determinadas direcciones sean más o menos favorables."
    )

    st.markdown(
        """
        <div style="border:1px solid #ddd8ef;border-radius:18px;padding:16px 18px;background:#faf8ff;margin:.4rem 0 1rem">
          <div style="font-size:.75rem;font-weight:900;color:#65549a;letter-spacing:.08em">IDEA SIMPLE</div>
          <div style="font-size:.92rem;color:#574f6d;line-height:1.55;margin-top:.25rem">
            <b>Cmet no intenta predecir el clima de un día específico.</b> Es una corrección de largo plazo:
            representa que las condiciones favorables para que el sonido llegue al receptor no ocurren todo el tiempo.
            Por eso se resta del nivel calculado para condiciones favorables.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    met_cards=[
        ("Aatm","Absorción del aire","Pérdida física por el medio atmosférico. Depende de frecuencia, temperatura, humedad y distancia."),
        ("Cmet","Frecuencia de condiciones favorables","Corrección estadística de largo plazo asociada a viento, gradientes térmicos y geometría."),
        ("C0","Magnitud meteorológica máxima","Representa cuánto puede pesar la corrección meteorológica del sitio/dirección cuando la distancia es suficientemente grande."),
    ]
    mh='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 1rem">'
    for sym,title,desc in met_cards:
        mh+=(
            f'<div style="border:1px solid #ddd8ef;border-radius:16px;padding:15px;background:#fff">'
            f'<div style="font-size:.76rem;font-weight:900;color:#65549a">{sym}</div>'
            f'<div style="font-size:.95rem;font-weight:850;color:#3f365f;margin:.2rem 0">{title}</div>'
            f'<div style="font-size:.82rem;color:#6d6680;line-height:1.4">{desc}</div></div>'
        )
    mh+='</div>'
    st.markdown(mh,unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### Ecuación de Cmet")
        st.latex(r"C_{met}=C_0\left[1-\frac{10(h_s+h_r)}{d_p}\right]")
        st.markdown(
            "La ecuación se aplica cuando **dp > 10(hs + hr)**. Si esa condición no se cumple, "
            "**Cmet = 0 dB** en este esquema."
        )
        st.markdown(
            "- **C0 [dB]:** parámetro meteorológico de largo plazo para el sitio y la dirección fuente–receptor.\n"
            "- **hs [m]:** altura de la fuente sobre el terreno.\n"
            "- **hr [m]:** altura del receptor sobre el terreno.\n"
            "- **dp [m]:** distancia horizontal fuente–receptor."
        )

    st.markdown("#### ¿De dónde sale C0?")
    st.markdown(
        """
        <div style="border:1px solid #ddd8ef;border-radius:18px;padding:16px 18px;
        background:linear-gradient(135deg,#fbf9ff,#f5f1fb);margin:.35rem 0 .85rem">
          <div style="font-size:.76rem;font-weight:900;color:#65549a;letter-spacing:.08em">
            C0 NO ES EL VIENTO DEL MOMENTO
          </div>
          <div style="font-size:.88rem;color:#625a76;line-height:1.55;margin-top:.3rem">
            <b>C0 se obtiene o selecciona a partir de información meteorológica de largo plazo</b>
            representativa del sitio y de la dirección de propagación. Resume estadísticamente
            cuánto pesan las condiciones favorables de propagación asociadas al viento y a los
            gradientes térmicos. Por eso no debe deducirse a partir de una sola medición de
            temperatura, humedad o velocidad del viento.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c0_steps=[
        ("1 · Define la dirección","Fuente → receptor","C0 puede cambiar entre receptores ubicados en direcciones distintas."),
        ("2 · Reúne climatología","Viento + estabilidad térmica","Usa estadísticas representativas del periodo de evaluación, no el clima de una hora."),
        ("3 · Obtén o adopta C0","Estudio / modelo / criterio declarado","El valor debe quedar documentado y ser coherente con el objetivo del cálculo."),
    ]
    c0h='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 .9rem">'
    for title,sub,desc in c0_steps:
        c0h+=(
            f'<div style="border:1px solid #e2deef;border-radius:16px;padding:14px;background:#fff">'
            f'<div style="font-size:.87rem;font-weight:850;color:#443965">{title}</div>'
            f'<div style="font-size:.76rem;font-weight:800;color:#766d8d;margin:.25rem 0">{sub}</div>'
            f'<div style="font-size:.78rem;color:#716982;line-height:1.42">{desc}</div></div>'
        )
    c0h+='</div>'
    st.markdown(c0h,unsafe_allow_html=True)

    st.info(
        "Si no existe una base meteorológica que permita justificar C0, no conviene inventarlo. "
        "Para estudiar condiciones favorables puede utilizarse **C0 = 0 dB**, lo que deja **Cmet = 0 dB** "
        "y no reduce el nivel calculado."
    )

    st.markdown("#### ¿Cómo se interpreta?")
    interp_cards=[
        ("Receptor relativamente cerca","dp ≤ 10(hs + hr)","Cmet = 0 dB","La geometría cercana domina y no se aplica esta corrección."),
        ("Distancia intermedia","dp > 10(hs + hr)","0 < Cmet < C0","La corrección comienza a crecer con la distancia."),
        ("Distancia muy grande","dp ≫ 10(hs + hr)","Cmet → C0","La corrección se aproxima al valor máximo definido por C0."),
    ]
    ih='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.4rem 0 1rem">'
    for title,cond,res,desc in interp_cards:
        ih+=(
            f'<div style="border:1px solid #e2deef;border-radius:16px;padding:14px;background:#fff">'
            f'<div style="font-size:.9rem;font-weight:850;color:#443965">{title}</div>'
            f'<div style="font-size:.76rem;color:#766d8d;margin:.3rem 0">{cond}</div>'
            f'<div style="font-size:1rem;font-weight:900;color:#65549a">{res}</div>'
            f'<div style="font-size:.78rem;color:#716982;margin-top:.3rem">{desc}</div></div>'
        )
    ih+='</div>'
    st.markdown(ih,unsafe_allow_html=True)

    def _cmet_edu(dp,hss,hrr,c0):
        lim=10.0*(float(hss)+float(hrr))
        if float(dp)<=lim or float(c0)<=0.0:
            return 0.0
        return float(c0)*max(0.0,1.0-lim/float(dp))

    st.markdown("#### Selecciona cómo definir C0")
    c0_mode=st.radio(
        "Origen de C0",
        [
            "Condición favorable / conservadora · C0 = 0 dB",
            "Valor conocido del proyecto o estudio meteorológico",
            "Exploración didáctica de sensibilidad",
        ],
        horizontal=True,
        key="c4l1_s4_c0_mode",
    )

    if c0_mode.startswith("Condición favorable"):
        c0=0.0
        st.success(
            "**C0 = 0 dB.** No se aplica reducción meteorológica de largo plazo. "
            "Este modo permite conservar el nivel calculado para condiciones favorables."
        )
    elif c0_mode.startswith("Valor conocido"):
        c0=st.number_input(
            "C0 documentado [dB]",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            key="c4l1_s4_c0_known",
            help="Ingresa el valor obtenido del estudio meteorológico, modelo o antecedente técnico del proyecto."
        )
        st.caption(
            "Registra siempre la fuente del valor: periodo estadístico, estación o modelo utilizado y dirección fuente–receptor."
        )
    else:
        c0=st.slider(
            "C0 de exploración [dB]",
            0.0,5.0,3.0,0.5,
            key="c4l1_s4_c0_sensitivity",
            help="Solo para observar sensibilidad. No representa una determinación normativa de C0."
        )
        st.warning(
            "Modo didáctico: mueve C0 para observar cuánto influye en Cmet. "
            "Este control no calcula C0 desde datos meteorológicos reales."
        )

    st.markdown("#### Explora el efecto de la geometría")
    cm1,cm2,cm3=st.columns(3)
    dp=cm1.slider("Distancia horizontal dp [m]",20,500,150,10,key="c4l1_s4_cmet_d")
    cm_hs=cm2.slider("Altura fuente hs [m]",0.5,10.0,1.5,0.5,key="c4l1_s4_cmet_hs")
    cm_hr=cm3.slider("Altura receptor hr [m]",1.0,20.0,1.5,0.5,key="c4l1_s4_cmet_hr")

    cmet=_cmet_edu(dp,cm_hs,cm_hr,c0)
    threshold=10.0*(cm_hs+cm_hr)
    applies=dp>threshold and c0>0

    st.latex(
        rf"C_{{met}}={c0:.2f}\left[1-\frac{{10({cm_hs:.1f}+{cm_hr:.1f})}}{{{dp:.0f}}}\right]"
    )

    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("C0 adoptado",f"{c0:.2f} dB")
    m2.metric("Umbral 10(hs+hr)",f"{threshold:.1f} m")
    m3.metric("dp",f"{dp:.0f} m")
    m4.metric("¿Aplica Cmet?","Sí" if applies else "No")
    m5.metric("Cmet",f"{cmet:.2f} dB")

    if applies:
        st.success(
            f"Como dp = {dp:.0f} m es mayor que 10(hs+hr) = {threshold:.1f} m, "
            f"el C0 adoptado de {c0:.2f} dB genera **Cmet = {cmet:.2f} dB**. "
            "Este valor se resta en la ecuación de propagación de largo plazo."
        )
    elif c0<=0:
        st.info(
            "C0 = 0 dB, por lo que **Cmet = 0 dB** independientemente de la distancia. "
            "No se aplica una reducción meteorológica de largo plazo."
        )
    else:
        st.info(
            f"dp = {dp:.0f} m no supera 10(hs+hr) = {threshold:.1f} m; "
            "por lo tanto, en este esquema **Cmet = 0 dB**."
        )

    st.caption(
        "Cadena de decisión: climatología y dirección fuente–receptor → C0 → geometría hs/hr/dp → Cmet → nivel de largo plazo."
    )

    st.markdown("### 4 · La ecuación ya está completa")
    st.markdown(
        """
        <div style="border:1px solid #cfddea;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#f7fbff,#eef5fb);
        box-shadow:0 8px 20px rgba(31,63,92,.06);margin:.25rem 0 1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">
            CIERRE DEL MODELO DE PROPAGACIÓN
          </div>
          <div style="font-size:1.15rem;font-weight:850;color:#17324b;margin:.35rem 0 .45rem">
            Todos los mecanismos principales ya están dentro de la ecuación
          </div>
          <div style="font-size:.9rem;color:#5b7184;line-height:1.55">
            A partir de aquí el problema deja de ser “qué término falta” y pasa a ser
            <b>cómo cambia cada término según el escenario real</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.latex(r"L_p = L_W + D_c - A_{div} - A_{atm} - A_{gr} - A_{bar} - C_{met}")

        eq_cards=[
            ("Lw","Emisión","Nivel de potencia sonora de la fuente.","#eef6fb","#176b9b"),
            ("Dc","Directividad","Corrección por orientación o concentración de la emisión.","#f3f7fb","#46647a"),
            ("Adiv","Distancia","Pérdida por divergencia geométrica.","#f7f8fa","#5d6670"),
            ("Aatm","Atmósfera","Pérdida por absorción del aire.","#f7f8fa","#5d6670"),
            ("Agr","Suelo","Interferencia entre camino directo y reflejado.","#eef9f1","#2d7a4a"),
            ("Abar","Barrera","Atenuación por difracción y geometría de pantalla.","#fff7e9","#98651c"),
            ("Cmet","Meteorología","Corrección estadística de largo plazo.","#f5f2fb","#65549a"),
        ]
        eqh='<div style="display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;margin:.8rem 0 .45rem">'
        for sym,title,desc,bg,color in eq_cards:
            eqh+=(
                f'<div style="border:1px solid #dce5eb;border-radius:14px;padding:11px 9px;background:{bg};min-height:116px">'
                f'<div style="font-size:.84rem;font-weight:900;color:{color}">{sym}</div>'
                f'<div style="font-size:.73rem;font-weight:800;color:#41576a;margin:.2rem 0 .3rem">{title}</div>'
                f'<div style="font-size:.69rem;line-height:1.35;color:#687b89">{desc}</div></div>'
            )
        eqh+='</div>'
        st.markdown(eqh,unsafe_allow_html=True)

        st.markdown(
            """
            <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;
            margin:.75rem 0 .2rem">
              <div style="border-radius:14px;padding:12px 14px;background:#eef6fb;color:#245b7e;text-align:center">
                <div style="font-size:.72rem;font-weight:900;letter-spacing:.06em">FUENTE</div>
                <div style="font-size:.83rem;margin-top:.2rem">Lw + Dc</div>
              </div>
              <div style="font-size:1.25rem;color:#7a8f9e;font-weight:800">→</div>
              <div style="border-radius:14px;padding:12px 14px;background:#f6f8fa;color:#485d6d;text-align:center">
                <div style="font-size:.72rem;font-weight:900;letter-spacing:.06em">PROPAGACIÓN</div>
                <div style="font-size:.83rem;margin-top:.2rem">Adiv + Aatm + Agr + Abar + Cmet</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.success(
        "Idea clave: el nivel en el receptor se obtiene combinando la emisión de la fuente con las pérdidas y correcciones "
        "que aparecen durante la propagación. En las etapas siguientes usaremos esta ecuación para representar una obra real."
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="border:1px solid #d8e6f0;border-radius:22px;padding:22px 24px;
        background:linear-gradient(135deg,#f8fbfe,#eef6fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">
            EJERCICIO DE DISEÑO · BARRERA ACÚSTICA
          </div>
          <div style="font-size:1.22rem;font-weight:850;color:#16314b;margin:.35rem 0">
            Diseña una barrera para cumplir un objetivo acústico
          </div>
          <div style="color:#536b80;line-height:1.55">
            Una fuente genera un nivel en el receptor superior al objetivo. Debes diseñar la barrera
            ajustando su <b>altura</b> y su <b>ubicación</b> hasta lograr que el nivel final sea
            <b>igual o inferior a 50 dBA</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lp_without_barrier=56.0
    lp_target=50.0
    required_reduction=lp_without_barrier-lp_target

    case1,case2,case3=st.columns(3)
    case1.metric("Nivel sin barrera",f"{lp_without_barrier:.1f} dBA")
    case2.metric("Objetivo",f"≤ {lp_target:.1f} dBA")
    case3.metric("Reducción mínima requerida",f"{required_reduction:.1f} dB")

    st.markdown(
        """
        <div style="border:1px solid #e1e8ef;border-radius:18px;padding:17px 19px;background:#fff;margin:.7rem 0 1rem">
          <div style="font-size:.8rem;font-weight:900;color:#17324a">INSTRUCCIÓN</div>
          <div style="color:#5e7385;line-height:1.5;margin-top:.25rem">
            Modifica la geometría de la barrera. Observa cómo cambian la línea de visión,
            la zona de sombra acústica, la diferencia de camino <b>z</b>, la atenuación <b>Abar</b>
            y el nivel final estimado en el receptor.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Variables de diseño")
    d1,d2,d3,d4=st.columns(4)
    ex_hs=d1.slider("Altura fuente hs [m]",0.5,6.0,1.5,0.5,key="c4l1_s4_design_hs")
    ex_hr=d2.slider("Altura receptor hr [m]",0.5,10.0,1.5,0.5,key="c4l1_s4_design_hr")
    ex_hb=d3.slider("Altura barrera hb [m]",0.5,8.0,2.5,0.1,key="c4l1_s4_design_hb")
    ex_freq=d4.selectbox("Frecuencia [Hz]",[125,250,500,1000,2000,4000],index=2,key="c4l1_s4_design_freq")

    d5,d6=st.columns(2)
    ex_dfb=d5.slider("Distancia fuente → barrera [m]",2.0,40.0,10.0,0.5,key="c4l1_s4_design_dfb")
    ex_dbr=d6.slider("Distancia barrera → receptor [m]",5.0,60.0,20.0,0.5,key="c4l1_s4_design_dbr")

    ex_total=ex_dfb+ex_dbr
    ex_los=ex_hs+(ex_hr-ex_hs)*(ex_dfb/max(ex_total,1e-9))
    ex_screens=ex_hb>ex_los
    ex_direct=math.sqrt(ex_total**2+(ex_hr-ex_hs)**2)
    ex_ds=math.sqrt(ex_dfb**2+(ex_hb-ex_hs)**2)
    ex_dr=math.sqrt(ex_dbr**2+(ex_hb-ex_hr)**2)
    ex_z=(ex_ds+ex_dr)-ex_direct
    ex_abar=_barrier_dz_edu(ex_ds,ex_dr,ex_direct,ex_freq) if ex_screens else 0.0
    lp_with_barrier=lp_without_barrier-ex_abar
    complies=lp_with_barrier<=lp_target

    max_h=max(float(ex_hs),float(ex_hb),float(ex_hr),2.0)+1.5
    x_s=90.0
    x_r=810.0
    x_b=x_s+(x_r-x_s)*(float(ex_dfb)/max(ex_total,1e-9))
    ground_y=285.0
    top_y=55.0
    scale_y=(ground_y-top_y)/max_h
    y_s=ground_y-float(ex_hs)*scale_y
    y_b=ground_y-float(ex_hb)*scale_y
    y_r=ground_y-float(ex_hr)*scale_y

    profile_status="CUMPLE OBJETIVO" if complies else "AÚN NO CUMPLE"
    profile_status_bg="#eaf7ee" if complies else "#fff3e2"
    profile_status_color="#25623a" if complies else "#8a5710"

    # Mantener siempre una etiqueta SVG válida. Cuando la barrera no bloquea
    # la línea de visión no dejamos una línea vacía dentro del bloque HTML,
    # porque Markdown puede cerrar el bloque SVG y mostrar el resto como código.
    shadow_polygon=(
        f'<polygon points="{x_b:.1f},{y_b:.1f} {x_r},{y_r:.1f} '
        f'{x_r},{ground_y} {x_b:.1f},{ground_y}" '
        'fill="rgba(226,139,45,0.11)"/>'
        if ex_screens else '<g aria-hidden="true"></g>'
    )
    shadow_label=(
        f'<text x="{(x_b+x_r)/2-72:.1f}" y="{ground_y-24:.1f}" '
        'font-size="14" font-weight="800" fill="#9a6617">ZONA DE SOMBRA</text>'
        if ex_screens else '<g aria-hidden="true"></g>'
    )

    design_svg=f"""
    <div style="border:1px solid #d9e4ec;border-radius:20px;background:#fbfdff;padding:12px 14px;margin:.5rem 0 1rem">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;margin:2px 0 8px">
        <div style="font-size:.74rem;font-weight:900;color:#526a7e;letter-spacing:.08em">
          PERFIL DE DISEÑO · FUENTE – BARRERA – RECEPTOR
        </div>
        <div style="border-radius:999px;padding:7px 12px;background:{profile_status_bg};color:{profile_status_color};
        font-size:.72rem;font-weight:900">{profile_status}</div>
      </div>
      <svg viewBox="0 0 900 340" width="100%" style="display:block;max-height:390px">
        <rect x="0" y="0" width="900" height="340" rx="18" fill="#f8fbfd"/>
        <line x1="55" y1="{ground_y}" x2="845" y2="{ground_y}" stroke="#8c9a88" stroke-width="4"/>
        <rect x="{x_b-8:.1f}" y="{y_b:.1f}" width="16" height="{ground_y-y_b:.1f}" rx="3" fill="#485b68"/>
        {shadow_polygon}
        <line x1="{x_s}" y1="{y_s:.1f}" x2="{x_r}" y2="{y_r:.1f}" stroke="#d9534f" stroke-width="3" stroke-dasharray="9 7"/>
        <polyline points="{x_s},{y_s:.1f} {x_b:.1f},{y_b:.1f} {x_r},{y_r:.1f}" fill="none" stroke="#e28b2d" stroke-width="4"/>
        <circle cx="{x_s}" cy="{y_s:.1f}" r="12" fill="#176b9b"/>
        <circle cx="{x_r}" cy="{y_r:.1f}" r="12" fill="#2f7d4b"/>
        <circle cx="{x_b:.1f}" cy="{y_b:.1f}" r="7" fill="#e28b2d"/>
        <text x="{x_s-18}" y="{y_s-20:.1f}" font-size="18" font-weight="800" fill="#176b9b">F</text>
        <text x="{x_b-7:.1f}" y="{y_b-16:.1f}" font-size="18" font-weight="800" fill="#7c4d12">B</text>
        <text x="{x_r-2}" y="{y_r-20:.1f}" font-size="18" font-weight="800" fill="#2f7d4b">R</text>
        <text x="{(x_s+x_b)/2-28:.1f}" y="{min(y_s,y_b)-12:.1f}" font-size="14" fill="#8a5c1c">dFB</text>
        <text x="{(x_b+x_r)/2-28:.1f}" y="{min(y_b,y_r)-12:.1f}" font-size="14" fill="#8a5c1c">dBR</text>
        <text x="{(x_s+x_r)/2-38:.1f}" y="{(y_s+y_r)/2+28:.1f}" font-size="14" fill="#5f768a">camino directo</text>
        <line x1="{x_s}" y1="{ground_y+18}" x2="{x_b:.1f}" y2="{ground_y+18}" stroke="#9fb0bd" stroke-width="2"/>
        <line x1="{x_b:.1f}" y1="{ground_y+18}" x2="{x_r}" y2="{ground_y+18}" stroke="#9fb0bd" stroke-width="2"/>
        <text x="{(x_s+x_b)/2-22:.1f}" y="{ground_y+38}" font-size="13" fill="#6a7d8e">{ex_dfb:.1f} m</text>
        <text x="{(x_b+x_r)/2-22:.1f}" y="{ground_y+38}" font-size="13" fill="#6a7d8e">{ex_dbr:.1f} m</text>
        {shadow_label}
      </svg>
    </div>
    """
    st.markdown(design_svg,unsafe_allow_html=True)

    st.markdown("### Resultado del diseño")
    rr1,rr2,rr3,rr4,rr5=st.columns(5)
    rr1.metric("Línea de visión","Bloqueada" if ex_screens else "Libre")
    rr2.metric("z",f"{ex_z:.3f} m")
    rr3.metric("Abar",f"{ex_abar:.1f} dB")
    rr4.metric("Lp final",f"{lp_with_barrier:.1f} dBA")
    rr5.metric("Objetivo","Cumple" if complies else "No cumple")

    if complies:
        st.success(
            f"Buen diseño. El nivel final estimado es **{lp_with_barrier:.1f} dBA**, "
            f"por lo que cumple con el objetivo de **≤ {lp_target:.1f} dBA**."
        )
    else:
        deficit=lp_with_barrier-lp_target
        st.warning(
            f"Aún no cumple. El nivel final estimado es **{lp_with_barrier:.1f} dBA**. "
            f"Necesitas aproximadamente **{deficit:.1f} dB** adicionales de reducción."
        )

    st.markdown(
        """
        <div style="border:1px solid #eadfc8;border-radius:17px;padding:15px 17px;background:#fffaf2;margin-top:.8rem">
          <div style="font-size:.78rem;font-weight:900;color:#8a5c13">PISTA DE DISEÑO</div>
          <div style="font-size:.84rem;color:#6f5d3f;line-height:1.45;margin-top:.25rem">
            No existe una única solución. Prueba cambiar la altura y la posición de la barrera.
            Busca una geometría que bloquee la línea directa, genere una zona de sombra acústica
            y entregue la reducción necesaria sin sobredimensionar innecesariamente la pantalla.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("role")=="Docente":
        with st.expander("👩‍🏫 Pauta docente · Etapa 4",expanded=False):
            st.markdown(
                f"""
                **Ejercicio:** diseño de barrera acústica  
                **Lp sin barrera:** {lp_without_barrier:.1f} dBA  
                **Objetivo:** ≤ {lp_target:.1f} dBA  
                **Reducción requerida:** {required_reduction:.1f} dB  

                **Configuración actual**
                - hs = {ex_hs:.1f} m
                - hr = {ex_hr:.1f} m
                - hb = {ex_hb:.1f} m
                - dFB = {ex_dfb:.1f} m
                - dBR = {ex_dbr:.1f} m
                - frecuencia = {ex_freq} Hz

                **Resultado**
                - Línea de visión bloqueada: {"Sí" if ex_screens else "No"}
                - Altura LOS en B: {ex_los:.2f} m
                - z = {ex_z:.3f} m
                - Abar = {ex_abar:.1f} dB
                - Lp final = {lp_with_barrier:.1f} dBA
                - Cumple: {"Sí" if complies else "No"}
                """
            )
            st.info(
                "Objetivo docente: que el alumno diseñe una solución y no solo sustituya valores en una ecuación. "
                "Debe relacionar geometría, línea de visión, zona de sombra acústica, diferencia de camino y reducción final."
            )



def _stage5(lab, saved):
    _header(
        5,
        "¿Cómo representar una obra como fuentes de ruido?",
        "Traducir equipos estacionarios, frentes de trabajo y tránsito asociado a la obra a representaciones acústicas coherentes.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d5e6f2;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#fbfdff,#eef6fb);box-shadow:0 8px 20px rgba(31,63,92,.05)">
          <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.1em">DEL EQUIPO REAL AL OBJETO DE CÁLCULO</div>
          <div style="font-size:1.18rem;font-weight:850;color:#17324a;margin:.3rem 0">
            La representación depende del fenómeno que realmente queremos modelar
          </div>
          <div style="color:#5d7183;line-height:1.55">
            En esta etapa utilizaremos <b>fuentes puntuales</b> para maquinaria localizada
            y una <b>fuente lineal vial basada en CNOSSOS</b> para representar el tránsito asociado a la obra
            sobre calles o vías de acceso.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · Dos objetos, dos fenómenos distintos")
    source_cards=[
        (
            "FUENTE PUNTUAL",
            "Maquinaria localizada",
            "Representa un equipo cuya posición de operación puede considerarse definida durante el período evaluado.",
            "Excavadora estacionaria · generador · bomba de hormigón · martillo trabajando en un frente definido",
            "#eef6fb","#176b9b"
        ),
        (
            "FUENTE LINEAL VIAL · CNOSSOS",
            "Tránsito asociado a la obra",
            "Representa vehículos que circulan por una vía. El modelo vial utiliza el flujo y las características del tránsito, no simplemente una máquina moviéndose.",
            "Camiones de retiro de material · mixer · transporte de áridos · vehículos que entran/salen por calles exteriores",
            "#fff7e9","#98651c"
        ),
    ]
    sh='<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:.9rem 0 1rem">'
    for tag,title,desc,examples,bg,color in source_cards:
        sh+=(
            f'<div style="border:1px solid #dce7ef;border-radius:19px;padding:18px;background:{bg};box-shadow:0 5px 14px rgba(40,70,95,.04)">'
            f'<div style="font-size:.7rem;font-weight:900;letter-spacing:.08em;color:{color}">{tag}</div>'
            f'<div style="font-size:1.03rem;font-weight:850;color:#213b50;margin:.3rem 0 .45rem">{title}</div>'
            f'<div style="font-size:.83rem;color:#607586;line-height:1.52">{desc}</div>'
            f'<div style="border-top:1px solid rgba(90,110,125,.15);font-size:.76rem;color:{color};font-weight:800;margin-top:.7rem;padding-top:.55rem">{examples}</div>'
            f'</div>'
        )
    sh+='</div>'
    st.markdown(sh,unsafe_allow_html=True)

    st.warning(
        "No uses la fuente lineal CNOSSOS como una representación genérica de cualquier maquinaria que se desplaza. "
        "Un cargador frontal o una excavadora que cambia de posición dentro de la obra no se transforma automáticamente en una fuente vial."
    )

    st.markdown("### 2 · Obra y tránsito asociado · vista en planta")
    svg=(
        '<div style="border:1px solid #d8e4ec;border-radius:22px;background:#fbfdff;padding:14px 16px;margin:.45rem 0 1rem;box-shadow:0 7px 18px rgba(33,65,90,.05)">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin:2px 0 10px">'
        '<div style="font-size:.73rem;font-weight:900;color:#526a7e;letter-spacing:.08em">PLANTA DIDÁCTICA · OBRA + VÍA EXTERIOR</div>'
        '<div style="font-size:.72rem;font-weight:850;color:#98651c;background:#fff5e6;border-radius:999px;padding:6px 10px">CNOSSOS → tránsito vial</div>'
        '</div>'
        '<svg viewBox="0 0 1000 520" width="100%" style="display:block">'
        '<defs>'
        '<marker id="arrowRoad" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#b87526"/></marker>'
        '<filter id="shadowSmall" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-opacity=".12"/></filter>'
        '</defs>'
        '<rect x="0" y="0" width="1000" height="520" rx="20" fill="#f8fbfd"/>'
        '<rect x="54" y="48" width="690" height="330" rx="22" fill="#eef3f6" stroke="#9fb0bc" stroke-width="3"/>'
        '<text x="76" y="80" font-size="17" font-weight="900" fill="#5e7382">PREDIO DE LA OBRA</text>'
        '<rect x="785" y="85" width="160" height="125" rx="15" fill="#f9eee8" stroke="#c89b7d" stroke-width="3" filter="url(#shadowSmall)"/>'
        '<text x="819" y="120" font-size="17" font-weight="900" fill="#885a3e">VIVIENDA</text>'
        '<text x="809" y="145" font-size="13" fill="#936c55">receptor sensible</text>'
        '<circle cx="785" cy="163" r="8" fill="#b34f4f"/><text x="798" y="168" font-size="13" font-weight="900" fill="#954343">R</text>'

        '<circle cx="215" cy="180" r="31" fill="#3b83b2" filter="url(#shadowSmall)"/>'
        '<text x="195" y="187" font-size="18" font-weight="900" fill="#fff">EX</text>'
        '<rect x="124" y="224" width="183" height="40" rx="10" fill="#ffffff" stroke="#d5e2ea"/>'
        '<text x="143" y="249" font-size="14" font-weight="850" fill="#2f607e">Excavadora · puntual</text>'

        '<rect x="415" y="135" width="62" height="62" rx="12" fill="#4f9a68" filter="url(#shadowSmall)"/>'
        '<text x="437" y="174" font-size="20" font-weight="900" fill="#fff">G</text>'
        '<rect x="374" y="216" width="145" height="40" rx="10" fill="#ffffff" stroke="#d5e2ea"/>'
        '<text x="399" y="241" font-size="14" font-weight="850" fill="#3f7350">Generador</text>'

        '<rect x="300" y="280" width="66" height="52" rx="10" fill="#7c72b8" filter="url(#shadowSmall)"/>'
        '<text x="317" y="313" font-size="17" font-weight="900" fill="#fff">BH</text>'
        '<rect x="251" y="343" width="166" height="40" rx="10" fill="#ffffff" stroke="#d5e2ea"/>'
        '<text x="268" y="368" font-size="14" font-weight="850" fill="#5f568c">Bomba · puntual</text>'

        '<rect x="612" y="260" width="88" height="70" rx="10" fill="#dfe7ec" stroke="#8094a1" stroke-width="2"/>'
        '<text x="628" y="291" font-size="13" font-weight="900" fill="#576d7a">PORTÓN</text>'
        '<text x="625" y="309" font-size="11" fill="#6d7f89">acceso obra</text>'

        '<rect x="0" y="405" width="1000" height="92" fill="#d5d9dc"/>'
        '<line x1="0" y1="451" x2="1000" y2="451" stroke="#ffffff" stroke-width="4" stroke-dasharray="26 20"/>'
        '<text x="28" y="430" font-size="14" font-weight="850" fill="#59646b">CALLE EXTERIOR / RUTA DE ACCESO</text>'
        '<path d="M70 468 L275 468 L470 468 L665 468 L860 468" fill="none" stroke="#b87526" stroke-width="5" marker-end="url(#arrowRoad)"/>'
        '<path d="M860 433 L690 433 L520 433 L350 433" fill="none" stroke="#b87526" stroke-width="5" marker-end="url(#arrowRoad)"/>'
        '<rect x="545" y="432" width="64" height="30" rx="7" fill="#d38c35" filter="url(#shadowSmall)"/>'
        '<rect x="589" y="438" width="24" height="24" rx="4" fill="#b87526"/>'
        '<circle cx="558" cy="466" r="7" fill="#5f5140"/><circle cx="598" cy="466" r="7" fill="#5f5140"/>'
        '<text x="635" y="482" font-size="13" font-weight="850" fill="#96631f">camiones de obra</text>'
        '<path d="M655 405 L655 350" stroke="#b87526" stroke-width="4" stroke-dasharray="8 6" marker-end="url(#arrowRoad)"/>'
        '<text x="670" y="388" font-size="12" font-weight="800" fill="#98651c">entrada / salida</text>'
        '</svg>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:9px">'
        '<div style="border-radius:12px;padding:10px 12px;background:#eef6fb;color:#2b607f;font-size:.77rem"><b>Dentro de la obra:</b> equipos localizados → fuente puntual.</div>'
        '<div style="border-radius:12px;padding:10px 12px;background:#fff7e9;color:#8b5e16;font-size:.77rem"><b>En la calle exterior:</b> flujo de camiones → fuente lineal vial CNOSSOS.</div>'
        '</div>'
        '</div>'
    )
    st.markdown(svg,unsafe_allow_html=True)

    st.markdown("### 3 · ¿Cómo representarías cada situación?")
    st.markdown(
        """
        <div style="border:1px solid #dce6ed;border-radius:18px;padding:15px 17px;background:#fff;margin:.3rem 0 .8rem">
          <div style="font-size:.8rem;font-weight:900;color:#17324a">CRITERIO DE DECISIÓN</div>
          <div style="font-size:.84rem;color:#637788;line-height:1.5;margin-top:.25rem">
            Primero identifica el fenómeno. Si es un <b>equipo operando desde una posición</b>, represéntalo como fuente puntual.
            Si es <b>tránsito vial generado por la obra</b>, represéntalo mediante una fuente lineal vial basada en CNOSSOS.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cases=[
        ("Excavadora trabajando desde un frente definido","Equipo en obra","Fuente puntual",
         "Se representa desde su posición de operación durante el escenario evaluado."),
        ("Generador instalado durante toda la jornada","Equipo estacionario","Fuente puntual",
         "Su emisión se origina desde una ubicación fija."),
        ("Bomba de hormigón estacionada durante un vaciado","Equipo estacionario","Fuente puntual",
         "Durante la actividad permanece localizada respecto de los receptores."),
        ("Camiones que retiran material y circulan por la calle exterior","Tránsito asociado a la obra","Fuente lineal vial · CNOSSOS",
         "Aquí interesa el flujo de vehículos sobre una vía: es el uso natural del objeto lineal CNOSSOS."),
        ("Camiones mixer que llegan repetidamente por una avenida de acceso","Tránsito asociado a la obra","Fuente lineal vial · CNOSSOS",
         "La vía puede representarse mediante el modelo de tránsito, usando sus parámetros de flujo y circulación."),
        ("Cargador frontal que se desplaza entre dos puntos dentro del predio","Maquinaria móvil interna","Varias posiciones puntuales",
         "No conviene tratarlo automáticamente como tráfico CNOSSOS. Puede representarse mediante varias posiciones puntuales representativas o escenarios alternativos de operación, según el objetivo del análisis."),
    ]

    for i,(prompt,kind,expected,why) in enumerate(cases):
        with st.container(border=True):
            head1,head2=st.columns([2.1,1])
            with head1:
                st.markdown(
                    f"<div style='font-size:.72rem;font-weight:900;color:#6b7d89;letter-spacing:.06em'>{kind.upper()}</div>"
                    f"<div style='font-size:.95rem;font-weight:850;color:#263f52;margin-top:.15rem'>{prompt}</div>",
                    unsafe_allow_html=True,
                )
            with head2:
                badge_bg="#eef6fb" if expected.startswith("Fuente puntual") else ("#fff7e9" if "CNOSSOS" in expected else "#f3f3f7")
                badge_color="#176b9b" if expected.startswith("Fuente puntual") else ("#98651c" if "CNOSSOS" in expected else "#666078")
                st.markdown(
                    f"<div style='text-align:center;border-radius:999px;padding:7px 10px;background:{badge_bg};"
                    f"color:{badge_color};font-size:.72rem;font-weight:900'>CASO {i+1}</div>",
                    unsafe_allow_html=True,
                )

            choice=st.radio(
                "Selecciona representación",
                ["Fuente puntual","Fuente lineal vial · CNOSSOS","Varias posiciones puntuales"],
                index=None,
                key=f"c4l1_s5_rep_{i}",
                horizontal=True,
            )
            if choice:
                if choice==expected:
                    st.success(f"Correcto · {why}")
                else:
                    st.warning(f"Revisa · {why}")

    st.markdown("### 4 · ¿Una fuente por máquina o una fuente puntual equivalente?")
    st.markdown(
        """
        <div style="border:1px solid #dce6ed;border-radius:19px;padding:16px 18px;background:#fff;margin:.35rem 0 .8rem">
          <div style="font-size:.78rem;font-weight:900;color:#17324a">DOS ESTRATEGIAS VÁLIDAS DENTRO DEL PREDIO</div>
          <div style="font-size:.84rem;color:#637788;line-height:1.55;margin-top:.3rem">
            Para una etapa de obra puedes modelar <b>cada maquinaria como una fuente puntual independiente</b>
            o, si las fuentes están suficientemente concentradas y el objetivo es una estimación global,
            reemplazarlas por <b>una fuente puntual equivalente</b> obtenida mediante suma energética.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rep_cards=[
        (
            "VARIAS FUENTES PUNTUALES",
            "Mayor detalle espacial",
            "Cada equipo conserva su posición, Lw, altura, tiempo activo y relación geométrica con barreras y receptores.",
            "Úsalo cuando las máquinas están separadas, hay receptores cercanos o necesitas identificar contribuciones individuales.",
            "#eef6fb","#176b9b"
        ),
        (
            "UNA FUENTE PUNTUAL EQUIVALENTE",
            "Simplificación por etapa o frente",
            "Las potencias sonoras de varias máquinas se suman energéticamente y se asignan a una posición representativa del conjunto.",
            "Úsalo para estimaciones globales cuando las fuentes están relativamente agrupadas y la geometría interna no cambia sustancialmente el resultado.",
            "#f3f8f4","#2d7a4a"
        ),
    ]
    rh='<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:.5rem 0 1rem">'
    for title,sub,desc,use,bg,color in rep_cards:
        rh+=(
            f'<div style="border:1px solid #dce6df;border-radius:18px;padding:17px;background:{bg}">'
            f'<div style="font-size:.74rem;font-weight:900;color:{color};letter-spacing:.06em">{title}</div>'
            f'<div style="font-size:.95rem;font-weight:850;color:#314b3d;margin:.3rem 0">{sub}</div>'
            f'<div style="font-size:.81rem;color:#61736a;line-height:1.48">{desc}</div>'
            f'<div style="font-size:.78rem;color:{color};font-weight:800;margin-top:.65rem">{use}</div>'
            f'</div>'
        )
    rh+='</div>'
    st.markdown(rh,unsafe_allow_html=True)

    st.markdown("#### Representación visual")
    eq_svg=(
        '<div style="border:1px solid #d8e4ec;border-radius:22px;background:#fbfdff;padding:18px 20px;margin:.5rem 0 1.1rem;box-shadow:0 8px 20px rgba(33,65,90,.06)">'
        '<div style="font-size:.88rem;font-weight:900;color:#526a7e;letter-spacing:.07em;margin:2px 0 14px">MISMA ETAPA DE OBRA · DOS FORMAS DE REPRESENTARLA</div>'
        '<svg viewBox="0 0 1000 430" width="100%" style="display:block">'
        '<defs>'
        '<marker id="eqArrow" markerWidth="11" markerHeight="11" refX="8" refY="3.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,7 L9,3.5 z" fill="#7f93a1"/></marker>'
        '<filter id="eqShadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-opacity=".12"/></filter>'
        '</defs>'
        '<rect x="0" y="0" width="1000" height="430" rx="20" fill="#f8fbfd"/>'

        '<rect x="28" y="42" width="405" height="315" rx="20" fill="#eef6fb" stroke="#b8d5e7" stroke-width="2.5"/>'
        '<text x="54" y="78" font-size="20" font-weight="900" fill="#176b9b">MODELO DETALLADO</text>'
        '<text x="54" y="104" font-size="15" font-weight="700" fill="#557487">Varias fuentes puntuales independientes</text>'
        '<circle cx="132" cy="190" r="34" fill="#3b83b2" filter="url(#eqShadow)"/><text x="108" y="198" font-size="20" font-weight="900" fill="#fff">EX</text>'
        '<circle cx="275" cy="155" r="34" fill="#4f9a68" filter="url(#eqShadow)"/><text x="260" y="163" font-size="20" font-weight="900" fill="#fff">G</text>'
        '<circle cx="232" cy="285" r="34" fill="#7c72b8" filter="url(#eqShadow)"/><text x="207" y="293" font-size="19" font-weight="900" fill="#fff">BH</text>'
        '<circle cx="360" cy="240" r="34" fill="#d38c35" filter="url(#eqShadow)"/><text x="341" y="248" font-size="19" font-weight="900" fill="#fff">M</text>'
        '<text x="88" y="238" font-size="14" font-weight="850" fill="#2f607e">Excavadora</text>'
        '<text x="244" y="207" font-size="14" font-weight="850" fill="#3f7350">Generador</text>'
        '<text x="194" y="336" font-size="14" font-weight="850" fill="#5f568c">Bomba</text>'
        '<text x="330" y="289" font-size="14" font-weight="850" fill="#96631f">Mixer</text>'
        '<text x="58" y="372" font-size="16" font-weight="700" fill="#5f7585">Cada fuente conserva su posición, Lw y geometría propia.</text>'

        '<line x1="455" y1="210" x2="545" y2="210" stroke="#7f93a1" stroke-width="5" marker-end="url(#eqArrow)"/>'
        '<text x="462" y="180" font-size="16" font-weight="900" fill="#687d8c">SUMA ENERGÉTICA</text>'
        '<text x="458" y="245" font-size="15" font-weight="700" fill="#6f8391">+ simplificación espacial</text>'

        '<rect x="567" y="42" width="405" height="315" rx="20" fill="#f3f9f4" stroke="#bedfc6" stroke-width="2.5"/>'
        '<text x="592" y="78" font-size="20" font-weight="900" fill="#2d7a4a">MODELO SIMPLIFICADO</text>'
        '<text x="592" y="104" font-size="15" font-weight="700" fill="#5f7867">Una fuente puntual equivalente</text>'
        '<circle cx="770" cy="215" r="68" fill="#2d7a4a" filter="url(#eqShadow)"/>'
        '<text x="715" y="209" font-size="22" font-weight="900" fill="#fff">Lw,eq</text>'
        '<text x="738" y="239" font-size="16" font-weight="850" fill="#e9f6ec">puntual</text>'
        '<line x1="770" y1="283" x2="770" y2="320" stroke="#2d7a4a" stroke-width="2.5" stroke-dasharray="6 5"/>'
        '<text x="630" y="342" font-size="16" font-weight="700" fill="#5a7462">Ubicación representativa del frente o etapa</text>'
        '<text x="602" y="367" font-size="16" font-weight="700" fill="#5a7462">Conserva la energía total, pero reduce el detalle espacial.</text>'
        '</svg>'

        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px">'
        '<div style="border:1px solid #cfe0ec;border-radius:16px;padding:15px 16px;background:#eef6fb;color:#2b607f;font-size:.9rem;line-height:1.5"><div style="font-size:.78rem;font-weight:900;letter-spacing:.05em;margin-bottom:.3rem">MODELO DETALLADO</div><b>Útil cuando necesitas:</b><br>• estudiar contribuciones individuales<br>• conservar distancias distintas<br>• evaluar barreras por equipo</div>'
        '<div style="border:1px solid #d4e7d8;border-radius:16px;padding:15px 16px;background:#f3f9f4;color:#406a4c;font-size:.9rem;line-height:1.5"><div style="font-size:.78rem;font-weight:900;letter-spacing:.05em;margin-bottom:.3rem">MODELO EQUIVALENTE</div><b>Útil cuando necesitas:</b><br>• representar globalmente una etapa<br>• simplificar un frente concentrado<br>• trabajar con una posición representativa</div>'
        '</div>'
        '</div>'
    )
    st.markdown(eq_svg,unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### Suma energética para construir la fuente equivalente")
        st.latex(r"L_{W,eq}=10\log_{10}\left(\sum_i 10^{L_{W,i}/10}\right)")
        st.markdown(
            "No se suman los Lw aritméticamente. Primero se suma la energía acústica de cada maquinaria y "
            "el resultado se expresa nuevamente en decibeles."
        )

    phases={
        "Excavación":[("Excavadora",105.0),("Retroexcavadora",101.0),("Camión",101.0)],
        "Obra gruesa":[("Bomba de hormigón",104.0),("Mixer",101.0),("Vibrador",97.0)],
        "Terminaciones":[("Sierra de corte",106.0),("Taladro",98.0),("Generador",100.0)],
    }
    phase=st.selectbox("Etapa de obra",list(phases.keys()),key="c4l1_s5_phase_eq")
    machines=phases[phase]
    lw_eq=10*math.log10(sum(10**(lw/10) for _,lw in machines))

    cols=st.columns(len(machines)+1)
    for col,(name,lw_i) in zip(cols,machines):
        col.metric(name,f"{lw_i:.0f} dB")
    cols[-1].metric("Lw equivalente",f"{lw_eq:.1f} dB")

    st.markdown(
        f"Para esta simplificación de **{phase.lower()}**, las {len(machines)} máquinas pueden representarse "
        f"por una fuente puntual equivalente de **Lw = {lw_eq:.1f} dB**, ubicada en una posición representativa "
        "del frente o zona de trabajo."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin:.75rem 0 1rem">
          <div style="border:1px solid #d7e5ee;border-radius:16px;padding:14px;background:#f7fbfe;text-align:center">
            <div style="font-size:.72rem;font-weight:900;color:#176b9b">MODELO DETALLADO</div>
            <div style="font-size:.82rem;color:#607586;margin-top:.35rem">● Excavadora &nbsp; ● Camión &nbsp; ● Generador</div>
            <div style="font-size:.75rem;color:#788894;margin-top:.3rem">posiciones y contribuciones separadas</div>
          </div>
          <div style="font-size:1.45rem;color:#8195a3;font-weight:900">→</div>
          <div style="border:1px solid #d7e8dc;border-radius:16px;padding:14px;background:#f5fbf6;text-align:center">
            <div style="font-size:.72rem;font-weight:900;color:#2d7a4a">MODELO SIMPLIFICADO</div>
            <div style="font-size:.9rem;color:#496657;font-weight:850;margin-top:.35rem">● Lw equivalente</div>
            <div style="font-size:.75rem;color:#788b7e;margin-top:.3rem">una posición representativa del frente</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "La fuente puntual equivalente es una aproximación espacial. No conviene usarla si las máquinas están muy separadas, "
        "si una barrera afecta solo a algunas fuentes, si existen receptores muy cercanos o si necesitas conocer cuál equipo domina. "
        "En esos casos mantén las fuentes puntuales independientes."
    )

    st.markdown("### 5 · Cuándo sí usar la fuente lineal CNOSSOS")

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.4rem 0 .8rem">
          <div style="border:1px solid #d6eadc;border-radius:17px;padding:15px;background:#f3fbf5">
            <div style="font-size:.75rem;font-weight:900;color:#2d7a4a">SÍ TIENE SENTIDO</div>
            <div style="font-size:.83rem;color:#597064;line-height:1.5;margin-top:.35rem">
              Viajes de camiones por calles exteriores, acceso a botadero, retiro de escombros,
              transporte de áridos, mixer y otros flujos viales generados por la obra.
            </div>
          </div>
          <div style="border:1px solid #ead9d1;border-radius:17px;padding:15px;background:#fff8f4">
            <div style="font-size:.75rem;font-weight:900;color:#a05b3a">NO AUTOMÁTICAMENTE</div>
            <div style="font-size:.83rem;color:#75645b;line-height:1.5;margin-top:.35rem">
              Excavadora, cargador frontal o maquinaria que simplemente cambia de posición dentro del predio.
              Ese movimiento no debe confundirse con un modelo de tráfico vial.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "Idea de cierre: **puntual = maquinaria localizada**; una etapa completa puede representarse con varias puntuales "
        "o, cuando sea técnicamente razonable, con una **puntual equivalente**. **Lineal CNOSSOS = tránsito vial asociado a la obra**."
    )


def _stage6(lab, saved):
    _header(
        6,
        "Diseño y control del ruido en una obra",
        "Seleccionar controles técnicamente aplicables según el tipo de fuente, su operación y la geometría respecto del receptor.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d7e5ef;border-radius:24px;padding:22px 24px;
        background:linear-gradient(135deg,#fbfdff,#f1f7fb);box-shadow:0 9px 24px rgba(30,65,92,.06);margin-bottom:1rem">
          <div style="display:inline-block;font-size:.78rem;font-weight:900;color:#0b6ea8;letter-spacing:.1em;
          background:#eaf5fb;border-radius:999px;padding:6px 10px">CONTROL ACÚSTICO APLICADO</div>
          <div style="font-size:1.36rem;font-weight:900;color:#17324a;margin:.55rem 0 .5rem">
            La medida correcta depende de cómo funciona realmente la fuente
          </div>
          <div style="color:#5d7183;line-height:1.6;font-size:.92rem">
            No sirve proponer un encierro para una máquina que debe desplazarse libremente, ni reubicar un equipo
            que obligatoriamente debe trabajar junto al receptor. El diseño debe ser <b>acústicamente eficaz</b>
            y al mismo tiempo <b>operacionalmente viable</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · Controles que utilizaremos")
    controls=[
        (
            "SILENCIADOR",
            "Conductos, escapes o ventilación",
            "Introduce una pérdida de inserción en la trayectoria de descarga. Su eficacia puede variar con la frecuencia.",
            "Ej.: escape de generador o ventilación forzada.",
            "#eef6fb","#176b9b"
        ),
        (
            "ENCIERRO",
            "Fuente fija que puede quedar rodeada",
            "Reduce transmisión directa mediante cerramientos. Las puertas, juntas, ventilación y penetraciones condicionan el desempeño real.",
            "Ej.: generador o equipo estacionario.",
            "#f2f8f4","#2d7a4a"
        ),
        (
            "SEMIENCIERRO",
            "Fuente que necesita una cara abierta",
            "Rodea parcialmente la fuente. La superficie abierta y su orientación respecto del receptor pasan a ser críticas.",
            "Ej.: sierra de corte fija con acceso del operador.",
            "#fff8e9","#98651c"
        ),
        (
            "ENCIERRO + SILENCIADOR",
            "Fuente fija con ventilación o escape relevante",
            "Combina transmisión por cerramiento y control de las vías de ventilación/escape.",
            "Ej.: generador estacionario de operación prolongada.",
            "#f5f2fb","#65549a"
        ),
        (
            "BARRERA",
            "Control sobre la trayectoria",
            "Interrumpe la línea de visión y genera difracción. Su eficacia depende de altura, posición y geometría fuente–barrera–receptor.",
            "Ej.: maquinaria que debe trabajar cerca del deslinde.",
            "#fff2ed","#a05b3a"
        ),
        (
            "REDUCCIÓN DIRECTA DOCUMENTADA",
            "Representación de un control conocido",
            "No es una medida física en sí misma. Se usa cuando ya existe una reducción medida, declarada o calculada que debe incorporarse al modelo.",
            "Ej.: IL/TL conocido de un tratamiento específico.",
            "#f3f5f7","#596b78"
        ),
    ]
    st.caption(
        "Una ficha por medida física: reconoce el mecanismo, su aplicación y sus restricciones."
    )
    image_names = (
        "silenciador.png",
        "encierro.png",
        "semiencierro.png",
        "encierro_silenciador.png",
        "barrera.png",
    )
    for row_start in range(0, len(image_names), 2):
        columns = st.columns(2)
        for col, index in zip(columns, range(row_start, min(row_start + 2, len(image_names)))):
            title, use, desc, example, bg, color = controls[index]
            with col:
                with st.container(border=True):
                    image_path = PROJECT_ROOT / "assets" / "controles" / image_names[index]
                    if image_path.is_file():
                        st.image(str(image_path), use_container_width=True)
                        st.caption(f"{title.capitalize()} · referencia visual didáctica.")
                    else:
                        st.markdown(
                            '<div role="img" aria-label="Render en preparación" '
                            'style="min-height:190px;border:1px dashed #c8d7e5;border-radius:12px;'
                            'display:flex;align-items:center;justify-content:center;'
                            f'background:{bg};color:{color};font-size:.88rem">'
                            'Render individual en preparación</div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown(
                        f'<div style="font-size:.75rem;font-weight:900;letter-spacing:.07em;color:{color};margin-top:.5rem">{title}</div>'
                        f'<div style="font-size:1.02rem;font-weight:850;color:#334c5f;margin:.32rem 0">{use}</div>'
                        f'<div style="font-size:.86rem;color:#657684;line-height:1.55">{desc}</div>'
                        f'<div style="border-top:1px solid rgba(90,110,125,.13);margin-top:.65rem;padding-top:.5rem;font-size:.8rem;color:{color};font-weight:800">{example}</div>',
                        unsafe_allow_html=True,
                    )

    title, use, desc, example, bg, color = controls[-1]
    with st.container(border=True):
        st.markdown(f"**{title}** · {use}")
        st.markdown(desc)
        st.caption(example)

    st.info(
        "Además de estos controles físicos, la planificación sigue siendo válida: evitar simultaneidad innecesaria, "
        "elegir ubicaciones favorables cuando la operación lo permita y orientar aberturas o escapes lejos del receptor."
    )

    st.markdown("### 2 · Caso de diseño · cuatro fuentes con restricciones reales")
    st.markdown(
        "En el plano existe una vivienda sensible al costado oriental. Cada fuente tiene una condición operacional distinta. "
        "El alumno debe elegir una solución que pueda aplicarse realmente en obra."
    )

    work_svg=(
        '<div style="border:1px solid #d8e4ec;border-radius:24px;background:#fbfdff;padding:18px 20px;margin:.55rem 0 1.1rem;box-shadow:0 10px 24px rgba(33,65,90,.06)">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px">'
        '<div><div style="font-size:.82rem;font-weight:900;color:#526a7e;letter-spacing:.08em">PLANTA DE ANÁLISIS</div>'
        '<div style="font-size:.85rem;color:#738590;margin-top:.2rem">La restricción operacional es parte del problema.</div></div>'
        '<div style="font-size:.78rem;font-weight:900;color:#8b5b3d;background:#fff3eb;border:1px solid #edd4c5;border-radius:999px;padding:7px 12px">R · receptor sensible</div>'
        '</div>'
        '<svg viewBox="0 0 1000 545" width="100%" style="display:block">'
        '<defs><filter id="s6Shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-opacity=".13"/></filter></defs>'
        '<rect x="0" y="0" width="1000" height="545" rx="22" fill="#f8fbfd"/>'
        '<rect x="48" y="54" width="714" height="420" rx="24" fill="#eef3f6" stroke="#9fb0bc" stroke-width="3"/>'
        '<text x="75" y="90" font-size="20" font-weight="900" fill="#5e7382">PREDIO DE LA OBRA</text>'
        '<text x="75" y="116" font-size="13" font-weight="700" fill="#7b8c97">Selecciona controles compatibles con la operación de cada fuente</text>'

        '<rect x="805" y="130" width="150" height="172" rx="16" fill="#f9eee8" stroke="#c89b7d" stroke-width="3" filter="url(#s6Shadow)"/>'
        '<rect x="825" y="154" width="110" height="55" rx="8" fill="#fff8f3" stroke="#e4c8b7"/>'
        '<text x="839" y="185" font-size="18" font-weight="900" fill="#885a3e">VIVIENDA</text>'
        '<text x="826" y="234" font-size="13" font-weight="700" fill="#936c55">receptor residencial</text>'
        '<circle cx="805" cy="260" r="12" fill="#b34f4f"/><text x="825" y="266" font-size="16" font-weight="900" fill="#954343">R</text>'

        '<circle cx="165" cy="180" r="40" fill="#4f9a68" filter="url(#s6Shadow)"/>'
        '<circle cx="136" cy="151" r="14" fill="#fff" stroke="#4f9a68" stroke-width="3"/><text x="131" y="157" font-size="13" font-weight="900" fill="#3f7350">1</text>'
        '<text x="149" y="188" font-size="22" font-weight="900" fill="#fff">G</text>'
        '<rect x="91" y="234" width="150" height="45" rx="11" fill="#fff" stroke="#d7e3ea"/>'
        '<text x="117" y="261" font-size="15" font-weight="900" fill="#3f7350">Generador</text>'

        '<circle cx="570" cy="160" r="40" fill="#d65f5f" filter="url(#s6Shadow)"/>'
        '<circle cx="541" cy="131" r="14" fill="#fff" stroke="#d65f5f" stroke-width="3"/><text x="536" y="137" font-size="13" font-weight="900" fill="#9e4545">2</text>'
        '<text x="546" y="168" font-size="21" font-weight="900" fill="#fff">MH</text>'
        '<rect x="487" y="214" width="168" height="45" rx="11" fill="#fff" stroke="#d7e3ea"/>'
        '<text x="506" y="241" font-size="15" font-weight="900" fill="#9e4545">Martillo hidráulico</text>'

        '<circle cx="660" cy="365" r="40" fill="#3b83b2" filter="url(#s6Shadow)"/>'
        '<circle cx="631" cy="336" r="14" fill="#fff" stroke="#3b83b2" stroke-width="3"/><text x="626" y="342" font-size="13" font-weight="900" fill="#2f607e">3</text>'
        '<text x="636" y="373" font-size="21" font-weight="900" fill="#fff">EX</text>'
        '<rect x="584" y="419" width="155" height="45" rx="11" fill="#fff" stroke="#d7e3ea"/>'
        '<text x="608" y="446" font-size="15" font-weight="900" fill="#2f607e">Excavadora</text>'

        '<circle cx="410" cy="365" r="40" fill="#7c72b8" filter="url(#s6Shadow)"/>'
        '<circle cx="381" cy="336" r="14" fill="#fff" stroke="#7c72b8" stroke-width="3"/><text x="376" y="342" font-size="13" font-weight="900" fill="#5f568c">4</text>'
        '<text x="384" y="373" font-size="20" font-weight="900" fill="#fff">SC</text>'
        '<rect x="330" y="419" width="163" height="45" rx="11" fill="#fff" stroke="#d7e3ea"/>'
        '<text x="355" y="446" font-size="15" font-weight="900" fill="#5f568c">Sierra de corte</text>'

        '<line x1="165" y1="180" x2="805" y2="260" stroke="#5e9a70" stroke-width="2.5" stroke-dasharray="10 8" opacity=".45"/>'
        '<line x1="570" y1="160" x2="805" y2="260" stroke="#d65f5f" stroke-width="3.5" stroke-dasharray="10 8" opacity=".72"/>'
        '<line x1="660" y1="365" x2="805" y2="260" stroke="#3b83b2" stroke-width="3.3" stroke-dasharray="10 8" opacity=".67"/>'
        '<line x1="410" y1="365" x2="805" y2="260" stroke="#7c72b8" stroke-width="2.8" stroke-dasharray="10 8" opacity=".6"/>'
        '</svg>'
        '<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:11px;margin-top:12px">'
        '<div style="border:1px solid #d7eadc;border-radius:14px;padding:12px;background:#eff8f1;color:#3f7350;font-size:.84rem;line-height:1.42"><b>1 · Generador</b><br><span style="color:#62776a">fijo · funciona gran parte de la jornada · posee escape/ventilación</span></div>'
        '<div style="border:1px solid #f0d7d7;border-radius:14px;padding:12px;background:#fff1f1;color:#934747;font-size:.84rem;line-height:1.42"><b>2 · Martillo</b><br><span style="color:#806565">debe trabajar en ese punto · alta emisión · próximo a R</span></div>'
        '<div style="border:1px solid #cfe0ec;border-radius:14px;padding:12px;background:#eef6fb;color:#2f607e;font-size:.84rem;line-height:1.42"><b>3 · Excavadora</b><br><span style="color:#637887">debe excavar junto al deslinde · no puede encerrarse</span></div>'
        '<div style="border:1px solid #ddd8ef;border-radius:14px;padding:12px;background:#f5f2fb;color:#5f568c;font-size:.84rem;line-height:1.42"><b>4 · Sierra</b><br><span style="color:#726c82">fija durante el corte · necesita acceso frontal del operador</span></div>'
        '</div>'
        '</div>'
    )
    st.markdown(work_svg,unsafe_allow_html=True)

    st.markdown("### 3 · Diseña la estrategia de control")
    st.markdown(
        """
        <div style="border:1px solid #d4e3ed;border-radius:20px;padding:22px 24px;
        background:linear-gradient(120deg,#f7fbfd,#eef5fa);margin:.4rem 0 1.2rem">
          <div style="font-size:.72rem;font-weight:800;letter-spacing:.12em;color:#176b9b">TU TURNO · 4 DECISIONES</div>
          <div style="font-size:1.2rem;font-weight:850;color:#17324a;margin:.4rem 0 .55rem">Una medida viable para cada fuente</div>
          <div style="font-size:.9rem;color:#526b7c;line-height:1.6">
            Revisa la condición operacional, elige una medida y comprueba su aplicabilidad.
            Usa el plano de la parte 2 para considerar la posición de la vivienda.
          </div>
          <div style="border-top:1px solid #d4e3ed;padding-top:12px;margin-top:14px;font-size:.82rem;color:#456275">
            <b>01</b> · Lee la restricción &nbsp;&nbsp; <b>02</b> · Elige el control &nbsp;&nbsp; <b>03</b> · Revisa el criterio
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    control_cases=[
        (
            "Generador",
            "Fijo · escape y ventilación · operación prolongada",
            ["Encierro + silenciador","Solo barrera","Semiencierro abierto hacia el receptor","Reubicarlo obligatoriamente"],
            "Encierro + silenciador",
            "Es una fuente fija y compatible con un cerramiento. El silenciador permite controlar además las vías de escape o ventilación, que de otro modo pueden limitar el desempeño del encierro.",
            "#4f9a68"
        ),
        (
            "Martillo hidráulico",
            "Alta emisión · debe operar en esa posición",
            ["Barrera próxima a la fuente","Encierro completo","Silenciador de escape","Semiencierro fijo alrededor del equipo"],
            "Barrera próxima a la fuente",
            "Como el frente no puede reubicarse y el equipo necesita libertad de movimiento, una pantalla temporal correctamente dimensionada es una medida de trayectoria más viable.",
            "#d65f5f"
        ),
        (
            "Excavadora",
            "Debe excavar junto al deslinde · maquinaria móvil",
            ["Barrera entre frente y receptor","Encierro completo","Semiencierro rígido","Moverla lejos del receptor"],
            "Barrera entre frente y receptor",
            "La ubicación viene impuesta por la excavación y la máquina debe moverse. Una barrera temporal puede actuar sobre la trayectoria sin impedir la operación; su eficacia dependerá de la geometría.",
            "#3b83b2"
        ),
        (
            "Sierra de corte",
            "Fuente fija · requiere acceso frontal",
            ["Semiencierro con abertura opuesta al receptor","Encierro hermético sin acceso","Solo aumentar horario","Barrera lejana sin cambiar orientación"],
            "Semiencierro con abertura opuesta al receptor",
            "El semiencierro permite mantener acceso operativo y orientar la cara abierta en sentido contrario al receptor, reduciendo la propagación directa.",
            "#7c72b8"
        ),
    ]

    correct_count=0
    for i,(name,kind,options,expected,why,color) in enumerate(control_cases):
        with st.container(border=True):
            context, decision = st.columns([1, 1.65], gap="large")
            with context:
                st.markdown(
                    f'<div style="border-left:4px solid {color};padding:4px 0 8px 16px;margin:6px 0 16px">'
                    f'<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:{color}">FUENTE 0{i+1}</div>'
                    f'<div style="font-size:1.35rem;font-weight:850;color:#17324a;line-height:1.2;margin:.5rem 0">{name}</div>'
                    '<div style="font-size:.76rem;font-weight:800;color:#627989;margin-top:1rem">CONDICIÓN OPERACIONAL</div>'
                    f'<div style="font-size:.92rem;color:#455f72;line-height:1.6;margin-top:.35rem">{kind}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.caption("El control debe permitir que la máquina siga realizando su trabajo.")

            with decision:
                st.markdown("**¿Qué medida aplicarías?**")
                choice=st.radio(
                    f"Medida principal para {name}",
                    options,
                    index=None,
                    horizontal=False,
                    label_visibility="collapsed",
                    key=f"c4l1_s6_control_{i}",
                )
                if choice:
                    if choice==expected:
                        correct_count+=1
                        st.success(f"Medida compatible con la operación. {why}")
                    else:
                        st.warning(f"Revisa la aplicabilidad. {why}")
                else:
                    st.caption("Selecciona una opción para ver el criterio técnico.")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    st.markdown("### 4 · ¿Dónde entra la reducción directa?")
    st.markdown(
        "**Reducción directa** es la forma de incorporar un desempeño conocido al cálculo. "
        "El control físico sigue siendo el tratamiento realizado sobre el equipo."
    )
    with st.container(border=True):
        st.markdown("#### Caso real documentado · mesa vibratoria para moldes de hormigón")
        visual, explanation = st.columns([1.15, 1])
        with visual:
            example_image = PROJECT_ROOT / "assets" / "controles" / "reduccion_directa_mesa_vibratoria.png"
            if example_image.is_file():
                st.image(str(example_image), use_container_width=True)
            else:
                st.info("Render del tratamiento en preparación.")
            st.caption(
                "Render ilustrativo generado: muestra una mesa con tratamiento estructural. "
                "No es una fotografía ni una reconstrucción exacta del equipo del caso."
            )
        with explanation:
            st.markdown(
                "**Situación:** durante las pruebas de un vibrador para fabricar productos de hormigón, "
                "el ruido se aproximaba a 100 dB.\n\n"
                "**Diagnóstico:** el bastidor radiaba vibraciones de alta frecuencia que no contribuían "
                "a compactar el hormigón.\n\n"
                "**Tratamiento:** se modificó la mesa para cambiar sus frecuencias naturales y amortiguar "
                "esa vibración, conservando la vibración útil para la compactación."
            )
            st.metric("Reducción publicada para este caso", "15 dB")
            st.markdown(
                "[Fuente: HSE · Concrete vibrator]"
                "(https://www.hse.gov.uk/noise/casestudies/concretevibrator.htm)"
            )
            st.caption("Información del caso: Redland Roof Tiles Ltd. e Industrial Noise and Vibration Centre Ltd.")

        st.markdown("#### Cómo representa este caso la reducción directa")
        st.markdown(
            "El **tratamiento estructural** es la medida física; los **15 dB documentados** describen "
            "su resultado en el caso estudiado. Si un modelo no representa ese mecanismo, puede recurrir "
            "a una reducción directa respaldada por un ensayo aplicable al equipo y a su condición de operación."
        )
        st.info(
            "HSE publica una reducción de ruido, pero la ficha no aporta un Lw antes/después, "
            "una distancia de medida ni un descriptor temporal. Por eso, los 15 dB no deben trasladarse "
            "automáticamente a la potencia sonora de otra máquina o al nivel de una vivienda."
        )
        st.markdown("#### Ejercicio de lectura del dato")
        st.latex(r"\Delta L=L_{\mathrm{antes}}-L_{\mathrm{después}}=15\ \mathrm{dB}")
        st.markdown(
            "**Ejemplo aritmético didáctico:** si se midieran 100 dB antes y 85 dB después, "
            "con el mismo descriptor, posición y operación, la diferencia sería 15 dB. "
            "Los 85 dB son un valor ilustrativo, no un nivel final publicado por HSE."
        )
        st.markdown(
            "**Qué documentar para usar una reducción directa:** equipo y tratamiento, fuente del dato, "
            "descriptor acústico, posición de medida, operación y límites de aplicación. "
            "No sumes nuevamente la misma reducción si el tratamiento ya está representado en el modelo."
        )


    st.markdown(
        """
        <div style="border:1px solid #d7e5ef;border-radius:20px;padding:16px 18px;
        background:linear-gradient(135deg,#f9fcfe,#f3f8fb);margin:.9rem 0 .3rem">
          <div style="font-size:.78rem;font-weight:900;color:#17324a;letter-spacing:.06em">IDEA DE CIERRE</div>
          <div style="font-size:.88rem;color:#607586;line-height:1.55;margin-top:.35rem">
            El control no se selecciona por una lista fija de “dB de reducción”. Primero se identifica
            <b>qué mecanismo puede aplicarse físicamente</b>; después se cuantifica su desempeño y se incorpora al cálculo.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _s7_level(energy):
    """Return a level from relative mean-square pressure; zero energy has no finite dB value."""
    return 10 * math.log10(energy) if energy > 0 else None


def _s7_schedule(sources, period=60, background=None):
    """Integrate independent constant-level contributions over exact activity intervals."""
    boundaries = sorted({0, period, *[t for source in sources for t in source["window"]]})
    segments = []
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        active = [source for source in sources if source["window"][0] <= start < source["window"][1]]
        energy = sum(10 ** (source["level"] / 10) for source in active)
        if background is not None:
            energy += 10 ** (background / 10)
        segments.append({
            "start": start, "end": end, "energy": energy,
            "level": _s7_level(energy), "active": [source["name"] for source in active],
        })
    mean_energy = sum((s["end"] - s["start"]) * s["energy"] for s in segments) / period
    return segments, _s7_level(mean_energy)


def _s7_timeline(sources, period=60):
    """Responsive SVG with a text equivalent in the source controls and interval table."""
    height = 68 + 54 * len(sources)
    svg = (
        f'<svg viewBox="0 0 840 {height}" width="100%" role="img" '
        'aria-label="Cronograma de actividad de las fuentes; las barras indican minutos activos">'
        '<rect width="840" height="100%" rx="16" fill="#f6f9fc"/>'
    )
    for minute in range(0, period + 1, 10):
        x = 170 + 640 * minute / period
        svg += (
            f'<line x1="{x}" x2="{x}" y1="35" y2="{height-20}" stroke="#dce6ee"/>'
            f'<text x="{x}" y="23" text-anchor="middle" font-size="12" fill="#526b7d">{minute} min</text>'
        )
    for i, source in enumerate(sources):
        y = 48 + 54 * i
        start, end = source["window"]
        x = 170 + 640 * start / period
        width = 640 * (end - start) / period
        svg += (
            f'<text x="14" y="{y+19}" font-size="14" font-weight="700" fill="#24445c">{source["name"]}</text>'
            f'<rect x="170" y="{y}" width="640" height="30" rx="7" fill="#e8eff5"/>'
        )
        if width > 0:
            svg += (
                f'<rect x="{x}" y="{y}" width="{width}" height="30" rx="7" fill="{source["color"]}">'
                f'<title>{source["name"]}: {start}–{end} min; {source["level"]:.1f} dB(A) durante operación</title></rect>'
            )
    st.markdown(svg + "</svg>", unsafe_allow_html=True)


def _s7_section(number, title, purpose):
    st.markdown(f"### {number} · {title}")
    st.caption(purpose)


def _stage7(lab, saved):
    _header(
        7,
        "Tiempo, simultaneidad y energía acústica",
        "Explorar cómo los ciclos de trabajo cambian el aporte de cada fuente y cómo el cronograma modifica los niveles durante una hora de obra.",
    )
    st.markdown(
        """
        <div style="border:1px solid #cfe0ed;border-radius:24px;padding:24px;
        background:linear-gradient(125deg,#f8fcff,#eaf3fa);margin-bottom:18px">
          <div style="font-size:.73rem;font-weight:850;letter-spacing:.12em;color:#176b9b">LABORATORIO INTERACTIVO · UN RECEPTOR · 60 MINUTOS</div>
          <div style="font-size:1.5rem;font-weight:850;color:#17324a;margin:.6rem 0">
            ¿Cuánto aporta una máquina que trabaja solo parte de la hora?
          </div>
          <div style="color:#526d80;line-height:1.65">
            Cambia tiempos y niveles, combina fuentes y organiza sus horarios.
            Observa por separado el promedio energético del período y los niveles de cada intervalo.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    route = st.columns(3)
    for col, title, description in zip(
        route,
        ["01 · Comprende", "02 · Experimenta", "03 · Resuelve"],
        ["Identifica las entradas y calcula el aporte equivalente.", "Compara energía y coincidencias de operación.", "Justifica el resultado de un caso de obra."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(description)

    _s7_section(1, "Identifica las entradas del cálculo", "Fija el receptor y el período; después identifica el nivel operativo y el tiempo activo de cada máquina.")
    concepts = [
        ("01", "Nivel durante operación", "L<sub>operación,i</sub>", "Nivel equivalente de la máquina i sola en el receptor mientras trabaja, separado del fondo. Se expresa en dB(A).", "#176b9b", "#eef7fc"),
        ("02", "Tiempo activo", "t<sub>i</sub>", "Duración total de la actividad dentro del período. Puede reunir varios ciclos si todos tienen el mismo nivel operativo.", "#65549a", "#f5f2fb"),
        ("03", "Período de evaluación", "T = 60 min", "Duración común del cálculo, que incluye actividad y parada. En esta etapa T es una hora; tᵢ y T usan la misma unidad.", "#2d7a4a", "#eff8f2"),
    ]
    for col, (number, title, symbol, description, color, bg) in zip(st.columns(3, gap="medium"), concepts):
        with col:
            st.markdown(
                f'<div style="border:1px solid #dce7ef;border-top:4px solid {color};border-radius:16px;'
                f'padding:20px;background:{bg};min-height:225px;box-sizing:border-box">'
                f'<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:{color}">ENTRADA {number}</div>'
                f'<div style="font-size:1.05rem;font-weight:850;color:#17324a;margin:.6rem 0">{title}</div>'
                f'<div style="font-size:1.65rem;font-weight:850;color:{color};margin:.7rem 0">{symbol}</div>'
                f'<div style="font-size:.88rem;line-height:1.65;color:#526b7c">{description}</div></div>',
                unsafe_allow_html=True,
            )
    st.info(
        "Todos los niveles se refieren al mismo receptor. Usamos niveles de presión sonora equivalentes "
        "ponderados A; no mezcles estas entradas con Lw o LAmax. La máquina conserva su nivel durante "
        "operación aunque trabaje menos minutos."
    )
    st.caption(
        "Este modelo considera la máquina apagada durante la parada. Si queda en ralentí o mantiene "
        "otra emisión, esa condición requiere su propio nivel y duración; no puede tratarse como aporte nulo. "
        "El período de una hora es una elección didáctica, no un criterio automático de evaluación normativa."
    )

    _s7_section(2, "Calcula el aporte equivalente del período", "La corrección temporal es un paso del cálculo; el aporte equivalente es su resultado. Aquí el período es una hora.")
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">UN SOLO MÉTODO · DOS PASOS</div>'
            '<div style="font-size:1.2rem;font-weight:850;color:#17324a;margin:.5rem 0">Del nivel operativo al aporte de toda la hora</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Qué queremos obtener:** el aporte equivalente del período, LAeq,T,i. "
            "Es el nivel constante que, mantenido durante todo T, representaría la misma energía "
            "que aporta la máquina en sus minutos activos. «Aporte de la hora» es el nombre abreviado "
            "cuando T = 60 min, no una magnitud diferente."
        )
        st.markdown("**Paso 1 · Calcula la corrección temporal**")
        st.latex(r"\Delta L_{t,i}=10\log_{10}(t_i/T)")
        st.markdown(
            "La corrección temporal ΔLt,i es un ajuste en **dB** por la fracción activa tᵢ/T. "
            "Vale 0 dB si la máquina trabaja todo T y es negativa si trabaja solo parte de T. "
            "Ajusta el promedio del período; no reduce físicamente la emisión durante operación."
        )
        st.markdown("**Paso 2 · Suma ese ajuste al nivel durante operación**")
        st.latex(r"L_{Aeq,T,i}=L_{\mathrm{operación},i}+\Delta L_{t,i}")
        st.markdown(
            "El resultado es el aporte equivalente de esa máquina, en **dB(A)**. "
            "La expresión combinada es la misma relación entre tiempo y nivel, no un segundo cálculo:"
        )
        st.latex(r"L_{Aeq,T,i}=L_{\mathrm{operación},i}+10\log_{10}(t_i/T)")
        parameter_definitions = [
            ("L<sub>Aeq,T,i</sub>", "Aporte de la máquina i al período completo", "Nivel equivalente referido a toda la hora, incluidos los minutos sin actividad.", "dB(A)"),
            ("L<sub>operación,i</sub>", "Nivel de la máquina i durante operación", "Aporte de la máquina sola en el receptor durante su tiempo activo, separado del fondo.", "dB(A)"),
            ("t<sub>i</sub>", "Tiempo activo de la máquina i", "Suma de los minutos en que funciona dentro del período de evaluación.", "min"),
            ("T", "Período total de evaluación", "Duración común sobre la que se reparte la energía. Aquí T = 60 min.", "min"),
        ]
        st.markdown("**Qué significa cada parámetro**")
        parameter_columns = st.columns(2, gap="medium")
        for index, (symbol, title, description, unit) in enumerate(parameter_definitions):
            with parameter_columns[index % 2]:
                st.markdown(
                    '<div style="border:1px solid #dce8f1;border-radius:12px;padding:15px 16px;'
                    'background:#f7fafc;margin-bottom:10px">'
                    '<div style="display:flex;justify-content:space-between;gap:10px;align-items:center">'
                    f'<span style="font-size:1.15rem;font-weight:850;color:#176b9b">{symbol}</span>'
                    f'<span style="font-size:.75rem;color:#526b7c;background:#e8eff5;border-radius:7px;padding:4px 8px">{unit}</span>'
                    '</div>'
                    f'<div style="font-size:.86rem;font-weight:800;color:#24445c;margin:.6rem 0 .3rem">{title}</div>'
                    f'<div style="font-size:.82rem;color:#627989;line-height:1.6">{description}</div></div>',
                    unsafe_allow_html=True,
                )
        st.caption(
            "i identifica la máquina; A indica ponderación A; eq indica nivel equivalente. "
            "tᵢ/T es la fracción activa, sin unidades: usa la misma unidad para ambos tiempos. "
            "El término 10 log10(tᵢ/T) es la corrección temporal ΔLt,i, expresada en dB. "
            "La ecuación con logaritmo se aplica para 0 < tᵢ ≤ T; si tᵢ = 0, no hay aporte de la máquina."
        )

        st.markdown("**Ejemplo guiado · 80 dB(A) durante 15 min de una hora**")
        st.latex(r"\frac{t_i}{T}=\frac{15}{60}=0{,}25\qquad\Delta L_{t,i}=10\log_{10}(0{,}25)=-6{,}02\ \mathrm{dB}")
        st.latex(r"L_{Aeq,60\,\mathrm{min},i}=80+(-6{,}02)=73{,}98\ \mathrm{dB(A)}")
        st.markdown(
            '<div style="border-left:3px solid #287bb0;border-radius:0 12px 12px 0;'
            'padding:14px 16px;background:#eef6fc;color:#456275;font-size:.88rem;line-height:1.65">'
            '<b>Interpretación:</b> durante sus 15 min de actividad, la máquina sigue aportando 80 dB(A). '
            'Su aporte repartido sobre la hora equivale a 73,98 dB(A). '
            'No se volvió más silenciosa: cambió el período sobre el que expresamos su energía.</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Supuestos: nivel constante durante operación, sin aporte de la máquina durante la parada "
            "y nivel de la máquina separado del fondo. Con 0 min activos no hay aporte; no se calcula log10(0). "
            "Este ejemplo usa los valores iniciales del simulador y no resuelve el caso nuevo de la parte 6."
        )
    st.markdown("#### Ahora experimenta con el nivel y la duración")
    inputs, result = st.columns([1.1, 1], gap="large")
    with inputs:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">AJUSTA LA FUENTE</div>'
                '<div style="font-size:1.08rem;font-weight:850;color:#17324a;margin:.4rem 0 .8rem">Nivel y duración de trabajo</div>',
                unsafe_allow_html=True,
            )
            base = st.slider("Aporte de la máquina sola durante operación [dB(A)]", 40, 110, 80, key="c4l1_s7_v2_base")
            active_minutes = st.slider("Minutos activos dentro de la hora", 0, 60, 15, key="c4l1_s7_v2_minutes")
            st.caption("Ingresa el aporte de la máquina en el receptor, separado del fondo.")
            st.markdown("**Ambiente del receptor · opcional**")
            use_background = st.checkbox("Incluir un ruido de fondo continuo", value=False, key="c4l1_s7_v2_background_on")
            background = 45
            if use_background:
                background = st.slider("Fondo continuo · LAeq en R1 [dB(A)]", 20, 80, 45, key="c4l1_s7_v2_background")
                st.caption("Por ejemplo, tránsito lejano u otras actividades. Se supone constante durante los 60 min, con la máquina encendida o apagada.")
            else:
                st.caption("Se calcula únicamente el aporte de la máquina. Omitir el fondo no equivale a suponer un ambiente de 0 dB.")
    fraction = active_minutes / 60
    source_energy = fraction * 10 ** (base / 10)
    equivalent = _s7_level(source_energy)
    correction = 10 * math.log10(fraction) if fraction > 0 else None
    total = _s7_level(source_energy + (10 ** (background / 10) if use_background else 0))
    with result:
        displayed_level = total if use_background else equivalent
        value = f"{displayed_level:.2f}" if displayed_level is not None else "Sin aporte"
        unit = "dB(A) · LAeq,T" if displayed_level is not None else "Fuente detenida"
        result_title = "RESULTADO · FUENTE + FONDO EN LA HORA" if use_background else "RESULTADO · APORTE DE LA MÁQUINA EN LA HORA"
        st.markdown(
            '<div style="border:1px solid #c9deed;border-radius:20px;padding:24px;'
            'background:linear-gradient(125deg,#f3faff,#e7f2fa);margin-bottom:14px">'
            f'<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">{result_title}</div>'
            f'<div style="font-size:2.65rem;font-weight:850;line-height:1.2;color:#17324a;margin:.8rem 0 .3rem">{value}</div>'
            f'<div style="font-size:.87rem;color:#526b7c">{unit}</div>'
            f'<div style="border-top:1px solid #c9deed;padding-top:13px;margin-top:18px;font-size:.88rem;color:#456275">'
            f'{active_minutes} min activos de 60 · nivel operativo {base} dB(A)</div></div>',
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            a, b = st.columns(2)
            a.metric("Tiempo activo", f"{fraction*100:.0f} %", help="t/T: minutos activos divididos por 60.")
            b.metric("Corrección temporal", f"{correction:.2f} dB" if correction is not None else "Sin aporte")
            st.markdown(
                '<div style="height:12px;border-radius:999px;background:#e8eff5;overflow:hidden">'
                f'<div style="height:100%;width:{fraction*100:.4f}%;background:#287bb0"></div></div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{active_minutes} min de actividad · {60-active_minutes} min sin aporte de la fuente")
            if use_background:
                st.metric("Máquina sola · aporte en la hora", f"{equivalent:.2f} dB(A)" if equivalent is not None else "Sin aporte")
                st.metric("Incremento del promedio sobre el fondo", f"{total-background:.2f} dB")
                operating_total = _s7_level(10**(base/10) + 10**(background/10))
                st.dataframe(
                    pd.DataFrame([
                        {"Estado": "Máquina activa", "Duración [min]": active_minutes, "Nivel fuente + fondo [dB(A)]": f"{operating_total:.2f}" if active_minutes else "No ocurre"},
                        {"Estado": "Máquina detenida", "Duración [min]": 60-active_minutes, "Nivel fuente + fondo [dB(A)]": f"{background:.2f}" if active_minutes < 60 else "No ocurre"},
                    ]), use_container_width=True, hide_index=True,
                )
    with st.container(border=True):
        st.markdown("**Referencias rápidas · efecto de la fracción activa en el mismo cálculo**")
        for col, percent in zip(st.columns(4), [100, 50, 25, 10]):
            with col:
                st.markdown(
                    '<div style="border:1px solid #dce7ef;border-radius:12px;padding:13px;background:#f7fafc;text-align:center">'
                    f'<div style="font-size:.78rem;color:#627989">{percent} % activo</div>'
                    f'<div style="font-size:1.18rem;font-weight:850;color:#24445c;margin-top:.3rem">{10*math.log10(percent/100):.2f} dB</div></div>',
                    unsafe_allow_html=True,
                )
        if active_minutes == 0:
            st.info(
                "La fuente no aporta energía a esta hora. Se muestra «Sin aporte»: log10(0) no tiene "
                "un valor finito y no corresponde asignarle 0 dB. Si hay fondo, este sigue presente."
            )
        else:
            st.markdown(
                f"**Lectura:** {active_minutes} min a {base} dB(A) aportan **{equivalent:.2f} dB(A)** "
                "al período de 60 min. La corrección cambia el aporte temporal; la máquina conserva "
                "su nivel durante operación."
            )
        if use_background:
            st.latex(r"L_{Aeq,T,\mathrm{total}}=10\log_{10}\left[(t/T)10^{L_{\mathrm{fuente}}/10}+10^{L_{\mathrm{fondo}}/10}\right]")
            st.markdown(
                "**Cómo se calcula:** durante la actividad se suman las energías de máquina y fondo; "
                "durante la parada permanece solo el fondo. Se ponderan ambos intervalos por su duración. "
                "La expresión anterior equivale a ese promedio porque el fondo está presente toda la hora."
            )
            st.info(
                "Si ingresas un nivel medido con la máquina encendida que ya incluye el fondo, "
                "no vuelvas a sumarlo: contarías dos veces su energía. Este simulador utiliza el aporte "
                "de la máquina separado del fondo; no aplica una corrección de mediciones."
            )
            if active_minutes == 0:
                st.caption(f"Con la máquina detenida toda la hora, el total coincide con el fondo: {background:.2f} dB(A).")
            st.caption(
                "El total no puede quedar por debajo del fondo incluido. Todos los niveles deben corresponder "
                "al mismo receptor y descriptor. Usa un LAeq del fondo representativo de T, no un LA90 ni un LAmax. "
                "Aquí se supone fondo constante: este cálculo energético no es una corrección normativa por ruido de fondo."
            )
            st.markdown(
                "[Referencia: FHWA · Noise Measurement Handbook, ajuste por fondo]"
                "(https://www.fhwa.dot.gov/ENVIRonment/noise/measurement/handbook.cfm)"
            )

    _s7_section(3, "Suma dos máquinas con distintos tiempos", "Define el nivel durante operación y los minutos activos de cada máquina. Ambas aportan al mismo receptor durante una hora.")
    machine_inputs = []
    for col, label, color in zip(st.columns(2, gap="large"), ["A", "B"], ["#287bb0", "#8a6bb5"]):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:{color}">MÁQUINA {label}</div>'
                    '<div style="font-size:1.05rem;font-weight:850;color:#17324a;margin:.45rem 0 .7rem">Nivel y tiempo durante operación</div>',
                    unsafe_allow_html=True,
                )
                selected_level = st.slider(
                    f"Máquina {label} · nivel durante operación [dB(A)]", 40, 100,
                    70 if label == "A" else 75, key=f"c4l1_s7_v3_machine_{label.lower()}_level",
                )
                minutes = st.slider(
                    f"Máquina {label} · minutos activos de 60", 0, 60,
                    40 if label == "A" else 10, key=f"c4l1_s7_v3_machine_{label.lower()}_minutes",
                )
                fraction = minutes / 60
                energy = fraction * 10**(selected_level/10)
                equivalent = _s7_level(energy)
                correction = 10*math.log10(fraction) if minutes else None
                a, b = st.columns(2)
                a.metric("Tiempo activo", f"{fraction*100:.1f} %")
                b.metric("Corrección temporal", f"{correction:.2f} dB" if correction is not None else "Sin aporte")
                st.markdown(
                    f'<div style="border:1px solid #dce7ef;border-radius:12px;padding:15px;background:#f7fafc">'
                    f'<div style="font-size:.78rem;color:#627989">Aporte de {label} a toda la hora</div>'
                    f'<div style="font-size:1.5rem;font-weight:850;color:{color};margin-top:.4rem">'
                    + (f'{equivalent:.2f} <span style="font-size:.85rem">dB(A)</span>' if equivalent is not None else 'Sin aporte')
                    + '</div></div>',
                    unsafe_allow_html=True,
                )
                machine_inputs.append({"label": label, "level": selected_level, "minutes": minutes,
                                       "energy": energy, "equivalent": equivalent})
    total_energy = sum(machine["energy"] for machine in machine_inputs)
    combined = _s7_level(total_energy)
    share_a = 100*machine_inputs[0]["energy"]/total_energy if total_energy else 0
    share_b = 100*machine_inputs[1]["energy"]/total_energy if total_energy else 0
    result_value = f'{combined:.2f} <span style="font-size:1rem;font-weight:600">dB(A)</span>' if combined is not None else "Sin aporte"
    st.markdown(
        '<div style="border:1px solid #c9deed;border-radius:20px;padding:22px 24px;'
        'background:linear-gradient(125deg,#f3faff,#eef1fa);margin:14px 0">'
        '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">RESULTADO · DOS MÁQUINAS · 60 MINUTOS</div>'
        f'<div style="font-size:2.5rem;font-weight:850;color:#17324a;margin:.55rem 0">{result_value}</div>'
        '<div style="font-size:.88rem;color:#526b7c">Primero se pondera cada máquina por su tiempo activo; '
        'después se suman sus energías.</div></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        finite = [machine for machine in machine_inputs if machine["equivalent"] is not None]
        a, b = st.columns(2)
        a.metric("Incremento sobre el mayor aporte horario",
                 f'{combined-max(machine["equivalent"] for machine in finite):.2f} dB' if finite else "Sin aporte")
        dominant = max(finite, key=lambda machine: machine["energy"]) if finite else None
        dominant_label = ("A y B · igual aporte" if len(finite) == 2 and abs(share_a-share_b) < 1e-9
                          else f'Máquina {dominant["label"]}' if dominant else "Ninguna")
        b.metric("Mayor contribución a la hora", dominant_label)
        st.markdown("**Cómo se reparte la energía del total**")
        st.markdown(
            '<div style="display:flex;height:18px;border-radius:999px;overflow:hidden;background:#e8eff5">'
            f'<div style="width:{share_a:.6f}%;background:#287bb0"></div>'
            f'<div style="width:{share_b:.6f}%;background:#8a6bb5"></div></div>'
            '<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:8px;font-size:.84rem;font-weight:750">'
            f'<span style="color:#287bb0">A · {share_a:.1f} %</span>'
            f'<span style="color:#8a6bb5">B · {share_b:.1f} %</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Porcentajes de energía acústica, no de sonoridad percibida. Con ambas máquinas detenidas no hay energía que repartir.")
        st.markdown("**01 · Aplica el mismo método a cada máquina**")
        st.latex(r"L_{Aeq,T,i}=L_{\mathrm{operación},i}+10\log_{10}(t_i/T)")
        st.markdown("**02 · Total energético de la hora**")
        st.latex(r"L_{Aeq,T,\Sigma}=10\log_{10}\left[\frac{t_A}{T}10^{L_A/10}+\frac{t_B}{T}10^{L_B/10}\right]")
        st.markdown("**Variables de las dos ecuaciones**")
        variable_definitions = [
            ("L<sub>operación,i</sub> · L<sub>A</sub> · L<sub>B</sub>", "Nivel durante operación", "Aporte de la máquina i sola en el receptor. L_A y L_B son los niveles operativos de A y B, separados del fondo.", "dB(A)"),
            ("t<sub>i</sub> · t<sub>A</sub> · t<sub>B</sub>", "Tiempo activo de cada máquina", "Minutos que funciona cada máquina dentro del período. A y B pueden tener distintas duraciones y trabajar simultáneamente.", "min"),
            ("T", "Período total de evaluación", "Duración común sobre la que se promedian las energías. En este ejercicio T = 60 min.", "min"),
            ("L<sub>Aeq,T,i</sub>", "Aporte equivalente de una máquina", "Energía de la máquina i repartida sobre todo T, después de aplicar su corrección temporal.", "dB(A)"),
            ("L<sub>Aeq,T,Σ</sub>", "Nivel equivalente del conjunto", "Resultado de sumar las energías de A y B y promediarlas sobre el mismo período T.", "dB(A)"),
            ("t<sub>i</sub>/T · t<sub>A</sub>/T · t<sub>B</sub>/T", "Fracción activa", "Proporción del período durante la que trabaja cada máquina. Usa la misma unidad para el numerador y el denominador.", "Sin unidad"),
        ]
        variable_columns = st.columns(2, gap="medium")
        for index, (symbol, title, description, unit) in enumerate(variable_definitions):
            with variable_columns[index % 2]:
                st.markdown(
                    '<div style="border:1px solid #dce8f1;border-radius:12px;padding:15px 16px;'
                    'background:#f7fafc;margin-bottom:10px">'
                    '<div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap">'
                    f'<span style="font-size:1.1rem;font-weight:850;color:#176b9b">{symbol}</span>'
                    f'<span style="font-size:.75rem;color:#526b7c;background:#e8eff5;border-radius:7px;padding:4px 8px">{unit}</span>'
                    '</div>'
                    f'<div style="font-size:.86rem;font-weight:800;color:#24445c;margin:.6rem 0 .3rem">{title}</div>'
                    f'<div style="font-size:.82rem;color:#627989;line-height:1.6">{description}</div></div>',
                    unsafe_allow_html=True,
                )
        st.caption(
            "i identifica la máquina; A y B identifican las dos máquinas; Σ representa el conjunto. "
            "En el descriptor LAeq, A indica ponderación A y eq indica nivel equivalente. "
            "log10 es el logaritmo en base 10. El término 10 log10(tᵢ/T) es una corrección en dB. "
            "Si tᵢ = 0, esa máquina aporta energía nula y se omite el logaritmo de cero."
        )
        st.markdown("**Sustitución con tus valores**")

        if combined is not None:
            terms = "+".join(f"({m['minutes']}/60)10^{{{m['level']}/10}}" for m in machine_inputs)
            st.latex(r"L_{Aeq,60\,\mathrm{min}}=10\log_{10}\left[" + terms + r"\right]=" + f"{combined:.2f}" + r"\ \mathrm{dB(A)}")
        st.info(
            "Prueba una máquina más ruidosa que trabaja pocos minutos frente a otra menos ruidosa que "
            "trabaja más tiempo. La dominante depende de ambas variables."
        )
        st.caption(
            "Se suman aportes separados del fondo, con nivel constante durante operación y sin aporte "
            "durante la parada. Los tiempos pueden solaparse y su suma superar 60 min. "
            "Este cálculo da el promedio horario; la parte 4 permite explorar las coincidencias."
        )

    _s7_section(4, "Descubre qué cambia con la simultaneidad", "Mantén iguales los tiempos activos y cambia solo la coincidencia de dos máquinas.")
    with st.container(border=True):
        st.markdown("**Experimento:** A y B aportan 70 dB(A) cada una mientras operan. Cada máquina trabaja 30 min de la hora.")
        overlap = st.slider("Minutos de operación simultánea", 0, 30, 0, key="c4l1_s7_v2_overlap")
        comparison_sources = [
            {"name": "Máquina A", "level": 70, "window": (0, 30), "color": "#287bb0"},
            {"name": "Máquina B", "level": 70, "window": (30-overlap, 60-overlap), "color": "#8a6bb5"},
        ]
        _s7_timeline(comparison_sources)
        comparison_segments, comparison_level = _s7_schedule(comparison_sources)
        interval_max = max(s["level"] for s in comparison_segments if s["level"] is not None)
        a, b, c = st.columns(3)
        a.metric("LAeq de la hora", f"{comparison_level:.2f} dB(A)")
        b.metric("Mayor nivel de intervalo", f"{interval_max:.2f} dB(A)")
        c.metric("Minutos sin estas fuentes", f"{overlap} min")
        st.success(
            "El LAeq de la hora permanece en 70,00 dB(A): cada fuente conserva su energía acumulada. "
            + (f"Hay {overlap} min con ambas máquinas: el nivel de esos intervalos es 73,01 dB(A), "
               f"y hay {overlap} min sin aporte de ellas."
               if overlap else "Sin coincidencia, una sola máquina opera en cada intervalo y el nivel es 70,00 dB(A) durante toda la hora.")
        )
        st.caption(
            "En este experimento se omite el fondo. «Sin aporte» no significa silencio real ni 0 dB. "
            "El mayor nivel de intervalo no es un LAFmax medido: describe la suma de niveles constantes del modelo. "
            "Separar horarios conserva el promedio solo si cada fuente mantiene su nivel y su tiempo activo dentro del mismo T."
        )
        with st.expander("Por qué el promedio se conserva"):
            st.latex(r"\frac{30}{60}10^{70/10}+\frac{30}{60}10^{70/10}=10^{70/10}")
            st.markdown(
                "Bajo los supuestos de suma energética y niveles constantes, el orden de los intervalos "
                "no cambia la energía acumulada. Cambiar el tiempo activo, el modo de operación o la geometría "
                "sí puede cambiar el LAeq. Separar tareas puede reducir las coincidencias ruidosas sin reducir "
                "por sí solo el promedio de toda la hora."
            )

    _s7_section(5, "Diseña una hora de obra", "Ajusta los horarios y niveles de cuatro fuentes y revisa el resultado en el receptor R1.")
    st.markdown(
        '<div style="border:1px solid #cbdfea;border-radius:20px;padding:20px 24px;'
        'background:linear-gradient(125deg,#f7fbfe,#eaf3fa);margin:8px 0 18px">'
        '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">SIMULADOR DE OBRA</div>'
        '<div style="font-size:1.2rem;font-weight:850;color:#17324a;margin:.5rem 0">Cuatro máquinas, una hora y un receptor</div>'
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px">'
        '<span style="background:#fff;border:1px solid #dce7ef;border-radius:999px;padding:6px 12px;color:#456275;font-size:.8rem">Receptor · R1</span>'
        '<span style="background:#fff;border:1px solid #dce7ef;border-radius:999px;padding:6px 12px;color:#456275;font-size:.8rem">Período · 60 min</span>'
        '<span style="background:#fff;border:1px solid #dce7ef;border-radius:999px;padding:6px 12px;color:#456275;font-size:.8rem">Entradas · nivel y horario</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Niveles didácticos de presión sonora en R1 durante operación; no son niveles universales "
        "de máquinas ni potencias sonoras. El generador puede mantenerse continuo o detenerse."
    )
    specifications = [
        ("Excavadora", 67, (0, 48), "#287bb0"),
        ("Mixer", 64, (12, 30), "#5a9270"),
        ("Martillo", 74, (30, 39), "#ce7452"),
        ("Generador", 59, (0, 60), "#8a6bb5"),
    ]
    st.markdown("#### Configura las fuentes")
    sources = []
    controls = st.columns(2, gap="large")
    for i, (name, level, window, color) in enumerate(specifications):
        with controls[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div style="border-left:4px solid {color};padding-left:12px;margin:4px 0 14px">'
                    f'<div style="font-size:.7rem;font-weight:850;letter-spacing:.1em;color:{color}">FUENTE 0{i+1}</div>'
                    f'<div style="font-size:1.2rem;font-weight:850;color:#17324a;margin-top:.3rem">{name}</div></div>',
                    unsafe_allow_html=True,
                )
                selected_level = st.slider(
                    f"Nivel de {name} en R1 [dB(A)]", 40, 100, level, key=f"c4l1_s7_v2_level_{i}"
                )
                selected_window = st.slider(
                    f"Inicio y término de {name} [min]", 0, 60, window, key=f"c4l1_s7_v2_window_{i}"
                )
                duration = selected_window[1]-selected_window[0]
                st.markdown(
                    '<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'
                    'background:#f4f8fb;border-radius:10px;padding:10px 12px;margin-top:8px;font-size:.8rem;color:#456275">'
                    f'<span><b>{duration} min</b> activos · {duration/60*100:.0f} %</span>'
                    f'<span>{selected_window[0]}–{selected_window[1]} min</span></div>',
                    unsafe_allow_html=True,
                )
                st.caption("Igualar inicio y término deja la máquina inactiva.")
                sources.append({"name": name, "level": selected_level, "window": selected_window, "color": color})
    st.markdown("#### Observa el cronograma y el resultado")
    with st.container(border=True):
        include_floor = st.checkbox("Agregar fondo continuo en R1", value=False, key="c4l1_s7_v2_floor_on")
        floor = st.slider("Fondo continuo · LAeq en R1 [dB(A)]", 20, 80, 45, key="c4l1_s7_v2_floor", disabled=not include_floor)
        st.markdown(
            '<div style="font-size:.75rem;font-weight:850;letter-spacing:.08em;color:#526d80;margin:14px 0 8px">CRONOGRAMA · 0 A 60 MIN</div>',
            unsafe_allow_html=True,
        )
        _s7_timeline(sources)
        st.caption("Cada color corresponde a una máquina. Las barras superpuestas en el tiempo indican operación simultánea.")
        segments, scenario_level = _s7_schedule(sources, background=floor if include_floor else None)
        contributions = []
        for source in sources:
            duration = source["window"][1] - source["window"][0]
            energy = duration / 60 * 10 ** (source["level"] / 10)
            contributions.append({**source, "duration": duration, "energy": energy, "equivalent": _s7_level(energy)})
        total_energy = sum(source["energy"] for source in contributions) + (10 ** (floor / 10) if include_floor else 0)
        available = [source for source in contributions if source["energy"] > 0]
        dominant = max(available, key=lambda source: source["energy"]) if available else None
        dominant_names = [
            source["name"] for source in available
            if math.isclose(source["energy"], dominant["energy"], rel_tol=1e-9)
        ] if dominant else []
        dominant_display = ("Empate: " + ", ".join(dominant_names) if len(dominant_names) > 1
                            else dominant_names[0] if dominant_names else "Ninguna")
        finite_segments = [s["level"] for s in segments if s["level"] is not None]
        reference_energy = sum((window[1]-window[0])/60 * 10**(level/10) for _, level, window, _ in specifications)
        reference_level = _s7_level(reference_energy + (10**(floor/10) if include_floor else 0))
        result_value = f'{scenario_level:.2f}' if scenario_level is not None else "Sin aporte"
        difference = f'{scenario_level-reference_level:+.2f} dB respecto del caso inicial' if scenario_level is not None else "Todas las máquinas están detenidas; no se incluye fondo."
        difference_color = "#2d7a4a" if scenario_level is not None and scenario_level <= reference_level else "#a05b3a"
        st.markdown(
            '<div style="border:1px solid #c9deed;border-radius:18px;padding:20px 24px;'
            'background:linear-gradient(125deg,#f3faff,#edf2fa);margin:16px 0">'
            '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">RESULTADO EN R1 · PROMEDIO DE LA HORA</div>'
            f'<div style="font-size:2.55rem;font-weight:850;color:#17324a;margin:.6rem 0">{result_value}'
            + (' <span style="font-size:1rem;font-weight:600">dB(A)</span>' if scenario_level is not None else '')
            + f'</div><div style="font-size:.86rem;font-weight:750;color:{difference_color}">{difference}</div></div>',
            unsafe_allow_html=True,
        )
        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.caption("INTERVALO MÁS RUIDOSO")
                st.metric("Mayor nivel de intervalo", f"{max(finite_segments):.2f} dB(A)" if finite_segments else "Sin aporte")
                st.caption("Nivel del modelo en un intervalo; no es un LAFmax medido.")
        with b:
            with st.container(border=True):
                st.caption("CONTRIBUCIÓN DOMINANTE")
                st.metric("Máquina con mayor aporte", dominant_display)
                st.caption("Se identifica después de ponderar el tiempo activo.")
        st.markdown("#### Aportes de cada máquina")
        st.dataframe(
            pd.DataFrame([{
                "Fuente": s["name"],
                "Nivel operativo [dB(A)]": f'{s["level"]:.1f}',
                "Tiempo activo [min]": s["duration"],
                "Corrección [dB]": f'{10*math.log10(s["duration"]/60):.2f}' if s["duration"] else "Sin aporte",
                "Aporte en 60 min [dB(A)]": f'{s["equivalent"]:.2f}' if s["equivalent"] is not None else "Sin aporte",
                "Energía del total [%]": f'{100*s["energy"]/total_energy:.1f}' if total_energy else "—",
            } for s in contributions]),
            use_container_width=True, hide_index=True,
        )
        if include_floor:
            st.caption(f"El fondo continuo también aporta {100*10**(floor/10)/total_energy:.1f} % de la energía total; no figura como máquina.")
        st.caption("La comparación usa los niveles y horarios iniciales de las cuatro máquinas, con la misma configuración de fondo.")
        st.markdown("#### Distribución de energía")
        st.bar_chart(
            pd.DataFrame({"Fuente": [s["name"] for s in contributions],
                          "Energía del total [%]": [100*s["energy"]/total_energy if total_energy else 0 for s in contributions]}).set_index("Fuente"),
            use_container_width=True,
        )
        with st.expander("Detalle de los intervalos del cronograma"):
            st.dataframe(
                pd.DataFrame([{
                    "Intervalo [min]": f'{s["start"]}–{s["end"]}',
                    "Duración [min]": s["end"]-s["start"],
                    "Máquinas activas": ", ".join(s["active"]) or "Ninguna",
                    "Nivel de intervalo [dB(A)]": f'{s["level"]:.2f}' if s["level"] is not None else "Sin aporte",
                } for s in segments]), use_container_width=True, hide_index=True,
            )
            st.caption("Se integra cada intervalo según su duración; los intervalos largos pesan más que los cortos.")
        st.markdown(
            '<div style="border:1px solid #dce7ef;border-radius:14px;padding:16px 18px;background:#f6f9fc;margin-top:14px">'
            '<div style="font-size:.75rem;font-weight:850;letter-spacing:.08em;color:#176b9b">EXPERIMENTA CON EL ESCENARIO</div>'
            '<div style="color:#456275;font-size:.88rem;line-height:1.8;margin-top:8px">'
            '<b>01 ·</b> Acorta el tiempo del martillo y observa el promedio.<br>'
            '<b>02 ·</b> Desplaza su horario manteniendo la duración y revisa las coincidencias.<br>'
            '<b>03 ·</b> Detén el generador y compara su aporte con el de las otras máquinas.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with st.expander("Profundiza · promedio energético por intervalos"):
        st.markdown(
            """
            <style>
            .st-key-c4l1_s7_equation {
                border:1px solid #c9ddeb !important;
                border-radius:22px !important;
                background:linear-gradient(130deg,#f8fcff 0%,#edf5fb 100%);
                padding:22px !important;
                box-shadow:0 8px 24px rgba(30,65,92,.06);
            }
            .st-key-c4l1_s7_equation [data-testid="stLatex"] {
                background:#fff;
                border:1px solid #dce8f1;
                border-radius:16px;
                padding:22px 12px;
                margin:8px 0 12px;
                color:#17324a;
                overflow-x:auto;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        with st.container(key="c4l1_s7_equation", border=True):
            st.markdown(
                '<div style="font-size:.72rem;font-weight:850;letter-spacing:.12em;color:#176b9b">'
                'LA ECUACIÓN · PROMEDIO ENERGÉTICO</div>'
                '<div style="font-size:1.2rem;font-weight:850;color:#17324a;margin:.5rem 0 .4rem">'
                'De los intervalos de trabajo al nivel de toda la hora</div>'
                '<div style="font-size:.88rem;color:#526b7c;line-height:1.6;margin-bottom:8px">'
                'Cada intervalo aporta energía según su nivel y su duración.</div>',
                unsafe_allow_html=True,
            )
            st.latex(r"L_{Aeq,T}=10\log_{10}\left[\frac{1}{T}\sum_j\Delta t_j\,10^{L_{Aeq,j}/10}\right]")
            terms = [
                ("T", "Período total", "60 min en este laboratorio."),
                ("Δtⱼ", "Duración del intervalo", "Minutos con un nivel constante."),
                ("L<sub>Aeq,j</sub>", "Nivel del intervalo", "Nivel equivalente en el receptor."),
            ]
            for col, (symbol, title, description) in zip(st.columns(3), terms):
                with col:
                    st.markdown(
                        '<div style="background:#fff;border:1px solid #dce8f1;border-radius:12px;padding:14px;min-height:125px">'
                        f'<div style="font-size:1.3rem;font-weight:850;color:#176b9b">{symbol}</div>'
                        f'<div style="font-size:.84rem;font-weight:800;color:#24445c;margin:.4rem 0">{title}</div>'
                        f'<div style="font-size:.8rem;line-height:1.5;color:#627989">{description}</div></div>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 12px">'
                '<span style="background:#deedf7;border-radius:9px;padding:8px 12px;color:#245b7c;font-size:.8rem;font-weight:750">01 · Convierte a energía</span>'
                '<span style="background:#deedf7;border-radius:9px;padding:8px 12px;color:#245b7c;font-size:.8rem;font-weight:750">02 · Pondera por duración</span>'
                '<span style="background:#deedf7;border-radius:9px;padding:8px 12px;color:#245b7c;font-size:.8rem;font-weight:750">03 · Suma y divide por T</span>'
                '<span style="background:#deedf7;border-radius:9px;padding:8px 12px;color:#245b7c;font-size:.8rem;font-weight:750">04 · Vuelve a dB</span>'
                '</div>'
                '<div style="font-size:.85rem;line-height:1.6;color:#526b7c">'
                '<b style="color:#24445c">Clave:</b> no promedies los dB aritméticamente. '
                'Si la máquina tiene varios modos de trabajo, usa el nivel y la duración de cada modo. '
                'T y Δtⱼ deben expresarse en la misma unidad.</div>'
                '<div style="border-top:1px solid #c9ddeb;padding-top:12px;margin-top:14px;'
                'color:#627989;font-size:.8rem;line-height:1.6">'
                '<b>Supuestos del laboratorio:</b> receptor y geometría fijos · nivel constante durante la actividad · '
                'contribuciones independientes · sin aporte propio de la máquina durante la parada.</div>',
                unsafe_allow_html=True,
            )
        st.caption("j identifica un intervalo del cronograma; i identifica una máquina. La suma por intervalos integra el nivel total de cada tramo. La suma por máquinas combina sus aportes equivalentes calculados sobre el mismo T. Son dos formas compatibles de contabilizar la misma energía, bajo los supuestos del laboratorio.")

        st.markdown("**Condiciones para usar la ecuación por intervalos**")
        st.caption(
            "Los intervalos j deben cubrir todo T sin huecos ni superposiciones: ΣΔtⱼ = T. "
            "Su nivel corresponde al total presente en el receptor durante ese tramo, incluido el fondo "
            "si se modela. Un tramo sin ninguna contribución tiene energía nula; no se representa como 0 dB."
        )
        st.markdown("**Si la máquina tiene varios modos, incluido el ralentí**")
        st.latex(r"L_{Aeq,T,i}=10\log_{10}\left[\sum_k\frac{t_{i,k}}{T}\,10^{L_{Aeq,i,k}/10}\right]")
        st.caption(
            "k identifica un modo de la máquina i; tᵢ,ₖ es su duración y LAeq,i,k su nivel en el receptor. "
            "Los modos no se superponen para la misma máquina. Incluye el ralentí con su nivel real; "
            "si existe una parada sin aporte, su término energético es cero. Esta es una extensión "
            "del método; los simuladores de esta etapa usan un solo modo activo por máquina."
        )
        st.caption(
            "10^(L/10) representa el factor relativo de presión sonora cuadrática media ponderada A "
            "respecto de la referencia acústica. Se usa como «energía relativa» para sumar contribuciones; "
            "no es una cantidad de energía expresada en joules."
        )

    _s7_section(6, "Resuelve y comprueba", "Resuelve un caso nuevo: transforma los porcentajes activos en tiempos y aportes equivalentes, y calcula el total.")
    case_data = [("Excavadora", 68.0, 60), ("Mixer", 65.0, 40), ("Martillo", 76.0, 10), ("Generador", 58.0, 100)]
    equivalents = [level+10*math.log10(duty/100) for _, level, duty in case_data]
    expected_total = _s7_level(sum(10**(level/10) for level in equivalents))
    expected_name = case_data[max(range(len(equivalents)), key=lambda i: equivalents[i])][0]
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">DESAFÍO INDIVIDUAL · CASO NUEVO</div>'
            '<div style="font-size:1.15rem;font-weight:850;color:#17324a;margin:.5rem 0">Evalúa una hora de trabajo en el receptor R1</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Antecedentes:** T = 60 min; receptor fijo; sin fondo en el cálculo. "
            "Los niveles corresponden a cada máquina sola durante operación en R1. "
            "Supón niveles constantes y sin aporte de la máquina durante la parada."
        )
        st.dataframe(
            pd.DataFrame([{"Fuente": name, "Nivel operativo [dB(A)]": level, "Tiempo activo [%]": duty}
                          for name, level, duty in case_data]),
            use_container_width=True, hide_index=True,
        )
        st.markdown(
            "**Tu trabajo:** calcula los minutos activos, la corrección temporal y el aporte equivalente "
            "de cada máquina. Después suma energéticamente los cuatro aportes e identifica la fuente dominante."
        )
        st.caption(
            "Usa las ecuaciones de las partes anteriores. Conserva los decimales durante el cálculo y "
            "redondea al final. La comprobación señala qué revisar sin mostrar los resultados."
        )
        with st.form("c4l1_s7_v3_exercise"):
            answers = []
            for i, (name, level, duty) in enumerate(case_data):
                st.markdown(f"**0{i+1} · {name}**")
                a, b, c = st.columns(3)
                with a:
                    minutes_answer = st.number_input(
                        f"{name} · minutos activos", min_value=0.0, max_value=60.0,
                        value=None, step=0.1, placeholder="Calcula t", key=f"c4l1_s7_v3_ex_minutes_{i}",
                    )
                with b:
                    correction_answer = st.number_input(
                        f"{name} · corrección temporal [dB]", min_value=-60.0, max_value=0.0,
                        value=None, step=0.1, placeholder="Calcula ΔLt", key=f"c4l1_s7_v3_ex_correction_{i}",
                    )
                with c:
                    equivalent_answer = st.number_input(
                        f"{name} · aporte en la hora [dB(A)]", min_value=0.0, max_value=120.0,
                        value=None, step=0.1, placeholder="Calcula LAeq,T", key=f"c4l1_s7_v3_ex_equivalent_{i}",
                    )
                answers.append((minutes_answer, correction_answer, equivalent_answer))
            st.markdown("**Integra el resultado de las cuatro máquinas**")
            a, b = st.columns(2)
            with a:
                ans_total = st.number_input(
                    "Total de la hora [dB(A)]", min_value=0.0, max_value=120.0,
                    value=None, step=0.1, placeholder="Suma las energías", key="c4l1_s7_v3_ex_total",
                )
            with b:
                ans_dom = st.selectbox(
                    "Fuente dominante", ["Selecciona", "Excavadora", "Mixer", "Martillo", "Generador"],
                    key="c4l1_s7_v3_ex_dominant",
                )
            explanation = st.text_area(
                "Justifica por qué domina esa fuente",
                placeholder="Relaciona el nivel durante operación con el tiempo activo.",
                key="c4l1_s7_v3_ex_explanation",
            )
            submitted = st.form_submit_button("Comprobar mi ejercicio", type="primary", use_container_width=True)
        if submitted:
            incomplete = any(value is None for row in answers for value in row) or ans_total is None or ans_dom == "Selecciona"
            if incomplete:
                st.warning("Completa todos los cálculos y selecciona la fuente dominante antes de comprobar.")
            elif len(explanation.strip()) < 40:
                st.warning("Justifica tu elección con al menos 40 caracteres, relacionando nivel y duración.")
            else:
                checks, feedback = [], []
                for (name, level, duty), (minutes_answer, correction_answer, equivalent_answer), expected_equivalent in zip(case_data, answers, equivalents):
                    row_checks = [
                        abs(minutes_answer-60*duty/100) <= .1,
                        abs(correction_answer-10*math.log10(duty/100)) <= .2,
                        abs(equivalent_answer-expected_equivalent) <= .2,
                    ]
                    checks.extend(row_checks)
                    for label, passed, hint in zip(
                        ["Tiempo activo", "Corrección temporal", "Aporte equivalente"], row_checks,
                        ["Convierte el porcentaje en una fracción y multiplícala por T.",
                         "Usa 10 log10(t/T); la corrección es cero o negativa.",
                         "Suma la corrección temporal al nivel durante operación."],
                    ):
                        feedback.append({"Fuente": name, "Cálculo": label,
                                         "Revisión": "Correcto" if passed else "Revisar",
                                         "Orientación": "—" if passed else hint})
                total_ok = abs(ans_total-expected_total) <= .2
                dominant_ok = ans_dom == expected_name
                checks.extend([total_ok, dominant_ok])
                feedback.extend([
                    {"Fuente": "Conjunto", "Cálculo": "Total de la hora", "Revisión": "Correcto" if total_ok else "Revisar",
                     "Orientación": "—" if total_ok else "Convierte los cuatro aportes equivalentes a energía, suma y vuelve a dB."},
                    {"Fuente": "Conjunto", "Cálculo": "Fuente dominante", "Revisión": "Correcto" if dominant_ok else "Revisar",
                     "Orientación": "—" if dominant_ok else "Compara los aportes equivalentes de la hora, no solo los niveles operativos."},
                ])
                if all(checks):
                    st.success("Correcto: resolviste los tiempos, las correcciones, los aportes y la suma energética.")
                else:
                    st.warning(f"Comprobaciones correctas: {sum(checks)}/{len(checks)}. Revisa las pistas y vuelve a intentarlo.")
                st.dataframe(pd.DataFrame(feedback), use_container_width=True, hide_index=True)
                st.caption(
                    "Tolerancia: ±0,1 min y ±0,2 dB. La justificación se guarda para revisión docente; "
                    "la comprobación automática valida los cálculos y la selección."
                )
                saved["c4l1_stage7_check"] = {
                    "correct": sum(checks), "total": len(checks), "exercise_version": 3,
                    "answers": {row[0]: {"minutes": answer[0], "correction": answer[1], "equivalent": answer[2]}
                                for row, answer in zip(case_data, answers)},
                    "total_answer": ans_total, "dominant_answer": ans_dom, "explanation": explanation,
                }
                _save_stage_state(lab, saved, 7)

    with st.expander("Criterios técnicos y referencias"):
        st.markdown(
            "**Para trasladar el cálculo a una obra:** declara receptor, período, descriptor, niveles por modo "
            "de operación, tiempos activos, coincidencias y tratamiento del fondo. Un porcentaje activo no "
            "describe por sí solo el cronograma.\n\n"
            "No apliques dos veces el tiempo activo a un nivel que ya representa toda la hora. "
            "No mezcles Lw, LAeq y LAmax como si fueran entradas equivalentes. "
            "La suma de energías presupone fuentes no coherentes; una interacción entre máquinas que cambie "
            "su emisión queda fuera de este modelo simplificado.\n\n"
            "[FHWA · Construction Noise Handbook: Terminology]"
            "(https://www.fhwa.dot.gov/environment/noise/construction_noise/handbook/handbook02.cfm)"
        )
    if st.session_state.get("role") == "Docente":
        with st.expander("Pauta docente detallada · ejercicio de la parte 6", expanded=False):
            st.markdown(
                '<div style="border:1px solid #d4e3ed;border-radius:16px;padding:18px 20px;background:#f1f7fb">'
                '<div style="font-size:.72rem;font-weight:850;letter-spacing:.1em;color:#176b9b">GUÍA DE CORRECCIÓN · USO DOCENTE</div>'
                '<div style="font-size:1.15rem;font-weight:850;color:#17324a;margin:.5rem 0">Qué debe calcular el alumno y cómo acompañarlo</div>'
                '<div style="font-size:.86rem;color:#526b7c;line-height:1.6">Esta pauta corresponde al caso nuevo de la parte 6, '
                'no a los valores modificables del simulador. El alumno mantiene sus campos vacíos y recibe pistas al comprobar.</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("#### 1 · Qué significa cada campo")
            st.markdown(
                "- **Minutos activos, tᵢ:** cuánto trabaja la máquina dentro de T = 60 min. "
                "Se obtiene multiplicando el porcentaje activo, expresado como fracción, por 60.\n"
                "- **Corrección temporal, ΔLt,i [dB]:** ajuste que reparte la energía de la actividad "
                "sobre toda la hora. No es una reducción física del ruido de la máquina. "
                "Es negativa si trabaja parte de la hora y cero si trabaja toda la hora.\n"
                "- **Aporte en la hora, LAeq,T,i [dB(A)]:** nivel operativo más la corrección temporal. "
                "Describe la contribución individual al promedio horario en R1.\n"
                "- **Total de la hora:** suma energética de los cuatro aportes equivalentes; "
                "no es su suma ni su promedio aritmético.\n"
                "- **Fuente dominante:** máquina con la mayor contribución energética a la hora, "
                "equivalente a la de mayor LAeq,T,i."
            )
            st.caption(
                "Los niveles de entrada son de presión sonora en el mismo receptor, separados del fondo; "
                "no son Lw ni LAmax. Se supone nivel constante durante operación y aporte nulo durante la parada."
            )
            st.markdown("#### 2 · Resultados para completar los campos")
            teacher_energies = [10**(value/10) for value in equivalents]
            teacher_energy_total = sum(teacher_energies)
            teacher_rows = []
            for (name, level, duty), equivalent, energy in zip(case_data, equivalents, teacher_energies):
                teacher_rows.append({
                    "Fuente": name,
                    "Nivel operativo [dB(A)]": f"{level:.2f}",
                    "Activo [%]": duty,
                    "Minutos activos": f"{60*duty/100:.2f}",
                    "Corrección temporal [dB]": f"{10*math.log10(duty/100):.2f}",
                    "Aporte en la hora [dB(A)]": f"{equivalent:.2f}",
                    "Energía del conjunto [%]": f"{100*energy/teacher_energy_total:.2f}",
                })
            st.dataframe(pd.DataFrame(teacher_rows), use_container_width=True, hide_index=True)
            st.caption("Los resultados se calculan con todos los decimales y se redondean aquí a dos decimales.")
            st.markdown("**Desarrollo por máquina**")
            for (name, level, duty), equivalent in zip(case_data, equivalents):
                with st.expander(f"{name} · desarrollo paso a paso"):
                    minutes = 60*duty/100
                    correction = 10*math.log10(duty/100)
                    st.markdown("**Paso 1 · Convierte el porcentaje en minutos**")
                    st.latex(r"t_i=\frac{p_i}{100}T=" + f"({duty}/100)\\times60={minutes:.0f}" + r"\ \mathrm{min}")
                    st.markdown("**Paso 2 · Calcula la corrección temporal**")
                    st.latex(r"\Delta L_{t,i}=10\log_{10}(t_i/T)=10\log_{10}" + f"({minutes:.0f}/60)={correction:.2f}" + r"\ \mathrm{dB}")
                    st.markdown("**Paso 3 · Obtén el aporte equivalente de la hora**")
                    st.latex(r"L_{Aeq,T,i}=L_{\mathrm{operación},i}+\Delta L_{t,i}=" + f"{level:.2f}+({correction:.2f})={equivalent:.2f}" + r"\ \mathrm{dB(A)}")
                    st.caption(
                        f"{name} conserva {level:.0f} dB(A) durante operación; "
                        f"su energía repartida sobre 60 min equivale a {equivalent:.2f} dB(A)."
                    )
            st.markdown("#### 3 · Cómo calcular el total")
            st.markdown(
                "**Primero**, transforma cada aporte horario en energía relativa: Eᵢ = 10^(LAeq,T,i/10). "
                "**Después**, suma las cuatro energías. **Finalmente**, aplica 10 log10 a esa suma. "
                "No vuelvas a multiplicar por el tiempo activo: ya está incorporado en los aportes equivalentes."
            )
            st.dataframe(
                pd.DataFrame([{"Fuente": row[0], "Energía relativa · sin unidad": f"{energy:,.2f}"}
                              for row, energy in zip(case_data, teacher_energies)]),
                use_container_width=True, hide_index=True,
            )
            st.latex(r"L_{Aeq,T,\Sigma}=10\log_{10}\left[\sum_i10^{L_{Aeq,T,i}/10}\right]")
            st.latex(r"L_{Aeq,T,\Sigma}=10\log_{10}\left[" + f"{teacher_energy_total:.2f}" + r"\right]=" + f"{expected_total:.2f}" + r"\ \mathrm{dB(A)}")
            st.success(f"Resultado esperado: {expected_total:.2f} dB(A). Fuente dominante: {expected_name}.")
            st.markdown("#### 4 · Justificación que se espera del alumno")
            st.markdown(
                "El **martillo** trabaja pocos minutos, pero su nivel operativo alto produce el mayor aporte "
                "equivalente de la hora. Su aporte es **66,00 dB(A)**, ligeramente superior al de la excavadora "
                "(**65,78 dB(A)**). Aporta aproximadamente **41,20 %** de la energía total; "
                "la excavadora aporta **39,18 %**. El generador opera toda la hora, pero su nivel menor "
                "limita su contribución.\n\n"
                "**Respuesta modelo:** «Domina el martillo porque, tras ponderar cada máquina por su tiempo "
                "activo, su aporte horario es el mayor. La excavadora tiene un aporte muy cercano. "
                "La selección considera nivel y duración, no solo el ruido durante operación»."
            )
            st.caption(
                "La diferencia entre los dos mayores aportes es pequeña: esta es la conclusión del caso "
                "numérico idealizado. En una obra real, la incertidumbre de niveles y tiempos puede cambiar el orden."
            )
            st.markdown("#### 5 · Criterios de corrección")
            st.markdown(
                "**Comprobación automática: 14 verificaciones**\n\n"
                "- 4 tiempos activos: tolerancia ±0,1 min.\n"
                "- 4 correcciones temporales y 4 aportes equivalentes: tolerancia ±0,2 dB.\n"
                "- 1 total energético: tolerancia ±0,2 dB.\n"
                "- 1 selección de fuente dominante: martillo.\n\n"
                "**Justificación: revisión docente.** El mínimo de 40 caracteres solo exige desarrollar "
                "la respuesta; no garantiza que sea técnicamente correcta."
            )
            st.dataframe(
                pd.DataFrame([
                    {"Criterio de la justificación": "Relaciona nivel y duración", "Puntos sugeridos": "0–2", "Logro completo": "Explica que la energía depende de ambas variables."},
                    {"Criterio de la justificación": "Compara aportes equivalentes", "Puntos sugeridos": "0–2", "Logro completo": "Identifica el martillo y reconoce la cercanía con la excavadora."},
                    {"Criterio de la justificación": "Interpreta el resultado", "Puntos sugeridos": "0–2", "Logro completo": "Distingue aporte horario de nivel operativo y evita sumar dB."},
                ]), use_container_width=True, hide_index=True,
            )
            st.caption(
                "Si necesitas una calificación: propuesta de 20 puntos, con 14 por cálculos y selección "
                "y 6 por justificación. Es una rúbrica sugerida; la app registra las 14 verificaciones, "
                "sin asignar automáticamente los puntos de la explicación."
            )
            st.markdown("#### 6 · Errores frecuentes y cómo orientarlos")
            st.dataframe(
                pd.DataFrame([
                    {"Error observado": "Usa 60 en lugar de 0,60", "Orientación docente": "Pide expresar primero el porcentaje como fracción."},
                    {"Error observado": "Confunde minutos con porcentaje", "Orientación docente": "Pregunta: ¿60 % de una hora cuántos minutos representa?"},
                    {"Error observado": "Ingresa −0,10 dB para la excavadora", "Orientación docente": "No se ingresa la fracción como corrección: hay que calcular 10 log10(0,60), que da aproximadamente −2,22 dB."},
                    {"Error observado": "Resta una corrección ya negativa", "Orientación docente": "El aporte es nivel operativo + corrección; restar un valor negativo aumentaría el nivel."},
                    {"Error observado": "Aplica otra vez el porcentaje a LAeq,T", "Orientación docente": "El aporte horario ya incluye el tiempo; la suma final utiliza sus energías directamente."},
                    {"Error observado": "Suma o promedia los dB", "Orientación docente": "Pide convertir cada aporte a energía, sumarlas y volver a decibeles."},
                    {"Error observado": "Elige por el mayor nivel operativo", "Orientación docente": "Pide ordenar los aportes de toda la hora. En este caso el martillo domina, pero debe justificarse por su aporte equivalente."},
                ]), use_container_width=True, hide_index=True,
            )
            st.markdown("#### 7 · Secuencia sugerida para acompañar al alumno")
            st.markdown(
                "1. Pide identificar T, el receptor y qué representa el nivel de entrada.\n"
                "2. Revisa la conversión a minutos antes de permitir avanzar a la corrección.\n"
                "3. Comprueba el signo de la corrección: debe ser ≤ 0; para el generador es 0.\n"
                "4. Pide explicar por qué el nivel operativo no cambia cuando se reduce el tiempo.\n"
                "5. Revisa la suma energética y pregunta si el total supera cada aporte individual.\n"
                "6. Solicita comparar martillo y excavadora antes de justificar la dominante.\n"
                "7. Usa las pistas de la comprobación para un segundo intento sin entregar la pauta al alumno."
            )


def _stage8(lab, saved):
    _header(
        8,
        "Caso integrador · modelación por etapas de una obra",
        "Integra trazabilidad, conversión, geometría y propagación en tres escenarios comparables de una obra de construcción."
    )

    st.markdown(
        """
        <style>
        .s8-hero{
            border:1px solid #cfe3ee;border-radius:24px;padding:24px 26px;
            background:linear-gradient(135deg,#eef8fc 0%,#ffffff 58%,#f5fbfd 100%);
            box-shadow:0 10px 28px rgba(23,59,83,.07);margin-bottom:.8rem;
        }
        .s8-eyebrow{font-size:.72rem;font-weight:900;letter-spacing:.11em;color:#087ba0;margin-bottom:.45rem}
        .s8-title{font-size:1.65rem;font-weight:900;color:#173b53;line-height:1.15;margin-bottom:.55rem}
        .s8-copy{color:#4d687a;line-height:1.65;font-size:.98rem}
        .s8-section{
            margin:1.4rem 0 .75rem;padding:13px 16px;border-radius:16px;
            background:linear-gradient(90deg,#173b53,#245d79);color:#fff;
            box-shadow:0 6px 18px rgba(23,59,83,.10);
        }
        .s8-section b{font-size:1.05rem}
        .s8-kpi{
            border:1px solid #d8e7ef;border-radius:18px;padding:15px 17px;
            background:#fff;min-height:105px;box-shadow:0 5px 16px rgba(23,59,83,.055)
        }
        .s8-kpi .n{font-size:1.45rem;font-weight:900;color:#087ba0}
        .s8-kpi .t{font-size:.83rem;color:#60798a;margin-top:.25rem}
        .s8-scenario{
            border:1px solid #d6e5ed;border-radius:20px;padding:18px 20px;
            background:linear-gradient(180deg,#ffffff,#f8fbfd);margin:.4rem 0 .8rem;
            box-shadow:0 7px 20px rgba(23,59,83,.055)
        }
        .s8-scenario-tag{font-size:.7rem;font-weight:900;letter-spacing:.08em;color:#087ba0}
        .s8-scenario-title{font-size:1.12rem;font-weight:850;color:#173b53;margin:.25rem 0 .25rem}
        .s8-scenario-copy{font-size:.9rem;color:#5b7485;line-height:1.5}
        .s8-note{
            border-left:4px solid #16a0bd;background:#f2fbfd;border-radius:12px;
            padding:12px 14px;color:#3f6173;margin:.55rem 0
        }
        .s8-final{
            border:1px solid #cde8dc;border-radius:20px;padding:18px 20px;
            background:linear-gradient(135deg,#f0fbf6,#ffffff);color:#315e49;
            box-shadow:0 6px 18px rgba(49,94,73,.06)
        }
        .s8-stepgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:.45rem 0 .8rem}
        .s8-step{
            border:1px solid #d8e5ec;border-radius:15px;padding:12px 11px;background:#fff;
            min-height:105px;box-shadow:0 4px 13px rgba(23,59,83,.045)
        }
        .s8-step .num{
            width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;
            background:#e9f7fb;color:#087ba0;font-weight:900;margin-bottom:.45rem
        }
        .s8-step .ttl{font-size:.83rem;font-weight:850;color:#173b53;margin-bottom:.2rem}
        .s8-step .txt{font-size:.76rem;line-height:1.35;color:#667d8c}
        .s8-model-flow{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:.35rem 0 .7rem}
        .s8-model-card{
            border:1px solid #d6e4ec;border-radius:18px;padding:16px 17px;background:#fff;
            box-shadow:0 5px 15px rgba(23,59,83,.05)
        }
        .s8-model-card .badge{font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0}
        .s8-model-card .head{font-size:1rem;font-weight:850;color:#173b53;margin:.25rem 0 .35rem}
        .s8-model-card .txt{font-size:.82rem;color:#60798a;line-height:1.45}
        .s8-analysis-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:.35rem 0 .8rem}
        .s8-analysis-card{
            border:1px solid #dbe7ed;border-radius:16px;padding:13px 14px;background:linear-gradient(180deg,#fff,#f9fcfd);
            min-height:110px
        }
        .s8-analysis-card .icon{font-size:1.1rem;margin-bottom:.25rem}
        .s8-analysis-card .ttl{font-size:.82rem;font-weight:850;color:#173b53;margin-bottom:.25rem}
        .s8-analysis-card .txt{font-size:.76rem;line-height:1.35;color:#687e8c}
        @media(max-width:850px){
            .s8-stepgrid,.s8-model-flow,.s8-analysis-grid{grid-template-columns:1fr}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="s8-hero">
          <div class="s8-eyebrow">CASO INTEGRADOR · ETAPA 8</div>
          <div class="s8-title">De los datos BS 5228 al mapa de ruido</div>
          <div class="s8-copy">
            Trabajarás como si prepararas una modelación acústica real: recibirás las fuentes,
            calcularás su potencia sonora, seleccionarás receptores y compararás tres momentos
            constructivos manteniendo una geometría común.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1,k2,k3,k4 = st.columns(4)
    for col, number, text_value in [
        (k1,"3","etapas constructivas"),
        (k2,"3","fuentes por escenario"),
        (k3,"3","receptores elegidos por ti"),
        (k4,"BS 5228","trazabilidad acústica"),
    ]:
        with col:
            st.markdown(
                f'<div class="s8-kpi"><div class="n">{number}</div><div class="t">{text_value}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Herramienta central · Noise Map Lab")
    tool_left, tool_right = st.columns([1.35, .65], gap="large")
    with tool_left:
        st.markdown(
            """
            <div class="s8-scenario">
              <div class="s8-scenario-tag">ANTES DE COMENZAR</div>
              <div class="s8-scenario-title">Conoce el modelador</div>
              <div class="s8-scenario-copy">
                Recorre la interfaz, identifica cómo se agregan fuentes y receptores y revisa
                dónde se configura la altura antes de abrir los escenarios del ejercicio.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tool_right:
        st.link_button(
            "🗺️ Conocer Noise Map Lab",
            NOISEMAP_URL,
            use_container_width=True,
            help="Abre la herramienta limpia, sin cargar un escenario del ejercicio.",
        )
        st.caption("Abre en otra pestaña y vuelve aquí para seguir la guía.")

    st.markdown("### 1 · Comprende el encargo")
    c1,c2 = st.columns([1.2,.8], gap="large")
    with c1:
        st.markdown(
            """
            <div class="s8-scenario">
              <div class="s8-scenario-tag">CASO DIDÁCTICO</div>
              <div class="s8-scenario-title">Obra de edificación en Santiago</div>
              <div class="s8-scenario-copy">
                El predio simplificado mide <b>50 × 40 m</b> y se presenta sobre el fondo
                cartográfico del <b>Parque Bicentenario de Cerrillos</b>. La ubicación funciona
                únicamente como soporte espacial para el ejercicio.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="s8-scenario">
              <div class="s8-scenario-tag">TU MISIÓN</div>
              <div class="s8-scenario-title">Comparar tres fases</div>
              <div class="s8-scenario-copy">
                A · Excavación<br>
                B · Obra gruesa en piso<br>
                C · Obra gruesa en altura
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="s8-note"><b>Importante:</b> no corresponde a una obra real ni a un expediente ambiental. '
        'La geometría, posiciones, alturas y simultaneidad son supuestos pedagógicos.</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Recupera lo trabajado antes: BS 5228 → Lp/Lw y espectro → propagación → suma energética → "
        "altura de fuente/receptor → representación espacial → lectura de resultados."
    )

    scenarios = {
        "A · Excavación y movimiento de tierras": [
            ("EX-01", "Excavadora hidráulica", 12.0, 21.0, 1.5),
            ("CF-01", "Cargador frontal", 28.0, 19.0, 1.5),
            ("CT-01", "Camión tolva articulado", 41.0, 10.0, 1.5),
        ],
        "B · Obra gruesa a nivel de piso": [
            ("MX-01", "Camión mixer", 9.0, 11.0, 1.5),
            ("BH-01", "Bomba de hormigón", 21.0, 17.0, 1.5),
            ("VI-01", "Vibrador de inmersión", 31.0, 23.0, 1.0),
        ],
        "C · Obra gruesa en altura": [
            ("BM-01", "Bomba + mixer a 5° piso", 10.0, 12.0, 1.5),
            ("VI-02", "Vibrador de inmersión", 29.0, 23.0, 15.0),
            ("GT-01", "Grúa torre", 34.0, 26.0, 24.0),
        ],
    }
    scenario_links = {
        "A · Excavación y movimiento de tierras": NOISEMAP_URL.rstrip("/") + "/?scenario=c3l1-s8-a",
        "B · Obra gruesa a nivel de piso": NOISEMAP_URL.rstrip("/") + "/?scenario=c3l1-s8-b",
        "C · Obra gruesa en altura": NOISEMAP_URL.rstrip("/") + "/?scenario=c3l1-s8-c",
    }
    scenario_meta = {
        "A · Excavación y movimiento de tierras": ("A","Excavación","Movimiento de tierras y retiro de material"),
        "B · Obra gruesa a nivel de piso": ("B","Obra gruesa · piso","Hormigonado y vibrado a nivel de terreno"),
        "C · Obra gruesa en altura": ("C","Obra gruesa · altura","Actividad distribuida entre terreno y pisos superiores"),
    }

    st.markdown("### 2 · Revisa las fuentes de cada escenario")
    st.markdown(
        "Los niveles provienen de **BS 5228-1:2009, Anexo C** y corresponden a condiciones de actividad específicas a 10 m."
    )

    for scenario_name, equipment in scenarios.items():
        code, short_title, desc = scenario_meta[scenario_name]
        with st.container(border=True):
            left,right = st.columns([1.45,.55], gap="large")
            with left:
                st.markdown(
                    f"""
                    <div class="s8-scenario-tag">ESCENARIO {code}</div>
                    <div class="s8-scenario-title">{short_title}</div>
                    <div class="s8-scenario-copy">{desc}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with right:
                st.link_button(
                    f"🗺️ Abrir escenario {code}",
                    scenario_links[scenario_name],
                    use_container_width=True,
                    help="Carga el predio, las posiciones y las alturas de las tres fuentes. El alumno debe ingresar los LwA calculados y seleccionar sus receptores.",
                )
            rows = []
            for sid, name, x, y, height in equipment:
                item = BS_PLANT[name]
                rows.append([
                    sid, name, item["activity"], f"{item['laeq10']:.0f}",
                    f"C.{item['table'].split('.')[-1]} · Ref. {item['ref']}",
                    f"{height:.1f}",
                ])
            st.dataframe(
                pd.DataFrame(
                    rows,
                    columns=["ID","Fuente","Actividad BS 5228","LAeq 10 m [dB(A)]","Referencia","Altura [m]"],
                ),
                hide_index=True,
                use_container_width=True,
            )
            st.caption(
                "Noise Map Lab carga la posición y altura de las fuentes y demarca el predio con líneas auxiliares. "
                "El área de cálculo no viene creada: debes dibujarla tú como parte del ejercicio, después de definir receptores e ingresar los LwA."
            )
            if code == "C":
                st.info("Las alturas de 15 m y 24 m son supuestos didácticos para estudiar propagación desde fuentes elevadas.")

    st.markdown("### 3 · Convierte los datos antes de modelar")
    eq1,eq2 = st.columns([.8,1.2], gap="large")
    with eq1:
        st.markdown(
            """
            <div class="s8-scenario">
              <div class="s8-scenario-tag">RELACIÓN DE TRABAJO</div>
              <div class="s8-scenario-title">De presión a potencia</div>
              <div class="s8-scenario-copy">
                Calcula tú mismo el LWA de cada fuente. No copies una respuesta ya resuelta:
                esta conversión forma parte del caso integrador.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with eq2:
        st.latex(r"L_{WA}\approx L_{Aeq,10m}+28\ \mathrm{dB}")
        st.caption(
            "LAeq,10m = presión sonora de la actividad a 10 m. · LWA = potencia sonora ponderada A estimada."
        )

    conversion_sources = []
    seen_sources = set()
    for equipment in scenarios.values():
        for _sid, name, _x, _y, _height in equipment:
            if name not in seen_sources:
                seen_sources.add(name)
                conversion_sources.append(name)

    stored_conversion = saved.get("c4l1_stage8_conversion_v4", {})
    with st.form("c4l1_s8_conversion_v4_form"):
        student_conversion = {}
        for index,name in enumerate(conversion_sources,1):
            item = BS_PLANT[name]
            with st.container(border=True):
                c1,c2,c3 = st.columns([1.45,.7,.85])
                with c1:
                    st.markdown(f"**{index:02d} · {name}**")
                    st.caption(f"Tabla {item['table']} · Ref. {item['ref']} · {item['activity']}")
                with c2:
                    st.metric("LAeq · 10 m", f"{item['laeq10']:.0f} dB(A)")
                with c3:
                    student_conversion[name] = st.number_input(
                        "LWA calculado",
                        value=stored_conversion.get(name),
                        step=.1,
                        format="%.1f",
                        key="c4l1_s8_conversion_" + name.replace(" ","_"),
                        placeholder="dB re 1 pW",
                    )
        conversion_method = st.text_area(
            "Explica brevemente tu procedimiento",
            value=saved.get("c4l1_stage8_conversion_method_v4",""),
            placeholder="Explica la relación utilizada, el significado del +28 dB y por qué LAeq a 10 m no es directamente LWA.",
            key="c4l1_s8_conversion_method_v4",
            height=105,
        )
        conversion_submit = st.form_submit_button("✓ Comprobar y guardar cálculos", use_container_width=True)

    if conversion_submit:
        missing = [name for name,value in student_conversion.items() if value is None]
        if missing:
            st.warning("Completa el LWA de todas las fuentes antes de comprobar.")
        else:
            incorrect = []
            for name,value in student_conversion.items():
                if abs(float(value)-(BS_PLANT[name]["laeq10"]+28.0)) > .2:
                    incorrect.append(name)
            if incorrect:
                st.warning("Revisa la conversión de: " + ", ".join(incorrect) + ".")
            elif len(conversion_method.strip()) < 60:
                st.warning("Los valores son correctos. Completa también la explicación con al menos 60 caracteres.")
            else:
                saved["c4l1_stage8_conversion_v4"] = dict(student_conversion)
                saved["c4l1_stage8_conversion_method_v4"] = conversion_method
                _save_stage_state(lab, saved, 8)
                st.success("Conversión correcta. Ya puedes continuar con la selección de receptores.")

    with st.expander("👨‍🏫 Pauta docente · respuestas de la conversión"):
        teacher_rows=[]
        for name in conversion_sources:
            item=BS_PLANT[name]
            teacher_rows.append([name,item["laeq10"],item["laeq10"]+28.0,item["table"],item["ref"]])
        st.dataframe(
            pd.DataFrame(
                teacher_rows,
                columns=["Fuente","LAeq 10 m [dB(A)]","LWA esperado [dB re 1 pW]","Tabla","Ref."],
            ),
            hide_index=True,use_container_width=True,
        )
        st.caption("Tolerancia sugerida: ±0,2 dB por redondeo.")

    st.markdown("### 4 · Selecciona tus receptores")
    st.markdown(
        """
        <div class="s8-stepgrid">
          <div class="s8-step"><div class="num">1</div><div class="ttl">Abre A · Excavación</div><div class="txt">Comienza con el escenario base ya cargado en Noise Map Lab.</div></div>
          <div class="s8-step"><div class="num">2</div><div class="ttl">Observa el entorno</div><div class="txt">Busca usos humanos expuestos fuera del predio de 50 × 40 m.</div></div>
          <div class="s8-step"><div class="num">3</div><div class="ttl">Elige 3 puntos</div><div class="txt">Selecciona receptores con distinta distancia y orientación respecto de la obra.</div></div>
          <div class="s8-step"><div class="num">4</div><div class="ttl">Define la altura</div><div class="txt">Incluye al menos un receptor bajo y, si corresponde, otro en altura.</div></div>
          <div class="s8-step"><div class="num">5</div><div class="ttl">Conserva la geometría</div><div class="txt">Usa exactamente R1, R2 y R3 en los escenarios B y C.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r1,r2,r3 = st.columns(3)
    for col,icon,title,copy in [
        (r1,"📍","R1 · Próximo","Punto de uso humano cercano al predio."),
        (r2,"↗️","R2 · Otra orientación","Punto ubicado en otro costado para comparar geometría."),
        (r3,"🏢","R3 · En altura","Punto de piso superior cuando el entorno lo permita."),
    ]:
        with col:
            st.markdown(
                f'<div class="s8-kpi"><div class="n" style="font-size:1.05rem">{icon} {title}</div><div class="t">{copy}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div class="s8-note"><b>Regla de comparación:</b> Noise Map Lab no precarga receptores ni el área de cálculo. '
        'Los receptores los defines una vez en A y los mantienes en B y C. Luego dibuja un área de cálculo que '
        'incluya el predio y los tres receptores, manteniendo una extensión equivalente en los tres escenarios.</div>',
        unsafe_allow_html=True,
    )

    receiver_record=saved.get("c4l1_stage8_receivers_v3",{})
    with st.form("c4l1_s8_receivers_v3_form"):
        st.markdown("#### Ficha de receptores")
        new_receivers={}
        for rid in ["R1","R2","R3"]:
            with st.container(border=True):
                c1,c2=st.columns([.72,.28])
                with c1:
                    desc=st.text_input(
                        f"{rid} · descripción",
                        value=receiver_record.get(rid,{}).get("description",""),
                        placeholder="Ej.: fachada residencial al norte del predio",
                        key=f"c4l1_s8_v3_desc_{rid}",
                    )
                with c2:
                    height_value=st.number_input(
                        f"{rid} · altura [m]",
                        min_value=.5,max_value=60.0,
                        value=float(receiver_record.get(rid,{}).get("height",1.5)),
                        step=.5,key=f"c4l1_s8_v3_h_{rid}",
                    )
                new_receivers[rid]={"description":desc,"height":height_value}
        receiver_note=st.text_area(
            "Justificación de la selección",
            value=saved.get("c4l1_stage8_receiver_note_v3",""),
            placeholder="Explica dónde ubicaste los receptores, por qué son representativos y cómo conservarás la misma geometría.",
            key="c4l1_s8_v3_receiver_note",
            height=105,
        )
        save_receivers=st.form_submit_button("✓ Guardar receptores",use_container_width=True)

    if save_receivers:
        if any(len(v["description"].strip())<10 for v in new_receivers.values()) or len(receiver_note.strip())<40:
            st.warning("Describe los tres receptores y justifica su ubicación con al menos 40 caracteres.")
        else:
            saved["c4l1_stage8_receivers_v3"]=new_receivers
            saved["c4l1_stage8_receiver_note_v3"]=receiver_note
            _save_stage_state(lab,saved,8)
            st.success("Receptores guardados. Utiliza exactamente esos mismos puntos en A, B y C.")

    st.markdown("### 5 · Modela las tres etapas")
    st.markdown(
        """
        <div class="s8-model-flow">
          <div class="s8-model-card">
            <div class="badge">ESCENARIO A</div>
            <div class="head">Excavación</div>
            <div class="txt">Abre el preset, ingresa los LwA, incorpora R1–R3 y dibuja el área de cálculo antes de ejecutar.</div>
          </div>
          <div class="s8-model-card">
            <div class="badge">ESCENARIO B</div>
            <div class="head">Obra gruesa · piso</div>
            <div class="txt">Carga la nueva fase, ingresa sus LwA, conserva R1–R3 y vuelve a definir un área de cálculo equivalente.</div>
          </div>
          <div class="s8-model-card">
            <div class="badge">ESCENARIO C</div>
            <div class="head">Obra gruesa · altura</div>
            <div class="txt">Ingresa los LwA, mantén R1–R3, dibuja el área de cálculo y analiza el efecto de la altura.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="s8-note">
          <b>Para que la comparación sea válida</b><br>
          Mantén constantes el método de cálculo, suelo, meteorología, área de cálculo y receptores.
          La variable que debe cambiar entre A, B y C es principalmente la <b>etapa constructiva y sus fuentes</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    check1,check2,check3,check4 = st.columns(4)
    for col,label,value in [
        (check1,"Método","igual"),
        (check2,"Suelo y meteo","igual"),
        (check3,"R1–R3","iguales"),
        (check4,"Fuentes","cambian por etapa"),
    ]:
        with col:
            st.metric(label,value)

    st.markdown("### 6 · Registra y compara los resultados")
    previous=saved.get("c4l1_stage8_results_v3",{})
    with st.form("c4l1_s8_results_v3_form"):
        results={}
        for scenario_key,scenario_label in [
            ("A","Excavación"),
            ("B","Obra gruesa en piso"),
            ("C","Obra gruesa en altura"),
        ]:
            with st.container(border=True):
                st.markdown(f"**{scenario_key} · {scenario_label}**")
                results[scenario_key]={}
                cols=st.columns(3)
                for col,rid in zip(cols,["R1","R2","R3"]):
                    with col:
                        results[scenario_key][rid]=st.number_input(
                            f"{rid} · dB(A)",
                            value=previous.get(scenario_key,{}).get(rid),
                            step=.1,format="%.1f",
                            key=f"c4l1_s8_v3_{scenario_key}_{rid}",
                            placeholder="Nivel total",
                        )
        model_note=st.text_area(
            "Configuración común de los tres modelos",
            value=saved.get("c4l1_stage8_model_note_v3",""),
            placeholder="Método, G, meteorología, alturas, criterio de colocación y nombres de los proyectos/capturas.",
            key="c4l1_s8_v3_model_note",
            height=105,
        )
        save_results=st.form_submit_button("✓ Guardar comparación",use_container_width=True)

    if save_results:
        flat=[results[s][r] for s in results for r in results[s]]
        if any(v is None for v in flat):
            st.warning("Completa los nueve niveles antes de guardar.")
        elif len(model_note.strip())<80:
            st.warning("Documenta la configuración común con al menos 80 caracteres.")
        else:
            saved["c4l1_stage8_results_v3"]=results
            saved["c4l1_stage8_model_note_v3"]=model_note
            _save_stage_state(lab,saved,8)
            st.success("Resultados guardados.")

    stored_results=saved.get("c4l1_stage8_results_v3",{})
    if stored_results:
        comparison=pd.DataFrame(
            [[rid,stored_results["A"][rid],stored_results["B"][rid],stored_results["C"][rid]]
             for rid in ["R1","R2","R3"]],
            columns=["Receptor","Excavación [dB(A)]","Obra gruesa · piso [dB(A)]","Obra gruesa · altura [dB(A)]"],
        )
        st.markdown("#### Comparación consolidada")
        st.dataframe(comparison,hide_index=True,use_container_width=True)
        cols=st.columns(3)
        for col,rid in zip(cols,["R1","R2","R3"]):
            values={
                "Excavación":stored_results["A"][rid],
                "Obra gruesa · piso":stored_results["B"][rid],
                "Obra gruesa · altura":stored_results["C"][rid],
            }
            stage=max(values,key=values.get)
            with col:
                st.metric(rid,f"{values[stage]:.1f} dB(A)",delta=stage,delta_color="off")

    st.markdown("### 7 · Interpreta lo que cambió")
    st.markdown(
        "Usa los resultados para construir una explicación técnica. No basta con indicar cuál número fue mayor."
    )
    st.markdown(
        """
        <div class="s8-analysis-grid">
          <div class="s8-analysis-card"><div class="icon">🔊</div><div class="ttl">Etapa dominante</div><div class="txt">Identifica qué fase produce el mayor nivel en cada receptor.</div></div>
          <div class="s8-analysis-card"><div class="icon">📏</div><div class="ttl">Distancia</div><div class="txt">Relaciona la separación fuente–receptor con los cambios observados.</div></div>
          <div class="s8-analysis-card"><div class="icon">↕️</div><div class="ttl">Altura</div><div class="txt">Explica cómo influye que algunas fuentes estén en pisos superiores.</div></div>
          <div class="s8-analysis-card"><div class="icon">Σ</div><div class="ttl">Contribución conjunta</div><div class="txt">Considera que el nivel total resulta de la suma energética de las fuentes.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="s8-note"><b>Pregunta guía:</b> ¿el receptor más cercano resulta siempre el más expuesto? '
        'Justifica tu respuesta utilizando la geometría y los niveles obtenidos.</div>',
        unsafe_allow_html=True,
    )

    analysis_saved=saved.get("c4l1_stage8_analysis_v3","")
    with st.form("c4l1_s8_analysis_v3_form"):
        analysis=st.text_area(
            "Conclusión técnica",
            value=analysis_saved,
            placeholder=(
                "Explica qué etapa produjo el mayor nivel en cada receptor, qué fuente parece dominar, "
                "cómo influyeron la distancia y la altura y por qué el receptor más cercano no necesariamente "
                "es el más expuesto en todos los escenarios."
            ),
            height=175,key="c4l1_s8_v3_analysis",
        )
        submit_analysis=st.form_submit_button("✓ Guardar conclusión",use_container_width=True)
    if submit_analysis:
        if not saved.get("c4l1_stage8_results_v3"):
            st.warning("Guarda primero los resultados de los tres escenarios.")
        elif len(analysis.strip())<140:
            st.warning("Desarrolla la conclusión con al menos 140 caracteres.")
        else:
            saved["c4l1_stage8_analysis_v3"]=analysis
            saved["c4l1_stage8_note"]=analysis
            _save_stage_state(lab,saved,8)
            st.success("Conclusión guardada.")

    st.markdown(
        """
        <div class="s8-final">
          <b>✓ Resultado esperado</b><br>
          Al terminar tendrás tres modelos comparables, tres receptores seleccionados y justificados,
          una tabla consolidada de niveles y una interpretación técnica de cómo cambia la exposición
          entre excavación, obra gruesa en piso y obra gruesa en altura.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("El control de ruido no forma parte de esta Etapa 8; se desarrollará en el Laboratorio 2.")

    with st.expander("👨‍🏫 Pauta docente · referencias BS 5228 y respuestas"):
        rows=[]
        for scenario_name,equipment in scenarios.items():
            for sid,name,x,y,height_value in equipment:
                item=BS_PLANT[name]
                rows.append([
                    scenario_name.split(" · ",1)[0],sid,name,item["activity"],item["laeq10"],
                    item["laeq10"]+28.0,item["table"],item["ref"],item["page"],height_value,
                ])
        st.dataframe(
            pd.DataFrame(
                rows,
                columns=[
                    "Escenario","ID","Fuente","Actividad","LAeq 10 m [dB(A)]",
                    "LWA esperado [dB]","Tabla","Ref.","Página","Altura didáctica [m]",
                ],
            ),
            hide_index=True,use_container_width=True,
        )
        st.caption(
            "Los niveles BS corresponden a registros específicos. Posiciones y alturas son didácticas. "
            "La aproximación +28 dB recupera el procedimiento trabajado previamente."
        )


def _stage9(lab, saved):
    _header(
        9,
        "Comprensión · cuestionario formativo",
        "Comprobar que el alumno comprende los conceptos trabajados durante la clase antes del ejercicio integrador final.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:20px;padding:20px 22px;
        background:linear-gradient(135deg,#fbfdff,#eef6ff)">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">EVALUACIÓN FORMATIVA</div>
          <div style="font-size:1.25rem;font-weight:900;color:#17324a;margin:.35rem 0">
            10 preguntas de comprensión
          </div>
          <div style="color:#586f82;line-height:1.55">
            Aplica lo visto en BS 5228, conversión Lp/Lw, geometría, propagación,
            suma energética, tiempo activo, receptores y lectura de modelos.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    questions = [
        (
            "BS 5228 entrega un LAeq,T a 10 m para una actividad concreta. ¿Qué debes evitar?",
            [
                "Usarlo como valor universal para toda máquina del mismo nombre",
                "Revisar tabla, referencia y actividad",
                "Identificar potencia y tamaño del equipo",
                "Distinguir LAeq,T de LAmax",
            ],
            0,
            "Los registros de BS 5228 corresponden a equipos y actividades concretas, no a un valor universal por nombre de máquina.",
        ),
        (
            "Si utilizas la aproximación didáctica trabajada en clase para registros estacionarios a 10 m, ¿cómo estimas LWA?",
            [
                "LWA = LAeq,10m − 28 dB",
                "LWA = LAeq,10m + 28 dB",
                "LWA = LAeq,10m + 3 dB",
                "LWA = LAeq,10m",
            ],
            1,
            "En este laboratorio se recupera la aproximación LWA ≈ LAeq,10m + 28 dB.",
        ),
        (
            "Dos fuentes de 70 dB(A) aportan lo mismo en un receptor y funcionan simultáneamente. El total será aproximadamente:",
            ["70 dB(A)", "73 dB(A)", "140 dB(A)", "67 dB(A)"],
            1,
            "Dos contribuciones iguales suman aproximadamente +3 dB, no se suman aritméticamente.",
        ),
        (
            "Una máquina opera el 25 % de un período de evaluación. ¿Qué corrección temporal aproximada representa?",
            ["0 dB", "−3 dB", "−6 dB", "+6 dB"],
            2,
            "10·log10(0,25) ≈ −6 dB.",
        ),
        (
            "Si duplicas la distancia fuente–receptor en campo libre, el término que cambia principalmente es:",
            ["Adiv", "Dc", "Lw", "Altura de la fuente"],
            0,
            "La divergencia geométrica aumenta con la distancia.",
        ),
        (
            "¿Por qué una fuente en altura puede cambiar el receptor crítico?",
            [
                "Porque aumenta automáticamente su Lw",
                "Porque cambia la geometría, línea de visión y distancia 3D respecto de receptores en distintos pisos",
                "Porque elimina Aatm",
                "Porque obliga a usar G = 1",
            ],
            1,
            "La altura modifica la relación geométrica fuente–receptor, no la potencia intrínseca de la fuente.",
        ),
        (
            "Si varias máquinas trabajan en una misma zona, ¿cuándo puede ser razonable representarlas como una fuente equivalente?",
            [
                "Siempre, sin justificar",
                "Cuando su frente de trabajo es compacto y la simplificación no altera de forma relevante la geometría respecto de los receptores",
                "Solo cuando tienen el mismo Lw",
                "Nunca",
            ],
            1,
            "Una fuente equivalente puede ser útil si la simplificación conserva el comportamiento espacial relevante.",
        ),
        (
            "¿Qué debes mantener igual para comparar correctamente dos etapas constructivas?",
            [
                "Solo el nombre del proyecto",
                "Receptores y criterios de cálculo, salvo la variable que se quiere comparar",
                "Todas las fuentes",
                "El resultado en dB",
            ],
            1,
            "Una comparación válida requiere conservar condiciones comunes y cambiar principalmente el escenario constructivo.",
        ),
        (
            "Un mapa muestra menor nivel en un receptor lejano, pero una fuente individual aporta más allí que otra fuente cercana. ¿Es posible?",
            [
                "No, la fuente más cercana siempre domina",
                "Sí, la contribución depende de Lw, distancia, altura, actividad y propagación",
                "No, porque todas las fuentes tienen el mismo Lw",
                "Solo si se suma dB aritméticamente",
            ],
            1,
            "La fuente dominante no depende únicamente de la distancia.",
        ),
        (
            "Para declarar cumplimiento frente a un criterio máximo, ¿qué debe coincidir entre resultado y límite?",
            [
                "Solo la unidad dB",
                "El descriptor, período de evaluación y ponderación aplicable",
                "Solo la distancia de 10 m",
                "El nombre de la fuente",
            ],
            1,
            "No es correcto comparar magnitudes con descriptores o períodos distintos.",
        ),
    ]

    answers=[]
    for i,(q,opts,correct,explanation) in enumerate(questions,1):
        with st.container(border=True):
            st.markdown(f"**{i}. {q}**")
            answers.append(
                st.radio(
                    "Selecciona una alternativa",
                    opts,
                    index=None,
                    key=f"c4l1_s9_q{i}",
                    label_visibility="collapsed",
                )
            )

    if st.button("Comprobar cuestionario",key="c4l1_s9_check",type="primary",use_container_width=True):
        if any(a is None for a in answers):
            st.warning("Responde las 10 preguntas antes de comprobar.")
        else:
            score=sum(1 for a,(_,opts,corr,_) in zip(answers,questions) if a==opts[corr])
            saved["c4l1_stage9_score"]=score
            _save_stage_state(lab,saved,9)
            c1,c2,c3=st.columns(3)
            c1.metric("Resultado",f"{score}/10")
            c2.metric("Porcentaje",f"{score*10}%")
            c3.metric("Referencia formativa","8/10")
            if score>=8:
                st.success("Buen dominio conceptual. Puedes continuar al caso integrador.")
            elif score>=6:
                st.warning("Base suficiente, pero conviene revisar las respuestas incorrectas antes de continuar.")
            else:
                st.error("Revisa las etapas anteriores antes de resolver el caso integrador final.")

            st.markdown("#### Retroalimentación")
            for i,(answer,(q,opts,corr,explanation)) in enumerate(zip(answers,questions),1):
                if answer==opts[corr]:
                    st.success(f"{i}. Correcta · {explanation}")
                else:
                    st.error(f"{i}. Revisa este concepto · {explanation}")

    with st.expander("👨‍🏫 Pauta docente · cuestionario"):
        teacher_rows=[]
        for i,(q,opts,corr,explanation) in enumerate(questions,1):
            teacher_rows.append([i,q,opts[corr],explanation])
        st.dataframe(
            pd.DataFrame(teacher_rows,columns=["N°","Pregunta","Respuesta esperada","Fundamento"]),
            hide_index=True,
            use_container_width=True,
        )


def _stage10(lab, saved):
    _header(
        10,
        "Caso integrador final · modelación y evaluación de cumplimiento",
        "Resolver un caso más abierto: buscar datos BS 5228, definir la estrategia de modelación, estimar niveles en receptores y evaluar criterios máximos.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:22px;padding:22px 24px;
        background:linear-gradient(135deg,#fbfdff,#eef6ff)">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">EJERCICIO INTEGRADOR FINAL</div>
          <div style="font-size:1.3rem;font-weight:900;color:#17324a;margin:.35rem 0">Tú defines cómo modelar la obra</div>
          <div style="color:#586f82;line-height:1.55">
            Esta vez no recibirás las fuentes armadas. Solo se entrega el predio y la lista de maquinaria.
            Deberás buscar los antecedentes acústicos, decidir cómo representar cada etapa, ubicar receptores,
            ejecutar la predicción y verificar si se cumplen los criterios del ejercicio.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · Abre el predio del caso")
    stage10_url = NOISEMAP_URL.rstrip("/") + "/?scenario=c3l1-s10"
    st.link_button(
        "🗺️ Abrir predio de la Etapa 10 en Noise Map Lab",
        stage10_url,
        use_container_width=True,
        help="Carga únicamente la demarcación del predio. Fuentes, receptores y área de cálculo los define el alumno.",
    )
    st.info(
        "El predio didáctico mide **70 × 55 m** y está demarcado con líneas auxiliares. "
        "No se entregan fuentes, receptores ni área de cálculo."
    )

    st.markdown("### 2 · Maquinaria disponible")
    st.markdown(
        "Busca en **BS 5228-1:2009, Anexo C** una referencia apropiada para cada equipo. "
        "Debes justificar la tabla y referencia seleccionada según la actividad representada."
    )
    machines=[
        "Excavadora hidráulica",
        "Camión tolva articulado",
        "Martillo hidráulico",
        "Camión mixer",
        "Bomba de hormigón",
        "Vibrador de inmersión",
        "Grúa torre",
    ]
    machine_phase={
        "Excavadora hidráulica":"Excavación y movimiento de tierras",
        "Camión tolva articulado":"Excavación y movimiento de tierras",
        "Martillo hidráulico":"Rotura localizada / preparación",
        "Camión mixer":"Hormigonado",
        "Bomba de hormigón":"Hormigonado",
        "Vibrador de inmersión":"Hormigonado / estructura",
        "Grúa torre":"Obra gruesa y trabajo en altura",
    }
    df_machines=pd.DataFrame(
        [[m,machine_phase[m]] for m in machines],
        columns=["Maquinaria","Actividad que debes representar"],
    )
    st.dataframe(df_machines,hide_index=True,use_container_width=True)

    st.markdown("### 3 · Recupera las referencias BS 5228")
    previous_bs=saved.get("c4l1_stage10_bs_v2",{})
    bs_entries={}
    with st.form("c4l1_s10_bs_v2_form"):
        for machine in machines:
            with st.container(border=True):
                st.markdown(f"**{machine}**")
                a,b,c1,d=st.columns([.8,.7,.9,.9])
                with a:
                    table=st.text_input(
                        "Tabla",
                        value=previous_bs.get(machine,{}).get("table",""),
                        placeholder="Ej. C.2",
                        key=f"c4l1_s10_table_{machine}",
                    )
                with b:
                    ref=st.text_input(
                        "Ref.",
                        value=previous_bs.get(machine,{}).get("ref",""),
                        placeholder="N°",
                        key=f"c4l1_s10_ref_{machine}",
                    )
                with c1:
                    lp10=st.number_input(
                        "Nivel a 10 m [dB(A)]",
                        value=previous_bs.get(machine,{}).get("lp10"),
                        step=.1,
                        format="%.1f",
                        key=f"c4l1_s10_lp10_{machine}",
                        placeholder="BS 5228",
                    )
                with d:
                    lwa=st.number_input(
                        "LWA estimado [dB]",
                        value=previous_bs.get(machine,{}).get("lwa"),
                        step=.1,
                        format="%.1f",
                        key=f"c4l1_s10_lwa_{machine}",
                        placeholder="Calcula",
                    )
                bs_entries[machine]={"table":table,"ref":ref,"lp10":lp10,"lwa":lwa}
        bs_justification=st.text_area(
            "Justifica brevemente cómo seleccionaste las referencias",
            value=saved.get("c4l1_stage10_bs_justification_v2",""),
            placeholder="Explica cómo verificaste actividad, equipo, descriptor y condición del registro.",
            height=110,
            key="c4l1_s10_bs_justification_v2",
        )
        bs_submit=st.form_submit_button("Guardar búsqueda BS 5228",use_container_width=True)

    if bs_submit:
        incomplete=[
            m for m,v in bs_entries.items()
            if not v["table"].strip() or not v["ref"].strip() or v["lp10"] is None or v["lwa"] is None
        ]
        if incomplete:
            st.warning("Completa tabla, referencia, nivel a 10 m y LWA para toda la maquinaria.")
        elif len(bs_justification.strip())<80:
            st.warning("Justifica la selección de referencias con al menos 80 caracteres.")
        else:
            saved["c4l1_stage10_bs_v2"]=bs_entries
            saved["c4l1_stage10_bs_justification_v2"]=bs_justification
            _save_stage_state(lab,saved,10)
            st.success("Antecedentes BS 5228 guardados.")

    st.markdown("### 4 · Define cómo representarás las etapas")
    st.markdown(
        "No existe una única representación correcta. Puedes modelar las máquinas como **fuentes individuales**, "
        "agrupar un frente compacto mediante una **fuente equivalente**, o utilizar una combinación de ambos enfoques. "
        "La decisión debe conservar una geometría acústicamente razonable."
    )

    strategy_saved=saved.get("c4l1_stage10_strategy_v2",{})
    with st.form("c4l1_s10_strategy_v2_form"):
        strategy={}
        for code,title in [
            ("A","Excavación / preparación"),
            ("B","Hormigonado a nivel de piso"),
            ("C","Obra gruesa en altura"),
        ]:
            with st.container(border=True):
                st.markdown(f"**{code} · {title}**")
                representation=st.radio(
                    "Representación",
                    ["Fuentes individuales","Fuente equivalente de frente","Modelo mixto"],
                    index=None if not strategy_saved.get(code,{}).get("representation") else
                        ["Fuentes individuales","Fuente equivalente de frente","Modelo mixto"].index(strategy_saved[code]["representation"]),
                    key=f"c4l1_s10_strategy_{code}",
                    horizontal=True,
                )
                justification=st.text_area(
                    "Justificación",
                    value=strategy_saved.get(code,{}).get("justification",""),
                    placeholder="Explica qué máquinas usarás, dónde las ubicarás o cómo construirás la fuente equivalente.",
                    key=f"c4l1_s10_strategy_note_{code}",
                    height=90,
                )
                strategy[code]={"representation":representation,"justification":justification}
        strategy_submit=st.form_submit_button("Guardar estrategia de modelación",use_container_width=True)

    if strategy_submit:
        if any(v["representation"] is None or len(v["justification"].strip())<60 for v in strategy.values()):
            st.warning("Selecciona una estrategia y justifica cada etapa con al menos 60 caracteres.")
        else:
            saved["c4l1_stage10_strategy_v2"]=strategy
            _save_stage_state(lab,saved,10)
            st.success("Estrategia de modelación guardada.")

    st.markdown("### 5 · Define los receptores y el descriptor de evaluación")
    st.markdown(
        "Selecciona tres receptores fuera del predio y documenta su posición y altura. "
        "Para este ejercicio, el resultado de cada escenario se interpretará como **LAeq,15 min** "
        "incorporando el porcentaje de tiempo activo que definas para las fuentes."
    )

    criteria=pd.DataFrame(
        [
            ["R1","Residencial",65.0,"LAeq,15 min"],
            ["R2","Oficina / comercio",70.0,"LAeq,15 min"],
            ["R3","Receptor sensible",60.0,"LAeq,15 min"],
        ],
        columns=["Receptor","Uso didáctico","Límite máximo [dB(A)]","Descriptor"],
    )
    st.dataframe(criteria,hide_index=True,use_container_width=True)
    st.warning(
        "Estos límites son **criterios didácticos del laboratorio** para practicar una evaluación de cumplimiento. "
        "No corresponden a límites regulatorios ni deben citarse como exigencia legal."
    )

    receiver_saved=saved.get("c4l1_stage10_receivers_v2",{})
    receiver_data={}
    with st.form("c4l1_s10_receivers_v2_form"):
        for rid,use_type,limit_value,_descriptor in criteria.itertuples(index=False,name=None):
            with st.container(border=True):
                c1,c2=st.columns([.72,.28])
                with c1:
                    description=st.text_input(
                        f"{rid} · {use_type} · ubicación",
                        value=receiver_saved.get(rid,{}).get("description",""),
                        placeholder="Describe dónde lo colocaste respecto del predio",
                        key=f"c4l1_s10_receiver_desc_{rid}",
                    )
                with c2:
                    height_value=st.number_input(
                        f"{rid} · altura [m]",
                        min_value=.5,max_value=60.0,
                        value=float(receiver_saved.get(rid,{}).get("height",1.5)),
                        step=.5,key=f"c4l1_s10_receiver_h_{rid}",
                    )
                receiver_data[rid]={"description":description,"height":height_value}
        receiver_submit=st.form_submit_button("Guardar receptores",use_container_width=True)

    if receiver_submit:
        if any(len(v["description"].strip())<20 for v in receiver_data.values()):
            st.warning("Describe con mayor precisión la ubicación de los tres receptores.")
        else:
            saved["c4l1_stage10_receivers_v2"]=receiver_data
            _save_stage_state(lab,saved,10)
            st.success("Receptores guardados.")

    st.markdown("### 6 · Modela y registra los resultados")
    st.markdown(
        "Construye los tres escenarios en Noise Map Lab. Mantén constantes los receptores y el área de cálculo. "
        "Puedes cambiar posiciones de maquinaria entre etapas cuando sea coherente con el frente de trabajo."
    )

    result_saved=saved.get("c4l1_stage10_results_v2",{})
    limit_map={"R1":65.0,"R2":70.0,"R3":60.0}
    scenario_labels={
        "A":"Excavación / preparación",
        "B":"Hormigonado a nivel de piso",
        "C":"Obra gruesa en altura",
    }
    results={}
    with st.form("c4l1_s10_results_v2_form"):
        for code,label in scenario_labels.items():
            with st.container(border=True):
                st.markdown(f"**{code} · {label}**")
                cols=st.columns(3)
                results[code]={}
                for col,rid in zip(cols,["R1","R2","R3"]):
                    with col:
                        results[code][rid]=st.number_input(
                            f"{rid} · LAeq,15 min [dB(A)]",
                            value=result_saved.get(code,{}).get(rid),
                            step=.1,
                            format="%.1f",
                            key=f"c4l1_s10_result_{code}_{rid}",
                            placeholder="Resultado del modelo",
                        )
        common_settings=st.text_area(
            "Configuración y supuestos comunes",
            value=saved.get("c4l1_stage10_common_settings_v2",""),
            placeholder="Área de cálculo, G, meteorología, alturas, tiempos activos, tratamiento de fuentes equivalentes y otros supuestos.",
            height=120,
            key="c4l1_s10_common_settings_v2",
        )
        result_submit=st.form_submit_button("Guardar y evaluar cumplimiento",use_container_width=True)

    if result_submit:
        flat=[results[s][r] for s in results for r in results[s]]
        if any(v is None for v in flat):
            st.warning("Completa los nueve resultados antes de evaluar.")
        elif len(common_settings.strip())<100:
            st.warning("Documenta la configuración y los supuestos con al menos 100 caracteres.")
        else:
            saved["c4l1_stage10_results_v2"]=results
            saved["c4l1_stage10_common_settings_v2"]=common_settings
            _save_stage_state(lab,saved,10)
            st.success("Resultados guardados y evaluación actualizada.")

    stored=saved.get("c4l1_stage10_results_v2",{})
    if stored:
        rows=[]
        for code,label in scenario_labels.items():
            for rid in ["R1","R2","R3"]:
                level=float(stored[code][rid])
                limit_value=limit_map[rid]
                rows.append([
                    code,
                    label,
                    rid,
                    level,
                    limit_value,
                    "Cumple" if level<=limit_value else "No cumple",
                    level-limit_value,
                ])
        compliance_df=pd.DataFrame(
            rows,
            columns=[
                "Etapa","Escenario","Receptor","LAeq,15 min [dB(A)]",
                "Límite [dB(A)]","Evaluación","Margen [dB]",
            ],
        )
        st.markdown("#### Evaluación de cumplimiento")
        st.dataframe(compliance_df,hide_index=True,use_container_width=True)

        failures=compliance_df[compliance_df["Evaluación"]=="No cumple"]
        if failures.empty:
            st.success("Todos los receptores cumplen los criterios didácticos en los tres escenarios.")
        else:
            st.error(
                f"Se identifican {len(failures)} combinaciones escenario–receptor que superan el criterio didáctico."
            )

    st.markdown("### 7 · Cierra el caso con una conclusión técnica")
    conclusion=st.text_area(
        "Conclusión integradora",
        value=saved.get("c4l1_stage10_conclusion_v2",""),
        height=220,
        key="c4l1_s10_conclusion_v2",
        placeholder=(
            "Explica qué etapa fue más crítica, qué receptor resultó más expuesto, qué fuentes o frentes dominaron, "
            "qué decisiones de modelación tomaste, qué escenarios cumplen o no y cuáles son las principales limitaciones del análisis."
        ),
    )
    if st.button("Guardar caso integrador final",key="c4l1_s10_save_v2",type="primary",use_container_width=True):
        if not saved.get("c4l1_stage10_results_v2"):
            st.warning("Guarda primero los resultados de los tres escenarios.")
        elif len(conclusion.strip())<220:
            st.warning("Desarrolla una conclusión técnica de al menos 220 caracteres.")
        else:
            saved["c4l1_stage10_conclusion_v2"]=conclusion
            _save_stage_state(lab,saved,10)
            st.success("Caso integrador final guardado.")

    with st.expander("👨‍🏫 Pauta docente · referencias y criterios de revisión"):
        teacher_rows=[]
        for machine in machines:
            item=BS_PLANT[machine]
            teacher_rows.append([
                machine,
                item["table"],
                item["ref"],
                item.get("metric","LAeq,T"),
                item["laeq10"],
                item["laeq10"]+28.0,
                item["activity"],
            ])
        st.dataframe(
            pd.DataFrame(
                teacher_rows,
                columns=["Maquinaria","Tabla","Ref.","Descriptor BS","Nivel a 10 m [dB(A)]","LWA didáctico [dB]","Actividad"],
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.markdown(
            "**Criterios de corrección:** trazabilidad correcta de la BS; coherencia entre actividad y referencia; "
            "conversión de nivel correctamente aplicada; estrategia espacial justificada; receptores representativos; "
            "descriptor LAeq,15 min consistente con el criterio; comparación de cumplimiento correctamente interpretada."
        )
        st.caption(
            "Se aceptan estrategias distintas —fuentes individuales, equivalentes o mixtas— si están técnicamente justificadas "
            "y permiten reconstruir el razonamiento del alumno."
        )



_STAGES = [
    _stage0, _stage1, _stage2, _stage3, _stage4, _stage5,
    _stage6, _stage7, _stage8, _stage9, _stage10,
]

def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage = max(0, min(int(stage), 10))
    return _STAGES[stage](lab, saved)
