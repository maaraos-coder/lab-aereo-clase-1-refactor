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
