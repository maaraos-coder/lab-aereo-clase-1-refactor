"""Reusable didactic calculation helpers for Curso 2 · Laboratorio 1.

These functions intentionally separate:
- bare-slab prediction L_n,0(f) in the simplified verified regime used in Stage 5;
- mechanical mass-spring-mass quantities used in Stage 6;
- asymptotic Cremer/Vér *didactic trends*, not normative/full predictive formulas.

No ISO 12354 / ISO 717-2 single-number processing is implemented here.
"""
from __future__ import annotations

import math
import numpy as np

THIRD_OCTAVE_BANDS = np.array(
    [125,160,200,250,315,400,500,630,800,1000,1250,1600,2000],
    dtype=float,
)

def surface_mass(rho_kg_m3: float, h_m: float) -> float:
    return float(rho_kg_m3) * float(h_m)

def reduced_surface_mass(m1: float, m2: float) -> float:
    m1=float(m1); m2=float(m2)
    if m1 <= 0 or m2 <= 0:
        raise ValueError("Las masas superficiales deben ser positivas.")
    return (m1*m2)/(m1+m2)

def natural_frequency_hz(m1: float, m2: float, s_mn_m3: float) -> tuple[float,float]:
    mr = reduced_surface_mass(m1,m2)
    s = float(s_mn_m3)*1e6
    if s <= 0:
        raise ValueError("La rigidez dinámica debe ser positiva.")
    f0 = (1.0/(2.0*math.pi))*math.sqrt(s/mr)
    return mr, f0

def force_transmissibility(r: float, zeta: float) -> float:
    r=float(r); zeta=float(zeta)
    return math.sqrt(
        (1.0+(2.0*zeta*r)**2) /
        ((1.0-r**2)**2+(2.0*zeta*r)**2)
    )

def ln0_above_fc_db(f_hz: float, r_db: float, sigma_rad: float=1.0) -> float:
    """Simplified Stage-5 bare-slab relation for the stated applicable regime.

    L_n,0 = 43 + 30 log10(f) - 10 log10(sigma_rad) - R(f)

    This is not a universal expression and the caller must label its field
    of application explicitly.
    """
    f=float(f_hz); R=float(r_db); sigma=float(sigma_rad)
    if f <= 0 or sigma <= 0:
        raise ValueError("f y sigma_rad deben ser positivos.")
    return 43.0 + 30.0*math.log10(f) - 10.0*math.log10(sigma) - R

def delta_ln_asymptotic_trend_db(f_hz, f0_hz: float, model: str="Cremer"):
    """Didactic asymptotic trend retained from the previous Stage 6.

    It is deliberately named 'trend' and MUST NOT be presented as a
    universal/normative ΔL_n formula. Values below f0 are clipped to zero
    because only the above-resonance asymptotic tendency is being displayed.
    """
    arr=np.asarray(f_hz,dtype=float)
    f0=float(f0_hz)
    if f0 <= 0:
        raise ValueError("f0 debe ser positiva.")
    slope = 12.0 if str(model).lower().startswith("cremer") else 9.0
    ratio=np.maximum(arr/f0,1.0)
    return slope*np.log2(ratio)

def nearest_third_octave(f_hz: float) -> float:
    f=max(float(f_hz),1e-9)
    return float(THIRD_OCTAVE_BANDS[np.argmin(np.abs(np.log(THIRD_OCTAVE_BANDS/f)))])
