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
 4: "Exigir DnT,w y adaptación pertinente para la transmisión entre viviendas, incluyendo flancos, y una variante coherente.",
 5: "Revisar LnT,w y términos aplicables de impacto, piso original y variante resiliente, incluyendo vías laterales.",
 6: "Verificar la secuencia NoiseMap: eje de Pasaje Chimbote, polígono de edificio, receptor exterior frente a fachada sur a altura de piso 5, auditoría geométrica válida, categorías 1/2/3/4a/4b, tres períodos y JSON trazable. No aplicar -3 dB al resultado incidente; evaluar límites del motor educativo antes de revisar paños, vanos, curva ventana-marco-sello y SONARA.",
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
 ("La superficie de la vivienda de Chimbote sirve para obtener directamente el volumen de un dormitorio.",False,"Se necesita la superficie del dormitorio y su altura."),
 ("DₙT,w entre viviendas se obtiene simplemente usando el Rw de un muro aislado.",False,"Se consideran recintos y vías laterales."),
 ("Es válido declarar una dimensión leída del plano sin identificar lámina o cota.",False,"Toda dimensión debe ser trazable."),
 ("El alumno puede reemplazar un dato desconocido por una hipótesis explícita justificada.",True,"Las hipótesis se identifican y se evalúa su sensibilidad."),
 ("Una mejora de Rw garantiza automáticamente Clase B para la vivienda completa.",False,"Hay que comprobar todos los criterios aplicables."),
 ("La suma de fachada debe considerar paño opaco y superficie acristalada.",True,"La composición y las fugas importan."),
 ("La clase de una solución se asigna a partir de un solo resultado de SONARA.",False,"La cobertura y todos los criterios aplicables deben verificarse."),
 ("Un piso flotante puede perder eficacia por puentes rígidos perimetrales.",True,"Los cortocircuitos reducen la mejora real."),
 ("El descriptor de instalaciones puede depender de si el funcionamiento es continuo o intermitente.",True,"Debe declararse el régimen de operación."),
 ("Una predicción de diseño equivale a certificar una vivienda construida.",False,"El resultado de diseño no sustituye la verificación de obra."),
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
    if _readonly():
        st.info("Vista de proyección: los cambios no se guardan en las entregas de los alumnos.")
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
        "**Calcula la superficie de piso y el volumen interior del recinto receptor de cada caso.** "
        "**AI-01, IM-01 e IN-01:** dormitorio de CH-A-P05-S03 (piso 5). "
        "**FA-01:** estar de esa misma vivienda. "
        "Área = superficie útil de piso (m²); volumen = área útil × altura libre (m³). "
        "Para recintos irregulares descompón la geometría según los planos."
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
            "Área (m²)": st.column_config.TextColumn("Área piso m²", width="small", help="Superficie útil horizontal del piso del recinto receptor, no de sus muros."),
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
        "**¿Qué superficie se pide?** **AI-01:** área del muro medianero M-01 "
        "entre el estar vecino y el dormitorio. **IM-01:** área de losa L-01 "
        "compartida con el dormitorio superior. **FA-01:** área bruta del paño "
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
            "Longitud (m)": st.column_config.TextColumn("Longitud", width="small"),
            "Altura (m)": st.column_config.TextColumn("Altura", width="small"),
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
    _header(3)
    st.markdown("### Caracterización de la materialidad original")
    st.info("La condición inicial del edificio para este ejercicio está **definida en una ficha de especificaciones docentes**. No inventes materiales ni agregues mejoras en esta etapa. Identifica cada sistema, consulta sus parámetros y prepara los modelos iniciales en SONARA.")
    st.markdown("#### A · Sistemas originales del encargo")
    st.dataframe(BASE_CONSTRUCTION,hide_index=True,use_container_width=True)
    st.caption("Todos los sistemas se adoptan como supuestos docentes. No constituyen especificaciones verificadas del proyecto real. Los valores Rw, R(f), ΔL(f) o resultados de fachada NO vienen precalculados. La identificación de los nueve componentes T/M/L/F/V/S/IS forma parte del ejercicio.")
    st.markdown("#### B · Caracteriza los sistemas para SONARA")
    cols=["Código base","Caso","Material / composición adoptada","Geometría desde Etapa 2","Dato acústico o curva requerida","Fuente técnica o hipótesis","Uniones, flancos y montaje"]
    old=saved.get("c5l2_s3") or {}
    rows=_table(old.get("systems") or [],cols,"c5l2_systems")
    st.markdown("#### C · Reverberación calculada en SONARA")
    st.info("Determina volumen y superficies del recinto desde la geometría de Etapa 2, asigna absorción por bandas a pisos, cielo, muros, puertas y ventanas, y calcula TR en SONARA. No se entrega un TR fijo. Si una cota no está acreditada, aplica exclusivamente un supuesto identificado del suplemento.")
    tr_details=st.text_area("Resultados TR de SONARA por banda, superficies de absorción, fuentes alfa y método",value=old.get("tr_details",""),height=130)
    st.markdown("#### D · Condiciones comunes y trazabilidad")
    assumptions=st.text_area("Registra densidades, tránsito supuesto, descarga WC de vivienda superior y trayecto hipotético, curvas y límites de validez",value=old.get("assumptions",""),height=140)
    st.markdown("#### E · Qué tendrá que diseñarse después")
    st.markdown("En las Etapas **4–7** debes proponer tus variantes: refuerzo de separador, pavimento resiliente, solución de fachada y control de instalación. Conserva el **mismo modelo original** al comparar con la variante.")
    if st.button("Guardar caracterización original",type="primary",key="c5l2_save_systems"):
        codes={str(x.get("Código base","")).strip().upper() for x in rows if isinstance(x,dict)}
        expected={entry["Código"] for entry in BASE_CONSTRUCTION}
        missing=sorted(expected-codes)
        if missing:
            st.warning("Completa la caracterización para los nueve componentes: "+", ".join(missing)+".")
        elif len(tr_details.strip())<40:
            st.warning("Documenta el cálculo del TR realizado en SONARA, sus bandas y las absorciones utilizadas.")
        elif len(assumptions.strip())<40:
            st.warning("Justifica la procedencia de los parámetros acústicos, condiciones y limitaciones (mínimo 40 caracteres).")
        else:
            _save(lab,saved,3,"c5l2_s3",{"systems":rows,"assumptions":assumptions,"tr_details":tr_details,"base_version":"chimbote_original_v1"})


