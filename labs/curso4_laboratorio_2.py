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

    st.markdown("#### Registro de vértices")
    vertex_text = st.text_area(
        "Copia aquí las coordenadas de los vértices que obtengas del plano oficial",
        value=saved.get("c4l2_s1_vertices",""),
        placeholder=(
            "Ejemplo de formato (no son coordenadas del proyecto):\n"
            "V1 | lat ... | lon ...\nV2 | lat ... | lon ...\nV3 | lat ... | lon ..."
        ),
        height=140,
        key="c4l2_s1_vertices_input",
    )

    st.markdown("### 4 · Reconstruye las partes principales del proyecto")
    st.markdown(
        "La ficha SEA informa 6 torres de 4 pisos, 360 departamentos, 277 estacionamientos vehiculares, "
        "106 estacionamientos de bicicletas, 4 locales comerciales y 3 sedes sociales. "
        "Ahora revisa la Descripción del Proyecto y reconoce cómo se organiza físicamente la obra."
    )
    project_parts = st.text_area(
        "Partes y obras que identificaste",
        value=saved.get("c4l2_s1_parts",""),
        placeholder="Torres, estacionamientos, circulaciones, áreas verdes, instalaciones de faena, accesos, obras exteriores, etc.",
        height=120,
        key="c4l2_s1_parts_input",
    )

    st.markdown("### 5 · Reconstruye las etapas constructivas")
    st.caption("No uses una secuencia genérica: contrástala con lo declarado en la Descripción del Proyecto y sus actualizaciones.")
    phases = st.text_area(
        "Etapas / frentes de trabajo identificados",
        value=saved.get("c4l2_s1_phases",""),
        placeholder=(
            "Ej.: preparación / movimiento de tierras / fundaciones / estructura / terminaciones / urbanización. "
            "Registra solo lo que puedas sustentar con el expediente."
        ),
        height=145,
        key="c4l2_s1_phases_input",
    )

    st.markdown("### 6 · Identifica maquinaria y equipos")
    st.markdown(
        "Busca la maquinaria declarada tanto en la **Descripción del Proyecto** como en el antecedente de **Ruido y Vibraciones**. "
        "En esta etapa todavía no necesitas buscar niveles BS 5228: primero identifica qué equipo existe y en qué fase opera."
    )
    machinery = st.text_area(
        "Maquinaria / equipos y etapa asociada",
        value=saved.get("c4l2_s1_machinery",""),
        placeholder=(
            "Formato sugerido:\n"
            "Equipo | cantidad si está declarada | etapa | actividad\n"
            "Equipo | cantidad | etapa | actividad"
        ),
        height=170,
        key="c4l2_s1_machinery_input",
    )

    st.markdown("### 7 · Reconstruye el cronograma")
    chronology = st.text_area(
        "Cronograma de construcción",
        value=saved.get("c4l2_s1_chronology",""),
        placeholder=(
            "Registra duración total y secuencia de actividades. Indica qué etapas podrían superponerse "
            "solo cuando el cronograma del expediente lo permita."
        ),
        height=145,
        key="c4l2_s1_chronology_input",
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
        missing=[]
        if len(project_parts.strip()) < 60: missing.append("partes y obras")
        if len(phases.strip()) < 60: missing.append("etapas constructivas")
        if len(machinery.strip()) < 80: missing.append("maquinaria")
        if len(chronology.strip()) < 60: missing.append("cronograma")
        if len(synthesis.strip()) < 100: missing.append("síntesis")
        if missing:
            st.warning("Completa con mayor detalle: " + ", ".join(missing) + ".")
        else:
            saved.update({
                "c4l2_s1_vertices":vertex_text,
                "c4l2_s1_parts":project_parts,
                "c4l2_s1_phases":phases,
                "c4l2_s1_machinery":machinery,
                "c4l2_s1_chronology":chronology,
                "c4l2_s1_synthesis":synthesis,
                "done_1":True,
            })
            _save(lab,saved,1)
            st.success("Ficha guardada. Ya tienes la base documental para comenzar a transformar la obra en un modelo acústico.")

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
