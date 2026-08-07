"""Configuración académica y de navegación de los laboratorios.

Este módulo contiene únicamente datos y constantes. No ejecuta Streamlit ni
accede a Supabase, para que pueda importarse sin efectos secundarios.
"""

COURSE_ID = "diplomado-acustica-edificacion"

ACADEMIC_COURSES = [
    {
        "title": "Aislamiento acústico al ruido aéreo",
        "labs": [
            {"number": 1, "opens_at": "2026-07-25T00:00:00-04:00", "implemented": True},
            {"number": 2, "opens_at": "2026-07-31T00:00:00-04:00", "implemented": True},
        ],
    },
    {
        "title": "Control de ruido de impacto y ruido de instalaciones",
        "labs": [
            {"number": 1, "opens_at": "2026-08-22T00:00:00-04:00", "implemented": False},
            {"number": 2, "opens_at": "2026-08-29T00:00:00-04:00", "implemented": False},
        ],
    },
    {
        "title": "Control de ruido ambiental",
        "labs": [
            {"number": 1, "opens_at": "2026-09-12T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-09-26T00:00:00-03:00", "implemented": False},
        ],
    },
    {
        "title": "Factores del ruido en el proceso de construcción",
        "labs": [
            {"number": 1, "opens_at": "2026-10-10T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-10-17T00:00:00-03:00", "implemented": False},
        ],
    },
    {
        "title": "Certificaciones acústicas en la edificación residencial",
        "labs": [
            {"number": 1, "opens_at": "2026-11-07T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-11-14T00:00:00-03:00", "implemented": False},
        ],
    },
]

LABORATORIES = {
    1: {
        "id": "clase-01-aislamiento-ruido-aereo",
        "title": "Laboratorio 1",
        "description": "",
        "stages": list(range(11)),
    },
    2: {
        "id": "clase-02-aislamiento-ruido-aereo-minvu",
        "title": "Laboratorio 2",
        "description": "",
        "stages": list(range(11)),
    },
}

APPLICATION_POINTS = {
    3: {"s3q1": 2, "s3q2": 2, "s3q3": 2, "s3q4": 2, "s3q5": 2},
    5: {"s5q1": 4, "s5q2": 3, "s5q3": 3},
    7: {"minvu_guided": 20, "s7q1": 2, "s7q2": 2, "s7q3": 2, "s7q4": 2, "s7q5": 2, "s7q6": 2, "s7q7": 2, "s7q8": 2, "s7q9": 1, "s7q10": 1, "s7q11": 2},
    9: {"e9_pairs": 20},
    10: {"final_exam": 100},
}

APPLICATION_TOTAL = sum(sum(stage.values()) for stage in APPLICATION_POINTS.values())

LAB_POINT_SCHEMAS = {
    1: {stage: APPLICATION_POINTS[stage] for stage in [3, 5, 7, 9, 10]},
    2: {
        6: {"direccion_guiada": 10},
        7: {"compare_solutions": 10},
        8: {"compound_door": 10},
        9: {"final_comprehension": 40},
        10: {"final_integrated_design": 60},
    },
}

LAB_ACTIVITY_STAGES = {1: [3, 5, 7, 9], 2: [6, 7, 8]}

# Actividades formativas que cuentan para el porcentaje de avance del alumno.
# Incluye preguntas de comprensión comprobables y ejercicios guardados, pero no
# las evaluaciones oficiales del Laboratorio 2 (Etapas 9 y 10).
FORMATIVE_PROGRESS_KEYS = {
    1: {
        1: ["e1"],
        2: ["e2_sabine_check", "e2_lab_1", "e2_lab_2"],
        3: ["s3q1", "s3q2", "s3q3", "s3q4", "s3q5"],
        4: ["e4_flow", "e4_payback", "e4_roi", "e4_decision"],
        5: ["s5_decision_case", "e5", "s5q1", "s5q2", "s5q3"],
        6: ["e6", "e6_tau_practical", "e6_comp_practical"],
        7: [
            "e7_guided_tau", "e7_guided_result", "s7q4_interpretation",
            "minvu_guided", "s7q1", "s7q2", "s7q3", "s7q4", "s7q5",
            "s7q6", "s7q7", "s7q8", "s7q9", "s7q10", "s7q11",
        ],
        8: ["e8"],
        9: ["e9_pairs"],
    },
    2: {
        1: [f"lab2_s1_q{i}" for i in range(1, 6)],
        2: [f"lab2_s2_q{i}" for i in range(1, 6)],
        3: ["lab2_s3_design_decision", *[f"lab2_s3_compare_q{i}" for i in range(1, 6)]],
        4: ["lab2_s4_analysis", *[f"lab2_s4_q{i}" for i in range(1, 6)]],
        5: [f"lab2_s5_q{i}" for i in range(1, 6)],
        6: ["direccion_guiada", *[f"lab2_s6_q{i}" for i in range(1, 6)]],
        7: ["compare_solutions", *[f"lab2_s7_q{i}" for i in range(1, 6)]],
        8: ["compound_door", *[f"lab2_s8_q{i}" for i in range(1, 6)]],
    },
}

