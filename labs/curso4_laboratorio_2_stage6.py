"""Etapa 6 · Curso 4 Laboratorio 2: diseño e implementación de medidas de control."""

MEASURE_OPTIONS=[
    "Seleccionar medida",
    "Barrera acústica perimetral",
    "Cierre de vanos",
    "Semiencierro",
    "Secuencialidad operacional",
    "Barrera trasladable IMIV",
    "Reemplazo / restricción de maquinaria",
]

FRONT_TEMPLATE=[
    {"Frente / condición":"Escenario 1 · Movimiento de tierra","Tipo de trabajo":"Nivel de suelo"},
    {"Frente / condición":"Escenario 2 · Obra gruesa suelo","Tipo de trabajo":"Nivel de suelo"},
    {"Frente / condición":"Escenario 2 · Obra gruesa altura","Tipo de trabajo":"En altura"},
    {"Frente / condición":"Escenario 2 · Urbanización","Tipo de trabajo":"Nivel de suelo"},
    {"Frente / condición":"Escenario 2 · Terminaciones","Tipo de trabajo":"En altura / interior"},
    {"Frente / condición":"Escenario 3 · Obras IMIV","Tipo de trabajo":"Vía pública"},
]


def _num(v):
    try:
        return float(str(v).replace(",",".").strip())
    except Exception:
        return None


def _scenario_key(front):
    s=str(front or "")
    if "Escenario 1" in s:
        return "Escenario 1"
    if "Escenario 2" in s:
        return "Escenario 2"
    if "Escenario 3" in s:
        return "Escenario 3"
    return s


def _original_maxima(saved):
    """Máximo modelado por escenario a partir de la Etapa 5 del alumno."""
    rows=saved.get("c4l2_s5_detailed_results") or []
    out={}
    for row in rows:
        laeq=_num(row.get("LAeq [dB(A)]"))
        if laeq is None:
            continue
        key=_scenario_key(row.get("Frente"))
        cur=out.get(key)
        if cur is None or laeq>cur["laeq"]:
            out[key]={
                "laeq":laeq,
                "receptor":str(row.get("Receptor") or ""),
            }
    return out


def _student_design_rows(saved):
    maxima=_original_maxima(saved)
    rows=[]
    for base in FRONT_TEMPLATE:
        key=_scenario_key(base["Frente / condición"])
        m=maxima.get(key,{})
        original=m.get("laeq")
        limit=65.0
        excess=(original-limit) if original is not None else None
        rows.append({
            "Frente / condición":base["Frente / condición"],
            "Tipo de trabajo":base["Tipo de trabajo"],
            "Receptor crítico":m.get("receptor") or "",
            "LAeq original [dB(A)]":original,
            "Límite [dB(A)]":limit,
            "Excedencia [dB]":round(excess,1) if excess is not None else None,
            "Medida seleccionada":"Seleccionar medida",
            "Justificación":"",
            "Proyecto controlado":"",
        })
    return rows


