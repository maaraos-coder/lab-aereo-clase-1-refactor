"""Regresiones del control por equipo, unidades y camino de propagación."""
from copy import deepcopy
import math
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

import pandas as pd

from labs import curso4_control_models as model
from labs import curso4_laboratorio_2_stage6 as stage6
from labs.curso4_lab2_acoustics import source_fingerprint
from labs.curso4_lab2_control_scope import (
    NO_CONTROL, front_sources, recombine_front, validate_scope, render_scope,
)

FRONT = 'Escenario 1 · Movimiento de tierra'


def saved_state():
    return {
        'c4l2_s3_acoustic_sources': [
            {'Máquina / equipo proyecto':name, 'Etapa':FRONT, 'Cantidad':1,
             'Lw_bandas':[level] * 8, 'LWA_global':level + 5}
            for name, level in [('Minicargador',100),('Excavadora',100),('Retroexcavadora',100)]
        ],
        'c4l2_s4_scenarios':[{'Etapa':FRONT,'Máquinas simultáneas':['Minicargador','Excavadora','Retroexcavadora']}],
        'c4l2_s5_detailed_results':[{'Frente':'Escenario 1','Receptor':'R1','LAeq [dB(A)]':70}],
        'done_5':True, 'student_answer':'respuesta propia',
    }


def applications(entries, reduction=10):
    output = {}
    for i, entry in enumerate(entries):
        source = entry['source']
        output[entry['id']] = {'measure':NO_CONTROL, 'source_signature':source_fingerprint([source])}
        if i == 0:
            treatment = model.default_treatment('direct')
            treatment['control_reduction_db'] = {str(f):reduction for f in model.OCTAVE_BANDS}
            output[entry['id']].update({'measure':'Reducción directa','treated_units':1,
                'treatment':treatment,'evidence':'Ficha técnica identificada por el alumno'})
    return output


class ScopeMathTests(unittest.TestCase):
    def test_one_machine_control_does_not_reduce_the_entire_front(self):
        entries = front_sources(saved_state(), FRONT)
        result = recombine_front(entries, applications(entries), strict=True)
        self.assertAlmostEqual(result['original'][0], 100 + 10 * math.log10(3))
        self.assertAlmostEqual(result['controlled'][0], 100 + 10 * math.log10(2.1))
        self.assertLess(result['original'][0] - result['controlled'][0], 2)
        self.assertEqual(result['machines'][1]['Lw_original'], result['machines'][1]['Lw_controlado'])

    def test_some_units_receive_control_and_rest_remain_original(self):
        saved = saved_state()
        saved['c4l2_s3_acoustic_sources'] = saved['c4l2_s3_acoustic_sources'][:1]
        saved['c4l2_s3_acoustic_sources'][0]['Cantidad'] = 3
        entries = front_sources(saved, FRONT)
        app = applications(entries)
        result = recombine_front(entries, app, strict=True)
        self.assertAlmostEqual(result['controlled'][0], 100 + 10 * math.log10(2.1))
        app[entries[0]['id']]['treated_units'] = 4
        with self.assertRaises(ValueError): recombine_front(entries, app, strict=True)

    def test_front_identity_and_original_simultaneity_are_respected(self):
        saved = saved_state()
        saved['c4l2_s3_acoustic_sources'].append({**saved['c4l2_s3_acoustic_sources'][0], 'Etapa':'Escenario 2 · Urbanización'})
        saved['c4l2_s4_scenarios'][0]['Máquinas simultáneas'] = ['Minicargador']
        self.assertEqual(len(front_sources(saved, 'FT1 · ' + FRONT)), 1)
        self.assertEqual(front_sources(saved, 'Escenario 2'), [])

    def test_missing_evidence_stale_source_and_unselected_equipment_block_finalization(self):
        entries = front_sources(saved_state(), FRONT)
        for change in ({'evidence':''}, {'source_signature':'old'}, {'measure':'Seleccionar aplicación'}):
            app = applications(entries)
            app[entries[0]['id']].update(change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError): recombine_front(entries, app, strict=True)
                result = recombine_front(entries, app)
                self.assertTrue(result['pending'])
                self.assertEqual(result['original'], result['controlled'])

    def test_barrier_does_not_change_emitted_power(self):
        saved = saved_state()
        entries = front_sources(saved, FRONT)
        app = applications(entries)
        for application in app.values(): application['measure'] = NO_CONTROL
        barrier = {'enabled':True,'protected_ids':[entries[0]['id']],'ubicacion':'Borde poniente',
            'receptor':'R1','calculo':{'illustrative':True},'altura_m':3,'longitud_m':20,
            'distancia_fr_m':20,'distancia_fb_m':5,'altura_fuente_m':1.5,'altura_receptor_m':1.5}
        cfg = {'scope_schema_version':2,'medida':'Barrera acústica','machines':app,'propagation':barrier}
        result = validate_scope(saved, FRONT, cfg)
        self.assertEqual(result['original'], result['controlled'])
        cfg['propagation']['protected_ids'] = ['unknown']
        with self.assertRaises(ValueError): validate_scope(saved, FRONT, cfg)

    def test_enclosure_uses_emitted_power_balance_and_not_receiver_delta(self):
        entries = front_sources(saved_state(), FRONT)
        app = applications(entries)
        cfg = model.default_treatment('enclosure')
        app[entries[0]['id']].update({'measure':'Encierro completo','treatment':cfg,
                                    'calculo':{'controlled_dba':-999,'original_dba':999}})
        result = recombine_front(entries, app, strict=True)
        reduction = model.enclosure_balance(cfg, 63)[1]
        self.assertAlmostEqual(result['controlled'][0], 10 * math.log10(2 * 10**10 + 10**((100-reduction)/10)))

    def test_silencer_requires_effective_reduction_of_modeled_machine(self):
        entries = front_sources(saved_state(), FRONT)
        app = applications(entries)
        app[entries[0]['id']].update({'measure':'Silenciador','treatment':model.default_treatment('silencer')})
        with self.assertRaises(ValueError): recombine_front(entries, app, strict=True)
        app[entries[0]['id']]['effective_machine_reduction'] = True
        self.assertFalse(recombine_front(entries, app, strict=True)['pending'])

    def test_legacy_front_treatment_is_not_implicitly_applied_to_all_machines(self):
        with self.assertRaises(ValueError): validate_scope(saved_state(), FRONT, {'medida':'Encierro completo','treatment':model.default_treatment()})


