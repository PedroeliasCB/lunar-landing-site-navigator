"""JPL Horizons client for observer tables seen from the lunar surface.

Source: JPL Horizons REST API, https://ssd-api.jpl.nasa.gov/doc/horizons.html
Recipe: RESOURCE/TOOLS/HORIZONS_GUIDE.md (sections 3 and 6).

- Observer site on the Moon: CENTER='coord@301', COORD_TYPE='GEODETIC',
  SITE_COORD='lon_deg_east,lat_deg,alt_km' (lunar longitude is positive EAST).
- QUANTITIES 4 = apparent azimuth/elevation (airless, no refraction on the Moon),
  20 = observer range (AU for Sun/Earth) and range-rate (km/s).
- Data rows sit between $$SOE and $$EOE.

Units: azimuth_deg and elevation_deg in degrees, range_km in km,
range_rate_km_s in km/s.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
AU_KM = 149_597_870.7  # IAU 2012 Resolution B2, exact
BODIES = {"sun": "10", "earth": "399"}
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "horizons"


def build_params(body_id: str, lon_deg_e: float, lat_deg: float, alt_km: float,
                 start: str, stop: str, step: str = "1h") -> dict:
    """Horizons parameters for one observer table (strings must be single-quoted)."""
    return {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{lon_deg_e},{lat_deg},{alt_km}'",
        "START_TIME": f"'{start}'",
        "STOP_TIME": f"'{stop}'",
        "STEP_SIZE": f"'{step}'",
        "QUANTITIES": "'4,20'",
        "CSV_FORMAT": "'YES'",
    }


def _cache_key(params: dict) -> str:
    norm = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def fetch_raw(params: dict, use_cache: bool = True, retries: int = 3) -> str:
    """Return the raw Horizons text table, cached on disk by sha256 of the request."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{_cache_key(params)}.txt"
    if use_cache and path.exists():
        return path.read_text(encoding="utf-8")
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(API_URL, params=params, timeout=60)
            r.raise_for_status()
            payload = r.json()
            if "error" in payload:
                raise RuntimeError(f"Horizons error: {payload['error']}")
            text = payload.get("result", "")
            if "$$SOE" not in text:  # HTTP 200 can still carry an error message
                raise RuntimeError("Horizons returned no $$SOE block:\n" + text[-1500:])
            path.write_text(text, encoding="utf-8")
            (path.with_suffix(".json")).write_text(
                json.dumps({"params": params, "signature": payload.get("signature")}, indent=2),
                encoding="utf-8")
            return text
        except Exception as exc:  # retry on network or API errors
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Horizons request failed after {retries} tries: {last}")


def parse_observer_table(text: str) -> pd.DataFrame:
    """Parse rows between $$SOE and $$EOE.

    Columns are located from the CSV header line printed just above $$SOE;
    if that fails we fall back to the positions documented in HORIZONS_GUIDE
    (0 datetime, 3 azimuth, 4 elevation, 5 range, 6 range-rate).
    """
    lines = text.splitlines()
    soe = next(i for i, l in enumerate(lines) if l.strip() == "$$SOE")
    eoe = next(i for i, l in enumerate(lines) if l.strip() == "$$EOE")
    header = None
    for l in reversed(lines[:soe]):
        if "Date" in l and "," in l:
            header = [h.strip() for h in l.split(",")]
            break

    def find(prefix, default):
        if header:
            for i, h in enumerate(header):
                if h.startswith(prefix):
                    return i
        return default

    i_az, i_el = find("Azi", 3), find("Elev", 4)
    i_rg, i_rr = find("delta", 5), find("deldot", 6)
    rows = []
    for l in lines[soe + 1:eoe]:
        f = [x.strip() for x in l.split(",")]
        if len(f) <= max(i_az, i_el, i_rg, i_rr):
            continue
        rows.append({
            "time_utc": f[0],
            "azimuth_deg": float(f[i_az]),
            "elevation_deg": float(f[i_el]),
            "range_km": float(f[i_rg]) * AU_KM,
            "range_rate_km_s": float(f[i_rr]),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["time_utc"] = pd.to_datetime(df["time_utc"], format="%Y-%b-%d %H:%M")
    return df


def observer_table(body: str, lon_deg_e: float, lat_deg: float, alt_km: float,
                   start: str, stop: str, step: str = "1h") -> tuple[pd.DataFrame, str]:
    """Fetch and parse one table. body is 'sun' or 'earth'. Returns (df, raw_text)."""
    params = build_params(BODIES[body], lon_deg_e, lat_deg, alt_km, start, stop, step)
    raw = fetch_raw(params)
    return parse_observer_table(raw), raw
