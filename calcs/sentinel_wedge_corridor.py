#!/usr/bin/env python3
"""
Sentinel-2 CORRIDOR test of the up-valley wedge: measure along the river,
not in angular sectors.

WHY THIS EXISTS. sentinel_wedge.py asked "did the 26 Aug flow actually go up
the Kyirong arm above the border junction?" and answered it by comparing
bare-ground area (NDVI < 0.20) after/before in 0.5 km distance bands cut into
angular sectors around the junction. That found the up-valley arm widening
x2.5 at the junction, tapering to x1.1 by 3.5 km, while the two through-flow
arms stayed wide for 5-7 km. The weakness is the sector: at 3 km radius a
sector is a wedge several hundred metres wide that averages the valley floor
in with the hillsides either side of it, and where the arm bends the sector
walks off the river altogether. This script replaces the sectors with a
corridor of +/-150 m either side of the OSM river centreline (sensitivity
+/-100 and +/-250 m), binned every 250 m by distance ALONG the centreline
from the junction, and reports for every bin: pixels valid in both epochs,
bare fraction before and after, the after/before bare-area ratio, and the
mean NDVI change, each beside a hillside band 300-600 m from the same
centreline that serves as the local null. The downstream (Bhote Koshi) arm
is the positive control, as in the original.

INPUTS (nothing is re-downloaded).
  output/wedge_ndvi_pre.npy   NDVI, S2C 12 Aug 2026, one clear scene
  output/wedge_ndvi_post.npy  NDVI, per-pixel median of 27 Aug - 3 Sept 2026
  data/osm_rivers.json        Overpass waterways; the three arms are chained
                              from the shared junction node by node id
                              (Gyirong Zangbo / Kyirong Tsangpo up-valley,
                              Lende Khola, Bhote Koshi downstream)

GEOREFERENCING. sentinel_wedge.py did not save the affine transform. It is
reproduced by re-running its STAC search, opening the 12 Aug red-band COG
and rebuilding the same bbox window. That window has fractional offsets
(col 3124.73, row 5289.07, size 1990.43 x 2242.43); GDAL served it as a
1990 x 2242 array by nearest-neighbour sampling from the ROUNDED origin
(col 3125, row 5289) - verified pixel-for-pixel against integer-window reads
(every column maps to source column 3125+i; rows map to 5289+j except the
last ~12 rows, which map to 5290+j). So the array origin is (331250 E,
3147150 N) in EPSG:32645 with exact 10 m pixels, good to one pixel. The saved
pre array reproduces bit-for-bit from the 12 Aug scene, so it is that single
scene, not a composite. If the network is down the recovered transform is
read from output/wedge_transform.json, written on the first successful run.

RULES SET BEFORE THE NUMBERS WERE LOOKED AT (do not move them afterwards).
  * bare = NDVI < 0.20, as in sentinel_wedge.py.
  * a bin counts only if >= 30 % of its corridor pixels are valid in both
    epochs and it has >= 20 bare pixels before; otherwise "n/a".
  * "widening ends" = first distance from which the after/before ratio
    stays <= 1.10 for two consecutive counted bins.
  * "NDVI change back to background" = first distance from which the
    corridor's excess NDVI change over its own hillside band stays within
    2 sd of the hillside-band bin means (all arms pooled) for two
    consecutive counted bins.
  * the first 0.75 km of every arm sits inside the junction fan where the
    three corridors overlap; those bins are reported but not used to place
    an end-point.

WHAT IT FOUND (6 Sept 2026 run, +/-150 m; RESULTS.md has every bin).
  Up-valley (Kyirong) arm: the stripped strip is unambiguous to 2.0 km.
  Bare fraction 44 -> 91 % in the first 0.5 km, 29 -> 63 % at 0.75-1 km,
  15 -> 28 % at 1.75-2 km (after/before 1.9-2.4, NDVI excess over the
  hillside band -0.07 to -0.31). It then tapers: ratio 1.59 at 2.0-2.25 km,
  1.22 and 1.18 at 2.25-2.75 km (10-15 m of added bare width across a 300 m
  corridor), 1.42 at 2.75-3.0 km on 51 % coverage, unresolved at 3.0-3.25 km
  (8 % coverage), then 0.98 and 1.06 at 3.25-3.75 km. By the fixed rules the
  NDVI excess is back inside the hillside noise (2 sd = 0.093) from
  2.0-2.25 km, and the ratio is <= 1.1 from 3.25-3.5 km at all three corridor
  widths (the NDVI rule moves between 1.25 and 2.5 km with width, the ratio
  rule does not move). A straight line through the added bare width from
  0.75 to 3.0 km (101 m -> 41 m -> 10 m) reaches zero at 2.8-2.9 km. So the
  signal ends between 2.25 and 3.5 km and cannot be placed more finely,
  because the 3.0-3.25 km bin is cloud-masked; it is a taper, not a strip
  that stops. One later bin, 3.75-4.0 km, has ratio 1.52, but its own
  hillside band darkened by -0.10 in the same bin, so it reads as composite
  residue rather than flood; beyond 4.25 km every bin is 0.91-1.03.
  Lhende (source) arm: ratio 2.9-6.4 and NDVI excess -0.23 to -0.43 over
  the whole 6 km; never returns to background.
  Downstream control: the array ends 5.25 km below the junction; ratio
  1.3-2.8 (16 of 18 bins beyond the fan >= 1.44) and NDVI excess -0.09 to
  -0.34 the whole way; the ratio rule never fires. The NDVI rule does fire
  at 2.5-2.75 km, where the excess dips to -0.09 and -0.03 for two bins
  before the signal resumes at -0.21 to -0.31, so that rule can be tripped
  by a local dip and the ratio rule is the sturdier of the two.
  Nulls: hillside-band NDVI change is -0.005 +/- 0.047 per bin. Hillside
  bins rarely hold 20 bare pixels, so the ratio null rests on 13 bins:
  median 1.00, 10-90 % range 0.86-1.50, i.e. single-bin ratios up to ~1.5
  occur on ground that was not flooded.
  Coverage: the post composite is cloud-masked over 57 % of the AOI; the
  up-valley corridor bins are 95-100 % both-valid to 2.5 km, then 51, 8,
  70, 65 and 85 % from 2.75 to 4.0 km, and >= 95 % beyond. The downstream
  arm leaves the array at 5.3 km, so that control is 5.25 km long, not 8.
  Against the original sectors (x1.1 by 3.5 km): same end-point by the
  rule, but the corridor resolves the taper - full-strength to 2 km,
  marginal from 2.25 km - which the sectors could not.
"""
import argparse, csv, json, math, os, sys, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "output")
DATA = os.path.join(ROOT, "data")

