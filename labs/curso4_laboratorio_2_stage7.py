"""Etapa 7 · Comparación de la condición original y controlada."""

import math


BANDS=["31,5 Hz","63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz"]


def _num(value):
    try:
        number=float(str(value).replace(",",".").strip())
        return number if math.isfinite(number) else None
    except Exception:
        return None


def _key(row):
    return (str(row.get("Frente") or "").strip(),str(row.get("Receptor") or "").strip())


def _controlled_template(original_rows,saved_rows):
    saved_map={_key(row):row for row in (saved_rows or [])}
    output=[]
    for original in original_rows:
        front,receptor=_key(original)
        previous=saved_map.get((front,receptor),{})
        output.append({
            "Frente":front,
            "Receptor":receptor,
            **{band:previous.get(band) for band in BANDS},
            "LAeq controlado [dB(A)]":previous.get("LAeq controlado [dB(A)]"),
        })
    return output


def _comparison_rows(original_rows,controlled_rows,limit):
    controlled_map={_key(row):row for row in controlled_rows}
    rows=[]
    for original in original_rows:
        original_laeq=_num(original.get("LAeq [dB(A)]"))
        if original_laeq is None:
            continue
        controlled=controlled_map.get(_key(original),{})
        controlled_laeq=_num(controlled.get("LAeq controlado [dB(A)]"))
        reduction=None if controlled_laeq is None else original_laeq-controlled_laeq
        if controlled_laeq is None:
            result="Pendiente"
        elif controlled_laeq>limit:
            result="Mejora, pero sobre el límite" if reduction and reduction>0 else "Sobre el límite"
        elif controlled_laeq==limit:
            result="En el límite"
        else:
            result="Bajo el límite"
        rows.append({
            "Frente":original.get("Frente"),
            "Receptor":original.get("Receptor"),
            "Original [dB(A)]":round(original_laeq,1),
            "Controlado [dB(A)]":round(controlled_laeq,1) if controlled_laeq is not None else None,
            "Reducción [dB]":round(reduction,1) if reduction is not None else None,
            "Límite ref. [dB(A)]":limit,
            "Margen [dB]":round(limit-controlled_laeq,1) if controlled_laeq is not None else None,
            "Resultado":result,
        })
    return rows


def _teacher_panel(st,pd):
    if st.session_state.get("role")!="Docente":
        return
    st.markdown("""
    <div style="border:1px solid #bcd8e7;border-left:5px solid #0b7fa5;border-radius:18px;
                padding:17px 19px;background:linear-gradient(135deg,#f8fcff,#edf7fb);margin:.7rem 0 1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VISTA DOCENTE · CRITERIO DE REVISIÓN</div>
      <div style="font-size:1.05rem;font-weight:900;color:#173b53;margin:.3rem 0">Comparar modelos equivalentes, no resultados aislados</div>
      <div style="color:#526f80;line-height:1.55">La condición controlada debe conservar fuentes, receptores, geometría y configuración de cálculo. La única diferencia admisible es la medida de control y los cambios indispensables para implementarla.</div>
    </div>
    """,unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Criterio":"Comparabilidad","Evidencia":"Mismas fuentes, posiciones, receptores, alturas y parámetros de cálculo."},
        {"Criterio":"Reducción","Evidencia":"ΔL = LAeq original − LAeq controlado, informado por receptor."},
        {"Criterio":"Espectro","Evidencia":"La reducción por bandas es coherente con la medida diseñada."},
        {"Criterio":"Límite","Evidencia":"El nivel modelado se compara con la referencia diurna o nocturna guardada."},
    ]),hide_index=True,use_container_width=True)


