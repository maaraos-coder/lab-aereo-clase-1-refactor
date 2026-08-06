"""Versiones históricas de etapas.

Estas funciones se conservan únicamente como referencia y no forman parte
del flujo activo de la aplicación. Se extrajeron sin modificar sus cuerpos.
"""

def _legacy_stage7():
    header("ETAPA 7 · APLICACIÓN PRÁCTICA","Diseño de aislamiento acústico",
           "Aplica las ecuaciones de la etapa anterior siguiendo una ruta de cálculo clara y verificable.")
    full_matter(7)
    st.markdown(
        '<div class="question-box"><div class="question-label">CASO GUIADO · MURO CON PUERTA</div>'
        '<div class="question-text">Una sala emisora tiene 82 dB. La separación mide 15 m² e incorpora una puerta de 2 m². '
        'El muro tiene R = 50 dB y la puerta R = 30 dB. Calcula el área débil, el aislamiento compuesto y el nivel estimado en el receptor. '
        'Luego decide si cumple la meta de 45 dB.</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Todos los datos son fijos. Resuelve cada paso y comprueba antes de continuar.")
    source=82.0
    target=45.0
    total_area=15.0
    weak_area=2.0
    wall_area=total_area-weak_area
    r_wall=50.0
    r_weak=30.0
    weak_pct=100*weak_area/total_area
    tau_wall=10**(-r_wall/10)
    tau_weak=10**(-r_weak/10)
    tau_total=(wall_area*tau_wall+weak_area*tau_weak)/total_area
    r_total=-10*math.log10(tau_total)
    receiver=source-r_total
    case_df=pd.DataFrame([
        ["Nivel emisor",f"{source:.0f} dB"],
        ["Área total",f"{total_area:.0f} m²"],
        ["Área de puerta",f"{weak_area:.0f} m²"],
        ["Área efectiva de muro",f"{wall_area:.0f} m²"],
        ["R muro",f"{r_wall:.0f} dB"],
        ["R puerta",f"{r_weak:.0f} dB"],
        ["Meta en receptor",f"≤ {target:.0f} dB"],
    ],columns=["Dato","Valor"])
    st.dataframe(case_df,hide_index=True,use_container_width=True)
    st.markdown(
        '<div class="worked-example"><h3>Origen de las áreas y porcentajes</h3>'
        '<div class="worked-step">El área total de 15 m² corresponde a toda la separación, incluida la puerta.</div>'
        '<div class="worked-step">Área efectiva del muro = 15−2 = <b>13 m²</b>.</div>'
        '<div class="worked-step">Porcentaje de puerta = (2/15)×100 = <b>13,3 %</b>. '
        'En la ecuación se usa 2/15 = 0,1333.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="good"><b>Resultado del paso geométrico:</b> la puerta ocupa '
        '<b>13,3 %</b> de la separación, porque (2 m²/15 m²)×100 = 13,3 %. '
        'Este porcentaje proviene de las áreas del caso y no es un dato supuesto.</div>',
        unsafe_allow_html=True,
    )
    formula_card(
        "Combinación energética del muro y la puerta",
        r"\tau_i=10^{-R_i/10}\qquad"
        r"\tau_{\mathrm{total}}=\frac{S_{\mathrm{muro}}\tau_{\mathrm{muro}}+"
        r"S_{\mathrm{puerta}}\tau_{\mathrm{puerta}}}{S_{\mathrm{total}}}"
        r"\qquad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
        "<b>Rᵢ</b>: reducción sonora de cada elemento (dB)<br>"
        "<b>τᵢ</b>: coeficiente de transmisión de cada elemento (adimensional)<br>"
        "<b>S<sub>muro</sub></b>: área efectiva del muro = 13 m²<br>"
        "<b>S<sub>puerta</sub></b>: área de la puerta = 2 m²<br>"
        "<b>S<sub>total</sub></b>: área total de la separación = 15 m²",
        "Para combinar elementos con aislamientos diferentes. Los valores de R en dB "
        "no se promedian; primero deben convertirse a coeficientes τ y ponderarse por área.",
    )
    check("e7_guided_tau","¿Qué coeficientes de transmisión corresponden al muro y a la puerta?",
          ["τmuro=10⁻⁵ y τpuerta=10⁻³","τmuro=50 y τpuerta=30","τmuro=0,50 y τpuerta=0,30"],
          "τmuro=10⁻⁵ y τpuerta=10⁻³",
          "Se aplica τ=10^(−R/10): para 50 dB resulta 10⁻⁵ y para 30 dB resulta 10⁻³.")
    st.latex(rf"\tau_{{total}}=\frac{{13(10^{{-5}})+2(10^{{-3}})}}{{15}}={tau_total:.6f}")
    st.latex(rf"R_{{total}}=-10\log_{{10}}(\tau_{{total}})={r_total:.1f}\ \mathrm{{dB}}")
    formula_card(
        "Diferencia de nivel y estimación del nivel receptor",
        r"\begin{aligned}"
        r"\Delta L &= L_{\mathrm{emisor}}-L_{\mathrm{receptor}}\\"
        r"L_{\mathrm{receptor}} &\approx L_{\mathrm{emisor}}-R_{\mathrm{total}}"
        r"\end{aligned}",
        "<b>ΔL</b>: diferencia entre el nivel emisor y el nivel receptor (dB)<br>"
        "<b>L<sub>emisor</sub></b>: nivel en la sala emisora = 82 dB<br>"
        "<b>L<sub>receptor</sub></b>: nivel estimado en la sala receptora (dB)<br>"
        "<b>R<sub>total</sub></b>: aislamiento compuesto calculado = "
        f"{r_total:.1f} dB",
        "En este ejercicio simplificado se considera que la reducción producida por la "
        "separación es aproximadamente igual a la diferencia de nivel. Por eso se resta "
        "Rtotal al nivel emisor. En una medición normalizada real también deben considerarse "
        "la geometría y las condiciones acústicas del recinto receptor.",
    )
    st.latex(
        rf"L_{{\mathrm{{receptor}}}}\approx 82-{r_total:.1f}"
        rf"={receiver:.1f}\ \mathrm{{dB}}"
    )
    check("e7_guided_result",f"Con Rtotal ≈ {r_total:.1f} dB, ¿cuál es el nivel receptor estimado y cumple la meta?",
          [f"{receiver:.1f} dB; sí cumple",f"{receiver:.1f} dB; no cumple","32,0 dB; sí cumple","52,0 dB; no cumple"],
          f"{receiver:.1f} dB; sí cumple",
          f"En esta estimación simplificada, ΔL ≈ Rtotal y Lreceptor = 82−{r_total:.1f} "
          f"= {receiver:.1f} dB. Como es menor o igual que 45 dB, el caso cumple.")
    st.markdown(
        '<div class="good"><b>Lectura profesional:</b> el procedimiento siempre sigue la misma ruta: '
        'áreas → porcentajes → τ de cada elemento → τ ponderado → R compuesto → '
        'diferencia de nivel estimada → nivel receptor → comparación con la meta.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>🧪</span><h3>Aplicación conceptual III · 11 ejercicios</h3></div>',unsafe_allow_html=True)
    solutions={}
    q="En un ensayo simplificado, el nivel medio en el recinto emisor es 85 dB y en el receptor es 45 dB. Sin aplicar correcciones de recinto, calcula R."
    s="Aplicación simplificada: **R = L₁ − L₂ = 85 − 45 = 40 dB**. En un ensayo normalizado real se incorporan las correcciones y condiciones definidas por el método."
    formative_numeric(7,"s7q1",q,[("r","R (dB)",0.0,1.0)],lambda v:(abs(v["r"]-40)<.1,"R debe ser 40 dB: resta nivel receptor al nivel emisor."),s);solutions["s7q1"]=s
    q="Para un elemento con R = 40 dB, calcula el coeficiente de transmisión τ."
    s="**τ = 10^(−R/10) = 10⁻⁴ = 0,0001**, equivalente a 0,01 % de la energía incidente."
    formative_numeric(7,"s7q2",q,[("tau","τ",0.0,0.0001)],lambda v:(abs(v["tau"]-0.0001)<=0.00001,"τ debe ser 0,0001."),s);solutions["s7q2"]=s
    q="Aplica la ley de masa ideal para m′ = 30 kg/m² y f = 500 Hz. Calcula R."
    expected=20*math.log10(30*500)-47
    s=f"**R ≈ 20 log₁₀(30×500) − 47 = {expected:.1f} dB**. Es una aproximación válida solo en la región controlada por masa."
    formative_numeric(7,"s7q3",q,[("r","R (dB)",0.0,0.1)],lambda v:(abs(v["r"]-expected)<=0.3,f"El resultado esperado es aproximadamente {expected:.1f} dB."),s);solutions["s7q3"]=s
    st.markdown("#### Ejercicio guiado · Rigidez flexional y frecuencia crítica")
    formula_card(
        "Ecuaciones que debes aplicar",
        r"\begin{aligned}"
        r"D&=\frac{Eh^3}{12(1-\nu^2)}\\[0.65em]"
        r"f_c&=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}"
        r"\end{aligned}",
        "<b>D</b>: rigidez flexional de la placa (N·m)<br>"
        "<b>E</b>: módulo de Young (Pa)<br>"
        "<b>h</b>: espesor de la placa (m)<br>"
        "<b>ν</b>: coeficiente de Poisson (adimensional)<br>"
        "<b>f<sub>c</sub></b>: frecuencia crítica o de coincidencia (Hz)<br>"
        "<b>c</b>: velocidad del sonido en el aire (m/s)<br>"
        "<b>m′</b>: masa superficial de la placa (kg/m²)",
        "Primero calcula D con todas las magnitudes en el Sistema Internacional. "
        "Después utiliza ese resultado en la ecuación de fᶜ.",
    )
    st.markdown(
        '<div class="worked-example"><h3>Preparación de los datos</h3>'
        '<div class="worked-step"><strong>Módulo de Young:</strong> '
        'E = 2,5 GPa = <b>2,5×10⁹ Pa</b>.</div>'
        '<div class="worked-step"><strong>Espesor:</strong> '
        'h = 12 mm = <b>0,012 m</b>.</div>'
        '<div class="worked-step"><strong>Datos que ya están en SI:</strong> '
        'ν = 0,30; m′ = 9,6 kg/m²; c = 343 m/s.</div>'
        '<div class="worked-result">Ruta de cálculo: convertir unidades → calcular D → '
        'calcular fᶜ → interpretar el resultado.</div></div>',
        unsafe_allow_html=True,
    )
    q=("Una placa tiene E = 2,5 GPa, h = 12 mm, ν = 0,30, m′ = 9,6 kg/m² "
       "y c = 343 m/s. Calcula primero la rigidez flexional D y después la frecuencia "
       "crítica fᶜ.")
    s=("Con unidades SI: **D = Eh³/[12(1−ν²)] = 395,6 N·m**. Luego, "
       "**fᶜ = c²/(2π)√(m′/D) ≈ 2.917 Hz**. Cerca de esa frecuencia puede producirse "
       "el fenómeno de coincidencia: la placa radia con mayor eficiencia y aparece una "
       "disminución o valle en su aislamiento.")
    formative_numeric(7,"s7q4",q,[("d","D (N·m)",0.0,1.0),("fc","fᶜ (Hz)",0.0,10.0)],
        lambda v:(abs(v["d"]-395.6)<=3 and abs(v["fc"]-2917)<=25,"Se esperaba D ≈ 395,6 N·m y fᶜ ≈ 2.917 Hz. Verifica convertir 12 mm a 0,012 m."),s);solutions["s7q4"]=s
    check(
        "s7q4_interpretation",
        "¿Qué puede ocurrir con el aislamiento de la placa cerca de su frecuencia crítica fᶜ?",
        [
            "Puede disminuir y formar un valle por el fenómeno de coincidencia",
            "Aumenta siempre 6 dB, sin importar el material",
            "La placa deja de transmitir completamente",
            "Solo cambia el tiempo de reverberación del recinto",
        ],
        "Puede disminuir y formar un valle por el fenómeno de coincidencia",
        "Cerca de fᶜ aumenta la eficiencia de acoplamiento y radiación de la placa, "
        "por lo que el aislamiento puede presentar una caída.",
    )
    q="Un recinto posee 60 m² de superficie con α = 0,10 y agrega 25 m² de material con α = 0,80. Calcula la absorción equivalente total."
    s="**A = 60×0,10 + 25×0,80 = 6 + 20 = 26 m² sabin**."
    formative_numeric(7,"s7q5",q,[("a","A total (m² sabin)",0.0,1.0)],lambda v:(abs(v["a"]-26)<.1,"La absorción equivalente total es 26 m² sabin."),s);solutions["s7q5"]=s
    q="Compara dos ventanas: A tiene Rw = 40 dB y B tiene Rw = 35 dB. ¿Cuál transmite menos energía y cuántas veces difieren aproximadamente sus coeficientes τ?"
    s="La ventana A transmite menos. Una diferencia de 5 dB corresponde a una razón de transmisión de **10^(5/10) ≈ 3,16**: B transmite aproximadamente 3,16 veces más energía que A."
    formative_development(7,"s7q6",q,s,[["a","40"],["menos","menor"],["3,16","3.16","tres"]],"No compares los dB como una razón lineal: convierte la diferencia mediante 10^(ΔR/10).");solutions["s7q6"]=s
    q="¿Qué ocurre idealmente con R cuando se duplica la masa superficial de una hoja simple?"
    s="En la región ideal controlada por masa, **R aumenta aproximadamente 6 dB**. No es una regla universal cerca de resonancias, coincidencia, fugas o flancos."
    formative_development(7,"s7q7",q,s,[["6","seis"],["masa"],["ideal","coincid","resonan","aproxim"]],"Indica tanto la mejora aproximada como las condiciones que limitan la ley de masa.");solutions["s7q7"]=s
    q="¿Qué función cumple la lana mineral dentro de un tabique de doble hoja?"
    s="Absorbe y amortigua la energía dentro de la cámara, reduce la severidad de resonancias y mejora el sistema. **No aporta aislamiento por sí sola ni sustituye el desacoplamiento**, la masa o el sellado."
    formative_development(7,"s7q8",q,s,[["absor","amort"],["cámara","camara","resonan"],["no","desacopl","masa"]],"Evita atribuirle a la lana mineral toda la capacidad aislante del tabique.");solutions["s7q8"]=s
    q="Un muro de alto aislamiento incorpora una ventana pequeña de bajo R. ¿Cómo puede afectar esa ventana al aislamiento global?"
    s="Puede dominar el resultado global porque su τ es mucho mayor que el del muro. Se deben combinar los coeficientes de transmisión ponderados por área; **no se promedian los dB**."
    formative_development(7,"s7q9",q,s,[["domina","reduce","debil"],["coeficiente","tau","transmis"],["área","area"],["no","promedi"]],"Explica por qué una superficie pequeña puede transportar una fracción grande de la energía.");solutions["s7q9"]=s
    q="El muro separador fue mejorado, pero el ruido sigue llegando por la unión con el cielo y el piso. ¿Qué fenómeno ocurre y cómo se aborda?"
    s="Existe **transmisión indirecta o por flancos**. Deben diagnosticarse los encuentros y vías estructurales, controlar continuidades rígidas, sellar pasos y diseñar el conjunto constructivo, no solo el paño separador."
    formative_development(7,"s7q10",q,s,[["flanco","indirect"],["cielo","piso","encuentro"],["vía","via","estructura","sell"]],"Nombra la trayectoria real y propone una intervención sobre ese encuentro.");solutions["s7q10"]=s
    q="Un muro de 12 m² tiene R = 55 dB e incorpora una puerta de 2 m² con R = 25 dB. Calcula el R compuesto."
    tau_total=(12*10**(-55/10)+2*10**(-25/10))/14
    r_total=-10*math.log10(tau_total)
    s=f"τtotal = [12·10^(−55/10)+2·10^(−25/10)]/14. Por tanto, **Rtotal ≈ {r_total:.1f} dB**. La puerta reduce drásticamente el desempeño del conjunto."
    formative_numeric(7,"s7q11",q,[("r","R compuesto (dB)",0.0,0.1)],
        lambda v:(abs(v["r"]-r_total)<=0.3,f"El resultado esperado es aproximadamente {r_total:.1f} dB; combina τ ponderados por superficie."),s);solutions["s7q11"]=s
    score_counter(7)
    teacher_group_review(7,solutions)


def _legacy_stage10():
    header("ETAPA 10 · EVALUACIÓN FINAL","Evaluación práctica final · Aislamiento a Ruido Aéreo",
           "30 preguntas: 29 teórico-aplicadas y un caso integrador con costo-beneficio.")
    full_matter(10)
    if "exam_answers" not in st.session_state: st.session_state.exam_answers={}
    tab1,tab2=st.tabs(["Preguntas 1 a 29","Pregunta 30 · Caso práctico"])
    with tab1:
        qn=st.selectbox("Pregunta",range(29),format_func=lambda i:f"Pregunta {i+1}")
        q,opts,correct=QUESTIONS[qn]
        st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA {qn+1} DE 29</div><div class="question-text">{q}</div></div>',unsafe_allow_html=True)
        ans=st.radio("Selecciona una alternativa",opts,index=None,key=f"q{qn}",label_visibility="collapsed")
        if st.button("Guardar respuesta",key=f"save{qn}"):
            if ans is None: st.warning("Selecciona una alternativa.")
            else: st.session_state.exam_answers[qn]=opts.index(ans);st.success("Respuesta guardada.")
        st.progress(len(st.session_state.exam_answers)/29)
    with tab2:
        st.markdown('<div class="question-box"><div class="question-label">PREGUNTA 30 · CASO PROFESIONAL INTEGRADOR</div><div class="question-text">¿Qué solución recomendarías para proteger un dormitorio contiguo a una sala de máquinas?</div><p>La fuente domina en 125, 250 y 500 Hz. Calcula, compara y justifica tu decisión técnico-económica.</p></div>',unsafe_allow_html=True)
        df=pd.DataFrame({
          "Indicador":["Rw","Cₜᵣ","Rw+Cₜᵣ","R en 125 Hz","R en 250 Hz","R en 500 Hz","Costo instalado","Vida útil"],
          "Solución A":["52 dB","−9 dB","43 dB","27 dB","34 dB","47 dB","$1.800.000","20 años"],
          "Solución B":["49 dB","−4 dB","45 dB","34 dB","39 dB","45 dB","$2.100.000","25 años"]})
        st.dataframe(df,hide_index=True,use_container_width=True)
        c1,c2=st.columns(2)
        V=c1.number_input("V (m³)",1.,500.,50.,key="case_V")
        A=c2.number_input("A (m² sabin)",1.,200.,20.,key="case_A")
        calc=st.number_input("Calcula T₆₀ (s)",0.,10.,0.,.01,key="case_calc")
        diff=st.number_input("Diferencia de costo ($)",0,5000000,0,step=50000,key="case_diff")
        pct=st.number_input("Incremento porcentual de B respecto de A (%)",0.,200.,0.,.1,key="case_pct")
        bands=st.multiselect("Bandas críticas",[125,250,500,1000],key="case_bands")
        choice=st.radio("Recomendación",["Solución A","Solución B"],index=None,key="case_choice")
        justification=st.text_area("Justificación técnico-económica",key="case_justification")
        if st.button("Finalizar y corregir evaluación",type="primary"):
            theory=sum(st.session_state.exam_answers.get(i)==QUESTIONS[i][2] for i in range(29))
            practical=0
            practical+=3 if abs(calc-.4025)<=.03 else 0
            practical+=2 if set(bands)=={125,250,500} else 0
            practical+=3 if choice=="Solución B" else 0
            practical+=2 if abs(diff-300000)<=10000 else 0
            practical+=2 if abs(pct-16.7)<=.5 else 0
            words=justification.lower()
            practical+=4 if all(k in words for k in ["costo","125"]) else 2 if justification.strip() else 0
            practical+=4 if any(k in words for k in ["vida útil","cumple","objetivo","grave","250"]) else 0
            total=theory/29*80+practical
            st.session_state.exam_result=(theory,practical,total)
            level="Correcta" if total>=60 else "Incorrecta"
            _save_formative(
                10,"final_exam","Evaluación final del Curso 1",
                json.dumps(
                    {"respuestas_teoricas":st.session_state.exam_answers,
                     "aciertos_teoricos":theory,"puntaje_caso":practical},
                    ensure_ascii=False,
                ),
                level,
                f"Teoría: {theory}/29 aciertos. Caso práctico: {practical}/20 puntos.",
                score=total,max_score=100,
                correct_answer=(
                    "Pauta: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; "
                    "bandas 125, 250 y 500 Hz; Solución B por mejor respuesta grave, "
                    "mejor Rw+Cₜᵣ y mayor vida útil."
                ),
            )
    if "exam_result" in st.session_state:
        theory,practical,total=st.session_state.exam_result
        st.markdown(f'<div class="good"><b>Resultado: {total:.1f}/100</b><br>Teoría: {theory}/29 aciertos, ponderados a 80 puntos. Caso práctico: {practical}/20 puntos.<br>{"APROBADO" if total>=60 else "REQUIERE REFORZAMIENTO"}</div>',unsafe_allow_html=True)
        st.info("Respuesta esperada: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; bandas 125, 250 y 500 Hz; Solución B por mejor respuesta grave, mejor Rw+Cₜᵣ y mayor vida útil. Si ambas cumplieran holgadamente la meta, A podría ser suficiente.")
    score_counter(10)
    teacher_group_review(
        10,
        {"final_exam":"La evaluación suma 80 puntos teóricos y 20 puntos del caso integrador. "
         "La aprobación interna se alcanza con 60/100; el docente puede revisar y ajustar el puntaje con fundamento."},
    )


def _legacy_v1_legacy_v1_lab2_heading(stage, title, purpose):
    header(
        f"ETAPA {stage} · LABORATORIO 2",
        title,
        purpose,
        show_overview=False,
        duration_minutes=LEGACY_V1_LAB2_MINUTES[stage],
    )


def _legacy_v1_lab2_stage0():
    _legacy_v1_lab2_heading(0, "Ruta profesional de cuatro horas",
                  "Del requerimiento acústico a una recomendación verificable, construible y defendible.")
    st.markdown(r"""
    ### Resultado de aprendizaje
    Al finalizar podrás transformar un requerimiento CES/MINVU en una solución de separación interior,
    distinguir el descriptor correcto, estimar el desempeño instalado y controlar los puntos débiles.
    """)
    st.dataframe(pd.DataFrame([
        ["00:00–00:15","Apertura, objetivos y antecedentes del encargo"],
        ["00:15–00:35","Requerimientos CES usados en la asesoría MINVU"],
        ["00:35–01:00","Rw, C, Ctr, R′w, DnT,w y DnT,A"],
        ["01:00–01:35","Modelos: placa simple, coincidencia, Sharp y masa–aire–masa"],
        ["01:35–02:10","Cinco problemas numéricos resueltos"],
        ["02:10–02:20","Pausa"],
        ["02:20–02:45","Aplicación didáctica de ISO 12354"],
        ["02:45–03:20","Caso guiado: Sala de Reuniones Dirección"],
        ["03:20–03:40","TA-01 y comparación de tres soluciones"],
        ["03:40–04:00","Puertas, aislamiento compuesto y preparación de evaluación"],
    ], columns=["Minutos","Actividad"]), hide_index=True, use_container_width=True)
    st.info("La evaluación individual de la Sala de Reuniones Licitaciones se abre únicamente cuando el docente la publica.")


def _legacy_v1_lab2_stage1():
    _legacy_v1_lab2_heading(1, "Del requerimiento CES al criterio de diseño",
                  "Separar exigencia, descriptor, recinto, condición de ensayo y margen de proyecto.")
    st.markdown(r"""
    ### Lectura correcta del encargo

    1. Identifica el par de recintos y el elemento separador.
    2. Confirma si el valor corresponde a laboratorio, edificio terminado o diferencia entre recintos.
    3. Conserva el descriptor escrito en el requerimiento: no reemplaces automáticamente \(D_{nT,A}\) por \(R_w\).
    4. Registra el espectro relevante: voz, tránsito, instalaciones u otra fuente.
    5. Define un margen de diseño y las pérdidas previsibles de obra.

    **Regla profesional:** una solución no cumple porque su ficha tenga un \(R_w\) mayor que la meta.
    Debe existir una cadena de cálculo que conecte el elemento ensayado con la condición instalada.
    """)
    st.warning("Los valores del caso MINVU se usan como antecedentes de una asesoría específica. No deben presentarse como exigencias universales para todo edificio.")


def _legacy_v1_lab2_stage2():
    _legacy_v1_lab2_heading(2, "Descriptores sin confusiones",
                  "Elegir el indicador que responde a la pregunta técnica real.")
    st.dataframe(pd.DataFrame([
        ["R(f)","Laboratorio, por banda","Reducción sonora del elemento ensayado"],
        ["Rw","Laboratorio, índice único","Valor ponderado ISO 717-1 del elemento"],
        ["C / Ctr","Adaptación espectral","Corrección según familia de espectro; Ctr penaliza más el contenido grave de tránsito"],
        ["R′w","Edificio terminado","Reducción aparente; incorpora montaje y transmisiones laterales"],
        ["DnT,w","Entre recintos","Diferencia de niveles normalizada al tiempo de reverberación"],
        ["DnT,A","Entre recintos, ponderación A","Valor asociado al espectro normalizado que exige el encargo"],
    ], columns=["Descriptor","Ámbito","Qué representa"]), hide_index=True, use_container_width=True)
    st.latex(r"D_{nT}=L_1-L_2+10\log_{10}\left(\frac{T}{T_0}\right),\qquad T_0=0.5\ \mathrm{s}")
    st.markdown(r"**No existe una conversión universal fija** entre \(R_w\), \(R'_w\) y \(D_{nT,w}\). La geometría, absorción, montaje y flancos cambian el resultado.")


def _legacy_v1_lab2_stage3():
    _legacy_v1_lab2_heading(3, "Modelos de predicción de la tesis",
                  "Reconocer el alcance y las limitaciones de cada modelo antes de calcular.")
    st.dataframe(pd.DataFrame([
        ["Ley de masa","Placa simple, zona controlada por masa",r"R≈20 log10(m·f)−47","No representa resonancia ni coincidencia"],
        ["Coincidencia","Placas delgadas",r"fc depende de masa, rigidez y espesor","Produce una pérdida localizada de aislamiento"],
        ["Sharp","Placas simples reales","Ajuste por regiones alrededor de fc","Útil como modelo semiempírico, no sustituye un ensayo"],
        ["Masa–aire–masa","Sistemas dobles","Dos hojas + cámara + absorbente","La resonancia puede degradar bajas frecuencias"],
    ], columns=["Modelo","Uso","Idea de cálculo","Advertencia"]), hide_index=True, use_container_width=True)
    m=st.slider("Masa superficial de la placa (kg/m²)",5,80,25,key="lab2_model_m")
    f=st.select_slider("Frecuencia (Hz)",options=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150],value=500,key="lab2_model_f")
    st.metric("Predicción ideal por ley de masa",f"{float(mass_r(m,f)):.1f} dB")
    st.caption("Es una referencia ideal por banda; no es Rw ni desempeño garantizado en obra.")


