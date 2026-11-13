"""Validated batch recovery of Course 4 / Laboratory 2 / Stage 6 front backups.

Only returns machine configurations. Does NOT mark Stage 6 complete, create
academic justifications, or modify any previous stage.
"""
from __future__ import annotations

from copy import deepcopy
import json

from labs.curso4_lab2_control_scope import _front_name, front_sources
from labs.curso4_lab2_acoustics import source_fingerprint
from labs.c4l2_stage6_checkpoint import reconcile_machine_ids

MAX_SINGLE_BYTES = 2_000_000
MAX_FILES = 6


def recover_front_backups(saved, files):
    """Validate *all* files before returning merged configs; fail atomically."""
    items = list(files or [])
    if not items or len(items) > MAX_FILES:
        raise ValueError("Selecciona entre uno y seis respaldos JSON de la Etapa 6.")

    names = list(dict.fromkeys(
        str(row.get("Etapa") or "").strip()
        for row in (saved.get("c4l2_s3_acoustic_sources") or [])
        if str(row.get("Etapa") or "").strip()
    ))
    by_key = {_front_name(name): name for name in names}
    if len(by_key) != len(names):
        raise ValueError("Hay nombres de frente ambiguos en la Etapa 3; revisa esa etapa.")

    recovered = {}
    summary = []
    for filename, payload in items:
        if len(payload) > MAX_SINGLE_BYTES:
            raise ValueError(f"{filename}: supera 2 MB.")
        try:
            doc = json.loads(payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise ValueError(f"{filename}: JSON no válido o codificación incorrecta.")
        if not isinstance(doc, dict) or doc.get("schema_version") != 2 or doc.get("stage") != 6:
            raise ValueError(f"{filename}: no es un respaldo de la Etapa 6, versión 2.")
        original = doc.get("front")
        key = _front_name(original)
        front = by_key.get(key)
        if front is None:
            raise ValueError(f"{filename}: el frente {original!r} no existe en la Etapa 3.")
        if front in recovered:
            raise ValueError(f"Hay dos archivos para el mismo frente: {front}.")
        config = doc.get("configuration")
        if not isinstance(config, dict) or config.get("scope_schema_version") != 2:
            raise ValueError(f"{filename}: no contiene una configuración de máquinas compatible.")

        entries = front_sources(saved, front)
        if not entries:
            raise ValueError(f"{filename}: no se recuperan máquinas de las etapas 3 y 4.")
        mapped, unresolved = reconcile_machine_ids(
            config.get("machines"), entries, source_fingerprint
        )
        expected_ids = {entry["id"] for entry in entries}
        if unresolved or set(mapped) != expected_ids:
            missing = len(expected_ids - set(mapped))
            raise ValueError(
                f"{filename}: no se pueden vincular todas las máquinas "
                f"({len(mapped)}/{len(entries)} recuperadas; {missing} faltantes; "
                f"{len(unresolved)} ambiguas). No se ha modificado el avance."
            )
        if doc.get("machine_count") is not None and doc["machine_count"] != len(entries):
            raise ValueError(f"{filename}: cambió la cantidad de máquinas del frente.")

        clean = deepcopy(config)
        clean["machines"] = mapped
        # This is an observation from the backup, not a new technical proposal.
        options = {str(app.get("measure") or "") for app in mapped.values()}
        if clean.get("medida") == "Seleccionar medida" and len(options) == 1:
            common = next(iter(options))
            if common in ("Silenciador", "Reducción directa", "Encierro completo",
                          "Semiencierro", "Encierro + silenciador"):
                clean["medida"] = common
        recovered[front] = clean
        summary.append((front, len(mapped), clean.get("medida", "")))

    return recovered, summary