def _model(stage,lab,saved,case):
    _header(stage)
    title,descriptor,scope=CASES[case]
    st.markdown(f"### {case} · {title}")
    st.caption(f"Descriptor de referencia: {descriptor}. Elementos: {scope}. Selecciona umbral de Clase B consultando la norma, con fila/nota identificable.")
    if not saved.get("c5l2_s2"):
        st.warning("No hay ficha geométrica guardada de la Etapa 2.")
    criteria=(saved.get("c5l2_s1") or {}).get("criteria") or {}
    selected=criteria.get(case) or {}
    if selected:
        st.markdown("#### Criterio Clase B previamente definido por el alumno")
        st.caption(f"{selected.get('descriptor','')} · {selected.get('direction','')} {selected.get('limit','')} · Fuente: {selected.get('reference','')}")
        st.caption(selected.get("condition",""))
    else:
        st.warning("Define primero el requisito Clase B de este caso en la Etapa 1. Los límites normativos no se proporcionan de forma automática.")
    old=saved.get(f"c5l2_s{stage}") or {}
    with st.form(f"c5l2_model_{case}"):
        fields={}
        fields["geometry"]=st.text_area("Geometría obtenida del plano y trasladada a SONARA",old.get("geometry",""))
        fields["base"]=st.text_area("Sistema original y resultado SONARA (descriptor, valor, unidades, versión)",old.get("base",""))
        fields["variant"]=st.text_area("Variante diseñada y resultado SONARA (descriptor, valor, unidades, versión)",old.get("variant",""))
        fields["target"]=st.text_area("Criterio Clase B: descriptor, umbral, sentido, tabla/nota de la norma",old.get("target",""))
        fields["comparison"]=st.text_area("Comparación, margen, limitaciones y evidencia SONARA",old.get("comparison",""))
        submitted=st.form_submit_button("Guardar resultados y alternativa",type="primary")
    if submitted:
        if any(len(v.strip())<18 for v in fields.values()):
            st.warning("Registra geometría, ambos modelos, requisito ISO y comparación de manera verificable.")
        else:_save(lab,saved,stage,f"c5l2_s{stage}",{"case":case,**fields})

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
sur. Finaliza el trazado siguiendo los controles de dibujo. La calle debe quedar
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
los caudales y velocidades por categoría. Para este ejercicio utiliza
los datos **supuestos** de la sección «Escenario de tránsito supuesto».
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
por los supuestos que figuran en la ficha de esta etapa.

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
**receptor, edificio y vía** elegidos; después pulsa
**Importar niveles a la ficha de fachada**.
Registra la distancia y altura obtenidas, el método y las limitaciones,
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
    st.markdown("#### Importar resultado desde NoiseMap (opcional)")
    imported_file=st.file_uploader("Archivo JSON exportado desde NoiseMap",type=["json"],
                                   key="c5l2_noise_import")
    imported=None
    if imported_file is not None:
        try:
            imported=json.loads(imported_file.getvalue().decode("utf-8-sig"))
            if not isinstance(imported,dict) or "receiver_period_levels_dba" not in imported:
                st.warning("El archivo no contiene los niveles de período del receptor; revisa el formato exportado.")
                imported=None
            elif any(imported["receiver_period_levels_dba"].get(k) is None for k in ("day","evening","night")):
                st.warning("El archivo tiene uno o más períodos sin niveles calculados. No puede transferirse como tres niveles válidos.")
                imported=None
        except (UnicodeError,ValueError,AttributeError,TypeError):
            imported=None
            st.error("No se pudo leer el JSON de NoiseMap.")
    if imported is not None:
        source_method=str(imported.get("method",""))
        st.warning("El archivo describe: "+source_method+
                   ". La propagación educativa de NoiseMap NO corresponde a CNOSSOS-EU 2.5 completo.")
        if st.button("Importar niveles a la ficha de fachada",key="c5l2_apply_noise_result"):
            imported_audit=imported.get("facade_geometry_audit") or {}
            if imported.get("incident_sound") is not True or not imported_audit.get("valid_for_incident_facade_demo"):
                st.error("La exportación debe corresponder a Lden incidente con auditoría de fachada válida; vuelve a calcular en NoiseMap.")
                st.stop()
            for key,value in imported["receiver_period_levels_dba"].items():
                if key in ("day","evening","night") and value is not None:
                    st.session_state[f"c5l2_ext_{key}"]=str(round(float(value),2))
            imported_geometry=imported.get("facade_geometry_audit") or imported.get("geometry") or {}
            imported_label="Importación NoiseMap: "+source_method
            st.session_state["c5l2_imported_noise_provenance"]=imported_label
            st.session_state["c5l2_imported_noise_geom"]=imported_geometry
            st.session_state["c5l2_imported_noise_source"]={
                "road":imported.get("road_name",""),
                "building":imported.get("facade_building_name",""),
                "receiver":imported.get("receiver_name",""),
                "incident_sound":imported.get("incident_sound"),
                "normative":imported.get("normative"),
            }
            st.rerun()
    if st.session_state.get("c5l2_imported_noise_provenance"):
        st.info("Origen de niveles importados: "+st.session_state["c5l2_imported_noise_provenance"])
        source=st.session_state.get("c5l2_imported_noise_source") or {}
        geometry=st.session_state.get("c5l2_imported_noise_geom") or {}
        if source.get("road") or source.get("building") or source.get("receiver"):
            st.caption(
                "Modelo NoiseMap importado · Vía: "+str(source.get("road") or "sin especificar")+
                " · Edificio: "+str(source.get("building") or "sin especificar")+
                " · Receptor: "+str(source.get("receiver") or "sin especificar")
            )
        if "receiver_to_facade_m" in geometry:
            st.caption(
                "Auditoría importada · receptor–fachada: "+
                str(geometry["receiver_to_facade_m"])+" m · fachada–calle: "+
                str(geometry.get("facade_to_road_m","sin dato"))+" m · altura: "+
                str(geometry.get("receiver_height_m","sin dato"))+" m."
            )
            if not geometry.get("valid_for_incident_facade_demo",False):
                st.warning("La auditoría importada no validó la ubicación de fachada. Corrige el escenario en NoiseMap.")
        if source.get("incident_sound") is not True:
            st.warning("El JSON no declara cálculo incidente en fachada; verifica el método antes de utilizar los niveles.")
    default_flows={"Día":{"Livianos":80,"Pesados medianos":3,"Pesados":1,"Motocicletas":7},
                   "Tarde":{"Livianos":45,"Pesados medianos":1,"Pesados":0,"Motocicletas":4},
                   "Noche":{"Livianos":10,"Pesados medianos":0,"Pesados":0,"Motocicletas":1}}
    st.markdown("#### A · Escenario ficticio de tránsito elevado")
    st.warning("Los flujos de 80/45/10 livianos por hora (día/tarde/noche) son un **escenario docente intencionalmente elevado**, no aforos de Pasaje Chimbote ni estimaciones representativas del tránsito real. Mantén esa advertencia en los resultados; el pasaje no debe dibujarse como avenida.")
    with st.form("c5l2_traffic_and_facade"):
        p1,p2=st.columns(2)
        with p1:
            street=st.text_input("Vía modelada",value=traffic_old.get("street","Pasaje Chimbote"))
            speed=st.number_input("Velocidad de circulación [km/h]",min_value=5,max_value=130,
                                  value=int(traffic_old.get("speed",30)))
            road_surface=st.selectbox("Tipo de pavimento",["Asfalto convencional","Hormigón","Otro, justificar"],
                                     index=["Asfalto convencional","Hormigón","Otro, justificar"].index(traffic_old.get("surface","Asfalto convencional")))
        with p2:
            dist=st.number_input("Distancia calzada–fachada [m] (medir del plano)",min_value=0.0,max_value=500.0,
                                  value=float(traffic_old.get("distance",0)),step=0.5)
            receiver_height=st.number_input("Altura receptor exterior [m] (medir o justificar)",min_value=0.0,max_value=150.0,
                                            value=float(traffic_old.get("height",0)),step=0.5)
            receiver_ref=st.text_input("Fuente de las cotas del receptor y su orientación",value=traffic_old.get("receiver_ref",""))
        st.markdown("**Flujos medios horarios por período y categoría [veh/h]**")
        flows={}
        for period in ("Día","Tarde","Noche"):
            cols=st.columns(4)
            flows[period]={}
            for col,(cat,default) in zip(cols,default_flows[period].items()):
                previous=(traffic_old.get("flows") or {}).get(period) or {}
                flows[period][cat]=col.number_input(f"{period} · {cat}",min_value=0,max_value=100000,
                                                    value=int(previous.get(cat,default)),key=f"c5l2_t_{period}_{cat}")
        st.markdown("#### B · Nivel exterior en receptor (modelo documentado)")
        st.caption("Lden se calcula únicamente a partir de **tres niveles por período**. No se deriva de los flujos usando ecuaciones sin calibración.")
        p3,p4,p5=st.columns(3)
        levels={}
        for col,key,label in [(p3,"day","Lday [dB(A)]"),(p4,"evening","Levening [dB(A)]"),(p5,"night","Lnight [dB(A)]")]:
            levels[key]=col.text_input(label,value=str(traffic_old.get("levels",{}).get(key,"")),key=f"c5l2_ext_{key}")
        method=st.text_area("Método, versión del motor, geometría, evidencia y alcance (CNOSSOS-EU o aproximación identificada)",value=traffic_old.get("method",st.session_state.get("c5l2_imported_noise_provenance","")))
        st.markdown("#### C · Diseño de la fachada sur del estar en SONARA")
        fields={}
        for key,label in [
            ("geometry","Área bruta, área opaca y superficie vidriada; volumen y TR del recinto"),
            ("base","Fachada original en SONARA: entradas, curvas, descriptor y resultado"),
            ("variant","Variante de fachada en SONARA: sistema propuesto y resultado"),
            ("target","Requisito Clase B: descriptor, umbral, sentido y referencia ISO"),
            ("comparison","Comparación, margen, limitaciones y vínculo con la exposición exterior")]:
            fields[key]=st.text_area(label,value=old.get(key,""),height=100)
        submit=st.form_submit_button("Guardar modelación vial y diseño de fachada",type="primary")
    parsed={}
    if all(levels[k].strip() for k in ("day","evening","night")):
        try:
            parsed={k:float(levels[k].replace(",",".")) for k in ("day","evening","night")}
            if any(not math.isfinite(x) or x < -20 or x > 150 for x in parsed.values()):
                parsed={}
            if parsed:
                total=(12*10**(parsed["day"]/10)+4*10**((parsed["evening"]+5)/10)+8*10**((parsed["night"]+10)/10))/24
                computed=10*math.log10(total)
                st.metric("Lden exterior · calculado con niveles ingresados",f"{computed:.1f} dB(A)")
                st.caption("12 h día + 4 h tarde (+5 dB) + 8 h noche (+10 dB). La fórmula no valida el motor con que se calcularon los tres niveles.")
            else:computed=None
        except ValueError:
            computed=None
    else:computed=None
    if submit:
        if dist<=0 or receiver_height<=0 or not receiver_ref.strip():
            st.warning("Determina distancia, altura y fuente de cotas del receptor antes de guardar.")
        elif computed is None:
            st.warning("Ingresa tres niveles exteriores finitos y dentro de rango, calculados por un modelo acústico documentado.")
        elif len(method.strip())<40:
            st.warning("Identifica claramente el método, versión y limitaciones de la predicción exterior.")
        elif any(len(str(v).strip())<18 for v in fields.values()):
            st.warning("Completa la geometría y comparación de los dos diseños de fachada en SONARA.")
        else:
            record={"case":"FA-01","traffic":{"street":street,"speed":speed,"surface":road_surface,
                "distance":dist,"height":receiver_height,"receiver_ref":receiver_ref,
                "flows":flows,"levels":levels,"method":method,"lden":round(computed,2),
                "method_note":"Lden verified mathematically; this app does not perform CNOSSOS-EU emission/propagation"},
                **fields}
            _save(lab,saved,6,"c5l2_s6",record)
    st.caption("Esta etapa integra exposición exterior y aislamiento de fachada. La determinación de Clase B corresponde al alumno, no al motor de NoiseMap.")


