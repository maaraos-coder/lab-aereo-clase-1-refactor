"""Etapas activas del Laboratorio 1.

El módulo conserva intacto el contenido pedagógico. ``app.py`` inyecta las
dependencias compartidas antes de ejecutar cada etapa o helper, evitando
duplicar infraestructura y manteniendo el estado de Streamlit existente.
"""

_RUNTIME_PROTECTED = {
    "run_stage", "run_helper", "_STAGES", "_HELPERS", "_RUNTIME_PROTECTED",
    "_bind_runtime",
    *{f"_stage{i}_impl" for i in range(11)},
    "_lab1_final_submission_impl", "_lab1_case_score_impl", "_finish_lab1_final_impl",
}

def _bind_runtime(runtime):
    """Actualiza dependencias compartidas sin sobrescribir este módulo."""
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and not name.startswith("lab1_stage"):
            module_globals[name] = value

def _stage0_impl():
    header('ETAPA 0 · BIENVENIDA', 'Laboratorio del curso Aislamiento a Ruido Aéreo', 'Una experiencia visual para comprender el fenómeno, experimentar con variables y decidir con criterio técnico y económico.')
    st.markdown(f'<div class="class-clock"><div><strong>⏱️ Duración total de la clase: 4 horas</strong><br><span>{sum(STAGE_MINUTES.values())} min de aprendizaje y aplicación + {BREAK_MINUTES} min de pausa</span></div><div><strong>{TOTAL_CLASS_MINUTES} min</strong></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>', unsafe_allow_html=True)
    html = '<div class="route-grid">'
    for i, ((_, title), (short, desc)) in enumerate(zip(STAGES[1:], ROUTE_SUMMARIES), 1):
        html += f'<div class="route-card"><span class="step">{i}</span><div><b>{title}</b><p>{desc}</p><span class="route-time">⏱️ {STAGE_MINUTES[i]} min</span></div></div>'
        if i == BREAK_AFTER_STAGE:
            html += f'<div class="break-card"><span class="step">☕</span><div><b>Pausa pedagógica</b><p>Descanso antes del bloque de fundamentos físicos.</p><span class="route-time">⏱️ {BREAK_MINUTES} min</span></div></div>'
    st.markdown(html + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> concepto visual → explicación técnica → ejemplo → interacción → interpretación → ejercicio → retroalimentación.</div>', unsafe_allow_html=True)

def _stage1_impl():
    header('ETAPA 1 · MATERIA + LABORATORIO', 'Control del ruido: fuente, trayectoria y receptor', 'Antes de elegir un material hay que localizar dónde nace el ruido, cómo se propaga y a quién afecta.')
    full_matter(1)
    lesson('Modelo de control', 'Fuente: genera la energía. Trayectoria: medio y vías de propagación. Receptor: persona, actividad o recinto afectado. Una solución robusta puede combinar los tres.')
    st.markdown('<div class="section-band"><span>🎛️</span><h3>Laboratorio visual: interviene la escena</h3></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    source = c1.selectbox('🏭 En la fuente', ['Sin intervención', 'Encerrar la fuente', 'Soportes antivibratorios', 'Equipo de menor emisión'])
    path = c2.selectbox('〰️ En la trayectoria', ['Sin intervención', 'Barrera acústica'])
    receiver = c3.selectbox('👤 En el receptor', ['Sin intervención', 'Protección auditiva', 'Cabina acústica', 'Mejorar fachada'])
    distance = st.select_slider('📏 Separación física entre la fuente y el receptor', options=['Distancia inicial', 'Distancia aumentada'], help='La distancia no es una barrera ni una intervención en la trayectoria: es una condición geométrica del problema.')
    gains = {'Sin intervención': 0, 'Encerrar la fuente': 10, 'Soportes antivibratorios': 5, 'Equipo de menor emisión': 12, 'Barrera acústica': 12, 'Protección auditiva': 10, 'Cabina acústica': 15, 'Mejorar fachada': 11}
    distance_gain = 5 if distance == 'Distancia aumentada' else 0
    total = gains[source] + gains[path] + gains[receiver] + distance_gain
    enclosure = '<div class="machine-box"></div>' if source == 'Encerrar la fuente' else ''
    mounts = '<div class="mounts">▰ ▰</div>' if source == 'Soportes antivibratorios' else ''
    barrier = '<div class="barrier"></div>' if path == 'Barrera acústica' else ''
    cabin = '<div class="receiver-cabin"></div>' if receiver == 'Cabina acústica' else ''
    facade = '<div class="receiver-facade"></div>' if receiver == 'Mejorar fachada' else ''
    phones = '<div class="headphones">🎧</div>' if receiver == 'Protección auditiva' else ''
    wave_count = max(1, 6 - round(total / 7))
    waves = ')' * wave_count
    distance_class = ' distance-on' if distance == 'Distancia aumentada' else ''
    distance_label = 'Fuente y receptor más separados' if distance == 'Distancia aumentada' else 'Distancia inicial'
    st.markdown(f'<div class="scene-pro{distance_class}"><div class="scene-caption">Nivel visual estimado: {85 - total} dB</div>{enclosure}{mounts}<div class="machine">⚙️</div><div class="waves">))) {waves}</div>{barrier}{cabin}{facade}{phones}<div class="person">🧑</div><div class="distance-label">↔ {distance_label}</div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Nivel inicial', '85 dB')
    b.metric('Reducción estimada', f'{total} dB')
    c.metric('Nivel resultante', f'{85 - total} dB')
    st.markdown('<div class="warn">Las reducciones se suman aquí con fines didácticos. En un proyecto real deben evaluarse por bandas, vías dominantes y condiciones de montaje.</div>', unsafe_allow_html=True)
    check('e1', 'Una máquina afecta una oficina contigua. ¿Dónde actúa el muro separador?', ['Fuente', 'Trayectoria', 'Receptor'], 'Trayectoria', 'El muro se interpone en el camino de propagación.')

def _stage2_impl():
    header('ETAPA 2 · LABORATORIO DE DOS RECINTOS', 'Aislamiento no es absorción', 'Cambia el panel separador y acondiciona el recinto receptor para observar qué magnitud modifica cada decisión.')
    full_matter(2)
    lesson('Aislamiento acústico', 'Reduce la energía que atraviesa un elemento entre recintos. Se mejora con masa, estanqueidad, desacoplamiento y control de vías indirectas.')
    lesson('Absorción acústica', 'Reduce reflexiones dentro del mismo recinto. Se expresa mediante α entre 0 y 1 y modifica reverberación e inteligibilidad.')
    st.markdown('<div class="section-band"><span>🧪</span><h3>Ejemplo didáctico: recinto emisor → panel → recinto receptor</h3></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    panel = c1.selectbox('🧱 Panel separador', ['Panel liviano simple', 'Muro de albañilería', 'Tabique doble desacoplado'], help='Este control modifica la transmisión entre los dos recintos.')
    material = c2.selectbox('🟦 Material absorbente en el receptor', ['Sin tratamiento', 'Panel poroso α = 0,40', 'Lana mineral revestida α = 0,75', 'Panel de alto desempeño α = 0,90'], help='Este material controla las reflexiones dentro del recinto receptor.')
    area = c3.slider('📐 Superficie absorbente instalada (m²)', 0, 60, 0, 5)
    panel_data = {'Panel liviano simple': (30, 'light'), 'Muro de albañilería': (45, 'masonry'), 'Tabique doble desacoplado': (55, 'double')}
    alpha_data = {'Sin tratamiento': 0.0, 'Panel poroso α = 0,40': 0.4, 'Lana mineral revestida α = 0,75': 0.75, 'Panel de alto desempeño α = 0,90': 0.9}
    R, panel_class = panel_data[panel]
    alpha = alpha_data[material]
    V = 120.0
    A0 = 18.0
    A = A0 + alpha * area
    T0 = 0.161 * V / A0
    T = 0.161 * V / A
    source_level = 85.0
    room_correction = 10 * math.log10(A / A0) if A > A0 else 0.0
    receiver_level = source_level - R - room_correction
    absorber_count = 0 if area == 0 or alpha == 0 else min(4, max(1, math.ceil(area / 15)))
    absorber_html = ''.join((f"""<div class="absorber {('ceiling' if i == 3 else f'a{i + 1}')}"></div>""" for i in range(absorber_count)))
    echo_count = max(0, 3 - round((A - A0) / 18))
    echoes = ''.join((f'<div class="echo-wave e{i + 1}">↝ ↝</div>' for i in range(echo_count)))
    wave_strength = max(1, min(5, round((60 - R) / 7)))
    transmitted = ')' * wave_strength
    st.markdown(f'<div class="two-room-lab"><div class="lab-room"><div class="room-name">RECINTO EMISOR · 85 dB</div><div class="speaker-visual">🔊</div><div class="incident-wave">))) )))</div></div><div class="lab-panel {panel_class}">{panel}<br>R = {R} dB</div><div class="lab-room receiver"><div class="room-name">RECINTO RECEPTOR</div>{absorber_html}{echoes}<div class="transmitted-wave">{transmitted}</div><div class="listener-visual">🧑\u200d💻</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="concept-grid"><div class="concept-result">🧱<b>{R:.0f} dB</b><span>Aislamiento R del panel<br><strong>No cambia por agregar absorbentes</strong></span></div><div class="concept-result">🟦<b>{A:.1f} m² sabin</b><span>Absorción equivalente del receptor<br>Inicial: {A0:.1f} m² sabin</span></div><div class="concept-result">⏱️<b>{T:.2f} s</b><span>T₆₀ del recinto receptor<br>Inicial: {T0:.2f} s</span></div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Nivel estimado en el receptor', f'{receiver_level:.1f} dB')
    b.metric('Cambio de T₆₀', f'{T - T0:+.2f} s')
    c.metric('Cambio del aislamiento R', '0 dB' if material != 'Sin tratamiento' else 'Sin tratamiento')
    st.markdown('<div class="good"><b>Interpretación:</b> cambiar el panel separador modifica el aislamiento entre recintos. Agregar material absorbente en el receptor aumenta su absorción equivalente, reduce las reflexiones y disminuye el T₆₀. El nivel medido en el receptor puede bajar por la menor reverberación, pero el valor R propio del panel no aumenta.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>📐</span><h3>Laboratorio visual: absorción equivalente y ecuación de Sabine</h3></div>', unsafe_allow_html=True)
    formula_card('Absorción equivalente y ecuación de Sabine', 'A=\\sum_i S_i\\alpha_i \\qquad T_{60}=0{,}161\\,\\frac{V}{A}', '<b>S</b>: superficie (m²)<br><b>α</b>: coeficiente de absorción<br><b>V</b>: volumen (m³)<br><b>A</b>: absorción equivalente (m² sabin)', 'Para estimar el tiempo de reverberación en un recinto de campo aproximadamente difuso.')
    c1, c2, c3 = st.columns(3)
    sabine_v = c1.number_input('Volumen (m³)', 50, 1000, 220, key='e2_sabine_v')
    sabine_base = c2.number_input('Absorción inicial (m² sabin)', 5.0, 200.0, 28.0, key='e2_sabine_base')
    sabine_area = c3.number_input('Área nueva (m²)', 0.0, 300.0, 55.0, key='e2_sabine_area')
    sabine_alpha = st.select_slider('α del material en 500 Hz', options=[0.05, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95], value=0.8, key='e2_sabine_alpha')
    sabine_a = sabine_base + sabine_area * sabine_alpha
    sabine_t = 0.161 * sabine_v / sabine_a
    sabine_t0 = 0.161 * sabine_v / sabine_base
    a, b, c = st.columns(3)
    a.metric('A nueva', f'{sabine_a:.1f} m² sabin')
    b.metric('T₆₀ inicial', f'{sabine_t0:.2f} s')
    c.metric('T₆₀ final', f'{sabine_t:.2f} s', delta=f'{sabine_t - sabine_t0:+.2f} s')
    if sabine_t <= 0.8:
        st.success('Condición didáctica favorable para habla: decaimiento rápido y mejor claridad.')
    elif sabine_t <= 1.2:
        st.warning('Condición intermedia. Puede requerir más absorción según volumen y uso.')
    else:
        st.error('Reverberación alta para una actividad centrada en la palabra.')
    check('e2_sabine_check', 'Si el volumen se mantiene y se duplica A, ¿qué ocurre con T₆₀?', ['Se duplica', 'Se reduce aproximadamente a la mitad', 'No cambia'], 'Se reduce aproximadamente a la mitad', 'Sabine muestra una relación inversa entre T₆₀ y A.')
    check('e2_lab_1', 'Si mantienes el mismo panel y agregas material absorbente en el recinto receptor, ¿qué cambia principalmente?', ['Aumenta el aislamiento R del panel', 'Aumenta la absorción y disminuye el T₆₀', 'Aumenta la transmisión por el panel'], 'Aumenta la absorción y disminuye el T₆₀', 'El absorbente actúa sobre las reflexiones del recinto receptor. No modifica por sí solo la propiedad aislante del panel.')
    check('e2_lab_2', '¿Qué intervención permite reducir directamente la energía que atraviesa desde el recinto emisor?', ['Cambiar por un panel separador de mayor aislamiento', 'Agregar paneles absorbentes al receptor', 'Reducir únicamente el T₆₀ del receptor'], 'Cambiar por un panel separador de mayor aislamiento', 'La transmisión entre recintos se controla mejorando la separación: masa, estanqueidad, desacoplamiento y vías laterales.')

def _stage3_impl():
    header('ETAPA 3 · PREGUNTAS DE APLICACIÓN', 'Aislamiento, absorción y acondicionamiento acústico', 'Responde las cinco situaciones, comprueba tu razonamiento y revisa la aclaración correspondiente.')
    st.markdown('<div class="section-band"><span>✍️</span><h3>Aplicación conceptual · responde y comprueba</h3></div>', unsafe_allow_html=True)
    questions = [('s3q1', 'En una sala de reuniones se instalan paneles acústicos de espuma en todas las paredes. ¿Este tratamiento mejora el aislamiento acústico entre salas contiguas? Justifica tu respuesta.', 'No de forma significativa. La espuma es principalmente absorbente: reduce reflexiones y reverberación dentro de la sala, pero su baja masa no impide eficazmente la transmisión. Para aislar se debe mejorar el cerramiento mediante masa, estanqueidad, desacoplamiento y control de fugas y flancos.', [['no', 'no mejora'], ['absor', 'reverber'], ['masa', 'estanque', 'desacopl', 'cerramiento']], 'Diferencia el control de reflexiones interiores del control de transmisión entre recintos.'), ('s3q2', 'Se requiere reducir el eco en una oficina sin afectar la transmisión de sonido hacia otros recintos. ¿Qué tipo de tratamiento acústico se debe aplicar y por qué?', 'Se debe aplicar acondicionamiento absorbente interior —paneles, cielo acústico o bafles— para aumentar la absorción equivalente y reducir el T₆₀. El objetivo es controlar reflexiones dentro de la oficina, no modificar el aislamiento del cerramiento.', [['absor', 'acondicion'], ['eco', 'reflex', 'reverber'], ['t60', 'tiempo de reverberación']], 'La intervención buscada actúa dentro del mismo recinto y no sobre el sonido que atraviesa la separación.'), ('s3q3', 'Una persona sigue escuchando a sus vecinos a pesar de instalar paneles acústicos de espuma en su muro. ¿Cuál es el error común en la solución adoptada?', 'El error es confundir absorción con aislamiento. La espuma puede reducir reflexiones en la habitación, pero no aporta suficiente masa ni desacoplamiento. Deben revisarse muro, puertas, ventanas, juntas, enchufes y transmisiones laterales.', [['confund', 'absorción', 'absorcion'], ['aislamiento', 'transmisión', 'transmision'], ['masa', 'desacopl', 'sell', 'fuga', 'flanco']], 'Explica por qué un material absorbente no se transforma automáticamente en un buen aislante.'), ('s3q4', 'Un gimnasio necesita reducir el ruido percibido en oficinas contiguas. ¿Se deben usar materiales absorbentes o aislantes? Propón una solución adecuada.', 'Se requieren principalmente soluciones aislantes y de control vibratorio: piso resiliente o flotante, soportes antivibratorios, cerramientos dobles desacoplados, mayor masa y sellado. Los absorbentes pueden complementar reduciendo la reverberación del gimnasio, pero no sustituyen el aislamiento.', [['aisl', 'transmis'], ['vibr', 'piso flotante', 'soporte'], ['doble', 'masa', 'sell', 'desacopl']], 'Distingue el ruido aéreo de los impactos y vibraciones que pueden viajar por la estructura.'), ('s3q5', 'Se diseñan dos salas de clases. Una usa paneles absorbentes en el techo y la otra usa muros dobles entre salas. ¿Cuál solución afecta más la inteligibilidad del habla dentro de la sala y cuál mejora el aislamiento entre ellas?', 'Los paneles absorbentes del techo reducen el T₆₀ y mejoran principalmente la inteligibilidad dentro del aula. Los muros dobles desacoplados reducen la transmisión y mejoran principalmente el aislamiento entre las salas.', [['panel', 'techo', 'absorb'], ['intelig', 'reverber'], ['muro doble', 'aislamiento', 'transmis']], 'Asocia cada solución con el lugar donde aparece su beneficio: dentro de la sala o al otro lado de la separación.')]
    solutions = {}
    for key, q, solution, groups, note in questions:
        formative_development(3, key, q, solution, groups, note)
        solutions[key] = solution
    score_counter(3)
    teacher_group_review(3, solutions)

def _stage4_impl():
    header('ETAPA 4 · MATERIA + MODELO', 'Aislamiento acústico y costo-beneficio', 'La mejor solución no es la de mayor número ni la más barata: es la que cumple la meta con un costo justificable.')
    full_matter(4)
    lesson('Orden correcto de decisión', '1) definir meta y espectro; 2) descartar lo que no cumple; 3) comparar costo del ciclo, vida útil, riesgo, ROI y recuperación; 4) revisar margen de seguridad.')
    formula_card('Del beneficio anual bruto al flujo neto anual', 'F_{\\mathrm{neto,anual}}=B_{\\mathrm{bruto,anual}}-C_{\\mathrm{recurrente,anual}}', '<b>F<sub>neto</sub></b>: flujo anual neto ($/año)<br><b>B<sub>bruto</sub></b>: ahorro o ganancia total que produce la solución durante un año, antes de descontar gastos ($/año)<br><b>C<sub>recurrente</sub></b>: operación, inspección y mantención que se repiten cada año ($/año)', 'Para evitar ambigüedad, la aplicación no usa «beneficio anual neto» como un concepto separado: el dinero que queda después de descontar costos se llama flujo neto anual.')
    st.markdown('<div class="worked-example"><h3>Dos cantidades diferentes</h3><div class="worked-step"><strong>1 · Beneficio anual bruto.</strong> Es todo el ahorro o ganancia generado durante un año, antes de descontar gastos. Se suman los ingresos atribuibles a la solución y los costos que permite evitar: multas, paralizaciones, reclamos, pérdida de productividad, arriendos temporales o reparaciones repetidas.</div><div class="worked-step"><strong>2 · Costos recurrentes anuales.</strong> Son los gastos que se repiten cada año: mantención, inspecciones, reposición de sellos, energía adicional u operación. La inversión inicial se analiza por separado.</div><div class="worked-step"><strong>3 · Flujo neto anual.</strong> Es el dinero que realmente queda disponible cada año. Si el beneficio bruto es $700.000 y los costos recurrentes son $100.000, entonces $700.000 − $100.000 = <b>$600.000/año</b>.</div><div class="worked-result"><b>Lectura del resultado:</b> un flujo positivo aporta recursos para recuperar la inversión; un flujo igual a cero no la recupera; y uno negativo significa que los costos anuales superan los beneficios anuales. El payback se calcula dividiendo la inversión inicial por este flujo positivo.</div></div>', unsafe_allow_html=True)
    formula_card('Payback · tiempo para recuperar la inversión', 'Payback=\\frac{I_0}{F_{\\mathrm{neto,anual}}}', '<b>I₀</b>: inversión inicial ($)<br><b>F<sub>neto,anual</sub></b>: beneficio anual bruto menos costos recurrentes ($/año)', 'Responde una pregunta concreta: ¿cuántos años tardaré en recuperar el dinero invertido? Un payback menor significa recuperación más rápida, pero no informa cuánto se gana después.')
    formula_card('ROI · rentabilidad de la inversión', 'ROI=\\frac{B_{\\mathrm{acumulado}}-C_{\\mathrm{total}}}{C_{\\mathrm{total}}}\\,100', '<b>B acumulado</b>: beneficios obtenidos durante el período analizado ($)<br><b>C total</b>: inversión inicial más todos los costos del mismo período ($)', 'Responde: ¿cuánto gané o perdí, en porcentaje, respecto de todo lo que costó la inversión? ROI positivo = ganancia; 0 % = solo se recuperaron los costos; negativo = pérdida.')
    st.markdown('<div class="worked-example"><h3>Ejemplo resuelto · ¿Qué significan ROI y payback?</h3><div class="worked-step"><strong>1 · Verificación técnica.</strong> Un encapsulamiento cuesta $2.000.000 y cumple la meta acústica. Recién ahora corresponde analizar su economía.</div><div class="worked-step"><strong>2 · Flujo neto anual.</strong> El beneficio anual bruto es $700.000 y la mantención recurrente es $100.000. Flujo neto anual = $700.000 − $100.000 = <b>$600.000/año</b>.</div><div class="worked-step"><strong>3 · Payback.</strong> $2.000.000 ÷ $600.000/año = <b>3,33 años</b>. Significa que al cabo de aproximadamente 3 años y 4 meses se recupera la inversión inicial.</div><div class="worked-step"><strong>4 · ROI a 5 años.</strong> Beneficio acumulado = $700.000 × 5 = $3.500.000. Costo total = $2.000.000 + ($100.000 × 5) = $2.500.000. ROI = ($3.500.000 − $2.500.000) ÷ $2.500.000 × 100 = <b>40 %</b>.</div><div class="worked-result">Interpretación: al terminar los 5 años, el proyecto recuperó todos sus costos y generó un beneficio neto equivalente al 40 % del costo total. El ROI no indica cuándo se recuperó el dinero; ese dato lo entrega el payback.</div></div>', unsafe_allow_html=True)
    st.markdown('### Ejemplos para interpretar los indicadores')
    st.caption('Selecciona una respuesta en cada situación. Los datos son fijos para concentrar la actividad en la interpretación.')
    check('e4_flow', 'Una solución evita costos por $900.000 al año y requiere $150.000 anuales de mantención. ¿Cuál es su flujo anual neto?', ['$750.000/año', '$900.000/año', '$1.050.000/año', '$150.000/año'], '$750.000/año', 'Fneto = Ba − Ca = $900.000 − $150.000 = $750.000 por año.')
    check('e4_payback', 'Una medida cuesta $2.400.000 y genera un flujo anual neto de $600.000. ¿Cuál es su payback?', ['2 años', '4 años', '6 años', '40 %'], '4 años', 'Payback = I₀/Fneto = $2.400.000/$600.000 por año = 4 años.')
    check('e4_roi', 'En cinco años, una solución acumula beneficios por $4.500.000 y costos totales por $3.000.000. ¿Cuál es su ROI?', ['33,3 %', '50 %', '66,7 %', '150 %'], '50 %', 'ROI = (B−C)/C×100 = ($4.500.000−$3.000.000)/$3.000.000×100 = 50 %.')
    check('e4_decision', 'La alternativa A tiene ROI de 70 %, pero alcanza 36 dB. La alternativa B tiene ROI de 35 % y alcanza la meta de 40 dB. ¿Cuál puede recomendarse?', ['Alternativa A, porque tiene mayor ROI', 'Alternativa B, porque primero cumple la meta', 'Promediar dB y ROI', 'Ninguna, porque el ROI debe superar 50 %'], 'Alternativa B, porque primero cumple la meta', 'La suficiencia acústica es el filtro inicial. La rentabilidad solo permite comparar alternativas técnicamente suficientes.')

def _stage5_impl():
    header('ETAPA 5 · APLICACIÓN CONCEPTUAL', 'Decisión técnico-económica', 'Compara alternativas, filtra por suficiencia acústica y encuentra el mejor compromiso.')
    full_matter(5)
    st.markdown('<div class="question-box"><div class="question-label">CASO DE DECISIÓN</div><div class="question-text">¿Cuál de las tres soluciones recomendarías para cumplir el objetivo acústico con el menor costo del ciclo? Revisa la meta fija y los datos de cada alternativa; luego justifica por qué tu elección es técnicamente suficiente antes de compararla económicamente.</div></div>', unsafe_allow_html=True)
    st.caption('Instrucción: la meta y todos los datos son fijos. Analiza la tabla, descarta las soluciones que no cumplen y presenta tu recomendación sin modificar valores.')
    target = 38
    st.info('Objetivo acústico mínimo del caso: **38 dB**')
    fixed = [['Solución A', 32, 1200000, 2640000, 7200000, 172.7, 1.7], ['Solución B', 40, 1900000, 4540000, 13800000, 204.0, 2.0], ['Solución C', 47, 3200000, 7100000, 18750000, 164.1, 3.2]]
    df = pd.DataFrame(fixed, columns=['Solución', 'Aislamiento', 'Inversión', 'Costo ciclo', 'Beneficio acumulado', 'ROI', 'Payback'])
    df['Cumple'] = df['Aislamiento'] >= target
    st.dataframe(df.style.format({'Inversión': '${:,.0f}', 'Costo ciclo': '${:,.0f}', 'Beneficio acumulado': '${:,.0f}', 'ROI': '{:.1f}%', 'Payback': '{:.1f} años'}), use_container_width=True, hide_index=True)
    feasible = df[df.Cumple]
    if feasible.empty:
        st.error('Ninguna alternativa cumple. No corresponde recomendar por precio o ROI.')
    else:
        best = feasible.loc[feasible['Costo ciclo'].idxmin()]
        st.success(f"Entre las alternativas suficientes, {best['Solución']} tiene el menor costo del ciclo. La decisión final debe revisar además bandas críticas, montaje y riesgo.")
    recommendation = st.radio('Selecciona la solución que recomendarías', ['Solución A', 'Solución B', 'Solución C'], index=None, key='s5_table_recommendation', horizontal=True)
    justification = st.text_area('Justifica tu decisión utilizando cumplimiento acústico y costo del ciclo', key='s5_table_justification', placeholder='Ejemplo: descarto… porque no cumple; entre las que cumplen selecciono… porque…')
    if st.button('Comprobar decisión', key='b_s5_table_decision'):
        if recommendation is None:
            st.warning('Selecciona una solución antes de comprobar.')
        elif feasible.empty:
            st.error('Ninguna solución cumple la meta seleccionada. La decisión correcta es rediseñar las alternativas antes de recomendar una.')
        elif recommendation != best['Solución']:
            st.error(f"La recomendación no es la óptima con estos datos. Primero descarta las alternativas que no cumplen y, entre las suficientes, compara el costo del ciclo. La respuesta esperada es {best['Solución']}.")
        elif len(justification.strip()) < 20:
            st.warning(f"{best['Solución']} es la alternativa esperada, pero falta desarrollar la justificación técnica y económica.")
        else:
            st.success(f"Correcto. {best['Solución']} cumple el objetivo y presenta el menor costo del ciclo entre las alternativas suficientes.")
    check('e5', 'Una alternativa tiene excelente ROI, pero no alcanza la meta acústica. ¿Qué corresponde?', ['Elegirla por su ROI', 'Descartarla o rediseñarla antes de comparar economía', 'Promediar ROI y dB'], 'Descartarla o rediseñarla antes de comparar economía', 'La suficiencia técnica precede a la optimización económica.')
    st.markdown('<div class="section-band"><span>🧮</span><h3>Aplicación técnico-económica · responde y comprueba</h3></div>', unsafe_allow_html=True)
    q1 = 'Un ingeniero propone aumentar el aislamiento de una oficina de 40 dB a 50 dB. ¿Qué elementos debería considerar para decidir si esto es una buena inversión?'
    s1 = 'Debe comprobar el nivel actual y la meta, privacidad y uso, espectro de la fuente, cumplimiento, beneficio real de 10 dB, costo del ciclo, factibilidad, puertas, ventanas, juntas y flancos, vida útil, riesgo y rendimiento decreciente. «Más dB» no basta si la mejora no es necesaria o no puede lograrse en obra.'
    formative_development(5, 's5q1', q1, s1, [['meta', 'objetivo', 'norma'], ['costo', 'inversión', 'inversion'], ['puerta', 'ventana', 'fuga', 'flanco'], ['beneficio', 'privacidad', 'confort'], ['factib', 'vida útil', 'vida util', 'riesgo']], 'La decisión debe integrar suficiencia acústica, vías dominantes, costo completo y beneficio útil.')
    q2 = 'Un sistema cuesta $1.200.000 CLP y reduce 30 dB. Otro cuesta $2.400.000 CLP y reduce 38 dB. Calcula el costo por dB de ambos e indica cuál ofrece mayor eficiencia.'
    s2 = 'Sistema 1: $1.200.000/30 = **$40.000 por dB**. Sistema 2: $2.400.000/38 = **$63.158 por dB** aproximadamente. El sistema 1 es más eficiente por este indicador, siempre que alcance la meta acústica.'
    formative_numeric(5, 's5q2', q2, [('a', 'Sistema 1 · CLP/dB', 0.0, 1000.0), ('b', 'Sistema 2 · CLP/dB', 0.0, 1000.0)], lambda v: (abs(v['a'] - 40000) <= 500 and abs(v['b'] - 63157.9) <= 600, 'Los valores esperados son $40.000/dB y aproximadamente $63.158/dB; el menor costo por dB corresponde al sistema 1.'), s2)
    q3 = 'Opción A: inversión $500.000, beneficio $700.000. Opción B: inversión $1.000.000, beneficio $950.000. Calcula el ROI de ambas e identifica la mejor.'
    s3 = 'ROI A = ($700.000−$500.000)/$500.000×100 = **40 %**. ROI B = ($950.000−$1.000.000)/$1.000.000×100 = **−5 %**. La opción A tiene el mejor retorno.'
    formative_numeric(5, 's5q3', q3, [('a', 'ROI A (%)', 0.0, 1.0), ('b', 'ROI B (%)', 0.0, 1.0)], lambda v: (abs(v['a'] - 40) <= 0.2 and abs(v['b'] + 5) <= 0.2, 'Se esperaba ROI A = 40 % y ROI B = −5 %. La alternativa A ofrece el mejor retorno.'), s3)
    score_counter(5)
    teacher_group_review(5, {'s5q1': s1, 's5q2': s2, 's5q3': s3})

def _stage6_impl():
    header('ETAPA 6 · MATERIA + SIMULADORES', 'Fundamentos físicos del aislamiento acústico', 'Masa, frecuencia, transmisión, coincidencia, sistemas dobles, estanqueidad y elementos débiles.')
    full_matter(6)
    tabs = st.tabs(['Transmisión y R', 'Ley de masa', 'Coincidencia', 'Sistemas dobles', 'Elementos compuestos'])
    with tabs[0]:
        formula_card('Coeficiente de transmisión y reducción sonora', '\\tau=\\frac{W_t}{W_i} \\qquad R=10\\log_{10}\\left(\\frac{1}{\\tau}\\right)', '<b>Wₜ</b>: potencia transmitida (W)<br><b>Wᵢ</b>: potencia incidente (W)<br><b>τ</b>: fracción transmitida<br><b>R</b>: reducción sonora (dB)', 'Para relacionar físicamente la energía que atraviesa una separación con su aislamiento por banda.')
        formula_card('Despeje directo del coeficiente de transmisión', '\\tau=10^{-R/10}', '<b>R</b>: reducción sonora (dB)<br><b>τ</b>: fracción adimensional entre 0 y 1', 'Para conocer qué fracción de la energía atraviesa un elemento cuando se dispone de R.')
        R = st.slider('R (dB)', 10, 70, 40, key='r6')
        t = 10 ** (-R / 10)
        st.metric('Fracción de energía transmitida', f'{t:.8f} ({t * 100:.6f} %)')
        st.markdown(f'<div class="worked-example"><h3>¿De dónde sale el porcentaje?</h3><div class="worked-step"><strong>1.</strong> La ecuación entrega una fracción decimal: τ = 10<sup>−{R}/10</sup> = {t:.8f}.</div><div class="worked-step"><strong>2.</strong> Para expresarla como porcentaje se multiplica por 100: {t:.8f} × 100 = <b>{t * 100:.6f} %</b>.</div><div class="worked-result">Este porcentaje corresponde a energía transmitida, no a porcentaje de superficie.</div></div>', unsafe_allow_html=True)
        st.info('Ejemplo: R = 40 dB → τ = 10⁻⁴ = 0,0001. Solo se transmite 0,01 % de la energía incidente.')
        check('e6_tau_practical', 'Si R = 30 dB, ¿qué porcentaje de energía se transmite?', ['0,001 %', '0,01 %', '0,1 %', '3 %'], '0,1 %', 'τ = 10⁻³ = 0,001; al multiplicar por 100 se obtiene 0,1 %.')
    with tabs[1]:
        formula_card('Ley de masa ideal para una hoja simple', "R\\approx20\\log_{10}(m'f)-47", '<b>m′</b>: masa superficial (kg/m²)<br><b>f</b>: frecuencia (Hz)<br><b>R</b>: reducción sonora (dB)', 'Aproximación de campo difuso en la región controlada por masa, lejos de resonancias, coincidencia, fugas y flancos.')
        m = st.slider('Masa superficial m′ (kg/m²)', 5, 150, 25)
        curve = mass_r(m, FREQS)
        curve2 = mass_r(2 * m, FREQS)
        line_chart(FREQS, [('m′', curve), ('2·m′', curve2)], 'Ley de masa ideal', 'R (dB)')
        st.info('Duplicar masa o frecuencia aumenta aproximadamente 6 dB en la región ideal de ley de masa.')
    with tabs[2]:
        formula_card('Frecuencia crítica de una placa', "f_c=\\frac{c^2}{2\\pi}\\sqrt{\\frac{m'}{D}}\\qquad D=\\frac{Eh^3}{12(1-\\nu^2)}", '<b>c</b>: velocidad del sonido (m/s)<br><b>m′</b>: masa superficial (kg/m²)<br><b>D</b>: rigidez flexional (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor (m)<br><b>ν</b>: coeficiente de Poisson', 'Para estimar la banda donde la coincidencia puede producir una caída del aislamiento de una placa homogénea.')
        fc = st.slider('Frecuencia crítica estimada (Hz)', 100, 3150, 800)
        ideal = mass_r(25, FREQS)
        dip = ideal - 12 * np.exp(-0.5 * (np.log(FREQS / fc) / 0.24) ** 2)
        line_chart(FREQS, [('Ley de masa ideal', ideal), ('Con coincidencia', dip)], 'Efecto didáctico de coincidencia', 'R (dB)')
        st.warning('Cerca de fᶜ el panel radia con mayor eficiencia y puede aparecer una caída de aislamiento.')
    with tabs[3]:
        gap = st.slider('Cámara (mm)', 20, 300, 80)
        absorb = st.checkbox('Absorbente en cámara', True)
        gain = 8 + min(gap / 30, 8) + (5 if absorb else 0)
        st.metric('Mejora didáctica sobre hoja simple', f'{gain:.1f} dB')
        st.caption('El desempeño real depende de masas, rigidez de uniones, frecuencia masa–aire–masa y puentes estructurales.')
    with tabs[4]:
        formula_card('Aislamiento de elementos compuestos', '\\tau_{\\mathrm{total}}=\\frac{\\sum_i S_i\\tau_i}{\\sum_i S_i}\\qquad R_{\\mathrm{total}}=-10\\log_{10}(\\tau_{\\mathrm{total}})', '<b>Sᵢ</b>: área del elemento i (m²)<br><b>τᵢ=10^{-Rᵢ/10}</b>: coeficiente de transmisión de cada elemento', 'Para combinar un muro con puertas, ventanas u otros componentes. Los aislamientos en dB no se promedian.')
        st.markdown('#### Aplicación práctica · muro con puerta')
        st.write('Datos fijos: muro de **4,0 m × 3,0 m** (12 m²), puerta de **1,0 m × 2,0 m** (2 m²), R del paño de muro = **55 dB** y R de la puerta = **25 dB**.')
        total_area = 12.0
        weak_area = 2.0
        share = weak_area / total_area
        wall_area = total_area - weak_area
        main_partition = 55
        door = 25
        tau = (wall_area * 10 ** (-main_partition / 10) + weak_area * 10 ** (-door / 10)) / total_area
        comp = -10 * np.log10(tau)
        st.markdown('<div class="worked-example"><h3>Cálculo del porcentaje de área débil</h3><div class="worked-step"><strong>1 · Área total del cerramiento.</strong> 4,0 × 3,0 = <b>12 m²</b>.</div><div class="worked-step"><strong>2 · Área de la puerta.</strong> 1,0 × 2,0 = <b>2 m²</b>.</div><div class="worked-step"><strong>3 · Porcentaje débil.</strong> (Sdébil/Stotal) × 100 = (2/12) × 100 = <b>16,7 %</b>.</div><div class="worked-result">En la ecuación se usa la fracción 2/12 = 0,1667. El área útil del muro es 12−2 = 10 m²; la puerta no se suma nuevamente al total.</div></div>', unsafe_allow_html=True)
        st.metric('R compuesto', f'{comp:.1f} dB')
        st.info('Los dB no se promedian: se combinan coeficientes de transmisión ponderados por superficie.')
        st.markdown('<div class="good"><b>Comprobación geométrica:</b> la puerta representa <b>16,7 %</b> del cerramiento, porque (2 m²/12 m²)×100 = 16,7 %. La fracción que se utiliza en la ecuación es 2/12 = 0,1667.</div>', unsafe_allow_html=True)
        check('e6_comp_practical', f'Al combinar energéticamente ambos elementos, el resultado es aproximadamente {comp:.1f} dB. ¿Por qué queda mucho más cerca de la puerta que del muro?', ['Porque se promediaron 55 y 25 dB', 'Porque la puerta tiene un τ mucho mayor y domina la energía transmitida', 'Porque la puerta ocupa más superficie que el muro'], 'Porque la puerta tiene un τ mucho mayor y domina la energía transmitida', 'Aunque solo ocupa 16,7 % del área, la puerta transmite mucha más energía por metro cuadrado. Por eso los coeficientes τ se ponderan por superficie.')
    check('e6', 'Si se duplica la masa superficial de un panel dentro de la región ideal de la ley de masa, ¿qué mejora aproximada se espera?', ['3 dB', '6 dB', '10 dB', 'El aislamiento no cambia'], '6 dB', 'La ley de masa ideal predice aproximadamente 6 dB de aumento de R al duplicar la masa superficial, para una misma frecuencia.')

def _stage7_impl():
    header('ETAPA 7 · APLICACIÓN PRÁCTICA', 'Diseño de aislamiento acústico', 'Aplica las ecuaciones de la etapa anterior siguiendo una ruta de cálculo clara y verificable.')
    full_matter(7)
    st.markdown('<div class="question-box"><div class="question-label">CASO GUIADO · MURO CON PUERTA</div><div class="question-text">Una sala emisora tiene 82 dB. La separación mide 15 m² e incorpora una puerta de 2 m². El muro tiene R = 50 dB y la puerta R = 30 dB. Calcula el área débil, el aislamiento compuesto y el nivel estimado en el receptor. Luego decide si cumple la meta de 45 dB.</div></div>', unsafe_allow_html=True)
    st.caption('Todos los datos son fijos. Resuelve cada paso y comprueba antes de continuar.')
    source = 82.0
    target = 45.0
    total_area = 15.0
    weak_area = 2.0
    wall_area = total_area - weak_area
    r_wall = 50.0
    r_weak = 30.0
    weak_pct = 100 * weak_area / total_area
    tau_wall = 10 ** (-r_wall / 10)
    tau_weak = 10 ** (-r_weak / 10)
    tau_total = (wall_area * tau_wall + weak_area * tau_weak) / total_area
    r_total = -10 * math.log10(tau_total)
    receiver = source - r_total
    case_df = pd.DataFrame([['Nivel emisor', f'{source:.0f} dB'], ['Área total', f'{total_area:.0f} m²'], ['Área de puerta', f'{weak_area:.0f} m²'], ['Área efectiva de muro', f'{wall_area:.0f} m²'], ['R muro', f'{r_wall:.0f} dB'], ['R puerta', f'{r_weak:.0f} dB'], ['Meta en receptor', f'≤ {target:.0f} dB']], columns=['Dato', 'Valor'])
    st.dataframe(case_df, hide_index=True, use_container_width=True)
    st.markdown('<div class="worked-example"><h3>Origen de las áreas y porcentajes</h3><div class="worked-step">El área total de 15 m² corresponde a toda la separación, incluida la puerta.</div><div class="worked-step">Área efectiva del muro = 15−2 = <b>13 m²</b>.</div><div class="worked-step">Porcentaje de puerta = (2/15)×100 = <b>13,3 %</b>. En la ecuación se usa 2/15 = 0,1333.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="good"><b>Resultado del paso geométrico:</b> la puerta ocupa <b>13,3 %</b> de la separación, porque (2 m²/15 m²)×100 = 13,3 %. Este porcentaje proviene de las áreas del caso y no es un dato supuesto.</div>', unsafe_allow_html=True)
    formula_card('Combinación energética del muro y la puerta', '\\tau_i=10^{-R_i/10}\\qquad\\tau_{\\mathrm{total}}=\\frac{S_{\\mathrm{muro}}\\tau_{\\mathrm{muro}}+S_{\\mathrm{puerta}}\\tau_{\\mathrm{puerta}}}{S_{\\mathrm{total}}}\\qquad R_{\\mathrm{total}}=-10\\log_{10}(\\tau_{\\mathrm{total}})', '<b>Rᵢ</b>: reducción sonora de cada elemento (dB)<br><b>τᵢ</b>: coeficiente de transmisión de cada elemento (adimensional)<br><b>S<sub>muro</sub></b>: área efectiva del muro = 13 m²<br><b>S<sub>puerta</sub></b>: área de la puerta = 2 m²<br><b>S<sub>total</sub></b>: área total de la separación = 15 m²', 'Para combinar elementos con aislamientos diferentes. Los valores de R en dB no se promedian; primero deben convertirse a coeficientes τ y ponderarse por área.')
    check('e7_guided_tau', '¿Qué coeficientes de transmisión corresponden al muro y a la puerta?', ['τmuro=10⁻⁵ y τpuerta=10⁻³', 'τmuro=50 y τpuerta=30', 'τmuro=0,50 y τpuerta=0,30'], 'τmuro=10⁻⁵ y τpuerta=10⁻³', 'Se aplica τ=10^(−R/10): para 50 dB resulta 10⁻⁵ y para 30 dB resulta 10⁻³.')
    st.latex(f'\\tau_{{total}}=\\frac{{13(10^{{-5}})+2(10^{{-3}})}}{{15}}={tau_total:.6f}')
    st.latex(f'R_{{total}}=-10\\log_{{10}}(\\tau_{{total}})={r_total:.1f}\\ \\mathrm{{dB}}')
    formula_card('Diferencia de nivel y estimación del nivel receptor', '\\begin{aligned}\\Delta L &= L_{\\mathrm{emisor}}-L_{\\mathrm{receptor}}\\\\L_{\\mathrm{receptor}} &\\approx L_{\\mathrm{emisor}}-R_{\\mathrm{total}}\\end{aligned}', f'<b>ΔL</b>: diferencia entre el nivel emisor y el nivel receptor (dB)<br><b>L<sub>emisor</sub></b>: nivel en la sala emisora = 82 dB<br><b>L<sub>receptor</sub></b>: nivel estimado en la sala receptora (dB)<br><b>R<sub>total</sub></b>: aislamiento compuesto calculado = {r_total:.1f} dB', 'En este ejercicio simplificado se considera que la reducción producida por la separación es aproximadamente igual a la diferencia de nivel. Por eso se resta Rtotal al nivel emisor. En una medición normalizada real también deben considerarse la geometría y las condiciones acústicas del recinto receptor.')
    st.latex(f'L_{{\\mathrm{{receptor}}}}\\approx 82-{r_total:.1f}={receiver:.1f}\\ \\mathrm{{dB}}')
    check('e7_guided_result', f'Con Rtotal ≈ {r_total:.1f} dB, ¿cuál es el nivel receptor estimado y cumple la meta?', [f'{receiver:.1f} dB; sí cumple', f'{receiver:.1f} dB; no cumple', '32,0 dB; sí cumple', '52,0 dB; no cumple'], f'{receiver:.1f} dB; sí cumple', f'En esta estimación simplificada, ΔL ≈ Rtotal y Lreceptor = 82−{r_total:.1f} = {receiver:.1f} dB. Como es menor o igual que 45 dB, el caso cumple.')
    st.markdown('<div class="good"><b>Lectura profesional:</b> el procedimiento siempre sigue la misma ruta: áreas → porcentajes → τ de cada elemento → τ ponderado → R compuesto → diferencia de nivel estimada → nivel receptor → comparación con la meta.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>🧪</span><h3>Aplicación conceptual III · 11 ejercicios</h3></div>', unsafe_allow_html=True)
    solutions = {}
    q = 'En un ensayo simplificado, el nivel medio en el recinto emisor es 85 dB y en el receptor es 45 dB. Sin aplicar correcciones de recinto, calcula R.'
    s = 'Aplicación simplificada: **R = L₁ − L₂ = 85 − 45 = 40 dB**. En un ensayo normalizado real se incorporan las correcciones y condiciones definidas por el método.'
    formative_numeric(7, 's7q1', q, [('r', 'R (dB)', 0.0, 1.0)], lambda v: (abs(v['r'] - 40) < 0.1, 'R debe ser 40 dB: resta nivel receptor al nivel emisor.'), s)
    solutions['s7q1'] = s
    q = 'Para un elemento con R = 40 dB, calcula el coeficiente de transmisión τ.'
    s = '**τ = 10^(−R/10) = 10⁻⁴ = 0,0001**, equivalente a 0,01 % de la energía incidente.'
    formative_numeric(7, 's7q2', q, [('tau', 'τ', 0.0, 0.0001)], lambda v: (abs(v['tau'] - 0.0001) <= 1e-05, 'τ debe ser 0,0001.'), s)
    solutions['s7q2'] = s
    q = 'Aplica la ley de masa ideal para m′ = 30 kg/m² y f = 500 Hz. Calcula R.'
    expected = 20 * math.log10(30 * 500) - 47
    s = f'**R ≈ 20 log₁₀(30×500) − 47 = {expected:.1f} dB**. Es una aproximación válida solo en la región controlada por masa.'
    formative_numeric(7, 's7q3', q, [('r', 'R (dB)', 0.0, 0.1)], lambda v: (abs(v['r'] - expected) <= 0.3, f'El resultado esperado es aproximadamente {expected:.1f} dB.'), s)
    solutions['s7q3'] = s
    st.markdown('#### Ejercicio guiado · Rigidez flexional y frecuencia crítica')
    formula_card('Ecuaciones que debes aplicar', "\\begin{aligned}D&=\\frac{Eh^3}{12(1-\\nu^2)}\\\\[0.65em]f_c&=\\frac{c^2}{2\\pi}\\sqrt{\\frac{m'}{D}}\\end{aligned}", '<b>D</b>: rigidez flexional de la placa (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor de la placa (m)<br><b>ν</b>: coeficiente de Poisson (adimensional)<br><b>f<sub>c</sub></b>: frecuencia crítica o de coincidencia (Hz)<br><b>c</b>: velocidad del sonido en el aire (m/s)<br><b>m′</b>: masa superficial de la placa (kg/m²)', 'Primero calcula D con todas las magnitudes en el Sistema Internacional. Después utiliza ese resultado en la ecuación de fᶜ.')
    st.markdown('<div class="worked-example"><h3>Preparación de los datos</h3><div class="worked-step"><strong>Módulo de Young:</strong> E = 2,5 GPa = <b>2,5×10⁹ Pa</b>.</div><div class="worked-step"><strong>Espesor:</strong> h = 12 mm = <b>0,012 m</b>.</div><div class="worked-step"><strong>Datos que ya están en SI:</strong> ν = 0,30; m′ = 9,6 kg/m²; c = 343 m/s.</div><div class="worked-result">Ruta de cálculo: convertir unidades → calcular D → calcular fᶜ → interpretar el resultado.</div></div>', unsafe_allow_html=True)
    q = 'Una placa tiene E = 2,5 GPa, h = 12 mm, ν = 0,30, m′ = 9,6 kg/m² y c = 343 m/s. Calcula primero la rigidez flexional D y después la frecuencia crítica fᶜ.'
    s = 'Con unidades SI: **D = Eh³/[12(1−ν²)] = 395,6 N·m**. Luego, **fᶜ = c²/(2π)√(m′/D) ≈ 2.917 Hz**. Cerca de esa frecuencia puede producirse el fenómeno de coincidencia: la placa radia con mayor eficiencia y aparece una disminución o valle en su aislamiento.'
    formative_numeric(7, 's7q4', q, [('d', 'D (N·m)', 0.0, 1.0), ('fc', 'fᶜ (Hz)', 0.0, 10.0)], lambda v: (abs(v['d'] - 395.6) <= 3 and abs(v['fc'] - 2917) <= 25, 'Se esperaba D ≈ 395,6 N·m y fᶜ ≈ 2.917 Hz. Verifica convertir 12 mm a 0,012 m.'), s)
    solutions['s7q4'] = s
    check('s7q4_interpretation', '¿Qué puede ocurrir con el aislamiento de la placa cerca de su frecuencia crítica fᶜ?', ['Puede disminuir y formar un valle por el fenómeno de coincidencia', 'Aumenta siempre 6 dB, sin importar el material', 'La placa deja de transmitir completamente', 'Solo cambia el tiempo de reverberación del recinto'], 'Puede disminuir y formar un valle por el fenómeno de coincidencia', 'Cerca de fᶜ aumenta la eficiencia de acoplamiento y radiación de la placa, por lo que el aislamiento puede presentar una caída.')
    q = 'Un recinto posee 60 m² de superficie con α = 0,10 y agrega 25 m² de material con α = 0,80. Calcula la absorción equivalente total.'
    s = '**A = 60×0,10 + 25×0,80 = 6 + 20 = 26 m² sabin**.'
    formative_numeric(7, 's7q5', q, [('a', 'A total (m² sabin)', 0.0, 1.0)], lambda v: (abs(v['a'] - 26) < 0.1, 'La absorción equivalente total es 26 m² sabin.'), s)
    solutions['s7q5'] = s
    q = 'Compara dos ventanas: A tiene Rw = 40 dB y B tiene Rw = 35 dB. ¿Cuál transmite menos energía y cuántas veces difieren aproximadamente sus coeficientes τ?'
    s = 'La ventana A transmite menos. Una diferencia de 5 dB corresponde a una razón de transmisión de **10^(5/10) ≈ 3,16**: B transmite aproximadamente 3,16 veces más energía que A.'
    formative_development(7, 's7q6', q, s, [['a', '40'], ['menos', 'menor'], ['3,16', '3.16', 'tres']], 'No compares los dB como una razón lineal: convierte la diferencia mediante 10^(ΔR/10).')
    solutions['s7q6'] = s
    q = '¿Qué ocurre idealmente con R cuando se duplica la masa superficial de una hoja simple?'
    s = 'En la región ideal controlada por masa, **R aumenta aproximadamente 6 dB**. No es una regla universal cerca de resonancias, coincidencia, fugas o flancos.'
    formative_development(7, 's7q7', q, s, [['6', 'seis'], ['masa'], ['ideal', 'coincid', 'resonan', 'aproxim']], 'Indica tanto la mejora aproximada como las condiciones que limitan la ley de masa.')
    solutions['s7q7'] = s
    q = '¿Qué función cumple la lana mineral dentro de un tabique de doble hoja?'
    s = 'Absorbe y amortigua la energía dentro de la cámara, reduce la severidad de resonancias y mejora el sistema. **No aporta aislamiento por sí sola ni sustituye el desacoplamiento**, la masa o el sellado.'
    formative_development(7, 's7q8', q, s, [['absor', 'amort'], ['cámara', 'camara', 'resonan'], ['no', 'desacopl', 'masa']], 'Evita atribuirle a la lana mineral toda la capacidad aislante del tabique.')
    solutions['s7q8'] = s
    q = 'Un muro de alto aislamiento incorpora una ventana pequeña de bajo R. ¿Cómo puede afectar esa ventana al aislamiento global?'
    s = 'Puede dominar el resultado global porque su τ es mucho mayor que el del muro. Se deben combinar los coeficientes de transmisión ponderados por área; **no se promedian los dB**.'
    formative_development(7, 's7q9', q, s, [['domina', 'reduce', 'debil'], ['coeficiente', 'tau', 'transmis'], ['área', 'area'], ['no', 'promedi']], 'Explica por qué una superficie pequeña puede transportar una fracción grande de la energía.')
    solutions['s7q9'] = s
    q = 'El muro separador fue mejorado, pero el ruido sigue llegando por la unión con el cielo y el piso. ¿Qué fenómeno ocurre y cómo se aborda?'
    s = 'Existe **transmisión indirecta o por flancos**. Deben diagnosticarse los encuentros y vías estructurales, controlar continuidades rígidas, sellar pasos y diseñar el conjunto constructivo, no solo el paño separador.'
    formative_development(7, 's7q10', q, s, [['flanco', 'indirect'], ['cielo', 'piso', 'encuentro'], ['vía', 'via', 'estructura', 'sell']], 'Nombra la trayectoria real y propone una intervención sobre ese encuentro.')
    solutions['s7q10'] = s
    q = 'Un muro de 12 m² tiene R = 55 dB e incorpora una puerta de 2 m² con R = 25 dB. Calcula el R compuesto.'
    tau_total = (12 * 10 ** (-55 / 10) + 2 * 10 ** (-25 / 10)) / 14
    r_total = -10 * math.log10(tau_total)
    s = f'τtotal = [12·10^(−55/10)+2·10^(−25/10)]/14. Por tanto, **Rtotal ≈ {r_total:.1f} dB**. La puerta reduce drásticamente el desempeño del conjunto.'
    formative_numeric(7, 's7q11', q, [('r', 'R compuesto (dB)', 0.0, 0.1)], lambda v: (abs(v['r'] - r_total) <= 0.3, f'El resultado esperado es aproximadamente {r_total:.1f} dB; combina τ ponderados por superficie.'), s)
    solutions['s7q11'] = s
    score_counter(7)
    teacher_group_review(7, solutions)

def _stage8_impl():
    header('ETAPA 8 · MATERIA + INTERPRETACIÓN', 'Índices de aislamiento acústico', 'Los números únicos permiten comparar, pero deben corresponder al método, lugar y espectro del problema.')
    full_matter(8)
    data = [('R(f)', 'Reducción por banda', 'Laboratorio/curva'), ('Rw', 'Reducción ponderada', 'Laboratorio ISO'), ('R′w', 'Reducción aparente', 'Terreno, incluye vías laterales'), ('DₙT,w', 'Diferencia estandarizada', 'Entre recintos, corregida por T'), ('D₂m,nT,w', 'Diferencia de fachada', 'Exterior a 2 m'), ('STC / ASTC', 'Clasificación ASTM', 'Laboratorio / terreno'), ('OITC', 'Exterior–interior', 'Transporte y bajas frecuencias'), ('CAC', 'Paso por cielo/plenum', 'Cielos suspendidos')]
    st.dataframe(pd.DataFrame(data, columns=['Indicador', 'Representa', 'Contexto']), hide_index=True, use_container_width=True)
    formula_card('Índice ponderado y términos de adaptación', 'R_w(C;C_{tr})=52(-2;-7)\\,\\mathrm{dB}\\Rightarrow R_w+C=50\\,\\mathrm{dB},\\;R_w+C_{tr}=45\\,\\mathrm{dB}', '<b>Rw</b>: valor ponderado ISO<br><b>C</b>: adaptación para espectros medios-altos<br><b>Ctr</b>: adaptación para tránsito y contenido grave', 'Para adaptar el índice global al espectro de la fuente. C y Ctr se suman algebraicamente; no son aislamientos independientes.')
    source = st.selectbox('Fuente a evaluar', ['Voz / actividades domésticas', 'Tránsito, buses o bajos', 'Fachada bajo criterio ASTM', 'Fuente tonal industrial'])
    recommendation = {'Voz / actividades domésticas': 'Revisar Rw y Rw+C.', 'Tránsito, buses o bajos': 'Priorizar Rw+Cₜᵣ y la curva grave.', 'Fachada bajo criterio ASTM': 'Revisar OITC además de STC.', 'Fuente tonal industrial': 'La curva completa en la banda tonal es indispensable.'}[source]
    st.info(recommendation)
    check('e8', 'Un tabique tiene Rw=55 dB en laboratorio y R′w=47 dB en obra. ¿El laboratorio estaba necesariamente equivocado?', ['Sí', 'No; montaje y vías laterales pueden explicar la diferencia'], 'No; montaje y vías laterales pueden explicar la diferencia', 'R′w incorpora el comportamiento aparente de la construcción instalada.')

def _stage9_impl():
    header('ETAPA 9 · APLICACIÓN PRÁCTICA', 'Interpretación de índices acústicos', 'Relaciona cada índice con su definición, contexto de medición y uso correcto.')
    full_matter(9)
    st.markdown('### Actividad · Relaciona los términos pareados')
    st.markdown('En la columna izquierda aparecen los índices acústicos. En la derecha están las definiciones numeradas y mezcladas. Selecciona junto a cada índice el número que le corresponde.')
    paired_terms = {'R': 'Índice por banda de frecuencia que expresa la reducción sonora de un elemento en laboratorio.', 'R_w': 'Índice único ponderado ISO obtenido al ajustar una curva de referencia a resultados de laboratorio.', 'R′_w': 'Índice único aparente medido en obra, que incorpora montaje, encuentros y transmisiones laterales.', 'D_nT,w': 'Diferencia de niveles entre recintos, normalizada por el tiempo de reverberación y ponderada.', 'D_2m,nT,w': 'Diferencia de niveles de fachada medida con el nivel exterior a 2 m, normalizada y ponderada.', 'C': 'Término de adaptación espectral asociado principalmente a ruido rosa y fuentes de contenido medio-alto.', 'Cₜᵣ': 'Término de adaptación espectral apropiado para tránsito y fuentes con contenido importante en bajas frecuencias.', 'STC': 'Clasificación ASTM de número único usada principalmente para particiones interiores.', 'OITC': 'Clasificación ASTM orientada al aislamiento frente a ruido exterior, especialmente transporte.', 'CAC': 'Clasificación del aislamiento entre recintos que comparten un cielo suspendido y plenum.'}
    definitions = list(paired_terms.values())
    mixed_order = [7, 2, 5, 0, 8, 3, 9, 1, 6, 4]
    numbered_definitions = {number: definitions[source_index] for number, source_index in enumerate(mixed_order, 1)}
    correct_numbers = {term: next((number for number, definition in numbered_definitions.items() if definition == correct_definition)) for term, correct_definition in paired_terms.items()}
    placeholder = '—'
    selections = {}
    left, right = st.columns([0.85, 2.15], gap='large')
    with left:
        st.markdown('#### Índices o descriptores')
        for idx, term in enumerate(paired_terms):
            row_label, row_value = st.columns([1.2, 0.8])
            row_label.markdown(f'**{term}**')
            selections[term] = row_value.selectbox(f'Número para {term}', [placeholder] + list(range(1, 11)), key=f'e9_pair_number_{idx}', label_visibility='collapsed')
    with right:
        st.markdown('#### Definiciones numeradas')
        for number, definition in numbered_definitions.items():
            st.markdown(f'<div class="card" style="margin:.28rem 0;padding:.72rem .9rem"><b style="color:#0871bd">{number}.</b> {definition}</div>', unsafe_allow_html=True)
    if st.button('Comprobar términos pareados', key='e9_check_pairs', type='primary'):
        unanswered = [term for term, value in selections.items() if value == placeholder]
        if unanswered:
            st.warning(f"Completa todas las relaciones. Faltan: {', '.join(unanswered)}.")
        else:
            correct_count = sum((selections[term] == correct_numbers[term] for term in paired_terms))
            pair_score = correct_count * 2
            level = 'Correcta' if correct_count == len(paired_terms) else 'Parcialmente correcta' if correct_count >= 4 else 'Incorrecta'
            _save_formative(9, 'e9_pairs', 'Relaciona cada índice acústico con su definición.', json.dumps(selections, ensure_ascii=False), level, f'{correct_count} de {len(paired_terms)} relaciones correctas.', score=pair_score, max_score=20)
            if correct_count == len(paired_terms):
                st.success('¡Correcto! Relacionaste adecuadamente los 10 términos acústicos.')
            else:
                st.warning(f'Obtuviste {correct_count} de {len(paired_terms)} relaciones correctas.')
                for term, correct_definition in paired_terms.items():
                    if selections[term] != correct_numbers[term]:
                        st.error(f'{term}: la relación seleccionada no corresponde. El número correcto es {correct_numbers[term]}: {correct_definition}', icon='↔️')
            repeated = {number for number in range(1, 11) if list(selections.values()).count(number) > 1}
            if repeated:
                st.info(f"Revisa los números repetidos ({', '.join(map(str, sorted(repeated)))}): cada definición se utiliza una sola vez.")
    score_counter(9)
    if st.session_state.get('role') == 'Docente':
        with st.expander('👩\u200d🏫 Pauta docente · Términos pareados'):
            st.markdown('Proyecte primero las relaciones sin revelar la pauta. Pida que el curso justifique especialmente las diferencias entre laboratorio, obra, recintos y fachada.')
            if st.checkbox('Mostrar solución de términos pareados', key='e9_reveal_pairs'):
                st.dataframe(pd.DataFrame([{'Término': term, 'N.º correcto': correct_numbers[term], 'Definición correcta': definition} for term, definition in paired_terms.items()]), hide_index=True, use_container_width=True)
                st.info('Tip técnico: la prima en R′w identifica desempeño aparente en obra; el subíndice 2m identifica fachada; nT indica normalización por reverberación. C y Cₜᵣ no son índices independientes: se suman algebraicamente a Rw.')
        teacher_group_review(9, {'e9_pairs': 'Cada uno de los 10 términos debe asociarse una sola vez con la definición mostrada en la pauta docente.'})

def _lab1_final_submission_impl():
    """Return the student's definitive Lab 1 submission, if it exists."""
    client=_supabase()
    user_key=st.session_state.get('user_key')
    if client is None or not user_key:
        return None
    try:
        rows=(client.table('responses').select('*')
              .eq('class_id',CLASS_ID).eq('user_key',user_key)
              .eq('stage',10).eq('question_key','final_exam')
              .limit(1).execute().data or [])
    except Exception:
        return None
    if not rows:
        return None
    row=rows[0]
    payload=_stage9_answer_payload(row)
    return {'row':row,'payload':payload if isinstance(payload,dict) else {}}

def _lab1_case_score_impl(calc,diff,pct,bands,choice,justification):
    practical=0
    practical += 3 if abs(float(calc)-0.4025)<=0.03 else 0
    practical += 2 if set(bands or [])=={125,250,500} else 0
    practical += 3 if choice=='Solución B' else 0
    practical += 2 if abs(float(diff)-300000)<=10000 else 0
    practical += 2 if abs(float(pct)-16.7)<=0.5 else 0
    words=str(justification or '').lower()
    practical += 4 if all(k in words for k in ['costo','125']) else 2 if words.strip() else 0
    practical += 4 if any(k in words for k in ['vida útil','cumple','objetivo','grave','250']) else 0
    return min(20,practical)

def _finish_lab1_final_impl(reason='submitted'):
    answers=dict(st.session_state.get('lab1_final_answers',{}))
    answers={str(i):answers.get(str(i)) for i in range(29)}
    answer_indexes={}
    hits=0
    for i,(_,options,correct) in enumerate(LAB1_QUESTIONS):
        selected=answers[str(i)]
        answer_indexes[str(i)]=options.index(selected) if selected in options else None
        hits += int(selected==options[correct])
    practical=_lab1_case_score_impl(
        st.session_state.get('case_calc',0),st.session_state.get('case_diff',0),
        st.session_state.get('case_pct',0),st.session_state.get('case_bands',[]),
        st.session_state.get('case_choice'),st.session_state.get('case_justification',''),
    )
    theory_score=hits/29*80
    total=theory_score+practical
    payload={
        'respuestas_teoricas':answer_indexes,'respuestas_texto':answers,
        'aciertos_teoricos':hits,'puntaje_teorico':theory_score,
        'puntaje_caso':practical,'reason':reason,'finished_at':_now(),
        'caso_integrador':{
            'volumen':st.session_state.get('case_V',50.0),
            'absorcion':st.session_state.get('case_A',20.0),
            't60':st.session_state.get('case_calc',0),
            'diferencia_costo':st.session_state.get('case_diff',0),
            'incremento_porcentual':st.session_state.get('case_pct',0),
            'bandas_criticas':st.session_state.get('case_bands',[]),
            'recomendacion':st.session_state.get('case_choice'),
            'justificacion':st.session_state.get('case_justification',''),
        },
    }
    _save_formative(
        10,'final_exam','Evaluación final del Curso 1',
        json.dumps(payload,ensure_ascii=False),
        'Correcta' if total>=60 else 'Incorrecta',
        f'Teoría: {hits}/29 aciertos ({theory_score:.1f}/80). Caso práctico: {practical}/20 puntos.',
        score=total,max_score=100,
        correct_answer=('Pauta: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; '
                        'bandas 125, 250 y 500 Hz; Solución B.'),
    )
    st.session_state['lab1_exam_submitted']=True
    st.session_state['exam_result']=(hits,practical,total)
    save_user_progress()

def _stage10_impl():
    header('ETAPA 10 · EVALUACIÓN FINAL', 'Evaluación práctica final · Aislamiento a Ruido Aéreo', '30 preguntas: 29 teórico-aplicadas y un caso integrador con costo-beneficio.')
    full_matter(10)
    if st.session_state.get('role')=='Docente':
        st.info('Vista docente: pauta de consulta. El docente no desarrolla esta evaluación.')
        for i,(question,options,correct) in enumerate(LAB1_QUESTIONS):
            with st.expander(f'Pregunta {i+1} · {question}',expanded=i==0):
                for option_index,option in enumerate(options):
                    st.write(f"{'✅' if option_index==correct else '○'} {chr(65+option_index)}. {option}")
        st.markdown('### Respuestas y rúbrica de alumnos')
        _teacher_lab1_final_results()
        return

    remote=_lab1_final_submission_impl()
    if remote or st.session_state.get('lab1_exam_submitted'):
        payload=(remote or {}).get('payload',{})
        row=(remote or {}).get('row',{})
        answers=payload.get('respuestas_teoricas',{})
        hits=int(payload.get('aciertos_teoricos',0) or 0)
        practical=float(payload.get('puntaje_caso',0) or 0)
        total=float(row.get('auto_score',hits/29*80+practical) or 0)
        st.success(f'Evaluación enviada y guardada · Puntaje: {total:.1f}/100')
        st.caption('El intento está cerrado. Tus respuestas permanecen disponibles al cerrar sesión o volver a ingresar.')
        with st.expander('Revisar respuestas 1 a 29'):
            for i,(question,options,correct) in enumerate(LAB1_QUESTIONS):
                raw=answers.get(str(i),answers.get(i)) if isinstance(answers,dict) else None
                try: selected=int(raw) if raw is not None else None
                except (TypeError,ValueError): selected=None
                chosen=options[selected] if selected is not None and 0<=selected<len(options) else 'Sin respuesta'
                st.markdown(f"**{'✅' if selected==correct else '❌'} {i+1}. {question}**")
                st.write(f'Tu respuesta: {chosen}')
                st.caption(f'Respuesta correcta: {options[correct]}')
        st.info('Pauta del caso: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; bandas 125, 250 y 500 Hz; Solución B.')
        return

    tab1, tab2 = st.tabs(['Preguntas 1 a 29', 'Pregunta 30 · Caso práctico'])
    with tab1:
        # Keep every answer in a durable dictionary. Only one radio widget is
        # rendered at a time, and Streamlit removes hidden widget keys when the
        # student changes question; the dictionary must therefore be the source
        # of truth for progress and Supabase persistence.
        if not isinstance(st.session_state.get('lab1_final_answers'),dict):
            # Migrate any answer saved by APP 112-114 under the former q0..q28
            # widget keys, so the student's existing progress is not discarded.
            st.session_state['lab1_final_answers']={
                str(i):st.session_state.get(f'q{i}')
                for i in range(29) if st.session_state.get(f'q{i}') is not None
            }
        draft_answers=st.session_state['lab1_final_answers']
        qn = st.selectbox('Pregunta', range(29), format_func=lambda i: f'Pregunta {i + 1}')
        q, opts, correct = LAB1_QUESTIONS[qn]
        st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA {qn + 1} DE 29</div><div class="question-text">{q}</div></div>', unsafe_allow_html=True)
        saved_answer=draft_answers.get(str(qn))
        radio_index=opts.index(saved_answer) if saved_answer in opts else None
        ans = st.radio('Selecciona una alternativa', opts, index=radio_index,
                       key=f'_lab1_visible_q{qn}', label_visibility='collapsed')
        if st.button('Guardar respuesta', key=f'save{qn}'):
            if ans is None:
                st.warning('Selecciona una alternativa.')
            else:
                draft_answers[str(qn)]=ans
                st.session_state['lab1_final_answers']=draft_answers
                save_user_progress()
                st.success('Respuesta guardada.')
        answered=sum(draft_answers.get(str(i)) is not None for i in range(29))
        hits=sum(draft_answers.get(str(i))==LAB1_QUESTIONS[i][1][LAB1_QUESTIONS[i][2]] for i in range(29))
        theory_score=hits/29*80
        st.progress(answered/29)
        st.caption(f'{answered} de 29 respuestas registradas · Puntaje teórico acumulado: {theory_score:.1f}/80')
    with tab2:
        st.markdown('<div class="question-box"><div class="question-label">PREGUNTA 30 · CASO PROFESIONAL INTEGRADOR</div><div class="question-text">¿Qué solución recomendarías para proteger un dormitorio contiguo a una sala de máquinas?</div><p>La fuente domina en 125, 250 y 500 Hz. Calcula, compara y justifica tu decisión técnico-económica.</p></div>', unsafe_allow_html=True)
        df = pd.DataFrame({'Indicador': ['Rw', 'Cₜᵣ', 'Rw+Cₜᵣ', 'R en 125 Hz', 'R en 250 Hz', 'R en 500 Hz', 'Costo instalado', 'Vida útil'], 'Solución A': ['52 dB', '−9 dB', '43 dB', '27 dB', '34 dB', '47 dB', '$1.800.000', '20 años'], 'Solución B': ['49 dB', '−4 dB', '45 dB', '34 dB', '39 dB', '45 dB', '$2.100.000', '25 años']})
        st.dataframe(df, hide_index=True, use_container_width=True)
        c1, c2 = st.columns(2)
        V = c1.number_input('V (m³)', 1.0, 500.0, 50.0, key='case_V')
        A = c2.number_input('A (m² sabin)', 1.0, 200.0, 20.0, key='case_A')
        calc = st.number_input('Calcula T₆₀ (s)', 0.0, 10.0, 0.0, 0.01, key='case_calc')
        diff = st.number_input('Diferencia de costo ($)', 0, 5000000, 0, step=50000, key='case_diff')
        pct = st.number_input('Incremento porcentual de B respecto de A (%)', 0.0, 200.0, 0.0, 0.1, key='case_pct')
        bands = st.multiselect('Bandas críticas', [125, 250, 500, 1000], key='case_bands')
        choice = st.radio('Recomendación', ['Solución A', 'Solución B'], index=None, key='case_choice')
        justification = st.text_area('Justificación técnico-económica', key='case_justification')
        practical_live=_lab1_case_score_impl(calc,diff,pct,bands,choice,justification)
        draft_answers=st.session_state.get('lab1_final_answers',{})
        theory_hits=sum(draft_answers.get(str(i))==LAB1_QUESTIONS[i][1][LAB1_QUESTIONS[i][2]] for i in range(29))
        theory_live=theory_hits/29*80
        st.markdown(f'<div class="good"><b>Puntaje acumulado: {theory_live+practical_live:.1f}/100</b><br>Teoría: {theory_live:.1f}/80 · Caso práctico: {practical_live}/20.</div>',unsafe_allow_html=True)
        answered=sum(draft_answers.get(str(i)) is not None for i in range(29))
        if st.button('Enviar evaluación definitiva',type='primary',use_container_width=True,key='lab1_final_submit'):
            if answered<29 or choice is None or not justification.strip():
                st.session_state['lab1_confirm_incomplete']=True
                st.warning('La evaluación tiene respuestas pendientes. Revísalas antes del envío definitivo.')
            else:
                try:
                    _finish_lab1_final_impl('submitted')
                    st.rerun()
                except Exception as exc:
                    st.error(f'No fue posible enviar la evaluación. Tus respuestas continúan guardadas como avance. Detalle: {exc}')
        if st.session_state.get('lab1_confirm_incomplete'):
            if st.button('Confirmar envío con respuestas pendientes',key='lab1_final_submit_incomplete'):
                try:
                    _finish_lab1_final_impl('submitted_incomplete')
                    st.rerun()
                except Exception as exc:
                    st.error(f'No fue posible enviar la evaluación. Tus respuestas continúan guardadas como avance. Detalle: {exc}')

_STAGES = [
    _stage0_impl, _stage1_impl, _stage2_impl, _stage3_impl, _stage4_impl,
    _stage5_impl, _stage6_impl, _stage7_impl, _stage8_impl, _stage9_impl,
    _stage10_impl,
]

_HELPERS = {
    "_lab1_final_submission": _lab1_final_submission_impl,
    "_lab1_case_score": _lab1_case_score_impl,
    "_finish_lab1_final": _finish_lab1_final_impl,
}

def run_stage(stage_index, runtime):
    _bind_runtime(runtime)
    return _STAGES[stage_index]()

def run_helper(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _HELPERS[name](*args, **kwargs)
