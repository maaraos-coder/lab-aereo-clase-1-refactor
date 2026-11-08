"""Pure JSONB delta builder for Curso 4 Laboratorio 2 saves.

Never resend historical maps when only a source treatment changes.
"""


def changed_progress_fields(last_persisted, current):
    if not isinstance(last_persisted, dict) or not isinstance(current, dict):
        raise TypeError("Los avances deben ser diccionarios.")
    return {key: value for key, value in current.items()
            if key not in last_persisted or last_persisted[key] != value}


def save_progress_changes(client, progress_row, changes):
    patch = {
        "p_class_id": progress_row["class_id"],
        "p_user_key": progress_row["user_key"],
        "p_changes": changes,
    }
    result = client.rpc("patch_c4l2_progress", patch).execute()
    if result.data is True:
        return
    if result.data is not False:
        raise RuntimeError("No se pudo confirmar la actualización parcial del progreso.")

    # The RPC updates existing rows only. Insert the first draft without
    # replacing progress if another session created the row in the meantime.
    try:
        client.table("user_progress").insert(
            {**progress_row, "state_json": changes}, returning="minimal"
        ).execute()
    except Exception as error:
        if getattr(error, "code", None) != "23505":
            raise
        result = client.rpc("patch_c4l2_progress", patch).execute()
        if result.data is not True:
            raise RuntimeError("No se pudo confirmar la actualización parcial del progreso.") from error
