#!/usr/bin/env python3
"""
How much went UP the Kyirong arm? A volumetric estimate from the valley
floor, the mud-line head, and the imagery-limited reach.

WHY THIS EXISTS (Dave, 6 Sept evening). Everything we have on the event's size
is a discharge or a stage - a photograph with no time axis. The one thing that
integrates is the backwater that ran up the Chinese arm above the border
junction: it filled, it drained, and it left marks. If we can measure the
volume it held at peak, and say what share of the flow at the junction went
up-valley, we get a volume that passed the junction that never used the clock,
the erosion volume or the deposition cap. Subtract what the 22 km of Lhende
contributed and it is an independent estimate of the release.

WHAT THIS SCRIPT DOES.
  1. Chains the Kyirong Tsangpo centreline up-valley from the junction out
     of data/osm_rivers.json (the same chain calcs/sentinel_wedge_corridor.py
     used), densified to 100 m stations for 6 km.
  2. Samples 30 m DEM cross-sections (Mapzen via OpenTopoData, +/-600 m) at
     every station and caches them in data/upvalley_transects.json.
  3. Builds the bed profile and stage-area tables, then integrates the
     stored volume for two readings of the same mud-line head:
       POND   - a level surface at L metres, filling the arm to where the bed
                climbs to L (what a backwater pond behind the node would hold);
       TONGUE - a surface falling from L at the junction to the bed at a
                chosen limit x_end (what a run-up surge holds at its peak),
                with a linear and a concave (p=2) profile as the bracket.
  4. Compares the DEM width of each surface with the widths read off the
     0.55 m Pelican imagery (dossier section 16a), which is the check on
     which reading is right.
  5. Turns the stored volume into a volume at the node using a bracket of
     up-valley split fractions, and into a release estimate by subtracting
     what the Lhende reach contributed. Every step is a bracket.

HONESTY, up front. The 30 m DEM over-reads an incised valley floor: our
profile put the bed at km 22 at 1,832 m against Dave's 1,815 m in Google
Earth (dossier 6c), the `LADDER_SECTIONS=dem` experiment showed low-stage
storage far too fat for the same reason. So at a given absolute water level
the DEM UNDER-reads depth and area near the floor. Volumes are computed on the
raw DEM and again with the bed lowered by the junction offset, as a bracket.
The split fraction is not measured by anything here; it is bracketed. The
routing model's junction element is a weir with an 8 m driving-head cap
(model/core.py), which is why it only ever filled the arm to ~48 m - it cannot
represent a 47 m/s jet hitting a T-junction, and is not used here.

Run:  .venv/bin/python calcs/upvalley_wedge_volume.py [--refetch]
"""
import argparse, json, math, os, sys, time, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
CACHE = os.path.join(DATA, "upvalley_transects.json")

JUNCTION = (28.2781, 85.3770)        # same datum as the corridor test
ARM_WAY = 904894054                  # OSM way at the junction, Kyirong arm
L_ARM_KM = 6.0
STEP_M = 100.0                       # station spacing along the arm
HALF_PTS, SPACING = 20, 30.0         # transect: 41 points, +/-600 m
BED_JUNCTION_GE = 1815.0             # Dave's Google Earth bed at the junction
LEVELS = [1915.0, 1920.0, 1925.0, 1930.0]     # impact-cliff mud line 1,920-1,930
X_ENDS_KM = [3.5, 4.6]               # contour trace / imagery limit
# widths read off the Pelican 0.55 m scenes (dossier 16a): (km_from, km_to, lo, hi)
IMG_WIDTHS = [(0.0, 2.5, 150.0, 250.0), (3.8, 4.6, 110.0, 145.0)]
IMG_BASE = (40.0, 60.0)              # pre-event channel width, May 2026
# what the Lhende reach contributed to the volume at the node (dossier 15)
LHENDE_CONTRIB_MM3 = (3.0, 15.0)     # 0.5 channel water + 2.6-13 bed (floor lowered 2-12 m over ~1 km2) + <=1-2.5 melt


# ------------------------------------------------------------ centreline --
def load_ways():
    d = json.load(open(os.path.join(DATA, "osm_rivers.json")))
    return {e["id"]: e for e in d["elements"] if e["type"] == "way"}


def dj_pair(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111.2,
                      (a["lon"] - b["lon"]) * 111.2 * math.cos(math.radians(28.28)))


