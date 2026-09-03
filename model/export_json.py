#!/usr/bin/env python3
"""Export model outputs as JSON for the report's D3 charts."""
import json, os, runpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "report", "chart_data.json")

def ds(arr, step):
    return [round(float(v), 3) for v in np.asarray(arr)[::step]]

print("running snowplow...")
sp = runpy.run_path(os.path.join(HERE, "snowplow.py"))
print("running ladder (3 runs, ~2-4 min)...")
ld = runpy.run_path(os.path.join(HERE, "ladder.py"))

x = sp["x_km"]; step = 2
snow = sp["SCEN"][0]                      # snowplow best-evidence scenario
data = {
    "timing": {
        "km": ds(x, step),
        "front": ds(sp["t_front"], step),
        "peak": ds(sp["t_peak"], step),
        "front_obs": [[km, m, w] for km, m, w in sp["FRONT_OBS"]],
        "peak_obs": [[km, m, w] for km, m, w in sp["PEAK_OBS"]],
    },
    "speed": {
        "km": ds(x, step),
        "u": ds(sp["U_front"], step),
        "obs": [[11, 52, "avg 0–22 km (Kargel, 193 km/h)"],
                [30, 45, "geopera, border: 45–52"],
                [40, 11, "geopera, Syabrubesi opening"],
                [50, 21, "border→Betrawati celerity"],
                [90, 6, "Betrawati→Galchhi celerity"],
                [160, 7, "lower-reach celerity"]],
    },
    "sources": {
        "km": ds(x, step),
        "melt": ds(snow["melt"] / 1e6, step),
        "pore": ds(snow["pore"] / 1e6, step),
        "chan": ds(snow["chan"] / 1e6, step),
        "infl": ds(snow["infl"] / 1e6, step),
    },
    "ladder": {
        "t": ds(ld["t2"], 3),
        "runs": {},
        "obs_devghat": [7.383, 5850],
    },
    "sidevalleys": {
        "t": ds(ld["t2"], 3),
        "series": {nm: ds(ld["hs2"][nm], 3) for nm in ld["hs2"]},
    },
}
for run_key, q in [("run1", ld["q1"]), ("run2", ld["q2"]), ("run3", ld["q3"]),
                   ("run2d", ld["q2d"])]:
    data["ladder"]["runs"][run_key] = {s: ds(v, 3) for s, v in q.items()}

# budget-explorer arrays (client-side ledger re-computation)
data["budget"] = {
    "km": [round(float(v), 3) for v in x],
    "qbase": [round(float(v), 1) for v in sp["Q_base"]],
    "dx_m": [round(float(v), 1) for v in np.gradient(x) * 1000.0],
    "dt_s": [round(float(v), 1) for v in np.gradient(sp["t_front"]) * 60.0],
    "dur_dev_s": float(np.maximum((45.0 + 0.85 * (x - 22.0)) * 60.0, 420.0)[-1]),
}

# Chamoli hindcast curves (Phase F): produced by hindcast/chamoli/
# run_voellmy.py; merged when present.
ch = os.path.join(HERE, "..", "hindcast", "chamoli", "voellmy_curves.json")
if os.path.exists(ch):
    data["chamoli"] = json.load(open(ch))
    print("merged chamoli voellmy curves")

# Carry forward keys this script does not generate — notably "map", which
# export_map.py APPENDS to chart_data.json. Without this, re-running the
# model export silently drops the corridor map from the report page.
if os.path.exists(OUT):
    try:
        prev = json.load(open(OUT))
        for k in prev:
            if k not in data:
                data[k] = prev[k]
                print(f"carried forward '{k}' from previous chart_data.json")
    except json.JSONDecodeError:
        pass

with open(OUT, "w") as fh:
    json.dump(data, fh, separators=(",", ":"))
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB)")
if "map" not in data:
    print("  WARNING: no 'map' key — run model/export_map.py to add it")
