"""Editor docente y capa de contenido publicable para la Plataforma Diplomado."""

from __future__ import annotations

import copy
import json
import re
import uuid
from typing import Any

import streamlit as st


EMPTY_CONTENT = {
    "title": "",
    "objective": "",
    "content_markdown": "",
    "activity_markdown": "",
    "teacher_solution": "",
    "media": [],
    "minutes": 20,
    "replace_base": False,
}


def _render_media(items: list[dict]) -> None:
    for item in items or []:
        url = item.get("url", "")
        if not url:
            continue
        title = item.get("title") or item.get("name") or "Recurso de apoyo"
        caption = item.get("caption", "")
        kind = item.get("kind", "image")
        if kind == "image":
            st.image(url, caption=caption or title, use_container_width=True)
        else:
            st.link_button(f"📄 Abrir {title}", url, use_container_width=True)
            if caption:
                st.caption(caption)


def render_media(items: list[dict]) -> None:
    """Render stage media without repeating the editable text blocks."""
    _render_media(items)


def _upload_media(client, uploaded, class_id: str, stage: int) -> dict:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", uploaded.name).strip("-") or "archivo"
    object_path = f"{class_id}/etapa-{stage}/{uuid.uuid4().hex[:12]}-{safe_name}"
    client.storage.from_("diplomado-media").upload(
        object_path,
        uploaded.getvalue(),
        {"content-type": uploaded.type or "application/octet-stream", "upsert": "false"},
    )
    public = client.storage.from_("diplomado-media").get_public_url(object_path)
    url = public if isinstance(public, str) else public.get("publicUrl") or public.get("publicURL")
    return {
        "path": object_path,
        "url": url,
        "name": uploaded.name,
        "kind": "image" if (uploaded.type or "").startswith("image/") else "pdf",
        "title": "",
        "caption": "",
    }


