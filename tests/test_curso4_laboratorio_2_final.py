import unittest

from labs import curso4_laboratorio_2_stage7 as stage7
from labs import curso4_laboratorio_2_stage8 as stage8
from labs import curso4_laboratorio_2_stage9 as stage9
from labs import curso4_laboratorio_2_stage10 as stage10


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


if __name__=="__main__":
    unittest.main()