FINAL_EXAM_STAGE = 10

STAGES = [
("Etapa 0","Introducción y ruta del curso"),
("Etapa 1","Control del ruido: fuente, trayectoria y receptor"),
("Etapa 2","Aislamiento y absorción acústica"),
("Etapa 3","Aplicación: absorción, reverberación e inteligibilidad"),
("Etapa 4","Aislamiento y análisis costo-beneficio"),
("Etapa 5","Aplicación conceptual técnico-económica"),
("Etapa 6","Fundamentos físicos del aislamiento acústico"),
("Etapa 7","Aplicación práctica del aislamiento acústico"),
("Etapa 8","Índices de aislamiento acústico"),
("Etapa 9","Aplicación práctica de los índices"),
("Etapa 10","Evaluación final · Aislamiento a Ruido Aéreo"),
]

STAGE_MINUTES = {0:10, 1:20, 2:25, 3:20, 4:20, 5:15, 6:30, 7:25, 8:20, 9:20, 10:25}

BREAK_AFTER_STAGE = 5

BREAK_MINUTES = 10

TOTAL_CLASS_MINUTES = sum(STAGE_MINUTES.values()) + BREAK_MINUTES

STAGE_GUIDE = {
0:("🧭","CONOCERÁS","La ruta completa del laboratorio y el propósito profesional de cada etapa.",
   "🎯","AL FINAL","Sabrás qué aprenderás, cómo experimentarás y cómo se evaluará tu avance.",
   "⏱️","RECORRIDO","240 minutos totales: 230 de trabajo guiado y una pausa de 10 minutos."),
1:("🏭","COMPRENDERÁS","Fuente, trayectoria y receptor; propagación aérea, estructural, directa e indirecta.",
   "🧪","EXPERIMENTARÁS","Encapsulado, barrera, separación física, cabina, fachada y protección auditiva sobre una escena dinámica.",
   "✅","APLICARÁS","La intervención correcta según el lugar donde nace, viaja o se recibe el ruido."),
2:("🧱","DIFERENCIARÁS","Aislamiento, absorción, reverberación e inteligibilidad sin confundir sus funciones.",
   "🔊","OBSERVARÁS","Qué energía se refleja, absorbe y transmite entre dos recintos.",
   "📐","CALCULARÁS","Cómo la absorción equivalente modifica el tiempo de reverberación."),
3:("🏫","RESOLVERÁS","Casos de acondicionamiento de aulas, reuniones y recintos con ruido exterior.",
   "🧮","CALCULARÁS","Absorción equivalente y tiempo de reverberación con la ecuación de Sabine.",
   "💬","INTERPRETARÁS","La relación entre reverberación, ruido de fondo y claridad de la palabra."),
4:("💰","COMPRENDERÁS","Costo total, rendimiento decreciente, ROI, recuperación y punto de equilibrio.",
   "📊","COMPARARÁS","Mejora acústica, inversión, mantención, vida útil y beneficios evitados.",
   "🎯","DECIDIRÁS","Solo entre soluciones que primero cumplen la meta acústica."),
5:("⚖️","ANALIZARÁS","Alternativas técnico-económicas bajo una meta acústica común.",
   "📈","EVALUARÁS","Costo del ciclo, ROI, payback, riesgo y suficiencia técnica.",
   "✅","RECOMENDARÁS","La opción justificable, no simplemente la más barata o la de mayor aislamiento."),
6:("🌊","COMPRENDERÁS","Transmisión, ley de masa, resonancia, coincidencia y sistemas dobles.",
   "🧪","EXPERIMENTARÁS","Masa, frecuencia, cámaras, absorbentes, sellos y elementos débiles.",
   "📉","INTERPRETARÁS","Curvas por bandas y las causas físicas de sus valles y pendientes."),
7:("🛠️","RESOLVERÁS","Ejercicios prácticos de cerramientos simples, dobles y compuestos.",
   "🔎","DIAGNOSTICARÁS","La banda crítica, el elemento débil y la vía dominante.",
   "✅","VERIFICARÁS","El cumplimiento de una meta sin sobredimensionar componentes secundarios."),
8:("📏","CONOCERÁS","R, Rw, C, Ctr, STC, OITC e índices de laboratorio, terreno y fachada.",
   "🗂️","INTERPRETARÁS","Fichas técnicas, normas, contextos y adaptaciones espectrales.",
   "🎯","SELECCIONARÁS","El indicador que representa correctamente la fuente y el problema real."),
9:("📉","CALCULARÁS","Rw mediante la curva de referencia y sus desviaciones desfavorables.",
   "🔄","COMPARARÁS","Particiones con igual índice global pero distinto comportamiento espectral.",
   "✅","DECIDIRÁS","Según voz, tránsito, bajas frecuencias, laboratorio o terreno."),
10:("📝","RESPONDERÁS","29 preguntas teórico-aplicadas de todas las etapas.",
    "🏢","RESOLVERÁS","Un caso profesional con T60, bandas críticas e índices acústicos.",
    "💰","JUSTIFICARÁS","La solución final mediante desempeño, costo, vida útil y objetivo de diseño."),
}

