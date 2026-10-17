import ast
import base64
from copy import deepcopy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import zipfile

import pandas as pd

from views.curso4_lab2_review import (
    CATALOG, CLASS_ID, final_result, payload_of, report_bundle,
    render_review, review_note, persist_review,
)


def submission(user,points=24):
    payload={'report_meta':{'author':user},'stage_9':{'score':points},
        'stage_8':{'conclusion':'Conclusión de '+user},
        'maps':{group:[{'name':group+'.png','mime':'image/png','caption':user+' '+group,
                        'data':base64.b64encode((user+group).encode()).decode()}]
                for group in ('original','control','comparison')}}
    return {'id':user,'class_id':CLASS_ID,'question_key':'c4l2_integrated_project',
            'stage':10,'user_key':user,'users':{'display_name':user},'answer':payload,
            'teacher_score':None,'auto_score':0,'status':'submitted'}


class Query:
    def __init__(self,client,table):
        self.client=client; self.table_name=table; self.filters={}; self.updates=None
    def select(self,*a): return self
    def eq(self,key,value): self.filters[key]=value; return self
    def limit(self,*a): return self
    def order(self,*a,**k): return self
    def update(self,values): self.updates=deepcopy(values); return self
    def execute(self):
        self.client.queries.append((self.table_name,deepcopy(self.filters),self.updates))
        if self.client.fail: raise RuntimeError('offline')
        rows=[r for r in self.client.rows if all(r.get(k)==v for k,v in self.filters.items())]
        if self.updates is not None:
            for row in rows: row.update(deepcopy(self.updates))
        return SimpleNamespace(data=deepcopy(rows))


class Client:
    def __init__(self,rows): self.rows=deepcopy(rows); self.queries=[]; self.fail=False
    def table(self,name): return Query(self,name)


class UI:
    def __init__(self,role='Docente',student=0):
        self.session_state={'role':role}; self.student=student
        self.images=[]; self.messages=[]; self.downloads=[]; self.save=False
    def __enter__(self): return self
    def __exit__(self,*a): pass
    def columns(self,n,**k): return [self]*n
    def tabs(self,labels): return [self]*len(labels)
    def selectbox(self,label,options,**k):
        if label=='Alumno': return self.student
        if label=='Curso': return next(x for x in options if x.startswith('Curso 4'))
        if label=='Laboratorio': return next(x for x in options if x.startswith('Laboratorio 2'))
        if label=='Evaluación': return next(x for x in options if x.startswith('Etapa 10'))
        return list(options)[0]
    def expander(self,*a,**k): return self
    def markdown(self,text,**k): self.messages.append(str(text))
    def caption(self,text,**k): self.messages.append(str(text))
    def write(self,*a,**k): self.messages.extend(map(str,a))
    def json(self,*a,**k): pass
    def metric(self,*a,**k): pass
    def dataframe(self,*a,**k): pass
    def image(self,raw,**k): self.images.append(raw)
    def info(self,s): self.messages.append(s)
    def warning(self,s): self.messages.append(s)
    def success(self,s): self.messages.append('success:'+s)
    def error(self,s): self.messages.append('error:'+s)
    def number_input(self,label,min_value,max_value,**k): return max_value
    def text_area(self,*a,**k): return 'Retroalimentación docente'
    def button(self,*a,**k): return self.save
    def download_button(self,*a,**k): self.downloads.append((a,k))


