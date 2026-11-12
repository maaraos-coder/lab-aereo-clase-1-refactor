"""Etapa 6 · Curso 4 Laboratorio 2: diseño e implementación de medidas de control."""

from copy import deepcopy
import json
import hashlib
import logging
import math

_LOG = logging.getLogger(__name__)


def _stage6_json_safe(value):
    """Converts Stage 6 numeric UI objects to JSON primitives without changing other stages."""
    def normalize(item):
        if hasattr(item, 'item') and callable(item.item):
            return normalize(item.item())
        if isinstance(item, dict):
            return {str(k): normalize(v) for k,v in item.items()}
        if isinstance(item, (tuple, list)):
            return [normalize(v) for v in item]
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError('El diseño contiene un valor numérico no finito.')
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        raise TypeError('Tipo no serializable en el diseño: '+type(item).__name__)
    return normalize(value)


def _stage6_save_error(st, error, operation, backup=None):
    """Show safe diagnostic and recovery file; retain in-memory work."""
    identifier = hashlib.sha256((type(error).__name__+str(error)).encode('utf-8',errors='replace')).hexdigest()[:10].upper()
    _LOG.exception('Curso4 Lab2 Etapa6 save failure [%s] operation=%s', identifier, operation)
    st.error('No se pudo confirmar el guardado de la Etapa 6 (código '+identifier+'). '
             'Tu diseño sigue disponible en esta sesión. No cierres la página sin guardar un respaldo.')
    if backup is not None:
        try:
            payload=json.dumps(_stage6_json_safe(backup),ensure_ascii=False,allow_nan=False,indent=2)
        except (TypeError,ValueError,RecursionError):
            st.warning('No fue posible exportar esta configuración; conserva abierta la sesión y comunica el código de error.')
        else:
            st.download_button('Descargar respaldo de mi diseño (.json)',payload,
                file_name='respaldo_etapa6_control.json',mime='application/json',
                key='c4l2_s6_backup_'+operation+'_'+identifier)

from labs.curso4_lab2_control_scope import _front_name, render_scope, validate_scope

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


