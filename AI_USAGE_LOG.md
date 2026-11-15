# AI Usage Log - NASA Space Apps Challenge 2026

Rules: RESOURCE/FORM/SI_RULES.md. Every AI use: tool, what it produced, what a human verified.

| Timestamp (BOT) | Tool | What the AI did | What a human verified |
| :--- | :--- | :--- | :--- |
| 2026-11-14 16:00 | Claude (Anthropic) | Compiled the inventory of 39 NASA API endpoints (nasa_apis.csv) | Pedro: pending live test of each endpoint |
| 2026-11-14 20:00 | Claude (Anthropic) | Installed the team AI kit for Claude Code (skills, hooks, MCP config) | Pedro: checked /mcp shows the 4 servers connected |
| 2026-11-14 21:00 | Claude (Anthropic) | Wrote the Horizons client, P2 smoke test and parser unit test | Pedro: ran P2 (2027-01-01, 1 h, 357.5E -86.0); 25/25 rows parsed for Sun and Earth; first-row az/el identical to raw table; ranges plausible (Sun 0.98270 AU = 147.0e6 km, Earth 391,604 km) |
| 2026-11-14 21:10 | Claude (Anthropic) | Wrote LOLA DEM reader (download, label parse, south polar stereographic projection, bilinear sampling), site list from SITE_CATALOG, P3 check script and projection tests | Pedro ran P3: label SCALING_FACTOR 0.5 m/DN confirmed; Malapert (86.0 S, 356.6 E) = 4690.5 m (LDEM_80S_80M), 4690.3 m (LDEM_85S_20M) vs LROC QuickMap TerrainHeight 4689.630 m (2 m/px terrain, slope 17.272 deg); difference < 1 m |
| 2026-11-14 21:15 | Claude (Anthropic) | Wrote P4 precompute script (Horizons Sun/Earth per site, 30-day chunks, site altitude from LOLA DEM) | Pedro: pending, run after Gate 1 sets window and step |
