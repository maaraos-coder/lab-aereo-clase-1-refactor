"""Etapa 9 · Cuestionario oficial de comprensión, 30 puntos."""

import json


QUESTIONS=[
    ("Comparabilidad","Para comparar el modelo original con el controlado, ¿qué cambio principal debe existir entre ambos?",[
        "Solo la medida de control y los ajustes indispensables para implementarla",
        "La ubicación de todos los receptores",
        "Las potencias de todas las fuentes",
        "La resolución y el método de cálculo",
    ],0,"Una comparación válida conserva la línea base y modifica la medida que se desea evaluar."),
    ("TL e inserción","¿Por qué no corresponde restar directamente el TL de un panel al LAeq de un receptor?",[
        "Porque el TL solo se expresa en Hz",
        "Porque la reducción final depende del sistema completo, aberturas, orientación, otras caras y propagación",
        "Porque el TL siempre es menor que 10 dB",
        "Porque el LAeq no admite ninguna resta",
    ],1,"El TL caracteriza la transmisión del elemento; no equivale automáticamente a la reducción global en el receptor."),
    ("Barrera","¿Cuál es la condición geométrica esencial para que una barrera produzca apantallamiento?",[
        "Tener cualquier masa superficial",
        "Interrumpir la línea de visión acústica entre fuente y receptor",
        "Estar detrás del receptor",
        "Tener la misma altura que la fuente",
    ],1,"La barrera debe interceptar la trayectoria directa y generar una diferencia de recorrido por difracción."),
    ("Semiencierro","En un semiencierro, ¿por qué importa la orientación de la cara abierta?",[
        "Porque determina hacia dónde se emite con menor atenuación",
        "Porque cambia automáticamente el nivel de potencia de la máquina",
        "Porque elimina la absorción interior",
        "Porque convierte el equipo en una fuente lineal",
    ],0,"La abertura mantiene una trayectoria de emisión dominante cuya orientación respecto del receptor es decisiva."),
    ("Suma energética","Dos fuentes independientes aportan 70 dB(A) cada una en un receptor. El total aproximado es:",[
        "70 dB(A)","73 dB(A)","140 dB(A)","67 dB(A)",
    ],1,"Dos contribuciones iguales sumadas energéticamente producen aproximadamente +3 dB."),
    ("Límite de referencia","Para Zona III, los límites usados como referencia educativa en este laboratorio son:",[
        "55 dB(A) diurno y 45 dB(A) nocturno",
        "60 dB(A) diurno y 50 dB(A) nocturno",
        "65 dB(A) diurno y 50 dB(A) nocturno",
        "70 dB(A) diurno y 60 dB(A) nocturno",
    ],2,"El laboratorio utiliza 65 dB(A) diurno y 50 dB(A) nocturno como referencia del DS N.º 38/2011 del MMA para Zona III."),
    ("Receptor y zona","¿Qué ubicación determina el límite de referencia que se aplica en la comparación?",[
        "La ubicación de la fuente más ruidosa",
        "La ubicación del receptor",
        "El centro geométrico de la obra",
        "El punto donde está la barrera",
    ],1,"El límite se asocia a la zona donde se encuentra el receptor evaluado."),
    ("Alcance del modelo","Si Noise Map Lab entrega un valor bajo el límite de referencia, la conclusión correcta es:",[
        "El modelo predice un nivel bajo el límite; no reemplaza una verificación normativa mediante medición",
        "La autoridad debe certificar automáticamente el cumplimiento",
        "La fuente deja de estar regulada",
        "El resultado no requiere revisar los datos de entrada",
    ],0,"Una modelación permite una evaluación predictiva, pero no sustituye por sí sola el procedimiento de medición aplicable."),
    ("Ley de masa","La estimación TL ≈ 20·log10(m·f) − 47 utilizada para una placa representa:",[
        "Un certificado garantizado para cualquier cerramiento",
        "Una aproximación educativa para una hoja simple, homogénea y sellada en la región controlada por masa",
        "La reducción exacta en todos los receptores",
        "El índice de absorción del revestimiento interior",
    ],1,"La ley de masa es una aproximación y no representa resonancias, coincidencia, fugas ni el sistema completo instalado."),
    ("Iteración","La solución controlada reduce el nivel de 72 a 68 dB(A), pero el límite de referencia es 65 dB(A). ¿Qué corresponde concluir?",[
        "La medida no produjo ningún efecto",
        "La medida mejora el resultado, pero es insuficiente y debe optimizarse o complementarse",
        "La medida cumple porque redujo más de 3 dB",
        "Debe cambiarse el receptor para obtener cumplimiento",
    ],1,"Una reducción positiva no garantiza suficiencia; el resultado final todavía se encuentra sobre el límite."),
]


def _grade(score,max_score=30.0):
    percentage=100*float(score)/float(max_score)
    if percentage<60:
        return round(1.0+3.0*(percentage/60.0),1)
    return round(4.0+3.0*((percentage-60.0)/40.0),1)


def _payload(row):
    value=(row or {}).get("answer") or {}
    if isinstance(value,str):
        try:return json.loads(value)
        except Exception:return {}
    return value if isinstance(value,dict) else {}