def _stage8(lab,saved):
    _header(8)
    st.markdown("### Matriz de verificación · meta Clase B")
    st.warning("La aplicación no asigna automáticamente la clase. Selecciona el descriptor correcto y verifica cada fila, adaptación y nota de ISO/TS 19488:2021.")
    for code,(name,desc,_) in CASES.items():
        st.markdown(f"**{code} · {name}** · {desc}")
    old=saved.get("c5l2_s8") or {}
    initial=((saved.get("c5l2_s1") or {}).get("criteria") or {})
    if not initial:
        st.warning("Aún no hay una matriz de requisitos Clase B registrada en la Etapa 1.")
    with st.form("c5l2_s8_form"):
        result={}
        for code in CASES:
            v=(old.get("cases") or {}).get(code) or {}
            norm=initial.get(code) or {}
            st.markdown(f"#### {code}")
            if norm:st.caption(f"Requisito que definiste en Etapa 1: {norm.get('descriptor','')} · {norm.get('direction','')} {norm.get('limit','')} · {norm.get('reference','')}")
            result[code]={
              "descriptor":st.text_input("Descriptor del criterio",v.get("descriptor",norm.get("descriptor","")),key=f"c5l2_matrix_{code}_descriptor"),
              "baseline":st.text_input("Resultado original",v.get("baseline",""),key=f"c5l2_matrix_{code}_base"),
              "final":st.text_input("Resultado variante",v.get("final",""),key=f"c5l2_matrix_{code}_final"),
              "class_b":st.text_input("Umbral B y referencia exacta ISO",v.get("class_b",(norm.get("direction","")+" "+norm.get("limit","")+" · "+norm.get("reference","")).strip(" ·")),key=f"c5l2_matrix_{code}_iso"),
              "decision":st.selectbox("Verificación de la variante",["Pendiente","Cumple según predicción","No cumple","No determinable"],index=["Pendiente","Cumple según predicción","No cumple","No determinable"].index(v.get("decision","Pendiente")),key=f"c5l2_matrix_{code}_decision"),
            }
        conclusion=st.text_area("Alcance de la conclusión y verificaciones posteriores",old.get("conclusion",""),height=130)
        submitted=st.form_submit_button("Guardar matriz Clase B",type="primary")
    if submitted:
        if any(not x["class_b"].strip() or x["decision"]=="Pendiente" for x in result.values()) or len(conclusion.strip())<45:
            st.warning("Completa la referencia ISO, la decisión de cada caso y el alcance de la conclusión.")
        else:_save(lab,saved,8,"c5l2_s8",{"cases":result,"conclusion":conclusion})

