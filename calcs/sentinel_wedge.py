#!/usr/bin/env python3
"""
Sentinel-2 test of the UP-VALLEY BACKWATER WEDGE hypothesis.

THE QUESTION (Dave, 4 Sept). Tracing the 1,920-1,930 m stagnation elevation
measured at the border impact cliff, it stays above the valley floor for
~3.5 km up the arm above the junction. Did the flow actually GO there, or is
that just where a contour runs?

THE DISCRIMINATOR. A contour and a backwater wedge end in the SAME place - a
wedge runs until the bed climbs to the stagnation head, L = H/S. They differ in
what lies BETWEEN: a wedge strips vegetation and leaves scour the whole way; a
contour leaves the valley green. So the test is not the endpoint, it is the
presence or absence of a stripped corridor between the junction and it.

METHOD. Pull pre- and post-event Sentinel-2 L2A over the junction, compute NDVI
(vegetation index) for each, and difference them. Vegetation stripped by the
flow shows as a large NDVI drop in a connected corridor. Then measure how far
that corridor extends up the arm. No auth needed: Element84's Earth Search STAC
over the AWS public Sentinel-2 COG mirror, windowed reads so we fetch kilobytes
rather than gigabytes.

    NDVI = (NIR - RED) / (NIR + RED)  =  (B08 - B04) / (B08 + B04)

CAVEATS THE OUTPUT MUST CARRY.
  * Monsoon cloud. Scene-wide cloud cover is 39-88% over this period; the AOI
    may be clear in a cloudy scene or vice versa. Cloud and cloud-shadow both
    depress NDVI and can mimic stripping, so the SCL band is used to mask.
  * An NDVI drop shows where vegetation went, not how deep the water was. It
    bounds inundation extent, not stage.
  * 10 m pixels. A 3.5 km corridor is 350 pixels long - ample - but the
    up-valley arm is narrow and partly shadowed by its own walls.
"""
import json, os, sys, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
os.makedirs(OUT, exist_ok=True)

# junction at the border; the arm in question runs up-valley (NW) from it
JUNCTION = (28.2781, 85.3770)
BBOX = [85.28, 28.24, 85.48, 28.44]
STAC = "https://earth-search.aws.element84.com/v1/search"


