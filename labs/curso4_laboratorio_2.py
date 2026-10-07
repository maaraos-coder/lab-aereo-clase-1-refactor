"""Curso 4 · Laboratorio 2 · Proyecto real Eyzaguirre.

Renderer específico del Laboratorio 2. La Etapa 1 reconstruye el proyecto real
Conjunto Habitacional Eyzaguirre desde su expediente SEIA antes de modelar.
"""

_RUNTIME_PROTECTED = {"run_stage", "_bind_runtime", "_RUNTIME_PROTECTED"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED:
            module_globals[name] = value

CLASS_ID = "clase-08-construccion-lab-2"
NOISEMAP_URL = "https://noisemap-akuzoft.vercel.app/"
SEA_PROJECT_URL = "https://seia.sea.gob.cl/expediente/ficha/fichaPrincipal.php?modo=normal&id_expediente=2165522433"
SEA_PAC_URL = "https://www.sea.gob.cl/portal-de-participacion-ciudadana-y-consulta-indigena/proyecto/conjunto-habitacional-eyzaguirre"
ADENDA_INDEX_URL = "https://ambihub.cl/seia/anexos?f_cap=Anexos&f_tipo=DIA&page=3"

# Punto de referencia publicado por la Municipalidad de Puente Alto para
# "Eyzaguirre 355". Se usa solo para llegar al sector en el mapa.
# NO se presenta como vértice ni como polígono oficial del Lote G-1.
PROJECT_REFERENCE_LAT = -33.613112
PROJECT_REFERENCE_LON = -70.570855

def _header(stage, title, purpose):
    header(
        f"ETAPA {stage} · LABORATORIO 2",
        title,
        purpose,
        show_overview=False,
        duration_minutes=25 if stage not in (9, 10) else 35,
    )

def _save(lab, saved, stage):
    saved[f"c4l2_updated_{stage}"] = _now()
    _save_future_state(lab["id"], saved)

def _stage0(lab, saved):
    title, objective, concept, activity = lab["stages"][0]
    _header(0, title, objective)
    st.markdown(concept)
    st.info("Este laboratorio seguirá un proyecto real del SEIA a lo largo de sus etapas. La Etapa 1 comienza reconstruyendo el proyecto antes de cualquier modelación acústica.")

def _stage1(lab, saved):
    _header(
        1,
        "Conoce el proyecto · Conjunto Habitacional Eyzaguirre",
        "Reconstruir ubicación, escala, etapas, maquinaria y cronograma del proyecto a partir de su expediente ambiental antes de representarlo acústicamente.",
    )

    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:22px;padding:22px 24px;
        background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.1em;color:#087ba0">PROYECTO REAL · SEIA</div>
          <div style="font-size:1.45rem;font-weight:900;color:#173b53;margin:.35rem 0">
            Conjunto Habitacional Eyzaguirre
          </div>
          <div style="color:#506d7f;line-height:1.6">
            En este laboratorio no inventaremos una obra. Partiremos del expediente ambiental,
            reconstruiremos su geometría y secuencia constructiva y, en las etapas siguientes,
            transformaremos esos antecedentes en un modelo acústico.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .c4l2-table-head{
            display:flex;align-items:flex-start;gap:13px;
            padding:15px 17px;margin:.55rem 0 .55rem;
            border:1px solid #d8e6ee;border-radius:16px;
            background:linear-gradient(135deg,#ffffff,#f7fbfd);
            box-shadow:0 5px 16px rgba(23,59,83,.045);
        }
        .c4l2-table-icon{
            width:38px;height:38px;border-radius:11px;
            display:flex;align-items:center;justify-content:center;
            background:#e9f7fb;color:#087ba0;font-size:1.05rem;
            flex:0 0 38px;
        }
        .c4l2-table-kicker{
            font-size:.68rem;font-weight:900;letter-spacing:.09em;
            color:#087ba0;margin-bottom:.15rem;
        }
        .c4l2-table-title{
            font-size:.98rem;font-weight:850;color:#173b53;
            margin-bottom:.15rem;
        }
        .c4l2-table-copy{
            font-size:.79rem;color:#667f8f;line-height:1.45;
        }
        div[data-testid="stDataFrame"]{
            border:1px solid #d9e6ed !important;
            border-radius:15px !important;
            overflow:hidden !important;
            box-shadow:0 4px 14px rgba(23,59,83,.04) !important;
            margin-bottom:.75rem !important;
        }
        div[data-testid="stDataFrame"] [role="columnheader"]{
            font-weight:800 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Expediente SEIA", "2165522433")
    k2.metric("Predio aprox.", "22.701 m²")
    k3.metric("Torres", "6")
    k4.metric("Viviendas", "360")

    st.markdown("### 1 · Abre las fuentes oficiales")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.link_button("🔎 Ficha oficial SEIA", SEA_PROJECT_URL, use_container_width=True)
    with c2:
        st.link_button("📄 Página pública del proyecto", SEA_PAC_URL, use_container_width=True)
    with c3:
        st.link_button("📚 Anexos / Adenda", ADENDA_INDEX_URL, use_container_width=True)
    st.caption(
        "Trabaja siempre desde documentos del expediente. Para esta etapa interesa especialmente la Descripción del Proyecto, "
        "los Antecedentes del Proyecto, Ruido y Vibraciones, Ficha Resumen y Adenda/Adenda Complementaria."
    )

    st.markdown("### 2 · Reconoce la ubicación y la escala")
    left,right = st.columns([1.2,.8], gap="large")
    with left:
        st.markdown(
            """
            **Antecedentes documentados**

            - **Dirección:** Avenida Eyzaguirre N.º 0355, Lote G-1.
            - **Comuna:** Puente Alto, Región Metropolitana.
            - **Superficie del terreno:** aproximadamente 22.701 m².
            - **Proyecto:** 6 torres de 4 pisos.
            - **Programa:** 360 departamentos, estacionamientos, locales comerciales y sedes sociales.
            - **Acceso vehicular indicado por SEA:** calle Carlos Aguirre Luco.
            """
        )
    with right:
        st.markdown(
            f"""
            <div style="border:1px solid #d8e6ee;border-radius:18px;padding:17px;background:#fff">
              <div style="font-size:.72rem;font-weight:850;color:#087ba0">PUNTO DE REFERENCIA PARA LLEGAR AL SECTOR</div>
              <div style="font-size:1.05rem;font-weight:850;color:#173b53;margin:.45rem 0">Lat {PROJECT_REFERENCE_LAT:.6f}<br>Lon {PROJECT_REFERENCE_LON:.6f}</div>
              <div style="font-size:.82rem;color:#647d8c;line-height:1.45">
                Coordenada pública asociada a Eyzaguirre 355. Sirve para centrar el mapa;
                <b>no es un vértice del Lote G-1</b>.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "No se estiman ni inventan vértices del predio. Mientras no se disponga del plano georreferenciado oficial con su "
        "tabla de coordenadas, el punto anterior se usa solo para localizar el sector. Los vértices deben obtenerse del "
        "antecedente cartográfico oficial del expediente."
    )

    st.markdown("### 3 · Lleva el proyecto a Noise Map Lab")
    a,b = st.columns([.68,.32], gap="large")
    with a:
        st.markdown(
            """
            **Procedimiento de esta etapa**

            1. Abre Noise Map Lab.
            2. Busca **“Avenida Eyzaguirre 355, Puente Alto”** o usa la coordenada de referencia.
            3. Contrasta el mapa con el plano/antecedente cartográfico del expediente.
            4. Cuando identifiques el polígono oficial, reconstruye su perímetro con **líneas auxiliares**.
            5. Nombra los vértices **V1, V2, V3…** y registra sus coordenadas.
            6. **No dibujes todavía el área de cálculo.** El límite del predio y el dominio acústico son objetos distintos.
            """
        )
    with b:
        st.link_button("🗺️ Abrir Noise Map Lab", NOISEMAP_URL, use_container_width=True)
        st.caption("Primero georreferencia el proyecto; la modelación vendrá después.")

    st.info(
        "Criterio de trabajo: **predio = líneas auxiliares**. El área de cálculo se definirá en una etapa posterior cuando ya existan fuentes y receptores."
    )

    st.markdown(
        """
        <div class="c4l2-table-head">
          <div class="c4l2-table-icon">📍</div>
          <div>
            <div class="c4l2-table-kicker">GEORREFERENCIACIÓN</div>
            <div class="c4l2-table-title">Registro de vértices del predio</div>
            <div class="c4l2-table-copy">Una fila por vértice del polígono oficial. Agrega o elimina filas según el plano y conserva el orden V1, V2, V3…</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    vertex_saved=saved.get("c4l2_s1_vertices_table") or [
        {"Vértice":"V1","Latitud":None,"Longitud":None},
        {"Vértice":"V2","Latitud":None,"Longitud":None},
        {"Vértice":"V3","Latitud":None,"Longitud":None},
        {"Vértice":"V4","Latitud":None,"Longitud":None},
    ]
    vertex_df=st.data_editor(
        pd.DataFrame(vertex_saved),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="c4l2_s1_vertices_editor",
        row_height=42,
        column_config={
            "Vértice":st.column_config.TextColumn("Vértice",help="Ej.: V1, V2, V3",width="small"),
            "Latitud":st.column_config.NumberColumn("Latitud",format="%.6f",width="medium"),
            "Longitud":st.column_config.NumberColumn("Longitud",format="%.6f",width="medium"),
        },
    )

    st.markdown("### 4 · Reconstruye las partes principales del proyecto")
    st.markdown(
        """
        <div class="c4l2-table-head">
          <div class="c4l2-table-icon">🏗️</div>
          <div>
            <div class="c4l2-table-kicker">PARTES Y OBRAS</div>
            <div class="c4l2-table-title">Inventario físico del proyecto</div>
            <div class="c4l2-table-copy">Registra cada parte u obra reconocida en la Descripción del Proyecto e indica cantidad, ubicación y documento donde la encontraste.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    parts_saved=saved.get("c4l2_s1_parts_table") or [
        {"Parte / obra":"","Cantidad":"","Ubicación / sector":"","Fuente documental":""},
        {"Parte / obra":"","Cantidad":"","Ubicación / sector":"","Fuente documental":""},
        {"Parte / obra":"","Cantidad":"","Ubicación / sector":"","Fuente documental":""},
        {"Parte / obra":"","Cantidad":"","Ubicación / sector":"","Fuente documental":""},
    ]
    parts_df=st.data_editor(
        pd.DataFrame(parts_saved),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="c4l2_s1_parts_editor",
        row_height=42,
        column_config={
            "Parte / obra":st.column_config.TextColumn("Parte / obra",help="Ej.: torre, estacionamiento, instalación de faena",width="medium"),
            "Cantidad":st.column_config.TextColumn("Cantidad",width="small"),
            "Ubicación / sector":st.column_config.TextColumn("Ubicación / sector",width="medium"),
            "Fuente documental":st.column_config.TextColumn("Fuente documental",help="Documento o anexo donde lo identificaste",width="large"),
        },
    )

    st.markdown("### 5 · Reconstruye las etapas constructivas")
    st.markdown(
        """
        <div class="c4l2-table-head">
          <div class="c4l2-table-icon">🧱</div>
          <div>
            <div class="c4l2-table-kicker">SECUENCIA CONSTRUCTIVA</div>
            <div class="c4l2-table-title">Etapas y frentes de trabajo</div>
            <div class="c4l2-table-copy">Ordena la secuencia según el expediente. Cada fila debe representar una etapa o frente con su actividad principal, sector y respaldo documental.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    phases_saved=saved.get("c4l2_s1_phases_table") or [
        {"N°":1,"Etapa / frente":"","Actividad principal":"","Sector del predio":"","Documento de respaldo":""},
        {"N°":2,"Etapa / frente":"","Actividad principal":"","Sector del predio":"","Documento de respaldo":""},
        {"N°":3,"Etapa / frente":"","Actividad principal":"","Sector del predio":"","Documento de respaldo":""},
        {"N°":4,"Etapa / frente":"","Actividad principal":"","Sector del predio":"","Documento de respaldo":""},
    ]
    phases_df=st.data_editor(
        pd.DataFrame(phases_saved),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="c4l2_s1_phases_editor",
        row_height=42,
        column_config={
            "N°":st.column_config.NumberColumn("N°",min_value=1,step=1,width="small"),
            "Etapa / frente":st.column_config.TextColumn("Etapa / frente",width="medium"),
            "Actividad principal":st.column_config.TextColumn("Actividad principal",width="large"),
            "Sector del predio":st.column_config.TextColumn("Sector del predio",width="medium"),
            "Documento de respaldo":st.column_config.TextColumn("Documento de respaldo",width="large"),
        },
    )

    st.markdown("### 6 · Identifica maquinaria y equipos")
    st.markdown(
        """
        <div class="c4l2-table-head">
          <div class="c4l2-table-icon">🚜</div>
          <div>
            <div class="c4l2-table-kicker">FUENTES POTENCIALES</div>
            <div class="c4l2-table-title">Maquinaria y equipos declarados</div>
            <div class="c4l2-table-copy">Busca los equipos en la Descripción del Proyecto y en Ruido y Vibraciones. Todavía no necesitas asignar niveles BS 5228.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    machinery_saved=saved.get("c4l2_s1_machinery_table") or [
        {"Máquina / equipo":"","Cantidad":None,"Etapa asociada":"","Actividad":"","Tipo":"","Fuente documental":""},
        {"Máquina / equipo":"","Cantidad":None,"Etapa asociada":"","Actividad":"","Tipo":"","Fuente documental":""},
        {"Máquina / equipo":"","Cantidad":None,"Etapa asociada":"","Actividad":"","Tipo":"","Fuente documental":""},
        {"Máquina / equipo":"","Cantidad":None,"Etapa asociada":"","Actividad":"","Tipo":"","Fuente documental":""},
    ]
    machinery_df=st.data_editor(
        pd.DataFrame(machinery_saved),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="c4l2_s1_machinery_editor",
        row_height=42,
        column_config={
            "Máquina / equipo":st.column_config.TextColumn("Máquina / equipo",width="medium"),
            "Cantidad":st.column_config.NumberColumn("Cantidad",min_value=0,step=1,width="small"),
            "Etapa asociada":st.column_config.TextColumn("Etapa asociada",width="medium"),
            "Actividad":st.column_config.TextColumn("Actividad",width="large"),
            "Tipo":st.column_config.SelectboxColumn("Tipo",options=["Fija","Móvil","Frente de trabajo","Auxiliar","No definido"],width="medium"),
            "Fuente documental":st.column_config.TextColumn("Fuente documental",width="large"),
        },
    )

    st.markdown("### 7 · Reconstruye el cronograma")
    st.markdown(
        """
        <div class="c4l2-table-head">
          <div class="c4l2-table-icon">🗓️</div>
          <div>
            <div class="c4l2-table-kicker">PROGRAMACIÓN DE OBRA</div>
            <div class="c4l2-table-title">Cronograma resumido</div>
            <div class="c4l2-table-copy">Una fila por actividad o etapa. Registra solo fechas, duraciones y superposiciones que puedas sostener con el expediente.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    chronology_saved=saved.get("c4l2_s1_chronology_table") or [
        {"Etapa / actividad":"","Inicio":"","Término":"","Duración":"","¿Se superpone?":"","Observación":""},
        {"Etapa / actividad":"","Inicio":"","Término":"","Duración":"","¿Se superpone?":"","Observación":""},
        {"Etapa / actividad":"","Inicio":"","Término":"","Duración":"","¿Se superpone?":"","Observación":""},
        {"Etapa / actividad":"","Inicio":"","Término":"","Duración":"","¿Se superpone?":"","Observación":""},
    ]
    chronology_df=st.data_editor(
        pd.DataFrame(chronology_saved),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="c4l2_s1_chronology_editor",
        row_height=42,
        column_config={
            "Etapa / actividad":st.column_config.TextColumn("Etapa / actividad",width="large"),
            "Inicio":st.column_config.TextColumn("Inicio",help="Mes, semana o fecha según documento",width="small"),
            "Término":st.column_config.TextColumn("Término",width="small"),
            "Duración":st.column_config.TextColumn("Duración",width="small"),
            "¿Se superpone?":st.column_config.SelectboxColumn("¿Se superpone?",options=["Sí","No","No indicado"],width="medium"),
            "Observación":st.column_config.TextColumn("Observación",width="large"),
        },
    )

    st.markdown("### 8 · Cierra la ficha del proyecto")
    synthesis = st.text_area(
        "Síntesis técnica",
        value=saved.get("c4l2_s1_synthesis",""),
        placeholder=(
            "Resume por qué la geometría, el cronograma y la maquinaria son necesarios antes de construir un modelo de ruido."
        ),
        height=125,
        key="c4l2_s1_synthesis_input",
    )

    if st.button("✓ Guardar ficha del proyecto", type="primary", use_container_width=True, key="c4l2_s1_save"):
        def _records_without_empty_rows(df, main_column):
            clean=df.copy()
            clean=clean.where(pd.notna(clean),None)
            return [
                row for row in clean.to_dict("records")
                if str(row.get(main_column) or "").strip()
            ]

        vertex_records=_records_without_empty_rows(vertex_df,"Vértice")
        part_records=_records_without_empty_rows(parts_df,"Parte / obra")
        phase_records=_records_without_empty_rows(phases_df,"Etapa / frente")
        machinery_records=_records_without_empty_rows(machinery_df,"Máquina / equipo")
        chronology_records=_records_without_empty_rows(chronology_df,"Etapa / actividad")

        missing=[]
        valid_vertices=[
            r for r in vertex_records
            if r.get("Latitud") is not None and r.get("Longitud") is not None
        ]
        if len(valid_vertices) < 3: missing.append("al menos 3 vértices con latitud y longitud")
        if len(part_records) < 3: missing.append("al menos 3 partes u obras")
        if len(phase_records) < 3: missing.append("al menos 3 etapas constructivas")
        if len(machinery_records) < 3: missing.append("al menos 3 máquinas o equipos")
        if len(chronology_records) < 3: missing.append("al menos 3 filas del cronograma")
        if len(synthesis.strip()) < 100: missing.append("síntesis técnica")

        if missing:
            st.warning("Completa: " + ", ".join(missing) + ".")
        else:
            saved.update({
                "c4l2_s1_vertices_table":vertex_records,
                "c4l2_s1_parts_table":part_records,
                "c4l2_s1_phases_table":phase_records,
                "c4l2_s1_machinery_table":machinery_records,
                "c4l2_s1_chronology_table":chronology_records,
                "c4l2_s1_synthesis":synthesis,
                "done_1":True,
            })
            _save(lab,saved,1)
            st.success("Ficha guardada. La información quedó estructurada para utilizarla en las siguientes etapas.")

    if st.session_state.get("role") == "Docente":
        with st.expander("👨‍🏫 Pauta docente · Etapa 1", expanded=False):
            st.markdown(
                """
                **Datos mínimos documentados que deben reconocer**

                - Proyecto: Conjunto Habitacional Eyzaguirre.
                - Expediente: 2165522433.
                - Titular: Entidad Patrocinante Unión Ltda.
                - Dirección: Av. Eyzaguirre N.º 0355, Lote G-1, Puente Alto.
                - Superficie aproximada: 22.701 m².
                - 6 torres de 4 pisos.
                - 360 departamentos.
                - 277 estacionamientos vehiculares.
                - 106 estacionamientos de bicicletas.
                - 4 locales comerciales.
                - 3 sedes sociales.
                - Accesos vehiculares informados por calle Carlos Aguirre Luco.

                **Revisión espacial**

                El alumno debe distinguir correctamente entre **punto de referencia**, **vértices del predio**
                y **área de cálculo**. No se debe aceptar un polígono inventado a partir de una coordenada central.
                """
            )
            st.warning(
                "La tabla exacta de vértices debe provenir del plano/georreferenciación oficial del expediente. "
                "No se entrega una geometría estimada como si fuera documental."
            )

def _generic(stage, lab, saved):
    title, objective, concept, activity = lab["stages"][stage]
    _header(stage, title, objective)
    st.markdown("### Desarrollo técnico")
    st.markdown(concept)
    st.markdown("### Actividad")
    st.write(activity)
    st.info("Esta etapa se desarrollará progresivamente a partir del proyecto Conjunto Habitacional Eyzaguirre.")

_STAGES = [_stage0, _stage1] + [None] * 9

def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage=max(0,min(int(stage),10))
    if stage==0:
        return _stage0(lab,saved)
    if stage==1:
        return _stage1(lab,saved)
    return _generic(stage,lab,saved)