JUNCTION = (28.2781, 85.3770)                 # lat, lon (border junction)
BBOX = [85.28, 28.24, 85.48, 28.44]           # identical to sentinel_wedge.py
STAC = "https://earth-search.aws.element84.com/v1/search"
BARE = 0.20                                    # NDVI threshold, as before
BIN_M = 250.0
HALF_WIDTHS = (150.0, 100.0, 250.0)            # first one is the headline
HILL_BAND = (300.0, 600.0)                     # hillside null, m off centreline
MIN_COV, MIN_BARE_PRE = 0.30, 20
OVERLAP_KM = 0.75                              # junction fan, not used for ends
ARMS = [  # label, OSM way at the junction, length analysed (km)
    ("up-valley (Kyirong Tsangpo)", 904894054, 8.0),
    ("Lhende Khola (source side)", 937405875, 6.0),
    ("downstream (Bhote Koshi)", 201928141, 8.0),
]
COLORS = {0: "#2a78d6", 1: "#eb6834", 2: "#1baf7a"}   # fixed categorical order


READING = """## Reading of the tables (written from the 6 Sept 2026 run; a re-run reprints it unchanged)

* Up-valley arm. The strip is unambiguous to 2.0 km (ratio 1.9-2.4, bare
  fraction roughly doubled, NDVI excess -0.07 to -0.31, added bare width
  140 m at the junction falling to 40 m at 2 km). From 2.25 km the ratio is
  1.2 with 10-15 m of added width - a residual that is inside the 0.86-1.50
  range unflooded hillside bins produce - and by 3.25-3.75 km it is 0.98-1.06.
  The 2.75-3.0 km bin (1.42, 51 % coverage) and the masked 3.0-3.25 km bin are
  why the ratio rule fires only at 3.25-3.5 km; the NDVI-excess rule fires at
  2.0-2.25 km. The added-width taper is close to linear and its straight-line
  zero is 2.8-2.9 km. Honest statement: full-strength stripping to 2 km, a
  taper to nothing somewhere between 2.25 and 3.5 km, position within that
  band not resolvable with this composite. The 3.75-4.0 km bin (ratio 1.52)
  sits on a hillside band that darkened -0.10 in the same bin and is read as
  composite residue, not flood; beyond 4.25 km every bin is 0.91-1.03.
* Controls. Downstream (positive control, 5.25 km to the array edge): ratio
  1.3-2.8, NDVI excess -0.09 to -0.34, never satisfies the ratio rule. The
  NDVI rule does fire on it at 2.5-2.75 km because of a two-bin dip after
  which the signal resumes, which shows that rule can be tripped by a local
  dip; the ratio rule is the sturdier of the two. Lhende (source side): ratio
  2.9-6.4 and excess -0.23 to -0.43 the whole 6 km.
* Against the 1,920-1,930 m contour (~3.5 km): the stripping does not run at
  full strength to 3.5 km. Whether a wedge that tapers to zero near 3 km is
  the same thing as "the contour" is a physics question this test does not
  answer; the data say the stripped width declines roughly linearly from the
  junction and is indistinguishable from unflooded ground by 3.25 km.
* Caveats carried: 57 % of the AOI is cloud-masked in the post composite and
  the up-valley bins between 2.75 and 4.0 km have 8-85 % coverage; the SCL
  mask does not remove terrain shadow (it largely cancels in the NDVI
  difference, not in the bare threshold); the first 0.75 km of each arm is
  the junction fan where the corridors overlap (overlap column); the OSM
  centreline is the pre-event channel, so an avulsion wider than the
  half-width would leave the corridor - the +/-250 m run gives the same
  end-point; the hillside "hill after/before" column is n/a wherever the
  band has fewer than 20 bare pixels before, which is most bins.
"""


