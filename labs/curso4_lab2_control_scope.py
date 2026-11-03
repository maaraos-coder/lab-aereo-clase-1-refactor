"""Aplicación trazable de tratamientos a equipos y recomposición del frente."""
from copy import deepcopy
import hashlib
import math
import re

from labs.curso4_lab2_acoustics import (
    BAND_LABELS, equivalent_spectrum, parse_level, source_fingerprint,
    sum_levels, weighted_power,
)
from labs import curso4_control_models as model

NO_CONTROL = "Sin tratamiento en la fuente"
KINDS = {"Encierro completo":"enclosure", "Semiencierro":"semi",
         "Encierro + silenciador":"enclosure_silencer", "Silenciador":"silencer",
         "Reducción directa":"direct"}
APPLICATION_OPTIONS = ["Seleccionar aplicación", NO_CONTROL] + list(KINDS)


def _front_name(value):
    return re.sub(r"^FT\d+\s*[·:–-]\s*", "", str(value or "")).strip().casefold()


def front_sources(saved, front):
    """Solo las fuentes del frente exacto y su simultaneidad original."""
    name = _front_name(front)
    scenarios = [s for s in saved.get("c4l2_s4_scenarios", []) if _front_name(s.get("Etapa")) == name]
    simultaneous = scenarios[0].get("Máquinas simultáneas") if scenarios else None
    configs = saved.get("c4l2_s4_front_configs") or {}
    if simultaneous is None:
        rows = next((rows for key, rows in configs.items() if _front_name(key) == name), None)
        if rows is not None:
            simultaneous = [r.get("Máquina") for r in rows if r.get("¿Simultánea?") == "Sí"]
    output = []
    for index, source in enumerate(saved.get("c4l2_s3_acoustic_sources") or []):
        if _front_name(source.get("Etapa")) != name:
            continue
        if simultaneous is not None and source.get("Máquina / equipo proyecto") not in simultaneous:
            continue
        identity = f"{name}|{index}|{source.get('Máquina / equipo proyecto')}"
        output.append({"id":hashlib.sha256(identity.encode()).hexdigest()[:16], "source":deepcopy(source)})
    return output


def application_reduction(source, application, require_evidence=True):
    measure = application.get("measure")
    if measure not in (NO_CONTROL, *KINDS):
        raise ValueError("Selecciona una aplicación para esta máquina.")
    if application.get("source_signature") != source_fingerprint([source]):
        raise ValueError("Revisa la aplicación: cambió la fuente original o falta vincularla.")
    if measure == NO_CONTROL:
        return [0.] * 8, 0
    if measure not in KINDS:
        raise ValueError("Selecciona una aplicación para cada máquina.")
    if require_evidence and not str(application.get("evidence") or "").strip():
        raise ValueError("Documenta el respaldo técnico y la compatibilidad del tratamiento.")
    quantity = parse_level(source.get("Cantidad"))
    treated = parse_level(application.get("treated_units"))
    if treated is None or not treated.is_integer() or not 1 <= treated <= quantity:
        raise ValueError("Indica cuántas unidades reciben tratamiento, sin superar la cantidad original.")
    treatment = application.get("treatment") or {}
    if treatment.get("noise_control_type") != KINDS[measure]:
        raise ValueError("El cálculo no corresponde a la medida elegida para esa máquina.")
    if measure == "Silenciador" and not application.get("effective_machine_reduction"):
        raise ValueError("La IL de un escape no atenúa toda la máquina. Justifica una reducción efectiva del equipo o modela la componente separadamente.")
    reductions = []
    for frequency in model.OCTAVE_BANDS:
        if KINDS[measure] in ("enclosure", "semi", "enclosure_silencer"):
            try:
                reduction = model.enclosure_balance(treatment, frequency)[1]
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError("Completa la geometría y las superficies del tratamiento.") from error
        else:
            field = "silencer_il_db" if measure == "Silenciador" else "control_reduction_db"
            reduction = (treatment.get(field) or {}).get(str(frequency))
        reduction = parse_level(reduction)
        if reduction is None or reduction < 0:
            raise ValueError("Se necesita una reducción de potencia válida para cada banda.")
        reductions.append(reduction)
    return reductions, int(treated)


