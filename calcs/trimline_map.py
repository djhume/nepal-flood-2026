#!/usr/bin/env python3
"""
Map every mud line in the corridor from post-event imagery plus a DEM.

WHY (Dave, 6 Sept late; brief in research/trimline-mapping-brief.md). The size
envelope was scored on timing, a border speed, an erosion volume and a
deposition cap - never on a water depth. Four lines now say the passing runs
are too small below the junction (dossier sections 17, 18). The missing
observable is a peak-stage profile along the corridor: wherever the
stripped-ground boundary crosses the topography we get a three-dimensional
point on the mud line. Inner/outer-bank pairs at bends give velocities, and
stage x velocity gives a peak-discharge profile - the input the next ensemble
needs.

METHOD, in stages (each cached under output/cache/, all from open sources):
  s2       Sentinel-2 L2A off the AWS COG mirror (Element84 STAC, no login):
           pre-event NDVI composite (least-cloudy August scenes) and a
           post-event per-pixel median (27 Aug - 6 Sept), tile T45RUM, 10 m,
           over the whole corridor scar -> Betrawati.
  pelican  Planet Pelican 0.55 m pansharpened scenes, 27 Aug and 1 Sept
           (Syabrubesi -> Rasuwagadhi; CC-BY-NC-4.0, analysed, never stored),
           read through the 3x overview (1.5 m) along each cross-section only.
  map      For every 100 m station on the OSM centreline, walk the cross-
           section outward on each bank through the "bare after" mask until it
           ends; that pixel is the trimline point. Sample the DEM there
           (bilinear) and along the section for the bed. Stage = trimline -
           bed. At bends, v^2 = g Rc dh / W from the inner/outer difference.
           Q = A(eta) x 0.85 v where both exist.

RULES FIXED BEFORE THE NUMBERS WERE LOOKED AT (do not move them afterwards):
  * bare after: S2 NDVI < 0.20 (as sentinel_wedge*.py); Pelican
    NDVI(band6, band3) < 0.10 (band 3 behaves as red, band 6 as NIR: veg
    median +0.36, mud -0.17 in a test window at the junction).
  * vegetated before (S2 only): pre NDVI >= 0.30.
  * gap tolerance inside a bare run: 1 px (S2), 3 px (Pelican, 4.5 m).
  * a walk that meets cloud / shadow / nodata before the run ends is
    TRUNCATED and gives no trimline (flagged, never filled). A run still
    bare at +/-600 m is OPEN (bare hillside / landslide), no trimline.
  * bed = minimum of the DEM section within +/-150 m of the centreline,
    taken as the minimum over stations within +/-300 m along the path; the
    strict downstream running minimum is carried as a second column.
  * bend: 3-point circle over +/-300 m, Rc < 3000 m; the outer bank is the
    one the centreline turns away from. Velocity only where dh > 1 sigma.
  * head-on geometry (run-up, not stage; dossier 6c): turn > 60 deg over
    +/-300 m, an OSM side stream joining within 200 m (that bank only), and
    the border junction km 21.5-22.8 (both banks). Flagged, excluded from
    the stage average and from the velocity table.
  * vertical error per point: (1.5 px of the layer x tan(wall slope)) added
    in quadrature to the DEM's own error, taken as 4 + 6 tan(slope) m for
    GLO-30 and 1.5 + 2 tan(slope) m for HMA 8 m.
  * section-mean velocity = 0.85 x the superelevation (surface) velocity.

HONESTY. A stripped-ground boundary is a FLOOR on the water surface
(vegetation survives brief immersion); on the 1 Sept scenes it is a
post-drain surface. A mark where the flow met a wall head-on is run-up, not
stage. The 30 m DEM over-reads incised floors and under-reads heights on
steep walls by tens of metres in places. Nothing here is a finding; it is a
table with its coverage and flags.

DEM. Copernicus GLO-30 tiles N28/N27 E085 (data/, gitignored, URLs in
DATA-SOURCES.md); HMA 8 m mosaic tile 675/676 (NSIDC HMA_DEM8m_MOS, Earthdata
login) used automatically when data/HMA_DEM8m_MOS_20170716_tile-675.tif exists.
Never the Mapzen profile (void-fill artefacts, dossier 17).

Run:
  .venv/bin/python calcs/trimline_map.py --stage s2         # ~30-60 min
  .venv/bin/python calcs/trimline_map.py --stage pelican    # ~10 min
  .venv/bin/python calcs/trimline_map.py --stage map [--junction]
"""
import argparse, csv, json, math, os, sys, time, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
CACHE = os.path.join(OUT, "cache")
os.makedirs(CACHE, exist_ok=True)

G = 9.81
UTM = "EPSG:32645"
STEP_M = 100.0                 # station spacing along the centreline
HALF_SEC = 600.0               # half cross-section length (m)
BED_HALF = 150.0               # bed search half-width (m)
BED_ALONG = 300.0              # bed local envelope half-length along path (m)
CURV_HALF = 300.0              # circle-fit half-window (m)
RC_MAX = 3000.0                # straighter than this = no bend
TURN_HEADON = 60.0             # degrees over +/-CURV_HALF
SIDEVALLEY_M = 200.0
JUNCTION_KM = (21.5, 22.8)
SURFACE_TO_MEAN = 0.85
KM_END = 200.0                 # Devghat is at km 199.2 on data/river_path.csv
BBOX = [85.10, 27.94, 85.56, 28.42]   # upper box: scar -> Betrawati (68.4), tile T45RUM
BBOX_LOWER = [84.40, 27.70, 85.22, 28.00]   # lower box: Betrawati -> Devghat (T45RTL/RUL + RTM/RUM slivers)
S2_BOXES = {"upper": BBOX, "lower": BBOX_LOWER}
DEM_BBOX = [84.40, 27.68, 85.56, 28.42]
OVERRIDES = os.path.join(DATA, "trimline_overrides.csv")   # manual flags with provenance
FIT_HALF_KM = 1.0              # robust running fit window, +/- km
STAC = "https://earth-search.aws.element84.com/v1/search"
PLANET = ("https://data.source.coop/planet/disasterdata/"
          "nepal-flash-flood-2026-08-26/post-event/")
PELICAN = {  # date -> (collection, item ids)
    "20260827": ("pelican-2026-08-27", ["20260827_060956_98_3009",
                                        "20260827_060958_31_3009",
                                        "20260827_060959_65_3009"]),
    "20260901": ("pelican-2026-09-01", ["20260901_050632_98_300b",
                                        "20260901_050634_33_300b",
                                        "20260901_050635_67_300b"]),
}
LAYERS = {   # name -> (bare threshold, gap px, placement px, native res m)
    "s2":          dict(bare=0.20, gap=1, place=1.5, res=10.0),
    # change-based: bare after AND not bare before, plus the pre-event bare
    # channel run - the like-for-like of a disturbance product (geopera's),
    # blind to bare rock / scree / roads that were bare before the event
    "s2chg":       dict(bare=0.20, gap=1, place=1.5, res=10.0),
    "pelican0827": dict(bare=0.10, gap=3, place=1.5, res=1.5),
    "pelican0901": dict(bare=0.10, gap=3, place=1.5, res=1.5),
}
VEG_PRE = 0.30
SCL_BAD = [0, 1, 3, 8, 9, 10]   # nodata, saturated, shadow, cloud med/high, cirrus
GLO30 = [os.path.join(DATA, "Copernicus_DSM_COG_10_N28_00_E085_00_DEM.tif"),
         os.path.join(DATA, "Copernicus_DSM_COG_10_N27_00_E085_00_DEM.tif"),
         os.path.join(DATA, "Copernicus_DSM_COG_10_N27_00_E084_00_DEM.tif")]
HMA = [os.path.join(DATA, "HMA_DEM8m_MOS_20170716_tile-675.tif"),
       os.path.join(DATA, "HMA_DEM8m_MOS_20170716_tile-676.tif"),
       os.path.join(DATA, "HMA_DEM8m_MOS_20170716_tile-674.tif")]


def half_sec(s):
    """Cross-section half-length: 600 m in the gorges, 1,500 m on the
    floodplain below Betrawati (the flood edge there is far from the river)."""
    return HALF_SEC if (s["arm"] != "main" or s["km"] <= 70.0) else 1500.0

# Dave's marks and the published cross-checks (dossier 6c, 18; geopera v1.1)
CHECKS = {
    "junction bed (GE)": 1815.0, "junction lee mud line (GE, hut)": 1875.0,
    "junction impact cliff (GE)": (1920.0, 1930.0),
    "Hakubesi km 43-45 stage above pre-event bed (helicopter stills)": (45.0, 70.0),
    "Syabrubesi opening velocity (geopera)": 11.0,
}
# dossier 18 passing-run peak depths (m): km 22, Syabrubesi 37.6, Hakubesi 43.5
MODEL_DEPTHS = {22.0: (31, 123), 37.6: (3.9, 19.7), 43.5: (4.6, 20.9), 107.6: (3.1, 4.1)}
# lower-river gauge observations (dossier 1, 4): stage RISE, so a floor on stage
GAUGE_STAGE = {107.6: ("Galchhi +9 m / 30 min", 9.0), 199.2: ("Devghat 6.57 m", 6.57)}
LANDMARKS = ((22.0, "junction"), (37.6, "Syabrubesi"), (43.5, "Hakubesi"), (68.4, "Betrawati"),
             (107.6, "Galchhi"), (199.2, "Devghat"))


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
def to_utm(lons, lats):
    from rasterio.warp import transform
    xs, ys = transform("EPSG:4326", UTM, list(lons), list(lats))
    return np.asarray(xs, float), np.asarray(ys, float)


def to_lonlat(xs, ys):
    from rasterio.warp import transform
    lo, la = transform(UTM, "EPSG:4326", list(np.asarray(xs, float)),
                       list(np.asarray(ys, float)))
    return np.asarray(lo), np.asarray(la)


def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))


