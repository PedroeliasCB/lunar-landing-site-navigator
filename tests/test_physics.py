"""Physics tests with oracle values from RESOURCE/SCIENCE/WORKED_NUMBERS.md and DS1-DS3."""
import numpy as np

from backend import skyline as sk, visibility as vis
from backend.constants import R_MOON_M


def test_curvature_drop_E06():
    for d_km, hc in [(1, 0.3), (10, 28.8), (100, 2877.9), (200, 11511.5)]:
        assert abs((d_km * 1000) ** 2 / (2 * R_MOON_M) - hc) < 0.1


def test_smooth_sphere_dip_E09():
    for mast, dip in [(1, -0.061), (2, -0.087), (5, -0.137), (10, -0.194)]:
        assert abs(sk.smooth_sphere_dip_deg(mast) - dip) < 0.001


def test_destination_DS2():
    lat, lon = sk.destination(-89.0, 0.0, [90.0], [100_000.0])
    assert abs(lat[0, 0] - (-86.56)) < 0.01 and abs(lon[0, 0] - 73.2) < 0.1
    lat, lon = sk.destination(-90.0, 0.0, [37.0], [100_000.0])   # pole special case
    assert abs(lat[0, 0] - (-86.7020)) < 1e-3 and abs(lon[0, 0] - 37.0) < 1e-9


def test_flat_terrain_gives_sphere_dip():
    d = sk.ray_distances_m()
    h = np.zeros((4, d.size))  # perfectly spherical Moon
    H, dist, cov = sk.skyline_from_profile(d, h, 0.0, 2.0)
    assert np.allclose(H, sk.smooth_sphere_dip_deg(2.0), atol=0.01) and cov == 1.0


def test_angular_radius_E10():
    assert abs(vis.angular_radius_deg("sun", 149_597_870.7) - 0.2665) < 1e-3
    assert abs(vis.angular_radius_deg("earth", 384_400) - 0.951) < 1e-3


def test_lit_fraction_E11():
    assert abs(vis.lit_fraction(0.0, 0.0, 0.2665) - 0.5) < 1e-12   # skyline through the centre
    assert vis.lit_fraction(1.0, 0.0, 0.2665) == 1.0                # fully above
    assert vis.lit_fraction(-1.0, 0.0, 0.2665) == 0.0               # fully below
    # skyline half a radius above the centre: segment area ratio (acos(.5) - .5*sqrt(.75))/pi = 0.1955
    assert abs(vis.lit_fraction(0.0, 0.5 * 0.2665, 0.2665) - 0.19550) < 1e-4


def test_events_and_metrics():
    t = np.arange(0, 48, 1.0)
    m = np.sin(2 * np.pi * t / 24) + 0.0001
    ev = vis.crossings(t, m)
    assert ev[0][1] == "set" and abs(ev[0][0] - 12.0) < 0.05
    up = m > 0
    met = vis.metrics(up, np.ones_like(up), m, 1.0)
    assert 45 < met["sunlight_pct"] < 55 and met["earth_pct"] == 100.0 and met["blackout_longest_h"] == 0.0


def test_flux_E19():
    assert abs(vis.solar_flux(0.98329) - 1407) < 1 and abs(vis.solar_flux(1.01671) - 1316) < 1


def test_elevated_site_sees_below_zero():
    """A site 1 km above a spherical surrounding sees the geometric dip acos(R/(R+1000)) ~ -1.94 deg, not -0.087."""
    d = sk.ray_distances_m()
    h = np.zeros((2, d.size))
    H, _, _ = sk.skyline_from_profile(d, h, 1000.0, 0.0)   # site 1 km above its spherical surroundings
    expect = -np.degrees(np.arccos(R_MOON_M / (R_MOON_M + 1000.0)))
    assert np.allclose(H, expect, atol=0.02)
