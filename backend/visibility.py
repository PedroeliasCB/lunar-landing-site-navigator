"""Visibility, events, windows and metrics (RESOURCE/BUILD/ALGORITHMS/DS3, decisions D1, D2, D6, D8).

E10 rho = asin(R_body / distance)              angular radius
E11 f = (acos(u) - u sqrt(1-u^2)) / pi, u = (H - e)/rho   lit fraction of the disc above the skyline
E13 horizontal panel factor = max(0, sin e);  E14 vertical panel facing the Sun azimuth = cos e
E19 S = S0 / r_AU^2
Up test (E-up): centre convention e > H(az) + thr ; any-part convention e + rho > H(az) + thr.
"""
from __future__ import annotations

import numpy as np

from backend.constants import R_SUN_KM, R_EARTH_KM, AU_KM, S0_W_M2, N_AZ


def skyline_at(H_deg, az_deg):
    """Linear interpolation of H on the circular 0.5 deg grid."""
    step = 360.0 / len(H_deg)
    x = (np.asarray(az_deg) % 360.0) / step
    i0 = np.floor(x).astype(int) % len(H_deg)
    i1 = (i0 + 1) % len(H_deg)
    f = x - np.floor(x)
    return H_deg[i0] * (1 - f) + H_deg[i1] * f


def angular_radius_deg(body, dist_km):
    r = R_SUN_KM if body == "sun" else R_EARTH_KM
    return np.degrees(np.arcsin(r / np.asarray(dist_km)))                    # E10


def lit_fraction(e_deg, H_deg, rho_deg):
    u = np.clip((np.asarray(H_deg) - np.asarray(e_deg)) / np.asarray(rho_deg), -1.0, 1.0)
    return (np.arccos(u) - u * np.sqrt(1 - u * u)) / np.pi                   # E11


def margin(el, az, H_deg, rho, convention="centre", thr_deg=0.0):
    """Signed clearance (deg) of the body above the skyline for the convention."""
    base = el - skyline_at(H_deg, az) - thr_deg
    return base + rho if convention == "any" else base


def runs(flag):
    """Run-length encoding: list of (start_idx, end_idx_exclusive, value)."""
    flag = np.asarray(flag, bool)
    if flag.size == 0:
        return []
    change = np.flatnonzero(np.diff(flag.astype(int))) + 1
    starts = np.concatenate([[0], change])
    ends = np.concatenate([change, [flag.size]])
    return [(int(s), int(e), bool(flag[s])) for s, e in zip(starts, ends)]


def crossings(t_h, m):
    """Times (h) where margin m changes sign, interpolated within the step (D8)."""
    out = []
    for i in np.flatnonzero(np.sign(m[:-1]) != np.sign(m[1:])):
        if m[i] == m[i + 1]:
            continue
        f = m[i] / (m[i] - m[i + 1])
        out.append((float(t_h[i] + f * (t_h[i + 1] - t_h[i])), "rise" if m[i + 1] > m[i] else "set"))
    return out


def windows(t_h, up, step_h):
    """Up windows as (start_h, end_h, hours); each sample covers [t, t+step)."""
    return [(t_h[s], t_h[e - 1] + step_h, (e - s) * step_h) for s, e, v in runs(up) if v]


def longest_false_h(up, step_h):
    r = [(e - s) * step_h for s, e, v in runs(up) if not v]
    return max(r) if r else 0.0


def metrics(sun_up, earth_up, sun_el, step_h):
    sun_up, earth_up = np.asarray(sun_up, bool), np.asarray(earth_up, bool)
    neither = ~sun_up & ~earth_up
    blk = [(e - s) * step_h for s, e, v in runs(neither) if v]
    return {
        "sunlight_pct": round(100.0 * sun_up.mean(), 2),
        "longest_night_h": round(longest_false_h(sun_up, step_h), 2),
        "earth_pct": round(100.0 * earth_up.mean(), 2),
        "longest_no_earth_h": round(longest_false_h(earth_up, step_h), 2),
        "both_pct": round(100.0 * (sun_up & earth_up).mean(), 2),
        "blackout_longest_h": round(max(blk) if blk else 0.0, 2),
        "max_sun_el_deg": round(float(np.max(sun_el)), 4),
    }


def solar_flux(dist_au):
    return S0_W_M2 / np.asarray(dist_au) ** 2                                # E19
