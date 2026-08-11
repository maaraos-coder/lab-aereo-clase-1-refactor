"""Vista de proyección para la ventana compartida en Zoom."""

_RUNTIME_PROTECTED = {"run_view", "_bind_runtime", "_RUNTIME_PROTECTED", "_set_projection_impl", "projection_view_impl"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED:
            module_globals[name] = value

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return globals()[f"{name}_impl"](*args, **kwargs)

def _set_projection_impl(stage=None,question="",answer="",solution="",show_answer=False,show_solution=False,class_id=None):
    target_class_id = class_id or CLASS_ID
    client=_supabase()
    if client is not None:
        client.table("projection_state").upsert({
            "course_id":COURSE_ID,"class_id":target_class_id,"stage":stage,
            "question":question,"answer":answer,"solution":solution,
            "show_answer":bool(show_answer),"show_solution":bool(show_solution),
            "updated_at":_now(),
        },on_conflict="course_id,class_id").execute()
    else:
        with _activity_db() as con:
            con.execute(
            """UPDATE projection_state SET stage=?,question=?,answer=?,solution=?,
            show_answer=?,show_solution=?,updated_at=? WHERE id=1""",
            (stage,question,answer,solution,int(show_answer),int(show_solution),
             dt.datetime.now().isoformat(timespec="seconds")),
            )

def projection_view_impl():
    """Complete student-facing class screen intended for a separate Zoom window."""
    future_lab_id = st.query_params.get("future_lab")
    target_class_id = future_lab_id if future_lab_id in globals().get("FUTURE_LABS", {}) else CLASS_ID

    client=_supabase()
    if client is not None:
        rows=_remote_rows("projection_state",course_id=COURSE_ID,class_id=target_class_id)
        item=rows[0] if rows else {}
        row=(item.get("stage"),item.get("question"),item.get("answer"),item.get("solution"),
             item.get("show_answer"),item.get("show_solution"),item.get("updated_at"))
    else:
        with _activity_db() as con:
            row=con.execute(
                "SELECT stage,question,answer,solution,show_answer,show_solution,updated_at "
                "FROM projection_state WHERE id=1"
            ).fetchone()

    stage=row[0] if row else None
    if stage is None:
        title = (
            FUTURE_LABS[future_lab_id]["course"]
            if future_lab_id in globals().get("FUTURE_LABS", {})
            else "Laboratorio de aislamiento a ruido aéreo"
        )
        st.markdown(
            f'<div class="hero"><div class="tag">VISTA DE PROYECCIÓN · ALUMNOS</div>'
            f'<h1>{title}</h1>'
            '<p>Pantalla preparada. Seleccione una etapa desde el panel docente.</p></div>',
            unsafe_allow_html=True,
        )
        st.info("El docente todavía no ha seleccionado el contenido de la clase.")
    else:
        st.session_state["projection_mode"]=True
        st.session_state["role"]="Proyección"
        st.session_state["name"]="Pantalla de clase"
        if future_lab_id in globals().get("FUTURE_LABS", {}):
            lab=FUTURE_LABS[future_lab_id]
            _course_views.run_view("future_projection_stage", globals(), lab, int(stage))
        else:
            stage_functions=LAB_STAGE_FUNCTIONS[ACTIVE_LAB]
            stage_functions[int(stage)]()
        if row[4] and row[2]:
            st.markdown("#### Respuesta anónima seleccionada por el docente")
            st.info(row[2])
        if row[5] and row[3]:
            st.markdown("#### Solución revelada por el docente")
            st.success(row[3])
    st.caption("Vista para alumnos: sin profundización docente, nombres, puntajes ni controles privados.")
    if st.button("Actualizar pantalla",width="stretch"):
        st.rerun()
