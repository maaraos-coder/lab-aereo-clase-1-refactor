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


def _course2_lab1_stage0_pump_svg(encierro=False, absorbente=False, antivibratorios=False, flexible=False):
    """SVG técnico conceptual de una bomba y sus caminos de transmisión."""
    base_color = "#35d07f" if antivibratorios else "#ff8a3d"
    pipe_color = "#35d07f" if flexible else "#ff8a3d"
    air_reduction = encierro or absorbente
    air_color = "#35d07f" if air_reduction else "#35c7ff"
    air_opacity = "0.34" if air_reduction else "0.95"
    base_opacity = "0.35" if antivibratorios else "0.95"
    pipe_opacity = "0.35" if flexible else "0.95"

    enclosure = ""
    if encierro:
        enclosure = """
        <rect x="150" y="92" width="390" height="300" rx="18" fill="#0b1730" fill-opacity="0.72"
              stroke="#72d7ff" stroke-width="4"/>
        <rect x="168" y="110" width="354" height="264" rx="12" fill="none"
              stroke="#72d7ff" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="8 8"/>
        <text x="345" y="126" text-anchor="middle" class="smallLabel">ENCIERRO ACÚSTICO</text>
        """
    absorbent_svg = ""
    if absorbente:
        absorbent_svg = """
        <g fill="#8ed9ff" fill-opacity="0.34" stroke="#8ed9ff" stroke-opacity="0.55">
          <path d="M185 150 l18 -14 l18 14 l18 -14 l18 14 l18 -14 l18 14" fill="none" stroke-width="5"/>
          <path d="M185 174 l18 -14 l18 14 l18 -14 l18 14 l18 -14 l18 14" fill="none" stroke-width="5"/>
          <path d="M185 198 l18 -14 l18 14 l18 -14 l18 14 l18 -14 l18 14" fill="none" stroke-width="5"/>
        </g>
        <text x="235" y="226" text-anchor="middle" class="mini">ABSORBENTE</text>
        """
    if antivibratorios:
        isolators = """
        <g stroke="#53e19f" stroke-width="6" fill="none" stroke-linecap="round">
          <path d="M258 401 q12 -18 24 0 q12 18 24 0 q12 -18 24 0"/>
          <path d="M372 401 q12 -18 24 0 q12 18 24 0 q12 -18 24 0"/>
        </g>
        <text x="345" y="430" text-anchor="middle" class="mini green">ANTIVIBRATORIOS</text>
        """
    else:
        isolators = """
        <rect x="270" y="388" width="52" height="18" rx="3" fill="#9099aa"/>
        <rect x="385" y="388" width="52" height="18" rx="3" fill="#9099aa"/>
        <text x="345" y="430" text-anchor="middle" class="mini">APOYO RÍGIDO</text>
        """
    if flexible:
        flexible_piece = """
        <g stroke="#53e19f" fill="none" stroke-width="7" stroke-linecap="round">
          <path d="M575 276 q14 -16 28 0 q14 16 28 0 q14 -16 28 0 q14 16 28 0"/>
        </g>
        <text x="630" y="252" text-anchor="middle" class="mini green">CONEXIÓN FLEXIBLE</text>
        """
    else:
        flexible_piece = """
        <line x1="575" y1="276" x2="688" y2="276" stroke="#4aa8ff" stroke-width="14" stroke-linecap="round"/>
        <text x="630" y="252" text-anchor="middle" class="mini">CONEXIÓN RÍGIDA</text>
        """

    base_status = "REDUCIDO" if antivibratorios else "ACTIVO"
    pipe_status = "REDUCIDO" if flexible else "ACTIVO"
    air_status = "REDUCIDO" if air_reduction else "ACTIVO"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 650" width="100%" role="img"
        aria-label="Esquema técnico interactivo de control vibroacústico de una bomba centrífuga">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#071223"/><stop offset="1" stop-color="#0b2945"/>
        </linearGradient>
        <linearGradient id="slab" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#68788b"/><stop offset="1" stop-color="#364354"/>
        </linearGradient>
        <filter id="glowOrange"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <filter id="glowCyan"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <style>
          .title{{font:700 28px Arial,sans-serif;fill:#f5fbff}} .sub{{font:400 16px Arial,sans-serif;fill:#b9d4e8}}
          .label{{font:700 16px Arial,sans-serif;fill:#f4f8fb}} .smallLabel{{font:700 14px Arial,sans-serif;fill:#a9e7ff;letter-spacing:1px}}
          .mini{{font:700 12px Arial,sans-serif;fill:#b6c6d6;letter-spacing:.5px}} .green{{fill:#6df0b2}}
          .status{{font:700 13px Arial,sans-serif}}
        </style>
      </defs>
      <rect width="1120" height="650" rx="22" fill="url(#bg)"/>
      <text x="45" y="52" class="title">Laboratorio conceptual · Controla la bomba</text>
      <text x="45" y="80" class="sub">Observa qué camino modifica cada medida de control.</text>

      <rect x="820" y="108" width="250" height="360" rx="14" fill="#102943" stroke="#345776" stroke-width="3"/>
      <text x="945" y="140" text-anchor="middle" class="smallLabel">ESTRUCTURA / RECINTO</text>
      <line x1="835" y1="334" x2="1055" y2="334" stroke="#566c80" stroke-width="7"/>
      <rect x="900" y="350" width="108" height="52" rx="9" fill="#182335" stroke="#4e677f" stroke-width="2"/>
      <text x="954" y="382" text-anchor="middle" class="mini">RECEPTOR</text>

      <rect x="70" y="455" width="980" height="82" rx="8" fill="url(#slab)" stroke="#8aa0b2" stroke-width="2"/>
      <g stroke="#91a2b1" stroke-opacity="0.25" stroke-width="2">
        <path d="M100 480 H1020 M100 505 H1020"/><path d="M160 460 V532 M270 460 V532 M380 460 V532 M490 460 V532 M600 460 V532 M710 460 V532"/>
      </g>
      <text x="560" y="520" text-anchor="middle" class="smallLabel">LOSA DE HORMIGÓN</text>

      {enclosure}
      {absorbent_svg}

      <g>
        <rect x="245" y="344" width="220" height="44" rx="6" fill="#566474" stroke="#8495a6" stroke-width="3"/>
        <rect x="278" y="282" width="110" height="64" rx="18" fill="#2476ac" stroke="#7ad4ff" stroke-width="3"/>
        <circle cx="386" cy="314" r="39" fill="#175779" stroke="#7ad4ff" stroke-width="4"/>
        <circle cx="386" cy="314" r="13" fill="#b8d5e6"/>
        <rect x="210" y="295" width="80" height="40" rx="11" fill="#314861" stroke="#6e8398" stroke-width="3"/>
        <g stroke="#73879a" stroke-width="4"><line x1="225" y1="301" x2="225" y2="328"/><line x1="242" y1="301" x2="242" y2="328"/><line x1="259" y1="301" x2="259" y2="328"/></g>
        <text x="345" y="270" text-anchor="middle" class="label">BOMBA CENTRÍFUGA</text>
      </g>
      {isolators}

      <line x1="425" y1="314" x2="575" y2="276" stroke="#4aa8ff" stroke-width="14" stroke-linecap="round"/>
      {flexible_piece}
      <line x1="688" y1="276" x2="842" y2="276" stroke="#4aa8ff" stroke-width="14" stroke-linecap="round"/>
      <line x1="842" y1="276" x2="842" y2="210" stroke="#4aa8ff" stroke-width="14" stroke-linecap="round"/>
      <path d="M812 276 h60" stroke="#a5b6c7" stroke-width="5"/>
      <path d="M832 260 v32 M852 260 v32" stroke="#a5b6c7" stroke-width="5"/>
      <text x="840" y="190" text-anchor="middle" class="mini">SOPORTE A ESTRUCTURA</text>

      <g opacity="{base_opacity}" filter="url(#glowOrange)">
        <path d="M345 406 C345 425 345 438 345 455" stroke="{base_color}" stroke-width="9" fill="none" stroke-linecap="round"/>
        <path d="M240 485 C300 452 390 452 450 485" stroke="{base_color}" stroke-width="5" fill="none"/>
        <path d="M205 505 C290 458 405 458 490 505" stroke="{base_color}" stroke-width="3" fill="none" opacity=".7"/>
      </g>

      <g opacity="{pipe_opacity}" filter="url(#glowOrange)">
        <path d="M430 298 C555 240 700 238 826 266" stroke="{pipe_color}" stroke-width="6" fill="none" stroke-dasharray="10 7"/>
        <circle cx="842" cy="276" r="22" fill="none" stroke="{pipe_color}" stroke-width="5"/>
      </g>

      <g opacity="{air_opacity}" filter="url(#glowCyan)" fill="none" stroke="{air_color}" stroke-linecap="round">
        <path d="M168 250 Q95 314 168 377" stroke-width="6"/>
        <path d="M138 220 Q35 314 138 408" stroke-width="4"/>
        <path d="M490 226 Q565 314 490 400" stroke-width="5"/>
      </g>

      <g>
        <rect x="74" y="565" width="300" height="58" rx="12" fill="#0d2138" stroke="{base_color}" stroke-width="2"/>
        <text x="96" y="590" class="mini">CAMINO 1 · BASE → LOSA</text>
        <text x="96" y="612" class="status" fill="{base_color}">{base_status}</text>

        <rect x="410" y="565" width="300" height="58" rx="12" fill="#0d2138" stroke="{pipe_color}" stroke-width="2"/>
        <text x="432" y="590" class="mini">CAMINO 2 · TUBERÍA → ESTRUCTURA</text>
        <text x="432" y="612" class="status" fill="{pipe_color}">{pipe_status}</text>

        <rect x="746" y="565" width="300" height="58" rx="12" fill="#0d2138" stroke="{air_color}" stroke-width="2"/>
        <text x="768" y="590" class="mini">CAMINO 3 · RUIDO AÉREO</text>
        <text x="768" y="612" class="status" fill="{air_color}">{air_status}</text>
      </g>
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

    st.markdown(_course2_lab1_stage0_pump_svg(**config), unsafe_allow_html=True)

    base_state="Reducido" if antivibratorios else "Activo"
    pipe_state="Reducido" if flexible else "Activo"
    air_state="Reducido" if (encierro or absorbente) else "Activo"
    s1,s2,s3=st.columns(3)
    with s1:
        st.metric("Base → losa", base_state)
    with s2:
        st.metric("Tubería → estructura", pipe_state)
    with s3:
        st.metric("Ruido aéreo", air_state)

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

    st.markdown("### 5 · Ejemplo: pisada")
    st.latex(
        r"\text{PIE}\rightarrow F(t)\rightarrow\text{LOSA}\rightarrow\text{VIBRACIÓN}"
        r"\rightarrow\text{RADIACIÓN}\rightarrow\text{RECEPTOR}"
    )

    st.markdown("### 6 · Ejemplo: bomba")
    st.write("Una bomba puede excitar varios caminos simultáneamente:")
    st.latex(r"\text{BOMBA}\rightarrow\text{BASE}\rightarrow\text{LOSA}")
    st.latex(r"\text{BOMBA}\rightarrow\text{TUBERÍA}\rightarrow\text{SOPORTE}\rightarrow\text{ESTRUCTURA}")
    st.latex(r"\text{CARCASA}\rightarrow\text{AIRE}")
    st.warning("Una misma fuente puede utilizar varios caminos simultáneamente.")

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