def osm_corridor_path():
    """The same greedy stitch as model/build_profile.py (so chainage matches
    data/river_path.csv), but kept at full OSM vertex density. Returns
    (lat, lon) list from the scar, and the list of (km_from, km_to) spans
    that are straight-line bridges rather than mapped channel."""
    NAMES = {"Chhochen Khola", "东林藏布", "吉隆藏布", "भोटे कोशी", "Bhote Koshi",
             "Bhote Kosi", "Bhotekoshi", "Trishuli River", "Trishuli Ganga River",
             "त्रिशुली नदी"}
    SCAR = (28.2765, 85.5194)
    DEVGHAT = (27.7095, 84.4290)
    ways, seen = [], set()
    for fname in ("osm_rivers.json", "osm_rivers_lower.json"):
        d = json.load(open(os.path.join(DATA, fname)))
        for e in d["elements"]:
            name = e.get("tags", {}).get("name", "")
            if name in NAMES and e.get("geometry") and e["id"] not in seen:
                seen.add(e["id"])
                pts = [(g["lat"], g["lon"]) for g in e["geometry"]]
                ln = sum(hav(pts[i - 1], pts[i]) for i in range(1, len(pts)))
                if ln < 0.3:
                    continue
                ways.append({"id": e["id"], "name": name, "pts": pts})
    unused = ways[:]
    start = min(unused, key=lambda w: min(hav(SCAR, p) for p in w["pts"]))
    unused.remove(start)
    if hav(SCAR, start["pts"][0]) > hav(SCAR, start["pts"][-1]):
        start["pts"].reverse()
    path = start["pts"][:]
    bridges = []
    while hav(path[-1], DEVGHAT) > 2.0:
        end = path[-1]
        best, bestd, bestrev = None, 1e9, False
        for w in unused:
            for rev in (False, True):
                near = w["pts"][-1] if rev else w["pts"][0]
                far = w["pts"][0] if rev else w["pts"][-1]
                gap = hav(end, near)
                if gap < bestd and hav(far, DEVGHAT) < hav(end, DEVGHAT) + 2.0:
                    best, bestd, bestrev = w, gap, rev
        if best is None or bestd > 5.0:
            break
        unused.remove(best)
        pts = best["pts"][::-1] if bestrev else best["pts"]
        if bestd > 0.15:
            bridges.append((len(path) - 1, len(path)))   # vertex index pair
        path.extend(pts)
    imin = min(range(len(path)), key=lambda i: hav(path[i], DEVGHAT))
    path = path[:imin + 1]
    path.insert(0, SCAR)
    bridges = [(a + 1, b + 1) for a, b in bridges]
    return path, bridges


def stations_main():
    """100 m stations along the corridor path to KM_END, in UTM, with unit
    tangents (downstream) and left normals. Chainage matches river_path.csv
    to the metre (same stitch, same haversine)."""
    path, bridges = osm_corridor_path()
    lat = np.array([p[0] for p in path]); lon = np.array([p[1] for p in path])
    cum = np.zeros(len(path))
    for i in range(1, len(path)):
        cum[i] = cum[i - 1] + hav(path[i - 1], path[i])
    bridge_km = [(cum[a], cum[b]) for a, b in bridges]
    x, y = to_utm(lon, lat)
    s_km = np.arange(0.0, min(KM_END, cum[-1]), STEP_M / 1000.0)
    sx = np.interp(s_km, cum, x); sy = np.interp(s_km, cum, y)
    # tangent from +/-150 m along the (metre-accurate) chainage
    h = 0.15
    xa = np.interp(s_km - h, cum, x); ya = np.interp(s_km - h, cum, y)
    xb = np.interp(s_km + h, cum, x); yb = np.interp(s_km + h, cum, y)
    tx, ty = xb - xa, yb - ya
    L = np.hypot(tx, ty); L[L == 0] = 1.0
    tx, ty = tx / L, ty / L
    nx, ny = -ty, tx                       # left of the flow
    st = []
    for i in range(len(s_km)):
        st.append(dict(arm="main", km=float(s_km[i]), x=float(sx[i]), y=float(sy[i]),
                       tx=float(tx[i]), ty=float(ty[i]), nx=float(nx[i]), ny=float(ny[i]),
                       bridged=any(a - 0.05 <= s_km[i] <= b + 0.05 for a, b in bridge_km)))
    # curvature via 3-point circle at +/-CURV_HALF, and the turn angle
    hc = CURV_HALF / 1000.0
    for i, s in enumerate(st):
        k = s_km[i]
        p = [(np.interp(t, cum, x), np.interp(t, cum, y)) for t in (k - hc, k, k + hc)]
        (x1, y1), (x2, y2), (x3, y3) = p
        a = math.hypot(x2 - x1, y2 - y1); b = math.hypot(x3 - x2, y3 - y2)
        c = math.hypot(x3 - x1, y3 - y1)
        cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        if abs(cross) < 1e-6 or a == 0 or b == 0:
            s["Rc"], s["turn_sign"], s["turn_deg"] = float("inf"), 0, 0.0
            continue
        s["Rc"] = a * b * c / (2 * abs(cross))
        s["turn_sign"] = int(np.sign(cross))          # +1 = turning left
        d1 = math.atan2(y2 - y1, x2 - x1); d2 = math.atan2(y3 - y2, x3 - x2)
        s["turn_deg"] = abs((math.degrees(d2 - d1) + 180) % 360 - 180)
    return st, (x, y, cum)


def stations_kyirong():
    """The up-valley arm (Kyirong Tsangpo, OSM way 904894054) from the
    junction, 100 m stations to 6 km; same fields, arm='kyirong', km =
    distance up the arm (negative tangent = flow direction during the
    surge is UP the arm, so 'left' is left looking up-valley)."""
    sys.path.insert(0, HERE)
    import sentinel_wedge_corridor as swc
    ways = swc.load_ways()
    geom, _ = swc.chain_from_junction(ways, 904894054, 7.0)
    lon = np.array([p["lon"] for p in geom]); lat = np.array([p["lat"] for p in geom])
    x, y = to_utm(lon, lat)
    seg = np.hypot(np.diff(x), np.diff(y))
    cum = np.concatenate([[0.0], np.cumsum(seg)]) / 1000.0
    s_km = np.arange(0.0, min(6.0, cum[-1]), STEP_M / 1000.0)
    sx = np.interp(s_km, cum, x); sy = np.interp(s_km, cum, y)
    h = 0.15
    xa = np.interp(s_km - h, cum, x); ya = np.interp(s_km - h, cum, y)
    xb = np.interp(s_km + h, cum, x); yb = np.interp(s_km + h, cum, y)
    tx, ty = xb - xa, yb - ya
    L = np.hypot(tx, ty); L[L == 0] = 1.0
    tx, ty = tx / L, ty / L
    st = []
    for i in range(len(s_km)):
        st.append(dict(arm="kyirong", km=float(s_km[i]), x=float(sx[i]), y=float(sy[i]),
                       tx=float(tx[i]), ty=float(ty[i]), nx=float(-ty[i]), ny=float(tx[i]),
                       bridged=False, Rc=float("inf"), turn_sign=0, turn_deg=0.0))
    return st


def side_streams():
    """End-points of OSM waterways that are NOT the corridor (side valleys)."""
    NAMES = {"Chhochen Khola", "东林藏布", "吉隆藏布", "भोटे कोशी", "Bhote Koshi",
             "Bhote Kosi", "Bhotekoshi", "Trishuli River", "Trishuli Ganga River",
             "त्रिशुली नदी"}
    lons, lats = [], []
    for fname in ("osm_rivers.json", "osm_rivers_lower.json"):
        d = json.load(open(os.path.join(DATA, fname)))
        for e in d["elements"]:
            if e["type"] != "way" or not e.get("geometry"):
                continue
            if e.get("tags", {}).get("name", "") in NAMES:
                continue
            for g in (e["geometry"][0], e["geometry"][-1]):
                lons.append(g["lon"]); lats.append(g["lat"])
    x, y = to_utm(lons, lats)
    return x, y


