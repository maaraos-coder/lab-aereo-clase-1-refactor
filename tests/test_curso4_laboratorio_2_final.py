import unittest

from labs import curso4_laboratorio_2_stage7 as stage7
from labs import curso4_laboratorio_2_stage8 as stage8
from labs import curso4_laboratorio_2_stage9 as stage9
from labs import curso4_laboratorio_2_stage10 as stage10
from labs.curso4_lab2_reference_solution import build_reference_report


class Curso4Laboratorio2FinalTests(unittest.TestCase):
    def test_comparison_calculates_reduction_and_reference_result(self):
        original=[{"Frente":"Escenario 1","Receptor":"R1","LAeq [dB(A)]":72.0}]
        controlled=[{"Frente":"Escenario 1","Receptor":"R1","LAeq controlado [dB(A)]":64.0}]
        result=stage7._comparison_rows(original,controlled,65.0)[0]
        self.assertEqual(result["Reducción [dB]"],8.0)
        self.assertEqual(result["Margen [dB]"],1.0)
        self.assertEqual(result["Resultado"],"Bajo el límite")

    def test_insufficient_control_is_identified(self):
        original=[{"Frente":"Escenario 2","Receptor":"R2","LAeq [dB(A)]":72.0}]
        controlled=[{"Frente":"Escenario 2","Receptor":"R2","LAeq controlado [dB(A)]":68.0}]
        result=stage7._comparison_rows(original,controlled,65.0)[0]
        self.assertEqual(result["Reducción [dB]"],4.0)
        self.assertEqual(result["Resultado"],"Mejora, pero sobre el límite")

    def test_optimization_defaults_follow_controlled_result(self):
        design=[{
            "Frente / condición":"Escenario 1 · Movimiento de tierra",
            "Medida seleccionada":"Barrera acústica",
            "Proyecto controlado":"E1 controlado",
        }]
        comparison=[{
            "Frente":"Escenario 1","Receptor":"R1",
            "Controlado [dB(A)]":64.0,"Reducción [dB]":8.0,
        }]
        result=stage8._optimization_rows(design,comparison,[],65.0)[0]
        self.assertEqual(result["Decisión final"],"Mantener solución")
        self.assertEqual(result["Proyecto definitivo"],"E1 controlado")

    def test_score_distribution_and_chilean_grade(self):
        self.assertEqual(len(stage9.QUESTIONS),10)
        self.assertEqual(sum(item[2] for item in stage10.RUBRIC),70)
        self.assertEqual(stage9._grade(18),4.0)
        self.assertEqual(stage9._grade(30),7.0)
        self.assertEqual(stage10._grade(60),4.0)
        self.assertEqual(stage10._grade(100),7.0)

    def test_integrated_report_recovers_real_stage_keys_and_maps(self):
        saved={
            "c4l2_s1_chronology_table":[{"Actividad":"Excavación"}],
            "c4l2_s2_relevance_table":[{"Receptor":"R1"}],
            "c4l2_s3_bs_assignments":[{"Equipo":"Excavadora"}],
            "c4l2_s4_scenarios":[{"Frente":"FT1"}],
            "c4l2_s4_front_configs":{"FT1":{"grid":5}},
            "c4l2_s6_tl_calculator":{"material":"OSB"},
            "c4l2_s7_comparability":{"sources":True},
            "c4l2_s8_checks":{"verified":True},
            "c4l2_s10_maps":{"original":[{"name":"mapa.webp","data":"AA=="}]},
        }
        report=stage10._submission_payload(saved)
        self.assertEqual(report["stage_4"]["scenarios"][0]["Frente"],"FT1")
        self.assertEqual(report["stage_6"]["tl_calculator"]["material"],"OSB")
        self.assertEqual(report["maps"]["original"][0]["name"],"mapa.webp")

    def test_teacher_guide_matches_practical_rubric(self):
        expected={stage:points for stage,_,points in stage10.RUBRIC}
        actual={
            stage:sum(points for _,points in criteria)
            for stage,criteria in stage10.TEACHER_GUIDE.items()
        }
        self.assertEqual(actual,expected)

    def test_teacher_reference_contains_complete_development(self):
        report=build_reference_report()
        for stage in range(1,9):
            self.assertTrue(report.get(f"stage_{stage}"))
        comparisons=report["stage_7"]["comparison"]
        self.assertTrue(comparisons)
        self.assertLessEqual(max(row["Controlado [dB(A)]"] for row in comparisons),65)
        self.assertEqual(len(report["stage_6"]["design"]),6)


if __name__=="__main__":
    unittest.main()

