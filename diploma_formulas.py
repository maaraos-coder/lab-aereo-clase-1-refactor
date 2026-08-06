"""Formulario técnico general del diplomado con ecuaciones renderizadas en LaTeX."""

FORMULA_CATALOG = [{
    "course": "Aislamiento acústico al ruido aéreo",
    "labs": [
        {
            "number": 1,
            "subtitle": "Fundamentos, recintos, transmisión y evaluación económica",
            "topics": [
                ("1. Recintos y absorción", [
                    ("Absorción equivalente", "A = Σ(α<sub>i</sub>·S<sub>i</sub>)",
                     [("A","absorción equivalente","m² sabin"),("α<sub>i</sub>","coeficiente de absorción","—"),("S<sub>i</sub>","superficie i","m²")],
                     "Suma los aportes absorbentes de las superficies."),
                    ("Ecuación de Sabine", "T<sub>60</sub> = 0,161·V/A",
                     [("T<sub>60</sub>","tiempo de reverberación","s"),("V","volumen del recinto","m³"),("A","absorción equivalente","m² sabin")],
                     "Estima la reverberación bajo condiciones compatibles con Sabine."),
                ]),
                ("2. Transmisión y cerramientos compuestos", [
                    ("Coeficiente de transmisión", "τ = W<sub>t</sub>/W<sub>i</sub> = 10<sup>−R/10</sup>",
                     [("τ","fracción de potencia transmitida","—"),("W<sub>t</sub>","potencia transmitida","W"),("W<sub>i</sub>","potencia incidente","W"),("R","reducción sonora","dB")],
                     "Convierte el aislamiento en una fracción energética."),
                    ("Reducción sonora", "R = 10·log<sub>10</sub>(1/τ)",
                     [("R","reducción sonora por banda","dB"),("τ","coeficiente de transmisión","—")],
                     "Expresa logarítmicamente la razón entre potencia incidente y transmitida."),
                    ("Cerramiento compuesto", "τ<sub>t</sub> = Σ(S<sub>i</sub>τ<sub>i</sub>)/ΣS<sub>i</sub><br>R<sub>t</sub> = −10·log<sub>10</sub>(τ<sub>t</sub>)",
                     [("S<sub>i</sub>","área de cada componente","m²"),("τ<sub>i</sub>","transmisión de cada componente","—"),("R<sub>t</sub>","reducción del conjunto","dB")],
                     "Combina muro, puerta o ventana en energía; los dB no se promedian."),
                ]),
                ("3. Placas simples", [
                    ("Masa superficial", "m′ = ρ·h", [("m′","masa por unidad de superficie","kg/m²"),("ρ","densidad","kg/m³"),("h","espesor","m")], "Relaciona material y espesor con la masa superficial."),
                    ("Ley de masa", "R ≈ 20·log<sub>10</sub>(m′·f) − 47", [("R","reducción sonora aproximada","dB"),("m′","masa superficial","kg/m²"),("f","frecuencia","Hz")], "Aproximación de campo difuso en la región controlada por masa."),
                    ("Rigidez flexional", "D = E·h<sup>3</sup>/[12(1−ν<sup>2</sup>)]", [("D","rigidez flexional","N·m"),("E","módulo de Young","Pa"),("h","espesor","m"),("ν","coeficiente de Poisson","—")], "Paso previo para estimar la coincidencia."),
                    ("Frecuencia crítica", "f<sub>c</sub> = c<sup>2</sup>/(2π)·√(m′/D)", [("f<sub>c</sub>","frecuencia crítica","Hz"),("c","velocidad del sonido","m/s"),("m′","masa superficial","kg/m²"),("D","rigidez flexional","N·m")], "Ubica la zona donde puede caer el aislamiento por coincidencia."),
                ]),
                ("4. Evaluación económica", [
                    ("Flujo neto anual", "F<sub>neto</sub> = B<sub>bruto</sub> − C<sub>recurrente</sub>", [("F<sub>neto</sub>","flujo neto anual","$/año"),("B<sub>bruto</sub>","beneficio bruto anual","$/año"),("C<sub>recurrente</sub>","costos recurrentes","$/año")], "Determina el flujo disponible para recuperar la inversión."),
                    ("Payback", "Payback = I<sub>0</sub>/F<sub>neto</sub>", [("I<sub>0</sub>","inversión inicial","$"),("F<sub>neto</sub>","flujo neto anual","$/año")], "Calcula el periodo simple de recuperación."),
                    ("ROI", "ROI = (B<sub>acumulado</sub>−C<sub>total</sub>)/C<sub>total</sub>·100", [("B<sub>acumulado</sub>","beneficios acumulados","$"),("C<sub>total</sub>","costos totales","$"),("ROI","retorno sobre costos","%")], "Compara beneficios y costos del mismo periodo."),
                ]),
            ],
        },
        {
            "number": 2,
            "subtitle": "Pérdida de transmisión, placas simples y dobles, ventanas, Rw, C y Ctr",
            "topics": [
                ("1. Pérdida de transmisión", [
                    ("Coeficiente de transmisión", "τ = W<sub>t</sub>/W<sub>i</sub>", [("τ","fracción transmitida","—"),("W<sub>t</sub>","potencia transmitida","W"),("W<sub>i</sub>","potencia incidente","W")], "Punto de partida físico del Laboratorio 2."),
                    ("Pérdida de transmisión", "TL = −10·log<sub>10</sub>(τ)<br>τ = 10<sup>−TL/10</sup>", [("TL","pérdida de transmisión","dB"),("τ","coeficiente de transmisión","—")], "Convierte en ambos sentidos entre τ y TL."),
                ]),
                ("2. Panel simple e incidencia", [
                    ("Masa superficial", "m′ = ρ·h", [("m′","masa superficial","kg/m²"),("ρ","densidad","kg/m³"),("h","espesor","m")], "Calcula la masa por metro cuadrado."),
                    ("Transmisión angular", "τ(θ) = [1 + (ωm′cosθ/2ρ<sub>0</sub>c)<sup>2</sup>]<sup>−1</sup>", [("θ","ángulo de incidencia","°"),("ω","frecuencia angular, 2πf","rad/s"),("ρ<sub>0</sub>","densidad del aire","kg/m³"),("c","velocidad del sonido","m/s")], "Calcula la transmisión de una hoja ideal para cada ángulo."),
                    ("TL de campo", "TL<sub>campo</sub> = −10·log<sub>10</sub>(τ̄)", [("τ̄","transmisión integrada angularmente","—"),("TL<sub>campo</sub>","pérdida de transmisión de campo","dB")], "Transforma el promedio energético angular en decibeles."),
                    ("Rigidez y frecuencia crítica", "D = E·h<sup>3</sup>/[12(1−ν<sup>2</sup>)]<br>f<sub>c</sub> = c<sup>2</sup>/(2π)·√(m′/D)", [("D","rigidez flexional","N·m"),("f<sub>c</sub>","frecuencia crítica","Hz")], "Describe rigidez y coincidencia en placas homogéneas."),
                ]),
                ("3. Sistemas dobles", [
                    ("Resonancia masa–aire–masa", "f<sub>0</sub> ≈ 60·√[(1/d)(1/m′<sub>1</sub>+1/m′<sub>2</sub>)]", [("f<sub>0</sub>","frecuencia de resonancia","Hz"),("d","cámara de aire","m"),("m′<sub>1</sub>,m′<sub>2</sub>","masas superficiales","kg/m²")], "Ubica la resonancia principal del sistema doble."),
                    ("Frecuencia límite de cámara", "f<sub>l</sub> = c/(2πd)", [("f<sub>l</sub>","frecuencia límite","Hz"),("c","velocidad del sonido","m/s"),("d","profundidad de cámara","m")], "Separa regiones del modelo simplificado de Sharp."),
                ]),
                ("4. Ventanas simples y dobles", [
                    ("Ventana simple", "m′ = ρ<sub>vidrio</sub>·h", [("m′","masa superficial del vidrio","kg/m²"),("ρ<sub>vidrio</sub>","densidad del vidrio","kg/m³"),("h","espesor del vidrio","m")], "La curva TL se obtiene con el modelo de placa simple utilizado en el laboratorio."),
                    ("Ventana doble", "f<sub>0</sub> ≈ 60·√[(1/d)(1/m′<sub>1</sub>+1/m′<sub>2</sub>)]", [("f<sub>0</sub>","resonancia masa–aire–masa","Hz"),("d","separación entre vidrios","m"),("m′<sub>1</sub>,m′<sub>2</sub>","masas superficiales de los vidrios","kg/m²")], "Permite analizar vidrios iguales o asimétricos y el efecto de la cámara."),
                ]),
                ("5. Índice ponderado y adaptaciones", [
                    ("Índice Rw", "R<sub>w</sub> = valor de la referencia ajustada a 500 Hz", [("R<sub>w</sub>","índice ponderado ISO","dB")], "Se obtiene tras cumplir el criterio de desviaciones desfavorables."),
                    ("Adaptación C", "X<sub>1</sub> = −10·log<sub>10</sub>[Σ10<sup>(L<sub>1,i</sub>−R<sub>i</sub>)/10</sup>]<br>C = X<sub>1</sub>−R<sub>w</sub>", [("L<sub>1,i</sub>","espectro normalizado 1","dB"),("R<sub>i</sub>","reducción por banda","dB"),("C","adaptación espectral","dB")], "Adapta Rw al espectro normalizado 1."),
                    ("Adaptación Ctr", "X<sub>2</sub> = −10·log<sub>10</sub>[Σ10<sup>(L<sub>2,i</sub>−R<sub>i</sub>)/10</sup>]<br>C<sub>tr</sub> = X<sub>2</sub>−R<sub>w</sub>", [("L<sub>2,i</sub>","espectro normalizado 2","dB"),("C<sub>tr</sub>","adaptación para tránsito","dB")], "Adapta Rw a fuentes con mayor contenido grave."),
                    ("Forma de informar", "R<sub>w</sub>(C;C<sub>tr</sub>)", [("R<sub>w</sub>","índice ponderado","dB"),("C,C<sub>tr</sub>","términos de adaptación","dB")], "Los términos se aplican por separado según la fuente."),
                ]),
            ],
        },
    ],
}]


