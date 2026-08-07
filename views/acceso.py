"""Vista de acceso y autenticación inicial.

La lógica se conserva sin cambios. ``app.py`` inyecta las dependencias
compartidas antes de ejecutar la vista para evitar acoplamientos circulares.
"""

_RUNTIME_PROTECTED = {"run_view", "_bind_runtime", "_VIEWS", "_RUNTIME_PROTECTED"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and name not in _VIEWS:
            module_globals[name] = value

def _login_impl():
    institutional_header()
    header(
        "DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN",
        "Plataforma de Laboratorios Interactivos",
        "Aprendizaje, experimentación, evaluación y seguimiento académico en acústica de la edificación.",
    )

    course_col, lab_col, eval_col = st.columns(3)
    with course_col:
        st.markdown(
            """
            <div style="padding:1rem 1.05rem;border:1px solid #d7e5f2;border-radius:14px;background:#ffffff;min-height:118px;">
                <div style="font-size:1.35rem;">📘</div>
                <div style="font-weight:800;color:#0b3f6c;margin-top:.2rem;">Cursos del diplomado</div>
                <div style="font-size:.88rem;color:#5d6f7f;margin-top:.35rem;">Acceso progresivo a contenidos y actividades por curso.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with lab_col:
        st.markdown(
            """
            <div style="padding:1rem 1.05rem;border:1px solid #d7e5f2;border-radius:14px;background:#ffffff;min-height:118px;">
                <div style="font-size:1.35rem;">🧪</div>
                <div style="font-weight:800;color:#0b3f6c;margin-top:.2rem;">Laboratorios interactivos</div>
                <div style="font-size:.88rem;color:#5d6f7f;margin-top:.35rem;">Exploración técnica, ejercicios, simulaciones y casos aplicados.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with eval_col:
        st.markdown(
            """
            <div style="padding:1rem 1.05rem;border:1px solid #d7e5f2;border-radius:14px;background:#ffffff;min-height:118px;">
                <div style="font-size:1.35rem;">🎓</div>
                <div style="font-weight:800;color:#0b3f6c;margin-top:.2rem;">Evaluación y desempeño</div>
                <div style="font-size:.88rem;color:#5d6f7f;margin-top:.35rem;">Seguimiento formativo, calificaciones oficiales y retroalimentación.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.55rem'></div>", unsafe_allow_html=True)
    role=st.radio("Perfil",["Alumno","Docente"],horizontal=True)
    name=st.text_input("Nombre completo")
    if role=="Alumno":
        rut=st.text_input("RUT o cédula de identificación")
        valid=bool(name.strip() and rut.strip())
        identification=_normalize_identification(rut)
    else:
        password=st.text_input("Clave docente",type="password")
        try:
            teacher_password=str(st.secrets["teacher"]["password"])
        except (KeyError, FileNotFoundError):
            teacher_password="docente123"
        valid=name.strip() and password==teacher_password
        identification="docente"
    if st.button("Ingresar",type="primary",use_container_width=True):
        if role=="Alumno" and valid:
            authorized,detail=_authorized_student(name,rut)
            if not authorized:
                st.error(detail)
                return
            roster_name=detail.get("display_name") or name.strip()
            roster_email=detail.get("email") or ""
            user_key=_make_user_key(role,name,identification)
            st.session_state.update(access=True,role=role,name=roster_name,user_key=user_key)
            _register_user(user_key,role,roster_name,rut,roster_email)
            load_user_progress(user_key)
            st.rerun()
        elif role=="Docente" and valid:
            user_key=_make_user_key(role,name,identification)
            st.session_state.update(access=True,role=role,name=name,user_key=user_key)
            _register_user(user_key,role,name)
            load_user_progress(user_key)
            st.rerun()
        else:
            st.error("Completa correctamente los datos de acceso.")

_VIEWS = {"login": _login_impl}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
