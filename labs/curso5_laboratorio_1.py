"""Curso 5 · Laboratorio 1 · Certificación acústica de viviendas.

Caso ficticio de diseño acústico residencial. SONARA se utiliza como motor de
cálculo externo; la selección de indicadores, la trazabilidad y la
clasificación ISO/TS 19488 son responsabilidad del estudiante.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


CLASS_ID = "clase-09-certificaciones-lab-1"
SONARA_URL = "https://sonara-ea1b.onrender.com/"
ISO_STATUS_URL = "https://www.iso.org/standard/77742.html"
C5L1_STAGE_MINUTES = [10, 20, 20, 20, 20, 30, 25, 25, 25, 25, 30]
_RUNTIME_PROTECTED = {"run_stage", "_bind_runtime", "_RUNTIME_PROTECTED", "C5L1_STAGE_MINUTES"}


def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED:
            module_globals[name] = value


PROJECT = {
    "name": "Edificio Los Alerces",
    "status": "Caso ficticio de uso exclusivamente académico",
    "location": "Comuna urbana de Santiago, Chile",
    "use": "Edificio residencial en altura",
    "storeys": 5,
    "dwellings": 20,
    "floor_height_m": 2.50,
    "structural_system": "Muros y losas de hormigón armado",
    "evaluation_unit": "Departamento A-302 · tercer piso",
    "adjacencies": {
        "horizontal": "Departamento A-301 · muro medianero",
        "vertical": "Departamento A-402 · losa superior",
        "facade": "Estar-comedor y dormitorio principal · fachada norte",
        "services": "Baño principal junto a shaft sanitario S-1",
    },
}

ROOMS = [
    ["Estar-comedor", 20.4, 51.0, "Norte", "Fachada + medianero A-301"],
    ["Dormitorio principal", 11.5, 28.8, "Norte", "Fachada"],
    ["Dormitorio 2", 9.2, 23.0, "Sur", "Pasillo común"],
    ["Cocina", 7.8, 19.5, "Interior", "Núcleo húmedo / baño"],
    ["Baño principal", 4.1, 10.3, "Interior", "Shaft S-1"],
]

MATERIALS = [
    ["M-01", "Muro medianero A-301/A-302", "Hormigón armado", "180 mm", "Continuo entre losas; encuentros sellados"],
    ["L-01", "Losa entre A-302/A-402", "Hormigón armado", "160 mm", "Piso: resiliente 10 + sobrelosa 40 + terminación 10 mm"],
    ["F-01", "Paño opaco fachada norte", "HA + aislante + placa de yeso", "150 + 50 + 15 mm", "Trasdosado desacoplado"],
    ["V-01", "Ventana estar", "DVH 6/12/4 · marco aluminio", "4.80 m²", "Juntas perimetrales continuas"],
    ["V-02", "Ventana dormitorio", "DVH 6/12/4 · marco aluminio", "2.40 m²", "Juntas perimetrales continuas"],
    ["T-01", "Tabique interior", "Yeso 12,5 + cámara 65 con lana + yeso 12,5", "90 mm", "Canales con banda resiliente"],
    ["S-01", "Shaft sanitario", "2 RF 12,5 + cámara 70 con lana + 2 RF 12,5", "120 mm", "Tuberías con abrazaderas resilientes"],
]

CALCULATION_CASES = {
    "Aéreo interior": {
        "code": "AI-01",
        "source": "Estar A-301",
        "receiver": "Estar A-302",
        "descriptor": "DₙT,w (C; Ctr)",
        "geometry": "Muro M-01 · 10,2 m² · V receptor 51,0 m³",
    },
    "Impacto": {
        "code": "IM-01",
        "source": "Estar A-402",
        "receiver": "Estar A-302",
        "descriptor": "L′ₙT,w (CI)",
        "geometry": "Losa L-01 · 20,4 m² · V receptor 51,0 m³",
    },
    "Fachada": {
        "code": "FA-01",
        "source": "Exterior norte",
        "receiver": "Estar A-302",
        "descriptor": "D₂m,nT,w (C; Ctr)",
        "geometry": "Fachada 15,3 m² · ventana V-01 4,8 m²",
    },
    "Instalaciones": {
        "code": "IN-01",
        "source": "Descarga sanitaria simultánea",
        "receiver": "Dormitorio principal A-302",
        "descriptor": "LAFmax,nT y/o LAeq,nT según condición declarada",
        "geometry": "Shaft S-01 junto a baño · dormitorio receptor V = 28,8 m³",
    },
}


def _asset(filename: str) -> Path:
    return PROJECT_ROOT / "assets" / "curso5_lab1" / filename


def _header(stage: int, title: str, purpose: str):
    header(
        f"ETAPA {stage} · LABORATORIO 1",
        title,
        purpose,
        show_overview=False,
        duration_minutes=C5L1_STAGE_MINUTES[stage],
    )


def _save(lab, saved, stage: int, **values):
    saved.update(values)
    saved[f"done_{stage}"] = True
    saved[f"c5l1_done_{stage}"] = True
    saved[f"c5l1_updated_{stage}"] = _now()
    _save_future_state(lab["id"], saved)


def _sonara_button(label="Abrir SONARA para calcular"):
    st.link_button(
        f"🔊 {label}",
        SONARA_URL,
        width="stretch",
        help="SONARA se abre en otra pestaña; conserva esta guía para registrar los resultados.",
    )
    st.caption(
        "SONARA entrega resultados de cálculo. La selección del descriptor, la comprobación de su alcance "
        "y la clasificación acústica son responsabilidad del alumno."
    )


def _project_badge():
    st.warning(
        "**CASO FICTICIO · Edificio Los Alerces.** La geometría y las materialidades fueron creadas para "
        "este laboratorio. No corresponden a una obra construida ni constituyen una certificación real."
    )


def _project_downloads():
    """Ficha completa de proyecto, recintos y materialidades en un CSV para Excel."""
    rows = [
        ["Proyecto", "Nombre", PROJECT["name"], "", ""],
        ["Proyecto", "Uso", PROJECT["use"], "", ""],
        ["Proyecto", "Pisos", PROJECT["storeys"], "", ""],
        ["Proyecto", "Viviendas", PROJECT["dwellings"], "", ""],
        ["Proyecto", "Unidad de estudio", PROJECT["evaluation_unit"], "", ""],
        ["Proyecto", "Altura interior [m]", PROJECT["floor_height_m"], "", ""],
    ]
    for name, area, volume, orientation, adjacency in ROOMS:
        rows.append(["Recinto", name, area, volume, f"{orientation} · {adjacency}"])
    for code, element, system, dimension, note in MATERIALS:
        rows.append(["Materialidad", f"{code} · {element}", system, dimension, note])
    csv = pd.DataFrame(
        rows,
        columns=["Sección", "Elemento / campo", "Valor / sistema", "Volumen / dimensión", "Observación"],
    ).to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "📊 Descargar ficha del proyecto para Excel (CSV)",
        data=csv,
        file_name="edificio_los_alerces_expediente.csv",
        mime="text/csv",
        width="stretch",
        key="c5l1_project_csv",
    )


def _show_drawing(filename: str, caption: str):
    path = _asset(filename)
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.error(f"No se encontró el plano académico: {filename}")



# Operational instructions follow the current SONARA screens.
SONARA_DESIGN_GUIDES = {
    "Aéreo interior": {
        "route": "Calculadora libre → Ruido aéreo; después Transmisión entre recintos (ISO 12354-1).",
        "inputs": [
            ["M-01 · separador", "Hormigón armado · 180 mm", "Selecciona una ficha con propiedades completas; registra densidad y procedencia."],
            ["Geometría AI-01", "S = 10,2 m² · V receptor = 51,0 m³", "Copia el TR adoptado desde tu protocolo; no confundas área de muro con área de piso."],
            ["Flancos", "Losa, muros laterales y fachada según planos", "Obtén espesores y longitudes de unión del expediente; justifica cualquier dato faltante."],
        ],
        "steps": [
            "En Ruido aéreo selecciona Panel simple y modela M-01 con una capa de hormigón de 180 mm. Conserva R(f), Rw, C y Ctr como resultados del elemento.",
            "Abre Transmisión entre recintos (ISO 12354-1). Ingresa S = 10,2 m², V = 51,0 m³ y el TR receptor declarado. Introduce el Rw calculado en «Rw elemento separador».",
            "Activa los flancos que existan en los planos. Para cada encuentro registra material, masa superficial, longitud y tipo de unión o Kij. Usa «Calcular con SONARA» cuando puedas definir sus capas.",
            "Identifica si domina el camino directo o uno lateral. Diseña una variante: modificar M-01 o añadir un trasdosado desacoplado; si domina un flanco, actúa sobre el encuentro correspondiente.",
            "Recalcula el descriptor entre recintos con la misma geometría y compara la variante con la base. Registra DₙT,w y las adaptaciones que correspondan a la curva final.",
        ],
        "limit": "El ingreso directo por Rw del módulo entre recintos reconstruye una curva de referencia: declara esa aproximación. No copies C y Ctr de la placa como si fueran los términos de la curva final entre recintos.",
        "evidence": "Configuración de M-01 y su variante, captura del visual constructivo, entradas de recintos/uniones, curvas y resultado final DₙT,w.",
    },
    "Impacto": {
        "route": "Calculadora libre → Ruido de impacto → ISO 12354-2.",
        "inputs": [
            ["L-01 · losa base", "Hormigón armado · 160 mm", "Registra la densidad seleccionada; SONARA obtiene la masa superficial."],
            ["Piso superior", "Piso: resiliente 10 + sobrelosa 40 + terminación 10 mm", "Capa resiliente 10 mm y terminación 10 mm (AC-04). La rigidez requiere ficha o hipótesis."],
            ["Geometría IM-01", "Área entrepiso = 20,4 m² · V = 51,0 m³", "Usa el mismo TR receptor en la comparación base/variante."],
        ],
        "steps": [
            "Selecciona ISO 12354-2 y «Calcular por masa superficial». Ingresa 160 mm y la densidad documentada del hormigón. No uses 200 mm sumando la sobrelosa a la losa estructural.",
            "Calcula primero la losa base sin revestimiento ni cielo. Guarda el resultado como IM-01 · Base y registra los flancos considerados.",
            "Para la variante, selecciona un revestimiento del catálogo con espectro ΔL medido y montaje compatible; documenta su ficha. Alternativamente usa «Piso flotante físico».",
            "En Piso flotante físico ingresa la masa superficial de la sobrelosa: m′ = densidad × 0,040 m. Ingresa la rigidez dinámica s′ de la capa resiliente desde una ficha; no la deduzcas solo de su espesor.",
            "Define el cielo inferior solo si forma parte de tu propuesta. Completa área 20,4 m², volumen 51,0 m³, TR y flancos; revisa el visual constructivo y recalcula.",
            "Compara L′ₙT,w y CI de base y variante; menor nivel de impacto significa mejor desempeño. Explica la influencia del piso, de los puentes rígidos y de los flancos.",
        ],
        "limit": "No sumes dos mejoras ΔL para el mismo sistema: el catálogo medido y el modelo físico son alternativas. La banda resiliente perimetral no equivale a una rigidez dinámica conocida.",
        "evidence": "Losa y densidad, ficha ΔL o masa/rigidez del piso físico, montaje, flancos, visual constructivo, curva y L′ₙT,w con CI.",
    },
    "Fachada": {
        "route": "Calculadora libre → Ruido aéreo para los componentes; después Fachada (ISO 12354-3).",
        "inputs": [
            ["Fachada FA-01", "Área total = 15,3 m² · V = 51,0 m³", "Mismo estar receptor que AI-01 e IM-01."],
            ["V-01 · ventana estar", "DVH 6/12/4 · 4,80 m²", "6 y 4 mm son vidrios; 12 mm es cámara, no una placa."],
            ["F-01 · paño opaco", "10,50 m² · HA 150 + cámara 50 + yeso 15 mm", "150 + 50 + 15 mm no se modela como tres capas sólidas adheridas."],
        ],
        "steps": [
            "Diseña F-01 en Ruido aéreo → Panel doble: hoja de hormigón de 150 mm, cámara de 50 mm con absorbente y hoja de yeso de 15 mm. Declara el montaje desacoplado y la ficha del absorbente.",
            "Diseña V-01 en Ruido aéreo → Ventana → DVH: vidrio 6 mm, aire 12 mm y vidrio 4 mm. Documenta que el conjunto real también depende de marco, juntas y condiciones de ensayo.",
            "Abre Fachada (ISO 12354-3). Ingresa volumen 51,0 m³ y área total 15,3 m². Crea dos componentes: opaco 10,50 m² y ventana 4,80 m².",
            "El selector SONARA de cada componente calcula una placa simple. Para trasladar tu panel doble o DVH usa «Manual Rw/Ctr» con sus resultados; documenta la reconstrucción espectral aproximada que realiza ese modo.",
            "Ingresa exposición exterior y corrección por forma a partir de antecedentes o hipótesis identificadas. Añade juntas o aireadores únicamente cuando puedas justificar sus datos.",
            "Compara una variante del componente dominante —ventana, sellos o paño opaco— manteniendo áreas y exposición. Guarda D₂m,nT,w y C/Ctr de la fachada completa.",
        ],
        "limit": "El modo Manual Rw/Ctr no transfiere íntegramente el espectro calculado del componente. Informa esa limitación. No uses el Rw de la ventana como resultado global ni registres el dormitorio V-02 dentro del caso del estar V-01.",
        "evidence": "Modelos F-01 y V-01, Rw/Ctr transferidos, áreas, hipótesis exterior/forma, juntas consideradas y curva final de fachada.",
    },
    "Instalaciones": {
        "route": "Calculadora libre → Ruido de instalaciones (EN 12354-5).",
        "inputs": [
            ["IN-01 · descarga sanitaria", "Condición de operación definida por el alumno", "Se requiere espectro de fuente trazable; los valores iniciales de SONARA son ejemplos."],
            ["S-01 · cierre", "2 RF 12,5 + cámara 70 + 2 RF 12,5 = 120 mm", "Ver AC-04; selecciona las fichas de placas y absorbente. No asignes 120 mm a cada capa."],
            ["Receptor", "Dormitorio principal · V = 28,8 m³", "Declara TR, absorción equivalente y recorrido; A ≈ 0,16 V/T como hipótesis de campo difuso."],
        ],
        "steps": [
            "Define una descarga o ciclo de funcionamiento reproducible, su duración y simultaneidad. Obtén datos espectrales de fabricante o ensayo; si no existen, identifica el cálculo como escenario académico.",
            "Diseña el cierre S-01 en Ruido aéreo → Panel doble con espesores y cámara expresamente definidos. Conserva R(f), no solo Rw.",
            "En Ruido de instalaciones selecciona la condición de funcionamiento y la vía «Aérea · recinto adyacente». Ingresa el espectro Lw, el área real del cierre, R por bandas de octava y las absorciones fuente/receptor.",
            "Para las fijaciones usa una vía «Estructural» solo con nivel de fuerza/velocidad y función de transferencia instalada compatibles. Una abrazadera resiliente no se representa restando una atenuación arbitraria.",
            "Usa «Agregar vías simultáneas» si cuentas con datos para la vía aérea y estructural. Compara mejoras de cierre, sellado o fijaciones manteniendo la misma descarga y receptor.",
            "Registra LAeq únicamente para la condición temporal definida. El modo intermitente entrega LAFmax estimado: declara su alcance y no conviertas un LAeq en un máximo FAST.",
        ],
        "limit": "Si no puedes justificar uno de los descriptores, déjalo sin determinar y documenta qué dato o medición falta. No inventes niveles para completar el expediente.",
        "evidence": "Fuente y bandas, operación, cierre S-01, fijaciones, transferencia/atenuación justificadas y descriptor temporal compatible.",
    },
}


def _sonara_design_guide(case_name):
    guide = SONARA_DESIGN_GUIDES[case_name]
    st.markdown("### 🛠️ Cómo diseñar esta solución en SONARA")
    st.info("**Ruta en SONARA:** " + guide["route"])
    st.dataframe(
        pd.DataFrame(guide["inputs"], columns=["Elemento / dato", "Entrada del caso", "Comprobación"]),
        hide_index=True, width="stretch",
    )
    st.markdown("\n\n".join(f"{index}. {step}" for index, step in enumerate(guide["steps"], 1)))
    st.warning(guide["limit"])
    st.markdown("**Evidencia que debes conservar:** " + guide["evidence"])
    st.caption("El traslado de datos entre SONARA y este laboratorio es manual; abrir SONARA no importa ni guarda resultados automáticamente.")


def _download_plan_set(key):
    path = _asset("los_alerces_planos_acusticos.pdf")
    if path.is_file():
        st.download_button(
            "📐 Descargar juego de planos · PDF A3 (4 láminas)",
            data=path.read_bytes(), file_name=path.name, mime="application/pdf",
            width="stretch", key=key,
        )
    else:
        st.error("El juego de planos PDF no está disponible.")


def _download_standard(key):
    path = _asset("ISO-TS-19488-2021.pdf")
    if path.is_file():
        st.download_button(
            "📘 Descargar norma ISO/TS 19488:2021 · PDF",
            data=path.read_bytes(), file_name=path.name, mime="application/pdf",
            width="stretch", key=key,
        )
    else:
        st.error("El PDF de ISO/TS 19488:2021 no está disponible.")


def _design_context(saved):
    target = saved.get("c5l1_s3_target", "Sin definir")
    st.info(f"**Objetivo elegido en etapa 3:** {target}. Consulta el protocolo guardado antes de comparar variantes.")
    inputs = saved.get("c5l1_s4_inputs", {})
    if inputs:
        st.dataframe(pd.DataFrame([
            ["TR estar", inputs.get("tr_stay"), "s"],
            ["TR dormitorio", inputs.get("tr_bedroom"), "s"],
            ["Densidad HA", inputs.get("rho_ha"), "kg/m³"],
            ["Densidad sobrelosa", inputs.get("rho_screed"), "kg/m³"],
            ["Rigidez dinámica s′", inputs.get("dynamic_stiffness"), "MN/m³"],
            ["Exposición exterior Lden", inputs.get("lden"), "dB"],
        ], columns=["Dato del protocolo", "Valor", "Unidad"]), hide_index=True, width="stretch")
    else:
        st.warning("Aún no has guardado las entradas de la etapa 4. Defínelas o justifica las pendientes antes de calcular.")


def _result_form(lab, saved, stage, case_name, fields, prompt):
    case = CALCULATION_CASES[case_name]
    st.markdown(f"### Caso {case['code']} · {case_name}")
    st.markdown(
        f"**Fuente:** {case['source']}  \n**Receptor:** {case['receiver']}  \n"
        f"**Geometría:** {case['geometry']}  \n**Descriptor de trabajo:** {case['descriptor']}"
    )
    _design_context(saved)
    st.info(prompt)
    _sonara_design_guide(case_name)
    _sonara_button("Abrir SONARA para diseñar esta solución")

    stored = saved.get(f"c5l1_result_{case['code']}", {})
    st.markdown("### Registra tu solución final y la comparación con la base")
    st.caption("Usa tus propios cálculos; los números del ejemplo de etapa 3 no son resultados de este formulario.")
    with st.form(f"c5l1_form_{case['code']}"):
        values = {}
        cols = st.columns(min(3, len(fields)))
        for index, (key, label, unit) in enumerate(fields):
            values[key] = cols[index % len(cols)].number_input(
                f"{label} [{unit}]",
                value=stored.get(key),
                step=0.1,
                format="%.1f",
                placeholder="Resultado SONARA",
            )
        st.markdown("#### Comparación de diseño · base → variante")
        target = st.text_input(
            "Objetivo de diseño y descriptor",
            value=stored.get("target", saved.get("c5l1_s4_criteria", "")),
            placeholder="Umbral elegido por ti, sentido de comparación y referencia consultada.",
        )
        base_design = st.text_area(
            "Solución inicial y resultado base",
            value=stored.get("base_design", ""),
            placeholder="Capas, espesores, montaje y resultado antes de mejorar.",
        )
        design_change = st.text_area(
            "Cambio propuesto y efecto observado",
            value=stored.get("design_change", ""),
            placeholder="Qué cambiaste, qué mantuviste y por qué mejora o no el descriptor final.",
        )
        evidence = st.text_area(
            "Identificación de las evidencias de SONARA",
            value=stored.get("evidence", ""),
            placeholder="Nombre del proyecto/solución, fecha y archivos de curvas, capturas o informes conservados.",
        )
        undetermined = False
        normalized = False
        if case_name == "Instalaciones":
            normalized = st.checkbox(
                "He comprobado normalización a T₀ = 0,5 s y condición temporal de las salidas",
                value=bool(stored.get("normalized", False)),
            )
            undetermined = st.checkbox(
                "Hay un descriptor sin determinar por falta de antecedentes",
                value=bool(stored.get("undetermined", False)),
                help="Deja vacío el descriptor no sustentado y explica en la trazabilidad qué falta.",
            )
        notes = st.text_area(
            "Supuestos, configuración y trazabilidad",
            value=stored.get("notes", ""),
            height=120,
            placeholder="Modelo utilizado, elementos, dimensiones, uniones, fuente de datos y limitaciones.",
        )
        submitted = st.form_submit_button("Guardar resultados de diseño", width="stretch")
    if submitted:
        if any(value is None for value in values.values()) and not undetermined:
            st.warning("Completa los resultados o declara, en instalaciones, el descriptor sin determinar.")
        elif undetermined and all(value is not None for value in values.values()):
            st.warning("La declaración sin determinar requiere dejar vacío el resultado no sustentado.")
        elif case_name == "Instalaciones" and any(value is not None for value in values.values()) and not normalized:
            st.warning("Comprueba la normalización y la condición temporal antes de registrar un nivel como LAeq,nT o LAFmax,nT.")
        elif len(target.strip()) < 15 or len(base_design.strip()) < 40 or len(design_change.strip()) < 40 or len(evidence.strip()) < 15:
            st.warning("Registra objetivo (15 caracteres), base (40), cambio y efecto (40) e identificación de evidencia (15).")
        elif len(notes.strip()) < 80:
            st.warning("Documenta los supuestos y la configuración con al menos 80 caracteres.")
        else:
            payload = {
                **values, "notes": notes, "descriptor": case["descriptor"],
                "target": target, "base_design": base_design, "design_change": design_change,
                "evidence": evidence, "undetermined": undetermined, "normalized": normalized,
            }
            _save(lab, saved, stage, **{f"c5l1_result_{case['code']}": payload})
            st.success("Resultado guardado. La clase acústica todavía no ha sido asignada.")


def _stage0(lab, saved):
    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 1 · Certificación acústica de viviendas",
        "Una ruta de diseño desde el expediente del Edificio Los Alerces hasta la clasificación acústica justificada por el estudiante.",
        show_overview=False,
        duration_minutes=C5L1_STAGE_MINUTES[0],
    )

    active_minutes = sum(C5L1_STAGE_MINUTES[1:])
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Ruta guiada del Laboratorio 1</strong>'
        f'<br><span>Caso ficticio · Edificio Los Alerces · SONARA + ISO</span>'
        f'</div><div><strong>{active_minutes} min</strong></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:18px;padding:17px 19px;
        background:linear-gradient(135deg,#f8fcff,#edf6fb);margin:.8rem 0 1rem">
          <div style="font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
            CASO CONDUCTOR · PROYECTO FICTICIO
          </div>
          <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">
            Edificio Los Alerces · Departamento A-302
          </div>
          <div style="color:#587486;line-height:1.55;font-size:.84rem">
            Trabajarás con un expediente académico común de un edificio residencial de cinco pisos.
            Interpretarás planos y materialidades, prepararás modelos y registrarás resultados obtenidos
            mediante SONARA. La clasificación acústica final se realiza y justifica por cada estudiante,
            consultando ISO/TS 19488; la plataforma no asigna clases automáticamente.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )
    descriptions = [
        "Conoce el edificio, sus recintos, adyacencias, materiales y las situaciones acústicas que evaluarás.",
        "Lee cuatro láminas técnicas PNG/PDF, comprueba las cotas y reconoce caminos de transmisión.",
        "Comprende las clases ISO con un ejemplo resuelto y elige un objetivo de diseño.",
        "Prepara y guarda las entradas, fuentes e hipótesis para diseñar en SONARA.",
        "Calcula el aislamiento aéreo entre viviendas y documenta los caminos directos y laterales.",
        "Calcula el ruido de impacto a través de la losa y el efecto del sistema de piso.",
        "Evalúa el aislamiento de la fachada compuesta e identifica sus elementos más débiles.",
        "Registra el ruido de instalaciones, las condiciones de operación y las limitaciones del método.",
        "Consolida resultados, descriptores y evidencias sin asignar todavía la clase acústica.",
        "Consulta ISO/TS 19488, asigna y justifica la clasificación; entrega el expediente final.",
    ]
    cards = ""
    for stage in range(1, 11):
        title = lab["stages"][stage][0]
        cards += (
            '<div class="route-card">'
            f'<span class="step">{stage}</span><div>'
            f'<b>{title}</b>'
            f'<p>{descriptions[stage - 1]}</p>'
            f'<span class="route-time">⏱️ {C5L1_STAGE_MINUTES[stage]} min</span>'
            '</div></div>'
        )
    st.markdown(f'<div class="route-grid">{cards}</div>', unsafe_allow_html=True)

    st.success(
        "Resultado esperado: expediente de diseño y ficha de clasificación trazables, "
        "con resultados de SONARA y decisión ISO justificada por el alumno."
    )
    st.warning(
        "Continuidad del trabajo: utiliza «Guardar avance de esta etapa» antes de cambiar de sección. "
        "Las etapas posteriores recuperan los antecedentes y resultados previamente guardados."
    )


def _stage1(lab, saved):
    _header(
        1,
        "Expediente del Edificio Los Alerces",
        "Comprender el encargo, el alcance de la clasificación y el muestreo antes de modelar.",
    )
    _project_badge()

    st.markdown("### 🏙️ Conoce el Edificio Los Alerces")
    render_path = _asset("alerces_render_profesional.jpg")
    if render_path.is_file():
        st.image(
            str(render_path),
            caption=(
                "Render arquitectónico ilustrativo del Edificio Los Alerces. "
                "La identificación de A-302 y sus relaciones acústicas deben "
                "contrastarse con los planos técnicos de la Etapa 2."
            ),
            use_container_width=True,
        )
    else:
        _show_drawing(
            "render_isometrico_alerces.svg",
            "Esquema provisional. Pendiente incorporar el render arquitectónico en "
            "assets/curso5_lab1/alerces_render_profesional.jpg.",
        )

    st.markdown("### 🏢 ¿Qué vamos a clasificar?")
    st.info(
        "**Encargo profesional simulado:** analizar acústicamente el Edificio Los Alerces, "
        "de 20 viviendas, y construir un expediente de diseño basado en cálculos mediante SONARA. "
        "La ISO 12354 sirve para predecir el desempeño; la ISO/TS 19488:2021 permite "
        "establecer una clasificación, su alcance y la verificación correspondiente. "
        "**Una predicción de proyecto no sustituye las mediciones y verificaciones del edificio terminado.**"
    )
    st.markdown(
        "**¿Por qué empezamos por A-302?** Es una unidad didáctica donde podemos estudiar "
        "separación horizontal con A-301, transmisión de impacto desde A-402, fachada norte "
        "y ruido del shaft sanitario. El resultado de esta vivienda **no se extrapola "
        "automáticamente a los otros 19 departamentos**."
    )

    st.markdown("### 📖 Cómo funciona la clasificación ISO/TS 19488:2021")
    st.markdown(
        "La **cláusula 4 (p. 6)** define las clases **A, B, C, D, E y F**: "
        "A representa el desempeño acústico más exigente; **NPD** significa "
        "que el desempeño no se ha determinado. Se pueden clasificar características "
        "individuales, una vivienda o un edificio completo, siempre indicando el alcance."
    )
    st.markdown(
        "La **cláusula 5 (pp. 7–9)** presenta los criterios para el aislamiento aéreo "
        "entre viviendas, el ruido de impacto, el aislamiento frente al exterior, "
        "el ruido de instalaciones y la reverberación o absorción en escaleras "
        "y zonas de acceso. En este ejercicio calcularemos cuatro familias en A-302; "
        "**no verificamos todavía todos los requisitos de una clasificación global del edificio**."
    )
    st.info(
        "**Ejemplo de lectura de las clases (Anexo A.4, pp. 13–14):** "
        "se puede informar una clase por característica, una clase global para una "
        "vivienda o una clase global del edificio. Cuando se informa una única clase, "
        "debe cumplirse el conjunto de criterios que correspondan a ese alcance; "
        "no se promedian automáticamente las letras de las clases parciales."
    )

    st.markdown("### 📐 ¿Cuántas viviendas y mediciones requiere un edificio real?")
    st.markdown(
        "**No hay una equivalencia universal entre porcentaje de muestreo y porcentaje "
        "de departamentos.** El Anexo A diferencia la clasificación de una vivienda "
        "individual de la verificación del edificio completo y establece dos "
        "procedimientos para obtener evidencia de conformidad."
    )
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown(
            "**Procedimiento A — A.2.1, pp. 11–12**\n\n"
            "Verificación combinada en **tres momentos**: "
            "(1) cálculos de predicción durante el diseño, "
            "(2) inspecciones visuales durante la construcción "
            "y (3) mediciones en el edificio terminado. "
            "En la etapa de medición se selecciona **el 5 % de las estructuras "
            "y recintos que se medirán**, con prioridad a situaciones representativas "
            "o críticas. **No equivale a medir el 5 % de las viviendas.**"
        )
    with c_b:
        st.markdown(
            "**Procedimiento B — A.2.2, p. 12**\n\n"
            "Verificación **solo mediante mediciones** en el edificio terminado. "
            "Se selecciona como mínimo el **10 % de los tipos de construcción** "
            "de muros separadores y pisos, cubriendo suficientemente cada tipo "
            "y priorizando situaciones críticas. "
            "**No equivale a medir el 10 % de las viviendas.**"
        )
    st.warning(
        "**Edificio completo — A.2.3, p. 12:** el mínimo es **3 mediciones "
        "por cada tipo de construcción diferente y característica acústica**. "
        "El mínimo no fija por sí solo cuántas viviendas deben medirse. "
        "La cantidad final dependerá de las tipologías, distribuciones, "
        "recintos y particularidades del proyecto."
    )
    st.markdown(
        "**Para Los Alerces (20 viviendas):** A-302 será nuestra unidad de modelación. "
        "Como ejercicio, el estudiante identificará cuántas tipologías diferentes existen "
        "en el edificio y propondrá dónde obtener evidencia; **no debe suponer que "
        "basta con evaluar 1, 2 o 3 departamentos** sin caracterizar esas tipologías."
    )
    st.caption(
        "Referencia de lectura: ISO/TS 19488:2021, cláusulas 4, 5 y 6; "
        "Anexo A.1–A.4 (pp. 11–14 del documento; pp. 17–20 del PDF). "
        ""
    )

    st.markdown("### 📥 Norma de referencia · ISO/TS 19488:2021")
    st.caption(
        "Descarga el documento de referencia para consultar los criterios de "
        "clasificación y el Anexo A durante el desarrollo del laboratorio."
    )
    # Mismo mecanismo que la norma BS 5228 del Curso 4 / Laboratorio 1:
    # lectura directa desde assets/<curso>/ y st.download_button.
    iso_pdf_path = PROJECT_ROOT / "assets" / "curso5_lab1" / "ISO-TS-19488-2021.pdf"
    if iso_pdf_path.is_file():
        st.download_button(
            "📘 Abrir / descargar norma ISO/TS 19488:2021 · PDF",
            data=iso_pdf_path.read_bytes(),
            file_name="ISO-TS-19488-2021.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="c5l1_iso19488_pdf",
        )
    else:
        st.info(
            "El PDF ISO/TS 19488:2021 debe estar disponible en "
            "assets/curso5_lab1/ISO-TS-19488-2021.pdf para habilitar su descarga."
        )

    st.markdown("### 🏗️ Conoce el proyecto")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pisos", PROJECT["storeys"])
    c2.metric("Viviendas", PROJECT["dwellings"])
    c3.metric("Altura interior", f'{PROJECT["floor_height_m"]:.2f} m')
    c4.metric("Caso de estudio", "A-302")
    st.markdown("### 🔊 Situaciones acústicas del caso A-302")
    st.dataframe(
        pd.DataFrame(
            [
                ["Aéreo entre viviendas", "A-301", "A-302", "Muro M-01", "ISO 12354-1"],
                ["Impacto entre pisos", "A-402", "A-302", "Losa L-01", "ISO 12354-2"],
                ["Ruido exterior", "Fachada norte", "Estar A-302", "F-01 + V-01", "ISO 12354-3"],
                ["Instalaciones", "Shaft S-1", "A-302", "Cierre + fijaciones", "Método aplicable de instalaciones"],
            ],
            columns=["Situación", "Origen", "Receptor", "Elemento / vía", "Referencia de diseño"],
        ),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Las situaciones se estudian de forma individual. En la Etapa 2 se muestran "
        "la planta, el corte y los detalles para interpretar sus recorridos."
    )

    st.markdown("### 📋 Programa de la vivienda evaluada")
    st.dataframe(
        pd.DataFrame(
            ROOMS,
            columns=["Recinto", "Área [m²]", "Volumen [m³]", "Orientación", "Adyacencia crítica"],
        ),
        hide_index=True,
        width="stretch",
    )
    st.markdown("### 🧱 Materialidades de anteproyecto")
    st.dataframe(
        pd.DataFrame(
            MATERIALS,
            columns=["Código", "Elemento", "Sistema", "Dimensión", "Observación"],
        ),
        hide_index=True,
        width="stretch",
    )
    st.markdown("### 📊 Ficha del proyecto para Excel")
    st.caption(
        "Descarga un único archivo CSV con los datos generales del edificio, "
        "recintos y materialidades. Puedes abrirlo en Excel para consultar y "
        "organizar los antecedentes de cálculo."
    )
    _project_downloads()

    st.markdown(
        '<div class="section-band"><span>✍️</span>'
        '<h3>Actividad 1 · Diagnóstico y propuesta de muestreo</h3></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "El diagnóstico del A-302 se utilizará como base en las siguientes etapas. "
        "El plan de muestreo es una propuesta razonada para el edificio completo, "
        "no una certificación ni una cantidad de ensayos prefijada."
    )
    st.markdown(
        '<div style="padding:14px 18px;border:1px solid #cfe0ef;border-radius:14px;'
        'background:linear-gradient(135deg,#f7fbff,#eaf5fc);margin:10px 0 15px">'
        '<strong style="color:#125779">TU ENCARGO PROFESIONAL</strong><br>'
        '<span style="color:#345569">Diagnostica el A-302, selecciona el procedimiento '
        'de verificación y propone una muestra fundamentada para las 20 viviendas.</span>'
        '</div>', unsafe_allow_html=True,
    )
    with st.form("c5l1_stage1_diagnostic_form", border=True):
        st.markdown("#### Diagnóstico acústico del A-302")
        answer = st.text_area(
            "Diagnostica las cuatro situaciones acústicas del departamento A-302",
            value=saved.get("c5l1_s1_answer", ""),
            placeholder="Describe fuente, receptor, elemento y mecanismo de transmisión para cada caso.",
            height=160,
        )
        procedure_options = [
            "Selecciona un procedimiento",
            "A · predicciones, inspecciones y mediciones",
            "B · mediciones en edificio terminado",
        ]
        previous_procedure = saved.get("c5l1_s1_procedure", procedure_options[0])
        if previous_procedure not in procedure_options:
            previous_procedure = procedure_options[0]
        st.markdown("#### Procedimiento de verificación")
        procedure = st.selectbox(
            "Procedimiento para una futura verificación del edificio",
            procedure_options,
            index=procedure_options.index(previous_procedure),
        )
        st.markdown("#### Diseño del plan de muestreo")
        sample = st.text_area(
            "Propón un plan de muestreo para las 20 viviendas",
            value=saved.get("c5l1_s1_sampling", ""),
            placeholder=(
                "Propón qué unidades, recintos, elementos y orientaciones revisarías; "
                "justifica cantidad de ensayos por tipología y característica acústica. "
                "Explica por qué 20 viviendas no implica medir simplemente 2."
            ),
            height=180,
        )
        st.markdown("#### Alcance y limitaciones")
        scope = st.text_area(
            "Alcance, límites y evidencias adicionales",
            value=saved.get("c5l1_s1_scope", ""),
            placeholder=(
                "Distingue la evaluación preliminar de A-302 de la clasificación del "
                "edificio completo. Indica qué información falta para definir la muestra."
            ),
            height=130,
        )
        submitted = st.form_submit_button("Guardar diagnóstico y plan de muestreo", width="stretch")
    if submitted:
        if len(answer.strip()) < 120 or len(sample.strip()) < 160 or len(scope.strip()) < 90:
            st.warning(
                "Completa el diagnóstico (mín. 120 caracteres), el plan de muestreo "
                "(mín. 160) y el alcance (mín. 90)."
            )
        elif procedure == procedure_options[0]:
            st.warning("Selecciona y justifica un procedimiento de verificación.")
        else:
            _save(
                lab, saved, 1,
                c5l1_s1_answer=answer,
                c5l1_s1_procedure=procedure,
                c5l1_s1_sampling=sample,
                c5l1_s1_scope=scope,
            )
            st.success(
                "Diagnóstico y plan de muestreo guardados. Los cálculos posteriores "
                "seguirán usando A-302 como unidad didáctica."
            )


def _stage2(lab, saved):
    _header(2, "Lectura acústica de planos y detalles", "Obtener del plano los datos que se usarán en SONARA y reconocer los caminos críticos.")
    _project_badge()
    st.markdown(
        "Las cuatro láminas tienen presentación de plano técnico, cotas y detalles de partida. "
        "**Se muestran como imágenes PNG de alta resolución; el juego PDF permite ampliar e imprimir en A3.** "
        "Las cotas son datos del caso ficticio, no dimensiones que debas medir sobre la pantalla."
    )
    _download_plan_set("c5l1_s2_plans_pdf")
    tabs = st.tabs(["AC-01 · Planta", "AC-02 · Corte", "AC-03 · Fachada", "AC-04 · Detalles"])
    sheets = [
        ("planta_tipo.png", "AC-01 · Planta parcial nivel 3 · norte arriba · A-302 y estar adyacente A-301", "Localiza M-01, V-01, V-02 y S-1. El estar en L tiene 20,40 m²; el paño medianero útil mide 4,08 × 2,50 m."),
        ("corte_aa.png", "AC-02 · Corte A-A · cinco niveles · altura libre 2,50 m", "A-402 está sobre A-302. L-01 tiene 160 mm de hormigón y un paquete superior de 60 mm; no los sumes como losa desnuda."),
        ("fachada_norte.png", "AC-03 · Elevación norte · paño FA-01 destacado", "FA-01 solo incluye el estar: 15,30 m² brutos = 10,50 m² opacos + 4,80 m² de V-01. V-02 pertenece al dormitorio."),
        ("detalles_constructivos.png", "AC-04 · M-01, L-01, F-01 y S-01 · espesores en mm", "Distingue placa, cámara, absorbente y unión. El espesor total de S-01 es 120 mm; no corresponde a cada placa."),
    ]
    for tab, (filename, caption, instruction) in zip(tabs, sheets):
        with tab:
            _show_drawing(filename, caption)
            st.info(instruction)
    st.markdown("### De la lámina al modelo de cálculo")
    matrix = [
        ["AI-01", "A-301 → A-302", "M-01", "4,08 × 2,50 = 10,20 m²", "V 51,0 m³ · HA 180 mm", "Directa + uniones laterales"],
        ["IM-01", "A-402 → A-302", "L-01", "Estar: 20,40 m²", "V 51,0 m³ · losa 160 mm", "Piso + losa + flancos"],
        ["FA-01", "Exterior → estar A-302", "F-01 + V-01", "15,30 = 10,50 + 4,80 m²", "V 51,0 m³ · DVH 6/12/4", "Componentes + juntas"],
        ["IN-01", "Shaft → dormitorio", "S-01 + fijaciones", "V receptor 28,8 m³", "Cierre 120 mm · área según recorrido", "Aérea + estructural"],
    ]
    st.dataframe(pd.DataFrame(matrix, columns=["Caso", "Fuente / receptor", "Elemento", "Geometría útil", "Datos de partida", "Vías"]), hide_index=True, width="stretch")
    st.warning("El plano no entrega TR, rigidez dinámica ni potencia sonora sanitaria. Esos datos se justifican en la etapa 4; no se deducen de un dibujo.")
    with st.form("c5l1_s2_reading_form"):
        geometry = st.text_area("Comprueba las áreas de M-01 y FA-01 y el volumen del estar", value=saved.get("c5l1_s2_geometry", ""), placeholder="Escribe las operaciones y distingue área bruta, área opaca y ventana.", height=120)
        findings = st.text_area("Tres riesgos constructivos observados en las láminas", value=saved.get("c5l1_s2_findings", ""), placeholder="Elemento, encuentro o puente; mecanismo acústico y posible medida.", height=130)
        missing_data = st.text_area("Datos que debes buscar o adoptar como hipótesis", value=saved.get("c5l1_s2_missing", ""), placeholder="Qué falta, por qué importa y de dónde lo obtendrías.", height=110)
        submitted = st.form_submit_button("Guardar lectura de planos", width="stretch")
    if submitted:
        if min(len(geometry.strip()), len(findings.strip()), len(missing_data.strip())) < 80:
            st.warning("Desarrolla la comprobación geométrica, tres riesgos y los datos faltantes (mín. 80 caracteres por apartado).")
        else:
            _save(lab, saved, 2, c5l1_s2_geometry=geometry, c5l1_s2_findings=findings, c5l1_s2_missing=missing_data)
            st.success("Lectura guardada: úsala al preparar el protocolo de diseño.")



def _global_building_explanation():
    st.markdown("### ¿Cómo se obtiene la clase global del edificio?")
    st.markdown(
        "**No se calcula promediando dB ni letras.** Se comprueba qué clase puede "
        "cumplirse para todas las características y situaciones aplicables al edificio. "
        "La clase global queda limitada por la menos favorable dentro del alcance verificado."
    )
    st.markdown(
        "1. **Define el edificio y su alcance:** viviendas, recintos protegidos, usos colindantes "
        "y zonas comunes que correspondan.\n"
        "2. **Identifica tipologías y condiciones críticas:** muros y pisos diferentes, "
        "encuentros, fachadas con exposiciones distintas y equipos o instalaciones.\n"
        "3. **Justifica la cobertura y la verificación:** explica qué casos representan cada "
        "tipología y qué cálculos, inspecciones y mediciones aportan evidencia según cláusula 6 "
        "y Anexo A. La muestra no se define solo contando departamentos.\n"
        "4. **Clasifica cada situación con su descriptor correcto:** compara con la fila, "
        "condición, bandas y notas aplicables; identifica cualquier resultado no determinado.\n"
        "5. **Revisa cada característica del edificio:** una situación menos favorable no "
        "desaparece porque otras tengan buen desempeño.\n"
        "6. **Declara la clase global sustentada:** todos los requisitos aplicables deben "
        "cumplir esa clase. Conserva las clases parciales superiores y el alcance en el informe."
    )
    st.markdown("#### Ejemplo hipotético de edificio completo")
    st.caption(
        "Este ejemplo supone que las tipologías y situaciones aplicables ya están cubiertas "
        "por un procedimiento de verificación válido. No son resultados de Los Alerces."
    )
    st.dataframe(
        pd.DataFrame([
            ["Aéreo", "Separaciones y encuentros representativos evaluados", "C"],
            ["Impacto", "Tipos de entrepiso y transmisiones relevantes evaluados", "D"],
            ["Exterior", "Recintos y fachadas con sus exposiciones evaluados", "C"],
            ["Instalaciones", "Fuentes y condiciones de funcionamiento evaluadas", "C"],
            ["Accesos / escaleras", "Reverberación o absorción aplicable evaluada", "B"],
        ], columns=["Característica del edificio", "Cobertura supuesta", "Clase sustentada"]),
        hide_index=True, width="stretch",
    )
    st.success(
        "La clase global del ejemplo es D: impacto limita el conjunto. Para aspirar a C "
        "hay que mejorar y verificar los casos de impacto que no alcanzan C, manteniendo "
        "el cumplimiento de las demás características. No basta mejorar uno de varios "
        "entrepisos deficientes."
    )
    st.warning(
        "Si una característica requerida o una tipología relevante carece de evidencia, "
        "no la omitas para asignar una clase global. Documenta lo pendiente o la declaración "
        "NPD cuando corresponda y conserva las conclusiones parciales."
    )
    st.markdown(
        "**Aplicación al laboratorio:** AI-01, IM-01, FA-01 e IN-01 describen solo cuatro "
        "situaciones de A-302. Permiten diseñar y comparar soluciones; no representan "
        "automáticamente las 20 viviendas. En la etapa 10 debes proponer cómo extender "
        "el expediente y verificar el edificio, sin inventar resultados para los casos faltantes."
    )
    st.caption("Referencia: ISO/TS 19488:2021, cláusulas 4–6 y Anexo A.2–A.4.")


def _stage3(lab, saved):
    _header(3, "Cómo se clasifica una vivienda", "Comprender los criterios ISO con un ejemplo resuelto antes de definir el objetivo de diseño.")
    _download_standard("c5l1_stage3_iso19488_pdf")
    st.markdown("**Secuencia:** resultado acústico → descriptor correcto → límite aplicable → clase por característica → conclusión con alcance.")
    tabs = st.tabs(["Clases y criterios", "Ejemplo resuelto · A-302", "Edificio completo", "Tu objetivo y alcance"])
    with tabs[0]:
        st.markdown("### Seis clases y una declaración de desempeño")
        st.markdown("**A es la clase más exigente; F la menos exigente del esquema.** NPD se utiliza cuando el desempeño no está determinado, no se requiere o queda fuera de las clases. No es una séptima clase ni una nota cero.")
        st.dataframe(pd.DataFrame([
            ["A → B → C → D → E → F", "De mayor a menor exigencia acústica"],
            ["Clase por característica", "Aéreo, impacto, exterior, instalaciones o zonas de acceso"],
            ["Clase de vivienda", "Requiere todos los criterios aplicables al alcance de esa vivienda"],
            ["Clase de edificio", "Requiere alcance y verificación del edificio; no se extrapola A-302"],
        ], columns=["Concepto", "Interpretación"]), hide_index=True, width="stretch")
        st.dataframe(pd.DataFrame([
            ["Aéreo", "DₙT,A / DₙT,50 o alternativa permitida", "Mayor aislamiento", "5.2 · tabla 1"],
            ["Impacto", "L′ₙT,w y requisito de baja frecuencia cuando aplica", "Menor nivel", "5.3 · tabla 2"],
            ["Exterior", "Aislamiento adaptado al espectro y exposición Lden", "Según exposición", "5.4 · tabla 3"],
            ["Instalaciones", "LAeq,nT o LAFmax,nT según funcionamiento", "Menor nivel", "5.5 · tabla 4"],
            ["Accesos / escaleras", "Reverberación o absorción en las bandas requeridas", "Según espacio", "5.6 · tabla 5"],
        ], columns=["Característica", "Qué comprobar", "Comparación", "Consulta en el PDF"]), hide_index=True, width="stretch")
        st.info("Un número único sin su descriptor, bandas, normalización y condición de operación no basta. La acústica entre habitaciones dentro de la misma vivienda no integra estas clases.")
        st.markdown("**La clase global no es un promedio de letras:** queda limitada por la prestación menos favorable, siempre que se hayan cubierto todos los criterios aplicables. Consulta cláusula 6 y Anexo A para la verificación.")
    with tabs[1]:
        st.warning("EJEMPLO RESUELTO · Todos los resultados acústicos siguientes son hipotéticos. No son una salida calculada de SONARA ni respuestas que debas copiar en las etapas 5–8.")
        st.markdown("### Encargo del ejemplo: al menos clase C en las cuatro situaciones")
        st.markdown("A-302 recibe ruido aéreo desde A-301, impacto desde A-402, ruido exterior norte y ruido sanitario. Se usan las geometrías de AC-01 a AC-04 y las tablas 1–4 de ISO/TS 19488:2021.")
        st.markdown("#### 1 · AI-01: separar el Rw del muro del resultado entre recintos")
        st.markdown("Modela HA 180 mm, S = 10,20 m², V = 51,0 m³, TR declarado y flancos. Supón una salida final **DₙT,w = 55 dB y C = −2 dB**. Entonces **DₙT,A = 53 dB**. La fila entre viviendas de la tabla 1 exige **≥ 52 dB para C**: cumple. Para comprobar B mediante la alternativa DₙT,A, la nota de la tabla conduce a **≥ 56 dB**: 53 dB no basta. No compares 55 dB con un límite escrito para otro descriptor.")
        st.markdown("#### 2 · IM-01: reducir el nivel de impacto")
        st.markdown("Losa L-01 de 160 mm y recinto de V = 51,0 m³. Supón **69 dB** sin tratamiento y **L′ₙT,w = 53 dB** después del piso flotante. **53 ≤ 54 dB** cumple C en la fila entre viviendas de la tabla 2. No alcanza B: supera 50 dB y además B exige comprobar la baja frecuencia. La diferencia del caso es 16 dB; no la presentes automáticamente como ΔLw de un ensayo del revestimiento.")
        st.markdown("#### 3 · FA-01: clasificar con la exposición exterior")
        st.markdown("Fachada 15,30 m² = opaco 10,50 + V-01 4,80 m²; V = 51,0 m³. Adopta **Lden = 65 dB solo como hipótesis del ejemplo**. Supón D₂m,nT,w = 44 dB y Ctr = −6 dB: el aislamiento adaptado al tráfico es **38 dB**. Para C, tabla 3: **65 − 28 = 37 dB**, comprobando también el mínimo de la nota. **38 ≥ 37** cumple C. B requiere **65 − 24 = 41 dB**: no cumple. Declara la correspondencia del descriptor de SONARA con la magnitud requerida; no intercambies descriptores sin justificarla.")
        st.markdown("#### 4 · IN-01: el funcionamiento y la normalización importan")
        st.markdown("Descarga intermitente percibida en dormitorio (V = 28,8 m³). Supón **LAFmax,nT = 36 dB**, obtenido con la condición y normalización correctas. Tabla 4: C exige **≤ 34 dB**, D **≤ 38 dB**. Alcanza D y falla el objetivo C. Rediseña el camino dominante —cierre, sellado o fijaciones—. Si una variante entrega **33 dB**, alcanza C. Un LAeq o un máximo sin normalizar no sustituye este indicador.")
        st.dataframe(pd.DataFrame([
            ["AI-01", "DₙT,A = 53 dB", "C", "C"],
            ["IM-01", "L′ₙT,w = 53 dB", "C", "C"],
            ["FA-01", "Aislamiento adaptado = 38 dB; Lden 65", "C", "C"],
            ["IN-01", "LAFmax,nT: 36 → 33 dB", "D", "C"],
        ], columns=["Caso", "Resultado hipotético", "Antes de rediseñar IN-01", "Después"]), hide_index=True, width="stretch")
        st.success("Decisión de diseño: instalaciones limita inicialmente las cuatro características a D. Mejorar el muro no corrige ese problema. Después de actuar sobre IN-01, las cuatro situaciones alcanzan C.")
        st.warning("Conclusión limitada: cuatro situaciones del A-302 alcanzan preliminarmente C. Falta cubrir las otras situaciones aplicables, accesos/escaleras cuando correspondan y la verificación. No declares clase C global de A-302 ni de las 20 viviendas a partir de este ejemplo parcial.")
        st.caption("Referencia de comprobación: tablas 1–4, notas de descriptor y Anexo A.3–A.4 del PDF disponible. En obra se requieren los procedimientos de verificación aplicables.")
    with tabs[2]:
        _global_building_explanation()
    with tabs[3]:
        st.markdown("### Elige el objetivo para tu propio diseño")
        options = ["Selecciona un objetivo", "Clase A", "Clase B", "Clase C", "Clase D", "Clase E", "Clase F"]
        previous = saved.get("c5l1_s3_target", options[0])
        with st.form("c5l1_s3_scope_form"):
            target = st.selectbox("Clase objetivo de diseño (no es clase obtenida)", options, index=options.index(previous) if previous in options else 0)
            scope = st.text_area("Declaración de alcance de tu clasificación", value=saved.get("c5l1_s3_scope", ""), placeholder="ISO/TS 19488:2021, cuatro situaciones de A-302, fase de diseño, casos pendientes y exclusiones.", height=140)
            reason = st.text_area("Por qué no basta promediar las clases ni evaluar un único muro", value=saved.get("c5l1_s3_reason", ""), height=110)
            submitted = st.form_submit_button("Guardar objetivo y alcance", width="stretch")
        if submitted:
            if target == options[0] or "19488" not in scope or len(scope.strip()) < 120 or len(reason.strip()) < 80:
                st.warning("Elige el objetivo, desarrolla el alcance (120 caracteres, incluyendo 19488) y explica la regla de clase limitante (80 caracteres).")
            else:
                _save(lab, saved, 3, c5l1_s3_target=target, c5l1_s3_scope=scope, c5l1_s3_reason=reason)
                st.success("Objetivo guardado. Ahora prepara las entradas en la etapa 4; todavía no has obtenido una clase.")


def _stage4(lab, saved):
    _header(4, "Preparar el diseño en SONARA", "Convertir el objetivo y los planos en entradas trazables antes de calcular.")
    st.info(f"**Objetivo recuperado de etapa 3:** {saved.get('c5l1_s3_target', 'Pendiente de definir')}.")
    with st.expander("Recuperar lectura de planos y alcance"):
        st.markdown(saved.get("c5l1_s2_geometry", "Sin comprobación geométrica guardada."))
        st.markdown(saved.get("c5l1_s2_findings", "Sin riesgos guardados."))
        st.markdown(saved.get("c5l1_s3_scope", "Sin alcance guardado."))
    st.dataframe(pd.DataFrame([
        ["M-01 / AI-01", "HA 180 mm; S 10,20 m²; V 51,0 m³", "Ruido aéreo → Transmisión entre recintos", "DₙT,w y adaptaciones finales"],
        ["L-01 / IM-01", "Losa 160; resiliente 10; sobrelosa 40; terminación 10 mm", "Ruido de impacto → ISO 12354-2", "L′ₙT,w y adaptación aplicable"],
        ["F-01 + V-01 / FA-01", "10,50 m² opacos + 4,80 m² de ventana", "Componentes en Ruido aéreo → Fachada", "Aislamiento de fachada adaptado"],
        ["S-01 / IN-01", "2 RF 12,5 / cámara 70 / 2 RF 12,5 mm; V 28,8 m³", "Cierre en Ruido aéreo → Instalaciones", "LAeq,nT / LAFmax,nT según operación"],
    ], columns=["Caso", "Datos del expediente", "Ruta SONARA", "Resultado a registrar"]), hide_index=True, width="stretch")
    st.markdown("### Tu secuencia de trabajo")
    st.markdown("""1. Elige la fila normativa, el descriptor y el objetivo para cada caso.