def chain_from_junction(ways, start_wid, max_km):
    from collections import defaultdict
    ends = defaultdict(list)
    for wid, w in ways.items():
        ends[w["nodes"][0]].append((wid, 0))
        ends[w["nodes"][-1]].append((wid, -1))
    jlat, jlon = JUNCTION
    dj = lambda p: math.hypot((p["lat"] - jlat) * 111.2,
                              (p["lon"] - jlon) * 111.2 * math.cos(math.radians(jlat)))
    w = ways[start_wid]
    nodes, geom = list(w["nodes"]), list(w["geometry"])
    if dj(geom[-1]) < dj(geom[0]):
        nodes, geom = nodes[::-1], geom[::-1]
    name = w["tags"].get("name:en") or w["tags"].get("name")
    used = {start_wid}
    length = lambda g: sum(dj_pair(a, b) for a, b in zip(g[:-1], g[1:]))
    while length(geom) < max_km:
        cands = [(cw, ce) for cw, ce in ends[nodes[-1]] if cw not in used]
        rivers = [c for c in cands if ways[c[0]]["tags"].get("waterway") == "river"]
        same = [c for c in rivers if (ways[c[0]]["tags"].get("name:en")
                                      or ways[c[0]]["tags"].get("name")) == name]
        cands = same or rivers or cands
        if not cands:
            break
        cw, ce = cands[0]
        used.add(cw)
        nn, gg = list(ways[cw]["nodes"]), list(ways[cw]["geometry"])
        if ce == -1:
            nn, gg = nn[::-1], gg[::-1]
        nodes += nn[1:]
        geom += gg[1:]
    return geom


def local_xy(lat, lon):
    la0, lo0 = JUNCTION
    return ((lon - lo0) * 111320.0 * math.cos(math.radians(la0)),
            (lat - la0) * 110574.0)


def latlon_from_xy(x, y):
    la0, lo0 = JUNCTION
    return (la0 + y / 110574.0, lo0 + x / (111320.0 * math.cos(math.radians(la0))))


def stations():
    geom = chain_from_junction(load_ways(), ARM_WAY, L_ARM_KM + 0.5)
    xy = np.array([local_xy(p["lat"], p["lon"]) for p in geom])
    seg = np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.arange(0.0, min(s[-1], L_ARM_KM * 1000) + 1, STEP_M)
    xs, ys = np.interp(t, s, xy[:, 0]), np.interp(t, s, xy[:, 1])
    # local tangent from +/-2 stations, perpendicular for the transect
    out = []
    for i in range(len(t)):
        i0, i1 = max(i - 2, 0), min(i + 2, len(t) - 1)
        dx, dy = xs[i1] - xs[i0], ys[i1] - ys[i0]
        L = math.hypot(dx, dy) or 1.0
        pe, pn = -dy / L, dx / L
        out.append((t[i] / 1000.0, xs[i], ys[i], pe, pn))
    return out


