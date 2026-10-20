Warning: truncated output (original token count: 396925)
... 539121 bytes omitted ...

import streamlit.components.v1 as components
from pathlib import Path
import math
import json
import os
from typing import Any, Dict, Iterable, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from labs import curso4_laboratorio_1 as _c4l1
from labs import curso4_laboratorio_2 as _c4l2


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
ASSET_DIR = PROJECT_ROOT / "assets"

"""Vistas de cursos, selección de laboratorios y laboratorios futuros.

La lógica se conserva sin cambios. ``app.py`` inyecta las dependencias
compartidas antes de ejecutar cada vista para evitar acoplamientos circulares.
"""

_RUNTIME_PROTECTED = {"run_view", "_bind_runtime", "_VIEWS", "_RUNTIME_PROTECTED", "__file__", "__spec__", "__package__", "MODULE_DIR", "PROJECT_ROOT", "ASSET_DIR"}

def _bind_runtime(runtime):
    module_globals = globals()
    for name, value in runtime.items():
        if name not in _RUNTIME_PROTECTED and name not in _VIEWS:
            module_globals[name] = value

def course_dashboard_impl():
    header("MIS CLASES","Diplomado en Acústica en la Edificación",
           "Selecciona un curso y abre el laboratorio habilitado en la fecha programada.")

    st.markdown(
        """
        <style>
        .dashboard-lab-card{
            min-height:178px;
            height:178px;
            display:flex;
            flex-direction:column;
            box-sizing:border-box;
            border:1px solid #cbd9e8;
            border-left:4px solid #1689d8;
            border-radius:14px;
            background:#fff;
            padding:14px 16px 13px;
            margin:0 0 8px 0;
            box-shadow:0 3px 12px rgba(15,23,42,.035);
            overflow:hidden;
        }
        .dashboard-lab-card .dashboard-kicker{
            color:#075ea8;font-size:.72rem;font-weight:850;
            letter-spacing:.055em;text-transform:uppercase;margin-bottom:5px;
        }
        .dashboard-lab-card .dashboard-date{
            color:#748398;font-size:.79rem;line-height:1.25;min-height:20px;
        }
        .dashboard-lab-card .dashboard-divider{
            height:1px;background:#d8e0e9;margin:13px 0 11px;flex:0 0 auto;
        }
        .dashboard-lab-card .dashboard-state{
            color:#142033;font-size:.88rem;font-weight:750;line-height:1.3;margin-bottom:5px;
        }
        .dashboard-lab-card .dashboard-detail{
            color:#66768a;font-size:.80rem;line-height:1.35;
            display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
        }
        @media (max-width:800px){
            .dashboard-lab-card{min-height:168px;height:auto;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def _dashboard_card(number, meta, state, detail):
        html=(
            f'<div class="dashboard-lab-card">'
            f'<div class="dashboard-kicker">LABORATORIO {number}</div>'
            + (f'<div class="dashboard-date">{meta}</div>' if meta else '')
            + f'<div class="dashboard-divider"></div>'
            f'<div class="dashboard-state">{state}</div>'
            f'<div class="dashboard-detail">{detail}</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    client=_supabase()
    if client is None:
        st.warning("Supabase todavía no está configurado. La aplicación está usando almacenamiento local de prueba.")
        classes=[
            {"id":"clase-01-aislamiento-ruido-aereo","class_number":1,
             "title":"Laboratorio 1","description":"","status":"published","due_at":None},
            {"id":"clase-02-aislamiento-ruido-aereo-minvu","class_number":2,
             "title":"Laboratorio 2","description":"","status":"draft","due_at":None},
        ]
    else:
        classes=_course_classes(client)

    class_by_number={item.get("class_number"):item for item in classes}
    summaries,course_result=_result_summary()
    first_course=ACADEMIC_COURSES[0]
    st.markdown(f"### {first_course['title']}")

    visible_first=[]
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
        visible_first.append((lab,item,opening,released,available))

    first_cols=st.columns(2)
    for col,(lab,item,opening,released,available) in zip(first_cols,visible_first):
        number=lab["number"]
        summary=summaries[number]
        progress_status=("Pendiente" if summary["answered"]==0 else
                         "Completado" if summary["answered"]>=summary["expected"] else "En progreso")
        if st.session_state.get("role")=="Docente":
            availability=("Publicado para alumnos" if released else "Borrador · oculto para alumnos")
        else:
            availability="Disponible" if available else f"Habilitación: {_opening_label(opening)}"

        with col:
            # En "Mis clases" no se muestran puntajes ni métricas de desempeño.
            # Esa información se concentra exclusivamente en "Mi desempeño".
            # "Mis clases" es una vista de acceso, no de desempeño.
            # Para Alumno y Docente se omiten puntajes y métricas de actividades;
            # esas cifras se consultan en las vistas específicas de desempeño/evaluación.
            card_state = "Publicado para alumnos" if released else "Borrador · oculto para alumnos"
            card_detail = "Accede al laboratorio para revisar sus contenidos y actividades."
            _dashboard_card(
                number,
                availability,
                card_state,
                card_detail,
            )
            if available and st.button(
                "Continuar laboratorio" if number==ACTIVE_LAB else "Abrir laboratorio",
                key=f"open_lab_{number}",
                type="primary" if number==ACTIVE_LAB else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_lab=number
                st.session_state["_open_lab_requested"]=True
                st.rerun()

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
                _dashboard_card(
                    lab["number"],
                    '',
                    state,
                    lab["focus"],
                )
                if st.button("Abrir laboratorio",key=f'open_{lab["id"]}',use_container_width=True):
                    st.session_state["future_lab_id"]=lab["id"]
                    st.rerun()

def _future_saved_impl(class_id):
    """Return the saved state for the selected student and future class."""
    from labs.curso4_lab2_projection import CLASS_ID as projection_lab, is_projection, load_draft
    if class_id == projection_lab and is_projection(st):
        try:
            return load_draft(st, _supabase(), COURSE_ID, class_id)
        except Exception:
            st.error("No se pudo recuperar el avance de la clase. Revisa la conexión y actualiza la pantalla para volver a intentarlo.")
            st.stop()
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
    """Guarda el avance personal o el borrador independiente de la clase proyectada."""
    from labs.curso4_lab2_projection import CLASS_ID as projection_lab, is_projection, save_draft
    if is_projection(st):
        if class_id == projection_lab:
            save_draft(st, _supabase(), COURSE_ID, class_id, state)
        else:
            st.session_state[f"future_saved_{class_id}"] = state
        return
    # Lab 2 confirma el almacenamiento antes de reemplazar el último avance.
    if class_id != projection_lab:
        st.session_state[f"future_saved_{class_id}"] = state

    # Seguridad adicional: si no existe un usuario autenticado no se persiste.
    user_key = st.session_state.get("user_key")
    if not user_key:
        if class_id == projection_lab:
            raise RuntimeError("No hay un usuario autenticado para guardar el avance.")
        return

    client = _supabase()
    if client is None:
        if class_id == projection_lab:
            raise RuntimeError("No hay conexión para guardar el avance.")
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
    if class_id == projection_lab:
        from copy import deepcopy
        st.session_state[f"future_saved_{class_id}"] = deepcopy(state)

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

    # Navegación del Curso 2 · Lab 1: exclusivamente mediante la barra lateral.
    # La bienvenida se considera visitada al abrirla como alumno; Proyección no persiste progreso.
    if st.session_state.get("role") == "Alumno" and not saved.get("done_0"):
        saved["done_0"] = True
        saved["updated_0"] = _now()
        _save_future_state_impl(class_id, saved)

    st.caption("Para continuar, selecciona la siguiente etapa desde la barra lateral.")


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

    st.caption("Navega entre etapas desde la barra lateral.")


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
          <div style="padding:12p…212152 tokens truncated…esentatividad temporal ni corrige sectores sin mediciones.",
            "Demuestra que no existen errores instrumentales.",
            "Permite eliminar la descripción de limitaciones."
        ],
        1,
        "La validación cruzada evalúa comportamiento predictivo entre los datos disponibles; no demuestra por sí sola representatividad temporal o territorial."
    ),
    (
        "Suma energética",
        "Dos fuentes independientes producen 63 dB cada una en el mismo receptor. Si actúan simultáneamente, el nivel total es aproximadamente:",
        [
            "63 dB",
            "66 dB",
            "126 dB",
            "60 dB"
        ],
        1,
        "Dos niveles iguales sumados energéticamente incrementan aproximadamente 3 dB."
    ),
    (
        "Software y modelo",
        "Un software supera casos de prueba de aseguramiento de calidad para implementar un método de propagación. ¿Qué falta comprobar antes de confiar en el mapa de un proyecto real?",
        [
            "Nada: superar los casos de prueba garantiza que cualquier proyecto será correcto.",
            "Que las fuentes, emisiones, geometría, terreno y demás entradas representen adecuadamente el escenario real, idealmente contrastándolo con mediciones cuando sea posible.",
            "Solo que el mapa tenga una escala de colores atractiva.",
            "Que la grilla tenga el máximo número de celdas posible."
        ],
        1,
        "Verificar la implementación del método en software y validar el modelo de un caso real son controles distintos."
    ),
    (
        "Mapa proyectado",
        "En un modelo ya calculado, se desplaza únicamente el receptor R1 sin modificar fuentes ni entorno. ¿Qué debería ocurrir?",
        [
            "Debe cambiar todo el campo sonoro porque el receptor genera la propagación.",
            "El campo calculado permanece; cambia el nivel leído por R1 en su nueva posición.",
            "El nivel de potencia de la fuente debe ajustarse automáticamente.",
            "La operación convierte el mapa proyectado en un mapa interpolado."
        ],
        1,
        "El receptor es un punto de evaluación pasivo. Mover la fuente altera el campo; mover solo el receptor cambia dónde se consulta ese campo."
    ),
]


def _c3l2_s9_remote():
    user_key=st.session_state.get("user_key")
    if not user_key:return None
    rows=_remote_rows("responses",class_id=_C3L2_CLASS_ID,user_key=user_key) or []
    row=next((r for r in rows if int(r.get("stage") or -1)==9 and r.get("question_key")=="final_comprehension"),None)
    if not row:return None
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try:payload=json.loads(payload)
        except Exception:payload={}
    return {"row":row,"payload":payload}


def _c3l2_s9_save(saved):
    saved["c3l2_e9_answers"]={str(i):st.session_state.get(f"c3l2_e9_q{i}") for i in range(10)}
    saved["updated_9"]=_now()
    _c3l2_save(saved)


def _c3l2_s9_finish(saved,reason):
    answers={str(i):st.session_state.get(f"c3l2_e9_q{i}") for i in range(10)}
    score=sum(4 for i,q in enumerate(_C3L2_STAGE9_QUESTIONS) if answers.get(str(i))==q[2][q[3]])
    payload={"version":_C3L2_VERSION,"answers":answers,"score":score,"max_score":40,"reason":reason,"finished_at":_now()}
    client=_supabase(); user_key=st.session_state.get("user_key")
    if client is not None and user_key:
        qid=f"{_C3L2_CLASS_ID}-final_comprehension-v2"
        client.table("questions").upsert({
            "id":qid,"class_id":_C3L2_CLASS_ID,"stage":9,"question_key":"final_comprehension",
            "question_text":"Curso 3 · Laboratorio 2 · Evaluación de comprensión",
            "correct_answer":"Pauta de 10 preguntas","max_score":40,"content_version":2,"active":True,"updated_at":_now(),
        },on_conflict="id").execute()
        client.table("responses").upsert({
            "course_id":COURSE_ID,"class_id":_C3L2_CLASS_ID,"user_key":user_key,"stage":9,
            "question_key":"final_comprehension","question_text":"Evaluación de comprensión · Curso 3",
            "correct_answer":"Pauta de 10 preguntas","answer":payload,"auto_level":"Finalizada",
            "feedback":f"Resultado automático: {score}/40 puntos.","auto_score":score,"max_score":40,
            "status":"submitted","updated_at":_now(),"submitted_at":_now(),
        },on_conflict="class_id,user_key,question_key").execute()
    saved["c3l2_e9_submitted"]=True; saved["c3l2_e9_score"]=score; saved["done_9"]=True
    _c3l2_save(saved)


def _c3l2_stage9(lab,saved):
    _c3l2_header(
        9,
        "Evaluación oficial · preguntas de comprensión",
        "Diez preguntas de dificultad media–alta · 40 puntos · evaluación oficial del Curso 3.",
        35,
    )
    role=_c3l2_role()

    st.markdown("""
    <div class="c3l2-intro">
      <div class="c3l2-k">EVALUACIÓN OFICIAL · 40 PUNTOS</div>
      <div class="c3l2-title">Comprensión integrada de las Etapas 1 a 8</div>
      Las 10 preguntas combinan interpretación conceptual, cálculo breve y criterio técnico.
      Cada pregunta vale <b>4 puntos</b>.
    </div>
    """,unsafe_allow_html=True)

    if role=="Docente":
        st.markdown("## Pauta docente")
        st.caption("10 preguntas · 4 puntos cada una · 40 puntos totales.")
        for i,q in enumerate(_C3L2_STAGE9_QUESTIONS,1):
            with st.container(border=True):
                st.markdown(f"### {i}. {q[1]}")
                st.caption(f"{q[0]} · 4 puntos")
                for j,opt in enumerate(q[2]):
                    st.write(("✓ " if j==q[3] else "○ ")+opt)
                st.success("Respuesta correcta: "+q[2][q[3]])
                st.info(q[4])
        st.info("Las entregas oficiales se revisan en **Evaluaciones entregadas → Curso 3 → Laboratorio 2**.")
        return

    remote=_c3l2_s9_remote()
    if remote or saved.get("c3l2_e9_submitted"):
        row=(remote or {}).get("row",{}); payload=(remote or {}).get("payload",{})
        answers=payload.get("answers",saved.get("c3l2_e9_answers",{})) if isinstance(payload,dict) else {}
        score=float(
            row.get("teacher_score")
            if row and row.get("teacher_score") is not None
            else row.get("auto_score")
            if row
            else saved.get("c3l2_e9_score",0) or 0
        )
        correct=sum(
            answers.get(str(i))==q[2][q[3]]
            for i,q in enumerate(_C3L2_STAGE9_QUESTIONS)
        )
        st.success(f"Evaluación finalizada · {correct}/10 correctas · {score:g}/40 puntos.")
        st.caption("La entrega quedó bloqueada en modo solo lectura. La calificación se consolida en Mi desempeño.")

        for i,q in enumerate(_C3L2_STAGE9_QUESTIONS,1):
            chosen=answers.get(str(i-1)) if isinstance(answers,dict) else None
            correct_opt=q[2][q[3]]
            with st.container(border=True):
                st.markdown(f"### {i}. {q[1]}")
                st.write(f"**Tu respuesta:** {chosen or 'Sin respuesta'}")
                if chosen==correct_opt:
                    st.success("✓ Correcta · 4/4 puntos")
                else:
                    st.error("✗ Incorrecta · 0/4 puntos")
                    st.write(f"**Respuesta correcta:** {correct_opt}")
                st.info(q[4])
        return

    # Restaurar respuestas guardadas.
    for i,v in (saved.get("c3l2_e9_answers") or {}).items():
        key=f"c3l2_e9_q{i}"
        if key not in st.session_state and int(i)<len(_C3L2_STAGE9_QUESTIONS) and v in _C3L2_STAGE9_QUESTIONS[int(i)][2]:
            st.session_state[key]=v

    answered=sum(st.session_state.get(f"c3l2_e9_q{i}") is not None for i in range(10))
    a,b=st.columns(2)
    a.metric("Respondidas",f"{answered}/10")
    b.metric("Puntaje máximo","40 puntos")
    st.caption("Tus respuestas se guardan automáticamente. Puedes salir de la etapa y continuar antes del envío definitivo.")

    for i,q in enumerate(_C3L2_STAGE9_QUESTIONS):
        with st.container(border=True):
            h1,h2=st.columns([8,1])
            with h1:
                st.markdown(f"### {i+1}. {q[1]}")
                st.caption(q[0])
            with h2:
                st.markdown(
                    '<div style="text-align:center;border:1px solid #bfdbfe;border-radius:10px;'
                    'padding:6px 8px;background:#eff6ff;font-weight:800;color:#075985">4 pts</div>',
                    unsafe_allow_html=True,
                )
            st.radio(
                "Selecciona una alternativa",
                q[2],
                index=None,
                key=f"c3l2_e9_q{i}",
                label_visibility="collapsed",
                on_change=_c3l2_s9_save,
                args=(saved,),
            )

    answered=sum(st.session_state.get(f"c3l2_e9_q{i}") is not None for i in range(10))
    st.caption(f"{answered} de 10 respuestas registradas.")

    if st.button("💾 GUARDAR BORRADOR",use_container_width=True,key="c3l2_e9_draft"):
        _c3l2_s9_save(saved)
        st.success(f"Borrador guardado · {answered}/10 respuestas.")

    if st.button("ENVIAR EVALUACIÓN DEFINITIVA",type="primary",use_container_width=True,key="c3l2_e9_submit"):
        if answered<10:
            st.session_state["c3l2_e9_confirm"]=True
            st.warning(f"Faltan {10-answered} respuestas. Puedes continuar o confirmar el envío incompleto.")
        else:
            _c3l2_s9_finish(saved,"submitted")
            st.rerun()

    if st.session_state.get("c3l2_e9_confirm") and answered<10:
        if st.button("CONFIRMAR ENVÍO INCOMPLETO",use_container_width=True,key="c3l2_e9_submit_incomplete"):
            _c3l2_s9_finish(saved,"submitted_incomplete")
            st.rerun()


def _c3l2_s10_remote():
    user_key=st.session_state.get("user_key")
    if not user_key:return None
    rows=_remote_rows("responses",class_id=_C3L2_CLASS_ID,user_key=user_key) or []
    row=next((r for r in rows if int(r.get("stage") or -1)==10 and r.get("question_key")=="final_integrated_design"),None)
    if not row:return None
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try:payload=json.loads(payload)
        except Exception:payload={}
    return {"row":row,"payload":payload}


def _c3l2_s10_submit(saved,payload):
    client=_supabase(); user_key=st.session_state.get("user_key")
    if client is not None and user_key:
        qid=f"{_C3L2_CLASS_ID}-final_integrated_design-v2"
        client.table("questions").upsert({
            "id":qid,"class_id":_C3L2_CLASS_ID,"stage":10,"question_key":"final_integrated_design",
            "question_text":"Curso 3 · Laboratorio 2 · Medición de ruido de tráfico vehicular",
            "correct_answer":"Rúbrica docente de campaña vial, mediciones y mapa de ruido","max_score":60,
            "content_version":2,"active":True,"updated_at":_now(),
        },on_conflict="id").execute()
        client.table("responses").upsert({
            "course_id":COURSE_ID,"class_id":_C3L2_CLASS_ID,"user_key":user_key,"stage":10,
            "question_key":"final_integrated_design","question_text":"Evaluación aplicada · ruido de tráfico vehicular · Curso 3",
            "correct_answer":"Rúbrica docente de campaña vial, mediciones y mapa de ruido","answer":payload,
            "auto_level":"Pendiente de revisión","feedback":"Entrega registrada. Pendiente de revisión docente.",
            "auto_score":0,"max_score":60,"status":"submitted","updated_at":_now(),"submitted_at":_now(),
        },on_conflict="class_id,user_key,question_key").execute()
    saved["c3l2_s10_submitted"]=True; saved["c3l2_s10_submission_payload"]=payload; saved["done_10"]=True
    saved["c3l2_stage10"]=payload
    _c3l2_save(saved)


def _c3l2_stage10(lab,saved):
    _c3l2_header(
        10,
        "Evaluación oficial · mediciones de ruido de tráfico vehicular",
        "Realizar una campaña en una intersección vial, registrar 18 mediciones y construir un mapa vial defendible.",
        60,
    )
    role=_c3l2_role()

    rubric=pd.DataFrame([
        ("Lugar, croquis y evidencias",8,"Identifica claramente la intersección, describe el entorno y aporta enlaces de ubicación/evidencias."),
        ("Metodología y estabilización",10,"Explica procedimiento, Leq/Lmax, aplicación del criterio de estabilización de 2 dB y condiciones de medición."),
        ("Registro completo de mediciones",12,"9 puntos en vía principal + 9 en vía secundaria, con Leq, Lmax, hora y observaciones trazables."),
        ("Separación y diseño de campaña",8,"Los puntos siguen el criterio de 25–30 pasos desde la intersección y la red representa ambas vías."),
        ("Mapa vial de ruido",10,"Representa los resultados por intervalos de 3 o 5 dB, con lectura clara y coherente con los datos."),
        ("Análisis y conclusión",12,"Interpreta tendencias, diferencias entre vías, Leq/Lmax, limitaciones y alcance sin sobreafirmar."),
    ],columns=["Criterio","Puntos","Pauta"])

    if role=="Docente":
        st.markdown("""
        <div class="c3l2-intro">
          <div class="c3l2-k">PAUTA DOCENTE · 60 PUNTOS</div>
          <div class="c3l2-title">Tarea integradora · ruido de tráfico vehicular</div>
          La plataforma reemplaza el reporte escrito por una entrega estructurada: antecedentes, metodología,
          18 registros de medición, mapa vial automático, análisis y conclusión.
        </div>
        """,unsafe_allow_html=True)
        st.dataframe(rubric,hide_index=True,use_container_width=True)
        st.markdown("""
        **Condiciones centrales del encargo**
        - Intersección entre una vía principal y una vía secundaria.
        - 9 puntos por cada vía.
        - Separación aproximada de 25 a 30 pasos normales entre registros.
        - Registro de Leq y Lmax.
        - Aplicación documentada del criterio de estabilización de 2 dB.
        - Mapa vial con intervalos de 3 o 5 dB.
        """)
        st.info("Las entregas se califican en **Evaluaciones entregadas → Curso 3 → Laboratorio 2 → Etapa 10**.")
        return

    remote=_c3l2_s10_remote()
    if remote or saved.get("c3l2_s10_submitted"):
        row=(remote or {}).get("row",{}); payload=(remote or {}).get("payload",{})
        if not isinstance(payload,dict) or not payload:
            payload=saved.get("c3l2_s10_submission_payload",{}) if isinstance(saved.get("c3l2_s10_submission_payload"),dict) else {}
        reviewed=bool(row and (row.get("status")=="reviewed" or row.get("teacher_score") is not None))
        score=row.get("teacher_score") if reviewed else None

        st.success("Evaluación entregada.")
        if reviewed:
            st.metric("Puntaje oficial",f"{float(score):g}/60")
        else:
            st.info("Pendiente de revisión docente. La entrega permanece bloqueada en modo solo lectura.")

        st.write(f"**Intersección:** {payload.get('principal') or '—'} / {payload.get('secondary') or '—'}")
        st.write(f"**Sector:** {payload.get('sector') or '—'}")
        st.write(f"**Aplicación utilizada:** {payload.get('app_name') or '—'}")
        st.write(f"**Intervalo del mapa:** {payload.get('map_interval') or '—'} dB")
        rows=payload.get("measurements") or []
        st.write(f"**Registros entregados:** {len(rows)}/18")
        if rows:
            st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.write(f"**Metodología:** {payload.get('methodology') or '—'}")
        st.write(f"**Análisis:** {payload.get('analysis') or '—'}")
        st.write(f"**Limitaciones:** {payload.get('limitations') or '—'}")
        st.write(f"**Conclusión:** {payload.get('conclusion') or '—'}")
        return

    data=saved.get("c3l2_stage10") if isinstance(saved.get("c3l2_stage10"),dict) else {}
    data=dict(data or {})

    st.markdown("""
    <div class="c3l2-intro">
      <div class="c3l2-k">EVALUACIÓN APLICADA · 60 PUNTOS</div>
      <div class="c3l2-title">Medición de ruido de tráfico vehicular en una intersección real</div>
      <p style="margin:.45rem 0 .75rem">
        Debes realizar una campaña real de medición en una intersección formada por una <b>vía principal</b> y una <b>vía secundaria</b>,
        registrar <b>18 mediciones</b> y construir con ellas un mapa vial georreferenciado.
      </p>
      <div style="font-weight:800;margin-bottom:.35rem">Qué debes hacer</div>
      <ol style="margin:.15rem 0 .8rem 1.25rem;padding:0;line-height:1.5">
        <li>Selecciona una intersección real e identifica cuál corresponde a la vía principal y cuál a la vía secundaria.</li>
        <li>Define el centro de la intersección como referencia de inicio y registra sus coordenadas.</li>
        <li>Realiza <b>9 mediciones consecutivas en la vía principal</b> y <b>9 en la vía secundaria</b>.</li>
        <li>Los 9 puntos de cada vía deben seguir <b>una misma línea de recorrido</b>; no se distribuyen enfrentados entre ambas veredas.</li>
        <li>Entre un punto y el siguiente avanza aproximadamente <b>25–30 pasos normales</b> y registra la cantidad real recorrida.</li>
        <li>En cada punto registra <b>Leq, Lmax, hora, coordenadas GPS y una observación breve</b> del tránsito o de algún evento relevante.</li>
        <li>Al finalizar, revisa el mapa vial automático, analiza las diferencias entre ambas vías y redacta tus limitaciones y conclusión técnica.</li>
      </ol>
      <div style="font-weight:800;margin-bottom:.35rem">Cómo debes medir</div>
      <ul style="margin:.15rem 0 0 1.25rem;padding:0;line-height:1.5">
        <li>Realiza la medición desde un lugar <b>seguro, fuera de la calzada</b>. No debes ubicarte en medio de la calle.</li>
        <li>Usa el <b>Sonómetro del Diplomado</b> y mantén el teléfono en una posición y orientación similares durante toda la campaña.</li>
        <li>En cada punto observa el Leq hasta que la lectura se encuentre <b>estabilizada dentro de un rango aproximado de 2 dB</b>; luego registra Leq y Lmax.</li>
        <li>Evita tapar el micrófono o medir con el teléfono pegado al cuerpo, y anota eventos que puedan alterar la lectura, como bocinas, sirenas, buses detenidos u obras.</li>
        <li>Guarda la <b>coordenada real del lugar donde mediste</b>. La plataforma conservará ese dato y, para el mapa, desplazará gráficamente el punto hacia el eje de la vía.</li>
      </ul>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 1. Lugar de medición y evidencias")
    c1,c2=st.columns(2)
    principal=c1.text_input("Vía principal",value=data.get("principal",""),key="c3l2_s10_mainroad")
    secondary=c2.text_input("Vía secundaria",value=data.get("secondary",""),key="c3l2_s10_secondary")
    sector=st.text_input("Sector / comuna / ciudad",value=data.get("sector",""),key="c3l2_s10_sector")
    st.caption("Para que el mapa quede sobre la ubicación real, registra también el centro de la intersección y las coordenadas GPS de cada punto de medición.")
    g1,g2=st.columns(2)
    intersection_lat=g1.number_input(
        "Latitud centro de la intersección",
        min_value=-90.0,max_value=90.0,
        value=float(data.get("intersection_lat") or 0.0),
        step=0.000001,format="%.6f",key="c3l2_s10_intersection_lat",
        help="Coordenada del centro geométrico aproximado del cruce. Se usa como ancla para llevar los puntos al eje de cada vía en el mapa."
    )
    intersection_lon=g2.number_input(
        "Longitud centro de la intersección",
        min_value=-180.0,max_value=180.0,
        value=float(data.get("intersection_lon") or 0.0),
        step=0.000001,format="%.6f",key="c3l2_s10_intersection_lon",
        help="Coordenada del centro geométrico aproximado del cruce."
    )
    site_description=st.text_area(
        "Descripción breve del lugar y su entorno",
        value=data.get("site_description",""),
        height=90,
        key="c3l2_s10_site_desc",
        placeholder="Describe tipo de vías, edificaciones, flujo aparente, superficies, obstáculos y elementos relevantes."
    )
    e1,e2=st.columns(2)
    maps_url=e1.text_input(
        "Enlace de ubicación / imagen satelital",
        value=data.get("maps_url",""),
        placeholder="Google Maps / Google Earth u otro enlace compartido",
        key="c3l2_s10_maps_url",
    )
    evidence_url=e2.text_input(
        "Enlace a fotografías y capturas de la aplicación",
        value=data.get("evidence_url",""),
        placeholder="Carpeta compartida con fotos y pantallazos",
        key="c3l2_s10_evidence_url",
    )

    st.markdown("### 2. Metodología de la campaña")
    st.markdown(
        """
        <div class="c3l2-card blue" style="margin-bottom:.75rem">
          <div class="c3l2-k">INSTRUMENTO DE MEDICIÓN</div>
          Utiliza el <b>Sonómetro del Diplomado</b> para registrar Leq y Lmax en cada punto.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(
        "🎚️ Abrir Sonómetro del Diplomado",
        "https://soundlevelmeteruc.vercel.app/",
        use_container_width=True,
    )
    m1,m2,m3=st.columns(3)
    app_name=m1.text_input(
        "Aplicación utilizada",
        value=data.get("app_name") or "Sonómetro del Diplomado UC",
        placeholder="Ej.: Sonómetro del Diplomado UC",
        key="c3l2_s10_app"
    )
    measurement_date=m2.text_input("Fecha de medición",value=data.get("measurement_date",""),placeholder="dd-mm-aaaa",key="c3l2_s10_date")
    period=m3.text_input("Periodo / horario",value=data.get("period",""),placeholder="Ej.: 18:00–19:00",key="c3l2_s10_period")

    st.markdown("""
    <div class="c3l2-grid2">
      <div class="c3l2-card blue">
        <div class="c3l2-k">RED DE MEDICIÓN</div>
        <b>18 registros en total</b><br>
        9 puntos asociados a la vía principal y 9 a la vía secundaria.
      </div>
      <div class="c3l2-card green">
        <div class="c3l2-k">SEPARACIÓN</div>
        <b>25–30 pasos normales</b><br>
        El origen de la secuencia corresponde a la intersección de ambas vías.
      </div>
      <div class="c3l2-card orange">
        <div class="c3l2-k">DESCRIPTORES</div>
        <b>Leq + Lmax</b><br>
        Registra ambos valores para cada punto utilizando el criterio de estabilización definido.
      </div>
      <div class="c3l2-card">
        <div class="c3l2-k">ESTABILIZACIÓN</div>
        <b>Criterio de 2 dB</b><br>
        Describe cómo verificaste la estabilización antes de cerrar cada registro.
      </div>
    </div>
    """,unsafe_allow_html=True)

    methodology=st.text_area(
        "Describe cómo realizaste las mediciones y cómo aplicaste el criterio de estabilización de 2 dB",
        value=data.get("methodology",""),
        height=125,
        key="c3l2_s10_method",
        placeholder="Incluye posición del teléfono, secuencia de puntos, duración aproximada, lectura de Leq/Lmax y criterio usado para considerar estable el registro."
    )

    st.markdown("### 3. Registra los 18 puntos")

    components.html("""
<div style="font-family:Arial,sans-serif;color:#243447;border:1px solid #dbe5ec;border-radius:16px;padding:18px 18px 14px;background:#fbfdff;box-sizing:border-box">
  <div style="font-size:12px;font-weight:800;letter-spacing:.05em;color:#0b4f83;margin-bottom:4px">EJEMPLO · CÓMO DISTRIBUIR LOS PUNTOS</div>
  <div style="font-size:17px;font-weight:800;margin-bottom:8px">Parte desde la intersección y sigue cada vía por separado</div>
  <div style="font-size:14px;line-height:1.5;color:#425466;margin-bottom:12px">
    Los puntos <b>P1–P9</b> corresponden a la <b>vía principal</b> y los puntos <b>S1–S9</b> a la <b>vía secundaria</b>. Todos los puntos de una misma vía se representan sobre <b>un único eje longitudinal</b>.
    Entre puntos consecutivos camina aproximadamente <b>25–30 pasos normales</b> y registra la cantidad real recorrida.
  </div>
  <svg viewBox="0 0 860 430" role="img" aria-label="Esquema de una intersección con nueve puntos P sobre la vía principal y nueve puntos S sobre la vía secundaria, todos alineados sobre el eje de cada vía" style="width:100%;height:auto;display:block">
    <defs>
      <filter id="c3l2-shadow-fix" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#0f172a" flood-opacity=".14"/>
      </filter>
    </defs>
    <rect x="18" y="20" width="824" height="388" rx="18" fill="#f4f8fb" stroke="#d8e4ec"/>
    <rect x="36" y="196" width="788" height="82" rx="10" fill="#dfe7ec"/>
    <rect x="366" y="40" width="110" height="348" rx="10" fill="#e7edf1"/>
    <line x1="48" y1="237" x2="812" y2="237" stroke="#94a3b8" stroke-width="3" stroke-dasharray="14 12"/>
    <line x1="421" y1="52" x2="421" y2="376" stroke="#94a3b8" stroke-width="3" stroke-dasharray="14 12"/>
    <rect x="54" y="208" width="150" height="30" rx="15" fill="#ffffff" stroke="#cbd5e1"/>
    <text x="129" y="228" text-anchor="middle" font-size="15" font-weight="800" fill="#0f4c74">VÍA PRINCIPAL</text>
    <g transform="translate(449,128) rotate(-90)">
      <rect x="-79" y="-16" width="158" height="32" rx="16" fill="#ffffff" stroke="#cbd5e1"/>
      <text x="0" y="5" text-anchor="middle" font-size="15" font-weight="800" fill="#6b3f10">VÍA SECUNDARIA</text>
    </g>
    <circle cx="421" cy="237" r="23" fill="#ffffff" stroke="#334155" stroke-width="2.5" filter="url(#c3l2-shadow-fix)"/>
    <text x="421" y="233" text-anchor="middle" font-size="11" font-weight="800" fill="#0f172a">INICIO</text>
    <text x="421" y="248" text-anchor="middle" font-size="9.5" fill="#475569">intersección</text>
    <line x1="454" y1="174" x2="500" y2="174" stroke="#475569" stroke-width="1.8"/>
    <polygon points="454,174 463,169 463,179" fill="#475569"/>
    <polygon points="500,174 491,169 491,179" fill="#475569"/>
    <text x="477" y="163" text-anchor="middle" font-size="11.5" font-weight="700" fill="#334155">25–30 pasos aprox.</text>
    <g font-family="Arial,sans-serif" font-size="10.5" font-weight="800" text-anchor="middle">
      <g fill="#0b78b4" stroke="#ffffff" stroke-width="2">
        <circle cx="474" cy="190" r="15"/><circle cx="515" cy="190" r="15"/><circle cx="556" cy="190" r="15"/>
        <circle cx="597" cy="190" r="15"/><circle cx="638" cy="190" r="15"/><circle cx="679" cy="190" r="15"/>
        <circle cx="720" cy="190" r="15"/><circle cx="761" cy="190" r="15"/><circle cx="802" cy="190" r="15"/>
      </g>
      <g fill="#ffffff">
        <text x="474" y="194">P1</text><text x="515" y="194">P2</text><text x="556" y="194">P3</text>
        <text x="597" y="194">P4</text><text x="638" y="194">P5</text><text x="679" y="194">P6</text>
        <text x="720" y="194">P7</text><text x="761" y="194">P8</text><text x="802" y="194">P9</text>
      </g>
      <g fill="#d97706" stroke="#ffffff" stroke-width="2">
        <circle cx="350" cy="182" r="15"/><circle cx="350" cy="166" r="15"/><circle cx="350" cy="150" r="15"/>
        <circle cx="350" cy="134" r="15"/><circle cx="350" cy="118" r="15"/><circle cx="350" cy="102" r="15"/>
        <circle cx="350" cy="86" r="15"/><circle cx="350" cy="70" r="15"/><circle cx="350" cy="54" r="15"/>
      </g>
      <g fill="#ffffff">
        <text x="350" y="186">S1</text><text x="350" y="170">S2</text><text x="350" y="154">S3</text>
        <text x="350" y="138">S4</text><text x="350" y="122">S5</text><text x="350" y="106">S6</text>
        <text x="350" y="90">S7</text><text x="350" y="74">S8</text><text x="350" y="58">S9</text>
      </g>
    </g>
    <g font-family="Arial,sans-serif" fill="#334155">
      <rect x="62" y="314" width="324" height="68" rx="12" fill="#ffffff" stroke="#dbe5ec"/>
      <circle cx="88" cy="338" r="8" fill="#0b78b4"/>
      <text x="105" y="343" font-size="13" font-weight="800">P1–P9 · vía principal</text>
      <text x="88" y="365" font-size="11.5">Registra Leq, Lmax, hora, observación y pasos reales.</text>
      <rect x="474" y="314" width="324" height="68" rx="12" fill="#ffffff" stroke="#dbe5ec"/>
      <circle cx="500" cy="338" r="8" fill="#d97706"/>
      <text x="517" y="343" font-size="13" font-weight="800">S1–S9 · vía secundaria</text>
      <text x="500" y="365" font-size="11.5">Los 9 puntos se mantienen sobre la misma línea de la vía; no se ubican enfrentados en ambas veredas.</text>
    </g>
  </svg>
  <div style="margin-top:10px;padding:10px 12px;border-radius:10px;background:#eef7fb;color:#23435a;font-size:13px;line-height:1.45">
    <b>Ejemplo de un registro:</b> P1 · 28 pasos · Leq 68,4 dB(A) · Lmax 76,2 dB(A) · 10:32 · “tránsito vehicular continuo”.
    El valor de pasos es solo un ejemplo: debes ingresar lo que efectivamente recorriste.
  </div>
</div>
""", height=610, scrolling=False)

    previous=data.get("measurements") if isinstance(data.get("measurements"),list) and len(data.get("measurements"))==18 else None
    if previous:
        measurement_df=pd.DataFrame(previous)
        legacy_steps=(
            "Pasos desde punto anterior" in measurement_df.columns
            and len(measurement_df)==18
            and all(v==27 for v in measurement_df["Pasos desde punto anterior"].tolist())
            and all(pd.isna(v) for v in measurement_df.get("Leq [dB(A)]",pd.Series([None]*18)).tolist())
            and all(pd.isna(v) for v in measurement_df.get("Lmax [dB(A)]",pd.Series([None]*18)).tolist())
        )
        if legacy_steps:
            measurement_df["Pasos desde punto anterior"]=None
        if "Latitud" not in measurement_df.columns:
            measurement_df["Latitud"]=None
        if "Longitud" not in measurement_df.columns:
            measurement_df["Longitud"]=None
    else:
        rows=[]
        for route,prefix in [("Vía principal","P"),("Vía secundaria","S")]:
            for n in range(1,10):
                rows.append({
                    "Punto":f"{prefix}{n}",
                    "Vía":route,
                    "Pasos desde punto anterior":None,
                    "Latitud":None,
                    "Longitud":None,
                    "Leq [dB(A)]":None,
                    "Lmax [dB(A)]":None,
                    "Hora":"",
                    "Observación":"",
                })
        measurement_df=pd.DataFrame(rows)

    edited=st.data_editor(
        measurement_df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Punto","Vía"],
        column_config={
            "Punto":st.column_config.TextColumn("Punto",width="small"),
            "Vía":st.column_config.TextColumn("Vía",width="medium"),
            "Pasos desde punto anterior":st.column_config.NumberColumn("Pasos",min_value=1,max_value=100,step=1,width="small"),
            "Latitud":st.column_config.NumberColumn("Latitud",min_value=-90.0,max_value=90.0,step=0.000001,format="%.6f",help="Coordenada GPS real del lugar donde realizaste la medición."),
            "Longitud":st.column_config.NumberColumn("Longitud",min_value=-180.0,max_value=180.0,step=0.000001,format="%.6f",help="Coordenada GPS real del lugar donde realizaste la medición."),
            "Leq [dB(A)]":st.column_config.NumberColumn("Leq [dB(A)]",min_value=30.0,max_value=120.0,step=0.1,format="%.1f"),
            "Lmax [dB(A)]":st.column_config.NumberColumn("Lmax [dB(A)]",min_value=30.0,max_value=140.0,step=0.1,format="%.1f"),
            "Hora":st.column_config.TextColumn("Hora",width="small"),
            "Observación":st.column_config.TextColumn("Observación",width="large"),
        },
        key="c3l2_s10_editor",
    )

    def _c3l2_s10_clean_value(v):
        if v is None:
            return None
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        if isinstance(v,(np.integer,np.floating)):
            return v.item()
        return v

    measurements=[]
    for row in edited.to_dict("records"):
        measurements.append({k:_c3l2_s10_clean_value(v) for k,v in row.items()})

    complete=[
        r for r in measurements
        if isinstance(r.get("Leq [dB(A)]"),(int,float))
        and isinstance(r.get("Lmax [dB(A)]"),(int,float))
    ]
    spacing_ok=sum(
        1 for r in measurements
        if isinstance(r.get("Pasos desde punto anterior"),(int,float))
        and 25<=float(r.get("Pasos desde punto anterior"))<=30
    )

    geocoded=[
        r for r in measurements
        if isinstance(r.get("Latitud"),(int,float)) and isinstance(r.get("Longitud"),(int,float))
        and -90<=float(r.get("Latitud"))<=90 and -180<=float(r.get("Longitud"))<=180
        and not (abs(float(r.get("Latitud")))<1e-9 and abs(float(r.get("Longitud")))<1e-9)
    ]
    q1,q2,q3,q4=st.columns(4)
    q1.metric("Registros completos",f"{len(complete)}/18")
    q2.metric("Separaciones 25–30 pasos",f"{spacing_ok}/18")
    q3.metric("Coordenadas GPS",f"{len(geocoded)}/18")
    q4.metric("Cobertura","2 vías" if len({r.get("Vía") for r in complete})==2 else "Incompleta")

    st.markdown("### 4. Mapa vial georreferenciado automático")
    st.markdown(
        """
        <div class="c3l2-card blue" style="margin-bottom:.8rem">
          <div class="c3l2-k">MAPA SOBRE UBICACIÓN REAL</div>
          <b>La coordenada medida se conserva como evidencia.</b><br>
          Para representar el ruido de la vía, la plataforma proyecta cada punto GPS hacia un <b>eje vial estimado</b> que pasa por el centro de la intersección. Así, el color se dibuja sobre la calzada y no sobre la vereda donde se sostuvo el teléfono.
        </div>
        """,
        unsafe_allow_html=True,
    )
    interval=st.radio(
        "Intervalo de representación",
        [5,3],
        horizontal=True,
        format_func=lambda x:f"{x} dB",
        index=0 if data.get("map_interval",5)!=3 else 1,
        key="c3l2_s10_interval",
    )

    from views.measurement_map import render_road_map
    valid_levels, center_ok = render_road_map(
        complete, intersection_lat, intersection_lon, interval,
        key="c3l2_s10_real_roadmap",
    )

    st.markdown("### 5. Análisis de resultados")
    if valid_levels:
        lmax_values=[float(r["Lmax [dB(A)]"]) for r in complete if isinstance(r.get("Lmax [dB(A)]"),(int,float))]
        a,b,c8=st.columns(3)
        a.metric("Leq máximo",f"{max(valid_levels):.1f} dB(A)")
        b.metric("Leq mínimo",f"{min(valid_levels):.1f} dB(A)")
        c8.metric("Rango Leq",f"{max(valid_levels)-min(valid_levels):.1f} dB")
        if lmax_values:
            st.caption(f"Lmax observado: {min(lmax_values):.1f} a {max(lmax_values):.1f} dB(A).")

    analysis=st.text_area(
        "Analiza el comportamiento observado en ambas vías",
        value=data.get("analysis",""),
        height=150,
        key="c3l2_s10_analysis",
        placeholder="Compara vía principal y secundaria, tendencia con la distancia, diferencias Leq/Lmax, eventos relevantes y lo que muestran los intervalos del mapa."
    )
    limitations=st.text_area(
        "Limitaciones e incertidumbres",
        value=data.get("limitations",""),
        height=110,
        key="c3l2_s10_limitations",
        placeholder="Considera precisión de la aplicación, duración, variabilidad del tránsito, meteorología, eventos puntuales, conteo de pasos y representatividad temporal."
    )
    conclusion=st.text_area(
        "Conclusión técnica",
        value=data.get("conclusion",""),
        height=125,
        key="c3l2_s10_conclusion",
        placeholder="Resume el patrón acústico observado y el alcance real de los resultados."
    )

    st.markdown("### 6. Revisión antes de entregar")
    checklist=[
        ("Lugar identificado",bool(principal.strip() and secondary.strip() and sector.strip())),
        ("Evidencias enlazadas",bool(maps_url.strip() and evidence_url.strip())),
        ("Metodología desarrollada",len(methodology.strip())>=100),
        ("18 registros Leq/Lmax completos",len(complete)==18),
        ("18 separaciones entre 25 y 30 pasos",spacing_ok==18),
        ("18 puntos con coordenadas GPS",len(geocoded)==18),
        ("Centro de la intersección georreferenciado",center_ok),
        ("Análisis desarrollado",len(analysis.strip())>=150),
        ("Limitaciones desarrolladas",len(limitations.strip())>=80),
        ("Conclusión desarrollada",len(conclusion.strip())>=100),
    ]
    for label,ok in checklist:
        st.write(("✅ " if ok else "○ ")+label)

    if st.button("💾 Guardar borrador",use_container_width=True,key="c3l2_s10_draft"):
        data.update({
            "principal":principal,"secondary":secondary,"sector":sector,
            "intersection_lat":intersection_lat,"intersection_lon":intersection_lon,
            "site_description":site_description,"maps_url":maps_url,"evidence_url":evidence_url,
            "app_name":app_name,"measurement_date":measurement_date,"period":period,
            "methodology":methodology,"measurements":measurements,"map_interval":interval,
            "analysis":analysis,"limitations":limitations,"conclusion":conclusion,
        })
        saved["c3l2_stage10"]=data
        _c3l2_save(saved)
        st.success("Borrador guardado. Puedes salir y continuar después.")

    if st.button("ENTREGAR EVALUACIÓN DEFINITIVA",type="primary",use_container_width=True,key="c3l2_s10_submit"):
        if not all(ok for _,ok in checklist):
            st.warning("Aún faltan antecedentes obligatorios. Revisa la lista antes de realizar el envío definitivo.")
        elif not app_name.strip() or not measurement_date.strip() or not period.strip():
            st.warning("Completa aplicación utilizada, fecha y periodo de medición.")
        elif len(site_description.strip())<80:
            st.warning("Desarrolla con mayor detalle la descripción del lugar.")
        else:
            payload={
                "version":2,
                "principal":principal,"secondary":secondary,"sector":sector,
                "intersection_lat":intersection_lat,"intersection_lon":intersection_lon,
                "site_description":site_description,
                "maps_url":maps_url,"evidence_url":evidence_url,
                "app_name":app_name,"measurement_date":measurement_date,"period":period,
                "methodology":methodology,
                "measurements":measurements,
                "map_interval":interval,
                "analysis":analysis,"limitations":limitations,"conclusion":conclusion,
                "rubric_max":60,
                "submitted_at":_now(),
            }
            _c3l2_s10_submit(saved,payload)
            st.rerun()


def _render_course3_lab2_stage0(lab,saved): return _c3l2_stage0(lab,saved)
def _render_course3_lab2_stage1(lab,saved): return _c3l2_stage1(lab,saved)
def _render_course3_lab2_stage2(lab,saved): return _c3l2_stage2(lab,saved)
def _render_course3_lab2_stage3(lab,saved): return _c3l2_stage3(lab,saved)
def _render_course3_lab2_stage4(lab,saved): return _c3l2_stage4(lab,saved)
def _render_course3_lab2_stage5(lab,saved): return _c3l2_stage5(lab,saved)
def _render_course3_lab2_stage6(lab,saved): return _c3l2_stage6(lab,saved)
def _render_course3_lab2_stage7(lab,saved): return _c3l2_stage7(lab,saved)
def _render_course3_lab2_stage8(lab,saved): return _c3l2_stage8(lab,saved)
def _render_course3_lab2_stage9(lab,saved): return _c3l2_stage9(lab,saved)
def _render_course3_lab2_stage10(lab,saved): return _c3l2_stage10(lab,saved)

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

        # Navegación principal por propósito.
        # Evitamos radios pequeños y mantenemos intacta la navegación de etapas.
        future_view_key=f"future_main_view_{class_id}"
        future_options=["🏠 Mis clases", results_view_label, current_lab_label]
        if st.session_state.get(future_view_key) not in future_options:
            st.session_state[future_view_key]=current_lab_label

        role_now=st.session_state.get("role","Alumno")

        # Navegación principal con radio buttons dentro de tarjetas. Al estar
        # dentro del laboratorio, la tercera opción se muestra seleccionada.
        active_view=current_lab_label

        st.markdown(
            """
        <style>
        /* Navegación principal: radio buttons contenidos en tarjetas */
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) > div[role="radiogroup"] {
            gap: .44rem;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) > div[role="radiogroup"] > label {
            width: 100%;
            margin: 0;
            padding: .62rem .68rem;
            border: 1px solid rgba(142, 221, 242, .28);
            border-radius: 12px;
            background: rgba(12, 73, 112, .30);
            transition: background .16s ease, border-color .16s ease, box-shadow .16s ease, transform .08s ease;
            cursor: pointer;
            align-items: flex-start;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) > div[role="radiogroup"] > label:hover {
            background: rgba(21, 111, 160, .34);
            border-color: rgba(89, 212, 239, .58);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) > div[role="radiogroup"] > label:active {
            transform: translateY(1px);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) > div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg, rgba(8, 94, 143, .72), rgba(12, 125, 166, .52));
            border-color: #59d4ef;
            box-shadow: inset 3px 0 0 #59d4ef, 0 0 0 1px rgba(89, 212, 239, .08);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) input[type="radio"] {
            accent-color: #59d4ef;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) [data-testid="stMarkdownContainer"] p {
            font-weight: 700;
            line-height: 1.22;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Navegación principal"]) [data-testid="stCaptionContainer"] {
            color: #a9cada;
            font-size: .69rem;
            line-height: 1.18;
            margin-top: .12rem;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Ruta de aprendizaje: tarjetas-radio compactas para Alumno y Docente.
        # Mantiene el mismo lenguaje visual de la navegación principal, sin
        # modificar la lógica ni el estado guardado de cada etapa.
        st.markdown(
            """
        <style>
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [role="radiogroup"] {
            gap: .34rem !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [role="radiogroup"] > label {
            width: 100% !important;
            margin: 0 !important;
            padding: .48rem .56rem !important;
            border: 1px solid rgba(142,221,242,.20) !important;
            border-radius: 10px !important;
            background: rgba(12,73,112,.22) !important;
            transition: background .15s ease,border-color .15s ease,box-shadow .15s ease,transform .08s ease !important;
            cursor: pointer !important;
            align-items: flex-start !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [role="radiogroup"] > label:hover {
            background: rgba(21,111,160,.30) !important;
            border-color: rgba(89,212,239,.48) !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [role="radiogroup"] > label:active {
            transform: translateY(1px);
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg,rgba(8,94,143,.62),rgba(12,125,166,.42)) !important;
            border-color: #59d4ef !important;
            box-shadow: inset 3px 0 0 #59d4ef,0 0 0 1px rgba(89,212,239,.06) !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [data-baseweb="radio"] {
            display:flex !important;
            opacity:1 !important;
            visibility:visible !important;
            flex:0 0 auto !important;
            margin-top:.05rem !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] input[type="radio"] {
            accent-color:#59d4ef !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-future_stage_"] [data-testid="stMarkdownContainer"] p {
            font-size:.75rem !important;
            font-weight:650 !important;
            line-height:1.28 !important;
            text-align:left !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            r"""
    <style>
    /* =========================================================
       SIDEBAR · ANCHO Y ALTO REALMENTE UNIFORMES
       Fuerza también wrappers internos de BaseWeb/Streamlit.
       ========================================================= */

    section[data-testid="stSidebar"] {
        --future-card-height: 64px;
    }

    /* Todo el árbol del radio ocupa el ancho disponible */
    section[data-testid="stSidebar"] div[data-testid="stRadio"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > div,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-baseweb="radio"] {
        width:100% !important;
        max-width:100% !important;
        min-width:0 !important;
        box-sizing:border-box !important;
        align-self:stretch !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
        display:flex !important;
        flex-direction:column !important;
        align-items:stretch !important;
        gap:.48rem !important;
    }

    /* La tarjeta real es el componente BaseWeb del radio */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label[data-baseweb="radio"],
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > label,
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > div > label {
        width:100% !important;
        max-width:100% !important;
        min-width:100% !important;
        flex:0 0 100% !important;

        height:var(--future-card-height) !important;
        min-height:var(--future-card-height) !important;
        max-height:var(--future-card-height) !important;

        margin:0 !important;
        padding:.60rem .70rem !important;
        box-sizing:border-box !important;

        display:flex !important;
        align-items:center !important;
        justify-content:flex-start !important;
        gap:.50rem !important;

        border:1px solid rgba(94,194,225,.52) !important;
        border-radius:11px !important;
        background:linear-gradient(
            135deg,
            rgba(8,58,92,.70),
            rgba(10,79,117,.48)
        ) !important;
        box-shadow:0 2px 7px rgba(0,0,0,.08) !important;
        overflow:hidden !important;
    }

    /* Hover */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover,
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > div > label:hover {
        background:linear-gradient(
            135deg,
            rgba(13,85,128,.82),
            rgba(15,111,151,.58)
        ) !important;
        border-color:rgba(89,212,239,.90) !important;
    }

    /* Seleccionado */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] div[role="radiogroup"] > div > label:has(input:checked) {
        background:linear-gradient(
            135deg,
            rgba(4,104,154,.96),
            rgba(13,140,179,.76)
        ) !important;
        border-color:#69ddf3 !important;
        box-shadow:
            inset 4px 0 0 #69ddf3,
            0 4px 12px rgba(0,0,0,.12) !important;
    }

    /* Contenido textual: siempre usa todo el espacio restante */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
        width:100% !important;
        max-width:100% !important;
        min-width:0 !important;
        flex:1 1 0 !important;
        display:flex !important;
        align-items:center !important;
        box-sizing:border-box !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        width:100% !important;
        max-width:100% !important;
        min-width:0 !important;
        margin:0 !important;
        color:#fff !important;
        font-size:.75rem !important;
        font-weight:700 !important;
        line-height:1.22 !important;
        white-space:normal !important;
        overflow-wrap:anywhere !important;
        text-align:left !important;
    }

    /* Radio visible con ancho reservado idéntico */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
        flex:0 0 16px !important;
        width:16px !important;
        height:16px !important;
        margin:0 !important;
        accent-color:#69ddf3 !important;
    }

    /* Ambos paneles exteriores ocupan el mismo ancho */
    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlockBorderWrapper"] {
        width:100% !important;
        max-width:100% !important;
        min-width:0 !important;
        box-sizing:border-box !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        width:100% !important;
        max-width:100% !important;
        min-width:0 !important;
        box-sizing:border-box !important;
    }

    /* Captions no alteran el ancho de la tarjeta */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] [data-testid="stCaptionContainer"] {
        width:100% !important;
        max-width:100% !important;
        box-sizing:border-box !important;
    }
    </style>
