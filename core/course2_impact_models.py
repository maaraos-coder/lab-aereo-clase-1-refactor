"""Shared didactic calculations for Curso 2 · Laboratorio 1 · Etapas 5–7.

No ISO 12354, ISO 717-2 or single-number ratings are implemented here.
Cremer/Vér outputs below are deliberately ASYMPTOTIC DIDACTIC TRENDS, not
universal/full formulations.
"""
from __future__ import annotations
import math
import numpy as np

BANDS = np.array([125,160,200,250,315,400,500,630,800,1000,1250,1600,2000], dtype=float)

def surface_mass(rho, h_m):
    return float(rho) * float(h_m)

def reduced_mass(m1, m2):
    m1, m2 = float(m1), float(m2)
    if m1 <= 0 or m2 <= 0:
        raise ValueError("m1 y m2 deben ser positivas")
    return m1*m2/(m1+m2)

def natural_frequency(m1, m2, s_mn_m3):
    mr = reduced_mass(m1, m2)
    s = float(s_mn_m3)*1e6
    if s <= 0:
        raise ValueError("s' debe ser positiva")
    return mr, (1/(2*math.pi))*math.sqrt(s/mr)

def transmissibility_force(r, zeta):
    r, zeta = float(r), float(zeta)
    return math.sqrt((1+(2*zeta*r)**2)/((1-r**2)**2+(2*zeta*r)**2))

def ln0_above_fc(f_hz, R_db, sigma_rad=1.0):
    f, R, sigma = float(f_hz), float(R_db), float(sigma_rad)
    if f <= 0 or sigma <= 0:
        raise ValueError("f y sigma deben ser positivas")
    return 43 + 30*math.log10(f) - 10*math.log10(sigma) - R

def asymptotic_delta_trend(freqs, f0, model="Cremer"):
    """Didactic above-resonance tendency only.
    Cremer: 12 dB/oct, Vér: 9 dB/oct. Values below f0 are not extrapolated;
    NaN is returned there instead of inventing a resonant dip.
    """
    freqs = np.asarray(freqs, dtype=float)
    f0 = float(f0)
    slope = 12.0 if str(model).lower().startswith("cremer") else 9.0
    out = np.full(freqs.shape, np.nan, dtype=float)
    mask = freqs > f0
    out[mask] = slope*np.log2(freqs[mask]/f0)
    return out

def nearest_band(f):
    f=float(f)
    return float(BANDS[np.argmin(np.abs(np.log(BANDS/f)))])
