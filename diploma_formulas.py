"""Formulario técnico escalable del Diplomado en Acústica."""

from __future__ import annotations

from html import escape
from typing import Any, Iterable


FORMULA_CATALOG: list[dict[str, Any]] = [
    {
        "id": "curso_1",
        "number": 1,
        "title": "Aislamiento acústico al ruido aéreo",
        "enabled": True,
        "themes": [
            {
                "title": "Acústica de recintos",
                "formulas": [
                    {
                        "title": "Absorción equivalente",
                        "latex": r"A=\sum_{i=1}^{n}\alpha_i S_i",
                        "variables": [
                            (r"A", "absorción equivalente", "m² sabin"),
                            (r"\alpha_i", "coeficiente de absorción de la superficie i", "—"),
                            (r"S_i", "superficie i", "m²"),
                        ],
                        "use": "Suma los aportes absorbentes de las superficies de un recinto.",
                    },
                    {
                        "title": "Tiempo de reverberación de Sabine",
                        "latex": r"T_{60}=0.161\,\frac{V}{A}",
                        "variables": [
                            (r"T_{60}", "tiempo de reverberación", "s"),
                            (r"V", "volumen del recinto", "m³"),
                            (r"A", "absorción equivalente", "m² sabin"),
                        ],
                        "use": "Estima la reverberación en condiciones compatibles con el modelo de Sabine.",
                    },
                ],
            },
            {
                "title": "Transmisión y aislamiento",
                "formulas": [
                    {
                        "title": "Coeficiente de transmisión sonora",
                        "latex": r"\tau=\frac{W_t}{W_i}=10^{-R/10}",
                        "variables": [
                            (r"\tau", "coeficiente de transmisión sonora", "—"),
                            (r"W_t", "potencia sonora transmitida", "W"),
                            (r"W_i", "potencia sonora incidente", "W"),
                            (r"R", "índice de reducción sonora", "dB"),
                        ],
                        "use": "Relaciona la fracción de energía transmitida con el aislamiento expresado en decibeles.",
                    },
                    {
                        "title": "Índice de reducción sonora",
                        "latex": r"R=10\log_{10}\!\left(\frac{1}{\tau}\right)=-10\log_{10}(\tau)",
                        "variables": [
                            (r"R", "índice de reducción sonora", "dB"),
                            (r"\tau", "coeficiente de transmisión sonora", "—"),
                        ],
                        "use": "Expresa logarítmicamente la relación entre energía incidente y transmitida.",
                    },
                    {
                        "title": "Cerramiento compuesto",
                        "latex": r"\tau_T=\frac{\sum_i S_i\tau_i}{\sum_i S_i}\qquad R_T=-10\log_{10}(\tau_T)",
                        "variables": [
                            (r"S_i", "superficie del componente i", "m²"),
                            (r"\tau_i", "coeficiente de transmisión del componente i", "—"),
                            (r"\tau_T", "coeficiente de transmisión total", "—"),
                            (r"R_T", "índice de reducción sonora del conjunto", "dB"),
                        ],
                        "use": "Combina energéticamente los componentes; los valores en dB no se promedian.",
                    },
                    {
                        "title": "Diferencia de nivel estandarizada",
                        "latex": r"D_{nT}=L_1-L_2+10\log_{10}\!\left(\frac{T}{T_0}\right)",
                        "variables": [
                            (r"D_{nT}", "diferencia de nivel estandarizada", "dB"),
                            (r"L_1", "nivel en recinto emisor", "dB"),
                            (r"L_2", "nivel en recinto receptor", "dB"),
                            (r"T", "tiempo de reverberación receptor", "s"),
                            (r"T_0", "tiempo de reverberación de referencia", "s"),
                        ],
                        "use": "Normaliza la diferencia de niveles respecto de la reverberación del recinto receptor.",
                    },
                ],
            },
            {
                "title": "Placas simples",
                "formulas": [
                    {
                        "title": "Masa superficial",
                        "latex": r"m'=\rho h",
                        "variables": [(r"m'", "masa superficial", "kg/m²"), (r"\rho", "densidad", "kg/m³"), (r"h", "espesor", "m")],
                        "use": "Relaciona densidad y espesor con la masa por unidad de superficie.",
                    },
                    {
                        "title": "Ley de masa",
                        "latex": r"R\approx20\log_{10}(m'f)-47",
                        "variables": [(r"R", "índice de reducción sonora aproximado", "dB"), (r"m'", "masa superficial", "kg/m²"), (r"f", "frecuencia", "Hz")],
                        "use": "Describe la tendencia ideal de una placa simple en la región controlada por masa.",
                    },
                    {
                        "title": "Rigidez flexional",
                        "latex": r"D=\frac{Eh^3}{12(1-\nu^2)}",
                        "variables": [(r"D", "rigidez flexional", "N·m"), (r"E", "módulo de Young", "Pa"), (r"h", "espesor", "m"), (r"\nu", "coeficiente de Poisson", "—")],
                        "use": "Caracteriza la resistencia de una placa a la flexión.",
                    },
                    {
                        "title": "Frecuencia crítica o de coincidencia",
                        "latex": r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
                        "variables": [(r"f_c", "frecuencia crítica", "Hz"), (r"c", "velocidad del sonido", "m/s"), (r"m'", "masa superficial", "kg/m²"), (r"D", "rigidez flexional", "N·m")],
                        "use": "Ubica la zona de coincidencia donde puede disminuir el aislamiento.",
                    },
                ],
            },
            {
                "title": "Sistemas dobles y ventanas",
                "formulas": [
                    {
                        "title": "Resonancia masa–aire–masa",
                        "latex": r"f_0\approx60\sqrt{\frac{1}{d}\left(\frac{1}{m'_1}+\frac{1}{m'_2}\right)}",
                        "variables": [(r"f_0", "frecuencia de resonancia masa–aire–masa", "Hz"), (r"d", "profundidad de cámara", "m"), (r"m'_1,m'_2", "masas superficiales", "kg/m²")],
                        "use": "Estima la resonancia principal de un sistema de dos hojas.",
                    },
                    {
                        "title": "Frecuencia límite asociada a la cámara",
                        "latex": r"f_l=\frac{c}{2\pi d}",
                        "variables": [(r"f_l", "frecuencia límite", "Hz"), (r"c", "velocidad del sonido", "m/s"), (r"d", "profundidad de cámara", "m")],
                        "use": "Separa regiones de comportamiento en modelos simplificados de sistemas dobles.",
                    },
                ],
            },
            {
                "title": "Índices ponderados y adaptaciones espectrales",
                "formulas": [
                    {
                        "title": "Forma de informar el índice ponderado",
                        "latex": r"R_w(C;C_{tr})",
                        "variables": [(r"R_w", "índice ponderado de reducción sonora", "dB"), (r"C", "término de adaptación espectral", "dB"), (r"C_{tr}", "adaptación para tránsito", "dB")],
                        "use": "Presenta el índice único junto con sus términos de adaptación.",
                    },
                    {
                        "title": "Término de adaptación C",
                        "latex": r"X_1=-10\log_{10}\!\left[\sum_i10^{(L_{1,i}-R_i)/10}\right]\qquad C=X_1-R_w",
                        "variables": [(r"L_{1,i}", "espectro de referencia 1", "dB"), (r"R_i", "reducción en banda i", "dB"), (r"C", "término de adaptación", "dB")],
                        "use": "Adapta el índice ponderado al espectro de referencia correspondiente.",
                    },
                    {
                        "title": "Término de adaptación Ctr",
                        "latex": r"X_2=-10\log_{10}\!\left[\sum_i10^{(L_{2,i}-R_i)/10}\right]\qquad C_{tr}=X_2-R_w",
                        "variables": [(r"L_{2,i}", "espectro de referencia 2", "dB"), (r"R_i", "reducción en banda i", "dB"), (r"C_{tr}", "adaptación para tránsito", "dB")],
                        "use": "Adapta el índice ponderado a fuentes con mayor contenido de bajas frecuencias.",
                    },
                ],
            },
            {
                "title": "Evaluación económica",
                "formulas": [
                    {
                        "title": "Flujo neto anual",
                        "latex": r"F_{neto}=B_{bruto}-C_{recurrente}",
                        "variables": [(r"F_{neto}", "flujo neto anual", "$/año"), (r"B_{bruto}", "beneficio bruto anual", "$/año"), (r"C_{recurrente}", "costos recurrentes", "$/año")],
                        "use": "Determina el flujo anual disponible para recuperar la inversión.",
                    },
                    {
                        "title": "Periodo simple de recuperación",
                        "latex": r"\mathrm{Payback}=\frac{I_0}{F_{neto}}",
                        "variables": [(r"I_0", "inversión inicial", "$"), (r"F_{neto}", "flujo neto anual", "$/año")],
                        "use": "Estima el tiempo requerido para recuperar la inversión.",
                    },
                    {
                        "title": "Retorno sobre la inversión",
                        "latex": r"ROI=\frac{B_{acumulado}-C_{total}}{C_{total}}\,100",
                        "variables": [(r"ROI", "retorno sobre la inversión", "%"), (r"B_{acumulado}", "beneficios acumulados", "$"), (r"C_{total}", "costos totales", "$")],
                        "use": "Compara beneficios y costos acumulados en un mismo periodo.",
                    },
                ],
            },
        ],
    },

    {
        "id": "curso_2",
        "number": 2,
        "title": "Control de ruido de impacto y ruido de instalaciones",
        "enabled": True,
        "themes": [
            {
                "title": "Magnitudes de impacto y normalización",
                "formulas": [
                    {
                        "title": "Predicción del nivel de impacto de la losa base",
                        "latex": r"L_{n,0}(f)=43+30\log_{10}(f)-10\log_{10}(\sigma_{rad})-R(f)",
                        "variables": [
                            (r"L_{n,0}(f)", "nivel estimado de ruido de impacto de la losa base", "dB"),
                            (r"f", "frecuencia de análisis", "Hz"),
                            (r"\sigma_{rad}", "eficiencia de radiación adoptada por el modelo", "—"),
                            (r"R(f)", "índice de reducción sonora de la losa en la banda f", "dB"),
                        ],
                        "use": "Modelo predictivo utilizado en el Curso 2 · Laboratorio 1 para estimar, por bandas, el nivel de impacto de la losa base dentro de las hipótesis del ejercicio.",
                    },
                    {
                        "title": "Definición de mejora del tratamiento",
                        "latex": r"\Delta L_n(f)=L_{n,0}(f)-L_n(f)",
                        "variables": [
                            (r"\Delta L_n(f)", "mejora del tratamiento en la banda f", "dB"),
                            (r"L_{n,0}(f)", "nivel estimado de la losa base sin tratamiento", "dB"),
                            (r"L_n(f)", "nivel estimado con el tratamiento aplicado", "dB"),
                        ],
                        "use": "Define la mejora espectral como diferencia de niveles respecto de la condición base. La mejora depende de la frecuencia.",
                    },
                    {
                        "title": "Mejora de piso flotante · modelo continuo Cremer/Vigran",
                        "latex": r"\Delta L_n(f)=20\log_{10}\!\left(\frac{(2\pi f)^2m'_1}{s'}\right)",
                        "variables": [
                            (r"\Delta L_n(f)", "mejora estimada del piso flotante", "dB"),
                            (r"f", "frecuencia de banda", "Hz"),
                            (r"m'_1", "masa superficial de la masa flotante o sobrelosa", "kg/m²"),
                            (r"s'", "rigidez dinámica superficial de la capa resiliente", "N/m³"),
                        ],
                        "use": "Forma utilizada en el laboratorio para una capa resiliente continua idealizada. No debe confundirse con la transmisibilidad mecánica T_F.",
                    },
                    {
                        "title": "Forma equivalente de la mejora usando la frecuencia natural",
                        "latex": r"\Delta L_n(f)=40\log_{10}\!\left(\frac{f}{f_{0,\mathrm{cont}}}\right)",
                        "variables": [
                            (r"\Delta L_n(f)", "mejora estimada por banda", "dB"),
                            (r"f", "frecuencia de análisis", "Hz"),
                            (r"f_{0,\mathrm{cont}}", "frecuencia natural del modelo continuo idealizado", "Hz"),
                        ],
                        "use": "Forma equivalente del modelo continuo bajo sus hipótesis. Permite visualizar que la mejora aumenta al alejarse por encima de la región resonante.",
                    },
                    {
                        "title": "Predicción espectral del piso terminado",
                        "latex": r"L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)",
                        "variables": [
                            (r"L_{n,0}(f)", "nivel de impacto estimado de la losa base", "dB"),
                            (r"\Delta L_n(f)", "mejora estimada del tratamiento", "dB"),
                            (r"L_{n,\mathrm{final}}(f)", "nivel final estimado del sistema terminado", "dB"),
                        ],
                        "use": "Combina banda por banda la predicción de la losa base y la mejora del tratamiento. Sigue siendo una predicción espectral, no un número único.",
                    },
                    {
                        "title": "Área de absorción equivalente desde reverberación",
                        "latex": r"A=0.16\,\frac{V}{T}",
                        "variables": [(r"A", "área de absorción equivalente", "m²"), (r"V", "volumen del recinto", "m³"), (r"T", "tiempo de reverberación", "s")],
                        "use": "Permite obtener la absorción equivalente del recinto a partir de una medición de reverberación.",
                    },
                    {
                        "title": "Nivel normalizado de impactos en edificio",
                        "latex": r"L'_n=L_i+10\log_{10}\!\left(\frac{A}{A_0}\right)",
                        "variables": [(r"L'_n", "nivel normalizado de impactos", "dB"), (r"L_i", "nivel de impacto medido", "dB"), (r"A", "absorción equivalente", "m²"), (r"A_0", "absorción de referencia", "10 m²")],
                        "use": "Se utiliza cuando el criterio está definido respecto de un área de absorción equivalente de referencia.",
                    },
                    {
                        "title": "Nivel estandarizado por reverberación",
                        "latex": r"L'_{nT}=L_i-10\log_{10}\!\left(\frac{T}{T_0}\right)",
                        "variables": [(r"L'_{nT}", "nivel estandarizado de impactos", "dB"), (r"L_i", "nivel de impacto medido", "dB"), (r"T", "reverberación medida", "s"), (r"T_0", "reverberación de referencia", "s")],
                        "use": "Se utiliza cuando el descriptor está definido respecto de un tiempo de reverberación de referencia.",
                    },
                ],
            },
            {
                "title": "Ponderación ISO 717-2",
                "formulas": [
                    {
                        "title": "Desviación desfavorable por banda",
                        "latex": r"d_i=\max\!\left(0,L_{n,i}-L_{\mathrm{ref},i}\right)",
                        "variables": [(r"d_i", "desviación desfavorable", "dB"), (r"L_{n,i}", "nivel de impacto de la banda i", "dB"), (r"L_{\mathrm{ref},i}", "referencia desplazada", "dB")],
                        "use": "Solo penaliza las bandas cuyo nivel de impacto queda por encima de la referencia.",
                    },
                    {
                        "title": "Criterio de suma de desviaciones",
                        "latex": r"\sum_i d_i\le 32\ \mathrm{dB}",
                        "variables": [(r"d_i", "desviación desfavorable de la banda i", "dB")],
                        "use": "Define el criterio de ajuste de la referencia para 16 bandas de tercio de octava.",
                    },
                    {
                        "title": "Lectura del número único",
                        "latex": r"L_{n,w}=L_{\mathrm{ref,límite}}(500\ \mathrm{Hz})",
                        "variables": [(r"L_{n,w}", "nivel normalizado ponderado de impactos", "dB")],
                        "use": "Una vez encontrada la posición límite, el descriptor se lee en 500 Hz.",
                    },
                ],
            },
            {
                "title": "Suma energética y términos espectrales",
                "formulas": [
                    {
                        "title": "Suma energética de niveles",
                        "latex": r"L_{n,\mathrm{sum}}=10\log_{10}\!\left(\sum_i10^{L_{n,i}/10}\right)",
                        "variables": [(r"L_{n,\mathrm{sum}}", "nivel global por suma energética", "dB"), (r"L_{n,i}", "nivel de cada banda", "dB")],
                        "use": "Construye el nivel global a partir de niveles por banda; los dB no se suman aritméticamente.",
                    },
                    {
                        "title": "Término de adaptación espectral CI",
                        "latex": r"C_I=L_{n,\mathrm{sum}(100-2500)}-15-L_{n,w}",
                        "variables": [(r"C_I", "término de adaptación espectral", "dB"), (r"L_{n,\mathrm{sum}(100-2500)}", "suma energética 100–2500 Hz", "dB"), (r"L_{n,w}", "descriptor ponderado", "dB")],
                        "use": "Complementa Lnw con información espectral; no representa una mejora física adicional.",
                    },
                    {
                        "title": "Término ampliado CI,50–2500",
                        "latex": r"C_{I,50-2500}=L_{n,\mathrm{sum}(50-2500)}-15-L_{n,w}",
                        "variables": [(r"C_{I,50-2500}", "término de adaptación ampliado", "dB"), (r"L_{n,\mathrm{sum}(50-2500)}", "suma energética 50–2500 Hz", "dB"), (r"L_{n,w}", "descriptor ponderado", "dB")],
                        "use": "Añade 50, 63 y 80 Hz para revelar información grave adicional.",
                    },
                ],
            },
            {
                "title": "Revestimientos y reducción ponderada",
                "formulas": [
                    {
                        "title": "Masa superficial de una capa",
                        "latex": r"m'=\rho h",
                        "variables": [
                            (r"m'", "masa superficial de la capa", "kg/m²"),
                            (r"\rho", "densidad del material", "kg/m³"),
                            (r"h", "espesor de la capa", "m"),
                        ],
                        "use": "Se utiliza para construir la masa superficial de la sobrelosa o de otras capas del sistema.",
                    },
                    {
                        "title": "Masa reducida del piso flotante",
                        "latex": r"m'_r=\frac{m'_1m'_2}{m'_1+m'_2}",
                        "variables": [
                            (r"m'_r", "masa superficial reducida", "kg/m²"),
                            (r"m'_1", "masa superficial de la capa flotante", "kg/m²"),
                            (r"m'_2", "masa superficial de la losa base", "kg/m²"),
                        ],
                        "use": "Representa la masa dinámica equivalente cuando ambas masas participan en el movimiento relativo.",
                    },
                    {
                        "title": "Frecuencia natural del piso flotante",
                        "latex": r"f_0=\frac{1}{2\pi}\sqrt{\frac{s'}{m'_r}}",
                        "variables": [
                            (r"f_0", "frecuencia natural aproximada del sistema", "Hz"),
                            (r"s'", "rigidez dinámica superficial", "N/m³"),
                            (r"m'_r", "masa superficial reducida", "kg/m²"),
                        ],
                        "use": "Ubica la región resonante del piso flotante idealizado antes de calcular la mejora acústica.",
                    },
                    {
                        "title": "Piso pesado de referencia tratado",
                        "latex": r"L_{n,r}(f)=L_{n,r,0}(f)-\Delta L(f)",
                        "variables": [(r"L_{n,r,0}(f)", "piso pesado de referencia sin revestimiento", "dB"), (r"\Delta L(f)", "reducción del revestimiento por banda", "dB"), (r"L_{n,r}(f)", "piso de referencia tratado", "dB")],
                        "use": "Aplica primero la reducción espectral del revestimiento al piso de referencia.",
                    },
                    {
                        "title": "Reducción ponderada del revestimiento",
                        "latex": r"\Delta L_w=L_{n,r,0,w}-L_{n,r,w}=78-L_{n,r,w}",
                        "variables": [(r"\Delta L_w", "reducción ponderada del revestimiento", "dB"), (r"L_{n,r,0,w}", "piso pesado de referencia sin revestimiento", "78 dB"), (r"L_{n,r,w}", "piso pesado de referencia tratado y ponderado", "dB")],
                        "use": "Resume la reducción espectral del revestimiento mediante el piso pesado de referencia ISO 717-2.",
                    },
                ],
            },
            {
                "title": "Bomba y aislamiento vibratorio",
                "formulas": [
                    {
                        "title": "Frecuencia de excitación por velocidad de giro",
                        "latex": r"f_e=\frac{n}{60}",
                        "variables": [(r"f_e", "frecuencia fundamental de excitación", "Hz"), (r"n", "velocidad de giro", "rpm")],
                        "use": "Convierte las rpm de una máquina rotatoria en su frecuencia fundamental 1×.",
                    },
                    {
                        "title": "Frecuencia natural masa–resorte",
                        "latex": r"f_n=\frac{1}{2\pi}\sqrt{\frac{k_t}{m}}",
                        "variables": [(r"f_n", "frecuencia natural del montaje", "Hz"), (r"k_t", "rigidez total", "N/m"), (r"m", "masa soportada", "kg")],
                        "use": "Relaciona masa y rigidez del sistema de aislamiento.",
                    },
                    {
                        "title": "Razón de frecuencias",
                        "latex": r"r=\frac{f_e}{f_n}",
                        "variables": [(r"r", "razón de frecuencias", "—"), (r"f_e", "frecuencia de excitación", "Hz"), (r"f_n", "frecuencia natural", "Hz")],
                        "use": "Ubica el montaje respecto de resonancia, transición y región de aislamiento.",
                    },
                    {
                        "title": "Transmisibilidad de fuerza",
                        "latex": r"T_F=\sqrt{\frac{1+(2\zeta r)^2}{(1-r^2)^2+(2\zeta r)^2}}",
                        "variables": [(r"T_F", "transmisibilidad de fuerza", "—"), (r"\zeta", "razón de amortiguamiento", "—"), (r"r", "razón de frecuencias", "—")],
                        "use": "Estima la fracción de fuerza dinámica transmitida por la base en el modelo ideal.",
                    },
                    {
                        "title": "Porcentaje ideal de fuerza transmitida",
                        "latex": r"\%F_{\mathrm{trans}}=100\,T_F",
                        "variables": [(r"\%F_{\mathrm{trans}}", "porcentaje ideal de fuerza transmitida", "%"), (r"T_F", "transmisibilidad de fuerza", "—")],
                        "use": "Expresa la transmisibilidad de fuerza como porcentaje para facilitar su interpretación.",
                    },
                ],
            },
        ],
    },
]


