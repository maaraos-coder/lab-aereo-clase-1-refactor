"""Non-destructive regression tests for C4L2 partial Supabase writes."""
import unittest
from copy import deepcopy
from labs.c4l2_progress_patch import changed_progress_fields


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


if __name__ == "__main__":
    unittest.main()