# ------------------------------------------------------------------ DEM ----
def fetch(st):
    pts = []
    for km, x, y, pe, pn in st:
        for k in range(-HALF_PTS, HALF_PTS + 1):
            d = k * SPACING
            pts.append(latlon_from_xy(x + d * pe, y + d * pn))
    print(f"fetching {len(pts)} DEM samples (Mapzen via OpenTopoData) ...")
    el = []
    for i in range(0, len(pts), 100):
        locs = "|".join(f"{a:.6f},{b:.6f}" for a, b in pts[i:i + 100])
        req = urllib.request.Request("https://api.opentopodata.org/v1/mapzen",
                                     data=json.dumps({"locations": locs}).encode(),
                                     headers={"Content-Type": "application/json"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    d = json.loads(resp.read())
                assert d["status"] == "OK", d
                break
            except Exception as e:
                print(f"   retry {attempt+1}: {e}"); time.sleep(3)
        el.extend(r["elevation"] if r["elevation"] is not None else np.nan
                  for r in d["results"])
        time.sleep(1.2)
    n = 2 * HALF_PTS + 1
    z = np.array(el, float).reshape(len(st), n)
    json.dump({"km": [s[0] for s in st], "x": [s[1] for s in st], "y": [s[2] for s in st],
               "pe": [s[3] for s in st], "pn": [s[4] for s in st],
               "spacing": SPACING, "half_pts": HALF_PTS, "z": z.tolist(),
               "source": "Mapzen terrain tiles via api.opentopodata.org/v1/mapzen (30 m)",
               "datum": f"junction {JUNCTION}"}, open(CACHE, "w"))
    print(f"cached -> {os.path.relpath(CACHE, ROOT)}")
    return z


GLO30 = os.path.join(DATA, "Copernicus_DSM_COG_10_N28_00_E085_00_DEM.tif")


def sample_glo30(st):
    """Sample the transect points from the local Copernicus GLO-30 tile
    (bilinear). Source URL in DATA-SOURCES.md; the tile itself is gitignored."""
    import rasterio
    from rasterio.enums import Resampling
    pts = []
    for km, x, y, pe, pn in st:
        for k in range(-HALF_PTS, HALF_PTS + 1):
            d = k * SPACING
            la, lo = latlon_from_xy(x + d * pe, y + d * pn)
            pts.append((lo, la))
    with rasterio.open(GLO30) as src:
        # bilinear: read a window around the reach once and interpolate
        vals = np.array([v[0] for v in src.sample(pts)], float)
        nod = src.nodata
    if nod is not None:
        vals[vals == nod] = np.nan
    z = vals.reshape(len(st), 2 * HALF_PTS + 1)
    print(f"sampled {z.size} points from Copernicus GLO-30 ({os.path.basename(GLO30)})")
    return z


# ------------------------------------------------------- stage geometry ----
def wet_area(z, eta):
    """Cross-section area (m2) and width (m) below level eta, contiguous span
    through the transect minimum (side gullies excluded)."""
    z = np.where(np.isfinite(z), z, 9999.0)
    imin = int(np.argmin(z))
    if eta <= z[imin]:
        return 0.0, 0.0
    lo = imin
    while lo > 0 and z[lo - 1] < eta:
        lo -= 1
    hi = imin
    while hi < len(z) - 1 and z[hi + 1] < eta:
        hi += 1
    seg = z[lo:hi + 1]
    return float(np.sum(np.maximum(eta - seg, 0.0)) * SPACING), float(len(seg) * SPACING)


def volume_for_surface(km, z, eta_of_x):
    """Integrate area(eta(x)) dx along the arm; returns Mm3, plus per-station
    widths. eta_of_x may be NaN where the surface is below the bed."""
    V, widths = 0.0, []
    for i in range(len(km)):
        eta = eta_of_x[i]
        if not np.isfinite(eta):
            widths.append(0.0); continue
        A, W = wet_area(z[i], eta)
        V += A * STEP_M
        widths.append(W)
    return V / 1e6, np.array(widths)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--dem", default="glo30", choices=["glo30", "mapzen"],
                    help="glo30 = local Copernicus GLO-30 tile (default); mapzen = OpenTopoData cache")
    a, _ = ap.parse_known_args()
    st = stations()
    km = np.array([s[0] for s in st])
    if a.dem == "glo30":
        z = sample_glo30(st)
        DEM_LABEL = "Copernicus GLO-30 (TanDEM-X, 2011-2015, ~30 m, ~2-4 m vertical)"
    elif os.path.exists(CACHE) and not a.refetch:
        c = json.load(open(CACHE))
        z = np.array(c["z"], float)[:len(km)]
        print(f"loaded cached transects ({len(km)} stations) from {os.path.relpath(CACHE, ROOT)}")
        DEM_LABEL = "Mapzen 30 m via OpenTopoData (void-fill artefacts in the gorge)"
    else:
        z = fetch(st)
        DEM_LABEL = "Mapzen 30 m via OpenTopoData (void-fill artefacts in the gorge)"
    n = len(km)
    bed_raw = np.nanmin(z, axis=1)

    # THE DEM IS NOT TRUSTWORTHY STATION BY STATION. In this slot gorge the
    # Mapzen tiles carry void-fill artefacts: at 1.0 km the transect minimum
    # reads 1,977 m against 1,866 m at 2.0 km, and 2,067 m at 4.0 km against
    # 1,913 at 5.0. A river bed rises monotonically up-valley, and a 30 m DEM
    # in a gorge errs HIGH (it fills the slot), so the trustworthy profile is
    # the upstream minimum: bed(x) = min of the raw minima at all x' >= x.
    bed_env = np.minimum.accumulate(bed_raw[::-1])[::-1]
    good = np.abs(bed_raw - bed_env) < 10.0          # stations whose transect hits the floor
    off = bed_env[0] - BED_JUNCTION_GE
    print(f"\nDEM bed at the junction {bed_env[0]:.0f} m vs Google Earth {BED_JUNCTION_GE:.0f} m ({off:+.0f} m)")
    print(f"good stations (transect minimum within 10 m of the envelope): {good.sum()} of {n}")
    slope = (bed_env[-1] - bed_env[0]) / (km[-1] * 1000)

    # per-station depth -> (area, width) tables; a bad station borrows the
    # SHAPE (area and width as functions of depth above its own floor) of the
    # nearest good station
    D = np.arange(0.0, 131.0, 1.0)
    A_tab = np.zeros((n, len(D))); W_tab = np.zeros((n, len(D)))
    good_idx = np.flatnonzero(good)
    src = np.array([i if good[i] else good_idx[np.argmin(np.abs(good_idx - i))] for i in range(n)])
    for i in range(n):
        j = src[i]
        zz = np.where(np.isfinite(z[j]), z[j], 9999.0)
        z0 = float(np.min(zz))
        for k, d in enumerate(D):
            A_tab[i, k], W_tab[i, k] = wet_area(zz, z0 + d)
    def AW(i, d):
        d = float(np.clip(d, 0.0, D[-1]))
        return (float(np.interp(d, D, A_tab[i])), float(np.interp(d, D, W_tab[i])))
    def depth_for_width(i, Wt):
        """smallest depth at which the station's width reaches Wt (m)."""
        k = np.argmax(W_tab[i] >= Wt)
        return float(D[k]) if W_tab[i, k] >= Wt else float(D[-1])

    def integrate(depth):
        """depth[i] above bed_env; NaN = dry. Returns Mm3 and widths."""
        V, W = 0.0, np.zeros(n)
        for i in range(n):
            if np.isfinite(depth[i]) and depth[i] > 0:
                A, W[i] = AW(i, depth[i]); V += A * STEP_M
        return V / 1e6, W

    lines = []
    P = lambda s="": (print(s), lines.append(s))
    P("# Up-valley wedge volume — results (6 Sept 2026, evening)\n")
    P(f"DEM: {DEM_LABEL}; {n} stations at {STEP_M:.0f} m; transects ±{HALF_PTS*SPACING:.0f} m; "
      f"junction datum {JUNCTION}. The bed used is the upstream-minimum envelope of the transect minima (a river bed "
      f"rises monotonically and a 30 m DEM in a gorge errs high), and {n-good.sum()} of {n} stations whose transect "
      f"minimum sits >10 m above the envelope borrow the cross-section shape of their nearest sound neighbour. Bed at the junction {bed_env[0]:.0f} m (Google Earth "
      f"{BED_JUNCTION_GE:.0f}); mean grade to {km[-1]:.0f} km {100*slope:.2f}%.\n")
    P("Bed envelope: " + ", ".join(f"{k:.1f} km {b:.0f} m" for k, b in zip(km[::5], bed_env[::5])) + "\n")
    P("## Where the bed reaches the stagnation level\n")
    P("| level | bed envelope reaches it at | agent's SRTM/ASTER read (dossier 16a) |")
    P("|---|---|---|")
    for L in LEVELS:
        i1 = np.argmax(bed_env >= L) if (bed_env >= L).any() else None
        r1 = f"{km[i1]:.1f} km" if i1 is not None else f">{km[-1]:.1f} km"
        P(f"| {L:.0f} m | {r1} | 1,920–1,930 m met at ~4.5–5 km, ±0.7 km |")
    P("\nDave's Google Earth trace put the 1,920–1,930 m contour at 3.5 km; the imagery limit is 4.6 km "
      "(agent chainage, ~0.4 km longer than ours at the same point).\n")

    results = {}
    # ---- readings of the same mud-line head --------------------------------
    P("## Stored volume at peak, by reading\n")
    P("| reading | surface | volume | width at 1 / 2 / 4 km |")
    P("|---|---|---|---|")
    def w3(W):
        return " / ".join(f"{W[int(np.argmin(np.abs(km-kk)))]:.0f}" for kk in (1.0, 2.0, 4.0)) + " m"
    for L in LEVELS:
        depth = L - bed_env
        stop = np.argmax(bed_env >= L) if (bed_env >= L).any() else n
        depth[stop:] = np.nan
        V, W = integrate(depth); results[("pond", L)] = (V, W, km[min(stop, n-1)])
        P(f"| pond | level {L:.0f} m, to {km[min(stop,n-1)]:.1f} km | **{V:.1f} Mm³** | {w3(W)} |")
    for xe in X_ENDS_KM:
        je = int(np.argmin(np.abs(km - xe))); z_end = bed_env[je]
        for p, shape in ((1, "linear"), (2, "concave, p=2"), (0.5, "convex, p=0.5")):
            eta = np.full(n, np.nan)
            for i in range(je + 1):
                eta[i] = z_end + (1925.0 - z_end) * max(1 - km[i] / xe, 0.0) ** p
            depth = eta - bed_env
            depth[~np.isfinite(depth) | (depth <= 0)] = np.nan
            V, W = integrate(depth); results[("tongue", xe, p)] = (V, W)
            P(f"| tongue, {shape} | 1,925 m at the junction, touching the bed at {xe:.1f} km | **{V:.1f} Mm³** | {w3(W)} |")
    # ---- the reading Dave asked for: imagery area x cross-section -----------
    P("\n## The imagery reading: inundated width from the 0.55 m scenes → depth through the cross-section → volume\n")
    P("Widths read off the Pelican scenes (dossier 16a): 150–250 m across the floor from 0 to 2.5 km, 110–145 m from "
      "3.8 to 4.6 km; 2.5–3.8 km is cloud (interpolated). Each station's cross-section converts a width into the "
      "depth that produces it; the volume is the integral. This is the 2-D area × topography estimate.\n")
    P("| imagery width case | 0–2.5 km width | 3.8–4.6 km width | volume | implied depth at 1 km / 2 km / 4 km |")
    P("|---|---|---|---|---|")
    for lab, wlo, whi in (("low", 150.0, 110.0), ("mid", 200.0, 128.0), ("high", 250.0, 145.0)):
        depth = np.full(n, np.nan)
        for i in range(n):
            x = km[i]
            if x <= 2.5: Wt = wlo
            elif x >= 3.8 and x <= 4.6: Wt = whi
            elif 2.5 < x < 3.8: Wt = wlo + (whi - wlo) * (x - 2.5) / 1.3
            else: continue
            depth[i] = depth_for_width(i, Wt)
        V, W = integrate(depth); results[("img", lab)] = (V, W, depth)
        d3 = " / ".join(f"{depth[int(np.argmin(np.abs(km-kk)))]:.0f}" for kk in (1.0, 2.0, 4.0)) + " m"
        P(f"| {lab} | {wlo:.0f} m | {whi:.0f} m | **{V:.1f} Mm³** | {d3} |")
    P("\nCaveat on the imagery reading: the width on 1 September is the width of the DEPOSIT and stripped ground "
      "left after the water drained, which is a floor on the width the flow reached, not the width at peak; and the "
      "30 m cross-sections are borrowed at the artefact stations. Treat it as a lower-to-middle estimate of the peak "
      "stored volume.\n")
    # ---- width check ----------------------------------------------------------
    P("## Width check: which reading matches the imagery?\n")
    P("| surface | DEM width 0–2.5 km (median) | 3.8–4.6 km (median) | imagery |")
    P("|---|---|---|---|")
    def med(W, a, b):
        m = (km >= a) & (km <= b) & (W > 0)
        return float(np.median(W[m])) if m.any() else float("nan")
    for key, lab in [(("pond", 1925.0), "pond at 1,925 m"), (("pond", 1915.0), "pond at 1,915 m"),
                     (("tongue", 4.6, 1), "tongue to 4.6 km, linear"), (("tongue", 4.6, 2), "tongue to 4.6 km, concave"),
                     (("tongue", 4.6, 0.5), "tongue to 4.6 km, convex"), (("tongue", 3.5, 1), "tongue to 3.5 km, linear")]:
        W = results[key][1]
        P(f"| {lab} | {med(W,0,2.5):.0f} m | {med(W,3.8,4.6):.0f} m | 150–250 / 110–145 m |")
    # ---- deposit ---------------------------------------------------------------
    P("\n## Solids left in the arm (from reported thicknesses; no before/after DEM exists for this reach)\n")
    dep_lo = (1700*150*3.0 + 800*150*1.0 + 800*110*0.5) / 1e6
    dep_hi = (1700*250*5.0 + 800*250*2.0 + 800*145*2.0) / 1e6
    P(f"Bed raised 'nearly 5 m' in the last 1.7 km (CCTV engineers), mud 1–2 m beyond, thin fill at 3.8–4.6 km: "
      f"**{dep_lo:.1f}–{dep_hi:.1f} Mm³ of solids**, i.e. a few per cent of the stored volume — the arm mostly drained.\n")
    # ---- to the node and the release ------------------------------------------
    P("## From stored volume to the volume at the node, and to the release\n")
    brg, spl, fp, fc = split_at_node(800.0, 2)
    up, dn = spl["up-valley (Kyirong)"], spl["downstream (Bhote Koshi)"]
    P("Split at the node from the valley geometry. Curves fitted to the OSM centrelines over 800 m give an "
      f"inflow heading of {brg:.0f}°, a downstream exit on {dn['bearing']:.0f}° ({dn['angle']:.0f}° turn) and an "
      f"up-valley exit on {up['bearing']:.0f}° ({up['angle']:.0f}° turn): momentum projection f_up = {fp:.2f}, cosine "
      f"weighting {fc:.2f}. But centrelines through the VOLUMETRIC middle of each valley (GLO-30 cross-section "
      "centroids at 30–90 m depth; `--volumetric`) show the answer depends on which reach of the Lhende is called "
      "'incoming': its last 500 m bends south toward the downstream exit (turn ~10–20°, up-valley 150–175°, "
      "f_up ≈ 0), while the kilometre above runs west-south-west, at right angles to both exits (turns 85–100° "
      "each way, cosine-weighted f_up 0.35–0.57). A 60–110 m deep flow at 47 m/s does not follow a 500 m bend, "
      "so the truth lies between, and the geometry alone cannot fix it. Bracket used: f_up = 0.10, 0.30, 0.50. "
      "The routing model cannot supply it either: its junction branch is a weir capped at 8 m of driving head "
      "(`model/core.py`). What would: peak-discharge continuity at the node, Q_in = Q_down + Q_up, from trimlines "
      "and superelevation in the reaches just above and just below the junction (`calcs/node_discharge_continuity.py`).\n")
    P(f"Lhende reach contribution subtracted: {LHENDE_CONTRIB_MM3[0]:.0f}–{LHENDE_CONTRIB_MM3[1]:.0f} Mm³ "
      "(0.5 channel water; 2.6–13 entrained bed — the stereo DEM has the gorge floor lowered 2–12 m — plus "
      "whatever of the 2025 outburst deposits it took; ≤1–2.5 melt; dossier 15).\n")
    P("| stored-volume case | V_up | at node, f_up 0.50 | 0.30 | 0.10 | release, f_up 0.50 | 0.30 | 0.10 |")
    P("|---|---|---|---|---|---|---|---|")
    cases = [("imagery widths, low", results[("img","low")][0]),
             ("imagery widths, mid", results[("img","mid")][0]),
             ("imagery widths, high", results[("img","high")][0]),
             ("tongue to 4.6 km, concave", results[("tongue",4.6,2)][0]),
             ("tongue to 4.6 km, linear", results[("tongue",4.6,1)][0]),
             ("tongue to 3.5 km, linear", results[("tongue",3.5,1)][0]),
             ("pond at 1,925 m (over-fills the imagery widths)", results[("pond",1925.0)][0])]
    for lab, Vu in cases:
        node = [Vu / f for f in (0.5, 0.3, 0.1)]
        rel = [f"{max(v-LHENDE_CONTRIB_MM3[1],0):.0f}–{max(v-LHENDE_CONTRIB_MM3[0],0):.0f}" for v in node]
        P(f"| {lab} | {Vu:.1f} | {node[0]:.0f} | {node[1]:.0f} | {node[2]:.0f} | {rel[0]} | {rel[1]} | {rel[2]} |")
    P("\nOur size envelope (finding 04) is 14–34 Mm³, median 21, from the clock, the border speed, the erosion "
      "volume and the deposition cap. None of those enters the table above.\n")
    open(os.path.join(OUT, "upvalley_wedge.md"), "w").write("\n".join(lines) + "\n")

    # ---- figure -----------------------------------------------------------------
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(17, 5.2))
    ax[0].plot(km, bed_raw, color="#bbb", lw=1, label="raw transect minimum (artefacts)")
    ax[0].plot(km, bed_env, color="#22303a", lw=2, label="bed: upstream-minimum envelope")
    ax[0].axhspan(1920, 1930, color="#a5403a", alpha=0.15, label="impact-cliff mud line 1,920–1,930 m")
    for key, lab, c in [(("tongue",4.6,1), "tongue to 4.6 km, linear", "#1e5f8e"), (("tongue",4.6,2), "concave", "#7fb3cf")]:
        pass
    je = int(np.argmin(np.abs(km-4.6))); z_end = bed_env[je]
    for p, c, lab in ((1, "#1e5f8e", "tongue, linear"), (2, "#7fb3cf", "tongue, concave"), (0.5, "#164a70", "tongue, convex")):
        eta = [z_end + (1925-z_end)*max(1-x/4.6,0)**p for x in km[:je+1]]
        ax[0].plot(km[:je+1], eta, color=c, lw=1.2, ls="--", label=lab)
    dimg = results[("img","mid")][2]
    ax[0].plot(km, bed_env + np.nan_to_num(dimg, nan=0.0) * np.where(np.isfinite(dimg), 1, np.nan), color="#1baf7a", lw=2, label="surface implied by imagery widths (mid)")
    ax[0].set_ylim(1780, 1990); ax[0].set_xlabel("km up the Kyirong arm from the junction"); ax[0].set_ylabel("m a.s.l.")
    ax[0].set_title("Bed and candidate peak surfaces"); ax[0].legend(fontsize=7.5)
    for key, lab, c in [(("pond",1925.0), "pond 1,925 m", "#a5403a"), (("tongue",4.6,1), "tongue 4.6 km linear", "#1e5f8e"),
                        (("tongue",4.6,2), "tongue 4.6 km concave", "#7fb3cf"), (("img","mid"), "imagery mid", "#1baf7a")]:
        ax[1].plot(km, results[key][1], label=lab, color=c)
    for a0, a1, lo, hi in IMG_WIDTHS:
        ax[1].fill_between([a0, a1], lo, hi, color="#1baf7a", alpha=0.2)
    ax[1].set_xlabel("km up the arm"); ax[1].set_ylabel("wetted width, m"); ax[1].set_ylim(0, 700)
    ax[1].set_title("Width of each surface vs the imagery (green bands)"); ax[1].legend(fontsize=8)
    labs = [c[0] for c in cases]; vals = [c[1] for c in cases]
    ax[2].barh(range(len(cases)), vals, color="#1e5f8e"); ax[2].set_yticks(range(len(cases))); ax[2].set_yticklabels(labs, fontsize=7.5)
    ax[2].set_xlabel("stored volume up the arm, Mm³"); ax[2].set_title("Stored volume by reading"); ax[2].invert_yaxis()
    fig.suptitle("Up-valley wedge on a 30 m DEM with artefacts: brackets, not point values", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "upvalley_wedge.png"), dpi=130)
    print("\nwrote output/upvalley_wedge.md and output/upvalley_wedge.png")




