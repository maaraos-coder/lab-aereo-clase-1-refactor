"""Formulario técnico escalable del Diplomado en Acústica.

Cada curso se agrega como un bloque dentro de ``FORMULA_CATALOG``. El motor de
renderizado no necesita modificarse cuando se incorporan nuevos cursos, temas o
ecuaciones: basta con añadir datos y marcar el curso como ``enabled=True``.

Las ecuaciones incluidas corresponden a contenido técnico de clase. No se
incluyen sustituciones numéricas, criterios particulares ni fórmulas creadas
solo para resolver un ejercicio específico.
"""

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
                        "latex": (
                            r"\tau_T=\frac{\sum_{i=1}^{n}S_i\tau_i}{\sum_{i=1}^{n}S_i}"
                            r"\qquad"
                            r"R_T=-10\log_{10}(\tau_T)"
                        ),
                        "variables": [
                            (r"S_i", "superficie del componente i", "m²"),
                            (r"\tau_i", "coeficiente de transmisión del componente i", "—"),
                            (r"\tau_T", "coeficiente de transmisión total", "—"),
                            (r"R_T", "índice de reducción sonora del conjunto", "dB"),
                        ],
                        "use": "Combina energéticamente los componentes de un cerramiento; los valores en dB no se promedian.",
                    },
                    {
                        "title": "Diferencia de nivel estandarizada",
                        "latex": r"D_{nT}=L_1-L_2+10\log_{10}\!\left(\frac{T}{T_0}\right)",
                        "variables": [
                            (r"D_{nT}", "diferencia de nivel estandarizada", "dB"),
                            (r"L_1", "nivel en el recinto emisor", "dB"),
                            (r"L_2", "nivel en el recinto receptor", "dB"),
                            (r"T", "tiempo de reverberación del recinto receptor", "s"),
                            (r"T_0", "tiempo de reverberación de referencia", "s"),
                        ],
                        "use": "Normaliza la diferencia de niveles respecto del tiempo de reverberación del recinto receptor.",
                    },
                ],
            },
            {
                "title": "Placas simples",
                "formulas": [
                    {
                        "title": "Masa superficial",
                        "latex": r"m'=\rho h",
                        "variables": [
                            (r"m'", "masa superficial", "kg/m²"),
                            (r"\rho", "densidad del material", "kg/m³"),
                            (r"h", "espesor de la placa", "m"),
                        ],
                        "use": "Relaciona densidad y espesor con la masa por unidad de superficie.",
                    },
                    {
                        "title": "Ley de masa",
                        "latex": r"R\approx20\log_{10}(m'f)-47",
                        "variables": [
                            (r"R", "índice de reducción sonora aproximado", "dB"),
                            (r"m'", "masa superficial", "kg/m²"),
                            (r"f", "frecuencia", "Hz"),
                        ],
                        "use": "Describe la tendencia ideal de una placa simple en la región controlada por masa.",
                    },
                    {
                        "title": "Rigidez flexional",
                        "latex": r"D=\frac{Eh^3}{12(1-\nu^2)}",
                        "variables": [
                            (r"D", "rigidez flexional", "N·m"),
                            (r"E", "módulo de Young", "Pa"),
                            (r"h", "espesor", "m"),
                            (r"\nu", "coeficiente de Poisson", "—"),
                        ],
                        "use": "Caracteriza la resistencia de una placa a la flexión.",
                    },
                    {
                        "title": "Frecuencia crítica o de coincidencia",
                        "latex": r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
                        "variables": [
                            (r"f_c", "frecuencia crítica", "Hz"),
                            (r"c", "velocidad del sonido en el aire", "m/s"),
                            (r"m'", "masa superficial", "kg/m²"),
                            (r"D", "rigidez flexional", "N·m"),
                        ],
                        "use": "Ubica la zona de coincidencia donde puede disminuir el aislamiento de la placa.",
                    },
                    {
                        "title": "Transmisión de una hoja ideal según el ángulo",
                        "latex": r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}",
                        "variables": [
                            (r"\theta", "ángulo de incidencia", "°"),
                            (r"\omega", "frecuencia angular, 2πf", "rad/s"),
                            (r"m'", "masa superficial", "kg/m²"),
                            (r"\rho_0", "densidad del aire", "kg/m³"),
                            (r"c", "velocidad del sonido", "m/s"),
                        ],
                        "use": "Representa la transmisión ideal de una placa flexible para una incidencia determinada.",
                    },
                ],
            },
            {
                "title": "Sistemas dobles y ventanas",
                "formulas": [
                    {
                        "title": "Resonancia masa–aire–masa",
                        "latex": r"f_0\approx60\sqrt{\frac{1}{d}\left(\frac{1}{m'_1}+\frac{1}{m'_2}\right)}",
                        "variables": [
                            (r"f_0", "frecuencia de resonancia masa–aire–masa", "Hz"),
                            (r"d", "profundidad de la cámara de aire", "m"),
                            (r"m'_1,m'_2", "masas superficiales de las hojas", "kg/m²"),
                        ],
                        "use": "Estima la resonancia principal de un sistema de dos hojas separadas por aire.",
                    },
                    {
                        "title": "Frecuencia límite asociada a la cámara",
                        "latex": r"f_l=\frac{c}{2\pi d}",
                        "variables": [
                            (r"f_l", "frecuencia límite de la cámara", "Hz"),
                            (r"c", "velocidad del sonido", "m/s"),
                            (r"d", "profundidad de la cámara", "m"),
                        ],
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
                        "variables": [
                            (r"R_w", "índice ponderado de reducción sonora", "dB"),
                            (r"C", "término de adaptación espectral 1", "dB"),
                            (r"C_{tr}", "término de adaptación para tránsito", "dB"),
                        ],
                        "use": "Presenta el índice único junto con sus términos de adaptación espectral.",
                    },
                    {
                        "title": "Término de adaptación C",
                        "latex": (
                            r"X_1=-10\log_{10}\!\left[\sum_i10^{(L_{1,i}-R_i)/10}\right]"
                            r"\qquad C=X_1-R_w"
                        ),
                        "variables": [
                            (r"L_{1,i}", "valor del espectro de referencia 1 en la banda i", "dB"),
                            (r"R_i", "índice de reducción sonora en la banda i", "dB"),
                            (r"C", "término de adaptación espectral", "dB"),
                        ],
                        "use": "Adapta el índice ponderado al espectro de referencia correspondiente.",
                    },
                    {
                        "title": "Término de adaptación Ctr",
                        "latex": (
                            r"X_2=-10\log_{10}\!\left[\sum_i10^{(L_{2,i}-R_i)/10}\right]"
                            r"\qquad C_{tr}=X_2-R_w"
                        ),
                        "variables": [
                            (r"L_{2,i}", "valor del espectro de referencia 2 en la banda i", "dB"),
                            (r"R_i", "índice de reducción sonora en la banda i", "dB"),
                            (r"C_{tr}", "término de adaptación para tránsito", "dB"),
                        ],
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
                        "variables": [
                            (r"F_{neto}", "flujo neto anual", "$/año"),
                            (r"B_{bruto}", "beneficio bruto anual", "$/año"),
                            (r"C_{recurrente}", "costos recurrentes", "$/año"),
                        ],
                        "use": "Determina el flujo anual disponible para recuperar la inversión.",
                    },
                    {
                        "title": "Periodo simple de recuperación",
                        "latex": r"\mathrm{Payback}=\frac{I_0}{F_{neto}}",
                        "variables": [
                            (r"I_0", "inversión inicial", "$"),
                            (r"F_{neto}", "flujo neto anual", "$/año"),
                        ],
                        "use": "Estima el tiempo requerido para recuperar la inversión inicial.",
                    },
                    {
                        "title": "Retorno sobre la inversión",
                        "latex": r"ROI=\frac{B_{acumulado}-C_{total}}{C_{total}}\,100",
                        "variables": [
                            (r"ROI", "retorno sobre la inversión", "%"),
                            (r"B_{acumulado}", "beneficios acumulados", "$"),
                            (r"C_{total}", "costos totales", "$"),
                        ],
                        "use": "Compara los beneficios y costos acumulados en un mismo periodo.",
                    },
                ],
            },
        ],
    },
    # Los cursos nuevos se incorporan copiando la plantilla siguiente y
    # marcándola como enabled=True cuando su contenido técnico esté validado.
    # {
    #     "id": "curso_2",
    #     "number": 2,
    #     "title": "Control de ruido de impacto y ruido de instalaciones",
    #     "enabled": False,
    #     "themes": [],
    # },
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
    """Construye el formulario completo.

    ``visible_labs`` se conserva por compatibilidad con la aplicación actual,
    pero el catálogo nuevo se controla mediante ``enabled`` a nivel de curso.
    """
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
                    <details class="theme" open>
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