LATEX_EQUATIONS = {
    "A = Σ(α<sub>i</sub>·S<sub>i</sub>)": r"A=\sum_{i=1}^{n}\alpha_i S_i",
    "T<sub>60</sub> = 0,161·V/A": r"T_{60}=0.161\,\frac{V}{A}",
    "τ = W<sub>t</sub>/W<sub>i</sub> = 10<sup>−R/10</sup>": r"\tau=\frac{W_t}{W_i}=10^{-R/10}",
    "R = 10·log<sub>10</sub>(1/τ)": r"R=10\log_{10}\!\left(\frac{1}{\tau}\right)=-10\log_{10}(\tau)",
    "τ<sub>t</sub> = Σ(S<sub>i</sub>τ<sub>i</sub>)/ΣS<sub>i</sub><br>R<sub>t</sub> = −10·log<sub>10</sub>(τ<sub>t</sub>)": r"\tau_T=\frac{\sum_{i=1}^{n}S_i\tau_i}{\sum_{i=1}^{n}S_i}\qquad R_T=-10\log_{10}(\tau_T)",
    "m′ = ρ·h": r"m'=\rho h",
    "R ≈ 20·log<sub>10</sub>(m′·f) − 47": r"R\approx20\log_{10}(m'f)-47",
    "D = E·h<sup>3</sup>/[12(1−ν<sup>2</sup>)]": r"D=\frac{Eh^3}{12\left(1-\nu^2\right)}",
    "f<sub>c</sub> = c<sup>2</sup>/(2π)·√(m′/D)": r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
    "F<sub>neto</sub> = B<sub>bruto</sub> − C<sub>recurrente</sub>": r"F_{\mathrm{neto}}=B_{\mathrm{bruto}}-C_{\mathrm{recurrente}}",
    "Payback = I<sub>0</sub>/F<sub>neto</sub>": r"\mathrm{Payback}=\frac{I_0}{F_{\mathrm{neto}}}",
    "ROI = (B<sub>acumulado</sub>−C<sub>total</sub>)/C<sub>total</sub>·100": r"ROI=\frac{B_{\mathrm{acumulado}}-C_{\mathrm{total}}}{C_{\mathrm{total}}}\,100",
    "τ = W<sub>t</sub>/W<sub>i</sub>": r"\tau=\frac{W_t}{W_i}",
    "TL = −10·log<sub>10</sub>(τ)<br>τ = 10<sup>−TL/10</sup>": r"TL=-10\log_{10}(\tau)\qquad \tau=10^{-TL/10}",
    "τ(θ) = [1 + (ωm′cosθ/2ρ<sub>0</sub>c)<sup>2</sup>]<sup>−1</sup>": r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}",
    "TL<sub>campo</sub> = −10·log<sub>10</sub>(τ̄)": r"TL_{\mathrm{campo}}=-10\log_{10}(\bar{\tau})",
    "D = E·h<sup>3</sup>/[12(1−ν<sup>2</sup>)]<br>f<sub>c</sub> = c<sup>2</sup>/(2π)·√(m′/D)": r"D=\frac{Eh^3}{12\left(1-\nu^2\right)}\qquad f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
    "f<sub>0</sub> ≈ 60·√[(1/d)(1/m′<sub>1</sub>+1/m′<sub>2</sub>)]": r"f_0\approx60\sqrt{\frac{1}{d}\left(\frac{1}{m'_1}+\frac{1}{m'_2}\right)}",
    "f<sub>l</sub> = c/(2πd)": r"f_l=\frac{c}{2\pi d}",
    "m′ = ρ<sub>vidrio</sub>·h": r"m'=\rho_{\mathrm{vidrio}}h",
    "R<sub>w</sub> = valor de la referencia ajustada a 500 Hz": r"R_w=\text{valor de la curva de referencia desplazada a }500\,\mathrm{Hz}",
    "X<sub>1</sub> = −10·log<sub>10</sub>[Σ10<sup>(L<sub>1,i</sub>−R<sub>i</sub>)/10</sup>]<br>C = X<sub>1</sub>−R<sub>w</sub>": r"X_1=-10\log_{10}\!\left[\sum_i10^{(L_{1,i}-R_i)/10}\right]\qquad C=X_1-R_w",
    "X<sub>2</sub> = −10·log<sub>10</sub>[Σ10<sup>(L<sub>2,i</sub>−R<sub>i</sub>)/10</sup>]<br>C<sub>tr</sub> = X<sub>2</sub>−R<sub>w</sub>": r"X_2=-10\log_{10}\!\left[\sum_i10^{(L_{2,i}-R_i)/10}\right]\qquad C_{tr}=X_2-R_w",
    "R<sub>w</sub>(C;C<sub>tr</sub>)": r"R_w\,(C;C_{tr})",
}

