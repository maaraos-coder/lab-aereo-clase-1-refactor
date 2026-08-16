import streamlit.components.v1 as components
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
ASSET_DIR = PROJECT_ROOT / "assets"

"""Vistas de cursos, selección de laboratorios y laboratorios futuros.

La lógica se conserva sin cambios. ``app.py`` inyecta las dependencias
compartidas antes de ejecutar cada vista para evitar acoplamientos circulares.
"""

_RUNTIME_PROTECTED = {"run_view", "_bind_runtime", "_VIEWS", "_RUNTIME_PROTECTED"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and name not in _VIEWS:
            module_globals[name] = value

def course_dashboard_impl():
    header("MIS CLASES","Diplomado en Acústica en la Edificación",
           "Selecciona un curso y abre el laboratorio habilitado en la fecha programada.")
    client=_supabase()
    if client is None:
        st.warning("Supabase todavía no está configurado. La aplicación está usando almacenamiento local de prueba.")
        classes=[
            {"id":"clase-01-aislamiento-ruido-aereo","class_number":1,
             "title":"Laboratorio 1",
             "description":"","status":"published","due_at":None},
            {"id":"clase-02-aislamiento-ruido-aereo-minvu","class_number":2,
             "title":"Laboratorio 2",
             "description":"","status":"draft","due_at":None},
        ]
    else:
        classes=_course_classes(client)
    class_by_number={item.get("class_number"):item for item in classes}
    summaries,course_result=_result_summary()
    first_course=ACADEMIC_COURSES[0]
    st.markdown(f"### {first_course['title']}")
    for lab in first_course["labs"]:
        number=lab["number"]
        item=class_by_number.get(number,{})
        opening=_effective_opening(number,item.get("opens_at"),lab["opens_at"])
        released=item.get("status") in ("published","archived")
        if st.session_state.get("role")=="Alumno" and not released:
            continue
        available=released and _is_open(opening)
        if st.session_state.get("role")=="Docente":
            available=True
        summary=summaries[number]
        progress_status=("Pendiente" if summary["answered"]==0 else
                         "Completado" if summary["answered"]>=summary["expected"] else "En progreso")
        if st.session_state.get("role")=="Docente":
            availability=("Publicado para alumnos" if released else
                          "Borrador · oculto para alumnos")
        else:
            availability="Disponible" if available else f"Habilitación: {_opening_label(opening)}"
        st.markdown(
            f'<div class="lesson"><div class="overview-title">LABORATORIO {number}</div>'
            f'<span class="muted">{availability}</span><hr>'
            f'<b>{summary["earned"]:g}/{summary["maximum"]:g} puntos</b><br>'
            f'<span class="muted">Estado: {progress_status} · '
            f'{summary["answered"]} de {summary["expected"]} actividades realizadas</span></div>',
            unsafe_allow_html=True)
        if available and st.button(
            "Continuar laboratorio" if number==ACTIVE_LAB else "Abrir laboratorio",
            key=f"open_lab_{number}",type="primary" if number==ACTIVE_LAB else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_lab=number
            st.session_state["_open_lab_requested"]=True
            st.rerun()

    lab2_released=class_by_number.get(2,{}).get("status") in ("published","archived")
    if st.session_state.get("role")=="Alumno":
        st.markdown("#### Resultado del curso")
        if not lab2_released:
            st.info("El curso continúa en desarrollo. Tu avance del laboratorio publicado se conserva.")
        elif not course_result["final_done"]:
            st.warning(
                f'**Evaluación final: Pendiente.** Puntaje acumulado actual: '
                f'{course_result["earned"]:g}/{course_result["maximum"]:g} puntos. '
                'La nota final se calculará cuando envíes la evaluación final del Laboratorio 2.'
            )
        else:
            state="Aprobado" if course_result["grade"]>=4.0 else "Reprobado"
            st.success(
                f'**{state}.** Puntaje final: {course_result["earned"]:g}/'
                f'{course_result["maximum"]:g} puntos ({course_result["percent"]:.1f}%). '
                f'Nota final: **{course_result["grade"]:.1f}**.'
            )

    st.markdown("---")
    for course in COURSE_LABS:
        visible_labs=[]
        for lab in course["labs"]:
            row=next((r for r in classes if r.get("id")==lab["id"]),{})
            published=row.get("status") in ("published","archived")
            if st.session_state.get("role")=="Docente" or (published and _is_open(row.get("opens_at") or lab["opens_at"])):
                visible_labs.append((lab,row,published))
        if not visible_labs:
            continue
        st.markdown(f"### {course['course']}")
        columns=st.columns(2)
        for column,(lab,row,published) in zip(columns,visible_labs):
            with column:
                state=("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                st.markdown(
                    f'<div class="lesson"><div class="overview-title">LABORATORIO {lab["number"]}</div>'
                    f'<span class="muted">Programado: {_opening_label(row.get("opens_at") or lab["opens_at"])}</span><hr>'
                    f'<b>{state}</b><br><span class="muted">{lab["focus"]}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abrir laboratorio",key=f'open_{lab["id"]}',use_container_width=True):
                    st.session_state["future_lab_id"]=lab["id"]
                    st.rerun()

def _future_saved_impl(class_id):
    """Return the saved state for the selected student and future class."""
    cache_key=f"future_saved_{class_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    client=_supabase()
    if client is None:
        return {}
    try:
        rows=(client.table("user_progress").select("state_json")
              .eq("class_id",class_id).eq("user_key",st.session_state.user_key)
              .limit(1).execute().data or [])
        state=rows[0].get("state_json",{}) if rows else {}
        state=json.loads(state) if isinstance(state,str) else state
        st.session_state[cache_key]=state
        return state
    except Exception:
        return {}

def _save_future_state_impl(class_id,state):
    """Guarda progreso solo para usuarios reales.

    La vista de Proyección es interactiva durante la clase, pero su estado es
    temporal: nunca debe escribir respuestas, avance ni puntaje en la base de datos.
    """
    st.session_state[f"future_saved_{class_id}"] = state

    # Pantalla de Zoom / proyección: estado solo de sesión.
    if (
        st.session_state.get("projection_mode")
        or st.session_state.get("role") == "Proyección"
    ):
        return

    # Seguridad adicional: si no existe un usuario autenticado no se persiste.
    user_key = st.session_state.get("user_key")
    if not user_key:
        return

    client = _supabase()
    if client is None:
        return

    client.table("user_progress").upsert({
        "course_id": COURSE_ID,
        "class_id": class_id,
        "user_key": user_key,
        "role": st.session_state.get("role", "Alumno"),
        "display_name": st.session_state.get("name", ""),
        "state_json": state,
        "updated_at": _now(),
    }, on_conflict="class_id,user_key").execute()

def _course2_lab1_stage0_asset(filename, caption):
    """Muestra el asset oficial si existe; de lo contrario deja su espacio identificado."""
    path = ROOT / "assets" / filename
    if path.exists():
        st.image(str(path), width="stretch")
        if caption:
            st.caption(caption)
    else:
        st.info(
            f"Asset pendiente: `{filename}`. "
            "Sube el render definitivo a la carpeta `assets/` conservando exactamente este nombre."
        )


def _course2_lab1_stage0_dynamic_image(filename, source=None, caption=None):
    """Renderiza UNA sola imagen y superpone el camino energético seleccionado.

    No genera imágenes adicionales ni cambia el asset original. El resaltado se crea
    en memoria sobre el mismo render para mantener la interfaz limpia en escritorio y móvil.
    """
    path = ROOT / "assets" / filename
    if not path.exists():
        st.info(
            f"Asset pendiente: `{filename}`. "
            "Sube el render definitivo a la carpeta `assets/` conservando exactamente este nombre."
        )
        return

    if source not in {"Pisada", "Bomba", "Descarga sanitaria"}:
        st.image(str(path), width="stretch")
        if caption:
            st.caption(caption)
        return

    try:
        from PIL import Image, ImageDraw, ImageEnhance

        base = Image.open(path).convert("RGBA")
        w, h = base.size
        # Oscurecimiento muy leve: mantiene legible el edificio, pero hace que el
        # recorrido seleccionado tenga jerarquía visual sin cargar una segunda imagen.
        rgb = base.convert("RGB")
        rgb = ImageEnhance.Brightness(rgb).enhance(0.78)
        img = rgb.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        def P(x, y):
            return (int(x * w), int(y * h))

        def glow_line(points, color, width=9):
            pts=[P(x,y) for x,y in points]
            for extra, alpha in ((14, 35), (8, 70), (0, 230)):
                draw.line(pts, fill=(*color, alpha), width=max(2,width+extra), joint="curve")
            for x,y in pts:
                r=max(5,width//2)
                draw.ellipse((x-r,y-r,x+r,y+r), fill=(*color,220))

        def support_mark(x, y, color):
            cx,cy=P(x,y)
            for rr,alpha in ((22,45),(14,90),(7,220)):
                draw.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), outline=(*color,alpha), width=max(2,rr//5))

        def radiation_down(cx, cy, scale=1.0):
            """Dibuja radiación acústica desde una superficie hacia el recinto inferior.

            El punto (cx, cy) representa la superficie estructural radiante. Los arcos
            cian nacen allí y se abren hacia ABAJO, de modo que la lectura visual sea
            superficie vibrante -> aire del recinto -> receptor, y nunca al revés.
            """
            c=(44, 210, 255)
            px,py=P(cx,cy)
            stroke=max(3,int(w*0.0025))
            for i in range(4):
                rx=int(w*(0.030+0.017*i)*scale)
                ry=int(h*(0.045+0.022*i)*scale)
                # PIL mide los ángulos desde las 3 en punto en sentido horario.
                # 0..180 corresponde a la mitad INFERIOR de la elipse.
                box=(px-rx, py-ry, px+rx, py+ry)
                draw.arc(box, start=0, end=180, fill=(*c,220-30*i), width=stroke)

            # Pequeña indicación de sentido descendente sin texto ni flechas invasivas.
            # Se mantiene dentro de la misma imagen y ayuda a leer la dirección física.
            y0=py+int(h*0.018*scale)
            y1=py+int(h*0.070*scale)
            draw.line((px,y0,px,y1), fill=(*c,205), width=max(3,int(w*0.002)))
            ah=max(6,int(w*0.006))
            draw.polygon([(px,y1+ah),(px-ah,y1-ah//2),(px+ah,y1-ah//2)], fill=(*c,215))

        if source == "Pisada":
            orange=(255, 151, 25)
            # Pie -> losa -> cielo del dormitorio receptor.
            glow_line([(0.35,0.285),(0.35,0.315),(0.35,0.37),(0.35,0.43)], orange, width=max(7,int(w*0.005)))
            # Propagación lateral por la losa inmediatamente bajo la pisada.
            glow_line([(0.22,0.305),(0.35,0.305),(0.49,0.305)], orange, width=max(5,int(w*0.0035)))
            support_mark(0.35,0.305,orange)
            # Radiación desde el cielo vibrante hacia la pareja ubicada justo debajo.
            radiation_down(0.35,0.335,1.45)

        elif source == "Bomba":
            blue=(38, 146, 255)
            # Camino 1: bomba -> base -> losa del subterráneo.
            glow_line([(0.23,0.88),(0.23,0.91)], blue, width=max(7,int(w*0.005)))
            support_mark(0.23,0.91,blue)
            # Camino 2: bomba -> impulsión -> montante -> ramales hacia cocinas.
            glow_line([(0.24,0.87),(0.45,0.87),(0.68,0.87),(0.69,0.68),(0.69,0.47),(0.69,0.24)], blue, width=max(7,int(w*0.0045)))
            for y in (0.68,0.47,0.24):
                glow_line([(0.69,y),(0.61,y)], blue, width=max(5,int(w*0.003)))
                support_mark(0.69,y,blue)
            # Ejemplo de una superficie estructural excitada por soportes de la montante
            # que posteriormente puede radiar hacia el recinto contiguo.
            radiation_down(0.62,0.455,1.10)

        elif source == "Descarga sanitaria":
            purple=(177, 77, 255)
            # WC -> ramal -> bajante común -> fijaciones -> estructura.
            glow_line([(0.78,0.24),(0.83,0.24),(0.83,0.47),(0.83,0.70),(0.83,0.88)], purple, width=max(7,int(w*0.0045)))
            glow_line([(0.78,0.47),(0.83,0.47)], purple, width=max(5,int(w*0.003)))
            glow_line([(0.78,0.70),(0.83,0.70)], purple, width=max(5,int(w*0.003)))
            for y in (0.30,0.50,0.70):
                support_mark(0.83,y,purple)
            # Radiación desde una superficie próxima a una fijación hacia recinto habitable.
            radiation_down(0.75,0.485,1.05)

        img = Image.alpha_composite(img, overlay)
        st.image(img, width="stretch")
        if caption:
            st.caption(caption)
    except Exception:
        # Si Pillow fallara por cualquier motivo, nunca bloqueamos la etapa.
        st.image(str(path), width="stretch")
        if caption:
            st.caption(caption)


def _course2_stage0_footstep_svg(stage=0):
    """Lámina SVG profesional del recorrido vibroacústico de una pisada."""
    stage=max(0,min(int(stage),4))
    orange="#ff8a2a"; cyan="#37d6ff"
    active=[stage>=i for i in range(5)]
    def op(i):
        return "1" if active[i] else ".16"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 650" width="100%" role="img" aria-label="Ruta vibroacústica de una pisada desde el impacto hasta el receptor">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#061426"/><stop offset="1" stop-color="#0a2742"/></linearGradient>
      <linearGradient id="concretePro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8c9296"/><stop offset=".18" stop-color="#666e73"/><stop offset="1" stop-color="#353d43"/></linearGradient>
      <linearGradient id="roomPro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#30363b"/><stop offset="1" stop-color="#171d22"/></linearGradient>
      <linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7b5b3e"/><stop offset=".5" stop-color="#a57b54"/><stop offset="1" stop-color="#684a32"/></linearGradient>
      <pattern id="aggregate" width="48" height="36" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="2.2" fill="#c1c5c8" opacity=".28"/><circle cx="32" cy="18" r="3" fill="#20272d" opacity=".55"/><path d="M4 31 l12 -6 l10 5 l11 -4" fill="none" stroke="#b5bcc1" stroke-width="1" opacity=".22"/></pattern>
      <pattern id="woodgrain" width="70" height="16" patternUnits="userSpaceOnUse"><path d="M0 4 C18 0 32 9 50 4 S68 8 70 4" fill="none" stroke="#d2aa83" stroke-width="1" opacity=".25"/></pattern>
      <filter id="glowO"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <filter id="glowC"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <style>.t{{font-family:Inter,Arial,sans-serif;fill:#eef7ff}} .muted{{fill:#9fb0be}} .label{{font-size:17px;font-weight:700}} .tiny{{font-size:14px}} .title{{font-size:24px;font-weight:800}}</style>
    </defs>
    <rect width="1440" height="650" rx="22" fill="url(#bg)"/>
    <g opacity="{op(0)}">
      <path d="M292 42 c24 35 32 83 22 120 l-18 58 -70 0 c-17 0 -27 -19 -14 -32 25 -25 43 -51 52 -82 l7 -64z" fill="#20252a" stroke="#c8d0d5" stroke-width="3"/>
      <path d="M216 212 c40 12 91 12 132 0 l24 20 -12 21 -128 0 c-38 0 -55 -32 -16 -41z" fill="#c9ced2" stroke="#eff3f5" stroke-width="3"/>
      <path d="M228 244 h132" stroke="#79848c" stroke-width="4"/>
      <circle cx="292" cy="264" r="12" fill="{orange}" filter="url(#glowO)"/>
      <path d="M292 266 V320" stroke="{orange}" stroke-width="7" filter="url(#glowO)"/>
      <path d="M281 307 l11 14 11 -14" fill="none" stroke="{orange}" stroke-width="5"/>
    </g>
    <rect x="100" y="252" width="1070" height="28" rx="3" fill="url(#wood)" stroke="#c6a27f" stroke-width="2"/>
    <rect x="100" y="252" width="1070" height="28" fill="url(#woodgrain)"/>
    <rect x="100" y="280" width="1070" height="175" rx="4" fill="url(#concretePro)" stroke="#b9c2c8" stroke-width="3"/>
    <rect x="100" y="280" width="1070" height="175" fill="url(#aggregate)" opacity=".85"/>
    <g stroke="#151c22" stroke-width="8" opacity=".95"><line x1="125" y1="312" x2="1145" y2="312"/><line x1="125" y1="425" x2="1145" y2="425"/></g>
    <g stroke="#6c7780" stroke-width="2" opacity=".75">
      <line x1="155" y1="292" x2="155" y2="443"/><line x1="245" y1="292" x2="245" y2="443"/><line x1="335" y1="292" x2="335" y2="443"/><line x1="425" y1="292" x2="425" y2="443"/><line x1="515" y1="292" x2="515" y2="443"/><line x1="605" y1="292" x2="605" y2="443"/><line x1="695" y1="292" x2="695" y2="443"/><line x1="785" y1="292" x2="785" y2="443"/><line x1="875" y1="292" x2="875" y2="443"/><line x1="965" y1="292" x2="965" y2="443"/><line x1="1055" y1="292" x2="1055" y2="443"/>
    </g>
    <g opacity="{op(1)}" filter="url(#glowO)" fill="none" stroke="{orange}">
      <path d="M245 302 Q292 276 339 302" stroke-width="5"/><path d="M225 321 Q292 282 359 321" stroke-width="4" opacity=".7"/>
    </g>
    <g opacity="{op(2)}" filter="url(#glowO)" fill="none" stroke="{orange}" stroke-width="4">
      <path d="M165 345 C240 319 280 371 355 345 S470 319 545 345 S660 371 735 345 S850 319 925 345 S1040 371 1115 345"/>
      <path d="M165 390 C240 364 280 416 355 390 S470 364 545 390 S660 416 735 390 S850 364 925 390 S1040 416 1115 390" opacity=".68"/>
      <path d="M470 366 H655" stroke-width="3"/><path d="M646 358 l13 8 -13 8" fill="none"/>
      <path d="M760 366 H945" stroke-width="3"/><path d="M936 358 l13 8 -13 8" fill="none"/>
    </g>
    <rect x="100" y="455" width="1070" height="20" fill="#1f262c" stroke="#7a858d" stroke-width="2"/>
    <g stroke="#858f96" stroke-width="2"><line x1="245" y1="455" x2="245" y2="481"/><line x1="445" y1="455" x2="445" y2="481"/><line x1="645" y1="455" x2="645" y2="481"/><line x1="845" y1="455" x2="845" y2="481"/><line x1="1045" y1="455" x2="1045" y2="481"/></g>
    <rect x="100" y="475" width="1070" height="155" fill="url(#roomPro)" stroke="#42515c" stroke-width="2"/>
    <rect x="210" y="548" width="380" height="44" rx="8" fill="#56636d"/><rect x="245" y="520" width="310" height="46" rx="10" fill="#737f88"/>
    <rect x="225" y="590" width="350" height="18" fill="#20282e"/><circle cx="350" cy="536" r="14" fill="#d3b09a"/><circle cx="430" cy="536" r="14" fill="#d3b09a"/>
    <rect x="795" y="520" width="180" height="90" rx="5" fill="#222c34" stroke="#5d6d79" stroke-width="4"/><rect x="845" y="548" width="60" height="38" rx="5" fill="#536372"/><circle cx="875" cy="566" r="12" fill="#d0af96"/>
    <path d="M100 475 H1170" stroke="{orange}" stroke-width="3" opacity="{op(2)}" filter="url(#glowO)"/>
    <g opacity="{op(3)}" fill="none" stroke="{cyan}" stroke-width="5" filter="url(#glowC)">
      <path d="M260 478 Q535 635 810 478"/><path d="M205 478 Q535 680 865 478"/><path d="M150 478 Q535 725 920 478"/>
    </g>
    <g opacity="{op(4)}"><circle cx="390" cy="548" r="70" fill="none" stroke="{cyan}" stroke-width="3" stroke-dasharray="9 8"/><text x="390" y="626" text-anchor="middle" class="t label" fill="{cyan}">RECEPTOR</text></g>
    <g class="t tiny" opacity=".95">
      <text x="1010" y="235">Acabado de piso</text><path d="M1000 230 H955 V252" fill="none" stroke="#c8d2d9" stroke-width="2" stroke-dasharray="6 5"/>
      <text x="1010" y="300">Losa de hormigón armado</text><path d="M1000 295 H950 V315" fill="none" stroke="#c8d2d9" stroke-width="2" stroke-dasharray="6 5"/>
      <text x="1010" y="454" fill="{cyan}">Superficie radiante</text><path d="M1000 448 H940" fill="none" stroke="{cyan}" stroke-width="2" stroke-dasharray="6 5" opacity="{op(3)}"/>
    </g>
    <rect x="1198" y="78" width="205" height="250" rx="16" fill="#0b2743" stroke="#27506d" stroke-width="2"/>
    <text x="1220" y="112" class="t label">Ruta de la energía</text>
    <g class="t tiny">
      <circle cx="1224" cy="150" r="13" fill="{orange}" opacity="{op(0)}"/><text x="1224" y="155" text-anchor="middle" font-weight="800">1</text><text x="1250" y="155">Impacto</text>
      <circle cx="1224" cy="190" r="13" fill="{orange}" opacity="{op(1)}"/><text x="1224" y="195" text-anchor="middle" font-weight="800">2</text><text x="1250" y="195">Respuesta de la losa</text>
      <circle cx="1224" cy="230" r="13" fill="{orange}" opacity="{op(2)}"/><text x="1224" y="235" text-anchor="middle" font-weight="800">3</text><text x="1250" y="235">Propagación</text>
      <circle cx="1224" cy="270" r="13" fill="{cyan}" opacity="{op(3)}"/><text x="1224" y="275" text-anchor="middle" font-weight="800">4</text><text x="1250" y="275">Radiación</text>
      <circle cx="1224" cy="310" r="13" fill="{cyan}" opacity="{op(4)}"/><text x="1224" y="315" text-anchor="middle" font-weight="800">5</text><text x="1250" y="315">Receptor</text>
    </g>
    </svg>'''

def _course2_stage0_pump_paths_svg(active="base"):
    """Mapa SVG profesional de tres caminos simultáneos de una bomba centrífuga."""
    active=active if active in {"base","pipe","air"} else "base"
    orange="#ff9a32"; cyan="#36d8ff"
    def o(name): return "1" if name==active else ".22"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 560" width="100%" role="img" aria-label="Mapa de caminos de transmisión de una bomba centrífuga">
      <defs>
        <linearGradient id="bgPump" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#041426"/><stop offset="1" stop-color="#0a2b48"/></linearGradient>
        <linearGradient id="motor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a6f9d"/><stop offset="1" stop-color="#0e3450"/></linearGradient>
        <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#aab5bd"/><stop offset=".5" stop-color="#53616c"/><stop offset="1" stop-color="#222d35"/></linearGradient>
        <filter id="orangeGlow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <filter id="cyanGlow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <style>.t{{font-family:Inter,Arial,sans-serif;fill:#eef8ff}} .title{{font-size:24px;font-weight:800}} .label{{font-size:17px;font-weight:700}} .small{{font-size:15px;fill:#9db1c2}}</style>
      </defs>
      <rect width="1280" height="560" rx="22" fill="url(#bgPump)"/>
      <text x="36" y="44" class="t title">Una bomba centrífuga · tres caminos simultáneos</text>
      <text x="36" y="70" class="t small">La fuente es una sola; los mecanismos de transmisión no lo son.</text>
      <rect x="42" y="416" width="860" height="82" rx="5" fill="#4b5660" stroke="#7f8d98" stroke-width="3"/><path d="M45 448 H898" stroke="#2d353d" stroke-width="5" opacity=".6"/>
      <rect x="905" y="100" width="32" height="398" fill="#626e77" stroke="#92a0aa" stroke-width="2"/>
      <rect x="938" y="170" width="292" height="328" fill="#111e29" stroke="#4d6170" stroke-width="3"/>
      <rect x="986" y="360" width="190" height="58" rx="10" fill="#364756"/><rect x="1010" y="334" width="142" height="44" rx="9" fill="#536577"/><circle cx="1055" cy="352" r="14" fill="#d0b09c"/><circle cx="1110" cy="352" r="14" fill="#d0b09c"/>
      <text x="1084" y="456" text-anchor="middle" class="t label">RECINTO RECEPTOR</text>
      <g>
        <rect x="160" y="300" width="355" height="47" rx="7" fill="#434f5a" stroke="#8c9aa5" stroke-width="3"/>
        <rect x="180" y="215" width="205" height="88" rx="18" fill="url(#motor)" stroke="#64b8e8" stroke-width="3"/>
        <g stroke="#7bc7ef" stroke-width="2" opacity=".55"><line x1="205" y1="226" x2="205" y2="292"/><line x1="225" y1="226" x2="225" y2="292"/><line x1="245" y1="226" x2="245" y2="292"/><line x1="265" y1="226" x2="265" y2="292"/><line x1="285" y1="226" x2="285" y2="292"/><line x1="305" y1="226" x2="305" y2="292"/></g>
        <rect x="386" y="247" width="62" height="25" rx="8" fill="#65727c"/>
        <path d="M447 195 C530 184 555 268 502 305 C470 328 428 309 423 272 C418 238 426 205 447 195z" fill="url(#metal)" stroke="#c4ccd2" stroke-width="3"/>
        <circle cx="469" cy="254" r="32" fill="#18232b" stroke="#a7b1b9" stroke-width="4"/><circle cx="469" cy="254" r="9" fill="#d7dde1"/>
        <path d="M483 198 V145 H705" fill="none" stroke="url(#metal)" stroke-width="24" stroke-linejoin="round"/><path d="M705 145 H892 V250" fill="none" stroke="url(#metal)" stroke-width="24"/>
        <path d="M502 254 H735" fill="none" stroke="url(#metal)" stroke-width="26"/>
        <rect x="726" y="232" width="50" height="45" rx="7" fill="#1d384a" stroke="#4ed3ff" stroke-width="2"/>
      </g>
      <g opacity="{o('base')}" filter="url(#orangeGlow)" stroke="{orange}" fill="none"><path d="M230 347 V416" stroke-width="7"/><path d="M430 347 V416" stroke-width="7"/><path d="M200 458 H520" stroke-width="5"/></g>
      <text x="165" y="392" class="t label" fill="{orange}" opacity="{o('base')}">BASE → LOSA → ESTRUCTURA</text>
      <g opacity="{o('pipe')}" filter="url(#cyanGlow)" fill="none" stroke="{cyan}" stroke-width="5" stroke-dasharray="10 7"><path d="M522 254 H738"/><path d="M752 254 H883 V315 H914"/></g>
      <g opacity="{o('pipe')}" fill="none" stroke="{cyan}" stroke-width="4"><path d="M756 278 V416"/><path d="M861 278 V416"/></g>
      <text x="575" y="300" class="t label" fill="{cyan}" opacity="{o('pipe')}">TUBERÍA → SOPORTES → ESTRUCTURA</text>
      <g opacity="{o('air')}" filter="url(#orangeGlow)" fill="none" stroke="#ff5252" stroke-width="5"><path d="M530 205 Q590 252 530 298"/><path d="M560 184 Q645 252 560 320"/><path d="M935 244 Q1000 294 935 344"/><path d="M958 225 Q1045 294 958 363"/></g>
      <text x="783" y="193" class="t label" fill="#ff6868" opacity="{o('air')}">CARCASA → AIRE → RECEPTOR</text>
      <rect x="948" y="88" width="282" height="68" rx="12" fill="#0b2743" stroke="#244d6a"/><text x="970" y="116" class="t label">Camino seleccionado</text><text x="970" y="142" class="t small">Los otros permanecen posibles, pero atenuados.</text>
    </svg>'''


def _course2_lab1_stage0_pump_svg(encierro=False, absorbente=False, antivibratorios=False, flexible=False):
    """SVG técnico profesional de control vibroacústico de una bomba centrífuga."""
    orange="#ff9a32"; cyan="#35d7ff"; green="#48d895"; red="#ff5b5b"
    base_color=green if antivibratorios else orange
    pipe_color=green if flexible else cyan
    air_state="Parcial" if (encierro or absorbente) else "Activo"
    air_color=green if (encierro and absorbente) else ("#e8b44a" if (encierro or absorbente) else red)
    base_state="Reducido" if antivibratorios else "Activo"
    pipe_state="Reducido" if flexible else "Activo"
    enclosure=''
    if encierro:
        enclosure='''<rect x="96" y="108" width="470" height="308" rx="12" fill="#0b1d2e" fill-opacity=".73" stroke="#7dd9ff" stroke-width="5"/><rect x="112" y="124" width="438" height="276" rx="8" fill="none" stroke="#7dd9ff" stroke-opacity=".35" stroke-width="2"/>'''
    absorb=''
    if absorbente:
        absorb='''<g stroke="#8fdcff" stroke-width="5" fill="none" opacity=".65"><path d="M122 143 l18 -12 l18 12 l18 -12 l18 12 l18 -12 l18 12 l18 -12 l18 12"/><path d="M122 165 l18 -12 l18 12 l18 -12 l18 12 l18 -12 l18 12 l18 -12 l18 12"/></g>'''
    if antivibratorios:
        isolators='''<g stroke="#48d895" stroke-width="6" fill="none" stroke-linecap="round"><path d="M218 412 q12 -20 24 0 q12 20 24 0 q12 -20 24 0"/><path d="M418 412 q12 -20 24 0 q12 20 24 0 q12 -20 24 0"/></g>'''
    else:
        isolators='''<rect x="218" y="400" width="74" height="24" rx="4" fill="#808c95"/><rect x="412" y="400" width="74" height="24" rx="4" fill="#808c95"/>'''
    flex='''<line x1="655" y1="266" x2="740" y2="266" stroke="#62717c" stroke-width="24" stroke-linecap="round"/>'''
    if flexible:
        flex='''<g stroke="#48d895" stroke-width="8" fill="none"><path d="M655 266 q10 -18 20 0 q10 18 20 0 q10 -18 20 0 q10 18 20 0"/></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 650" width="100%" role="img" aria-label="Laboratorio conceptual de control vibroacústico de una bomba centrífuga">
      <defs>
        <linearGradient id="labBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#041425"/><stop offset="1" stop-color="#0a2945"/></linearGradient>
        <linearGradient id="labMotor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b77a7"/><stop offset="1" stop-color="#0d3553"/></linearGradient>
        <linearGradient id="labMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bac3ca"/><stop offset=".5" stop-color="#65727c"/><stop offset="1" stop-color="#29343c"/></linearGradient>
        <filter id="lg"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <style>.t{{font-family:Inter,Arial,sans-serif;fill:#eef8ff}} .title{{font-size:24px;font-weight:800}} .label{{font-size:17px;font-weight:700}} .small{{font-size:14px;fill:#a5b8c8}}</style>
      </defs>
      <rect width="1280" height="650" rx="22" fill="url(#labBg)"/>
      <text x="36" y="44" class="t title">Laboratorio conceptual · Controla la bomba</text>
      <text x="36" y="69" class="t small">Activa medidas y observa qué camino físico se modifica realmente.</text>
      {enclosure}{absorb}
      <rect x="150" y="356" width="430" height="42" rx="7" fill="#414e58" stroke="#8b9aa6" stroke-width="3"/>
      <rect x="175" y="230" width="222" height="102" rx="18" fill="url(#labMotor)" stroke="#65bce9" stroke-width="3"/>
      <g stroke="#7bc8ef" stroke-width="2" opacity=".45"><line x1="200" y1="242" x2="200" y2="320"/><line x1="222" y1="242" x2="222" y2="320"/><line x1="244" y1="242" x2="244" y2="320"/><line x1="266" y1="242" x2="266" y2="320"/><line x1="288" y1="242" x2="288" y2="320"/><line x1="310" y1="242" x2="310" y2="320"/></g>
      <rect x="397" y="266" width="65" height="28" rx="7" fill="#66737d"/>
      <path d="M460 205 C555 196 579 292 518 332 C482 355 438 329 433 291 C428 251 438 216 460 205z" fill="url(#labMetal)" stroke="#c8d0d5" stroke-width="3"/>
      <circle cx="485" cy="277" r="36" fill="#17242d" stroke="#aeb9c0" stroke-width="4"/><circle cx="485" cy="277" r="10" fill="#dde2e5"/>
      <path d="M499 211 V158 H708" fill="none" stroke="url(#labMetal)" stroke-width="26" stroke-linejoin="round"/>
      <path d="M521 277 H655" fill="none" stroke="url(#labMetal)" stroke-width="27"/>{flex}
      <path d="M740 266 H925 V350 H1010" fill="none" stroke="url(#labMetal)" stroke-width="26"/>
      <rect x="887" y="329" width="54" height="46" rx="6" fill="#1a3548" stroke="#56d2ff" stroke-width="2"/>
      {isolators}
      <rect x="80" y="432" width="970" height="80" rx="4" fill="#4a565f" stroke="#7c8993" stroke-width="3"/><path d="M110 470 H1018" stroke="#2e363d" stroke-width="5" opacity=".6"/>
      <g opacity=".95" filter="url(#lg)" stroke="{base_color}" fill="none"><path d="M255 398 V432" stroke-width="7"/><path d="M452 398 V432" stroke-width="7"/></g>
      <g opacity=".9" filter="url(#lg)" stroke="{pipe_color}" fill="none" stroke-dasharray="10 7"><path d="M742 266 H922 V350 H1008" stroke-width="5"/><path d="M905 376 V512" stroke-width="4"/></g>
      <g opacity=".8" filter="url(#lg)" stroke="{air_color}" fill="none" stroke-width="5"><path d="M125 218 Q55 278 125 338"/><path d="M95 192 Q0 278 95 364"/><path d="M542 210 Q606 278 542 346"/></g>
      <rect x="1048" y="145" width="205" height="367" fill="#111f2c" stroke="#526777" stroke-width="3"/>
      <rect x="1082" y="355" width="130" height="46" rx="8" fill="#344657"/><rect x="1098" y="334" width="98" height="38" rx="8" fill="#526578"/><circle cx="1130" cy="349" r="13" fill="#d3b19d"/>
      <text x="1150" y="448" text-anchor="middle" class="t label">RECINTO</text>
      <rect x="80" y="540" width="342" height="82" rx="13" fill="#0b2743" stroke="{base_color}" stroke-width="2"/><text x="104" y="568" class="t small">BASE → LOSA</text><text x="104" y="600" class="t label" fill="{base_color}">{base_state}</text>
      <rect x="469" y="540" width="342" height="82" rx="13" fill="#0b2743" stroke="{pipe_color}" stroke-width="2"/><text x="493" y="568" class="t small">TUBERÍA → ESTRUCTURA</text><text x="493" y="600" class="t label" fill="{pipe_color}">{pipe_state}</text>
      <rect x="858" y="540" width="342" height="82" rx="13" fill="#0b2743" stroke="{air_color}" stroke-width="2"/><text x="882" y="568" class="t small">RUIDO AÉREO</text><text x="882" y="600" class="t label" fill="{air_color}">{air_state}</text>
    </svg>'''


def _course2_lab1_stage0_pump_lab(class_id, saved):
    """Punto 7 · Laboratorio conceptual de control vibroacústico de una bomba."""
    st.markdown("### 7 · Laboratorio conceptual · Controla la bomba")
    st.write(
        "Selecciona una medida y observa **qué cambia físicamente en la instalación** "
        "y qué camino de transmisión resulta afectado. "
        "Los estados son conceptuales y no representan una predicción en dB."
    )

    states = {
        "Estado inicial": {
            "asset": "curso2_lab1_etapa0_p7_estado_inicial.webp",
            "base": ("ACTIVO", "La bomba puede excitar directamente la losa mediante apoyos rígidos."),
            "pipe": ("ACTIVO", "La tubería y sus apoyos mantienen continuidad mecánica con la estructura."),
            "air": ("ACTIVO", "La máquina puede radiar ruido directamente al aire."),
            "note": "Instalación de referencia sin medidas de control.",
        },
        "Aisladores bajo la bomba": {
            "asset": "curso2_lab1_etapa0_p7_aisladores.webp",
            "base": ("REDUCIDO", "Los aisladores desacoplan la bancada respecto de la losa."),
            "pipe": ("ACTIVO", "La tubería todavía puede actuar como puente estructural."),
            "air": ("ACTIVO", "El ruido aéreo de la máquina no ha sido tratado."),
            "note": "Los aisladores actúan principalmente sobre el camino máquina → bancada → losa.",
        },
        "Conexión flexible": {
            "asset": "curso2_lab1_etapa0_p7_conexion_flexible.webp",
            "base": ("ACTIVO", "Los apoyos de la bomba siguen conectados a la losa."),
            "pipe": ("PARCIAL", "El flexible reduce la transmisión desde la bomba hacia la tubería rígida."),
            "air": ("ACTIVO", "La radiación aérea no se modifica."),
            "note": "La conexión flexible interviene la continuidad mecánica entre máquina y tubería.",
        },
        "Soportes resilientes": {
            "asset": "curso2_lab1_etapa0_p7_soportes_resilientes.webp",
            "base": ("ACTIVO", "La transmisión por los apoyos de la bomba no cambia."),
            "pipe": ("PARCIAL", "Los soportes resilientes reducen el puente tubería → estructura."),
            "air": ("ACTIVO", "La radiación aérea no se modifica."),
            "note": "Los soportes resilientes desacoplan la tubería de la estructura en sus apoyos.",
        },
        "Encierro acústico sin ventilación": {
            "asset": "curso2_lab1_etapa0_p7_encierro_sin_ventilacion.webp",
            "base": ("ACTIVO", "El encierro no desacopla la bomba de la losa."),
            "pipe": ("ACTIVO", "La tubería continúa siendo un camino estructural posible."),
            "air": ("PARCIAL", "El cerramiento reduce la radiación directa y mantiene ventilación del equipo."),
            "note": "El cerramiento reduce la radiación aérea de la máquina, pero sin ventilación puede aumentar la temperatura del motor; se usa aquí como contraste conceptual, no como solución recomendada para operación continua.",
        },
        "Encierro acústico con ventilación": {
            "asset": "curso2_lab1_etapa0_p7_encierro_con_ventilacion.webp",
            "base": ("ACTIVO", "Esta medida no actúa sobre los apoyos de la máquina."),
            "pipe": ("ACTIVO", "Esta medida no actúa sobre la transmisión por tuberías."),
            "air": ("REDUCIDO", "Las entradas y salidas de aire se tratan para limitar la fuga acústica."),
            "note": "El encierro incorpora louvers para permitir el paso de aire y favorecer la disipación del calor del motor, evitando dejar una abertura completamente libre.",
        },
        "Control estructural completo": {
            "asset": "curso2_lab1_etapa0_p7_control_estructural.webp",
            "base": ("REDUCIDO", "Los aisladores reducen el camino máquina → losa."),
            "pipe": ("REDUCIDO", "Flexible y soportes resilientes reducen el camino por tuberías."),
            "air": ("ACTIVO", "La radiación aérea directa todavía debe tratarse."),
            "note": "Aisladores + conexión flexible + soportes resilientes.",
        },
        "Control integral ventilado": {
            "asset": "curso2_lab1_etapa0_p7_control_integral_ventilado_v2.webp",
            "base": ("REDUCIDO", "La bancada está desacoplada de la losa."),
            "pipe": ("REDUCIDO", "La tubería está desacoplada en conexión y apoyos."),
            "air": ("REDUCIDO", "Encierro ventilado y silenciadores reducen el camino aéreo."),
            "note": "Control integral: aisladores bajo la bomba + conexión flexible + soportes resilientes + encierro acústico opaco con louvers de ventilación.",
        },
    }

    state_key = f"{class_id}_pump_control_state"
    stored = saved.get("stage0_pump_lab_state", "Estado inicial")
    aliases = {
        "Aisladores": "Aisladores bajo la bomba",
        "Encierro acústico": "Encierro acústico sin ventilación",
        "Encierro + absorbente": "Encierro acústico con ventilación",
        "Control integral": "Control integral ventilado",
    }
    stored = aliases.get(stored, stored)
    if stored not in states:
        stored = "Estado inicial"
    if state_key not in st.session_state:
        st.session_state[state_key] = stored

    def choose(label, suffix):
        if st.button(
            label,
            key=f"{class_id}_pump_state_{suffix}",
            use_container_width=True,
            type="primary" if st.session_state[state_key] == label else "secondary",
        ):
            st.session_state[state_key] = label
            saved["stage0_pump_lab_state"] = label
            saved["stage0_pump_lab_explored"] = True
            saved["stage0_pump_lab_updated_at"] = _now()
            _save_future_state_impl(class_id, saved)
            st.rerun()

    st.markdown("#### 1 · Explora una medida")
    r1, r2 = st.columns(3), st.columns(3)
    labels = [
        "Estado inicial",
        "Aisladores bajo la bomba",
        "Conexión flexible",
        "Soportes resilientes",
        "Encierro acústico sin ventilación",
        "Encierro acústico con ventilación",
    ]
    for i, label in enumerate(labels):
        with (r1[i] if i < 3 else r2[i-3]):
            choose(label, i)

    st.markdown("#### 2 · Compara soluciones")
    c1, c2 = st.columns(2)
    with c1:
        choose("Control estructural completo", 20)
    with c2:
        choose("Control integral ventilado", 21)

    current = st.session_state[state_key]
    if current not in states:
        current = "Estado inicial"
        st.session_state[state_key] = current
    cfg = states[current]

    path = ASSET_DIR / cfg["asset"]
    if path.exists():
        st.image(str(path), width="stretch")
    else:
        st.error(f"No se encontró el render `{cfg['asset']}`.")

    st.info(cfg["note"])

    st.markdown("#### ¿Qué camino estás interviniendo?")
    cols = st.columns(3)
    cards = [
        ("MÁQUINA → LOSA", cfg["base"]),
        ("TUBERÍA → ESTRUCTURA", cfg["pipe"]),
        ("CARCASA → AIRE", cfg["air"]),
    ]
    for col, (title, (status, desc)) in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(f"### {status}")
                st.caption(desc)

    if current == "Aisladores bajo la bomba":
        st.warning("Una tubería rígida puede seguir puenteando el aislamiento de la base.")
    elif current == "Conexión flexible":
        st.warning("El flexible no sustituye el tratamiento de los soportes rígidos de la tubería.")
    elif current == "Soportes resilientes":
        st.warning("Los soportes resilientes no sustituyen una conexión flexible próxima a la máquina.")
    elif current == "Encierro acústico sin ventilación":
        st.warning("Este estado muestra qué ocurre al encerrar la máquina sin prever ventilación: puede reducir ruido aéreo, pero no es una solución adecuada para operación continua si el motor acumula calor.")
    elif current == "Encierro acústico con ventilación":
        st.info("Los louvers permiten ventilación del encierro. Su diseño debe limitar la transmisión sonora y mantener el caudal de aire necesario para el motor.")
    elif current == "Control estructural completo":
        st.success("Los caminos estructurales representados están intervenidos; el camino aéreo permanece activo.")
    elif current == "Control integral ventilado":
        st.success("La solución combina control estructural, control aéreo y ventilación acústicamente tratada.")

    st.markdown(
        """
        <div style="
            border:1px solid #cfd8e3;
            border-radius:12px;
            padding:16px 18px;
            margin:14px 0 18px 0;
            background:#f8fbff;">
            <div style="font-weight:700; font-size:1.02rem; margin-bottom:10px;">
                🧭 Conclusión del laboratorio
            </div>
            <div style="line-height:1.6; margin-bottom:8px;">
                Una bomba puede transferir energía simultáneamente por <b>apoyos</b>,
                <b>tuberías</b> y <b>radiación aérea</b>. Por eso:
            </div>
            <ul style="margin:8px 0 0 20px; line-height:1.6;">
                <li>los aisladores no sustituyen el desacoplamiento de tuberías;</li>
                <li>una conexión flexible no sustituye soportes adecuados;</li>
                <li>un encierro no sustituye el control estructural;</li>
                <li>un encierro acústico debe permitir la <b>ventilación necesaria del motor y la disipación del calor</b>;</li>
                <li>los louvers de ventilación deben seleccionarse y disponerse para permitir el flujo de aire sin crear una vía acústica dominante.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Principio profesional**")
    st.info(
        "El control efectivo consiste en identificar los caminos relevantes "
        "y aplicar la medida adecuada en el punto físico correcto."
    )

def _course2_lab1_stage0_energy_interactive(class_id, saved):
    """Observación inicial y exploración visual de las fuentes."""
    projection_mode = (
        st.session_state.get("projection_mode")
        or st.session_state.get("role") == "Proyección"
    )

    projection_state_key = f"{class_id}_s0_projection_energy"

    if projection_mode:
        state = st.session_state.get(projection_state_key, {})
        if not isinstance(state, dict):
            state = {}
    else:
        state = saved.get("stage0_energy") if isinstance(saved.get("stage0_energy"), dict) else {}

    identified = bool(state.get("identified", False))
    explored = set(state.get("explored", []))

    sources = {
        "Pisada": "curso2_lab1_etapa0_highlight_pisada.webp",
        "Bomba": "curso2_lab1_etapa0_highlight_bomba.webp",
        "Descarga sanitaria": "curso2_lab1_etapa0_highlight_sanitaria.webp",
    }
    base_asset = ASSET_DIR / "curso2_lab1_etapa0_edificio_vibroacustico.webp"

    st.markdown("### 🔎 Observa el edificio")
    st.write(
        "Identifica primero las fuentes relevantes. Después podrás seguir, sobre la **misma escena**, "
        "el recorrido principal de la energía de cada una."
    )

    if not identified:
        if base_asset.exists():
            st.image(base_asset, width="stretch")
        else:
            st.warning("Falta la imagen base del edificio vibroacústico.")

        options = [
            "Pisadas de una persona",
            "Bomba centrífuga",
            "Descarga sanitaria",
            "Conversación de la pareja",
            "Refrigerador",
            "Iluminación del departamento",
        ]
        correct = {"Pisadas de una persona", "Bomba centrífuga", "Descarga sanitaria"}

        selected = set()
        for i, opt in enumerate(options):
            if st.checkbox(opt, key=f"{class_id}_s0_ident_{i}"):
                selected.add(opt)

        c1, c2 = st.columns([0.78, 0.22])

        with c1:
            if st.button(
                "Comprobar identificación",
                type="primary",
                use_container_width=True,
                key=f"{class_id}_s0_check_sources",
            ):
                if selected == correct:
                    new_state = {
                        "identified": True,
                        "explored": sorted(explored),
                        "updated_at": _now(),
                    }

                    if projection_mode:
                        st.session_state[projection_state_key] = new_state
                    else:
                        saved["stage0_energy"] = new_state
                        _save_future_state_impl(class_id, saved)

                    st.rerun()
                else:
                    st.session_state[f"{class_id}_s0_ident_feedback"] = True

        with c2:
            if projection_mode and st.button(
                "Reiniciar",
                use_container_width=True,
                key=f"{class_id}_s0_reset_sources_projection",
            ):
                st.session_state.pop(projection_state_key, None)
                st.session_state.pop(f"{class_id}_s0_ident_feedback", None)
                for i in range(len(options)):
                    st.session_state.pop(f"{class_id}_s0_ident_{i}", None)
                st.rerun()

        if st.session_state.get(f"{class_id}_s0_ident_feedback"):
            missed = correct - selected
            extra = selected - correct

            feedback = []
            if missed:
                feedback.append("Falta identificar: **" + ", ".join(sorted(missed)) + "**.")
            if extra:
                feedback.append(
                    "Revisa: **" + ", ".join(sorted(extra)) +
                    "**; no corresponde a las fuentes estructurales objetivo de esta observación."
                )

            st.warning(" ".join(feedback) if feedback else
                       "Revisa la escena y vuelve a intentarlo.")

        st.caption("Actividad de observación · sin puntaje.")
        return len(explored), len(sources)

    st.success(
        "Muy bien. Identificaste las fuentes representadas. "
        "Ahora sigue la energía desde cada una."
    )
    st.markdown("#### Sigue la energía")
    st.caption(
        "Selecciona una fuente. La imagen base es la misma; "
        "solo cambia el camino destacado."
    )

    cols = st.columns(3)
    active_key = f"{class_id}_s0_active_source"
    if active_key not in st.session_state:
        st.session_state[active_key] = "Pisada"

    for col, name in zip(cols, sources):
        with col:
            label = ("✓ " if name in explored else "") + name
            if st.button(
                label,
                use_container_width=True,
                type="primary" if st.session_state[active_key] == name else "secondary",
                key=f"{class_id}_s0_source_{name}",
            ):
                st.session_state[active_key] = name
                explored.add(name)

                new_state = {
                    "identified": True,
                    "explored": sorted(explored),
                    "updated_at": _now(),
                }

                if projection_mode:
                    st.session_state[projection_state_key] = new_state
                else:
                    saved["stage0_energy"] = new_state
                    _save_future_state_impl(class_id, saved)

                st.rerun()

    active = st.session_state[active_key]
    img = ASSET_DIR / sources[active]
    if img.exists():
        st.image(img, width="stretch")
    else:
        st.warning(f"Falta el asset `{sources[active]}`.")

    explanations = {
        "Pisada": (
            "El impacto excita directamente la losa. La vibración se propaga por la estructura "
            "y una superficie puede radiar sonido hacia el recinto receptor."
        ),
        "Bomba": (
            "La bomba puede transferir energía por su base y por la tubería; "
            "además, su carcasa puede radiar directamente al aire."
        ),
        "Descarga sanitaria": (
            "La excitación asociada al flujo puede transmitirse a la tubería y a sus fijaciones, "
            "propagarse por la estructura y radiarse posteriormente al aire."
        ),
    }
    st.info(explanations[active])

    if st.button(
        "↺ Volver a identificar las fuentes",
        use_container_width=True,
        key=f"{class_id}_s0_reset_ident",
    ):
        new_state = {
            "identified": False,
            "explored": sorted(explored),
            "updated_at": _now(),
        }

        if projection_mode:
            st.session_state[projection_state_key] = new_state
        else:
            saved["stage0_energy"] = new_state
            _save_future_state_impl(class_id, saved)

        st.session_state.pop(f"{class_id}_s0_ident_feedback", None)
        for i in range(6):
            st.session_state.pop(f"{class_id}_s0_ident_{i}", None)
        st.rerun()

    return len(explored), len(sources)

def _future_stage0_mcq(class_id, saved, key, question, options, correct, feedback):
    """Pregunta formativa persistente para la Etapa 0; no asigna puntaje ni nota."""
    state_key = f"{class_id}_{key}"
    record = saved.get(key) if isinstance(saved.get(key), dict) else {}
    previous = record.get("choice")
    if state_key not in st.session_state and previous in options:
        st.session_state[state_key] = previous

    st.markdown(f"**{question}**")
    choice = st.radio(
        "Selecciona una respuesta",
        options,
        index=None,
        key=state_key,
        label_visibility="collapsed",
    )

    if record.get("completed"):
        if record.get("correct"):
            st.success(feedback)
        else:
            st.error("Respuesta incorrecta. Revisa el mecanismo de transmisión y vuelve a intentarlo si lo necesitas.")
        st.caption(f"Respuesta guardada: {record.get('choice', '—')}")

    label = "Actualizar respuesta" if record.get("completed") else "Comprobar y guardar"
    if st.button(label, key=f"save_{state_key}"):
        if choice is None:
            st.warning("Selecciona una alternativa antes de comprobar.")
        else:
            is_correct = choice == correct
            saved[key] = {
                "choice": choice,
                "correct": is_correct,
                "completed": True,
                "updated_at": _now(),
            }
            _save_future_state_impl(class_id, saved)
            st.rerun()



def _render_course2_lab1_welcome(lab, saved):
    """Etapa 0 · Bienvenida y ruta, con la misma lógica visual del Curso 1."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"

    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 1 · Control de ruido de impacto e instalaciones",
        "Una experiencia visual y aplicada para comprender cómo se genera, transmite, mide y controla la energía vibroacústica en edificios.",
        show_overview=False,
        duration_minutes=10,
    )

    # 210 min de aprendizaje + 30 min de pausa = 4 h.
    route_minutes = [35, 15, 15, 15, 15, 20, 20, 20, 25, 30]
    break_after_stage = 5
    break_minutes = 30
    active_minutes = sum(route_minutes)
    total_minutes = active_minutes + break_minutes

    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Duración total del laboratorio: 4 horas</strong>'
        f'<br><span>{active_minutes} min de aprendizaje y aplicación + {break_minutes} min de pausa</span>'
        f'</div><div><strong>{total_minutes} min</strong></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )

    route_descriptions = [
        "Reconoce el edificio como sistema vibroacústico y sigue la energía desde la fuente hasta el receptor.",
        "Distingue fuente, camino de transmisión, estructura radiante y receptor.",
        "Interpreta desplazamiento, velocidad y aceleración como magnitudes complementarias.",
        "Comprende los descriptores utilizados para evaluar ruido de impacto.",
        "Aplica conceptualmente la normalización por tiempo de reverberación.",
        "Lee espectros y selecciona una cadena básica de instrumentación.",
        "Relaciona piso flotante, resiliencia, desacoplamiento y puentes rígidos.",
        "Aplica criterios de control a bombas, tuberías y otras instalaciones.",
        "Comprueba tu comprensión mediante preguntas conceptuales y aplicadas.",
        "Integra diagnóstico, evidencia y medidas de control en un caso profesional.",
    ]

    html = '<div class="route-grid">'
    for stage in range(1, len(lab["stages"])):
        title = lab["stages"][stage][0]
        description = route_descriptions[stage - 1]
        minutes = route_minutes[stage - 1]
        html += (
            f'<div class="route-card"><span class="step">{stage}</span><div>'
            f'<b>{title}</b><p>{description}</p>'
            f'<span class="route-time">⏱️ {minutes} min</span></div></div>'
        )
        if stage == break_after_stage:
            html += (
                f'<div class="break-card"><span class="step">☕</span><div>'
                f'<b>Pausa pedagógica</b><p>Descanso antes de continuar con el bloque aplicado.</p>'
                f'<span class="route-time">⏱️ {break_minutes} min</span></div></div>'
            )
    st.markdown(html + "</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> '
        'observación visual → mecanismo físico → magnitud → medición → diagnóstico → control → caso profesional.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="warn" style="margin-top:1rem"><b>Idea central del laboratorio:</b> '
        'antes de seleccionar una solución debes reconocer por dónde entra, se propaga y se radia la energía.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Comenzar laboratorio →", type="primary", key=f"start_course2_lab1_{class_id}", width="stretch"):
        saved["done_0"] = True
        saved["updated_0"] = _now()
        _save_future_state_impl(class_id, saved)
        st.session_state[stage_selector_key] = 1
        st.rerun()


def _course2_stage1_comprehension_block(class_id, saved):
    """Cinco preguntas de comprensión de la Etapa 1, con lógica por rol."""
    role = st.session_state.get("role", "Alumno")
    projection_mode = (
        st.session_state.get("projection_mode")
        or role == "Proyección"
    )

    questions = [
        {
            "id": "q1",
            "question": (
                "Una bomba está ubicada dos pisos más abajo y una persona escucha ruido en un dormitorio. "
                "¿Cuál es la interpretación más correcta?"
            ),
            "options": [
                "El sonido necesariamente viajó solo por el aire.",
                "Puede existir transmisión estructural, transmisión aérea o ambas simultáneamente.",
                "Si la bomba está lejos, la transmisión estructural deja de ser relevante.",
                "La distancia entre pisos permite descartar las tuberías como camino de transmisión.",
            ],
            "correct": 1,
            "feedback": (
                "Una misma fuente puede transferir energía por varios caminos simultáneamente. "
                "La distancia no permite concluir que el fenómeno sea exclusivamente aéreo."
            ),
        },
        {
            "id": "q2",
            "question": (
                "Se mide vibración claramente en una losa. ¿Qué conclusión puede hacerse respecto de la radiación acústica?"
            ),
            "options": [
                "Toda vibración medible implica radiación acústica eficiente.",
                "La vibración demuestra que la losa es la fuente dominante de ruido.",
                "La vibración puede permitir radiación, pero no demuestra por sí sola que ésta sea eficiente.",
                "Si existe vibración, la frecuencia deja de ser relevante.",
            ],
            "correct": 2,
            "feedback": (
                "La eficiencia de radiación depende, entre otros factores, de la frecuencia, las dimensiones, "
                "el patrón espacial de vibración y el acoplamiento estructura–aire."
            ),
        },
        {
            "id": "q3",
            "question": (
                "¿Cuál de las siguientes secuencias representa mejor un fenómeno de ruido de origen estructural?"
            ),
            "options": [
                "Fuente → aire → receptor → vibración.",
                "Fuente → excitación → respuesta estructural → propagación → radiación → receptor.",
                "Fuente → receptor → estructura → aire.",
                "Radiación → fuente → propagación → estructura.",
            ],
            "correct": 1,
            "feedback": (
                "La energía parte en la fuente, excita una estructura, se propaga mecánicamente, "
                "puede radiarse al aire y finalmente alcanzar al receptor."
            ),
        },
        {
            "id": "q4",
            "question": (
                "Una bomba está montada sobre aisladores, pero una tubería rígida sale directamente de la bomba "
                "y está fijada al edificio mediante soportes rígidos. ¿Qué problema puede permanecer?"
            ),
            "options": [
                "Ninguno: los aisladores bajo la bomba eliminan todos los caminos estructurales.",
                "La tubería puede puentear el aislamiento y transmitir vibración hacia la estructura.",
                "Solo puede quedar ruido aéreo; la transmisión estructural queda descartada.",
                "Los soportes rígidos reducen automáticamente la transmisión de vibración.",
            ],
            "correct": 1,
            "feedback": (
                "La tubería y sus soportes pueden constituir un puente mecánico. "
                "El aislamiento de la base no controla automáticamente ese camino."
            ),
        },
        {
            "id": "q5",
            "question": (
                "Una bomba está sobre aisladores, la tubería tiene conexión flexible y soportes resilientes. "
                "Las vibraciones estructurales disminuyen, pero la bomba sigue siendo claramente audible. "
                "¿Qué camino investigarías ahora prioritariamente?"
            ),
            "options": [
                "Base → losa → estructura.",
                "Tubería → soportes → estructura.",
                "Carcasa → aire → receptor.",
                "Ninguno; si bajó la vibración estructural, el problema ya está resuelto.",
            ],
            "correct": 2,
            "feedback": (
                "Si los caminos estructurales ya fueron intervenidos y el equipo sigue siendo audible, "
                "debe investigarse prioritariamente la radiación aérea de la carcasa hacia el receptor."
            ),
        },
    ]

    st.markdown("### 7 · Comprueba tu comprensión")
    st.caption(
        "Cinco preguntas para verificar si puedes aplicar el modelo físico de la etapa, "
        "no solo recordar definiciones."
    )

    # Docente: pauta visible, sin responder ni generar progreso.
    if role == "Docente" and not projection_mode:
        for idx, q in enumerate(questions, start=1):
            with st.container(border=True):
                st.markdown(f"#### {idx}. {q['question']}")
                for option_idx, option in enumerate(q["options"]):
                    prefix = "✅" if option_idx == q["correct"] else "○"
                    st.write(f"{prefix} {chr(65 + option_idx)}. {option}")
                st.caption("Explicación: " + q["feedback"])
        return

    # Proyección: interacción temporal, sin base de datos.
    if projection_mode:
        projection_key = f"{class_id}_stage1_projection_answers"
        projection_answers = st.session_state.get(projection_key, {})
        if not isinstance(projection_answers, dict):
            projection_answers = {}

        for idx, q in enumerate(questions, start=1):
            st.markdown(f"#### {idx}. {q['question']}")
            selected = st.radio(
                f"Pregunta proyectada {idx}",
                q["options"],
                index=None,
                key=f"{class_id}_projection_{q['id']}",
                label_visibility="collapsed",
            )
            c1, c2 = st.columns([0.78, 0.22])
            with c1:
                if st.button(
                    "Comprobar",
                    key=f"{class_id}_projection_check_{q['id']}",
                    use_container_width=True,
                ):
                    if selected is None:
                        st.warning("Selecciona una alternativa antes de comprobar.")
                    else:
                        selected_idx = q["options"].index(selected)
                        projection_answers[q["id"]] = {
                            "selected": selected_idx,
                            "correct": selected_idx == q["correct"],
                        }
                        st.session_state[projection_key] = projection_answers
                        st.rerun()
            with c2:
                if st.button(
                    "Limpiar",
                    key=f"{class_id}_projection_reset_{q['id']}",
                    use_container_width=True,
                ):
                    projection_answers.pop(q["id"], None)
                    st.session_state[projection_key] = projection_answers
                    st.session_state.pop(f"{class_id}_projection_{q['id']}", None)
                    st.rerun()

            result = projection_answers.get(q["id"])
            if isinstance(result, dict):
                if result.get("correct"):
                    st.success("Correcto. " + q["feedback"])
                else:
                    st.error("Aún no es correcto. Revisa el mecanismo físico y vuelve a intentarlo.")
            st.markdown("---")
        return

    # Alumno: guardado formativo.
    answer_key = "stage1_comprehension"
    stored_answers = saved.get(answer_key, {})
    if not isinstance(stored_answers, dict):
        stored_answers = {}

    for idx, q in enumerate(questions, start=1):
        st.markdown(f"#### {idx}. {q['question']}")
        previous = stored_answers.get(q["id"], {})
        previous_idx = previous.get("selected") if isinstance(previous, dict) else None
        default_idx = (
            previous_idx
            if isinstance(previous_idx, int) and 0 <= previous_idx < len(q["options"])
            else None
        )

        selected = st.radio(
            f"Pregunta {idx}",
            q["options"],
            index=default_idx,
            key=f"{class_id}_stage1_{q['id']}",
            label_visibility="collapsed",
        )

        if st.button(
            "Comprobar y guardar",
            key=f"{class_id}_stage1_check_{q['id']}",
        ):
            selected_idx = q["options"].index(selected)
            is_correct = selected_idx == q["correct"]
            stored_answers[q["id"]] = {
                "selected": selected_idx,
                "correct": is_correct,
                "updated_at": _now(),
            }
            saved[answer_key] = stored_answers
            saved["updated_1"] = _now()
            _save_future_state_impl(class_id, saved)
            st.rerun()

        result = stored_answers.get(q["id"])
        if isinstance(result, dict) and "selected" in result:
            if result.get("correct"):
                st.success("Correcto. " + q["feedback"])
            else:
                st.error("Aún no es correcto. Revisa el mecanismo físico y vuelve a intentarlo.")

        st.markdown("---")

    answered_count = sum(
        1 for q in questions
        if isinstance(stored_answers.get(q["id"]), dict)
        and "selected" in stored_answers[q["id"]]
    )
    correct_count = sum(
        1 for q in questions
        if isinstance(stored_answers.get(q["id"]), dict)
        and stored_answers[q["id"]].get("correct") is True
    )

    st.markdown(
        f"""
        <div style="
            border:1px solid #cfd8e3;
            border-radius:12px;
            padding:14px 16px;
            margin:8px 0 18px 0;
            background:#f8fbff;">
            <b>Progreso de comprensión</b><br>
            Respondidas: <b>{answered_count}/5</b> · Correctas: <b>{correct_count}/5</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_course2_lab1_stage1(lab, saved):
    """Etapa 1 · Del fenómeno al diagnóstico y al control."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = (
        st.session_state.get("projection_mode")
        or role == "Proyección"
    )

    header(
        "ETAPA 1 · LABORATORIO 1",
        "El edificio como sistema vibroacústico",
        "Observa, sigue la energía, diagnostica sus caminos y decide dónde intervenir.",
        show_overview=False,
        duration_minutes=45,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.markdown(
        """
- Reconocer el edificio como un **sistema de transmisión de energía vibroacústica**.
- Diferenciar transmisión **aérea** y **estructural**.
- Comprender cuándo una superficie vibrante puede **radiar sonido** al aire.
- Seguir una ruta completa desde **fuente → excitación → propagación → radiación → receptor**.
- Diagnosticar **caminos simultáneos** en una instalación y seleccionar medidas de control coherentes.
        """
    )

    st.markdown("### Antes de comenzar")
    st.info(
        "En acústica de edificios no basta con identificar dónde se escucha el ruido. "
        "Para controlarlo necesitamos descubrir **dónde se genera la energía, cómo entra al sistema, "
        "por dónde se propaga y qué elemento termina radiándola hacia el receptor**."
    )
    st.latex(
        r"\mathrm{FUENTE \rightarrow EXCITACIÓN \rightarrow RESPUESTA \rightarrow PROPAGACIÓN "
        r"\rightarrow RADIACIÓN \rightarrow RECEPTOR}"
    )

    # --------------------------------------------------------
    # 0 · OBSERVAR
    # --------------------------------------------------------
    _course2_lab1_stage0_energy_interactive(class_id, saved)

    # --------------------------------------------------------
    # 1 · MODELO MENTAL
    # --------------------------------------------------------
    st.markdown("### 1 · Sigue la energía")
    st.write(
        "Una vez identificada la fuente, el diagnóstico no consiste en volver a preguntar qué produce ruido, "
        "sino en seguir **cómo la energía sale de la fuente, entra al edificio, cambia de medio y llega al receptor**."
    )
    st.latex(
        r"\boxed{\mathrm{FUENTE \rightarrow EXCITACIÓN \rightarrow RESPUESTA \rightarrow "
        r"PROPAGACIÓN \rightarrow RADIACIÓN \rightarrow RECEPTOR}}"
    )
    st.info(
        "Una misma fuente puede disponer de **varios caminos simultáneos**. "
        "El análisis vibroacústico consiste en seguirlos y determinar cuáles son relevantes en el receptor."
    )

    # --------------------------------------------------------
    # 2 · DOS FORMAS DE ENTRAR AL SISTEMA
    # --------------------------------------------------------
    st.markdown("### 2 · Dos formas de entrar al sistema")
    c_air, c_struct = st.columns(2)

    with c_air:
        with st.container(border=True):
            st.markdown("#### Ruido aéreo")
            st.latex(r"p \rightarrow v_n \rightarrow p")
            st.write(
                "La fuente genera primero fluctuaciones de presión en el aire. "
                "Ese campo puede excitar un elemento constructivo, hacerlo vibrar y producir una nueva radiación al otro lado."
            )
            st.caption("**Primero el aire.**")

    with c_struct:
        with st.container(border=True):
            st.markdown("#### Ruido estructural")
            st.latex(r"F(t) \rightarrow v_n(t) \rightarrow p(t)")
            st.write(
                "La fuente introduce primero una fuerza o velocidad mecánica en la estructura. "
                "La vibración se propaga por elementos sólidos y una superficie puede posteriormente radiar sonido al aire."
            )
            st.caption("**Primero la estructura.**")

    st.caption(
        "Aquí \(v_n\) representa la **componente normal** del movimiento de la superficie, "
        "la que desplaza directamente el aire adyacente."
    )

    # --------------------------------------------------------
    # 3 · CUÁNDO VIBRAR PRODUCE SONIDO
    # --------------------------------------------------------
    st.markdown("### 3 · ¿Cuándo una superficie vibrante produce sonido?")
    st.write(
        "Primero necesitamos movimiento normal de la superficie; después debemos preguntarnos "
        "si ese movimiento se acopla de manera eficiente con el aire."
    )

    # Reuse the pre-existing surface-motion interactive if present in this project.
    tangential = ASSET_DIR / "curso2_lab1_etapa0_mov_tangencial.webp"
    normal = ASSET_DIR / "curso2_lab1_etapa0_mov_normal_apreciable.webp"

    motion_key = f"{class_id}_stage1_motion"
    motion = st.radio(
        "Explora dos formas de movimiento de la misma superficie:",
        ["Movimiento tangencial", "Movimiento normal"],
        horizontal=True,
        key=motion_key,
    )

    motion_asset = tangential if motion == "Movimiento tangencial" else normal
    if motion_asset.exists():
        st.image(motion_asset, width="stretch")

    if motion == "Movimiento tangencial":
        st.info(
            "El movimiento es principalmente paralelo a la superficie. "
            "Puede existir vibración medible, pero el desplazamiento normal del aire es pequeño."
        )
    else:
        st.success(
            "La superficie se mueve hacia y desde el aire. "
            "Existe una componente normal capaz de generar fluctuaciones de presión."
        )

    st.latex(r"v_n(t)\neq 0 \quad \Rightarrow \quad \text{la superficie puede acoplar energía al aire}")

    radiation_overview = ASSET_DIR / "curso2_lab1_etapa0_vibracion_radiacion.webp"
    if radiation_overview.exists():
        st.image(radiation_overview, width="stretch")

    st.markdown("#### Pero vibrar no significa radiar eficientemente")
    st.latex(r"\mathrm{VIBRACIÓN\ MEDIBLE \neq RADIACIÓN\ ACÚSTICA\ EFICIENTE}")
    st.write(
        "Dos superficies pueden presentar niveles comparables de vibración y, aun así, radiar cantidades de sonido muy diferentes. "
        "Importan la distribución espacial y fase del movimiento, la frecuencia, las dimensiones y el acoplamiento estructura–aire."
    )

    rad_cols = st.columns(2)
    coherent_img = ASSET_DIR / "curso2_lab1_etapa0_radiacion_coherente.webp"
    cancellation_img = ASSET_DIR / "curso2_lab1_etapa0_radiacion_cancelacion.webp"
    with rad_cols[0]:
        if coherent_img.exists():
            st.image(coherent_img, width="stretch")
            st.caption("Mayor contribución coherente: distintas regiones pueden reforzar la radiación neta.")
    with rad_cols[1]:
        if cancellation_img.exists():
            st.image(cancellation_img, width="stretch")
            st.caption("Mayor cancelación espacial: regiones fuera de fase pueden reducir la radiación neta.")

    st.markdown(
        """
        <div style="
            border:1px solid #cfd8e3;
            border-radius:12px;
            padding:16px 18px;
            margin:10px 0 18px 0;
            background:#f8fbff;">
            <div style="font-weight:700; font-size:1.02rem; margin-bottom:8px;">
                💡 ¿Qué representa la eficiencia de radiación σ?
            </div>
            <div style="line-height:1.55;">
                La eficiencia de radiación <b>σ</b> expresa cuán eficazmente el movimiento normal
                de una superficie se convierte en potencia acústica radiada.
                <br><br>
                Medir vibración <b>no demuestra, por sí solo, que una superficie sea un radiador acústico eficiente</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # 4 · APLICACIÓN 1: PISADA
    # --------------------------------------------------------
    st.markdown("### 4 · Aplicación 1 · Sigue una pisada")
    st.write(
        "Ahora sigue una ruta completa desde el impacto hasta el receptor. "
        "La energía cambia de forma y de medio a lo largo del recorrido."
    )

    step_names = ["Impacto", "Respuesta de la losa", "Propagación", "Radiación", "Receptor"]
    step_key = f"{class_id}_stage1_footstep_step"
    if step_key not in st.session_state:
        st.session_state[step_key] = 0

    cols = st.columns(5)
    for i, label in enumerate(step_names):
        with cols[i]:
            if st.button(
                f"{i+1} · {label}",
                key=f"{class_id}_stage1_footstep_{i}",
                use_container_width=True,
                type="primary" if st.session_state[step_key] == i else "secondary",
            ):
                st.session_state[step_key] = i
                st.rerun()

    # Use existing footstep assets if available; otherwise fall back to the main footstep render.
    footstep_assets = [
        "curso2_lab1_etapa0_pisada_impacto.webp",
        "curso2_lab1_etapa0_pisada_respuesta.webp",
        "curso2_lab1_etapa0_pisada_propagacion.webp",
        "curso2_lab1_etapa0_pisada_radiacion.webp",
        "curso2_lab1_etapa0_pisada_receptor.webp",
    ]
    fallback = ASSET_DIR / "curso2_lab1_etapa0_pisada_impacto.webp"
    selected_idx = st.session_state[step_key]
    selected_asset = ASSET_DIR / footstep_assets[selected_idx]
    if selected_asset.exists():
        st.image(selected_asset, width="stretch")
    elif fallback.exists():
        st.image(fallback, width="stretch")

    footstep_feedback = [
        ("F(t)", "El contacto pie–piso introduce una fuerza dinámica variable en el tiempo sobre el sistema de piso."),
        ("v_n(t)", "La losa responde vibrando. La respuesta depende de masa, rigidez, amortiguamiento y condiciones de apoyo."),
        ("v(\mathbf{x},t)", "La vibración se propaga por la losa y por los elementos estructurales conectados."),
        ("p(t)", "Una superficie vibrante puede acoplar energía al aire y producir un campo acústico."),
        ("L_p", "El receptor percibe el resultado final de uno o varios caminos de transmisión."),
    ]
    symbol, explanation = footstep_feedback[selected_idx]
    with st.container(border=True):
        st.latex(symbol)
        st.write(explanation)

    # --------------------------------------------------------
    # 5 · APLICACIÓN 2: DIAGNOSTICA UNA BOMBA
    # --------------------------------------------------------
    st.markdown("### 5 · Aplicación 2 · Diagnostica una bomba")
    st.write(
        "La misma bomba puede entregar energía por varios caminos. "
        "Selecciona uno y observa **qué elemento físico del sistema transporta la energía**."
    )

    path_key = f"{class_id}_stage1_pump_path"
    pump_paths = {
        "Base → losa → estructura": {
            "asset": "curso2_lab1_etapa0_p6_base_resaltada.webp",
            "title": "BOMBA → BASE → LOSA → ESTRUCTURA",
            "text": (
                "La vibración pasa por los apoyos de la máquina hacia la losa y desde allí puede propagarse por la estructura."
            ),
            "question": (
                "Si instalamos aisladores bajo la bomba, ¿podemos concluir que desaparecieron todos los caminos estructurales?"
            ),
            "answer": "No. La tubería y sus soportes todavía pueden constituir un camino mecánico paralelo.",
        },
        "Tubería → soportes → estructura": {
            "asset": "curso2_lab1_etapa0_p6_tuberia_resaltada.webp",
            "title": "BOMBA → TUBERÍA → SOPORTES → ESTRUCTURA",
            "text": (
                "La tubería puede transferir vibración y sus soportes conectarla mecánicamente con la estructura del edificio."
            ),
            "question": (
                "¿Qué concepto explica que una tubería rígida comprometa el aislamiento conseguido bajo la bomba?"
            ),
            "answer": "Puede actuar como un puente rígido y ofrecer una ruta alternativa de transmisión estructural.",
        },
        "Carcasa → aire → receptor": {
            "asset": "curso2_lab1_etapa0_p6_aire_resaltado.webp",
            "title": "CARCASA → AIRE → RECEPTOR",
            "text": (
                "El motor y la carcasa también pueden radiar directamente al aire. "
                "Este camino requiere medidas distintas del desacoplamiento estructural."
            ),
            "question": (
                "Si los caminos estructurales disminuyen pero la bomba sigue siendo audible, ¿qué investigarías?"
            ),
            "answer": "La radiación aérea de la carcasa y las condiciones acústicas entre la fuente y el receptor.",
        },
    }

    path_labels = list(pump_paths.keys())
    if path_key not in st.session_state:
        st.session_state[path_key] = path_labels[0]

    cols = st.columns(3)
    for col, label in zip(cols, path_labels):
        with col:
            if st.button(
                label,
                key=f"{class_id}_stage1_path_{label}",
                use_container_width=True,
                type="primary" if st.session_state[path_key] == label else "secondary",
            ):
                st.session_state[path_key] = label
                st.rerun()

    current_path = pump_paths[st.session_state[path_key]]
    pimg = ASSET_DIR / current_path["asset"]
    if pimg.exists():
        st.image(pimg, width="stretch")

    with st.container(border=True):
        st.markdown(f"#### {current_path['title']}")
        st.write(current_path["text"])

    # Micro-question: temporary in projection/docente, stored only for alumno not needed;
    # pedagogically it is discussion, not scored.
    reveal_key = f"{class_id}_stage1_path_reveal_{st.session_state[path_key]}"
    st.markdown("**Pregunta para discutir:** " + current_path["question"])
    if st.button(
        "Mostrar explicación" if not st.session_state.get(reveal_key) else "Ocultar explicación",
        key=f"{reveal_key}_btn",
    ):
        st.session_state[reveal_key] = not st.session_state.get(reveal_key, False)
        st.rerun()
    if st.session_state.get(reveal_key):
        st.info(current_path["answer"])

    st.success(
        "**Una fuente ≠ un solo camino.** "
        "Los tres mecanismos pueden coexistir y controlar uno no garantiza que los otros hayan dejado de transmitir energía."
    )

    # --------------------------------------------------------
    # 6 · DESAFÍO: CONTROLA LA BOMBA
    # --------------------------------------------------------
    st.markdown("### 6 · Desafío · Controla la bomba")
    st.write(
        "Ahora ya conoces los caminos. La tarea cambia: **elige la medida que actúa sobre el camino que quieres reducir**."
    )
    _course2_lab1_stage0_pump_lab(class_id, saved)

    # Replace duplicated conclusion with one compact synthesis card.
    st.markdown(
        """
        <div style="
            border:1px solid #cfd8e3;
            border-radius:12px;
            padding:16px 18px;
            margin:14px 0 18px 0;
            background:#f8fbff;">
            <div style="font-weight:700; font-size:1.05rem; margin-bottom:10px;">
                🎯 Lo que debes llevarte de esta etapa
            </div>
            <div style="line-height:1.6;">
                Una medida de control es eficaz solo si actúa sobre el <b>camino que realmente transporta energía</b>
                hacia el receptor.
                <br><br>
                <b>Apoyos → aisladores</b><br>
                <b>Tuberías → conexión flexible + soportes resilientes</b><br>
                <b>Radiación aérea → encierro acústico</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # 7 · COMPRENSIÓN
    # --------------------------------------------------------
    _course2_stage1_comprehension_block(class_id, saved)

    nav_left, nav_right = st.columns(2)
    with nav_left:
        if st.button("← Etapa 0", key=f"stage1_prev_{class_id}", width="stretch"):
            st.session_state[stage_selector_key] = 0
            st.rerun()
    with nav_right:
        if st.button("Etapa 2 →", key=f"stage1_next_{class_id}", width="stretch"):
            st.session_state[stage_selector_key] = 2
            st.rerun()

def future_lab_view_impl(lab):
    """Renderer de los laboratorios posteriores manteniendo la navegación institucional."""
    class_id=lab["id"]
    saved=_future_saved(class_id)
    current_lab_label=f"📚 Laboratorio {lab['number']} y actividades"
    results_view_label=(
        "📝 Evaluaciones entregadas"
        if st.session_state.get("role")=="Docente"
        else "🎓 Mi desempeño"
    )

    with st.sidebar:
        uc=ROOT/"assets/logos/logo_uc.png"; decon=ROOT/"assets/logos/logo_decon_uc.png"
        if uc.exists(): st.image(str(uc),width=75)
        if decon.exists(): st.image(str(decon),width=130)
        st.markdown("## ◉ LABORATORIO")
        st.markdown(
            f'<div style="background:#0b4f83;border:1px solid #59d4ef;border-radius:12px;'
            f'padding:.75rem .85rem;margin:.35rem 0 .8rem"><b>LABORATORIO {lab["number"]}</b><br>'
            f'<span style="font-size:.78rem;color:#d9f5ff">{lab["course_short"]}</span></div>',
            unsafe_allow_html=True)
        st.caption("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN")
        st.markdown(f"**{st.session_state.name}**  \n{st.session_state.role}")

        # Misma navegación principal utilizada en los laboratorios del Curso 1.
        future_view_key=f"future_main_view_{class_id}"
        future_options=["🏠 Mis clases", results_view_label, current_lab_label]
        if st.session_state.get(future_view_key) not in future_options:
            st.session_state[future_view_key]=current_lab_label
        future_view=st.radio(
            "Vista",
            future_options,
            key=future_view_key,
            help="Selecciona Mis clases, tu desempeño/evaluaciones o la ruta del laboratorio.",
        )
        if future_view != current_lab_label:
            st.session_state.pop("future_lab_id",None)
            st.session_state["main_view"]=future_view
            st.rerun()

        total_stages = len(lab["stages"])
        if st.session_state.get("role") == "Alumno":
            answered = sum(1 for i in range(total_stages) if saved.get(f"done_{i}"))
            st.progress(answered / total_stages if total_stages else 0)
            if class_id == "clase-03-impacto-instalaciones-lab-1":
                content_completed = sum(1 for i in range(1, total_stages) if saved.get(f"done_{i}"))
                st.caption(
                    f"Avance: {answered}/{total_stages} etapas · "
                    f"{content_completed*10}/100 puntos formativos"
                )
            else:
                st.caption(
                    f"Avance: {answered}/{total_stages} etapas · "
                    f"{answered*10}/{total_stages*10} puntos formativos"
                )
        elif st.session_state.get("role") == "Docente":
            st.caption("Vista docente · el avance y los resultados se revisan desde ‘Evaluaciones entregadas’.")

        # Herramientas comunes del diplomado.
        formula_popup_button()
        st.button(
            "📕 Generar apunte visual (PDF)",
            key=f"future_pdf_pending_{class_id}",
            width="stretch",
            disabled=True,
            help="La exportación visual de este nuevo laboratorio se habilitará cuando sus etapas estén completamente integradas.",
        )

        # Mismos controles de proyección docente disponibles en el Curso 1.
        if st.session_state.get("role")=="Docente":
            st.link_button(
                "🖥️ Abrir vista para Zoom",
                f"?projection=1&future_lab={class_id}",
                width="stretch",
                help="Ábrela en otra ventana y comparte solo esa ventana en Zoom.",
            )
            future_projection_options = {
                f"Etapa {i} · {lab['stages'][i][0]}": i
                for i in range(len(lab["stages"]))
            }
            future_projection_label = st.selectbox(
                "Contenido visible en Zoom",
                list(future_projection_options),
                key=f"future_projection_stage_selector_{class_id}",
            )
            future_projection_stage = future_projection_options[future_projection_label]
            if st.button(
                "Mostrar etapa en Zoom",
                key=f"future_projection_show_{class_id}",
                width="stretch",
            ):
                _set_projection(stage=future_projection_stage, class_id=class_id)
                st.success(
                    f"{future_projection_label} enviada a Zoom. "
                    "Pulsa ‘Actualizar pantalla’ en la ventana de Zoom."
                )

        selected=st.radio(
            "Ruta de aprendizaje",
            list(range(len(lab["stages"]))),
            format_func=lambda i:f"Etapa {i} · {lab['stages'][i][0]}",
            key=f"future_stage_{class_id}",
        )

        if st.session_state.get("role")=="Docente":
            # Mantiene los controles docentes con la misma organización visual del Curso 1.
            if "teacher_student_management" in globals():
                with st.expander("⚙️ Gestión de alumnos"):
                    teacher_student_management()
            with st.expander("🔒 Publicación de laboratorios"):
                client=_supabase()
                if client is not None:
                    row=_class_row(class_id)
                    published=row.get("status")=="published"
                    st.caption("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                    if st.button(
                        "Ocultar laboratorio" if published else "Publicar laboratorio",
                        key=f"future_publish_{class_id}",
                        width="stretch",
                    ):
                        client.table("classes").update({
                            "status":"draft" if published else "published","updated_at":_now()
                        }).eq("id",class_id).execute()
                        _clear_course_cache()
                        st.rerun()
            st.caption("Las evaluaciones de los alumnos se revisan en la vista ‘Evaluaciones entregadas’.")

        if st.button("Cerrar sesión",width="stretch"):
            st.session_state.clear(); st.rerun()
        st.caption("Docente: Marco Araos Barría")

    if class_id == "clase-03-impacto-instalaciones-lab-1":
        if selected == 0:
            _render_course2_lab1_welcome(lab, saved)
            return
        if selected == 1:
            _render_course2_lab1_stage1(lab, saved)
            return

    title,objective,concept,activity=lab["stages"][selected]
    stage_minutes=20 if selected not in (9,10) else 35
    header(f"ETAPA {selected} · LABORATORIO {lab['number']}",title,objective)
    st.caption(f"{lab['course']} · Fuente base: {lab['source']} · 4 horas totales")
    left,right=st.columns([1.25,.75])
    with left:
        st.markdown("### Desarrollo técnico")
        st.markdown(concept)
        if selected in (2,3,4,5,8):
            st.markdown("#### Regla de trabajo")
            if "ambiental" in lab["id"]:
                st.latex(r"L_{eq}=10\log_{10}\left(\frac{1}{T}\sum_i t_i\,10^{L_i/10}\right)")
            elif "construccion" in lab["id"]:
                st.latex(r"L_p(r_2)=L_p(r_1)-20\log_{10}(r_2/r_1)")
            elif "impacto" in lab["id"]:
                st.latex(r"L'_{nT}=L_i-10\log_{10}(T/T_0)")
            else:
                st.latex(r"D_{nT}=L_1-L_2+10\log_{10}(T/T_0)")
        st.info("Criterio profesional: registra dato, método, unidad, supuesto e interpretación. Un resultado sin trazabilidad no es verificable.")
    with right:
        st.markdown("### Mapa de decisión")
        st.markdown(f"""
        1. **Fenómeno:** {title}  
        2. **Magnitud:** elegir el indicador correcto.  
        3. **Método:** separar cálculo, medición y estimación.  
        4. **Decisión:** comparar con el criterio aplicable.  
        5. **Verificación:** definir cómo comprobar la medida.
        """)
        st.metric("Tiempo de etapa",f"{stage_minutes} min")

    st.markdown("### Actividad interactiva")
    st.write(activity)

    if st.session_state.get("role") == "Alumno":
        answer=st.text_area(
            "Desarrollo del alumno",
            value=saved.get(f"answer_{selected}",""),
            height=150,key=f"future_answer_{class_id}_{selected}",
            placeholder="Describe datos, procedimiento, resultado e interpretación.",
        )
        c1,c2,c3=st.columns(3)
        magnitude=c1.selectbox("Magnitud principal",["Seleccionar","Nivel por bandas","Índice único","Tiempo / duración","Vibración","Clase / cumplimiento"],key=f"mag_{class_id}_{selected}")
        method=c2.selectbox("Tipo de evidencia",["Seleccionar","Cálculo","Medición","Modelación","Inspección","Combinación"],key=f"method_{class_id}_{selected}")
        confidence=c3.slider("Confianza en la respuesta",1,5,3,key=f"conf_{class_id}_{selected}")
        if st.button("Guardar y completar etapa",type="primary",key=f"complete_{class_id}_{selected}"):
            if len(answer.strip())<40 or magnitude=="Seleccionar" or method=="Seleccionar":
                st.warning("Completa un desarrollo de al menos 40 caracteres y selecciona magnitud y evidencia.")
            else:
                saved.update({
                    f"answer_{selected}":answer,f"magnitude_{selected}":magnitude,
                    f"method_{selected}":method,f"confidence_{selected}":confidence,
                    f"done_{selected}":True,f"updated_{selected}":_now(),
                })
                _save_future_state(class_id,saved)
                st.success("Etapa guardada. El avance pertenece únicamente a este laboratorio.")
                st.rerun()
    elif st.session_state.get("role") == "Docente":
        with st.container(border=True):
            st.markdown("#### Evidencia esperada del alumno")
            st.markdown(
                "Identificación correcta del fenómeno; selección coherente de magnitud y método; "
                "procedimiento trazable; resultado con unidad; decisión vinculada al criterio y una medida verificable."
            )
            st.markdown("#### Orientación para retroalimentar")
            st.markdown(
                "Revisar si la respuesta distingue propiedad del elemento, desempeño en terreno, exposición y percepción. "
                "Corregir promedios aritméticos de decibeles, símbolos intercambiados y conclusiones normativas sin fuente."
            )

def future_projection_stage_impl(lab, stage):
    """Vista limpia de una etapa futura para la ventana compartida en Zoom."""
    stage = int(stage or 0)
    if stage < 0 or stage >= len(lab.get("stages", [])):
        stage = 0

    st.session_state["projection_mode"] = True
    st.session_state["role"] = "Proyección"
    st.session_state["name"] = "Pantalla de clase"

    # Curso 2 · Laboratorio 1: Etapa 0 de bienvenida y Etapa 1 vibroacústica.
    # La proyección usa estado efímero para no registrar respuestas desde Zoom.
    if lab.get("id") == "clase-03-impacto-instalaciones-lab-1":
        if stage == 0:
            _render_course2_lab1_welcome(lab, {})
            return
        if stage == 1:
            _render_course2_lab1_stage1(lab, {})
            return

    title, objective, concept, activity = lab["stages"][stage]
    stage_minutes = 20 if stage not in (9, 10) else 35
    header(f"ETAPA {stage} · LABORATORIO {lab['number']}", title, objective)
    st.markdown("### Desarrollo técnico")
    st.markdown(concept)
    if stage in (2, 3, 4, 5, 8):
        st.markdown("#### Regla de trabajo")
        if "ambiental" in lab["id"]:
            st.latex(r"L_{eq}=10\log_{10}\left(\frac{1}{T}\sum_i t_i\,10^{L_i/10}\right)")
        elif "construccion" in lab["id"]:
            st.latex(r"L_p(r_2)=L_p(r_1)-20\log_{10}(r_2/r_1)")
        elif "impacto" in lab["id"]:
            st.latex(r"L'_{nT}=L_i-10\log_{10}(T/T_0)")
        else:
            st.latex(r"D_{nT}=L_1-L_2+10\log_{10}(T/T_0)")
    st.info("Criterio profesional: registra dato, método, unidad, supuesto e interpretación.")
    st.markdown("### Actividad interactiva")
    st.write(activity)

    # Control temporal para conducción de la clase en la pantalla proyectada.
    # No persiste en base de datos.
    projection_state_key = f"projection_stage_{lab['id']}_{stage}_state"
    projection_state = st.session_state.get(projection_state_key, "Explorar")
    options = ["Explorar", "Revisar concepto", "Cerrar actividad"]
    projection_state = st.segmented_control(
        "Estado de la actividad",
        options,
        default=projection_state if projection_state in options else "Explorar",
        key=f"{projection_state_key}_control",
        label_visibility="collapsed",
    )
    if projection_state:
        st.session_state[projection_state_key] = projection_state

    if projection_state == "Revisar concepto":
        st.info(concept)
    elif projection_state == "Cerrar actividad":
        st.success("Actividad revisada en clase. Continúa con la siguiente etapa cuando corresponda.")


# Enlaces internos para que la vista futura use las implementaciones locales.
def _future_saved(class_id):
    return _future_saved_impl(class_id)

def _save_future_state(class_id, state):
    return _save_future_state_impl(class_id, state)


_VIEWS = {
    "course_dashboard": course_dashboard_impl,
    "_future_saved": _future_saved_impl,
    "_save_future_state": _save_future_state_impl,
    "future_lab_view": future_lab_view_impl,
    "future_projection_stage": future_projection_stage_impl,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
