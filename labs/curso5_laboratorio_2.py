"""Curso 5 · Laboratorio 2: proyecto residencial real, meta ISO/TS 19488 Clase B.

Las etapas 0–8 son formativas; la 9 evalúa 30 puntos y la 10 consolida
una entrega de desarrollo de 70 puntos para evaluación docente.
Los cálculos acústicos se realizan en SONARA, no en esta aplicación.
"""
from __future__ import annotations
import json
import math
from copy import deepcopy
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

CLASS_ID = "clase-10-certificaciones-lab-2"
SONARA_URL = "https://sonara-ea1b.onrender.com/"
PROJECT = "Edificio Chimbote · Torre A"
SITE = "Piso 5 · hilera sur · tercer departamento desde poniente · CH-A-P05-S03"
ANNEX_URL = "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/blob/curso3-lab2-etapas-3-10/docs/curso5_lab2_chimbote_ficha_geometrica_alumno.md"
MATERIALS_URL = "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/blob/curso3-lab2-etapas-3-10/docs/curso5_lab2_chimbote_especificaciones_alumno.md"
BASE_CONSTRUCTION = [
 {"Código":"M-01","Caso":"AI-01","Elemento":"Muro entre viviendas","Composición original":"Hormigón armado 180 mm; densidad 2.400 kg/m³","Montaje":"Encuentros rígidos; sin trasdosado"},
 {"Código":"L-01","Caso":"IM-01","Elemento":"Losa entre viviendas","Composición original":"HA 160 mm + mortero 30 mm + cerámica 10 mm","Montaje":"Sin capa resiliente ni cielo suspendido"},
 {"Código":"F-01","Caso":"FA-01","Elemento":"Fachada opaca","Composición original":"HA 150 mm; densidad 2.400 kg/m³","Montaje":"Sin trasdosado"},
 {"Código":"V-01","Caso":"FA-01","Elemento":"Ventana","Composición original":"DVH 4/12/4 mm con marco aluminio","Montaje":"Sin curva de ensayo del conjunto"},
 {"Código":"S-01","Caso":"IN-01","Elemento":"Cierre sanitario","Composición original":"Yeso-cartón 12,5 mm/cara + perfil 70 mm + lana mineral 50 mm","Montaje":"Fijaciones convencionales"},
 {"Código":"IS-01","Caso":"IN-01","Elemento":"Descarga sanitaria","Composición original":"PVC DN110 y descarga WC 6 L de vivienda superior (piso 6)","Montaje":"Abrazaderas rígidas y recorrido hacia dormitorio receptor de piso 5 como hipótesis docente"},
 {"Código":"T-01","Caso":"TR","Elemento":"Piso estar","Composición original":"Cerámica adherida","Montaje":"Alfa por banda a documentar"},
 {"Código":"T-02","Caso":"TR","Elemento":"Muros y cielo","Composición original":"Pintura sobre superficies rígidas","Montaje":"Alfa por banda a documentar"},
 {"Código":"T-03","Caso":"TR","Elemento":"Piso dormitorio","Composición original":"Laminado sin aporte resiliente acreditado","Montaje":"Alfa por banda a documentar"},
]
# Presets genéricos verificables en SONARA, app.py → app_reverberacion_iso.
# Son datos académicos de cálculo, no fichas de ensayo del acabado.
TR_OCTAVE_BANDS = (125, 250, 500, 1000, 2000, 4000)
TR_SONARA_PRESETS = {
    "Hormigón / superficie dura": (0.01, 0.01, 0.02, 0.02, 0.02, 0.03),
    "Yeso pintado": (0.10, 0.05, 0.04, 0.07, 0.09, 0.10),
    "Vidrio": (0.18, 0.06, 0.04, 0.03, 0.02, 0.02),
    "Alfombra": (0.08, 0.24, 0.57, 0.69, 0.71, 0.73),
    "Cielo acústico": (0.45, 0.70, 0.85, 0.90, 0.90, 0.85),
    "Panel de lana mineral": (0.35, 0.80, 0.95, 1.00, 1.00, 1.00),
    # Fuente NBR 12179:1992, tabla reproducida en artículo de acústica UFRJ:
    # https://www.scielo.br/j/ac/a/yNvTbGMXxGxBYVbWYzDk3mP/
    # Incorporado asimismo en SONARA/main, no producto ensayado de Chimbote.
    "Puerta de madera maciza": (0.14, 0.10, 0.06, 0.08, 0.10, 0.10),
}
GEOMETRY_ASSUMPTIONS = [
 ("DOC-01", "Planta tipo", "Parte 1 · PDF página 8 · verificar cotas del caso seleccionado"),
 ("DOC-02", "Corte general", "Parte 1 · PDF página 12 · verificar altura libre del recinto"),
 ("DOC-03", "Elevación sur Torre A", "Parte 2 · página 5 · fachada del estar, cotejar con planta tipo"),
]
ACOUSTIC_ASSUMPTIONS = [
 ("AC-01", "Reverberación", "Se calcula por banda en SONARA: NO se entrega TR"),
 ("AC-02", "Exposición exterior de ejercicio", "Lden 60 dB, supuesto docente no medido"),
 ("AC-03", "Descarga", "WC 6 L, un evento"),
 ("AC-04", "Lw octavas 63-4000 Hz", "70 / 68 / 66 / 64 / 61 / 58 / 55 dB (ficticio)"),
]
STANDARD = "ISO/TS 19488:2021"
CASES = {
    "AI-01": ("Aislamiento aéreo entre viviendas", "DₙT,w y adaptación espectral aplicable", "Muro separador y flancos"),
    "IM-01": ("Ruido de impacto de vivienda superior", "L′ₙT,w y término de baja frecuencia aplicable", "Losa, piso y transmisiones laterales"),
    "FA-01": ("Aislamiento de fachada", "D₂m,nT,w y adaptación apropiada", "Paño opaco, ventana y sellos"),
    "IN-01": ("Ruido de instalaciones", "LAeq,nT o LAFmax,nT según la operación", "Fuente, fijaciones, vías aérea y estructural"),
}
STAGES = [
 ("Bienvenida y ruta de aprendizaje", "Conocer las actividades y la metodología del laboratorio."),
 ("Encargo profesional y reconocimiento del proyecto", "Conocer el Edificio Chimbote, descargar el expediente y definir los requisitos de Clase B."),
 ("Ficha geométrica del alumno", "Cuantificar cotas, superficies, alturas y volúmenes de los recintos asignados por el laboratorio."),
 ("Sistemas constructivos y datos de SONARA", "Documentar materiales, uniones, tiempos y condiciones."),
 ("Diseño acústico aéreo", "Comparar modelo original y variante en SONARA."),
 ("Diseño de ruido de impacto", "Comparar losa y solución resiliente en SONARA."),
 ("Diseño de fachada", "Calcular fachada compuesta y variante en SONARA."),
 ("Diseño de instalaciones", "Modelar operación y vías de transmisión en SONARA."),
 ("Matriz de resultados y Clase B", "Verificar cada descriptor sin automatizar la clasificación ISO."),
 ("Evaluación oficial de comprensión", "Diez preguntas, treinta puntos y envío definitivo."),
 ("Informe integrador evaluado", "Entrega técnica de setenta puntos para revisión docente."),
]
TEACHER = {
 0: "Etapa de bienvenida: explicar la ruta y la metodología, sin entregar todavía el encargo ni los documentos. El expediente y el caso de estudio se presentan en la Etapa 1.",
 1: "Presentar el proyecto Chimbote y la unidad CH-A-P05-S03; verificar localización en el plano, descargar los antecedentes y distinguir el proyecto real de los supuestos académicos. Comprobar criterios de Clase B de ISO/TS 19488:2021 con descriptor, valor, dirección y referencia, sin entregar solución.",
 2: "Los recintos están fijados por el encargo: el muro estar poniente–dormitorio se aprecia en la planta tipo; pisos 5 y 6 están cubiertos por la planta tipo 3–16. Verificar dimensiones y uniones reales, paños de fachada sur y modelar instalación sanitaria sin presuponer transmisión directa por un tabique. NO copiar cotas de otros departamentos.",
 3: "Materialidad original académica M-01 L-01 F-01 V-01 S-01 IS-01 T-01 T-02 T-03. Revisar superficies interiores, absorciones por banda y cálculo del TR en SONARA: no adoptar TR prefijado.",
 4: "Comprobar el registro de geometría ISO 12354-1 (S, V y recintos), M-01 de HA 180 mm y 432 kg/m² nominales, encuentros y flancos, TR por banda del dormitorio y resultados originales/mejorados de SONARA. Rw, R′w y DnT,w no son intercambiables. Exigir comparación con el descriptor y la meta Clase B determinados en Etapa 1, sin inventar valores de una simulación no realizada.",
 5: "Verificar geometría de la losa superior IM-01 recuperada de Etapa 2, TR por bandas de Etapa 3, modelo original L-01, uniones, solución libre y JSON de SONARA. Clase B exige L′nT,w ≤ 50 dB Y L′nT,50 ≤ 54 dB simultáneamente (ISO/TS 19488:2021 Tabla 2); una reducción del nivel es una mejora. El resultado es una predicción, no una medición.",
 6: "Verificar el JSON obligatorio y la secuencia NoiseMap: eje de Pasaje Chimbote, polígono de edificio, receptor exterior frente a fachada sur a altura de piso 5, auditoría geométrica válida, categorías 1/2/3/4a/4b, tres períodos y JSON trazable. No aplicar -3 dB al resultado incidente; evaluar límites del motor educativo antes de revisar paños, vanos, curva ventana-marco-sello y SONARA.",
 7: "Descarga WC de vivienda distinta (piso 6) → dormitorio receptor piso 5. Para ruido intermitente de vivienda vecina verificar LAF,max,nT ≤30 dB(A), ISO/TS 19488:2021 Tabla 4 Clase B; la predicción no acredita cumplimiento sin modelar las vías aérea y estructural.",
 8: "Comparar con los requisitos reales de Clase B determinados por el alumno; no automatizar la certificación global.",
 9: "Cuestionario oficial de 10 preguntas × 3 puntos; verificar persistencia de entrega.",
 10: "Rúbrica oficial 70 puntos; revisión docente del expediente, trazabilidad, SONARA y limitaciones.",
}
RUBRIC = [
 ("Expediente y trazabilidad",8),("Ficha geométrica",12),
 ("Datos constructivos y supuestos",8),("Diseño aéreo",10),
 ("Diseño de impacto",10),("Diseño de fachada",8),
 ("Diseño de instalaciones",8),("Clasificación, informe y limitaciones",6),
]
QUIZ = [
    ("¿Por qué dos pares de recintos con el mismo muro separador pueden presentar distinto DₙT,w?",
     ("Porque el DₙT,w depende solo del área del muro.",
      "Porque también influyen las vías laterales y la geometría de los recintos.",
      "Porque la normalización a un TR de referencia elimina la transmisión directa."),
     1, "El Rw caracteriza al elemento. El DₙT,w caracteriza la diferencia de niveles estandarizada entre recintos, donde también contribuyen los flancos."),
    ("¿Qué efecto tiene aumentar Kᵢⱼ en una unión si las demás entradas del modelo se mantienen?",
     ("Aumenta la transmisión vibratoria por esa unión.",
      "Aumenta el Rw del elemento separador.",
      "Disminuye la transmisión vibratoria por esa unión."),
     2, "Un Kᵢⱼ mayor representa una mayor reducción de la transmisión vibratoria entre los elementos de la unión."),
    ("¿Qué aporta C₅₀₋₃₁₅₀ al sumarse a DₙT,w?",
     ("Una adaptación espectral que incorpora el comportamiento desde 50 Hz.",
      "Una corrección por el ruido de fondo durante la medición.",
      "Una corrección que convierte el aislamiento del separador en el del conjunto."),
     0, "La adaptación utiliza un espectro de referencia y amplía la evaluación hacia las bajas frecuencias."),
    ("¿Por qué un puente rígido perimetral puede reducir la eficacia de un piso flotante?",
     ("Porque aumenta la absorción sonora en el recinto emisor.",
      "Porque permite que parte de la vibración evite la capa resiliente.",
      "Porque modifica el tiempo de reverberación de referencia."),
     1, "El contacto rígido crea un camino mecánico que transmite vibración alrededor del desacople."),
    ("¿Por qué una reducción de L′ₙT,w no garantiza la misma reducción de L′ₙT,50?",
     ("Porque ambos descriptores se obtienen de recintos diferentes.",
      "Porque L′ₙT,50 es el promedio de los niveles de presión sonora sin estandarizar.",
      "Porque una intervención puede mejorar unas bandas más que otras y cambiar la adaptación espectral."),
     2, "La mejora puede ser distinta en bajas frecuencias. La adaptación espectral recoge parte de esa diferencia."),
    ("¿Cómo se combinan las contribuciones del paño opaco y la ventana al calcular la reducción acústica de una fachada compuesta?",
     ("Se suman los factores de transmisión ponderados por las áreas y se convierten a decibelios.",
      "Se promedian aritméticamente los índices en decibelios ponderados por las áreas.",
      "Se adopta el mayor índice de reducción de los dos componentes."),
     0, "Las contribuciones se combinan en energía. Un componente con menor aislamiento puede dominar aun si ocupa menos área."),
    ("¿Qué define un Lden incidente en fachada en relación con las reflexiones?",
     ("Incluye la reflexión del propio muro receptor y excluye la de los edificios vecinos.",
      "Excluye la reflexión de la propia fachada receptora y puede incluir otras reflexiones.",
      "Excluye toda reflexión del entorno, como en campo libre."),
     1, "El carácter incidente se refiere a la exclusión de la reflexión de la fachada evaluada."),
    ("¿Por qué el nivel nocturno recibe mayor ponderación que el diurno al calcular Lden?",
     ("Porque el cálculo supone que por la noche siempre hay más fuentes activas.",
      "Porque el nivel nocturno se suma aritméticamente al nivel diurno.",
      "Porque se aplica una penalización al nivel nocturno antes de combinar las energías de los períodos."),
     2, "La ponderación nocturna forma parte de la definición del indicador. La combinación también considera la duración de cada período."),
    ("¿Qué diferencia a LAFmax,nT de LAeq,nT para un evento intermitente?",
     ("LAFmax,nT describe el máximo con ponderación temporal F y LAeq,nT el promedio energético del intervalo.",
      "LAFmax,nT es el promedio energético y LAeq,nT el máximo con ponderación temporal F.",
      "Ambos representan el mismo máximo después de estandarizar la reverberación."),
     0, "Estandarizar la reverberación no convierte un promedio energético en un máximo temporal."),
    ("¿Qué permite concluir una predicción de diseño cuando alcanza todos los requisitos acústicos aplicables de una clase?",
     ("Que el desempeño construido queda verificado por el cálculo.",
      "Que el diseño alcanza la meta bajo las hipótesis modeladas y el desempeño en obra requiere verificación.",
      "Que las incertidumbres de materiales, montaje y flancos quedan eliminadas."),
     1, "La predicción depende de las entradas y de cómo se construya la solución. La verificación en obra comprueba el desempeño real."),
]

def _bind(runtime):
    for k,v in runtime.items():
        if k not in {"run_stage","_bind","CLASS_ID","STAGES","TEACHER"}:
            globals()[k]=v

def _is_teacher():
    return st.session_state.get("role")=="Docente" and not bool(st.session_state.get("projection_mode"))

def _readonly():
    return bool(st.session_state.get("projection_mode"))

def _plans_archive_path(folder):
    """Prefer the updated six-sheet original plans package, then legacy ZIP."""
    for name in (
        "Chimbote_Torre_A_CH-A-P05-S03_planos_6_laminas.zip",
        "Chimbote_Torre_A_CH-A-P05-S03_planos.zip",
    ):
        candidate = folder / name
        if candidate.is_file():
            return candidate
    return None


def _plans_pdf_bytes(folder):
    """Read original plan PDF or the PDF held in a published archive."""
    filename = "Chimbote_Torre_A_CH-A-P05-S03_planos.pdf"
    direct = folder / filename
    archive = _plans_archive_path(folder)
    if archive is not None:
        with ZipFile(archive, "r") as bundle:
            entry = bundle.getinfo(filename)
            if entry.file_size > 60_000_000:
                raise ValueError("El PDF de planos supera el límite de seguridad.")
            data = bundle.read(entry)
        if not data.startswith(b"%PDF-"):
            raise ValueError("El ZIP de planos no contiene un PDF válido.")
        return data
    if direct.is_file():
        return direct.read_bytes()
    return None


def _student_document_pack():
    """Create a single download with the original Chimbote PDF and student annexes."""
    root = Path(__file__).resolve().parent.parent
    folder = root / "assets" / "curso5_lab2"
    plans_pdf = _plans_pdf_bytes(folder)
    if plans_pdf is None:
        return None, "Falta publicar el PDF o ZIP original de planos en assets/curso5_lab2."
    docs = [
        root / "docs" / "curso5_lab2_chimbote_ficha_geometrica_alumno.md",
        root / "docs" / "curso5_lab2_chimbote_especificaciones_alumno.md",
        root / "docs" / "curso5_lab2_chimbote_suplemento_cotas_alumno.md",
        root / "docs" / "curso5_lab2_chimbote_trafico_lden_alumno.md",
    ]
    for doc in docs:
        if not doc.is_file():
            return None, "Falta el documento " + doc.name
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as bundle:
        bundle.writestr("01_Planos/Chimbote_Torre_A_CH-A-P05-S03_planos.pdf", plans_pdf)
        for doc in docs:
            bundle.write(doc, arcname="02_Anexos_MD/" + doc.name)
        for pdf in sorted(folder.glob("0[1-4]_*.pdf")):
            bundle.write(pdf, arcname="03_Anexos_PDF/" + pdf.name)
        bundle.writestr("LEEME.txt",
            "Curso 5 Laboratorio 2 - Edificio Chimbote - Torre A - CH-A-P05-S03\\n"
            "Tercer departamento desde poniente de hilera sur, piso 5.\\n"
            "La materialidad indicada es academica. El alumno calcula geometria y reverberacion en SONARA.\\n"
            "El paquete no incluye la pauta docente ni requisitos normativos resueltos.\\n")
    return output.getvalue(), None


def _header(stage):
    title,objective=STAGES[stage]
    header(f"ETAPA {stage} · LABORATORIO 2",title,objective,show_overview=False,duration_minutes=25 if stage<9 else 40)
    # Mantener la portada limpia: los datos del caso se presentan en el encargo
    # y las referencias a los planos, en los apartados correspondientes.
    if stage in range(4,9):
        st.link_button("Abrir SONARA · cálculos acústicos",SONARA_URL, use_container_width=False)


def _save(lab,saved,stage,key,value,*,complete=True):
    if st.session_state.get("print_mode"):
        return False
    if _readonly() and not st.session_state.get("c5l2_projection_unlocked"):
        st.info("Habilita el guardado docente para conservar el avance de la clase.")
        return False
    try:
        json.dumps(value, allow_nan=False)
    except (ValueError, TypeError):
        st.error("Hay datos que no se pueden guardar. Revisa los valores y archivos JSON de esta etapa.")
        return False
    candidate=deepcopy(saved)
    changed = candidate.get(key) != value
    candidate[key]=value
    if complete:
        candidate[f"done_{stage}"]=True
    elif changed:
        # A draft never grants completion. Previously completed stages are
        # reopened only when their actual submitted content changes.
        candidate[f"done_{stage}"]=False
    candidate[f"c5l2_updated_{stage}"]=_now()
    try:
        _save_future_state(lab["id"],candidate)
    except Exception:
        st.error("No se pudo confirmar el guardado. Conserva tus respuestas y vuelve a intentarlo.")
        return False
    saved.update(candidate)
    if complete:
        st.success("Etapa completada y guardada. Puedes continuar con la siguiente etapa.")
    else:
        st.success("Avance guardado. Puedes continuar más tarde sin perder tus respuestas.")
    return True

def _table(rows,columns,key):
    import pandas as pd
    df=pd.DataFrame(rows or [{}],columns=columns)
    return st.data_editor(df,num_rows="dynamic",hide_index=True,use_container_width=True,key=key).fillna("").to_dict("records")

def _plain(stage,lab,saved,section,fields):
    _header(stage)
    st.markdown("### Trabajo del estudiante")
    st.info(section)
    old=saved.get(f"c5l2_s{stage}") or {}
    with st.form(f"c5l2_form_{stage}"):
        values={}
        for key,label,help_text in fields:
            values[key]=st.text_area(label,value=old.get(key,""),help=help_text,height=110)
        submitted=st.form_submit_button("Guardar etapa",type="primary")
    if submitted:
        if any(len(str(v).strip())<15 for v in values.values()):
            st.warning("Completa cada apartado con una descripción técnica de al menos 15 caracteres.")
        else:_save(lab,saved,stage,f"c5l2_s{stage}",values)

