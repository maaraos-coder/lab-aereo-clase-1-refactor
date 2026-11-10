"""Curso 5 · Laboratorio 2: proyecto residencial real, meta ISO/TS 19488 Clase B.

Las etapas 0–8 son formativas; la 9 evalúa 30 puntos y la 10 consolida
una entrega de desarrollo de 70 puntos para evaluación docente.
Los cálculos acústicos se realizan en SONARA, no en esta aplicación.
"""
from __future__ import annotations
import json
from copy import deepcopy

CLASS_ID = "clase-10-certificaciones-lab-2"
SONARA_URL = "https://sonara-ea1b.onrender.com/"
PROJECT = "Proyecto Inmobiliario DS19 y DS49 Barrio Balmaceda"
SITE = "Lote 1 · Edificio A1 · vivienda tipo A de piso intermedio"
STANDARD = "ISO/TS 19488:2021"
CASES = {
    "AI-01": ("Aislamiento aéreo entre viviendas", "DₙT,w y adaptación espectral aplicable", "Muro separador y flancos"),
    "IM-01": ("Ruido de impacto de vivienda superior", "L′ₙT,w y término de baja frecuencia aplicable", "Losa, piso y transmisiones laterales"),
    "FA-01": ("Aislamiento de fachada", "D₂m,nT,w y adaptación apropiada", "Paño opaco, ventana y sellos"),
    "IN-01": ("Ruido de instalaciones", "LAeq,nT o LAFmax,nT según la operación", "Fuente, fijaciones, vías aérea y estructural"),
}
STAGES = [
 ("Encargo profesional y alcance", "Diseñar una vivienda del proyecto real para los requisitos de Clase B."),
 ("Reconocimiento documental", "Identificar proyecto, vivienda, láminas y evidencias."),
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
 0: "Distinguir objetivo Clase B de certificación real: el laboratorio evalúa cuatro casos representativos, no declara automáticamente clase global del edificio.",
 1: "Proyecto real Barrio Balmaceda, Renca. Lote 1 (DS19), edificio A1 y una tipología A de piso intermedio. Comprobar edificio, lámina, nivel y relación de las viviendas.",
 2: "La ficha de referencia se resuelve únicamente con cotas verificables: S separador = longitud efectiva × altura; V = superficie útil del recinto × altura. Identificar cara útil de muro, superficies vidriadas y paños opacos. No confundir superficie de tipología completa con superficie de recinto. Registrar plano/cota y tolerancia para cada valor.",
 3: "Comprobar material de cada hoja, espesor, masa superficial, puentes rígidos, uniones, características de capa resiliente, solución de ventana completa, TR y condiciones de fuente. Separar lo documentado de hipótesis docentes.",
 4: "Exigir DₙT,w y adaptación pertinente con flancos y misma geometría en original/variante; Rw del elemento aislado no sustituye aislamiento entre recintos.",
 5: "Conservar condición original de entrepiso; justificar s′ o ΔL ensayado, masa de sobrelosa, continuidad perimetral y vías indirectas. Revisar L′ₙT,w y el descriptor complementario aplicable.",
 6: "Pedir superficies opaca/vidriada y prestaciones del conjunto ventana-marco-sello; no atribuir a vidrio aislado el desempeño de fachada terminada. Exposición exterior debe ser trazable o hipótesis.",
 7: "Para instalación sanitaria intermitente usar descriptor temporal apropiado; no declarar conformidad del total si solo modelaron transmisión aérea. Documentar montaje y vía estructural.",
 8: "La clasificación se realiza por el alumno consultando la tabla/nota exacta de ISO/TS 19488:2021. Sin umbral citado no se acredita Clase B; no inventar un resultado normativo.",
 9: "Cuestionario cerrado, diez ítems × 3 puntos, un intento; respuestas y puntaje quedan en responses para Evaluaciones entregadas.",
 10: "Rúbrica de 70 puntos; revisar documentación, geometría, sistemas y los cuatro modelos SONARA, clasificación y limitaciones. El docente asigna el puntaje práctico.",
}
RUBRIC = [
 ("Expediente y trazabilidad",8),("Ficha geométrica",12),
 ("Datos constructivos y supuestos",8),("Diseño aéreo",10),
 ("Diseño de impacto",10),("Diseño de fachada",8),
 ("Diseño de instalaciones",8),("Clasificación, informe y limitaciones",6),
]
QUIZ = [
 ("La superficie de la vivienda tipo A sirve para obtener directamente el volumen de un dormitorio.",False,"Se necesita la superficie del dormitorio y su altura."),
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
    return st.session_state.get("role")=="Docente"

def _readonly():
    return bool(st.session_state.get("projection_mode"))

def _header(stage):
    title,objective=STAGES[stage]
    header(f"ETAPA {stage} · LABORATORIO 2",title,objective,show_overview=False,duration_minutes=25 if stage<9 else 40)
    st.caption(f"Curso 5 · {PROJECT} · {SITE} · Objetivo Clase B · {STANDARD}")
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
    st.markdown("### Encargo profesional")
    st.markdown("Se analizará una vivienda tipo A de un piso intermedio del edificio A1, Lote 1, del proyecto real **Barrio Balmaceda**. El objetivo docente es diseñar soluciones que alcancen los **requisitos de Clase B** en cuatro familias acústicas. La geometría se extraerá de las láminas, no se entregará resuelta al estudiante.")
    st.warning("Se estudian cuatro situaciones; no se declara automáticamente la clasificación global del edificio ni se sustituye la medición en obra.")
    st.markdown("**Secuencia:** expediente → ficha geométrica → sistemas → SONARA (aéreo, impacto, fachada, instalaciones) → matriz ISO → evaluación.")
    st.markdown("**Documentos del encargo:** Anexo N.º 3 Planos; descripción del proyecto o actividad (DIA). Las láminas deben consultarse en su edición original.")
    if st.button("Registrar lectura del encargo",key="c5l2_s0"):
        _save(lab,saved,0,"c5l2_s0",{"acknowledged":True,"target":"B","scope":SITE})

def _stage1(lab,saved):
    _plain(1,lab,saved,"Identifica las láminas del Lote 1, edificio A1 y la vivienda tipo A de piso intermedio. Justifica cuál corresponde a la vivienda inferior, superior y contigua; no utilices superficies de otra tipología.",[
      ("location","Edificio, piso y tipología seleccionados","Identifica ubicación en planta y unidad exacta."),
      ("documents","Fuentes documentales: archivo, lámina y revisión","Incluye trazabilidad de plantas, cortes y elevaciones."),
      ("adjacencies","Relaciones horizontales, verticales y exposición exterior","Identifica la vivienda contigua, la superior y las fachadas."),
      ("limitations","Datos faltantes o ilegibles","Indica cómo resolverlos sin inventar cotas."),
    ])

def _stage2(lab,saved):
    _header(2)
    st.markdown("### Construye la ficha geométrica desde los planos")
    st.info("No se proporcionan medidas resueltas: identifica cada recinto, mide cotas y anota la lámina. No uses la superficie total de la vivienda como si fuera el área de un recinto.")
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
    st.markdown("### Inventario para calcular en SONARA")
    st.info("Los materiales se extraen de especificaciones si existen. En caso contrario se adoptan hipótesis de diseño claramente declaradas y justificadas.")
    cols=["Caso","Elemento","Sistema de capas / material","Espesor (mm)","Fuente documental / hipótesis","Propiedad acústica requerida","Observaciones sobre uniones"]
    old=saved.get("c5l2_s3") or {}
    rows=_table(old.get("systems") or [],cols,"c5l2_systems")
    assumptions=st.text_area("Condiciones comunes: TR, densidades, exposición exterior, funcionamiento de instalaciones",value=old.get("assumptions",""),height=130)
    if st.button("Guardar sistemas y condiciones",type="primary",key="c5l2_save_systems"):
        if not any(x.get("Elemento") for x in rows) or len(assumptions.strip())<25:
            st.warning("Registra los elementos y justifica las hipótesis de trabajo.")
        else:_save(lab,saved,3,"c5l2_s3",{"systems":rows,"assumptions":assumptions})

def _model(stage,lab,saved,case):
    _header(stage)
    title,descriptor,scope=CASES[case]
    st.markdown(f"### {case} · {title}")
    st.caption(f"Descriptor de referencia: {descriptor}. Elementos: {scope}. Selecciona umbral de Clase B consultando la norma, con fila/nota identificable.")
    if not saved.get("c5l2_s2"):
        st.warning("No hay ficha geométrica guardada de la Etapa 2.")
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

def _stage8(lab,saved):
    _header(8)
    st.markdown("### Matriz de verificación · meta Clase B")
    st.warning("La aplicación no asigna automáticamente la clase. Selecciona el descriptor correcto y verifica cada fila, adaptación y nota de ISO/TS 19488:2021.")
    for code,(name,desc,_) in CASES.items():
        st.markdown(f"**{code} · {name}** · {desc}")
    old=saved.get("c5l2_s8") or {}
    with st.form("c5l2_s8_form"):
        result={}
        for code in CASES:
            v=(old.get("cases") or {}).get(code) or {}
            st.markdown(f"#### {code}")
            result[code]={
              "descriptor":st.text_input("Descriptor del criterio",v.get("descriptor",""),key=f"c5l2_matrix_{code}_descriptor"),
              "baseline":st.text_input("Resultado original",v.get("baseline",""),key=f"c5l2_matrix_{code}_base"),
              "final":st.text_input("Resultado variante",v.get("final",""),key=f"c5l2_matrix_{code}_final"),
              "class_b":st.text_input("Umbral B y referencia exacta ISO",v.get("class_b",""),key=f"c5l2_matrix_{code}_iso"),
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
            if stage==2:st.info("Pauta geométrica: completar valores solo desde cotas legibles de los planos originales. No inventar dimensiones.")
            if stage in range(4,9):st.caption("Revisar el caso calculado en SONARA y el criterio ISO exacto, sin atribuir al software una certificación.")

def run_stage(stage,lab,saved,runtime):
    _bind(runtime)
    stage=max(0,min(10,int(stage)))
    if stage==0:_stage0(lab,saved)
    elif stage==1:_stage1(lab,saved)
    elif stage==2:_stage2(lab,saved)
    elif stage==3:_stage3(lab,saved)
    elif stage in (4,5,6,7):_model(stage,lab,saved,{4:"AI-01",5:"IM-01",6:"FA-01",7:"IN-01"}[stage])
    elif stage==8:_stage8(lab,saved)
    elif stage==9:_stage9(lab,saved)
    else:_stage10(lab,saved)
    _teacher(stage)