def _legacy_v1_lab2_stage4():
    _legacy_v1_lab2_heading(4, "Cinco problemas numéricos resueltos",
                  "Seguir datos, fórmula, sustitución, unidad e interpretación.")
    problems=[
        ("1 · Ley de masa","m=25 kg/m²; f=500 Hz",r"R=20\log_{10}(25·500)-47=34.9\ \mathrm{dB}","Predicción ideal por banda, no Rw."),
        ("2 · Término espectral","Rw=52 dB; C=−3 dB",r"R_w+C=52-3=49\ \mathrm{dB}","La adaptación espectral reduce el valor útil para ese espectro."),
        ("3 · Diferencia normalizada","L1=85 dB; L2=48 dB; T=0.8 s",r"D_{nT}=85-48+10\log_{10}(0.8/0.5)=39.0\ \mathrm{dB}","Normalizar permite comparar recintos con distinta reverberación."),
        ("4 · Elemento compuesto","Muro 8.11 m² a 49 dB; puerta 1.89 m² a 31 dB",r"R_{comp}=-10\log_{10}\frac{8.11·10^{-4.9}+1.89·10^{-3.1}}{10}=38.1\ \mathrm{dB}","La puerta domina pese a ocupar menos área."),
        ("5 · Paso a desempeño estimado","Rcomp,A=38.1 dB; Kgeo=3.2 dB; obra=3 dB",r"D_{nT,A}\approx38.1+3.2-3.0=38.3\ \mathrm{dB}","El margen debe verificarse, no suponerse."),
    ]
    for title,data,development,meaning in problems:
        with st.expander(title, expanded=title.startswith("1")):
            st.write(f"**Datos:** {data}")
            st.latex(development)
            st.write(f"**Interpretación:** {meaning}")
    check("lab2_p4","¿Qué componente suele controlar una separación compuesta?",["El de mayor área","El de menor aislamiento ponderado por su área","El más caro"],"El de menor aislamiento ponderado por su área","La combinación debe hacerse energéticamente; los dB no se promedian.")


