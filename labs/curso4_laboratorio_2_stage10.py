"""Etapa 10 · Entrega y evaluación integral del Laboratorio 2."""

import json


RUBRIC=[
    (1,"Antecedentes y comprensión del proyecto",5),
    (2,"Selección y caracterización de receptores",5),
    (3,"Maquinaria, espectros y potencias acústicas",10),
    (4,"Modelación de la condición original",10),
    (5,"Resultados y condición crítica",10),
    (6,"Diseño y fundamentación de medidas de control",15),
    (7,"Comparación original–controlada",10),
    (8,"Optimización y cierre técnico",5),
]


def _grade(score,max_score=100.0):
    percentage=100*float(score)/float(max_score)
    if percentage<60:
        return round(1.0+3.0*(percentage/60.0),1)
    return round(4.0+3.0*((percentage-60.0)/40.0),1)


def _payload(row):
    value=(row or {}).get("answer") or {}
    if isinstance(value,str):
        try:return json.loads(value)
        except Exception:return {}
    return value if isinstance(value,dict) else {}


def _quiz_score(row,saved):
    if row:
        if row.get("teacher_score") is not None:return float(row["teacher_score"])
        if row.get("auto_score") is not None:return float(row["auto_score"])
    return float(saved.get("c4l2_s9_score") or 0)


def _practical_score(row):
    if row and row.get("teacher_score") is not None:
        return float(row["teacher_score"])
    return None


def _table_records(value,identity="Ítem"):
    """Convierte listas o diccionarios guardados en filas legibles de informe."""
    if isinstance(value,list):
        rows=value
    elif isinstance(value,dict):
        rows=[]
        for key,item in value.items():
            if isinstance(item,dict):
                rows.append({identity:key,**item})
            else:
                rows.append({identity:key,"Detalle":item})
    else:
        rows=[]
    cleaned=[]
    for row in rows:
        if not isinstance(row,dict):
            row={"Detalle":row}
        cleaned.append({
            str(key):(
                json.dumps(item,ensure_ascii=False)
                if isinstance(item,(dict,list)) else item
            )
            for key,item in row.items()
            if str(key)!="Zona D.S.38"
        })
    return cleaned


def _report_table(st,pd,title,value,identity="Ítem"):
    rows=_table_records(value,identity)
    st.markdown(f"**{title}**")
    if rows:
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    else:
        st.caption("Sin información registrada en esta parte.")


def _report_text(st,title,value):
    st.markdown(f"**{title}**")
    if str(value or "").strip():
        st.write(str(value).strip())
    else:
        st.caption("Sin desarrollo registrado.")


