"""Regression tests: atomic Stage 6 JSON import must preserve previous work."""
import json
import unittest
from copy import deepcopy

from labs.c4l2_stage6_batch_import import recover_front_backups
from labs.curso4_lab2_control_scope import front_sources
from labs.curso4_lab2_acoustics import source_fingerprint


class FrontRestoreTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "done_3": True, "done_4": True, "done_5": True,
            "c4l2_s3_acoustic_sources": [],
            "c4l2_s4_scenarios": [],
            "c4l2_s5_detailed_results": [{"LAeq [dB(A)]": 61.2}],
        }
        self.files = []
        for index in range(1, 7):
            front = f"Escenario {index} : Frente {index}"
            machine = {"Etapa": front, "Máquina / equipo proyecto": f"Equipo {index}",
                       "Cantidad": 1, "Lw_bandas": [90]*8}
            self.state["c4l2_s3_acoustic_sources"].append(machine)
            self.state["c4l2_s4_scenarios"].append({
                "Etapa": front, "Frente": f"FT{index} · {front}",
                "Máquinas simultáneas": [f"Equipo {index}"]
            })
        for index in range(1, 7):
            front = f"Escenario {index} : Frente {index}"
            entry = front_sources(self.state, front)[0]
            doc = {
                "schema_version": 2, "stage": 6, "front": front,
                "strategy": "Seleccionar medida", "machine_count": 1,
                "configuration": {
                    "scope_schema_version": 2, "medida": "Seleccionar medida",
                    "machines": {
                        entry["id"]: {
                            "measure": "Silenciador",
                            "source_signature": source_fingerprint([entry["source"]]),
                            "treated_units": 1,
                        }
                    }
                }
            }
            self.files.append((f"FT{index}.json", json.dumps(doc).encode("utf-8")))

    def test_imports_six_fronts_without_touching_prior_stages(self):
        before=deepcopy(self.state)
        imported, report=recover_front_backups(self.state, self.files)
        self.assertEqual(len(imported),6)
        self.assertEqual(sum(count for _,count,_ in report),6)
        self.assertEqual(self.state,before)
        self.assertTrue(all(v["medida"] == "Silenciador" for v in imported.values()))

    def test_duplicate_front_rejected_atomically(self):
        with self.assertRaisesRegex(ValueError,"dos archivos"):
            recover_front_backups(self.state,self.files[:1]+self.files[:1])

    def test_unknown_machine_rejected(self):
        name,payload=self.files[0]
        doc=json.loads(payload)
        doc["configuration"]["machines"]={"unknown_machine":{"measure":"Silenciador"}}
        with self.assertRaisesRegex(ValueError,"vincular"):
            recover_front_backups(self.state,[(name,json.dumps(doc).encode())])

    def test_wrong_stage_and_front_rejected(self):
        name,payload=self.files[0]
        doc=json.loads(payload)
        doc["stage"]=5
        with self.assertRaisesRegex(ValueError,"Etapa 6"):
            recover_front_backups(self.state,[(name,json.dumps(doc).encode())])
        doc["stage"]=6
        doc["front"]="frente ajeno"
        with self.assertRaisesRegex(ValueError,"no existe"):
            recover_front_backups(self.state,[(name,json.dumps(doc).encode())])


if __name__=="__main__":
    unittest.main()
