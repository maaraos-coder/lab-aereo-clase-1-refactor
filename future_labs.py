"""Contenido académico de los laboratorios 3 a 10.

Cada laboratorio usa identificadores propios y once etapas. El contenido fue
reorganizado desde el programa, las presentaciones MAB y las guías de trabajo.
"""

COURSE_LABS = [
    {
        "course": "Control de ruido de impacto y ruido de instalaciones",
        "course_short": "IMPACTO E INSTALACIONES",
        "labs": [
            {
                "number": 1,
                "class_number": 3,
                "id": "clase-03-impacto-instalaciones-lab-1",
                "opens_at": "2026-08-22T00:00:00-04:00",
                "source": "Clase 3",
                "focus": "Transmisión estructural, descriptores y diagnóstico",
                "stages": [
                    ("Ruta y diagnóstico inicial", "Distinguir ruido aéreo, de impacto y estructural antes de elegir una solución.", "Una fuente excita una estructura; la vibración se propaga por uniones rígidas y vuelve a radiarse como sonido en el recinto receptor.", "Clasifica pisadas, bomba, descarga sanitaria y conversación según mecanismo dominante."),
                    ("Fuente, estructura y receptor", "Seguir la cadena completa de transmisión.", "La transmisión directa ocurre por el elemento excitado; el flanqueo utiliza muros, vigas, pilares o encuentros. Una solución eficaz debe interrumpir la trayectoria dominante.", "Marca fuente, camino directo, flancos y receptor en un caso de losa entre viviendas."),
                    ("Magnitudes vibratorias", "Interpretar velocidad, aceleración y nivel vibratorio.", "La velocidad vibratoria describe el movimiento de la superficie; el nivel Lv se expresa respecto de una referencia. La aceleración es útil para caracterizar equipos y respuesta estructural.", "Calcula un nivel relativo a partir de una velocidad eficaz y explica qué significa."),
                    ("Ruido de impacto normalizado", "Comprender Ln, LnT y L'nT.", "Los niveles de impacto se corrigen para reducir la influencia del recinto receptor. Ln usa absorción equivalente de referencia; LnT usa tiempo de reverberación de referencia. En terreno aparece la prima por transmisión aparente.", "Elige el descriptor correcto para laboratorio y para terreno."),
                    ("Normalización por reverberación", "Aplicar la corrección sin invertir su sentido.", "Si el recinto receptor reverbera más, el nivel medido aumenta. La corrección normaliza el resultado a condiciones de referencia y debe aplicarse por bandas.", "Corrige tres bandas con T medido y T0, mostrando sustitución y unidad."),
                    ("Lectura espectral", "Detectar bandas críticas y mecanismos.", "Un único número resume, pero la curva revela bajas frecuencias, resonancias y flancos. Dos pisos con igual índice ponderado pueden percibirse de forma distinta.", "Compara dos espectros y selecciona la solución más robusta."),
                    ("Instrumentación", "Seleccionar cadena de medición y control de calidad.", "La cadena incluye máquina de impactos, sonómetro clase 1, calibrador, fuente para TR y, cuando corresponda, acelerómetro. Se documentan posiciones, fondo, calibración y geometría.", "Ordena el procedimiento de verificación antes, durante y después de medir."),
                    ("Aplicación: piso flotante", "Relacionar mejora de impacto con desacoplamiento.", "Un piso flotante funciona por resiliencia y separación. Los puentes rígidos perimetrales pueden anular gran parte de la mejora.", "Diagnostica cuatro detalles constructivos y encuentra el puente acústico."),
                    ("Aplicación: equipo mecánico", "Diseñar control de vibraciones en instalaciones.", "La selección de aisladores depende de masa, frecuencia de excitación y frecuencia natural. Un aislador mal seleccionado puede amplificar cerca de resonancia.", "Compara apoyos rígidos, neopreno y resortes para una bomba."),
                    ("Caso profesional", "Integrar medición, diagnóstico y recomendación.", "El informe debe separar evidencia, incertidumbre, mecanismo dominante, criterio y medida verificable.", "Redacta una conclusión técnica para un reclamo por impactos y bomba de agua."),
                    ("Evaluación individual", "Demostrar dominio conceptual y aplicado.", "Evaluación de 100 puntos con descriptores, cálculo por bandas, instrumentación, diagnóstico y control.", "Resuelve el caso individual y entrega desarrollo trazable."),
                ],
            },
            {
                "number": 2,
                "class_number": 4,
                "id": "clase-04-impacto-instalaciones-lab-2",
                "opens_at": "2026-08-29T00:00:00-04:00",
                "source": "Clase 4",
                "focus": "Medición, ponderación, normativa y diseño de control",
                "stages": [
                    ("Ruta de medición", "Planificar una campaña reproducible.", "Se define objetivo, descriptor, elemento bajo ensayo, recintos, posiciones y criterio antes de encender instrumentos.", "Construye el plan de medición de una losa de departamentos."),
                    ("Laboratorio y terreno", "No confundir Ln,w con L'nT,w.", "El laboratorio caracteriza el elemento bajo condiciones controladas; el terreno incorpora encuentros, ejecución y flancos.", "Asocia cada símbolo con lugar, corrección y finalidad."),
                    ("ISO 16283-2", "Aplicar el método de terreno.", "La medición combina posiciones de máquina y micrófono, niveles por bandas, ruido de fondo y TR. La representatividad requiere distribución espacial.", "Detecta errores en un montaje con una sola posición."),
                    ("ISO 717-2", "Obtener el índice ponderado.", "La curva de referencia se desplaza según desviaciones desfavorables; para impacto, menor nivel representa mejor desempeño.", "Ajusta la curva y determina el índice único."),
                    ("Términos CI", "Interpretar bajas frecuencias.", "CI y CI,50-2500 complementan el índice ponderado; no son mejoras que se suman arbitrariamente a una solución.", "Compara dos pisos con igual Ln,w y distinto CI."),
                    ("Reducción ΔL", "Cuantificar un revestimiento de piso.", "ΔL compara una losa de referencia con y sin revestimiento bajo condiciones normalizadas. No equivale automáticamente al desempeño final de cualquier losa.", "Calcula ΔL por bandas y discute su transferibilidad."),
                    ("Soluciones constructivas", "Vincular mecanismo y detalle.", "Pisos flotantes, mantas resilientes, cielos suspendidos y encuentros elásticos actúan en trayectorias distintas.", "Selecciona un paquete de control para vivienda y justifica."),
                    ("Ruido de instalaciones", "Evaluar fuentes continuas e intermitentes.", "Bombas, ascensores, HVAC y descargas requieren considerar nivel continuo, máximo, tonalidad, impulsividad y horario según el criterio aplicable.", "Escoge descriptores para cuatro instalaciones."),
                    ("Aislación vibratoria", "Evitar resonancia y puentes rígidos.", "La transmisibilidad depende de la razón entre frecuencia de excitación y natural y del amortiguamiento. La aislación efectiva exige separación suficiente de resonancia.", "Calcula la razón de frecuencias y decide si el sistema aísla."),
                    ("Caso losa 160 mm", "Resolver el caso de la presentación corregido.", "Se procesan bandas, TR, índice ponderado, incertidumbre y alternativas; la recomendación incluye control de ejecución.", "Entrega tabla, curva, conclusión y solución."),
                    ("Evaluación individual", "Integrar medición y diseño.", "Caso de impacto e instalaciones con rúbrica de 100 puntos y soluciones ocultas.", "Resuelve sin reutilizar el caso guiado."),
                ],
            },
        ],
    },
    {
        "course": "Control de ruido ambiental",
        "course_short": "RUIDO AMBIENTAL",
        "labs": [
            {
                "number": 1,
                "class_number": 5,
                "id": "clase-05-ruido-ambiental-lab-1",
                "opens_at": "2026-09-12T00:00:00-03:00",
                "source": "Clase 5",
                "focus": "Descriptores, campañas, salud y análisis de casos",
                "stages": [
                    ("Ruta y conceptos", "Diferenciar sonido, ruido y contaminación acústica.", "El ruido ambiental se caracteriza por nivel, tiempo, espectro, contexto y respuesta humana; no basta una cifra aislada.", "Define el problema de un barrio mixto."),
                    ("Suma energética", "Calcular LAeq correctamente.", "Los decibeles son logarítmicos: los intervalos se combinan energéticamente y se ponderan por duración.", "Calcula LAeq de cuatro intervalos de 15 minutos."),
                    ("Percentiles", "Interpretar L10 y L90.", "L10 representa niveles excedidos durante 10 % del tiempo y suele reflejar eventos; L90 aproxima el fondo estable cuando la fuente y el contexto lo permiten.", "Interpreta una diferencia L10–L90 de 20 dB."),
                    ("Eventos y SEL", "Normalizar energía de eventos.", "SEL concentra la energía de un evento en un segundo de referencia y permite comparar eventos de distinta duración.", "Calcula SEL de un camión y una bocina."),
                    ("Día, tarde y noche", "Calcular Lden sin promediar aritméticamente.", "Lden integra periodos con penalizaciones convencionales de tarde y noche; su uso depende del marco de evaluación.", "Calcula Lden con 12 h, 4 h y 8 h."),
                    ("Efectos y molestia", "Comunicar riesgo sin confundir guía y límite legal.", "Las guías sanitarias, curvas dosis–respuesta y normas legales cumplen funciones distintas. Toda comparación debe indicar fuente, periodo e indicador.", "Clasifica afirmaciones como guía, evidencia o exigencia."),
                    ("Instrumentación", "Diseñar una cadena de medición trazable.", "Sonómetro, calibrador, pantalla antiviento, meteorología, ubicación y registro temporal forman parte del dato.", "Detecta cinco fallas en una campaña."),
                    ("Diseño de campaña", "Seleccionar puntos y horarios representativos.", "La estrategia depende del objetivo: cumplimiento de una fuente, diagnóstico urbano o exposición comunitaria.", "Diseña puntos para vivienda, escuela y vía arterial."),
                    ("Caso grupo electrógeno", "Procesar espectros exterior–interior.", "Se convierten bandas Z a A energéticamente, se comparan puntos y se distingue diferencia de niveles de aislamiento de un criterio de exposición.", "Calcula el peor caso y propone una medida en fachada."),
                    ("Priorización de control", "Pasar de datos a decisión.", "Una buena medida identifica la fuente dominante, la reducción necesaria, viabilidad y verificación posterior.", "Prioriza tres medidas para el barrio mixto."),
                    ("Evaluación individual", "Resolver un caso integral.", "Evaluación de 100 puntos con LAeq, percentiles, SEL, Lden, campaña y conclusión.", "Entrega cálculo, interpretación y plan de control."),
                ],
            },
            {
                "number": 2,
                "class_number": 6,
                "id": "clase-06-ruido-ambiental-lab-2",
                "opens_at": "2026-09-26T00:00:00-03:00",
                "source": "Clase 6",
                "focus": "Trabajo de campo, percepción y tráfico",
                "stages": [
                    ("Ruta de terreno", "Preparar una salida segura y comparable.", "El teléfono puede apoyar aprendizaje y reconocimiento, pero no sustituye un sonómetro calibrado para cumplimiento.", "Distingue ejercicio didáctico de medición reglamentaria."),
                    ("Paisaje sonoro", "Registrar percepción y contexto.", "La valoración del ambiente acústico integra fuentes dominantes, agradabilidad, actividad y expectativa.", "Completa una ficha de escucha de cinco minutos."),
                    ("Aplicaciones móviles", "Reconocer límites metrológicos.", "Micrófono, calibración, rango, procesamiento y dispositivo condicionan el resultado. La app no convierte automáticamente el teléfono en instrumento normativo.", "Compara Sound Meter X y un sonómetro clase 1."),
                    ("Protocolo de punto fijo", "Estandarizar ubicación y registro.", "Se documentan coordenadas, altura, distancia a fachadas, clima, duración, fuentes y eventos.", "Ordena una ficha de campaña."),
                    ("Tráfico vehicular", "Relacionar flujo, composición y nivel.", "El nivel depende del caudal, velocidad, pesados, pavimento, pendiente y propagación.", "Explica por qué duplicar vehículos no duplica dB."),
                    ("Conteo sincronizado", "Alinear acústica y tránsito.", "El conteo por categorías debe cubrir exactamente el mismo intervalo que el registro sonoro.", "Corrige una tabla desfasada."),
                    ("Comparación de lugares", "Usar métricas consistentes.", "La comparación requiere misma duración, ponderación, condiciones y tratamiento de eventos atípicos.", "Compara tres entornos y justifica."),
                    ("Mapa de observación", "Representar datos sin falsa precisión.", "Un mapa didáctico muestra patrones; un mapa estratégico requiere modelación, entradas verificadas y validación.", "Ubica puntos y zonas de incertidumbre."),
                    ("Calidad del dato", "Identificar sesgos y repetir cuando corresponde.", "Viento, lluvia, manipulación, voz del observador y saturación pueden invalidar muestras.", "Decide qué registros conservar."),
                    ("Informe de terreno", "Comunicar método, resultados y límites.", "El informe separa observación, medición indicativa y conclusión reglamentaria.", "Redacta resultados sin sobreafirmar."),
                    ("Evaluación individual", "Diseñar y defender una campaña.", "Caso de tráfico con datos, percepción, control de calidad y propuesta.", "Entrega ficha y análisis individual."),
                ],
            },
        ],
    },
    {
        "course": "Factores del ruido en el proceso de construcción",
        "course_short": "RUIDO EN CONSTRUCCIÓN",
        "labs": [
            {
                "number": 1,
                "class_number": 7,
                "id": "clase-07-construccion-lab-1",
                "opens_at": "2026-10-10T00:00:00-03:00",
                "source": "Curso 4 · Bloques 1 y 2",
                "focus": "Fuentes, fases, propagación y estimación",
                "stages": [
                    ("Ruta de obra", "Relacionar fase, equipo y receptor.", "La emisión cambia con excavación, estructura, terminaciones y logística; el escenario crítico no siempre coincide con la mayor potencia nominal.", "Construye una línea de tiempo de fuentes."),
                    ("Inventario de equipos", "Caracterizar fuente y ciclo de trabajo.", "Se registran potencia sonora o nivel de referencia, cantidad, ubicación, altura, directividad y porcentaje de uso.", "Completa una ficha de excavadora, camión y martillo."),
                    ("Lp y Lw", "No confundir nivel de presión y potencia.", "Lw caracteriza emisión; Lp depende además de distancia, geometría y ambiente. No se trasladan como si fueran la misma magnitud.", "Identifica la magnitud correcta en tres fichas."),
                    ("Propagación geométrica", "Estimar atenuación con distancia.", "Para fuente puntual ideal en campo libre, duplicar distancia reduce aproximadamente 6 dB; otras geometrías y reflexiones cambian el comportamiento.", "Calcula niveles a 10, 20 y 40 m."),
                    ("Suma de equipos", "Combinar fuentes simultáneas.", "Los niveles se suman energéticamente y deben ajustarse por cantidad y tiempo de operación.", "Combina tres equipos con ciclos distintos."),
                    ("Barreras y terreno", "Evaluar interrupción de línea de vista.", "La eficacia depende de geometría, frecuencia, estanqueidad y trayectorias laterales; la masa por sí sola no basta.", "Compara dos ubicaciones de barrera."),
                    ("Fachadas receptoras", "Estimar exposición exterior e interior.", "La orientación, aberturas y desempeño de fachada condicionan el nivel interior; la diferencia medida no debe llamarse Rw.", "Calcula un escenario con ventana abierta y cerrada."),
                    ("Fases críticas", "Priorizar por duración y sensibilidad.", "Un evento alto y breve y una actividad moderada prolongada requieren criterios y controles diferentes.", "Ordena actividades por riesgo."),
                    ("Modelo simplificado", "Documentar supuestos e incertidumbre.", "La predicción preliminar debe declarar datos de entrada, correcciones, simultaneidad y margen.", "Completa una hoja de cálculo guiada."),
                    ("Caso de planificación", "Diseñar el control antes de iniciar.", "Se combinan logística, horario, equipo de menor emisión, barrera y comunicación comunitaria.", "Propón un plan para excavación junto a viviendas."),
                    ("Evaluación individual", "Resolver una predicción de obra.", "Caso de 100 puntos con fuentes, distancias, simultaneidad, barrera y decisión.", "Entrega desarrollo y medidas."),
                ],
            },
            {
                "number": 2,
                "class_number": 8,
                "id": "clase-08-construccion-lab-2",
                "opens_at": "2026-10-17T00:00:00-03:00",
                "source": "Curso 4 · Bloque 3, tareas y evaluación",
                "focus": "Gestión, monitoreo, control y comunicación",
                "stages": [
                    ("Ruta de gestión", "Integrar prevención, seguimiento y respuesta.", "El plan eficaz define responsabilidades, criterios, controles, monitoreo y escalamiento.", "Asigna responsables a cada acción."),
                    ("Jerarquía de control", "Actuar primero donde el control es más eficaz.", "Sustitución, control en fuente, trayectoria, gestión temporal y receptor se combinan según el caso.", "Clasifica doce medidas."),
                    ("Selección de equipos", "Incorporar emisión en compras y arriendos.", "La comparación debe usar magnitudes y condiciones equivalentes, no solo potencia del motor.", "Elige entre tres equipos."),
                    ("Planificación horaria", "Reducir exposición y conflicto.", "Se consideran sensibilidad del receptor, duración, simultaneidad y comunicación; horario permitido no significa ausencia de molestia.", "Diseña una semana de faenas."),
                    ("Barreras temporales", "Especificar continuidad y geometría.", "Una barrera efectiva evita huecos, supera la línea de vista y se aproxima a fuente o receptor.", "Detecta fallas de montaje."),
                    ("Monitoreo", "Definir alertas útiles.", "El monitoreo puede ser diagnóstico, de gestión o de cumplimiento. Umbrales y ventanas temporales deben responder al objetivo.", "Configura un tablero de alertas."),
                    ("Eventos impulsivos", "Gestionar perforación y golpes.", "El carácter impulsivo exige identificar eventos, técnica constructiva y alternativas de menor impacto.", "Compara corte, perforación y demolición."),
                    ("Relación comunitaria", "Responder con evidencia y trazabilidad.", "Aviso previo, canal único, registro y retroalimentación reducen incertidumbre, pero no reemplazan el control físico.", "Redacta un aviso responsable."),
                    ("Plan de contingencia", "Escalar cuando el control falla.", "Se detiene, verifica, corrige, documenta y reanuda bajo condiciones definidas.", "Construye un flujo de decisión."),
                    ("Caso integral", "Aplicar los tres bloques del curso.", "El caso reúne cronograma, predicción, control, monitoreo y comunicación.", "Desarrolla un plan para obra urbana."),
                    ("Evaluación individual", "Defender un plan de gestión.", "Evaluación basada en los ejercicios, tareas y caso equivalente del Curso 4.", "Entrega matriz y conclusión."),
                ],
            },
        ],
    },
    {
        "course": "Certificaciones acústicas en la edificación residencial",
        "course_short": "CERTIFICACIONES ACÚSTICAS",
        "labs": [
            {
                "number": 1,
                "class_number": 9,
                "id": "clase-09-certificaciones-lab-1",
                "opens_at": "2026-11-07T00:00:00-03:00",
                "source": "Clase 9",
                "focus": "Índices, clasificación y muestreo",
                "stages": [
                    ("Ruta de clasificación", "Comprender qué se clasifica y para qué.", "Una clase comunica desempeño bajo un esquema definido; no reemplaza las curvas ni el informe de ensayo.", "Identifica usuarios y decisiones."),
                    ("Familias de índices", "Separar aéreo, impacto, fachada e instalaciones.", "Cada familia utiliza magnitudes, métodos y sentidos de desempeño distintos.", "Asocia ocho índices."),
                    ("Laboratorio y terreno", "Distinguir Rw, R'w y DnT,w.", "Rw caracteriza elemento en laboratorio; R'w es aparente; DnT,w caracteriza diferencia estandarizada entre recintos.", "Corrige una ficha técnica."),
                    ("Fachadas", "Interpretar D2m,nT,w y términos espectrales.", "La medición de fachada incluye nivel exterior a posición definida e interior corregido; Ctr representa sensibilidad a espectros con contenido grave.", "Selecciona indicador para avenida."),
                    ("Impacto", "Interpretar L'nT,w en sentido correcto.", "En impacto, valores menores representan mejor desempeño. No debe mezclarse la lógica de clases con aislamiento aéreo.", "Ordena tres soluciones."),
                    ("Instalaciones", "Usar LAeq y LAmax con condiciones declaradas.", "El tipo de fuente y el método de operación condicionan el resultado.", "Elige descriptor para ascensor y ventilación."),
                    ("Curvas ISO 717", "Obtener números únicos sin promediar.", "La curva de referencia se ajusta mediante desviaciones; el valor único no es promedio aritmético.", "Ajusta una curva."),
                    ("Tipologías y muestreo", "Evitar generalizaciones indebidas.", "La clasificación de edificio requiere reglas de muestreo y representatividad del esquema específico; no puede afirmarse una regla universal sin revisar la norma.", "Diseña muestras por tipología."),
                    ("Comparación normativa", "No inventar equivalencias entre esquemas.", "ISO/TS 19488, UNE y NCh pueden diferir en clases, indicadores, alcance y agregación. Las tablas deben verificarse en la edición aplicable.", "Compara estructura, no números memorizados."),
                    ("Caso de edificio", "Integrar categorías y tipologías.", "Se determina clase por resultado y se aplica la regla global definida por el esquema, documentando excepciones.", "Clasifica un edificio simulado."),
                    ("Evaluación individual", "Aplicar índices y clasificación.", "Caso de 100 puntos con curvas, tipologías y conclusión.", "Entrega trazabilidad normativa."),
                ],
            },
            {
                "number": 2,
                "class_number": 10,
                "id": "clase-10-certificaciones-lab-2",
                "opens_at": "2026-11-14T00:00:00-03:00",
                "source": "Clase 10",
                "focus": "CES, verificación y expediente de certificación",
                "stages": [
                    ("Ruta CES", "Ubicar la acústica dentro del sistema.", "CES evalúa edificios de uso público y articula requerimientos obligatorios y voluntarios; no es una certificación residencial.", "Distingue CES de clasificación residencial."),
                    ("Actores y etapas", "Comprender responsabilidades.", "Mandante, asesor, evaluador y entidad administradora participan en etapas de diseño, construcción y verificación.", "Asigna entregables."),
                    ("Requisitos acústicos", "Ordenar fachada, interiores, instalaciones y acondicionamiento.", "Cada requerimiento posee alcance, indicador, evidencia y condición de evaluación propios.", "Construye una matriz de cumplimiento."),
                    ("NED y fachada", "Determinar exposición con método trazable.", "La exposición puede provenir de medición, mapas o categorías cuando el manual lo admita; debe usarse la versión vigente.", "Elige método para tres proyectos."),
                    ("Diseño de envolvente", "Controlar componentes débiles.", "Ventanas, puertas, rejillas, sellos y encuentros dominan el desempeño compuesto.", "Calcula fachada compuesta."),
                    ("Aislamiento interior", "Especificar el índice correcto.", "El requisito debe expresar magnitud, valor, recinto, método y condición; Rw de producto no reemplaza DnT,A de edificio.", "Reescribe una especificación."),
                    ("Impacto e instalaciones", "Integrar disciplinas.", "Los detalles de losa, equipos y ductos deben coordinarse para evitar puentes rígidos y ruido de servicio.", "Revisa una coordinación BIM simulada."),
                    ("Reverberación y STI", "Conectar acondicionamiento con uso.", "TR y STI evalúan aspectos distintos y dependen de ocupación, ruido de fondo y geometría. Sabine es una aproximación bajo supuestos.", "Calcula absorción requerida y discute límites."),
                    ("Evidencias", "Preparar documentación verificable.", "Memorias, fichas, ensayos, planos, especificaciones, inspecciones y mediciones deben ser coherentes entre sí.", "Detecta documentos faltantes."),
                    ("Caso asesor CES", "Cerrar brechas antes de evaluación.", "El asesor compara requisito, diseño, evidencia y riesgo de obra y propone acciones verificables.", "Completa una revisión de sala y fachada."),
                    ("Evaluación final", "Resolver un expediente equivalente.", "Evaluación individual de 100 puntos con fachada, interior, impacto, instalaciones y acondicionamiento.", "Entrega decisión y lista de evidencias."),
                ],
            },
        ],
    },
]

FUTURE_LABS = {}
for course_index, course in enumerate(COURSE_LABS, start=1):
    for lab in course["labs"]:
        lab["course_index"] = course_index
        lab["course"] = course["course"]
        lab["course_short"] = course["course_short"]
        FUTURE_LABS[lab["id"]] = lab

