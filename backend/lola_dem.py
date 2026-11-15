"""LRO LOLA polar gridded DEMs (data set LRO-L-LOLA-4-GDR-V1.0): download, read, sample.

Sources
- Files: PDS Geosciences Node, lrolol_1xxx/data/lola_gdr/polar/img/ (mirror: imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/)
- Label fields (ldem_80s_80m.lbl, ldem_85s_20m.lbl): LSB_INTEGER 16 bit, SCALING_FACTOR = 0.5,
  OFFSET = 1737400 m, UNIT = METER, POLAR STEREOGRAPHIC centred at -90 deg, radius 1737.4 km.
  height_m = DN * 0.5  (relative to the 1737.4 km sphere); radius_m = DN * 0.5 + 1737400.
- Projection (catalog/dsmap_polar.cat, south pole): longitude 0 points up from the centre,
  90 E points right. Inverse given there:
      X = (I - N/2 - 0.5) * MAP_SCALE ; Y = -(J - N/2 - 0.5) * MAP_SCALE      (I sample, J line, 1-based)
      rho = sqrt(X^2 + Y^2); lon = atan2(X, Y); lat = -90 + (180/pi) * 2 * atan(rho / (2 R))
  Forward used here is the exact inverse of that (checked by a round-trip test).
"""
from __future__ import annotations

import math
import os
import re
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
DEM_DIR = Path(os.environ.get("LOLA_DEM_DIR", ROOT / "data" / "raw" / "dem"))
MIRRORS = [
    "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/{name}",
    "https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/{upper}",
]
PRODUCTS = {  # expected .IMG sizes in bytes from the PDS listing (Nov 14, 2026)
    "ldem_80s_80m": 115_520_000,
    "ldem_85s_20m": 460_136_448,
}


def _download(name: str, dest: Path, expected: int | None = None) -> Path:
    if dest.exists() and (expected is None or dest.stat().st_size == expected):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    last = None
    for tpl in MIRRORS:
        url = tpl.format(name=name, upper=name.upper())
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0)) or expected or 0
                done = 0
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
                        done += len(chunk)
                        if total and name.endswith(".img"):
                            print(f"\r  {name}: {done/1e6:7.1f} / {total/1e6:.1f} MB", end="")
            if name.endswith(".img"):
                print()
            if expected and tmp.stat().st_size != expected:
                raise RuntimeError(f"size {tmp.stat().st_size} != expected {expected}")
            tmp.replace(dest)
            return dest
        except Exception as exc:
            last = exc
            print(f"  mirror failed ({url}): {exc}")
    raise RuntimeError(f"Could not download {name}: {last}")


def download(product: str) -> tuple[Path, Path]:
    """Download .lbl and .img for a product, e.g. 'ldem_80s_80m'. Returns (img, lbl)."""
    lbl = _download(f"{product}.lbl", DEM_DIR / f"{product}.lbl")
    img = _download(f"{product}.img", DEM_DIR / f"{product}.img", PRODUCTS.get(product))
    return img, lbl


def read_label(lbl_path: Path) -> dict:
    """Parse the PDS3 keywords we need from a .LBL file (numbers without units)."""
    text = Path(lbl_path).read_text(errors="ignore")
    keys = ["LINES", "LINE_SAMPLES", "SAMPLE_BITS", "SCALING_FACTOR", "OFFSET", "MAP_SCALE",
            "A_AXIS_RADIUS", "CENTER_LATITUDE", "LINE_PROJECTION_OFFSET", "SAMPLE_PROJECTION_OFFSET",
            "SAMPLE_TYPE", "MAP_PROJECTION_TYPE", "UNIT"]
    out = {}
    for k in keys:
        m = re.search(rf"^\s*{k}\s*=\s*\"?([^\"<\r\n]+)", text, re.M)
        if m:
            v = m.group(1).strip()
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


