"""Etapas activas del Laboratorio 2.

Este módulo conserva el código pedagógico de cada etapa. ``app.py`` inyecta
las dependencias compartidas justo antes de ejecutar una etapa, evitando
duplicar la infraestructura de Streamlit, persistencia y componentes UI.
"""

_RUNTIME_PROTECTED = {
    "run_stage", "_STAGES", "_RUNTIME_PROTECTED", "_lab2_heading",
    "_saved_formative_response", "_render_saved_activity_state",
    *{f"_stage{i}_impl" for i in range(11)},
}

def _bind_runtime(runtime):
    """Actualiza las dependencias compartidas sin sobrescribir este módulo."""
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and not name.startswith("lab2_stage"):
            module_globals[name] = value

def _saved_formative_response(stage, key):
    """Recupera respuestas formativas mediante el motor central."""
    return _evaluations.run_evaluation(
        "_saved_formative_response", globals(), stage, key
    )

def _render_saved_activity_state(saved):
    """Muestra el estado persistente mediante el motor central."""
    return _evaluations.run_evaluation(
        "_render_saved_activity_state", globals(), saved
    )

def _lab2_heading(stage, title, purpose):
    header(f"ETAPA {stage} · LABORATORIO 2", title, purpose,
           show_overview=False, duration_minutes=LAB2_MINUTES[stage])

def _stage0_impl():
    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 2 · Modelos de predicción del aislamiento acústico",
        "Una experiencia visual para reconocer el sistema constructivo, seleccionar el modelo físico y leer correctamente su curva de pérdida de transmisión.",
        show_overview=False,
        duration_minutes=LAB2_MINUTES[0],
    )
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Duración total del laboratorio: 4 horas</strong>'
        f'<br><span>{LAB2_ACTIVE_MINUTES} min de aprendizaje y evaluación + '
        f'{LAB2_BREAK_MINUTES} min de pausa</span>'
        f'</div><div><strong>{LAB2_TOTAL_MINUTES} min</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )
    route = [
        ("Pérdida de transmisión", "Relaciona la energía incidente y transmitida con τ y TL.", LAB2_MINUTES[1]),
        ("Panel simple", "Reconoce incidencia, rigidez, resonancias, ley de masa y coincidencia.", LAB2_MINUTES[2]),
        ("Comparación de placas", "Compara yeso-cartón, vidrio monolítico y hormigón por bandas.", LAB2_MINUTES[3]),
        ("Panel doble", "Explora masas, cámara de aire, resonancia y conexiones estructurales.", LAB2_MINUTES[4]),
        ("Modelo de Sharp", "Calcula f₀, fₗ y el TL correspondiente en cada tramo.", LAB2_MINUTES[5]),
        ("Ventanas dobles", "Analiza la cámara, las hojas y la pérdida de transmisión del sistema.", LAB2_MINUTES[6]),
        ("Bandas de frecuencia", "Distingue octavas y tercios de octava e interpreta sus curvas.", LAB2_MINUTES[7]),
        ("Rw, C y Ctr", "Obtiene e interpreta el índice ponderado y sus adaptaciones espectrales.", LAB2_MINUTES[8]),
        ("Evaluación de comprensión", "Resuelve 10 preguntas con alternativas en un único intento.", LAB2_MINUTES[9]),
        ("Aplicación integradora", "Desarrolla y justifica la solución del caso técnico final.", LAB2_MINUTES[10]),
    ]
    html = '<div class="route-grid">'
    for i, (title, description, minutes) in enumerate(route, 1):
        html += (
            f'<div class="route-card"><span class="step">{i}</span><div>'
            f'<b>{title}</b><p>{description}</p>'
            f'<span class="route-time">⏱️ {minutes} min</span></div></div>'
        )
    st.markdown(html + "</div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="warn" style="margin-top:1rem"><b>☕ Pausa programada: '
        f'{LAB2_BREAK_MINUTES} minutos</b><br>Se realizará después de la Etapa '
        f'{LAB2_BREAK_AFTER_STAGE}. Primer bloque: 105 min · Pausa: 30 min · '
        f'Segundo bloque: 105 min.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> '
        'concepto visual → fundamento físico → ecuación → simulación → caso real → interpretación de la curva.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warn" style="margin-top:.8rem"><b>Alcance del modelo:</b> '
        'las predicciones corresponden al elemento idealizado. El resultado construido también '
        'depende del montaje, sellos, encuentros, dimensiones y transmisiones laterales.</div>',
        unsafe_allow_html=True,
    )

