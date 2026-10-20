from pathlib import Path

from future_labs import FUTURE_LABS
from labs import curso5_laboratorio_1 as lab


def test_course5_lab1_is_specialized_and_has_eleven_stages():
    metadata = FUTURE_LABS[lab.CLASS_ID]
    assert metadata["number"] == 1
    assert len(metadata["stages"]) == 11
    assert "SONARA" in metadata["focus"]
    assert "clasificación ISO realizada por el alumno" in metadata["focus"]


def test_case_contains_all_acoustic_families_and_no_prefilled_class():
    assert set(lab.CALCULATION_CASES) == {
        "Aéreo interior",
        "Impacto",
        "Fachada",
        "Instalaciones",
    }
    assert lab.PROJECT["status"].lower().startswith("caso ficticio")
    assert "class" not in lab.PROJECT
    assert "classification" not in lab.PROJECT


def test_project_dossier_has_geometry_materials_and_drawings():
    assert lab.PROJECT["dwellings"] == 20
    assert len(lab.ROOMS) >= 5
    assert len(lab.MATERIALS) >= 7
    asset_dir = Path(__file__).resolve().parents[1] / "assets" / "curso5_lab1"
    expected = {
        "planta_tipo.svg",
        "corte_aa.svg",
        "fachada_norte.svg",
        "detalles_constructivos.svg",
    }
    assert expected == {path.name for path in asset_dir.glob("*.svg")}


def test_sonara_is_external_calculator_and_iso_is_student_task():
    source = Path(lab.__file__).read_text(encoding="utf-8")
    assert lab.SONARA_URL == "https://sonara-ea1b.onrender.com/"
    assert "La plataforma no calcula ni recomienda la clase" in source
    assert "clasificación ISO/TS 19488 son responsabilidad del estudiante" in source
    assert "ISO/TS 19488:2021" in source


def test_stage_dispatch_is_complete():
    assert len(lab._STAGES) == 11
    assert [renderer.__name__ for renderer in lab._STAGES] == [
        f"_stage{index}" for index in range(11)
    ]


def test_course5_lab2_is_reserved_for_the_future_real_project():
    lab2 = FUTURE_LABS["clase-10-certificaciones-lab-2"]
    assert "Proyecto real" in lab2["focus"]
    assert "PRÓXIMO LABORATORIO" in lab2["focus"]
    assert "CES" not in lab2["focus"]
    assert all("CES" not in " ".join(stage) for stage in lab2["stages"])
