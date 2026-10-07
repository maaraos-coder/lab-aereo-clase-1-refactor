"""Etapa 4 · Curso 4 Laboratorio 2: modelación de la condición original."""

import math
import re
import unicodedata

OCTAVE_LABELS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]

def _safe_name(value):
    txt="".join(ch for ch in unicodedata.normalize("NFD",str(value or "")) if unicodedata.category(ch)!="Mn")
    txt=re.sub(r"[^A-Za-z0-9]+","_",txt).strip("_")
    return txt or "Etapa"

def _parse_num(value):
    try:
        return float(str(value).replace(",",".").strip())
    except Exception:
        return None

def _sum_db(values):
    vals=[float(v) for v in values if v is not None]
    if not vals:
        return None
    return 10*math.log10(sum(10**(v/10) for v in vals))

def _qty(value):
    try:
        q=int(float(value))
        return max(1,q)
    except Exception:
        return 1

def _teacher_pauta(st,pd,sources):
    if st.session_state.get("role")!="Docente":
        return
    with st.expander("👨‍🏫 Pauta docente · Etapa 4",expanded=False):
        st.markdown("""
        **Criterio de corrección**

        - La condición original se modela **sin medidas de control**.
        - Las máquinas se agrupan por **etapa/frente de trabajo**.
        - Solo deben sumarse fuentes que puedan operar simultáneamente en la condición crítica.
        - La suma se realiza **energéticamente y por banda de octava**.
        - La fuente equivalente se ubica dentro del predio, en la posición **físicamente posible más próxima** al receptor objetivo.
        - Cada etapa se guarda como un proyecto/escenario independiente en Noise Map Lab.
        - El escenario original no debe sobrescribirse cuando posteriormente se incorporen medidas de control.
        """)
        if not sources:
            st.info("La pauta conceptual está disponible, pero aún no existen fuentes acústicas guardadas desde la Etapa 3.")
            return
        stages={}
        for s in sources:
            stages.setdefault(str(s.get("Etapa") or "Etapa no definida"),[]).append(s)
        rows=[]
        for stage,items in stages.items():
            for s in items:
                rows.append({
                    "Etapa":stage,
                    "Máquina":s.get("Máquina / equipo proyecto"),
                    "Cantidad":s.get("Cantidad"),
                    "BS":s.get("Referencia BS"),
                    "LWA":round(float(s.get("LWA_global") or 0),1),
                })
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.caption("La solución exacta de cada fuente equivalente depende de la simultaneidad que sea técnicamente defendible para ese frente.")