def _legacy_v1_lab2_stage5():
    _legacy_v1_lab2_heading(5, "ISO 12354 como puente de diseño",
                  "Pasar del dato del elemento al comportamiento esperado del edificio.")
    st.markdown(r"""
    ### Secuencia didáctica simplificada

    **1. Entrada:** curva o índice del elemento ensayado.  
    **2. Geometría:** área separadora, volumen receptor y absorción/tiempo de reverberación.  
    **3. Caminos:** transmisión directa más contribuciones laterales.  
    **4. Resultado:** aislamiento aparente o diferencia normalizada, según la magnitud requerida.  
    **5. Verificación:** comparar con la meta, margen y condiciones reales de ejecución.

    La aplicación usa una aproximación pedagógica para seguir la cadena de decisiones.
    No debe etiquetarse como cálculo normativo completo cuando no se modelan todas las uniones y vías laterales.
    """)
    st.latex(r"R'=-10\log_{10}\left(\tau_d+\sum \tau_{flanco}\right)")
    st.info("La contribución total se suma en energía. Una vía lateral débil puede limitar el desempeño aunque el tabique directo sea excelente.")


def _legacy_v1_lab2_stage6():
    _legacy_v1_lab2_heading(6, "Ejercicio guiado · Sala de Reuniones Dirección",
                  "Resolver el caso junto al docente y documentar cada decisión.")
    st.image(str(ROOT/"assets/course_visuals/stage6_double_wall.webp"),use_container_width=True)
    st.markdown(r"""
    ### Ficha de trabajo

    - Delimita emisor, receptor y separación.
    - Calcula volumen receptor, superficie total, puerta y paño opaco.
    - Selecciona el descriptor exigido.
    - Compara el valor de laboratorio con la estimación instalada.
    - Declara margen, pérdida de obra y controles de constructibilidad.
    """)
    cad_viewer_button(6)
    response=st.text_area("Conclusión guiada del equipo",key="lab2_direccion_conclusion",
                          placeholder="Descriptor, solución, resultado, margen, punto débil y controles de obra.")
    if st.button("Guardar conclusión guiada",key="lab2_save_direccion"):
        if len(response.strip())<40:
            st.warning("Desarrolla una conclusión técnica más completa.")
        else:
            _save_formative(6,"direccion_guiada","Caso guiado · Sala de Reuniones Dirección",
                            response,"Correcta","Conclusión enviada para revisión docente.",score=10,max_score=10)
            st.success("Conclusión guardada.")
    score_counter(6)


