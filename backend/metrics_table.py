"""Write docs/METRICS_TABLE.md from docs/data (RESOURCE/BUILD/METRICS_TABLE.md format). Run after build_site_data."""
import json

from backend.horizons import ROOT

D = ROOT / "docs" / "data"


def main():
    idx = json.load(open(D / "index.json")); val = json.load(open(D / "validation.json"))
    L = ["# METRICS TABLE - pipeline results per site", "",
         f"Window: {idx['series_start_utc']} + 30 days · Step: {idx['step_min']} min · Disc convention: centre (D1 headline) · "
         "Earth threshold: 0 deg above skyline (D2) · Mast: 2 m (D3) · Ephemeris: JPL Horizons precomputed (D5) · "
         "DEM: LDEM_85S_20M + LDEM_80S_80M, 150 km, 720 azimuths (D4) · Generated " + idx["generated_utc"], "",
         "| Site | Status | Terrain | Sunlight % | Longest night (h) | Earth-in-view % | Longest no-signal (h) | Both up % | Longest blackout (h) | Max Sun elev (deg) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for s in idx["sites"]:
        m = s["metrics"]
        L.append(f"| {s['name']} | {s['status']} | {s['terrain_source']} | {m['sunlight_pct']} | {m['longest_night_h']} | {m['earth_pct']} | "
                 f"{m['longest_no_earth_h']} | {m['both_pct']} | {m['blackout_longest_h']} | {m['max_sun_el_deg']} |")
    L += ["", "## Validation", "", "| Site | Check | Ours | Reference | Difference | Source / note |", "|---|---|---|---|---|---|"]
    for r in val:
        L.append(f"| {r['site']} | {r['metric']} | {r['ours']} | {r['reference']} | {r['difference']} | {r['reference_source']}. {r['comment']} |")
    (ROOT / "docs" / "METRICS_TABLE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
