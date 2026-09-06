#!/usr/bin/env python3
"""
Trimline check-plot: the post-event Pelican image with the DEM contours and
the mapped trimline points drawn on it, so a mud line can be judged by eye
against what the masks found (Dave, 7 Sept: "the satellite image combined
with the topo must be the much better measurement here").

LICENCE. The Planet imagery is CC-BY-NC-4.0 (c) Planet Labs PBC. This script
writes its figures to output/cache/insets/ (gitignored) as analysis copies
for the people working on this; they must not be committed or published.
The code is ours.

    .venv/bin/python calcs/trimline_inset.py --name junction \\
        --lat 28.2795 --lon 85.3790 --half 700 --res 0.5
    .venv/bin/python calcs/trimline_inset.py --name arm \\
        --lat 28.2885 --lon 85.3700 --half 1300 --res 1.5
    .venv/bin/python calcs/trimline_inset.py --name hakubesi --date skysat0827 \\
        --lat 28.122 --lon 85.291 --half 1000 --res 1.5
"""
import argparse, csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trimline_map as tm

OUTDIR = os.path.join(tm.CACHE, "insets")
COL = {"s2": "#2a78d6", "s2chg": "#1f9e89", "pelican0827": "#eb6834", "pelican0901": "#b04cf0"}


# every open Planet collection with a visual COG: (collection path, item ids, native visual pixel m)
SOURCES = {
    "pelican0901": ("pelican-2026-09-01", tm.PELICAN["20260901"][1], 0.5),
    "pelican0827": ("pelican-2026-08-27", tm.PELICAN["20260827"][1], 0.5),
    "skysat0827": ("skysat-2026-08-27", ["20260827_020055_ssc1_u0001", "20260827_020055_ssc1_u0002"], 0.5),
    "skysat0831": ("skysat-2026-08-31", ["20260831_092523_ssc9_u0002", "20260831_092523_ssc9_u0003"], 0.5),
    "planetscope0828": ("planetscope-2026-08-28", ["20260828_045742_14_2544", "20260828_045744_48_2544",
                                                   "20260828_045746_81_2544", "20260828_045749_15_2544",
                                                   "20260828_050143_19_2520"], 3.0),
}


