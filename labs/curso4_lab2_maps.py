"""Carga y persistencia de mapas para el informe integral del Laboratorio 2."""

import base64
import io


MAP_STATE_KEY="c4l2_s10_maps"


def _compress(uploaded):
    from PIL import Image

    image=Image.open(uploaded).convert("RGB")
    image.thumbnail((1800,1400))
    output=io.BytesIO()
    image.save(output,format="WEBP",quality=88,method=4)
    stem=str(uploaded.name).rsplit(".",1)[0]
    return {
        "name":stem+".webp",
        "caption":stem.replace("_"," "),
        "mime":"image/webp",
        "data":base64.b64encode(output.getvalue()).decode("ascii"),
    }


def render_uploader(st,saved,runtime,lab,*,group,title,description,stage,key):
    """Muestra un cargador reutilizable y guarda los mapas dentro del avance."""
    st.markdown(f"### {title}")
    st.write(description)
    maps=dict(saved.get(MAP_STATE_KEY) or {})
    current=list(maps.get(group) or [])
    uploaded=st.file_uploader(
        "Selecciona uno o varios mapas",
        type=["png","jpg","jpeg","webp"],
        accept_multiple_files=True,
        key=f"{key}_files",
        help="Puedes utilizar capturas de planta, mapas de niveles o vistas de corte exportadas desde Noise Map Lab.",
    )
    st.caption(f"Mapas guardados en este apartado: {len(current)}")
    save_col,clear_col=st.columns([.7,.3])
    if save_col.button("Guardar mapas",type="primary",use_container_width=True,key=f"{key}_save"):
        if not uploaded:
            st.warning("Selecciona al menos un archivo antes de guardar.")
        else:
            try:
                maps[group]=[_compress(item) for item in uploaded]
                saved[MAP_STATE_KEY]=maps
                runtime["_save"](lab,saved,stage)
                st.success("Mapas guardados e incorporados al informe final.")
                st.rerun()
            except Exception as exc:
                st.error(f"No fue posible procesar uno de los mapas: {exc}")
    if clear_col.button("Quitar mapas",use_container_width=True,key=f"{key}_clear",disabled=not current):
        maps[group]=[]
        saved[MAP_STATE_KEY]=maps
        runtime["_save"](lab,saved,stage)
        st.rerun()

    if current:
        st.markdown("**Vista previa de la evidencia guardada**")
        columns=st.columns(2)
        for index,item in enumerate(current):
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

