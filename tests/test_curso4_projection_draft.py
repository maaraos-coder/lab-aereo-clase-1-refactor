import unittest
from copy import deepcopy
from types import SimpleNamespace
from labs.curso4_lab2_projection import CLASS_ID, cache_key, load_draft, save_draft
from labs.curso4_lab2_drafts import render_draft_save


class Client:
    def __init__(self):
        self.row={"stage":1,"draft_state":{}}
        self.fail=False
        self.tables=[]
    def table(self,name):
        self.tables.append(name)
        self.values=None
        return self
    def select(self,*args): return self
    def eq(self,*args): return self
    def limit(self,*args): return self
    def update(self,values):
        self.values=values
        return self
    def execute(self):
        if self.fail: raise RuntimeError('offline')
        if self.values: self.row.update(deepcopy(self.values))
        return SimpleNamespace(data=[deepcopy(self.row)])


class UI:
    def __init__(self,role='Proyección'):
        self.session_state={'role':role}
        self.messages=[]
        self.buttons=[]
    def caption(self,s): self.messages.append(s)
    def warning(self,s): self.messages.append(s)
    def error(self,s): self.messages.append(s)
    def success(self,s): self.messages.append(s)
    def markdown(self,*args,**kwargs): pass
    def button(self,s,**kwargs):
        self.buttons.append(s)
        return False


class ProjectionDraftTests(unittest.TestCase):
    def test_recovers_after_session_restart_without_student_progress(self):
        client=Client();ui=UI()
        state={'c4l2_s1_vertices_table':[{'Vértice':'V1','Latitud':-33.6}]}
        save_draft(ui,client,'course',CLASS_ID,state)
        recovered=load_draft(UI(),client,'course',CLASS_ID)
        self.assertEqual(recovered,state)
        self.assertEqual(client.row['stage'],1)
        self.assertEqual(set(client.tables),{'projection_state'})

    def test_failed_save_does_not_acknowledge_or_replace_checkpoint(self):
        client=Client();ui=UI()
        save_draft(ui,client,'course',CLASS_ID,{'value':1})
        client.fail=True
        with self.assertRaises(RuntimeError): save_draft(ui,client,'course',CLASS_ID,{'value':2})
        self.assertEqual(ui.session_state[cache_key(CLASS_ID)+'_persisted'],{'value':1})

    def test_autosaves_changed_projection_values_only_and_keeps_manual_button(self):
        ui=UI();client=Client();saved=load_draft(ui,client,'course',CLASS_ID);calls=[]
        def save(lab,state,stage):
            calls.append(stage)
            save_draft(ui,client,'course',lab['id'],state)
        for _ in range(2): render_draft_save(ui,saved,{'_save':save},{'id':CLASS_ID},1,{'table':[{'v':1}]},'draft')
        self.assertEqual(calls,[1])
        self.assertTrue(ui.buttons)
        self.assertNotIn('done_1',client.row['draft_state'])

    def test_teacher_button_visible_without_automatic_write(self):
        ui=UI('Docente')
        render_draft_save(ui,{}, {'_save':lambda *a:self.fail('unexpected write')},{'id':CLASS_ID},1,{'table':[]},'draft')
        self.assertEqual(len(ui.buttons),1)

    def test_failed_load_not_cached_as_empty_draft(self):
        ui=UI();client=Client();client.fail=True
        with self.assertRaises(RuntimeError):load_draft(ui,client,'course',CLASS_ID)
        self.assertNotIn(cache_key(CLASS_ID),ui.session_state)
