#!/usr/bin/env python3
"""
DEM-measured valley widths along the Seti path -> widths.csv.

Why this exists: run_seti.py v1 gave the whole path slot-canyon widths of
25-60 m, including path km 5-11 — which is the SABCHE CIRQUE, a glacial
amphitheatre several kilometres across. Routing a 22 Mm3 avalanche down a
60 m channel there makes it a 300 m deep dam-break wave that reaches
Kharapani in 7 minutes; giving the cirque its real width lets the avalanche
do what it actually did, which is spread out and stop.

Method (the same idea as model/transects.py on the Trishuli): sample the DEM
on a perpendicular stencil at each node and measure how far the ground stays
within STAGE_M of the channel floor. That is a flood-relevant width, and it
is pure geometry — it contains no timing, speed or discharge information.

Known limit, stated: a 30 m DEM cannot resolve an incised inner slot, so in
the gorge this method reads the width of the canyon rim rather than of the
channel. The measurement is therefore floored at W_MIN (the documented
slot character of the Seti gorge) and the sensitivity to that floor is run
in run_seti.py.
"""
import csv, json, math, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE_M = 30.0          # flood-relevant stage above the channel floor
W_MIN, W_MAX = 25.0, 3000.0
OFFS = [-2000, -1500, -1100, -800, -600, -450, -330, -240, -175, -125, -90,
        -60, -30, 0, 30, 60, 90, 125, 175, 240, 330, 450, 600, 800, 1100,
        1500, 2000]

rows = list(csv.DictReader(open(os.path.join(HERE, "profile.csv"))))
S = [(float(r["dist_km"]), float(r["lat"]), float(r["lon"]),
      float(r["elev_m"])) for r in rows]


def transect(i):
    a, b = S[max(i - 1, 0)], S[min(i + 1, len(S) - 1)]
    dla, dlo = b[1] - a[1], (b[2] - a[2]) * math.cos(math.radians(a[1]))
    n = math.hypot(dla, dlo) or 1.0
    pla, plo = -dlo / n, dla / n
    return [(S[i][1] + pla * o / 111000.0,
             S[i][2] + plo * o / 111000.0 / math.cos(math.radians(S[i][1])))
            for o in OFFS]


locs = [p for i in range(len(S)) for p in transect(i)]
print(f"{len(S)} nodes x {len(OFFS)} stencil = {len(locs)} DEM samples")
elev = []
for i in range(0, len(locs), 100):
    batch = locs[i:i + 100]
    req = urllib.request.Request(
        "https://api.opentopodata.org/v1/mapzen",
        data=json.dumps({"locations":
                         "|".join(f"{p[0]},{p[1]}" for p in batch)}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read())
    assert d["status"] == "OK", d
    elev.extend(r["elevation"] for r in d["results"])
    time.sleep(1.1)
print(f"  got {len(elev)}")

n = len(OFFS)
c0 = OFFS.index(0)
out = []
for i, s in enumerate(S):
    row = elev[i * n:(i + 1) * n]
    base = min(v for v in row[c0 - 2:c0 + 3] if v is not None)
    # walk outward from the centre until the ground climbs above base+STAGE
    lo = hi = 0.0
    for j in range(c0, -1, -1):
        if row[j] is None or row[j] - base > STAGE_M:
            break
        lo = OFFS[j]
    for j in range(c0, n):
        if row[j] is None or row[j] - base > STAGE_M:
            break
        hi = OFFS[j]
    out.append((s[0], max(W_MIN, min(W_MAX, hi - lo))))

with open(os.path.join(HERE, "widths.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dist_km", "width_m"])
    for km, ww in out:
        w.writerow([f"{km:.3f}", f"{ww:.0f}"])
print(f"wrote widths.csv; cirque (km 5-11) mean "
      f"{sum(w for k, w in out if 5 <= k <= 11)/max(sum(1 for k,_ in out if 5<=k<=11),1):.0f} m, "
      f"gorge (km 12-25) mean "
      f"{sum(w for k, w in out if 12 <= k <= 25)/max(sum(1 for k,_ in out if 12<=k<=25),1):.0f} m")
