"""Etapa 6 · Curso 4 Laboratorio 2: diseño e implementación de medidas de control."""

from copy import deepcopy
from labs.curso4_lab2_control_scope import render_scope, validate_scope

MEASURE_OPTIONS=[
    "Seleccionar medida",
    "Combinación de medidas",
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


def _build_design_rows(maxima,limit=65.0,fronts=None):
    rows=[]
    for base in (FRONT_TEMPLATE if fronts is None else fronts):
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
    names=list(dict.fromkeys(str(source.get("Etapa") or "").strip()
        for source in (saved.get("c4l2_s3_acoustic_sources") or []) if str(source.get("Etapa") or "").strip()))
    types={row["Frente / condición"]:row["Tipo de trabajo"] for row in FRONT_TEMPLATE}
    fronts=[{"Frente / condición":name,"Tipo de trabajo":types.get(name,"Según actividad registrada")} for name in names]
    return _build_design_rows(_original_maxima(saved),limit,fronts=fronts or None)


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
            su justificación técnica y el nombre de la copia controlada. La aplicación por máquina se configura en la sección 6.
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
                "Estrategia general",options=MEASURE_OPTIONS,required=True,width="medium",
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
        "Después asigna los parámetros a las máquinas concretas del frente elegido. La práctica no aplica automáticamente una reducción al frente completo."
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
        from labs.curso4_lab2_drafts import render_draft_save
        render_draft_save(st,saved,runtime,lab,6,{
            "c4l2_s6_tl_calculator":tl_config,
            "c4l2_s6_treatment_study":study_cfg,
            "c4l2_s6_treatment_study_results":study_results,
        },"c4l2_s6_save_draft")
        return

    st.markdown("### 5 · Diseña la estrategia para cada frente")
    st.info("El frente agrupa máquinas para representar su emisión conjunta. Un tratamiento de fuente actúa solo sobre las máquinas y unidades que selecciones; una barrera actúa sobre el camino hacia el receptor. Elige Combinación de medidas si tu estrategia usa tratamientos distintos.")
    st.markdown("**Ejemplo de procedimiento:** si se encierra solo el minicargador, la excavadora y la retroexcavadora conservan su emisión original. El frente controlado se obtiene sumando energéticamente las tres contribuciones resultantes, no restando el aislamiento del encierro al total del frente.")
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
    prefix="c4l2_s6_scope_"+hashlib.sha1((str(role)+selected_front).encode()).hexdigest()[:12]
    cfg_saved=st.session_state.get(prefix+"_work") or (saved.get("c4l2_s6_measure_config") or {}).get(selected_front,{})
    cfg=render_scope(st,pd,saved,selected_front,measure,cfg_saved,prefix,workshop,study_cfg,tl_spectrum)
    st.session_state[prefix+"_work"]=deepcopy(cfg)
    if st.button("Guardar aplicaciones y cálculo de este frente",key=prefix+"_save_front"):
        try:
            validate_scope(saved,selected_front,cfg)
        except ValueError as error:
            st.warning(str(error)+" Puedes conservar el diseño incompleto con Guardar avance.")
        else:
            candidate=deepcopy(saved)
            candidate["c4l2_s6_control_design"]=design_records
            candidate["c4l2_s6_measure_config"]={**(saved.get("c4l2_s6_measure_config") or {}),selected_front:cfg}
            candidate["done_6"]=False
            try:
                runtime["_save"](lab,candidate,6)
            except Exception:
                st.error("No se pudo guardar la aplicación. Revisa la conexión y vuelve a intentarlo.")
            else:
                saved.update(candidate)
                st.success("Aplicaciones por máquina y balance del frente guardados. Puedes configurar otro frente.")

    st.markdown("### 7 · Implementa una copia controlada en Noise Map Lab")
    st.markdown("""
    1. Abre el **proyecto original** correspondiente al frente.
    2. **Duplica / guarda con otro nombre** antes de modificarlo.
    3. Aplica cada tratamiento únicamente a las máquinas y unidades identificadas. Conserva la emisión de las demás y recompón energéticamente el frente; no restes la atenuación de una máquina a todo el conjunto.
    4. Para barreras, encierros o semiencierros con efecto direccional, representa las máquinas por separado cuando sus posiciones, alturas u orientaciones importen. Verifica qué caminos quedan protegidos. No apliques la medida otra vez a un espectro que ya la incorpora.
    5. Conserva fuentes, receptores y geometría originales para comparar. Si necesitas desagregar una fuente equivalente, construye también una copia original desagregada y comprueba su comparabilidad antes de atribuir la diferencia al control.
    6. Revisa visualmente la medida en planta y, si corresponde, en el **corte F–R**.
    7. Guarda el proyecto controlado. **No recalifiques todavía el resultado en esta etapa**: la comparación se realizará en la Etapa 7.
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
    saved_checks=saved.get("c4l2_s6_checks") or {}
    v1=st.checkbox("Conservé intacto el escenario original.",value=bool(saved_checks.get("original")),key="c4l2_s6_check_original")
    v2=st.checkbox("La medida es físicamente compatible con la actividad constructiva.",value=bool(saved_checks.get("viable")),key="c4l2_s6_check_viable")
    v3=st.checkbox("La medida está correctamente ubicada respecto de la fuente y el receptor.",value=bool(saved_checks.get("geometry")),key="c4l2_s6_check_geometry")
    v4=st.checkbox("Guardé el escenario controlado con un nombre diferente.",value=bool(saved_checks.get("copy")),key="c4l2_s6_check_copy")

    configs=dict(saved.get("c4l2_s6_measure_config") or {})
    for row in design_records:
        front=str(row.get("Frente / condición") or "")
        work_key="c4l2_s6_scope_"+hashlib.sha1((str(role)+front).encode()).hexdigest()[:12]+"_work"
        if work_key in st.session_state:
            configs[front]=deepcopy(st.session_state[work_key])
    if selected_front:
        configs[selected_front]=cfg
    from labs.curso4_lab2_drafts import render_draft_save
    draft_updates={
        "c4l2_s6_tl_calculator":tl_config,
        "c4l2_s6_treatment_study":study_cfg,
        "c4l2_s6_treatment_study_results":study_results,
        "c4l2_s6_control_design":design_records,
        "c4l2_s6_measure_config":configs,
        "c4l2_s6_checks":{"original":v1,"viable":v2,"geometry":v3,"copy":v4},
    }
    if design_records!=saved.get("c4l2_s6_control_design") or configs!=saved.get("c4l2_s6_measure_config"):
        draft_updates["done_6"]=False
    render_draft_save(st,saved,runtime,lab,6,draft_updates,"c4l2_s6_save_draft")

    if st.button("✓ Validar y finalizar la Etapa 6",type="primary",use_container_width=True,key="c4l2_s6_save"):
        incomplete=[r for r in design_records
            if str(r.get("Medida seleccionada") or "") in ("", "Seleccionar medida")
            or not str(r.get("Justificación") or "").strip()
            or not str(r.get("Proyecto controlado") or "").strip()]
        errors=[]
        for row in design_records:
            front=str(row.get("Frente / condición") or "")
            configuration=configs.get(front,{})
            try:
                if configuration.get("medida") != row.get("Medida seleccionada"):
                    raise ValueError("Revisa las aplicaciones de la estrategia seleccionada.")
                validate_scope(saved,front,configuration)
            except ValueError as error:
                errors.append(f"{front}: {error}")
        if incomplete:
            st.warning("Completa estrategia, justificación y nombre del proyecto controlado para todos los frentes.")
        elif errors:
            for error in errors: st.warning(error)
        elif not all([v1,v2,v3,v4]):
            st.warning("Completa las cuatro verificaciones antes de guardar.")
        else:
            candidate=deepcopy(saved)
            candidate.update({"c4l2_s6_control_design":design_records,
                "c4l2_s6_measure_config":configs,
                "c4l2_s6_checks":{"original":v1,"viable":v2,"geometry":v3,"copy":v4},
                "done_6":True})
            try:
                runtime["_save"](lab,candidate,6)
            except Exception:
                st.error("No se pudo guardar el diseño. Revisa la conexión y vuelve a intentarlo.")
            else:
                saved.update(candidate)
                st.success("Diseño por máquinas y propagación guardado. La Etapa 7 comparará los escenarios modelados.")