# --------------------------------------------------------------------------
# stage s2: whole-corridor NDVI composites (cached)
# --------------------------------------------------------------------------
def stac_search(dt, bbox=BBOX):
    q = {"collections": ["sentinel-2-c1-l2a"], "bbox": bbox, "datetime": dt,
         "limit": 200}
    req = urllib.request.Request(STAC, data=json.dumps(q).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        feats = json.loads(r.read())["features"]
    return [f for f in feats if str(f["properties"].get("grid:code", "")).startswith("MGRS-45R")]


def s2_grid(bbox):
    """Common 10 m EPSG:32645 grid over a lon/lat bbox: (x0, y0, x1, y1, W, H).
    Every Sentinel-2 tile in the zone sits on this grid (origins are multiples
    of 10 m), so tiles paste at integer offsets without resampling."""
    from rasterio.warp import transform_bounds
    l, b, r, t = transform_bounds("EPSG:4326", UTM, *bbox)
    x0 = math.floor(l / 10) * 10; x1 = math.ceil(r / 10) * 10
    y0 = math.floor(b / 10) * 10; y1 = math.ceil(t / 10) * 10
    return x0, y0, x1, y1, int((x1 - x0) / 10), int((y1 - y0) / 10)


def s2_paste(feat, grid, mosaic):
    """Read the part of one scene inside the grid, compute NDVI, mask with
    SCL, paste where the mosaic is still empty. Returns the masked fraction."""
    import rasterio
    from rasterio.windows import Window
    x0, y0, x1, y1, W, H = grid
    a = feat["assets"]
    with rasterio.open(a["red"]["href"]) as s_:
        b = s_.bounds
        l, r_ = max(x0, b.left), min(x1, b.right); bo, t = max(y0, b.bottom), min(y1, b.top)
        if r_ - l < 20 or t - bo < 20:
            return None
        c0 = int(round((l - s_.transform.c) / 10)); r0 = int(round((s_.transform.f - t) / 10))
        w = Window(c0, r0, int(round((r_ - l) / 10)), int(round((t - bo) / 10)))
        red = s_.read(1, window=w).astype("float32")
    with rasterio.open(a["nir"]["href"]) as s_:
        nir = s_.read(1, window=w).astype("float32")
    with rasterio.open(a["scl"]["href"]) as s_:
        scl = s_.read(1, window=Window(w.col_off / 2, w.row_off / 2, w.width / 2, w.height / 2),
                      out_shape=red.shape)
    bad = np.isin(scl, SCL_BAD) | (red + nir <= 0)
    v = (nir - red) / np.maximum(nir + red, 1.0); v[bad] = np.nan
    gc = int(round((l - x0) / 10)); gr = int(round((y1 - t) / 10))
    sub = mosaic[gr:gr + v.shape[0], gc:gc + v.shape[1]]
    v = v[:sub.shape[0], :sub.shape[1]]
    take = np.isnan(sub) & np.isfinite(v)
    sub[take] = v[take]
    return float(bad.mean())


def stage_s2(refetch=False, boxes=("upper", "lower")):
    """Pre/post NDVI composites per box, cached under output/cache/s2/.
    'upper' keeps the original file names (pre.npy, post.npy, meta.json)."""
    d = os.path.join(CACHE, "s2"); os.makedirs(d, exist_ok=True)
    for name in boxes:
        bbox = S2_BOXES[name]
        pfx = "" if name == "upper" else name + "_"
        meta_p = os.path.join(d, pfx + "meta.json")
        if os.path.exists(meta_p) and not refetch:
            print(f"s2 {name} composites cached:", meta_p); continue
        t0 = time.time()
        grid = s2_grid(bbox); x0, y0, x1, y1, W, H = grid
        print(f"s2 {name}: grid {W}x{H} px at 10 m, {UTM}, origin ({x0}, {y1})", flush=True)
        pre = stac_search("2026-08-01T00:00:00Z/2026-08-26T00:00:00Z", bbox)
        post = stac_search("2026-08-26T12:00:00Z/2026-09-07T00:00:00Z", bbox)
        meta = {"transform": [10.0, 0.0, float(x0), 0.0, -10.0, float(y1)], "crs": UTM,
                "shape": [H, W], "bbox": bbox, "pre": [], "post": []}
        for lab, feats in (("pre", pre), ("post", post)):
            by_date = {}
            for f in feats:
                by_date.setdefault(f["properties"]["datetime"][:10], []).append(f)
            dates = sorted(by_date)
            if lab == "pre":   # the 4 least-cloudy dates (mean scene cloud over the tiles)
                dates = sorted(dates, key=lambda dd: np.mean([f["properties"]["eo:cloud_cover"]
                                                              for f in by_date[dd]]))[:4]
            layers = []
            for dd in dates:
                mosaic = np.full((H, W), np.nan, "float32")
                ids = []
                for f in by_date[dd]:
                    try:
                        bad = s2_paste(f, grid, mosaic)
                    except Exception as e:
                        print(f"  {lab} {f['id']}: read failed ({e})"); continue
                    if bad is not None:
                        ids.append((f["id"], round(bad, 3)))
                valid = float(np.isfinite(mosaic).mean())
                print(f"  {lab} {dd}: {len(ids)} tiles, {100*valid:.1f}% of the box valid "
                      f"[{time.time()-t0:.0f} s]", flush=True)
                if valid > 0.001:
                    layers.append(mosaic.astype("float16"))
                    meta[lab].append({"date": dd, "tiles": ids, "box_valid": valid})
            stack = np.stack(layers).astype("float32")
            with np.errstate(all="ignore"):
                comp = np.nanmedian(stack, axis=0)
            nval = np.sum(np.isfinite(stack), axis=0).astype("uint8")
            np.save(os.path.join(d, f"{pfx}{lab}.npy"), comp.astype("float16"))
            np.save(os.path.join(d, f"{pfx}{lab}_nvalid.npy"), nval)
            meta[f"{lab}_valid_frac"] = float(np.isfinite(comp).mean())
            print(f"  -> {name} {lab} composite from {len(layers)} dates: "
                  f"{100*meta[f'{lab}_valid_frac']:.1f}% of the box valid", flush=True)
            del stack, layers
        json.dump(meta, open(meta_p, "w"), indent=1)
        print(f"s2 {name} done in {time.time()-t0:.0f} s -> {d}")


class S2Layer:
    """All cached composites (upper box, lower box); a point is sampled from
    the first box that contains it."""
    def __init__(self):
        from affine import Affine
        d = os.path.join(CACHE, "s2")
        self.boxes = []
        for pfx in ("", "lower_"):
            mp = os.path.join(d, pfx + "meta.json")
            if not os.path.exists(mp):
                continue
            meta = json.load(open(mp))
            self.boxes.append(dict(meta=meta, tr=Affine(*meta["transform"]),
                                   pre=np.load(os.path.join(d, pfx + "pre.npy")).astype("float32"),
                                   post=np.load(os.path.join(d, pfx + "post.npy")).astype("float32")))
        if not self.boxes:
            raise FileNotFoundError(os.path.join(d, "meta.json"))
        self.meta = self.boxes[0]["meta"]
        self.res = 10.0

    def sample(self, x, y):
        """Returns ndvi_post, ndvi_pre (NaN = invalid / off every box)."""
        post = np.full(x.shape, np.nan, "float32"); pre = post.copy(); done = np.zeros(x.shape, bool)
        for b in self.boxes:
            tr = b["tr"]; shape = b["pre"].shape
            c = np.floor((x - tr.c) / tr.a).astype(int)
            r = np.floor((y - tr.f) / tr.e).astype(int)
            ok = (c >= 0) & (c < shape[1]) & (r >= 0) & (r < shape[0]) & ~done
            post[ok] = b["post"][r[ok], c[ok]]; pre[ok] = b["pre"][r[ok], c[ok]]
            done |= ok
        return post, pre


# --------------------------------------------------------------------------
# stage pelican: section samples from the 0.55 m scenes (cached)
# --------------------------------------------------------------------------
def pelican_items(date):
    coll, ids = PELICAN[date]
    out = []
    for i in ids:
        base = f"{PLANET}{coll}/items/{i}/{i}"
        out.append((i, base + "_pansharpened.tif"))
    return out


def stage_pelican(stations, refetch=False):
    """For each station and bank, sample NDVI(b6,b3) at 1.5 m along the
    cross-section from the pansharpened COG's 3x overview, one 1-km chunk of
    stations at a time. Cloud = band 1 > 22000 (bright in the bluest band);
    dark = band 6 < 3000 (deep shadow, treated as invalid, not bare)."""
    import rasterio
    from rasterio.windows import Window, from_bounds
    from rasterio.enums import Resampling
    d = os.path.join(CACHE, "pelican"); os.makedirs(d, exist_ok=True)
    res = LAYERS["pelican0827"]["res"]
    offs = np.arange(-HALF_SEC, HALF_SEC + res / 2, res)
    all_stations = stations
    for date in PELICAN:
        p = os.path.join(d, f"sections_{date}.npz")
        old = None
        stations = all_stations
        if os.path.exists(p) and not refetch:
            # incremental: sample only stations not already in the cache
            old = np.load(p)
            have = {(str(a), round(float(k), 3)) for a, k in zip(old["arm"], old["km"])}
            stations = [s for s in all_stations if (s["arm"], round(s["km"], 3)) not in have]
            if not stations:
                print("pelican cached:", p); continue
            print(f"pelican {date}: {len(stations)} new stations to add to the cache")
        t0 = time.time()
        N = len(stations)
        ndvi = np.full((N, offs.size), np.nan, "float32")
        state = np.zeros((N, offs.size), "uint8")   # 0 none, 1 valid, 2 cloud, 3 dark
        # big curl chunks + merged ranges: the COG is pixel-interleaved 6-band
        # uint16 in 512 px tiles, and GDAL's default 16 kB ranges made the
        # first attempt crawl at ~100 kB/s from source.coop.
        env = rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                           CPL_VSIL_CURL_CHUNK_SIZE=4 * 1024 * 1024,
                           CPL_VSIL_CURL_CACHE_SIZE=512 * 1024 * 1024,
                           GDAL_HTTP_MULTIRANGE="YES",
                           GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
                           GDAL_HTTP_MAX_RETRY=4, GDAL_HTTP_RETRY_DELAY=3)
        env.__enter__()
        srcs = [(i, rasterio.open(h)) for i, h in pelican_items(date)]
        CH = 30
        try:
            for k0 in range(0, N, CH):
                chunk = stations[k0:k0 + CH]
                xs = np.array([[s["x"] + o * s["nx"] for o in offs] for s in chunk])
                ys = np.array([[s["y"] + o * s["ny"] for o in offs] for s in chunk])
                l, r_, b, t = xs.min(), xs.max(), ys.min(), ys.max()
                for sid, src in srcs:
                    bb = src.bounds
                    if r_ < bb.left or l > bb.right or t < bb.bottom or b > bb.top:
                        continue
                    w = from_bounds(max(l, bb.left), max(b, bb.bottom),
                                    min(r_, bb.right), min(t, bb.top), src.transform)
                    w = Window(int(w.col_off) // 3 * 3, int(w.row_off) // 3 * 3,
                               int(math.ceil(w.width / 3)) * 3, int(math.ceil(w.height / 3)) * 3)
                    if w.width < 3 or w.height < 3:
                        continue
                    oh, ow = w.height // 3, w.width // 3
                    arr = src.read([1, 3, 6], window=w, out_shape=(3, oh, ow),
                                   resampling=Resampling.average).astype("float32")
                    wt = src.window_transform(w)
                    cc = np.floor((xs - wt.c) / (wt.a * 3)).astype(int)
                    rr = np.floor((ys - wt.f) / (wt.e * 3)).astype(int)
                    ok = (cc >= 0) & (cc < ow) & (rr >= 0) & (rr < oh)
                    b1 = np.full(xs.shape, np.nan, "float32"); b3 = b1.copy(); b6 = b1.copy()
                    b1[ok] = arr[0][rr[ok], cc[ok]]; b3[ok] = arr[1][rr[ok], cc[ok]]
                    b6[ok] = arr[2][rr[ok], cc[ok]]
                    has = ok & (b3 > 0) & (b6 > 0)
                    cloud = has & (b1 > 22000)
                    dark = has & ~cloud & (b6 < 3000)
                    good = has & ~cloud & ~dark
                    v = (b6 - b3) / np.maximum(b6 + b3, 1.0)
                    sl = slice(k0, k0 + len(chunk))
                    st_ = state[sl]; nd = ndvi[sl]
                    # a valid read from any frame wins; cloud/dark only if nothing better
                    take = good & (st_ != 1)
                    nd[take] = v[take]; st_[take] = 1
                    st_[cloud & (st_ == 0)] = 2
                    st_[dark & (st_ == 0)] = 3
                    state[sl] = st_; ndvi[sl] = nd
                print(f"  {date}: stations {k0}-{k0+len(chunk)} "
                      f"valid {100*np.mean(state[:k0+len(chunk)]==1):.0f}% "
                      f"[{time.time()-t0:.0f} s]", flush=True)
        finally:
            for _, s in srcs:
                s.close()
            env.__exit__(None, None, None)
        km_arr = np.array([s["km"] for s in stations]); arm_arr = np.array([s["arm"] for s in stations])
        if old is not None:
            ndvi = np.concatenate([old["ndvi"], ndvi]); state = np.concatenate([old["state"], state])
            km_arr = np.concatenate([old["km"], km_arr]); arm_arr = np.concatenate([old["arm"], arm_arr])
        np.savez_compressed(p, ndvi=ndvi, state=state, offs=offs, km=km_arr, arm=arm_arr)
        print(f"pelican {date}: {100*np.mean(state==1):.1f}% of section samples valid "
              f"in {time.time()-t0:.0f} s -> {p}")


class PelicanLayer:
    def __init__(self, date, stations):
        p = os.path.join(CACHE, "pelican", f"sections_{date}.npz")
        z = np.load(p)
        self.ndvi, self.state, self.offs = z["ndvi"], z["state"], z["offs"]
        km = z["km"]; arm = z["arm"]
        self.index = {(str(a), round(float(k), 3)): i for i, (a, k) in enumerate(zip(arm, km))}
        self.res = LAYERS["pelican0827"]["res"]

    def section(self, s):
        i = self.index.get((s["arm"], round(s["km"], 3)))
        if i is None:
            return None
        return self.ndvi[i], self.state[i], self.offs


