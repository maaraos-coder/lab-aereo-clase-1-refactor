"""Vista docente y centro de resultados.

Las funciones conservan su lógica original. ``app.py`` inyecta las
dependencias compartidas antes de cada ejecución para mantener compatibilidad
con el estado, la navegación y los servicios existentes.
"""

_RUNTIME_PROTECTED = {
    "run_view", "_bind_runtime", "_VIEWS", "_RUNTIME_PROTECTED",
}

def _bind_runtime(runtime):
    """Inyecta dependencias compartidas sin sobrescribir la infraestructura."""
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and name not in _VIEWS:
            module_globals[name] = value

def _teacher_group_review_impl(stage,solutions):
    if st.session_state.get("role")!="Docente":
        return
    st.markdown('<div class="teacher-only"><b>👥 Revisión grupal de respuestas</b>'
                '<span>Seleccione una respuesta y revele la pauta solamente cuando decida discutirla con el curso.</span></div>',
                unsafe_allow_html=True)
    client=_supabase()
    remote=client is not None
    if remote:
        raw=client.table("responses").select("*,users(display_name)").eq(
            "class_id",CLASS_ID).eq("stage",stage).order("question_key").order("updated_at").execute().data or []
        rows=[(r["id"],r.get("updated_at",""),(r.get("users") or {}).get("display_name","Alumno"),
               r["question_key"],r["question_text"],
               (r.get("answer") or {}).get("value",json.dumps(r.get("answer") or {},ensure_ascii=False)),
               r.get("auto_level"),r.get("feedback"),r.get("teacher_level"),
               float(r.get("auto_score") or 0),float(r.get("max_score") or 0),
               None if r.get("teacher_score") is None else float(r["teacher_score"]),
               r.get("teacher_note")) for r in raw]
    else:
        with _activity_db() as con:
            rows=con.execute(
            "SELECT id,created_at,student,question_key,question,answer,auto_level,feedback,teacher_level,"
            "auto_score,max_score,teacher_score,teacher_note "
            "FROM formative_responses WHERE stage=? ORDER BY question_key,created_at",(stage,)).fetchall()
    if not rows:
        st.info("Todavía no hay respuestas guardadas de alumnos para esta etapa.")
        return
    labels=[f"{r[3]} · {r[2]} · {r[1].replace('T',' ')}" for r in rows]
    selected=st.selectbox("Respuesta para revisar",range(len(rows)),format_func=lambda i:labels[i],key=f"review_{stage}")
    rid,_,student,qkey,question,answer,auto_level,feedback,teacher_level,auto_score,max_score,teacher_score,teacher_note=rows[selected]
    anonymous=st.toggle("Ocultar nombre al proyectar",value=True,key=f"anon_{stage}")
    st.markdown(f"**Pregunta:** {question}")
    st.markdown(f"**Respuesta de {'Alumno/a' if anonymous else student}:**")
    st.info(answer)
    st.caption(f"Evaluación automática inicial: {auto_level} · {auto_score:g}/{max_score:g} puntos. {feedback or ''}")
    solution=solutions.get(qkey,"Revise la pauta técnica asociada a esta pregunta.")
    if st.toggle("Mostrar solución esperada",key=f"reveal_{stage}"):
        st.success(solution)
    st.markdown("##### Control de la pantalla compartida")
    p1,p2,p3,p4=st.columns(4)
    if p1.button("Mostrar pregunta",key=f"project_q_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,False,False)
        st.success("Pregunta enviada a la vista de alumnos.")
    if p2.button("Mostrar respuesta",key=f"project_a_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,True,False)
        st.success("Respuesta anonimizada enviada a la vista de alumnos.")
    if p3.button("Revelar solución",key=f"project_s_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,True,True)
        st.success("Solución revelada en la vista de alumnos.")
    if p4.button("Limpiar pantalla",key=f"project_clear_{stage}_{rid}",use_container_width=True):
        _set_projection()
        st.success("Pantalla de proyección limpiada.")
    levels=["Sin revisar","Correcta","Parcialmente correcta","Incorrecta"]
    current=levels.index(teacher_level) if teacher_level in levels else 0
    mark=st.selectbox("Evaluación docente",levels,index=current,key=f"mark_{stage}_{rid}")
    manual=st.number_input(
        "Puntaje docente",min_value=0.0,max_value=float(max_score),value=float(teacher_score if teacher_score is not None else auto_score),
        step=0.5,key=f"teacher_score_{stage}_{rid}",
        help="Este puntaje reemplaza la corrección automática en el contador del alumno.",
    )
    note=st.text_area("Observación para el alumno",value=teacher_note or "",key=f"teacher_note_{stage}_{rid}")
    if st.button("Guardar evaluación docente",key=f"save_mark_{stage}_{rid}"):
        if remote:
            client.table("responses").update({
                "teacher_level":mark,"teacher_score":manual,"teacher_note":note,
                "status":"reviewed","updated_at":_now(),
            }).eq("id",rid).execute()
        else:
            with _activity_db() as con:
                con.execute(
                "UPDATE formative_responses SET teacher_level=?,teacher_score=?,teacher_note=? WHERE id=?",
                (mark,manual,note,rid),
                )
        st.success("Evaluación docente y puntaje guardados.")
    if remote:
        summary_rows={}
        for r in raw:
            name=(r.get("users") or {}).get("display_name","Alumno")
            item=summary_rows.setdefault(name,{"Alumno":name,"Puntaje":0.0,"Respondido_sobre":0.0,"Actividades":0})
            item["Puntaje"]+=float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0)
            item["Respondido_sobre"]+=float(r.get("max_score") or 0);item["Actividades"]+=1
        summary=pd.DataFrame(summary_rows.values())
    else:
        with _activity_db() as con:
            summary=pd.read_sql_query(
            """SELECT student AS Alumno,
            ROUND(SUM(COALESCE(teacher_score,auto_score)),1) AS Puntaje,
            ROUND(SUM(max_score),1) AS Respondido_sobre,
            COUNT(*) AS Actividades
            FROM formative_responses WHERE stage=? GROUP BY student ORDER BY Puntaje DESC""",
                con,params=(stage,),
            )
    with st.expander("Panel de resultados de la etapa"):
        st.dataframe(summary,hide_index=True,use_container_width=True)
        st.download_button(
            "Descargar resultados CSV",summary.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"resultados_etapa_{stage}.csv",mime="text/csv",key=f"download_scores_{stage}",
        )

def _teacher_student_management_impl():
    """Reset one stage, reset all work, or remove a test student."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    remote=client is not None
    if remote:
        response_users=client.table("responses").select("user_key").eq("class_id",CLASS_ID).execute().data or []
        keys=sorted({r["user_key"] for r in response_users})
        users=client.table("users").select("user_key,display_name").in_("user_key",keys).execute().data if keys else []
        student_map={u["display_name"]:u["user_key"] for u in users}
        students=sorted(student_map)
    else:
        with _activity_db() as con:
            students=[r[0] for r in con.execute(
            "SELECT DISTINCT student FROM formative_responses ORDER BY student"
            ).fetchall()]
    if not students:
        st.info("Todavía no hay alumnos con respuestas guardadas.")
        return
    student=st.selectbox("Alumno",students,key="manage_student")
    scope=st.selectbox(
        "Alcance del reinicio",
        ["Curso completo"]+[f"Etapa {n}" for n in sorted(APPLICATION_POINTS)],
        key="manage_scope",
    )
    confirm=st.checkbox(
        f"Confirmo que deseo modificar los registros de {student}",
        key="manage_confirm",
    )
    c1,c2=st.columns(2)
    if c1.button("Reiniciar respuestas",disabled=not confirm,use_container_width=True):
        if remote:
            user_key=student_map[student]
            query=client.table("responses").delete().eq("class_id",CLASS_ID).eq("user_key",user_key)
            if scope!="Curso completo":
                query=query.eq("stage",int(scope.split()[-1]))
            query.execute()
            if scope=="Curso completo":
                client.table("user_progress").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
        else:
          with _activity_db() as con:
            if scope=="Curso completo":
                con.execute("DELETE FROM formative_responses WHERE student=?",(student,))
                con.execute("DELETE FROM user_progress WHERE display_name=?",(student,))
            else:
                stage_number=int(scope.split()[-1])
                con.execute(
                    "DELETE FROM formative_responses WHERE student=? AND stage=?",
                    (student,stage_number),
                )
                rows=con.execute(
                    "SELECT user_key,state_json FROM user_progress WHERE display_name=?",(student,)
                ).fetchall()
                prefixes={
                    3:("s3","ans_s3","checked_s3"),5:("s5","ans_s5","checked_s5"),
                    7:("s7","ans_s7","checked_s7"),9:("s9","e9_","ans_e9","checked_e9"),
                    10:("q","exam_","case_","final_"),
                }.get(stage_number,(f"s{stage_number}",f"ans_s{stage_number}",f"checked_s{stage_number}"))
                for user_key,state_json in rows:
                    try:
                        state=json.loads(state_json)
                    except (TypeError,json.JSONDecodeError):
                        state={}
                    state={k:v for k,v in state.items() if not k.startswith(prefixes)}
                    con.execute(
                        "UPDATE user_progress SET state_json=?,updated_at=? WHERE user_key=?",
                        (json.dumps(state,ensure_ascii=False),
                         dt.datetime.now().isoformat(timespec="seconds"),user_key),
                    )
        st.success(f"Se reiniciaron las respuestas de {student} en: {scope.lower()}.")
        st.rerun()
    if c2.button("Eliminar alumno de prueba",disabled=not confirm,use_container_width=True):
        if remote:
            user_key=student_map[student]
            client.table("responses").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
            client.table("user_progress").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
            client.table("enrollments").delete().eq("course_id",COURSE_ID).eq("user_key",user_key).execute()
            client.table("users").delete().eq("user_key",user_key).execute()
        else:
            with _activity_db() as con:
                con.execute("DELETE FROM formative_responses WHERE student=?",(student,))
                con.execute("DELETE FROM user_progress WHERE display_name=?",(student,))
        st.success(f"Se eliminó el registro de prueba de {student}.")
        st.rerun()

def _teacher_publication_management_impl():
    """Let the teacher reveal a laboratory only when it is ready to be taught."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    if client is None:
        st.warning("Supabase debe estar conectado para administrar publicaciones.")
        return
    st.markdown("#### Publicación de laboratorios")
    try:
        classes=_course_classes(client)
    except Exception:
        st.error("No fue posible consultar el estado de publicación.")
        return
    for item in classes:
        number=item.get("class_number")
        if number not in LABORATORIES:
            continue
        published=item.get("status")=="published"
        label=f"Laboratorio {number}"
        st.caption(f"{label}: {'publicado para alumnos' if published else 'oculto para alumnos'}")
        action="Ocultar laboratorio" if published else "Publicar laboratorio"
        if st.button(action,key=f"publication_{number}",use_container_width=True):
            new_status="draft" if published else "published"
            client.table("classes").update(
                {"status":new_status,"updated_at":_now()}
            ).eq("id",item["id"]).execute()
            _clear_course_cache()
            st.success(f"{label} quedó {'publicado' if new_status=='published' else 'oculto'}.")
            st.rerun()

def _teacher_stage9_results_impl(compact=False):
    """Teacher-only automatic rubric and editable grading for Stage 9."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    if client is None:
        st.warning("Conecta Supabase para consultar las respuestas de los alumnos.")
        return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)")
             .eq("class_id","clase-02-aislamiento-ruido-aereo-minvu").eq("stage",9)
             .eq("question_key","final_comprehension")
             .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.error(f"No fue posible consultar las respuestas de la Etapa 9: {exc}")
        return
    if not raw:
        st.info("Todavía no hay evaluaciones de la Etapa 9 enviadas por alumnos.")
        return

    def student_name(row):
        user=row.get("users") or {}
        return user.get("display_name") or row.get("user_key","Alumno")

    selected=st.selectbox(
        "Alumno evaluado",range(len(raw)),
        format_func=lambda i:f"{student_name(raw[i])} · {float(raw[i].get('auto_score') or 0):g}/40",
        key=f"stage9_teacher_student_{'compact' if compact else 'full'}",
    )
    row=raw[selected]
    payload=_stage9_answer_payload(row)
    answers=payload.get("answers",{}) if isinstance(payload,dict) else {}
    st.caption(
        f"Respuesta recibida: {str(row.get('updated_at') or '').replace('T',' ')[:19]} · "
        "guardada en Supabase, tabla responses, clave final_comprehension."
    )

    automatic=[]
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i)) if isinstance(answers,dict) else None
        correct=item["options"][item["correct"]]
        automatic.append(4.0 if chosen==correct else 0.0)

    st.markdown("#### Rúbrica automática editable")
    st.caption("La pauta asigna 4 puntos por respuesta correcta. El docente puede ajustar cada criterio entre 0 y 4 puntos y dejar la justificación correspondiente.")
    awarded=[]
    current_total=row.get("teacher_score")
    saved_rubric=payload.get("rubric_scores",[]) if isinstance(payload,dict) else []
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i)) if isinstance(answers,dict) else None
        correct=item["options"][item["correct"]]
        with st.expander(
            f"{i+1}. {item['title']} · {'Correcta' if chosen==correct else 'Incorrecta'} · {automatic[i]:g}/4",
            expanded=(not compact and i==0),
        ):
            st.markdown(f"**Pregunta:** {item['question']}")
            st.write(f"**Respuesta del alumno:** {chosen or 'Sin respuesta'}")
            st.success(f"**Respuesta correcta:** {correct}")
            st.info(item["explanation"])
            default=(float(saved_rubric[i]) if i<len(saved_rubric) else automatic[i])
            awarded.append(st.number_input(
                "Puntaje otorgado",0.0,4.0,float(default),0.5,
                key=f"stage9_rubric_{row['id']}_{i}_{'c' if compact else 'f'}",
            ))
    total=float(sum(awarded))
    note=st.text_area(
        "Observación general para el alumno",value=row.get("teacher_note") or "",
        key=f"stage9_note_{row['id']}_{'c' if compact else 'f'}",
    )
    automatic_total=float(sum(automatic))
    automatic_grade=_grade_from_percent(automatic_total/40*100)
    adjusted_grade=_grade_from_percent(total/40*100)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Puntaje automático",f"{automatic_total:g}/40")
    c2.metric("Nota automática",f"{automatic_grade:.1f}")
    c3.metric("Puntaje ajustado",f"{total:g}/40")
    c4.metric("Nota ajustada",f"{adjusted_grade:.1f}")
    if st.button("Guardar rúbrica docente",type="primary",use_container_width=True,
                 key=f"stage9_save_rubric_{row['id']}_{'c' if compact else 'f'}"):
        updated_payload=dict(payload)
        updated_payload["rubric_scores"]=awarded
        client.table("responses").update({
            "answer":updated_payload,
            "teacher_level":"Correcta" if total>=24 else "Incorrecta",
            "teacher_score":total,"teacher_note":note,
            "status":"reviewed","updated_at":_now(),
        }).eq("id",row["id"]).execute()
        st.success("Rúbrica y observación docente guardadas.")

    summary=[]
    for result in raw:
        result_payload=_stage9_answer_payload(result)
        result_answers=result_payload.get("answers",{}) if isinstance(result_payload,dict) else {}
        answered=sum(bool(result_answers.get(str(i))) for i in range(10))
        summary.append({
            "Alumno":student_name(result),"Respondidas":f"{answered}/10",
            "Puntaje automático":float(result.get("auto_score") or 0),
            "Nota automática":round(_grade_from_percent(float(result.get("auto_score") or 0)/40*100),1),
            "Puntaje docente":result.get("teacher_score"),
            "Nota final":round(_grade_from_percent(float(result.get("teacher_score") if result.get("teacher_score") is not None else result.get("auto_score") or 0)/40*100),1),
            "Estado":"Revisada" if result.get("teacher_score") is not None else "Corrección automática",
        })
    frame=pd.DataFrame(summary)
    with st.expander("Resumen y descarga del curso"):
        st.dataframe(frame,hide_index=True,use_container_width=True)
        st.download_button(
            "Descargar resultados CSV",frame.to_csv(index=False).encode("utf-8-sig"),
            "resultados_etapa_9.csv","text/csv",
            key=f"stage9_download_{'c' if compact else 'f'}",
        )

def _teacher_stage9_answer_key_impl():
    """Teacher view of the assessment: alternatives and key, never answer controls."""
    st.info("Vista docente: esta pantalla es una pauta de consulta. No inicia el temporizador ni permite desarrollar la evaluación.")
    for i,item in enumerate(STAGE9_QUESTIONS):
        correct=item["options"][item["correct"]]
        with st.expander(f"Pregunta {i+1} · {item['title']}",expanded=i==0):
            st.markdown(f"**{item['question']}**")
            for option_index,option in enumerate(item["options"]):
                prefix="✅" if option_index==item["correct"] else "○"
                st.write(f"{prefix} {chr(65+option_index)}. {option}")
            st.success(f"Respuesta correcta: {correct}")
            st.info(item["explanation"])

def _teacher_lab1_final_results_impl(compact=False):
    """Resultados de la evaluación final (Etapa 10) del Laboratorio 1."""
    client=_supabase()
    if client is None:
        st.warning("Conecta Supabase para consultar las respuestas de los alumnos.")
        return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)")
             .eq("class_id",CLASS_ID).eq("stage",10)
             .eq("question_key","final_exam")
             .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.error(f"No fue posible consultar la evaluación del Laboratorio 1: {exc}")
        return
    if not raw:
        st.info("Todavía no hay evaluaciones finales enviadas en el Laboratorio 1.")
        return

    def student_name(row):
        user=row.get("users") or {}
        return user.get("display_name") or user.get("email") or row.get("user_key","Alumno")

    selected=st.selectbox(
        "Alumno evaluado",range(len(raw)),
        format_func=lambda i:f"{student_name(raw[i])} · {float(raw[i].get('auto_score') or 0):.1f}/100",
        key=f"teacher_lab1_final_student_{'compact' if compact else 'full'}",
    )
    row=raw[selected]
    payload=_stage9_answer_payload(row)
    answers=payload.get("respuestas_teoricas",{}) if isinstance(payload,dict) else {}
    theory_hits=int(payload.get("aciertos_teoricos",0) or 0) if isinstance(payload,dict) else 0
    case_score=float(payload.get("puntaje_caso",0) or 0) if isinstance(payload,dict) else 0
    auto_score=float(row.get("auto_score") or 0)
    st.caption(f"Envío: {str(row.get('updated_at') or '').replace('T',' ')[:19]} · Laboratorio 1 · Etapa 10")
    automatic_grade=_grade_from_percent(auto_score)
    effective_score=float(row.get("teacher_score") if row.get("teacher_score") is not None else auto_score)
    effective_grade=_grade_from_percent(effective_score)
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Aciertos teóricos",f"{theory_hits}/29")
    c2.metric("Caso integrador",f"{case_score:g}/20")
    c3.metric("Puntaje automático",f"{auto_score:.1f}/100")
    c4.metric("Nota automática",f"{automatic_grade:.1f}")
    c5.metric("Nota vigente",f"{effective_grade:.1f}")

    with st.expander("Respuestas 1 a 29",expanded=not compact):
        for i,(question,options,correct_index) in enumerate(LAB1_QUESTIONS):
            chosen_raw=answers.get(str(i),answers.get(i)) if isinstance(answers,dict) else None
            try: chosen_index=int(chosen_raw) if chosen_raw is not None else None
            except (TypeError,ValueError): chosen_index=None
            chosen=options[chosen_index] if chosen_index is not None and 0<=chosen_index<len(options) else "Sin respuesta"
            correct=options[correct_index]
            icon="✅" if chosen_index==correct_index else "❌"
            st.markdown(f"**{icon} {i+1}. {question}**")
            st.write(f"Respuesta del alumno: {chosen}")
            st.caption(f"Respuesta correcta: {correct}")

    with st.expander("Pregunta 30 · Caso profesional integrador"):
        case=payload.get("caso_integrador",{}) if isinstance(payload,dict) else {}
        if case:
            st.write(f"T₆₀ calculado: {case.get('t60','Sin respuesta')}")
            st.write(f"Diferencia de costo: {case.get('diferencia_costo','Sin respuesta')}")
            st.write(f"Incremento porcentual: {case.get('incremento_porcentual','Sin respuesta')}")
            st.write(f"Bandas críticas: {case.get('bandas_criticas',[])}")
            st.write(f"Recomendación: {case.get('recomendacion','Sin respuesta')}")
            st.write(f"Justificación: {case.get('justificacion','Sin respuesta')}")
        else:
            st.info("Este envío pertenece a una versión anterior: conserva el puntaje del caso, pero no el detalle de sus campos.")
        st.success("Pauta: T₆₀≈0,40 s; $300.000; 16,7 %; bandas 125, 250 y 500 Hz; Solución B con justificación técnica y económica.")

    st.markdown("#### Rúbrica automática editable")
    adjusted=st.number_input(
        "Puntaje final otorgado por el docente",0.0,100.0,
        float(row.get("teacher_score") if row.get("teacher_score") is not None else auto_score),0.5,
        key=f"teacher_lab1_final_score_{row['id']}_{'c' if compact else 'f'}",
    )
    adjusted_grade=_grade_from_percent(adjusted)
    st.info(f"Nota calculada con el puntaje ajustado: **{adjusted_grade:.1f}** · Exigencia de aprobación: 60 % (nota 4,0).")
    note=st.text_area("Observación docente",value=row.get("teacher_note") or "",
                      key=f"teacher_lab1_final_note_{row['id']}_{'c' if compact else 'f'}")
    if st.button("Guardar revisión del Laboratorio 1",type="primary",use_container_width=True,
                 key=f"teacher_lab1_final_save_{row['id']}_{'c' if compact else 'f'}"):
        client.table("responses").update({
            "teacher_level":"Correcta" if adjusted>=60 else "Incorrecta",
            "teacher_score":adjusted,"teacher_note":note,"status":"reviewed","updated_at":_now(),
        }).eq("id",row["id"]).execute()
        st.success("Puntaje y observación docente guardados.")

def _teacher_course_results_impl(compact=False):
    """Centro docente de las evaluaciones calificadas del curso.

    La nota del curso se obtiene exclusivamente con las evaluaciones del
    Laboratorio 2: Etapa 9 (40 puntos) y Etapa 10 (60 puntos).
    """
    if st.session_state.get("role") != "Docente":
        return

    st.markdown("### Evaluaciones entregadas por los alumnos")
    st.caption(
        "La nota del curso se calcula únicamente con el Laboratorio 2: "
        "Etapa 9 (40 puntos) y Etapa 10 (60 puntos). La nota final se publica "
        "cuando ambas evaluaciones han sido entregadas."
    )

    client = _supabase()
    if client is not None:
        try:
            all_rows = (
                client.table("responses")
                .select("*,users(display_name,email)")
                .eq("class_id", "clase-02-aislamiento-ruido-aereo-minvu")
                .in_("question_key", ["final_comprehension", "final_integrated_design"])
                .order("updated_at", desc=True)
                .execute().data
                or []
            )

            consolidated = {}
            seen = set()
            for row in all_rows:
                user = row.get("users") or {}
                user_key = row.get("user_key") or user.get("email") or str(row.get("id"))
                question_key = row.get("question_key")

                # La consulta viene ordenada desde la entrega más reciente. Si
                # existieran duplicados, se utiliza solamente el último registro.
                unique_key = (user_key, question_key)
                if unique_key in seen:
                    continue
                seen.add(unique_key)

                item = consolidated.setdefault(
                    user_key,
                    {
                        "Alumno": user.get("display_name") or user.get("email") or user_key,
                        "Lab. 2 · Etapa 9": "Pendiente",
                        "Lab. 2 · Etapa 10": "Pendiente",
                        "Avance": "0 de 2",
                        "Nota final": "Pendiente",
                        "Estado": "Sin entregas",
                        "_stage9_score": None,
                        "_stage10_score": None,
                        "_reviewed": False,
                    },
                )

                score = row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score")
                score = float(score or 0)
                if row.get("teacher_score") is not None or row.get("status") == "reviewed":
                    item["_reviewed"] = True

                if question_key == "final_comprehension":
                    item["_stage9_score"] = score
                    item["Lab. 2 · Etapa 9"] = f"{score:.1f}/40"
                elif question_key == "final_integrated_design":
                    item["_stage10_score"] = score
                    item["Lab. 2 · Etapa 10"] = f"{score:.1f}/60"

            for item in consolidated.values():
                delivered = int(item["_stage9_score"] is not None) + int(item["_stage10_score"] is not None)
                item["Avance"] = f"{delivered} de 2"

                if delivered == 2:
                    total = item["_stage9_score"] + item["_stage10_score"]
                    item["Nota final"] = f"{total:.1f}% · Nota {_grade_from_percent(total):.1f}"
                    item["Estado"] = "Con revisión docente" if item["_reviewed"] else "Corrección automática"
                elif delivered == 1:
                    partial = item["_stage9_score"] if item["_stage9_score"] is not None else item["_stage10_score"]
                    maximum = 40 if item["_stage9_score"] is not None else 60
                    item["Nota final"] = "Pendiente"
                    item["Estado"] = f"Evaluación incompleta · {partial:.1f}/{maximum} puntos registrados"
                else:
                    item["Nota final"] = "Pendiente"
                    item["Estado"] = "Sin entregas"

                item.pop("_stage9_score", None)
                item.pop("_stage10_score", None)
                item.pop("_reviewed", None)

            if consolidated:
                with st.expander("Resumen acumulado de todos los alumnos"):
                    summary_frame = pd.DataFrame(consolidated.values())
                    st.dataframe(summary_frame, hide_index=True, width="stretch")
                    st.download_button(
                        "Descargar consolidado CSV",
                        summary_frame.to_csv(index=False).encode("utf-8-sig"),
                        "resultados_curso_1.csv",
                        "text/csv",
                        key=f"course_results_csv_{'compact' if compact else 'full'}",
                    )
            else:
                st.info("Todavía no hay evaluaciones calificadas del Laboratorio 2.")
        except Exception as exc:
            st.warning(f"No fue posible construir el resumen acumulado: {exc}")

    evaluations = {
        "Laboratorio 2 · Etapa 9 · Evaluación de comprensión": ("stage9", 40),
        "Laboratorio 2 · Etapa 10 · Diseño integrador": ("stage10", 60),
    }
    label = st.selectbox(
        "Evaluación",
        list(evaluations),
        key=f"course_results_evaluation_{'compact' if compact else 'full'}",
    )
    kind, _ = evaluations[label]
    if kind == "stage9":
        _teacher_stage9_results_impl(compact=compact)
    else:
        _teacher_lab2_integrated_results_impl(compact=compact)

def _teacher_lab2_integrated_results_impl(compact=False):
    client=_supabase()
    if client is None:
        st.info("Los resultados estarán disponibles al conectar la aplicación.")
        return
    try:
        rows=(client.table("responses").select("*,users(display_name,email)")
              .eq("class_id","clase-02-aislamiento-ruido-aereo-minvu")
              .eq("question_key","final_integrated_design").execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar los desarrollos: {exc}"); return
    if not rows:
        st.info("Todavía no hay desarrollos enviados en la Etapa 10 del Laboratorio 2."); return
    labels=[]
    for row in rows:
        user=row.get("users") or {}; labels.append(f"{user.get('display_name') or user.get('email') or row.get('user_key')} · {str(row.get('updated_at') or '')[:16]}")
    idx=st.selectbox("Alumno",range(len(rows)),format_func=lambda i:labels[i],key=f"teacher_l2s10_student_{'c' if compact else 'f'}")
    row=rows[idx]; payload=row.get("answer") or {}
    if isinstance(payload,dict) and "value" in payload:
        try: payload=json.loads(payload["value"])
        except Exception: payload={}
    result=payload.get("calculated_result",{}) if isinstance(payload,dict) else {}
    student=payload.get("student_result",{}) if isinstance(payload,dict) else {}
    st.markdown(f"**Resultado calculado:** Rw(C; Ctr) = {result.get('rw','—')} ({result.get('c','—')}; {result.get('ctr','—')}) dB")
    st.write(f"Respuesta ingresada por el alumno: Rw={student.get('rw','—')} dB · C={student.get('c','—')} dB · Ctr={student.get('ctr','—')} dB")
    for label,key in (("Muro/tabique","wall"),("Ventana","window"),("Puerta","door")):
        data=payload.get(key,{}) if isinstance(payload,dict) else {}; st.write(f"**{label}:** {data.get('description','Sin información')} · Rw {data.get('rw','—')} dB")
    st.write(f"Puntaje de diseño: {payload.get('design_score',0):g}/40 · Comprensión: {payload.get('comprehension_score',0):g}/20")
    auto_score=float(row.get("auto_score") or 0)
    current=row.get("teacher_score") if row.get("teacher_score") is not None else auto_score
    c1,c2,c3=st.columns(3)
    c1.metric("Puntaje automático",f"{auto_score:g}/60")
    c2.metric("Nota automática",f"{_grade_from_percent(auto_score/60*100):.1f}")
    c3.metric("Estado","Revisada" if row.get("teacher_score") is not None else "Corrección automática")
    adjusted=st.number_input("Puntaje docente",0.,60.,float(current),1.,key=f"teacher_l2s10_score_{row.get('id')}_{compact}")
    st.info(f"Nota calculada con el puntaje ajustado: **{_grade_from_percent(adjusted/60*100):.1f}** · Exigencia 60 %.")
    note=st.text_area("Observación docente",value=row.get("teacher_note") or "",key=f"teacher_l2s10_note_{row.get('id')}_{compact}")
    if st.button("Guardar revisión del diseño integrador",type="primary",key=f"teacher_l2s10_save_{row.get('id')}_{compact}"):
        client.table("responses").update({"teacher_score":adjusted,"teacher_note":note,"teacher_level":"Correcta" if adjusted>=36 else "Parcialmente correcta","status":"reviewed","updated_at":_now()}).eq("id",row["id"]).execute(); st.success("Revisión guardada.")

def _teacher_lab2_stage10_answer_key_impl():
    """Pauta docente de la Etapa 10, sin controles destinados al alumno."""
    st.info(
        "Vista docente: esta pantalla muestra la pauta y los resultados correctos. "
        "No permite seleccionar sistemas, ingresar valores, contestar preguntas ni enviar el ejercicio."
    )
    st.markdown("### Pauta del cálculo integrador")
    st.latex(r"\tau_{T,f}=\frac{19{,}71\,10^{-R_{m,f}/10}+2{,}40\,10^{-R_{v,f}/10}+1{,}89\,10^{-R_{p,f}/10}}{24{,}00}")
    st.latex(r"R_{T,f}=-10\log_{10}(\tau_{T,f})")
    st.success(
        "Resultado correcto del procedimiento: combinar las curvas por transmisión y superficie "
        "en cada tercio de octava; con la curva combinada construir Rw y calcular C y Ctr. "
        "El diseño cumple cuando Rw ≥ 40 dB. El valor numérico depende de la solución seleccionada por cada alumno."
    )
    _lab2_s10_teacher_solved_examples_impl()
    st.markdown("### Pauta · Preguntas de comprensión")
    for i,(question,options,correct) in enumerate(LAB2_S10_QUESTIONS):
        with st.expander(f"Pregunta {i+1}",expanded=i==0):
            st.markdown(f"**{question}**")
            for option_index,option in enumerate(options):
                prefix="✅" if option_index==correct else "○"
                st.write(f"{prefix} {chr(65+option_index)}. {option}")
            st.success(f"Respuesta correcta: {options[correct]}")
            st.info(LAB2_S10_EXPLANATIONS[i])

def _lab2_s10_teacher_solved_examples_impl():
    """Ejemplos numéricos resueltos, visibles únicamente en la pauta docente."""
    examples=[]

    wall_a=_lab2_s10_single("Ladrillo cerámico",120)
    window_a,*_=_glass_panel_tl(6,.010,LAB2_S10_FREQS)
    door_a=_lab2_s10_door_curve(32)
    examples.append({
        "title":"Ejemplo 1 · Solución que no cumple",
        "purpose":"Permite explicar por qué un muro razonable no compensa una ventana simple y una puerta de prestación limitada.",
        "wall":"Ladrillo cerámico de 120 mm",
        "window":"Vidrio simple de 6 mm",
        "door":"P3 · Madera maciza de 45 mm, con sellos",
        "curves":[wall_a,np.asarray(window_a,dtype=float),door_a],
    })

    wall_b=_lab2_s10_double(
        "Yeso-cartón alta densidad",15,2,
        "Yeso-cartón alta densidad",15,2,
        100,"Lana mineral 40 kg/m³",
    )
    window_b,*_=_double_window_model(6,10,.020,1.2,2.0,.10,.010,.010,LAB2_S10_FREQS)
    door_b=_lab2_s10_door_curve(48)
    examples.append({
        "title":"Ejemplo 2 · Solución que cumple",
        "purpose":"Ejemplo de pauta con tabique desacoplado, vidrios asimétricos y una puerta reforzada.",
        "wall":"2× yeso-cartón alta densidad 15 mm / cámara 100 mm con lana mineral 40 kg/m³ / 2× yeso-cartón alta densidad 15 mm",
        "window":"Ventana doble 6/20/10 mm",
        "door":"P6 · Puerta acústica reforzada",
        "curves":[wall_b,np.asarray(window_b,dtype=float),door_b],
    })

    st.markdown("### Ejemplos resueltos del cálculo integrador")
    st.caption(
        "Estas son pautas de referencia, no las únicas soluciones posibles. Todos los valores "
        "se obtienen con las mismas funciones de cálculo utilizadas por el alumno."
    )
    for example_index,example in enumerate(examples):
        wall_curve,window_curve,door_curve=example["curves"]
        combined=-10*np.log10((
            19.71*10**(-wall_curve/10)
            +2.40*10**(-window_curve/10)
            +1.89*10**(-door_curve/10)
        )/24.0)
        wr,wc,wctr=_lab2_s10_indices(wall_curve)
        vr,vc,vctr=_lab2_s10_indices(window_curve)
        dr,dc,dctr=_lab2_s10_indices(door_curve)
        rw,c,ctr=_lab2_s10_indices(combined)
        weakest=min([(wr,"muro/tabique"),(vr,"ventana"),(dr,"puerta")])[1]
        with st.expander(example["title"],expanded=example_index==0):
            st.write(example["purpose"])
            st.markdown(
                f"**Muro/tabique:** {example['wall']}  \n"
                f"**Ventana:** {example['window']}  \n"
                f"**Puerta:** {example['door']}"
            )
            summary=pd.DataFrame([
                ["Muro/tabique",19.71,example["wall"],f"{wr} ({wc:+d}; {wctr:+d})"],
                ["Ventana",2.40,example["window"],f"{vr} ({vc:+d}; {vctr:+d})"],
                ["Puerta",1.89,example["door"],f"{dr} ({dc:+d}; {dctr:+d})"],
            ],columns=["Elemento","Superficie (m²)","Solución","Rw (C; Ctr) dB"])
            st.dataframe(summary,hide_index=True,use_container_width=True)
            a,b,c1,c2=st.columns(4)
            a.metric("Rw combinado",f"{rw} dB")
            b.metric("C",f"{c:+d} dB")
            c1.metric("Ctr",f"{ctr:+d} dB")
            c2.metric("Rw + C",f"{rw+c} dB")
            (st.success if rw>=40 else st.error)(
                f"{'Cumple' if rw>=40 else 'No cumple'}: Rw = {rw} dB "
                f"{'≥' if rw>=40 else '<'} 40 dB. Elemento de menor Rw: {weakest}."
            )
            _lab2_s10_plot(
                f"{example['title']} · curvas por tercios de octava",
                [("Muro/tabique",wall_curve),("Ventana",window_curve),
                 ("Puerta",door_curve),("Paramento combinado",combined)],
            )
            st.markdown("**Desarrollo espectral correcto**")
            st.dataframe(pd.DataFrame({
                "Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),
                "Muro/tabique Rm (dB)":np.round(wall_curve,1),
                "Ventana Rv (dB)":np.round(window_curve,1),
                "Puerta Rp (dB)":np.round(door_curve,1),
                "R combinado (dB)":np.round(combined,1),
            }),hide_index=True,use_container_width=True)
            st.info(
                f"Resultado de pauta: Rw(C; Ctr) = {rw} ({c:+d}; {ctr:+d}) dB; "
                f"Rw+C = {rw+c} dB y Rw+Ctr = {rw+ctr} dB."
            )

_VIEWS = {
    'teacher_group_review': _teacher_group_review_impl,
    'teacher_student_management': _teacher_student_management_impl,
    'teacher_publication_management': _teacher_publication_management_impl,
    'teacher_stage9_results': _teacher_stage9_results_impl,
    'teacher_stage9_answer_key': _teacher_stage9_answer_key_impl,
    '_teacher_lab1_final_results': _teacher_lab1_final_results_impl,
    'teacher_course_results': _teacher_course_results_impl,
    '_teacher_lab2_integrated_results': _teacher_lab2_integrated_results_impl,
    'teacher_lab2_stage10_answer_key': _teacher_lab2_stage10_answer_key_impl,
    '_lab2_s10_teacher_solved_examples': _lab2_s10_teacher_solved_examples_impl,
}

def run_view(name, runtime, *args, **kwargs):
    """Ejecuta una vista con el contexto compartido de la aplicación."""
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