# ------------------------------------------------------------------------------
# THE SPLIT AT THE NODE FROM THE VALLEY GEOMETRY (Dave, 6 Sept evening):
# fit smooth curves to the middle of each arm near the junction, take the
# tangent directions where they meet, and project the incoming momentum.
# ------------------------------------------------------------------------------
ARMS_AT_NODE = {"up-valley (Kyirong)": 904894054, "Lhende (inflow)": 937405875,
                "downstream (Bhote Koshi)": 201928141}


def arm_tangent_at_junction(way_id, fit_m=800.0, deg=2):
    """Least-squares polynomial through the first fit_m of the arm's OSM
    centreline (local metres, parameterised by along-distance); returns the
    unit tangent AT the junction pointing AWAY from it, and the bearing."""
    geom = chain_from_junction(load_ways(), way_id, 3.0)
    xy = np.array([local_xy(p["lat"], p["lon"]) for p in geom])
    seg = np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    m = s <= fit_m
    cx = np.polyfit(s[m], xy[m, 0], deg); cy = np.polyfit(s[m], xy[m, 1], deg)
    tx, ty = np.polyval(np.polyder(cx), 0.0), np.polyval(np.polyder(cy), 0.0)
    L = math.hypot(tx, ty)
    tx, ty = tx / L, ty / L
    return (tx, ty), (math.degrees(math.atan2(tx, ty)) % 360)