# --------------------------------------------------------------------------
# DEM
# --------------------------------------------------------------------------
class DEM:
    """GLO-30 (two tiles, EPSG:4326) or HMA 8 m (own CRS), bilinear sampling
    and slope. HMA nodata falls back to GLO-30 with a flag."""
    def __init__(self, prefer_hma=True):
        import rasterio
        from scipy.ndimage import map_coordinates
        self.mc = map_coordinates
        self.tiles = []
        self.name = "GLO-30"
        self.hma = []
        for p in GLO30:
            if os.path.exists(p):
                self.tiles.append(self._load(p))
        if not self.tiles:
            sys.exit("no GLO-30 tile in data/ - see DATA-SOURCES.md")
        if prefer_hma:
            for p in HMA:
                if os.path.exists(p):
                    self.hma.append(self._load(p, window_bbox=DEM_BBOX))
            if self.hma:
                self.name = "HMA 8 m (GLO-30 fill)"
                self._datum_check()

    def _datum_check(self):
        """HMA mosaics are heights above the WGS84 ellipsoid; GLO-30 (and
        Google Earth) are orthometric (EGM2008 / EGM96). The geoid sits
        ~-35 to -45 m here. Measure the offset on gentle ground and remove
        it, so that every elevation in the table is on the GLO-30 datum."""
        rng = np.random.default_rng(0)
        lon = rng.uniform(BBOX[0], BBOX[2], 20000); lat = rng.uniform(BBOX[1], BBOX[3], 20000)
        x, y = to_utm(lon, lat)
        glo = np.full(x.shape, np.nan, "float32"); gsl = glo.copy()
        for t in self.tiles:
            zz, ss = self._sample_tile(t, x, y)
            take = np.isnan(glo) & np.isfinite(zz); glo[take], gsl[take] = zz[take], ss[take]
        hma = np.full(x.shape, np.nan, "float32")
        for t in self.hma:
            zz, _ = self._sample_tile(t, x, y)
            take = np.isnan(hma) & np.isfinite(zz); hma[take] = zz[take]
        ok = np.isfinite(glo) & np.isfinite(hma) & (gsl < 0.15)
        d = hma[ok] - glo[ok]
        self.hma_shift = float(np.median(d))
        print(f"HMA - GLO-30 on {ok.sum()} gentle points: median {self.hma_shift:+.1f} m, "
              f"IQR {np.percentile(d, 25):+.1f}..{np.percentile(d, 75):+.1f}; "
              f"HMA shifted by {-self.hma_shift:+.1f} m onto the GLO-30 datum")
        for t in self.hma:
            t["arr"] -= self.hma_shift

    def _load(self, p, window_bbox=None):
        import rasterio
        from rasterio.warp import transform_bounds
        from rasterio.windows import from_bounds, Window
        src = rasterio.open(p)
        if window_bbox is None:
            arr = src.read(1).astype("float32"); tr = src.transform
        else:
            l, b, r, t = transform_bounds("EPSG:4326", src.crs, *window_bbox)
            w = from_bounds(max(l, src.bounds.left), max(b, src.bounds.bottom),
                            min(r, src.bounds.right), min(t, src.bounds.top), src.transform)
            w = Window(int(w.col_off), int(w.row_off), int(w.width), int(w.height))
            arr = src.read(1, window=w).astype("float32"); tr = src.window_transform(w)
        nod = src.nodata
        if nod is not None:
            arr[arr == nod] = np.nan
        arr[arr < -1000] = np.nan
        crs = str(src.crs)
        src.close()
        # pixel size in metres (for the on-demand slope)
        if crs.upper().startswith("EPSG:4326"):
            latc = tr.f + tr.e * arr.shape[0] / 2
            dx = abs(tr.a) * 111320.0 * math.cos(math.radians(latc))
            dy = abs(tr.e) * 110574.0
        else:
            dx, dy = abs(tr.a), abs(tr.e)
        return dict(path=p, arr=arr, tr=tr, crs=crs, dx=dx, dy=dy)

    def _sample_tile(self, t, x, y):
        from rasterio.warp import transform
        if t["crs"] == UTM:
            X, Y = x, y
        else:
            X, Y = transform(UTM, t["crs"], list(x), list(y))
            X, Y = np.asarray(X), np.asarray(Y)
        col = (X - t["tr"].c) / t["tr"].a - 0.5
        row = (Y - t["tr"].f) / t["tr"].e - 0.5
        inside = (col >= 1) & (col <= t["arr"].shape[1] - 2) & (row >= 1) & (row <= t["arr"].shape[0] - 2)
        z = np.full(x.shape, np.nan, "float32"); sl = z.copy()
        if inside.any():
            rr, cc = row[inside], col[inside]
            z[inside] = self.mc(t["arr"], [rr, cc], order=1, mode="nearest")
            # slope from bilinear samples one pixel either side (no gradient arrays in memory)
            zx1 = self.mc(t["arr"], [rr, cc + 1], order=1, mode="nearest")
            zx0 = self.mc(t["arr"], [rr, cc - 1], order=1, mode="nearest")
            zy1 = self.mc(t["arr"], [rr + 1, cc], order=1, mode="nearest")
            zy0 = self.mc(t["arr"], [rr - 1, cc], order=1, mode="nearest")
            sl[inside] = np.hypot((zx1 - zx0) / (2 * t["dx"]), (zy1 - zy0) / (2 * t["dy"]))
        return z, sl

    def sample(self, x, y):
        """z, slope (rise/run), source code (0 GLO-30, 1 HMA)."""
        x = np.asarray(x, float); y = np.asarray(y, float)
        z = np.full(x.shape, np.nan, "float32"); sl = z.copy(); srcc = np.zeros(x.shape, "int8")
        for t in self.hma:
            zz, ss = self._sample_tile(t, x, y)
            take = np.isnan(z) & np.isfinite(zz)
            z[take], sl[take], srcc[take] = zz[take], ss[take], 1
        for t in self.tiles:
            zz, ss = self._sample_tile(t, x, y)
            take = np.isnan(z) & np.isfinite(zz)
            z[take], sl[take] = zz[take], ss[take]
            # HMA slope is NaN beside a void pixel: borrow the GLO-30 slope
            fix = np.isfinite(z) & np.isnan(sl) & np.isfinite(ss)
            sl[fix] = ss[fix]
        return z, sl, srcc

    def sigma(self, slope, srcc):
        t = np.tan(np.arctan(slope))
        return np.where(srcc == 1, 1.5 + 2.0 * t, 4.0 + 6.0 * t)


# --------------------------------------------------------------------------
# the bank walk
# --------------------------------------------------------------------------
def walk(bare, valid, offs, side, gap_px, start_search_m=150.0):
    """bare/valid: arrays along the section (offs increasing = left).
    side +1 = left, -1 = right. Returns dict(status, d_trim, d_start, n_run)."""
    i0 = int(np.argmin(np.abs(offs)))
    order = range(i0, len(offs)) if side > 0 else range(i0, -1, -1)
    idx = list(order)
    # no data over the channel itself (frame edge, cloud): truncated, not
    # "no bare" - the 1 Sept Pelican frames stop short of the Hakubesi channel
    if not np.any(valid[np.abs(offs) <= 30.0]):
        return dict(status="truncated", d_trim=np.nan, d_start=np.nan, n_run=0)
    # find the start: first bare pixel within start_search_m of the centreline
    start = None
    for j in idx:
        if abs(offs[j]) > start_search_m:
            break
        if not valid[j]:
            continue
        if bare[j]:
            start = j; break
    if start is None:
        # is it cloud all the way or vegetation all the way?
        near = [j for j in idx if abs(offs[j]) <= start_search_m]
        if near and not np.any(valid[near]):
            return dict(status="truncated", d_trim=np.nan, d_start=np.nan, n_run=0)
        return dict(status="no-bare", d_trim=np.nan, d_start=np.nan, n_run=0)
    last_bare, gap, n_run = start, 0, 0
    for j in idx[idx.index(start):]:
        if not valid[j]:
            return dict(status="truncated", d_trim=np.nan, d_start=abs(offs[start]),
                        n_run=n_run, d_last=abs(offs[last_bare]))
        if bare[j]:
            last_bare, gap, n_run = j, 0, n_run + 1
        else:
            gap += 1
            if gap > gap_px:
                step = abs(offs[1] - offs[0])
                return dict(status="ok", d_trim=abs(offs[last_bare]) + step / 2,
                            d_start=abs(offs[start]), n_run=n_run, j_trim=last_bare)
    return dict(status="open", d_trim=np.nan, d_start=abs(offs[start]), n_run=n_run,
                d_last=abs(offs[last_bare]))


def s2chg_mask(post, pre, offs, gap_px):
    """Change-based stripped mask on a section: bare after AND (not bare
    before OR inside the pre-event bare channel run from the centreline)."""
    valid = np.isfinite(post) & np.isfinite(pre)
    barepre = np.isfinite(pre) & (pre < LAYERS["s2"]["bare"])
    chan = np.zeros_like(valid)
    for side_ in (1, -1):
        wp = walk(barepre, np.isfinite(pre), offs, side_, gap_px)
        if wp["status"] in ("ok", "open", "truncated"):
            dmax = wp["d_trim"] if wp["status"] == "ok" else wp.get("d_last", 0.0)
            chan |= (np.sign(offs) == side_) & (np.abs(offs) <= (dmax if np.isfinite(dmax) else 0.0))
    chan |= offs == 0
    return valid & (post < LAYERS["s2"]["bare"]) & (~barepre | chan)


