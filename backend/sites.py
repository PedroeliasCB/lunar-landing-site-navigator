"""Curated landing sites, copied from RESOURCE/RESEARCH/SITE_CATALOG.md (Nov 15, 00:29 UTC).

Frame: planetocentric latitude, east-positive longitude, lunar ME (DE421).
Canonical longitude in code: 0-360 deg East (lon_e_deg). Status: OFFICIAL / SECONDARY / TEAM.
TEAM points are "selected by max illumination inside the region" (catalog rule 2).
South polar sites use LOLA terrain; Apollo 11 (near side) uses the smooth-sphere horizon (validation: Earth always up).
"""

SITES = [
    {"id": "malapert", "name": "Malapert Massif", "lat_deg": -86.0, "lon_e_deg": 356.6,
     "status": "TEAM", "source": "Team prototype max-illumination point", "group": "artemis_region"},
    {"id": "haworth", "name": "Haworth", "lat_deg": -86.6, "lon_e_deg": 355.7,
     "status": "TEAM", "source": "Team prototype max-illumination point", "group": "artemis_region"},
    {"id": "nobile_rim_1", "name": "Nobile Rim 1", "lat_deg": -85.2, "lon_e_deg": 52.0,
     "status": "TEAM", "source": "Team prototype max-illumination point", "group": "artemis_region"},
    {"id": "de_gerlache_rim_2", "name": "de Gerlache Rim 2", "lat_deg": -88.3, "lon_e_deg": 253.2,
     "status": "TEAM", "source": "Team prototype max-illumination point", "group": "artemis_region"},
    {"id": "mons_mouton", "name": "Mons Mouton (IM-2 intended)", "lat_deg": -84.78, "lon_e_deg": 29.13,
     "status": "OFFICIAL", "source": "LROC post 1401", "group": "artemis_region"},
    {"id": "connecting_ridge", "name": "Connecting Ridge", "lat_deg": -89.53432, "lon_e_deg": 209.94767,
     "status": "OFFICIAL", "source": "LPSC 2024 abstract 1695", "group": "artemis_2022"},
    {"id": "peak_near_shackleton", "name": "Peak Near Shackleton", "lat_deg": -89.01701, "lon_e_deg": 126.27302,
     "status": "OFFICIAL", "source": "LPSC 2024 abstract 1695", "group": "artemis_2022"},
    {"id": "apollo_11", "name": "Apollo 11 (Tranquility Base)", "lat_deg": 0.67416, "lon_e_deg": 23.47314,
     "status": "OFFICIAL", "source": "NSSDC lunar_sites (Wagner et al. 2017); LROC featured site 51", "group": "apollo"},
    {"id": "im1_odysseus", "name": "IM-1 Odysseus (Malapert A)", "lat_deg": -80.13, "lon_e_deg": 1.44,
     "status": "OFFICIAL", "source": "LEAG 2024 abstract 5037", "group": "clps_flown"},
]


def to_lon_180(lon_e_deg: float) -> float:
    """Convert 0-360 E to -180..180 E (only for display)."""
    return ((lon_e_deg + 180.0) % 360.0) - 180.0
