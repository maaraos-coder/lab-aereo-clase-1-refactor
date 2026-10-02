"""Curso 4 · Laboratorio 1: simuladores formativos de ruido de construcción."""

import math
import streamlit as st

CLASS_ID = "clase-07-construccion-lab-1"


def energetic(levels):
    return 10 * math.log10(sum(10 ** (level / 10) for level in levels))


def pressure(power, distance, q=2, attenuation=0):
    return power + 10 * math.log10(q / (4 * math.pi * distance ** 2)) - attenuation


def power_from_pressure(level, distance, q=2, attenuation=0):
    return level + 10 * math.log10(4 * math.pi * distance ** 2 / q) + attenuation


TITLES = [
    "Ruta de la obra", "Fases, fuentes y receptores", "Inventario de equipos",
    "Presión y potencia sonora", "Propagación exterior completa · Agr, Abar y Cmet", "Suma de fuentes",
    "Ciclos de trabajo", "Barreras temporales", "Escenario de obra",
    "Comprobación formativa", "Caso integrador formativo",
]

QUESTIONS = [
    ("¿Qué dato caracteriza la emisión de una máquina con independencia de la distancia?", ["Lp en un receptor", "Lw de la fuente", "LAeq del barrio"], 1, "Lw describe la emisión; Lp cambia con la posición y el entorno."),
    ("Al duplicar la distancia a una fuente puntual ideal, el nivel baja aproximadamente…", ["3 dB", "6 dB", "10 dB"], 1, "La divergencia esférica ideal produce 20 log₁₀(2) ≈ 6 dB."),
    ("Dos máquinas idénticas de 80 dBA funcionando a la vez producen…", ["80 dBA", "83 dBA", "160 dBA"], 1, "Dos contribuciones iguales suman 10 log₁₀(2) ≈ 3 dB."),
    ("¿Qué se debe comprobar para estimar una barrera?", ["Solo su masa", "Línea de vista, huecos y rodeos laterales", "Solo el color"], 1, "La geometría y las vías de transmisión determinan su eficacia real."),
]


