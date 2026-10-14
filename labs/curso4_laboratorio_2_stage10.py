"""Etapa 10 · Entrega y evaluación integral del Laboratorio 2."""

import base64
import html
import io
import json


RUBRIC=[
    (1,"Antecedentes y comprensión del proyecto",5),
    (2,"Selección y caracterización de receptores",5),
    (3,"Maquinaria, espectros y potencias acústicas",10),
    (4,"Modelación de la condición original",10),
    (5,"Resultados y condición crítica",10),
    (6,"Diseño y fundamentación de medidas de control",15),
    (7,"Comparación original–controlada",10),
    (8,"Optimización y cierre técnico",5),
]

SECTION_INTROS={
    1:(
        "Se presentan los antecedentes utilizados para comprender el proyecto, delimitar el área de estudio y "
        "reconocer la secuencia constructiva. La evaluación considera la trazabilidad de la información, la correcta "
        "identificación de las obras y la coherencia de la maquinaria asociada a cada fase."
    ),
    2:(
        "Se identifican los receptores acústicos relevantes y se documentan su ubicación, altura, uso y relación "
        "espacial con el proyecto. Se evalúa que la selección sea representativa y esté técnicamente justificada."
    ),
    3:(
        "Se caracterizan las fuentes de ruido empleadas en la modelación mediante niveles de potencia y espectros "
        "por bandas. Se revisa la correspondencia entre cada actividad, la maquinaria seleccionada y sus datos acústicos."
    ),
    4:(
        "Se documenta la construcción de los escenarios originales en Noise Map Lab, conservando geometría, fuentes, "
        "receptores y parámetros de cálculo. Los resultados representan la condición de referencia antes de incorporar controles."
    ),
    5:(
        "Se analizan los niveles obtenidos en los receptores, su comportamiento espectral y la condición más desfavorable. "
        "La comparación utiliza los límites diurno y nocturno definidos como referencia normativa del laboratorio."
    ),
    6:(
        "Se fundamentan las medidas de control seleccionadas para cada frente y se documentan sus parámetros de diseño. "
        "La evaluación considera la viabilidad constructiva, el cálculo acústico y la correcta implementación en el modelo."
    ),
    7:(
        "Se comparan los modelos original y controlado bajo condiciones equivalentes. Se cuantifica la reducción obtenida, "
        "el margen respecto del límite y la efectividad real de la solución en los receptores evaluados."
    ),
    8:(
        "Se presenta la solución técnica definitiva después de revisar los resultados controlados. El cierre reúne los ajustes, "
        "la estrategia de implementación, las limitaciones del estudio y el plan de verificación propuesto."
    ),
    9:(
        "El cuestionario comprueba individualmente la comprensión de los conceptos aplicados durante el laboratorio. "
        "Su resultado se incorpora automáticamente al puntaje final una vez enviada la evaluación."
    ),
}


def _grade(score,max_score=100.0):
    percentage=100*float(score)/float(max_score)
    if percentage<60:
        return round(1.0+3.0*(percentage/60.0),1)
    return round(4.0+3.0*((percentage-60.0)/40.0),1)


def _payload(row):
    value=(row or {}).get("answer") or {}
    if isinstance(value,str):
        try:return json.loads(value)
        except Exception:return {}
    return value if isinstance(value,dict) else {}


def _quiz_score(row,saved):
    if row:
        if row.get("teacher_score") is not None:return float(row["teacher_score"])
        if row.get("auto_score") is not None:return float(row["auto_score"])
    return float(saved.get("c4l2_s9_score") or 0)


def _practical_score(row):
    if row and row.get("teacher_score") is not None:
        return float(row["teacher_score"])
    return None


