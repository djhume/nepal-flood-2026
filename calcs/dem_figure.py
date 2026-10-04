"""Figure for PLAN §13: the scar in the elevation change, and one cross-section.

Reads the cache written by dem_volume.py. Writes output/dem_volume.png.
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from rasterio.warp import transform as warp_transform

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "output/cache/dem"

INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
LOSS, GAIN, MID, VOID = "#e34948", "#2a78d6", "#f0efec", "#a8a7a1"
PRE_C, POST_C = "#52514e", "#2a78d6"
CMAP = LinearSegmentedColormap.from_list("dh", ["#7a1514", LOSS, MID, GAIN, "#104281"])
CMAP.set_bad(VOID)


def main():
    g = json.load(open(C / "grid.json"))
    a, _, c, _, e, f = g["transform"]
    H, W = g["shape"]
    J = json.load(open(C / "dem_volume.json"))
    dh = np.load(C / "dh_median_coreg.npy")
    post = np.load(C / "post_wmean.npy")
    pre = post - dh
    fp10, fp30 = np.load(C / "footprint_10.npy"), np.load(C / "footprint_30.npy")
    x0, x1, y0, y1 = 353300, 357100, 3128300, 3131700
    c0, c1 = int((x0 - c) / a), int((x1 - c) / a)
    r0, r1 = int((f - y1) / -e), int((f - y0) / -e)
    ext = (x0 / 1e3, x1 / 1e3, y0 / 1e3, y1 / 1e3)
    ext_c = (x0 / 1e3, x1 / 1e3, y1 / 1e3, y0 / 1e3)

    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": "#c9c8c2"})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.8), gridspec_kw={"width_ratios": [1, 1.15]},
                                 facecolor=SURF)
    for z in (ax, bx):
        z.set_facecolor(SURF)

    im = ax.imshow(dh[r0:r1, c0:c1], cmap=CMAP, vmin=-200, vmax=200, extent=ext, interpolation="nearest")
    cs = ax.contour(pre[r0:r1, c0:c1], levels=np.arange(3600, 5600, 200), extent=ext_c,
                    colors=INK2, linewidths=0.3, alpha=0.6)
    ax.clabel(cs, fontsize=6, fmt="%d", colors=INK2)
    ax.contour(fp10[r0:r1, c0:c1].astype(float), levels=[0.5], extent=ext_c, colors=INK, linewidths=1.4)
    ax.contour(fp30[r0:r1, c0:c1].astype(float), levels=[0.5], extent=ext_c, colors=INK,
               linewidths=0.9, linestyles="--")
    pts = {"Davies": (85.5252, 28.2853), "Petley": (85.5194, 28.2765),
           "UNOSAT centroid": (85.52131874351738, 28.289125143886345)}
    for k, (lon, lat) in pts.items():
        x, y = warp_transform("EPSG:4326", "EPSG:32645", [lon], [lat])
        ax.plot(x[0] / 1e3, y[0] / 1e3, "o", ms=6, mfc=SURF, mec=INK, mew=1.2)
        off = {"UNOSAT centroid": (-8, 6), "Davies": (8, -4), "Petley": (8, -4)}[k]
        ax.annotate(k, (x[0] / 1e3, y[0] / 1e3), xytext=off, textcoords="offset points", fontsize=8,
                    color=INK, ha="right" if off[0] < 0 else "left",
                    bbox=dict(fc=SURF, ec="none", alpha=0.8, pad=1))
    yprof = f + (np.nonzero(fp10)[0].mean() + 0.5) * e      # section through the footprint centroid
    ax.plot([x0 / 1e3, x1 / 1e3], [yprof / 1e3] * 2, color=INK, lw=0.6, ls=":")
    ax.annotate("section →", (x0 / 1e3 + 0.05, yprof / 1e3 + 0.04), fontsize=7.5, color=INK2)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xlabel("km east, UTM 45N"); ax.set_ylabel("km north")
    ax.set_aspect("equal")
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.set_label("surface change, after minus before (m)", color=INK2)
    cb.outline.set_visible(False)
    ax.set_title("Elevation change at the scar, c. 2015 to 6–8 Sept 2026", loc="left", fontsize=10)
    ax.text(0.01, 0.01, "solid: footprint at −10 m   dashed: at −30 m   grey: no data   contours: before, 200 m",
            transform=ax.transAxes, fontsize=7, color=INK2, va="bottom",
            bbox=dict(fc=SURF, ec="none", alpha=0.85, pad=2))

    r = int((f - yprof) / -e)
    xs = (c + (np.arange(c0, c1) + 0.5) * a)
    zb, za = pre[r, c0:c1], post[r, c0:c1]
    inside = fp10[r, c0:c1]
    bx.fill_between(xs / 1e3, za, zb, where=inside & np.isfinite(za) & np.isfinite(zb),
                    color=LOSS, alpha=0.25, lw=0)
    bx.plot(xs / 1e3, zb, color=PRE_C, lw=2, label="before (2015–17)")
    bx.plot(xs / 1e3, za, color=POST_C, lw=2, label="after (6–8 Sept 2026)")
    i = np.nanargmin(np.abs(np.where(inside, (zb - za) - np.nanmedian((zb - za)[inside]), np.nan)))
    bx.annotate("removed", (xs[i] / 1e3, (zb[i] + za[i]) / 2), xytext=(-70, 25),
                textcoords="offset points", fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    bx.legend(frameon=False, loc="upper left", fontsize=8)
    bx.set_xlim(ext[0], ext[1])
    bx.set_xlabel("km east, UTM 45N")
    bx.set_ylabel("elevation above the WGS 84 ellipsoid (m)")
    bx.grid(axis="y", color="#e4e3df", lw=0.6)
    for s in ("top", "right"):
        bx.spines[s].set_visible(False)
    bx.set_title(f"West–east section at {yprof / 1e3:.2f} km north", loc="left", fontsize=10)

    lo, hi = J["range"]
    fig.text(0.01, -0.02,
             f"Preliminary. Detachment volume over the footprint, glacier thinning removed: "
             f"{5 * round(lo / 5):.0f}–{5 * np.ceil(hi / 5):.0f} Mm³. "
             "Data: Shean & Bhushan (2026), Zenodo 10.5281/zenodo.22842748 and .22842746, CC BY-NC 4.0. "
             "Arithmetic: calcs/dem_volume.py.", fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(ROOT / "output/dem_volume.png", dpi=130, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    main()