def _legacy_v1_lab2_stage7():
    _legacy_v1_lab2_heading(7, "Comparación de tres soluciones",
                  "Contrastar la TA-01 original con alternativas técnicamente viables.")
    st.dataframe(pd.DataFrame([
        ["Solución 1","TA-01 original",60,-4,56,140,92000],
        ["Solución 2","Tabique reforzado desacoplado",52,-3,49,140,68000],
        ["Solución 3","Tabique básico mejorado",47,-2,45,100,45000],
    ],columns=["Alternativa","Sistema","Rw","C","Rw+C","Espesor (mm)","Costo ($/m²)"]),
        hide_index=True,use_container_width=True)
    choice=st.radio("¿Qué solución debe recomendarse?",[
        "Siempre TA-01 porque tiene el Rw más alto",
        "La de menor costo que cumpla con margen después de considerar puerta y obra",
        "Siempre la alternativa más barata",
    ],index=None,key="lab2_solution_choice")
    reason=st.text_area("Justificación",key="lab2_solution_reason")
    if st.button("Enviar comparación",key="lab2_solution_submit"):
        correct=choice=="La de menor costo que cumpla con margen después de considerar puerta y obra"
        score=(6 if correct else 0)+(4 if len(reason.strip())>=50 else 2 if reason.strip() else 0)
        _save_formative(7,"compare_solutions","Comparación TA-01 y alternativas",
                        json.dumps({"seleccion":choice,"justificacion":reason},ensure_ascii=False),
                        "Correcta" if score>=6 else "Parcialmente correcta",
                        "La selección final depende del sistema compuesto, margen y constructibilidad.",score=score,max_score=10)
        st.success(f"Respuesta guardada: {score}/10 puntos.")
    score_counter(7)