def split_at_node(fit_m=800.0, deg=2):
    t = {k: arm_tangent_at_junction(w, fit_m, deg) for k, w in ARMS_AT_NODE.items()}
    # incoming momentum direction = the Lhende's tangent REVERSED (it points away
    # from the junction, the flow comes toward it)
    inx, iny = -t["Lhende (inflow)"][0][0], -t["Lhende (inflow)"][0][1]
    out = {}
    for k in ("up-valley (Kyirong)", "downstream (Bhote Koshi)"):
        ex, ey = t[k][0]
        cos = inx * ex + iny * ey
        out[k] = dict(bearing=t[k][1], angle=math.degrees(math.acos(max(-1, min(1, cos)))), cos=cos)
    inflow_brg = (math.degrees(math.atan2(inx, iny)) % 360)
    # two simple partition rules, both bracketing the truth rather than giving it
    pos = {k: max(v["cos"], 0.0) for k, v in out.items()}          # momentum projection
    cw = {k: (1 + v["cos"]) / 2 for k, v in out.items()}           # cosine-weighted
    f_proj = pos["up-valley (Kyirong)"] / max(sum(pos.values()), 1e-9)
    f_cw = cw["up-valley (Kyirong)"] / sum(cw.values())
    return inflow_brg, out, f_proj, f_cw


