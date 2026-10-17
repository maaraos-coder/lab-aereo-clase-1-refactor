"""Regresiones de selección, resumen y guardado sin servicios externos.

Se carga el catálogo literal del Lab 1 sin importar sus componentes Streamlit.
El renderer de Etapa 3 se ejecuta completo con una UI de prueba.
"""
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_stage3():
    tree = ast.parse((ROOT / 'labs/curso4_laboratorio_1.py').read_text(encoding='utf-8'))
    catalog = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'BS_PLANT' for t in node.targets))
    namespace = {'BS_PLANT': ast.literal_eval(catalog)}
    path = ROOT / 'labs/curso4_laboratorio_2_stage3.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module == 'labs.curso4_laboratorio_1')]
    exec(compile(tree, str(path), 'exec'), namespace)
    return SimpleNamespace(**namespace)


stage3 = load_stage3()


class UI:
    def __init__(self, role, button=None):
        self.session_state = {'role': role}
        self.clicked = button
        self.frames = []
        self.messages = []
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def markdown(self, *args, **kwargs): pass
    def latex(self, *args, **kwargs): pass
    def caption(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def columns(self, n, **kwargs): return [self] * n
    def expander(self, *args, **kwargs): return self
    def selectbox(self, label, options, **kwargs): return options[0]
    def dataframe(self, df, **kwargs): self.frames.append(df.copy())
    def button(self, label, **kwargs): return kwargs.get('key') == self.clicked
    def warning(self, message): self.messages.append(('warning', message))
    def info(self, message): self.messages.append(('info', message))
    def error(self, message): self.messages.append(('error', message))
    def success(self, message): self.messages.append(('success', message))


def render(role, refs, saved=None, button=None, fail=False):
    saved = deepcopy(saved) if saved is not None else {
        'c4l2_s1_machinery_table': [
            {'Máquina / equipo': 'Minicargador', 'Cantidad': 1, 'Etapa asociada': 'E1'},
            {'Máquina / equipo': 'Minicargador', 'Cantidad': 2, 'Etapa asociada': 'E2'},
        ],
        'student_answer': {'calculation': 'respuesta propia'},
    }
    ui = UI(role, button)
    writes = []
    grid_inputs = []
    def grid(df, **kwargs):
        grid_inputs.append(df.copy())
        if refs is not None:
            df['Referencia BS'] = [refs[i % len(refs)] for i in range(len(df))]
        return df
    def save(lab, candidate, stage):
        if fail: raise RuntimeError('offline')
        writes.append(deepcopy(candidate))
    stage3.render({'id': 'lab'}, saved, {
        'st': ui, 'pd': pd, 'header': lambda *a, **k: None,
        '_professional_grid': grid, '_save': save,
    })
    summary = next(df for df in ui.frames if 'Máquina proyecto' in df)
    return saved, ui, writes, summary, grid_inputs


class Stage3Tests(unittest.TestCase):
    def test_every_catalog_entry_has_consistent_summary_and_source(self):
        for ref, item in stage3.SOURCE_CATALOG.items():
            with self.subTest(ref=ref):
                assignments = [{'Máquina / equipo proyecto': 'Equipo', 'Etapa': 'E1', 'Referencia BS': ref}]
                row = stage3._summary_rows(assignments)[0]
                source = stage3._acoustic_sources(assignments)[0]
                self.assertEqual(row['Referencia BS'], ref)
                self.assertEqual(row['Lp 10 m [dB(A)]'], item['laeq10'])
                self.assertEqual(row['LWA [dB(A)]'], source['LWA_global'])
                self.assertEqual(source['Lp_bandas'], item['bands'])
                self.assertEqual(source['Lw_bandas'], [v + 28 for v in item['bands']])
                self.assertEqual(source['band_labels'], ['63 Hz','125 Hz','250 Hz','500 Hz','1 kHz','2 kHz','4 kHz','8 kHz'])
                self.assertEqual(source['a_corr'], [-26.2,-16.1,-8.6,-3.2,0.0,1.2,1.0,-1.1])

    def test_unknown_and_unselected_stay_pending_without_fabricated_sources(self):
        assignments = [{'Referencia BS': ref} for ref in (None, '', 'Seleccionar referencia BS', 'desconocida')]
        self.assertEqual(stage3._acoustic_sources(assignments), [])
        for row in stage3._summary_rows(assignments):
            self.assertEqual(row['Referencia BS'], 'Pendiente')
            self.assertIsNone(row['Lp 10 m [dB(A)]'])
            self.assertIsNone(row['LWA [dB(A)]'])

    def test_full_render_draft_and_reload_in_all_views(self):
        refs = ['Adenda 2 · Minicargador · C.4 ítem 14', 'Excavadora hidráulica']
        for role in ('Alumno', 'Proyección', 'Docente'):
            with self.subTest(role=role):
                saved, ui, writes, summary, _ = render(role, refs, button='c4l2_s3_save_draft')
                self.assertTrue(summary['Lp 10 m [dB(A)]'].notna().all())
                self.assertNotIn('Pendiente', summary['Referencia BS'].tolist())
                self.assertTrue(writes)
                self.assertFalse(saved.get('done_3'))
                self.assertEqual(len(saved['c4l2_s3_acoustic_sources']), len(summary))
                self.assertEqual(saved['student_answer'], {'calculation': 'respuesta propia'})
                _, _, _, reloaded, grids = render(role, None, saved=saved)
                self.assertEqual(grids[0]['Referencia BS'].tolist(), summary['Referencia BS'].tolist())
                pd.testing.assert_frame_equal(summary, reloaded)

    def test_validation_blocks_pending_and_saves_valid_selection(self):
        for role in ('Alumno', 'Proyección', 'Docente'):
            saved, ui, _, _, _ = render(role, ['Seleccionar referencia BS'], button='c4l2_s3_save')
            self.assertFalse(saved.get('done_3', False))
            self.assertTrue(any(kind == 'warning' and 'Falta seleccionar' in message for kind, message in ui.messages))
            saved, _, writes, _, _ = render(role, ['Excavadora hidráulica'], button='c4l2_s3_save')
            self.assertTrue(saved['done_3'])
            self.assertTrue(writes[-1]['done_3'])

    def test_changed_draft_removes_stale_source_and_completion(self):
        saved, _, _, _, _ = render('Alumno', ['Excavadora hidráulica'], button='c4l2_s3_save')
        changed, _, _, summary, _ = render('Alumno', ['Seleccionar referencia BS'], saved, 'c4l2_s3_save_draft')
        self.assertEqual(changed['c4l2_s3_acoustic_sources'], [])
        self.assertFalse(changed['done_3'])
        self.assertTrue(summary['Lp 10 m [dB(A)]'].isna().all())
        self.assertEqual(saved['student_answer'], changed['student_answer'])

    def test_failed_writes_do_not_acknowledge_completion_or_replace_saved_values(self):
        original, _, _, _, _ = render('Alumno', ['Excavadora hidráulica'], button='c4l2_s3_save')
        for role in ('Alumno', 'Proyección', 'Docente'):
            for button in ('c4l2_s3_save', 'c4l2_s3_save_draft'):
                with self.subTest(role=role, button=button):
                    saved, ui, writes, _, _ = render(role, ['Retroexcavadora'], original, button, fail=True)
                    self.assertEqual(saved, original)
                    self.assertEqual(writes, [])
                    self.assertTrue(any(kind == 'error' for kind, _ in ui.messages))
                    self.assertFalse(any(kind == 'success' for kind, _ in ui.messages))


class PersonalPersistenceTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'views/cursos.py'
        node = next(node for node in ast.parse(path.read_text(encoding='utf-8')).body
                    if isinstance(node, ast.FunctionDef) and node.name == '_save_future_state_impl')
        self.ui = UI('Alumno')
        self.ui.session_state['user_key'] = 'student'
        self.client = SimpleNamespace(table=lambda name: self.client,
                                      upsert=lambda *a, **k: self.client,
                                      execute=lambda: None)
        namespace = {'st': self.ui, '_supabase': lambda: self.client,
                     'COURSE_ID': 'course', '_now': lambda: 'now'}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
        self.save = namespace['_save_future_state_impl']
        self.class_id = 'clase-08-construccion-lab-2'
        self.key = f'future_saved_{self.class_id}'
        self.ui.session_state[self.key] = {'previous': True}

    def test_success_updates_cache_only_after_write_and_copies_state(self):
        def execute():
            self.assertEqual(self.ui.session_state[self.key], {'previous': True})
        self.client.execute = execute
        state = {'new': [1]}
        self.save(self.class_id, state)
        state['new'].append(2)
        self.assertEqual(self.ui.session_state[self.key], {'new': [1]})

    def test_storage_failure_keeps_previous_checkpoint(self):
        def execute(): raise RuntimeError('offline')
        self.client.execute = execute
        with self.assertRaises(RuntimeError): self.save(self.class_id, {'new': True})
        self.assertEqual(self.ui.session_state[self.key], {'previous': True})

    def test_missing_connection_or_user_does_not_silently_succeed(self):
        self.client = None
        with self.assertRaises(RuntimeError): self.save(self.class_id, {'new': True})
        self.ui.session_state.pop('user_key')
        with self.assertRaises(RuntimeError): self.save(self.class_id, {'new': True})
        self.assertEqual(self.ui.session_state[self.key], {'previous': True})


if __name__ == '__main__':
    unittest.main()
