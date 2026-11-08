"""Non-destructive regression tests for C4L2 partial Supabase writes."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
from labs.c4l2_progress_patch import changed_progress_fields, save_progress_changes


class DeltaSaveTests(unittest.TestCase):
    def test_treatment_changes_do_not_resend_heavy_maps(self):
        original = {
            "c4l2_s10_maps": {"original": [{"data": "A" * 5_000_000}]},
            "c4l2_s6_measure_config": {"FT1": {"measure": "Sin tratamiento"}},
            "done_3": True,
        }
        snapshot = deepcopy(original)
        current = deepcopy(original)
        current["c4l2_s6_measure_config"]["FT1"]["measure"] = "Encierro completo"
        changed = changed_progress_fields(snapshot, current)
        self.assertEqual(set(changed), {"c4l2_s6_measure_config"})
        merged = {**snapshot, **changed}
        self.assertEqual(merged["c4l2_s10_maps"], snapshot["c4l2_s10_maps"])
        self.assertEqual(merged["done_3"], True)

    def test_in_place_edit_is_detected_against_persisted_snapshot(self):
        state = {"c4l2_s6_measure_config": {"FT1": {"treated_units": 1}}}
        snapshot = deepcopy(state)
        state["c4l2_s6_measure_config"]["FT1"]["treated_units"] = 2
        self.assertEqual(changed_progress_fields(snapshot, state), state)

    def test_empty_change_avoids_database_call(self):
        self.assertEqual(changed_progress_fields({"done_3": True}, {"done_3": True}), {})

    def test_first_save_creates_progress_after_patch_reports_missing_row(self):
        client = Mock()
        client.rpc.return_value.execute.return_value = SimpleNamespace(data=False)
        row = {"class_id": "clase-08-construccion-lab-2", "user_key": "audit"}
        changes = {"c4l2_s6_tl_calculator": {"thickness": 18.5}}

        save_progress_changes(client, row, changes)

        client.table.assert_called_once_with("user_progress")
        client.table.return_value.insert.assert_called_once_with(
            {**row, "state_json": changes}, returning="minimal"
        )

    def test_concurrent_first_save_retries_patch_without_replacing_row(self):
        client = Mock()
        client.rpc.return_value.execute.side_effect = [
            SimpleNamespace(data=False), SimpleNamespace(data=True)
        ]
        conflict = RuntimeError("duplicate key")
        conflict.code = "23505"
        client.table.return_value.insert.return_value.execute.side_effect = conflict

        save_progress_changes(client, {"class_id": "lab", "user_key": "audit"}, {"done_6": False})

        self.assertEqual(client.rpc.call_count, 2)
        self.assertEqual(client.rpc.call_args_list[0], client.rpc.call_args_list[1])


if __name__ == "__main__":
    unittest.main()