def _enabled_courses() -> Iterable[dict[str, Any]]:
    return (course for course in FORMULA_CATALOG if course.get("enabled", False))


def _formula_search_text(course: dict[str, Any], theme: dict[str, Any], formula: dict[str, Any]) -> str:
    values = [course["title"], theme["title"], formula["title"], formula.get("use", "")]
    values.extend(f"{symbol} {meaning} {unit}" for symbol, meaning, unit in formula.get("variables", []))
    return " ".join(values).lower()


def _render_formula_card(course: dict[str, Any], theme: dict[str, Any], formula: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td class='symbol'>\\({escape(symbol)}\\)</td>"
        f"<td>{escape(meaning)}</td>"
        f"<td>{escape(unit)}</td>"
        "</tr>"
        for symbol, meaning, unit in formula.get("variables", [])
    )
    search_text = escape(_formula_search_text(course, theme, formula), quote=True)
    return f"""
    <article class="formula-card" data-search="{search_text}">
      <h4>{escape(formula['title'])}</h4>
      <div class="equation">\\[{formula['latex']}\\]</div>
      <table>
        <thead><tr><th>Símbolo</th><th>Corresponde a</th><th>Unidad</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p class="formula-use"><strong>Uso:</strong> {escape(formula.get('use', ''))}</p>
    </article>
    """


