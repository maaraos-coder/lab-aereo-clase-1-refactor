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
    """Abre el formulario en un diálogo nativo de Streamlit.

    Se evita ``window.open`` porque los navegadores pueden bloquear ventanas
    emergentes creadas desde un iframe de ``components.html``.
    """
    visible_labs = {(1, 1), (1, 2)}
    popup_html = build_formulary_html(visible_labs)

    if st.button(
        "📐 Abrir Formulario actualizado · Lab. 1 y 2",
        key="open_diploma_formulary",
        use_container_width=True,
    ):
        st.session_state["show_diploma_formulary"] = True

    if not st.session_state.get("show_diploma_formulary", False):
        return

    @st.dialog("📐 Formulario · Curso 1", width="large")
    def _show_formulary_dialog():
        components.html(
            popup_html,
            height=720,
            scrolling=True,
        )
        if st.button(
            "Cerrar formulario",
            key="close_diploma_formulary",
            use_container_width=True,
        ):
            st.session_state["show_diploma_formulary"] = False
            st.rerun()

    _show_formulary_dialog()


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