class UI:
    def __init__(self, role):
        self.session_state = {'role':role}
        self.messages = []
        self.machine = 0
        self.clicked = set()
        self.column_config = SimpleNamespace(TextColumn=lambda *a,**k:None,
            NumberColumn=lambda *a,**k:None,SelectboxColumn=lambda *a,**k:None)
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def markdown(self,*a,**k): pass
    def caption(self,*a,**k): pass
    def info(self,s): self.messages.append(('info',s))
    def warning(self,s): self.messages.append(('warning',s))
    def success(self,s): self.messages.append(('success',s))
    def error(self,s): self.messages.append(('error',s))
    def metric(self,*a,**k): pass
    def dataframe(self,*a,**k): pass
    def image(self,*a,**k): pass
    def write(self,*a,**k): pass
    def expander(self,*a,**k): return self
    def columns(self,n,**k): return [self] * (n if isinstance(n,int) else len(n))
    def selectbox(self,label,options,index=0,**k): return options[self.machine if label=='Máquina a configurar' else index]
    def multiselect(self,label,options,default=None,**k): return default or []
    def checkbox(self,label,value=False,key='',**k): return True if key.startswith('c4l2_s6_check_') else value
    def number_input(self,label,value,**k): return value
    def text_input(self,label,value='',**k): return value
    def text_area(self,label,value='',**k): return value
    def button(self,label,key='',**k): return key in self.clicked
    def link_button(self,*a,**k): pass
    def file_uploader(self,*a,**k): return []
    def data_editor(self,frame,**k): return frame


