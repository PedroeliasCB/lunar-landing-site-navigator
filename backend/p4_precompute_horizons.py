"""P4 - Precompute Horizons Sun (10) and Earth (399) observer tables for every curated site.

Window and step come from Gate 1 (RESOURCE/SCIENCE/OPEN_SCIENCE_DECISIONS.md). Pass them as arguments:
    python -m backend.p4_precompute_horizons --start 2027-01-01 --stop 2028-01-01 --step 1h
Requests are split in chunks of at most 30 days (HORIZONS_GUIDE section 6) and cached by request hash,
so a re-run only downloads what is missing.
Site altitude = LOLA height at the site (data/processed/p3_site_elevations.csv; 20 m DEM if available,
else 80 m), converted to km above the 1737.4 km sphere.
Output: data/processed/horizons/<site_id>_<body>.csv  (one file per site and body)
"""
import argparse
import csv
from datetime import datetime, timedelta

import pandas as pd

from backend.horizons import observer_table, ROOT
from backend.sites import SITES

OUT = ROOT / "data" / "processed" / "horizons"
ELEV = ROOT / "data" / "processed" / "p3_site_elevations.csv"


def site_alt_km() -> dict:
    alt = {}
    with open(ELEV) as fh:
        for r in csv.DictReader(fh):
            h = r["height_m_ldem_85s_20m"]
            h = r["height_m_ldem_80s_80m"] if h in ("", "nan") else h
            alt[r["id"]] = float(h) / 1000.0
    return alt


def chunks(start: str, stop: str, days: int = 30):
    a, b = datetime.fromisoformat(start), datetime.fromisoformat(stop)
    while a < b:
        c = min(a + timedelta(days=days), b)
        yield a.strftime("%Y-%m-%d %H:%M"), c.strftime("%Y-%m-%d %H:%M")
        a = c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="UTC, e.g. 2027-01-01")
    ap.add_argument("--stop", required=True, help="UTC, e.g. 2028-01-01")
    ap.add_argument("--step", default="1h", help="Horizons step, e.g. 1h, 10m")
    ap.add_argument("--sites", default="all", help="comma-separated site ids or 'all'")
    args = ap.parse_args()

    alts = site_alt_km()
    OUT.mkdir(parents=True, exist_ok=True)
    chosen = SITES if args.sites == "all" else [s for s in SITES if s["id"] in args.sites.split(",")]
    for s in chosen:
        alt = alts.get(s["id"], 0.0)
        for body in ("sun", "earth"):
            parts = []
            for a, b in chunks(args.start, args.stop):
                df, _ = observer_table(body, s["lon_e_deg"], s["lat_deg"], round(alt, 4), a, b, args.step)
                parts.append(df)
            df = pd.concat(parts).drop_duplicates("time_utc").sort_values("time_utc")
            df.insert(0, "site_id", s["id"])
            path = OUT / f"{s['id']}_{body}.csv"
            df.round({"azimuth_deg": 5, "elevation_deg": 5, "range_km": 1, "range_rate_km_s": 6}).to_csv(path, index=False)
            print(f"{s['id']:22s} {body:5s} alt {alt*1000:7.1f} m  rows {len(df):6d}  "
                  f"el {df.elevation_deg.min():7.3f}..{df.elevation_deg.max():7.3f} deg  -> {path.name}")


if __name__ == "__main__":
    main()
