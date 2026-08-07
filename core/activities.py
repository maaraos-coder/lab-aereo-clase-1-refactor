"""Motor unificado de actividades del diplomado.

Centraliza el catálogo de actividades, su clasificación académica y el cálculo de
avance. No depende de Streamlit ni de Supabase: recibe filas ya recuperadas y
entrega estructuras simples que pueden usar la vista alumno y la vista docente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from config.laboratorios import COURSE_ID, FORMATIVE_PROGRESS_KEYS, LABORATORIES


OFFICIAL_EVALUATION_KEYS = frozenset({"final_comprehension", "final_integrated_design"})


@dataclass(frozen=True)
class ActivityDefinition:
    course_id: str
    laboratory: int
    class_id: str
    stage: int
    key: str
    activity_type: str
    official: bool = False

    @property
    def activity_id(self) -> str:
        return f"{self.course_id}:lab{self.laboratory}:s{self.stage}:{self.key}"


def infer_activity_type(key: str) -> str:
    """Classify an activity from its stable key without changing old keys."""
    key = str(key or "")
    if key in OFFICIAL_EVALUATION_KEYS:
        return "official_evaluation"
    if "guided" in key or "compare" in key or "compound" in key:
        return "interactive"
    if key.startswith("lab2_") and "_q" in key:
        return "comprehension"
    if key.startswith("e") and "check" in key:
        return "calculation"
    if key.startswith("s") and "q" in key:
        return "formative_exercise"
    return "formative_activity"


def build_activity_catalog(course_id: str = COURSE_ID) -> dict[str, ActivityDefinition]:
    catalog: dict[str, ActivityDefinition] = {}
    for lab_number, stages in FORMATIVE_PROGRESS_KEYS.items():
        class_id = LABORATORIES[int(lab_number)]["id"]
        for stage, keys in stages.items():
            for key in keys:
                definition = ActivityDefinition(
                    course_id=course_id,
                    laboratory=int(lab_number),
                    class_id=class_id,
                    stage=int(stage),
                    key=str(key),
                    activity_type=infer_activity_type(str(key)),
                    official=False,
                )
                catalog[definition.activity_id] = definition
    return catalog


ACTIVITY_CATALOG = build_activity_catalog()


def activity_metadata(class_id: str, stage: int, key: str) -> dict[str, Any]:
    """Return metadata persisted inside the answer JSON for future compatibility."""
    lab_number = next(
        (number for number, info in LABORATORIES.items() if info["id"] == class_id),
        None,
    )
    official = str(key) in OFFICIAL_EVALUATION_KEYS
    return {
        "laboratory": lab_number,
        "stage": int(stage),
        "key": str(key),
        "type": infer_activity_type(str(key)),
        "official": official,
        "completed": True,
    }


def _row_pair(row: Mapping[str, Any]) -> tuple[int, str]:
    return int(row.get("stage") or -1), str(row.get("question_key") or "")


def formative_progress_snapshot(
    rows: Iterable[Mapping[str, Any]],
    *,
    course_id: str = COURSE_ID,
) -> dict[int, dict[str, Any]]:
    """Calculate consistent progress from the single activity catalog.

    Existing rows with keys unknown to the catalog are ignored deliberately. This
    prevents notes, notebook entries or official evaluations from inflating the
    progress denominator. New activities only need to be registered once in
    ``FORMATIVE_PROGRESS_KEYS`` and are then reflected everywhere.
    """
    rows = list(rows or [])
    catalog = build_activity_catalog(course_id)
    by_lab: dict[int, list[ActivityDefinition]] = {number: [] for number in LABORATORIES}
    for definition in catalog.values():
        by_lab.setdefault(definition.laboratory, []).append(definition)

    result: dict[int, dict[str, Any]] = {}
    for lab_number, definitions in sorted(by_lab.items()):
        class_id = LABORATORIES[lab_number]["id"]
        saved_pairs = {
            _row_pair(row)
            for row in rows
            if str(row.get("class_id") or "") == class_id
            and str(row.get("question_key") or "") not in OFFICIAL_EVALUATION_KEYS
        }
        expected_pairs = {(item.stage, item.key) for item in definitions}
        completed_pairs = saved_pairs & expected_pairs
        stage_map: dict[int, list[ActivityDefinition]] = {}
        for item in definitions:
            stage_map.setdefault(item.stage, []).append(item)

        stage_rows = []
        for stage, items in sorted(stage_map.items()):
            expected_stage = {(item.stage, item.key) for item in items}
            completed_stage = completed_pairs & expected_stage
            expected = len(expected_stage)
            completed = len(completed_stage)
            stage_rows.append({
                "stage": stage,
                "completed": completed,
                "expected": expected,
                "percent": (100.0 * completed / expected) if expected else 0.0,
                "activities": [item.key for item in items],
            })

        expected = len(expected_pairs)
        completed = len(completed_pairs)
        result[lab_number] = {
            "expected": expected,
            "completed": completed,
            "percent": (100.0 * completed / expected) if expected else 0.0,
            "stage_rows": stage_rows,
        }
    return result