class ReviewTests(unittest.TestCase):
    def test_catalog_separates_lab2_and_uses_actual_submission_keys(self):
        configs=list(CATALOG.values())
        self.assertEqual([c['question_key'] for c in configs],['c4l2_final_quiz','c4l2_integrated_project'])
        self.assertEqual([c['maximum'] for c in configs],[30,70])
        self.assertTrue(all(c['class_id']==CLASS_ID for c in configs))

    def test_final_grade_combines_30_and_70_and_stays_pending_without_review(self):
        row=submission('A',24)
        self.assertIsNone(final_result(row)['grade'])
        row['teacher_score']=36
        self.assertEqual(final_result(row)['total'],60)
        self.assertEqual(final_result(row)['grade'],4)
        row['teacher_score']=70
        self.assertEqual(final_result(row,{'teacher_score':30})['grade'],7)
        row['teacher_score']=float('nan')
        self.assertIsNone(final_result(row)['grade'])

    def test_bundle_contains_original_snapshot_and_all_uploaded_map_groups(self):
        payload=submission('A')['answer']
        with zipfile.ZipFile(io.BytesIO(report_bundle(payload))) as archive:
            self.assertEqual(json.loads(archive.read('informe_entregado.json')),payload)
            for i,group in enumerate(('original','control','comparison'),1):
                self.assertEqual(archive.read(f'imagenes/grupo_{i}/mapa_1.png'),('A'+group).encode())

    def test_individual_report_shows_selected_students_images_only(self):
        rows=[submission('A'),submission('B')]
        ui=UI(student=1)
        render_review(ui,pd,Client(rows),rows,list(CATALOG.values())[1],lambda:'now')
        self.assertEqual(ui.images,[b'Boriginal',b'Bcontrol',b'Bcomparison'])
        self.assertIn('Conclusión de B',ui.messages)
        self.assertNotIn('Conclusión de A',ui.messages)
        self.assertEqual(rows[1]['answer'],submission('B')['answer'])

    def test_saving_rubric_preserves_answer_and_targets_one_student(self):
        rows=[submission('A'),submission('B')]
        client=Client(rows); ui=UI(student=1); ui.save=True
        render_review(ui,pd,client,rows,list(CATALOG.values())[1],lambda:'now')
        self.assertEqual(client.rows[0],rows[0])
        self.assertEqual(client.rows[1]['answer'],rows[1]['answer'])
        self.assertEqual(client.rows[1]['teacher_score'],70)
        self.assertEqual(review_note(client.rows[1])['feedback'],'Retroalimentación docente')
        self.assertEqual(len(review_note(client.rows[1])['rubric_scores']),8)
        writes=[q for q in client.queries if q[2] is not None]
        self.assertEqual(writes[0][1]['user_key'],'B')
        self.assertNotIn('answer',writes[0][2])

    def test_role_guard_and_failed_or_unconfirmed_write(self):
        row=submission('A'); client=Client([row]); ui=UI('Alumno')
        render_review(ui,pd,client,[row],list(CATALOG.values())[1],lambda:'now')
        self.assertEqual(client.queries,[])
        with self.assertRaises(RuntimeError): persist_review(Client([]),row,{'teacher_score':70})
        client.fail=True
        ui=UI(); ui.save=True
        render_review(ui,pd,client,[row],list(CATALOG.values())[1],lambda:'now')
        self.assertFalse(any(m.startswith('success:') for m in ui.messages))
        self.assertTrue(any(m.startswith('error:') for m in ui.messages))

    def test_menu_integration_queries_lab2_and_renders_submitted_report(self):
        path=Path(__file__).resolve().parents[1]/'views/docente.py'
        node=next(n for n in ast.parse(path.read_text(encoding='utf-8')).body
                  if isinstance(n,ast.FunctionDef) and n.name=='_teacher_course_results_impl')
        row=submission('A'); client=Client([row]); ui=UI()
        namespace={'st':ui,'pd':pd,'json':json,'_supabase':lambda:client,'_now':lambda:'now',
                   'safe_filename':lambda s:'safe'}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
        namespace['_teacher_course_results_impl']()
        self.assertEqual(ui.images,[b'Aoriginal',b'Acontrol',b'Acomparison'])
        self.assertTrue(any(filters.get('class_id')==CLASS_ID and filters.get('question_key')=='c4l2_integrated_project'
                            for table,filters,updates in client.queries))


if __name__=='__main__': unittest.main()