def _stage1_impl():
    _lab2_heading(
        1,
        "Pérdida de transmisión: τ, TL y escala decibel",
        "Comprender el decibel como una relación logarítmica y convertir, en ambos sentidos, entre coeficiente de transmisión y pérdida de transmisión.",
    )
    _lab2_image("panel_simple")

    st.markdown("### 1. El decibel no es una cantidad absoluta")
    st.markdown(r"""
    El **decibel (dB)** expresa de forma logarítmica la **relación entre dos cantidades**.
    No es una unidad absoluta como el watt, el metro o el pascal. En relaciones de
    potencia o energía se utiliza:
    """)
    st.latex(r"L=10\log_{10}\left(\frac{W_1}{W_0}\right)")
    st.markdown(r"""
    En acústica las potencias, intensidades y presiones abarcan rangos enormes. La escala
    logarítmica los convierte en valores manejables y permite interpretar órdenes de
    magnitud: una razón energética de 10 equivale a 10 dB; de 100, a 20 dB; y de
    1.000, a 30 dB.
    """)

    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### Nivel de presión sonora")
        st.latex(r"L_p=20\log_{10}\left(\frac{p}{p_0}\right)")
        st.markdown(
            "Compara la presión acústica **p** con la presión de referencia "
            "**p₀ = 20 µPa**. Ejemplo: **85 dB SPL**."
        )
    with c2:
        st.markdown("#### Pérdida de transmisión")
        st.latex(r"TL=10\log_{10}\left(\frac{W_i}{W_t}\right)")
        st.markdown(
            "Compara la potencia incidente **Wᵢ** y la transmitida **Wₜ**. "
            "Un **TL = 30 dB** no es un sonido de 30 dB."
        )
    st.info(
        "Decir solamente «40 dB» está incompleto: siempre debe indicarse la magnitud, "
        "por ejemplo 40 dB SPL, TL = 40 dB o R = 40 dB."
    )

    st.markdown("### 2. Del coeficiente τ a la pérdida de transmisión TL")
    st.markdown("""
    El coeficiente de transmisión **τ** es la fracción adimensional de la potencia
    incidente que atraviesa la separación:
    """)
    st.latex(r"\tau=\frac{W_t}{W_i}\qquad 0\leq\tau\leq1")
    st.markdown("La definición de pérdida de transmisión es:")
    st.latex(r"TL=10\log_{10}\left(\frac{W_i}{W_t}\right)")
    st.markdown("Como **Wᵢ/Wₜ = 1/τ**, la sustitución entrega:")
    st.latex(r"TL=10\log_{10}\left(\frac{1}{\tau}\right)")
    st.latex(r"\boxed{TL=-10\log_{10}(\tau)}")
    st.markdown("Y para realizar la conversión inversa:")
    st.latex(r"\boxed{\tau=10^{-TL/10}}")

    st.markdown("### 3. Explorador técnico τ ↔ TL")
    control_mode=st.radio(
        "Variable que deseas controlar",
        ["TL (dB)","τ (coeficiente de transmisión)"],
        horizontal=True,
        key="lab2_tau_tl_mode",
    )
    if control_mode=="TL (dB)":
        tl=float(st.slider(
            "Pérdida de transmisión TL (dB)",0,60,30,1,key="lab2_tau_tl_db"
        ))
        tau=10**(-tl/10)
    else:
        tau_options=[10**(-i/10) for i in range(60,-1,-1)]
        tau=st.select_slider(
            "Coeficiente de transmisión τ",
            options=tau_options,
            value=1e-3,
            format_func=lambda value: (
                f"{value:.6f}".rstrip("0").rstrip(".")
                if value >= 1e-4 else f"{value:.1e}"
            ),
            key="lab2_tau_value",
        )
        tl=-10*math.log10(tau)
        st.caption(
            f"τ siempre es positivo. Equivalencia logarítmica: "
            f"τ = 10^({math.log10(tau):.1f})"
        )

    transmitted_pct=100*tau
    not_transmitted_pct=100*(1-tau)
    m1,m2,m3=st.columns(3)
    m1.metric("TL",f"{tl:.1f} dB")
    m2.metric("τ",f"{tau:.6g}")
    m3.metric("Energía transmitida",f"{transmitted_pct:.6g} %")

    incident_units=1_000_000.0
    transmitted_units=incident_units*tau
    energy_fig=go.Figure()
    energy_fig.add_trace(go.Bar(
        x=["Potencia incidente Wi","Potencia transmitida Wt"],
        y=[incident_units,transmitted_units],
        marker_color=["#0b69d1","#ef8b2c"],
        text=[f"{incident_units:,.0f} unidades",f"{transmitted_units:,.3g} unidades"],
        textposition="outside",
        hovertemplate="%{x}<br>%{y:,.6g} unidades<extra></extra>",
    ))
    energy_fig.update_layout(
        title="Comparación energética en escala logarítmica",
        yaxis_title="Potencia relativa (unidades)",
        yaxis_type="log",
        yaxis_range=[-1,6.45],
        height=360,
        showlegend=False,
        margin=dict(l=35,r=20,t=65,b=40),
    )
    tau_curve=np.logspace(0,-6,241)
    tl_curve=-10*np.log10(tau_curve)
    relation_fig=go.Figure()
    relation_fig.add_trace(go.Scatter(
        x=tau_curve,y=tl_curve,mode="lines",name="TL = −10 log₁₀(τ)",
        line=dict(width=4,color="#0b69d1"),
    ))
    relation_fig.add_trace(go.Scatter(
        x=[tau],y=[tl],mode="markers+text",name="Selección actual",
        marker=dict(size=13,color="#ef8b2c"),
        text=[f"τ={tau:.3g} · TL={tl:.1f} dB"],
        textposition="top center",
    ))
    relation_fig.update_layout(
        title="Relación logarítmica entre τ y TL",
        xaxis_title="Coeficiente de transmisión τ",
        yaxis_title="Pérdida de transmisión TL (dB)",
        xaxis_type="log",
        xaxis_autorange="reversed",
        yaxis_range=[0,64],
        height=360,
        hovermode="closest",
        margin=dict(l=35,r=20,t=65,b=40),
    )
    relation_fig.update_xaxes(
        tickvals=[1,1e-1,1e-2,1e-3,1e-4,1e-5,1e-6],
        ticktext=["1","0,1","0,01","0,001","10⁻⁴","10⁻⁵","10⁻⁶"],
    )
    graph_left,graph_right=st.columns(2,gap="medium")
    with graph_left:
        st.plotly_chart(
            energy_fig,
            use_container_width=True,
            key="lab2_tau_tl_energy_chart",
        )
    with graph_right:
        st.plotly_chart(
            relation_fig,
            use_container_width=True,
            key="lab2_tau_tl_relation_chart",
        )
    st.markdown(
        f'<div class="lesson"><b>Lectura técnica:</b> de 1.000.000 unidades incidentes, '
        f'atraviesan {transmitted_units:,.3g}. Esto corresponde a τ = {tau:.6g}, '
        f'{transmitted_pct:.6g} % transmitido y TL = {tl:.1f} dB. '
        f'La fracción no transmitida es {not_transmitted_pct:.6g} %; este último valor '
        f'no debe confundirse automáticamente con absorción, porque también incluye energía reflejada.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 4. ¿Por qué aquí se usa TL y después aparecerá R?")
    st.markdown("""
    En esta etapa usamos **TL** (*Transmission Loss*) porque partimos de la relación física
    entre potencia incidente y transmitida y trabajamos con modelos predictivos. En ensayos
    normalizados de elementos constructivos se usa habitualmente el **índice de reducción
    acústica R**, obtenido a partir de los niveles de las cámaras y de las condiciones
    del ensayo. Ambos describen el aislamiento por bandas y pueden coincidir bajo
    condiciones ideales, pero el símbolo debe corresponder al contexto y al método de
    obtención. Más adelante, la curva **R(f)** permitirá calcular **Rw**.
    """)

    st.markdown("### 5. Preguntas de comprensión")
    check(
        "lab2_s1_q1",
        "Un panel tiene τ = 0,01. ¿Qué porcentaje de la energía incidente lo atraviesa?",
        ["10 %","1 %","0,1 %","0,01 %"],
        "1 %",
        "τ es una fracción: 0,01 × 100 = 1 %.",
    )
    check(
        "lab2_s1_q2",
        "Si τ = 0,001, ¿qué TL se obtiene mediante TL = −10 log₁₀(τ)?",
        ["10 dB","20 dB","30 dB","40 dB"],
        "30 dB",
        "log₁₀(0,001) = −3; por tanto, TL = −10(−3) = 30 dB.",
    )
    check(
        "lab2_s1_q3",
        "¿Cuál afirmación describe correctamente el decibel?",
        [
            "Es una unidad absoluta de potencia sonora",
            "Expresa logarítmicamente una relación entre cantidades",
            "Siempre representa nivel de presión sonora",
            "Es equivalente a un watt",
        ],
        "Expresa logarítmicamente una relación entre cantidades",
        "El dB expresa una razón logarítmica; la magnitud concreta depende de la ecuación y de sus referencias.",
    )
    check(
        "lab2_s1_q4",
        "El panel A tiene TL = 20 dB y el B, TL = 30 dB. ¿Qué comparación es correcta?",
        [
            "B transmite diez veces menos energía que A",
            "B transmite solamente 10 % menos energía que A",
            "A y B transmiten la misma energía",
            "B transmite el doble de energía que A",
        ],
        "B transmite diez veces menos energía que A",
        "Un aumento de 10 dB en TL divide por diez la energía transmitida.",
    )
    check(
        "lab2_s1_q5",
        "¿Por qué se usa TL en esta etapa y R en un ensayo normalizado de una partición?",
        [
            "TL se relaciona aquí con un modelo energético; R corresponde al resultado normalizado del elemento ensayado",
            "TL se usa solo en exteriores y R solo en interiores",
            "TL se mide en watt y R en decibeles",
            "No existe diferencia de contexto entre ambos símbolos",
        ],
        "TL se relaciona aquí con un modelo energético; R corresponde al resultado normalizado del elemento ensayado",
        "TL es habitual en la formulación física y predictiva; R es la denominación normalizada del índice de reducción acústica por bandas.",
    )

def _stage2_impl():
    _lab2_heading(2, "Panel simple: incidencia y cuatro zonas físicas",
                  "Relacionar masa, frecuencia, rigidez, resonancia y coincidencia con la forma de la curva.")
    _lab2_image("panel_simple")
    st.caption(
        "Placa simple sometida a una onda sonora: una parte de la energía se refleja, "
        "otra hace vibrar la placa y una fracción se transmite al recinto receptor."
    )
    st.markdown("""
    Un **panel simple** es una hoja o conjunto de capas unidas rígidamente que vibran como
    una sola masa: vidrio monolítico, placa de yeso, tablero de madera, chapa o muro macizo.
    No existe una segunda hoja independiente ni una cámara que actúe como resorte.
    """)
    st.markdown("### 1. ¿Qué define a una placa simple?")
    st.markdown("""
    Se considera **placa simple** al elemento que, frente a la excitación sonora, se
    desplaza y flexiona esencialmente como una sola hoja. Puede estar constituido por
    un único material o por capas adheridas rígidamente; lo importante es que no existan
    dos hojas independientes separadas por una cámara de aire.

    Su primera propiedad acústica es la **masa superficial**: la masa contenida en cada
    metro cuadrado de placa. Para una placa homogénea se obtiene multiplicando la densidad
    del material por su espesor:
    """)
    st.latex(r"m'=\rho h")
    st.markdown("""
    - **m′**: masa superficial, en kg/m².
    - **ρ**: densidad del material, en kg/m³.
    - **h**: espesor, en m.

    La masa superficial —y no la masa total de toda la placa— es la que interviene en la
    ley de masa. Dos placas del mismo material y espesor tienen la misma m′ aunque sus
    superficies totales sean distintas. Al aumentar m′ crece la oposición inercial al
    movimiento, pero la respuesta real también depende de la rigidez de flexión, las
    dimensiones, los apoyos, el amortiguamiento y la frecuencia.
    """)
    _lab2_image("s2_punto1")
    _lab2_plain_language_cards(
        "La masa superficial indica cuánto pesa un metro cuadrado de placa.",
        "Compara placas del mismo tamaño: la más densa o gruesa tendrá mayor m′.",
        "Usar la masa total de la pared. La ley de masa utiliza kg/m², no kg.",
    )
    st.markdown("### 2. Incidencia normal y oblicua")
    st.markdown("""
    El ángulo **θ se mide respecto de la línea normal a la placa**, no respecto de su
    superficie:

    - **Incidencia normal (θ = 0°):** la onda llega perpendicularmente a la placa.
    - **Incidencia oblicua (0° < θ < 90°):** la onda llega inclinada.
    - **Incidencia rasante (θ próxima a 90°):** la propagación es casi paralela a la placa.

    La incidencia normal y la oblicua describen una sola dirección de llegada. En cambio,
    en un recinto reverberante existe energía que alcanza la placa desde muchas direcciones:
    eso se representa mediante un promedio energético angular.
    """)
    _lab2_image("s2_punto2")
    _lab2_plain_language_cards(
        "El sonido puede llegar de frente o inclinado; el ángulo cambia cómo empuja la placa.",
        "El ángulo se mide desde la línea perpendicular a la placa: 0° es incidencia normal.",
        "Medir θ desde la superficie o creer que 78° representa por sí solo todo el campo.",
    )
    st.markdown("### 3. Coeficiente de transmisión sonora según el ángulo")
    st.latex(r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}")
    st.latex(r"TL(\theta)=-10\log_{10}\left[\tau(\theta)\right]")
    st.markdown("""
    El coeficiente **τ(θ)** representa la fracción de potencia sonora incidente que
    atraviesa la placa para una dirección específica. Es un valor adimensional entre
    0 y 1: cuanto menor es τ, menor energía se transmite y mayor es la pérdida de
    transmisión **TL**.

    En esta expresión, **ω = 2πf** es la frecuencia angular, **m′** es la masa
    superficial de la placa, **ρ₀** es la densidad del aire, **c** es la velocidad del
    sonido y **θ** es el ángulo medido desde la normal. El término **cos θ** hace que
    la impedancia efectiva que presenta la placa cambie con la dirección de llegada.
    Por eso una misma placa y una misma frecuencia no entregan un único resultado para
    todas las incidencias.

    El cálculo se realiza primero en escala energética mediante τ(θ). Después se
    convierte a decibeles con **TL(θ) = −10 log₁₀[τ(θ)]**. Por ejemplo, τ = 0,01
    significa que atraviesa el 1 % de la potencia incidente y equivale a TL = 20 dB.
    """)
    _lab2_image("s2_tau_angulo")
    _lab2_plain_language_cards(
        "Cada dirección deja pasar una fracción distinta de energía, representada por τ(θ).",
        "Observa cómo varía la energía transmitida al cambiar únicamente el ángulo.",
        "Interpretar τ como decibeles: τ es una proporción energética y TL es su expresión logarítmica.",
    )
    st.markdown("### 4. Incidencia aleatoria y promedio de campo")
    st.latex(
        r"\overline{\tau}="
        r"\frac{\displaystyle\int_{0}^{\theta_{\mathrm{lim}}}"
        r"\tau(\theta)\sin\theta\cos\theta\,d\theta}"
        r"{\displaystyle\int_{0}^{\theta_{\mathrm{lim}}}"
        r"\sin\theta\cos\theta\,d\theta}"
    )
    st.latex(r"TL_{\mathrm{campo}}=-10\log_{10}\left(\overline{\tau}\right)")
    st.markdown("""
    En un campo sonoro reverberante la placa recibe simultáneamente energía desde muchas
    direcciones. El resultado de campo no corresponde al TL de un ángulo particular:
    se obtiene integrando los coeficientes **τ(θ)** de todas las direcciones consideradas.

    La ponderación **sin θ cos θ** tiene un significado físico. **sin θ** representa la
    cantidad de direcciones disponibles dentro de cada anillo angular, mientras que
    **cos θ** representa la componente de intensidad sonora normal a la superficie.
    El denominador normaliza esa ponderación para que el resultado sea un promedio
    energético y no una suma dependiente del intervalo elegido.

    En este laboratorio se adopta **θ_lim = 78°** como aproximación práctica de campo.
    Se integran todas las incidencias entre 0° y 78°; no se calcula únicamente la
    transmisión a 78°. Una vez obtenido el coeficiente medio **τ̄**, recién entonces
    se transforma a decibeles para obtener **TL_campo**.
    """)
    _lab2_image("s2_punto4")
    _lab2_plain_language_cards(
        "Un recinto real envía sonido hacia la placa desde muchas direcciones a la vez.",
        "El resultado de campo integra desde 0° hasta 78° con ponderación energética.",
        "Promediar directamente los TL o tomar el valor a 78° como si fuera el promedio de campo.",
    )
    st.markdown("""
    - **Incidencia aleatoria o campo difuso ideal:** supone direcciones distribuidas
      estadísticamente hasta 90°.
    - **Incidencia de campo:** aproximación práctica del promedio angular; frecuentemente
      se limita la integración cerca de 78° para representar mejor resultados experimentales.

    No se promedian directamente valores de TL en decibeles. Primero se promedian los
    coeficientes de transmisión τ y después se transforma el resultado a decibeles.
    """)
    st.markdown("### 5. Rigidez de flexión: la placa también se deforma")
    st.markdown("""
    Una placa simple no se desplaza únicamente como una masa rígida: también se curva.
    La resistencia que opone a esa deformación se denomina **rigidez de flexión**:
    """)
    st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    st.markdown("""
    - **D**: rigidez de flexión por unidad de ancho, en N·m.
    - **E**: módulo de Young, en Pa.
    - **h**: espesor, en m.
    - **ν**: coeficiente de Poisson, adimensional.

    La relación D ∝ h³ muestra que el espesor afecta mucho más a la rigidez que a la masa
    superficial: si se duplica h, m′ se duplica, pero D aumenta idealmente ocho veces.
    Esta rigidez determina los modos propios y, junto con m′, la propagación de las ondas
    de flexión y la frecuencia crítica.
    """)
    st.markdown("#### Ecuación de movimiento de una placa simple sometida a presión sonora")
    st.markdown("""
    Para describir cómo responde la placa cuando el sonido la excita, se plantea su
    equilibrio dinámico: la presión sonora aplicada debe vencer simultáneamente la
    resistencia de la placa a curvarse y la inercia asociada a su masa superficial.
    """)
    st.latex(r"D\nabla^4\xi+m'\frac{\partial^2\xi}{\partial t^2}=\Delta p")
    st.markdown("""
    En esta ecuación de movimiento, **D∇⁴ξ** representa la resistencia a la flexión,
    **m′∂²ξ/∂t²** la inercia de la masa superficial y **Δp** la diferencia de presión
    sonora entre ambas caras que hace vibrar la placa. En la región donde domina la
    inercia puede simplificarse este equilibrio y obtenerse la ley de masa.
    """)
    _lab2_image("s2_punto3")
    _lab2_plain_language_cards(
        "La placa no solo se desplaza: también se curva. D mide cuánto cuesta doblarla.",
        "El espesor aparece elevado al cubo; pequeños cambios de h modifican mucho la rigidez.",
        "Suponer que una placa más pesada siempre tiene proporcionalmente mayor rigidez.",
    )
    st.markdown("### 6. De la impedancia de masa a la ley de masa aproximada")
    st.markdown("""
    En la región donde domina la **inercia**, una hoja ideal puede representarse mediante
    su impedancia mecánica por unidad de superficie. Para una excitación armónica:
    """)
    st.latex(r"z_m=j\omega m'")
    st.markdown("Al sustituirla en la expresión de transmisión de una hoja entre dos medios de aire:")
    st.latex(r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}")
    st.markdown("y aplicar la definición desarrollada en la Etapa 1:")
    st.latex(r"TL(\theta)=-10\log_{10}\left[\tau(\theta)\right]")
    st.markdown("""
    Para incidencia normal, **θ = 0°** y, por tanto, **cos θ = 1**. Si el término de masa
    es mucho mayor que 1, se desprecia el 1 de la expresión. Luego se sustituye la
    frecuencia angular por su relación con la frecuencia ordinaria:
    """)
    st.latex(r"\omega=2\pi f")
    st.latex(r"TL_n\approx20\log_{10}(m'f)+20\log_{10}\left(\frac{\pi}{\rho_0c}\right)")
    st.latex(r"TL_n\approx20\log_{10}(m'f)-42\quad\text{dB}")
    st.info("La expresión anterior corresponde a incidencia normal y conduce, para aire "
            "en condiciones habituales, a una constante cercana a −42 dB.")
    st.latex(r"TL_{\mathrm{campo}}\approx20\log_{10}(m'f)-47\quad\mathrm{dB}")
    st.markdown("""
    La forma con **−47 dB** incorpora una corrección aproximada de incidencia de campo.
    No es una constante universal ni una ley física diferente: depende del modelo angular
    adoptado y solo describe la tendencia de la zona controlada por masa, lejos de las
    resonancias, la coincidencia, las fugas y las transmisiones laterales.
    """)
    _lab2_image("s2_ley_masa",
                "Zona controlada por masa: una placa más pesada opone mayor inercia.")
    _lab2_plain_language_cards(
        "Una placa pesada se parece a un carro difícil de empujar: se mueve menos ante el sonido.",
        "En la zona de masa, duplicar m′ o la frecuencia aumenta el TL aproximadamente 6 dB.",
        "Extender la recta de ley de masa a resonancias y coincidencia, donde deja de ser válida.",
    )

    st.markdown("### 7. Frecuencia crítica y coincidencia")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}")
    st.markdown("""
    La **frecuencia crítica** es la zona en que la onda sonora puede acoplarse con
    una onda de flexión de la placa. Ese acoplamiento facilita la transmisión y
    puede producir un valle en la curva de aislamiento.

    **En sencillo:** existe una zona donde la placa vibra de una forma especialmente
    favorable para que el sonido pase. Se calcula usando la masa superficial y la
    rigidez explicadas antes; no es un parámetro independiente.
    """)
    st.latex(r"m'=\rho h")
    st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    st.latex(r"f_c\propto\frac{1}{h}\sqrt{\frac{\rho}{E}}")
    st.caption(
        "η no determina por sí solo fᶜ; influye principalmente en la profundidad "
        "y anchura del valle de coincidencia."
    )
    _lab2_image("s2_frecuencia_critica",
                "Coincidencia entre la onda sonora y la onda de flexión de una placa.")
    _lab2_plain_language_cards(
        "Es una zona donde la onda aérea logra hacer vibrar la placa con especial eficiencia.",
        "La curva real forma un valle respecto de la tendencia ideal de ley de masa.",
        "Confundir la frecuencia crítica con una resonancia propia global de la placa.",
    )

    st.markdown("### 8. Laboratorio interactivo: incidencia y aislamiento")
    st.markdown("""
    Una misma placa puede evaluarse bajo tres condiciones de incidencia. La diferencia
    no está en el material, sino en **cómo llega la energía sonora** y en la forma de
    combinarla:

    - **Incidencia normal:** ondas paralelas que llegan perpendicularmente a la placa.
    - **Campo de laboratorio 0°–78°:** promedio energético de múltiples incidencias
      comprendidas entre 0° y 78°.
    - **Campo difuso ideal 0°–90°:** modelo ideal con energía procedente de todo el
      hemisferio incidente.

    Selecciona una condición para resaltarla y cambia la frecuencia. La aplicación
    recalcula simultáneamente los tres resultados, de modo que puedas comparar el efecto
    del modelo de incidencia sin confundir el promedio de campo con un rayo aislado.
    """)

    lab_mode_options = [
        "Incidencia normal · 0°",
        "Campo de laboratorio · 0° a 78°",
        "Campo difuso ideal · 0° a 90°",
    ]
    control_a, control_b = st.columns([1.55, 1])
    field_mode = control_a.radio(
        "Condición que deseas observar",
        lab_mode_options,
        index=1,
        horizontal=True,
        key="lab2_field_mode",
    )
    angular_frequency = control_b.select_slider(
        "Frecuencia de cálculo (Hz)",
        options=LAB2_FREQS.tolist(),
        value=500,
        key="lab2_field_frequency",
    )

    angular_mass = 10.0

    def _field_average_tau(limit_degrees):
        field_angles = np.linspace(0.0, float(limit_degrees), 900)
        field_angles_rad = np.deg2rad(field_angles)
        field_tau = np.array([
            _mass_sheet_tau(angular_mass, angular_frequency, float(theta))
            for theta in field_angles
        ])
        field_weights = np.sin(field_angles_rad) * np.cos(field_angles_rad)
        if hasattr(np, "trapezoid"):
            numerator = np.trapezoid(field_tau * field_weights, field_angles_rad)
            denominator = np.trapezoid(field_weights, field_angles_rad)
        else:
            numerator = np.trapz(field_tau * field_weights, field_angles_rad)
            denominator = np.trapz(field_weights, field_angles_rad)
        return max(float(numerator / max(denominator, 1e-15)), 1e-15)

    tau_normal = _mass_sheet_tau(angular_mass, angular_frequency, 0)
    tau_field_78 = _field_average_tau(78.0)
    tau_field_90 = _field_average_tau(89.9)
    tl_normal = -10 * math.log10(tau_normal)
    tl_field_78 = -10 * math.log10(tau_field_78)
    tl_field_90 = -10 * math.log10(tau_field_90)

    field_results = {
        "Incidencia normal · 0°": (tau_normal, tl_normal),
        "Campo de laboratorio · 0° a 78°": (tau_field_78, tl_field_78),
        "Campo difuso ideal · 0° a 90°": (tau_field_90, tl_field_90),
    }
    selected_tau, selected_tl = field_results[field_mode]

    # Esquema pedagógico: tres campos visibles y la selección destacada.
    field_colors = {
        "Incidencia normal · 0°": "#1565c0",
        "Campo de laboratorio · 0° a 78°": "#ef6c00",
        "Campo difuso ideal · 0° a 90°": "#7b1fa2",
    }
    field_titles = [
        "Incidencia normal",
        "Campo de laboratorio 0°–78°",
        "Campo difuso ideal 0°–90°",
    ]
    field_keys = lab_mode_options
    fig_fields = go.Figure()
    for panel_index, (panel_title, panel_key) in enumerate(zip(field_titles, field_keys)):
        x0 = panel_index * 4.0
        active = panel_key == field_mode
        color = field_colors[panel_key]
        fig_fields.add_shape(
            type="rect",
            x0=x0 + 0.05,
            x1=x0 + 3.75,
            y0=0.15,
            y1=4.65,
            fillcolor=color if active else "#f8fafc",
            opacity=0.11 if active else 1.0,
            line=dict(color=color if active else "#cbd5e1", width=4 if active else 1.5),
            layer="below",
        )
        panel_x = x0 + 2.55
        fig_fields.add_shape(
            type="rect",
            x0=panel_x,
            x1=panel_x + 0.12,
            y0=0.8,
            y1=3.85,
            fillcolor="#475569",
            line=dict(color="#334155", width=1),
        )
        fig_fields.add_annotation(
            x=x0 + 1.9,
            y=4.3,
            text=f"<b>{panel_title}</b>",
            showarrow=False,
            font=dict(size=14, color="#0f172a"),
        )

        if panel_index == 0:
            ray_origins = [(x0 + 0.45, 1.45), (x0 + 0.45, 2.3), (x0 + 0.45, 3.15)]
        elif panel_index == 1:
            ray_origins = [
                (x0 + 0.45, 0.65), (x0 + 0.45, 1.25), (x0 + 0.45, 2.3),
                (x0 + 0.45, 3.35), (x0 + 0.45, 3.95),
            ]
        else:
            ray_origins = [
                (x0 + 0.35, 0.35), (x0 + 0.35, 0.9), (x0 + 0.35, 1.55),
                (x0 + 0.35, 2.3), (x0 + 0.35, 3.05), (x0 + 0.35, 3.7),
                (x0 + 0.35, 4.25),
            ]
        for origin_x, origin_y in ray_origins:
            fig_fields.add_annotation(
                x=panel_x,
                y=2.3,
                ax=origin_x,
                ay=origin_y,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.1,
                arrowwidth=2.8 if active else 1.8,
                arrowcolor=color if active else "#94a3b8",
            )
        fig_fields.add_annotation(
            x=x0 + 1.9,
            y=0.42,
            text="<b>SELECCIONADO</b>" if active else "Seleccionar arriba",
            showarrow=False,
            font=dict(size=11, color=color if active else "#64748b"),
        )

    fig_fields.update_xaxes(range=[0, 11.8], visible=False, fixedrange=True)
    fig_fields.update_yaxes(range=[0, 4.9], visible=False, fixedrange=True)
    fig_fields.update_layout(
        title="Cómo llega la energía sonora a la placa",
        height=430,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(
        fig_fields,
        use_container_width=True,
        key="lab2_three_incidence_fields",
        config={"displayModeBar": False},
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("TL normal", f"{tl_normal:.1f} dB", "Incidencia 0°")
    m2.metric("TL de campo", f"{tl_field_78:.1f} dB", "Promedio 0°–78°")
    m3.metric("TL difuso ideal", f"{tl_field_90:.1f} dB", "Promedio 0°–90°")

    comparison_names = ["Normal 0°", "Campo 0°–78°", "Difuso ideal 0°–90°"]
    comparison_values = [tl_normal, tl_field_78, tl_field_90]
    comparison_colors = [
        field_colors["Incidencia normal · 0°"],
        field_colors["Campo de laboratorio · 0° a 78°"],
        field_colors["Campo difuso ideal · 0° a 90°"],
    ]
    fig_comparison = go.Figure(go.Bar(
        x=comparison_names,
        y=comparison_values,
        marker_color=comparison_colors,
        text=[f"{value:.1f} dB" for value in comparison_values],
        textposition="outside",
        hovertemplate="%{x}<br>TL = %{y:.1f} dB<extra></extra>",
    ))
    fig_comparison.update_layout(
        title=f"Comparación del aislamiento a {angular_frequency} Hz",
        xaxis_title="Condición de incidencia",
        yaxis_title="Pérdida de transmisión, TL (dB)",
        height=360,
        margin=dict(l=35, r=15, t=60, b=45),
        showlegend=False,
    )
    fig_comparison.update_yaxes(
        range=[0, max(comparison_values) * 1.22],
        gridcolor="#e2e8f0",
    )
    st.plotly_chart(
        fig_comparison,
        use_container_width=True,
        key="lab2_field_tl_comparison",
        config={"displayModeBar": False},
    )

    transmitted_percent = 100.0 * selected_tau
    if field_mode == "Incidencia normal · 0°":
        field_explanation = (
            "Las ondas llegan perpendicularmente y todas comparten la misma dirección. "
            "El resultado corresponde a una incidencia única, no a un promedio angular."
        )
    elif field_mode == "Campo de laboratorio · 0° a 78°":
        field_explanation = (
            "El resultado combina energéticamente todas las incidencias entre 0° y 78°. "
            "No corresponde al TL de una onda que llega a 78°."
        )
    else:
        field_explanation = (
            "El modelo ideal incorpora incidencias de prácticamente todo el hemisferio. "
            "Los ángulos rasantes se incluyen con su ponderación energética, no con igual peso."
        )
    st.markdown(
        f'<div class="lesson"><b>Interpretación automática:</b> a '
        f'<b>{angular_frequency} Hz</b>, la condición <b>{field_mode}</b> entrega '
        f'<b>TL = {selected_tl:.1f} dB</b> y transmite aproximadamente '
        f'<b>{transmitted_percent:.3g} %</b> de la energía incidente en este modelo '
        f'ideal de masa. {field_explanation}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Ver detalle matemático"):
        st.markdown(
            "Para cada dirección se calcula primero el coeficiente de transmisión "
            "de la hoja simple:"
        )
        st.latex(
            r"\tau(\theta)=\left[1+\left("
            r"\frac{\omega m'\cos\theta}{2\rho_0c}"
            r"\right)^2\right]^{-1}"
        )
        st.markdown(
            "Para los campos angulares, los coeficientes se integran con ponderación "
            "energética y solo después se convierten a decibeles:"
        )
        st.latex(
            r"\overline{\tau}="
            r"\frac{\displaystyle\int_{0}^{\theta_{\max}}\tau(\theta)"
            r"\sin\theta\cos\theta\,d\theta}"
            r"{\displaystyle\int_{0}^{\theta_{\max}}"
            r"\sin\theta\cos\theta\,d\theta}"
        )
        st.latex(r"TL=-10\log_{10}\left(\overline{\tau}\right)")
        st.markdown("""
        - **τ(θ):** coeficiente de transmisión para el ángulo θ.
        - **θ:** ángulo de incidencia medido desde la normal.
        - **ω = 2πf:** frecuencia angular.
        - **m′:** masa superficial de la placa.
        - **ρ₀:** densidad del aire.
        - **c:** velocidad del sonido en el aire.
        - **θmáx:** 78° para el campo de laboratorio y aproximadamente 90° para el
          campo difuso ideal.
        - **τ̄:** coeficiente de transmisión promedio.
        - **TL:** pérdida de transmisión, en dB.

        Los valores de TL no se promedian directamente. Primero se promedia la energía
        mediante τ y luego se transforma el resultado a decibeles.
        """)
    st.markdown("### 9. Explorador de las cuatro zonas")
    material=st.selectbox("Material",["Yeso-cartón","Vidrio","Madera contrachapada","Hormigón"],key="lab2_panel_material")
    props={
        # densidad, espesor, E [GPa], nu, eta aproximada
        "Yeso-cartón":(800,12.5,2.5,.30,.030),
        "Vidrio":(2500,6.0,70.0,.23,.010),
        "Madera contrachapada":(600,18.0,8.0,.30,.025),
        "Hormigón":(2400,100.0,30.0,.20,.020),
    }
    rho,default_h,young,poisson,eta=props[material]
    h=st.slider("Espesor (mm)",4.0,200.0,float(default_h),0.5,key="lab2_panel_h")
    selected_zone=st.radio("Zona que deseas analizar",
        ["1 · Rigidez","2 · Resonancias","3 · Ley de masa","4 · Coincidencia"],
        horizontal=True,key="lab2_selected_zone")
    mass,stiffness,calculated_fc=_critical_frequency(rho,h,young,poisson)
    default_loss=max(5,min(16,5-10*math.log10(eta)))
    curve=_simple_real_curve(mass,calculated_fc,default_loss)
    zone_explanations={
        "1 · Rigidez":(
            "A muy baja frecuencia dominan la rigidez, el tamaño, los apoyos y las "
            "fijaciones. Al variar el material o el espesor cambia la rigidez a "
            "flexión D; por eso esta zona no puede predecirse solo con la masa "
            "superficial m′."
        ),
        "2 · Resonancias":(
            "Los modos propios dependen de la relación D/m′, de las dimensiones y "
            "de los bordes. Una placa más rígida desplaza sus modos; una placa mayor "
            "o más pesada tiende a llevarlos hacia frecuencias menores."
        ),
        "3 · Ley de masa":(
            "Entre las resonancias y la coincidencia domina la inercia. En esta "
            "región resulta útil la ley de masa: al duplicar m′ o la frecuencia, "
            "el aislamiento aumenta aproximadamente 6 dB."
        ),
        "4 · Coincidencia":(
            f"Para la selección actual, la frecuencia crítica es aproximadamente "
            f"{calculated_fc:.0f} Hz. En torno a ella, la onda aérea se acopla con "
            "una onda de flexión de la placa y aumenta la energía transmitida."
        ),
    }
    st.markdown("#### Cómo interpretar la zona seleccionada")
    st.markdown(
        f"**{selected_zone}.** {zone_explanations[selected_zone]} "
        "En el gráfico, el fondo coloreado identifica el intervalo donde domina "
        "este mecanismo."
    )
    if selected_zone=="1 · Rigidez":
        st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    elif selected_zone=="3 · Ley de masa":
        st.latex(r"TL\approx20\log_{10}(m'f)-47")
    elif selected_zone=="4 · Coincidencia":
        st.latex(r"f_c\propto\frac{1}{h}\sqrt{\frac{\rho}{E}}")
    # Rangos didácticos para mostrar dónde domina cada mecanismo. La zona de
    # coincidencia sigue a fᶜ, por lo que cambia al modificar material o espesor.
    zone_highlights={
        "1 · Rigidez":(50,125,"Zona de rigidez","#9ec5fe"),
        "2 · Resonancias":(63,250,"Zona de resonancias","#ffd8a8"),
        "3 · Ley de masa":(
            250,max(315,.80*calculated_fc),"Zona de ley de masa","#b7e4c7"
        ),
        "4 · Coincidencia":(
            .80*calculated_fc,1.25*calculated_fc,
            "Zona de coincidencia","#f3b4c2"
        ),
    }
    _plot_curves([
        ("Respuesta aproximada",curve,"solid"),
        ("Ley de masa ideal",_mass_law_curve(mass),"dash"),
    ],f"{material} · m′ = {mass:.1f} kg/m²",
       [(calculated_fc,"fᶜ")],zone_highlights[selected_zone])
    z1,z2,z3=st.columns(3)
    z1.metric("Masa superficial m′",f"{mass:.1f} kg/m²")
    z2.metric("Rigidez D",f"{stiffness:.1f} N·m")
    z3.metric("Frecuencia crítica fᶜ",f"{calculated_fc:.0f} Hz")
    st.caption("Modelo didáctico: muestra mecanismos y tendencias; no sustituye una curva de ensayo del producto.")
    st.markdown("### 10. Preguntas de comprensión")
    check("lab2_s2_q1",
        "¿De dónde proviene el término aproximado −47 dB de la ley de masa?",
        [
            "De una corrección de incidencia de campo/difusa aplicada a la tendencia controlada por masa",
            "De la frecuencia crítica de cualquier material",
            "De convertir watt directamente en presión sonora",
            "Es una constante universal exacta para todas las placas",
        ],
        "De una corrección de incidencia de campo/difusa aplicada a la tendencia controlada por masa",
        "La aproximación normal conduce a una constante cercana a −42 dB; −47 dB representa una aproximación de campo y no reproduce resonancia ni coincidencia.")
    check("lab2_s2_q2",
        "En el laboratorio angular, ¿qué significa θ = 0°?",
        ["Incidencia normal","Incidencia rasante","Campo difuso","Ausencia de transmisión"],
        "Incidencia normal",
        "El ángulo se mide respecto de la normal a la placa; por ello 0° corresponde a llegada perpendicular.")
    check("lab2_s2_q3",
        "¿Cómo se obtiene correctamente el TL de un campo con múltiples ángulos?",
        [
            "Se promedian energéticamente los τ(θ) y luego se convierten a TL",
            "Se promedian directamente los TL en dB",
            "Se toma solamente el TL a 78°",
            "Se usa siempre el TL a 0°",
        ],
        "Se promedian energéticamente los τ(θ) y luego se convierten a TL",
        "Los decibeles no se promedian aritméticamente para esta operación; primero se combinan coeficientes de transmisión.")
    check("lab2_s2_q4",
        "¿En qué zona es válida la tendencia TL ≈ 20 log₁₀(m′f) − 47?",
        [
            "En la zona controlada por masa, lejos de resonancias y coincidencia",
            "En todas las frecuencias sin excepción",
            "Únicamente en la zona de rigidez",
            "Solo exactamente en la frecuencia crítica",
        ],
        "En la zona controlada por masa, lejos de resonancias y coincidencia",
        "La ley de masa aproximada describe una región, no la curva completa de una placa real.")
    check("lab2_s2_q5",
        "Para una misma placa homogénea, ¿qué tendencia presenta fᶜ al aumentar el espesor?",
        [
            "Disminuye aproximadamente en proporción inversa al espesor",
            "Aumenta en proporción al cubo del espesor",
            "Permanece siempre constante",
            "Se vuelve igual a la primera resonancia modal",
        ],
        "Disminuye aproximadamente en proporción inversa al espesor",
        "Como m′ crece con h y D con h³, fᶜ es aproximadamente proporcional a 1/h para un mismo material.")

def _stage3_impl():
    """Ejercicio comparativo de tres placas simples homogéneas."""
    _lab2_heading(
        3,
        "Ejercicio aplicado: comparación de tres placas simples",
        "Predecir el TL de campo de yeso-cartón, madera y hormigón, y justificar una decisión de diseño.",
    )
    st.markdown("""
    ### Encargo profesional

    Debes seleccionar una **placa homogénea simple** para separar un recinto ruidoso
    de una sala de trabajo. Estudiarás tres alternativas —yeso-cartón, madera y
    hormigón— entre **50 y 5.000 Hz**.

    El propósito no es limitarse a decir que el hormigón aísla más. Debes explicar
    cómo la densidad, el espesor, la rigidez y el amortiguamiento modifican la masa
    superficial, la frecuencia crítica y la curva completa de aislamiento.
    """)
    st.success("""
    **En palabras simples:** probaremos tres “paredes de una sola pieza”. La aplicación
    enviará sonido contra cada una desde muchas direcciones y calculará cuánto logra
    atravesarla. Una curva más alta significa que pasa menos sonido.
    """)
    _lab2_image(
        "panel_simple",
        "Modelo utilizado: una placa homogénea simple, sin cámara, montantes ni una segunda hoja.",
    )
    st.info(
        "**Método común para las tres alternativas:** primero se calcula "
        "τ(θ,f), después se integran energéticamente todas las incidencias entre "
        "0° y 78° y, finalmente, el resultado se transforma en TL de campo."
    )

    st.markdown("### Las tres placas que se compararán")
    image_col_1,image_col_2,image_col_3=st.columns(3)
    with image_col_1:
        st.markdown("#### Yeso-cartón")
        _lab2_image(
            "yeso_carton",
            "Una placa simple de yeso-cartón, sin perfiles, cámara ni segunda hoja.",
        )
        st.markdown(
            "**En palabras simples:** es una hoja liviana. Se mueve con mayor "
            "facilidad cuando recibe sonido y, por eso, normalmente deja pasar más "
            "energía que una placa pesada."
        )
    with image_col_2:
        st.markdown("#### Madera")
        _lab2_image(
            "madera",
            "Un panel simple y macizo de madera, sin entramado ni revestimientos.",
        )
        st.markdown(
            "**En palabras simples:** combina un peso moderado con una rigidez "
            "mayor que la del yeso-cartón. Su respuesta cambia con la frecuencia "
            "y con la facilidad con que el panel puede flexionarse."
        )
    with image_col_3:
        st.markdown("#### Hormigón")
        _lab2_image(
            "hormigon",
            "Un muro simple y macizo de hormigón, sin cámaras ni capas adicionales.",
        )
        st.markdown(
            "**En palabras simples:** concentra mucha masa en cada metro cuadrado. "
            "Cuesta más hacerlo vibrar, por lo que generalmente transmite menos "
            "sonido que las alternativas livianas."
        )
    st.caption(
        "Las imágenes representan una sola hoja homogénea de cada material. "
        "No corresponden a tabiques dobles ni a sistemas con cámara de aire."
    )

    st.markdown("### 1 · Modelo físico utilizado")
    st.markdown("#### Masa superficial")
    st.latex(r"m'=\rho h")
    st.caption("Masa por unidad de superficie de la placa, expresada en kg/m².")
    st.info(
        "**Explicación para no ingenieros:** indica cuánto pesa un metro cuadrado "
        "de la placa. No importa cuánto pesa el muro completo, sino cuánto material "
        "hay en cada m². En general, una placa con mayor masa superficial es más "
        "difícil de mover y puede aislar mejor."
    )

    st.markdown("#### Rigidez a flexión")
    st.latex(r"B=\frac{E h^3}{12}")
    st.caption("Rigidez a flexión por unidad de ancho, expresada en N·m.")
    st.info(
        "**Explicación para no ingenieros:** representa qué tan difícil es doblar "
        "la placa. Una lámina flexible vibra con facilidad; una muy rígida se opone "
        "a curvarse. El espesor influye mucho porque aparece elevado al cubo."
    )

    st.markdown("#### Frecuencia crítica")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{B}}")
    st.caption("Frecuencia a partir de la cual puede producirse el fenómeno de coincidencia.")
    st.info(
        "**Explicación para no ingenieros:** es una frecuencia especialmente "
        "desfavorable. Cerca de ella, el sonido del aire logra hacer vibrar la placa "
        "de manera muy eficiente y el aislamiento puede presentar una caída, aunque "
        "la placa sea pesada."
    )

    st.markdown("#### Coeficiente de transmisión para cada frecuencia y ángulo")
    st.write(
        "Para evitar una expresión excesivamente larga, se definen primero dos "
        "términos auxiliares. Esta forma es algebraicamente equivalente a la "
        "ecuación completa utilizada en el cálculo."
    )
    st.latex(
        r"A(\theta,f)=\frac{\omega m'\cos\theta}{2\rho_0c}"
    )
    st.latex(
        r"C(\theta,f)=\frac{\omega^2 B\sin^4\theta}{c^4m'}"
    )
    st.latex(
        r"\tau(\theta,f)="
        r"\frac{1}{\left[1+\eta A(\theta,f)C(\theta,f)\right]^2"
        r"+\left[A(\theta,f)\left(1-C(\theta,f)\right)\right]^2}"
    )
    st.info(
        "**Explicación para no ingenieros:** τ es la fracción de energía sonora que "
        "consigue atravesar la placa. Si τ es grande, pasa más sonido; si τ es "
        "pequeño, la placa aísla mejor. Se calcula para distintas frecuencias y "
        "ángulos porque el sonido no siempre llega de frente."
    )
    st.markdown("#### Coeficiente de transmisión de campo")
    st.latex(
        r"\overline{\tau}_{campo}(f)=2{,}0904"
        r"\int_0^{78^\circ}\tau(\theta,f)\cos\theta\sin\theta\,d\theta"
    )
    st.info(
        "**Explicación para no ingenieros:** en un recinto real el sonido llega "
        "desde muchas direcciones. Esta integración reúne todas esas incidencias "
        "entre 0° y 78° en un único valor energético representativo del campo sonoro."
    )
    st.markdown("#### Pérdida por transmisión de campo")
    st.latex(
        r"TL_{campo}(f)=10\log_{10}\left(\frac{1}"
        r"{\overline{\tau}_{campo}(f)}\right)"
        r"=-10\log_{10}\left[\overline{\tau}_{campo}(f)\right]"
    )
    st.info(
        "**Explicación para no ingenieros:** TL expresa el aislamiento en decibeles. "
        "Un TL mayor significa que atraviesa menos energía sonora. Por ejemplo, una "
        "subida de la curva indica una mejora; un valle señala una frecuencia donde "
        "la placa está aislando menos."
    )
    st.caption(
        "ω = 2πf; ρ₀ = 1,18 kg/m³; c = 343 m/s. "
        "78° es el límite superior de integración, no un único rayo."
    )
    st.markdown("#### Variables y unidades")
    st.dataframe(
        pd.DataFrame([
            ["ρ", "Densidad del material", "kg/m³"],
            ["h", "Espesor de la placa", "m"],
            ["m′", "Masa superficial", "kg/m²"],
            ["E", "Módulo de Young", "Pa"],
            ["B", "Rigidez a flexión", "N·m"],
            ["η", "Factor de pérdidas", "Adimensional"],
            ["f", "Frecuencia", "Hz"],
            ["ω = 2πf", "Frecuencia angular", "rad/s"],
            ["θ", "Ángulo respecto de la normal", "grados o radianes"],
        ], columns=["Símbolo", "Significado", "Unidad"]),
        use_container_width=True,
        hide_index=True,
    )

    presets={
        "Yeso-cartón":{
            "rho":800.0,"h":12.5,"e":2.5,"eta":0.030,
            "color":"#1677d2",
            "note":"Placa liviana de referencia.",
        },
        "Madera":{
            "rho":600.0,"h":18.0,"e":10.0,"eta":0.020,
            "color":"#d58b16",
            "note":"Modelo isotrópico simplificado; la madera real depende de la dirección de las fibras.",
        },
        "Hormigón":{
            "rho":2400.0,"h":100.0,"e":30.0,"eta":0.010,
            "color":"#d64545",
            "note":"Elemento pesado homogéneo de referencia.",
        },
    }
    frequencies=np.arange(50.0,5000.0+1,10.0)
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    material_results={}

    st.markdown("### 2 · Analiza cada material")
    st.markdown("""
    Recorre las tres pestañas. Puedes modificar los valores de referencia. Para
    comparar correctamente, la aplicación aplicará el mismo intervalo de frecuencia,
    campo angular y ecuaciones a todas las alternativas.
    """)
    st.markdown("""
    **Guía rápida de los controles**

    - **Densidad:** qué tan concentrada está la materia; no es el peso total.
    - **Espesor:** distancia entre las dos caras de esta única placa.
    - **Módulo de Young:** resistencia del material a deformarse.
    - **Factor de pérdidas:** capacidad del material para amortiguar su vibración.
    """)
    tabs=st.tabs(list(presets.keys()))
    for tab,(material,preset) in zip(tabs,presets.items()):
        slug={"Yeso-cartón":"yeso","Madera":"madera","Hormigón":"hormigon"}[material]
        with tab:
            st.markdown(f"#### Caso · {material}")
            st.caption(preset["note"])
            _lab2_image(
                {"Yeso-cartón":"yeso_carton","Madera":"madera",
                 "Hormigón":"hormigon"}[material],
                {
                    "Yeso-cartón":(
                        "Placa simple homogénea de yeso-cartón: una sola hoja, sin "
                        "montantes, cámara ni segunda placa."
                    ),
                    "Madera":(
                        "Panel simple homogéneo de madera: una sola hoja maciza, sin "
                        "entramado, cámara ni revestimientos adicionales."
                    ),
                    "Hormigón":(
                        "Muro simple homogéneo de hormigón: una sola hoja maciza."
                    ),
                }[material],
            )
            st.info(
                "La imagen y el cálculo representan el mismo modelo idealizado: "
                "**una única placa simple, homogénea e infinita**. No se incorporan "
                "montantes, uniones, cavidades, segundas hojas ni transmisiones laterales."
            )
            st.markdown({
                "Yeso-cartón":(
                    "**Cómo interpretar este caso:** al ser una placa liviana y "
                    "delgada, tendrá una masa superficial baja. Observa dónde aparece "
                    "su frecuencia crítica y si la curva presenta allí una pérdida "
                    "de aislamiento."
                ),
                "Madera":(
                    "**Cómo interpretar este caso:** el mayor espesor aumenta tanto "
                    "la masa como, con mucha más fuerza, la rigidez. Comprueba si eso "
                    "hace que su curva y su frecuencia crítica sean distintas de las "
                    "del yeso-cartón."
                ),
                "Hormigón":(
                    "**Cómo interpretar este caso:** su elevada densidad y espesor "
                    "producen una masa superficial muy grande. Compara cuánto aumenta "
                    "el TL y recuerda que aquí se modela solo el material, no sus "
                    "encuentros ni posibles fugas en obra."
                ),
            }[material])
            c1,c2,c3=st.columns(3)
            rho=c1.number_input(
                "Densidad ρ (kg/m³)",300.0,3000.0,preset["rho"],10.0,
                key=f"lab2_s3_{slug}_rho")
            h_mm=c2.number_input(
                "Espesor h (mm)",4.0,300.0,preset["h"],0.5,
                key=f"lab2_s3_{slug}_h")
            young_gpa=c3.number_input(
                "Módulo de Young E (GPa)",0.1,100.0,preset["e"],0.1,
                key=f"lab2_s3_{slug}_e")
            eta=st.number_input(
                "Factor de pérdidas η",0.001,0.200,preset["eta"],0.001,
                format="%.3f",key=f"lab2_s3_{slug}_eta")

            h=h_mm/1000
            surface_mass=rho*h
            stiffness=young_gpa*1e9*h**3/12
            critical_frequency=343.0**2/(2*math.pi)*math.sqrt(surface_mass/stiffness)
            tau_field,tl_field,_,_,_=_panel_simple_field_tl(
                frequencies,surface_mass,stiffness,eta)
            sample_tau,sample_tl,_,_,_=_panel_simple_field_tl(
                sample_frequencies,surface_mass,stiffness,eta)
            material_results[material]={
                "m":surface_mass,"B":stiffness,"fc":critical_frequency,
                "tau":tau_field,"tl":tl_field,"sample_tau":sample_tau,
                "sample_tl":sample_tl,"color":preset["color"],
            }

            m1,m2,m3=st.columns(3)
            m1.metric("Masa superficial m′",f"{surface_mass:.2f} kg/m²")
            m2.metric("Rigidez B",f"{stiffness:,.1f} N·m")
            m3.metric("Frecuencia crítica fᶜ",f"{critical_frequency:,.0f} Hz")
            st.caption(
                "Estos resultados indican cuánto pesa la placa por metro cuadrado, "
                "cuánto se resiste a curvarse y dónde puede aparecer la coincidencia."
            )
            if 50 <= critical_frequency <= 5000:
                st.warning(
                    f"fᶜ = {critical_frequency:,.0f} Hz está dentro del intervalo. "
                    "Busca su efecto en la curva."
                )
            else:
                st.success(
                    f"fᶜ = {critical_frequency:,.0f} Hz queda fuera del intervalo mostrado."
                )

            fig_material=go.Figure()
            fig_material.add_trace(go.Scatter(
                x=frequencies,y=tl_field,mode="lines",name=material,
                line=dict(color=preset["color"],width=4)))
            if 50 <= critical_frequency <= 5000:
                fig_material.add_vline(
                    x=critical_frequency,line_dash="dash",
                    line_color=preset["color"],annotation_text="fᶜ",
                    annotation_position="top")
            fig_material.update_layout(
                title=f"TL de campo · {material}",
                xaxis_title="Frecuencia (Hz) · escala lineal",
                yaxis_title="TL de campo (dB)",
                xaxis=dict(type="linear",range=[50,5000],dtick=500),
                height=420,hovermode="x unified",
                margin=dict(l=40,r=20,t=60,b=45),
                showlegend=False)
            st.plotly_chart(
                fig_material,use_container_width=True,
                key=f"lab2_s3_{slug}_curve")
            st.info(
                "**Cómo leer la curva:** de izquierda a derecha se pasa de sonidos "
                "graves a agudos; cuanto más alta está la línea, mayor es el "
                "aislamiento. Observa qué ocurre cerca de la línea vertical fᶜ."
            )
            st.dataframe(
                pd.DataFrame({
                    "Frecuencia (Hz)":sample_frequencies.astype(int),
                    "τ̄ campo":sample_tau,
                    "Energía transmitida (%)":100*sample_tau,
                    "TL campo (dB)":sample_tl,
                }).style.format({
                    "τ̄ campo":"{:.6f}",
                    "Energía transmitida (%)":"{:.4f}",
                    "TL campo (dB)":"{:.1f}",
                }),
                use_container_width=True,hide_index=True)
            st.caption(
                "La tabla presenta el mismo fenómeno de dos formas: menor energía "
                "transmitida equivale a un TL mayor."
            )

    st.markdown("### 3 · Comparación conjunta")
    st.markdown(
        "Aquí se superponen las tres alternativas. En cada frecuencia, la curva que "
        "queda más arriba entrega el mayor aislamiento según este modelo."
    )
    visible=st.multiselect(
        "Curvas visibles",
        list(presets.keys()),
        default=list(presets.keys()),
        key="lab2_s3_visible_materials",
    )
    comparison=go.Figure()
    for material in visible:
        result=material_results[material]
        comparison.add_trace(go.Scatter(
            x=frequencies,y=result["tl"],mode="lines",name=material,
            line=dict(color=result["color"],width=3)))
        if 50 <= result["fc"] <= 5000:
            comparison.add_vline(
                x=result["fc"],line_dash="dot",line_color=result["color"],
                annotation_text=f"fᶜ {material}",annotation_position="top")
    comparison.update_layout(
        title="Comparación de TL de campo · mismas ecuaciones y campo hasta 78°",
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500),
        height=500,hovermode="x unified",
        margin=dict(l=40,r=20,t=75,b=45),
        legend=dict(orientation="h",y=1.16))
    st.plotly_chart(
        comparison,use_container_width=True,key="lab2_s3_comparison")
    st.info(
        "**No compares solo el espesor.** También importan la densidad, la masa "
        "superficial y la rigidez. Por eso el orden de las curvas puede cambiar "
        "según la frecuencia."
    )

    comparison_rows=[]
    for material,result in material_results.items():
        row={
            "Material":material,
            "m′ (kg/m²)":result["m"],
            "B (N·m)":result["B"],
            "fᶜ (Hz)":result["fc"],
        }
        for i,freq in enumerate(sample_frequencies):
            row[f"TL {int(freq)} Hz"]=result["sample_tl"][i]
        comparison_rows.append(row)
    st.dataframe(
        pd.DataFrame(comparison_rows).style.format({
            "m′ (kg/m²)":"{:.2f}","B (N·m)":"{:,.1f}","fᶜ (Hz)":"{:,.0f}",
            **{f"TL {int(f)} Hz":"{:.1f}" for f in sample_frequencies},
        }),
        use_container_width=True,hide_index=True)
    st.caption(
        "Para justificar tu decisión, compara una misma columna de frecuencia entre "
        "los tres materiales y cita sus valores."
    )
    st.caption(
        "Predicción teórica de placas infinitas y homogéneas. No equivale a un ensayo "
        "normalizado y no incorpora juntas, apoyos, dimensiones finitas, fugas ni flancos."
    )

    st.markdown("### 4 · Decisión de diseño")
    st.markdown("""
    **Restricción del proyecto:** se busca el mayor aislamiento entre **500 y
    2.000 Hz**, pero primero debes comparar el desempeño técnico de las tres
    alternativas. Después, considera que el proyecto exige una solución liviana y
    descarta el hormigón.

    Tu respuesta debe:

    1. Identificar la mayor masa superficial.
    2. Comparar el TL en 500, 1.000 y 2.000 Hz.
    3. Ubicar la frecuencia crítica de cada placa.
    4. Explicar cualquier caída cercana a la coincidencia.
    5. Elegir entre yeso-cartón y madera bajo la restricción de bajo peso.
    """)
    saved_decision=_saved_formative_response(3,"lab2_s3_design_decision")
    saved_answer=(saved_decision or {}).get("answer") or {}
    if "lab2_s3_design_decision" not in st.session_state and isinstance(saved_answer,dict) and saved_answer.get("value"):
        st.session_state["lab2_s3_design_decision"]=str(saved_answer.get("value"))
    decision=st.text_area(
        "Conclusión técnica y alternativa seleccionada",
        key="lab2_s3_design_decision",height=160,
        placeholder=(
            "La alternativa con mayor m′ es... Entre 500 y 2.000 Hz se observa... "
            "Las frecuencias críticas son... Al excluir el hormigón, seleccionaría... porque..."
        ))
    _render_saved_activity_state(saved_decision)
    decision_label="Actualizar respuesta" if saved_decision else "Comprobar y guardar"
    if st.button(decision_label,key="lab2_s3_check_decision"):
        if len(decision.strip()) < 140:
            level="Parcialmente correcta"
            feedback="La justificación aún es breve. Incluye valores de m′, fᶜ y TL en al menos dos frecuencias, y explica la selección liviana."
        else:
            level="Correcta"
            feedback="La extensión es suficiente. Verifica que tu elección se apoye en los resultados calculados y no solamente en el nombre o espesor del material."
        if _save_formative(3,"lab2_s3_design_decision","Conclusión técnica y alternativa seleccionada",decision,level,feedback,score=0,max_score=0):
            st.rerun()
        else:
            st.error("No fue posible guardar el desarrollo. Intenta nuevamente.")

    st.markdown("### 5 · Comprobación conceptual")
    check(
        "lab2_s3_compare_q1",
        "¿Por qué se integran los coeficientes τ antes de calcular el TL de campo?",
        [
            "Porque primero debe combinarse la energía transmitida y después convertirse a decibeles",
            "Porque los valores de TL no dependen del ángulo",
            "Porque 78° representa una única incidencia real",
            "Porque así se elimina la frecuencia crítica",
        ],
        "Porque primero debe combinarse la energía transmitida y después convertirse a decibeles",
        "El promedio se realiza en magnitudes energéticas; los TL angulares no se promedian directamente.",
    )
    check(
        "lab2_s3_compare_q2",
        "¿Qué afirmación interpreta correctamente la comparación?",
        [
            "El desempeño depende de masa superficial, rigidez, amortiguamiento y frecuencia",
            "La placa más gruesa siempre posee la frecuencia crítica más alta",
            "Todos los materiales de igual espesor producen la misma curva",
            "La coincidencia se añade dibujando una corrección artificial",
        ],
        "El desempeño depende de masa superficial, rigidez, amortiguamiento y frecuencia",
        "La curva surge del mismo modelo físico para las tres placas; no basta comparar solamente espesores.",
    )
    check(
        "lab2_s3_compare_q3",
        "Si aumenta el espesor de una placa manteniendo su densidad, ¿qué ocurre directamente con su masa superficial?",
        [
            "Aumenta, porque m′ = ρh",
            "Disminuye, porque la placa se vuelve más rígida",
            "Permanece constante, porque solo depende del material",
            "Se hace igual a la densidad del aire",
        ],
        "Aumenta, porque m′ = ρh",
        "La masa superficial es proporcional tanto a la densidad como al espesor de la placa.",
    )
    check(
        "lab2_s3_compare_q4",
        "¿Qué representa una disminución del TL alrededor de la frecuencia crítica?",
        [
            "Una mayor transmisión asociada al fenómeno de coincidencia",
            "La desaparición completa de la vibración de la placa",
            "Un aumento automático de la masa superficial",
            "Un error producido por usar frecuencia lineal",
        ],
        "Una mayor transmisión asociada al fenómeno de coincidencia",
        "Cerca de la frecuencia crítica se favorece el acoplamiento entre el campo sonoro y las ondas de flexión de la placa.",
    )
    check(
        "lab2_s3_compare_q5",
        "¿Por qué la imagen del sistema constructivo real no debe interpretarse como una predicción completa del tabique?",
        [
            "Porque el ejercicio modela una placa homogénea e infinita y no incorpora juntas, apoyos ni flancos",
            "Porque las imágenes no tienen dimensiones escritas",
            "Porque el hormigón no puede analizarse mediante masa superficial",
            "Porque el modelo solo funciona para incidencia normal",
        ],
        "Porque el ejercicio modela una placa homogénea e infinita y no incorpora juntas, apoyos ni flancos",
        "El modelo permite estudiar el material aislado, pero no reemplaza la evaluación del elemento instalado en obra.",
    )

def _stage4_impl():
    """Explicación técnica de dos placas simples separadas por una cámara de aire."""
    _lab2_heading(
        4,
        "Pérdida de transmisión en paneles dobles",
        "Comprender el sistema masa–aire–masa, sus frecuencias características y las tres regiones del modelo.",
    )
    _lab2_image(
        "panel_doble",
        "Modelo idealizado: dos placas homogéneas simples separadas por una cámara de aire.",
    )
    st.markdown(r"""
    ### Introducción

    Un panel doble está formado por **dos placas separadas por una cámara de
    aire**. A diferencia de una placa simple, su comportamiento no depende
    solamente de la masa y la rigidez de cada hoja: el aire encerrado actúa como
    un resorte y acopla el movimiento de ambas placas.

    El conjunto puede representarse como un sistema **masa–aire–masa**:

    - La placa 1 constituye la primera masa.
    - La cámara de aire aporta la elasticidad.
    - La placa 2 constituye la segunda masa.

    Este mecanismo produce una frecuencia de resonancia \(f_0\) y obliga a
    estudiar la pérdida por transmisión mediante tres regiones. Por eso, agregar
    una segunda placa no genera la misma mejora en todas las frecuencias.
    """)
    st.info(
        "**Continuidad con la Etapa 3:** cada hoja se calcula primero como una placa "
        "simple con integración de campo entre 0° y 78°. Después, ambas curvas se "
        "combinan mediante la ecuación de panel doble."
    )
    st.caption(
        "En esta explicación se utiliza el modelo teórico ideal. Las correcciones "
        "por absorbente, montantes, fijaciones, fugas y transmisiones laterales no "
        "forman parte de esta etapa."
    )

    st.markdown("### 1 · Propiedades de las dos placas")
    st.markdown(r"""
        Cada hoja conserva las propiedades del panel simple estudiado en la
        Etapa 3. Para la placa \(i\):
    """)
    st.latex(r"m'_i=\rho_i h_i")
    st.latex(r"B_i=\frac{E_i h_i^3}{12}")
    st.caption(
        "Para cada hoja i, m′ es la masa superficial en kg/m² y B es la rigidez "
        "a flexión en N·m."
    )
    _lab2_image(
        "s4_propiedades_placas",
        "Cada hoja aporta masa superficial y rigidez a flexión al sistema doble.",
    )
    _lab2_plain_language_cards(
        "Cada placa conserva su propio peso por metro cuadrado y su propia resistencia a doblarse.",
        "El espesor aumenta la masa linealmente, pero la rigidez crece con el cubo del espesor.",
        "Suponer que dos placas separadas por aire se comportan desde el inicio como una sola placa gruesa.",
    )

    st.markdown("### 2 · Resonancia masa–aire–masa")
    st.markdown(r"""
    En \(f_0\), las dos placas y el aire de la cámara interactúan con mayor
    intensidad. Esta resonancia constituye una zona desfavorable porque puede
    reducir el aislamiento del sistema. Su posición depende de las masas
    superficiales y de la profundidad \(d\) de la cámara:
    """)
    st.latex(
        r"f_0=\frac{1}{2\pi}"
        r"\sqrt{\rho_0c^2}"
        r"\sqrt{\frac{m'_1+m'_2}{m'_1m'_2d}}"
    )
    st.markdown(r"""
    Al aumentar la masa de las hojas o la profundidad de la cámara, \(f_0\)
    normalmente se desplaza hacia frecuencias más bajas.

    La segunda frecuencia característica, \(f_1\), marca el cambio hacia la
    región superior del modelo:
    """)
    st.latex(r"f_1=\frac{c}{2\pi d}")
    st.caption(
        "En ambas expresiones, d se ingresa en metros; ρ₀ = 1,18 kg/m³ y c = 343 m/s."
    )
    _lab2_image(
        "s4_resonancia",
        "En la resonancia, las dos masas quedan acopladas por el resorte neumático de la cámara.",
    )
    _lab2_plain_language_cards(
        "Las placas son las masas y el aire encerrado funciona como un resorte que las conecta.",
        "Una cámara más profunda o placas más pesadas desplazan normalmente f₀ hacia frecuencias bajas.",
        "Pensar que agregar una segunda placa siempre mejora el aislamiento: cerca de f₀ puede aparecer una caída.",
    )

    st.markdown("### 3 · Ecuación por regiones")
    st.latex(
        r"TL_D(f)=\begin{cases}"
        r"TL_{eq}(f), & f<f_0\\[4pt]"
        r"TL_1(f)+TL_2(f)+20\log_{10}(fd)-29, & f_0\leq f<f_1\\[4pt]"
        r"TL_1(f)+TL_2(f)+6, & f\geq f_1"
        r"\end{cases}"
    )
    st.markdown(r"""
    **Región 1 · Bajo \(f_0\).** Las placas se comportan de manera acoplada y se
    representan como un panel equivalente. Todavía no se obtiene el beneficio
    completo de la cámara.
    """)
    st.latex(r"m'_{eq}=m'_1+m'_2")
    st.latex(r"B_{eq}=B_1+B_2")
    st.latex(r"\eta_{eq}=\eta_1+\eta_2")
    st.markdown(r"""
    **Región 2 · Entre \(f_0\) y \(f_1\).** Se desarrolla el comportamiento
    masa–aire–masa. La pérdida por transmisión depende de las dos placas y
    aparece explícitamente la profundidad \(d\) de la cámara.

    **Región 3 · Sobre \(f_1\).** El modelo combina la pérdida por transmisión
    de ambas hojas y agrega 6 dB.
    """)
    st.caption(
        "TL₁, TL₂ y TLₑq se obtienen con el mismo cálculo angular y de campo "
        "utilizado para las placas simples en la Etapa 3."
    )
    _lab2_image(
        "s4_regiones",
        "La respuesta del panel doble cambia al atravesar f₀ y f₁.",
    )
    _lab2_plain_language_cards(
        "La curva no se calcula con una sola regla: el modelo cambia según la frecuencia.",
        "Bajo f₀ domina el conjunto acoplado; entre f₀ y f₁ actúa masa–aire–masa; sobre f₁ se combinan ambas hojas.",
        "Aplicar la ecuación de la región central a todo el espectro o interpretar las discontinuidades como un fenómeno real exacto.",
    )

    materials={
        "Yeso-cartón":{"rho":800.0,"E":2.5,"eta":0.030,"h":12.5},
        "Madera":{"rho":600.0,"E":10.0,"eta":0.020,"h":18.0},
        "Hormigón":{"rho":2400.0,"E":30.0,"eta":0.010,"h":100.0},
    }
    st.markdown("### 4 · Explorador técnico del modelo")
    st.markdown(
        "Modifica los parámetros para observar cómo cambian las masas superficiales, "
        "las frecuencias características y la curva. Esta sección ilustra la teoría; "
        "el ejercicio de aplicación aparece al final."
    )
    col_left,col_right=st.columns(2)
    with col_left:
        st.markdown("#### Placa 1")
        material_1=st.selectbox(
            "Material de la placa 1",list(materials),index=0,
            key="lab2_s4_material_1")
        default_1=materials[material_1]
        h1_mm=st.number_input(
            "Espesor de la placa 1 (mm)",4.0,300.0,float(default_1["h"]),0.5,
            key="lab2_s4_h1")
    with col_right:
        st.markdown("#### Placa 2")
        material_2=st.selectbox(
            "Material de la placa 2",list(materials),index=0,
            key="lab2_s4_material_2")
        default_2=materials[material_2]
        h2_mm=st.number_input(
            "Espesor de la placa 2 (mm)",4.0,300.0,float(default_2["h"]),0.5,
            key="lab2_s4_h2")
    depth_mm=st.slider(
        "Profundidad de la cámara d (mm)",20,300,70,5,
        key="lab2_s4_depth")

    h1=h1_mm/1000
    h2=h2_mm/1000
    d=depth_mm/1000
    m1=default_1["rho"]*h1
    m2=default_2["rho"]*h2
    b1=default_1["E"]*1e9*h1**3/12
    b2=default_2["E"]*1e9*h2**3/12
    eta1=default_1["eta"]
    eta2=default_2["eta"]
    rho_air=1.18
    sound_speed=343.0
    f0=(1/(2*math.pi))*math.sqrt(rho_air*sound_speed**2)*math.sqrt(
        (m1+m2)/(m1*m2*d)
    )
    f1=sound_speed/(2*math.pi*d)

    frequencies=np.arange(50.0,5000.0+1,10.0)
    _,tl1,_,_,_=_panel_simple_field_tl(frequencies,m1,b1,eta1)
    _,tl2,_,_,_=_panel_simple_field_tl(frequencies,m2,b2,eta2)
    _,tl_equivalent,_,_,_=_panel_simple_field_tl(
        frequencies,m1+m2,b1+b2,eta1+eta2
    )
    tl_double=np.empty_like(frequencies)
    region_1=frequencies < f0
    region_2=(frequencies >= f0) & (frequencies < f1)
    region_3=frequencies >= f1
    tl_double[region_1]=tl_equivalent[region_1]
    tl_double[region_2]=(
        tl1[region_2]+tl2[region_2]
        +20*np.log10(frequencies[region_2]*d)-29
    )
    tl_double[region_3]=tl1[region_3]+tl2[region_3]+6

    a,b,c,d_metric=st.columns(4)
    a.metric("Masa placa 1",f"{m1:.2f} kg/m²")
    b.metric("Masa placa 2",f"{m2:.2f} kg/m²")
    c.metric("Resonancia f₀",f"{f0:.0f} Hz")
    d_metric.metric("Transición f₁",f"{f1:.0f} Hz")

    st.markdown("#### Curva y tres regiones del modelo")
    st.markdown(
        "La curva azul gruesa representa el **TL del sistema doble**. Las líneas "
        "punteadas muestran el comportamiento de cada placa por separado. Los fondos "
        "de color identifican las tres regiones del modelo y las líneas verticales "
        "marcan las frecuencias características calculadas para la configuración actual."
    )
    fig=go.Figure()
    fig.add_vrect(
        x0=50,x1=min(f0,5000),fillcolor="#dcecff",opacity=.42,
        line_width=0)
    if f0 < 5000:
        fig.add_vrect(
            x0=max(50,f0),x1=min(f1,5000),fillcolor="#fff0cf",opacity=.42,
            line_width=0)
    if f1 < 5000:
        fig.add_vrect(
            x0=max(50,f1),x1=5000,fillcolor="#dcf5e8",opacity=.42,
            line_width=0)
    # El panel doble se dibuja primero para que las curvas de cada placa
    # permanezcan visibles por encima, incluso cuando siguen valores cercanos.
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl_double,mode="lines",name="Panel doble",
        line=dict(color="#173f63",width=5)))
    # Los marcadores alternados permiten reconocer ambas placas cuando son
    # idénticas y sus curvas coinciden exactamente.
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl1,mode="lines",
        name=f"Placa 1: {material_1}",
        line=dict(color="#1976d2",width=2.5,dash="dash")))
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl2,mode="lines",
        name=f"Placa 2: {material_2}",
        line=dict(color="#e07a00",width=2.5,dash="dot")))
    marker_step=max(1,len(frequencies)//16)
    fig.add_trace(go.Scatter(
        x=frequencies[::marker_step],y=tl1[::marker_step],
        mode="markers",showlegend=False,hoverinfo="skip",
        marker=dict(color="#1976d2",size=6,symbol="circle")))
    fig.add_trace(go.Scatter(
        x=frequencies[marker_step//2::marker_step],
        y=tl2[marker_step//2::marker_step],
        mode="markers",showlegend=False,hoverinfo="skip",
        marker=dict(
            color="white",line=dict(color="#e07a00",width=2),
            size=8,symbol="diamond")))
    if 50 <= f0 <= 5000:
        fig.add_vline(x=f0,line_dash="dash",line_color="#d64545",
                      annotation_text="f₀",annotation_position="top right")
    if 50 <= f1 <= 5000:
        fig.add_vline(x=f1,line_dash="dash",line_color="#16845b",
                      annotation_text="f₁",annotation_position="top right")
    fig.update_layout(
        title=dict(
            text="Pérdida por transmisión del sistema de panel doble",
            x=.5,
            xanchor="center",
            font=dict(size=20,color="#173f63"),
        ),
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500,showgrid=True),
        yaxis=dict(showgrid=True,gridcolor="rgba(23,63,99,.10)"),
        height=650,hovermode="x unified",
        margin=dict(l=65,r=30,t=90,b=145),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-.20,
            xanchor="center",
            x=.5,
            title_text="",
            bgcolor="rgba(255,255,255,.92)",
            bordercolor="rgba(23,63,99,.18)",
            borderwidth=1,
            font=dict(size=13),
        ))
    st.plotly_chart(fig,use_container_width=True,key="lab2_s4_double_curve")
    st.caption(
        "Las discontinuidades en f₀ y f₁ pertenecen a la formulación idealizada por "
        "tramos. La predicción no incorpora fugas, uniones rígidas ni transmisiones laterales."
    )
    _lab2_plain_language_cards(
        "Mueve los materiales, espesores y la cámara para ver cómo cambia la pared completa, no solo una placa.",
        "Observa primero dónde quedan f₀ y f₁; después compara la línea gruesa del panel doble con las dos líneas punteadas.",
        "Elegir la mejor solución mirando un único valor máximo de TL e ignorar la caída de resonancia y la banda de interés.",
    )

    st.markdown("#### Resultados por frecuencia")
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    sample_indices=[int(np.argmin(np.abs(frequencies-f))) for f in sample_frequencies]
    table=pd.DataFrame({
        "Frecuencia (Hz)":sample_frequencies.astype(int),
        "TL placa 1 (dB)":tl1[sample_indices],
        "TL placa 2 (dB)":tl2[sample_indices],
        "TL panel doble (dB)":tl_double[sample_indices],
        "Región":[
            "1 · Panel equivalente" if f < f0 else
            "2 · Masa–aire–masa" if f < f1 else
            "3 · Región superior"
            for f in sample_frequencies
        ],
    })
    st.dataframe(
        table.style.format({
            "TL placa 1 (dB)":"{:.1f}",
            "TL placa 2 (dB)":"{:.1f}",
            "TL panel doble (dB)":"{:.1f}",
        }),
        use_container_width=True,hide_index=True)

    st.markdown("### 5 · Ejercicio breve de aplicación")
    st.markdown(r"""
    Una sala de máquinas debe separarse de una oficina mediante dos placas y una
    cámara de aire. Utiliza el explorador con la configuración seleccionada y:

    1. Informa \(m'_1\), \(m'_2\), \(f_0\) y \(f_1\).
    2. Identifica qué región está activa a 125, 500, 1.000 y 4.000 Hz.
    3. Compara el \(TL\) del panel doble con el de cada placa simple.
    4. Modifica solamente la profundidad de la cámara y explica cómo cambian
       \(f_0\), \(f_1\) y el comportamiento entre 500 y 2.000 Hz.
    5. Recomienda una profundidad de cámara y justifica técnicamente tu decisión.
    """)
    saved_analysis=_saved_formative_response(4,"lab2_s4_analysis")
    saved_answer=(saved_analysis or {}).get("answer") or {}
    if "lab2_s4_analysis" not in st.session_state and isinstance(saved_answer,dict) and saved_answer.get("value"):
        st.session_state["lab2_s4_analysis"]=str(saved_answer.get("value"))
    analysis=st.text_area(
        "Conclusión técnica",
        key="lab2_s4_analysis",height=150,
        placeholder=(
            "Las masas superficiales son... La resonancia f₀ aparece en... "
            "Entre 500 y 2.000 Hz el sistema... Aumentaría/disminuiría la cámara porque..."
        ))
    _render_saved_activity_state(saved_analysis)
    analysis_label="Actualizar respuesta" if saved_analysis else "Comprobar y guardar"
    if st.button(analysis_label,key="lab2_s4_check_analysis"):
        if len(analysis.strip()) < 140:
            level="Parcialmente correcta"
            feedback="La conclusión aún es breve. Incluye m′₁, m′₂, f₀, f₁, al menos dos valores de TL y una decisión sobre la cámara."
        else:
            level="Correcta"
            feedback="La extensión es suficiente. Verifica que tu decisión se apoye en los valores calculados y en la región activa del modelo."
        if _save_formative(4,"lab2_s4_analysis","Conclusión técnica del panel doble",analysis,level,feedback,score=0,max_score=0):
            st.rerun()
        else:
            st.error("No fue posible guardar el análisis. Intenta nuevamente.")

    st.markdown("### 6 · Comprobación conceptual")
    check(
        "lab2_s4_q1",
        "¿Qué representa físicamente el aire contenido en la cámara?",
        ["Un resorte acústico","Una tercera placa rígida","Una fuente sonora","Una fuga"],
        "Un resorte acústico",
        "Las dos placas actúan como masas y el aire encerrado aporta la elasticidad del sistema."
    )
    check(
        "lab2_s4_q2",
        "¿Qué sucede normalmente con f₀ al aumentar la profundidad de la cámara?",
        ["Disminuye","Aumenta","No cambia","Se hace igual a f₁"],
        "Disminuye",
        "Al aumentar d disminuye la rigidez efectiva del resorte de aire y la resonancia se desplaza hacia abajo."
    )
    check(
        "lab2_s4_q3",
        "¿Qué modelo se aplica por debajo de f₀?",
        [
            "Un panel equivalente con masas, rigideces y pérdidas combinadas",
            "La suma de ambas placas más 6 dB",
            "Solo la placa más pesada",
            "La ecuación de la cámara sin considerar las placas",
        ],
        "Un panel equivalente con masas, rigideces y pérdidas combinadas",
        "Bajo f₀ el cálculo utiliza m′eq, Beq y ηeq para representar la respuesta conjunta."
    )
    check(
        "lab2_s4_q4",
        "¿Cuál expresión corresponde a la región entre f₀ y f₁?",
        [
            "TL₁ + TL₂ + 20 log₁₀(fd) − 29",
            "TL₁ + TL₂ + 6",
            "TL de la placa 1 solamente",
            "20 log₁₀(m′₁ + m′₂)",
        ],
        "TL₁ + TL₂ + 20 log₁₀(fd) − 29",
        "En la región intermedia intervienen ambas hojas y aparece explícitamente la profundidad de la cámara."
    )
    check(
        "lab2_s4_q5",
        "¿Por qué esta curva no predice por sí sola el desempeño completo de un tabique construido?",
        [
            "Porque no incorpora montantes, fijaciones, fugas, encuentros ni transmisiones laterales",
            "Porque solo puede calcularse a 78 Hz",
            "Porque las masas superficiales no afectan el aislamiento",
            "Porque un panel doble siempre funciona como una placa simple",
        ],
        "Porque no incorpora montantes, fijaciones, fugas, encuentros ni transmisiones laterales",
        "El ejercicio representa el mecanismo ideal de dos placas y una cámara; la obra agrega caminos estructurales y defectos posibles."
    )

def _stage5_impl():
    _lab2_heading(
        5,
        "Del panel doble ideal al tabique real",
        "Distinguir conexiones lineales metálicas y de madera, y reconocer el principio de una conexión puntual.",
    )

    st.markdown("""
    En la Etapa 4 estudiamos dos hojas y una cámara como un sistema ideal. Un tabique
    construido necesita perfiles, fijaciones y encuentros para sostenerse. Cuando un
    mismo montante une mecánicamente ambas caras aparece un **puente estructural**:
    parte de la vibración evita el camino puramente aéreo de la cámara y se transmite
    por una conexión continua.
    """)
    _lab2_image(
        "s5_tabique_real",
        "Tabique real: placas, cámara absorbente, perfiles y fijaciones forman un solo sistema constructivo.",
    )
    _lab2_plain_language_cards(
        "La cámara no trabaja sola. Los tornillos y montantes pueden funcionar como un camino rígido entre una cara y la otra.",
        "Sigue la energía ámbar que llega a la primera placa y el camino cian que atraviesa los perfiles.",
        "Suponer que agregar lana mineral elimina el puente rígido. El absorbente ayuda a la cámara, pero no desacopla las placas.",
    )

    st.markdown("### 1 · Sistema ideal y sistema conectado")
    st.markdown("""
    En un sistema independiente cada hoja pertenece a una estructura diferente y la
    transmisión está dominada por las dos masas, la cámara y su amortiguamiento. En
    una conexión lineal, un montante o pie derecho continuo acopla ambas caras a lo
    largo de una línea. Esa unión cambia el mecanismo y limita el beneficio del
    desacoplamiento.
    """)
    _lab2_image(
        "s5_ideal_vs_conectado",
        "Comparación conceptual: doble estructura independiente y estructura conectada mediante montantes continuos.",
    )
    _lab2_plain_language_cards(
        "Dos hojas separadas pueden vibrar con mayor independencia. Si las amarramos con el mismo perfil, la vibración encuentra un atajo.",
        "Compara la intensidad de la onda transmitida y la concentración de energía en las uniones.",
        "Comparar ambos sistemas solo por su masa total. La forma en que las hojas están conectadas también controla el resultado.",
    )

    st.markdown("### 2 · Conexión lineal con perfilería metálica")
    st.markdown("""
    En un tabique de yeso-cartón, los tornillos fijan ambas caras a montantes metálicos
    compartidos. Cada montante forma una **línea vertical continua de conexión
    estructural**. La vibración de la primera hoja puede entrar al perfil y volver a
    radiarse desde la segunda hoja a lo largo de esa línea.
    """)
    _lab2_image(
        "s5_conexion_lineal_metal",
        "Conexión lineal metálica: las dos caras quedan vinculadas por montantes continuos de acero galvanizado.",
    )
    _lab2_plain_language_cards(
        "El perfil metálico funciona como un puente largo y continuo entre las dos caras del tabique.",
        "Sigue el recorrido placa → tornillos → montante metálico → tornillos → placa opuesta.",
        "Creer que cada tornillo constituye por sí solo una conexión puntual. Aquí los tornillos descargan sobre un mismo perfil continuo: el conjunto se modela como conexión lineal.",
    )

    st.markdown("### 3 · Conexión lineal con pies derechos de madera")
    st.markdown("""
    El principio es el mismo cuando ambas caras se fijan a un **pie derecho continuo
    de madera**. Cambia el material y su rigidez, pero la geometría de la unión sigue
    siendo lineal: el elemento estructural se prolonga verticalmente y conecta las
    hojas a lo largo de toda su altura.
    """)
    _lab2_image(
        "s5_conexion_lineal_madera",
        "Conexión lineal de madera: ambas caras se fijan a pies derechos continuos compartidos.",
    )
    _lab2_plain_language_cards(
        "Aunque sea madera, el pie derecho también crea un camino estructural continuo entre ambas caras.",
        "Observa que la energía se distribuye a lo largo de cada elemento vertical y no solo en un punto aislado.",
        "Clasificar la unión por el material. Lo que define que sea lineal es la continuidad geométrica del contacto, no que el montante sea metálico o de madera.",
    )

    st.markdown("### 4 · Conexión puntual")
    st.markdown("""
    Una materialización constructiva real del apoyo puntual es el sistema de
    **clips acústicos resilientes**. Cada clip se fija al montante en una posición
    discreta y sostiene un canal metálico horizontal. Las dos placas de esa cara se
    atornillan al canal, no directamente al montante.

    El contacto con la estructura primaria queda concentrado en los clips separados.
    El canal es continuo porque debe sostener las placas, pero su vínculo con los
    montantes ocurre solo en esos puntos resilientes. El resultado depende del tipo,
    rigidez, separación y carga admisible de los clips, además de la configuración
    completa del tabique.
    """)
    _lab2_image(
        "s5_conexion_puntual",
        "Apoyo puntual real: clips resilientes separados fijan canales horizontales que reciben las dos placas de una cara.",
    )
    _lab2_plain_language_cards(
        "Las placas descansan sobre canales; los canales se conectan a los montantes mediante clips separados que reducen el puente rígido directo.",
        "Sigue el montaje real: montante → clip resiliente → canal horizontal → dos placas de yeso-cartón.",
        "Confundir el canal horizontal con una conexión lineal rígida al montante. El canal es continuo, pero se apoya en clips discretos y resilientes.",
    )

    st.markdown("### 5 · Comparación constructiva")
    st.markdown("""
    | Tipo de conexión | Cómo se reconoce | Camino estructural |
    |---|---|---|
    | Lineal metálica | Ambas caras fijadas a un perfil metálico continuo compartido | A lo largo del montante |
    | Lineal de madera | Ambas caras fijadas a un pie derecho continuo compartido | A lo largo del pie derecho |
    | Puntual resiliente | Clips separados fijados a montantes sostienen canales horizontales | Concentrado en cada clip antes de distribuirse por el canal |

    **Idea clave:** metal y madera corresponden a dos materializaciones de una
    conexión lineal rígida. El sistema de clips introduce apoyos puntuales
    resilientes reales; no debe calcularse con la ecuación de conexión lineal sin
    disponer del modelo o de datos de ensayo del sistema específico.
    """)

    st.markdown("### 6 · Cómo se obtiene el TL total del tabique")
    st.markdown("""
    El tabique transmite energía simultáneamente por dos caminos: el campo
    acústico de la cámara y las conexiones rígidas. Por ello, sus pérdidas por
    transmisión no se suman ni se restan directamente en decibeles. Primero se
    calcula cada camino, luego se transforma cada TL en coeficiente de transmisión
    y finalmente se suman las energías transmitidas.
    """)

    st.markdown("#### 6.1 · Camino aéreo: TL base con cámara vacía")
    st.markdown("""
    Es la pérdida por transmisión de las dos hojas separadas por una **cámara de
    aire vacía**, antes de incorporar montantes o material absorbente. Se calcula
    por bandas de frecuencia y cambia según la región en que se encuentre el
    sistema.
    """)
    st.latex(r"""
    TL_{\mathrm{base}}(f)=
    \begin{cases}
    TL_{m'_1+m'_2}(f), & f<f_0 \\[4pt]
    TL_1(f)+TL_2(f)+20\log_{10}(f\,d)-29, & f_0\leq f<f_l \\[4pt]
    TL_1(f)+TL_2(f)+6, & f\geq f_l
    \end{cases}
    """)
    st.latex(
        r"f_0=\frac{1}{2\pi}\sqrt{\rho_0c^2"
        r"\left(\frac{m'_1+m'_2}{m'_1m'_2d}\right)}"
    )
    st.latex(r"f_l=\frac{c}{2\pi d}")
    st.markdown(r"""
- $TL_1(f)$ y $TL_2(f)$: pérdida por transmisión de cada hoja.
- $TL_{m'_1+m'_2}(f)$: pérdida por transmisión de una hoja equivalente con la masa superficial total.
- $d$: profundidad de la cámara, en metros.
- $f_0$: frecuencia de resonancia masa–aire–masa.
- $f_l$: frecuencia límite utilizada para separar las regiones del modelo.
    """)

    st.markdown("#### 6.2 · Camino estructural: TL de la conexión lineal")
    st.markdown("""
    Cuando ambas caras se vinculan mediante montantes continuos, el modelo
    simplificado representa el sistema conectado a partir de una hoja equivalente
    y una corrección asociada a la geometría de las líneas de unión.
    """)
    st.latex(r"TL_{\mathrm{línea}}(f)=TL_{m'_1+m'_2}(f)+\Delta TL_{m'}")
    st.latex(
        r"\Delta TL_{m'}="
        r"10\log_{10}(b\,f_c)+"
        r"20\log_{10}\left(\frac{m'_1}{m'_1+m'_2}\right)-18"
    )
    st.markdown(r"""
- $b$: separación entre líneas de conexión o montantes, en metros.
- $f_c$: frecuencia crítica más alta de las dos hojas, en Hz.
- $m'_1$ y $m'_2$: masas superficiales de las hojas 1 y 2, en $\mathrm{kg/m^2}$.
- $TL_{m'_1+m'_2}(f)$: pérdida por transmisión de una hoja equivalente cuya masa superficial es $m'_1+m'_2$.
- $\Delta TL_{m'}$: corrección, en decibeles, asociada a la conexión lineal.
    """)

    st.markdown("#### 6.3 · TL total con cámara vacía")
    st.markdown("""
    El camino aéreo y el camino estructural actúan **en paralelo**. Para
    combinarlos, cada pérdida por transmisión se convierte primero en su
    coeficiente de transmisión:
    """)
    st.latex(r"\tau_{\mathrm{base}}(f)=10^{-TL_{\mathrm{base}}(f)/10}")
    st.latex(r"\tau_{\mathrm{línea}}(f)=10^{-TL_{\mathrm{línea}}(f)/10}")
    st.latex(
        r"\boxed{TL_{\mathrm{total}}(f)=-10\log_{10}\left["
        r"10^{-TL_{\mathrm{base}}(f)/10}+"
        r"10^{-TL_{\mathrm{línea}}(f)/10}\right]}"
    )
    st.markdown("""
    El resultado queda siempre controlado por el camino que transmite más
    energía, es decir, por el que posee el TL más bajo. Si ambos caminos tienen
    exactamente el mismo TL, su combinación entrega 3 dB menos que cada camino
    por separado.
    """)

    st.markdown("#### 6.4 · Camino aéreo con material absorbente")
    st.markdown("""
    El material poroso incorporado dentro de la cámara disipa energía mediante
    pérdidas viscosas y térmicas, reduce las reflexiones internas y amortigua el
    acoplamiento acústico entre las hojas. Su aporte modifica únicamente el
    camino aéreo de la cámara:
    """)
    st.latex(
        r"TL_{\mathrm{abs}}(f)="
        r"TL_{\mathrm{base}}(f)+\Delta TL_{\mathrm{abs}}(f)"
    )
    st.markdown(r"""
- $\Delta TL_{\mathrm{abs}}(f)$: mejora por banda asociada al amortiguamiento de la cámara.
- El absorbente **no elimina** el camino mecánico formado por montantes y fijaciones.
- Su efecto real depende de la frecuencia, resistividad al flujo, espesor, profundidad de cámara y porcentaje de llenado; no solamente de la densidad nominal.
    """)

    st.markdown("#### 6.5 · TL total con conexión lineal y absorbente")
    st.markdown("""
    El resultado final se obtiene combinando el camino aéreo ya amortiguado con
    el camino estructural, que permanece activo:
    """)
    st.latex(r"\tau_{\mathrm{abs}}(f)=10^{-TL_{\mathrm{abs}}(f)/10}")
    st.latex(r"\tau_{\mathrm{total,abs}}(f)=\tau_{\mathrm{abs}}(f)+\tau_{\mathrm{línea}}(f)")
    st.latex(
        r"\boxed{TL_{\mathrm{total,abs}}(f)=-10\log_{10}\left["
        r"10^{-TL_{\mathrm{abs}}(f)/10}+"
        r"10^{-TL_{\mathrm{línea}}(f)/10}\right]}"
    )
    st.markdown(r"""
    **Lectura física:** el absorbente reduce la energía transmitida por la cámara,
    pero no interrumpe la transmisión por perfiles y fijaciones. Cuando
    $TL_{\mathrm{abs}}$ supera ampliamente a $TL_{\mathrm{línea}}$, el camino
    estructural domina y el resultado final se aproxima a
    $TL_{\mathrm{línea}}$. Por eso la mejora del TL total puede ser menor que
    $\Delta TL_{\mathrm{abs}}$.
    """)

    st.markdown("#### 6.6 · Resultado completo por frecuencia")
    st.markdown(r"""
    En cada banda se deben informar los cinco valores siguientes:

    | Resultado | Significado |
    |---|---|
    | $TL_{\mathrm{base}}(f)$ | Camino aéreo del panel doble con cámara vacía |
    | $TL_{\mathrm{línea}}(f)$ | Camino mecánico asociado a la conexión lineal |
    | $TL_{\mathrm{total}}(f)$ | Resultado de cámara vacía + conexión lineal |
    | $TL_{\mathrm{abs}}(f)$ | Camino aéreo con material absorbente |
    | $TL_{\mathrm{total,abs}}(f)$ | Resultado final de absorbente + conexión lineal |

    **Secuencia correcta:** se calcula el TL de cada camino, se convierte a
    $\tau$, se suman los coeficientes de transmisión y se vuelve a decibeles.
    """)
    st.warning("""
    **Alcance del cálculo:** la descomposición permite comprender por separado la
    cámara, la conexión y el absorbente. Es un modelo pedagógico y no reemplaza
    un ensayo de laboratorio ni incorpora automáticamente fugas, cajas eléctricas,
    encuentros, transmisiones laterales o errores de montaje.
    """)

    st.markdown("### 7 · Laboratorio interactivo: construye el tabique")
    st.info(
        "Modifica las propiedades de las hojas y la cámara. El laboratorio calcula "
        "el comportamiento acústico del tabique y lo compara con una hoja equivalente "
        "de igual masa superficial total."
    )
    _lab2_image(
        "s5_geometria_camara_montantes",
        "Geometría utilizada por el modelo: d es la profundidad libre de la cámara, "
        "medida perpendicularmente entre las caras interiores de las hojas; b es la "
        "separación eje a eje entre dos montantes consecutivos.",
    )
    st.markdown("""
    **Cómo leer las dos dimensiones del render**

    - **d · Profundidad de la cámara:** distancia perpendicular entre las caras
      interiores de las dos hojas. Se ingresa en milímetros y se convierte a metros
      para calcular las frecuencias **f₀** y **fₗ**.

    - **b · Separación de montantes:** distancia horizontal **eje a eje** entre
      dos perfiles consecutivos. No corresponde al ancho libre del paño. Interviene
      en la corrección del camino de transmisión por conexión lineal, **ΔTLₘ′**.
    """)
    support_type=st.radio(
        "Tipo de conexión lineal que deseas representar",
        ["Perfilería metálica", "Pies derechos de madera"],
        horizontal=True,
        key="s5_real_support_type",
    )
    if support_type=="Perfilería metálica":
        st.info(
            "Perfilería metálica liviana · Sus alas y alma delgada son más flexibles "
            "que un pie derecho macizo. Esa resiliencia suele reducir el acoplamiento "
            "mecánico entre las dos hojas y entregar mayor aislamiento que una "
            "estructura de madera equivalente. Un perfil metálico más grueso y rígido "
            "puede perder parte de esa ventaja."
        )
    else:
        st.warning(
            "Pies derechos de madera · Su sección maciza presenta mayor rigidez y "
            "normalmente forma un puente mecánico más eficaz entre ambas hojas. Por "
            "ello, una solución equivalente suele aislar menos que con perfilería "
            "metálica liviana, especialmente cuando las placas están fijadas "
            "directamente a ambos lados del mismo pie derecho."
        )
    st.caption(
        "Alcance del cálculo: la ecuación simplificada disponible representa una "
        "conexión lineal genérica y todavía entrega el mismo valor para metal y "
        "madera. La diferencia real depende de la rigidez y geometría del montante, "
        "su espesor o sección, la separación, las fijaciones y las capas de placa. "
        "Por rigor técnico no se aplica una corrección arbitraria sin datos mecánicos "
        "o resultados de ensayo de la solución constructiva."
    )
    c1,c2,c3,c4=st.columns(4)
    m1=c1.number_input("Masa hoja 1 · m′₁ (kg/m²)",5.0,80.0,10.0,1.0,key="s5_real_m1")
    m2=c2.number_input("Masa hoja 2 · m′₂ (kg/m²)",5.0,80.0,10.0,1.0,key="s5_real_m2")
    depth=c3.number_input("Profundidad de cámara · d (mm)",30,300,70,10,key="s5_real_d")
    spacing=c4.select_slider(
        "Separación de montantes · b (m)",
        options=[0.30,0.40,0.45,0.60,0.80,1.00],
        value=0.60,
        key="s5_real_b",
    )
    # Las hojas se representan como placas homogéneas de yeso-cartón. A partir
    # de la masa superficial seleccionada se obtiene el espesor equivalente,
    # su rigidez de flexión y, finalmente, la frecuencia crítica. De esta forma
    # f_c es un resultado físico del modelo y no un dato libre del alumno.
    leaf_density=800.0
    leaf_young=2.5e9
    leaf_poisson=0.30
    leaf_h1=float(m1)/leaf_density
    leaf_h2=float(m2)/leaf_density
    rigidity1=leaf_young*leaf_h1**3/(12.0*(1.0-leaf_poisson**2))
    rigidity2=leaf_young*leaf_h2**3/(12.0*(1.0-leaf_poisson**2))
    sound_speed=343.0
    fc1_value=(
        sound_speed**2/(2.0*np.pi)
        *np.sqrt(float(m1)/rigidity1)
    )
    fc2_value=(
        sound_speed**2/(2.0*np.pi)
        *np.sqrt(float(m2)/rigidity2)
    )

    c5,c6,c7=st.columns(3)
    c5.metric("Frecuencia crítica calculada · hoja 1",f"{fc1_value:.0f} Hz")
    c6.metric("Frecuencia crítica calculada · hoja 2",f"{fc2_value:.0f} Hz")
    selected_f=c7.selectbox(
        "Banda que deseas inspeccionar (Hz)",
        LAB2_FREQS.tolist(),
        index=9,
        key="s5_real_f",
    )
    st.caption(
        "Las frecuencias críticas no son parámetros seleccionables. Se calculan "
        "automáticamente para hojas homogéneas de yeso-cartón a partir de m′, "
        "ρ = 800 kg/m³, E = 2,5 GPa y ν = 0,30."
    )

    c8,c9,c10=st.columns(3)
    eta1=c8.number_input(
        "Factor de pérdidas hoja 1 · η₁",
        min_value=0.005,max_value=0.200,value=0.030,step=0.005,
        format="%.3f",key="s5_real_eta1",
    )
    eta2=c9.number_input(
        "Factor de pérdidas hoja 2 · η₂",
        min_value=0.005,max_value=0.200,value=0.030,step=0.005,
        format="%.3f",key="s5_real_eta2",
    )
    absorbent_type=c10.selectbox(
        "Absorbente en la cámara",
        ["Sin absorbente","Lana mineral 40 kg/m³","Lana mineral 60 kg/m³","Lana mineral 80 kg/m³"],
        index=2,key="s5_real_absorbent",
    )

    def _angular_transmission_integral(surface_mass,rigidity,loss_factor,frequencies):
        rho_air=1.18
        sound_speed=343.0
        theta=np.linspace(0.0,(4.0/9.0)*np.pi,720)
        sin_theta=np.sin(theta)
        cos_theta=np.cos(theta)
        values=[]
        for frequency in np.asarray(frequencies,dtype=float):
            omega=2.0*np.pi*frequency
            mass_term=(omega*surface_mass*cos_theta)/(2.0*rho_air*sound_speed)
            bending_term=((omega**2)*rigidity*(sin_theta**4))/(surface_mass*sound_speed**4)
            denominator=(1.0+loss_factor*mass_term*bending_term)**2+(mass_term*(1.0-bending_term))**2
            angular_integrand=(1.0/denominator)*cos_theta*sin_theta
            angular_integral=float(np.trapezoid(angular_integrand,theta))
            transmission=max(angular_integral*2.0904,1e-12)
            values.append(10.0*np.log10(1.0/transmission))
        return np.asarray(values,dtype=float)

    rho_air=1.18
    cavity_depth=max(float(depth)*1e-3,1e-4)
    tl_leaf1=_angular_transmission_integral(float(m1),rigidity1,float(eta1),LAB2_FREQS)
    tl_leaf2=_angular_transmission_integral(float(m2),rigidity2,float(eta2),LAB2_FREQS)
    equivalent=_angular_transmission_integral(
        float(m1+m2),rigidity1+rigidity2,float(eta1+eta2),LAB2_FREQS,
    )
    f0=(
        (1.0/(2.0*np.pi))*np.sqrt(rho_air*sound_speed**2)
        *np.sqrt((float(m1)+float(m2))/(float(m1)*float(m2)*cavity_depth))
    )
    fl=sound_speed/(2.0*np.pi*cavity_depth)
    absorbent_gain={
        "Sin absorbente":0.0,
        "Lana mineral 40 kg/m³":1.5,
        "Lana mineral 60 kg/m³":3.0,
        "Lana mineral 80 kg/m³":4.5,
    }[absorbent_type]
    absorbent_gain_curve=np.where(
        LAB2_FREQS < fl,
        absorbent_gain,
        absorbent_gain*0.35,
    )
    base=np.zeros_like(LAB2_FREQS,dtype=float)
    for band_index,frequency in enumerate(LAB2_FREQS):
        if frequency<f0:
            base[band_index]=equivalent[band_index]
        elif frequency<fl:
            base[band_index]=(
                tl_leaf1[band_index]+tl_leaf2[band_index]
                +20.0*np.log10(max(float(frequency)*cavity_depth,1e-12))-29.0
            )
        else:
            base[band_index]=(
                tl_leaf1[band_index]+tl_leaf2[band_index]+6.0
            )

    fc_high=max(fc1_value,fc2_value)
    line_correction=(
        10.0*np.log10(max(float(spacing)*fc_high,1e-12))
        +20.0*np.log10(float(m1)/(float(m1)+float(m2)))
        -18.0
    )
    line_path=equivalent+line_correction
    air_abs=base+absorbent_gain_curve
    tau_base=np.power(10.0,-base/10.0)
    tau_line=np.power(10.0,-line_path/10.0)
    tau_air_abs=np.power(10.0,-air_abs/10.0)
    total_empty=-10.0*np.log10(np.maximum(tau_base+tau_line,1e-12))
    total_abs=-10.0*np.log10(np.maximum(tau_air_abs+tau_line,1e-12))
    total_abs_improvement=total_abs-total_empty
    idx=int(np.where(LAB2_FREQS==selected_f)[0][0])
    has_absorbent=absorbent_type!="Sin absorbente"
    absorbent_card_title=(
        "2 · Cámara absorbente · sin conexión"
        if has_absorbent else
        "2 · Cámara vacía · sin conexión (sin absorbente seleccionado)"
    )
    real_card_title=(
        "🟢 4 · TL REAL · absorbente + conexión"
        if has_absorbent else
        "🟢 4 · TL REAL · cámara vacía + conexión"
    )

    st.markdown("#### Comparación de las cuatro configuraciones")
    st.caption(
        f"Resultados en la banda de {selected_f} Hz · "
        f"f₀ = {f0:.0f} Hz · fₗ = {fl:.0f} Hz"
    )
    a,b,c,d=st.columns(4)
    a.metric(
        f"1 · Cámara vacía · sin conexión · {selected_f} Hz",
        f"{base[idx]:.1f} dB",
        help="TL del camino aéreo ideal: dos hojas separadas por una cámara vacía, sin montantes que unan ambas caras.",
    )
    b.metric(
        f"{absorbent_card_title} · {selected_f} Hz",
        f"{air_abs[idx]:.1f} dB",
        delta=f"{absorbent_gain_curve[idx]:+.1f} dB por absorbente",
        help="TL del camino aéreo después de incorporar el aporte por banda del material absorbente, todavía sin conexión lineal.",
    )
    c.metric(
        f"3 · Cámara vacía · con conexión · {selected_f} Hz",
        f"{total_empty[idx]:.1f} dB",
        delta=f"{total_empty[idx]-base[idx]:+.1f} dB por conexión",
        delta_color="normal",
        help="Resultado de combinar energéticamente el camino aéreo de la cámara vacía con el camino mecánico de la conexión lineal.",
    )
    d.metric(
        f"{real_card_title} · {selected_f} Hz",
        f"{total_abs[idx]:.1f} dB",
        delta=f"{total_abs_improvement[idx]:+.1f} dB de mejora real",
        help="Resultado constructivo final: camino aéreo con absorbente combinado energéticamente con la conexión lineal.",
    )

    st.info(
        f"**Lectura comparativa a {selected_f} Hz:** sin conexión, la cámara vacía "
        f"entrega {base[idx]:.1f} dB y la cámara con {absorbent_type.lower()} "
        f"entrega {air_abs[idx]:.1f} dB. Al incorporar la conexión lineal, la "
        f"cámara vacía queda en {total_empty[idx]:.1f} dB. La configuración "
        f"completa —absorbente más conexión— entrega un **TL real de "
        f"{total_abs[idx]:.1f} dB**, equivalente a una mejora real de "
        f"{total_abs_improvement[idx]:+.1f} dB respecto de la misma conexión "
        f"con cámara vacía."
    )

    with st.expander("Ver resultados numéricos en todas las bandas", expanded=True):
        results_by_band=pd.DataFrame({
            "Frecuencia (Hz)":LAB2_FREQS.astype(int),
            "1 · Cámara vacía, sin conexión (dB)":np.round(base,1),
            "2 · Cámara absorbente, sin conexión (dB)":np.round(air_abs,1),
            "3 · Cámara vacía, con conexión (dB)":np.round(total_empty,1),
            "4 · TL real: absorbente + conexión (dB)":np.round(total_abs,1),
            "TL del camino lineal usado en el cálculo (dB)":np.round(line_path,1),
            "Aporte del absorbente al camino aéreo (dB)":np.round(absorbent_gain_curve,1),
            "Mejora real entre configuraciones 3 y 4 (dB)":np.round(total_abs_improvement,1),
        })
        st.dataframe(
            results_by_band,
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Las configuraciones 3 y 4 incluyen la conexión. Se obtienen sumando "
            "los coeficientes de transmisión del camino aéreo y del camino lineal; "
            "no mediante suma o resta directa de decibeles."
        )

    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=base,mode="lines+markers",
        name="1 · Cámara vacía · sin conexión",
        line=dict(color="#08a9d8",width=4),marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=air_abs,mode="lines+markers",
        name=absorbent_card_title,
        line=dict(color="#65a30d",width=4,dash="dot"),marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=total_empty,mode="lines+markers",
        name="3 · Cámara vacía · con conexión",
        line=dict(color="#9b59b6",width=4),marker=dict(size=6,symbol="triangle-up"),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=total_abs,mode="lines+markers",
        name=real_card_title.replace("🟢 ",""),
        line=dict(color="#1b9e77",width=5),marker=dict(size=7,symbol="square"),
    ))
    fig.add_vline(x=selected_f,line_color="#1d3557",line_dash="dot",line_width=2)
    fig.add_annotation(
        x=selected_f,y=max(
            float(base[idx]),float(air_abs[idx]),
            float(total_empty[idx]),float(total_abs[idx]),
        ),
        text=f"{selected_f} Hz",showarrow=True,arrowhead=2,ay=-42,
        font=dict(color="#17324d"),
    )
    fig.update_layout(
        title="Comparación de las cuatro configuraciones del tabique",
        xaxis_title="Frecuencia central (Hz)",yaxis_title="Pérdida por transmisión TL (dB)",
        xaxis_type="log",hovermode="x unified",height=520,
        margin=dict(l=45,r=25,t=75,b=115),
        legend=dict(
            orientation="h",yanchor="top",y=-0.23,xanchor="center",x=.5,
            bgcolor="rgba(255,255,255,.92)",
        ),
    )
    fig.update_xaxes(
        tickvals=[63,125,250,500,1000,2000,4000],
        ticktext=["63","125","250","500","1k","2k","4k"],
        range=[math.log10(50),math.log10(5000)],autorange=False,
    )
    st.plotly_chart(fig,use_container_width=True,key="lab2_s5_real_wall_curve")

    st.markdown("### 8 · Interpretación automática del diseño")
    if spacing <= .40:
        spacing_reading="La modulación es cerrada: existen muchas líneas de conexión por metro de tabique."
    elif spacing <= .60:
        spacing_reading="La modulación es habitual: el efecto de los montantes sigue siendo parte central del sistema."
    else:
        spacing_reading="La modulación es más abierta: hay menos líneas de conexión, pero debe verificarse la estabilidad constructiva."
    symmetry=abs(m1-m2)/(m1+m2)
    if symmetry < .10:
        mass_reading="Las hojas son casi simétricas; sus respuestas críticas pueden concentrarse en zonas similares."
    else:
        mass_reading="Las hojas son asimétricas; esto puede separar parcialmente sus respuestas críticas."
    if st.session_state.get("role")=="Docente":
        with st.container(border=True):
            st.markdown("#### 🔐 Lectura docente · ¿En qué frecuencias actúa mejor el absorbente?")
            st.markdown(
                "Para la configuración seleccionada, las frecuencias que delimitan "
                "las regiones de análisis son:"
            )
            freq_col_1, freq_col_2 = st.columns(2)
            with freq_col_1:
                st.caption("Resonancia masa–aire–masa")
                st.latex(rf"f_0 \approx {f0:.0f}\ \mathrm{{Hz}}")
            with freq_col_2:
                st.caption("Frecuencia límite del modelo")
                st.latex(rf"f_l \approx {fl:.0f}\ \mathrm{{Hz}}")
            st.markdown(
                """
                Estos valores permiten interpretar el aporte del material poroso por regiones:

                1. **Bajo f₀: aporte generalmente limitado.** Las longitudes de onda
                   son grandes y el comportamiento está controlado principalmente por las
                   masas de las hojas y la rigidez del aire encerrado. La lana puede
                   introducir amortiguamiento, pero no reemplaza masa, mayor separación ni
                   desacoplamiento. En esta zona no debe esperarse una ganancia uniforme
                   importante de TL.

                2. **En torno a f₀: aporte especialmente valioso.** El material poroso
                   disipa energía por pérdidas viscosas y térmicas y reduce el factor de
                   calidad de la resonancia masa–aire–masa. Su principal beneficio es
                   hacer menos profundo y menos abrupto el valle de TL. Normalmente
                   amortigua la resonancia más de lo que desplaza su frecuencia central.

                3. **Entre f₀ y fₗ: región de mejor eficacia de banda ancha.**
                   Aquí disminuyen las reflexiones múltiples, las ondas estacionarias y el
                   acoplamiento acústico entre hojas. El efecto aumenta cuando el material
                   ocupa una fracción importante de la cámara sin quedar excesivamente
                   comprimido y posee una resistividad al flujo adecuada.

                4. **Sobre fₗ: el absorbente todavía controla el campo de la cámara,
                   pero la mejora adicional del TL total puede estabilizarse.** En esta
                   región pueden dominar la coincidencia de las placas, los montantes,
                   tornillos, encuentros y otros puentes estructurales. Si el **TL de la
                   conexión lineal** es menor que el TL del camino aéreo, agregar
                   más absorbente producirá poca mejora en el **TL real**.
                """
            )
            st.markdown(
                fr"""
                **Lectura de este diseño:** se seleccionó **{absorbent_type}** y una cámara
                de **{depth:.0f} mm**. {spacing_reading} {mass_reading} La frecuencia
                crítica dominante es **{fc_high:.0f} Hz** y la corrección del modelo
                lineal es **{line_correction:+.1f} dB**. El resultado final se obtiene
                combinando energéticamente el camino aéreo absorbido con el camino por
                {support_type.lower()}; el absorbente no se suma directamente al TL de
                los montantes.

                **Criterio profesional:** no debe elegirse una lana solamente por su
                densidad nominal. El comportamiento depende de la **resistividad al
                flujo**, espesor instalado, porcentaje de llenado, compresión, posición,
                profundidad de la cámara y frecuencia. Este laboratorio representa esas
                tendencias mediante una ganancia pedagógica por bandas; no constituye la
                predicción certificada de un producto ni reemplaza un ensayo.
                """
            )

    with st.expander("Ver procedimiento matemático paso a paso"):
        st.markdown("**1. Masa superficial total**")
        st.latex(
            rf"m'_1+m'_2={m1:.1f}+{m2:.1f}={m1+m2:.1f}\ \mathrm{{kg/m^2}}"
        )

        st.markdown("**2. Rigidez de cada hoja**")
        st.latex(r"B_i=m'_i\left(\frac{c^2}{2\pi f_{c,i}}\right)^2")
        st.latex(
            rf"B_1={rigidity1:.2f}\ \mathrm{{N\,m}},"
            rf"\qquad B_2={rigidity2:.2f}\ \mathrm{{N\,m}}"
        )

        st.markdown(
            "**3. Transmisión angular:** el modelo integra la transmisión de cada "
            "hoja para ángulos de incidencia entre 0° y 80°."
        )

        st.markdown("**4. Frecuencia de resonancia masa–aire–masa**")
        st.latex(rf"f_0={f0:.1f}\ \mathrm{{Hz}}")

        st.markdown("**5. Frecuencia límite de la cámara**")
        st.latex(rf"f_l={fl:.1f}\ \mathrm{{Hz}}")

        st.markdown("**6. Corrección del modelo de conexión lineal**")
        st.latex(
            rf"\Delta TL_{{m'}}="
            rf"10\log_{{10}}({float(spacing):.2f}\cdot {fc_high:.0f})+"
            rf"20\log_{{10}}\left(\frac{{{float(m1):.1f}}}"
            rf"{{{float(m1):.1f}+{float(m2):.1f}}}\right)-18"
            rf"={line_correction:.2f}\ \mathrm{{dB}}"
        )
        st.latex(
            rf"TL_\mathrm{{línea}}({selected_f})="
            rf"TL_{{m'_1+m'_2}}({selected_f})+\Delta TL_{{m'}}="
            rf"{equivalent[idx]:.1f}+({line_correction:.2f})="
            rf"{line_path[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**7. TL total con cámara vacía**")
        st.latex(
            rf"TL_\mathrm{{total}}({selected_f})=-10\log_{{10}}\left("
            rf"10^{{-{base[idx]:.1f}/10}}+10^{{-{line_path[idx]:.1f}/10}}\right)"
            rf"={total_empty[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**8. Camino aéreo con absorbente**")
        st.latex(
            rf"\Delta TL_\mathrm{{abs}}({selected_f})="
            rf"{absorbent_gain_curve[idx]:.1f}\ \mathrm{{dB}}"
        )
        st.latex(
            rf"TL_\mathrm{{abs}}({selected_f})="
            rf"{base[idx]:.1f}+{absorbent_gain_curve[idx]:.1f}="
            rf"{air_abs[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**9. TL total final con absorbente y conexión lineal**")
        st.latex(
            rf"TL_\mathrm{{total,abs}}({selected_f})=-10\log_{{10}}\left("
            rf"10^{{-{air_abs[idx]:.1f}/10}}+10^{{-{line_path[idx]:.1f}/10}}\right)"
            rf"={total_abs[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.caption(
            "Las curvas se calculan mediante tres regiones de comportamiento. "
            "El absorbente modifica el camino aéreo; la conexión lineal permanece como "
            "un camino mecánico paralelo. Los resultados totales se obtienen sumando "
            "coeficientes de transmisión y convirtiendo nuevamente a decibeles."
        )

    st.markdown("### 9 · Comprobación conceptual")
    check(
        "lab2_s5_q1",
        "¿Por qué un montante compartido puede reducir el beneficio de una cámara?",
        [
            "Porque crea un camino estructural entre ambas hojas",
            "Porque elimina la masa de las placas",
            "Porque convierte la lana mineral en una fuente sonora",
            "Porque abre necesariamente una fuga de aire",
        ],
        "Porque crea un camino estructural entre ambas hojas",
        "La vibración puede viajar por placas, tornillos y perfil continuo sin depender solo del campo aéreo de la cámara.",
    )
    check(
        "lab2_s5_q2",
        "¿Qué representa b en el modelo de conexión lineal?",
        [
            "La separación entre líneas de conexión o montantes",
            "El espesor de la lana mineral",
            "La profundidad total de ambas placas",
            "La velocidad del sonido",
        ],
        "La separación entre líneas de conexión o montantes",
        "b describe la modulación de las conexiones continuas y se expresa en metros.",
    )
    check(
        "lab2_s5_q3",
        "¿Agregar absorbente dentro de la cámara elimina por sí solo el puente rígido?",
        ["No","Sí","Solo sobre 500 Hz","Solo si ambas hojas pesan lo mismo"],
        "No",
        "El absorbente amortigua el campo de la cámara, pero no separa mecánicamente las fijaciones y perfiles.",
    )
    check(
        "lab2_s5_q4",
        "¿La curva calculada garantiza el desempeño final del tabique en obra?",
        [
            "No, deben considerarse ensayo, montaje, fugas, encuentros y flancos",
            "Sí, porque incorpora todos los detalles constructivos",
            "Sí, pero únicamente si b=0,60 m",
            "No, porque el aislamiento nunca puede calcularse",
        ],
        "No, deben considerarse ensayo, montaje, fugas, encuentros y flancos",
        "El modelo sirve para comprender tendencias; el desempeño real depende de más caminos de transmisión y de la ejecución.",
    )
    check(
        "lab2_s5_q5",
        "¿Qué diferencia geométrica principal existe entre una conexión lineal y una puntual?",
        [
            "La lineal se prolonga continuamente; la puntual actúa en posiciones discretas",
            "La lineal siempre es metálica y la puntual siempre es de madera",
            "La puntual no transmite vibración",
            "No existe ninguna diferencia",
        ],
        "La lineal se prolonga continuamente; la puntual actúa en posiciones discretas",
        "La clasificación depende de cómo se distribuye el acoplamiento: a lo largo de una línea o en puntos separados.",
    )

