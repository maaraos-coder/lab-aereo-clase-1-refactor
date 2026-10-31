"""Curso 5 · Laboratorio 1 · Certificación acústica de viviendas.

Diseño acústico residencial orientado a clase A. SONARA se utiliza como motor de
cálculo externo; la selección de indicadores, la trazabilidad y la
clasificación ISO/TS 19488 son responsabilidad del estudiante.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


CLASS_ID = "clase-09-certificaciones-lab-1"
EXERCISE_SCOPE = ("ISO/TS 19488:2021 · fase de diseño. Objetivo del proyecto: clase A para Los Alerces. "
    "Desarrollo obligatorio del laboratorio: AI-01 (aéreo A-301 → A-302), IM-01 (impacto A-402 → A-302), "
    "FA-01 (fachada norte → estar A-302) e IN-01 (descarga sanitaria → dormitorio A-302), "
    "con solución base y rediseño en Proyecto de SONARA. La conclusión se limita a estos cuatro casos; "
    "no acredita por sí sola clase global de A-302 ni de las 20 viviendas. La extensión al edificio y "
    "las inspecciones/mediciones posteriores se explican como contexto, sin campaña de ensayos en este ejercicio.")

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
    "status": "Proyecto de diseño acústico · objetivo clase A",
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
    ["Cocina", 7.8, 19.5, "Interior", "Distribuidor y estar-comedor"],
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


# Orientaciones de revisión: no son resultados precalculados de SONARA.
TEACHER_GUIDE = {
    0: ("Encuadre del encargo", [
        ("Comprensión del caso", "Reconoce el encargo de diseñar soluciones para alcanzar clase A en un edificio de 20 viviendas, comenzando por A-302. Distingue diseño, clasificación preliminar y verificación de obra."),
        ("Producto esperado", "Expediente con diagnóstico, planos, objetivo, protocolo, cuatro cálculos base/variante, matriz e informe de clasificación con alcance."),
    ], "No presentar el laboratorio como certificación real ni atribuir resultados al edificio completo."),
    1: ("Diagnóstico y plan de predicciones", [
        ("Diagnóstico esperado", "AI-01: estar A-301 → estar A-302, muro M-01 y flancos. IM-01: estar A-402 → estar A-302, losa L-01 y uniones. FA-01: exterior norte → estar A-302, F-01/V-01 y juntas. IN-01: descarga sanitaria → dormitorio A-302, cierre S-01, fijaciones y vías aérea/estructural."),
        ("Procedimiento", "El procedimiento futuro es contexto opcional. El laboratorio desarrolla la fase de predicción del procedimiento A; inspecciones y mediciones quedan para etapas posteriores de una obra. No confundir modelos de SONARA con ensayos."),
        ("Requisitos A", "Revisar que el alumno haya elegido para cada caso la fila correcta, descriptor, límite/sentido, condiciones y requisitos adicionales de clase A, con referencia a tabla/fila/nota/página. No aceptar una letra A sin criterio registrado."),
        ("Plan de predicciones", "Exigir cuatro casos base/rediseño con entradas, descriptores y evidencia en SONARA. Las 20 viviendas proceden de 5 pisos × 4 departamentos; no son una muestra ISO. Identificar modelos adicionales por soluciones, geometrías, uniones, exposición e instalaciones. No pedir número de ensayos de campo."),
        ("Alcance", "Distingue los cuatro casos preliminares de A-302 de las demás situaciones y de las otras 19 viviendas. Identifica planos completos, tipologías, fuentes y verificación pendientes."),
    ], "No aceptar dos viviendas solo por aplicar un porcentaje a 20, sin justificar representatividad y procedimiento."),
    2: ("Lectura de planos", [
        ("Operaciones esperadas", "M-01: 4,08 × 2,50 = 10,20 m². Estar: 20,40 × 2,50 = 51,0 m³. FA-01: 15,30 − 4,80 = 10,50 m² opacos; ventana 4,80 m². V-02 pertenece al dormitorio."),
        ("Tres riesgos razonados", "Ejemplos aceptables: continuidad rígida en encuentros → flancos; puente perimetral del piso flotante → transmisión de impacto; juntas de ventana o shaft sin sellar → fuga aérea; fijaciones sanitarias rígidas → vía estructural. Cada riesgo debe relacionar elemento, mecanismo y medida."),
        ("Datos faltantes", "TR, densidades documentadas, rigidez dinámica o ficha ΔL, datos espectrales sanitarios, uniones y exposición exterior: explicar fuente de obtención y efecto en el modelo."),
    ], "No sumar sobrelosa a los 160 mm de losa estructural ni deducir rigidez o potencia sonora a partir del dibujo."),
    3: ("Objetivo y alcance", [
        ("Objetivo", "La meta obligatoria es clase A. Revisar tabiques, muros, ventanas, puertas, losas, encuentros e instalaciones; exigir rediseño cuando una característica no alcance A. Es una meta, no la clase obtenida. Debe citar ISO/TS 19488:2021 y acotar las cuatro situaciones en fase de diseño."),
        ("Regla de clasificación", "La clase común depende del requisito limitante entre las situaciones aplicables verificadas; no se promedian letras ni dB. La ausencia de evidencia impide concluir conformidad global completa."),
        ("Comprobación del ejemplo", "En el ejemplo hipotético de esta etapa: aéreo C, impacto C, fachada C e instalaciones D antes del rediseño; el conjunto de esos casos queda limitado a D. Tras mejorar instalaciones a C, los cuatro casos alcanzan C, sin acreditar vivienda ni edificio completos."),
    ], "No aceptar el ejemplo resuelto como cálculo propio ni una clase A/B sin comprobar requisitos adicionales aplicables."),
    4: ("Protocolo y entradas", [
        ("Flujo de proyecto", "Exigir proyecto Los Alerces con recintos y matriz de elementos; cálculos realizados desde Diseñar, base y rediseño guardados en Soluciones y evidencias del Informe. Contrastar el requisito del catálogo con la meta clase A."),
        ("Trazabilidad", "Revisar TR del estar/dormitorio, densidad HA, exposición exterior y procedencia de cada dato. Distinguir ficha, hipótesis académica y antecedente pendiente; no imponer un TR o densidad únicos sin fuente."),
        ("Piso", "Si usa modelo físico: masa superficial de sobrelosa = densidad × 0,040 m y s′ documentada. Si usa catálogo medido, justificar compatibilidad del montaje y por qué s′ no se usa."),
        ("Criterios y protocolo", "Para cada caso: descriptor, límite, sentido de comparación, tabla/nota y objetivo. Exigir nombres Base/Variante, capturas/curvas y condiciones constantes para comparar."),
    ], "Los valores iniciales de SONARA no constituyen antecedentes del proyecto. Revisar coherencia de unidades y fuentes antes de aprobar el protocolo."),
    5: ("AI-01 · Aéreo interior", [
        ("Modelo esperado", "M-01 de HA 180 mm; S = 10,20 m², V receptor = 51,0 m³ y TR declarado. Revisar caminos directo y laterales, uniones y su trazabilidad."),
        ("Resultado y mejora", "Exigir DₙT,w y adaptaciones de la curva final entre recintos. Para DₙT,A comprobar DₙT,w + C. Comparar base y variante con igual geometría e identificar el camino dominante; mayor aislamiento es mejor."),
    ], "Rw del muro no sustituye DₙT,w. No trasladar automáticamente C/Ctr del elemento a la curva entre recintos; declarar la reconstrucción aproximada por Rw."),
    6: ("IM-01 · Impacto", [
        ("Modelo esperado", "Losa HA 160 mm, área 20,40 m², V = 51,0 m³; base sin tratamiento y variante documentada con piso/cielo si corresponde. Misma geometría, TR y condiciones de comparación."),
        ("Revisión técnica", "Catálogo ΔL medido compatible o modelo físico con masa de sobrelosa y s′ trazable. Revisar puentes rígidos y flancos. Exigir L′ₙT,w y CI compatibles; menor nivel es mejor."),
    ], "No sumar mejoras de catálogo y modelo físico del mismo sistema. La diferencia base/variante no es automáticamente el ΔLw de ensayo del revestimiento."),
    7: ("FA-01 · Fachada", [
        ("Modelo esperado", "Fachada 15,30 m²: opaco F-01 10,50 m² + V-01 4,80 m²; V = 51,0 m³. Verificar panel desacoplado, DVH 6/12/4, juntas, exposición y corrección de forma justificadas."),
        ("Comparación", "Exigir resultado de fachada completa y adaptaciones finales, correspondencia del descriptor con el criterio elegido y exposición exterior declarada. La variante debe actuar sobre el componente dominante conservando áreas y exposición."),
    ], "No promediar aritméticamente aislamientos ni usar Rw de la ventana como aislamiento global. Declarar la aproximación del traslado Manual Rw/Ctr."),
    8: ("IN-01 · Instalaciones", [
        ("Modelo esperado", "Fuente sanitaria espectral y condición temporal documentadas, cierre S-01 de 120 mm totales, receptor dormitorio V = 28,8 m³, TR/absorción y vías justificadas."),
        ("Descriptores", "Comprobar normalización a T₀ = 0,5 s y compatibilidad temporal de LAeq,nT y LAFmax,nT. No convertir un promedio en máximo FAST. Si falta un dato, aceptar sin determinar únicamente con limitación y plan para obtenerlo."),
        ("Variante", "Comparar cierre, sellado o fijaciones con la misma fuente, operación y receptor. La vía estructural exige datos de excitación/transferencia compatibles; no una atenuación arbitraria."),
    ], "No premiar valores inventados para completar campos. Un descriptor requerido sin determinar limita la conclusión global."),
    9: ("Matriz y revisión crítica", [
        ("Integridad", "Contrastar AI-01, IM-01, FA-01 e IN-01 con las evidencias y resultados guardados. Revisar unidades, términos espectrales, normalización y estados pendiente/sin determinar."),
        ("Operaciones", "DₙT,A = DₙT,w + C y aislamiento de fachada adaptado = D₂m,nT,w + Ctr solo con adaptaciones compatibles. Estas operaciones no asignan por sí solas una clase."),
        ("Juicio crítico", "Identificar resultado débil respecto del objetivo, incertidumbre dominante y verificación en obra concreta. Debe conservar base, cambio y evidencias por caso."),
    ], "Una matriz llena no demuestra cumplimiento; cualquier dato sin determinar debe conservar su limitación en el informe."),
    10: ("Clasificación e informe final", [
        ("Clase por caso", "Rehacer la comparación de los resultados propios con descriptor, umbral, sentido ≥/≤, tabla, fila y notas de la edición consultada. Revisar adaptaciones y requisitos adicionales antes de aceptar la letra."),
        ("Clase limitante", "Comprobar la mejor clase común sustentada, sin promediar. Distinguir clase objetivo, clase alcanzada por caso y conclusión preliminar de los cuatro casos; NPD no equivale a clase F."),
        ("Extensión al edificio", "Exigir plan para tipologías y situaciones pendientes, otros recintos/fachadas, accesos/escaleras e instalaciones aplicables, cobertura del muestreo, inspecciones y mediciones. No extrapolar A-302 a 20 viviendas."),
        ("Informe profesional", "Debe enlazar alcance → fuentes/entradas → base/variante → curva/descriptor → umbral/clase → limitante → incertidumbres y verificación. Aceptar propuestas distintas si son reproducibles y técnicamente justificadas."),
    ], "No existe una letra única correcta para todos los alumnos: depende de sus modelos y datos. No aceptar certificación global cuando falta cobertura o evidencia."),
}


def _lab_table(data, **kwargs):
    """Tablas de lectura con formato consistente, contenido escapado y desplazamiento móvil."""
    from html import escape
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    def cell(value):
        if value is None:
            return "—"
        try:
            if pd.isna(value):
                return "—"
        except (TypeError, ValueError):
            pass
        return escape(str(value))
    headings = "".join("<th scope='col'>" + escape(str(col)) + "</th>" for col in frame.columns)
    rows = "".join("<tr>" + "".join("<td>" + cell(value) + "</td>" for value in row) + "</tr>" for row in frame.itertuples(index=False, name=None))
    st.markdown(
        "<style>.c5-table-wrap{overflow-x:auto;border:1px solid #cadce8;border-radius:14px;margin:16px 0 24px;background:#fff;box-shadow:0 4px 16px #17384e08}"
        ".c5-table{width:100%;border-collapse:separate;border-spacing:0;color:#193c53;font-size:1rem;line-height:1.6}"
        ".c5-table th{background:#164c68;color:#fff!important;text-align:left;font-weight:700;padding:16px 18px;border:0;vertical-align:top}"
        ".c5-table td{padding:16px 18px;border:0;border-bottom:1px solid #e0eaf0;vertical-align:top;min-width:135px;overflow-wrap:anywhere}"
        ".c5-table tbody tr:nth-child(even){background:#f0f6fa}.c5-table tbody tr:last-child td{border-bottom:0}"
        ".c5-table tbody td:first-child{font-weight:650;color:#125470}.c5-table tbody tr:hover{background:#e7f3f7}"
        "@media(max-width:640px){.c5-table{font-size:.95rem}.c5-table td,.c5-table th{padding:12px;min-width:125px}}"
        ".c5-guide-card{border:1px solid #ccdee8;border-left:4px solid #12808b;border-radius:12px;background:#fff;padding:18px 20px;margin:14px 0;color:#193c53;line-height:1.65}"
        ".c5-guide-card strong{display:block;color:#125470;font-size:1.06rem;margin-bottom:8px}</style>"
        "<div class='c5-table-wrap' role='region' aria-label='Tabla de síntesis' tabindex='0'><table class='c5-table'><thead><tr>" + headings + "</tr></thead><tbody>" + rows + "</tbody></table></div>",
        unsafe_allow_html=True,
    )


def _teacher_stage1_answers():
    st.markdown("### Respuestas de referencia · actividad 1")
    st.caption("Corresponde a los cuatro apartados que completa el estudiante. ISO/TS 19488:2021 · Acoustics — Acoustic classification of dwellings. Páginas impresas / páginas del PDF del laboratorio.")
    st.markdown("#### 1 · Diagnóstico: fuente, receptor, camino y riesgo")
    _lab_table(pd.DataFrame([
        ["AI-01", "Estar A-301 → estar A-302", "M-01, 10,20 m²; receptor 51,0 m³", "Paso directo por el separador y caminos laterales por losas y muros. Un trasdosado puede mejorar la vía directa sin resolver el flanco dominante."],
        ["IM-01", "Estar A-402 → estar A-302", "L-01, HA 160 mm; piso de 20,40 m²", "Excitación de la losa por impactos y transmisión estructural. Puentes rígidos del piso flotante y encuentros pueden anular parte de la mejora."],
        ["FA-01", "Exterior norte → estar A-302", "15,30 m²: opaco 10,50 + ventana 4,80 m²", "La ventana y las juntas pueden dominar la fachada. El alumno debe combinar componentes por energía y declarar exposición exterior; no promediar sus Rw."],
        ["IN-01", "Descarga sanitaria → dormitorio A-302", "Shaft S-01; receptor 28,8 m³", "Ruido aéreo a través del cierre/juntas y transmisión estructural por fijaciones. Se necesita fuente espectral y operación documentadas."],
    ], columns=["Caso", "Fuente → receptor", "Datos del caso", "Respuesta razonada esperada"]))
    st.markdown("#### 2 · Requisitos de A: qué debe aparecer en los campos")
    _lab_table(pd.DataFrame([
        ["AI-01", "DₙT,50 = DₙT,w + C₅₀–₃₁₅₀", "≥ 58 dB", "Entre recintos habitables de viviendas diferentes, en todas direcciones. Usar adaptación de la curva final entre recintos. Una referencia simplificada por DₙT,w exige justificar las notas y no acredita automáticamente la baja frecuencia.", "§5.2 · tabla 1, fila 1 y notas · p. 7 / PDF 13"],
        ["IM-01", "L′ₙT,w y L′ₙT,50", "≤ 46 dB y ≤ 50 dB, respectivamente", "Entre viviendas. Para A deben comprobarse ambos criterios; L′ₙT,50 incorpora el término de adaptación de impacto de baja frecuencia correspondiente. No basta anotar CI sin comprobar su intervalo ni la suma.", "§5.3 · tabla 2, fila 1 y notas · p. 8 / PDF 14"],
        ["FA-01", "Descriptor de fachada adaptado exigido por la tabla 3", "≥ Lden − 20 dB, junto con mínimos y notas aplicables", "No hay un único número sin exposición declarada. Ejemplo exclusivamente ilustrativo: con Lden = 65 dB, el término da 45 dB. No adoptar 65 dB como antecedente real del proyecto. Verificar descriptor, ponderación y alcance de las notas.", "§5.4 · tabla 3 y notas · p. 8 / PDF 14"],
        ["IN-01", "LAFmax,nT para operación intermitente; LAeq,nT si corresponde a funcionamiento continuo", "≤ 26 dB(A) para máximo FAST; ≤ 22 dB(A) para equivalente continuo", "La descarga del caso se trata según su operación intermitente documentada. No intercambiar máximo, promedio ni FAST/SLOW. Aplicar T₀ = 0,5 s; si el alumno usa otra magnitud admitida, revisar la equivalencia y notas antes de comparar.", "§5.5 · tabla 4, fila y notas de operación · p. 9 / PDF 15"],
    ], columns=["Caso", "Descriptor esperado", "Criterio de clase A", "Condiciones que debe explicar", "Referencia"]))
    st.info("Estos son objetivos de comparación, no resultados calculados ni soluciones constructivas únicas. Si SONARA no entrega un descriptor adicional exigido para A, el alumno debe identificarlo y documentar cómo lo obtendría; no concluir clase A completa con un indicador incompleto.")
    st.markdown("#### 3 · Plan de predicciones: ejemplo de respuesta completa")
    st.markdown("Crear Los Alerces en Proyecto de SONARA; registrar recintos y requerimientos AI-01, IM-01, FA-01 e IN-01. Para cada caso conservar Base y Rediseño_A con la misma geometría, fuente y condiciones de comparación. Registrar materiales, espesores, uniones, flancos, TR y procedencia de datos; guardar configuración, curvas, indicadores y referencia del requisito. Comparar el resultado con A y señalar la brecha si no cumple. Son cuatro casos con al menos dos configuraciones cada uno; no son ocho mediciones ni ocho viviendas. Añadir modelos si cambian solución, geometría, encuentros, exposición o instalaciones.")
    st.markdown("#### 4 · Alcance: ejemplo de conclusión admisible")
    st.markdown("La propuesta comprende cuatro situaciones de A-302 en fase de diseño. Las 20 viviendas corresponden a cinco pisos con cuatro departamentos por piso. Para extender la propuesta al edificio faltan inventario de tipologías, otros pares de recintos, fachadas/exposiciones, puertas y accesos cuando correspondan, instalaciones y zonas comunes aplicables. Los tabiques interiores pueden diseñarse adicionalmente, pero no equivalen al separador entre viviendas. Las inspecciones y mediciones son fases futuras del procedimiento A; aquí no se pide campaña de ensayos.")
    st.warning("**Errores que requieren corrección:** confundir Rw con aislamiento entre recintos; omitir condiciones o requisitos adicionales de A; usar un máximo como promedio; asignar clase global sin cobertura suficiente.")
    st.markdown("#### Criterios para devolver la actividad")
    _lab_table(pd.DataFrame([
        ["Diagnóstico", "Cuatro recorridos completos y riesgos vinculados al elemento y mecanismo.", "Solo enumera materiales o confunde fuente y receptor."],
        ["Requisitos A", "Descriptor + límite/sentido + condiciones + tabla/fila/nota/página para cada caso.", "Solo escribe A, usa Rw para toda situación o ignora requisitos adicionales."],
        ["Plan", "Base/rediseño, entradas trazables, comparación y evidencia guardada en Proyecto.", "Pide mediciones ahora, inventa datos o presenta una sola cifra sin configuración."],
        ["Alcance", "Distingue cuatro casos, vivienda y edificio; identifica modelos/datos pendientes.", "Extrapola automáticamente A-302 a las 20 viviendas."],
    ], columns=["Apartado", "Logrado", "Requiere corrección"]))
    st.markdown("**Criterio de revisión:** logrado si diagnóstico, requisitos, plan y alcance se sustentan con evidencia; parcialmente logrado si hay omisiones subsanables; por corregir si el descriptor, criterio o alcance invalida la conclusión. Guardar solo confirma la entrega.")


def _teacher_guide(stage):
    state = getattr(st, "session_state", {})
    if state.get("role") != "Docente" or state.get("projection_mode"):
        return
    title, criteria, errors = TEACHER_GUIDE[stage]
    with st.expander(f"👨‍🏫 Pauta docente · Etapa {stage} · {title}", expanded=False):
        st.caption("Uso exclusivo del docente · respuestas esperadas y criterios de revisión formativa.")
        if stage == 1:
            _teacher_stage1_answers()
            return
        from html import escape
        for criterion, expected in criteria:
            st.markdown("<div class='c5-guide-card'><strong>" + escape(criterion) + "</strong>" + escape(expected) + "</div>", unsafe_allow_html=True)
        if stage in range(5, 9):
            family = list(CALCULATION_CASES)[stage - 5]
            st.markdown("**Evidencias mínimas:** " + SONARA_DESIGN_GUIDES[family]["evidence"])
            st.info("No hay un resultado numérico único: revisar entradas, método, curva y comparación reproducible. Los números de etapa 3 son hipotéticos.")
        st.warning("**Errores que requieren corrección:** " + errors)
        st.markdown("**Criterio de revisión:** logrado si cumple los criterios con evidencia; parcialmente logrado si hay omisiones subsanables; por corregir si el método, descriptor o alcance invalida la conclusión. Guardar el formulario acredita entrega, no corrección técnica.")


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
    st.info("**Meta del proyecto: clase A.** Diseña las soluciones constructivas y comprueba su desempeño mediante SONARA.")


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
        "route": "Proyecto → Elementos → Diseñar: Ruido aéreo e ISO 12354-1 → Soluciones.",
        "inputs": [
            ["M-01 · separador", "Hormigón armado · 180 mm", "Selecciona una ficha con propiedades completas; registra densidad y procedencia."],
            ["Geometría AI-01", "S = 10,2 m² · V receptor = 51,0 m³", "Copia el TR adoptado desde tu protocolo; no confundas área de muro con área de piso."],
            ["Flancos", "Losa, muros laterales y fachada según planos", "Obtén espesores y longitudes de unión del expediente; justifica cualquier dato faltante."],
        ],
        "steps": [
            "Dentro de Proyecto → Diseñar, selecciona Ruido aéreo y Panel simple y modela M-01 con una capa de hormigón de 180 mm. Conserva R(f), Rw, C y Ctr como resultados del elemento.",
            "En el mismo proyecto, activa el requerimiento entre recintos y selecciona Diseñar → ISO 12354-1. Ingresa S = 10,2 m², V = 51,0 m³ y el TR receptor declarado. Introduce el Rw calculado en «Rw elemento separador».",
            "Activa los flancos que existan en los planos. Para cada encuentro registra material, masa superficial, longitud y tipo de unión o Kij. Usa «Calcular con SONARA» cuando puedas definir sus capas.",
            "Identifica si domina el camino directo o uno lateral. Diseña una variante: modificar M-01 o añadir un trasdosado desacoplado; si domina un flanco, actúa sobre el encuentro correspondiente.",
            "Recalcula el descriptor entre recintos con la misma geometría y compara la variante con la base. Registra DₙT,w y las adaptaciones que correspondan a la curva final.",
        ],
        "limit": "El ingreso directo por Rw del módulo entre recintos reconstruye una curva de referencia: declara esa aproximación. No copies C y Ctr de la placa como si fueran los términos de la curva final entre recintos.",
        "evidence": "Configuración de M-01 y su variante, captura del visual constructivo, entradas de recintos/uniones, curvas y resultado final DₙT,w.",
    },
    "Impacto": {
        "route": "Proyecto → Elementos (Paramento horizontal) → Diseñar → Ruido de impacto → Soluciones.",
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
        "route": "Proyecto → Elementos (Fachada, Ventana y Puerta según corresponda) → Diseñar → Fachada ISO 12354-3 → Soluciones.",
        "inputs": [
            ["Fachada FA-01", "Área total = 15,3 m² · V = 51,0 m³", "Mismo estar receptor que AI-01 e IM-01."],
            ["V-01 · ventana estar", "DVH 6/12/4 · 4,80 m²", "6 y 4 mm son vidrios; 12 mm es cámara, no una placa."],
            ["F-01 · paño opaco", "10,50 m² · HA 150 + cámara 50 + yeso 15 mm", "150 + 50 + 15 mm no se modela como tres capas sólidas adheridas."],
        ],
        "steps": [
            "Desde Proyecto → Diseñar → Ruido aéreo, diseña F-01 como Panel doble: hoja de hormigón de 150 mm, cámara de 50 mm con absorbente y hoja de yeso de 15 mm. Declara el montaje desacoplado y la ficha del absorbente.",
            "Desde Proyecto → Diseñar → Ruido aéreo, diseña V-01 como Ventana → DVH: vidrio 6 mm, aire 12 mm y vidrio 4 mm. Documenta que el conjunto real también depende de marco, juntas y condiciones de ensayo.",
            "Abre Fachada (ISO 12354-3). Ingresa volumen 51,0 m³ y área total 15,3 m². Crea dos componentes: opaco 10,50 m² y ventana 4,80 m².",
            "El selector SONARA de cada componente calcula una placa simple. Para trasladar tu panel doble o DVH usa «Manual Rw/Ctr» con sus resultados; documenta la reconstrucción espectral aproximada que realiza ese modo.",
            "Ingresa exposición exterior y corrección por forma a partir de antecedentes o hipótesis identificadas. Añade juntas o aireadores únicamente cuando puedas justificar sus datos.",
            "Compara una variante del componente dominante —ventana, sellos o paño opaco— manteniendo áreas y exposición. Guarda D₂m,nT,w y C/Ctr de la fachada completa.",
        ],
        "limit": "El modo Manual Rw/Ctr no transfiere íntegramente el espectro calculado del componente. Informa esa limitación. No uses el Rw de la ventana como resultado global ni registres el dormitorio V-02 dentro del caso del estar V-01.",
        "evidence": "Modelos F-01 y V-01, Rw/Ctr transferidos, áreas, hipótesis exterior/forma, juntas consideradas y curva final de fachada.",
    },
    "Instalaciones": {
        "route": "Proyecto → Elementos (Instalaciones / HVAC) → Diseñar → Instalaciones EN 12354-5 → Soluciones.",
        "inputs": [
            ["IN-01 · descarga sanitaria", "Condición de operación definida por el alumno", "Se requiere espectro de fuente trazable; los valores iniciales de SONARA son ejemplos."],
            ["S-01 · cierre", "2 RF 12,5 + cámara 70 + 2 RF 12,5 = 120 mm", "Ver AC-04; selecciona las fichas de placas y absorbente. No asignes 120 mm a cada capa."],
            ["Receptor", "Dormitorio principal · V = 28,8 m³", "Declara TR, absorción equivalente y recorrido; A ≈ 0,16 V/T como hipótesis de campo difuso."],
        ],
        "steps": [
            "Define una descarga o ciclo de funcionamiento reproducible, su duración y simultaneidad. Obtén datos espectrales de fabricante o ensayo; si no existen, identifica el cálculo como escenario académico.",
            "Desde Proyecto → Diseñar → Ruido aéreo, diseña el cierre S-01 como Panel doble con espesores y cámara expresamente definidos. Conserva R(f), no solo Rw.",
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
    st.markdown("**Continuidad del proyecto:** selecciona el elemento activo en Diseñar; calcula y guarda las soluciones con nombres como AI-01_Base y AI-01_Diseno_A. Comprueba en Soluciones que pertenecen al proyecto y requerimiento correctos. Conserva ambos resultados y recupéralos para el Informe.")
    _lab_table(
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
    st.info(f"**Meta obligatoria: Clase A. Objetivo registrado previamente:** {target}. Consulta el protocolo guardado antes de comparar variantes.")
    inputs = saved.get("c5l1_s4_inputs", {})
    if inputs:
        _lab_table(pd.DataFrame([
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
    _show_class_a_requirements(saved, case["code"])
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
        f'<br><span>Diseño para clase A · SONARA + ISO</span>'
        f'</div><div><strong>{active_minutes} min</strong></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:18px;padding:17px 19px;
        background:linear-gradient(135deg,#f8fcff,#edf6fb);margin:.8rem 0 1rem">
          <div style="font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
            ENCARGO · DISEÑO ACÚSTICO CLASE A
          </div>
          <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">
            Edificio Los Alerces · Departamento A-302
          </div>
          <div style="color:#587486;line-height:1.55;font-size:.84rem">
            Trabajarás con un expediente académico común de un edificio residencial de cinco pisos.
            Diseñarás tabiques, muros, ventanas, puertas y losas para alcanzar clase A; prepararás modelos y registrarás resultados obtenidos
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
        "Comprende las clases ISO y establece los requisitos de la meta obligatoria: clase A.",
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


def _show_class_a_requirements(saved, code=None):
    requirements = saved.get("c5l1_s1_requirements", {})
    rows = [[key, row.get("descriptor", ""), row.get("limit", ""), row.get("conditions", ""), row.get("reference", "")] for key, row in requirements.items() if code is None or key == code]
    st.markdown("#### Requisitos de clase A definidos por ti en la etapa 1")
    if rows:
        _lab_table(pd.DataFrame(rows, columns=["Caso", "Descriptor", "Límite A", "Condiciones", "Referencia"]))
        st.caption("Requisitos registrados por el alumno, pendientes de revisión técnica; guardar no valida la interpretación de la norma.")
    else:
        st.warning("Aún no hay requisitos de clase A guardados para este caso. Completa ese apartado en la etapa 1 antes de definir el modelo.")


def _coverage_explanation():
    """Guía visual de representatividad; ejemplos sin resultados atribuidos al proyecto."""
    st.markdown("### ¿Cuándo podemos decir que todo el edificio alcanza una clase?")
    st.markdown("**Aquí hacemos predicciones de diseño, no mediciones en terreno.** A-302 es el punto de partida para modelar cuatro situaciones acústicas. Para extender la propuesta al edificio, debemos identificar qué otras soluciones, encuentros, exposiciones y recintos necesitan cálculos adicionales.")
    st.markdown("""
