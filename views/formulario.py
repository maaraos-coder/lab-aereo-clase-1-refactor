"""Vista y acceso al Formulario Técnico de Acústica."""

_LOCAL_NAMES = {
    "run_view", "_bind_runtime", "_LOCAL_NAMES",
    "_formula_reference_impl", "_formula_popup_button_impl",
}


def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value


def _formula_reference_impl():
    """Vista de respaldo dentro de la aplicación."""
    header(
        "FORMULARIO DEL DIPLOMADO",
        "Formulario Técnico de Acústica",
        "Las ecuaciones se incorporan por curso y tema una vez validado su contenido técnico.",
    )
    st.info("Usa el botón «📐 Formulario» de la barra lateral para abrir la página completa en otra pestaña.")


def _formula_popup_button_impl():
    """Abre el formulario en una pestaña independiente mediante una ruta real."""
    st.markdown(
        """
        <style>
        a#formulario-tecnico-btn,
        a#formulario-tecnico-btn:link,
        a#formulario-tecnico-btn:visited,
        a#formulario-tecnico-btn:hover,
        a#formulario-tecnico-btn:active,
        a#formulario-tecnico-btn:focus {
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            width:100% !important;
            min-height:42px !important;
            padding:9px 12px !important;
            box-sizing:border-box !important;
            border:1px solid #65d9f3 !important;
            border-radius:8px !important;
            background:#0b659c !important;
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            text-decoration:none !important;
            font-weight:700 !important;
            font-size:14px !important;
            line-height:1.2 !important;
            opacity:1 !important;
            text-shadow:none !important;
        }
        a#formulario-tecnico-btn:hover,
        a#formulario-tecnico-btn:focus {
            background:#087dbd !important;
            border-color:#a7efff !important;
        }
        a#formulario-tecnico-btn span {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            opacity:1 !important;
        }
        </style>
        <a id="formulario-tecnico-btn"
           href="?formulas=1"
           target="_blank"
           rel="noopener noreferrer"
           title="Abrir el formulario técnico en otra pestaña">
            <span>📐&nbsp; Formulario</span>
        </a>
        """,
        unsafe_allow_html=True,
    )


def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    if name == "formula_reference":
        return _formula_reference_impl(*args, **kwargs)
    if name == "formula_popup_button":
        return _formula_popup_button_impl(*args, **kwargs)
    raise KeyError(f"Vista de formulario desconocida: {name}")
