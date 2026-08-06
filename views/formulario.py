"""Vista independiente del Formulario Técnico del Diplomado."""

_LOCAL_NAMES = {
    "run_view",
    "_bind_runtime",
    "_LOCAL_NAMES",
    "_formula_reference_impl",
    "_formula_popup_button_impl",
}


def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value


def _formula_reference_impl():
    """Renderiza el formulario como una página independiente."""
    visible_labs = {(1, 1), (1, 2)}
    html = build_formulary_html(visible_labs)
    components.html(html, height=1200, scrolling=True)


def _formula_popup_button_impl():
    """Muestra un enlace simple que abre el formulario en otra pestaña."""
    st.markdown(
        """
        <a href="?formulas=1" target="_blank" rel="noopener noreferrer"
           style="display:flex;align-items:center;justify-content:center;width:100%;
                  min-height:42px;padding:9px 12px;border-radius:8px;
                  background:#0b4f83;color:#fff !important;border:1px solid #59d4ef;
                  font-weight:700;font-size:14px;text-decoration:none;line-height:1.2;">
            📐 Formulario
        </a>
        """,
        unsafe_allow_html=True,
    )


def run_view(name, runtime, *args, **kwargs):
    """Ejecuta una de las dos vistas públicas del módulo."""
    _bind_runtime(runtime)
    if name == "formula_reference":
        return _formula_reference_impl(*args, **kwargs)
    if name == "formula_popup_button":
        return _formula_popup_button_impl(*args, **kwargs)
    raise KeyError(f"Vista de formulario desconocida: {name}")
