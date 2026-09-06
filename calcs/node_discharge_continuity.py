#!/usr/bin/env python3
"""
Peak-discharge continuity at the border junction: the split from mud lines.

WHY (Dave, 6 Sept late). The volume that ran up the Chinese arm only becomes
a volume through the junction once we know the SHARE that went up, and the
valley geometry cannot fix that share (calcs/upvalley_wedge_volume.py
--volumetric: anywhere from ~0 to ~0.55 depending on which reach of the
Lhende is called 'incoming'). Mass conservation at the node at the instant of
peak does not need a time axis:

    Q_in(peak) = Q_down(peak) + Q_up(peak)     =>   f_up = 1 - Q_down / Q_in

and a peak discharge at a station is a cross-section area at the trimline
times a velocity, both of which mud lines give: area from the trimline
elevation through a DEM cross-section, velocity from superelevation at a bend
(v^2 = g r dh / W) or from run-up on an obstacle (v = sqrt(2 g R / alpha)).
Helicopter footage is exactly the source for those marks.

INPUT: a CSV of stations (data/node_stations.csv), one row per mark:

    arm,km,lat,lon,trim_m,inner_m,outer_m,radius_m,runup_m,alpha,note
    lhende,21.2,28.2850,85.3860,1905,,,,,,"left-bank mud line at the spur"
    lhende,21.6,28.2830,85.3835,1898,1890,1906,350,,,"bend, inner/outer trimlines"
    down,22.6,28.2740,85.3765,1885,,,,,,"right bank above the headworks"
    down,23.1,28.2700,85.3760,1878,1872,1884,400,,,"bend below the tunnel portal"

  arm      lhende (above the junction) or down (below it)
  km       path chainage (data/river_path.csv; junction = 22.0)
  lat,lon  where the mark is (for the DEM cross-section)
  trim_m   trimline elevation on a straight, channel-parallel reach (stage)
  inner_m, outer_m, radius_m   superelevation pair at a bend + bend radius
  runup_m, alpha               run-up height on a head-on obstacle, efficiency
  note     what the mark is and which frame/timestamp of which video

For each station the script cuts a GLO-30 cross-section perpendicular to the
path, computes the area and top width at trim_m, takes every velocity
estimate the row allows, and reports Q = A x v (with v as SECTION-MEAN: a
surface velocity from superelevation is multiplied by 0.85). It then reports
the peak Q above and below the node and the implied f_up, with the spread.

STATUS: tool only; data/node_stations.csv does not exist yet. The marks are
Dave's to read off the helicopter footage and Google Earth. Run:

    .venv/bin/python calcs/node_discharge_continuity.py data/node_stations.csv
"""
import csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
GLO30 = os.path.join(DATA, "Copernicus_DSM_COG_10_N28_00_E085_00_DEM.tif")
G = 9.81
HALF_PTS, SPACING = 25, 20.0          # +/-500 m at 20 m (bilinear on 30 m)
SURFACE_TO_MEAN = 0.85


def path():
    rows = list(csv.DictReader(open(os.path.join(DATA, "river_path.csv"))))
    return np.array([[float(r["dist_km"]), float(r["lat"]), float(r["lon"])] for r in rows])


def section(lat, lon, km, pth):
    """GLO-30 cross-section perpendicular to the path at chainage km, centred
    on (lat, lon). Returns offsets (m) and elevations."""
    import rasterio
    i = int(np.argmin(np.abs(pth[:, 0] - km)))
    i0, i1 = max(i - 2, 0), min(i + 2, len(pth) - 1)
    dn = (pth[i1, 1] - pth[i0, 1]) * 110574.0
    de = (pth[i1, 2] - pth[i0, 2]) * 111320.0 * math.cos(math.radians(lat))
    L = math.hypot(dn, de) or 1.0
    pe, pn = -dn / L, de / L
    offs = np.arange(-HALF_PTS, HALF_PTS + 1) * SPACING
    pts = [(lon + d * pe / (111320.0 * math.cos(math.radians(lat))),
            lat + d * pn / 110574.0) for d in offs]
    with rasterio.open(GLO30) as src:
        z = np.array([v[0] for v in src.sample(pts)], float)
    return offs, z


