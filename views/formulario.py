"""Vista independiente del Formulario Técnico del Diplomado.

Conserva el formulario acumulativo existente construido en app.py y añade,
sin reemplazarlo, el bloque de ecuaciones del Curso 2 · Laboratorio 2.
"""

_LOCAL_NAMES = {
    "run_view",
    "_bind_runtime",
    "_LOCAL_NAMES",
    "_formula_reference_impl",
    "_formula_popup_button_impl",
    "_base_build_formulary_html",
    "_append_c2l2_formulas",
    "build_formulary_html",
}

_base_build_formulary_html = None


def _bind_runtime(runtime):
    global _base_build_formulary_html

    if _base_build_formulary_html is None:
        candidate = runtime.get("build_formulary_html")
        if callable(candidate) and candidate is not build_formulary_html:
            _base_build_formulary_html = candidate

    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value


def _append_c2l2_formulas(html):
    section = r'''
    <section id="curso2-lab2-formulas" style="
        margin:32px 20px 42px;
        padding:24px;
        border:1px solid #b9d7ee;
        border-radius:20px;
        background:linear-gradient(180deg,#f8fbff 0%,#eef7ff 100%);
        color:#10233c;
        font-family:Arial,Helvetica,sans-serif;
    ">
      <div style="font-size:12px;font-weight:800;letter-spacing:.09em;color:#0b6fa4;margin-bottom:8px">
        CURSO 2 · LABORATORIO 2
      </div>
      <h1 style="margin:0 0 8px;font-size:26px;color:#0b3558">
        Ruido de impacto · ISO 717-2 · Revestimientos · Instalaciones
      </h1>
      <p style="margin:0 0 22px;line-height:1.55;color:#496277">
        Ecuaciones utilizadas en las Etapas 1–10, con definición de símbolos y lectura práctica.
      </p>

      <style>
        #curso2-lab2-formulas .eq-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
        #curso2-lab2-formulas .eq-card{background:#fff;border:1px solid #d8e5ef;border-radius:15px;padding:16px 17px}
        #curso2-lab2-formulas .eq-title{font-size:15px;font-weight:800;color:#0b4f83;margin-bottom:10px}
        #curso2-lab2-formulas .eq{font-family:"Times New Roman",serif;font-size:21px;text-align:center;margin:10px 0 12px;padding:11px;border-radius:10px;background:#f7fbff;overflow-x:auto}
        #curso2-lab2-formulas .vars{font-size:13px;line-height:1.55;color:#40576b}
        #curso2-lab2-formulas .use{margin-top:9px;padding-top:9px;border-top:1px solid #e7eef4;font-size:13px;line-height:1.5;color:#163d5c}
        #curso2-lab2-formulas .group-title{grid-column:1/-1;margin:20px 0 0;padding:10px 13px;border-left:4px solid #0b84c6;background:#e8f5fc;border-radius:8px;font-size:17px;font-weight:800;color:#0b4f83}
        #curso2-lab2-formulas .note{grid-column:1/-1;background:#fff8e8;border:1px solid #f1d397;border-radius:12px;padding:13px 15px;font-size:13px;line-height:1.5;color:#77520b}
        @media(max-width:760px){#curso2-lab2-formulas .eq-grid{grid-template-columns:1fr}}
      </style>

      <div class="eq-grid">

        <div class="group-title">A · Magnitudes de impacto y medición en terreno</div>

        <div class="eq-card">
          <div class="eq-title">Predicción del nivel final de impacto</div>
          <div class="eq">L<sub>n,final</sub>(f) = L<sub>n,0</sub>(f) − ΔL<sub>n</sub>(f)</div>
          <div class="vars"><b>L<sub>n,0</sub>(f)</b>: nivel base [dB]<br><b>ΔL<sub>n</sub>(f)</b>: reducción prevista [dB]<br><b>L<sub>n,final</sub>(f)</b>: espectro predicho [dB]</div>
          <div class="use">Conecta la predicción del Laboratorio 1 con la ponderación del Laboratorio 2.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Área de absorción equivalente</div>
          <div class="eq">A ≈ 0,16 · V / T</div>
          <div class="vars"><b>A</b>: absorción equivalente [m²]<br><b>V</b>: volumen [m³]<br><b>T</b>: tiempo de reverberación [s]</div>
          <div class="use">Relaciona la reverberación medida con la absorción equivalente del recinto receptor.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Nivel normalizado de impactos en edificio</div>
          <div class="eq">L′<sub>n</sub> = L<sub>i</sub> + 10 log<sub>10</sub>(A/A<sub>0</sub>)</div>
          <div class="vars"><b>L<sub>i</sub></b>: nivel de impacto medido [dB]<br><b>A</b>: absorción equivalente [m²]<br><b>A<sub>0</sub></b>: 10 m²</div>
          <div class="use">Se usa cuando el criterio se expresa respecto de absorción equivalente.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Nivel estandarizado por reverberación</div>
          <div class="eq">L′<sub>nT</sub> = L<sub>i</sub> − 10 log<sub>10</sub>(T/T<sub>0</sub>)</div>
          <div class="vars"><b>T</b>: reverberación medida [s]<br><b>T<sub>0</sub></b>: tiempo de referencia [s]</div>
          <div class="use">Se usa cuando el descriptor está definido respecto de un tiempo de reverberación de referencia.</div>
        </div>

        <div class="group-title">B · ISO 717-2 · Construcción de L<sub>n,w</sub></div>

        <div class="eq-card">
          <div class="eq-title">Desviación desfavorable</div>
          <div class="eq">d<sub>i</sub> = max[0, L<sub>n,i</sub> − L<sub>ref,i</sub>]</div>
          <div class="vars"><b>d<sub>i</sub></b>: desviación desfavorable [dB]</div>
          <div class="use">Solo penaliza cuando el nivel de impacto queda por encima de la referencia.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Criterio de suma</div>
          <div class="eq">Σ d<sub>i</sub> ≤ 32 dB</div>
          <div class="vars">Se aplica a las 16 bandas de tercio de octava usadas en la ponderación.</div>
          <div class="use">La posición límite es la más baja que cumple; 1 dB más abajo debe superar 32 dB.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Lectura del número único</div>
          <div class="eq">L<sub>n,w</sub> = L<sub>ref,límite</sub>(500 Hz)</div>
          <div class="vars"><b>L<sub>n,w</sub></b>: nivel normalizado ponderado de impactos [dB]</div>
          <div class="use">Se lee en 500 Hz una vez encontrada la posición límite.</div>
        </div>

        <div class="group-title">C · Suma energética y términos espectrales</div>

        <div class="eq-card">
          <div class="eq-title">Suma energética</div>
          <div class="eq">L<sub>n,sum</sub> = 10 log<sub>10</sub>[ Σ 10<sup>L<sub>n,i</sub>/10</sup> ]</div>
          <div class="vars"><b>L<sub>n,sum</sub></b>: suma energética global [dB]</div>
          <div class="use">Los dB no se suman aritméticamente: primero se convierten a energía.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Término C<sub>I</sub></div>
          <div class="eq">C<sub>I</sub> = L<sub>n,sum(100–2500)</sub> − 15 − L<sub>n,w</sub></div>
          <div class="vars"><b>C<sub>I</sub></b>: término de adaptación espectral [dB]</div>
          <div class="use">Complementa L<sub>n,w</sub>; no representa una mejora física.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Término C<sub>I,50–2500</sub></div>
          <div class="eq">C<sub>I,50–2500</sub> = L<sub>n,sum(50–2500)</sub> − 15 − L<sub>n,w</sub></div>
          <div class="vars">Añade 50, 63 y 80 Hz a la suma energética.</div>
          <div class="use">Permite visualizar información grave adicional.</div>
        </div>

        <div class="group-title">D · Revestimientos · ΔL(f) y ΔL<sub>w</sub></div>

        <div class="eq-card">
          <div class="eq-title">Piso de referencia tratado</div>
          <div class="eq">L<sub>n,r</sub>(f) = L<sub>n,r,0</sub>(f) − ΔL(f)</div>
          <div class="vars"><b>L<sub>n,r,0</sub>(f)</b>: referencia sin revestimiento<br><b>ΔL(f)</b>: reducción por banda<br><b>L<sub>n,r</sub>(f)</b>: referencia tratada</div>
          <div class="use">Primero se modifica la curva por frecuencia y luego se vuelve a ponderar.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Reducción ponderada del revestimiento</div>
          <div class="eq">ΔL<sub>w</sub> = L<sub>n,r,0,w</sub> − L<sub>n,r,w</sub> = 78 − L<sub>n,r,w</sub></div>
          <div class="vars"><b>L<sub>n,r,0,w</sub></b>: 78 dB<br><b>L<sub>n,r,w</sub></b>: referencia tratada ponderada<br><b>ΔL<sub>w</sub></b>: reducción ponderada</div>
          <div class="use">ΔL<sub>w</sub> no es el promedio de ΔL(f).</div>
        </div>

        <div class="note"><b>78 dB:</b> valor ponderado del piso pesado de referencia usado por ISO 717-2; no representa automáticamente una losa real del proyecto.</div>

        <div class="group-title">E · Bomba · excitación y aislamiento vibratorio</div>

        <div class="eq-card">
          <div class="eq-title">Frecuencia de excitación</div>
          <div class="eq">f<sub>e</sub> = n / 60</div>
          <div class="vars"><b>f<sub>e</sub></b>: frecuencia [Hz]<br><b>n</b>: velocidad [rpm]</div>
          <div class="use">Caso del laboratorio: 1450 rpm → f<sub>e</sub> ≈ 24,17 Hz.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Frecuencia natural masa–resorte</div>
          <div class="eq">f<sub>n</sub> = (1/2π) √(k<sub>t</sub>/m)</div>
          <div class="vars"><b>k<sub>t</sub></b>: rigidez total [N/m]<br><b>m</b>: masa [kg]</div>
          <div class="use">Relaciona las propiedades del montaje con la excitación de la máquina.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Razón de frecuencias</div>
          <div class="eq">r = f<sub>e</sub> / f<sub>n</sub></div>
          <div class="vars"><b>r</b>: razón adimensional</div>
          <div class="use">r≈1: resonancia · 1&lt;r≤√2: transición · r&gt;√2: región de aislamiento ideal.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Transmisibilidad de fuerza</div>
          <div class="eq">T<sub>F</sub> = √{ [1+(2ζr)<sup>2</sup>] / [(1−r<sup>2</sup>)<sup>2</sup>+(2ζr)<sup>2</sup>] }</div>
          <div class="vars"><b>T<sub>F</sub></b>: transmisibilidad [-]<br><b>ζ</b>: amortiguamiento [-]<br><b>r</b>: razón de frecuencias [-]</div>
          <div class="use">T<sub>F</sub>&lt;1 indica menor fuerza transmitida por la base en el modelo ideal.</div>
        </div>

        <div class="eq-card">
          <div class="eq-title">Fuerza transmitida ideal</div>
          <div class="eq">%F<sub>trans</sub> = 100 · T<sub>F</sub></div>
          <div class="vars">Convierte la transmisibilidad a porcentaje.</div>
          <div class="use">Facilita la interpretación docente y la comparación entre montajes.</div>
        </div>

        <div class="note"><b>Camino paralelo:</b> una buena r y una baja T<sub>F</sub> solo describen la base. Una tubería rígida puede puentear el aislamiento: <b>bomba → tubería → soporte → estructura</b>.</div>

      </div>
    </section>
    '''

    if not isinstance(html, str):
        return html
    if "</body>" in html:
        return html.replace("</body>", section + "</body>", 1)
    return html + section


