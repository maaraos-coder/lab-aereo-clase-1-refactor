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


def _teacher_view(st,pd):
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;padding:17px 19px;
                background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VISTA DOCENTE · EVALUACIÓN INTEGRAL</div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">70 puntos de desarrollo práctico + 30 puntos de cuestionario</div>
      <div style="color:#526f80;line-height:1.55">La Etapa 10 no agrega un ejercicio nuevo. Consolida las evidencias de las Etapas 1 a 8 y deja el expediente bloqueado para revisión. El cuestionario de la Etapa 9 se corrige automáticamente.</div>
    </div>
    """,unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Etapa":stage,"Criterio":criterion,"Puntaje máximo":points}
        for stage,criterion,points in RUBRIC
    ]),hide_index=True,use_container_width=True)
    a,b,c=st.columns(3)
    a.metric("Desarrollo práctico","70 puntos")
    b.metric("Cuestionario","30 puntos")
    c.metric("Total","100 puntos")
    st.markdown("#### Conversión a nota")
    st.write("Exigencia del 60 %: 60 puntos equivalen a nota 4,0 y 100 puntos a nota 7,0.")
    st.info("Revisa cada entrega en **Evaluaciones entregadas**, asigna el puntaje práctico sobre 70 y publica la retroalimentación. La nota final se calculará con ese puntaje más el resultado del cuestionario.")


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
        _teacher_view(st,pd)
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
        st.markdown("### Evidencias incluidas en la entrega")
        summary=_payload(final_row).get("evidence_summary") if final_row else _evidence_summary(saved)
        if not isinstance(summary,dict):summary=_evidence_summary(saved)
        st.dataframe(pd.DataFrame([{"Evidencia":key.replace("_"," ").title(),"Registros":value} for key,value in summary.items()]),hide_index=True,use_container_width=True)
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

    st.markdown("### 2 · Revisa el expediente consolidado")
    summary=_evidence_summary(saved)
    st.dataframe(pd.DataFrame([
        {"Componente":"Vértices del proyecto","Registros":summary["vertices"]},
        {"Componente":"Receptores","Registros":summary["receptors"]},
        {"Componente":"Fuentes acústicas","Registros":summary["sources"]},
        {"Componente":"Frentes originales","Registros":summary["original_fronts"]},
        {"Componente":"Resultados originales","Registros":summary["original_results"]},
        {"Componente":"Estrategias de control","Registros":summary["control_strategies"]},
        {"Componente":"Resultados controlados","Registros":summary["controlled_results"]},
        {"Componente":"Soluciones definitivas","Registros":summary["final_strategies"]},
    ]),hide_index=True,use_container_width=True)

    st.markdown("### 3 · Rúbrica del desarrollo práctico")
    st.dataframe(pd.DataFrame([{"Etapa":stage,"Criterio":criterion,"Puntaje máximo":points} for stage,criterion,points in RUBRIC]),hide_index=True,use_container_width=True)
    st.caption("El docente asignará el puntaje práctico después de revisar la calidad técnica, coherencia y trazabilidad de las evidencias. Completar campos no otorga automáticamente el puntaje máximo.")

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