def _grade(score,total=100):
    pct=100*float(score)/float(total)
    return round(1+3*pct/60,1) if pct<60 else round(4+3*(pct-60)/40,1)

def _get_submission(stage,question_key):
    if _readonly() or _is_teacher():return None
    client=_supabase()
    if client is None or not st.session_state.get("user_key"):return None
    try:
        r=(client.table("responses").select("answer,auto_score,teacher_score,status")
           .eq("class_id",CLASS_ID).eq("user_key",st.session_state["user_key"])
           .eq("stage",stage).eq("question_key",question_key).limit(1).execute())
        return (r.data or [None])[0]
    except Exception:
        return None

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
        for n,(q,answer,reason) in enumerate(QUIZ,1):
            st.write(f"**{n}. {q}** · {'Verdadero' if answer else 'Falso'} · {reason}")
        return
    remote=_get_submission(9,"c5l2_quiz_v1")
    if remote or saved.get("c5l2_s9_submitted"):
        row=remote or {}
        score=row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score", saved.get("c5l2_s9_score",0))
        st.success("Cuestionario enviado. No se permiten más intentos.")
        st.metric("Puntaje",f"{float(score or 0):g}/30")
        st.metric("Nota cuestionario",f"{_grade(float(score or 0),30):.1f}")
        return
    old=saved.get("c5l2_s9_draft") or {}
    answers={}
    for i,(q,_,_) in enumerate(QUIZ):
        val=old.get(str(i),"Sin responder")
        answers[str(i)]=st.radio(f"{i+1}. {q}",["Sin responder","Verdadero","Falso"],index=["Sin responder","Verdadero","Falso"].index(val),key=f"c5l2_quiz_{i}")
    a,b=st.columns(2)
    if a.button("Guardar borrador",key="c5l2_quiz_draft"):
        _save(lab,saved,9,"c5l2_s9_draft",answers)
        saved["done_9"]=False
    if b.button("Enviar cuestionario definitivo",type="primary",key="c5l2_quiz_submit"):
        if "Sin responder" in answers.values():
            st.warning("Responde todas las preguntas.")
            return
        score=sum(3 for i,(_,expected,_) in enumerate(QUIZ) if (answers[str(i)]=="Verdadero")==expected)
        payload={"version":1,"answers":answers,"max_score":30,"score":score,"target_class":"B"}
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