def build_formulary_html(visible_labs=None) -> str:
    course_sections: list[str] = []
    formula_count = 0

    for course in _enabled_courses():
        theme_sections: list[str] = []
        for theme in course.get("themes", []):
            cards = []
            for formula in theme.get("formulas", []):
                cards.append(_render_formula_card(course, theme, formula))
                formula_count += 1
            if cards:
                theme_sections.append(
                    f"""
                    <details class="theme">
                      <summary>{escape(theme['title'])}</summary>
                      <div class="theme-content">{''.join(cards)}</div>
                    </details>
                    """
                )

        course_sections.append(
            f"""
            <section class="course-section" data-course="{escape(course['id'], quote=True)}">
              <div class="course-heading">
                <span>CURSO {course['number']}</span>
                <h2>{escape(course['title'])}</h2>
              </div>
              {''.join(theme_sections)}
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Formulario Técnico de Acústica</title>
<script>
window.MathJax = {{
  tex: {{inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']]}},
  svg: {{fontCache: 'global'}}
}};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
:root{{--navy:#07345c;--blue:#087fbd;--pale:#eef6fc;--line:#c8ddec;--text:#0c2f50;}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f7fa;color:var(--text);font-family:Arial,Helvetica,sans-serif}}
.wrapper{{max-width:1180px;margin:0 auto;padding:18px}}
.hero{{background:linear-gradient(120deg,var(--navy),#0a8bc3);color:#fff;border-radius:0 0 22px 22px;padding:24px 32px;margin-bottom:20px}}
.hero small{{font-weight:800;letter-spacing:.15em;color:#aaf0ff}}
.hero h1{{margin:12px 0 7px;font-size:clamp(28px,4vw,44px)}}
.hero p{{margin:0;max-width:850px;line-height:1.5}}
.toolbar{{position:sticky;top:0;z-index:20;background:rgba(244,247,250,.96);padding:10px 0 12px;backdrop-filter:blur(8px)}}
.search{{width:100%;border:1px solid #91b9d3;border-radius:10px;padding:12px 14px;font-size:16px;color:var(--text);background:#fff}}
.stats{{font-size:13px;color:#4a6a82;margin-top:7px}}
.course-section{{margin:20px 0 30px}}
.course-heading{{border-left:6px solid var(--blue);padding:5px 0 5px 14px;margin-bottom:12px}}
.course-heading span{{font-weight:800;color:var(--blue);letter-spacing:.08em}}
.course-heading h2{{margin:4px 0 0;font-size:25px}}
details.theme{{background:#fff;border:1px solid var(--line);border-radius:13px;margin:12px 0;overflow:hidden}}
details.theme>summary{{cursor:pointer;background:#e5f2fb;padding:15px 18px;font-size:20px;font-weight:800;color:#075184}}
.theme-content{{padding:14px}}
.formula-card{{border:1px solid #d2e2ee;border-left:5px solid #0a83c4;border-radius:12px;padding:15px 17px;margin:12px 0;background:#fff}}
.formula-card h4{{font-size:18px;color:#075184;margin:0 0 7px}}
.equation{{overflow-x:auto;text-align:center;background:#f7fafc;border-radius:9px;padding:10px;font-size:1.05rem}}
table{{width:100%;border-collapse:collapse;margin-top:10px}}
th,td{{border-top:1px solid #d9e5ee;padding:8px 10px;text-align:left;vertical-align:top}}
th{{font-size:12px;text-transform:uppercase;color:#365b76}}
td.symbol{{width:18%;font-weight:700}}
.formula-use{{margin:10px 0 0;color:#34576f;line-height:1.45}}
.empty{{display:none;background:#fff4d8;border:1px solid #e4c66c;border-radius:10px;padding:14px;margin-top:12px}}
@media(max-width:700px){{.wrapper{{padding:8px}}.hero{{padding:20px 18px}}th,td{{padding:7px 6px;font-size:13px}}}}
</style>
</head>
<body>
<header class="hero">
  <small>FORMULARIO DEL DIPLOMADO</small>
  <h1>Formulario Técnico de Acústica</h1>
  <p>Herramienta de consulta con las ecuaciones y relaciones técnicas incorporadas a medida que se desarrollan y validan los cursos del diplomado.</p>
</header>
<main class="wrapper">
  <div class="toolbar">
    <input id="formula-search" class="search" type="search" placeholder="Buscar fórmula, variable o concepto…" autocomplete="off">
    <div class="stats"><span id="visible-count">{formula_count}</span> de {formula_count} fórmulas visibles</div>
    <div id="empty-message" class="empty">No se encontraron fórmulas para esa búsqueda.</div>
  </div>
  {''.join(course_sections)}
</main>
<script>
const input=document.getElementById('formula-search');
const cards=[...document.querySelectorAll('.formula-card')];
const counter=document.getElementById('visible-count');
const empty=document.getElementById('empty-message');
function normalize(value){{return value.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim();}}
function filterCards(){{
  const query=normalize(input.value);
  let visible=0;
  cards.forEach(card=>{{
    const show=!query || normalize(card.dataset.search).includes(query);
    card.style.display=show?'block':'none';
    if(show) visible++;
  }});
  document.querySelectorAll('details.theme').forEach(theme=>{{
    const hasVisible=[...theme.querySelectorAll('.formula-card')].some(card=>card.style.display!=='none');
    theme.style.display=hasVisible?'block':'none';
    if(query && hasVisible) theme.open=true;
  }});
  document.querySelectorAll('.course-section').forEach(course=>{{
    const hasVisible=[...course.querySelectorAll('.formula-card')].some(card=>card.style.display!=='none');
    course.style.display=hasVisible?'block':'none';
  }});
  counter.textContent=visible;
  empty.style.display=visible?'none':'block';
}}
input.addEventListener('input',filterCards);
</script>
</body>
</html>"""