def _stage0(lab, saved):
    """Bienvenida y ruta de aprendizaje, consistente con los demás laboratorios."""
    import html

    stage_minutes = [10, 25, 35, 40, 45, 45, 55, 40, 35, 30, 45]
    active_minutes = sum(stage_minutes[1:])
    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 2 · Diseño acústico de una vivienda",
        "Una ruta profesional desde los planos del Edificio Chimbote hasta la evaluación de soluciones de Clase B conforme a ISO/TS 19488:2021.",
        show_overview=False,
        duration_minutes=stage_minutes[0],
    )

    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Ruta guiada del Laboratorio 2</strong>'
        f'<br><span>Edificio Chimbote · Meta de diseño Clase B · SONARA + NoiseMap</span>'
        f'</div><div><strong>{active_minutes} min</strong></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )
    descriptions = [
        "Recibe el encargo del Edificio Chimbote, descarga planos y anexos, reconoce la vivienda y define los criterios de Clase B.",
        "Obtén de planos las superficies, alturas, volúmenes, vanos y adyacencias de los recintos seleccionados.",
        "Registra sistemas constructivos, materiales, datos de entrada y tiempos de reverberación calculados en SONARA.",
        "Modela el aislamiento aéreo original, incorpora flancos y propone una variante constructiva verificable.",
        "Modela el ruido de impacto de la losa y comprueba la mejora de una solución resiliente.",
        "Estima la exposición al tránsito en NoiseMap y diseña en SONARA la fachada y sus vanos.",
        "Caracteriza la operación de instalaciones, las vías de transmisión y posibles medidas correctivas.",
        "Consolida resultados, contrasta cada descriptor con la meta Clase B y declara las limitaciones.",
        "Responde la evaluación oficial de comprensión: diez preguntas, con un máximo de 30 puntos.",
        "Integra las evidencias de diseño y entrega el informe técnico para evaluación docente (70 puntos).",
    ]
    cards = ""
    for stage in range(1, 11):
        title = lab["stages"][stage][0] if len(lab.get("stages", [])) > stage else STAGES[stage][0]
        cards += (
            '<div class="route-card">'
            f'<span class="step">{stage}</span><div>'
            f'<b>{html.escape(str(title))}</b>'
            f'<p>{html.escape(descriptions[stage - 1])}</p>'
            f'<span class="route-time">⏱️ {stage_minutes[stage]} min</span>'
            '</div></div>'
        )
    st.markdown(f'<div class="route-grid">{cards}</div>', unsafe_allow_html=True)

    st.success(
        "Resultado esperado: expediente de diseño de la vivienda CH-A-P05-S03, "
        "modelaciones y variantes justificadas, matriz comparativa con los requisitos "
        "de Clase B e informe técnico integrador."
    )
    st.info(
        "Bienvenida: consulta el recorrido completo y las herramientas. "
        "En la Etapa 1 recibirás el encargo profesional, la presentación "
        "del proyecto, los planos y la documentación complementaria."
    )
    st.warning(
        "Continuidad del trabajo: guarda cada etapa antes de cambiar de sección "
        "y conserva una copia de tus archivos de modelación. Las etapas siguientes "
        "recuperarán los antecedentes guardados."
    )