def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 4 · LABORATORIO 2",
        "Modela la condición original · frentes de trabajo",
        "Construir la peor condición de exposición sonora sin medidas de control, agrupando las máquinas por etapa en fuentes equivalentes y guardando un escenario original por frente.",
        show_overview=False,
        duration_minutes=45,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
    background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">ESCENARIO BASE · SIN CONTROL</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">
        Primero necesitamos saber cuánto ruido produce la obra antes de intervenirla
      </div>
      <div style="color:#526f80;line-height:1.6">
        Cada etapa constructiva se representará mediante un <b>frente de trabajo</b>.
        Las máquinas que puedan operar simultáneamente se combinarán mediante suma energética para formar
        una <b>fuente equivalente</b>. Ese frente se ubicará en la posición físicamente posible más próxima
        al receptor objetivo, todavía <b>sin barreras, encierros, silenciadores ni otras medidas de control</b>.
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 1 · ¿Qué es una fuente equivalente de un frente?")
    st.markdown("""
    En vez de modelar cada máquina como un escenario independiente, agruparemos las máquinas que pertenecen
    a una misma etapa y que pueden funcionar simultáneamente. Para cada banda de octava:

    \[
    L_{W,f,eq}=10\log_{10}\left(\sum_i10^{L_{W,f,i}/10}\right)
    \]

    Si existen varias unidades iguales operando simultáneamente:

    \[
    L_{W,f,N}=L_{W,f}+10\log_{10}(N)
    \]

    El resultado es el espectro de potencia sonora de la **fuente equivalente del frente de trabajo**.
    """)
    st.warning("Peor condición no significa inventar simultaneidades imposibles. Debe ser una condición crítica, pero técnicamente realizable según la etapa y el cronograma del proyecto.")

    sources=saved.get("c4l2_s3_acoustic_sources") or []
    receptors=saved.get("c4l2_s2_receptors_table") or []

    st.markdown("### 2 · Recupera las fuentes y agrúpalas por etapa")
    if not sources:
        st.warning("Aún no hay caracterización acústica guardada desde la Etapa 3. Completa y guarda la Etapa 3 para construir los frentes de trabajo.")
        _teacher_pauta(st,pd,sources)
        return

    stages=[]
    for s in sources:
        stage=str(s.get("Etapa") or "Etapa no definida").strip()
        if stage not in stages:
            stages.append(stage)

    stage=st.selectbox("Etapa / frente a modelar",stages,key="c4l2_s4_stage")
    stage_index=stages.index(stage)+1
    stage_sources=[s for s in sources if str(s.get("Etapa") or "Etapa no definida").strip()==stage]
    front_name=f"FT{stage_index} · {stage}"

    st.markdown(f"#### {front_name}")
    config_key=f"c4l2_s4_cfg_{_safe_name(stage)}"
    default_cfg=[]
    for s in stage_sources:
        default_cfg.append({
            "Máquina":s.get("Máquina / equipo proyecto"),
            "Cantidad declarada":_qty(s.get("Cantidad")),
            "¿Simultánea?":"Sí",
            "Referencia BS":s.get("Referencia BS"),
            "LWA [dB(A)]":round(float(s.get("LWA_global") or 0),1),
        })
    if config_key not in st.session_state:
        old=(saved.get("c4l2_s4_front_configs") or {}).get(stage)
        st.session_state[config_key]=old if old else default_cfg

    cfg=runtime["_professional_grid"](
        pd.DataFrame(st.session_state[config_key]),
        key=f"{config_key}_grid",
        widths={"Máquina":220,"Cantidad declarada":135,"¿Simultánea?":135,"Referencia BS":220,"LWA [dB(A)]":125},
        select_options={"¿Simultánea?":["Sí","No"]},
        numeric_columns=["Cantidad declarada","LWA [dB(A)]"],
        height=max(235,min(430,90+42*len(stage_sources))),
    )
    st.session_state[config_key]=cfg.where(pd.notna(cfg),None).to_dict("records")
    selected_names={str(r.get("Máquina")) for r in st.session_state[config_key] if r.get("¿Simultánea?")=="Sí"}

    st.caption("Marca solo las máquinas que pueden operar simultáneamente en la condición crítica de esta etapa.")

    active=[]
    for s in stage_sources:
        if str(s.get("Máquina / equipo proyecto")) in selected_names:
            active.append(s)

    st.markdown("### 3 · Calcula la fuente equivalente")
    if not active:
        st.info("Selecciona al menos una máquina simultánea para construir el frente.")
        _teacher_pauta(st,pd,sources)
        return

    band_matrix={"Banda":OCTAVE_LABELS}
    expected=[]
    for s in active:
        name=str(s.get("Máquina / equipo proyecto"))
        q=_qty(s.get("Cantidad"))
        lw=list(s.get("Lw_bandas") or [])
        contribution=[float(v)+10*math.log10(q) for v in lw]
        band_matrix[f"{name} ×{q}"]=[round(v,1) for v in contribution]
    for idx in range(8):
        expected.append(_sum_db([band_matrix[k][idx] for k in band_matrix if k!="Banda"]))

    st.caption("Los valores mostrados ya incorporan la cantidad de unidades declaradas. Realiza tú la suma energética para cada banda.")
    st.dataframe(pd.DataFrame(band_matrix),hide_index=True,use_container_width=True)

    answer_key=f"c4l2_s4_answers_{_safe_name(stage)}"
    saved_answers=st.session_state.get(answer_key,{})
    st.markdown("#### Ingresa tu Lw equivalente por banda")
    answers={}
    cols=st.columns(4)
    for i,label in enumerate(OCTAVE_LABELS):
        with cols[i%4]:
            answers[label]=st.text_input(
                label,
                value=str(saved_answers.get(label,"")),
                key=f"{answer_key}_{i}",
                placeholder="dB",
            )
    st.session_state[answer_key]=answers

    check_key=f"c4l2_s4_check_{_safe_name(stage)}"
    if st.button("Comprobar suma energética",use_container_width=True,key=check_key):
        parsed=[_parse_num(answers[x]) for x in OCTAVE_LABELS]
        if any(v is None for v in parsed):
            st.warning("Completa las 8 bandas antes de comprobar.")
        else:
            ok=[abs(a-e)<=0.2 for a,e in zip(parsed,expected)]
            if all(ok):
                st.success("Correcto. El espectro equivalente del frente está bien calculado.")
                st.session_state[f"{check_key}_ok"]=True
            else:
                bad=[OCTAVE_LABELS[i] for i,v in enumerate(ok) if not v]
                st.warning("Revisa la suma energética en: "+", ".join(bad)+".")
                st.session_state[f"{check_key}_ok"]=False

    st.markdown("### 4 · Ubica el frente en la peor posición físicamente posible")
    st.markdown("""
    Lleva la fuente equivalente a **Noise Map Lab** y ubícala dentro del predio en el punto más próximo
    al receptor objetivo **donde realmente pueda desarrollarse esa actividad**. No atravieses edificios,
    límites o zonas incompatibles solo para reducir artificialmente la distancia.
    """)

    rec_options=[str(r.get("Receptor")) for r in receptors if str(r.get("Receptor") or "").strip()]
    if not rec_options:
        st.warning("No hay receptores guardados desde la Etapa 2. Puedes revisar el cálculo del frente, pero debes completar la Etapa 2 antes de guardar el escenario espacial.")
        _teacher_pauta(st,pd,sources)
        return

    rec_lookup={str(r.get("Receptor")):r for r in receptors}
    a,b,c=st.columns(3)
    with a:
        target_rec=st.selectbox("Receptor objetivo",rec_options,key=f"c4l2_s4_target_{_safe_name(stage)}")
    with b:
        distance=st.number_input("Distancia fuente–receptor [m]",min_value=0.1,value=10.0,step=0.5,key=f"c4l2_s4_dist_{_safe_name(stage)}")
    with c:
        source_h=st.number_input("Altura fuente equivalente [m]",min_value=0.1,value=1.5,step=0.1,key=f"c4l2_s4_height_{_safe_name(stage)}")

    rec=rec_lookup.get(target_rec,{})
    st.caption(f"Receptor seleccionado: {target_rec} · {rec.get('Descripción','')} · altura receptor: {rec.get('Altura (m)','—')} m")

    sector=st.text_input("Ubicación / sector del frente dentro del predio",key=f"c4l2_s4_sector_{_safe_name(stage)}",placeholder="Ej.: borde poniente del frente de excavación, próximo a R2")

    st.link_button("🗺️ Abrir Noise Map Lab",runtime["NOISEMAP_URL"],use_container_width=True)

    st.markdown("### 5 · Guarda esta etapa como proyecto original")
    suggested=f"Eyzaguirre_FT{stage_index}_{_safe_name(stage)}_Original"
    project_name=st.text_input(
        "Nombre del proyecto en Noise Map Lab",
        value=suggested,
        key=f"c4l2_s4_project_{_safe_name(stage)}",
    )
    st.markdown("""
    En **Guardar proyecto** de Noise Map Lab conserva este escenario antes de hacer cualquier modificación.
    Ese archivo será la referencia para comparar las medidas de control en las etapas siguientes.
    """)
    confirmed=st.checkbox(
        "Confirmo que guardé este escenario original en Noise Map Lab",
        key=f"c4l2_s4_savedmap_{_safe_name(stage)}",
    )

    st.markdown("### 6 · Registra los resultados de la condición original")
    result_key=f"c4l2_s4_results_{_safe_name(stage)}"
    existing_results=(saved.get("c4l2_s4_results") or {}).get(stage)
    result_rows=existing_results or [
        {"Receptor":r.get("Receptor"),"Distancia F–R [m]":None,"LAeq predicho [dB(A)]":None}
        for r in receptors if str(r.get("Receptor") or "").strip()
    ]
    results_df=runtime["_professional_grid"](
        pd.DataFrame(result_rows),
        key=f"{result_key}_grid",
        widths={"Receptor":120,"Distancia F–R [m]":170,"LAeq predicho [dB(A)]":200},
        numeric_columns=["Distancia F–R [m]","LAeq predicho [dB(A)]"],
        height=max(235,min(430,90+42*len(result_rows))),
    )

    if st.button("✓ Guardar escenario original de esta etapa",type="primary",use_container_width=True,key=f"c4l2_s4_save_{_safe_name(stage)}"):
        parsed=[_parse_num(answers[x]) for x in OCTAVE_LABELS]
        missing=[]
        if not st.session_state.get(f"{check_key}_ok",False):
            missing.append("suma energética correcta")
        if not sector.strip():
            missing.append("ubicación del frente")
        if not project_name.strip():
            missing.append("nombre del proyecto")
        if not confirmed:
            missing.append("confirmación de guardado en Noise Map Lab")
        clean_results=results_df.where(pd.notna(results_df),None).to_dict("records")
        if not any(r.get("LAeq predicho [dB(A)]") is not None for r in clean_results):
            missing.append("al menos un resultado predicho")
        if missing:
            st.warning("Completa: "+", ".join(missing)+".")
        else:
            front_configs=saved.get("c4l2_s4_front_configs") or {}
            front_configs[stage]=st.session_state[config_key]
            all_results=saved.get("c4l2_s4_results") or {}
            all_results[stage]=clean_results
            scenarios=[x for x in (saved.get("c4l2_s4_scenarios") or []) if x.get("Etapa")!=stage]
            scenarios.append({
                "Frente":front_name,
                "Etapa":stage,
                "Receptor objetivo":target_rec,
                "Distancia objetivo [m]":distance,
                "Altura fuente [m]":source_h,
                "Ubicación / sector":sector,
                "Proyecto Noise Map":project_name,
                "Lw equivalente por bandas":[round(v,2) for v in expected],
                "Máquinas simultáneas":[s.get("Máquina / equipo proyecto") for s in active],
            })
            saved["c4l2_s4_front_configs"]=front_configs
            saved["c4l2_s4_results"]=all_results
            saved["c4l2_s4_scenarios"]=scenarios
            saved["done_4"]=len(scenarios)>=len(stages)
            runtime["_save"](lab,saved,4)
            st.success("Escenario original guardado. Puedes cambiar de etapa y construir el siguiente frente.")

    st.markdown("### 7 · Escenarios originales guardados")
    scenarios=saved.get("c4l2_s4_scenarios") or []
    if scenarios:
        overview=[]
        for x in scenarios:
            overview.append({
                "Frente":x.get("Frente"),
                "Receptor objetivo":x.get("Receptor objetivo"),
                "Distancia [m]":x.get("Distancia objetivo [m]"),
                "Proyecto Noise Map":x.get("Proyecto Noise Map"),
            })
        st.dataframe(pd.DataFrame(overview),hide_index=True,use_container_width=True)
        st.caption(f"Avance: {len(scenarios)} de {len(stages)} etapas/frentes guardados.")
    else:
        st.info("Aún no has guardado escenarios originales.")

    _teacher_pauta(st,pd,sources)