class PolarDEM:
    """Memory-mapped LOLA south polar DEM with lat/lon sampling."""

    def __init__(self, img_path: Path, lbl_path: Path):
        self.label = read_label(lbl_path)
        L = self.label
        assert L.get("SAMPLE_TYPE") == "LSB_INTEGER" and L.get("SAMPLE_BITS") == 16, L
        assert L.get("CENTER_LATITUDE") == -90, "only south polar products are supported"
        self.lines = int(L["LINES"])
        self.samples = int(L["LINE_SAMPLES"])
        self.scale_m = float(L["MAP_SCALE"])            # m/pixel
        self.k_m = float(L["SCALING_FACTOR"])           # m per DN (0.5)
        self.radius_m = float(L["A_AXIS_RADIUS"]) * 1000.0
        self.loff = float(L["LINE_PROJECTION_OFFSET"])  # 0-based centre row
        self.soff = float(L["SAMPLE_PROJECTION_OFFSET"])
        self.dn = np.memmap(img_path, dtype="<i2", mode="r", shape=(self.lines, self.samples))

    # --- projection (south polar stereographic, sphere R = 1737.4 km) ---
    def latlon_to_xy_m(self, lat_deg, lon_e_deg):
        rho = 2.0 * self.radius_m * np.tan(np.radians(90.0 + np.asarray(lat_deg)) / 2.0)
        lon = np.radians(lon_e_deg)
        return rho * np.sin(lon), rho * np.cos(lon)     # x right, y up (towards lon 0)

    def xy_m_to_latlon(self, x_m, y_m):
        rho = np.hypot(x_m, y_m)
        lat = -90.0 + np.degrees(2.0 * np.arctan(rho / (2.0 * self.radius_m)))
        lon = np.degrees(np.arctan2(x_m, y_m)) % 360.0
        return lat, lon

    def xy_to_rowcol(self, x_m, y_m):
        """0-based fractional (row, col)."""
        return self.loff - np.asarray(y_m) / self.scale_m, self.soff + np.asarray(x_m) / self.scale_m

    def rowcol_to_xy(self, row, col):
        return (np.asarray(col) - self.soff) * self.scale_m, (self.loff - np.asarray(row)) * self.scale_m

    # --- sampling ---
    def height_at_xy(self, x_m, y_m):
        """Bilinear height (m above the 1737.4 km sphere). NaN outside the grid."""
        r, c = self.xy_to_rowcol(x_m, y_m)
        r, c = np.atleast_1d(r).astype(float), np.atleast_1d(c).astype(float)
        r0, c0 = np.floor(r).astype(int), np.floor(c).astype(int)
        ok = (r0 >= 0) & (c0 >= 0) & (r0 < self.lines - 1) & (c0 < self.samples - 1)
        out = np.full(r.shape, np.nan)
        if ok.any():
            rr, cc, r0o, c0o = r[ok], c[ok], r0[ok], c0[ok]
            fr, fc = rr - r0o, cc - c0o
            z00 = self.dn[r0o, c0o].astype(float); z01 = self.dn[r0o, c0o + 1].astype(float)
            z10 = self.dn[r0o + 1, c0o].astype(float); z11 = self.dn[r0o + 1, c0o + 1].astype(float)
            z = (z00 * (1 - fr) * (1 - fc) + z01 * (1 - fr) * fc + z10 * fr * (1 - fc) + z11 * fr * fc)
            out[ok] = z * self.k_m
        return out

    def height_at(self, lat_deg, lon_e_deg):
        x, y = self.latlon_to_xy_m(lat_deg, lon_e_deg)
        return self.height_at_xy(x, y)

    def contains(self, lat_deg, lon_e_deg) -> bool:
        r, c = self.xy_to_rowcol(*self.latlon_to_xy_m(lat_deg, lon_e_deg))
        return bool(0 <= r < self.lines - 1 and 0 <= c < self.samples - 1)


def load(product: str) -> PolarDEM:
    img, lbl = download(product)
    return PolarDEM(img, lbl)
