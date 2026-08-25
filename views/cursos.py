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

    st.markdown("#### Pero vibrar no significa radiar eficientemente")
    st.latex(r"\mathrm{VIBRACIÓN\ MEDIBLE \neq RADIACIÓN\ ACÚSTICA\ EFICIENTE}")
    st.write(
        "Para analizar la radiación no necesitamos todavía una fuente concreta. "
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


def _render_course2_lab1_stage2(lab, saved):
    """Curso 2 · Lab 1 · Etapa 2: excitación y respuesta estructural."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")

    def _asset(name):
        p = ASSET_DIR / name
        if p.exists():
            st.image(p, width="stretch")
            return True
        # Desarrollo: placeholder discreto, nunca una imagen inventada.
        if st.session_state.get("dev_mode", False):
            st.caption(f"[Render pendiente: {name}]")
        return False

    def _card(title, body, icon="💡"):
        st.markdown(
            f"""<div style="border:1px solid #cfd8e3;border-radius:12px;padding:16px 18px;
            margin:10px 0 16px;background:#f8fbff">
            <div style="font-weight:800;margin-bottom:7px">{icon} {title}</div>
            <div style="line-height:1.55">{body}</div></div>""",
            unsafe_allow_html=True,
        )

    def _mcq(key, question, options, correct, feedback, store=False):
        st.markdown(f"#### {question}")
        ans = st.radio(
            question, options, index=None,
            key=f"{class_id}_s2_{key}",
            label_visibility="collapsed",
        )
        check_key = f"{class_id}_s2_check_{key}"
        if st.button("Comprobar" + (" y guardar" if store and role == "Alumno" and not projection_mode else ""),
                     key=check_key):
            if ans is None:
                st.warning("Selecciona una alternativa.")
            else:
                ok = options.index(ans) == correct
                st.session_state[f"{check_key}_result"] = ok
                if store and role == "Alumno" and not projection_mode:
                    answers = saved.get("stage2_comprehension", {})
                    if not isinstance(answers, dict):
                        answers = {}
                    answers[key] = {"selected": options.index(ans), "correct": ok, "updated_at": _now()}
                    saved["stage2_comprehension"] = answers
                    saved["updated_2"] = _now()
                    _save_future_state_impl(class_id, saved)
        result = st.session_state.get(f"{check_key}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.error("Aún no. " + feedback)

    header(
        "ETAPA 2 · LABORATORIO 1",
        "Excitación y respuesta estructural",
        "Impedancia, movilidad, resonancia, ondas de flexión y radiación.",
        show_overview=False,
        duration_minutes=55,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.write(
        "Comprender que una misma fuerza dinámica puede producir respuestas vibratorias distintas según "
        "las propiedades dinámicas de la estructura, y relacionar fuerza, movilidad, resonancia, propagación "
        "estructural y radiación acústica."
    )

    # 1 Opening
    st.markdown("### 1 · Misma fuerza, distinta respuesta")
    _asset("curso2_lab1_etapa2_misma_fuerza_distinta_respuesta.webp")
    _mcq(
        "opening",
        "Si la fuerza aplicada es exactamente la misma, ¿ambas estructuras vibrarán igual?",
        [
            "A. Sí, porque la fuerza es la misma.",
            "B. No, porque la respuesta depende también de las propiedades dinámicas de la estructura.",
            "C. Solo depende de la masa.",
            "D. Solo depende del espesor.",
        ],
        1,
        "Una fuerza no determina por sí sola la vibración producida. La respuesta depende de cómo la estructura se comporta dinámicamente en esa frecuencia.",
    )

    # 2 Impedance + mobility
    st.markdown("### 2 · Impedancia mecánica y movilidad")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Impedancia mecánica")
        st.latex(r"Z_m(f)=\frac{F(f)}{v(f)}")
        st.write("**F(f):** fuerza dinámica [N]  \n**v(f):** velocidad vibratoria [m/s]  \n**Zₘ(f):** impedancia mecánica [N·s/m]")
        st.write("Representa la oposición dinámica de una estructura a adquirir velocidad vibratoria frente a una fuerza aplicada.")
        st.latex(r"Z_m\uparrow\Rightarrow v\downarrow \qquad Z_m\downarrow\Rightarrow v\uparrow")
        st.latex(r"Z_m=Z_m(f)")
        st.info("La impedancia mecánica no es simplemente rigidez estática. Es una propiedad dinámica que depende de la frecuencia.")
    with c2:
        st.markdown("#### Movilidad mecánica")
        st.latex(r"Y(f)=\frac{v(f)}{F(f)}")
        st.latex(r"v(f)=Y(f)F(f)")
        st.write("La movilidad indica cuánta velocidad vibratoria desarrolla una estructura por unidad de fuerza aplicada.")
        st.latex(r"Y\uparrow\Rightarrow \text{estructura más fácil de excitar}")
        st.latex(r"Y\downarrow\Rightarrow \text{estructura menos sensible a esa excitación}")
    _card(
        "EN PALABRAS SIMPLES",
        "Imagina que aplicamos la misma fuerza sobre una puerta liviana y sobre un muro de hormigón. "
        "Ambos responden de manera distinta. En vibraciones ocurre algo parecido, pero la respuesta depende además "
        "de la frecuencia a la que aplicamos la fuerza."
    )

    # 3 Numerical example + interactive 2.1
    st.markdown("### 3 · De la fuerza a la velocidad vibratoria")
    st.latex(r"F=100\ \mathrm{N}")
    a,b = st.columns(2)
    with a:
        st.markdown("#### Piso A")
        st.latex(r"Y_A=2\times10^{-6}\ \frac{\mathrm{m/s}}{\mathrm{N}}")
        st.latex(r"v_A=Y_AF=2\times10^{-4}\ \mathrm{m/s}")
    with b:
        st.markdown("#### Piso B")
        st.latex(r"Y_B=8\times10^{-6}\ \frac{\mathrm{m/s}}{\mathrm{N}}")
        st.latex(r"v_B=Y_BF=8\times10^{-4}\ \mathrm{m/s}")
    st.latex(r"\frac{v_B}{v_A}=4")
    st.latex(r"\Delta L_v=20\log_{10}(4)\approx 12\ \mathrm{dB}")
    st.success("La fuente no cambió. Lo que cambió fue la respuesta dinámica del sistema.")

    st.markdown("#### 🔬 Laboratorio de movilidad")
    F = st.slider("Fuerza dinámica F (N)", 10, 500, 100, 10, key=f"{class_id}_s2_F")
    logY = st.slider("log₁₀ de la movilidad Y [m/(N·s)]", -7.0, -3.0, -5.7, 0.1, key=f"{class_id}_s2_logY")
    Y = 10**logY
    v = F*Y
    m1,m2,m3 = st.columns(3)
    m1.metric("Fuerza", f"{F} N")
    m2.metric("Movilidad", f"{Y:.2e} m/(N·s)")
    m3.metric("Velocidad", f"{v:.2e} m/s")
    vib_index = min(100, max(0, (math.log10(max(v,1e-12))+8)/6*100))
    st.progress(vib_index/100)
    st.caption("Indicador visual relativo de magnitud vibratoria; no corresponde a un límite normativo.")

    compare = st.toggle("Comparar con otra estructura", key=f"{class_id}_s2_compare")
    if compare:
        ca, cb = st.columns(2)
        with ca:
            logYA = st.slider("log₁₀ Y_A", -7.0, -3.0, -5.7, 0.1, key=f"{class_id}_s2_logYA")
        with cb:
            logYB = st.slider("log₁₀ Y_B", -7.0, -3.0, -5.1, 0.1, key=f"{class_id}_s2_logYB")
        YA,YB = 10**logYA,10**logYB
        vA,vB = F*YA,F*YB
        ratio = vB/vA
        dlv = 20*math.log10(ratio)
        st.latex(rf"\frac{{v_B}}{{v_A}}={ratio:.2f}")
        st.latex(rf"\Delta L_v={dlv:.1f}\ \mathrm{{dB}}")
        st.info("MISMA FUERZA ≠ MISMA RESPUESTA")

    # 4 Resonance
    st.markdown("### 4 · Resonancia: masa, amortiguamiento y rigidez")
    st.latex(r"m\ddot{x}+c\dot{x}+kx=F(t)")
    r1,r2,r3 = st.columns(3)
    with r1:
        with st.container(border=True):
            st.markdown("**MASA**")
            st.latex(r"m\ddot{x}")
            st.write("Inercia")
    with r2:
        with st.container(border=True):
            st.markdown("**AMORTIGUAMIENTO**")
            st.latex(r"c\dot{x}")
            st.write("Disipación de energía")
    with r3:
        with st.container(border=True):
            st.markdown("**RIGIDEZ**")
            st.latex(r"kx")
            st.write("Fuerza restauradora")
    _card("QUÉ DEBES ENTENDER", "Masa, rigidez y amortiguamiento determinan cómo responde dinámicamente un sistema. Una estructura no responde igual a todas las frecuencias.", "👀")
    st.latex(r"f_0=\frac{1}{2\pi}\sqrt{\frac{k}{m}}")
    st.latex(r"m\uparrow\Rightarrow f_0\downarrow \qquad k\uparrow\Rightarrow f_0\uparrow")

    st.markdown("#### 🔬 Descubre la resonancia")
    cc1,cc2,cc3 = st.columns(3)
    with cc1:
        mass = st.slider("Masa m (kg)", 10.0, 1000.0, 150.0, 10.0, key=f"{class_id}_s2_mass")
    with cc2:
        stiffness = st.slider("Rigidez k (kN/m)", 10.0, 5000.0, 600.0, 10.0, key=f"{class_id}_s2_k")
    f0 = (1/(2*math.pi))*math.sqrt(stiffness*1000/mass)
    with cc3:
        fe = st.slider("Frecuencia de excitación fₑ (Hz)", 1.0, 100.0, min(100.0,max(1.0,f0)), 0.5, key=f"{class_id}_s2_fe")
    st.metric("Frecuencia natural f₀", f"{f0:.2f} Hz")
    # conceptual SDOF curve, fixed damping for visualization only
    import numpy as np
    import matplotlib.pyplot as plt
    freqs = np.linspace(1, 100, 400)
    zeta = 0.08
    rr = freqs/max(f0,1e-9)
    response = 1/np.sqrt((1-rr**2)**2+(2*zeta*rr)**2)
    fig, ax = plt.subplots()
    ax.plot(freqs, response)
    ax.axvline(f0, linestyle="--")
    ax.axvline(fe, linestyle=":")
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("Respuesta relativa")
    ax.set_title("Modelo didáctico de un grado de libertad")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    if abs(fe-f0)/max(f0,1e-9) <= 0.1:
        st.warning("RESONANCIA · La estructura está siendo excitada cerca de su frecuencia natural y la respuesta puede aumentar considerablemente.")
    _mcq(
        "res_energy",
        "¿La resonancia genera energía?",
        ["A. Sí.", "B. No, la energía la aporta la fuente.", "C. Solo si no existe amortiguamiento."],
        1,
        "La resonancia no crea energía. Hace que el sistema responda especialmente bien a la energía suministrada por la fuente."
    )

    # 5 Modes
    st.markdown("### 5 · Una losa real tiene muchos modos")
    st.write("El sistema masa–resorte sirve para comprender la resonancia, pero una losa real es un sistema continuo.")
    st.latex(r"f_1,\quad f_2,\quad f_3,\quad \ldots")
    st.write("Cada frecuencia propia corresponde a una forma particular de deformación denominada **modo propio**.")
    _asset("curso2_lab1_etapa2_modos_placa.webp")

    st.markdown("#### 🔬 Busca la resonancia")
    fscan = st.slider("Frecuencia de exploración f (Hz)", 20, 500, 120, 5, key=f"{class_id}_s2_fscan")
    Fconst = 80.0
    # conceptual multimodal mobility
    fs = np.linspace(20,500,700)
    peaks = [(70,1.0,13),(180,0.75,20),(340,0.55,28)]
    mob = np.full_like(fs,0.08)
    for fp,amp,w in peaks:
        mob += amp/(1+((fs-fp)/w)**2)
    ycur = float(np.interp(fscan,fs,mob))
    vrel = Fconst*ycur
    fig, ax = plt.subplots()
    ax.plot(fs,mob)
    ax.axvline(fscan, linestyle="--")
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("|Y(f)| relativa")
    ax.set_title("Movilidad conceptual con varios modos")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.metric("Respuesta relativa v(f)=Y(f)F", f"{vrel:.1f} u.r.")
    st.info("Un máximo de vibración no demuestra necesariamente que la fuente esté generando más fuerza. Puede corresponder a una resonancia estructural.")

    # 6 Structural waves + bending
    st.markdown("### 6 · Ondas en estructuras")
    w1,w2,w3 = st.columns(3)
    with w1:
        st.markdown("#### Longitudinal")
        st.write("Movimiento aproximadamente paralelo a la dirección de propagación.")
    with w2:
        st.markdown("#### Corte")
        st.write("Movimiento transversal respecto de la propagación.")
    with w3:
        st.markdown("#### Flexión")
        st.write("Deformación transversal de la placa.")
    _asset("curso2_lab1_etapa2_ondas_estructurales.webp")
    st.success("Las ondas de flexión son especialmente importantes en acústica de edificios porque producen movimiento normal de las superficies y pueden contribuir significativamente a la radiación acústica.")

    st.markdown("#### Rigidez flexional y masa superficial")
    q1,q2 = st.columns(2)
    with q1:
        st.latex(r"B=\frac{Eh^3}{12(1-\nu^2)}")
        st.write("**E:** módulo de Young · **h:** espesor · **ν:** coeficiente de Poisson · **B:** rigidez flexional")
        st.latex(r"B\propto h^3")
    with q2:
        st.latex(r"m'=\rho h")
        st.latex(r"m'\propto h")
    _card("COMPARACIÓN CLAVE", "Si duplicamos el espesor, aproximadamente <b>m′ → 2m′</b>, mientras <b>B → 8B</b>. Aumentar el espesor modifica simultáneamente masa y rigidez, pero no en la misma proporción.", "📐")

    st.markdown("#### 🔬 Cambia el espesor")
    h_mm = st.slider("Espesor de hormigón h (mm)", 80, 250, 150, 5, key=f"{class_id}_s2_h")
    # Explicit didactic values, visible for later review
    rho = 2400.0
    E = 30e9
    nu = 0.20
    h = h_mm/1000
    ms = rho*h
    B = E*h**3/(12*(1-nu**2))
    st.caption("Valores utilizados para el ejercicio: ρ = 2400 kg/m³, E = 30 GPa, ν = 0,20. Parámetros explícitos para revisión docente.")
    d1,d2 = st.columns(2)
    d1.metric("Masa superficial m′", f"{ms:.0f} kg/m²")
    d2.metric("Rigidez flexional B", f"{B/1e6:.2f} MN·m")
    hs = np.linspace(.08,.25,100)
    mss = rho*hs
    Bs = E*hs**3/(12*(1-nu**2))
    fig, ax = plt.subplots()
    ax.plot(hs*1000,mss)
    ax.scatter([h_mm],[ms])
    ax.set_xlabel("Espesor (mm)"); ax.set_ylabel("m′ (kg/m²)"); ax.set_title("Masa superficial vs espesor")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True); plt.close(fig)
    fig, ax = plt.subplots()
    ax.plot(hs*1000,Bs/1e6)
    ax.scatter([h_mm],[B/1e6])
    ax.set_xlabel("Espesor (mm)"); ax.set_ylabel("B (MN·m)"); ax.set_title("Rigidez flexional vs espesor")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True); plt.close(fig)

    # 7 Bending waves
    st.markdown("### 7 · Ondas de flexión: una propagación dispersiva")
    st.latex(r"k_B^4=\frac{m'\omega^2}{B}")
    st.latex(r"k_B=\left(\frac{m'\omega^2}{B}\right)^{1/4}")
    st.latex(r"c_B=\frac{\omega}{k_B}")
    st.latex(r"c_B=\left(\frac{B\omega^2}{m'}\right)^{1/4}")
    st.latex(r"\boxed{c_B=c_B(f)}")
    st.write("Las ondas de flexión son **dispersivas**: diferentes frecuencias se propagan con diferentes velocidades de fase.")
    _card("EN PALABRAS SIMPLES", "Las frecuencias graves y agudas no viajan exactamente de la misma manera por una placa.")
    vv1,vv2 = st.columns(2)
    with vv1:
        with st.container(border=True):
            st.markdown("#### Velocidad vibratoria · v")
            st.write("Movimiento local del material.")
    with vv2:
        with st.container(border=True):
            st.markdown("#### Velocidad de propagación · cᵦ")
            st.write("Velocidad a la que avanza la perturbación.")
    st.info("Analogía: una ola avanza por el mar, mientras las partículas de agua se mueven localmente. No son la misma velocidad.")

    # 8 Radiation
    st.markdown("### 8 · De vibración a radiación acústica")
    st.latex(r"W_{\mathrm{rad}}=\rho_0c_0S\sigma\left\langle v_n^2\right\rangle")
    st.write("**ρ₀:** densidad del aire · **c₀:** velocidad del sonido · **S:** superficie radiante · **vₙ:** velocidad normal · **σ:** eficiencia de radiación")
    st.latex(r"\boxed{\sigma=\text{eficiencia de radiación}}")
    st.write("Dos superficies que vibran con la misma velocidad no necesariamente radian la misma potencia sonora.")
    st.latex(r"\boxed{\text{VIBRACIÓN ELEVADA}\neq\text{RADIACIÓN ELEVADA NECESARIAMENTE}}")
    _asset("curso2_lab1_etapa2_vibracion_radiacion.webp")

    st.markdown("#### 🔬 De vibración a sonido")
    vn = st.slider("Velocidad normal vₙ (mm/s)", 0.1, 10.0, 2.0, 0.1, key=f"{class_id}_s2_vn")/1000
    S = st.slider("Área radiante S (m²)", 0.5, 30.0, 8.0, 0.5, key=f"{class_id}_s2_S")
    sigma = st.slider("Eficiencia de radiación σ", 0.01, 1.50, 0.30, 0.01, key=f"{class_id}_s2_sigma")
    Wrel = S*sigma*vn**2
    st.metric("Potencia acústica relativa", f"{Wrel:.3e} u.r.")
    st.progress(min(1.0, max(0.0, math.log10(1+Wrel*1e6)/4)))
    st.caption("Simulación didáctica basada en Wrad ∝ S·σ·vₙ². No representa un nivel acústico normativo.")

    # 9 Integration + final exercise
    st.markdown("### 9 · Integra la cadena")
    st.latex(r"\boxed{F(f)\rightarrow Y(f)\rightarrow v(f)\rightarrow \mathrm{PROPAGACIÓN}\rightarrow \sigma(f)\rightarrow W_{\mathrm{rad}}(f)\rightarrow L_p(f)}")
    g1,g2,g3,g4,g5 = st.columns(5)
    for col, title, body in zip(
        [g1,g2,g3,g4,g5],
        ["FUENTE","RESPUESTA","PROPAGACIÓN","RADIACIÓN","RECEPTOR"],
        ["F","Y, v","Ondas estructurales","σ, W","Lₚ"]
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(body)

    st.markdown("#### Ejercicio final de la etapa")
    st.latex(r"F=80\ \mathrm{N},\quad Y_A=3\times10^{-6},\quad Y_B=12\times10^{-6}\ \frac{\mathrm{m/s}}{\mathrm{N}}")
    e1,e2 = st.columns(2)
    with e1:
        va_in = st.number_input("Paso 1 · v_A (m/s)", min_value=0.0, format="%.6f", key=f"{class_id}_s2_ex_va")
        ratio_in = st.number_input("Paso 3 · v_B/v_A", min_value=0.0, format="%.2f", key=f"{class_id}_s2_ex_ratio")
    with e2:
        vb_in = st.number_input("Paso 2 · v_B (m/s)", min_value=0.0, format="%.6f", key=f"{class_id}_s2_ex_vb")
        dl_in = st.number_input("Paso 4 · ΔL_v (dB)", format="%.1f", key=f"{class_id}_s2_ex_dl")
    if st.button("Comprobar ejercicio", key=f"{class_id}_s2_ex_check"):
        ok = (
            abs(va_in-2.4e-4) <= 2e-6 and abs(vb_in-9.6e-4) <= 2e-6
            and abs(ratio_in-4) <= .05 and abs(dl_in-12.04) <= .2
        )
        if ok:
            st.success("Correcto: v_A = 2,4×10⁻⁴ m/s; v_B = 9,6×10⁻⁴ m/s; razón = 4; ΔL_v ≈ 12,0 dB.")
        else:
            st.warning("Revisa v=YF y luego ΔL_v=20 log₁₀(v_B/v_A).")
    _mcq(
        "interpretation",
        "¿Podemos concluir que el recinto receptor tendrá exactamente 12 dB más de ruido con el Piso B?",
        ["A. Sí.", "B. No."],
        1,
        "Todavía debemos considerar propagación estructural, superficie radiante y eficiencia de radiación. La velocidad vibratoria es una parte de la cadena, no el resultado acústico final."
    )

    # 10 comprehension
    st.markdown("### 10 · Preguntas de comprensión de la etapa")
    st.caption("Formativas y no calificadas.")
    qs = [
        ("q1","Una movilidad elevada significa:",
         ["A. Mayor aislamiento aéreo.","B. Mayor velocidad vibratoria por unidad de fuerza.","C. Mayor masa.","D. Menor frecuencia necesariamente."],1,
         "La movilidad es v/F: expresa la velocidad vibratoria desarrollada por unidad de fuerza."),
        ("q2","Un pico de vibración con fuerza constante puede deberse a:",
         ["A. Una resonancia estructural.","B. Aumento automático de masa.","C. Desaparición del sonido.","D. Aumento obligatorio de la fuerza."],0,
         "Un pico de movilidad puede elevar la respuesta aunque la fuerza aplicada permanezca constante."),
        ("q3","¿Velocidad vibratoria y velocidad de propagación son la misma magnitud?",
         ["A. Sí.","B. No."],1,
         "La velocidad vibratoria describe el movimiento local; la velocidad de propagación describe el avance de la perturbación."),
        ("q4","Dos placas presentan la misma velocidad vibratoria. ¿Deben radiar exactamente la misma potencia acústica?",
         ["A. Sí.","B. No."],1,
         "La potencia radiada depende también del área y de la eficiencia de radiación, entre otros factores."),
    ]
    for q in qs:
        _mcq(*q, store=True)

    st.markdown("### Cierre")
    st.latex(r"\boxed{F\not\Rightarrow L_p}")
    st.latex(r"\boxed{F\rightarrow Y\rightarrow v\rightarrow \mathrm{PROPAGACIÓN}\rightarrow \sigma\rightarrow W\rightarrow L_p}")
    st.success(
        "Ahora sabemos que una misma fuerza puede producir respuestas muy distintas dependiendo de la estructura. "
        "En la siguiente etapa utilizaremos esta cadena para diagnosticar situaciones reales de impacto e instalaciones."
    )

    left,right = st.columns(2)
    with left:
        if st.button("← Etapa 1", key=f"s2_prev_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 1
            st.rerun()
    with right:
        if st.button("Etapa 3 →", key=f"s2_next_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 3
            st.rerun()


def _render_course2_lab1_stage3(lab, saved):
    """Curso 2 · Lab 1 · Etapa 3: diagnóstico vibroacústico."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")
    ns = f"{class_id}_s3"

    import numpy as np
    import matplotlib.pyplot as plt

    def _asset(name, caption=None):
        p = ASSET_DIR / name
        if p.exists():
            st.image(p, width="stretch")
            if caption:
                st.caption(caption)
            return True
        st.info("Render pendiente de incorporar en assets.")
        return False

    def _card(title, body, icon="💡"):
        st.markdown(
            f"""<div style="border:1px solid #cfd8e3;border-radius:12px;padding:16px 18px;
            margin:10px 0 16px;background:#f8fbff">
            <div style="font-weight:800;margin-bottom:7px">{icon} {title}</div>
            <div style="line-height:1.55">{body}</div></div>""",
            unsafe_allow_html=True,
        )

    def _mcq(key, question, options, correct, feedback, multi=False, correct_set=None):
        st.markdown(f"#### {question}")
        state_key = f"{ns}_{key}"
        if multi:
            selected = []
            for i,opt in enumerate(options):
                if st.checkbox(opt, key=f"{state_key}_{i}"):
                    selected.append(i)
            answer = set(selected)
        else:
            val = st.radio(question, options, index=None, key=state_key, label_visibility="collapsed")
            answer = None if val is None else options.index(val)
        if st.button("Comprobar", key=f"{state_key}_check"):
            if (multi and not answer) or (not multi and answer is None):
                st.warning("Selecciona una respuesta.")
            else:
                ok = answer == (set(correct_set) if multi else correct)
                st.session_state[f"{state_key}_result"] = ok
        result = st.session_state.get(f"{state_key}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.warning("Revisa la hipótesis. " + feedback)

    header(
        "ETAPA 3 · LABORATORIO 1",
        "Diagnóstico vibroacústico: de la molestia al camino de transmisión",
        "Aplicación práctica: formular y comprobar hipótesis físicas antes de seleccionar una solución.",
        show_overview=False,
        duration_minutes=60,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.write(
        "Analizar un problema real de ruido estructural distinguiendo reclamo, fuente, excitación, camino, "
        "radiación, receptor y evidencia experimental."
    )
    st.latex(r"\boxed{\mathrm{RECLAMO}\rightarrow\mathrm{FUENTE}\rightarrow\mathrm{EXCITACIÓN}\rightarrow\mathrm{CAMINO}\rightarrow\mathrm{RADIACIÓN}\rightarrow\mathrm{RECEPTOR}}")

    st.markdown("### 1 · Del reclamo al diagnóstico")
    q1,q2,q3 = st.columns(3)
    for col, quote in zip([q1,q2,q3], ["“Escucho pasos.”","“Hay un zumbido durante la noche.”","“Cada vez que descargan el WC se escucha en mi dormitorio.”"]):
        with col:
            with st.container(border=True):
                st.markdown(f"### {quote}")
    st.write("Estas frases describen una **molestia**, pero todavía no constituyen un diagnóstico acústico.")
    st.latex(r"\boxed{\mathrm{MOLESTIA}\neq\mathrm{DIAGNÓSTICO}}")
    _card("DIAGNOSTICAR", "Formular y comprobar una hipótesis física.", "🔎")

    st.markdown("### 2 · Metodología de diagnóstico")
    nodes = [
        ("1 · RECLAMO","¿Qué percibe el usuario?"),
        ("2 · FUENTE","¿Qué sistema podría generar la energía?"),
        ("3 · EXCITACIÓN","¿Cómo ingresa la energía?"),
        ("4 · CAMINO","¿Por dónde puede propagarse?"),
        ("5 · RADIACIÓN","¿Qué superficie puede convertir vibración en sonido?"),
        ("6 · EVIDENCIA","¿Qué observaríamos o mediríamos para comprobar la hipótesis?"),
    ]
    cols = st.columns(3)
    for i,(title,body) in enumerate(nodes):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(body)
    st.latex(r"\boxed{\mathrm{HIPÓTESIS}\rightarrow\mathrm{VERIFICACIÓN}\rightarrow\mathrm{CONTROL}}")
    st.info("En esta etapa el control aparece después del diagnóstico, no antes.")

    st.markdown("## 🔎 DIAGNOSTICA EL EDIFICIO")
    _asset("curso2_lab1_etapa3_diagnostico_edificio.webp")
    case = st.radio(
        "Selecciona un reclamo para investigarlo:",
        ["👣 CASO A — Pisadas","⚙️ CASO B — Zumbido de bomba","🚿 CASO C — Descarga sanitaria"],
        horizontal=True, key=f"{ns}_case"
    )

    if case.startswith("👣"):
        st.markdown("### CASO A · Pisadas")
        st.info("“Escucho claramente los pasos del departamento superior, especialmente durante la noche.”")
        st.write("El dormitorio está inmediatamente bajo otro departamento. El piso superior posee una losa estructural con acabado duro.")
        _mcq(
            "a1","A1 · ¿Cuál es la fuente inicial de energía?",
            ["A. El aire del dormitorio superior.","B. El contacto pie–piso.","C. El cielo del dormitorio receptor.","D. El muro lateral."],
            1,"La pisada aplica una fuerza dinámica F(t) directamente sobre el sistema de piso."
        )
        st.latex(r"F(t)")
        st.markdown("#### A2 · Identifica el camino directo")
        direct = ["PIE","PISO / LOSA","CARA INFERIOR DE LOSA","AIRE DEL DORMITORIO","RECEPTOR"]
        chosen = st.multiselect("Selecciona los elementos que forman el camino directo:", direct, key=f"{ns}_a2")
        if st.button("Comprobar camino directo", key=f"{ns}_a2_check"):
            if set(chosen) == set(direct):
                st.success("CAMINO DIRECTO identificado: PIE → PISO/LOSA → CARA INFERIOR → AIRE → RECEPTOR.")
            else:
                st.warning("Sigue la energía desde el contacto mecánico hasta la radiación hacia el dormitorio.")
        st.markdown("#### A3 · Posibles flancos")
        flanks = ["Muro lateral","Fachada","Pilar","Tabique conectado","Aire exterior"]
        flank_sel = st.multiselect("¿Qué elementos podrían participar en una transmisión estructural indirecta?", flanks, key=f"{ns}_a3")
        if st.button("Interpretar selección", key=f"{ns}_a3_check"):
            structural = {"Muro lateral","Fachada","Pilar","Tabique conectado"}
            good = set(flank_sel) <= structural and len(flank_sel)>0
            if good:
                st.success("Selección físicamente plausible. La existencia de estos caminos no implica que sean dominantes.")
            else:
                st.info("Los flancos estructurales requieren conexión mecánica con la losa. El aire exterior no es, por sí mismo, un flanco estructural.")
        _mcq(
            "a_interpret","Si medimos una vibración elevada en un muro lateral, ¿podemos concluir inmediatamente que ese muro es el camino dominante?",
            ["A. Sí.","B. No."],1,
            "Una vibración elevada es evidencia, pero debe relacionarse con la fuente, la propagación, la radiación del elemento y la respuesta en el receptor."
        )

    elif case.startswith("⚙️"):
        st.markdown("### CASO B · Bomba centrífuga")
        st.info("Durante la noche se percibe un zumbido en una vivienda ubicada sobre una sala técnica con una bomba centrífuga.")
        _asset("curso2_lab1_etapa3_bomba_camino.webp")
        st.markdown("#### Mini ejercicio · frecuencia de rotación")
        rpm = st.number_input("Velocidad de giro n (rpm)", min_value=0.0, value=1500.0, step=50.0, key=f"{ns}_rpm")
        fr_input = st.number_input("Calcula fᵣ = n/60 (Hz)", min_value=0.0, step=1.0, key=f"{ns}_fr")
        if st.button("Comprobar cálculo", key=f"{ns}_fr_check"):
            expected = rpm/60.0
            if abs(fr_input-expected) <= 0.05:
                st.success(f"Correcto: fᵣ = {expected:.1f} Hz.")
            else:
                st.warning(f"Revisa fᵣ=n/60. Para {rpm:.0f} rpm, fᵣ={expected:.1f} Hz.")
        fr = rpm/60.0 if rpm else 0
        st.latex(rf"f_r={fr:.1f}\ \mathrm{{Hz}},\qquad 2f_r={2*fr:.1f}\ \mathrm{{Hz}},\qquad 3f_r={3*fr:.1f}\ \mathrm{{Hz}}")
        st.caption("Una máquina rotatoria puede presentar componentes relacionadas con su frecuencia de rotación y otros fenómenos periódicos. La presencia de armónicos depende de la fuente y del sistema.")

        st.markdown("#### B1 · Espectro conceptual")
        f = np.linspace(5,100,600)
        def peak(fc,amp,w):
            return amp*np.exp(-0.5*((f-fc)/w)**2)
        spectrum = 28 + peak(25,22,2.2)+peak(50,17,2.8)+peak(75,9,3.2)
        fig,ax = plt.subplots()
        ax.plot(f,spectrum)
        ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("Magnitud relativa (dB)")
        ax.set_title("Ejemplo didáctico · respuesta espectral en la losa")
        ax.grid(True,alpha=.2)
        st.pyplot(fig,use_container_width=True); plt.close(fig)
        _mcq(
            "b1","El espectro medido en la losa presenta máximos cercanos a 25 y 50 Hz. ¿Qué podemos afirmar?",
            ["A. La bomba es con certeza la única fuente.","B. Existe evidencia compatible con una excitación relacionada con la bomba, pero se necesita comprobar la relación causal.","C. El ruido es necesariamente aéreo.","D. El máximo de 50 Hz demuestra que existe resonancia."],
            1,"La coincidencia espectral permite formular una hipótesis, pero no demuestra por sí sola causalidad."
        )
        st.latex(r"\boxed{\mathrm{COINCIDENCIA\ FRECUENCIAL}\neq\mathrm{PRUEBA\ DE\ CAUSALIDAD}}")

        st.markdown("#### B2 · Identifica los caminos físicamente posibles")
        routes = [
            "BOMBA → BASE → LOSA  · estructural",
            "BOMBA → TUBERÍA → SOPORTE → ESTRUCTURA  · estructural",
            "CARCASA → AIRE → CERRAMIENTO  · aéreo",
        ]
        route_sel = st.multiselect("Selecciona las rutas posibles:", routes, key=f"{ns}_b2")
        if st.button("Comprobar rutas", key=f"{ns}_b2_check"):
            if set(route_sel)==set(routes):
                st.success("Correcto: los tres caminos son físicamente posibles y pueden coexistir.")
            else:
                st.warning("No descartes un camino únicamente porque exista otro. La bomba puede excitar simultáneamente base, tubería y aire.")

        st.markdown("#### 📍 B3 · Selecciona puntos de diagnóstico")
        points = ["Carcasa de bomba","Bancada","Losa junto a la bomba","Tubería de impulsión","Soporte de tubería","Muro del dormitorio","Aire del dormitorio"]
        point_sel = st.multiselect("Elige uno o varios puntos para investigar el problema:", points, key=f"{ns}_b3")
        explanations = {
            "Carcasa de bomba":"Caracteriza la respuesta de la fuente.",
            "Bancada":"Permite observar la energía transmitida hacia el apoyo.",
            "Losa junto a la bomba":"Permite analizar la entrada de vibración a la estructura.",
            "Tubería de impulsión":"Permite investigar un camino estructural paralelo.",
            "Soporte de tubería":"Permite verificar transferencia tubería–estructura.",
            "Muro del dormitorio":"Permite comprobar si la vibración alcanza una superficie potencialmente radiante.",
            "Aire del dormitorio":"Entrega el resultado acústico final.",
        }
        for p in point_sel:
            _card(p, explanations[p], "📍")
        st.info("Medir solamente el nivel acústico en el dormitorio cuantifica el resultado, pero no necesariamente identifica el camino dominante.")

        st.markdown("#### B4 · Comparación espectral")
        curve_names = ["Bomba","Losa","Tubería","Muro receptor","Lp dormitorio"]
        curve_sel = st.multiselect("Activa o desactiva curvas:", curve_names, default=["Bomba","Losa","Tubería","Muro receptor"], key=f"{ns}_b4")
        profiles = {
            "Bomba": (38,24,17,8),
            "Losa": (30,18,13,6),
            "Tubería": (33,21,14,7),
            "Muro receptor": (25,12,8,4),
            "Lp dormitorio": (22,10,7,3),
        }
        fig,ax = plt.subplots()
        for name in curve_sel:
            base,p25,p50,p75 = profiles[name]
            y=base+peak(25,p25,2.3)+peak(50,p50,3.0)+peak(75,p75,3.5)
            ax.plot(f,y,label=name)
        ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("Magnitud relativa (dB)")
        ax.set_title("Comparación espectral didáctica")
        ax.grid(True,alpha=.2)
        if curve_sel: ax.legend()
        st.pyplot(fig,use_container_width=True); plt.close(fig)
        _mcq(
            "b_final","Si el máximo de 25 Hz aparece en la bomba, tubería, losa y muro receptor, ¿la hipótesis de transmisión estructural se fortalece?",
            ["A. Sí.","B. No."],0,
            "La presencia coherente de una componente asociada a la fuente en varios puntos del camino constituye evidencia más sólida, aunque no es una prueba absoluta."
        )

    else:
        st.markdown("### CASO C · Descarga sanitaria")
        st.info("“Cuando descargan el WC del departamento superior escucho claramente el agua y también siento que el muro suena.”")
        _asset("curso2_lab1_etapa3_shaft_sanitario.webp")
        _mcq(
            "c1","C1 · ¿Qué mecanismos son físicamente posibles?",
            ["A. Radiación sonora directa de la tubería.","B. Transmisión por abrazaderas.","C. Contacto rígido en paso de losa.","D. Radiación del cerramiento del shaft.","E. Todos los anteriores."],
            4,"Una descarga sanitaria es normalmente un problema mixto: flujo, vibración de tuberías, conexiones estructurales y radiación del cerramiento pueden participar simultáneamente."
        )
        st.markdown("#### C2 · Sigue dos caminos")
        c_air = st.toggle("Activar camino aéreo", key=f"{ns}_c_air")
        c_struct = st.toggle("Activar camino estructural", key=f"{ns}_c_struct")
        ca,cs = st.columns(2)
        with ca:
            with st.container(border=True):
                st.markdown("**CAMINO AÉREO**")
                if c_air:
                    st.write("TUBERÍA → AIRE DEL SHAFT → CERRAMIENTO → DORMITORIO")
                else:
                    st.caption("Actívalo para seguir la ruta.")
        with cs:
            with st.container(border=True):
                st.markdown("**CAMINO ESTRUCTURAL**")
                if c_struct:
                    st.write("TUBERÍA → ABRAZADERA → MURO/LOSA → RADIACIÓN → DORMITORIO")
                else:
                    st.caption("Actívalo para seguir la ruta.")
        st.markdown("#### C3 · Encuentra puntos críticos")
        crit = ["Codo","Abrazadera","Penetración de losa","Contacto con tabique","Cierre del shaft"]
        crit_sel = st.multiselect("Selecciona puntos para inspeccionar:", crit, key=f"{ns}_c3")
        crit_text = {
            "Codo":"Los cambios de dirección del flujo pueden incrementar fuerzas dinámicas sobre la tubería.",
            "Abrazadera":"Una fijación rígida puede transferir vibración de la tubería hacia el elemento constructivo.",
            "Penetración de losa":"Una conexión rígida en el paso puede crear un camino adicional de transmisión.",
            "Contacto con tabique":"Un contacto no previsto puede puentear desacoples y excitar el cerramiento.",
            "Cierre del shaft":"El cerramiento puede recibir energía y radiarla hacia el dormitorio.",
        }
        for p in crit_sel:
            _card(p,crit_text[p],"📍")

    st.markdown("---")
    st.markdown("### 3 · Antes de controlar, diagnostica")
    bad,good = st.columns(2)
    with bad:
        with st.container(border=True):
            st.markdown("#### ❌ Procedimiento incorrecto")
            st.write("“Hay ruido.”")
            st.write("↓")
            st.write("“Instalemos material acústico.”")
    with good:
        with st.container(border=True):
            st.markdown("#### ✅ Procedimiento técnico")
            st.write("Hay ruido → identificar fuente → identificar excitación → identificar caminos → obtener evidencia → priorizar camino dominante → seleccionar control.")
    st.latex(r"\boxed{\mathrm{DIAGNÓSTICO}\rightarrow\mathrm{CONTROL}}")
    st.latex(r"\boxed{\mathrm{MOLESTIA}\not\rightarrow\mathrm{PRODUCTO}}")

    st.markdown("## 🧪 CONSTRUYE TU DIAGNÓSTICO")
    scenarios = {
        "Pasos del piso superior": {
            "fuentes":["Pisada","Bomba","Descarga sanitaria"],
            "fuente":"Pisada",
            "exc":["Mecánica","Aérea","Hidráulica","Mixta"], "exc_ok":"Mecánica",
            "caminos":["Losa / estructura","Base o tubería","Aéreo + estructural"], "camino":"Losa / estructura",
            "verifs":["Respuesta vibratoria del piso y/o superficies receptoras","Bomba → base/tubería → estructura → receptor","Tubería, abrazaderas, shaft y muro receptor"],
            "verif":"Respuesta vibratoria del piso y/o superficies receptoras",
            "controls":["Intervención en contacto/piso/desacople","Aislamiento/desacople de camino","Desacople y tratamiento del sistema"],
            "control":"Intervención en contacto/piso/desacople",
        },
        "Zumbido coincidente con bomba": {
            "fuentes":["Pisada","Bomba","Descarga sanitaria"], "fuente":"Bomba",
            "exc":["Mecánica","Aérea","Hidráulica","Mecánica + posible aérea"], "exc_ok":"Mecánica + posible aérea",
            "caminos":["Losa / estructura","Base o tubería","Aéreo + estructural"], "camino":"Base o tubería",
            "verifs":["Respuesta vibratoria del piso y/o superficies receptoras","Bomba → base/tubería → estructura → receptor","Tubería, abrazaderas, shaft y muro receptor"],
            "verif":"Bomba → base/tubería → estructura → receptor",
            "controls":["Intervención en contacto/piso/desacople","Aislamiento/desacople de camino","Desacople y tratamiento del sistema"],
            "control":"Aislamiento/desacople de camino",
        },
        "Descarga sanitaria": {
            "fuentes":["Pisada","Bomba","Flujo/tubería"], "fuente":"Flujo/tubería",
            "exc":["Mecánica","Aérea","Hidráulica","Hidráulica/mecánica"], "exc_ok":"Hidráulica/mecánica",
            "caminos":["Losa / estructura","Base o tubería","Aéreo + estructural"], "camino":"Aéreo + estructural",
            "verifs":["Respuesta vibratoria del piso y/o superficies receptoras","Bomba → base/tubería → estructura → receptor","Tubería, abrazaderas, shaft y muro receptor"],
            "verif":"Tubería, abrazaderas, shaft y muro receptor",
            "controls":["Intervención en contacto/piso/desacople","Aislamiento/desacople de camino","Desacople y tratamiento del sistema"],
            "control":"Desacople y tratamiento del sistema",
        },
    }
    scenario = st.selectbox("Caso de diagnóstico", list(scenarios), key=f"{ns}_labcase")
    sc = scenarios[scenario]
    src_ans = st.selectbox("FUENTE", ["— Selecciona —"]+sc["fuentes"], key=f"{ns}_lab_src")
    exc_ans = st.selectbox("EXCITACIÓN", ["— Selecciona —"]+sc["exc"], key=f"{ns}_lab_exc")
    path_ans = st.selectbox("CAMINO PRINCIPAL HIPOTÉTICO", ["— Selecciona —"]+sc["caminos"], key=f"{ns}_lab_path")
    verify_ans = st.selectbox("PUNTO / SECUENCIA DE VERIFICACIÓN", ["— Selecciona —"]+sc["verifs"], key=f"{ns}_lab_verify")
    diagnostic_complete = all(x!="— Selecciona —" for x in [src_ans,exc_ans,path_ans,verify_ans])
    if not diagnostic_complete:
        st.info("Completa fuente, excitación, camino y verificación antes de seleccionar una familia de control.")
        control_ans = None
    else:
        control_ans = st.selectbox("CONTROL PRELIMINAR", ["— Selecciona —"]+sc["controls"], key=f"{ns}_lab_control")
        if st.button("Comprobar diagnóstico", key=f"{ns}_lab_check"):
            ok = (
                src_ans==sc["fuente"] and exc_ans==sc["exc_ok"] and path_ans==sc["camino"]
                and verify_ans==sc["verif"] and control_ans==sc["control"]
            )
            if ok:
                st.success("Hipótesis coherente. El control es preliminar y queda condicionado a la verificación experimental del camino.")
            else:
                st.warning("Revisa la secuencia física. No selecciones el control por la molestia: primero conecta fuente, excitación, camino y evidencia.")

    st.markdown("### 4 · Preguntas de comprensión")
    st.caption("Formativas y no calificadas.")
    _mcq("q1","1. Una componente de 25 Hz aparece tanto en la bomba como en el dormitorio receptor. ¿Esto demuestra por sí solo que la bomba es la causa?",["A. Sí.","B. No."],1,"La coincidencia frecuencial es evidencia compatible, no prueba causal por sí sola.")
    _mcq("q2","2. ¿Medir únicamente el nivel de presión sonora en el recinto receptor permite identificar siempre el camino dominante?",["A. Sí.","B. No."],1,"El nivel en el receptor cuantifica el resultado, pero normalmente se necesitan observaciones intermedias para investigar el camino.")
    _mcq("q3","3. Una descarga sanitaria puede presentar simultáneamente caminos aéreos y estructurales.",["A. Verdadero.","B. Falso."],0,"El flujo puede excitar aire, tubería, fijaciones, estructura y cerramientos.")
    _mcq("q4","4. Una superficie que vibra intensamente es necesariamente el camino dominante.",["A. Verdadero.","B. Falso."],1,"La vibración debe relacionarse con la fuente, la propagación y la capacidad de radiación del elemento.")

    st.markdown("### Cierre")
    st.latex(r"\boxed{\mathrm{RECLAMO}\rightarrow\mathrm{HIPÓTESIS}\rightarrow\mathrm{EVIDENCIA}\rightarrow\mathrm{DIAGNÓSTICO}}")
    st.latex(r"\boxed{\mathrm{DIAGNÓSTICO}\rightarrow\mathrm{CONTROL}}")
    st.write("Un problema acústico no se resuelve identificando únicamente dónde se escucha el ruido. Es necesario reconstruir el camino que siguió la energía desde la fuente hasta el receptor.")
    st.success("En la siguiente etapa estudiaremos con mayor profundidad qué ocurre cuando la excitación es un impacto sobre un piso y por qué distintos sistemas constructivos producen respuestas tan diferentes.")

    left,right = st.columns(2)
    with left:
        if st.button("← Etapa 2", key=f"s3_prev_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 2
            st.rerun()
    with right:
        if st.button("Etapa 4 →", key=f"s3_next_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 4
            st.rerun()


def _render_course2_lab1_stage4(lab, saved):
    """Curso 2 · Lab 1 · Etapa 4: física del ruido de impacto."""
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
            st.image(path, width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode", False):
            st.caption(f"[Render pendiente: {name}]")
        return False

    def _card(title, body, icon="💡"):
        st.markdown(
            f"""<div style="border:1px solid #cfd8e3;border-radius:12px;padding:16px 18px;
            margin:10px 0 16px;background:#f8fbff">
            <div style="font-weight:800;margin-bottom:7px">{icon} {title}</div>
            <div style="line-height:1.55">{body}</div></div>""",
            unsafe_allow_html=True,
        )

    def _mcq(key, question, options, correct, feedback, store=False):
        st.markdown(f"#### {question}")

        # Docente: pauta visible, sin responder ni generar avance personal.
        if role == "Docente" and not projection_mode:
            with st.container(border=True):
                for i, option in enumerate(options):
                    prefix = "✅" if i == correct else "○"
                    st.write(f"{prefix} {option}")
                st.caption("Explicación: " + feedback)
            return

        state_key = f"{ns}_{key}"
        selected = st.radio(
            question,
            options,
            index=None,
            key=state_key,
            label_visibility="collapsed",
        )

        button_label = "Comprobar"
        if store and role == "Alumno" and not projection_mode:
            button_label = "Comprobar y guardar"

        if st.button(button_label, key=f"{state_key}_check"):
            if selected is None:
                st.warning("Selecciona una alternativa.")
            else:
                selected_idx = options.index(selected)
                ok = selected_idx == correct
                st.session_state[f"{state_key}_result"] = ok

                if store and role == "Alumno" and not projection_mode:
                    answers = saved.get("stage4_comprehension", {})
                    if not isinstance(answers, dict):
                        answers = {}
                    answers[key] = {
                        "selected": selected_idx,
                        "correct": ok,
                        "updated_at": _now(),
                    }
                    saved["stage4_comprehension"] = answers
                    saved["updated_4"] = _now()
                    _save_future_state_impl(class_id, saved)

        result = st.session_state.get(f"{state_key}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.warning("Revisa el concepto. " + feedback)

    header(
        "ETAPA 4 · LABORATORIO 1",
        "Física del ruido de impacto",
        "De la fuerza de contacto a la respuesta del piso.",
        show_overview=False,
        duration_minutes=60,
    )

    st.markdown("### Objetivo de aprendizaje")
    st.write(
        "Comprender el impacto como una fuerza variable en el tiempo, relacionar duración de contacto y contenido frecuencial, "
        "interpretar la interacción fuente–piso y seguir la cadena física desde F(f) hasta la radiación."
    )
    st.latex(
        r"\boxed{\mathrm{IMPACTO}\rightarrow F(t)\rightarrow F(f)\rightarrow "
        r"\mathrm{RESPUESTA\ DEL\ PISO}\rightarrow v(f)\rightarrow \mathrm{RADIACIÓN}}"
    )

    # ------------------------------------------------------------------
    # 1 · APERTURA
    # ------------------------------------------------------------------
    st.markdown("### 1 · Mismo peso, impacto diferente")
    _asset("curso2_lab1_etapa4_impacto_duro_resiliente.webp")

    _mcq(
        "opening",
        "¿Por qué el segundo impacto puede generar menos ruido si la persona y su peso son exactamente los mismos?",
        [
            "A. Porque disminuye la masa de la persona.",
            "B. Porque cambia la interacción mecánica durante el contacto.",
            "C. Porque la capa resiliente absorbe directamente todo el sonido aéreo.",
            "D. Porque la gravedad cambia.",
        ],
        1,
        "La capa resiliente modifica la forma temporal de la fuerza de impacto. "
        "Al cambiar la duración y rigidez del contacto también cambia su contenido espectral.",
    )

    # ------------------------------------------------------------------
    # 2 · IMPACTO COMO FUERZA VARIABLE
    # ------------------------------------------------------------------
    st.markdown("### 2 · El impacto como fuerza variable")
    st.latex(r"F=F(t)")
    st.write(
        "Durante un impacto, la fuerza no es constante. Aumenta rápidamente, alcanza un máximo "
        "y posteriormente disminuye."
    )
    st.latex(r"\boxed{J=\int F(t)\,dt}")
    st.write("**J:** impulso mecánico · **F(t):** fuerza · **dt:** intervalo temporal.")
    st.info("En esta etapa interesa reconocer tres atributos del impacto: **magnitud, duración y forma temporal**.")

    _card(
        "EN PALABRAS SIMPLES",
        "Un golpe no se caracteriza solamente por “qué tan fuerte fue”. También importa cuánto duró el contacto. "
        "Una cuchara metálica y una pelota de goma pueden entregar impactos de energía comparable, pero la interacción temporal es distinta.",
    )

    st.markdown("#### Impacto duro vs. impacto resiliente")
    hard, soft = st.columns(2)
    with hard:
        with st.container(border=True):
            st.markdown("**IMPACTO DURO**")
            st.write("• contacto corto  \n• pendiente rápida  \n• pico elevado  \n• espectro más extendido hacia altas frecuencias")
            st.latex(r"\Delta t\downarrow\Rightarrow\text{mayor extensión espectral}")
    with soft:
        with st.container(border=True):
            st.markdown("**IMPACTO RESILIENTE**")
            st.write("• contacto más prolongado  \n• fuerza distribuida en mayor tiempo  \n• menor contenido relativo de altas frecuencias")
            st.latex(r"\Delta t\uparrow\Rightarrow\text{menor contenido relativo de alta frecuencia}")
    st.caption("Esto no significa que las componentes de baja frecuencia desaparezcan.")

    # ------------------------------------------------------------------
    # Interactivo 4.1
    # ------------------------------------------------------------------
    st.markdown("### 🔬 3 · Del tiempo al espectro")
    st.caption("Simulación conceptual/didáctica. No representa una máquina de impactos normalizada.")

    dt_ms = st.slider(
        "Duración de contacto Δt (ms)",
        min_value=0.5,
        max_value=30.0,
        value=5.0,
        step=0.5,
        key=f"{ns}_dt",
    )

    # Pulso gaussiano de impulso constante, utilizado solo como demostración.
    dt = dt_ms / 1000.0
    t = np.linspace(-0.06, 0.06, 1600)
    sigma_t = max(dt / 2.355, 1e-5)
    force = np.exp(-0.5 * (t / sigma_t) ** 2)
    impulse_area = np.sum(0.5 * (force[:-1] + force[1:]) * np.diff(t))
    force = force / max(float(impulse_area), 1e-12)  # impulso normalizado

    fig, ax = plt.subplots()
    ax.plot(t * 1000, force / force.max())
    ax.set_xlabel("Tiempo (ms)")
    ax.set_ylabel("F(t) normalizada")
    ax.set_title("Forma temporal del impacto")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    freqs = np.fft.rfftfreq(len(t), d=(t[1] - t[0]))
    spectrum = np.abs(np.fft.rfft(force))
    spectrum = spectrum / max(spectrum.max(), 1e-12)
    valid = freqs <= 2000

    fig, ax = plt.subplots()
    ax.plot(freqs[valid], spectrum[valid])
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("|F(f)| normalizada")
    ax.set_title("Contenido frecuencial conceptual")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    _mcq(
        "duration_q",
        "Al aumentar la duración del contacto, ¿qué ocurre principalmente con el contenido de alta frecuencia del impacto?",
        [
            "A. Aumenta necesariamente.",
            "B. Tiende a disminuir.",
            "C. Permanece idéntico.",
            "D. Desaparece toda la fuerza.",
        ],
        1,
        "Un contacto más prolongado distribuye la fuerza en mayor tiempo y tiende a reducir el contenido relativo de alta frecuencia.",
    )

    # ------------------------------------------------------------------
    # 4 · EL PISO PARTICIPA
    # ------------------------------------------------------------------
    st.markdown("### 4 · El piso también participa en el impacto")
    st.latex(r"\boxed{F_{\mathrm{impacto}}\neq\text{propiedad exclusiva del martillo}}")
    st.write(
        "La fuerza de contacto depende de la interacción entre el elemento impactante y la respuesta mecánica local del piso."
    )
    st.latex(r"Y(f)=\frac{v(f)}{F(f)}")
    st.write("Un piso con distinta movilidad modifica la interacción durante el impacto.")

    massive, light = st.columns(2)
    with massive:
        with st.container(border=True):
            st.markdown("#### Piso masivo")
            st.write(
                "**Ejemplo:** losa de hormigón.  \n"
                "• alta masa  \n"
                "• alta impedancia de punto en muchos rangos  \n"
                "• deformación local pequeña  \n"
                "• interacción relativamente dura"
            )
    with light:
        with st.container(border=True):
            st.markdown("#### Piso liviano")
            st.write(
                "**Ejemplo:** entramado de madera.  \n"
                "• mayor movilidad local  \n"
                "• respuesta local más relevante  \n"
                "• posición del impacto importante  \n"
                "• interacción martillo–estructura más acoplada"
            )
    st.caption("“Liviano” no significa automáticamente “peor” en todo el rango de frecuencias.")
    _asset("curso2_lab1_etapa4_mismo_martillo_dos_pisos.webp")

    # ------------------------------------------------------------------
    # Interactivo 4.2
    # ------------------------------------------------------------------
    st.markdown("### 🔬 5 · Mismo martillo, otro piso")
    floor_type = st.segmented_control(
        "Selecciona el piso",
        ["LOSA MASIVA", "PISO LIVIANO"],
        default="LOSA MASIVA",
        key=f"{ns}_floor_type",
    )

    f = np.linspace(20, 800, 700)
    if floor_type == "LOSA MASIVA":
        mobility = 0.18 + 0.18 * np.exp(-0.5 * ((f - 180) / 60) ** 2) + 0.12 * np.exp(-0.5 * ((f - 520) / 100) ** 2)
        contact = np.exp(-f / 680)
        label = "Movilidad conceptual relativamente menor"
    else:
        mobility = 0.32 + 0.55 * np.exp(-0.5 * ((f - 110) / 45) ** 2) + 0.38 * np.exp(-0.5 * ((f - 360) / 70) ** 2)
        contact = np.exp(-f / 520)
        label = "Movilidad conceptual mayor y con resonancias más marcadas"

    velocity = mobility * contact

    fig, ax = plt.subplots()
    ax.plot(f, mobility)
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("Y(f) relativa")
    ax.set_title("Movilidad conceptual del piso")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(f, contact)
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("|F(f)| relativa")
    ax.set_title("Fuerza de contacto conceptual")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(f, velocity)
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("v(f) relativa")
    ax.set_title("Respuesta resultante · v(f)=Y(f)F(f)")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.info(label)
    st.latex(r"\boxed{v(f)=Y(f)F(f)}")
    st.caption("Modelo conceptual simplificado; no corresponde a un cálculo FEM.")

    _mcq(
        "same_hammer",
        "Si la misma máquina de impactos se coloca sobre dos pisos diferentes, ¿podemos asumir que la fuerza efectiva transmitida es exactamente idéntica?",
        ["A. Sí.", "B. No."],
        1,
        "La interacción entre martillo y piso depende de la respuesta mecánica local del sistema.",
    )

    # ------------------------------------------------------------------
    # 6 · POSICIÓN DEL IMPACTO
    # ------------------------------------------------------------------
    st.markdown("### 6 · La posición del impacto también importa")
    st.write(
        "En pisos livianos o modulares, la movilidad local puede cambiar considerablemente con la posición."
    )
    st.latex(r"Y=Y(f,x,y)")
    _asset("curso2_lab1_etapa4_posiciones_impacto.webp")

    position = st.segmented_control(
        "¿Dónde golpeas?",
        ["S1 · Sobre nervio", "S2 · Entre nervios", "S3 · Próximo al borde"],
        default="S1 · Sobre nervio",
        key=f"{ns}_position",
    )

    pos_cfg = {
        "S1 · Sobre nervio": ("BAJA", 0.70, 210),
        "S2 · Entre nervios": ("ALTA", 1.30, 145),
        "S3 · Próximo al borde": ("MEDIA", 0.95, 175),
    }
    level, amp, fp = pos_cfg[position]
    fpos = np.linspace(20, 500, 500)
    ypos = 0.12 + amp / (1 + ((fpos - fp) / 40) ** 2)

    st.metric("Movilidad local relativa", level)
    fig, ax = plt.subplots()
    ax.plot(fpos, ypos)
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("Y(f) relativa")
    ax.set_title(f"Respuesta conceptual · {position}")
    ax.grid(True, alpha=.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.success("POSICIÓN DE IMPACTO → RESPUESTA DIFERENTE")

    # ------------------------------------------------------------------
    # 7 · CADENA PREDICTIVA
    # ------------------------------------------------------------------
    st.markdown("### 7 · Cadena predictiva del ruido de impacto")
    st.latex(
        r"\boxed{F(f)\rightarrow Y(f)\rightarrow v(f)\rightarrow "
        r"W_{\mathrm{rad}}(f)\rightarrow L_n(f)}"
    )
    st.write(
        "Esta es la arquitectura física de un modelo de predicción del nivel de ruido de impacto. "
        "Todavía no utilizaremos una fórmula cerrada para Lₙ(f)."
    )

    st.markdown("#### Radiación")
    st.latex(r"W_{\mathrm{rad}}=\rho_0c_0S\sigma\left\langle v_n^2\right\rangle")
    st.write(
        "Una vez conocida la respuesta vibratoria, todavía debemos conocer cuánto de esa vibración "
        "se convierte en potencia sonora."
    )
    st.latex(r"\boxed{\mathrm{VIBRACIÓN}\neq\mathrm{RUIDO\ FINAL}}")

    # ------------------------------------------------------------------
    # Interactivo 4.4
    # ------------------------------------------------------------------
    st.markdown("### 🔬 8 · Construye el modelo")
    model_steps = [
        ("IMPACTO", r"F(t)", "El contacto genera una fuerza variable en el tiempo."),
        ("ESPECTRO DE FUERZA", r"F(f)", "La forma temporal del impacto determina su contenido frecuencial."),
        ("RESPUESTA DEL PISO", r"Y(f)", "La movilidad describe la sensibilidad dinámica local del piso."),
        ("VELOCIDAD", r"v(f)=Y(f)F(f)", "La fuerza y la movilidad determinan la respuesta vibratoria."),
        ("RADIACIÓN", r"\sigma,\ W_{\mathrm{rad}}", "La superficie vibrante convierte parte de la energía en sonido."),
        ("RESULTADO", r"L_n(f)", "El resultado acústico es el final de toda la cadena física."),
    ]
    build_key = f"{ns}_build_step"
    if build_key not in st.session_state:
        st.session_state[build_key] = 0

    current = st.session_state[build_key]
    with st.container(border=True):
        st.markdown(f"#### {model_steps[current][0]}")
        st.latex(model_steps[current][1])
        st.write(model_steps[current][2])

    b1, b2 = st.columns(2)
    with b1:
        if st.button(
            "Reiniciar",
            key=f"{ns}_build_reset",
            use_container_width=True,
            disabled=current == 0,
        ):
            st.session_state[build_key] = 0
            st.rerun()
    with b2:
        if st.button(
            "Continuar →",
            key=f"{ns}_build_next",
            use_container_width=True,
            type="primary",
            disabled=current >= len(model_steps) - 1,
        ):
            st.session_state[build_key] += 1
            st.rerun()

    # ------------------------------------------------------------------
    # 9 · ABSOLUTO VS MEJORA
    # ------------------------------------------------------------------
    st.markdown("### 9 · Nivel absoluto y mejora son problemas distintos")
    qa, qb = st.columns(2)
    with qa:
        with st.container(border=True):
            st.markdown("#### Pregunta A")
            st.write("¿Cuánto ruido produce este piso?")
            st.latex(r"L_n(f)")
    with qb:
        with st.container(border=True):
            st.markdown("#### Pregunta B")
            st.write("¿Cuánto mejora si agregamos un tratamiento?")
            st.latex(r"\Delta L(f)")
    st.latex(r"\boxed{\Delta L(f)=L_{n,0}(f)-L_n(f)}")
    st.latex(r"\boxed{L_n(f)=L_{n,0}(f)-\Delta L(f)}")

    _card(
        "DOS PROBLEMAS DIFERENTES",
        "Predecir el nivel absoluto de un piso requiere modelar fuente, estructura y radiación. "
        "Predecir la mejora de un tratamiento puede ser más sencillo porque se compara el sistema tratado "
        "con una condición de referencia.",
    )
    _asset("curso2_lab1_etapa4_base_tratado.webp")

    st.markdown("### 🔬 10 · Nivel o mejora")
    _mcq(
        "level_or_improvement_1",
        "Caso 1 · “Necesito saber cuánto ruido producirá esta losa desnuda.”",
        ["A. Lₙ(f)", "B. ΔL(f)"],
        0,
        "La pregunta busca un nivel absoluto del sistema.",
    )
    _mcq(
        "level_or_improvement_2",
        "Caso 2 · “Quiero saber cuánto mejora una solución respecto del piso base.”",
        ["A. Lₙ(f)", "B. ΔL(f)"],
        1,
        "La pregunta compara una condición tratada con una condición de referencia.",
    )

    # ------------------------------------------------------------------
    # 11 · LIMITACIONES DE MODELOS
    # ------------------------------------------------------------------
    st.markdown("### 11 · Limitaciones de los modelos")
    st.latex(r"\boxed{\mathrm{MODELO}\neq\mathrm{REALIDAD\ EXACTA}}")
    st.write(
        "Una predicción puede depender de propiedades reales de materiales, condiciones de borde, amortiguamiento, "
        "posición de impacto, geometría, uniones, flanqueo, incertidumbre de la fuerza y radiación acústica."
    )

    st.markdown("#### Jerarquía de modelos")
    ma, mb, mc = st.columns(3)
    with ma:
        with st.container(border=True):
            st.markdown("**Modelo conceptual**")
            st.latex(r"F\rightarrow Y\rightarrow v")
    with mb:
        with st.container(border=True):
            st.markdown("**Modelo analítico**")
            st.write("Ecuaciones de placas / modelos específicos.")
    with mc:
        with st.container(border=True):
            st.markdown("**Modelo numérico**")
            st.write("FEM vibroacústico.")
    st.latex(r"\boxed{\mathrm{EXCITACIÓN}\rightarrow\mathrm{ESTRUCTURA}\rightarrow\mathrm{ACÚSTICA}}")

    _card(
        "¿PARA QUÉ SIRVE UN MODELO?",
        "No para “adivinar exactamente” un resultado. Sirve para comparar alternativas, comprender tendencias, "
        "identificar variables dominantes, dimensionar soluciones, anticipar riesgos y apoyar decisiones de diseño.",
        "🎓",
    )

    # ------------------------------------------------------------------
    # 12 · EJERCICIO
    # ------------------------------------------------------------------
    st.markdown("### 12 · Ejercicio de la etapa")
    st.latex(
        r"F=120\ \mathrm{N},\qquad "
        r"Y_A=2.5\times10^{-6}\frac{\mathrm{m/s}}{\mathrm{N}},\qquad "
        r"Y_B=10\times10^{-6}\frac{\mathrm{m/s}}{\mathrm{N}}"
    )

    e1, e2 = st.columns(2)
    with e1:
        va = st.number_input(
            "a) v_A (m/s)",
            min_value=0.0,
            value=0.0,
            format="%.6f",
            key=f"{ns}_va",
        )
        ratio = st.number_input(
            "c) v_B / v_A",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            key=f"{ns}_ratio",
        )
    with e2:
        vb = st.number_input(
            "b) v_B (m/s)",
            min_value=0.0,
            value=0.0,
            format="%.6f",
            key=f"{ns}_vb",
        )
        dlv = st.number_input(
            "Diferencia de nivel vibratorio (dB)",
            value=0.0,
            format="%.1f",
            key=f"{ns}_dlv",
        )

    if st.button("Comprobar ejercicio", key=f"{ns}_exercise_check"):
        ok = (
            abs(va - 3.0e-4) <= 3e-6
            and abs(vb - 1.2e-3) <= 3e-6
            and abs(ratio - 4.0) <= 0.05
            and abs(dlv - 12.04) <= 0.2
        )
        if ok:
            st.success(
                "Correcto: v_A=3,0×10⁻⁴ m/s; v_B=1,2×10⁻³ m/s; "
                "v_B/v_A=4 y 20log₁₀(4)≈12 dB."
            )
        else:
            st.warning("Revisa v=YF y luego 20log₁₀(v_B/v_A).")

    _mcq(
        "exercise_interpretation",
        "¿Podemos concluir que el Piso B producirá exactamente 12 dB más de Lₙ?",
        ["A. Sí.", "B. No."],
        1,
        "Todavía debemos considerar propagación, distribución vibratoria y eficiencia de radiación.",
    )

    # ------------------------------------------------------------------
    # 13 · COMPRENSIÓN
    # ------------------------------------------------------------------
    st.markdown("### 13 · Preguntas de comprensión")
    st.caption("Formativas y no calificadas.")

    _mcq(
        "q1",
        "1. Un impacto más corto tiende a presentar:",
        [
            "A. Menor contenido de alta frecuencia.",
            "B. Mayor extensión espectral hacia altas frecuencias.",
            "C. Exactamente el mismo espectro.",
            "D. Solamente componentes bajas.",
        ],
        1,
        "Un contacto más breve concentra la fuerza en el tiempo y extiende relativamente su contenido hacia frecuencias más altas.",
        store=True,
    )
    _mcq(
        "q2",
        "2. La fuerza efectiva de una máquina de impactos depende solamente de la masa del martillo.",
        ["A. Verdadero.", "B. Falso."],
        1,
        "También interviene la interacción dinámica entre el martillo y el piso.",
        store=True,
    )
    _mcq(
        "q3",
        "3. En un piso liviano, cambiar la posición de impacto puede modificar la respuesta.",
        ["A. Verdadero.", "B. Falso."],
        0,
        "La movilidad local puede variar con la posición sobre nervios, entre nervios o cerca de bordes.",
        store=True,
    )
    _mcq(
        "q4",
        "4. Predecir Lₙ(f) y predecir ΔL(f) son exactamente el mismo problema.",
        ["A. Verdadero.", "B. Falso."],
        1,
        "El primero busca un nivel absoluto; el segundo compara una solución con una condición de referencia.",
        store=True,
    )

    # ------------------------------------------------------------------
    # CIERRE
    # ------------------------------------------------------------------
    st.markdown("### Cierre")
    st.latex(
        r"\boxed{F(t)\rightarrow F(f)\rightarrow Y(f)\rightarrow v(f)\rightarrow "
        r"W_{\mathrm{rad}}(f)\rightarrow L_n(f)}"
    )
    st.write(
        "El ruido de impacto no depende únicamente del golpe. Es el resultado de la interacción entre la fuente, "
        "la respuesta dinámica del piso y la eficiencia con que la estructura vibrante radia sonido."
    )
    st.success(
        "En la siguiente etapa aplicaremos estos principios para analizar distintas soluciones constructivas de piso "
        "y entender por qué algunas reducen el impacto y otras pueden fracasar en obra."
    )

    left, right = st.columns(2)
    with left:
        if st.button("← Etapa 3", key=f"s4_prev_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 3
            st.rerun()
    with right:
        if st.button("Etapa 5 →", key=f"s4_next_{class_id}", use_container_width=True):
            st.session_state[stage_selector_key] = 5
            st.rerun()

def _render_course2_lab1_stage5(lab, saved):
    """ETAPA 5 — Predicción de L_n,0(f) de la losa base mediante el modelo de Vér."""
    import numpy as np
    import matplotlib.pyplot as plt
    from core.acoustics import critical_frequency
    from core.course2_impact_models import (
        ver_impact_velocity_before_contact,
        ver_impact_force_harmonic,
        ver_force_spectral_density,
        ver_lw_oct_db,
        ver_ln_supercritical_db,
        ver_ln_subcritical_db,
        ver_ln_piecewise_db,
    )

    class_id=lab["id"]
    stage_selector_key=f"future_stage_{class_id}"
    role=st.session_state.get("role","Alumno")
    projection_mode=bool(st.session_state.get("projection_mode") or role=="Proyección")
    ns=f"{class_id}_s5"
    stage_no=5

    def _asset(name, caption=None):
        p=ASSET_DIR/name
        if p.exists():
            st.image(p,width="stretch")
            if caption:
                st.caption(caption)
            return True
        if st.session_state.get("dev_mode",False):
            st.caption(f"[Render pendiente: {name}]")
        return False

    def _mcq(key, question, options, correct, feedback, store=False):
        st.markdown(f"#### {question}")
        if role=="Docente" and not projection_mode:
            with st.container(border=True):
                for i,opt in enumerate(options):
                    st.write(("✅ " if i==correct else "○ ")+opt)
                st.caption(feedback)
            return
        sk=f"{ns}_{key}"
        choice=st.radio(question,options,index=None,key=sk,label_visibility="collapsed")
        label="Comprobar y guardar" if store and role=="Alumno" and not projection_mode else "Comprobar"
        if st.button(label,key=f"{sk}_check"):
            if choice is None:
                st.warning("Selecciona una alternativa.")
            else:
                idx=options.index(choice)
                ok=idx==correct
                st.session_state[f"{sk}_result"]=ok
                if store and role=="Alumno" and not projection_mode:
                    data=saved.get(f"stage{stage_no}_comprehension",{})
                    if not isinstance(data,dict):
                        data={}
                    data[key]={"selected":idx,"correct":ok,"updated_at":_now()}
                    saved[f"stage{stage_no}_comprehension"]=data
                    saved[f"updated_{stage_no}"]=_now()
                    _save_future_state_impl(class_id,saved)
        result=st.session_state.get(f"{sk}_result")
        if result is True:
            st.success("Correcto. "+feedback)
        elif result is False:
            st.warning("Revisa el concepto. "+feedback)

    header(
        "ETAPA 5 · LABORATORIO 1",
        "Predicción del nivel de ruido de impacto de la losa base",
        "Modelo analítico de Vér: de la excitación mecánica a Lₙ(f).",
        show_overview=False,
        duration_minutes=80,
    )

    # 1. Bridge
    st.markdown("## De la excitación mecánica al nivel de ruido de impacto")
    st.write(
        "Hasta ahora hemos estudiado por separado la excitación, la respuesta vibratoria "
        "de la losa y su capacidad para radiar sonido. El objetivo ahora es conectar estas "
        "variables para predecir el ruido generado en el recinto receptor."
    )
    st.latex(
        r"\boxed{\mathrm{IMPACTO}\rightarrow F(f)\rightarrow"
        r"\mathrm{VIBRACIÓN\ DE\ LA\ LOSA}\rightarrow\sigma_{\mathrm{rad}}(f)"
        r"\rightarrow W_{\mathrm{rad}}(f)\rightarrow L_n(f)}"
    )
    st.info(
        "El modelo de Vér permite establecer este puente entre la excitación mecánica "
        "de la losa y el ruido de impacto radiado al recinto inferior."
    )

    # 2. Excitation
    st.markdown("## 1 · Excitación producida por la máquina de impactos")
    st.write(
        "Vér representa la excitación periódica mediante sus componentes espectrales. "
        "El objetivo aquí es reconocer que la fuente de impacto puede caracterizarse "
        "en frecuencia."
    )
    st.latex(r"\boxed{F_n=2f_rmv_0}")
    st.latex(r"\boxed{v_0=\sqrt{2gh}}")
    st.write(
        "**fᵣ**: frecuencia de repetición · **m**: masa del martillo · "
        "**v₀**: velocidad antes del impacto · **g**: gravedad · **h**: altura de caída."
    )
    st.latex(r"\boxed{S_{f0}=4f_rm^2gh}")
    st.write(
        "Para la máquina de impactos normalizada considerada por Vér, la densidad "
        "espectral de fuerza resulta aproximadamente:"
    )
    st.latex(r"\boxed{S_{f0}\approx4\ \mathrm{N^2/Hz}}")
    st.caption(
        "Fuente: Vér & Beranek (eds.), *Noise and Vibration Control Engineering*, "
        "2nd ed., cap. 11, §11.11 *Impact Noise*, Ecs. (11.158)–(11.160)."
    )

    with st.container(border=True):
        fr=st.number_input("fᵣ [Hz]",min_value=0.1,value=10.0,step=0.5,key=f"{ns}_fr")
        mass=st.number_input("m [kg]",min_value=0.01,value=0.5,step=0.05,key=f"{ns}_mass")
        hdrop=st.number_input("h [m]",min_value=0.001,value=0.04,step=0.005,format="%.3f",key=f"{ns}_hdrop")
        try:
            v0=ver_impact_velocity_before_contact(9.81,hdrop)
            fn=ver_impact_force_harmonic(fr,mass,v0)
            sf=ver_force_spectral_density(fr,mass,9.81,hdrop)
            c1,c2,c3=st.columns(3)
            c1.metric("v₀",f"{v0:.3f} m/s")
            c2.metric("Fₙ",f"{fn:.2f} N")
            c3.metric("S_f0",f"{sf:.2f} N²/Hz")
        except ValueError as exc:
            st.warning(str(exc))

    # 3. Radiation
    st.markdown("## 2 · De la vibración a la radiación acústica")
    st.write(
        "Una losa que vibra no necesariamente radia sonido con la misma eficiencia en "
        "todas las frecuencias. La conversión de vibración estructural en sonido depende "
        "de la eficiencia de radiación σ_rad."
    )
    st.latex(
        r"\boxed{L_{W,\mathrm{oct}}\approx10\log_{10}\left["
        r"\frac{\rho c\,\sigma_{\mathrm{rad}}}"
        r"{5.1\,\rho_p^2c_L\eta_p t^3}\right]+120}"
    )
    st.caption(
        "Fuente: Vér & Beranek (eds.), *Noise and Vibration Control Engineering*, "
        "2nd ed., cap. 11, §11.11 *Impact Noise*, Ec. (11.162)."
    )
    with st.container(border=True):
        st.markdown("**Variables**")
        st.write(
            "ρ: densidad del aire · c: velocidad del sonido · σ_rad: eficiencia de radiación · "
            "ρₚ: densidad de la losa · c_L: velocidad longitudinal del material · "
            "ηₚ: factor de pérdidas total · t: espesor de la losa."
        )
    st.info("🔎 **Observa el término t³.**")
    st.write(
        "Dentro de las hipótesis del modelo, duplicar el espesor de una losa homogénea "
        "produce aproximadamente una reducción de 9 dB en el nivel de potencia sonora radiada."
    )
    st.latex(r"\boxed{t\rightarrow2t\quad\Rightarrow\quad\Delta L_W\approx-9\ \mathrm{dB}}")
    st.write("Un aumento del amortiguamiento ηₚ también reduce la respuesta radiada.")

    # 4. Critical frequency from actual plate properties
    st.markdown("## 3 · La frecuencia crítica cambia el comportamiento")
    st.write(
        "La frecuencia crítica no se selecciona arbitrariamente. Se calcula a partir de "
        "las propiedades de la placa."
    )
    c1,c2=st.columns(2)
    with c1:
        rho_p=st.number_input("Densidad de la losa ρₚ [kg/m³]",min_value=500.0,max_value=4000.0,
                              value=2400.0,step=50.0,key=f"{ns}_rho_p")
        t_mm=st.number_input("Espesor t [mm]",min_value=20.0,max_value=500.0,
                            value=160.0,step=5.0,key=f"{ns}_tmm")
    with c2:
        young=st.number_input("Módulo de Young E [GPa]",min_value=1.0,max_value=80.0,
                              value=30.0,step=1.0,key=f"{ns}_E")
        nu=st.number_input("Coeficiente de Poisson ν",min_value=0.05,max_value=0.49,
                           value=0.20,step=0.01,format="%.2f",key=f"{ns}_nu")

    try:
        surface_mass, stiffness, fc = critical_frequency(rho_p,t_mm,young,nu,343.0)
    except Exception as exc:
        surface_mass, stiffness, fc = None, None, None
        st.warning(f"No fue posible calcular f_c con estos datos: {exc}")

    if fc and fc>0:
        a,b,c=st.columns(3)
        a.metric("m′",f"{surface_mass:.1f} kg/m²")
        b.metric("D",f"{stiffness:.1f} N·m")
        c.metric("f_c",f"{fc:.0f} Hz")
        st.latex(
            r"\boxed{f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}},\qquad "
            r"D=\frac{Eh^3}{12(1-\nu^2)}}"
        )
        st.caption(
            "Frecuencia crítica y rigidez flexional: relación de placa simple reutilizada "
            "desde el Curso 1. La aplicación calcula f_c a partir de las propiedades de la losa."
        )
        # simple regime visualization
        fig,ax=plt.subplots(figsize=(8,1.8))
        ax.set_xscale("log")
        ax.set_xlim(80,5000)
        ax.axvspan(80,max(80,min(fc,5000)),alpha=.12)
        ax.axvspan(max(80,min(fc,5000)),5000,alpha=.06)
        ax.axvline(fc,linestyle="--")
        ax.text(120,0.55,"Régimen subcrítico",transform=ax.get_xaxis_transform())
        ax.text(max(fc*1.15,500),0.55,"Sobre frecuencia crítica",transform=ax.get_xaxis_transform())
        ax.set_yticks([])
        ax.set_xlabel("Frecuencia [Hz]")
        ax.grid(True,which="both",alpha=.15)
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)
        st.write(
            "La frecuencia crítica separa dos regímenes de radiación. Por ello, "
            "el modelo de predicción no utiliza exactamente la misma expresión a ambos lados de f_c."
        )

    # 5. Supercritical
    st.markdown("## 4 · Predicción para f > f_c")
    st.latex(
        r"\boxed{L_n+R=43+30\log_{10}(f)-10\log_{10}(\sigma_{\mathrm{rad}})-\Delta L_n}"
    )
    st.caption(
        "Fuente: Vér & Beranek (eds.), *Noise and Vibration Control Engineering*, "
        "2nd ed., cap. 11, §11.11 *Impact Noise*, Ec. (11.172)."
    )
    st.write("Para una losa estructural desnuda:")
    st.latex(r"\Delta L_n=0")
    st.latex(
        r"\boxed{L_n=43+30\log_{10}(f)-10\log_{10}(\sigma_{\mathrm{rad}})-R}"
    )
    st.write(
        "Sobre la frecuencia crítica, la eficiencia de radiación puede aproximarse a "
        "σ_rad≈1 bajo las hipótesis correspondientes:"
    )
    st.latex(r"\boxed{L_n\approx43+30\log_{10}(f)-R}")
    st.warning("Esta simplificación no se presenta como una ley universal.")

    # 6. Subcritical
    st.markdown("## 5 · Predicción para f < f_c")
    st.latex(
        r"\boxed{R+L_n=39.5+20\log_{10}(f)-\Delta L_n"
        r"-10\log_{10}\left(\frac{\eta_p}{f_c\sigma_{\mathrm{rad}}}\right)}"
    )
    st.caption(
        "Fuente: Vér & Beranek (eds.), *Noise and Vibration Control Engineering*, "
        "2nd ed., cap. 11, §11.11 *Impact Noise*, Ec. (11.173)."
    )
    st.write("Para la losa desnuda, ΔLₙ=0:")
    st.latex(
        r"\boxed{L_n=39.5+20\log_{10}(f)"
        r"-10\log_{10}\left(\frac{\eta_p}{f_c\sigma_{\mathrm{rad}}}\right)-R}"
    )
    st.write(
        "Bajo la frecuencia crítica aparecen explícitamente el amortiguamiento de la losa, "
        "la frecuencia crítica y la eficiencia de radiación. Por eso no basta con conocer "
        "únicamente la masa superficial."
    )

    # 7. Main interactive
    st.markdown("## 🔬 6 · Explora la predicción de ruido de impacto")
    bands=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150]
    fsel=st.select_slider("Frecuencia f [Hz]",options=bands,value=500,key=f"{ns}_fsel")
    Rsel=st.slider("R(f) [dB]",30.0,80.0,55.0,.5,key=f"{ns}_Rsel")
    sigma=st.slider("σ_rad(f)",0.05,1.50,1.00,.05,key=f"{ns}_sigma")
    eta=st.slider("ηₚ",0.001,0.100,0.020,0.001,format="%.3f",key=f"{ns}_eta")

    if not fc or fc<=0:
        st.warning("No hay una f_c válida; revisa las propiedades de la losa.")
    elif sigma<=0 or eta<=0:
        st.warning("σ_rad y ηₚ deben ser mayores que cero.")
    else:
        try:
            ln,regime=ver_ln_piecewise_db(fsel,Rsel,fc,sigma,eta,0.0)
            c1,c2,c3,c4=st.columns(4)
            c1.metric("f",f"{fsel} Hz")
            c2.metric("f_c",f"{fc:.0f} Hz")
            c3.metric("R(f)",f"{Rsel:.1f} dB")
            c4.metric("Lₙ(f)",f"{ln:.1f} dB")
            if regime=="subcrítico":
                st.warning("RÉGIMEN SUBCRÍTICO · se aplica automáticamente la expresión para f<f_c.")
            else:
                st.success("SOBRE FRECUENCIA CRÍTICA · se aplica automáticamente la expresión para f≥f_c.")
        except ValueError as exc:
            st.warning(str(exc))

    # 8. Full graph
    st.markdown("## 7 · Curva Lₙ(f) y cambio de régimen")
    if fc and fc>0 and sigma>0 and eta>0:
        # Didactic R(f) input for visual exploration only
        Rcurve=np.array([47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62],dtype=float)
        Lcurve=[]
        regimes=[]
        for ff,rr in zip(bands,Rcurve):
            try:
                val,rg=ver_ln_piecewise_db(ff,rr,fc,sigma,eta,0.0)
            except ValueError:
                val,rg=np.nan,""
            Lcurve.append(val); regimes.append(rg)
        fig,ax=plt.subplots()
        ax.semilogx(bands,Lcurve,marker="o",label="Lₙ(f)")
        ax.axvline(fc,linestyle="--",label="f_c")
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("Lₙ [dB]")
        ax.grid(True,which="both",alpha=.2)
        ax.legend()
        ymin,ymax=ax.get_ylim()
        ax.text(110,ymax-(ymax-ymin)*.12,"Régimen subcrítico")
        ax.text(max(fc*1.1,400),ymax-(ymax-ymin)*.12,"Sobre frecuencia crítica")
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)
        st.caption(
            "La curva R(f) de este gráfico es un dato de ejercicio didáctico para visualizar "
            "el cambio de régimen; no corresponde a un producto comercial."
        )

    # 9. Thickness activity
    st.markdown("## 8 · ¿Qué ocurre si duplicamos el espesor?")
    rho_air=st.number_input("ρ aire [kg/m³]",min_value=0.5,max_value=2.0,value=1.21,step=.01,key=f"{ns}_rhoair")
    c_air=st.number_input("c aire [m/s]",min_value=300.0,max_value=380.0,value=343.0,step=1.0,key=f"{ns}_cair")
    cL=st.number_input("c_L material [m/s]",min_value=500.0,max_value=8000.0,value=3500.0,step=100.0,key=f"{ns}_cL")
    try:
        lw1=ver_lw_oct_db(rho_air,c_air,max(sigma,1e-9),rho_p,cL,max(eta,1e-9),t_mm/1000.0)
        lw2=ver_lw_oct_db(rho_air,c_air,max(sigma,1e-9),rho_p,cL,max(eta,1e-9),2*t_mm/1000.0)
        c1,c2,c3=st.columns(3)
        c1.metric("Losa A · t",f"{lw1:.1f} dB")
        c2.metric("Losa B · 2t",f"{lw2:.1f} dB")
        c3.metric("ΔL_W",f"{lw2-lw1:.1f} dB")
        st.latex(r"\boxed{t\rightarrow2t\Rightarrow\Delta L_W\approx-9\ \mathrm{dB}}")
        st.write(
            "Una losa más gruesa presenta una respuesta radiada menor frente a la excitación "
            "de impacto, dentro de las hipótesis del modelo utilizado."
        )
    except ValueError as exc:
        st.warning(str(exc))

    # 10. Comprehension question
    st.markdown("## 9 · Pregunta de comprensión")
    _mcq(
        "fc_regimes",
        "Una losa presenta una frecuencia crítica de 250 Hz. ¿Debe utilizarse necesariamente "
        "la misma expresión de predicción de Lₙ a 125 Hz y a 1000 Hz?",
        [
            "A. Sí, porque el nivel de impacto depende solamente de la masa superficial.",
            "B. Sí, porque la frecuencia crítica solo afecta al aislamiento aéreo.",
            "C. No. 125 Hz está bajo la frecuencia crítica y 1000 Hz está sobre ella, por lo que corresponden a regímenes distintos.",
            "D. No, pero únicamente porque cambia la ponderación A.",
        ],
        2,
        "La frecuencia crítica marca un cambio en el comportamiento vibroacústico de la losa "
        "y las expresiones de Vér distinguen los regímenes bajo y sobre f_c.",
        store=True,
    )

    # Closing
    st.markdown("## 10 · Cierre")
    st.write(
        "Ahora podemos seguir la cadena completa: el impacto introduce energía mecánica, "
        "la losa responde vibratoriamente, esa vibración se convierte en potencia acústica "
        "según su eficiencia de radiación y finalmente aparece un nivel de ruido de impacto "
        "Lₙ en el recinto receptor."
    )
    st.latex(
        r"\boxed{\mathrm{IMPACTO}\rightarrow\mathrm{FUERZA}\rightarrow"
        r"\mathrm{VIBRACIÓN}\rightarrow\mathrm{RADIACIÓN}\rightarrow L_n}"
    )
    st.success(
        "En las siguientes etapas utilizaremos esta relación para analizar soluciones "
        "constructivas destinadas a reducir el ruido de impacto."
    )

    with st.container(border=True):
        st.markdown("### 📚 Referencia técnica de esta etapa")
        st.write(
            "Vér, I. L. & Beranek, L. L. (eds.). *Noise and Vibration Control Engineering: "
            "Principles and Applications*, 2nd ed., Wiley, 2006. "
            "Capítulo 11, §11.11 **Impact Noise**."
        )
        st.write(
            "Ecuaciones utilizadas: (11.158)–(11.160) para la excitación periódica, "
            "(11.162) para la potencia sonora radiada, (11.172) para el régimen sobre "
            "la frecuencia crítica y (11.173) para el régimen subcrítico."
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
    """ETAPA 6 — Predicción de la mejora de un piso flotante: ΔLₙ(f)."""
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    from core.course2_impact_models import (
        BANDS,
        surface_mass,
        reduced_mass,
        natural_frequency,
        transmissibility_force,
        nearest_band,
        delta_ln_cremer_continuous_db,
        delta_ln_ver_discrete_db,
    )

    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")
    ns = f"{class_id}_s6"
    stage_no = 6

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

    def _mcq(key, question, options, correct, feedback, store=False):
        st.markdown(f"#### {question}")
        if role == "Docente" and not projection_mode:
            with st.container(border=True):
                for i, opt in enumerate(options):
                    st.write(("✅ " if i == correct else "○ ") + opt)
                st.caption(feedback)
            return
        sk = f"{ns}_{key}"
        choice = st.radio(question, options, index=None, key=sk, label_visibility="collapsed")
        label = "Comprobar y guardar" if store and role == "Alumno" and not projection_mode else "Comprobar"
        if st.button(label, key=f"{sk}_check"):
            if choice is None:
                st.warning("Selecciona una alternativa.")
            else:
                idx = options.index(choice)
                ok = idx == correct
                st.session_state[f"{sk}_result"] = ok
                if store and role == "Alumno" and not projection_mode:
                    data = saved.get(f"stage{stage_no}_comprehension", {})
                    if not isinstance(data, dict):
                        data = {}
                    data[key] = {"selected": idx, "correct": ok, "updated_at": _now()}
                    saved[f"stage{stage_no}_comprehension"] = data
                    saved[f"updated_{stage_no}"] = _now()
                    _save_future_state_impl(class_id, saved)
        result = st.session_state.get(f"{sk}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.warning("Revisa el concepto. " + feedback)

    header(
        "ETAPA 6 · LABORATORIO 1",
        "Predicción de la mejora de un piso flotante: ΔLₙ(f)",
        "De la solución constructiva a la ecuación de mejora por bandas.",
        show_overview=False,
        duration_minutes=90,
    )

    # ================================================================
    # BLOQUE 1 — OBJETIVO
    # ================================================================
    st.markdown("## 1 · ¿Qué queremos calcular?")
    st.write(
        "En la Etapa 5 estimamos el nivel de ruido de impacto de la **losa base**, "
        "$L_{n,0}(f)$. Ahora queremos conocer cuánto cambia ese resultado cuando incorporamos "
        "una solución de piso flotante."
    )
    st.latex(r"\boxed{\Delta L_n(f)=L_{n,0}(f)-L_n(f)}")
    st.write(
        "$\\Delta L_n(f)$ es una **mejora por banda de frecuencia**. "
        "No es una constante del producto ni una penalización fija."
    )
    st.latex(
        r"\boxed{m'_1,\ m'_2,\ s'\rightarrow m'_r\rightarrow f_0"
        r"\rightarrow \mathrm{MODELO}\rightarrow\Delta L_n(f)}"
    )
    st.info(
        "La Etapa 6 termina en ΔLₙ(f). En la Etapa 7 combinaremos esa mejora con "
        "$L_{n,0}(f)$ para obtener el piso terminado."
    )

    # ================================================================
    # BLOQUE 2 — SISTEMA REAL Y TIPO DE MODELO
    # ================================================================
    st.markdown("## 2 · ¿Qué sistema constructivo estamos modelando?")
    _asset("curso2_lab1_etapa6_revestimiento_vs_flotante.webp")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Revestimiento resiliente superficial")
            st.write(
                "Ejemplos: alfombra, caucho o revestimiento blando directamente bajo la terminación. "
                "Su efecto principal está en el **contacto del impacto**: modifica $F(t)$ y $F(f)$."
            )
            st.latex(r"F(t)\rightarrow F(f)")
    with c2:
        with st.container(border=True):
            st.markdown("### Piso flotante")
            st.write(
                "Existe una **masa superior** separada de la losa base mediante un elemento resiliente. "
                "Aparece un sistema dinámico con resonancia propia."
            )
            st.latex(r"\mathrm{MASA\ SUPERIOR}+\mathrm{ELEMENTO\ RESILIENTE}+\mathrm{BASE}")

    st.latex(r"\boxed{\mathrm{REVESTIMIENTO\ RESILIENTE}\neq\mathrm{PISO\ FLOTANTE}}")

    st.markdown("### ¿Qué piso representa cada modelo?")
    st.write(
        "Antes de seleccionar Cremer o Vér debemos mirar **cómo está construido físicamente el piso**."
    )

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### A · Capa resiliente continua — modelo tipo Cremer")
            st.write(
                "La sobrelosa descansa sobre un material resiliente que cubre prácticamente toda la superficie."
            )
            st.write(
                "**Ejemplos reales:** manta acústica continua bajo sobrelosa; lámina elastomérica continua; "
                "lana mineral rígida colocada de forma continua; panel pesado sobre una capa resiliente continua."
            )
            st.latex(
                r"\mathrm{SOBRELOSA}\newline"
                r"\mathrm{CAPA\ RESILIENTE\ CONTINUA}\newline"
                r"\mathrm{LOSA\ BASE}"
            )
            st.write(
                "La transferencia mecánica se distribuye sobre la superficie."
            )
    with c2:
        with st.container(border=True):
            st.markdown("### B · Apoyos resilientes discretos — modelo tipo Vér")
            st.write(
                "La masa flotante descansa sobre elementos resilientes separados espacialmente."
            )
            st.write(
                "**Ejemplos reales:** pads de caucho; plots o pedestales elastoméricos; aisladores individuales; "
                "montajes antivibratorios distribuidos en una retícula."
            )
            st.latex(
                r"\mathrm{LOSA\ FLOTANTE}\newline"
                r"\bullet\quad\bullet\quad\bullet\quad\bullet\newline"
                r"\mathrm{LOSA\ BASE}"
            )
            st.write(
                "La transferencia se concentra en puntos de apoyo. Por eso aparece $N$, la densidad de apoyos por unidad de superficie."
            )

    st.warning(
        "Primero identificamos la configuración constructiva y **después** elegimos el modelo. "
        "No elegimos Cremer o Vér por la pendiente o por el resultado que nos convenga."
    )

    # ================================================================
    # BLOQUE 3 — PARÁMETROS DINÁMICOS
    # ================================================================
    st.markdown("## 3 · Construimos los parámetros dinámicos")
    _asset("curso2_lab1_etapa6_modelo_masa_resorte_masa.webp")
    st.latex(r"\boxed{m'_1\quad-\quad s'\quad-\quad m'_2}")
    st.write(
        "$m'_1$: masa superficial de la capa flotante · "
        "$s'$: rigidez dinámica superficial del apoyo resiliente · "
        "$m'_2$: masa superficial de la losa base."
    )

    st.markdown("### Masa superficial")
    st.latex(r"\boxed{m'=\rho h}")
    st.write(
        "La masa superficial indica cuánta masa aporta una capa por cada metro cuadrado."
    )
    st.latex(
        r"\rho=2100\ \mathrm{kg/m^3},\qquad "
        r"h=0.05\ \mathrm{m}\qquad "
        r"\Rightarrow\qquad "
        r"\boxed{m'=105\ \mathrm{kg/m^2}}"
    )

    st.markdown("### Rigidez dinámica superficial")
    _asset("curso2_lab1_etapa6_rigidez_dinamica.webp")
    st.latex(r"\boxed{s'\ [\mathrm{N/m^3}]\quad\text{o}\quad\mathrm{MN/m^3}}")
    st.write(
        "$s'$ describe cuánto se opone el elemento resiliente a una deformación **dinámica distribuida**."
    )
    st.warning(
        "No confundir $s'$ con el módulo de Young, la rigidez estática, el espesor ni la constante de un resorte puntual."
    )

    st.markdown("### Masa reducida")
    st.write(
        "Cuando ambas masas pueden participar en el movimiento relativo, utilizamos una masa equivalente:"
    )
    st.latex(r"\boxed{m'_r=\frac{m'_1m'_2}{m'_1+m'_2}}")
    st.write(
        "Si la losa base es mucho más pesada que la sobrelosa, entonces $m'_r\approx m'_1$."
    )

    st.markdown("### 🔬 Construye el sistema")
    c1, c2, c3 = st.columns(3)
    m1 = c1.slider("m′₁ [kg/m²]", 50, 250, 120, 5, key=f"{ns}_model_m1")
    m2 = c2.slider("m′₂ [kg/m²]", 150, 600, 400, 10, key=f"{ns}_model_m2")
    s_dyn = c3.slider("s′ [MN/m³]", 3.0, 50.0, 10.0, .5, key=f"{ns}_model_s")
    mr, f0_general = natural_frequency(m1, m2, s_dyn)
    a,b,c = st.columns(3)
    a.metric("m′ᵣ", f"{mr:.1f} kg/m²")
    b.metric("f₀ general", f"{f0_general:.1f} Hz")
    c.metric("1/3 octava cercana", f"{nearest_band(f0_general):g} Hz")

    # ================================================================
    # BLOQUE 4 — RESONANCIA Y TF
    # ================================================================
    st.markdown("## 4 · ¿Qué significa la resonancia?")
    st.latex(r"\boxed{f_0=\frac1{2\pi}\sqrt{\frac{s'}{m'_r}}}")
    st.write(
        "$f_0$ identifica la región donde el sistema puede presentar una respuesta relativa elevada. "
        "No significa que desde allí el piso comience a aislar perfectamente."
    )
    st.latex(r"s'\uparrow\Rightarrow f_0\uparrow,\qquad m'_r\uparrow\Rightarrow f_0\downarrow")

    st.markdown("### Transmisibilidad: solo para entender la dinámica")
    st.latex(r"\boxed{r=\frac f{f_0}}")
    st.latex(
        r"\boxed{T_F=\sqrt{\frac{1+(2\zeta r)^2}{(1-r^2)^2+(2\zeta r)^2}}}"
    )
    st.error("⚠️ $T_F\\neq\\Delta L_n$")
    st.write(
        "$T_F$ describe la transmisión mecánica de fuerza en un sistema ideal. "
        "$\\Delta L_n$ es una mejora vibroacústica y requiere un modelo adicional."
    )

    st.markdown("### 🔬 Atraviesa la resonancia")
    c1,c2,c3 = st.columns(3)
    tf0 = c1.slider("f₀ [Hz]", 20.0, 200.0, 60.0, 1.0, key=f"{ns}_tf0")
    ff = c2.slider("f [Hz]", 10.0, 500.0, 90.0, 1.0, key=f"{ns}_ff")
    zeta = c3.slider("ζ", .01, .40, .10, .01, key=f"{ns}_zeta")
    r = ff/tf0
    tf = transmissibility_force(r, zeta)
    a,b = st.columns(2)
    a.metric("r=f/f₀", f"{r:.2f}")
    b.metric("T_F", f"{tf:.2f}")
    rr=np.linspace(.1,4,500)
    yy=np.sqrt((1+(2*zeta*rr)**2)/((1-rr**2)**2+(2*zeta*rr)**2))
    fig,ax=plt.subplots()
    ax.plot(rr,yy)
    ax.scatter([r],[tf])
    ax.axvline(1,linestyle="--",label="resonancia")
    ax.axvline(math.sqrt(2),linestyle=":",label="r=√2")
    ax.set_xlabel("r=f/f₀")
    ax.set_ylabel("T_F")
    ax.set_ylim(0,8)
    ax.grid(True,alpha=.2)
    ax.legend()
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    # ================================================================
    # BLOQUE 5 — DELTA L: CORAZÓN DE LA ETAPA
    # ================================================================
    st.markdown("## 5 · El salto clave: de f₀ a ΔLₙ(f)")
    st.write(
        "Hasta ahora solo hemos descrito la dinámica. **Aquí aparece por primera vez la ecuación que entrega la mejora acústica.**"
    )

    st.markdown("### A · Capa resiliente continua — Cremer/Vigran")
    st.write(
        "Para una capa elástica continua idealizada, con la base suficientemente pesada/impedante, "
        "la mejora de nivel de impacto puede escribirse como:"
    )
    st.latex(
        r"\boxed{\Delta L_n(f)=20\log_{10}\left(\frac{\omega^2m'_1}{s'}\right)}"
    )
    st.write("con $\\omega=2\\pi f$:")
    st.latex(
        r"\boxed{\Delta L_n(f)=20\log_{10}\left(\frac{(2\pi f)^2m'_1}{s'}\right)}"
    )
    st.write(
        "Si definimos la frecuencia natural del **modelo continuo simplificado**:"
    )
    st.latex(
        r"\boxed{f_{0,\mathrm{cont}}\approx\frac1{2\pi}\sqrt{\frac{s'}{m'_1}}}"
    )
    st.write("entonces:")
    st.latex(
        r"\boxed{\Delta L_n(f)=40\log_{10}\left(\frac f{f_{0,\mathrm{cont}}}\right)}"
    )
    st.warning(
        "Este $f_{0,\mathrm{cont}}$ no es necesariamente idéntico al $f_0$ general calculado con masa reducida. "
        "La diferencia proviene de la hipótesis de base muy pesada del modelo simplificado."
    )
    st.caption(
        "Fuente: Vigran, *Building Acoustics* (2008), Ec. 8.44; "
        "Cremer, Heckl & Ungar, *Structure-Borne Sound*, Ecs. 406–406a."
    )

    st.markdown("### B · Apoyos resilientes discretos — Vér")
    st.write(
        "Para apoyos elásticos discretos, Vér estudia un sistema diferente. "
        "La aproximación de alta frecuencia utilizada aquí es:"
    )
    st.latex(
        r"\boxed{\Delta L_n(f)\approx10\log_{10}\left["
        r"\frac{c_{L1}h_1N\eta_{11}}{2\pi^3f_0^4}\,f^3\right]}"
    )
    st.write(
        "$N$ representa la cantidad de apoyos por unidad de superficie. "
        "El término $f^3$ conduce a una tendencia cercana a 9 dB/octava bajo las hipótesis correspondientes."
    )
    st.caption(
        "Fuente: Vigran, *Building Acoustics* (2008), Ecs. 8.45–8.46; Vér (1971)."
    )

    c1,c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Cremer")
            st.write("Manta/capa resiliente continua.")
            st.write("Transferencia distribuida.")
            st.write("Modelo localmente reactivo idealizado.")
    with c2:
        with st.container(border=True):
            st.markdown("### Vér")
            st.write("Pads, plots o aisladores separados.")
            st.write("Transferencia concentrada en apoyos.")
            st.write("Modelo para apoyos discretos.")

    # ================================================================
    # BLOQUE 6 — LABORATORIO ESTRELLA
    # ================================================================
    st.markdown("## 🔬 6 · Laboratorio principal — Predice ΔLₙ(f)")
    st.write(
        "Selecciona primero el **tipo físico de piso**. La app mostrará únicamente las variables compatibles con ese modelo."
    )

    model = st.segmented_control(
        "Configuración constructiva",
        [
            "CAPA RESILIENTE CONTINUA — CREMER",
            "APOYOS RESILIENTES DISCRETOS — VÉR",
        ],
        default="CAPA RESILIENTE CONTINUA — CREMER",
        key=f"{ns}_main_model",
    )

    if model.startswith("CAPA"):
        c1,c2 = st.columns(2)
        cm1 = c1.slider("m′₁ [kg/m²]", 50, 250, 120, 5, key=f"{ns}_cm1")
        cs = c2.slider("s′ [MN/m³]", 3.0, 50.0, 10.0, .5, key=f"{ns}_cs")

        f0_cont = (1/(2*math.pi))*math.sqrt((cs*1e6)/cm1)
        vals=[]
        for f in BANDS:
            d,_ = delta_ln_cremer_continuous_db(f, cm1, cs)
            vals.append(d)
        vals=np.array(vals,dtype=float)

        a,b = st.columns(2)
        a.metric("f₀ continuo", f"{f0_cont:.1f} Hz")
        b.metric("Tipo de apoyo", "Continuo")

        fig,ax=plt.subplots()
        ax.semilogx(BANDS,vals,marker="o",label="ΔLₙ(f)")
        ax.axvline(f0_cont,linestyle="--",label="f₀ continuo")
        ax.axvline(4*f0_cont,linestyle=":",label="4f₀ · referencia")
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("ΔLₙ [dB]")
        ax.grid(True,which="both",alpha=.2)
        ax.legend()
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)

        st.dataframe(
            [
                {
                    "f [Hz]":int(f),
                    "f/f₀":round(float(f/f0_cont),2),
                    "ΔLₙ [dB]":None if np.isnan(d) else round(float(d),1),
                }
                for f,d in zip(BANDS,vals)
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Bandas en o bajo la resonancia quedan sin valor. "
            "Valores muy alejados de la región de validez deben interpretarse como extrapolación del modelo ideal."
        )

    else:
        c1,c2,c3 = st.columns(3)
        vh = c1.slider("h₁ [mm]", 20, 120, 50, 5, key=f"{ns}_vh")
        vcL = c2.slider("c_L1 [m/s]", 1000, 6000, 3500, 100, key=f"{ns}_vcl")
        vN = c3.slider("N [apoyos/m²]", 1.0, 25.0, 9.0, 1.0, key=f"{ns}_vN")
        c4,c5 = st.columns(2)
        veta = c4.slider("η₁₁", .005, .100, .020, .005, key=f"{ns}_veta")
        vf0 = c5.slider("f₀ [Hz]", 20.0, 150.0, 40.0, 1.0, key=f"{ns}_vf0")

        vals=np.array(
            [
                delta_ln_ver_discrete_db(f,vf0,vh/1000,vcL,vN,veta) if f>vf0 else np.nan
                for f in BANDS
            ],
            dtype=float,
        )

        a,b = st.columns(2)
        a.metric("f₀", f"{vf0:.1f} Hz")
        b.metric("Densidad de apoyos N", f"{vN:.0f} /m²")

        fig,ax=plt.subplots()
        ax.semilogx(BANDS,vals,marker="o",label="ΔLₙ(f)")
        ax.axvline(vf0,linestyle="--",label="f₀")
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("ΔLₙ [dB]")
        ax.grid(True,which="both",alpha=.2)
        ax.legend()
        st.pyplot(fig,use_container_width=True)
        plt.close(fig)

        st.dataframe(
            [
                {
                    "f [Hz]":int(f),
                    "f/f₀":round(float(f/vf0),2),
                    "ΔLₙ [dB]":None if np.isnan(d) else round(float(d),1),
                }
                for f,d in zip(BANDS,vals)
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Aproximación de alta frecuencia para apoyos elásticos discretos. "
            "No debe trasladarse a una manta continua."
        )

    # ================================================================
    # BLOQUE 7 — DEFECTOS
    # ================================================================
    st.markdown("## 7 · ¿Qué pasa si la obra deja de parecerse al modelo?")
    _asset("curso2_lab1_etapa6_piso_correcto_puenteado.webp")
    st.write(
        "Los modelos anteriores suponen un desacople definido. Un puente rígido crea un camino mecánico paralelo."
    )
    st.latex(r"\boxed{K_{\mathrm{eq}}=K_{\mathrm{res}}+\sum_iK_{\mathrm{puente},i}}")

    defect = st.selectbox(
        "Selecciona un defecto",
        [
            "Contacto perimetral",
            "Tornillo atravesando la capa resiliente",
            "Tubería rígida",
            "Capa resiliente discontinua",
        ],
        key=f"{ns}_defect",
    )

    defect_data = {
        "Contacto perimetral": (
            "La sobrelosa toca el muro y aparece una ruta rígida lateral.",
            "Restituir banda perimetral y separación mecánica.",
            "Requiere caracterizar rigidez y extensión del contacto; no corresponde asignar una penalización fija en dB.",
        ),
        "Tornillo atravesando la capa resiliente": (
            "El tornillo une la masa superior con la base y puentea el apoyo resiliente.",
            "Eliminar o rediseñar la fijación para mantener el desacople.",
            "Puede aproximarse mediante una rigidez puntual adicional, pero el modelo continuo deja de representar completamente el sistema.",
        ),
        "Tubería rígida": (
            "La tubería o su soporte se transforma en un camino estructural adicional.",
            "Usar penetraciones y soportes desacoplados compatibles con la instalación.",
            "Debe analizarse como un camino adicional con su propia impedancia/rigidez dinámica.",
        ),
        "Capa resiliente discontinua": (
            "Aparecen zonas de apoyo de rigidez distinta o contacto directo.",
            "Restituir continuidad y apoyo uniforme de la capa.",
            "Una rigidez efectiva solo es una aproximación si se conoce la proporción y geometría del defecto.",
        ),
    }
    mechanism, correction, calculation = defect_data[defect]

    c1,c2,c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### Mecanismo")
            st.write(mechanism)
    with c2:
        with st.container(border=True):
            st.markdown("### Corrección")
            st.write(correction)
    with c3:
        with st.container(border=True):
            st.markdown("### ¿Cómo se calcula?")
            st.write(calculation)

    st.warning(
        "NO ES INCALCULABLE ≠ LO CALCULA ESTE MODELO. "
        "Un defecto puede requerir caminos estructurales separados, FEM/SEA o medición."
    )

    # ================================================================
    # BLOQUE 8 — EJERCICIO FINAL
    # ================================================================
    st.markdown("## 8 · Ejercicio final: del piso real a ΔLₙ")
    st.write(
        "Consideremos un piso flotante con capa resiliente **continua**:"
    )
    st.latex(
        r"m'_1=120\ \mathrm{kg/m^2},\qquad "
        r"m'_2=400\ \mathrm{kg/m^2},\qquad "
        r"s'=10\ \mathrm{MN/m^3}"
    )

    emr, ef0 = natural_frequency(120,400,10)
    st.markdown("### Paso 1 · Modelo general")
    st.latex(
        r"m'_r=\frac{120(400)}{120+400}"
        r"=\boxed{92.3\ \mathrm{kg/m^2}}"
    )
    st.latex(
        r"f_{0,\mathrm{general}}=\frac1{2\pi}\sqrt{\frac{10\times10^6}{92.3}}"
        r"=\boxed{52.4\ \mathrm{Hz}}"
    )
    st.write(
        "Este valor caracteriza el sistema general de dos masas."
    )

    st.markdown("### Paso 2 · Elegimos el modelo compatible con la construcción")
    st.write(
        "Como el apoyo es una **capa resiliente continua**, adoptamos la formulación de Cremer/Vigran."
    )
    f0_cont_ex = (1/(2*math.pi))*math.sqrt(10e6/120.0)
    st.latex(
        r"f_{0,\mathrm{cont}}\approx\frac1{2\pi}\sqrt{\frac{10\times10^6}{120}}"
        rf"=\boxed{{{f0_cont_ex:.1f}\ \mathrm{{Hz}}}}"
    )
    st.write(
        "La diferencia entre 52.4 Hz y este valor no es un error: "
        "el segundo pertenece a la aproximación de base suficientemente pesada utilizada por el modelo continuo."
    )

    st.markdown("### Paso 3 · Calculamos ΔLₙ a 125 Hz")
    f_ex=125.0
    arg_ex=(((2*math.pi*f_ex)**2)*120.0)/10e6
    delta_ex=20*math.log10(arg_ex)
    st.latex(
        r"\Delta L_n(125)=20\log_{10}\left["
        r"\frac{(2\pi\cdot125)^2(120)}{10\times10^6}\right]"
    )
    st.latex(rf"\boxed{{\Delta L_n(125)\approx {delta_ex:.1f}\ \mathrm{{dB}}}}")

    st.markdown("### Paso 4 · Calculamos por bandas")
    rows=[]
    for f in [63,125,250]:
        d,_=delta_ln_cremer_continuous_db(f,120,10)
        rows.append(
            {
                "f [Hz]":f,
                "f/f₀ continuo":round(f/f0_cont_ex,2),
                "ΔLₙ [dB]":None if np.isnan(d) else round(float(d),1),
            }
        )
    st.dataframe(rows,use_container_width=True,hide_index=True)
    st.write(
        "Ahora cada valor tiene un origen visible: **configuración real → modelo → parámetros → ecuación → ΔLₙ(f)**."
    )

    _mcq(
        "final_origin",
        "¿Qué debemos hacer antes de aplicar una ecuación de ΔLₙ?",
        [
            "A. Elegir la ecuación que entregue mayor mejora.",
            "B. Identificar cómo está construido el piso y seleccionar el modelo compatible.",
            "C. Usar siempre Vér.",
            "D. Usar siempre Cremer.",
        ],
        1,
        "Primero se identifica la configuración física; después se selecciona el modelo.",
        store=True,
    )

    st.markdown("## 9 · Preguntas de comprensión")
    _mcq("q1","Una manta continua y pads separados representan exactamente el mismo sistema.",["Verdadero","Falso"],1,"Son configuraciones diferentes.",store=True)
    _mcq("q2","$f_0$ por sí sola entrega ΔLₙ.",["Verdadero","Falso"],1,"f₀ localiza la resonancia; se requiere un modelo de mejora.",store=True)
    _mcq("q3","$T_F$ y ΔLₙ son exactamente la misma magnitud.",["Verdadero","Falso"],1,"Una es mecánica y la otra vibroacústica.",store=True)
    _mcq("q4","En el modelo de Vér mostrado, N representa la densidad de apoyos discretos.",["Verdadero","Falso"],0,"Correcto.",store=True)
    _mcq("q5","Un puente rígido puede dejar la obra fuera de las hipótesis del modelo ideal.",["Verdadero","Falso"],0,"Correcto.",store=True)

    st.markdown("## 10 · Cierre")
    st.latex(
        r"\boxed{\mathrm{CONSTRUCCIÓN}\rightarrow\mathrm{MODELO}"
        r"\rightarrow(m',s')\rightarrow f_0\rightarrow\Delta L_n(f)}"
    )
    st.write(
        "La mejora de impacto no se obtiene solo con una frecuencia de resonancia ni con una transmisibilidad. "
        "Primero debemos identificar el sistema físico y luego utilizar una formulación compatible con esa configuración."
    )
    st.write("En la Etapa 7 combinaremos:")
    st.latex(r"\boxed{L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)}")

    with st.container(border=True):
        st.markdown("### 📚 Fuentes técnicas")
        st.write("Vigran, T. E. (2008), *Building Acoustics*, sección de pisos flotantes, Ecs. 8.43–8.46.")
        st.write("Cremer, Heckl & Ungar, *Structure-Borne Sound*, formulación de pisos flotantes continuos.")
        st.write("Vér, I. L. (1971), *Impact noise isolation of composite floors*, JASA 50, 1043–1050.")

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
    """ETAPA 7 — Predicción completa del piso: de la losa base al sistema terminado."""
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    from core.acoustics import critical_frequency
    from core.course2_impact_models import (
        BANDS,
        ver_ln_piecewise_db,
        reduced_mass,
        natural_frequency,
        delta_ln_cremer_continuous_db,
        delta_ln_ver_discrete_db,
    )

    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"
    role = st.session_state.get("role", "Alumno")
    projection_mode = bool(st.session_state.get("projection_mode") or role == "Proyección")
    ns = f"{class_id}_s7"
    stage_no = 7

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

    def _mcq(key, question, options, correct, feedback, store=False):
        st.markdown(f"#### {question}")
        if role == "Docente" and not projection_mode:
            with st.container(border=True):
                for i, opt in enumerate(options):
                    st.write(("✅ " if i == correct else "○ ") + opt)
                st.caption(feedback)
            return
        sk = f"{ns}_{key}"
        choice = st.radio(question, options, index=None, key=sk, label_visibility="collapsed")
        label = "Comprobar y guardar" if store and role == "Alumno" and not projection_mode else "Comprobar"
        if st.button(label, key=f"{sk}_check"):
            if choice is None:
                st.warning("Selecciona una alternativa.")
            else:
                idx = options.index(choice)
                ok = idx == correct
                st.session_state[f"{sk}_result"] = ok
                if store and role == "Alumno" and not projection_mode:
                    data = saved.get(f"stage{stage_no}_comprehension", {})
                    if not isinstance(data, dict):
                        data = {}
                    data[key] = {"selected": idx, "correct": ok, "updated_at": _now()}
                    saved[f"stage{stage_no}_comprehension"] = data
                    saved[f"updated_{stage_no}"] = _now()
                    _save_future_state_impl(class_id, saved)
        result = st.session_state.get(f"{sk}_result")
        if result is True:
            st.success("Correcto. " + feedback)
        elif result is False:
            st.warning("Revisa el concepto. " + feedback)

    # ------------------------------------------------------------------
    # Shared numerical inputs/functions: reuse Stage 5 and Stage 6 logic.
    # ------------------------------------------------------------------
    bands = np.asarray(BANDS, dtype=float)
    band_x = np.arange(len(bands), dtype=float)

    def _band_labels():
        labels = []
        for f in bands:
            if f >= 1000:
                k = f / 1000.0
                labels.append(f"{k:g}k")
            else:
                labels.append(f"{int(round(f))}")
        return labels

    def _format_band_axis(ax):
        ax.set_xticks(band_x)
        ax.set_xticklabels(_band_labels(), rotation=45, ha="right")
        ax.set_xlabel("Bandas de frecuencia [Hz]")
        ax.grid(True, axis="y", alpha=.2)
        ax.margins(x=.02)

    def _plot_band_curve(ax, values, label, marker="o"):
        arr = np.asarray(values, dtype=float)
        ax.plot(band_x, arr, marker=marker, label=label)

    def _nearest_band_text(freq):
        idx = int(np.argmin(np.abs(np.log(bands / float(freq)))))
        nearest = bands[idx]
        return f"{float(freq):.1f} Hz · banda central más cercana: {int(round(nearest))} Hz"

    # Same didactic R(f) subset used in Stage 5, restricted to the exact
    # bands shared with Stage 6: 125–2000 Hz in thirds of octave.
    R_base = np.array([48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60], dtype=float)

    # Stage 5 default homogeneous concrete slab used as the exercise base.
    rho_p_base = 2400.0
    t_base_mm = 160.0
    E_base_gpa = 30.0
    nu_base = 0.20
    sigma_base = 1.0
    eta_base = 0.020

    _, _, fc_base = critical_frequency(
        rho_p_base, t_base_mm, E_base_gpa, nu_base, 343.0
    )

    def _ln0_curve():
        vals = []
        regimes = []
        for f, R in zip(bands, R_base):
            ln, regime = ver_ln_piecewise_db(
                f, R, fc_base, sigma_base, eta_base, 0.0
            )
            vals.append(float(ln))
            regimes.append(regime)
        return np.asarray(vals, dtype=float), regimes

    def _delta_continuous_curve(m1, s_mn):
        vals = []
        f0_cont = (1/(2*math.pi))*math.sqrt((float(s_mn)*1e6)/float(m1))
        for f in bands:
            d, _ = delta_ln_cremer_continuous_db(f, m1, s_mn)
            vals.append(d)
        return np.asarray(vals, dtype=float), f0_cont

    def _delta_discrete_curve(f0, h1_mm, cL1, N, eta11):
        vals = []
        for f in bands:
            if f <= f0:
                vals.append(np.nan)
            else:
                vals.append(
                    delta_ln_ver_discrete_db(
                        f, f0, float(h1_mm)/1000.0, cL1, N, eta11
                    )
                )
        return np.asarray(vals, dtype=float)

    def _final_curve(ln0, delta):
        out = np.full_like(ln0, np.nan, dtype=float)
        mask = np.isfinite(ln0) & np.isfinite(delta)
        out[mask] = ln0[mask] - delta[mask]
        return out

    ln0_base, regimes_base = _ln0_curve()

    header(
        "ETAPA 7 · LABORATORIO 1",
        "Predicción completa del piso: de la losa base al sistema terminado",
        "Aplicación práctica avanzada del bloque predictivo de ruido de impacto.",
        show_overview=False,
        duration_minutes=95,
    )

    # ================================================================
    # 1. APERTURA
    # ================================================================
    st.markdown("## 1 · Ya tenemos las dos piezas del problema")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### ETAPA 5 · LOSA BASE")
            st.latex(r"\boxed{L_{n,0}(f)}")
            st.write("Predicción espectral del nivel de ruido de impacto de la losa sin tratamiento.")
    with c2:
        with st.container(border=True):
            st.markdown("### ETAPA 6 · MEJORA")
            st.latex(r"\boxed{\Delta L_n(f)}")
            st.write("Mejora espectral introducida por el tratamiento compatible con el modelo seleccionado.")

    st.write("¿Cómo obtenemos ahora el nivel estimado del piso terminado?")
    st.latex(
        r"\boxed{L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)}"
    )
    st.caption("Esta relación se obtiene directamente por reordenamiento de la definición de ΔLₙ anterior.")
    st.success(
        "Ésta es la ecuación visual principal de la Etapa 7. "
        r"La salida que compararemos será $L_{n,\mathrm{final}}(f)$ por bandas."
    )

    # ================================================================
    # 2. PHYSICAL INTERPRETATION + DECIBELS
    # ================================================================
    st.markdown("## 2 · ¿Qué significa cada término?")
    c1,c2,c3=st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### LOSA BASE")
            st.latex(r"L_{n,0}(f)")
            st.write("Nivel estimado antes del tratamiento.")
    with c2:
        with st.container(border=True):
            st.markdown("### MEJORA")
            st.latex(r"\Delta L_n(f)")
            st.write("Diferencia de niveles introducida por el tratamiento.")
    with c3:
        with st.container(border=True):
            st.markdown("### PISO TERMINADO")
            st.latex(r"L_{n,\mathrm{final}}(f)")
            st.write("Nivel estimado después de aplicar la mejora.")

    st.markdown("### ¿Por qué podemos restar decibeles aquí?")
    st.write(
        "$\\Delta L_n$ ya está **definido como una diferencia de niveles** expresada en dB:"
    )
    st.latex(r"\Delta L_n(f)=L_{n,0}(f)-L_n(f)")
    st.write("Por definición:")
    st.latex(r"L_n(f)=L_{n,0}(f)-\Delta L_n(f)")
    st.info(
        "No estamos restando directamente potencias lineales. "
        "Estamos aplicando una diferencia de niveles previamente definida."
    )

    # ================================================================
    # 3. SIMPLE EXAMPLE
    # ================================================================
    st.markdown("## 3 · Ejemplo simple · 500 Hz")
    st.latex(r"L_{n,0}(500)=69\ \mathrm{dB}")
    st.latex(r"\Delta L_n(500)=22\ \mathrm{dB}")
    st.latex(r"L_{n,\mathrm{final}}(500)=69-22")
    st.latex(r"\boxed{L_{n,\mathrm{final}}(500)=47\ \mathrm{dB}}")
    st.write(
        "La lectura correcta es: según el modelo utilizado, el tratamiento reduce 22 dB "
        "el nivel de la losa base **en la banda de 500 Hz**."
    )
    st.warning(
        "No significa que todas las bandas mejoren 22 dB, que cualquier obra mida exactamente 47 dB, "
        "que se hayan incluido flancos ni que 47 dB sea un número único."
    )
    _mcq(
        "simple47",
        "¿Una obra construida con esta solución necesariamente medirá exactamente 47 dB a 500 Hz?",
        ["A. Sí", "B. No"],
        1,
        "Es una predicción dentro de las hipótesis del modelo; ejecución, materiales, bordes y caminos secundarios pueden modificarla.",
    )

    _asset("curso2_lab1_etapa7_losa_base_piso_final.webp")

    # ================================================================
    # 4. MAIN INTERACTIVE
    # ================================================================
    st.markdown("## 🔬 4 · Interactivo principal — Construye la predicción completa")
    st.write(
        "La rama de la losa base reutiliza la función de la Etapa 5. "
        "La rama del tratamiento reutiliza las funciones de la Etapa 6. "
        "Aquí **no se vuelven a definir sus ecuaciones**."
    )

    with st.container(border=True):
        st.markdown("### Flujo")
        st.latex(
            r"\mathrm{LOSA\ BASE}\rightarrow\mathrm{MODELO\ ETAPA\ 5}"
            r"\rightarrow L_{n,0}(f)"
        )
        st.latex(
            r"\mathrm{TRATAMIENTO}\rightarrow(m'_1,m'_2,s')"
            r"\rightarrow\mathrm{MODELO\ ETAPA\ 6}\rightarrow\Delta L_n(f)"
        )
        st.latex(
            r"\boxed{L_{n,0}(f)-\Delta L_n(f)\rightarrow L_{n,\mathrm{final}}(f)}"
        )

    st.caption(
        "Losa base didáctica de esta etapa: hormigón homogéneo 160 mm, "
        "ρ=2400 kg/m³, E=30 GPa, ν=0.20; R(f) proviene del ejercicio de Etapa 5. "
        "No corresponde a una ficha comercial."
    )

    model_main = st.segmented_control(
        "Tratamiento",
        [
            "CAPA RESILIENTE CONTINUA — CREMER",
            "APOYOS RESILIENTES DISCRETOS — VÉR",
        ],
        default="CAPA RESILIENTE CONTINUA — CREMER",
        key=f"{ns}_main_model",
    )

    if model_main.startswith("CAPA"):
        c1,c2,c3=st.columns(3)
        main_m1=c1.slider("m′₁ [kg/m²]",50,200,110,5,key=f"{ns}_main_m1")
        main_m2=c2.slider("m′₂ [kg/m²]",150,600,380,10,key=f"{ns}_main_m2")
        main_s=c3.slider("s′ [MN/m³]",3.0,40.0,12.0,.5,key=f"{ns}_main_s")
        main_mr, main_f0_general = natural_frequency(main_m1, main_m2, main_s)
        delta_main, main_f0_model = _delta_continuous_curve(main_m1,main_s)
    else:
        c1,c2,c3=st.columns(3)
        main_m1=c1.slider("m′₁ [kg/m²]",50,200,110,5,key=f"{ns}_main_vm1")
        main_m2=c2.slider("m′₂ [kg/m²]",150,600,380,10,key=f"{ns}_main_vm2")
        main_s=c3.slider("s′ equivalente [MN/m³]",3.0,40.0,12.0,.5,key=f"{ns}_main_vs")
        main_mr, main_f0_general = natural_frequency(main_m1, main_m2, main_s)
        d1,d2,d3=st.columns(3)
        h1=d1.slider("h₁ [mm]",20,120,50,5,key=f"{ns}_main_h1")
        cL1=d2.slider("c_L1 [m/s]",1000,6000,3500,100,key=f"{ns}_main_cL")
        N=d3.slider("N [apoyos/m²]",1.0,25.0,9.0,1.0,key=f"{ns}_main_N")
        d4,d5=st.columns(2)
        eta11=d4.slider("η₁₁",.005,.100,.020,.005,key=f"{ns}_main_eta")
        main_f0_model=d5.slider("f₀ del modelo Vér [Hz]",20.0,150.0,float(round(main_f0_general)),1.0,key=f"{ns}_main_vf0")
        delta_main=_delta_discrete_curve(main_f0_model,h1,cL1,N,eta11)

    final_main=_final_curve(ln0_base,delta_main)

    st.markdown("### Tres salidas distintas")
    a,b,c=st.columns(3)
    a.metric("LOSA BASE · Lₙ,₀", "curva por bandas")
    b.metric("MEJORA · ΔLₙ", "curva por bandas")
    c.metric("PISO TERMINADO · Lₙ,final", "curva por bandas")
    d,e=st.columns(2)
    d.metric("m′ᵣ",f"{main_mr:.1f} kg/m²")
    e.metric("f₀ general",f"{main_f0_general:.1f} Hz")

    st.markdown("### Gráfico principal · losa base vs piso terminado")
    st.caption(
        "Resultados presentados en las mismas bandas centrales utilizadas por las Etapas 5 y 6. "
        "Los segmentos solo conectan visualmente valores de bandas discretas; no representan una interpolación continua."
    )
    show_base=st.checkbox("Mostrar LOSA BASE",True,key=f"{ns}_show_base")
    show_final=st.checkbox("Mostrar PISO TERMINADO",True,key=f"{ns}_show_final")
    fig,ax=plt.subplots()
    if show_base:
        _plot_band_curve(ax, ln0_base, "LOSA BASE · Lₙ,₀")
    if show_final:
        _plot_band_curve(ax, final_main, "PISO TERMINADO · Lₙ,final")
    _format_band_axis(ax)
    ax.set_ylabel("Nivel de ruido de impacto [dB]")
    ax.legend()
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    st.markdown("### Gráfico de mejora")
    fig,ax=plt.subplots()
    _plot_band_curve(ax, delta_main, "ΔLₙ(f)")
    _format_band_axis(ax)
    ax.set_ylabel("ΔLₙ [dB]")
    ax.legend()
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)
    st.caption(
        "f₀ es un parámetro físico continuo y no una banda espectral. "
        "Por eso no se dibuja como un punto de la curva por bandas."
    )
    st.info(
        "Frecuencia natural del modelo: "
        + _nearest_band_text(main_f0_model)
        + ". Esto solo ubica la resonancia respecto de las bandas analizadas."
    )

    st.markdown("### Tabla por bandas")
    table_main=[]
    for f,R,l0,d,lf in zip(bands,R_base,ln0_base,delta_main,final_main):
        table_main.append({
            "Frecuencia [Hz]":int(f),
            "R(f) [dB]":round(float(R),1),
            "Lₙ,₀(f) [dB]":round(float(l0),1),
            "ΔLₙ(f) [dB]":None if not np.isfinite(d) else round(float(d),1),
            "Lₙ,final(f) [dB]":None if not np.isfinite(lf) else round(float(lf),1),
        })
    st.dataframe(table_main,use_container_width=True,hide_index=True)

    _mcq(
        "notconstant",
        "¿El tratamiento desplaza toda la curva exactamente la misma cantidad?",
        ["A. Sí", "B. No"],
        1,
        "No. ΔLₙ es función de la frecuencia, por lo que la separación entre las curvas cambia por banda.",
    )

    # ================================================================
    # 5. THREE ALTERNATIVES
    # ================================================================
    st.markdown("## 5 · Problema de diseño — Compara tres pisos")
    _asset("curso2_lab1_etapa7_tres_alternativas.webp")
    st.write("Losa base común: $m'_2=380$ kg/m². Las tres alternativas usan capa resiliente continua.")
    st.caption(
        "Masa reducida y frecuencia natural: modelo clásico masa–resorte–masa desarrollado en Etapa 6. "
        "La referencia bibliográfica exacta de esta derivación debe mantenerse trazada en la documentación técnica del curso."
    )

    alternatives={
        "A":{"m1":70.0,"m2":380.0,"s":25.0,"h":45.0},
        "B":{"m1":110.0,"m2":380.0,"s":12.0,"h":65.0},
        "C":{"m1":150.0,"m2":380.0,"s":8.0,"h":90.0},
    }
    alt_results={}
    cols=st.columns(3)
    for col,(name,p) in zip(cols,alternatives.items()):
        mr_i,f0_i=natural_frequency(p["m1"],p["m2"],p["s"])
        delta_i,f0c_i=_delta_continuous_curve(p["m1"],p["s"])
        final_i=_final_curve(ln0_base,delta_i)
        alt_results[name]={**p,"mr":mr_i,"f0":f0_i,"f0_model":f0c_i,"delta":delta_i,"final":final_i}
        with col:
            with st.container(border=True):
                st.markdown(f"### Alternativa {name}")
                st.write(f"m′₁ = {p['m1']:.0f} kg/m²")
                st.write(f"s′ = {p['s']:.0f} MN/m³")
                st.write(f"m′ᵣ ≈ {mr_i:.1f} kg/m²")
                st.write(f"f₀ general ≈ {f0_i:.1f} Hz")

    st.caption(
        "Validación requerida: A ≈ 59.1 kg/m² y 103.5 Hz · "
        "B ≈ 85.3 kg/m² y 59.7 Hz · C ≈ 107.5 kg/m² y 43.4 Hz."
    )

    st.markdown("## 🔬 6 · Interactivo — Compara tres pisos")
    alt_sel=st.segmented_control(
        "Mostrar",["A","B","C","COMPARAR TODAS"],default="COMPARAR TODAS",key=f"{ns}_altsel"
    )
    fig,ax=plt.subplots()
    names=list(alternatives) if alt_sel=="COMPARAR TODAS" else [alt_sel]
    for name in names:
        _plot_band_curve(ax, alt_results[name]["final"], f"{name} · Lₙ,final")
    _format_band_axis(ax)
    ax.set_ylabel("Lₙ,final [dB]")
    ax.legend()
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    def _best_at(freq):
        idx=int(np.argmin(np.abs(np.log(bands/float(freq)))))
        vals={n:alt_results[n]["final"][idx] for n in alternatives}
        vals={n:v for n,v in vals.items() if np.isfinite(v)}
        if not vals:
            return None,None,idx
        best=min(vals,key=vals.get)
        return best,vals[best],idx

    st.markdown("### Interpretación calculada")
    qcols=st.columns(3)
    for col,freq in zip(qcols,[125,500,1000]):
        best,val,idx=_best_at(freq)
        with col:
            with st.container(border=True):
                st.markdown(f"### {freq} Hz")
                if best is None:
                    st.write("Sin resultado válido en esta banda.")
                else:
                    st.write(f"Menor Lₙ,final: **{best}**")
                    st.write(f"{val:.1f} dB")
    st.write(
        "La solución con menor $f_0$ **no se declara automáticamente mejor**. "
        r"La comparación principal se hace con $L_{n,\mathrm{final}}(f)$."
    )
    st.latex(r"\boxed{\mathrm{MENOR}\ f_0\neq\mathrm{AUTOMÁTICAMENTE\ MEJOR\ PROYECTO}}")

    # ================================================================
    # 7. CONSTRAINTS
    # ================================================================
    # ================================================================
    # 7. FROM ACOUSTIC RESULT TO PROJECT DECISION
    # ================================================================
    st.markdown("## 7 · De la mejor curva acústica a una solución viable")
    st.write(
        "Hasta aquí hemos comparado las alternativas principalmente mediante "
        "$L_{n,\mathrm{final}}(f)$. Ahora incorporamos las restricciones reales del proyecto."
    )
    st.latex(
        r"\boxed{\mathrm{MEJOR\ CURVA}\ L_{n,\mathrm{final}}(f)"
        r"\neq\mathrm{AUTOMÁTICAMENTE\ MEJOR\ PROYECTO}}"
    )

    st.warning(
        "NUEVA INFORMACIÓN DEL PROYECTO · carga adicional máxima: 120 kg/m² · altura disponible: 75 mm"
    )

    design_rows = []
    check_freqs = [125, 500, 1000]
    for name, p in alternatives.items():
        row = {
            "Alternativa": name,
            "Carga [kg/m²]": p["m1"],
            "Espesor didáctico [mm]": p["h"],
            "Cumple carga": p["m1"] <= 120,
            "Cumple altura": p["h"] <= 75,
        }
        for freq in check_freqs:
            idx = int(np.argmin(np.abs(np.log(bands / float(freq)))))
            val = alt_results[name]["final"][idx]
            row[f"Lₙ,final {freq} Hz [dB]"] = None if not np.isfinite(val) else round(float(val), 1)
        design_rows.append(row)

    st.dataframe(design_rows, use_container_width=True, hide_index=True)
    st.caption(
        "Los espesores indicados son datos específicos de este ejercicio y no propiedades universales de estas soluciones."
    )

    st.markdown("### Lectura profesional")
    st.write(
        "La alternativa C puede presentar una curva acústicamente favorable, pero queda fuera del ejercicio "
        "por carga y altura. A y B permanecen como soluciones viables y deben compararse mediante sus curvas "
        "$L_{n,\mathrm{final}}(f)$, no únicamente por $f_0$."
    )

    st.latex(
        r"\boxed{\mathrm{DISEÑO}=\mathrm{ACÚSTICA}+\mathrm{ESTRUCTURA}"
        r"+\mathrm{ARQUITECTURA}+\mathrm{CONSTRUCTIBILIDAD}+\mathrm{DURABILIDAD}}"
    )

    feasible = [name for name, p in alternatives.items() if p["m1"] <= 120 and p["h"] <= 75]
    if "B" in feasible:
        b_better_somewhere = False
        for idx in range(len(bands)):
            vb = alt_results["B"]["final"][idx]
            if not np.isfinite(vb):
                continue
            competitors = [
                alt_results[n]["final"][idx]
                for n in feasible
                if n != "B" and np.isfinite(alt_results[n]["final"][idx])
            ]
            if not competitors or vb <= min(competitors):
                b_better_somewhere = True
                break

        if b_better_somewhere:
            st.success(
                "Dentro de las restricciones establecidas para este ejercicio, "
                "la alternativa B representa un compromiso técnicamente favorable."
            )
        else:
            st.info(
                "B cumple las restricciones de proyecto, pero su selección final debe justificarse "
                "con la comparación espectral calculada frente a las demás alternativas viables."
            )

    # ================================================================
    # 8. PROFESSIONAL DECISION
    # ================================================================
    st.markdown("## 8 · Decisión profesional del caso")
    st.write(
        "La decisión no se toma minimizando $f_0$. Se toma integrando el resultado acústico "
        "con las restricciones del proyecto."
    )

    c1, c2, c3 = st.columns(3)
    for col, name in zip([c1, c2, c3], ["A", "B", "C"]):
        p = alternatives[name]
        with col:
            with st.container(border=True):
                st.markdown(f"### Alternativa {name}")
                st.write("**Acústica:** revisar la curva $L_{n,\mathrm{final}}(f)$ calculada.")
                st.write(f"**Carga:** {'Cumple' if p['m1'] <= 120 else 'No cumple'}")
                st.write(f"**Altura:** {'Cumple' if p['h'] <= 75 else 'No cumple'}")
                if p["m1"] <= 120 and p["h"] <= 75:
                    st.success("VIABLE EN ESTE EJERCICIO")
                else:
                    st.error("NO VIABLE EN ESTE EJERCICIO")

    st.latex(r"\boxed{\mathrm{DECIDIR}\neq\mathrm{ESCOGER\ EL\ MENOR}\ f_0}")

    # ================================================================
    # 9. EXPLORE YOUR OWN DESIGN
    # ================================================================
    st.markdown("## 🔬 9 · Diseña y predice tu piso")
    st.write(
        "Construye una solución propia modificando masa y rigidez, pero recuerda que el **resultado principal** "
        "es siempre $L_{n,\mathrm{final}}(f)$ por bandas."
    )

    o1, o2, o3 = st.columns(3)
    om1 = o1.slider("m′₁ [kg/m²]", 50, 200, 110, 5, key=f"{ns}_om1")
    om2 = o2.slider("m′₂ [kg/m²]", 150, 600, 380, 10, key=f"{ns}_om2")
    os = o3.slider("s′ [MN/m³]", 3.0, 40.0, 12.0, .5, key=f"{ns}_os")

    omodel = st.segmented_control(
        "Modelo del tratamiento",
        ["CAPA RESILIENTE CONTINUA — CREMER", "APOYOS RESILIENTES DISCRETOS — VÉR", "COMPARAR"],
        default="CAPA RESILIENTE CONTINUA — CREMER",
        key=f"{ns}_omodel",
    )

    omr, of0 = natural_frequency(om1, om2, os)
    odelta_c, of0c = _delta_continuous_curve(om1, os)
    ofinal_c = _final_curve(ln0_base, odelta_c)

    vh, vcL, vN, veta = 50.0, 3500.0, 9.0, .020
    odelta_v = _delta_discrete_curve(of0, vh, vcL, vN, veta)
    ofinal_v = _final_curve(ln0_base, odelta_v)

    st.markdown("### RESULTADO PRINCIPAL · Lₙ,final(f)")
    fig, ax = plt.subplots()
    if omodel in ("CAPA RESILIENTE CONTINUA — CREMER", "COMPARAR"):
        _plot_band_curve(ax, ofinal_c, "Cremer · Lₙ,final")
    if omodel in ("APOYOS RESILIENTES DISCRETOS — VÉR", "COMPARAR"):
        _plot_band_curve(ax, ofinal_v, "Vér · Lₙ,final")
    _format_band_axis(ax)
    ax.set_ylabel("Lₙ,final [dB]")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("### Parámetros que explican el resultado")
    r1, r2, r3 = st.columns(3)
    r1.metric("m′ᵣ", f"{omr:.1f} kg/m²")
    r2.metric("f₀ general", f"{of0:.1f} Hz")
    r3.metric("Carga estructural", "Cumple" if om1 <= 120 else "No cumple")

    oheight = st.slider(
        "Espesor total del diseño [mm] · dato específico del proyecto",
        30, 120, 65, 5, key=f"{ns}_oheight"
    )
    st.metric("Restricción arquitectónica", "Cumple" if oheight <= 75 else "No cumple")
    st.caption(
        "Para Vér se usan valores didácticos explícitos: h₁=50 mm, c_L1=3500 m/s, "
        "N=9 apoyos/m² y η₁₁=0.020. No son propiedades universales."
    )

    # ================================================================
    # 10. DESIGN MAP
    # ================================================================
    # ================================================================
    # 10. CAUSE–EFFECT SENSITIVITY
    # ================================================================
    st.markdown("## 🔬 10 · ¿Por qué cambió el resultado?")
    st.write(
        "En lugar de buscar un 'óptimo' en un mapa abstracto, aquí modificamos **una sola variable a la vez** "
        "y observamos cómo cambia la predicción final."
    )

    st.markdown("### Solución de referencia")
    ref_m1 = 110.0
    ref_m2 = 380.0
    ref_s = 12.0

    ref_mr, ref_f0 = natural_frequency(ref_m1, ref_m2, ref_s)
    ref_delta, ref_f0c = _delta_continuous_curve(ref_m1, ref_s)
    ref_final = _final_curve(ln0_base, ref_delta)

    c1, c2, c3 = st.columns(3)
    c1.metric("m′₁ referencia", f"{ref_m1:.0f} kg/m²")
    c2.metric("s′ referencia", f"{ref_s:.0f} MN/m³")
    c3.metric("f₀ general", f"{ref_f0:.1f} Hz")

    change = st.radio(
        "Selecciona una modificación",
        [
            "A · Aumentar masa superior: 110 → 150 kg/m²",
            "B · Reducir rigidez dinámica: 12 → 8 MN/m³",
            "C · Aumentar rigidez dinámica: 12 → 20 MN/m³",
        ],
        key=f"{ns}_cause_effect_choice",
    )

    if change.startswith("A"):
        mod_m1, mod_m2, mod_s = 150.0, 380.0, 12.0
        changed_parameter = "m′₁"
        interpretation = (
            "Aumentar la masa superior incrementa la masa reducida y tiende a desplazar la resonancia hacia frecuencias menores."
        )
    elif change.startswith("B"):
        mod_m1, mod_m2, mod_s = 110.0, 380.0, 8.0
        changed_parameter = "s′"
        interpretation = (
            "Reducir la rigidez dinámica desplaza la resonancia hacia frecuencias menores y modifica la mejora espectral."
        )
    else:
        mod_m1, mod_m2, mod_s = 110.0, 380.0, 20.0
        changed_parameter = "s′"
        interpretation = (
            "Aumentar la rigidez dinámica desplaza la resonancia hacia frecuencias mayores y puede reducir la separación respecto de f₀ en algunas bandas."
        )

    mod_mr, mod_f0 = natural_frequency(mod_m1, mod_m2, mod_s)
    mod_delta, mod_f0c = _delta_continuous_curve(mod_m1, mod_s)
    mod_final = _final_curve(ln0_base, mod_delta)

    st.markdown("### Qué cambió")
    a, b, c, d = st.columns(4)
    a.metric("m′₁", f"{mod_m1:.0f} kg/m²", delta=f"{mod_m1-ref_m1:+.0f}")
    b.metric("s′", f"{mod_s:.0f} MN/m³", delta=f"{mod_s-ref_s:+.0f}")
    c.metric("m′ᵣ", f"{mod_mr:.1f} kg/m²", delta=f"{mod_mr-ref_mr:+.1f}")
    d.metric("f₀", f"{mod_f0:.1f} Hz", delta=f"{mod_f0-ref_f0:+.1f} Hz")

    st.write(interpretation)
    st.latex(
        r"\boxed{\mathrm{CAMBIO\ CONSTRUCTIVO}\rightarrow f_0"
        r"\rightarrow\Delta L_n(f)\rightarrow L_{n,\mathrm{final}}(f)}"
    )

    st.markdown("### Comparación espectral")
    fig, ax = plt.subplots()
    _plot_band_curve(ax, ref_final, "Referencia · Lₙ,final")
    _plot_band_curve(ax, mod_final, "Modificada · Lₙ,final")
    _format_band_axis(ax)
    ax.set_ylabel("Lₙ,final [dB]")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("### ¿Dónde mejoró y dónde empeoró?")
    compare_rows = []
    for freq in [125, 500, 1000]:
        idx = int(np.argmin(np.abs(np.log(bands / float(freq)))))
        vr = ref_final[idx]
        vm = mod_final[idx]
        diff = np.nan
        if np.isfinite(vr) and np.isfinite(vm):
            diff = vm - vr
        if np.isfinite(diff):
            if diff < -0.05:
                reading = "Mejora"
            elif diff > 0.05:
                reading = "Empeora"
            else:
                reading = "Prácticamente igual"
        else:
            reading = "Sin comparación válida"
        compare_rows.append({
            "Banda [Hz]": freq,
            "Referencia Lₙ,final [dB]": None if not np.isfinite(vr) else round(float(vr), 1),
            "Modificada Lₙ,final [dB]": None if not np.isfinite(vm) else round(float(vm), 1),
            "Cambio [dB]": None if not np.isfinite(diff) else round(float(diff), 1),
            "Lectura": reading,
        })

    st.dataframe(compare_rows, use_container_width=True, hide_index=True)

    st.info(
        "Un cambio de parámetro no produce necesariamente el mismo efecto en todo el espectro. "
        "Por eso conviene analizar la curva completa y no una sola banda ni únicamente f₀."
    )

    _mcq(
        "cause_effect_q",
        "Si reducimos s′ y baja f₀, ¿podemos concluir automáticamente que todas las bandas tendrán menor Lₙ,final?",
        ["A. Sí", "B. No"],
        1,
        "No. Debe revisarse la respuesta espectral completa porque ΔLₙ depende de la frecuencia.",
    )

    st.markdown("## 11 · Del modelo a la obra")
    _asset("curso2_lab1_etapa7_modelo_vs_obra.webp")
    st.write(
        "Después de seleccionar una solución por su comportamiento espectral y sus restricciones, "
        "debemos comprobar que la obra conserve las condiciones del modelo ideal."
    )

    defects = st.multiselect(
        "Activar defecto",
        ["CONTACTO PERIMETRAL", "TORNILLO", "TUBERÍA", "DISCONTINUIDAD RESILIENTE"],
        key=f"{ns}_defects",
    )
    meanings = {
        "CONTACTO PERIMETRAL": "Se crea un camino mecánico paralelo entre la masa flotante y la estructura.",
        "TORNILLO": "Una fijación rígida puentea el apoyo resiliente.",
        "TUBERÍA": "La penetración o su soporte puede convertirse en un camino estructural adicional.",
        "DISCONTINUIDAD RESILIENTE": "El apoyo deja de representar la continuidad ideal asumida por el modelo.",
    }

    if defects:
        st.error(
            "ADVERTENCIA · EL SISTEMA CONSTRUIDO YA NO REPRESENTA COMPLETAMENTE "
            "EL MODELO IDEAL UTILIZADO EN LA PREDICCIÓN."
        )
        for d in defects:
            st.write(f"**{d}:** {meanings[d]}")
        st.latex(
            r"\mathrm{CAMINO\ PREVISTO:}\quad"
            r"\mathrm{sobrelosa}\rightarrow\mathrm{capa\ resiliente}\rightarrow\mathrm{losa}"
        )
        st.latex(
            r"\mathrm{CAMINO\ ADICIONAL:}\quad"
            r"\mathrm{sobrelosa}\rightarrow\mathrm{puente\ rígido}\rightarrow\mathrm{estructura}"
        )
        st.caption("No se aplica ninguna penalización inventada en dB.")
    st.markdown("## 12 · ¿La predicción y la medición serán idénticas?")
    st.write("**No necesariamente.**")
    st.write(
        "Pueden existir diferencias por simplificación del modelo, propiedades reales, amortiguamiento, "
        "condiciones de borde, ejecución, caminos secundarios e incertidumbre experimental."
    )
    st.info(
        "No se implementa el interactivo Predicción vs medición porque en el proyecto actual no existe "
        "un conjunto de datos espectrales bibliográficos validados. No se inventan puntos ni se reconstruyen curvas desde memoria."
    )
    _mcq(
        "avgerror",
        "Si el error promedio es pequeño, ¿significa que el error es pequeño en todas las bandas?",
        ["A. Sí","B. No"],
        1,
        "Un error global pequeño no garantiza coincidencia banda a banda.",
    )
    st.latex(
        r"\boxed{\mathrm{ERROR\ PROMEDIO\ PEQUEÑO}\neq"
        r"\mathrm{ERROR\ PEQUEÑO\ EN\ TODO\ EL\ ESPECTRO}}"
    )

    # ================================================================
    # 13. NO SINGLE NUMBER / BRIDGE TO LAB 2
    # ================================================================
    st.markdown("## 13 · La Etapa 7 termina en la curva espectral")
    st.latex(r"\boxed{L_{n,\mathrm{final}}(f)}")
    st.warning(
        "No calculamos $L_{n,w}$, $L'_n,w$, $L'_{nT,w}$, $C_I$, curvas de referencia "
        "ni procedimientos ISO 717-2 / ISO 12354 en esta etapa."
    )
    st.write(
        "Ahora tenemos muchos valores de $L_n$, uno para cada frecuencia. "
        "¿Cómo transformaremos después esta información espectral en descriptores comparables?"
    )
    st.success("Ese problema será desarrollado en el Laboratorio 2.")

    # ================================================================
    # 14. INTEGRATING EXERCISE
    # ================================================================
    st.markdown("## 14 · Ejercicio integrador")
    st.write(
        "Se entrega la curva R(f) del ejercicio, las propiedades de la losa y un tratamiento continuo "
        "con $m'_1=110$ kg/m², $m'_2=380$ kg/m² y $s'=12$ MN/m³."
    )
    st.dataframe(
        [{"f [Hz]":int(f),"R(f) [dB]":round(float(R),1)} for f,R in zip(bands,R_base)],
        use_container_width=True,hide_index=True,
    )

    step_key=f"{ns}_integrating_step"
    if step_key not in st.session_state:
        st.session_state[step_key]=0
    step=int(st.session_state[step_key])

    labels=[
        "PASO 1 · CALCULAR LOSA BASE",
        "PASO 2 · CALCULAR MASA REDUCIDA",
        "PASO 3 · CALCULAR f₀",
        "PASO 4 · OBTENER ΔLₙ(f)",
        "PASO 5 · OBTENER Lₙ,final(f)",
        "PASO 6 · INTERPRETAR",
    ]
    if step < len(labels):
        if st.button(labels[step],key=f"{ns}_integrating_button",use_container_width=True):
            st.session_state[step_key]=step+1
            st.rerun()

    ex_mr,ex_f0=natural_frequency(110,380,12)
    ex_delta,ex_f0c=_delta_continuous_curve(110,12)
    ex_final=_final_curve(ln0_base,ex_delta)

    if step>=1:
        st.markdown("### PASO 1 · Losa base")
        st.write("Se reutiliza la función predictiva de la Etapa 5.")
        st.dataframe(
            [{"f [Hz]":int(f),"Lₙ,₀ [dB]":round(float(v),1)} for f,v in zip(bands,ln0_base)],
            use_container_width=True,hide_index=True,
        )
    if step>=2:
        st.markdown("### PASO 2 · Masa reducida")
        st.latex(r"m'_r=\frac{110(380)}{110+380}")
        st.latex(rf"\boxed{{m'_r\approx{ex_mr:.1f}\ \mathrm{{kg/m^2}}}}")
    if step>=3:
        st.markdown("### PASO 3 · Frecuencia natural")
        st.latex(r"f_0=\frac1{2\pi}\sqrt{\frac{12\times10^6}{m'_r}}")
        st.latex(rf"\boxed{{f_0\approx{ex_f0:.1f}\ \mathrm{{Hz}}}}")
    if step>=4:
        st.markdown("### PASO 4 · Mejora ΔLₙ(f)")
        st.write("Como el tratamiento es una capa resiliente continua, se reutiliza el modelo Cremer/Vigran de la Etapa 6.")
        st.dataframe(
            [{"f [Hz]":int(f),"ΔLₙ [dB]":None if not np.isfinite(v) else round(float(v),1)}
             for f,v in zip(bands,ex_delta)],
            use_container_width=True,hide_index=True,
        )
    if step>=5:
        st.markdown("### PASO 5 · Piso terminado")
        st.latex(r"L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)")
        st.dataframe(
            [{"f [Hz]":int(f),"Lₙ,final [dB]":None if not np.isfinite(v) else round(float(v),1)}
             for f,v in zip(bands,ex_final)],
            use_container_width=True,hide_index=True,
        )
    if step>=6:
        st.markdown("### PASO 6 · Interpretación")
        st.write(
            "Compara la forma espectral de la losa base y del piso terminado, ubica la región de resonancia "
            "y señala al menos dos limitaciones: por ejemplo, hipótesis del modelo ideal y sensibilidad a ejecución/puentes."
        )
        st.success(
            "Conclusión técnica esperada: la predicción permite comparar tendencias y alternativas, "
            "pero debe interpretarse dentro del campo de validez del modelo y de la configuración constructiva."
        )

    # ================================================================
    # 15. FORMATIVE QUESTIONS
    # ================================================================
    st.markdown("## 15 · Preguntas formativas")
    _mcq("q1",r"$L_{n,\mathrm{final}}(f)=L_{n,0}(f)-\Delta L_n(f)$.",["Verdadero","Falso"],0,"Correcto.",store=True)
    _mcq("q2","ΔLₙ es necesariamente igual en todas las bandas.",["Verdadero","Falso"],1,"Es función de la frecuencia.",store=True)
    _mcq("q3","La solución con menor f₀ siempre será automáticamente la mejor solución constructiva.",["Verdadero","Falso"],1,"Debe evaluarse el espectro y las restricciones.",store=True)
    _mcq("q4","Un puente rígido puede hacer que la obra deje de representar adecuadamente el modelo ideal.",["Verdadero","Falso"],0,"Correcto.",store=True)
    _mcq("q5","Un resultado predictivo debe interpretarse dentro del campo de aplicación y las hipótesis del modelo.",["Verdadero","Falso"],0,"Correcto.",store=True)
    _mcq("q6",r"$L_{n,\mathrm{final}}(f)$ corresponde automáticamente a $L_{n,w}$.",["Verdadero","Falso"],1,"No. Aquí todavía tenemos una curva espectral.",store=True)
    _mcq("q7","El número único se obtiene promediando aritméticamente todos los niveles por bandas.",["Verdadero","Falso"],1,"No; el procedimiento normativo se estudiará después.",store=True)

    # ================================================================
    # 16. FINAL MAP / CONCLUSION
    # ================================================================
    st.markdown("## 16 · Mapa conceptual final")
    st.latex(
        r"\boxed{\mathrm{PROPIEDADES\ DE\ LA\ LOSA}\rightarrow R(f)"
        r"\rightarrow L_{n,0}(f)\rightarrow\Delta L_n(f)"
        r"\rightarrow L_{n,\mathrm{final}}(f)}"
    )
    st.write(
        "**Laboratorio 2:** medición + descriptores + curvas de referencia + números únicos."
    )

    with st.container(border=True):
        st.markdown("### Conclusión profesional")
        st.latex(
            r"\boxed{\mathrm{BUENA\ PREDICCIÓN}=\mathrm{MODELO}"
            r"+\mathrm{DATOS\ DE\ ENTRADA}+\mathrm{CAMPO\ DE\ VALIDEZ}"
            r"+\mathrm{SENSIBILIDAD}+\mathrm{INTERPRETACIÓN}}"
        )
        st.write(
            "Una predicción acústica útil no consiste únicamente en generar una curva. "
            "Debe permitir comprender qué fenómeno controla el resultado, qué parámetros son sensibles, "
            "cuáles son las hipótesis del modelo y qué condiciones constructivas deben conservarse "
            "para que la obra represente razonablemente el sistema analizado."
        )

    with st.container(border=True):
        st.markdown("### 📚 Fuente / fundamento")
        st.write(
            "Losa base $L_{n,0}(f)$: relaciones de impacto de Vér utilizadas en Etapa 5, "
            "Vér & Beranek (eds.), *Noise and Vibration Control Engineering*, 2nd ed., Wiley, 2006, "
            "cap. 11, §11.11."
        )
        st.write(
            "Capa continua: Vigran, *Building Acoustics* (2008), Ec. 8.44; "
            "Cremer, Heckl & Ungar, *Structure-Borne Sound*."
        )
        st.write(
            "Apoyos discretos: Vigran, Ecs. 8.45–8.46; Vér (1971), "
            "*Impact noise isolation of composite floors*."
        )
        st.write(
            "Masa reducida y frecuencia natural: modelo clásico masa–resorte–masa desarrollado en Etapa 6."
        )

    st.markdown("## 17 · Transición a Etapa 8")
    st.latex(
        r"\boxed{L_{n,0}(f)-\Delta L_n(f)=L_{n,\mathrm{final}}(f)}"
    )
    st.success("HEMOS COMPLETADO LA CADENA PREDICTIVA DEL RUIDO DE IMPACTO.")
    st.write(
        "En la Etapa 8 aplicaremos fuerza dinámica, resonancia, transmisibilidad, desacople y caminos estructurales "
        "al control de ruido y vibraciones de bombas, ventiladores, ductos, tuberías y otras instalaciones."
    )

    left,right=st.columns(2)
    with left:
        if st.button("← Etapa 6",key=f"s7_prev_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=6
            st.rerun()
    with right:
        if st.button("Etapa 8 →",key=f"s7_next_{class_id}",use_container_width=True):
            st.session_state[stage_selector_key]=8
            st.rerun()


def _render_course2_lab1_stage8(lab, saved):
    """Etapa 8 — Medidas de control del ruido de instalaciones y equipos."""
    import math
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # ---------- utilidades ----------
    def fe_rpm(rpm): return max(float(rpm),0.0)/60.0
    def fn_delta(delta_mm):
        dm=max(float(delta_mm)/1000.0,1e-12)
        return (1/(2*math.pi))*math.sqrt(9.81/dm)
    def tf_force(r,z):
        r=float(r); z=max(float(z),0.0)
        return math.sqrt((1+(2*z*r)**2)/max((1-r*r)**2+(2*z*r)**2,1e-12))
    def ref(txt):
        st.caption("Fuente / fundamento: Harris, *Manual de medidas acústicas y control del ruido*, 3.ª ed., "+txt+".")
    def asset(name):
        for base in ("assets","images","static"):
            q=Path(base)/name
            if q.exists():
                st.image(str(q),use_container_width=True)
                return True
        return False

    # Base de diagnóstico. No es un catálogo de productos: relaciona mecanismo, camino y familia de control.
    control_db = {
        "Bomba": {
            "vibración en losa": [("Vibración transmitida por la base","Camino estructural",["Aislamiento vibratorio","Bancada/bloque de inercia cuando corresponda","Revisar carga, rigidez y montaje"])],
            "vibración de tubería": [("Vibración transmitida por tuberías","Conexiones / estructura",["Conexiones flexibles","Soportes resilientes","Revisar penetraciones y contactos rígidos"])],
            "cavitación": [("Cavitación / condición hidráulica","Fuente",["Corregir condición hidráulica","Revisar succión, presión disponible y operación","No intentar resolverla solo con aisladores"])],
            "ruido aéreo elevado": [("Radiación de bomba/motor","Camino aéreo",["Equipo de menor emisión","Encapsulamiento/cerramiento cuando corresponda","Aislamiento y tratamiento del recinto"])],
            "ruido tonal": [("Rotación, motor o fenómeno hidráulico tonal","Fuente + aire/estructura",["Diagnóstico espectral","Balanceo/alineación/mantenimiento según causa","Control del camino dominante"])],
        },
        "Ventilador": {
            "vibración en losa": [("Vibración de motor/rotor/base","Camino estructural",["Balanceo y mantenimiento","Aislamiento vibratorio","Soportes adecuados"])],
            "ruido por ducto": [("Ruido aerodinámico propagado por ducto","Camino aéreo / ducto",["Control aerodinámico","Silenciador cuando corresponda","Revestimiento acústico cuando corresponda","Transiciones adecuadas"])],
            "ruido aéreo elevado": [("Radiación de carcasa/ventilador","Camino aéreo",["Selección de menor emisión","Cerramiento","Tratamiento del recinto"])],
            "ruido tonal": [("Paso de álabes / rotación","Fuente + ducto",["Revisar velocidad y aerodinámica","Balanceo","Control acústico del ducto"])],
        },
        "Compresor": {
            "vibración en losa": [("Fuerzas dinámicas","Camino estructural",["Aislamiento vibratorio","Bancada/bloque de inercia cuando corresponda","Revisar estabilidad y conexiones"])],
            "vibración de tubería": [("Pulsaciones / vibración de conexiones","Conexiones",["Conexiones flexibles","Control de pulsaciones según sistema","Soportes adecuados"])],
            "ruido aéreo elevado": [("Radiación de carcasa","Camino aéreo",["Encapsulamiento","Selección/mantenimiento","Tratamiento del recinto"])],
            "impactos": [("Fuerzas dinámicas/reciprocantes","Fuente + estructura",["Diagnosticar tipo de compresor","Control en fuente","Aislamiento y/o masa de inercia según diseño"])],
        },
        "Chiller / HVAC": {
            "vibración en losa": [("Compresor, bombas o ventiladores","Camino estructural",["Aislamiento vibratorio","Soportes resilientes","Revisar conexiones"])],
            "vibración de tubería": [("Transmisión por red hidráulica","Conexiones",["Conexiones flexibles","Soportes resilientes","Evitar puentes"])],
            "ruido aéreo elevado": [("Compresor/ventiladores","Camino aéreo",["Selección de baja emisión","Pantallas/cerramientos cuando corresponda","Ubicación"])],
            "ruido tonal": [("Ventiladores/compresor","Fuente + aire",["Diagnóstico de fuente","Control de ventiladores","Pantalla/cerramiento si corresponde"])],
        },
        "Unidad exterior A/A": {
            "vibración en losa": [("Compresor/ventilador transmitido por soporte","Camino estructural",["Aisladores adecuados","Soporte correctamente diseñado","Mantenimiento"])],
            "ruido aéreo elevado": [("Ventilador/compresor","Camino aéreo",["Equipo silencioso","Ubicación","Pantalla acústica cuando corresponda"])],
            "ruido tonal": [("Compresor o ventilador","Fuente + aire/estructura",["Diagnóstico tonal","Mantenimiento","Control del camino dominante"])],
        },
        "Grupo electrógeno": {
            "vibración en losa": [("Vibración del motor","Camino estructural",["Aisladores","Bancada","Control de conexiones"])],
            "ruido aéreo elevado": [("Motor/carcasa","Camino aéreo",["Encapsulamiento","Aislamiento del recinto","Control de ventilación compatible con flujo"])],
            "ruido tonal": [("Motor/elementos rotatorios","Fuente + aire/estructura",["Diagnóstico","Mantenimiento","Control del camino dominante"])],
        },
        "Ascensor": {
            "vibración en losa": [("Máquina de tracción / guías","Camino estructural",["Aislamiento de maquinaria","Desacoplamiento estructural","Soportes resilientes"])],
            "impactos": [("Puertas, maniobras o contactos","Fuente + estructura",["Control de impactos","Mantenimiento","Desacoplamiento"])],
            "ruido aéreo elevado": [("Maquinaria / recinto","Camino aéreo",["Diseño del recinto de maquinaria","Aislamiento","Separación de recintos sensibles"])],
        },
        "Sistema de tuberías": {
            "vibración de tubería": [("Flujo, equipos conectados o contactos","Conexiones / estructura",["Diseño hidráulico adecuado","Soportes resilientes","Conexiones flexibles","Penetraciones desacopladas"])],
            "impactos": [("Golpe de ariete / válvulas","Fuente + estructura",["Control hidráulico del golpe","Revisar válvulas y operación","Soportes y desacoplamiento"])],
            "ruido aéreo elevado": [("Radiación de tubería","Camino aéreo",["Control en fuente/flujo","Aislamiento de tubería cuando corresponda","Diseño de shaft"])],
        },
    }

    st.markdown("## Etapa 8 — Medidas de control del ruido de instalaciones y equipos")
    st.write("La pregunta profesional de esta etapa es: **tengo una instalación que genera ruido en un edificio, ¿qué conjunto de medidas debo evaluar?**")
    st.latex(r"\text{EQUIPO / INSTALACIÓN}\rightarrow\text{MECANISMO}\rightarrow\text{CAMINO}\rightarrow\text{MEDIDA}\rightarrow\text{COMBINACIÓN DE CONTROLES}")
    st.info("**NO SE SELECCIONA UNA MEDIDA DE CONTROL SIN IDENTIFICAR PRIMERO EL PROBLEMA.**")
    asset("curso2_lab1_etapa8_sala_instalaciones.webp")

    st.markdown("### 1 · ¿Dónde podemos actuar?")
    zone=st.radio("Selecciona una zona del sistema FUENTE → CAMINO → RECEPTOR",["Fuente","Camino estructural","Camino aéreo","Conexiones","Ubicación / configuración"],horizontal=True,key="e8_zone")
    zones={
        "Fuente":["Seleccionar equipos de menor emisión","Reducir velocidad cuando el sistema lo permita","Balancear elementos rotatorios","Alinear motor y equipo","Mantenimiento","Corregir piezas sueltas","Evitar cavitación","Reducir turbulencia e impactos","Modificar condiciones de operación"],
        "Camino estructural":["Aisladores elastoméricos","Resortes","Bancadas/bloques de inercia","Soportes resilientes","Desacoplamiento","Evitar puentes rígidos"],
        "Camino aéreo":["Encapsulamientos/cerramientos","Barreras/pantallas cuando corresponda","Silenciadores","Revestimientos acústicos","Tratamiento de ductos","Aumentar aislamiento del recinto"],
        "Conexiones":["Conectores flexibles de tuberías","Soportes resilientes","Conectores flexibles de ductos","Pasos de instalaciones desacoplados"],
        "Ubicación / configuración":["Alejar equipos de recintos sensibles","Evitar instalación sobre dormitorios cuando sea posible","Usar recintos técnicos","Evitar apoyos desfavorables","Resolver ubicación durante el diseño"],
    }
    st.markdown("**Medidas a evaluar:**\n\n- "+"\n- ".join(zones[zone]))
    st.latex(r"\text{CONTROL}=\text{FUENTE}+\text{ESTRUCTURA}+\text{AIRE}+\text{CONEXIONES}+\text{RECINTO/UBICACIÓN}")

    st.markdown("### 2 · Diagnóstico antes de la solución")
    d1,d2=st.columns(2)
    with d1:
        st.checkbox("¿Existe vibración?",key="e8_diag_v")
        st.checkbox("¿Existe ruido aéreo?",key="e8_diag_a")
        st.checkbox("¿Existen tuberías?",key="e8_diag_p")
        st.checkbox("¿Existen ductos?",key="e8_diag_d")
        st.checkbox("¿Existen conexiones rígidas?",key="e8_diag_r")
    with d2:
        st.checkbox("¿Existe flujo de aire o agua?",key="e8_diag_f")
        st.checkbox("¿Cavitación, turbulencia o pulsación?",key="e8_diag_c")
        st.selectbox("Receptor sensible",["Dormitorio","Vivienda vecina","Oficina","Sala de clases","Hospital/recinto sensible","Otro"],key="e8_receiver")
    st.write("El diagnóstico debe separar **qué genera el ruido**, **por dónde se transmite** y **qué receptor resulta afectado**.")

    st.markdown("### 3 · Bombas de agua — múltiples mecanismos")
    asset("curso2_lab1_etapa8_bomba_problemas.webp")
    st.code("""BOMBA
├── vibración del conjunto
├── desequilibrio / desalineación
├── fuerzas hidráulicas
├── turbulencia / cavitación
├── pulsaciones
├── vibración de tuberías
└── radiación acústica de carcasa""",language=None)
    pump_problem=st.selectbox("Problema de la bomba",["Vibración por base","Vibración por tuberías","Cavitación","Desequilibrio / desalineación","Ruido aéreo bomba/motor"],key="e8_pump_problem")
    pump_controls={
        "Vibración por base":"Aislamiento vibratorio + posible bancada/bloque de inercia + rigidez/deflexión y distribución de cargas.",
        "Vibración por tuberías":"Conexiones flexibles + soportes resilientes + revisión de abrazaderas, penetraciones y contactos.",
        "Cavitación":"**Prioridad: corregir la fuente / condición hidráulica.** No intentar resolverla colocando solamente resortes.",
        "Desequilibrio / desalineación":"Balanceo + alineación + mantenimiento + corrección en la fuente.",
        "Ruido aéreo bomba/motor":"Equipo de menor emisión + cerramiento/encapsulamiento cuando corresponda + aislamiento/tratamiento del recinto.",
    }
    st.success(pump_controls[pump_problem])

    st.markdown("### 4 · Interactivo — ¿Qué le pasa a esta bomba?")
    probs=st.multiselect("Activa problemas",["Desequilibrio","Cavitación","Apoyo rígido","Tubería rígida","Abrazaderas rígidas","Ruido aéreo de motor","Recinto técnico reverberante"],key="e8_pump_multi")
    mapping={
        "Desequilibrio":("FUENTE",["Balanceo","Alineación/mantenimiento"]),
        "Cavitación":("FUENTE / HIDRÁULICA",["Corregir condición hidráulica","Revisar operación y succión"]),
        "Apoyo rígido":("CAMINO ESTRUCTURAL",["Aislamiento vibratorio","Revisar bancada/montaje"]),
        "Tubería rígida":("CONEXIONES",["Conexión flexible","Revisar trazado y penetraciones"]),
        "Abrazaderas rígidas":("CONEXIONES / ESTRUCTURA",["Soportes resilientes","Evitar puentes"]),
        "Ruido aéreo de motor":("CAMINO AÉREO",["Encapsulamiento/cerramiento","Aislamiento del recinto"]),
        "Recinto técnico reverberante":("RECINTO",["Tratamiento absorbente compatible con el recinto"]),
    }
    for pr in probs:
        area,meas=mapping[pr]; st.write(f"**{pr} → {area}:** "+", ".join(meas))

    st.markdown("### 5 · Ventiladores")
    asset("curso2_lab1_etapa8_ventilador.webp")
    st.write("Revisar separadamente desequilibrio, motor, carcasa, bancada, ductos, ruido aerodinámico, turbulencia, paso de álabes y radiación por ductos.")
    vent_case=st.radio("Ventilador: selecciona el fenómeno",["A. Vibración transmitida a la estructura","B. Ruido propagado por el ducto"],key="e8_vent_case")
    if vent_case.startswith("A"):
        st.success("Control principal del camino: balanceo/mantenimiento + aislamiento mecánico + soportes/conexiones adecuados.")
    else:
        st.success("Control principal del camino: aerodinámica del sistema + silenciador/revestimiento cuando corresponda + geometría y velocidad del ducto.")
    st.warning("El mismo tratamiento NO resuelve necesariamente ambos fenómenos.")

    st.markdown("### 6 · Compresores")
    asset("curso2_lab1_etapa8_compresor.webp")
    comp=st.radio("Tipo conceptual",["Rotativo","Reciprocante"],horizontal=True,key="e8_comp")
    if comp=="Rotativo":
        st.write("Evaluar rotación, vibración, ruido aéreo, conexiones, pulsaciones y condiciones de operación.")
    else:
        st.write("Además de ruido aéreo y conexiones, las fuerzas dinámicas y pulsaciones pueden ser especialmente relevantes; no debe modelarse como equivalente a un rotativo.")
    st.write("Medidas posibles: aislamiento vibratorio, masa/bancada cuando corresponda, conexiones flexibles, control de pulsaciones, encapsulamiento, mantenimiento y ubicación.")

    st.markdown("### 7 · Chillers y equipos HVAC")
    asset("curso2_lab1_etapa8_chiller.webp")
    st.write("Un chiller o unidad HVAC puede combinar compresor, ventiladores, bombas, tuberías, estructura y radiación aérea.")
    st.markdown("- **Estructura:** aislamiento vibratorio y soportes.\n- **Tuberías:** conexiones flexibles y soportes resilientes.\n- **Aire:** selección de baja emisión, pantallas/cerramientos cuando correspondan.\n- **Diseño:** ubicación y relación con receptores sensibles.")

    st.markdown("### 8 · Unidades exteriores de aire acondicionado")
    st.write("Separar compresor, ventilador, vibración de carcasa, transmisión por soportes, ruido aéreo y ubicación.")
    st.info("Una pantalla acústica no necesariamente controla vibración estructural. Un aislador no necesariamente controla el ruido aéreo del ventilador.")

    st.markdown("### 9 · Ascensores")
    asset("curso2_lab1_etapa8_ascensor.webp")
    st.write("Fuentes posibles: máquina de tracción, motor, poleas, guías, fricción, puertas, maniobras e impactos.")
    st.write("Medidas conceptuales: aislamiento de maquinaria, desacoplamiento estructural, soportes resilientes, control de impactos, mantenimiento, diseño del recinto y separación de recintos sensibles.")
    st.caption("No se asignan reducciones inventadas en dB.")

    st.markdown("### 10 · Grupos electrógenos — un equipo, varias familias de control")
    asset("curso2_lab1_etapa8_grupo_electrogeno.webp")
    gen=pd.DataFrame([
        ["Vibración del motor","Estructura","Aisladores / bancada"],
        ["Escape","Aire","Silenciador apropiado para el sistema"],
        ["Admisión / ventilación","Aire / flujo","Control acústico compatible con caudal y pérdidas"],
        ["Carcasa / motor","Aire","Encapsulamiento / aislamiento"],
        ["Ubicación","Configuración","Separación de receptores"],
    ],columns=["Problema","Camino","Familia de medida"])
    st.dataframe(gen,use_container_width=True)

    st.markdown("### 11 · Tuberías")
    asset("curso2_lab1_etapa8_tuberias.webp")
    st.write("Analizar vibración desde equipos, turbulencia, cambios bruscos, válvulas, presión, golpes, contactos estructurales y soportes.")
    st.markdown("- conexiones flexibles;\n- soportes resilientes;\n- diseño hidráulico adecuado;\n- velocidades apropiadas;\n- control de golpes;\n- penetraciones desacopladas;\n- evitar puentes estructurales.")

    st.markdown("### 12 · Ductos: no confundir aire con vibración mecánica")
    duct=st.radio("Fenómeno",["Ruido que viaja por el ducto","Vibración mecánica del ducto"],horizontal=True,key="e8_duct")
    if duct.startswith("Ruido"):
        st.success("Evaluar silenciadores, revestimiento acústico cuando corresponda, velocidad, transiciones y reducción de turbulencia.")
    else:
        st.success("Evaluar conectores flexibles, soportes resilientes y desacoplamiento respecto del ventilador/estructura.")

    st.markdown("### 13 · Ruido de fontanería")
    st.write("Descargas, válvulas, tuberías, bombas, golpes de ariete y contactos estructurales pueden coexistir.")
    st.write("Medidas: control en fuente, velocidades adecuadas, fijaciones resilientes, desacoplamiento, aislamiento de tuberías cuando corresponda, diseño de shafts y prevención de contactos rígidos.")

    st.markdown("### 14 · Selección del aislamiento antivibratorio")
    st.write(
        "Un antivibratorio no se selecciona únicamente por el peso del equipo ni por decidir entre "
        "“goma” o “resorte”. La selección parte de la excitación del equipo, continúa con la frecuencia "
        "natural y la deflexión que necesitamos, y termina verificando la carga real que recibe cada apoyo."
    )
    st.latex(r"\boxed{\mathrm{EQUIPO}\rightarrow f_e\rightarrow f_n\rightarrow \delta\rightarrow \mathrm{CARGA\ POR\ APOYO}\rightarrow \mathrm{AISLADOR}\rightarrow \mathrm{VERIFICACI\acute{O}N}}")

    st.markdown("#### Paso 1 · Identifica la frecuencia perturbadora")
    st.write("Para un equipo rotatorio, si en este ejercicio consideramos como excitación dominante la componente 1×RPM:")
    st.latex(r"f_e=\frac{\mathrm{RPM}}{60}")
    st.info(
        "Las RPM no siempre describen toda la excitación real. Pueden existir frecuencia de paso de álabes o palas, "
        "armónicos, pulsaciones, componentes electromagnéticas u otras excitaciones. En un proyecto real debe "
        "identificarse la frecuencia perturbadora relevante."
    )

    st.markdown("#### Paso 2 · Separa la frecuencia natural de la excitación")
    st.latex(r"f_n=\frac{1}{2\pi}\sqrt{\frac{k}{m}}")
    st.latex(r"r=\frac{f_e}{f_n}")
    st.write(
        "Si la frecuencia natural queda próxima a la excitación, el sistema puede trabajar cerca de resonancia. "
        "Por eso el objetivo no es simplemente interponer un material flexible, sino obtener una rigidez bajo carga "
        "que sitúe la frecuencia natural suficientemente alejada de la excitación."
    )
    st.latex(r"T_F=\sqrt{\frac{1+(2\zeta r)^2}{(1-r^2)^2+(2\zeta r)^2}}")
    st.caption("T_F es la transmisibilidad de fuerza del modelo idealizado; no es directamente una reducción de nivel sonoro en dB.")

    st.markdown("#### Paso 3 · Traduce la frecuencia natural a una deflexión")
    st.latex(r"\delta=\frac{mg}{k}")
    st.latex(r"f_n=\frac{1}{2\pi}\sqrt{\frac{g}{\delta}}")
    st.write(
        "Esta relación crea el puente con un catálogo comercial: una frecuencia natural objetivo implica una "
        "determinada deflexión estática. En general, una mayor deflexión corresponde a una frecuencia natural menor."
    )
    st.latex(r"\boxed{\delta\uparrow\quad\Rightarrow\quad f_n\downarrow}")

    st.markdown("#### Paso 4 · Comprueba la carga por apoyo")
    st.write("Como primera aproximación, si la carga se distribuye uniformemente entre N apoyos:")
    st.latex(r"F_{\mathrm{apoyo}}\approx\frac{Mg}{N}")
    st.warning(
        "La distribución uniforme es una hipótesis del ejercicio. En equipos reales las reacciones pueden ser diferentes "
        "por la posición del centro de gravedad, la bancada y la distribución interna de masas. La selección final debe "
        "realizarse con la carga real de cada apoyo."
    )

    st.markdown("#### Interactivo · Del equipo al requerimiento del aislador")
    ca,cb,cc=st.columns(3)
    with ca:
        rpm=st.slider("Velocidad [RPM]",300,3600,1500,50,key="e8_iso_rpm")
        mass=st.slider("Masa total del equipo [kg]",200,4000,1600,50,key="e8_iso_mass")
    with cb:
        supports=st.slider("Número de apoyos",2,8,4,1,key="e8_iso_supports")
        delta=st.slider("Deflexión estática del aislador [mm]",5.0,105.0,50.8,1.0,key="e8_iso_delta")
    with cc:
        z=st.slider("Razón de amortiguamiento ζ",.01,.30,.08,.01,key="e8_iso_z")

    fe=fe_rpm(rpm)
    fn=fn_delta(delta)
    r=fe/max(fn,1e-9)
    tf=tf_force(r,z)
    kg_support=mass/supports
    force_support=kg_support*9.81
    isolation=max(0.0,(1.0-tf)*100.0) if tf < 1 else 0.0

    c=st.columns(6)
    c[0].metric("fₑ",f"{fe:.2f} Hz")
    c[1].metric("fₙ",f"{fn:.2f} Hz")
    c[2].metric("r",f"{r:.2f}")
    c[3].metric("T_F",f"{tf:.3f}")
    c[4].metric("Carga/apoyo",f"{kg_support:.0f} kg")
    c[5].metric("F/apoyo",f"{force_support:.0f} N")
    if tf < 1:
        st.success(f"En el modelo idealizado, T_F < 1. La reducción de fuerza transmitida asociada es aproximadamente {isolation:.1f} %. Esto no equivale directamente a una reducción acústica en dB.")
    else:
        st.error("Con estos parámetros no existe aislamiento de fuerza en el modelo idealizado (T_F ≥ 1). Revisa la proximidad a la resonancia.")

    rr=np.linspace(.05,max(6.0,min(20.0,r*1.15)),500)
    tt=[tf_force(x,z) for x in rr]
    fig,ax=plt.subplots()
    ax.plot(rr,tt,label="Transmisibilidad")
    ax.axhline(1,ls="--")
    ax.axvline(1,ls="--")
    ax.axvline(math.sqrt(2),ls="--")
    ax.scatter([r],[tf],zorder=5)
    ax.set_xlabel("r = fₑ / fₙ")
    ax.set_ylabel("T_F")
    ax.set_ylim(0,min(8,max(3,float(np.percentile(tt,95)))))
    ax.grid(True,alpha=.2)
    st.pyplot(fig,use_container_width=True)
    plt.close(fig)

    st.markdown("#### Paso 5 · ¿Elastómero o resorte?")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**AISLADOR ELASTOMÉRICO**")
        st.write(
            "Puede ser apropiado cuando la deflexión requerida es relativamente pequeña y sus propiedades bajo la "
            "carga de operación permiten alcanzar la frecuencia natural buscada. Es compacto y aporta amortiguamiento, "
            "pero debe verificarse con datos dinámicos y carga–deflexión del fabricante."
        )
    with c2:
        st.markdown("**AISLADOR DE RESORTE**")
        st.write(
            "Permite obtener deflexiones estáticas mayores y frecuencias naturales menores. Puede resultar conveniente "
            "cuando se necesita una separación importante entre fₑ y fₙ. Deben revisarse estabilidad, movimientos, "
            "conexiones y, cuando corresponda, requisitos de restricción sísmica."
        )
    st.latex(r"\boxed{\mathrm{TIPO\ DE\ AISLADOR}\neq\mathrm{SELECCI\acute{O}N\ FINAL}}")
    st.write(
        "Después de elegir una familia todavía debemos encontrar un modelo cuya carga de operación y deflexión sean "
        "compatibles con el apoyo que estamos diseñando."
    )

    st.markdown("### 15 · Ejercicio profesional — selecciona un antivibratorio de catálogo")
    st.write(
        "Trabajaremos con una bomba centrífuga didáctica de 1600 kg, 1500 RPM y cuatro apoyos. "
        "Para este ejercicio se adopta 1×RPM como excitación dominante y distribución uniforme de carga."
    )
    ex_mass,ex_rpm,ex_n=1600.0,1500.0,4
    ex_fe=ex_rpm/60.0
    ex_kg=ex_mass/ex_n
    ex_lb=ex_kg*2.2046226218
    st.latex(r"f_e=\frac{1500}{60}=25\ \mathrm{Hz}")
    st.latex(r"m_{\mathrm{apoyo}}=\frac{1600}{4}=400\ \mathrm{kg}\approx 882\ \mathrm{lb}")

    st.write(
        "Usaremos como documento comercial real la familia **Kinetics FDS — Free Standing Spring Isolators**. "
        "El fabricante indica aplicaciones que incluyen bombas montadas sobre base, compresores, equipos de climatización "
        "y ventiladores, con deflexiones estáticas disponibles hasta 4 in (102 mm)."
    )
    st.caption("Los datos de modelos mostrados a continuación se toman de la ficha oficial Kinetics FDS 4-inch Deflection Isolator. No son valores inventados para el ejercicio.")

    fds_models=[
        ("FDS 4-100",100,4.00),
        ("FDS 4-250",250,4.00),
        ("FDS 4-500",500,4.00),
        ("FDS 4-750",750,4.00),
        ("FDS 4-1000",1000,4.00),
        ("FDS 4-1250",1250,4.00),
        ("FDS 4-1600",1600,4.00),
    ]
    catalog=pd.DataFrame(fds_models,columns=["Modelo","Carga nominal [lb]","Deflexión nominal [in]"])
    st.dataframe(catalog,use_container_width=True,hide_index=True)

    model_name=st.selectbox("Selecciona un modelo del catálogo", [x[0] for x in fds_models], index=4, key="e8_catalog_model")
    selected=next(x for x in fds_models if x[0]==model_name)
    rated_lb=float(selected[1])
    rated_def_in=float(selected[2])

    # Para un resorte lineal ideal, la deflexión a carga parcial escala con F/k.
    # Es una estimación didáctica, no sustituye la curva/dato de operación del fabricante.
    op_def_in=rated_def_in*(ex_lb/rated_lb)
    op_def_mm=op_def_in*25.4
    op_fn=fn_delta(max(op_def_mm,1e-9))
    op_r=ex_fe/max(op_fn,1e-9)
    op_tf=tf_force(op_r,0.08)
    load_ok=ex_lb <= rated_lb

    d1,d2,d3,d4=st.columns(4)
    d1.metric("Carga requerida",f"{ex_lb:.0f} lb/apoyo")
    d2.metric("Carga nominal catálogo",f"{rated_lb:.0f} lb")
    d3.metric("δ estimada a carga",f"{op_def_mm:.1f} mm")
    d4.metric("fₙ estimada",f"{op_fn:.2f} Hz")

    st.write(
        "Para poder comparar candidatos dentro del ejercicio, se supone comportamiento lineal del resorte y se estima "
        "la deflexión a la carga de operación mediante proporcionalidad carga–deflexión:"
    )
    st.latex(r"\delta_{\mathrm{op}}\approx\delta_{\mathrm{nom}}\frac{F_{\mathrm{op}}}{F_{\mathrm{nom}}}")
    st.caption("Esta proporcionalidad es una idealización didáctica. La selección de proyecto debe verificarse con los datos de operación/carga–deflexión del fabricante.")

    if not load_ok:
        st.error("NO COMPATIBLE POR CARGA: la carga estimada por apoyo supera la carga nominal publicada para este modelo.")
    else:
        st.success("COMPATIBLE POR CAPACIDAD NOMINAL dentro de las hipótesis del ejercicio.")
        st.write(f"Con la deflexión de operación idealizada: **r ≈ {op_r:.2f}** y **T_F ≈ {op_tf:.3f}**.")
        if rated_lb > ex_lb*1.8:
            st.warning(
                "Aunque soporta la carga, este resorte está trabajando bastante por debajo de su carga nominal. "
                "Eso reduce su deflexión de operación y eleva fₙ. Un aislador con mayor capacidad no es automáticamente una mejor selección."
            )

    st.markdown("#### La selección todavía no termina")
    st.write(
        "Una vez encontrada una combinación compatible de carga y comportamiento dinámico, deben revisarse la distribución "
        "real de cargas, estabilidad, movimientos de arranque/parada, conexiones flexibles, soportación de tuberías, ambiente, "
        "anclajes y documentación específica del fabricante."
    )
    st.warning(
        "Además, la ficha FDS indica que estos aisladores libres no proporcionan por sí solos restricción sísmica o de viento. "
        "Cuando el proyecto requiera restricción frente a acciones externas debe seleccionarse y diseñarse una solución apropiada para esa condición."
    )

    st.markdown("#### Nueva información del caso")
    st.info("La bomba está conectada directamente a tuberías rígidas.")
    bridge=st.radio(
        "¿Una buena selección de los resortes garantiza por sí sola que el sistema completo quede correctamente aislado?",
        ["Selecciona una respuesta","Sí","No"],key="e8_catalog_bridge"
    )
    if bridge=="No":
        st.success("Correcto. La tubería rígida puede crear un camino mecánico paralelo y reducir la efectividad del desacoplamiento.")
        st.latex(r"\boxed{\mathrm{BUEN\ AISLADOR}\neq\mathrm{BUEN\ SISTEMA\ DE\ AISLAMIENTO}}")
        st.write("También deben evaluarse conexiones flexibles, soportación resiliente y cualquier otro puente estructural.")
    elif bridge=="Sí":
        st.error("Revisa el camino completo: una conexión rígida puede puentear el aislamiento de la base.")

    st.markdown("### 15.1 · Relaciona el problema con la medida")
    st.write("En lugar de memorizar una matriz, relaciona cada mecanismo con la medida que primero corresponde evaluar.")
    pairs={
        "Cavitación en una bomba":"Corregir la condición hidráulica",
        "Vibración transmitida por la base":"Aislamiento vibratorio",
        "Vibración transmitida por tubería":"Conexión flexible + soportes resilientes",
        "Ruido aerodinámico de un ventilador":"Control aerodinámico / silenciador cuando corresponda",
        "Escape de un grupo electrógeno":"Silenciador de escape",
        "Ruido aéreo dominante de un compresor":"Encapsulamiento",
    }
    options=["Selecciona..."]+list(pairs.values())
    score=0
    for idx,(problem,answer) in enumerate(pairs.items()):
        ans=st.selectbox(problem,options,key=f"e8_pair_{idx}")
        if ans==answer:
            st.success("✓ Correspondencia correcta.")
            score+=1
        elif ans!="Selecciona...":
            st.warning("Revisa primero cuál es el mecanismo y por qué camino se transmite.")
    if score==len(pairs):
        st.success("Has relacionado correctamente todos los mecanismos con una medida coherente.")

    st.markdown("### 16 · Interactivo principal — DISEÑA LA SOLUCIÓN")
    eq=st.selectbox("Tipo de equipo",list(control_db.keys()),key="e8_design_eq")
    symptoms=st.multiselect("Síntomas observados",["vibración en losa","ruido en recinto vecino","ruido por ducto","vibración de tubería","ruido tonal","cavitación","impactos","ruido aéreo elevado"],key="e8_design_sym")
    # translate generic neighbour symptom to likely air/structure; deliberately not overdiagnose
    found=[]
    for s in symptoms:
        if s in control_db[eq]: found += control_db[eq][s]
        elif s=="ruido en recinto vecino":
            found.append(("Ruido recibido: mecanismo todavía no identificado","Requiere diagnóstico",["Comprobar componente aéreo y estructural antes de seleccionar la medida"]))
        elif s=="ruido por ducto" and eq!="Ventilador":
            found.append(("Posible propagación por ducto","Camino aéreo",["Verificar conexión al sistema de ventilación y controlar el ducto si corresponde"]))
    if found:
        st.markdown("**Posibles mecanismos y caminos:**")
        for mech,path,meas in found:
            st.write(f"- **{mech}** → {path}: "+", ".join(meas))
    else:
        st.info("Selecciona uno o más síntomas. La app no asignará automáticamente una solución sin un mecanismo plausible.")
    all_measures=sorted({m for db in control_db.values() for arr in db.values() for _,_,ms in arr for m in ms})
    chosen=st.multiselect("¿Qué medidas evaluarías?",all_measures,key="e8_design_measures")
    if found and chosen:
        valid={m for _,_,ms in found for m in ms}
        hits=set(chosen)&valid
        if hits: st.success("Medidas relacionadas con los mecanismos identificados: "+", ".join(sorted(hits)))
        misses=set(chosen)-valid
        if misses: st.warning("Estas medidas no están directamente vinculadas al diagnóstico simplificado actual: "+", ".join(sorted(misses))+". Revisa si existe otro mecanismo que las justifique.")
    st.caption("Puede haber varias respuestas correctas. El objetivo es comprobar correspondencia mecanismo–camino–medida.")

    st.markdown("### 17 · Arma la solución completa — sala de bombas bajo departamentos")
    st.write("Problemas detectados: vibración por base + tuberías rígidas + cavitación + recinto técnico reverberante.")
    combo=st.multiselect("Selecciona una combinación",["Resorte","Elastómero","Conexión flexible","Soporte resiliente","Corregir condición hidráulica","Absorción en recinto","Barrera exterior","Silenciador de ducto"],key="e8_combo")
    groups={
        "CONTROL EN FUENTE":{"Corregir condición hidráulica"},
        "CONTROL ESTRUCTURAL":{"Resorte","Elastómero"},
        "CONTROL DE CONEXIONES":{"Conexión flexible","Soporte resiliente"},
        "CONTROL DEL RECINTO":{"Absorción en recinto"},
    }
    for name,opts in groups.items():
        hit=set(combo)&opts
        if hit: st.success(name+": "+", ".join(sorted(hit)))
        else: st.warning(name+": falta una medida relacionada con el problema declarado.")
    if "Barrera exterior" in combo or "Silenciador de ducto" in combo:
        st.info("Barrera exterior/silenciador de ducto no corresponden directamente a los cuatro problemas declarados en este caso.")
    asset("curso2_lab1_etapa8_solucion_integral.webp")

    st.markdown("### 18 · ¿Dónde actúa esta medida?")
    measure_area={
        "Balanceo":"Fuente","Aislador":"Camino estructural","Conexión flexible":"Conexiones","Silenciador":"Camino aéreo",
        "Encapsulamiento":"Camino aéreo","Soporte resiliente":"Conexiones","Pantalla":"Camino aéreo",
        "Tratamiento absorbente":"Recinto","Corrección hidráulica":"Fuente"
    }
    mm=st.selectbox("Medida",list(measure_area),key="e8_where_m")
    aa=st.radio("Zona",["Fuente","Camino estructural","Camino aéreo","Conexiones","Recinto"],horizontal=True,key="e8_where_a")
    if aa==measure_area[mm]: st.success("Correcto para la clasificación principal de este ejercicio.")
    else: st.warning(f"En este ejercicio, {mm} se clasifica principalmente en: {measure_area[mm]}.")

    st.markdown("### 19 · Encuentra todos los caminos")
    asset("curso2_lab1_etapa8_sala_instalaciones.webp")
    paths=st.multiselect("Identifica caminos presentes en una sala técnica",["Base → losa","Tubería → soporte → estructura","Ducto → soportes / estructura","Propagación aérea","Penetraciones","Soportes/anclajes"],key="e8_paths")
    if paths:
        st.write("Para cada camino identificado debe elegirse una medida específica; **aislar la base no elimina automáticamente los demás caminos**.")

    st.markdown("### 20 · Preguntas formativas")
    qs=[
        ("Una bomba con cavitación se corrige principalmente instalando resortes.",["Verdadero","Falso"],"Falso"),
        ("Un equipo puede requerir simultáneamente control en fuente, estructura y conexiones.",["Verdadero","Falso"],"Verdadero"),
        ("Una pantalla acústica controla necesariamente vibración estructural.",["Verdadero","Falso"],"Falso"),
        ("Un aislador controla necesariamente el ruido aéreo de un ventilador.",["Verdadero","Falso"],"Falso"),
        ("El ruido por ducto y la vibración mecánica del ducto deben diagnosticarse por separado.",["Verdadero","Falso"],"Verdadero"),
        ("Un grupo electrógeno puede requerir aisladores, silenciador de escape y control de ventilación.",["Verdadero","Falso"],"Verdadero"),
        ("Las conexiones rígidas pueden puentear un aislamiento vibratorio.",["Verdadero","Falso"],"Verdadero"),
        ("La ubicación del equipo puede ser una medida de control.",["Verdadero","Falso"],"Verdadero"),
    ]
    for i,(q,op,ans) in enumerate(qs):
        v=st.radio(f"{i+1}. {q}",op,index=None,key=f"e8_form_{i}")
        if v is not None:
            st.success("Correcto.") if v==ans else st.warning("Revisa mecanismo, camino y familia de control.")

    st.markdown("### 21 · Conclusión — selecciona una estrategia, no un producto aislado")
    st.latex(r"\text{DIAGNÓSTICO}\rightarrow\text{MECANISMO}\rightarrow\text{CAMINO}\rightarrow\text{MEDIDA}")
    st.latex(r"\text{RUIDO DE INSTALACIONES}\Rightarrow\text{FUENTE}+\text{AISLAMIENTO VIBRATORIO}+\text{TUBERÍAS}+\text{DUCTOS}+\text{ENCAPSULAMIENTO}+\text{SILENCIADORES}+\text{RECINTO}+\text{UBICACIÓN}")
    st.info("**NO EXISTE UNA SOLUCIÓN UNIVERSAL.** Un antivibratorio es una herramienta dentro de una estrategia de control.")
    st.success("Al finalizar, la pregunta es: **¿cuál es el mecanismo, por dónde se transmite y qué conjunto de medidas de control debo evaluar?**")
    st.markdown("### Fuentes y bibliografía de la Etapa 8")
    st.write(
        "Las ecuaciones, criterios y estrategias de esta etapa deben interpretarse dentro del campo de aplicación "
        "de las fuentes técnicas indicadas. El ejercicio comercial utiliza datos publicados por el fabricante y "
        "no constituye una especificación de producto para un proyecto real."
    )
    st.markdown(
        "- **Harris, C. M.** — *Manual de medidas acústicas y control del ruido*: principios de control, "
        "aislamiento de vibraciones, maquinaria, HVAC, transmisión estructural y fontanería.\n"
        "- **Kinetics Noise Control — FDS Free Standing Spring Isolators**: ficha de producto y aplicaciones.\n"
        "- **Kinetics Noise Control — FDS 4-inch Deflection Isolator, Drawing S-01.20-41**: "
        "cargas nominales y deflexiones de los modelos utilizados en el ejercicio."
    )


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
        if stage == 2:
            _render_course2_lab1_stage2(lab, {})
            return
        if stage == 3:
            _render_course2_lab1_stage3(lab, {})
            return
        if stage == 4:
            _render_course2_lab1_stage4(lab, {})
            return
        if stage == 5:
            _render_course2_lab1_stage5(lab, {})
            return
        if stage == 6:
            _render_course2_lab1_stage6(lab, {})
            return
        if stage == 7:
            _render_course2_lab1_stage7(lab, {})
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
