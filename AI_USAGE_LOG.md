# AI Usage Log - NASA Space Apps Challenge 2026

Rules: RESOURCE/FORM/SI_RULES.md. Every AI use: tool, what it produced, what a human verified.

| Timestamp (BOT) | Tool | What the AI did | What a human verified |
| :--- | :--- | :--- | :--- |
| 2026-11-14 16:00 | Claude (Anthropic) | Compiled the inventory of 39 NASA API endpoints (nasa_apis.csv) | Pedro: pending live test of each endpoint |
| 2026-11-14 20:00 | Claude (Anthropic) | Installed the team AI kit for Claude Code (skills, hooks, MCP config) | Pedro: checked /mcp shows the 4 servers connected |
| 2026-11-14 21:00 | Claude (Anthropic) | Wrote the Horizons client, P2 smoke test and parser unit test | Pedro: ran P2 (2027-01-01, 1 h, 357.5E -86.0); 25/25 rows parsed for Sun and Earth; first-row az/el identical to raw table; ranges plausible (Sun 0.98270 AU = 147.0e6 km, Earth 391,604 km) |
| 2026-11-14 21:10 | Claude (Anthropic) | Wrote LOLA DEM reader (download, label parse, south polar stereographic projection, bilinear sampling), site list from SITE_CATALOG, P3 check script and projection tests | Pedro ran P3: label SCALING_FACTOR 0.5 m/DN confirmed; Malapert (86.0 S, 356.6 E) = 4690.5 m (LDEM_80S_80M), 4690.3 m (LDEM_85S_20M) vs LROC QuickMap TerrainHeight 4689.630 m (2 m/px terrain, slope 17.272 deg); difference < 1 m |
| 2026-11-14 21:15 | Claude (Anthropic) | Wrote P4 precompute script (Horizons Sun/Earth per site, 30-day chunks, site altitude from LOLA DEM) | Pedro: pending, run after Gate 1 sets window and step |
| 2026-11-15 12:00 | Claude (Anthropic) | Read RESOURCE/BUILD (START_HERE, FEATURES, DESIGN_DIRECTION, DATA_CONTRACT, ALGORITHMS DS1-DS3 + REVIEW) and wrote the engine: skyline from LOLA (E06-E09, DS2 with REVIEW fixes), visibility/events/metrics (E10, E11, E19, DS3), physics tests | Pedro: tests pass with WORKED_NUMBERS oracles (curvature, dip -0.087 deg at 2 m, destination 86.56 S 73.2 E, flux 1407/1316 W/m2) |
| 2026-11-15 12:30 | Claude (Anthropic) | Wrote backend/build_site_data.py (Horizons 60 d at 10 min + skylines for 0/2/5/10 m masts -> docs/data JSON) and the static web app (docs/: Plan, Compare, Timeline, Evidence, Learn) | Pedro: pending, run pipeline and review numbers; browser metrics checked equal to pipeline metrics in Node |
| 2026-11-15 12:45 | Claude (Anthropic) | Found and fixed a skyline bug (horizon was clamped to the flat-ground dip, so elevated ridges could not see a grazing Sun); added a test for an elevated site; added Malapert summit (highest 20 m LOLA pixel within 8 km of the TEAM point) and the "Move 2.5 km" preset | Pedro: re-ran the pipeline; Connecting Ridge sunlight 0 % -> 41.9 % with Sun max -0.18 deg above the flat horizon (ridge 1.65 km above surroundings), consistent with physics |
| 2026-11-15 12:50 | Claude (Anthropic) | Reviewed the deployed site in Chrome (Compare, Timeline, Plan, Evidence; no console errors) and fixed drawers showing on load | Pedro: pending final check in incognito |
