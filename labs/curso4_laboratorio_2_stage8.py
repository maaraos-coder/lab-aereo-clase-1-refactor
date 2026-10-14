"""Etapa 8 · Optimización y cierre técnico de la solución."""

import math


DECISIONS=["Mantener solución","Ajustar solución","Reemplazar solución"]


def _num(value):
    try:
        number=float(str(value).replace(",",".").strip())
        return number if math.isfinite(number) else None
    except Exception:
        return None


def _scenario(front):
    text=str(front or "")
    if "Escenario 1" in text:return "Escenario 1"
    if "Escenario 2" in text:return "Escenario 2"
    if "Escenario 3" in text:return "Escenario 3"
    return text


def _optimization_rows(design_rows,comparison_rows,saved_rows,limit):
    saved_map={str(row.get("Frente / condición") or ""):row for row in (saved_rows or [])}
    levels={}
    reductions={}
    for row in comparison_rows:
        scenario=_scenario(row.get("Frente"))
        level=_num(row.get("Controlado [dB(A)]"))
        reduction=_num(row.get("Reducción [dB]"))
        if level is not None:
            levels[scenario]=max(level,levels.get(scenario,-math.inf))
        if reduction is not None:
            reductions.setdefault(scenario,[]).append(reduction)

    output=[]
    for design in design_rows:
        front=str(design.get("Frente / condición") or "")
        scenario=_scenario(front)
        previous=saved_map.get(front,{})
        controlled=levels.get(scenario)
        mean_reduction=None
        if reductions.get(scenario):
            mean_reduction=sum(reductions[scenario])/len(reductions[scenario])
        output.append({
            "Frente / condición":front,
            "Medida inicial":design.get("Medida seleccionada") or "",
            "Máximo controlado [dB(A)]":round(controlled,1) if controlled is not None else None,
            "Reducción media [dB]":round(mean_reduction,1) if mean_reduction is not None else None,
            "Resultado":("Pendiente" if controlled is None else "Bajo el límite" if controlled<=limit else "Sobre el límite"),
            "Decisión final":previous.get("Decisión final") or ("Mantener solución" if controlled is not None and controlled<=limit else "Ajustar solución"),
            "Ajuste o especificación final":previous.get("Ajuste o especificación final") or "",
            "Proyecto definitivo":previous.get("Proyecto definitivo") or design.get("Proyecto controlado") or "",
        })
    return output