def _teacher_solution(st,pd):
    if st.session_state.get("role")!="Docente":
        return

    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                padding:17px 19px;background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.8rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        VISTA DOCENTE · SOLUCIÓN DE REFERENCIA · ADENDA 2
      </div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">
        Medidas de control comprometidas para la fase de construcción
      </div>
      <div style="color:#526f80;line-height:1.55">
        Esta solución se muestra solo al docente. La tabla de trabajo del alumno permanece sin medidas resueltas.
      </div>
    </div>
    """,unsafe_allow_html=True)

    rows=[
        {
            "Condición":"Frentes a nivel de suelo",
            "Medida":"Barrera acústica perimetral",
            "Configuración":"6 m hacia receptores / 2,4 m hacia sitios eriazos",
            "Material":"Densidad superficial ≥10 kg/m²; OSB 15 mm o equivalente",
            "Criterio":"Juntas entre paneles y unión al piso herméticas",
        },
        {
            "Condición":"Construcción en altura",
            "Medida":"Cierre de vanos",
            "Configuración":"Cubrir ventanas y sectores abiertos hacia el exterior",
            "Material":"Densidad superficial ≥10 kg/m²; OSB 15 mm o equivalente",
            "Criterio":"Confinar la emisión de obra gruesa y terminaciones",
        },
        {
            "Condición":"Losa de avance / maquinaria ruidosa",
            "Medida":"Semiencierro",
            "Configuración":"Mín. 2,4 × 2,4 × 2,4 m; cuatro caras",
            "Material":"OSB 15 mm + absorbente interior ≥50 mm",
            "Criterio":"Priorizar cercanía a receptores",
        },
        {
            "Condición":"Obras IMIV",
            "Medida":"Barrera acústica + gestión operacional",
            "Configuración":"Barrera 2,4 m en todo el contorno + barrera trasladable para cango",
            "Material":"Densidad superficial ≥10 kg/m²",
            "Criterio":"Uso secuencial: solo una maquinaria simultánea por frente",
        },
        {
            "Condición":"Obras IMIV",
            "Medida":"Restricción / reemplazo de maquinaria",
            "Configuración":"Camión mixer → betonera",
            "Material":"—",
            "Criterio":"Si se requiere camión mientras opera otra máquina, motor apagado",
        },
    ]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

    st.info(
        "La Adenda 2 mantiene el frente de trabajo a nivel de suelo para modelar con controles y evalúa "
        "los receptores a la altura crítica donde la barrera pierde efectividad; el frente en altura se extiende "
        "a toda la altura del edificio para representar la condición desfavorable."
    )

    with st.expander("👨‍🏫 Criterios de corrección",expanded=False):
        st.markdown("""
        - La medida debe ser **físicamente aplicable** al proceso constructivo.
        - No aceptar como control principal simplemente “alejar la máquina” si la tarea exige trabajar junto al receptor.
        - La barrera debe interrumpir la trayectoria fuente–receptor y mantener continuidad/hermeticidad.
        - Cierre de vanos y semiencierro corresponden a trabajos en altura, no a maquinaria móvil a nivel de suelo.
        - Para IMIV, la **secuencialidad** y el **reemplazo del mixer por betonera** forman parte de la solución documental.
        - El escenario original debe conservarse intacto para la comparación de la Etapa 7.
        """)


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]

    runtime["header"](
        "ETAPA 6 · LABORATORIO 2",
        "Diseña e implementa las medidas de control",
        "Seleccionar medidas técnicamente aplicables para los escenarios que presentan mayores niveles y construir una copia controlada del modelo sin modificar la condición original.",
        show_overview=False,
        duration_minutes=45,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
                background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        DEL DIAGNÓSTICO AL CONTROL
      </div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">
        No buscamos una medida “bonita”: buscamos una medida viable y acústicamente efectiva
      </div>
      <div style="color:#526f80;line-height:1.6">
        Recupera la condición original de la Etapa 5, identifica dónde existe mayor exposición sonora y
        selecciona una medida compatible con el tipo de trabajo. Luego duplica el escenario original en
        Noise Map Lab e implementa allí el control.
      </div>
    </div>
    """,unsafe_allow_html=True)

    _teacher_solution(st,pd)

    st.markdown("### 1 · Recupera el problema acústico")
    maxima=_original_maxima(saved)
    if maxima:
        problem=[]
        for sc,m in maxima.items():
            excess=m["laeq"]-65.0
            problem.append({
                "Escenario":sc,
                "Receptor crítico":m["receptor"],
                "Mayor LAeq [dB(A)]":round(m["laeq"],1),
                "Límite [dB(A)]":65,
                "Excedencia [dB]":round(excess,1),
                "Diagnóstico":"Requiere reducción" if excess>0 else "Cumple",
            })
        st.dataframe(pd.DataFrame(problem),hide_index=True,use_container_width=True)
    else:
        st.warning(
            "Aún no hay resultados guardados desde la Etapa 5. Puedes estudiar las medidas y preparar el diseño, "
            "pero para cuantificar la necesidad de control debes completar y guardar los LAeq originales."
        )

    st.markdown("### 2 · Conoce las familias de medidas")
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.5rem 0 1rem">
      <div style="border:1px solid #d7e5ec;border-radius:16px;padding:15px;background:#fbfdff">
        <b style="color:#173b53">🧱 Barrera acústica</b><br>
        <span style="color:#5b7484;font-size:.9rem">Interrumpe la propagación directa entre una fuente a nivel de suelo y el receptor.</span>
      </div>
      <div style="border:1px solid #d7e5ec;border-radius:16px;padding:15px;background:#fbfdff">
        <b style="color:#173b53">🪟 Cierre de vanos</b><br>
        <span style="color:#5b7484;font-size:.9rem">Confina trabajos ejecutados dentro del edificio, cubriendo aberturas hacia el exterior.</span>
      </div>
      <div style="border:1px solid #d7e5ec;border-radius:16px;padding:15px;background:#fbfdff">
        <b style="color:#173b53">📦 Semiencierro</b><br>
        <span style="color:#5b7484;font-size:.9rem">Rodea maquinaria ruidosa en losa de avance y combina masa con absorción interior.</span>
      </div>
      <div style="border:1px solid #d7e5ec;border-radius:16px;padding:15px;background:#fbfdff">
        <b style="color:#173b53">🔁 Gestión operacional</b><br>
        <span style="color:#5b7484;font-size:.9rem">Reduce simultaneidad, restringe equipos o reemplaza maquinaria cuando el proceso lo permite.</span>
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.info(
        "Una medida no es válida solo porque reduzca dB en teoría. También debe permitir ejecutar la actividad. "
        "Por ejemplo, no corresponde proponer simplemente alejar una excavadora si la excavación debe realizarse junto al deslinde."
    )

    st.markdown("### 3 · Selecciona la estrategia para cada frente")
    saved_rows=saved.get("c4l2_s6_control_design") or _student_design_rows(saved)
    design_df=runtime["_professional_grid"](
        pd.DataFrame(saved_rows),
        key="c4l2_s6_design_grid",
        widths={
            "Frente / condición":260,
            "Tipo de trabajo":150,
            "Receptor crítico":120,
            "LAeq original [dB(A)]":165,
            "Límite [dB(A)]":125,
            "Excedencia [dB]":135,
            "Medida seleccionada":235,
            "Justificación":340,
            "Proyecto controlado":235,
        },
        select_options={"Medida seleccionada":MEASURE_OPTIONS},
        numeric_columns=["LAeq original [dB(A)]","Límite [dB(A)]","Excedencia [dB]"],
        height=430,
        editable_columns=["Medida seleccionada","Justificación","Proyecto controlado"],
    )
    design_records=design_df.where(pd.notna(design_df),None).to_dict("records")

    st.caption(
        "Los niveles originales se recuperan de tu Etapa 5. Selecciona una medida, justifica por qué es aplicable "
        "y define el nombre del proyecto controlado que guardarás en Noise Map Lab."
    )

    st.markdown("### 4 · Configura una medida en detalle")
    labels=[str(r.get("Frente / condición") or "") for r in design_records]
    selected_front=st.selectbox("Frente a configurar",labels,key="c4l2_s6_front_detail")
    selected=next((r for r in design_records if str(r.get("Frente / condición"))==selected_front),{})
    measure=str(selected.get("Medida seleccionada") or "Seleccionar medida")

    cfg_saved=(saved.get("c4l2_s6_measure_config") or {}).get(selected_front,{})
    cfg={}

    if measure=="Barrera acústica perimetral":
        c1,c2,c3=st.columns(3)
        cfg["altura_m"]=c1.number_input("Altura de barrera [m]",min_value=0.5,max_value=12.0,
                                        value=float(cfg_saved.get("altura_m") or 2.4),step=.1,key="c4l2_s6_bar_height")
        cfg["longitud_m"]=c2.number_input("Longitud [m]",min_value=1.0,max_value=500.0,
                                          value=float(cfg_saved.get("longitud_m") or 20.0),step=1.0,key="c4l2_s6_bar_len")
        cfg["densidad_kgm2"]=c3.number_input("Densidad superficial [kg/m²]",min_value=1.0,max_value=100.0,
                                             value=float(cfg_saved.get("densidad_kgm2") or 10.0),step=1.0,key="c4l2_s6_bar_density")
        cfg["ubicacion"]=st.text_input("Ubicación / tramo protegido",value=str(cfg_saved.get("ubicacion") or ""),key="c4l2_s6_bar_location")
        st.caption("Verifica en el corte F–R que la barrera intercepte efectivamente la trayectoria de propagación.")

    elif measure=="Cierre de vanos":
        cfg["fachada"]=st.text_input("Fachada / vanos a cerrar",value=str(cfg_saved.get("fachada") or ""),key="c4l2_s6_vanos_face")
        cfg["densidad_kgm2"]=st.number_input("Densidad superficial mínima [kg/m²]",min_value=1.0,max_value=100.0,
                                             value=float(cfg_saved.get("densidad_kgm2") or 10.0),step=1.0,key="c4l2_s6_vanos_density")
        cfg["material"]=st.text_input("Material",value=str(cfg_saved.get("material") or "OSB 15 mm o equivalente"),key="c4l2_s6_vanos_material")

    elif measure=="Semiencierro":
        a,b,c,d=st.columns(4)
        cfg["largo_m"]=a.number_input("Largo [m]",min_value=.5,max_value=10.0,value=float(cfg_saved.get("largo_m") or 2.4),step=.1,key="c4l2_s6_semi_l")
        cfg["ancho_m"]=b.number_input("Ancho [m]",min_value=.5,max_value=10.0,value=float(cfg_saved.get("ancho_m") or 2.4),step=.1,key="c4l2_s6_semi_w")
        cfg["alto_m"]=c.number_input("Alto [m]",min_value=.5,max_value=10.0,value=float(cfg_saved.get("alto_m") or 2.4),step=.1,key="c4l2_s6_semi_h")
        cfg["absorbente_mm"]=d.number_input("Absorbente interior [mm]",min_value=0,max_value=200,value=int(cfg_saved.get("absorbente_mm") or 50),step=10,key="c4l2_s6_semi_abs")
        cfg["cara_abierta"]=st.selectbox("Cara abierta orientada hacia",["Seleccionar","Interior de obra","Lado opuesto al receptor","Otro"],key="c4l2_s6_semi_open")

    elif measure=="Secuencialidad operacional":
        cfg["simultaneas_antes"]=st.number_input("N° máquinas simultáneas en condición original",min_value=1,max_value=10,value=int(cfg_saved.get("simultaneas_antes") or 2),key="c4l2_s6_seq_before")
        cfg["simultaneas_despues"]=st.number_input("N° máquinas simultáneas después del control",min_value=1,max_value=10,value=int(cfg_saved.get("simultaneas_despues") or 1),key="c4l2_s6_seq_after")
        st.success("Para obras IMIV, la Adenda 2 establece solo una maquinaria operando simultáneamente por frente.")

    elif measure=="Barrera trasladable IMIV":
        cfg["altura_m"]=st.number_input("Altura [m]",min_value=.5,max_value=6.0,value=float(cfg_saved.get("altura_m") or 2.4),step=.1,key="c4l2_s6_imiv_h")
        cfg["densidad_kgm2"]=st.number_input("Densidad superficial [kg/m²]",min_value=1.0,max_value=100.0,value=float(cfg_saved.get("densidad_kgm2") or 10.0),step=1.0,key="c4l2_s6_imiv_d")
        cfg["fuente_protegida"]=st.text_input("Fuente a proteger",value=str(cfg_saved.get("fuente_protegida") or "Cango"),key="c4l2_s6_imiv_source")

    elif measure=="Reemplazo / restricción de maquinaria":
        cfg["equipo_original"]=st.text_input("Equipo original",value=str(cfg_saved.get("equipo_original") or ""),key="c4l2_s6_rep_old")
        cfg["equipo_reemplazo"]=st.text_input("Equipo de reemplazo",value=str(cfg_saved.get("equipo_reemplazo") or ""),key="c4l2_s6_rep_new")
        cfg["restriccion"]=st.text_area("Restricción operacional",value=str(cfg_saved.get("restriccion") or ""),key="c4l2_s6_rep_rule",height=90)

    else:
        st.info("Selecciona una medida en la tabla anterior para habilitar sus parámetros de configuración.")

    st.markdown("### 5 · Implementa una copia controlada en Noise Map Lab")
    st.markdown("""
    1. Abre el **proyecto original** correspondiente al frente.
    2. **Duplica / guarda con otro nombre** antes de modificarlo.
    3. Incorpora la medida seleccionada manteniendo fuentes, receptores y geometría original.
    4. Revisa visualmente la medida en planta y, si corresponde, en el **corte F–R**.
    5. Guarda el proyecto controlado. **No recalifiques todavía el resultado en esta etapa**: la comparación se realizará en la Etapa 7.
    """)
    st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)

    st.markdown("### 6 · Verificación antes de guardar")
    v1=st.checkbox("Conservé intacto el escenario original.",key="c4l2_s6_check_original")
    v2=st.checkbox("La medida es físicamente compatible con la actividad constructiva.",key="c4l2_s6_check_viable")
    v3=st.checkbox("La medida está correctamente ubicada respecto de la fuente y el receptor.",key="c4l2_s6_check_geometry")
    v4=st.checkbox("Guardé el escenario controlado con un nombre diferente.",key="c4l2_s6_check_copy")

    if st.button("✓ Guardar diseño de control",type="primary",use_container_width=True,key="c4l2_s6_save"):
        incomplete=[
            r for r in design_records
            if str(r.get("Medida seleccionada") or "")=="Seleccionar medida"
            or not str(r.get("Justificación") or "").strip()
            or not str(r.get("Proyecto controlado") or "").strip()
        ]
        if incomplete:
            st.warning("Completa medida, justificación y nombre del proyecto controlado para todos los frentes.")
        elif not all([v1,v2,v3,v4]):
            st.warning("Completa las cuatro verificaciones antes de guardar.")
        else:
            configs=dict(saved.get("c4l2_s6_measure_config") or {})
            if selected_front and measure!="Seleccionar medida":
                configs[selected_front]={"medida":measure,**cfg}
            saved["c4l2_s6_control_design"]=design_records
            saved["c4l2_s6_measure_config"]=configs
            saved["done_6"]=True
            runtime["_save"](lab,saved,6)
            st.success("Diseño de control guardado. La Etapa 7 comparará condición original y controlada.")
