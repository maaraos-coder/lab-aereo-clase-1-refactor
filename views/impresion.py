"""Vista de impresión visual de los laboratorios.

Renderiza las etapas activas con el mismo motor de Streamlit, pero elimina la
navegación, los controles interactivos y los estados personales. El usuario
puede guardar la página como PDF desde el diálogo de impresión del navegador.
"""
from __future__ import annotations

import html


def _print_css(lab_number: int) -> str:
    return f"""
    <style>
    /* Página de impresión: contenido completo y sin interfaz de aplicación. */
    [data-testid="stSidebar"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stMainMenu"],
    footer {{ display:none !important; }}

    .stApp {{ background:#ffffff !important; }}
    .main .block-container {{
        max-width: 1120px !important;
        padding: 1.2rem 2rem 4rem !important;
    }}

    /* Se ocultan los controles, pero se conservan resultados, gráficos y texto. */
    [data-testid="stSlider"],
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stRadio"],
    [data-testid="stCheckbox"],
    [data-testid="stTextInput"],
    [data-testid="stTextArea"],
    [data-testid="stNumberInput"],
    [data-testid="stFileUploader"],
    [data-testid="stDataEditor"],
    [data-testid="stButton"],
    [data-testid="stDownloadButton"],
    [data-testid="stLinkButton"],
    div[data-baseweb="select"],
    button[kind="secondary"],
    button[kind="primary"] {{ display:none !important; }}

    /* En impresión deben verse todas las pestañas y expandibles. */
    [data-baseweb="tab-list"] {{ display:none !important; }}
    [data-baseweb="tab-panel"] {{ display:block !important; opacity:1 !important; }}
    [data-testid="stExpander"] details {{ open: true; }}
    [data-testid="stExpander"] summary {{ display:none !important; }}
    [data-testid="stExpanderDetails"] {{ display:block !important; }}

    /* Evita cortes incómodos. */
    .print-stage {{
        break-before: page;
        page-break-before: always;
        padding-top: .2rem;
    }}
    .print-stage:first-of-type {{ break-before:auto; page-break-before:auto; }}
    img, svg, canvas, [data-testid="stPlotlyChart"], table {{
        max-width:100% !important;
        break-inside:avoid;
        page-break-inside:avoid;
    }}
    h1,h2,h3,h4,.section-band,.formula-card,.worked-example,.good,.warn,.info-box {{
        break-after:avoid;
        page-break-after:avoid;
    }}
    .element-container {{ break-inside:auto; }}

    .print-cover {{
        min-height: 78vh;
        display:flex;
        flex-direction:column;
        justify-content:center;
        padding:2.2rem 2.5rem;
        border-radius:22px;
        background:linear-gradient(135deg,#082945 0%,#0b5b91 58%,#10a7d2 100%);
        color:#fff;
        margin-bottom:2rem;
    }}
    .print-cover .eyebrow {{font-size:.82rem;letter-spacing:.16em;font-weight:800;color:#79e7ff;}}
    .print-cover h1 {{font-size:2.55rem;line-height:1.08;margin:.85rem 0 .6rem;color:#fff;}}
    .print-cover h2 {{font-size:1.25rem;font-weight:500;color:#eaf8ff;margin:0;}}
    .print-cover p {{margin-top:1.5rem;color:#eaf8ff;max-width:760px;}}
    .print-note {{
        background:#eaf5ff;border:1px solid #9ec9e8;border-radius:10px;
        padding:.8rem 1rem;margin:1rem 0 1.5rem;color:#0b3e68;
    }}
    .print-action {{
        position:sticky;top:.5rem;z-index:9999;display:flex;justify-content:flex-end;
        margin-bottom:.7rem;
    }}
    @media print {{
        @page {{ size:A4; margin:12mm 11mm 14mm; }}
        .print-action,.print-note {{ display:none !important; }}
        .main .block-container {{ max-width:none !important;padding:0 !important; }}
        .print-cover {{ min-height:250mm;border-radius:0;break-after:page;page-break-after:always; }}
        body {{ -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important; }}
    }}
    </style>
    """


def render_print_view(runtime: dict, lab_number: int) -> None:
    """Renderiza todas las etapas del laboratorio con apariencia de alumno."""
    st = runtime["st"]
    components = runtime["components"]
    stage_functions = runtime["LAB_STAGE_FUNCTIONS"][lab_number]
    stage_titles = runtime["LAB_STAGE_TITLES"][lab_number]

    # Estado neutro: evita leer o mostrar intentos y resultados personales.
    st.session_state["print_mode"] = True
    st.session_state["role"] = "Alumno"
    st.session_state["access"] = True
    st.session_state["user_key"] = "print-preview"
    st.session_state["user_name"] = "Vista alumno"
    st.session_state["active_lab"] = lab_number
    runtime["ACTIVE_LAB"] = lab_number
    runtime["CLASS_ID"] = runtime["LABORATORIES"][lab_number]["id"]
    runtime["CLASS_NUMBER"] = lab_number

    # La exportación visual nunca escribe progreso ni consulta datos personales.
    runtime["_supabase"] = lambda: None
    runtime["save_user_progress"] = lambda *args, **kwargs: None
    runtime["load_user_progress"] = lambda *args, **kwargs: None

    st.markdown(_print_css(lab_number), unsafe_allow_html=True)

    title = {
        1: "Fundamentos del aislamiento acústico",
        2: "Modelos de predicción del aislamiento acústico",
    }[lab_number]
    st.markdown(
        f"""
        <section class="print-cover">
          <div class="eyebrow">DIPLOMADO EN ACÚSTICA APLICADA A LA EDIFICACIÓN</div>
          <h1>Laboratorio {lab_number}</h1>
          <h2>{html.escape(str(title))}</h2>
          <p>Apunte visual generado desde la vista del alumno. Conserva ecuaciones, imágenes,
          tablas, gráficos y el estado de referencia de las actividades interactivas.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="print-note"><b>Cómo guardar:</b> usa el botón “Imprimir / Guardar PDF”, '
        'elige <b>Guardar como PDF</b>, activa los gráficos de fondo y usa escala 100 %.</div>',
        unsafe_allow_html=True,
    )
    components.html(
        """
        <div style="display:flex;justify-content:flex-end">
          <button onclick="window.parent.print()" style="background:#0b5f98;color:white;border:1px solid #63d6f2;border-radius:9px;padding:10px 18px;font-weight:700;cursor:pointer">🖨️ Imprimir / Guardar PDF</button>
        </div>
        """,
        height=55,
    )

    for index, stage_fn in enumerate(stage_functions):
        prefix, stage_title = stage_titles[index]
        st.markdown(
            f'<div class="print-stage"><div style="font-size:.76rem;letter-spacing:.12em;'
            f'font-weight:800;color:#0b74b5">LABORATORIO {lab_number}</div>'
            f'<h1 style="margin:.15rem 0 1rem;color:#0a3559">{html.escape(prefix)} - '
            f'{html.escape(stage_title)}</h1></div>',
            unsafe_allow_html=True,
        )
        try:
            stage_fn()
        except Exception as exc:
            # Una etapa no debe impedir imprimir las demás. El mensaje permite
            # identificar el punto que requiere una adaptación específica.
            st.warning(f"Esta etapa no pudo renderizarse completamente en modo impresión: {exc}")

    components.html(
        """
        <script>
        // Da tiempo a Plotly, KaTeX e imágenes para completar su render.
        setTimeout(() => {
          const doc = window.parent.document;
          doc.querySelectorAll('details').forEach(el => el.open = true);
        }, 1800);
        </script>
        """,
        height=0,
    )