def build_formulary_html(visible_labs):
    if callable(_base_build_formulary_html):
        base_html = _base_build_formulary_html(visible_labs)
    else:
        base_html = '<!doctype html><html><head><meta charset="utf-8"><title>Formulario</title></head><body></body></html>'
    return _append_c2l2_formulas(base_html)


def _formula_reference_impl():
    visible_labs = {(1, 1), (1, 2)}
    html = build_formulary_html(visible_labs)
    components.html(html, height=1600, scrolling=True)


def _formula_popup_button_impl():
    st.markdown(
        '''
        <a href="?formulas=1" target="_blank" rel="noopener noreferrer"
           style="display:flex;align-items:center;justify-content:center;width:100%;
                  min-height:42px;padding:9px 12px;border-radius:8px;
                  background:#0b4f83;color:#fff !important;border:1px solid #59d4ef;
                  font-weight:700;font-size:14px;text-decoration:none;line-height:1.2;">
            📐 Formulario
        </a>
        ''',
        unsafe_allow_html=True,
    )


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    if name == "formula_reference":
        return _formula_reference_impl(*args, **kwargs)
    if name == "formula_popup_button":
        return _formula_popup_button_impl(*args, **kwargs)
    raise KeyError(f"Vista de formulario desconocida: {name}")