""",
            unsafe_allow_html=True,
        )

        nav_titles={
            "🏠 Mis clases":"📚  Mis clases",
            results_view_label:(
                "📝  Evaluaciones entregadas"
                if role_now=="Docente"
                else "📊  Mi desempeño"
            ),
            current_lab_label:(
                f"🧪  Laboratorio {lab['number']}"
                if role_now=="Docente"
                else "🧪  Laboratorios y actividades"
            ),
        }
        nav_captions=[
            "Cursos y laboratorios",
            (
                "Respuestas y puntajes"
                if role_now=="Docente"
                else "Evaluaciones, notas y avance formativo"
            ),
            (
                "Ruta y actividades del laboratorio actual"
                if role_now=="Docente"
                else "Ruta, ejercicios y progreso"
            ),
        ]
        nav_key=f"future_nav_radio_{class_id}"
        if st.session_state.get(nav_key) not in future_options:
            st.session_state[nav_key]=current_lab_label

        # Navegación principal mediante radio buttons dentro de tarjetas.
        st.markdown(
            """
            <style>
            /* =====================================================
               RADIO CARDS · NAVEGACIÓN Y RUTA DE APRENDIZAJE
               ===================================================== */
            section[data-testid="stSidebar"] div[role="radiogroup"] {
                display:flex !important;
                flex-direction:column !important;
                gap:.48rem !important;
                width:100% !important;
            }

            /* Cada opción completa se transforma visualmente en tarjeta */
            section[data-testid="stSidebar"] div[role="radiogroup"] label {
                box-sizing:border-box !important;
                width:100% !important;
                min-height:48px !important;
                margin:0 !important;
                padding:.62rem .72rem !important;

                border:1px solid rgba(94,194,225,.46) !important;
                border-radius:11px !important;
                background:linear-gradient(
                    135deg,
                    rgba(8,58,92,.62),
                    rgba(10,79,117,.42)
                ) !important;

                display:flex !important;
                align-items:flex-start !important;
                gap:.48rem !important;
                cursor:pointer !important;

                box-shadow:0 2px 7px rgba(0,0,0,.08) !important;
                transition:
                    background .16s ease,
                    border-color .16s ease,
                    box-shadow .16s ease,
                    transform .10s ease !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background:linear-gradient(
                    135deg,
                    rgba(13,85,128,.76),
                    rgba(15,111,151,.52)
                ) !important;
                border-color:rgba(89,212,239,.88) !important;
                box-shadow:0 4px 12px rgba(0,0,0,.12) !important;
                transform:translateY(-1px) !important;
            }

            /* Seleccionado */
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background:linear-gradient(
                    135deg,
                    rgba(4,104,154,.95),
                    rgba(13,140,179,.72)
                ) !important;
                border-color:#69ddf3 !important;
                box-shadow:
                    inset 4px 0 0 #69ddf3,
                    0 4px 13px rgba(0,0,0,.13) !important;
            }

            /* Radio visible */
            section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
                accent-color:#69ddf3 !important;
                transform:scale(1.10) !important;
                margin-top:.12rem !important;
                flex:0 0 auto !important;
            }

            /* Texto */
            section[data-testid="stSidebar"] div[role="radiogroup"]
            [data-testid="stMarkdownContainer"] {
                flex:1 1 auto !important;
                min-width:0 !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"]
            [data-testid="stMarkdownContainer"] p {
                margin:0 !important;
                color:#fff !important;
                font-size:.79rem !important;
                font-weight:720 !important;
                line-height:1.30 !important;
                text-align:left !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"]
            [data-testid="stCaptionContainer"] {
                color:#b8d9e8 !important;
                font-size:.69rem !important;
                line-height:1.20 !important;
                margin-top:.14rem !important;
            }

            /* Navegación principal: tarjetas más altas */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_nav_radio_"] div[role="radiogroup"] label {
                min-height:58px !important;
                padding:.72rem .78rem !important;
                border-radius:12px !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_nav_radio_"] div[role="radiogroup"]
            [data-testid="stMarkdownContainer"] p {
                font-size:.82rem !important;
                font-weight:760 !important;
            }

            /* Etapas: compactas pero claramente enmarcadas */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] div[role="radiogroup"] {
                gap:.42rem !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] div[role="radiogroup"] label {
                min-height:46px !important;
                padding:.58rem .66rem !important;
                border-radius:10px !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] div[role="radiogroup"]
            [data-testid="stMarkdownContainer"] p {
                font-size:.77rem !important;
                font-weight:680 !important;
                line-height:1.28 !important;
            }

            /* Fallback amplio: Streamlit puede no conservar st-key en ciertas versiones */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"] div[role="radiogroup"] label {
                border:1px solid rgba(94,194,225,.46) !important;
                border-radius:11px !important;
            }

            /* =====================================================
               AJUSTE DE ALINEACIÓN · MISMO ANCHO EN TODAS LAS TARJETAS
               ===================================================== */
            section[data-testid="stSidebar"] div[data-testid="stRadio"],
            section[data-testid="stSidebar"] div[data-testid="stRadio"] > div,
            section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
                width:100% !important;
                max-width:100% !important;
                box-sizing:border-box !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label {
                width:100% !important;
                max-width:100% !important;
                flex:0 0 100% !important;
                box-sizing:border-box !important;
            }

            /* Texto ocupa el espacio disponible sin achicar la tarjeta */
            section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label
            [data-testid="stMarkdownContainer"] {
                width:100% !important;
                max-width:100% !important;
                flex:1 1 auto !important;
            }

            /* =====================================================
               BLOQUE COMPLETO · RUTA DE APRENDIZAJE
               ===================================================== */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] {
                width:100% !important;
                box-sizing:border-box !important;
                padding:.72rem .62rem .78rem !important;
                margin-top:.52rem !important;
                border:1px solid rgba(89,212,239,.28) !important;
                border-radius:14px !important;
                background:linear-gradient(
                    180deg,
                    rgba(7,48,77,.46),
                    rgba(7,43,70,.26)
                ) !important;
                box-shadow:0 5px 16px rgba(0,0,0,.08) !important;
            }

            /* Título Ruta de aprendizaje dentro del marco */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] > label,
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] > div:first-child {
                width:100% !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] [data-testid="stWidgetLabel"] {
                margin-bottom:.52rem !important;
                padding:.12rem .10rem .34rem !important;
                border-bottom:1px solid rgba(89,212,239,.20) !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] [data-testid="stWidgetLabel"] p {
                margin:0 !important;
                color:#e9f8ff !important;
                font-size:.80rem !important;
                font-weight:800 !important;
                letter-spacing:.01em !important;
            }

            /* Todas las etapas con misma altura mínima y alineación */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] div[role="radiogroup"] > label {
                min-height:48px !important;
                width:100% !important;
                padding:.59rem .66rem !important;
                display:flex !important;
                align-items:center !important;
            }

            /* Navegación principal alineada al mismo ancho */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_nav_radio_"] {
                width:100% !important;
            }

            section[data-testid="stSidebar"]
            div[class*="st-key-future_nav_radio_"] div[role="radiogroup"] > label {
                width:100% !important;
                min-height:58px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                """
                <div class="future-sidebar-panel-title">
                    <div class="future-sidebar-panel-kicker">NAVEGACIÓN</div>
                    <div class="future-sidebar-panel-subtitle">Accesos principales</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            selected_view=st.radio(
                "Navegación principal",
                future_options,
                index=future_options.index(current_lab_label),
                format_func=lambda option: nav_titles[option],
                captions=nav_captions,
                key=nav_key,
                label_visibility="collapsed",
                help="Selecciona el espacio al que quieres ir.",
            )

        # Ajuste final de estética del sidebar:
        # ambos grupos quedan en paneles equivalentes y todas las tarjetas
        # tienen exactamente el mismo ancho y alto.
        st.markdown(
            """
            <style>
            /* Paneles exteriores: Navegación y Ruta */
            section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
                width:100% !important;
                max-width:100% !important;
                box-sizing:border-box !important;
                border:1px solid rgba(89,212,239,.30) !important;
                border-radius:14px !important;
                background:linear-gradient(
                    180deg,
                    rgba(7,49,78,.56),
                    rgba(7,42,68,.34)
                ) !important;
                box-shadow:0 6px 18px rgba(0,0,0,.08) !important;
                overflow:hidden !important;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"] > div {
                padding:.72rem !important;
                box-sizing:border-box !important;
            }

            .future-sidebar-panel-title {
                padding:.08rem .08rem .62rem;
                margin-bottom:.58rem;
                border-bottom:1px solid rgba(89,212,239,.24);
            }
            .future-sidebar-panel-kicker {
                color:#f4fcff;
                font-size:1.00rem;
                font-weight:900;
                letter-spacing:.045em;
                line-height:1.15;
            }
            .future-sidebar-panel-subtitle {
                color:#a9ccdc;
                font-size:.72rem;
                font-weight:600;
                margin-top:.20rem;
                line-height:1.20;
            }

            /* El widget radio ocupa TODO el panel */
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[data-testid="stRadio"],
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] {
                width:100% !important;
                max-width:100% !important;
                box-sizing:border-box !important;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] {
                display:grid !important;
                grid-template-columns:minmax(0,1fr) !important;
                gap:.48rem !important;
                align-items:stretch !important;
            }

            /* Todas las tarjetas: MISMO ancho y MISMO alto */
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] > label {
                width:100% !important;
                max-width:100% !important;
                min-width:0 !important;
                height:64px !important;
                min-height:64px !important;
                max-height:64px !important;
                box-sizing:border-box !important;
                margin:0 !important;
                padding:.60rem .68rem !important;

                display:flex !important;
                align-items:center !important;
                gap:.48rem !important;

                border:1px solid rgba(94,194,225,.52) !important;
                border-radius:11px !important;
                background:linear-gradient(
                    135deg,
                    rgba(8,58,92,.70),
                    rgba(10,79,117,.48)
                ) !important;
                box-shadow:0 2px 7px rgba(0,0,0,.08) !important;
                overflow:hidden !important;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] > label:hover {
                background:linear-gradient(
                    135deg,
                    rgba(13,85,128,.82),
                    rgba(15,111,151,.58)
                ) !important;
                border-color:rgba(89,212,239,.90) !important;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] > label:has(input:checked) {
                background:linear-gradient(
                    135deg,
                    rgba(4,104,154,.96),
                    rgba(13,140,179,.76)
                ) !important;
                border-color:#69ddf3 !important;
                box-shadow:
                    inset 4px 0 0 #69ddf3,
                    0 4px 12px rgba(0,0,0,.12) !important;
            }

            /* Radio */
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] input[type="radio"] {
                accent-color:#69ddf3 !important;
                transform:scale(1.10) !important;
                flex:0 0 auto !important;
                margin:0 !important;
            }

            /* Texto: ancho completo, máximo dos líneas visuales */
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] [data-testid="stMarkdownContainer"] {
                width:100% !important;
                min-width:0 !important;
                max-width:100% !important;
                flex:1 1 auto !important;
                display:flex !important;
                align-items:center !important;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[role="radiogroup"] [data-testid="stMarkdownContainer"] p {
                width:100% !important;
                margin:0 !important;
                color:#fff !important;
                font-size:.75rem !important;
                font-weight:700 !important;
                line-height:1.22 !important;
                text-align:left !important;
                white-space:normal !important;
                overflow-wrap:anywhere !important;
            }

            /* Captions de navegación quedan dentro de la misma altura visual */
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stCaptionContainer"] {
                color:#a9cada !important;
                font-size:.64rem !important;
                line-height:1.1 !important;
                margin:.10rem 0 0 !important;
            }

            /* Evita que estilos anteriores reduzcan algunos cards según contenido */
            section[data-testid="stSidebar"]
            div[class*="st-key-future_nav_radio_"] div[role="radiogroup"] > label,
            section[data-testid="stSidebar"]
            div[class*="st-key-future_stage_"] div[role="radiogroup"] > label {
                width:100% !important;
                height:64px !important;
                min-height:64px !important;
                max-height:64px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if selected_view=="🏠 Mis clases":
            st.session_state[future_view_key]="🏠 Mis clases"
            st.session_state.pop("future_lab_id",None)
            st.session_state["main_view"]="🏠 Mis clases"
            st.session_state.pop(nav_key,None)
            st.rerun()
        elif selected_view==results_view_label:
            st.session_state[future_view_key]=results_view_label
            st.session_state.pop("future_lab_id",None)
            st.session_state["main_view"]=results_view_label
            st.session_state.pop(nav_key,None)
            st.rerun()
        else:
            st.session_state[future_view_key]=current_lab_label

        # La tarjeta global de progreso del diplomado debe estar siempre visible
        # para el alumno, sin importar el curso o laboratorio que tenga abierto.
        # Usa exactamente el mismo resumen académico que la navegación principal.
        if st.session_state.get("role") == "Alumno":
            student_sidebar_summary(
                _supabase(),
                st.session_state.get("user_key", ""),
            )

        # El avance del alumno se muestra exclusivamente en la tarjeta global
        # “PROGRESO DEL DIPLOMADO”. Se elimina el indicador local del laboratorio
        # para evitar duplicidad y métricas contradictorias en la barra lateral.
        total_stages = len(lab["stages"])
        if st.session_state.get("role") == "Docente":
            if class_id == _C3L1_CLASS_ID:
                st.caption("Vista docente · Laboratorio 1 del Curso 3 completamente formativo, sin nota.")
            else:
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
                f"Etapa {i} · {(
                    _future_stage_display_title(lab,i)
                    if class_id==_C2L2_CLASS_ID
                    else _c3l1_nav_stage_title(lab,i)
                    if class_id==_C3L1_CLASS_ID
                    else _c3l2_nav_stage_title(lab,i)
                    if class_id==_C3L2_CLASS_ID
                    else lab['stages'][i][0]
                )}": i
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

        with st.container(border=True):
            st.markdown(
                """
                <div class="future-sidebar-panel-title">
                    <div class="future-sidebar-panel-kicker">RUTA DE APRENDIZAJE</div>
                    <div class="future-sidebar-panel-subtitle">Etapas del laboratorio</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            selected=st.radio(
                "Ruta de aprendizaje",
                _stage_options,
                format_func=lambda i:(
                    f"Etapa {i} · {_future_stage_display_title(lab,i)}"
                    if class_id==_C2L2_CLASS_ID
                    else f"Etapa {i} · {_c3l1_nav_stage_title(lab,i)}"
                    if class_id==_C3L1_CLASS_ID
                    else f"Etapa {i} · {_c3l2_nav_stage_title(lab,i)}"
                    if class_id==_C3L2_CLASS_ID
                    else f"Etapa {i} · {lab['stages'][i][0]}"
                ),
                key=_stage_key,
                label_visibility="collapsed",
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
            if class_id == _C3L1_CLASS_ID:
                st.caption("Curso 3 · Laboratorio 1: las Etapas 0–10 son formativas y sin nota. La vista docente muestra pautas técnicas dentro de cada etapa.")
            else:
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

    if class_id == _C2L2_CLASS_ID:
        renderers=[
            _c2l2_stage0,_c2l2_stage1,_c2l2_stage2,_c2l2_stage3,_c2l2_stage4,
            _c2l2_stage5,_c2l2_stage6,_c2l2_stage7,_c2l2_stage8,_c2l2_stage9,_c2l2_stage10,
        ]
        renderers[selected](lab,saved)
        return

    if class_id == _C3L1_CLASS_ID:
        renderers = [
            _render_course3_lab1_stage0,
            _render_course3_lab1_stage1,
            _render_course3_lab1_stage2,
            _render_course3_lab1_stage3,
            _render_course3_lab1_stage4,
            _render_course3_lab1_stage5,
            _render_course3_lab1_stage6,
            _render_course3_lab1_stage7,
            _render_course3_lab1_stage8,
            _render_course3_lab1_stage9,
            _render_course3_lab1_stage10,
        ]
        renderers[selected](lab, saved)
        return

    if class_id == _C3L2_CLASS_ID:
        renderers = [
            _render_course3_lab2_stage0,
            _render_course3_lab2_stage1,
            _render_course3_lab2_stage2,
            _render_course3_lab2_stage3,
            _render_course3_lab2_stage4,
            _render_course3_lab2_stage5,
            _render_course3_lab2_stage6,
            _render_course3_lab2_stage7,
            _render_course3_lab2_stage8,
            _render_course3_lab2_stage9,
            _render_course3_lab2_stage10,
        ]
        renderers[selected](lab, saved)
        return

    if str(class_id).strip() == "clase-07-construccion-lab-1" or "construccion-lab-1" in str(class_id):
        from labs import curso4_laboratorio_1 as _c4l1_live
        _c4l1_live.run_stage(selected, lab, saved, globals())
        return

    if str(class_id).strip() == "clase-08-construccion-lab-2" or "construccion-lab-2" in str(class_id):
        from labs import curso4_laboratorio_2 as _c4l2_live
        _c4l2_live.run_stage(selected, lab, saved, globals())
        return

    if str(class_id).strip() == "clase-09-certificaciones-lab-1":
        from labs import curso5_laboratorio_1 as _c5l1_live
        _c5l1_live.run_stage(selected, lab, saved, globals())
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

    if class_id == "clase-03-impacto-instalaciones-lab-1":
        renderers = {
            0: _render_course2_lab1_welcome, 1: _render_course2_lab1_stage1,
            2: _render_course2_lab1_stage2, 3: _render_course2_lab1_stage3,
            4: _render_course2_lab1_stage4, 5: _render_course2_lab1_stage5,
            6: _render_course2_lab1_stage6, 7: _render_course2_lab1_stage7,
            8: _render_course2_lab1_stage8, 9: _render_course2_lab1_stage9,
            10: _render_course2_lab1_stage10,
        }
    elif class_id == _C2L2_CLASS_ID:
        # Curso 2 · Laboratorio 2: el apunte visual usa exactamente los
        # renderizadores reales de las etapas 0 a 10. projection_mode=True
        # evita guardar respuestas o modificar el progreso del alumno.
        renderers = {
            0: _c2l2_stage0, 1: _c2l2_stage1, 2: _c2l2_stage2,
            3: _c2l2_stage3, 4: _c2l2_stage4, 5: _c2l2_stage5,
            6: _c2l2_stage6, 7: _c2l2_stage7, 8: _c2l2_stage8,
            9: _c2l2_stage9, 10: _c2l2_stage10,
        }
    elif class_id == _C3L1_CLASS_ID:
        renderers = {
            0: _render_course3_lab1_stage0,
            1: _render_course3_lab1_stage1,
            2: _render_course3_lab1_stage2,
            3: _render_course3_lab1_stage3,
            4: _render_course3_lab1_stage4,
            5: _render_course3_lab1_stage5,
            6: _render_course3_lab1_stage6,
            7: _render_course3_lab1_stage7,
            8: _render_course3_lab1_stage8,
            9: _render_course3_lab1_stage9,
            10: _render_course3_lab1_stage10,
        }
    elif class_id == _C3L2_CLASS_ID:
        renderers = {
            0: _render_course3_lab2_stage0,
            1: _render_course3_lab2_stage1,
            2: _render_course3_lab2_stage2,
            3: _render_course3_lab2_stage3,
            4: _render_course3_lab2_stage4,
            5: _render_course3_lab2_stage5,
            6: _render_course3_lab2_stage6,
            7: _render_course3_lab2_stage7,
            8: _render_course3_lab2_stage8,
            9: _render_course3_lab2_stage9,
            10: _render_course3_lab2_stage10,
        }
    elif str(class_id).strip() == "clase-07-construccion-lab-1" or "construccion-lab-1" in str(class_id):
        # Curso 4 · Laboratorio 1: reutiliza exactamente los renderizadores
        # reales de las etapas. print/projection_mode evita persistir respuestas.
        renderers = {
            stage: (lambda stage_index: (
                lambda current_lab, current_saved:
                    _c4l1.run_stage(stage_index, current_lab, current_saved, globals())
            ))(stage)
            for stage in range(11)
        }
    elif str(class_id).strip() == "clase-09-certificaciones-lab-1":
        from labs import curso5_laboratorio_1 as _c5l1_live
        renderers = {
            stage: (lambda stage_index: (
                lambda current_lab, current_saved:
                    _c5l1_live.run_stage(stage_index, current_lab, current_saved, globals())
            ))(stage)
            for stage in range(11)
        }
    else:
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

    # El Laboratorio 2 del Curso 4 recupera su borrador persistente de clase.
    if lab.get("id") == "clase-08-construccion-lab-2":
        projection_saved = _future_saved_impl(lab["id"])
    else:
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

    # Curso 2 · Laboratorio 2: Zoom debe utilizar exactamente los mismos
    # renderizadores especializados que Alumno/Docente. El estado es efímero
    # porque projection_mode=True impide persistir respuestas en Supabase.
    if lab.get("id") == _C2L2_CLASS_ID:
        renderers = [
            _c2l2_stage0,
            _c2l2_stage1,
            _c2l2_stage2,
            _c2l2_stage3,
            _c2l2_stage4,
            _c2l2_stage5,
            _c2l2_stage6,
            _c2l2_stage7,
            _c2l2_stage8,
            _c2l2_stage9,
            _c2l2_stage10,
        ]
        renderers[stage](lab, projection_saved)
        return

    if lab.get("id") == _C3L1_CLASS_ID:
        renderers = [
            _render_course3_lab1_stage0,
            _render_course3_lab1_stage1,
            _render_course3_lab1_stage2,
            _render_course3_lab1_stage3,
            _render_course3_lab1_stage4,
            _render_course3_lab1_stage5,
            _render_course3_lab1_stage6,
            _render_course3_lab1_stage7,
            _render_course3_lab1_stage8,
            _render_course3_lab1_stage9,
            _render_course3_lab1_stage10,
        ]
        renderers[stage](lab, projection_saved)
        return

    if lab.get("id") == _C3L2_CLASS_ID:
        renderers = [
            _render_course3_lab2_stage0,
            _render_course3_lab2_stage1,
            _render_course3_lab2_stage2,
            _render_course3_lab2_stage3,
            _render_course3_lab2_stage4,
            _render_course3_lab2_stage5,
            _render_course3_lab2_stage6,
            _render_course3_lab2_stage7,
            _render_course3_lab2_stage8,
            _render_course3_lab2_stage9,
            _render_course3_lab2_stage10,
        ]
        renderers[stage](lab, projection_saved)
        return

    if str(lab.get("id","")).strip() == "clase-07-construccion-lab-1" or "construccion-lab-1" in str(lab.get("id","")):
        from labs import curso4_laboratorio_1 as _c4l1_live
        _c4l1_live.run_stage(stage, lab, projection_saved, globals())
        return

    if str(lab.get("id","")).strip() == "clase-08-construccion-lab-2" or "construccion-lab-2" in str(lab.get("id","")):
        from labs import curso4_laboratorio_2 as _c4l2_live
        _c4l2_live.run_stage(stage, lab, projection_saved, globals())
        return

    if str(lab.get("id", "")).strip() == "clase-09-certificaciones-lab-1":
        from labs import curso5_laboratorio_1 as _c5l1_live
        _c5l1_live.run_stage(stage, lab, projection_saved, globals())
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
    "c2l1_stage9_teacher_view": _c2l1_stage9_teacher_view,
    "c2l1_stage10_teacher_view": _c2l1_stage10_teacher_view,
}

def run_view(name, runtime, *args, **kwargs):
    _bind_runtime(runtime)
    return _VIEWS[name](*args, **kwargs)
