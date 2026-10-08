"""Etapa 3 · Curso 4 Laboratorio 2: niveles de potencia sonora de maquinaria."""

import math
import unicodedata
from labs.curso4_laboratorio_1 import BS_PLANT

OCTAVE_LABELS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]
A_CORR=[-39.4,-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0]
REPORT_BANDS=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"]
ADENDA_A_CORR=[-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0,-1.1]

ADENDA2_SOURCES={
    "Adenda 2 · Minicargador · C.4 ítem 14":{
        "bands":[68,67,63,62,62,61,54,47],"laeq10":67,"table":"C.4","ref":"14",
        "page":"Adenda 2 · Tabla 13/14/16/17","activity":"Movimiento de tierra / obra gruesa / urbanización / terminaciones",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Retroexcavadora · C.2 ítem 8":{
        "bands":[74,66,64,64,63,60,59,50],"laeq10":68,"table":"C.2","ref":"8",
        "page":"Adenda 2 · Tabla 13/14/16","activity":"Movimiento de tierra / obra gruesa / urbanización",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Excavadora · C.2 ítem 23":{
        "bands":[79,81,68,69,66,65,61,52],"laeq10":73,"table":"C.2","ref":"23",
        "page":"Adenda 2 · Tabla 13","activity":"Movimiento de tierra",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Rodillo compactador · C.2 ítem 40":{
        "bands":[82,78,67,71,67,64,60,57],"laeq10":73,"table":"C.2","ref":"40",
        "page":"Adenda 2 · Tabla 14/16/18","activity":"Obra gruesa / urbanización / IMIV",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Camión mixer + bomba · C.4 ítem 32":{
        "bands":[73,73,77,76,72,70,65,62],"laeq10":78,"table":"C.4","ref":"32",
        "page":"Adenda 2 · Tabla 14/16/18","activity":"Obra gruesa / urbanización / IMIV",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Grúa pluma · C.4 ítem 46":{
        "bands":[78,69,67,64,62,57,49,40],"laeq10":67,"table":"C.4","ref":"46",
        "page":"Adenda 2 · Tabla 15","activity":"Obra gruesa en altura",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Vibrador de inmersión · C.4 ítem 34":{
        "bands":[62,70,70,64,62,61,59,56],"laeq10":69,"table":"C.4","ref":"34",
        "page":"Adenda 2 · Tabla 15/18","activity":"Obra gruesa en altura / IMIV",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Motoniveladora · consultor":{
        "bands":[72,75,67,59,60,56,49,44],"laeq10":65,"table":"Consultor","ref":"—",
        "page":"Adenda 2 · Tabla 16","activity":"Urbanización",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Alzahombre · C.4 ítem 57":{
        "bands":[78,76,62,63,60,59,58,49],"laeq10":67,"table":"C.4","ref":"57",
        "page":"Adenda 2 · Tabla 17","activity":"Terminaciones",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
    "Adenda 2 · Cango · C.1 ítem 8":{
        "bands":[77,72,73,69,68,66,64,60],"laeq10":74,"table":"C.1","ref":"8",
        "page":"Adenda 2 · Tabla 18","activity":"Obras IMIV",
        "power":"—","size":"—","metric":"NPSeq","band_labels":REPORT_BANDS,"a_corr":ADENDA_A_CORR,
    },
}

SOURCE_CATALOG={**BS_PLANT,**ADENDA2_SOURCES}

def _norm(value):
    text=str(value or "").strip().lower()
    text="".join(ch for ch in unicodedata.normalize("NFD",text) if unicodedata.category(ch)!="Mn")
    for token in ("camion ","camión ","maquina ","máquina ","equipo "):
        text=text.replace(token,token)
    return " ".join(text.split())

def _suggest_bs(project_name):
    n=_norm(project_name)
    aliases={
        "minicargador":"Adenda 2 · Minicargador · C.4 ítem 14",
        "retroexcavadora":"Adenda 2 · Retroexcavadora · C.2 ítem 8",
        "excavadora":"Adenda 2 · Excavadora · C.2 ítem 23",
        "rodillo compactador":"Adenda 2 · Rodillo compactador · C.2 ítem 40",
        "camion mixer + bomba hormigon":"Adenda 2 · Camión mixer + bomba · C.4 ítem 32",
        "grua pluma":"Adenda 2 · Grúa pluma · C.4 ítem 46",
        "vibrador de inmersion":"Adenda 2 · Vibrador de inmersión · C.4 ítem 34",
        "motoniveladora":"Adenda 2 · Motoniveladora · consultor",
        "alzahombre":"Adenda 2 · Alzahombre · C.4 ítem 57",
        "cango":"Adenda 2 · Cango · C.1 ítem 8",
        "excavadora hidraulica":"Excavadora hidráulica",
        "cargador frontal":"Cargador frontal",
        "camion tolva":"Camión tolva articulado",
        "tolva":"Camión tolva articulado",
        "rodillo":"Rodillo vibratorio",
        "rodillo vibratorio":"Rodillo vibratorio",
        "mixer":"Camión mixer",
        "camion mixer":"Camión mixer",
        "bomba de hormigon":"Bomba de hormigón",
        "bomba hormigon":"Bomba de hormigón",
        "grua torre":"Grúa torre",
        "vibrador":"Vibrador de inmersión",
        "manipulador telescopico":"Manipulador telescópico",
        "martillo hidraulico":"Martillo hidráulico",
        "martillo neumatico":"Martillo neumático",
        "sierra de corte":"Sierra de corte de hormigón",
        "generador":"Generador diésel",
        "generador diesel":"Generador diésel",

    }
    if n in aliases:
        return aliases[n]
    for key,val in aliases.items():
        if key in n or n in key:
            return val
    for name in SOURCE_CATALOG:
        if _norm(name)==n:
            return name
    return "Seleccionar referencia BS"

def _calc(item):
    lp=list(item["bands"])
    lw=[v+28.0 for v in lp]
    a_corr=item.get("a_corr",A_CORR)
    lwa_bands=[v+a for v,a in zip(lw,a_corr)]
    lwa_spec=10*math.log10(sum(10**(v/10) for v in lwa_bands))
    lwa_global=item["laeq10"]+28.0
    return lp,lw,lwa_bands,lwa_spec,lwa_global

def _adenda2_machines():
    """Maquinaria de construcción utilizada en los escenarios 1–3 de la Adenda 2."""
    return [
        {"Máquina / equipo":"Minicargador","Cantidad":1,"Etapa asociada":"Escenario 1 · Movimiento de tierra"},
        {"Máquina / equipo":"Retroexcavadora","Cantidad":1,"Etapa asociada":"Escenario 1 · Movimiento de tierra"},
        {"Máquina / equipo":"Excavadora","Cantidad":1,"Etapa asociada":"Escenario 1 · Movimiento de tierra"},

        {"Máquina / equipo":"Rodillo compactador","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa suelo"},
        {"Máquina / equipo":"Minicargador","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa suelo"},
        {"Máquina / equipo":"Retroexcavadora","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa suelo"},
        {"Máquina / equipo":"Camión mixer + bomba hormigón","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa suelo"},

        {"Máquina / equipo":"Grúa pluma","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa altura"},
        {"Máquina / equipo":"Vibrador de inmersión","Cantidad":1,"Etapa asociada":"Escenario 2 · Obra gruesa altura"},

        {"Máquina / equipo":"Rodillo compactador","Cantidad":1,"Etapa asociada":"Escenario 2 · Urbanización"},
        {"Máquina / equipo":"Minicargador","Cantidad":1,"Etapa asociada":"Escenario 2 · Urbanización"},
        {"Máquina / equipo":"Retroexcavadora","Cantidad":1,"Etapa asociada":"Escenario 2 · Urbanización"},
        {"Máquina / equipo":"Motoniveladora","Cantidad":1,"Etapa asociada":"Escenario 2 · Urbanización"},
        {"Máquina / equipo":"Camión mixer + bomba hormigón","Cantidad":1,"Etapa asociada":"Escenario 2 · Urbanización"},

        {"Máquina / equipo":"Minicargador","Cantidad":1,"Etapa asociada":"Escenario 2 · Terminaciones"},
        {"Máquina / equipo":"Alzahombre","Cantidad":1,"Etapa asociada":"Escenario 2 · Terminaciones"},

        {"Máquina / equipo":"Cango","Cantidad":1,"Etapa asociada":"Escenario 3 · Obras IMIV"},
        {"Máquina / equipo":"Camión mixer + bomba hormigón","Cantidad":1,"Etapa asociada":"Escenario 3 · Obras IMIV"},
        {"Máquina / equipo":"Vibrador de inmersión","Cantidad":1,"Etapa asociada":"Escenario 3 · Obras IMIV"},
        {"Máquina / equipo":"Rodillo compactador","Cantidad":1,"Etapa asociada":"Escenario 3 · Obras IMIV"},
    ]


def _render_teacher_pauta(st,pd):
    if st.session_state.get("role")!="Docente":
        return

    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                padding:16px 18px;background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.8rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">
        VISTA DOCENTE · ADENDA 2
      </div>
      <div style="font-size:1.04rem;font-weight:900;color:#173b53;margin:.25rem 0">
        Fuentes y niveles de referencia del último informe de ruido
      </div>
      <div style="color:#526f80;line-height:1.5">
        Los valores siguientes corresponden al Anexo 05 · Estudio Ruido y Vibraciones,
        versión 02 (Adenda 2, 23-09-2026). Alumno y Proyección Zoom deben desarrollar
        la búsqueda y conversión sin ver esta solución.
      </div>
    </div>
    """,unsafe_allow_html=True)

    report_sources=[
        ("Escenario 1 · Movimiento de tierra","Minicargador","C4","14",[68,67,63,62,62,61,54,47],67),
        ("Escenario 1 · Movimiento de tierra","Retroexcavadora","C2","8",[74,66,64,64,63,60,59,50],68),
        ("Escenario 1 · Movimiento de tierra","Excavadora","C2","23",[79,81,68,69,66,65,61,52],73),

        ("Escenario 2 · Obra gruesa suelo","Rodillo compactador","C2","40",[82,78,67,71,67,64,60,57],73),
        ("Escenario 2 · Obra gruesa suelo","Minicargador","C4","14",[68,67,63,62,62,61,54,47],67),
        ("Escenario 2 · Obra gruesa suelo","Retroexcavadora","C2","8",[74,66,64,64,63,60,59,50],68),
        ("Escenario 2 · Obra gruesa suelo","Camión mixer + bomba hormigón","C4","32",[73,73,77,76,72,70,65,62],78),

        ("Escenario 2 · Obra gruesa altura","Grúa pluma","C4","46",[78,69,67,64,62,57,49,40],67),
        ("Escenario 2 · Obra gruesa altura","Vibrador de inmersión","C4","34",[62,70,70,64,62,61,59,56],69),

        ("Escenario 2 · Urbanización","Rodillo compactador","C2","40",[82,78,67,71,67,64,60,57],73),
        ("Escenario 2 · Urbanización","Minicargador","C4","14",[68,67,63,62,62,61,54,47],67),
        ("Escenario 2 · Urbanización","Retroexcavadora","C2","8",[74,66,64,64,63,60,59,50],68),
        ("Escenario 2 · Urbanización","Motoniveladora","Consultor","—",[72,75,67,59,60,56,49,44],65),
        ("Escenario 2 · Urbanización","Camión mixer + bomba hormigón","C4","32",[73,73,77,76,72,70,65,62],78),

        ("Escenario 2 · Terminaciones","Minicargador","C4","14",[68,67,63,62,62,61,54,47],67),
        ("Escenario 2 · Terminaciones","Alzahombre","C4","57",[78,76,62,63,60,59,58,49],67),

        ("Escenario 3 · Obras IMIV","Cango","C1","8",[77,72,73,69,68,66,64,60],74),
        ("Escenario 3 · Obras IMIV","Camión mixer + bomba hormigón","C4","32",[73,73,77,76,72,70,65,62],78),
        ("Escenario 3 · Obras IMIV","Vibrador de inmersión","C4","34",[62,70,70,64,62,61,59,56],69),
        ("Escenario 3 · Obras IMIV","Rodillo compactador","C2","40",[82,78,67,71,67,64,60,57],73),
    ]

    band_labels=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"]
    rows=[]
    for front,name,table,item,bands,npseq in report_sources:
        row={
            "Frente / escenario":front,
            "Máquina":name,
            "Tabla":table,
            "Ítem":item,
            "NPSeq @10 m [dB(A)]":npseq,
            "LWA aprox. [+28]":npseq+28,
        }
        for label,val in zip(band_labels,bands):
            row[label]=val
        rows.append(row)

    st.markdown("#### Valores oficiales a 10 m · Tablas 13 a 18")
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

    totals=[
        {"Frente / escenario":"Escenario 1 · Movimiento de tierra","NPSeq total @10 m [dB(A)]":75,"LWA equivalente aprox. [dB(A)]":103},
        {"Frente / escenario":"Escenario 2 · Obra gruesa suelo","NPSeq total @10 m [dB(A)]":80,"LWA equivalente aprox. [dB(A)]":108},
        {"Frente / escenario":"Escenario 2 · Obra gruesa altura","NPSeq total @10 m [dB(A)]":71,"LWA equivalente aprox. [dB(A)]":99},
        {"Frente / escenario":"Escenario 2 · Urbanización","NPSeq total @10 m [dB(A)]":80,"LWA equivalente aprox. [dB(A)]":108},
        {"Frente / escenario":"Escenario 2 · Terminaciones","NPSeq total @10 m [dB(A)]":70,"LWA equivalente aprox. [dB(A)]":98},
        {"Frente / escenario":"Escenario 3 · Obras IMIV","NPSeq total @10 m [dB(A)]":80,"LWA equivalente aprox. [dB(A)]":108},
    ]
    st.markdown("#### Totales oficiales por frente")
    st.dataframe(pd.DataFrame(totals),hide_index=True,use_container_width=True)
    st.caption(
        "Los NPSeq @10 m y sus espectros provienen directamente de la Adenda 2. "
        "La columna LWA aproximada aplica la misma conversión docente +28 dB utilizada en este laboratorio; "
        "no es un valor tabulado por el consultor."
    )

    chosen=st.selectbox(
        "Ver desarrollo de un frente",
        [x["Frente / escenario"] for x in totals],
        key="c4l2_s3_teacher_adenda_front",
    )
    selected=[x for x in report_sources if x[0]==chosen]
    detail=[]
    for _,name,table,item,bands,npseq in selected:
        d={"Máquina":name,"Ref.":f"{table} · {item}","NPSeq [dB(A)]":npseq}
        for label,val in zip(band_labels,bands):
            d[label]=val
        detail.append(d)
    st.dataframe(pd.DataFrame(detail),hide_index=True,use_container_width=True)

    with st.expander("👨‍🏫 Criterios de revisión",expanded=False):
        st.markdown("""
        - El alumno debe conservar **tabla, ítem, máquina y actividad** de la referencia seleccionada.
        - El dato del informe es **NPS/NPSeq a 10 m**, no potencia sonora.
        - Para el ejercicio, la conversión a potencia se desarrolla explícitamente antes de ingresar la fuente al modelo.
        - En **IMIV** la Adenda 2 exige posteriormente uso secuencial de maquinaria; esa condición se aplicará en la etapa de medidas de control.
        - La Motoniveladora corresponde a una medición del **consultor**, no a una referencia BS 5228.
        """)


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 3 · LABORATORIO 2",
        "Niveles de potencia sonora de la maquinaria",
        "Vincular las máquinas identificadas en la Etapa 1 con referencias trazables y obtener niveles de potencia sonora globales y por bandas, usando como contraste la Adenda 2 del Estudio de Ruido y Vibraciones.",
        show_overview=False,
        duration_minutes=30,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
    background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">DE LA MAQUINARIA REAL A LA FUENTE ACÚSTICA</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">
        Cada máquina del proyecto necesita una entrada acústica trazable
      </div>
      <div style="color:#526f80;line-height:1.6">
        Recuperaremos la maquinaria registrada en la Etapa 1 y la vincularemos con un registro
        representativo de <b>BS 5228-1</b>. El resultado será el nivel de potencia sonora global
        y el espectro de potencia por bandas que luego ingresaremos al modelo.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 1 · Presión a 10 m no es potencia sonora")
    a,b=st.columns(2,gap="large")
    with a:
        st.markdown("#### Dato original de BS 5228")
        st.markdown("""
        Las tablas utilizadas en este laboratorio entregan un **nivel de presión sonora a 10 m**
        para una actividad y condición de operación concreta. Ese dato debe conservar su
        descriptor original, tabla, referencia y actividad.
        """)
    with b:
        st.markdown("#### Dato que necesita la fuente")
        st.latex(r"L_{W,f}\approx L_{p,f}(10\,m)+28\;\mathrm{dB}")
        st.caption("Conversión práctica utilizada en el Laboratorio 1 para los registros seleccionados de las tablas C.1–C.11.")

    st.warning("No escribas un valor de presión a 10 m como si fuese Lw. Primero debes convertirlo y conservar la trazabilidad del registro original.")

    st.markdown("### Consulta la BS 5228")
    bs_path=runtime.get("BS5228_PATH")
    if bs_path is not None and bs_path.exists():
        st.download_button(
            "📘 Abrir / descargar BS 5228-1",
            data=bs_path.read_bytes(),
            file_name=bs_path.name,
            mime="application/pdf",
            use_container_width=True,
            key="c4l2_s3_bs_pdf",
            help="Documento base para buscar tabla, referencia, actividad y espectro de cada maquinaria.",
        )
        st.caption("BS 5228-1:2009+A1:2014 · Anexo C · tablas de maquinaria y actividades de obra.")
    else:
        st.warning("No se encontró el PDF de BS 5228 entre los recursos del laboratorio.")

    st.markdown("### 2 · Recupera las máquinas de la Etapa 1")
    if st.session_state.get("role")=="Docente":
        stage1_rows=_adenda2_machines()
    else:
        stage1_rows=saved.get("c4l2_s1_machinery_table") or []
    project_machines=[r for r in stage1_rows if str(r.get("Máquina / equipo") or "").strip()]
    if not project_machines:
        st.warning("Todavía no hay maquinaria guardada en la Etapa 1. Vuelve a la Etapa 1, completa la tabla de maquinaria y guarda la ficha antes de continuar.")
        _render_teacher_pauta(st,pd)
        return

    st.caption(f"Se recuperaron **{len(project_machines)}** registros de maquinaria desde la Etapa 1. No necesitas volver a escribirlos.")

    assignments_saved={
        f"{str(x.get('Máquina / equipo proyecto') or '')}|{str(x.get('Etapa') or '')}":x
        for x in (saved.get("c4l2_s3_bs_assignments") or [])
    }
    assignment_rows=[]
    for r in project_machines:
        project_name=str(r.get("Máquina / equipo") or "").strip()
        project_stage=str(r.get("Etapa asociada") or "")
        old=assignments_saved.get(f"{project_name}|{project_stage}",{})
        assignment_rows.append({
            "Máquina / equipo proyecto":project_name,
            "Cantidad":r.get("Cantidad"),
            "Etapa":r.get("Etapa asociada") or "",
            "Referencia BS":(
                old.get("Referencia BS")
                or (_suggest_bs(project_name) if st.session_state.get("role")=="Docente" else "Seleccionar referencia BS")
            ),
        })

    st.markdown("""
    <div class="c4l2-table-head"><div class="c4l2-table-icon">📚</div><div>
      <div class="c4l2-table-kicker">TRAZABILIDAD BS 5228</div>
      <div class="c4l2-table-title">Asocia cada máquina del proyecto con un registro representativo</div>
      <div class="c4l2-table-copy">La coincidencia debe justificarse por tipo de equipo, tamaño y actividad. La sugerencia automática es solo un punto de partida.</div>
      <div class="c4l2-source"><b>📄 Dónde buscar:</b> <b>BS 5228-1:2009+A1:2014 · Anexo C</b>, Tablas C.1–C.11.
      En cada referencia revisa tipo de máquina, potencia/tamaño, actividad, descriptor y nivel a 10 m.
      Las páginas exactas se muestran al seleccionar cada registro.</div>
    </div></div>
    """,unsafe_allow_html=True)

    bs_options=["Seleccionar referencia BS"]+list(SOURCE_CATALOG.keys())
    assign_df=runtime["_professional_grid"](
        pd.DataFrame(assignment_rows),
        key="c4l2_s3_assign_grid",
        widths={"Máquina / equipo proyecto":245,"Cantidad":100,"Etapa":190,"Referencia BS":260},
        select_options={"Referencia BS":bs_options},
        numeric_columns=["Cantidad"],
        height=max(235,min(520,90+42*len(assignment_rows))),
    )
    assign_records=assign_df.where(pd.notna(assign_df),None).to_dict("records")

    st.markdown("### 3 · Revisa la referencia antes de aceptarla")
    valid_refs=[r for r in assign_records if r.get("Referencia BS") in SOURCE_CATALOG]
    if not valid_refs:
        st.info("Selecciona al menos una referencia BS en la tabla anterior para revisar sus antecedentes acústicos.")
    else:
        labels=[f"{r['Máquina / equipo proyecto']} → {r['Referencia BS']}" for r in valid_refs]
        chosen_label=st.selectbox("Máquina a revisar",labels,key="c4l2_s3_review_machine")
        idx=labels.index(chosen_label)
        chosen=valid_refs[idx]
        item=SOURCE_CATALOG[chosen["Referencia BS"]]
        metric=item.get("metric","LAeq,T")
        lp,lw,lwa_bands,lwa_spec,lwa_global=_calc(item)

        m1,m2,m3,m4=st.columns(4)
        m1.metric("Tabla BS",item["table"])
        m2.metric("Referencia",f"Ref. {item['ref']}")
        m3.metric("Descriptor",metric)
        m4.metric("Nivel a 10 m",f"{item['laeq10']:.0f} dB(A)")
        st.caption(f"📄 {item['page']} · Actividad: {item['activity']} · Potencia/tamaño: {item['power']} · {item['size']}")

        if item.get("driveby"):
            st.warning("Este registro corresponde a una pasada móvil y usa LAmax/Lmax. Conserva ese descriptor; no lo trates como un LAeq estacionario.")

        st.markdown("### 4 · Obtén el espectro de potencia sonora")
        spec_rows=[]
        band_labels=item.get("band_labels",OCTAVE_LABELS)
        a_corr=item.get("a_corr",A_CORR)
        for f_label,lpv,lwv,ac,lwav in zip(band_labels,lp,lw,a_corr,lwa_bands):
            spec_rows.append({
                "Banda":f_label,
                "Lp a 10 m [dB]":lpv,
                "Lw [dB]":lwv,
                "Corr. A [dB]":ac,
                "LwA banda [dB(A)]":round(lwav,1),
            })
        st.dataframe(pd.DataFrame(spec_rows),hide_index=True,use_container_width=True)

        r1,r2,r3=st.columns(3)
        r1.metric("LWA global · +28",f"{lwa_global:.1f} dB(A)")
        r2.metric("LWA desde espectro",f"{lwa_spec:.1f} dB(A)")
        r3.metric("Diferencia",f"{lwa_spec-lwa_global:+.1f} dB")
        st.caption("Una pequeña diferencia es esperable por redondeo de los valores tabulados por banda.")

        st.markdown("#### ¿Qué ingresarás a Noise Map Lab?")
        st.markdown(
            f"Para **{chosen['Máquina / equipo proyecto']}**, usando la referencia **{chosen['Referencia BS']}**, "
            "el modo por bandas utiliza los valores **Lw [dB]** de la tabla anterior. "
            f"Si trabajas en broadband, la referencia global es **LWA ≈ {lwa_global:.1f} dB(A)**."
        )

    st.markdown("### 5 · Resumen acústico de todas las máquinas")
    summary=[]
    for r in assign_records:
        ref=r.get("Referencia BS")
        if ref not in BS_PLANT:
            summary.append({
                "Máquina proyecto":r.get("Máquina / equipo proyecto"),
                "Referencia BS":"Pendiente",
                "Tabla / Ref.":"",
                "Página":"",
                "Lp 10 m [dB(A)]":None,
                "LWA [dB(A)]":None,
            })
            continue
        item=SOURCE_CATALOG[ref]
        _,_,_,_,lwa_global=_calc(item)
        summary.append({
            "Máquina proyecto":r.get("Máquina / equipo proyecto"),
            "Referencia BS":ref,
            "Tabla / Ref.":f"{item['table']} · Ref. {item['ref']}",
            "Página":item["page"],
            "Lp 10 m [dB(A)]":item["laeq10"],
            "LWA [dB(A)]":round(lwa_global,1),
        })
    st.dataframe(pd.DataFrame(summary),hide_index=True,use_container_width=True)

    st.markdown("### 6 · Guarda la caracterización acústica")
    st.caption("Al guardar, el laboratorio conserva la referencia BS y los espectros calculados para reutilizarlos cuando ubiquemos las fuentes en Noise Map Lab.")
    if st.button("✓ Guardar niveles de potencia",type="primary",use_container_width=True,key="c4l2_s3_save"):
        pending=[r for r in assign_records if r.get("Referencia BS") not in SOURCE_CATALOG]
        if pending:
            st.warning(f"Falta seleccionar una referencia BS válida para **{len(pending)}** máquina(s).")
        else:
            acoustic=[]
            for r in assign_records:
                item=SOURCE_CATALOG[r["Referencia BS"]]
                lp,lw,lwa_bands,lwa_spec,lwa_global=_calc(item)
                acoustic.append({
                    **r,
                    "Tabla":item["table"],
                    "Ref":item["ref"],
                    "Página":item["page"],
                    "Actividad BS":item["activity"],
                    "Descriptor original":item.get("metric","LAeq,T"),
                    "Lp10_global":item["laeq10"],
                    "Lp_bandas":lp,
                    "Lw_bandas":lw,
                    "LwA_bandas":lwa_bands,
                    "LWA_global":lwa_global,
                    "LWA_espectro":lwa_spec,
                })
            saved["c4l2_s3_bs_assignments"]=assign_records
            saved["c4l2_s3_acoustic_sources"]=acoustic
            saved["done_3"]=True
            runtime["_save"](lab,saved,3)
            st.success("Caracterización acústica guardada. Estos niveles quedan disponibles para la siguiente etapa.")

    _render_teacher_pauta(st,pd)