def search(dt, max_cloud=90):
    q = {"collections": ["sentinel-2-c1-l2a"], "bbox": BBOX,
         "datetime": dt, "limit": 50,
         "query": {"eo:cloud_cover": {"lt": max_cloud}}}
    req = urllib.request.Request(STAC, data=json.dumps(q).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["features"]


def read_window(href, bbox):
    """Windowed read of a COG straight off S3 over HTTP - kilobytes, not GB."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.open(href) as src:
        l, b, r, t = transform_bounds("EPSG:4326", src.crs, *bbox)
        win = from_bounds(l, b, r, t, src.transform)
        arr = src.read(1, window=win)
        return arr.astype("float32"), src.window_transform(win), src.crs


def ndvi_for(feat, bbox):
    a = feat["assets"]
    red, _, _ = read_window(a["red"]["href"], bbox)
    nir, tr, crs = read_window(a["nir"]["href"], bbox)
    scl, _, _ = read_window(a["scl"]["href"], bbox)
    if red.shape != nir.shape:
        n = (min(red.shape[0], nir.shape[0]), min(red.shape[1], nir.shape[1]))
        red, nir = red[:n[0], :n[1]], nir[:n[0], :n[1]]
    # SCL: 3 cloud shadow, 8 cloud medium, 9 cloud high, 10 cirrus, 0 nodata
    from PIL import Image
    s = np.array(Image.fromarray(scl).resize((red.shape[1], red.shape[0]),
                                             Image.NEAREST))
    bad = np.isin(s, [0, 1, 3, 8, 9, 10])
    v = (nir - red) / np.maximum(nir + red, 1e-6)
    v[bad] = np.nan
    return v, tr, crs, float(np.mean(bad))


if __name__ == "__main__":
    pre = search("2026-08-01T00:00:00Z/2026-08-26T00:00:00Z")
    post = search("2026-08-26T12:00:00Z/2026-09-05T00:00:00Z")
    pick = lambda f: sorted(f, key=lambda s: s["properties"]["eo:cloud_cover"])
    print("candidate scenes (scene-wide cloud %):")
    for lab, fs in (("PRE ", pre), ("POST", post)):
        for s in pick(fs)[:4]:
            print(f"  {lab} {s['properties']['datetime'][:10]}  "
                  f"{s['properties']['eo:cloud_cover']:5.1f}%  {s['id']}")

    # A single post-event scene is hopeless here - late-August monsoon put
    # 70-100% cloud over this AOI in every pass. Build a per-pixel COMPOSITE
    # instead: for each pixel take the median of whatever is unmasked across
    # all post-event dates. Standard practice for monsoon-season change
    # detection, and it is why one cloudy scene is not the end of the test.
    def stack(feats, label):
        layers, used = [], []
        for s in pick(feats):
            try:
                v, tr, crs, bad = ndvi_for(s, BBOX)
            except Exception as e:
                print(f"  {label} {s['id'][:28]}: read failed ({e})")
                continue
            print(f"  {label} {s['properties']['datetime'][:10]}: "
                  f"{100*bad:5.1f}% of AOI masked")
            layers.append(v)
            used.append(s["properties"]["datetime"][:10])
            if bad < 0.10 and label == "pre":
                break            # one clear pre-event scene is enough
        if not layers:
            return None, []
        n = (min(l.shape[0] for l in layers), min(l.shape[1] for l in layers))
        arr = np.stack([l[:n[0], :n[1]] for l in layers])
        with np.errstate(all="ignore"):
            comp = np.nanmedian(arr, axis=0)
        cov = float(np.mean(np.isfinite(comp)))
        print(f"  -> {label} composite from {len(used)} scene(s) "
              f"{used}: {100*cov:.1f}% of AOI usable")
        return comp, used

    vp, pre_used = stack(pre, "pre")
    vq, post_used = stack(post, "post")
    if vp is None or vq is None:
        sys.exit("no usable imagery")
    n = (min(vp.shape[0], vq.shape[0]), min(vp.shape[1], vq.shape[1]))
    vp, vq = vp[:n[0], :n[1]], vq[:n[0], :n[1]]
    d = vq - vp
    both = float(np.mean(np.isfinite(d)))
    print(f"\nboth-valid coverage after compositing: {100*both:.1f}% of AOI")
    if both < 0.15:
        print("WARNING: too little overlapping clear sky to conclude anything.")
    sp = {"properties": {"datetime": (pre_used[0] if pre_used else "?")}}
    sq = {"properties": {"datetime": (post_used[0] if post_used else "?")
                         + f" +{len(post_used)-1} more"}}
    stripped = (d < -0.25) & np.isfinite(d)
    print(f"\npair: {sp['properties']['datetime']} -> "
          f"{sq['properties']['datetime']}")
    print(f"AOI {n[1]}x{n[0]} px at 10 m = {n[1]*10/1000:.1f} x "
          f"{n[0]*10/1000:.1f} km")
    print(f"pixels with NDVI drop > 0.25: {stripped.sum():,} "
          f"({100*stripped.mean():.1f}% of AOI) = "
          f"{stripped.sum()*100/1e6:.2f} km2")
    np.save(os.path.join(OUT, "wedge_ndvi_diff.npy"), d)
    np.save(os.path.join(OUT, "wedge_ndvi_pre.npy"), vp)
    np.save(os.path.join(OUT, "wedge_ndvi_post.npy"), vq)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.6))
    for a, img, t, cm, vr in (
            (ax[0], vp, f"NDVI pre  {sp['properties']['datetime']}",
             "RdYlGn", (-0.2, 0.9)),
            (ax[1], vq, f"NDVI post composite {sq['properties']['datetime']}",
             "RdYlGn", (-0.2, 0.9)),
            (ax[2], d, "NDVI change (blue = vegetation lost)",
             "RdBu", (-0.6, 0.6))):
        im = a.imshow(img, cmap=cm, vmin=vr[0], vmax=vr[1])
        a.set_title(t, fontsize=10)
        a.axis("off")
        fig.colorbar(im, ax=a, fraction=0.046)
    fig.suptitle("Sentinel-2 test of the up-valley wedge: does stripped "
                 "vegetation run ~3.5 km above the junction?", fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT, "wedge_ndvi.png")
    fig.savefig(p, dpi=140)
    print(f"figure -> {p}")