if __name__ == "__main__" and "--volumetric" not in sys.argv:
    print("\nSPLIT AT THE NODE from spline-fitted centreline tangents")
    for fit_m, deg in ((400.0, 1), (800.0, 2), (1200.0, 2), (1200.0, 3)):
        brg, out, fp, fc = split_at_node(fit_m, deg)
        up, dn = out["up-valley (Kyirong)"], out["downstream (Bhote Koshi)"]
        print(f"  fit {fit_m:5.0f} m, degree {deg}: inflow heading {brg:5.1f}°; up-valley exit {up['bearing']:5.1f}° "
              f"(turn {up['angle']:5.1f}°), downstream exit {dn['bearing']:5.1f}° (turn {dn['angle']:5.1f}°) "
              f"-> f_up by momentum projection {fp:.2f}, by cosine weighting {fc:.2f}")
    main()


# ------------------------------------------------------------------------------
# VOLUMETRIC CENTRELINES (Dave, 6 Sept late): the OSM river line hugs the
# low-flow channel and wiggles. The flow that mattered was 60-110 m deep and
# filled the valley, so the direction that matters is the middle of the
# VALLEY at that stage. For each arm: cut GLO-30 cross-sections every 50 m for
# 1.5 km from the junction, find the centroid of the wetted section at a
# reference depth above the local bed, string those centroids into a line,
# fit a quadratic through the first fit_m metres, and take the tangent at the
# junction. Then the split, as before.
# ------------------------------------------------------------------------------
def arm_stations(way_id, L_km=1.5, step=50.0):
    geom = chain_from_junction(load_ways(), way_id, L_km + 0.5)
    xy = np.array([local_xy(p["lat"], p["lon"]) for p in geom])
    seg = np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.arange(0.0, min(s[-1], L_km * 1000) + 1, step)
    xs, ys = np.interp(t, s, xy[:, 0]), np.interp(t, s, xy[:, 1])
    out = []
    for i in range(len(t)):
        i0, i1 = max(i - 2, 0), min(i + 2, len(t) - 1)
        dx, dy = xs[i1] - xs[i0], ys[i1] - ys[i0]
        L = math.hypot(dx, dy) or 1.0
        out.append((t[i] / 1000.0, xs[i], ys[i], -dy / L, dx / L))
    return out


