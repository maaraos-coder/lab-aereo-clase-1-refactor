"""Regresión: la Etapa 5 no remite a pautas docentes desde la vista alumno."""
from pathlib import Path


def test_stage5_student_warning_uses_student_only_guidance():
    source = (Path(__file__).resolve().parents[1] / "labs" / "curso4_laboratorio_2_stage5.py").read_text(encoding="utf-8")
    assert "Puedes revisar la metodología y la pauta docente" not in source
    assert "Verifica en la Etapa 4 que los frentes estén validados y guardados." in source


def test_teacher_pauta_is_guarded_by_role():
    source = (Path(__file__).resolve().parents[1] / "labs" / "curso4_laboratorio_2_stage5.py").read_text(encoding="utf-8")
    section = source.split("def _teacher_pauta(st,pd):", 1)[1].split("\ndef ", 1)[0]
    assert 'st.session_state.get("role")!="Docente"' in section
    assert "return" in section.split("with st.expander", 1)[0]