def area_width(z, eta):
    z = np.where(np.isfinite(z), z, 9999.0)
    imin = int(np.argmin(z))
    if eta <= z[imin]:
        return 0.0, 0.0, float(z[imin])
    lo = imin
    while lo > 0 and z[lo - 1] < eta: lo -= 1
    hi = imin
    while hi < len(z) - 1 and z[hi + 1] < eta: hi += 1
    seg = z[lo:hi + 1]
    return float(np.sum(np.maximum(eta - seg, 0)) * SPACING), float(len(seg) * SPACING), float(z[imin])


def main(csv_path):
    if not os.path.exists(csv_path):
        sys.exit(f"{csv_path} not found — see the docstring for the format")
    pth = path()
    rows = list(csv.DictReader(open(csv_path)))
    out = {"lhende": [], "down": []}
    print(f"{'arm':7s} {'km':>5s} {'stage':>6s} {'bed':>6s} {'A m2':>8s} {'W m':>6s} {'v super':>8s} {'v runup':>8s} {'Q Mm3/s':>9s}  note")
    for r in rows:
        f = lambda k: float(r[k]) if r.get(k, "").strip() else None
        arm, km, lat, lon = r["arm"].strip(), float(r["km"]), float(r["lat"]), float(r["lon"])
        offs, z = section(lat, lon, km, pth)
        trim = f("trim_m") or f("outer_m")
        if trim is None:
            print(f"{arm:7s} {km:5.1f}  no stage on this row"); continue
        A, W, bed = area_width(z, trim)
        vs = []
        v_super = v_runup = None
        if f("inner_m") is not None and f("outer_m") is not None and f("radius_m"):
            dh = f("outer_m") - f("inner_m")
            _, Wb, _ = area_width(z, f("outer_m"))
            if dh > 0 and Wb > 0:
                v_super = math.sqrt(G * f("radius_m") * dh / Wb) * SURFACE_TO_MEAN
                vs.append(v_super)
        if f("runup_m"):
            alpha = f("alpha") or 0.6
            v_runup = math.sqrt(2 * G * f("runup_m") / alpha) * SURFACE_TO_MEAN
            vs.append(v_runup)
        Qs = [A * v for v in vs]
        out[arm].append((km, A, W, vs, Qs, r.get("note", "")))
        print(f"{arm:7s} {km:5.1f} {trim:6.0f} {bed:6.0f} {A:8.0f} {W:6.0f} "
              f"{(v_super or float('nan')):8.1f} {(v_runup or float('nan')):8.1f} "
              f"{(max(Qs)/1e6 if Qs else float('nan')):9.3f}  {r.get('note','')}")
    def peak(arm):
        q = [Q for *_, Qs, _ in out[arm] for Q in Qs]
        return (min(q), max(q)) if q else None
    qi, qd = peak("lhende"), peak("down")
    print()
    if qi and qd:
        f_lo = max(0.0, 1 - qd[1] / qi[0]); f_hi = max(0.0, 1 - qd[0] / qi[1])
        print(f"peak Q above the node {qi[0]/1e3:.0f}–{qi[1]/1e3:.0f} k m3/s; below {qd[0]/1e3:.0f}–{qd[1]/1e3:.0f} k m3/s")
        print(f"=> up-valley share of the peak, f_up = {f_lo:.2f}–{f_hi:.2f}")
        print("   (assumes the peaks above and below are simultaneous and the arm was filling at peak;")
        print("    section-mean velocity taken as 0.85 x the surface value; areas from a 30 m DEM)")
    else:
        print("need at least one velocity-bearing station on each side of the node for the split")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "node_stations.csv"))