def _legacy_v1_lab2_stage8():
    _legacy_v1_lab2_heading(8, "Aislamiento compuesto y efecto de puertas",
                  "Comprobar por qué una abertura pequeña puede controlar el resultado.")
    wall_area=8.11
    door_area=1.89
    rw_wall=st.slider("Rw+C del paño opaco (dB)",35,60,49,key="lab2_wall_rating")
    rw_door=st.slider("Rw+C de la puerta (dB)",15,45,31,key="lab2_door_rating")
    result=compound_r([wall_area,door_area],[rw_wall,rw_door])
    st.metric("Aislamiento compuesto estimado",f"{result:.1f} dB")
    st.caption(f"Paño opaco: {wall_area:.2f} m² · Puerta: {door_area:.2f} m².")
    st.latex(r"R_{comp}=-10\log_{10}\left(\frac{\sum S_i10^{-R_i/10}}{\sum S_i}\right)")
    answer=st.text_area("¿Qué especificación constructiva agregarías a la puerta?",key="lab2_door_control")
    if st.button("Guardar análisis de puerta",key="lab2_door_submit"):
        hits=sum(k in answer.lower() for k in ["sello","marco","inferior","burlete","umbral"])
        score=10 if hits>=3 else 6 if hits>=1 else 2
        _save_formative(8,"compound_door","Aislamiento compuesto y puerta",answer,
                        "Correcta" if score>=6 else "Parcialmente correcta",
                        f"Resultado compuesto calculado: {result:.1f} dB.",score=score,max_score=10)
        st.success(f"Análisis guardado: {score}/10 puntos.")
    score_counter(8)