SYMBOL_LATEX = {
    "A": "A", "V": "V", "R": "R", "D": "D", "E": "E", "h": "h", "f": "f", "c": "c",
    "τ": r"\tau", "τ̄": r"\bar{\tau}", "θ": r"\theta", "ω": r"\omega", "ρ": r"\rho", "ν": r"\nu",
    "m′": "m'", "ROI": "ROI", "Payback": r"\mathrm{Payback}", "TL": "TL", "C": "C",
    "C,C<sub>tr</sub>": r"C,C_{tr}",
}


def _symbol_latex(symbol):
    if symbol in SYMBOL_LATEX:
        return SYMBOL_LATEX[symbol]
    converted = symbol
    converted = converted.replace("<sub>", "_{").replace("</sub>", "}")
    converted = converted.replace("<sup>", "^{").replace("</sup>", "}")
    converted = converted.replace("τ", r"\tau").replace("ρ", r"\rho")
    converted = converted.replace("ν", r"\nu").replace("θ", r"\theta")
    converted = converted.replace("ω", r"\omega").replace("′", "'")
    return converted


def _cards(formulae):
    html = ""
    for name, equation, variables, use in formulae:
        latex = LATEX_EQUATIONS.get(equation, equation)
        rows = "".join(
            f"<tr><th>\\({_symbol_latex(symbol)}\\)</th><td>{meaning}</td><td>{unit}</td></tr>"
            for symbol, meaning, unit in variables
        )
        html += (
            f"<article><h4>{name}</h4><div class='eq'>\\[{latex}\\]</div>"
            f"<table><thead><tr><th>Símbolo</th><th>Corresponde a</th><th>Unidad</th></tr></thead>"
            f"<tbody>{rows}</tbody></table><p class='use'><b>Uso:</b> {use}</p></article>"
        )
    return html


