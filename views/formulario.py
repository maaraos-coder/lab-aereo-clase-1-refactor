"""Formulario técnico acumulativo del diplomado.

La vista recibe dependencias compartidas desde ``app.py`` para conservar el
comportamiento existente sin importaciones circulares.
"""

_LOCAL_NAMES = {"run_view", "_bind_runtime", "_VIEWS", "_LOCAL_NAMES",
                "_formula_reference_impl", "_formula_popup_button_impl"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value

def _formula_reference_impl():
    """Fallback reference view; the sidebar button opens the complete floating formulary."""
    header("FORMULARIO DEL DIPLOMADO","Compendio de los dos laboratorios disponibles",
           "Incluye únicamente las fórmulas utilizadas actualmente en los Laboratorios 1 y 2 del Curso 1.")
    st.info("Usa el botón «Abrir Formulario del Diplomado» de la barra lateral.")
    tab1,tab2,tab3,tab4=st.tabs([
        "Recintos y absorción","Transmisión y aislamiento",
        "Placas y sistemas dobles","Evaluación económica",
    ])
    with tab1:
        formula_card("Área de absorción equivalente",r"A=\sum_i \alpha_i S_i",
                     "<b>A</b>: absorción equivalente [m² sabin]<br><b>αᵢ</b>: coeficiente de absorción [-]<br><b>Sᵢ</b>: superficie [m²]",
                     "Para sumar la absorción aportada por las superficies de un recinto.")
        formula_card("Tiempo de reverberación de Sabine",r"T_{60}=0.161\,\frac{V}{A}",
                     "<b>T₆₀</b>: tiempo [s]<br><b>V</b>: volumen [m³]<br><b>A</b>: absorción equivalente [m² sabin]",
                     "Para estimar la reverberación cuando el campo es suficientemente difuso.")
    with tab2:
        formula_card("Coeficiente de transmisión",r"\tau=10^{-R/10}",
                     "<b>τ</b>: coeficiente de transmisión [-]<br><b>R</b>: índice de reducción sonora [dB]",
                     "Para transformar un aislamiento en una fracción de energía transmitida.")
        formula_card("Elemento compuesto",r"\tau_{\mathrm{total}}=\frac{\sum_i S_i\tau_i}{\sum_i S_i}\quad;\quad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
                     "<b>Sᵢ</b>: área de cada elemento [m²]<br><b>τᵢ</b>: transmisión de cada elemento [-]<br><b>Rtotal</b>: reducción compuesta [dB]",
                     "Para muros con puertas, ventanas, rendijas u otros elementos de distinto aislamiento.")
        formula_card("Porcentaje de área débil",r"p_{\mathrm{débil}}=\frac{S_{\mathrm{débil}}}{S_{\mathrm{total}}}\,100",
                     "<b>pdébil</b>: porcentaje [%]<br><b>Sdébil</b>: área débil [m²]<br><b>Stotal</b>: área total [m²]",
                     "Para cuantificar qué parte del cerramiento corresponde al elemento de menor aislamiento.")
        formula_card("Diferencia de nivel simplificada",r"\Delta L=L_{\mathrm{emisor}}-L_{\mathrm{receptor}}",
                     "<b>ΔL</b>: diferencia de nivel [dB]<br><b>L</b>: nivel sonoro [dB]",
                     "Relación didáctica. En evaluación normalizada también intervienen geometría y reverberación.")
    with tab3:
        formula_card("Ley de masa (aproximación)",r"R\approx20\log_{10}(m'f)-47",
                     "<b>R</b>: reducción sonora [dB]<br><b>m′</b>: masa superficial [kg/m²]<br><b>f</b>: frecuencia [Hz]",
                     "Para observar la tendencia ideal de una placa simple fuera de resonancias y coincidencia.")
        formula_card("Rigidez flexional",r"D=\frac{Eh^3}{12(1-\nu^2)}",
                     "<b>D</b>: rigidez [N·m]<br><b>E</b>: módulo de Young [Pa]<br><b>h</b>: espesor [m]<br><b>ν</b>: Poisson [-]",
                     "Paso previo al cálculo de la frecuencia crítica de una placa.")
        formula_card("Frecuencia crítica",r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
                     "<b>fc</b>: frecuencia crítica [Hz]<br><b>c</b>: velocidad del sonido [m/s]<br><b>m′</b>: masa superficial [kg/m²]<br><b>D</b>: rigidez [N·m]",
                     "Para ubicar la zona de coincidencia donde puede caer el aislamiento.")
        formula_card("Resonancia masa–aire–masa",r"f_0\approx60\sqrt{\frac{1}{d}\left(\frac{1}{m'_1}+\frac{1}{m'_2}\right)}",
                     "<b>f₀</b>: resonancia [Hz]<br><b>d</b>: cámara [m]<br><b>m′₁,m′₂</b>: masas superficiales [kg/m²]",
                     "Estimación para sistemas dobles separados por una cámara de aire.")
    with tab4:
        formula_card("Flujo neto anual",r"F_{\mathrm{neto}}=B_{\mathrm{bruto}}-C_{\mathrm{anual}}",
                     "<b>Fneto</b>: flujo anual disponible [$ /año]<br><b>Bbruto</b>: beneficio bruto [$ /año]<br><b>Canual</b>: costos recurrentes [$ /año]",
                     "Es el dinero anual que efectivamente queda para recuperar la inversión.")
        formula_card("Payback",r"\mathrm{Payback}=\frac{I_0}{F_{\mathrm{neto}}}",
                     "<b>I₀</b>: inversión inicial [$]<br><b>Fneto</b>: flujo neto [$ /año]",
                     "Indica cuántos años tarda en recuperarse la inversión.")
        formula_card("Retorno sobre la inversión",r"ROI=\frac{B_{\mathrm{total}}-I_0}{I_0}\,100",
                     "<b>ROI</b>: rentabilidad [%]<br><b>Btotal</b>: beneficio acumulado [$]<br><b>I₀</b>: inversión inicial [$]",
                     "Indica cuánto se ganó o perdió en relación con lo invertido.")


def _formula_popup_button_impl():
    """Open the cumulative Diploma reference without creating a second login session."""
    # El formulario describe el material académico actualmente cargado, no el
    # calendario de publicación. Alumno y docente deben consultar exactamente
    # los mismos dos laboratorios reales del Curso 1.
    visible_labs={(1,1),(1,2)}
    popup=build_formulary_html(visible_labs)
    popup_json=json.dumps(popup,ensure_ascii=False)
    components.html(f"""
    <button id="open-formulas">📐 Abrir Formulario actualizado · Lab. 1 y 2</button>
    <style>body{{margin:0}}button{{width:100%;height:42px;background:#0b4f83;color:white;
    border:1px solid #59d4ef;border-radius:8px;font-weight:700;font-size:13px;cursor:pointer}}
    button:hover{{background:#0878bd;border-color:#8ee9ff}}</style>
    <script>document.getElementById('open-formulas').onclick=()=>{{
      const win=window.open('','formulario_diplomado_app123','popup=yes,width=820,height=880,resizable=yes,scrollbars=yes');
      win.document.open();win.document.write({popup_json});win.document.close();
    }};</script>""",height=48,scrolling=False)
    return
    lab1_formulae=[
        ("Absorción equivalente","A = Σ α<sub>i</sub> · S<sub>i</sub>",[
            ("A","área de absorción acústica equivalente","m² sabin"),
            ("α<sub>i</sub>","coeficiente de absorción de la superficie i","adimensional"),
            ("S<sub>i</sub>","área de la superficie i","m²")]),
        ("Tiempo de reverberación de Sabine","T<sub>60</sub> = 0,161 · V / A",[
            ("T<sub>60</sub>","tiempo para que el nivel sonoro decaiga 60 dB","s"),
            ("V","volumen del recinto","m³"),
            ("A","área de absorción acústica equivalente","m² sabin")]),
        ("Coeficiente de transmisión","τ = 10<sup>−R/10</sup>",[
            ("τ","relación entre potencia sonora transmitida e incidente","adimensional"),
            ("R","índice de reducción sonora del elemento","dB")]),
        ("Elemento compuesto","τ<sub>t</sub> = Σ(S<sub>i</sub>·τ<sub>i</sub>) / ΣS<sub>i</sub><br>R<sub>t</sub> = −10·log<sub>10</sub>(τ<sub>t</sub>)",[
            ("τ<sub>t</sub>","coeficiente de transmisión total del cerramiento","adimensional"),
            ("S<sub>i</sub>","área de cada elemento (muro, puerta o ventana)","m²"),
            ("τ<sub>i</sub>","coeficiente de transmisión de cada elemento","adimensional"),
            ("R<sub>t</sub>","índice de reducción sonora del elemento compuesto","dB")]),
        ("Diferencia de nivel estandarizada","D<sub>nT</sub> = L<sub>1</sub> − L<sub>2</sub> + 10·log<sub>10</sub>(T/T<sub>0</sub>)",[
            ("D<sub>nT</sub>","diferencia de nivel estandarizada entre recintos","dB"),
            ("L<sub>1</sub>","nivel promedio en el recinto emisor","dB"),
            ("L<sub>2</sub>","nivel promedio en el recinto receptor","dB"),
            ("T","tiempo de reverberación medido en el receptor","s"),
            ("T<sub>0</sub>","tiempo de reverberación de referencia; usualmente 0,5 s","s")]),
        ("Ley de masa (aproximación)","R ≈ 20·log<sub>10</sub>(m′·f) − 47",[
            ("R","índice de reducción sonora aproximado","dB"),
            ("m′","masa superficial de la placa","kg/m²"),
            ("f","frecuencia","Hz")]),
        ("Rigidez flexional","D = E·h<sup>3</sup> / [12·(1−ν<sup>2</sup>)]",[
            ("D","rigidez flexional por unidad de ancho","N·m"),
            ("E","módulo de Young del material","Pa"),
            ("h","espesor de la placa","m"),
            ("ν","coeficiente de Poisson","adimensional")]),
        ("Frecuencia crítica","f<sub>c</sub> = c<sup>2</sup>/(2π) · √(m′/D)",[
            ("f<sub>c</sub>","frecuencia crítica o de coincidencia","Hz"),
            ("c","velocidad del sonido en el aire","m/s"),
            ("m′","masa superficial de la placa","kg/m²"),
            ("D","rigidez flexional de la placa","N·m")]),
        ("Resonancia masa–aire–masa","f<sub>0</sub> ≈ 60·√[(1/d)·(1/m′<sub>1</sub>+1/m′<sub>2</sub>)]",[
            ("f<sub>0</sub>","frecuencia de resonancia del sistema doble","Hz"),
            ("d","profundidad de la cámara de aire","m"),
            ("m′<sub>1</sub>, m′<sub>2</sub>","masas superficiales de las dos hojas","kg/m²")]),
        ("Periodo de recuperación","Payback = I<sub>0</sub> / F<sub>neto</sub>",[
            ("I<sub>0</sub>","inversión inicial","$"),
            ("F<sub>neto</sub>","flujo neto anual atribuible a la solución","$/año"),
            ("Payback","tiempo necesario para recuperar la inversión","años")]),
        ("Retorno sobre la inversión","ROI = (B<sub>total</sub> − I<sub>0</sub>) / I<sub>0</sub> · 100",[
            ("B<sub>total</sub>","beneficio económico acumulado en el periodo analizado","$"),
            ("I<sub>0</sub>","inversión inicial","$"),
            ("ROI","retorno sobre la inversión","%")]),
    ]
    lab2_formulae=[
        ("Adaptaciones espectrales ISO","R<sub>w</sub> + C &nbsp;&nbsp;·&nbsp;&nbsp; R<sub>w</sub> + C<sub>tr</sub>",[
            ("R<sub>w</sub>","índice ponderado de reducción sonora del elemento ensayado","dB"),
            ("C","término de adaptación para espectros predominantemente medios y altos","dB"),
            ("C<sub>tr</sub>","término de adaptación para tránsito y espectros con contenido grave","dB")]),
        ("Diferencia de nivel estandarizada","D<sub>nT</sub> = L<sub>1</sub> − L<sub>2</sub> + 10·log<sub>10</sub>(T/T<sub>0</sub>)",[
            ("D<sub>nT</sub>","diferencia de nivel estandarizada entre recintos","dB"),
            ("L<sub>1</sub>","nivel promedio en el recinto emisor","dB"),
            ("L<sub>2</sub>","nivel promedio en el recinto receptor","dB"),
            ("T","tiempo de reverberación medido en el recinto receptor","s"),
            ("T<sub>0</sub>","tiempo de reverberación de referencia; usualmente 0,5 s en viviendas","s")]),
        ("Descriptor adaptado del caso","D<sub>nT,A</sub> = D<sub>nT,w</sub> + C",[
            ("D<sub>nT,A</sub>","diferencia de nivel estandarizada ponderada A para el espectro considerado","dB"),
            ("D<sub>nT,w</sub>","valor único ponderado de la diferencia de nivel estandarizada","dB"),
            ("C","término de adaptación espectral correspondiente","dB")]),
        ("Paso simplificado de elemento a edificio","D<sub>nT,A</sub> ≈ R<sub>comp,A</sub> + 10·log<sub>10</sub>(0,32·V/S) − L<sub>obra</sub>",[
            ("D<sub>nT,A</sub>","diferencia de nivel estandarizada adaptada estimada","dB"),
            ("R<sub>comp,A</sub>","reducción sonora adaptada del elemento compuesto","dB"),
            ("V","volumen del recinto receptor","m³"),
            ("S","área del elemento separador","m²"),
            ("L<sub>obra</sub>","pérdida estimada por montaje, encuentros y ejecución","dB")]),
        ("Aislamiento del cerramiento compuesto","τ<sub>comp</sub> = Σ(S<sub>i</sub>·10<sup>−R<sub>i</sub>/10</sup>)/ΣS<sub>i</sub><br>R<sub>comp</sub> = −10·log<sub>10</sub>(τ<sub>comp</sub>)",[
            ("τ<sub>comp</sub>","coeficiente de transmisión del cerramiento completo","adimensional"),
            ("S<sub>i</sub>","área de cada componente, por ejemplo muro o puerta","m²"),
            ("R<sub>i</sub>","índice de reducción sonora de cada componente","dB"),
            ("R<sub>comp</sub>","índice de reducción sonora del conjunto","dB")]),
    ]

    def build_cards(formulae):
        cards=""
        for name,equation,variables in formulae:
            rows="".join(
                f"<tr><th>{symbol}</th><td>{meaning}</td><td>{unit}</td></tr>"
                for symbol,meaning,unit in variables)
            cards+=(
                f"<article><h3>{name}</h3><div class='eq'>{equation}</div>"
                f"<table><thead><tr><th>Símbolo</th><th>Corresponde a</th><th>Unidad</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></article>")
        return cards

    cards=(
        "<section><div class='lab-title'><b>Laboratorio 1</b>"
        "<span>Fundamentos, recintos, transmisión, placas y evaluación económica</span></div>"
        + build_cards(lab1_formulae) + "</section>"
    )
    show_lab2=st.session_state.get("role")=="Docente" or ACTIVE_LAB==2
    if show_lab2:
        cards+=(
            "<section><div class='lab-title lab2'><b>Laboratorio 2</b>"
            "<span>CES–MINVU, descriptores de edificio, ISO 12354 y casos profesionales</span></div>"
            + build_cards(lab2_formulae) + "</section>"
        )
    popup=f"""<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>
    <style>body{{font-family:Arial,sans-serif;background:#f4f8fc;color:#102b49;margin:0;padding:18px}}
    header{{position:sticky;top:0;background:linear-gradient(135deg,#07172b,#0878bd);color:white;
    border-radius:14px;padding:16px 18px;box-shadow:0 8px 22px #07172b33}}header b{{font-size:20px}}
    .lab-title{{display:flex;flex-direction:column;gap:3px;background:#e8f5fd;border:1px solid #b9def3;
    border-radius:12px;padding:12px 14px;margin:16px 0 10px;color:#084f83}}.lab-title b{{font-size:17px}}
    .lab-title span{{font-size:12px;color:#536b82}}.lab-title.lab2{{background:#eef8f2;border-color:#bfe3cf;color:#08724e}}
    article{{background:white;border:1px solid #d8e6f3;border-left:5px solid #0a75bd;
    border-radius:12px;padding:12px 14px;margin:10px 0}}h3{{font-size:14px;margin:0 0 8px;color:#0a4f86}}
    .eq{{font-size:20px;font-weight:800;line-height:1.55;margin-bottom:10px}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:6px 7px;border-top:1px solid #e1eaf2;text-align:left;vertical-align:top}}
    thead th{{color:#53657a;font-size:11px;text-transform:uppercase}}tbody th{{color:#083f6b;white-space:nowrap}}
    small{{display:block;margin-top:7px;color:#60718a}}</style>
    </head><body><header><b>📐 {title}</b><br><small style='color:#d9f5ff'>Formulario acumulativo del curso, organizado por laboratorio</small></header>{cards}</body></html>"""
    popup_json=json.dumps(popup,ensure_ascii=False)
    components.html(f"""
    <button id="open-formulas">📐 Abrir fórmulas</button>
    <style>body{{margin:0}}button{{width:100%;height:42px;background:#0b4f83;color:white;
    border:1px solid #59d4ef;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer}}
    button:hover{{background:#0878bd;border-color:#8ee9ff}}</style>
    <script>document.getElementById('open-formulas').onclick=()=>{{
      const win=window.open('','formulario_laboratorio','popup=yes,width=720,height=840,resizable=yes,scrollbars=yes');
      win.document.open();win.document.write({popup_json});win.document.close();
    }};</script>""",height=48,scrolling=False)


_VIEWS = {
    "formula_reference": _formula_reference_impl,
    "formula_popup_button": _formula_popup_button_impl,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