def recombine_front(entries, applications, strict=False):
    """Suma unidades tratadas y no tratadas; nunca aplica ΔLp de una barrera."""
    if not entries:
        raise ValueError("Guarda las máquinas y la simultaneidad original de este frente en las Etapas 3 y 4.")
    original_contributions, original = equivalent_spectrum([entry["source"] for entry in entries])
    controlled_contributions, rows, pending, provisional = [], [], [], []
    for entry, original_machine in zip(entries, original_contributions):
        source = entry["source"]
        application = applications.get(entry["id"], {})
        status = "Calculado"
        try:
            reductions, treated = application_reduction(source, application, require_evidence=strict)
        except ValueError as error:
            if strict:
                raise ValueError(f"{source.get('Máquina / equipo proyecto')}: {error}") from error
            reductions, treated = [0.] * 8, 0
            status = "Pendiente: se conserva la emisión original"
            pending.append(f"{source.get('Máquina / equipo proyecto')}: {error}")
        else:
            if application.get("measure") == NO_CONTROL:
                status = "Sin tratamiento declarado"
            elif not str(application.get("evidence") or "").strip():
                status = "Estimación provisional: falta justificación"
                provisional.append(str(source.get("Máquina / equipo proyecto")))
        quantity = int(parse_level(source["Cantidad"]))
        controlled = []
        for power, reduction in zip(source["Lw_bandas"], reductions):
            components = []
            if quantity > treated:
                components.append(float(power) + 10 * math.log10(quantity - treated))
            if treated:
                components.append(float(power) - reduction + 10 * math.log10(treated))
            controlled.append(sum_levels(components))
        controlled_contributions.append(controlled)
        rows.append({"machine_id":entry["id"], "Máquina":source.get("Máquina / equipo proyecto"),
                     "Medida":applications.get(entry["id"],{}).get("measure","Seleccionar aplicación"),
                     "Estado":status,
                     "Unidades originales":quantity, "Unidades tratadas":treated,
                     "Lw_original":original_machine, "Lw_controlado":controlled})
    controlled = [sum_levels(band) for band in zip(*controlled_contributions)]
    return {"band_labels":list(BAND_LABELS), "original":original, "controlled":controlled,
            "original_lwa":weighted_power(original), "controlled_lwa":weighted_power(controlled),
            "machines":rows, "pending":pending, "provisional":provisional, "scope":"emitted_power_only"}


def validate_scope(saved, front, config):
    if config.get("scope_schema_version") != 2:
        raise ValueError("Asigna las medidas a las máquinas; el diseño anterior del frente se conserva para revisión.")
    entries = front_sources(saved, front)
    result = recombine_front(entries, config.get("machines") or {}, strict=True)
    propagation = config.get("propagation") or {}
    if config.get("medida") == "Barrera acústica" and not propagation.get("enabled"):
        raise ValueError("Configura la barrera de la estrategia elegida.")
    if propagation.get("enabled"):
        ids = {entry["id"] for entry in entries}
        targets = propagation.get("protected_ids") or []
        if not targets or not set(targets) <= ids:
            raise ValueError("Identifica las máquinas cuyo camino al receptor se pretende apantallar.")
        if not str(propagation.get("ubicacion") or "").strip() or not str(propagation.get("receptor") or "").strip():
            raise ValueError("Identifica el tramo de barrera y el receptor protegido.")
        if propagation.get("calculo") is None:
            raise ValueError("Completa un cálculo geométrico válido de la barrera.")
        geometry = [parse_level(propagation.get(key)) for key in
                    ("altura_m", "longitud_m", "distancia_fr_m", "distancia_fb_m", "altura_fuente_m", "altura_receptor_m")]
        if any(value is None or value <= 0 for value in geometry) or geometry[3] >= geometry[2]:
            raise ValueError("Revisa la geometría: la barrera debe estar entre fuente y receptor.")
    applied = any(app.get("measure") in KINDS for key, app in (config.get("machines") or {}).items()
                  if key in {entry["id"] for entry in entries})
    if not applied and not propagation.get("enabled"):
        raise ValueError("La estrategia debe identificar al menos una máquina tratada o una barrera.")
    return result