def build_formulary_html(visible_labs):
    body = ""
    for course_index, course in enumerate(FORMULA_CATALOG, 1):
        labs = ""
        for lab in course["labs"]:
            if (course_index, lab["number"]) not in visible_labs:
                continue

            topics = "".join(
                f"<div class='topic'><h3>{title}</h3>{_cards(items)}</div>"
                for title, items in lab["topics"]
            )
            labs += f"<details open><summary>Laboratorio {lab['number']} · {lab['subtitle']}</summary>{topics}</details>"
        if labs:
            body += f"<section><h2>Curso 1 · {course['course']}</h2>{labs}</section>"

    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Formulario de Laboratorio</title>
    <script>
      window.MathJax = {{
        tex: {{inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']]}},
        svg: {{fontCache: 'global'}}
      }};
    </script>
    <script async id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    <style>
    *{{box-sizing:border-box}}body{{font-family:Arial,sans-serif;background:#f3f7fb;color:#102b49;margin:0;padding:18px}}
    header{{position:sticky;top:0;z-index:5;background:linear-gradient(135deg,#07172b,#0878bd);color:white;border-radius:14px;padding:16px 18px;box-shadow:0 8px 22px #07172b26}}
    header b{{font-size:21px}}header span{{display:block;color:#d9f5ff;font-size:12px;margin-top:5px}}
    .version{{display:inline-block;margin-top:8px;padding:3px 8px;border-radius:999px;background:#dff7ea;color:#08724e;font-size:11px;font-weight:800}}
    h2{{font-size:18px;color:#073f6b}}details{{background:white;border:1px solid #cfe1ef;border-radius:13px;margin:12px 0;overflow:hidden}}
    summary{{cursor:pointer;background:#e8f5fd;color:#084f83;font-weight:800;padding:13px 15px}}
    .topic{{padding:4px 13px 11px}}.topic h3{{font-size:14px;color:#08724e;border-bottom:2px solid #d8eee4;padding-bottom:6px}}
    article{{background:white;border:1px solid #d8e6f3;border-left:5px solid #0a75bd;border-radius:11px;padding:14px 16px;margin:12px 0}}
    h4{{font-size:15px;margin:0 0 6px;color:#0a4f86}}
    .eq{{font-size:22px;line-height:1.55;margin:10px 0 14px;padding:12px 10px;background:#f8fbfe;border-radius:8px;text-align:center;overflow-x:auto}}
    .eq mjx-container{{margin:0!important}}table{{width:100%;border-collapse:collapse;font-size:13px}}
    th,td{{padding:7px 8px;border-top:1px solid #e1eaf2;text-align:left;vertical-align:middle}}
    thead th{{color:#53657a;font-size:11px;text-transform:uppercase}}tbody th{{color:#083f6b;white-space:nowrap;font-size:15px}}
    .use{{font-size:12px;color:#53657a}}
    @media(max-width:640px){{body{{padding:10px}}.eq{{font-size:18px}}th,td{{font-size:11px;padding:6px 5px}}}}
    </style></head><body><header><b>📐 Formulario de Laboratorio</b></header>{body}</body></html>'''
