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
    ["Dormitorio 2", 9.2, 23.0, "Sur · sin ventana", "Muro opaco hacia pasillo común"],
    ["Cocina", 7.8, 19.5, "Interior", "Distribuidor y estar-comedor"],
    ["Baño principal", 4.1, 10.3, "Interior", "Shaft S-1"],
]

SOURCE_ROOMS = [
    ["Estar A-301", 20.4, 51.0, "Piso 3 · oeste de A-302", "AI-01 · hipótesis académica; altura libre 2,50 m"],
    ["Estar A-402", 20.4, 51.0, "Piso 4 · sobre A-302", "IM-01 · repetición académica del estar A-302; altura libre 2,50 m"],
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
        ("Orientación y continuidad", "AC-01: norte arriba y A-301 al oeste. AC-03: vista desde exterior norte, oeste a derecha; A-302 en tercer piso, segunda vivienda desde derecha. A-402 encima. Acceso sur y muro sin ventanas al pasillo. Balcones esquemáticos: no deducir correcciones del render."),
        ("Criterio de revisión", "Revisar operaciones con unidades, tres riesgos vinculados a lámina y caso, y datos pendientes con magnitud y fuente prevista. Guardar conserva respuestas, no certifica corrección. No exigir mediciones ni clase obtenida en esta etapa."),
        ("Operaciones esperadas", "M-01: 4,08 × 2,50 = 10,20 m². Estar: 20,40 × 2,50 = 51,0 m³. FA-01: 15,30 − 4,80 = 10,50 m² opacos; ventana 4,80 m². V-02 pertenece al dormitorio."),
        ("Tres riesgos razonados", "Ejemplos aceptables: continuidad rígida en encuentros → flancos; puente perimetral del piso flotante → transmisión de impacto; juntas de ventana o shaft sin sellar → fuga aérea; fijaciones sanitarias rígidas → vía estructural. Cada riesgo debe relacionar elemento, mecanismo y medida."),
        ("Datos faltantes", "TR, densidades documentadas, rigidez dinámica o ficha ΔL, datos espectrales sanitarios, uniones y exposición exterior: explicar fuente de obtención y efecto en el modelo."),
    ], "No sumar sobrelosa a los 160 mm de losa estructural ni deducir rigidez o potencia sonora a partir del dibujo."),
    3: ("Interpretación y decisión de diseño", [
        ("Elección esperada", "Elegir la variante de 59 dB: supera el objetivo DₙT,50 ≥ 58 dB. La solución inicial de 55 dB queda 3 dB por debajo. No son resultados reales de SONARA."),
        ("Margen y mejora", "Variante: margen +1 dB respecto del mínimo. Mejora entre propuestas: 4 dB. Distinguir margen, mejora y objetivo; no confundir 4 dB con una prestación ensayada del revestimiento."),
        ("Condiciones que debe revisar", "Mismo descriptor, emisor/receptor, flancos, normalización, bandas e hipótesis. El Rw del muro no sustituye DₙT,50. Un margen pequeño requiere revisar incertidumbre y sensibilidad."),
        ("Alcance de la decisión", "El resultado solo permite hablar del objetivo de AI-01 bajo las hipótesis del ejemplo. Los otros tres casos necesitan sus propios cálculos y comprobaciones. No exigir repetir la clasificación global de la Etapa 1."),
        ("Criterio formativo", "Logrado si justifica elección, margen, condiciones y pendientes. Parcial si omite un punto; por corregir si compara descriptores distintos o declara clase global a partir de AI-01."),
    ], "No aceptar el ejemplo como resultado propio. No cambiar el objetivo del laboratorio a C; la meta sigue siendo A."),
    4: ("Preparación del proyecto y entradas", {
        "A · Introduce los datos de partida": [
            ("Ejemplo docente · TR de los receptores", "Estar 0,60 s y dormitorio 0,50 s. Son hipótesis para una condición interior definida, no mediciones ni valores obligatorios. El alumno puede buscar un informe de reverberación del recinto o estimar el TR con el volumen de la ficha y la absorción de materiales y mobiliario. Registrar condición de ocupación, fuente y método."),
            ("Ejemplo docente · hormigón armado", "2.400 kg/m³ como densidad nominal adoptada para el ejercicio. Buscar la especificación estructural o ficha de la mezcla y registrar el documento o, si no existe, identificar el valor como hipótesis."),
            ("Ejemplo docente · piso flotante", "Si se usa un sistema ensayado de catálogo, dejar vacías densidad de sobrelosa y s′ y citar la ficha de ΔL del conjunto, verificando el montaje. Si se usa el modelo físico, obtener la densidad en la ficha del mortero de sobrelosa y s′, en MN/m³, en la ficha o ensayo de la capa resiliente exacta. No deducir s′ del espesor de 10 mm ni copiar la densidad del hormigón estructural."),
            ("Ejemplo docente · exposición de fachada", "60 dB Lden como hipótesis didáctica para la fachada norte. El objetivo FA-01 resulta en max(60 − 20; 30) = 40 dB. Buscar en un mapa estratégico de ruido o estudio acústico que informe Lden: anotar ubicación representativa, año y fuente. El caso ficticio no tiene un valor medido asignado; no sustituirlo directamente por un LAeq de corta duración."),
        ],
        "B · Explica de dónde salen los datos": [
            ("Trazabilidad", "Revisar TR del estar/dormitorio, densidad HA, exposición exterior y procedencia de cada dato. Distinguir ficha, hipótesis académica y antecedente pendiente; no imponer un TR o densidad únicos sin fuente."),
            ("Revisión del formulario", "Comprobar fuentes y unidades de TR, densidad HA y Lden. Si utiliza s′, necesita densidad de sobrelosa. Si usa catálogo, justificar compatibilidad. Guardar no demuestra que ya estén completos los espectros y las transferencias de instalaciones."),
            ("Piso", "Si usa modelo físico: masa superficial de sobrelosa = densidad × 0,040 m y s′ documentada. Si usa catálogo medido, justificar compatibilidad del montaje y por qué s′ no se usa."),
            ("Objetivos ya fijados", "No exigir que el alumno redefina los límites A: los muestra el encargo. En fachada, revisar Lden y max(Lden − 20; 30). Exigir ambos indicadores de impacto y máximo FAST para la descarga intermitente."),
        ],
        "C · Organiza tus cálculos y evidencias": [
            ("Flujo de proyecto", "Revisar el proyecto Los Alerces con sus recintos y matriz de elementos. En esta etapa basta preparar entradas y protocolo; base, rediseño y evidencias se desarrollan en las etapas 5–8. Contrastar el requisito del catálogo con la meta clase A."),
            ("Criterios y protocolo", "Para cada caso: descriptor, límite, sentido de comparación, tabla/nota y objetivo. Exigir nombres Base/Variante, capturas/curvas y condiciones constantes para comparar."),
        ],
    }, "Los valores iniciales de SONARA no constituyen antecedentes del proyecto. Revisar coherencia de unidades y fuentes antes de aprobar el protocolo."),
    5: ("AI-01 · Aéreo interior", [
        ("Modelo esperado", "M-01 de HA 180 mm; S = 10,20 m², V receptor = 51,0 m³ y TR declarado. Revisar caminos directo y laterales, uniones y su trazabilidad."),
        ("Resultado y mejora", "Exigir DₙT,w y adaptaciones de la curva final entre recintos. Para DₙT,A comprobar DₙT,w + C. Comparar base y variante con igual geometría e identificar el camino dominante; mayor aislamiento es mejor."),
    ], "Rw del muro no sustituye DₙT,w. No trasladar automáticamente C/Ctr del elemento a la curva entre recintos; declarar la reconstrucción aproximada por Rw."),
    6: ("IM-01 · Impacto", [
        ("Caso base guardado en SONARA", "Los Alerces · Marco Araos · Docente → Soluciones → Estar A-402 → Estar-comedor A-302 · Paramento horizontal. Solución «IM-01 · L-01 · Base preliminar · losa desnuda sin flancos»."),
        ("Entradas de la corrida docente", "Ruido de impacto → ISO 12354-2 → Calcular por masa superficial. Losa de hormigón armado de 160 mm, densidad adoptada de 2.400 kg/m³ y masa superficial de 384 kg/m². Área del entrepiso de 20,40 m², volumen receptor de 51,0 m³ y TR receptor adoptado de 0,60 s. Selecciona Modelo genérico / físico → Sin revestimiento, Sin cielo y desactiva Incluir flanqueos de impacto. Esta base preliminar representa la transmisión directa."),
        ("Resultados y metas", "Lₙ,0,w estimado: 73,5 dB. Resultado entre recintos L′ₙT,w: 76 dB (30 dB sobre la meta de 46 dB). L′ₙT,50 proyectado: 76 dB (26 dB sobre la meta de 50 dB). CI mostrado: −4 dB. Para baja frecuencia usa L′ₙT,50 proyectado, que incorpora la adaptación de 50–2.500 Hz. La base no cumple ambas metas."),
        ("Base docente con flancos guardada en SONARA", "Busca «IM-01 · L-01 · Base preliminar con flancos M-01 y F-01». Conserva las entradas de la corrida directa y activa dos encuentros. Para ambos, R emisor = 44 dB y m′ emisor = 384 kg/m². Muro lateral 1 (M-01): longitud 4,08 m, R receptor = 45 dB y m′ receptor = 432 kg/m². Fachada / elemento lateral (núcleo de F-01): longitud 6,12 m, R receptor = 43 dB y m′ receptor = 360 kg/m². Selecciona Unión rígida pesada en ambos encuentros. SONARA muestra Kij ≈ 8,7 dB en cada uno."),
        ("Fundamento y resultado con flancos", "Las longitudes se adoptaron de las cotas de AC-01, suponiendo contacto continuo. AC-02 sitúa A-402 sobre A-302 y AC-04 documenta espesores. La continuidad rígida es una hipótesis docente. Los Rw se estimaron como paneles simples de HA de 160, 180 y 150 mm, con 2.400 kg/m³, E = 11 GPa, η = 0,006 y ν = 0,20. F-01 representa solo el núcleo estructural, sin atribuir mejora al trasdosado ni a la ventana. Los demás flancos quedan fuera de esta corrida por falta de datos. L′ₙT,w = 76 dB, L′ₙT,50 proyectado = 76 dB y CI mostrado = −3 dB. Ambos indicadores siguen sobre sus metas. La coincidencia de los índices redondeados con la corrida directa no implica igualdad de las curvas."),
        ("Comparación con la variante", "Conserva área, volumen, TR y criterio de flanqueo al comparar el efecto del tratamiento. Si incorporas flancos para evaluar el desempeño del conjunto, vuelve a calcular la base con la misma configuración de flancos."),
        ("Variante docente guardada en SONARA", "Busca «IM-01 · L-01 · Variante sobrelosa flotante genérica · flancos M-01 y F-01». Se usó Modelo genérico / físico → Sobrelosa flotante, sin cielo y con los mismos flancos de la base. El programa aplica un espectro genérico de mejora: los espesores 10 + 40 + 10 mm describen el detalle de AC-04 y no se ingresaron en este modo. L′ₙT,w bajó de 76 a 67 dB (mejora de 9 dB, aún 21 dB sobre la meta). L′ₙT,50 proyectado bajó de 76 a 74 dB (mejora de 2 dB, aún 24 dB sobre la meta)."),
        ("Revisión técnica", "Catálogo ΔL medido compatible o modelo físico con masa de sobrelosa y s′ trazable. Revisar puentes rígidos y flancos. Exigir L′ₙT,w y CI compatibles; menor nivel es mejor."),
    ], "No sumar mejoras de catálogo y modelo físico del mismo sistema. La diferencia base/variante no es automáticamente el ΔLw de ensayo del revestimiento."),
    7: ("FA-01 · Fachada", [
        ("Modelo esperado", "Fachada 15,30 m²: opaco F-01 10,50 m² + V-01 4,80 m²; V = 51,0 m³. Verificar panel desacoplado, DVH 6/12/4, juntas, exposición y corrección de forma justificadas."),
        ("Comparación", "Exigir resultado de fachada completa y adaptaciones finales, correspondencia del descriptor con el criterio elegido y exposición exterior declarada. La variante debe actuar sobre el componente dominante conservando áreas y exposición."),
    ], "No promediar aritméticamente aislamientos ni usar Rw de la ventana como aislamiento global. Declarar la aproximación del traslado Manual Rw/Ctr."),
    8: ("IN-01 · Instalaciones", [
        ("Modelo esperado", "Fuente sanitaria espectral y condición temporal documentadas, cierre S-01 de 120 mm totales, receptor dormitorio V = 28,8 m³, TR/absorción y vías justificadas."),
        ("Corridas guardadas en SONARA", "Los Alerces · Marco Araos · Docente → Soluciones → Baño principal A-302 → Dormitorio principal A-302 · Instalaciones / HVAC. Busca «IN-01_Base docente» e «IN-01_Variante docente»."),
        ("Operación y espectro de entrada", "Descarga única de WC de 6 L, evento de 10 s como hipótesis, sin usos simultáneos. Bandas 63, 125, 250, 500, 1000, 2000 y 4000 Hz. Lw hipotético para el instante de mayor emisión: 70 / 68 / 66 / 64 / 61 / 58 / 55 dB re 1 pW. Son valores de ejemplo del módulo, sin medición FAST ni respaldo de fabricante. La duración describe el escenario y no interviene en el cálculo del máximo proyectado."),
        ("Geometría y absorción", "Dormitorio V = 28,8 m³. Supuestos didácticos: S-01 expuesto = 3,00 m² y absorción equivalente del lado fuente = 1,50 m² en todas las bandas. TR receptor = 0,50 s; A receptor ≈ 0,16 × 28,8 / 0,50 = 9,22 m². Verifica el área real y la validez del campo difuso, especialmente si el emisor es un shaft estrecho."),
        ("Cierre y espectros R", "Dos placas RF de 12,5 mm por cara, cámara de 70 mm y montante simple a 600 mm como hipótesis de modelación. Proxy del catálogo SONARA: yeso USG Sheetrock Firecode C de 1/2 pulgada, ajustado a 12,5 mm. R de octava obtenido con el motor de panel doble, promediando coeficientes de transmisión dentro de cada octava. Base con cámara sin absorbente: 5,4 / 13,0 / 32,1 / 48,8 / 64,5 / 73,6 / 57,8 dB. Variante con lana mineral de 60 kg/m³: 7,7 / 16,0 / 35,1 / 51,8 / 66,0 / 74,7 / 58,9 dB. El proxy acústico no acredita resistencia al fuego."),
        ("Resultado y alcance", "En SONARA usa Intermitente (LAFmax estimado) → Aérea · recinto adyacente, sin atenuaciones adicionales. Base 41,2 dB(A) y variante 38,5 dB(A), mejora de 2,7 dB. Frente a la meta de 26 dB(A), ambas proyecciones aéreas quedan por encima, por 15,2 y 12,5 dB respectivamente. La vía estructural queda sin cuantificar y el máximo FAST real requiere verificación."),
        ("Registro y verificación", "Deja LAeq,nT sin determinar para este ejemplo: falta un espectro equivalente del ciclo y un intervalo de evaluación. Para verificar en obra, reproduce la descarga, registra el máximo FAST en el dormitorio y mide el TR para normalizar a T₀ = 0,5 s. Para modelar las fijaciones, solicita datos compatibles de excitación y transferencia instalada."),
    ], "Distingue el escenario académico de una caracterización de la descarga real. No conviertas LAeq en máximo FAST ni simules una abrazadera con una resta arbitraria."),
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