def _report_typography(st):
    """Jerarquía tipográfica sobria para la lectura del informe en pantalla."""
    st.markdown("""
    <style>
      [data-testid="stMain"] {
        --c4-report-display: "Aptos Display", "Segoe UI Variable Display", "Segoe UI", sans-serif;
        --c4-report-body: "Aptos", "Segoe UI Variable Text", "Segoe UI", sans-serif;
      }
      [data-testid="stMain"] h1,
      [data-testid="stMain"] h2,
      [data-testid="stMain"] h3,
      [data-testid="stMain"] h4 {
        font-family:var(--c4-report-display) !important;
        color:#102f46;
        letter-spacing:-.025em;
        line-height:1.16;
        text-wrap:balance;
      }
      [data-testid="stMain"] h1 { font-weight:850 !important; }
      [data-testid="stMain"] h2 { font-weight:820 !important; }
      [data-testid="stMain"] h3 {
        font-size:1.18rem !important;
        font-weight:800 !important;
        margin-top:1.4rem !important;
      }
      [data-testid="stMain"] h4 { font-weight:780 !important; }
      [data-testid="stMain"] p,
      [data-testid="stMain"] li,
      [data-testid="stMain"] label,
      [data-testid="stMain"] [data-testid="stCaptionContainer"] {
        font-family:var(--c4-report-body) !important;
        letter-spacing:-.006em;
        line-height:1.62;
      }
      [data-testid="stMain"] strong {
        font-family:var(--c4-report-display) !important;
        color:#173b53;
        font-weight:780;
        letter-spacing:-.012em;
      }
      [data-testid="stMain"] [data-testid="stMetricLabel"] p {
        font-size:.72rem !important;
        font-weight:750 !important;
        letter-spacing:.035em !important;
        text-transform:uppercase;
        color:#587487;
      }
      [data-testid="stMain"] [data-testid="stMetricValue"] {
        font-family:var(--c4-report-display) !important;
        color:#102f46;
        font-weight:780;
        letter-spacing:-.035em;
      }
      [data-testid="stMain"] div[data-testid="stDataFrame"] {
        font-family:var(--c4-report-body) !important;
        border-radius:14px;
        overflow:hidden;
        box-shadow:0 4px 16px rgba(23,59,83,.045);
      }
      [data-testid="stMain"] button {
        font-family:var(--c4-report-display) !important;
        font-weight:750 !important;
        letter-spacing:-.01em;
      }
      [data-testid="stMain"] .c4-report-cover,
      [data-testid="stMain"] .c4-report-section,
      [data-testid="stMain"] .c4-report-intro,
      [data-testid="stMain"] .c4-report-summary {
        font-family:var(--c4-report-body) !important;
      }
      [data-testid="stMain"] .c4-report-cover > div,
      [data-testid="stMain"] .c4-report-section > div {
        font-family:inherit;
      }
    </style>
    """,unsafe_allow_html=True)


def _table_records(value,identity="Ítem"):
    """Convierte listas o diccionarios guardados en filas legibles de informe."""
    if isinstance(value,list):
        rows=value
    elif isinstance(value,dict):
        rows=[]
        for key,item in value.items():
            if isinstance(item,dict):
                rows.append({identity:key,**item})
            else:
                rows.append({identity:key,"Detalle":item})
    else:
        rows=[]
    cleaned=[]
    for row in rows:
        if not isinstance(row,dict):
            row={"Detalle":row}
        cleaned.append({
            str(key):(
                json.dumps(item,ensure_ascii=False)
                if isinstance(item,(dict,list)) else item
            )
            for key,item in row.items()
            if str(key)!="Zona D.S.38"
        })
    return cleaned


def _report_table(st,pd,title,value,identity="Ítem"):
    rows=_table_records(value,identity)
    st.markdown(f"**{title}**")
    if rows:
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    else:
        st.caption("Sin información registrada en esta parte.")


def _report_text(st,title,value):
    st.markdown(f"**{title}**")
    if str(value or "").strip():
        st.write(str(value).strip())
    else:
        st.caption("Sin desarrollo registrado.")