ROUTE_SUMMARIES = [
("Fuente, trayectoria y receptor","Ubica dónde nace el ruido, cómo viaja y dónde conviene intervenir."),
("Aislamiento y absorción","Distingue transmisión entre recintos de reflexiones y reverberación interior."),
("Aplicación acústica interior","Calcula T₆₀ y mejora la inteligibilidad mediante decisiones concretas."),
("Costo-beneficio","Relaciona meta acústica, inversión, ROI, vida útil y costos evitados."),
("Decisión técnico-económica","Compara alternativas y descarta las que no cumplen técnicamente."),
("Fundamentos físicos","Explora masa, frecuencia, resonancia, coincidencia y sistemas dobles."),
("Diseño práctico","Detecta bandas críticas, elementos débiles y vías dominantes."),
("Índices acústicos","Interpreta Rw, C, Ctr, STC, OITC y resultados de terreno."),
("Aplicación de índices","Trabaja con curvas, desviaciones, fuentes y fichas técnicas."),
("Evaluación final","Integra acústica y costo-beneficio en una decisión profesional."),
]

STAGE_INTROS = {
3:("Ahora aplicarás lo aprendido","Identifica el fenómeno, clasifica la intervención y responde cada ejercicio en pantalla. La retroalimentación te mostrará por qué una opción es correcta."),
5:("Decidir exige dos filtros","Primero comprueba el desempeño acústico; después compara inversión, vida útil, ROI y costo del ciclo."),
7:("Diseño guiado por la banda crítica","Modifica el cerramiento y el elemento débil. La curva mostrará qué banda y qué vía dominan el nivel receptor."),
9:("Del espectro al indicador","Trabaja con curvas por bandas antes de tomar una decisión basada en Rw, C, Ctr, STC u OITC."),
10:("Evaluación final","Responde 29 preguntas de alternativas y un caso integrador directamente en pantalla."),
}

LAB2_MINUTES = [10, 15, 25, 15, 20, 20, 10, 15, 20, 20, 40]

LAB2_BREAK_AFTER_STAGE = 5

LAB2_BREAK_MINUTES = 30

LAB2_ACTIVE_MINUTES = sum(LAB2_MINUTES)

LAB2_TOTAL_MINUTES = LAB2_ACTIVE_MINUTES + LAB2_BREAK_MINUTES

LAB1_STAGE_TITLES = [
    ("Etapa 0","Introducción y ruta del curso"),
    ("Etapa 1","Control del ruido: fuente, trayectoria y receptor"),
    ("Etapa 2","Aislamiento y absorción acústica"),
    ("Etapa 3","Aplicación: absorción, reverberación e inteligibilidad"),
    ("Etapa 4","Aislamiento y análisis costo-beneficio"),
    ("Etapa 5","Aplicación conceptual técnico-económica"),
    ("Etapa 6","Fundamentos físicos del aislamiento acústico"),
    ("Etapa 7","Aplicación práctica del aislamiento acústico"),
    ("Etapa 8","Índices de aislamiento acústico"),
    ("Etapa 9","Aplicación práctica de los índices"),
    ("Etapa 10","Evaluación final del Laboratorio 1"),
]

LAB2_STAGE_TITLES = [
    ("Etapa 0","Ruta completa del Laboratorio 2"),
    ("Etapa 1","Pérdida de transmisión: energía, τ y TL"),
    ("Etapa 2","Panel simple: incidencia y cuatro zonas"),
    ("Etapa 3","Comparación aplicada de placas simples"),
    ("Etapa 4","Pérdida de transmisión en paneles dobles"),
    ("Etapa 5","Modelo de Sharp: TL por tramos"),
    ("Etapa 6","Pérdida de transmisión en ventanas dobles"),
    ("Etapa 7","Bandas de frecuencia: octavas y tercios"),
    ("Etapa 8","Número único Rw, C y Ctr"),
    ("Etapa 9","Evaluación final · Preguntas de comprensión"),
    ("Etapa 10","Aplicación integradora · segunda mitad"),
]

LAB_STAGE_TITLES = {1: LAB1_STAGE_TITLES, 2: LAB2_STAGE_TITLES}
