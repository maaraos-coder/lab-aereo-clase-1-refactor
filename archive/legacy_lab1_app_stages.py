"""Versiones históricas de las etapas 0–10 que antes permanecían duplicadas en app.py.

No participan en LAB_STAGE_FUNCTIONS. Se conservan únicamente como referencia histórica.
"""

def stage0():
    header("ETAPA 0 · BIENVENIDA","Laboratorio del curso Aislamiento a Ruido Aéreo",
           "Una experiencia visual para comprender el fenómeno, experimentar con variables y decidir con criterio técnico y económico.")
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Duración total de la clase: 4 horas</strong>'
        f'<br><span>{sum(STAGE_MINUTES.values())} min de aprendizaje y aplicación + {BREAK_MINUTES} min de pausa</span></div>'
        f'<div><strong>{TOTAL_CLASS_MINUTES} min</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',unsafe_allow_html=True)
    html='<div class="route-grid">'
    for i,((_,title),(short,desc)) in enumerate(zip(STAGES[1:],ROUTE_SUMMARIES),1):
        html+=f'<div class="route-card"><span class="step">{i}</span><div><b>{title}</b><p>{desc}</p><span class="route-time">⏱️ {STAGE_MINUTES[i]} min</span></div></div>'
        if i==BREAK_AFTER_STAGE:
            html+=f'<div class="break-card"><span class="step">☕</span><div><b>Pausa pedagógica</b><p>Descanso antes del bloque de fundamentos físicos.</p><span class="route-time">⏱️ {BREAK_MINUTES} min</span></div></div>'
    st.markdown(html+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> concepto visual → explicación técnica → ejemplo → interacción → interpretación → ejercicio → retroalimentación.</div>',unsafe_allow_html=True)

def stage1():
    header("ETAPA 1 · MATERIA + LABORATORIO","Control del ruido: fuente, trayectoria y receptor",
           "Antes de elegir un material hay que localizar dónde nace el ruido, cómo se propaga y a quién afecta.")
    full_matter(1)
    lesson("Modelo de control","Fuente: genera la energía. Trayectoria: medio y vías de propagación. Receptor: persona, actividad o recinto afectado. Una solución robusta puede combinar los tres.")
    st.markdown('<div class="section-band"><span>🎛️</span><h3>Laboratorio visual: interviene la escena</h3></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    source=c1.selectbox("🏭 En la fuente",["Sin intervención","Encerrar la fuente","Soportes antivibratorios","Equipo de menor emisión"])
    path=c2.selectbox("〰️ En la trayectoria",["Sin intervención","Barrera acústica"])
    receiver=c3.selectbox("👤 En el receptor",["Sin intervención","Protección auditiva","Cabina acústica","Mejorar fachada"])
    distance=st.select_slider(
        "📏 Separación física entre la fuente y el receptor",
        options=["Distancia inicial","Distancia aumentada"],
        help="La distancia no es una barrera ni una intervención en la trayectoria: es una condición geométrica del problema.",
    )
    gains={"Sin intervención":0,"Encerrar la fuente":10,"Soportes antivibratorios":5,"Equipo de menor emisión":12,
           "Barrera acústica":12,
           "Protección auditiva":10,"Cabina acústica":15,"Mejorar fachada":11}
    distance_gain=5 if distance=="Distancia aumentada" else 0
    total=gains[source]+gains[path]+gains[receiver]+distance_gain
    enclosure='<div class="machine-box"></div>' if source=="Encerrar la fuente" else ""
    mounts='<div class="mounts">▰ ▰</div>' if source=="Soportes antivibratorios" else ""
    barrier='<div class="barrier"></div>' if path=="Barrera acústica" else ""
    cabin='<div class="receiver-cabin"></div>' if receiver=="Cabina acústica" else ""
    facade='<div class="receiver-facade"></div>' if receiver=="Mejorar fachada" else ""
    phones='<div class="headphones">🎧</div>' if receiver=="Protección auditiva" else ""
    wave_count=max(1,6-round(total/7))
    waves=")"*wave_count
    distance_class=" distance-on" if distance=="Distancia aumentada" else ""
    distance_label="Fuente y receptor más separados" if distance=="Distancia aumentada" else "Distancia inicial"
    st.markdown(
        f'<div class="scene-pro{distance_class}"><div class="scene-caption">Nivel visual estimado: {85-total} dB</div>'
        f'{enclosure}{mounts}<div class="machine">⚙️</div><div class="waves">))) {waves}</div>{barrier}'
        f'{cabin}{facade}{phones}<div class="person">🧑</div><div class="distance-label">↔ {distance_label}</div></div>',
        unsafe_allow_html=True,
    )
    a,b,c=st.columns(3);a.metric("Nivel inicial","85 dB");b.metric("Reducción estimada",f"{total} dB");c.metric("Nivel resultante",f"{85-total} dB")
    st.markdown('<div class="warn">Las reducciones se suman aquí con fines didácticos. En un proyecto real deben evaluarse por bandas, vías dominantes y condiciones de montaje.</div>',unsafe_allow_html=True)
    check("e1","Una máquina afecta una oficina contigua. ¿Dónde actúa el muro separador?",["Fuente","Trayectoria","Receptor"],"Trayectoria","El muro se interpone en el camino de propagación.")

def stage2():
    header("ETAPA 2 · LABORATORIO DE DOS RECINTOS","Aislamiento no es absorción",
           "Cambia el panel separador y acondiciona el recinto receptor para observar qué magnitud modifica cada decisión.")
    full_matter(2)
    lesson("Aislamiento acústico","Reduce la energía que atraviesa un elemento entre recintos. Se mejora con masa, estanqueidad, desacoplamiento y control de vías indirectas.")
    lesson("Absorción acústica","Reduce reflexiones dentro del mismo recinto. Se expresa mediante α entre 0 y 1 y modifica reverberación e inteligibilidad.")
    st.markdown('<div class="section-band"><span>🧪</span><h3>Ejemplo didáctico: recinto emisor → panel → recinto receptor</h3></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    panel=c1.selectbox(
        "🧱 Panel separador",
        ["Panel liviano simple","Muro de albañilería","Tabique doble desacoplado"],
        help="Este control modifica la transmisión entre los dos recintos.",
    )
    material=c2.selectbox(
        "🟦 Material absorbente en el receptor",
        ["Sin tratamiento","Panel poroso α = 0,40","Lana mineral revestida α = 0,75","Panel de alto desempeño α = 0,90"],
        help="Este material controla las reflexiones dentro del recinto receptor.",
    )
    area=c3.slider("📐 Superficie absorbente instalada (m²)",0,60,0,5)

    panel_data={
        "Panel liviano simple":(30,"light"),
        "Muro de albañilería":(45,"masonry"),
        "Tabique doble desacoplado":(55,"double"),
    }
    alpha_data={
        "Sin tratamiento":0.0,
        "Panel poroso α = 0,40":0.40,
        "Lana mineral revestida α = 0,75":0.75,
        "Panel de alto desempeño α = 0,90":0.90,
    }
    R,panel_class=panel_data[panel]
    alpha=alpha_data[material]
    V=120.0
    A0=18.0
    A=A0+alpha*area
    T0=.161*V/A0
    T=.161*V/A
    source_level=85.0
    # Relación didáctica: el campo reverberante del receptor disminuye al
    # aumentar A, aunque la propiedad aislante R del panel permanece igual.
    room_correction=10*math.log10(A/A0) if A>A0 else 0.0
    receiver_level=source_level-R-room_correction
    absorber_count=0 if area==0 or alpha==0 else min(4,max(1,math.ceil(area/15)))
    absorber_html="".join(
        f'<div class="absorber {"ceiling" if i==3 else f"a{i+1}"}"></div>'
        for i in range(absorber_count)
    )
    echo_count=max(0,3-round((A-A0)/18))
    echoes="".join(f'<div class="echo-wave e{i+1}">↝ ↝</div>' for i in range(echo_count))
    wave_strength=max(1,min(5,round((60-R)/7)))
    transmitted=")"*wave_strength
    st.markdown(
        f'<div class="two-room-lab">'
        f'<div class="lab-room"><div class="room-name">RECINTO EMISOR · 85 dB</div>'
        f'<div class="speaker-visual">🔊</div><div class="incident-wave">))) )))</div></div>'
        f'<div class="lab-panel {panel_class}">{panel}<br>R = {R} dB</div>'
        f'<div class="lab-room receiver"><div class="room-name">RECINTO RECEPTOR</div>'
        f'{absorber_html}{echoes}<div class="transmitted-wave">{transmitted}</div>'
        f'<div class="listener-visual">🧑‍💻</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="concept-grid">'
        f'<div class="concept-result">🧱<b>{R:.0f} dB</b><span>Aislamiento R del panel<br><strong>No cambia por agregar absorbentes</strong></span></div>'
        f'<div class="concept-result">🟦<b>{A:.1f} m² sabin</b><span>Absorción equivalente del receptor<br>Inicial: {A0:.1f} m² sabin</span></div>'
        f'<div class="concept-result">⏱️<b>{T:.2f} s</b><span>T₆₀ del recinto receptor<br>Inicial: {T0:.2f} s</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    a,b,c=st.columns(3)
    a.metric("Nivel estimado en el receptor",f"{receiver_level:.1f} dB")
    b.metric("Cambio de T₆₀",f"{T-T0:+.2f} s")
    c.metric("Cambio del aislamiento R","0 dB" if material!="Sin tratamiento" else "Sin tratamiento")
    st.markdown(
        '<div class="good"><b>Interpretación:</b> cambiar el panel separador modifica el aislamiento entre recintos. '
        'Agregar material absorbente en el receptor aumenta su absorción equivalente, reduce las reflexiones y disminuye '
        'el T₆₀. El nivel medido en el receptor puede bajar por la menor reverberación, pero el valor R propio del panel no aumenta.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>📐</span><h3>Laboratorio visual: absorción equivalente y ecuación de Sabine</h3></div>',unsafe_allow_html=True)
    formula_card("Absorción equivalente y ecuación de Sabine",
                 r"A=\sum_i S_i\alpha_i \qquad T_{60}=0{,}161\,\frac{V}{A}",
                 "<b>S</b>: superficie (m²)<br><b>α</b>: coeficiente de absorción<br><b>V</b>: volumen (m³)<br><b>A</b>: absorción equivalente (m² sabin)",
                 "Para estimar el tiempo de reverberación en un recinto de campo aproximadamente difuso.")
    c1,c2,c3=st.columns(3)
    sabine_v=c1.number_input("Volumen (m³)",50,1000,220,key="e2_sabine_v")
    sabine_base=c2.number_input("Absorción inicial (m² sabin)",5.,200.,28.,key="e2_sabine_base")
    sabine_area=c3.number_input("Área nueva (m²)",0.,300.,55.,key="e2_sabine_area")
    sabine_alpha=st.select_slider(
        "α del material en 500 Hz",
        options=[0.05,.10,.20,.35,.50,.65,.80,.95],
        value=.80,
        key="e2_sabine_alpha",
    )
    sabine_a=sabine_base+sabine_area*sabine_alpha
    sabine_t=.161*sabine_v/sabine_a
    sabine_t0=.161*sabine_v/sabine_base
    a,b,c=st.columns(3)
    a.metric("A nueva",f"{sabine_a:.1f} m² sabin")
    b.metric("T₆₀ inicial",f"{sabine_t0:.2f} s")
    c.metric("T₆₀ final",f"{sabine_t:.2f} s",delta=f"{sabine_t-sabine_t0:+.2f} s")
    if sabine_t<=.8:
        st.success("Condición didáctica favorable para habla: decaimiento rápido y mejor claridad.")
    elif sabine_t<=1.2:
        st.warning("Condición intermedia. Puede requerir más absorción según volumen y uso.")
    else:
        st.error("Reverberación alta para una actividad centrada en la palabra.")
    check(
        "e2_sabine_check",
        "Si el volumen se mantiene y se duplica A, ¿qué ocurre con T₆₀?",
        ["Se duplica","Se reduce aproximadamente a la mitad","No cambia"],
        "Se reduce aproximadamente a la mitad",
        "Sabine muestra una relación inversa entre T₆₀ y A.",
    )
    check(
        "e2_lab_1",
        "Si mantienes el mismo panel y agregas material absorbente en el recinto receptor, ¿qué cambia principalmente?",
        ["Aumenta el aislamiento R del panel","Aumenta la absorción y disminuye el T₆₀","Aumenta la transmisión por el panel"],
        "Aumenta la absorción y disminuye el T₆₀",
        "El absorbente actúa sobre las reflexiones del recinto receptor. No modifica por sí solo la propiedad aislante del panel.",
    )
    check(
        "e2_lab_2",
        "¿Qué intervención permite reducir directamente la energía que atraviesa desde el recinto emisor?",
        ["Cambiar por un panel separador de mayor aislamiento","Agregar paneles absorbentes al receptor","Reducir únicamente el T₆₀ del receptor"],
        "Cambiar por un panel separador de mayor aislamiento",
        "La transmisión entre recintos se controla mejorando la separación: masa, estanqueidad, desacoplamiento y vías laterales.",
    )

def stage3():
    header("ETAPA 3 · PREGUNTAS DE APLICACIÓN","Aislamiento, absorción y acondicionamiento acústico",
           "Responde las cinco situaciones, comprueba tu razonamiento y revisa la aclaración correspondiente.")
    st.markdown('<div class="section-band"><span>✍️</span><h3>Aplicación conceptual · responde y comprueba</h3></div>',unsafe_allow_html=True)
    questions=[
      ("s3q1","En una sala de reuniones se instalan paneles acústicos de espuma en todas las paredes. ¿Este tratamiento mejora el aislamiento acústico entre salas contiguas? Justifica tu respuesta.",
       "No de forma significativa. La espuma es principalmente absorbente: reduce reflexiones y reverberación dentro de la sala, pero su baja masa no impide eficazmente la transmisión. Para aislar se debe mejorar el cerramiento mediante masa, estanqueidad, desacoplamiento y control de fugas y flancos.",
       [["no","no mejora"],["absor","reverber"],["masa","estanque","desacopl","cerramiento"]],"Diferencia el control de reflexiones interiores del control de transmisión entre recintos."),
      ("s3q2","Se requiere reducir el eco en una oficina sin afectar la transmisión de sonido hacia otros recintos. ¿Qué tipo de tratamiento acústico se debe aplicar y por qué?",
       "Se debe aplicar acondicionamiento absorbente interior —paneles, cielo acústico o bafles— para aumentar la absorción equivalente y reducir el T₆₀. El objetivo es controlar reflexiones dentro de la oficina, no modificar el aislamiento del cerramiento.",
       [["absor","acondicion"],["eco","reflex","reverber"],["t60","tiempo de reverberación"]],"La intervención buscada actúa dentro del mismo recinto y no sobre el sonido que atraviesa la separación."),
      ("s3q3","Una persona sigue escuchando a sus vecinos a pesar de instalar paneles acústicos de espuma en su muro. ¿Cuál es el error común en la solución adoptada?",
       "El error es confundir absorción con aislamiento. La espuma puede reducir reflexiones en la habitación, pero no aporta suficiente masa ni desacoplamiento. Deben revisarse muro, puertas, ventanas, juntas, enchufes y transmisiones laterales.",
       [["confund","absorción","absorcion"],["aislamiento","transmisión","transmision"],["masa","desacopl","sell","fuga","flanco"]],"Explica por qué un material absorbente no se transforma automáticamente en un buen aislante."),
      ("s3q4","Un gimnasio necesita reducir el ruido percibido en oficinas contiguas. ¿Se deben usar materiales absorbentes o aislantes? Propón una solución adecuada.",
       "Se requieren principalmente soluciones aislantes y de control vibratorio: piso resiliente o flotante, soportes antivibratorios, cerramientos dobles desacoplados, mayor masa y sellado. Los absorbentes pueden complementar reduciendo la reverberación del gimnasio, pero no sustituyen el aislamiento.",
       [["aisl","transmis"],["vibr","piso flotante","soporte"],["doble","masa","sell","desacopl"]],"Distingue el ruido aéreo de los impactos y vibraciones que pueden viajar por la estructura."),
      ("s3q5","Se diseñan dos salas de clases. Una usa paneles absorbentes en el techo y la otra usa muros dobles entre salas. ¿Cuál solución afecta más la inteligibilidad del habla dentro de la sala y cuál mejora el aislamiento entre ellas?",
       "Los paneles absorbentes del techo reducen el T₆₀ y mejoran principalmente la inteligibilidad dentro del aula. Los muros dobles desacoplados reducen la transmisión y mejoran principalmente el aislamiento entre las salas.",
       [["panel","techo","absorb"],["intelig","reverber"],["muro doble","aislamiento","transmis"]],"Asocia cada solución con el lugar donde aparece su beneficio: dentro de la sala o al otro lado de la separación."),
    ]
    solutions={}
    for key,q,solution,groups,note in questions:
        formative_development(3,key,q,solution,groups,note); solutions[key]=solution
    score_counter(3)
    teacher_group_review(3,solutions)

def stage4():
    header("ETAPA 4 · MATERIA + MODELO","Aislamiento acústico y costo-beneficio",
           "La mejor solución no es la de mayor número ni la más barata: es la que cumple la meta con un costo justificable.")
    full_matter(4)
    lesson("Orden correcto de decisión","1) definir meta y espectro; 2) descartar lo que no cumple; 3) comparar costo del ciclo, vida útil, riesgo, ROI y recuperación; 4) revisar margen de seguridad.")
    formula_card("Del beneficio anual bruto al flujo neto anual",
                 r"F_{\mathrm{neto,anual}}=B_{\mathrm{bruto,anual}}-C_{\mathrm{recurrente,anual}}",
                 "<b>F<sub>neto</sub></b>: flujo anual neto ($/año)<br>"
                 "<b>B<sub>bruto</sub></b>: ahorro o ganancia total que produce la solución durante un año, antes de descontar gastos ($/año)<br>"
                 "<b>C<sub>recurrente</sub></b>: operación, inspección y mantención que se repiten cada año ($/año)",
                 "Para evitar ambigüedad, la aplicación no usa «beneficio anual neto» como un concepto separado: el dinero que queda después de descontar costos se llama flujo neto anual.")
    st.markdown(
        '<div class="worked-example"><h3>Dos cantidades diferentes</h3>'
        '<div class="worked-step"><strong>1 · Beneficio anual bruto.</strong> Es todo el ahorro o ganancia generado durante un año, antes de descontar gastos. '
        'Se suman los ingresos atribuibles a la solución y los costos que permite evitar: '
        'multas, paralizaciones, reclamos, pérdida de productividad, arriendos temporales o reparaciones repetidas.</div>'
        '<div class="worked-step"><strong>2 · Costos recurrentes anuales.</strong> Son los gastos que se repiten cada año: '
        'mantención, inspecciones, reposición de sellos, energía adicional u operación. La inversión inicial se analiza por separado.</div>'
        '<div class="worked-step"><strong>3 · Flujo neto anual.</strong> Es el dinero que realmente queda disponible cada año. '
        'Si el beneficio bruto es $700.000 y los costos recurrentes son $100.000, entonces '
        '$700.000 − $100.000 = <b>$600.000/año</b>.</div>'
        '<div class="worked-result"><b>Lectura del resultado:</b> un flujo positivo aporta recursos para recuperar la inversión; '
        'un flujo igual a cero no la recupera; y uno negativo significa que los costos anuales superan los beneficios anuales. '
        'El payback se calcula dividiendo la inversión inicial por este flujo positivo.</div></div>',
        unsafe_allow_html=True,
    )
    formula_card("Payback · tiempo para recuperar la inversión",
                 r"Payback=\frac{I_0}{F_{\mathrm{neto,anual}}}",
                 "<b>I₀</b>: inversión inicial ($)<br><b>F<sub>neto,anual</sub></b>: beneficio anual bruto menos costos recurrentes ($/año)",
                 "Responde una pregunta concreta: ¿cuántos años tardaré en recuperar el dinero invertido? Un payback menor significa recuperación más rápida, pero no informa cuánto se gana después.")
    formula_card("ROI · rentabilidad de la inversión",
                 r"ROI=\frac{B_{\mathrm{acumulado}}-C_{\mathrm{total}}}{C_{\mathrm{total}}}\,100",
                 "<b>B acumulado</b>: beneficios obtenidos durante el período analizado ($)<br><b>C total</b>: inversión inicial más todos los costos del mismo período ($)",
                 "Responde: ¿cuánto gané o perdí, en porcentaje, respecto de todo lo que costó la inversión? ROI positivo = ganancia; 0 % = solo se recuperaron los costos; negativo = pérdida.")
    st.markdown(
        '<div class="worked-example"><h3>Ejemplo resuelto · ¿Qué significan ROI y payback?</h3>'
        '<div class="worked-step"><strong>1 · Verificación técnica.</strong> Un encapsulamiento cuesta $2.000.000 y cumple la meta acústica. '
        'Recién ahora corresponde analizar su economía.</div>'
        '<div class="worked-step"><strong>2 · Flujo neto anual.</strong> El beneficio anual bruto es $700.000 y la mantención recurrente es $100.000. '
        'Flujo neto anual = $700.000 − $100.000 = <b>$600.000/año</b>.</div>'
        '<div class="worked-step"><strong>3 · Payback.</strong> $2.000.000 ÷ $600.000/año = <b>3,33 años</b>. '
        'Significa que al cabo de aproximadamente 3 años y 4 meses se recupera la inversión inicial.</div>'
        '<div class="worked-step"><strong>4 · ROI a 5 años.</strong> Beneficio acumulado = $700.000 × 5 = $3.500.000. '
        'Costo total = $2.000.000 + ($100.000 × 5) = $2.500.000. '
        'ROI = ($3.500.000 − $2.500.000) ÷ $2.500.000 × 100 = <b>40 %</b>.</div>'
        '<div class="worked-result">Interpretación: al terminar los 5 años, el proyecto recuperó todos sus costos y generó un beneficio neto equivalente al 40 % del costo total. '
        'El ROI no indica cuándo se recuperó el dinero; ese dato lo entrega el payback.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Ejemplos para interpretar los indicadores")
    st.caption("Selecciona una respuesta en cada situación. Los datos son fijos para concentrar la actividad en la interpretación.")
    check(
        "e4_flow",
        "Una solución evita costos por $900.000 al año y requiere $150.000 anuales de mantención. ¿Cuál es su flujo anual neto?",
        ["$750.000/año","$900.000/año","$1.050.000/año","$150.000/año"],
        "$750.000/año",
        "Fneto = Ba − Ca = $900.000 − $150.000 = $750.000 por año.",
    )
    check(
        "e4_payback",
        "Una medida cuesta $2.400.000 y genera un flujo anual neto de $600.000. ¿Cuál es su payback?",
        ["2 años","4 años","6 años","40 %"],
        "4 años",
        "Payback = I₀/Fneto = $2.400.000/$600.000 por año = 4 años.",
    )
    check(
        "e4_roi",
        "En cinco años, una solución acumula beneficios por $4.500.000 y costos totales por $3.000.000. ¿Cuál es su ROI?",
        ["33,3 %","50 %","66,7 %","150 %"],
        "50 %",
        "ROI = (B−C)/C×100 = ($4.500.000−$3.000.000)/$3.000.000×100 = 50 %.",
    )
    check(
        "e4_decision",
        "La alternativa A tiene ROI de 70 %, pero alcanza 36 dB. La alternativa B tiene ROI de 35 % y alcanza la meta de 40 dB. ¿Cuál puede recomendarse?",
        ["Alternativa A, porque tiene mayor ROI","Alternativa B, porque primero cumple la meta","Promediar dB y ROI","Ninguna, porque el ROI debe superar 50 %"],
        "Alternativa B, porque primero cumple la meta",
        "La suficiencia acústica es el filtro inicial. La rentabilidad solo permite comparar alternativas técnicamente suficientes.",
    )

def stage5():
    header("ETAPA 5 · APLICACIÓN CONCEPTUAL","Decisión técnico-económica",
           "Compara alternativas, filtra por suficiencia acústica y encuentra el mejor compromiso.")
    full_matter(5)
    st.markdown(
        '<div class="question-box"><div class="question-label">CASO DE DECISIÓN</div>'
        '<div class="question-text">¿Cuál de las tres soluciones recomendarías para cumplir el objetivo acústico '
        'con el menor costo del ciclo? Revisa la meta fija y los datos de cada alternativa; luego justifica por qué '
        'tu elección es técnicamente suficiente antes de compararla económicamente.</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Instrucción: la meta y todos los datos son fijos. Analiza la tabla, descarta las soluciones que no cumplen y presenta tu recomendación sin modificar valores.")
    target=38
    st.info("Objetivo acústico mínimo del caso: **38 dB**")
    fixed=[
        ["Solución A",32,1200000,2640000,7200000,172.7,1.7],
        ["Solución B",40,1900000,4540000,13800000,204.0,2.0],
        ["Solución C",47,3200000,7100000,18750000,164.1,3.2],
    ]
    df=pd.DataFrame(fixed,columns=["Solución","Aislamiento","Inversión","Costo ciclo","Beneficio acumulado","ROI","Payback"])
    df["Cumple"]=df["Aislamiento"]>=target
    st.dataframe(df.style.format({"Inversión":"${:,.0f}","Costo ciclo":"${:,.0f}","Beneficio acumulado":"${:,.0f}","ROI":"{:.1f}%","Payback":"{:.1f} años"}),use_container_width=True,hide_index=True)
    feasible=df[df.Cumple]
    if feasible.empty: st.error("Ninguna alternativa cumple. No corresponde recomendar por precio o ROI.")
    else:
        best=feasible.loc[feasible["Costo ciclo"].idxmin()]
        st.success(f'Entre las alternativas suficientes, {best["Solución"]} tiene el menor costo del ciclo. La decisión final debe revisar además bandas críticas, montaje y riesgo.')
    recommendation=st.radio(
        "Selecciona la solución que recomendarías",
        ["Solución A","Solución B","Solución C"],
        index=None,
        key="s5_table_recommendation",
        horizontal=True,
    )
    justification=st.text_area(
        "Justifica tu decisión utilizando cumplimiento acústico y costo del ciclo",
        key="s5_table_justification",
        placeholder="Ejemplo: descarto… porque no cumple; entre las que cumplen selecciono… porque…",
    )
    if st.button("Comprobar decisión",key="b_s5_table_decision"):
        if recommendation is None:
            st.warning("Selecciona una solución antes de comprobar.")
        elif feasible.empty:
            st.error("Ninguna solución cumple la meta seleccionada. La decisión correcta es rediseñar las alternativas antes de recomendar una.")
        elif recommendation!=best["Solución"]:
            st.error(f'La recomendación no es la óptima con estos datos. Primero descarta las alternativas que no cumplen y, entre las suficientes, compara el costo del ciclo. La respuesta esperada es {best["Solución"]}.')
        elif len(justification.strip())<20:
            st.warning(f'{best["Solución"]} es la alternativa esperada, pero falta desarrollar la justificación técnica y económica.')
        else:
            st.success(f'Correcto. {best["Solución"]} cumple el objetivo y presenta el menor costo del ciclo entre las alternativas suficientes.')
    check("e5","Una alternativa tiene excelente ROI, pero no alcanza la meta acústica. ¿Qué corresponde?",["Elegirla por su ROI","Descartarla o rediseñarla antes de comparar economía","Promediar ROI y dB"],"Descartarla o rediseñarla antes de comparar economía","La suficiencia técnica precede a la optimización económica.")
    st.markdown('<div class="section-band"><span>🧮</span><h3>Aplicación técnico-económica · responde y comprueba</h3></div>',unsafe_allow_html=True)
    q1="Un ingeniero propone aumentar el aislamiento de una oficina de 40 dB a 50 dB. ¿Qué elementos debería considerar para decidir si esto es una buena inversión?"
    s1="Debe comprobar el nivel actual y la meta, privacidad y uso, espectro de la fuente, cumplimiento, beneficio real de 10 dB, costo del ciclo, factibilidad, puertas, ventanas, juntas y flancos, vida útil, riesgo y rendimiento decreciente. «Más dB» no basta si la mejora no es necesaria o no puede lograrse en obra."
    formative_development(5,"s5q1",q1,s1,[["meta","objetivo","norma"],["costo","inversión","inversion"],["puerta","ventana","fuga","flanco"],["beneficio","privacidad","confort"],["factib","vida útil","vida util","riesgo"]],"La decisión debe integrar suficiencia acústica, vías dominantes, costo completo y beneficio útil.")
    q2="Un sistema cuesta $1.200.000 CLP y reduce 30 dB. Otro cuesta $2.400.000 CLP y reduce 38 dB. Calcula el costo por dB de ambos e indica cuál ofrece mayor eficiencia."
    s2="Sistema 1: $1.200.000/30 = **$40.000 por dB**. Sistema 2: $2.400.000/38 = **$63.158 por dB** aproximadamente. El sistema 1 es más eficiente por este indicador, siempre que alcance la meta acústica."
    formative_numeric(5,"s5q2",q2,[("a","Sistema 1 · CLP/dB",0.0,1000.0),("b","Sistema 2 · CLP/dB",0.0,1000.0)],
        lambda v:(abs(v["a"]-40000)<=500 and abs(v["b"]-63157.9)<=600,"Los valores esperados son $40.000/dB y aproximadamente $63.158/dB; el menor costo por dB corresponde al sistema 1."),s2)
    q3="Opción A: inversión $500.000, beneficio $700.000. Opción B: inversión $1.000.000, beneficio $950.000. Calcula el ROI de ambas e identifica la mejor."
    s3="ROI A = ($700.000−$500.000)/$500.000×100 = **40 %**. ROI B = ($950.000−$1.000.000)/$1.000.000×100 = **−5 %**. La opción A tiene el mejor retorno."
    formative_numeric(5,"s5q3",q3,[("a","ROI A (%)",0.0,1.0),("b","ROI B (%)",0.0,1.0)],
        lambda v:(abs(v["a"]-40)<=0.2 and abs(v["b"]+5)<=0.2,"Se esperaba ROI A = 40 % y ROI B = −5 %. La alternativa A ofrece el mejor retorno."),s3)
    score_counter(5)
    teacher_group_review(5,{"s5q1":s1,"s5q2":s2,"s5q3":s3})

def stage6():
    header("ETAPA 6 · MATERIA + SIMULADORES","Fundamentos físicos del aislamiento acústico",
           "Modelos físicos de placas simples, Sharp, resonancia y ventanas dobles mediante Quirt.")
    full_matter(6)
    tabs=st.tabs(["Transmisión y R","Ley de masa","Coincidencia","Sharp · panel doble","Quirt · ventanas","Elementos compuestos"])
    with tabs[0]:
        formula_card("Coeficiente de transmisión y reducción sonora",
                     r"\tau=\frac{W_t}{W_i} \qquad R=10\log_{10}\left(\frac{1}{\tau}\right)",
                     "<b>Wₜ</b>: potencia transmitida (W)<br><b>Wᵢ</b>: potencia incidente (W)<br><b>τ</b>: fracción transmitida<br><b>R</b>: reducción sonora (dB)",
                     "Para relacionar físicamente la energía que atraviesa una separación con su aislamiento por banda.")
        formula_card("Despeje directo del coeficiente de transmisión",
                     r"\tau=10^{-R/10}",
                     "<b>R</b>: reducción sonora (dB)<br><b>τ</b>: fracción adimensional entre 0 y 1",
                     "Para conocer qué fracción de la energía atraviesa un elemento cuando se dispone de R.")
        R=st.slider("R (dB)",10,70,40,key="r6"); t=10**(-R/10)
        st.metric("Fracción de energía transmitida",f"{t:.8f} ({t*100:.6f} %)")
        st.markdown(
            f'<div class="worked-example"><h3>¿De dónde sale el porcentaje?</h3>'
            f'<div class="worked-step"><strong>1.</strong> La ecuación entrega una fracción decimal: '
            f'τ = 10<sup>−{R}/10</sup> = {t:.8f}.</div>'
            f'<div class="worked-step"><strong>2.</strong> Para expresarla como porcentaje se multiplica por 100: '
            f'{t:.8f} × 100 = <b>{t*100:.6f} %</b>.</div>'
            f'<div class="worked-result">Este porcentaje corresponde a energía transmitida, no a porcentaje de superficie.</div></div>',
            unsafe_allow_html=True,
        )
        st.info("Ejemplo: R = 40 dB → τ = 10⁻⁴ = 0,0001. Solo se transmite 0,01 % de la energía incidente.")
        check("e6_tau_practical","Si R = 30 dB, ¿qué porcentaje de energía se transmite?",
              ["0,001 %","0,01 %","0,1 %","3 %"],"0,1 %",
              "τ = 10⁻³ = 0,001; al multiplicar por 100 se obtiene 0,1 %.")
    with tabs[1]:
        formula_card("Ley de masa ideal para una hoja simple",
                     r"R\approx20\log_{10}(m'f)-47",
                     "<b>m′</b>: masa superficial (kg/m²)<br><b>f</b>: frecuencia (Hz)<br><b>R</b>: reducción sonora (dB)",
                     "Aproximación de campo difuso en la región controlada por masa, lejos de resonancias, coincidencia, fugas y flancos.")
        m=st.slider("Masa superficial m′ (kg/m²)",5,150,25)
        curve=mass_r(m,FREQS); curve2=mass_r(2*m,FREQS)
        line_chart(FREQS,[("m′",curve),("2·m′",curve2)],"Ley de masa ideal","R (dB)")
        st.info("Duplicar masa o frecuencia aumenta aproximadamente 6 dB en la región ideal de ley de masa.")
    with tabs[2]:
        formula_card("Frecuencia crítica de una placa",
                     r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}\qquad D=\frac{Eh^3}{12(1-\nu^2)}",
                     "<b>c</b>: velocidad del sonido (m/s)<br><b>m′</b>: masa superficial (kg/m²)<br><b>D</b>: rigidez flexional (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor (m)<br><b>ν</b>: coeficiente de Poisson",
                     "Para estimar la banda donde la coincidencia puede producir una caída del aislamiento de una placa homogénea.")
        fc=st.slider("Frecuencia crítica estimada (Hz)",100,3150,800)
        ideal=mass_r(25,FREQS); dip=ideal-12*np.exp(-.5*(np.log(FREQS/fc)/.24)**2)
        line_chart(FREQS,[("Ley de masa ideal",ideal),("Con coincidencia",dip)],"Efecto didáctico de coincidencia","R (dB)")
        st.warning("Cerca de fᶜ el panel radia con mayor eficiencia y puede aparecer una caída de aislamiento.")
    with tabs[3]:
        st.markdown("#### Panel doble con cavidad absorbente · método de Sharp")
        formula_card(
            "Resonancia masa-aire-masa",
            r"f_0\approx60\sqrt{\frac{1/m_1+1/m_2}{d}}",
            "<b>m₁, m₂</b>: masas superficiales de las hojas (kg/m²)<br>"
            "<b>d</b>: separación entre hojas (m)<br><b>f₀</b>: frecuencia de resonancia (Hz)",
            "Para identificar el valle de baja frecuencia antes de interpretar la mejora del sistema doble.",
        )
        gap=st.slider("Cámara (mm)",20,300,80); absorb=st.checkbox("Absorbente en cámara",True)
        m1=st.slider("Masa hoja 1 (kg/m²)",5,80,20,key="sharp_m1")
        m2=st.slider("Masa hoja 2 (kg/m²)",5,80,20,key="sharp_m2")
        f0=60*math.sqrt((1/m1+1/m2)/(gap/1000))
        gain=8+min(gap/30,8)+(5 if absorb else 0)
        c1,c2=st.columns(2)
        c1.metric("f₀ aproximada",f"{f0:.0f} Hz")
        c2.metric("Mejora didáctica sobre hoja simple",f"{gain:.1f} dB")
        st.caption("Sharp es apropiado para paneles dobles cuya cavidad contiene absorbente. El desempeño depende además de conexiones de línea, separación de montantes, frecuencias críticas y puentes estructurales.")
    with tabs[4]:
        st.markdown("#### Ventana doble · modelo de Quirt de tu tesis")
        st.info(
            "Una ventana doble no se trata como un tabique con lana mineral. Su cavidad no está rellena y "
            "los modos interiores dependen también de la altura y el ancho del marco."
        )
        formula_card(
            "Frecuencia de resonancia f₁ · ecuación 2.28",
            r"f_1=\frac{1}{2\pi}\sqrt{\frac{(\rho_{s1}+\rho_{s2})\rho_0c^2}{d\,\rho_{s1}\rho_{s2}}}",
            "<b>ρs₁, ρs₂</b>: masa superficial de cada vidrio (kg/m²)<br>"
            "<b>ρ₀</b>: densidad del aire (kg/m³)<br><b>c</b>: velocidad del sonido (m/s)<br>"
            "<b>d</b>: cámara entre vidrios (m)",
            "Separa los dos regímenes del modelo de ventana doble.",
        )
        formula_card(
            "Régimen superior de la ventana doble",
            r"TL=TL_{\rho s1}+TL_{\rho s2}+10\log_{10}\alpha+10\log_{10}d+"
            r"10\log_{10}\left(\frac{h+w}{hw}\right)+3",
            "<b>α</b>: absorción a incidencia aleatoria del perímetro<br>"
            "<b>h, w</b>: alto y ancho de la cavidad (m)<br>"
            "<b>TLρs₁, TLρs₂</b>: pérdida de cada vidrio por banda",
            "Sobre f₁, la cavidad se considera un espacio reverberante. Bajo f₁ se usa una placa equivalente con la suma de masas.",
        )
        q1,q2,q3=st.columns(3)
        glass1=q1.number_input("Vidrio 1 (mm)",2.0,12.0,3.0,.5,key="quirt_g1")
        glass2=q2.number_input("Vidrio 2 (mm)",2.0,12.0,3.0,.5,key="quirt_g2")
        q3.number_input("Densidad vidrio (kg/m³)",2000.,2800.,2500.,50.,key="quirt_density",disabled=True)
        q4,q5,q6=st.columns(3)
        gap_mm=q4.number_input("Cámara d (mm)",4.0,100.0,6.0,1.0,key="quirt_gap")
        height=q5.number_input("Alto h (m)",.30,4.00,1.75,.05,key="quirt_h")
        width=q6.number_input("Ancho w (m)",.30,4.00,.62,.05,key="quirt_w")
        alpha=st.slider("Absorción perimetral α",.02,.30,.10,.01,key="quirt_alpha")
        density=2500.0
        qm1=density*glass1/1000
        qm2=density*glass2/1000
        curve,f1=quirt_window_curve(qm1,qm2,gap_mm/1000,height,width,alpha)
        base=mass_r(qm1+qm2,FREQS)
        c1,c2,c3=st.columns(3)
        c1.metric("Masa vidrio 1",f"{qm1:.1f} kg/m²")
        c2.metric("Masa vidrio 2",f"{qm2:.1f} kg/m²")
        c3.metric("Resonancia f₁",f"{f1:.0f} Hz")
        line_chart(
            FREQS,
            [("Ventana doble · Quirt",curve),("Placa equivalente bajo f₁",base)],
            f"Predicción didáctica {glass1:g}({gap_mm:g}){glass2:g}",
            "TL (dB)",
        )
        st.markdown(
            '<div class="good"><b>Lectura del modelo:</b> bajo f₁ las dos hojas se estiman como una placa '
            'con la suma de masas. Sobre f₁ intervienen cada vidrio, la cámara, el perímetro y las dimensiones '
            'del marco. El análisis debe entregar además Rw, C y Ctr mediante ISO 717-1.</div>',
            unsafe_allow_html=True,
        )
        check(
            "e6_quirt",
            "¿Por qué no corresponde aplicar sin cambios el método de Sharp a una ventana doble?",
            [
                "Porque la cavidad de la ventana no lleva absorbente y sus modos dependen también del marco",
                "Porque el vidrio no posee masa superficial",
                "Porque las ventanas solo se evalúan con absorción Sabine",
            ],
            "Porque la cavidad de la ventana no lleva absorbente y sus modos dependen también del marco",
            "Tu tesis adopta Quirt para representar la cavidad sin absorbente y la influencia de h y w.",
        )
    with tabs[5]:
        formula_card("Aislamiento de elementos compuestos",
                     r"\tau_{\mathrm{total}}=\frac{\sum_i S_i\tau_i}{\sum_i S_i}\qquad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
                     "<b>Sᵢ</b>: área del elemento i (m²)<br><b>τᵢ=10^{-Rᵢ/10}</b>: coeficiente de transmisión de cada elemento",
                     "Para combinar un muro con puertas, ventanas u otros componentes. Los aislamientos en dB no se promedian.")
        st.markdown("#### Aplicación práctica · muro con puerta")
        st.write("Datos fijos: muro de **4,0 m × 3,0 m** (12 m²), puerta de **1,0 m × 2,0 m** (2 m²), "
                 "R del paño de muro = **55 dB** y R de la puerta = **25 dB**.")
        total_area=12.0
        weak_area=2.0
        share=weak_area/total_area
        wall_area=total_area-weak_area
        main_partition=55
        door=25
        tau=(wall_area*10**(-main_partition/10)+weak_area*10**(-door/10))/total_area
        comp=-10*np.log10(tau)
        st.markdown(
            '<div class="worked-example"><h3>Cálculo del porcentaje de área débil</h3>'
            '<div class="worked-step"><strong>1 · Área total del cerramiento.</strong> 4,0 × 3,0 = <b>12 m²</b>.</div>'
            '<div class="worked-step"><strong>2 · Área de la puerta.</strong> 1,0 × 2,0 = <b>2 m²</b>.</div>'
            '<div class="worked-step"><strong>3 · Porcentaje débil.</strong> '
            '(Sdébil/Stotal) × 100 = (2/12) × 100 = <b>16,7 %</b>.</div>'
            '<div class="worked-result">En la ecuación se usa la fracción 2/12 = 0,1667. '
            'El área útil del muro es 12−2 = 10 m²; la puerta no se suma nuevamente al total.</div></div>',
            unsafe_allow_html=True,
        )
        st.metric("R compuesto",f"{comp:.1f} dB")
        st.info("Los dB no se promedian: se combinan coeficientes de transmisión ponderados por superficie.")
        st.markdown(
            '<div class="good"><b>Comprobación geométrica:</b> la puerta representa '
            '<b>16,7 %</b> del cerramiento, porque (2 m²/12 m²)×100 = 16,7 %. '
            'La fracción que se utiliza en la ecuación es 2/12 = 0,1667.</div>',
            unsafe_allow_html=True,
        )
        check("e6_comp_practical",f"Al combinar energéticamente ambos elementos, el resultado es aproximadamente {comp:.1f} dB. ¿Por qué queda mucho más cerca de la puerta que del muro?",
              ["Porque se promediaron 55 y 25 dB","Porque la puerta tiene un τ mucho mayor y domina la energía transmitida","Porque la puerta ocupa más superficie que el muro"],
              "Porque la puerta tiene un τ mucho mayor y domina la energía transmitida",
              "Aunque solo ocupa 16,7 % del área, la puerta transmite mucha más energía por metro cuadrado. Por eso los coeficientes τ se ponderan por superficie.")
    check(
        "e6",
        "Si se duplica la masa superficial de un panel dentro de la región ideal de la ley de masa, ¿qué mejora aproximada se espera?",
        ["3 dB","6 dB","10 dB","El aislamiento no cambia"],
        "6 dB",
        "La ley de masa ideal predice aproximadamente 6 dB de aumento de R al duplicar la masa superficial, para una misma frecuencia.",
    )

def stage7():
    header(
        "ETAPA 7 · EJERCICIO PROFESIONAL GUIADO",
        "MINVU Magallanes · Sala de Reuniones Dirección",
        "Sigue el proceso completo: requerimiento → geometría → objetivo del elemento → cálculo acústico → DnT,A → decisión de obra.",
    )
    st.image(
        str(ROOT/"assets/course_visuals/minvu_direccion_guided.jpg"),
        caption="Recorte pedagógico del nivel 4. El recinto guiado está marcado en rojo y la longitud compartida es 5,55 m.",
        use_container_width=True,
    )
    st.markdown(
        '<div class="question-box"><div class="question-label">ENCARGO REAL ADAPTADO</div>'
        '<div class="question-text">Diseñar la separación entre Sala de Reuniones Dirección y Oficina Director.</div>'
        '<p>Meta: <b>DnT,A ≥ 35 dB</b>; margen mínimo: <b>5 dB</b>; pérdida de obra: <b>3 dB</b>; '
        'espesor máximo: <b>150 mm</b>. Para actividad interior se utilizará <b>Rw + C</b>.</p></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        pd.DataFrame(
            [
                ["Área Sala de Reuniones Dirección","20,98 m²","Plano nivel 4"],
                ["Área Oficina Director","27,46 m²","Plano nivel 4"],
                ["Longitud del separador","5,55 m","Cota del plano"],
                ["Altura libre","2,70 m","Dato docente"],
                ["Pérdida de obra","3 dB","Supuesto pedagógico"],
                ["Margen mínimo","5 dB","Criterio del encargo"],
            ],
            columns=["Dato","Valor","Origen"],
        ),
        hide_index=True,
        use_container_width=True,
    )

    area_floor=20.98
    height=2.70
    length=5.55
    volume=area_floor*height
    surface=length*height
    kgeo=geometry_term(volume,surface)
    target=35.0
    margin=5.0
    work_loss=3.0
    objective=target+margin+work_loss-kgeo

    st.markdown("### Paso 1 · Identificar el requerimiento")
    descriptor=st.radio(
        "¿Qué descriptor debe verificarse?",
        ["Rw del tabique","DnT,A entre recintos","Tiempo de reverberación"],
        index=None,
        key="minvu_guided_descriptor",
        horizontal=True,
    )
    st.info("La exigencia corresponde al desempeño entre recintos. Rw y Rw+C son entradas del elemento; no son la meta final del edificio.")

    st.markdown("### Paso 2 · Levantar la geometría")
    c1,c2,c3=st.columns(3)
    v_answer=c1.number_input("Volumen receptor V (m³)",0.0,500.0,0.0,.01,key="minvu_guided_v")
    s_answer=c2.number_input("Superficie separadora S (m²)",0.0,200.0,0.0,.01,key="minvu_guided_s")
    k_answer=c3.number_input("Kgeo (dB)",-20.0,20.0,0.0,.01,key="minvu_guided_k")
    with st.expander("Ver fórmula de geometría"):
        formula_card(
            "Geometría del recinto receptor",
            r"V=A_{\mathrm{piso}}h\qquad S=Lh\qquad K_{\mathrm{geo}}=10\log_{10}\left(\frac{0,32V}{S}\right)",
            "<b>V</b>: volumen receptor (m³)<br><b>S</b>: superficie total del separador (m²)<br>"
            "<b>h</b>: altura libre (m)<br><b>L</b>: longitud compartida (m)",
            "Para conectar el aislamiento del elemento con la diferencia estandarizada entre estos recintos.",
        )

    st.markdown("### Paso 3 · Calcular el objetivo del elemento")
    objective_answer=st.number_input(
        "Rw + C objetivo mínimo (dB), incluyendo margen y pérdida de obra",
        0.0,100.0,0.0,.01,key="minvu_guided_objective",
    )
    st.caption("Despeje: (Rw+C)objetivo = meta + margen + pérdida de obra - Kgeo.")

    alternatives=pd.DataFrame(
        [
            ["G-01","Hoja simple reforzada, montante común",40,-2,-7,100,45000],
            ["G-02","Doble placa, cámara con lana, montante alternado",50,-3,-9,140,68000],
            ["TA-01","Solución real: 2 placas/cara y montantes al tresbolillo",60,-4,-11,140,92000],
        ],
        columns=["Código","Descripción","Rw","C","Ctr","Espesor (mm)","Costo ref. ($/m²)"],
    )
    alternatives["Rw+C"]=alternatives["Rw"]+alternatives["C"]
    alternatives["DnT,A estimado"]=alternatives["Rw+C"]+kgeo-work_loss
    alternatives["Margen sobre meta"]=alternatives["DnT,A estimado"]-target

    st.markdown("### Paso 4 · Diseñar y comparar soluciones")
    st.dataframe(
        alternatives[["Código","Descripción","Rw","C","Ctr","Rw+C","Espesor (mm)","Costo ref. ($/m²)"]],
        hide_index=True,
        use_container_width=True,
    )
    st.markdown(
        "En el modelo registra las capas, la cámara, el absorbente y el tipo de conexión. "
        "Revisa la curva R(f), la resonancia masa-aire-masa y las frecuencias críticas antes de aceptar el número único."
    )
    selected=st.radio(
        "¿Qué alternativa es la solución mínima que cumple la meta y el margen?",
        ["G-01","G-02","TA-01"],
        index=None,
        key="minvu_guided_choice",
        horizontal=True,
    )
    dnta_answer=st.number_input(
        "DnT,A estimado de la alternativa elegida (dB)",
        0.0,100.0,0.0,.01,key="minvu_guided_dnta",
    )
    reason=st.text_area(
        "Justificación profesional breve",
        placeholder="Nombra el descriptor, el margen, el espesor, el costo y al menos un riesgo de ejecución.",
        key="minvu_guided_reason",
    )

    st.markdown("### Paso 5 · Elementos débiles y modelo de ventanas")
    st.markdown(
        "Si aparece una ventana doble, el cálculo debe utilizar el modelo de **Quirt**. "
        "Si aparece una puerta u otro componente, el paño se combina energéticamente por superficies."
    )
    quirt_choice=st.radio(
        "¿Qué dato distingue al modelo Quirt de una simple suma de dos vidrios?",
        [
            "Solo el color del vidrio",
            "La cámara sin absorbente, f₁ y las dimensiones h y w del marco",
            "Únicamente el costo de la ventana",
        ],
        index=None,
        key="minvu_guided_quirt",
    )

    if st.button("Comprobar y guardar ejercicio guiado",type="primary",key="minvu_guided_submit"):
        required=[
            descriptor is not None,
            v_answer>0,
            s_answer>0,
            objective_answer>0,
            selected is not None,
            dnta_answer>0,
            bool(reason.strip()),
            quirt_choice is not None,
        ]
        if not all(required):
            st.warning("Completa todos los pasos antes de comprobar el ejercicio.")
        else:
            score=0
            score+=2 if descriptor=="DnT,A entre recintos" else 0
            score+=2 if abs(v_answer-volume)<=.15 else 0
            score+=2 if abs(s_answer-surface)<=.15 else 0
            score+=2 if abs(k_answer-kgeo)<=.12 else 0
            score+=3 if abs(objective_answer-objective)<=.35 else 0
            score+=3 if selected=="G-02" else 0
            score+=2 if abs(dnta_answer-44.8)<=.35 else 0
            words=reason.lower()
            score+=2 if sum(k in words for k in ["margen","espesor","costo","sello","flanco","losa"])>=3 else 1
            score+=2 if quirt_choice=="La cámara sin absorbente, f₁ y las dimensiones h y w del marco" else 0
            level="Correcta" if score>=17 else "Parcialmente correcta" if score>=10 else "Incorrecta"
            _save_formative(
                7,"minvu_guided","Ejercicio profesional guiado MINVU · Sala de Reuniones Dirección",
                json.dumps(
                    {
                        "descriptor":descriptor,"V":v_answer,"S":s_answer,"Kgeo":k_answer,
                        "objetivo":objective_answer,"alternativa":selected,"DnTA":dnta_answer,
                        "justificacion":reason,"quirt":quirt_choice,
                    },
                    ensure_ascii=False,
                ),
                level,
                f"Resultado guiado: {score}/20 puntos.",
                score=score,max_score=20,
                correct_answer="V=56,65 m³; S=14,99 m²; Kgeo=0,83 dB; objetivo Rw+C=42,17 dB; G-02; DnT,A=44,8 dB.",
            )
            if score>=17:
                st.success(f"Ejercicio completado: {score}/20. Aplicaste correctamente el flujo profesional.")
            else:
                st.warning(f"Resultado: {score}/20. Revisa los pasos señalados en la pauta.")

    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Pauta docente · revelar desarrollo completo"):
            st.latex(rf"V=20,98\times2,70={volume:.2f}\ \mathrm{{m^3}}")
            st.latex(rf"S=5,55\times2,70={surface:.2f}\ \mathrm{{m^2}}")
            st.latex(rf"K_{{geo}}=10\log_{{10}}(0,32V/S)={kgeo:.2f}\ \mathrm{{dB}}")
            st.latex(rf"(R_w+C)_{{objetivo}}=35+5+3-{kgeo:.2f}={objective:.2f}\ \mathrm{{dB}}")
            st.dataframe(
                alternatives[["Código","Rw+C","DnT,A estimado","Margen sobre meta","Costo ref. ($/m²)"]],
                hide_index=True,use_container_width=True,
            )
            st.success("Decisión esperada: G-02. G-01 solo logra 35,8 dB y no alcanza el margen; TA-01 es robusta, pero resulta sobredimensionada para este encargo pedagógico.")
            st.markdown(
                "**Solución real TA-01:** canal 92 mm; montantes de 60 mm al tresbolillo; lana de vidrio de 50 mm; "
                "placas de 10 y 15 mm por cara; juntas traslapadas y banda de estanqueidad perimetral. "
                "Resultado del informe: Rw=60 dB, C=-4 dB, Ctr=-11 dB."
            )
    score_counter(7)
    teacher_group_review(
        7,
        {"minvu_guided":"V=56,65 m³; S=14,99 m²; Kgeo=+0,83 dB; Rw+C objetivo=42,17 dB; G-02; DnT,A=44,8 dB."},
    )

def stage8():
    header("ETAPA 8 · DEL ELEMENTO AL EDIFICIO","ISO 12354 e índices de aislamiento acústico",
           "Conecta Rw, C y Ctr del elemento con geometría, pérdidas de obra, flancos y el DnT,A exigido en el caso MINVU.")
    full_matter(8)
    st.markdown("### Ruta profesional utilizada en la asesoría")
    st.markdown(
        '<div class="worked-example"><h3>El cálculo del elemento no entrega por sí solo el desempeño terminado del recinto</h3>'
        '<div class="worked-step"><strong>1 · Elemento.</strong> Se predicen R(f), Rw, C y Ctr.</div>'
        '<div class="worked-step"><strong>2 · Obra.</strong> Se consideran montaje, sellos, encuentros y transmisión lateral para estimar R′.</div>'
        '<div class="worked-step"><strong>3 · Recintos.</strong> La geometría V/S y la normalización permiten estimar DnT,w o DnT,A.</div>'
        '<div class="worked-result">Flujo: requerimiento → cálculo del elemento → pérdida de obra/flancos → geometría → cumplimiento.</div></div>',
        unsafe_allow_html=True,
    )
    formula_card(
        "Relación didáctica empleada en el caso MINVU",
        r"D_{nT,A}\approx(R_w+C)+10\log_{10}\left(\frac{0,32V}{S}\right)-L_{\mathrm{obra}}-L_{\mathrm{flancos}}",
        "<b>V</b>: volumen receptor (m³)<br><b>S</b>: superficie total del separador (m²)<br>"
        "<b>Lobra</b>: pérdida pedagógica de ejecución (dB)<br><b>Lflancos</b>: penalización simplificada de vías laterales (dB)",
        "Para comprender el cálculo inverso y comparar alternativas. No sustituye el modelo detallado por bandas de ISO 12354-1.",
    )
    st.warning(
        "Rw, R′w y DnT,A no son intercambiables. La prima identifica el comportamiento aparente en obra; "
        "nT indica normalización por reverberación; A incorpora la adaptación espectral utilizada por el criterio del caso."
    )
    data=[
      ("R(f)","Reducción por banda","Laboratorio/curva"),
      ("Rw","Reducción ponderada","Laboratorio ISO"),
      ("R′w","Reducción aparente","Terreno, incluye vías laterales"),
      ("DₙT,w","Diferencia estandarizada","Entre recintos, corregida por T"),
      ("D₂m,nT,w","Diferencia de fachada","Exterior a 2 m"),
      ("STC / ASTC","Clasificación ASTM","Laboratorio / terreno"),
      ("OITC","Exterior–interior","Transporte y bajas frecuencias"),
      ("CAC","Paso por cielo/plenum","Cielos suspendidos"),
    ]
    st.dataframe(pd.DataFrame(data,columns=["Indicador","Representa","Contexto"]),hide_index=True,use_container_width=True)
    formula_card("Índice ponderado y términos de adaptación",
                 r"R_w(C;C_{tr})=52(-2;-7)\,\mathrm{dB}\Rightarrow R_w+C=50\,\mathrm{dB},\;R_w+C_{tr}=45\,\mathrm{dB}",
                 "<b>Rw</b>: valor ponderado ISO<br><b>C</b>: adaptación para espectros medios-altos<br><b>Ctr</b>: adaptación para tránsito y contenido grave",
                 "Para adaptar el índice global al espectro de la fuente. C y Ctr se suman algebraicamente; no son aislamientos independientes.")
    source=st.selectbox("Fuente a evaluar",["Voz / actividades domésticas","Tránsito, buses o bajos","Fachada bajo criterio ASTM","Fuente tonal industrial"])
    recommendation={"Voz / actividades domésticas":"Revisar Rw y Rw+C.","Tránsito, buses o bajos":"Priorizar Rw+Cₜᵣ y la curva grave.",
    "Fachada bajo criterio ASTM":"Revisar OITC además de STC.","Fuente tonal industrial":"La curva completa en la banda tonal es indispensable."}[source]
    st.info(recommendation)
    check("e8","Un tabique tiene Rw=55 dB en laboratorio y R′w=47 dB en obra. ¿El laboratorio estaba necesariamente equivocado?",["Sí","No; montaje y vías laterales pueden explicar la diferencia"],"No; montaje y vías laterales pueden explicar la diferencia","R′w incorpora el comportamiento aparente de la construcción instalada.")

def stage9():
    header("ETAPA 9 · APLICACIÓN PRÁCTICA","Interpretación de índices acústicos",
           "Relaciona cada índice con su definición, contexto de medición y uso correcto.")
    full_matter(9)
    st.markdown("### Actividad · Relaciona los términos pareados")
    st.markdown(
        "En la columna izquierda aparecen los índices acústicos. En la derecha están las definiciones "
        "numeradas y mezcladas. Selecciona junto a cada índice el número que le corresponde."
    )
    paired_terms = {
        "R": "Índice por banda de frecuencia que expresa la reducción sonora de un elemento en laboratorio.",
        "R_w": "Índice único ponderado ISO obtenido al ajustar una curva de referencia a resultados de laboratorio.",
        "R′_w": "Índice único aparente medido en obra, que incorpora montaje, encuentros y transmisiones laterales.",
        "D_nT,w": "Diferencia de niveles entre recintos, normalizada por el tiempo de reverberación y ponderada.",
        "D_2m,nT,w": "Diferencia de niveles de fachada medida con el nivel exterior a 2 m, normalizada y ponderada.",
        "C": "Término de adaptación espectral asociado principalmente a ruido rosa y fuentes de contenido medio-alto.",
        "Cₜᵣ": "Término de adaptación espectral apropiado para tránsito y fuentes con contenido importante en bajas frecuencias.",
        "STC": "Clasificación ASTM de número único usada principalmente para particiones interiores.",
        "OITC": "Clasificación ASTM orientada al aislamiento frente a ruido exterior, especialmente transporte.",
        "CAC": "Clasificación del aislamiento entre recintos que comparten un cielo suspendido y plenum.",
    }
    definitions = list(paired_terms.values())
    mixed_order=[7,2,5,0,8,3,9,1,6,4]
    numbered_definitions={number:definitions[source_index] for number,source_index in enumerate(mixed_order,1)}
    correct_numbers={
        term:next(number for number,definition in numbered_definitions.items() if definition==correct_definition)
        for term,correct_definition in paired_terms.items()
    }
    placeholder = "—"
    selections = {}
    left,right=st.columns([.85,2.15],gap="large")
    with left:
        st.markdown("#### Índices o descriptores")
        for idx,term in enumerate(paired_terms):
            row_label,row_value=st.columns([1.2,.8])
            row_label.markdown(f"**{term}**")
            selections[term]=row_value.selectbox(
                f"Número para {term}",[placeholder]+list(range(1,11)),
                key=f"e9_pair_number_{idx}",label_visibility="collapsed",
            )
    with right:
        st.markdown("#### Definiciones numeradas")
        for number,definition in numbered_definitions.items():
            st.markdown(
                f'<div class="card" style="margin:.28rem 0;padding:.72rem .9rem">'
                f'<b style="color:#0871bd">{number}.</b> {definition}</div>',
                unsafe_allow_html=True,
            )
    if st.button("Comprobar términos pareados",key="e9_check_pairs",type="primary"):
        unanswered=[term for term,value in selections.items() if value==placeholder]
        if unanswered:
            st.warning(f"Completa todas las relaciones. Faltan: {', '.join(unanswered)}.")
        else:
            correct_count=sum(selections[term]==correct_numbers[term] for term in paired_terms)
            pair_score=correct_count*2
            level="Correcta" if correct_count==len(paired_terms) else "Parcialmente correcta" if correct_count>=4 else "Incorrecta"
            _save_formative(
                9,"e9_pairs","Relaciona cada índice acústico con su definición.",
                json.dumps(selections,ensure_ascii=False),level,
                f"{correct_count} de {len(paired_terms)} relaciones correctas.",
                score=pair_score,max_score=20,
            )
            if correct_count==len(paired_terms):
                st.success("¡Correcto! Relacionaste adecuadamente los 10 términos acústicos.")
            else:
                st.warning(f"Obtuviste {correct_count} de {len(paired_terms)} relaciones correctas.")
                for term,correct_definition in paired_terms.items():
                    if selections[term]!=correct_numbers[term]:
                        st.error(
                            f"{term}: la relación seleccionada no corresponde. "
                            f"El número correcto es {correct_numbers[term]}: {correct_definition}",
                            icon="↔️",
                        )
            repeated={number for number in range(1,11) if list(selections.values()).count(number)>1}
            if repeated:
                st.info(f"Revisa los números repetidos ({', '.join(map(str,sorted(repeated)))}): cada definición se utiliza una sola vez.")
    score_counter(9)
    if st.session_state.get("role")=="Docente":
        with st.expander("👩‍🏫 Pauta docente · Términos pareados"):
            st.markdown(
                "Proyecte primero las relaciones sin revelar la pauta. Pida que el curso justifique "
                "especialmente las diferencias entre laboratorio, obra, recintos y fachada."
            )
            if st.checkbox("Mostrar solución de términos pareados",key="e9_reveal_pairs"):
                st.dataframe(
                    pd.DataFrame(
                        [{"Término":term,"N.º correcto":correct_numbers[term],"Definición correcta":definition}
                         for term,definition in paired_terms.items()]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
                st.info(
                    "Tip técnico: la prima en R′w identifica desempeño aparente en obra; "
                    "el subíndice 2m identifica fachada; nT indica normalización por reverberación. "
                    "C y Cₜᵣ no son índices independientes: se suman algebraicamente a Rw."
                )
        teacher_group_review(9,{"e9_pairs":"Cada uno de los 10 términos debe asociarse una sola vez con la definición mostrada en la pauta docente."})

def stage10():
    header(
        "ETAPA 10 · EVALUACIÓN PROFESIONAL FINAL",
        "MINVU Magallanes · Sala de Reuniones Licitaciones",
        "Caso individual equivalente al ejercicio guiado. Cambia la geometría e incorpora una puerta que puede dominar el resultado.",
    )
    already_submitted=any(row[1]=="final_exam" for row in _student_scores())
    if already_submitted and st.session_state.get("role")!="Docente":
        st.success("Tu evaluación final ya fue enviada. El intento quedó cerrado y guardado.")
        st.info("El docente puede revisar tu desarrollo, ajustar el puntaje con fundamento o habilitar un nuevo intento desde Gestión de alumnos.")
        score_counter(10)
        return

    st.image(
        str(ROOT/"assets/course_visuals/minvu_licitaciones_exam.jpg"),
        caption="Recorte del nivel 4. La Sala de Reuniones Licitaciones está marcada en rojo y el paño hacia circulación incluye una puerta.",
        use_container_width=True,
    )
    st.markdown(
        '<div class="question-box"><div class="question-label">ENCARGO INDIVIDUAL · 90 MINUTOS</div>'
        '<div class="question-text">Propón la combinación de menor costo que cumpla DnT,A ≥ 35 dB.</div>'
        '<p>Después de una pérdida de obra de 3 dB debe conservar un margen mínimo de 3 dB. '
        'Usa <b>Rw + C</b>, combina tabique y puerta energéticamente y justifica la solución.</p></div>',
        unsafe_allow_html=True,
    )
    st.warning("Intento único. Revisa todos los campos antes de presionar «Enviar evaluación final».")

    floor_area=24.84
    height=2.70
    length=3.72
    door_w=0.90
    door_h=2.10
    volume=floor_area*height
    surface=length*height
    door_area=door_w*door_h
    wall_area=surface-door_area
    kgeo=geometry_term(volume,surface)
    work_loss=3.0
    required_dnta=38.0

    opaque={
        "O-01":{"name":"Tabique básico","rw":44,"c":-2,"thickness":100,"cost":45000},
        "O-02":{"name":"Tabique reforzado desacoplado","rw":52,"c":-3,"thickness":140,"cost":68000},
        "O-03":{"name":"TA-01","rw":60,"c":-4,"thickness":140,"cost":92000},
    }
    doors={
        "P-01":{"name":"Puerta hueca sin sello inferior","rw":22,"c":-1,"cost":280000},
        "P-02":{"name":"Puerta sólida con sellos","rw":32,"c":-1,"cost":690000},
        "P-03":{"name":"Puerta acústica certificada","rw":40,"c":-1,"cost":1650000},
    }
    st.markdown("### Antecedentes del caso")
    st.dataframe(
        pd.DataFrame(
            [
                ["Área de piso receptor","24,84 m²"],["Altura libre","2,70 m"],
                ["Longitud del separador","3,72 m"],["Puerta","0,90 × 2,10 m"],
                ["Meta","DnT,A ≥ 35 dB"],["Margen mínimo","3 dB"],
                ["Pérdida de obra","3 dB"],["Espesor máximo","150 mm"],
            ],
            columns=["Dato","Valor"],
        ),
        hide_index=True,use_container_width=True,
    )
    component_rows=[]
    for code,item in opaque.items():
        component_rows.append([code,item["name"],item["rw"],item["c"],item["rw"]+item["c"],f'{item["thickness"]} mm',f'${item["cost"]:,.0f}/m²'.replace(",","." )])
    for code,item in doors.items():
        component_rows.append([code,item["name"],item["rw"],item["c"],item["rw"]+item["c"],"—",f'${item["cost"]:,.0f}/un'.replace(",","." )])
    st.dataframe(
        pd.DataFrame(component_rows,columns=["Código","Componente","Rw","C","Rw+C","Espesor","Costo"]),
        hide_index=True,use_container_width=True,
    )

    st.markdown("### 1 · Requerimiento y descriptor · 10 puntos")
    descriptor=st.radio(
        "Selecciona la verificación correcta",
        [
            "Comparar directamente Rw con 35 dB",
            "Calcular DnT,A con Rw+C, geometría y pérdida de obra",
            "Promediar Rw del muro y de la puerta",
        ],
        index=None,key="final_descriptor",
    )

    st.markdown("### 2 · Levantamiento geométrico · 15 puntos")
    g1,g2,g3=st.columns(3)
    v_ans=g1.number_input("V (m³)",0.0,500.0,0.0,.01,key="final_v")
    s_ans=g2.number_input("S total (m²)",0.0,200.0,0.0,.01,key="final_s")
    sd_ans=g3.number_input("S puerta (m²)",0.0,20.0,0.0,.01,key="final_sd")
    g4,g5=st.columns(2)
    sw_ans=g4.number_input("S tabique neto (m²)",0.0,200.0,0.0,.01,key="final_sw")
    k_ans=g5.number_input("Kgeo (dB)",-20.0,20.0,0.0,.01,key="final_kgeo")

    st.markdown("### 3 · Configuración del modelo acústico · 15 puntos")
    model_text=st.text_area(
        "Describe cómo configurarías y revisarías O-02 en el modelo acústico",
        placeholder="Capas, cámara, absorbente, montantes/conexión, curva R(f), resonancia y frecuencias críticas.",
        key="final_model",
    )

    st.markdown("### 4 · Aislamiento compuesto y paso a DnT,A · 35 puntos")
    st.latex(r"R_{\mathrm{comp,A}}=-10\log_{10}\left[\frac{S_m10^{-(R_w+C)_m/10}+S_p10^{-(R_w+C)_p/10}}{S}\right]")
    st.latex(r"D_{nT,A}\approx R_{\mathrm{comp,A}}+K_{\mathrm{geo}}-L_{\mathrm{obra}}")
    test_pairs=[("O-01","P-01"),("O-01","P-02"),("O-02","P-02")]
    pair_answers={}
    for idx,(o,p) in enumerate(test_pairs,1):
        st.markdown(f"**Combinación {idx}: {o} + {p}**")
        c1,c2=st.columns(2)
        pair_answers[(o,p)]=(
            c1.number_input("Rcomp,A (dB)",0.0,100.0,0.0,.01,key=f"final_rcomp_{idx}"),
            c2.number_input("DnT,A estimado (dB)",0.0,100.0,0.0,.01,key=f"final_dnta_{idx}"),
        )

    st.markdown("### 5 · Optimización · 10 puntos")
    choice=st.selectbox(
        "Combinación de menor costo que alcanza 38 dB (meta + margen)",
        ["— Selecciona —"]+[f"{o} + {p}" for o in opaque for p in doors],
        key="final_choice",
    )
    cost_ans=st.number_input(
        "Costo instalado de la combinación elegida ($)",
        0,5000000,0,step=1000,key="final_cost",
    )

    st.markdown("### 6 · Constructibilidad y conclusión · 15 puntos")
    construction=st.text_area(
        "Indica cinco medidas de control de obra verificables",
        placeholder="Ej.: continuidad losa a losa, sellos, juntas, cajas, marco y sello inferior de puerta...",
        key="final_construction",
    )
    conclusion=st.text_area(
        "Conclusión profesional · máximo 150 palabras",
        max_chars=1200,
        placeholder="Señala combinación, descriptor, resultado, margen, costo, elemento dominante y riesgo de obra.",
        key="final_conclusion",
    )

    if st.button("Enviar evaluación final",type="primary",key="final_exam_submit"):
        numeric_complete=all([
            v_ans>0,s_ans>0,sd_ans>0,sw_ans>0,
            all(r>0 and d>0 for r,d in pair_answers.values()),
            cost_ans>0,
        ])
        if descriptor is None or not numeric_complete or choice.startswith("—") or not model_text.strip() or not construction.strip() or not conclusion.strip():
            st.warning("La evaluación está incompleta. Revisa requerimiento, geometría, tres combinaciones, costo y respuestas profesionales.")
        else:
            score=0.0
            score+=10 if descriptor=="Calcular DnT,A con Rw+C, geometría y pérdida de obra" else 0
            geometry_checks=[
                abs(v_ans-volume)<=.15,abs(s_ans-surface)<=.10,abs(sd_ans-door_area)<=.05,
                abs(sw_ans-wall_area)<=.10,abs(k_ans-kgeo)<=.10,
            ]
            score+=3*sum(geometry_checks)

            model_words=model_text.lower()
            model_hits=sum(any(term in model_words for term in group) for group in [
                ["placa","capa"],["cámara","camara"],["lana","absorb"],["montante","desacopl","conex"],
                ["curva","r(f)"],["resonan","crítica","critica","coincid"],
            ])
            score+=15 if model_hits>=5 else 10 if model_hits>=3 else 5 if model_hits>=1 else 0

            expected={}
            for o,p in test_pairs:
                ro=opaque[o]["rw"]+opaque[o]["c"]
                rp=doors[p]["rw"]+doors[p]["c"]
                rcomp=compound_r([wall_area,door_area],[ro,rp])
                expected[(o,p)]=(rcomp,rcomp+kgeo-work_loss)
            compound_hits=0
            dnta_hits=0
            for pair,(r_ans,d_ans) in pair_answers.items():
                r_expected,d_expected=expected[pair]
                compound_hits+=abs(r_ans-r_expected)<=.25
                dnta_hits+=abs(d_ans-d_expected)<=.25
            score+=(20/3)*compound_hits
            score+=5*dnta_hits

            optimal_cost=round(wall_area*opaque["O-02"]["cost"]+doors["P-02"]["cost"])
            score+=6 if choice=="O-02 + P-02" else 0
            score+=4 if abs(cost_ans-optimal_cost)<=2000 else 0

            construction_words=construction.lower()
            construction_hits=sum(any(term in construction_words for term in group) for group in [
                ["losa"],["sello","burlete"],["junta","traslap"],["caja","enchufe"],
                ["puerta","marco","inferior"],["ducto","paso"],["encuentro"],["foto","inspección","inspeccion"],
            ])
            score+=10 if construction_hits>=5 else 6 if construction_hits>=3 else 3 if construction_hits>=1 else 0

            conclusion_words=conclusion.lower()
            conclusion_hits=sum(any(term in conclusion_words for term in group) for group in [
                ["o-02"],["p-02"],["dnt","38,3","38.3"],["margen"],["costo"],["puerta","domin"],
            ])
            score+=5 if conclusion_hits>=4 else 3 if conclusion_hits>=2 else 1
            score=min(100.0,score)
            level="Correcta" if score>=60 else "Incorrecta"
            _save_formative(
                10,"final_exam","Evaluación profesional final MINVU · Sala de Reuniones Licitaciones",
                json.dumps(
                    {
                        "descriptor":descriptor,
                        "geometria":{"V":v_ans,"S":s_ans,"Spuerta":sd_ans,"Stabique":sw_ans,"Kgeo":k_ans},
                        "modelo_acustico":model_text,
                        "combinaciones":{f"{o}+{p}":{"Rcomp":r,"DnTA":d} for (o,p),(r,d) in pair_answers.items()},
                        "seleccion":choice,"costo":cost_ans,
                        "constructibilidad":construction,"conclusion":conclusion,
                    },
                    ensure_ascii=False,
                ),
                level,
                f"Puntaje automático inicial: {score:.1f}/100. Pendiente de revisión docente cualitativa.",
                score=score,max_score=100,
                correct_answer="V=67,07; S=10,04; Sp=1,89; Sm=8,15; Kgeo=3,30. Alternativa óptima: O-02+P-02; DnT,A=38,3 dB; costo=$1.244.472.",
            )
            st.session_state.exam_result=score
            st.success(f"Evaluación enviada y cerrada. Puntaje automático inicial: {score:.1f}/100.")
            st.info("La conclusión, la configuración del modelo y las medidas de obra quedan disponibles para revisión del docente.")

    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Pauta docente · resultados y rúbrica"):
            st.markdown(
                f"**Geometría:** V={volume:.2f} m³; S={surface:.2f} m²; Spuerta={door_area:.2f} m²; "
                f"Stabique={wall_area:.2f} m²; Kgeo={kgeo:.2f} dB."
            )
            rows=[]
            for o,oi in opaque.items():
                for p,pi in doors.items():
                    rcomp=compound_r([wall_area,door_area],[oi["rw"]+oi["c"],pi["rw"]+pi["c"]])
                    dnta=rcomp+kgeo-work_loss
                    cost=wall_area*oi["cost"]+pi["cost"]
                    rows.append([f"{o} + {p}",round(rcomp,1),round(dnta,1),round(cost)])
            st.dataframe(pd.DataFrame(rows,columns=["Combinación","Rcomp,A","DnT,A","Costo ($)"]),hide_index=True,use_container_width=True)
            st.success("Respuesta óptima: O-02 + P-02. DnT,A ≈ 38,3 dB; margen ≈ 3,3 dB; costo ≈ $1.244.472.")
            st.markdown(
                "**Rúbrica:** requerimiento 10; geometría 15; configuración del modelo 15; "
                "aislamiento compuesto 20; paso a DnT,A 15; optimización 10; constructibilidad 10; conclusión 5."
            )
    score_counter(10)
    teacher_group_review(
        10,
        {"final_exam":"V=67,07 m³; S=10,04 m²; Sp=1,89 m²; Sm=8,15 m²; Kgeo=3,30 dB. "
         "O-02+P-02 es la combinación mínima que logra meta+margen: DnT,A≈38,3 dB."},
    )