def _original_maxima(saved, *, by_front=False):
    """Máximo modelado por escenario a partir de la Etapa 5 del alumno."""
    rows=saved.get("c4l2_s5_detailed_results") or []
    out={}
    for row in rows:
        laeq=_num(row.get("LAeq [dB(A)]"))
        if laeq is None:
            continue
        key=_front_name(row.get("Frente")) if by_front else _scenario_key(row.get("Frente"))
        cur=out.get(key)
        if cur is None or laeq>cur["laeq"]:
            out[key]={
                "laeq":laeq,
                "front":str(row.get("Frente") or ""),
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


def _build_design_rows(maxima,limit=65.0,fronts=None, *, by_front=False):
    rows=[]
    for base in (FRONT_TEMPLATE if fronts is None else fronts):
        key=_front_name(base["Frente / condición"]) if by_front else _scenario_key(base["Frente / condición"])
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
    """Mantiene la identidad del frente de Etapas 3/4 al recuperar la Etapa 5.

    Los nombres/códigos exportados por Noise Map Lab pueden no coincidir con
    el nombre de la etapa de las fuentes originales. No deben sustituirla:
    render_scope necesita ese identificador para recuperar las máquinas.
    """
    names=list(dict.fromkeys(str(source.get("Etapa") or "").strip()
        for source in (saved.get("c4l2_s3_acoustic_sources") or []) if str(source.get("Etapa") or "").strip()))
    types={row["Frente / condición"]:row["Tipo de trabajo"] for row in FRONT_TEMPLATE}
    maxima=_original_maxima(saved,by_front=True)
    scenarios=saved.get("c4l2_s4_scenarios") or []
    if not names:
        fronts=[{"Frente / condición":m["front"],"Tipo de trabajo":types.get(m["front"],"Según actividad registrada")} for m in maxima.values()]
        return _build_design_rows(maxima,limit,fronts=fronts or None,by_front=True)

    matched={}
    for name in names:
        key=_front_name(name)
        match=maxima.get(key)
        if match is None:
            # Relación persistida en la Etapa 4 entre nombre de etapa y
            # nombre/código del frente exportado hacia la Etapa 5.
            for scenario in scenarios:
                if _front_name(scenario.get("Etapa")) != key:
                    continue
                match=maxima.get(_front_name(scenario.get("Frente")))
                if match is not None:
                    break
        if match is not None:
            matched[key]=match
    fronts=[{"Frente / condición":name,"Tipo de trabajo":types.get(name,"Según actividad registrada")} for name in names]
    return _build_design_rows(matched,limit,fronts=fronts,by_front=True)


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
            su justificación técnica y el nombre de la copia controlada. La aplicación por máquina se configura en el apartado de configuración en detalle.
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

    st.info(
        "**Tu entrega, para cada frente.** Identifica el receptor crítico y la reducción de LAeq que necesitas. "
        "Elige y justifica una medida viable. Registra qué máquinas reciben tratamiento y cuáles conservan su emisión. "
        "Implementa la medida en Noise Map Lab y guarda el proyecto controlado y su línea base comparable para la Etapa 7."
    )
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
    maxima=_original_maxima(saved,by_front=True)
    if maxima:
        problem=[]
        for sc,m in maxima.items():
            excess=m["laeq"]-reference_limit
            problem.append({
                "Frente":m["front"],
                "Receptor crítico":m["receptor"],
                "Mayor LAeq [dB(A)]":round(m["laeq"],1),
                "Límite [dB(A)]":reference_limit,
                "Excedencia [dB]":round(excess,1),
                "Diagnóstico":"Sobre el límite" if excess>0 else ("En el límite" if excess == 0 else "Bajo el límite"),
            })
        st.dataframe(pd.DataFrame(problem),hide_index=True,use_container_width=True)
    else:
        st.warning(
            "Aún no hay resultados guardados desde la Etapa 5. Puedes estudiar las medidas y preparar el diseño, "
            "pero para cuantificar la necesidad de control debes completar y guardar los LAeq originales."
        )

    from labs import curso4_control_workshop as workshop
    from labs import curso4_control_models as control_model
    role=st.session_state.get("role")
    is_teacher=role=="Docente"
    stage5_rows=saved.get("c4l2_s5_detailed_results") or []
    has_stage5_results=bool(saved.get("done_5")) and any(
        _num(r.get("LAeq [dB(A)]")) is not None for r in stage5_rows
    )
    if not is_teacher and has_stage5_results:
        from labs.curso4_laboratorio_2_stage5 import _front_label_issues
        mismatched=_front_label_issues(stage5_rows,saved)
        if mismatched:
            st.warning(
                "**Se detectaron nombres de frentes que no corresponden a la Etapa 4.** "
                "En la Etapa 5 aparecen: " + ", ".join(mismatched) + ". "
                "Vuelve a la Etapa 5 y revisa la columna «Frente»: identifica "
                "qué FT1–FT6 produjo cada resultado y utiliza su nombre original. "
                "No es necesario rehacer las Etapas 3 y 4 ni modificar valores "
                "acústicos; si un resultado agrupa varios frentes, no lo asignes "
                "a uno individual sin verificar su procedencia."
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
        with st.expander("Herramientas de apoyo · ejemplos, TL y práctica"):
            st.info("Estas herramientas son opcionales. Usa la calculadora TL si necesitas estimar el aislamiento de un panel. Si elegiste una barrera, configura su ubicación y los caminos fuente–receptor en el apartado B del diseño en detalle.")
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

            st.markdown("**Diseñador de práctica**")
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

        from labs.curso4_lab2_drafts import render_draft_save
        render_draft_save(st,saved,runtime,lab,6,{
            "c4l2_s6_tl_calculator":tl_config,
            "c4l2_s6_treatment_study":study_cfg,
            "c4l2_s6_treatment_study_results":study_results,
        },"c4l2_s6_save_draft")
        return

    st.markdown("### 2 · Diseña la estrategia para cada frente")
    st.info("El frente agrupa máquinas para representar su emisión conjunta. Un tratamiento de fuente actúa solo sobre las máquinas y unidades que selecciones; una barrera actúa sobre el camino hacia el receptor. Elige Combinación de medidas si tu estrategia usa tratamientos distintos.")
    st.markdown("**Ejemplo de procedimiento:** si se encierra solo el minicargador, la excavadora y la retroexcavadora conservan su emisión original. El frente controlado se obtiene sumando energéticamente las tres contribuciones resultantes, no restando el aislamiento del encierro al total del frente.")
    if is_teacher:
        saved_rows=saved.get("c4l2_s6_control_design") or _teacher_design_rows(reference_limit)
        design_grid_key="c4l2_s6_design_grid_teacher_v2"
    else:
        previous={_front_name(row.get("Frente / condición")):row for row in saved.get("c4l2_s6_control_design") or []}
        saved_rows=_student_design_rows(saved,reference_limit)
        for row in saved_rows:
            prior=previous.get(_front_name(row["Frente / condición"]),{})
            for field in ("Medida seleccionada","Justificación","Proyecto controlado"):
                if field in prior:
                    row[field]=prior[field]
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

    with st.expander("Herramientas de apoyo · ejemplos, TL y práctica"):
        st.info("Estas herramientas son opcionales. Usa la calculadora TL si necesitas estimar el aislamiento de un panel. Si elegiste una barrera, configura su ubicación y los caminos fuente–receptor en el apartado B del diseño en detalle.")
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

        st.markdown("**Diseñador de práctica**")
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

    st.markdown("### 3 · Configura tu medida en detalle")
    st.caption("Si propones solo una barrera, marca cada máquina como «Sin tratamiento en la fuente» y configura la barrera en el apartado B.")
    labels=[str(r.get("Frente / condición") or "") for r in design_records]
    selected_front=st.selectbox("Frente a configurar",labels,key="c4l2_s6_front_detail")
    selected=next((r for r in design_records if str(r.get("Frente / condición"))==selected_front),{})
    measure=str(selected.get("Medida seleccionada") or "Seleccionar medida")

    import hashlib
    prefix="c4l2_s6_scope_"+hashlib.sha1((str(role)+selected_front).encode()).hexdigest()[:12]
    with st.expander("Recuperar respaldo JSON de este frente"):
        restored_file=st.file_uploader("Archivo de respaldo de la Etapa 6",type=["json"],
            key=prefix+"_backup_upload")
        if restored_file and st.button("Restaurar este frente desde el archivo",
                                       key=prefix+"_restore"):
            try:
                raw=restored_file.getvalue()
                if len(raw)>2_000_000:
                    raise ValueError("El archivo excede el tamaño permitido para un frente.")
                restored=json.loads(raw.decode("utf-8"))
                if not isinstance(restored,dict):
                    raise ValueError("El respaldo debe contener un objeto JSON.")
                backup_front=restored.get("front",restored.get("frente"))
                restored_cfg=restored.get("configuration",restored.get("configuracion"))
                if restored_cfg is None and isinstance(restored.get("configuraciones"),dict):
                    restored_cfg=restored["configuraciones"].get(selected_front)
                if backup_front and backup_front!=selected_front:
                    raise ValueError("El respaldo pertenece a otro frente de trabajo.")
                if not isinstance(restored_cfg,dict) or restored_cfg.get("scope_schema_version")!=2:
                    raise ValueError("Este respaldo no contiene un diseño compatible de la Etapa 6.")
                # A Streamlit selectbox keeps its old widget value after JSON
                # restore. Without clearing it the first selected machine can
                # overwrite its recovered treatment on the very next rerun.
                from labs.curso4_lab2_control_scope import front_sources
                from labs.curso4_lab2_acoustics import source_fingerprint
                from labs.c4l2_stage6_checkpoint import (
                    reconcile_machine_ids, reset_stage6_widgets
                )
                entries=front_sources(saved,selected_front)
                recovered=restored_cfg.get("machines")
                mapped,unresolved=reconcile_machine_ids(
                    recovered,entries,source_fingerprint
                )
                if unresolved:
                    raise ValueError(
                        "No fue posible vincular con seguridad estas aplicaciones: "+
                        ", ".join(unresolved)+
                        ". Revisa si cambiaron nombres, cantidades o espectros de Etapas 3/4."
                    )
                # Preserve every application; the recovered IDs can differ
                # when Stage 3 source rows have been reordered.
                restored_cfg["machines"]=mapped
                recovered_strategy=str(restored_cfg.get("medida") or restored.get("strategy") or "")
                if recovered_strategy and recovered_strategy!=measure:
                    raise ValueError(
                        "El respaldo corresponde a la estrategia '"+recovered_strategy+
                        "'. Selecciónala en la tabla de estrategias antes de restaurar."
                    )
                clean_cfg=_stage6_json_safe(restored_cfg)
                reset_stage6_widgets(st.session_state,prefix)
                st.session_state[prefix+"_work"]=clean_cfg
                st.session_state[prefix+"_recovered_count"]=len(mapped)
            except (UnicodeError,json.JSONDecodeError,TypeError,ValueError) as error:
                st.warning("No se pudo restaurar el respaldo: "+str(error))
            else:
                st.success("Respaldo recuperado en esta sesión ("+str(len(recovered))+" máquinas). Revisa la primera máquina y guarda el frente.")
                st.rerun()
    cfg_saved=st.session_state.get(prefix+"_work") or (saved.get("c4l2_s6_measure_config") or {}).get(selected_front,{})
    if st.session_state.get(prefix+"_recovered_count") is not None:
        recovered_count=st.session_state[prefix+"_recovered_count"]
        st.caption(
            "Respaldo restaurado: "+str(recovered_count)+" aplicaciones de máquina. "
            "Comprueba especialmente la máquina 1 y su medida antes de guardar."
        )
    cfg=render_scope(st,pd,saved,selected_front,measure,cfg_saved,prefix,workshop,study_cfg,tl_spectrum)
    st.session_state[prefix+"_work"]=deepcopy(cfg)
    # Respaldo local independiente de Supabase, disponible incluso antes de
    # finalizar las validaciones académicas del frente.
    from labs.curso4_lab2_control_scope import front_sources
    expected_machines=front_sources(saved,selected_front)
    backed_ids=set((cfg.get("machines") or {}).keys())
    missing_machines=[
        str(entry["source"].get("Máquina / equipo proyecto") or entry["id"])
        for entry in expected_machines if entry["id"] not in backed_ids
    ]
    st.caption(
        "Cobertura del respaldo de este frente: "+
        str(len(backed_ids & {entry["id"] for entry in expected_machines}))+
        " de "+str(len(expected_machines))+" máquinas registradas."
    )
    if missing_machines:
        st.warning(
            "Este respaldo todavía no contiene aplicación individual para: "+
            ", ".join(missing_machines)+
            ". Si corresponde, selecciónala y marca expresamente "
            "«Sin tratamiento en la fuente» antes de guardar."
        )
    try:
        backup_json=json.dumps(_stage6_json_safe({
            "schema_version":2,"stage":6,"front":selected_front,
            "strategy":measure,
            "machine_count":len(expected_machines),
            "missing_machine_names":missing_machines,
            "configuration":cfg,
        }),ensure_ascii=False,allow_nan=False,indent=2)
    except (ValueError,TypeError,RecursionError) as error:
        st.warning("La configuración contiene datos que deben revisarse antes de poder exportarla: "+type(error).__name__)
    else:
        st.download_button("Descargar respaldo de este frente (.json)",backup_json,
            file_name="etapa6_"+hashlib.sha1(selected_front.encode()).hexdigest()[:10]+".json",
            mime="application/json",key=prefix+"_backup_current",
            help="Guarda en tu equipo los tratamientos actuales. Es independiente del guardado en la plataforma.")
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
                candidate["c4l2_s6_measure_config"][selected_front]=_stage6_json_safe(cfg)
                candidate["c4l2_s6_control_design"]=_stage6_json_safe(design_records)
                runtime["_save"](lab,candidate,6)
            except Exception as error:
                _stage6_save_error(st,error,"frente",{
                    "etapa":6,"frente":selected_front,
                    "estrategias":design_records,"configuracion":cfg,
                })
            else:
                saved.update(candidate)
                st.success("Aplicaciones por máquina y balance del frente guardados. Puedes configurar otro frente.")

    st.markdown("### 4 · Del frente equivalente al control por máquinas en Noise Map Lab")
    st.info("La fuente puntual que representa al frente contiene la suma de varias máquinas. No le asignes un encierro, semiencierro o silenciador si la medida solo corresponde a una de ellas: el programa trataría toda la emisión agrupada. Para aplicar controles individuales, sustituye esa representación por las máquinas que la componen en una copia del proyecto.")
    st.info("TL es el aislamiento del panel. ΔLw es la reducción de potencia emitida por las fuentes tratadas. ΔLAeq es la reducción en el receptor, obtenida al comparar los dos modelos en Noise Map Lab.")
    st.markdown("#### A · Conserva tres archivos identificables")
    st.dataframe(pd.DataFrame([
        {"Archivo sugerido":"FT_Original_Equivalente","Contenido":"Frente como una fuente equivalente, sin control.","Uso":"Conservar el trabajo de las Etapas 4 y 5; no sobrescribirlo."},
        {"Archivo sugerido":"FT_Original_Maquinas","Contenido":"Las máquinas del mismo frente por separado, todavía sin medidas.","Uso":"Línea base comparable para evaluar los controles individuales."},
        {"Archivo sugerido":"FT_Controlado_Maquinas","Contenido":"Copia del original por máquinas, con los tratamientos seleccionados.","Uso":"Comparar con FT_Original_Maquinas en la Etapa 7."},
    ]),hide_index=True,use_container_width=True)
    st.caption("Sustituye FT por el frente y agrega el receptor o la posición crítica cuando corresponda. En Proyecto → Guardar proyecto se descarga un archivo .noisemap.json: conserva cada archivo con un nombre que identifique su representación y condición. Proyecto → Abrir proyecto recupera el escenario completo; Importar objetos JSON agrega objetos y no sustituye el proyecto.")
    st.markdown("#### B · Construye primero el original por máquinas, sin control")
    st.markdown("""
    1. En **Proyecto → Abrir proyecto**, recupera el original del frente. Conserva su archivo intacto y trabaja en una copia.
    2. En esa copia, **retira la fuente equivalente del frente que vas a sustituir**. Conserva los otros frentes, receptores, edificios, terreno, área de cálculo y configuración que formen parte del escenario.
    3. Usa **Fuente (F)** para crear las máquinas originales del frente: por ejemplo, minicargador, retroexcavadora y excavadora. Puedes usar **Ingresar coordenadas** para conservar una ubicación trazable.
    4. En la ficha de cada máquina, ingresa su **Lw original por bandas de octava, sin ponderación A**, recuperado de la Etapa 3 y disponible en la tabla inferior. No ingreses a cada máquina el espectro total del frente ni su LWA global en todas las bandas.
    5. Representa cada unidad por separado si tiene otra posición o recibirá otro tratamiento. Si agrupas N unidades idénticas en un mismo punto y con el mismo control, usa su espectro conjunto **Lw + 10·log₁₀(N)** una sola vez; no vuelvas a sumar la cantidad por otra vía.
    6. Mantén las mismas máquinas simultáneas del original. **Sin medidas de control**, utiliza **Calcular mapa** y revisa **Resultados**. Guarda el archivo como **FT_Original_Maquinas**.
    """)
    from labs.curso4_lab2_control_scope import front_sources
    original_entries=front_sources(saved,selected_front)
    if original_entries:
        from labs.curso4_lab2_acoustics import BAND_LABELS
        source_rows=[]
        for entry in original_entries:
            source=entry["source"]
            bands=source.get("Lw_bandas") or []
            if len(bands)==len(BAND_LABELS):
                source_rows.append({"Máquina":source.get("Máquina / equipo proyecto"),
                    "Unidades originales":source.get("Cantidad"),
                    **dict(zip(BAND_LABELS,bands))})
        if source_rows:
            st.markdown("**Datos para crear las fuentes originales del frente seleccionado · Lw [dB] por una unidad**")
            st.dataframe(pd.DataFrame(source_rows),hide_index=True,use_container_width=True)
            st.caption("Datos originales de la Etapa 3; todavía no incluyen tratamientos ni la suma de varias unidades. La cantidad indica cuántas unidades debes representar.")
    st.warning("Evita contar dos veces el frente: en la copia por máquinas no deben quedar activas a la vez su fuente equivalente y las fuentes que la sustituyen. Una fuente equivalente de otro frente se conserva si pertenece al escenario original.")
    st.markdown("#### C · Comprueba que la línea base sea comparable")
    st.markdown("""
    - Como comprobación de la suma, puedes colocar provisionalmente las máquinas en **el mismo punto, altura y condiciones de emisión de la fuente equivalente**, sin tratamientos. Bajo las mismas condiciones de propagación, la suma debe reproducir el resultado equivalente, salvo el redondeo de entrada. Si no coincide, revisa espectros, unidades y fuentes duplicadas.
    - Para diseñar el control, utiliza posiciones, alturas y orientaciones **físicamente posibles y documentadas**. Si separarlas cambia la geometría respecto del frente equivalente, puede cambiar el LAeq aun sin controles: esa diferencia no es eficacia de una medida.
    - En ese caso, registra la nueva línea base sin control por separado para la **Etapa 7**, identificando el proyecto **FT_Original_Maquinas** y el receptor/posición crítica. Conserva el archivo original equivalente como antecedente. En la **Etapa 7** compara original y controlado con la misma representación por máquinas.
    """)
    st.markdown("#### D · Crea la copia controlada y trata solo los equipos elegidos")
    st.markdown("""
    1. Abre **FT_Original_Maquinas** y conserva otra copia como **FT_Controlado_Maquinas**.
    2. Selecciona la fuente de la máquina que recibirá el control. Configura **su** encierro, semiencierro, silenciador o reducción directa con los parámetros definidos en la sección 6. Las otras máquinas conservan sus emisiones y condiciones originales.
    3. Si configuras el tratamiento en la ficha de la fuente, conserva su **Lw original** como entrada. **No introduzcas además el espectro ya reducido** calculado en el laboratorio: estarías aplicando dos veces el mismo control.
    4. Para una **barrera**, utiliza la herramienta **Barrera** y dibuja su ubicación real. Comprueba con **Corte** qué caminos máquina–receptor quedan apantallados; no restes su atenuación al Lw del frente ni la atribuyas a máquinas no protegidas.
    5. Mantén posiciones, alturas, receptores y parámetros del original por máquinas; cambia únicamente los controles y la geometría indispensable de estos. Usa **Calcular mapa**, consulta **Resultados** y guarda el archivo controlado.
    6. Repite para cada frente y, cuando corresponda, para cada posición crítica respecto de un receptor. La comparación cuantitativa se realiza en la **Etapa 7** entre las dos copias por máquinas correspondientes.

    **Ejemplo:** si solo el minicargador recibe un encierro, el modelo controlado contiene minicargador con encierro, retroexcavadora sin ese control y excavadora sin ese control. La antigua fuente equivalente que agrupaba esas tres máquinas ya no participa en esa copia.
    """)
    st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)

    from labs.curso4_lab2_maps import render_uploader
    render_uploader(
        st,saved,runtime,lab,
        group="control",
        title="5 · Adjunta los mapas con las medidas implementadas",
        description=(
            "Sube capturas donde se observe la ubicación y geometría de la barrera, encierro, semiencierro o silenciador "
            "incorporado. Si la medida tiene orientación o aberturas, agrega también una vista de corte."
        ),
        stage=6,
        key="c4l2_s6_control_maps",
    )

    st.markdown("### 6 · Verificación antes de guardar")
    st.caption("Las capturas sirven como respaldo visual. Usa Guardar avance para conservar un borrador, guarda cada frente cuando esté listo y finaliza después de completar todos los frentes.")
    saved_checks=saved.get("c4l2_s6_checks") or {}
    v1=st.checkbox("Conservé intacto el escenario original.",value=bool(saved_checks.get("original")),key="c4l2_s6_check_original")
    v2=st.checkbox("La medida es físicamente compatible con la actividad constructiva.",value=bool(saved_checks.get("viable")),key="c4l2_s6_check_viable")
    v3=st.checkbox("La medida está correctamente ubicada y ambas copias usan la misma representación por máquinas y geometría comparable, sin duplicar el frente equivalente.",value=bool(saved_checks.get("representation")),key="c4l2_s6_check_representation")
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
        "c4l2_s6_checks":{"original":v1,"viable":v2,"geometry":v3,"representation":v3,"copy":v4},
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
                "c4l2_s6_checks":{"original":v1,"viable":v2,"geometry":v3,"representation":v3,"copy":v4},
                "done_6":True})
            try:
                candidate["c4l2_s6_measure_config"]=_stage6_json_safe(configs)
                candidate["c4l2_s6_control_design"]=_stage6_json_safe(design_records)
                runtime["_save"](lab,candidate,6)
            except Exception as error:
                _stage6_save_error(st,error,"final",{
                    "etapa":6,"estrategias":design_records,"configuraciones":configs,
                })
            else:
                saved.update(candidate)
                st.success("Diseño por máquinas y propagación guardado. La Etapa 7 comparará los escenarios modelados.")
