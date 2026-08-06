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
    header("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN","Curso · Aislamiento a Ruido Aéreo","Laboratorios interactivos 1 y 2")
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