def _stage10(lab,saved):
    _header(10)
    st.markdown("### Expediente integrador · 70 puntos")
    st.markdown("La evaluación recupera el trabajo realizado en las Etapas 1–8. El docente revisará el informe y aplicará la rúbrica.")
    for title,points in RUBRIC:st.caption(f"{title}: {points} puntos")
    for stage in range(1,9):
        key=f"c5l2_s{stage}"
        with st.expander(f"Etapa {stage} · {STAGES[stage][0]} · {'Guardada' if saved.get(key) else 'Pendiente'}"):
            st.json(saved[key]) if saved.get(key) else st.info("Sin datos.")
    if _is_teacher():
        st.markdown("#### Pauta de evaluación")
        for title,points in RUBRIC:st.write(f"**{title} · {points} puntos**")
        st.info("Evaluar fuentes, coherencia geométrica, datos de SONARA, solución base/variante y trazabilidad. La nota práctica se asigna desde Evaluaciones entregadas.")
        return
    remote=_get_submission(10,"c5l2_report_v1")
    if remote or saved.get("c5l2_s10_submitted"):
        st.success("Informe enviado para evaluación docente. La entrega oficial está bloqueada.")
        return
    old=saved.get("c5l2_s10") or {}
    with st.form("c5l2_final_report"):
        report=st.text_area("Conclusión técnica: meta Clase B, resultados, alcance, incertidumbre y verificaciones de obra",old.get("report",""),height=230)
        evidence=st.text_area("Referencias a proyectos SONARA, versiones, resultados y anexos utilizados",old.get("evidence",""),height=150)
        submitted=st.form_submit_button("Enviar expediente definitivo · 70 puntos",type="primary")
    if submitted:
        missing=[i for i in range(1,9) if not saved.get(f"c5l2_s{i}")]
        if missing:
            st.warning("Antes del envío completa las Etapas: "+", ".join(map(str,missing)))
        elif len(report.strip())<240 or len(evidence.strip())<80:
            st.warning("Amplía la conclusión técnica (mínimo 240 caracteres) y las evidencias (mínimo 80).")
        else:
            payload={"version":1,"target_class":"B","standard":STANDARD,
                     "report":report,"evidence":evidence,
                     "stages":{str(i):saved[f"c5l2_s{i}"] for i in range(1,9)},
                     "rubric":RUBRIC,"practical_max":70,
                     "quiz_score":saved.get("c5l2_s9_score")}
            try:
                _submit(10,"c5l2_report_v1","Curso 5 · Laboratorio 2 · Informe integrador",payload,0,70)
                _save(lab,saved,10,"c5l2_s10",{"report":report,"evidence":evidence})
                saved["c5l2_s10_submitted"]=True
                _save_future_state(lab["id"],saved)
            except Exception:
                st.error("No se pudo confirmar la entrega. Reintenta sin cerrar la página.")
            else:st.success("Informe enviado a evaluación docente · 70 puntos de desarrollo práctico.")


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
    st.table([
        {"Caso":"AI-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³","Códigos":"HD-01 / HG-01"},
        {"Caso":"IM-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³","Códigos":"HD-01 / HG-01"},
        {"Caso":"FA-01","Recinto":"Estar P5","Largo":"3,75 m",
         "Ancho":"2,43 m","Altura":"2,50 m","Área piso":"9,11 m²",
         "Volumen":"22,78 m³","Códigos":"HE-01 / HG-01"},
        {"Caso":"IN-01","Recinto":"Dormitorio P5","Largo":"3,10 m",
         "Ancho":"2,60 m","Altura":"2,50 m","Área piso":"8,06 m²",
         "Volumen":"20,15 m³","Códigos":"HD-01 / HG-01"},
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
         "Longitud":"3,10 m","Altura":"2,50 m",
         "Superficie":"7,75 m²","Código":"HM-01 × HG-01"},
        {"Caso":"IM-01","Elemento":"L-01 · losa dormitorios",
         "Longitud":"3,10 m","Altura":"2,60 m (ancho)",
         "Superficie":"8,06 m²","Código":"HL-01 (superposición)"},
        {"Caso":"FA-01","Elemento":"F-01 · fachada sur estar",
         "Longitud":"2,43 m","Altura":"2,50 m",
         "Superficie":"6,075 m²","Código":"HF-02 × HG-01"},
        {"Caso":"IN-01","Elemento":"S-01 · cierre sanitario",
         "Longitud":"1,40 m","Altura":"2,50 m",
         "Superficie":"3,50 m²","Código":"HI-01 × HG-01"},
    ])
    st.caption(
        "En **IM-01**, la segunda dimensión se registra en el campo "
        "«Altura (m)» únicamente por compatibilidad con la tabla C: es el "
        "**ancho en planta de la losa (2,60 m)**, no su espesor ni la "
        "altura de un tabique. Lo mismo debe indicarse en «Lámina / cota»."
    )

    st.markdown("#### D · Fachada sur del estar (FA-01)")
    st.table([
        {"Campo":"Recinto receptor","Respuesta":"Estar CH-A-P05-S03 · P5"},
        {"Campo":"Orientación","Respuesta":"Sur → Pasaje Chimbote"},
        {"Campo":"Ancho docente fachada HF-02","Respuesta":"2,43 m"},
        {"Campo":"Altura útil HG-01","Respuesta":"2,50 m"},
        {"Campo":"Paño bruto de fachada","Respuesta":"2,43 × 2,50 = 6,075 m²"},
        {"Campo":"Ventana única HV-02","Respuesta":"1,80 × 1,20 = 2,160 m²"},
        {"Campo":"Paño opaco","Respuesta":"6,075 − 2,160 = 3,915 m²"},
        {"Campo":"Lámina / origen","Respuesta":"Planta P1 pág. 8 + sur P2 pág. 5; HF-02/HG-01/HV-02: DOCENTE"},
    ])
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


def _teacher(stage):
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
            if stage==3:
                st.info("Comprobar que el alumno determine TR por bandas en SONARA; no introducir valores fijos 0,5/0,6 s.")
def run_stage(stage,lab,saved,runtime):
    _bind(runtime)
    stage=max(0,min(10,int(stage)))
    if stage==0:_stage0(lab,saved)
    elif stage==1:_stage1(lab,saved)
    elif stage==2:_stage2(lab,saved)
    elif stage==3:_stage3(lab,saved)
    elif stage==6:_stage6(lab,saved)
    elif stage in (4,5,7):_model(stage,lab,saved,{4:"AI-01",5:"IM-01",7:"IN-01"}[stage])
    elif stage==8:_stage8(lab,saved)
    elif stage==9:_stage9(lab,saved)
    else:_stage10(lab,saved)
    _teacher(stage)
