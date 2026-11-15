"""Parser test on a table with the documented Horizons CSV layout."""
from backend.horizons import parse_observer_table, AU_KM

SAMPLE = """header text
 Date__(UT)__HR:MN, , , Azi_(a-app), Elev_(a-app),             delta,     deldot,
$$SOE
 2027-Jan-01 00:00, , ,  10.000000,  1.250000,  0.98330000000000,  0.0123456,
 2027-Jan-01 01:00, , ,  10.500000, -0.250000,  0.98330100000000, -0.0123456,
$$EOE
footer
"""


def test_parse_values_and_units():
    df = parse_observer_table(SAMPLE)
    assert len(df) == 2
    assert df.azimuth_deg.tolist() == [10.0, 10.5]
    assert df.elevation_deg.tolist() == [1.25, -0.25]
    assert abs(df.range_km[0] - 0.9833 * AU_KM) < 1e-3
    assert df.elevation_deg.between(-90, 90).all()
    assert df.azimuth_deg.between(0, 360).all()
