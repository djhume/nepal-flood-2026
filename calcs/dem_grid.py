"""Common 2 m grid for the pre/post DEM differencing of PLAN §13.

Every surface is resampled (bilinear) onto the grid of Shean & Bhushan's
recommended post-event composite, cropped to the footprint of their 2 m
pre-event composite. All inputs are EPSG:32645 with heights above the WGS 84
ellipsoid, so no datum shift is needed. Data: Zenodo 10.5281/zenodo.22842746
(post) and 10.5281/zenodo.22842748 (pre), CC BY-NC 4.0, kept in
data/dem_rasuwa/ (gitignored).

Also resamples two independent pre-event surfaces (NSIDC HMA 8 m mosaic and
Copernicus GLO-30) and rasterises RGI 7.0 outlines (GLIMS WFS, CC BY 4.0).

Writes output/cache/dem/*.npy plus grid.json. Run once; dem_volume.py reads
the cache.
"""
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, transform as warp_transform, transform_bounds
from rasterio.windows import from_bounds
from rasterio.features import rasterize

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/dem_rasuwa"
OUT = ROOT / "output/cache/dem"
POST = str(D / "composites/rasuwa_post_vantor_20260827-20260908_2m_")
WV2 = str(D / "composites/rasuwa_post_wv02_20260908_B030001100EF4C10-B030001100EF4E10-B030001100EF4F10_2m_")
LG2 = D / "pairs/rasuwa_post_lg02_20260906_B12000110123B110-B12000110123B310_2m_dem_v1.0.tif"
PRE = str(D / "pre/HMA_DEM_2m_zoom/HMA_DEM_2m_zoom_")
RGI = ROOT / "data/rgi7_langtang.json"
# two independent pre-event surfaces, for the cross-check of the 2 m one:
# NSIDC HMA 8 m mosaic (Shean 2017, 10.5067/KXOVQ9L172S2; same Maxar archive and
# pipeline, different strips and compositing; ellipsoidal) and Copernicus GLO-30
# (TanDEM-X radar 2011-2015; EGM2008, so it carries the geoid offset, removed in
# dem_volume.py by co-registration). Both in data/, see DATA-SOURCES.md.
MOS8 = ROOT / "data/HMA_DEM8m_MOS_20170716_tile-676.tif"
GLO30 = ROOT / "data/Copernicus_DSM_COG_10_N28_00_E085_00_DEM.tif"


def load_on_grid(path, dst_transform, shape, resampling=Resampling.bilinear):
    """Read only the part of the source under the destination grid (+10 px)."""
    dst = np.full(shape, np.nan, dtype=np.float32)
    left, top = dst_transform.c, dst_transform.f
    right, bottom = left + shape[1] * dst_transform.a, top + shape[0] * dst_transform.e
    with rasterio.open(path) as s:
        bb = (left, bottom, right, top)
        if s.crs.to_epsg() != 32645:     # the independent pre-event surfaces
            bb = transform_bounds("EPSG:32645", s.crs, left - 200, bottom - 200, right + 200, top + 200)
        w = from_bounds(*bb, s.transform)
        w = rasterio.windows.Window(w.col_off - 10, w.row_off - 10, w.width + 20, w.height + 20)
        w = w.round_offsets().round_lengths()
        src = s.read(1, window=w, boundless=True, fill_value=s.nodata if s.nodata is not None else 0).astype(np.float32)
        src_tr = s.window_transform(w)
        src_nd = s.nodata
        if src_nd is not None:
            src[src == src_nd] = np.nan
        reproject(src, dst, src_transform=src_tr, src_crs=s.crs,
                  dst_transform=dst_transform, dst_crs="EPSG:32645",
                  resampling=resampling, src_nodata=np.nan, dst_nodata=np.nan)
    return dst


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with rasterio.open(PRE + "median_gated_v1.0.tif") as p:
        pb = p.bounds
    with rasterio.open(POST + "wmean_v1.0.tif") as s:
        w = from_bounds(pb.left, pb.bottom, pb.right, pb.top, s.transform).round_offsets().round_lengths()
        tr = s.window_transform(w)
        shape = (int(w.height), int(w.width))
        post = s.read(1, window=w).astype(np.float32)
    post[post == -9999] = np.nan
    np.save(OUT / "post_wmean.npy", post)

    layers = {
        "post_ordered": (POST + "ordered_v1.0.tif", Resampling.bilinear),
        "post_count": (POST + "count_v1.0.tif", Resampling.nearest),
        "post_source": (POST + "ordered_source_v1.0.tif", Resampling.nearest),
        "post_wv2": (WV2 + "ordered_v1.0.tif", Resampling.bilinear),
        "post_lg2": (LG2, Resampling.bilinear),
        "pre_gated": (PRE + "median_gated_v1.0.tif", Resampling.bilinear),
        "pre_median": (PRE + "median_v1.0.tif", Resampling.bilinear),
        "pre_count": (PRE + "count_v1.0.tif", Resampling.nearest),
        "pre_nmad": (PRE + "nmad_v1.0.tif", Resampling.bilinear),
        "pre_mos8m": (MOS8, Resampling.bilinear),
        "pre_glo30": (GLO30, Resampling.bilinear),
    }
    for name, (path, rs) in layers.items():
        a = load_on_grid(path, tr, shape, resampling=rs)
        if name in ("post_count", "pre_count", "post_source"):
            a[a == 0] = np.nan  # 0 is nodata in count/source layers
        np.save(OUT / f"{name}.npy", a)
        print(name, f"valid {np.isfinite(a).mean():.3f}")

    # RGI 7.0 outlines (GLIMS WFS, EPSG:4326) rasterised onto the grid
    rgi = json.load(open(RGI))
    shapes = []
    for f in rgi["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        out = []
        for poly in polys:
            rings = []
            for ring in poly:
                lon = [c[0] for c in ring]
                lat = [c[1] for c in ring]
                x, y = warp_transform("EPSG:4326", "EPSG:32645", lon, lat)
                rings.append(list(zip(x, y)))
            out.append(rings)
        shapes.append(({"type": "MultiPolygon", "coordinates": out}, 1))
    glac = rasterize(shapes, out_shape=shape, transform=tr, fill=0, dtype="uint8")
    np.save(OUT / "rgi_glacier.npy", glac)
    print("glacier fraction of grid", glac.mean().round(3))

    json.dump({"transform": list(tr)[:6], "shape": shape, "crs": "EPSG:32645"},
              open(OUT / "grid.json", "w"))
    print("grid", shape, tr)


if __name__ == "__main__":
    main()
