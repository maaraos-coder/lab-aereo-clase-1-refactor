"""Bandas de BS 5228 / Adenda 2 y cálculos de potencia sin dependencia de UI."""
import math
import hashlib
import json

BAND_LABELS = ["63 Hz", "125 Hz", "250 Hz", "500 Hz", "1 kHz", "2 kHz", "4 kHz", "8 kHz"]
A_CORRECTIONS = [-26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
LEGACY_LABELS = ["31,5 Hz"] + BAND_LABELS[:-1]
ANSWER_TOLERANCE_DB = 0.5


def source_fingerprint(sources):
    # JSONB puede devolver las claves en otro orden tras recuperar el avance.
    canonical = json.dumps(sources, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def parse_level(value):
    try:
        number = float(str(value).strip().replace(",", "."))
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def sum_levels(values):
    values = list(values)
    if not values or any(parse_level(v) is None for v in values):
        raise ValueError("Completa todos los niveles con números finitos.")
    values = [float(v) for v in values]
    peak = max(values)
    return peak + 10 * math.log10(sum(10 ** ((v - peak) / 10) for v in values))


def equivalent_spectrum(sources):
    """Suma bandas homólogas, sin redondear ni aplicar ponderación A."""
    contributions = []
    for source in sources:
        # Los registros históricos sin metadatos pertenecen al mismo catálogo
        # BS/Adenda (63 Hz–8 kHz). Nunca desplazar un espectro declarado distinto.
        labels = source.get("band_labels", BAND_LABELS)
        if not isinstance(labels, (list, tuple)) or list(labels) != BAND_LABELS:
            raise ValueError("Las fuentes deben tener las mismas bandas de 63 Hz a 8 kHz. Revisa la Etapa 3.")
        if source.get("spectrum_weighting", "Z") != "Z":
            raise ValueError("Se requieren bandas Lw sin ponderación A. Revisa la Etapa 3.")
        bands = source.get("Lw_bandas") or []
        if len(bands) != len(BAND_LABELS) or any(parse_level(v) is None for v in bands):
            raise ValueError("Falta un espectro de potencia válido en la Etapa 3.")
        quantity = parse_level(source.get("Cantidad"))
        if quantity is None or quantity < 1 or not quantity.is_integer():
            raise ValueError("La cantidad de máquinas debe ser un entero positivo. Revisa la Etapa 1.")
        contributions.append([float(v) + 10 * math.log10(quantity) for v in bands])
    if not contributions:
        raise ValueError("Selecciona al menos una fuente.")
    return contributions, [sum_levels(band) for band in zip(*contributions)]


def check_answers(answers, expected):
    return [parse_level(answers.get(label)) is not None
            and abs(parse_level(answers[label]) - value) <= ANSWER_TOLERANCE_DB + 1e-9
            for label, value in zip(BAND_LABELS, expected)]


def weighted_power(bands):
    if len(bands) != len(BAND_LABELS):
        raise ValueError("Se requieren las ocho bandas de octava.")
    return sum_levels([float(v) + correction for v, correction in zip(bands, A_CORRECTIONS)])


def recover_answers(answers):
    """Conserva los números por posición de la antigua tabla mal rotulada."""
    if "31,5 Hz" in answers and "8 kHz" not in answers:
        return {new: answers.get(old, "") for old, new in zip(LEGACY_LABELS, BAND_LABELS)}, True
    return dict(answers), False