def render_scope(st, pd, saved, front, strategy, previous, prefix, workshop, study_cfg, tl_spectrum):
    """Una configuración independiente por equipo y otra para propagación."""
    config = deepcopy(previous or {})
    if config and config.get("scope_schema_version") != 2:
        config = {"legacy_front_configuration":config}
        st.info("Se conserva la configuración anterior del frente. Asígnala explícitamente a las máquinas que corresponda antes de finalizar.")
    config.update({"medida":strategy, "scope_schema_version":2})
    entries = front_sources(saved, front)
    if not entries:
        st.warning("No hay máquinas originales recuperadas para este frente. Guarda su caracterización en la Etapa 3 y su simultaneidad en la Etapa 4; no se cargarán equipos ni niveles de ejemplo como solución.")
        return config
    try:
        equivalent_spectrum([entry["source"] for entry in entries])
    except ValueError as error:
        st.warning(str(error))
        return config
    st.markdown("#### A · Tratamientos aplicados a las máquinas")
    st.caption("Configura cada equipo por separado. Puedes usar medidas diferentes dentro de un mismo frente o declarar expresamente los equipos sin tratamiento. Si hay varias unidades, indica cuántas reciben la medida.")
    applications = config.setdefault("machines", {})
    labels = {entry["id"]:f"{i} · {entry['source']['Máquina / equipo proyecto']} ×{entry['source']['Cantidad']}" for i, entry in enumerate(entries, 1)}
    selected_id = st.selectbox("Máquina a configurar", list(labels), format_func=labels.get, key=prefix+"_machine")
    source = next(entry["source"] for entry in entries if entry["id"] == selected_id)
    old = applications.get(selected_id, {})
    option = old.get("measure", "Seleccionar aplicación")
    measure_key=prefix+"_"+selected_id+"_measure"
    # Mantener un índice constante: cambiar el valor inicial en cada rerun puede
    # recrear el widget y devolver la selección anterior al reconstruir la ficha.
    if measure_key not in st.session_state:
        st.session_state[measure_key]=option if option in APPLICATION_OPTIONS else APPLICATION_OPTIONS[0]
    measure = st.selectbox("Aplicación sobre esta máquina", APPLICATION_OPTIONS, key=measure_key)
    machine_prefix = prefix+"_"+selected_id+"_"+hashlib.sha1(measure.encode()).hexdigest()[:8]
    application = deepcopy(old) if old.get("measure") == measure else {}
    signature = source_fingerprint([source])
    application["measure"] = measure
    changed_source = bool(old.get("source_signature") and old["source_signature"] != signature)
    reviewed = True
    if changed_source:
        st.warning("Cambió la caracterización original de esta máquina. Revisa cantidad, espectro y compatibilidad del tratamiento.")
        reviewed = st.checkbox("Revisé esta aplicación con la fuente original actualizada.", value=False,
                               key=machine_prefix+"_review_"+signature)
    if reviewed:
        application["source_signature"] = signature
    if measure in KINDS:
        application["treated_units"] = st.number_input("Unidades de esta máquina que reciben tratamiento", min_value=1,
            max_value=int(parse_level(source["Cantidad"])), value=min(int(parse_level(source["Cantidad"])),int(application.get("treated_units") or 1)), step=1, key=machine_prefix+"_units_"+signature)
        initial = application.get("treatment") or model.default_treatment(KINDS[measure])
        use_study = st.checkbox("Usar los parámetros de la práctica como punto de partida", value=False, key=machine_prefix+"_practice")
        if use_study:
            if study_cfg.get("noise_control_type") == KINDS[measure]:
                initial = deepcopy(study_cfg)
            else:
                st.warning("La práctica debe usar el mismo tipo de tratamiento que esta máquina.")
        designer_prefix=machine_prefix+("_practice" if use_study else "_design")
        treatment, calculation = workshop.render_designer(st,pd,designer_prefix,initial,
            fixed_kind=KINDS[measure],suggested_tl=tl_spectrum,
            source_lw=dict(zip(map(str,model.OCTAVE_BANDS),source["Lw_bandas"])),
            source_label=str(source["Máquina / equipo proyecto"]))
        application.update({"treatment":treatment,"calculo":calculation})
        application["evidence"] = st.text_area("Respaldo técnico y compatibilidad con esta máquina",
            value=str(application.get("evidence") or ""), key=machine_prefix+"_evidence",
            help="Identifica datos técnicos, mediciones o hipótesis docentes justificadas. Se exige para finalizar, pero no bloquea la estimación provisional. El TL del panel y la reducción final en el receptor son magnitudes distintas.")
        st.caption("Puedes explorar la reducción con los parámetros actuales aunque este texto esté vacío. La justificación y la viabilidad de la medida se revisan antes de finalizar; el cálculo no decide por sí solo si una máquina móvil puede operar dentro del encierro.")
        if measure == "Silenciador":
            st.warning("Un silenciador actúa sobre una emisión canalizada. Si solo trata el escape, su IL no puede descontarse de toda la máquina: separa esa componente en Noise Map Lab o justifica la reducción efectiva del equipo completo.")
            application["effective_machine_reduction"] = st.checkbox("Los valores ingresados representan una reducción efectiva justificada de la emisión total de la máquina modelada.", value=bool(application.get("effective_machine_reduction")), key=machine_prefix+"_effective")
    applications[selected_id] = application
    st.markdown("#### B · Barrera en el camino fuente–receptor")
    propagation = deepcopy(config.get("propagation") or {})
    propagation["enabled"] = st.checkbox("Incorporar una barrera en este frente", value=bool(propagation.get("enabled") or strategy=="Barrera acústica"), key=prefix+"_barrier_enabled")
    if propagation["enabled"]:
        st.info("La barrera no cambia el Lw de las máquinas. Su efecto depende de cada camino F–R. No se aplicará la atenuación del ejemplo al espectro de potencia del frente.")
        propagation["protected_ids"] = st.multiselect("Máquinas cuyo camino al receptor se pretende apantallar",list(labels),default=[i for i in propagation.get("protected_ids",[]) if i in labels],format_func=labels.get,key=prefix+"_barrier_targets")
        barrier, calculation = workshop.render_barrier_calculator(st,pd,prefix+"_barrier",propagation)
        st.caption("La calculadora de barrera es un ejemplo de un único camino F–R; sus niveles no son la predicción del frente ni se reutilizan como una reducción uniforme. Evalúa cada camino real en Noise Map Lab.")
        propagation.update(barrier)
        propagation["calculo"] = calculation
        propagation["ubicacion"] = st.text_input("Ubicación / tramo protegido",value=str(propagation.get("ubicacion") or ""),key=prefix+"_barrier_location")
        propagation["receptor"] = st.text_input("Receptor / posición crítica que se evaluará",value=str(propagation.get("receptor") or ""),key=prefix+"_barrier_receptor")
        propagation["densidad_kgm2"] = st.number_input("Masa superficial del panel [kg/m²]",min_value=1.,max_value=200.,value=float(propagation.get("densidad_kgm2",10.)),step=1.,key=prefix+"_barrier_mass")
        st.caption("Comprueba en planta y corte qué máquinas quedan protegidas. Si importa su posición, altura u orientación, representa las máquinas por separado; no extiendas el apantallamiento a todo el frente por usar una fuente equivalente.")
    config["propagation"] = propagation
    st.markdown("#### C · Recompón la potencia del frente controlado")
    try:
        result = recombine_front(entries, applications)
    except ValueError as error:
        st.warning(str(error))
        return config
    config["controlled_front"] = result
    st.dataframe(pd.DataFrame([{"Máquina":row["Máquina"],"Medida":row["Medida"],"Estado":row["Estado"],"Unidades originales":row["Unidades originales"],"Unidades tratadas":row["Unidades tratadas"],"Reducción LWA del equipo [dB]":round(weighted_power(row["Lw_original"])-weighted_power(row["Lw_controlado"]),2)} for row in result["machines"]]),hide_index=True,use_container_width=True)
    if result["pending"]:
        st.warning("Las máquinas sin una aplicación válida conservan su emisión original. Los tratamientos válidos de las demás máquinas sí se incluyen en el cálculo.")
        for message in result["pending"]: st.caption(message)
    if result["provisional"]:
        st.info("Estimación provisional calculada con los parámetros configurados. Falta justificar antes de finalizar: "+", ".join(result["provisional"])+". La falta de ese texto no anula el tratamiento.")
    st.dataframe(pd.DataFrame({"Banda":BAND_LABELS,"Lw original del frente [dB]":result["original"],"Lw con tratamientos de fuente [dB]":result["controlled"],"Reducción ΔLw del frente [dB]":[round(a-b,2) for a,b in zip(result["original"],result["controlled"])]}),hide_index=True,use_container_width=True)
    st.metric("LWA del frente con tratamientos de fuente",f"{result['controlled_lwa']:.2f} dB(A)")
    st.metric("Reducción de potencia del frente · ΔLWA",f"{result['original_lwa']-result['controlled_lwa']:.2f} dB")
    st.caption("Se suman energéticamente las unidades tratadas y las no tratadas. Este es un balance de potencia emitida, no el LAeq en el receptor. La barrera, la orientación de las caras y la geometría se evalúan en Noise Map Lab. Los parámetros de ejemplo requieren respaldo antes de finalizar.")
    st.info("Para implementar controles individuales en Noise Map Lab, sustituye la fuente equivalente por sus máquinas en una copia del original. No coloques un encierro de una máquina sobre la fuente que agrupa todo el frente. La sección 7 explica cómo crear y comparar las copias por máquinas.")
    return config
