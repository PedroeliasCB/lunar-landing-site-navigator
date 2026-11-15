"""P3 - Download LDEM_80S_80M (far field) + LDEM_85S_20M (near field), confirm label scaling,
read the site elevation at every curated polar site from both DEMs, and compare.

Run from the project root:  python -m backend.p3_dem_check
Then compare Malapert with LROC QuickMap (https://quickmap.lroc.asu.edu, LOLA elevation layer).
Outputs data/processed/p3_site_elevations.csv
"""
import csv

from backend.lola_dem import load, ROOT
from backend.sites import SITES, to_lon_180


def main():
    dems = {}
    for p in ("ldem_80s_80m", "ldem_85s_20m"):
        print(f"Loading {p} ...")
        d = load(p)
        L = d.label
        print(f"  {p}: {d.lines}x{d.samples} px, {d.scale_m:g} m/px, SCALING_FACTOR={L['SCALING_FACTOR']} "
              f"m/DN, OFFSET={L['OFFSET']:.0f} m, UNIT={L.get('UNIT')}")
        assert L["SCALING_FACTOR"] == 0.5, "label scaling is not 0.5 m/DN - stop and check"
        dems[p] = d

    rows = []
    print(f"\n{'site':28s} {'lat':>9s} {'lon E':>9s} {'h 80 m DEM':>12s} {'h 20 m DEM':>12s} {'diff':>8s}")
    for s in SITES:
        h80 = float(dems["ldem_80s_80m"].height_at(s["lat_deg"], s["lon_e_deg"])[0])
        h20 = float(dems["ldem_85s_20m"].height_at(s["lat_deg"], s["lon_e_deg"])[0])
        diff = h20 - h80
        rows.append({**{k: s[k] for k in ("id", "name", "lat_deg", "lon_e_deg", "status", "source")},
                     "lon_180_deg": round(to_lon_180(s["lon_e_deg"]), 5),
                     "height_m_ldem_80s_80m": round(h80, 1), "height_m_ldem_85s_20m": round(h20, 1)})
        f = lambda v: "outside" if v != v else f"{v:10.1f} m"
        print(f"{s['name'][:28]:28s} {s['lat_deg']:9.4f} {s['lon_e_deg']:9.4f} {f(h80):>12s} {f(h20):>12s} "
              f"{'' if diff != diff else f'{diff:7.1f}':>8s}")

    # Round-trip projection check (lat/lon -> x,y -> lat/lon)
    d = dems["ldem_85s_20m"]
    for s in SITES:
        lat2, lon2 = d.xy_m_to_latlon(*d.latlon_to_xy_m(s["lat_deg"], s["lon_e_deg"]))
        assert abs(lat2 - s["lat_deg"]) < 1e-9 and abs(((lon2 - s["lon_e_deg"] + 180) % 360) - 180) < 1e-9

    out = ROOT / "data" / "processed" / "p3_site_elevations.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nSaved {out}")
    print("Next: open QuickMap, click Malapert (86.0 S, 356.6 E = -3.4 E) with the LOLA elevation layer and compare.")


if __name__ == "__main__":
    main()