# --------------------------------------------------------------------------
# stage map
# --------------------------------------------------------------------------
def stage_map(stations, dem, layers, junction_only=False, tag=""):
    from rasterio.warp import transform as rtransform
    sidex, sidey = side_streams()
    rows = []
    try:
        s2pre = S2Layer()          # the 12 Aug pre image, for the Pelican change test
    except FileNotFoundError:
        s2pre = None
        print("no Sentinel-2 cache: Pelican walks are NOT change-based (they will climb bare rock)")
    # bed profile first (needs the whole path for the envelope)
    HMAX = max(half_sec(s) for s in stations)
    dem_offs = np.arange(-HMAX, HMAX + 5, 10.0)
    Z = []
    for s in stations:
        xs = s["x"] + dem_offs * s["nx"]; ys = s["y"] + dem_offs * s["ny"]
        z, _, _ = dem.sample(xs, ys)
        z[np.abs(dem_offs) > half_sec(s)] = np.nan
        Z.append(z)
    Z = np.array(Z)
    near = np.abs(dem_offs) <= BED_HALF
    bed_raw = np.nanmin(Z[:, near], axis=1)
    overrides = []
    if os.path.exists(OVERRIDES):
        overrides = list(csv.DictReader(open(OVERRIDES)))
    bed_loc = bed_raw.copy(); bed_env = bed_raw.copy()
    for arm in ("main", "kyirong"):
        ii = [i for i, s in enumerate(stations) if s["arm"] == arm]
        if not ii:
            continue
        km = np.array([stations[i]["km"] for i in ii]); br = bed_raw[ii]
        for a, i in enumerate(ii):
            # neighbours on the side where the TRUE bed is higher (upstream on
            # the main path; up-valley on the arm): a DSM that only over-reads
            # cannot put this minimum below the true bed, so stage stays a
            # floor. (First draft used +/-300 m; in the 5 % reach at the
            # junction that reached 10-25 m downhill and inflated stage.)
            if arm == "main":
                w = (km[a] - km <= BED_ALONG / 1000.0 + 1e-9) & (km <= km[a] + 1e-9)
            else:
                w = (km - km[a] <= BED_ALONG / 1000.0 + 1e-9) & (km >= km[a] - 1e-9)
            bed_loc[i] = np.nanmin(br[w])
        if arm == "main":
            bed_env[ii] = np.fmin.accumulate(np.where(np.isfinite(br), br, np.inf))
        else:   # up the arm the bed rises: running maximum going up-valley
            bed_env[ii] = np.fmax.accumulate(np.where(np.isfinite(br), br, -np.inf))
    for i, s in enumerate(stations):
        if junction_only and not ((s["arm"] == "main" and 19.0 <= s["km"] <= 26.0)
                                  or (s["arm"] == "kyirong" and s["km"] <= 1.5)):
            continue
        base = dict(arm=s["arm"], km=round(s["km"], 3), x=round(s["x"], 1), y=round(s["y"], 1),
                    bed_raw=bed_raw[i], bed=bed_loc[i], bed_env=bed_env[i],
                    Rc=s["Rc"], turn_deg=s["turn_deg"], turn_sign=s["turn_sign"],
                    bridged=int(s["bridged"]))
        # geometry flags
        flags_both = []
        if s["arm"] == "main" and JUNCTION_KM[0] <= s["km"] <= JUNCTION_KM[1]:
            flags_both.append("junction")
        if s["turn_deg"] > TURN_HEADON:
            flags_both.append("sharp-bend")
        if s["bridged"]:
            flags_both.append("bridged-centreline")
        dside = np.hypot(sidex - s["x"], sidey - s["y"])
        sv = dside <= SIDEVALLEY_M
        side_flag = {1: False, -1: False}
        if sv.any():
            rel = ((sidex[sv] - s["x"]) * s["nx"] + (sidey[sv] - s["y"]) * s["ny"])
            for r_ in rel:
                side_flag[1 if r_ > 0 else -1] = True
        for lname, layer in layers.items():
            cfg = LAYERS[lname]
            cap_flag = {}
            if lname in ("s2", "s2chg"):
                hs = half_sec(s)
                offs = np.arange(-hs, hs + 5, 10.0)
                xs = s["x"] + offs * s["nx"]; ys = s["y"] + offs * s["ny"]
                post, pre = layer.sample(xs, ys)
                valid = np.isfinite(post)
                bare = valid & (post < cfg["bare"])
                vegpre = np.isfinite(pre) & (pre >= VEG_PRE)
                barepre = np.isfinite(pre) & (pre < cfg["bare"])
                if lname == "s2chg":
                    valid = valid & np.isfinite(pre)
                    bare = s2chg_mask(post, pre, offs, cfg["gap"])
            else:
                sec = layer.section(s)
                if sec is None:
                    continue
                nd, state, offs = sec
                valid = state == 1
                bare = valid & (nd < cfg["bare"])
                vegpre = np.zeros_like(valid); barepre = np.zeros_like(valid)
                xs = s["x"] + offs * s["nx"]; ys = s["y"] + offs * s["ny"]
                cap_flag = {1: "", -1: ""}
                if s2pre is not None:
                    # NDVI alone walks straight up bare rock above the mud
                    # line (first junction run: 2,040-2,190 m), and a 10 m
                    # "not bare before" test does not stop it on sparsely
                    # vegetated rock walls (second run). So the Pelican walk
                    # only REFINES the 10 m change-based boundary: it may end
                    # anywhere inside d_s2chg + 15 m; if it would go further it
                    # is stopped there and flagged capped-by-s2chg. Where the
                    # S2 walk on that side is cloud-truncated the Pelican walk
                    # is uncapped and flagged.
                    post10, pre = s2pre.sample(xs, ys)
                    vegpre = np.isfinite(pre) & (pre >= VEG_PRE)
                    barepre = np.isfinite(pre) & (pre < LAYERS["s2"]["bare"])
                    gap10 = int(round(10.0 / cfg["res"]))
                    chg = s2chg_mask(post10, pre, offs, gap10)
                    for side_ in (1, -1):
                        wc = walk(chg, np.isfinite(post10) & np.isfinite(pre), offs, side_, gap10)
                        this = np.sign(offs) == side_
                        if wc["status"] == "ok":
                            beyond = this & (np.abs(offs) > wc["d_trim"] + 15.0)
                            if np.any(bare[beyond] & valid[beyond]):
                                # would the Pelican run have continued past the cap?
                                wtest = walk(bare, valid, offs, side_, cfg["gap"])
                                if wtest["status"] != "ok" or wtest["d_trim"] > wc["d_trim"] + 15.0:
                                    cap_flag[side_] = "capped-by-s2chg"
                            bare = bare & ~beyond
                            valid = valid | beyond      # the cap is a boundary, not cloud
                        else:
                            cap_flag[side_] = f"uncapped-s2-{wc['status']}"
            if not valid.any():
                continue
            rec = dict(base); rec["layer"] = lname
            rec["valid_frac"] = float(valid.mean())
            for side, lab in ((1, "L"), (-1, "R")):
                w = walk(bare, valid, offs, side, cfg["gap"])
                rec[f"status_{lab}"] = w["status"]
                rec[f"d_{lab}"] = w["d_trim"]
                rec[f"d_start_{lab}"] = w.get("d_start", np.nan)
                rec[f"d_last_{lab}"] = w.get("d_last", np.nan)
                fl = list(flags_both)
                if side_flag[side]:
                    fl.append("side-valley")
                if lname.startswith("pelican") and cap_flag.get(side):
                    fl.append(cap_flag[side])
                for o in overrides:
                    if (o["arm"] == s["arm"] and o["bank"] in (lab, "both")
                            and float(o["km_from"]) - 1e-6 <= s["km"] <= float(o["km_to"]) + 1e-6):
                        fl.append("manual:" + o["flag"])
                if w["status"] == "ok":
                    j = w["j_trim"]
                    xt, yt = xs[j], ys[j]
                    lo, la = to_lonlat([xt], [yt])
                    z, sl, srcc = dem.sample(np.array([xt]), np.array([yt]))
                    rec[f"lon_{lab}"], rec[f"lat_{lab}"] = round(float(lo[0]), 6), round(float(la[0]), 6)
                    rec[f"z_{lab}"] = float(z[0]); rec[f"slope_{lab}"] = float(sl[0])
                    sig_place = cfg["place"] * cfg["res"] * float(sl[0])
                    sig_dem = float(dem.sigma(sl, srcc)[0])
                    rec[f"sig_{lab}"] = math.hypot(sig_place, sig_dem)
                    rec[f"dem_src_{lab}"] = int(srcc[0])
                    rec[f"stage_{lab}"] = float(z[0]) - bed_loc[i]
                    if lname in ("s2", "s2chg") or s2pre is not None:
                        run = (np.abs(offs) <= w["d_trim"]) & (np.sign(offs) == side) | (offs == 0)
                        rec[f"changed_{lab}"] = int(np.any(vegpre[run]))
                        # was the trimline pixel itself bare BEFORE the event?
                        # then the boundary found is a pre-existing bare/veg
                        # edge (rock, scree, road) and the mud line may be lower
                        rec[f"prebare_{lab}"] = int(bool(barepre[j]))
                        if barepre[j]:
                            fl.append("prebare-at-trim")
                        # pre-event bare run from the centreline (channel width before)
                        wp = walk(barepre, np.isfinite(pre), offs, side, cfg["gap"])
                        rec[f"d_pre_{lab}"] = wp["d_trim"] if wp["status"] == "ok" else np.nan
                        if not rec[f"changed_{lab}"]:
                            fl.append("no-change-in-run")
                else:
                    for k in ("lon", "lat", "z", "slope", "sig", "stage", "dem_src", "changed", "d_pre", "prebare"):
                        rec[f"{k}_{lab}"] = np.nan
                rec[f"flags_{lab}"] = ";".join(fl) if fl else ""
            # both-bank quantities
            okL = rec["status_L"] == "ok"; okR = rec["status_R"] == "ok"
            rec["width"] = rec["d_L"] + rec["d_R"] if (okL and okR) else np.nan
            clean = lambda lab: rec[f"status_{lab}"] == "ok" and not rec[f"flags_{lab}"]
            st_ = [rec[f"stage_{lab}"] for lab in ("L", "R") if clean(lab)]
            rec["stage"] = float(np.mean(st_)) if st_ else np.nan
            rec["stage_n"] = len(st_)
            rec["v_super"] = rec["v_lo"] = rec["v_hi"] = rec["dh"] = rec["Q"] = rec["A"] = rec["Fr"] = np.nan
            rec["outer"] = ""; rec["v_quality"] = ""
            if okL and okR and np.isfinite(s["Rc"]) and s["Rc"] < RC_MAX and s["turn_sign"] != 0 \
                    and "sharp-bend" not in flags_both and "junction" not in flags_both:
                outer = "R" if s["turn_sign"] > 0 else "L"
                inner = "L" if outer == "R" else "R"
                dh = rec[f"z_{outer}"] - rec[f"z_{inner}"]
                sig = math.hypot(rec[f"sig_{outer}"], rec[f"sig_{inner}"])
                rec["outer"] = outer; rec["dh"] = dh; rec["dh_sig"] = sig
                if dh > sig and rec["width"] > 20:
                    v = math.sqrt(G * s["Rc"] * dh / rec["width"])
                    rec["v_super"] = v
                    rec["v_lo"] = math.sqrt(G * s["Rc"] * 0.7 * max(dh - sig, 0.5) / (rec["width"] * 1.3))
                    rec["v_hi"] = math.sqrt(G * s["Rc"] * 1.3 * (dh + sig) / (rec["width"] * 0.7))
                    eta = 0.5 * (rec["z_L"] + rec["z_R"])
                    hm = eta - bed_loc[i]
                    rec["Fr"] = v / math.sqrt(G * hm) if hm > 0 else np.nan
                    # strong = the pair means something: dh > 2 sigma, a bend at
                    # least twice as wide as the channel, Froude in the range
                    # the forced-vortex relation is validated for (0.5-2.5,
                    # Aberg et al. 2024 via geopera's superelevation.py)
                    strong = (dh > 2 * sig and s["Rc"] >= 2 * rec["width"]
                              and np.isfinite(rec["Fr"]) and 0.5 <= rec["Fr"] <= 2.5)
                    rec["v_quality"] = "strong" if strong else "weak"
                    if strong:
                        A, W = wet_area(Z[i], dem_offs, eta)
                        rec["A"] = A; rec["Q"] = A * v * SURFACE_TO_MEAN
            rows.append(rec)
    return rows, (dem_offs, Z)


def wet_area(z, offs, eta):
    z = np.where(np.isfinite(z), z, 9999.0)
    near = np.abs(offs) <= BED_HALF
    imin = int(np.flatnonzero(near)[np.argmin(z[near])])
    if eta <= z[imin]:
        return 0.0, 0.0
    lo = imin
    while lo > 0 and z[lo - 1] < eta: lo -= 1
    hi = imin
    while hi < len(z) - 1 and z[hi + 1] < eta: hi += 1
    seg = z[lo:hi + 1]; dx = abs(offs[1] - offs[0])
    return float(np.sum(np.maximum(eta - seg, 0)) * dx), float(len(seg) * dx)