def _stage6_impl():
    """Etapa 6 completa: pérdida de transmisión en ventanas dobles (Quirt, 1983)."""
    _lab2_heading(
        6,
        "Pérdida de transmisión sonora en ventanas dobles",
        "Comprender cómo las masas de los vidrios, la cámara y sus dimensiones "
        "modifican el TL por bandas.",
    )

    hero = ROOT / "assets/lab2/etapa6_ventana_doble_quirt_profesional.png"
    if hero.exists():
        st.image(str(hero), use_container_width=True)
    st.caption(
        "Dos vidrios separados por una cámara de aire: la primera hoja vibra, "
        "excita el campo de la cavidad y este pone en movimiento la segunda hoja."
    )

    st.markdown("### 1 · ¿Qué es una ventana doble desde el punto de vista acústico?")
    st.markdown("""
    Una ventana doble es un sistema **masa–aire–masa**. Cada vidrio funciona como una
    masa y el aire encerrado entre ambos actúa como un resorte. El sonido no atraviesa
    simplemente dos obstáculos independientes: las hojas quedan acopladas por la cámara.

    Por eso su respuesta presenta dos regiones:

    - **Bajo la frecuencia f₁:** las dos hojas se mueven fuertemente acopladas y el
      conjunto se aproxima a una placa cuya masa superficial es la suma de ambos vidrios.
    - **Sobre f₁:** las hojas responden de manera más independiente y la cavidad puede
      tratarse aproximadamente como un espacio reverberante. Intervienen el TL de cada
      vidrio, la separación, el perímetro y las dimensiones de la ventana.

    **En palabras simples:** antes de f₁, los dos vidrios tienden a “viajar juntos”.
    Después de f₁, la cámara ayuda a separarlos acústicamente y el aislamiento puede
    crecer con mayor rapidez.
    """)

    st.markdown("### 2 · Frecuencia que separa ambos comportamientos")
    formula_card(
        "Frecuencia f₁ de la ventana doble · Quirt (1983)",
        r"f_1=\frac{1}{2\pi}\sqrt{\frac{(\rho_{s1}+\rho_{s2})\rho_0c^2}"
        r"{d\,\rho_{s1}\rho_{s2}}}",
        "<b>ρs₁, ρs₂</b>: masas superficiales de los vidrios (kg/m²)<br>"
        "<b>ρ₀</b>: densidad del aire (kg/m³)<br>"
        "<b>c</b>: velocidad del sonido (m/s)<br>"
        "<b>d</b>: separación libre entre vidrios (m)<br>"
        "<b>f₁</b>: frecuencia límite del modelo (Hz)",
        "Para saber en qué banda deja de utilizarse la placa equivalente y comienza "
        "el régimen superior de la cavidad.",
    )
    st.info(
        "Aumentar la profundidad d reduce f₁. Esto desplaza la zona desfavorable hacia "
        "frecuencias más bajas. Aumentar la masa de los vidrios también tiende a reducirla."
    )

    st.markdown("### 3 · Pérdida de transmisión bajo f₁")
    st.latex(r"f<f_1")
    st.latex(r"TL(f)\approx TL_{\rho_{s1}+\rho_{s2}}(f)")
    st.markdown("""
    En esta región se estima el TL como el de una placa infinita cuya masa superficial
    equivale a la suma:
    """)
    st.latex(r"\rho_{s,\mathrm{eq}}=\rho_{s1}+\rho_{s2}")
    st.markdown(
        "**Lectura sencilla:** la cámara todavía no entrega toda la ventaja esperada; "
        "ambas hojas se comportan aproximadamente como una masa equivalente."
    )

    st.markdown("### 4 · Pérdida de transmisión sobre f₁")
    st.latex(r"f\geq f_1")
    formula_card(
        "Régimen superior de la ventana doble",
        r"TL=TL_{\rho_{s1}}+TL_{\rho_{s2}}+10\log_{10}(\alpha)"
        r"+10\log_{10}(d)+10\log_{10}\left(\frac{h+w}{hw}\right)+3",
        "<b>TLρs₁, TLρs₂</b>: TL individual de cada vidrio por banda<br>"
        "<b>α</b>: absorción a incidencia aleatoria del perímetro interior<br>"
        "<b>d</b>: profundidad de la cámara (m)<br>"
        "<b>h, w</b>: alto y ancho interiores de la cavidad (m)",
        "Para estimar el TL cuando la cavidad se considera un espacio reverberante.",
    )
    st.markdown("""
    La ecuación no significa que cualquier aumento de cámara entregue siempre la misma
    mejora. El resultado depende simultáneamente de las masas, la frecuencia, el tamaño
    de la cavidad y las pérdidas en el perímetro.

    **α no representa un absorbente que rellena la cámara.** Corresponde a la absorción
    efectiva del perímetro y de las superficies interiores. En una ventana estándar la
    cavidad permanece libre; por eso no debe aplicarse sin cambios el modelo de un tabique
    relleno con lana mineral.
    """)

    st.markdown("### 5 · Lo que el modelo ideal todavía no incluye")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        "**Marco y sellos**\n\nUna pequeña fuga puede dominar la transmisión y reducir "
        "fuertemente el aislamiento medido."
    )
    c2.markdown(
        "**Coincidencia del vidrio**\n\nCada hoja puede presentar un valle propio. "
        "Vidrios iguales tienden a superponer sus debilidades."
    )
    c3.markdown(
        "**Transmisiones laterales**\n\nEncuentros, cajones de persiana y la fachada "
        "pueden limitar el resultado instalado."
    )
    st.warning(
        "Una cámara pequeña con dos vidrios iguales puede ser excelente térmicamente, "
        "pero no necesariamente es la solución acústica óptima. La asimetría desplaza "
        "las coincidencias y una cámara mayor reduce el acoplamiento masa–aire–masa."
    )

    st.markdown("## Laboratorio interactivo · construye y analiza una ventana doble")
    st.caption(
        "Modifica una variable a la vez y observa f₁, la región activa y la curva de TL."
    )
    dimensions_render = ROOT / "assets/lab2/ventana_doble_parametros_d_h_w.png"
    if dimensions_render.exists():
        st.image(str(dimensions_render), use_container_width=True)
        st.caption(
            "Geometría utilizada en el laboratorio: d es la separación entre placas; "
            "h y w corresponden a la altura y al ancho de la cavidad."
        )
    a, b, c = st.columns(3)
    g1 = a.slider("Espesor vidrio 1 (mm)", 3.0, 12.0, 4.0, 0.5, key="l2s6_g1")
    g2 = b.slider("Espesor vidrio 2 (mm)", 3.0, 12.0, 6.0, 0.5, key="l2s6_g2")
    gap_mm = c.slider("Separación entre placas d (mm)", 6, 200, 40, 2, key="l2s6_gap")
    d1, d2, d3 = st.columns(3)
    height = d1.slider("Altura de la cavidad h (m)", 0.5, 3.0, 1.5, 0.1, key="l2s6_h")
    width = d2.slider("Ancho de la cavidad w (m)", 0.5, 3.0, 1.2, 0.1, key="l2s6_w")
    alpha = d3.slider("Absorción perimetral α", 0.02, 0.30, 0.10, 0.01, key="l2s6_alpha")

    p1, p2 = st.columns(2)
    eta1 = p1.slider(
        "Factor de pérdidas del vidrio 1 η₁",
        0.001, 0.100, 0.010, 0.001,
        format="%.3f", key="l2s6_eta1",
    )
    eta2 = p2.slider(
        "Factor de pérdidas del vidrio 2 η₂",
        0.001, 0.100, 0.010, 0.001,
        format="%.3f", key="l2s6_eta2",
    )

    gap = gap_mm / 1000.0
    window_tl, tl1, tl2, equivalent, f1, masses, fcs, geometry = (
        _double_window_model(
            g1, g2, gap, height, width, alpha, eta1, eta2, FREQS
        )
    )
    m1, m2 = masses

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Masa vidrio 1", f"{m1:.1f} kg/m²")
    e2.metric("Masa vidrio 2", f"{m2:.1f} kg/m²")
    e3.metric("Frecuencias críticas", f"{fcs[0]:.0f} / {fcs[1]:.0f} Hz")
    e4.metric("Frecuencia f₁", f"{f1:.0f} Hz")

    selected_f = st.select_slider(
        "Frecuencia que deseas inspeccionar (Hz)",
        options=[int(v) for v in FREQS],
        value=500,
        key="l2s6_selected_f",
    )
    idx = int(np.argmin(np.abs(FREQS - selected_f)))
    regime = "Bajo f₁ · placa equivalente" if selected_f < f1 else "Sobre f₁ · cavidad reverberante"
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Régimen activo", regime)
    r2.metric("TL vidrio 1 · modelo físico", f"{tl1[idx]:.1f} dB")
    r3.metric("TL vidrio 2 · modelo físico", f"{tl2[idx]:.1f} dB")
    r4.metric("TL ventana doble", f"{window_tl[idx]:.1f} dB")
    st.caption(
        f"Configuración {g1:g}–{gap_mm}–{g2:g} mm. "
        f"A {selected_f} Hz se aplica: {regime}."
    )

    _plot_curves(
        [
            ("Ventana doble · modelo completo", window_tl, "solid"),
            ("Masa equivalente bajo f₁", equivalent, "dash"),
            ("Vidrio 1 · modelo físico", tl1, "dot"),
            ("Vidrio 2 · modelo físico", tl2, "dot"),
        ],
        "Pérdida de transmisión sonora por bandas",
        [(f1, "f₁"), (fcs[0], "fᶜ₁"), (fcs[1], "fᶜ₂")],
    )

    table = pd.DataFrame({
        "Frecuencia (Hz)": FREQS.astype(int),
        "Régimen": np.where(FREQS < f1, "Bajo f₁", "Sobre f₁"),
        "TL vidrio 1 (dB)": np.round(tl1, 1),
        "TL vidrio 2 (dB)": np.round(tl2, 1),
        "TL placa equivalente (dB)": np.round(equivalent, 1),
        "TL ventana doble (dB)": np.round(window_tl, 1),
    })
    st.dataframe(table, use_container_width=True, hide_index=True)

    with st.expander("Ver cálculo matemático en la frecuencia seleccionada"):
        st.markdown("**1 · Masas superficiales de los vidrios**")
        st.latex(
            rf"\rho_{{s1}}=2500\cdot {g1/1000:.4f}={m1:.2f}\ \mathrm{{kg/m^2}}"
        )
        st.latex(
            rf"\rho_{{s2}}=2500\cdot {g2/1000:.4f}={m2:.2f}\ \mathrm{{kg/m^2}}"
        )
        st.markdown("**2 · Frecuencia de cambio de régimen**")
        st.latex(rf"f_1={f1:.1f}\ \mathrm{{Hz}}")
        st.markdown("**3 · Cada vidrio se calcula primero con el modelo físico de placa simple**")
        st.latex(r"TL_{\mathrm{vidrio}}(f)=-10\log_{10}\overline{\tau}(f)")
        st.latex(
            rf"TL_{{1,\mathrm{{vidrio}}}}({selected_f})"
            rf"={tl1[idx]:.2f}\ \mathrm{{dB}},\quad "
            rf"f_{{c1}}={fcs[0]:.0f}\ \mathrm{{Hz}}"
        )
        st.latex(
            rf"TL_{{2,\mathrm{{vidrio}}}}({selected_f})"
            rf"={tl2[idx]:.2f}\ \mathrm{{dB}},\quad "
            rf"f_{{c2}}={fcs[1]:.0f}\ \mathrm{{Hz}}"
        )
        if selected_f < f1:
            st.markdown("**4 · La frecuencia seleccionada está bajo f₁**")
            st.latex(
                rf"TL({selected_f})=TL_{{\rho_{{s1}}+\rho_{{s2}}}}"
                rf"={equivalent[idx]:.1f}\ \mathrm{{dB}}"
            )
        else:
            st.markdown("**4 · La frecuencia seleccionada está sobre f₁**")
            st.latex(
                rf"TL({selected_f})={tl1[idx]:.1f}+{tl2[idx]:.1f}"
                rf"+10\log_{{10}}({alpha:.2f})+10\log_{{10}}({gap:.3f})"
                rf"+10\log_{{10}}\left(\frac{{{height:.1f}+{width:.1f}}}"
                rf"{{{height:.1f}\cdot {width:.1f}}}\right)+3"
            )
            st.latex(rf"TL({selected_f})={window_tl[idx]:.1f}\ \mathrm{{dB}}")
        st.caption(
            "Los TL de los vidrios incluyen masa, rigidez, amortiguamiento, incidencia "
            "angular y coincidencia mediante el modelo físico de placa simple. Quirt representa después "
            "la cavidad ideal; no incorpora fugas, marco, herrajes ni transmisión lateral."
        )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · interpretación y límites"):
            st.markdown("""
            - **Alrededor de f₁** debe enfatizarse el acoplamiento masa–aire–masa y la
              transición entre las dos expresiones; no interpretar un salto del modelo
              como una discontinuidad exacta de una ventana real.
            - **En bajas frecuencias** domina el acoplamiento y el ruido de tránsito
              pesado puede revelar la principal debilidad del sistema.
            - **En medias y altas frecuencias** crece el beneficio de separar las hojas,
              pero pueden aparecer coincidencias de los vidrios.
            - **Vidrios asimétricos** no garantizan por sí solos más TL en cada banda,
              pero evitan que ambas coincidencias se superpongan exactamente.
            - **El resultado instalado** estará limitado por marco, sellos, encuentros,
              cajones, ventilaciones y transmisiones laterales. La curva ideal no debe
              presentarse como un valor certificado de obra.
            """)

    st.markdown("### Cinco preguntas de comprensión")
    check(
        "lab2_s6_q1",
        "¿Qué representa físicamente el aire encerrado entre los dos vidrios?",
        ["Un resorte acústico que acopla ambas masas", "Una tercera placa sólida",
         "Una fuga permanente", "Un absorbente poroso"],
        "Un resorte acústico que acopla ambas masas",
        "El sistema se interpreta como masa–aire–masa: vidrio, resorte de aire y vidrio.",
    )
    check(
        "lab2_s6_q2",
        "¿Cómo se estima el TL bajo f₁ en este modelo?",
        ["Como una placa equivalente con la suma de masas", "Sumando directamente 20 dB",
         "Usando solo el vidrio más delgado", "Ignorando ambos vidrios"],
        "Como una placa equivalente con la suma de masas",
        "Bajo f₁ ambas hojas se consideran fuertemente acopladas.",
    )
    check(
        "lab2_s6_q3",
        "¿Qué suele ocurrir con f₁ al aumentar la profundidad d de la cámara?",
        ["Disminuye", "Aumenta", "Permanece siempre fija", "Se transforma en Rw"],
        "Disminuye",
        "En la ecuación, d está en el denominador dentro de la raíz.",
    )
    check(
        "lab2_s6_q4",
        "¿Por qué dos vidrios distintos pueden ser preferibles acústicamente?",
        ["Porque separan sus debilidades de coincidencia", "Porque eliminan el marco",
         "Porque llenan la cámara con absorbente", "Porque hacen innecesarios los sellos"],
        "Porque separan sus debilidades de coincidencia",
        "La asimetría ayuda a que los valles propios de ambas hojas no coincidan exactamente.",
    )
    check(
        "lab2_s6_q5",
        "¿La curva ideal calculada garantiza el mismo TL en la ventana instalada?",
        ["No; marco, sellos, fugas y flancos pueden dominar", "Sí, siempre",
         "Sí, si ambos vidrios son iguales", "Solo depende del color del marco"],
        "No; marco, sellos, fugas y flancos pueden dominar",
        "El desempeño real debe verificarse mediante datos de ensayo y una ejecución estanca.",
    )

