# P3 validation - LOLA DEM site elevation vs LROC QuickMap

Date: 2026-11-14 21:10 BOT

| Check | Value |
|---|---|
| Label SCALING_FACTOR (both DEMs) | 0.5 m per DN, OFFSET 1737400 m, UNIT METER |
| Malapert (86.0 S, 356.6 E), LDEM_80S_80M | 4690.5 m |
| Malapert, LDEM_85S_20M | 4690.3 m |
| Malapert, LROC QuickMap Inspect "TerrainHeight" | 4689.630 m (TerrainPixelScale 2.000 m/px, TerrainSlope 17.272 deg) |
| Difference DEM vs QuickMap | < 1 m |

Height is relative to the 1737.4 km reference sphere. QuickMap query: point at -86.0 lat, -3.4 lon, Inspect tab, box 0.03 km, 1x1 px.
All 8 curated polar sites: data/processed/p3_site_elevations.csv (80 m vs 20 m DEM agree within 2.5 m; IM-1 at 80.13 S is outside the 85S DEM, as expected).
