#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DJI Mavic 3 Multispektral → helles pseudo-RGB-Preview.
Aufruf:
python create_stackedRGB.py 2025-08-27 --subfolder 1_Weide
"""

import os, sys, argparse
from os.path import join, exists
import numpy as np
import rasterio as rio

# ---------- Hilfsfunktionen ----------

def to01(A):
    A = A.astype("float32")
    m = float(np.nanmax(A))
    if m <= 0:
        return A
    if m > 20000:
        A /= 65535.0
    elif m > 2000:
        A /= 10000.0
    else:
        A /= m
    return np.clip(A, 0, 1)

def synth_blue(G, R, RE):
    # Erzeuge pseudo-blau, stärkerer RE-Anteil für helleres Gesamtbild
    B = 1.15 * G + 0.55 * (RE - 0.4 * R)
    return np.clip(B, 0.0, 1.0)

def joint_stretch(R, G, B, pmin=0.1, pmax=99.9, gamma=0.65):
    # noch hellere Ausgabe
    stk = np.stack([R, G, B], 0)
    vals = stk[np.isfinite(stk)]
    lo, hi = np.percentile(vals, [pmin, pmax])
    if hi <= lo:
        hi = lo + 1e-6

    def st(A):
        A = (A - lo) / (hi - lo)
        return np.clip(A, 0, 1)

    R, G, B = st(R), st(G), st(B)
    # Gamma kleiner als 1 → Aufhellung
    R, G, B = R ** gamma, G ** gamma, B ** gamma

    R8 = (R * 255 + 0.5).astype("uint8")
    G8 = (G * 255 + 0.5).astype("uint8")
    B8 = (B * 255 + 0.5).astype("uint8")
    return R8, G8, B8

# ---------- Hauptfunktion ----------

def process_images_for_date(date, subfolder=None, src_name="{date}_allChannels.tif"):
    base = join(date, subfolder, "Agisoft", "Agi_EXPORT") if subfolder else join(date, "Agisoft", "Agi_EXPORT")
    src_path = join(base, src_name.format(date=date))
    out_path = join(base, f"{date}_RGB_from_M3M.tif")

    if not exists(src_path):
        print(f"[{date}] fehlt: {src_path}")
        return False

    with rio.open(src_path) as ds:
        if ds.count < 3:
            print(f"[{date}] Zu wenige Bänder.")
            return False

        G = ds.read(1)
        R = ds.read(2)
        RE = ds.read(3)

        R, G, RE = to01(R), to01(G), to01(RE)
        B = synth_blue(G, R, RE)
        R8, G8, B8 = joint_stretch(R, G, B, pmin=0.1, pmax=99.9, gamma=0.65)

        prof = ds.profile.copy()
        prof.update(driver="GTiff", count=3, dtype="uint8", compress="lzw")
        prof.pop("nodata", None)

        os.makedirs(base, exist_ok=True)
        with rio.open(out_path, "w", **prof) as dst:
            dst.write(np.stack([R8, G8, B8], 0))

    print(f"[{date}] OK → {out_path}")
    return True

# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("dates", nargs="+")
    p.add_argument("--subfolder", default=None)
    args = p.parse_args()
    for d in args.dates:
        process_images_for_date(d, args.subfolder)

if __name__ == "__main__":
    sys.exit(main())
