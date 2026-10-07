"""Curso 4 · Laboratorio 2 · Proyecto real Eyzaguirre.

Renderer específico del Laboratorio 2. La Etapa 1 reconstruye el proyecto real
Conjunto Habitacional Eyzaguirre desde su expediente SEIA antes de modelar.
"""

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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


def _professional_grid(df, key, widths=None, select_options=None, numeric_columns=None, height=260):
    """Grilla editable con encabezados claros y líneas visibles."""
    widths=widths or {}
    select_options=select_options or {}
    numeric_columns=set(numeric_columns or [])
    gb=GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        editable=True,
        sortable=False,
        filter=False,
        resizable=True,
        wrapText=False,
        suppressMovable=True,
    )
    for column in df.columns:
        kwargs={"headerName":str(column).upper()}
        if column in widths:
            kwargs["width"]=widths[column]
            kwargs["minWidth"]=max(80, int(widths[column]*0.75))
        if column in select_options:
            kwargs["cellEditor"]="agSelectCellEditor"
            kwargs["cellEditorParams"]={"values":select_options[column]}
        if column in numeric_columns:
            kwargs["type"]=["numericColumn"]
        gb.configure_column(column, **kwargs)

    gb.configure_grid_options(
        rowHeight=42,
        headerHeight=46,
        suppressHorizontalScroll=False,
        singleClickEdit=True,
        stopEditingWhenCellsLoseFocus=True,
    )
    options=gb.build()

    custom_css={
        ".ag-root-wrapper":{
            "border":"1px solid #b8cad7 !important",
            "border-radius":"12px !important",
            "overflow":"hidden !important",
            "box-shadow":"0 4px 14px rgba(23,59,83,.06) !important",
        },
        ".ag-header":{
            "background":"#0b5f8f !important",
            "border-bottom":"2px solid #084a70 !important",
        },
        ".ag-header-row":{
            "background":"#0b5f8f !important",
        },
        ".ag-header-cell":{
            "background":"#0b5f8f !important",
            "color":"#ffffff !important",
            "font-weight":"800 !important",
            "font-size":"12px !important",
            "letter-spacing":".035em !important",
            "border-right":"1px solid rgba(255,255,255,.22) !important",
        },
        ".ag-header-cell-label":{
            "justify-content":"flex-start !important",
        },
        ".ag-row":{
            "border-bottom":"1px solid #d7e2e9 !important",
        },
        ".ag-row-even":{
            "background":"#ffffff !important",
        },
        ".ag-row-odd":{
            "background":"#f8fbfd !important",
        },
        ".ag-cell":{
            "border-right":"1px solid #dfe8ee !important",
            "display":"flex !important",
            "align-items":"center !important",
            "font-size":"13px !important",
            "color":"#243746 !important",
            "padding-left":"10px !important",
            "padding-right":"10px !important",
        },
        ".ag-cell-focus":{
            "border":"2px solid #1496c8 !important",
            "box-shadow":"inset 0 0 0 1px #1496c8 !important",
        },
        ".ag-row-hover":{
            "background":"#eef7fb !important",
        },
    }

    result=AgGrid(
        df,
        gridOptions=options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        data_return_mode="AS_INPUT",
        fit_columns_on_grid_load=False,
        height=height,
        key=key,
        custom_css=custom_css,
        theme="streamlit",
        allow_unsafe_jscode=False,
    )
    data=result.get("data",df)
    return pd.DataFrame(data)

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
    vertex_df=_professional_grid(
        pd.DataFrame(vertex_saved),
        key="c4l2_s1_vertices_grid",
        widths={"Vértice":110,"Latitud":180,"Longitud":180},
        numeric_columns=["Latitud","Longitud"],
        height=245,
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
    parts_df=_professional_grid(
        pd.DataFrame(parts_saved),
        key="c4l2_s1_parts_grid",
        widths={"Parte / obra":220,"Cantidad":110,"Ubicación / sector":220,"Fuente documental":280},
        height=245,
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
    phases_df=_professional_grid(
        pd.DataFrame(phases_saved),
        key="c4l2_s1_phases_grid",
        widths={"N°":85,"Etapa / frente":200,"Actividad principal":260,"Sector del predio":190,"Documento de respaldo":260},
        numeric_columns=["N°"],
        height=245,
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
    machinery_df=_professional_grid(
        pd.DataFrame(machinery_saved),
        key="c4l2_s1_machinery_grid",
        widths={"Máquina / equipo":210,"Cantidad":100,"Etapa asociada":180,"Actividad":240,"Tipo":160,"Fuente documental":250},
        select_options={"Tipo":["Fija","Móvil","Frente de trabajo","Auxiliar","No definido"]},
        numeric_columns=["Cantidad"],
        height=245,
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
    chronology_df=_professional_grid(
        pd.DataFrame(chronology_saved),
        key="c4l2_s1_chronology_grid",
        widths={"Etapa / actividad":220,"Inicio":120,"Término":120,"Duración":120,"¿Se superpone?":150,"Observación":280},
        select_options={"¿Se superpone?":["Sí","No","No indicado"]},
        height=245,
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
