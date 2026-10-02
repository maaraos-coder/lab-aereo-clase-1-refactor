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
