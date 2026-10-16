"""Controles compartidos para guardar borradores del Laboratorio 2."""


def render_draft_save(st, saved, runtime, lab, stage, updates, key):
    """Guarda el estado visible sin marcar la etapa como completada."""
    role = st.session_state.get("role")
    if role == "Docente" or role == "Proyección" or st.session_state.get("projection_mode"):
        return False

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
        saved.update(updates)
        runtime["_save"](lab, saved, stage)
        st.success("Avance guardado. Puedes cambiar de etapa o salir y continuar más tarde.")
        return True
    return False
