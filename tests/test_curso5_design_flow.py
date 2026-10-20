"""UI-independent regression checks for the academic design workflow.

Run with unittest; the runtime provides Streamlit through _bind_runtime.
"""
from copy import deepcopy
from pathlib import Path
import unittest

from labs import curso5_laboratorio_1 as lab
from future_labs import FUTURE_LABS

ROOT = Path(__file__).resolve().parents[1]


class Surface:
    def __init__(self, values=None, submit=False):
        self.values = values or {}
        self.submit = submit
        self.messages = []
        self.images = []
        self.downloads = []

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def columns(self, spec): return [self] * (spec if isinstance(spec, int) else len(spec))
    def tabs(self, labels): return [self] * len(labels)
    def form(self, *args, **kwargs): return self
    def expander(self, *args, **kwargs): return self
    def text_area(self, label, value='', **kwargs): return self.values.get(label, value)
    def text_input(self, label, value='', **kwargs): return self.values.get(label, value)
    def number_input(self, label, value=None, **kwargs): return self.values.get(label, value)
    def checkbox(self, label, value=False, **kwargs): return self.values.get(label, value)
    def selectbox(self, label, options, index=0, **kwargs): return self.values.get(label, options[index])
    def form_submit_button(self, *args, **kwargs): return self.submit
    def button(self, *args, **kwargs): return False
    def markdown(self, text, **kwargs): self.messages.append(('markdown', text))
    def warning(self, text, **kwargs): self.messages.append(('warning', text))
    def success(self, text, **kwargs): self.messages.append(('success', text))
    def error(self, text, **kwargs): self.messages.append(('error', text))
    def info(self, text, **kwargs): self.messages.append(('info', text))
    def caption(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def dataframe(self, *args, **kwargs): pass
    def link_button(self, *args, **kwargs): pass
    def image(self, path, **kwargs): self.images.append(path)
    def download_button(self, label, **kwargs): self.downloads.append((label, kwargs))


class DesignFlowTests(unittest.TestCase):
    def setUp(self):
        self.originals = {name: getattr(lab, name, None) for name in ('st', 'PROJECT_ROOT', 'header', '_now', '_save_future_state')}
        self.persisted = []
        lab.PROJECT_ROOT = ROOT
        lab.header = lambda *args, **kwargs: None
        lab._now = lambda: '2026-10-20T18:00:00-03:00'
        lab._save_future_state = lambda ident, state: self.persisted.append(deepcopy(state))

    def tearDown(self):
        for name, value in self.originals.items():
            if value is None: lab.__dict__.pop(name, None)
            else: setattr(lab, name, value)

    def test_all_eleven_stages_render_without_saving_empty_forms(self):
        ui = Surface(); lab.st = ui
        for render in lab._STAGES:
            render(FUTURE_LABS[lab.CLASS_ID], {})
        self.assertFalse(self.persisted)
        self.assertFalse([m for m in ui.messages if m[0] == 'error' and 'no está disponible' in m[1]])

    def test_stage2_uses_four_raster_sheets_and_real_pdf_download(self):
        ui = Surface(); lab.st = ui
        lab._stage2({'id': 'test'}, {})
        self.assertEqual(4, len(ui.images))
        self.assertTrue(all(str(path).endswith('.png') for path in ui.images))
        data = ui.downloads[0][1]
        self.assertEqual('application/pdf', data['mime'])
        self.assertTrue(data['data'].startswith(b'%PDF'))

    def test_classification_objective_is_saved_and_recovered(self):
        state = {}
        ui = Surface({
            'Clase objetivo de diseño (no es clase obtenida)': 'Clase C',
            'Declaración de alcance de tu clasificación': 'ISO/TS 19488:2021 · cuatro situaciones del A-302 en fase de diseño. ' * 4,
            'Por qué no basta promediar las clases ni evaluar un único muro': 'La clase limitante y las características pendientes deben justificarse. ' * 3,
        }, submit=True)
        lab.st = ui; lab._stage3({'id': 'test'}, state)
        self.assertEqual('Clase C', self.persisted[-1]['c5l1_s3_target'])
        lab.st = Surface(); lab._stage4({'id': 'test'}, state)
        self.assertTrue(any('Clase C' in str(text) for _, text in lab.st.messages))

    def test_protocol_numeric_inputs_persist_and_reappear_in_calculation(self):
        values = {
            'TR estar [s]': .6, 'TR dormitorio [s]': .5,
            'Densidad HA [kg/m³]': 2400., 'Densidad sobrelosa [kg/m³]': 2000.,
            'Rigidez dinámica s′ [MN/m³] · si usas piso físico': 15., 'Exposición exterior Lden [dB]': 65.,
            'Fuentes de datos, hipótesis y antecedentes pendientes': 'Hipótesis académicas de cálculo; los espectros sanitarios requieren antecedentes. ' * 3,
            'Criterios de diseño que comprobarás en cada caso': 'Descriptor, límite, condición y nota de la tabla aplicable a cada caso. ' * 3,
            'Protocolo personal de cálculo': 'Conservo la base y comparo una variante, manteniendo geometría y fuente. ' * 4,
        }
        state = {'c5l1_s3_target': 'Clase C'}
        lab.st = Surface(values, submit=True); lab._stage4({'id': 'test'}, state)
        self.assertEqual(.6, self.persisted[-1]['c5l1_s4_inputs']['tr_stay'])
        lab.st = Surface(); lab._stage5({'id': 'test'}, state)
        self.assertTrue(any('Clase C' in str(text) for _, text in lab.st.messages))

    def test_incomplete_design_cannot_be_marked_complete(self):
        lab.st = Surface({'DₙT,w [dB]': 55., 'C [dB]': -2., 'Ctr [dB]': -5.}, submit=True)
        state = {}; lab._stage5({'id': 'test'}, state)
        self.assertFalse(state.get('c5l1_done_5', False))
        self.assertFalse(self.persisted)

    def test_service_raw_levels_require_normalization_confirmation(self):
        lab.st = Surface({'LAeq,nT [dB(A)]': 28., 'LAFmax,nT [dB(A)]': 33.}, submit=True)
        lab._stage8({'id': 'test'}, {})
        self.assertFalse(self.persisted)
        self.assertTrue(any('Comprueba la normalización' in str(text) for _, text in lab.st.messages))

    def test_documented_missing_service_descriptor_can_be_saved(self):
        narrative = 'Configuración, evidencia, dato faltante y condiciones normalizadas documentadas. ' * 3
        values = {
            'LAeq,nT [dB(A)]': None, 'LAFmax,nT [dB(A)]': 33.,
            'He comprobado normalización a T₀ = 0,5 s y condición temporal de las salidas': True,
            'Hay un descriptor sin determinar por falta de antecedentes': True,
            'Objetivo de diseño y descriptor': 'Clase C; LAFmax,nT según funcionamiento intermitente.',
            'Solución inicial y resultado base': narrative,
            'Cambio propuesto y efecto observado': narrative,
            'Identificación de las evidencias de SONARA': 'IN-01 / Base y Variante / informe 20-10',
            'Supuestos, configuración y trazabilidad': narrative,
        }
        state = {}; lab.st = Surface(values, submit=True); lab._stage8({'id': 'test'}, state)
        result = self.persisted[-1]['c5l1_result_IN-01']
        self.assertTrue(result['undetermined'])
        self.assertTrue(result['normalized'])
        self.assertIsNone(result['laeq'])
        self.assertEqual(33., result['lafmax'])


if __name__ == '__main__':
    unittest.main()