# --------------------------------------------------------------------------
# 1. georeferencing
# --------------------------------------------------------------------------
def search(dt, max_cloud=90):
    q = {"collections": ["sentinel-2-c1-l2a"], "bbox": BBOX,
         "datetime": dt, "limit": 50,
         "query": {"eo:cloud_cover": {"lt": max_cloud}}}
    req = urllib.request.Request(STAC, data=json.dumps(q).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["features"]


def recover_transform(shape):
    """Rebuild the window sentinel_wedge.py read, from the same STAC search.

    Returns (Affine, crs_string, note). Header reads only - no pixel data."""
    cache = os.path.join(OUT, "wedge_transform.json")
    try:
        import rasterio
        from rasterio.warp import transform_bounds
        from rasterio.windows import from_bounds
        from affine import Affine
        pre = search("2026-08-01T00:00:00Z/2026-08-26T00:00:00Z")
        best = sorted(pre, key=lambda s: s["properties"]["eo:cloud_cover"])[0]
        with rasterio.open(best["assets"]["red"]["href"]) as src:
            l, b, r, t = transform_bounds("EPSG:4326", src.crs, *BBOX)
            win = from_bounds(l, b, r, t, src.transform)
            frac_tr = src.window_transform(win)
            crs = str(src.crs)
            # GDAL sampled the fractional window from the ROUNDED offsets
            # (verified empirically, see docstring); lengths truncate.
            col0, row0 = int(round(win.col_off)), int(round(win.row_off))
            n = (int(win.height), int(win.width))
            tr = src.transform * Affine.translation(col0, row0)
        note = (f"pre scene {best['id']} ({best['properties']['datetime'][:10]}, "
                f"{best['properties']['eo:cloud_cover']:.1f}% cloud); window "
                f"col_off {win.col_off:.2f} row_off {win.row_off:.2f} "
                f"{win.width:.2f}x{win.height:.2f} -> array {n[1]}x{n[0]}; "
                f"fractional-origin transform would be "
                f"({frac_tr.c:.2f}, {frac_tr.f:.2f}); using rounded origin "
                f"({tr.c:.0f}, {tr.f:.0f})")
        if n != tuple(shape):
            note += f"; WARNING window shape {n} != saved array shape {shape}"
        json.dump({"transform": list(tr)[:6], "crs": crs, "shape": list(n),
                   "note": note}, open(cache, "w"), indent=1)
        return tr, crs, note
    except Exception as e:
        if os.path.exists(cache):
            c = json.load(open(cache))
            from affine import Affine
            return (Affine(*c["transform"]), c["crs"],
                    c["note"] + f" [from cache; live recovery failed: {e}]")
        sys.exit(f"cannot recover transform and no cache: {e}")


def to_utm(lons, lats, crs):
    from rasterio.warp import transform as rtransform
    xs, ys = rtransform("EPSG:4326", crs, list(lons), list(lats))
    return np.asarray(xs), np.asarray(ys)


# --------------------------------------------------------------------------
# 2. river centrelines from OSM, chained from the junction node
# --------------------------------------------------------------------------
def load_ways():
    d = json.load(open(os.path.join(DATA, "osm_rivers.json")))
    return {e["id"]: e for e in d["elements"] if e["type"] == "way"}


def chain_from_junction(ways, start_wid, max_km):
    """Walk ways end-to-end by shared node id, starting at the junction end
    of start_wid, preferring waterway=river and the same name at forks."""
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
    used, chain = {start_wid}, [(start_wid, name)]
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
        chain.append((cw, ways[cw]["tags"].get("name:en") or ways[cw]["tags"].get("name")))
    return geom, chain


def dj_pair(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111.2,
                      (a["lon"] - b["lon"]) * 111.2 * math.cos(math.radians(28.28)))


def densify(xs, ys, step=10.0):
    """Resample a polyline to ~step m spacing; return x, y, along-distance."""
    seg = np.hypot(np.diff(xs), np.diff(ys))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.arange(0.0, s[-1], step)
    return np.interp(t, s, xs), np.interp(t, s, ys), t


# --------------------------------------------------------------------------
# 3. distance of every pixel to each centreline (chunked brute force; no scipy)
# --------------------------------------------------------------------------
def nearest_on_line(px, py, lx, ly, ls, pad):
    """For pixel centres (px, py) [1-D], nearest vertex of (lx, ly): returns
    distance and along-distance arrays. Pixels outside the padded bbox of
    the line get inf / nan without being evaluated."""
    n = px.size
    dist = np.full(n, np.inf, dtype="float32")
    along = np.full(n, np.nan, dtype="float32")
    inbox = ((px >= lx.min() - pad) & (px <= lx.max() + pad) &
             (py >= ly.min() - pad) & (py <= ly.max() + pad))
    idx = np.flatnonzero(inbox)
    lx64, ly64 = lx.astype("float64"), ly.astype("float64")
    for k in range(0, idx.size, 4000):
        ii = idx[k:k + 4000]
        dx = px[ii, None] - lx64[None, :]
        dy = py[ii, None] - ly64[None, :]
        d2 = dx * dx + dy * dy
        j = np.argmin(d2, axis=1)
        dist[ii] = np.sqrt(d2[np.arange(ii.size), j])
        along[ii] = ls[j]
    return dist, along


# --------------------------------------------------------------------------
# 4. per-bin statistics
# --------------------------------------------------------------------------
def bin_stats(sel, along, pre, post, nbins):
    """sel: boolean mask of pixels belonging to this corridor (or band).
    Returns dict of arrays indexed by bin."""
    b = np.floor(along[sel] / BIN_M).astype(int)
    ok = (b >= 0) & (b < nbins)
    b = b[ok]
    p, q = pre[sel][ok], post[sel][ok]
    valid = np.isfinite(p) & np.isfinite(q)
    out = {k: np.zeros(nbins) for k in
           ("n_pix", "n_valid", "bare_pre", "bare_post", "sum_d")}
    np.add.at(out["n_pix"], b, 1)
    np.add.at(out["n_valid"], b[valid], 1)
    np.add.at(out["bare_pre"], b[valid & (p < BARE)], 1)
    np.add.at(out["bare_post"], b[valid & (q < BARE)], 1)
    np.add.at(out["sum_d"], b[valid], (q - p)[valid])
    with np.errstate(all="ignore"):
        out["cov"] = out["n_valid"] / out["n_pix"]
        out["frac_pre"] = out["bare_pre"] / out["n_valid"]
        out["frac_post"] = out["bare_post"] / out["n_valid"]
        out["ratio"] = out["bare_post"] / out["bare_pre"]
        out["mean_d"] = out["sum_d"] / out["n_valid"]
    return out


def first_sustained(dist_km, cond, counted, start_km):
    """First bin distance >= start_km from which cond holds for two
    consecutive COUNTED bins (uncounted bins are skipped, not broken)."""
    idx = [i for i in range(len(dist_km)) if counted[i] and dist_km[i] >= start_km]
    for a, b in zip(idx[:-1], idx[1:]):
        if cond[a] and cond[b]:
            return dist_km[a]
    return None


def run(hw, pre, post, px, py, lines, nbins_of, shape):
    """Assign pixels to corridors (nearest arm wins), compute per-bin tables
    for corridor and hillside band. Returns list of per-arm dicts."""
    D = np.stack([l["dist"] for l in lines])          # (3, npix)
    nearest = np.argmin(D, axis=0)
    dmin = D.min(axis=0)
    res = []
    for k, l in enumerate(lines):
        nb = nbins_of[k]
        corr = (nearest == k) & (l["dist"] <= hw)
        other = np.delete(D, k, axis=0).min(axis=0)
        overlap = corr & (other <= hw)
        band = ((l["dist"] > HILL_BAND[0]) & (l["dist"] <= HILL_BAND[1]) &
                (other > HILL_BAND[0]))
        c = bin_stats(corr, l["along"], pre, post, nb)
        o = bin_stats(overlap, l["along"], pre, post, nb)
        h = bin_stats(band, l["along"], pre, post, nb)
        with np.errstate(all="ignore"):
            c["overlap_frac"] = o["n_pix"] / c["n_pix"]
            # extra bare width averaged over the bin, in metres: the same
            # two columns (bare fraction after - before) times corridor width.
            # Unlike the ratio it does not blow up where little was bare before.
            c["added_w"] = (c["frac_post"] - c["frac_pre"]) * 2 * hw
        c["hill"] = h
        c["mask"] = corr.reshape(shape)
        c["dist_km"] = (np.arange(nb) + 0.5) * BIN_M / 1000.0
        c["counted"] = (c["cov"] >= MIN_COV) & (c["bare_pre"] >= MIN_BARE_PRE)
        res.append(c)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=os.path.join(OUT, "wedge_corridor"),
                    help="where RESULTS.md and the per-bin CSV go")
    args = ap.parse_args()
    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    pre = np.load(os.path.join(OUT, "wedge_ndvi_pre.npy"))
    post = np.load(os.path.join(OUT, "wedge_ndvi_post.npy"))
    assert pre.shape == post.shape
    shape = pre.shape
    print(f"arrays {shape[1]}x{shape[0]} px; pre valid {100*np.isfinite(pre).mean():.1f}%, "
          f"post valid {100*np.isfinite(post).mean():.1f}%, both "
          f"{100*(np.isfinite(pre)&np.isfinite(post)).mean():.1f}%")

    tr, crs, note = recover_transform(shape)
    print("georeferencing:", note)
    a, e, c0, f0 = tr.a, tr.e, tr.c, tr.f
    cols, rows = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    px = (c0 + (cols.ravel() + 0.5) * a).astype("float64")
    py = (f0 + (rows.ravel() + 0.5) * e).astype("float64")
    jx, jy = to_utm([JUNCTION[1]], [JUNCTION[0]], crs)
    jx, jy = float(jx[0]), float(jy[0])
    jc, jr = (jx - c0) / a, (jy - f0) / e
    print(f"junction at UTM ({jx:.0f}, {jy:.0f}) = array col {jc:.1f} row {jr:.1f}")

    ways = load_ways()
    lines, nbins_of = [], []
    for k, (label, wid, Lkm) in enumerate(ARMS):
        geom, chain = chain_from_junction(ways, wid, Lkm + 1.0)
        lon = [p["lon"] for p in geom]
        lat = [p["lat"] for p in geom]
        xs, ys = to_utm(lon, lat, crs)
        lx, ly, ls = densify(xs, ys, 10.0)
        # analyse only to Lkm, but keep 1 km more of line so that the
        # nearest-vertex search does not snap end-of-line pixels onto the arm
        keep = ls <= (Lkm + 1.0) * 1000
        lx, ly, ls = lx[keep], ly[keep], ls[keep]
        inside = ((lx >= c0) & (lx <= c0 + shape[1] * a) &
                  (ly <= f0) & (ly >= f0 + shape[0] * e))
        L_in = ls[inside].max() / 1000 if inside.any() else 0.0
        L_use = min(Lkm, L_in)
        nb = int(math.floor(L_use * 1000 / BIN_M))
        print(f"arm {k} {label}: chained {[c[0] for c in chain]} "
              f"{[c[1] for c in chain]}; line {ls[-1]/1000:.2f} km; inside the "
              f"array to {L_in:.2f} km; analysing {nb} bins to {nb*BIN_M/1000:.2f} km")
        dist, along = nearest_on_line(px, py, lx, ly, ls, HILL_BAND[1] + 100)
        lines.append({"label": label, "lx": lx, "ly": ly, "ls": ls,
                      "dist": dist, "along": along, "L_use": L_use})
        nbins_of.append(nb)

    # hillside null: sd of per-bin hillside means, all arms pooled
    results = {}
    for hw in HALF_WIDTHS:
        results[hw] = run(hw, pre.ravel(), post.ravel(), px, py, lines,
                          nbins_of, shape)
    R = results[HALF_WIDTHS[0]]
    hill_means = np.concatenate([r["hill"]["mean_d"][np.isfinite(r["hill"]["mean_d"])
                                                    & (r["hill"]["n_valid"] >= 50)]
                                 for r in R])
    hill_sd = float(np.std(hill_means))
    hill_mean = float(np.mean(hill_means))
    both = np.isfinite(pre) & np.isfinite(post)
    far = (np.stack([l["dist"] for l in lines]).min(axis=0) > HILL_BAND[0]).reshape(shape)
    global_bg = float(np.nanmean((post - pre)[both & far]))
    print(f"\nhillside band (300-600 m) per-bin mean NDVI change: mean {hill_mean:+.3f}, "
          f"sd {hill_sd:.3f} over {hill_means.size} bins; all pixels > 300 m from "
          f"any arm: {global_bg:+.3f}")

    # ----- end-points per arm, per half-width
    ends = {}
    for hw, RR in results.items():
        for k, r in enumerate(RR):
            d = r["dist_km"]
            excess = r["mean_d"] - r["hill"]["mean_d"]
            counted = r["counted"] & np.isfinite(excess) & (r["hill"]["n_valid"] >= 50)
            e_ratio = first_sustained(d, r["ratio"] <= 1.10, r["counted"], OVERLAP_KM)
            e_ndvi = first_sustained(d, np.abs(excess) <= 2 * hill_sd, counted, OVERLAP_KM)
            ends[(hw, k)] = (e_ratio, e_ndvi)

    # ----- print + write tables
    lines_md = []
    P = lines_md.append
    P("# Corridor test of the up-valley wedge - results\n")
    P(f"Arrays {shape[1]}x{shape[0]} px at 10 m, EPSG:32645, origin "
      f"({c0:.0f}, {f0:.0f}). {note}\n")
    P(f"Pre = S2 12 Aug 2026 single scene; post = median composite 27 Aug - 3 Sept. "
      f"Both-valid coverage over the whole AOI {100*both.mean():.1f} %.\n")
    P(f"Bare = NDVI < {BARE}. Bins {BIN_M:.0f} m along the OSM centreline from the "
      f"junction. A bin is COUNTED if both-valid coverage >= {100*MIN_COV:.0f} % and "
      f">= {MIN_BARE_PRE} bare pixels before; the first {OVERLAP_KM} km is the "
      f"junction fan (corridors overlap) and is never used to place an end-point. "
      f"Hillside band = {HILL_BAND[0]:.0f}-{HILL_BAND[1]:.0f} m off the same "
      f"centreline, clear of the other arms.\n")
    P(f"Hillside null: per-bin mean NDVI change in the band, all arms pooled: "
      f"{hill_mean:+.3f} +/- {hill_sd:.3f} (1 sd, n={hill_means.size} bins); all "
      f"both-valid pixels > {HILL_BAND[0]:.0f} m from any arm: {global_bg:+.3f}.\n")
    hill_ratios = np.concatenate([r["hill"]["ratio"][np.isfinite(r["hill"]["ratio"])
                                                     & (r["hill"]["bare_pre"] >= MIN_BARE_PRE)]
                                  for r in R])
    P(f"Hillside null for the ratio: bare area after/before in the band, bins with >= "
      f"{MIN_BARE_PRE} bare px before: median {np.median(hill_ratios):.2f}, "
      f"10-90 % range {np.percentile(hill_ratios, 10):.2f}-{np.percentile(hill_ratios, 90):.2f} "
      f"(n={hill_ratios.size} bins).\n")
    P("End-point rules (fixed before the run): widening ends where ratio <= 1.10 "
      "for two consecutive counted bins; NDVI change is back at background where "
      "|corridor mean - hillside mean| <= 2 sd of the hillside bins for two "
      "consecutive counted bins.\n")
    P("## End-points by corridor half-width\n")
    P("| arm | half-width | widening ends (ratio<=1.1) | NDVI excess back in noise | bins counted / total |")
    P("|---|---|---|---|---|")
    for k, (label, _, _) in enumerate(ARMS):
        for hw in HALF_WIDTHS:
            r = results[hw][k]
            er, en = ends[(hw, k)]
            fmt = lambda v: "not within reach" if v is None else f"{v - BIN_M/2000:.2f}-{v + BIN_M/2000:.2f} km"
            P(f"| {label} | +/-{hw:.0f} m | {fmt(er)} | {fmt(en)} | "
              f"{int(r['counted'].sum())} / {r['counted'].size} |")
    P("")
    csv_rows = []
    for k, (label, _, _) in enumerate(ARMS):
        r = results[HALF_WIDTHS[0]][k]
        h = r["hill"]
        P(f"## {label}  (+/-{HALF_WIDTHS[0]:.0f} m corridor)\n")
        P(f"Analysed to {r['dist_km'].size * BIN_M / 1000:.2f} km"
          + (" (array edge)" if lines[k]["L_use"] < ARMS[k][2] else "") + ".\n")
        P("| km | corridor px | both-valid % | overlap % | bare before % | bare after % | "
          "after/before | hill after/before | added bare width m | mean dNDVI | hill dNDVI | "
          "excess | hill both-valid px | counted |")
        P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for i in range(r["dist_km"].size):
            f = lambda v, p=2: "n/a" if not np.isfinite(v) else f"{v:.{p}f}"
            ex = r["mean_d"][i] - h["mean_d"][i]
            P(f"| {r['dist_km'][i]-BIN_M/2000:.2f}-{r['dist_km'][i]+BIN_M/2000:.2f} | "
              f"{int(r['n_pix'][i])} | {100*r['cov'][i]:.0f} | "
              f"{100*r['overlap_frac'][i]:.0f} | {f(100*r['frac_pre'][i],0)} | "
              f"{f(100*r['frac_post'][i],0)} | {f(r['ratio'][i])} | {f(h['ratio'][i])} | "
              f"{f(r['added_w'][i],0)} | "
              f"{f(r['mean_d'][i],3)} | {f(h['mean_d'][i],3)} | {f(ex,3)} | "
              f"{int(h['n_valid'][i])} | {'yes' if r['counted'][i] else 'no'} |")
            for hw in HALF_WIDTHS:
                rr = results[hw][k]
                csv_rows.append(dict(arm=label, half_width_m=hw, km_from=r["dist_km"][i]-BIN_M/2000,
                                     km_to=r["dist_km"][i]+BIN_M/2000, n_pix=int(rr["n_pix"][i]),
                                     n_valid=int(rr["n_valid"][i]), cov=rr["cov"][i],
                                     overlap_frac=rr["overlap_frac"][i],
                                     bare_pre=int(rr["bare_pre"][i]), bare_post=int(rr["bare_post"][i]),
                                     frac_pre=rr["frac_pre"][i], frac_post=rr["frac_post"][i],
                                     ratio=rr["ratio"][i], hill_ratio=rr["hill"]["ratio"][i],
                                     added_bare_width_m=rr["added_w"][i],
                                     mean_dndvi=rr["mean_d"][i],
                                     hill_mean_dndvi=rr["hill"]["mean_d"][i],
                                     hill_n_valid=int(rr["hill"]["n_valid"][i]),
                                     counted=bool(rr["counted"][i])))
        P("")
    with open(os.path.join(args.results_dir, "wedge_corridor_bins.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)

    # ----- verdict paragraph (numbers pulled from the tables, not typed)
    r0 = results[HALF_WIDTHS[0]][0]
    er, en = ends[(HALF_WIDTHS[0], 0)]
    covs = r0["cov"][r0["dist_km"] <= 4.0]
    near = r0["ratio"][(r0["dist_km"] > OVERLAP_KM) & (r0["dist_km"] <= 1.5) & r0["counted"]]
    farr = r0["ratio"][(r0["dist_km"] > 2.5) & (r0["dist_km"] <= 4.0) & r0["counted"]]
    ctrl = results[HALF_WIDTHS[0]][2]
    cr = ctrl["ratio"][(ctrl["dist_km"] > OVERLAP_KM) & ctrl["counted"]]
    lh = results[HALF_WIDTHS[0]][1]
    lr = lh["ratio"][(lh["dist_km"] > OVERLAP_KM) & lh["counted"]]
    sens = ", ".join(f"+/-{hw:.0f} m: {'none' if ends[(hw,0)][0] is None else f'{ends[(hw,0)][0]:.2f} km'}"
                     for hw in HALF_WIDTHS)
    # descriptive, added after the first run: the added bare width tapers
    # roughly linearly up the arm, so report where a straight line through
    # the counted bins between the fan and 3 km reaches zero. Not a rule.
    P("## Taper of the up-valley stripping (descriptive, added after the first run)\n")
    P("Added bare width = (bare fraction after - before) x corridor width, so it is "
      "independent of corridor width if the stripping lies inside the corridor. A "
      "straight line is fitted through the counted bins from the fan edge to 3.0 km "
      "and its zero crossing reported; this is a description of the taper, not one "
      "of the pre-set end-point rules.\n")
    P("| half-width | added width at 0.75-1.0 km | at 1.75-2.0 km | at 2.5-2.75 km | "
      "line zero-crossing | slope m per km |")
    P("|---|---|---|---|---|---|")
    for hw in HALF_WIDTHS:
        rr = results[hw][0]
        d, w = rr["dist_km"], rr["added_w"]
        sel = rr["counted"] & (d > OVERLAP_KM) & (d <= 3.0) & np.isfinite(w)
        m, b = np.polyfit(d[sel], w[sel], 1)
        pick = lambda lo: w[np.argmin(np.abs(d - lo))]
        P(f"| +/-{hw:.0f} m | {pick(0.875):.0f} m | {pick(1.875):.0f} m | {pick(2.625):.0f} m | "
          f"{-b/m:.2f} km | {m:.0f} |")
    P("")
    P("## Verdict\n")
    P(f"Up-valley arm: after/before bare-area ratio in the counted bins between "
      f"{OVERLAP_KM} and 1.5 km is {', '.join(f'{v:.2f}' for v in near) or 'n/a'}; "
      f"between 2.5 and 4 km it is {', '.join(f'{v:.2f}' for v in farr) or 'n/a'}. "
      f"By the fixed rule the widening ends at "
      f"{'no point within the analysed reach' if er is None else f'{er - BIN_M/2000:.2f}-{er + BIN_M/2000:.2f} km'} "
      f"and the NDVI-change excess over the hillsides is back within 2 sd "
      f"({2*hill_sd:.3f}) at "
      f"{'no point within the analysed reach' if en is None else f'{en - BIN_M/2000:.2f}-{en + BIN_M/2000:.2f} km'}. "
      f"Sensitivity of the widening end to corridor width: {sens}. "
      f"Control: the downstream corridor (analysed to {ctrl['dist_km'].size*BIN_M/1000:.2f} km, "
      f"the array edge) has ratios {', '.join(f'{v:.2f}' for v in cr)} beyond the fan, "
      f"and the Lhende (source) corridor {', '.join(f'{v:.2f}' for v in lr)}. "
      f"Caveats: both-valid coverage in the up-valley corridor bins to 4 km runs "
      f"{100*np.nanmin(covs):.0f}-{100*np.nanmax(covs):.0f} % (post composite is "
      f"cloud-masked over {100*(1-np.isfinite(post).mean()):.0f} % of the AOI); the "
      f"SCL mask removes cloud and cloud shadow but not terrain shadow, which in "
      f"this gorge depresses NDVI on the same side of the valley in both epochs and "
      f"so mostly cancels in the difference but not in the bare threshold; the "
      f"first {OVERLAP_KM} km of every arm lies in the junction fan where the three "
      f"corridors overlap (overlap column) and was excluded from end-point placement; "
      f"the OSM centreline is the pre-event channel, so a channel that avulsed more "
      f"than the half-width would fall outside the corridor (the +/-250 m run guards "
      f"against this); bare fraction before is already high in the gorge bed, which "
      f"caps how large the ratio can be.\n")
    P(READING)
    md = "\n".join(lines_md)
    with open(os.path.join(args.results_dir, "RESULTS.md"), "w") as fh:
        fh.write(md)
    print("\n" + md)

    # ----- figure
    make_figure(pre, post, results[HALF_WIDTHS[0]], results, lines, shape,
                (c0, f0, a, e), (jx, jy), hill_sd, ends)


def make_figure(pre, post, R, results, lines, shape, geo, junc, hill_sd, ends):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    c0, f0, a, e = geo
    jx, jy = junc
    hw0 = HALF_WIDTHS[0]
    fig, ax = plt.subplots(1, 3, figsize=(19, 7.0))
    for A in ax:
        A.spines[["top", "right"]].set_visible(False)
        A.grid(True, color="#e5e4e0", lw=0.8)
        A.set_axisbelow(True)

    # (1) ratio vs distance
    A = ax[0]
    A.axhline(1.0, color="#7a7975", lw=1, ls="--")
    A.axvspan(0, OVERLAP_KM, color="#f0efec", zorder=0)
    A.text(OVERLAP_KM / 2, 0.05, "junction\nfan", ha="center", va="bottom",
           fontsize=8, color="#52514e")
    for k, r in enumerate(R):
        d, y = r["dist_km"], r["ratio"]
        ok = r["counted"] & np.isfinite(y)
        A.plot(d[ok], y[ok], "-", color=COLORS[k], lw=2, zorder=3)
        A.plot(d[ok], y[ok], "o", color=COLORS[k], ms=5, zorder=4)
        A.plot(d[~ok & np.isfinite(y)], y[~ok & np.isfinite(y)], "o", mfc="white",
               mec=COLORS[k], ms=5, zorder=4)
        for hw in HALF_WIDTHS[1:]:
            rr = results[hw][k]
            okk = rr["counted"] & np.isfinite(rr["ratio"])
            A.plot(rr["dist_km"][okk], rr["ratio"][okk], "-", color=COLORS[k],
                   lw=0.8, alpha=0.5, zorder=2)
        if ok.any():
            i = np.flatnonzero(ok)[-1]
            A.annotate(lines[k]["label"].split(" (")[0], (d[i], y[i]),
                       xytext=(4, 0), textcoords="offset points", fontsize=8,
                       color=COLORS[k], va="center")
    er, en = ends[(hw0, 0)]
    ytop = A.get_ylim()[1]
    if en is not None:
        A.axvline(en - BIN_M / 2000, color=COLORS[0], lw=1, ls="-.")
        A.text(en - BIN_M / 2000 - 0.05, ytop * 0.99, "up-valley NDVI excess\nback in hillside noise\n"
               f"{en - BIN_M/2000:.2f}-{en + BIN_M/2000:.2f} km", fontsize=7.5,
               color=COLORS[0], va="top", ha="right")
    if er is not None:
        A.axvline(er - BIN_M / 2000, color=COLORS[0], lw=1, ls=":")
        A.text(er - BIN_M / 2000 + 0.05, ytop * 0.99, "up-valley ratio <= 1.1\n"
               f"from {er - BIN_M/2000:.2f}-{er + BIN_M/2000:.2f} km",
               fontsize=7.5, color=COLORS[0], va="top")
    A.set_xlabel("distance along river from the junction (km)")
    A.set_ylabel(f"bare area after / before  (NDVI < {BARE}, +/-{hw0:.0f} m corridor)")
    A.set_title("Channel widening along each arm", fontsize=10, loc="left")
    A.legend(handles=[Line2D([], [], color=COLORS[k], lw=2, marker="o", ms=5,
                             label=lines[k]["label"]) for k in range(3)]
             + [Line2D([], [], color="#7a7975", lw=0.8, alpha=0.6, label="+/-100 and +/-250 m"),
                Line2D([], [], marker="o", mfc="white", mec="#7a7975", ls="", ms=5,
                       label="bin not counted (coverage < 30 % or < 20 bare px before)")],
             fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
             frameon=False)
    A.set_ylim(bottom=0)

    # (2) map with the corridors
    A = ax[1]
    d = post - pre
    xs = np.array([l["lx"] for l in lines], dtype=object)
    # crop to the arms +/- 1 km
    allx = np.concatenate([l["lx"] for l in lines]); ally = np.concatenate([l["ly"] for l in lines])
    x0, x1 = allx.min() - 800, allx.max() + 800
    y0, y1 = ally.min() - 800, ally.max() + 800
    cc0, cc1 = int(max(0, (x0 - c0) / a)), int(min(shape[1], (x1 - c0) / a))
    rr0, rr1 = int(max(0, (y1 - f0) / e)), int(min(shape[0], (y0 - f0) / e))
    sub = d[rr0:rr1, cc0:cc1]
    ext = [(c0 + cc0 * a - jx) / 1000, (c0 + cc1 * a - jx) / 1000,
           (f0 + rr1 * e - jy) / 1000, (f0 + rr0 * e - jy) / 1000]
    im = A.imshow(sub, cmap="RdBu", vmin=-0.6, vmax=0.6, extent=ext,
                  interpolation="nearest")
    A.imshow(np.where(np.isfinite(sub), np.nan, 1.0), cmap="Greys", vmin=0, vmax=3,
             extent=ext, interpolation="nearest")     # masked = light grey
    for k, r in enumerate(R):
        m = r["mask"][rr0:rr1, cc0:cc1].astype(float)
        A.contour(m, levels=[0.5], colors=[COLORS[k]], linewidths=1.2,
                  extent=ext, origin="upper")
        # km ticks along the centreline
        l = lines[k]
        for km in range(1, int(l["L_use"]) + 1):
            j = np.argmin(np.abs(l["ls"] - km * 1000))
            A.plot((l["lx"][j] - jx) / 1000, (l["ly"][j] - jy) / 1000, "o",
                   ms=3, color=COLORS[k], mec="white", mew=0.6)
            if km % 2 == 0:
                A.annotate(f"{km}", ((l["lx"][j] - jx) / 1000, (l["ly"][j] - jy) / 1000),
                           xytext=(4, 3), textcoords="offset points", fontsize=7,
                           color=COLORS[k])
    A.plot(0, 0, "k+", ms=10, mew=1.5)
    A.set_xlabel("km east of the junction")
    A.set_ylabel("km north of the junction")
    A.set_title(f"NDVI change with the +/-{hw0:.0f} m corridors (grey = no clear view)",
                fontsize=10, loc="left")
    A.grid(False)
    cb = fig.colorbar(im, ax=A, fraction=0.04, pad=0.02)
    cb.set_label("NDVI change, post - pre (red = vegetation lost)", fontsize=8)
    A.set_aspect("equal")

    # (3) up-valley bare-fraction profile
    A = ax[2]
    r = R[0]
    d = r["dist_km"]
    A.bar(d, r["cov"], width=BIN_M / 1000 * 0.9, color="#e5e4e0", label="both-valid coverage")
    A.axvspan(0, OVERLAP_KM, color="#f0efec", zorder=0)
    # break the lines at uncounted bins so a near-empty bin does not read as a value
    fp = np.where(r["counted"], r["frac_pre"], np.nan)
    fq = np.where(r["counted"], r["frac_post"], np.nan)
    A.plot(d, fp, "-", color="#7a7975", lw=2, label="bare fraction before (12 Aug)")
    A.plot(d, fq, "-", color=COLORS[0], lw=2, label="bare fraction after (27 Aug-3 Sept)")
    A.plot(d[~r["counted"]], r["frac_post"][~r["counted"]], "o", mfc="white", mec=COLORS[0], ms=5)
    A.plot(d[r["counted"]], r["frac_post"][r["counted"]], "o", color=COLORS[0], ms=5)
    A.set_ylim(0, 1)
    A.set_xlabel("distance up the Kyirong arm from the junction (km)")
    A.set_ylabel("fraction of corridor pixels")
    A.set_title("Up-valley arm: bare fraction before and after", fontsize=10, loc="left")
    A.legend(fontsize=7.5, loc="upper right", frameon=False)
    if er is not None:
        A.axvline(er - BIN_M / 2000, color=COLORS[0], lw=1, ls=":")
    if en is not None:
        A.axvline(en - BIN_M / 2000, color=COLORS[0], lw=1, ls="-.")

    fig.suptitle("Sentinel-2 corridor test: how far up the Kyirong arm did the "
                 "26 Aug flow strip the valley floor?", fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT, "wedge_corridor.png")
    fig.savefig(p, dpi=140)
    print(f"figure -> {p}")


if __name__ == "__main__":
    main()
