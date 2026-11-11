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
 {"Código":"IS-01","Caso":"IN-01","Elemento":"Descarga sanitaria","Composición original":"PVC DN110 y descarga WC 6 L","Montaje":"Abrazaderas rígidas, escenario docente"},
 {"Código":"T-01","Caso":"TR","Elemento":"Piso estar","Composición original":"Cerámica adherida","Montaje":"Alfa por banda a documentar"},
 {"Código":"T-02","Caso":"TR","Elemento":"Muros y cielo","Composición original":"Pintura sobre superficies rígidas","Montaje":"Alfa por banda a documentar"},
 {"Código":"T-03","Caso":"TR","Elemento":"Piso dormitorio","Composición original":"Laminado sin aporte resiliente acreditado","Montaje":"Alfa por banda a documentar"},
]
GEOMETRY_ASSUMPTIONS = [
 ("DOC-01", "Planta tipo", "Parte 1 · PDF página 8 · verificar cotas del caso seleccionado"),
 ("DOC-02", "Corte general", "Parte 1 · PDF página 12 · verificar altura libre del recinto"),
 ("DOC-03", "Elevaciones", "Parte 2 · cotejar dimensiones de vanos"),
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
 ("Encargo profesional y alcance", "Diseñar una vivienda del proyecto real para los requisitos de Clase B."),
 ("Requisitos Clase B y reconocimiento documental", "Definir los cuatro criterios normativos antes de comenzar las modelaciones."),
 ("Ficha geométrica del alumno", "Extraer de planos las superficies, alturas, volúmenes y adyacencias."),
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
 0: "Caso fijo CH-A-P05-S03; corroborar en el plano original Torre A, hilera sur tercera vivienda desde poniente, piso 5; la marca destaca el sector, no reemplaza la geometría del dibujo.",
 1: "Verificar que el alumno haya consultado los criterios de Clase B de ISO/TS 19488:2021 para aislamiento aéreo, impacto, fachada e instalaciones, con descriptor, valor, dirección y referencia; no mostrar solución.",
 2: "Comprobar áreas, volúmenes, recintos contiguos, proyección del piso superior, altura efectiva, vanos y trazabilidad por lámina/cota. NO atribuir al sector cotas de otros departamentos ni completar dimensiones sin verificar.",
 3: "Materialidad original académica M-01 L-01 F-01 V-01 S-01 IS-01 T-01 T-02 T-03. Revisar superficies interiores, absorciones por banda y cálculo del TR en SONARA: no adoptar TR prefijado.",
 4: "Exigir DnT,w y adaptación pertinente para la transmisión entre viviendas, incluyendo flancos, y una variante coherente.",
 5: "Revisar LnT,w y términos aplicables de impacto, piso original y variante resiliente, incluyendo vías laterales.",
 6: "Verificar la secuencia NoiseMap: eje de Pasaje Chimbote, polígono de edificio, receptor exterior frente a fachada sur a altura de piso 5, auditoría geométrica válida, categorías 1/2/3/4a/4b, tres períodos y JSON trazable. No aplicar -3 dB al resultado incidente; evaluar límites del motor educativo antes de revisar paños, vanos, curva ventana-marco-sello y SONARA.",
 7: "Escenario sanitario académico: revisar Lw, condiciones de operación y vía aérea/estructural; no afirmar conformidad si la vía estructural queda sin modelar.",
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

def _student_document_pack():
    """Create a single download with the original Chimbote PDF and student annexes."""
    root = Path(__file__).resolve().parent.parent
    folder = root / "assets" / "curso5_lab2"
    plan = folder / "Chimbote_Torre_A_CH-A-P05-S03_planos.pdf"
    if not plan.is_file():
        return None, "Falta publicar el PDF original de planos resaltados en assets/curso5_lab2."
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
        bundle.write(plan, arcname="01_Planos/Chimbote_Torre_A_CH-A-P05-S03_planos.pdf")
        for doc in docs:
            bundle.write(doc, arcname="02_Anexos/" + doc.name)
        bundle.writestr("LEEME.txt",
            "Curso 5 Laboratorio 2 - Edificio Chimbote - Torre A - CH-A-P05-S03\\n"
            "Tercer departamento desde poniente de hilera sur, piso 5.\\n"
            "La materialidad indicada es academica. El alumno calcula geometria y reverberacion en SONARA.\\n"
            "El paquete no incluye la pauta docente ni requisitos normativos resueltos.\\n")
    return output.getvalue(), None


def _header(stage):
    title,objective=STAGES[stage]
    header(f"ETAPA {stage} · LABORATORIO 2",title,objective,show_overview=False,duration_minutes=25 if stage<9 else 40)
    st.caption(f"Curso 5 · {PROJECT} · {SITE} · Objetivo Clase B · {STANDARD}")
    if stage in (1,2,3):
        st.caption("Fuentes del ejercicio: planta tipo original, cortes, elevaciones y ficha académica. Toda cota debe provenir del dibujo o documentarse como hipótesis.")
    if stage in (2,3):
        st.link_button("Ver ficha geométrica del alumno", ANNEX_URL)
        st.link_button("Ver suplemento de cotas (sin resolver)", "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/blob/curso3-lab2-etapas-3-10/docs/curso5_lab2_chimbote_suplemento_cotas_alumno.md")
        st.link_button("Consultar materialidad original del ejercicio", MATERIALS_URL)
    if stage in range(4,9):
        st.link_button("Abrir SONARA · cálculos acústicos",SONARA_URL, use_container_width=False)


def _save(lab,saved,stage,key,value):
    if _readonly():
        st.info("Vista de proyección: los cambios no se guardan en las entregas de los alumnos.")
        return
    candidate=deepcopy(saved)
    candidate[key]=value
    candidate[f"done_{stage}"]=True
    candidate[f"c5l2_updated_{stage}"]=_now()
    try:
        _save_future_state(lab["id"],candidate)
    except Exception as error:
        st.error("No se pudo guardar esta etapa. Conserva tu información y vuelve a intentarlo.")
        return
    saved.update(candidate)
    st.success("Etapa guardada. Los datos estarán disponibles en las etapas siguientes.")

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

def _stage0(lab,saved):
    _header(0)
    st.markdown("### Encargo profesional · Edificio Chimbote")
    st.markdown("Trabajaremos con la **Torre A, piso 5, tercer departamento desde poniente en la hilera sur**, marcado sobre la planta tipo con el código académico **CH-A-P05-S03**. Identifica los recintos reales en los planos y diseña soluciones para las cuatro familias de Clase B ISO/TS 19488:2021.")
    st.warning("La marca de color es orientativa para localizar la unidad. No representa un área medida. Los cálculos, superficies, volúmenes y TR serán determinados por el alumno.")
    st.markdown("**Secuencia:** requisitos Clase B → geometría → materialidad y TR en SONARA → diseño aéreo, impacto, fachada e instalaciones → verificación → evaluación.")
    st.markdown("### Descarga única de documentación")
    st.caption("Un ZIP con planta tipo original (vivienda resaltada), cortes, elevaciones, especificaciones, suplemento de cotas y ficha de tránsito vial. La pauta docente queda excluida.")
    pack, issue = _student_document_pack()
    if pack is None:
        st.warning(issue + " Hasta incorporar el PDF binario a la rama, el botón de descarga completo está deshabilitado.")
    else:
        st.download_button("📥 Descargar planos y documentación del alumno (.zip)",data=pack,
            file_name="Curso5_Lab2_Chimbote_CH-A-P05-S03_Alumno.zip",mime="application/zip",
            type="primary",use_container_width=True,key="c5l2_docs_download")
    if st.button("Registrar lectura del encargo",key="c5l2_s0"):
        _save(lab,saved,0,"c5l2_s0",{"acknowledged":True,"target":"B","scope":SITE})


def _stage1(lab,saved):
    _header(1)
    st.markdown("### A · Define los requisitos normativos antes de modelar")
    st.info("Consulta ISO/TS 19488:2021 y determina los requisitos de **Clase B** para las cuatro situaciones. No basta con escribir 'B': identifica el descriptor exacto, umbral, condición, sentido de comparación y tabla/nota de la fuente.")
    st.caption("El caso de fachada puede depender de la exposición exterior y el de instalaciones del régimen de operación. Explica la condición que elegiste. Las cifras normativas se investigan por el alumno y NO se proporcionan en esta pantalla.")
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
        st.markdown("### B · Reconoce Torre A y la vivienda CH-A-P05-S03")
        descriptions=[
            ("location","Edificio, piso y vivienda seleccionados","Torre A, piso 5, tercera vivienda desde poniente en hilera sur (CH-A-P05-S03)."),
            ("documents","Documentación consultada","Archivo, lámina, revisión y cotas relevantes."),
            ("adjacencies","Relaciones horizontales, verticales y fachada","Identifica vivienda al oriente y vivienda superpuesta en piso 6. Verifica recintos realmente contiguos."),
            ("limitations","Datos faltantes y método para resolverlos","Distingue documentación del proyecto y supuestos del anexo."),
        ]
        documentation={}
        for key,label,explanation in descriptions:
            documentation[key]=st.text_area(label,value=old.get(key,""),help=explanation,height=80,key=f"c5l2_s1_{key}")
        submitted=st.form_submit_button("Guardar criterios Clase B y reconocimiento",type="primary")
    if submitted:
        incomplete=[code for code,row in fields.items() if
            not row["descriptor"].strip() or not row["limit"].strip() or
            row["direction"]=="Selecciona" or not row["reference"].strip() or
            len(row["condition"].strip())<20]
        missing_docs=[key for key,value in documentation.items() if len(value.strip())<15]
        if incomplete:
            st.warning("Faltan requisitos o referencias normativas de: "+", ".join(incomplete)+". Completa las condiciones para cada familia.")
        elif missing_docs:
            st.warning("Completa la identificación y trazabilidad documental antes de guardar la etapa.")
        else:
            _save(lab,saved,1,"c5l2_s1",{"criteria":fields,**documentation})
    if _is_teacher():
        st.caption("Pauta docente: revisar la ISO autorizada y la tabla exacta, sin asumir que todos los indicadores tienen un solo valor o se comparan en el mismo sentido. La etapa es formativa: el guardado no valida automáticamente la corrección de los umbrales.")



def _stage2(lab,saved):
    _header(2)
    st.markdown("### Construye la ficha geométrica desde los planos")
    st.info("Determina las superficies, alturas, volúmenes y separaciones desde la planta tipo, el corte y las elevaciones de Chimbote. No copies cotas de otro departamento; marca como pendiente cualquier dimensión no verificable.")
    old=saved.get("c5l2_s2") or {}
    rec_cols=["Recinto","Piso / unidad","Largo (m)","Ancho (m)","Altura (m)","Área (m²)","Volumen (m³)","Plano / cota"]
    sep_cols=["Caso","Recinto emisor","Recinto receptor","Elemento","Longitud (m)","Altura (m)","Superficie (m²)","Plano / cota"]
    env_cols=["Recinto","Orientación","Paño total (m²)","Ventanas (m²)","Opaco (m²)","Plano / cota"]
    st.markdown("#### A · Recintos y volúmenes")
    rooms=_table(old.get("rooms") or [],rec_cols,"c5l2_rooms")
    st.markdown("#### B · Separaciones y losas")
    sep=_table(old.get("separations") or [],sep_cols,"c5l2_separations")
    st.markdown("#### C · Fachada y ventanas")
    env=_table(old.get("facades") or [],env_cols,"c5l2_facades")
    with st.expander("Criterios de construcción de la ficha"):
        st.markdown("Identifica áreas efectivas, espesores, orientación, altura libre y volumen útil. Señala dimensiones deducidas de escala como estimaciones, no como cotas. Documenta fuente y unidades.")
    if st.button("Guardar ficha geométrica",type="primary",key="c5l2_save_geometry"):
        if not any(str(x.get("Recinto","")).strip() for x in rooms) or not any(str(x.get("Elemento","")).strip() for x in sep):
            st.warning("Incluye al menos un recinto y un elemento de separación identificados.")
        else:_save(lab,saved,2,"c5l2_s2",{"rooms":rooms,"separations":sep,"facades":env})

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
    assumptions=st.text_area("Registra densidades, Lden supuesto, descarga sanitaria, curvas de referencia y límites de validez",value=old.get("assumptions",""),height=140)
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
    st.info("Ubica el receptor exterior en la **fachada sur de CH-A-P05-S03**. La vía didáctica será **Pasaje Chimbote**, no Mirador Azul. Documenta la distancia y la altura del receptor desde los planos; la exposición exterior NO se fija de antemano.")
    st.link_button("🌍 Abrir NoiseMap · dirección oficial", "https://noisemap-akuzoft.vercel.app/",
                   help="Abre la herramienta de mapa de ruido y continúa con el procedimiento de esta etapa.")
    st.warning(
        "NoiseMap obtiene la **emisión vial CNOSSOS-EU §2.2** por octavas para vehículos "
        "**1, 2, 3, 4a y 4b**, pero la propagación hacia el receptor sigue usando el "
        "**motor exterior educativo**, no el método reglamentario CNOSSOS-EU §2.5. "
        "El Lden calculado se utiliza aquí como **estimación académica**, no como "
        "evaluación reglamentaria de exposición."
    )
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
frente a la **fachada sur**, a aproximadamente **0,1 m por fuera de su plano**,
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
            for key,value in imported["receiver_period_levels_dba"].items():
                if key in ("day","evening","night") and value is not None:
                    st.session_state[f"c5l2_ext_{key}"]=str(round(float(value),2))
            imported_geometry=imported.get("geometry") or {}
            imported_label="Importación NoiseMap: "+source_method
            st.session_state["c5l2_imported_noise_provenance"]=imported_label
            st.session_state["c5l2_imported_noise_geom"]=imported_geometry
            st.rerun()
    if st.session_state.get("c5l2_imported_noise_provenance"):
        st.info("Origen de niveles importados: "+st.session_state["c5l2_imported_noise_provenance"])
    default_flows={"Día":{"Livianos":80,"Pesados medianos":3,"Pesados":1,"Motocicletas":7},
                   "Tarde":{"Livianos":45,"Pesados medianos":1,"Pesados":0,"Motocicletas":4},
                   "Noche":{"Livianos":10,"Pesados medianos":0,"Pesados":0,"Motocicletas":1}}
    st.markdown("#### A · Escenario de tránsito supuesto")
    st.caption("Los aforos siguientes son **hipótesis académicas**, no registros reales del pasaje.")
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
        st.markdown("#### C · Diseño de fachada en SONARA")
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

def _teacher(stage):
    if _is_teacher():
        with st.expander(f"Pauta docente · Etapa {stage}",expanded=False):
            st.write(TEACHER[stage])
            if stage==2:
                st.warning("No hay ficha numérica cerrada para CH-A-P05-S03. Las cotas/áreas anteriores de Barrio Balmaceda NO son válidas para este proyecto.")
                st.link_button("Auditoría geométrica de Chimbote (solo docente)", "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/blob/curso3-lab2-etapas-3-10/docs/curso5_lab2_chimbote_pauta_docente.md")
                st.link_button("Pauta docente · submodelo geométrico resuelto", "https://github.com/maaraos-coder/lab-aereo-clase-1-refactor/blob/curso3-lab2-etapas-3-10/docs/curso5_lab2_chimbote_pauta_submodelo_docente.md")
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
