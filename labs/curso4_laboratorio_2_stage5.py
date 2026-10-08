"""Etapa 5 · Curso 4 Laboratorio 2: resultados detallados de la condición original."""

import math
from labs.curso4_laboratorio_1 import BS_PLANT

OCTAVE_LABELS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]
REPORT_BANDS=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"]
A_CORR=[-39.4,-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0]


def _num(v):
    try:
        return float(str(v).replace(",",".").strip())
    except Exception:
        return None


def _sum_db(values):
    vals=[float(v) for v in values if v is not None]
    if not vals:
        return None
    return 10*math.log10(sum(10**(v/10) for v in vals))


def _teacher_fronts():
    """Frentes y totales publicados en la Adenda 2."""
    return {
        "Escenario 1 · Movimiento de tierra":{
            "bands_nps":[54,65,62,68,69,69,65,54],
            "npseq":75,
            "machines":["Minicargador","Retroexcavadora","Excavadora"],
            "table":"13",
        },
        "Escenario 2 · Obra gruesa suelo":{
            "bands_nps":[57,64,69,74,74,73,68,62],
            "npseq":80,
            "machines":["Rodillo compactador","Minicargador","Retroexcavadora","Camión mixer + bomba hormigón"],
            "table":"14",
        },
        "Escenario 2 · Obra gruesa altura":{
            "bands_nps":[52,56,63,64,65,64,60,55],
            "npseq":71,
            "machines":["Grúa pluma","Vibrador de inmersión"],
            "table":"15",
        },
        "Escenario 2 · Urbanización":{
            "bands_nps":[57,65,70,74,74,73,68,62],
            "npseq":80,
            "machines":["Rodillo compactador","Minicargador","Retroexcavadora","Motoniveladora","Camión mixer + bomba hormigón"],
            "table":"16",
        },
        "Escenario 2 · Terminaciones":{
            "bands_nps":[52,60,57,62,64,64,60,50],
            "npseq":70,
            "machines":["Minicargador","Alzahombre"],
            "table":"17",
        },
        "Escenario 3 · Obras IMIV":{
            "bands_nps":[57,64,71,75,75,74,70,64],
            "npseq":80,
            "machines":["Cango","Camión mixer + bomba hormigón","Vibrador de inmersión","Rodillo compactador"],
            "table":"18",
        },
    }


def _teacher_result_rows():
    """Resultados sin medidas de control publicados en la Adenda 2, Tabla 27."""
    matrix={
        "R01":{"Escenario 1":51,"Escenario 2":48,"Escenario 3":66},
        "R02":{"Escenario 1":66,"Escenario 2":72,"Escenario 3":70},
        "R03":{"Escenario 1":59,"Escenario 2":67,"Escenario 3":64},
        "R04":{"Escenario 1":65,"Escenario 2":71,"Escenario 3":45},
        "R05":{"Escenario 1":59,"Escenario 2":67,"Escenario 3":64},
        "R06":{"Escenario 1":64,"Escenario 2":72,"Escenario 3":58},
        "R07":{"Escenario 1":62,"Escenario 2":69,"Escenario 3":59},
        "R08":{"Escenario 1":62,"Escenario 2":67,"Escenario 3":48},
        "R09":{"Escenario 1":55,"Escenario 2":59,"Escenario 3":45},
        "RIMIV01":{"Escenario 3":74},
        "RIMIV02":{"Escenario 3":70},
        "RIMIV03":{"Escenario 3":73},
        "RIMIV04":{"Escenario 3":73},
        "RIMIV05":{"Escenario 3":78},
        "RIMIV06":{"Escenario 3":78},
        "RIMIV07":{"Escenario 3":77},
        "RIMIV08":{"Escenario 3":73},
        "RIMIV09":{"Escenario 3":76},
    }
    rows=[]
    for receptor,scenarios in matrix.items():
        for scenario,laeq in scenarios.items():
            rows.append({
                "Frente":scenario,
                "Receptor":receptor,
                "Distancia F–R [m]":None,
                **{b:None for b in OCTAVE_LABELS},
                "LAeq [dB(A)]":laeq,
            })
    return rows


def _student_result_template():
    """Estructura Escenario–Receptor sin entregar resultados al alumno."""
    rows=[]
    for ref in _teacher_result_rows():
        rows.append({
            "Frente":ref.get("Frente"),
            "Receptor":ref.get("Receptor"),
            "Distancia F–R [m]":None,
            **{b:None for b in OCTAVE_LABELS},
            "LAeq [dB(A)]":None,
        })
    return rows


