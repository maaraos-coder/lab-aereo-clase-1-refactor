"""Controles compartidos para guardar borradores del Laboratorio 2."""


def render_draft_save(st, saved, runtime, lab, stage, updates, key):
    """Guarda el estado visible sin marcar la etapa como completada."""
    from copy import deepcopy
    from labs.curso4_lab2_projection import is_projection, cache_key
    projection = is_projection(st)
    # Cada edición confirmada por el formulario llega en un rerun de Streamlit.
    # Se guarda solo si cambia el contenido, sin finalizar ni evaluar la etapa.
    if projection:
        persisted = st.session_state.get(cache_key(lab["id"]) + "_persisted", {})
        changed = any(persisted.get(k) != v for k, v in updates.items())
        if changed:
            candidate = deepcopy(saved)
            candidate.update(updates)
            try:
                runtime["_save"](lab, candidate, stage)
            except Exception:
                st.warning("No se pudo guardar el último cambio. Mantén esta ventana abierta y pulsa Guardar avance cuando vuelva la conexión.")
            else:
                saved.update(candidate)
                st.caption("✓ Avance de la clase guardado automáticamente.")
        else:
            st.caption("✓ Avance de la clase guardado.")

    st.markdown(
        """
        <div style="border:1px solid #b9d9e8;border-left:5px solid #0b7fa5;border-radius:16px;
                    padding:14px 17px;background:linear-gradient(135deg,#f8fcff,#eef8fc);
                    margin:1rem 0 .55rem">
          <div style="font-size:.72rem;font-weight:900;letter-spacing:.08em;color:#087ba0">
            GUARDADO DE BORRADOR
          </div>
          <div style="font-size:1rem;font-weight:850;color:#173b53;margin:.2rem 0">
            Conserva tu avance antes de cambiar de etapa o salir
          </div>
          <div style="color:#526f80;line-height:1.5">
            Este botón guarda tablas, selecciones y textos visibles. No finaliza la etapa ni exige que todo esté completo.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("💾 Guardar avance de esta etapa", use_container_width=True, key=key):
        candidate = deepcopy(saved)
        candidate.update(updates)
        try:
            runtime["_save"](lab, candidate, stage)
        except Exception:
            st.error("No se pudo guardar el avance. Revisa la conexión y vuelve a intentarlo.")
            return False
        saved.update(candidate)
        st.success("Avance guardado. Puedes cambiar de etapa o salir y continuar más tarde.")
        return True
    return False