<style>
.c5-coverage{--ink:#17384e;--muted:#456176;--line:#ccdde8;color:var(--ink);font-family:inherit;line-height:1.6;margin:1rem 0 1.8rem}
.c5-coverage *{box-sizing:border-box}
.c5-coverage .cv-hero{background:linear-gradient(120deg,#113b59,#126976);color:#fff;border-radius:20px;padding:24px;margin-bottom:18px}
.c5-coverage .cv-eyebrow{font-size:.8rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;margin:0 0 8px}
.c5-coverage .cv-hero h4{color:#fff;font-size:1.35rem;line-height:1.3;margin:0 0 12px}
.c5-coverage p{margin:0 0 12px;font-size:1rem}
.c5-coverage p:last-child{margin-bottom:0}
.c5-coverage .cv-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:14px 0 22px}
.c5-coverage .cv-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 12px #17384e08;min-width:0}
.c5-coverage .cv-head{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.c5-coverage .cv-num{display:flex;align-items:center;justify-content:center;flex:0 0 36px;height:36px;border-radius:12px;background:#e1f2f2;color:#09616a;font-weight:900}
.c5-coverage h4{color:var(--ink);font-size:1.12rem;line-height:1.35;margin:0}
.c5-coverage h5{color:var(--ink);font-size:1.06rem;margin:22px 0 10px}
.c5-coverage .cv-example{background:#edf5fb;border-left:3px solid #3281ad;padding:12px 14px;border-radius:0 10px 10px 0;margin:12px 0}
.c5-coverage .cv-ref{color:var(--muted);font-size:.85rem;line-height:1.5;border-top:1px solid #dbe6ed;padding-top:12px;margin-top:14px}
.c5-coverage .cv-wide{grid-column:1/-1}
.c5-coverage .cv-note{background:#fff4dc;border:1px solid #efd49d;padding:18px;border-radius:14px;margin:16px 0}
.c5-coverage .cv-success{background:#e6f4ee;border:1px solid #afd7c6;padding:18px;border-radius:14px;margin:16px 0}
.c5-coverage .cv-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:14px 0;border-bottom:1px solid #dbe6ed}
.c5-coverage .cv-row:last-child{border-bottom:0}
.c5-coverage .cv-small{font-size:.9rem;color:var(--muted)}
@media(max-width:640px){.c5-coverage .cv-grid{grid-template-columns:1fr}.c5-coverage .cv-wide{grid-column:auto}.c5-coverage .cv-card,.c5-coverage .cv-hero{padding:18px}.c5-coverage .cv-row{grid-template-columns:1fr;gap:6px}}
</style>
<section class="c5-coverage" aria-label="Cómo comprobar el edificio completo">
<div class="cv-hero"><div class="cv-eyebrow">La idea principal</div><h4>La evidencia debe cubrir lo que quieres clasificar</h4><p>Si quieres declarar clase A para todo el edificio, debes sustentar que <strong>todas las viviendas cumplen los criterios aplicables de A</strong>. Una vivienda favorable no demuestra cómo se comportan las demás.</p><p>En diseño no se trata de repetir el mismo cálculo 20 veces: se modelan las situaciones acústicas distintas y se justifica dónde puede aplicarse cada resultado. La clasificación del edificio terminado requiere verificación posterior.</p></div>
<div class="cv-grid">
<article class="cv-card"><div class="cv-head"><span class="cv-num">1</span><h4>Di de qué vas a hablar</h4></div><p><strong>“Alcance” significa qué incluye tu conclusión.</strong> Puedes hablar de una característica, de una vivienda o de todo el edificio.</p><div class="cv-example">En nuestro encargo: queremos diseñar las <strong>20 viviendas de Los Alerces para clase A</strong>. Comenzamos con cuatro situaciones de A-302.</div><p>Mientras falte comprobar el resto, informamos resultados de esos casos y una meta de diseño para el edificio.</p><div class="cv-ref">§4 · Acoustic classes · p. 6 / PDF 12.<br>A.1 · General · p. 11 / PDF 17.</div></article>
<article class="cv-card"><div class="cv-head"><span class="cv-num">2</span><h4>Busca lo que cambia entre viviendas</h4></div><p>Revisa <strong>muros, losas, encuentros, fachadas e instalaciones</strong>. Dos departamentos con la misma planta pueden tener condiciones acústicas distintas.</p><div class="cv-example">Uno mira a la avenida; otro al patio. Uno está junto a equipos; otro no. Aunque tengan igual ventana, la exposición exterior puede cambiar lo que deben cumplir.</div><p>Agrupa situaciones comparables y separa las que necesiten una comprobación diferente.</p><div class="cv-ref">§6 · Verification · pp. 9–10 / PDF 15–16.<br>A.1 · General · p. 11 / PDF 17.</div></article>
<article class="cv-card"><div class="cv-head"><span class="cv-num">3</span><h4>Justifica qué casos representan a cada grupo</h4></div><p>Elige situaciones que cubran cada solución y sus condiciones desfavorables. Explica <strong>por qué las elegidas representan a las que no evaluarás directamente</strong>.</p><div class="cv-example">A-302 no representa automáticamente a una vivienda frente a una avenida ni a otra junto a una sala de equipos. Esas situaciones necesitan evidencia que las cubra.</div><p>Si la ejecución, las uniones o el uso varían, puede ser necesario ampliar la muestra.</p><div class="cv-ref">§6 · Verification · p. 10 / PDF 16.<br>A.1–A.2.2 · General y procedimientos A/B · pp. 11–12 / PDF 17–18.</div></article>
<article class="cv-card"><div class="cv-head"><span class="cv-num">4</span><h4>Reúne la evidencia en cada fase</h4></div><p><strong>Ahora:</strong> calcula y rediseña las soluciones en Proyecto de SONARA. Relaciona cada resultado con sus recintos, elementos y condiciones.</p><div class="cv-example"><strong>Después:</strong> planifica inspecciones durante la obra y mediciones del edificio terminado para comprobar que lo diseñado se ejecutó y funciona.</div><p>Ese recorrido corresponde al procedimiento A. El procedimiento B verifica mediante mediciones finales.</p><div class="cv-ref">A.2.1 · Procedure A: Verification by calculations, visual inspections and field measurements · pp. 11–12 / PDF 17–18.<br>A.2.2 · Procedure B: Verification by field measurements only · p. 12 / PDF 18.</div></article>
<article class="cv-card cv-wide"><div class="cv-head"><span class="cv-num">5</span><h4>Comprueba si puedes concluir sobre todo el edificio</h4></div><p>Pregunta final: <strong>¿cada situación y característica aplicable está respaldada por evidencia suficiente?</strong> Si falta un grupo, déjalo pendiente y explica cómo lo verificarás.</p><div class="cv-success"><strong>Para alcanzar A:</strong> todos los requisitos aplicables deben quedar cubiertos y satisfechos. Si una característica alcanza B, hay que rediseñarla para cumplir el encargo A; si no tiene evidencia, todavía no puedes concluir la clase global.</div><div class="cv-ref">§4 · Acoustic classes · p. 6 / PDF 12.<br>A.3 · Contents of verification report for classification of a dwelling or a building · p. 13 / PDF 19.<br>A.4 · Classification examples · pp. 13–14 / PDF 19–20.</div></article>
</div>
<h5>Cuatro palabras, con ejemplos concretos</h5>
<div class="cv-card">
<div class="cv-row"><strong>Vivienda = el departamento completo</strong><span>A-302 contiene estar, dormitorios, cocina y baño. No es un único ensayo.</span></div>
<div class="cv-row"><strong>Recinto = una habitación</strong><span>El estar de A-302 puede recibir ruido de A-301 y del piso superior: son situaciones diferentes.</span></div>
<div class="cv-row"><strong>Tipo constructivo = una solución y su configuración</strong><span>Dos muros con iguales capas pueden necesitar revisión separada si cambian sus encuentros o caminos laterales.</span></div>
<div class="cv-row"><strong>Ensayo = comprobar una característica en una situación</strong><span>Evaluar ruido aéreo e impacto entre la misma pareja de recintos son dos evaluaciones con sus respectivos métodos.</span></div>
<p class="cv-small">Ejemplos didácticos para interpretar A.1–A.2.3, pp. 11–12 / PDF 17–18.</p>
</div>
<h5>Ahora: ¿qué tengo que calcular en SONARA?</h5>
<p>Trabaja en <strong>Proyecto → Recintos → Elementos → Diseñar → Soluciones</strong>. Para cada caso guarda una solución base, su rediseño hacia clase A, los datos de entrada y los resultados comparables.</p>
<div class="cv-card">
<div class="cv-row"><strong>AI-01 · Aéreo entre viviendas</strong><span>Emisor: estar A-301. Receptor: estar A-302. Diseña M-01 y sus encuentros; calcula el desempeño entre recintos, no solo el Rw del muro.</span></div>
<div class="cv-row"><strong>IM-01 · Impacto</strong><span>Emisor: estar A-402. Receptor: estar A-302. Compara losa/piso base con la solución tratada; revisa flancos y puentes rígidos.</span></div>
<div class="cv-row"><strong>FA-01 · Fachada</strong><span>Exterior norte → estar A-302. Diseña conjuntamente paño opaco, ventana y juntas, conservando áreas y exposición al comparar.</span></div>
<div class="cv-row"><strong>IN-01 · Instalaciones</strong><span>Descarga sanitaria → dormitorio A-302. Modela cierre, fijaciones y vías de transmisión con datos de fuente y operación documentados.</span></div>
<p><strong>Punto de partida: 4 casos × 2 configuraciones (base y rediseño) = 8 configuraciones calculadas.</strong> No son ocho viviendas ni ocho mediciones. Una configuración puede producir varios indicadores. Si una variante no alcanza A, añade iteraciones y documenta la brecha.</p>
<p class="cv-small">Organización del ejercicio, no mínimo de predicciones fijado por ISO/TS 19488.</p>
</div>
<h5>Después: ¿cómo extiendo el diseño a las demás viviendas?</h5>
<div class="cv-grid">
<article class="cv-card"><h4>Puede reutilizarse si justificas la equivalencia</h4><p>Misma solución y montaje, geometría relevante, uniones, flancos, condiciones de fuente y exposición. Identifica qué viviendas o pares de recintos quedan cubiertos y por qué.</p><p>Una planta repetida por sí sola no demuestra esa equivalencia.</p></article>
<article class="cv-card"><h4>Necesita un caso de cálculo adicional</h4><p>Otro muro, losa o encuentro; diferente volumen receptor; otra fachada, ventana o exposición; instalaciones o condiciones de funcionamiento distintas.</p><p>Si faltan los planos o datos, registra el caso como pendiente. No le atribuyas el resultado de A-302.</p></article>
</div>
<div class="cv-note"><strong>No hay un porcentaje de predicciones que reemplace este análisis.</strong> Los porcentajes y mínimos de medición del Anexo A se refieren a la verificación de campo; no se usan para decidir cuántos modelos de SONARA debes construir.</div>
<div class="cv-success"><strong>Tu tarea en este laboratorio:</strong> identifica qué cubren AI-01, IM-01, FA-01 e IN-01; enumera qué situaciones de las otras viviendas siguen pendientes y explica cómo obtendrías evidencia para ellas. No inventes su desempeño.</div>
<p class="cv-small">Fuente: ISO/TS 19488:2021 · Acoustics — Acoustic classification of dwellings. El Anexo A es informativo: ofrece un procedimiento de referencia. La cláusula 6 permite adaptarlo justificadamente a las condiciones del edificio, respetando el requisito general de representación suficiente. Páginas impresas / páginas del visor PDF de esta copia.</p>
</section>
""", unsafe_allow_html=True)
    st.info("Esta información es contexto profesional. Ahora no se pide una campaña de medición ni un número de ensayos. Nuestro trabajo es la predicción y el diseño; después habrá que comprobar la ejecución y el desempeño real.")
    st.markdown("""<section class="c5-coverage"><h5>Entonces, ¿cómo elijo cuántas mediciones hacer?</h5>
<p>Primero completa el inventario de situaciones; después aplica el procedimiento y los mínimos que correspondan al alcance. No hay un número de departamentos que podamos deducir solo de que el edificio tenga 20 viviendas.</p>
<div class="cv-grid">
<article class="cv-card"><h4>Procedimiento A</h4><p>Combina cálculo, inspección y medición. En la fase final, A.2.1 indica seleccionar el <strong>5 % de estructuras y recintos</strong> a medir; normalmente se incluye un recinto grande y uno pequeño.</p><div class="cv-ref">A.2.1 · Procedure A · pp. 11–12 / PDF 17–18.</div></article>
<article class="cv-card"><h4>Procedimiento B</h4><p>Se basa en mediciones del edificio terminado. A.2.2 indica al menos el <strong>10 % de los tipos de construcción de muros separadores y pisos</strong>, con representación suficiente; normalmente un recinto grande y uno pequeño por vivienda seleccionada.</p><div class="cv-ref">A.2.2 · Procedure B · p. 12 / PDF 18.</div></article>
</div>
<div class="cv-note"><strong>Si verificas el edificio completo:</strong> A.2.3 establece un mínimo de <strong>3 mediciones por tipo de estructura y característica acústica</strong>. No son tres mediciones en total ni tres departamentos. Revisa también los porcentajes, la representatividad y si debes ampliar la muestra.</div>
<div class="cv-card"><h4>Ejemplo de conteo, solo para entender la regla</h4><div class="cv-row"><span>Muro tipo M1 · aislamiento aéreo</span><strong>Al menos 3 evaluaciones</strong></div><div class="cv-row"><span>Losa tipo L1 · aislamiento aéreo</span><strong>Al menos 3 evaluaciones</strong></div><div class="cv-row"><span>Losa tipo L1 · impacto</span><strong>Al menos 3 evaluaciones</strong></div><p><strong>Subtotal: 9 evaluaciones para estas tres combinaciones.</strong> Aún faltan fachada, instalaciones y las demás situaciones aplicables; la muestra final puede ser mayor. No significa nueve viviendas distintas.</p><div class="cv-ref">Hipótesis didáctica, no inventario confirmado de Los Alerces.<br>A.2.3 · Verification of an entire building · p. 12 / PDF 18.</div></div>
</section>""", unsafe_allow_html=True)


def _stage1(lab, saved):
    _header(
        1,
        "Expediente del Edificio Los Alerces",
        "Entender el edificio y organizar los casos de predicción para diseñar hacia clase A.",
    )

    st.markdown("### 1 · Conoce el edificio que vas a diseñar")
    st.markdown("Los Alerces es un edificio residencial de **5 pisos, con 4 departamentos por piso: 20 viviendas en total**. La estructura de partida es de muros y losas de hormigón armado. Trabajaremos inicialmente con **A-302, en el tercer piso**, y sus relaciones con A-301, A-402, la fachada norte y el shaft sanitario S-1.")
    st.markdown("#### El edificio y la ubicación de A-302")
    _show_drawing("alerces_edificio_isometrico_v3.jpg", "Vista exterior ilustrativa · cinco pisos. A-302 está en el tercer piso, segunda vivienda desde el oeste; al mirar la fachada norte desde el exterior, aparece segunda desde la derecha.")
    _show_drawing("alerces_colindancias.svg", "Ubicación esquemática de las cuatro viviendas del tercer piso y sus relaciones verticales. Norte arriba; sin escala. La geometría de A-302 se detalla en AC-01.")
    st.markdown("#### Interior de A-302 · acceso y conexiones")
    _show_drawing(
        "alerces_render_acceso_v4.jpg",
        "A-302 · acceso desde el pasillo común y conexiones entre recintos. "
        "La puerta principal P-01 tiene 0,90 m de paso útil; el distribuidor 1,03 m; "
        "las puertas de dormitorios y baño, 0,80 m. Norte al fondo y A-301 al oeste. El cerramiento hacia el pasillo común es opaco, sin ventanas. "
        "Para dimensiones y cálculos utiliza la planta AC-01 revisada de la Etapa 2.",
    )

    st.markdown("**Cómo se recorre A-302:** desde el pasillo común entras por P-01 al distribuidor. Desde allí accedes a cocina, baño, dormitorio principal y estar-comedor. El dormitorio 2 tiene su puerta hacia el estar. La cocina también comunica con el estar mediante un vano abierto.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pisos", PROJECT["storeys"])
    c2.metric("Viviendas", PROJECT["dwellings"])
    c3.metric("Altura interior", f'{PROJECT["floor_height_m"]:.2f} m')
    c4.metric("Caso de estudio", "A-302")
    st.markdown("#### Los cuatro casos que guiarán el laboratorio")
    _lab_table(
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

    st.markdown("#### Recintos de A-302")
    _lab_table(
        pd.DataFrame(
            ROOMS,
            columns=["Recinto", "Área [m²]", "Volumen [m³]", "Orientación", "Adyacencia crítica"],
        ),
        hide_index=True,
        width="stretch",
    )
    st.markdown("#### Soluciones iniciales para revisar y rediseñar")
    _lab_table(
        pd.DataFrame(
            MATERIALS,
            columns=["Código", "Elemento", "Sistema", "Dimensión", "Observación"],
        ),
        hide_index=True,
        width="stretch",
    )
    st.markdown("#### Descarga los antecedentes del proyecto")
    st.caption(
        "Descarga un único archivo CSV con los datos generales del edificio, "
        "recintos y materialidades. Puedes abrirlo en Excel para consultar y "
        "organizar los antecedentes de cálculo."
    )
    _project_downloads()


    st.markdown("### 2 · Tu encargo: diseñar soluciones para clase A")
    st.info(
        "**Encargo de diseño:** desarrolla las soluciones constructivas del Edificio Los Alerces, "
        "de 5 pisos con 4 departamentos por piso (20 viviendas en total), para que el proyecto pueda alcanzar la **clase A, la más exigente**. "
        "Diseña tabiques, muros separadores, ventanas, puertas, losas y sistemas de piso, "
        "junto con sus encuentros, sellos y soluciones para instalaciones. Utiliza **SONARA** "
        "para calcular, comparar alternativas y justificar la solución elegida. Las materialidades "
        "del expediente son una base de partida que debes revisar y rediseñar. "
        "Aplica ISO 12354 para la predicción y contrasta los resultados con los requisitos de "
        "clase A de ISO/TS 19488:2021. Entrega especificaciones, cálculos, evidencias y una "
        "matriz de cumplimiento; identifica lo pendiente para cubrir el edificio completo."
    )

    st.markdown("### 3 · Qué pide la ISO y cómo lo aplicarás")
    _download_standard("c5l1_s1_standard")
    st.caption("Norma: ISO/TS 19488:2021 · Acoustics — Acoustic classification of dwellings. En las referencias se distingue página impresa / página del visor PDF; este archivo tiene seis páginas preliminares.")
    st.markdown("#### Clases y regla de asignación")
    _lab_table(pd.DataFrame([
        ["A → F", "A es la clase más exigente y F la menos exigente. Para obtener una clase deben cumplirse todos sus requisitos aplicables.", "§4 · Acoustic classes · p. 6 / PDF 12"],
        ["NPD", "Sin desempeño requerido o determinado, o desempeño que no cumple F; debe aclararse la situación. No lo conviertas en una letra ni lo promedies.", "§4 · Acoustic classes · p. 6 / PDF 12"],
        ["Clase global", "La clase común queda limitada por la característica de menor clase. Los ejemplos del Anexo A muestran la decisión; no se promedian letras.", "A.4 · Classification examples · pp. 13–14 / PDF 19–20"],
        ["Meta del laboratorio", "Diseñar para A y comprobar cada requisito con resultados propios. La meta no es una clase ya obtenida.", "Aplicación didáctica de §4 y §5 · pp. 6–9 / PDF 12–15"],
    ], columns=["Idea", "Cómo interpretarla", "Referencia: apartado · título · página"]))
    st.markdown("#### Límites de clase A que utilizarás en el diseño")
    st.markdown("Estos son los objetivos de comparación del laboratorio. **≥ significa aislamiento mínimo; ≤ significa nivel o tiempo máximo.** Comprueba el descriptor completo: el mismo valor con otro indicador no representa necesariamente el mismo requisito.")
    _lab_table(pd.DataFrame([
        ["AI-01 · entre viviendas", "DₙT,50 = DₙT,w + C₅₀–₃₁₅₀ ≥ 58 dB", "Estar A-301 → estar A-302. Se compara el desempeño entre recintos, incluidos los flancos, con la fila 1. No el Rw del muro aislado.", "§5.2 · Airborne sound insulation · tabla 1, fila 1 y nota a · p. 7 / PDF 13"],
        ["IM-01 · impacto entre viviendas", "L′ₙT,w ≤ 46 dB Y L′ₙT,50 ≤ 50 dB", "Estar A-402 → estar A-302. Ambos criterios se comprueban para A: impacto convencional y baja frecuencia. Un valor menor representa mejor desempeño.", "§5.3 · Impact sound insulation · tabla 2, fila 1 y nota a · p. 8 / PDF 14"],
        ["FA-01 · fachada y cubierta", "DₙT,A,tr ≥ max(Lden − 20; 30) dB", "El requisito depende de la exposición exterior. 30 dB es el mínimo de la nota b. Usa la adaptación del espectro de la fuente; justifica la correspondencia entre el descriptor normativo y la salida de fachada de SONARA.", "§5.4 · Airborne sound insulation against exterior noise · tabla 3, fila 1 y notas a–b · p. 8 / PDF 14"],
        ["IN-01 · instalaciones intermitentes", "LAFmax,nT ≤ 26 dB(A)", "Para la descarga sanitaria, declarar la operación intermitente/irregular. Máximo con ponderación FAST y normalización a T₀ = 0,5 s; no sustituirlo por LAeq.", "§5.5 · Sound from building service equipment · tabla 4, fila 2 y notas · p. 9 / PDF 15"],
        ["Instalaciones continuas · si corresponden", "LAeq,nT ≤ 22 dB(A)", "Para equipos con ruido continuo y operación declarada. No es una segunda condición temporal que deba inventarse para una descarga intermitente.", "§5.5 · tabla 4, fila 1 · p. 9 / PDF 15"],
        ["Accesos comunes, excepto escaleras", "T ≤ 0,6 s", "Donde sea aplicable. Comprobar cada banda de octava de 500, 1 000 y 2 000 Hz. Se incorpora al ampliar el alcance; los cuatro casos de A-302 no lo calculan.", "§5.6 · Reverberation time and sound absorption in stairwells and access areas · tabla 5, fila 1 y nota a · p. 9 / PDF 15"],
        ["Escaleras comunes", "T ≤ 0,9 s O A ≥ 0,45 × Sfloor", "Alternativas de la tabla 5, por banda de 500, 1 000 y 2 000 Hz. A es el área de absorción equivalente, en m²; Sfloor es la superficie transitable, en m². No confundir A de absorción con clase A.", "§5.6 · tabla 5, fila 2 y notas a–b · p. 9 / PDF 15"],
    ], columns=["Situación", "Requisito de clase A", "Cómo debes aplicarlo", "Referencia"]))
    st.markdown("#### Fachada: convierte la expresión en un objetivo numérico")
    _lab_table(pd.DataFrame([
        ["45 dB", "45 − 20 = 25 dB", "30 dB, por el mínimo normativo"],
        ["55 dB", "55 − 20 = 35 dB", "35 dB"],
        ["65 dB", "65 − 20 = 45 dB", "45 dB"],
    ], columns=["Lden exterior supuesto", "Cálculo", "Aislamiento adaptado mínimo para A"]))
    st.caption("Ejemplos didácticos; no fijan la exposición real de Los Alerces. El alumno debe adoptar y documentar su Lden y obtener el límite correspondiente antes de diseñar la ventana o la fachada.")
    st.markdown("#### Otras situaciones de la norma · contexto, sin cálculos adicionales")
    st.markdown("**Tu entrega mantiene los cuatro casos AI-01, IM-01, FA-01 e IN-01.** La norma también contempla las situaciones siguientes. Se muestran para entender por qué esos cuatro casos no bastan para declarar la clase de todo un edificio; **no debes añadirlas al proyecto de SONARA ni resolverlas en este laboratorio**.")
    _lab_table(pd.DataFrame([
        ["Voces en el pasillo o la escalera común → recinto de una vivienda", "Ruido aéreo: atraviesa el cerramiento que incluye la puerta de entrada. Debe evaluarse el conjunto, no solo la puerta.", "DₙT,A ≥ 46 dB · más aislamiento es mejor", "§5.2 · Airborne sound insulation · tabla 1, fila 2 · p. 7 / PDF 13"],
        ["Actividad ruidosa en un local → recinto de una vivienda", "Ruido aéreo, por ejemplo música. Además del aislamiento, hay que estimar el ruido de la actividad concreta. El ejemplo no implica que Los Alerces tenga ese local.", "DₙT,50 ≥ 64 dB · más aislamiento es mejor", "§5.2 · Airborne sound insulation · tabla 1, fila 3 · p. 7 / PDF 13"],
        ["Pisadas en zonas comunes o en balcones, terrazas y baños de otra vivienda → recinto receptor", "Ruido de impacto: el golpe se transmite por la estructura. No es el ruido de voces del primer caso. Revisar las exclusiones de la nota b para espacios menores de 4 m².", "L′ₙT,w ≤ 50 dB · menos ruido recibido es mejor", "§5.3 · Impact sound insulation · tabla 2, fila 2 y nota b · p. 8 / PDF 14"],
        ["Golpes o impactos de una actividad ruidosa en un local → recinto de una vivienda", "Ruido de impacto transmitido por la estructura. Es una situación distinta del ruido aéreo de ese mismo local; deben cumplirse ambos límites de impacto indicados.", "L′ₙT,w ≤ 40 dB Y L′ₙT,50 ≤ 44 dB · menos ruido recibido es mejor", "§5.3 · Impact sound insulation · tabla 2, fila 3 y notas a/c · p. 8 / PDF 14"],
    ], columns=["De dónde viene el ruido y a dónde llega", "Qué significa en la práctica", "Requisito de clase A", "Referencia · ISO/TS 19488:2021"]))
    st.caption("Cómo leerla: la flecha indica fuente → receptor. En aislamiento aéreo se exige un mínimo (≥); en impacto se limita el nivel recibido (≤). Estos valores corresponden a situaciones distintas: no sustituyen los objetivos de AI-01 ni de IM-01.")
    st.info("**Notas de interpretación:** tabla 1, nota a: si se emplea DₙT,A en lugar de DₙT,50, el límite aumenta 2 dB (AI-01: ≥ 60 dB); si se emplea DₙT,w en lugar de DₙT,A, se añaden otros 2 dB (≥ 62 dB). Documenta la vía elegida, no intercambies cifras sin cambiar el descriptor. Tabla 4 permite máximo SLOW con límite 4 dB más estricto que FAST (clase A: LASmax,nT ≤ 22 dB(A)). No conviertas un resultado FAST en SLOW restándole 4 dB: cambia el límite, no el resultado.")
    st.markdown("**Tu trabajo con estos límites:** selecciona la relación aplicable, registra el descriptor y criterio completos en la actividad, declara los datos que condicionan el valor y luego calcula y rediseña en SONARA. El objetivo está dado; tu tarea es demostrar cómo lo aplicas y qué solución permite cumplirlo.")
    st.info("**Aplicación a Los Alerces:** los cuatro casos de A-302 permiten comenzar el diseño. Para concluir sobre el edificio se deben cubrir también las demás viviendas, tipologías y situaciones aplicables. La cláusula 4 excluye de esta clasificación el aislamiento entre recintos interiores de una misma vivienda; esos tabiques pueden diseñarse como prestación adicional, pero no deben confundirse con el separador entre viviendas.")

    st.markdown("### 4 · Qué podrás concluir a partir de las predicciones")
    st.markdown("La **cláusula 6 y el Anexo A.2.1** contemplan cálculos de predicción como parte de la verificación. El procedimiento A integra tres fases: el cálculo permite anticipar el desempeño, la inspección comprueba cómo se construyó y la medición verifica el resultado terminado. **En este laboratorio desarrollamos la primera fase:** diseñar para clase A mediante SONARA y preparar las comprobaciones posteriores.")
    _lab_table(pd.DataFrame([
        ["Diseño · lo que hacemos ahora", "Proyecto de SONARA: recintos, elementos, capas, encuentros, base y rediseño; predicciones según la parte aplicable de ISO/EN 12354.", "Comprobar viabilidad de clase A, especificar soluciones y localizar riesgos. Resultado: desempeño previsto."],
        ["Construcción · lo que se debe planificar", "Inspecciones de materiales, juntas, bandas resilientes, fijaciones, encuentros y ejecución respecto de planos aprobados.", "Comprobar que la solución calculada se ejecutó correctamente."],
        ["Edificio terminado · lo que falta verificar", "Ensayos de aislamiento aéreo, impacto y fachada; mediciones de instalaciones y reverberación cuando correspondan.", "Contrastar el desempeño real y sustentar la clasificación dentro del alcance verificado."],
    ], columns=["Fase", "Evidencia", "Para qué sirve"]))
    st.markdown("**Diseñar con margen:** A.2.1 aconseja al menos media clase (2 dB) cuando la experiencia práctica respalda ese margen; pueden necesitarse márgenes mayores en soluciones sensibles a la ejecución. No es una garantía universal: justifica el margen por característica, incertidumbre y sistema. Para aislamiento se busca superar el mínimo; para impacto e instalaciones, quedar por debajo del máximo.")
    st.warning("**Qué podrás concluir:** propuesta de diseño orientada a clase A y resultados previstos de los casos calculados. La verificación completa del procedimiento A requiere también inspecciones y mediciones finales. El estado de cumplimiento mostrado por SONARA no sustituye la revisión de todos los descriptores, requisitos adicionales, situaciones y evidencias de la clasificación.")
    st.caption("Fuente: ISO/TS 19488:2021, cláusula 6 (pp. 9–10) y Anexo A informativo, A.1–A.2.3 (pp. 11–12; páginas 17–18 del PDF). Las tablas anteriores son una síntesis didáctica; consultar el documento para las condiciones de conformidad, tolerancias y métodos completos.")


    st.markdown("#### Alcance del ejercicio · definido por el docente")
    st.info(EXERCISE_SCOPE)
    _lab_table(pd.DataFrame([
        ["Proyecto y meta", "Los Alerces: 5 pisos, 20 viviendas. Meta de diseño: clase A."],
        ["Unidad de trabajo", "A-302 y sus relaciones con A-301, A-402, exterior norte y shaft S-1."],
        ["Casos obligatorios", "AI-01, IM-01, FA-01 e IN-01; base y rediseño, criterios A, entradas, curvas e indicadores."],
        ["Producto del alumno", "Especificaciones constructivas, evidencia de cálculo y comparación con los límites de clase A por caso."],
        ["Conclusión permitida", "Desempeño previsto de las cuatro situaciones. Justificar si alcanzan A o qué brecha queda."],
        ["Fuera de los cálculos obligatorios", "Otras viviendas, otras fachadas y pares de recintos, accesos y escaleras. Su cobertura se comenta; no se inventan datos ni se exige campaña de medición."],
    ], columns=["Decisión del encargo", "Definición para todos los estudiantes"]))
    st.markdown("**¿Qué decide el alumno?** Las soluciones constructivas y su justificación: capas, materiales, espesores, encuentros, tratamientos y alternativas. El objetivo A y los cuatro casos los fija el encargo; el alumno no elige otro edificio ni un alcance diferente.")
    st.caption("Contexto normativo: §4 · Acoustic classes · p. 6 / PDF 12 permite declarar características, viviendas o edificios completos; A.3 · Contents of verification report for classification of a dwelling or a building · p. 13 / PDF 19 exige precisar la conclusión y su evidencia. Esa flexibilidad de la norma no cambia el alcance docente fijado aquí.")
    st.markdown("#### Ejemplo didáctico: tres tipologías dentro de un condominio")
    _lab_table(pd.DataFrame([
        ["T1 · departamentos interiores", "Aéreo A · impacto A · fachada A · instalaciones A · comunes A", "A"],
        ["T2 · departamentos frente a avenida", "Aéreo A · impacto A · fachada B · instalaciones A · comunes A", "B, limitada por fachada"],
        ["T3 · viviendas próximas a equipos", "Aéreo A · impacto A · fachada A · instalaciones C · comunes según aplicabilidad", "C, limitada por instalaciones"],
    ], columns=["Grupo supuesto", "Clases de características supuestas", "Clase común del grupo si toda la evidencia lo respalda"]))
    st.markdown("**Lectura del ejemplo:** no corresponde anunciar clase A para todo el conjunto mientras existan situaciones B o C. Si estas tipologías pertenecen a un mismo edificio y la verificación cubre todas las viviendas y requisitos, su clase global queda limitada a C. Si están en edificios distintos, informa la clase de cada edificio. Una eventual declaración común del condominio necesita un alcance explícito y evidencia de todas sus partes; no surge de promediar A, B y C. Para cumplir el encargo de clase A hay que rediseñar la fachada de T2 y las instalaciones de T3, y volver a comprobar todos los requisitos.")
    st.caption("Ejemplo hipotético creado para explicar la regla de §4 y A.4; no corresponde a resultados medidos ni a un inventario confirmado de Los Alerces. Una tipología arquitectónica repetida puede requerir más de un grupo acústico por sus encuentros, exposición o instalaciones.")
    st.caption("Regla de informe: A.3 · Contents of verification report for classification of a dwelling or a building · p. 13 / PDF 19: si varían las clases entre viviendas, recintos o características, la asignación considera la clase mínima de lo pertinente; pueden declararse además clases superiores de unidades individuales y tablas de resultados.")
    _coverage_explanation()

    st.markdown("### 5 · Cómo trabajarás en Proyecto de SONARA")
    st.markdown(
        "**SONARA** es la aplicación de cálculo que utilizarás durante el laboratorio. "
        "En ella construirás las soluciones por capas, definirás materiales y espesores, "
        "revisarás curvas por frecuencia y compararás el desempeño de distintas alternativas. "
        "Trabajarás desde Proyecto con recintos, elementos, soluciones guardadas e informe; sus herramientas de diseño incluyen ruido aéreo, transmisión entre recintos, impacto, fachada e instalaciones."
    )
    st.markdown(
        "**Cómo trabajaremos:** abre SONARA → Proyecto y crea el proyecto Los Alerces. Registra los recintos y los elementos a diseñar; desde Diseñar, modela la solución inicial y guarda su configuración "
        "y resultados, diseña una alternativa y vuelve a calcular. Traslada manualmente al "
        "laboratorio los indicadores y las evidencias. Contrasta cada resultado con clase A "
        "y rediseña hasta cumplir o documentar con precisión la brecha pendiente. SONARA "
        "calcula el desempeño; tú justificas la clasificación."
    )
    st.markdown(
        "**Tu entrega:** cuadro de tabiques, muros, puertas, ventanas y losas con capas, "
        "espesores, materiales, uniones y sellos; comparación inicial/diseño; curvas e "
        "indicadores; requisitos de clase A y comprobación por situación. Incluye puertas "
        "y otros elementos donde correspondan, ampliando el inventario de situaciones del edificio."
    )
    _sonara_button("Conocer SONARA y comenzar el diseño")


    st.markdown(
        '<div class="section-band"><span>✍️</span>'
        '<h3>6 · Tu actividad: diagnóstico y plan de predicciones</h3></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "El diagnóstico del A-302 se utilizará como base en las siguientes etapas. "
        "El plan de predicciones identifica los casos de diseño y su cobertura en el edificio; "
        "en este laboratorio no se realizan mediciones en terreno."
    )
    st.markdown(
        '<div style="padding:14px 18px;border:1px solid #cfe0ef;border-radius:14px;'
        'background:linear-gradient(135deg,#f7fbff,#eaf5fc);margin:10px 0 15px">'
        '<strong style="color:#125779">TU ENCARGO PROFESIONAL</strong><br>'
        '<span style="color:#345569">Diagnostica el A-302, prepara el plan '
        'de diseño y organiza los casos que calcularás en SONARA y los que quedan pendientes.</span>'
        '</div>', unsafe_allow_html=True,
    )
    with st.form("c5l1_stage1_diagnostic_form", border=True):
        st.markdown("#### 1 · Identifica qué debes resolver en A-302")
        answer = st.text_area(
            "Diagnostica las cuatro situaciones acústicas del departamento A-302",
            value=saved.get("c5l1_s1_answer", ""),
            placeholder="AI-01: A-301 → A-302, muro y flancos. IM-01: A-402 → A-302, losa y piso. FA-01: exterior → estar A-302, fachada y ventana. IN-01: descarga sanitaria → dormitorio A-302, cierre y fijaciones. Explica el mecanismo y el riesgo que debes resolver en cada caso.",
            height=160,
        )
        procedure = saved.get("c5l1_s1_procedure", "A · fase de predicción de diseño")
        st.info("Trabajamos en la fase de diseño: prepara los modelos y calcula en Proyecto de SONARA. Las inspecciones y mediciones pertenecen a la verificación futura; no tienes que elegir un procedimiento ni diseñar una campaña de ensayos aquí.")
        st.markdown("#### 2 · Identifica los requisitos de clase A antes de diseñar")
        st.markdown("Usa los límites detallados en esta etapa y contrasta la fila y notas del PDF con cada relación fuente–receptor. Registra el descriptor exacto, el límite de A (o su expresión), el sentido de comparación y las condiciones aplicables. Estos serán tus objetivos de diseño en SONARA; no uses Rw como sustituto automático de un requisito entre recintos.")
        st.caption("ISO/TS 19488:2021 · Acoustics — Acoustic classification of dwellings: §5.2 / tabla 1, p. 7 (PDF 13); §5.3 / tabla 2, pp. 7–8 (PDF 13–14); §5.4 / tabla 3, p. 8 (PDF 14); §5.5 / tabla 4, p. 9 (PDF 15).")
        st.info("Para fachada, declara la exposición exterior que exige la expresión elegida y comprueba sus mínimos/notas. Para A, revisa todos los requisitos adicionales de baja frecuencia aplicables. Para instalaciones, distingue la condición de operación y el descriptor temporal. Si falta un antecedente, identifica el dato pendiente y cómo lo obtendrás.")
        requirements = {}
        previous_requirements = saved.get("c5l1_s1_requirements", {})
        for family, case in CALCULATION_CASES.items():
            code = case["code"]
            prior = previous_requirements.get(code, {})
            st.markdown(f"**{code} · {family} · objetivo clase A**")
            requirements[code] = {
                "descriptor": st.text_input("Descriptor requerido", value=prior.get("descriptor", ""), key=f"c5l1_req_descriptor_{code}", placeholder="Magnitud exacta de la fila y notas aplicables"),
                "limit": st.text_input("Límite de clase A y sentido de comparación", value=prior.get("limit", ""), key=f"c5l1_req_limit_{code}", placeholder="≥ mínimo / ≤ máximo; valor, unidad o expresión completa"),
                "conditions": st.text_area("Condiciones y requisitos adicionales", value=prior.get("conditions", ""), key=f"c5l1_req_conditions_{code}", placeholder="Fila/situación, términos espectrales, baja frecuencia, exposición o funcionamiento y datos pendientes."),
                "reference": st.text_input("Tabla, fila, nota y página consultadas", value=prior.get("reference", ""), key=f"c5l1_req_reference_{code}", placeholder="ISO/TS 19488:2021 · tabla … · fila … · nota … · p. …"),
            }
        st.markdown("#### 3 · Organiza el diseño en Proyecto de SONARA")
        sample = st.text_area(
            "Organiza tus casos de predicción y su cobertura en el edificio",
            value=saved.get("c5l1_s1_sampling", ""),
            placeholder=(
                "Para AI-01, IM-01, FA-01 e IN-01 indica emisor, receptor, elemento, entradas y descriptor; "
                "describe la base y el rediseño. Explica qué otras situaciones necesitan un modelo adicional "
                "y qué datos faltan. No propongas cantidades de mediciones en este ejercicio."
            ),
            height=180,
        )
        st.markdown("#### 4 · Explica qué cubre tu propuesta y qué falta")
        scope = st.text_area(
            "Explica los límites del alcance fijado por el docente",
            value=saved.get("c5l1_s1_scope", ""),
            placeholder=(
                "Sin cambiar el alcance: explica por qué estos cuatro casos no acreditan por sí solos la clase global y qué antecedentes serían necesarios para extender el estudio."
            ),
            height=130,
        )
        submitted = st.form_submit_button("Guardar diagnóstico y plan de predicciones", width="stretch")
    if submitted:
        incomplete_requirements = [code for code, row in requirements.items() if any(not str(value).strip() for value in row.values())]
        if incomplete_requirements:
            st.warning("Completa los requisitos de clase A (descriptor, límite, condiciones y referencia) para: " + ", ".join(incomplete_requirements))
        elif len(answer.strip()) < 120 or len(sample.strip()) < 160 or len(scope.strip()) < 90:
            st.warning(
                "Completa el diagnóstico (mín. 120 caracteres), el plan de predicciones "
                "(mín. 160) y el alcance (mín. 90)."
            )
        else:
            _save(
                lab, saved, 1,
                c5l1_exercise_scope=EXERCISE_SCOPE,
                c5l1_s1_requirements=requirements,
                c5l1_s1_answer=answer,
                c5l1_s1_procedure=procedure,
                c5l1_s1_sampling=sample,
                c5l1_s1_scope=scope,
            )
            st.success(
                "Diagnóstico y plan de predicciones guardados. Los cálculos posteriores "
                "seguirán usando A-302 como unidad didáctica."
            )


def _stage2(lab, saved):
    _header(2, "Lectura acústica de planos y detalles", "Obtener del plano los datos que se usarán en SONARA y reconocer los caminos críticos.")
    _project_badge()
    st.markdown(
        "Las cuatro láminas tienen presentación de plano técnico, cotas y detalles de partida. "
        "**Se muestran como imágenes PNG de alta resolución; el juego PDF permite ampliar e imprimir en A3.** "
        "Usa las cotas del proyecto como datos geométricos; las materialidades iniciales pueden rediseñarse para alcanzar clase A."
    )
    _download_plan_set("c5l1_s2_plans_pdf")
    tabs = st.tabs(["AC-01 · Planta", "AC-02 · Corte", "AC-03 · Fachada", "AC-04 · Detalles"])
    sheets = [
        ("planta_tipo.png", "AC-01 · Planta parcial nivel 3 · norte arriba · A-302 y estar adyacente A-301", "Sigue el acceso P-01 desde el pasillo común y comprueba las conexiones con cocina, baño, dormitorio principal y estar; desde el estar se entra al dormitorio 2. Localiza M-01, V-01, V-02 y S-1. El estar en L conserva 20,40 m² y el medianero útil 4,08 × 2,50 m."),
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
    _lab_table(pd.DataFrame(matrix, columns=["Caso", "Fuente / receptor", "Elemento", "Geometría útil", "Datos de partida", "Vías"]), hide_index=True, width="stretch")
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
    _lab_table(
        pd.DataFrame([
            ["Aéreo", "Separaciones y encuentros representativos evaluados", "C"],
            ["Impacto", "Tipos de entrepiso y transmisiones relevantes evaluados", "D"],
            ["Exterior", "Recintos y fachadas con sus exposiciones evaluados", "C"],
            ["Instalaciones", "Fuentes y condiciones de funcionamiento evaluadas", "C"],
            ["Accesos / escaleras", "Reverberación o absorción aplicable evaluada", "B"],
        ], columns=["Característica del edificio", "Cobertura supuesta", "Clase sustentada"]),
        hide_index=True, width="stretch",
    )
    st.markdown("#### Por qué la clase global es D, paso a paso")
    st.markdown(
        "Las clases están ordenadas por exigencia: **A → B → C → D → E → F**. "
        "En este ejemplo, una característica que alcanza C también satisface los criterios "
        "menos exigentes de D; una que alcanza B satisface C y D. Esto no significa "
        "que su clase individual cambie: conserva B o C en el informe."
    )
    _lab_table(
        pd.DataFrame([
            ["Aéreo", "C", "Sí", "Sí"],
            ["Impacto", "D", "No", "Sí"],
            ["Exterior / fachada", "C", "Sí", "Sí"],
            ["Instalaciones", "C", "Sí", "Sí"],
            ["Accesos / escaleras", "B", "Sí", "Sí"],
            ["Conjunto del edificio", "Clase que TODOS pueden cumplir", "NO", "SÍ"],
        ], columns=["Característica", "Clase individual", "¿Cumple al menos C?", "¿Cumple al menos D?"]),
        hide_index=True, width="stretch",
    )
    st.markdown(
        "**Prueba de C:** falla porque impacto solo alcanza D. No puedes declarar C "
        "para todo el edificio aunque los otros cuatro ítems cumplan C o mejor. "
        "**Prueba de D:** los cinco ítems cumplen D o mejor; por eso D es la clase "
        "más exigente que todos pueden cumplir simultáneamente. E y F también serían "
        "menos exigentes, pero no describen la mejor clase común sustentada."
    )
    st.info(
        "Regla de decisión: busca la clase más exigente cuyos requisitos se cumplen "
        "en TODAS las características y situaciones aplicables verificadas. No conviertas "
        "las letras a números para promediarlas ni elijas la clase más frecuente."
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
    _show_class_a_requirements(saved)
    _download_standard("c5l1_stage3_iso19488_pdf")
    st.markdown("**Secuencia:** resultado acústico → descriptor correcto → límite aplicable → clase por característica → conclusión con alcance.")
    tabs = st.tabs(["Clases y criterios", "Ejemplo resuelto · A-302", "Edificio completo", "Tu objetivo y alcance"])
    with tabs[0]:
        st.markdown("### Seis clases y una declaración de desempeño")
        st.markdown("**A es la clase más exigente; F la menos exigente del esquema.** NPD se utiliza cuando el desempeño no está determinado, no se requiere o queda fuera de las clases. No es una séptima clase ni una nota cero.")
        _lab_table(pd.DataFrame([
            ["A → B → C → D → E → F", "De mayor a menor exigencia acústica"],
            ["Clase por característica", "Aéreo, impacto, exterior, instalaciones o zonas de acceso"],
            ["Clase de vivienda", "Requiere todos los criterios aplicables al alcance de esa vivienda"],
            ["Clase de edificio", "Requiere alcance y verificación del edificio; no se extrapola A-302"],
        ], columns=["Concepto", "Interpretación"]), hide_index=True, width="stretch")
        _lab_table(pd.DataFrame([
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
        _lab_table(pd.DataFrame([
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
        st.markdown("### Objetivo del encargo: clase A")
        options = ["Clase A"]
        previous = saved.get("c5l1_s3_target", options[0])
        with st.form("c5l1_s3_scope_form"):
            target = st.selectbox("Clase objetivo de diseño (no es clase obtenida)", options, index=options.index(previous) if previous in options else 0)
            scope = EXERCISE_SCOPE
            st.markdown("**Alcance obligatorio del encargo:** " + scope)
            reason = st.text_area("Por qué no basta promediar las clases ni evaluar un único muro", value=saved.get("c5l1_s3_reason", ""), height=110)
            submitted = st.form_submit_button("Guardar objetivo y alcance", width="stretch")
        if submitted:
            if len(reason.strip()) < 80:
                st.warning("El alcance y la meta A ya están fijados. Explica la regla de clase limitante con al menos 80 caracteres.")
            else:
                _save(lab, saved, 3, c5l1_s3_target=target, c5l1_s3_scope=scope, c5l1_s3_reason=reason)
                st.success("Objetivo guardado. Ahora prepara las entradas en la etapa 4; todavía no has obtenido una clase.")


def _stage4(lab, saved):
    _header(4, "Preparar el proyecto en SONARA", "Convertir el objetivo y los planos en entradas trazables antes de calcular.")
    _show_class_a_requirements(saved)
    st.info(f"**Meta obligatoria: Clase A. Objetivo registrado:** {saved.get('c5l1_s3_target', 'Pendiente de definir')}.")
    st.markdown("### Crear y organizar el proyecto en SONARA")
    st.markdown("""1. Entra a **Proyecto → Proyecto**, escribe **Los Alerces · tu nombre** y pulsa **Crear / actualizar proyecto**.
2. En **Recintos**, registra los emisores y receptores de los planos: estar A-301, estar A-302, estar A-402 y dormitorio A-302; identifica nivel, uso, área y volumen. Añade exterior y los recintos de instalaciones cuando corresponda, sin inventar geometría faltante.
3. En **Elementos**, selecciona emisor, receptor y tipo de elemento. Añade los casos AI-01, IM-01, FA-01 e IN-01, además de tabiques, ventanas y puertas que correspondan al alcance. Pulsa **Agregar elemento a la matriz** o **Diseñar este elemento**.
4. En **Diseñar**, comprueba **Elemento activo a diseñar** y elige la herramienta en **Calculadora del requerimiento**. Realiza allí los cálculos del laboratorio.
5. Guarda la base y el rediseño, identificados por caso. Comprueba ambos en **Soluciones** y prepara la documentación desde **Informe**.
6. Registra en este laboratorio los indicadores, referencias y evidencias; el traslado desde SONARA es manual.""")
    st.info("**Requisitos de clase A:** contrasta el descriptor y el valor del requerimiento disponible en el catálogo con ISO/TS 19488:2021. La selección de una referencia o el estado de cumplimiento de SONARA no acredita por sí solo clase A. Si el catálogo no ofrece el requisito exacto, documenta la diferencia y comprueba el umbral y los requisitos adicionales en tu matriz del laboratorio.")
    with st.expander("Recuperar lectura de planos y alcance"):
        st.markdown(saved.get("c5l1_s2_geometry", "Sin comprobación geométrica guardada."))
        st.markdown(saved.get("c5l1_s2_findings", "Sin riesgos guardados."))
        st.markdown(saved.get("c5l1_s3_scope", "Sin alcance guardado."))
    _lab_table(pd.DataFrame([
        ["M-01 / AI-01", "HA 180 mm; S 10,20 m²; V 51,0 m³", "Proyecto → Diseñar → ISO 12354-1", "DₙT,w y adaptaciones finales"],
        ["L-01 / IM-01", "Losa 160; resiliente 10; sobrelosa 40; terminación 10 mm", "Proyecto → Diseñar → Ruido de impacto", "L′ₙT,w y adaptación aplicable"],
        ["F-01 + V-01 / FA-01", "10,50 m² opacos + 4,80 m² de ventana", "Proyecto → Diseñar → Fachada ISO 12354-3", "Aislamiento de fachada adaptado"],
        ["S-01 / IN-01", "2 RF 12,5 / cámara 70 / 2 RF 12,5 mm; V 28,8 m³", "Proyecto → Diseñar → Instalaciones EN 12354-5", "LAeq,nT / LAFmax,nT según operación"],
    ], columns=["Caso", "Datos del expediente", "Ruta SONARA", "Resultado a registrar"]), hide_index=True, width="stretch")
    st.markdown("### Tu secuencia de trabajo")
    st.markdown("""1. Identifica la fila normativa, el descriptor y todos los requisitos de clase A para cada caso.
2. Prepara la solución base y registra sus resultados.
3. Identifica el camino dominante y modifica una variable.
4. Recalcula conservando el resto de condiciones.
5. Compara con clase A, rediseña si falta desempeño y guarda la solución final y las brechas pendientes.
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
    _lab_table(result_df, hide_index=True, width="stretch")
    st.markdown("### Indicadores para la comparación normativa")
    ai = saved.get("c5l1_result_AI-01", {})
    fa = saved.get("c5l1_result_FA-01", {})
    dnta = ai["dntw"] + ai["c"] if ai.get("dntw") is not None and ai.get("c") is not None else None
    facade_adapted = fa["d2mntw"] + fa["ctr"] if fa.get("d2mntw") is not None and fa.get("ctr") is not None else None
    _lab_table(pd.DataFrame([
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
    _lab_table(
        pd.DataFrame(decisions, columns=["Caso", "Objetivo", "Base", "Cambio y efecto", "Evidencias"]),
        hide_index=True, width="stretch",
    )
    st.download_button(
        "Descargar expediente de diseño SONARA (JSON)",
        data=json.dumps(
            {
                "project": PROJECT,
                "target": saved.get("c5l1_s3_target"),
                "scope": EXERCISE_SCOPE,
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
    st.info("**Revisión de la meta clase A:** compara cada característica con A. Si obtienes otra clase, documenta la brecha y el rediseño necesario; no declares alcanzada la meta. Incluye el cuadro de soluciones de tabiques, muros, ventanas, puertas, losas y encuentros, y las situaciones pendientes del edificio.")
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
            "Explica por qué la conclusión no se extiende automáticamente a todo Los Alerces",
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
    result = _STAGES[stage](lab, saved)
    _teacher_guide(stage)
    return result