def volumetric_centreline(way_id, depth_ref, L_km=1.5, step=50.0):
    """Centroid of the wetted cross-section at depth_ref above the station's
    own floor (upstream-minimum envelope along the arm), in local xy."""
    st = arm_stations(way_id, L_km, step)
    z = sample_glo30(st)
    bed = np.nanmin(z, axis=1)
    bed = np.minimum.accumulate(bed[::-1])[::-1]        # rises away from the junction
    offs = (np.arange(-HALF_PTS, HALF_PTS + 1)) * SPACING
    pts, along = [], []
    for i, (km, x, y, pe, pn) in enumerate(st):
        zz = np.where(np.isfinite(z[i]), z[i], 9999.0)
        eta = bed[i] + depth_ref
        imin = int(np.argmin(zz))
        lo = imin
        while lo > 0 and zz[lo - 1] < eta: lo -= 1
        hi = imin
        while hi < len(zz) - 1 and zz[hi + 1] < eta: hi += 1
        d = np.maximum(eta - zz[lo:hi + 1], 0.0)
        if d.sum() <= 0: continue
        c = float(np.sum(offs[lo:hi + 1] * d) / d.sum())
        pts.append((x + c * pe, y + c * pn)); along.append(km * 1000)
    return np.array(pts), np.array(along)


