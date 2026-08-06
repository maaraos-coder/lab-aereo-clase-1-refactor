"""Cálculos acústicos y matemáticos puros compartidos por la aplicación."""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np


def mass_r(mass, frequency):
    return 20 * np.log10(np.maximum(np.asarray(mass) * np.asarray(frequency), 1)) - 47


def compound_r(areas: Sequence[float], ratings: Sequence[float]) -> float:
    """Combinación energética de componentes expresados en decibeles."""
    total_area = float(sum(areas))
    if total_area <= 0:
        raise ValueError("La superficie total debe ser mayor que cero.")
    if len(areas) != len(ratings):
        raise ValueError("Las listas de superficies y aislamientos deben tener igual longitud.")
    tau = sum(float(s) * 10 ** (-float(r) / 10) for s, r in zip(areas, ratings)) / total_area
    return -10 * math.log10(max(tau, 1e-30))


def geometry_term(volume: float, separating_area: float) -> float:
    """Término didáctico V/S para T0=0,5 s usado en el ejercicio MINVU."""
    if float(volume) <= 0 or float(separating_area) <= 0:
        raise ValueError("El volumen y la superficie separadora deben ser mayores que cero.")
    return 10 * math.log10(0.32 * float(volume) / float(separating_area))


def quirt_window_curve(m1, m2, gap, height, width, alpha, freqs):
    """Implementación didáctica del modelo de Quirt para ventanas dobles."""
    rho0 = 1.21
    c = 343.0
    freqs = np.asarray(freqs, dtype=float)
    f1 = (1 / (2 * math.pi)) * math.sqrt(((m1 + m2) * rho0 * c**2) / (gap * m1 * m2))
    low = mass_r(m1 + m2, freqs)
    leaf1 = mass_r(m1, freqs)
    leaf2 = mass_r(m2, freqs)
    high = (
        leaf1 + leaf2 + 10 * math.log10(alpha) + 10 * math.log10(gap)
        + 10 * math.log10((height + width) / (height * width)) + 3
    )
    return np.where(freqs < f1, low, high), f1


def rw_from_curve(curve, reference_curve):
    curve = np.asarray(curve, dtype=float)
    reference_curve = np.asarray(reference_curve, dtype=float)
    best = None
    for shift in range(-30, 31):
        ref = reference_curve + shift
        dev = np.maximum(ref - curve, 0)
        if dev.sum() <= 32:
            best = (int(ref[7]), ref, dev)
    return best


def mass_sheet_tau(mass, frequency, theta, rho_air=1.21, sound_speed=343.0):
    """Hoja flexible controlada por masa para un ángulo de incidencia."""
    omega = 2 * math.pi * frequency
    ratio = omega * mass * max(math.cos(math.radians(theta)), 0.001) / (2 * rho_air * sound_speed)
    return 1.0 / (1.0 + ratio**2)


def critical_frequency(rho, h_mm, young_gpa, poisson, sound_speed=343.0):
    h = h_mm / 1000
    surface_mass = rho * h
    stiffness = young_gpa * 1e9 * h**3 / (12 * (1 - poisson**2))
    fc = sound_speed**2 / (2 * math.pi) * math.sqrt(surface_mass / stiffness)
    return surface_mass, stiffness, fc


def mass_law_curve(mass, frequencies):
    frequencies = np.asarray(frequencies, dtype=float)
    return 20 * np.log10(np.maximum(mass * frequencies, 1)) - 47


def simple_real_curve(mass, fc, frequencies, loss=9):
    frequencies = np.asarray(frequencies, dtype=float)
    base = mass_law_curve(mass, frequencies)
    dip = loss * np.exp(-0.5 * (np.log2(frequencies / fc) / 0.30) ** 2)
    low = 5 * np.exp(-0.5 * (np.log2(frequencies / 90) / 0.55) ** 2)
    return base - dip - low


def sharp_parameters(m1, m2, depth):
    d = max(depth / 1000, 0.01)
    f0 = 60 * math.sqrt((1 / m1 + 1 / m2) / d)
    fl = max(f0 * 4, 200)
    return f0, fl


def sharp_curve(m1, m2, depth, frequencies, connection="Independiente"):
    frequencies = np.asarray(frequencies, dtype=float)
    f0, fl = sharp_parameters(m1, m2, depth)
    d = depth / 1000
    total = []
    for f in frequencies:
        if f < f0:
            value = float(mass_r(m1 + m2, f))
        elif f < fl:
            value = float(mass_r(m1, f) + mass_r(m2, f) + 20 * math.log10(max(f * d, 0.01)) - 29)
        else:
            value = float(mass_r(m1, f) + mass_r(m2, f) + 6)
        if connection == "Montante compartido":
            value -= 9
        elif connection == "Puente accidental":
            value -= 6
        total.append(value)
    return np.array(total), f0, fl


def panel_simple_tau(frequency, angles_rad, surface_mass, stiffness, loss_factor,
                     rho_air=1.18, sound_speed=343.0):
    """Coeficiente de transmisión angular para una placa simple homogénea."""
    omega = 2 * np.pi * np.asarray(frequency, dtype=float)
    theta = np.asarray(angles_rad, dtype=float)
    omega_grid = omega[..., np.newaxis]
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    mass_term = omega_grid * surface_mass * cos_theta / (2 * rho_air * sound_speed)
    flexural_term = omega_grid**2 * stiffness * sin_theta**4 / (sound_speed**4 * surface_mass)
    real_part = 1 + loss_factor * mass_term * flexural_term
    imaginary_part = mass_term * (1 - flexural_term)
    return 1 / np.maximum(real_part**2 + imaginary_part**2, 1e-15)


def panel_simple_field_tl(frequencies, surface_mass, stiffness, loss_factor):
    """Cálculo de campo para una placa simple entre 0 y 78 grados."""
    angles = np.linspace(0.0, np.deg2rad(78.0), 720)
    tau_angular = panel_simple_tau(frequencies, angles, surface_mass, stiffness, loss_factor)
    weights = np.sin(angles) * np.cos(angles)
    integrand = tau_angular * weights
    if hasattr(np, "trapezoid"):
        integral = np.trapezoid(integrand, angles, axis=-1)
    else:
        integral = np.trapz(integrand, angles, axis=-1)
    normalizer = 2.0904
    tau_field = np.maximum(normalizer * integral, 1e-12)
    tl_field = -10 * np.log10(tau_field)
    return tau_field, tl_field, angles, tau_angular, normalizer