def _report_cover(st,meta):
    author=html.escape(str(
        st.session_state.get("name")
        or (meta or {}).get("author")
        or "Alumno/a del diplomado"
    ))
    st.markdown(f"""
    <div class="c4-report-cover" style="border:1px solid #b9d4e2;border-radius:24px;overflow:hidden;margin:.5rem 0 1.4rem;
                box-shadow:0 12px 34px rgba(23,59,83,.09);background:white">
      <div style="height:9px;background:linear-gradient(90deg,#075985,#0b91b8,#57c4d3)"></div>
      <div style="padding:26px 28px 22px">
        <div style="display:flex;justify-content:space-between;gap:20px;align-items:flex-start;flex-wrap:wrap">
          <div>
            <div style="font-size:.68rem;font-weight:900;letter-spacing:.13em;color:#0b7fa5">CURSO 4 · LABORATORIO 2</div>
            <div style="font-size:1.65rem;line-height:1.18;font-weight:950;color:#102f46;margin:.45rem 0 .55rem">
              INFORME TÉCNICO DE MODELACIÓN<br>Y CONTROL DE RUIDO
            </div>
            <div style="font-size:1rem;font-weight:800;color:#31566d">Conjunto Habitacional Eyzaguirre · Puente Alto</div>
          </div>
          <div style="border:1px solid #c9dce8;border-radius:14px;padding:12px 15px;background:#f3f9fc;min-width:190px">
            <div style="font-size:.62rem;font-weight:900;letter-spacing:.08em;color:#678397">DOCUMENTO</div>
            <div style="font-size:.95rem;font-weight:900;color:#173b53">C4–L2 · INFORME FINAL</div>
            <div style="font-size:.76rem;color:#587487;margin-top:.4rem">Puntaje total: 100 puntos</div>
          </div>
        </div>
        <div style="border-top:1px solid #dce9ef;margin-top:20px;padding-top:14px;display:grid;
                    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;color:#526f80;font-size:.79rem">
          <div><b style="color:#173b53">Preparado por</b><br>{author}</div>
          <div><b style="color:#173b53">Metodología</b><br>Modelación en Noise Map Lab</div>
          <div><b style="color:#173b53">Contexto académico</b><br>Diplomado · Curso 4 · Laboratorio 2</div>
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)


def _render_maps(st,title,maps):
    st.markdown(f"**{title}**")
    if not maps:
        st.caption("No se adjuntaron mapas en esta parte del informe.")
        return
    columns=st.columns(2)
    for index,item in enumerate(maps):
        try:
            raw=base64.b64decode(str(item.get("data") or ""))
        except Exception:
            raw=b""
        if raw:
            columns[index%2].image(
                raw,
                caption=str(item.get("caption") or item.get("name") or f"Mapa {index+1}"),
                use_container_width=True,
            )


def _compress_map(uploaded):
    """Normaliza capturas del mapa para poder guardarlas dentro de la entrega."""
    from PIL import Image
    image=Image.open(uploaded).convert("RGB")
    image.thumbnail((1800,1400))
    output=io.BytesIO()
    image.save(output,format="WEBP",quality=88,method=4)
    return {
        "name":str(uploaded.name).rsplit(".",1)[0]+".webp",
        "caption":str(uploaded.name).rsplit(".",1)[0].replace("_"," "),
        "mime":"image/webp",
        "data":base64.b64encode(output.getvalue()).decode("ascii"),
    }


def _map_upload_panel(st,saved,runtime,lab):
    st.markdown("### 2 · Adjunta los mapas de Noise Map Lab")
    st.markdown(
        "Carga las capturas o mapas exportados para que formen parte del informe final. "
        "Puedes adjuntar varios archivos PNG, JPG o WEBP en cada apartado."
    )
    current=saved.get("c4l2_s10_maps") or {}
    groups=[
        ("original","Etapa 4 · Condición original"),
        ("control","Etapa 6 · Medidas de control implementadas"),
        ("comparison","Etapa 7 · Condición controlada y comparación"),
    ]
    uploads={}
    for key,label in groups:
        uploads[key]=st.file_uploader(
            label,type=["png","jpg","jpeg","webp"],accept_multiple_files=True,
            key=f"c4l2_s10_upload_{key}",
        )
        st.caption(f"Mapas guardados actualmente: {len(current.get(key) or [])}")
    save_col,clear_col=st.columns([.7,.3])
    with save_col:
        save_maps=st.button("Guardar mapas en el informe",type="primary",use_container_width=True,key="c4l2_s10_save_maps")
    with clear_col:
        clear_maps=st.button("Quitar todos los mapas",use_container_width=True,key="c4l2_s10_clear_maps")
    if save_maps:
        updated={key:list(current.get(key) or []) for key,_ in groups}
        try:
            changed=False
            for key,_ in groups:
                if uploads[key]:
                    updated[key]=[_compress_map(item) for item in uploads[key]]
                    changed=True
            if not changed:
                st.warning("Selecciona al menos un mapa antes de guardar.")
            else:
                saved["c4l2_s10_maps"]=updated
                runtime["_save"](lab,saved,10)
                st.success("Mapas incorporados al informe final.")
                st.rerun()
        except Exception as exc:
            st.error(f"No fue posible procesar uno de los mapas: {exc}")
    if clear_maps:
        saved["c4l2_s10_maps"]={}
        runtime["_save"](lab,saved,10)
        st.rerun()


def _section_header(st,stage,title,points,complete=True):
    state="EVIDENCIA RECUPERADA" if complete else "EVIDENCIA PENDIENTE"
    state_color="#087ba0" if complete else "#9a6700"
    st.markdown(f"""
    <div class="c4-report-section" style="margin:1.45rem 0 .7rem;border:1px solid #c9dce8;border-left:6px solid {state_color};
                border-radius:18px;padding:16px 18px;background:linear-gradient(135deg,#fbfdff,#eef7fb)">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
        <div>
          <div style="font-size:.67rem;font-weight:900;letter-spacing:.09em;color:{state_color}">
            ETAPA {stage} · {state}
          </div>
          <div style="font-size:1.08rem;font-weight:900;color:#173b53;margin-top:.22rem">{title}</div>
        </div>
        <div style="white-space:nowrap;border-radius:999px;padding:9px 14px;background:#0b7fa5;color:white;
                    font-size:.78rem;font-weight:900;letter-spacing:.03em">
          PUNTAJE MÁXIMO · {points} PTOS
        </div>
      </div>
      <div style="margin-top:12px;padding-top:11px;border-top:1px solid #d9e7ee;color:#526f80;
                  font-size:.82rem;line-height:1.58;max-width:1050px">
        {SECTION_INTROS.get(stage,"")}
      </div>
    </div>
    """,unsafe_allow_html=True)


def _render_integrated_report(st,pd,report,done=None,quiz_score=None):
    """Informe continuo con todas las evidencias de las Etapas 1 a 8."""
    done=done or {}
    reference=report.get("reference") or {}
    maps=report.get("maps") or {}
    _report_cover(st,report.get("report_meta") or {})
    st.markdown("""
    <div class="c4-report-intro" style="border:1px solid #d3e2ea;border-radius:18px;padding:18px 20px;background:#fbfdff;margin-bottom:1rem">
      <div style="font-size:.69rem;font-weight:900;letter-spacing:.09em;color:#087ba0">OBJETO Y ALCANCE DEL INFORME</div>
      <div style="font-size:1.03rem;font-weight:900;color:#173b53;margin:.3rem 0 .5rem">
        Evaluación de la condición acústica original y de la solución de control
      </div>
      <div style="color:#526f80;line-height:1.65;font-size:.84rem">
        Este informe consolida el trabajo desarrollado durante el laboratorio: antecedentes del proyecto,
        receptores, caracterización de fuentes, construcción del modelo original, análisis de resultados,
        diseño de medidas de control y verificación de la condición controlada. La información proviene de
        los registros guardados por el alumno y de los resultados obtenidos mediante Noise Map Lab.
        <br><br>
        La revisión se organiza en ocho secciones técnicas con un total de 70 puntos. El cuestionario individual
        aporta 30 puntos adicionales. Los límites diurno y nocturno se utilizan exclusivamente como referencia
        normativa para interpretar los resultados modelados.
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.markdown("### Resumen de evaluación del informe")
    st.dataframe(pd.DataFrame([
        {
            "Sección":f"{stage}. {criterion}",
            "Estado":"Evidencia recuperada" if done.get(stage,True) else "Pendiente",
            "Puntaje máximo":points,
        }
        for stage,criterion,points in RUBRIC
    ]),hide_index=True,use_container_width=True)

    _section_header(st,1,RUBRIC[0][1],RUBRIC[0][2],done.get(1,True))
    s1=report.get("stage_1") or {}
    _report_table(st,pd,"Polígono y vértices del proyecto",s1.get("vertices"),"Vértice")
    _report_table(st,pd,"Partes y sectores del proyecto",s1.get("parts"),"Parte")
    _report_table(st,pd,"Etapas o fases constructivas",s1.get("phases"),"Etapa")
    _report_table(st,pd,"Maquinaria identificada",s1.get("machinery"),"Equipo")
    _report_table(st,pd,"Cronología y secuencia de actividades",s1.get("chronology"),"Actividad")

    _section_header(st,2,RUBRIC[1][1],RUBRIC[1][2],done.get(2,True))
    s2=report.get("stage_2") or {}
    _report_table(st,pd,"Receptores seleccionados",s2.get("receptors"),"Receptor")
    _report_table(st,pd,"Justificación y relevancia de los receptores",s2.get("relevance"),"Receptor")

    _section_header(st,3,RUBRIC[2][1],RUBRIC[2][2],done.get(3,True))
    s3=report.get("stage_3") or {}
    _report_table(st,pd,"Fuentes acústicas, espectros y niveles de potencia",s3.get("sources"),"Fuente")
    _report_table(st,pd,"Asignaciones y referencias de la BS 5228",s3.get("bs_assignments"),"Equipo")

    _section_header(st,4,RUBRIC[3][1],RUBRIC[3][2],done.get(4,True))
    s4=report.get("stage_4") or {}
    _report_table(st,pd,"Escenarios y frentes originales",s4.get("scenarios") or s4.get("fronts"),"Frente")
    _report_table(st,pd,"Configuración acústica de los frentes",s4.get("front_configs"),"Frente")
    _report_table(st,pd,"Resultados por receptor",s4.get("results"),"Frente")
    _render_maps(st,"Mapas de la condición original",maps.get("original"))

    _section_header(st,5,RUBRIC[4][1],RUBRIC[4][2],done.get(5,True))
    a,b=st.columns(2)
    a.metric("Periodo de referencia",str(reference.get("period") or "Diurno"))
    try:limit_text=f"{float(reference.get('limit_db',65)):.0f} dB(A)"
    except (TypeError,ValueError):limit_text="—"
    b.metric("Límite de referencia",limit_text)
    s5=report.get("stage_5") or {}
    _report_table(st,pd,"Resultados de la condición original",s5.get("results"),"Resultado")
    _report_table(st,pd,"Condición crítica identificada",s5.get("critical"),"Parámetro")
    _report_text(st,"Interpretación espacial",s5.get("spatial_note"))
    _report_text(st,"Interpretación espectral",s5.get("spectral_note"))

    _section_header(st,6,RUBRIC[5][1],RUBRIC[5][2],done.get(6,True))
    s6=report.get("stage_6") or {}
    _report_table(st,pd,"Estrategia de control por frente",s6.get("design"),"Frente")
    _report_table(st,pd,"Configuración y cálculo de las medidas",s6.get("configurations"),"Frente")
    _report_table(st,pd,"Diseño del panel y cálculo de TL",s6.get("tl_calculator"),"Parámetro")
    _report_table(st,pd,"Estudio del tratamiento acústico",s6.get("treatment_study"),"Parámetro")
    _report_table(st,pd,"Resultados del estudio de tratamiento",s6.get("treatment_results"),"Resultado")
    _render_maps(st,"Mapas con las medidas de control implementadas",maps.get("control"))

    _section_header(st,7,RUBRIC[6][1],RUBRIC[6][2],done.get(7,True))
    s7=report.get("stage_7") or {}
    _report_table(st,pd,"Resultados de la condición controlada",s7.get("controlled_results"),"Resultado")
    _report_table(st,pd,"Comparación original–controlada",s7.get("comparison"),"Comparación")
    _report_table(st,pd,"Comprobación de comparabilidad",s7.get("comparability"),"Comprobación")
    _report_table(st,pd,"Proyectos controlados utilizados",s7.get("project_names"),"Frente")
    _render_maps(st,"Mapas de la condición controlada y comparación",maps.get("comparison"))
    _report_text(st,"Evaluación de la efectividad",s7.get("effectiveness"))
    _report_text(st,"Diferencias observadas entre ambos modelos",s7.get("differences"))

    _section_header(st,8,RUBRIC[7][1],RUBRIC[7][2],done.get(8,True))
    s8=report.get("stage_8") or {}
    _report_table(st,pd,"Estrategia técnica definitiva",s8.get("final_strategy"),"Frente")
    _report_text(st,"Conclusión técnica",s8.get("conclusion"))
    _report_text(st,"Plan de implementación",s8.get("implementation"))
    _report_text(st,"Limitaciones y supuestos",s8.get("limitations"))
    _report_text(st,"Plan de verificación",s8.get("verification"))
    _report_table(st,pd,"Lista de verificación del cierre",s8.get("checks"),"Comprobación")

    _section_header(st,9,"Cuestionario oficial de comprensión",30,quiz_score is not None)
    if quiz_score is None:
        st.info("El puntaje del cuestionario se incorporará cuando se complete y envíe la Etapa 9.")
    else:
        st.metric("Resultado automático del cuestionario",f"{float(quiz_score):g} / 30 puntos")

    st.markdown("""
    <div class="c4-report-summary" style="margin:1.2rem 0;border:1px solid #bcd8e7;border-radius:20px;padding:18px 20px;
                background:linear-gradient(135deg,#eaf7fb,#f8fcff)">
      <div style="font-size:.68rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ESTRUCTURA DE LA NOTA FINAL</div>
      <div style="font-size:1.12rem;font-weight:900;color:#173b53;margin:.35rem 0">Informe técnico 70 puntos + cuestionario 30 puntos = 100 puntos</div>
      <div style="color:#526f80">La nota final se publica después de que el docente revise y puntúe las ocho secciones del informe.</div>
    </div>
    """,unsafe_allow_html=True)


def _teacher_view(st,pd,saved):
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;padding:17px 19px;
                background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VISTA DOCENTE · EVALUACIÓN INTEGRAL</div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">70 puntos de desarrollo práctico + 30 puntos de cuestionario</div>
      <div style="color:#526f80;line-height:1.55">La Etapa 10 no agrega un ejercicio nuevo. Consolida las evidencias de las Etapas 1 a 8 y deja el expediente bloqueado para revisión. El cuestionario de la Etapa 9 se corrige automáticamente.</div>
    </div>
    """,unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Desarrollo práctico","70 puntos")
    b.metric("Cuestionario","30 puntos")
    c.metric("Total","100 puntos")
    st.markdown("#### Conversión a nota")
    st.write("Exigencia del 60 %: 60 puntos equivalen a nota 4,0 y 100 puntos a nota 7,0.")
    st.info("Revisa cada entrega en **Evaluaciones entregadas**, asigna el puntaje práctico sobre 70 y publica la retroalimentación. La nota final se calculará con ese puntaje más el resultado del cuestionario.")
    st.markdown("### Informe integral que recibirá el docente")
    st.caption("Cada capítulo muestra su puntaje máximo y recupera la evidencia guardada en la etapa correspondiente.")
    report=_submission_payload(saved)
    done={stage:bool(saved.get(f"done_{stage}")) for stage in range(1,9)}
    quiz=float(saved.get("c4l2_s9_score") or 0) if saved.get("done_9") else None
    _render_integrated_report(st,pd,report,done,quiz)


def _evidence_summary(saved):
    return {
        "vertices":len(saved.get("c4l2_s1_vertices_table") or []),
        "receptors":len(saved.get("c4l2_s2_receptors_table") or []),
        "sources":len(saved.get("c4l2_s3_acoustic_sources") or []),
        "original_fronts":len(saved.get("c4l2_s4_scenarios") or saved.get("c4l2_s4_front_configs") or {}),
        "original_results":len(saved.get("c4l2_s5_detailed_results") or []),
        "control_strategies":len(saved.get("c4l2_s6_control_design") or []),
        "controlled_results":len(saved.get("c4l2_s7_controlled_results") or []),
        "final_strategies":len(saved.get("c4l2_s8_final_strategy") or []),
    }


def _submission_payload(saved):
    return {
        "version":"c4l2_stage10_v2_report",
        "report_meta":saved.get("c4l2_s10_report_meta") or {},
        "maps":saved.get("c4l2_s10_maps") or {},
        "rubric":[{"stage":stage,"criterion":criterion,"max_score":points} for stage,criterion,points in RUBRIC],
        "practical_max_score":70,
        "quiz_max_score":30,
        "reference":{
            "period":saved.get("c4l2_s5_reference_period") or "Diurno",
            "limit_db":saved.get("c4l2_s5_reference_limit_db") or 65.0,
            "standard":"Referencia normativa del laboratorio",
        },
        "evidence_summary":_evidence_summary(saved),
        "stage_1":{
            "vertices":saved.get("c4l2_s1_vertices_table") or [],
            "parts":saved.get("c4l2_s1_parts_table") or [],
            "phases":saved.get("c4l2_s1_phases_table") or [],
            "machinery":saved.get("c4l2_s1_machinery_table") or [],
            "chronology":saved.get("c4l2_s1_chronology_table") or [],
        },
        "stage_2":{
            "receptors":saved.get("c4l2_s2_receptors_table") or [],
            "relevance":saved.get("c4l2_s2_relevance_table") or [],
        },
        "stage_3":{
            "sources":saved.get("c4l2_s3_acoustic_sources") or [],
            "bs_assignments":saved.get("c4l2_s3_bs_assignments") or [],
        },
        "stage_4":{
            "scenarios":saved.get("c4l2_s4_scenarios") or [],
            "front_configs":saved.get("c4l2_s4_front_configs") or {},
            "results":saved.get("c4l2_s4_results") or {},
        },
        "stage_5":{
            "results":saved.get("c4l2_s5_detailed_results") or [],
            "critical":saved.get("c4l2_s5_critical") or {},
            "spatial_note":saved.get("c4l2_s5_spatial_note") or "",
            "spectral_note":saved.get("c4l2_s5_spectral_note") or "",
        },
        "stage_6":{
            "design":saved.get("c4l2_s6_control_design") or [],
            "configurations":saved.get("c4l2_s6_measure_config") or {},
            "tl_calculator":saved.get("c4l2_s6_tl_calculator") or {},
            "treatment_study":saved.get("c4l2_s6_treatment_study") or {},
            "treatment_results":saved.get("c4l2_s6_treatment_study_results") or {},
        },
        "stage_7":{
            "controlled_results":saved.get("c4l2_s7_controlled_results") or [],
            "comparison":saved.get("c4l2_s7_comparison") or [],
            "comparability":saved.get("c4l2_s7_comparability") or {},
            "project_names":saved.get("c4l2_s7_project_names") or {},
            "effectiveness":saved.get("c4l2_s7_effectiveness") or "",
            "differences":saved.get("c4l2_s7_differences") or "",
        },
        "stage_8":{
            "final_strategy":saved.get("c4l2_s8_final_strategy") or [],
            "conclusion":saved.get("c4l2_s8_conclusion") or "",
            "implementation":saved.get("c4l2_s8_implementation") or "",
            "limitations":saved.get("c4l2_s8_limitations") or "",
            "verification":saved.get("c4l2_s8_verification") or "",
            "checks":saved.get("c4l2_s8_checks") or {},
        },
        "stage_9":saved.get("c4l2_s9_submission") or {},
    }


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    _report_typography(st)
    runtime["header"](
        "ETAPA 10 · LABORATORIO 2",
        "Entrega y evaluación integral",
        "Consolidar el proyecto desarrollado durante todo el laboratorio, enviarlo a evaluación y obtener la nota final sobre 100 puntos.",
        show_overview=False,duration_minutes=25,
    )
    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ENTREGA FINAL · 100 PUNTOS</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">Tu proyecto completo, desde los antecedentes hasta la solución controlada</div>
      <div style="color:#526f80;line-height:1.6">La plataforma reúne las evidencias guardadas en las Etapas 1 a 8. El desarrollo práctico vale 70 puntos y el cuestionario de la Etapa 9 vale 30 puntos.</div>
    </div>
    """,unsafe_allow_html=True)
    author=(
        st.session_state.get("name")
        or st.session_state.get("user_name")
        or st.session_state.get("student_name")
        or "Alumno/a del diplomado"
    )
    # El nombre visible del usuario reemplaza cualquier identificador interno
    # que haya quedado guardado en una versión anterior del informe.
    saved["c4l2_s10_report_meta"]={"author":str(author)}

    if st.session_state.get("role")=="Docente":
        _teacher_view(st,pd,saved)
        return

    quiz_row=runtime["_evaluation_row"](9,"c4l2_final_quiz")
    final_row=runtime["_evaluation_row"](10,"c4l2_integrated_project")
    submitted=bool(final_row or saved.get("c4l2_s10_submitted"))
    quiz_score=_quiz_score(quiz_row,saved)
    practical_score=_practical_score(final_row)

    if submitted:
        st.success("Evaluación integral enviada. El expediente quedó bloqueado para revisión docente.")
        a,b,c,d=st.columns(4)
        a.metric("Cuestionario",f"{quiz_score:g}/30")
        if practical_score is None:
            b.metric("Desarrollo práctico","Pendiente")
            c.metric("Puntaje final","Pendiente")
            d.metric("Nota final","Pendiente")
            st.info("La nota final aparecerá cuando el docente asigne el puntaje práctico sobre 70 puntos.")
        else:
            total=max(0.0,min(100.0,quiz_score+practical_score))
            grade=_grade(total)
            b.metric("Desarrollo práctico",f"{practical_score:g}/70")
            c.metric("Puntaje final",f"{total:g}/100")
            d.metric("Nota final",f"{grade:.1f}")
            if total>=60:st.success("Evaluación aprobada con exigencia del 60 %.")
            else:st.error("El puntaje final se encuentra bajo la exigencia de aprobación del 60 %.")
        feedback=(final_row or {}).get("teacher_feedback") or (final_row or {}).get("feedback")
        if feedback:st.markdown(f"**Retroalimentación docente:** {feedback}")
        st.markdown("### Informe técnico entregado")
        report=_payload(final_row) if final_row else _submission_payload(saved)
        if not isinstance(report,dict) or not report.get("stage_1"):
            report=_submission_payload(saved)
        _render_integrated_report(st,pd,report,{stage:True for stage in range(1,9)},quiz_score)
        return

    st.markdown("### 1 · Comprueba el avance del laboratorio")
    progress=[]
    for stage,criterion,points in RUBRIC:
        progress.append({
            "Etapa":stage,"Evidencia evaluada":criterion,"Puntaje máximo":points,
            "Estado":"Completa" if saved.get(f"done_{stage}") else "Pendiente",
        })
    progress.append({"Etapa":9,"Evidencia evaluada":"Cuestionario individual","Puntaje máximo":30,"Estado":"Completa" if saved.get("done_9") or quiz_row else "Pendiente"})
    st.dataframe(pd.DataFrame(progress),hide_index=True,use_container_width=True)
    completed=sum(saved.get(f"done_{stage}") is True for stage in range(1,9))
    a,b,c=st.columns(3)
    a.metric("Etapas prácticas",f"{completed}/8")
    b.metric("Cuestionario",f"{quiz_score:g}/30" if saved.get("done_9") or quiz_row else "Pendiente")
    c.metric("Puntaje práctico máximo","70 puntos")

    _map_upload_panel(st,saved,runtime,lab)

    st.markdown("### 3 · Revisa el informe técnico consolidado")
    st.caption(
        "Este es el informe que se enviará al docente. Cada capítulo recupera el trabajo guardado en la etapa "
        "correspondiente y muestra el puntaje máximo que puede obtener."
    )
    report=_submission_payload(saved)
    done={stage:bool(saved.get(f"done_{stage}")) for stage in range(1,9)}
    quiz_visible=quiz_score if saved.get("done_9") or quiz_row else None
    _render_integrated_report(st,pd,report,done,quiz_visible)
    st.caption("El docente asignará el puntaje después de revisar la calidad técnica, coherencia y trazabilidad de cada sección. Completar campos no otorga automáticamente el puntaje máximo.")

    st.markdown("### 4 · Entrega definitiva")

    declaration=st.checkbox(
        "Declaro que revisé el expediente, que los resultados corresponden a mis modelos y que esta es mi entrega definitiva.",
        key="c4l2_s10_declaration",
    )
    if st.button("ENTREGAR EVALUACIÓN INTEGRAL",type="primary",use_container_width=True,key="c4l2_s10_submit"):
        missing=[str(stage) for stage in range(1,9) if not saved.get(f"done_{stage}")]
        if missing:
            st.warning("Falta completar las Etapas "+", ".join(missing)+" antes de enviar la evaluación integral.")
        elif not (saved.get("done_9") or quiz_row):
            st.warning("Primero debes enviar el cuestionario de la Etapa 9.")
        elif not declaration:
            st.warning("Confirma la declaración de entrega definitiva.")
        else:
            payload=_submission_payload(saved)
            stored=runtime["_submit_evaluation"](
                10,"c4l2_integrated_project","Curso 4 · Laboratorio 2 · Evaluación integral",
                payload,0,70,"Entrega recibida. Pendiente de revisión y puntaje docente.",
                auto_level="Pendiente de revisión docente",
            )
            saved["c4l2_s10_submission_summary"]=payload["evidence_summary"]
            saved["c4l2_s10_submitted"]=True
            saved["done_10"]=True
            runtime["_save"](lab,saved,10)
            if not stored:
                st.warning("La entrega quedó guardada en tu progreso, pero no fue posible registrarla remotamente en este momento.")
            st.rerun()

