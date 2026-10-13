"""Regresiones de las medidas de control del Curso 4 · Lab 2."""
import math
import unittest
from labs import curso4_control_models as m

class TreatmentTests(unittest.TestCase):
    def test_direct_reduction_is_energy_consistent(self):
        _,before,after=m.treatment_results(m.default_treatment('direct'))
        self.assertAlmostEqual(before-after,8.0,places=8)

    def test_opening_orientation_changes_receiver_exposure(self):
        cfg=m.default_treatment('semi')
        front=m.treatment_results(cfg,bearing=0)[2]
        back=m.treatment_results(cfg,bearing=180)[2]
        self.assertGreater(back,front)

    def test_absorption_affects_cavity_balance(self):
        lined=m.default_treatment(); bare=m.default_treatment()
        bare['enclosure_lining_mode']='unlined'
        self.assertLess(m.treatment_results(lined)[2],m.treatment_results(bare)[2])

    def test_energy_balance_with_open_partial_and_vent_faces(self):
        for kind in ('enclosure','semi','enclosure_silencer'):
            cfg=m.default_treatment(kind)
            cfg['enclosure_faces']['left'].update(state='partial',opening_pct=20.)
            for f in m.OCTAVE_BANDS:
                paths,reduction=m.enclosure_balance(cfg,f)
                self.assertGreaterEqual(reduction,0.)
                self.assertLessEqual(sum(p['Área transmisora [m²]'] for p in paths),sum(p['Área de pérdidas [m²]'] for p in paths)+1e-10)

    def test_ventilation_il_reduces_power(self):
        a=m.default_treatment('enclosure_silencer');b=m.default_treatment('enclosure_silencer')
        a['enclosure_vent_face']=b['enclosure_vent_face']='front'
        a['silencer_il_db']={str(f):0. for f in m.OCTAVE_BANDS}
        self.assertLess(m.treatment_results(b)[2],m.treatment_results(a)[2])

    def test_barrier_below_line_of_sight_has_no_screening(self):
        rows,before,after,_,_=m.barrier_results(height=1.)
        self.assertEqual(before,after)
        self.assertTrue(all(r['Abar [dB]']==0. for r in rows))

    def test_finite_barrier_controls_bands_without_exceeding_cap(self):
        rows,before,after,_,_=m.barrier_results()
        self.assertGreater(before,after)
        self.assertTrue(all(0.<=r['Abar [dB]']<=20. for r in rows))

    def test_zero_tl_and_zero_absorption_conserve_power(self):
        cfg=m.default_treatment();cfg['enclosure_lining_mode']='custom'
        cfg['enclosure_absorption_coeff']={str(f):0. for f in m.OCTAVE_BANDS}
        for face in cfg['enclosure_faces'].values(): face['rw_db']=0.
        self.assertAlmostEqual(m.enclosure_balance(cfg,500)[1],0.)

if __name__=='__main__': unittest.main()
