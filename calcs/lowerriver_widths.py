#!/usr/bin/env python3
"""
LOWER-RIVER SECTION WIDTHS from the DEM at the fitted stage (dossier §24).

v10 left one conflict: the model carries the Trishuli below Betrawati as a
267 m channel (one v6 station's value held flat km 70–108, then the 120 m
rule) where the site table has ~500 m at Galchhi, and the wet runs put
14–19 m there against ≤ 9.9. The imagery-based width filter has 8 stations
below km 60 and none below km 92 (10 m Sentinel returns the gravel margin
down there). So take the width from the elevation model directly: at every
100 m station of the trimline mapper, sample the transect on HMA 8 m
(GLO-30 fill), put the water at bed + stage_fit(km) from
output/trimline_fit.csv, and record the wetted area A, top width W_top and
equivalent rectangular width W_eq = A / stage — the quantity v6 used where
imagery gave an A. Also W_top at bed + 5 / 10 / 20 m for the reader.

Caveats carried: the DEM is a 2017 surface (HMA) — terraces are real, the
2026 channel is not; the fit stage below Mugling rests on few clean points
(§19a) so W_eq there is indicative; a floodplain conveys less than its
wetted width (v11 samples a factor).

Run: .venv/bin/python calcs/lowerriver_widths.py   -> output/lowerriver_widths.csv
"""
import csv, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import trimline_map as TM

KM0, KM1 = 40.0, 200.0
HALF, STEP = 900.0, 8.0            # transect half-width and sample step, m


def fit_stage():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "output", "trimline_fit.csv"))))
    km = np.array([float(r["km"]) for r in rows]); s = np.array([float(r["stage_fit"]) for r in rows])
    return lambda k: float(np.interp(k, km, s))


def main():
    st, _ = TM.stations_main()
    dem = TM.DEM()
    sfit = fit_stage()
    offs = np.arange(-HALF, HALF + STEP, STEP)
    bed_half = getattr(TM, "BED_HALF", 150.0)
    out = []
    for s in st:
        if s["km"] < KM0 or s["km"] > KM1: continue
        x = s["x"] + offs * s["nx"]; y = s["y"] + offs * s["ny"]
        z, _, src = dem.sample(x, y)
        if np.isfinite(z).sum() < 0.8 * len(z): continue
        zz = np.where(np.isfinite(z), z, 9999.0)
        near = np.abs(offs) <= bed_half
        bed = float(zz[near].min())
        stage = sfit(s["km"])
        A, W = TM.wet_area(zz, offs, bed + stage)
        row = dict(km=round(s["km"], 1), bed=round(bed, 1), stage_fit=round(stage, 1),
                   A=round(A), W_top=round(W), W_eq=round(A / stage) if stage > 0 else 0,
                   hma=int(np.mean(src == 1) > 0.5))
        for h in (5, 10, 20):
            row[f"W_top_{h}"] = round(TM.wet_area(zz, offs, bed + h)[1])
        out.append(row)
    p = os.path.join(ROOT, "output", "lowerriver_widths.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    km = np.array([r["km"] for r in out]); weq = np.array([r["W_eq"] for r in out], float); wt = np.array([r["W_top"] for r in out], float)
    print(f"{len(out)} stations km {km.min():.1f}–{km.max():.1f} -> {p}")
    print("reach        n   stage_fit  W_eq p25/med/p75   W_top med   W_top@10m med")
    for lo, hi in ((40, 46), (46, 70), (70, 90), (90, 108.2), (108.2, 120), (120, 140), (140, 170), (170, 200)):
        m = (km >= lo) & (km < hi)
        if not m.any(): continue
        w10 = np.array([r["W_top_10"] for r in out], float)[m]
        print(f"  {lo:5.1f}-{hi:5.1f} {m.sum():4d}  {np.median([r['stage_fit'] for r in out if lo <= r['km'] < hi]):6.1f}   "
              f"{np.percentile(weq[m],25):5.0f}/{np.median(weq[m]):5.0f}/{np.percentile(weq[m],75):5.0f}     {np.median(wt[m]):5.0f}      {np.median(w10):5.0f}")


if __name__ == "__main__":
    main()
