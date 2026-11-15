# AI Usage Log - NASA Space Apps Challenge 2026

Rules: RESOURCE/FORM/SI_RULES.md. Every AI use: tool, what it produced, what a human verified.

| Timestamp (BOT) | Tool | What the AI did | What a human verified |
| :--- | :--- | :--- | :--- |
| 2026-11-14 16:00 | Claude (Anthropic) | Compiled the inventory of 39 NASA API endpoints (nasa_apis.csv) | Pedro: pending live test of each endpoint |
| 2026-11-14 20:00 | Claude (Anthropic) | Installed the team AI kit for Claude Code (skills, hooks, MCP config) | Pedro: checked /mcp shows the 4 servers connected |
| 2026-11-14 21:00 | Claude (Anthropic) | Wrote the Horizons client, P2 smoke test and parser unit test | Pedro: ran P2 (2027-01-01, 1 h, 357.5E -86.0); 25/25 rows parsed for Sun and Earth; first-row az/el identical to raw table; ranges plausible (Sun 0.98270 AU = 147.0e6 km, Earth 391,604 km) |