def _teacher_stage2_answers():
    st.markdown("### Revisión de la ficha de lectura")
    st.info("**Propósito formativo:** comprobar que el alumno sabe extraer y justificar entradas del modelo. No se exige todavía calcular aislamiento, obtener una clase ni diseñar ensayos.")
    st.markdown("#### 01 · Geometría esperada")
    _lab_table(pd.DataFrame([
        ["M-01 · separador", "4,08 × 2,50", "10,20 m²", "Área del separador entre los estares, no superficie de piso."],
        ["Volumen del estar", "20,40 × 2,50", "51,0 m³", "Usar altura libre; no altura entre niveles."],
        ["FA-01 · fachada bruta", "6,12 × 2,50", "15,30 m²", "Solo el paño del estar."],
        ["V-01 · ventana del estar", "3,20 × 1,50", "4,80 m²", "No incorporar V-02 del dormitorio."],
        ["F-01 · opaco", "15,30 − 4,80", "10,50 m²", "Comprobar 10,50 + 4,80 = 15,30 m²."],
    ], columns=["Magnitud", "Operación", "Resultado esperado", "Qué revisar"]))
    st.markdown("#### 02 · Riesgos: ejemplos de respuestas válidas")
    st.caption("La actividad solicita tres fichas: dónde está el riesgo, cómo podría pasar el ruido y qué revisar. No es obligatorio repetir estos ejemplos ni utilizar tres casos diferentes.")
    _lab_table(pd.DataFrame([
        ["AI-01 · AC-01/AC-04", "Encuentro rígido del medianero con losas o fachada", "Transmisión por flancos", "Revisar continuidad, uniones y solución de desacople cuando corresponda."],
        ["IM-01 · AC-02/AC-04", "Contacto rígido de sobrelosa con perímetro", "Puente que reduce la eficacia del piso flotante", "Comprobar banda perimetral, pasos y continuidad de la capa resiliente."],
        ["FA-01 · AC-03/AC-04", "Juntas de ventana mal resueltas", "Fugas de ruido aéreo", "Revisar marco, sellos y prestación del conjunto instalado."],
        ["IN-01 · AC-01/AC-04", "Fijaciones o pasos sanitarios rígidos", "Transmisión estructural y posibles fugas aéreas", "Revisar abrazaderas, pasos y continuidad del cierre del shaft."],
    ], columns=["Caso y lámina", "Riesgo posible", "Mecanismo", "Comprobación o mejora"]))
    st.markdown("#### 03 · Datos pendientes: qué debe reconocer")
    st.caption("El alumno elige tres datos. Cada ficha debe identificar el dato y su caso, explicar su uso y proponer una fuente; no se exige aportar todavía el valor numérico.")
    _lab_table(pd.DataFrame([
        ["Aéreo", "R(f) o indicadores compatibles, TR en s y datos de flancos/uniones", "Ficha, cálculo del elemento y descripción del encuentro."],
        ["Impacto", "Prestación del piso, ΔL(f) o rigidez dinámica en MN/m³ según método", "Ficha del sistema completo o hipótesis documentada; no duplicar mejoras."],
        ["Fachada", "Prestación espectral de ventana y opaco, exposición Lden en dB", "Ficha del conjunto y antecedente de exposición o hipótesis declarada."],
        ["Instalaciones", "Datos de fuente y transferencia aérea/estructural según módulo", "Condición de descarga, ficha o datos compatibles con el método; no inferirlos del dibujo."],
    ], columns=["Familia", "Datos que podrían faltar", "Procedencia esperada"]))
    st.markdown("#### Criterio de revisión: devolución formativa")
    _lab_table(pd.DataFrame([
        ["Logrado", "Cinco operaciones con unidades correctas; tres fichas de riesgo con ubicación, recorrido y revisión; tres datos pendientes con caso/unidad, uso y fuente."],
        ["Parcialmente logrado", "Razonamiento válido con una omisión o error localizado que puede corregirse."],
        ["Por corregir", "Confunde área y volumen, incorpora otra ventana, interpreta espesores como aislamiento o inventa datos sin declararlos."],
    ], columns=["Estado formativo", "Cómo reconocerlo"]))
    st.warning("**Errores que requieren corrección:** no sumar el paquete de piso a los 160 mm de losa desnuda; no deducir prestaciones del render; no confundir riesgo con defecto confirmado. Los balcones son esquemáticos. Guardar acredita entrega, no corrección técnica.")
    st.caption("Continuidad con Etapa 1: A-301 al oeste, A-402 encima, fachada norte y shaft S-1 junto al dormitorio principal. En elevación exterior norte, oeste a la derecha. Pauta exclusiva de vista Docente; no se muestra en Alumno ni Zoom.")


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
        if stage == 2:
            _teacher_stage2_answers()
            return
        from html import escape
        sections = criteria.items() if stage == 4 else [(None, criteria)]
        for heading, cards in sections:
            if heading:
                st.markdown(f"#### {heading}")
            for criterion, expected in cards:
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
    for name, area, volume, location, provenance in SOURCE_ROOMS:
        rows.append(["Recinto emisor", name, area, volume, f"{location} · {provenance}"])
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
            "Abre Flanqueos → Incluir flanqueos y configura los encuentros de M-01 siguiendo la guía de campos que aparece debajo.",
            "Identifica si domina el camino directo o uno lateral. Diseña una variante: modificar M-01 o añadir un trasdosado desacoplado; si domina un flanco, actúa sobre el encuentro correspondiente.",
            "Recalcula con la misma geometría y documenta los caminos activos en ambas corridas. Compara el DₙT,50 proyectado de base y variante con la meta de 58 dB.",
        ],
        "limit": "El ingreso directo por Rw del módulo entre recintos reconstruye una curva de referencia: declara esa aproximación. No copies C y Ctr de la placa como si fueran los términos de la curva final entre recintos.",
        "evidence": "Configuración de M-01 y su variante, captura del visual constructivo, entradas de recintos/uniones, curvas finales y resultados DₙT,w y DₙT,50 de ambas corridas.",
    },
    "Impacto": {
        "route": "Proyecto → Elementos (Paramento horizontal) → Diseñar → Ruido de impacto → Soluciones.",
        "inputs": [
            ["L-01 · losa base", "Hormigón armado · 160 mm", "Registra la densidad seleccionada; SONARA obtiene la masa superficial."],
            ["Piso superior", "Piso: resiliente 10 + sobrelosa 40 + terminación 10 mm", "Capa resiliente 10 mm y terminación 10 mm (AC-04). La rigidez requiere ficha o hipótesis."],
            ["Geometría IM-01", "Área entrepiso = 20,4 m² · V = 51,0 m³", "Usa el mismo TR receptor en la comparación base/variante."],
        ],
        "steps": [
            "En Proyecto → Diseñar, abre «Elemento activo a diseñar» y selecciona Estar A-402 → Estar-comedor A-302 · Paramento horizontal. Comprueba que la banda indique «Requerimiento activo: IM-01 · L-01». En Calculadora del requerimiento elige Ruido de impacto y luego el método ISO 12354-2. Selecciona «Calcular por masa superficial» e ingresa 160 mm de losa estructural y la densidad documentada.",
            "Calcula la losa base sin revestimiento ni cielo. Usa la guía de flanqueos que aparece debajo para configurar los encuentros y guarda la corrida como IM-01 · Base con flancos. Puedes conservar una corrida directa aparte para distinguir el efecto de los caminos laterales.",
            "Para reproducir la variante docente, selecciona Modelo genérico / físico → Sobrelosa flotante. Declara que usaste su espectro genérico. Para caracterizar una solución específica, puedes usar un espectro ΔL medido de un montaje compatible o «Piso flotante físico» con datos justificados.",
            "En Piso flotante físico ingresa la masa superficial de la sobrelosa: m′ = densidad × 0,040 m. Ingresa la rigidez dinámica s′ de la capa resiliente desde una ficha; no la deduzcas solo de su espesor.",
            "Define el cielo inferior solo si forma parte de tu propuesta. Completa área 20,4 m², volumen 51,0 m³, TR y flancos; revisa el visual constructivo y recalcula.",
            "Compara L′ₙT,w y L′ₙT,50 proyectado de base y variante con sus metas de 46 y 50 dB, respectivamente. Menor nivel de impacto significa mejor desempeño. Explica la influencia del piso, los puentes rígidos y los flancos.",
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
            "En Origen acústico, usa «SONARA · Panel doble» para F-01 y «SONARA · DVH» para V-01. El cálculo de fachada usa directamente la curva por bandas de cada componente.",
            "Ingresa exposición exterior y corrección por forma a partir de antecedentes o hipótesis identificadas. Añade juntas o aireadores únicamente cuando puedas justificar sus datos.",
            "Compara una variante del componente dominante —ventana, sellos o paño opaco— manteniendo áreas y exposición. Para ambas corridas, copia D₂m,nT,w, C y Ctr desde «Descriptores de la curva de fachada D₂m,nT». La ficha calcula D₂m,nT,Atr y el margen respecto a la meta.",
        ],
        "limit": "El modo Manual Rw/Ctr no transfiere íntegramente el espectro calculado del componente. Informa esa limitación. No uses el Rw de la ventana como resultado global ni registres el dormitorio V-02 dentro del caso del estar V-01.",
        "evidence": "Modelos F-01 y V-01, espectros de los componentes, áreas, hipótesis exterior y de forma, juntas consideradas y curva final de fachada.",
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
    if case_name == "Aéreo interior":
        st.markdown("#### Cómo completar los flancos de AI-01")
        st.markdown(
            "Localiza M-01 en la planta AC-01. El estar A-301 es el emisor y el estar A-302 es el receptor. "
            "Identifica qué elemento lateral llega al separador en cada extremo y revisa su continuidad en planta, corte y detalles. "
            "Activa solo los encuentros que modeles. Configura **Losa de piso** y **Losa de cielo** por separado si ambas corresponden al caso."
        )
        _lab_table(
            pd.DataFrame([
                ["R elemento lado emisor / receptor [dB]", "En Manual, introduce el Rw del tramo lateral de A-301 y el del tramo lateral de A-302. Usa un ensayo de la misma solución o un cálculo con sus capas y espesores. SONARA reconstruye la curva por bandas a partir de esos índices. Si los tramos son iguales, «Calcular con SONARA» aplica a ambos la curva calculada para una sola composición."],
                ["Longitud de unión lᵢⱼ [m]", "Usa la longitud de contacto del flanco con M-01. Para un muro lateral con contacto vertical completo, adopta 2,50 m según AC-02. Para piso o cielo, usa 4,08 m solo si el contacto abarca todo el largo útil de M-01 en AC-01. Si el encuentro es parcial, mide el tramo conectado."],
                ["m′ emisor / receptor [kg/m²]", "Calcula por separado la masa superficial de los tramos de A-301 y A-302. Para cada capa incluida en el elemento modelado, multiplica densidad [kg/m³] por espesor [m] y suma las masas. Como ejemplo, 150 mm de hormigón a 2.400 kg/m³ dan 360 kg/m². Ese espesor es ilustrativo."],
                ["Tipo de unión / desacople", "Revisa el detalle del encuentro con M-01. Identifica la geometría, la continuidad y la presencia de una junta elástica. Elige la opción que represente el detalle o usa Manual si cuentas con un Kij respaldado."],
                ["Corrección de unión Kij [dB]", "Ingresa un valor medido según la serie ISO 10848 o una estimación aplicable al tipo de unión y al camino de transmisión según ISO 12354-1. El valor automático de SONARA es referencial. Registra su procedencia y el criterio adoptado."],
            ], columns=["Campo en SONARA", "Cómo completarlo"]),
            hide_index=True, width="stretch",
        )
        st.markdown("#### Cómo elegir el tipo de unión en SONARA")
        st.markdown(
            "Ubica la unión con M-01 en **AC-01**, revisa su continuidad en **AC-02** y consulta el detalle "
            "estructural o la ficha de montaje para confirmar cómo se conectan las piezas. "
            "Identifica qué elementos continúan a través del encuentro y cuáles terminan en él."
        )
        _lab_table(
            pd.DataFrame([
                ["Unión rígida pesada", "Elementos pesados conectados rígidamente. En AI-01, úsala como aproximación preliminar si el detalle confirma que la losa de hormigón y M-01 forman un encuentro monolítico."],
                ["Unión rígida liviana", "Elemento liviano fijado directamente al soporte mediante una conexión rígida. Comprueba el sistema de fijación."],
                ["Unión semi-rígida", "El detalle o la ficha documenta una conexión con rigidez parcial. Si la conexión es desconocida, registra ese dato como pendiente."],
                ["Montante simple", "Las placas comparten una misma fila de montantes. Revisa a qué perfilería se fija cada cara."],
                ["Montantes independientes / doble estructura", "Revisa en la ficha qué perfilería sostiene cada cara. Distingue los montantes de cada hoja de los dos bastidores completos y comprueba si hay puentes rígidos."],
                ["Junta elástica / resiliente", "El desacople debe estar en el encuentro que modelas. Una capa resiliente bajo el pavimento por sí sola deja sin confirmar el desacople entre muro y losa."],
                ["Manual", "Ingresa un Kij de ensayo o de un cálculo aplicable a la geometría, a los elementos y al camino de transmisión. Registra el origen del valor."],
            ], columns=["Opción en SONARA", "Qué verificar antes de elegir"]),
            hide_index=True, width="stretch",
        )
        st.markdown(
            "Consulta la [ISO 12354-1:2017](https://www.iso.org/standard/70242.html), **Anexo E** para uniones "
            "de edificios pesados y **Anexo F** para construcciones livianas. En el Anexo E, busca la geometría "
            "del encuentro, por ejemplo en T o en cruz, y el camino de transmisión correspondiente. "
            "Para datos medidos, consulta la [serie ISO 10848](https://www.iso.org/standard/67229.html) "
            "y verifica que el ensayo represente tu unión."
        )
        st.info(
            "Las categorías del menú son aproximaciones de SONARA y el Kij automático es referencial. "
            "Documenta para cada encuentro el plano o detalle, la composición de ambos lados y el origen del Kij. "
            "Si faltan datos, declara la hipótesis y reporta la corrida como preliminar. "
            "Los valores precargados en SONARA son ejemplos de entrada."
        )
    if case_name == "Impacto":
        st.markdown("#### Cómo configurar los flanqueos de impacto de IM-01")
        st.markdown(
            "El impacto excita la losa L-01 en A-402. Parte de la vibración puede pasar a los muros unidos a la losa "
            "y radiar al estar-comedor A-302. Identifica en AC-01 los bordes en contacto, usa AC-02 para comprobar la relación "
            "entre pisos y revisa en AC-04 los espesores y el detalle constructivo. En el modo ISO 12354-2, activa «Incluir flanqueos de impacto» "
            "y marca únicamente los encuentros que hayas caracterizado o cuya hipótesis puedas justificar."
        )
        _lab_table(
            pd.DataFrame([
                ["R emisor / R receptor [dB]", "Para cada camino losa → muro, ingresa el Rw de la losa excitada y el Rw del elemento lateral que radia hacia el receptor. Usa datos de ensayo o declara cómo estimaste cada Rw."],
                ["Longitud de unión [m]", "En AC-01, sigue en planta el borde común losa–muro y toma la cota del tramo conectado. Contrasta su continuidad en AC-02 y AC-04. Si el contacto es parcial, mide solo el tramo unido."],
                ["m′ emisor / m′ receptor [kg/m²]", "Usa las masas superficiales de la losa y del elemento lateral del camino. Para una capa homogénea, multiplica densidad [kg/m³] por espesor [m]."],
                ["Tipo de unión y Kij [dB]", "Elige Unión rígida pesada si el encuentro entre elementos pesados es rígido o si lo adoptas como hipótesis explícita. Una banda resiliente del piso flotante no demuestra desacople de la unión estructural. Usa Manual cuando dispongas de un Kij respaldado para ese encuentro. El valor automático de SONARA es referencial."],
            ], columns=["Campo en SONARA", "Cómo completarlo"]),
            hide_index=True, width="stretch",
        )
        st.markdown("##### Longitudes y tipo de unión en el ejemplo docente")
        _lab_table(pd.DataFrame([
            ["L-01 → M-01 (Muro lateral 1)", "4,08 m", "Cota del borde oeste del estar en AC-01. Se supone contacto continuo con el muro de HA de 180 mm."],
            ["L-01 → F-01 (Fachada / elemento lateral)", "6,12 m", "Cota del borde norte del estar en AC-01. Se supone una línea estructural continua; comprueba el detalle a la altura de la losa antes de descontar un vano."],
        ], columns=["Camino", "Longitud adoptada", "Cómo se obtuvo"]), hide_index=True, width="stretch")
        st.markdown(
            "En ambos encuentros se adoptó **Unión rígida pesada** porque se modelaron losa y núcleo de muro de HA "
            "con contacto rígido continuo. Es una hipótesis docente y el Kij automático de 8,7 dB es referencial. "
            "Selecciona **Unión rígida liviana** si el flanco liviano está fijado rígidamente al soporte, o **Unión semi-rígida** "
            "si el detalle acredita rigidez parcial. Para tabiques, revisa si las caras comparten montantes o tienen perfilerías "
            "independientes o doble bastidor. Elige **Junta elástica / resiliente** solo si el desacople está en la unión estructural "
            "que modelas. Usa **Manual** cuando tengas un Kij de ensayo o de cálculo aplicable al encuentro."
        )
        st.info(
            "Revisa el camino directo, los flancos activos y el total en las curvas por bandas. "
            "Conserva los mismos encuentros al evaluar la variante, salvo cambios constructivos que afecten la unión. "
            "Documenta qué caminos omitiste, por qué y qué supuestos usaste."
        )
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
    is_ai = case["code"] == "AI-01"
    ai_target = 58
    is_facade = case["code"] == "FA-01"
    lden = saved.get("c5l1_s4_inputs", {}).get("lden") if is_facade else None
    facade_target = max(lden - 20, 30) if lden is not None else None
    st.markdown("### Registra tu solución final y la comparación con la base")
    st.caption("Usa tus propios cálculos; los números del ejemplo de etapa 3 no son resultados de este formulario.")
    with st.form(f"c5l1_form_{case['code']}"):
        values = {}
        if is_ai:
            st.info(f"**Meta AI-01 · DₙT,50 ≥ {ai_target} dB.** Copia DₙT,w y «DnT,50 proyectado» de cada corrida en SONARA.")
            for title, prefix in (("Base · M-01", "base_"), ("Variante · solución final", "")):
                st.markdown(f"#### {title}")
                columns = st.columns(2)
                for column, (key, label) in zip(columns, (
                    ("dntw", "DₙT,w [dB]"), ("dnt50", "DₙT,50 proyectado [dB]"),
                )):
                    field = prefix + key
                    values[field] = column.number_input(
                        label, value=stored.get(field), step=0.1, format="%.1f",
                        placeholder="Resultado SONARA", key=f"c5l1_ai_{field}",
                    )
            st.caption("C y Ctr de la variante son opcionales. La adaptación C₅₀–₃₁₅₀ se obtiene de la diferencia entre DₙT,50 y DₙT,w de cada corrida.")
        if is_facade:
            st.info("Copia D₂m,nT,w, C y Ctr de la misma curva de fachada D₂m,nT en SONARA. El formulario suma D₂m,nT,w + Ctr al guardar.")
            if facade_target is None:
                st.caption("Registra el Lden adoptado en la etapa 4 para calcular la meta. El mínimo absoluto de 30 dB es una referencia provisional.")
            else:
                st.caption(f"Lden adoptado: {lden:g} dB · Meta de diseño: D₂m,nT,Atr ≥ {facade_target:g} dB.")
        groups = (("Base", "base_"), ("Variante · solución final", "")) if is_facade else ((None, ""),)
        for title, prefix in groups:
            if title:
                st.markdown(f"#### {title}")
            cols = st.columns(min(3, len(fields)))
            for index, (key, label, unit) in enumerate(fields):
                field = prefix + key
                values[field] = cols[index % len(cols)].number_input(
                    f"{label} [{unit}]",
                    value=stored.get(field),
                    step=0.1,
                    format="%.1f",
                    placeholder="Resultado SONARA",
                    **({"key": f"c5l1_fa_{field}"} if is_facade else {}),
                )
        st.markdown("#### Comparación de diseño · base → variante")
        if is_facade:
            target = (
                f"D₂m,nT,Atr ≥ {facade_target:g} dB · Lden {lden:g} dB · objetivo de diseño FA-01"
                if facade_target is not None else "FA-01 · meta pendiente de Lden · mínimo absoluto 30 dB"
            )
        else:
            target = f"DₙT,50 ≥ {ai_target} dB · objetivo de diseño AI-01" if is_ai else st.text_input(
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
            placeholder=(
                "Qué cambiaste, qué mantuviste y qué camino directo o lateral limita la variante."
                if is_ai else "Qué cambiaste, qué mantuviste y por qué mejora o no el descriptor final."
            ),
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
        if is_ai and any(values[key] is None for key in ("base_dntw", "base_dnt50", "dntw", "dnt50")):
            st.warning("Completa DₙT,w y DₙT,50 proyectado de la base y de la variante.")
        elif is_facade and any(value is None for value in values.values()):
            st.warning("Completa D₂m,nT,w, C y Ctr de la base y de la variante.")
        elif not is_ai and any(value is None for value in values.values()) and not undetermined:
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
            if is_facade:
                payload["base_d2mnt_atr"] = round(values["base_d2mntw"] + values["base_ctr"], 1)
                payload["d2mnt_atr"] = round(values["d2mntw"] + values["ctr"], 1)
            _save(lab, saved, stage, **{f"c5l1_result_{case['code']}": payload})
            st.success("Resultado guardado. La clase acústica todavía no ha sido asignada.")
    if is_ai:
        result = saved.get("c5l1_result_AI-01", {})
        comparison = []
        for title, prefix in (("Base", "base_"), ("Variante", "")):
            dntw, dnt50 = result.get(prefix + "dntw"), result.get(prefix + "dnt50")
            if dntw is not None and dnt50 is not None:
                comparison.append([title, dntw, round(dnt50 - dntw, 1), dnt50, round(dnt50 - ai_target, 1)])
        if comparison:
            _lab_table(pd.DataFrame(comparison, columns=[
                "Corrida guardada", "DₙT,w [dB]", "C₅₀–₃₁₅₀ [dB]",
                "DₙT,50 proyectado [dB]", f"Margen frente a {ai_target} dB",
            ]), hide_index=True, width="stretch")
        if len(comparison) == 2:
            st.caption(f"Variación de DₙT,50 · variante menos base: {result['dnt50'] - result['base_dnt50']:+.1f} dB.")

    if is_facade:
        result = saved.get("c5l1_result_FA-01", {})
        comparison = []
        for title, prefix in (("Base", "base_"), ("Variante", "")):
            weighted, ctr = result.get(prefix + "d2mntw"), result.get(prefix + "ctr")
            if weighted is None or ctr is None:
                continue
            adapted = round(weighted + ctr, 1)
            margin = round(adapted - facade_target, 1) if facade_target is not None else None
            comparison.append([title, weighted, result.get(prefix + "c"), ctr, adapted, margin])
        if comparison:
            _lab_table(pd.DataFrame(comparison, columns=[
                "Corrida guardada", "D₂m,nT,w [dB]", "C [dB]", "Ctr [dB]",
                "D₂m,nT,Atr [dB]", "Margen frente a la meta [dB]",
            ]), hide_index=True, width="stretch")
        if len(comparison) == 2:
            st.caption(f"Variación de D₂m,nT,Atr · variante menos base: {comparison[1][4] - comparison[0][4]:+.1f} dB.")


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
    rows = [
        ["AI-01", "DₙT,50", "≥ 58 dB", "Resultado entre recintos con flancos.", "§5.2 · tabla 1, fila 1 · p. 7 / PDF 13"],
        ["IM-01", "L′ₙT,w Y L′ₙT,50", "≤ 46 dB Y ≤ 50 dB", "Comprobar ambos indicadores y adaptación de baja frecuencia.", "§5.3 · tabla 2, fila 1 · p. 8 / PDF 14"],
        ["FA-01", "DₙT,A,tr · justificar correspondencia con salida de fachada", "≥ max(Lden − 20; 30) dB", "Depende de exposición y espectro documentados.", "§5.4 · tabla 3, notas a–b · p. 8 / PDF 14"],
        ["IN-01", "LAFmax,nT", "≤ 26 dB(A)", "Descarga intermitente; máximo FAST normalizado a T₀ = 0,5 s.", "§5.5 · tabla 4, fila 2 · p. 9 / PDF 15"],
    ]
    if code is not None:
        rows = [row for row in rows if row[0] == code]
    st.markdown("#### Objetivos de clase A del ejercicio")
    _lab_table(pd.DataFrame(rows, columns=["Caso", "Descriptor", "Objetivo A", "Condiciones", "Referencia ISO/TS 19488:2021"]))
    st.caption("Criterios fijados por el encargo y desarrollados en la Etapa 1. No debes volver a introducirlos. Tus anotaciones previas se conservan, pero no sustituyen estos objetivos. Aplicar las notas completas de cada tabla.")
    lden = saved.get("c5l1_s4_inputs", {}).get("lden")
    if code is None or code == "FA-01":
        if isinstance(lden, (int, float)):
            st.info(f"**FA-01:** con Lden guardado de {lden:g} dB, el límite es **≥ {max(lden - 20, 30):g} dB**. Comprueba descriptor, espectro y notas.")
        else:
            st.info("**FA-01:** la regla ya está definida. Registra y justifica Lden en esta etapa para obtener su límite numérico.")


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
    st.markdown("#### Recintos emisores colindantes para SONARA")
    _lab_table(pd.DataFrame(SOURCE_ROOMS, columns=["Recinto", "Área [m²]", "Volumen [m³]", "Ubicación", "Procedencia"]), hide_index=True, width="stretch")
    st.info("Datos definidos para este ejercicio: estar A-301 y estar A-402, cada uno de 20,40 m² y altura libre 2,50 m; V = 20,40 × 2,50 = 51,0 m³. A-301 es una hipótesis académica porque su planta es parcial; A-402 repite el estar A-302. No midas el dibujo parcial ni uses área o volumen cero. Exterior norte no es un recinto cerrado: su volumen no aplica.")
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
    st.markdown("#### Otras situaciones de la norma · fuera del alcance de este laboratorio")
    st.markdown("En este laboratorio desarrollarás únicamente los cuatro casos **AI-01, IM-01, FA-01 e IN-01**. Las situaciones siguientes se presentan como referencia y **no requieren cálculos ni modelos adicionales en SONARA para esta entrega**. Quedan fuera del alcance del ejercicio; esto no significa que sean no aplicables al edificio ni elimina los requisitos de una clasificación completa.")
    _lab_table(pd.DataFrame([
        ["Voces en el pasillo o la escalera común → recinto de una vivienda", "Ruido aéreo: atraviesa el cerramiento que incluye la puerta de entrada. Debe evaluarse el conjunto, no solo la puerta.", "DₙT,A ≥ 46 dB · más aislamiento es mejor", "§5.2 · Airborne sound insulation · tabla 1, fila 2 · p. 7 / PDF 13"],
        ["Actividad ruidosa en un local → recinto de una vivienda", "Ruido aéreo, por ejemplo música. Además del aislamiento, hay que estimar el ruido de la actividad concreta. El ejemplo no implica que Los Alerces tenga ese local.", "DₙT,50 ≥ 64 dB · más aislamiento es mejor", "§5.2 · Airborne sound insulation · tabla 1, fila 3 · p. 7 / PDF 13"],
        ["Pisadas en zonas comunes o en balcones, terrazas y baños de otra vivienda → recinto receptor", "Ruido de impacto: el golpe se transmite por la estructura. No es el ruido de voces del primer caso. Revisar las exclusiones de la nota b para espacios menores de 4 m².", "L′ₙT,w ≤ 50 dB · menos ruido recibido es mejor", "§5.3 · Impact sound insulation · tabla 2, fila 2 y nota b · p. 8 / PDF 14"],
        ["Golpes o impactos de una actividad ruidosa en un local → recinto de una vivienda", "Ruido de impacto transmitido por la estructura. Es una situación distinta del ruido aéreo de ese mismo local; deben cumplirse ambos límites de impacto indicados.", "L′ₙT,w ≤ 40 dB Y L′ₙT,50 ≤ 44 dB · menos ruido recibido es mejor", "§5.3 · Impact sound insulation · tabla 2, fila 3 y notas a/c · p. 8 / PDF 14"],
    ], columns=["De dónde viene el ruido y a dónde llega", "Qué significa en la práctica", "Requisito de clase A", "Referencia · ISO/TS 19488:2021"]))
    st.caption("Cómo leerla: la flecha indica fuente → receptor. En aislamiento aéreo se exige un mínimo (≥); en impacto se limita el nivel recibido (≤). Estos valores corresponden a situaciones distintas: no sustituyen los objetivos de AI-01 ni de IM-01.")
    st.markdown("#### Cómo comparar tus resultados con la clase A")
    st.markdown("Cada requisito tiene un **descriptor**, un **límite** y un **sentido de comparación**. Compara siempre el resultado con el límite del mismo descriptor.")
    _lab_table(pd.DataFrame([
        ["Aislamiento aéreo", "Mínimo: resultado ≥ límite", "Un aislamiento mayor ofrece mejor protección."],
        ["Ruido de impacto e instalaciones", "Máximo: resultado ≤ límite", "Un nivel recibido menor ofrece mejor protección."],
    ], columns=["Característica", "Cómo se comprueba", "Qué significa"]))

    st.markdown("##### Aislamiento entre viviendas · criterio de AI-01")
    st.info("**Criterio principal del ejercicio: DₙT,50 ≥ 58 dB.** Evalúa estar A-301 → estar A-302, incluyendo transmisión directa y flancos. El Rw del muro aislado no acredita por sí solo este objetivo.")
    _lab_table(pd.DataFrame([
        ["DₙT,50", "≥ 58 dB", "Descriptor principal que utilizaremos en AI-01."],
        ["DₙT,A", "≥ 60 dB", "Alternativa: límite 2 dB mayor que el de DₙT,50."],
        ["DₙT,w", "≥ 62 dB", "Alternativa: límite 2 dB mayor que el de DₙT,A."],
    ], columns=["Descriptor del resultado", "Límite de clase A para AI-01", "Cuándo utilizarlo"]))
    st.markdown("**Son alternativas, no tres comprobaciones simultáneas.** Los ajustes cambian el límite exigido; no convierten un resultado de un descriptor a otro sumándole 2 o 4 dB. Si SONARA entrega otro descriptor, obtén los datos necesarios para calcular el requerido o documenta la alternativa admitida.")
    st.caption("Referencia: ISO/TS 19488:2021 · §5.2, Airborne sound insulation · tabla 1, fila 1 y nota a · p. 7 / PDF 13.")

    st.markdown("##### Ruido de instalaciones · FAST y SLOW")
    st.markdown("FAST y SLOW son ponderaciones temporales distintas para determinar el nivel máximo. Si utilizas la alternativa SLOW admitida por la tabla 4, debes emplear su descriptor y su límite específico, **4 dB menor que el correspondiente a FAST**. Para clase A, el máximo SLOW normalizado es **LASmax,nT ≤ 22 dB(A)**.")
    st.info("**Cambia el límite de comparación, no el resultado.** No restes 4 dB a un resultado FAST para obtener SLOW. Comprueba qué descriptor proporciona el modelo y qué condición de funcionamiento representa.")
    st.caption("Referencia: ISO/TS 19488:2021 · §5.5, Sound from service equipment · tabla 4 y nota relativa a SLOW · p. 9 / PDF 15.")

    st.markdown("##### Qué debes entregar en los cuatro casos")
    _lab_table(pd.DataFrame([
        ["1 · Identifica el objetivo", "Registra el descriptor, el límite, el signo ≥ o ≤ y las condiciones aplicables."],
        ["2 · Documenta los datos", "Indica geometría, materiales, fuentes e hipótesis; identifica cualquier dato pendiente."],
        ["3 · Calcula la condición inicial", "Modela el caso en Proyecto de SONARA y conserva la evidencia del resultado."],
        ["4 · Diseña y comprueba la mejora", "Modifica la solución, vuelve a calcular y compara el mismo descriptor con su límite."],
    ], columns=["Paso", "Qué debes hacer"]))

    st.markdown("##### Hasta dónde llega tu conclusión")
    st.info("La entrega evalúa el **desempeño previsto de AI-01, IM-01, FA-01 e IN-01**. Las demás situaciones quedan fuera del alcance de este laboratorio. Tus resultados no demuestran la clase global de la vivienda ni del edificio; esa conclusión requiere cubrir todas las características y situaciones aplicables, además de la verificación correspondiente.")
    st.markdown("**Separadores entre viviendas y tabiques interiores:** el muro A-301/A-302 forma parte del caso AI-01. Los tabiques entre recintos de la propia A-302 pueden diseñarse como una prestación adicional; el aislamiento dentro de una misma vivienda queda excluido de esta clasificación.")
    st.caption("Referencia: ISO/TS 19488:2021 · §4, Acoustic classes · p. 6 / PDF 12.")

    st.markdown("### 4 · Cómo evaluar y presentar tus predicciones")
    st.info("**Estás en la etapa de diseño.** En esta entrega trabajarás con cálculos en **Proyecto de SONARA**. No debes realizar mediciones, elegir un procedimiento de ensayo ni definir una muestra de viviendas.")
    st.markdown("#### Alcance del ejercicio")
    st.markdown("Diseñarás soluciones para alcanzar los objetivos de clase A en **cuatro situaciones de A-302**. Los Alerces tiene 20 viviendas, pero esta entrega no exige calcularlas todas ni demostrar la clase global del edificio.")
    _lab_table(pd.DataFrame([
        ["AI-01 · aéreo entre viviendas", "Estar A-301 → estar A-302", "Separador M-01, encuentros y transmisiones por flancos."],
        ["IM-01 · impacto", "Estar A-402 → estar A-302", "Losa L-01, sistema de piso y encuentros."],
        ["FA-01 · fachada", "Exterior norte → estar A-302", "Conjunto F-01 + V-01, juntas y condiciones de exposición adoptadas."],
        ["IN-01 · instalaciones", "Descarga sanitaria → dormitorio principal A-302", "Cierre del shaft S-1, fijaciones y vías de transmisión."],
    ], columns=["Caso", "Relación que estudiarás", "Qué debes diseñar"]))
    st.markdown("#### Del cálculo inicial a la solución propuesta")
    _lab_table(pd.DataFrame([
        ["1 · Prepara el modelo", "Registra geometría, materiales, encuentros, fuente y condiciones aplicables. Documenta hipótesis y datos pendientes."],
        ["2 · Calcula la condición inicial", "Obtén el descriptor requerido para cada caso y compáralo con su objetivo de clase A."],
        ["3 · Rediseña", "Elige materiales, capas, espesores, tratamientos y encuentros que mejoren el desempeño. Justifica cada cambio."],
        ["4 · Comprueba la propuesta", "Recalcula con el mismo criterio y conserva evidencia de entradas y resultados. Indica si alcanza el objetivo o cuánto falta."],
    ], columns=["Paso", "Trabajo en Proyecto de SONARA"]))
    st.markdown("**Diseña con margen:** busca superar el mínimo de aislamiento y quedar por debajo de los máximos de impacto e instalaciones. Justifica el margen adoptado según la solución y la incertidumbre; alcanzar exactamente el límite en una predicción deja poco margen frente a variaciones de ejecución.")
    st.caption("Referencia: ISO/TS 19488:2021 · Anexo A informativo, A.2.1, Procedure A · pp. 11–12 / PDF 17–18: combina predicciones de diseño, inspecciones durante la construcción y comprobaciones en el edificio terminado. Aquí se desarrolla la fase de predicción.")

    st.markdown("#### Qué debe mostrar tu entrega")
    _lab_table(pd.DataFrame([
        ["Condición inicial", "Datos e hipótesis, solución base, descriptor calculado y comparación con el límite."],
        ["Propuesta de mejora", "Especificación constructiva, cambios justificados y resultado del nuevo cálculo."],
        ["Conclusión por caso", "Alcanza el objetivo de diseño, no lo alcanza o no puede determinarse con los datos disponibles. Explica la brecha o información pendiente."],
        ["Evidencia", "Modelos y resultados de Proyecto de SONARA que permitan revisar lo calculado."],
    ], columns=["Contenido", "Qué debes registrar"]))
    st.info("**Conclusión del laboratorio:** desempeño previsto de AI-01, IM-01, FA-01 e IN-01. Si los cuatro alcanzan sus límites, puedes afirmar que la propuesta satisface los objetivos de diseño de esos cuatro casos. Esto no demuestra por sí solo la clase A global de A-302 ni del edificio.")

    st.markdown("#### Cómo se determina la clase acústica global")
    st.markdown("Esta explicación es contexto para comprender el alcance de tus resultados; no añade cálculos a la entrega. **Las clases no se promedian.** Si se evaluaran todas las características aplicables de una vivienda o edificio, la clase global quedaría limitada por la clase más desfavorable que corresponda considerar.")
    _lab_table(pd.DataFrame([
        ["Grupo T1", "Aéreo A · impacto A · fachada A · instalaciones A · comunes A", "A"],
        ["Grupo T2", "Aéreo A · impacto A · fachada B · instalaciones A · comunes A", "B · limitada por fachada"],
        ["Grupo T3", "Aéreo A · impacto A · fachada A · instalaciones C · comunes A", "C · limitada por instalaciones"],
    ], columns=["Grupo del ejemplo", "Clases de todas las características aplicables", "Clase del grupo"]))
    st.markdown("**Lectura del ejemplo:** si los tres grupos pertenecen a un mismo edificio y la evaluación completa respalda esos resultados, su clase global queda limitada a **C**. Para aspirar a A habría que mejorar la fachada del grupo T2 y las instalaciones del grupo T3, y comprobar nuevamente el conjunto. Si pertenecen a edificios distintos, informa la clase de cada edificio; no promedies las letras para el condominio.")
    st.caption("Ejemplo hipotético, ajeno a los resultados de Los Alerces. Referencia: ISO/TS 19488:2021 · §4, Acoustic classes · p. 6 / PDF 12; A.3, Contents of verification report for classification of a dwelling or a building · p. 13 / PDF 19; A.4, Classification examples · pp. 13–14 / PDF 19–20.")

    st.markdown("#### Qué ocurre después del diseño")
    st.markdown("En una obra real, las predicciones se complementan posteriormente con inspecciones de ejecución y comprobaciones del edificio terminado. **Esas actividades quedan fuera de esta entrega.** Por eso aquí no se solicitan porcentajes de muestreo, cantidades de ensayos ni un plan de mediciones.")
    st.caption("Referencia: ISO/TS 19488:2021 · cláusula 6 y Anexo A informativo, A.2.1 · pp. 9–12 / PDF 15–18.")

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
    st.info("**Objetivo:** preparar los datos de los cuatro casos de A-302 para Proyecto de SONARA. Esta etapa no exige mediciones ni determinar todavía una clase acústica.")
    st.markdown("### 1 · Recorre las cuatro láminas")
    _lab_table(pd.DataFrame([
        ["AC-01 · Planta", "Ubica recintos, puertas, ventanas norte, acceso desde el pasillo y shaft. A-301 está al oeste.", "Geometría, emisor, receptor y recorridos posibles del ruido."],
        ["AC-02 · Corte", "A-402 está encima de A-302. Distingue altura libre, losa y paquete de piso.", "Relación vertical y volumen receptor."],
        ["AC-03 · Fachada", "Desde el exterior norte, oeste queda a la derecha. A-302: tercer piso, segunda vivienda desde la derecha.", "Paño FA-01 del estar y ventana V-01; V-02 pertenece al dormitorio."],
        ["AC-04 · Detalles", "Reconoce capas, espesores, juntas, bandas y fijaciones de la solución inicial.", "Composición de partida y encuentros que podrían necesitar mejoras."],
    ], columns=["Lámina", "Qué debes observar", "Para qué sirve"]))
    _download_plan_set("c5l1_s2_plans_pdf")
    tabs = st.tabs(["AC-01 · Planta", "AC-02 · Corte", "AC-03 · Fachada", "AC-04 · Detalles"])
    sheets = [
        ("planta_tipo.png", "AC-01 · Planta parcial nivel 3 · norte arriba · A-302 y estar adyacente A-301", "Sigue el acceso P-01 desde el pasillo común y comprueba las conexiones con cocina, baño, dormitorio principal y estar; desde el estar se entra al dormitorio 2. Localiza M-01, V-01, V-02 y S-1. El estar en L conserva 20,40 m² y el medianero útil 4,08 × 2,50 m."),
        ("corte_aa.png", "AC-02 · Corte A-A · cinco niveles · altura libre 2,50 m", "A-402 está sobre A-302. L-01 tiene 160 mm de hormigón y un paquete superior de 60 mm; no los sumes como losa desnuda."),
        ("fachada_norte.png", "AC-03 · Elevación norte · paño FA-01 destacado", "Vista exterior norte: A-301 queda a la derecha de A-302. Los balcones son esquemáticos: no deduzcas de ellos geometrías ni correcciones acústicas. FA-01 solo incluye el estar: 15,30 m² brutos = 10,50 m² opacos + 4,80 m² de V-01. V-02 pertenece al dormitorio."),
        ("detalles_constructivos.png", "AC-04 · M-01, L-01, F-01 y S-01 · espesores en mm", "Distingue placa, cámara, absorbente y unión. El espesor total de S-01 es 120 mm; no corresponde a cada placa."),
    ]
    for tab, (filename, caption, instruction) in zip(tabs, sheets):
        with tab:
            _show_drawing(filename, caption)
            st.info(instruction)
    st.markdown("### 2 · De la lámina al modelo de cálculo")
    matrix = [
        ["AI-01", "A-301 → A-302", "M-01", "4,08 × 2,50 = 10,20 m²", "V 51,0 m³ · HA 180 mm", "Directa + uniones laterales"],
        ["IM-01", "A-402 → A-302", "L-01", "Estar: 20,40 m²", "V 51,0 m³ · losa 160 mm", "Piso + losa + flancos"],
        ["FA-01", "Exterior → estar A-302", "F-01 + V-01", "15,30 = 10,50 + 4,80 m²", "V 51,0 m³ · DVH 6/12/4", "Componentes + juntas"],
        ["IN-01", "Descarga sanitaria → dormitorio principal A-302", "S-01 + fijaciones", "V receptor 28,8 m³", "Cierre 120 mm · área según recorrido", "Aérea + estructural"],
    ]
    _lab_table(pd.DataFrame(matrix, columns=["Caso", "Fuente / receptor", "Elemento", "Geometría útil", "Datos de partida", "Vías"]), hide_index=True, width="stretch")
    st.markdown("### 3 · Qué datos tienes y cuáles faltan")
    _lab_table(pd.DataFrame([
        ["Disponibles", "Geometría y composición inicial", "Áreas, altura libre, volúmenes y espesores. Comprueba unidades: m, m², m³ y mm."],
        ["Pendientes", "Prestaciones acústicas", "Datos espectrales de muros y ventanas, propiedades de materiales y mejora del sistema de piso. Un espesor o la indicación DVH no acreditan aislamiento."],
        ["Por completar", "Recintos y encuentros", "TR adoptado, superficies de flancos, longitudes y tipos de unión según el modelo."],
        ["Por documentar", "Exposición exterior", "Lden y condiciones de fachada; no se deducen del render ni de la orientación norte."],
        ["Según método", "Instalaciones sanitarias", "Fuente, condición de descarga, fijaciones y transmisión aérea/estructural. Identifica las magnitudes que requiere el módulo; la potencia sonora sola no caracteriza toda la instalación."],
    ], columns=["Estado", "Familia de datos", "Cómo utilizarla"]))
    st.info("Marca lo no documentado como **pendiente** o como **hipótesis justificada**, con su procedencia y efecto. En la Etapa 4 prepararás las entradas de Proyecto de SONARA. Las dimensiones describen geometría: no demuestran el aislamiento.")
    st.markdown("### 4 · Lee los planos y completa tu ficha")
    st.markdown("**¿Qué tienes que hacer?** Calcula cinco magnitudes, explica tres caminos posibles del ruido y señala tres datos que faltan para calcular en SONARA. Usa las láminas de arriba; todavía no debes calcular aislamiento.")
    st.markdown("""
    <style>
    .st-key-c5l1_s2_reading_form [data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-radius:18px!important;border:1px solid #cee0e9!important;box-shadow:0 5px 20px #16445b09;margin-bottom:18px}
    .st-key-c5l1_s2_reading_form input,.st-key-c5l1_s2_reading_form textarea{background:#f7fbfd!important;color:#143d53!important;border:1px solid #bfd5e0!important;border-radius:10px!important}
    .c5s2-head{padding:20px 22px;border-radius:14px;background:#e6f4f7;border-left:5px solid #0786a0;margin-bottom:15px}
    .c5s2-heading-row{display:flex;align-items:flex-start;gap:16px}.c5s2-heading-number{display:block;flex:0 0 48px;min-width:48px;font-size:32px;font-weight:800;line-height:1.15;color:#08788e}.c5s2-heading-copy{flex:1;min-width:0}
    .c5s2-head h3{margin:6px 0!important;font-size:23px!important;color:#123e56!important}
    .c5s2-head p{margin:0;color:#365b6e;font-size:16px;line-height:1.6}
    .c5s2-example{padding:14px 18px;background:#fff4de;border-radius:10px;border-left:4px solid #dba43d;color:#604711;margin:12px 0;font-size:15px}
    </style>
    """, unsafe_allow_html=True)
    form_values = {}
    def answer(label, key, placeholder):
        value = st.text_input(label, value=saved.get(key, ""), key=key, placeholder=placeholder)
        form_values[key] = value
        return value
    def step_head(number, title, instruction):
        st.markdown(f'<div class="c5s2-head"><div class="c5s2-heading-row"><div class="c5s2-heading-number">{int(number):02d}</div><div class="c5s2-heading-copy"><h3>{title}</h3><p>{instruction}</p></div></div></div>', unsafe_allow_html=True)
    with st.form("c5l1_s2_reading_form", border=False):
        with st.container(border=True):
            step_head("1", "Calcula áreas y volumen", "En cada campo escribe la operación y el resultado con su unidad. Las pistas indican qué dimensiones buscar.")
            geometry_prompts = [
                ("Área del muro M-01 que separa los dos estares", "Largo del muro × altura libre. Busca las cotas en AC-01 y AC-02.", "m01"),
                ("Volumen del estar-comedor de A-302", "Superficie de piso del estar × altura libre. Resultado en m³.", "volume"),
                ("Área bruta de la fachada del estar FA-01", "Ancho del paño del estar × altura libre. Incluye el espacio de la ventana.", "gross"),
                ("Área de la ventana V-01 del estar", "Ancho × alto de V-01. No incluyas la ventana V-02 del dormitorio.", "window"),
                ("Área opaca F-01: parte de fachada que no es ventana", "Área bruta FA-01 − área de V-01. Resultado en m².", "opaque"),
            ]
            geometry_answers = []
            for label, hint, code in geometry_prompts:
                st.markdown("**" + label + "**")
                st.markdown(hint)
                example = "Ejemplo de formato: 12,00 m² × 2,40 m = 28,80 m³" if code == "volume" else "Ejemplo de formato: 3,00 m × 2,00 m = 6,00 m²"
                value = answer("Tu operación y resultado", "c5l1_s2_geo_" + code, example)
                geometry_answers.append(label + ": " + value)
            st.caption("Autocomprobación: área opaca + área de ventana debe ser igual al área bruta de la fachada.")
            if saved.get("c5l1_s2_geometry") and not saved.get("c5l1_s2_geo_m01"):
                st.info("Tu respuesta anterior se conserva como referencia: " + saved["c5l1_s2_geometry"])
        with st.container(border=True):
            step_head("2", "Explica por dónde podría pasar el ruido", "Elige tres puntos del proyecto que convendría revisar. Para cada uno indica dónde está, cómo pasa el ruido y qué comprobarías.")
            st.markdown('<div class="c5s2-example"><strong>Ejemplo de razonamiento, de otro elemento:</strong> una rejilla comunica dos recintos → el sonido pasa por la abertura → revisar el recorrido y el tratamiento acústico. Escribe tus propios casos de Los Alerces.</div>', unsafe_allow_html=True)
            risk_answers = []
            for i in range(1, 4):
                st.markdown(f"##### Punto a revisar {i}")
                place = answer("¿Dónde está? · " + str(i), f"c5l1_s2_risk_{i}_place", "Indica caso, lámina y elemento: muro, piso, ventana, shaft o encuentro.")
                mechanism = answer("¿Cómo podría pasar el ruido? · " + str(i), f"c5l1_s2_risk_{i}_mechanism", "Explica el recorrido: por el elemento, por una junta o a través de la estructura.")
                action = answer("¿Qué revisarías o mejorarías? · " + str(i), f"c5l1_s2_risk_{i}_action", "Propón una comprobación o una solución relacionada con ese recorrido.")
                risk_answers.append(f"Riesgo {i}: {place} | mecanismo: {mechanism} | revisión: {action}")
            st.caption("Describe un riesgo posible. No afirmes que existe un defecto construido: estamos analizando un diseño.")
            if saved.get("c5l1_s2_findings") and not saved.get("c5l1_s2_risk_1_place"):
                st.info("Tu respuesta anterior se conserva como referencia: " + saved["c5l1_s2_findings"])
        with st.container(border=True):
            step_head("3", "Señala qué información falta", "Escoge tres datos de la tabla de pendientes. Explica para qué los necesitas y de dónde los obtendrías.")
            pending_answers = []
            for i in range(1, 4):
                st.markdown(f"##### Dato pendiente {i}")
                datum = answer("¿Qué dato necesitas y para qué caso? · " + str(i), f"c5l1_s2_pending_{i}_datum", "Nombre del dato y unidad cuando corresponda; indica AI-01, IM-01, FA-01 o IN-01.")
                purpose = answer("¿Para qué lo utilizarías? · " + str(i), f"c5l1_s2_pending_{i}_purpose", "Explica qué parte del cálculo permite completar.")
                source = answer("¿Dónde lo buscarías? · " + str(i), f"c5l1_s2_pending_{i}_source", "Ficha técnica, cálculo previo o hipótesis documentada. Puedes dejarlo pendiente.")
                pending_answers.append(f"Dato {i}: {datum} | uso: {purpose} | fuente: {source}")
            st.caption("No debes inventar el valor ni proponer cantidades de mediciones. Aquí identificas la información necesaria.")
            if saved.get("c5l1_s2_missing") and not saved.get("c5l1_s2_pending_1_datum"):
                st.info("Tu respuesta anterior se conserva como referencia: " + saved["c5l1_s2_missing"])
        st.markdown("**Antes de guardar:** cinco operaciones con unidades · tres recorridos del ruido explicados · tres datos pendientes con su fuente.")
        submitted = st.form_submit_button("Guardar mi ficha de planos", type="primary", width="stretch")
    if submitted:
        if any(not value.strip() for value in form_values.values()):
            st.warning("Completa las cinco operaciones y los tres campos de cada riesgo y dato pendiente antes de guardar.")
        else:
            _save(lab, saved, 2, c5l1_s2_geometry="\n".join(geometry_answers), c5l1_s2_findings="\n".join(risk_answers), c5l1_s2_missing="\n".join(pending_answers), **form_values)
            st.success("Ficha guardada. Estas respuestas te servirán para preparar los modelos en la Etapa 4.")



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
    _header(3, "De la predicción a la decisión de diseño", "Aprender a comparar un resultado con el objetivo A y decidir si la solución necesita rediseño.")
    st.info("**Tu siguiente tarea:** interpretar resultados. En la Etapa 1 identificaste los objetivos; en la Etapa 2 preparaste geometría, riesgos y datos pendientes. Aquí practicarás cómo decidir si una propuesta alcanza su objetivo. Todavía no debes calcular en SONARA.")
    st.markdown("### 1 · Antes de comparar, comprueba qué resultado tienes")
    _lab_table(pd.DataFrame([
        ["Caso y receptor", "¿El resultado corresponde al mismo emisor, receptor y elemento que el objetivo?", "AI-01: estar A-301 → estar A-302."],
        ["Descriptor", "¿El resultado y el límite están expresados con la misma magnitud?", "DₙT,50 se compara con DₙT,50. El Rw del muro no lo sustituye."],
        ["Condiciones", "¿Se consideran las bandas, flancos, normalización y condiciones exigidas?", "Si falta una condición necesaria, la comprobación queda pendiente."],
        ["Decisión", "¿Supera el mínimo o queda por debajo del máximo aplicable?", "Si no alcanza el objetivo, identifica la brecha y rediseña la vía pertinente."],
    ], columns=["Qué revisar", "Pregunta que debes hacerte", "Aplicación"]))
    st.markdown("### 2 · Ejemplo guiado: mejorar el separador AI-01")
    st.caption("Resultados hipotéticos para practicar la interpretación. No son cálculos de SONARA ni valores para copiar en las etapas de diseño.")
    st.markdown("Usamos el caso ya conocido: **M-01 = 10,20 m²**, estar receptor de **51,0 m³** y transmisión directa más flancos. El objetivo de la Etapa 1 es **DₙT,50 ≥ 58 dB**. Suponemos que ambos resultados siguientes están expresados correctamente y contemplan las condiciones requeridas.")
    _lab_table(pd.DataFrame([
        ["Solución inicial", "DₙT,50 = 55 dB", "55 − 58 = −3 dB", "No alcanza el objetivo: faltan 3 dB."],
        ["Propuesta rediseñada", "DₙT,50 = 59 dB", "59 − 58 = +1 dB", "Alcanza el objetivo previsto de AI-01, con 1 dB de margen."],
    ], columns=["Propuesta", "Resultado supuesto", "Margen respecto del objetivo", "Decisión de diseño"]))
    st.markdown("**¿Qué cambió?** El resultado entre recintos mejoró 4 dB. Para atribuir esa mejora a una solución, debes documentar qué cambiaste y recalcular. No basta aumentar el espesor del muro sin revisar los flancos y encuentros.")
    st.info("**Qué puedes concluir:** la variante alcanza el objetivo A de AI-01 bajo las hipótesis del ejemplo. No demuestra los resultados de IM-01, FA-01 ni IN-01, ni la clase global de la vivienda o edificio. Un margen de 1 dB merece revisar la incertidumbre y la sensibilidad del diseño; no garantiza el comportamiento construido.")

    st.markdown("### 3 · Usa la comparación correcta en cada caso")
    _lab_table(pd.DataFrame([
        ["AI-01 y FA-01 · aislamiento", "Resultado − mínimo exigido", "Positivo: supera el mínimo. Negativo: falta aislamiento."],
        ["IM-01 e IN-01 · nivel recibido", "Máximo permitido − resultado", "Positivo: queda por debajo del máximo. Negativo: el nivel es demasiado alto."],
        ["Cualquier caso", "Descriptor o condición incompletos", "No concluyas cumplimiento: completa los datos antes de decidir."],
    ], columns=["Tipo de resultado", "Cómo expresar el margen favorable", "Cómo interpretarlo"]))
    st.caption("Compara cada requisito aplicable por separado. Un margen favorable en un indicador no compensa otro requisito incumplido. En fachada, utiliza el límite correspondiente a la exposición documentada en la Etapa 1.")
    st.caption("Referencia: ISO/TS 19488:2021 · §5.2, tabla 1, fila 1 y nota a · p. 7 / PDF 13; criterios por característica en §5.2–5.5, tablas 1–4 · pp. 7–9 / PDF 13–15. Las reglas generales de alcance ya se desarrollan en la Etapa 1.")

    st.markdown("### 4 · Tu actividad: interpreta y decide")
    st.info("**Actividad de interpretación escrita:** usa los resultados del ejemplo. No necesitas abrir SONARA; compara los valores y justifica tu decisión.")
    st.markdown("A partir del ejemplo de 55 → 59 dB, explica: **qué propuesta elegirías y por qué; cuánto margen tiene; qué condiciones revisarías; y por qué ese resultado no resuelve los otros tres casos**. No se pide elegir otra clase ni repetir la teoría de clasificación global.")
    if saved.get("c5l1_s3_reason"):
        st.caption("Tu respuesta guardada se conserva. Puedes actualizarla para responder a esta actividad.")
    with st.form("c5l1_s3_scope_form"):
        target = "Clase A"
        scope = EXERCISE_SCOPE
        st.markdown("**Objetivo del proyecto: clase A · caso del ejemplo: AI-01.**")
        reason = st.text_area("Tu decisión y su justificación", value=saved.get("c5l1_s3_reason", ""), placeholder="Elijo… porque… El margen es… Antes de aceptar el diseño revisaría… Para los otros casos todavía falta…", height=180)
        submitted = st.form_submit_button("Guardar interpretación del ejemplo", type="primary", width="stretch")
    if submitted:
        if not reason.strip():
            st.warning("Explica tu elección, el margen, las condiciones que revisarías y lo que falta para los demás casos.")
        else:
            _save(lab, saved, 3, c5l1_s3_target=target, c5l1_s3_scope=scope, c5l1_s3_reason=reason)
            st.success("Interpretación guardada. En la Etapa 4 prepararás las entradas de tus modelos en Proyecto de SONARA.")


def _stage4(lab, saved):
    _header(4, "Preparar el proyecto en SONARA", "Convertir el objetivo y los planos en entradas trazables antes de calcular.")
    _show_class_a_requirements(saved)
    st.info("**Meta del proyecto: Clase A · trabajo en Proyecto de SONARA.** Aquí preparas las entradas. Los cálculos base y rediseño se desarrollan en las etapas 5–8.")
    st.markdown("### 1 · Crea y organiza los cuatro casos")
    st.markdown("""1. Entra a **Proyecto → Proyecto**, escribe **Los Alerces · tu nombre** y pulsa **Crear / actualizar proyecto**.
2. En **Recintos**, registra estar A-301 (piso 3), estar A-302 (piso 3) y estar A-402 (piso 4), cada uno con área 20,40 m² y volumen 51,0 m³; dormitorio principal A-302 (piso 3), 11,50 m² y 28,8 m³. Los emisores son definiciones académicas de la ficha, no mediciones del dibujo parcial. Comprueba V = área × altura libre (2,50 m); los volúmenes se presentan redondeados a una decimal. Añade exterior norte (sin volumen cerrado) y baño principal A-302 (4,10 m²; 10,3 m³) para instalaciones cuando corresponda.
3. En **Elementos**, selecciona emisor, receptor y tipo de elemento. Añade los casos **AI-01, IM-01, FA-01 e IN-01** con sus componentes. Los cuatro casos son el alcance de esta entrega. Pulsa **Agregar elemento a la matriz** o **Diseñar este elemento**.
4. En **Diseñar**, comprueba **Elemento activo a diseñar**, identifica la calculadora que usarás y revisa el requisito del caso. Para fachada, define el umbral una vez que justifiques el Lden.
5. En el formulario de esta etapa del **laboratorio**, registra las entradas, su procedencia y cómo compararás la base con el rediseño. Guarda la preparación.
6. En las **etapas 5–8**, calcula y guarda la base y el rediseño de cada caso en SONARA. Comprueba las variantes en **Soluciones**, reúne evidencias desde **Informe** y traslada los resultados al laboratorio de forma manual.""")
    st.info("**Requisitos de clase A:** contrasta el descriptor y el valor del requerimiento disponible en el catálogo con ISO/TS 19488:2021. La selección de una referencia o el estado de cumplimiento de SONARA no acredita por sí solo clase A. Si el catálogo no ofrece el requisito exacto, documenta la diferencia y comprueba el umbral y los requisitos adicionales en tu matriz del laboratorio.")
    st.markdown("### 2 · Datos del expediente y herramienta de cálculo")
    st.markdown("Usa tu ficha de la Etapa 2 como apoyo. Esta matriz resume geometría y composición; no acredita prestaciones acústicas.")
    _lab_table(pd.DataFrame([
        ["M-01 / AI-01", "HA 180 mm; S 10,20 m²; V 51,0 m³", "Proyecto → Diseñar → ISO 12354-1", "DₙT,w y adaptaciones finales"],
        ["L-01 / IM-01", "Losa 160; resiliente 10; sobrelosa 40; terminación 10 mm", "Proyecto → Diseñar → Ruido de impacto", "L′ₙT,w y adaptación aplicable"],
        ["F-01 + V-01 / FA-01", "10,50 m² opacos + 4,80 m² de ventana", "Proyecto → Diseñar → Fachada ISO 12354-3", "Aislamiento de fachada adaptado"],
        ["S-01 / IN-01", "2 RF 12,5 / cámara 70 / 2 RF 12,5 mm; V 28,8 m³", "Proyecto → Diseñar → Instalaciones EN 12354-5", "LAFmax,nT para la descarga intermitente"],
    ], columns=["Caso", "Datos del expediente", "Ruta SONARA", "Resultado a registrar"]), hide_index=True, width="stretch")
    st.markdown("### 3 · Planifica la comparación que harás en las etapas 5–8")
    st.markdown("""1. Usa los objetivos A mostrados arriba. Comprueba que la salida del módulo corresponda al descriptor y las condiciones requeridas.
2. Prepara la solución base y registra sus resultados.
3. Identifica el camino dominante y modifica una variable.
4. Recalcula conservando el resto de condiciones.
5. Compara con clase A, rediseña si falta desempeño y guarda la solución final y las brechas pendientes.
6. Clasifica tus propios resultados en la etapa 10.""")
    st.warning("Los valores iniciales de SONARA no son datos del proyecto. Los campos siguientes quedan vacíos hasta que elijas una ficha o declares una hipótesis. La masa de sobrelosa se calcula como densidad × 0,040 m; su capa resiliente de 10 mm no determina s′ por sí sola.")
    st.markdown("### 4 · Registra las entradas y su procedencia")
    _lab_table(pd.DataFrame([
        ["TR del estar y dormitorio", "Condición del receptor, en segundos.", "Busca un informe de reverberación o estima el TR con el volumen de la ficha y la absorción del recinto. Si adoptas un valor, indica que es una hipótesis y describe la condición del recinto."],
        ["Densidad HA", "Propiedad del material, en kg/m³.", "Busca la especificación estructural o la ficha del hormigón. Si usas una densidad nominal, cita su referencia o declárala como hipótesis."],
        ["Densidad de sobrelosa", "Masa de la capa superior del piso.", "Busca la ficha del mortero u hormigón de sobrelosa. Solo se usa en el modelo físico."],
        ["Rigidez dinámica s′", "Caracteriza la capa resiliente del piso.", "Busca s′ en MN/m³ en la ficha o ensayo de la capa resiliente seleccionada. Si usas un sistema ensayado de catálogo, deja vacíos ambos campos del piso y cita la ficha de ΔL y el montaje."],
        ["Lden exterior", "Fija el objetivo de fachada.", "Busca un mapa estratégico de ruido o estudio que informe Lden para la exposición de la fachada. Cita fuente, año y ubicación; para el proyecto ficticio puedes declarar un escenario justificado."],
    ], columns=["Entrada", "Para qué sirve", "Dónde buscar y qué registrar"]))
    st.markdown("""<style>

    [class*="st-key-c5s4_"]{background:#fff!important;border:1px solid #c9dde8!important;border-radius:16px!important;padding:20px!important;box-shadow:0 4px 15px #16445b08;margin-bottom:16px}
    .c5s4-input-title{font-size:20px;font-weight:750;color:#12475e;border-bottom:2px solid #13a0b6;padding-bottom:10px;margin-bottom:10px}
    .c5s4-input-note{font-size:14px;color:#456577;line-height:1.5;margin-bottom:16px}
    [class*="st-key-c5s4_"] [data-testid="stWidgetLabel"] p{font-size:15px!important;font-weight:600!important;color:#173f56!important}
    [class*="st-key-c5s4_"] [data-testid="stNumberInputContainer"]{background:#f0f7fb!important;border:1px solid #a8c7d7!important;border-radius:10px!important;min-height:48px}
    [class*="st-key-c5s4_"] input{background:transparent!important;color:#123e56!important;font-size:18px!important;font-weight:600!important;padding:12px!important}
    [class*="st-key-c5s4_"] input::placeholder{font-size:14px!important;font-weight:400!important;color:#5c7788!important;opacity:1}
    [class*="st-key-c5s4_"] button{color:#087c96!important}
    .st-key-c5l1_s4_protocol_form{background:#fff;border:1px solid #c9dce7;border-radius:18px;padding:22px;box-shadow:0 6px 22px #16445b0a}
    .st-key-c5l1_s4_protocol_form [data-testid="stWidgetLabel"] p{font-size:16px!important;font-weight:600!important;color:#173f56!important}.st-key-c5l1_s4_protocol_form input,.st-key-c5l1_s4_protocol_form textarea{font-size:16px!important;background:#f4f9fc!important;border:1px solid #c2d8e3!important;border-radius:10px!important}
    </style>""", unsafe_allow_html=True)
    prev = saved.get("c5l1_s4_inputs", {})
    with st.form("c5l1_s4_protocol_form", border=False):
        st.markdown("#### A · Introduce los datos de partida")
        st.markdown("Registra el valor que utilizarás y explica su origen en el apartado B. **TR** significa tiempo de reverberación; **HA**, hormigón armado. La densidad de sobrelosa y la rigidez dinámica corresponden al modelo físico del piso; si no lo utilizas, déjalas vacías y explica el motivo.")
        inputs = {}
        def input_card(column, key, title, subtitle, fields):
            with column:
                with st.container(border=True, key=key):
                    st.markdown(f'<div class="c5s4-input-title">{title}</div><div class="c5s4-input-note">{subtitle}</div>', unsafe_allow_html=True)
                    for name, label, minimum, step, hint in fields:
                        inputs[name] = st.number_input(label, min_value=minimum, value=prev.get(name), step=step, placeholder=hint)
        left, right = st.columns(2)
        input_card(left, "c5s4_rooms", "Recintos receptores", "Tiempo de reverberación adoptado · segundos", [
            ("tr_stay", "TR estar [s]", .1, .1, "Introduce el TR del estar"),
            ("tr_bedroom", "TR dormitorio [s]", .1, .1, "Introduce el TR del dormitorio"),
        ])
        input_card(right, "c5s4_concrete", "Hormigón estructural", "Densidad del material de partida · kg/m³", [
            ("rho_ha", "Densidad HA [kg/m³]", 500., 50., "Introduce la densidad del hormigón"),
        ])
        left, right = st.columns(2)
        input_card(left, "c5s4_floor", "Sistema de piso", "Solo para el modelo físico · deja vacío si utilizas catálogo", [
            ("rho_screed", "Densidad sobrelosa [kg/m³]", 100., 50., "Densidad de la sobrelosa"),
            ("dynamic_stiffness", "Rigidez dinámica s′ [MN/m³] · si usas piso físico", .1, .5, "Rigidez de la capa resiliente"),
        ])
        input_card(right, "c5s4_exterior", "Exposición exterior", "Dato que determina el objetivo de fachada · dB", [
            ("lden", "Exposición exterior Lden [dB]", 0., 1., "Introduce tu Lden documentado"),
        ])
        st.markdown("#### B · Explica de dónde salen los datos")
        st.markdown("**Para cada valor indica:** nombre del dato, valor y unidad, fuente y motivo de elección. Si es una hipótesis, identifícala; si falta información, déjala señalada como pendiente.")
        input_sources = st.text_area("Fuentes de datos, hipótesis y antecedentes pendientes", value=saved.get("c5l1_s4_sources", ""), placeholder="Dato: … | Valor y unidad: … | Fuente: … | Justificación: …\nPendiente: …", height=140)
        st.markdown("**Cómo comprobarás los cuatro casos:** explica qué resultado buscarás en SONARA y cómo lo compararás con el objetivo A de la tabla superior. Para fachada, utiliza el límite correspondiente a tu Lden. Si el módulo no entrega un indicador necesario, señala qué falta.")
        criteria = st.text_area("Criterios de diseño que comprobarás en cada caso", value=saved.get("c5l1_s4_criteria", ""), placeholder="AI-01: resultado que buscaré y comparación…\nIM-01: los dos indicadores que comprobaré…\nFA-01: exposición adoptada y límite…\nIN-01: máximo normalizado y condición de descarga…", height=140)
        st.markdown("#### C · Organiza tus cálculos y evidencias")
        st.markdown("Explica cómo distinguirás la solución inicial de la propuesta mejorada, qué cambiarás y qué condiciones mantendrás para compararlas. Indica qué resultados, curvas o capturas guardarás.")
        protocol = st.text_area("Protocolo personal de cálculo", value=saved.get("c5l1_s4_protocol", ""), placeholder="Nombres Base/Variante, capturas, curvas, unidades, condiciones que mantendrás y cómo justificarás los cambios.", height=130)
        submitted = st.form_submit_button("Guardar preparación del proyecto", type="primary", width="stretch")
    if submitted:
        if inputs["tr_stay"] is None or inputs["tr_bedroom"] is None or inputs["rho_ha"] is None or inputs["lden"] is None:
            st.warning("Define TR del estar y dormitorio, densidad HA y exposición exterior; justifica los restantes datos según el modelo elegido.")
        elif not all(value.strip() for value in (input_sources, criteria, protocol)):
            st.warning("Completa las fuentes, cómo comprobarás los objetivos y cómo organizarás base y rediseño.")
        elif inputs["dynamic_stiffness"] is not None and inputs["rho_screed"] is None:
            st.warning("Si utilizas s′ para el modelo físico, registra también la densidad de sobrelosa.")
        else:
            _save(lab, saved, 4, c5l1_s4_inputs=inputs, c5l1_s4_sources=input_sources, c5l1_s4_criteria=criteria, c5l1_s4_protocol=protocol)
            st.success("Entradas guardadas; se recuperarán en las etapas 5–8.")
    _sonara_button("Abrir SONARA y preparar Los Alerces")


def _stage5(lab, saved):
    _header(5, "Diseño frente a ruido aéreo entre viviendas", "Modelar el muro separador y los caminos laterales del caso AI-01.")
    _result_form(
        lab, saved, 5, "Aéreo interior",
        [("c", "C de la variante", "dB"), ("ctr", "Ctr de la variante", "dB")],
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
    st.markdown("### Condición de operación · ejemplo docente IN-01")
    st.markdown(
        "Simula **una descarga de WC de 6 L** en el baño principal A-302, con un evento "
        "de **10 s como hipótesis** y sin otras descargas ni artefactos funcionando a la vez. "
        "Evalúa el instante de mayor emisión de la descarga en el dormitorio principal A-302. "
        "Mantén la misma operación al comparar la base y la variante."
    )
    st.caption(
        "El ejemplo usa potencia sonora hipotética por octavas y modela la vía aérea a través de S-01. "
        "La duración describe la operación y no se usa para convertir niveles. "
        "Para evaluar el máximo FAST real o sumar la vía estructural necesitas antecedentes específicos de la descarga y del montaje."
    )
    st.markdown("### Entradas de SONARA · supuestos de las soluciones docentes")
    st.info(
        "Selecciona «Aérea · recinto adyacente» para activar R del separador y su área. "
        "En «Aérea · mismo recinto», SONARA estima el ruido en el recinto donde está la fuente."
    )
    _lab_table(pd.DataFrame([
        ["Tipo de funcionamiento", "Intermitente (LAFmax estimado)"],
        ["Vía de transmisión", "Aérea · recinto adyacente"],
        ["Distancia y directividad Q", "Se dejaron en 2,00 m y 2,00. Esta vía no los utiliza."],
        ["Absorción equivalente fuente", "1,50 m² · hipótesis didáctica"],
        ["Absorción equivalente receptor", "9,22 m² · estimada con 0,16 × 28,8 / 0,50"],
        ["TR receptor", "0,50 s · hipótesis didáctica. SONARA normaliza a T₀ = 0,50 s."],
        ["Área del separador S-01", "3,00 m² · hipótesis didáctica"],
        ["Vías adicionales", "0 · la vía estructural queda sin cuantificar"],
    ], columns=["Campo de SONARA", "Entrada para ambas corridas"]), hide_index=True, width="stretch")
    st.markdown(
        "El cierre S-01 tiene **dos placas RF de 12,5 mm por cara y una cámara de 70 mm**. "
        "Para estimar R se usó como proxy acústico yeso USG Sheetrock Firecode C de ½ pulgada, "
        "ajustado a 12,5 mm, con montante simple y fijaciones cada 600 mm. "
        "La base tiene cámara vacía y la variante incorpora lana mineral de 60 kg/m³."
    )
    _lab_table(pd.DataFrame([
        ["63", "70", "5,4", "7,7", "0"],
        ["125", "68", "13,0", "16,0", "0"],
        ["250", "66", "32,1", "35,1", "0"],
        ["500", "64", "48,8", "51,8", "0"],
        ["1.000", "61", "64,5", "66,0", "0"],
        ["2.000", "58", "73,6", "74,7", "0"],
        ["4.000", "55", "57,8", "58,9", "0"],
    ], columns=["Banda [Hz]", "Lw hipotético [dB re 1 pW]", "R base [dB]", "R variante [dB]", "Atenuación adicional [dB]"]), hide_index=True, width="stretch")
    st.caption(
        "Calcula primero con la columna R base. Para la variante, sustituye solo R del separador. "
        "Compara el LAFmax,nT proyectado de ambas corridas con la meta de 26 dB(A). "
        "Los Lw son hipotéticos y los R provienen del modelo por bandas de S-01."
    )
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
        ("AI-01", "Aéreo interior", "dnt50", "DₙT,50 proyectado · variante", "dB"),
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