def _legacy_v1_lab2_stage9():
    _legacy_v1_lab2_heading(9, "Preparación de la evaluación individual",
                  "Practicar el método sin revelar el caso evaluado.")
    st.markdown("""
    ### Lista de comprobación

    - Descriptor y meta correctamente identificados.
    - Geometría y áreas netas calculadas.
    - Conversión energética de muro y puerta.
    - Paso justificado desde laboratorio a estimación instalada.
    - Comparación de alternativas con margen.
    - Controles de obra verificables.
    - Conclusión breve con resultado, costo, riesgo y recomendación.
    """)
    with st.expander("Banco de práctica"):
        st.markdown(r"""
        1. ¿Por qué \(R_w\) no debe compararse directamente con \(D_{nT,A}\)?  
        2. ¿Qué cambia al reemplazar una puerta hueca por una puerta sellada?  
        3. ¿Cuándo usarías \(C\) y cuándo \(C_{tr}\)?  
        4. ¿Qué representa una pérdida de obra?  
        5. ¿Por qué una solución de mayor \(R_w\) puede no ser la recomendación óptima?
        """)
    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Guion docente y fichas"):
            st.markdown("""
            **Guion de 30 diapositivas:** apertura (1–3), encargo CES/MINVU (4–7),
            descriptores (8–12), modelos de tesis (13–17), problemas resueltos (18–22),
            ISO 12354 (23–25), caso Dirección y alternativas (26–28), evaluación y cierre (29–30).

            **Fichas:** requerimiento; geometría; componentes; comparación; control de obra;
            conclusión profesional. Las soluciones y la evaluación futura permanecen protegidas.
            """)


def _legacy_v1_lab2_stage10():
    _legacy_v1_lab2_heading(10, "Evaluación individual · Sala de Reuniones Licitaciones",
                  "Resolver un caso equivalente con intento único y rúbrica analítica de 100 puntos.")
    cad_viewer_button(10)
    stage10()