def _teacher_panel(st,pd):
    if st.session_state.get("role")!="Docente":return
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;padding:17px 19px;
                background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VISTA DOCENTE · CIERRE TÉCNICO</div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">La iteración forma parte del diseño</div>
      <div style="color:#526f80;line-height:1.55">No penalices que una primera solución resulte insuficiente si el alumno reconoce la causa, ajusta parámetros coherentes y conserva la trazabilidad entre versiones.</div>
    </div>
    """,unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Criterio":"Decisión","Qué revisar":"Mantener, ajustar o reemplazar se fundamenta en resultados modelados."},
        {"Criterio":"Especificación","Qué revisar":"Dimensiones, material, TL/Rw, aberturas, orientación o ubicación quedan definidas."},
        {"Criterio":"Viabilidad","Qué revisar":"La medida permite ejecutar la actividad constructiva y puede mantenerse."},
        {"Criterio":"Limitaciones","Qué revisar":"Reconoce simplificaciones e incertidumbres de la modelación."},
    ]),hide_index=True,use_container_width=True)


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 8 · LABORATORIO 2",
        "Optimiza y cierra la solución técnica",
        "Transformar los resultados de la comparación en una propuesta definitiva, viable, trazable y preparada para la evaluación final.",
        show_overview=False,duration_minutes=35,
    )
    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ITERAR · DECIDIR · DOCUMENTAR</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">La primera propuesta no siempre es la solución final</div>
      <div style="color:#526f80;line-height:1.6">Revisa la reducción obtenida, decide qué medidas se conservan y documenta los ajustes necesarios. El resultado será la ficha técnica final que se incluirá en la Etapa 10.</div>
    </div>
    """,unsafe_allow_html=True)
    _teacher_panel(st,pd)

    comparison=saved.get("c4l2_s7_comparison") or []
    design=saved.get("c4l2_s6_control_design") or []
    period=str(saved.get("c4l2_s5_reference_period") or "Diurno")
    limit=_num(saved.get("c4l2_s5_reference_limit_db"))
    if limit is None:limit=50.0 if period=="Nocturno" else 65.0

    st.markdown("### 1 · Revisa el desempeño alcanzado")
    if not comparison:
        st.warning("Completa la comparación original–controlada de la Etapa 7 antes de cerrar la solución.")
    else:
        levels=[_num(row.get("Controlado [dB(A)]")) for row in comparison]
        levels=[value for value in levels if value is not None]
        reductions=[_num(row.get("Reducción [dB]")) for row in comparison]
        reductions=[value for value in reductions if value is not None]
        a,b,c,d=st.columns(4)
        a.metric("Resultados comparados",len(levels))
        b.metric("Mayor controlado",f"{max(levels):.1f} dB(A)" if levels else "—")
        c.metric("Reducción media",f"{sum(reductions)/len(reductions):.1f} dB" if reductions else "—")
        d.metric("Bajo referencia",f"{sum(value<=limit for value in levels)}/{len(levels)}" if levels else "—")
        if levels and max(levels)>limit:
            st.warning(f"La solución todavía presenta receptores sobre el límite {period.lower()} de referencia de {limit:.0f} dB(A). Debes ajustar o reemplazar las medidas asociadas.")
        elif levels:
            st.success("Todos los resultados controlados registrados están bajo el límite de referencia seleccionado.")

    st.markdown("### 2 · Define la solución definitiva por frente")
    rows=_optimization_rows(design,comparison,saved.get("c4l2_s8_final_strategy") or [],limit)
    if not rows:
        st.info("La Etapa 6 todavía no contiene estrategias guardadas.")
        final_df=pd.DataFrame([])
    else:
        final_df=st.data_editor(
            pd.DataFrame(rows),hide_index=True,use_container_width=True,num_rows="fixed",
            height=max(300,46+42*len(rows)),key="c4l2_s8_strategy_editor",
            disabled=["Frente / condición","Medida inicial","Máximo controlado [dB(A)]","Reducción media [dB]","Resultado"],
            column_config={
                "Frente / condición":st.column_config.TextColumn("Frente / condición",width="large"),
                "Medida inicial":st.column_config.TextColumn("Medida inicial",width="medium"),
                "Máximo controlado [dB(A)]":st.column_config.NumberColumn("Máx. controlado",format="%.1f dB(A)",width="small"),
                "Reducción media [dB]":st.column_config.NumberColumn("Reducción media",format="%.1f dB",width="small"),
                "Resultado":st.column_config.TextColumn("Resultado",width="medium"),
                "Decisión final":st.column_config.SelectboxColumn("Decisión final",options=DECISIONS,required=True,width="medium"),
                "Ajuste o especificación final":st.column_config.TextColumn("Ajuste o especificación final",width="large"),
                "Proyecto definitivo":st.column_config.TextColumn("Proyecto definitivo",width="medium"),
            },
        )

    st.markdown("### 3 · Redacta el cierre técnico")
    a,b=st.columns(2,gap="large")
    with a:
        conclusion=st.text_area(
            "Conclusión técnica final",value=str(saved.get("c4l2_s8_conclusion") or ""),height=150,
            key="c4l2_s8_conclusion_work",placeholder="Resume el problema original, la medida definitiva, la reducción y el resultado frente al límite de referencia.",
        )
        implementation=st.text_area(
            "Condiciones de implementación y mantenimiento",value=str(saved.get("c4l2_s8_implementation") or ""),height=130,
            key="c4l2_s8_implementation_work",placeholder="Indica montaje, sellos, inspección, ventilación, acceso, reposición o mantenimiento necesario.",
        )
    with b:
        limitations=st.text_area(
            "Limitaciones e incertidumbres",value=str(saved.get("c4l2_s8_limitations") or ""),height=150,
            key="c4l2_s8_limitations_work",placeholder="Distingue simplificaciones del modelo, calidad de datos, condiciones meteorológicas y diferencias con una medición real.",
        )
        verification=st.text_area(
            "Plan de verificación",value=str(saved.get("c4l2_s8_verification") or ""),height=130,
            key="c4l2_s8_verification_work",placeholder="Explica cómo comprobarías en terreno que la medida fue correctamente construida y funciona como se diseñó.",
        )

    st.markdown("### 4 · Verifica la entrega técnica")
    previous_checks=saved.get("c4l2_s8_checks") or {}
    check_labels={
        "traceability":"Conservé identificados el proyecto original y la copia controlada definitiva.",
        "specification":"Definí dimensiones, materiales y parámetros acústicos de las medidas.",
        "viability":"Comprobé que las medidas son compatibles con la operación de la faena.",
        "results":"Relacioné la conclusión con resultados numéricos y no solo con el mapa de colores.",
    }
    checks={name:st.checkbox(label,value=bool(previous_checks.get(name)),key=f"c4l2_s8_check_{name}") for name,label in check_labels.items()}

    draft_records=final_df.where(pd.notna(final_df),None).to_dict("records") if not final_df.empty else []
    from labs.curso4_lab2_drafts import render_draft_save
    render_draft_save(st,saved,runtime,lab,8,{
        "c4l2_s8_final_strategy":draft_records,
        "c4l2_s8_conclusion":conclusion,
        "c4l2_s8_implementation":implementation,
        "c4l2_s8_limitations":limitations,
        "c4l2_s8_verification":verification,
        "c4l2_s8_checks":checks,
    },"c4l2_s8_save_draft")

    if st.button("✓ Validar y finalizar la Etapa 8",type="primary",use_container_width=True,key="c4l2_s8_save"):
        records=final_df.where(pd.notna(final_df),None).to_dict("records") if not final_df.empty else []
        incomplete=[row for row in records if not str(row.get("Ajuste o especificación final") or "").strip() or not str(row.get("Proyecto definitivo") or "").strip()]
        if not saved.get("done_7"):
            st.warning("Completa la Etapa 7 antes de cerrar la solución definitiva.")
        elif not records or incomplete:
            st.warning("Completa la especificación y el nombre del proyecto definitivo para todos los frentes.")
        elif not all(checks.values()):
            st.warning("Confirma las cuatro verificaciones de entrega técnica.")
        elif min(len(conclusion.strip()),len(implementation.strip()),len(limitations.strip()),len(verification.strip()))<60:
            st.warning("Desarrolla cada apartado del cierre técnico con al menos 60 caracteres.")
        else:
            saved["c4l2_s8_final_strategy"]=records
            saved["c4l2_s8_conclusion"]=conclusion
            saved["c4l2_s8_implementation"]=implementation
            saved["c4l2_s8_limitations"]=limitations
            saved["c4l2_s8_verification"]=verification
            saved["c4l2_s8_checks"]=checks
            saved["done_8"]=True
            runtime["_save"](lab,saved,8)
            st.success("Solución definitiva guardada. Ya puedes rendir el cuestionario de la Etapa 9.")

