#!/usr/bin/env python3
"""
Extract valley CROSS-SECTIONS along the flood path from the Mapzen/SRTM
terrain (30 m posting) and build nonlinear stage-storage tables:
  width(eta) and flow area(eta) per station, eta = stage above local channel
  minimum, contiguous span containing the channel (so side gullies don't
  contribute phantom storage).

This replaces the ladder's rectangular-channel guess: capacitance C(eta)
becomes piecewise-nonlinear - tiny in gorges even at high stage, exploding
where valleys open (Dave's "non-linear valley sides").

Output: data/transects.json {km, eta_grid, width[st][lvl], area[st][lvl]}
"""
import csv, json, math, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

STEP_KM = 5.0          # station spacing along path
HALF_PTS = 20          # points each side of channel
SPACING = 30.0         # m between transect points (matches DEM posting)
ETA_MAX, ETA_STEP = 120.0, 2.0

rows = list(csv.DictReader(open(os.path.join(DATA, "river_path.csv"))))
path = [(float(r["dist_km"]), float(r["lat"]), float(r["lon"])) for r in rows]

# stations + perpendicular directions
stations = []
target = 0.0
for i, (km, la, lo) in enumerate(path):
    if km >= target:
        j0, j1 = max(i - 2, 0), min(i + 2, len(path) - 1)
        dn = (path[j1][1] - path[j0][1]) * 110574.0          # m north
        de = (path[j1][2] - path[j0][2]) * 111320.0 * math.cos(math.radians(la))
        L = math.hypot(dn, de) or 1.0
        # unit perpendicular (east, north)
        pe, pn = -dn / L, de / L
        stations.append((km, la, lo, pe, pn))
        target += STEP_KM
print(f"{len(stations)} transect stations")

# build all query points
pts = []
for km, la, lo, pe, pn in stations:
    for k in range(-HALF_PTS, HALF_PTS + 1):
        d = k * SPACING
        pts.append((la + d * pn / 110574.0,
                    lo + d * pe / (111320.0 * math.cos(math.radians(la)))))
print(f"{len(pts)} DEM samples to fetch")

elevs = []
for i in range(0, len(pts), 100):
    batch = pts[i:i + 100]
    locs = "|".join(f"{a:.6f},{b:.6f}" for a, b in batch)
    req = urllib.request.Request(
        "https://api.opentopodata.org/v1/mapzen",
        data=json.dumps({"locations": locs}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read())
    assert d["status"] == "OK", d
    elevs.extend(r["elevation"] if r["elevation"] is not None else 9999
                 for r in d["results"])
    time.sleep(1.2)
print(f"fetched {len(elevs)} elevations")

NPTS = 2 * HALF_PTS + 1
eta_grid = [i * ETA_STEP for i in range(int(ETA_MAX / ETA_STEP) + 1)]
out = {"km": [], "eta": eta_grid, "width": [], "area": []}
for s, (km, la, lo, pe, pn) in enumerate(stations):
    z = elevs[s * NPTS:(s + 1) * NPTS]
    imin = min(range(NPTS), key=lambda i: z[i])
    z0 = z[imin]
    W, A = [], []
    for eta in eta_grid:
        # contiguous wetted span through the channel minimum
        lo_i = imin
        while lo_i > 0 and z[lo_i - 1] - z0 < eta:
            lo_i -= 1
        hi_i = imin
        while hi_i < NPTS - 1 and z[hi_i + 1] - z0 < eta:
            hi_i += 1
        wet = range(lo_i, hi_i + 1)
        W.append(len(wet) * SPACING if eta > 0 else 0.0)
        A.append(sum(max(eta - (z[i] - z0), 0.0) for i in wet) * SPACING)
    out["km"].append(round(km, 2))
    out["width"].append([round(w, 1) for w in W])
    out["area"].append([round(a, 1) for a in A])

with open(os.path.join(DATA, "transects.json"), "w") as fh:
    json.dump(out, fh, separators=(",", ":"))
print(f"wrote data/transects.json ({os.path.getsize(os.path.join(DATA,'transects.json'))//1024} KB)")

# quick diagnostic: width at 10 m and 60 m stage at a few stations
for s in range(0, len(stations), 5):
    km = out["km"][s]
    w10 = out["width"][s][int(10 / ETA_STEP)]
    w60 = out["width"][s][int(60 / ETA_STEP)]
    print(f"  km {km:6.1f}: width @10m = {w10:6.0f} m | @60m = {w60:6.0f} m")