def read_visual(date, x0, y0, x1, y1, res):
    """RGB uint8 mosaic of a collection's visual frames over a UTM box.
    'date' is a SOURCES key; res must be native x 3^k (COG overviews)."""
    import rasterio
    from rasterio.windows import from_bounds, Window
    from rasterio.enums import Resampling
    env = rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                       CPL_VSIL_CURL_CHUNK_SIZE=4 * 1024 * 1024,
                       CPL_VSIL_CURL_CACHE_SIZE=512 * 1024 * 1024,
                       GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES")
    coll, ids, native = SOURCES[date]
    f = int(round(res / native))
    W = int(round((x1 - x0) / res)); H = int(round((y1 - y0) / res))
    rgb = np.zeros((3, H, W), "uint8")
    with env:
        for i in ids:
            href = f"{tm.PLANET}{coll}/items/{i}/{i}_visual.tif"
            with rasterio.open(href) as src:
                b = src.bounds
                if x1 < b.left or x0 > b.right or y1 < b.bottom or y0 > b.top:
                    continue
                l, r_ = max(x0, b.left), min(x1, b.right); bo, t = max(y0, b.bottom), min(y1, b.top)
                w = from_bounds(l, bo, r_, t, src.transform)
                w = Window(int(w.col_off) // f * f, int(w.row_off) // f * f,
                           int(w.width) // f * f, int(w.height) // f * f)
                if w.width < f or w.height < f:
                    continue
                oh, ow = w.height // f, w.width // f
                arr = src.read([1, 2, 3], window=w, out_shape=(3, oh, ow),
                               resampling=Resampling.average)
                wt = src.window_transform(w)
                c0 = int(round((wt.c - x0) / res)); r0 = int(round((y1 - wt.f) / res))
                rr = slice(max(r0, 0), min(r0 + oh, H)); cc = slice(max(c0, 0), min(c0 + ow, W))
                sub = arr[:, (rr.start - r0):(rr.stop - r0), (cc.start - c0):(cc.stop - c0)]
                have = rgb[:, rr, cc].sum(axis=0) > 0
                new = sub.sum(axis=0) > 0
                take = new & ~have
                block = rgb[:, rr, cc]; block[:, take] = sub[:, take]; rgb[:, rr, cc] = block
    return rgb


def stretch(rgb):
    out = np.zeros(rgb.shape, "float32")
    valid = rgb.sum(axis=0) > 0
    for k in range(3):
        v = rgb[k][valid].astype("float32")
        lo, hi = (np.percentile(v, 1), np.percentile(v, 99)) if v.size else (0, 255)
        out[k] = np.clip((rgb[k] - lo) / max(hi - lo, 1), 0, 1) ** 0.8
    out[:, ~valid] = 0.15
    return np.moveaxis(out, 0, -1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--lat", type=float, required=True); ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--half", type=float, default=700.0, help="half box size, m")
    ap.add_argument("--res", type=float, default=0.5, choices=[0.5, 1.5, 4.5, 3.0, 9.0])
    ap.add_argument("--date", default="pelican0901", choices=list(SOURCES),
                    help="imagery source (collection)")
    ap.add_argument("--layers", default="pelican0901,s2chg")
    ap.add_argument("--levels", default="1875,1925", help="highlighted contours")
    a = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    cx, cy = tm.to_utm([a.lon], [a.lat]); cx, cy = float(cx[0]), float(cy[0])
    x0, x1, y0, y1 = cx - a.half, cx + a.half, cy - a.half, cy + a.half
    print(f"box UTM45 x {x0:.0f}-{x1:.0f} y {y0:.0f}-{y1:.0f}, {a.res} m")
    rgb = read_visual(a.date, x0, y0, x1, y1, a.res)
    print(f"image {rgb.shape[2]}x{rgb.shape[1]} px, {100*np.mean(rgb.sum(axis=0)>0):.0f}% with data")
    img = stretch(rgb)
    dem = tm.DEM(prefer_hma=True)
    g = 4.0 if a.half <= 800 else 8.0
    gx, gy = np.meshgrid(np.arange(x0, x1, g), np.arange(y0, y1, g))
    z, _, _ = dem.sample(gx.ravel(), gy.ravel()); z = z.reshape(gx.shape)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.imshow(img, extent=(x0, x1, y0, y1), origin="upper", interpolation="nearest")
    zmin = np.nanpercentile(z, 1); zmax = np.nanpercentile(z, 99)
    lv = np.arange(math.floor(zmin / 10) * 10, zmax, 10)
    cs = ax.contour(gx, gy, z, levels=lv, colors="white", linewidths=0.35, alpha=0.7)
    ax.clabel(cs, levels=[l for l in lv if l % 50 == 0], fontsize=6, fmt="%d", colors="white")
    hl = [float(v) for v in a.levels.split(",") if v]
    for lvv, c in zip(hl, ("#39ff14", "#ff3030", "#ffd400")):
        ax.contour(gx, gy, z, levels=[lvv], colors=c, linewidths=1.4, linestyles="--")
        ax.plot([], [], "--", color=c, label=f"{lvv:.0f} m contour ({dem.name})")
    # centrelines with km
    st_main, _ = tm.stations_main(); st_arm = tm.stations_kyirong()
    for st, c, lab in ((st_main, "#ffffff", "km"), (st_arm, "#ffe680", "arm km")):
        pts = [s for s in st if x0 <= s["x"] <= x1 and y0 <= s["y"] <= y1]
        ax.plot([s["x"] for s in pts], [s["y"] for s in pts], "-", color=c, lw=0.8, alpha=0.8)
        for s in pts:
            if abs(s["km"] * 5 - round(s["km"] * 5)) < 1e-6:
                ax.text(s["x"], s["y"], f"{s['km']:.1f}", fontsize=6, color=c)
    # trimline points
    rows = list(csv.DictReader(open(os.path.join(tm.OUT, "trimlines.csv"))))
    layers = a.layers.split(",")
    off = {"pelican0901": (6, 5), "pelican0827": (6, -9), "s2chg": (-30, 5), "s2": (-30, -9)}
    n = 0
    for r in rows:
        if r["layer"] not in layers:
            continue
        for lab, mk in (("L", "^"), ("R", "v")):
            if r[f"status_{lab}"] != "ok" or not r[f"lon_{lab}"]:
                continue
            x, y = tm.to_utm([float(r[f"lon_{lab}"])], [float(r[f"lat_{lab}"])])
            if not (x0 <= x[0] <= x1 and y0 <= y[0] <= y1):
                continue
            c = COL[r["layer"]]; flagged = bool(r[f"flags_{lab}"])
            ax.plot(x[0], y[0], mk, color=c, ms=7, mfc="none" if flagged else c, mew=1.2)
            ax.annotate(f"{float(r[f'z_{lab}']):.0f}", (x[0], y[0]), xytext=off.get(r["layer"], (6, 5)),
                        textcoords="offset points", fontsize=6.5, color=c,
                        bbox=dict(boxstyle="round,pad=0.15", fc="black", ec="none", alpha=0.45))
            n += 1
    # geopera stations
    gp = os.path.join(tm.CACHE, "geopera", "trimline_profile_v2.csv")
    if os.path.exists(gp):
        for r in csv.DictReader(open(gp)):
            x, y = float(r["x"]), float(r["y"])
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                continue
            ax.plot(x, y, "x", color="#ffffff", ms=6, mew=1)
            lab = " ".join(f"{b}{float(r[f'trim_{b}_m']):.0f}" for b in ("L", "R")
                           if r[f"trim_{b}_m"] not in ("", "nan"))
            ax.annotate(lab, (x, y), xytext=(-4, -10), textcoords="offset points", fontsize=6, color="#dddddd")
    for lname in layers:
        ax.plot([], [], "s", color=COL[lname], label=f"{lname} trimline (▲ left / ▼ right bank; hollow = flagged)")
    ax.plot([], [], "x", color="white", label="geopera v1.1 station (their L/R trimline z)")
    ax.legend(fontsize=7, loc="lower left", facecolor="black", labelcolor="white", framealpha=0.6)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal")
    ax.set_title(f"{a.name}: Planet {a.date} visual at {a.res} m, "
                 f"contours {dem.name} every 10 m; {n} trimline points. UTM 45N (m)\n"
                 "(c) Planet Labs PBC, CC-BY-NC-4.0 - ANALYSIS COPY, output/cache only, do not commit or publish",
                 fontsize=9)
    p = os.path.join(OUTDIR, f"{a.name}_{a.date}_{a.res}m.png")
    fig.tight_layout(); fig.savefig(p, dpi=150); print("figure ->", p)


if __name__ == "__main__":
    main()