def _teacher_solution_panel(st,pd):
    """Muestra la solución directamente en la vista docente, no en la proyección/alumno."""
    if st.session_state.get("role")!="Docente":
        return

    fronts=_teacher_fronts()
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                padding:17px 19px;background:linear-gradient(135deg,#f8fcff,#edf7fb);
                margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        VISTA DOCENTE · SOLUCIÓN DE REFERENCIA
      </div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">
        Los datos de control aparecen completos aunque el alumno no haya recuperado fuentes
      </div>
      <div style="color:#526f80;line-height:1.55">
        Esta solución corresponde al último informe (Adenda 2) y sirve únicamente como referencia de corrección. La tabla de trabajo inferior queda sin resultados, incluso en vista Docente. La vista de Alumno
        y la Proyección Zoom mantienen estos campos sin resolver.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("#### Frentes de referencia · Adenda 2")
    summary=[]
    for front,data in fronts.items():
        summary.append({
            "Frente":front,
            "N° equipos":len(data["machines"]),
            "NPSeq total @10 m [dB(A)]":data["npseq"],
            "LWA aprox. [+28]":data["npseq"]+28,
            "Tabla Adenda 2":data["table"],
            "Equipos":" · ".join(data["machines"]),
        })
    st.dataframe(pd.DataFrame(summary),hide_index=True,use_container_width=True)

    st.markdown("#### Espectro total publicado a 10 m")
    chosen=st.selectbox(
        "Frente a revisar",
        list(fronts.keys()),
        key="c4l2_s5_teacher_front_main",
    )
    data=fronts[chosen]
    st.dataframe(
        pd.DataFrame({
            "Banda":REPORT_BANDS,
            "NPS total @10 m [dB(A) banda]":data["bands_nps"],
        }),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        f"{chosen} · NPSeq total @10 m = {data['npseq']} dB(A). "
        "La Adenda 2 publica bandas entre 63 Hz y 8 kHz."
    )

    st.markdown("#### Resultados oficiales sin medidas de control · Tabla 27")
    st.dataframe(pd.DataFrame(_teacher_result_rows()),hide_index=True,use_container_width=True)
    st.success(
        "Máximo de la Adenda 2 sin control: **78 dB(A)** en RIMIV05 y RIMIV06 (Escenario 3). "
        "Entre R01–R09, el mayor valor es **72 dB(A)** en R02 y R06 (Escenario 2). "
        "El límite diurno de todos los receptores R01–R09 es 65 dB(A), Zona III."
    )
    st.caption(
        "Referencia documental: Anexo 05 · Adenda 2, Tabla 27, págs. 53–54. "
        "El informe publica niveles globales por receptor; los espectros en recepción deben obtenerse del modelo del alumno."
    )

    with st.expander("Control aritmético opcional · divergencia geométrica",expanded=False):
        st.markdown(
            "Este cálculo sirve únicamente para revisar órdenes de magnitud y no sustituye la modelación ISO 9613."
        )
        st.latex(r"A_{div}=20\log_{10}(r)+11")
        st.latex(r"L_p\approx L_w-A_{div}")


def _teacher_pauta(st,pd):
    if st.session_state.get("role")!="Docente":
        return
    with st.expander("👨‍🏫 Pauta docente · criterios de revisión",expanded=False):
        st.markdown("""
        La solución numérica ya se muestra directamente en la **vista Docente** de esta etapa.
        Utiliza esta pauta solo como lista de comprobación:

        - El escenario evaluado corresponde a la **condición original sin medidas de control**.
        - Se identifica correctamente **frente, receptor, distancia F–R y alturas**.
        - Los resultados se registran **por banda de octava y globales**.
        - El receptor crítico se determina por el **mayor nivel modelado**, no por apreciación visual.
        - El escenario original se conserva para compararlo posteriormente con las medidas de control.
        - El control en campo libre sirve solo para revisar órdenes de magnitud y no sustituye Noise Map Lab.
        """)

def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]

    runtime["header"](
        "ETAPA 5 · LABORATORIO 2",
        "Resultados detallados de la condición original",
        "Extraer, organizar e interpretar los resultados del escenario original antes de incorporar medidas de control.",
        show_overview=False,
        duration_minutes=35,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
    background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        RESULTADOS · ESCENARIO ORIGINAL
      </div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">
        Ahora dejamos de construir el modelo y comenzamos a leerlo
      </div>
      <div style="color:#526f80;line-height:1.6">
        La Etapa 4 dejó guardados los escenarios originales de cada frente de trabajo. En esta etapa
        obtendremos los niveles en los receptores, revisaremos su contenido espectral e identificaremos
        la condición más desfavorable que servirá como línea base para evaluar posteriormente las medidas de control.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 1 · Supuesto geométrico del caso")
    st.markdown("""
    <div style="border:1px solid #d7e5ec;border-left:5px solid #0b7fa5;border-radius:16px;
    padding:17px 19px;background:#fbfdff;margin:.35rem 0 1rem">
      <div style="font-weight:900;color:#173b53;margin-bottom:.35rem">Terreno aproximadamente plano</div>
      <div style="color:#526f80;line-height:1.6">
        Para este laboratorio se considerará que el sector de estudio presenta una topografía
        <b>aproximadamente plana</b>. Por ello, <b>no incorporaremos curvas de nivel ni cotas topográficas</b>
        al modelo y concentraremos el análisis en las fuentes, receptores, distancias, alturas y obstáculos.
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.info(
        "Esta es una simplificación del caso docente. En un proyecto real con desniveles relevantes, "
        "taludes, cortes o diferencias importantes de elevación, la topografía sí debe incorporarse."
    )

    role=st.session_state.get("role")
    is_teacher=role=="Docente"
    is_projection=role=="Proyección" or bool(st.session_state.get("projection_mode"))

    # La solución se revela solo en la vista docente.
    _teacher_solution_panel(st,pd)

    stage4_fronts=saved.get("c4l2_s4_fronts") or {}
    stage4_results=saved.get("c4l2_s4_results") or {}
    sources=saved.get("c4l2_s3_acoustic_sources") or []
    receptors=saved.get("c4l2_s2_receptors_table") or []

    st.markdown("### 2 · Recupera los escenarios originales")
    if stage4_fronts:
        overview=[]
        for front,cfg in stage4_fronts.items():
            overview.append({
                "Frente":front,
                "Proyecto guardado":cfg.get("project_name") or cfg.get("Proyecto Noise Map Lab") or "",
                "Receptor objetivo":cfg.get("target_receptor") or cfg.get("Receptor objetivo") or "",
                "Distancia F–R [m]":cfg.get("distance") or cfg.get("Distancia F–R [m]"),
                "Altura fuente [m]":cfg.get("source_height") or cfg.get("Altura fuente [m]"),
                "Sector":cfg.get("sector") or cfg.get("Ubicación") or "",
            })
        st.dataframe(pd.DataFrame(overview),hide_index=True,use_container_width=True)
    else:
        st.warning(
            "Aún no se recuperaron escenarios originales de la Etapa 4. Puedes revisar la metodología y la pauta docente, "
            "pero para completar esta etapa debes guardar al menos un frente original."
        )

    st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)

    st.markdown("### 3 · Registra los resultados detallados")
    st.markdown("""
    Para cada combinación **frente–receptor**, debes obtener directamente desde **Noise Map Lab**:

    - el **espectro por bandas** informado en el receptor;
    - el **LAeq global [dB(A)]**;
    - y, cuando corresponda, la **distancia fuente–receptor** utilizada en ese escenario.

    La tabla solo entrega la combinación **Escenario–Receptor** como guía.  
    **Los resultados acústicos no vienen precargados:** debes registrarlos a partir de tu propia modelación.
    """)

    # La tabla de trabajo nunca entrega los resultados.
    # Solo precarga la combinación Escenario–Receptor; espectro y LAeq deben ser
    # obtenidos por el alumno desde Noise Map Lab.
    blank_template=_student_result_template()

    if is_teacher:
        saved_detail=saved.get("c4l2_s5_detailed_results") or blank_template
        teacher_seed_version="adenda2_stage5_student_results_blank_v2"
        if st.session_state.get("c4l2_s5_teacher_seed_version")!=teacher_seed_version:
            st.session_state["c4l2_s5_detail_work"]=[dict(x) for x in blank_template]
            st.session_state["c4l2_s5_teacher_seed_version"]=teacher_seed_version
    elif is_projection:
        saved_detail=blank_template
        projection_seed_version="adenda2_stage5_projection_blank_v2"
        if st.session_state.get("c4l2_s5_projection_seed_version")!=projection_seed_version:
            st.session_state["c4l2_s5_detail_work"]=[dict(x) for x in blank_template]
            st.session_state["c4l2_s5_projection_seed_version"]=projection_seed_version
    else:
        saved_detail=saved.get("c4l2_s5_detailed_results") or blank_template

    def _empty_result_row(_n):
        return {
            "Frente":"",
            "Receptor":"",
            "Distancia F–R [m]":None,
            **{b:None for b in OCTAVE_LABELS},
            "LAeq [dB(A)]":None,
        }

    detail_df=runtime["_dynamic_grid"](
        saved_detail,
        state_key="c4l2_s5_detail_work",
        grid_key="c4l2_s5_detail_grid",
        empty_row_factory=_empty_result_row,
        widths={
            "Frente":190,"Receptor":110,"Distancia F–R [m]":155,
            **{b:105 for b in OCTAVE_LABELS},
            "LAeq [dB(A)]":135,
        },
        numeric_columns=["Distancia F–R [m]"]+OCTAVE_LABELS+["LAeq [dB(A)]"],
        min_rows=1,
        add_label="➕ Agregar resultado",
        remove_label="➖ Quitar última fila",
    )
    detail_records=detail_df.where(pd.notna(detail_df),None).to_dict("records")

    st.markdown("### 4 · Identifica la condición crítica")
    valid=[r for r in detail_records if _num(r.get("LAeq [dB(A)]")) is not None]
    if valid:
        critical=max(valid,key=lambda r:_num(r.get("LAeq [dB(A)]")))
        c1,c2,c3=st.columns(3)
        c1.metric("Frente crítico",str(critical.get("Frente") or "—"))
        c2.metric("Receptor crítico",str(critical.get("Receptor") or "—"))
        c3.metric("Mayor LAeq",f"{_num(critical.get('LAeq [dB(A)]')):.1f} dB(A)")
        st.success(
            "La condición crítica se determina a partir del mayor nivel numérico obtenido en los receptores "
            "para los escenarios originales modelados."
        )
    else:
        st.info("Ingresa al menos un resultado global de LAeq para identificar automáticamente la condición crítica.")

    st.markdown("### 5 · Interpreta el mapa y el espectro")
    a,b=st.columns(2,gap="large")
    with a:
        spatial=st.text_area(
            "Lectura espacial del mapa",
            value=str(
                saved.get("c4l2_s5_spatial_note")
                or (
                    "En la Adenda 2, el máximo sin control es 78 dB(A) en RIMIV05 y RIMIV06 para el Escenario 3. "
                    "Entre R01–R09, R02 y R06 alcanzan 72 dB(A) en el Escenario 2. "
                    "La condición crítica depende de la ubicación de los frentes y de la geometría respecto de cada receptor."
                    if is_teacher else ""
                )
            ),
            placeholder="Ej.: el mayor nivel se concentra en el borde del frente próximo a R1 y disminuye al aumentar la distancia...",
            key="c4l2_s5_spatial_note_work",
            height=130,
        )
    with b:
        spectral=st.text_area(
            "Lectura espectral",
            value=str(
                saved.get("c4l2_s5_spectral_note")
                or (
                    "El informe publicado entrega niveles globales por receptor, no el espectro de recepción. "
                    "Las bandas deben extraerse del modelo desarrollado en Noise Map Lab para fundamentar la selección de medidas de control."
                    if is_teacher else ""
                )
            ),
            placeholder="Ej.: predominan las bandas de 125–500 Hz, asociadas al conjunto de maquinaria pesada...",
            key="c4l2_s5_spectral_note_work",
            height=130,
        )

    st.markdown("""
    <div style="border-left:4px solid #2b7a4b;background:#f3faf6;border-radius:12px;
                padding:13px 16px;margin:.9rem 0;color:#355c46;line-height:1.55">
      <b>Línea base:</b> estos resultados corresponden a la <b>condición original sin medidas de control</b>.
      Deben conservarse sin modificaciones para poder cuantificar posteriormente la reducción lograda por cada medida.
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 6 · Guarda los resultados originales")
    if st.button("✓ Guardar resultados detallados",type="primary",use_container_width=True,key="c4l2_s5_save"):
        if not valid:
            st.warning("Registra al menos un resultado global de LAeq antes de guardar.")
        elif not str(spatial or "").strip() or not str(spectral or "").strip():
            st.warning("Completa la lectura espacial y la lectura espectral antes de guardar.")
        else:
            saved["c4l2_s5_detailed_results"]=detail_records
            saved["c4l2_s5_spatial_note"]=spatial
            saved["c4l2_s5_spectral_note"]=spectral
            saved["c4l2_s5_critical"]={
                "Frente":critical.get("Frente"),
                "Receptor":critical.get("Receptor"),
                "LAeq":_num(critical.get("LAeq [dB(A)]")),
            }
            saved["done_5"]=True
            runtime["_save"](lab,saved,5)
            st.success("Resultados originales guardados. Esta será la referencia antes de incorporar medidas de control.")

    _teacher_pauta(st,pd)
