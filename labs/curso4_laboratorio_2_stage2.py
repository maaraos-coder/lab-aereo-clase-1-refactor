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
    is_teacher=st.session_state.get("role")=="Docente"
    teacher_receptors=[
      {"Receptor":"R1","Uso / tipo":"Complejo educacional","Descripción":"Punto de proyección en patio del Complejo Educacional Consolidada","Latitud":-33.6119671,"Longitud":-70.5708285,"Altura (m)":1.5,"Dist. al predio (m)":67,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R2","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6127289,"Longitud":-70.5704974,"Altura (m)":1.5,"Dist. al predio (m)":5,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R3","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6128730,"Longitud":-70.5697995,"Altura (m)":1.5,"Dist. al predio (m)":16,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R4","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6134444,"Longitud":-70.5702517,"Altura (m)":1.5,"Dist. al predio (m)":15,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R5","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6137228,"Longitud":-70.5696316,"Altura (m)":1.5,"Dist. al predio (m)":15,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R6","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6139859,"Longitud":-70.5702185,"Altura (m)":1.5,"Dist. al predio (m)":7,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R7","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6144599,"Longitud":-70.5705289,"Altura (m)":1.5,"Dist. al predio (m)":5,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R8","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6145446,"Longitud":-70.5709615,"Altura (m)":1.5,"Dist. al predio (m)":5,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
      {"Receptor":"R9","Uso / tipo":"Vivienda","Descripción":"Punto de proyección en patio de vivienda","Latitud":-33.6139433,"Longitud":-70.5714464,"Altura (m)":1.5,"Dist. al predio (m)":13,"Fuente documental":"Anexo 03.2 · Tabla 4 · pág. 17"},
    ]
    teacher_relevance=[
      {"Receptor":"R1","¿Por qué se selecciona?":"Receptor sensible próximo al proyecto","Qué representa":"Complejo educacional","Observación espacial":"Ubicado al norte del predio; distancia mínima aproximada 67 m."},
      {"Receptor":"R2","¿Por qué se selecciona?":"Vivienda inmediatamente próxima al límite","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 5 m."},
      {"Receptor":"R3","¿Por qué se selecciona?":"Vivienda sensible cercana al frente oriental","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 16 m."},
      {"Receptor":"R4","¿Por qué se selecciona?":"Vivienda sensible cercana al frente oriental","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 15 m."},
      {"Receptor":"R5","¿Por qué se selecciona?":"Vivienda sensible cercana al frente oriental","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 15 m."},
      {"Receptor":"R6","¿Por qué se selecciona?":"Vivienda inmediatamente próxima al límite","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 7 m."},
      {"Receptor":"R7","¿Por qué se selecciona?":"Vivienda inmediatamente próxima al límite sur","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 5 m."},
      {"Receptor":"R8","¿Por qué se selecciona?":"Vivienda inmediatamente próxima al límite sur","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 5 m."},
      {"Receptor":"R9","¿Por qué se selecciona?":"Vivienda sensible cercana al límite occidental","Qué representa":"Vivienda","Observación espacial":"Distancia mínima aproximada 13 m."},
    ]

    default_rows=saved.get("c4l2_s2_receptors_table") or (
      teacher_receptors if is_teacher else [
        {"Receptor":"R1","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
        {"Receptor":"R2","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
        {"Receptor":"R3","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""},
      ]
    )
    if is_teacher and not saved.get("c4l2_s2_receptors_table"):
      current=st.session_state.get("c4l2_s2_receptors_work")
      has_content=bool(current) and any(str(x.get("Descripción") or "").strip() for x in current)
      if not has_content:
        st.session_state["c4l2_s2_receptors_work"]=[dict(x) for x in teacher_receptors]
    if "c4l2_s2_receptors_work" not in st.session_state:
      st.session_state["c4l2_s2_receptors_work"]=[dict(x) for x in default_rows]

    rows=st.session_state["c4l2_s2_receptors_work"]
    grid=runtime["_professional_grid"](pd.DataFrame(rows),"c4l2_s2_receptors_grid",
      widths={"Receptor":105,"Uso / tipo":170,"Descripción":250,"Latitud":150,"Longitud":150,"Altura (m)":120,"Dist. al predio (m)":155,"Fuente documental":240},
      numeric_columns=["Latitud","Longitud","Altura (m)","Dist. al predio (m)"],height=max(255,min(520,90+42*len(rows))))
    st.session_state["c4l2_s2_receptors_work"]=grid.where(pd.notna(grid),None).to_dict("records")

    add_col,remove_col,info_col=st.columns([.23,.23,.54])
    with add_col:
      if st.button("➕ Agregar receptor",use_container_width=True,key="c4l2_s2_add_receiver"):
        current=st.session_state["c4l2_s2_receptors_work"]
        n=len(current)+1
        current.append({"Receptor":f"R{n}","Uso / tipo":"","Descripción":"","Latitud":None,"Longitud":None,"Altura (m)":None,"Dist. al predio (m)":None,"Fuente documental":""})
        st.session_state["c4l2_s2_receptors_work"]=current
        st.rerun()
    with remove_col:
      if st.button("➖ Quitar último",use_container_width=True,key="c4l2_s2_remove_receiver",disabled=len(rows)<=3):
        current=st.session_state["c4l2_s2_receptors_work"]
        if len(current)>3:
          current.pop()
          st.session_state["c4l2_s2_receptors_work"]=current
        st.rerun()
    with info_col:
      st.caption(f"Receptores registrados: **{len(rows)}** · mínimo 3, sin máximo fijo.")

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
    receptor_names=[str(x.get("Receptor") or f"R{i+1}") for i,x in enumerate(st.session_state["c4l2_s2_receptors_work"])]
    saved_rel={str(x.get("Receptor")):x for x in (saved.get("c4l2_s2_relevance_table") or [])}
    if is_teacher and not saved_rel:
      saved_rel={str(x.get("Receptor")):x for x in teacher_relevance}
    if "c4l2_s2_relevance_work" not in st.session_state:
      st.session_state["c4l2_s2_relevance_work"]=[
        dict(saved_rel.get(name,{"Receptor":name,"¿Por qué se selecciona?":"","Qué representa":"","Observación espacial":""}))
        for name in receptor_names
      ]
    else:
      current_rel={str(x.get("Receptor")):x for x in st.session_state["c4l2_s2_relevance_work"]}
      st.session_state["c4l2_s2_relevance_work"]=[
        dict(current_rel.get(name,saved_rel.get(name,{"Receptor":name,"¿Por qué se selecciona?":"","Qué representa":"","Observación espacial":""})))
        for name in receptor_names
      ]

    rel=st.session_state["c4l2_s2_relevance_work"]
    relgrid=runtime["_professional_grid"](pd.DataFrame(rel),"c4l2_s2_relevance_grid",
      widths={"Receptor":105,"¿Por qué se selecciona?":280,"Qué representa":240,"Observación espacial":300},
      height=max(235,min(500,90+42*len(rel))))
    st.session_state["c4l2_s2_relevance_work"]=relgrid.where(pd.notna(relgrid),None).to_dict("records")

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
      st.markdown("""
      <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                  padding:16px 18px;background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:1rem 0">
        <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
          VISTA DOCENTE · REFERENCIA DE CORRECCIÓN
        </div>
        <div style="font-size:1.04rem;font-weight:900;color:#173b53;margin:.25rem 0">
          Receptores y geometría esperada
        </div>
        <div style="color:#526f80;line-height:1.5">
          La vista docente muestra los criterios y, cuando existen datos guardados, los receptores registrados.
          Alumno y Proyección Zoom deben identificar y documentar los puntos desde el expediente.
        </div>
      </div>
      """,unsafe_allow_html=True)

      teacher_receptors=saved.get("c4l2_s2_receptors_table") or []
      if teacher_receptors:
        st.markdown("#### Receptores registrados · vista docente")
        st.dataframe(pd.DataFrame(teacher_receptors),hide_index=True,use_container_width=True)
      else:
        st.info(
          "No se muestran coordenadas inventadas como solución. La posición exacta de R1, R2, R3… "
          "debe provenir del Anexo de Ruido y Vibraciones y de la cartografía oficial del proyecto."
        )

      with st.expander("👨‍🏫 Criterios de revisión",expanded=False):
        st.markdown("""
        - El receptor debe entenderse como un **punto tridimensional**.
        - Debe conservarse la identificación documental **R1, R2, R3...**.
        - Registrar coordenadas, altura y distancia al predio.
        - Distinguir **distancia al predio** de **distancia fuente–receptor**.
        - Justificar por qué se selecciona cada receptor.
        - Reproducir correctamente cada punto en Noise Map Lab.
        """)
