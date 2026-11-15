"""Build the app data (RESOURCE/BUILD/DATA_CONTRACT.md) for every curated site.

Run from the project root on a machine with internet (JPL Horizons) and the LOLA DEMs:
    python -m backend.build_site_data
Writes docs/data/index.json, docs/data/sites/<id>.json, docs/data/validation.json.

Decisions applied (RESOURCE/SCIENCE/OPEN_SCIENCE_DECISIONS.md, DECIDED):
D1 headline = centre of disc, table also any-part; D2 threshold 0 deg (slider in UI);
D3 mast 2 m (skylines precomputed for 0, 2, 5, 10 m); D4 150 km, 720 bins; D5 precomputed Horizons;
D7 10 min step; the series spans 60 days so the UI can slip a 30-day window by up to 30 days.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import numpy as np

from backend import skyline as sk, visibility as vis
from backend.constants import MASTS_M, MAST_DEFAULT_M, AU_KM, C_KM_S, LUNAR_TILT_DEG
from backend.horizons import observer_table, ROOT
from backend.lola_dem import load
from backend.sites import SITES, to_lon_180

START, DAYS, STEP_MIN, WINDOW_DAYS = "2027-03-01", 60, 10, 30
PIPELINE_VERSION = "1.0.0"
OUT = ROOT / "docs" / "data"


def horizons_series(body, site, alt_km):
    parts = []
    t0 = datetime.fromisoformat(START)
    for k in range(0, DAYS, 30):
        a = (t0 + timedelta(days=k)).strftime("%Y-%m-%d %H:%M")
        b = (t0 + timedelta(days=min(k + 30, DAYS))).strftime("%Y-%m-%d %H:%M")
        df, _ = observer_table(body, site["lon_e_deg"], site["lat_deg"], round(alt_km, 4), a, b, f"{STEP_MIN}m")
        parts.append(df)
    import pandas as pd
    df = pd.concat(parts).drop_duplicates("time_utc").sort_values("time_utc").reset_index(drop=True)
    df = df[df.time_utc < t0 + timedelta(days=DAYS)]
    expected = DAYS * 24 * 60 // STEP_MIN
    assert len(df) == expected, f"{site['id']} {body}: {len(df)} rows, expected {expected}"
    return df


def analyse(sun, earth, H, step_h, n, convention="centre", thr=0.0):
    t_h = np.arange(n) * step_h
    rs = vis.angular_radius_deg("sun", sun.range_km.values[:n])
    re_ = vis.angular_radius_deg("earth", earth.range_km.values[:n])
    ms = vis.margin(sun.elevation_deg.values[:n], sun.azimuth_deg.values[:n], H, rs, convention, thr)
    me = vis.margin(earth.elevation_deg.values[:n], earth.azimuth_deg.values[:n], H, re_, convention, thr)
    su, eu = ms > 0, me > 0
    met = vis.metrics(su, eu, sun.elevation_deg.values[:n], step_h)
    return t_h, ms, me, su, eu, met


def iso(t0, hours):
    return (t0 + timedelta(hours=float(hours))).strftime("%Y-%m-%dT%H:%MZ")


def main():
    OUT.joinpath("sites").mkdir(parents=True, exist_ok=True)
    print("Loading LOLA DEMs ...")
    d20, d80 = load("ldem_85s_20m"), load("ldem_80s_80m")
    dems = [(d20, "LDEM_85S_20M"), (d80, "LDEM_80S_80M")]
    t0 = datetime.fromisoformat(START)
    step_h = STEP_MIN / 60.0
    n_win = WINDOW_DAYS * 24 * 60 // STEP_MIN
    index, validation = [], []

    for s in SITES:
        h_site, src = sk.site_height(dems, s["lat_deg"], s["lon_e_deg"])
        polar = src != "smooth_sphere"
        if polar:
            d, h = sk.terrain_profile([d20, d80], s["lat_deg"], s["lon_e_deg"])
        skylines, coverage = {}, 1.0
        for mast in MASTS_M:
            if polar:
                H, dist, coverage = sk.skyline_from_profile(d, h, h_site, mast)
            else:
                H = np.full(len(sk.AZ_DEG), sk.smooth_sphere_dip_deg(mast)); dist = np.full(len(sk.AZ_DEG), np.sqrt(2 * 1737400.0 * mast) / 1000)
            skylines[str(int(mast))] = {"H_deg": np.round(H, 3).tolist(), "dist_km": np.round(dist, 2).tolist()}
        alt_km = (h_site if polar else 0.0) / 1000.0
        print(f"{s['id']:22s} terrain {src:14s} h_site {h_site if polar else 0:8.1f} m  coverage {coverage:.3f}  -> Horizons")
        sun, earth = horizons_series("sun", s, alt_km), horizons_series("earth", s, alt_km)
        # Round exactly as stored in the JSON so the pipeline metrics and the browser (docs/app.js) agree bit for bit
        for df in (sun, earth):
            df["azimuth_deg"], df["elevation_deg"] = df.azimuth_deg.round(3), df.elevation_deg.round(3)
        sun["range_km"] = (sun.range_km / AU_KM).round(6) * AU_KM
        earth["range_km"] = earth.range_km.round(0)

        Hd = np.array(skylines[str(int(MAST_DEFAULT_M))]["H_deg"])
        t_h, ms, me, su, eu, met = analyse(sun, earth, Hd, step_h, n_win, "centre")
        *_, met_any = analyse(sun, earth, Hd, step_h, n_win, "any")
        ev = {k: [{"t": iso(t0, t), "kind": kind} for t, kind in vis.crossings(t_h, m)] for k, m in (("sun", ms), ("earth", me))}
        win = {k: [{"start": iso(t0, a), "end": iso(t0, b), "hours": round(hh, 2)} for a, b, hh in vis.windows(t_h, u, step_h)]
               for k, u in (("sun", su), ("earth", eu), ("blackout", ~su & ~eu))}

        rec = {
            "id": s["id"], "name": s["name"], "group": s["group"],
            "lat": s["lat_deg"], "lon_e": round(to_lon_180(s["lon_e_deg"]), 5), "frame": "MOON_ME",
            "status": s["status"], "source": s["source"],
            "h_site_m": round(h_site, 1) if polar else None, "mast_m": MAST_DEFAULT_M,
            "terrain_source": src, "terrain_coverage": round(coverage, 3),
            "skyline": {"az_step_deg": 360.0 / len(sk.AZ_DEG), "by_mast": skylines},
            "window": {"start_utc": START + "T00:00Z", "days_series": DAYS, "days_default": WINDOW_DAYS, "step_min": STEP_MIN},
            "sun": {"az": np.round(sun.azimuth_deg.values, 3).tolist(), "el": np.round(sun.elevation_deg.values, 3).tolist(),
                    "dist_au": np.round(sun.range_km.values / AU_KM, 6).tolist()},
            "earth": {"az": np.round(earth.azimuth_deg.values, 3).tolist(), "el": np.round(earth.elevation_deg.values, 3).tolist(),
                      "dist_km": np.round(earth.range_km.values, 0).tolist()},
            "events": ev, "windows": win, "metrics": met,
            "metrics_by_convention": {"centre": met, "any": met_any},
            "conventions": {"disc": "centre", "dte_threshold_deg": 0.0, "mast_m": MAST_DEFAULT_M},
            "provenance": {"ephemeris": "JPL Horizons (DE441) precomputed, observer table, airless apparent az/el",
                           "terrain": src, "computed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                           "pipeline_version": PIPELINE_VERSION},
        }
        with open(OUT / "sites" / f"{s['id']}.json", "w") as fh:
            json.dump(rec, fh, separators=(",", ":"))
        index.append({k: rec[k] for k in ("id", "name", "group", "lat", "lon_e", "status", "source", "terrain_source", "h_site_m")}
                     | {"metrics": met})
        # Validation rows (F15, D9)
        bound = 90 - abs(s["lat_deg"]) + LUNAR_TILT_DEG
        if s["lat_deg"] < -60: validation.append({"site": s["name"], "metric": "Max Sun elevation above the flat horizon in window (deg)",
                           "ours": met["max_sun_el_deg"], "reference": round(bound, 2),
                           "reference_source": "E21 smooth-sphere bound 90-|lat|+1.5424 (WORKED_NUMBERS 3)",
                           "difference": round(met["max_sun_el_deg"] - bound, 2),
                           "comment": "must not exceed the bound; a 30-day window sits below the annual maximum"})
        if s["id"] == "apollo_11":
            validation.append({"site": s["name"], "metric": "Earth in view (%)", "ours": met["earth_pct"], "reference": 100.0,
                               "reference_source": "VALIDATION_TARGETS: near-side site always sees Earth",
                               "difference": round(met["earth_pct"] - 100.0, 2), "comment": "pass if 100"})
        print(f"   sunlight {met['sunlight_pct']:6.2f} %  night {met['longest_night_h']:7.1f} h  earth {met['earth_pct']:6.2f} %"
              f"  both {met['both_pct']:6.2f} %  max sun el {met['max_sun_el_deg']:.3f} deg")

    validation.append({"site": "Malapert Massif", "metric": "Terrain height (m)", "ours": 4690.3, "reference": 4689.63,
                       "reference_source": "LROC QuickMap Inspect TerrainHeight (2 m/px)", "difference": 0.67, "comment": "P3, < 1 m"})
    validation.append({"site": "Test site 86 S 357.5 E", "metric": "Horizons table parse (rows, az/el)", "ours": "25/25 identical",
                       "reference": "raw Horizons text", "reference_source": "P2 smoke test", "difference": 0, "comment": "pass"})
    validation.append({"site": "Polar sites", "metric": "Sun / Earth visibility vs PGDA 69 long-term maps", "ours": "GAP",
                       "reference": "PGDA 69 AVGVISIB", "reference_source": "Mazarico et al. 2011", "difference": None,
                       "comment": "not compared yet: PGDA 69 is an 18.6-year average, our window is 30 days"})
    json.dump({"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "pipeline_version": PIPELINE_VERSION,
               "series_start_utc": START + "T00:00Z", "series_days": DAYS, "step_min": STEP_MIN, "sites": index},
              open(OUT / "index.json", "w"), indent=1)
    json.dump(validation, open(OUT / "validation.json", "w"), indent=1)
    print(f"\nWrote {len(index)} sites to {OUT}")


if __name__ == "__main__":
    main()
