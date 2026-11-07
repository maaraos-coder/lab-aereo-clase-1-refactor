"""Pure JSONB delta builder for Curso 4 Laboratorio 2 saves.

Never resend historical maps when only a source treatment changes.
"""


def changed_progress_fields(last_persisted, current):
    if not isinstance(last_persisted, dict) or not isinstance(current, dict):
        raise TypeError("Los avances deben ser diccionarios.")
    return {key: value for key, value in current.items()
            if key not in last_persisted or last_persisted[key] != value}
