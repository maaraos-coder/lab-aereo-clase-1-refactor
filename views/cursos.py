import streamlit.components.v1 as components

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
    st.markdown("#### Resultado del curso")
    if st.session_state.get("role")=="Alumno" and not lab2_released:
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
    client=_supabase()
    st.session_state[f"future_saved_{class_id}"]=state
    if client is None:
        return
    client.table("user_progress").upsert({
        "course_id":COURSE_ID,"class_id":class_id,
        "user_key":st.session_state.user_key,
        "role":st.session_state.get("role","Alumno"),
        "display_name":st.session_state.get("name",""),
        "state_json":state,"updated_at":_now(),
    },on_conflict="class_id,user_key").execute()

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
    """Figura SVG técnica del recorrido pisada → estructura → radiación → receptor."""
    stage=max(0,min(int(stage),4))
    orange="#ff8a2a"; cyan="#35d7ff"; panel="#0b2743"
    active=[stage>=0,stage>=1,stage>=2,stage>=3,stage>=4]
    def a(i): return "1" if active[i] else ".16"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 560" width="100%" role="img" aria-label="Sección técnica de propagación de una pisada hasta un recinto receptor">
    <defs>
      <linearGradient id="bgFoot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#051426"/><stop offset="1" stop-color="#0b2a46"/></linearGradient>
      <linearGradient id="concrete" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#777f86"/><stop offset=".45" stop-color="#4d565f"/><stop offset="1" stop-color="#2f3942"/></linearGradient>
      <linearGradient id="room" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2a38"/><stop offset="1" stop-color="#0c1722"/></linearGradient>
      <filter id="go"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <filter id="gc"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <pattern id="agg" width="42" height="30" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="2" fill="#8d969e" opacity=".35"/><circle cx="26" cy="20" r="3" fill="#222c35" opacity=".45"/><path d="M2 27 l11 -5 l8 5" fill="none" stroke="#9aa3aa" stroke-width="1" opacity=".2"/></pattern>
      <style>.t{{font-family:Inter,Arial,sans-serif;fill:#eef8ff}} .muted{{fill:#93a9bc}} .small{{font-size:16px}} .label{{font-size:18px;font-weight:700}} .title{{font-size:25px;font-weight:800}}</style>
    </defs>
    <rect width="1280" height="560" rx="22" fill="url(#bgFoot)"/>
    <text x="36" y="44" class="t title">De la pisada al receptor</text>
    <text x="36" y="72" class="t muted small">Sección técnica · excitación mecánica, propagación estructural y radiación al aire</text>
    <g opacity="{a(0)}">
      <path d="M238 106 c18 -25 30 -48 38 -72 l43 4 c2 31 2 60 -5 84 l-11 32 -76 0 c-12 0 -18 -12 -11 -22 z" fill="#1d242c" stroke="#b9c5cf" stroke-width="3"/>
      <path d="M214 151 c33 10 74 12 111 2 l16 20 -10 18 -107 0 c-31 0 -46 -27 -10 -40z" fill="#c9ced3" stroke="#e8ecef" stroke-width="3"/>
      <path d="M223 185 h114" stroke="#7b8791" stroke-width="4"/>
      <circle cx="278" cy="199" r="13" fill="{orange}" filter="url(#go)"/>
    </g>
    <rect x="70" y="200" width="865" height="18" rx="4" fill="#b6b0a6"/>
    <rect x="70" y="218" width="865" height="150" rx="5" fill="url(#concrete)" stroke="#a9b3bc" stroke-width="3"/>
    <rect x="70" y="218" width="865" height="150" fill="url(#agg)" opacity=".75"/>
    <g stroke="#1c242c" stroke-width="7" opacity=".9"><line x1="95" y1="244" x2="910" y2="244"/><line x1="95" y1="344" x2="910" y2="344"/></g>
    <g opacity="{a(1)}" filter="url(#go)"><path d="M278 201 V245" stroke="{orange}" stroke-width="8"/><path d="M278 245 v86" stroke="{orange}" stroke-width="5"/><path d="M265 315 l13 16 13 -16" fill="none" stroke="{orange}" stroke-width="5"/></g>
    <g opacity="{a(2)}" fill="none" stroke="{orange}" filter="url(#go)" stroke-width="4">
      <path d="M115 274 C180 250 210 300 275 275 S370 250 435 275 S530 300 595 275 S690 250 755 275 S850 300 915 275"/>
      <path d="M115 310 C180 286 210 336 275 311 S370 286 435 311 S530 336 595 311 S690 286 755 311 S850 336 915 311" opacity=".72"/>
    </g>
    <rect x="248" y="284" width="218" height="54" rx="10" fill="#0a1c2d" stroke="{orange}" stroke-width="2" opacity="{a(2)}"/>
    <text x="357" y="307" text-anchor="middle" class="t label" fill="{orange}" opacity="{a(2)}">VIBRACIÓN EN LA LOSA</text>
    <text x="357" y="327" text-anchor="middle" class="t muted small" opacity="{a(2)}">energía mecánica en el sólido</text>
    <rect x="70" y="368" width="865" height="154" fill="url(#room)" stroke="#34495a" stroke-width="2"/>
    <rect x="126" y="449" width="370" height="48" rx="8" fill="#2b3d4d"/><rect x="157" y="429" width="310" height="44" rx="12" fill="#445669"/>
    <circle cx="258" cy="445" r="16" fill="#d3b39f"/><circle cx="340" cy="445" r="16" fill="#d3b39f"/>
    <rect x="126" y="497" width="370" height="9" fill="#101820"/>
    <path d="M603 522 V399 h270 v123" fill="none" stroke="#526579" stroke-width="5"/><rect x="638" y="426" width="72" height="42" rx="5" fill="#18293a"/><circle cx="674" cy="447" r="13" fill="#c9a98f"/>
    <g opacity="{a(3)}" fill="none" stroke="{cyan}" stroke-width="5" filter="url(#gc)">
      <path d="M165 370 Q278 438 391 370"/><path d="M120 370 Q278 477 436 370"/><path d="M82 370 Q278 515 474 370"/>
    </g>
    <g opacity="{a(4)}"><circle cx="298" cy="452" r="64" fill="none" stroke="{cyan}" stroke-width="3" stroke-dasharray="8 8"/><text x="298" y="536" text-anchor="middle" class="t label" fill="{cyan}">RECEPTOR</text></g>
    <rect x="972" y="102" width="270" height="335" rx="16" fill="{panel}" stroke="#244c6a" stroke-width="2"/>
    <text x="1000" y="137" class="t label">Lectura del fenómeno</text>
    <g class="t small">
      <circle cx="1004" cy="177" r="14" fill="{orange}" opacity="{a(0)}"/><text x="1004" y="183" text-anchor="middle" font-weight="800">1</text><text x="1030" y="183">Impacto / F(t)</text>
      <circle cx="1004" cy="224" r="14" fill="{orange}" opacity="{a(1)}"/><text x="1004" y="230" text-anchor="middle" font-weight="800">2</text><text x="1030" y="230">Respuesta de la losa</text>
      <circle cx="1004" cy="271" r="14" fill="{orange}" opacity="{a(2)}"/><text x="1004" y="277" text-anchor="middle" font-weight="800">3</text><text x="1030" y="277">Propagación estructural</text>
      <circle cx="1004" cy="318" r="14" fill="{cyan}" opacity="{a(3)}"/><text x="1004" y="324" text-anchor="middle" font-weight="800">4</text><text x="1030" y="324">Radiación acústica</text>
      <circle cx="1004" cy="365" r="14" fill="{cyan}" opacity="{a(4)}"/><text x="1004" y="371" text-anchor="middle" font-weight="800">5</text><text x="1030" y="371">Receptor</text>
    </g>
    <text x="1000" y="407" class="t muted small">Naranja: energía en la estructura</text><text x="1000" y="431" class="t muted small">Cian: sonido propagándose en el aire</text>
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
    """Mini simulador SVG: permite intervenir distintos caminos de una bomba."""
    st.markdown("### 7 · Laboratorio conceptual · Controla la bomba")
    st.write(
        "Activa medidas de control y observa **qué camino cambia realmente**. "
        "Los estados son conceptuales: sirven para razonar sobre caminos de transmisión, no son una predicción numérica."
    )

    stored=saved.get("stage0_pump_lab", {}) if isinstance(saved.get("stage0_pump_lab"), dict) else {}
    defaults={
        "encierro": bool(stored.get("encierro", False)),
        "absorbente": bool(stored.get("absorbente", False)),
        "antivibratorios": bool(stored.get("antivibratorios", False)),
        "flexible": bool(stored.get("flexible", False)),
    }
    keys={name:f"{class_id}_pump_{name}" for name in defaults}
    for name,val in defaults.items():
        if keys[name] not in st.session_state:
            st.session_state[keys[name]]=val

    c1,c2,c3,c4=st.columns(4)
    with c1:
        encierro=st.toggle("Encierro acústico", key=keys["encierro"], help="Actúa principalmente sobre el ruido aéreo radiado por la máquina.")
    with c2:
        absorbente=st.toggle("Absorbente interior", key=keys["absorbente"], help="Reduce reflexiones/campo reverberante, pero no desacopla por sí solo la estructura.")
    with c3:
        antivibratorios=st.toggle("Antivibratorios", key=keys["antivibratorios"], help="Intervienen el camino bomba → base → losa.")
    with c4:
        flexible=st.toggle("Conexión flexible", key=keys["flexible"], help="Interviene el camino bomba → tubería → soportes → estructura.")

    config={
        "encierro":bool(encierro), "absorbente":bool(absorbente),
        "antivibratorios":bool(antivibratorios), "flexible":bool(flexible),
    }
    old_config={name:bool(stored.get(name, False)) for name in defaults}
    if config != old_config:
        saved["stage0_pump_lab"]={**config,"updated_at":_now()}
        saved["stage0_pump_lab_explored"]=True
        _save_future_state_impl(class_id,saved)

    components.html(_course2_lab1_stage0_pump_svg(**config), height=665, scrolling=False)


    if antivibratorios and not flexible:
        st.warning(
            "Instalaste antivibratorios y redujiste el camino por la base, pero **la tubería rígida mantiene un camino estructural paralelo**."
        )
    elif flexible and not antivibratorios:
        st.info(
            "Desacoplaste la tubería, pero la bomba todavía puede introducir vibración directamente por su base hacia la losa."
        )
    elif antivibratorios and flexible:
        st.success(
            "Estás interviniendo los dos caminos estructurales representados: base–losa y tubería–soportes. "
            "Aun así, el control del ruido aéreo debe evaluarse por separado."
        )
    else:
        st.info(
            "La instalación mantiene activos los dos caminos estructurales principales. Prueba distintas medidas y observa qué recorrido cambia."
        )

    if encierro or absorbente:
        st.caption(
            "El tratamiento acústico del recinto/encierro actúa principalmente sobre el campo sonoro aéreo; "
            "no sustituye el desacoplamiento mecánico de base y tuberías."
        )

    if st.button("↺ Quitar todas las medidas", key=f"{class_id}_pump_reset", width="stretch"):
        for key in keys.values():
            st.session_state[key]=False
        saved["stage0_pump_lab"]={"encierro":False,"absorbente":False,"antivibratorios":False,"flexible":False,"updated_at":_now()}
        saved["stage0_pump_lab_explored"]=True
        _save_future_state_impl(class_id,saved)
        st.rerun()

    st.latex(r"\boxed{\text{CONTROL EFECTIVO}=\text{CONTROL DEL CAMINO RELEVANTE}}")
    st.caption("Laboratorio conceptual · actividad formativa sin puntaje.")

def _course2_lab1_stage0_energy_interactive(class_id, saved):
    """Descubrimiento + 'Sigue la energía', persistente, táctil y sin nota."""
    sources = {
        "Pisada": {
            "title": "Pisada · impacto directo sobre la estructura",
            "chain": r"\text{PIE}\rightarrow F(t)\rightarrow\text{LOSA}\rightarrow\text{PROPAGACIÓN ESTRUCTURAL}\rightarrow\text{RADIACIÓN ACÚSTICA}\rightarrow\text{RECEPTOR}",
            "explanation": "La fuerza de impacto entra directamente a la losa. La vibración se propaga por el elemento estructural y el cielo del dormitorio inmediatamente inferior puede radiar sonido hacia la pareja receptora.",
            "focus": "Naranja: propagación mecánica por la estructura. Cian: radiación acústica desde una superficie vibrante hacia el aire del recinto receptor.",
        },
        "Bomba": {
            "title": "Bomba centrífuga · caminos por base y tuberías",
            "chain": r"\text{BOMBA}\rightarrow\begin{cases}\text{BASE}\rightarrow\text{LOSA}\rightarrow\text{ESTRUCTURA}\rightarrow\text{RADIACIÓN}\\\text{TUBERÍA}\rightarrow\text{SOPORTES}\rightarrow\text{ESTRUCTURA}\rightarrow\text{RADIACIÓN}\end{cases}",
            "explanation": "La bomba excita su base y también la tubería de impulsión. La montante y sus soportes transportan vibración hacia otros pisos; una pared, losa u otro elemento conectado puede vibrar y radiar posteriormente sonido al aire.",
            "focus": "Azul: camino mecánico asociado a bomba y tuberías. Cian: ejemplo de radiación acústica desde una superficie estructural excitada.",
        },
        "Descarga sanitaria": {
            "title": "Descarga sanitaria · tubería, fijaciones y radiación",
            "chain": r"\text{DESCARGA}\rightarrow\text{RAMAL}\rightarrow\text{BAJANTE}\rightarrow\text{ABRAZADERAS}\rightarrow\text{ESTRUCTURA}\rightarrow\text{RADIACIÓN ACÚSTICA}\rightarrow\text{RECEPTOR}",
            "explanation": "El flujo y los cambios de dirección generan fuerzas fluctuantes en la bajante. Las abrazaderas transmiten vibración a la construcción y una superficie conectada puede convertirse en una fuente sonora secundaria.",
            "focus": "Morado: camino mecánico por la instalación sanitaria. Cian: radiación acústica posterior hacia un recinto habitable.",
        },
    }

    unlocked = bool(saved.get("stage0_energy_unlocked", False))
    selected_key=f"{class_id}_stage0_energy_source"
    selected=st.session_state.get(selected_key)
    if selected not in sources:
        selected=saved.get("stage0_energy_source") if saved.get("stage0_energy_source") in sources else None

    # UNA sola zona gráfica. Antes de explorar se ve limpia; después del clic se
    # vuelve a dibujar en el MISMO lugar con el recorrido seleccionado encima.
    _course2_lab1_stage0_dynamic_image(
        "curso2_lab1_etapa0_edificio_vibroacustico.webp",
        source=selected if unlocked else None,
        caption="Observa el edificio. El color de la fuente sigue el camino mecánico; las ondas cian representan la radiación acústica hacia el aire.",
    )

    if not unlocked:
        st.markdown("#### 🔎 Observa el edificio")
        st.write("**¿Cuáles de los siguientes elementos identificarías inicialmente como fuentes relevantes para analizar transmisión estructural?**")
        choices = [
            "Pisadas de una persona",
            "Bomba centrífuga",
            "Descarga sanitaria",
            "Conversación de la pareja",
            "Refrigerador",
            "Iluminación del departamento",
        ]
        previous = saved.get("stage0_source_identification", [])
        if not isinstance(previous, list): previous=[]
        selected_choices=[]
        for i, option in enumerate(choices):
            k=f"{class_id}_stage0_identify_{i}"
            if k not in st.session_state:
                st.session_state[k]=option in previous
            if st.checkbox(option, key=k): selected_choices.append(option)
        if st.button("Comprobar identificación", type="primary", key=f"{class_id}_stage0_identify_check", width="stretch"):
            saved["stage0_source_identification"] = selected_choices
            expected={"Pisadas de una persona","Bomba centrífuga","Descarga sanitaria"}
            chosen=set(selected_choices)
            saved["stage0_source_identification_correct"] = chosen == expected
            saved["stage0_energy_unlocked"] = True
            saved["stage0_source_identification_checked_at"] = _now()
            _save_future_state_impl(class_id, saved)
            st.rerun()
        st.caption("Actividad de observación · sin puntaje. Al comprobar podrás explorar los caminos de energía.")
        return 0, len(sources)

    if saved.get("stage0_source_identification_correct"):
        st.success("Muy bien. Identificaste las tres fuentes representadas. Ahora sigue la energía desde cada fuente hasta la estructura, la radiación y el receptor.")
    else:
        st.info("En este render se analizan tres fuentes: pisada, bomba centrífuga y descarga sanitaria. Explora sus caminos para comprobar cómo pueden introducir energía mecánica en el edificio.")

    # Permite repetir la observación sin borrar el progreso de exploración ni la nota
    # (esta actividad es formativa). Es útil también para que el docente pueda
    # volver a mostrar el descubrimiento inicial durante una clase.
    if st.button(
        "↺ Volver a identificar las fuentes",
        key=f"{class_id}_stage0_reidentify",
        width="stretch",
        help="Reabre la actividad de observación inicial. No elimina las fuentes ya exploradas.",
    ):
        saved["stage0_source_identification_previous"] = saved.get("stage0_source_identification", [])
        saved["stage0_source_identification"] = []
        saved["stage0_source_identification_correct"] = False
        saved["stage0_energy_unlocked"] = False
        saved["stage0_source_identification_checked_at"] = None
        saved["stage0_energy_source"] = None
        st.session_state.pop(selected_key, None)
        for i in range(6):
            st.session_state.pop(f"{class_id}_stage0_identify_{i}", None)
        _save_future_state_impl(class_id, saved)
        st.rerun()

    st.markdown("#### Sigue la energía")
    st.write("Selecciona una fuente. **La imagen de arriba es la misma**: al elegir una opción se superpone su camino de propagación y su posible radiación acústica.")

    explored=saved.get("stage0_energy_explored", [])
    if not isinstance(explored,list): explored=[]
    explored=[x for x in explored if x in sources]

    cols=st.columns(3)
    for col, source in zip(cols, sources):
        with col:
            label=f"{'✓ ' if source in explored else ''}{source}"
            if st.button(label,key=f"stage0_energy_btn_{class_id}_{source}",type="primary" if selected==source else "secondary",width="stretch"):
                st.session_state[selected_key]=source
                saved["stage0_energy_source"]=source
                if source not in explored: explored.append(source)
                saved["stage0_energy_explored"]=explored
                saved["stage0_energy_updated_at"]=_now()
                _save_future_state_impl(class_id,saved)
                st.rerun()

    selected=st.session_state.get(selected_key, selected)
    if selected in sources:
        data=sources[selected]
        with st.container(border=True):
            st.markdown(f"#### {data['title']}")
            st.latex(data["chain"])
            st.write(data["explanation"])
            st.info(data["focus"])

    st.progress(len(explored)/len(sources))
    st.caption(f"Exploración: {len(explored)} de {len(sources)} fuentes · actividad formativa sin nota.")
    return len(explored),len(sources)

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


def _render_course2_lab1_stage0(lab, saved):
    """Etapa 0 real del Curso 2 · Laboratorio 1, integrada al flujo futuro existente."""
    class_id = lab["id"]
    stage_selector_key = f"future_stage_{class_id}"

    header(
        "ETAPA 0 · LABORATORIO 1",
        "El edificio como sistema vibroacústico",
        "Reconocer cómo la energía puede ingresar al edificio, propagarse por su estructura y radiarse posteriormente como sonido.",
        show_overview=False,
        duration_minutes=20,
    )
    st.caption(f"{lab['course']} · Laboratorio 1")

    st.markdown("### Objetivo de aprendizaje")
    st.markdown(
        """
- Reconocer el edificio como medio de transmisión de energía vibratoria.
- Diferenciar conceptualmente transmisión aérea y estructural.
- Identificar fuente, excitación, propagación, radiación y receptor.
- Reconocer que una misma fuente puede generar simultáneamente ruido aéreo y estructural.
- Comprender que una superficie estructural vibrante puede radiar posteriormente sonido hacia el aire.
        """
    )

    st.markdown("### Antes de comenzar")
    st.info(
        "En acústica de edificios no basta con identificar dónde se escucha el ruido. "
        "Para controlarlo necesitamos descubrir dónde se genera la energía, cómo ingresa a la estructura, "
        "por dónde se propaga y qué elemento termina radiándola hacia el receptor."
    )
    st.latex(
        r"\text{FUENTE}\rightarrow\text{EXCITACIÓN}\rightarrow\text{RESPUESTA}"
        r"\rightarrow\text{PROPAGACIÓN}\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
    )

    # La imagen principal se renderiza dentro del interactivo para evitar duplicarla.
    # Antes de elegir una fuente se muestra el render base; después, la misma zona
    # visual cambia a la versión resaltada correspondiente.

    # El interactivo debe quedar inmediatamente asociado al render principal.
    # En móvil los botones son táctiles y se apilan automáticamente si falta ancho.
    explored_count, explored_total = _course2_lab1_stage0_energy_interactive(class_id, saved)

    st.markdown("### 1 · Situación inicial")
    st.write("Observa un edificio residencial en el que pueden coexistir una pisada, una bomba centrífuga, una descarga sanitaria y un ventilador.")
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q1",
        "¿Cuál de estas fuentes puede producir ruido estructural?",
        [
            "A. Solo la pisada",
            "B. La pisada y la bomba",
            "C. Solo la bomba",
            "D. Todas pueden hacerlo dependiendo de cómo estén conectadas al edificio",
        ],
        "D. Todas pueden hacerlo dependiendo de cómo estén conectadas al edificio",
        "Todas pueden introducir energía mecánica en elementos constructivos. Esa energía puede propagarse por losas, muros, pilares, tuberías, soportes u otros elementos y posteriormente producir sonido en otro recinto.",
    )

    st.markdown("### 2 · Ruido aéreo y ruido estructural")
    aerial, structural = st.columns(2)
    with aerial:
        with st.container(border=True):
            st.markdown("#### Ruido aéreo")
            st.latex(r"p\rightarrow v\rightarrow p")
            st.write(
                "La fuente genera primero fluctuaciones de presión en el aire. Esa presión puede hacer vibrar un cerramiento y éste radiar nuevamente al otro lado."
            )
            st.markdown("**Ruido aéreo: primero el aire.**")
    with structural:
        with st.container(border=True):
            st.markdown("#### Ruido estructural")
            st.latex(r"F\rightarrow v\rightarrow p")
            st.write(
                "La fuente introduce primero una fuerza mecánica en la estructura. La vibración se propaga por elementos sólidos y posteriormente una superficie puede radiar sonido al aire."
            )
            st.markdown("**Ruido estructural: primero la estructura.**")

    st.markdown("### 3 · De la vibración al sonido")
    st.write(
        "Hasta ahora seguimos la energía a través del edificio. Ahora acerquémonos a una superficie estructural "
        "para observar qué ocurre cuando su vibración termina produciendo sonido en el recinto receptor."
    )
    _course2_lab1_stage0_asset(
        "curso2_lab1_etapa0_vibracion_radiacion.webp",
        "Naranja: fuerza y vibración estructural. Cian: radiación acústica desde la cara inferior de la losa hacia el aire del recinto receptor.",
    )
    st.latex(r"F(t)\rightarrow v(t)\rightarrow v_n(t)\rightarrow p(t)")

    vib_steps = {
        "F(t) · Fuerza": {
            "title": "1 · Fuerza dinámica — F(t)",
            "text": "La pisada introduce una fuerza que varía en el tiempo sobre la losa. Ese es el punto de entrada de energía mecánica al sistema estructural.",
            "latex": r"F(t)\rightarrow \text{estructura}",
        },
        "v(t) · Vibración": {
            "title": "2 · Velocidad vibratoria — v(t)",
            "text": "La losa responde vibrando. Esa respuesta mecánica puede propagarse por el propio elemento y por otros componentes estructuralmente conectados.",
            "latex": r"F(t)\rightarrow v(t)",
        },
        "vₙ(t) · Superficie": {
            "title": "3 · Componente normal — v_n(t)",
            "text": "De toda la vibración de la superficie, la componente perpendicular a ella es la que desplaza el aire adyacente y puede iniciar la radiación acústica.",
            "latex": r"v(t)\rightarrow v_n(t)",
        },
        "p(t) · Sonido": {
            "title": "4 · Presión sonora — p(t)",
            "text": "El movimiento normal de la superficie produce fluctuaciones de presión en el aire. Esas fluctuaciones se propagan por el dormitorio y pueden ser percibidas por el receptor.",
            "latex": r"v_n(t)\rightarrow p(t)",
        },
    }
    vib_key = f"{class_id}_stage0_vib_step"
    if vib_key not in st.session_state:
        st.session_state[vib_key] = "F(t) · Fuerza"
    vib_cols = st.columns(4)
    for col, label in zip(vib_cols, vib_steps):
        with col:
            if st.button(
                label,
                key=f"{vib_key}_{label}",
                type="primary" if st.session_state.get(vib_key) == label else "secondary",
                width="stretch",
            ):
                st.session_state[vib_key] = label
                st.rerun()
    vib_data = vib_steps[st.session_state[vib_key]]
    with st.container(border=True):
        st.markdown(f"#### {vib_data['title']}")
        st.latex(vib_data["latex"])
        st.write(vib_data["text"])

    st.info(
        "**En palabras simples:** una losa o muro no necesita moverse de manera visible para producir ruido. "
        "Movimientos extremadamente pequeños de su superficie pueden desplazar el aire y generar sonido audible."
    )

    st.markdown("### 4 · Vibración no es igual a radiación")
    st.latex(r"\text{VIBRACIÓN}\neq\text{RADIACIÓN ACÚSTICA}")
    st.write(
        "El render anterior muestra una superficie que sí está radiando, pero medir vibración no permite concluir por sí solo "
        "que la superficie sea un radiador acústico eficiente. La radiación depende de la frecuencia, la distribución espacial "
        "de la vibración, la superficie involucrada y el acoplamiento con el aire. Más adelante se introducirá la eficiencia de radiación σ."
    )

    st.markdown("### 5 · Caso visual · De la pisada al receptor")
    st.write("Recorre el fenómeno sin convertirlo en un cuestionario. Selecciona una etapa y observa cómo cambia el camino de la energía.")
    foot_stage_key=f"{class_id}_stage0_foot_visual"
    if foot_stage_key not in st.session_state:
        st.session_state[foot_stage_key]=0
    foot_labels=["Impacto", "Respuesta de la losa", "Propagación", "Radiación", "Receptor"]
    foot_cols=st.columns(5)
    for idx,(col,label) in enumerate(zip(foot_cols,foot_labels)):
        with col:
            if st.button(label,key=f"{foot_stage_key}_{idx}",type="primary" if st.session_state[foot_stage_key]==idx else "secondary",width="stretch"):
                st.session_state[foot_stage_key]=idx
                st.rerun()
    components.html(_course2_stage0_footstep_svg(int(st.session_state[foot_stage_key])), height=570, scrolling=False)
    foot_explain=[
        (r"F(t)", "La pisada introduce una fuerza dinámica en la losa."),
        (r"F(t)\rightarrow v(t)", "La estructura responde: la losa adquiere velocidad vibratoria."),
        (r"F(t)\rightarrow v(t)\rightarrow v_n(t)", "La vibración se propaga y aparece movimiento normal en la superficie del cielo."),
        (r"v_n(t)\rightarrow p(t)", "La superficie vibrante desplaza el aire y comienza la radiación acústica."),
        (r"F(t)\rightarrow v(t)\rightarrow v_n(t)\rightarrow p(t)\rightarrow \text{RECEPTOR}", "La presión sonora se propaga por el recinto hasta el receptor."),
    ]
    latex,text=foot_explain[int(st.session_state[foot_stage_key])]
    st.latex(latex)
    st.caption(text)

    st.markdown("### 6 · Mapa de caminos · Una bomba, tres rutas")
    st.write("Selecciona un camino en el esquema. La misma bomba puede excitar los tres simultáneamente.")
    pump_path_key=f"{class_id}_stage0_pump_path_visual"
    if pump_path_key not in st.session_state:
        st.session_state[pump_path_key]="base"
    p1,p2,p3=st.columns(3)
    choices=[("base","Base → losa"),("pipe","Tubería → estructura"),("air","Carcasa → aire")]
    for col,(value,label) in zip((p1,p2,p3),choices):
        with col:
            if st.button(label,key=f"{pump_path_key}_{value}",type="primary" if st.session_state[pump_path_key]==value else "secondary",width="stretch"):
                st.session_state[pump_path_key]=value
                st.rerun()
    active_path=st.session_state[pump_path_key]
    components.html(_course2_stage0_pump_paths_svg(active_path), height=570, scrolling=False)
    path_info={
        "base":(r"\text{BOMBA}\rightarrow\text{BASE}\rightarrow\text{LOSA}\rightarrow\text{ESTRUCTURA}","Camino estructural directo por los apoyos de la máquina."),
        "pipe":(r"\text{BOMBA}\rightarrow\text{TUBERÍA}\rightarrow\text{SOPORTES}\rightarrow\text{ESTRUCTURA}","Camino estructural paralelo: una tubería rígida puede puentear el aislamiento de la base."),
        "air":(r"\text{CARCASA}\rightarrow\text{AIRE}\rightarrow\text{RECEPTOR}","Camino aéreo directo: requiere medidas distintas de las que controlan transmisión estructural."),
    }
    st.latex(path_info[active_path][0])
    st.caption(path_info[active_path][1])

    _course2_lab1_stage0_pump_lab(class_id, saved)

    st.markdown("### Preguntas de comprensión")
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q2",
        "Una persona escucha una bomba ubicada dos pisos más abajo. ¿Podemos concluir que el sonido viajó solamente por el aire?",
        [
            "A. Sí",
            "B. No, también puede existir transmisión estructural",
            "C. Sí, porque las vibraciones no producen sonido",
            "D. Solo si la bomba trabaja bajo 100 Hz",
        ],
        "B. No, también puede existir transmisión estructural",
        "Correcto. La distancia vertical no permite concluir el camino de transmisión: pueden coexistir radiación aérea y propagación estructural por losas, muros, tuberías o soportes.",
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q3",
        "Una pared presenta vibración medible. ¿Podemos concluir que necesariamente es un radiador acústico eficiente?",
        ["A. Sí", "B. No"],
        "B. No",
        "Correcto. Vibración medible no implica radiación acústica eficiente; la eficiencia depende de frecuencia, patrón vibratorio, superficie y acoplamiento con el aire.",
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_q4",
        "¿Cuál secuencia representa mejor un fenómeno de ruido de origen estructural?",
        ["A. p → p", "B. F → v → p", "C. v → F → p", "D. p → F"],
        "B. F → v → p",
        "Correcto. En el ruido de origen estructural una fuerza excita primero la estructura, ésta vibra y luego una superficie puede radiar presión sonora al aire.",
    )

    st.markdown("### Mini caso profesional")
    st.write(
        "Una bomba está instalada sobre aisladores, pero una tubería sale rígidamente desde la bomba y está fijada mediante abrazaderas metálicas directamente al muro."
    )
    _future_stage0_mcq(
        class_id,
        saved,
        "stage0_case",
        "¿Cuál es la hipótesis técnica más razonable?",
        [
            "A. Los aisladores necesariamente están defectuosos",
            "B. Debe colocarse material absorbente en el dormitorio",
            "C. Puede existir un camino estructural paralelo por tubería y soportes",
            "D. El problema debe ser exclusivamente aéreo",
        ],
        "C. Puede existir un camino estructural paralelo por tubería y soportes",
        "Un buen aislador bajo la máquina no garantiza el aislamiento del sistema completo si existe otra conexión rígida capaz de puentearlo.",
    )

    st.markdown("### Cierre")
    st.latex(
        r"\text{FUENTE}\rightarrow\text{EXCITACIÓN}\rightarrow\text{RESPUESTA ESTRUCTURAL}"
        r"\rightarrow\text{PROPAGACIÓN}\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
        r"\rightarrow\text{CONTROL}"
    )
    st.success(
        "En las siguientes etapas aprenderemos a cuantificar cada parte de esta cadena. "
        "La primera pregunta será: si dos estructuras reciben exactamente la misma fuerza, ¿vibran necesariamente igual?"
    )

    required = ["stage0_q1", "stage0_q2", "stage0_q3", "stage0_q4", "stage0_case"]
    completed_questions = sum(
        1 for key in required
        if isinstance(saved.get(key), dict) and saved[key].get("completed")
    )
    st.caption(f"Respuestas formativas guardadas: {completed_questions} de {len(required)}")

    if saved.get("done_0"):
        st.success("Etapa 0 completada y guardada en tu progreso.")
    else:
        if st.button("Completar Etapa 0", type="primary", key=f"complete_stage0_{class_id}"):
            if completed_questions < len(required):
                st.warning("Guarda las cinco respuestas formativas antes de completar la etapa.")
            elif explored_count < explored_total:
                st.warning("Explora Pisada, Bomba y Descarga sanitaria en ‘Sigue la energía’ antes de completar la etapa.")
            else:
                saved["done_0"] = True
                saved["updated_0"] = _now()
                _save_future_state_impl(class_id, saved)
                st.rerun()

    nav_left, nav_right = st.columns(2)
    with nav_left:
        st.button("← Anterior", disabled=True, key=f"stage0_prev_{class_id}", width="stretch")
    with nav_right:
        if st.button("Etapa 1 →", key=f"stage0_next_{class_id}", width="stretch"):
            st.session_state[stage_selector_key] = 1
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

        answered=sum(1 for i in range(11) if saved.get(f"done_{i}"))
        st.progress(answered/11)
        st.caption(f"Avance: {answered}/11 etapas · {answered*10}/110 puntos formativos")

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
            list(range(11)),
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

    if class_id == "clase-03-impacto-instalaciones-lab-1" and selected == 0:
        _render_course2_lab1_stage0(lab, saved)
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

    if st.session_state.get("role")=="Docente":
        # Las etapas futuras no siempre incluyen un bloque editable/teacher_solution.
        # No se debe abortar el render por una variable opcional inexistente.
        editable = {}
        with st.expander("🔐 Orientación docente y respuesta esperada"):
            if editable.get("teacher_solution"):
                st.markdown(editable["teacher_solution"])
            st.markdown(f"""
            **Evidencia mínima:** identificación correcta del fenómeno; selección coherente
            de magnitud y método; procedimiento trazable; resultado con unidad; decisión
            vinculada al criterio; medida verificable.

            **Retroalimentación sugerida:** revisar si la respuesta distingue propiedad de
            elemento, desempeño en terreno, exposición y percepción. Penalizar promedios
            aritméticos de decibeles, símbolos intercambiados y conclusiones normativas sin fuente.
            """)

def future_projection_stage_impl(lab, stage):
    """Vista limpia de una etapa futura para la ventana compartida en Zoom."""
    stage = int(stage or 0)
    if stage < 0 or stage >= len(lab.get("stages", [])):
        stage = 0

    st.session_state["projection_mode"] = True
    st.session_state["role"] = "Proyección"
    st.session_state["name"] = "Pantalla de clase"

    # La Etapa 0 integrada del Curso 2 se proyecta con el mismo contenido visible
    # del alumno, pero sobre un estado efímero para no registrar respuestas de la
    # pantalla de Zoom en la base de datos.
    if lab.get("id") == "clase-03-impacto-instalaciones-lab-1" and stage == 0:
        _render_course2_lab1_stage0(lab, {})
        return

    title, objective, concept, activity = lab["stages"][stage]
    stage_minutes = 20 if stage not in (9, 10) else 35
    header(f"ETAPA {stage} · LABORATORIO {lab['number']}", title, objective)
    st.caption(f"{lab['course']} · Vista para alumnos")
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
    st.caption(f"Tiempo de referencia de la etapa: {stage_minutes} min")


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
