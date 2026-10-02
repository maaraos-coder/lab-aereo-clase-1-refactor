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
        "Traducir equipos estacionarios y tránsito asociado a la obra a objetos acústicos coherentes antes de modelar en Noise Map Lab.",
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
            En este laboratorio utilizaremos <b>fuentes puntuales</b> para maquinaria localizada
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

    st.markdown("### 3 · ¿Qué objeto crearías en Noise Map Lab?")
    st.markdown(
        """
        <div style="border:1px solid #dce6ed;border-radius:18px;padding:15px 17px;background:#fff;margin:.3rem 0 .8rem">
          <div style="font-size:.8rem;font-weight:900;color:#17324a">CRITERIO DE DECISIÓN</div>
          <div style="font-size:.84rem;color:#637788;line-height:1.5;margin-top:.25rem">
            Primero identifica el fenómeno. Si es un <b>equipo operando desde una posición</b>, crea una fuente puntual.
            Si es <b>tránsito vial generado por la obra</b>, crea una fuente lineal CNOSSOS sobre la vía correspondiente.
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
        ("Cargador frontal que se desplaza entre dos puntos dentro del predio","Maquinaria móvil interna","Fuente puntual / escenario de posiciones",
         "No conviene tratarlo automáticamente como tráfico CNOSSOS. Puede representarse mediante posiciones o escenarios de operación según el objetivo del análisis."),
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
                ["Fuente puntual","Fuente lineal vial · CNOSSOS","Fuente puntual / escenario de posiciones"],
                index=None,
                key=f"c4l1_s5_rep_{i}",
                horizontal=True,
            )
            if choice:
                if choice==expected:
                    st.success(f"Correcto · {why}")
                else:
                    st.warning(f"Revisa · {why}")

    st.markdown("### 4 · Cuándo sí usar la fuente lineal CNOSSOS")
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
        "Puente hacia Noise Map Lab: **puntual = maquinaria localizada**; "
        "**lineal CNOSSOS = tránsito vial asociado a la obra**. Esta distinción evita usar un objeto correcto para el fenómeno equivocado."
    )


def _stage6(lab, saved):
    _header(
        6,
        "Diseño y control del ruido en una obra",
        "Seleccionar controles por jerarquía y usar la geometría de la obra para reducir el nivel en receptores sensibles.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e6ef;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#fbfdff,#f3f8fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.1em">DISEÑO ACÚSTICO DE OBRA</div>
          <div style="font-size:1.18rem;font-weight:850;color:#17324a;margin:.3rem 0">
            Controlar no es “poner una barrera”: es decidir dónde conviene actuar
          </div>
          <div style="color:#5d7183;line-height:1.55">
            Una solución eficaz puede reducir la emisión en la fuente, modificar la trayectoria
            o reorganizar espacialmente la obra. La mejor estrategia suele combinar más de un nivel de control.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · Jerarquía de control")
    hierarchy=[
        (
            "1 · CONTROL EN LA FUENTE",
            "Actuar antes de la propagación",
            ["Equipo menos ruidoso","Silenciador","Encierro","Semiencierro","Mantenimiento","Reducción de Lw"],
            "#eef6fb","#176b9b"
        ),
        (
            "2 · CONTROL EN LA TRAYECTORIA",
            "Modificar cómo viaja el sonido",
            ["Aumentar distancia","Cambiar orientación","Barreras","Aprovechar edificios/acopios","Reubicar instalaciones fijas"],
            "#fff7e9","#98651c"
        ),
        (
            "3 · CONTROL MEDIANTE PLANIFICACIÓN",
            "Modificar la organización espacial/temporal",
            ["Separar frentes ruidosos","Evitar concentrar fuentes junto al receptor","Elegir ubicaciones de equipos estacionarios"],
            "#f5f2fb","#65549a"
        ),
    ]
    hh='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.6rem 0 1rem">'
    for title,sub,items,bg,color in hierarchy:
        lis="".join(f'<li style="margin:.22rem 0">{x}</li>' for x in items)
        hh+=(
            f'<div style="border:1px solid #dce5eb;border-radius:18px;padding:16px;background:{bg}">'
            f'<div style="font-size:.72rem;font-weight:900;letter-spacing:.06em;color:{color}">{title}</div>'
            f'<div style="font-size:.9rem;font-weight:800;color:#334c5f;margin:.3rem 0 .45rem">{sub}</div>'
            f'<ul style="padding-left:1rem;margin:.2rem 0;color:#657684;font-size:.79rem;line-height:1.45">{lis}</ul>'
            f'</div>'
        )
    hh+='</div>'
    st.markdown(hh,unsafe_allow_html=True)

    st.info(
        "Orden de razonamiento: primero pregunta si puedes reducir Lw; después si puedes mejorar la trayectoria; "
        "finalmente organiza la obra para evitar escenarios innecesariamente desfavorables."
    )

    st.markdown("### 2 · Caso de diseño en planta")
    st.markdown(
        "**Situación:** debes ubicar un generador estacionario dentro de la obra. "
        "Existe una vivienda sensible al costado oriental. El generador tiene el mismo Lw en las tres alternativas; "
        "lo que cambia es la geometría y la presencia de un obstáculo."
    )

    position=st.radio(
        "Selecciona la ubicación del generador",
        ["A · Cerca del receptor","B · Zona central","C · Detrás del edificio auxiliar"],
        horizontal=True,
        key="c4l1_s6_location",
    )

    configs={
        "A · Cerca del receptor": dict(x=620,y=175,d=22,bar=0,desc="Muy próximo al receptor y sin obstáculo entre ambos."),
        "B · Zona central": dict(x=390,y=245,d=55,bar=0,desc="Mayor distancia, pero todavía con línea de visión directa."),
        "C · Detrás del edificio auxiliar": dict(x=185,y=265,d=92,bar=7,desc="Mayor distancia y con un edificio auxiliar usado como apantallamiento conceptual."),
    }
    cfg=configs[position]
    lw=105.0
    lp_free=lw-(20*math.log10(cfg["d"])+11)
    lp_final=lp_free-cfg["bar"]

    svg=f"""
    <div style="border:1px solid #d8e4ec;border-radius:20px;background:#fbfdff;padding:12px 14px;margin:.5rem 0 1rem">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:7px">
        <div style="font-size:.72rem;font-weight:900;color:#526a7e;letter-spacing:.08em">PLANTA · UBICACIÓN DEL GENERADOR</div>
        <div style="font-size:.73rem;font-weight:850;color:#176b9b">{position}</div>
      </div>
      <svg viewBox="0 0 900 410" width="100%" style="display:block">
        <rect x="0" y="0" width="900" height="410" rx="18" fill="#f7fafc"/>
        <rect x="55" y="50" width="610" height="315" rx="18" fill="#f0f4f6" stroke="#9cadb8" stroke-width="3"/>
        <text x="72" y="78" font-size="16" font-weight="800" fill="#607585">OBRA</text>

        <rect x="700" y="110" width="145" height="125" rx="12" fill="#f9efe9" stroke="#c99b7d" stroke-width="3"/>
        <text x="723" y="142" font-size="16" font-weight="900" fill="#8b5b3d">VIVIENDA</text>
        <circle cx="700" cy="175" r="8" fill="#b34f4f"/>
        <text x="712" y="180" font-size="13" font-weight="800" fill="#8b4545">R</text>

        <rect x="245" y="120" width="115" height="150" rx="9" fill="#b7c6d0" stroke="#718694" stroke-width="3"/>
        <text x="263" y="195" font-size="14" font-weight="900" fill="#445965">EDIFICIO</text>
        <text x="268" y="214" font-size="12" fill="#536b78">AUXILIAR</text>

        <circle cx="620" cy="175" r="18" fill="#d9e4eb"/><text x="611" y="181" font-size="13" font-weight="900" fill="#667784">A</text>
        <circle cx="390" cy="245" r="18" fill="#d9e4eb"/><text x="381" y="251" font-size="13" font-weight="900" fill="#667784">B</text>
        <circle cx="185" cy="265" r="18" fill="#d9e4eb"/><text x="176" y="271" font-size="13" font-weight="900" fill="#667784">C</text>

        <circle cx="{cfg['x']}" cy="{cfg['y']}" r="24" fill="#176b9b"/>
        <text x="{cfg['x']-11}" y="{cfg['y']+6}" font-size="17" font-weight="900" fill="#fff">G</text>
        <line x1="{cfg['x']}" y1="{cfg['y']}" x2="700" y2="175" stroke="#d9534f" stroke-width="3" stroke-dasharray="9 7"/>
      </svg>
    </div>
    """
    st.markdown(svg,unsafe_allow_html=True)

    m1,m2,m3,m4=st.columns(4)
    m1.metric("Lw generador",f"{lw:.0f} dB")
    m2.metric("Distancia al receptor",f"{cfg['d']} m")
    m3.metric("Control de trayectoria",f"{cfg['bar']} dB")
    m4.metric("Lp estimado",f"{lp_final:.1f} dB")

    st.markdown(
        f"**Lectura de la alternativa:** {cfg['desc']} "
        "El cálculo mostrado usa divergencia geométrica y, para la alternativa C, una reducción conceptual adicional por apantallamiento."
    )

    if position.startswith("A"):
        st.warning(
            "Ubicación desfavorable: la corta distancia domina. Antes de pensar en un tratamiento complejo, "
            "conviene revisar si el equipo puede alejarse del receptor."
        )
    elif position.startswith("B"):
        st.info(
            "La reubicación mejora el escenario por distancia, pero la trayectoria continúa directa. "
            "Todavía existe margen para orientar o apantallar."
        )
    else:
        st.success(
            "La alternativa combina planificación y trayectoria: mayor distancia y uso de un obstáculo existente. "
            "En un proyecto real la eficacia del apantallamiento debe calcularse con su geometría."
        )

    st.markdown("### 3 · Compara una medida en la fuente")
    source_red=st.slider(
        "Reducción adicional de Lw mediante selección/encierro/silenciador [dB]",
        0,20,0,1,
        key="c4l1_s6_source_red",
    )
    controlled=lp_final-source_red
    x1,x2,x3=st.columns(3)
    x1.metric("Lp por ubicación",f"{lp_final:.1f} dB")
    x2.metric("Reducción en fuente",f"{source_red} dB")
    x3.metric("Lp combinado",f"{controlled:.1f} dB")

    st.caption(
        "El ejercicio muestra por qué el diseño suele combinar decisiones: una buena ubicación puede reducir la necesidad "
        "de controles más costosos en la fuente o en la trayectoria."
    )


def _stage7(lab, saved):
    _header(
        7,
        "Ciclos de operación, simultaneidad y suma energética",
        "Convertir niveles instantáneos de maquinaria en aportes equivalentes del período y combinar varias fuentes de forma energética.",
    )

    st.markdown(
        """
        <div style="border:1px solid #d9e6ef;border-radius:22px;padding:20px 22px;
        background:linear-gradient(135deg,#fbfdff,#f3f8fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;color:#0b6ea8;letter-spacing:.1em">DEL INSTANTE AL PERÍODO DE EVALUACIÓN</div>
          <div style="font-size:1.16rem;font-weight:850;color:#17324a;margin:.3rem 0">
            Una obra no mantiene todas sus máquinas funcionando al 100 % todo el tiempo
          </div>
          <div style="color:#5d7183;line-height:1.55">
            Para representar un período debemos corregir cada fuente por su tiempo activo y después
            sumar energéticamente los aportes equivalentes.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1 · Ciclo de operación")
    with st.container(border=True):
        st.latex(r"\Delta L_t=10\log_{10}\left(\frac{t}{T}\right)")
        st.markdown(
            "**t** es el tiempo durante el cual la máquina está activa y **T** el período total de evaluación. "
            "Como t/T ≤ 1, la corrección temporal es cero o negativa."
        )

    duty_examples=[100,50,25,10]
    ex_cols=st.columns(4)
    for col,p in zip(ex_cols,duty_examples):
        corr=10*math.log10(p/100)
        col.metric(f"{p} % activo",f"{corr:.1f} dB",help="Corrección temporal respecto del nivel durante operación.")

    base=st.slider("Nivel durante operación [dB(A)]",60,110,80,key="c4l1_s7_base")
    pct=st.slider("Tiempo activo [%]",1,100,25,key="c4l1_s7_pct")
    corr=10*math.log10(pct/100)
    eq=base+corr
    c1,c2,c3=st.columns(3)
    c1.metric("Nivel operativo",f"{base:.1f} dB(A)")
    c2.metric("Corrección temporal",f"{corr:.1f} dB")
    c3.metric("Aporte equivalente",f"{eq:.1f} dB(A)")

    st.markdown("### 2 · Simultaneidad")
    st.markdown(
        "El porcentaje activo describe **cuánto tiempo aporta cada fuente al período**, pero no significa que todas "
        "funcionen simultáneamente en cada instante. Para un escenario real deben definirse ciclos y coincidencias "
        "de operación de forma coherente con la faena."
    )
    st.info(
        "Una fuente muy ruidosa que opera pocos minutos puede aportar menos energía al período que una fuente algo más silenciosa que funciona continuamente."
    )

    st.markdown("### 3 · Suma energética")
    with st.container(border=True):
        st.latex(r"L_{\Sigma}=10\log_{10}\left(\sum_i10^{L_i/10}\right)")
        st.markdown(
            "Los niveles equivalentes de cada fuente se convierten a energía, se suman y luego vuelven a expresarse en decibeles. "
            "**Nunca se suman los dB aritméticamente.**"
        )

    st.markdown("### 4 · Caso aplicado de obra")
    st.markdown(
        "Calcula primero el aporte equivalente de cada máquina en el período y luego la suma energética total."
    )

    case_data=[
        ("Excavadora",67.0,80),
        ("Mixer",64.0,30),
        ("Martillo",74.0,15),
        ("Generador",59.0,100),
    ]
    rows=[]
    for name,level,duty in case_data:
        dt=10*math.log10(duty/100)
        leq=level+dt
        rows.append([name,level,duty,dt,leq])

    df=pd.DataFrame(
        rows,
        columns=["Máquina","Nivel durante operación [dBA]","Tiempo activo [%]","ΔLt [dB]","Aporte equivalente [dBA]"]
    )
    st.dataframe(
        df.style.format({
            "Nivel durante operación [dBA]":"{:.1f}",
            "ΔLt [dB]":"{:.1f}",
            "Aporte equivalente [dBA]":"{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    eqs=[r[4] for r in rows]
    total=10*math.log10(sum(10**(v/10) for v in eqs))
    dominant_idx=max(range(len(rows)),key=lambda i:eqs[i])
    dominant=rows[dominant_idx]

    cards=st.columns(4)
    for col,row in zip(cards,rows):
        col.metric(row[0],f"{row[4]:.1f} dBA",delta=f"{row[3]:.1f} dB temporal")

    st.markdown("#### Suma del período")
    st.latex(
        r"L_{\Sigma}=10\log_{10}\left("
        + "+".join([f"10^{{{v:.1f}/10}}" for v in eqs])
        + r"\right)"
    )
    r1,r2,r3=st.columns(3)
    r1.metric("Nivel total del período",f"{total:.1f} dBA")
    r2.metric("Fuente dominante",dominant[0])
    r3.metric("Aporte dominante",f"{dominant[4]:.1f} dBA")

    st.success(
        f"En este período domina **{dominant[0]}**, con un aporte equivalente de **{dominant[4]:.1f} dBA**. "
        "La fuente dominante se identifica después de considerar el tiempo activo, no solo mirando el nivel instantáneo."
    )

    st.markdown("### 5 · Comprueba tu cálculo")
    answers=[]
    qcols=st.columns(2)
    with qcols[0]:
        ans_exc=st.number_input(
            "Aporte equivalente de Excavadora [dBA]",
            min_value=0.0,max_value=120.0,value=60.0,step=0.1,
            key="c4l1_s7_ans_exc"
        )
        ans_ham=st.number_input(
            "Aporte equivalente de Martillo [dBA]",
            min_value=0.0,max_value=120.0,value=60.0,step=0.1,
            key="c4l1_s7_ans_ham"
        )
    with qcols[1]:
        ans_total=st.number_input(
            "Nivel total del período [dBA]",
            min_value=0.0,max_value=120.0,value=60.0,step=0.1,
            key="c4l1_s7_ans_total"
        )
        ans_dom=st.selectbox(
            "¿Qué fuente domina el período?",
            ["Selecciona","Excavadora","Mixer","Martillo","Generador"],
            key="c4l1_s7_ans_dom"
        )

    if st.button("Comprobar caso aplicado",key="c4l1_s7_case_check",type="primary"):
        checks=[
            abs(ans_exc-rows[0][4])<=0.2,
            abs(ans_ham-rows[2][4])<=0.2,
            abs(ans_total-total)<=0.2,
            ans_dom==dominant[0],
        ]
        if all(checks):
            st.success("Correcto. Aplicaste la corrección temporal, la suma energética y la identificación de la fuente dominante.")
        else:
            msgs=[]
            if not checks[0]: msgs.append("revisa la Excavadora")
            if not checks[1]: msgs.append("revisa el Martillo")
            if not checks[2]: msgs.append("revisa la suma energética")
            if not checks[3]: msgs.append("revisa la fuente dominante")
            st.warning("Aún hay diferencias: " + ", ".join(msgs) + ".")

    if st.session_state.get("role")=="Docente":
        with st.expander("👩‍🏫 Pauta docente · Etapa 7",expanded=False):
            st.markdown(
                f"""
                **Resultados esperados**
                - Excavadora: {rows[0][4]:.1f} dBA equivalentes.
                - Mixer: {rows[1][4]:.1f} dBA equivalentes.
                - Martillo: {rows[2][4]:.1f} dBA equivalentes.
                - Generador: {rows[3][4]:.1f} dBA equivalentes.
                - Total: {total:.1f} dBA.
                - Fuente dominante del período: {dominant[0]}.
                """
            )
            st.info(
                "Conducción sugerida: compare primero el nivel instantáneo del Martillo con su aporte equivalente "
                "y haga que el alumno explique por qué la duración puede cambiar la fuente dominante."
            )


def _stage8(lab, saved):
    _header(
        8,
        "Caso profesional guiado · introducción a Noise Map Lab",
        "Presentar la herramienta de modelación y desarrollar por primera vez un caso profesional completo y guiado.",
    )
    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#fbfdff,#eef6ff)">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">PRESENTACIÓN DE LA HERRAMIENTA</div>
          <div style="font-size:1.25rem;font-weight:900;color:#17324a;margin:.35rem 0">Noise Map Lab</div>
          <div style="color:#586f82;line-height:1.55">
            A partir de esta etapa usaremos una herramienta educativa para integrar en un mismo escenario
            fuentes, receptores, espectros, suelo, barreras, controles y resultados espaciales.
          </div>
        </div>
        """,unsafe_allow_html=True
    )
    st.warning("La herramienta tiene fines educativos y no sustituye una implementación certificada ni una evaluación acústica formal.")

    st.markdown("### Qué reconocerás en la interfaz")
    ui_cards=[
        ("Fuente","Lw, espectro, altura, directividad, tiempo activo y control."),
        ("Receptor","Posición y altura donde se calcula el nivel."),
        ("Área de cálculo","Zona donde se construye el mapa de ruido."),
        ("Terreno","Factor G, topografía y geometría del escenario."),
        ("Barreras","Altura, posición y perfil fuente–barrera–receptor."),
        ("Resultados","Nivel por receptor, contribuciones y mapa espacial."),
    ]
    html='<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:1rem 0">'
    for title,desc in ui_cards:
        html+=f'<div style="border:1px solid #dce7f0;border-radius:16px;padding:15px;background:#fff"><div style="font-weight:850;color:#18324a">{title}</div><div style="font-size:.82rem;color:#64788b;margin-top:.3rem">{desc}</div></div>'
    html+='</div>'
    st.markdown(html,unsafe_allow_html=True)
    _model_button()

    st.markdown("### Caso profesional guiado")
    st.markdown(
        "**Situación:** obra de edificación con una excavadora hidráulica, un camión mixer y un martillo hidráulico. "
        "Existe un receptor residencial al norte del predio. El objetivo es construir el escenario, calcularlo e identificar "
        "qué fuente domina en el receptor."
    )
    case_df=pd.DataFrame([
        ["Excavadora hidráulica", "BS 5228 C.2 Ref. 19", "100 %", "1,5 m"],
        ["Camión mixer", "BS 5228 C.4 Ref. 20", "60 %", "1,5 m"],
        ["Martillo hidráulico", "BS 5228 C.1 Ref. 1", "25 %", "1,5 m"],
    ],columns=["Fuente","Referencia","Tiempo activo","Altura"])
    st.dataframe(case_df,use_container_width=True,hide_index=True)

    st.markdown(
        "1. Crea y renombra las tres fuentes.\n"
        "2. Ingresa el Lw o espectro trabajado en las etapas anteriores.\n"
        "3. Asigna los tiempos activos indicados.\n"
        "4. Define un receptor residencial y un área de cálculo.\n"
        "5. Configura el terreno del caso.\n"
        "6. Calcula y registra el nivel total y la contribución de cada fuente.\n"
        "7. Identifica la fuente dominante."
    )
    note=st.text_area(
        "Registro técnico del caso",
        value=saved.get("c4l1_stage8_note",""),
        key="c4l1_s8_note",
        placeholder="Nivel total, fuente dominante, condiciones principales y observaciones del escenario.",
        height=150,
    )
    if st.button("Guardar registro del caso",key="c4l1_s8_save",type="primary"):
        if len(note.strip())<80:
            st.warning("Desarrolla un registro técnico de al menos 80 caracteres.")
        else:
            saved["c4l1_stage8_note"]=note
            _save_stage_state(lab,saved,8)
            st.success("Registro guardado.")


def _stage9(lab, saved):
    _header(
        9,
        "Comprensión · interpretación de propagación y modelación",
        "Comprobar que el alumno comprende los conceptos antes del ejercicio integrador final.",
    )
    st.markdown(
        """
        <div style="border:1px solid #eadfc8;border-radius:20px;padding:20px 22px;background:linear-gradient(135deg,#fffaf3,#fff7e8)">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#9a6617">10 PREGUNTAS DE COMPRENSIÓN</div>
          <div style="font-size:1.2rem;font-weight:850;color:#4b3515;margin:.35rem 0">
            Interpreta, no memorices
          </div>
          <div style="color:#6d5a3b">Las preguntas combinan conceptos de fuente, propagación, suelo, barreras, meteorología, ciclos y simultaneidad.</div>
        </div>
        """,unsafe_allow_html=True
    )
    questions=[
        ("Una fuente mantiene el mismo Lw pero el receptor duplica su distancia. ¿Qué término cambia principalmente?",
         ["Dc","Adiv","Agr solamente","Tiempo activo"],1),
        ("¿Qué describe mejor G = 0?",
         ["Suelo duro/acústicamente reflectante","50 % de absorción","Fuente omnidireccional","Suelo totalmente poroso"],0),
        ("Aatm aumenta especialmente cuando:",
         ["Baja la potencia eléctrica del equipo","Aumentan distancia y frecuencia","G se hace 0","Q se hace 1"],1),
        ("Si una barrera no corta la línea de visión fuente–receptor:",
         ["Abar necesariamente es máxima","El apantallamiento puede ser pequeño o nulo","Cmet se duplica","Lw disminuye"],1),
        ("¿Qué diferencia a Cmet de Aatm?",
         ["Cmet es una corrección meteorológica de largo plazo; Aatm es absorción molecular","Son exactamente el mismo término","Cmet depende solo de G","Aatm solo se usa con barreras"],0),
        ("Una máquina funciona 25 % del período. La corrección temporal es aproximadamente:",
         ["0 dB","-3 dB","-6 dB","+6 dB"],2),
        ("Dos fuentes de 70 dB cada una funcionando simultáneamente producen aproximadamente:",
         ["70 dB","73 dB","140 dB","67 dB"],1),
        ("¿Cuál es el efecto conceptual de un control aplicado directamente a la fuente?",
         ["Reduce Lw antes de la propagación","Aumenta Adiv","Cambia automáticamente G","Elimina Cmet"],0),
        ("La fuente dominante en un receptor:",
         ["Siempre es la de mayor Lw","Puede depender de Lw, distancia, control y propagación","Siempre es la más cercana","Nunca cambia con el tiempo activo"],1),
        ("¿Por qué conviene revisar contribuciones individuales en un modelo?",
         ["Para identificar qué fuente explica mayor parte del nivel y orientar el control","Para sumar dB aritméticamente","Para eliminar la necesidad de receptores","Para reemplazar las mediciones"],0),
    ]
    answers=[]
    for i,(q,opts,correct) in enumerate(questions,1):
        answers.append(st.radio(f"{i}. {q}",opts,index=None,key=f"c4l1_s9_q{i}"))
    if st.button("Comprobar respuestas",key="c4l1_s9_check",type="primary",use_container_width=True):
        if any(a is None for a in answers):
            st.warning("Responde las 10 preguntas antes de comprobar.")
        else:
            score=sum(1 for a,(_,opts,corr) in zip(answers,questions) if a==opts[corr])
            st.metric("Resultado",f"{score}/10")
            if score>=8: st.success("Muy buen dominio conceptual. Puedes pasar al caso integrador.")
            elif score>=6: st.warning("Base suficiente, pero conviene revisar los conceptos que fallaste.")
            else: st.error("Revisa las etapas anteriores antes del caso integrador.")
            if st.session_state.get("role")=="Docente":
                st.caption("Pauta: "+", ".join(f"{i+1}:{q[1][q[2]]}" for i,q in enumerate(questions)))


def _stage10(lab, saved):
    _header(
        10,
        "Caso integrador · predicción profesional con Noise Map Lab",
        "Integrar caracterización de fuentes, propagación, simultaneidad, diagnóstico y control en un escenario completo.",
    )
    st.markdown(
        """
        <div style="border:1px solid #d9e7f3;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#fbfdff,#eef6ff)">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#0b6ea8">CASO FINAL</div>
          <div style="font-size:1.25rem;font-weight:900;color:#17324a;margin:.35rem 0">Predicción de ruido de una obra de construcción</div>
          <div style="color:#586f82;line-height:1.55">
            Construye el escenario completo, identifica el receptor y la fuente dominante, aplica una medida de control
            y documenta el cambio antes/después.
          </div>
        </div>
        """,unsafe_allow_html=True
    )
    _model_button()

    st.markdown("### Antecedentes del caso")
    st.markdown(
        "- Predio de obra: **60 × 45 m**.\n"
        "- Receptor R1: vivienda al norte del predio.\n"
        "- Receptor R2: oficina al este.\n"
        "- Fuentes: excavadora hidráulica, bomba de hormigón, martillo hidráulico y generador diésel.\n"
        "- Terreno: combinación de superficie dura y suelo poroso.\n"
        "- Debes representar al menos una medida de control técnicamente justificada."
    )
    st.markdown("### Tareas")
    checklist=[
        "Caractericé las cuatro fuentes con antecedente acústico trazable",
        "Definí Lw o espectro y altura de cada fuente",
        "Definí R1 y R2",
        "Configuré terreno y geometría",
        "Incorporé ciclos de operación",
        "Calculé el escenario inicial",
        "Identifiqué receptor crítico y fuente dominante",
        "Apliqué una medida de control",
        "Recalculé el escenario",
        "Comparé antes/después y declaré supuestos",
    ]
    checked=[st.checkbox(item,key=f"c4l1_s10_check_{i}") for i,item in enumerate(checklist)]
    before=st.number_input("Nivel receptor crítico antes [dB(A)]",30.0,120.0,70.0,0.1,key="c4l1_s10_before")
    after=st.number_input("Nivel receptor crítico después [dB(A)]",30.0,120.0,65.0,0.1,key="c4l1_s10_after")
    st.metric("Reducción obtenida",f"{before-after:.1f} dB")
    conclusion=st.text_area(
        "Conclusión técnica",
        value=saved.get("c4l1_stage10_conclusion",""),
        height=220,
        key="c4l1_s10_conclusion",
        placeholder="Fuente dominante, receptor crítico, términos relevantes, medida de control aplicada, reducción obtenida, supuestos y limitaciones.",
    )
    if st.button("Guardar caso integrador",key="c4l1_s10_save",type="primary",use_container_width=True):
        if not all(checked):
            st.warning("Completa la lista de verificación.")
        elif len(conclusion.strip())<180:
            st.warning("Desarrolla una conclusión técnica de al menos 180 caracteres.")
        else:
            saved["c4l1_stage10_conclusion"]=conclusion
            saved["c4l1_stage10_result"]={"before":before,"after":after,"reduction":before-after}
            _save_stage_state(lab,saved,10)
            st.success("Caso integrador guardado.")


_STAGES = [
    _stage0, _stage1, _stage2, _stage3, _stage4, _stage5,
    _stage6, _stage7, _stage8, _stage9, _stage10,
]

def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage = max(0, min(int(stage), 10))
    return _STAGES[stage](lab, saved)