def _legacy_v2_lab2_stage3():
    _lab2_heading(
        3,
        "Ejercicio aplicado: TL de una placa simple de yeso-cartón",
        "Construir la predicción continua desde las propiedades del material hasta el TL de campo.",
    )
    st.markdown("""
    ### Situación profesional
    Se proyecta una **placa homogénea simple de yeso-cartón** para separar un recinto
    emisor de uno receptor. Antes de utilizar índices globales o datos por bandas, se
    desea predecir cómo cambia su pérdida por transmisión entre **50 y 5.000 Hz**.

    En este primer ejercicio no se aplicará la ley de masa aproximada ni una corrección
    dibujada para la coincidencia. La curva se obtendrá directamente con la ecuación
    angular de placa simple y su integración de campo.
    """)
    _lab2_image(
        "yeso_carton",
        "Placa simple: una hoja homogénea, sin cámara ni segunda placa independiente.",
    )

    st.markdown("### Ruta del ejercicio")
    st.markdown("""
    1. Ingresar las propiedades del yeso-cartón.
    2. Calcular masa superficial, rigidez de flexión y frecuencia crítica.
    3. Calcular el coeficiente de transmisión de cada ángulo.
    4. Integrar energéticamente todas las incidencias entre 0° y 78°.
    5. Transformar el coeficiente de campo en TL y analizar la curva continua.
    """)
    st.info(
        "**Idea clave:** 78° no es un único rayo. Es el límite superior del campo "
        "angular utilizado para integrar todas las incidencias desde 0° hasta 78°."
    )

    st.markdown("### Paso 1 · Propiedades de la placa")
    st.caption(
        "Los valores iniciales son referencias didácticas para una placa de yeso-cartón. "
        "Puedes modificarlos para observar qué propiedad cambia la predicción."
    )
    p1,p2,p3=st.columns(3)
    rho=p1.number_input(
        "Densidad ρ (kg/m³)", min_value=300.0, max_value=3000.0,
        value=800.0, step=10.0, key="lab2_s3_rho",
        help="Masa contenida en un metro cúbico del material.")
    h_mm=p2.number_input(
        "Espesor h (mm)", min_value=4.0, max_value=50.0,
        value=12.5, step=0.5, key="lab2_s3_h",
        help="El cálculo convierte automáticamente milímetros a metros.")
    young_gpa=p3.number_input(
        "Módulo de Young E (GPa)", min_value=0.1, max_value=100.0,
        value=2.5, step=0.1, key="lab2_s3_e",
        help="Representa la resistencia elástica del material a deformarse.")
    p4,p5,p6=st.columns(3)
    poisson=p4.number_input(
        "Coeficiente de Poisson ν", min_value=0.05, max_value=0.49,
        value=0.30, step=0.01, format="%.2f", key="lab2_s3_nu",
        help="Relaciona la deformación transversal con la longitudinal.")
    eta=p5.number_input(
        "Factor de pérdidas η", min_value=0.001, max_value=0.200,
        value=0.030, step=0.001, format="%.3f", key="lab2_s3_eta",
        help="Representa el amortiguamiento interno de la placa.")
    selected_frequency=p6.number_input(
        "Frecuencia a inspeccionar (Hz)", min_value=50, max_value=5000,
        value=1000, step=50, key="lab2_s3_selected_frequency")

    st.markdown(
        '<div class="lesson"><b>Traducción para no ingenieros:</b> ρ y h determinan '
        "cuánta masa existe en cada metro cuadrado; E, h y ν determinan cuánto se "
        "resiste la placa a curvarse; η indica cuánta vibración interna logra disipar.</div>",
        unsafe_allow_html=True,
    )

    h=h_mm/1000
    surface_mass=rho*h
    stiffness=young_gpa*1e9*h**3/(12*(1-poisson**2))
    critical_frequency=343.0**2/(2*math.pi)*math.sqrt(surface_mass/stiffness)

    st.markdown("### Paso 2 · Magnitudes calculadas")
    st.latex(r"m'=\rho h")
    st.latex(r"B=\frac{Eh^3}{12(1-\nu^2)}")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{B}}")
    r1,r2,r3=st.columns(3)
    r1.metric("Masa superficial m′",f"{surface_mass:.2f} kg/m²")
    r2.metric("Rigidez de flexión B",f"{stiffness:.2f} N·m")
    r3.metric("Frecuencia crítica fᶜ",f"{critical_frequency:.0f} Hz")
    if 50 <= critical_frequency <= 5000:
        st.warning(
            f"La frecuencia crítica calculada ({critical_frequency:.0f} Hz) está dentro "
            "del intervalo analizado. Revisa la curva cerca de ese valor: allí puede "
            "aumentar la transmisión por coincidencia."
        )
    else:
        st.success(
            f"La frecuencia crítica calculada ({critical_frequency:.0f} Hz) queda fuera "
            "del intervalo de 50 a 5.000 Hz."
        )

    st.markdown("### Paso 3 · De un ángulo al coeficiente de transmisión")
    st.markdown(r"""
    Para una misma frecuencia, el sonido puede alcanzar la placa desde muchas direcciones.
    La tesis calcula primero un coeficiente \(\tau(\theta,f)\) para cada dirección.
    \(\tau=1\) significa transmisión total y un valor próximo a cero significa que pasa
    una fracción muy pequeña de la energía incidente.
    """)
    st.latex(
        r"\tau(\theta,f)=\left\{\left[1+\eta"
        r"\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)"
        r"\left(\frac{\omega^2B\sin^4\theta}{c^4m'}\right)\right]^2+"
        r"\left[\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)"
        r"\left(1-\frac{\omega^2B\sin^4\theta}{c^4m'}\right)\right]^2"
        r"\right\}^{-1}"
    )
    st.caption(
        "ω = 2πf; θ se mide respecto de la normal; ρ₀ = 1,21 kg/m³; c = 343 m/s."
    )

    selected_f=float(selected_frequency)
    tau_field_one,tl_field_one,angles,tau_angular,normalizer=(
        _panel_simple_field_tl(
            np.array([selected_f]),surface_mass,stiffness,eta
        )
    )
    tau_selected=tau_angular[0]
    angles_deg=np.degrees(angles)
    angular_fig=go.Figure()
    angular_fig.add_trace(go.Scatter(
        x=angles_deg,y=100*tau_selected,mode="lines",
        line=dict(color="#08a6c9",width=4),
        name=f"{selected_frequency} Hz"))
    angular_fig.add_vline(x=78,line_dash="dash",line_color="#ef8b2c")
    angular_fig.update_layout(
        title=f"Transmisión angular a {selected_frequency} Hz",
        xaxis_title="Ángulo respecto de la normal (°)",
        yaxis_title="Energía transmitida (%)",
        xaxis=dict(range=[0,90]),
        height=390,margin=dict(l=35,r=20,t=60,b=40),
        hovermode="x unified")
    st.plotly_chart(
        angular_fig,use_container_width=True,key="lab2_s3_angular_curve")
    st.markdown(
        '<div class="lesson"><b>Cómo leer este gráfico:</b> cada punto corresponde a '
        "una dirección de llegada distinta, no a una frecuencia distinta. La línea se "
        "detiene en 78° porque esa es la última incidencia incorporada al campo de "
        "laboratorio.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Paso 4 · Construcción del campo hasta 78°")
    st.latex(
        r"\overline{\tau}_{campo}(f)=2{,}0904"
        r"\int_0^{78^\circ}\tau(\theta,f)\cos\theta\sin\theta\,d\theta"
    )
    st.latex(
        r"TL_{campo}(f)=-10\log_{10}\left[\overline{\tau}_{campo}(f)\right]"
    )
    st.markdown(r"""
    El factor \(2{,}0904\) normaliza la ponderación angular limitada a 78°. Primero se
    suman las fracciones de energía transmitida, considerando el peso correspondiente a
    cada dirección. **Solo después** ese promedio se convierte a decibeles. Promediar
    directamente los valores de TL sería incorrecto.
    """)
    f1,f2,f3=st.columns(3)
    f1.metric(
        f"τ̄ de campo a {selected_frequency} Hz",
        f"{float(tau_field_one[0]):.6f}")
    f2.metric(
        "Energía transmitida",
        f"{100*float(tau_field_one[0]):.4f} %")
    f3.metric(
        "TL de campo",
        f"{float(tl_field_one[0]):.1f} dB")

    st.markdown("### Paso 5 · Curva continua de TL en frecuencia lineal")
    frequencies=np.arange(50.0,5000.0+1,10.0)
    tau_field,tl_field,_,_,_= _panel_simple_field_tl(
        frequencies,surface_mass,stiffness,eta)
    selected_index=int(np.argmin(np.abs(frequencies-selected_f)))
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl_field,mode="lines",
        name="TL de campo · 0° a 78°",
        line=dict(color="#0967d2",width=4)))
    if 50 <= critical_frequency <= 5000:
        fig.add_vline(
            x=critical_frequency,line_dash="dash",line_color="#ef8b2c",
            annotation_text="fᶜ",annotation_position="top")
    fig.add_trace(go.Scatter(
        x=[frequencies[selected_index]],y=[tl_field[selected_index]],
        mode="markers",name=f"{int(frequencies[selected_index])} Hz",
        marker=dict(size=12,color="#ef8b2c")))
    fig.update_layout(
        title="Pérdida por transmisión de campo · placa simple de yeso-cartón",
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500),
        height=470,hovermode="x unified",
        margin=dict(l=40,r=20,t=65,b=45),
        legend=dict(orientation="h",y=1.12))
    st.plotly_chart(fig,use_container_width=True,key="lab2_s3_tl_linear")
    st.caption(
        "Curva predictiva continua del modelo teórico. No corresponde a un ensayo "
        "normalizado ni incorpora dimensiones finitas, apoyos, juntas, fugas o flancos."
    )

    st.markdown("### Paso 6 · Lectura de resultados")
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    sample_tau,sample_tl,_,_,_=_panel_simple_field_tl(
        sample_frequencies,surface_mass,stiffness,eta)
    results=pd.DataFrame({
        "Frecuencia (Hz)":sample_frequencies.astype(int),
        "τ̄ campo":sample_tau,
        "Energía transmitida (%)":100*sample_tau,
        "TL campo (dB)":sample_tl,
    })
    st.dataframe(
        results.style.format({
            "τ̄ campo":"{:.6f}",
            "Energía transmitida (%)":"{:.4f}",
            "TL campo (dB)":"{:.1f}",
        }),
        use_container_width=True,hide_index=True)
    min_index=int(np.argmin(tl_field))
    max_transmission_index=int(np.argmax(tau_field))
    a,b,c=st.columns(3)
    a.metric(
        "Menor TL calculado",
        f"{tl_field[min_index]:.1f} dB",
        f"a {frequencies[min_index]:.0f} Hz")
    b.metric(
        "Mayor transmisión",
        f"{100*tau_field[max_transmission_index]:.3f} %",
        f"a {frequencies[max_transmission_index]:.0f} Hz")
    c.metric(
        "TL a 1.000 Hz",
        f"{sample_tl[3]:.1f} dB")

    st.markdown("### Paso 7 · Conclusión del alumno")
    st.markdown(r"""
    Responde utilizando los resultados obtenidos, no solamente una descripción general:

    - ¿La frecuencia crítica está dentro del intervalo analizado?
    - ¿Qué sucede con el TL cerca de \(f_c\)?
    - ¿En qué frecuencia de la tabla se transmite la mayor fracción de energía?
    - ¿Por qué \(TL\) no es constante para una misma placa?
    """)
    conclusion=st.text_area(
        "Redacta tu conclusión técnica",
        key="lab2_s3_conclusion",height=130,
        placeholder=(
            "Ejemplo de estructura: La placa posee m′ = ... kg/m² y fᶜ = ... Hz. "
            "La curva muestra que... La banda más desfavorable es..."))
    if st.button("Comprobar mi análisis",key="lab2_s3_check_conclusion"):
        if len(conclusion.strip()) < 80:
            st.warning(
                "Desarrolla un poco más la respuesta: incluye m′, fᶜ, una frecuencia "
                "desfavorable y la relación entre τ y TL.")
        else:
            st.success(
                "Tu análisis tiene una extensión suficiente. Contrástalo con los valores "
                "calculados y verifica que no confundas 78° con un único ángulo.")

    check(
        "lab2_s3_q1",
        "¿Qué representa el límite de 78° en este ejercicio?",
        [
            "El único ángulo con que se ensaya la placa",
            "El límite superior de la integración de múltiples incidencias",
            "La frecuencia crítica expresada en grados",
            "El ángulo de montaje del tabique",
        ],
        "El límite superior de la integración de múltiples incidencias",
        "El campo incorpora todos los ángulos entre 0° y 78° con ponderación energética.",
    )
    check(
        "lab2_s3_q2",
        "¿Cuál es el orden correcto para obtener el TL de campo?",
        [
            "Promediar los TL angulares y luego calcular τ",
            "Calcular τ angular, integrar τ y convertir el promedio a TL",
            "Calcular solamente τ a 78°",
            "Promediar las frecuencias y aplicar la ley de masa",
        ],
        "Calcular τ angular, integrar τ y convertir el promedio a TL",
        "Los decibeles no se promedian directamente: primero se integra la energía transmitida.",
    )


