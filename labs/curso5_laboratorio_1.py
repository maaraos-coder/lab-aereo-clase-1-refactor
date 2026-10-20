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
    ["Cocina", 7.8, 19.5, "Interior", "Shaft S-1"],
    ["Baño principal", 4.1, 10.3, "Interior", "Shaft S-1"],
]

MATERIALS = [
    ["M-01", "Muro medianero A-301/A-302", "Hormigón armado", "180 mm", "Continuo entre losas; encuentros sellados"],
    ["L-01", "Losa entre A-302/A-402", "Hormigón armado", "160 mm", "Sobrelosa 40 mm + terminación flotante"],
    ["F-01", "Paño opaco fachada norte", "HA + aislante + placa de yeso", "150 + 50 + 15 mm", "Trasdosado desacoplado"],
    ["V-01", "Ventana estar", "DVH 6/12/4 · marco aluminio", "4.80 m²", "Juntas perimetrales continuas"],
    ["V-02", "Ventana dormitorio", "DVH 6/12/4 · marco aluminio", "2.40 m²", "Juntas perimetrales continuas"],
    ["T-01", "Tabique interior", "Doble placa yeso + lana mineral", "90 mm", "Canales con banda resiliente"],
    ["S-01", "Shaft sanitario", "Doble placa RF + lana mineral", "120 mm", "Tuberías con abrazaderas resilientes"],
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
        "descriptor": "LAFmax y/o LAeq según condición declarada",
        "geometry": "Shaft S-01 · recorrido vertical contiguo a baño",
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
            ["Piso superior", "Sobrelosa 40 mm + terminación flotante", "La capa resiliente y su rigidez no están definidas: selecciona una ficha o declara una hipótesis."],
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
            ["S-01 · cierre", "Doble placa RF + lana · conjunto 120 mm", "Faltan espesores individuales: define placas, cámara y montaje sin asignar 120 mm a cada capa."],
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


def _result_form(lab, saved, stage, case_name, fields, prompt):
    case = CALCULATION_CASES[case_name]
    st.markdown(f"### Caso {case['code']} · {case_name}")
    st.markdown(
        f"**Fuente:** {case['source']}  \n**Receptor:** {case['receiver']}  \n"
        f"**Geometría:** {case['geometry']}  \n**Descriptor de trabajo:** {case['descriptor']}"
    )
    st.info(prompt)
    _sonara_design_guide(case_name)
    _sonara_button("Abrir SONARA para diseñar esta solución")

    stored = saved.get(f"c5l1_result_{case['code']}", {})
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
            value=stored.get("target", ""),
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
        if case_name == "Instalaciones":
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
        elif len(notes.strip()) < 80:
            st.warning("Documenta los supuestos y la configuración con al menos 80 caracteres.")
        else:
            payload = {
                **values, "notes": notes, "descriptor": case["descriptor"],
                "target": target, "base_design": base_design, "design_change": design_change,
                "evidence": evidence, "undetermined": undetermined,
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
        "Interpreta planta, corte, fachada y detalles constructivos para reconocer caminos de transmisión.",
        "Distingue el cálculo según ISO 12354 de la clasificación conforme a ISO/TS 19488.",
        "Prepara los datos de entrada, los modelos y la trazabilidad necesaria antes de usar SONARA.",
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
    _header(2, "Lectura acústica de planos y cortes", "Relacionar geometría, encuentros y caminos de transmisión con cada cálculo posterior.")
    _project_badge()
    tabs = st.tabs(["Planta tipo", "Corte A–A", "Fachada norte", "Detalles críticos"])
    with tabs[0]:
        _show_drawing("planta_tipo.svg", "Planta tipo · tercer piso · unidad A-302 destacada")
    with tabs[1]:
        _show_drawing("corte_aa.svg", "Corte A–A · apilamiento vertical y losa evaluada")
    with tabs[2]:
        _show_drawing("fachada_norte.svg", "Fachada norte · paños opacos y vanos de A-302")
    with tabs[3]:
        _show_drawing("detalles_constructivos.svg", "Detalles académicos · medianero, losa flotante y shaft")
    st.markdown("### Matriz de adyacencias")
    matrix = [
        ["AI-01", "A-301", "A-302", "M-01", "Directa + flancos"],
        ["IM-01", "A-402", "A-302", "L-01", "Estructural + radiación"],
        ["FA-01", "Exterior norte", "Estar A-302", "F-01 + V-01", "Compuesta"],
        ["IN-01", "Shaft S-01", "Dormitorio A-302", "Tubería + cierre", "Estructural + aérea"],
    ]
    st.dataframe(pd.DataFrame(matrix, columns=["Caso", "Fuente", "Receptor", "Elemento", "Vías a revisar"]), hide_index=True, width="stretch")
    findings = st.text_area("Tres riesgos constructivos observados en los planos", value=saved.get("c5l1_s2_findings", ""), height=130)
    if st.button("Guardar revisión de planos", key="c5l1_s2_save", width="stretch"):
        if len(findings.strip()) < 100:
            st.warning("Registra al menos tres riesgos con una explicación breve.")
        else:
            _save(lab, saved, 2, c5l1_s2_findings=findings)
            st.success("Revisión de planos guardada.")


def _stage3(lab, saved):
    _header(3, "Marco de clasificación ISO/TS 19488", "Definir qué se clasificará y qué evidencia debe respaldar cada categoría.")
    st.markdown(
        """
        ### Separación de responsabilidades

        - **SONARA:** calcula prestaciones acústicas de diseño a partir de la geometría, los sistemas y los supuestos ingresados.
        - **Alumno:** verifica el indicador, consulta ISO/TS 19488:2021, selecciona el umbral aplicable, asigna la clase y explica las limitaciones.
        - **Laboratorio:** organiza el expediente y conserva trazabilidad; no entrega una clase automática ni reproduce tablas normativas.

        La clasificación de proyecto es una **estimación de diseño**. No equivale a una clasificación obtenida mediante mediciones finales en obra.
        """
    )
    mapping = [
        ["Aéreo interior", "DₙT,w y adaptaciones espectrales", "Mayor suele representar mejor desempeño"],
        ["Impacto", "L′ₙT,w y adaptación aplicable", "Menor suele representar mejor desempeño"],
        ["Fachada", "D₂m,nT,w y adaptaciones espectrales", "Mayor suele representar mejor desempeño"],
        ["Instalaciones", "Nivel de servicio y condición de operación", "Menor suele representar mejor desempeño"],
    ]
    st.dataframe(pd.DataFrame(mapping, columns=["Familia", "Descriptor por comprobar", "Sentido de desempeño"]), hide_index=True, width="stretch")
    st.info(
        "ISO/TS 19488:2021 continúa siendo la edición publicada utilizada en este laboratorio. "
        "ISO mantiene una segunda edición en desarrollo; antes de clasificar, comprueba el estado y la edición vigente."
    )
    iso_pdf_path = _asset("ISO-TS-19488-2021.pdf")
    if iso_pdf_path.is_file():
        st.download_button(
            "📘 Descargar norma ISO/TS 19488:2021 · PDF",
            data=iso_pdf_path.read_bytes(),
            file_name="ISO-TS-19488-2021.pdf",
            mime="application/pdf",
            width="stretch",
            key="c5l1_stage3_iso19488_pdf",
        )
    else:
        st.error("El PDF de ISO/TS 19488:2021 no está disponible para descargar.")
    scope = st.text_area(
        "Declaración de alcance de tu clasificación",
        value=saved.get("c5l1_s3_scope", ""),
        placeholder="Edición normativa consultada, unidad evaluada, categorías incluidas, fase de diseño y exclusiones.",
        height=140,
    )
    if st.button("Guardar alcance normativo", key="c5l1_s3_save", width="stretch"):
        if "19488" not in scope or len(scope.strip()) < 120:
            st.warning("Incluye ISO/TS 19488 y desarrolla el alcance con al menos 120 caracteres.")
        else:
            _save(lab, saved, 3, c5l1_s3_scope=scope)
            st.success("Alcance guardado. Aún no se ha asignado ninguna clase.")


def _stage4(lab, saved):
    _header(4, "Protocolo de modelación y trazabilidad", "Preparar datos coherentes antes de abrir SONARA y evitar resultados sin respaldo.")
    checklist = [
        ["Geometría", "Áreas, volúmenes, longitudes de unión y relación fuente–receptor", "Planos del caso"],
        ["Elementos", "Capas, espesores, masas y condiciones de montaje", "Cuadro de materialidades"],
        ["Uniones", "Tipo de encuentro y caminos laterales considerados", "Corte y detalles"],
        ["Fuente", "Condición de operación o exposición exterior", "Hipótesis declarada"],
        ["Salida", "Descriptor, bandas, unidades y versión del cálculo", "Registro SONARA"],
    ]
    st.dataframe(pd.DataFrame(checklist, columns=["Grupo", "Dato mínimo", "Evidencia"]), hide_index=True, width="stretch")
    st.error("No conviertas un Rw de catálogo directamente en DₙT,w, R′w o D₂m,nT,w. Son magnitudes de contextos diferentes.")
    st.markdown("### Ruta de diseño por elemento")
    st.dataframe(
        pd.DataFrame([
            ["M-01 y flancos", "Ruido aéreo → Transmisión entre recintos", "DₙT,w y adaptaciones finales", "Etapa 5"],
            ["L-01, piso y cielo", "Ruido de impacto → ISO 12354-2", "L′ₙT,w y CI", "Etapa 6"],
            ["F-01 + V-01", "Ruido aéreo → Fachada", "D₂m,nT,w y adaptaciones finales", "Etapa 7"],
            ["S-01 y fijaciones", "Ruido aéreo → Ruido de instalaciones", "LAeq / LAFmax según datos y operación", "Etapa 8"],
        ], columns=["Diseño", "Módulo SONARA", "Resultado que vuelve al laboratorio", "Guía detallada"]),
        hide_index=True, width="stretch",
    )
    st.markdown(
        "**Ciclo de trabajo:** define el objetivo y su descriptor → calcula la solución base → "
        "identifica el camino dominante → modifica una variable → recalcula → compara y justifica. "
        "Guarda una solución base y una variante por caso. Mantén geometría, operación y criterio "
        "de comparación constantes salvo que el cambio sea parte explícita del diseño."
    )
    st.info(
        "Los datos que no figuran en el expediente —TR, rigidez dinámica, espectros de fuente o "
        "propiedades de uniones— deben obtenerse de una ficha o declararse como hipótesis académicas. "
        "No conserves un valor por defecto de SONARA sin justificarlo."
    )
    _sonara_button("Abrir SONARA y preparar el proyecto Los Alerces")
    protocol = st.text_area(
        "Protocolo personal de cálculo",
        value=saved.get("c5l1_s4_protocol", ""),
        placeholder="Describe cómo nombrarás versiones, qué capturas guardarás, cómo verificarás unidades y cómo registrarás cambios.",
        height=150,
    )
    if st.button("Aprobar protocolo y continuar", key="c5l1_s4_save", width="stretch"):
        if len(protocol.strip()) < 140:
            st.warning("Define un protocolo reproducible con al menos 140 caracteres.")
        else:
            _save(lab, saved, 4, c5l1_s4_protocol=protocol)
            st.success("Protocolo guardado. Ya puedes comenzar los cálculos.")


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
        [("laeq", "LAeq", "dB(A)"), ("lafmax", "LAFmax", "dB(A)")],
        "Representa la descarga sanitaria, el cierre S-01, las fijaciones y las vías estructural y aérea. Si el método no permite un descriptor, decláralo como limitación en vez de inventarlo.",
    )
    st.info("El cálculo de instalaciones depende fuertemente de datos de fuente, montaje y operación. Una estimación sin esos antecedentes debe informarse con una incertidumbre y un plan de verificación en obra.")


def _stage9(lab, saved):
    _header(9, "Matriz consolidada de resultados", "Revisar integridad, unidades y trazabilidad antes de consultar los umbrales de clasificación.")
    rows = []
    definitions = [
        ("AI-01", "Aéreo interior", "dntw", "DₙT,w", "dB"),
        ("IM-01", "Impacto", "lntw", "L′ₙT,w", "dB"),
        ("FA-01", "Fachada", "d2mntw", "D₂m,nT,w", "dB"),
        ("IN-01", "Instalaciones", "laeq", "LAeq", "dB(A)"),
        ("IN-01", "Instalaciones", "lafmax", "LAFmax", "dB(A)"),
    ]
    for code, family, key, descriptor, unit in definitions:
        result = saved.get(f"c5l1_result_{code}", {})
        status = "Registrado" if result.get(key) is not None else ("Sin determinar · justificado" if result.get("undetermined") else "Pendiente")
        rows.append([code, family, descriptor, result.get(key), unit, status])
    result_df = pd.DataFrame(rows, columns=["Caso", "Familia", "Descriptor", "Resultado", "Unidad", "Estado"])
    st.dataframe(result_df, hide_index=True, width="stretch")
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
            {case["code"]: saved.get(f"c5l1_result_{case['code']}", {}) for case in CALCULATION_CASES.values()},
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
            "Regla utilizada para obtener la conclusión global",
            value=previous.get("overall_rule", ""),
            height=100,
            placeholder="Explica la regla de agregación o por qué no corresponde asignar una clase global.",
        )
        conclusion = st.text_area(
            "Conclusión profesional y plan de verificación",
            value=previous.get("conclusion", ""),
            height=180,
            placeholder="Clasificación, categoría dominante, mejoras propuestas, incertidumbres y mediciones finales requeridas.",
        )
        submitted = st.form_submit_button("Entregar clasificación del proyecto", width="stretch")
    if submitted:
        invalid = [family for family in families if not entries[family]["class"].strip() or not entries[family]["threshold"].strip() or len(entries[family]["justification"].strip()) < 20]
        results_ready = all(saved.get(f"c5l1_result_{code}") for code in ["AI-01", "IM-01", "FA-01", "IN-01"])
        if not results_ready:
            st.warning("Faltan resultados de SONARA. Completa las Etapas 5 a 8 antes de entregar.")
        elif invalid:
            st.warning("Completa clase, umbral y justificación para: " + ", ".join(invalid))
        elif len(overall_rule.strip()) < 80 or len(conclusion.strip()) < 180:
            st.warning("Desarrolla la regla global y la conclusión con la extensión mínima solicitada.")
        else:
            payload = {**entries, "overall_rule": overall_rule, "conclusion": conclusion, "standard": "ISO/TS 19488:2021", "phase": "Diseño"}
            _save(lab, saved, 10, c5l1_classification=payload)
            st.success("Clasificación entregada para revisión docente. Se conserva como clasificación de diseño realizada por el alumno.")


_STAGES = [_stage0, _stage1, _stage2, _stage3, _stage4, _stage5, _stage6, _stage7, _stage8, _stage9, _stage10]


def run_stage(stage, lab, saved, runtime):
    _bind_runtime(runtime)
    stage = max(0, min(int(stage), 10))
    return _STAGES[stage](lab, saved)
