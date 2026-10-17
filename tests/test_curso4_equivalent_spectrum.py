"""Cálculo espectral y recorrido del alumno sin conexión ni componentes web."""
import ast
import math
from copy import deepcopy
from pathlib import Path
import unittest

import pandas as pd

from labs.curso4_lab2_acoustics import (
    BAND_LABELS, A_CORRECTIONS, LEGACY_LABELS, equivalent_spectrum,
    weighted_power, recover_answers, check_answers, parse_level, source_fingerprint,
)

ROOT = Path(__file__).resolve().parents[1]
STAGE = 'Escenario 1'
ANSWERS = [108, 109, 98, 99, 97, 95, 92, 83]
SPECTRA = [[96,95,91,90,90,89,82,75], [102,94,92,92,91,88,87,78], [107,109,96,97,94,93,89,80]]


def sources():
    return [{'Máquina / equipo proyecto': name, 'Cantidad': 1, 'Etapa': STAGE,
             'Referencia BS': name, 'Lw_bandas': bands, 'LWA_global': 100}
            for name, bands in zip(('Minicargador', 'Retroexcavadora', 'Excavadora'), SPECTRA)]


def load_renderer(stage):
    path = ROOT / f'labs/curso4_laboratorio_2_stage{stage}.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module == 'labs.curso4_laboratorio_1')]
    namespace = {'__file__': str(path), 'BS_PLANT': {}}
    exec(compile(tree, str(path), 'exec'), namespace)
    namespace['_teacher_pauta'] = lambda *a: None
    namespace['_teacher_solution_panel'] = lambda *a: None
    return namespace['render']


class UI:
    def __init__(self, role='Alumno'):
        self.session_state = {'role': role}
        self.inputs = dict(zip(BAND_LABELS, map(str, ANSWERS)))
        self.clicked = set()
        self.messages = []
        self.metrics = []
        self.frames = []
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def columns(self, n, **k): return [self] * (n if isinstance(n, int) else len(n))
    def markdown(self, *a, **k): pass
    def latex(self, *a, **k): pass
    def caption(self, *a, **k): pass
    def write(self, *a, **k): pass
    def image(self, *a, **k): pass
    def link_button(self, *a, **k): pass
    def file_uploader(self, *a, **k): return []
    def selectbox(self, label, options, index=0, **k): return options[index]
    def segmented_control(self, label, options, default=None, **k): return default
    def number_input(self, label, value, **k): return value
    def checkbox(self, *a, **k): return True
    def text_input(self, label, value='', **k):
        value = self.inputs.get(label, value)
        if label.startswith('Ubicación / sector'): value = 'Sector poniente'
        self.session_state[k['key']] = value
        return value
    def text_area(self, label, value='', **k): return value
    def button(self, label, **k): return k.get('key') in self.clicked
    def dataframe(self, df, **k): self.frames.append(df.copy())
    def metric(self, label, value, **k): self.metrics.append((label, value))
    def warning(self, value): self.messages.append(('warning', value))
    def info(self, value): self.messages.append(('info', value))
    def success(self, value): self.messages.append(('success', value))
    def error(self, value): self.messages.append(('error', value))


def seed():
    return {'c4l2_s3_acoustic_sources': sources(),
            'c4l2_s2_receptors_table': [{'Receptor': 'R1'}],
            'student_response': 'texto del alumno'}


def run_stage4(ui, saved, fail=False):
    writes = []
    def save(lab, candidate, stage):
        if fail: raise RuntimeError('offline')
        writes.append(deepcopy(candidate))
    def grid(df, **k):
        if 'LAeq predicho [dB(A)]' in df:
            df['LAeq predicho [dB(A)]'] = 60
        return df
    load_renderer(4)({'id': 'lab'}, saved, {
        'st': ui, 'pd': pd, 'header': lambda *a, **k: None,
        '_professional_grid': grid, '_save': save, 'NOISEMAP_URL': 'https://example.com',
    })
    return writes