# --------------------------------------------------------------------------
# geopera cross-check: their observations projected onto OUR chainage
# --------------------------------------------------------------------------
def geopera_points(path_xy):
    """geopera v1.1 trimline profile (200 m stations, HMA 8 m + GLO fill),
    projected onto OUR chainage by nearest path vertex. Their L/R convention
    is the same as ours (checked 7 Sept: GLO-30 sampled at their L/R points
    reproduces their trim_L/trim_R elevations; the mirror point does not).
    Returns one dict per (station, bank) with the absolute trimline elevation
    z, height above their thalweg h, and the offset d from their centreline."""
    p = os.path.join(CACHE, "geopera", "trimline_profile_v2.csv")
    if not os.path.exists(p):
        return []
    x, y, cum = path_xy
    rows = list(csv.DictReader(open(p)))
    out = []
    f = lambda v: float(v) if v not in ("", "nan", None) else np.nan
    for r in rows:
        X, Y = float(r["x"]), float(r["y"])
        j = int(np.argmin(np.hypot(x - X, y - Y)))
        off = float(np.hypot(x[j] - X, y[j] - Y))
        for bank in ("L", "R"):
            z = f(r[f"trim_{bank}_m"]); h = f(r[f"h_{bank}_m"])
            if not np.isfinite(z) or not np.isfinite(h) or h <= 0.5:
                continue
            out.append(dict(km=float(cum[j]), km_theirs=float(r["chainage_m"]) / 1000.0,
                            bank=bank, z=z, h=h, thalweg=f(r["thalweg_m"]), d=f(r[f"d_{bank}_m"]),
                            void=int(r[f"void_{bank}"]), offset_m=off))
    return out


def geopera_velocities(path_xy):
    p = os.path.join(CACHE, "geopera", "superelevation_velocities.geojson")
    if not os.path.exists(p):
        return []
    x, y, cum = path_xy
    d = json.load(open(p))
    out = []
    for f in d["features"]:
        pr = f["properties"]
        if pr["v_ms"] in ("", None):
            continue
        X, Y = to_utm([f["geometry"]["coordinates"][0]], [f["geometry"]["coordinates"][1]])
        j = int(np.argmin(np.hypot(x - X[0], y - Y[0])))
        out.append(dict(km=float(cum[j]), v=float(pr["v_ms"]), v_lo=float(pr["v_lo"]),
                        v_hi=float(pr["v_hi"]), flags=pr["flags"]))
    return out


# --------------------------------------------------------------------------
# robust running fit along the corridor (Dave, 7 Sept: "run a fit through
# the points so as to remove the ones that are artefacts of where the image
# becomes too hard to determine")
# --------------------------------------------------------------------------
def robust_fit(rows, half_km=FIT_HALF_KM):
    """Pool the clean bank points of the best layer at each station (Pelican
    1 Sept where it has both banks, else the Sentinel-2 change layer), then a
    running median over +/-half_km with MAD rejection: a point further than
    max(2.5 MAD, 10 m) from its window median is an OUTLIER (marked on the
    row, never averaged in). Three passes. Returns the fit at every 100 m
    station as {km: (median, p10, p90, n)} and the pooled points."""
    have_pel = {r["km"] for r in rows if r["arm"] == "main" and r["layer"] == "pelican0901"
                and r["status_L"] == "ok" and r["status_R"] == "ok"}
    pts = []
    for i, r in enumerate(rows):
        if r["arm"] != "main":
            continue
        use = r["layer"] == "pelican0901" or (r["layer"] == "s2chg" and r["km"] not in have_pel)
        if not use:
            continue
        for lab in ("L", "R"):
            if r[f"status_{lab}"] == "ok" and not r[f"flags_{lab}"] and np.isfinite(r[f"stage_{lab}"]):
                pts.append((r["km"], r[f"stage_{lab}"], r["layer"], i, lab))
    if not pts:
        return {}, pts, np.zeros(0, bool)
    km = np.array([p[0] for p in pts]); st = np.array([p[1] for p in pts])
    out = np.zeros(len(pts), bool)
    for _ in range(3):
        for j in range(len(pts)):
            w = (np.abs(km - km[j]) <= half_km) & ~out
            w[j] = True
            if w.sum() < 5:
                continue
            med = np.median(st[w]); mad = 1.4826 * np.median(np.abs(st[w] - med))
            out[j] = abs(st[j] - med) > max(2.5 * mad, 10.0)
    fit = {}
    for k in np.arange(0.0, KM_END, 0.1):
        w = (np.abs(km - k) <= half_km) & ~out
        if w.sum() >= 5:
            fit[round(float(k), 1)] = (float(np.median(st[w])), float(np.percentile(st[w], 10)),
                                       float(np.percentile(st[w], 90)), int(w.sum()))
    for (kk, ss, lay, i, lab), o in zip(pts, out):
        rows[i][f"outlier_{lab}"] = int(o)
    return fit, pts, out


def write_fit(fit, path):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["km", "stage_fit", "fit_p10", "fit_p90", "n_points"])
        for k in sorted(fit):
            m, lo, hi, n = fit[k]
            w.writerow([f"{k:.1f}", f"{m:.1f}", f"{lo:.1f}", f"{hi:.1f}", n])


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
COLS = ["arm", "km", "layer", "x", "y", "bed_raw", "bed", "bed_env",
        "status_L", "d_L", "lon_L", "lat_L", "z_L", "slope_L", "sig_L", "stage_L", "flags_L",
        "status_R", "d_R", "lon_R", "lat_R", "z_R", "slope_R", "sig_R", "stage_R", "flags_R",
        "stage", "stage_n", "width", "Rc", "turn_deg", "outer", "dh", "dh_sig",
        "v_super", "v_lo", "v_hi", "v_quality", "A", "Q", "Fr", "valid_frac",
        "changed_L", "changed_R", "d_pre_L", "d_pre_R", "d_start_L", "d_start_R",
        "d_last_L", "d_last_R", "prebare_L", "prebare_R", "outlier_L", "outlier_R",
        "dem_src_L", "dem_src_R", "bridged"]


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            o = {}
            for k in COLS:
                v = r.get(k, "")
                if isinstance(v, float):
                    o[k] = "" if not np.isfinite(v) else (f"{v:.1f}" if abs(v) > 50 else f"{v:.2f}")
                else:
                    o[k] = v
            if r.get("Q") and np.isfinite(r.get("Q", np.nan)):
                o["Q"] = f"{r['Q']:.0f}"; o["A"] = f"{r['A']:.0f}"
            for k in ("lon_L", "lat_L", "lon_R", "lat_R"):
                if np.isfinite(r.get(k, np.nan)):
                    o[k] = f"{r[k]:.6f}"
            w.writerow(o)


REACHES = [("Lhende gorge", 8.0, 21.5), ("border junction", 21.5, 22.8),
           ("Bhote Koshi gorge", 22.8, 35.6), ("Syabrubesi opening", 35.6, 40.0),
           ("Hakubesi deposit + gorge", 40.0, 46.0), ("to Betrawati", 46.0, 70.0),
           ("Betrawati to Galchhi", 70.0, 108.0), ("Galchhi to Mugling", 108.0, 150.0),
           ("Mugling to Devghat", 150.0, 200.0)]