def _legacy_v2_lab2_stage6():
    _lab2_heading(6, "Comparación aplicada y cierre parcial",
                  "Contrastar un panel pesado con un tabique liviano de doble estructura.")
    concrete=_simple_real_curve(240,180,5)
    double,f0,fl=_sharp_curve(20,20,140,"Independiente")
    left,right=st.columns(2)
    with left:
        st.markdown("#### Panel pesado")
        _lab2_image("comparador_hormigon")
        st.caption("Hormigón 100 mm · una hoja · m′≈240 kg/m²")
    with right:
        st.markdown("#### Tabique liviano doble")
        _lab2_image("comparador_tabique")
        st.caption("Dos hojas · cámara 140 mm · bastidores independientes")
    _plot_curves([
        ("Hormigón 100 mm",concrete,"solid"),
        ("Tabique doble liviano",double,"dash"),
    ],"Dos estrategias distintas de aislamiento",[(f0,"f₀ doble"),(fl,"fₗ doble")])
    st.success("""
    **Conclusión:** más masa no garantiza superioridad en todas las bandas. Un sistema
    liviano correctamente desacoplado puede alcanzar una pendiente mayor sobre su
    resonancia; el panel pesado suele ser robusto en bajas frecuencias. La decisión exige
    comparar curvas, espectro, espesor, peso, encuentros, costo y calidad de ejecución.
    """)
    st.markdown("### Puente hacia la segunda mitad")
    st.write("En el siguiente bloque se desarrollarán ventanas dobles, bandas de octava y tercio de octava, y los números únicos Rw, C y Ctr.")


