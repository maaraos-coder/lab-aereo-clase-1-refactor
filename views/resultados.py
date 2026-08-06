"""Vista de resultados académicos del alumno.

La lógica se conserva sin cambios. ``app.py`` inyecta las dependencias
compartidas antes de ejecutar cada vista para evitar acoplamientos circulares.
"""

_LOCAL_NAMES = {
    "run_view", "_bind_runtime", "_VIEWS", "_LOCAL_NAMES",
    "_results_catalog", "_student_result_payload", "_result_date",
    "_friendly_result_label", "_clean_result_rows",
    "_render_final_exam_result", "_render_comprehension_result",
    "_render_integrated_result", "results_view",
}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _LOCAL_NAMES:
            module_globals[name] = value

def _results_catalog():
    """Describe the ten laboratories for results and teacher release controls."""
    first_course=[]
    for lab_number in (1,2):
        minutes=STAGE_MINUTES if lab_number==1 else dict(enumerate(LAB2_MINUTES))
        stages=[]
        for stage,(prefix,title) in enumerate(LAB_STAGE_TITLES[lab_number]):
            stages.append({
                "title":title,
                "objective":f"{prefix} del Laboratorio {lab_number}.",
                "content_markdown":"",
                "activity_markdown":"",
                "teacher_solution":"",
                "minutes":int(minutes.get(stage,20)),
            })
        first_course.append({
            "id":LABORATORIES[lab_number]["id"],
            "course":"Aislamiento a ruido aéreo",
            "lab":lab_number,
            "stages":stages,
        })
    later=[]
    for lab in FUTURE_LABS.values():
        stages=[]
        for stage,(title,objective,concept,activity) in enumerate(lab["stages"]):
            stages.append({
                "title":title,"objective":objective,
                "content_markdown":concept,"activity_markdown":activity,
                "teacher_solution":"",
                "minutes":20 if stage not in (9,10) else 35,
            })
        later.append({
            "id":lab["id"],"course":lab["course"],"lab":lab["number"],"stages":stages,
        })
    return first_course+later

def _student_result_payload(value):
    """Decode the different answer formats used by both laboratories."""
    payload=value
    for _ in range(3):
        if isinstance(payload,str):
            try:
                payload=json.loads(payload)
            except (json.JSONDecodeError,TypeError):
                return payload
        elif isinstance(payload,dict) and set(payload)=={"value"}:
            payload=payload.get("value")
        else:
            break
    return payload

def _result_date(value):
    if not value:
        return "Fecha no registrada"
    try:
        parsed=dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return parsed.astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y · %H:%M h")
    except (TypeError,ValueError):
        return str(value).replace("T"," ")[:16]

def _friendly_result_label(key):
    labels={
        "t60":"Tiempo de reverberación","volumen":"Volumen",
        "absorcion":"Absorción equivalente","diferencia_costo":"Diferencia de costo",
        "incremento_porcentual":"Incremento porcentual","bandas_criticas":"Bandas críticas",
        "recomendacion":"Recomendación","justificacion":"Justificación",
        "rw":"Rw","c":"C","ctr":"Ctr","description":"Descripción",
        "design_score":"Puntaje de diseño","comprehension_score":"Puntaje de comprensión",
        "wall":"Muro o tabique","window":"Ventana","door":"Puerta",
    }
    return labels.get(str(key),str(key).replace("_"," ").strip().capitalize())

def _clean_result_rows(payload,prefix=""):
    """Create readable rows while excluding persistence-only fields."""
    hidden={"reason","finished_at","rubric_scores","verification_signature","curve","tl","frequencies"}
    rows=[]
    if not isinstance(payload,dict):
        return [(prefix or "Respuesta",payload)]
    for key,value in payload.items():
        if key in hidden or key in {"answers","respuestas_teoricas","caso_integrador","calculated_result","student_result"}:
            continue
        label=f"{prefix} · {_friendly_result_label(key)}" if prefix else _friendly_result_label(key)
        if isinstance(value,dict):
            rows.extend(_clean_result_rows(value,label))
        elif isinstance(value,list):
            rows.append((label,", ".join(map(str,value)) if value else "Sin selección"))
        elif value not in (None,""):
            rows.append((label,value))
    return rows

def _render_final_exam_result(payload):
    theory=float(payload.get("puntaje_teorico",0) or 0)
    case=float(payload.get("puntaje_caso",0) or 0)
    hits=int(payload.get("aciertos_teoricos",0) or 0)
    c1,c2,c3=st.columns(3)
    c1.metric("Aciertos teóricos",f"{hits}/29")
    c2.metric("Puntaje teórico",f"{theory:g}/80")
    c3.metric("Caso integrador",f"{case:g}/20")
    case_data=payload.get("caso_integrador",{})
    if isinstance(case_data,dict) and case_data:
        st.markdown("**Caso profesional integrador**")
        table=pd.DataFrame(
            [{"Parámetro":_friendly_result_label(k),"Respuesta":", ".join(map(str,v)) if isinstance(v,list) else v}
             for k,v in case_data.items() if v not in (None,"")]
        )
        if not table.empty:
            st.dataframe(table,hide_index=True,use_container_width=True)

