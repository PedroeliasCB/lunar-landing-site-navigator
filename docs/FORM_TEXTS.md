# FORM TEXTS - final texts for the submission form (draft by Pedro + Claude, Nov 15 12:50 BOT; Julio reviews)

Field rules: `../FORM/SUBMISSION_FORM_FIELDS.md`. Judging criteria: `../FORM/JUDGING_CRITERIA.md`. Numbers below come from `METRICS_TABLE.md` (pipeline run 2026-11-15 15:57 UTC).

## Project Name
LunaSight: Lunar Landing Site Navigator

## Summary (50-200 words, max 1500 characters)
LunaSight answers the first two questions of any lunar landing: will the lander get sunlight for power, and can it talk directly to Earth? For any curated site and date, it computes where the Sun and Earth sit relative to the real terrain horizon, built from NASA LRO LOLA elevation models (20 m and 80 m per pixel, rays to 150 km, Moon curvature included, no atmospheric refraction), with Sun and Earth positions from JPL Horizons every 10 minutes. Planners compare up to four site and date scenarios side by side: a 360 degree horizon panorama with the Sun and Earth discs, sunlight and Earth-in-view percentages, countdowns to sunset and Earthset, longest night, blackout periods, and a GO / MARGINAL / NO-GO verdict from visible thresholds. A timeline shows when each site is lit and in contact. Small moves matter: on the Malapert Massif, a point on the south-facing slope sees Earth 0 % of a 30-day window, while the summit 2.5 km away sees it 100 % of the time and doubles its sunlight. A Learn mode explains each number; an Evidence panel lists sources, conventions and validation checks.

Character count: 1096 characters, 190 words.

## Project Details
- **What it does / how it works:** A Python pipeline downloads Sun and Earth observer tables from JPL Horizons for each site (lunar mean-Earth frame, airless apparent azimuth and elevation, 60 days at 10 min) and computes the terrain skyline H(az) from LOLA polar DEMs (LDEM_85S_20M near field, LDEM_80S_80M far field; 720 azimuths; rays to 150 km; curvature drop d^2/2R). A body is up when its elevation is above the skyline (centre of disc for the headline, any part also shown). The pipeline writes one JSON file per site; a static web app (GitHub Pages) shows panoramas, metrics, windows and timelines, and lets the user change mast height (0, 2, 5, 10 m), disc convention, Earth link threshold and date slip.
- **Benefits and intended impact:** Mission planners, students and the public can test a landing site and date in seconds and see why it works or fails. Every metric maps to hardware: the longest night sizes the battery, Earth-in-view decides direct radio versus relay.
- **Tools, languages, hardware/software:** Python 3 (numpy, pandas, requests, pytest), HTML, CSS and JavaScript without frameworks, IBM Plex fonts, Git and GitHub Pages. AI assistance: Claude (Anthropic) for code, under human direction and review.
- **What is creative:** The horizon panorama draws the real LOLA skyline with the Sun and Earth at true angular size and their paths over the window (Earth libration visible). The change explainer turns deltas into causes: it names the azimuth, angle and distance of the ridge that hides the Sun. Presets show the core value in one click: "Move 2.5 km: Malapert slope vs summit", "Slip a landing by 14 days", "Apollo 11 vs south pole ridge".
- **Factors the team considered:** No atmospheric refraction (horizon = terrain plus the edge of the lunar sphere); elevated ridges see the horizon below 0 deg; disc convention (centre vs any part); 2 m lander mast; Earth libration; date slips; validation against LROC QuickMap heights, Horizons raw tables, the smooth-sphere Sun elevation bound and Apollo 11 (Earth 100 %). Known gap: no comparison yet with the PGDA 69 long-term visibility maps.

## NASA data used (Link Text / Link URL)
- JPL Horizons System / https://ssd.jpl.nasa.gov/horizons/
- LRO LOLA polar gridded DEMs (PDS Geosciences Node) / https://pds-geosciences.wustl.edu/missions/lro/lola.htm
- LROC QuickMap (validation) / https://quickmap.lroc.im-ldi.com/

## Links
- Repository: https://github.com/PedroeliasCB/lunar-landing-site-navigator
- Live app: https://pedroeliascb.github.io/lunar-landing-site-navigator/

## 30-second pitch script
| Seconds | On screen | Voice / caption |
|---|---|---|
| 0-5 | Compare view, Malapert slope card showing Earth 0 % | "A lander that cannot see the Sun has no power. One that cannot see Earth cannot call home." |
| 5-15 | Panorama with the LOLA skyline, Sun and Earth discs; press Play | "LunaSight puts NASA's Horizons ephemeris on top of the real LOLA terrain horizon for any site and date." |
| 15-25 | Preset "Move 2.5 km: Malapert slope vs summit" | "Move 2.5 km on Malapert: Earth goes from 0 to 100 % and sunlight doubles." |
| 25-30 | Timeline and the GO chip | "Compare sites and dates in seconds, with every number traced to NASA data." |
