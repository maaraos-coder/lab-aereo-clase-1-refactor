import streamlit.components.v1 as components
from pathlib import Path
import math

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

    st.markdown("### Observa el edificio")
    st.write(
        "Identifica las fuentes que pueden introducir fuerzas o vibraciones directamente en la estructura del edificio."
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
        "Una experiencia visual y aplicada para comprender cómo se genera, transmite, predice, diagnostica y controla la energía vibroacústica en edificios.",
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
        "Sigue la energía desde la fuente hasta el receptor e identifica los caminos de transmisión dentro del edificio.",
        "Explora impedancia, movilidad, resonancia, ondas de flexión y radiación para entender la respuesta de la estructura.",
        "Pasa de la molestia observada a una hipótesis física sobre la fuente y el camino de transmisión dominante.",
        "Analiza cómo la fuerza de contacto, el tipo de piso y la duración del impacto determinan la respuesta vibratoria.",
        "Calcula Lₙ,₀(f) de la losa base conectando excitación, respuesta estructural y radiación acústica.",
        "Obtén ΔLₙ(f) de un piso flotante a partir de masa, rigidez dinámica, resonancia y modelos predictivos.",
        "Combina Lₙ,₀(f) y ΔLₙ(f) para predecir el piso terminado, comparar alternativas y analizar errores de obra.",
        "Diagnostica bombas, ventiladores, tuberías y otros equipos para seleccionar medidas sobre la fuente y los caminos de transmisión.",
        "Comprueba los conceptos trabajados sobre impacto, vibraciones, predicción, instalaciones y control.",
        "Resuelve un caso completo de ruido de impacto e instalaciones mediante diagnóstico, cálculo y diseño de medidas de control.",
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
        'observación visual → mecanismo físico → diagnóstico → predicción → comparación → control → caso profesional.</div>',
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

    # --------------------------------------------------------
    # 0 · OBSERVAR
    # --------------------------------------------------------
    _course2_lab1_stage0_energy_interactive(class_id, saved)

    # --------------------------------------------------------
    # 1 · MODELO MENTAL
    # --------------------------------------------------------
    st.markdown("### 1 · Sigue la energía")
    st.write(
        "Una vez identificada la fuente, el diagnóstico consiste en seguir **cómo la energía entra al edificio, "
        "se transmite y finalmente llega al receptor**."
    )

    st.markdown(
        """
        <style>
        .energy-flow {
            display:grid;
            grid-template-columns:repeat(6,minmax(0,1fr));
            gap:.55rem;
            align-items:stretch;
            margin:.9rem 0 1rem 0;
        }
        .energy-step {
            position:relative;
            border:1px solid rgba(99,102,241,.20);
            border-radius:16px;
            background:linear-gradient(180deg,rgba(255,255,255,.98),rgba(248,250,252,.96));
            padding:.9rem .75rem .8rem;
            text-align:center;
            min-height:112px;
            box-shadow:0 5px 18px rgba(15,23,42,.06);
        }
        .energy-step:not(:last-child)::after {
            content:'→';
            position:absolute;
            right:-.46rem;
            top:50%;
            transform:translate(50%,-50%);
            z-index:3;
            width:1.55rem;
            height:1.55rem;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#fff;
            color:#4f46e5;
            font-weight:800;
            box-shadow:0 2px 8px rgba(15,23,42,.10);
        }
        .energy-kicker {
            font-size:.72rem;
            font-weight:800;
            letter-spacing:.05em;
            color:#4f46e5;
            margin-bottom:.35rem;
        }
        .energy-label {
            font-size:.98rem;
            font-weight:800;
            color:#111827;
            line-height:1.12;
        }
        .energy-sub {
            margin-top:.38rem;
            font-size:.78rem;
            line-height:1.25;
            color:#64748b;
        }
        .energy-note {
            border-radius:14px;
            padding:.78rem 1rem;
            background:linear-gradient(90deg,rgba(79,70,229,.08),rgba(14,165,233,.07));
            border:1px solid rgba(79,70,229,.14);
            color:#334155;
            margin-bottom:.8rem;
        }
        @media (max-width: 900px) {
            .energy-flow {grid-template-columns:repeat(2,minmax(0,1fr));}
            .energy-step::after {display:none !important;}
        }
        </style>
        <div class="energy-flow">
          <div class="energy-step"><div class="energy-kicker">01</div><div class="energy-label">FUENTE</div><div class="energy-sub">Equipo, impacto o actividad</div></div>
          <div class="energy-step"><div class="energy-kicker">02</div><div class="energy-label">EXCITACIÓN</div><div class="energy-sub">Fuerza o presión que entrega energía</div></div>
          <div class="energy-step"><div class="energy-kicker">03</div><div class="energy-label">RESPUESTA</div><div class="energy-sub">El elemento entra en vibración</div></div>
          <div class="energy-step"><div class="energy-kicker">04</div><div class="energy-label">PROPAGACIÓN</div><div class="energy-sub">La energía recorre estructura o aire</div></div>
          <div class="energy-step"><div class="energy-kicker">05</div><div class="energy-label">RADIACIÓN</div><div class="energy-sub">Una superficie vibrante genera sonido</div></div>
          <div class="energy-step"><div class="energy-kicker">06</div><div class="energy-label">RECEPTOR</div><div class="energy-sub">Recinto o persona donde se percibe</div></div>
        </div>
        <div class="energy-note"><b>Idea de lectura:</b> no basta con reconocer la fuente; hay que reconstruir el camino completo de la energía hasta el receptor.</div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Una misma fuente puede disponer de **varios caminos simultáneos**. "
        "El análisis vibroacústico consiste en seguirlos y determinar cuáles son relevantes en el receptor."
    )

    # --------------------------------------------------------
    # 2 · DOS FORMAS DE ENTRAR AL SISTEMA
    # --------------------------------------------------------
    st.markdown("### 2 · Dos formas de entrar al sistema")
    st.caption("Compara el camino dominante de la energía antes de entrar en modelos y ecuaciones.")

    st.markdown(
        """
        <style>
        .path-card-head {
            font-size:1.16rem; font-weight:800; color:#111827; margin:.15rem 0 .55rem 0;
        }
        .path-card-body {
            border:1px solid rgba(99,102,241,.16); border-radius:16px; padding:.85rem .95rem .9rem;
            background:linear-gradient(180deg,rgba(255,255,255,.98),rgba(248,250,252,.97));
            box-shadow:0 5px 16px rgba(15,23,42,.05); margin-top:.55rem; min-height:228px;
        }
        .path-sequence {
            display:flex; align-items:center; justify-content:center; gap:.5rem;
            margin:.35rem 0 .7rem; flex-wrap:wrap;
        }
        .path-node {
            min-width:58px; border-radius:12px; padding:.55rem .65rem; text-align:center;
            background:#fff; border:1px solid rgba(79,70,229,.18); box-shadow:0 2px 8px rgba(15,23,42,.05);
        }
        .path-symbol {font-size:1.35rem;font-weight:850;color:#4f46e5;line-height:1;}
        .path-name {font-size:.70rem;color:#64748b;margin-top:.25rem;line-height:1.1;}
        .path-arrow {font-size:1.25rem;font-weight:800;color:#94a3b8;}
        .path-explain {font-size:.91rem;line-height:1.45;color:#334155;margin:.2rem 0 .65rem;}
        .path-dominant {
            display:inline-block; border-radius:999px; padding:.34rem .7rem; font-size:.78rem; font-weight:750;
            background:rgba(79,70,229,.08); color:#4338ca; border:1px solid rgba(79,70,229,.14);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    c_air, c_struct = st.columns(2, gap="large")

    with c_air:
        st.markdown('<div class="path-card-head">Ruido aéreo</div>', unsafe_allow_html=True)
        air_path = ASSET_DIR / "curso2_lab1_etapa1_ruido_aereo.webp"
        if air_path.exists():
            st.image(air_path, width="stretch")
        st.markdown(
            """
            <div class="path-card-body">
              <div class="path-sequence">
                <div class="path-node"><div class="path-symbol">p</div><div class="path-name">presión sonora<br>incidente</div></div>
                <div class="path-arrow">→</div>
                <div class="path-node"><div class="path-symbol">v</div><div class="path-name">vibración del<br>cerramiento</div></div>
                <div class="path-arrow">→</div>
                <div class="path-node"><div class="path-symbol">p</div><div class="path-name">sonido radiado<br>al receptor</div></div>
              </div>
              <div class="path-explain">La fuente genera una <b>onda sonora en el aire</b>. Al llegar a un cerramiento, puede hacerlo vibrar; esa vibración puede generar nuevamente sonido hacia el recinto receptor.</div>
              <span class="path-dominant">Camino dominante · AIRE</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_struct:
        st.markdown('<div class="path-card-head">Ruido estructural</div>', unsafe_allow_html=True)
        struct_path = ASSET_DIR / "curso2_lab1_etapa1_ruido_estructural.webp"
        if struct_path.exists():
            st.image(struct_path, width="stretch")
        st.markdown(
            """
            <div class="path-card-body">
              <div class="path-sequence">
                <div class="path-node"><div class="path-symbol">F</div><div class="path-name">fuerza<br>aplicada</div></div>
                <div class="path-arrow">→</div>
                <div class="path-node"><div class="path-symbol">v</div><div class="path-name">vibración<br>estructural</div></div>
                <div class="path-arrow">→</div>
                <div class="path-node"><div class="path-symbol">p</div><div class="path-name">sonido radiado<br>al receptor</div></div>
              </div>
              <div class="path-explain">Una acción mecánica aplica una <b>fuerza directamente sobre la estructura</b>. La vibración se propaga por los elementos sólidos y una superficie vibrante puede radiar sonido al recinto receptor.</div>
              <span class="path-dominant">Camino dominante · ESTRUCTURA</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # 3 · PUENTE ENTRE FUERZA, VIBRACIÓN, PROPAGACIÓN Y SONIDO
    # --------------------------------------------------------
    st.markdown("### 3 · El puente entre fuerza, vibración, propagación y sonido")
    st.write(
        "Antes de analizar una pisada, necesitamos una relación sencilla que conecte "
        "**lo que excita la estructura** con **lo que finalmente escuchamos**, sin olvidar "
        "que la vibración debe propagarse por el edificio antes de llegar al recinto receptor."
    )

    bridge_html = """
<style>
.bridge-main{border:1px solid rgba(79,70,229,.16);border-radius:20px;background:linear-gradient(135deg,rgba(79,70,229,.05),rgba(14,165,233,.04));padding:1.1rem 1.2rem;margin:.7rem 0 1rem 0;text-align:center}
.bridge-chain{font-family:Georgia,"Times New Roman",serif;font-size:1.78rem;font-weight:900;color:#312e81;letter-spacing:.015em;margin-bottom:.7rem}
.bridge-meaning{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.65rem;margin-top:.7rem}
.bridge-pill{border-radius:14px;border:1px solid rgba(99,102,241,.12);background:#fff;padding:.72rem .75rem;color:#334155;font-size:.84rem;line-height:1.35}
.bridge-pill b{color:#0f172a}
.bridge-arrow{color:#94a3b8;font-weight:900}
.tool-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem;margin:.75rem 0 1rem 0}
.tool-card{border:1px solid rgba(15,23,42,.10);border-radius:18px;background:linear-gradient(180deg,#fff,#f8fafc);padding:1rem 1.05rem}
.tool-kicker{color:#64748b;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.35rem}
.tool-eq{font-family:Georgia,"Times New Roman",serif;font-size:1.55rem;font-weight:800;color:#1e3a8a;text-align:center;margin:.2rem 0 .65rem 0}
.tool-what{color:#0f172a;font-size:.88rem;font-weight:800;margin-bottom:.25rem}
.tool-text{color:#475569;font-size:.86rem;line-height:1.42}
.propagation-card{border:1px solid rgba(14,116,144,.18);border-radius:16px;background:rgba(14,116,144,.045);padding:.9rem 1rem;margin:.15rem 0 .9rem 0;color:#334155;font-size:.88rem;line-height:1.42}
.propagation-card b{color:#0f172a}
.ref-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.55rem;margin:.5rem 0 .9rem 0}
.ref-chip{border:1px solid rgba(99,102,241,.12);border-radius:12px;background:#fff;padding:.58rem .7rem;text-align:center;color:#475569;font-size:.80rem}
.ref-chip strong{color:#312e81;font-size:1rem;display:block;margin-bottom:.15rem}
.next-step{border:1px solid rgba(16,185,129,.20);border-radius:16px;background:rgba(16,185,129,.055);padding:.9rem 1rem;color:#334155;font-size:.91rem;line-height:1.42;margin:.35rem 0 1rem 0}
.next-step b{color:#065f46}
@media(max-width:900px){.bridge-meaning{grid-template-columns:repeat(2,minmax(0,1fr))}.tool-grid,.ref-row{grid-template-columns:1fr}}
@media(max-width:540px){.bridge-meaning{grid-template-columns:1fr}}
</style>

<div class="bridge-main">
    <div class="bridge-chain">F → v → propagación estructural → p</div>
    <div class="bridge-meaning">
        <div class="bridge-pill"><b>F · Fuerza</b><br>excita la estructura.</div>
        <div class="bridge-pill"><b>v · Vibración</b><br>es la respuesta mecánica.</div>
        <div class="bridge-pill"><b>Propagación</b><br>la vibración viaja por la losa y sus conexiones.</div>
        <div class="bridge-pill"><b>p · Presión sonora</b><br>una superficie vibrante puede radiar sonido al aire.</div>
    </div>
</div>

<div class="tool-grid">
    <div class="tool-card">
        <div class="tool-kicker">Herramienta 1 · de fuerza a vibración</div>
        <div class="tool-eq">v = F / Z</div>
        <div class="tool-what">¿Qué nos dice?</div>
        <div class="tool-text">
            La respuesta vibratoria depende de la fuerza aplicada y de cuánto se opone la estructura a vibrar.
            Esa oposición se representa mediante la <b>impedancia mecánica Z</b>.
        </div>
    </div>

    <div class="tool-card">
        <div class="tool-kicker">Herramienta 2 · de vibración a sonido</div>
        <div class="tool-eq">p ≈ ρ₀ · c · v</div>
        <div class="tool-what">¿Qué nos dice?</div>
        <div class="tool-text">
            Cuando la vibración llega a una superficie, esta puede transferir movimiento al aire y generar una
            variación de presión sonora. Aquí <b>ρ₀</b> representa la densidad del aire y <b>c</b> la velocidad del sonido.
        </div>
    </div>
</div>

<div class="propagation-card">
    <b>¿Y qué ocurre entre ambas relaciones?</b><br>
    La vibración no aparece directamente en el recinto receptor: primero debe <b>propagarse por la losa y por los
    elementos estructurales conectados</b>. En la siguiente parte veremos ese recorrido en una situación concreta.
</div>

<div class="ref-row">
    <div class="ref-chip"><strong>F</strong>Fuerza aplicada · N</div>
    <div class="ref-chip"><strong>Z</strong>Impedancia mecánica</div>
    <div class="ref-chip"><strong>v</strong>Velocidad de vibración · m/s</div>
    <div class="ref-chip"><strong>p</strong>Presión sonora · Pa</div>
</div>

<div class="next-step">
    <b>Ahora viene la aplicación:</b> en la Parte 4 seguiremos esta cadena completa —
    <b>F → v → propagación estructural → p</b> — en una situación concreta:
    <b>una pisada sobre una losa</b>.
</div>
"""
    st.markdown(bridge_html.replace("\n", ""), unsafe_allow_html=True)

    st.caption(
        "Modelo introductorio: estas relaciones se usan aquí para comprender la cadena física "
        "antes de incorporar efectos más complejos como frecuencia, resonancia y eficiencia de radiación."
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
                Lo que debes llevarte de esta etapa
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


def _render_course2_lab1_stage2(lab, saved):
    """Curso 2 · Lab 1 · Etapa 2: respuesta, resonancia, propagación y radiación."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")

    import numpy as np
    import matplotlib.pyplot as plt

    def _asset(name, caption=None):
        p = ASSET_DIR / name
        if p.exists():
            st.image(p, width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode", False):
            st.caption(f"[Render pendiente: {name}]")
        return False

    def _mcq(key, question, options, correct, feedback):
        st.markdown(f"#### {question}")
        ans = st.radio(
            question, options, index=None,
            key=f"{class_id}_s2_{key}",
            label_visibility="collapsed",
        )
        check_key = f"{class_id}_s2_check_{key}"
        if st.button("Comprobar", key=check_key):
            if ans is None:
                st.warning("Selecciona una alternativa.")
            else:
                st.session_state[f"{check_key}_result"] = options.index(ans) == correct
        result = st.session_state.get(f"{check_key}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.error("Aún no. " + feedback)

    header(
        "ETAPA 2 · LABORATORIO 1",
        "Excitación y respuesta estructural",
        "Por qué una misma fuerza produce respuestas distintas y cómo esa vibración se propaga y puede radiar sonido.",
        show_overview=False,
        duration_minutes=55,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.write(
        "Relacionar **fuerza, respuesta vibratoria, resonancia, modos propios, propagación estructural "
        "y radiación acústica**, de modo que en la siguiente etapa puedas diagnosticar cuál de estos "
        "mecanismos domina en una situación real."
    )

    # 1 · Entrada
    st.markdown("### 1 · Misma fuerza, distinta respuesta")
    st.write(
        "La Etapa 1 terminó con una idea clave: una fuente introduce energía en la estructura. "
        "Ahora veremos por qué **la fuerza aplicada no basta para predecir cuánto vibrará una losa**."
    )
    _asset("curso2_lab1_etapa2_misma_fuerza_distinta_respuesta.webp")
    _mcq(
        "opening",
        "Si aplicamos exactamente la misma fuerza a dos estructuras diferentes, ¿deben vibrar igual?",
        [
            "A. Sí, porque la fuerza es la misma.",
            "B. No, porque la respuesta depende de las propiedades dinámicas de cada estructura.",
            "C. Sí, si ambas son de hormigón.",
            "D. Solo depende del espesor.",
        ],
        1,
        "La fuerza es la excitación; la estructura determina su propia respuesta dinámica."
    )

    # 2 · Impedancia y movilidad
    st.markdown("### 2 · Dos formas de describir la respuesta")
    st.write(
        "Para conectar la **fuerza F** con la **velocidad vibratoria v** utilizaremos dos magnitudes equivalentes, "
        "pero con interpretaciones opuestas."
    )
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:10px 0 16px">
          <div style="border:1px solid #d8e1ec;border-radius:18px;padding:18px;background:linear-gradient(180deg,#fff,#f8fafc)">
            <div style="font-size:.78rem;font-weight:800;color:#64748b;letter-spacing:.05em">OPOSICIÓN A VIBRAR</div>
            <div style="font-size:1.25rem;font-weight:850;color:#0f172a;margin:.35rem 0">Impedancia mecánica · Z</div>
            <div style="font-family:Georgia,serif;font-size:1.45rem;color:#1e3a8a;text-align:center;margin:.7rem 0">Z = F / v</div>
            <div style="color:#475569;line-height:1.45">Una Z mayor significa que la estructura ofrece más oposición dinámica al movimiento.</div>
          </div>
          <div style="border:1px solid #d8e1ec;border-radius:18px;padding:18px;background:linear-gradient(180deg,#fff,#f8fafc)">
            <div style="font-size:.78rem;font-weight:800;color:#64748b;letter-spacing:.05em">FACILIDAD PARA VIBRAR</div>
            <div style="font-size:1.25rem;font-weight:850;color:#0f172a;margin:.35rem 0">Movilidad mecánica · Y</div>
            <div style="font-family:Georgia,serif;font-size:1.45rem;color:#1e3a8a;text-align:center;margin:.7rem 0">Y = v / F</div>
            <div style="color:#475569;line-height:1.45">Una Y mayor significa que la estructura desarrolla más velocidad vibratoria por cada unidad de fuerza.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Impedancia y movilidad **dependen de la frecuencia**. La misma estructura puede responder de forma muy distinta según cómo se la excite.")

    st.markdown("#### ¿Qué hace que la movilidad sea distinta?")
    st.write(
        "La movilidad **no aumenta porque aumentemos la fuerza**. En régimen lineal, la movilidad pertenece "
        "a la respuesta dinámica de la estructura a una frecuencia determinada."
    )
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:.55rem 0 .8rem">
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Masa</b><br><span style="color:#64748b">Influye en la inercia del sistema.</span></div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Rigidez</b><br><span style="color:#64748b">Controla cuánto se opone a deformarse.</span></div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Amortiguamiento</b><br><span style="color:#64748b">Disipa energía vibratoria.</span></div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Frecuencia</b><br><span style="color:#64748b">Puede acercar el sistema a una resonancia.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _mcq(
        "mobility_why",
        "Si dos estructuras reciben la misma fuerza, ¿qué puede hacer que una tenga mayor movilidad que la otra?",
        [
            "A. Solo la magnitud de la fuerza.",
            "B. Sus propiedades dinámicas y la frecuencia de excitación.",
            "C. Solo el área de la losa.",
            "D. La presión sonora del recinto.",
        ],
        1,
        "La movilidad depende de la estructura y de la frecuencia a la que se la excita."
    )

    st.markdown("#### Laboratorio · misma fuerza, dos estructuras")
    st.write(
        "Aquí la **fuerza es la excitación** y la **movilidad pertenece a la estructura a una frecuencia determinada**. "
        "Cambiar la fuerza modifica la velocidad vibratoria, pero no modifica por sí sola la movilidad si trabajamos en régimen lineal."
    )
    st.markdown(
        """<div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin:.4rem 0 .8rem">
        <b>Relación:</b> v(f) = Y(f) · F(f). &nbsp; La movilidad Y(f) cambia principalmente con la
        <b>estructura y la frecuencia</b>, no con la magnitud de F.
        </div>""",
        unsafe_allow_html=True,
    )

    F = st.slider("Fuerza dinámica común F (N)", 10, 500, 100, 10, key=f"{class_id}_s2_F")
    fmob = st.slider("Frecuencia de excitación para comparar Y(f) (Hz)", 20, 400, 120, 5, key=f"{class_id}_s2_fmob")

    # Curvas conceptuales de movilidad de dos estructuras distintas.
    def _mob_curve(f, base, modes):
        y = base
        for fp, amp, width in modes:
            y += amp / (1.0 + ((f - fp) / width) ** 2)
        return y

    YA_rel = _mob_curve(fmob, 0.10, [(80, 0.90, 18), (240, 0.40, 30)])
    YB_rel = _mob_curve(fmob, 0.08, [(150, 1.05, 22), (330, 0.50, 34)])
    # Escala didáctica en m/(N·s)
    YA = YA_rel * 1e-5
    YB = YB_rel * 1e-5
    vA, vB = F * YA, F * YB

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Estructura A**")
        st.metric("Movilidad Yₐ(f)", f"{YA:.2e} m/(N·s)")
        st.metric("Velocidad vₐ", f"{vA:.2e} m/s")
    with c2:
        st.markdown("**Estructura B**")
        st.metric("Movilidad Yᵦ(f)", f"{YB:.2e} m/(N·s)")
        st.metric("Velocidad vᵦ", f"{vB:.2e} m/s")

    ratio=max(vA,vB)/max(min(vA,vB),1e-15)
    which="A" if vA>vB else "B"
    st.markdown(
        f"""<div style="border-radius:14px;padding:12px 16px;background:#f0fdf4;border:1px solid #bbf7d0">
        A <b>{fmob} Hz</b>, la estructura <b>{which}</b> presenta mayor movilidad y por eso, con la misma fuerza,
        desarrolla una velocidad vibratoria aproximadamente <b>{ratio:.1f} veces</b> mayor.
        </div>""",
        unsafe_allow_html=True,
    )
    st.caption("Curvas de movilidad conceptuales para aprendizaje; no corresponden a un elemento constructivo normativo específico.")

    # 3 · Resonancia
    st.markdown("### 3 · La respuesta cambia con la frecuencia")
    st.write(
        "Una estructura no responde igual a todas las frecuencias. Cuando la excitación se aproxima a una "
        "frecuencia natural, la respuesta puede aumentar notablemente: eso es **resonancia**."
    )
    _asset("curso2_lab1_etapa2_resonancia.gif")
    st.markdown(
        """
        <div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin:.5rem 0 .9rem">
        <b>¿Qué significa “mayor respuesta”?</b><br>
        En esta etapa usamos <b>respuesta vibratoria</b> para referirnos a cuánto vibra la estructura.
        La representamos principalmente mediante la <b>velocidad vibratoria v(f)</b>. Cerca de resonancia,
        con la misma fuerza aplicada, la velocidad de vibración puede aumentar notablemente.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ¿Qué describe la ecuación dinámica?")
    st.write(
        "El modelo más simple combina tres propiedades del sistema —masa, amortiguamiento y rigidez— "
        "con una fuerza externa que cambia en el tiempo."
    )
    st.latex(r"m\ddot{x}+c\dot{x}+kx=F(t)")
    r1,r2,r3=st.columns(3)
    with r1:
        st.markdown("**m · masa**  \nInercia del sistema.")
    with r2:
        st.markdown("**c · amortiguamiento**  \nDisipa energía.")
    with r3:
        st.markdown("**k · rigidez**  \nTiende a restaurar la posición.")

    st.markdown(
        """
        <div style="border-radius:14px;padding:12px 16px;background:#f8fafc;border:1px solid #dce4ec;margin:.5rem 0 .9rem">
        <b>F(t) · fuerza externa</b><br>
        Es la excitación que actúa sobre el sistema. La vibración observada resulta del equilibrio dinámico entre
        esa fuerza y los efectos de masa, amortiguamiento y rigidez.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #d8e2ec;border-radius:18px;padding:16px 18px;background:linear-gradient(180deg,#fff,#f8fafc);margin:.6rem 0 .9rem">
        <div style="font-weight:850;color:#0f172a;font-size:1.02rem;margin-bottom:.45rem">Frecuencia natural del sistema</div>
        <div style="color:#475569;line-height:1.5">
        La <b>frecuencia natural f₀</b> es la frecuencia a la que este sistema ideal tiende naturalmente a vibrar.
        Para este modelo simple, depende principalmente de la masa <b>m</b> y de la rigidez <b>k</b>.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"f_0=\frac{1}{2\pi}\sqrt{\frac{k}{m}}")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:.4rem 0 .9rem">
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Si aumenta k</b><br><span style="color:#64748b">f₀ aumenta.</span></div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Si aumenta m</b><br><span style="color:#64748b">f₀ disminuye.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cc1,cc2,cc3 = st.columns(3)
    with cc1:
        mass=st.slider("Masa m (kg)",10.0,1000.0,150.0,10.0,key=f"{class_id}_s2_mass")
    with cc2:
        stiffness=st.slider("Rigidez k (kN/m)",10.0,5000.0,600.0,10.0,key=f"{class_id}_s2_k")
    f0=(1/(2*math.pi))*math.sqrt(stiffness*1000/mass)
    with cc3:
        fe=st.slider("Frecuencia de excitación fₑ (Hz)",1.0,100.0,min(100.0,max(1.0,f0)),0.5,key=f"{class_id}_s2_fe")
    st.caption(
        "**Frecuencia de excitación fₑ:** frecuencia con que la fuente aplica una fuerza repetitiva sobre el sistema. "
        "Se compara con la frecuencia natural f₀ para evaluar si la excitación se acerca a una condición de resonancia."
    )
    st.metric("Frecuencia natural f₀",f"{f0:.2f} Hz")
    freqs=np.linspace(1,100,400); zeta=.08
    rr=freqs/max(f0,1e-9)
    response=1/np.sqrt((1-rr**2)**2+(2*zeta*rr)**2)
    fig,ax=plt.subplots()
    ax.plot(freqs,response)
    ax.axvline(f0,linestyle="--",label="f₀")
    ax.axvline(fe,linestyle=":",label="fₑ")
    ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("Respuesta relativa")
    ax.set_title("Respuesta dinámica conceptual"); ax.grid(True,alpha=.2); ax.legend()
    st.pyplot(fig,use_container_width=True); plt.close(fig)
    if abs(fe-f0)/max(f0,1e-9)<=.1:
        st.warning("Estás excitando cerca de la frecuencia natural: la respuesta aumenta por resonancia.")
    _mcq(
        "res_energy",
        "¿La resonancia crea energía?",
        ["A. Sí.","B. No, la energía la aporta la fuente.","C. Solo cuando no hay amortiguamiento."],
        1,
        "La resonancia amplifica la respuesta del sistema frente a la energía que ya entrega la fuente."
    )

    # 4 · De una resonancia simple a los modos de una losa real
    st.markdown("### 4 · De una resonancia simple a los modos de una losa real")
    st.write(
        "En la Parte 3 usamos un sistema simple para entender una **frecuencia natural f₀** y la resonancia. "
        "Una losa real es más compleja: puede deformarse de varias maneras y, por eso, posee "
        "**varias frecuencias naturales**."
    )

    st.markdown(
        """
        <div style="border:1px solid #d8e2ec;border-radius:18px;padding:16px 18px;
                    background:linear-gradient(180deg,#fff,#f8fafc);margin:.6rem 0 .9rem">
          <div style="font-weight:850;color:#0f172a;font-size:1.02rem;margin-bottom:.45rem">
            El paso siguiente
          </div>
          <div style="color:#475569;line-height:1.5">
            En un sistema simple hablamos de una frecuencia natural principal.
            En una losa real aparecen varias:
          </div>
          <div style="font-family:Georgia,'Times New Roman',serif;font-size:1.35rem;
                      text-align:center;color:#1e3a8a;margin:.7rem 0">
            f₁, f₂, f₃, …
          </div>
          <div style="color:#475569;line-height:1.5">
            Cada una de esas frecuencias está asociada a una <b>forma particular de vibrar</b>.
            Esa forma característica se llama <b>modo propio</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:.55rem 0 .85rem">
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center">
            <b>f₁</b><br><span style="color:#64748b">→ modo 1</span>
          </div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center">
            <b>f₂</b><br><span style="color:#64748b">→ modo 2</span>
          </div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center">
            <b>f₃</b><br><span style="color:#64748b">→ modo 3</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin:.3rem 0 .85rem">
          <b>Conexión con la Parte 3:</b><br>
          La <b>resonancia</b> nos indica <b>cuándo aumenta la respuesta</b> al acercarnos a una frecuencia natural.<br>
          El <b>modo propio</b> nos muestra <b>cómo se deforma la losa</b> cuando esa frecuencia domina la respuesta.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ¿Qué es un modo propio?")
    st.write(
        "Un **modo propio** es una forma característica de vibración de la losa asociada a una frecuencia natural determinada. "
        "Si la frecuencia de excitación se acerca a esa frecuencia natural, ese patrón de vibración puede amplificarse."
    )

    st.markdown(
        """
        <div style="border:1px solid #d8e2ec;border-radius:18px;padding:16px 18px;background:#fff;margin:.55rem 0 .85rem">
          <div style="font-weight:850;color:#0f172a;font-size:1.02rem;margin-bottom:.45rem">
            ¿Cómo leer los índices (m,n)?
          </div>
          <div style="color:#475569;line-height:1.5">
            Para esta introducción, piensa en los índices como una forma sencilla de describir
            <b>cómo se divide espacialmente el patrón de vibración</b> sobre una losa rectangular.
            No indican qué tan fuerte vibra la losa.
          </div>
          <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:.7rem">
            <div style="padding:10px;border-radius:12px;background:#f8fafc;border:1px solid #e2e8f0">
              <b>(1,1)</b><br><span style="color:#64748b">1 × 1 zona principal</span>
            </div>
            <div style="padding:10px;border-radius:12px;background:#f8fafc;border:1px solid #e2e8f0">
              <b>(2,1)</b><br><span style="color:#64748b">2 × 1 zonas</span>
            </div>
            <div style="padding:10px;border-radius:12px;background:#f8fafc;border:1px solid #e2e8f0">
              <b>(2,2)</b><br><span style="color:#64748b">2 × 2 zonas</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _asset("curso2_lab1_etapa2_modos_animados.gif")

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:.5rem 0 1rem">
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Modo propio</b><br>
            <span style="color:#64748b">Patrón espacial de vibración asociado a una frecuencia natural.</span>
          </div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Nodo</b><br>
            <span style="color:#64748b">Zona del modo donde el desplazamiento es prácticamente cero.</span>
          </div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Antinodo</b><br>
            <span style="color:#64748b">Zona donde el movimiento alcanza amplitudes máximas.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border-radius:14px;padding:12px 16px;background:#f0fdf4;border:1px solid #bbf7d0;margin:.3rem 0 .85rem">
          <b>Idea clave:</b> una losa real puede resonar de distintas maneras.
          Cada frecuencia natural está asociada a un modo propio diferente.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fscan=st.slider("Explora la frecuencia (Hz)",20,500,120,5,key=f"{class_id}_s2_fscan")
    Fconst=80.0
    fs=np.linspace(20,500,700)
    peaks=[(70,1.0,13),(180,.75,20),(340,.55,28)]
    mob=np.full_like(fs,.08)
    for fp,amp,w in peaks:
        mob+=amp/(1+((fs-fp)/w)**2)
    ycur=float(np.interp(fscan,fs,mob)); vrel=Fconst*ycur

    fig,ax=plt.subplots()
    ax.plot(fs,mob)
    ax.axvline(fscan,linestyle="--")
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("|Y(f)| relativa")
    ax.set_title("Movilidad conceptual con varios modos")
    ax.grid(True,alpha=.2)
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    st.metric("Respuesta vibratoria relativa",f"{vrel:.1f} u.r.")

    nearest_mode=min([70,180,340], key=lambda ff: abs(fscan-ff))
    mode_name={
        70:"primer patrón modal",
        180:"segundo patrón modal",
        340:"tercer patrón modal"
    }[nearest_mode]

    if abs(fscan-nearest_mode) <= 25:
        st.success(
            f"Estás cerca de una frecuencia natural del modelo (~{nearest_mode} Hz). "
            f"El **{mode_name}** puede dominar la forma de vibración."
        )
    else:
        st.info(
            "Estás entre picos de respuesta. Ninguno de los modos del modelo conceptual domina claramente."
        )

    st.caption(
        "Los picos representan frecuencias naturales del modelo conceptual. "
        "Cada pico puede asociarse a una forma modal diferente."
    )

    # 5 · Propagación
    st.markdown("### 5 · La vibración no se queda donde nació")
    st.write(
        "Después de excitarse, la energía se propaga por los elementos conectados. En placas y losas, "
        "las **ondas de flexión** son especialmente importantes porque producen movimiento normal de la superficie."
    )
    _asset("curso2_lab1_etapa2_onda_flexion.gif")
    st.markdown(
        """<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.6rem 0 1rem">
        <div style="padding:14px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Velocidad vibratoria · v</b><br><span style="color:#64748b">Describe cuánto se mueve localmente el material.</span></div>
        <div style="padding:14px;border:1px solid #d9e2ec;border-radius:14px;background:#fff"><b>Velocidad de propagación</b><br><span style="color:#64748b">Describe qué tan rápido avanza la perturbación por la estructura.</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.info("No son la misma magnitud: una describe movimiento local; la otra, el avance de la energía.")

    # 6 · Espesor, masa y rigidez
    st.markdown("### 6 · ¿Qué cambia cuando hacemos una losa más gruesa?")
    st.write(
        "El espesor modifica simultáneamente la **masa superficial** y la **rigidez flexional**, "
        "pero no en la misma proporción."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.55rem 0 .9rem">
          <div style="border:1px solid #d9e2ec;border-radius:16px;padding:14px 16px;background:#fff">
            <b>Masa superficial · m′</b><br>
            <span style="color:#64748b">Cuánta masa existe por cada metro cuadrado de losa.</span>
          </div>
          <div style="border:1px solid #d9e2ec;border-radius:16px;padding:14px 16px;background:#fff">
            <b>Rigidez flexional · B</b><br>
            <span style="color:#64748b">Qué tan difícil es doblar o curvar la losa. Una B mayor significa mayor oposición a la flexión.</span>
          </div>
        </div>
        <div style="border-radius:14px;padding:12px 16px;background:#fff7ed;border:1px solid #fed7aa;margin-bottom:.8rem">
        <b>Analogía:</b> una regla delgada se dobla fácilmente; una regla del mismo material pero mucho más gruesa cuesta mucho más doblarla.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.latex(r"m'=\rho h")
    st.caption("La masa superficial crece de forma lineal con el espesor: m′ ∝ h.")

    st.latex(r"B=\frac{E h^3}{12(1-\nu^2)}")
    st.caption("La rigidez flexional crece con el cubo del espesor: B ∝ h³.")

    st.markdown(
        """
        <div style="border:1px solid #f4c58b;border-radius:18px;padding:16px 18px;background:linear-gradient(180deg,#fffaf3,#fff7ed);margin:.7rem 0 .9rem">
          <div style="font-weight:900;color:#9a3412;font-size:1.04rem;margin-bottom:.5rem">Si duplicamos el espesor</div>
          <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;text-align:center">
            <div style="padding:12px;border-radius:12px;background:#fff;border:1px solid #fed7aa"><b>Espesor</b><br><span style="font-size:1.35rem">h × 2</span></div>
            <div style="padding:12px;border-radius:12px;background:#fff;border:1px solid #fed7aa"><b>Masa superficial</b><br><span style="font-size:1.35rem">m′ × 2</span></div>
            <div style="padding:12px;border-radius:12px;background:#fff;border:1px solid #fed7aa"><b>Rigidez flexional</b><br><span style="font-size:1.35rem">B × 8</span></div>
          </div>
          <div style="margin-top:.7rem;color:#7c2d12;line-height:1.45">
          La masa aumenta en proporción directa al espesor, pero la rigidez flexional aumenta mucho más rápido porque depende de <b>h³</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    h_mm=st.slider("Espesor de hormigón h (mm)",80,250,150,5,key=f"{class_id}_s2_h")
    rho=2400.; E=30e9; nu=.20; h=h_mm/1000
    ms=rho*h; B=E*h**3/(12*(1-nu**2))

    m1,m2=st.columns(2)
    m1.metric("Masa superficial m′",f"{ms:.0f} kg/m²")
    m2.metric("Rigidez flexional B",f"{B/1e6:.2f} MN·m")

    h_ref_mm = 100
    ratio_h = h_mm / h_ref_mm
    ratio_m = ratio_h
    ratio_B = ratio_h**3

    st.markdown("#### Ahora prueba con una losa real")
    st.write(
        f"Comparamos una losa de referencia de **{h_ref_mm} mm** con la losa seleccionada de **{h_mm} mm**."
    )
    c1,c2,c3 = st.columns(3)
    c1.metric("Espesor", f"{ratio_h:.2f} ×")
    c2.metric("Masa superficial", f"{ratio_m:.2f} ×")
    c3.metric("Rigidez flexional", f"{ratio_B:.2f} ×")

    st.markdown(
        f"""
        <div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin-top:.55rem">
        Al pasar de <b>{h_ref_mm} mm</b> a <b>{h_mm} mm</b>, la masa superficial aumenta aproximadamente
        <b>{ratio_m:.2f} veces</b>, mientras que la rigidez flexional aumenta aproximadamente
        <b>{ratio_B:.2f} veces</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 7 · Dispersión de ondas de flexión
    st.markdown("### 7 · En flexión, distintas frecuencias no viajan igual")

    st.markdown("#### 1 · Primero observa el fenómeno")
    st.write(
        "Una **onda de flexión** es una deformación transversal que se desplaza por la losa. "
        "La propia superficie se curva mientras la perturbación avanza."
    )
    _asset("curso2_lab1_etapa2_dispersion_flexion.gif")

    st.markdown("#### 2 · Movimiento local y propagación no son lo mismo")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.55rem 0 .75rem">
          <div style="padding:14px;border:1px solid #d9e2ec;border-radius:16px;background:#fff">
            <b>Velocidad vibratoria · v</b><br>
            <span style="color:#64748b">
              Describe qué tan rápido se mueve <b>un punto de la losa</b> hacia arriba y abajo mientras vibra.
            </span>
          </div>
          <div style="padding:14px;border:1px solid #d9e2ec;border-radius:16px;background:#fff">
            <b>Velocidad de propagación · c<sub>B</sub></b><br>
            <span style="color:#64748b">
              Describe qué tan rápido <b>avanza la onda de flexión</b> por la losa.
            </span>
          </div>
        </div>
        <div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin-bottom:.85rem">
          <b>No son la misma velocidad.</b> Una describe el movimiento local de la superficie;
          la otra describe el avance de la perturbación por la estructura.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 3 · ¿Qué significa que la onda sea dispersiva?")
    st.write(
        "Significa que **la velocidad de propagación depende de la frecuencia**. "
        "Por eso una componente grave y una componente aguda no necesariamente avanzan de la misma manera por la losa."
    )
    st.markdown(
        """
        <div style="border:1px solid #d8e2ec;border-radius:18px;padding:14px 16px;background:#fff;margin:.55rem 0 .85rem;text-align:center">
          <div style="font-size:1.18rem;font-weight:850;color:#1e3a8a">
            frecuencia f cambia → k<sub>B</sub> cambia → c<sub>B</sub> cambia
          </div>
          <div style="margin-top:.35rem;color:#64748b">
            En ondas de flexión, cambiar la frecuencia modifica la forma espacial de la onda y su velocidad de fase.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 4 · ¿Cómo se describe matemáticamente?")
    st.write(
        "Primero obtenemos el **número de onda de flexión \(k_B\)**. "
        "Esta magnitud relaciona la frecuencia con las propiedades mecánicas de la losa."
    )
    st.latex(r"""k_B^4 = \frac{m'\,\omega^2}{B}""")

    st.markdown(
        """
        <div style="border-radius:14px;padding:12px 16px;background:#f8fafc;border:1px solid #dce4ec;margin:.4rem 0 .8rem">
          <b>¿De qué depende k<sub>B</sub>?</b><br>
          De la <b>masa superficial m′</b>, de la <b>frecuencia angular ω</b>
          y de la <b>rigidez flexional B</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "Una vez conocido \(k_B\), podemos obtener la **velocidad de fase de la onda de flexión \(c_B\)**:"
    )
    st.latex(r"""c_B = \frac{\omega}{k_B}""")

    st.markdown("#### 5 · Símbolos que aparecen en las ecuaciones")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:.5rem 0 .85rem">
          <div style="padding:10px;border:1px solid #d9e2ec;border-radius:12px;background:#fff">
            <b>m′</b><br><span style="color:#64748b">masa superficial</span>
          </div>
          <div style="padding:10px;border:1px solid #d9e2ec;border-radius:12px;background:#fff">
            <b>B</b><br><span style="color:#64748b">rigidez flexional</span>
          </div>
          <div style="padding:10px;border:1px solid #d9e2ec;border-radius:12px;background:#fff">
            <b>ω = 2πf</b><br><span style="color:#64748b">frecuencia angular</span>
          </div>
          <div style="padding:10px;border:1px solid #d9e2ec;border-radius:12px;background:#fff">
            <b>k<sub>B</sub></b><br><span style="color:#64748b">número de onda de flexión</span>
          </div>
          <div style="padding:10px;border:1px solid #d9e2ec;border-radius:12px;background:#fff">
            <b>c<sub>B</sub></b><br><span style="color:#64748b">velocidad de fase</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border-radius:16px;padding:14px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin:.3rem 0 .9rem">
          <b>Idea clave:</b> en una onda de flexión, la frecuencia influye en cómo se propaga la perturbación.
          Por eso las ondas de flexión son <b>dispersivas</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 8 · Radiación
    st.markdown("### 8 · Vibrar mucho no significa necesariamente sonar mucho")
    st.write(
        "La última transición de la cadena ocurre cuando una superficie vibrante logra transferir energía al aire. "
        "La eficiencia con que lo hace se representa mediante **σ, eficiencia de radiación**."
    )
    _asset("curso2_lab1_etapa2_vibracion_radiacion.webp")
    st.markdown(
        """
        <div style="border:1px solid #d8e2ec;border-radius:18px;padding:16px 18px;
                    background:linear-gradient(180deg,#fff,#f8fafc);margin:.55rem 0 .8rem">
          <div style="font-weight:850;color:#0f172a;font-size:1.02rem;margin-bottom:.45rem">
            ¿Qué describe esta relación?
          </div>
          <div style="color:#475569;line-height:1.5">
            Esta expresión muestra, de forma simplificada, de qué depende la
            <b>potencia acústica radiada</b> por una superficie que vibra.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.latex(r"""W_{\mathrm{rad}} \propto S\,\sigma\,v_n^2""")

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:.55rem 0 .9rem">
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>W<sub>rad</sub></b><br>
            <span style="color:#64748b">
              Potencia acústica radiada: energía acústica que la superficie entrega al aire por unidad de tiempo.
            </span>
          </div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>S</b><br>
            <span style="color:#64748b">
              Área radiante: superficie que efectivamente participa en la radiación sonora.
            </span>
          </div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>σ</b><br>
            <span style="color:#64748b">
              Eficiencia de radiación: indica qué tan eficazmente la vibración se transforma en sonido en el aire.
            </span>
          </div>
          <div style="padding:12px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>v<sub>n</sub></b><br>
            <span style="color:#64748b">
              Velocidad normal de vibración: velocidad con que la superficie se mueve perpendicularmente a su plano.
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border-radius:16px;padding:14px 16px;background:#fff7ed;
                    border:1px solid #fed7aa;margin:.3rem 0 .8rem">
          <b>Idea clave:</b> la potencia radiada aumenta con el área <b>S</b>,
          con la eficiencia de radiación <b>σ</b> y, especialmente,
          con el <b>cuadrado de la velocidad normal v<sub>n</sub></b>.
          Por eso dos superficies que vibran con la misma velocidad no necesariamente
          radian la misma potencia acústica.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### Laboratorio · ¿qué superficie radiará más sonido?")
    st.write(
        "Imagina dos superficies de un edificio que presentan la **misma velocidad normal de vibración**. "
        "Sin embargo, no tienen necesariamente la misma área radiante ni la misma eficiencia de radiación."
    )
    st.markdown(
        """<div style="border-radius:14px;padding:12px 16px;background:#eef6ff;border:1px solid #d8e8fa;margin:.4rem 0 .8rem">
        <b>Desafío:</b> antes de cambiar los controles, predice cuál superficie radiará mayor potencia acústica.
        Luego modifica <b>S</b> y <b>σ</b> y comprueba tu hipótesis.
        </div>""",
        unsafe_allow_html=True,
    )
    prediction = st.radio(
        "Predicción inicial",
        ["A radiará más", "B radiará más", "Radiarán igual"],
        index=None,
        key=f"{class_id}_s2_rad_prediction",
        horizontal=True,
    )

    vn=st.slider("Velocidad normal común vₙ (mm/s)",.1,10.0,2.0,.1,key=f"{class_id}_s2_vn")/1000
    rc1,rc2=st.columns(2)
    with rc1:
        st.markdown("**Superficie A**")
        S1=st.slider("Área radiante Sₐ (m²)",.5,30.0,8.0,.5,key=f"{class_id}_s2_S1")
        sig1=st.slider("Eficiencia de radiación σₐ",.01,1.50,.20,.01,key=f"{class_id}_s2_sig1")
        W1=S1*sig1*vn**2
        st.metric("Potencia acústica radiada relativa A",f"{W1:.3e}")
    with rc2:
        st.markdown("**Superficie B**")
        S2=st.slider("Área radiante Sᵦ (m²)",.5,30.0,8.0,.5,key=f"{class_id}_s2_S2")
        sig2=st.slider("Eficiencia de radiación σᵦ",.01,1.50,.80,.01,key=f"{class_id}_s2_sig2")
        W2=S2*sig2*vn**2
        st.metric("Potencia acústica radiada relativa B",f"{W2:.3e}")

    winner = "A radiará más" if W1>W2 else ("B radiará más" if W2>W1 else "Radiarán igual")
    if st.button("Comprobar predicción", key=f"{class_id}_s2_rad_check"):
        if prediction is None:
            st.warning("Haz primero una predicción.")
        elif prediction == winner:
            st.success("Correcto. Tu predicción coincide con el resultado del modelo.")
        else:
            st.info(f"Con los valores actuales, la respuesta es: **{winner}**.")

    st.markdown(
        f"""<div style="border-radius:14px;padding:12px 16px;background:#f0fdf4;border:1px solid #bbf7d0;margin-top:.7rem">
        <b>Conclusión:</b> aunque ambas superficies vibran con el mismo vₙ, la radiación no tiene por qué ser igual.
        En este caso, el modelo indica: <b>{winner}</b>. El área radiante S y la eficiencia σ también controlan la radiación.
        </div>""",
        unsafe_allow_html=True,
    )
    st.caption("Comparación didáctica basada en Wrad ∝ S·σ·vₙ². No representa un nivel normativo.")

    # 9 · Integración y puente a Etapa 3
    st.markdown("### 9 · La cadena que usarás para diagnosticar")
    st.write(
        "Ya puedes leer un problema vibroacústico como una cadena. En la Etapa 3 utilizarás exactamente "
        "esta lógica para decidir dónde está el mecanismo dominante."
    )
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:.7rem 0 1rem">
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center"><b>1 · FUENTE</b><br><span style="color:#64748b">Fuerza F</span></div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center"><b>2 · RESPUESTA</b><br><span style="color:#64748b">Y, Z, v</span></div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center"><b>3 · PROPAGACIÓN</b><br><span style="color:#64748b">Ondas estructurales</span></div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center"><b>4 · RADIACIÓN</b><br><span style="color:#64748b">σ, W</span></div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff;text-align:center"><b>5 · RECEPTOR</b><br><span style="color:#64748b">Nivel sonoro</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _mcq(
        "final_chain",
        "Si observas un nivel sonoro elevado en el receptor, ¿basta con concluir que la fuente está aplicando una fuerza muy grande?",
        ["A. Sí.","B. No."],
        1,
        "También pueden intervenir alta movilidad, resonancias, buenos caminos de propagación y una radiación eficiente."
    )

    st.markdown("### Cierre")
    st.success(
        "Una misma fuerza puede producir respuestas muy distintas. Ahora sabes que antes del sonido en el receptor "
        "existen etapas de **respuesta, resonancia, propagación y radiación**. En la Etapa 3 utilizaremos esta cadena "
        "para diagnosticar casos reales de impacto e instalaciones."
    )

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 1",key=f"s2_prev_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=1
            st.rerun()
    with right:
        if st.button("Etapa 3 →",key=f"s2_next_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=3
            st.rerun()


def _render_course2_lab1_stage3(lab, saved):
    """Etapa 3 · laboratorio aplicado de diagnóstico vibroacústico."""
    import math
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go

    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")

    def _persist():
        saved["stage3_updated_at"] = _now()
        fn = globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn):
            fn(class_id, saved)

    def _asset(name, caption=None):
        path = ASSET_DIR / name
        if path.exists():
            st.image(str(path), width="stretch")
            if caption:
                st.caption(caption)
            return True
        st.info(f"Asset pendiente: `{name}`")
        return False

    state = saved.get("stage3_case")
    if not isinstance(state, dict):
        state = {}
        saved["stage3_case"] = state

    header(
        "ETAPA 3 · LABORATORIO 1",
        "Aplicación: diagnostica un zumbido de origen desconocido",
        "Caso aplicado: diseña una campaña de medición, interpreta datos y reconstruye el camino vibroacústico.",
        show_overview=False,
        duration_minutes=75,
    )

    st.markdown("### Misión")
    st.write(
        "Un residente informa un **zumbido de baja frecuencia durante la noche** en su dormitorio. "
        "El ruido aparece por intervalos y, en ocasiones, también percibe una ligera vibración. "
        "**No se conoce la fuente ni el camino de transmisión.**"
    )
    st.info(
        "Tu trabajo no es adivinar la fuente. Debes formular hipótesis, decidir qué medir, seleccionar el instrumento adecuado, "
        "obtener evidencia y recién después emitir un diagnóstico."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin:.7rem 0 1rem">
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>1 · Observar</b><br><span style="color:#64748b">formular hipótesis</span></div>
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>2 · Medir</b><br><span style="color:#64748b">punto + instrumento</span></div>
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>3 · Comparar</b><br><span style="color:#64748b">frecuencias y niveles</span></div>
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>4 · Calcular</b><br><span style="color:#64748b">respuesta dinámica</span></div>
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>5 · Verificar</b><br><span style="color:#64748b">prueba causal</span></div>
          <div style="padding:10px;border:1px solid #dbe4ee;border-radius:12px;background:#fff;text-align:center"><b>6 · Diagnosticar</b><br><span style="color:#64748b">con evidencia</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # 1 · Inspección e hipótesis
    # ------------------------------------------------------------------
    st.markdown("## 1 · Inspecciona el edificio y formula hipótesis")
    st.write(
        "Observa la escena. Como el reclamo solo describe un zumbido, existen varias fuentes plausibles. "
        "Selecciona **hasta tres hipótesis iniciales**."
    )
    _asset(
        "curso2_lab1_etapa3_edificio_diagnostico.webp",
        "Edificio residencial en corte. La escena contiene varias fuentes y caminos posibles."
    )

    source_options = [
        "Bomba centrífuga en sala de máquinas",
        "Ventilador de extracción en cubierta",
        "Tubería de impulsión rígidamente conectada",
        "Descarga sanitaria",
        "Actividad de ocupantes / impactos",
    ]
    prev_sources = state.get("sources", [])
    selected_sources = st.multiselect(
        "Hipótesis iniciales",
        source_options,
        default=[x for x in prev_sources if x in source_options],
        max_selections=3,
        key=f"{class_id}_s3_sources",
    )
    if st.button("Guardar hipótesis iniciales", key=f"{class_id}_s3_save_sources"):
        if not selected_sources:
            st.warning("Selecciona al menos una hipótesis.")
        else:
            state["sources"] = selected_sources
            _persist()
            st.success("Hipótesis guardadas. Todavía no existe evidencia suficiente para elegir una causa.")

    # ------------------------------------------------------------------
    # 2 · Diseño de campaña de medición
    # ------------------------------------------------------------------
    st.markdown("## 2 · Diseña tu campaña de medición")
    st.write(
        "Dispones de tiempo limitado y puedes realizar **máximo cuatro mediciones**. "
        "En cada medición debes decidir **dónde medir, con qué instrumento y qué parámetro obtener**."
    )
    _asset(
        "curso2_lab1_etapa3_puntos_medicion.webp",
        "Los marcadores representan zonas posibles de investigación. No todos los puntos requieren el mismo instrumento."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:.5rem 0 .9rem">
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Acelerómetro</b><br><span style="color:#64748b">Mide aceleración de una superficie vibrante y permite obtener su espectro.</span>
          </div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Sensor de velocidad vibratoria</b><br><span style="color:#64748b">Mide velocidad RMS de vibración en elementos sólidos.</span>
          </div>
          <div style="padding:13px;border:1px solid #d9e2ec;border-radius:14px;background:#fff">
            <b>Sonómetro / micrófono</b><br><span style="color:#64748b">Mide presión sonora en el aire y su contenido espectral.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    points = [
        "Carcasa de la bomba",
        "Apoyo de la bomba sobre la losa",
        "Tubería de impulsión",
        "Muro / shaft técnico",
        "Cielo del dormitorio receptor",
        "Aire del dormitorio receptor",
        "Ventilador de cubierta",
    ]
    instruments = [
        "Acelerómetro",
        "Sensor de velocidad vibratoria",
        "Sonómetro / micrófono",
    ]
    parameters_by_instrument = {
        "Acelerómetro": [
            "Aceleración RMS (m/s²)",
            "Espectro de aceleración / frecuencia dominante (Hz)",
        ],
        "Sensor de velocidad vibratoria": [
            "Velocidad vibratoria RMS (mm/s)",
            "Espectro de velocidad / frecuencia dominante (Hz)",
        ],
        "Sonómetro / micrófono": [
            "Nivel de presión sonora Lp (dB)",
            "Espectro acústico / frecuencia dominante (Hz)",
        ],
    }
    valid_medium = {
        "Carcasa de la bomba": "estructura",
        "Apoyo de la bomba sobre la losa": "estructura",
        "Tubería de impulsión": "estructura",
        "Muro / shaft técnico": "estructura",
        "Cielo del dormitorio receptor": "estructura",
        "Aire del dormitorio receptor": "aire",
        "Ventilador de cubierta": "estructura",
    }

    plans = []
    for i in range(4):
        st.markdown(f"**Medición {i+1}**")
        c1,c2,c3 = st.columns(3)
        with c1:
            p = st.selectbox(
                "Punto",
                ["— No usar —"] + points,
                key=f"{class_id}_s3_plan_point_{i}",
            )
        with c2:
            inst = st.selectbox(
                "Instrumento",
                ["— Selecciona —"] + instruments,
                key=f"{class_id}_s3_plan_inst_{i}",
            )
        with c3:
            pars = parameters_by_instrument.get(inst, [])
            par = st.selectbox(
                "Parámetro",
                ["— Selecciona —"] + pars,
                key=f"{class_id}_s3_plan_param_{i}",
            )
        if p != "— No usar —":
            plans.append((p, inst, par))

    st.caption(
        "Ejemplo: para conocer la vibración del cielo necesitas un sensor sobre el cielo; "
        "para caracterizar lo que escucha el residente necesitas un sonómetro en el aire del dormitorio."
    )

    # Simulated measurement database
    measurement_db = {
        "Carcasa de la bomba": {
            "Aceleración RMS (m/s²)": "0,86 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "25 Hz",
            "Velocidad vibratoria RMS (mm/s)": "1,35 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "25 Hz",
        },
        "Apoyo de la bomba sobre la losa": {
            "Aceleración RMS (m/s²)": "0,69 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "25 Hz",
            "Velocidad vibratoria RMS (mm/s)": "1,10 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "25 Hz",
        },
        "Tubería de impulsión": {
            "Aceleración RMS (m/s²)": "0,62 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "25 Hz",
            "Velocidad vibratoria RMS (mm/s)": "0,92 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "25 Hz",
        },
        "Muro / shaft técnico": {
            "Aceleración RMS (m/s²)": "0,31 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "25 Hz",
            "Velocidad vibratoria RMS (mm/s)": "0,48 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "25 Hz",
        },
        "Cielo del dormitorio receptor": {
            "Aceleración RMS (m/s²)": "0,45 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "25 Hz",
            "Velocidad vibratoria RMS (mm/s)": "0,71 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "25 Hz",
        },
        "Aire del dormitorio receptor": {
            "Nivel de presión sonora Lp (dB)": "48 dB",
            "Espectro acústico / frecuencia dominante (Hz)": "25 Hz",
        },
        "Ventilador de cubierta": {
            "Aceleración RMS (m/s²)": "0,38 m/s²",
            "Espectro de aceleración / frecuencia dominante (Hz)": "47 Hz",
            "Velocidad vibratoria RMS (mm/s)": "0,55 mm/s",
            "Espectro de velocidad / frecuencia dominante (Hz)": "47 Hz",
        },
    }

    if st.button("Validar y realizar campaña", type="primary", key=f"{class_id}_s3_measure"):
        if len(plans) < 2:
            st.warning("Realiza al menos dos mediciones para poder comparar evidencia.")
        else:
            errors = []
            used_points = []
            for p,inst,par in plans:
                if inst == "— Selecciona —" or par == "— Selecciona —":
                    errors.append(f"{p}: falta seleccionar instrumento o parámetro.")
                    continue
                medium = valid_medium[p]
                if medium == "aire" and inst != "Sonómetro / micrófono":
                    errors.append(f"{p}: el aire del dormitorio debe caracterizarse acústicamente con sonómetro/micrófono.")
                if medium == "estructura" and inst == "Sonómetro / micrófono":
                    errors.append(f"{p}: para medir la vibración del elemento debes usar acelerómetro o sensor de velocidad.")
                if p in used_points:
                    errors.append(f"{p}: repetiste el mismo punto.")
                used_points.append(p)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                state["measurement_plan"] = plans
                state["measured"] = True
                _persist()
                st.rerun()

    if state.get("measured"):
        rows = []
        for p,inst,par in state.get("measurement_plan", []):
            result = measurement_db.get(p, {}).get(par, "Sin resultado")
            rows.append({
                "Punto": p,
                "Instrumento": inst,
                "Parámetro": par,
                "Resultado": result,
            })

        title_col, reset_col = st.columns([4, 1])
        with title_col:
            st.markdown("#### Resultados obtenidos")
        with reset_col:
            if st.button(
                "Resetear mediciones",
                key=f"{class_id}_s3_reset_measurements",
                use_container_width=True,
            ):
                # Borra resultados persistidos de la campaña.
                state.pop("measurement_plan", None)
                state.pop("measured", None)

                # Limpia también los widgets de planificación para que
                # el alumno pueda comenzar una campaña completamente nueva.
                for i in range(4):
                    for suffix in ("point", "inst", "param"):
                        st.session_state.pop(f"{class_id}_s3_plan_{suffix}_{i}", None)

                _persist()
                st.rerun()

        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        st.info(
            "Una coincidencia de frecuencia entre varios puntos puede sugerir un camino de transmisión, "
            "pero la causalidad debe verificarse con una prueba adicional."
        )

    # ------------------------------------------------------------------
    # 3 · Comparación espectral
    # ------------------------------------------------------------------
    st.markdown("## 3 · Compara posibles fuentes con el receptor")
    st.write(
        "Ahora compara **espectros acústicos** medidos cerca de dos fuentes candidatas con el sonido medido en el dormitorio. "
        "En los tres casos se representa el **nivel de presión sonora por frecuencia, Lp (dB)**. "
        "El objetivo es detectar coincidencias que orienten el diagnóstico, sin confundirlas todavía con una prueba causal."
    )

    # Frecuencias discretas: posiciones numéricas uniformes para aprovechar todo
    # el ancho del gráfico y etiquetas de frecuencia independientes.
    freq_labels = ["10", "16", "20", "25", "31,5", "40", "50", "63", "80", "100"]
    xpos = list(range(len(freq_labels)))

    # Niveles de presión sonora simulados y físicamente intuitivos (dB).
    # Bomba y dormitorio comparten el máximo dominante en 25 Hz.
    # El ventilador presenta su máximo principal en 50 Hz.
    pump = [39, 43, 52, 72, 55, 48, 46, 42, 38, 35]
    fan  = [36, 38, 41, 43, 45, 50, 68, 54, 43, 38]
    rec  = [34, 37, 46, 62, 51, 46, 44, 40, 36, 33]

    fig = go.Figure()

    # Banda visual de 25 Hz.
    fig.add_vrect(
        x0=2.62, x1=3.38,
        fillcolor="rgba(37,99,235,0.10)",
        line_width=0,
        layer="below",
    )

    fig.add_trace(go.Scatter(
        x=xpos, y=pump,
        mode="lines+markers",
        name="Bomba · medición acústica cercana",
        line=dict(width=3),
        marker=dict(size=[8,8,8,12,8,8,8,8,8,8]),
        hovertemplate="Bomba<br>%{customdata} Hz<br>Lp = %{y:.0f} dB<extra></extra>",
        customdata=freq_labels,
    ))
    fig.add_trace(go.Scatter(
        x=xpos, y=fan,
        mode="lines+markers",
        name="Ventilador · medición acústica cercana",
        line=dict(width=2),
        marker=dict(size=[8,8,8,8,8,8,12,8,8,8]),
        hovertemplate="Ventilador<br>%{customdata} Hz<br>Lp = %{y:.0f} dB<extra></extra>",
        customdata=freq_labels,
    ))
    fig.add_trace(go.Scatter(
        x=xpos, y=rec,
        mode="lines+markers",
        name="Dormitorio receptor",
        line=dict(width=3, dash="dash"),
        marker=dict(size=[8,8,8,12,8,8,8,8,8,8]),
        hovertemplate="Dormitorio<br>%{customdata} Hz<br>Lp = %{y:.0f} dB<extra></extra>",
        customdata=freq_labels,
    ))

    fig.add_annotation(
        x=3, y=72,
        text="<b>25 Hz</b><br>coincidencia dominante<br>bomba ↔ dormitorio",
        showarrow=True,
        arrowhead=2,
        ax=75, ay=-58,
        bgcolor="rgba(255,255,255,0.96)",
        bordercolor="#cbd5e1",
        borderwidth=1,
    )
    fig.add_annotation(
        x=6, y=68,
        text="<b>50 Hz</b><br>máximo principal<br>del ventilador",
        showarrow=True,
        arrowhead=2,
        ax=55, ay=-52,
        bgcolor="rgba(255,255,255,0.96)",
        bordercolor="#cbd5e1",
        borderwidth=1,
    )

    fig.update_layout(
        height=470,
        margin=dict(l=65, r=25, t=82, b=65),
        xaxis=dict(
            title=dict(text="Frecuencia (Hz)", font=dict(size=14)),
            range=[-0.35, len(freq_labels)-0.65],
            tickmode="array",
            tickvals=xpos,
            ticktext=freq_labels,
            tickangle=0,
            tickfont=dict(size=13),
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Nivel de presión sonora por banda, Lp (dB)", font=dict(size=14)),
            range=[25, 80],
            dtick=5,
            tickfont=dict(size=13),
            gridcolor="rgba(148,163,184,0.22)",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.07,
            xanchor="left",
            x=0,
            font=dict(size=12),
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{class_id}_s3_spectra")

    st.markdown(
        """
        <div style="border:1px solid #dbeafe;background:#eff6ff;border-radius:14px;padding:13px 16px;margin:.2rem 0 .9rem">
          <b>Lectura del gráfico:</b> la medición acústica cercana a la bomba presenta su máximo en
          <b>25 Hz (72 dB)</b> y el dormitorio receptor también muestra su componente principal en
          <b>25 Hz (62 dB)</b>. El ventilador, en cambio, tiene su máximo alrededor de
          <b>50 Hz (68 dB)</b>. La coincidencia de frecuencia fortalece la hipótesis de la bomba,
          pero todavía no demuestra por sí sola el camino de transmisión ni la causalidad.
        </div>
        """,
        unsafe_allow_html=True,
    )

    interp = st.selectbox(
        "¿Qué hipótesis queda mejor respaldada por esta comparación?",
        [
            "— Selecciona —",
            "La bomba es una fuente candidata fuerte porque comparte el componente dominante de 25 Hz con el dormitorio.",
            "El ventilador es necesariamente la causa porque está en la cubierta.",
            "La coincidencia espectral demuestra por sí sola el camino completo.",
        ],
        key=f"{class_id}_s3_interp",
    )
    if st.button("Guardar interpretación espectral", key=f"{class_id}_s3_interp_check"):
        ok = interp.startswith("La bomba es una fuente candidata fuerte")
        state["spectral_evidence"] = bool(ok)
        _persist()
        if ok:
            st.success("Bien. La bomba pasa a ser una hipótesis fuerte, pero todavía debemos demostrar el camino y la causalidad.")
        else:
            st.warning("Busca la coincidencia dominante entre la fuente candidata y el dormitorio, sin confundir correlación con prueba causal.")

    # ------------------------------------------------------------------
    # 4 · Comparación de caminos mediante movilidad
    # ------------------------------------------------------------------
    st.markdown("## 4 · Compara dos caminos estructurales candidatos")
    st.write(
        "La comparación espectral orienta hacia la bomba, pero ahora necesitamos saber **por dónde podría transmitirse con mayor facilidad su vibración**. "
        "Usa lo aprendido en la Etapa 2: para una misma fuerza dinámica, un camino con mayor movilidad desarrolla mayor velocidad vibratoria."
    )
    st.latex(r"v(f)=Y(f)\,F(f)")

    st.markdown(
        """
        <div style="border:1px solid #e2e8f0;border-radius:14px;padding:12px 15px;background:#fff;margin:.3rem 0 .8rem">
          <b>Pregunta de diagnóstico:</b> si la bomba aplica la misma fuerza a sus conexiones, ¿qué camino tendría mayor capacidad de transmitir vibración hacia el edificio?
        </div>
        """,
        unsafe_allow_html=True,
    )

    F = st.number_input(
        "Fuerza dinámica común de la bomba F (N)",
        20.0, 500.0, 120.0, 10.0,
        key=f"{class_id}_s3_F"
    )

    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### Camino A · apoyo → losa")
        st.caption("Transmisión desde el apoyo de la bomba hacia la losa de la sala de máquinas.")
        YA_u = st.number_input(
            "Movilidad Yₐ (×10⁻⁶ m/(N·s))",
            0.1, 20.0, 3.0, 0.1,
            key=f"{class_id}_s3_YA"
        )
        vA = F * YA_u * 1e-6
        st.metric("Velocidad vibratoria estimada vₐ", f"{vA*1000:.3f} mm/s")

    with cb:
        st.markdown("#### Camino B · tubería → shaft/muro")
        st.caption("Transmisión por la tubería rígidamente conectada y sus uniones con el edificio.")
        YB_u = st.number_input(
            "Movilidad Yᵦ (×10⁻⁶ m/(N·s))",
            0.1, 20.0, 8.0, 0.1,
            key=f"{class_id}_s3_YB"
        )
        vB = F * YB_u * 1e-6
        st.metric("Velocidad vibratoria estimada vᵦ", f"{vB*1000:.3f} mm/s")

    if vA > 0:
        ratio = vB / vA
        st.info(
            f"Con estos valores, el camino B desarrolla aproximadamente **{ratio:.1f} veces** la velocidad vibratoria del camino A. "
            "Esto no demuestra todavía que sea el camino dominante, pero permite priorizarlo para contrastarlo con las mediciones."
        )

    predicted_path = st.radio(
        "Antes de comprobar: ¿qué camino esperas que presente mayor respuesta vibratoria?",
        ["Camino A · apoyo → losa", "Camino B · tubería → shaft/muro", "Serán iguales"],
        index=None,
        key=f"{class_id}_s3_path_prediction",
    )

    if st.button("Comparar cálculo con la evidencia", key=f"{class_id}_s3_dyn_check"):
        correct = (vB > vA and predicted_path == "Camino B · tubería → shaft/muro") or (vA > vB and predicted_path == "Camino A · apoyo → losa") or (abs(vA-vB) < 1e-12 and predicted_path == "Serán iguales")
        state["dynamic_response"] = True
        state["calc_vA_mm_s"] = float(vA*1000)
        state["calc_vB_mm_s"] = float(vB*1000)
        state["dynamic_prediction_ok"] = bool(correct)
        _persist()
        if correct:
            st.success(
                "La predicción coincide con el cálculo. Ahora compara esta tendencia con las mediciones estructurales para decidir si el camino candidato también está respaldado experimentalmente."
            )
        else:
            st.warning(
                "Revisa la relación v = Y·F: como la fuerza es la misma en ambos candidatos, la mayor movilidad produce la mayor velocidad vibratoria."
            )

    # ------------------------------------------------------------------
    # 5 · Resonancia
    # ------------------------------------------------------------------
    st.markdown("## 5 · ¿Puede existir amplificación dinámica?")
    st.write(
        "La componente dominante de la bomba es 25 Hz. Una medición/estimación modal del elemento estructural indica una frecuencia natural cercana a 24 Hz."
    )
    fe = 25.0
    fn = 24.0
    zeta = 0.08
    fs = np.linspace(5,60,400)
    r = fs/fn
    resp = 1/np.sqrt((1-r**2)**2+(2*zeta*r)**2)
    rf = go.Figure()
    rf.add_trace(go.Scatter(x=fs,y=resp,mode="lines",name="Respuesta relativa"))
    rf.add_vline(x=fn,line_dash="dash",annotation_text="fₙ = 24 Hz")
    rf.add_vline(x=fe,line_dash="dot",annotation_text="fₑ = 25 Hz")
    rf.update_layout(height=330,xaxis_title="Frecuencia (Hz)",yaxis_title="Respuesta relativa",margin=dict(l=30,r=20,t=25,b=35))
    st.plotly_chart(rf,use_container_width=True,key=f"{class_id}_s3_resonance")
    st.info(
        "La proximidad entre la frecuencia de excitación de la fuente y una frecuencia natural del elemento "
        "puede aumentar la respuesta vibratoria sin que aumente la fuerza aplicada."
    )
    if st.button("Registrar posible resonancia", key=f"{class_id}_s3_res_check"):
        state["resonance"] = True
        _persist()
        st.success("Hipótesis de amplificación dinámica registrada.")

    # ------------------------------------------------------------------
    # 6 · Reconstrucción de camino
    # ------------------------------------------------------------------
    st.markdown("## 6 · Reconstruye el camino de transmisión")
    st.write(
        "Con la evidencia disponible, construye el camino físico más probable desde la bomba hasta el dormitorio."
    )
    lists = [
        ["— Selecciona —","Bomba centrífuga","Ventilador","Descarga sanitaria"],
        ["— Selecciona —","Fuerza dinámica en apoyos / tuberías","Presión sonora aérea","Impacto de pisada"],
        ["— Selecciona —","Vibración de apoyos y tubería","Movimiento del aire exterior","Movimiento del agua únicamente"],
        ["— Selecciona —","Losa / shaft / uniones estructurales","Aire exterior","Ventana"],
        ["— Selecciona —","Cielo o muro del dormitorio","Bomba","Ventilador"],
        ["— Selecciona —","Aire del dormitorio receptor","Sala de máquinas","Cubierta"],
    ]
    labels = ["Fuente","Excitación","Respuesta","Propagación","Superficie radiante","Receptor"]
    vals=[]
    cols=st.columns(3)
    for i,(labx,opts) in enumerate(zip(labels,lists)):
        with cols[i%3]:
            vals.append(st.selectbox(labx,opts,key=f"{class_id}_s3_path_{i}"))
    expected = [
        "Bomba centrífuga",
        "Fuerza dinámica en apoyos / tuberías",
        "Vibración de apoyos y tubería",
        "Losa / shaft / uniones estructurales",
        "Cielo o muro del dormitorio",
        "Aire del dormitorio receptor",
    ]
    if st.button("Comprobar camino",key=f"{class_id}_s3_path_check"):
        hits=sum(a==b for a,b in zip(vals,expected))
        state["path_hits"]=hits
        state["path_ok"]=hits==len(expected)
        _persist()
        if hits==len(expected):
            st.success("Camino físicamente coherente. Ahora falta una prueba que fortalezca la causalidad.")
        else:
            st.warning(f"Hay {hits} de {len(expected)} pasos coherentes. Revisa cómo entra la energía y por dónde llega al dormitorio.")

    # ------------------------------------------------------------------
    # 7 · Prueba causal
    # ------------------------------------------------------------------
    st.markdown("## 7 · Elige una prueba de confirmación")
    st.write(
        "La coincidencia a 25 Hz y el camino estructural son evidencia importante, pero todavía necesitamos una prueba que relacione directamente la fuente con el efecto."
    )
    tests = [
        "Detener temporalmente la bomba y medir simultáneamente vibración en el camino y nivel sonoro en el dormitorio.",
        "Medir una sola vez el nivel sonoro del dormitorio.",
        "Agregar material absorbente al dormitorio sin verificar la fuente.",
        "Medir solo la temperatura de la sala de máquinas.",
    ]
    test = st.radio("Prueba propuesta",tests,index=None,key=f"{class_id}_s3_test")
    if st.button("Simular prueba",key=f"{class_id}_s3_test_run"):
        ok = test == tests[0]
        state["confirmation"] = bool(ok)
        _persist()
        if ok:
            st.success(
                "Resultado simulado: al detener la bomba, disminuye fuertemente el componente de 25 Hz en el apoyo, tubería, cielo y dormitorio. "
                "Al volver a operar, reaparece. La evidencia causal es fuerte."
            )
        elif test:
            st.warning("La prueba seleccionada entrega evidencia insuficiente para confirmar la causalidad.")
        else:
            st.warning("Selecciona una prueba.")

    # ------------------------------------------------------------------
    # 8 · Diagnóstico final
    # ------------------------------------------------------------------
    st.markdown("## 8 · Emite tu diagnóstico")
    st.write("Integra la campaña de medición, el espectro, el cálculo dinámico, el camino y la prueba de confirmación.")

    d1,d2,d3 = st.columns(3)
    with d1:
        final_source = st.selectbox(
            "Fuente probable",
            ["— Selecciona —","Bomba centrífuga","Ventilador de cubierta","Descarga sanitaria"],
            key=f"{class_id}_s3_final_source",
        )
    with d2:
        final_path = st.selectbox(
            "Camino dominante",
            ["— Selecciona —","Apoyos / tuberías → estructura → dormitorio","Solo aire","Ventana exterior"],
            key=f"{class_id}_s3_final_path",
        )
    with d3:
        final_rad = st.selectbox(
            "Superficie radiante",
            ["— Selecciona —","Cielo / muro del dormitorio","Bomba","Ventilador"],
            key=f"{class_id}_s3_final_rad",
        )

    justification = st.text_area(
        "Justificación técnica",
        value=state.get("justification",""),
        placeholder="Explica qué mediciones realizaste, qué magnitudes observaste, qué frecuencia coincidió y qué prueba confirmó la hipótesis.",
        key=f"{class_id}_s3_justification",
    )

    if st.button("Comprobar y guardar diagnóstico",type="primary",key=f"{class_id}_s3_final_check"):
        score=0
        score += 15 if state.get("measured") else 0
        score += 15 if state.get("spectral_evidence") else 0
        score += 15 if state.get("dynamic_response") else 0
        score += 10 if state.get("resonance") else 0
        score += 20 if state.get("path_ok") else int(state.get("path_hits",0))*3
        score += 15 if state.get("confirmation") else 0
        score += 4 if final_source=="Bomba centrífuga" else 0
        score += 3 if final_path=="Apoyos / tuberías → estructura → dormitorio" else 0
        score += 3 if final_rad=="Cielo / muro del dormitorio" else 0
        if justification.strip():
            score=min(100,score+5)

        state.update({
            "final_source":final_source,
            "final_path":final_path,
            "final_radiator":final_rad,
            "justification":justification,
            "score":int(score),
            "completed":score>=70 and bool(justification.strip()),
        })
        if state["completed"]:
            saved["done_3"]=True
        _persist()
        st.rerun()

    if state.get("score") is not None:
        st.metric("Resultado formativo del diagnóstico",f"{state['score']}/100")
        if state.get("completed"):
            st.success("Diagnóstico suficientemente sustentado. La etapa queda completada.")
        else:
            st.warning("Aún faltan evidencias o pasos del proceso de diagnóstico.")

    # ------------------------------------------------------------------
    # Vista docente
    # ------------------------------------------------------------------
    if role == "Docente":
        st.markdown("---")
        st.markdown("## Vista docente · desarrollo esperado")
        st.markdown("### Reclamo")
        st.write(
            "Zumbido nocturno de baja frecuencia en dormitorio, de aparición intermitente y origen inicialmente desconocido."
        )
        st.markdown("### Fuente y camino esperados")
        st.write(
            "La hipótesis principal es la bomba centrífuga. Su componente dominante de 25 Hz se transmite por apoyos y/o tuberías "
            "hacia elementos estructurales conectados; una superficie del dormitorio (cielo o muro) radia finalmente sonido al aire receptor."
        )
        st.markdown("### Estrategia de medición")
        st.write(
            "Debe combinar mediciones estructurales y acústicas: acelerómetro o sensor de velocidad sobre bomba/apoyos/tubería/cielo, "
            "y sonómetro o micrófono para medir Lp y espectro en el aire del dormitorio."
        )
        st.markdown("### Magnitudes")
        st.write(
            "Estructura: aceleración RMS, velocidad vibratoria RMS y espectros. "
            "Aire receptor: nivel de presión sonora Lp y espectro acústico. "
            "No deben mezclarse las unidades ni tratar todos los puntos como si midieran la misma magnitud."
        )
        st.markdown("### Evidencia")
        st.write(
            "Coincidencia espectral a 25 Hz en bomba, camino estructural y dormitorio; respuesta dinámica compatible; "
            "y prueba de detención de bomba que reduce/desaparece el componente dominante."
        )
        st.markdown("### Diagnóstico")
        st.write(
            "Bomba centrífuga → fuerza dinámica en apoyos/tuberías → vibración estructural → propagación por conexiones → "
            "radiación desde cielo/muro del dormitorio → presión sonora en el receptor."
        )

    st.markdown("---")
    nav1,nav2=st.columns(2)
    with nav1:
        if st.button("← Etapa 2",key=f"{class_id}_s3_prev",use_container_width=True):
            st.session_state[stage_selector_key]=2
            st.rerun()
    with nav2:
        if st.button("Etapa 4 →",key=f"{class_id}_s3_next",use_container_width=True):
            st.session_state[stage_selector_key]=4
            st.rerun()


def _render_course2_lab1_stage4(lab, saved):
    """Curso 2 · Lab 1 · Etapa 4: puente físico hacia la predicción del ruido de impacto."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")
    ns = f"{class_id}_s4"

    import numpy as np
    import matplotlib.pyplot as plt

    def _asset(name, caption=None):
        path = ASSET_DIR / name
        if path.exists():
            st.image(str(path), width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode", False):
            st.caption(f"[Asset pendiente: {name}]")
        return False

    def _persist():
        saved["updated_4"] = _now()
        fn = globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn):
            fn(class_id, saved)

    def _concept(title, body):
        st.markdown(
            f"""<div style="border:1px solid #dbe4ee;border-radius:14px;padding:14px 16px;
            background:#f8fbff;margin:.5rem 0 .9rem">
            <div style="font-weight:800;color:#0f172a;margin-bottom:5px">{title}</div>
            <div style="color:#475569;line-height:1.5">{body}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    header(
        "ETAPA 4 · LABORATORIO 1",
        "Física del ruido de impacto",
        "Puente hacia la predicción del nivel de ruido de impacto de la losa base.",
        show_overview=False,
        duration_minutes=65,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.write(
        "Comprender qué hace especial a una excitación de impacto y reconocer las variables físicas "
        "que necesitaremos en la Etapa 5 para predecir el nivel de ruido de impacto de una losa base."
    )
    st.latex(
        r"\boxed{F(t)\rightarrow F(f)\rightarrow Y(f)\rightarrow v(f)\rightarrow "
        r"W_{\mathrm{rad}}(f)\rightarrow L_n(f)}"
    )
    st.info(
        "En esta etapa **no calcularemos todavía Lₙ(f)**. Prepararemos cada eslabón físico para que "
        "la predicción de la Etapa 5 tenga sentido."
    )

    # ------------------------------------------------------------------
    # 1 · IMPACTO
    # ------------------------------------------------------------------
    st.markdown("## 1 · ¿Qué ocurre durante un impacto?")
    _asset(
        "curso2_lab1_etapa4_impacto_fuerza.gif",
        "Animación conceptual: la fuerza aparece, alcanza un máximo y desaparece durante el contacto."
    )
    st.write(
        "Un impacto no es una fuerza constante. La interacción entre el elemento que golpea y el piso "
        "produce una **fuerza variable en el tiempo**."
    )
    st.latex(r"F=F(t)")
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("Magnitud", "Fmáx")
    with c2:
        st.metric("Duración", "Δt")
    with c3:
        st.metric("Forma temporal", "F(t)")
    _concept(
        "Idea clave",
        "Dos impactos con una carga estática semejante pueden excitar de manera muy distinta al piso "
        "si cambia la duración o la rigidez del contacto."
    )

    # ------------------------------------------------------------------
    # 2 · TIME -> FREQUENCY
    # ------------------------------------------------------------------
    st.markdown("## 2 · Del tiempo a la frecuencia")
    st.write(
        "La duración del contacto modifica el contenido frecuencial de la excitación. "
        "Esta relación será una de las entradas físicas del modelo predictivo."
    )
    _asset("curso2_lab1_etapa4_tiempo_frecuencia.gif")

    _concept(
        "Qué significa físicamente",
        "Un contacto corto obliga a la fuerza a cambiar muy rápido y, por ello, aparecen componentes en un rango amplio de frecuencias. "
        "Cuando el contacto dura más, la fuerza cambia más lentamente y disminuye el contenido relativo de frecuencias altas. "
        "Esto no significa que desaparezcan las bajas frecuencias ni que cambie necesariamente la energía total."
    )

    dt_ms = st.slider(
        "Duración de contacto Δt (ms)",
        min_value=1.0,
        max_value=30.0,
        value=5.0,
        step=0.5,
        key=f"{ns}_dt",
    )

    # Pulso gaussiano normalizado solo con finalidad didáctica.
    t = np.linspace(-0.06, 0.06, 1600)
    sigma_t = max((dt_ms/1000.0)/2.355,1e-5)
    force = np.exp(-0.5*(t/sigma_t)**2)
    force /= max(force.max(),1e-12)
    freqs=np.fft.rfftfreq(len(t),d=t[1]-t[0])
    spec=np.abs(np.fft.rfft(force))
    spec/=max(spec.max(),1e-12)
    valid=freqs<=2000

    ct,cf=st.columns(2)
    with ct:
        fig,ax=plt.subplots(figsize=(6,3.4))
        ax.plot(t*1000,force)
        ax.set_xlabel("Tiempo (ms)")
        ax.set_ylabel("F(t) normalizada")
        ax.set_title("Fuerza en el tiempo")
        ax.grid(True,alpha=.2)
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)
    with cf:
        fig,ax=plt.subplots(figsize=(6,3.4))
        ax.plot(freqs[valid],spec[valid])
        ax.set_xlabel("Frecuencia (Hz)")
        ax.set_ylabel("|F(f)| normalizada")
        ax.set_title("Contenido frecuencial")
        ax.grid(True,alpha=.2)
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)

    if dt_ms <= 6:
        st.success("Contacto corto: la fuerza cambia muy rápido, por lo que el impacto contiene componentes en un rango más amplio de frecuencias, incluyendo frecuencias altas.")
    elif dt_ms >= 16:
        st.info("Contacto más largo: la fuerza cambia más lentamente y disminuye el contenido relativo de frecuencias altas.")
    else:
        st.info("Duración intermedia → transición entre ambos comportamientos.")

    # ------------------------------------------------------------------
    # 3 · FLOOR PARTICIPATES
    # ------------------------------------------------------------------
    st.markdown("## 3 · El piso también participa")
    st.write(
        "La excitación por impacto no puede separarse completamente de la estructura que recibe el golpe. "
        "El piso tiene una respuesta dinámica propia."
    )
    st.latex(r"\boxed{Y(f)=\frac{v(f)}{F(f)}}")
    st.latex(r"\boxed{v(f)=Y(f)\,F(f)}")
    st.caption("Y(f): movilidad · v(f): velocidad vibratoria · F(f): fuerza de excitación.")
    _asset(
        "curso2_lab1_etapa4_dos_pisos.gif",
        "Misma excitación conceptual; distinta movilidad → distinta respuesta vibratoria."
    )
    _concept(
        "Conexión con la Etapa 2",
        "Ya aprendiste qué es la movilidad. Aquí la usamos específicamente para comprender "
        "por qué un impacto puede producir respuestas distintas en dos pisos."
    )

    # ------------------------------------------------------------------
    # 4 · SAME IMPACT, TWO FLOORS
    # ------------------------------------------------------------------
    st.markdown("## 4 · Laboratorio: mismo impacto, dos pisos")
    st.write(
        "Compara dos estructuras sometidas a la misma excitación conceptual. "
        "El objetivo no es decidir cuál piso es 'mejor' en general, sino observar cómo cambia v(f)."
    )

    profiles={
        "Losa de hormigón 200 mm": {"base":0.18,"p1":170,"a1":0.18,"p2":510,"a2":0.11},
        "Losa de hormigón 120 mm": {"base":0.24,"p1":150,"a1":0.28,"p2":470,"a2":0.17},
        "Piso liviano entramado": {"base":0.34,"p1":110,"a1":0.52,"p2":350,"a2":0.36},
    }
    ca,cb=st.columns(2)
    with ca:
        floor_a=st.selectbox("Piso A",list(profiles),index=0,key=f"{ns}_floor_a")
    with cb:
        floor_b=st.selectbox("Piso B",list(profiles),index=2,key=f"{ns}_floor_b")

    f=np.linspace(20,800,700)
    force_f=np.exp(-f/620)

    def mobility(cfg):
        return (
            cfg["base"]
            +cfg["a1"]*np.exp(-0.5*((f-cfg["p1"])/55)**2)
            +cfg["a2"]*np.exp(-0.5*((f-cfg["p2"])/95)**2)
        )

    YA=mobility(profiles[floor_a]); YB=mobility(profiles[floor_b])
    vA=YA*force_f; vB=YB*force_f

    tab1,tab2,tab3=st.tabs(["F(f) · excitación","Y(f) · movilidad","v(f) · respuesta"])

    with tab1:
        st.markdown(
            """
            <div style="border:1px solid #dbe4ee;border-radius:14px;padding:13px 16px;background:#f8fbff;margin:.2rem 0 .7rem">
              <b>¿Qué muestra este gráfico?</b><br>
              Representa <b>qué frecuencias contiene la fuerza de impacto</b>.<br><br>
              <b>Eje X:</b> frecuencia (Hz).<br>
              <b>Eje Y:</b> magnitud relativa de la fuerza.<br><br>
              En esta comparación usamos la <b>misma F(f) para ambos pisos</b>, de modo que cualquier diferencia posterior
              se deba a la respuesta de la estructura.
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig,ax=plt.subplots(figsize=(8,3.6))
        ax.plot(f,force_f)
        ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("|F(f)| relativa")
        ax.set_title("Excitación común para ambos pisos"); ax.grid(True,alpha=.2)
        st.pyplot(fig,use_container_width=True); plt.close(fig)

    with tab2:
        st.markdown(
            """
            <div style="border:1px solid #dbe4ee;border-radius:14px;padding:13px 16px;background:#f8fbff;margin:.2rem 0 .7rem">
              <b>¿Qué muestra este gráfico?</b><br>
              La movilidad indica <b>qué tan fácilmente vibra cada piso</b> cuando recibe una fuerza a cada frecuencia.<br><br>
              <b>Mayor Y(f)</b> → mayor velocidad vibratoria ante la misma fuerza.<br>
              <b>Menor Y(f)</b> → mayor oposición dinámica.<br><br>
              Los máximos de la curva señalan frecuencias donde la estructura responde con mayor facilidad.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.latex(r"Y(f)=\frac{v(f)}{F(f)}")
        fig,ax=plt.subplots(figsize=(8,3.6))
        ax.plot(f,YA,label="Piso A")
        ax.plot(f,YB,label="Piso B")
        ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("Y(f) relativa")
        ax.set_title("Movilidad de los dos pisos"); ax.grid(True,alpha=.2); ax.legend()
        st.pyplot(fig,use_container_width=True); plt.close(fig)

    with tab3:
        st.markdown(
            """
            <div style="border:1px solid #dbe4ee;border-radius:14px;padding:13px 16px;background:#f8fbff;margin:.2rem 0 .7rem">
              <b>¿Qué muestra este gráfico?</b><br>
              Es la <b>respuesta vibratoria resultante</b> luego de combinar la fuerza de impacto con la movilidad del piso.<br><br>
              Una curva más alta significa que ese piso desarrolla <b>mayor velocidad vibratoria</b> en esa frecuencia.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.latex(r"v(f)=Y(f)\,F(f)")
        fig,ax=plt.subplots(figsize=(8,3.6))
        ax.plot(f,vA,label="Piso A")
        ax.plot(f,vB,label="Piso B")
        ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("v(f) relativa")
        ax.set_title("Respuesta vibratoria resultante"); ax.grid(True,alpha=.2); ax.legend()
        st.pyplot(fig,use_container_width=True); plt.close(fig)

    st.markdown(
        """
        <div style="border:1px solid #bfdbfe;background:#eff6ff;border-radius:14px;padding:13px 16px;margin:.7rem 0 1rem">
          <b>Cómo leer los tres gráficos juntos</b><br>
          Primero observamos <b>qué frecuencias contiene el impacto F(f)</b>; luego,
          <b>cómo responde cada piso Y(f)</b>; y finalmente obtenemos
          <b>cuánto vibra cada piso v(f)</b>.<br><br>
          <div style="text-align:center;font-weight:800;color:#1e3a8a">
            Impacto F(f) + respuesta del piso Y(f) → vibración v(f)
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_eval=st.slider("Frecuencia para comparar (Hz)",50,700,160,10,key=f"{ns}_f_eval")
    ia=int(np.argmin(np.abs(f-f_eval)))
    ratio=float(vB[ia]/max(vA[ia],1e-9))

    st.markdown(f"#### Comparación a {f_eval} Hz")
    ma,mb,mc=st.columns(3)
    with ma:
        st.markdown(
            f"""
            <div style="border:1px solid #dbe4ee;border-radius:16px;padding:16px;background:#fff;min-height:205px;height:auto;box-sizing:border-box;margin-bottom:10px">
              <div style="font-weight:800;color:#0f172a">Movilidad del Piso A</div>
              <div style="font-size:1.75rem;font-weight:800;margin:.35rem 0">{YA[ia]:.3f} u.r.</div>
              <div style="color:#64748b;line-height:1.4">
                Indica qué tan fácilmente responde el Piso A ante una fuerza aplicada a {f_eval} Hz.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mb:
        relation_b = "mayor" if YB[ia] > YA[ia] else "menor"
        st.markdown(
            f"""
            <div style="border:1px solid #dbe4ee;border-radius:16px;padding:16px;background:#fff;min-height:205px;height:auto;box-sizing:border-box;margin-bottom:10px">
              <div style="font-weight:800;color:#0f172a">Movilidad del Piso B</div>
              <div style="font-size:1.75rem;font-weight:800;margin:.35rem 0">{YB[ia]:.3f} u.r.</div>
              <div style="color:#64748b;line-height:1.4">
                A {f_eval} Hz, su movilidad es <b>{relation_b}</b> que la del Piso A.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mc:
        st.markdown(
            f"""
            <div style="border:1px solid #bfdbfe;border-radius:16px;padding:16px;background:#eff6ff;min-height:205px;height:auto;box-sizing:border-box;margin-bottom:10px">
              <div style="font-weight:800;color:#0f172a">Comparación de vibración</div>
              <div style="font-size:1.75rem;font-weight:800;margin:.35rem 0">{ratio:.2f} veces</div>
              <div style="color:#475569;line-height:1.4">
                Con la misma excitación, el Piso B alcanza una velocidad vibratoria
                de aproximadamente <b>{ratio:.2f} veces</b> la del Piso A.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if ratio > 1.05:
        st.info(
            f"A {f_eval} Hz ambos pisos reciben la misma F(f), pero el Piso B tiene mayor movilidad. "
            f"Por eso su respuesta vibratoria es aproximadamente {ratio:.2f} veces la del Piso A."
        )
    elif ratio < 0.95:
        st.info(
            f"A {f_eval} Hz ambos pisos reciben la misma F(f), pero el Piso A presenta mayor respuesta vibratoria."
        )
    else:
        st.info(
            f"A {f_eval} Hz las respuestas de ambos pisos son muy similares para esta excitación conceptual."
        )

    pred=st.radio(
        f"Con la misma fuerza de impacto a {f_eval} Hz, ¿qué piso vibrará más?",
        ["Piso A","Piso B","Prácticamente iguales"],
        index=None,
        horizontal=True,
        key=f"{ns}_floor_prediction",
    )
    if st.button("Comprobar comparación",key=f"{ns}_floor_check"):
        if abs(vA[ia]-vB[ia])/max(vA[ia],vB[ia],1e-9)<0.05:
            correct="Prácticamente iguales"
        else:
            correct="Piso A" if vA[ia]>vB[ia] else "Piso B"
        if pred==correct:
            st.success("Correcto. La respuesta cambia porque Y(f) cambia, aun usando la misma excitación conceptual.")
        elif pred is None:
            st.warning("Selecciona una predicción.")
        else:
            st.warning("Revisa v(f)=Y(f)F(f) en la frecuencia seleccionada.")

    # ------------------------------------------------------------------
    # 5 · POSITION
    # ------------------------------------------------------------------
    st.markdown("## 5 · La posición del impacto también importa")
    st.write(
        "En un piso real la movilidad puede variar espacialmente. "
        "Por eso la posición del impacto puede cambiar la respuesta."
    )
    st.latex(r"Y=Y(f,x,y)")

    pos=st.segmented_control(
        "Explora la posición",
        ["S1 · Sobre apoyo/nervio","S2 · Entre apoyos","S3 · Cerca del borde"],
        default="S1 · Sobre apoyo/nervio",
        key=f"{ns}_position",
    )
    cfg={
        "S1 · Sobre apoyo/nervio":("BAJA",0.58,215),
        "S2 · Entre apoyos":("ALTA",1.25,145),
        "S3 · Cerca del borde":("MEDIA",0.88,180),
    }
    lev,amp,fp=cfg[pos]
    fpos=np.linspace(20,500,500)
    ypos=0.12+amp/(1+((fpos-fp)/42)**2)
    st.metric("Movilidad local relativa",lev)
    fig,ax=plt.subplots(figsize=(8,3.5))
    ax.plot(fpos,ypos)
    ax.axvline(fp,linestyle="--",alpha=.5)
    ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("Y(f) relativa")
    ax.set_title(f"Respuesta conceptual · {pos}"); ax.grid(True,alpha=.2)
    st.pyplot(fig,use_container_width=True); plt.close(fig)
    _concept(
        "Qué debes llevar a la Etapa 5",
        "Una predicción requiere definir cómo representaremos la respuesta de la losa. "
        "La estructura no responde igual en todas las frecuencias ni necesariamente en todos los puntos."
    )

    # ------------------------------------------------------------------
    # 6 · RADIATION
    # ------------------------------------------------------------------
    st.markdown("## 6 · De vibración a sonido")
    _asset(
        "curso2_lab1_etapa4_radiacion.gif",
        "La velocidad normal de la losa moviliza el aire del recinto receptor."
    )
    st.write(
        "Conocer v(f) todavía no entrega directamente Lₙ. "
        "Debemos estimar cuánto de esa vibración se transforma en potencia acústica."
    )
    st.latex(r"W_{\mathrm{rad}}=\rho_0c_0S\sigma\,v_n^2")

    r1,r2,r3=st.columns(3)
    with r1:
        vn_um=st.slider("Velocidad normal vₙ (µm/s)",0.1,20.0,4.0,0.1,key=f"{ns}_vn")
    with r2:
        area=st.slider("Área radiante S (m²)",5.0,80.0,30.0,1.0,key=f"{ns}_area")
    with r3:
        sigma=st.slider("Eficiencia de radiación σ",0.05,1.0,0.35,0.05,key=f"{ns}_sigma")

    rho0=1.2; c0=343.0; vn=vn_um*1e-6
    Wrad=rho0*c0*area*sigma*vn**2
    Lw=10*np.log10(max(Wrad,1e-20)/1e-12)
    rr1,rr2=st.columns(2)
    with rr1:
        st.metric("Potencia sonora radiada",f"{Wrad:.2e} W")
    with rr2:
        st.metric("Nivel de potencia relativo a 1 pW",f"{Lw:.1f} dB")
    st.caption(
        "Laboratorio conceptual: el objetivo es observar tendencias. "
        "La predicción de Lₙ de la Etapa 5 utilizará un modelo específico para la losa base."
    )

    # ------------------------------------------------------------------
    # 7 · BUILD THE CHAIN / BRIDGE TO STAGE 5
    # ------------------------------------------------------------------
    st.markdown("## 7 · Construye la cadena que usaremos en la predicción")
    st.write(
        "Ordena conceptualmente los eslabones físicos. La salida de uno se convierte en la entrada del siguiente."
    )

    options=[
        "— Selecciona —",
        "F(t) · Fuerza en el tiempo",
        "F(f) · Espectro de fuerza",
        "Y(f) · Movilidad del piso",
        "v(f) · Velocidad vibratoria",
        "Wrad(f) · Potencia acústica radiada",
        "Ln(f) · Nivel de ruido de impacto",
    ]
    expected=options[1:]
    selections=[]
    cols=st.columns(3)
    for i in range(6):
        with cols[i%3]:
            selections.append(
                st.selectbox(
                    f"Paso {i+1}",
                    options,
                    index=0,
                    key=f"{ns}_chain_{i}",
                )
            )

    if st.button("Comprobar cadena",type="primary",key=f"{ns}_chain_check"):
        hits=sum(a==b for a,b in zip(selections,expected))
        saved["stage4_chain_hits"]=hits
        saved["stage4_bridge_ready"]=hits==6
        _persist()
        if hits==6:
            st.success("Cadena completa. Ya tienes preparado el mapa físico que utilizará la predicción de la Etapa 5.")
        else:
            st.warning(f"{hits} de 6 pasos están en la posición correcta. Sigue la transformación: tiempo → frecuencia → estructura → vibración → radiación → nivel.")

    st.markdown("### Antes de pasar a la Etapa 5")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown("**Excitación**")
        st.latex(r"F(f)")
    with c2:
        st.markdown("**Respuesta de la losa**")
        st.latex(r"Y(f)")
    with c3:
        st.markdown("**Vibración**")
        st.latex(r"v(f)")
    with c4:
        st.markdown("**Radiación**")
        st.latex(r"W_{\mathrm{rad}}(f)")

    st.success(
        "**Puente a la Etapa 5:** en la siguiente etapa aplicaremos estas relaciones a una **losa base definida** "
        "para obtener la predicción de su **nivel de ruido de impacto Lₙ(f)**. "
        "Recién después podremos estudiar cuánto mejora una solución constructiva respecto de esa base."
    )

    if role=="Docente" and not projection_mode:
        st.markdown("---")
        st.markdown("## Vista docente · desarrollo esperado")
        st.write(
            "La Etapa 4 debe funcionar como puente físico hacia la predicción. "
            "No se busca todavía obtener Lₙ(f), sino asegurar que el estudiante comprenda la cadena "
            "F(t) → F(f) → Y(f) → v(f) → Wrad(f) → Lₙ(f)."
        )
        st.write(
            "**Puntos críticos:** impacto corto extiende el contenido relativo hacia altas frecuencias; "
            "la movilidad correcta es Y=v/F; la misma excitación puede producir respuestas distintas; "
            "la posición modifica Y(f,x,y); y la vibración necesita un modelo de radiación antes de transformarse en resultado acústico."
        )

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 3",key=f"s4_prev_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=3
            st.rerun()
    with right:
        if st.button("Etapa 5 · Predecir losa base →",key=f"s4_next_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=5
            st.rerun()

def _render_course2_lab1_stage5(lab, saved):
    """Etapa 5 · Predicción guiada y banda a banda de L_n,0(f) para la losa base."""
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    from core.acoustics import critical_frequency
    from core.course2_impact_models import (
        ver_impact_velocity_before_contact,
        ver_impact_force_harmonic,
        ver_force_spectral_density,
        ver_ln_piecewise_db,
    )

    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role","Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role=="Proyección")
    ns=f"{class_id}_s5"

    def _asset(name, caption=None):
        p=ASSET_DIR/name
        if p.exists():
            st.image(str(p),width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode",False):
            st.caption(f"[Asset pendiente: {name}]")
        return False

    def _persist():
        saved["updated_5"]=_now()
        fn=globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn):
            fn(class_id,saved)

    def _card(title,value,text,tone="white"):
        bg="#fff" if tone=="white" else "#eff6ff"
        bd="#dbe4ee" if tone=="white" else "#bfdbfe"
        st.markdown(
            f"""<div style="border:1px solid {bd};border-radius:16px;padding:15px 16px;
            background:{bg};min-height:170px;box-sizing:border-box;margin-bottom:6px">
              <div style="font-weight:800;color:#0f172a">{title}</div>
              <div style="font-size:1.6rem;font-weight:850;color:#0f172a;margin:.35rem 0">{value}</div>
              <div style="color:#64748b;line-height:1.45">{text}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    def _mass_law_R(f_hz, m_surface):
        # Aproximación didáctica de ley de masa para una placa homogénea.
        # Se usa para cerrar el laboratorio sin pedir R(f) como dato arbitrario.
        val=20.0*math.log10(max(float(m_surface)*float(f_hz),1e-12))-47.0
        return max(5.0,float(val))

    def _sigma_estimate(f_hz, fc_hz):
        # Aproximación pedagógica dependiente de f/fc:
        # bajo fc crece progresivamente; sobre fc se aproxima a 1.
        r=max(float(f_hz)/max(float(fc_hz),1e-9),1e-6)
        if r < 1.0:
            return max(0.05,min(0.98,math.sqrt(r)))
        return 1.0

    def _band_solution(f_hz, m_surface, fc_hz, eta):
        R=_mass_law_R(f_hz,m_surface)
        sigma=_sigma_estimate(f_hz,fc_hz)
        ln,regime=ver_ln_piecewise_db(float(f_hz),float(R),float(fc_hz),float(sigma),float(eta),0.0)
        return float(R),float(sigma),float(ln),regime

    header(
        "ETAPA 5 · LABORATORIO 1",
        "Predicción del nivel de ruido de impacto de la losa base",
        "Construye banda por banda la curva de referencia Lₙ,₀(f).",
        show_overview=False,
        duration_minutes=90,
    )

    st.markdown("### De la física de la Etapa 4 a una predicción")
    st.write(
        "En la etapa anterior construimos la cadena física. Ahora la convertiremos en una predicción "
        "para una **losa de hormigón desnuda**, que será la referencia de las soluciones posteriores."
    )

    st.markdown("### Mapa de variables que usaremos")
    top_cols = st.columns(5)
    with top_cols[0]:
        with st.container(border=True):
            st.markdown("**Fuente**")
            st.latex(r"F(f)")
            st.caption("Excitación mecánica en frecuencia.")
    with top_cols[1]:
        with st.container(border=True):
            st.markdown("**Losa**")
            st.latex(r"m',\;D,\;\eta_p")
            st.caption("Propiedades dinámicas de la placa.")
    with top_cols[2]:
        with st.container(border=True):
            st.markdown("**Radiación**")
            st.latex(r"f_c,\;\sigma_{\mathrm{rad}}")
            st.caption("Cambio de régimen y eficiencia radiativa.")
    with top_cols[3]:
        with st.container(border=True):
            st.markdown("**Régimen**")
            st.latex(r"f<f_c\quad \mathrm{o}\quad f\geq f_c")
            st.caption("Define qué ecuación de Vér corresponde.")
    with top_cols[4]:
        with st.container(border=True):
            st.markdown("**Predicción**")
            st.latex(r"L_{n,0}(f)")
            st.caption("Nivel de impacto de la losa base.")
    st.info(
        "La etapa termina cuando hayas calculado y registrado correctamente cada banda. "
        "El gráfico se construirá únicamente con tus resultados validados."
    )

    # ==============================================================
    # 1. LOSA BASE
    # ==============================================================
    st.markdown("## 1 · Define la losa base")
    st.write(
        "Estos parámetros describen la placa que vamos a modelar. "
        "No hay tratamiento resiliente: ésta es la condición de referencia."
    )
    c1,c2=st.columns(2)
    with c1:
        rho_p=st.number_input("Densidad ρₚ (kg/m³)",1500.0,3000.0,2400.0,50.0,key=f"{ns}_rho")
        t_mm=st.number_input("Espesor t (mm)",80.0,350.0,160.0,5.0,key=f"{ns}_t")
        eta=st.number_input("Factor de pérdidas ηₚ",0.001,0.100,0.020,0.001,format="%.3f",key=f"{ns}_eta")
    with c2:
        E=st.number_input("Módulo de Young E (GPa)",10.0,60.0,30.0,1.0,key=f"{ns}_E")
        nu=st.number_input("Coeficiente de Poisson ν",0.05,0.49,0.20,0.01,format="%.2f",key=f"{ns}_nu")
        st.markdown(
            """<div style="border:1px solid #dbe4ee;border-radius:14px;padding:13px 15px;background:#f8fbff;margin-top:8px">
            <b>Qué estamos definiendo</b><br>
            Una placa homogénea de hormigón. A partir de estos datos obtendremos masa superficial,
            rigidez flexional y frecuencia crítica.
            </div>""",
            unsafe_allow_html=True,
        )

    try:
        m_surface,D,fc=critical_frequency(rho_p,t_mm,E,nu,343.0)
    except Exception as exc:
        m_surface,D,fc=None,None,None
        st.error(f"No fue posible calcular la losa: {exc}")

    if fc:
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            _card("Masa superficial m′",f"{m_surface:.1f} kg/m²","Cuánta masa tiene la losa por cada metro cuadrado.")
        with cc2:
            _card("Rigidez flexional D",f"{D:.2e} N·m","Qué tan difícil es curvar la placa; depende fuertemente del espesor.")
        with cc3:
            _card("Frecuencia crítica f_c",f"{fc:.0f} Hz","Frecuencia que separa dos regímenes de radiación del modelo.",tone="blue")

    # ==============================================================
    # 2. FUENTE NORMALIZADA
    # ==============================================================
    st.markdown("## 2 · ¿Por qué necesitamos caracterizar la máquina de impactos?")
    st.write(
        "Porque toda predicción necesita una **entrada mecánica conocida y repetible**. "
        "La máquina normalizada proporciona esa excitación de referencia; no estamos estudiando la máquina como objetivo final."
    )
    _asset(
        "curso2_lab1_etapa5_maquina_impactos.gif",
        "La animación muestra la caída, la velocidad antes del impacto y el contacto con la losa."
    )

    st.markdown("### ¿Qué datos de la fuente necesita el modelo?")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:.45rem 0 .85rem">
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:145px">
            <b>h · Altura de caída</b><br>
            <span style="color:#64748b">Define la energía potencial antes de caer.</span>
          </div>
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:145px">
            <b>v₀ · Velocidad de impacto</b><br>
            <span style="color:#64748b">Velocidad del martillo inmediatamente antes del contacto.</span>
          </div>
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:145px">
            <b>fᵣ · Repetición</b><br>
            <span style="color:#64748b">Cantidad de impactos que se repiten por segundo.</span>
          </div>
          <div style="padding:14px;border:1px solid #bfdbfe;border-radius:14px;background:#eff6ff;min-height:145px">
            <b>S_f0 · Excitación espectral</b><br>
            <span style="color:#475569">Representación de la entrada mecánica que luego utilizará el modelo de predicción.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style="border:1px solid #bfdbfe;background:#eff6ff;border-radius:14px;padding:13px 16px;margin:.3rem 0 .8rem">
        <b>En una frase:</b> caracterizamos la máquina únicamente para definir <b>qué excitación mecánica recibe la losa</b>.
        A partir de esa entrada, el modelo estima el nivel de ruido de impacto.
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Configuración normalizada de referencia")
    st.write(
        "Para la predicción oficial del laboratorio usamos una **máquina de impactos de referencia**. "
        "Los parámetros siguientes describen cómo se genera la excitación mecánica y no representan una elección libre de diseño."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:.5rem 0 .8rem">
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:155px">
            <b>fᵣ · Frecuencia de repetición</b><br>
            <span style="color:#64748b">Indica cuántos impactos se producen por segundo. En la configuración de referencia usamos <b>10 Hz</b>.</span>
          </div>
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:155px">
            <b>m · Masa del martillo</b><br>
            <span style="color:#64748b">Masa del elemento que golpea la losa. En esta referencia usamos <b>0,50 kg</b>.</span>
          </div>
          <div style="padding:14px;border:1px solid #dbe4ee;border-radius:14px;background:#fff;min-height:155px">
            <b>h · Altura de caída</b><br>
            <span style="color:#64748b">Distancia desde la cual cae el martillo antes del contacto. En esta referencia usamos <b>0,040 m</b> (40 mm).</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #bfdbfe;background:#eff6ff;border-radius:14px;padding:13px 16px;margin:.3rem 0 .8rem">
          <b>¿Para qué sirven estos tres datos?</b><br>
          A partir de <b>m</b> y <b>h</b> obtenemos la velocidad antes del impacto <b>v₀</b>.
          Al incorporar la repetición <b>fᵣ</b>, el modelo puede caracterizar la excitación periódica que recibe la losa.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.latex(r"v_0=\sqrt{2gh}")
    st.latex(r"F_n=2f_rmv_0")
    st.latex(r"S_{f0}=4f_rm^2gh")

    source_mode = st.radio(
        "Modo de la fuente",
        ["Usar máquina normalizada de referencia", "Explorar variaciones de la fuente"],
        index=0,
        horizontal=True,
        key=f"{ns}_source_mode",
    )

    if source_mode == "Usar máquina normalizada de referencia":
        fr = 10.0
        mass = 0.50
        h = 0.040

        s1,s2,s3=st.columns(3)
        with s1:
            _card("fᵣ · Repetición",f"{fr:.2f} Hz","Valor de referencia utilizado para la predicción oficial.")
        with s2:
            _card("m · Masa",f"{mass:.2f} kg","Masa de referencia del martillo.")
        with s3:
            _card("h · Altura de caída",f"{h:.3f} m","Equivale a 40 mm de caída.",tone="blue")
    else:
        st.info(
            "Modo exploratorio: puedes modificar la fuente para observar tendencias. "
            "Estos cambios **no sustituyen** la configuración normalizada usada para el baseline oficial."
        )
        s1,s2,s3=st.columns(3)
        with s1:
            fr=st.number_input("Repetición fᵣ (Hz)",0.1,30.0,10.0,0.5,key=f"{ns}_fr")
        with s2:
            mass=st.number_input("Masa del martillo m (kg)",0.05,2.0,0.50,0.05,key=f"{ns}_mass")
        with s3:
            h=st.number_input("Altura de caída h (m)",0.005,0.200,0.040,0.005,format="%.3f",key=f"{ns}_h")

    try:
        v0=ver_impact_velocity_before_contact(9.81,h)
        Fn=ver_impact_force_harmonic(fr,mass,v0)
        Sf0=ver_force_spectral_density(fr,mass,9.81,h)

        st.markdown("### Resultado de la caracterización de la fuente")
        a1,a2,a3=st.columns(3)
        with a1:
            _card(
                "Velocidad antes del impacto v₀",
                f"{v0:.3f} m/s",
                "Velocidad del martillo inmediatamente antes del contacto."
            )
        with a2:
            _card(
                "Fuerza periódica característica Fₙ",
                f"{Fn:.2f} N",
                "Magnitud asociada a la excitación repetitiva de la fuente."
            )
        with a3:
            _card(
                "Densidad espectral de fuerza S_f0",
                f"{Sf0:.2f} N²/Hz",
                "Describe la intensidad de la excitación mecánica distribuida por unidad de frecuencia. "
                "No es una fuerza instantánea en newtons.",
                tone="blue"
            )
    except Exception as exc:
        st.warning(str(exc))

    st.caption(
        "Vér & Beranek, *Noise and Vibration Control Engineering*, 2nd ed., cap. 11, §11.11, "
        "Ecs. (11.158)–(11.160)."
    )

    # ==============================================================
    # 3. FRECUENCIA CRÍTICA — DETALLADO
    # ==============================================================
    st.markdown("## 3 · Entiende la frecuencia crítica antes de calcular")
    st.write(
        "La frecuencia crítica no es simplemente una frontera matemática. "
        "Indica un cambio en la relación entre la **onda de flexión de la losa** y la **radiación hacia el aire**."
    )
    _asset(
        "curso2_lab1_etapa5_cambio_regimen.gif",
        "La misma losa puede encontrarse bajo, cerca o sobre su frecuencia crítica según la banda que estemos analizando."
    )

    st.markdown("### ¿Qué representa físicamente la frecuencia crítica?")
    st.write(
        "Piensa en la losa como una superficie que vibra e intenta mover el aire del recinto. "
        "La vibración de la losa se propaga mediante **ondas de flexión**, mientras que el sonido se propaga en el aire. "
        "La frecuencia crítica aparece cuando ambas formas de propagación alcanzan una condición de acoplamiento especialmente eficiente."
    )

    st.markdown(
        """
        <div style="border:1px solid #dbe4ee;border-radius:15px;padding:14px 16px;background:#fff;margin:.4rem 0 .8rem">
          <b>En palabras simples:</b><br>
          por debajo de la frecuencia crítica, la losa puede vibrar sin radiar sonido de manera especialmente eficiente.
          Al acercarnos a <b>f_c</b>, el acoplamiento entre la vibración de la placa y el aire mejora.
          Por encima de <b>f_c</b>, el comportamiento radiativo cambia y el modelo utiliza otro régimen de predicción.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 3.1 · ¿De dónde sale f_c?")
    st.latex(r"m'=\rho_p\,t")
    st.latex(r"D=\frac{Et^3}{12(1-\nu^2)}")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:.5rem 0 .9rem">
          <div style="padding:13px;border:1px solid #dbe4ee;border-radius:14px;background:#fff"><b>m′ · masa superficial</b><br><span style="color:#64748b">Aumenta con densidad y espesor.</span></div>
          <div style="padding:13px;border:1px solid #dbe4ee;border-radius:14px;background:#fff"><b>D · rigidez flexional</b><br><span style="color:#64748b">Aumenta aproximadamente con t³.</span></div>
          <div style="padding:13px;border:1px solid #bfdbfe;border-radius:14px;background:#eff6ff"><b>f_c · frecuencia crítica</b><br><span style="color:#475569">Resulta de la relación entre masa y rigidez de la placa.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 3.2 · ¿Qué cambia al acercarnos y cruzar la frecuencia crítica?")
    st.write(
        "La losa no cambia de material ni deja de vibrar. Lo que cambia es **qué tan eficientemente esa vibración puede transformarse en sonido radiado**."
    )

    csub, ccrit, csup = st.columns(3)
    with csub:
        st.markdown(
            """
            <div style="border:1px solid #bfdbfe;border-radius:16px;padding:15px;background:#eff6ff;min-height:245px">
              <div style="font-weight:850;color:#1d4ed8">1 · BAJO f_c</div>
              <div style="font-size:1.25rem;font-weight:850;margin:.35rem 0">f &lt; f_c</div>
              <div style="color:#475569;line-height:1.5">
                La placa puede vibrar, pero el acoplamiento con el aire es menos eficiente.
                En este régimen el modelo conserva explícitamente
                <b>ηₚ</b>, <b>f_c</b> y <b>σrad</b>.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ccrit:
        st.markdown(
            """
            <div style="border:1px solid #fde68a;border-radius:16px;padding:15px;background:#fffbeb;min-height:245px">
              <div style="font-weight:850;color:#b45309">2 · CERCA DE f_c</div>
              <div style="font-size:1.25rem;font-weight:850;margin:.35rem 0">f ≈ f_c</div>
              <div style="color:#57534e;line-height:1.5">
                Se alcanza una condición de coincidencia entre la propagación flexional de la placa
                y el sonido en el aire. El acoplamiento placa–aire mejora y la radiación puede aumentar.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with csup:
        st.markdown(
            """
            <div style="border:1px solid #bbf7d0;border-radius:16px;padding:15px;background:#f0fdf4;min-height:245px">
              <div style="font-weight:850;color:#15803d">3 · SOBRE f_c</div>
              <div style="font-size:1.25rem;font-weight:850;margin:.35rem 0">f &gt; f_c</div>
              <div style="color:#475569;line-height:1.5">
                La placa puede radiar de manera más eficiente. Bajo la aproximación empleada,
                <b>σrad puede aproximarse a 1</b> y la ecuación de predicción cambia.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="border:1px solid #dbe4ee;border-radius:14px;padding:14px 16px;background:#f8fbff;margin:.7rem 0 .7rem">
          <b>La cadena física es:</b><br>
          vibración de la losa → acoplamiento con el aire → eficiencia de radiación → nivel de ruido de impacto.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="border:1px solid #fecaca;border-radius:14px;padding:14px 16px;background:#fff7f7;margin:.4rem 0 .9rem">
          <b>No confundir f_c con una frecuencia natural.</b><br>
          Una <b>frecuencia natural</b> está asociada a modos propios y a una posible resonancia de la estructura.
          La <b>frecuencia crítica</b> está asociada al acoplamiento entre las ondas de flexión de la placa
          y las ondas acústicas del aire.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 3.3 · Explora una banda")
    f_demo=st.select_slider(
        "Frecuencia a comparar con f_c (Hz)",
        options=[63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150],
        value=250,
        key=f"{ns}_fdemo",
    )
    if fc:
        ratio=float(f_demo/fc)
        c1,c2,c3=st.columns(3)
        with c1:
            _card("Frecuencia seleccionada",f"{f_demo} Hz","Banda que estás analizando.")
        with c2:
            _card("Frecuencia crítica de la losa",f"{fc:.0f} Hz","Propiedad calculada a partir de masa y rigidez.")
        with c3:
            if ratio < 0.90:
                pos_txt="Bajo f_c"
                pos_desc=f"{f_demo} Hz está por debajo de f_c. Corresponde el régimen subcrítico."
            elif ratio <= 1.10:
                pos_txt="Cerca de f_c"
                pos_desc=f"{f_demo} Hz está muy próximo a f_c. Estamos en la zona de transición crítica."
            else:
                pos_txt="Sobre f_c"
                pos_desc=f"{f_demo} Hz está por encima de f_c. Corresponde el régimen sobre frecuencia crítica."
            _card("Posición respecto de f_c",pos_txt,pos_desc,tone="blue")

        st.caption(f"Dato secundario: f / f_c = {ratio:.2f}")

        if ratio < 0.90:
            st.warning(
                f"{f_demo} Hz está bajo f_c ≈ {fc:.0f} Hz. "
                "La predicción debe usar la expresión subcrítica."
            )
        elif ratio <= 1.10:
            st.info(
                f"{f_demo} Hz está cerca de f_c ≈ {fc:.0f} Hz. "
                "Estás observando la zona donde cambia el comportamiento radiativo."
            )
        else:
            st.success(
                f"{f_demo} Hz está sobre f_c ≈ {fc:.0f} Hz. "
                "La predicción debe usar la expresión correspondiente al régimen sobre frecuencia crítica."
            )

    # ==============================================================
    # 4. ECUACIONES + UNA BANDA
    # ==============================================================
    st.markdown("## 4 · Laboratorio: calcula una banda completa")
    st.write(
        "Ahora usamos la frecuencia seleccionada como única decisión del alumno. "
        "Las propiedades acústicas necesarias se estiman automáticamente a partir de la losa y de esa banda."
    )

    st.markdown("### ¿Qué ecuación de predicción estamos usando?")
    st.write(
        "El modelo de Vér estima el nivel de ruido de impacto de la losa a partir de la banda de frecuencia, "
        "su aislamiento aéreo, la eficiencia de radiación y —bajo f_c— el amortiguamiento estructural. "
        "Como estamos calculando la **losa base sin tratamiento**, se toma ΔLₙ = 0."
    )

    st.markdown("#### A · Si la banda está bajo la frecuencia crítica")
    st.markdown(
        """<div style="border:2px solid #bfdbfe;border-radius:16px;padding:14px 18px;background:#eff6ff;margin:.35rem 0 .55rem">
        <div style="font-weight:850;color:#1d4ed8">CONDICIÓN: f &lt; f_c</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.latex(
        r"\boxed{"
        r"L_{n,0}(f)=39.5+20\log_{10}(f)"
        r"-10\log_{10}\left(\frac{\eta_p}{f_c\,\sigma_{\mathrm{rad}}(f)}\right)"
        r"-R(f)"
        r"}"
    )
    st.write(
        "En este régimen la predicción depende explícitamente del **amortiguamiento de la losa**, "
        "de la **frecuencia crítica** y de la **eficiencia de radiación**."
    )

    st.markdown("#### B · Si la banda está sobre la frecuencia crítica")
    st.markdown(
        """<div style="border:2px solid #bbf7d0;border-radius:16px;padding:14px 18px;background:#f0fdf4;margin:.35rem 0 .55rem">
        <div style="font-weight:850;color:#15803d">CONDICIÓN: f ≥ f_c</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.latex(
        r"\boxed{"
        r"L_{n,0}(f)=43+30\log_{10}(f)"
        r"-10\log_{10}\left(\sigma_{\mathrm{rad}}(f)\right)"
        r"-R(f)"
        r"}"
    )
    st.write(
        "Sobre la frecuencia crítica cambia el régimen de radiación y la expresión se simplifica. "
        "En la aproximación utilizada, σrad puede acercarse a 1."
    )

    st.markdown("### ¿Qué significa cada parámetro?")
    p1,p2,p3=st.columns(3)
    with p1:
        _card(
            "f · Frecuencia",
            "Hz",
            "Banda que estamos calculando. Cada frecuencia puede caer bajo o sobre f_c."
        )
    with p2:
        _card(
            "R(f) · Índice de reducción sonora",
            "dB",
            "Representa la capacidad estimada de la losa para oponerse a la transmisión sonora aérea en esa banda."
        )
    with p3:
        _card(
            "σrad(f) · Eficiencia de radiación",
            "adimensional",
            "Indica qué tan eficientemente la vibración de la placa se transforma en sonido radiado."
        )

    p4,p5,p6=st.columns(3)
    with p4:
        _card(
            "ηₚ · Factor de pérdidas",
            "adimensional",
            "Representa el amortiguamiento estructural de la losa. Aparece explícitamente en el régimen subcrítico."
        )
    with p5:
        _card(
            "f_c · Frecuencia crítica",
            "Hz",
            "Separa los dos regímenes de radiación y decide qué ecuación corresponde."
        )
    with p6:
        _card(
            "Lₙ,₀(f) · Resultado",
            "dB",
            "Nivel de ruido de impacto predicho para la losa base sin tratamiento en esa banda.",
            tone="blue"
        )

    st.markdown(
        """
        <div style="border:1px solid #dbe4ee;border-radius:14px;padding:14px 16px;background:#f8fbff;margin:.5rem 0 .9rem">
          <b>Lectura física de la ecuación:</b><br>
          la frecuencia fija la banda de análisis; R(f) representa cuánto se opone la losa a transmitir sonido;
          σrad representa cuánto de su vibración logra radiar; ηₚ introduce el efecto del amortiguamiento bajo f_c;
          y el resultado final es Lₙ,₀(f).
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "**Importante sobre R(f) y σrad:** las ecuaciones de Vér del material de referencia necesitan estas variables, "
        "pero el documento no entrega una fórmula única para obtenerlas desde las propiedades de la losa. "
        "Para este laboratorio se estiman automáticamente mediante aproximaciones didácticas transparentes: "
        "R(f) con una ley de masa de placa homogénea y σrad a partir de f/f_c. "
        "No deben confundirse con una medición de laboratorio ni con un modelo FEM."
    )

    bands=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150]
    fsel=st.select_slider(
        "Selecciona la banda que quieres calcular (Hz)",
        options=bands,
        value=250,
        key=f"{ns}_fsel",
    )

    if fc:
        R_auto,sigma_auto,ln_auto,regime=_band_solution(fsel,m_surface,fc,eta)
        st.markdown("### Paso 1 · El modelo obtiene las entradas de esa banda")
        q1,q2,q3,q4=st.columns(4)
        with q1:
            _card("f / f_c",f"{fsel/fc:.2f}",("Subcrítico" if fsel<fc else "Sobre frecuencia crítica"))
        with q2:
            _card("R(f) estimado",f"{R_auto:.1f} dB","Estimación automática mediante ley de masa.")
        with q3:
            _card("σrad estimada",f"{sigma_auto:.2f}","Estimación automática dependiente de f/f_c.")
        with q4:
            _card("ηₚ",f"{eta:.3f}","Factor de pérdidas definido para la losa.")

        st.markdown("### Paso 2 · Se selecciona automáticamente la ecuación")
        if fsel < fc:
            st.info("Se aplica la expresión **subcrítica** porque f < f_c.")
            st.latex(
                rf"L_{{n,0}}({fsel})=39.5+20\log_{{10}}({fsel})"
                rf"-10\log_{{10}}\left(\frac{{{eta:.3f}}}{{{fc:.1f}\cdot {sigma_auto:.3f}}}\right)-{R_auto:.1f}"
            )
        else:
            st.success("Se aplica la expresión **sobre frecuencia crítica** porque f ≥ f_c.")
            st.latex(
                rf"L_{{n,0}}({fsel})=43+30\log_{{10}}({fsel})"
                rf"-10\log_{{10}}({sigma_auto:.3f})-{R_auto:.1f}"
            )

        st.markdown("### Paso 3 · Resultado de la banda")
        _card(
            f"Lₙ,₀({fsel} Hz)",
            f"{ln_auto:.1f} dB",
            "Anota este valor. En la siguiente parte tendrás que registrarlo correctamente "
            "para incorporar esta banda a la curva base.",
            tone="blue",
        )

    # ==============================================================
    # 5. CURVA BANDA A BANDA — EL ALUMNO INGRESA
    # ==============================================================
    st.markdown("## 5 · Construye tú mismo la curva base Lₙ,₀(f)")
    st.write(
        "El gráfico parte vacío. Calcula una banda en la Parte 4, escribe aquí el resultado y compruébalo. "
        "**Solo los valores correctos se incorporan al gráfico.**"
    )

    answers=saved.get("stage5_band_answers",{})
    if not isinstance(answers,dict):
        answers={}
        saved["stage5_band_answers"]=answers

    band_register=st.selectbox(
        "Banda que vas a registrar",
        bands,
        index=bands.index(fsel) if fsel in bands else 0,
        key=f"{ns}_band_register",
    )
    entered=st.number_input(
        f"Ingresa Lₙ,₀({band_register} Hz) calculado (dB)",
        min_value=0.0,max_value=150.0,value=0.0,step=0.1,format="%.1f",
        key=f"{ns}_band_value",
    )

    ccheck,creset=st.columns([2,1])
    with ccheck:
        if st.button("Comprobar y agregar al gráfico",type="primary",key=f"{ns}_add_band",use_container_width=True):
            if not fc:
                st.warning("Primero define correctamente la losa.")
            else:
                Rb,sb,expected,_=_band_solution(band_register,m_surface,fc,eta)
                if abs(float(entered)-float(expected)) <= 0.15:
                    answers[str(band_register)]=round(float(expected),3)
                    saved["stage5_band_answers"]=answers
                    _persist()
                    st.success(f"Banda {band_register} Hz correcta. Se agregó al gráfico.")
                    st.rerun()
                else:
                    st.warning(
                        "El valor no coincide con el cálculo de esa banda. "
                        "Vuelve a la Parte 4, selecciona la misma frecuencia y revisa la ecuación aplicada."
                    )
    with creset:
        if st.button("Resetear curva",key=f"{ns}_reset_curve",use_container_width=True):
            saved["stage5_band_answers"]={}
            saved.pop("stage5_baseline",None)
            saved["done_5"]=False
            _persist()
            st.rerun()

    completed=[f for f in bands if str(f) in answers]
    st.progress(len(completed)/len(bands),text=f"Bandas completadas: {len(completed)} / {len(bands)}")

    # Tabla de estado sin revelar los valores pendientes.
    rows=[]
    for ff in bands:
        if str(ff) in answers:
            rows.append({"Banda (Hz)":ff,"Estado":"Completada","Lₙ,₀ (dB)":f"{answers[str(ff)]:.1f}"})
        else:
            rows.append({"Banda (Hz)":ff,"Estado":"Pendiente","Lₙ,₀ (dB)":"—"})
    st.dataframe(rows,hide_index=True,use_container_width=True)

    if completed:
        # Eje por bandas discretas: cada banda ocupa el mismo espacio visual.
        band_positions={ff:i for i,ff in enumerate(bands)}
        x=np.array([band_positions[f] for f in completed],dtype=float)
        y=np.array([answers[str(f)] for f in completed],dtype=float)
        order=np.argsort(x)

        fig,ax=plt.subplots(figsize=(10.5,4.8))
        ax.plot(
            x[order],
            y[order],
            marker="o",
            linewidth=2.2,
            markersize=7,
            label="Bandas validadas"
        )

        # Mostrar todas las bandas normalizadas en el eje X.
        all_positions=np.arange(len(bands))
        ax.set_xticks(all_positions)
        ax.set_xticklabels([str(f) for f in bands],rotation=45,ha="right")

        # Marcar la posición aproximada de f_c entre bandas, sin convertir el
        # eje en una escala continua/logarítmica.
        if fc <= bands[0]:
            fc_pos=0.0
        elif fc >= bands[-1]:
            fc_pos=float(len(bands)-1)
        else:
            fc_pos=0.0
            for i in range(len(bands)-1):
                f1,f2=bands[i],bands[i+1]
                if f1 <= fc <= f2:
                    frac=(fc-f1)/(f2-f1)
                    fc_pos=i+frac
                    break

        ax.axvline(
            fc_pos,
            linestyle="--",
            linewidth=1.5,
            label=f"f_c ≈ {fc:.0f} Hz"
        )

        ax.set_xlim(-0.4,len(bands)-0.6)
        ax.set_xlabel("Bandas de frecuencia (Hz)")
        ax.set_ylabel("Lₙ,₀ (dB)")
        ax.set_title("Curva base construida por bandas")
        ax.grid(True,axis="y",alpha=.22)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)

        st.caption(
            "Cada posición del eje X corresponde a una banda discreta del laboratorio. "
            "La línea vertical indica la ubicación aproximada de la frecuencia crítica entre esas bandas."
        )
    else:
        st.info("Todavía no hay puntos validados. Calcula la primera banda en la Parte 4.")

    if len(completed)==len(bands):
        st.success(
            "Has completado todas las bandas. La curva Lₙ,₀(f) está lista para guardarse como referencia oficial."
        )

    # ==============================================================
    # 6. GUARDA BASELINE
    # ==============================================================
    st.markdown("## 6 · Guarda la referencia oficial de la losa")
    st.write(
        "Solo cuando todas las bandas estén validadas puedes guardar el baseline que utilizarán las siguientes etapas."
    )

    if len(completed)==len(bands) and fc:
        ln_full=[float(answers[str(f)]) for f in bands]
        b1,b2,b3=st.columns(3)
        with b1:
            _card("Losa base",f"{t_mm:.0f} mm",f"m′ = {m_surface:.1f} kg/m²")
        with b2:
            _card("f_c",f"{fc:.0f} Hz","Cambio de régimen de la placa.")
        with b3:
            _card("Curva",f"{len(bands)} bandas","Lₙ,₀(f) completada por el alumno.",tone="blue")

        if st.button("Guardar Lₙ,₀(f) como baseline",type="primary",key=f"{ns}_save_base"):
            R_list=[]; sigma_list=[]
            for ff in bands:
                RR,ss,_,_=_band_solution(ff,m_surface,fc,eta)
                R_list.append(round(RR,3)); sigma_list.append(round(ss,4))
            saved["stage5_baseline"]={
                "bands_hz":[int(f) for f in bands],
                "ln0_db":[round(v,3) for v in ln_full],
                "R_estimated_db":R_list,
                "sigma_estimated":sigma_list,
                "rho_p_kg_m3":float(rho_p),
                "thickness_mm":float(t_mm),
                "young_gpa":float(E),
                "poisson":float(nu),
                "eta":float(eta),
                "surface_mass_kg_m2":float(m_surface),
                "D_Nm":float(D),
                "fc_hz":float(fc),
                "source":{
                    "mode":source_mode,
                    "fr_hz":float(fr),
                    "hammer_mass_kg":float(mass),
                    "drop_height_m":float(h),
                    "v0_m_s":float(v0),
                    "Fn_N":float(Fn),
                    "Sf0_N2_Hz":float(Sf0),
                },
                "estimation_note":"R(f): aproximación didáctica de ley de masa; sigma_rad(f): aproximación didáctica dependiente de f/f_c.",
                "updated_at":_now(),
            }
            saved["done_5"]=True
            _persist()
            st.success("Baseline guardado. Las etapas posteriores ya pueden comparar soluciones con esta curva.")

    # ==============================================================
    # CIERRE / DOCENTE
    # ==============================================================
    st.markdown("## Cierre · Ya tenemos la referencia que necesitábamos")
    st.latex(r"\boxed{L_{n,0}(f)}")
    st.write(
        "La curva base representa la predicción de la losa desnuda. "
        "A partir de ahora estudiaremos cuánto cambia al incorporar una solución constructiva."
    )
    st.latex(r"L_{n,\mathrm{tratado}}(f)=L_{n,0}(f)-\Delta L(f)")
    st.success("La Etapa 6 utilizará esta referencia para comenzar a estudiar parámetros de control de impacto.")

    with st.container(border=True):
        st.markdown("### Referencia y alcance del modelo")
        st.write(
            "Vér, I. L. & Beranek, L. L. (eds.). *Noise and Vibration Control Engineering: "
            "Principles and Applications*, 2nd ed., Wiley, 2006. Cap. 11, §11.11 Impact Noise."
        )
        st.write(
            "Las expresiones de predicción bajo y sobre f_c corresponden al material de referencia de esta etapa. "
            "Las estimaciones automáticas de R(f) y σrad(f) se incorporan únicamente para hacer autocontenido el laboratorio "
            "y se identifican expresamente como aproximaciones didácticas."
        )

    if role=="Docente" and not projection_mode:
        st.markdown("---")
        st.markdown("## Vista docente · desarrollo esperado")
        st.write(
            "El alumno debe justificar por qué se caracteriza la fuente, comprender físicamente f_c, "
            "identificar la expresión de Vér aplicable y construir la curva banda por banda."
        )
        st.write(
            "R(f) y σrad(f) no se presentan como datos libres: la plataforma los estima automáticamente "
            "mediante aproximaciones didácticas y las identifica como tales."
        )
        st.write(
            "La etapa se completa solo al validar todas las bandas y guardar Lₙ,₀(f)."
        )

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 4",key=f"s5_prev_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=4
            st.rerun()
    with right:
        if st.button("Etapa 6 →",key=f"s5_next_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=6
            st.rerun()

def _render_course2_lab1_stage6(lab, saved):
    """Etapa 6 · Diseño de una solución y predicción banda a banda de ΔL_n(f)."""
    import math
    import numpy as np
    import matplotlib.pyplot as plt

    class_id=lab["id"]
    stage_selector_key=f"future_stage_{class_id}"
    role=st.session_state.get("role","Alumno")
    projection_mode=bool(st.session_state.get("projection_mode") or role=="Proyección")
    ns=f"{class_id}_s6"

    def _asset(name,caption=None):
        p=ASSET_DIR/name
        if p.exists():
            st.image(str(p),width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode",False):
            st.caption(f"[Asset pendiente: {name}]")
        return False

    def _persist():
        saved["updated_6"]=_now()
        fn=globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn):
            fn(class_id,saved)

    def _card(title,value,text,tone="white"):
        bg="#fff" if tone=="white" else "#eff6ff"
        bd="#dbe4ee" if tone=="white" else "#bfdbfe"
        st.markdown(
            f"""<div style="border:1px solid {bd};border-radius:16px;padding:15px 16px;
            background:{bg};min-height:165px;box-sizing:border-box;margin-bottom:6px">
              <div style="font-weight:800;color:#0f172a">{title}</div>
              <div style="font-size:1.55rem;font-weight:850;color:#0f172a;margin:.35rem 0">{value}</div>
              <div style="color:#64748b;line-height:1.45">{text}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    def _mred(m1,m2):
        return (m1*m2)/max(m1+m2,1e-12)

    def _f0_general(s_MN_m3,m1,m2):
        mr=_mred(m1,m2)
        return (1/(2*math.pi))*math.sqrt((s_MN_m3*1e6)/max(mr,1e-12))

    def _f0_cont(s_MN_m3,m1):
        return (1/(2*math.pi))*math.sqrt((s_MN_m3*1e6)/max(m1,1e-12))

    def _delta_cremer(f,s_MN_m3,m1):
        # Formulación presentada en la etapa fuente:
        # ΔLn = 20 log10((2πf)^2 m1'/s')
        arg=((2*math.pi*f)**2 * m1)/(s_MN_m3*1e6)
        return 20*math.log10(max(arg,1e-12))

    def _delta_ver_demo(f,f0,cL1,h1,Nsup,eta11):
        # Implementación didáctica de la expresión mostrada en la etapa anterior.
        # Se conserva como modelo distinto para apoyos discretos.
        num=cL1*h1*Nsup*eta11*(f**3)
        den=2*(math.pi**3)*(f0**4)
        return 10*math.log10(max(num/max(den,1e-12),1e-12))

    header(
        "ETAPA 6 · LABORATORIO 1",
        "Predicción de la mejora del piso flotante: ΔLₙ(f)",
        "Diseña la solución y construye banda por banda su mejora respecto de la losa base.",
        show_overview=False,
        duration_minutes=90,
    )

    st.markdown("### Continuidad con la Etapa 5")
    baseline=saved.get("stage5_baseline")
    if baseline:
        bands=[int(x) for x in baseline.get("bands_hz",[])]
        ln0=[float(x) for x in baseline.get("ln0_db",[])]
        m2=float(baseline.get("surface_mass_kg_m2",384.0))
        t_base=float(baseline.get("thickness_mm",160.0))
        fc_base=float(baseline.get("fc_hz",0.0))
        st.success("Se recuperó correctamente la losa base guardada en la Etapa 5.")
        b1,b2,b3=st.columns(3)
        with b1: _card("Losa base",f"{t_base:.0f} mm",f"Masa superficial m′₂ = {m2:.1f} kg/m²")
        with b2: _card("Frecuencia crítica",f"{fc_base:.0f} Hz","Propiedad calculada en la Etapa 5.")
        with b3: _card("Baseline",f"{len(bands)} bandas","Curva Lₙ,₀(f) disponible para comparar la solución.",tone="blue")
    else:
        st.warning(
            "No encuentro una curva base guardada de la Etapa 5. "
            "Para mantener la continuidad del laboratorio, completa y guarda primero Lₙ,₀(f)."
        )
        bands=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150]
        ln0=[]
        m2=384.0

    st.latex(r"\boxed{\Delta L_n(f)=L_{n,0}(f)-L_n(f)}")
    st.info(
        "En esta etapa **no calcularemos todavía Lₙ,final(f)**. "
        "El resultado que debemos producir es únicamente la curva de mejora ΔLₙ(f). "
        "La Etapa 7 combinará ambas curvas."
    )

    # ==============================================================
    # 1 · ELEGIR SISTEMA
    # ==============================================================
    st.markdown("## 1 · ¿Cómo está construido el piso?")
    st.write(
        "Primero identifica la configuración física. El modelo no se elige por cuál entrega más dB, "
        "sino por cómo está construido realmente el sistema."
    )
    systems_render=ASSET_DIR/"curso2_lab1_etapa6_sistemas_flotantes_profesional.webp"
    if systems_render.exists():
        st.image(
            str(systems_render),
            width="stretch",
            caption="Comparación física: capa resiliente continua y apoyos resilientes discretos."
        )

    config=st.radio(
        "Configuración constructiva",
        [
            "Piso flotante sobre capa resiliente continua",
            "Piso flotante sobre apoyos resilientes discretos",
        ],
        horizontal=True,
        key=f"{ns}_config",
    )

    if config=="Piso flotante sobre capa resiliente continua":
        model="Cremer/Vigran"
        st.success("Construcción identificada → modelo compatible: **Cremer/Vigran**.")
        st.caption("La transferencia mecánica se distribuye prácticamente sobre toda la superficie.")
    else:
        model="Vér"
        st.success("Construcción identificada → modelo compatible: **Vér**.")
        st.caption("La transferencia mecánica se concentra en apoyos separados espacialmente.")

    st.markdown(
        """<div style="border:1px solid #fde68a;background:#fffbeb;border-radius:14px;padding:13px 16px;margin:.5rem 0 .8rem">
        <b>Regla del laboratorio:</b> no se permite cambiar de modelo para obtener una mejora mayor.
        La geometría y el mecanismo de apoyo determinan qué formulación es físicamente compatible.
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Ejemplos de sistemas reales")
    link1,link2,link3=st.columns(3)
    with link1:
        st.link_button(
            "ROCKWOOL · suelo flotante",
            "https://www.rockwool.com/es/productos-y-aplicaciones/aislamiento-suelos-y-forjados/suelo-flotante/suelo-flotante/",
            use_container_width=True,
        )
    with link2:
        st.link_button(
            "REGUPOL · capa continua",
            "https://acoustics.regupol.com/products/range/regupol-comfort/regupol-comfort-5/",
            use_container_width=True,
        )
    with link3:
        st.link_button(
            "Kinetics · apoyos discretos",
            "https://kineticsnoise.com/flm/lift-slab-floor-mount",
            use_container_width=True,
        )
    st.caption(
        "Los enlaces se incluyen para comparar la idealización del modelo con configuraciones constructivas reales."
    )

    # ==============================================================
    # 2 · CONSTRUIR SOLUCIÓN
    # ==============================================================
    st.markdown("## 2 · Construye físicamente el piso flotante")
    st.write(
        "La losa base ya viene de la Etapa 5. Ahora define la **masa flotante superior** "
        "y el **elemento resiliente** que la separa de la losa base."
    )

    if config=="Piso flotante sobre capa resiliente continua":
        st.info("Sistema de referencia: **piso laminado flotante liviano sobre manta resiliente continua**.")
        c1,c2,c3=st.columns(3)
        with c1:
            rho1=st.number_input("Densidad del piso laminado ρ₁ (kg/m³)",500.0,1200.0,850.0,25.0,key=f"{ns}_rho1_cont")
        with c2:
            h1_mm=st.number_input("Espesor del piso laminado h₁ (mm)",6.0,20.0,12.0,1.0,key=f"{ns}_h1_cont")
        with c3:
            s_dyn=st.number_input("Rigidez dinámica superficial de la manta s′ (MN/m³)",1.0,80.0,15.0,0.5,key=f"{ns}_sdyn_cont")
    else:
        st.info("Sistema de referencia: **sobrelosa flotante pesada sobre apoyos resilientes discretos**.")
        c1,c2,c3=st.columns(3)
        with c1:
            rho1=st.number_input("Densidad de la sobrelosa ρ₁ (kg/m³)",1500.0,2600.0,2100.0,50.0,key=f"{ns}_rho1_disc")
        with c2:
            h1_mm=st.number_input("Espesor de la sobrelosa h₁ (mm)",30.0,120.0,50.0,5.0,key=f"{ns}_h1_disc")
        with c3:
            s_dyn=st.number_input("Rigidez dinámica superficial equivalente s′ (MN/m³)",1.0,80.0,10.0,0.5,key=f"{ns}_sdyn_disc")

    m1=rho1*(h1_mm/1000.0)
    mr=_mred(m1,m2)
    f0g=_f0_general(s_dyn,m1,m2)

    q1,q2,q3,q4=st.columns(4)
    with q1:
        if config=="Piso flotante sobre capa resiliente continua":
            _card("m′₁ · Piso laminado flotante",f"{m1:.1f} kg/m²","Masa superficial del piso laminado desacoplado por la manta.")
        else:
            _card("m′₁ · Sobrelosa flotante",f"{m1:.1f} kg/m²","Masa superficial de la sobrelosa sobre apoyos discretos.")
    with q2: _card("m′₂ · Losa base",f"{m2:.1f} kg/m²","Dato recuperado de la Etapa 5.")
    with q3: _card("m′ᵣ · Masa reducida",f"{mr:.1f} kg/m²","Masa equivalente para el movimiento relativo.")
    with q4: _card("f₀ · Sistema general",f"{f0g:.1f} Hz","Frecuencia natural del sistema masa flotante–resiliente–losa base.",tone="blue")

    st.markdown("### Rigidez dinámica superficial del elemento resiliente")
    sr1,sr2=st.columns([1.1,1])
    with sr1:
        if (ASSET_DIR/"curso2_lab1_etapa6_rigidez_dinamica_profesional.webp").exists():
            st.image(str(ASSET_DIR/"curso2_lab1_etapa6_rigidez_dinamica_profesional.webp"),width="stretch")
            st.caption("Arriba: piso laminado flotante (m′₁) · Centro: manta resiliente (s′) · Abajo: losa base (m′₂).")
    with sr2:
        st.markdown(
            """
            <div style="border:1px solid #dbe4ee;border-radius:18px;padding:17px;background:#fff;margin-bottom:10px">
              <div style="font-weight:850;color:#0f172a;font-size:1.05rem">¿Qué representa s′?</div>
              <div style="color:#64748b;line-height:1.5;margin-top:.4rem">
                Mide cuánto se opone el elemento resiliente a una
                <b>deformación dinámica distribuida</b> sobre la superficie.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.latex(r"\boxed{s'\;[\mathrm{MN/m^3}]}")
        st.markdown(
            """
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
              <div style="border:1px solid #bbf7d0;border-radius:14px;padding:13px;background:#f0fdf4">
                <b>s′ alta</b><br>
                <span style="color:#475569">Apoyo más rígido.<br>Tiende a elevar f₀.</span>
              </div>
              <div style="border:1px solid #bfdbfe;border-radius:14px;padding:13px;background:#eff6ff">
                <b>s′ baja</b><br>
                <span style="color:#475569">Apoyo más flexible.<br>Tiende a reducir f₀.</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <div style="border:1px solid #fde68a;background:#fffbeb;border-radius:14px;padding:13px 16px;margin:.6rem 0 .9rem">
          <b>No confundir s′ con:</b> módulo de Young E, rigidez estática,
          espesor del material ni constante de un resorte puntual.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==============================================================
    # 3 · RESONANCIA APLICADA
    # ==============================================================
    st.markdown("## 3 · Frecuencia natural del piso flotante")
    st.write(
        "Aplicamos aquí el concepto de resonancia al sistema "
        "**masa flotante – elemento resiliente – losa base**. "
        "Cuando la excitación se aproxima a f₀, la respuesta relativa del sistema puede aumentar."
    )

    if (ASSET_DIR/"curso2_lab1_etapa6_frecuencia_natural_profesional.webp").exists():
        st.image(str(ASSET_DIR/"curso2_lab1_etapa6_frecuencia_natural_profesional.webp"),width="stretch")

    with st.container(border=True):
        st.markdown("### Ecuaciones del sistema")
        eq1,eq2=st.columns(2)
        with eq1:
            st.markdown("**Masa reducida**")
            st.latex(r"m_r'=\frac{m_1'm_2'}{m_1'+m_2'}")
        with eq2:
            st.markdown("**Frecuencia natural**")
            st.latex(r"f_0=\frac{1}{2\pi}\sqrt{\frac{s'}{m_r'}}")

    st.markdown("### ¿Qué pasa si cambio los parámetros?")
    rr1,rr2,rr3=st.columns(3)
    with rr1:
        st.markdown(
            """<div style="border:1px solid #bbf7d0;border-radius:16px;padding:15px;background:#f0fdf4;min-height:170px">
            <b>Apoyo más rígido</b><br><br>
            <span style="font-size:1.15rem;font-weight:800">s′ ↑ → f₀ ↑</span><br><br>
            <span style="color:#475569">La resonancia se desplaza hacia frecuencias mayores.</span>
            </div>""",unsafe_allow_html=True)
    with rr2:
        st.markdown(
            """<div style="border:1px solid #bfdbfe;border-radius:16px;padding:15px;background:#eff6ff;min-height:170px">
            <b>Mayor masa flotante</b><br><br>
            <span style="font-size:1.15rem;font-weight:800">m′₁ ↑ → f₀ ↓</span><br><br>
            <span style="color:#475569">Más masa tiende a bajar la resonancia.</span>
            </div>""",unsafe_allow_html=True)
    with rr3:
        st.markdown(
            """<div style="border:1px solid #ddd6fe;border-radius:16px;padding:15px;background:#f5f3ff;min-height:170px">
            <b>Base mucho más pesada</b><br><br>
            <span style="font-size:1.05rem;font-weight:800">m′₂ ≫ m′₁ → m′ᵣ ≈ m′₁</span><br><br>
            <span style="color:#475569">Aparece la aproximación utilizada por el modelo continuo.</span>
            </div>""",unsafe_allow_html=True)

    if model=="Cremer/Vigran":
        f0_model=_f0_cont(s_dyn,m1)
    else:
        f0_model=f0g

    if model=="Cremer/Vigran":
        st.markdown("### ¿Con qué parámetros se calcularon estas frecuencias?")
        pfc1,pfc2,pfc3=st.columns(3)
        with pfc1:
            _card("m′₁ · Piso laminado",f"{m1:.1f} kg/m²","Calculado a partir de la densidad y el espesor definidos arriba.")
        with pfc2:
            _card("m′₂ · Losa base",f"{m2:.1f} kg/m²","Valor recuperado de la Etapa 5.")
        with pfc3:
            _card("s′ · Manta resiliente",f"{s_dyn:.2f} MN/m³","Rigidez dinámica superficial del elemento resiliente.",tone="blue")

        st.markdown("#### Sistema general de dos masas")
        st.latex(fr"""m_r'=\frac{{{m1:.1f}\cdot {m2:.1f}}}{{{m1:.1f}+{m2:.1f}}}
        ={mr:.1f}\;\mathrm{{kg/m^2}}""")
        st.latex(fr"""f_{{0,\mathrm{{general}}}}
        =\frac{{1}}{{2\pi}}\sqrt{{\frac{{{s_dyn:.2f}\times10^6}}{{{mr:.1f}}}}}
        ={f0g:.1f}\;\mathrm{{Hz}}""")

        st.markdown("#### Modelo continuo simplificado")
        st.write("Supone que la losa base es suficientemente pesada y utiliza principalmente la masa superficial del piso flotante.")
        st.latex(fr"""f_{{0,\mathrm{{cont}}}}
        =\frac{{1}}{{2\pi}}\sqrt{{\frac{{{s_dyn:.2f}\times10^6}}{{{m1:.1f}}}}}
        ={f0_model:.1f}\;\mathrm{{Hz}}""")

        cf1,cf2=st.columns(2)
        with cf1:
            _card("Sistema general",f"{f0g:.1f} Hz","Usa m′₁, m′₂ y s′ a través de la masa reducida.")
        with cf2:
            _card("Modelo continuo",f"{f0_model:.1f} Hz","Usa m′₁ y s′ bajo la hipótesis de base pesada.",tone="blue")
        st.info("Los valores pueden diferir porque corresponden a hipótesis de modelación diferentes.")
    else:
        st.markdown("### ¿Con qué parámetros se calcula f₀?")
        pfc1,pfc2,pfc3=st.columns(3)
        with pfc1:
            _card("m′₁ · Sobrelosa",f"{m1:.1f} kg/m²","Masa superficial de la sobrelosa flotante.")
        with pfc2:
            _card("m′₂ · Losa base",f"{m2:.1f} kg/m²","Valor recuperado de la Etapa 5.")
        with pfc3:
            _card("s′ equivalente",f"{s_dyn:.2f} MN/m³","Rigidez dinámica superficial equivalente de los apoyos.",tone="blue")

        st.latex(fr"""m_r'=\frac{{{m1:.1f}\cdot {m2:.1f}}}{{{m1:.1f}+{m2:.1f}}}
        ={mr:.1f}\;\mathrm{{kg/m^2}}""")
        st.latex(fr"""f_0=\frac{{1}}{{2\pi}}
        \sqrt{{\frac{{{s_dyn:.2f}\times10^6}}{{{mr:.1f}}}}}
        ={f0_model:.1f}\;\mathrm{{Hz}}""")
        _card("Frecuencia natural utilizada",f"{f0_model:.1f} Hz","Resultado calculado con la masa reducida del sistema.",tone="blue")

    # ==============================================================
    # 4 · MODELO ACÚSTICO
    # ==============================================================
    st.markdown("## 4 · De la dinámica a la mejora acústica ΔLₙ(f)")
    st.write(
        "La frecuencia natural por sí sola **no entrega la mejora acústica**. "
        "Ahora usamos la formulación compatible con la construcción seleccionada."
    )

    active_bg="#eff6ff" if model=="Cremer/Vigran" else "#f0fdf4"
    active_bd="#bfdbfe" if model=="Cremer/Vigran" else "#bbf7d0"
    st.markdown(
        f"""<div style="border:2px solid {active_bd};border-radius:18px;padding:16px 18px;background:{active_bg};margin:.5rem 0 .9rem">
        <div style="font-size:1.05rem;font-weight:850;color:#0f172a">MODELO ACTIVO</div>
        <div style="font-size:1.45rem;font-weight:900;margin:.25rem 0">{model}</div>
        <div style="color:#475569">La configuración física del piso determinó automáticamente este modelo.</div>
        </div>""",
        unsafe_allow_html=True,
    )

    if model=="Cremer/Vigran":
        st.markdown("### Capa resiliente continua")
        st.write("La masa flotante superior descansa sobre una capa resiliente distribuida prácticamente en toda la superficie.")
        with st.container(border=True):
            st.markdown("**Ecuación principal**")
            st.latex(
                r"\boxed{\Delta L_n(f)=20\log_{10}\left("
                r"\frac{(2\pi f)^2m_1'}{s'}"
                r"\right)}"
            )
            st.caption("Calcula la mejora por banda a partir de frecuencia, masa flotante y rigidez dinámica superficial.")

        st.markdown("### Cómo se construye el cálculo de ΔLₙ(f)")
        st.write("En vez de repetir variables en varias tarjetas, seguimos una secuencia única:")

        f_demo_calc = 250 if 250 in bands else bands[0]
        delta_demo_calc = max(0.0,_delta_cremer(f_demo_calc,s_dyn,m1))

        st.markdown("#### 1 · Datos definidos para el piso")
        fd1,fd2=st.columns(2)
        with fd1:
            _card("m′₁ · Masa superficial",f"{m1:.1f} kg/m²","Resultado de densidad × espesor del piso laminado.")
        with fd2:
            _card("s′ · Rigidez dinámica",f"{s_dyn:.2f} MN/m³","Propiedad de la manta resiliente.",tone="blue")

        st.markdown("#### 2 · De esos datos obtenemos f₀,cont")
        st.latex(fr"""f_{{0,\mathrm{{cont}}}}
        =\frac{{1}}{{2\pi}}\sqrt{{\frac{{{s_dyn:.2f}\times10^6}}{{{m1:.1f}}}}}
        ={f0_model:.1f}\;\mathrm{{Hz}}""")
        st.info(f"{f0_model:.1f} Hz es una **propiedad calculada del piso**, no una banda elegida.")

        st.markdown("#### 3 · Elegimos una banda para evaluar la mejora")
        _card("Frecuencia de ejemplo",f"{f_demo_calc} Hz","Esta frecuencia sí corresponde a una banda del laboratorio.")

        st.markdown("#### 4 · Calculamos ΔLₙ en esa banda")
        st.latex(fr"""\Delta L_n({f_demo_calc})
        =40\log_{{10}}\left(\frac{{{f_demo_calc}}}{{{f0_model:.1f}}}\right)
        ={delta_demo_calc:.1f}\;\mathrm{{dB}}""")
        _card(
            f"Mejora prevista a {f_demo_calc} Hz",
            f"{delta_demo_calc:.1f} dB",
            "Este valor corresponde a una sola banda. Luego repetiremos el procedimiento para construir la curva completa.",
            tone="blue"
        )

    else:
        st.markdown("### Apoyos resilientes discretos")
        st.write("La masa flotante descansa sobre pads, plots o aisladores separados.")
        with st.container(border=True):
            st.markdown("**Ecuación principal**")
            st.latex(
                r"\boxed{\Delta L_n(f)\approx10\log_{10}\left["
                r"\frac{c_{L1}h_1N\eta_{11}}{2\pi^3f_0^4}\,f^3"
                r"\right]}"
            )
        st.write("En este modelo aparece N, la densidad de apoyos por unidad de superficie.")
        p1,p2,p3=st.columns(3)
        with p1:
            Nsup=st.number_input("Densidad de apoyos N (1/m²)",0.5,20.0,4.0,0.5,key=f"{ns}_N")
        with p2:
            cL1=st.number_input("Velocidad longitudinal c_L1 (m/s)",1000.0,6000.0,3500.0,100.0,key=f"{ns}_cL")
        with p3:
            eta11=st.number_input("Factor de pérdidas η₁₁",0.005,0.100,0.020,0.005,key=f"{ns}_eta11")

    st.markdown(
        """<div style="border:1px solid #fde68a;background:#fffbeb;border-radius:14px;padding:13px 16px;margin:.7rem 0 .9rem">
        <b>No confundir:</b> la transmisibilidad mecánica describe fuerza transmitida;
        ΔLₙ(f) representa una <b>mejora acústica por banda</b>.
        </div>""",
        unsafe_allow_html=True,
    )

    # ==============================================================
    # 5 · CALCULAR UNA BANDA
    # ==============================================================
    st.markdown("## 5 · Laboratorio: calcula una banda")
    st.write(
        "Selecciona una frecuencia. La app usa automáticamente el modelo compatible con la construcción y muestra el resultado."
    )
    fsel=st.select_slider("Banda de frecuencia (Hz)",options=bands,value=250 if 250 in bands else bands[0],key=f"{ns}_fsel")

    if model=="Cremer/Vigran":
        delta=max(0.0,_delta_cremer(fsel,s_dyn,m1))
        st.latex(
            rf"\Delta L_n({fsel})="
            rf"20\log_{{10}}\left("
            rf"\frac{{(2\pi\cdot {fsel})^2\cdot {m1:.1f}}}{{{s_dyn:.2f}\times10^6}}"
            rf"\right)"
        )
        st.caption(
            f"f₀,cont ≈ {f0_model:.1f} Hz. "
            "Bandas demasiado próximas o bajo la resonancia deben interpretarse con cautela."
        )
    else:
        h1_m=h1_mm/1000.0
        delta=max(0.0,_delta_ver_demo(fsel,f0_model,cL1,h1_m,Nsup,eta11))
        st.latex(
            rf"\Delta L_n({fsel})\approx10\log_{{10}}\left["
            rf"\frac{{{cL1:.0f}\cdot {h1_m:.3f}\cdot {Nsup:.2f}\cdot {eta11:.3f}}}"
            rf"{{2\pi^3\cdot {f0_model:.1f}^4}}\cdot {fsel}^3"
            rf"\right]"
        )

    _card(
        f"Mejora prevista ΔLₙ({fsel} Hz)",
        f"{delta:.1f} dB",
        "Anota este resultado. En la siguiente parte tendrás que registrarlo correctamente "
        "para incorporarlo a la curva de mejora.",
        tone="blue"
    )

    # ==============================================================
    # 6 · CONSTRUIR CURVA
    # ==============================================================
    st.markdown("## 6 · Construye la curva ΔLₙ(f) banda por banda")
    st.write(
        "Igual que en la Etapa 5, el gráfico comienza vacío. "
        "Cada valor correcto que ingreses agrega un nuevo punto."
    )

    answers=saved.get("stage6_delta_answers",{})
    if not isinstance(answers,dict):
        answers={}
        saved["stage6_delta_answers"]=answers

    f_reg=st.selectbox(
        "Banda que vas a registrar",
        bands,
        index=bands.index(fsel) if fsel in bands else 0,
        key=f"{ns}_band_register"
    )
    entered=st.number_input(
        f"Ingresa ΔLₙ({f_reg} Hz) calculado (dB)",
        min_value=0.0,max_value=100.0,value=0.0,step=0.1,format="%.1f",
        key=f"{ns}_band_value"
    )

    def expected_delta(ff):
        if model=="Cremer/Vigran":
            return max(0.0,_delta_cremer(ff,s_dyn,m1))
        return max(0.0,_delta_ver_demo(ff,f0_model,cL1,h1_mm/1000.0,Nsup,eta11))

    ca,cb=st.columns([2,1])
    with ca:
        if st.button("Comprobar y agregar al gráfico",type="primary",key=f"{ns}_add",use_container_width=True):
            exp=expected_delta(f_reg)
            if abs(float(entered)-float(exp))<=0.15:
                answers[str(f_reg)]=round(float(exp),3)
                saved["stage6_delta_answers"]=answers
                _persist()
                st.success(f"Banda {f_reg} Hz correcta.")
                st.rerun()
            else:
                st.warning("El valor no coincide. Revisa la Parte 5 con la misma banda.")
    with cb:
        if st.button("Resetear curva",key=f"{ns}_reset",use_container_width=True):
            saved["stage6_delta_answers"]={}
            saved.pop("stage6_solution",None)
            saved["done_6"]=False
            _persist()
            st.rerun()

    completed=[ff for ff in bands if str(ff) in answers]
    st.progress(len(completed)/len(bands),text=f"Bandas completadas: {len(completed)} / {len(bands)}")

    rows=[]
    for ff in bands:
        if str(ff) in answers:
            rows.append({"Banda (Hz)":ff,"Estado":"Completada","ΔLₙ (dB)":f"{answers[str(ff)]:.1f}"})
        else:
            rows.append({"Banda (Hz)":ff,"Estado":"Pendiente","ΔLₙ (dB)":"—"})
    st.dataframe(rows,hide_index=True,use_container_width=True)

    if completed:
        pos={ff:i for i,ff in enumerate(bands)}
        x=np.array([pos[ff] for ff in completed],dtype=float)
        y=np.array([answers[str(ff)] for ff in completed],dtype=float)
        order=np.argsort(x)
        fig,ax=plt.subplots(figsize=(10.5,4.8))
        ax.plot(x[order],y[order],marker="o",linewidth=2.2,label="ΔLₙ(f) validada")
        ax.set_xticks(np.arange(len(bands)))
        ax.set_xticklabels([str(ff) for ff in bands],rotation=45,ha="right")
        ax.set_xlim(-0.4,len(bands)-0.6)
        ax.set_xlabel("Bandas de frecuencia (Hz)")
        ax.set_ylabel("Mejora ΔLₙ (dB)")
        ax.set_title("Curva de mejora construida por el alumno")
        ax.grid(True,axis="y",alpha=.22)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)
    else:
        st.info("Todavía no hay bandas validadas.")

    # ==============================================================
    # 7 · DEFECTOS
    # ==============================================================
    st.markdown("## 7 · ¿Qué pasa si la obra deja de parecerse al modelo?")
    st.write(
        "Los modelos anteriores suponen un desacople definido. "
        "Un puente rígido puede introducir un camino adicional de transmisión."
    )
    st.latex(r"K_{\mathrm{eq}}=K_{\mathrm{res}}+\sum_i K_{\mathrm{puente},i}")
    st.warning(
        "Esto no significa que el defecto sea incalculable; significa que puede quedar fuera de las hipótesis "
        "del modelo simplificado y requerir medición, FEM/SEA o un modelo de caminos estructurales."
    )

    if config=="Piso flotante sobre capa resiliente continua":
        st.markdown("### Defectos del piso laminado flotante")
        defect=st.selectbox(
            "Ejemplo de defecto",
            [
                "Contacto perimetral rígido",
                "Fijación atravesando la manta resiliente",
                "Penetración de tubería sin desacople",
                "Elemento fijo apoyado sobre el piso",
            ],
            key=f"{ns}_defect_laminado_final"
        )

        defect_data={
            "Contacto perimetral rígido":{
                "asset":"curso2_lab1_etapa6_laminado_defecto_perimetral_final.webp",
                "mechanism":"El piso laminado toca rígidamente el muro o queda comprimido por el rodapié.",
                "correction":"Mantener una junta perimetral libre y evitar contactos rígidos con muros o rodapiés."
            },
            "Fijación atravesando la manta resiliente":{
                "asset":"curso2_lab1_etapa6_laminado_defecto_fijacion_final.webp",
                "mechanism":"La fijación atraviesa el sistema flotante y crea una conexión rígida con la losa base.",
                "correction":"Eliminar o rediseñar la fijación para no atravesar el desacople resiliente."
            },
            "Penetración de tubería sin desacople":{
                "asset":"curso2_lab1_etapa6_laminado_defecto_tuberia_final.webp",
                "mechanism":"La tubería queda en contacto rígido con el piso laminado y puentea la manta resiliente.",
                "correction":"Incorporar manguito o junta resiliente alrededor de la penetración."
            },
            "Elemento fijo apoyado sobre el piso":{
                "asset":"curso2_lab1_etapa6_laminado_defecto_elemento_fijo_final.webp",
                "mechanism":"Un mueble, tabique u otro elemento fijo inmoviliza localmente el piso flotante.",
                "correction":"Evitar que elementos fijos bloqueen o conecten rígidamente el piso flotante con la estructura."
            },
        }

    else:
        st.markdown("### Defectos de la sobrelosa sobre apoyos discretos")
        defect=st.selectbox(
            "Ejemplo de defecto",
            [
                "Contacto perimetral rígido",
                "Tornillo conectando ambas masas",
                "Instalación conectando ambas masas",
            ],
            key=f"{ns}_defect_discreto_final"
        )

        defect_data={
            "Contacto perimetral rígido":{
                "asset":"curso2_lab1_etapa6_discreto_defecto_perimetral_final.webp",
                "mechanism":"La sobrelosa toca el muro y crea una ruta estructural paralela a los apoyos resilientes.",
                "correction":"Restituir la separación perimetral y evitar contacto rígido con los cerramientos."
            },
            "Tornillo conectando ambas masas":{
                "asset":"curso2_lab1_etapa6_discreto_defecto_tornillo_final.webp",
                "mechanism":"La fijación conecta rígidamente la sobrelosa con la losa base.",
                "correction":"Eliminar o rediseñar la fijación para mantener el desacople entre ambas masas."
            },
            "Instalación conectando ambas masas":{
                "asset":"curso2_lab1_etapa6_discreto_defecto_instalacion_final.webp",
                "mechanism":"La instalación rígida une la sobrelosa y la base, creando un camino mecánico paralelo.",
                "correction":"Desacoplar la instalación en penetraciones, abrazaderas y puntos de apoyo."
            },
        }

    data=defect_data[defect]
    defect_asset=ASSET_DIR/data["asset"]

    if defect_asset.exists():
        # El render ya contiene su propia señalización visual.
        # No se añaden títulos, banners ni advertencias superpuestas.
        st.image(str(defect_asset),width="stretch")

    # Explicación de la app separada del render, sin duplicar contenido visual.
    d1,d2=st.columns(2)
    with d1:
        _card(
            "Qué ocurre",
            "Camino mecánico paralelo",
            data["mechanism"]
        )
    with d2:
        _card(
            "Cómo corregirlo",
            "Restituir el desacople",
            data["correction"],
            tone="blue"
        )

    # ==============================================================
    # 8 · GUARDAR SOLUCIÓN
    # ==============================================================
    st.markdown("## 8 · Guarda la solución para la Etapa 7")
    st.write(
        "Cuando todas las bandas estén calculadas, guardaremos la solución constructiva y su curva ΔLₙ(f)."
    )

    if len(completed)==len(bands):
        delta_full=[float(answers[str(ff)]) for ff in bands]
        z1,z2,z3=st.columns(3)
        with z1: _card("Modelo",model,"Seleccionado por la configuración física.")
        with z2: _card("f₀ del modelo",f"{f0_model:.1f} Hz","Referencia dinámica de la solución.")
        with z3: _card("Curva ΔLₙ",f"{len(bands)} bandas","Lista para combinar con Lₙ,₀(f).",tone="blue")

        if st.button("Guardar solución y ΔLₙ(f)",type="primary",key=f"{ns}_save_solution"):
            data={
                "configuration":config,
                "model":model,
                "bands_hz":[int(ff) for ff in bands],
                "delta_ln_db":[round(v,3) for v in delta_full],
                "m1_surface_kg_m2":float(m1),
                "m2_surface_kg_m2":float(m2),
                "reduced_mass_kg_m2":float(mr),
                "s_dyn_MN_m3":float(s_dyn),
                "f0_general_hz":float(f0g),
                "f0_model_hz":float(f0_model),
                "rho1_kg_m3":float(rho1),
                "h1_mm":float(h1_mm),
                "updated_at":_now(),
            }
            if model=="Vér":
                data.update({
                    "support_density_per_m2":float(Nsup),
                    "cL1_m_s":float(cL1),
                    "eta11":float(eta11),
                })
            saved["stage6_solution"]=data
            saved["done_6"]=True
            _persist()
            st.success("Solución guardada. La Etapa 7 ya puede combinarla con la curva base.")

    # ==============================================================
    # CIERRE
    # ==============================================================
    st.markdown("## Cierre · Ya tenemos las dos piezas")
    cA,cB=st.columns(2)
    with cA:
        st.markdown("**De la Etapa 5**")
        st.latex(r"L_{n,0}(f)")
        st.caption("Nivel de impacto de la losa base.")
    with cB:
        st.markdown("**De la Etapa 6**")
        st.latex(r"\Delta L_n(f)")
        st.caption("Mejora prevista de la solución.")

    st.write("En la siguiente etapa combinaremos ambas:")
    st.latex(r"\boxed{L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)}")
    st.success(
        "Etapa 7: predicción completa del piso terminado."
    )

    with st.container(border=True):
        st.markdown("### Fuentes técnicas")
        st.write(
            "Vigran, T. E. (2008), *Building Acoustics*, sección de pisos flotantes, Ecs. 8.43–8.46."
        )
        st.write(
            "Cremer, Heckl & Ungar, *Structure-Borne Sound*, formulación para pisos flotantes continuos."
        )
        st.write(
            "Vér, I. L. (1971), *Impact noise isolation of composite floors*, JASA 50, 1043–1050."
        )

    if role=="Docente" and not projection_mode:
        st.markdown("---")
        st.markdown("## Vista docente · desarrollo esperado")
        st.write(
            "La etapa debe terminar en una curva ΔLₙ(f), no en Lₙ,final(f). "
            "La configuración física determina el modelo: capa continua → Cremer/Vigran; apoyos discretos → Vér."
        )
        st.write(
            "La losa base y m′₂ deben recuperarse de la Etapa 5. "
            "El estudiante calcula la solución banda por banda y la guarda para la Etapa 7."
        )

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 5",key=f"s6_prev_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=5
            st.rerun()
    with right:
        if st.button("Etapa 7 →",key=f"s6_next_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=7
            st.rerun()

def _render_course2_lab1_stage7(lab, saved):
    """Etapa 7 · Construcción y decisión sobre la curva final del piso terminado."""
    import math
    import numpy as np
    import matplotlib.pyplot as plt

    class_id=lab["id"]
    stage_selector_key=f"future_stage_{class_id}"
    role=st.session_state.get("role","Alumno")
    projection_mode=bool(st.session_state.get("projection_mode") or role=="Proyección")
    ns=f"{class_id}_s7"

    def _asset(name,caption=None):
        p=ASSET_DIR/name
        if p.exists():
            st.image(str(p),width="stretch")
            if caption: st.caption(caption)
            return True
        return False

    def _persist():
        saved["updated_7"]=_now()
        fn=globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn): fn(class_id,saved)

    def _card(title,value,text,tone="white"):
        bg="#fff" if tone=="white" else "#f3f0ff"
        bd="#dbe4ee" if tone=="white" else "#d8ccff"
        st.markdown(f"""<div style="border:1px solid {bd};border-radius:16px;padding:15px 16px;background:{bg};min-height:155px;margin-bottom:6px">
        <div style="font-weight:850;color:#0f172a">{title}</div><div style="font-size:1.45rem;font-weight:900;color:#0f172a;margin:.35rem 0">{value}</div>
        <div style="color:#64748b;line-height:1.45">{text}</div></div>""",unsafe_allow_html=True)

    baseline=saved.get("stage5_baseline") or {}
    solution=saved.get("stage6_solution") or {}

    # La dependencia Etapa 5 -> Etapa 6 -> Etapa 7 es obligatoria para el Alumno.
    # Para Docente y Proyección la etapa debe poder revisarse completa aunque aún no
    # existan resultados previos. En ese caso usamos datos demostrativos temporales.
    teacher_preview = role in ("Docente","Proyección") or projection_mode
    using_teacher_demo = False

    bands=[int(x) for x in baseline.get("bands_hz",[]) if x is not None]
    ln0=[float(x) for x in baseline.get("ln0_db",[]) if x is not None]
    sbands=[int(x) for x in solution.get("bands_hz",[]) if x is not None]
    delta=[float(x) for x in solution.get("delta_ln_db",[]) if x is not None]

    demo_bands=[125,160,200,250,315,400,500,630,800,1000,1250,1600,2000]

    if teacher_preview and (not bands or not ln0):
        bands=demo_bands[:]
        ln0=[58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,82.0]
        using_teacher_demo=True

    if teacher_preview and (not sbands or not delta):
        sbands=demo_bands[:]
        delta=[15.0,19.0,23.0,27.0,31.0,35.0,39.0,43.0,47.0,51.0,55.0,59.0,63.0]
        using_teacher_demo=True

    if not bands or not ln0:
        bands=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150]
        ln0=[]

    if sbands and sbands!=bands:
        common=[f for f in bands if f in sbands]
        idx0={f:i for i,f in enumerate(bands)}
        idxd={f:i for i,f in enumerate(sbands)}
        ln0=[ln0[idx0[f]] for f in common] if ln0 else []
        delta=[delta[idxd[f]] for f in common]
        bands=common

    ready=bool(ln0 and delta and len(ln0)==len(delta)==len(bands))

    header(
        "ETAPA 7 · LABORATORIO 1",
        "Predicción completa del piso terminado",
        "Combina la curva de la losa base con la mejora del sistema y toma una decisión de diseño.",
        show_overview=False,
        duration_minutes=85,
    )

    _asset("curso2_lab1_etapa7_cadena_fisica.webp")

    st.markdown("## 1 · Recuperamos lo que ya construiste")
    st.write("La Etapa 7 no vuelve a calcular desde cero las Etapas 5 y 6. **Recupera sus resultados guardados** y los combina por banda.")
    c1,c2,c3=st.columns(3)
    with c1:
        _card("Etapa 5 · Losa base",f"{len(ln0)} bandas" if ln0 else "Pendiente","Curva guardada Lₙ,₀(f).")
    with c2:
        _card("Etapa 6 · Mejora",f"{len(delta)} bandas" if delta else "Pendiente","Curva guardada ΔLₙ(f).")
    with c3:
        _card("Etapa 7 · Resultado","Lₙ,final(f)","Se construye restando las dos curvas banda por banda.",tone="purple")

    st.latex(r"\boxed{L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)}")
    st.info("Aquí ΔLₙ(f) ya es una **diferencia de niveles en dB**. Por eso la operación es una resta de niveles definidos de esta manera, no una resta directa de potencias lineales.")

    if using_teacher_demo:
        st.markdown(
            """
            <div style="border:1px solid #c4b5fd;background:#f5f3ff;border-radius:14px;
            padding:13px 16px;margin:.5rem 0 .9rem">
              <b>Vista docente · datos demostrativos</b><br>
              Las Etapas 5 y/o 6 aún no tienen resultados guardados en esta sesión.
              Para que puedas revisar la Etapa 7 completa, se cargaron curvas de demostración.
              <b>No corresponden a resultados de un alumno y no sustituyen las tablas reales.</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not ready and not teacher_preview:
        st.warning(
            "Para realizar esta etapa con continuidad real, primero debes guardar la curva base "
            "en la Etapa 5 y la curva de mejora en la Etapa 6."
        )
        left,right=st.columns(2)
        with left:
            if st.button("← Etapa 6",key=f"s7_prev_{class_id}",use_container_width=True):
                st.session_state[stage_selector_key]=6
                st.rerun()
        with right:
            st.button(
                "Etapa 8 →",
                disabled=True,
                use_container_width=True,
                key=f"s7_next_disabled_{class_id}"
            )
        return

    ln0_arr=np.asarray(ln0,float); delta_arr=np.asarray(delta,float); final_arr=ln0_arr-delta_arr

    # =========================================================
    # LAB A
    # =========================================================
    st.markdown("## 2 · Laboratorio A — Construye la curva final banda por banda")
    st.write("La app te entrega los dos datos obtenidos en las etapas anteriores. Tu tarea es **hacer la resta y registrar correctamente el nivel final**. Cada resultado validado agrega un punto a la curva.")
    _asset("curso2_lab1_etapa7_construccion_curva.gif","El gráfico se construye progresivamente a medida que validas bandas.")

    answers=saved.get("stage7_final_answers",{})
    if not isinstance(answers,dict): answers={}
    fsel=st.selectbox("Banda que vas a resolver",bands,key=f"{ns}_band")
    i=bands.index(fsel)
    a1,a2,a3=st.columns(3)
    with a1: _card("Losa base",f"{ln0_arr[i]:.1f} dB",f"Lₙ,₀({fsel} Hz) recuperado de Etapa 5.")
    with a2: _card("Mejora",f"{delta_arr[i]:.1f} dB",f"ΔLₙ({fsel} Hz) recuperado de Etapa 6.")
    with a3: _card("Operación",f"{ln0_arr[i]:.1f} − {delta_arr[i]:.1f}","Calcula el nivel final y escríbelo abajo.",tone="purple")

    entered=st.number_input(f"Lₙ,final({fsel} Hz) [dB]",min_value=-20.0,max_value=150.0,value=0.0,step=0.1,format="%.1f",key=f"{ns}_entered")
    b1,b2=st.columns([2,1])
    with b1:
        if st.button("Comprobar y agregar a la curva",type="primary",use_container_width=True,key=f"{ns}_check_band"):
            expected=float(final_arr[i])
            if abs(float(entered)-expected)<=0.15:
                answers[str(fsel)]=round(expected,3); saved["stage7_final_answers"]=answers; _persist(); st.success("Correcto. Banda incorporada."); st.rerun()
            else:
                st.warning("Revisa la resta banda por banda. El valor todavía no coincide.")
    with b2:
        if st.button("Resetear curva",use_container_width=True,key=f"{ns}_reset_curve"):
            saved["stage7_final_answers"]={}; saved.pop("stage7_result",None); saved["done_7"]=False; _persist(); st.rerun()

    completed=[f for f in bands if str(f) in answers]
    st.progress(len(completed)/len(bands),text=f"Bandas validadas: {len(completed)} / {len(bands)}")

    if completed:
        pos={f:i for i,f in enumerate(bands)}
        x=np.arange(len(bands))
        fig,ax=plt.subplots(figsize=(10.5,4.8))
        ax.plot(x,ln0_arr,marker="o",label="Losa base · Lₙ,₀(f)")
        xc=[pos[f] for f in completed]; yc=[answers[str(f)] for f in completed]
        order=np.argsort(xc); xc=np.asarray(xc)[order]; yc=np.asarray(yc,float)[order]
        ax.plot(xc,yc,marker="o",linewidth=2.3,label="Piso terminado · Lₙ,final(f)")
        ax.set_xticks(x); ax.set_xticklabels([str(f) if f<1000 else f"{f/1000:g}k" for f in bands],rotation=45,ha="right")
        ax.set_xlabel("Bandas de frecuencia [Hz]"); ax.set_ylabel("Nivel de ruido de impacto [dB]"); ax.set_title("Curva final construida por el alumno")
        ax.grid(True,axis="y",alpha=.22); ax.legend(); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)

    st.markdown("### Tabla de trabajo")
    st.dataframe([
        {"Banda (Hz)":f,"Lₙ,₀ (dB)":round(float(ln0_arr[j]),1),"ΔLₙ (dB)":round(float(delta_arr[j]),1),"Lₙ,final (dB)":round(float(answers[str(f)]),1) if str(f) in answers else "—"}
        for j,f in enumerate(bands)
    ],hide_index=True,use_container_width=True)

    # =========================================================
    # LAB B
    # =========================================================
    st.markdown("## 3 · Laboratorio B — Sensibilidad del diseño")
    st.write("Ahora sí puedes modificar el piso y observar **por qué cambia la curva final**. Este laboratorio no reemplaza la solución guardada de Etapa 6; es una exploración de sensibilidad.")
    model=solution.get("model","Cremer/Vigran")
    m1_ref=float(solution.get("m1_surface_kg_m2",85.0)); m2=float(solution.get("m2_surface_kg_m2",baseline.get("surface_mass_kg_m2",384.0))); s_ref=float(solution.get("s_dyn_MN_m3",12.0))
    h_ref=float(solution.get("h1_mm",40.0))
    cc1,cc2=st.columns(2)
    with cc1:
        m1_test=st.slider("Masa superficial superior m′₁ (kg/m²)",max(2.0,m1_ref*.35),max(20.0,m1_ref*2.0),m1_ref,step=1.0,key=f"{ns}_sens_m1")
    with cc2:
        s_test=st.slider("Rigidez dinámica s′ (MN/m³)",max(1.0,s_ref*.35),max(5.0,s_ref*2.2),s_ref,step=0.5,key=f"{ns}_sens_s")

    mr=(m1_test*m2)/max(m1_test+m2,1e-9)
    f0_general=(1/(2*math.pi))*math.sqrt((s_test*1e6)/mr)
    if model=="Cremer/Vigran":
        f0_model=(1/(2*math.pi))*math.sqrt((s_test*1e6)/m1_test)
        delta_test=np.asarray([max(0.0,40*math.log10(max(f/f0_model,1e-12))) for f in bands],float)
    else:
        f0_model=f0_general
        # Para la sensibilidad del modelo discreto conservamos la forma f^3 del ejercicio original.
        N=float(solution.get("support_density_per_m2",4.0)); cL=float(solution.get("cL1_m_s",3500.0)); eta=float(solution.get("eta11",0.02)); h_m=h_ref/1000.0
        vals=[]
        for f in bands:
            arg=(cL*h_m*N*eta*(f**3))/(2*(math.pi**3)*(f0_model**4))
            vals.append(max(0.0,10*math.log10(max(arg,1e-12))))
        delta_test=np.asarray(vals,float)
    final_test=ln0_arr-delta_test

    s1,s2,s3=st.columns(3)
    with s1: _card("Modelo",model,"Se conserva el tipo de sistema elegido en Etapa 6.")
    with s2: _card("f₀ calculada",f"{f0_model:.1f} Hz","Resultado dinámico de los parámetros actuales.")
    with s3: _card("Cambio medio",f"{np.mean(final_test-final_arr):+.1f} dB","Diferencia media respecto de la solución guardada.",tone="purple")

    fig,ax=plt.subplots(figsize=(10.5,4.8)); x=np.arange(len(bands))
    ax.plot(x,final_arr,marker="o",label="Solución guardada")
    ax.plot(x,final_test,marker="o",label="Solución explorada")
    ax.set_xticks(x); ax.set_xticklabels([str(f) if f<1000 else f"{f/1000:g}k" for f in bands],rotation=45,ha="right")
    ax.set_xlabel("Bandas de frecuencia [Hz]"); ax.set_ylabel("Lₙ,final [dB]"); ax.set_title("¿Cómo cambia el piso terminado?")
    ax.grid(True,axis="y",alpha=.22); ax.legend(); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    st.info("No evalúes el diseño únicamente por f₀. La decisión debe mirar la **curva final completa** y las restricciones de proyecto.")

    # =========================================================
    # LAB C
    # =========================================================
    st.markdown("## 4 · Laboratorio C — Selección profesional desde catálogos reales")
    st.write(
        "Ahora trabajarás como proyectista. El cliente no te entrega la rigidez dinámica de la solución: "
        "**debes buscarla en una ficha técnica real**, interpretar correctamente los datos y utilizarlos para diseñar el piso."
    )

    st.markdown(
        """
        <div style="border:1px solid #bfdbfe;background:#eff6ff;border-radius:16px;padding:15px 17px;margin:.5rem 0 1rem">
          <b>Encargo profesional</b><br>
          Diseña una sobrelosa flotante sobre una manta resiliente real que cumpla simultáneamente:
          <br><br>
          <b>1.</b> Nivel máximo de ruido de impacto a 500 Hz.<br>
          <b>2.</b> Carga adicional máxima permitida por el proyecto.<br>
          <b>3.</b> La carga aplicada debe ser compatible con la capacidad declarada por la manta seleccionada.
          <br><br>
          El objetivo es encontrar una solución <b>acústicamente suficiente y lo más liviana posible</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Datos ocultos para validación. El alumno NO los ve hasta leer y validar el catálogo.
    catalog_products = {
        "REGUPOL sound 15": {
            "url": "https://acoustics.regupol.com/fileadmin/user_upload/acoustics/products/documents/technical_data/en/regupol_sound/regupol_sound_15/Technical_data_REGUPOL_sound_15.pdf",
            "manufacturer": "REGUPOL",
            "thickness_mm": 12.0,
            "s_dyn": 6.0,
            "delta_lw": 29.0,
            "load_value": 30.0,
            "load_unit": "kN/m²",
            "load_kN_m2": 30.0,
        },
        "REGUPOL sound 47": {
            "url": "https://acoustics.regupol.com/fileadmin/user_upload/acoustics/products/documents/technical_data/en/regupol_sound/regupol_sound_47/Technical_data_REGUPOL_sound_47.pdf",
            "manufacturer": "REGUPOL",
            "thickness_mm": 8.0,
            "s_dyn": 30.0,
            "delta_lw": 22.0,
            "load_value": 30.0,
            "load_unit": "kN/m²",
            "load_kN_m2": 30.0,
        },
        "Getzner Acoustic Floor Mat 29": {
            "url": "https://www.getzner.com/es/productos/productos-para-la-construccion/aislamiento-acustico-de-impacto",
            "manufacturer": "Getzner",
            "thickness_mm": 11.0,
            "s_dyn": 10.0,
            "delta_lw": 29.0,
            "load_value": 5000.0,
            "load_unit": "kg/m²",
            "load_kN_m2": 5000.0 * 9.80665 / 1000.0,
        },
        "Getzner Acoustic Floor Mat 35": {
            "url": "https://www.getzner.com/media/17656/download/Data%20Sheet%20Acoustic%20Floor%20Mat%2035%20EN.pdf?v=2",
            "manufacturer": "Getzner",
            "thickness_mm": 16.0,
            "s_dyn": 5.0,
            "delta_lw": 35.0,
            "load_value": 2500.0,
            "load_unit": "kg/m²",
            "load_kN_m2": 2500.0 * 9.80665 / 1000.0,
        },
    }

    # ---------------------------------------------------------
    # C1 · Caso del proyecto
    # ---------------------------------------------------------
    st.markdown("### C1 · Restricciones del proyecto")
    st.write(
        "Estos límites pertenecen **al caso de ejercicio**; no representan por sí solos una exigencia normativa."
    )
    pc1,pc2=st.columns(2)
    with pc1:
        target500=st.number_input(
            "Nivel máximo permitido Lₙ,final a 500 Hz (dB)",
            20.0,100.0,50.0,1.0,
            key=f"{ns}_catalog_target500"
        )
    with pc2:
        max_added_mass=st.number_input(
            "Carga adicional máxima del piso (kg/m²)",
            20.0,300.0,100.0,5.0,
            key=f"{ns}_catalog_maxmass"
        )

    j500=min(range(len(bands)),key=lambda j:abs(bands[j]-500))
    base500=float(ln0_arr[j500])
    st.info(
        f"La losa base de tu proyecto, recuperada de la Etapa 5, tiene "
        f"**Lₙ,₀({bands[j500]} Hz) = {base500:.1f} dB**."
    )

    # ---------------------------------------------------------
    # C2 · Buscar datos reales
    # ---------------------------------------------------------
    st.markdown("### C2 · Elige un producto y consulta su ficha técnica")
    product_name=st.selectbox(
        "Producto resiliente a investigar",
        list(catalog_products.keys()),
        key=f"{ns}_catalog_product"
    )
    product=catalog_products[product_name]

    ca,cb=st.columns([1.35,1])
    with ca:
        st.write(
            f"Seleccionaste **{product_name}**. Abre la ficha oficial del fabricante y localiza los datos solicitados."
        )
    with cb:
        st.link_button(
            "Abrir ficha técnica oficial",
            product["url"],
            use_container_width=True
        )
        if product["manufacturer"]=="Getzner":
            st.caption(
                "Si Getzner cambia la URL del PDF, consulta la página oficial de "
                "Aislamiento acústico de impacto y abre la ficha del producto seleccionado."
            )

    st.markdown(
        """
        <div style="border:1px solid #fde68a;background:#fffbeb;border-radius:14px;padding:13px 16px;margin:.4rem 0 .8rem">
          <b>No copies todavía valores desde la app:</b> la actividad consiste en encontrarlos en la ficha.
          Busca <b>espesor</b>, <b>rigidez dinámica superficial s′</b>,
          <b>capacidad/rango de carga</b> y <b>ΔL<sub>w</sub></b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    e1,e2,e3,e4=st.columns(4)
    with e1:
        cat_h=st.number_input(
            "Espesor encontrado (mm)",
            min_value=1.0,max_value=50.0,value=10.0,step=0.5,
            key=f"{ns}_cat_h"
        )
    with e2:
        cat_s=st.number_input(
            "s′ encontrado (MN/m³)",
            min_value=0.5,max_value=100.0,value=10.0,step=0.5,
            key=f"{ns}_cat_s"
        )
    with e3:
        cat_load=st.number_input(
            f"Capacidad/rango de carga ({product['load_unit']})",
            min_value=1.0,max_value=10000.0,
            value=30.0 if product["load_unit"]=="kN/m²" else 2500.0,
            step=1.0 if product["load_unit"]=="kN/m²" else 100.0,
            key=f"{ns}_cat_load"
        )
    with e4:
        cat_dlw=st.number_input(
            "ΔLw declarado (dB)",
            min_value=1.0,max_value=60.0,value=25.0,step=1.0,
            key=f"{ns}_cat_dlw"
        )

    catalog_valid=saved.get("stage7_catalog_validated_product")==product_name

    if st.button(
        "Comprobar datos del catálogo",
        type="primary",
        use_container_width=True,
        key=f"{ns}_catalog_validate"
    ):
        checks = {
            "Espesor": abs(float(cat_h)-product["thickness_mm"]) <= 0.25,
            "Rigidez dinámica s′": abs(float(cat_s)-product["s_dyn"]) <= 0.25,
            "Carga": abs(float(cat_load)-product["load_value"]) <= max(0.2,product["load_value"]*0.015),
            "ΔLw": abs(float(cat_dlw)-product["delta_lw"]) <= 0.25,
        }
        if all(checks.values()):
            saved["stage7_catalog_validated_product"]=product_name
            saved["stage7_catalog_extracted"]={
                "product":product_name,
                "thickness_mm":float(product["thickness_mm"]),
                "s_dyn_MN_m3":float(product["s_dyn"]),
                "declared_load_value":float(product["load_value"]),
                "declared_load_unit":product["load_unit"],
                "delta_lw_db":float(product["delta_lw"]),
            }
            _persist()
            st.success("Datos correctos. Ya puedes usar este producto en el diseño.")
            st.rerun()
        else:
            wrong=[k for k,v in checks.items() if not v]
            st.warning("Revisa en la ficha técnica: " + ", ".join(wrong) + ".")

    catalog_valid=saved.get("stage7_catalog_validated_product")==product_name
    if not catalog_valid:
        st.info("Valida correctamente los datos del catálogo para desbloquear el diseño.")
    else:
        st.success(f"Catálogo validado: {product_name}")

        # Mostrar lo que el alumno ya encontró, ahora como datos activos del modelo.
        v1,v2,v3,v4=st.columns(4)
        with v1: _card("Espesor de manta",f"{product['thickness_mm']:.0f} mm","Dato extraído de la ficha.")
        with v2: _card("Rigidez dinámica s′",f"{product['s_dyn']:.1f} MN/m³","Dato que alimentará el modelo espectral.",tone="blue")
        with v3: _card("Capacidad declarada",f"{product['load_value']:g} {product['load_unit']}","Se usará para comprobar compatibilidad de carga.")
        with v4: _card("ΔLw del fabricante",f"{product['delta_lw']:.0f} dB","Índice ponderado declarado. No sustituye ΔLₙ(f).")

        st.warning(
            "ΔLw es un **índice ponderado de referencia del producto**. "
            "No lo introducimos directamente en la ecuación de ΔLₙ(500 Hz). "
            "Para nuestra predicción espectral utilizaremos s′."
        )

        # -----------------------------------------------------
        # C3 · Diseñar la sobrelosa
        # -----------------------------------------------------
        st.markdown("### C3 · Diseña la sobrelosa flotante")
        st.write(
            "Ahora debes elegir la masa superior. Para una sobrelosa homogénea, la carga adicional por unidad de superficie es:"
        )
        st.latex(r"\boxed{m_1'=\rho_1\,h_1}")
        st.caption(
            "ρ₁ en kg/m³ · h₁ en m · m′₁ en kg/m². "
            "En este ejercicio despreciamos la pequeña masa propia de la manta para concentrarnos en la sobrelosa."
        )

        sc1,sc2=st.columns(2)
        with sc1:
            screed_rho=st.selectbox(
                "Material de la sobrelosa",
                [
                    "Mortero cementicio liviano · 1600 kg/m³",
                    "Mortero cementicio · 2000 kg/m³",
                    "Hormigón · 2300 kg/m³",
                ],
                index=1,
                key=f"{ns}_screed_material"
            )
        rho_map={
            "Mortero cementicio liviano · 1600 kg/m³":1600.0,
            "Mortero cementicio · 2000 kg/m³":2000.0,
            "Hormigón · 2300 kg/m³":2300.0,
        }
        rho1=rho_map[screed_rho]
        with sc2:
            screed_h_mm=st.slider(
                "Espesor de sobrelosa h₁ (mm)",
                25,100,40,5,
                key=f"{ns}_screed_h"
            )

        h1_m=screed_h_mm/1000.0
        m1_design=rho1*h1_m
        applied_load_kN_m2=m1_design*9.80665/1000.0

        st.latex(
            fr"""m_1'={rho1:.0f}\cdot {h1_m:.3f}
            ={m1_design:.1f}\;\mathrm{{kg/m^2}}"""
        )

        # -----------------------------------------------------
        # C4 · Acústica
        # -----------------------------------------------------
        st.markdown("### C4 · Calcula el desempeño acústico a 500 Hz")
        s_used=float(product["s_dyn"])
        f0_design=(1/(2*math.pi))*math.sqrt((s_used*1e6)/max(m1_design,1e-12))
        delta500=max(0.0,40*math.log10(max(bands[j500]/f0_design,1e-12)))
        final500=base500-delta500

        ac1,ac2,ac3=st.columns(3)
        with ac1:
            _card("Frecuencia natural",f"{f0_design:.1f} Hz","Calculada con m′₁ y s′ del producto.")
        with ac2:
            _card(f"ΔLₙ({bands[j500]} Hz)",f"{delta500:.1f} dB","Mejora espectral predicha por el modelo.")
        with ac3:
            _card(f"Lₙ,final({bands[j500]} Hz)",f"{final500:.1f} dB","Nivel final estimado del piso.",tone="purple")

        st.markdown("**Sustitución utilizada**")
        st.latex(
            fr"""f_{{0,\mathrm{{cont}}}}
            =\frac{{1}}{{2\pi}}\sqrt{{\frac{{{s_used:.1f}\times10^6}}{{{m1_design:.1f}}}}}
            ={f0_design:.1f}\;\mathrm{{Hz}}"""
        )
        st.latex(
            fr"""\Delta L_n({bands[j500]})
            =40\log_{{10}}\left(\frac{{{bands[j500]}}}{{{f0_design:.1f}}}\right)
            ={delta500:.1f}\;\mathrm{{dB}}"""
        )
        st.latex(
            fr"""L_{{n,\mathrm{{final}}}}({bands[j500]})
            ={base500:.1f}-{delta500:.1f}
            ={final500:.1f}\;\mathrm{{dB}}"""
        )

        # -----------------------------------------------------
        # C5 · Tres verificaciones
        # -----------------------------------------------------
        st.markdown("### C5 · ¿La solución es profesionalmente viable?")
        acoustic_ok=final500 <= target500
        project_load_ok=m1_design <= max_added_mass
        product_load_ok=applied_load_kN_m2 <= product["load_kN_m2"]

        vr1,vr2,vr3=st.columns(3)
        with vr1:
            _card(
                "Criterio acústico",
                "Cumple" if acoustic_ok else "No cumple",
                f"{final500:.1f} dB frente al máximo de {target500:.1f} dB.",
                tone="purple" if acoustic_ok else "white"
            )
        with vr2:
            _card(
                "Carga del proyecto",
                "Cumple" if project_load_ok else "No cumple",
                f"m′₁ = {m1_design:.1f} kg/m² frente al máximo de {max_added_mass:.1f} kg/m²."
            )
        with vr3:
            _card(
                "Compatibilidad de la manta",
                "Cumple" if product_load_ok else "No cumple",
                f"Carga aplicada ≈ {applied_load_kN_m2:.2f} kN/m²; debe estar dentro del rango declarado.",
                tone="blue" if product_load_ok else "white"
            )

        viable_catalog=acoustic_ok and project_load_ok and product_load_ok
        if viable_catalog:
            st.success(
                "SOLUCIÓN VIABLE: cumple acústica, carga máxima del proyecto y capacidad declarada de la manta."
            )
        else:
            st.warning(
                "La solución todavía no es viable. Cambia producto, material o espesor de sobrelosa y vuelve a comprobar."
            )

        # -----------------------------------------------------
        # C6 · Registrar intentos y comparar
        # -----------------------------------------------------
        st.markdown("### C6 · Registra tus alternativas")
        attempts=saved.get("stage7_catalog_attempts",[])
        if not isinstance(attempts,list):
            attempts=[]

        if st.button(
            "Guardar este intento",
            use_container_width=True,
            key=f"{ns}_save_catalog_attempt"
        ):
            attempt={
                "Producto":product_name,
                "Sobrelosa":screed_rho.split(" · ")[0],
                "h₁ (mm)":int(screed_h_mm),
                "m′₁ (kg/m²)":round(m1_design,1),
                "s′ (MN/m³)":round(s_used,1),
                "f₀ (Hz)":round(f0_design,1),
                f"Lₙ,final {bands[j500]} Hz (dB)":round(final500,1),
                "Acústica":"Cumple" if acoustic_ok else "No cumple",
                "Carga proyecto":"Cumple" if project_load_ok else "No cumple",
                "Carga producto":"Cumple" if product_load_ok else "No cumple",
                "Viable":"Sí" if viable_catalog else "No",
            }
            attempts.append(attempt)
            saved["stage7_catalog_attempts"]=attempts[-20:]
            _persist()
            st.success("Intento registrado.")
            st.rerun()

        attempts=saved.get("stage7_catalog_attempts",[])
        if attempts:
            st.dataframe(attempts,hide_index=True,use_container_width=True)

            viable_attempts=[a for a in attempts if a.get("Viable")=="Sí"]
            if viable_attempts:
                lightest=min(viable_attempts,key=lambda a:float(a["m′₁ (kg/m²)"]))
                st.success(
                    f"Mejor solución viable registrada hasta ahora: "
                    f"**{lightest['Producto']}**, {lightest['h₁ (mm)']} mm de sobrelosa, "
                    f"m′₁ = {lightest['m′₁ (kg/m²)']} kg/m²."
                )
            else:
                st.info("Todavía no has registrado una alternativa que cumpla los tres criterios.")

        if st.button(
            "Resetear intentos del Laboratorio C",
            key=f"{ns}_reset_catalog_attempts"
        ):
            saved["stage7_catalog_attempts"]=[]
            saved.pop("stage7_catalog_validated_product",None)
            saved.pop("stage7_catalog_extracted",None)
            _persist()
            st.rerun()

    st.markdown(
        """
        <div style="border:1px solid #dbe4ee;border-radius:16px;padding:14px 16px;background:#fff;margin-top:1rem">
          <b>Lectura profesional:</b> una manta con menor s′ puede ayudar a reducir la frecuencia natural,
          pero la solución final no se decide por un único parámetro. Debes comprobar
          <b>Lₙ,final(f)</b>, la masa añadida, la capacidad de carga del producto y las hipótesis del modelo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if teacher_preview and using_teacher_demo:
        st.info(
            "Modo revisión docente: todos los controles de esta etapa están disponibles. "
            "Cuando existan curvas reales guardadas en Etapas 5 y 6, la Etapa 7 las utilizará automáticamente."
        )

    # =========================================================
    # SAVE / CLOSING
    # =========================================================
    st.markdown("## 5 · Cierre — Guarda la predicción completa")
    if len(completed)==len(bands):
        st.success("Has construido correctamente todas las bandas de Lₙ,final(f).")
        if st.button("Guardar curva final y decisión",type="primary",use_container_width=True,key=f"{ns}_save"):
            saved["stage7_result"]={
                "bands_hz":[int(f) for f in bands],
                "ln0_db":[round(float(v),3) for v in ln0_arr],
                "delta_ln_db":[round(float(v),3) for v in delta_arr],
                "ln_final_db":[round(float(v),3) for v in final_arr],
                "source_stage5":True,"source_stage6":True,
                "model":model,
                "decision_exploration":{"m1_kg_m2":float(m1_test),"s_dyn_MN_m3":float(s_test),"f0_hz":float(f0_model),"viable":bool(viable)},
                "updated_at":_now(),
            }
            saved["done_7"]=True; _persist(); st.success("Etapa 7 guardada. Ya existe una curva final completa para continuar.")
    else:
        st.info("Completa todas las bandas del Laboratorio A para habilitar el guardado final.")

    st.latex(r"\boxed{L_{n,0}(f)-\Delta L_n(f)=L_{n,\mathrm{final}}(f)}")
    st.write("La Etapa 7 termina en una **curva espectral completa del piso terminado**. No calculamos todavía un número único ni promedios normativos.")
    st.success("Etapa 8: pasaremos desde el piso terminado a medidas de control de ruido y vibraciones en instalaciones.")

    if role=="Docente" and not projection_mode:
        with st.container(border=True):
            st.markdown("### Vista docente · objetivo de la etapa")
            st.write("El estudiante debe demostrar que sabe combinar resultados previos, construir Lₙ,final(f) por bandas y justificar una decisión considerando desempeño acústico y restricciones del caso.")

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 6",key=f"s7_prev_{class_id}",use_container_width=True): st.session_state[stage_selector_key]=6; st.rerun()
    with right:
        if st.button("Etapa 8 →",key=f"s7_next_{class_id}",use_container_width=True): st.session_state[stage_selector_key]=8; st.rerun()


def _render_course2_lab1_stage8(lab, saved):
    """Etapa 8 — Diagnóstico y control profesional del ruido de instalaciones."""
    import math
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    class_id=lab["id"]
    role=st.session_state.get("role","Alumno")
    ns=f"{class_id}_s8"

    # ---------------------------------------------------------
    # CASO ÚNICO · TODA LA ETAPA 8
    # ---------------------------------------------------------
    CASE_VERSION="lowara_shos_50_125_75_v1"
    CASE_MODEL="Lowara SHOS 50-125/75/P"
    CASE_SERIES="Lowara SHOE–SHOS–SHOD 50-125/75"
    CASE_RPM=2900.0
    CASE_F_ROT=CASE_RPM/60.0
    CASE_BAND_HZ=50.0
    CASE_Q=48.0
    CASE_MOTOR_KW=7.5
    CASE_MASS_KG=79.0
    CASE_SUPPORTS=4
    CASE_NPSHR=3.8

    # ---------------------------------------------------------
    # Restauración de controles guardados del alumno
    # ---------------------------------------------------------
    def _json_safe(value):
        if value is None or isinstance(value,(str,int,float,bool)):
            return value
        if isinstance(value,(list,tuple)):
            out=[]
            for x in value:
                sx=_json_safe(x)
                if sx is not None:
                    out.append(sx)
            return out
        if isinstance(value,dict):
            out={}
            for k,v in value.items():
                sv=_json_safe(v)
                if sv is not None:
                    out[str(k)]=sv
            return out
        return None

    _action_fragments=(
        "_save","_check","_add","_clear","_execute","_reset","_validate",
        "_next","_prev","_back","_run","_guardar","_comprobar"
    )

    ui_saved=saved.get("stage8_ui_state",{})
    if isinstance(ui_saved,dict):
        for _k,_v in ui_saved.items():
            if (
                isinstance(_k,str)
                and _k.startswith(ns)
                and not any(frag in _k for frag in _action_fragments)
                and _k not in st.session_state
            ):
                st.session_state[_k]=_v

    # Compatibilidad con alumnos que ya habían guardado resultados antes
    _npsh_old=saved.get("stage8_npsh_case",{})
    if isinstance(_npsh_old,dict) and _npsh_old.get("validated"):
        st.session_state.setdefault(f"{ns}_npsha_student",float(_npsh_old.get("npsha_m",0.0)))
        st.session_state.setdefault(f"{ns}_npshr_student",float(_npsh_old.get("npshr_m",0.0)))
        st.session_state.setdefault(f"{ns}_npsh_margin_student",float(_npsh_old.get("margin_m",0.0)))

    _diag_old=saved.get("stage8_diagnosis",{})
    if isinstance(_diag_old,dict):
        if isinstance(_diag_old.get("mechanisms"),list):
            st.session_state.setdefault(f"{ns}_diag_mech_final",_diag_old["mechanisms"])
        if _diag_old.get("dominant_path"):
            st.session_state.setdefault(f"{ns}_diag_path_final",_diag_old["dominant_path"])
        if _diag_old.get("reasoning"):
            st.session_state.setdefault(f"{ns}_diag_reason_final",_diag_old["reasoning"])

    _iso_old=saved.get("stage8_isolator_design",{})
    if isinstance(_iso_old,dict) and _iso_old.get("saved"):
        st.session_state.setdefault(f"{ns}_iso_rpm",int(round(_iso_old.get("rpm",CASE_RPM))))
        st.session_state.setdefault(f"{ns}_iso_mass",int(round(_iso_old.get("mass_kg",CASE_MASS_KG))))
        st.session_state.setdefault(f"{ns}_iso_supports",int(round(_iso_old.get("supports",CASE_SUPPORTS))))
        st.session_state.setdefault(f"{ns}_iso_zeta",float(_iso_old.get("zeta",0.08)))
        st.session_state.setdefault(f"{ns}_iso_component",_iso_old.get("component","1×RPM"))
        st.session_state.setdefault(f"{ns}_iso_target",int(round(_iso_old.get("target_isolation_pct",90))))
        st.session_state.setdefault(f"{ns}_iso_delta",float(_iso_old.get("candidate_deflection_mm",50.0)))

    _cat_old=saved.get("stage8_catalog_result",{})
    if isinstance(_cat_old,dict) and _cat_old.get("model"):
        st.session_state.setdefault(f"{ns}_cat_model",_cat_old["model"])
        st.session_state.setdefault(f"{ns}_cat_lb",float(_cat_old.get("rated_load_lb",900.0)))
        st.session_state.setdefault(f"{ns}_cat_def",float(_cat_old.get("rated_deflection_in",4.0)))

    def _asset(name,caption=None):
        p=ASSET_DIR/name
        if p.exists():
            st.image(str(p),width="stretch")
            if caption: st.caption(caption)
            return True
        return False

    def _persist():
        # Guardar también el estado de controles para reconstruir la sesión del alumno.
        ui_state={}
        for _k,_v in list(st.session_state.items()):
            if (
                isinstance(_k,str)
                and _k.startswith(ns)
                and not any(frag in _k for frag in _action_fragments)
            ):
                _sv=_json_safe(_v)
                if _sv is not None:
                    ui_state[_k]=_sv
        saved["stage8_ui_state"]=ui_state
        saved["updated_8"]=_now()
        fn=globals().get("_save_future_state_impl") or globals().get("_save_future_state")
        if callable(fn): fn(class_id,saved)

    # Si el alumno tenía respuestas de la versión anterior (1500 RPM), se reinician
    # solo los datos incompatibles de Etapa 8. Esto ocurre una sola vez.
    if saved.get("stage8_case_version") != CASE_VERSION:
        for _old_key in [
            "stage8_ui_state","stage8_npsh_case","stage8_measurement_plan",
            "stage8_campaign_executed","stage8_evidence","stage8_diagnosis",
            "stage8_isolator_design","stage8_catalog_validated",
            "stage8_catalog_lookup","stage8_catalog_result"
        ]:
            saved.pop(_old_key,None)
        for _ssk in list(st.session_state.keys()):
            if isinstance(_ssk,str) and _ssk.startswith(ns):
                st.session_state.pop(_ssk,None)
        saved["stage8_case_version"]=CASE_VERSION
        saved["stage8_case"]={
            "model":CASE_MODEL,
            "series":CASE_SERIES,
            "rpm":CASE_RPM,
            "f_rot_hz":CASE_F_ROT,
            "spectral_band_hz":CASE_BAND_HZ,
            "flow_m3_h":CASE_Q,
            "motor_kw":CASE_MOTOR_KW,
            "mass_kg":CASE_MASS_KG,
            "supports":CASE_SUPPORTS,
        }
        _persist()

    def _card(title,value,text,tone="white"):
        palette={
            "white":("#ffffff","#dbe4ee"),
            "blue":("#eff6ff","#bfdbfe"),
            "green":("#f0fdf4","#bbf7d0"),
            "orange":("#fff7ed","#fed7aa"),
            "purple":("#f5f3ff","#ddd6fe"),
        }
        bg,bd=palette.get(tone,palette["white"])
        st.markdown(
            f"""<div style="border:1px solid {bd};border-radius:16px;padding:15px 16px;
            background:{bg};min-height:145px;margin-bottom:8px">
            <div style="font-weight:850;color:#0f172a">{title}</div>
            <div style="font-size:1.3rem;font-weight:900;color:#0f172a;margin:.35rem 0">{value}</div>
            <div style="color:#64748b;line-height:1.45">{text}</div></div>""",
            unsafe_allow_html=True
        )

    def fe_rpm(rpm):
        return max(float(rpm),0.0)/60.0

    def fn_delta(delta_mm):
        dm=max(float(delta_mm)/1000.0,1e-12)
        return (1/(2*math.pi))*math.sqrt(9.81/dm)

    def tf_force(r,z):
        r=float(r); z=max(float(z),0.0)
        return math.sqrt((1+(2*z*r)**2)/max((1-r*r)**2+(2*z*r)**2,1e-12))

    def _format_band_axis(ax, freqs):
        """Eje logarítmico con cada banda visible para lectura didáctica."""
        labels=[]
        for f in freqs:
            if abs(float(f)-round(float(f)))<1e-9:
                labels.append(str(int(round(float(f)))))
            else:
                labels.append(str(float(f)).replace(".",","))
        ax.set_xscale("log")
        ax.set_xticks(freqs)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_xlim(float(freqs[0])*0.92, float(freqs[-1])*1.08)
        ax.tick_params(axis="x", which="minor", bottom=False, labelbottom=False)

    header(
        "ETAPA 8 · LABORATORIO 1",
        "DIAGNÓSTICO Y CONTROL VIBROACÚSTICO DE UNA BOMBA CENTRÍFUGA",
        "Desarrollar un único caso profesional desde el diagnóstico hasta la selección real del aislador.",
        show_overview=False
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:.35rem 0 1rem">
          <div style="background:#fff;border:1px solid #dbe4ee;border-radius:16px;padding:16px">
            <div style="font-size:.78rem;font-weight:900;color:#2563eb;letter-spacing:.05em">DIAGNOSTICARÁS</div>
            <div style="font-size:1.05rem;font-weight:850;color:#0f172a;margin-top:.35rem">Qué está generando el problema</div>
            <div style="color:#64748b;margin-top:.35rem">Separarás excitación rotacional, condición hidráulica, transmisión estructural, tuberías y radiación aérea.</div>
          </div>
          <div style="background:#fff;border:1px solid #dbe4ee;border-radius:16px;padding:16px">
            <div style="font-size:.78rem;font-weight:900;color:#0f766e;letter-spacing:.05em">COMPROBARÁS</div>
            <div style="font-size:1.05rem;font-weight:850;color:#0f172a;margin-top:.35rem">Por dónde se transmite</div>
            <div style="color:#64748b;margin-top:.35rem">Usarás mediciones para distinguir base/losa, tuberías, campo acústico y condición hidráulica.</div>
          </div>
          <div style="background:#fff;border:1px solid #dbe4ee;border-radius:16px;padding:16px">
            <div style="font-size:.78rem;font-weight:900;color:#9333ea;letter-spacing:.05em">DISEÑARÁS</div>
            <div style="font-size:1.05rem;font-weight:850;color:#0f172a;margin-top:.35rem">Una estrategia verificable</div>
            <div style="color:#64748b;margin-top:.35rem">Cada medida deberá responder a un mecanismo y a un camino confirmado.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="border:1px solid #bfdbfe;background:linear-gradient(90deg,#eff6ff,#ffffff);
        border-radius:18px;padding:16px 18px;margin:.4rem 0 1rem">
          <div style="font-size:.78rem;font-weight:900;color:#2563eb;letter-spacing:.06em">CASO ÚNICO · ETAPA 8</div>
          <div style="font-size:1.25rem;font-weight:900;color:#0f172a;margin:.25rem 0">{CASE_MODEL}</div>
          <div style="color:#475569;line-height:1.55">
            La misma bomba se mantiene en <b>Laboratorio A</b>, análisis de <b>NPSH/cavitación</b>,
            <b>Laboratorio B</b> y selección comercial del <b>Laboratorio C</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    case1,case2,case3,case4=st.columns(4)
    with case1:
        _card("Velocidad",f"{CASE_RPM:.0f} RPM",f"1×RPM = {CASE_F_ROT:.1f} Hz.",tone="blue")
    with case2:
        _card("Motor",f"{CASE_MOTOR_KW:.1f} kW","Potencia nominal asociada al modelo del caso.")
    with case3:
        _card("Masa del conjunto",f"{CASE_MASS_KG:.0f} kg","Peso de catálogo de la variante SHOS 50-125/75/P.",tone="green")
    with case4:
        _card("Punto hidráulico",f"{CASE_Q:.0f} m³/h","Caudal utilizado para la lectura de NPSHᵣ.",tone="purple")

    st.caption(
        "Para el dimensionamiento antivibratorio se adoptan **4 apoyos con reparto uniforme** como hipótesis del ejercicio. "
        "Si se agrega una bancada de inercia, su masa debe sumarse y la carga por apoyo debe recalcularse."
    )
    st.markdown(
        """
        <style>
        .s8-route{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:.4rem 0 .7rem}
        .s8-step{position:relative;background:#fff;border:1px solid #d8e3ef;border-radius:15px;padding:13px 13px 14px;min-height:104px}
        .s8-step:not(:last-child):after{content:'→';position:absolute;right:-10px;top:37px;color:#7890aa;font-weight:900;font-size:1.15rem;z-index:3}
        .s8-num{font-size:.72rem;font-weight:900;color:#2563eb;letter-spacing:.06em}
        .s8-title{font-size:.94rem;font-weight:900;color:#0f2748;margin:.18rem 0}
        .s8-sub{font-size:.79rem;color:#64748b;line-height:1.3}
        .s8-principle{border:1px solid #bcd2ed;background:linear-gradient(90deg,#f4f8ff,#eef7ff);border-radius:15px;padding:13px 16px;margin:0 0 1rem;color:#17365d}
        @media(max-width:900px){.s8-route{grid-template-columns:1fr}.s8-step:not(:last-child):after{display:none}}
        </style>
        <div class="s8-route">
          <div class="s8-step"><div class="s8-num">01</div><div class="s8-title">EQUIPO</div><div class="s8-sub">¿Qué instalación tengo y en qué condición opera?</div></div>
          <div class="s8-step"><div class="s8-num">02</div><div class="s8-title">MECANISMO</div><div class="s8-sub">¿Qué genera realmente el ruido o la vibración?</div></div>
          <div class="s8-step"><div class="s8-num">03</div><div class="s8-title">CAMINO</div><div class="s8-sub">¿Por dónde llega la energía al receptor?</div></div>
          <div class="s8-step"><div class="s8-num">04</div><div class="s8-title">MEDIDA</div><div class="s8-sub">¿Dónde conviene actuar para cortar el problema?</div></div>
          <div class="s8-step"><div class="s8-num">05</div><div class="s8-title">VERIFICACIÓN</div><div class="s8-sub">¿La solución redujo el mecanismo o camino dominante?</div></div>
        </div>
        <div class="s8-principle"><b>Principio de diagnóstico:</b> no selecciones una medida de control antes de identificar <b>qué genera el problema</b> y <b>por qué camino llega al receptor</b>. &nbsp; Diagnosticar primero → controlar después.</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================
    # 1 · SISTEMA COMPLETO
    # =========================================================
    st.markdown("## 1 · Un equipo no es una fuente aislada: forma parte de un sistema")
    st.write(
        "Una instalación debe analizarse como un sistema completo. Un mismo equipo puede generar ruido por aire, "
        "introducir fuerzas en la estructura y transmitir vibración a través de tuberías, ductos o soportes."
    )
    _asset(
        "curso2_lab1_etapa8_sistema_profesional.webp",
        "La bomba está conectada a su red hidráulica; la ventilación de la sala es un sistema independiente."
    )

    st.markdown("### 1.1 · Antes de diagnosticar: identifica las partes de la bomba")
    st.write(
        "Para interpretar después RPM, cavitación, NPSH y vibración necesitas reconocer primero qué ocurre físicamente "
        "dentro del conjunto bomba–motor. La sección transversal muestra el recorrido del líquido y los componentes principales."
    )
    _asset(
        "curso2_lab1_etapa8_bomba_seccion_transversal.webp",
        "Sección transversal didáctica de una bomba centrífuga y su conjunto motor."
    )
    st.markdown(
        """
        **Recorrido básico del líquido:** succión → ojo del impulsor → impulsor → voluta → descarga.

        **Componentes que aparecerán después en el diagnóstico:** impulsor, eje, sello, rodamientos, acoplamiento,
        motor, bridas, tuberías y base del conjunto.
        """
    )

    zone=st.radio(
        "Selecciona qué parte del problema quieres revisar",
        ["Fuente / bomba","Base y losa","Tuberías y conexiones","Radiación aérea","Receptor"],
        horizontal=True,key=f"{ns}_zone"
    )

    if zone=="Fuente / bomba":
        st.markdown("### Actuar en la fuente · reducir lo que nace en el equipo")
        st.write(
            "Controlar en la fuente significa modificar la **selección, operación o condición física del equipo** para que "
            "genere menos fuerza dinámica, turbulencia, pulsaciones o ruido antes de que la energía entre a los caminos de transmisión."
        )
        f1,f2,f3=st.columns(3)
        with f1:
            _card("Selección y punto de operación","Evitar generar de más",
                  "Seleccionar equipos con datos acústicos adecuados; evitar sobredimensionamiento; operar bombas y ventiladores cerca de su zona eficiente; reducir RPM con variador cuando el proceso lo permita.",tone="blue")
            _card("Condición mecánica","Rotor / eje / acoplamiento",
                  "Balanceo dinámico, alineación motor–bomba, revisión de rodamientos, holguras, acoplamientos, correas y piezas sueltas. Un aislador no corrige un rotor desequilibrado.")
        with f2:
            _card("Condición hidráulica","Bombas",
                  "Revisar caudal, presión de succión, NPSH, válvulas, obstrucciones y pérdidas en aspiración. Evitar cavitación y pulsaciones hidráulicas.",tone="green")
            _card("Condición aerodinámica","Ventiladores / ductos",
                  "Reducir velocidad excesiva, evitar entrada distorsionada, codos inmediatos, transiciones abruptas y grandes pérdidas de presión que regeneren ruido.")
        with f3:
            _card("Mantenimiento","Conservar la condición de diseño",
                  "Lubricación, limpieza de impulsor/ventilador, tensión de correas, rodamientos, filtros, válvulas y aprietes. El deterioro puede aumentar ruido aunque el aislamiento sea correcto.",tone="orange")
            st.markdown("**Ejemplo técnico**")
            st.latex(r"f_{1\times}=\frac{\mathrm{RPM}}{60}")
            st.caption(f"{CASE_RPM:.0f} RPM → {CASE_F_ROT:.1f} Hz. En los espectros por bandas, esta componente aparece principalmente en la banda central de {CASE_BAND_HZ:.0f} Hz.")

        st.markdown("#### ¿Qué significan estas acciones en la práctica?")
        source_terms=pd.DataFrame([
            ["Balanceo", "Corregir la distribución de masa de una pieza giratoria para reducir fuerzas periódicas al rotar."],
            ["Alineación", "Ajustar la posición relativa de los ejes del motor y de la bomba para evitar esfuerzos y vibraciones adicionales."],
            ["Punto de operación", "Trabajar en una zona de caudal y presión adecuada para el equipo, evitando condiciones ineficientes o inestables."],
            ["Condición hidráulica", "Revisar presión de succión, caudal, pérdidas y margen NPSH para evitar cavitación o pulsaciones."],
            ["Mantenimiento", "Conservar rodamientos, acoplamientos, impulsor, válvulas y fijaciones en la condición prevista de diseño."],
        ],columns=["Concepto","Qué significa"])
        st.dataframe(source_terms,hide_index=True,use_container_width=True)

        st.markdown("#### Fuente y camino no son lo mismo")
        sf1,sf2=st.columns(2)
        with sf1:
            _card(
                "Actuar en la fuente",
                "Generar menos",
                "Ejemplos: corregir cavitación, balancear un conjunto giratorio, alinear motor–bomba o reducir una velocidad excesiva cuando el proceso lo permita.",
                tone="green"
            )
        with sf2:
            _card(
                "Actuar en el camino",
                "Transmitir menos",
                "Ejemplos: resortes bajo la bomba, conexiones flexibles, soportes resilientes, silenciadores o tratamientos del recinto.",
                tone="blue"
            )
        st.info(
            "En esta parte no necesitas memorizar términos de mecánica. Lo importante es distinguir si una medida "
            "**reduce lo que genera el equipo** o si **reduce la energía que se transmite después**."
        )

    elif zone=="Base y losa":
        st.markdown("### Camino estructural · reducir la fuerza que entra al edificio")
        c1,c2,c3=st.columns(3)
        with c1: _card("Aislamiento vibratorio","Resortes / elastómeros","Seleccionar por frecuencia perturbadora, frecuencia natural, deflexión y carga real; no solo por tipo de material.",tone="green")
        with c2: _card("Bancada y soporte","Controlar movimiento","Una base de inercia puede estabilizar conjuntos y distribuir cargas, pero debe integrarse con el sistema de aislación.")
        with c3: _card("Evitar puentes","Revisar montaje","Pernos, anclajes, tuberías, ductos y apoyos rígidos pueden crear caminos paralelos y anular parte del aislamiento.",tone="orange")

    elif zone=="Radiación aérea":
        st.markdown("### Radiación aérea · ruido emitido por la bomba y el motor")
        c1,c2,c3=st.columns(3)
        with c1:
            _card("Carcasa y motor","emisión directa","Las superficies vibrantes pueden radiar sonido al recinto técnico.",tone="blue")
        with c2:
            _card("Campo de la sala","reverberación","La absorción puede reducir acumulación sonora, pero no corrige una fuente mecánica o hidráulica.")
        with c3:
            _card("Envolvente","transmisión aérea","Puertas, muros y penetraciones condicionan cuánto sonido aéreo llega a recintos vecinos.",tone="orange")

    elif zone=="Tuberías y conexiones":
        st.markdown("### Tuberías y conexiones · evitar caminos mecánicos paralelos")
        c1,c2,c3=st.columns(3)
        with c1: _card("Conectores flexibles","Bomba–tubería","Desacoplan movimientos y reducen transferencia mecánica cuando están correctamente dimensionados e instalados.",tone="green")
        with c2: _card("Soportes resilientes","Tuberías","Evitan que la vibración del servicio se inyecte directamente en muros, losas o estructuras auxiliares.")
        with c3: _card("Penetraciones","Manguitos y sellos","Una penetración rígida puede puentear el sistema; el detalle constructivo forma parte de la solución.",tone="orange")

    else:
        st.markdown("### Receptor · comprobar qué llega realmente al dormitorio")
        c1,c2,c3=st.columns(3)
        with c1: _card("Ubicación","Alejar receptores sensibles","Separar salas técnicas de dormitorios, estudios u otros espacios críticos reduce la exigencia sobre tratamientos posteriores.",tone="blue")
        with c2: _card("Recinto técnico","Absorción y envolvente","Absorción reduce acumulación reverberante; cerramientos y puertas controlan transmisión aérea hacia espacios vecinos.")
        with c3: _card("Operación","Horario y mantenimiento","Una estrategia profesional también considera periodos sensibles, accesibilidad, ventilación, mantenimiento y verificación posterior.",tone="green")


    # =========================================================
    # 2 · LAB A: DIAGNÓSTICO
    # =========================================================
    st.markdown("## 2 · Laboratorio A — Diagnóstico de una bomba centrífuga")
    st.markdown(
        """
        **Caso profesional.** Los ocupantes del dormitorio ubicado sobre la sala técnica reportan un
        **zumbido grave y persistente durante la noche**. Indican que el ruido aparece cuando entra en operación
        la bomba **Lowara SHOS 50-125/75/P** y disminuye o desaparece cuando la bomba se detiene.

        La bomba opera a **2900 RPM**. A partir del reclamo todavía no podemos afirmar si el problema está dominado
        por una componente rotacional, una condición hidráulica, la transmisión por la base, las tuberías
        o la radiación aérea.

        **Objetivo:** diseñar una campaña de medición, interpretar los resultados y construir un diagnóstico sustentado
        en evidencias. La app no entregará la conclusión al alumno antes de que analice los datos.
        """
    )

    if role=="Docente":
        with st.container(border=True):
            st.markdown("### Clave docente · desarrollo esperado del diagnóstico")
            st.write(
                "Esta sección resume la lógica que debería construir el estudiante durante el Laboratorio A. "
                "No aparece en Alumno ni en Zoom/Proyección."
            )

            td1,td2,td3,td4=st.columns(4)
            with td1:
                _card(
                    "1 · Reclamo",
                    "Zumbido grave nocturno",
                    "El síntoma aparece cuando opera la bomba y se reduce al detenerla. Esto orienta la campaña, pero todavía no identifica el mecanismo.",
                    tone="blue"
                )
            with td2:
                _card(
                    "2 · Referencia rotacional",
                    "2900 RPM → 48,3 Hz",
                    "En espectros por bandas, la componente 1×RPM se espera principalmente en la banda central de 50 Hz.",
                    tone="purple"
                )
            with td3:
                _card(
                    "3 · Caminos",
                    "Base + tuberías + aire",
                    "Debe comprobarse si la misma banda aparece en carcasa, apoyo, tuberías, sala técnica y dormitorio."
                )
            with td4:
                _card(
                    "4 · Hidráulica",
                    "NPSH + banda ancha",
                    "El margen NPSH evalúa riesgo hidráulico. La cavitación solo se fortalece como hipótesis si existe evidencia vibroacústica compatible.",
                    tone="green"
                )

            st.markdown("#### Diagnóstico esperado al integrar las evidencias")
            st.info(
                "**Componente principal del zumbido:** una excitación asociada al giro de la bomba, "
                "1×RPM ≈ 48,3 Hz, observable principalmente en la banda de 50 Hz. "
                "Si esa componente aparece en carcasa, base/tuberías y dormitorio, existe correspondencia espectral "
                "compatible con transmisión desde la bomba hacia el receptor."
            )
            st.warning(
                "**Cavitación:** NPSHₐ < NPSHᵣ indica una condición hidráulica desfavorable, "
                "pero no explica por sí sola el zumbido tonal. La hipótesis de cavitación se fortalece únicamente "
                "si además aparecen contenido de banda ancha, inestabilidad hidráulica u otra evidencia compatible."
            )
            st.success(
                "**Conclusión docente esperada:** el caso puede contener dos fenómenos simultáneos: "
                "(1) una componente rotacional asociada al zumbido de baja frecuencia y transmitida por base/tuberías, "
                "y (2) una condición hidráulica compatible con cavitación que puede agregar ruido y vibración de banda ancha."
            )

    # ---------------------------------------------------------
    # 2.1 Cavitación y NPSH: prerrequisito
    # ---------------------------------------------------------
    st.markdown("### 2.1 · Antes de diagnosticar: ¿qué es la cavitación?")
    st.write(
        "La **cavitación** puede aparecer cuando la presión local del líquido cae hasta valores cercanos a su presión de vapor. "
        "Se forman cavidades o burbujas de vapor que luego llegan a zonas de mayor presión y colapsan. Ese proceso puede generar ruido, vibración, pérdida de desempeño y, si persiste, erosión del impulsor."
    )
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:.55rem 0 1rem">
          <div style="border:1px solid #cfe0f1;border-radius:14px;padding:13px;background:#fff"><b>1 · Baja la presión local</b><br><span style="color:#64748b">Zona de succión/entrada del impulsor.</span></div>
          <div style="border:1px solid #cfe0f1;border-radius:14px;padding:13px;background:#fff"><b>2 · Se forma vapor</b><br><span style="color:#64748b">Aparecen pequeñas cavidades de vapor.</span></div>
          <div style="border:1px solid #cfe0f1;border-radius:14px;padding:13px;background:#fff"><b>3 · Viajan a mayor presión</b><br><span style="color:#64748b">Las burbujas salen de la zona de baja presión.</span></div>
          <div style="border:1px solid #f3c7bf;border-radius:14px;padding:13px;background:#fff7f5"><b>4 · Colapsan</b><br><span style="color:#7c4a42">Generan impulsos, ruido, vibración y posible erosión.</span></div>
        </div>
        """,unsafe_allow_html=True
    )

    st.markdown("#### Antes de seguir: tono y contenido de banda ancha no son lo mismo")
    st.write(
        "En un espectro podemos encontrar energía concentrada alrededor de una frecuencia concreta o energía distribuida "
        "sobre muchas frecuencias. Esta diferencia será importante cuando interpretemos las mediciones de la bomba."
    )

    patt_f=np.array([20,25,31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000],dtype=float)
    patt_tonal=np.array([0.12,0.15,0.18,0.22,3.6,0.28,0.16,0.13,0.11,0.10,0.09,0.08,0.075,0.070,0.065,0.060,0.055,0.050,0.047,0.044,0.041])
    patt_broad=np.array([0.16,0.22,0.19,0.20,0.23,0.24,0.26,0.30,0.34,0.39,0.46,0.55,0.66,0.78,0.88,0.95,1.02,1.05,1.00,0.93,0.84])

    tp1,tp2=st.columns(2)
    with tp1:
        st.markdown("**Componente tonal**")
        fig,ax=plt.subplots(figsize=(6.4,3.2))
        ax.plot(patt_f,patt_tonal,marker='o')
        _format_band_axis(ax,patt_f)
        ax.set_yscale('log')
        ax.set_xlabel("Bandas de frecuencia (Hz)")
        ax.set_ylabel("Nivel vibratorio relativo")
        ax.set_title("Energía concentrada en una frecuencia")
        ax.grid(True,alpha=.22)
        fig.tight_layout()
        st.pyplot(fig,use_container_width=True); plt.close(fig)
        st.caption(
            "Ejemplo didáctico: aparece un pico claramente diferenciado. En una máquina rotatoria puede coincidir, "
            "por ejemplo, con 1×RPM u otro fenómeno periódico."
        )
    with tp2:
        st.markdown("**Contenido de banda ancha (broadband)**")
        fig,ax=plt.subplots(figsize=(6.4,3.2))
        ax.plot(patt_f,patt_broad,marker='o')
        _format_band_axis(ax,patt_f)
        ax.set_yscale('log')
        ax.set_xlabel("Bandas de frecuencia (Hz)")
        ax.set_ylabel("Nivel vibratorio relativo")
        ax.set_title("Energía distribuida en muchas frecuencias")
        ax.grid(True,alpha=.22)
        fig.tight_layout()
        st.pyplot(fig,use_container_width=True); plt.close(fig)
        st.caption(
            "La energía aumenta en un rango amplio del espectro. Procesos irregulares como turbulencia, impactos "
            "o colapso de burbujas pueden producir este tipo de patrón."
        )

    st.info(
        "**Banda ancha** significa que la energía no está concentrada únicamente en un tono. "
        "Un aumento de banda ancha puede ser compatible con cavitación, pero **no la demuestra por sí solo**."
    )

    r1,r2,r3,r4=st.columns(4)
    with r1:
        _card(
            "Ruido",
            "irregular + banda ancha",
            "Puede percibirse como grava, crepitación o golpeteo y acompañarse de energía distribuida en varias frecuencias.",
            tone="blue"
        )
    with r2:
        _card(
            "Vibración",
            "más que un tono",
            "Puede aumentar en un rango de frecuencias. Un pico aislado a 1×RPM por sí solo no demuestra cavitación."
        )
    with r3:
        _card(
            "Hidráulica",
            "presión + caudal + NPSH",
            "La condición de succión permite evaluar si la hipótesis de cavitación es físicamente plausible.",
            tone="green"
        )
    with r4:
        _card(
            "Daño",
            "erosión / pitting",
            "La cavitación persistente puede deteriorar el impulsor; es una consecuencia que refuerza el diagnóstico, no una condición necesaria para detectarlo.",
            tone="orange"
        )

    st.markdown("#### ¿Qué es NPSH y por qué se usa?")
    st.write(
        "El NPSH expresa el **margen de presión disponible en la succión antes de alcanzar condiciones favorables "
        "para la vaporización del líquido**. Para diagnosticar cavitación debemos separar dos cantidades que provienen "
        "de lugares distintos."
    )
    n1,n2=st.columns(2)
    with n1:
        _card(
            "NPSH disponible · NPSHₐ",
            "lo determina la instalación",
            "Depende de presión disponible, temperatura y presión de vapor, diferencia de altura y pérdidas del circuito de succión. No lo entrega el catálogo de la bomba.",
            tone="green"
        )
    with n2:
        _card(
            "NPSH requerido · NPSHᵣ",
            "lo determina la bomba",
            "Se obtiene de la curva del fabricante para un caudal y una velocidad de giro determinados. Debe leerse en la ficha técnica.",
            tone="blue"
        )

    st.markdown("##### ¿Cómo se calcula el NPSH disponible?")
    st.write(
        "Para un sistema que aspira desde un estanque abierto, una forma simplificada de expresar el margen disponible es:"
    )

    st.latex(
        r"\boxed{\displaystyle NPSH_A="
        r"\frac{p_{\mathrm{atm}}}{\rho g}"
        r"+z"
        r"-h_f"
        r"-\frac{p_v}{\rho g}}"
    )

    st.markdown("**Significado de cada término**")

    p1,p2,p3=st.columns(3)
    with p1:
        st.latex(r"p_{\mathrm{atm}}\;[\mathrm{Pa}]")
        st.caption("Presión atmosférica absoluta que actúa sobre la superficie libre del líquido.")
    with p2:
        st.latex(r"\rho\;[\mathrm{kg/m^3}]")
        st.caption("Densidad del líquido a la temperatura de operación.")
    with p3:
        st.latex(r"g\;[\mathrm{m/s^2}]")
        st.caption("Aceleración de gravedad.")

    p4,p5,p6=st.columns(3)
    with p4:
        st.latex(r"z\;[\mathrm{m}]")
        st.caption(
            "Diferencia de cota entre la superficie libre y el eje de la bomba. "
            "Es positiva si el nivel del líquido está sobre la bomba y negativa si está bajo ella."
        )
    with p5:
        st.latex(r"h_f\;[\mathrm{m}]")
        st.caption("Pérdidas de carga de la línea de succión.")
    with p6:
        st.latex(r"p_v\;[\mathrm{Pa}]")
        st.caption("Presión de vapor del líquido a la temperatura de operación.")

    st.markdown("**Lectura física de la ecuación**")
    st.latex(
        r"\boxed{\text{presión disponible}"
        r"+\text{altura estática}"
        r"-\text{pérdidas en succión}"
        r"-\text{presión de vapor}"
        r"\;\longrightarrow\;NPSH_A}"
    )

    st.info(
        "El NPSHₐ aumenta cuando existe mayor presión disponible en la succión o mayor altura favorable, "
        "y disminuye cuando aumentan las pérdidas de carga o la presión de vapor del líquido."
    )
    st.info(
        "Si se dispone de una medición de **presión absoluta directamente en la brida de succión**, el NPSHₐ también puede "
        "determinarse a partir de esa presión, la velocidad local y la presión de vapor. En este ejercicio utilizaremos el balance desde un estanque abierto."
    )

    st.markdown("##### ¿Qué información se mide y qué información se consulta?")
    npsh_rows=[
        ("Presión atmosférica o presión absoluta de succión","Barómetro / transductor","Instalación"),
        ("Caudal Q","Caudalímetro / sistema de control","Instalación"),
        ("Temperatura del líquido","Termómetro / sensor","Instalación"),
        ("Presión de vapor pᵥ","Tabla de propiedades a la temperatura medida","Propiedad del líquido"),
        ("Diferencia de cota z","Plano / medición en terreno","Instalación"),
        ("Pérdidas h_f","Cálculo hidráulico de la succión","Instalación"),
        ("NPSHᵣ","Curva NPSH–Q del fabricante","Bomba / catálogo"),
    ]
    st.dataframe(
        pd.DataFrame(npsh_rows,columns=["Dato","Cómo se obtiene","De dónde proviene"]),
        hide_index=True,use_container_width=True
    )

    st.markdown("#### Laboratorio NPSH · instalación real + catálogo real")
    st.markdown(
        "**Misma bomba del caso:** Lowara SHOS 50-125/75/P."
    )
    st.write("Punto de operación utilizado en el ejercicio:")
    st.latex(r"Q=48\;\mathrm{m^3/h}")

    st.markdown("**Tu trabajo tiene dos partes:**")
    np_a,np_b=st.columns(2)
    with np_a:
        _card(
            "A · Instalación",
            "Calcular NPSHₐ",
            "Obtendrás el NPSH disponible a partir de presión, temperatura, altura y pérdidas de la línea de succión.",
            tone="green"
        )
    with np_b:
        _card(
            "B · Bomba",
            "Leer NPSHᵣ",
            "Abrirás el catálogo oficial y leerás el NPSH requerido en la curva correspondiente al caudal de operación.",
            tone="blue"
        )

    lc1,lc2=st.columns([1.25,1])
    with lc1:
        st.markdown("**A · Datos de la instalación**")
        install_data=pd.DataFrame([
            ["Presión atmosférica absoluta", "101,3 kPa"],
            ["Temperatura del agua", "20 °C"],
            ["Presión de vapor del agua a 20 °C", "2,34 kPa"],
            ["Densidad adoptada", "998 kg/m³"],
            ["Diferencia de cota (z)", "−4,50 m"],
            ["Pérdidas de carga en succión (h_f)", "2,20 m"],
            ["Caudal de operación (Q)", "48 m³/h"],
        ],columns=["Variable","Valor"])
        st.dataframe(install_data,hide_index=True,use_container_width=True)
    with lc2:
        st.markdown("**B · Catálogo de la bomba**")
        st.markdown("**Dónde buscar en el catálogo**")
        st.success(
            "Ve directamente a la **página 58** del catálogo PDF. "
            "La página está titulada **SHOE–SHOS–SHOD 50-125 · Operating Characteristics at 50 Hz, 2 Poles**."
        )
        st.markdown(
            """
            En esa página encontrarás tres gráficos. Para este ejercicio utiliza el **gráfico central de NPSH**:

            1. confirma que la página corresponde a **50-125** y aproximadamente **2900 RPM**;
            2. identifica la curva **50-125/75**;
            3. en el eje horizontal inferior localiza **Q = 48 m³/h**;
            4. sube verticalmente hasta interceptar la curva 50-125/75;
            5. desde la intersección desplázate horizontalmente hacia el **eje vertical izquierdo**, expresado en metros;
            6. registra el valor de **NPSH requerido** que obtengas gráficamente.
            """
        )
        st.link_button(
            "Abrir catálogo oficial Lowara / Xylem",
            "https://www.xylem.com/siteassets/brand/lowara/resources/technical-brochure/19100390u_d_05-2023_co-sho-50hz_uk.pdf",
            use_container_width=True
        )
        st.caption(
            "Referencia para la actividad: **página 58**, gráfico central NPSH–Q, curva 50-125/75. "
            "Al tratarse de una lectura gráfica se acepta una pequeña tolerancia."
        )


    # Clave exclusiva de revisión docente.
    # Zoom/Proyección conserva el comportamiento del alumno para poder desarrollar la actividad en clase.
    is_teacher_npsh = role == "Docente"
    if is_teacher_npsh:
        st.markdown("##### Clave docente · valores esperados del ejercicio")
        st.write(
            "La figura utiliza el **mismo catálogo que abre actualmente la app**. "
            "La curva corresponde a **SHOE–SHOS–SHOD 50-125**, página impresa **58**, "
            "modelo hidráulico 50-125/75. Esta ayuda no se muestra en Alumno ni en Zoom/Proyección."
        )
        _asset(
            "curso2_lab1_etapa8_npsh_clave_docente.webp",
            "Clave docente · catálogo actual, página 58: Q ≈ 48 m³/h → curva 50-125/75 → NPSHᵣ ≈ 3,8 m."
        )
        kd1,kd2,kd3,kd4=st.columns(4)
        with kd1:
            _card(
                "NPSHᵣ · catálogo",
                "≈ 3,8 m",
                "Lectura gráfica en página 58, Q ≈ 48 m³/h, curva 50-125/75. Se acepta una pequeña tolerancia.",
                tone="blue"
            )
        with kd2:
            _card(
                "NPSHₐ · instalación",
                "≈ 3,41 m",
                "Resultado calculado con presión atmosférica, cota, pérdidas y presión de vapor del caso.",
                tone="green"
            )
        with kd3:
            _card(
                "Margen vs. catálogo",
                "≈ −0,39 m",
                "3,41 − 3,80. La instalación dispone de menos NPSH que el requerido por la curva.",
                tone="orange"
            )
        with kd4:
            _card(
                "Referencia práctica",
                "≈ 4,30 m",
                "El fabricante sugiere aumentar el valor de catálogo en 0,5 m para uso práctico. Déficit práctico ≈ −0,89 m.",
                tone="orange"
            )
        st.info(
            "Esta clave solo aparece en **Vista Docente**. En **Alumno** y **Zoom/Proyección** "
            "los campos permanecen como actividad a completar."
        )

        st.markdown("##### ¿Cómo interpretar el margen NPSH?")
        st.latex(r"M_{NPSH}=NPSH_A-NPSH_R")

        mi1,mi2,mi3=st.columns(3)
        with mi1:
            _card(
                "M_NPSH > 0",
                "Margen positivo",
                "La instalación dispone de más NPSH que el requerido por la bomba. "
                "Es una condición favorable, aunque en proyecto debe existir un margen de diseño suficiente.",
                tone="green"
            )
        with mi2:
            _card(
                "M_NPSH = 0",
                "Sin margen",
                "NPSH disponible y requerido coinciden. La instalación queda en el límite "
                "y pequeñas variaciones de operación pueden volverla desfavorable.",
                tone="orange"
            )
        with mi3:
            _card(
                "M_NPSH < 0",
                "Condición desfavorable",
                "La instalación dispone de menos NPSH que el requerido. "
                "La condición hidráulica es compatible con riesgo de cavitación.",
                tone="orange"
            )

        st.markdown("##### Interpretación del caso del laboratorio")
        st.latex(
            r"M_{NPSH}=3.41-3.80\approx-0.39\;\mathrm{m}"
        )
        st.warning(
            "**Lectura docente:** la instalación dispone aproximadamente **0,39 m menos** de NPSH "
            "que el requerido por la bomba en ese punto de operación. Por lo tanto, la condición de "
            "succión es hidráulicamente desfavorable y compatible con riesgo de cavitación."
        )
        st.markdown(
            """
            **Importante para la corrección:** un margen negativo **no demuestra por sí solo que el ruido medido sea causado por cavitación**.
            En el laboratorio la hipótesis se fortalece cuando se combina:

            - evidencia hidráulica: margen NPSH insuficiente;
            - evidencia vibroacústica: aumento de contenido de banda ancha;
            - comportamiento operacional: presión/caudal o desempeño compatibles con una condición hidráulica anómala.
            """
        )
        st.success(
            "Conclusión esperada del alumno: **la condición hidráulica y la evidencia vibroacústica, consideradas en conjunto, "
            "son compatibles con cavitación**. No corresponde afirmar que NPSH se convierte directamente en dB o mm/s."
        )

    # Valor real calculado internamente para comprobar el trabajo del alumno
    rho_w=998.0
    g_npsh=9.81
    patm_pa=101300.0
    pv_pa=2340.0
    z_npsh=-4.50
    hf_npsh=2.20
    npsha_expected=patm_pa/(rho_w*g_npsh)+z_npsh-hf_npsh-pv_pa/(rho_w*g_npsh)

    st.markdown("##### Paso 1 · Calcula el NPSH disponible")
    st.latex(
        r"NPSH_A=\frac{101300}{998\cdot9.81}-4.50-2.20-\frac{2340}{998\cdot9.81}"
    )
    npsha_student=st.number_input(
        "Ingresa tu NPSHₐ calculado (m)",
        min_value=0.0,max_value=15.0,value=0.0,step=0.05,
        key=f"{ns}_npsha_student"
    )

    st.markdown("##### Paso 2 · Lee el NPSH requerido en el catálogo")
    npshr_student=st.number_input(
        "NPSHᵣ leído en la curva del fabricante a Q ≈ 48 m³/h (m)",
        min_value=0.0,max_value=10.0,value=0.0,step=0.1,
        key=f"{ns}_npshr_student",
        help=(
            "Vista Docente: utiliza la clave mostrada arriba para revisar la lectura. "
            "Alumno/Zoom: lee el valor directamente en la curva NPSH–Q del catálogo."
        )
    )

    st.markdown("##### Paso 3 · Calcula el margen")
    st.latex(r"M_{NPSH}=NPSH_A-NPSH_R")
    margin_student=st.number_input(
        "Margen M_NPSH calculado (m)",
        min_value=-10.0,max_value=10.0,value=0.0,step=0.05,
        key=f"{ns}_npsh_margin_student"
    )

    if role == "Docente":
        st.caption(
            "Revisión docente: el formulario se mantiene editable para que puedas probar la actividad; "
            "la clave superior muestra los valores esperados sin autocompletar las respuestas."
        )

    if st.button(
        "Comprobar cálculo y lectura del catálogo",
        type="primary",
        use_container_width=True,
        key=f"{ns}_npsh_real_check"
    ):
        ok_a=abs(float(npsha_student)-float(npsha_expected))<=0.12
        # La curva del catálogo es gráfica: valor cercano a 3.8 m en Q≈48 m³/h.
        ok_r=3.5 <= float(npshr_student) <= 4.1
        ok_m=abs(float(margin_student)-(float(npsha_student)-float(npshr_student)))<=0.12

        if ok_a and ok_r and ok_m:
            saved["stage8_npsh_case"]={
                "product":CASE_MODEL,
                "Q_m3_h":48.0,
                "npsha_m":float(npsha_student),
                "npshr_m":float(npshr_student),
                "margin_m":float(margin_student),
                "validated":True,
            }
            _persist()
            st.success(
                "Cálculo coherente. Has obtenido NPSHₐ desde la instalación y NPSHᵣ desde la curva real del fabricante."
            )
            if margin_student<=0:
                st.warning(
                    "El margen resulta nulo o negativo: la condición es compatible con riesgo de cavitación y requiere corregir la instalación/punto de operación."
                )
            else:
                st.info(
                    "El margen es positivo, pero en proyecto no basta con que sea apenas mayor que cero: debe revisarse el margen recomendado para la aplicación."
                )
            st.caption(
                "La ficha Lowara indica que los valores NPSH mostrados son de laboratorio y sugiere aumentar esos valores en 0,5 m para uso práctico."
            )
        else:
            problems=[]
            if not ok_a: problems.append("revisa el cálculo de NPSHₐ y los signos de z y h_f")
            if not ok_r: problems.append("revisa la lectura de la curva NPSH–Q del catálogo")
            if not ok_m: problems.append("revisa la resta NPSHₐ − NPSHᵣ")
            st.warning("Aún hay algo que revisar: " + "; ".join(problems) + ".")

    npsh_saved=saved.get("stage8_npsh_case",{})
    if isinstance(npsh_saved,dict) and npsh_saved.get("validated"):
        nn1,nn2,nn3=st.columns(3)
        with nn1:
            _card("NPSHₐ calculado",f"{npsh_saved['npsha_m']:.2f} m","Resultado obtenido desde las condiciones de la instalación.",tone="green")
        with nn2:
            _card("NPSHᵣ leído",f"{npsh_saved['npshr_m']:.2f} m","Lectura realizada por el alumno en la curva del fabricante.",tone="blue")
        with nn3:
            _card("Margen",f"{npsh_saved['margin_m']:+.2f} m","Diferencia disponible − requerido.",tone="orange" if npsh_saved["margin_m"]<=0 else "green")

    st.markdown("#### ¿Qué tiene que ver el NPSH con el ruido y la vibración?")
    st.write(
        "El cálculo de NPSH **no predice un nivel acústico en dB**. Su función en este laboratorio es distinta: "
        "indica si existe una condición hidráulica capaz de favorecer la formación y el colapso de burbujas. "
        "Después debemos buscar evidencia vibroacústica compatible."
    )

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:9px;margin:.6rem 0 1rem">
          <div style="border:1px solid #cbd5e1;border-radius:14px;padding:12px;background:#fff;text-align:center">
            <b>1 · NPSH</b><br><span style="color:#64748b">margen hidráulico insuficiente</span>
          </div>
          <div style="display:flex;align-items:center;justify-content:center;font-size:1.5rem">→</div>
          <div style="border:1px solid #fed7aa;border-radius:14px;padding:12px;background:#fff7ed;text-align:center">
            <b>2 · Cavidades de vapor</b><br><span style="color:#7c4a03">formación y colapso irregular</span>
          </div>
          <div style="display:flex;align-items:center;justify-content:center;font-size:1.5rem">→</div>
          <div style="border:1px solid #bfdbfe;border-radius:14px;padding:12px;background:#eff6ff;text-align:center">
            <b>3 · Evidencia vibroacústica</b><br><span style="color:#1e40af">ruido/vibración adicional de banda ancha</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nb1,nb2=st.columns(2)
    with nb1:
        _card(
            "Lo que sí aporta el NPSH",
            "evidencia hidráulica",
            "Un margen insuficiente indica que la condición de succión es compatible con riesgo de cavitación.",
            tone="green"
        )
    with nb2:
        _card(
            "Lo que NO aporta el NPSH",
            "no entrega dB ni mm/s",
            "No existe una conversión universal desde el margen NPSH hacia un nivel acústico o vibratorio.",
            tone="orange"
        )

    st.markdown("##### Integración que buscaremos en la campaña")
    i1,i2,i3,i4=st.columns([1,1,1,1.1])
    with i1:
        _card(
            "1 · Evidencia hidráulica",
            "NPSH + presión + caudal",
            "Comprueba si existe una condición de succión compatible con riesgo de cavitación.",
            tone="green"
        )
    with i2:
        _card(
            "2 · Evidencia vibroacústica",
            "banda ancha",
            "Busca energía adicional distribuida en varias frecuencias, no solamente un tono aislado.",
            tone="blue"
        )
    with i3:
        _card(
            "3 · Operación",
            "estabilidad del proceso",
            "Revisa presión, caudal y cambios de desempeño durante la operación de la bomba.",
            tone="white"
        )
    with i4:
        _card(
            "4 · Diagnóstico integrado",
            "compatible con cavitación",
            "La hipótesis se fortalece solo cuando distintas evidencias independientes son coherentes entre sí.",
            tone="purple"
        )
    st.info(
        "**Principio de diagnóstico:** ninguna evidencia aislada demuestra por sí sola cavitación. "
        "La conclusión se fortalece cuando la condición hidráulica, las mediciones vibroacústicas "
        "y el comportamiento operacional apuntan al mismo mecanismo."
    )

    # ---------------------------------------------------------
    # 2.2 Plan real de medición
    # ---------------------------------------------------------
    st.markdown("### 2.2 · Diseña tu plan de medición")
    st.write(
        "Ahora decide **qué medir, dónde medir y qué quieres comprobar**. No es obligatorio medir todo: si ejecutas una campaña incompleta, también tendrás evidencia incompleta."
    )
    _asset("curso2_lab1_etapa8_bomba_medicion_profesional.webp")
    st.caption("A · base/apoyo · B · carcasa/motor · C · tubería de descarga cercana · D · tubería más alejada")

    measure_catalog={
        "RPM / tacómetro":{
            "Eje del motor":["Establecer 1×RPM como referencia espectral"]
        },
        "Vibración · velocidad RMS":{
            "B · Carcasa/motor":["Caracterizar vibración en la fuente"],
            "A · Base/apoyo":["Comprobar transmisión hacia estructura"],
            "C · Tubería cercana":["Comprobar camino por tuberías"],
            "D · Tubería alejada":["Evaluar persistencia a lo largo de tubería"],
        },
        "Ruido · espectro por bandas":{
            "Dormitorio receptor":["Identificar qué componentes acústicas llegan al receptor"],
            "Sala técnica":["Caracterizar el campo acústico próximo a la fuente"],
        },
        "Condición hidráulica / NPSH":{
            "Succión de la bomba":["Evaluar condición compatible con cavitación"]
        },
    }
    pc1,pc2,pc3=st.columns([1.05,1,1.45])
    with pc1:
        mtype=st.selectbox("Magnitud / instrumento",list(measure_catalog),key=f"{ns}_plan_type")
    available_locations=list(measure_catalog[mtype].keys())
    with pc2:
        mloc=st.selectbox("Dónde medir",available_locations,key=f"{ns}_plan_location")
    with pc3:
        mobj=st.selectbox(
            "Qué quiero comprobar",
            measure_catalog[mtype][mloc],
            key=f"{ns}_plan_objective"
        )

    plan=saved.get("stage8_measurement_plan",[])
    if not isinstance(plan,list): plan=[]
    badd,breset=st.columns([2,1])
    with badd:
        if st.button("Agregar medición al plan",type="primary",use_container_width=True,key=f"{ns}_plan_add"):
            row={"Medición":mtype,"Punto":mloc,"Objetivo":mobj}
            if row not in plan:
                plan.append(row)
                saved["stage8_measurement_plan"]=plan
                _persist(); st.rerun()
            else:
                st.info("Esa medición ya está en el plan.")
    with breset:
        if st.button("Limpiar plan",use_container_width=True,key=f"{ns}_plan_reset"):
            saved["stage8_measurement_plan"]=[]
            saved["stage8_campaign_executed"]=False
            saved["stage8_evidence"]={}
            _persist(); st.rerun()

    plan=saved.get("stage8_measurement_plan",[])
    if plan:
        st.dataframe(pd.DataFrame(plan),hide_index=True,use_container_width=True)
        selected_points={r["Punto"] for r in plan}
        coverage={
            "Excitación":"Eje del motor" in selected_points,
            "Fuente mecánica":"B · Carcasa/motor" in selected_points,
            "Estructura":"A · Base/apoyo" in selected_points,
            "Tuberías":bool({"C · Tubería cercana","D · Tubería alejada"}&selected_points),
            "Aéreo · sala":"Sala técnica" in selected_points,
            "Receptor":"Dormitorio receptor" in selected_points,
            "Hidráulica":"Succión de la bomba" in selected_points,
        }
        coverage_items=list(coverage.items())
        for i in range(0,len(coverage_items),4):
            batch=coverage_items[i:i+4]
            cols=st.columns(len(batch))
            for col,(lab,ok) in zip(cols,batch):
                with col:
                    _card(
                        lab,
                        "Incluido" if ok else "No medido",
                        "La campaña entregará datos de esta parte." if ok else "No tendrás evidencia directa de esta parte.",
                        tone="green" if ok else "orange"
                    )
        if st.button("Ejecutar campaña de medición",type="primary",use_container_width=True,key=f"{ns}_campaign_run"):
            saved["stage8_campaign_executed"]=True
            _persist(); st.rerun()
    else:
        st.info("Agrega al menos una medición para construir la campaña.")

    # ---------------------------------------------------------
    # 2.3 Resultados sólo de lo que el alumno midió
    # ---------------------------------------------------------
    if saved.get("stage8_campaign_executed") and plan:
        st.markdown("### 2.3 · Ejecuta las mediciones: observa antes de concluir")
        st.write(
            "La app muestra únicamente los resultados correspondientes a tu plan. **No se entrega la interpretación automática**: identifica picos, compara puntos y registra tus evidencias."
        )
        selected_points={r["Punto"] for r in plan}
        evidence=saved.get("stage8_evidence",{})
        if not isinstance(evidence,dict): evidence={}

        freqs=np.array([10,12.5,16,20,25,31.5,40,50,63,80,100,125,160,200],dtype=float)
        carc=np.array([0.22,0.25,0.30,0.36,0.44,0.58,0.82,7.6,0.72,0.50,0.36,0.28,0.21,0.17])
        base=np.array([0.12,0.14,0.17,0.20,0.24,0.30,0.42,4.8,0.48,0.33,0.25,0.19,0.14,0.11])
        pipe_c=np.array([0.10,0.12,0.15,0.18,0.22,0.28,0.38,4.2,0.43,0.31,0.24,0.18,0.13,0.10])
        pipe_d=np.array([0.08,0.10,0.12,0.15,0.19,0.24,0.33,3.1,0.35,0.26,0.20,0.15,0.11,0.08])
        # Nivel en sala técnica: campo próximo a la fuente.
        # Nivel en dormitorio: receptor sensible.
        lp_room=np.array([55,56,57,58,59,60,62,72,67,63,60,57,54,52],dtype=float)
        lp=np.array([33,34,35,36,37,38,40,46,42,39,37,35,34,33],dtype=float)

        if "Eje del motor" in selected_points:
            st.markdown("#### Medición · RPM / referencia de giro")
            q1,q2=st.columns([1,1.2])
            with q1:
                _card("Tacómetro",f"{CASE_RPM:.0f} RPM","Dato medido en el eje de la misma bomba. Convierte RPM a Hz antes de comparar con el espectro.",tone="blue")
            with q2:
                rpm_calc=st.number_input("Calcula 1×RPM (Hz)",0.0,100.0,0.0,0.5,key=f"{ns}_ev_rpm")
                if st.button("Registrar evidencia de RPM",key=f"{ns}_ev_rpm_save"):
                    if abs(rpm_calc-CASE_F_ROT)<=0.6:
                        evidence["rpm"]=f"1×RPM = {CASE_F_ROT:.1f} Hz → banda de {CASE_BAND_HZ:.0f} Hz"
                        saved["stage8_evidence"]=evidence; _persist(); st.success("Evidencia registrada.")
                    else: st.warning("Revisa la conversión RPM/60.")
            st.caption(
                f"El valor exacto es {CASE_F_ROT:.1f} Hz. Como los gráficos se presentan en bandas preferentes, "
                f"esa componente se observa principalmente en la banda de {CASE_BAND_HZ:.0f} Hz."
            )

        if "B · Carcasa/motor" in selected_points:
            st.markdown("#### Medición B · Vibración en carcasa")
            fig,ax=plt.subplots(figsize=(8.5,3.8))
            ax.plot(freqs,carc,marker='o')
            _format_band_axis(ax,freqs)
            ax.set_yscale('log')
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Velocidad RMS (mm/s)')
            ax.grid(True,alpha=.25)
            ax.set_title('Espectro de vibración · carcasa/motor')
            if evidence.get("carcasa"):
                ax.axvline(CASE_BAND_HZ,linestyle='--',linewidth=1.2)
                ax.annotate("50 Hz",xy=(50,7.6),xytext=(63,4.8),arrowprops=dict(arrowstyle="->"))
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)
            dom=st.number_input("¿Cuál es la frecuencia dominante del gráfico? (Hz)",0.0,200.0,0.0,1.0,key=f"{ns}_ev_carc_f")
            if st.button("Registrar evidencia de carcasa",key=f"{ns}_ev_carc_save"):
                if abs(dom-CASE_BAND_HZ)<=1:
                    evidence["carcasa"]="Pico dominante de vibración en carcasa en la banda de 50 Hz"
                    saved["stage8_evidence"]=evidence; _persist(); st.success("Evidencia registrada.")
                else: st.warning("Observa nuevamente el máximo del espectro.")

        if "A · Base/apoyo" in selected_points:
            st.markdown("#### Medición A · Vibración en base/apoyo")
            fig,ax=plt.subplots(figsize=(8.5,3.8))
            ax.plot(freqs,base,marker='o')
            _format_band_axis(ax,freqs)
            ax.set_yscale('log')
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Velocidad RMS (mm/s)')
            ax.grid(True,alpha=.25)
            ax.set_title('Espectro de vibración · base/apoyo')
            if evidence.get("estructura"):
                ax.axvline(CASE_BAND_HZ,linestyle='--',linewidth=1.2)
                ax.annotate("50 Hz",xy=(50,4.8),xytext=(63,3.0),arrowprops=dict(arrowstyle="->"))
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)
            base_interp=st.radio("¿Qué evidencia aporta que la misma componente aparezca en la base?",["La vibración queda confinada a la máquina","Existe evidencia de transmisión hacia la estructura","Demuestra cavitación","Demuestra propagación exclusivamente aérea"],key=f"{ns}_ev_base_q")
            if st.button("Registrar evidencia estructural",key=f"{ns}_ev_base_save"):
                if base_interp=="Existe evidencia de transmisión hacia la estructura":
                    evidence["estructura"]="Componente de 50 Hz presente en base/apoyo: camino estructural plausible"
                    saved["stage8_evidence"]=evidence; _persist(); st.success("Evidencia registrada.")
                else: st.warning("La presencia de la componente en el apoyo indica que la fuerza dinámica está entrando al soporte.")

        if "C · Tubería cercana" in selected_points or "D · Tubería alejada" in selected_points:
            st.markdown("#### Medición · Vibración en tuberías")
            fig,ax=plt.subplots(figsize=(8.5,3.5))
            if "C · Tubería cercana" in selected_points: ax.plot(freqs,pipe_c,marker='o',label='C · cercana')
            if "D · Tubería alejada" in selected_points: ax.plot(freqs,pipe_d,marker='o',label='D · alejada')
            _format_band_axis(ax,freqs)
            ax.set_yscale('log')
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Velocidad RMS (mm/s)')
            ax.grid(True,alpha=.25)
            ax.legend()
            ax.set_title('Espectro de vibración · tuberías')
            if evidence.get("tuberias"):
                ax.axvline(CASE_BAND_HZ,linestyle='--',linewidth=1.2)
                ax.annotate("50 Hz",xy=(50,4.2),xytext=(63,2.6),arrowprops=dict(arrowstyle="->"))
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)
            if {"C · Tubería cercana","D · Tubería alejada"}.issubset(selected_points):
                pipe_interp=st.radio("¿Qué observas al comparar C y D?",["La componente desaparece completamente","La componente de 50 Hz disminuye pero persiste a distancia","La frecuencia cambia a 50 Hz","No hay información útil"],key=f"{ns}_ev_pipe_q")
                if st.button("Registrar evidencia por tuberías",key=f"{ns}_ev_pipe_save"):
                    if pipe_interp=="La componente de 50 Hz disminuye pero persiste a distancia":
                        evidence["tuberias"]="50 Hz persiste desde C hasta D: tuberías constituyen un camino mecánico plausible"
                        saved["stage8_evidence"]=evidence; _persist(); st.success("Evidencia registrada.")
                    else: st.warning("Compara la posición del pico y su amplitud en ambos puntos.")
            else:
                st.info("Mediste solo un punto de tubería. Puedes detectar vibración, pero tienes menos evidencia para evaluar su persistencia a lo largo de la red.")

        if "Sala técnica" in selected_points:
            st.markdown("#### Medición · Espectro acústico en sala técnica")
            st.write(
                "Esta medición caracteriza el campo acústico próximo a la bomba. "
                "El objetivo todavía no es decidir el camino dominante, sino identificar qué componentes están presentes cerca de la fuente."
            )
            fig,ax=plt.subplots(figsize=(8.5,3.8))
            ax.plot(freqs,lp_room,marker='o')
            _format_band_axis(ax,freqs)
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Nivel (dB)')
            ax.grid(True,alpha=.25)
            ax.set_title('Espectro acústico · sala técnica')
            if evidence.get("aereo_sala"):
                ax.axvline(CASE_BAND_HZ,linestyle='--',linewidth=1.2)
                ax.annotate("50 Hz",xy=(50,72),xytext=(63,69),arrowprops=dict(arrowstyle="->"))
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)

            room_f=st.number_input(
                "¿En qué banda aparece la componente más destacada en la sala técnica? (Hz)",
                0.0,200.0,0.0,1.0,
                key=f"{ns}_ev_room_f"
            )
            room_interp=st.radio(
                "¿Qué puedes afirmar solo con esta medición?",
                [
                    "Existe una componente acústica importante cerca de la fuente",
                    "Demuestra que el camino dominante hacia el dormitorio es aéreo",
                    "Demuestra cavitación",
                    "Demuestra que la estructura no transmite vibración",
                ],
                key=f"{ns}_ev_room_q"
            )
            if st.button("Registrar evidencia acústica en sala",key=f"{ns}_ev_room_save"):
                if abs(room_f-CASE_BAND_HZ)<=1 and room_interp=="Existe una componente acústica importante cerca de la fuente":
                    evidence["aereo_sala"]="Componente acústica destacada en la banda de 50 Hz en la sala técnica"
                    saved["stage8_evidence"]=evidence
                    _persist()
                    st.success("Evidencia registrada.")
                else:
                    st.warning(
                        "Lee primero la banda dominante. Una medición acústica en la sala confirma emisión próxima a la fuente, "
                        "pero no demuestra por sí sola qué camino domina hacia el dormitorio."
                    )

        if "Dormitorio receptor" in selected_points:
            st.markdown("#### Medición · Espectro acústico en dormitorio")
            fig,ax=plt.subplots(figsize=(8.5,3.8))
            ax.plot(freqs,lp,marker='o')
            _format_band_axis(ax,freqs)
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Nivel (dB)')
            ax.grid(True,alpha=.25)
            ax.set_title('Espectro acústico · receptor')
            if evidence.get("receptor"):
                ax.axvline(CASE_BAND_HZ,linestyle='--',linewidth=1.2)
                ax.annotate("50 Hz",xy=(50,46),xytext=(63,44),arrowprops=dict(arrowstyle="->"))
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)
            recv_f=st.number_input("¿En qué frecuencia aparece la componente más destacada? (Hz)",0.0,200.0,0.0,1.0,key=f"{ns}_ev_recv_f")
            if st.button("Registrar evidencia en receptor",key=f"{ns}_ev_recv_save"):
                if abs(recv_f-CASE_BAND_HZ)<=1:
                    evidence["receptor"]="Componente acústica destacada en la banda de 50 Hz en el dormitorio"
                    saved["stage8_evidence"]=evidence; _persist(); st.success("Evidencia registrada.")
                else: st.warning("Revisa el máximo local más relevante del espectro mostrado.")

        if {"Sala técnica","Dormitorio receptor"}.issubset(selected_points):
            st.markdown("#### Comparación acústica · sala técnica → dormitorio")
            st.write(
                "Como planificaste mediciones en ambos recintos, ahora puedes comparar sus formas espectrales. "
                "Busca si las componentes aparecen en las mismas bandas y cómo cambia su nivel."
            )
            fig,ax=plt.subplots(figsize=(8.8,4.0))
            ax.plot(freqs,lp_room,marker='o',label='Sala técnica')
            ax.plot(freqs,lp,marker='o',label='Dormitorio receptor')
            _format_band_axis(ax,freqs)
            ax.set_xlabel('Bandas de frecuencia (Hz)')
            ax.set_ylabel('Nivel (dB)')
            ax.grid(True,alpha=.25)
            ax.legend()
            ax.set_title('Comparación espectral · fuente próxima y receptor')
            fig.tight_layout()
            st.pyplot(fig,use_container_width=True); plt.close(fig)

            compare_air=st.radio(
                "¿Qué conclusión es válida al observar ambos espectros?",
                [
                    "La componente de 50 Hz aparece en ambos, lo que aporta correspondencia espectral",
                    "La diferencia entre curvas es directamente el aislamiento acústico del edificio",
                    "La coincidencia demuestra que el único camino es aéreo",
                    "Como los niveles son distintos, no existe relación entre fuente y receptor",
                ],
                key=f"{ns}_ev_air_compare"
            )
            if compare_air=="La componente de 50 Hz aparece en ambos, lo que aporta correspondencia espectral":
                st.success(
                    "Correcto. La correspondencia espectral es evidencia útil, pero todavía debe compararse con la evidencia estructural "
                    "y de tuberías antes de decidir cuál camino domina."
                )
            else:
                st.info(
                    "No interpretes la diferencia entre ambos niveles como una pérdida de transmisión directa: "
                    "son mediciones realizadas en campos acústicos y posiciones distintas."
                )

        if "Succión de la bomba" in selected_points:
            st.markdown("#### Medición hidráulica · condición de succión")
            npsh_case=saved.get("stage8_npsh_case",{})
            if not isinstance(npsh_case,dict) or not npsh_case.get("validated"):
                st.warning(
                    "Incluiste la condición hidráulica en tu campaña, pero todavía no has completado el laboratorio NPSH anterior. "
                    "Calcula primero NPSHₐ con los datos de la instalación y lee NPSHᵣ en el catálogo real."
                )
            else:
                h1,h2,h3=st.columns(3)
                with h1:
                    _card("Caudal Q",f"{npsh_case['Q_m3_h']:.0f} m³/h","Punto de operación usado para consultar la curva.")
                with h2:
                    _card("NPSHₐ",f"{npsh_case['npsha_m']:.2f} m","Resultado que calculaste desde la instalación.",tone="green")
                with h3:
                    _card("NPSHᵣ",f"{npsh_case['npshr_m']:.2f} m","Valor que leíste en la curva oficial del fabricante.",tone="blue")

                npsh_interp=st.radio(
                    "¿Qué evidencia aporta el margen que calculaste?",
                    [
                        "Demuestra desequilibrio mecánico",
                        "Condición compatible con riesgo de cavitación",
                        "Demuestra que el ruido es únicamente aéreo",
                        "No aporta información hidráulica",
                    ],
                    key=f"{ns}_ev_npsh_q"
                )
                if st.button("Registrar evidencia hidráulica",key=f"{ns}_ev_npsh_save"):
                    if npsh_case["margin_m"]<=0 and npsh_interp=="Condición compatible con riesgo de cavitación":
                        evidence["hidraulica"]=(
                            f"NPSHₐ − NPSHᵣ = {npsh_case['margin_m']:+.2f} m: "
                            "condición hidráulica compatible con riesgo de cavitación"
                        )
                        saved["stage8_evidence"]=evidence
                        _persist()
                        st.success("Evidencia hidráulica registrada.")
                    elif npsh_case["margin_m"]>0 and npsh_interp=="Condición compatible con riesgo de cavitación":
                        st.info("El margen es positivo. Evalúa además el margen de diseño requerido por el fabricante/aplicación antes de sostener esa hipótesis.")
                    else:
                        st.warning("Relaciona el signo y magnitud del margen con la condición hidráulica, no con un defecto mecánico.")

        # -----------------------------------------------------
        # Medición complementaria para relacionar NPSH con ruido/vibración
        # -----------------------------------------------------
        if {"B · Carcasa/motor","Succión de la bomba"}.issubset(selected_points):
            st.markdown("#### Medición complementaria · ¿aparece contenido de banda ancha?")
            st.write(
                "Como tu plan incluye **vibración en carcasa** y **condición hidráulica**, puedes confrontar ambas evidencias. "
                "Los siguientes espectros son **simulados con finalidad didáctica**: muestran el tipo de cambio que buscaríamos, "
                "no una firma universal de cavitación."
            )

            cav_f=np.array([20,25,31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000],dtype=float)
            vib_ref=np.array([0.16,0.18,0.20,0.24,2.6,0.31,0.20,0.16,0.14,0.13,0.12,0.11,0.10,0.095,0.09,0.085,0.080,0.075,0.070,0.066,0.062,0.058,0.055,0.052,0.050])
            vib_low=np.array([0.20,0.23,0.26,0.31,2.8,0.42,0.34,0.36,0.40,0.46,0.54,0.64,0.76,0.90,1.04,1.16,1.24,1.30,1.27,1.20,1.12,1.04,0.95,0.86,0.78])
            noise_ref=np.array([47,48,49,50,57,52,48,46,45,44,43,42,42,41,41,40,40,39,39,38,38,37,37,36,36],dtype=float)
            noise_low=np.array([49,50,51,52,59,55,54,55,56,58,60,62,64,66,68,69,70,71,71,70,69,68,66,64,62],dtype=float)

            bw1,bw2=st.columns(2)
            with bw1:
                fig,ax=plt.subplots(figsize=(6.5,3.7))
                ax.plot(cav_f,vib_ref,marker='o',label='Condición de referencia')
                ax.plot(cav_f,vib_low,marker='o',label='Condición con margen NPSH insuficiente')
                _format_band_axis(ax,cav_f)
                ax.set_yscale('log')
                ax.set_xlabel("Bandas de frecuencia (Hz)")
                ax.set_ylabel("Velocidad RMS relativa")
                ax.set_title("Vibración en carcasa · comparación didáctica")
                ax.grid(True,alpha=.22); ax.legend(fontsize=8)
                fig.tight_layout()
                st.pyplot(fig,use_container_width=True); plt.close(fig)
            with bw2:
                fig,ax=plt.subplots(figsize=(6.5,3.7))
                ax.plot(cav_f,noise_ref,marker='o',label='Condición de referencia')
                ax.plot(cav_f,noise_low,marker='o',label='Condición con margen NPSH insuficiente')
                _format_band_axis(ax,cav_f)
                ax.set_xlabel("Bandas de frecuencia (Hz)")
                ax.set_ylabel("Nivel acústico relativo (dB)")
                ax.set_title("Ruido próximo a la bomba · comparación didáctica")
                ax.grid(True,alpha=.22); ax.legend(fontsize=8)
                fig.tight_layout()
                st.pyplot(fig,use_container_width=True); plt.close(fig)

            bw_pattern=st.radio(
                "¿Qué cambio principal observas en la condición hidráulicamente desfavorable?",
                [
                    "Solo aparece un tono nuevo y aislado",
                    "Aumenta la energía en un rango amplio de frecuencias",
                    "Desaparece toda componente asociada a RPM",
                    "El espectro no cambia",
                ],
                key=f"{ns}_broadband_pattern"
            )
            bw_meaning=st.radio(
                "¿Qué conclusión es técnicamente correcta?",
                [
                    "El patrón de banda ancha demuestra por sí solo cavitación",
                    "El patrón de banda ancha es compatible con un proceso irregular, pero debe combinarse con evidencia hidráulica",
                    "Todo contenido de banda ancha proviene necesariamente de una bomba",
                    "NPSH permite convertir directamente este espectro a dB",
                ],
                key=f"{ns}_broadband_meaning"
            )

            if st.button("Registrar evidencia de banda ancha",key=f"{ns}_broadband_save"):
                npsh_case=saved.get("stage8_npsh_case",{})
                hydraulic_ok=(
                    isinstance(npsh_case,dict)
                    and npsh_case.get("validated")
                    and float(npsh_case.get("margin_m",99))<=0
                )
                if (
                    bw_pattern=="Aumenta la energía en un rango amplio de frecuencias"
                    and bw_meaning=="El patrón de banda ancha es compatible con un proceso irregular, pero debe combinarse con evidencia hidráulica"
                ):
                    evidence["banda_ancha"]="Aumento de energía distribuida en un rango amplio del espectro"
                    if hydraulic_ok:
                        evidence["cavitacion_integrada"]=(
                            "Margen NPSH insuficiente + patrón vibroacústico de banda ancha: "
                            "conjunto de evidencias compatible con cavitación"
                        )
                    saved["stage8_evidence"]=evidence
                    _persist()
                    st.success("Evidencia vibroacústica registrada.")
                    if hydraulic_ok:
                        st.success(
                            "Ahora sí existe una **integración de evidencia hidráulica y vibroacústica compatible con cavitación**. "
                            "Sigue siendo un diagnóstico técnico, no una conversión directa de NPSH a nivel de ruido."
                        )
                else:
                    st.warning(
                        "Revisa la diferencia entre un tono aislado y un aumento distribuido en muchas frecuencias. "
                        "Recuerda además que la banda ancha no demuestra cavitación por sí sola."
                    )

        # -----------------------------------------------------
        # 2.4 Tablero de evidencia y diagnóstico
        # -----------------------------------------------------
        evidence=saved.get("stage8_evidence",{})
        st.markdown("### 2.4 · Tablero de evidencias construido por ti")
        labels=[
            ("Excitación",evidence.get("rpm") or evidence.get("carcasa")),
            ("Fuente mecánica",evidence.get("carcasa")),
            ("Estructura",evidence.get("estructura")),
            ("Tuberías",evidence.get("tuberias")),
            ("Sala técnica",evidence.get("aereo_sala")),
            ("Receptor",evidence.get("receptor")),
            ("Hidráulica / NPSH",evidence.get("hidraulica")),
            ("Banda ancha",evidence.get("banda_ancha")),
            ("Integración cavitación",evidence.get("cavitacion_integrada")),
        ]
        cols=st.columns(3)
        for i,(lab,val) in enumerate(labels):
            with cols[i%3]:
                _card(
                    lab,
                    "Evidencia" if val else "Sin evidencia",
                    val or "No fue medida o todavía no has interpretado correctamente el resultado.",
                    tone="green" if val else "orange"
                )

        st.warning(
            "Una coincidencia de frecuencias aumenta la evidencia de relación, pero por sí sola no demuestra causalidad. "
            "Del mismo modo, **NPSH insuficiente no entrega un nivel de ruido** y **banda ancha no demuestra cavitación por sí sola**. "
            "El diagnóstico se fortalece cuando varias evidencias independientes apuntan al mismo mecanismo."
        )

        if evidence.get("hidraulica") and evidence.get("banda_ancha"):
            st.success(
                "Has combinado evidencia de dos dominios distintos: **condición hidráulica + comportamiento vibroacústico**. "
                "Esta integración es mucho más fuerte que interpretar cualquiera de las dos por separado."
            )

        st.markdown("### 2.5 · Construye tu diagnóstico preliminar")
        mech=st.multiselect("Mecanismos que mantienes como plausibles",["Desequilibrio / desalineación","Fuerzas hidráulicas / pulsaciones","Cavitación","Radiación aérea de carcasa"],key=f"{ns}_diag_mech_final")
        dom_path=st.selectbox("Camino dominante que propones",["Aún no puedo definirlo","Estructura/base","Tuberías","Aéreo","Combinación de base + tuberías"],key=f"{ns}_diag_path_final")
        reasoning=st.text_area("Justifica tu diagnóstico usando las evidencias que construiste",key=f"{ns}_diag_reason_final",height=120)
        if st.button("Guardar diagnóstico preliminar",type="primary",use_container_width=True,key=f"{ns}_diag_final_save"):
            if len(evidence)<3:
                st.warning("Tu diagnóstico tiene poca evidencia. Puedes guardarlo después de analizar más mediciones.")
            elif dom_path=="Aún no puedo definirlo" or len(reasoning.strip())<45:
                st.warning("Define un camino y justifica la decisión con los resultados observados.")
            else:
                saved["stage8_diagnosis"]={"plan":plan,"evidence":evidence,"mechanisms":mech,"dominant_path":dom_path,"reasoning":reasoning.strip()}
                _persist(); st.success("Diagnóstico preliminar guardado.")
    # =========================================================
    # 3 · LAB B: DIMENSIONAMIENTO ANTIVIBRATORIO
    # =========================================================
    st.markdown("## 3 · Laboratorio B — De la vibración de la bomba a la especificación del aislador")

    st.markdown(
        """
        **Problema de ingeniería.** El diagnóstico confirmó que parte de la fuerza dinámica generada por la bomba
        entra a la estructura a través de su base. Ahora debemos transformar esa información en una
        **especificación técnica que pueda buscarse en un catálogo real**.

        Al terminar este laboratorio todavía no elegirás una marca. Primero obtendrás los cuatro
        requerimientos que debe cumplir cualquier aislador candidato:
        """
    )

    rq_a,rq_b,rq_c,rq_d=st.columns(4)
    with rq_a:
        _card(
            "1 · Carga por apoyo",
            "lb / apoyo",
            "Cuánto peso debe soportar realmente cada aislador.",
            tone="blue"
        )
    with rq_b:
        _card(
            "2 · Deflexión requerida",
            "δ mínima",
            "Compresión estática mínima necesaria para obtener la frecuencia natural de diseño."
        )
    with rq_c:
        _card(
            "3 · Frecuencia natural",
            "fₙ máxima",
            "Límite máximo de frecuencia natural admisible para mantener separación respecto de la excitación.",
            tone="purple"
        )
    with rq_d:
        _card(
            "4 · Transmisibilidad",
            "T_F máxima",
            "Fracción máxima de fuerza dinámica que aceptaremos transmitir a la estructura.",
            tone="green"
        )

    st.info(
        "Estos cuatro requerimientos serán la **entrada del Laboratorio C**. "
        "El catálogo se usa después para comprobar qué producto real satisface simultáneamente la carga y el comportamiento dinámico."
    )

    _asset(
        "curso2_lab1_etapa8_aislamiento_resonancia.webp",
        "Conjunto bomba–motor sobre bancada y aisladores. El aislador soporta el peso estático y reduce la transmisión de fuerza dinámica."
    )

    # ---------------------------------------------------------
    # RUTA VISIBLE
    # ---------------------------------------------------------
    st.markdown("### 3.0 · Ruta técnica de selección")
    route = [
        ("01","Máquina","RPM · masa · componente perturbadora"),
        ("02","Carga","kg y lb que recibe cada apoyo"),
        ("03","Dinámica","fₙ · deflexión · razón r"),
        ("04","Desempeño","T_F · porcentaje de aislamiento"),
        ("05","Especificación","carga + δ + fₙ + T_F"),
        ("06","Catálogo","producto real que cumple lo calculado"),
    ]
    rc=st.columns(6)
    for col,(num,title,text) in zip(rc,route):
        with col:
            st.markdown(
                f"""<div style="border:1px solid #dbe4ee;border-radius:14px;padding:11px 10px;
                min-height:132px;background:#fff">
                <div style="font-size:.72rem;font-weight:900;color:#2563eb">{num}</div>
                <div style="font-weight:900;color:#0f172a;margin:.2rem 0">{title}</div>
                <div style="font-size:.82rem;color:#64748b;line-height:1.35">{text}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # ---------------------------------------------------------
    # 3.1 CONCEPTO FÍSICO
    # ---------------------------------------------------------
    st.markdown("### 3.1 · ¿Qué hace realmente un aislador antivibratorio?")
    st.write(
        "La bomba tiene que seguir soportada: el aislador **no elimina el peso**. "
        "Su función dinámica es permitir un movimiento controlado del conjunto para que una fracción menor "
        "de la fuerza vibratoria llegue a la losa."
    )

    c1,c2=st.columns(2)
    with c1:
        _card(
            "Carga estática",
            "W = m · g",
            "Es el peso del conjunto que el resorte debe sostener permanentemente. Determina cuánto se comprime el aislador.",
            tone="blue"
        )
    with c2:
        _card(
            "Fuerza dinámica",
            "F(t)",
            "Es la componente variable asociada al funcionamiento de la máquina. El objetivo es reducir cuánto de ella llega a la estructura.",
            tone="purple"
        )

    st.latex(r"\boxed{T_F=\frac{F_{\mathrm{transmitida}}}{F_{\mathrm{excitación}}}}")
    st.write(
        "La **transmisibilidad de fuerza** es el indicador principal de este modelo."
    )
    st.latex(r"T_F=0.10")
    st.write(
        "En este ejemplo, la amplitud de fuerza transmitida sería aproximadamente el 10 % "
        "de la fuerza dinámica de excitación considerada."
    )

    st.info(
        "**Primer criterio profesional:** un aislador debe cumplir simultáneamente una condición **estática** "
        "(soportar la carga) y una condición **dinámica** (alcanzar la deflexión/frecuencia natural necesaria)."
    )

    # ---------------------------------------------------------
    # 3.2 DATOS DE LA MÁQUINA
    # ---------------------------------------------------------
    st.markdown("### 3.2 · Recuperamos los datos de la misma bomba del Laboratorio A")
    st.write(
        "El Laboratorio B **no parte de una bomba nueva**. Recuperamos los datos del caso que ya diagnosticamos."
    )

    rpm=CASE_RPM
    mass=CASE_MASS_KG
    supports=CASE_SUPPORTS
    component="1×RPM"
    multiplier=1.0
    frot=CASE_F_ROT
    fe=CASE_F_ROT

    i1,i2,i3,i4=st.columns(4)
    with i1:
        _card("Velocidad",f"{rpm:.0f} RPM",f"1×RPM = {CASE_F_ROT:.1f} Hz.",tone="blue")
    with i2:
        _card("Masa",f"{mass:.0f} kg","Peso de catálogo de la misma variante SHOS.")
    with i3:
        _card("Apoyos",f"{supports}","Hipótesis del ejercicio: reparto uniforme.",tone="green")
    with i4:
        _card("Componente de diseño","1×RPM","La campaña A la relacionó con la banda de 50 Hz.",tone="purple")

    st.warning(
        "Los **79 kg** corresponden al conjunto catalogado. Si el proyecto incluye una bancada de inercia adicional, "
        "debes sumar su masa y recalcular la carga de cada aislador."
    )

    st.markdown("#### A · De RPM a frecuencia de excitación")
    st.latex(r"f_{\mathrm{giro}}=\frac{\mathrm{RPM}}{60}")
    st.latex(
        fr"f_{{\mathrm{{giro}}}}=\frac{{{rpm}}}{{60}}={frot:.2f}\;\mathrm{{Hz}}"
    )
    if multiplier != 1:
        st.latex(
            fr"f_e={multiplier:g}\,f_{{\mathrm{{giro}}}}={fe:.2f}\;\mathrm{{Hz}}"
        )
    else:
        st.latex(fr"f_e=f_{{\mathrm{{giro}}}}={fe:.2f}\;\mathrm{{Hz}}")

    fd1,fd2,fd3=st.columns(3)
    with fd1:
        _card("1×RPM","una repetición por vuelta","Referencia básica para componentes asociadas al giro.")
    with fd2:
        _card("2×RPM","dos repeticiones por vuelta","Puede aparecer en otros mecanismos periódicos.")
    with fd3:
        _card(
            "Paso de álabes",
            "N × frecuencia de giro",
            "Si el impulsor tiene N álabes, cada vuelta puede producir N excitaciones asociadas al paso de los álabes.",
            tone="blue"
        )

    st.write("Para el paso de álabes, la relación general es:")
    st.latex(r"f_{\mathrm{álabes}}=N\,f_{\mathrm{giro}}")

    st.warning(
        "Para aislamiento se debe comprobar la **frecuencia perturbadora relevante más baja**. "
        "Una frecuencia más baja suele exigir una frecuencia natural todavía menor y, por tanto, mayor deflexión."
    )

    # ---------------------------------------------------------
    # 3.3 CARGA POR APOYO
    # ---------------------------------------------------------
    st.markdown("### 3.3 · Carga que debe soportar cada aislador")
    kg_support=mass/supports
    force_support=kg_support*9.81
    lb_support=kg_support*2.2046226218

    st.latex(r"m_i=\frac{m_{\mathrm{total}}}{N}")
    st.latex(
        fr"m_i=\frac{{{mass}}}{{{supports}}}={kg_support:.1f}\;\mathrm{{kg/apoyo}}"
    )
    st.latex(
        fr"W_i=m_i g={kg_support:.1f}\cdot9.81={force_support:.0f}\;\mathrm{{N}}"
    )

    lc1,lc2,lc3=st.columns(3)
    with lc1:
        _card("Masa por apoyo",f"{kg_support:.1f} kg","Distribución uniforme adoptada en el ejercicio.",tone="green")
    with lc2:
        _card("Peso por apoyo",f"{force_support:.0f} N","Fuerza estática vertical sobre cada aislador.")
    with lc3:
        _card("Carga para catálogo",f"{lb_support:.0f} lb","Unidad usada por el catálogo Kinetics FDS.",tone="blue")

    st.info(
        "En una instalación real no se debe asumir automáticamente que todos los apoyos reciben la misma carga. "
        "La posición del centro de gravedad y la bancada pueden producir cargas diferentes."
    )

    # ---------------------------------------------------------
    # 3.4 RIGIDEZ, DEFLEXIÓN Y FRECUENCIA NATURAL
    # ---------------------------------------------------------
    st.markdown("### 3.4 · ¿Por qué el catálogo habla de carga y deflexión?")
    st.write(
        "Un resorte se caracteriza físicamente por su rigidez. Pero muchos catálogos entregan una **carga nominal** "
        "y la **deflexión que produce esa carga**. Con esos dos datos podemos interpretar su rigidez."
    )

    st.latex(r"\boxed{k_i\approx\frac{F_i}{\delta_i}}")
    st.write(
        "Para varios resortes iguales trabajando en paralelo, la rigidez vertical total es aproximadamente:"
    )
    st.latex(r"k_{\mathrm{tot}}\approx N\,k_i")
    st.write("La frecuencia natural del conjunto aislado es:")
    st.latex(r"\boxed{f_n=\frac{1}{2\pi}\sqrt{\frac{k_{\mathrm{tot}}}{m}}}")

    st.markdown("#### Relación directa con la deflexión estática")
    st.write(
        "En equilibrio estático, el peso del conjunto comprime los resortes hasta alcanzar una deflexión estática. ""Esa deflexión permite relacionar directamente el montaje con su frecuencia natural:"
    )
    st.latex(r"\boxed{f_n=\frac{1}{2\pi}\sqrt{\frac{g}{\delta}}}")
    st.write(
        "Esta ecuación explica por qué la **deflexión** es un parámetro fundamental de catálogo: "
        "a mayor deflexión de trabajo, menor frecuencia natural del sistema."
    )

    ex1,ex2=st.columns(2)
    with ex1:
        _card(
            "Resorte más rígido",
            "menor deflexión",
            "Produce una frecuencia natural más alta y puede entregar menor separación respecto de la excitación.",
            tone="orange"
        )
    with ex2:
        _card(
            "Resorte más flexible",
            "mayor deflexión",
            "Produce una frecuencia natural más baja y normalmente aumenta la separación dinámica.",
            tone="green"
        )

    # ---------------------------------------------------------
    # 3.5 RAZÓN DE FRECUENCIAS Y TRANSMISIBILIDAD
    # ---------------------------------------------------------
    st.markdown("### 3.5 · ¿Cuándo comienza realmente el aislamiento?")
    st.latex(r"\boxed{r=\frac{f_e}{f_n}}")
    st.write(
        "La razón de frecuencias compara la frecuencia de excitación de la bomba con la frecuencia natural del sistema aislado."
    )

    reg1,reg2,reg3,reg4=st.columns(4)
    with reg1:
        _card(
            "r < 1",
            "Excitación bajo fₙ",
            "La frecuencia de la bomba está por debajo de la frecuencia natural del sistema."
        )
    with reg2:
        _card(
            "r ≈ 1",
            "Resonancia",
            "La excitación se aproxima a la frecuencia natural y la respuesta puede amplificarse.",
            tone="orange"
        )
    with reg3:
        _card(
            "1 < r < √2",
            "Zona de transición",
            "La excitación ya superó fₙ, pero todavía no existe una reducción efectiva de fuerza transmitida."
        )
    with reg4:
        _card(
            "r > √2",
            "Región de aislamiento",
            "En el modelo ideal, la fuerza transmitida comienza a ser menor que la fuerza de excitación.",
            tone="green"
        )

    st.latex(
        r"\boxed{T_F="
        r"\sqrt{\frac{1+(2\zeta r)^2}{(1-r^2)^2+(2\zeta r)^2}}}"
    )

    zeta=st.slider(
        "Razón de amortiguamiento ζ",0.01,0.30,0.08,0.01,
        key=f"{ns}_iso_zeta"
    )

    # Curva de transmisibilidad para entender el diseño
    r_curve=np.linspace(0.10,8.0,500)
    tf_curve=np.array([tf_force(rr,zeta) for rr in r_curve])

    fig,ax=plt.subplots(figsize=(9.2,4.0))
    ax.plot(r_curve,tf_curve)
    ax.axhline(1.0,linestyle="--",linewidth=1)
    ax.axvline(1.0,linestyle="--",linewidth=1)
    ax.axvline(math.sqrt(2),linestyle="--",linewidth=1)
    ax.set_xlim(0.1,8)
    ax.set_ylim(0,3.0)
    ax.set_xlabel(r"Razón de frecuencias  r = fₑ/fₙ")
    ax.set_ylabel(r"Transmisibilidad de fuerza  T_F")
    ax.set_title("Transmisibilidad del sistema masa–resorte–amortiguador")
    ax.grid(True,alpha=.22)
    fig.tight_layout()
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    st.caption(
        "La curva muestra por qué no basta con elegir un resorte que 'se vea blando': "
        "la selección debe producir una razón de frecuencias suficiente en el punto real de operación."
    )

    # ---------------------------------------------------------
    # 3.6 OBJETIVO DE DISEÑO
    # ---------------------------------------------------------
    st.markdown("### 3.6 · Convierte el objetivo de aislamiento en una deflexión requerida")
    target_iso=st.slider(
        "Aislamiento objetivo de fuerza (%)",90,99,98,1,
        key=f"{ns}_iso_target"
    )
    tf_target=max(1.0-target_iso/100.0,0.001)

    st.latex(
        fr"T_{{F,\mathrm{{objetivo}}}}=1-\frac{{{target_iso}}}{{100}}={tf_target:.3f}"
    )

    def _r_required(target_tf,z):
        lo=math.sqrt(2.0)+1e-5
        hi=100.0
        if tf_force(hi,z)>target_tf:
            return hi
        for _ in range(90):
            mid=(lo+hi)/2
            if tf_force(mid,z)>target_tf:
                lo=mid
            else:
                hi=mid
        return hi

    r_req=_r_required(tf_target,zeta)
    fn_max=fe/r_req
    delta_min_m=9.81/max((2*math.pi*fn_max)**2,1e-12)
    delta_min_mm=delta_min_m*1000.0

    dr1,dr2,dr3,dr4=st.columns(4)
    with dr1:
        _card("Objetivo",f"{target_iso:.0f} %",f"T_F ≤ {tf_target:.3f}.",tone="green")
    with dr2:
        _card("r mínima",f"≥ {r_req:.2f}","Separación dinámica necesaria.")
    with dr3:
        _card("fₙ máxima",f"≤ {fn_max:.2f} Hz","La frecuencia natural no debería superar este valor.",tone="purple")
    with dr4:
        _card("δ mínima",f"≥ {delta_min_mm:.1f} mm","Deflexión estática requerida por el modelo.",tone="blue")

    st.markdown("#### Sustitución del caso")
    st.latex(
        fr"f_{{n,\max}}=\frac{{f_e}}{{r_{{\min}}}}"
        fr"=\frac{{{fe:.2f}}}{{{r_req:.2f}}}"
        fr"={fn_max:.2f}\;\mathrm{{Hz}}"
    )
    st.latex(
        fr"\delta_{{\min}}="
        fr"\frac{{g}}{{(2\pi f_{{n,\max}})^2}}"
        fr"={delta_min_mm:.1f}\;\mathrm{{mm}}"
    )

    # ---------------------------------------------------------
    # 3.7 PRESELECCIÓN TÉCNICA DE FAMILIAS DE RESORTE
    # ---------------------------------------------------------
    st.markdown("### 3.7 · ¿Qué tipo de resorte deberíamos buscar?")
    st.write(
        "Los catálogos norteamericanos suelen expresar la deflexión de los resortes en **pulgadas**. "
        "Antes de comparar familias debemos entender esa unidad y distinguir entre **deflexión nominal** "
        "y **deflexión real de operación**."
    )

    st.markdown("#### ¿Qué significa “in”?")
    st.write(
        "**in** es la abreviatura inglesa de *inch* (pulgada). En esta etapa siempre mostraremos también "
        "su equivalente en milímetros."
    )
    st.latex(r"1\;\mathrm{in}=25.4\;\mathrm{mm}")
    st.latex(r"4\;\mathrm{in}=101.6\;\mathrm{mm}")

    conv1,conv2=st.columns(2)
    with conv1:
        _card(
            "Familia de 1 pulgada (1 in)",
            "25,4 mm nominales",
            "La familia está diseñada para desarrollar aproximadamente una pulgada de compresión cuando trabaja cerca de su carga nominal.",
            tone="blue"
        )
    with conv2:
        _card(
            "Familia de 4 pulgadas (4 in)",
            "101,6 mm nominales",
            "La familia está diseñada para desarrollar aproximadamente cuatro pulgadas de compresión cuando trabaja cerca de su carga nominal.",
            tone="purple"
        )

    st.markdown("#### Deflexión nominal no significa deflexión real")
    st.write(
        "La cifra de 1 o 4 pulgadas describe la **deflexión nominal de la familia a su carga nominal de catálogo**. "
        "Nuestra bomba puede cargar el resorte con un valor diferente; por eso debemos estimar cuánto se comprimirá realmente."
    )
    st.latex(
        r"\boxed{\delta_{\mathrm{op}}\approx"
        r"\delta_{\mathrm{nom}}\frac{F_{\mathrm{op}}}{F_{\mathrm{nom}}}}"
    )

    dn1,dn2,dn3=st.columns(3)
    with dn1:
        _card(
            "Carga nominal",
            "F_nom",
            "Carga para la que el fabricante declara la deflexión nominal."
        )
    with dn2:
        _card(
            "Carga de operación",
            f"{lb_support:.1f} lb/apoyo",
            "Es la carga que realmente entrega nuestra bomba a cada aislador.",
            tone="green"
        )
    with dn3:
        _card(
            "Deflexión de operación",
            "δ_op",
            "Compresión que realmente desarrollará el resorte con la carga del proyecto.",
            tone="blue"
        )

    st.markdown("#### Apliquémoslo a la misma bomba del caso")
    st.write(
        f"Con {CASE_MASS_KG:.0f} kg distribuidos uniformemente sobre {CASE_SUPPORTS} apoyos, "
        f"cada aislador recibe aproximadamente **{kg_support:.2f} kg**, equivalentes a **{lb_support:.1f} lb**."
    )

    # Ejemplos representativos de las dos familias que después aparecen en el catálogo.
    one_rated_lb=50.0
    one_nom_in=0.97
    four_rated_lb=100.0
    four_nom_in=4.00

    one_op_in=one_nom_in*(lb_support/one_rated_lb)
    one_op_mm=one_op_in*25.4
    one_fn=fn_delta(max(one_op_mm,1e-9))
    one_r=fe/max(one_fn,1e-9)
    one_tf=tf_force(one_r,zeta)
    one_iso=max(0.0,(1-one_tf)*100.0)

    four_op_in=four_nom_in*(lb_support/four_rated_lb)
    four_op_mm=four_op_in*25.4
    four_fn=fn_delta(max(four_op_mm,1e-9))
    four_r=fe/max(four_fn,1e-9)
    four_tf=tf_force(four_r,zeta)
    four_iso=max(0.0,(1-four_tf)*100.0)

    ex1,ex2=st.columns(2)
    with ex1:
        st.markdown("**Ejemplo preliminar · familia de 1 pulgada**")
        _card(
            "Ejemplo FDS 1-50",
            "50 lb nominales · 0,97 in",
            "Usamos este modelo solo para comprender cómo cambia la deflexión cuando la carga real no coincide exactamente con la nominal.",
            tone="blue"
        )
        st.latex(
            fr"\delta_{{\mathrm{{op}}}}\approx"
            fr"0.97\;\mathrm{{in}}\;"
            fr"\frac{{{lb_support:.1f}}}{{50}}"
            fr"={one_op_in:.2f}\;\mathrm{{in}}"
            fr"={one_op_mm:.1f}\;\mathrm{{mm}}"
        )
        st.write(
            f"Con esa deflexión: **fₙ ≈ {one_fn:.2f} Hz**, "
            f"**r ≈ {one_r:.1f}** y aislamiento idealizado ≈ **{one_iso:.1f} %**."
        )

    with ex2:
        st.markdown("**Ejemplo preliminar · familia de 4 pulgadas**")
        _card(
            "Ejemplo FDS 4-100",
            "100 lb nominales · 4,00 in",
            "Aunque la familia se denomine 4 pulgadas, nuestra bomba no desarrolla automáticamente 101,6 mm de deflexión.",
            tone="purple"
        )
        st.latex(
            fr"\delta_{{\mathrm{{op}}}}\approx"
            fr"4.00\;\mathrm{{in}}\;"
            fr"\frac{{{lb_support:.1f}}}{{100}}"
            fr"={four_op_in:.2f}\;\mathrm{{in}}"
            fr"={four_op_mm:.1f}\;\mathrm{{mm}}"
        )
        st.write(
            f"Con esa deflexión: **fₙ ≈ {four_fn:.2f} Hz**, "
            f"**r ≈ {four_r:.1f}** y aislamiento idealizado ≈ **{four_iso:.1f} %**."
        )

    st.markdown("#### Comparación técnica preliminar")
    compare_df=pd.DataFrame([
        [
            "1 pulgada (1 in)",
            "25,4 mm",
            "FDS 1-50",
            f"{one_rated_lb:.0f} lb",
            f"{one_op_mm:.1f} mm",
            f"{one_fn:.2f} Hz",
            f"{one_r:.1f}",
            f"{one_iso:.1f} %",
        ],
        [
            "4 pulgadas (4 in)",
            "101,6 mm",
            "FDS 4-100",
            f"{four_rated_lb:.0f} lb",
            f"{four_op_mm:.1f} mm",
            f"{four_fn:.2f} Hz",
            f"{four_r:.1f}",
            f"{four_iso:.1f} %",
        ],
    ],columns=[
        "Familia",
        "Deflexión nominal de la familia",
        "Ejemplo",
        "Carga nominal",
        "Deflexión estimada con nuestra carga",
        "fₙ estimada",
        "r = fₑ/fₙ",
        "Aislamiento idealizado",
    ])
    st.dataframe(compare_df,hide_index=True,use_container_width=True)

    st.markdown("#### ¿Por qué no elegimos simplemente la familia de mayor deflexión?")
    why1,why2,why3=st.columns(3)
    with why1:
        _card(
            "Dinámica",
            "Más deflexión → menor fₙ",
            "Puede mejorar la separación respecto de la excitación, siempre que el resorte trabaje realmente en el rango previsto.",
            tone="green"
        )
    with why2:
        _card(
            "Carga",
            "Evitar sobredimensionar",
            "Un resorte con capacidad muy superior puede trabajar demasiado descargado, comprimirse poco y perder parte de la ventaja esperada.",
            tone="orange"
        )
    with why3:
        _card(
            "Construcción",
            "Movimiento y estabilidad",
            "Grandes deflexiones implican más recorrido, altura y control de movimientos; también deben revisarse tuberías y restricciones laterales."
        )

    st.info(
        "**Criterio de preselección:** no buscamos el resorte con el número de pulgadas más grande. "
        "Buscamos una familia cuya **carga nominal sea compatible con la carga real** y cuya "
        "**deflexión de operación** permita cumplir la frecuencia natural y transmisibilidad calculadas."
    )

    st.markdown("#### ¿Qué debemos comprobar después en el catálogo?")
    next1,next2,next3,next4=st.columns(4)
    with next1:
        _card(
            "1 · Carga",
            f"≥ {lb_support:.1f} lb",
            "La capacidad del aislador debe ser suficiente para la carga real por apoyo.",
            tone="blue"
        )
    with next2:
        _card(
            "2 · Deflexión real",
            f"≥ {delta_min_mm:.1f} mm",
            "Debe alcanzarse bajo la carga de operación, no solamente a la carga nominal."
        )
    with next3:
        _card(
            "3 · Frecuencia natural",
            f"≤ {fn_max:.2f} Hz",
            "Se recalcula a partir de la deflexión que realmente desarrolla el producto.",
            tone="purple"
        )
    with next4:
        _card(
            "4 · Transmisibilidad",
            f"≤ {tf_target:.3f}",
            "Es la verificación dinámica final del modelo.",
            tone="green"
        )

    st.success(
        "Con esta información ya podemos entrar al Laboratorio C con una **especificación calculada**, "
        "en lugar de abrir el catálogo y escoger un resorte solo por su nombre o capacidad."
    )

    # ---------------------------------------------------------
    # 3.8 FICHA PARA CATALOGO
    # ---------------------------------------------------------
    st.markdown("### 3.8 · Especificación que llevaremos al catálogo")
    spec1,spec2,spec3,spec4=st.columns(4)
    with spec1:
        _card("Carga de operación",f"{lb_support:.0f} lb/apoyo",f"≈ {kg_support:.0f} kg.",tone="blue")
    with spec2:
        _card("Deflexión mínima",f"{delta_min_mm:.1f} mm","Debe alcanzarse bajo la carga real de operación.")
    with spec3:
        _card("fₙ máxima",f"{fn_max:.2f} Hz","Resultado máximo admisible del aislador instalado.",tone="purple")
    with spec4:
        _card("T_F máxima",f"{tf_target:.3f}",f"Objetivo ≈ {target_iso:.0f} % de aislamiento.",tone="green")

    st.markdown("#### Qué deberás leer en la ficha técnica")
    cat_fields=pd.DataFrame([
        ["Modelo / tamaño","Identifica el resorte comercial."],
        ["Rated load / carga nominal","Carga para la cual el fabricante declara la deflexión nominal."],
        ["Rated deflection / deflexión nominal","Compresión del resorte a su carga nominal."],
        ["Free height / altura libre","Altura física del resorte sin carga; sirve para instalación y revisión dimensional."],
        ["Operating load / carga de operación","Nuestra carga calculada; no viene del catálogo, la aporta el proyecto."],
        ["Operating deflection / deflexión real","Debe calcularse para la carga real y comprobar que satisface el requerimiento dinámico."],
    ],columns=["Dato","Para qué sirve"])
    st.dataframe(cat_fields,hide_index=True,use_container_width=True)

    current_design={
        "saved":False,
        "rpm":float(CASE_RPM),
        "pump_model":CASE_MODEL,
        "flow_m3_h":float(CASE_Q),
        "motor_kw":float(CASE_MOTOR_KW),
        "component":component,
        "forcing_multiplier":float(multiplier),
        "fe_hz":float(fe),
        "mass_kg":float(mass),
        "supports":int(supports),
        "load_per_support_kg":float(kg_support),
        "load_per_support_N":float(force_support),
        "load_per_support_lb":float(lb_support),
        "zeta":float(zeta),
        "target_isolation_pct":float(target_iso),
        "target_tf":float(tf_target),
        "required_r":float(r_req),
        "max_fn_hz":float(fn_max),
        "min_deflection_mm":float(delta_min_mm),
    }

    if st.button(
        "Guardar especificación y pasar al catálogo",
        type="primary",
        use_container_width=True,
        key=f"{ns}_iso_save"
    ):
        current_design["saved"]=True
        saved["stage8_isolator_design"]=current_design
        _persist()
        st.success("Especificación guardada. El Laboratorio C utilizará estos requerimientos.")
        st.rerun()

    saved_design=saved.get("stage8_isolator_design",{})
    if isinstance(saved_design,dict) and saved_design.get("saved"):
        st.success(
            f"Especificación activa: {saved_design['load_per_support_lb']:.0f} lb/apoyo · "
            f"δ ≥ {saved_design['min_deflection_mm']:.1f} mm · "
            f"fₙ ≤ {saved_design['max_fn_hz']:.2f} Hz · "
            f"T_F ≤ {saved_design['target_tf']:.3f}."
        )

    # =========================================================
    # 4 · LAB C: SELECCIÓN REAL DE CATÁLOGO
    # =========================================================
    st.markdown("## 4 · Laboratorio C — Selecciona y verifica un aislador de catálogo")

    design=saved.get("stage8_isolator_design",{})
    if not (isinstance(design,dict) and design.get("saved")):
        design=current_design.copy()
        if role=="Docente":
            st.info(
                "Vista docente: se muestran los valores actuales del Laboratorio B para revisar el flujo completo."
            )
        else:
            st.warning(
                "Aún no has guardado la especificación B. Puedes explorar este laboratorio, "
                "pero guarda primero B para conservar la selección al volver."
            )

    req_lb=float(design["load_per_support_lb"])
    req_kg=float(design["load_per_support_kg"])
    req_delta=float(design["min_deflection_mm"])
    req_fn=float(design["max_fn_hz"])
    req_tf=float(design["target_tf"])
    req_iso=float(design["target_isolation_pct"])
    req_fe=float(design["fe_hz"])
    req_zeta=float(design["zeta"])

    st.markdown("### 4.1 · Lo que debe cumplir el producto")
    rr1,rr2,rr3,rr4=st.columns(4)
    with rr1:
        _card("Carga real",f"{req_lb:.0f} lb","Carga de operación por aislador.",tone="blue")
    with rr2:
        _card("δ mínima",f"{req_delta:.1f} mm","Resultado del dimensionamiento B.")
    with rr3:
        _card("fₙ máxima",f"{req_fn:.2f} Hz","Límite dinámico calculado.",tone="purple")
    with rr4:
        _card("T_F máxima",f"{req_tf:.3f}",f"Objetivo ≈ {req_iso:.0f} %.",tone="green")

    st.markdown("### 4.2 · Elige una familia de deflexión")
    family=st.radio(
        "Familia Kinetics FDS a investigar",
        ["FDS 1 in · deflexión nominal ≈ 1 pulgada","FDS 4 in · deflexión nominal = 4 pulgadas"],
        horizontal=True,
        key=f"{ns}_cat_family"
    )

    if family.startswith("FDS 1"):
        catalog_url="https://kineticsnoise.com/files/content/downloads/submittal_drawings/pdf/01/01-20fds/S-01-20-11.pdf"
        catalog_label="Abrir catálogo oficial Kinetics FDS — 1 in"
        models={
            "FDS 1-24":(24.0,1.04),
            "FDS 1-30":(30.0,1.00),
            "FDS 1-37":(37.0,1.00),
            "FDS 1-50":(50.0,0.97),
            "FDS 1-75":(75.0,1.01),
            "FDS 1-100":(100.0,0.98),
            "FDS 1-150":(150.0,1.00),
            "FDS 1-210":(210.0,1.02),
            "FDS 1-300":(300.0,1.00),
            "FDS 1-385":(385.0,1.00),
            "FDS 1-500":(500.0,1.00),
        }
        default_model="FDS 1-50"
    else:
        catalog_url="https://kineticsnoise.com/files/content/downloads/submittal_drawings/pdf/01/01-20fds/S-01-20-41.pdf"
        catalog_label="Abrir catálogo oficial Kinetics FDS — 4 in"
        models={
            "FDS 4-100":(100.0,4.00),
            "FDS 4-250":(250.0,4.00),
            "FDS 4-500":(500.0,4.00),
            "FDS 4-750":(750.0,4.00),
            "FDS 4-1000":(1000.0,4.00),
            "FDS 4-1250":(1250.0,4.00),
            "FDS 4-1600":(1600.0,4.00),
        }
        default_model="FDS 4-1000"

    st.link_button(catalog_label,catalog_url,use_container_width=True)

    st.markdown(
        """
        **Cómo leer la ficha**

        1. busca la fila del modelo;
        2. identifica **Rated Load**;
        3. identifica **Rated Deflection**;
        4. compara la carga nominal con tu **carga de operación**;
        5. calcula la deflexión que realmente desarrollará el resorte bajo tu carga.
        """
    )

    model_names=list(models)
    default_index=model_names.index(default_model) if default_model in model_names else 0
    mc1,mc2,mc3=st.columns(3)
    with mc1:
        model=st.selectbox(
            "Modelo a evaluar",
            model_names,
            index=default_index,
            key=f"{ns}_cat_model"
        )
    with mc2:
        entered_load=st.number_input(
            "Rated Load leído (lb)",
            min_value=10.0,max_value=5000.0,value=50.0,step=1.0,
            key=f"{ns}_cat_lb"
        )
    with mc3:
        entered_def=st.number_input(
            "Rated Deflection leída (in)",
            min_value=0.5,max_value=5.0,value=1.0,step=.01,
            key=f"{ns}_cat_def"
        )

    true_load,true_def=models[model]
    lookup_ok=abs(entered_load-true_load)<=1.0 and abs(entered_def-true_def)<=0.02

    if st.button(
        "Comprobar lectura del catálogo",
        type="primary",
        use_container_width=True,
        key=f"{ns}_cat_check"
    ):
        if lookup_ok:
            saved["stage8_catalog_validated"]=model
            saved["stage8_catalog_lookup"]={
                "family":family,
                "model":model,
                "rated_load_lb":float(true_load),
                "rated_deflection_in":float(true_def),
            }
            _persist()
            st.success("Lectura correcta. Ahora comprobaremos cómo trabaja ese resorte con la carga real.")
            st.rerun()
        else:
            st.warning("Revisa Rated Load y Rated Deflection en la fila seleccionada.")

    if saved.get("stage8_catalog_validated")==model:
        st.markdown("### 4.3 · De valor nominal a condición real de operación")
        st.write(
            "El fabricante declara la deflexión a la **carga nominal**. "
            "Si nuestra carga es distinta, aproximamos la deflexión de operación mediante comportamiento lineal:"
        )
        st.latex(
            r"\boxed{\delta_{\mathrm{op}}\approx"
            r"\delta_{\mathrm{rated}}\frac{F_{\mathrm{op}}}{F_{\mathrm{rated}}}}"
        )

        load_ok=req_lb<=true_load
        op_def_in=true_def*(req_lb/true_load)
        op_def_mm=op_def_in*25.4

        # Rigidez equivalente del aislador en la aproximación lineal
        req_force_N=req_kg*9.81
        k_i_N_m=req_force_N/max(op_def_mm/1000.0,1e-12)

        op_fn=fn_delta(max(op_def_mm,1e-9))
        op_r=req_fe/max(op_fn,1e-12)
        op_tf=tf_force(op_r,req_zeta)
        op_iso=max(0.0,(1-op_tf)*100.0)

        st.latex(
            fr"\delta_{{\mathrm{{op}}}}\approx"
            fr"{true_def:.2f}\,\mathrm{{in}}\;"
            fr"\frac{{{req_lb:.0f}}}{{{true_load:.0f}}}"
            fr"={op_def_in:.2f}\,\mathrm{{in}}"
            fr"={op_def_mm:.1f}\,\mathrm{{mm}}"
        )
        st.latex(
            fr"k_i\approx\frac{{F_i}}{{\delta_{{\mathrm{{op}}}}}}"
            fr"=\frac{{{req_force_N:.0f}}}{{{op_def_mm/1000:.4f}}}"
            fr"\approx{k_i_N_m/1000:.1f}\;\mathrm{{kN/m}}"
        )
        st.latex(
            fr"f_n=\frac{{1}}{{2\pi}}\sqrt{{\frac{{g}}{{\delta_{{\mathrm{{op}}}}}}}}"
            fr"={op_fn:.2f}\;\mathrm{{Hz}}"
        )
        st.latex(
            fr"r=\frac{{{req_fe:.2f}}}{{{op_fn:.2f}}}={op_r:.2f}"
        )

        def_ok=op_def_mm>=req_delta
        fn_ok=op_fn<=req_fn
        tf_ok=op_tf<=req_tf
        overall=load_ok and def_ok and fn_ok and tf_ok

        ck1,ck2,ck3,ck4=st.columns(4)
        with ck1:
            _card(
                "1 · Carga",
                "Cumple" if load_ok else "No cumple",
                f"Operación {req_lb:.0f} lb · nominal {true_load:.0f} lb.",
                tone="green" if load_ok else "orange"
            )
        with ck2:
            _card(
                "2 · Deflexión real",
                f"{op_def_mm:.1f} mm",
                f"Requerida ≥ {req_delta:.1f} mm.",
                tone="green" if def_ok else "orange"
            )
        with ck3:
            _card(
                "3 · Frecuencia natural",
                f"{op_fn:.2f} Hz",
                f"Requerida ≤ {req_fn:.2f} Hz.",
                tone="green" if fn_ok else "orange"
            )
        with ck4:
            _card(
                "4 · Transmisibilidad",
                f"T_F={op_tf:.3f}",
                f"Aislamiento estimado ≈ {op_iso:.1f} %.",
                tone="green" if tf_ok else "orange"
            )

        if overall:
            st.success(
                f"**{model} cumple la especificación dinámica del ejercicio bajo la carga real calculada.**"
            )
        else:
            failed=[]
            if not load_ok: failed.append("carga nominal insuficiente")
            if not def_ok: failed.append("deflexión real insuficiente")
            if not fn_ok: failed.append("frecuencia natural demasiado alta")
            if not tf_ok: failed.append("transmisibilidad mayor al objetivo")
            st.warning("El modelo no cumple completamente: " + "; ".join(failed) + ".")

        if load_ok and req_lb/true_load<0.65:
            st.warning(
                "El aislador está trabajando bastante por debajo de su carga nominal. "
                "Aunque tenga gran capacidad, se comprime menos de lo previsto. "
                "Por eso un resorte 'más grande' no significa automáticamente un aislamiento mejor."
            )

        st.markdown("### 4.4 · Decisión de selección")
        st.write(
            "Una selección correcta debe cumplir **todos** los criterios anteriores y además ser compatible "
            "con restricciones de instalación, estabilidad, conexiones de tubería y eventuales requerimientos sísmicos."
        )

        if st.button(
            "Guardar selección del aislador",
            use_container_width=True,
            key=f"{ns}_cat_eval_save"
        ):
            saved["stage8_catalog_result"]={
                "family":family,
                "model":model,
                "rated_load_lb":float(true_load),
                "rated_deflection_in":float(true_def),
                "required_load_lb":float(req_lb),
                "operating_deflection_mm":float(op_def_mm),
                "stiffness_kN_m":float(k_i_N_m/1000.0),
                "operating_fn_hz":float(op_fn),
                "operating_r":float(op_r),
                "operating_tf":float(op_tf),
                "operating_isolation_pct":float(op_iso),
                "load_ok":bool(load_ok),
                "deflection_ok":bool(def_ok),
                "fn_ok":bool(fn_ok),
                "tf_ok":bool(tf_ok),
                "overall_ok":bool(overall),
            }
            _persist()
            st.success("Selección guardada en el progreso del alumno.")

        if role=="Docente":
            st.markdown("#### Clave docente · qué debería observarse")
            st.info(
                f"Clave del caso: {CASE_MASS_KG:.0f} kg / {CASE_SUPPORTS} apoyos ≈ "
                f"**{req_lb:.1f} lb por aislador**. En la familia FDS de 1 in, el alumno debe buscar "
                "un modelo cuya Rated Load sea suficiente y luego recalcular la deflexión de operación. "
                "El **FDS 1-50** es un candidato lógico para discutir porque su Rated Load es 50 lb y "
                "su Rated Deflection es aproximadamente 0,97 in."
            )

        st.markdown("### 4.5 · El aislador no puede quedar puenteado")
        st.write(
            "La selección de resortes puede ser correcta y aun así fracasar si tuberías, anclajes o conexiones rígidas "
            "crean un camino paralelo entre la bomba y la estructura."
        )
        bridge=st.radio(
            "¿Qué debe verificarse como parte del cierre de la especificación?",
            [
                "Selecciona",
                "Conexiones flexibles y soportes resilientes de tuberías",
                "Conectar rígidamente las tuberías para estabilizar la bomba",
                "Aumentar siempre la capacidad nominal del resorte",
            ],
            key=f"{ns}_bridge"
        )
        if bridge=="Conexiones flexibles y soportes resilientes de tuberías":
            st.success(
                "Correcto. El aislamiento de la base debe mantenerse en los demás caminos mecánicos."
            )
        elif bridge not in ("Selecciona",):
            st.warning("Revisa el concepto de caminos paralelos de transmisión.")

    # =========================================================
    # 5 · CIERRE
    # =========================================================
    st.markdown("## 5 · Cierre — del diagnóstico al control de la bomba")
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:.4rem 0 1rem">
          <div style="border:1px solid #cbd5e1;border-radius:13px;padding:12px;background:#fff"><b>Diagnóstico</b><br><span style="color:#64748b">qué ocurre</span></div>
          <div style="border:1px solid #cbd5e1;border-radius:13px;padding:12px;background:#fff"><b>Mecanismo</b><br><span style="color:#64748b">qué lo genera</span></div>
          <div style="border:1px solid #cbd5e1;border-radius:13px;padding:12px;background:#fff"><b>Camino</b><br><span style="color:#64748b">por dónde viaja</span></div>
          <div style="border:1px solid #cbd5e1;border-radius:13px;padding:12px;background:#fff"><b>Medida</b><br><span style="color:#64748b">dónde actuar</span></div>
          <div style="border:1px solid #bbf7d0;border-radius:13px;padding:12px;background:#f0fdf4"><b>Verificación</b><br><span style="color:#48745a">comprobar resultado</span></div>
        </div>
        """,unsafe_allow_html=True
    )
    st.write(
        "La Etapa 8 termina cuando puedes seguir la cadena completa de una **bomba centrífuga**: "
        "reconocer sus componentes, diseñar una campaña de medición, interpretar evidencia mecánica e hidráulica, "
        "evaluar cavitación mediante NPSH y, finalmente, convertir RPM, masa y carga en una "
        "**especificación antivibratoria verificable contra un catálogo comercial real**."
    )
    st.success(
        "Idea central: primero identifica **qué ocurre y por dónde se transmite**; después selecciona y verifica la medida de control."
    )

    st.markdown("### Fuentes y bibliografía de la Etapa 8")
    st.markdown(
        "- **CIBSE Guide B5 (2002), Noise and vibration control for HVAC** — análisis de caminos de transmisión, bombas y control de vibraciones.\n"
        "- **Harris, C. M.** — principios de vibración de maquinaria y aislamiento vibratorio.\n"
        "- **Lowara / Xylem — SHOE–SHOS–SHOD Series** — curva NPSH–Q utilizada en el laboratorio de cavitación/NPSH.\n"
        "- **Kinetics Noise Control — FDS Free Standing Spring Isolators** — catálogo utilizado para la selección del aislador."
    )


# -----------------------------------------------------------------------------
# Curso 2 · Laboratorio 1 · Etapa 9 — Preguntas de comprensión
# Reutiliza la lógica estructural de evaluación del Diplomado: 4 puntos por
# respuesta, escala chilena 1,0–7,0 con 60 % para nota 4,0, persistencia e9_*
# y una única respuesta final_comprehension en la tabla responses.
# -----------------------------------------------------------------------------
_C2L1_STAGE9_QUESTIONS = [
    {"title":"Transmisión estructural","question":"Una persona camina sobre una losa y se escucha ruido en el recinto inferior. ¿Cuál describe mejor el proceso?","options":["El impacto genera solamente sonido aéreo en el recinto superior.","El impacto introduce energía mecánica en la estructura, la vibración se propaga y las superficies pueden posteriormente radiar sonido.","El ruido aparece exclusivamente por reflexión en el recinto inferior.","La estructura no participa en la transmisión."],"correct":1,"explanation":"El impacto aplica una fuerza dinámica al elemento constructivo. La estructura vibra, la energía se propaga por los sólidos y determinadas superficies pueden radiar sonido al recinto."},
    {"title":"Ruido aéreo vs estructural","question":"¿Cuál es la diferencia fundamental entre ruido aéreo y ruido de origen estructural?","options":["El ruido estructural siempre tiene menor frecuencia.","En el ruido estructural, una parte importante de la energía se transmite mecánicamente por elementos sólidos antes de radiarse como sonido.","El ruido aéreo no puede atravesar elementos constructivos.","Son exactamente el mismo fenómeno."],"correct":1,"explanation":"La diferencia está en el camino de transmisión dominante: en el origen estructural la energía se propaga mecánicamente por sólidos antes de radiarse acústicamente."},
    {"title":"Piso flotante","question":"¿Cuál representa mejor el principio físico de un piso flotante?","options":["Aumentar solamente el espesor del acabado.","Introducir una masa desacoplada de la base mediante un elemento resiliente.","Absorber exclusivamente el sonido dentro del recinto inferior.","Eliminar completamente cualquier vibración estructural."],"correct":1,"explanation":"El piso flotante se idealiza como masas desacopladas mediante un elemento resiliente; su objetivo es reducir la transmisión mecánica, no eliminar toda vibración."},
    {"title":"Rigidez dinámica","question":"Dos pisos flotantes tienen las mismas masas. El sistema A posee menor rigidez dinámica que el sistema B. Manteniendo las demás variables constantes, ¿qué ocurre generalmente con la frecuencia natural de A?","options":["Aumenta.","Disminuye.","Permanece necesariamente igual.","Se vuelve independiente de las masas."],"correct":1,"explanation":"En el modelo estudiado, una menor rigidez dinámica, manteniendo las masas, conduce generalmente a una menor frecuencia natural."},
    {"title":"Frecuencia natural","question":"¿Qué representa f₀ en el modelo del piso flotante estudiado?","options":["La frecuencia de muestreo de un instrumento.","Una frecuencia característica asociada a la resonancia del sistema masa–resorte–masa.","El número único de aislamiento.","La máxima frecuencia transmitida."],"correct":1,"explanation":"f₀ caracteriza la resonancia del sistema dinámico idealizado; no es un descriptor acústico de número único."},
    {"title":"Masa reducida","question":"¿Por qué aparece la masa reducida m’ᵣ en el modelo?","options":["Porque solamente vibra la masa superior.","Porque permite representar la interacción dinámica entre las dos masas del sistema.","Porque reemplaza la rigidez dinámica.","Porque es simplemente el promedio de las dos masas."],"correct":1,"explanation":"La masa reducida representa la interacción dinámica de las dos masas y no corresponde a un promedio aritmético."},
    {"title":"Losa base","question":"¿Qué representa Lₙ,₀(f)?","options":["La mejora del piso flotante.","El nivel estimado de ruido de impacto de la losa base antes de aplicar la mejora del tratamiento.","El número único final.","El ruido de fondo."],"correct":1,"explanation":"Lₙ,₀(f) es la predicción espectral de la condición base, antes de incorporar la mejora del tratamiento."},
    {"title":"Mejora del tratamiento","question":"¿Qué representa ΔLₙ(f)?","options":["El nivel absoluto de ruido de impacto.","La mejora introducida por el tratamiento respecto de la condición base.","La frecuencia natural.","El aislamiento aéreo."],"correct":1,"explanation":"ΔLₙ(f) es una diferencia de niveles que cuantifica la mejora del tratamiento y depende de la frecuencia."},
    {"title":"Dependencia frecuencial","question":"Un sistema presenta ΔLₙ(125 Hz) = 8 dB y ΔLₙ(500 Hz) = 22 dB. ¿Cuál es la interpretación correcta?","options":["Existe un error porque ΔLₙ debe ser constante.","La mejora puede variar con la frecuencia.","El sistema solamente funciona en 500 Hz.","Ambos valores deben promediarse inmediatamente."],"correct":1,"explanation":"La mejora es espectral: ΔLₙ = ΔLₙ(f). Por ello puede adoptar valores distintos en diferentes bandas."},
    {"title":"Predicción final","question":"Si Lₙ,₀(500 Hz) = 69 dB y ΔLₙ(500 Hz) = 22 dB, ¿cuál es Lₙ,final(500 Hz)?","options":["91 dB","47 dB","22 dB","69 dB"],"correct":1,"explanation":"Por definición, Lₙ,final(f) = Lₙ,₀(f) − ΔLₙ(f). En 500 Hz: 69 − 22 = 47 dB."},
    {"title":"Interpretación del modelo","question":"El modelo predice Lₙ,final(500 Hz) = 47 dB. ¿Qué podemos afirmar?","options":["La obra construida medirá necesariamente exactamente 47 dB.","Es un resultado predictivo dentro de las hipótesis y datos de entrada del modelo.","El sistema cumple automáticamente cualquier norma.","Corresponde automáticamente a Lₙ,w."],"correct":1,"explanation":"Una predicción depende del modelo, sus hipótesis y los datos de entrada. No equivale automáticamente a una medición ni demuestra cumplimiento normativo."},
    {"title":"Decisión de diseño","question":"Un sistema presenta menor f₀ que otro. ¿Podemos concluir inmediatamente que es la mejor solución del proyecto?","options":["Sí.","No."],"correct":1,"explanation":"No. También deben considerarse comportamiento espectral, carga, espesor, estabilidad, constructibilidad y durabilidad."},
    {"title":"Puente rígido","question":"Un piso flotante queda conectado accidentalmente a la estructura mediante un contacto rígido perimetral. ¿Qué puede ocurrir?","options":["Nada.","Puede aparecer un camino mecánico paralelo que reduzca el desacoplamiento previsto.","El aislamiento necesariamente mejora.","Solamente cambia el ruido aéreo."],"correct":1,"explanation":"El contacto rígido crea un camino mecánico paralelo capaz de puentear el elemento resiliente y degradar el desacoplamiento idealizado."},
    {"title":"Diagnóstico de instalaciones","question":"Una bomba genera ruido en un dormitorio cercano. ¿Cuál debería ser el primer paso técnico?","options":["Comprar inmediatamente resortes.","Instalar absorbente en el dormitorio.","Identificar los mecanismos de generación y los caminos de transmisión.","Aumentar automáticamente la masa de la bomba."],"correct":2,"explanation":"Antes de seleccionar una medida debe diagnosticarse qué genera el problema y por qué caminos llega al receptor."},
    {"title":"Cavitación","question":"Una bomba presenta cavitación importante. ¿Cuál es la estrategia conceptualmente prioritaria?","options":["Instalar solamente resortes.","Corregir las condiciones hidráulicas que originan la cavitación.","Agregar absorbente al techo.","Aumentar la reverberación."],"correct":1,"explanation":"La prioridad es actuar sobre la fuente del fenómeno: corregir las condiciones hidráulicas que producen cavitación."},
    {"title":"Tuberías como camino","question":"Una bomba está correctamente montada sobre aisladores, pero las tuberías están conectadas rígidamente a la estructura. ¿Qué afirmación es correcta?","options":["El aislamiento de la base garantiza que no exista transmisión estructural.","Las tuberías pueden constituir un camino mecánico paralelo.","Las tuberías solamente transmiten agua.","Los aisladores de la bomba aíslan automáticamente las tuberías."],"correct":1,"explanation":"Las tuberías rígidamente conectadas pueden transmitir fuerza vibratoria y constituir un camino paralelo independiente de los apoyos de la máquina."},
    {"title":"RPM a Hz","question":"Una bomba gira a 1800 rpm. ¿Cuál es su frecuencia de rotación?","options":["18 Hz","30 Hz","60 Hz","1800 Hz"],"correct":1,"explanation":"La frecuencia de rotación es fₑ = n/60. Por tanto, 1800/60 = 30 Hz."},
    {"title":"Región de aislamiento","question":"Para el modelo ideal estudiado, r = fₑ/fₙ. ¿Qué condición marca el comienzo de la región ideal de aislamiento mecánico?","options":["r = 0","r = 1","r > √2","r < 1"],"correct":2,"explanation":"En torno a r = 1 está la resonancia. En el modelo ideal, la región de aislamiento comienza para r > √2; que fₑ sea mayor que fₙ no basta por sí solo."},
    {"title":"Transmisibilidad","question":"Si T_F > 1, ¿qué significa dentro del modelo mecánico?","options":["Existe amplificación de la fuerza transmitida.","Existe aislamiento perfecto.","El nivel acústico disminuye exactamente T_F dB.","No existe vibración."],"correct":0,"explanation":"T_F > 1 significa que la fuerza transmitida está amplificada respecto de la excitación de referencia. T_F no es directamente una reducción acústica en dB."},
    {"title":"Selección de aislador","question":"¿Cuál es la forma técnicamente correcta de seleccionar un aislador?","options":["Bomba = goma; ventilador = resorte.","Considerarlo solamente por el peso total.","Considerar frecuencia de excitación, masa, carga por apoyo, rigidez/deflexión, frecuencia natural, estabilidad y condiciones de instalación.","Elegir siempre el más blando."],"correct":2,"explanation":"La selección exige verificar conjuntamente excitación, carga real por apoyo, propiedades dinámicas, estabilidad y condiciones constructivas; no basta el tipo de equipo."},
    {"title":"Ventilador","question":"Un ventilador transmite vibración por su base y además ruido a través del ducto. ¿Unos buenos aisladores bajo el ventilador resuelven necesariamente ambos problemas?","options":["Sí.","No."],"correct":1,"explanation":"Los aisladores actúan sobre el camino mecánico de la base. El ruido propagado por el ducto requiere medidas específicas para ese camino."},
    {"title":"Silenciador","question":"¿Sobre qué problema actúa principalmente un silenciador de ducto?","options":["Sobre la propagación acústica a través del ducto.","Sobre cualquier vibración transmitida por la base de la máquina.","Sobre la frecuencia natural de un resorte.","Sobre la masa de la losa."],"correct":0,"explanation":"El silenciador se emplea para reducir la propagación acústica por el sistema de ductos; no sustituye el control de vibración de la base."},
    {"title":"Absorción en recinto técnico","question":"Una sala de máquinas presenta alta reverberación. Instalar material absorbente puede:","options":["reducir el campo reverberante del recinto.","eliminar automáticamente la vibración estructural.","corregir la cavitación.","sustituir cualquier aislador."],"correct":0,"explanation":"La absorción puede reducir reflexiones y campo reverberante, pero no corrige por sí sola mecanismos de vibración estructural o cavitación."},
    {"title":"Estrategia combinada","question":"Una bomba presenta simultáneamente cavitación, transmisión por la base y tuberías rígidas. ¿Cuál es la estrategia más correcta?","options":["Utilizar solamente un resorte.","Aplicar una combinación de medidas sobre cada mecanismo.","Instalar solamente absorción en el recinto receptor.","No intervenir porque existen varios mecanismos."],"correct":1,"explanation":"Deben combinarse medidas sobre la fuente, el camino estructural y las conexiones, atendiendo cada mecanismo identificado."},
    {"title":"Enfoque profesional","question":"¿Cuál resume mejor el enfoque del laboratorio?","options":["Siempre debe seleccionarse la solución con menor frecuencia natural.","Todo problema de instalaciones se resuelve mediante aisladores.","Deben identificarse fuente, mecanismo y caminos antes de seleccionar una combinación de medidas.","Si existe ruido, debe añadirse absorbente."],"correct":2,"explanation":"El enfoque profesional parte del diagnóstico: fuente → mecanismo → camino → medida → verificación."},
]


def _c2l1_stage9_submission():
    user_key=st.session_state.get("user_key")
    if not user_key:
        return None
    rows=_remote_rows("responses",class_id="clase-03-impacto-instalaciones-lab-1",user_key=user_key) or []
    row=next((r for r in rows if int(r.get("stage") or -1)==9 and r.get("question_key")=="final_comprehension"),None)
    if not row:
        return None
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try: payload=json.loads(payload)
        except Exception: payload={}
    return {"row":row,"payload":payload if isinstance(payload,dict) else {}}


def _c2l1_finish_stage9(reason="submitted"):
    total=len(_C2L1_STAGE9_QUESTIONS)
    answers={str(i):st.session_state.get(f"e9_q{i}") for i in range(total)}
    score=sum(4 for i,item in enumerate(_C2L1_STAGE9_QUESTIONS)
              if answers.get(str(i))==item["options"][item["correct"]])
    payload={"answers":answers,"reason":reason,"finished_at":_now(),"question_count":total,"points_each":4}
    _save_formative(
        9,"final_comprehension","Etapa 9 · Preguntas de comprensión",
        json.dumps(payload,ensure_ascii=False),
        "Correcta" if score>=60 else "Incorrecta",
        f"Resultado automático: {score}/100 puntos.",score=score,max_score=100,
        correct_answer="Pauta automática de las 25 preguntas disponible después del cierre.",
    )
    st.session_state["e9_submitted"]=True
    st.session_state["e9_score"]=score
    st.session_state["e9_saved_answers"]=answers
    save_user_progress()


def _c2l1_stage9_teacher_view():
    st.info("Vista docente: pauta y resultados de la Etapa 9. La evaluación mantiene 4 puntos por pregunta y la escala 1,0–7,0 con exigencia de 60 %.")
    for i,item in enumerate(_C2L1_STAGE9_QUESTIONS):
        correct=item["options"][item["correct"]]
        with st.container(border=True):
            st.markdown(f"#### Pregunta {i+1} · {item['title']}")
            st.markdown(f"**{item['question']}**")
            for j,opt in enumerate(item["options"]):
                st.write(("✅ " if j==item["correct"] else "○ ")+f"{chr(65+j)}. {opt}")
            st.success(f"Respuesta correcta: {correct}")
            st.info(item["explanation"])
    client=_supabase()
    if client is None:
        return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)")
             .eq("class_id","clase-03-impacto-instalaciones-lab-1").eq("stage",9)
             .eq("question_key","final_comprehension").order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar resultados: {exc}")
        return
    if not raw:
        st.caption("Todavía no hay evaluaciones enviadas.")
        return
    st.markdown("### Respuestas de alumnos y rúbrica")
    def sname(row):
        u=row.get("users") or {}; return u.get("display_name") or row.get("user_key","Alumno")
    ix=st.selectbox("Alumno evaluado",range(len(raw)),format_func=lambda k:f"{sname(raw[k])} · {float(raw[k].get('auto_score') or 0):g}/100",key="c2l1_e9_teacher_student")
    row=raw[ix]; payload=row.get("answer") or {}
    if isinstance(payload,str):
        try: payload=json.loads(payload)
        except Exception: payload={}
    answers=payload.get("answers",{}) if isinstance(payload,dict) else {}
    automatic=[]
    for i,item in enumerate(_C2L1_STAGE9_QUESTIONS):
        chosen=answers.get(str(i)); correct=item["options"][item["correct"]]
        automatic.append(4.0 if chosen==correct else 0.0)
    saved_rubric=payload.get("rubric_scores",[]) if isinstance(payload,dict) else []
    awarded=[]
    for i,item in enumerate(_C2L1_STAGE9_QUESTIONS):
        chosen=answers.get(str(i)); correct=item["options"][item["correct"]]
        with st.container(border=True):
            st.markdown(
                f"#### {i+1}. {item['title']} · "
                f"{'Correcta' if chosen==correct else 'Incorrecta'} · {automatic[i]:g}/4"
            )
            st.write(f"**Respuesta del alumno:** {chosen or 'Sin respuesta'}")
            st.success(f"**Respuesta correcta:** {correct}")
            st.info(item["explanation"])
            default=float(saved_rubric[i]) if i<len(saved_rubric) else automatic[i]
            awarded.append(
                st.number_input(
                    "Puntaje otorgado",0.0,4.0,default,0.5,
                    key=f"c2l1_e9_rubric_{row['id']}_{i}"
                )
            )
    total=float(sum(awarded)); auto=float(sum(automatic))
    note=st.text_area("Observación general para el alumno",value=row.get("teacher_note") or "",key=f"c2l1_e9_note_{row['id']}")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Puntaje automático",f"{auto:g}/100"); c2.metric("Nota automática",f"{_grade_from_percent(auto):.1f}")
    c3.metric("Puntaje ajustado",f"{total:g}/100"); c4.metric("Nota ajustada",f"{_grade_from_percent(total):.1f}")
    if st.button("Guardar rúbrica docente",type="primary",use_container_width=True,key=f"c2l1_e9_save_{row['id']}"):
        updated=dict(payload); updated["rubric_scores"]=awarded
        client.table("responses").update({"answer":updated,"teacher_level":"Correcta" if total>=60 else "Incorrecta","teacher_score":total,"teacher_note":note,"status":"reviewed","updated_at":_now()}).eq("id",row["id"]).execute()
        st.success("Rúbrica y observación docente guardadas.")


def _c2l1_stage_overview(stage_number):
    """Tarjetas propias del Curso 2 · Lab 1 para evitar heredar STAGE_GUIDE del Curso 1."""
    guides = {
        9: [
            ("🧠", "INTERPRETARÁS", "Fenómenos de impacto e instalaciones a partir de mecanismos, magnitudes y caminos de transmisión."),
            ("🧮", "COMPROBARÁS", "Relaciones entre masa, rigidez dinámica, frecuencia natural, mejora espectral y transmisibilidad."),
            ("🛠️", "DECIDIRÁS", "Qué medida de control corresponde según el mecanismo y cómo verificar técnicamente la decisión."),
        ],
        10: [
            ("🏢", "DIAGNOSTICARÁS", "Dos reclamos del mismo edificio: ruido de impacto por pisadas y zumbido nocturno de una bomba."),
            ("🧪", "EXPERIMENTARÁS", "Pisos flotantes, frecuencia natural, respuesta espectral y montajes antivibratorios bajo restricciones reales."),
            ("✅", "JUSTIFICARÁS", "Una estrategia integral de control mediante cálculos, caminos de transmisión, verificación e informe técnico."),
        ],
    }
    cards = guides.get(stage_number, [])
    if not cards:
        return
    html = '<div class="overview">'
    for icon, title, text in cards:
        html += (f'<div class="overview-card"><div class="overview-icon">{icon}</div>'
                 f'<div class="overview-title">{title}</div>'
                 f'<div class="overview-text">{text}</div></div>')
    st.markdown(html + '</div>', unsafe_allow_html=True)


def _render_course2_lab1_stage9(lab, saved):
    header("ETAPA 9 · LABORATORIO 1","PREGUNTAS DE COMPRENSIÓN","COMPRUEBA LO QUE HAS APRENDIDO", show_overview=False)
    _c2l1_stage_overview(9)
    st.write("Antes de resolver el desafío integrador final, revisaremos los conceptos fundamentales del laboratorio. Estas preguntas no buscan solamente recordar definiciones o fórmulas: deberás interpretar fenómenos, resultados, modelos y decisiones de control acústico.")
    st.caption("25 preguntas · 4 puntos por pregunta · 100 puntos totales · exigencia de aprobación: 60 % · misma escala de notas del Diplomado.")
    if st.session_state.get("role")=="Docente":
        _c2l1_stage9_teacher_view(); return
    remote=_c2l1_stage9_submission()
    submitted=bool(remote or st.session_state.get("e9_submitted"))
    if submitted:
        payload=(remote or {}).get("payload",{})
        row=(remote or {}).get("row",{})
        answers=payload.get("answers",{}) or st.session_state.get("e9_saved_answers",{})
        score=float(row.get("teacher_score") if row and row.get("teacher_score") is not None else (row.get("auto_score") if row else st.session_state.get("e9_score",0)) or 0)
        correct=sum(answers.get(str(i))==q["options"][q["correct"]] for i,q in enumerate(_C2L1_STAGE9_QUESTIONS))
        pct=score
        grade=_grade_from_percent(pct)
        st.success(f"Evaluación finalizada · {correct}/25 respuestas correctas · {score:g}/100 puntos · {pct:.0f}% · Nota {grade:.1f}")
        st.caption("El intento está cerrado. Tus respuestas permanecen disponibles para revisión.")
        for i,item in enumerate(_C2L1_STAGE9_QUESTIONS):
            chosen=answers.get(str(i)); correct_opt=item["options"][item["correct"]]
            with st.container(border=True):
                st.markdown(f"#### Pregunta {i+1} · {item['title']}")
                st.markdown(f"**{item['question']}**")
                st.write(f"Tu respuesta: {chosen or 'Sin respuesta'}")
                if chosen==correct_opt:
                    st.success("✓ CORRECTO")
                else:
                    st.error(f"✗ REVISA EL CONCEPTO · Respuesta correcta: {correct_opt}")
                st.info(item["explanation"])
        st.markdown("### YA CONOCES LAS PIEZAS DEL PROBLEMA. AHORA DEBES CONECTARLAS.")
        st.markdown("**SIGUIENTE: ETAPA 10 · DESAFÍO DE INTEGRACIÓN**")
        st.write("En la siguiente etapa deberás enfrentarte a una situación de ingeniería en la que no se indicará directamente qué ecuación o medida utilizar. Deberás identificar el fenómeno, interpretar los datos y justificar una decisión técnica.")
        return
    st.info("Selecciona una alternativa y pulsa COMPROBAR. La respuesta y su retroalimentación quedarán visibles. El estado se conserva con la arquitectura de progreso existente.")
    for i,item in enumerate(_C2L1_STAGE9_QUESTIONS):
        if i==13:
            st.markdown("---"); st.markdown("### De pisos a instalaciones")
            st.info("LOS PRINCIPIOS DE FUERZA, VIBRACIÓN, DESACOPLAMIENTO Y CAMINOS PARALELOS TAMBIÉN APARECEN EN LAS INSTALACIONES DEL EDIFICIO.")
        st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA {i+1} DE 25 · 4 PUNTOS</div><div class="question-text">{item["question"]}</div></div>',unsafe_allow_html=True)
        checked=bool(st.session_state.get(f"e9_checked_{i}"))
        choice=st.radio("Selecciona una alternativa",item["options"],index=None,key=f"e9_q{i}",label_visibility="collapsed",disabled=checked)
        if not checked:
            if st.button("COMPROBAR",key=f"e9_check_{i}",use_container_width=True):
                if choice is None: st.warning("Selecciona una alternativa antes de comprobar.")
                else:
                    st.session_state[f"e9_checked_{i}"]=True; save_user_progress(); st.rerun()
        else:
            correct_opt=item["options"][item["correct"]]
            if st.session_state.get(f"e9_q{i}")==correct_opt: st.success("✓ CORRECTO")
            else: st.error("✗ REVISA EL CONCEPTO")
            st.info(item["explanation"])
            if i==7: st.latex(r"\Delta L_n=\Delta L_n(f)")
            if i==9: st.latex(r"L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)"); st.write("69 − 22 = 47 dB")
            if i==16: st.latex(r"f_e=\frac{n}{60}=\frac{1800}{60}=30\ \mathrm{Hz}")
            if i==23: st.markdown("**CONTROL EN FUENTE + CONTROL ESTRUCTURAL + CONTROL DE CONEXIONES**")
            if i==24: st.markdown("**DIAGNÓSTICO → MECANISMO → CAMINO → MEDIDA → VERIFICACIÓN**")
    answered=sum(st.session_state.get(f"e9_q{i}") is not None for i in range(25))
    checked=sum(bool(st.session_state.get(f"e9_checked_{i}")) for i in range(25))
    st.progress(checked/25); st.caption(f"{checked} de 25 preguntas comprobadas · {answered} respuestas seleccionadas.")
    if st.button("Enviar evaluación definitiva",type="primary",use_container_width=True,key="e9_submit_button"):
        if checked<25:
            st.warning(f"Aún faltan {25-checked} preguntas por comprobar.")
            st.session_state["e9_confirm_incomplete"]=True
        else:
            _c2l1_finish_stage9("submitted"); st.rerun()
    if st.session_state.get("e9_confirm_incomplete") and checked<25:
        if st.button("Confirmar envío con respuestas pendientes",key="e9_submit_incomplete",use_container_width=True):
            _c2l1_finish_stage9("submitted_incomplete"); st.rerun()


# -----------------------------------------------------------------------------
# Curso 2 · Laboratorio 1 · Etapa 10 — Desafío integrador interactivo
# Aislado del contenido de los laboratorios anteriores. Conserva el cierre,
# persistencia, escala 1,0–7,0, exigencia 60 % y puntaje máximo 100 del motor
# de evaluación del Diplomado, pero reemplaza la antigua prueba de alternativas.
# -----------------------------------------------------------------------------
_C2L1_S10_CLASS_ID = "clase-03-impacto-instalaciones-lab-1"
_C2L1_S10_R = {125:35.0, 250:45.0, 500:55.0, 1000:61.0, 2000:67.0}
_C2L1_S10_FLOORS = {
    "Solución A · sistema liviano": {"m1":70.0, "s":25.0, "load":70.0, "thickness":55.0},
    "Solución B · sistema intermedio": {"m1":110.0, "s":12.0, "load":110.0, "thickness":70.0},
    "Solución C · mayor masa y menor rigidez": {"m1":150.0, "s":8.0, "load":150.0, "thickness":85.0},
}
_C2L1_S10_CRITERIA = [
    "comportamiento en bajas frecuencias", "comportamiento espectral general",
    "frecuencia natural", "carga estructural", "espesor disponible",
    "constructibilidad", "riesgo de puentes rígidos",
]

def _c2l1_s10_models():
    from core.course2_impact_models import (
        ln0_above_fc, reduced_mass, natural_frequency,
        delta_ln_cremer_continuous_db, transmissibility_force,
    )
    return ln0_above_fc, reduced_mass, natural_frequency, delta_ln_cremer_continuous_db, transmissibility_force

def _c2l1_s10_restore(saved):
    draft=saved.get("stage10_draft",{}) if isinstance(saved,dict) else {}
    if not isinstance(draft,dict): draft={}
    defaults={
        "c2s10_impact_1":"", "c2s10_impact_2":"", "c2s10_impact_3":"", "c2s10_impact_4":"",
        "c2s10_ln0":0.0, "c2s10_mr":0.0, "c2s10_f0":0.0,
        "c2s10_floor":"", "c2s10_floor_criteria":[], "c2s10_floor_note":"",
        "c2s10_ln250":0.0, "c2s10_ln500":0.0, "c2s10_ln1000":0.0,
        "c2s10_floor_errors":[], "c2s10_fe":0.0, "c2s10_ra":0.0, "c2s10_rb":0.0, "c2s10_rc":0.0,
        "c2s10_paths":[], "c2s10_cavitation":"", "c2s10_controls":[],
        "c2s10_final_limit":"", "c2s10_final_conclusion":"",
    }
    for key,default in defaults.items():
        if key not in st.session_state:
            st.session_state[key]=draft.get(key,default)
    checks=draft.get("checks",{}) if isinstance(draft.get("checks",{}),dict) else {}
    if "c2s10_checks" not in st.session_state: st.session_state["c2s10_checks"]=checks

def _c2l1_s10_save_draft(saved):
    keys=[k for k in st.session_state if str(k).startswith("c2s10_") and k not in {"c2s10_checks"}]
    draft={k:st.session_state.get(k) for k in keys}
    draft["checks"]=dict(st.session_state.get("c2s10_checks",{}))
    saved["stage10_draft"]=draft
    _save_future_state(_C2L1_S10_CLASS_ID,saved)

def _c2l1_s10_check(saved,block,ok,success,feedback):
    checks=dict(st.session_state.get("c2s10_checks",{})); checks[block]=bool(ok)
    st.session_state["c2s10_checks"]=checks; _c2l1_s10_save_draft(saved)
    (st.success if ok else st.warning)(success if ok else feedback)

def _c2l1_s10_scores():
    checks=st.session_state.get("c2s10_checks",{})
    technical=sum(10 for key in ["impact","ln0","floor_math","floor_final","floor_decision","pump_math","inspection","controls"] if checks.get(key))
    final_fields=[st.session_state.get("c2s10_floor"),st.session_state.get("c2s10_paths"),st.session_state.get("c2s10_controls"),st.session_state.get("c2s10_final_limit"),st.session_state.get("c2s10_final_conclusion")]
    report=20 if all(final_fields) and len(str(st.session_state.get("c2s10_final_conclusion","")).split())>=12 else 10 if sum(bool(x) for x in final_fields)>=4 else 0
    return technical,report,min(100,technical+report)

def _c2l1_stage10_submission():
    user_key=st.session_state.get("user_key")
    if not user_key: return None
    rows=_remote_rows("responses",class_id=_C2L1_S10_CLASS_ID,user_key=user_key) or []
    row=next((r for r in rows if int(r.get("stage") or -1)==10 and r.get("question_key")=="final_exam"),None)
    if not row: return None
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try: payload=json.loads(payload)
        except Exception: payload={}
    return {"row":row,"payload":payload if isinstance(payload,dict) else {}}

def _c2l1_finish_stage10(saved,reason="submitted"):
    technical,report,total=_c2l1_s10_scores()
    payload={
        "tipo":"desafio_integrador_interactivo", "reason":reason, "finished_at":_now(),
        "puntaje_tecnico":technical, "puntaje_informe":report,
        "impacto":{"secuencia":[st.session_state.get(f"c2s10_impact_{i}") for i in range(1,5)],"ln0_500":st.session_state.get("c2s10_ln0"),"mr":st.session_state.get("c2s10_mr"),"f0":st.session_state.get("c2s10_f0"),"solucion":st.session_state.get("c2s10_floor"),"criterios":st.session_state.get("c2s10_floor_criteria"),"ln_final":{"250":st.session_state.get("c2s10_ln250"),"500":st.session_state.get("c2s10_ln500"),"1000":st.session_state.get("c2s10_ln1000")},"errores_obra":st.session_state.get("c2s10_floor_errors")},
        "instalaciones":{"fe":st.session_state.get("c2s10_fe"),"rA":st.session_state.get("c2s10_ra"),"rB":st.session_state.get("c2s10_rb"),"rC":st.session_state.get("c2s10_rc"),"caminos":st.session_state.get("c2s10_paths"),"cavitacion":st.session_state.get("c2s10_cavitation"),"medidas":st.session_state.get("c2s10_controls")},
        "informe":{"limitacion":st.session_state.get("c2s10_final_limit"),"conclusion":st.session_state.get("c2s10_final_conclusion")},
        "checks":dict(st.session_state.get("c2s10_checks",{})),
    }
    # Persistencia aislada del Curso 2: no usar _save_formative(), porque ese
    # motor global trabaja con CLASS_ID del laboratorio activo del Curso 1.
    # Aquí la respuesta se guarda explícitamente bajo el class_id de este laboratorio.
    client=_supabase()
    user_key=st.session_state.get("user_key")
    if client is not None and user_key:
        qid=f"{_C2L1_S10_CLASS_ID}-final_exam-v1"
        client.table("questions").upsert({
            "id":qid,"class_id":_C2L1_S10_CLASS_ID,"stage":10,
            "question_key":"final_exam","question_text":"Etapa 10 · Desafío integrador interactivo",
            "correct_answer":"Pauta docente del desafío integrador interactivo.",
            "max_score":100,"content_version":2,"active":True,"updated_at":_now(),
        },on_conflict="id").execute()
        client.table("responses").upsert({
            "course_id":COURSE_ID,"class_id":_C2L1_S10_CLASS_ID,"user_key":user_key,
            "stage":10,"question_key":"final_exam","question_text":"Etapa 10 · Desafío integrador interactivo",
            "correct_answer":"Pauta docente del desafío integrador interactivo.",
            "answer":payload,"auto_level":"Correcta" if total>=60 else "Incorrecta",
            "feedback":f"Desempeño técnico: {technical}/80. Informe integrador: {report}/20.",
            "auto_score":total,"max_score":100,"status":"submitted",
            "updated_at":_now(),"submitted_at":_now(),
        },on_conflict="class_id,user_key,question_key").execute()
    saved["done_10"]=True; saved["stage10_result"]={"score":total,"technical":technical,"report":report,"submitted_at":_now(),"payload":payload}
    _c2l1_s10_save_draft(saved); _save_future_state(_C2L1_S10_CLASS_ID,saved)
    st.session_state["c2l1_exam_submitted"]=True

def _c2l1_stage10_teacher_view():
    ln0_above_fc,reduced_mass,natural_frequency,delta_cremer,transmissibility_force=_c2l1_s10_models()
    ln0=ln0_above_fc(500,55,1); mr,f0=natural_frequency(120,400,10); fe=1450/60
    st.info("Vista docente · solución desarrollada visible. El contenido pedagógico de esta etapa es propio del Curso 2 · Laboratorio 1; no se cargan tarjetas ni preguntas heredadas de laboratorios anteriores.")
    st.markdown("## 1 · Planteamiento completo")
    st.write("Edificio residencial de hormigón armado con dos reclamos simultáneos: ruido de impacto por pisadas desde el departamento superior y zumbido nocturno asociado a una bomba centrífuga. El estudiante debe diagnosticar, calcular, experimentar, identificar caminos y proponer control.")
    st.markdown("## 2 · Datos iniciales")
    st.write("Impacto: R(125–2000 Hz) = 35, 45, 55, 61 y 67 dB; σrad=1. Piso flotante base: m’1=120 kg/m², m’2=400 kg/m², s’=10 MN/m³. Restricciones: carga adicional ≤120 kg/m² y espesor ≤75 mm.")
    st.write("Instalaciones: bomba centrífuga de 600 kg, 1450 rpm y 4 apoyos. Montajes didácticos con fn=14, 8 y 4,5 Hz.")
    st.markdown("## 3 · Procedimiento y ecuaciones")
    st.latex(r"L_{n,0}=43+30\log_{10}(f)-10\log_{10}(\sigma_{rad})-R(f)")
    st.latex(r"m'_r=\frac{m'_1m'_2}{m'_1+m'_2},\qquad f_0=\frac{1}{2\pi}\sqrt{\frac{s'}{m'_r}}")
    st.latex(r"L_{n,final}(f)=L_{n,0}(f)-\Delta L_n(f),\qquad f_e=\frac{n}{60},\qquad r=\frac{f_e}{f_n}")
    st.markdown("## 4 · Cálculos desarrollados")
    st.write(f"A 500 Hz: Lₙ,₀ = {ln0:.1f} dB. Masa reducida = {mr:.1f} kg/m². Frecuencia natural = {f0:.1f} Hz. Frecuencia de rotación de la bomba = {fe:.2f} Hz.")
    st.write(f"Relaciones de frecuencia: A={fe/14:.2f}; B={fe/8:.2f}; C={fe/4.5:.2f}.")
    st.markdown("## 5 · Comparación de soluciones de piso")
    for name,d in _C2L1_S10_FLOORS.items():
        mr_i,f0_i=natural_frequency(d["m1"],400,d["s"])
        st.write(f"**{name}:** m’1={d['m1']:.0f} kg/m² · s’={d['s']:.0f} MN/m³ · m’r={mr_i:.1f} kg/m² · f₀={f0_i:.1f} Hz · carga {'cumple' if d['load']<=120 else 'NO cumple'} · espesor {'cumple' if d['thickness']<=75 else 'NO cumple'}.")
    st.write("Pauta de decisión: la Solución B constituye la referencia didáctica más equilibrada porque conserva carga y espesor dentro de las restricciones y mejora la separación dinámica frente a A; C no es aceptable sin rediseño por exceder las restricciones. La decisión debe justificarse con más de un criterio.")
    st.markdown("## 6 · Inspección de obra")
    st.write("Errores esperados: contacto rígido perimetral, penetración rígida y discontinuidad de la capa resiliente. Estos caminos pueden puentear el desacoplamiento; no se asigna una pérdida fija en dB sin datos.")
    st.markdown("## 7 · Instalaciones y caminos")
    st.write("La coincidencia de una componente cercana a 24 Hz en bomba, tubería, soporte y receptor fortalece la hipótesis de transmisión estructural, pero no demuestra causalidad por sí sola. Deben revisarse base, tuberías, soportes, penetraciones y condición hidráulica.")
    st.markdown("## 8 · Criterios para seleccionar control")
    st.write("Base → aisladores seleccionados por frecuencia y carga real; tuberías → conexiones flexibles y soportes resilientes; penetraciones → desacoplamiento/sellado compatible; cavitación → corregir primero la causa hidráulica; ruido aéreo residual → encierro/absorción/silenciación según el camino real.")
    st.markdown("## 9 · Respuesta profesional esperada")
    st.write("No aprobar la ejecución sin verificaciones adicionales. Deben comprobarse cargas por apoyo, estabilidad, especificaciones dinámicas, continuidad resiliente, ausencia de puentes, conexiones, condiciones hidráulicas y desempeño final medido cuando corresponda.")
    st.markdown("## 10 · Criterios de evaluación")
    st.write("80 puntos por desempeño técnico comprobado en ocho bloques interactivos + 20 puntos por informe integrador completo. Aprobación: 60 %, con la misma conversión de nota del Diplomado.")
    client=_supabase()
    if client is None: return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)").eq("class_id",_C2L1_S10_CLASS_ID).eq("stage",10).eq("question_key","final_exam").order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar resultados: {exc}"); return
    if not raw: st.caption("Todavía no hay desafíos enviados."); return
    st.markdown("## Resultados de alumnos")
    def sname(row):
        u=row.get("users") or {}; return u.get("display_name") or u.get("email") or row.get("user_key","Alumno")
    ix=st.selectbox("Alumno evaluado",range(len(raw)),format_func=lambda k:f"{sname(raw[k])} · {float(raw[k].get('teacher_score') if raw[k].get('teacher_score') is not None else raw[k].get('auto_score') or 0):.1f}/100",key="c2l1_e10_teacher_student")
    row=raw[ix]; payload=row.get("answer") or {}
    if isinstance(payload,str):
        try: payload=json.loads(payload)
        except Exception: payload={}
    score=float(row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score") or 0)
    c1,c2,c3=st.columns(3); c1.metric("Puntaje",f"{score:.1f}/100"); c2.metric("Porcentaje",f"{score:.1f}%"); c3.metric("Nota",f"{_grade_from_percent(score):.1f}")
    st.markdown("### Desarrollo entregado")
    for section in ["impacto","instalaciones","informe"]:
        st.markdown(f"**{section.capitalize()}**")
        st.json(payload.get(section,{}),expanded=True)

def _render_course2_lab1_stage10(lab,saved):
    import numpy as np
    import plotly.graph_objects as go
    ln0_above_fc,reduced_mass,natural_frequency,delta_cremer,transmissibility_force=_c2l1_s10_models()
    _c2l1_s10_restore(saved)
    header("ETAPA 10 · DESAFÍO INTEGRADOR","UN EDIFICIO, DOS PROBLEMAS","Diagnóstico, predicción y control del ruido de impacto y del ruido generado por instalaciones.", show_overview=False)
    _c2l1_stage_overview(10)
    if st.session_state.get("role")=="Docente": _c2l1_stage10_teacher_view(); return

    st.markdown("## 🏢 Problema integrador · Diagnóstico acústico de un edificio residencial")
    st.info(
        "Has sido contratado como **consultor acústico** para estudiar un edificio residencial en el que aparecen "
        "dos problemas simultáneos. En un departamento se perciben con claridad las **pisadas provenientes del piso "
        "superior** y, durante la noche, los residentes reportan un **zumbido asociado a la sala de bombas**. "
        "Tu tarea no es elegir una respuesta de memoria: deberás reconstruir los mecanismos físicos, realizar "
        "predicciones, comparar alternativas de piso flotante y aislamiento vibratorio, detectar caminos paralelos "
        "y terminar proponiendo una estrategia de control técnicamente justificable."
    )
    st.markdown(
        "**Objetivo del desafío:** conectar todo lo aprendido en el laboratorio para responder tres preguntas: "
        "**qué está ocurriendo, por dónde se transmite la energía y qué conjunto de medidas debe verificarse antes "
        "de aprobar una solución.**"
    )
    remote=_c2l1_stage10_submission()
    if remote or st.session_state.get("c2l1_exam_submitted"):
        payload=(remote or {}).get("payload",{}); row=(remote or {}).get("row",{})
        total=float(row.get("teacher_score") if row and row.get("teacher_score") is not None else (row.get("auto_score") if row else saved.get("stage10_result",{}).get("score",0)) or 0)
        st.success(f"Desafío enviado y guardado · {total:.1f}/100 · {total:.1f}% · Nota {_grade_from_percent(total):.1f} · {'APROBADO' if total>=60 else 'REPROBADO'}")
        st.write("El intento está cerrado y el desarrollo permanece guardado.")
        st.markdown("### Resumen final")
        st.json(payload if payload else saved.get("stage10_draft",{}),expanded=True)
        return

    main_asset=ASSET_DIR/"curso2_lab1_etapa10_edificio_integrador.webp"
    if main_asset.exists(): st.image(str(main_asset),width="stretch")
    else: st.info("Render preparado: `curso2_lab1_etapa10_edificio_integrador.webp`. La etapa funciona sin sustituirlo por imágenes heredadas o genéricas.")
    st.write("Actúas como **consultor acústico**. Debes resolver dos reclamos del mismo edificio: pisadas desde el piso superior y un zumbido nocturno asociado a la sala de bombas.")

    st.markdown("## A · Ruido de impacto")
    st.markdown("### 1 · Reconstruye el fenómeno")
    seq_opts=["","Fuerza de impacto","Vibración del piso","Propagación estructural","Radiación acústica"]
    cols=st.columns(4)
    for i,col in enumerate(cols,1):
        col.selectbox(f"Paso {i}",seq_opts,key=f"c2s10_impact_{i}")
    if st.button("COMPROBAR SECUENCIA",key="c2s10_check_impact",width="stretch"):
        got=[st.session_state.get(f"c2s10_impact_{i}") for i in range(1,5)]
        _c2l1_s10_check(saved,"impact",got==seq_opts[1:],"Secuencia correcta.","Revisa la cadena: primero existe una fuerza, luego respuesta vibratoria, propagación por la estructura y finalmente radiación acústica.")

    st.markdown("### 2 · Predice la losa base")
    st.caption("Datos didácticos entregados para el ejercicio: R(125,250,500,1000,2000 Hz) = 35,45,55,61,67 dB; σrad=1.")
    expected_ln0=ln0_above_fc(500,_C2L1_S10_R[500],1.0)
    st.number_input("Calcula Lₙ,₀(500 Hz) [dB]",0.0,120.0,step=0.1,key="c2s10_ln0")
    if st.button("COMPROBAR Lₙ,₀",key="c2s10_check_ln0"):
        _c2l1_s10_check(saved,"ln0",abs(st.session_state.c2s10_ln0-expected_ln0)<=0.6,"Cálculo correcto.","Revisa el signo de R(f), el término logarítmico y σrad. El valor se calcula con el mismo modelo de la Etapa 5.")

    st.markdown("### 3 · Construye el piso flotante")
    mr_expected,f0_expected=natural_frequency(120,400,10)
    c1,c2=st.columns(2)
    c1.number_input("m’ᵣ [kg/m²]",0.0,500.0,step=0.1,key="c2s10_mr")
    c2.number_input("f₀ [Hz]",0.0,300.0,step=0.1,key="c2s10_f0")
    if st.button("COMPROBAR MASA REDUCIDA Y f₀",key="c2s10_check_floor_math",width="stretch"):
        ok=abs(st.session_state.c2s10_mr-mr_expected)<=0.6 and abs(st.session_state.c2s10_f0-f0_expected)<=0.6
        _c2l1_s10_check(saved,"floor_math",ok,"m’ᵣ y f₀ correctos.","Comprueba la masa reducida y recuerda convertir s’ de MN/m³ a N/m³ antes de calcular f₀.")
    st.markdown("#### Experimento · mueve la resonancia")
    ex1=st.slider("Masa superficial superior m’₁ [kg/m²]",50,180,120,key="c2s10_exp_m1")
    exs=st.slider("Rigidez dinámica s’ [MN/m³]",3.0,30.0,10.0,0.5,key="c2s10_exp_s")
    exmr,exf0=natural_frequency(ex1,400,exs)
    a,b=st.columns(2); a.metric("m’ᵣ",f"{exmr:.1f} kg/m²"); b.metric("f₀",f"{exf0:.1f} Hz")
    fig=go.Figure(); fig.add_trace(go.Scatter(x=[10,200],y=[0,0],mode="lines",name="eje")); fig.add_trace(go.Scatter(x=[exf0],y=[0],mode="markers",marker=dict(size=16),name="f₀")); fig.update_xaxes(type="log",title="Frecuencia (Hz)"); fig.update_yaxes(visible=False); fig.update_layout(height=220,margin=dict(l=20,r=20,t=25,b=40)); st.plotly_chart(fig,width="stretch")

    st.markdown("### 4 · Compara soluciones constructivas")
    cards=st.columns(3)
    for col,(name,d) in zip(cards,_C2L1_S10_FLOORS.items()):
        mr_i,f0_i=natural_frequency(d["m1"],400,d["s"])
        with col:
            st.markdown(f"**{name}**")
            st.write(f"m’₁ {d['m1']:.0f} kg/m² · s’ {d['s']:.0f} MN/m³")
            st.write(f"m’ᵣ {mr_i:.1f} kg/m² · f₀ {f0_i:.1f} Hz")
            st.write(f"Carga: {'✓ CUMPLE' if d['load']<=120 else '✗ NO CUMPLE'}")
            st.write(f"Espesor: {'✓ CUMPLE' if d['thickness']<=75 else '✗ NO CUMPLE'}")
    st.selectbox("Solución que recomendarías",[""]+list(_C2L1_S10_FLOORS),key="c2s10_floor")
    st.multiselect("Criterios de decisión · selecciona al menos tres",_C2L1_S10_CRITERIA,key="c2s10_floor_criteria")
    st.text_area("Justificación breve",key="c2s10_floor_note")
    if st.button("COMPROBAR DECISIÓN DE PISO",key="c2s10_check_floor_decision",width="stretch"):
        ok=st.session_state.c2s10_floor.startswith("Solución B") and len(st.session_state.c2s10_floor_criteria)>=3 and len(st.session_state.c2s10_floor_note.strip())>=20
        _c2l1_s10_check(saved,"floor_decision",ok,"Decisión técnicamente coherente para los datos del caso.","No decidas sólo por f₀. Verifica carga, espesor, respuesta espectral y constructibilidad; la solución C excede las restricciones didácticas.")

    st.markdown("### 5 · Construye Lₙ,final(f)")
    selected=st.session_state.get("c2s10_floor") or "Solución B · sistema intermedio"
    d=_C2L1_S10_FLOORS.get(selected,_C2L1_S10_FLOORS["Solución B · sistema intermedio"])
    calc={}
    for f in [250,500,1000]:
        base=ln0_above_fc(f,_C2L1_S10_R[f],1.0); delta,_=delta_cremer(f,d["m1"],d["s"]); calc[f]=base-delta
    c1,c2,c3=st.columns(3); c1.number_input("Lₙ,final(250) [dB]",0.0,120.0,step=0.1,key="c2s10_ln250"); c2.number_input("Lₙ,final(500) [dB]",0.0,120.0,step=0.1,key="c2s10_ln500"); c3.number_input("Lₙ,final(1000) [dB]",0.0,120.0,step=0.1,key="c2s10_ln1000")
    if st.button("COMPROBAR RESULTADO ESPECTRAL",key="c2s10_check_floor_final",width="stretch"):
        ok=all(abs(st.session_state[k]-calc[f])<=0.7 for k,f in [("c2s10_ln250",250),("c2s10_ln500",500),("c2s10_ln1000",1000)])
        _c2l1_s10_check(saved,"floor_final",ok,"Resultados coherentes con el modelo seleccionado.","Recuerda construir cada banda como Lₙ,₀(f) − ΔLₙ(f). ΔLₙ no es una constante.")
    freqs=np.array(list(_C2L1_S10_R),dtype=float); base=np.array([ln0_above_fc(f,_C2L1_S10_R[int(f)],1.0) for f in freqs]); delta=np.array([delta_cremer(f,d["m1"],d["s"])[0] for f in freqs]); final=base-delta
    fig=go.Figure(); fig.add_trace(go.Scatter(x=freqs,y=base,mode="lines+markers",name="Losa base Lₙ,₀")); fig.add_trace(go.Scatter(x=freqs,y=final,mode="lines+markers",name="Piso tratado Lₙ,final")); fig.update_xaxes(type="log",title="Frecuencia (Hz)"); fig.update_yaxes(title="Nivel (dB)"); fig.update_layout(height=390,hovermode="x unified"); st.plotly_chart(fig,width="stretch")

    st.markdown("### 6 · Inspección de obra")
    floor_asset=ASSET_DIR/"curso2_lab1_etapa10_piso_errores.webp"
    if floor_asset.exists(): st.image(str(floor_asset),width="stretch")
    st.multiselect("Encuentra los tres errores",["Contacto rígido perimetral","Penetración rígida de una instalación","Discontinuidad de la capa resiliente","Mayor masa superficial","Absorbente en el recinto"],key="c2s10_floor_errors")

    st.markdown("## B · Ruido de instalaciones")
    st.markdown("### 7 · Frecuencia de excitación y montajes")
    fe_expected=1450/60
    c1,c2=st.columns(2); c1.number_input("fₑ = n/60 [Hz]",0.0,100.0,step=0.01,key="c2s10_fe"); c2.write("Bomba centrífuga · 600 kg · 1450 rpm · 4 apoyos")
    st.write("Montajes didácticos: A fₙ=14 Hz · B fₙ=8 Hz · C fₙ=4,5 Hz")
    a,b,c=st.columns(3); a.number_input("r_A",0.0,20.0,step=0.01,key="c2s10_ra"); b.number_input("r_B",0.0,20.0,step=0.01,key="c2s10_rb"); c.number_input("r_C",0.0,20.0,step=0.01,key="c2s10_rc")
    if st.button("COMPROBAR BOMBA Y MONTAJES",key="c2s10_check_pump_math",width="stretch"):
        ok=abs(st.session_state.c2s10_fe-fe_expected)<=0.15 and abs(st.session_state.c2s10_ra-fe_expected/14)<=0.08 and abs(st.session_state.c2s10_rb-fe_expected/8)<=0.08 and abs(st.session_state.c2s10_rc-fe_expected/4.5)<=0.12
        _c2l1_s10_check(saved,"pump_math",ok,"Conversión y relaciones de frecuencia correctas.","Revisa rpm/60 y calcula cada r con la frecuencia natural de su propio montaje.")
    zeta=st.slider("Amortiguamiento ζ",0.02,0.30,0.08,0.01,key="c2s10_zeta")
    rr=np.linspace(.2,7,240); tf=np.array([transmissibility_force(x,zeta) for x in rr]); fig=go.Figure(); fig.add_trace(go.Scatter(x=rr,y=tf,mode="lines",name="T_F(r)"));
    for label,fn in [("A",14),("B",8),("C",4.5)]:
        r=fe_expected/fn; fig.add_trace(go.Scatter(x=[r],y=[transmissibility_force(r,zeta)],mode="markers+text",text=[label],textposition="top center",name=label))
    fig.update_yaxes(type="log",title="Transmisibilidad de fuerza"); fig.update_xaxes(title="r = fₑ/fₙ"); fig.update_layout(height=390); st.plotly_chart(fig,width="stretch"); st.caption("T_F es una relación mecánica; no se interpreta directamente como una reducción en dB.")

    st.markdown("### 8 · Encuentra los caminos que siguen activos")
    pump_asset=ASSET_DIR/"curso2_lab1_etapa10_bomba_caminos.webp"
    if pump_asset.exists(): st.image(str(pump_asset),width="stretch")
    st.multiselect("Caminos mecánicos",["Tubería rígida","Abrazadera/soporte rígido","Penetración rígida en muro","Aire exterior","Pintura del recinto"],key="c2s10_paths")
    st.radio("Si aparecen síntomas compatibles con cavitación, ¿dónde actuarías primero?",["","Fuente / condición hidráulica","Base antivibratoria","Tubería solamente","Recinto receptor"],key="c2s10_cavitation")
    if st.button("COMPROBAR INSPECCIÓN",key="c2s10_check_inspection",width="stretch"):
        floor_ok=set(st.session_state.c2s10_floor_errors)=={"Contacto rígido perimetral","Penetración rígida de una instalación","Discontinuidad de la capa resiliente"}
        path_ok=set(st.session_state.c2s10_paths)=={"Tubería rígida","Abrazadera/soporte rígido","Penetración rígida en muro"} and st.session_state.c2s10_cavitation=="Fuente / condición hidráulica"
        _c2l1_s10_check(saved,"inspection",floor_ok and path_ok,"Inspección correctamente resuelta.","Busca caminos rígidos que puenteen el desacoplamiento. La cavitación se aborda primero investigando su causa hidráulica, no con absorbentes o aisladores.")

    st.markdown("### 9 · Construye la estrategia de control")
    control_opts=["Aisladores correctamente seleccionados","Conexión flexible","Soportes resilientes","Revisión/desacoplamiento de penetraciones","Corrección hidráulica","Balanceo/alineación cuando corresponda","Tratamiento del ruido aéreo residual si es necesario","Aumento arbitrario de masa","Cambiar automáticamente a neopreno"]
    st.multiselect("Selecciona una estrategia integral",control_opts,key="c2s10_controls")
    if st.button("COMPROBAR ESTRATEGIA",key="c2s10_check_controls",width="stretch"):
        req={"Aisladores correctamente seleccionados","Conexión flexible","Soportes resilientes","Revisión/desacoplamiento de penetraciones","Corrección hidráulica"}; chosen=set(st.session_state.c2s10_controls)
        ok=req.issubset(chosen) and "Aumento arbitrario de masa" not in chosen and "Cambiar automáticamente a neopreno" not in chosen
        _c2l1_s10_check(saved,"controls",ok,"La estrategia cubre fuente, base, conexiones y caminos estructurales.","Una medida única no cubre todos los mecanismos. Revisa base, tuberías, soportes, penetraciones y causa hidráulica.")

    st.markdown("## C · Informe técnico guiado")
    technical,report,total=_c2l1_s10_scores(); st.progress(total/100); st.caption(f"Puntaje acumulado: {total}/100 · desempeño técnico {technical}/80 · informe {report}/20")
    st.write(f"**Problema A:** Lₙ,₀(500) ingresado: {st.session_state.c2s10_ln0:.1f} dB · f₀: {st.session_state.c2s10_f0:.1f} Hz · solución: {st.session_state.c2s10_floor or 'pendiente'}.")
    st.write(f"**Problema B:** fₑ: {st.session_state.c2s10_fe:.2f} Hz · caminos: {', '.join(st.session_state.c2s10_paths) if st.session_state.c2s10_paths else 'pendientes'}.")
    st.selectbox("Limitación/verificación principal antes de ejecutar",["","Verificar cargas reales, especificaciones, ejecución y ausencia de puentes rígidos","Aprobar sin comprobaciones porque el cálculo basta","Verificar sólo el color de los aisladores"],key="c2s10_final_limit")
    st.text_area("Conclusión profesional final",key="c2s10_final_conclusion",placeholder="Integra diagnóstico, cálculos, solución de piso, caminos de la bomba, medidas de control y verificaciones pendientes.")
    c1,c2=st.columns(2)
    if c1.button("GUARDAR DESARROLLO",key="c2s10_save_draft",width="stretch"):
        _c2l1_s10_save_draft(saved); st.success("Desarrollo guardado. Puedes salir y continuar después.")
    technical,report,total=_c2l1_s10_scores()
    if c2.button("ENVIAR EVALUACIÓN DEFINITIVA",type="primary",key="c2s10_submit",width="stretch"):
        if technical<80 or report<20: st.warning("Aún hay bloques sin comprobar o el informe final está incompleto. Puedes guardar el desarrollo y continuar.")
        else: _c2l1_finish_stage10(saved,"submitted"); st.rerun()
    st.markdown("---")
    st.markdown("### Mapa conceptual final")
    st.markdown("**IMPACTO → FUERZA → ESTRUCTURA → LOSA BASE → PISO FLOTANTE → PREDICCIÓN → CONTROL → VERIFICACIÓN → DECISIÓN PROFESIONAL**")
    st.markdown("**INSTALACIÓN → EQUIPO → EXCITACIÓN → CAMINOS → CONTROL EN FUENTE + CONTROL ESTRUCTURAL + CONTROL DE CONEXIONES + CONTROL AÉREO → VERIFICACIÓN → DECISIÓN PROFESIONAL**")

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
        st.link_button(
            "📕 Generar apunte visual (PDF)",
            f"?print_future_lab={class_id}",
            width="stretch",
            help="Abre una vista limpia con las etapas 0 a 10 para imprimirla o guardarla como PDF.",
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

        # Normaliza la etapa guardada antes de construir el selector.
        # Evita ValueError cuando session_state conserva una etapa de una versión
        # anterior del laboratorio que ya no existe en la lista actual.
        _stage_key = f"future_stage_{class_id}"
        _stage_options = list(range(len(lab["stages"])))
        _saved_stage = st.session_state.get(_stage_key)
        if _saved_stage not in _stage_options:
            try:
                _saved_stage = int(_saved_stage)
            except (TypeError, ValueError):
                _saved_stage = 0
            if _saved_stage not in _stage_options:
                _saved_stage = max(_stage_options) if _stage_options else 0
            st.session_state[_stage_key] = _saved_stage

        selected=st.radio(
            "Ruta de aprendizaje",
            _stage_options,
            format_func=lambda i:f"Etapa {i} · {lab['stages'][i][0]}",
            key=_stage_key,
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
        if selected == 2:
            _render_course2_lab1_stage2(lab, saved)
            return
        if selected == 3:
            _render_course2_lab1_stage3(lab, saved)
            return
        if selected == 4:
            _render_course2_lab1_stage4(lab, saved)
            return
        if selected == 5:
            _render_course2_lab1_stage5(lab, saved)
            return
        if selected == 6:
            _render_course2_lab1_stage6(lab, saved)
            return
        if selected == 7:
            _render_course2_lab1_stage7(lab, saved)
            return
        if selected == 8:
            _render_course2_lab1_stage8(lab, saved)
            return
        if selected == 9:
            _render_course2_lab1_stage9(lab, saved)
            return
        if selected == 10:
            _render_course2_lab1_stage10(lab, saved)
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

def future_print_view_impl(lab):
    """Apunte visual imprimible para el Curso 2 · Laboratorio 1."""
    import html

    class_id = lab.get("id", "")
    st.session_state["print_mode"] = True
    st.session_state["projection_mode"] = True
    st.session_state["role"] = "Proyección"
    st.session_state["access"] = True
    st.session_state["user_key"] = "print-preview"
    st.session_state["name"] = "Apunte visual"

    st.markdown("""
        <style>
        [data-testid="stSidebar"], header[data-testid="stHeader"] {display:none !important;}
        .main .block-container {max-width:1050px;padding-top:1rem;padding-bottom:3rem;}
        .print-cover{padding:3rem 2.4rem;border:1px solid #d8e5ef;border-radius:18px;margin-bottom:1.5rem;}
        .print-cover h1{font-size:2.4rem;margin:.3rem 0;color:#0a3559;}
        .print-cover h2{font-size:1.45rem;color:#0b74b5;margin:.2rem 0 1rem;}
        .print-stage{break-before:page;page-break-before:always;margin-top:1.5rem;padding-top:.4rem;}
        .print-note{background:#eef7ff;border-left:4px solid #0b74b5;padding:.8rem 1rem;border-radius:8px;margin:1rem 0;}
        @media print {
          @page {size:A4; margin:12mm 11mm 14mm;}
          .print-note,[data-testid="stSidebar"] {display:none !important;}
          .main .block-container {max-width:none !important;padding:0 !important;}
          body {-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important;}
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(
        f'<section class="print-cover"><div style="font-size:.78rem;letter-spacing:.12em;font-weight:800;color:#0b74b5">DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN</div>'
        f'<h1>Laboratorio {html.escape(str(lab.get("number", "")))}</h1>'
        f'<h2>{html.escape(str(lab.get("focus", "")))}</h2>'
        '<p>Apunte visual generado desde el contenido real del laboratorio. Incluye las etapas 0 a 10, ecuaciones, tablas, gráficos y actividades en su estado de referencia.</p></section>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="print-note"><b>Cómo guardar:</b> pulsa “Imprimir / Guardar PDF”, elige <b>Guardar como PDF</b> y activa los gráficos de fondo.</div>', unsafe_allow_html=True)
    components.html(
        '<div style="display:flex;justify-content:flex-end"><button onclick="window.parent.print()" style="background:#0b5f98;color:white;border:1px solid #63d6f2;border-radius:9px;padding:10px 18px;font-weight:700;cursor:pointer">Imprimir / Guardar PDF</button></div>',
        height=55,
    )

    renderers = {
        0: _render_course2_lab1_welcome, 1: _render_course2_lab1_stage1,
        2: _render_course2_lab1_stage2, 3: _render_course2_lab1_stage3,
        4: _render_course2_lab1_stage4, 5: _render_course2_lab1_stage5,
        6: _render_course2_lab1_stage6, 7: _render_course2_lab1_stage7,
        8: _render_course2_lab1_stage8, 9: _render_course2_lab1_stage9,
        10: _render_course2_lab1_stage10,
    }
    if class_id != "clase-03-impacto-instalaciones-lab-1":
        st.warning("El apunte visual todavía no está integrado para este laboratorio.")
        return
    for stage in range(11):
        st.markdown('<div class="print-stage"></div>', unsafe_allow_html=True)
        try:
            renderers[stage](lab, {})
        except Exception as exc:
            st.warning(f"La Etapa {stage} no pudo renderizarse completamente en modo impresión: {exc}")
    components.html(
        "<script>setTimeout(()=>{const doc=window.parent.document;doc.querySelectorAll('details').forEach(el=>el.open=true);},1800);</script>",
        height=0,
    )


def future_projection_stage_impl(lab, stage):
    """Vista limpia de una etapa futura para la ventana compartida en Zoom."""
    stage = int(stage or 0)
    if stage < 0 or stage >= len(lab.get("stages", [])):
        stage = 0

    st.session_state["projection_mode"] = True
    st.session_state["role"] = "Proyección"
    st.session_state["name"] = "Pantalla de clase"

    # Estado compartido y efímero de la ventana Zoom.
    # Antes cada etapa recibía {}, por lo que tablas, bandas validadas y resultados
    # desaparecían después de cualquier st.rerun().
    #
    # Se utiliza la misma clave que _save_future_state_impl actualiza en sesión,
    # pero projection_mode impide escribir este estado en Supabase.
    projection_saved_key = f"future_saved_{lab.get('id', '')}"
    projection_saved = st.session_state.get(projection_saved_key)
    if not isinstance(projection_saved, dict):
        projection_saved = {}
        st.session_state[projection_saved_key] = projection_saved

    # Curso 2 · Laboratorio 1: las interacciones de Zoom se conservan únicamente
    # durante la sesión de proyección y NO modifican el progreso real.
    if lab.get("id") == "clase-03-impacto-instalaciones-lab-1":
        if stage == 0:
            _render_course2_lab1_welcome(lab, projection_saved)
            return
        if stage == 1:
            _render_course2_lab1_stage1(lab, projection_saved)
            return
        if stage == 2:
            _render_course2_lab1_stage2(lab, projection_saved)
            return
        if stage == 3:
            _render_course2_lab1_stage3(lab, projection_saved)
            return
        if stage == 4:
            _render_course2_lab1_stage4(lab, projection_saved)
            return
        if stage == 5:
            _render_course2_lab1_stage5(lab, projection_saved)
            return
        if stage == 6:
            _render_course2_lab1_stage6(lab, projection_saved)
            return
        if stage == 7:
            _render_course2_lab1_stage7(lab, projection_saved)
            return
        if stage == 8:
            _render_course2_lab1_stage8(lab, projection_saved)
            return
        if stage == 9:
            _render_course2_lab1_stage9(lab, projection_saved)
            return
        if stage == 10:
            _render_course2_lab1_stage10(lab, projection_saved)
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
    "future_print_view": future_print_view_impl,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
