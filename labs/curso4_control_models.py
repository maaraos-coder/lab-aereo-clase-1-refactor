"""Etapa 6: cálculos docentes compatibles con Noise Map Lab.
Funciones de cerramiento y barrera tomadas de maaraos-coder/noisemap,
rama v3-react-maplibre. El ejemplo exterior usa campo libre (G=0,
sin atmósfera, reflexiones ni edificios); el mapa conserva el cálculo completo.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict, Optional
OCTAVE_BANDS = (63,125,250,500,1000,2000,4000,8000)
EARTH_RADIUS_M = 6371000.0
SPEED_OF_SOUND_M_S = 343.0


@dataclass
class Source:
    name: str
    lat: float
    lon: float
    height_m: float = 1.5
    lw_db: float = 100.0
    dc_db: float = 0.0
    enabled: bool = True
    ground_elevation_m: float = 0.0


@dataclass
class Barrier:
    name: str
    lat_a: float
    lon_a: float
    lat_b: float
    lon_b: float
    height_m: float = 3.0
    enabled: bool = True
    ground_elevation_m: float = 0.0
    reflection_percent: float = 0.0
    # Stand-alone barriers have acoustically free vertical ends. Building
    # facades meet adjacent facades, so their endpoints must not fade to 0 dB.
    free_end_a: bool = True
    free_end_b: bool = True
    diffraction_enabled: bool = True


def latlon_to_xy(lat: float, lon: float, lat0: float, lon0: float) -> tuple[float, float]:
    """Local tangent-plane approximation, adequate for small teaching maps."""
    lat_r = math.radians(lat)
    lat0_r = math.radians(lat0)
    dlat = math.radians(lat - lat0)
    dlon = math.radians(lon - lon0)
    x = EARTH_RADIUS_M * dlon * math.cos((lat_r + lat0_r) / 2.0)
    y = EARTH_RADIUS_M * dlat
    return x, y


def xy_to_latlon(x: float, y: float, lat0: float, lon0: float) -> tuple[float, float]:
    lat = lat0 + math.degrees(y / EARTH_RADIUS_M)
    lat_mid = math.radians((lat + lat0) / 2.0)
    lon = lon0 + math.degrees(x / (EARTH_RADIUS_M * max(math.cos(lat_mid), 1e-9)))
    return lat, lon


def geometric_divergence_db(distance_m: float) -> float:
    r = max(float(distance_m), 1.0)
    return 20.0 * math.log10(r) + 11.0


def iso9613_2024_diffraction_dz_db(
    path_difference_m: float,
    d_source_edge_m: float,
    d_edge_receiver_m: float,
    direct_distance_m: float,
    frequency_hz: float,
    *,
    lateral: bool = False,
    c2: float = 20.0,
    c3: float = 1.0,
    e_m: float = 0.0,
    max_db: float = 20.0,
) -> float:
    """ISO 9613-2:2024 §7.4.1 barrier attenuation Dz, Formulae (18)-(21)."""
    wavelength = SPEED_OF_SOUND_M_S / max(float(frequency_hz), 1.0)
    z = float(path_difference_m)
    z_min = -2.0 * wavelength / max(c2 * c3, 1e-12)
    if z <= z_min:
        return 0.0

    if lateral:
        k_met = 1.0
    else:
        denom = max(2.0 * (z - z_min), 1e-12)
        geometric = (
            (max(float(d_source_edge_m), float(d_edge_receiver_m)) + max(float(e_m), 0.0))
            * min(float(d_source_edge_m), float(d_edge_receiver_m))
            * max(float(direct_distance_m), 0.0)
            / denom
        )
        k_met = math.exp(-(1.0 / 2000.0) * math.sqrt(max(geometric, 0.0)))

    argument = 1.0 + (2.0 + (c2 / wavelength) * c3 * z) * k_met
    dz = 10.0 * math.log10(max(argument, 1.0))
    return min(float(max_db), max(0.0, dz))


def _cross(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * by - ay * bx


def barrier_attenuation_db(
    sx: float,
    sy: float,
    sz: float,
    rx: float,
    ry: float,
    rz: float,
    barrier: Barrier,
    lat0: float,
    lon0: float,
    frequency_hz: float = 500.0,
    max_barrier_db: float = 20.0,
    ground_attenuation_db_value: float = 0.0,
) -> float:
    """ISO 9613-2:2024 §7.4 finite single-barrier screening.

    Top diffraction uses the 2024 Dz and Kmet formulation. Lateral diffraction
    around both vertical ends uses Kmet=1 and the three paths are combined
    energetically according to Formula (25).
    """
    ax, ay = latlon_to_xy(barrier.lat_a, barrier.lon_a, lat0, lon0)
    bx, by = latlon_to_xy(barrier.lat_b, barrier.lon_b, lat0, lon0)

    vx, vy = rx - sx, ry - sy
    wx, wy = bx - ax, by - ay
    wall_length = math.hypot(wx, wy)
    if wall_length < 1e-9:
        return 0.0

    den = _cross(vx, vy, wx, wy)
    if abs(den) < 1e-9:
        return 0.0

    qx, qy = ax - sx, ay - sy
    t = _cross(qx, qy, wx, wy) / den
    u = _cross(qx, qy, vx, vy) / den
    if t <= 0.0 or t >= 1.0:
        return 0.0

    ix = sx + t * vx
    iy = sy + t * vy
    los_z = sz + t * (rz - sz)
    barrier_top_z = barrier.ground_elevation_m + barrier.height_m
    if barrier_top_z <= los_z:
        return 0.0

    direct = math.sqrt(vx * vx + vy * vy + (rz - sz) ** 2)

    # Vertical-plane path over the top edge.
    dss_top = math.sqrt((ix - sx) ** 2 + (iy - sy) ** 2 + (barrier_top_z - sz) ** 2)
    dsr_top = math.sqrt((rx - ix) ** 2 + (ry - iy) ** 2 + (rz - barrier_top_z) ** 2)
    z_top = dss_top + dsr_top - direct
    dz_top = iso9613_2024_diffraction_dz_db(
        z_top, dss_top, dsr_top, direct, frequency_hz,
        lateral=False, max_db=max_barrier_db,
    )
    # Formula (16)/(17): positive ground attenuation is replaced by top-edge
    # screening, while negative ground effect is not subtracted.
    a_top = max(0.0, dz_top - max(float(ground_attenuation_db_value), 0.0))

    # ISO lateral paths around the two vertical end edges. At lateral edges
    # Kmet=1. A side path is relevant when it is longer than the direct path.
    edge_z = min(max(los_z, barrier.ground_elevation_m), barrier_top_z)

    def side_attenuation(ex: float, ey: float) -> float:
        dss = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2 + (edge_z - sz) ** 2)
        dsr = math.sqrt((rx - ex) ** 2 + (ry - ey) ** 2 + (rz - edge_z) ** 2)
        z_side = dss + dsr - direct
        if z_side <= 0.0:
            return 0.0
        return iso9613_2024_diffraction_dz_db(
            z_side, dss, dsr, direct, frequency_hz,
            lateral=True, max_db=max_barrier_db,
        )

    a_side1 = side_attenuation(ax, ay)
    a_side2 = side_attenuation(bx, by)

    # ISO 9613-2:2024 §7.4.3 relevance criterion:
    # a lateral path is neglected when the maximum lateral deviation of its
    # supporting point from the direct S-R line exceeds 8 times the maximum
    # vertical deviation of the top-path supporting point.
    horizontal_direct = math.hypot(vx, vy)
    vertical_deviation = max(0.0, barrier_top_z - los_z)

    def lateral_deviation(ex: float, ey: float) -> float:
        if horizontal_direct <= 1e-9:
            return 0.0
        return abs(_cross(vx, vy, ex - sx, ey - sy)) / horizontal_direct

    lateral_limit = 8.0 * vertical_deviation

    def smoothstep01(value: float) -> float:
        x = min(1.0, max(0.0, float(value)))
        return x * x * (3.0 - 2.0 * x)

    # Avoid a binary on/off switch for lateral paths at the relevance limit.
    # A narrow transition band keeps the finite-screen solution continuous
    # while retaining the ISO relevance criterion away from the boundary.
    relevance_softness = max(0.25, 0.12 * max(lateral_limit, 1.0))

    def lateral_weight(ex: float, ey: float) -> float:
        deviation = lateral_deviation(ex, ey)
        if lateral_limit <= 1e-9:
            return 0.0
        lower = max(0.0, lateral_limit - relevance_softness)
        upper = lateral_limit + relevance_softness
        if deviation <= lower:
            return 1.0
        if deviation >= upper:
            return 0.0
        return 1.0 - smoothstep01((deviation - lower) / max(upper - lower, 1e-9))

    side1_weight = lateral_weight(ax, ay)
    side2_weight = lateral_weight(bx, by)

    # The ideal geometrical shadow boundary of a finite screen is abrupt, but
    # the diffracted acoustic field is not. The former hard u=0/1 cutoff caused
    # 8–10 dB jumps between neighbouring map points. Taper the screening within
    # roughly one first-Fresnel-zone radius of each free end so attenuation
    # tends continuously to zero as the direct ray reaches the end.
    #
    # This taper is a numerical/engineering extension around the finite-screen
    # shadow boundary; the underlying Dz calculation remains unchanged.
    nearest_edge_fraction = min(u, 1.0 - u)
    if nearest_edge_fraction <= 0.0:
        return 0.0

    d1_horizontal = math.hypot(ix - sx, iy - sy)
    d2_horizontal = math.hypot(rx - ix, ry - iy)
    wavelength = SPEED_OF_SOUND_M_S / max(float(frequency_hz), 1.0)
    fresnel_radius = math.sqrt(
        max(0.0, wavelength * d1_horizontal * d2_horizontal / max(d1_horizontal + d2_horizontal, 1e-9))
    )
    edge_transition_m = min(6.0, max(0.75, fresnel_radius))
    edge_distance_m = nearest_edge_fraction * wall_length
    edge_weight = smoothstep01(edge_distance_m / edge_transition_m)

    energies = [10.0 ** (-a_top / 10.0)]
    if side1_weight > 1e-6:
        energies.append(side1_weight * 10.0 ** (-a_side1 / 10.0))
    if side2_weight > 1e-6:
        energies.append(side2_weight * 10.0 ** (-a_side2 / 10.0))

    a_bar = -10.0 * math.log10(max(sum(energies), 1e-12))
    a_bar = min(float(max_barrier_db), max(0.0, a_bar))
    return a_bar * edge_weight


def _dict_band_value(values: Dict[str, float], band_hz: float, default: float = 0.0) -> float:
    """Return a spectral value using logarithmic-frequency interpolation.

    Exact octave-band values are preserved. Frequencies between defined bands
    are interpolated in log(f), which is preferable to snapping Single mode to
    the nearest octave band.
    """
    if not values:
        return float(default)

    pts = []
    for band in OCTAVE_BANDS:
        raw = values.get(str(band), values.get(band))
        if raw is None:
            continue
        try:
            pts.append((float(band), max(0.0, float(raw))))
        except (TypeError, ValueError):
            continue
    if not pts:
        return float(default)

    f = max(float(band_hz), 1e-6)
    pts.sort()
    if f <= pts[0][0]:
        return pts[0][1]
    if f >= pts[-1][0]:
        return pts[-1][1]

    for (f0, v0), (f1, v1) in zip(pts, pts[1:]):
        if f0 <= f <= f1:
            if abs(f1 - f0) < 1e-12:
                return v0
            t = (math.log(f) - math.log(f0)) / (math.log(f1) - math.log(f0))
            return v0 + t * (v1 - v0)
    return float(default)


def _dict_band_value_signed(values: Dict[str, float], band_hz: float, default: float = 0.0) -> float:
    """Log-frequency interpolation that preserves signed spectral offsets."""
    if not values:
        return float(default)
    pts = []
    for band in OCTAVE_BANDS:
        raw = values.get(str(band), values.get(band))
        if raw is None:
            continue
        try:
            pts.append((float(band), float(raw)))
        except (TypeError, ValueError):
            continue
    if not pts:
        return float(default)
    f = max(float(band_hz), 1e-6)
    pts.sort()
    if f <= pts[0][0]:
        return pts[0][1]
    if f >= pts[-1][0]:
        return pts[-1][1]
    for (f0, v0), (f1, v1) in zip(pts, pts[1:]):
        if f0 <= f <= f1:
            t = (math.log(f) - math.log(f0)) / max(math.log(f1) - math.log(f0), 1e-12)
            return v0 + t * (v1 - v0)
    return float(default)


def _a_weighting_correction_db(frequency_hz: float) -> float:
    """IEC-style analytical A-weighting correction for an arbitrary frequency."""
    f = max(float(frequency_hz), 1e-6)
    f2 = f * f
    numerator = (12200.0 ** 2) * (f ** 4)
    denominator = (
        (f2 + 20.6 ** 2)
        * math.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
        * (f2 + 12200.0 ** 2)
    )
    ra = numerator / max(denominator, 1e-30)
    return 20.0 * math.log10(max(ra, 1e-30)) + 2.0


def _rw_estimated_tl_db(rw_db: float, band_hz: float) -> float:
    """Estimate an octave-band R/TL curve from a single Rw.

    The shape follows the ISO 717-1 reference-curve trend around 125-3150 Hz
    and is explicitly only a design estimate; 63 Hz and the upper octaves are
    extrapolated. A measured/certified spectrum should be preferred.
    """
    rw = max(0.0, float(rw_db or 0.0))
    offsets = {
        "63": -25.0,
        "125": -16.0,
        "250": -7.0,
        "500": 0.0,
        "1000": 3.0,
        "2000": 4.0,
        "4000": 4.0,
        "8000": 4.0,
    }
    return max(0.0, rw + _dict_band_value_signed(offsets, band_hz, 0.0))


ENCLOSURE_ABSORPTION_PRESETS = {
    # Generic room-side absorption coefficients for educational enclosure design.
    # These are not material certificates.
    "unlined": {
        "63": 0.02, "125": 0.02, "250": 0.03, "500": 0.04,
        "1000": 0.05, "2000": 0.05, "4000": 0.05, "8000": 0.05,
    },
    "low": {
        "63": 0.04, "125": 0.06, "250": 0.10, "500": 0.16,
        "1000": 0.22, "2000": 0.28, "4000": 0.30, "8000": 0.30,
    },
    "medium": {
        "63": 0.08, "125": 0.15, "250": 0.30, "500": 0.50,
        "1000": 0.65, "2000": 0.75, "4000": 0.80, "8000": 0.80,
    },
    "high": {
        "63": 0.15, "125": 0.30, "250": 0.55, "500": 0.72,
        "1000": 0.84, "2000": 0.90, "4000": 0.92, "8000": 0.92,
    },
}


def _enclosure_absorption_alpha(source, band_hz: float) -> float:
    mode = str(getattr(source, "enclosure_lining_mode", "unlined") or "unlined").lower()
    if mode == "custom":
        alpha = _dict_band_value(getattr(source, "enclosure_absorption_coeff", {}) or {}, band_hz, 0.05)
    else:
        alpha = _dict_band_value(ENCLOSURE_ABSORPTION_PRESETS.get(mode, ENCLOSURE_ABSORPTION_PRESETS["unlined"]), band_hz, 0.05)
    return min(max(float(alpha), 0.0), 0.99)


def _face_tl_db(source, face_name: str, band_hz: float) -> float:
    faces = getattr(source, "enclosure_faces", None) or {}
    face = faces.get(face_name) or {}
    mode = str(face.get("acoustic_mode", "rw") or "rw").lower()
    if mode == "spectrum":
        return _dict_band_value(face.get("tl_db") or {}, band_hz)
    return _rw_estimated_tl_db(
        float(face.get("rw_db", getattr(source, "enclosure_rw_db", 30.0)) or 0.0),
        band_hz,
    )


def _offset_latlon(lat: float, lon: float, east_m: float, north_m: float) -> tuple[float, float]:
    dlat = math.degrees(float(north_m) / 6_371_000.0)
    lat2 = float(lat) + dlat
    mean_lat = math.radians((float(lat) + lat2) / 2.0)
    dlon = math.degrees(float(east_m) / (6_371_000.0 * max(math.cos(mean_lat), 1e-9)))
    return lat2, float(lon) + dlon


def _enclosure_face_geometry(source) -> Dict[str, dict]:
    length = max(float(getattr(source, "enclosure_length_m", 2.0) or 2.0), 0.01)
    width = max(float(getattr(source, "enclosure_width_m", 2.0) or 2.0), 0.01)
    height = max(float(getattr(source, "enclosure_height_m", 2.5) or 2.5), 0.01)
    az = math.radians(float(getattr(source, "enclosure_azimuth_deg", 0.0) or 0.0))

    # Horizontal unit vectors, with azimuth measured clockwise from North.
    front = (math.sin(az), math.cos(az))
    right = (math.cos(az), -math.sin(az))

    center_z = max(float(source.height_m), height / 2.0)
    wall_z = center_z
    roof_z = center_z + height / 2.0
    floor_z = max(0.05, center_z - height / 2.0)

    specs = {
        "front": (front[0] * length / 2.0, front[1] * length / 2.0, wall_z, width * height, (front[0], front[1], 0.0)),
        "back": (-front[0] * length / 2.0, -front[1] * length / 2.0, wall_z, width * height, (-front[0], -front[1], 0.0)),
        "right": (right[0] * width / 2.0, right[1] * width / 2.0, wall_z, length * height, (right[0], right[1], 0.0)),
        "left": (-right[0] * width / 2.0, -right[1] * width / 2.0, wall_z, length * height, (-right[0], -right[1], 0.0)),
        "roof": (0.0, 0.0, roof_z, length * width, (0.0, 0.0, 1.0)),
        "floor": (0.0, 0.0, floor_z, length * width, (0.0, 0.0, -1.0)),
    }

    result = {}
    for name, (east, north, z, area, normal) in specs.items():
        lat, lon = _offset_latlon(source.lat, source.lon, east, north)
        result[name] = {
            "lat": lat,
            "lon": lon,
            "height_m": z,
            "area_m2": max(area, 1e-9),
            "normal": normal,
        }
    return result


def _face_open_fraction(face: dict) -> float:
    state = str(face.get("state", "closed") or "closed").lower()
    if state == "open":
        return 1.0
    if state == "partial":
        return min(max(float(face.get("opening_pct", 25.0) or 0.0) / 100.0, 0.0), 1.0)
    return 0.0


def _face_radiation_dc_db(
    face_geometry: dict,
    receiver_lat: float,
    receiver_lon: float,
    receiver_abs_z: float,
    source_ground_elevation_m: float,
) -> Optional[float]:
    """Lambertian half-space radiation from a panel/opening.

    Q(theta)=4*cos(theta), normalized so the pattern integrates to the face
    sound power over 4π. Returns None when the receiver lies behind the face.
    """
    sx, sy = latlon_to_xy(face_geometry["lat"], face_geometry["lon"], face_geometry["lat"], face_geometry["lon"])
    rx, ry = latlon_to_xy(receiver_lat, receiver_lon, face_geometry["lat"], face_geometry["lon"])
    dz = receiver_abs_z - (source_ground_elevation_m + float(face_geometry["height_m"]))
    distance = math.sqrt((rx - sx) ** 2 + (ry - sy) ** 2 + dz ** 2)
    if distance <= 1e-9:
        return 0.0

    ux, uy, uz = (rx - sx) / distance, (ry - sy) / distance, dz / distance
    nx, ny, nz = face_geometry["normal"]
    cos_theta = nx * ux + ny * uy + nz * uz
    if cos_theta <= 0.0:
        return None
    q = max(4.0 * cos_theta, 1e-12)
    return 10.0 * math.log10(q)


def _enclosure_virtual_sources(
    source,
    band_hz: float,
    input_lw_db: float,
    receiver_lat: float,
    receiver_lon: float,
    receiver_height_m: float,
    source_ground_elevation_m: float,
    receiver_ground_elevation_m: float,
) -> list[Source]:
    """Convert an enclosure/semi-enclosure into radiating face sources.

    A diffuse-field energy balance is used inside the enclosure. Closed panel
    area contributes room-side absorption plus transmission loss; open area is
    an acoustic loss area of 1.0. External power from every face is then
    propagated independently with a smooth Lambertian directivity.
    """
    faces_cfg = getattr(source, "enclosure_faces", None) or {}
    geometry = _enclosure_face_geometry(source)
    alpha = _enclosure_absorption_alpha(source, band_hz)

    vent_area_requested = 0.0
    vent_face = str(getattr(source, "enclosure_vent_face", "back") or "back").lower()
    if (getattr(source, "noise_control_type", "") or "").lower() == "enclosure_silencer":
        vent_area_requested = max(float(getattr(source, "enclosure_vent_area_m2", 0.0) or 0.0), 0.0)
    if vent_face not in geometry:
        vent_face = "back"

    # Build effective loss area of the cavity and remember external transmission areas.
    path_data = {}
    loss_area = 0.0
    remaining_vent_area = vent_area_requested

    for face_name, geom in geometry.items():
        face = faces_cfg.get(face_name) or {}
        area = float(geom["area_m2"])
        open_fraction = _face_open_fraction(face)
        open_area = area * open_fraction
        panel_area = max(0.0, area - open_area)

        vent_area = 0.0
        if face_name == vent_face and remaining_vent_area > 0.0 and panel_area > 0.0:
            vent_area = min(panel_area, remaining_vent_area)
            panel_area -= vent_area
            remaining_vent_area -= vent_area

        tl = _face_tl_db(source, face_name, band_hz)
        tau_panel = 10.0 ** (-tl / 10.0)

        # Closed portion loses energy by internal lining absorption and by transmission.
        # An opening (including the vent inlet) removes incident diffuse-field energy
        # from the cavity. This keeps the energy balance bounded by the input power.
        panel_loss_coeff = min(1.0, alpha + tau_panel)
        loss_area += panel_area * panel_loss_coeff + open_area + vent_area

        external_area_tau = panel_area * tau_panel + open_area
        if vent_area > 0.0:
            il = _dict_band_value(getattr(source, "silencer_il_db", {}) or {}, band_hz)
            tau_silencer = 10.0 ** (-il / 10.0)
            external_area_tau += vent_area * tau_silencer

        path_data[face_name] = {
            "external_area_tau": external_area_tau,
            "geometry": geom,
        }

    loss_area = max(loss_area, 1e-9)
    receiver_abs_z = receiver_ground_elevation_m + float(receiver_height_m)
    virtual_sources = []

    for face_name, data in path_data.items():
        ratio = max(0.0, min(1.0, data["external_area_tau"] / loss_area))
        if ratio <= 1e-12:
            continue
        dc = _face_radiation_dc_db(
            data["geometry"],
            receiver_lat,
            receiver_lon,
            receiver_abs_z,
            source_ground_elevation_m,
        )
        if dc is None:
            continue

        face_lw = float(input_lw_db) + 10.0 * math.log10(max(ratio, 1e-12))
        virtual_sources.append(Source(
            name=f"{source.name} · {face_name}",
            lat=float(data["geometry"]["lat"]),
            lon=float(data["geometry"]["lon"]),
            height_m=float(data["geometry"]["height_m"]),
            lw_db=face_lw,
            dc_db=dc,
            enabled=source.enabled,
            ground_elevation_m=source_ground_elevation_m,
        ))

    return virtual_sources

FACE_LABELS = {'front':'Frente','back':'Fondo','left':'Izquierda','right':'Derecha','roof':'Techo','floor':'Piso'}
DEFAULT_TL = dict(zip(map(str,OCTAVE_BANDS), (10,15,20,25,30,35,35,35)))
DEFAULT_IL = dict(zip(map(str,OCTAVE_BANDS), (3,6,10,15,20,22,20,16)))
EXAMPLE_LW = dict(zip(map(str,OCTAVE_BANDS), (90,94,98,100,98,94,90,86)))


def default_treatment(kind='enclosure'):
    faces={name:{'state':'closed','opening_pct':25,'acoustic_mode':'rw','rw_db':30.0,'tl_db':dict(DEFAULT_TL)} for name in FACE_LABELS}
    if kind=='semi':
        faces['back']['state']='open'
    return {'noise_control_type':kind,'enclosure_length_m':2.0,'enclosure_width_m':2.0,
            'enclosure_height_m':2.5,'enclosure_azimuth_deg':0.0,'enclosure_rw_db':30.0,
            'enclosure_faces':faces,'enclosure_lining_mode':'medium',
            'enclosure_absorption_coeff':dict(ENCLOSURE_ABSORPTION_PRESETS['medium']),
            'enclosure_vent_area_m2':0.10,'enclosure_vent_face':'back',
            'silencer_il_db':dict(DEFAULT_IL),'control_reduction_db':{str(f):8.0 for f in OCTAVE_BANDS}}


def energy_sum(levels):
    values=[v for v in levels if v is not None and math.isfinite(v)]
    if not values: return None
    m=max(values)
    return m+10*math.log10(sum(10**((v-m)/10) for v in values))


def enclosure_balance(config, frequency):
    """Same diffuse-field loss/transmission areas as the map backend."""
    s=SimpleNamespace(lat=0.0,lon=0.0,height_m=1.5,**config)
    geom=_enclosure_face_geometry(s); alpha=_enclosure_absorption_alpha(s,frequency)
    loss=0.0; paths=[]
    for name,g in geom.items():
        face=config['enclosure_faces'][name]; area=g['area_m2']
        opened=area*_face_open_fraction(face); panel=area-opened
        vent=min(panel,config.get('enclosure_vent_area_m2',0.0)) if config['noise_control_type']=='enclosure_silencer' and name==config.get('enclosure_vent_face') else 0.0
        panel-=vent; tl=_face_tl_db(s,name,frequency); tau=10**(-tl/10)
        lost=panel*min(1.0,alpha+tau)+opened+vent
        external=panel*tau+opened+vent*10**(-_dict_band_value(config.get('silencer_il_db',{}),frequency)/10)
        loss+=lost
        paths.append({'Cara':FACE_LABELS[name],'Área [m²]':area,'Abierta [m²]':opened,'Ventilación [m²]':vent,'TL panel [dB]':tl,'Área de pérdidas [m²]':lost,'Área transmisora [m²]':external})
    external=sum(p['Área transmisora [m²]'] for p in paths)
    ratio=min(1.0,external/max(loss,1e-9))
    return paths, -10*math.log10(max(ratio,1e-12))


def treatment_results(config, lw=None, distance=20.0, bearing=0.0, receiver_height=1.5):
    """Propagate the same face emitters in an explicitly simplified free field."""
    lw=lw or EXAMPLE_LW
    lat,lon=xy_to_latlon(distance*math.sin(math.radians(bearing)),distance*math.cos(math.radians(bearing)),0,0)
    source=SimpleNamespace(name='F',lat=0.0,lon=0.0,height_m=1.5,enabled=True,**config)
    rows=[]
    for f in OCTAVE_BANDS:
        power=float(lw[str(f)]); kind=config['noise_control_type']
        d=math.sqrt(distance**2+(receiver_height-1.5)**2)
        original=power-geometric_divergence_db(d)
        if kind in ('enclosure','semi','enclosure_silencer'):
            emitters=_enclosure_virtual_sources(source,f,power,lat,lon,receiver_height,0.0,0.0)
            levels=[]
            for e in emitters:
                x,y=latlon_to_xy(lat,lon,e.lat,e.lon)
                r=math.sqrt(x*x+y*y+(receiver_height-e.height_m)**2)
                levels.append(e.lw_db+e.dc_db-geometric_divergence_db(r))
            controlled=energy_sum(levels)
            _,reduction=enclosure_balance(config,f)
        else:
            reduction=float(config['silencer_il_db'][str(f)] if kind=='silencer' else config['control_reduction_db'][str(f)])
            controlled=original-reduction
        rows.append({'Hz':f,'Lw original [dB]':power,'Reducción de potencia emitida [dB]':reduction,'Lp original [dB]':original,'Lp controlado [dB]':controlled,'ΔLp receptor [dB]':None if controlled is None else original-controlled})
    original_a=energy_sum([r['Lp original [dB]']+_a_weighting_correction_db(r['Hz']) for r in rows])
    controlled_a=energy_sum([r['Lp controlado [dB]']+_a_weighting_correction_db(r['Hz']) for r in rows if r['Lp controlado [dB]'] is not None])
    return rows,original_a,controlled_a


def barrier_results(height=3.0,length=20.0,source_to_barrier=5.0,distance=20.0,source_height=1.5,receiver_height=1.5):
    # F=(0,0), R=(0,d), screen transverse to the path. Same finite-screen motor.
    a=xy_to_latlon(-length/2,source_to_barrier,0,0); b=xy_to_latlon(length/2,source_to_barrier,0,0)
    barrier=Barrier('B',*a,*b,height_m=height)
    direct=math.hypot(distance,receiver_height-source_height)
    los=source_height+(receiver_height-source_height)*source_to_barrier/distance
    delta=math.hypot(source_to_barrier,height-source_height)+math.hypot(distance-source_to_barrier,height-receiver_height)-direct
    rows=[]
    for f in OCTAVE_BANDS:
        att=barrier_attenuation_db(0,0,source_height,0,distance,receiver_height,barrier,0,0,f,20.0,0.0)
        original=EXAMPLE_LW[str(f)]-geometric_divergence_db(direct)
        rows.append({'Hz':f,'Abar [dB]':att,'Lp original [dB]':original,'Lp controlado [dB]':original-att})
    before=energy_sum([r['Lp original [dB]']+_a_weighting_correction_db(r['Hz']) for r in rows])
    after=energy_sum([r['Lp controlado [dB]']+_a_weighting_correction_db(r['Hz']) for r in rows])
    return rows,before,after,los,delta
