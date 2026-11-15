"""Terrain skyline H(az) from LOLA polar DEMs (RESOURCE/BUILD/ALGORITHMS/DS2 with REVIEW fixes).

E06  h_c(d)  = d^2 / (2 R)                                  curvature drop
E07  theta   = atan2(h_dem - h_site - h_obs - h_c, d)      obstruction angle
E08  H(az)   = max_d theta(d)                               skyline
E09  dip     = -acos(R / (R + h_obs))                       smooth-sphere horizon (used only where no DEM covers a ray)
Rays: great circles from the site (destination-point formula, DS2 section 3), az 0 = north, clockwise.
At a site exactly at the pole, rays are meridians: lon = az (REVIEW fix).
Sampling (DS2 section 5): 20 m steps to 20 km, then step = min(0.002 d, 400 m) to R_max = 150 km (D4).
DEM mosaic: LDEM_85S_20M where available, else LDEM_80S_80M; samples outside both are ignored.
No atmospheric refraction (C3).
"""
from __future__ import annotations

import numpy as np

from backend.constants import R_MOON_M, R_MAX_M, N_AZ

AZ_DEG = np.arange(N_AZ) * (360.0 / N_AZ)


def ray_distances_m(r_max_m: float = R_MAX_M) -> np.ndarray:
    near = np.arange(20.0, 20_000.0 + 1e-6, 20.0)
    far = [20_000.0]
    while far[-1] < r_max_m:
        far.append(far[-1] + min(0.002 * far[-1], 400.0))
    return np.concatenate([near, np.array(far[1:])])


def destination(lat0_deg, lon0_deg, az_deg, d_m):
    """Great-circle destination (rad math, deg in/out). Broadcasts az x d."""
    phi0, lam0 = np.radians(lat0_deg), np.radians(lon0_deg)
    a = np.radians(np.asarray(az_deg))[:, None]
    delta = np.asarray(d_m)[None, :] / R_MOON_M
    if abs(abs(lat0_deg) - 90.0) < 1e-9:  # pole: rays are meridians (REVIEW fix)
        lat = np.degrees(np.sign(lat0_deg) * (np.pi / 2 - delta)) * np.ones_like(a)
        lon = np.degrees(a) * np.ones_like(delta)
        return lat, lon % 360.0
    sin_phi = np.sin(phi0) * np.cos(delta) + np.cos(phi0) * np.sin(delta) * np.cos(a)
    phi = np.arcsin(np.clip(sin_phi, -1, 1))
    lam = lam0 + np.arctan2(np.sin(a) * np.sin(delta) * np.cos(phi0), np.cos(delta) - np.sin(phi0) * sin_phi)
    return np.degrees(phi), np.degrees(lam) % 360.0


def smooth_sphere_dip_deg(mast_m: float) -> float:
    """E09."""
    return -np.degrees(np.arccos(R_MOON_M / (R_MOON_M + mast_m)))


def terrain_profile(dems, lat0, lon0, az_deg=AZ_DEG, d_m=None):
    """Heights (m above the 1737.4 km sphere) along every ray; dems = [finest, ..., coarsest]."""
    d_m = ray_distances_m() if d_m is None else d_m
    lat, lon = destination(lat0, lon0, az_deg, d_m)
    h = np.full(lat.shape, np.nan)
    for dem in dems:  # finest first, fill only where still missing
        miss = np.isnan(h)
        if not miss.any():
            break
        vals = dem.height_at(lat[miss], lon[miss])
        h[miss] = vals
    return d_m, h


def site_height(dems, lat0, lon0) -> tuple[float, str]:
    for dem, name in dems:
        v = float(dem.height_at(lat0, lon0)[0])
        if v == v:
            return v, name
    return float("nan"), "smooth_sphere"


def skyline_from_profile(d_m, h, h_site_m, mast_m):
    """E06-E08. Returns H_deg[az], dist_km[az] of the blocking point, coverage fraction."""
    hc = d_m ** 2 / (2.0 * R_MOON_M)                          # E06
    theta = np.arctan2(h - h_site_m - mast_m - hc[None, :], d_m[None, :])  # E07
    theta = np.where(np.isnan(theta), -np.inf, theta)
    idx = np.argmax(theta, axis=1)
    H = np.degrees(theta[np.arange(theta.shape[0]), idx])     # E08
    # Elevated sites see the horizon BELOW 0 deg (terrain falls away); do not clamp to the flat-ground dip.
    # Only rays with no DEM samples at all fall back to the smooth-sphere dip (E09).
    H = np.where(np.isfinite(H), H, smooth_sphere_dip_deg(mast_m))
    dist_km = d_m[idx] / 1000.0
    coverage = float(np.mean(~np.isnan(h)))
    return H, dist_km, coverage