def _section_header(st,stage,title,points,complete=True):
    state="EVIDENCIA RECUPERADA" if complete else "EVIDENCIA PENDIENTE"
    state_color="#087ba0" if complete else "#9a6700"
    st.markdown(f"""
    <div style="margin:1.45rem 0 .7rem;border:1px solid #c9dce8;border-left:6px solid {state_color};
                border-radius:18px;padding:16px 18px;background:linear-gradient(135deg,#fbfdff,#eef7fb)">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
        <div>
          <div style="font-size:.67rem;font-weight:900;letter-spacing:.09em;color:{state_color}">
            ETAPA {stage} · {state}
          </div>
          <div style="font-size:1.08rem;font-weight:900;color:#173b53;margin-top:.22rem">{title}</div>
        </div>
        <div style="white-space:nowrap;border-radius:999px;padding:9px 14px;background:#0b7fa5;color:white;
                    font-size:.78rem;font-weight:900;letter-spacing:.03em">
          PUNTAJE MÁXIMO · {points} PTOS
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)


def _render_integrated_report(st,pd,report,done=None,quiz_score=None):
    """Informe continuo con todas las evidencias de las Etapas 1 a 8."""
    done=done or {}
    reference=report.get("reference") or {}

    _section_header(st,1,RUBRIC[0][1],RUBRIC[0][2],done.get(1,True))
    s1=report.get("stage_1") or {}
    _report_table(st,pd,"Polígono y vértices del proyecto",s1.get("vertices"),"Vértice")
    _report_table(st,pd,"Partes y sectores del proyecto",s1.get("parts"),"Parte")
    _report_table(st,pd,"Etapas o fases constructivas",s1.get("phases"),"Etapa")
    _report_table(st,pd,"Maquinaria identificada",s1.get("machinery"),"Equipo")

    _section_header(st,2,RUBRIC[1][1],RUBRIC[1][2],done.get(2,True))
    _report_table(st,pd,"Receptores seleccionados",(report.get("stage_2") or {}).get("receptors"),"Receptor")

    _section_header(st,3,RUBRIC[2][1],RUBRIC[2][2],done.get(3,True))
    _report_table(st,pd,"Fuentes acústicas, espectros y niveles de potencia",(report.get("stage_3") or {}).get("sources"),"Fuente")

    _section_header(st,4,RUBRIC[3][1],RUBRIC[3][2],done.get(4,True))
    s4=report.get("stage_4") or {}
    _report_table(st,pd,"Configuración de los frentes originales",s4.get("fronts"),"Frente")
    _report_table(st,pd,"Resultados y proyectos guardados",s4.get("results"),"Frente")

    _section_header(st,5,RUBRIC[4][1],RUBRIC[4][2],done.get(5,True))
    a,b=st.columns(2)
    a.metric("Periodo de referencia",str(reference.get("period") or "Diurno"))
    try:limit_text=f"{float(reference.get('limit_db',65)):.0f} dB(A)"
    except (TypeError,ValueError):limit_text="—"
    b.metric("Límite de referencia",limit_text)
    s5=report.get("stage_5") or {}
    _report_table(st,pd,"Resultados de la condición original",s5.get("results"),"Resultado")
    _report_table(st,pd,"Condición crítica identificada",s5.get("critical"),"Parámetro")
    _report_text(st,"Interpretación espacial",s5.get("spatial_note"))
    _report_text(st,"Interpretación espectral",s5.get("spectral_note"))

    _section_header(st,6,RUBRIC[5][1],RUBRIC[5][2],done.get(6,True))
    s6=report.get("stage_6") or {}
    _report_table(st,pd,"Estrategia de control por frente",s6.get("design"),"Frente")
    _report_table(st,pd,"Configuración y cálculo de las medidas",s6.get("configurations"),"Frente")

    _section_header(st,7,RUBRIC[6][1],RUBRIC[6][2],done.get(7,True))
    s7=report.get("stage_7") or {}
    _report_table(st,pd,"Resultados de la condición controlada",s7.get("controlled_results"),"Resultado")
    _report_table(st,pd,"Comparación original–controlada",s7.get("comparison"),"Comparación")
    _report_text(st,"Evaluación de la efectividad",s7.get("effectiveness"))
    _report_text(st,"Diferencias observadas entre ambos modelos",s7.get("differences"))

    _section_header(st,8,RUBRIC[7][1],RUBRIC[7][2],done.get(8,True))
    s8=report.get("stage_8") or {}
    _report_table(st,pd,"Estrategia técnica definitiva",s8.get("final_strategy"),"Frente")
    _report_text(st,"Conclusión técnica",s8.get("conclusion"))
    _report_text(st,"Plan de implementación",s8.get("implementation"))
    _report_text(st,"Limitaciones y supuestos",s8.get("limitations"))
    _report_text(st,"Plan de verificación",s8.get("verification"))

    _section_header(st,9,"Cuestionario oficial de comprensión",30,quiz_score is not None)
    if quiz_score is None:
        st.info("El puntaje del cuestionario se incorporará cuando se complete y envíe la Etapa 9.")
    else:
        st.metric("Resultado automático del cuestionario",f"{float(quiz_score):g} / 30 puntos")

    st.markdown("""
    <div style="margin:1.2rem 0;border:1px solid #bcd8e7;border-radius:20px;padding:18px 20px;
                background:linear-gradient(135deg,#eaf7fb,#f8fcff)">
      <div style="font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ESTRUCTURA DE LA NOTA FINAL</div>
      <div style="font-size:1.12rem;font-weight:900;color:#173b53;margin:.35rem 0">Informe técnico 70 puntos + cuestionario 30 puntos = 100 puntos</div>
      <div style="color:#526f80">La nota final se publica después de que el docente revise y puntúe las ocho secciones del informe.</div>
    </div>
    """,unsafe_allow_html=True)


def _teacher_view(st,pd,saved):
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;padding:17px 19px;
                background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VISTA DOCENTE · EVALUACIÓN INTEGRAL</div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">70 puntos de desarrollo práctico + 30 puntos de cuestionario</div>
      <div style="color:#526f80;line-height:1.55">La Etapa 10 no agrega un ejercicio nuevo. Consolida las evidencias de las Etapas 1 a 8 y deja el expediente bloqueado para revisión. El cuestionario de la Etapa 9 se corrige automáticamente.</div>
    </div>
    """,unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Desarrollo práctico","70 puntos")
    b.metric("Cuestionario","30 puntos")
    c.metric("Total","100 puntos")
    st.markdown("#### Conversión a nota")
    st.write("Exigencia del 60 %: 60 puntos equivalen a nota 4,0 y 100 puntos a nota 7,0.")
    st.info("Revisa cada entrega en **Evaluaciones entregadas**, asigna el puntaje práctico sobre 70 y publica la retroalimentación. La nota final se calculará con ese puntaje más el resultado del cuestionario.")
    st.markdown("### Informe integral que recibirá el docente")
    st.caption("Cada capítulo muestra su puntaje máximo y recupera la evidencia guardada en la etapa correspondiente.")
    report=_submission_payload(saved)
    done={stage:bool(saved.get(f"done_{stage}")) for stage in range(1,9)}
    quiz=float(saved.get("c4l2_s9_score") or 0) if saved.get("done_9") else None
    _render_integrated_report(st,pd,report,done,quiz)


def _evidence_summary(saved):
    return {
        "vertices":len(saved.get("c4l2_s1_vertices_table") or []),
        "receptors":len(saved.get("c4l2_s2_receptors_table") or []),
        "sources":len(saved.get("c4l2_s3_acoustic_sources") or []),
        "original_fronts":len(saved.get("c4l2_s4_fronts") or {}),
        "original_results":len(saved.get("c4l2_s5_detailed_results") or []),
        "control_strategies":len(saved.get("c4l2_s6_control_design") or []),
        "controlled_results":len(saved.get("c4l2_s7_controlled_results") or []),
        "final_strategies":len(saved.get("c4l2_s8_final_strategy") or []),
    }


def _submission_payload(saved):
    return {
        "version":"c4l2_stage10_v1",
        "rubric":[{"stage":stage,"criterion":criterion,"max_score":points} for stage,criterion,points in RUBRIC],
        "practical_max_score":70,
        "quiz_max_score":30,
        "reference":{
            "period":saved.get("c4l2_s5_reference_period") or "Diurno",
            "limit_db":saved.get("c4l2_s5_reference_limit_db") or 65.0,
            "standard":"DS N.º 38/2011 del MMA · referencia educativa",
        },
        "evidence_summary":_evidence_summary(saved),
        "stage_1":{
            "vertices":saved.get("c4l2_s1_vertices_table") or [],
            "parts":saved.get("c4l2_s1_parts_table") or [],
            "phases":saved.get("c4l2_s1_phases_table") or [],
            "machinery":saved.get("c4l2_s1_machinery_table") or [],
        },
        "stage_2":{"receptors":saved.get("c4l2_s2_receptors_table") or []},
        "stage_3":{"sources":saved.get("c4l2_s3_acoustic_sources") or []},
        "stage_4":{"fronts":saved.get("c4l2_s4_fronts") or {},"results":saved.get("c4l2_s4_results") or {}},
        "stage_5":{
            "results":saved.get("c4l2_s5_detailed_results") or [],
            "critical":saved.get("c4l2_s5_critical") or {},
            "spatial_note":saved.get("c4l2_s5_spatial_note") or "",
            "spectral_note":saved.get("c4l2_s5_spectral_note") or "",
        },
        "stage_6":{
            "design":saved.get("c4l2_s6_control_design") or [],
            "configurations":saved.get("c4l2_s6_measure_config") or {},
        },
        "stage_7":{
            "controlled_results":saved.get("c4l2_s7_controlled_results") or [],
            "comparison":saved.get("c4l2_s7_comparison") or [],
            "effectiveness":saved.get("c4l2_s7_effectiveness") or "",
            "differences":saved.get("c4l2_s7_differences") or "",
        },
        "stage_8":{
            "final_strategy":saved.get("c4l2_s8_final_strategy") or [],
            "conclusion":saved.get("c4l2_s8_conclusion") or "",
            "implementation":saved.get("c4l2_s8_implementation") or "",
            "limitations":saved.get("c4l2_s8_limitations") or "",
            "verification":saved.get("c4l2_s8_verification") or "",
        },
        "stage_9":saved.get("c4l2_s9_submission") or {},
    }


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 10 · LABORATORIO 2",
        "Entrega y evaluación integral",
        "Consolidar el proyecto desarrollado durante todo el laboratorio, enviarlo a evaluación y obtener la nota final sobre 100 puntos.",
        show_overview=False,duration_minutes=25,
    )
    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ENTREGA FINAL · 100 PUNTOS</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">Tu proyecto completo, desde los antecedentes hasta la solución controlada</div>
      <div style="color:#526f80;line-height:1.6">La plataforma reúne las evidencias guardadas en las Etapas 1 a 8. El desarrollo práctico vale 70 puntos y el cuestionario de la Etapa 9 vale 30 puntos.</div>
    </div>
    """,unsafe_allow_html=True)

    if st.session_state.get("role")=="Docente":
        _teacher_view(st,pd,saved)
        return

    quiz_row=runtime["_evaluation_row"](9,"c4l2_final_quiz")
    final_row=runtime["_evaluation_row"](10,"c4l2_integrated_project")
    submitted=bool(final_row or saved.get("c4l2_s10_submitted"))
    quiz_score=_quiz_score(quiz_row,saved)
    practical_score=_practical_score(final_row)

    if submitted:
        st.success("Evaluación integral enviada. El expediente quedó bloqueado para revisión docente.")
        a,b,c,d=st.columns(4)
        a.metric("Cuestionario",f"{quiz_score:g}/30")
        if practical_score is None:
            b.metric("Desarrollo práctico","Pendiente")
            c.metric("Puntaje final","Pendiente")
            d.metric("Nota final","Pendiente")
            st.info("La nota final aparecerá cuando el docente asigne el puntaje práctico sobre 70 puntos.")
        else:
            total=max(0.0,min(100.0,quiz_score+practical_score))
            grade=_grade(total)
            b.metric("Desarrollo práctico",f"{practical_score:g}/70")
            c.metric("Puntaje final",f"{total:g}/100")
            d.metric("Nota final",f"{grade:.1f}")
            if total>=60:st.success("Evaluación aprobada con exigencia del 60 %.")
            else:st.error("El puntaje final se encuentra bajo la exigencia de aprobación del 60 %.")
        feedback=(final_row or {}).get("teacher_feedback") or (final_row or {}).get("feedback")
        if feedback:st.markdown(f"**Retroalimentación docente:** {feedback}")
        st.markdown("### Informe técnico entregado")
        report=_payload(final_row) if final_row else _submission_payload(saved)
        if not isinstance(report,dict) or not report.get("stage_1"):
            report=_submission_payload(saved)
        _render_integrated_report(st,pd,report,{stage:True for stage in range(1,9)},quiz_score)
        return

    st.markdown("### 1 · Comprueba el avance del laboratorio")
    progress=[]
    for stage,criterion,points in RUBRIC:
        progress.append({
            "Etapa":stage,"Evidencia evaluada":criterion,"Puntaje máximo":points,
            "Estado":"Completa" if saved.get(f"done_{stage}") else "Pendiente",
        })
    progress.append({"Etapa":9,"Evidencia evaluada":"Cuestionario individual","Puntaje máximo":30,"Estado":"Completa" if saved.get("done_9") or quiz_row else "Pendiente"})
    st.dataframe(pd.DataFrame(progress),hide_index=True,use_container_width=True)
    completed=sum(saved.get(f"done_{stage}") is True for stage in range(1,9))
    a,b,c=st.columns(3)
    a.metric("Etapas prácticas",f"{completed}/8")
    b.metric("Cuestionario",f"{quiz_score:g}/30" if saved.get("done_9") or quiz_row else "Pendiente")
    c.metric("Puntaje práctico máximo","70 puntos")

    st.markdown("### 2 · Revisa el informe técnico consolidado")
    st.caption(
        "Este es el informe que se enviará al docente. Cada capítulo recupera el trabajo guardado en la etapa "
        "correspondiente y muestra el puntaje máximo que puede obtener."
    )
    report=_submission_payload(saved)
    done={stage:bool(saved.get(f"done_{stage}")) for stage in range(1,9)}
    quiz_visible=quiz_score if saved.get("done_9") or quiz_row else None
    _render_integrated_report(st,pd,report,done,quiz_visible)
    st.caption("El docente asignará el puntaje después de revisar la calidad técnica, coherencia y trazabilidad de cada sección. Completar campos no otorga automáticamente el puntaje máximo.")

    st.markdown("### 3 · Entrega definitiva")

    declaration=st.checkbox(
        "Declaro que revisé el expediente, que los resultados corresponden a mis modelos y que esta es mi entrega definitiva.",
        key="c4l2_s10_declaration",
    )
    if st.button("ENTREGAR EVALUACIÓN INTEGRAL",type="primary",use_container_width=True,key="c4l2_s10_submit"):
        missing=[str(stage) for stage in range(1,9) if not saved.get(f"done_{stage}")]
        if missing:
            st.warning("Falta completar las Etapas "+", ".join(missing)+" antes de enviar la evaluación integral.")
        elif not (saved.get("done_9") or quiz_row):
            st.warning("Primero debes enviar el cuestionario de la Etapa 9.")
        elif not declaration:
            st.warning("Confirma la declaración de entrega definitiva.")
        else:
            payload=_submission_payload(saved)
            stored=runtime["_submit_evaluation"](
                10,"c4l2_integrated_project","Curso 4 · Laboratorio 2 · Evaluación integral",
                payload,0,70,"Entrega recibida. Pendiente de revisión y puntaje docente.",
                auto_level="Pendiente de revisión docente",
            )
            saved["c4l2_s10_submission_summary"]=payload["evidence_summary"]
            saved["c4l2_s10_submitted"]=True
            saved["done_10"]=True
            runtime["_save"](lab,saved,10)
            if not stored:
                st.warning("La entrega quedó guardada en tu progreso, pero no fue posible registrarla remotamente en este momento.")
            st.rerun()