def _render_comprehension_result(payload):
    answers=payload.get("answers",{}) if isinstance(payload,dict) else {}
    if not isinstance(answers,dict):
        return
    correct=0
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i),"Sin respuesta")
        expected=item["options"][item["correct"]]
        is_correct=chosen==expected
        correct+=int(is_correct)
        with st.expander(f"{'✅' if is_correct else '❌'} Pregunta {i+1} · {item['title']}"):
            st.write(f"**Tu respuesta:** {chosen}")
            st.caption("La pauta y explicación se muestran cuando corresponda según la liberación docente.")
    st.caption(f"Respuestas correctas: {correct} de {len(STAGE9_QUESTIONS)}")

def _render_integrated_result(payload):
    calculated=payload.get("calculated_result",{}) if isinstance(payload,dict) else {}
    student=payload.get("student_result",{}) if isinstance(payload,dict) else {}
    c1,c2,c3=st.columns(3)
    c1.metric("Rw calculado",f"{calculated.get('rw','—')} dB")
    c2.metric("C",f"{calculated.get('c','—')} dB")
    c3.metric("Ctr",f"{calculated.get('ctr','—')} dB")
    components=[]
    for key,label in (("wall","Muro o tabique"),("window","Ventana"),("door","Puerta")):
        data=payload.get(key,{})
        if isinstance(data,dict):
            components.append({"Elemento":label,"Solución":data.get("description","Sin información"),"Rw":data.get("rw","—")})
    if components:
        st.dataframe(pd.DataFrame(components),hide_index=True,use_container_width=True)
    if student:
        st.caption(f"Resultado ingresado por el alumno: Rw {student.get('rw','—')} dB · C {student.get('c','—')} dB · Ctr {student.get('ctr','—')} dB")

def results_view(client,catalog,user_key):
    """Student-facing academic results center; never exposes raw JSON."""
    header("MIS RESULTADOS","Tu avance académico","Revisa tus actividades, evaluaciones y observaciones docentes.")
    if client is None:
        st.info("Los resultados estarán disponibles cuando la aplicación recupere la conexión permanente.")
        return
    try:
        rows=(client.table("responses").select("*").eq("user_key",user_key)
              .in_("class_id",[LABORATORIES[1]["id"],LABORATORIES[2]["id"]])
              .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar tus resultados en este momento: {exc}")
        return
    if not rows:
        st.info("Todavía no tienes actividades enviadas. Tus resultados aparecerán aquí después del primer envío.")
        return

    earned=sum(float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0) for r in rows)
    maximum=sum(float(r.get("max_score") or 0) for r in rows)
    percent=(100*earned/maximum) if maximum else 0
    reviewed=sum(r.get("teacher_score") is not None or r.get("status")=="reviewed" for r in rows)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Puntaje registrado",f"{earned:g} de {maximum:g}")
    c2.metric("Porcentaje",f"{percent:.1f} %")
    c3.metric("Actividades enviadas",f"{len(rows)}")
    c4.metric("Revisadas por docente",f"{reviewed} de {len(rows)}")
    st.progress(min(1.0,max(0.0,percent/100)))

    for lab_number,lab in LABORATORIES.items():
        lab_rows=[r for r in rows if r.get("class_id")==lab["id"]]
        st.markdown(f"### Laboratorio {lab_number}")
        if not lab_rows:
            st.caption("Aún no hay actividades enviadas en este laboratorio.")
            continue
        lab_earned=sum(float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0) for r in lab_rows)
        lab_max=sum(float(r.get("max_score") or 0) for r in lab_rows)
        st.caption(f"{len(lab_rows)} actividades registradas · {lab_earned:g} de {lab_max:g} puntos obtenidos")
        for row in lab_rows:
            score=float(row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score") or 0)
            max_score=float(row.get("max_score") or 0)
            reviewed_now=row.get("teacher_score") is not None or row.get("status")=="reviewed"
            title=row.get("question_text") or f"Etapa {row.get('stage','—')}"
            with st.expander(f"{'✅' if score>=.6*max_score else '🟡'} {title} · {score:g}/{max_score:g} puntos"):
                a,b,c=st.columns(3)
                a.metric("Puntaje",f"{score:g}/{max_score:g}")
                b.metric("Estado","Revisado" if reviewed_now else "Enviado")
                c.metric("Fecha",_result_date(row.get("submitted_at") or row.get("updated_at")))
                payload=_student_result_payload(row.get("answer"))
                key=row.get("question_key")
                if key=="final_exam" and isinstance(payload,dict):
                    _render_final_exam_result(payload)
                elif key=="final_comprehension" and isinstance(payload,dict):
                    _render_comprehension_result(payload)
                elif key=="final_integrated_design" and isinstance(payload,dict):
                    _render_integrated_result(payload)
                else:
                    clean=_clean_result_rows(payload)
                    if clean:
                        st.markdown("**Tu respuesta**")
                        st.dataframe(pd.DataFrame(clean,columns=["Parámetro","Respuesta"]),hide_index=True,use_container_width=True)
                    else:
                        st.caption("La respuesta fue registrada correctamente.")
                note=row.get("teacher_note")
                if note:
                    st.info(f"**Retroalimentación docente:** {note}")
                elif not reviewed_now:
                    st.caption("Pendiente de revisión docente.")

_VIEWS = {
    "_results_catalog": _results_catalog,
    "results_view": results_view,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