def render(lab, stage, saved, save):
    """La misma vista se reutiliza en alumno, docente, Zoom y apunte visual."""
    title = TITLES[stage]
    st.markdown(f"### Etapa {stage} · {title}")
    st.caption("Curso 4 · Laboratorio 1 · Actividad formativa sin nota")
    projection = st.session_state.get("projection_mode") or st.session_state.get("print_mode")
    key = f"c4l1_{stage}"

    if stage == 0:
        st.info("Explorarás una obra desde el inventario de máquinas hasta una predicción preliminar en una vivienda cercana. Cada cálculo mostrará sus supuestos.")
        st.markdown("**Ruta:** fases → Lw/Lp → propagación → simultaneidad → duración → barrera → decisión. Las etapas 9 y 10 también son formativas.")
    elif stage == 1:
        phase = st.selectbox("Fase de construcción", ["Excavación", "Estructura", "Terminaciones"], key=key+"phase")
        sources = {"Excavación": "excavadora, camiones y martillo", "Estructura": "bomba de hormigón, vibrador y camiones", "Terminaciones": "corte, perforación y transporte interno"}
        st.info(f"Fuentes a revisar: {sources[phase]}. Ubica el receptor sensible, la duración de cada operación y las máquinas simultáneas.")
        st.warning("El escenario crítico depende del receptor, la proximidad y los horarios; no se deduce solo del equipo con mayor Lw.")
    elif stage == 2:
        st.markdown("Registra por máquina la magnitud declarada, distancia de referencia, cantidad y porcentaje de funcionamiento. No ingreses Lp como si fuera Lw.")
        for name, level in [("Excavadora", 105), ("Camión", 101), ("Martillo", 110)]:
            with st.container(border=True):
                st.write(f"**{name}** · Lw de ejemplo: {level} dB(A)")
                st.number_input(f"Cantidad de {name.lower()}", 0, 10, 1, key=key+name)
        st.caption("Valores ilustrativos para aprender el método; sustituir por fichas trazables en un proyecto real.")
    elif stage == 3:
        st.latex(r"L_W=L_p+10\log_{10}(4\pi r^2/Q)+A")
        lp = st.number_input("Lp medido [dB(A)]", 30.0, 130.0, 78.0, key=key+"lp")
        r = st.number_input("Distancia [m]", 0.5, 500.0, 7.0, key=key+"r")
        q = st.selectbox("Directividad Q", [1, 2, 4], index=1, key=key+"q")
        a = st.number_input("Atenuación adicional conocida [dB]", 0.0, 30.0, 0.2, key=key+"a")
        st.metric("Lw estimado", f"{power_from_pressure(lp, r, q, a):.1f} dB(A)")
        st.caption("Campo ideal y fuente puntual. No aplicar esta inversión sin verificar reflexiones, fondo, directividad y condiciones de medida.")
    elif stage == 4:
        st.markdown("#### 1 · Ecuación general de propagación exterior")
        st.latex(r"L_p = L_W + D_c - A")
        st.latex(r"A = A_{div} + A_{atm} + A_{gr} + A_{bar} + A_{misc}")
        st.markdown(
            "La divergencia geométrica es solo una parte de la propagación. "
            "En esta etapa incorporamos explícitamente el **efecto de suelo** "
            "\\(A_{gr}\\), además de recordar dónde entran la atmósfera y las barreras."
        )

        st.markdown("#### 2 · ¿De dónde sale G en el efecto de suelo?")
        st.markdown(
            "En ISO 9613-2 el efecto de suelo se representa mediante un **factor de suelo G**, "
            "que describe el comportamiento acústico de la superficie. **G no es una atenuación "
            "en dB**: es un parámetro adimensional que entra en el cálculo de \\(A_{gr}\\)."
        )
        st.latex(r"A_{gr}=A_s+A_m+A_r")
        st.markdown(
            "- **\\(A_s\\)**: contribución de la región próxima a la fuente.\n"
            "- **\\(A_m\\)**: contribución de la región intermedia.\n"
            "- **\\(A_r\\)**: contribución de la región próxima al receptor.\n\n"
            "Cada contribución depende de la frecuencia, la geometría y del factor de suelo "
            "correspondiente a esa región."
        )

        left, right = st.columns([1, 1])
        with left:
            st.markdown(
                "**Interpretación de G**\n\n"
                "- **G = 0** → suelo acústicamente duro o reflectante: hormigón, pavimento o agua.\n"
                "- **G = 1** → suelo poroso: pasto, tierra o suelo forestal.\n"
                "- **0 < G < 1** → superficie mixta o equivalente."
            )
        with right:
            g = st.slider(
                "Factor de suelo G",
                0.0, 1.0, 0.5, 0.1,
                key=key+"g",
                help="Parámetro adimensional. No corresponde directamente a una corrección en dB."
            )
            if g == 0:
                st.info("G = 0: suelo duro. Predominan las reflexiones del terreno.")
            elif g == 1:
                st.success("G = 1: suelo poroso. El terreno presenta mayor interacción acústica.")
            else:
                st.info(f"G = {g:.1f}: condición intermedia o mixta.")

        st.warning(
            "Importante: G no se multiplica directamente por una cantidad de dB. "
            "El valor de G se utiliza dentro de las expresiones de ISO 9613-2 para obtener "
            "As, Am y Ar y, finalmente, Agr."
        )

        st.markdown("#### 3 · Antes de agregar suelo: efecto de la distancia")
        st.latex(r"L_p(r_2)=L_p(r_1)-20\log_{10}(r_2/r_1)")
        lp = st.slider("Nivel a 10 m [dB(A)]", 50, 110, 80, key=key+"lp")
        distances = [10, 20, 40, 80]
        st.line_chart(
            {
                "Distancia [m]": distances,
                "Nivel [dB(A)]": [lp - 20 * math.log10(d/10) for d in distances],
            },
            x="Distancia [m]",
            y="Nivel [dB(A)]",
        )
        st.caption(
            "Esta curva muestra únicamente divergencia geométrica para una fuente puntual ideal. "
            "El efecto de suelo Agr se calcula aparte mediante As + Am + Ar; no está incluido en esta curva."
        )
    elif stage == 5:
        a = st.slider("Equipo A en el receptor [dB(A)]", 40, 100, 78, key=key+"a")
        b = st.slider("Equipo B en el receptor [dB(A)]", 40, 100, 75, key=key+"b")
        c = st.slider("Equipo C en el receptor [dB(A)]", 40, 100, 70, key=key+"c")
        st.latex(r"L_{total}=10\log_{10}\left(\sum_i 10^{L_i/10}\right)")
        st.metric("Nivel simultáneo", f"{energetic([a,b,c]):.1f} dB(A)")
        st.caption("La suma representa funcionamiento simultáneo; no es el promedio de un periodo con máquinas intermitentes.")
    elif stage == 6:
        level = st.slider("Nivel durante la operación [dB(A)]", 40, 110, 85, key=key+"l")
        background = st.slider("Nivel cuando está detenida [dB(A)]", 30, 90, 55, key=key+"bg")
        duty = st.slider("Tiempo de operación en una hora [%]", 0, 100, 25, key=key+"duty")
        fraction = duty/100
        result = 10*math.log10(fraction*10**(level/10)+(1-fraction)*10**(background/10))
        st.metric("LAeq,1h estimado", f"{result:.1f} dB(A)")
        st.caption("Promedio energético de dos estados; no equivale a reducir linealmente el nivel según el porcentaje de uso.")
    elif stage == 7:
        incident = st.slider("Nivel sin barrera en receptor [dB(A)]", 40, 110, 79, key=key+"l")
        insertion = st.slider("Pérdida por inserción supuesta [dB]", 0, 20, 7, key=key+"il")
        st.metric("Nivel estimado con barrera", f"{incident-insertion:.1f} dB(A)")
        st.info("La pérdida por inserción debe justificarse por altura, ubicación, longitud, frecuencia y continuidad. Un valor supuesto no demuestra cumplimiento.")
    elif stage == 8:
        power = st.slider("Lw de la máquina [dB(A)]", 80, 125, 105, key=key+"lw")
        distance = st.slider("Distancia al receptor [m]", 2, 200, 25, key=key+"r")
        q = st.selectbox("Q del modelo", [1, 2, 4], index=1, key=key+"q")
        barrier = st.slider("Atenuación adicional [dB]", 0, 20, 0, key=key+"bar")
        st.metric("Lp preliminar en receptor", f"{pressure(power,distance,q,barrier):.1f} dB(A)")
        st.caption("Estimación de una sola fuente puntual. Para una obra real suma equipos, duraciones, reflexiones y condiciones del lugar.")
    elif stage == 9:
        _quiz(saved, save, stage, projection)
    elif stage == 10:
        st.markdown("**Caso:** excavadora Lw 105 dB(A) a 25 m y martillo Lw 110 dB(A) a 40 m; ambos en semiespacio (Q=2), simultáneos. Barrera con pérdida por inserción supuesta de 7 dB sobre ambas trayectorias.")
        a, b = pressure(105, 25), pressure(110, 40)
        total = energetic([a,b])
        left, right = st.columns(2)
        left.metric("Sin barrera", f"{total:.1f} dB(A)")
        right.metric("Con barrera supuesta", f"{total-7:.1f} dB(A)")
        st.caption("Supuestos ideales: fuentes puntuales, emisión estable y barrera idénticamente eficaz para ambas. El resultado no es una evaluación normativa.")
        answer = st.text_area("Conclusión técnica: datos faltantes, escenario crítico y cómo verificarías la medida", value=saved.get("c4l1_case", ""), key=key+"answer", height=130)
        if st.button("Guardar conclusión formativa", key=key+"save"):
            if len(answer.strip()) < 50:
                st.warning("Explica al menos los datos faltantes y la verificación en 50 caracteres.")
            else:
                saved["c4l1_case"] = answer
                saved[f"done_{stage}"] = True
                if not projection: save(CLASS_ID, saved)
                st.success("Conclusión guardada como actividad formativa, sin nota.")
        if st.session_state.get("role") == "Docente":
            with st.expander("Pauta docente"):
                st.write("Distinguir Lw/Lp; calcular cada trayectoria y suma energética; verificar geometría y eficacia real de la barrera; solicitar fichas, simultaneidad, duración, receptor y condiciones del entorno.")

    if 0 <= stage <= 8:
        if st.button("Marcar exploración formativa como completada", key=key+"done"):
            saved[f"done_{stage}"] = True
            if not projection: save(CLASS_ID, saved)
            st.success("Etapa registrada; no genera nota.")


def _quiz(saved, save, stage, projection):
    st.markdown("Comprueba conceptos antes del caso. Puedes corregir respuestas; no hay envío oficial ni calificación.")
    correct = 0
    for i, (prompt, options, expected, explanation) in enumerate(QUESTIONS):
        choice = st.radio(prompt, options, index=None, key=f"c4l1_q_{i}")
        if choice is not None:
            if options.index(choice) == expected: correct += 1
            st.caption(("✅ " if options.index(choice) == expected else "Revisa: ") + explanation)
    if st.button("Guardar comprobación formativa", key="c4l1_quiz_save"):
        if any(st.session_state.get(f"c4l1_q_{i}") is None for i in range(len(QUESTIONS))):
            st.warning("Responde las cuatro preguntas.")
        else:
            saved["c4l1_quiz_correct"] = correct
            saved[f"done_{stage}"] = True
            if not projection: save(CLASS_ID, saved)
            st.success(f"Comprobación guardada: {correct}/{len(QUESTIONS)}. Puedes volver a practicar.")
