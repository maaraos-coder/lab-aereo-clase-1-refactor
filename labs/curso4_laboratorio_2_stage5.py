"""Etapa 5 · Curso 4 Laboratorio 2: resultados detallados de la condición original."""

import math
from labs.curso4_laboratorio_1 import BS_PLANT

OCTAVE_LABELS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]
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
    teacher_map=[
        ("Movimiento de tierras","Excavadora hidráulica"),
        ("Movimiento de tierras","Retroexcavadora"),
        ("Movimiento de tierras","Cargador frontal"),
        ("Movimiento de tierras","Camión tolva articulado"),
        ("Movimiento de tierras","Rodillo vibratorio"),
        ("Hormigón / obra gruesa","Camión mixer"),
        ("Hormigón / obra gruesa","Bomba de hormigón"),
        ("Hormigón / obra gruesa","Vibrador de inmersión"),
        ("Estructura / izaje","Grúa torre"),
        ("Equipos auxiliares","Generador diésel"),
    ]
    grouped={}
    for front,bs_name in teacher_map:
        item=BS_PLANT[bs_name]
        bands=[float(v)+28.0 for v in item["bands"]]
        grouped.setdefault(front,[]).append((bs_name,bands))

    out={}
    for front,items in grouped.items():
        eq=[_sum_db([x[1][i] for x in items]) for i in range(8)]
        lwa_bands=[v+a for v,a in zip(eq,A_CORR)]
        lwa=_sum_db(lwa_bands)
        out[front]={"bands":eq,"lwa":lwa,"machines":[x[0] for x in items]}
    return out


def _teacher_result_rows():
    """Solución numérica docente de control, independiente de avances del alumno."""
    fronts=_teacher_fronts()
    rows=[]
    # Tres distancias de control para cada frente. Es un chequeo en campo libre,
    # no reemplaza el resultado final de Noise Map Lab.
    for front,data in fronts.items():
        for idx,r in enumerate((10,25,50),start=1):
            adiv=20*math.log10(r)+11
            lp_bands=[v-adiv for v in data["bands"]]
            lwa_bands=[v+a for v,a in zip(lp_bands,A_CORR)]
            laeq=_sum_db(lwa_bands)
            row={
                "Frente":front,
                "Receptor":f"R{idx}",
                "Distancia F–R [m]":r,
            }
            for label,val in zip(OCTAVE_LABELS,lp_bands):
                row[label]=round(val,1)
            row["LAeq [dB(A)]"]=round(laeq,1)
            rows.append(row)
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
        Esta solución sirve para conducir la clase y revisar órdenes de magnitud. La vista de Alumno
        y la Proyección Zoom mantienen estos campos sin resolver.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("#### Fuentes equivalentes de referencia")
    summary=[]
    for front,data in fronts.items():
        summary.append({
            "Frente":front,
            "N° equipos":len(data["machines"]),
            "LWA equivalente [dB(A)]":round(data["lwa"],1),
            "Equipos":" · ".join(data["machines"]),
        })
    st.dataframe(pd.DataFrame(summary),hide_index=True,use_container_width=True)

    st.markdown("#### Espectro equivalente de referencia")
    chosen=st.selectbox(
        "Frente a revisar",
        list(fronts.keys()),
        key="c4l2_s5_teacher_front_main",
    )
    data=fronts[chosen]
    st.dataframe(
        pd.DataFrame({
            "Banda":OCTAVE_LABELS,
            "Lw equivalente [dB]":[round(x,1) for x in data["bands"]],
        }),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(f"{chosen} · LWA equivalente ≈ {data['lwa']:.1f} dB(A).")

    st.markdown("#### Control de propagación de referencia")
    st.markdown(
        "Como verificación independiente del software se utiliza la divergencia geométrica de una "
        "fuente puntual en campo libre. Este control no reemplaza Noise Map Lab."
    )
    st.latex(r"A_{div}=20\log_{10}(r)+11")
    st.latex(r"L_p\approx L_w-A_{div}")
    st.dataframe(pd.DataFrame(_teacher_result_rows()),hide_index=True,use_container_width=True)
    st.caption(
        "Los resultados de esta tabla son controles docentes en campo libre a 10, 25 y 50 m. "
        "El valor definitivo del ejercicio corresponde al modelo realizado en Noise Map Lab."
    )


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
    Para cada combinación **frente–receptor**, registra el nivel por bandas que entrega el modelo y el nivel global.
    No copies únicamente el color del mapa: utiliza el valor numérico informado en el receptor.
    """)

    # En la vista docente, la tabla principal parte con la solución de control.
    # Alumno y Proyección Zoom parten sin resultados revelados y deben desarrollarlos.
    if is_teacher:
        saved_detail=saved.get("c4l2_s5_detailed_results") or _teacher_result_rows()
    elif is_projection:
        saved_detail=[
            {"Frente":"","Receptor":"","Distancia F–R [m]":None,
             **{b:None for b in OCTAVE_LABELS},"LAeq [dB(A)]":None}
        ]
    else:
        saved_detail=saved.get("c4l2_s5_detailed_results") or [
            {"Frente":"","Receptor":"","Distancia F–R [m]":None,
             **{b:None for b in OCTAVE_LABELS},"LAeq [dB(A)]":None}
        ]

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
                    "El mayor nivel se presenta en el receptor más próximo al frente de trabajo. "
                    "El nivel disminuye al aumentar la distancia fuente–receptor; la condición crítica "
                    "debe confirmarse con la geometría real del modelo."
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
                    "El espectro permite reconocer qué bandas dominan el aporte de cada frente. "
                    "La selección posterior de controles debe considerar esas bandas dominantes y no solo el LAeq global."
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
