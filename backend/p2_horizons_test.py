"""P2 - Horizons smoke test: 1 site, 1 day, 1 h step, Sun (10) and Earth (399).

Test coordinate = the example in RESOURCE/TOOLS/HORIZONS_GUIDE.md section 3.3
(357.5 deg E, -86.0 deg, 0 km). Replace with a SITE_CATALOG site when available.
Run from the project root:  python -m backend.p2_horizons_test
"""
from pathlib import Path

from backend.horizons import observer_table, ROOT

SITE = {"name": "guide_example", "lon_deg_e": 357.5, "lat_deg": -86.0, "alt_km": 0.0}
START, STOP, STEP = "2027-01-01", "2027-01-02", "1h"
OUT = ROOT / "data" / "processed" / "horizons"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for body in ("sun", "earth"):
        df, raw = observer_table(body, SITE["lon_deg_e"], SITE["lat_deg"], SITE["alt_km"],
                                 START, STOP, STEP)
        raw_path = OUT / f"P2_{SITE['name']}_{body}_raw.txt"
        raw_path.write_text(raw, encoding="utf-8")
        df.to_csv(OUT / f"P2_{SITE['name']}_{body}.csv", index=False)
        # Check: number of parsed rows equals the rows between $$SOE and $$EOE
        block = raw.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
        status = "OK" if len(block) == len(df) else "MISMATCH"
        print(f"\n== {body.upper()} ({status}: {len(df)} parsed / {len(block)} raw rows)")
        print("raw first row   :", block[0].strip())
        print("parsed first row:", df.iloc[0].to_dict())
        print(f"elevation range : {df.elevation_deg.min():.3f} to {df.elevation_deg.max():.3f} deg")


if __name__ == "__main__":
    main()