def _decode(value: Any) -> dict:
    if not value:
        return {}
    if isinstance(value, dict):
        return copy.deepcopy(value)
    try:
        decoded = json.loads(value)
        return decoded if isinstance(decoded, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def _row(client, class_id: str, stage: int) -> dict:
    if client is None:
        return {}
    try:
        rows = (
            client.table("cms_stage_content")
            .select("*")
            .eq("class_id", class_id)
            .eq("stage", int(stage))
            .limit(1)
            .execute()
            .data
            or []
        )
        return rows[0] if rows else {}
    except Exception:
        return {}


def get_content(client, class_id: str, stage: int, role: str = "Alumno") -> dict:
    """Return the published version, or a teacher's explicitly selected draft preview."""
    row = _row(client, class_id, stage)
    if not row:
        return {}
    preview = (
        role == "Docente"
        and st.session_state.get("cms_preview_class") == class_id
        and st.session_state.get("cms_preview_stage") == int(stage)
    )
    source = row.get("draft_content") if preview else row.get("published_content")
    return _decode(source)


def stage_label(client, class_id: str, stage: int, fallback: str, role: str) -> str:
    content = get_content(client, class_id, stage, role)
    return content.get("title") or fallback


def render_override(client, class_id: str, stage: int, role: str) -> bool:
    """Render a complete replacement when a published/draft override requests it."""
    content = get_content(client, class_id, stage, role)
    if not content or not content.get("replace_base"):
        return False
    st.markdown(f"## {content.get('title') or f'Etapa {stage}'}")
    if content.get("objective"):
        st.info(content["objective"])
    if content.get("content_markdown"):
        st.markdown(content["content_markdown"])
    if content.get("activity_markdown"):
        st.markdown("### Actividad")
        st.markdown(content["activity_markdown"])
    _render_media(content.get("media", []))
    if role == "Docente" and content.get("teacher_solution"):
        with st.expander("🔐 Solución y orientación docente"):
            st.markdown(content["teacher_solution"])
    if role == "Docente" and (
        st.session_state.get("cms_preview_class") == class_id
        and st.session_state.get("cms_preview_stage") == int(stage)
    ):
        st.warning("Vista previa del borrador. Los alumnos todavía no ven estos cambios.")
    return True


def append_content(client, class_id: str, stage: int, role: str) -> None:
    """Append editable additions when the teacher chose to retain the base stage."""
    content = get_content(client, class_id, stage, role)
    if not content or content.get("replace_base"):
        return
    if any(content.get(key) for key in ("content_markdown", "activity_markdown")):
        st.markdown("---")
        if content.get("title"):
            st.markdown(f"## {content['title']}")
        if content.get("objective"):
            st.info(content["objective"])
        if content.get("content_markdown"):
            st.markdown(content["content_markdown"])
        if content.get("activity_markdown"):
            st.markdown("### Actividad adicional")
            st.markdown(content["activity_markdown"])
        _render_media(content.get("media", []))
    if role == "Docente" and content.get("teacher_solution"):
        with st.expander("🔐 Solución y orientación docente"):
            st.markdown(content["teacher_solution"])


def apply_fields(client, class_id: str, stage: int, role: str, defaults: dict) -> dict:
    """Overlay editable fields on data-driven future laboratory content."""
    result = copy.deepcopy(defaults)
    content = get_content(client, class_id, stage, role)
    if not content:
        return result
    for key in ("title", "objective", "content_markdown", "activity_markdown", "teacher_solution", "minutes", "media"):
        if content.get(key) not in ("", None):
            result[key] = content[key]
    result["_cms_preview"] = (
        role == "Docente"
        and st.session_state.get("cms_preview_class") == class_id
        and st.session_state.get("cms_preview_stage") == int(stage)
    )
    return result


def _save_draft(client, class_id: str, stage: int, content: dict, now: str, user: str) -> None:
    client.table("cms_stage_content").upsert(
        {
            "class_id": class_id,
            "stage": int(stage),
            "draft_content": content,
            "draft_updated_at": now,
            "draft_updated_by": user,
        },
        on_conflict="class_id,stage",
    ).execute()


def _publish(client, class_id: str, stage: int, now: str, user: str) -> None:
    row = _row(client, class_id, stage)
    draft = _decode(row.get("draft_content"))
    if not draft:
        raise ValueError("Primero guarda un borrador.")
    version = int(row.get("published_version") or 0) + 1
    client.table("cms_stage_versions").insert(
        {
            "class_id": class_id,
            "stage": int(stage),
            "version": version,
            "content": draft,
            "published_at": now,
            "published_by": user,
        }
    ).execute()
    client.table("cms_stage_content").update(
        {
            "published_content": draft,
            "published_version": version,
            "published_at": now,
            "published_by": user,
        }
    ).eq("class_id", class_id).eq("stage", int(stage)).execute()


def _restore(client, class_id: str, stage: int, version: int, now: str, user: str) -> None:
    rows = (
        client.table("cms_stage_versions")
        .select("content")
        .eq("class_id", class_id)
        .eq("stage", int(stage))
        .eq("version", int(version))
        .limit(1)
        .execute()
        .data
        or []
    )
    if not rows:
        raise ValueError("La versión seleccionada ya no está disponible.")
    _save_draft(client, class_id, stage, _decode(rows[0]["content"]), now, user)


@st.dialog("Editor de contenidos del Diplomado", width="large")
def editor_dialog(client, catalog: list[dict], now_fn, current_class: str | None = None, current_stage: int = 0):
    if client is None:
        st.error("El editor necesita la conexión privada con Supabase.")
        return
    st.caption("Los cambios se guardan primero como borrador. Solo «Publicar» modifica la vista del alumno.")
    labels = {
        item["id"]: f"{item['course']} · Laboratorio {item['lab']}"
        for item in catalog
    }
    ids = list(labels)
    default_index = ids.index(current_class) if current_class in ids else 0
    class_id = st.selectbox(
        "Curso y laboratorio",
        ids,
        index=default_index,
        format_func=lambda value: labels[value],
        key="cms_editor_class",
    )
    item = next(entry for entry in catalog if entry["id"] == class_id)
    stage = st.selectbox(
        "Etapa",
        list(range(len(item["stages"]))),
        index=min(int(current_stage), len(item["stages"]) - 1),
        format_func=lambda value: f"Etapa {value} · {item['stages'][value]['title']}",
        key=f"cms_editor_stage_{class_id}",
    )
    base = item["stages"][stage]
    row = _row(client, class_id, stage)
    draft = _decode(row.get("draft_content"))
    published = _decode(row.get("published_content"))
    initial = dict(EMPTY_CONTENT)
    initial.update(
        {
            "title": base.get("title", ""),
            "objective": base.get("objective", ""),
            "content_markdown": base.get("content_markdown", ""),
            "activity_markdown": base.get("activity_markdown", ""),
            "teacher_solution": base.get("teacher_solution", ""),
            "minutes": int(base.get("minutes") or 20),
        }
    )
    initial.update(draft)

    status = (
        f"Versión publicada: {row.get('published_version') or 'ninguna'}"
        if published
        else "Esta etapa todavía usa exclusivamente el contenido base."
    )
    st.info(status)
    title = st.text_input("Título de la etapa", value=initial["title"])
    objective = st.text_area("Objetivo o bajada", value=initial["objective"], height=90)
    minutes = st.number_input("Duración (minutos)", 1, 240, int(initial["minutes"]))
    replace_base = st.toggle(
        "Reemplazar completamente el contenido base",
        value=bool(initial.get("replace_base")),
        help="Desactivado: agrega contenido al final. Activado: el alumno verá esta versión en lugar de la etapa programada.",
    )
    media_key = f"cms_media_{class_id}_{stage}"
    if media_key not in st.session_state:
        st.session_state[media_key] = copy.deepcopy(initial.get("media", []))
    tab_content, tab_activity, tab_media, tab_teacher, tab_preview, tab_history = st.tabs(
        ["Contenido", "Actividad", "Imágenes y PDF", "Solución docente", "Vista previa", "Historial"]
    )
    with tab_content:
        content = st.text_area(
            "Desarrollo técnico (admite Markdown)",
            value=initial["content_markdown"],
            height=330,
            help="Usa ## para subtítulos, **texto** para negrita y tablas Markdown cuando corresponda.",
        )
    with tab_activity:
        activity = st.text_area(
            "Consigna o actividad para el alumno",
            value=initial["activity_markdown"],
            height=260,
        )
    with tab_media:
        st.caption("Los archivos quedan asociados a esta etapa. PNG, JPG, WEBP y GIF se muestran dentro de la clase; los PDF quedan como material de consulta.")
        uploaded = st.file_uploader(
            "Subir imagen o PDF",
            type=["png", "jpg", "jpeg", "webp", "gif", "pdf"],
            key=f"cms_upload_{class_id}_{stage}",
        )
        media_title = st.text_input("Título del recurso", key=f"cms_media_title_{class_id}_{stage}")
        media_caption = st.text_input("Pie o descripción", key=f"cms_media_caption_{class_id}_{stage}")
        if st.button("Agregar a la etapa", key=f"cms_add_media_{class_id}_{stage}", disabled=uploaded is None):
            try:
                item_media = _upload_media(client, uploaded, class_id, stage)
                item_media["title"] = media_title.strip()
                item_media["caption"] = media_caption.strip()
                st.session_state[media_key].append(item_media)
                st.success("Archivo cargado. Guarda el borrador o publica para conservar su ubicación en la etapa.")
            except Exception as exc:
                st.error(f"No fue posible cargar el archivo: {exc}")
        current_media = st.session_state.get(media_key, [])
        if current_media:
            st.markdown("#### Recursos incorporados")
            remove = []
            for index, media in enumerate(current_media):
                left, right = st.columns([4, 1])
                left.write(f"{'🖼️' if media.get('kind') == 'image' else '📄'} {media.get('title') or media.get('name')}")
                if right.checkbox("Quitar", key=f"cms_remove_media_{class_id}_{stage}_{index}"):
                    remove.append(index)
            if remove:
                st.session_state[media_key] = [
                    media for index, media in enumerate(current_media) if index not in remove
                ]
    with tab_teacher:
        teacher_solution = st.text_area(
            "Respuesta esperada, pauta y orientación",
            value=initial["teacher_solution"],
            height=260,
            help="Este campo es exclusivo del perfil Docente.",
        )
    candidate = {
        "title": title.strip(),
        "objective": objective.strip(),
        "content_markdown": content,
        "activity_markdown": activity,
        "teacher_solution": teacher_solution,
        "media": copy.deepcopy(st.session_state.get(media_key, [])),
        "minutes": int(minutes),
        "replace_base": bool(replace_base),
    }
    with tab_preview:
        st.markdown(f"## {candidate['title'] or f'Etapa {stage}'}")
        if candidate["objective"]:
            st.info(candidate["objective"])
        if candidate["content_markdown"]:
            st.markdown(candidate["content_markdown"])
        if candidate["activity_markdown"]:
            st.markdown("### Actividad")
            st.markdown(candidate["activity_markdown"])
        _render_media(candidate.get("media", []))
        st.caption("La solución docente se oculta en esta previsualización.")
    with tab_history:
        versions = (
            client.table("cms_stage_versions")
            .select("version,published_at,published_by")
            .eq("class_id", class_id)
            .eq("stage", int(stage))
            .order("version", desc=True)
            .execute()
            .data
            or []
        )
        if not versions:
            st.caption("Todavía no existen versiones publicadas.")
        else:
            version = st.selectbox(
                "Versión para recuperar",
                [int(value["version"]) for value in versions],
                format_func=lambda value: f"Versión {value}",
            )
            if st.button("Restaurar esta versión como borrador"):
                _restore(client, class_id, stage, version, now_fn(), st.session_state.get("name", "Docente"))
                st.success("Versión restaurada como borrador. Aún no está publicada.")
                st.rerun()

    save, preview, publish = st.columns(3)
    if save.button("Guardar borrador", type="primary", use_container_width=True):
        _save_draft(client, class_id, stage, candidate, now_fn(), st.session_state.get("name", "Docente"))
        st.success("Borrador guardado. La vista del alumno no cambió.")
        st.rerun()
    if preview.button("Previsualizar en la clase", use_container_width=True):
        _save_draft(client, class_id, stage, candidate, now_fn(), st.session_state.get("name", "Docente"))
        st.session_state["cms_preview_class"] = class_id
        st.session_state["cms_preview_stage"] = int(stage)
        if class_id != current_class:
            st.warning("Borrador guardado. Abre ese laboratorio para verlo dentro de la clase.")
        else:
            st.rerun()
    confirm = st.checkbox("Confirmo que deseo publicar esta versión para los alumnos.")
    if publish.button("Publicar", disabled=not confirm, use_container_width=True):
        _save_draft(client, class_id, stage, candidate, now_fn(), st.session_state.get("name", "Docente"))
        _publish(client, class_id, stage, now_fn(), st.session_state.get("name", "Docente"))
        st.session_state.pop("cms_preview_class", None)
        st.session_state.pop("cms_preview_stage", None)
        st.success("Nueva versión publicada para los alumnos que tengan acceso al laboratorio.")
        st.rerun()


def editor_button(client, catalog: list[dict], now_fn, current_class: str | None = None, current_stage: int = 0):
    if st.button("✏️ Editar contenido", use_container_width=True, type="primary"):
        editor_dialog(client, catalog, now_fn, current_class, current_stage)