class ScopeUITests(unittest.TestCase):
    def workshop(self):
        calls = []
        def designer(st,pd,prefix,initial=None,**kwargs):
            calls.append(kwargs)
            return deepcopy(initial or model.default_treatment('direct')), {'bands':[], 'illustrative':True}
        return SimpleNamespace(render_designer=designer,render_examples=lambda *a:None,
            render_tl_calculator=lambda *a:({},{}),render_barrier_calculator=lambda *a:({},{})), calls

    def test_applied_designer_uses_actual_machine_spectrum_and_preserves_other_applications(self):
        saved = saved_state()
        entries = front_sources(saved, FRONT)
        config = {'scope_schema_version':2,'medida':'Reducción directa','machines':applications(entries)}
        previous = deepcopy(config)
        workshop, calls = self.workshop()
        ui = UI('Alumno')
        result = render_scope(ui,pd,saved,FRONT,'Reducción directa',config,'test',workshop,{}, {})
        self.assertEqual(calls[-1]['source_lw'], {str(f):100 for f in model.OCTAVE_BANDS})
        self.assertEqual(result['machines'][entries[1]['id']],previous['machines'][entries[1]['id']])
        self.assertEqual(config,previous)
        ui.machine = 1
        second = render_scope(ui,pd,saved,FRONT,'Reducción directa',result,'test',workshop,{}, {})
        self.assertEqual(second['machines'][entries[0]['id']],result['machines'][entries[0]['id']])

    def test_full_stage6_saves_and_recovers_explicit_scope_in_all_views(self):
        for role in ('Alumno','Proyección','Docente'):
            with self.subTest(role=role):
                saved = saved_state()
                entries = front_sources(saved, FRONT)
                saved['c4l2_s6_control_design'] = [{'Frente / condición':FRONT,'Tipo de trabajo':'Nivel de suelo',
                    'Receptor crítico':'R1','LAeq original [dB(A)]':70,'Medida seleccionada':'Reducción directa',
                    'Justificación':'Medida respaldada por ficha técnica','Proyecto controlado':'Proyecto propio controlado'}]
                saved['c4l2_s6_measure_config'] = {FRONT:{'medida':'Reducción directa','scope_schema_version':2,
                    'machines':applications(entries)}}
                ui = UI(role)
                ui.clicked = {'c4l2_s6_save'}
                workshop, calls = self.workshop()
                writes = []
                def save(lab,candidate,stage): writes.append(deepcopy(candidate))
                with patch.dict(sys.modules,{'labs.curso4_control_workshop':workshop}):
                    stage6.render({'id':'lab'},saved,{'st':ui,'pd':pd,'header':lambda *a,**k:None,'_save':save,'NOISEMAP_URL':'https://example.com'})
                self.assertTrue(saved['done_6'])
                self.assertEqual(saved['student_answer'],'respuesta propia')
                self.assertTrue(writes[-1]['done_6'])
                result = saved['c4l2_s6_measure_config'][FRONT]['controlled_front']
                self.assertAlmostEqual(result['controlled'][0],100+10*math.log10(2.1))
                self.assertEqual(len(saved['c4l2_s6_measure_config'][FRONT]['machines']),3)

    def test_legacy_configuration_is_preserved_without_target_assignment(self):
        saved = saved_state()
        legacy = {'medida':'Encierro completo','treatment':model.default_treatment('enclosure'),
                  'calculo':{'original_dba':80,'controlled_dba':50}}
        workshop, calls = self.workshop()
        result = render_scope(UI('Alumno'),pd,saved,FRONT,'Encierro completo',legacy,'legacy',workshop,{}, {})
        self.assertEqual(result['legacy_front_configuration'],legacy)
        self.assertTrue(result['controlled_front']['pending'])
        self.assertEqual(result['controlled_front']['original'],result['controlled_front']['controlled'])
        with self.assertRaises(ValueError): validate_scope(saved,FRONT,result)

    def test_failed_final_save_does_not_acknowledge_completion(self):
        saved = saved_state()
        entries = front_sources(saved, FRONT)
        saved['c4l2_s6_control_design'] = [{'Frente / condición':FRONT,'Tipo de trabajo':'Suelo',
            'LAeq original [dB(A)]':70,'Medida seleccionada':'Reducción directa',
            'Justificación':'Ficha técnica','Proyecto controlado':'Controlado'}]
        saved['c4l2_s6_measure_config'] = {FRONT:{'medida':'Reducción directa','scope_schema_version':2,
            'machines':applications(entries)}}
        original = deepcopy(saved)
        ui = UI('Alumno')
        ui.clicked = {'c4l2_s6_save'}
        workshop, calls = self.workshop()
        def fail(*args): raise RuntimeError('offline')
        with patch.dict(sys.modules,{'labs.curso4_control_workshop':workshop}):
            stage6.render({'id':'lab'},saved,{'st':ui,'pd':pd,'header':lambda *a,**k:None,'_save':fail,'NOISEMAP_URL':'https://example.com'})
        self.assertEqual(saved,original)
        self.assertTrue(any(kind=='error' for kind,message in ui.messages))
        self.assertFalse(any(kind=='success' for kind,message in ui.messages))

    def test_student_strategy_recovers_actual_front_names(self):
        saved = saved_state()
        saved['c4l2_s3_acoustic_sources'][0]['Etapa'] = 'Frente propio del alumno'
        names = [row['Frente / condición'] for row in stage6._student_design_rows(saved)]
        self.assertIn('Frente propio del alumno',names)
        self.assertNotIn('Escenario 2 · Terminaciones',names)


if __name__ == '__main__': unittest.main()
