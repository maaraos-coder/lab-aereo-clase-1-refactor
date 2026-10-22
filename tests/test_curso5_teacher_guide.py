"""La pauta se muestra únicamente al docente fuera de proyección."""
import unittest
from labs import curso5_laboratorio_1 as lab
from test_curso5_design_flow import Surface


class TeacherGuideTests(unittest.TestCase):
    def setUp(self):
        self.original = getattr(lab, 'st', None)

    def tearDown(self):
        if self.original is None:
            lab.__dict__.pop('st', None)
        else:
            lab.st = self.original

    def test_teacher_has_review_guidance_for_every_stage(self):
        ui = Surface()
        ui.session_state = {'role': 'Docente'}
        lab.st = ui
        for stage in range(11):
            ui.messages.clear()
            lab._teacher_guide(stage)
            self.assertTrue(any('Criterio de revisión:' in text for _, text in ui.messages))
            self.assertTrue(any('Errores que requieren corrección:' in text for _, text in ui.messages))

    def test_no_guidance_leaks_to_student_projection_or_unknown_role(self):
        for state in ({'role': 'Alumno'}, {'role': 'Proyección'},
                      {'role': 'Docente', 'projection_mode': True}, {}):
            with self.subTest(state=state):
                ui = Surface()
                ui.session_state = state
                lab.st = ui
                for stage in range(11):
                    lab._teacher_guide(stage)
                self.assertEqual([], ui.messages)
