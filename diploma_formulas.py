"""Formulario ordenado con las ecuaciones utilizadas en los Laboratorios 1 y 2."""

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
            "subtitle": "Pérdida de transmisión, placas simples y dobles, ventanas, Rw, C, Ctr y cálculo integrador",
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
                ("6. Diseño integrador del paramento", [
                    ("Transmisión de cada componente", "τ<sub>i,f</sub> = 10<sup>−R<sub>i,f</sub>/10</sup>", [("τ<sub>i,f</sub>","coeficiente de transmisión del componente i en la banda f","—"),("R<sub>i,f</sub>","TL o reducción sonora del componente i en la banda f","dB")], "Convierte por banda las curvas del muro, la ventana y la puerta a magnitudes energéticas."),
                    ("Paramento compuesto por banda", "τ<sub>T,f</sub> = [19,71·τ<sub>m,f</sub> + 2,40·τ<sub>v,f</sub> + 1,89·τ<sub>p,f</sub>]/24,00", [("τ<sub>T,f</sub>","transmisión total en la banda f","—"),("τ<sub>m,f</sub>","transmisión del muro o tabique","—"),("τ<sub>v,f</sub>","transmisión de la ventana","—"),("τ<sub>p,f</sub>","transmisión de la puerta","—")], "Aplica las superficies fijas del ejercicio sala–pasillo; no promedia valores en dB."),
                    ("Curva combinada", "R<sub>T,f</sub> = −10·log<sub>10</sub>(τ<sub>T,f</sub>)", [("R<sub>T,f</sub>","aislamiento combinado del paramento en la banda f","dB"),("τ<sub>T,f</sub>","coeficiente de transmisión total por banda","—")], "Construye la curva combinada que luego se utiliza para calcular Rw, C y Ctr."),
                    ("Criterio del ejercicio", "R<sub>w,total</sub> ≥ 40 dB", [("R<sub>w,total</sub>","índice ponderado del paramento completo","dB")], "Verifica el cumplimiento del paramento de 24,00 m² entre la sala de clases y el pasillo."),
                ]),
            ],
        },
    ],
}]

def _cards(formulae):
    html=""
    for name,equation,variables,use in formulae:
        rows="".join(f"<tr><th>{s}</th><td>{m}</td><td>{u}</td></tr>" for s,m,u in variables)
        html+=(f"<article><h4>{name}</h4><div class='eq'>{equation}</div><table><thead><tr>"
               f"<th>Símbolo</th><th>Corresponde a</th><th>Unidad</th></tr></thead><tbody>{rows}</tbody></table>"
               f"<p class='use'><b>Uso:</b> {use}</p></article>")
    return html

def build_formulary_html(visible_labs):
    body=""
    for course_index,course in enumerate(FORMULA_CATALOG,1):
        labs=""
        for lab in course["labs"]:
            if (course_index,lab["number"]) not in visible_labs:
                continue
            topics="".join(f"<div class='topic'><h3>{title}</h3>{_cards(items)}</div>" for title,items in lab["topics"])
            labs+=f"<details open><summary>Laboratorio {lab['number']} · {lab['subtitle']}</summary>{topics}</details>"
        if labs: body+=f"<section><h2>Curso 1 · {course['course']}</h2>{labs}</section>"
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Formulario Curso 1 · APP 123</title><style>
    *{{box-sizing:border-box}}body{{font-family:Arial,sans-serif;background:#f3f7fb;color:#102b49;margin:0;padding:18px}}header{{position:sticky;top:0;z-index:5;background:linear-gradient(135deg,#07172b,#0878bd);color:white;border-radius:14px;padding:16px 18px}}header b{{font-size:21px}}header span{{display:block;color:#d9f5ff;font-size:12px;margin-top:5px}}.version{{display:inline-block;margin-top:8px;padding:3px 8px;border-radius:999px;background:#dff7ea;color:#08724e;font-size:11px;font-weight:800}}h2{{font-size:18px;color:#073f6b}}details{{background:white;border:1px solid #cfe1ef;border-radius:13px;margin:12px 0;overflow:hidden}}summary{{cursor:pointer;background:#e8f5fd;color:#084f83;font-weight:800;padding:13px 15px}}.topic{{padding:4px 13px 11px}}.topic h3{{font-size:14px;color:#08724e;border-bottom:2px solid #d8eee4;padding-bottom:6px}}article{{border:1px solid #d8e6f3;border-left:5px solid #0a75bd;border-radius:11px;padding:11px 13px;margin:10px 0}}h4{{font-size:14px;margin:0 0 7px;color:#0a4f86}}.eq{{font-size:20px;font-weight:800;line-height:1.55;margin:7px 0 10px}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:6px 7px;border-top:1px solid #e1eaf2;text-align:left;vertical-align:top}}thead th{{color:#53657a;font-size:11px;text-transform:uppercase}}tbody th{{color:#083f6b;white-space:nowrap}}.use{{font-size:12px;color:#53657a}}</style></head><body><header><b>📐 Formulario · Curso 1</b><span>Fórmulas utilizadas en los Laboratorios 1 y 2, ordenadas según la secuencia real del curso</span><span class="version">FORMULARIO ACTUALIZADO · APP 123</span></header>{body}</body></html>'''