def _read_only(st,answers,score):
    correct=sum(answers.get(str(i))==q[2][q[3]] for i,q in enumerate(QUESTIONS))
    a,b,c=st.columns(3)
    a.metric("Respuestas correctas",f"{correct}/10")
    b.metric("Puntaje",f"{score:g}/30")
    c.metric("Nota",f"{_grade(score):.1f}")
    st.success("Cuestionario enviado. La entrega quedó bloqueada en modo solo lectura.")
    for i,q in enumerate(QUESTIONS,1):
        selected=answers.get(str(i-1))
        expected=q[2][q[3]]
        with st.container(border=True):
            st.markdown(f"**{i}. {q[1]}**")
            st.write(f"Tu respuesta: {selected or 'Sin respuesta'}")
            if selected==expected:
                st.success("Correcta · 3/3 puntos")
            else:
                st.error("Incorrecta · 0/3 puntos")
                st.write(f"Respuesta correcta: {expected}")
            st.caption(q[4])


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 9 · LABORATORIO 2",
        "Cuestionario oficial de comprensión",
        "Evaluar individualmente los conceptos aplicados durante las Etapas 1 a 8.",
        show_overview=False,duration_minutes=30,
    )
    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">EVALUACIÓN OFICIAL · 30 PUNTOS</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">10 preguntas · 3 puntos cada una</div>
      <div style="color:#526f80;line-height:1.6">El cuestionario integra modelación, suma energética, medidas de control, TL, comparación de escenarios y límite de referencia. La nota utiliza 60 % de exigencia.</div>
    </div>
    """,unsafe_allow_html=True)

    role=st.session_state.get("role")
    if role=="Docente":
        st.markdown("### Pauta docente")
        for i,q in enumerate(QUESTIONS,1):
            with st.container(border=True):
                st.markdown(f"**{i}. {q[1]}**")
                st.caption(f"{q[0]} · 3 puntos")
                for j,option in enumerate(q[2]):st.write(("✓ " if j==q[3] else "○ ")+option)
                st.info(q[4])
        st.caption("Las entregas se revisan en Evaluaciones entregadas. El cuestionario se corrige automáticamente sobre 30 puntos.")
        return

    remote=runtime["_evaluation_row"](9,"c4l2_final_quiz")
    if remote or saved.get("c4l2_s9_submitted"):
        payload=_payload(remote) if remote else saved.get("c4l2_s9_submission") or {}
        answers=payload.get("answers") or saved.get("c4l2_s9_answers") or {}
        score=(remote or {}).get("teacher_score")
        if score is None:score=(remote or {}).get("auto_score") if remote else saved.get("c4l2_s9_score",0)
        _read_only(st,answers,float(score or 0))
        return

    for index,value in (saved.get("c4l2_s9_answers") or {}).items():
        key=f"c4l2_s9_q{index}"
        idx=int(index)
        if key not in st.session_state and idx<len(QUESTIONS) and value in QUESTIONS[idx][2]:
            st.session_state[key]=value

    answered=sum(st.session_state.get(f"c4l2_s9_q{i}") is not None for i in range(len(QUESTIONS)))
    a,b,c=st.columns(3)
    a.metric("Respondidas",f"{answered}/10")
    b.metric("Puntaje máximo","30 puntos")
    c.metric("Exigencia","60 %")
    if not saved.get("done_8"):
        st.warning("Se recomienda completar la Etapa 8 antes de enviar el cuestionario.")

    for i,q in enumerate(QUESTIONS,1):
        with st.container(border=True):
            st.markdown(f"**{i}. {q[1]}**")
            st.caption(f"{q[0]} · 3 puntos")
            st.radio("Selecciona una alternativa",q[2],index=None,key=f"c4l2_s9_q{i-1}",label_visibility="collapsed")

    c1,c2=st.columns(2)
    if c1.button("Guardar borrador",use_container_width=True,key="c4l2_s9_draft"):
        answers={str(i):st.session_state.get(f"c4l2_s9_q{i}") for i in range(len(QUESTIONS))}
        saved["c4l2_s9_answers"]=answers
        runtime["_save"](lab,saved,9)
        st.success("Borrador guardado. Todavía puedes modificar las respuestas.")

    if c2.button("Enviar cuestionario definitivo",type="primary",use_container_width=True,key="c4l2_s9_submit"):
        answers={str(i):st.session_state.get(f"c4l2_s9_q{i}") for i in range(len(QUESTIONS))}
        if any(value is None for value in answers.values()):
            st.warning("Responde las 10 preguntas antes de realizar el envío definitivo.")
        else:
            score=sum(3 for i,q in enumerate(QUESTIONS) if answers[str(i)]==q[2][q[3]])
            payload={
                "version":"c4l2_stage9_v1","answers":answers,"score":score,"max_score":30,
                "correct_answers":{str(i):q[2][q[3]] for i,q in enumerate(QUESTIONS)},
                "grade":_grade(score),
            }
            stored=runtime["_submit_evaluation"](
                9,"c4l2_final_quiz","Curso 4 · Laboratorio 2 · Cuestionario oficial",
                payload,score,30,f"Resultado automático: {score}/30 puntos · nota {_grade(score):.1f}.",
            )
            saved["c4l2_s9_answers"]=answers
            saved["c4l2_s9_submission"]=payload
            saved["c4l2_s9_score"]=score
            saved["c4l2_s9_grade"]=_grade(score)
            saved["c4l2_s9_submitted"]=True
            saved["done_9"]=True
            runtime["_save"](lab,saved,9)
            if not stored:
                st.warning("El cuestionario quedó guardado en tu progreso, pero no fue posible registrar la entrega remota en este momento.")
            st.rerun()

