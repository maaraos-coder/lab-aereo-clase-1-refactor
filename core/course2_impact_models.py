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

def ver_impact_velocity_before_contact(g=9.81, h_m=0.04):
    """Impact velocity immediately before contact, v0 = sqrt(2gh)."""
    g=float(g); h=float(h_m)
    if g <= 0 or h <= 0:
        raise ValueError("g y h deben ser positivos.")
    return math.sqrt(2.0*g*h)


def ver_impact_force_harmonic(fr_hz, mass_kg, v0_m_s):
    """Harmonic force amplitude used in Vér's periodic impact representation."""
    fr=float(fr_hz); mass=float(mass_kg); v0=float(v0_m_s)
    if fr <= 0 or mass <= 0 or v0 < 0:
        raise ValueError("fr y masa deben ser positivas; v0 no puede ser negativa.")
    return 2.0*fr*mass*v0


def ver_force_spectral_density(fr_hz, mass_kg, g=9.81, h_m=0.04):
    """S_f0 = 4 f_r m^2 g h."""
    fr=float(fr_hz); mass=float(mass_kg); g=float(g); h=float(h_m)
    if min(fr,mass,g,h) <= 0:
        raise ValueError("Todos los parámetros deben ser positivos.")
    return 4.0*fr*(mass**2)*g*h


def ver_lw_oct_db(rho_air, c_air, sigma_rad, rho_plate, c_l, eta_p, thickness_m):
    """Vér impact-noise radiated octave-band sound power relation.

    L_W,oct ≈ 10log10[(rho c sigma)/(5.1 rho_p^2 c_L eta_p t^3)] + 120
    """
    vals=[rho_air,c_air,sigma_rad,rho_plate,c_l,eta_p,thickness_m]
    if any(float(v) <= 0 for v in vals):
        raise ValueError("Todos los parámetros de L_W,oct deben ser positivos.")
    ratio=(float(rho_air)*float(c_air)*float(sigma_rad))/(
        5.1*(float(rho_plate)**2)*float(c_l)*float(eta_p)*(float(thickness_m)**3)
    )
    return 10.0*math.log10(ratio)+120.0


def ver_ln_supercritical_db(f_hz, r_db, sigma_rad=1.0, delta_ln_db=0.0):
    """Vér relation for the stated supercritical regime.

    L_n + R = 43 + 30log10(f) - 10log10(sigma_rad) - Delta L_n
    """
    f=float(f_hz); R=float(r_db); sigma=float(sigma_rad); delta=float(delta_ln_db)
    if f <= 0 or sigma <= 0:
        raise ValueError("f y sigma_rad deben ser positivos.")
    return 43.0 + 30.0*math.log10(f) - 10.0*math.log10(sigma) - delta - R


def ver_ln_subcritical_db(f_hz, r_db, eta_p, fc_hz, sigma_rad, delta_ln_db=0.0):
    """Vér relation for the stated subcritical regime.

    R + L_n = 39.5 + 20log10(f) - Delta L_n
              - 10log10[eta_p/(fc sigma_rad)]
    """
    f=float(f_hz); R=float(r_db); eta=float(eta_p)
    fc=float(fc_hz); sigma=float(sigma_rad); delta=float(delta_ln_db)
    if f <= 0 or eta <= 0 or fc <= 0 or sigma <= 0:
        raise ValueError("f, eta_p, fc y sigma_rad deben ser positivos.")
    return (
        39.5 + 20.0*math.log10(f) - delta
        - 10.0*math.log10(eta/(fc*sigma))
        - R
    )


def ver_ln_piecewise_db(f_hz, r_db, fc_hz, sigma_rad, eta_p, delta_ln_db=0.0):
    """Automatically select Vér sub/supercritical expression."""
    if float(f_hz) < float(fc_hz):
        return ver_ln_subcritical_db(
            f_hz, r_db, eta_p, fc_hz, sigma_rad, delta_ln_db
        ), "subcrítico"
    return ver_ln_supercritical_db(
        f_hz, r_db, sigma_rad, delta_ln_db
    ), "supercrítico"