def coverage_table(rows, arm="main"):
    lines = ["| reach | km | layer | stations | both banks | one bank | cloud-truncated | open/no-bare | clean stage pts |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, a, b in REACHES:
        for lname in LAYERS:
            rr = [r for r in rows if r["arm"] == arm and a <= r["km"] < b and r["layer"] == lname]
            if not rr:
                continue
            both = sum(r["status_L"] == "ok" and r["status_R"] == "ok" for r in rr)
            one = sum((r["status_L"] == "ok") != (r["status_R"] == "ok") for r in rr)
            trunc = sum("truncated" in (r["status_L"], r["status_R"]) for r in rr)
            openn = sum((r["status_L"] in ("open", "no-bare")) or (r["status_R"] in ("open", "no-bare")) for r in rr)
            clean = sum(r["stage_n"] for r in rr)
            n_st = len({r["km"] for r in [x for x in rows if x["arm"] == arm and a <= x["km"] < b]})
            lines.append(f"| {name} | {a:.1f}-{b:.1f} | {lname} | {n_st} | {both} | {one} | {trunc} | {openn} | {clean} |")
    return "\n".join(lines)


def summarise(rows, geo, geov, dem_name, junction_only, fit=None, fit_pts=None, fit_out=None):
    P = []
    P.append(f"DEM: {dem_name}. Stations every {STEP_M:.0f} m; sections +/-{HALF_SEC:.0f} m "
             f"(+/-1,500 m below km 70).")
    P.append(coverage_table(rows))
    if fit:
        P.append(f"\nRobust running fit (Pelican 1 Sept where both banks, else the Sentinel-2 change "
                 f"layer; window +/-{FIT_HALF_KM:.0f} km, outliers = beyond max(2.5 MAD, 10 m), 3 passes): "
                 f"{len(fit_pts)} points, {int(fit_out.sum())} outliers "
                 f"({100*fit_out.mean():.0f} %). Fit stage by reach, median of the station fits "
                 f"[median p10 - p90 of the windows]:")
        P.append("| reach | fit stage m | stations with a fit / total |")
        P.append("|---|---|---|")
        for name, a, b in REACHES:
            ks = [k for k in fit if a <= k < b]
            n_st = int(round((b - a) / 0.1))
            if ks:
                m = np.median([fit[k][0] for k in ks]); lo = np.median([fit[k][1] for k in ks])
                hi = np.median([fit[k][2] for k in ks])
                P.append(f"| {name} {a:.0f}-{b:.0f} | {m:.0f} [{lo:.0f}-{hi:.0f}] | {len(ks)} / {n_st} |")
            else:
                P.append(f"| {name} {a:.0f}-{b:.0f} | - | 0 / {n_st} |")
    P.append("\nStage above bed by reach, clean stations only (both banks ok, no flags), median [10-90 %] (n):")
    P.append("| reach | " + " | ".join(LAYERS) + " |")
    P.append("|---|" + "---|" * len(LAYERS))
    for name, a, b in REACHES:
        cells = []
        for lname in LAYERS:
            st = np.array([r["stage"] for r in rows if r["arm"] == "main" and a <= r["km"] < b
                           and r["layer"] == lname and np.isfinite(r["stage"]) and r["stage_n"] == 2])
            cells.append(f"{np.median(st):.0f} [{np.percentile(st, 10):.0f}-{np.percentile(st, 90):.0f}] ({st.size})" if st.size else "-")
        P.append(f"| {name} {a:.0f}-{b:.0f} | " + " | ".join(cells) + " |")
    # junction check
    P.append("\n### Border junction km 21.5-22.8 (Dave: bed 1,815; lee 1,875; impact cliff 1,920-1,930)")
    P.append("| km | layer | bed(raw/loc) | L: z, d, status, flags | R: z, d, status, flags |")
    P.append("|---|---|---|---|---|")
    P.append("Main path: L = left bank looking downstream (east / Nepal side at the junction), "
             "R = right (west / China side). Kyirong arm: km up the arm from the junction, "
             "L = left looking UP the arm (south-west wall, the one facing the Lhende mouth).")
    for r in rows:
        if (r["arm"] == "main" and 21.0 <= r["km"] <= 23.3) or (r["arm"] == "kyirong" and r["km"] <= 1.0):
            f = lambda lab: (f"{r[f'z_{lab}']:.0f}±{r[f'sig_{lab}']:.0f} m at {r[f'd_{lab}']:.0f} m "
                             f"({r[f'lat_{lab}']:.5f},{r[f'lon_{lab}']:.5f})"
                             if r[f"status_{lab}"] == "ok" else r[f"status_{lab}"]) + \
                            (f" [{r[f'flags_{lab}']}]" if r[f"flags_{lab}"] else "")
            P.append(f"| {r['arm'][:3]} {r['km']:.1f} | {r['layer']} | {r['bed_raw']:.0f}/{r['bed']:.0f} | {f('L')} | {f('R')} |")
    # geopera comparison, border reach
    # Kyirong arm: trimline level per bank every 0.5 km (dossier 17 wants
    # "level = pond, sloping = tongue")
    arm = [r for r in rows if r["arm"] == "kyirong"]
    if arm:
        P.append("\n### Kyirong arm, km up the arm from the junction (L = south-west wall facing the Lhende)")
        P.append("| km | layer | bed raw | L: z at d [flags] | R: z at d [flags] |")
        P.append("|---|---|---|---|---|")
        for r in arm:
            if abs(r["km"] * 2 - round(r["km"] * 2)) > 1e-6:
                continue
            f = lambda lab: (f"{r[f'z_{lab}']:.0f}±{r[f'sig_{lab}']:.0f} at {r[f'd_{lab}']:.0f}"
                             if r[f"status_{lab}"] == "ok" else r[f"status_{lab}"]) + \
                            (f" [{r[f'flags_{lab}']}]" if r[f"flags_{lab}"] else "")
            P.append(f"| {r['km']:.1f} | {r['layer']} | {r['bed_raw']:.0f} | {f('L')} | {f('R')} |")
    if not junction_only:
        # Hakubesi and Syabrubesi checks (dossier 18; geopera 11 m/s at the opening)
        for name, a, b, expect in (("Hakubesi km 42.5-45.5", 42.5, 45.5, "stills: ~45-70 m above the pre-event bed"),
                                   ("Syabrubesi opening km 35.6-40.0", 35.6, 40.0, "geopera: velocity collapse to ~11 m/s at the opening")):
            P.append(f"\n### {name} — {expect}")
            P.append("| layer | stations | L stage min/med/max (n) | R stage min/med/max (n) | clean-station stage med | v_super (km: v) |")
            P.append("|---|---|---|---|---|---|")
            for lname in LAYERS:
                rr = [r for r in rows if r["arm"] == "main" and a <= r["km"] <= b and r["layer"] == lname]
                if not rr:
                    continue
                cell = {}
                for lab in ("L", "R"):
                    v = np.array([r[f"stage_{lab}"] for r in rr if r[f"status_{lab}"] == "ok" and not r[f"flags_{lab}"]])
                    cell[lab] = f"{v.min():.0f}/{np.median(v):.0f}/{v.max():.0f} ({v.size})" if v.size else "-"
                st = np.array([r["stage"] for r in rr if np.isfinite(r["stage"])])
                vs = [f"{r['km']:.1f}: {r['v_super']:.0f}" for r in rr if np.isfinite(r["v_super"])]
                P.append(f"| {lname} | {len(rr)} | {cell['L']} | {cell['R']} | "
                         f"{(f'{np.median(st):.0f} ({st.size})' if st.size else '-')} | {', '.join(vs) or '-'} |")
        if geov:
            gv = [g for g in geov if 35.0 <= g["km"] <= 46.0]
            P.append("geopera superelevation velocities in km 35-46 (our chainage): " +
                     ", ".join(f"{g['km']:.1f}: {g['v']:.0f} ({g['v_lo']:.0f}-{g['v_hi']:.0f}){' *' if g['flags'] != '-' else ''}" for g in gv))
    if geo:
        P.append("\n### geopera v1.1 trimlines projected onto our chainage — ABSOLUTE elevations, same bank")
        P.append("(theirs: HMA 8 m + GLO fill, their thalweg; ours: this run's DEM. "
                 "'d' = metres from the centreline. Height above bed follows in brackets.)")
        for a, b in ((19.0, 26.0), (35.0, 46.0)):
            sel = [g for g in geo if a <= g["km"] <= b]
            if not sel:
                continue
            hs = np.array([g["h"] for g in sel])
            P.append(f"\nkm {a:.0f}-{b:.0f}: geopera n={len(sel)}, heights above their thalweg "
                     f"min/median/max {hs.min():.0f}/{np.median(hs):.0f}/{hs.max():.0f} m")
            ours = [r for r in rows if r["arm"] == "main" and a <= r["km"] <= b]
            for lname in LAYERS:
                st = np.array([r["stage"] for r in ours if r["layer"] == lname and np.isfinite(r["stage"])])
                st_all = np.array([r[f"stage_{lab}"] for r in ours if r["layer"] == lname
                                   for lab in ("L", "R") if r[f"status_{lab}"] == "ok"])
                if st_all.size:
                    P.append(f"  ours {lname}: clean stations n={st.size} "
                             f"{(f'{st.min():.0f}/{np.median(st):.0f}/{st.max():.0f}' if st.size else '-')} m; "
                             f"all ok banks n={st_all.size} {st_all.min():.0f}/{np.median(st_all):.0f}/{st_all.max():.0f} m")
            # paired differences per layer
            for lname in LAYERS:
                dz = []
                for g in sel:
                    cand = [r for r in ours if r["layer"] == lname and abs(r["km"] - g["km"]) <= 0.12]
                    if not cand:
                        continue
                    r = min(cand, key=lambda r: abs(r["km"] - g["km"]))
                    if r[f"status_{g['bank']}"] == "ok" and not r[f"flags_{g['bank']}"]:
                        dz.append(r[f"z_{g['bank']}"] - g["z"])
                if dz:
                    dz = np.array(dz)
                    P.append(f"  {lname} minus geopera, same bank, unflagged stations: n={dz.size}, "
                             f"median {np.median(dz):+.0f} m, 10-90 % {np.percentile(dz, 10):+.0f}..{np.percentile(dz, 90):+.0f} m")
            P.append(f"\n| our km | bank | geopera z at d (h above thalweg) | ours: {' / '.join(LAYERS)}: z at d (stage) [flags] |")
            P.append("|---|---|---|---|")
            for g in sorted(sel, key=lambda g: (g["km"], g["bank"])):
                cells = []
                for lname in LAYERS:
                    cand = [r for r in ours if r["layer"] == lname and abs(r["km"] - g["km"]) <= 0.12]
                    if not cand:
                        cells.append("-"); continue
                    r = min(cand, key=lambda r: abs(r["km"] - g["km"]))
                    lab = g["bank"]
                    if r[f"status_{lab}"] == "ok":
                        cells.append(f"{r[f'z_{lab}']:.0f}±{r[f'sig_{lab}']:.0f} at {r[f'd_{lab}']:.0f} ({r[f'stage_{lab}']:.0f})"
                                     + (f" [{r[f'flags_{lab}']}]" if r[f"flags_{lab}"] else ""))
                    else:
                        cells.append(r[f"status_{lab}"])
                P.append(f"| {g['km']:.1f} | {g['bank']} | {g['z']:.0f} at {g['d']:.0f} ({g['h']:.0f}){'*' if g['void'] else ''} | "
                         + " / ".join(cells) + " |")
    return "\n".join(P)


def figure(rows, geo, geov, dem_name, path, fit=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    main = [r for r in rows if r["arm"] == "main"]
    fig, ax = plt.subplots(4, 1, figsize=(22, 13), sharex=True,
                           gridspec_kw={"height_ratios": [3, 1.6, 1.6, 0.7]})
    col = {"s2": "#2a78d6", "s2chg": "#1f9e89", "pelican0827": "#eb6834", "pelican0901": "#8e44ad"}
    for lname, c in col.items():
        rr = [r for r in main if r["layer"] == lname]
        for lab, mk in (("L", "^"), ("R", "v")):
            ok = [r for r in rr if r[f"status_{lab}"] == "ok"]
            clean = [r for r in ok if not r[f"flags_{lab}"]]
            flg = [r for r in ok if r[f"flags_{lab}"]]
            if clean:
                ax[0].errorbar([r["km"] for r in clean], [r[f"stage_{lab}"] for r in clean],
                               yerr=[r[f"sig_{lab}"] for r in clean], fmt=mk, ms=3, color=c,
                               ecolor=c, elinewidth=0.5, alpha=0.8, lw=0,
                               label=f"{lname} {'left' if lab=='L' else 'right'} bank")
            if flg:
                ax[0].plot([r["km"] for r in flg], [r[f"stage_{lab}"] for r in flg], mk, ms=3,
                           mfc="none", color=c, alpha=0.5)
    if geo:
        ax[0].plot([g["km"] for g in geo], [g["h"] for g in geo], "x", color="#444", ms=4,
                   alpha=0.7, label="geopera v1.1 trimlines (HMA 8 m; their thalweg)")
    for km, (lo, hi) in MODEL_DEPTHS.items():
        ax[0].plot([km, km], [lo, hi], "-", color="#1baf7a", lw=6, alpha=0.5)
    ax[0].plot([], [], "-", color="#1baf7a", lw=6, alpha=0.5, label="dossier 18 passing-run peak depths")
    ax[0].plot([22.0], [60], "s", color="k", ms=6, label="Dave: lee mud line 60 m above bed (GE)")
    ax[0].plot([22.0, 22.0], [105, 115], "-", color="k", lw=3, label="Dave: impact cliff 105-115 m")
    ax[0].plot([43.5, 43.5], [45, 70], "-", color="#d62728", lw=3, label="Hakubesi stills ~45-70 m")
    for km, (lab, h) in GAUGE_STAGE.items():
        ax[0].plot([km], [h], "D", color="#ff7f0e", ms=6)
    ax[0].plot([], [], "D", color="#ff7f0e", ms=6, label="gauge stage rise (Galchhi, Devghat; a floor)")
    if fit:
        # draw the fit in segments; never bridge a gap wider than the window
        ks = sorted(fit); segs, cur = [], [ks[0]]
        for k0, k1 in zip(ks[:-1], ks[1:]):
            if k1 - k0 > FIT_HALF_KM:
                segs.append(cur); cur = []
            cur.append(k1)
        segs.append(cur)
        for j, seg in enumerate(segs):
            ax[0].fill_between(seg, [fit[k][1] for k in seg], [fit[k][2] for k in seg], color="k", alpha=0.12, lw=0)
            ax[0].plot(seg, [fit[k][0] for k in seg], "-", color="k", lw=1.2,
                       label=(f"robust running fit (±{FIT_HALF_KM:.0f} km median; band = window p10-p90; "
                              "broken where no fit)") if j == 0 else None)
    ax[0].set_ylabel("stage above local bed (m)")
    ax[0].set_ylim(0, 200)
    ax[0].legend(fontsize=7, ncol=3, loc="upper right")
    ax[0].set_title(f"Trimline stage profile, {dem_name}; hollow markers = head-on / side-valley / junction "
                    "(run-up, not stage); stripped-ground boundary is a FLOOR on the water surface", fontsize=9)
    for lname, c in col.items():
        for q, mfc in (("strong", c), ("weak", "none")):
            rr = [r for r in main if r["layer"] == lname and np.isfinite(r["v_super"]) and r["v_quality"] == q]
            if rr:
                ax[1].errorbar([r["km"] for r in rr], [r["v_super"] for r in rr],
                               yerr=[[r["v_super"] - r["v_lo"] for r in rr], [r["v_hi"] - r["v_super"] for r in rr]],
                               fmt="o", ms=3.5, color=c, mfc=mfc, elinewidth=0.4 if q == "strong" else 0.2,
                               lw=0, alpha=1 if q == "strong" else 0.5,
                               label=f"{lname} superelevation, {q}" + (" (dh>2σ, Rc≥2W, Fr 0.5-2.5)" if q == "strong" else ""))
    if geov:
        ax[1].errorbar([g["km"] for g in geov], [g["v"] for g in geov],
                       yerr=[[g["v"] - g["v_lo"] for g in geov], [g["v_hi"] - g["v"] for g in geov]],
                       fmt="x", color="#444", ms=4, elinewidth=0.4, lw=0, alpha=0.7, label="geopera v1.1")
    ax[1].axhline(11, color="#999", ls=":", lw=1); ax[1].text(66, 12, "11 m/s (geopera, Syabrubesi)", fontsize=7)
    ax[1].set_ylabel("surface velocity (m/s)"); ax[1].set_ylim(0, 120); ax[1].legend(fontsize=6, ncol=3)
    for lname, c in col.items():
        rr = [r for r in main if r["layer"] == lname and np.isfinite(r["Q"])]
        if rr:
            ax[2].plot([r["km"] for r in rr], [r["Q"] / 1e3 for r in rr], "o", ms=3, color=c, label=lname)
    ax[2].set_ylabel("Q = A x 0.85 v, strong pairs only (10³ m³/s)"); ax[2].legend(fontsize=7)
    # coverage strip
    for k, (lname, c) in enumerate(col.items()):
        rr = [r for r in main if r["layer"] == lname]
        for r in rr:
            n = (r["status_L"] == "ok") + (r["status_R"] == "ok")
            ax[3].plot([r["km"]], [k], "|", color=c if n == 2 else ("#aaa" if n == 1 else "#eee"), ms=8)
    ax[3].set_yticks(range(len(col))); ax[3].set_yticklabels(list(col)); ax[3].set_ylim(-0.5, len(col) - 0.5)
    ax[3].set_xlabel("chainage from the scar (km, data/river_path.csv)")
    ax[3].set_title("coverage: colour = both banks, grey = one bank, blank = none", fontsize=8)
    for a in ax:
        a.grid(alpha=0.3)
        for km, lab in LANDMARKS:
            a.axvline(km, color="#bbb", lw=0.8)
    ax[0].set_xlim(5, KM_END)
    for km, lab in LANDMARKS:
        ax[0].text(km + 0.3, 190, lab, fontsize=7, color="#666")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    print("figure ->", path)


def junction_figure(rows, geo, dem, stations, path):
    """Plan view of the border junction: GLO-30/HMA contours, our trimline
    points per layer labelled with elevation, geopera's stations, and the
    OSM centrelines. Derived lines only - no imagery."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    jx, jy = to_utm([85.3770], [28.2781]); jx, jy = float(jx[0]), float(jy[0])
    R = 900.0
    gx, gy = np.meshgrid(np.arange(jx - R, jx + R, 15.0), np.arange(jy - R, jy + R, 15.0))
    z, _, _ = dem.sample(gx.ravel(), gy.ravel()); z = z.reshape(gx.shape)
    fig, ax = plt.subplots(figsize=(13, 12))
    cs = ax.contour(gx, gy, z, levels=np.arange(1780, 2100, 20), colors="#bbb", linewidths=0.5)
    ax.clabel(cs, levels=[1820, 1860, 1880, 1900, 1920, 1940, 1980], fontsize=6, fmt="%d")
    for lv, c in ((1875, "#1baf7a"), (1925, "#d62728")):
        ax.contour(gx, gy, z, levels=[lv], colors=c, linewidths=1.2, linestyles="--")
    for arm, c in (("main", "#333"), ("kyirong", "#777")):
        pts = [(s["x"], s["y"], s["km"]) for s in stations if s["arm"] == arm
               and abs(s["x"] - jx) < R and abs(s["y"] - jy) < R]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "-", color=c, lw=1)
        for x, y, km in pts[::2]:
            ax.text(x, y, f"{km:.1f}", fontsize=5, color=c)
    col = {"s2": "#2a78d6", "s2chg": "#1f9e89", "pelican0827": "#eb6834", "pelican0901": "#8e44ad"}
    off = {"s2": (0, 8), "s2chg": (0, -10), "pelican0827": (10, 4), "pelican0901": (10, -8)}
    for r in rows:
        for lab in ("L", "R"):
            if r[f"status_{lab}"] != "ok":
                continue
            x, y = to_utm([r[f"lon_{lab}"]], [r[f"lat_{lab}"]])
            if abs(x[0] - jx) > R or abs(y[0] - jy) > R:
                continue
            c = col.get(r["layer"], "k")
            mk = "^" if lab == "L" else "v"
            ax.plot(x[0], y[0], mk, color=c, ms=5, mfc="none" if r[f"flags_{lab}"] else c)
            dx, dy = off.get(r["layer"], (0, 0))
            ax.annotate(f"{r[f'z_{lab}']:.0f}", (x[0], y[0]), xytext=(dx, dy),
                        textcoords="offset points", fontsize=5.5, color=c)
    if geo:
        gsel = [g for g in geo if 20.5 <= g["km"] <= 23.5]
        # geopera station points sit on THEIR centreline; place them at their
        # station and label with bank and z
        p = os.path.join(CACHE, "geopera", "trimline_profile_v2.csv")
        for r in csv.DictReader(open(p)):
            x, y = float(r["x"]), float(r["y"])
            if abs(x - jx) > R or abs(y - jy) > R:
                continue
            ax.plot(x, y, "x", color="#444", ms=5)
            lab = []
            for b in ("L", "R"):
                v = r[f"trim_{b}_m"]
                if v not in ("", "nan"):
                    lab.append(f"{b}{float(v):.0f}")
            ax.annotate(" ".join(lab), (x, y), xytext=(-2, -9), textcoords="offset points",
                        fontsize=5.5, color="#444")
    ax.plot(jx, jy, "*", color="k", ms=10)
    for lname, c in col.items():
        ax.plot([], [], "s", color=c, label=lname)
    ax.plot([], [], "^", color="k", label="left bank (looking downstream / up the arm)")
    ax.plot([], [], "v", color="k", label="right bank")
    ax.plot([], [], "x", color="#444", label="geopera v1.1 station (L/R trimline z, HMA)")
    ax.plot([], [], "--", color="#1baf7a", label="1,875 m contour (Dave: lee line)")
    ax.plot([], [], "--", color="#d62728", label="1,925 m contour (Dave: impact cliff)")
    ax.legend(fontsize=7, loc="lower left")
    ax.set_aspect("equal"); ax.set_xlim(jx - R, jx + R); ax.set_ylim(jy - R, jy + R)
    ax.set_title(f"Border junction: trimline points from imagery on {dem.name} contours "
                 f"(hollow = flagged head-on / side-valley / junction). UTM 45N, m.", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150)
    print("figure ->", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["s2", "pelican", "map", "all"], default="map")
    ap.add_argument("--junction", action="store_true", help="map km 19-26 only, print the checks")
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--no-hma", action="store_true")
    ap.add_argument("--layers", default="s2,s2chg,pelican0827,pelican0901")
    ap.add_argument("--pelican-bare", type=float, default=None,
                    help="override the Pelican NDVI(b6,b3) bare threshold (rule: 0.10; the 1 Sept "
                         "histogram trough is at ~0.0 - use this for the sensitivity run only)")
    a = ap.parse_args()
    if a.pelican_bare is not None:
        for k in ("pelican0827", "pelican0901"):
            LAYERS[k]["bare"] = a.pelican_bare
        print(f"Pelican bare threshold overridden to {a.pelican_bare} (sensitivity run)")
    if a.stage in ("s2", "all"):
        stage_s2(a.refetch)
        if a.stage == "s2":
            return
    st_main, path_xy = stations_main()
    st_arm = stations_kyirong()
    stations = st_main + st_arm
    print(f"{len(st_main)} main-path stations to km {st_main[-1]['km']:.1f}; "
          f"{len(st_arm)} Kyirong-arm stations")
    if a.stage in ("pelican", "all"):
        sel = [s for s in stations if (s["arm"] == "kyirong") or (20.0 <= s["km"] <= 46.5)]
        stage_pelican(sel, a.refetch)
        if a.stage == "pelican":
            return
    dem = DEM(prefer_hma=not a.no_hma)
    print("DEM:", dem.name)
    layers = {}
    for lname in a.layers.split(","):
        try:
            if lname in ("s2", "s2chg"):
                layers[lname] = S2Layer()
            elif lname.startswith("pelican"):
                layers[lname] = PelicanLayer(lname[7:] and "2026" + lname[7:], stations)
        except FileNotFoundError as e:
            print(f"layer {lname} not available ({e}); skipped")
    if not layers:
        sys.exit("no imagery layers; run --stage s2 and/or --stage pelican first")
    rows, _ = stage_map(stations, dem, layers, junction_only=a.junction)
    geo = geopera_points(path_xy); geov = geopera_velocities(path_xy)
    tag = "_junction" if a.junction else ""
    fit, fit_pts, fit_out = ({}, [], np.zeros(0, bool))
    if not a.junction:
        fit, fit_pts, fit_out = robust_fit(rows)
        write_fit(fit, os.path.join(OUT, "trimline_fit.csv"))
        print("fit ->", os.path.join(OUT, "trimline_fit.csv"), f"({len(fit)} stations)")
    out_csv = os.path.join(OUT, f"trimlines{tag}.csv")
    write_csv(rows, out_csv)
    print("csv ->", out_csv, f"({len(rows)} rows)")
    txt = summarise(rows, geo, geov, dem.name, a.junction, fit, fit_pts, fit_out)
    print(txt)
    with open(os.path.join(OUT, f"trimline_map{tag}_RESULTS.md"), "w") as fh:
        fh.write(f"# trimline_map.py results{tag}\n\n{txt}\n")
    if a.junction:
        junction_figure(rows, geo, dem, stations, os.path.join(OUT, "trimline_junction.png"))
    else:
        figure(rows, geo, geov, dem.name, os.path.join(OUT, "trimline_profile.png"), fit)


if __name__ == "__main__":
    main()