def _stage1(lab,saved):
    _header(1)

    st.markdown("### A · Encargo profesional y presentación del proyecto")
    st.markdown(
        """
        <div style="border:1px solid #cfe0ef;border-radius:18px;padding:18px 20px;
        background:linear-gradient(135deg,#f8fcff,#edf6fb);margin:.75rem 0 1rem">
          <div style="font-size:.70rem;font-weight:900;letter-spacing:.08em;color:#087ba0">
            ENCARGO · DISEÑO ACÚSTICO RESIDENCIAL CLASE B
          </div>
          <div style="font-size:1.15rem;font-weight:900;color:#173b53;margin:.35rem 0">
            Edificio Chimbote · Torre A
          </div>
          <div style="color:#527083;line-height:1.65;font-size:.90rem">
            Actuarás como especialista responsable de analizar una vivienda del
            proyecto y proponer soluciones constructivas que permitan satisfacer
            los requisitos acústicos de <strong>Clase B</strong> de ISO/TS 19488:2021.
            Se estudiarán el aislamiento aéreo entre viviendas, el ruido de impacto,
            el aislamiento de fachada y el ruido de instalaciones. La propuesta debe
            respaldarse con planos, hipótesis trazables, modelaciones y una
            comparación técnica de la condición original con la mejorada.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### Vista general de Torre A")
    # Render ilustrativo; nunca es fuente de cotas ni de localización precisa.
    render_path = Path(__file__).resolve().parent.parent / "assets" / "curso5_lab2" / "chimbote_torre_a_render.png"
    if render_path.is_file():
        st.image(str(render_path), use_container_width=True)
        st.caption(
            "Figura 1 · Vista conceptual de Torre A frente a Pasaje Chimbote. "
            "No representa exactamente las fachadas ni permite obtener dimensiones. "
            "La ubicación de la vivienda se verifica exclusivamente en los planos originales."
        )

    st.markdown("#### Ubicación de la vivienda de estudio · planta original intervenida")
    st.markdown(
        "La unidad seleccionada debe reconocerse **en la planta original**. "
         "El render es únicamente una representación conceptual; "
        "no se utiliza para obtener cotas, superficies ni dimensiones."
    )
    highlighted_plan = (
        Path(__file__).resolve().parent.parent / "assets" / "curso5_lab2"
        / "Chimbote_CH-A-P05-S03_vivienda_resaltada.png"
    )
    if highlighted_plan.is_file():
        st.image(
            str(highlighted_plan),
            caption="Planta original, detalle de Torre A: vivienda CH-A-P05-S03 destacada en amarillo y contorno rojo.",
            use_container_width=True,
        )
    st.markdown(
        "**Torre A · piso 5 · hilera sur · tercer departamento desde poniente** "
        "(código académico **CH-A-P05-S03**). La planta tipo permite localizar "
        "la unidad y reconocer sus recintos y colindancias; los cortes y las "
        "elevaciones permiten comprobar alturas, vanos y geometría."
    )
    st.warning(
        "La marca de color en el plano es exclusivamente orientativa y no representa "
        "una superficie medida. Las dimensiones, áreas, volúmenes y tiempos "
        "de reverberación deben obtenerse de los documentos y cálculos, o "
        "declararse como hipótesis explícitas cuando falten datos."
    )

    st.markdown("### B · Planos y documentación complementaria")
    st.markdown(
         "Los **planos originales** son la fuente técnica principal. Las fichas y "
        "los supuestos académicos complementan la información cuando el expediente "
        "no contiene algún dato requerido. Consulta cada documento disponible por separado."
    )
    resource_dir = Path(__file__).resolve().parent.parent / "assets" / "curso5_lab2"
    branch_docs = (
        "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/"
        "blob/curso3-lab2-etapas-3-10/docs/"
    )
    resource_groups = [
        (
            "B1 · Documentación arquitectónica original",
            "Primero revisa la planta tipo, los cortes y las elevaciones. "
            "La planta intervenida del apartado A permite reconocer la vivienda, "
            "pero no sustituye los dibujos técnicos originales.",
            [
                (
                    "Planos originales de Torre A y vivienda identificada",
                    "Chimbote_Torre_A_CH-A-P05-S03_planos.pdf",
                    "Planta tipo, cortes y elevaciones norte/sur originales de Torre A; cotejar los vanos del estar con la elevación sur.",
                    None,
                ),
            ],
        ),
        (
            "B2 · Fichas técnicas y antecedentes para los cálculos",
            "Después consulta las fichas que ayudan a organizar la información "
            "extraída de los planos. Los supuestos deben identificarse como tales.",
            [
                (
                    "Ficha geométrica de la vivienda",
                    "01_Ficha_Geometrica_Chimbote_Alumno.pdf",
                    "Recintos, cerramientos, superficies, volúmenes y colindancias por determinar.",
                    "curso5_lab2_chimbote_ficha_geometrica_alumno.md",
                ),
                (
                    "Especificaciones constructivas académicas",
                    "02_Especificaciones_Constructivas_Chimbote_Alumno.pdf",
                    "Composiciones iniciales para evaluar aislamiento y mejoras.",
                    "curso5_lab2_chimbote_especificaciones_alumno.md",
                ),
                (
                    "Suplemento de cotas e hipótesis",
                    "03_Suplemento_Cotas_Chimbote_Alumno.pdf",
                    "Datos docentes a emplear solamente cuando falten cotas documentales.",
                    "curso5_lab2_chimbote_suplemento_cotas_alumno.md",
                ),
                (
                    "Tránsito y exposición acústica de fachada",
                    "04_Trafico_Fachada_Chimbote_Alumno.pdf",
                    "Datos supuestos de tránsito para modelar el ruido hacia Pasaje Chimbote.",
                    "curso5_lab2_chimbote_trafico_lden_alumno.md",
                ),
            ],
        ),
    ]
    for group_title, group_intro, resources in resource_groups:
        st.markdown(f"#### {group_title}")
        st.caption(group_intro)
        for title, filename, description, alternative in resources:
            file_path = resource_dir / filename
            # The published originals arrive as a ZIP. Offer the ZIP itself:
            # no unnecessary PDF decompression or memory duplication.
            if filename == "Chimbote_Torre_A_CH-A-P05-S03_planos.pdf":
                plans_zip = _plans_archive_path(resource_dir)
                if plans_zip is not None:
                    with st.container(border=True):
                        st.markdown(f"**{title}**")
                        st.caption(description)
                        st.download_button(
                            "📦 Descargar planos originales (.zip)",
                            data=plans_zip.read_bytes(),
                            file_name=plans_zip.name,
                            mime="application/zip",
                            key="c5l2_s1_plans_zip",
                            use_container_width=True,
                        )
                    continue
            pdf_data = file_path.read_bytes() if file_path.is_file() else None
            # La publicación se prepara antes de abrir el laboratorio.
            # No mostrar al alumnado mensajes internos de GitHub ni
            # botones con documentos todavía no disponibles.
            if pdf_data is None:
                continue
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(description)
                st.download_button(
                    "📥 Descargar PDF",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"c5l2_s1_download_{filename}",
                    use_container_width=True,
                )
    st.markdown("### C · Requisitos normativos de Clase B")
    st.info(
        "Consulta ISO/TS 19488:2021 y determina los requisitos de Clase B "
        "para las cuatro situaciones. Identifica descriptor, valor, condición "
        "de aplicación, sentido de comparación y referencia normativa."
    )
    st.caption(
        "El criterio de fachada depende de la exposición exterior y el de "
        "instalaciones del régimen de operación. No se entregan valores "
        "normativos resueltos: debes justificar la selección."
    )
    old=saved.get("c5l2_s1") or {}
    previous=old.get("criteria") or {}
    fields={}
    with st.form("c5l2_class_b_requirements"):
        for code,(name,_,_) in CASES.items():
            previous_row=previous.get(code) or {}
            st.markdown(f"#### {code} · {name}")
            col1,col2=st.columns(2)
            with col1:
                descriptor=st.text_input("Descriptor(s) normativo(s) y unidades",value=previous_row.get("descriptor",""),key=f"c5l2_norm_{code}_descriptor")
                limit=st.text_input("Requisito Clase B (valor y unidad)",value=previous_row.get("limit",""),key=f"c5l2_norm_{code}_limit")
            with col2:
                options=["Selecciona","Mayor o igual (≥)","Menor o igual (≤)","Intervalo / múltiples condiciones"]
                previous_direction=previous_row.get("direction","Selecciona")
                direction=st.selectbox("Sentido del criterio",options,index=options.index(previous_direction) if previous_direction in options else 0,key=f"c5l2_norm_{code}_direction")
                reference=st.text_input("Tabla, fila, nota y apartado ISO",value=previous_row.get("reference",""),key=f"c5l2_norm_{code}_reference")
            condition=st.text_area("Ámbito de aplicación, condiciones y justificación técnica",value=previous_row.get("condition",""),height=82,key=f"c5l2_norm_{code}_condition")
            fields[code]={"descriptor":descriptor,"limit":limit,"direction":direction,"reference":reference,"condition":condition}
        st.markdown("#### Guardado de la Etapa 1")
        st.caption(
            "Puedes guardar un borrador aunque falten requisitos. "
            "Para completar la etapa debes registrar los cinco campos de "
            "cada familia acústica: descriptor, requisito, sentido, referencia "
            "normativa y condición de aplicación."
        )
        save_col, finish_col = st.columns(2)
        with save_col:
            save_draft = st.form_submit_button(
                "💾 Guardar avance", use_container_width=True
            )
        with finish_col:
            finish_stage = st.form_submit_button(
                "✓ Completar Etapa 1", type="primary", use_container_width=True
            )
    if save_draft or finish_stage:
        # Preserve any historical documentation fields without forcing the
        # student to fill in the removed recognition form.
        payload={**old, "criteria":fields}
        if save_draft:
            _save(lab,saved,1,"c5l2_s1",payload,complete=False)
        else:
            incomplete=[code for code,row in fields.items() if
                not row["descriptor"].strip() or not row["limit"].strip() or
                row["direction"]=="Selecciona" or not row["reference"].strip() or
                len(row["condition"].strip())<20]
            if incomplete:
                st.warning(
                    "Faltan datos normativos o justificaciones en: "+
                    ", ".join(incomplete)+
                    ". Puedes guardar el avance sin completar la etapa."
                )
            else:
                _save(lab,saved,1,"c5l2_s1",payload,complete=True)



def _stage2(lab,saved):
    _header(2)
    st.markdown("### Construye la ficha geométrica desde los planos")
    st.info("Los recintos están fijados por el laboratorio. En la **planta tipo de Torre A (pisos 3–16)** se identifica el muro compartido estar poniente–dormitorio y el estar expuesto por la fachada sur. Los dormitorios de pisos 5 y 6 se superponen conforme a esa planta tipo. Tu trabajo es calcular **áreas, alturas, volúmenes, superficies de separación, fachada y vanos**, anotando láminas y cotas. En instalaciones, la descarga proviene del WC de la **vivienda distinta del piso 6**; el recorrido de la bajada hasta el dormitorio debe justificarse como modelo docente si no está en los planos.")
    old=saved.get("c5l2_s2") or {}
    fixed_cases = [
        ("AI-01", "Estar · vivienda poniente, piso 5",
         "Dormitorio · CH-A-P05-S03, piso 5", "M-01 · muro entre viviendas"),
        ("IM-01", "Dormitorio superpuesto · piso 6",
         "Dormitorio · CH-A-P05-S03, piso 5", "L-01 · losa entre pisos"),
        ("FA-01", "Exterior · Pasaje Chimbote",
         "Estar · CH-A-P05-S03, piso 5", "F-01/V-01 · fachada sur"),
        ("IN-01", "Descarga WC · baño vivienda superior, piso 6",
         "Dormitorio · CH-A-P05-S03, piso 5", "S-01/IS-01 · instalaciones"),
    ]
    st.markdown("#### A · Casos y recintos asignados por el docente")
    st.table(
        [{"Caso":case,"Emisor / fuente":emitter,"Receptor":receiver,"Elemento":element}
         for case,emitter,receiver,element in fixed_cases]
    )
    st.caption(
        "La planta tipo original incluye pisos 3–16, por lo que la superposición "
        "del dormitorio en pisos 5 y 6 es coherente en planta. "
        "Esto no determina espesores ni transmisiones. El WC del piso 6 "
        "pertenece a otra vivienda; su recorrido sanitario hacia el receptor "
        "es una hipótesis de modelación, no un trazado certificado en planos."
    )
    st.markdown("#### B · Geometría de los recintos receptores")
    st.markdown(
         "**Calcula el área horizontal del recinto y su volumen interior para el cálculo del TR.** "
        "**AI-01, IM-01 e IN-01:** dormitorio de CH-A-P05-S03 (piso 5). "
        "**FA-01:** estar de esa misma vivienda. "
         "En el modelo docente rectangular, **el área horizontal del piso y la del cielo del dormitorio coinciden**; el volumen se obtiene como área × altura libre. "
        "Para **IM-01**, el elemento que se evalúa acústicamente es la **losa superior (cielo) del dormitorio del piso 5**, que lo separa de la vivienda del piso 6. Su superficie se indica en la tabla C."
    )
    # The underlying saved structure is preserved (including receiver labels),
    # while the editor displays only short codes and student-editable geometry.
    rec_cols = ["Caso", "Recinto receptor", "Piso / unidad",
                "Largo (m)", "Ancho (m)", "Altura (m)",
                "Área (m²)", "Volumen (m³)", "Plano / cota"]
    room_labels = {
        case: (receiver, "Piso 5 · CH-A-P05-S03")
        for case, _, receiver, _ in fixed_cases
    }
    stored_rooms = {
        str(row.get("Caso") or ""): row for row in (old.get("rooms") or [])
        if isinstance(row, dict)
    }
    room_rows = []
    for case, _, _, _ in fixed_cases:
        receiver, location = room_labels[case]
        row = {column: stored_rooms.get(case, {}).get(column, "")
               for column in rec_cols}
        row.update({"Caso": case, "Recinto receptor": receiver,
                    "Piso / unidad": location})
        room_rows.append(row)
    import pandas as pd
    room_subject = {"AI-01":"Dormitorio P5", "IM-01":"Dormitorio P5",
                    "FA-01":"Estar P5", "IN-01":"Dormitorio P5"}
    for row in room_rows:
        row["Recinto a medir"] = room_subject[row["Caso"]]
    room_edit_cols = ["Caso", "Recinto a medir", "Largo (m)", "Ancho (m)", "Altura (m)",
                      "Área (m²)", "Volumen (m³)", "Plano / cota"]
    room_df = st.data_editor(
        pd.DataFrame(room_rows)[room_edit_cols],
        key="c5l2_rooms_compact_v2", hide_index=True, use_container_width=True,
        height=190, num_rows="fixed",
        disabled=["Caso", "Recinto a medir"],
        column_config={
            "Caso": st.column_config.TextColumn("Caso", width="small"),
            "Recinto a medir": st.column_config.TextColumn("Recinto", width="small"),
            "Largo (m)": st.column_config.TextColumn("Largo", width="small"),
            "Ancho (m)": st.column_config.TextColumn("Ancho", width="small"),
            "Altura (m)": st.column_config.TextColumn("Alto", width="small"),
            "Área (m²)": st.column_config.TextColumn("Área horizontal m²", width="small", help="Área en planta del recinto receptor. En el modelo rectangular sin salientes, coincide con el área de su cielo; se utiliza con la altura para obtener el volumen y el TR."),
            "Volumen (m³)": st.column_config.TextColumn("Volumen m³", width="small", help="Volumen interior útil del recinto: área de piso × altura libre, para geometría uniforme."),
            "Plano / cota": st.column_config.TextColumn("Lámina / cota", width="medium"),
        },
    )
    compact_room = room_df.fillna("").to_dict("records")
    rooms = []
    for master, edited in zip(room_rows, compact_room):
        rooms.append({**master, **edited})

    st.markdown("#### C · Superficies de separación y trazabilidad")
    st.markdown(
          "**Calcula el área del elemento de separación.** Para **AI-01, FA-01 e IN-01** multiplica largo por altura; para **IM-01**, largo por ancho de la losa superior. **AI-01:** área del muro medianero M-01 "
        "entre el estar vecino y el dormitorio. **IM-01:** área de losa L-01 "
         "**SUPERIOR**, sobre el cielo del dormitorio receptor del piso 5, bajo el dormitorio emisor del piso 6. **FA-01:** área bruta del paño "
        "de fachada sur del estar. **IN-01:** superficie del cierre S-01 "
        "que interviene en el recorrido supuesto de la descarga de WC vecina. "
        "El recorrido sanitario no está documentado: identifícalo como hipótesis."
    )
    sep_cols = ["Caso", "Recinto emisor", "Recinto receptor", "Elemento",
                "Longitud (m)", "Altura (m)", "Superficie (m²)", "Plano / cota"]
    stored_sep = {
        str(row.get("Caso") or ""): row
        for row in (old.get("separations") or []) if isinstance(row, dict)
    }
    sep_rows = []
    for case, emitter, receiver, element in fixed_cases:
        row = {column: stored_sep.get(case, {}).get(column, "")
               for column in sep_cols}
        row.update({"Caso": case, "Recinto emisor": emitter,
                    "Recinto receptor": receiver, "Elemento": element})
        sep_rows.append(row)
    sep_subject = {"AI-01":"Muro medianero M-01",
                   "IM-01":"Losa entre pisos L-01",
                   "FA-01":"Fachada sur estar F-01",
                   "IN-01":"Cierre sanitario S-01"}
    for row in sep_rows:
        row["Elemento a medir"] = sep_subject[row["Caso"]]
    sep_edit_cols = ["Caso", "Elemento a medir", "Longitud (m)", "Altura (m)",
                     "Superficie (m²)", "Plano / cota"]
    sep_df = st.data_editor(
        pd.DataFrame(sep_rows)[sep_edit_cols],
        key="c5l2_separations_compact_v2", hide_index=True,
        use_container_width=True, height=190, num_rows="fixed",
        disabled=["Caso", "Elemento a medir"],
        column_config={
            "Caso": st.column_config.TextColumn("Caso", width="small"),
            "Elemento a medir": st.column_config.TextColumn("Elemento / superficie", width="medium"),
            "Longitud (m)": st.column_config.TextColumn("Largo (m)", width="small", help="Longitud del elemento: muro, losa, fachada o cierre sanitario."),
            "Altura (m)": st.column_config.TextColumn("Ancho / alto (m)", width="medium", help="IM-01: ANCHO de la losa superior. AI-01, FA-01 e IN-01: ALTURA del muro, fachada o cierre."),
            "Superficie (m²)": st.column_config.TextColumn("Superficie m²", width="small"),
            "Plano / cota": st.column_config.TextColumn("Lámina / cota", width="large"),
        },
    )
    sep = [{**master, **edited}
           for master, edited in zip(sep_rows, sep_df.fillna("").to_dict("records"))]

    st.markdown("#### D · Fachada sur del estar y ventanas")
    st.markdown(
        "**Solo fachada sur del estar de CH-A-P05-S03 (piso 5)**, hacia Pasaje Chimbote. "
        "Indica **área bruta de ese paño**, **suma de áreas de sus ventanas** "
        "y **área opaca = área bruta − área de ventanas**. "
        "Utiliza planta tipo y elevación sur; si aplicas HV-02, declara el supuesto."
    )
    env_cols = ["Recinto", "Orientación", "Paño total (m²)",
                "Ventanas (m²)", "Opaco (m²)", "Plano / cota"]
    stored_env = (old.get("facades") or [{}])[0]
    env_row = {column: stored_env.get(column, "") for column in env_cols}
    env_row.update({"Recinto": "Estar · CH-A-P05-S03, piso 5",
                    "Orientación": "Sur · Pasaje Chimbote"})
    env_edit_cols = ["Paño total (m²)", "Ventanas (m²)",
                     "Opaco (m²)", "Plano / cota"]
    env_df = st.data_editor(
        pd.DataFrame([env_row])[env_edit_cols],
        key="c5l2_facades_compact_v2", hide_index=True,
        use_container_width=True, height=100, num_rows="fixed",
        column_config={
            "Paño total (m²)": st.column_config.TextColumn("Fachada total m²", width="medium"),
            "Ventanas (m²)": st.column_config.TextColumn("Ventanas m²", width="medium"),
            "Opaco (m²)": st.column_config.TextColumn("Opaco m²", width="medium"),
            "Plano / cota": st.column_config.TextColumn("Lámina / cota", width="large"),
        },
    )
    env = [{**env_row, **env_df.fillna("").to_dict("records")[0]}]
    with st.expander("Criterios para levantar la geometría"):
        st.markdown(
            "Registra las dimensiones **reales de la unidad seleccionada** con su lámina; "
            "separa las cotas documentales de las **hipótesis docentes HG-01, HV-02, HI-01**. "
            "Para recintos irregulares usa descomposición de superficies. "
            "El área opaca de fachada es área total menos vanos y nunca se toma del render."
        )
    state_payload = {"rooms": rooms, "separations": sep, "facades": env}
    draft_col, finish_col = st.columns(2)
    with draft_col:
        save_draft = st.button(
            "💾 Guardar avance", key="c5l2_save_geometry_draft_v2",
            use_container_width=True,
        )
    with finish_col:
        finish_stage = st.button(
            "✓ Completar Etapa 2", key="c5l2_complete_geometry_v2",
            type="primary", use_container_width=True,
        )
    if save_draft:
        _save(lab, saved, 2, "c5l2_s2", state_payload, complete=False)
    if finish_stage:
        if not all(str(row.get("Plano / cota", "")).strip()
                   for row in rooms + sep + env):
            st.warning(
                "Falta la referencia de lámina/cota de algún caso. "
                "Puedes guardar el avance sin cerrar la etapa."
            )
        elif not all(
            str(row.get(field, "")).strip()
            for row in rooms for field in ("Área (m²)", "Volumen (m³)")
        ):
            st.warning(
                "Completa áreas y volúmenes de los cuatro receptores. "
                "Si un recinto se repite en varios casos, registra el mismo resultado."
            )
        elif not all(
            str(row.get("Superficie (m²)", "")).strip() for row in sep
        ):
            st.warning("Documenta las superficies de separación/modelación de los cuatro casos.")
        elif not all(
            str(env[0].get(field, "")).strip()
            for field in ("Paño total (m²)", "Ventanas (m²)", "Opaco (m²)")
        ):
            st.warning("Completa la geometría de la fachada sur del estar.")
        else:
            _save(lab, saved, 2, "c5l2_s2", state_payload, complete=True)


def _stage3(lab,saved):
    """Materiality and octave-band reverberation worksheet for SONARA."""
    _header(3)
    import pandas as pd

    old = saved.get("c5l2_s3") or {}
    geometry = saved.get("c5l2_s2") or {}
    st.markdown("### Materialidad original y reverberación por bandas")
    st.info(
        "Los sistemas constructivos originales están definidos por el encargo. "
        "En esta etapa prepara **las superficies y los materiales de los recintos receptores** "
        "y registra el **tiempo de reverberación TR que calcules en SONARA por banda**. "
        "No se asigna un TR fijo ni se inventan coeficientes de absorción."
    )

    st.markdown("#### A · Sistemas constructivos originales del ejercicio")
    st.table([
        {"Código": item["Código"], "Elemento": item["Elemento"],
         "Composición académica": item["Composición original"]}
        for item in BASE_CONSTRUCTION
    ])
    st.caption(
        "La tabla A es la condición original para los modelos posteriores de "
        "aislamiento aéreo, impacto, fachada e instalaciones. Son especificaciones "
        "académicas, no propiedades verificadas del edificio. "
        "Las curvas de aislamiento de cada sistema se obtendrán en sus etapas de diseño."
    )

    st.markdown("#### B · Superficies y acabados para calcular TR en SONARA")
    st.markdown(
        "Calcula y registra **área de piso, cielo, muros opacos, puerta y ventana** "
        "por separado, para el **dormitorio** y el **estar** de la vivienda del piso 5. "
        "La suma de las superficies verticales debe descontar los vanos **una sola vez**. "
        "En SONARA asigna a cada acabado su **coeficiente de absorción α por banda** "
        "y documenta de dónde se obtuvo; no utilices Rw como absorción."
    )

    def _numeric(value):
        try:
            number = float(str(value).strip().replace(",", "."))
            return number if math.isfinite(number) and number >= 0 else None
        except (TypeError, ValueError):
            return None

    room_data = {str(item.get("Caso") or ""): item for item in geometry.get("rooms", [])
                 if isinstance(item, dict)}
    facades = geometry.get("facades") or [{}]
    facade = facades[0] if isinstance(facades[0], dict) else {}
    st.caption(
        "Las áreas y los volúmenes de la Etapa 2 se recuperan cuando están guardados. "
        "Puedes corregirlos aquí sin modificar la ficha geométrica original."
    )

    # Example figures are intentionally teacher-only, not prefilled to student fields.
    st.caption(
        "Solo se utilizan los acabados originales necesarios en este laboratorio. "
        "Las curvas α(f) correspondientes aparecen directamente bajo cada recinto, "
        "sin incluir alfombra, cielo acústico ni panel absorbente como condición base."
    )
    room_setup = [
        ("Dormitorio", "AI-01", [
            ("Piso", "Laminado sin aporte resiliente acreditado", "T-03"),
            ("Cielo", "Pintura sobre superficie rígida", "T-02"),
            ("Muros opacos", "Pintura sobre superficies rígidas", "T-02"),
            ("Puerta", "Puerta interior de madera maciza (supuesto docente)", "Referencia genérica con curva α"),
            ("Ventana", "Ventana del dormitorio (verificar en plano)", "Ficha técnica / plano"),
        ]),
        ("Estar", "FA-01", [
            ("Piso", "Cerámica adherida", "T-01"),
            ("Cielo", "Pintura sobre superficie rígida", "T-02"),
            ("Muros opacos", "Pintura sobre superficies rígidas", "T-02"),
            ("Puerta", "Puerta interior (material a justificar)", "HIPÓTESIS / ficha técnica"),
            ("Ventana", "DVH 4/12/4 mm con marco aluminio", "V-01"),
        ]),
    ]
    old_rooms = old.get("tr_rooms") if isinstance(old.get("tr_rooms"), dict) else {}
    result_rooms = {}
    for room_name, case, surfaces in room_setup:
        st.markdown(f"**{room_name} · geometría y terminaciones de referencia**")
        source_room = room_data.get(case, {})
        stored_room = old_rooms.get(room_name, {}) if isinstance(old_rooms, dict) else {}
        # An existing in-progress Stage 3 answer wins over geometry recovered
        # from Stage 2. Never override a student's submitted values.
        initial_area = stored_room.get("area", source_room.get("Área (m²)", ""))
        initial_volume = stored_room.get("volume", source_room.get("Volumen (m³)", ""))
        initial_height = stored_room.get("height", source_room.get("Altura (m)", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            area = st.text_input(
                f"{room_name} · área útil de piso [m²]",
                value=str(initial_area or ""), key=f"c5l2_tr_area_{room_name}",
                help="Área en planta del recinto receptor. No es área del muro separador.",
            )
        with c2:
            height = st.text_input(
                f"{room_name} · altura libre [m]",
                value=str(initial_height or ""), key=f"c5l2_tr_height_{room_name}",
            )
        with c3:
            volume = st.text_input(
                f"{room_name} · volumen interior [m³]",
                value=str(initial_volume or ""), key=f"c5l2_tr_volume_{room_name}",
                help="Se requiere para normalizar el cálculo de reverberación.",
            )
        default_areas = {}
        numeric_area, numeric_height = _numeric(area), _numeric(height)
        # Floor and ceiling have the same horizontal projection in the
        # rectangular academic model; existing saved stage-3 inputs override.
        if numeric_area is not None:
            default_areas["Piso"] = str(numeric_area)
            default_areas["Cielo"] = str(numeric_area)
        if room_name == "Estar":
            win = _numeric(facade.get("Ventanas (m²)"))
            if win is not None:
                default_areas["Ventana"] = str(win)
        old_surface_rows = stored_room.get("surfaces") or []
        by_name = {str(row.get("Superficie") or ""): row for row in old_surface_rows
                   if isinstance(row, dict)}
        table_rows = []
        for surface, material, reference in surfaces:
            previous = by_name.get(surface, {})
            default_preset = (
                "Vidrio" if surface == "Ventana"
                else "Yeso pintado" if surface in ("Cielo", "Muros opacos")
                else "Puerta de madera maciza" if surface == "Puerta"
                else "Hormigón / superficie dura"
            )
            previous_choice = str(previous.get("Material SONARA") or "")
            preset = previous_choice if previous_choice in TR_SONARA_PRESETS else default_preset
            table_rows.append({
                "Superficie": surface,
                "Área (m²)": str(previous.get("Área (m²)") or default_areas.get(surface, "")),
                "Acabado del encargo": material,
                "Material SONARA": preset,
            })
        surface_df = st.data_editor(
            pd.DataFrame(table_rows),
            key=f"c5l2_tr_surface_sonara_v2_{room_name}",
            hide_index=True, num_rows="fixed", use_container_width=True,
            height=225, disabled=["Superficie", "Acabado del encargo"],
            column_config={
                "Superficie": st.column_config.TextColumn("Superficie", width="small"),
                "Área (m²)": st.column_config.TextColumn("Área m²", width="small"),
                "Acabado del encargo": st.column_config.TextColumn(
                    "Acabado del encargo", width="medium"),
                "Material SONARA": st.column_config.SelectboxColumn(
                    "Preset α(f) en SONARA", options=[
                        "Hormigón / superficie dura", "Yeso pintado",
                        "Vidrio", "Puerta de madera maciza",
                    ],
                    required=True, width="large"),
            },
        )
        edited_surfaces = surface_df.fillna("").to_dict("records")
        st.markdown(f"**Coeficientes de absorción seleccionados · {room_name}**")
        st.table([
            {"Superficie": row["Superficie"], "Preset": row["Material SONARA"],
             **{str(hz) + " Hz": format(val, ".2f")
                for hz, val in zip(
                    TR_OCTAVE_BANDS,
                    TR_SONARA_PRESETS.get(str(row["Material SONARA"]), ())
                )}}
            for row in edited_surfaces
        ])
        result_rooms[room_name] = {
            "area": area, "height": height, "volume": volume,
            "surfaces": [
                {
                    **row,
                    "Material / acabado": row["Acabado del encargo"],
                    "Referencia α(f)": (
                        "SONARA / Reverberación / Material genérico: " +
                        str(row["Material SONARA"])
                    ),
                    "Alfa por banda": dict(zip(
                        TR_OCTAVE_BANDS,
                        TR_SONARA_PRESETS.get(str(row["Material SONARA"]), ())
                    )),
                }
                for row in edited_surfaces
            ],
        }
        st.caption(
            f"**{room_name}:** el área de muros opacos corresponde al total de muros "
            "menos puertas y ventanas. Si el plano no permite determinar un vano, "
            "utiliza únicamente un supuesto explícito del suplemento de cotas."
        )

    st.caption(
        "Puerta: curva de **madera maciza** (125–4000 Hz: "
        "0,14 / 0,10 / 0,06 / 0,08 / 0,10 / 0,10). "
        "Fuente de referencia NBR 12179:1992, reproducida en publicación UFRJ. "
        "El preset también fue incorporado en SONARA; no corresponde a "
        "una medición de la puerta de Chimbote."
    )
    st.markdown("#### C · Tiempo de reverberación obtenido en SONARA")
    st.markdown(
        "Registra el **TR [s] de cada banda de octava**, separando dormitorio y estar. "
        "Estos son **resultados obtenidos de SONARA**, no valores de α ni niveles "
        "de aislamiento acústico. Conserva los cálculos de la condición original."
    )
    bands = [125, 250, 500, 1000, 2000, 4000]
    stored_tr = {
        str(item.get("Banda (Hz)") or ""): item
        for item in (old.get("tr_bands") or []) if isinstance(item, dict)
    }
    band_rows = []
    for hz in bands:
        existing = stored_tr.get(str(hz), {})
        band_rows.append({
            "Banda (Hz)": hz,
            "TR dormitorio (s)": str(existing.get("TR dormitorio (s)") or ""),
            "TR estar (s)": str(existing.get("TR estar (s)") or ""),
        })
    band_df = st.data_editor(
        pd.DataFrame(band_rows), key="c5l2_tr_bands_v1",
        hide_index=True, num_rows="fixed", use_container_width=True,
        height=260, disabled=["Banda (Hz)"],
        column_config={
            "Banda (Hz)": st.column_config.NumberColumn("Octava Hz", width="small"),
            "TR dormitorio (s)": st.column_config.TextColumn("TR dormitorio [s]", width="medium"),
            "TR estar (s)": st.column_config.TextColumn("TR estar [s]", width="medium"),
        },
    )
    tr_bands = band_df.fillna("").to_dict("records")
    payload = {
        **old, "tr_rooms": result_rooms, "tr_bands": tr_bands,
        "base_version": "chimbote_original_tr_bandas_v2",
    }
    left, right = st.columns(2)
    with left:
        draft = st.button(
            "💾 Guardar avance", key="c5l2_stage3_save_draft_v2",
            use_container_width=True,
        )
    with right:
        finish = st.button(
            "✓ Completar Etapa 3", key="c5l2_stage3_finish_v2",
            use_container_width=True, type="primary",
        )
    if draft:
        _save(lab, saved, 3, "c5l2_s3", payload, complete=False)
    if finish:
        missing_room = []
        for room_name, room in result_rooms.items():
            if any(_numeric(room.get(key)) is None or _numeric(room.get(key)) <= 0
                   for key in ("area", "height", "volume")):
                missing_room.append(f"{room_name}: área/altura/volumen")
            for surface in room["surfaces"]:
                if _numeric(surface.get("Área (m²)")) is None:
                    missing_room.append(f"{room_name}: área de {surface['Superficie']}")
                if not str(surface.get("Material / acabado") or "").strip():
                    missing_room.append(f"{room_name}: material de {surface['Superficie']}")
                if str(surface.get("Material SONARA") or "") not in TR_SONARA_PRESETS:
                    missing_room.append(f"{room_name}: material SONARA de {surface['Superficie']}")
        bad_bands = [
            str(row["Banda (Hz)"]) + " Hz"
            for row in tr_bands
            if any(_numeric(row.get(key)) is None or _numeric(row.get(key)) <= 0
                   for key in ("TR dormitorio (s)", "TR estar (s)"))
        ]
        if missing_room:
            st.warning(
                "Para completar la etapa faltan superficies, materialidad o fuentes "
                "de absorción: " + ", ".join(missing_room[:8]) +
                ("…" if len(missing_room) > 8 else "")
            )
        elif bad_bands:
            st.warning(
                "Faltan valores de TR positivos para dormitorio y estar en: " +
                ", ".join(bad_bands) + ". Puedes guardar el avance."
            )
        else:
            _save(lab, saved, 3, "c5l2_s3", payload, complete=True)


def _stage4(lab, saved):
    """Structured ISO 12354-1 airborne insulation design worksheet, for SONARA."""
    import pandas as pd

    _header(4)
    old = saved.get("c5l2_s4") or {}
    geometry = saved.get("c5l2_s2") or {}
    reverberation = saved.get("c5l2_s3") or {}
    criterion = ((saved.get("c5l2_s1") or {}).get("criteria") or {}).get("AI-01") or {}

    st.markdown("### AI-01 · Aislamiento aéreo entre viviendas")
    st.info(
        "Diseña el aislamiento entre el **estar de la vivienda poniente (emisor)** "
        "y el **dormitorio de CH-A-P05-S03, piso 5 (receptor)**. "
        "Prepara los datos para **SONARA** y registra **dos simulaciones**: "
        "el muro M-01 original y una mejora diseñada por ti. "
        "Para la predicción entre recintos considera **ISO 12354-1** "
        "(transmisión directa y flanqueos); la valoración global se expresa "
        "con **ISO 717-1**. El Rw del elemento aislado no equivale a DₙT,w."
    )
    st.caption(
        "Secuencia: 1) recuperar geometría → 2) caracterizar muro y encuentros → "
        "3) ingresar en SONARA → 4) registrar modelo original → "
        "5) modificar la solución y recalcular → 6) contrastar con la meta Clase B."
    )

    rooms = {str(r.get("Caso") or ""): r for r in geometry.get("rooms", [])
             if isinstance(r, dict)}
    separations = {str(r.get("Caso") or ""): r
                   for r in geometry.get("separations", [])
                   if isinstance(r, dict)}
    receiver = rooms.get("AI-01", {})
    separator = separations.get("AI-01", {})
    tr_room = (reverberation.get("tr_rooms") or {}).get("Dormitorio", {})
    tr_bands = reverberation.get("tr_bands") or []

    def _val(value):
        return "" if value is None else str(value)

    def _positive(value):
        try:
            number = float(str(value).strip().replace(",", "."))
            return math.isfinite(number) and number > 0
        except (ValueError, TypeError):
            return False

    st.markdown("#### A · Datos geométricos necesarios para ISO 12354-1")
    st.caption(
        "Los campos se recuperan de las etapas 2 y 3 **si todavía no han sido "
        "editados aquí**. Son datos de trabajo para transcribir a SONARA, "
        "no resultados calculados automáticamente."
    )
    old_geo = old.get("iso_geometry") or {}
    # Prefer saved values from previous stages. Older empty Stage 4 drafts
    # must never mask geometry already recorded in Stage 2 / Stage 3.
    def _filled(*values):
        for value in values:
            if value is not None and str(value).strip():
                return value
        return ""

    defaults = {
        "source_room": "Estar de vivienda poniente · piso 5",
        "receiver_room": "Dormitorio · CH-A-P05-S03 · piso 5",
        "separator": "M-01 · hormigón armado 180 mm",
        "length": separator.get("Longitud (m)", ""),
        "height": separator.get("Altura (m)", ""),
        "surface": separator.get("Superficie (m²)", ""),
        "receiver_length": receiver.get("Largo (m)", ""),
        "receiver_width": receiver.get("Ancho (m)", ""),
        "receiver_height": receiver.get("Altura (m)", ""),
        "receiver_volume": _filled(receiver.get("Volumen (m³)"), tr_room.get("volume")),
        "receiver_area": _filled(receiver.get("Área (m²)"), tr_room.get("area")),
        "source_volume": "",
        "source_area": "",
        "source_height": "",
        "drawing": _filled(separator.get("Plano / cota"), receiver.get("Plano / cota")),
        "source_basis": "",
    }
    # Stage 2 provides the receptor geometry and M-01, Stage 3 supplies
    # an independent backup for receiver area/height/volume. Never invent
    # the source room dimensions: that is another dwelling.
    defaults["receiver_length"] = _filled(defaults["receiver_length"])
    defaults["receiver_width"] = _filled(defaults["receiver_width"])
    defaults["receiver_height"] = _filled(defaults["receiver_height"], tr_room.get("height"))
    if not defaults["surface"] and defaults["length"] and defaults["height"]:
        try:
            defaults["surface"] = f'{float(str(defaults["length"]).replace(",", ".")) * float(str(defaults["height"]).replace(",", ".")):.3f}'
        except (ValueError, TypeError):
            pass
    if not defaults["receiver_area"] and defaults["receiver_length"] and defaults["receiver_width"]:
        try:
            defaults["receiver_area"] = f'{float(str(defaults["receiver_length"]).replace(",", ".")) * float(str(defaults["receiver_width"]).replace(",", ".")):.3f}'
        except (ValueError, TypeError):
            pass
    if not defaults["receiver_volume"] and defaults["receiver_area"] and defaults["receiver_height"]:
        try:
            defaults["receiver_volume"] = f'{float(str(defaults["receiver_area"]).replace(",", ".")) * float(str(defaults["receiver_height"]).replace(",", ".")):.3f}'
        except (ValueError, TypeError):
            pass

    st.markdown("**Ficha geométrica vinculada al trabajo anterior**")
    st.caption(
        "Las dimensiones del muro M-01 y del dormitorio se recuperan "
        "automáticamente de las **respuestas guardadas** de Etapa 2; "
        "se complementan con la Etapa 3 cuando procede. "
        "El estar emisor pertenece a otra vivienda y no se inventa."
    )
    recovered = [name for name in (
        "length", "height", "surface", "receiver_length", "receiver_width",
        "receiver_height", "receiver_area", "receiver_volume", "drawing"
    ) if str(defaults.get(name) or "").strip()]
    if recovered:
        st.success(
            f"Datos previos disponibles: {len(recovered)}/9. "
            "Los campos recuperados se muestran automáticamente."
        )
    else:
        st.warning(
            "No hay dimensiones de AI-01 **guardadas** en la Etapa 2 "
            "ni dimensiones del dormitorio guardadas en la Etapa 3. "
            "Editar la tabla anterior no basta: debes pulsar **Guardar avance** "
            "o **Completar etapa** en esas etapas, con esta misma cuenta. "
            "No se usarán cotas inventadas."
        )
    geo = {}
    fields = [
        ("length", "Largo muro separador (m)"),
        ("height", "Altura muro separador (m)"),
        ("surface", "Superficie separadora S (m²)"),
        ("receiver_length", "Largo dormitorio receptor (m)"),
        ("receiver_width", "Ancho dormitorio receptor (m)"),
        ("receiver_height", "Altura dormitorio receptor (m)"),
        ("receiver_area", "Área dormitorio receptor (m²)"),
        ("receiver_volume", "Volumen receptor V (m³)"),
        ("source_area", "Área estar emisor (m²)"),
        ("source_height", "Altura estar emisor (m)"),
        ("source_volume", "Volumen emisor (m³)"),
    ]
    # Use a revision token derived from saved upstream content. Without this,
    # Streamlit preserves widget state after re-running and a previously blank
    # input can mask subsequently saved geometry even when value= is supplied.
    import hashlib
    upstream_signature = hashlib.sha256(
        json.dumps(
            {"geometry": defaults, "stage2": geometry, "stage3": reverberation},
            sort_keys=True, ensure_ascii=False, default=str
        ).encode("utf-8")
    ).hexdigest()[:12]
    for i in range(0, len(fields), 3):
        cols = st.columns(3)
        for col, (key, label) in zip(cols, fields[i:i+3]):
            with col:
                recovered_value = defaults.get(key, "")
                stored_value = old_geo.get(key, "")
                geo[key] = st.text_input(
                    label,
                    value=_val(_filled(recovered_value, stored_value)),
                    key=f"c5l2_s4_geometry_{key}_{upstream_signature}",
                    disabled=bool(str(recovered_value or "").strip()),
                    help=(
                        "Valor recuperado automáticamente: edítalo en la etapa de origen."
                        if str(recovered_value or "").strip()
                        else "No existe valor previo; indica un valor del plano o una hipótesis justificada."
                    )
                )
    cols = st.columns(2)
    with cols[0]:
        geo["drawing"] = st.text_input(
            "Referencia de plano / cota",
            value=_val(_filled(defaults["drawing"], old_geo.get("drawing"))),
            key=f"c5l2_s4_drawing_{upstream_signature}",
            disabled=bool(str(defaults["drawing"] or "").strip()),
        )
    with cols[1]:
        geo["source_basis"] = st.text_input(
            "Referencia o hipótesis de geometría emisora",
            value=_val(old_geo.get("source_basis", "")),
            key="c5l2_s4_source_basis",
            help="El estar de otra vivienda no se supone idéntico al dormitorio receptor."
        )
    if recovered:
        st.caption(
            "Los campos precargados son de **solo lectura**. Para corregirlos, "
            "vuelve a Etapa 2 o 3, guarda la modificación y regresa aquí. "
            "Los datos que aún faltan se pueden registrar directamente en esta ficha."
        )
    st.caption(
        "V = superficie horizontal × altura libre para recintos prismáticos. "
        "S = largo del medianero × altura. Si hay entrantes, puertas o geometría "
        "irregular, documenta el cálculo real. Para el emisor, **no reutilices "
        "automáticamente el volumen del dormitorio**."
    )
    if _positive(geo["length"]) and _positive(geo["height"]) and _positive(geo["surface"]):
        expected = float(geo["length"].replace(",", ".")) * float(geo["height"].replace(",", "."))
        actual = float(geo["surface"].replace(",", "."))
        if abs(actual - expected) > max(.05, .02 * expected):
            st.warning("Comprueba S: la superficie anotada difiere del producto largo × alto.")

    st.markdown("#### B · Muro original y vías de transmisión")
    st.table([{
        "Código": "M-01", "Solución original": "Hormigón armado 180 mm",
        "Densidad": "2.400 kg/m³", "Uniones": "Encuentros rígidos"
    }])
    st.caption(
        "Masa superficial nominal de referencia del muro original: "
        "0,18 m × 2.400 kg/m³ = 432 kg/m² (hipótesis de materialidad, "
        "no sustituto de una curva R(f) ensayada)."
    )
    previous_system = old.get("systems") or {}
    b1, b2, b3 = st.columns(3)
    with b1:
        model_type = st.selectbox(
            "Modelo utilizado en SONARA",
            ["ISO 12354-1 por bandas", "ISO 12354-1 simplificado", "Otro (justificar)"],
            index=(["ISO 12354-1 por bandas", "ISO 12354-1 simplificado",
                    "Otro (justificar)"].index(previous_system.get("model_type"))
                   if previous_system.get("model_type") in
                   ["ISO 12354-1 por bandas", "ISO 12354-1 simplificado",
                    "Otro (justificar)"] else 0),
            key="c5l2_s4_model_type"
        )
    with b2:
        data_origin = st.text_input(
            "Origen de R(f) / Rw de la base",
            value=previous_system.get("data_origin", ""),
            key="c5l2_s4_data_origin",
            placeholder="SONARA / ensayo / cálculo justificado"
        )
    with b3:
        reference_time = st.text_input(
            "Tiempo de referencia normativo T₀ (s) · no es TR", value=_val(previous_system.get("t0", "0.5")),
            key="c5l2_s4_t0"
        )
    st.markdown("**Tiempo de reverberación TR(f) del dormitorio receptor · Etapa 3**")
    st.caption(
        "Estos son los tiempos reales del modelo del alumno, recuperados de la "
        "Etapa 3, que se utilizan en SONARA. **TR(f) no es T₀**: T₀ = 0,5 s "
        "es el tiempo de referencia normativo para normalizar DₙT."
    )
    if tr_bands:
        st.dataframe(
            pd.DataFrame([
                {"Octava (Hz)": row.get("Banda (Hz)", ""),
                 "TR dormitorio (s)": row.get("TR dormitorio (s)", "")}
                for row in tr_bands
            ]),
            hide_index=True, use_container_width=True
        )
        if any(not _positive(row.get("TR dormitorio (s)")) for row in tr_bands):
            st.warning("Hay valores TR sin completar en la Etapa 3: revisa esas bandas.")
    else:
        st.warning(
            "No se encontraron tiempos TR por bandas guardados en la Etapa 3 "
            "para este alumno. Completa y guarda los resultados allí."
        )

    st.markdown("**Flancos aéreos · ficha de entradas para SONARA (ISO 12354-1)**")
    st.info(
        "Se reproduce la estructura real de los **cinco flancos** de SONARA. "
        "El ejercicio entrega materialidad, longitudes y las masas superficiales "
        "de referencia; los R laterales iniciales de 45/55 dB son **supuestos docentes "
        "provisionales**, no ensayos. El alumno registra **Kij** calculado "
        "en SONARA y conserva los detalles del proyecto en su JSON."
    )
    # HM-01 (3,10 m) y HG-01 (2,50 m) son las cotas docentes
    # explicitadas en la pauta geométrica de la Etapa 2.
    # Las medidas guardadas por el alumno siempre tienen prioridad.
    source_length = _filled(geo.get("length"), "3,10")
    source_height = _filled(geo.get("height"), "2,50")
    st.caption(
        "Longitudes de las juntas: **3,10 m** para losas de piso/cielo "
        "(HM-01) y **2,50 m** para muros laterales/fachada (HG-01) "
        "si la Etapa 2 aún no tiene cotas guardadas. "
        "Son **supuestos docentes de referencia**, no medidas de obra."
    )
    flank_columns = [
        "Flanco SONARA", "Activo", "Material / hipótesis",
        "R emisor (dB)", "R receptor (dB)", "Longitud lᵢⱼ (m)",
        "m' emisor (kg/m²)", "m' receptor (kg/m²)",
        "Tipo de unión SONARA", "Kij SONARA (dB)"
    ]
    flank_specs = [
        ("Muro lateral 1", True, "HA 180 mm · docente", "45", source_height, "432", "432"),
        ("Muro lateral 2", True, "HA 180 mm · docente", "45", source_height, "432", "432"),
        ("Fachada / elemento lateral", False, "Fachada HA 150 mm · F-01", "45", source_height, "360", "360"),
        ("Losa de piso", False, "HA 160 mm · L-01", "55", source_length, "384", "384"),
        ("Losa de cielo", False, "HA 160 mm · L-01", "55", source_length, "384", "384")
    ]
    old_flanks = previous_system.get("flanks") or []
    by_name = {str(row.get("Flanco SONARA") or row.get("Vía / encuentro") or ""): row
               for row in old_flanks if isinstance(row, dict)}
    flank_rows = []
    for name, active, material, rw, length, m1, m2 in flank_specs:
        previous = by_name.get(name, {})
        flank_rows.append({
            "Flanco SONARA": name, "Activo": "Sí" if active else "No",
            "Material / hipótesis": material,
            "R emisor (dB)": rw, "R receptor (dB)": rw,
            "Longitud lᵢⱼ (m)": length,
            "m' emisor (kg/m²)": m1, "m' receptor (kg/m²)": m2,
            "Tipo de unión SONARA": "Manual",
            "Kij SONARA (dB)": _filled(previous.get("Kij SONARA (dB)"),
                                     previous.get("Kij / Dv,ij / fuente"))
        })
    flanks = st.data_editor(
        pd.DataFrame(flank_rows, columns=flank_columns),
        key="c5l2_s4_flanks_sonara_inputs_v3", num_rows="fixed",
        hide_index=True, use_container_width=True,
        disabled=flank_columns[:-1],
        column_config={
            "Kij SONARA (dB)": st.column_config.TextColumn(
                "Kij calculado (dB)", help="Única columna editable: Kij de SONARA."
            )
        }
    ).fillna("").to_dict("records")
    st.caption(
        "Mantén los mismos flancos activos en SONARA que en la ficha. "
        "Para cambiar la hipótesis docente inicial o activar otro flanco, "
        "justifícalo en el proyecto JSON. Los R orientativos no son el "
        "resultado Rw calculado del flanco: reemplázalos en SONARA por el "
        "modelo calculado si dispones de él. 432, 384 y 360 kg/m² son "
        "masas nominales obtenidas de espesor × 2.400 kg/m³."
    )
    if not _filled(geo.get("length")) or not _filled(geo.get("height")):
        st.warning(
            "Las longitudes de unión mostradas son **cotas docentes** "
            "HM-01/HG-01 porque todavía no hay dimensiones AI-01 guardadas "
            "en la Etapa 2. Al guardar allí las cotas, se recuperarán aquí."
        )

    st.markdown("#### C · Propuesta libre de mejoramiento")
    st.info(
        "El diseño es **libre**: no hay una solución constructiva preseleccionada "
        "ni una tabla obligatoria de capas. Propón una mejora del muro M-01, "
        "describe sus materiales y justifica cómo se monta y cómo trata "
        "los flancos y puentes rígidos. Después simula la condición "
        "original y la mejorada en SONARA."
    )
    old_detail = old.get("design_detail") or {}
    improvement = st.text_area(
        "Materiales, composición y dimensiones de la solución propuesta",
        value=old_detail.get("materials", old_detail.get("improvement", "")),
        key="c5l2_s4_materials_free_v1", height=135,
        placeholder="Describe libremente las capas, espesores, masa superficial, cavidad, absorbentes u otros componentes que hayas elegido..."
    )
    mounting = st.text_area(
        "Montaje, encuentros, fijaciones y tratamiento de transmisiones laterales",
        value=old_detail.get("mounting", ""),
        key="c5l2_s4_mounting_free_v1", height=125,
        placeholder="Explica cómo se instala, cómo se conecta o desacopla y qué ocurre en las uniones con piso, cielo y muros laterales..."
    )
    evidence = st.text_area(
        "Supuestos y respaldo técnico de los materiales",
        value=old_detail.get("evidence", ""),
        key="c5l2_s4_evidence_free_v1", height=90,
        placeholder="Documenta los datos de entrada o fichas técnicas utilizados y las limitaciones de tu propuesta."
    )
    st.markdown("#### D · Resultados y proyectos JSON de SONARA")
    st.caption(
        "Descarga cada proyecto desde SONARA → **Guardar como JSON**. "
        "Adjunta aquí el proyecto **original** y el proyecto con la **mejora** "
        "por separado. El laboratorio conserva una copia para que el docente "
        "revise la geometría, los materiales, los flancos y los resultados."
    )
    st.warning(
        "SONARA muestra **DₙT,50 proyectado**, con estimación en 50–80 Hz "
        "cuando no hay espectro de ensayo: es una predicción académica, "
        "no una medición ni una certificación."
    )

    def _sonara_candidates(document):
        """Find ISO 12354-1 saved solutions in a single-project SONARA export."""
        if not isinstance(document, dict) or len(document) != 1:
            return [], None
        project_id, project = next(iter(document.items()))
        if not isinstance(project, dict) or project.get("id") != project_id:
            return [], None
        if not isinstance(project.get("nombre"), str):
            return [], None
        if not all(isinstance(project.get(k, []), list)
                   for k in ("requerimientos", "soluciones", "recintos")):
            return [], None
        solutions = []
        for sol in project.get("soluciones", []):
            if isinstance(sol, dict):
                solutions.append(sol)
        for req in project.get("requerimientos", []):
            if not isinstance(req, dict):
                return [], None
            if not isinstance(req.get("soluciones", []), list):
                return [], None
            for sol in req.get("soluciones", []):
                if isinstance(sol, dict):
                    solutions.append(sol)
        return solutions, project.get("nombre")

    def _metric_from_solution(solution, field):
        value = solution.get(field)
        if value is None or isinstance(value, bool):
            return None
        try:
            number = float(str(value).replace(",", "."))
            return round(number, 2) if math.isfinite(number) else None
        except (ValueError, TypeError):
            return None

    old_results = old.get("model_results") or []
    saved_files = old.get("sonara_json") or {}
    uploads = {}
    active_json = {}
    for idx, (key, title) in enumerate((
        ("original", "Condición original · M-01"),
        ("mejora", "Solución mejorada"),
    )):
        previous_file = saved_files.get(key) if isinstance(saved_files, dict) else None
        cols = st.columns([2, 3])
        with cols[0]:
            uploaded = st.file_uploader(
                f"📎 JSON SONARA · {title}", type=["json"],
                key=f"c5l2_s4_sonara_file_{key}_v1",
                help="Archivo de un solo proyecto, descargado con Guardar como JSON en SONARA.",
            )
        data = previous_file if isinstance(previous_file, dict) else None
        if uploaded is not None:
            raw = uploaded.getvalue()
            if len(raw) > 2 * 1024 * 1024:
                st.error(f"{title}: el JSON supera el límite de 2 MB.")
                data = None
            else:
                try:
                    loaded = json.loads(raw.decode("utf-8-sig"))
                    candidates, project_name = _sonara_candidates(loaded)
                    if project_name is None:
                        raise ValueError(
                            "Formato no reconocido. Exporta un proyecto individual "
                            "desde SONARA → Guardar como JSON."
                        )
                    import hashlib
                    data = {
                        "filename": uploaded.name,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "project_name": project_name,
                        "document": loaded,
                    }
                    st.success(f"{title}: proyecto «{project_name}» reconocido.")
                except (UnicodeDecodeError, ValueError) as exc:
                    st.error(f"{title}: {exc}")
                    data = None
        if data:
            active_json[key] = data
            candidates, project_name = _sonara_candidates(data.get("document"))
            with cols[1]:
                st.caption(
                    f"**Adjunto:** {data.get('filename', 'SONARA.json')} · "
                    f"Proyecto: {project_name or 'Sin título'} · "
                    f"{len(candidates)} solución(es) guardada(s)."
                )
                if not candidates:
                    st.warning(
                        "El archivo contiene el proyecto, pero no soluciones "
                        "ISO guardadas. Guarda la simulación en SONARA y "
                        "descarga nuevamente el JSON para importar resultados."
                    )
                options = []
                for number, sol in enumerate(candidates):
                    if str(sol.get("tipo_calculo", "")).lower().strip() == "iso 12354-1" or (
                        "dntw" in sol or "dnt50" in sol
                    ):
                        options.append((number, sol))
                if options:
                    selected_index = st.selectbox(
                        "Solución registrada en SONARA",
                        range(len(options)),
                        format_func=lambda n: str(
                            options[n][1].get("nombre")
                            or f"Solución {options[n][0] + 1}"
                        ),
                        key=f"c5l2_s4_selected_sonara_{key}_v1",
                    )
                    chosen = options[selected_index][1]
                    st.caption(
                        "Valores extraídos del JSON · "
                        f"DₙT,w: {_metric_from_solution(chosen, 'dntw')} dB · "
                        f"DₙT,50: {_metric_from_solution(chosen, 'dnt50')} dB."
                    )
                    active_json[key]["selected_solution_id"] = str(
                        chosen.get("id") or options[selected_index][0]
                    )
                    active_json[key]["extracted"] = {
                        "dntw": _metric_from_solution(chosen, "dntw"),
                        "dnt50": _metric_from_solution(chosen, "dnt50"),
                    }
                else:
                    st.info(
                        "No hay una solución de ISO 12354-1 identificable "
                        "en el archivo. Puedes registrar los valores manualmente."
                    )
            with st.expander(f"🔎 Revisar respaldo JSON · {title}", expanded=False):
                st.json(data["document"], expanded=False)
        elif uploaded is None:
            with cols[1]:
                st.caption("Sin JSON adjunto. Puedes guardar un avance incompleto.")
        uploads[key] = data

    st.markdown("**Comparación de indicadores globales**")
    result_columns = ["Modelo", "DₙT,w (dB)", "DₙT,50 proyectado (dB)",
                      "Respaldo JSON"]
    result_rows = []
    for idx, (key, label) in enumerate((
        ("original", "Original M-01"), ("mejora", "Mejora propuesta")
    )):
        previous = old_results[idx] if idx < len(old_results) and isinstance(old_results[idx], dict) else {}
        descriptor = previous.get("Descriptor calculado")
        global_value = previous.get("Resultado global (dB)")
        extracted = (uploads.get(key) or {}).get("extracted") or {}
        result_rows.append({
            "Modelo": label,
            "DₙT,w (dB)": _filled(
                extracted.get("dntw"), previous.get("DₙT,w (dB)"),
                global_value if descriptor == "DₙT,w" else ""),
            "DₙT,50 proyectado (dB)": _filled(
                extracted.get("dnt50"), previous.get("DₙT,50 proyectado (dB)"),
                global_value if descriptor == "DₙT,50" else ""),
            "Respaldo JSON": "✓ Proyecto guardado" if uploads.get(key) else "Pendiente",
            "Archivo / respaldo SONARA": _filled(
                previous.get("Archivo / respaldo SONARA"),
                (uploads.get(key) or {}).get("filename")),
        })
    results = st.data_editor(
        pd.DataFrame(result_rows, columns=result_columns),
        key="c5l2_s4_results_with_json_v1",
        hide_index=True, num_rows="fixed", use_container_width=True,
        disabled=["Modelo", "Respaldo JSON"],
        column_config={
            "DₙT,w (dB)": st.column_config.NumberColumn("DₙT,w (dB)", format="%.1f"),
            "DₙT,50 proyectado (dB)": st.column_config.NumberColumn(
                "DₙT,50 proyectado (dB)", format="%.1f"),
        },
    ).fillna("").to_dict("records")
    for row in results:
        row.pop("Respaldo JSON", None)
    st.caption(
        "Los valores se precargan de la solución ISO 12354-1 del JSON "
        "cuando están presentes; en caso contrario puedes ingresarlos "
        "manualmente. El docente revisará el proyecto adjunto."
    )
    st.markdown("#### E · Comprobación de la exigencia Clase B")
    st.info(
        "**Meta del caso AI-01 · ISO/TS 19488:2021, Tabla 1, Clase B:** "
        "**DₙT,50 ≥ 54 dB** para habitaciones habitables de viviendas distintas. "
        "Compara el resultado que corresponda al descriptor; un valor "
        "aislado DₙT,w no permite verificar directamente el umbral DₙT,50."
    )
    if criterion:
        st.caption(
            "Criterio consignado en Etapa 1: "
            + _val(criterion.get("descriptor")) + " · "
            + _val(criterion.get("direction")) + " "
            + _val(criterion.get("limit")) + ". "
            "Si difiere, revisa la fila aplicable de la norma."
        )
    st.caption(
        "Se compara el **DₙT,50 proyectado de la mejora**, no el DₙT,w. "
        "Un valor igual o mayor a 54 dB supera la meta académica de esta etapa."
    )
    try:
        original_value = float(str(results[0].get("DₙT,50 proyectado (dB)", "")).replace(",", "."))
        improved_value = float(str(results[1].get("DₙT,50 proyectado (dB)", "")).replace(",", "."))
        if math.isfinite(original_value) and math.isfinite(improved_value):
            margin = improved_value - 54
            delta = improved_value - original_value
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Mejora estimada en DₙT,50", f"{delta:+.1f} dB")
            with m2:
                st.metric("Margen frente a Clase B", f"{margin:+.1f} dB")
            if margin >= 0:
                st.success("La predicción académica alcanza la meta de la etapa.")
            else:
                st.warning("La predicción académica no alcanza todavía la meta Clase B.")
    except (ValueError, TypeError, IndexError):
        st.info("Ingresa ambos resultados DₙT,50 para ver la mejora y el margen automáticamente.")
    comparison = st.text_area(
        "Conclusión técnica y limitaciones del diseño",
        value=old_detail.get("comparison", ""), key="c5l2_s4_comparison_v2",
        placeholder="Compara original y mejora, explica el margen y señala restricciones del modelo..."
    )
    selected_descriptor = "DₙT,50"
    payload = {
        "case": "AI-01", "iso_geometry": geo,
        "systems": {"model_type": model_type, "data_origin": data_origin,
                    "t0": reference_time, "flanks": flanks},
        "model_results": results,
        "sonara_json": uploads,
        "design_detail": {
            "materials": improvement, "mounting": mounting,
            "improvement": improvement, "evidence": evidence,
            "descriptor": selected_descriptor, "comparison": comparison
        },
        "schema_version": "c5l2_airborne_iso12354_v3"
    }
    a, b = st.columns(2)
    with a:
        draft = st.button(
            "💾 Guardar avance", key="c5l2_s4_draft_iso_v1", use_container_width=True
        )
    with b:
        finish = st.button(
            "✓ Completar Etapa 4", key="c5l2_s4_finish_iso_v1",
            type="primary", use_container_width=True
        )
    if draft:
        _save(lab, saved, 4, "c5l2_s4", payload, complete=False)
    if finish:
        essentials = ["length", "height", "surface", "receiver_volume",
                      "receiver_area"]
        missing = [key for key in essentials if not _positive(geo.get(key))]
        measured = len(results) == 2 and all(
            _positive(r.get("DₙT,50 proyectado (dB)")) for r in results
        )
        if missing:
            st.warning("Faltan dimensiones o volumen del modelo receptor: "
                       + ", ".join(missing) + ". Guarda avance mientras completas.")
        elif not data_origin.strip() or not reference_time.strip():
            st.warning("Indica la fuente acústica del muro original y T₀.")
        elif not measured or len(results) != 2:
            st.warning("Registra el DₙT,50 proyectado del modelo original y de la mejora.")
        elif not all(uploads.get(key) for key in ("original", "mejora")):
            st.warning("Adjunta y guarda los JSON SONARA de la condición original y la mejora.")
        elif not all([improvement.strip(), mounting.strip(), evidence.strip(),
                      comparison.strip()]):
            st.warning("Documenta materiales, montaje, respaldo y conclusión técnica.")
        else:
            _save(lab, saved, 4, "c5l2_s4", payload, complete=True)


def _stage5(lab, saved):
    """Impact-noise design: same pedagogical structure as airborne Stage 4."""
    import hashlib
    import pandas as pd

    _header(5)
    old = saved.get("c5l2_s5") or {}
    geometry = saved.get("c5l2_s2") or {}
    reverberation = saved.get("c5l2_s3") or {}
    criterion = ((saved.get("c5l2_s1") or {}).get("criteria") or {}).get("IM-01") or {}
    rooms = {str(r.get("Caso") or ""): r for r in geometry.get("rooms", [])
             if isinstance(r, dict)}
    separations = {str(r.get("Caso") or ""): r for r in geometry.get("separations", [])
                   if isinstance(r, dict)}
    room = rooms.get("IM-01", {})
    slab = separations.get("IM-01", {})
    tr_room = (reverberation.get("tr_rooms") or {}).get("Dormitorio", {})
    tr_bands = reverberation.get("tr_bands") or []

    def _pick(*values):
        for v in values:
            if v is not None and str(v).strip():
                return v
        return ""

    def _number(value):
        try:
            v = float(str(value).strip().replace(",", "."))
            return v if math.isfinite(v) else None
        except (ValueError, TypeError):
            return None

    st.markdown("### IM-01 · Aislamiento al ruido de impacto entre viviendas")
    st.info(
        "**Fuente:** dormitorio de vivienda distinta del piso 6, sobre "
        "CH-A-P05-S03. **Receptor:** dormitorio de CH-A-P05-S03, piso 5. "
        "Evalúa la **losa superior del dormitorio receptor** (L-01). "
        "Utiliza SONARA con ISO 12354-2 e ISO 717-2: modela la base "
        "y una mejora constructiva libre, con vías laterales."
    )
    st.caption(
        "Ruta de trabajo: A · geometría previa → B · losa y transmisión → "
        "C · mejora libre → D · dos JSON SONARA y resultados → E · Clase B."
    )

    st.markdown("#### A · Geometría del entrepiso y dormitorio receptor")
    st.caption(
        "La Etapa 2 proporciona la geometría IM-01 del dormitorio y la "
        "**superficie de la losa superior**; la Etapa 3 aporta TR y, "
        "si falta, volumen del dormitorio. Los campos recuperados son de "
        "solo lectura y se corrigen en su etapa de origen."
    )
    defaults = {
        "slab_length": slab.get("Longitud (m)", ""),
        "slab_width": slab.get("Altura (m)", ""),
        "slab_area": slab.get("Superficie (m²)", ""),
        "room_length": room.get("Largo (m)", ""),
        "room_width": room.get("Ancho (m)", ""),
        "room_height": _pick(room.get("Altura (m)"), tr_room.get("height")),
        "room_area": _pick(room.get("Área (m²)"), tr_room.get("area")),
        "room_volume": _pick(room.get("Volumen (m³)"), tr_room.get("volume")),
        "drawing": _pick(slab.get("Plano / cota"), room.get("Plano / cota")),
    }
    if not defaults["slab_area"]:
        a, b = _number(defaults["slab_length"]), _number(defaults["slab_width"])
        if a is not None and b is not None:
            defaults["slab_area"] = f"{a*b:.3f}"
    if not defaults["room_area"]:
        a, b = _number(defaults["room_length"]), _number(defaults["room_width"])
        if a is not None and b is not None:
            defaults["room_area"] = f"{a*b:.3f}"
    if not defaults["room_volume"]:
        a, b = _number(defaults["room_area"]), _number(defaults["room_height"])
        if a is not None and b is not None:
            defaults["room_volume"] = f"{a*b:.3f}"
    previous_geo = old.get("iso_geometry") or {}
    signature = hashlib.sha256(
        json.dumps({"stage2": geometry, "stage3": reverberation},
                   ensure_ascii=False, sort_keys=True, default=str).encode()
    ).hexdigest()[:12]
    fields = [
        ("slab_length", "Largo de losa superior (m)"),
        ("slab_width", "Ancho de losa superior (m)"),
        ("slab_area", "Superficie de entrepiso (m²)"),
        ("room_length", "Largo dormitorio receptor (m)"),
        ("room_width", "Ancho dormitorio receptor (m)"),
        ("room_height", "Altura dormitorio receptor (m)"),
        ("room_area", "Área dormitorio receptor (m²)"),
        ("room_volume", "Volumen dormitorio receptor (m³)"),
    ]
    n_recovered = sum(bool(str(defaults.get(k) or "").strip()) for k in defaults)
    if n_recovered:
        st.success(f"Se recuperaron {n_recovered} campos geométricos/referencias de las etapas previas.")
    else:
        st.warning("No hay geometría IM-01 guardada. Revisa y guarda primero la Etapa 2 y la Etapa 3 en esta misma cuenta.")
    geo = {}
    for i in range(0, len(fields), 3):
        cols = st.columns(3)
        for col, (key, label) in zip(cols, fields[i:i+3]):
            recovered = defaults.get(key, "")
            with col:
                geo[key] = st.text_input(
                    label, value=str(_pick(recovered, previous_geo.get(key))),
                    key=f"c5l2_s5_geom_{key}_{signature}",
                    disabled=bool(str(recovered or "").strip()),
                    help="Valor recuperado de la etapa previa; corrígelo allí." if recovered else
                         "Dato no guardado previamente: anótalo desde el plano o una hipótesis documentada."
                )
    geo["drawing"] = st.text_input(
        "Plano / cota del entrepiso",
        value=str(_pick(defaults["drawing"], previous_geo.get("drawing"))),
        key=f"c5l2_s5_drawing_{signature}",
        disabled=bool(str(defaults["drawing"] or "").strip())
    )
    geo["source_basis"] = st.text_input(
        "Hipótesis de recinto excitador / superposición de planta",
        value=str(previous_geo.get("source_basis", "")),
        key="c5l2_s5_source_basis",
        help="La planta tipo acredita superposición en planta, pero no todos los detalles del montaje."
    )
    st.caption(
        "Para IM-01 se considera la **losa de cielo del dormitorio receptor**, "
        "no su piso. La superficie horizontal se obtiene de la planta del recinto "
        "y la configuración del suelo excitado pertenece al nivel superior."
    )

    st.markdown("#### B · Losa original, reverberación y flanqueos")
    st.table([{
        "Código": "L-01", "Elemento": "Losa separadora",
        "Configuración original": "HA 160 mm + mortero 30 mm + cerámica 10 mm",
        "Condición de montaje": "Sin capa resiliente ni cielo suspendido"
    }])
    st.caption(
        "Densidad de HA de referencia docente: 2.400 kg/m³ → masa nominal "
        "solo de la losa HA: 384 kg/m². El mortero y la cerámica deben "
        "caracterizarse por separado en SONARA; la masa total no se presume."
    )
    st.markdown("**TR(f) del dormitorio receptor · recuperado de Etapa 3**")
    if tr_bands:
        st.dataframe(pd.DataFrame([
            {"Banda Hz": r.get("Banda (Hz)", ""),
             "TR dormitorio (s)": r.get("TR dormitorio (s)", "")}
            for r in tr_bands
        ]), hide_index=True, use_container_width=True)
    else:
        st.warning("No hay TR por bandas guardado en Etapa 3; completa el cálculo allí.")
    old_base = old.get("base_inputs") or {}
    base1, base2, base3 = st.columns(3)
    with base1:
        mode = st.selectbox(
            "Modelo SONARA",
            ["ISO 12354-2", "Simplificado (justificar)"],
            index=1 if old_base.get("mode") == "Simplificado (justificar)" else 0,
            key="c5l2_s5_mode")
    with base2:
        t0 = st.text_input(
            "T₀ normativo (s) · distinto de TR",
            value=str(old_base.get("t0", "0.5")), key="c5l2_s5_t0")
    with base3:
        base_source = st.text_input(
            "Origen de propiedades acústicas de la losa",
            value=str(old_base.get("source", "")), key="c5l2_s5_base_source",
            placeholder="Catálogo SONARA / curva / ficha técnica")
    st.markdown("**Flanqueos de impacto · ficha de entradas para SONARA (ISO 12354-2)**")
    st.info(
        "SONARA utiliza **cuatro flancos**: Muro lateral 1, Muro lateral 2, "
        "Fachada / elemento lateral y Tabique separador / elemento vertical. "
        "Se entrega una ficha docente de datos de entrada; el estudiante "
        "solo completa **Kij (dB)** con el valor aplicado en SONARA."
    )
    length_from_stage2 = _number(geo.get("slab_length"))
    width_from_stage2 = _number(geo.get("slab_width"))
    union_length = length_from_stage2 if length_from_stage2 is not None and length_from_stage2 > 0 else 2.60
    union_width = width_from_stage2 if width_from_stage2 is not None and width_from_stage2 > 0 else 3.10
    if length_from_stage2 is None or width_from_stage2 is None:
        st.warning(
            "Se usan las cotas docentes de referencia 2,60 × 3,10 m donde "
            "no existe geometría IM-01 guardada; confirma las longitudes "
            "en la Etapa 2 antes de finalizar."
        )
    fl_cols = [
        "Flanco SONARA", "Activo", "Material / hipótesis",
        "R emisor (dB)", "R receptor (dB)", "Longitud unión (m)",
        "m' emisor (kg/m²)", "m' receptor (kg/m²)",
        "Tipo unión SONARA", "Kij SONARA (dB)"
    ]
    fl_specs = [
        ("Muro lateral 1", True, "HA 180 mm · docente", union_length, "432", "432"),
        ("Muro lateral 2", True, "HA 180 mm · docente", union_length, "432", "432"),
        ("Fachada / elemento lateral", False, "HA 150 mm · F-01", union_width, "360", "360"),
        ("Tabique separador / elemento vertical", False, "HA 180 mm · docente", union_width, "432", "432"),
    ]
    old_flanks = old_base.get("flanks") or []
    old_by_name = {
        str(row.get("Flanco SONARA") or row.get("Encuentro") or ""): row
        for row in old_flanks if isinstance(row, dict)
    }
    fl_def = []
    for index, (name, active, material, length, mass_source, mass_receiver) in enumerate(fl_specs):
        previous = old_by_name.get(name, {})
        if not previous and index < len(old_flanks) and isinstance(old_flanks[index], dict):
            previous = old_flanks[index]
        fl_def.append({
            "Flanco SONARA": name, "Activo": "Sí" if active else "No",
            "Material / hipótesis": material,
            "R emisor (dB)": "50", "R receptor (dB)": "50",
            "Longitud unión (m)": f"{length:.2f}",
            "m' emisor (kg/m²)": mass_source,
            "m' receptor (kg/m²)": mass_receiver,
            "Tipo unión SONARA": "Manual",
            "Kij SONARA (dB)": str(previous.get("Kij SONARA (dB)", ""))
        })
    flanks = st.data_editor(
        pd.DataFrame(fl_def, columns=fl_cols), hide_index=True,
        num_rows="fixed", use_container_width=True,
        disabled=fl_cols[:-1], key="c5l2_s5_flanks_sonara_inputs_v3",
        column_config={
            "Kij SONARA (dB)": st.column_config.TextColumn(
                "Kij calculado (dB)",
                help="Única columna editable: Kij aplicado en SONARA para cada flanco."
            )
        }
    ).fillna("").to_dict("records")
    st.caption(
        "R emisor = R receptor = 50 dB son **valores docentes de trabajo** "
        "(coinciden con los valores iniciales manuales del módulo SONARA), "
        "**no propiedades ensayadas** de los muros. Las masas nominales "
        "corresponden a la hipótesis HA de 2.400 kg/m³: "
        "180 mm → 432 kg/m² y 150 mm → 360 kg/m². "
        "Los cuatro flancos, sus estados de activación y las opciones de "
        "unión se deben reproducir en SONARA. Si cambian para la variante, "
        "el JSON conserva las nuevas entradas."
    )

    st.markdown("#### C · Diseño libre de la mejora de impacto")
    st.info(
        "El alumno elige **libremente** un tratamiento en el piso superior "
        "o en la construcción (piso flotante, subcapa resiliente, "
        "cielo suspendido desacoplado, u otro). No se prescribe una "
        "solución ni se entrega un ΔLw supuesto."
    )
    old_design = old.get("design_detail") or {}
    materials = st.text_area(
        "Composición propuesta, materiales y espesores",
        value=str(old_design.get("materials", "")),
        height=125, key="c5l2_s5_materials",
        placeholder="Capas y espesores; características de la subcapa, masa de sobrelosa y/o cielo..."
    )
    mounting = st.text_area(
        "Montaje, continuidad, encuentros y puentes rígidos",
        value=str(old_design.get("mounting", "")),
        height=110, key="c5l2_s5_mounting",
        placeholder="Juntas perimetrales, apoyos, uniones, desacople y tratamiento de flancos..."
    )
    evidence = st.text_area(
        "Parámetros de entrada SONARA y respaldo técnico",
        value=str(old_design.get("evidence", "")),
        height=95, key="c5l2_s5_evidence",
        placeholder="Rigidez dinámica, masa superficial, ΔLw si aplica, espectros, fichas y supuestos..."
    )

    st.markdown("#### D · Resultados SONARA y archivos JSON")
    st.info(
        "Para Clase B del caso IM-01 se exigen **ambas condiciones** "
        "de ISO/TS 19488:2021, Tabla 2: **L′ₙT,w ≤ 50 dB** "
        "**Y L′ₙT,50 ≤ 54 dB**. Cuanto más bajos sean los niveles, "
        "mejor es el aislamiento al ruido de impacto."
    )
    st.caption(
        "En SONARA guarda la simulación de impacto en el proyecto y descarga "
        "**Guardar como JSON**. Adjunta el original y la mejora, "
        "cada uno con su solución guardada. Se conserva el JSON completo "
        "para la revisión docente."
    )
    def _solutions(document):
        if not isinstance(document, dict) or len(document) != 1:
            return None, []
        pid, project = next(iter(document.items()))
        if not isinstance(project, dict) or project.get("id") != pid:
            return None, []
        if not isinstance(project.get("nombre"), str):
            return None, []
        if not all(isinstance(project.get(k, []), list)
                   for k in ("recintos", "requerimientos", "soluciones")):
            return None, []
        sols = list(project.get("soluciones") or [])
        for req in project.get("requerimientos") or []:
            if not isinstance(req, dict) or not isinstance(req.get("soluciones", []), list):
                return None, []
            sols.extend(req.get("soluciones", []))
        return project.get("nombre"), [
            row for row in sols if isinstance(row, dict) and (
                row.get("tipo_calculo") == "Ruido de impacto"
                or "lntw" in row or "lnt50" in row)
        ]

    saved_json = old.get("sonara_json") or {}
    attachments = {}
    extracted_values = {}
    for key, title in (("original", "Losa original L-01"),
                       ("mejora", "Solución mejorada")):
        upload = st.file_uploader(
            "📎 Proyecto SONARA JSON · " + title,
            type=["json"], key="c5l2_s5_json_" + key
        )
        attached = saved_json.get(key) if isinstance(saved_json, dict) else None
        if upload is not None:
            raw = upload.getvalue()
            if len(raw) > 2 * 1024 * 1024:
                st.error("El JSON supera 2 MB: " + title)
                attached = None
            else:
                try:
                    document = json.loads(raw.decode("utf-8-sig"))
                    project_name, sols = _solutions(document)
                    if project_name is None:
                        raise ValueError("El archivo no es un proyecto individual SONARA válido.")
                    attached = {
                        "filename": upload.name,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "project_name": project_name,
                        "document": document,
                    }
                    st.success("Archivo de proyecto reconocido: " + project_name)
                except (UnicodeDecodeError, ValueError) as exc:
                    st.error(f"{title}: {exc}")
                    attached = None
        if isinstance(attached, dict) and attached.get("document"):
            project_name, sols = _solutions(attached["document"])
            attachments[key] = attached
            st.caption(f"{title}: {attached.get('filename', '')} · {len(sols)} solución(es) de impacto.")
            if sols:
                selected = st.selectbox(
                    "Selecciona la solución de impacto en el proyecto · " + title,
                    range(len(sols)),
                    format_func=lambda n: str(sols[n].get("nombre") or f"Solución {n+1}"),
                    key="c5l2_s5_solution_" + key
                )
                sol = sols[selected]
                extracted_values[key] = {
                    "lntw": _number(sol.get("lntw")),
                    "lnt50": _number(sol.get("lnt50")),
                }
                attachments[key]["selected_solution_id"] = str(sol.get("id") or selected)
                st.caption(
                    f"Resultados JSON · L′ₙT,w = {extracted_values[key]['lntw']} dB; "
                    f"L′ₙT,50 = {extracted_values[key]['lnt50']} dB."
                )
            else:
                st.warning("No hay una solución de impacto guardada dentro de este JSON.")
            with st.expander("Ver JSON · " + title):
                st.json(attached["document"], expanded=False)
        else:
            st.caption("JSON pendiente: " + title)

    cols = ["Modelo", "L′ₙT,w (dB)", "L′ₙT,50 (dB)", "Respaldo JSON"]
    prev_rows = old.get("model_results") or []
    initial_rows = []
    for idx, (key, label) in enumerate((("original", "Losa original"),
                                        ("mejora", "Mejora propuesta"))):
        prev = prev_rows[idx] if idx < len(prev_rows) and isinstance(prev_rows[idx], dict) else {}
        found = extracted_values.get(key) or {}
        initial_rows.append({
            "Modelo": label,
            "L′ₙT,w (dB)": _pick(found.get("lntw"), prev.get("L′ₙT,w (dB)")),
            "L′ₙT,50 (dB)": _pick(found.get("lnt50"), prev.get("L′ₙT,50 (dB)")),
            "Respaldo JSON": "✓" if attachments.get(key) else "Pendiente"
        })
    results = st.data_editor(
        pd.DataFrame(initial_rows, columns=cols), key="c5l2_s5_results_v1",
        hide_index=True, use_container_width=True, num_rows="fixed",
        disabled=["Modelo", "Respaldo JSON"],
        column_config={
            "L′ₙT,w (dB)": st.column_config.NumberColumn("L′ₙT,w (dB)", format="%.1f"),
            "L′ₙT,50 (dB)": st.column_config.NumberColumn("L′ₙT,50 (dB)", format="%.1f")
        }
    ).fillna("").to_dict("records")
    for row in results:
        row.pop("Respaldo JSON", None)
    st.caption(
        "SONARA guarda lntw y lnt50 en las soluciones de impacto. "
        "Si no dispone de espectro suficiente para L′ₙT,50, "
        "no presumas el resultado. Si solo está disponible L′ₙT,w, "
        "registra el avance, pero no declares Clase B."
    )

    st.markdown("#### E · Comprobación de Clase B y conclusión")
    if criterion:
        st.caption(
            "Criterio ingresado en Etapa 1: " +
            str(criterion.get("descriptor", "")) + " " +
            str(criterion.get("direction", "")) + " " +
            str(criterion.get("limit", "")) + "."
        )
    st.info(
        "**Clase B · impacto entre viviendas:** "
        "L′ₙT,w ≤ 50 dB **y** L′ₙT,50 ≤ 54 dB "
        "(ISO/TS 19488:2021, Tabla 2). "
        "Los dos requisitos deben cumplirse simultáneamente."
    )
    if len(results) == 2:
        base_w = _number(results[0].get("L′ₙT,w (dB)"))
        new_w = _number(results[1].get("L′ₙT,w (dB)"))
        base_50 = _number(results[0].get("L′ₙT,50 (dB)"))
        new_50 = _number(results[1].get("L′ₙT,50 (dB)"))
        if all(v is not None for v in (base_w, new_w, base_50, new_50)):
            c1, c2, c3 = st.columns(3)
            c1.metric("Reducción de L′ₙT,w", f"{base_w-new_w:+.1f} dB")
            c2.metric("Margen Clase B · L′ₙT,w", f"{50-new_w:+.1f} dB")
            c3.metric("Margen Clase B · L′ₙT,50", f"{54-new_50:+.1f} dB")
            if new_w <= 50 and new_50 <= 54:
                st.success("La mejora alcanza las dos metas académicas de Clase B.")
            else:
                st.warning("La mejora no satisface simultáneamente los dos criterios de Clase B.")
        else:
            st.info("Pendiente: ingresa ambos indicadores del modelo original y mejorado.")
    conclusion = st.text_area(
        "Conclusión técnica, viabilidad y limitaciones del modelo",
        value=str(old_design.get("comparison", "")),
        key="c5l2_s5_conclusion", height=105
    )
    payload = {
        "case": "IM-01", "iso_geometry": geo,
        "base_inputs": {"mode": mode, "t0": t0,
                        "source": base_source, "flanks": flanks},
        "design_detail": {"materials": materials, "mounting": mounting,
                          "evidence": evidence, "comparison": conclusion},
        "model_results": results, "sonara_json": attachments,
        "schema_version": "c5l2_impact_iso12354_v1"
    }
    c1, c2 = st.columns(2)
    draft = c1.button("💾 Guardar avance", key="c5l2_s5_draft_v1", use_container_width=True)
    finish = c2.button("✓ Completar Etapa 5", key="c5l2_s5_finish_v1",
                       type="primary", use_container_width=True)
    if draft:
        _save(lab, saved, 5, "c5l2_s5", payload, complete=False)
    if finish:
        required_geo = ("slab_area", "room_area", "room_volume")
        if any(_number(geo.get(k)) is None or _number(geo.get(k)) <= 0
               for k in required_geo):
            st.warning("Faltan geometría y volumen del dormitorio receptor.")
        elif not all(str(v).strip() for v in
                     (materials, mounting, evidence, conclusion, base_source)):
            st.warning("Completa materiales, montaje, respaldo y conclusión.")
        elif not all(attachments.get(k) for k in ("original", "mejora")):
            st.warning("Adjunta ambos proyectos SONARA JSON con sus cálculos de impacto.")
        elif not all(_number(row.get(k)) is not None for row in results
                     for k in ("L′ₙT,w (dB)", "L′ₙT,50 (dB)")):
            st.warning("Se requieren L′ₙT,w y L′ₙT,50 en ambos modelos.")
        else:
            _save(lab, saved, 5, "c5l2_s5", payload, complete=True)


def _stage6(lab,saved):
    """NoiseMap road scenario + transparent Lden verification + SONARA facade."""
    _header(6)
    st.markdown("### FA-01 · Exposición al tránsito y diseño de fachada")
    st.info("Ubica el receptor exterior en la **fachada sur del ESTAR de CH-A-P05-S03**. Modela **Pasaje Chimbote como pasaje local**, no como una avenida ni como Mirador Azul. La geometría, la distancia y la altura deben documentarse mediante planos; el render es solo conceptual. La exposición exterior NO se fija de antemano.")
    st.link_button("🌍 Abrir NoiseMap · dirección oficial", "https://noisemap-akuzoft.vercel.app/",
                   help="Abre la herramienta de mapa de ruido y continúa con el procedimiento de esta etapa.")
    st.warning(
        "NoiseMap obtiene la **emisión vial CNOSSOS-EU §2.2** por octavas para vehículos "
        "**1, 2, 3, 4a y 4b**, pero la propagación hacia el receptor sigue usando el "
        "**motor exterior educativo**, no el método reglamentario CNOSSOS-EU §2.5. "
        "El Lden calculado se utiliza aquí como **estimación académica**, no como "
        "evaluación reglamentaria de exposición."
    )
    st.caption("Referencia arquitectónica obligatoria: planta tipo Torre A (Parte 1, pág. 8) + elevación SUR Torre A (Parte 2, pág. 5). El render conceptual no es válido para ubicar vanos ni obtener alturas o distancias.")
    st.markdown("#### Procedimiento guiado en NoiseMap · fachada y Lden")
    st.caption(
        "Realiza estos pasos dentro de NoiseMap. El dibujo del edificio es obligatorio "
        "**solo para el cálculo de Lden incidente en fachada** de este ejercicio: "
        "el motor necesita identificar la superficie receptora para excluir su reflexión."
    )
    with st.expander("Ver los 10 pasos: calle → edificio → receptor → Lden → JSON", expanded=True):
        st.markdown("""
**1. Prepara el escenario.** Abre la dirección oficial de **NoiseMap** con el botón anterior.
Usa el mapa para localizar el emplazamiento del ejercicio y consulta los planos de la
Torre A. Trabaja únicamente con el sector del caso **CH-A-P05-S03**, sin trasladar
cotas de otras viviendas.

**2. Dibuja el eje de la calle.** Selecciona la herramienta **Tráfico vial**
y traza sobre el mapa los puntos centrales de **Pasaje Chimbote**, frente a la fachada
sur. Marca al menos dos puntos y pulsa **Finalizar vía**. La calle debe quedar
**fuera del polígono de la vivienda** y en el lado correcto de la fachada.

**3. Dibuja el edificio.** Selecciona la herramienta **Edificio**, marca los
vértices exteriores de la planta del inmueble y utiliza **Cerrar edificio**.
Ajusta su altura a partir del corte o de una **hipótesis explícita**.
**No basta con dibujar la vivienda como un receptor**: el programa necesita
el polígono del edificio para reconocer el muro expuesto. Si aparece
«Dibuja el edificio» en el desplegable, significa que aún no existe
un edificio activo en el mapa.

**4. Ubica el receptor exterior.** Selecciona **Receptor** y crea un punto
frente al **paño sur del estar**, a aproximadamente **0,1 m por fuera de su plano**,
sin introducirlo en el edificio. Evita colocarlo en una esquina.
Establece la **altura sobre el terreno** correspondiente al piso 5, obtenida
del corte; si no se puede verificar, formula y justifica una hipótesis.
No confundas esa altura con el nivel absoluto del terreno.

**5. Configura los vehículos.** Selecciona la **vía dibujada** y edita
las velocidades por categoría. Para este ejercicio usa **30 km/h** y el
pavimento de referencia (asfalto convencional).
Relaciona livianos, medianos, pesados y motocicletas con las categorías
1, 2, 3 y 4b. No reemplaces motocicletas por vehículos pesados.
Los campos 4a (ciclomotores) y 4b (motocicletas) se introducen por separado.

**6. Configura el entorno.** En la misma ficha de vía, revisa
**superficie vial, pendiente y sentido de circulación**; indica el
tipo de intersección únicamente si existe una intersección modelada
y está correctamente ubicada. Registra los supuestos de suelo,
temperatura, humedad y reflexiones utilizados para la propagación
educativa. No inventes valores medidos.

**7. Introduce los tres períodos.** En **Lden de tránsito · tres períodos**,
escribe los **flujos horarios medios** por categoría para
**Día (12 h), Tarde (4 h) y Noche (8 h)**. Los números que
muestra NoiseMap al abrir no son aforos de Chimbote: **reemplázalos**
por los supuestos de la tabla del apartado A. Usa **0 ciclomotores/h (4a)**
en los tres períodos e ingresa los valores de motos en **Motocicletas/h (4b)**.

**8. Selecciona la fachada del ejercicio.** En **Auditoría del receptor en
fachada**, abre **Edificio de la vivienda estudiada** y selecciona el
edificio que dibujaste. Luego, en **Receptor exterior para el cálculo
Lden**, selecciona el punto creado en el paso 4.
La aplicación debe comprobar la distancia
**receptor–fachada**, la distancia **fachada–calle**,
la altura del receptor y si ambos están del lado correcto del muro.

**9. Ejecuta y revisa el cálculo.** Pulsa **Calcular Lden en receptor**.
Si aparece una advertencia geométrica, **corrige el dibujo o el receptor**:
no fuerces un valor. Revisa **Lday, Levening, Lnight y Lden**.
NoiseMap estima el **sonido incidente** excluyendo la reflexión
especular de la **propia fachada**; por ello **no restes 3 dB nuevamente**.
El resultado conserva el alcance **académico/no normativo**.

**10. Exporta y transfiere el resultado.** Pulsa **Exportar resultados JSON**
en NoiseMap. Regresa a esta Etapa 6 y carga el archivo en
**Importar resultado desde NoiseMap**. Comprueba que el JSON corresponde al
**receptor, edificio y vía** elegidos. La ficha lee el archivo al cargarlo.
La ficha recupera la distancia y altura de la auditoría importada; revisa el método y las limitaciones,
y continúa el diseño de la envolvente en **SONARA**.
        """)
        st.info(
            "**Punto de control antes de avanzar:** en NoiseMap deben existir "
            "una **vía**, un **edificio activo** y un **receptor exterior** "
            "frente a la calle, y la auditoría de fachada debe informar una "
            "posición válida. La exportación JSON no sustituye los planos "
            "ni las evidencias de SONARA."
        )
    norm=((saved.get("c5l2_s1") or {}).get("criteria") or {}).get("FA-01") or {}
    if norm:
        st.caption(f"Tu criterio Clase B: {norm.get('descriptor','')} · {norm.get('direction','')} {norm.get('limit','')} · Referencia: {norm.get('reference','')}")
    old=saved.get("c5l2_s6") or {}
    traffic_old=old.get("traffic") or {}
    st.markdown("#### Importar resultado desde NoiseMap · obligatorio")
    uploaded = st.file_uploader("Archivo JSON de Lden en receptor", type=["json"],
                                key="c5l2_noise_import")
    imported = traffic_old.get("noisemap_document") if uploaded is None else None
    if uploaded is not None:
        try:
            raw = uploaded.getvalue()
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("El JSON supera 2 MB.")
            imported = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeError, ValueError):
            st.error("Carga un JSON válido de NoiseMap de hasta 2 MB.")

    levels, audit, method = {}, {}, ""
    computed = None
    if imported is not None:
        try:
            audit = imported["facade_geometry_audit"]
            if imported["incident_sound"] is not True or audit["valid_for_incident_facade_demo"] is not True:
                raise ValueError
            method = imported["method"]
            if not isinstance(method, str) or not method.strip():
                raise ValueError
            raw_levels = imported["receiver_period_levels_dba"]
            levels = {key: raw_levels[key] for key in ("day", "evening", "night")}
            if any(type(value) not in (int, float) or not -20 <= value <= 150
                   for value in levels.values()):
                raise ValueError
            day, evening, night = (levels[k] for k in ("day", "evening", "night"))
            computed = 10 * math.log10((12*10**(day/10) + 4*10**((evening+5)/10)
                                       + 8*10**((night+10)/10))/24)
            st.success("JSON de NoiseMap importado · auditoría de fachada válida.")
            st.caption(f"{imported.get('road_name', '')} · {imported.get('facade_building_name', '')} · {imported.get('receiver_name', '')}")
        except (KeyError, TypeError, ValueError):
            levels, audit, method, imported = {}, {}, "", None
            st.error("Carga el JSON del cálculo incidente con auditoría válida y los tres niveles de período. Usa «Exportar resultados JSON» después de calcular Lden en el receptor.")
    elif uploaded is None:
        st.info("Para completar la etapa, carga el JSON que exporta NoiseMap tras calcular Lden en el receptor.")
    default_flows={"Día":{"Livianos":80,"Pesados medianos":3,"Pesados":1,"Motocicletas":7},
                   "Tarde":{"Livianos":45,"Pesados medianos":1,"Pesados":0,"Motocicletas":4},
                   "Noche":{"Livianos":10,"Pesados medianos":0,"Pesados":0,"Motocicletas":1}}
    st.markdown("#### A · Geometría y exposición exterior")
    geo = saved.get("c5l2_s2") or {}
    facade = (geo.get("facades") or [{}])[0]
    room = next((row for row in geo.get("rooms", []) if row.get("Caso") == "FA-01"), {})
    tr = saved.get("c5l2_s3") or {}
    living_tr = (tr.get("tr_rooms") or {}).get("Estar") or {}
    st.table([{**facade, "Volumen receptor (m³)": room.get("Volumen (m³)", "")}])
    if not facade or not room.get("Volumen (m³)"):
        st.caption("Guarda las áreas de fachada y el volumen del estar en la Etapa 2 para recuperarlos aquí.")
    tr_bands = [{"Banda (Hz)": row.get("Banda (Hz)"), "TR estar (s)": row["TR estar (s)"]}
                for row in tr.get("tr_bands", []) if row.get("TR estar (s)")]
    if tr_bands:
        st.table(tr_bands)
    else:
        st.caption("El TR por bandas se recupera al guardar los resultados del estar en la Etapa 3.")
    st.write("**Pasaje Chimbote · 30 km/h · Asfalto convencional**")
    st.caption("Flujos medios horarios [veh/h] del escenario docente de tránsito elevado.")
    st.table([{"Período": period, **counts} for period, counts in default_flows.items()])

    dist = audit.get("facade_to_road_m")
    receiver_height = audit.get("receiver_height_m")
    receiver_ref = "Auditoría NoiseMap" if audit else ""
    if computed is not None:
        st.caption(f"Auditoría NoiseMap · fachada–calle: {dist} m · altura del receptor: {receiver_height} m.")
        cols = st.columns(4)
        for col, (key, label) in zip(cols, (("day", "Lday"), ("evening", "Levening"), ("night", "Lnight"))):
            col.metric(label, f"{levels[key]:.1f} dB(A)")
        cols[3].metric("Lden exterior", f"{computed:.1f} dB(A)")
        st.caption(method)

    st.markdown("#### B · Fachada original")
    st.table([item for item in BASE_CONSTRUCTION if item["Caso"] == "FA-01"])
    st.link_button("Abrir SONARA · Fachada ISO 12354-3", SONARA_URL)

    st.markdown("#### C · Diseño libre de la mejora")
    variant = st.text_area("Materiales y composición", old.get("variant", ""))
    mounting = st.text_area("Montaje, marco, sellos y encuentros", old.get("mounting", ""))
    evidence = st.text_area("Respaldo acústico e hipótesis", old.get("evidence", ""))

    st.markdown("#### D · Resultados y proyectos JSON de SONARA")
    files = {}
    results = {}
    for name, label in (("original", "Fachada original F-01/V-01"), ("mejora", "Fachada mejorada")):
        col_file, col_result = st.columns(2)
        previous = (old.get("sonara_json") or {}).get(name)
        upload = col_file.file_uploader(f"JSON SONARA · {label}", type=["json"], key=f"c5l2_s6_{name}")
        data = previous
        if upload is not None:
            data = None
            try:
                raw = upload.getvalue()
                if len(raw) > 2 * 1024 * 1024:
                    raise ValueError
                document = json.loads(raw.decode("utf-8-sig"))
                if not isinstance(document, dict) or len(document) != 1:
                    raise ValueError
                project_id, project = next(iter(document.items()))
                if not isinstance(project, dict) or project.get("id") != project_id:
                    raise ValueError
                requirements = project.get("requerimientos", [])
                if not isinstance(requirements, list) or any(
                    not isinstance(group, dict) or not isinstance(group.get("soluciones", []), list)
                    for group in [project, *requirements]
                ):
                    raise ValueError
                data = {"filename": upload.name, "document": document}
            except (UnicodeError, ValueError):
                col_file.error("Carga un JSON válido de un solo proyecto SONARA, de hasta 2 MB.")
        if data:
            files[name] = data
            col_file.caption(data["filename"])
        available = {}
        if data:
            project = next(iter(data["document"].values()))
            groups = [project, *(project.get("requerimientos") or [])]
            for group in groups:
                if not isinstance(group, dict):
                    continue
                for solution in group.get("soluciones") or []:
                    if not isinstance(solution, dict):
                        continue
                    try:
                        value = float(solution["d2mnt_atr"])
                    except (KeyError, ValueError, TypeError):
                        continue
                    if math.isfinite(value):
                        available[len(available) + 1] = value
        if available:
            results[name] = col_result.selectbox(
                f"DₙT,A,tr [dB] · {label}", list(available.values()),
                key=f"c5l2_facade_result_{name}",
            )
        else:
            results[name] = col_result.number_input(
                f"DₙT,A,tr [dB] · {label}", min_value=-20.0, max_value=150.0,
                value=(old.get("model_results") or {}).get(name),
                key=f"c5l2_facade_manual_{name}",
            )

    st.markdown("#### E · Comprobación de Clase B")
    target = max(30, computed - 24) if computed is not None else None
    st.caption("ISO/TS 19488:2021, Tabla 3 · DₙT,A,tr = D₂m,nT,w + Ctr · mínimo: máx(30 dB, Lden − 24 dB).")
    if target is not None:
        st.metric("Meta Clase B", f"{target:.1f} dB")
    if results["original"] is not None and results["mejora"] is not None:
        st.metric("Mejora de la fachada", f'{results["mejora"] - results["original"]:+.1f} dB')
    if target is not None and results["mejora"] is not None:
        margin = results["mejora"] - target
        st.metric("Margen respecto a Clase B", f"{margin:+.1f} dB")
        st.write("Alcanza la meta según la predicción." if margin >= 0 else "Queda bajo la meta según la predicción.")
    comparison = st.text_area("Conclusión técnica y limitaciones", old.get("comparison", ""))
    payload = {**old, "case": "FA-01", "traffic": {**traffic_old,
        "street": "Pasaje Chimbote", "speed": 30, "surface": "Asfalto convencional",
        "flows": default_flows, "distance": dist, "height": receiver_height,
        "receiver_ref": receiver_ref, "audit": audit, "levels": levels, "method": method,
        "noisemap_document": imported,
        "lden": round(computed, 2) if computed is not None else None},
        "facade_geometry": facade, "receiver_volume": room.get("Volumen (m³)"),
        "receiver_tr": living_tr, "receiver_tr_bands": tr_bands, "variant": variant, "mounting": mounting,
        "evidence": evidence, "comparison": comparison, "target_db": target,
        "model_results": results, "sonara_json": files}
    draft, finish = st.columns(2)
    if draft.button("Guardar avance", key="c5l2_s6_draft"):
        _save(lab, saved, 6, "c5l2_s6", payload, complete=False)
    if finish.button("Completar Etapa 6", type="primary", key="c5l2_s6_finish"):
        if target is None:
            st.warning("Importa un JSON válido de NoiseMap para completar la Etapa 6.")
        elif len(files) != 2 or any(value is None for value in results.values()):
            st.warning("Adjunta ambos proyectos SONARA y registra sus resultados.")
        elif not all(field.strip() for field in (variant, mounting, evidence, comparison)):
            st.warning("Completa la descripción de la mejora, su respaldo y la conclusión.")
        else:
            _save(lab, saved, 6, "c5l2_s6", payload, complete=True)


def _stage7(lab, saved):
    _header(7)
    old = saved.get("c5l2_s7") or {}
    st.markdown("### IN-01 · Ruido de descarga sanitaria")
    st.caption("Descarga del WC de la vivienda del piso 6 → dormitorio CH-A-P05-S03 del piso 5.")

    st.markdown("#### A · Geometría y reverberación")
    geometry = saved.get("c5l2_s2") or {}
    room = next((row for row in geometry.get("rooms", []) if row.get("Caso") == "IN-01"), {})
    closure = next((row for row in geometry.get("separations", []) if row.get("Caso") == "IN-01"), {})
    tr = [{"Banda (Hz)": row["Banda (Hz)"], "TR dormitorio (s)": row["TR dormitorio (s)"]}
          for row in (saved.get("c5l2_s3") or {}).get("tr_bands", []) if row.get("TR dormitorio (s)")]
    st.table([{"Volumen dormitorio (m³)": room.get("Volumen (m³)", "Pendiente"),
               "Área cierre S-01 (m²)": closure.get("Superficie (m²)", "Pendiente")}])
    if tr:
        st.table(tr)
    else:
        st.caption("Guarda el TR por bandas del dormitorio en la Etapa 3.")
    st.caption("El módulo recibe un TR y una absorción equivalente del receptor. Documenta la banda representativa adoptada al trasladar los datos a SONARA.")

    st.markdown("#### B · Instalación original")
    st.table([item for item in BASE_CONSTRUCTION if item["Caso"] == "IN-01"])
    st.link_button("Abrir SONARA · Instalaciones EN 12354-5", SONARA_URL)
    st.markdown(
        "Selecciona **Intermitente (LAFmax estimado)**. Modela la vía aérea a través del cierre S-01 "
        "con el espectro máximo de la descarga y la reducción del cierre por octavas. "
        "Si dispones de datos de excitación y transferencia instalada, agrega la vía estructural "
        "por tubería y abrazaderas en **Agregar vías simultáneas**. Conserva el mismo evento en ambos modelos."
    )
    st.caption("Los espectros genéricos de SONARA son supuestos docentes. Identifica su procedencia, la compatibilidad con el máximo temporal F y cualquier vía omitida.")

    st.markdown("#### C · Diseño libre de la mejora")
    variant = st.text_area("Materiales y solución propuesta", old.get("variant", ""), key="c5l2_s7_variant")
    mounting = st.text_area("Montaje, fijaciones y vías intervenidas", old.get("mounting", ""), key="c5l2_s7_mounting")
    evidence = st.text_area("Respaldo acústico e hipótesis de ambos modelos", old.get("evidence", ""), key="c5l2_s7_evidence")

    st.markdown("#### D · Resultados y proyectos JSON de SONARA")
    st.caption("Guarda el cálculo de cada condición como solución en su proyecto SONARA antes de exportarlo.")
    files, results = {}, {}
    for name, label in (("original", "Instalación original"), ("mejora", "Instalación mejorada")):
        upload = st.file_uploader(f"JSON SONARA · {label}", type=["json"], key=f"c5l2_s7_json_{name}")
        data = (old.get("sonara_json") or {}).get(name)
        if upload is not None:
            data = None
            try:
                raw = upload.getvalue()
                if len(raw) > 2 * 1024 * 1024:
                    raise ValueError
                document = json.loads(raw.decode("utf-8-sig"))
                if not isinstance(document, dict) or len(document) != 1:
                    raise ValueError
                project_id, project = next(iter(document.items()))
                if not isinstance(project, dict) or project.get("id") != project_id:
                    raise ValueError
                requirements = project.get("requerimientos", [])
                if not isinstance(requirements, list) or any(
                    not isinstance(group, dict) or not isinstance(group.get("soluciones", []), list)
                    for group in [project, *requirements]
                ):
                    raise ValueError
                data = {"filename": upload.name, "document": document}
            except (ValueError, UnicodeError):
                st.error("Carga un JSON de un solo proyecto SONARA, de hasta 2 MB.")
        options = []
        if data:
            files[name] = data
            st.caption(data["filename"])
            project = next(iter(data["document"].values()))
            for group in [project, *(project.get("requerimientos") or [])]:
                if not isinstance(group, dict):
                    continue
                for solution in group.get("soluciones") or []:
                    if not isinstance(solution, dict):
                        continue
                    value = solution.get("lafmax_nt")
                    if type(value) in (float, int) and math.isfinite(value):
                        options.append(float(value))
        if options:
            results[name] = st.selectbox(f"LAFmax,nT [dB(A)] · {label}", list(dict.fromkeys(options)),
                                         key=f"c5l2_s7_result_{name}")
        else:
            results[name] = st.number_input(f"LAFmax,nT [dB(A)] · {label}", min_value=-20.0, max_value=150.0,
                                            value=(old.get("model_results") or {}).get(name),
                                            key=f"c5l2_s7_manual_{name}")

    st.markdown("#### E · Comprobación de Clase B")
    target = 30.0
    st.caption("ISO/TS 19488:2021, Tabla 4 · equipos intermitentes de espacios vecinos · LAFmax,nT ≤ 30 dB(A).")
    if results["original"] is not None and results["mejora"] is not None:
        st.metric("Reducción proyectada", f'{results["original"] - results["mejora"]:+.1f} dB')
    if results["mejora"] is not None:
        margin = target - results["mejora"]
        st.metric("Margen respecto a Clase B", f"{margin:+.1f} dB")
        st.write("Alcanza la meta según la predicción." if margin >= 0 else "Supera el límite según la predicción.")
    else:
        st.info("Registra el LAFmax,nT de la instalación mejorada para comprobar la meta.")
    comparison = st.text_area("Conclusión técnica y limitaciones", old.get("comparison", ""), key="c5l2_s7_comparison")
    payload = {**old, "case": "IN-01", "receiver": room, "closure": closure,
               "receiver_tr_bands": tr, "variant": variant, "mounting": mounting,
               "evidence": evidence, "comparison": comparison, "target_db": target,
               "model_results": results, "sonara_json": files}
    draft, finish = st.columns(2)
    if draft.button("Guardar avance", key="c5l2_s7_draft"):
        _save(lab, saved, 7, "c5l2_s7", payload, complete=False)
    if finish.button("Completar Etapa 7", type="primary", key="c5l2_s7_finish"):
        if len(files) != 2 or any(value is None for value in results.values()):
            st.warning("Adjunta ambos proyectos SONARA y registra sus resultados LAFmax,nT.")
        elif not all(field.strip() for field in (variant, mounting, evidence, comparison)):
            st.warning("Completa la mejora, el montaje, el respaldo y la conclusión.")
        else:
            _save(lab, saved, 7, "c5l2_s7", payload, complete=True)


def _class_b_matrix(saved):
    def number(value):
        if isinstance(value, bool):
            return None
        try:
            parsed = float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            return None
        return parsed if math.isfinite(parsed) else None

    facade = saved.get("c5l2_s6") or {}
    lden = number((facade.get("traffic") or {}).get("lden"))
    criteria = (
        (4, "AI-01", "DₙT,50", "DₙT,50 proyectado (dB)", 54, "≥"),
        (5, "IM-01", "L′ₙT,w", "L′ₙT,w (dB)", 50, "≤"),
        (5, "IM-01", "L′ₙT,50", "L′ₙT,50 (dB)", 54, "≤"),
        (6, "FA-01", "DₙT,A,tr", None, max(30, lden - 24) if lden is not None else None, "≥"),
        (7, "IN-01", "LAFmax,nT", None, 30, "≤"),
    )
    matrix = []
    for stage, case, descriptor, column, limit, direction in criteria:
        results = (saved.get(f"c5l2_s{stage}") or {}).get("model_results")
        original = improved = None
        if column and isinstance(results, list):
            values = [number(row.get(column)) if isinstance(row, dict) else None
                      for row in results[:2]]
            original, improved = (values + [None, None])[:2]
        elif column is None and isinstance(results, dict):
            original, improved = number(results.get("original")), number(results.get("mejora"))
        margin = None
        if improved is not None and limit is not None:
            margin = improved - limit if direction == "≥" else limit - improved
        matrix.append({
            "stage": stage, "case": case, "descriptor": descriptor, "original": original,
            "improved": improved, "limit": limit, "direction": direction, "margin": margin,
        })
    return matrix, lden


def _stage8(lab, saved):
    _header(8)
    st.markdown("### Matriz de verificación · Clase B")
    st.caption("Resultados guardados en las etapas 4 a 7 · ISO/TS 19488:2021, tablas 1 a 4.")
    matrix, lden = _class_b_matrix(saved)
    if lden is not None:
        st.caption(f"Fachada · Lden = {lden:g} dB(A) · meta DₙT,A,tr = máx(30 dB, Lden − 24 dB).")

    def display(value, unit):
        return f"{value:g} {unit}" if value is not None else "Pendiente"

    rows = []
    for result in matrix:
        unit = "dB(A)" if result["stage"] == 7 else "dB"
        margin = result["margin"]
        rows.append({
            "Etapa": result["stage"], "Caso": result["case"], "Descriptor": result["descriptor"],
            "Original": display(result["original"], unit),
            "Mejorado": display(result["improved"], unit),
            "Meta Clase B": f'{result["direction"]} {display(result["limit"], unit)}'
                            if result["limit"] is not None else "Pendiente de Lden",
            "Margen": f"{margin:+.2f} dB" if margin is not None else "Pendiente",
            "Verificación de la mejora": "Pendiente" if margin is None else
                "Alcanza la meta" if margin >= 0 else "No alcanza la meta",
        })
    st.table(rows)
    st.caption("Impacto requiere cumplir ambos límites. Un margen positivo indica holgura respecto del requisito.")

    pending = sorted({row["stage"] for row in matrix if row["original"] is None or row["margin"] is None})
    if pending:
        st.info("Faltan resultados guardados de las etapas " + ", ".join(map(str, pending)) + ".")
    elif all(row["margin"] >= 0 for row in matrix):
        st.success("Los cuatro casos alcanzan la meta de Clase B según las predicciones guardadas.")
    else:
        failing = list(dict.fromkeys(row["case"] for row in matrix if row["margin"] < 0))
        st.warning("Casos que no alcanzan la meta de Clase B según la predicción · " + ", ".join(failing))

    old = saved.get("c5l2_s8") or {}
    conclusion = st.text_area("Conclusión técnica y verificaciones posteriores",
                              old.get("conclusion", ""), height=130)
    payload = {"matrix": matrix, "lden": lden, "conclusion": conclusion}
    draft, finish = st.columns(2)
    if draft.button("Guardar avance", key="c5l2_s8_draft"):
        _save(lab, saved, 8, "c5l2_s8", payload, complete=False)
    if finish.button("Completar Etapa 8", type="primary", key="c5l2_s8_finish"):
        if pending:
            st.warning("Guarda los resultados pendientes en sus etapas de origen.")
        elif not conclusion.strip():
            st.warning("Redacta tu conclusión técnica.")
        else:
            _save(lab, saved, 8, "c5l2_s8", payload, complete=True)


def _grade(score,total=100):
    pct=100*float(score)/float(total)
    return round(1+3*pct/60,1) if pct<60 else round(4+3*(pct-60)/40,1)

def _get_submission(stage,question_key):
    if _readonly() or _is_teacher():return None
    client=_supabase()
    if client is None or not st.session_state.get("user_key"):
        st.error("No se pudo consultar el estado de la entrega. Actualiza antes de continuar.")
        st.stop()
    try:
        r=(client.table("responses").select("answer,auto_score,teacher_score,status")
           .eq("class_id",CLASS_ID).eq("user_key",st.session_state["user_key"])
           .eq("stage",stage).eq("question_key",question_key).limit(1).execute())
        return (r.data or [None])[0]
    except Exception:
        st.error("No se pudo consultar el estado de la entrega. Actualiza antes de continuar.")
        st.stop()

def _submit(stage,question_key,title,payload,score,max_score):
    if _readonly() or _is_teacher():
        raise PermissionError("La vista docente y Zoom no pueden efectuar entregas oficiales.")
    client=_supabase()
    user_key=st.session_state.get("user_key")
    if client is None or not user_key:
        raise RuntimeError("No existe una conexión válida para guardar la evaluación.")
    now=_now()
    client.table("questions").upsert({
        "id":f"{CLASS_ID}-{question_key}-v1","class_id":CLASS_ID,"stage":stage,
        "question_key":question_key,"question_text":title,"correct_answer":"Pauta docente de revisión",
        "max_score":max_score,"content_version":1,"active":True,"updated_at":now
    },on_conflict="id",returning="minimal").execute()
    client.table("responses").upsert({
        "course_id":"diplomado-acustica-edificacion","class_id":CLASS_ID,"user_key":user_key,
        "stage":stage,"question_key":question_key,"question_text":title,
        "correct_answer":"Pauta docente de revisión","answer":payload,"auto_score":score,
        "max_score":max_score,"status":"submitted","updated_at":now,"submitted_at":now,
        "feedback":"Entrega recibida; desarrollo sujeto a revisión docente.",
    },on_conflict="class_id,user_key,question_key",returning="minimal").execute()

def _stage9(lab,saved):
    _header(9)
    st.markdown("### Evaluación oficial · 10 preguntas × 3 puntos = 30 puntos")
    if _is_teacher():
        st.caption("Las respuestas y su fundamento están en la pauta docente de esta etapa.")
        return
    remote=_get_submission(9,"c5l2_quiz_v1")
    if remote or saved.get("c5l2_s9_submitted"):
        row=remote or {}
        score=row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score", saved.get("c5l2_s9_score",0))
        st.success("Cuestionario enviado. No se permiten más intentos.")
        st.metric("Puntaje",f"{float(score or 0):g}/30")
        st.metric("Nota cuestionario",f"{_grade(float(score or 0),30):.1f}")
        return
    old = saved.get("c5l2_s9_draft_v3") or {}
    answers = {}
    for i, (question, options, _, _) in enumerate(QUIZ):
        choices = ["Sin responder", *options]
        previous = old.get(str(i))
        answers[str(i)] = st.radio(
            f"{i + 1}. {question}", choices,
            index=choices.index(previous) if previous in choices else 0,
            key=f"c5l2_quiz_v3_{i}",
        )
    a, b = st.columns(2)
    if a.button("Guardar borrador", key="c5l2_quiz_draft"):
        _save(lab, saved, 9, "c5l2_s9_draft_v3", answers, complete=False)
    if b.button("Enviar cuestionario definitivo", type="primary", key="c5l2_quiz_submit", disabled=_readonly()):
        if "Sin responder" in answers.values():
            st.warning("Responde todas las preguntas.")
            return
        score = sum(3 for i, (_, options, expected, _) in enumerate(QUIZ)
                    if answers[str(i)] == options[expected])
        payload = {"version": 3, "answers": answers, "max_score": 30, "score": score, "target_class": "B"}
        try:
            _submit(9,"c5l2_quiz_v1","Curso 5 · Laboratorio 2 · Cuestionario",payload,score,30)
            _save(lab,saved,9,"c5l2_s9_submission",payload)
            saved["c5l2_s9_submitted"]=True
            saved["c5l2_s9_score"]=score
            _save_future_state(lab["id"],saved)
        except Exception:
            st.error("No se pudo confirmar el envío. Verifica tu conexión antes de repetir.")
        else:
            st.success(f"Envío confirmado · {score}/30 puntos · nota {_grade(score,30):.1f}")

def _stage10(lab, saved):
    _header(10)
    st.markdown("### Expediente integrador · 70 puntos")
    st.write("Integra tus predicciones de aislamiento y ruido de instalaciones. Justifica la decisión de Clase B para cada caso y explica cómo comprobarías el desempeño en obra.")

    matrix, lden = _class_b_matrix(saved)
    stage8 = saved.get("c5l2_s8") or {}
    pending = [stage for stage in range(1, 8) if not saved.get(f"done_{stage}")
               or not saved.get(f"c5l2_s{stage}")]
    if (not saved.get("done_8") or stage8.get("matrix") != matrix
            or stage8.get("lden") != lden):
        pending.append(8)

    st.markdown("#### Resultados del expediente")
    st.table([{
        "Caso": row["case"], "Descriptor": row["descriptor"],
        "Original": row["original"] if row["original"] is not None else "Pendiente",
        "Mejorado": row["improved"] if row["improved"] is not None else "Pendiente",
        "Meta Clase B": f'{row["direction"]} {row["limit"]:g}' if row["limit"] is not None else "Pendiente",
        "Margen (dB)": f'{row["margin"]:+.2f}' if row["margin"] is not None else "Pendiente",
        "Verificación": "Pendiente" if row["margin"] is None else
                        "Alcanza la meta" if row["margin"] >= 0 else "Fuera de meta",
    } for row in matrix])
    st.caption("Instalaciones se expresa en dB(A). Para impacto deben cumplirse ambos límites.")
    if lden is not None:
        st.caption(f"Lden de fachada recuperado de NoiseMap · {lden:g} dB(A).")

    with st.expander("Rúbrica · 70 puntos"):
        details = (
            "Identifica versiones, modelos, planos y respaldo de los resultados.",
            "Verifica recintos, cotas, áreas, volumen y origen de la geometría.",
            "Distingue propiedades documentadas de hipótesis y justifica los datos de entrada.",
            "Explica el cambio del separador y los flancos. Interpreta DₙT,50.",
            "Justifica el desacople y verifica ambos indicadores de impacto.",
            "Vincula el Lden incidente con la meta y evalúa el conjunto de fachada.",
            "Justifica el descriptor del evento y las vías de transmisión consideradas.",
            "Sintetiza las decisiones, sus limitaciones y las comprobaciones en obra.",
        )
        st.table([{"Criterio": title, "Puntos": points, "Evidencia esperada": detail}
                  for (title, points), detail in zip(RUBRIC, details)])

    if _is_teacher():
        st.info("Evalúa el expediente oficial en Evaluaciones entregadas. La matriz muestra el avance disponible en esta vista.")
        return
    remote = _get_submission(10, "c5l2_report_v1")
    old = saved.get("c5l2_s10") or {}
    if remote or saved.get("c5l2_s10_submitted"):
        st.success("Informe enviado para evaluación docente. La entrega oficial está bloqueada.")
        submitted_answer = (remote or {}).get("answer")
        submitted_answer = submitted_answer if isinstance(submitted_answer, dict) else old
        with st.expander("Ver texto entregado"):
            st.write(submitted_answer.get("report", ""))
            st.write(submitted_answer.get("evidence", ""))
        return

    if pending:
        st.info("Completa o actualiza las etapas " + ", ".join(map(str, pending)) + " antes del envío. Puedes guardar el borrador.")
    st.caption("Si modificas resultados de las etapas 4 a 7, vuelve a completar la matriz de la Etapa 8.")
    with st.form("c5l2_final_report"):
        report = st.text_area("Conclusión técnica y verificaciones en obra", old.get("report", ""), height=230,
                              help="Explica qué casos alcanzan la meta, qué limita a cada solución y qué verificarías en obra.")
        evidence = st.text_area("Evidencias y supuestos determinantes", old.get("evidence", ""), height=150,
                                help="Identifica las referencias y los supuestos que sustentan tus conclusiones. Los archivos guardados se incluyen en el expediente.")
        draft = st.form_submit_button("Guardar avance")
        submitted = st.form_submit_button("Enviar expediente definitivo · 70 puntos", type="primary",
                                          disabled=_readonly())
    text = {"report": report, "evidence": evidence}
    if draft:
        _save(lab, saved, 10, "c5l2_s10", text, complete=False)
    if submitted:
        if pending:
            st.warning("Completa las etapas pendientes antes del envío.")
        elif not report.strip() or not evidence.strip():
            st.warning("Completa la conclusión técnica y las evidencias.")
        else:
            payload = {"version": 1, "target_class": "B", "standard": STANDARD, **text,
                       "stages": {str(i): saved[f"c5l2_s{i}"] for i in range(1, 9)},
                       "rubric": RUBRIC, "practical_max": 70, "quiz_score": saved.get("c5l2_s9_score")}
            try:
                _submit(10, "c5l2_report_v1", "Curso 5 · Laboratorio 2 · Informe integrador", payload, 0, 70)
            except Exception:
                st.error("No se pudo confirmar la entrega. Conserva tu borrador y vuelve a intentarlo.")
            else:
                saved["c5l2_s10_submitted"] = True
                _save(lab, saved, 10, "c5l2_s10", text)
                st.success("Expediente enviado a evaluación docente.")


def _stage1_teacher_criteria_guide():
    """Solución docente campo por campo: ISO/TS 19488:2021, Clase B.

    Los umbrales son normativos; los casos y las fuentes docentes son
    modelos académicos, no una medición/certificación del edificio.
    """
    st.markdown("### Solución docente · requisitos Clase B de ISO/TS 19488:2021")
    st.success(
        "Esta pauta indica **qué debe escribir el alumno en cada campo**, "
        "incluidos los valores numéricos y las referencias normativas. "
        "No se copian las respuestas a la vista alumno."
    )
    st.info(
        "**IN-01 actualizado:** la fuente es la descarga del WC del baño "
        "de la **vivienda superior (piso 6)**, distinta de CH-A-P05-S03. "
        "Corresponde revisar el criterio Clase B para ruido intermitente "
        "procedente de espacios vecinos: **LAF,max,nT ≤ 30 dB(A)**. "
        "El trazado de la bajada sanitaria es un **supuesto docente**, "
        "no una característica acreditada por los planos."
    )
    answers = [
        {
            "code":"AI-01", "title":"Aislamiento aéreo entre viviendas",
            "pair":"Estar vivienda contigua al poniente (P5) → dormitorio CH-A-P05-S03 (P5).",
            "descriptor":"DₙT,50 = DₙT,w + C₅₀–₃₁₅₀ [dB].",
            "limit":"54 dB. Escribir: DₙT,50 ≥ 54 dB.",
            "direction":"Mayor o igual (≥).",
            "reference":"ISO/TS 19488:2021, apartado 5.2, Tabla 1, fila 1, columna Clase B; definición 3.2.4 y nota a de la tabla.",
            "condition":"Entre un recinto habitable de una vivienda y un recinto situado fuera de esa vivienda; aquí, estar de la vecina poniente y dormitorio receptor. Evaluar el aislamiento entre recintos con su reverberación normalizada y flancos. No sustituir por Rw del muro.",
            "check":"Se deben cumplir ≥54 dB para el descriptor extendido a bajas frecuencias. La norma contempla equivalencias condicionadas en su nota; no convertirlas sin citarla.",
        },
        {
            "code":"IM-01", "title":"Ruido de impacto de la vivienda superior",
            "pair":"Dormitorio de piso 6 → dormitorio CH-A-P05-S03, piso 5.",
            "descriptor":"Dos descriptores simultáneos: L′ₙT,w [dB] y L′ₙT,50 = L′ₙT,w + Cᵢ,₅₀–₂₅₀₀ [dB].",
            "limit":"L′ₙT,w ≤ 50 dB Y L′ₙT,50 ≤ 54 dB. **Ambos deben cumplirse**.",
            "direction":"Menor o igual (≤) para ambos.",
            "reference":"ISO/TS 19488:2021, apartado 5.3, Tabla 2, fila 1 (recintos habitables entre viviendas), columna Clase B y nota 1; definiciones 3.2.5–3.2.6.",
            "condition":"Impacto desde vivienda superior sobre entrepiso compartido con dormitorio receptor. Se debe considerar el nivel normalizado en el receptor, la transmisión lateral y la extensión a bajas frecuencias. No usar ΔL de producto como nivel final.",
            "check":"Una respuesta que incluya solo ≤54 dB o solo ≤50 dB está incompleta: Clase B exige los dos descriptores.",
        },
        {
            "code":"FA-01", "title":"Aislamiento acústico de fachada",
            "pair":"Tránsito hipotético de Pasaje Chimbote → estar CH-A-P05-S03, fachada sur.",
            "descriptor":"DₙT,A,tr = D₂m,nT,w + Ctr [dB] para la envolvente completa, conforme a las definiciones de la norma.",
            "limit":"DₙT,A,tr ≥ máx(30 dB; Lden − 24 dB). Por ejemplo, si Lden modelado = 60 dB: mínimo 36 dB. **60 dB es solo ejemplo, no exposición medida ni resultado predeterminado**.",
            "direction":"Mayor o igual (≥).",
            "reference":"ISO/TS 19488:2021, apartado 5.4, Tabla 3, columna Clase B (Lden − 24), notas 1 y 2 (mínimo 30 dB para clases A–D); definición de DₙT,A,tr en 3.2.7.",
            "condition":"Se aplica a fachada/techo de un recinto habitable expuesto a ruido exterior caracterizado por Lden. Usar el Lden del modelo de tránsito hipotético, identificar el carácter no normativo de la propagación NoiseMap y evaluar el conjunto muro-ventana-marco-sellos del estar, no solo el vidrio.",
            "check":"El requisito depende del Lden calculado y tiene piso de 30 dB; no afirmar un único número fijo para cualquier exposición.",
        },
        {
            "code":"IN-01", "title":"Ruido de instalación sanitaria de vivienda vecina",
            "pair":"Descarga WC del baño de la vivienda superpuesta (piso 6) → dormitorio de CH-A-P05-S03 (piso 5).",
            "descriptor":"LAF,max,nT [dB(A)] para el evento de descarga intermitente procedente de una vivienda vecina; nivel máximo con ponderación temporal F, normalizado a la reverberación del recinto receptor.",
            "limit":"LAF,max,nT ≤ 30 dB(A) para ruido de equipamiento intermitente/irregular procedente de un espacio vecino. El valor es el máximo Clase B para este supuesto de fuente y receptor.",
            "direction":"Menor o igual (≤).",
            "reference":"ISO/TS 19488:2021, apartado 5.5, Tabla 4, fila de equipos intermitentes o irregulares de espacios vecinos, columna Clase B; revisar notas y condiciones de aplicación.",
            "condition":"WC del piso 6 de otra vivienda, descarga de 6 L como condición docente, receptor dormitorio de CH-A-P05-S03 en piso 5. Documentar el evento y las vías de transmisión posibles aérea y estructural. La posición y trazado real de la bajada NO están acreditados por los planos; el modelo se declara hipótesis docente.",
            "check":"No utilizar Lw de fuente o LAeq del evento como sustituto de LAF,max,nT en dormitorio. Aunque se trate de una fuente de vivienda distinta, una predicción simplificada no constituye certificación in situ.",
        },
    ]
    for item in answers:
        with st.expander(
            item["code"]+" · "+item["title"]+" · respuesta docente completa",
            expanded=False,
        ):
            st.caption("Caso asignado: "+item["pair"])
            for n,label,field in [
                (1,"Descriptor(s) normativo(s) y unidades","descriptor"),
                (2,"Requisito Clase B (valor y unidad)","limit"),
                (3,"Sentido del criterio","direction"),
                (4,"Tabla, fila, nota y apartado ISO","reference"),
                (5,"Ámbito de aplicación, condiciones y justificación","condition"),
            ]:
                st.markdown(f"**{n} · {label}**")
                st.info(item[field])
            st.caption("Criterio de corrección: "+item["check"])
    st.markdown("#### Criterio de corrección general")
    st.markdown(
        "**AI-01:** DₙT,50 ≥ 54 dB.  \n"
        "**IM-01:** L′ₙT,w ≤ 50 dB **y** L′ₙT,50 ≤ 54 dB.  \n"
        "**FA-01:** DₙT,A,tr ≥ máx(30; Lden−24) dB.  \n"
        "**IN-01:** LAF,max,nT ≤ 30 dB(A) para WC intermitente de la **vivienda superior**, "
        "con trazado sanitario hipotético documentado."
    )
    st.caption(
        "Referencias: ISO/TS 19488:2021, apartados 5.2–5.5, "
        "Tablas 1–4 y sus notas. Los resultados de SONARA y NoiseMap "
        "constituyen predicción docente, no certificación in situ."
    )


def _stage2_teacher_geometry_results():
    """Teacher-only solved geometry for a reproducible SONARA teaching model.

    These numbers come from explicitly adopted teaching dimensions, NOT from
    a certified as-built survey. Keep aligned with student supplement §3.
    """
    st.markdown("### Solución docente · Etapa 2 · geometría base para SONARA")
    st.info(
        "Los resultados siguientes están **calculados y cerrados para el modelo "
        "académico** con las hipótesis de la sección 3 del «Suplemento de cotas». "
        "Son datos reproducibles para SONARA, **no cotas certificadas del edificio**. "
        "Fuente documental: planta tipo Torre A (Parte 1, pág. 8), elevación sur "
        "(Parte 2, pág. 5) y suplemento HD-01, HE-01, HG-01, HM-01, HL-01, "
        "HF-02, HV-02, HI-01 y HP-01."
    )
    st.markdown("#### A · Casos y elementos fijados")
    st.table([
        {"Caso":"AI-01","Emisor":"Estar vecino poniente · P5",
         "Receptor":"Dormitorio de estudio · P5","Elemento":"M-01"},
        {"Caso":"IM-01","Emisor":"Dormitorio superior · P6",
         "Receptor":"Dormitorio de estudio · P5","Elemento":"L-01"},
        {"Caso":"FA-01","Emisor":"Pasaje Chimbote",
         "Receptor":"Estar de estudio · P5","Elemento":"F-01 / V-01"},
        {"Caso":"IN-01","Emisor":"WC de vivienda superior · P6",
         "Receptor":"Dormitorio de estudio · P5","Elemento":"S-01 / IS-01"},
    ])

    st.markdown("#### B · Respuestas de la geometría de recintos")
    st.caption("La columna «Lámina / cota» reproduce el campo que completa el alumno. Señala la ubicación en el expediente y distingue claramente la dimensión docente.")
    st.table([
        {"Caso":"AI-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³",
         "Lámina / cota":"Planta tipo, Parte 1, pág. 8: cotas parciales del dormitorio; suplemento §3: HD-01 (2,60 × 3,10) y HG-01 (2,50), SUPUESTOS DOCENTES."},
        {"Caso":"IM-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³",
         "Lámina / cota":"Planta tipo, Parte 1, pág. 8 (pisos 5–6); suplemento §3: HD-01 y HG-01, SUPUESTOS DOCENTES."},
        {"Caso":"FA-01","Recinto":"Estar P5","Largo":"3,75 m",
         "Ancho":"2,43 m","Altura":"2,50 m","Área piso":"9,11 m²",
         "Volumen":"22,78 m³",
         "Lámina / cota":"Planta tipo, Parte 1, pág. 8: referencias parciales del sector estar; suplemento §3: HE-01 (recinto equivalente 2,43 × 3,75) y HG-01, SUPUESTOS DOCENTES."},
        {"Caso":"IN-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³",
         "Lámina / cota":"Planta tipo, Parte 1, pág. 8: dormitorio receptor; suplemento §3: HD-01 y HG-01, SUPUESTOS DOCENTES. Fuente WC superior: escenario docente."},
    ])
    st.markdown(
        "**Cálculos:** dormitorio 2,60 × 3,10 = **8,06 m²**; "
        "volumen = 8,06 × 2,50 = **20,15 m³**. "
        "Estar equivalente: 2,43 × 3,75 = **9,1125 m²** "
        "(se ingresa **9,11 m²**); volumen = 9,1125 × 2,50 "
        "= **22,78125 m³** (se ingresa **22,78 m³**)."
    )
    st.markdown("#### C · Superficies a ingresar en la tabla de separación")
    st.table([
        {"Caso":"AI-01","Elemento":"M-01 · muro medianero",
         "Largo":"3,10 m","Ancho / alto":"2,50 m (alto)",
         "Superficie":"7,75 m²",
         "Lámina / cota":"Planta tipo Parte 1, pág. 8 (relación entre viviendas). Suplemento §3: HM-01 × HG-01; longitud y altura DOCENTES."},
        {"Caso":"IM-01","Elemento":"L-01 · losa superior del receptor",
         "Largo":"3,10 m","Ancho / alto":"2,60 m (ancho)",
         "Superficie":"8,06 m²",
         "Lámina / cota":"Planta tipo Parte 1, pág. 8 (pisos 5–6). Suplemento §3: HL-01, huella de losa equivalente; SUPUESTO DOCENTE."},
        {"Caso":"FA-01","Elemento":"F-01 · fachada sur del estar",
         "Largo":"2,43 m","Ancho / alto":"2,50 m (alto)",
         "Superficie":"6,075 m²",
         "Lámina / cota":"Planta tipo Parte 1, pág. 8 + elevación sur Parte 2, pág. 5 (referencia de ubicación). Suplemento §3: HF-02 × HG-01; DIMENSIONES DOCENTES."},
        {"Caso":"IN-01","Elemento":"S-01 · cierre sanitario",
         "Largo":"1,40 m","Ancho / alto":"2,50 m (alto)",
         "Superficie":"3,50 m²",
         "Lámina / cota":"Suplemento §3: HI-01 × HG-01, cierre hipotético; NO hay trazado de bajada acreditado por planos."},
    ])
    st.caption(
        "En **IM-01**, la superficie evaluada es la cara inferior de la losa "
        "del piso 6, que constituye el cielo del dormitorio receptor del piso 5. "
         "En la tabla C: **Largo = 3,10 m y Ancho = 2,60 m (en planta)**; "
        "S = **8,06 m²**. La segunda dimensión NO representa altura ni espesor "
        "de losa. Para muros, fachada y cierre sanitario, la columna «Ancho / alto» representa su altura."
    )

    st.markdown("#### D · Fachada sur del estar (FA-01)")
    st.caption("El alumno registra una sola referencia en la fila del formulario; aquí se desglosa el origen de cada valor para facilitar su corrección.")
    st.table([
        {"Campo":"Recinto receptor","Respuesta":"Estar CH-A-P05-S03, piso 5",
         "Lámina / cota":"Planta tipo Torre A, Parte 1, pág. 8 (identificación del recinto)."},
        {"Campo":"Orientación","Respuesta":"Sur → Pasaje Chimbote",
         "Lámina / cota":"Planta tipo, Parte 1, pág. 8 y elevación sur, Parte 2, pág. 5."},
        {"Campo":"Ancho equivalente de fachada","Respuesta":"2,43 m",
         "Lámina / cota":"Suplemento de cotas §3, HF-02: SUPUESTO DOCENTE; no es ancho verificado del alzado."},
        {"Campo":"Altura interior del recinto","Respuesta":"2,50 m",
         "Lámina / cota":"Suplemento de cotas §3, HG-01: SUPUESTO DOCENTE."},
        {"Campo":"Paño bruto de fachada","Respuesta":"2,43 × 2,50 = 6,075 m²",
         "Lámina / cota":"CALCULADO: HF-02 × HG-01, suplemento §3."},
        {"Campo":"Ventana única","Respuesta":"1,80 × 1,20 = 2,160 m²",
         "Lámina / cota":"Suplemento de cotas §3, HV-02: SUPUESTO DOCENTE; ubicación referencial: elevación sur Parte 2, pág. 5."},
        {"Campo":"Paño opaco","Respuesta":"6,075 − 2,160 = 3,915 m²",
         "Lámina / cota":"CALCULADO: paño bruto − ventana; HF-02, HG-01, HV-02."},
    ])
    st.info(
        "**Texto para «Lámina / cota» de la fachada:** «Planta tipo Torre A "
        "(Parte 1, pág. 8) y elevación sur (Parte 2, pág. 5): ubicación. "
        "Suplemento de cotas §3: HF-02 (2,43 m), HG-01 (2,50 m), "
        "HV-02 (1,80 × 1,20 m), todos SUPUESTOS DOCENTES; áreas CALCULADAS»."
    )
    st.success(
        "**Números para introducir en la ficha:** fachada total **6,075 m²** "
        "(≈6,08), ventanas **2,160 m²** (2,16), paño opaco "
        "**3,915 m²** (≈3,92). Mantener cifras sin redondear durante el cálculo."
    )

    st.markdown("#### E · Superficies internas para TR por bandas en SONARA")
    st.table([
        {"Recinto":"Dormitorio","Piso":"8,06 m²","Cielo":"8,06 m²",
         "Muros brutos":"28,50 m²","Ventana":"No definida; 0 m² en modelo interior",
         "Puerta":"1,68 m² HP-01","Muros opacos":"26,82 m²"},
        {"Recinto":"Estar equivalente","Piso":"9,1125 m²","Cielo":"9,1125 m²",
         "Muros brutos":"30,90 m²","Ventana":"2,160 m² HV-02",
         "Puerta":"1,68 m² HP-01","Muros opacos":"27,06 m²"},
    ])
    st.markdown(
        "Perímetros: dormitorio 2(2,60 + 3,10) = **11,40 m**; "
        "estar 2(2,43 + 3,75) = **12,36 m**. "
        "Área bruta de muros = perímetro × 2,50 m. "
        "Se adopta **una puerta docente por recinto de 0,80 × 2,10 = 1,68 m²** "
        "y, en el dormitorio, **ninguna ventana contabilizada en este "
        "submodelo de TR** porque no se ha definido un vano de dormitorio. "
        "El estudiante puede justificar una variante más detallada si la "
        "documentación la permite. A partir de estas superficies se calculan "
        "las absorciones por bandas y el TR en SONARA; **no existe TR prefijado**."
    )
    st.warning(
        "La geometría base deja cerrado el **cálculo académico** sin alterar "
        "la arquitectura documentada: fachada, vanos, delimitación del estar "
        "y trazado sanitario siguen siendo supuestos del laboratorio. "
        "No utilizar estos resultados para certificar el edificio construido."
    )


def _teacher(stage, saved=None):
    if _is_teacher():
        with st.expander(f"Pauta docente · Etapa {stage}",expanded=False):
            if stage==1:
                st.write(TEACHER[stage])
                _stage1_teacher_criteria_guide()
            elif stage==2:
                # Display the answers directly: no links, previous-project
                # warnings or preliminary teacher text.
                _stage2_teacher_geometry_results()
            else:
                st.write(TEACHER[stage])
            if stage == 9:
                for n, (question, options, answer, reason) in enumerate(QUIZ, 1):
                    st.markdown(f"**{n}. {question}**")
                    st.write(f"**Respuesta correcta:** {options[answer]}")
                    st.caption(reason)
            if stage in (6, 7):
                label_prefix = "Fachada" if stage == 6 else "Instalación"
                records = ((saved or {}).get(f"c5l2_s{stage}") or {}).get("sonara_json") or {}
                for name, label in (("original", f"{label_prefix} original"), ("mejora", f"{label_prefix} mejorada")):
                    data = records.get(name)
                    if data and data.get("document"):
                        st.download_button(
                            "Descargar JSON · " + label,
                            json.dumps(data["document"], ensure_ascii=False, indent=2),
                            file_name=data["filename"], mime="application/json",
                            key=f"c5l2_s{stage}_teacher_" + name,
                        )
            if stage==5:
                st.markdown("**Pauta docente · aislamiento de impacto · Etapa 5**")
                st.write(
                    "Comprobar losa L-01 **superior** del dormitorio receptor "
                    "en piso 5, bajo la vivienda del piso 6. Base académica: "
                    "HA 160 mm + mortero 30 mm + cerámica 10 mm, sin capa "
                    "resiliente. Conservar geometría IM-01 y TR recuperados, "
                    "revisar flancos y montaje de la variante."
                )
                st.info(
                    "Clase B ISO/TS 19488:2021 Tabla 2: **L′ₙT,w ≤ 50 dB** "
                    "**Y L′ₙT,50 ≤ 54 dB**. La norma pide ambos indicadores, "
                    "no una alternativa. No inventar valores docentes calculados "
                    "si no existe un proyecto SONARA guardado."
                )
                records = ((saved or {}).get("c5l2_s5") or {}).get("sonara_json") or {}
                for name, label in (("original", "Original L-01"),
                                    ("mejora", "Mejora de impacto")):
                    doc = records.get(name)
                    if isinstance(doc, dict) and doc.get("document"):
                        st.markdown(f"**{label} · {doc.get('filename', 'SONARA.json')}**")
                        st.json(doc["document"], expanded=False)
                        st.download_button(
                            "⬇ Descargar JSON · " + label,
                            data=json.dumps(doc["document"], ensure_ascii=False, indent=2),
                            file_name=doc.get("filename", f"sonara_impacto_{name}.json"),
                            mime="application/json",
                            key="c5l2_s5_teacher_json_" + name,
                        )
                    else:
                        st.caption(f"{label}: JSON no entregado.")
            if stage==4:
                st.markdown("**Pauta docente · proyectos SONARA adjuntos**")
                st.caption(
                    "Consulta la condición original y la mejora guardadas por "
                    "el alumno en la Etapa 4. La ficha conserva el proyecto "
                    "JSON completo para revisar geometría, materiales, flancos "
                    "y los resultados de las soluciones."
                )
                saved_stage4 = (saved or {}).get("c5l2_s4") or {}
                refs = saved_stage4.get("sonara_json") or {}
                for mode, label in (("original", "Modelo original"),
                                    ("mejora", "Modelo mejorado")):
                    attachment = refs.get(mode)
                    if isinstance(attachment, dict) and attachment.get("document"):
                        st.write(f"**{label}** · {attachment.get('filename', 'SONARA.json')}")
                        st.caption("SHA-256: " + str(attachment.get("sha256", "")))
                        st.json(attachment["document"], expanded=False)
                        st.download_button(
                            f"⬇ Descargar proyecto SONARA · {label}",
                            json.dumps(attachment["document"], ensure_ascii=False, indent=2),
                            file_name=attachment.get("filename", f"sonara_{mode}.json"),
                            mime="application/json",
                            key=f"c5l2_s4_teacher_download_{mode}"
                        )
                    else:
                        st.caption(f"{label}: sin JSON guardado.")
            if stage==3:
                st.markdown("**Pauta de corrección · Etapa 3**")
                st.write("**A · Sistemas:** conservar M-01, L-01, F-01, V-01, S-01, IS-01 y T-01/T-02/T-03 como materialidad académica original. No exigir al estudiante volver a seleccionar esos sistemas.")
                st.write("**B · Geometría y materiales:** dormitorio y estar del piso 5; comprobar volúmenes recuperados de Etapa 2 y superficies de piso, cielo, muros, puerta y ventana. Los acabados físicos son los T-01/T-02/T-03 y V-01 del encargo; los presets genéricos de SONARA son equivalencias de cálculo y no ensayos del acabado.")
                st.markdown("**Respuesta docente · α(f) de los acabados originales**")
                st.table([
                    {"Material": label,
                     **{str(hz) + " Hz": format(alpha, ".2f")
                        for hz, alpha in zip(TR_OCTAVE_BANDS, TR_SONARA_PRESETS[label])}}
                    for label in (
                        "Hormigón / superficie dura", "Yeso pintado",
                        "Vidrio", "Puerta de madera maciza"
                    )
                ])
                st.markdown(
                    "**Asignación de la condición original:** "
                    "piso dormitorio laminado y piso estar cerámica → "
                    "**Hormigón / superficie dura** (aproximación reflectante); "
                    "cielos y muros pintados → **Yeso pintado**; "
                    "puerta interior docente → **Puerta de madera maciza** "
                    "(curva genérica de referencia NBR 12179); ventana → **Vidrio**. "
                    "Alfombra, cielo acústico y panel de lana mineral no son "
                    "terminaciones originales: se reservan para variantes."
                )
                st.markdown("**Solución docente · reverberación original con Sabine**")
                st.caption(
                    "Resultados del modelo equivalente vacío, usando exactamente "
                    "las áreas del suplemento, puerta de madera maciza y presets "
                    "de α(f) indicados. A(f) = ΣSᵢαᵢ(f); "
                    "TR(f) = 0,161·V/A(f). Son predicciones docentes, "
                    "no mediciones del edificio."
                )
                st.table([
                    {"Recinto":"Dormitorio", "Piso":"8,06", "Cielo":"8,06",
                     "Muros opacos":"26,82", "Puerta madera":"1,68",
                     "Ventana":"0,00", "Volumen m³":"20,15"},
                    {"Recinto":"Estar", "Piso":"9,1125", "Cielo":"9,1125",
                     "Muros opacos":"27,06", "Puerta madera":"1,68",
                     "Ventana":"2,16", "Volumen m³":"22,78125"},
                ])
                st.table([
                    {"Octava Hz":125, "A dormitorio m²":3.804,
                     "TR dormitorio s":0.853, "A estar m²":4.332,
                     "TR estar s":0.847},
                    {"Octava Hz":250, "A dormitorio m²":1.993,
                     "TR dormitorio s":1.628, "A estar m²":2.197,
                     "TR estar s":1.669},
                    {"Octava Hz":500, "A dormitorio m²":1.657,
                     "TR dormitorio s":1.958, "A estar m²":1.816,
                     "TR estar s":2.019},
                    {"Octava Hz":1000, "A dormitorio m²":2.737,
                     "TR dormitorio s":1.185, "A estar m²":2.914,
                     "TR estar s":1.259},
                    {"Octava Hz":2000, "A dormitorio m²":3.468,
                     "TR dormitorio s":0.935, "A estar m²":3.649,
                     "TR estar s":1.005},
                    {"Octava Hz":4000, "A dormitorio m²":3.898,
                     "TR dormitorio s":0.832, "A estar m²":4.102,
                     "TR estar s":0.894},
                ])
                st.info(
                    "Método y criterio: **Sabine** con las curvas α genéricas "
                    "de SONARA, excepto la puerta de madera maciza (curva "
                    "NBR 12179 adoptada también en SONARA). "
                    "En dormitorio se adopta **0 m² de ventana** "
                    "únicamente en el modelo docente interior. "
                    "Si el alumno usa **Eyring** o una geometría mejor "
                    "justificada, el TR cambia: calificar la consistencia "
                    "del modelo y no exigir estos números como universales."
                )
                st.write("**C · Reverberación:** exigir **TR en segundos por bandas de octava de 125, 250, 500, 1000, 2000 y 4000 Hz**, para ambos recintos. Comparar los resultados de SONARA con las superficies, curvas de α seleccionadas y el método Sabine/Eyring declarado. No hay TR fijado por defecto ni certificado.")
                st.caption("Guardar avance no finaliza la etapa; Completar Etapa 3 valida registro de geometría, materiales, fuentes α(f) y TR por bandas, no certifica exactitud de los cálculos.")
def run_stage(stage,lab,saved,runtime):
    _bind(runtime)
    stage=max(0,min(10,int(stage)))
    if stage==0:_stage0(lab,saved)
    elif stage==1:_stage1(lab,saved)
    elif stage==2:_stage2(lab,saved)
    elif stage==3:_stage3(lab,saved)
    elif stage==4:_stage4(lab,saved)
    elif stage==5:_stage5(lab,saved)
    elif stage==6:_stage6(lab,saved)
    elif stage==7:_stage7(lab,saved)
    elif stage==8:_stage8(lab,saved)
    elif stage==9:_stage9(lab,saved)
    else:_stage10(lab,saved)
    _teacher(stage,saved)
