# Lunar Landing Site Navigator

NASA Space Apps Challenge 2026 - challenge "Lunar Landing Site Navigator".
Team: Julio Gonzales (science and direction), Pedro Elias Chavez Burgos (code), Aaron Delgado (assets, demo, submission).

The app computes, for candidate lunar south pole landing sites, when the Sun (power) and the Earth (direct communication)
are above the real terrain horizon, using JPL Horizons ephemerides and LRO LOLA elevation models.

## Structure
| Path | Content |
|---|---|
| `backend/` | Python data pipeline (Horizons client, DEM horizon, metrics) |
| `data/processed/` | Small cached results used by the app (< 2 MB each) |
| `data/raw/` | Raw downloads (ignored by git) |
| `tests/` | Unit tests (`pytest`) |
| `AI_USAGE_LOG.md` | Every use of AI and what a human verified |

## Run
```bash
pip install -r requirements-nasa.txt
python -m backend.p2_horizons_test   # Horizons smoke test (P2)
python -m pytest tests
```

## NASA data
- JPL Horizons observer tables (DE441), https://ssd.jpl.nasa.gov/horizons/
- LRO LOLA polar DEMs (LDEM_80S_80M, LDEM_85S_20M), PDS Geosciences Node

## Horizons request parameters
`COMMAND` 10 (Sun) or 399 (Earth), `EPHEM_TYPE=OBSERVER`, `CENTER=coord@301`, `COORD_TYPE=GEODETIC`,
`SITE_COORD=lon_E,lat,alt_km`, `QUANTITIES=4,20`, `CSV_FORMAT=YES`. Apparent az/el, airless (no refraction).

## License
MIT
