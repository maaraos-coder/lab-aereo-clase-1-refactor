"""Etapa 3 · Curso 4 Laboratorio 2: niveles de potencia sonora de maquinaria."""

import math
import unicodedata
from labs.curso4_laboratorio_1 import BS_PLANT

OCTAVE_LABELS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]
A_CORR=[-39.4,-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0]

def _norm(value):
    text=str(value or "").strip().lower()
    text="".join(ch for ch in unicodedata.normalize("NFD",text) if unicodedata.category(ch)!="Mn")
    for token in ("camion ","camión ","maquina ","máquina ","equipo "):
        text=text.replace(token,token)
    return " ".join(text.split())

def _suggest_bs(project_name):
    n=_norm(project_name)
    aliases={
        "excavadora":"Excavadora hidráulica",
        "excavadora hidraulica":"Excavadora hidráulica",
        "retroexcavadora":"Retroexcavadora",
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
        "vibrador de inmersion":"Vibrador de inmersión",
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
    for name in BS_PLANT:
        if _norm(name)==n:
            return name
    return "Seleccionar referencia BS"

def _calc(item):
    lp=list(item["bands"])
    lw=[v+28.0 for v in lp]
    lwa_bands=[v+a for v,a in zip(lw,A_CORR)]
    lwa_spec=10*math.log10(sum(10**(v/10) for v in lwa_bands))
    lwa_global=item["laeq10"]+28.0
    return lp,lw,lwa_bands,lwa_spec,lwa_global

def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 3 · LABORATORIO 2",
        "Niveles de potencia sonora de la maquinaria",
        "Vincular las máquinas identificadas en la Etapa 1 con referencias trazables de BS 5228 y obtener niveles de potencia sonora globales y por bandas para modelación.",
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
    stage1_rows=saved.get("c4l2_s1_machinery_table") or []
    project_machines=[r for r in stage1_rows if str(r.get("Máquina / equipo") or "").strip()]
    if not project_machines:
        st.warning("Todavía no hay maquinaria guardada en la Etapa 1. Vuelve a la Etapa 1, completa la tabla de maquinaria y guarda la ficha antes de continuar.")
        return

    st.caption(f"Se recuperaron **{len(project_machines)}** registros de maquinaria desde la Etapa 1. No necesitas volver a escribirlos.")

    assignments_saved={str(x.get("Máquina / equipo proyecto")):x for x in (saved.get("c4l2_s3_bs_assignments") or [])}
    assignment_rows=[]
    for r in project_machines:
        project_name=str(r.get("Máquina / equipo") or "").strip()
        old=assignments_saved.get(project_name,{})
        assignment_rows.append({
            "Máquina / equipo proyecto":project_name,
            "Cantidad":r.get("Cantidad"),
            "Etapa":r.get("Etapa asociada") or "",
            "Referencia BS":old.get("Referencia BS") or _suggest_bs(project_name),
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

    bs_options=["Seleccionar referencia BS"]+list(BS_PLANT.keys())
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
    valid_refs=[r for r in assign_records if r.get("Referencia BS") in BS_PLANT]
    if not valid_refs:
        st.info("Selecciona al menos una referencia BS en la tabla anterior para revisar sus antecedentes acústicos.")
    else:
        labels=[f"{r['Máquina / equipo proyecto']} → {r['Referencia BS']}" for r in valid_refs]
        chosen_label=st.selectbox("Máquina a revisar",labels,key="c4l2_s3_review_machine")
        idx=labels.index(chosen_label)
        chosen=valid_refs[idx]
        item=BS_PLANT[chosen["Referencia BS"]]
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
        for f_label,lpv,lwv,ac,lwav in zip(OCTAVE_LABELS,lp,lw,A_CORR,lwa_bands):
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
        item=BS_PLANT[ref]
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
        pending=[r for r in assign_records if r.get("Referencia BS") not in BS_PLANT]
        if pending:
            st.warning(f"Falta seleccionar una referencia BS válida para **{len(pending)}** máquina(s).")
        else:
            acoustic=[]
            for r in assign_records:
                item=BS_PLANT[r["Referencia BS"]]
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

    if st.session_state.get("role")=="Docente":
        with st.expander("👨‍🏫 Pauta docente · Etapa 3"):
            st.markdown("""
            Revisar que cada maquinaria del proyecto tenga una referencia BS coherente con **equipo + tamaño/potencia + actividad**.
            El alumno debe distinguir el dato original de presión a 10 m del nivel de potencia utilizado en el modelo,
            mantener tabla/ref./página y conservar el descriptor original, especialmente en registros móviles.
            """)

            st.markdown("#### Referencias BS sugeridas por etapa")
            teacher_map=[
                ("Movimiento de tierras","Excavadora hidráulica","Excavadora hidráulica"),
                ("Movimiento de tierras","Retroexcavadora","Retroexcavadora"),
                ("Movimiento de tierras","Cargador frontal","Cargador frontal"),
                ("Movimiento de tierras","Camión tolva","Camión tolva articulado"),
                ("Movimiento de tierras","Rodillo vibratorio","Rodillo vibratorio"),
                ("Hormigón / obra gruesa","Camión mixer","Camión mixer"),
                ("Hormigón / obra gruesa","Bomba de hormigón","Bomba de hormigón"),
                ("Hormigón / obra gruesa","Vibrador de inmersión","Vibrador de inmersión"),
                ("Estructura / izaje","Grúa torre","Grúa torre"),
                ("Equipos auxiliares","Generador diésel","Generador diésel"),
            ]
            rows=[]
            for stage_name,project_machine,bs_name in teacher_map:
                item=BS_PLANT[bs_name]
                _,lw,_,lwa_spec,lwa_global=_calc(item)
                rows.append({
                    "Etapa":stage_name,
                    "Máquina proyecto":project_machine,
                    "Referencia BS":bs_name,
                    "Tabla / Ref.":f"{item['table']} · Ref. {item['ref']}",
                    "Página":item["page"],
                    "Descriptor":item.get("metric","LAeq,T"),
                    "Lp 10 m":f"{item['laeq10']:.0f} dB(A)",
                    "LWA ref.":f"{lwa_global:.0f} dB(A)",
                })
            st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

            st.markdown("#### Espectros de potencia esperados")
            selected_teacher=st.selectbox(
                "Ver espectro de referencia",
                [r[1] for r in teacher_map],
                key="c4l2_s3_teacher_spectrum",
            )
            bs_name=next(x[2] for x in teacher_map if x[1]==selected_teacher)
            item=BS_PLANT[bs_name]
            _,lw,_,_,lwa_global=_calc(item)
            st.dataframe(
                pd.DataFrame({"Banda":OCTAVE_LABELS,"Lw [dB]":[round(v,1) for v in lw]}),
                hide_index=True,
                use_container_width=True,
            )
            st.caption(
                f"BS 5228-1 · Tabla {item['table']} · Ref. {item['ref']} · {item['page']} · "
                f"LWA broadband de referencia ≈ {lwa_global:.1f} dB(A)."
            )
            st.info(
                "La selección final debe corresponder a la máquina, tamaño/potencia y actividad efectivamente declarados en el proyecto. "
                "Si el expediente usa un equipo distinto, la pauta debe ajustarse al registro BS más representativo."
            )
