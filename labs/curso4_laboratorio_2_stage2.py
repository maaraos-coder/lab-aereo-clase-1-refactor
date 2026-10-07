"""Etapa 2 · Curso 4 Laboratorio 2: identificación de receptores."""

def render(lab, saved, runtime):
    globals().update(runtime)
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 2 · LABORATORIO 2",
        "Identifica los receptores del entorno",
        "Reconocer qué es un receptor acústico, seleccionar puntos representativos y ubicarlos correctamente en Noise Map Lab.",
        show_overview=False,
        duration_minutes=25,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
    background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">DEL PREDIO AL ENTORNO</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">
        Un modelo necesita saber dónde queremos conocer el nivel
      </div>
      <div style="color:#526f80;line-height:1.6">
        Ahora identificaremos los puntos del entorno donde interesa conocer la exposición acústica.
        Esos puntos se representan mediante <b>receptores</b>.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 1 · ¿Qué es un receptor?")
    st.markdown("""
    Un **receptor** es el punto donde el modelo calcula el nivel de ruido producido por una o más fuentes.
    No es solo una casa o edificio: es una **posición tridimensional** definida por coordenadas y altura.

    Para describirlo necesitamos: **ubicación**, **altura sobre terreno**, **uso o sensibilidad**,
    **descripción física**, **distancia respecto del proyecto** e identificador **R1, R2, R3...**
    """)
    st.info("Un mismo edificio puede requerir más de un receptor si interesa analizar distintos pisos o fachadas.")

    st.markdown("### 2 · ¿Dónde buscar los receptores?")
    st.markdown("""
    <div class="c4l2-table-head"><div class="c4l2-table-icon">🏘️</div><div>
      <div class="c4l2-table-kicker">ENTORNO RECEPTOR</div>
      <div class="c4l2-table-title">Busca primero en el expediente y luego contrasta con el mapa</div>
      <div class="c4l2-table-copy">Identifica los receptores considerados por el estudio y revisa su posición respecto de la obra.</div>
      <div class="c4l2-source"><b>📄 Dónde buscar:</b> Anexo 05 · <b>Ruido y Vibraciones</b>, secciones de receptores,
      puntos de evaluación, entorno y mapas. Complementa con Anexo 01 · <b>Antecedentes del Proyecto</b>.
      Busca: “receptor”, “punto receptor”, “R1”, “R2”, “vivienda”, “distancia” y “coordenadas”.</div>
    </div></div>
    """,unsafe_allow_html=True)

    st.markdown("### 3 · ¿Qué debes registrar?")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Ubicación","X / Y"); c2.metric("Altura","Z")
    c3.metric("Distancia","m"); c4.metric("Uso","Descripción")
    st.caption("En esta etapa registra la distancia mínima al límite del predio. La distancia fuente–receptor se trabajará cuando ubiquemos las fuentes.")

    st.markdown("### 4 · Registra los receptores identificados")
    rows=saved.get("c4l2_s2_receptors_table") or [
      {"Receptor":"R1","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
      {"Receptor":"R2","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
      {"Receptor":"R3","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
    ]
    grid=runtime["_professional_grid"](pd.DataFrame(rows),"c4l2_s2_receptors_grid",
      widths={"Receptor":105,"Uso / tipo":170,"Descripción":250,"Latitud":150,"Longitud":150,"Altura (m)":120,"Dist. al predio (m)":155,"Fuente documental":240},
      numeric_columns=["Latitud","Longitud","Altura (m)","Dist. al predio (m)"],height=255)

    st.markdown("### 5 · Ubícalos en Noise Map Lab")
    a,b=st.columns([.68,.32],gap="large")
    with a:
      st.markdown("""
      1. Abre el proyecto iniciado en la Etapa 1.
      2. Mantén visible el límite del predio.
      3. Agrega un objeto **Receptor** para cada punto.
      4. Nómbralos **R1, R2, R3...** respetando la identificación del expediente.
      5. Ajusta la **altura** según el punto representado.
      6. Verifica posición, coordenadas y distancia al predio.
      7. Guarda el proyecto.
      """)
    with b:
      st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)
    st.warning("No coloques todos los receptores a la misma altura por defecto: la altura es parte de la geometría del problema.")

    st.markdown("### 6 · Justifica la selección")
    rel=saved.get("c4l2_s2_relevance_table") or [
      {"Receptor":"R1","¿Por qué se selecciona?":"","Qué representa":"","Observación espacial":""},
      {"Receptor":"R2","¿Por qué se selecciona?":"","Qué representa":"","Observación espacial":""},
      {"Receptor":"R3","¿Por qué se selecciona?":"","Qué representa":"","Observación espacial":""},
    ]
    relgrid=runtime["_professional_grid"](pd.DataFrame(rel),"c4l2_s2_relevance_grid",
      widths={"Receptor":105,"¿Por qué se selecciona?":280,"Qué representa":240,"Observación espacial":300},height=235)

    if st.button("✓ Guardar receptores",type="primary",use_container_width=True,key="c4l2_s2_save"):
      def clean(df,main):
        d=df.copy().where(pd.notna(df),None)
        return [x for x in d.to_dict("records") if str(x.get(main) or "").strip()]
      recs=clean(grid,"Receptor"); rels=clean(relgrid,"Receptor")
      valid=[x for x in recs if x.get("Latitud") is not None and x.get("Longitud") is not None and x.get("Altura (m)") is not None and x.get("Dist. al predio (m)") is not None and str(x.get("Descripción") or "").strip()]
      if len(valid)<3 or len([x for x in rels if str(x.get("¿Por qué se selecciona?") or "").strip()])<3:
        st.warning("Completa al menos 3 receptores con coordenadas, altura, distancia, descripción y justificación.")
      else:
        saved["c4l2_s2_receptors_table"]=recs
        saved["c4l2_s2_relevance_table"]=rels
        saved["done_2"]=True
        runtime["_save"](lab,saved,2)
        st.success("Receptores guardados para las siguientes etapas.")

    if st.session_state.get("role")=="Docente":
      with st.expander("👨‍🏫 Pauta docente · Etapa 2"):
        st.markdown("""
        Revisar que el alumno entienda el receptor como un **punto tridimensional**, conserve la identificación documental,
        registre coordenadas, altura y distancia, distinga distancia al predio de distancia fuente–receptor,
        justifique cada punto y lo reproduzca en Noise Map Lab.
        """)
