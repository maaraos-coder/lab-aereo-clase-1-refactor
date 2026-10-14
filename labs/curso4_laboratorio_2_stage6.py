"""Etapa 6 · Curso 4 Laboratorio 2: diseño e implementación de medidas de control."""

MEASURE_OPTIONS=[
    "Seleccionar medida",
    "Barrera acústica",
    "Reducción directa",
    "Silenciador",
    "Encierro completo",
    "Semiencierro",
    "Encierro + silenciador",
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


def _teacher_reference_maxima():
    """Máximos de referencia de la condición original usados solo en vista Docente."""
    return {
        "Escenario 1":{"laeq":66.0,"receptor":"R02"},
        "Escenario 2":{"laeq":72.0,"receptor":"R02 / R06"},
        "Escenario 3":{"laeq":78.0,"receptor":"RIMIV05 / RIMIV06"},
    }


def _build_design_rows(maxima,limit=65.0):
    rows=[]
    for base in FRONT_TEMPLATE:
        key=_scenario_key(base["Frente / condición"])
        m=maxima.get(key,{})
        original=m.get("laeq")
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


def _student_design_rows(saved,limit=65.0):
    return _build_design_rows(_original_maxima(saved),limit)


def _teacher_design_rows(limit=65.0):
    return _build_design_rows(_teacher_reference_maxima(),limit)


def _strategy_editor(st,pd,rows,key):
    """Editor nativo y compacto para evitar grillas embebidas en blanco."""
    columns=[
        "Frente / condición","Tipo de trabajo","Receptor crítico",
        "LAeq original [dB(A)]","Límite [dB(A)]","Excedencia [dB]",
        "Medida seleccionada","Justificación","Proyecto controlado",
    ]
    frame=pd.DataFrame(rows)
    for column in columns:
        if column not in frame.columns:
            frame[column]=None
    frame=frame[columns]

    exceedances=pd.to_numeric(frame["Excedencia [dB]"],errors="coerce")
    critical=(exceedances>0).sum()
    maximum=exceedances.max()
    maximum_text=f"{maximum:.1f} dB" if pd.notna(maximum) else "—"

    st.markdown(
        """
        <style>
          div[data-testid="stDataEditor"] {
            border:1px solid #c8dbe7;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 8px 24px rgba(23,59,83,.07);
          }
          div[data-testid="stDataEditor"] [role="columnheader"] {
            background:#edf7fb;
            color:#173b53;
            font-weight:800;
          }
        </style>
        <div style="border:1px solid #cfe0ed;border-radius:18px;padding:17px 19px;
                    background:linear-gradient(135deg,#f9fcfe,#eef7fb);margin:.35rem 0 .8rem">
          <div style="font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
            MATRIZ DE DECISIÓN
          </div>
          <div style="font-size:1.03rem;font-weight:900;color:#173b53;margin:.25rem 0">
            Una estrategia trazable para cada frente
          </div>
          <div style="color:#526f80;line-height:1.5">
            Los datos acústicos vienen de la Etapa 5. Completa únicamente la medida,
            su justificación técnica y el nombre de la copia controlada.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    m1,m2,m3=st.columns(3)
    m1.metric("Frentes evaluados",len(frame))
    m2.metric("Con excedencia",int(critical))
    m3.metric("Excedencia máxima",maximum_text)

    edited=st.data_editor(
        frame,
        key=key,
        hide_index=True,
        use_container_width=True,
        height=max(300,46+42*len(frame)),
        disabled=[
            "Frente / condición","Tipo de trabajo","Receptor crítico",
            "LAeq original [dB(A)]","Límite [dB(A)]","Excedencia [dB]",
        ],
        column_config={
            "Frente / condición":st.column_config.TextColumn("Frente / condición",width="large"),
            "Tipo de trabajo":st.column_config.TextColumn("Trabajo",width="medium"),
            "Receptor crítico":st.column_config.TextColumn("Receptor",width="small"),
            "LAeq original [dB(A)]":st.column_config.NumberColumn("LAeq original",format="%.1f dB(A)",width="small"),
            "Límite [dB(A)]":st.column_config.NumberColumn("Límite",format="%.1f dB(A)",width="small"),
            "Excedencia [dB]":st.column_config.NumberColumn("Excedencia",format="%.1f dB",width="small"),
            "Medida seleccionada":st.column_config.SelectboxColumn(
                "Medida de control",options=MEASURE_OPTIONS,required=True,width="medium",
            ),
            "Justificación":st.column_config.TextColumn(
                "Justificación técnica",help="Explica por qué la medida es aplicable a este frente.",width="large",
            ),
            "Proyecto controlado":st.column_config.TextColumn(
                "Nombre de la copia controlada",width="medium",
            ),
        },
        num_rows="fixed",
    )
    configured=(edited["Medida seleccionada"].fillna("")!="Seleccionar medida").sum()
    st.caption(f"{int(configured)} de {len(frame)} frentes ya tienen una medida seleccionada.")
    return edited


def _teacher_solution(st,pd):
    if st.session_state.get("role")!="Docente":
        return

    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                padding:17px 19px;background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.8rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        VISTA DOCENTE · CRITERIOS DE DISEÑO
      </div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">
        No existe una única medida correcta
      </div>
      <div style="color:#526f80;line-height:1.55">
        El proyecto Eyzaguirre se utiliza únicamente como caso de referencia. El alumno debe proponer,
        dimensionar y justificar su propia estrategia de control a partir de la condición original modelada.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("#### Qué debe demostrar una buena propuesta")
    st.dataframe(
        pd.DataFrame([
            {"Criterio":"Problema identificado","Qué revisar":"La medida responde a la fuente, camino de transmisión y receptor crítico realmente modelados."},
            {"Criterio":"Viabilidad constructiva","Qué revisar":"La medida no impide ejecutar la actividad para la cual la maquinaria es necesaria."},
            {"Criterio":"Geometría","Qué revisar":"La posición, dimensiones y orientación son coherentes con la propagación F–R."},
            {"Criterio":"Desempeño acústico","Qué revisar":"El alumno fundamenta TL, IL o reducción esperada sin confundir estas magnitudes."},
            {"Criterio":"Trazabilidad","Qué revisar":"El escenario original se conserva y el controlado se guarda como una copia independiente."},
        ]),
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("👨‍🏫 Criterios de corrección",expanded=False):
        st.markdown("""
        - Aceptar soluciones distintas si están **bien fundamentadas**.
        - No exigir reproducir las medidas de la Adenda.
        - No aceptar “alejar la fuente” si el proceso obliga a trabajar en ese sector.
        - En barreras, revisar que realmente exista interrupción de la visual acústica F–R.
        - En encierros y semiencierros, revisar superficies, aberturas, orientación y hermeticidad.
        - Distinguir **TL del elemento**, **IL del tratamiento** y **reducción final en el receptor**.
        - La comparación cuantitativa definitiva se realizará en la Etapa 7.
        """)


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]

    runtime["header"](
        "ETAPA 6 · LABORATORIO 2",
        "Diseña e implementa las medidas de control",
        "Diseñar medidas de control propias a partir de la condición original, estimar su comportamiento acústico y construir una copia controlada del modelo sin modificar el escenario base.",
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
        Diseña una medida viable y calcula su comportamiento acústico
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
    reference_period=str(saved.get("c4l2_s5_reference_period") or "Diurno")
    reference_limit=_num(saved.get("c4l2_s5_reference_limit_db"))
    if reference_limit is None:
        reference_limit=50.0 if reference_period=="Nocturno" else 65.0
    st.info(
        f"Criterio recuperado de la Etapa 5: **periodo {reference_period.lower()} · "
        f"límite de {reference_limit:.0f} dB(A)**, utilizado como referencia normativa del laboratorio."
    )
    maxima=_original_maxima(saved)
    if maxima:
        problem=[]
        for sc,m in maxima.items():
            excess=m["laeq"]-reference_limit
            problem.append({
                "Escenario":sc,
                "Receptor crítico":m["receptor"],
                "Mayor LAeq [dB(A)]":round(m["laeq"],1),
                "Límite [dB(A)]":reference_limit,
                "Excedencia [dB]":round(excess,1),
                "Diagnóstico":"Sobre el límite" if excess>0 else "Bajo el límite",
            })
        st.dataframe(pd.DataFrame(problem),hide_index=True,use_container_width=True)
    else:
        st.warning(
            "Aún no hay resultados guardados desde la Etapa 5. Puedes estudiar las medidas y preparar el diseño, "
            "pero para cuantificar la necesidad de control debes completar y guardar los LAeq originales."
        )

    from labs import curso4_control_workshop as workshop
    from labs import curso4_control_models as control_model
    workshop.render_examples(st,pd)
    st.warning(
        "El proyecto Eyzaguirre es el caso de aplicación. Diseña y justifica tus propias medidas "
        "a partir de la Etapa 5; los ejemplos no constituyen una solución obligatoria del proyecto."
    )
    tl_config,tl_spectrum=workshop.render_tl_calculator(
        st,pd,"c4l2_s6_tl_material_v1",saved.get("c4l2_s6_tl_calculator")
    )
    if st.button("Guardar diseño del panel",key="c4l2_s6_tl_save"):
        saved["c4l2_s6_tl_calculator"]=tl_config
        runtime["_save"](lab,saved,6)
        st.success("Panel y espectro TL guardados para utilizarlos en el diseñador.")

    st.markdown("### 4 · Diseñador de tratamientos · igual que Noise Map Lab")
    st.markdown(
        "Configura geometría, seis superficies, Rw o TL por bandas, absorción interior y ventilación. "
        "El resultado se obtiene del balance energético y de la emisión de cada cara. "
        "Después aplica estos mismos parámetros al frente elegido en la sección 5."
    )
    study_cfg,study_results=workshop.render_designer(
        st,pd,"c4l2_s6_study_v3",saved.get("c4l2_s6_treatment_study"),suggested_tl=tl_spectrum
    )
    if st.button("Guardar cálculo de práctica",key="c4l2_s6_study_save"):
        saved["c4l2_s6_treatment_study"]=study_cfg
        saved["c4l2_s6_treatment_study_results"]=study_results
        runtime["_save"](lab,saved,6)
        st.success("Práctica y parámetros guardados.")

    role=st.session_state.get("role")
    is_teacher=role=="Docente"
    stage5_rows=saved.get("c4l2_s5_detailed_results") or []
    has_stage5_results=bool(saved.get("done_5")) and any(
        _num(r.get("LAeq [dB(A)]")) is not None for r in stage5_rows
    )

    if not is_teacher and not has_stage5_results:
        st.markdown("### 5 · Diseño aplicado al caso")
        st.warning(
            "Esta parte se habilita después de completar y guardar la **Etapa 5**. "
            "Todavía no existen resultados originales guardados para recuperar en esta vista."
        )
        st.info(
            "Vuelve a la Etapa 5, registra los resultados obtenidos en Noise Map Lab y presiona "
            "**Guardar resultados detallados**. Luego regresa a la Etapa 6."
        )
        return

    st.markdown("### 5 · Diseña la estrategia para cada frente")
    if is_teacher:
        saved_rows=saved.get("c4l2_s6_control_design") or _teacher_design_rows(reference_limit)
        design_grid_key="c4l2_s6_design_grid_teacher_v2"
    else:
        saved_rows=saved.get("c4l2_s6_control_design") or _student_design_rows(saved,reference_limit)
        design_grid_key="c4l2_s6_design_grid_student_v2"

    # Unify previously named barrier variants; unsupported choices require a new selection.
    saved_rows=[dict(row) for row in saved_rows]
    for row in saved_rows:
        original=_num(row.get("LAeq original [dB(A)]"))
        row["Límite [dB(A)]"]=reference_limit
        row["Excedencia [dB]"]=round(original-reference_limit,1) if original is not None else None
        previous=row.get("Medida seleccionada")
        if previous in ("Barrera acústica perimetral","Barrera trasladable IMIV"):
            row["Medida seleccionada"]="Barrera acústica"
        elif previous not in MEASURE_OPTIONS:
            row["Medida seleccionada"]="Seleccionar medida"

    design_df=_strategy_editor(st,pd,saved_rows,design_grid_key)
    design_records=design_df.where(pd.notna(design_df),None).to_dict("records")

    if is_teacher:
        st.caption(
            "Vista Docente: receptor crítico, LAeq y excedencia se recuperan de la solución de referencia de la Etapa 5. "
            "La medida, justificación y proyecto controlado quedan deliberadamente sin resolver."
        )
    else:
        st.caption(
            "Los niveles originales se recuperan de tu Etapa 5 guardada. Selecciona una medida, justifica por qué es aplicable "
            "y define el nombre del proyecto controlado que guardarás en Noise Map Lab."
        )

    st.markdown("### 6 · Configura tu medida en detalle")
    labels=[str(r.get("Frente / condición") or "") for r in design_records]
    selected_front=st.selectbox("Frente a configurar",labels,key="c4l2_s6_front_detail")
    selected=next((r for r in design_records if str(r.get("Frente / condición"))==selected_front),{})
    measure=str(selected.get("Medida seleccionada") or "Seleccionar medida")

    import hashlib
    prefix="c4l2_s6_applied_"+hashlib.sha1((str(role)+selected_front+measure).encode()).hexdigest()[:12]
    cfg_saved=(saved.get("c4l2_s6_measure_config") or {}).get(selected_front,{})
    if measure=="Barrera acústica" and cfg_saved.get("medida") in ("Barrera acústica perimetral","Barrera trasladable IMIV"):
        cfg_saved=dict(cfg_saved,medida=measure)
    if cfg_saved.get("medida")!=measure:
        cfg_saved={}
    cfg={}
    calc=None
    treatment_kinds={
        "Encierro completo":"enclosure","Semiencierro":"semi",
        "Encierro + silenciador":"enclosure_silencer","Silenciador":"silencer",
        "Reducción directa":"direct",
    }
    if measure in treatment_kinds:
        initial=cfg_saved.get("treatment") or control_model.default_treatment(treatment_kinds[measure])
        if st.button("Usar parámetros de la práctica",key=prefix+"_copy"):
            if study_cfg["noise_control_type"]!=treatment_kinds[measure]:
                st.warning("Selecciona en la práctica el mismo tipo de tratamiento que elegiste para este frente.")
            else:
                configs=dict(saved.get("c4l2_s6_measure_config") or {})
                configs[selected_front]={"medida":measure,"treatment":study_cfg}
                saved["c4l2_s6_measure_config"]=configs
                for key in list(st.session_state):
                    if str(key).startswith(prefix): del st.session_state[key]
                runtime["_save"](lab,saved,6)
                st.rerun()
        treatment,calc=workshop.render_designer(
            st,pd,prefix,initial,fixed_kind=treatment_kinds[measure],suggested_tl=tl_spectrum
        )
        cfg["treatment"]=treatment
    elif measure=="Barrera acústica":
        cfg,calc=workshop.render_barrier_calculator(st,pd,prefix,cfg_saved)
        cfg["ubicacion"]=st.text_input("Ubicación / tramo protegido",value=str(cfg_saved.get("ubicacion") or ""),key=prefix+"_location")
        cfg["densidad_kgm2"]=st.number_input("Masa superficial del panel [kg/m²]",min_value=1.,max_value=200.,value=float(cfg_saved.get("densidad_kgm2",10.)),step=1.,key=prefix+"_mass")
    else:
        st.info("Selecciona una medida en la tabla anterior para habilitar su cálculo y configuración.")
    if measure!="Seleccionar medida":
        cfg["calculo"]=calc
        st.caption("El cálculo ilustrativo de esta sección no reemplaza los resultados controlados del proyecto. La comparación completa del caso se realiza en la Etapa 7.")
        if st.button("Guardar parámetros y cálculo de este frente",key=prefix+"_save_front"):
            if calc is None:
                st.warning("Corrige los parámetros para obtener un cálculo válido antes de guardarlo.")
            else:
                configs=dict(saved.get("c4l2_s6_measure_config") or {})
                configs[selected_front]={"medida":measure,**cfg}
                saved["c4l2_s6_control_design"]=design_records
                saved["c4l2_s6_measure_config"]=configs
                runtime["_save"](lab,saved,6)
                st.success("Parámetros y cálculo de este frente guardados. Puedes configurar otro frente.")

    st.markdown("### 7 · Implementa una copia controlada en Noise Map Lab")
    st.markdown("""
    1. Abre el **proyecto original** correspondiente al frente.
    2. **Duplica / guarda con otro nombre** antes de modificarlo.
    3. Incorpora la medida seleccionada manteniendo fuentes, receptores y geometría original.
    4. Revisa visualmente la medida en planta y, si corresponde, en el **corte F–R**.
    5. Guarda el proyecto controlado. **No recalifiques todavía el resultado en esta etapa**: la comparación se realizará en la Etapa 7.
    """)
    st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)

    from labs.curso4_lab2_maps import render_uploader
    render_uploader(
        st,saved,runtime,lab,
        group="control",
        title="8 · Adjunta los mapas con las medidas implementadas",
        description=(
            "Sube capturas donde se observe la ubicación y geometría de la barrera, encierro, semiencierro o silenciador "
            "incorporado. Si la medida tiene orientación o aberturas, agrega también una vista de corte."
        ),
        stage=6,
        key="c4l2_s6_control_maps",
    )

    st.markdown("### 9 · Verificación antes de guardar")
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
            if selected_front and measure!="Seleccionar medida" and calc is not None:
                configs[selected_front]={"medida":measure,**cfg}
            saved["c4l2_s6_control_design"]=design_records
            saved["c4l2_s6_measure_config"]=configs
            saved["done_6"]=True
            runtime["_save"](lab,saved,6)
            st.success("Diseño de control guardado. La Etapa 7 comparará tu condición original con la solución que diseñaste.")