def render(lab,saved,runtime):
    st=runtime["st"]; pd=runtime["pd"]
    runtime["header"](
        "ETAPA 7 · LABORATORIO 2",
        "Compara la condición original y controlada",
        "Cuantificar la reducción obtenida en Noise Map Lab, revisar su comportamiento espectral y verificar si el nivel modelado queda bajo el límite de referencia.",
        show_overview=False,
        duration_minutes=40,
    )

    st.markdown("""
    <div style="border:1px solid #cfe0ed;border-radius:22px;padding:22px 24px;
                background:linear-gradient(135deg,#f8fcff,#edf6fb);margin-bottom:1rem">
      <div style="font-size:.70rem;font-weight:900;letter-spacing:.09em;color:#087ba0">VERIFICACIÓN DEL CONTROL</div>
      <div style="font-size:1.28rem;font-weight:900;color:#173b53;margin:.35rem 0">Mismo escenario, una sola diferencia: la medida de control</div>
      <div style="color:#526f80;line-height:1.6">Registra los resultados de la copia controlada y compáralos con la línea base guardada en la Etapa 5. La reducción final debe obtenerse en los receptores del modelo, no restando directamente el TL del elemento.</div>
    </div>
    """,unsafe_allow_html=True)

    _teacher_panel(st,pd)
    original_rows=saved.get("c4l2_s5_detailed_results") or []
    original_valid=[row for row in original_rows if _num(row.get("LAeq [dB(A)]")) is not None]
    design_rows=saved.get("c4l2_s6_control_design") or []
    reference_period=str(saved.get("c4l2_s5_reference_period") or "Diurno")
    reference_limit=_num(saved.get("c4l2_s5_reference_limit_db"))
    if reference_limit is None:
        reference_limit=50.0 if reference_period=="Nocturno" else 65.0

    st.markdown("### 1 · Recupera la línea base y el criterio")
    a,b,c=st.columns(3)
    a.metric("Resultados originales",len(original_valid))
    b.metric("Periodo",reference_period)
    c.metric("Límite de referencia",f"{reference_limit:.0f} dB(A)")
    st.caption("Referencia educativa: Zona III del DS N.º 38/2011 del MMA. El resultado corresponde a una comparación modelada.")
    if not original_valid:
        st.warning("Primero debes registrar y guardar resultados originales en la Etapa 5.")
        return
    if not saved.get("done_6"):
        st.warning("La estrategia de control aún no está finalizada en la Etapa 6. Puedes revisar esta etapa, pero no completar la comparación definitiva.")

    st.markdown("### 2 · Confirma que ambos modelos sean comparables")
    previous_checks=saved.get("c4l2_s7_comparability") or {}
    checks={}
    labels={
        "sources":"Conservé las mismas fuentes, potencias y condiciones de operación.",
        "geometry":"Conservé posiciones, alturas, terreno y obstáculos originales.",
        "receivers":"Conservé los mismos receptores, coordenadas y alturas.",
        "settings":"Utilicé la misma configuración y resolución de cálculo.",
        "copy":"Trabajé sobre una copia y la única diferencia relevante es la medida de control.",
    }
    for name,label in labels.items():
        checks[name]=st.checkbox(label,value=bool(previous_checks.get(name)),key=f"c4l2_s7_check_{name}")

    st.markdown("### 3 · Registra la condición controlada")
    controlled_all=_controlled_template(original_rows,saved.get("c4l2_s7_controlled_results") or [])
    fronts=list(dict.fromkeys(str(row.get("Frente") or "") for row in original_valid))
    selected_front=st.selectbox("Frente a registrar",fronts,key="c4l2_s7_front")
    project_by_front={str(row.get("Frente / condición") or ""):str(row.get("Proyecto controlado") or "") for row in design_rows}
    related_projects=[name for front,name in project_by_front.items() if selected_front in front or front.startswith(selected_front)]
    suggested_project=next((name for name in related_projects if name.strip()),"")
    project_names=dict(saved.get("c4l2_s7_project_names") or {})
    project_name=st.text_input(
        "Proyecto controlado en Noise Map Lab",
        value=project_names.get(selected_front) or suggested_project,
        key="c4l2_s7_project_name",
    )

    front_rows=[row for row in controlled_all if str(row.get("Frente"))==selected_front]
    controlled_df=pd.DataFrame(front_rows)
    edited=st.data_editor(
        controlled_df,
        hide_index=True,
        use_container_width=True,
        height=max(220,46+42*len(controlled_df)),
        disabled=["Frente","Receptor"],
        num_rows="fixed",
        column_config={
            "Frente":st.column_config.TextColumn("Frente",width="large"),
            "Receptor":st.column_config.TextColumn("Receptor",width="small"),
            **{band:st.column_config.NumberColumn(band,min_value=0.0,max_value=150.0,step=.1,format="%.1f") for band in BANDS},
            "LAeq controlado [dB(A)]":st.column_config.NumberColumn("LAeq controlado",min_value=0.0,max_value=150.0,step=.1,format="%.1f dB(A)"),
        },
        key=f"c4l2_s7_editor_{fronts.index(selected_front)}",
    )
    if st.button("Guardar resultados de este frente",use_container_width=True,key="c4l2_s7_save_front"):
        edited_records=edited.where(pd.notna(edited),None).to_dict("records")
        edited_map={_key(row):row for row in edited_records}
        merged=[edited_map.get(_key(row),row) for row in controlled_all]
        project_names[selected_front]=project_name
        saved["c4l2_s7_controlled_results"]=merged
        saved["c4l2_s7_project_names"]=project_names
        runtime["_save"](lab,saved,7)
        st.success("Resultados controlados del frente guardados.")

    # Incorporar la edición visible a la vista comparativa, incluso antes de guardar.
    visible_map={_key(row):row for row in edited.where(pd.notna(edited),None).to_dict("records")}
    controlled_view=[visible_map.get(_key(row),row) for row in controlled_all]
    comparisons=_comparison_rows(original_rows,controlled_view,reference_limit)
    valid_comparisons=[row for row in comparisons if _num(row.get("Controlado [dB(A)]")) is not None]

    st.markdown("### 4 · Analiza la reducción obtenida")
    if valid_comparisons:
        st.dataframe(pd.DataFrame(comparisons),hide_index=True,use_container_width=True)
        reductions=[_num(row.get("Reducción [dB]")) for row in valid_comparisons]
        controlled_levels=[_num(row.get("Controlado [dB(A)]")) for row in valid_comparisons]
        d1,d2,d3,d4=st.columns(4)
        d1.metric("Comparaciones completas",f"{len(valid_comparisons)}/{len(comparisons)}")
        d2.metric("Reducción media",f"{sum(reductions)/len(reductions):.1f} dB")
        d3.metric("Mayor controlado",f"{max(controlled_levels):.1f} dB(A)")
        d4.metric("Bajo el límite",f"{sum(level<=reference_limit for level in controlled_levels)}/{len(controlled_levels)}")

        chart=pd.DataFrame(valid_comparisons)[["Receptor","Original [dB(A)]","Controlado [dB(A)]"]].set_index("Receptor")
        st.bar_chart(chart,use_container_width=True)

        spectral_candidates=[]
        original_map={_key(row):row for row in original_rows}
        controlled_map={_key(row):row for row in controlled_view}
        for key,original in original_map.items():
            controlled=controlled_map.get(key,{})
            if any(_num(original.get(band)) is not None and _num(controlled.get(band)) is not None for band in BANDS):
                spectral_candidates.append(key)
        if spectral_candidates:
            labels_spectral=[f"{front} · {receptor}" for front,receptor in spectral_candidates]
            chosen=st.selectbox("Comparación espectral",labels_spectral,key="c4l2_s7_spectral_choice")
            chosen_key=spectral_candidates[labels_spectral.index(chosen)]
            original=original_map[chosen_key]; controlled=controlled_map[chosen_key]
            spectral_df=pd.DataFrame({
                "Banda":BANDS,
                "Original":[_num(original.get(band)) for band in BANDS],
                "Controlado":[_num(controlled.get(band)) for band in BANDS],
            }).set_index("Banda")
            st.line_chart(spectral_df,use_container_width=True)
    else:
        st.info("Ingresa y guarda al menos un LAeq controlado para comenzar la comparación.")

    st.markdown("### 5 · Interpreta el resultado")
    effectiveness=st.text_area(
        "¿La medida fue suficiente y dónde produjo la mayor reducción?",
        value=str(saved.get("c4l2_s7_effectiveness") or ""),height=120,key="c4l2_s7_effectiveness_work",
        placeholder="Relaciona la reducción global y por bandas con la medida implementada.",
    )
    differences=st.text_area(
        "Explica diferencias respecto del cálculo de la Etapa 6",
        value=str(saved.get("c4l2_s7_differences") or ""),height=110,key="c4l2_s7_differences_work",
        placeholder="Considera geometría, aberturas, orientación, contribución de otras fuentes y propagación.",
    )

    if st.button("✓ Guardar y completar comparación",type="primary",use_container_width=True,key="c4l2_s7_complete"):
        stored_controlled=saved.get("c4l2_s7_controlled_results") or []
        stored_comparisons=_comparison_rows(original_rows,stored_controlled,reference_limit)
        missing=[row for row in stored_comparisons if _num(row.get("Controlado [dB(A)]")) is None]
        if not all(checks.values()):
            st.warning("Confirma las cinco condiciones de comparabilidad antes de completar la etapa.")
        elif missing:
            st.warning(f"Faltan resultados controlados para {len(missing)} combinaciones que sí tienen línea base.")
        elif len(effectiveness.strip())<40 or len(differences.strip())<40:
            st.warning("Desarrolla ambas interpretaciones con al menos 40 caracteres cada una.")
        else:
            saved["c4l2_s7_comparability"]=checks
            saved["c4l2_s7_comparison"]=stored_comparisons
            saved["c4l2_s7_effectiveness"]=effectiveness
            saved["c4l2_s7_differences"]=differences
            saved["done_7"]=True
            runtime["_save"](lab,saved,7)
            st.success("Comparación guardada. La Etapa 8 utilizará estos resultados para cerrar la solución definitiva.")