2. Prepara la solución base y registra sus resultados.
3. Identifica el camino dominante y modifica una variable.
4. Recalcula conservando el resto de condiciones.
5. Guarda una variante y justifica la decisión, incluso si no mejora.
6. Clasifica tus propios resultados en la etapa 10.""")
    st.warning("Los valores iniciales de SONARA no son datos del proyecto. Los campos siguientes quedan vacíos hasta que elijas una ficha o declares una hipótesis. La masa de sobrelosa se calcula como densidad × 0,040 m; su capa resiliente de 10 mm no determina s′ por sí sola.")
    prev = saved.get("c5l1_s4_inputs", {})
    with st.form("c5l1_s4_protocol_form"):
        columns = st.columns(2)
        inputs = {}
        for index, (key, label, minimum, step) in enumerate([
            ("tr_stay", "TR estar [s]", .1, .1),
            ("tr_bedroom", "TR dormitorio [s]", .1, .1),
            ("rho_ha", "Densidad HA [kg/m³]", 500., 50.),
            ("rho_screed", "Densidad sobrelosa [kg/m³]", 100., 50.),
            ("dynamic_stiffness", "Rigidez dinámica s′ [MN/m³] · si usas piso físico", .1, .5),
            ("lden", "Exposición exterior Lden [dB]", 0., 1.),
        ]):
            inputs[key] = columns[index % 2].number_input(label, min_value=minimum, value=prev.get(key), step=step, placeholder="Dato o hipótesis documentada")
        input_sources = st.text_area("Fuentes de datos, hipótesis y antecedentes pendientes", value=saved.get("c5l1_s4_sources", ""), placeholder="Justifica cada número. Si eliges catálogo de piso, explica por qué s′ no se utiliza. Fuente sanitaria y transferencia estructural: ficha o escenario declarado.", height=140)
        criteria = st.text_area("Criterios de diseño que comprobarás en cada caso", value=saved.get("c5l1_s4_criteria", ""), placeholder="Caso, descriptor, límite, sentido ≥/≤, tabla y nota. No copies sin revisar el ejemplo de etapa 3.", height=140)
        protocol = st.text_area("Protocolo personal de cálculo", value=saved.get("c5l1_s4_protocol", ""), placeholder="Nombres Base/Variante, capturas, curvas, unidades, condiciones que mantendrás y cómo justificarás los cambios.", height=130)
        submitted = st.form_submit_button("Guardar protocolo y entradas de diseño", width="stretch")
    if submitted:
        if inputs["tr_stay"] is None or inputs["tr_bedroom"] is None or inputs["rho_ha"] is None or inputs["lden"] is None:
            st.warning("Define TR del estar y dormitorio, densidad HA y exposición exterior; justifica los restantes datos según el modelo elegido.")
        elif len(input_sources.strip()) < 120 or len(criteria.strip()) < 120 or len(protocol.strip()) < 140:
            st.warning("Completa fuentes (120 caracteres), criterios (120) y protocolo (140).")
        else:
            _save(lab, saved, 4, c5l1_s4_inputs=inputs, c5l1_s4_sources=input_sources, c5l1_s4_criteria=criteria, c5l1_s4_protocol=protocol)
            st.success("Entradas guardadas; se recuperarán en las etapas 5–8.")
    _sonara_button("Abrir SONARA y preparar Los Alerces")


def _stage5(lab, saved):
    _header(5, "Diseño frente a ruido aéreo entre viviendas", "Modelar el muro separador y los caminos laterales del caso AI-01.")
    _result_form(
        lab, saved, 5, "Aéreo interior",
        [("dntw", "DₙT,w", "dB"), ("c", "C", "dB"), ("ctr", "Ctr", "dB")],
        "Construye los recintos A-301/A-302, el muro M-01 y los encuentros del plano. Revisa la curva por bandas antes de registrar el número único.",
    )
    st.markdown("**Control de coherencia:** identifica si domina el elemento directo o una unión lateral; explica qué modificación cambiaría esa conclusión.")


def _stage6(lab, saved):
    _header(6, "Diseño frente a ruido de impacto", "Modelar la losa base, el piso flotante y la transmisión al recinto inferior.")
    _result_form(
        lab, saved, 6, "Impacto",
        [("lntw", "L′ₙT,w", "dB"), ("ci", "CI", "dB")],
        "Modela L-01 con su sobrelosa y capa resiliente. Documenta la losa de referencia, la mejora del revestimiento y cualquier supuesto de flancos.",
    )
    st.markdown("**Control de coherencia:** en impacto, un valor global menor representa una prestación mejor; no inviertas ese sentido al clasificar.")


def _stage7(lab, saved):
    _header(7, "Diseño acústico de fachada", "Calcular la fachada compuesta y reconocer la influencia de vanos, sellos y exposición.")
    _result_form(
        lab, saved, 7, "Fachada",
        [("d2mntw", "D₂m,nT,w", "dB"), ("c", "C", "dB"), ("ctr", "Ctr", "dB")],
        "Construye el paño F-01 con la ventana V-01, sus áreas reales y el volumen del estar. Registra la exposición exterior adoptada por separado.",
    )
    st.markdown("**Control de coherencia:** compara el aporte del paño opaco, la ventana y el sellado. No atribuyas al muro el desempeño de la fachada completa.")


def _stage8(lab, saved):
    _header(8, "Proyección de ruido de instalaciones", "Estimar el ruido sanitario y declarar el método técnico y la condición de operación.")
    _result_form(
        lab, saved, 8, "Instalaciones",
        [("laeq", "LAeq,nT", "dB(A)"), ("lafmax", "LAFmax,nT", "dB(A)")],
        "Representa la descarga sanitaria, el cierre S-01, las fijaciones y las vías estructural y aérea. Si el método no permite un descriptor, decláralo como limitación en vez de inventarlo.",
    )
    st.warning("Comprueba que las salidas de instalaciones estén normalizadas a T₀ = 0,5 s y correspondan a la condición temporal registrada. Si recuperas resultados antiguos LAeq/LAFmax sin normalizar, revísalos antes de usarlos en la clasificación.")
    st.info("El cálculo de instalaciones depende fuertemente de datos de fuente, montaje y operación. Una estimación sin esos antecedentes debe informarse con una incertidumbre y un plan de verificación en obra.")


def _stage9(lab, saved):
    _header(9, "Matriz consolidada de resultados", "Revisar integridad, unidades y trazabilidad antes de consultar los umbrales de clasificación.")
    rows = []
    definitions = [
        ("AI-01", "Aéreo interior", "dntw", "DₙT,w", "dB"),
        ("IM-01", "Impacto", "lntw", "L′ₙT,w", "dB"),
        ("FA-01", "Fachada", "d2mntw", "D₂m,nT,w", "dB"),
        ("IN-01", "Instalaciones", "laeq", "LAeq,nT", "dB(A)"),
        ("IN-01", "Instalaciones", "lafmax", "LAFmax,nT", "dB(A)"),
    ]
    for code, family, key, descriptor, unit in definitions:
        result = saved.get(f"c5l1_result_{code}", {})
        status = "Registrado" if result.get(key) is not None else ("Sin determinar · justificado" if result.get("undetermined") else "Pendiente")
        if code == "IN-01" and result.get(key) is not None and not result.get("normalized"):
            status = "Pendiente"
        rows.append([code, family, descriptor, result.get(key), unit, status])
    result_df = pd.DataFrame(rows, columns=["Caso", "Familia", "Descriptor", "Resultado", "Unidad", "Estado"])
    st.dataframe(result_df, hide_index=True, width="stretch")
    st.markdown("### Indicadores para la comparación normativa")
    ai = saved.get("c5l1_result_AI-01", {})
    fa = saved.get("c5l1_result_FA-01", {})
    dnta = ai["dntw"] + ai["c"] if ai.get("dntw") is not None and ai.get("c") is not None else None
    facade_adapted = fa["d2mntw"] + fa["ctr"] if fa.get("d2mntw") is not None and fa.get("ctr") is not None else None
    st.dataframe(pd.DataFrame([
        ["AI-01", "DₙT,A = DₙT,w + C", dnta, "Verificar que C procede de la curva final entre recintos"],
        ["FA-01", "D₂m,nT,w + Ctr", facade_adapted, "Justificar correspondencia y espectro; comparar con Lden adoptado"],
    ], columns=["Caso", "Operación", "Valor [dB]", "Condición de uso"]), hide_index=True, width="stretch")
    st.info("Estas sumas ayudan a revisar los indicadores; no asignan clases. Para A/B pueden faltar descriptores de baja frecuencia que debes documentar antes de concluir.")
    st.markdown("### Decisiones y evidencias del diseño")
    decisions = []
    for family, case in CALCULATION_CASES.items():
        design = saved.get(f"c5l1_result_{case['code']}", {})
        decisions.append([
            case["code"], design.get("target", ""), design.get("base_design", ""),
            design.get("design_change", ""), design.get("evidence", ""),
        ])
    st.dataframe(
        pd.DataFrame(decisions, columns=["Caso", "Objetivo", "Base", "Cambio y efecto", "Evidencias"]),
        hide_index=True, width="stretch",
    )
    st.download_button(
        "Descargar expediente de diseño SONARA (JSON)",
        data=json.dumps(
            {
                "project": PROJECT,
                "target": saved.get("c5l1_s3_target"),
                "scope": saved.get("c5l1_s3_scope", ""),
                "inputs": saved.get("c5l1_s4_inputs", {}),
                "input_sources": saved.get("c5l1_s4_sources", ""),
                "criteria": saved.get("c5l1_s4_criteria", ""),
                "protocol": saved.get("c5l1_s4_protocol", ""),
                "results": {case["code"]: saved.get(f"c5l1_result_{case['code']}", {}) for case in CALCULATION_CASES.values()},
                "classification": saved.get("c5l1_classification", {}),
            },
            ensure_ascii=False, indent=2,
        ).encode("utf-8"),
        file_name="los_alerces_diseno_sonara.json", mime="application/json",
        key="c5l1_design_export", width="stretch",
    )
    missing = result_df[result_df["Estado"] == "Pendiente"]
    if missing.empty:
        if (result_df["Estado"] == "Sin determinar · justificado").any():
            st.warning("Expediente con resultados sin determinar. Conserva las limitaciones: no permite concluir un desempeño global completo.")
        else:
            st.success("La matriz está completa. Los valores aún no tienen una clase asignada.")
    else:
        st.warning(f"Faltan {len(missing)} resultados. Regresa a las etapas de cálculo antes de clasificar.")
    review = st.text_area(
        "Revisión crítica previa a la clasificación",
        value=saved.get("c5l1_s9_review", ""),
        placeholder="Detecta el resultado más débil, una incertidumbre dominante y una verificación necesaria en obra.",
        height=130,
    )
    if st.button("Cerrar matriz de diseño", key="c5l1_s9_save", width="stretch"):
        if not missing.empty:
            st.warning("Completa todos los resultados antes de cerrar la matriz.")
        elif len(review.strip()) < 120:
            st.warning("Desarrolla la revisión crítica con al menos 120 caracteres.")
        else:
            _save(lab, saved, 9, c5l1_s9_review=review)
            st.success("Matriz consolidada. Continúa con la clasificación individual.")


def _stage10(lab, saved):
    _header(10, "Clasificación realizada por el alumno", "Aplicar ISO/TS 19488 a los resultados y emitir una conclusión trazable de proyecto.")
    st.error(
        "La plataforma no calcula ni recomienda la clase. Consulta tu copia autorizada de ISO/TS 19488:2021, "
        "verifica el alcance de cada tabla y registra la decisión que puedas justificar."
    )
    if saved.get("c5l1_result_IN-01", {}).get("undetermined"):
        st.warning(
            "Instalaciones contiene un descriptor sin determinar. Consulta cómo declarar esa "
            "situación en la referencia elegida y explica la exclusión; no atribuyas una clase "
            "a la característica sin evidencia ni concluyas conformidad global completa."
        )
    st.info("Entrega una clasificación preliminar de los casos AI-01, IM-01, FA-01 e IN-01. El laboratorio no evalúa por sí solo todas las situaciones de A-302 ni las otras 19 viviendas; no presentes estos cuatro casos como certificación global.")
    st.markdown("**Informe final:** alcance → entradas y fuentes → base/variante → curva y descriptor → límite y clase por caso → clase limitante → incertidumbres y verificación en obra.")
    _download_standard("c5l1_s10_standard")
    with st.expander("Recordar cómo se clasifica el edificio completo"):
        _global_building_explanation()
    families = ["Aéreo interior", "Impacto", "Fachada", "Instalaciones"]
    previous = saved.get("c5l1_classification", {})
    entries = {}
    with st.form("c5l1_classification_form"):
        for family in families:
            st.markdown(f"#### {family}")
            c1, c2, c3 = st.columns([1, 1, 2])
            entries[family] = {
                "class": c1.text_input(
                    "Clase asignada",
                    value=previous.get(family, {}).get("class", ""),
                    placeholder="Según edición consultada",
                    key=f"c5l1_class_{family}",
                ),
                "threshold": c2.text_input("Umbral consultado", value=previous.get(family, {}).get("threshold", ""), key=f"c5l1_threshold_{family}"),
                "justification": c3.text_input("Justificación y referencia", value=previous.get(family, {}).get("justification", ""), key=f"c5l1_justification_{family}"),
            }
        overall_rule = st.text_area(
            "Clase limitante de los casos y alcance de la conclusión",
            value=previous.get("overall_rule", ""),
            height=100,
            placeholder="Compara las clases parciales sin promediarlas; explica qué falta para clasificar la vivienda o el edificio completo.",
        )
        building_plan = st.text_area(
            "Qué falta para obtener la clasificación global de Los Alerces",
            value=previous.get("building_plan", ""),
            height=140,
            placeholder="Tipologías pendientes, otros recintos/fachadas, accesos y escaleras, instalaciones, cobertura de la muestra y verificación. No inventes resultados de las otras viviendas.",
        )
        conclusion = st.text_area(
            "Conclusión profesional y plan de verificación",
            value=previous.get("conclusion", ""),
            height=180,
            placeholder="Clasificación, categoría dominante, mejoras propuestas, incertidumbres y mediciones finales requeridas.",
        )
        submitted = st.form_submit_button("Entregar clasificación del proyecto", width="stretch")
    if submitted:
        invalid = [family for family in families if entries[family]["class"].strip().upper() not in {"A", "B", "C", "D", "E", "F", "NPD"} or not entries[family]["threshold"].strip() or len(entries[family]["justification"].strip()) < 20]
        results_ready = all(saved.get(f"c5l1_result_{code}") for code in ["AI-01", "IM-01", "FA-01", "IN-01"])
        services = saved.get("c5l1_result_IN-01", {})
        if any(services.get(key) is not None for key in ("laeq", "lafmax")) and not services.get("normalized"):
            results_ready = False
        if not results_ready:
            st.warning("Faltan resultados de SONARA. Completa las Etapas 5 a 8 antes de entregar.")
        elif invalid:
            st.warning("Completa clase, umbral y justificación para: " + ", ".join(invalid))
        elif len(building_plan.strip()) < 100:
            st.warning("Explica qué falta para clasificar el edificio completo con al menos 100 caracteres.")
        elif len(overall_rule.strip()) < 80 or len(conclusion.strip()) < 180:
            st.warning("Desarrolla la regla global y la conclusión con la extensión mínima solicitada.")
        else:
            payload = {**entries, "overall_rule": overall_rule, "building_plan": building_plan, "conclusion": conclusion, "standard": "ISO/TS 19488:2021", "phase": "Diseño", "scope": "Cuatro situaciones modeladas de A-302; clasificación global no acreditada"}
            _save(lab, saved, 10, c5l1_classification=payload)
            st.success("Clasificación entregada para revisión docente. Se conserva como clasificación de diseño realizada por el alumno.")


_STAGES = [_stage0, _stage1, _stage2, _stage3, _stage4, _stage5, _stage6, _stage7, _stage8, _stage9, _stage10]


def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage = max(0, min(int(stage), 10))
    return _STAGES[stage](lab, saved)
