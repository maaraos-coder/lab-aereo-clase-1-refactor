"""Unit regressions for stage 6 durable backup and first machine restoration."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
from labs.c4l2_stage6_checkpoint import (
    QUESTION_KEY, save_stage6_checkpoint, load_stage6_checkpoint,
    reset_stage6_widgets, reconcile_machine_ids,
)


class FakeQuery:
    def __init__(self, database):
        self.database=database
        self.filters={}
        self.write=None
        self.fields=None

    def upsert(self,record,**options):
        self.write=deepcopy(record)
        return self

    def select(self,fields):
        self.fields=fields
        return self

    def eq(self,key,value):
        self.filters[key]=value
        return self

    def limit(self,n):
        return self

    def execute(self):
        if self.write is not None:
            key=(self.write["class_id"],self.write["user_key"],self.write["question_key"])
            self.database[key]=deepcopy(self.write)
            return SimpleNamespace(data=[])
        rows=[]
        for (class_id,user_key,question_key),record in self.database.items():
            if (self.filters.get("class_id")==class_id and
                self.filters.get("user_key")==user_key and
                self.filters.get("question_key")==question_key):
                rows.append({"answer":deepcopy(record["answer"])})
        return SimpleNamespace(data=rows)


class FakeClient:
    def __init__(self):
        self.store={}
        self.table_names=[]

    def table(self,name):
        self.table_names.append(name)
        if name!="responses":
            raise AssertionError("El respaldo no debe modificar progreso general")
        return FakeQuery(self.store)


class Stage6CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.client=FakeClient()
        self.state={
            "done_3":True,
            "c4l2_s3_acoustic_sources":[{"long_payload":"A"*1_500_000}],
            "c4l2_s5_detailed_results":[{"LAeq":52}],
            "c4l2_s6_measure_config":{
                "FT1":{"scope_schema_version":2,"medida":"Encierro completo",
                       "machines":{
                           "machine_1":{"measure":"Encierro completo","source_signature":"sig1"},
                           "machine_2":{"measure":"Sin tratamiento en la fuente","source_signature":"sig2"}
                       }}
            },
            "c4l2_s6_control_design":[{"Frente / condición":"FT1","Medida seleccionada":"Encierro completo"}],
            "c4l2_updated_6":"2026-11-12T11:00:00+00:00",
            "done_6":False,
        }

    def _write(self):
        return save_stage6_checkpoint(
            self.client,course_id="diplomado-acustica-edificacion",
            class_id="clase-08-construccion-lab-2",user_key="student-a",
            state=self.state
        )

    def test_verified_save_does_not_resend_other_stages(self):
        self.assertTrue(self._write())
        row=next(iter(self.client.store.values()))
        fields=row["answer"]["fields"]
        self.assertNotIn("c4l2_s3_acoustic_sources",fields)
        self.assertNotIn("c4l2_s5_detailed_results",fields)
        self.assertIn("machine_1",fields["c4l2_s6_measure_config"]["FT1"]["machines"])
        self.assertEqual(row["question_key"],QUESTION_KEY)
        self.assertEqual(row["max_score"],0)
        self.assertEqual(row["status"],"draft")
        self.assertEqual(self.client.table_names,["responses","responses"])

    def test_restore_first_machine_and_preserve_previous_stages(self):
        self._write()
        original=deepcopy(self.state)
        del original["c4l2_s6_measure_config"]
        original["c4l2_updated_6"]="2026-11-11T00:00:00+00:00"
        self.assertTrue(load_stage6_checkpoint(
            self.client,class_id="clase-08-construccion-lab-2",
            user_key="student-a",state=original))
        machines=original["c4l2_s6_measure_config"]["FT1"]["machines"]
        self.assertEqual(len(machines),2)
        self.assertEqual(machines["machine_1"]["measure"],"Encierro completo")
        self.assertTrue(original["done_3"])
        self.assertEqual(original["c4l2_s3_acoustic_sources"],self.state["c4l2_s3_acoustic_sources"])

    def test_newer_primary_state_not_overwritten(self):
        self._write()
        newer=deepcopy(self.state)
        newer["c4l2_updated_6"]="2026-11-13T00:00:00+00:00"
        newer["c4l2_s6_measure_config"]["FT1"]["machines"]["machine_1"]["measure"]="Reducción directa"
        self.assertFalse(load_stage6_checkpoint(
            self.client,class_id="clase-08-construccion-lab-2",
            user_key="student-a",state=newer))
        self.assertEqual(newer["c4l2_s6_measure_config"]["FT1"]["machines"]["machine_1"]["measure"],"Reducción directa")

    def test_reset_widgets_removes_stale_machine_selection_and_controls(self):
        prefix="c4l2_s6_scope_demo"
        session={
            prefix+"_machine":"machine_1",
            prefix+"_machine_1_measure":"Seleccionar aplicación",
            prefix+"_machine_1_evidence":"stale text",
            prefix+"_work":{"machines":{"machine_1":{"measure":"Encierro completo"}}},
            prefix+"_backup_upload":"FILE",
            prefix+"_restore":False,
            "unrelated":"KEEP",
        }
        removed=reset_stage6_widgets(session,prefix)
        self.assertEqual(len(removed),3)
        self.assertIn(prefix+"_work",session)
        self.assertIn(prefix+"_backup_upload",session)
        self.assertNotIn(prefix+"_machine_1_measure",session)
        self.assertEqual(session["unrelated"],"KEEP")

    def test_machine_id_reordered_is_recovered_by_source_signature(self):
        entries=[
            {"id":"new_1","source":{"name":"A"}},
            {"id":"new_2","source":{"name":"B"}},
        ]
        apps={
            "legacy_first":{"measure":"Encierro completo","source_signature":"A"},
            "legacy_second":{"measure":"Reducción directa","source_signature":"B"},
        }
        mapped,unresolved=reconcile_machine_ids(
            apps,entries,lambda rows:rows[0]["name"]
        )
        self.assertEqual(unresolved,[])
        self.assertEqual(mapped["new_1"]["measure"],"Encierro completo")
        self.assertEqual(mapped["new_2"]["measure"],"Reducción directa")

    def test_ambiguous_remapping_never_assigns_treatment_arbitrarily(self):
        entries=[
            {"id":"new_1","source":{"name":"A"}},
            {"id":"new_2","source":{"name":"A"}},
        ]
        apps={"legacy_first":{"measure":"Encierro completo","source_signature":"A"}}
        mapped,unresolved=reconcile_machine_ids(
            apps,entries,lambda rows:rows[0]["name"]
        )
        self.assertFalse(mapped)
        self.assertEqual(unresolved,["legacy_first"])


if __name__=="__main__":
    unittest.main()