class EquivalentSpectrumTests(unittest.TestCase):
    def test_source_signature_survives_storage_key_reordering(self):
        reordered = [dict(reversed(list(row.items()))) for row in sources()]
        self.assertEqual(source_fingerprint(sources()), source_fingerprint(reordered))

    def test_screenshot_rounding_is_accepted_in_all_eight_bands(self):
        _, expected = equivalent_spectrum(sources())
        for actual, reference in zip(expected, [108.447798,109.299652,98.340957,98.806287,96.785923,95.340957,91.625658,82.894072]):
            self.assertAlmostEqual(actual, reference, places=5)
        self.assertTrue(all(check_answers(dict(zip(BAND_LABELS, ANSWERS)), expected)))
        wrong = dict(zip(BAND_LABELS, [value + 1 for value in ANSWERS]))
        self.assertFalse(any(check_answers(wrong, expected)))

    def test_quantities_are_applied_once_without_intermediate_rounding(self):
        src = sources()[:1]
        src[0]['Cantidad'] = 3
        contributions, equivalent = equivalent_spectrum(src)
        for base, actual in zip(SPECTRA[0], equivalent):
            self.assertAlmostEqual(actual, base + 10 * math.log10(3), places=12)
        self.assertEqual(contributions[0], equivalent)

    def test_duplicate_machine_names_do_not_drop_energy(self):
        src = [sources()[0], deepcopy(sources()[0])]
        _, equivalent = equivalent_spectrum(src)
        self.assertAlmostEqual(equivalent[0], 96 + 10 * math.log10(2))

    def test_a_weighting_is_associated_with_frequency_not_array_offset(self):
        self.assertEqual(BAND_LABELS[0], '63 Hz')
        self.assertEqual(BAND_LABELS[-1], '8 kHz')
        self.assertEqual(A_CORRECTIONS[0], -26.2)
        bands = [-300] * 8
        bands[7] = 100
        self.assertAlmostEqual(weighted_power(bands), 98.9)
        _, equivalent = equivalent_spectrum(sources())
        per_source = sum(10 ** (weighted_power(src['Lw_bandas']) / 10) for src in sources())
        self.assertAlmostEqual(weighted_power(equivalent), 10 * math.log10(per_source))

    def test_nonfinite_incomplete_mislabeled_and_already_weighted_sources_block(self):
        for value in ('nan', 'inf', '-inf', '', None): self.assertIsNone(parse_level(value))
        self.assertEqual(parse_level('108,4'), 108.4)
        for change in ({'Lw_bandas': [100] * 7}, {'band_labels': LEGACY_LABELS},
                       {'Lw_bandas': [math.nan] * 8}, {'Cantidad': 1.5}, {'Cantidad': 0},
                       {'spectrum_weighting': 'A'}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError): equivalent_spectrum([{**sources()[0], **change}])

    def test_legacy_recovery_preserves_values_and_does_not_mutate_original(self):
        original = dict(zip(LEGACY_LABELS, map(str, ANSWERS)))
        recovered, changed = recover_answers(original)
        self.assertTrue(changed)
        self.assertEqual(list(recovered.values()), list(original.values()))
        self.assertEqual(list(original), LEGACY_LABELS)
        self.assertEqual(recover_answers(recovered), (recovered, False))

    def test_renderer_validates_and_saves_students_rounded_values_in_all_views(self):
        for role in ('Alumno', 'Proyección', 'Docente'):
            with self.subTest(role=role):
                ui = UI(role)
                ui.clicked = {'c4l2_s4_check_Escenario_1', 'c4l2_s4_save_Escenario_1'}
                saved = seed()
                writes = run_stage4(ui, saved)
                self.assertTrue(writes[-1]['done_4'])
                scenario = saved['c4l2_s4_scenarios'][0]
                self.assertEqual(scenario['Lw equivalente por bandas'], ANSWERS)
                self.assertEqual(scenario['band_labels'], BAND_LABELS)
                self.assertAlmostEqual(scenario['LWA equivalente [dB(A)]'], weighted_power(ANSWERS))
                self.assertEqual(saved['student_response'], 'texto del alumno')
                self.assertTrue(any('LWA global' in name for name, value in ui.metrics))
                ui.inputs['63 Hz'] = '120'
                ui.clicked = {'c4l2_s4_save_Escenario_1'}
                previous = deepcopy(saved)
                writes = run_stage4(ui, saved)
                for state in writes:
                    self.assertEqual(state['c4l2_s4_scenarios'][0]['Lw equivalente por bandas'], ANSWERS)
                    self.assertFalse(state['done_4'])
                    self.assertTrue(state['c4l2_s4_scenarios'][0]['requires_review'])
                self.assertTrue(any('suma energética correcta' in message for kind, message in ui.messages))

    def test_new_source_level_invalidates_an_old_check(self):
        ui = UI()
        ui.clicked = {'c4l2_s4_check_Escenario_1'}
        saved = seed()
        run_stage4(ui, saved)
        self.assertTrue(ui.session_state['c4l2_s4_check_Escenario_1_ok'])
        saved['c4l2_s3_acoustic_sources'][0]['Lw_bandas'] = [120] * 8
        ui.clicked = {'c4l2_s4_save_Escenario_1'}
        run_stage4(ui, saved)
        self.assertNotIn('c4l2_s4_scenarios', saved)
        self.assertFalse(ui.session_state['c4l2_s4_check_Escenario_1_ok'])

    def test_legacy_scenario_is_preserved_and_marked_for_review(self):
        ui = UI('Proyección')
        saved = seed()
        saved.update({'done_4': True, 'c4l2_s4_scenarios': [
            {'Etapa': STAGE, 'Lw equivalente por bandas': [108.448] * 8, 'Proyecto Noise Map': 'proyecto propio'}
        ]})
        run_stage4(ui, saved)
        self.assertFalse(saved['done_4'])
        self.assertTrue(saved['c4l2_s4_scenarios'][0]['requires_review'])
        self.assertEqual(saved['c4l2_s4_scenarios'][0]['Proyecto Noise Map'], 'proyecto propio')
        self.assertEqual(saved['c4l2_s4_scenarios'][0]['Lw equivalente por bandas'], [108.448] * 8)

    def test_draft_round_trip_preserves_legacy_and_current_answers(self):
        ui = UI()
        ui.inputs = {}
        saved = seed()
        old = dict(zip(LEGACY_LABELS, map(str, ANSWERS)))
        saved['c4l2_s4_drafts'] = {STAGE: {'answers': old}}
        ui.clicked = {'c4l2_s4_save_draft_Escenario_1'}
        run_stage4(ui, saved)
        draft = saved['c4l2_s4_drafts'][STAGE]
        self.assertEqual(list(draft['answers'].values()), list(old.values()))
        self.assertEqual(draft['answers_legacy'], old)
        new_ui = UI()
        new_ui.inputs = {}
        run_stage4(new_ui, saved)
        self.assertEqual(new_ui.session_state['c4l2_s4_answers_Escenario_1_octaves_v2'], draft['answers'])

    def test_failure_does_not_mark_scenario_complete(self):
        ui = UI()
        ui.clicked = {'c4l2_s4_save_Escenario_1'}
        saved = seed()
        previous = deepcopy(saved)
        self.assertEqual(run_stage4(ui, saved, fail=True), [])
        self.assertEqual(saved, previous)
        self.assertTrue(any(kind == 'error' for kind, message in ui.messages))

    def test_calculation_draft_can_be_saved_before_receptors_exist(self):
        ui = UI()
        ui.clicked = {'c4l2_s4_save_draft_Escenario_1'}
        saved = seed()
        saved.pop('c4l2_s2_receptors_table')
        run_stage4(ui, saved)
        self.assertEqual(saved['c4l2_s4_drafts'][STAGE]['answers'], dict(zip(BAND_LABELS, map(str, ANSWERS))))
        self.assertFalse(saved.get('done_4', False))

    def test_stage5_retains_saved_and_live_results_in_all_views(self):
        original = {'Frente': STAGE, 'Receptor': 'R1', '31,5 Hz': 50,
                    '63 Hz': 54, 'LAeq [dB(A)]': 60}
        for role in ('Alumno', 'Proyección', 'Docente'):
            with self.subTest(role=role):
                ui = UI(role)
                saved = {'c4l2_s5_detailed_results': [original]}
                ui.clicked = {'c4l2_s5_save_draft'}
                def dynamic(rows, **kwargs):
                    return pd.DataFrame(ui.session_state.get(kwargs['state_key'], rows))
                load_renderer(5)({'id': 'lab'}, saved, {
                    'st': ui, 'pd': pd, 'header': lambda *a, **k: None,
                    '_dynamic_grid': dynamic, '_save': lambda *a: None,
                    'NOISEMAP_URL': 'https://example.com',
                })
                row = saved['c4l2_s5_detailed_results'][0]
                for key, value in original.items(): self.assertEqual(row[key], value)
                self.assertIsNone(row['8 kHz'])
                self.assertTrue(any('No se han desplazado' in text for kind, text in ui.messages))

    def test_controlled_template_retains_legacy_values_and_adds_8khz(self):
        from labs.curso4_laboratorio_2_stage7 import _controlled_template, BANDS
        self.assertEqual(BANDS, BAND_LABELS)
        previous = {'Frente': STAGE, 'Receptor': 'R1', '31,5 Hz': 40,
                    '63 Hz': 43, '8 kHz': 32, 'LAeq controlado [dB(A)]': 55}
        self.assertEqual(_controlled_template([previous], [previous])[0]['31,5 Hz'], 40)
        self.assertEqual(_controlled_template([previous], [previous])[0]['8 kHz'], 32)


if __name__ == '__main__':
    unittest.main()
