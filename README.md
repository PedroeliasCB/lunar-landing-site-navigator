# Lunar Landing Site Navigator

NASA Space Apps Challenge 2026, challenge "Lunar Landing Site Navigator".
Team: Julio Gonzales (science and direction), Pedro Elias Chavez Burgos (code), Aaron Delgado (assets, demo, submission).

**Live app:** https://pedroeliascb.github.io/lunar-landing-site-navigator/

The app answers one question for a lunar landing site and date: *can a lander get power and talk to Earth here?*
It compares up to 4 scenarios (site + date) using the Sun and Earth positions from JPL Horizons and the real terrain
horizon computed from LRO LOLA elevation models, with no atmospheric refraction.

## What it shows
- **Horizon panorama** per scenario: 360 deg LOLA skyline with the Sun and Earth discs at true angular size, and their paths over the window (Earth libration).
- **Four key numbers**: Sun elevation and clearance above the terrain, countdown to sunset / Earthset (or next rise), sunlight % and Earth-in-view % over 30 days.
- **Verdict** GO / MARGINAL / NO-GO from planner thresholds that stay visible and editable.
- **Details**: longest night, longest no-Earth gap, blackout (no Sun and no Earth), panel factors (horizontal / vertical / tracking), solar flux, light time, window table, and a change explainer that names the ridge that blocks the Sun.
- **Timeline**: Gantt bars of Sun-up, Earth-up and blackout for every scenario, with a shared time scrubber and play.
- **Plan**: curated sites with status and source, date slip (+/- days), presets ("Artemis regions tour", "Slip a landing by 14 days", "Apollo 11 vs south pole ridge").
- **Learn mode**: one plain sentence per metric. **Evidence drawer**: sources, conventions and the validation table.

## How it works
```
JPL Horizons (observer tables, lunar site, airless)  -> Sun / Earth az, el, distance every 10 min, 60 days
LOLA LDEM_85S_20M + LDEM_80S_80M (PDS)               -> skyline H(az): 720 azimuths, rays to 150 km, curvature d^2/2R
backend/build_site_data.py                           -> docs/data/sites/<id>.json (+ index.json, validation.json)
docs/ (static HTML + JS, GitHub Pages)               -> applies the same visibility rules to the user's settings
```
Science decisions (team, Nov 14 2026): D1 centre-of-disc headline (any-part also shown), D2 0 deg above skyline (slider),
D3 2 m mast (0/2/5/10 m), D4 150 km and 720 bins, D5 precomputed Horizons, D6 relative power and longest night,
D7 30 days at 10 min, D8 interpolated crossings, D9 validation table.

Equations (team cheatsheet): E06 curvature drop, E07 obstruction angle, E08 skyline max, E09 smooth-sphere dip,
E10 angular radius, E11 lit fraction of the disc, E13/E14 panel factors, E19 solar flux.

## Validation
See `docs/METRICS_TABLE.md` (generated) and the Evidence drawer in the app:
- LOLA site height at Malapert 4690.3 m vs LROC QuickMap 4689.63 m (< 1 m).
- Horizons parsing: 25/25 rows identical to the raw table (P2).
- Physics unit tests with the team's worked numbers (`tests/test_physics.py`): curvature, dip, destination point, lit fraction, flux.
- Max Sun elevation at every polar site stays below the smooth-sphere bound 90 - |lat| + 1.54 deg.
- Apollo 11 (near side) sees Earth 100 % of the time.
- Browser metrics equal the pipeline metrics (same rounding, checked in Node).
- Not done yet (GAP): comparison with the PGDA 69 long-term visibility maps.

## Run it yourself
```bash
pip install numpy pandas requests pytest
python -m backend.p3_dem_check          # downloads the LOLA DEMs (575 MB) and checks site heights
python -m backend.build_site_data       # Horizons + skylines -> docs/data
python -m backend.metrics_table         # writes docs/METRICS_TABLE.md
python -m pytest tests
python -m http.server -d docs 8000      # open http://localhost:8000
```

## NASA data
- JPL Horizons System, https://ssd.jpl.nasa.gov/horizons/
- LRO LOLA polar gridded DEMs (LRO-L-LOLA-4-GDR-V1.0), PDS Geosciences Node, https://pds-geosciences.wustl.edu/missions/lro/lola.htm
- LROC QuickMap (validation), https://quickmap.lroc.im-ldi.com/

## Tools
Python 3 (numpy, pandas, requests, pytest), HTML/CSS/JavaScript (no framework), IBM Plex fonts (SIL OFL), GitHub Pages.
AI assistance: Claude (Anthropic) for code under human direction; see `AI_USAGE_LOG.md`.

Not affiliated with or endorsed by NASA. License: MIT.