def _stage7_impl():
    _lab2_heading(
        7,
        "Bandas de frecuencia: octavas y tercios de octava",
        "Transformar un espectro continuo en bandas normalizadas y elegir la resolución adecuada para interpretar el aislamiento acústico.",
    )

    st.markdown("""
    ### 1 · De una frecuencia continua a grupos comparables

    El sonido puede contener energía en una cantidad prácticamente continua de
    frecuencias. Mostrar cada frecuencia por separado entrega mucho detalle, pero
    dificulta comparar mediciones, materiales y soluciones constructivas.

    Por eso la acústica agrupa la energía en **bandas de frecuencia**. Cada banda
    reúne todas las frecuencias comprendidas entre un límite inferior y un límite
    superior, y se identifica mediante una **frecuencia central**.
    """)
    _lab2_image(
        "stage7_espectro_a_bandas",
        "El analizador agrupa un espectro continuo en intervalos de frecuencia que pueden compararse de manera ordenada.",
    )

    st.markdown(
        """
        <div class="route-grid">
          <div class="route-card"><span class="step">f</span><div><b>Frecuencia</b>
          <p>Indica cuántas oscilaciones ocurren cada segundo. Se expresa en hertz.</p></div></div>
          <div class="route-card"><span class="step">B</span><div><b>Banda</b>
          <p>Intervalo que reúne varias frecuencias para analizarlas como un conjunto.</p></div></div>
          <div class="route-card"><span class="step">fᶜ</span><div><b>Frecuencia central</b>
          <p>Nombre de la banda; no significa que solo se mida esa frecuencia.</p></div></div>
          <div class="route-card"><span class="step">R</span><div><b>Resolución</b>
          <p>Cuanto más estrecha es la banda, mayor detalle conserva el análisis.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "**En palabras simples:** una banda funciona como una caja. Dentro de ella se "
        "guarda la energía de un intervalo completo, y la frecuencia central es la "
        "etiqueta que usamos para reconocer esa caja."
    )

    st.markdown("### 2 · La escala no se divide en anchos iguales")
    st.write(
        "En una escala lineal se avanza sumando una cantidad fija, por ejemplo "
        "100, 200, 300 y 400 Hz. En las bandas de octava y de tercio se avanza "
        "multiplicando por una razón constante. Por eso su eje natural es logarítmico."
    )
    formula_card(
        "Relación entre frecuencias centrales consecutivas",
        r"f_{c,k+1}=f_{c,k}\,2^{1/b}",
        "<b>f<sub>c,k</sub></b>: frecuencia central de una banda (Hz)<br>"
        "<b>f<sub>c,k+1</sub></b>: frecuencia central siguiente (Hz)<br>"
        "<b>b</b>: número de bandas por octava; b=1 para octavas y b=3 para tercios",
        "Permite construir una sucesión proporcional. En una octava la frecuencia se "
        "duplica; en un tercio se multiplica aproximadamente por 1,26.",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Una octava", "× 2")
        st.caption("125 → 250 → 500 → 1.000 Hz")
    with c2:
        st.metric("Un tercio de octava", "× 1,26")
        st.caption("100 → 125 → 160 → 200 Hz")
    with c3:
        st.metric("Tres tercios", "× 2")
        st.caption("100 → 125 → 160 → 200 Hz")

    st.markdown("### 3 · Frecuencia central y límites de cada banda")
    formula_card(
        "Límites exactos de una banda fraccionaria",
        r"\begin{aligned}"
        r"f_i&=f_c\,2^{-1/(2b)}\\[0.35em]"
        r"f_s&=f_c\,2^{1/(2b)}\\[0.35em]"
        r"f_c&=\sqrt{f_i f_s}"
        r"\end{aligned}",
        "<b>fᵢ</b>: límite inferior de la banda (Hz)<br>"
        "<b>fₛ</b>: límite superior de la banda (Hz)<br>"
        "<b>f<sub>c</sub></b>: frecuencia central exacta (Hz)<br>"
        "<b>b</b>: 1 para octava y 3 para tercio de octava",
        "Sirve para saber qué frecuencias pertenecen realmente a una banda. La "
        "frecuencia central es la media geométrica de sus límites, no la media aritmética.",
    )

    calc_type = st.radio(
        "Calcula los límites de una banda",
        ["Octava", "Tercio de octava"],
        horizontal=True,
        key="lab2_s7_band_calc_type",
    )
    available_centers = (
        [63, 125, 250, 500, 1000, 2000, 4000]
        if calc_type == "Octava"
        else [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630,
              800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
    )
    nominal_fc = st.select_slider(
        "Frecuencia central nominal",
        available_centers,
        value=1000,
        format_func=lambda x: f"{x:,} Hz".replace(",", "."),
        key="lab2_s7_nominal_center",
    )
    bands_per_octave = 1 if calc_type == "Octava" else 3
    lower_limit = nominal_fc * 2 ** (-1 / (2 * bands_per_octave))
    upper_limit = nominal_fc * 2 ** (1 / (2 * bands_per_octave))
    m1, m2, m3 = st.columns(3)
    m1.metric("Límite inferior fᵢ", f"{lower_limit:.1f} Hz")
    m2.metric("Centro nominal fᶜ", f"{nominal_fc} Hz")
    m3.metric("Límite superior fₛ", f"{upper_limit:.1f} Hz")
    st.caption(
        "Los instrumentos muestran centros nominales redondeados —por ejemplo 125 o "
        "160 Hz— para facilitar la lectura. Los filtros se definen mediante relaciones "
        "exactas alrededor de su frecuencia central."
    )

    st.markdown("### 4 · Octava y tercio de octava")
    _lab2_image(
        "stage7_octava_vs_tercio",
        "Arriba: pocas bandas anchas. Abajo: tres subdivisiones por cada octava, capaces de revelar más detalle espectral.",
    )
    comparison = pd.DataFrame([
        ["Octava", "1", "2", "Vista general del espectro", "Diagnóstico rápido y comunicación global"],
        ["Tercio de octava", "3", "2^(1/3) ≈ 1,26", "Mayor detalle", "Aislamiento, normativa y detección de valles"],
    ], columns=["Análisis", "Bandas por octava", "Razón entre centros",
                "Qué muestra", "Uso típico"])
    st.dataframe(comparison, hide_index=True, use_container_width=True)
    st.info(
        "Una banda de tercio no contiene un tercio de la energía de una octava. "
        "Significa que el intervalo de una octava fue dividido logarítmicamente en "
        "tres bandas consecutivas."
    )

    st.markdown("### 5 · ¿Cómo se obtiene el nivel de una banda?")
    formula_card(
        "Suma energética dentro del intervalo",
        r"L_{\mathrm{banda}}=10\log_{10}\left(\sum_{j\in\mathrm{banda}}10^{L_j/10}\right)",
        "<b>L<sub>banda</sub></b>: nivel total de la banda (dB)<br>"
        "<b>Lⱼ</b>: nivel de cada componente o subintervalo contenido en la banda (dB)",
        "Los decibeles no se promedian aritméticamente. Primero se convierten a energía, "
        "se suman y después se vuelve a decibeles.",
    )
    st.warning(
        "**Error frecuente:** sumar o promediar directamente los valores en dB. "
        "Una banda representa la suma energética de todo lo que contiene."
    )

    st.markdown("### 6 · Laboratorio interactivo · del espectro a las bandas")
    st.write(
        "Construye una fuente con contenido amplio y agrega un tono dominante. Luego "
        "compara cuánto detalle conserva cada representación."
    )
    a, b, c = st.columns(3)
    with a:
        tone_frequency = st.slider(
            "Frecuencia del tono",
            80, 4000, 630, 10,
            key="lab2_s7_tone_frequency",
        )
    with b:
        tone_level = st.slider(
            "Intensidad del tono",
            0, 25, 16, 1,
            key="lab2_s7_tone_level",
        )
    with c:
        view_mode = st.radio(
            "Representación",
            ["Espectro fino", "Octavas", "Tercios", "Comparar"],
            key="lab2_s7_view_mode",
        )

    fine_f = np.geomspace(40, 8000, 720)
    base_level = (
        56
        - 5.5 * np.log2(fine_f / 250)
        + 3.2 * np.sin(np.log(fine_f) * 4.1)
        + 1.4 * np.cos(np.log(fine_f) * 9.3)
    )
    peak_width = 0.028
    tone_shape = tone_level * np.exp(
        -0.5 * (np.log2(fine_f / tone_frequency) / peak_width) ** 2
    )
    fine_levels = base_level + tone_shape

    octave_centers = np.array([63, 125, 250, 500, 1000, 2000, 4000], dtype=float)
    third_centers = np.array(
        [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
         1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000], dtype=float
    )

    def aggregate_bands(centers, subdivisions):
        results = []
        for center in centers:
            lo = center * 2 ** (-1 / (2 * subdivisions))
            hi = center * 2 ** (1 / (2 * subdivisions))
            mask = (fine_f >= lo) & (fine_f < hi)
            if not np.any(mask):
                results.append(np.nan)
                continue
            # Each logarithmic sample represents an equal spectral subinterval.
            results.append(10 * np.log10(np.sum(10 ** (fine_levels[mask] / 10))))
        return np.array(results)

    octave_levels = aggregate_bands(octave_centers, 1)
    third_levels = aggregate_bands(third_centers, 3)
    fig = go.Figure()
    if view_mode in ("Espectro fino", "Comparar"):
        fig.add_trace(go.Scatter(
            x=fine_f, y=fine_levels, name="Espectro fino",
            mode="lines", line=dict(color="#f39c3d", width=2),
        ))
    if view_mode in ("Octavas", "Comparar"):
        fig.add_trace(go.Scatter(
            x=octave_centers, y=octave_levels, name="Bandas de octava",
            mode="lines+markers", line=dict(color="#26a7df", width=4),
            marker=dict(size=9),
        ))
    if view_mode in ("Tercios", "Comparar"):
        fig.add_trace(go.Scatter(
            x=third_centers, y=third_levels, name="Bandas de tercio",
            mode="lines+markers", line=dict(color="#25d6b2", width=3),
            marker=dict(size=7),
        ))
    fig.add_vline(
        x=tone_frequency, line_dash="dot", line_color="#ff8a38",
        annotation_text=f"Tono: {tone_frequency} Hz",
        annotation_position="top",
    )
    fig.update_layout(
        title="Una misma fuente, distintas resoluciones",
        xaxis_title="Frecuencia (Hz)", yaxis_title="Nivel relativo (dB)",
        xaxis_type="log", hovermode="x unified", height=470,
        margin=dict(l=35, r=20, t=65, b=40),
        legend=dict(orientation="h", y=1.13),
    )
    fig.update_xaxes(
        tickvals=[50, 63, 100, 125, 250, 500, 1000, 2000, 4000, 8000],
        ticktext=["50", "63", "100", "125", "250", "500", "1k", "2k", "4k", "8k"],
    )
    st.plotly_chart(fig, use_container_width=True)

    nearest_oct = int(octave_centers[np.argmin(np.abs(np.log(octave_centers / tone_frequency)))])
    nearest_third = int(third_centers[np.argmin(np.abs(np.log(third_centers / tone_frequency)))])
    x1, x2, x3 = st.columns(3)
    x1.metric("Tono configurado", f"{tone_frequency} Hz")
    x2.metric("Banda de octava más próxima", f"{nearest_oct} Hz")
    x3.metric("Banda de tercio más próxima", f"{nearest_third} Hz")
    st.success(
        "**Lectura del laboratorio:** la octava entrega una tendencia compacta; el "
        "tercio de octava localiza mejor la zona del tono o del valle. Ninguna crea "
        "energía nueva: solo cambia la resolución con que se agrupa la misma señal."
    )

    st.markdown("### 7 · Relación con el aislamiento acústico")
    st.write("""
    Las curvas de pérdida de transmisión se presentan por bandas porque un elemento
    no aísla igual en todo el espectro. Los tercios de octava permiten reconocer:

    - resonancias y valles estrechos;
    - la región controlada por masa;
    - la caída de coincidencia;
    - diferencias entre dos soluciones que una octava podría ocultar;
    - bandas críticas de una fuente real.
    """)
    st.markdown(
        '<div class="good"><b>Idea central:</b> una octava resume; un tercio diagnostica. '
        'Para evaluar aislamiento acústico y construir índices ponderados se necesita '
        'conservar suficiente detalle por frecuencia.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · precisión técnica y conducción"):
            st.markdown("""
            - Aclare que **frecuencia lineal** y **bandas** no son magnitudes opuestas:
              una escala lineal representa incrementos aditivos; las bandas fraccionarias
              se ordenan mediante razones constantes y se visualizan mejor en escala logarítmica.
            - La frecuencia central mostrada normalmente es **nominal**. Los filtros
              normalizados emplean centros y límites exactos; no conviene deducir límites
              usando el punto medio aritmético.
            - Tres bandas de tercio consecutivas cubren una octava porque sus razones
              se multiplican tres veces y producen una razón total igual a 2.
            - El nivel de octava puede reconstruirse desde sus tres tercios mediante
              suma energética, no mediante promedio de dB.
            - En aislamiento, mayor resolución permite observar resonancia y coincidencia,
              pero no mejora por sí misma la exactitud física del modelo o de la medición.
            """)
            st.latex(
                r"L_{\mathrm{oct}}=10\log_{10}\left("
                r"10^{L_1/10}+10^{L_2/10}+10^{L_3/10}\right)"
            )

    st.markdown("### 8 · Cinco preguntas de comprensión")
    check(
        "lab2_s7_q1",
        "¿Qué representa la frecuencia central de una banda?",
        [
            "La etiqueta de un intervalo comprendido entre dos límites",
            "La única frecuencia que mide el instrumento",
            "El promedio aritmético obligatorio de todos los tonos",
            "La intensidad máxima del sonido",
        ],
        "La etiqueta de un intervalo comprendido entre dos límites",
        "La banda contiene un intervalo completo; la frecuencia central la identifica.",
    )
    check(
        "lab2_s7_q2",
        "¿Qué ocurre con la frecuencia al avanzar una octava completa?",
        ["Se duplica", "Aumenta siempre 100 Hz", "Se triplica", "Disminuye 3 dB"],
        "Se duplica",
        "Entre centros separados por una octava existe una razón de 2.",
    )
    check(
        "lab2_s7_q3",
        "¿Cuántas bandas de tercio de octava cubren una octava?",
        ["Tres", "Dos", "Diez", "Depende del nivel en dB"],
        "Tres",
        "Cada paso multiplica la frecuencia por 2^(1/3); tres pasos producen una razón total de 2.",
    )
    check(
        "lab2_s7_q4",
        "¿Por qué el tercio de octava ayuda a diagnosticar una caída de aislamiento?",
        [
            "Porque conserva más detalle espectral que una octava",
            "Porque siempre entrega 3 dB más",
            "Porque elimina la frecuencia crítica",
            "Porque convierte el aislamiento en absorción",
        ],
        "Porque conserva más detalle espectral que una octava",
        "Sus bandas más estrechas permiten localizar mejor valles, tonos y cambios de pendiente.",
    )
    check(
        "lab2_s7_q5",
        "¿Cómo deben combinarse varios niveles contenidos dentro de una banda?",
        [
            "Mediante suma energética",
            "Promediando directamente los dB",
            "Eligiendo siempre el valor menor",
            "Sumando las frecuencias centrales",
        ],
        "Mediante suma energética",
        "Los dB son logarítmicos: se convierten a energía, se suman y se vuelve a dB.",
    )

def _stage8_impl():
    _lab2_heading(
        8,
        "Número único de aislamiento a ruido aéreo: Rw, C y Ctr",
        "Convertir una curva de reducción sonora por tercios de octava en un descriptor único, sin perder de vista el espectro de la fuente.",
    )

    st.markdown("""
    ### 1 · ¿Por qué se informa Rw y no solamente R o TL?

    Tanto **R** como **TL** describen la reducción de la transmisión sonora en una
    **frecuencia o banda determinada**. Por ejemplo, informar R = 48 dB a 500 Hz
    solo explica lo que ocurre en esa banda: el mismo elemento puede entregar un
    valor menor en graves, uno mayor en agudos y presentar un valle de coincidencia.

    Por eso, un único R o TL no representa el comportamiento global del elemento y
    tampoco permite comparar soluciones si no se indica exactamente la frecuencia.
    En aislamiento a ruido aéreo se informa **Rw** porque resume, mediante un
    procedimiento normalizado, la curva completa de 16 tercios de octava entre
    100 y 3.150 Hz.

    **Rw no reemplaza la curva R(f): la resume.** La curva se conserva para el
    diagnóstico técnico; Rw se usa para declarar, especificar y comparar el
    desempeño mediante un mismo criterio.
    """)
    why_a, why_b, why_c = st.columns(3)
    with why_a:
        st.markdown(
            '<div class="route-card"><span class="step">R o TL</span><div>'
            '<b>Resultado por banda</b><p>Indica cuánto se reduce el sonido en una '
            'frecuencia concreta.</p></div></div>', unsafe_allow_html=True,
        )
    with why_b:
        st.markdown(
            '<div class="route-card"><span class="step">R(f)</span><div>'
            '<b>Diagnóstico completo</b><p>Permite localizar graves débiles, '
            'resonancias y coincidencia.</p></div></div>', unsafe_allow_html=True,
        )
    with why_c:
        st.markdown(
            '<div class="route-card"><span class="step">Rw</span><div>'
            '<b>Comparación normalizada</b><p>Condensa las 16 bandas con una misma '
            'regla de ponderación.</p></div></div>', unsafe_allow_html=True,
        )
    st.warning(
        "**Lectura correcta:** Rw = 52 dB no significa R = 52 dB en todas las "
        "frecuencias. Significa que la curva completa obtuvo un índice ponderado "
        "de 52 dB mediante el procedimiento normalizado."
    )

    st.markdown("""
    ### 2 · Del resultado por bandas al número único

    La reducción sonora **R** de un elemento constructivo cambia con la frecuencia.
    Una pared puede aislar bien en bandas medias y presentar un valle en bajas
    frecuencias o alrededor de la coincidencia. Por eso el resultado físico completo
    sigue siendo la curva **R(f)**.

    Para comparar soluciones y expresar requisitos de forma compacta, el método
    pondera esa curva mediante una referencia normalizada y obtiene **Rw**. Luego,
    los términos **C** y **Ctr** adaptan el resultado a dos familias de espectros.
    """)
    _lab2_image(
        "stage8_airborne_rw",
        "La curva de referencia se ajusta sobre R(f) y el número único Rw se lee en 500 Hz sobre esa referencia desplazada.",
    )
    st.markdown(
        """
        <div class="route-grid">
          <div class="route-card"><span class="step">R(f)</span><div><b>Curva por bandas</b>
          <p>Muestra cuánto reduce el elemento en cada tercio de octava.</p></div></div>
          <div class="route-card"><span class="step">Rw</span><div><b>Valor ponderado</b>
          <p>Resume la curva mediante el ajuste de una referencia normalizada.</p></div></div>
          <div class="route-card"><span class="step">C</span><div><b>Adaptación espectral 1</b>
          <p>Ajusta Rw a fuentes con mayor importancia relativa en frecuencias medias y altas.</p></div></div>
          <div class="route-card"><span class="step">Ctr</span><div><b>Adaptación espectral 2</b>
          <p>Da más importancia al contenido grave típico del tránsito urbano.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.success(
        "**En palabras simples:** Rw es el titular; C y Ctr explican cómo cambia ese "
        "titular cuando la fuente tiene otro reparto de energía por frecuencia."
    )

    st.markdown("### 3 · ¿Cuándo corresponde usar Rw?")
    st.write("""
    **Rw describe el aislamiento a ruido aéreo de un elemento ensayado en
    laboratorio**, como un muro, tabique, puerta, ventana, piso o cubierta. La fuente
    sonora se ubica en un recinto emisor y se determina cuánto se reduce la energía
    que atraviesa el elemento hacia el recinto receptor.

    No corresponde usar Rw para describir absorción interior, tiempo de reverberación
    ni ruido de impactos. Tampoco debe confundirse con el desempeño aparente de toda
    una construcción terminada, donde pueden intervenir encuentros, fugas y
    transmisiones laterales.
    """)
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            '<div class="good"><b>✓ Sí corresponde</b><br>Transmisión aérea a través '
            'de un elemento separador ensayado.</div>',
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="warn"><b>✗ No es absorción</b><br>No indica cuánto sonido '
            'absorbe una superficie dentro del mismo recinto.</div>',
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            '<div class="warn"><b>✗ No es impacto</b><br>No caracteriza golpes, '
            'pisadas ni excitación directa de la estructura.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 4 · Curva de referencia y desviaciones desfavorables")
    st.write("""
    La **curva de referencia** es una plantilla normalizada con una forma fija. No
    es la curva medida del tabique ni una exigencia independiente. Se coloca sobre
    el mismo gráfico de R(f) y solo puede desplazarse verticalmente, sin deformarla.

    En cada una de las 16 bandas se comparan dos valores. Si la referencia queda
    **por encima** de R(f), al elemento le falta aislamiento respecto de la plantilla
    y aparece una desviación desfavorable. Si R(f) queda por encima, el resultado es
    favorable, pero ese excedente vale cero: una banda muy buena no puede borrar un
    valle de otra banda.
    """)
    formula_card(
        "Desviación desfavorable en cada banda",
        r"d_i=\max\left(0,\;R_{\mathrm{ref},i}-R_i\right)",
        "<b>dᵢ</b>: desviación desfavorable en la banda i (dB)<br>"
        "<b>R<sub>ref,i</sub></b>: valor de la curva de referencia desplazada (dB)<br>"
        "<b>Rᵢ</b>: reducción sonora medida o calculada en esa banda (dB)",
        "Solo existe desviación cuando la curva real queda bajo la referencia. Si la "
        "curva real está por encima, esa diferencia favorable no compensa los valles.",
    )
    formula_card(
        "Condición de ajuste para 16 tercios de octava",
        r"\sum_{i=1}^{16}d_i\leq 32\ \mathrm{dB}",
        "<b>16 bandas</b>: desde 100 hasta 3.150 Hz<br>"
        "<b>32 dB</b>: suma máxima de desviaciones desfavorables",
        "La referencia se mueve verticalmente en pasos de 1 dB. Se busca la posición "
        "más alta que todavía cumple el límite total de 32 dB.",
    )
    st.info(
        "**Importante:** Rw no es el promedio de R, ni el mayor valor de la curva, ni "
        "simplemente R a 500 Hz. Es el valor de la **curva de referencia ya ajustada** "
        "en la banda de 500 Hz."
    )

    st.markdown("#### Compruébalo moviendo la referencia")
    demo_freq = np.array([100, 125, 160, 200, 250, 315, 400, 500,
                          630, 800, 1000, 1250, 1600, 2000, 2500, 3150])
    demo_r = np.array([27, 31, 35, 39, 43, 47, 50, 52,
                       54, 56, 55, 51, 57, 59, 61, 63], dtype=float)
    demo_ref_shape = np.array([33, 36, 39, 42, 45, 48, 51, 52,
                               53, 54, 55, 56, 56, 56, 56, 56], dtype=float)
    demo_rw = st.slider(
        "Posición de la referencia en 500 Hz (dB)", 42, 58, 50, 1,
        key="lab2_s8_demo_reference",
    )
    demo_ref = demo_ref_shape + (demo_rw - 52)
    demo_dev = np.maximum(0.0, demo_ref - demo_r)
    demo_total = float(np.sum(demo_dev))
    demo_fig = go.Figure()
    demo_fig.add_trace(go.Scatter(x=demo_freq, y=demo_r, mode="lines+markers",
                                  name="R(f)", line=dict(color="#25d6b2", width=4)))
    demo_fig.add_trace(go.Scatter(x=demo_freq, y=demo_ref, mode="lines+markers",
                                  name="Referencia desplazada",
                                  line=dict(color="#ff9f43", width=3, shape="hv")))
    for demo_i in np.where(demo_dev > 0)[0]:
        demo_fig.add_trace(go.Scatter(
            x=[demo_freq[demo_i], demo_freq[demo_i]],
            y=[demo_r[demo_i], demo_ref[demo_i]], mode="lines",
            line=dict(color="#ff4d6d", width=5), showlegend=False,
            hovertemplate=f"{demo_freq[demo_i]} Hz<br>Déficit: {demo_dev[demo_i]:.1f} dB<extra></extra>",
        ))
    demo_fig.update_layout(height=430, xaxis_type="log",
                           xaxis_title="Frecuencia central (Hz)",
                           yaxis_title="Reducción sonora (dB)",
                           hovermode="x unified", margin=dict(l=30, r=20, t=35, b=35))
    demo_fig.update_xaxes(tickvals=demo_freq,
                          ticktext=[str(v) if v < 1000 else f"{v/1000:g}k" for v in demo_freq])
    st.plotly_chart(demo_fig, use_container_width=True)
    demo_a, demo_b, demo_c = st.columns(3)
    demo_a.metric("Bandas desfavorables", int(np.sum(demo_dev > 0)))
    demo_b.metric("Suma de desviaciones", f"{demo_total:.1f} dB")
    demo_c.metric("Condición", "Cumple" if demo_total <= 32 else "No cumple")
    if demo_total <= 32:
        st.success("Esta posición cumple Σdᵢ ≤ 32 dB. Intenta subirla 1 dB: solo será la posición final si la nueva suma deja de cumplir.")
    else:
        st.error("Esta posición supera 32 dB. La referencia debe bajarse hasta recuperar el cumplimiento.")

    st.markdown("### 5 · Procedimiento gráfico para obtener Rw")
    st.markdown("""
    1. Se dispone de los valores de **R** en los 16 tercios de octava entre 100 y
       3.150 Hz.
    2. Se superpone la curva de referencia normalizada.
    3. Se calculan únicamente las diferencias donde la referencia queda sobre R.
    4. Se suman esas desviaciones desfavorables.
    5. Se desplaza la referencia en pasos enteros de 1 dB hasta encontrar la posición
       más alta cuya suma no supera 32 dB.
    6. El valor de esa referencia desplazada a 500 Hz es **Rw**.
    """)
    st.warning(
        "**Error frecuente:** permitir que bandas con aislamiento alto compensen un "
        "valle. El método no lo permite: las diferencias favorables valen cero."
    )

    rw_step = st.select_slider(
        "Recorre el procedimiento",
        options=[1, 2, 3, 4, 5], value=1,
        format_func=lambda n: {
            1: "1 · Curva R(f)", 2: "2 · Superponer referencia",
            3: "3 · Identificar déficits", 4: "4 · Verificar Σdᵢ ≤ 32 dB",
            5: "5 · Leer Rw en 500 Hz",
        }[n], key="lab2_s8_rw_step",
    )
    guided = go.Figure()
    guided.add_trace(go.Scatter(x=demo_freq, y=demo_r, mode="lines+markers",
                                name="R(f)", line=dict(color="#25d6b2", width=4)))
    if rw_step >= 2:
        guided.add_trace(go.Scatter(x=demo_freq, y=demo_ref, mode="lines+markers",
                                    name="Curva de referencia",
                                    line=dict(color="#ff9f43", width=3, shape="hv")))
    if rw_step >= 3:
        for demo_i in np.where(demo_dev > 0)[0]:
            guided.add_trace(go.Scatter(x=[demo_freq[demo_i], demo_freq[demo_i]],
                                        y=[demo_r[demo_i], demo_ref[demo_i]], mode="lines",
                                        line=dict(color="#ff4d6d", width=5), showlegend=False))
    if rw_step == 5:
        guided.add_vline(x=500, line_dash="dot", line_color="#ffffff")
        guided.add_annotation(x=500, y=demo_rw, text=f"Rw = {demo_rw} dB",
                              showarrow=True, arrowhead=2, bgcolor="#10263c")
    guided.update_layout(height=400, xaxis_type="log", xaxis_title="Frecuencia (Hz)",
                         yaxis_title="R (dB)", margin=dict(l=30, r=20, t=30, b=35))
    guided.update_xaxes(tickvals=demo_freq,
                        ticktext=[str(v) if v < 1000 else f"{v/1000:g}k" for v in demo_freq])
    st.plotly_chart(guided, use_container_width=True)
    guided_text = {
        1: "Primero se necesita la curva R(f) completa en las 16 bandas.",
        2: "La plantilla conserva su forma y se desplaza verticalmente en pasos enteros de 1 dB.",
        3: "Las líneas rojas son los únicos déficits que se contabilizan; los excedentes valen cero.",
        4: f"La suma actual es {demo_total:.1f} dB. Debe ser menor o igual que 32 dB.",
        5: f"Una vez hallada la posición más alta admisible, se lee la referencia a 500 Hz: Rw = {demo_rw} dB.",
    }[rw_step]
    st.info(guided_text)

    st.markdown("### 6 · ¿Qué significan C y Ctr?")
    st.write("""
    Dos elementos con el mismo Rw pueden comportarse de manera distinta frente a
    una conversación, música o tránsito. Los términos de adaptación espectral
    incorporan esa diferencia mediante espectros normalizados.

    - **C** se usa para la familia espectral con mayor importancia relativa en
      frecuencias medias y altas, asociada, por ejemplo, a actividades de vivienda,
      conversación, juegos infantiles o tránsito ferroviario rápido.
    - **Ctr** se usa para fuentes con contenido grave importante, como tránsito
      urbano, buses, camiones, música con bajos o ciertas fuentes industriales.
    """)
    formula_card(
        "Nivel resultante del espectro adaptado",
        r"X=-10\log_{10}\left(\sum_i10^{(L_i-R_i)/10}\right)",
        "<b>X</b>: aislamiento global frente al espectro considerado (dB)<br>"
        "<b>Lᵢ</b>: nivel relativo normalizado del espectro en la banda i (dB)<br>"
        "<b>Rᵢ</b>: reducción sonora del elemento en la banda i (dB)",
        "Se resta el aislamiento banda por banda al espectro de la fuente y se suma "
        "energéticamente lo que logra transmitirse.",
    )
    formula_card(
        "Términos de adaptación espectral",
        r"C=X_1-R_w,\qquad C_{tr}=X_2-R_w",
        "<b>X₁</b>: resultado con el espectro de referencia 1<br>"
        "<b>X₂</b>: resultado con el espectro de referencia 2<br>"
        "<b>Rw</b>: índice ponderado (dB)",
        "C y Ctr no son aislamientos independientes: se suman algebraicamente a Rw.",
    )
    st.markdown(
        '<div class="good"><b>Forma correcta de informar:</b> '
        'R<sub>w</sub>(C; C<sub>tr</sub>) = 52 (−2; −7) dB<br>'
        '<span>Para el espectro 1: Rw+C = 50 dB · Para tránsito: Rw+Ctr = 45 dB</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 6.1 · Punto de partida: conservar el Rw ya construido")
    st.write(
        "Para obtener **C** y **Ctr** no se construye otra curva ni se vuelve a "
        "calcular Rw. Se conserva la misma curva R(f) del procedimiento anterior "
        "y la posición final de la curva de referencia. Sobre ese resultado se "
        "aplican, uno después del otro, los dos espectros normalizados."
    )

    frequencies = demo_freq.astype(float)
    spectrum_c = np.array(
        [-29, -26, -23, -21, -19, -17, -15, -13,
         -12, -11, -10, -9, -9, -9, -9, -9],
        dtype=float,
    )
    spectrum_ctr = np.array(
        [-20, -20, -18, -16, -15, -14, -13, -12,
         -11, -9, -8, -9, -10, -11, -13, -15],
        dtype=float,
    )
    r_curve = demo_r.copy()
    best_shift = -60
    for shift in range(-60, 61):
        shifted = demo_ref_shape + shift
        deviations = np.maximum(0.0, shifted - r_curve)
        if float(np.sum(deviations)) <= 32.0 + 1e-9:
            best_shift = shift
    shifted_reference = demo_ref_shape + best_shift
    deviations = np.maximum(0.0, shifted_reference - r_curve)
    rw_value = int(round(52 + best_shift))
    x_c = -10.0 * np.log10(np.sum(10.0 ** ((spectrum_c - r_curve) / 10.0)))
    x_ctr = -10.0 * np.log10(np.sum(10.0 ** ((spectrum_ctr - r_curve) / 10.0)))
    c_value = int(round(x_c - rw_value))
    ctr_value = int(round(x_ctr - rw_value))
    total_deviation = float(np.sum(deviations))
    transmitted_c = spectrum_c - r_curve
    transmitted_ctr = spectrum_ctr - r_curve

    st.markdown(
        f'<div class="good"><b>Resultado que continúa desde el punto anterior:</b> '
        f'R<sub>w</sub> = {rw_value} dB · Σd<sub>i</sub> = {total_deviation:.1f} dB</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 6.2 · Construcción paso a paso de C")
    c_step = st.select_slider(
        "Recorre la construcción de C",
        options=[1, 2, 3, 4], value=1,
        format_func=lambda n: {
            1: "1 · Aplicar espectro 1", 2: "2 · Restar R(f)",
            3: "3 · Sumar la transmisión", 4: "4 · Obtener C",
        }[n], key="lab2_s8_c_step",
    )
    c_fig = go.Figure()
    c_fig.add_trace(go.Bar(x=frequencies, y=spectrum_c, name="Espectro 1",
                           marker_color="#56a8ff"))
    if c_step >= 2:
        c_fig.add_trace(go.Scatter(x=frequencies, y=transmitted_c,
                                   mode="lines+markers", name="Lᵢ − Rᵢ",
                                   line=dict(color="#ff9f43", width=4)))
    c_fig.update_layout(height=390, barmode="overlay", xaxis_type="log",
                        xaxis_title="Frecuencia central (Hz)",
                        yaxis_title="Nivel relativo (dB)",
                        margin=dict(l=30, r=20, t=25, b=35))
    c_fig.update_xaxes(tickvals=frequencies,
                       ticktext=[str(int(v)) if v < 1000 else f"{v/1000:g}k" for v in frequencies])
    st.plotly_chart(c_fig, use_container_width=True)
    c_explanation = {
        1: "El espectro 1 fija cuánta energía relativa aporta cada tercio de octava.",
        2: "Se resta Rᵢ en cada banda. El resultado Lᵢ−Rᵢ representa la energía relativa que logra transmitirse.",
        3: f"Las 16 contribuciones se suman energéticamente, no aritméticamente: X₁ = {x_c:.1f} dB.",
        4: f"Finalmente, C = X₁ − Rw = {x_c:.1f} − {rw_value} = {c_value:+d} dB.",
    }[c_step]
    st.info(c_explanation)
    if c_step >= 3:
        st.latex(rf"X_1=-10\log_{{10}}\left(\sum_i10^{{(L_{{1,i}}-R_i)/10}}\right)={x_c:.1f}\ \mathrm{{dB}}")
    if c_step == 4:
        st.latex(rf"C=X_1-R_w={x_c:.1f}-{rw_value}={c_value:+d}\ \mathrm{{dB}}")
        st.success(f"Para el espectro 1: Rw + C = {rw_value + c_value} dB.")

    st.markdown("#### 6.3 · Construcción paso a paso de Ctr")
    ctr_step = st.select_slider(
        "Recorre la construcción de Ctr",
        options=[1, 2, 3, 4], value=1,
        format_func=lambda n: {
            1: "1 · Aplicar espectro 2", 2: "2 · Restar R(f)",
            3: "3 · Sumar la transmisión", 4: "4 · Obtener Ctr",
        }[n], key="lab2_s8_ctr_step",
    )
    ctr_fig = go.Figure()
    ctr_fig.add_trace(go.Bar(x=frequencies, y=spectrum_ctr, name="Espectro 2",
                             marker_color="#b06cff"))
    if ctr_step >= 2:
        ctr_fig.add_trace(go.Scatter(x=frequencies, y=transmitted_ctr,
                                     mode="lines+markers", name="Lᵢ − Rᵢ",
                                     line=dict(color="#ff4d6d", width=4)))
    ctr_fig.update_layout(height=390, barmode="overlay", xaxis_type="log",
                          xaxis_title="Frecuencia central (Hz)",
                          yaxis_title="Nivel relativo (dB)",
                          margin=dict(l=30, r=20, t=25, b=35))
    ctr_fig.update_xaxes(tickvals=frequencies,
                         ticktext=[str(int(v)) if v < 1000 else f"{v/1000:g}k" for v in frequencies])
    st.plotly_chart(ctr_fig, use_container_width=True)
    ctr_explanation = {
        1: "El espectro 2 asigna mayor importancia relativa a las bajas frecuencias, características del tránsito urbano.",
        2: "Se resta la misma curva Rᵢ. Los valores L₂,ᵢ−Rᵢ muestran qué bandas graves dominan la transmisión.",
        3: f"Se realiza nuevamente una suma energética de las 16 bandas: X₂ = {x_ctr:.1f} dB.",
        4: f"Finalmente, Ctr = X₂ − Rw = {x_ctr:.1f} − {rw_value} = {ctr_value:+d} dB.",
    }[ctr_step]
    st.info(ctr_explanation)
    if ctr_step >= 3:
        st.latex(rf"X_2=-10\log_{{10}}\left(\sum_i10^{{(L_{{2,i}}-R_i)/10}}\right)={x_ctr:.1f}\ \mathrm{{dB}}")
    if ctr_step == 4:
        st.latex(rf"C_{{tr}}=X_2-R_w={x_ctr:.1f}-{rw_value}={ctr_value:+d}\ \mathrm{{dB}}")
        st.success(f"Para el espectro de tránsito: Rw + Ctr = {rw_value + ctr_value} dB.")

    st.markdown("#### 6.4 · Resultado completo")
    st.markdown(
        f'<div class="good"><b>Forma normalizada de informar:</b> '
        f'R<sub>w</sub>(C; C<sub>tr</sub>) = {rw_value} '
        f'({c_value:+d}; {ctr_value:+d}) dB<br>'
        f'<span>Rw+C = {rw_value+c_value} dB · '
        f'Rw+Ctr = {rw_value+ctr_value} dB</span></div>',
        unsafe_allow_html=True,
    )

    table = pd.DataFrame({
        "Frecuencia (Hz)": frequencies.astype(int),
        "R(f) (dB)": r_curve,
        "Espectro 1 (dB)": spectrum_c.astype(int),
        "L1-R (dB)": transmitted_c,
        "Espectro 2 (dB)": spectrum_ctr.astype(int),
        "L2-R (dB)": transmitted_ctr,
    })
    with st.expander("Ver cálculo banda por banda de C y Ctr"):
        st.dataframe(table.round(1), hide_index=True, use_container_width=True)

    st.markdown("### 7 · Cómo interpretar el resultado")
    source_type = st.radio(
        "Selecciona la fuente que quieres evaluar",
        ["Voces y actividades de vivienda", "Tránsito urbano, buses o música con bajos",
         "Fuente tonal o banda dominante"],
        horizontal=True,
        key="lab2_s8_source_type",
    )
    if source_type == "Voces y actividades de vivienda":
        st.info(
            f"Revisa principalmente **Rw+C = {rw_value+c_value} dB**, junto con la "
            "curva R(f) en las bandas donde se concentra la fuente."
        )
    elif source_type == "Tránsito urbano, buses o música con bajos":
        st.info(
            f"Revisa principalmente **Rw+Ctr = {rw_value+ctr_value} dB** y confirma "
            "el desempeño real en bajas frecuencias."
        )
    else:
        st.info(
            "Un número único puede ocultar la banda decisiva. Para una fuente tonal "
            "debe revisarse directamente **R(f)** en la frecuencia dominante."
        )
    st.warning(
        "Un Rw mayor no garantiza por sí solo la mejor solución para cualquier fuente. "
        "Dos elementos con igual Rw pueden tener Ctr y curvas graves muy diferentes."
    )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · precisión técnica y conducción"):
            st.markdown("""
            - Presente primero la curva R(f). El índice único debe aparecer como una
              consecuencia del análisis por bandas, no como sustituto de este.
            - La referencia se desplaza verticalmente sin cambiar su forma. El ajuste
              se realiza en pasos de 1 dB y se conserva la posición más alta que cumple
              la suma máxima de desviaciones desfavorables.
            - Las diferencias favorables no se restan de las desfavorables. Esta regla
              evita que un buen desempeño agudo oculte un valle importante.
            - Rw caracteriza el elemento bajo el método de ensayo correspondiente.
              No debe prometerse el mismo valor para la construcción instalada sin
              considerar sellos, encuentros, flancos y calidad de ejecución.
            - C y Ctr se calculan energéticamente con espectros normalizados. En muchos
              sistemas constructivos Ctr es más negativo porque el aislamiento suele
              ser menor en graves y el espectro de tránsito pondera más esa región.
            - La notación completa conserva los signos: 52 (−2; −7) dB. No escriba
              “C = 2” si el resultado real es −2 dB.
            """)
            st.latex(
                r"R_w(C;C_{tr})=52(-2;-7)\ \mathrm{dB}"
            )
            st.latex(
                r"R_w+C=50\ \mathrm{dB},\qquad R_w+C_{tr}=45\ \mathrm{dB}"
            )

    st.markdown("### 8 · Cinco preguntas de comprensión")
    check(
        "lab2_s8_q1",
        "¿Qué representa Rw?",
        [
            "Un índice único obtenido ajustando una curva de referencia a R(f)",
            "El promedio aritmético de todos los valores R",
            "El aislamiento exacto en todas las frecuencias",
            "El coeficiente de absorción del muro",
        ],
        "Un índice único obtenido ajustando una curva de referencia a R(f)",
        "Rw resume la curva mediante un procedimiento de referencia y desviaciones.",
    )
    check(
        "lab2_s8_q2",
        "¿Cuándo existe una desviación desfavorable?",
        [
            "Cuando la referencia ajustada queda sobre la curva R",
            "Cuando R queda sobre la referencia",
            "Siempre que la frecuencia supera 500 Hz",
            "Solo cuando Ctr es negativo",
        ],
        "Cuando la referencia ajustada queda sobre la curva R",
        "Solo el déficit de R respecto de la referencia aporta a la suma desfavorable.",
    )
    check(
        "lab2_s8_q3",
        "¿Dónde se lee Rw después de ajustar la referencia?",
        [
            "En el valor de la referencia ajustada a 500 Hz",
            "En la banda con mayor R",
            "En el promedio entre 100 y 3150 Hz",
            "En el valor de Ctr",
        ],
        "En el valor de la referencia ajustada a 500 Hz",
        "Ese valor define el índice ponderado una vez cumplido el criterio de ajuste.",
    )
    check(
        "lab2_s8_q4",
        "¿Qué combinación es especialmente pertinente frente a tránsito urbano?",
        ["Rw+Ctr", "Rw+C únicamente", "R a 3150 Hz únicamente", "El promedio de C y Ctr"],
        "Rw+Ctr",
        "Ctr adapta el resultado a un espectro con mayor contenido relativo en bajas frecuencias.",
    )
    check(
        "lab2_s8_q5",
        "¿Puede una fuente tonal evaluarse correctamente usando solo Rw?",
        [
            "No; debe revisarse también R(f) en la banda dominante",
            "Sí; Rw siempre contiene toda la información espectral",
            "Sí, pero solo si Ctr es cero",
            "No; debe usarse absorción Sabine",
        ],
        "No; debe revisarse también R(f) en la banda dominante",
        "El número único puede ocultar un valle localizado justo en la frecuencia de la fuente.",
    )

def _stage9_impl():
    _lab2_heading(
        9,"Evaluación final · Preguntas de comprensión",
        "Diez preguntas de selección única · 20 minutos · 40 puntos.",
    )
    st.info(
        "Esta evaluación tiene un solo intento. Tus respuestas se guardan automáticamente. "
        "Al enviar o agotarse el tiempo, el intento quedará cerrado y podrás revisar la pauta completa."
    )

    if st.session_state.get("role")=="Docente":
        teacher_stage9_answer_key()
        st.markdown("---")
        st.markdown("### Respuestas de alumnos y rúbrica")
        teacher_stage9_results()
        return

    remote=_stage9_submission()
    submitted=bool(remote or st.session_state.get("e9_submitted"))
    if submitted:
        saved=(remote or {}).get("answers") or st.session_state.get("e9_saved_answers",{})
        score=(remote or {}).get("score",st.session_state.get("e9_score",0))
        st.success(f"Evaluación finalizada · Puntaje: {score:g}/40")
        st.caption("El intento está cerrado. Puedes volver a esta etapa cuando quieras para revisar tus respuestas.")
        for i,item in enumerate(STAGE9_QUESTIONS):
            student_answer=saved.get(str(i)) if isinstance(saved,dict) else None
            correct=item["options"][item["correct"]]
            with st.expander(f"Pregunta {i+1} · {item['title']}",expanded=i==0):
                st.markdown(f"**{item['question']}**")
                st.write(f"Tu respuesta: {student_answer or 'Sin respuesta'}")
                if student_answer==correct:
                    st.success(f"Respuesta correcta: {correct}")
                else:
                    st.error(f"Respuesta correcta: {correct}")
                st.info(item["explanation"])
        return

    if not st.session_state.get("e9_started_at"):
        st.markdown("### Antes de comenzar")
        st.markdown(
            "- Dispondrás de **20 minutos continuos**.\n"
            "- Cada respuesta vale **4 puntos**.\n"
            "- Puedes cambiar tus respuestas mientras el tiempo esté activo.\n"
            "- Al finalizar, no podrás responder nuevamente sin un reinicio docente."
        )
        if st.button("Comenzar evaluación",type="primary",use_container_width=True,key="e9_start_button"):
            now=dt.datetime.now(dt.timezone.utc)
            st.session_state["e9_started_at"]=now.isoformat()
            st.session_state["e9_deadline"]=(now+dt.timedelta(minutes=20)).isoformat()
            save_user_progress()
            st.rerun()
        return

    deadline=st.session_state.get("e9_deadline")
    if not deadline:
        started=dt.datetime.fromisoformat(st.session_state["e9_started_at"].replace("Z","+00:00"))
        deadline=(started+dt.timedelta(minutes=20)).isoformat()
        st.session_state["e9_deadline"]=deadline
    _stage9_clock(deadline)

    for i,item in enumerate(STAGE9_QUESTIONS):
        st.markdown(
            f'<div class="question-box"><div class="question-label">PREGUNTA {i+1} DE 10 · 4 PUNTOS</div>'
            f'<div class="question-text">{item["question"]}</div></div>',
            unsafe_allow_html=True,
        )
        st.radio(
            "Selecciona una alternativa",item["options"],index=None,
            key=f"e9_q{i}",label_visibility="collapsed",
        )

    answered=sum(st.session_state.get(f"e9_q{i}") is not None for i in range(10))
    st.progress(answered/10)
    st.caption(f"{answered} de 10 respuestas registradas y guardadas.")
    if st.button("Enviar evaluación definitiva",type="primary",use_container_width=True,key="e9_submit_button"):
        if answered<10:
            st.warning(f"Aún faltan {10-answered} preguntas. Puedes enviarla, pero quedarán sin puntaje.")
            st.session_state["e9_confirm_incomplete"]=True
        else:
            _finish_stage9("submitted")
            st.rerun()
    if st.session_state.get("e9_confirm_incomplete") and answered<10:
        if st.button("Confirmar envío con respuestas pendientes",key="e9_submit_incomplete"):
            _finish_stage9("submitted_incomplete")
            st.rerun()

def _stage10_impl():
    _lab2_heading(10,"Diseño integrador · paramento sala–pasillo","Diseña muro, ventana y puerta; calcula Rw, C y Ctr; y verifica el requisito Rw ≥ 40 dB.")
    st.info("Duración: 40 minutos · 60 puntos. Las curvas se calculan con las mismas herramientas físicas utilizadas en las etapas anteriores.")
    st.markdown("### Encargo profesional")
    st.markdown("Una sala de clases de **8,00 × 6,00 × 3,00 m** recibe ruido desde el pasillo. El paramento separador mide **8,00 × 3,00 m** y debe alcanzar **Rw ≥ 40 dB**. Debes diseñar y seleccionar sus tres componentes.")
    geo=pd.DataFrame([["Muro o tabique",19.71,"82,13 %"],["Ventana 2,00 × 1,20 m",2.40,"10,00 %"],["Puerta 0,90 × 2,10 m",1.89,"7,87 %"],["Total",24.00,"100 %"]],columns=["Elemento","Superficie (m²)","Proporción"])
    st.dataframe(geo,hide_index=True,use_container_width=True)
    if st.session_state.get("role")=="Docente":
        teacher_lab2_stage10_answer_key()
        st.markdown("---")
        st.markdown("### Resultados enviados por los alumnos")
        _teacher_lab2_integrated_results()
        return

    st.markdown("## 1 · Diseña el muro o tabique")
    wall_type=st.radio("Sistema opaco",["Muro o placa simple","Tabique de placa doble"],horizontal=True,key="l2s10_wall_type")
    if wall_type=="Muro o placa simple":
        c1,c2=st.columns(2); mat=c1.selectbox("Material",list(LAB2_S10_MATERIALS),key="l2s10_sm"); th=c2.selectbox("Espesor (mm)",LAB2_S10_MATERIALS[mat]["th"],key="l2s10_st")
        wall_curve=_lab2_s10_single(mat,th); wall_desc=f"{mat} · {th:g} mm"
    else:
        a,b=st.columns(2)
        with a:
            m1=st.selectbox("Material hoja 1",list(LAB2_S10_LEAVES),key="l2s10_m1"); t1=st.selectbox("Espesor hoja 1 (mm)",LAB2_S10_LEAVES[m1]["th"],key="l2s10_t1"); n1=st.selectbox("Placas hoja 1",[1,2],key="l2s10_n1")
        with b:
            m2=st.selectbox("Material hoja 2",list(LAB2_S10_LEAVES),key="l2s10_m2"); t2=st.selectbox("Espesor hoja 2 (mm)",LAB2_S10_LEAVES[m2]["th"],key="l2s10_t2"); n2=st.selectbox("Placas hoja 2",[1,2],key="l2s10_n2")
        c,d=st.columns(2); gap=c.selectbox("Cámara (mm)",[40,60,80,100,120,150],key="l2s10_gap"); absorb=d.selectbox("Absorbente",["Sin absorbente","Lana de vidrio 15 kg/m³","Lana de vidrio 32 kg/m³","Lana mineral 40 kg/m³","Lana mineral 60 kg/m³"],key="l2s10_abs")
        wall_curve=_lab2_s10_double(m1,t1,n1,m2,t2,n2,gap,absorb); wall_desc=f"{n1}×{m1} {t1:g} / {gap} mm / {n2}×{m2} {t2:g} · {absorb}"
    wr,wc,wt=_lab2_s10_indices(wall_curve); st.success(f"Resultado diseñado: Rw(C; Ctr) = {wr} ({wc:+d}; {wt:+d}) dB")
    _lab2_s10_plot("Curva del elemento opaco",[("Muro/tabique",wall_curve)])
    if st.button("Incorporar muro al paramento",type="primary",key="l2s10_pick_wall"):
        st.session_state["l2s10_wall"]={"description":wall_desc,"curve":wall_curve.tolist(),"rw":wr,"c":wc,"ctr":wt}; save_user_progress(); st.success("Muro incorporado y guardado.")

    st.markdown("## 2 · Diseña la ventana")
    window_type=st.radio("Tipo de ventana",["Vidrio simple","Ventana doble"],horizontal=True,key="l2s10_window_type")
    if window_type=="Vidrio simple":
        g=st.selectbox("Espesor del vidrio (mm)",[4,5,6,8,10,12],key="l2s10_g"); window_curve,_m,_b,_fc=_glass_panel_tl(g,.010,LAB2_S10_FREQS); window_desc=f"Vidrio simple {g} mm"
    else:
        x,y,z=st.columns(3); g1=x.selectbox("Vidrio 1 (mm)",[4,5,6,8,10,12],key="l2s10_g1"); wg=y.selectbox("Cámara (mm)",[6,10,12,16,20,30,50,80],key="l2s10_wgap"); g2=z.selectbox("Vidrio 2 (mm)",[4,5,6,8,10,12],index=2,key="l2s10_g2")
        window_curve,*_=_double_window_model(g1,g2,wg/1000,1.2,2.0,.10,.010,.010,LAB2_S10_FREQS); window_desc=f"Ventana doble {g1}/{wg}/{g2} mm"
    vr,vc,vt=_lab2_s10_indices(window_curve); st.success(f"Resultado diseñado: Rw(C; Ctr) = {vr} ({vc:+d}; {vt:+d}) dB")
    _lab2_s10_plot("Curva de la ventana",[("Ventana",window_curve)])
    if st.button("Incorporar ventana al paramento",type="primary",key="l2s10_pick_window"):
        st.session_state["l2s10_window"]={"description":window_desc,"curve":np.asarray(window_curve).tolist(),"rw":vr,"c":vc,"ctr":vt}; save_user_progress(); st.success("Ventana incorporada y guardada.")

    st.markdown("## 3 · Selecciona la puerta")
    door=st.selectbox("Solución de puerta",list(LAB2_S10_DOORS),key="l2s10_door_type"); door_curve=_lab2_s10_door_curve(LAB2_S10_DOORS[door]); dr,dc,dtc=_lab2_s10_indices(door_curve)
    st.caption("La curva incluye de forma referencial el efecto de la hoja, sellos y encuentros; no se calcula solo por ley de masa.")
    st.success(f"Resultado referencial: Rw(C; Ctr) = {dr} ({dc:+d}; {dtc:+d}) dB")
    if st.button("Incorporar puerta al paramento",type="primary",key="l2s10_pick_door"):
        st.session_state["l2s10_door"]={"description":door,"curve":door_curve.tolist(),"rw":dr,"c":dc,"ctr":dtc}; save_user_progress(); st.success("Puerta incorporada y guardada.")

    st.markdown("## 4 · Paramento sala de clases–pasillo")
    wall=st.session_state.get("l2s10_wall"); window=st.session_state.get("l2s10_window"); door_saved=st.session_state.get("l2s10_door")
    if not all([wall,window,door_saved]):
        st.warning("Incorpora primero el muro, la ventana y la puerta. Cada botón conserva la curva completa para el cálculo compuesto."); return
    st.markdown(f"""<div style='border-radius:20px;padding:1.2rem;background:linear-gradient(135deg,#eaf5ff,#f8fbff);border:2px solid #88bce8'><b>PASILLO → SALA DE CLASES</b><br><br>🧱 <b>Muro · 19,71 m²:</b> {wall['description']} · Rw {wall['rw']} dB<br>🪟 <b>Ventana · 2,40 m²:</b> {window['description']} · Rw {window['rw']} dB<br>🚪 <b>Puerta · 1,89 m²:</b> {door_saved['description']} · Rw {door_saved['rw']} dB</div>""",unsafe_allow_html=True)
    combined=-10*np.log10((19.71*10**(-np.array(wall["curve"])/10)+2.40*10**(-np.array(window["curve"])/10)+1.89*10**(-np.array(door_saved["curve"])/10))/24.0)
    cr,cc,cct=_lab2_s10_indices(combined); _lab2_s10_plot("Aislamiento por tercios de octava",[("Muro",wall["curve"]),("Ventana",window["curve"]),("Puerta",door_saved["curve"]),("Paramento combinado",combined)])
    with st.expander("Ver tabla espectral del cálculo compuesto"):
        st.dataframe(pd.DataFrame({"Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),"Muro (dB)":np.round(wall["curve"],1),"Ventana (dB)":np.round(window["curve"],1),"Puerta (dB)":np.round(door_saved["curve"],1),"Combinado (dB)":np.round(combined,1)}),hide_index=True,use_container_width=True)
    st.markdown("## 5 · Calcula, ingresa e interpreta tu resultado")
    st.markdown("#### Ecuación del aislamiento compuesto")
    st.latex(r"\tau_{T,f}=\frac{S_m10^{-R_{m,f}/10}+S_v10^{-R_{v,f}/10}+S_p10^{-R_{p,f}/10}}{S_m+S_v+S_p}")
    st.latex(r"R_{T,f}=-10\log_{10}(\tau_{T,f})")
    st.caption("Para este ejercicio: Sm = 19,71 m²; Sv = 2,40 m²; Sp = 1,89 m²; ST = 24,00 m². La combinación se realiza en cada banda, no promediando decibeles ni valores Rw.")
    _lab2_s10_index_workbench(combined)
    st.markdown("### Ingresa tus resultados")
    submitted=bool(st.session_state.get("l2s10_submitted"))
    q1,q2,q3=st.columns(3); ans_rw=q1.number_input("Rw combinado (dB)",0,100,0,key="l2s10_ans_rw",disabled=submitted); ans_c=q2.number_input("C (dB)",-30,10,0,key="l2s10_ans_c",disabled=submitted); ans_ctr=q3.number_input("Ctr (dB)",-30,10,0,key="l2s10_ans_ctr",disabled=submitted)
    st.caption("Puedes corregir y verificar nuevamente cuantas veces necesites. El intento se bloquea únicamente al enviar el desarrollo definitivo.")
    current_signature=(int(ans_rw),int(ans_c),int(ans_ctr))
    if st.button("Verificar resultado",key="l2s10_verify",disabled=submitted):
        st.session_state["l2s10_verified_signature"]=current_signature; st.session_state["l2s10_verified"]=True; save_user_progress()
    verified_signature=tuple(st.session_state.get("l2s10_verified_signature",()))
    verified=verified_signature==current_signature and bool(st.session_state.get("l2s10_verified"))
    if st.session_state.get("l2s10_verified") and not verified:
        st.warning("Modificaste uno o más resultados después de verificar. Presiona nuevamente “Verificar resultado”.")
    if verified:
        numeric=sum([abs(ans_rw-cr)<=1,abs(ans_c-cc)<=1,abs(ans_ctr-cct)<=1]); design_score=20+numeric*(20/3)
        st.success(f"Resultado calculado: Rw(C; Ctr) = {cr} ({cc:+d}; {cct:+d}) dB · Rw+C = {cr+cc} dB")
        (st.success if cr>=40 else st.error)(f"{'Cumple' if cr>=40 else 'No cumple'} el requisito Rw ≥ 40 dB.")
        weakest=min([(wall['rw'],'muro'),(window['rw'],'ventana'),(door_saved['rw'],'puerta')])[1]; st.info(f"Elemento débil de la selección: **{weakest}**. La influencia final depende simultáneamente de su transmisión y superficie.")
    else: design_score=0

    st.markdown("## 6 · Preguntas de comprensión")
    correct_count=0
    answers={}
    for i,(question,options,correct) in enumerate(LAB2_S10_QUESTIONS):
        value=st.radio(f"{i+1}. {question}",options,index=None,key=f"l2s10_q{i}"); answers[str(i)]=value
        if value==options[correct]: correct_count+=1
    comprehension_score=correct_count*4; total=round(design_score+comprehension_score,1)
    st.metric("Puntaje acumulado",f"{total:g}/60")
    if st.button("Enviar desarrollo definitivo",type="primary",use_container_width=True,key="l2s10_submit",disabled=submitted):
        if not verified or any(v is None for v in answers.values()): st.warning("Verifica los resultados actualmente ingresados y responde las cinco preguntas antes de enviar.")
        else:
            payload={"geometry":{"room":"8.00×6.00×3.00 m","wall":19.71,"window":2.40,"door":1.89,"total":24.00},"wall":wall,"window":window,"door":door_saved,"combined_curve":combined.tolist(),"student_result":{"rw":ans_rw,"c":ans_c,"ctr":ans_ctr},"calculated_result":{"rw":cr,"c":cc,"ctr":cct},"answers":answers,"design_score":design_score,"comprehension_score":comprehension_score}
            _save_formative(10,"final_integrated_design","Diseño integrador del paramento sala–pasillo",json.dumps(payload,ensure_ascii=False),"Correcta" if total>=36 else "Parcialmente correcta",f"Resultado automático: {total:g}/60 puntos.",score=total,max_score=60,correct_answer=f"Resultado dependiente del diseño; cálculo verificado banda por banda. Selección enviada: Rw(C;Ctr)={cr}({cc:+d};{cct:+d}) dB.")
            st.session_state["l2s10_submitted"]=True; save_user_progress(); st.success(f"Desarrollo enviado y guardado · {total:g}/60 puntos.")

_STAGES = [
    _stage0_impl,
    _stage1_impl,
    _stage2_impl,
    _stage3_impl,
    _stage4_impl,
    _stage5_impl,
    _stage6_impl,
    _stage7_impl,
    _stage8_impl,
    _stage9_impl,
    _stage10_impl,
]

def run_stage(stage_index, runtime):
    """Ejecuta una etapa usando el contexto vigente de la aplicación principal."""
    _bind_runtime(runtime)
    return _STAGES[stage_index]()
