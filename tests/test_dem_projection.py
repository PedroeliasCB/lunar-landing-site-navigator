"""Projection tests for the LOLA south polar stereographic grid (no download needed)."""
import numpy as np

from backend.lola_dem import PolarDEM


def make(n=7600, scale=80.0):
    d = PolarDEM.__new__(PolarDEM)
    d.lines = d.samples = n
    d.scale_m, d.radius_m, d.k_m = scale, 1737400.0, 0.5
    d.loff = d.soff = n / 2 - 0.5        # matches LINE/SAMPLE_PROJECTION_OFFSET = 3799.5
    return d


def test_pole_is_grid_centre():
    d = make()
    r, c = d.xy_to_rowcol(*d.latlon_to_xy_m(-90.0, 0.0))
    assert abs(r - 3799.5) < 1e-9 and abs(c - 3799.5) < 1e-9


def test_orientation_lon0_up_lon90_right():
    d = make()
    r0, c0 = d.xy_to_rowcol(*d.latlon_to_xy_m(-85.0, 0.0))
    r90, c90 = d.xy_to_rowcol(*d.latlon_to_xy_m(-85.0, 90.0))
    assert r0 < 3799.5 and abs(c0 - 3799.5) < 1e-6      # lon 0 is up
    assert c90 > 3799.5 and abs(r90 - 3799.5) < 1e-6    # lon 90 E is right


def test_80S_edge_near_grid_edge():
    d = make()
    x, y = d.latlon_to_xy_m(-80.0, 90.0)
    _, c = d.xy_to_rowcol(x, y)
    assert 7550 < c < 7600   # 80 S lies at the edge of the 7600 px grid


def test_round_trip():
    d = make()
    lat, lon = np.array([-86.0, -89.53432, -80.13]), np.array([356.6, 209.94767, 1.44])
    lat2, lon2 = d.xy_m_to_latlon(*d.latlon_to_xy_m(lat, lon))
    assert np.allclose(lat, lat2) and np.allclose(lon, lon2)
