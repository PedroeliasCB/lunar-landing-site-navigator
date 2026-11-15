# METRICS TABLE - pipeline results per site

Window: 2027-03-01T00:00Z + 30 days · Step: 10 min · Disc convention: centre (D1 headline) · Earth threshold: 0 deg above skyline (D2) · Mast: 2 m (D3) · Ephemeris: JPL Horizons precomputed (D5) · DEM: LDEM_85S_20M + LDEM_80S_80M, 150 km, 720 azimuths (D4) · Generated 2026-11-15T15:57Z

| Site | Status | Terrain | Sunlight % | Longest night (h) | Earth-in-view % | Longest no-signal (h) | Both up % | Longest blackout (h) | Max Sun elev (deg) |
|---|---|---|---|---|---|---|---|---|---|
| Malapert Massif | TEAM | LDEM_85S_20M | 31.57 | 373.5 | 0.0 | 720.0 | 0.0 | 373.5 | 2.909 |
| Malapert summit (LOLA high point) | TEAM | LDEM_85S_20M | 64.86 | 242.83 | 100.0 | 0.0 | 64.86 | 0.0 | 2.949 |
| Haworth | TEAM | LDEM_85S_20M | 0.0 | 720.0 | 0.0 | 720.0 | 0.0 | 720.0 | 2.308 |
| Nobile Rim 1 | TEAM | LDEM_85S_20M | 30.37 | 295.67 | 16.27 | 369.33 | 16.27 | 295.67 | 3.849 |
| de Gerlache Rim 2 | TEAM | LDEM_85S_20M | 0.0 | 720.0 | 39.54 | 297.0 | 0.0 | 297.0 | 1.113 |
| Mons Mouton (IM-2 intended) | OFFICIAL | LDEM_85S_20M | 36.81 | 328.83 | 81.53 | 121.83 | 29.31 | 67.83 | 4.21 |
| Connecting Ridge | OFFICIAL | LDEM_85S_20M | 41.9 | 328.83 | 42.59 | 278.0 | 32.22 | 278.0 | -0.181 |
| Peak Near Shackleton | OFFICIAL | LDEM_85S_20M | 3.01 | 604.33 | 39.98 | 289.5 | 0.0 | 289.5 | 0.199 |
| Apollo 11 (Tranquility Base) | OFFICIAL | smooth_sphere | 49.38 | 299.0 | 100.0 | 0.0 | 49.38 | 0.0 | 89.647 |
| IM-1 Odysseus (Malapert A) | OFFICIAL | LDEM_80S_80M | 36.34 | 406.33 | 100.0 | 0.0 | 36.34 | 0.0 | 8.789 |

## Validation

| Site | Check | Ours | Reference | Difference | Source / note |
|---|---|---|---|---|---|
| Malapert Massif | Max Sun elevation above the flat horizon in window (deg) | 2.909 | 5.54 | -2.63 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Malapert summit (LOLA high point) | Max Sun elevation above the flat horizon in window (deg) | 2.949 | 5.58 | -2.63 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Haworth | Max Sun elevation above the flat horizon in window (deg) | 2.308 | 4.94 | -2.63 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Nobile Rim 1 | Max Sun elevation above the flat horizon in window (deg) | 3.849 | 6.34 | -2.49 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| de Gerlache Rim 2 | Max Sun elevation above the flat horizon in window (deg) | 1.113 | 3.24 | -2.13 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Mons Mouton (IM-2 intended) | Max Sun elevation above the flat horizon in window (deg) | 4.21 | 6.76 | -2.55 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Connecting Ridge | Max Sun elevation above the flat horizon in window (deg) | -0.181 | 2.01 | -2.19 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Peak Near Shackleton | Max Sun elevation above the flat horizon in window (deg) | 0.199 | 2.53 | -2.33 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Apollo 11 (Tranquility Base) | Earth in view (%) | 100.0 | 100.0 | 0.0 | VALIDATION_TARGETS: near-side site always sees Earth. pass if 100 |
| IM-1 Odysseus (Malapert A) | Max Sun elevation above the flat horizon in window (deg) | 8.789 | 11.41 | -2.62 | E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3). must not exceed the bound; a 30-day window sits below the annual maximum |
| Malapert Massif | Terrain height (m) | 4690.3 | 4689.63 | 0.67 | LROC QuickMap Inspect TerrainHeight (2 m/px). P3, < 1 m |
| Test site 86 S 357.5 E | Horizons table parse (rows, az/el) | 25/25 identical | raw Horizons text | 0 | P2 smoke test. pass |
| Polar sites | Sun / Earth visibility vs PGDA 69 long-term maps | GAP | PGDA 69 AVGVISIB | None | Mazarico et al. 2011. not compared yet: PGDA 69 is an 18.6-year average, our window is 30 days |