def volumetric_split(depth_ref=60.0, fit_m=800.0, deg=2):
    tang, brg = {}, {}
    for k, w in ARMS_AT_NODE.items():
        P_, s = volumetric_centreline(w, depth_ref)
        m = s <= fit_m
        cx = np.polyfit(s[m], P_[m, 0], deg); cy = np.polyfit(s[m], P_[m, 1], deg)
        tx, ty = np.polyval(np.polyder(cx), 0.0), np.polyval(np.polyder(cy), 0.0)
        L = math.hypot(tx, ty); tang[k] = (tx / L, ty / L)
        brg[k] = math.degrees(math.atan2(tx, ty)) % 360
    inx, iny = -tang["Lhende (inflow)"][0], -tang["Lhende (inflow)"][1]
    res = {}
    for k in ("up-valley (Kyirong)", "downstream (Bhote Koshi)"):
        c = inx * tang[k][0] + iny * tang[k][1]
        res[k] = dict(bearing=brg[k], turn=math.degrees(math.acos(max(-1, min(1, c)))), cos=c)
    pos = {k: max(v["cos"], 0) for k, v in res.items()}
    cw = {k: (1 + v["cos"]) / 2 for k, v in res.items()}
    f_proj = pos["up-valley (Kyirong)"] / max(sum(pos.values()), 1e-9)
    f_cw = cw["up-valley (Kyirong)"] / sum(cw.values())
    return (math.degrees(math.atan2(inx, iny)) % 360), res, f_proj, f_cw


if __name__ == "__main__" and "--volumetric" in sys.argv:
    print("\nVOLUMETRIC-CENTRELINE SPLIT (GLO-30 cross-section centroids, quadratic fit)")
    for depth_ref in (30.0, 60.0, 90.0):
        for fit_m in (500.0, 800.0, 1200.0):
            try:
                brg, res, fp, fc = volumetric_split(depth_ref, fit_m, 2)
            except Exception as e:
                print(f"  depth {depth_ref:.0f} m fit {fit_m:.0f} m: failed ({e})"); continue
            up, dn = res["up-valley (Kyirong)"], res["downstream (Bhote Koshi)"]
            print(f"  depth {depth_ref:3.0f} m, fit {fit_m:5.0f} m: inflow {brg:5.1f}°; up-valley exit {up['bearing']:5.1f}° "
                  f"(turn {up['turn']:5.1f}°), downstream {dn['bearing']:5.1f}° (turn {dn['turn']:5.1f}°) "
                  f"-> f_up projection {fp:.2f}, cosine {fc:.2f}")
    sys.exit(0)
