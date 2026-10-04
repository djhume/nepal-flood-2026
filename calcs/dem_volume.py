"""The detachment volume, measured by differencing the pre- and post-event DEMs.

PLAN §13. Inputs are Shean & Bhushan's composites on a common 2 m grid
(calcs/dem_grid.py builds the cache). Steps, numbered as in §13c:

  2  co-register pre to post on stable ground (vertical median plus a planar
     shift solved by least squares on the terrain gradient, Nuth & Kääb style)
  3  verify on the control: stable-ground dh binned by distance from the
     corridor, as in dossier §32b; gates G1 (§13d) and G1s (§13c step 3)
  4  footprint FROM the dh: the connected region below a threshold that holds
     the scar, holes filled; gate G3 against both published areas
  5  integrate dh over it; area and mean depth beside the volume
  6  corrections stated separately: glacier thinning measured on unaffected
     glaciers at the scar's own elevations; voids (gate G2, and a cross-check
     of the gate-failed cells against two independent pre-event surfaces);
     snow bounded on off-glacier ground
  7  a range: the envelope of every choice above, then widened by the
     spatially correlated random error

Nothing here is tuned. The thresholds and gates are the ones PLAN §13 wrote
down on 4 Oct, before any of this was computed. Output:
output/dem_volume_RESULTS.md, output/dem_volume.png.
"""
import json
from pathlib import Path

import numpy as np
from scipy import ndimage
from rasterio.warp import transform as warp_transform

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "output/cache/dem"
OUT = ROOT / "output"

# published scar locations (dossier §1; Huang et al. archive) and areas
POINTS = {
    "Petley": (85.5194, 28.2765),
    "Davies": (85.5252, 28.2853),
    "Huang et al. pin": (85.515, 28.271),
    "UNOSAT centroid": (85.52131874351738, 28.289125143886345),
}
A_UNOSAT = 1.957   # km², UNOSAT FL20260826NPL detachment zone, via Huang et al. unosat_areas.json
A_ARXIV = 1.009    # km², arXiv 2609.04563 preferred source area (0.491–1.841)

# pre-registered gates (PLAN §13c step 3 and §13d)
G1_BIAS, G1_NMAD = 1.0, 3.0      # §13d
G1S_BIAS, G1S_NMAD = 0.5, 2.0    # §13c step 3, stricter
G2_VOID = 0.40
G3_TOL = 0.50

THRESHOLDS = [-5.0, -10.0, -20.0, -30.0]   # §13c: "start at −10 m"
SCORED_T = [-10.0, -20.0, -30.0]           # −5 m sits inside the glacier-thinning signal (see table)
PRIMARY_T = -10.0
CORR_L = 500.0     # m, assumed correlation range of DEM error (Rolstad et al. 2009), conservative


def nmad(x):
    x = x[np.isfinite(x)]
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def to_utm(lon, lat):
    x, y = warp_transform("EPSG:4326", "EPSG:32645", [lon], [lat])
    return x[0], y[0]


def dist_to_polyline(X, Y, px, py, step=8):
    """Distance (m) from every grid cell to a polyline, via a distance
    transform on a coarse raster of the line (8-cell blocks)."""
    hh, ww = Y.size // step + 1, X.size // step + 1
    m = np.ones((hh, ww), bool)
    xs, ys = [px[0]], [py[0]]
    for i, d in enumerate(np.hypot(np.diff(px), np.diff(py))):
        t = np.arange(1, max(int(d / 4), 1) + 1) / max(int(d / 4), 1)
        xs.extend(px[i] + t * (px[i + 1] - px[i]))
        ys.extend(py[i] + t * (py[i + 1] - py[i]))
    xs, ys = np.array(xs), np.array(ys)
    cc = ((xs - X[0]) / (X[1] - X[0]) / step).astype(int)
    rr = ((ys - Y[0]) / (Y[1] - Y[0]) / step).astype(int)
    ok = (cc >= 0) & (cc < ww) & (rr >= 0) & (rr < hh)
    m[rr[ok], cc[ok]] = False
    d = ndimage.distance_transform_edt(m) * step * abs(X[1] - X[0])
    return np.repeat(np.repeat(d, step, 0), step, 1)[:Y.size, :X.size].astype(np.float32)


def shift_surface(z, sx, sy, a=2.0):
    """z evaluated at (x + sx, y + sy); y is northing and rows run south."""
    return ndimage.shift(z, (sy / a, -sx / a), order=1, mode="constant", cval=np.nan, prefilter=False)


def solve_shift(dh, gx, gy, m):
    """Least squares dh = sx·∂z/∂x + sy·∂z/∂y + c on stable cells, trimmed at 3 NMAD."""
    keep = m & np.isfinite(dh) & np.isfinite(gx) & np.isfinite(gy)
    d, x1, x2 = dh[keep], gx[keep], gy[keep]
    for _ in range(3):
        A = np.c_[x1, x2, np.ones_like(x1)]
        sol, *_ = np.linalg.lstsq(A, d, rcond=None)
        r = d - A @ sol
        ok = np.abs(r - np.median(r)) < 3 * nmad(r)
        d, x1, x2 = d[ok], x1[ok], x2[ok]
    return sol


def coregister(ref, z, gx, gy, stable, a=2.0):
    """Shift z onto ref: horizontal by iterated least squares, then the
    vertical median. Returns the shifted surface and (east, north, up)."""
    sx = sy = 0.0
    for _ in range(3):
        d = ref - shift_surface(z, sx, sy, a)
        dsx, dsy, _ = solve_shift(d, gx, gy, stable)
        sx, sy = sx + dsx, sy + dsy
    zs = shift_surface(z, sx, sy, a)
    up = float(np.nanmedian((ref - zs)[stable]))
    return zs + up, (sx, sy, up)


def footprint(dh, seed_rc, thr):
    """The connected region of dh < thr that holds the scar, holes filled.
    'Holds the scar' = the largest component meeting a ±300 m box on the seed."""
    below = np.isfinite(dh) & (dh < thr)
    lab, n = ndimage.label(below, structure=np.ones((3, 3)))
    r, c = seed_rc
    win = lab[max(r - 150, 0):r + 150, max(c - 150, 0):c + 150]
    ids = np.unique(win[win > 0])
    if ids.size == 0:
        return np.zeros_like(below)
    sizes = ndimage.sum(np.ones_like(lab), lab, index=ids)
    return ndimage.binary_fill_holes(lab == ids[np.argmax(sizes)])


def hypsometric_fill(dh, fp, z, band=50.0):
    """Voids inside the footprint take the median dh of valid footprint cells
    in the same 50 m elevation band (McNabb et al. 2019, 'local hypsometric')."""
    out = dh.copy()
    v = fp & np.isfinite(dh)
    holes = fp & ~np.isfinite(dh)
    if not holes.any():
        return out
    zb = np.floor(z / band)
    for b in np.unique(zb[holes & np.isfinite(z)]):
        sel = v & (zb == b)
        out[holes & (zb == b)] = np.median(dh[sel]) if sel.sum() > 20 else np.median(dh[v])
    out[holes & ~np.isfinite(z)] = np.median(dh[v])
    return out


def band_thinning(dh_ref, ref_mask, z, fp, glac, step=100.0):
    """Median dh on unaffected glacier in 100 m bands over the footprint's
    elevations; returns rows and the implied volume over the footprint
    (glacier cells only, and every cell)."""
    zf = z[fp]
    rows = []
    for z0 in np.arange(np.floor(np.nanmin(zf) / step) * step, np.nanmax(zf), step):
        ref = ref_mask & (z >= z0) & (z < z0 + step) & np.isfinite(dh_ref)
        inb = fp & (z >= z0) & (z < z0 + step)
        if inb.sum() == 0:
            continue
        med = float(np.median(dh_ref[ref])) if ref.sum() > 500 else np.nan
        rows.append([z0, int(ref.sum()), med, float(nmad(dh_ref[ref])) if ref.sum() > 500 else np.nan,
                     int(inb.sum()), float((inb & glac).sum() / inb.sum())])
    meds = np.array([r[2] for r in rows])
    good = np.isfinite(meds)
    idx = np.arange(len(meds))
    for i in idx[~good]:                       # bands with no reference glacier: nearest band
        meds[i] = meds[good][np.argmin(np.abs(idx[good] - i))]
    n = np.array([r[4] for r in rows]); gs = np.array([r[5] for r in rows])
    thin_g = float(-(meds * n * gs).sum() * 4 / 1e6)
    thin_a = float(-(meds * n).sum() * 4 / 1e6)
    return rows, thin_g, thin_a


def main():
    g = json.load(open(C / "grid.json"))
    a = g["transform"][0]
    PX = a * a / 1e6                                    # km² per cell; also Mm³ per metre
    H, W = g["shape"]
    X = g["transform"][2] + (np.arange(W) + 0.5) * a
    Y = g["transform"][5] + (np.arange(H) + 0.5) * g["transform"][4]
    ld = lambda k: np.load(C / f"{k}.npy")
    post = ld("post_wmean")
    glac = ld("rgi_glacier").astype(bool)
    rep = []

    def P(s=""):
        print(s)
        rep.append(s)

    # ---------- masks ----------
    rp = np.loadtxt(ROOT / "data/river_path.csv", delimiter=",", skiprows=1)
    rx, ry = warp_transform("EPSG:4326", "EPSG:32645", list(rp[:, 2]), list(rp[:, 1]))
    hp = np.loadtxt(ROOT / "data/huang_path_utm.csv", delimiter=",", comments="#")
    d_corr = np.minimum(dist_to_polyline(X, Y, np.array(rx), np.array(ry)),
                        dist_to_polyline(X, Y, hp[:, 0], hp[:, 1]))
    sx0, sy0 = to_utm(*POINTS["Davies"])
    XX, YY = np.meshgrid(X.astype(np.float32), Y.astype(np.float32))
    d_scar = np.hypot(XX - sx0, YY - sy0)
    del XX, YY
    glac_buf = ndimage.binary_dilation(glac, iterations=50)          # +100 m
    pre_m0 = ld("pre_median")
    gz = np.gradient(pre_m0, a)
    gy, gx = -gz[0], gz[1]                                          # ∂z/∂north, ∂z/∂east
    del gz
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    stable = (d_corr > 500) & (d_scar > 2000) & ~glac_buf & (slope < 40)

    # ---------- step 2: co-registration ----------
    P("## Step 2 — co-registration on stable ground")
    pre_g0 = ld("pre_gated")
    d0 = post - pre_g0
    P(f"stable ground: off-glacier (RGI 7.0 + 100 m), >500 m from our path and Huang et al.'s, "
      f">2 km from the scar, slope <40° — {(stable & np.isfinite(d0)).sum() * PX:.1f} km²")
    P(f"before: median {np.nanmedian(d0[stable]):+.2f} m, NMAD {nmad(d0[stable]):.2f} m")
    # post is the reference; shift the pre-event surface onto it
    sx = sy = 0.0
    for _ in range(3):
        d = post - shift_surface(pre_g0, sx, sy, a)
        dsx, dsy, _ = solve_shift(d, gx, gy, stable)
        sx, sy = sx + dsx, sy + dsy
    up = float(np.nanmedian((post - shift_surface(pre_g0, sx, sy, a))[stable]))
    pre_g = shift_surface(pre_g0, sx, sy, a) + up
    pre_m = shift_surface(pre_m0, sx, sy, a) + up
    del pre_g0, pre_m0, d0
    P(f"shift applied to the pre-event surface: {sx:+.2f} m E, {sy:+.2f} m N, {up:+.2f} m up")
    dh_g = post - pre_g
    dh_m = post - pre_m
    P(f"after: median {np.nanmedian(dh_g[stable]):+.2f} m, NMAD {nmad(dh_g[stable]):.2f} m")

    # ---------- step 3: control ----------
    P("\n## Step 3 — control, post-fit, binned as dossier §32b")
    base = (d_scar > 2000) & ~glac_buf & (slope < 40)
    ctrl = []
    P("| distance from either path | n | median | NMAD |")
    P("|---|---|---|---|")
    for lo, hi in [(500, 1000), (1000, 2000), (2000, 4000), (4000, np.inf)]:
        m = base & (d_corr > lo) & (d_corr <= hi) & np.isfinite(dh_g)
        ctrl.append((lo, hi, int(m.sum()), float(np.median(dh_g[m])), float(nmad(dh_g[m]))))
        P(f"| {lo:,}–{'' if np.isinf(hi) else f'{hi:,}'} m | {m.sum():,} | {ctrl[-1][3]:+.2f} | {ctrl[-1][4]:.2f} |")
    wb, wn = max(abs(r[3]) for r in ctrl), max(r[4] for r in ctrl)
    g1 = wb <= G1_BIAS and wn <= G1_NMAD
    g1s = wb <= G1S_BIAS and wn <= G1S_NMAD
    P("\nby elevation (snow and high-terrain check):")
    P("| band | n | median | NMAD |")
    P("|---|---|---|---|")
    for z0 in range(3500, 6500, 500):
        m = stable & (pre_m >= z0) & (pre_m < z0 + 500) & np.isfinite(dh_g)
        if m.sum() > 1000:
            P(f"| {z0:,}–{z0 + 500:,} m | {m.sum():,} | {np.median(dh_g[m]):+.2f} | {nmad(dh_g[m]):.2f} |")
    P(f"\n**G1** (§13d: bias ≤ {G1_BIAS} m, NMAD ≤ {G1_NMAD} m) — worst bin {wb:.2f} m / {wn:.2f} m → "
      f"**{'PASS' if g1 else 'FAIL'}**")
    P(f"**G1s** (§13c step 3: ≲ {G1S_BIAS} m, ≲ {G1S_NMAD} m) → **{'PASS' if g1s else 'FAIL'}**")

    # the gate-failed pixels on stable ground: the reason the median needs checking
    ung = np.isfinite(dh_m) & ~np.isfinite(dh_g)
    m = (d_scar > 2000) & ~glac_buf & ung
    P(f"\nThe authors' ungated median where their gate FAILS, on stable ground: n = {m.sum():,}, "
      f"median {np.median(dh_m[m]):+.1f} m, NMAD {nmad(dh_m[m]):.1f} m, **mean {np.mean(dh_m[m]):+.1f} m**, "
      f"5th percentile {np.percentile(dh_m[m], 5):+.0f} m. Where the gate passes: mean "
      f"{np.mean(dh_g[(d_scar > 2000) & ~glac_buf & np.isfinite(dh_g)]):+.1f} m.")

    # ---------- the two independent pre-event surfaces, co-registered to the 2 m one ----------
    P("\n## Two independent pre-event surfaces, co-registered to the gated 2 m surface on stable ground")
    alt = {}
    for name, lab in [("pre_mos8m", "NSIDC HMA 8 m mosaic"), ("pre_glo30", "Copernicus GLO-30")]:
        z0 = ld(name)
        raw = float(np.nanmedian((z0 - pre_g)[stable]))
        zs, sh = coregister(pre_g, z0, gx, gy, stable, a)
        r = (zs - pre_g)[stable]
        alt[name] = zs
        P(f"{lab}: raw offset {raw:+.2f} m; shift {sh[0]:+.1f} E, {sh[1]:+.1f} N, {sh[2]:+.2f} up; "
          f"post-fit stable NMAD {nmad(r):.2f} m")
    del z0, zs

    # ---------- step 4: footprint ----------
    P("\n## Step 4 — footprint from the elevation change (ungated median, co-registered)")
    seed = (int(round((sy0 - Y[0]) / (Y[1] - Y[0]))), int(round((sx0 - X[0]) / (X[1] - X[0]))))
    lo3, hi3 = (1 - G3_TOL) * max(A_UNOSAT, A_ARXIV), (1 + G3_TOL) * min(A_UNOSAT, A_ARXIV)
    P(f"G3 window — within ±{100 * G3_TOL:.0f} % of both {A_ARXIV} (arXiv) and {A_UNOSAT} km² (UNOSAT): "
      f"{lo3:.2f}–{hi3:.2f} km²")
    P("| threshold | area km² | vs arXiv | vs UNOSAT | **G3** | void, median % | void, gated % (**G2**) | "
      "edge on void % | elevation m |")
    P("|---|---|---|---|---|---|---|---|---|")
    fps = {}
    for t in THRESHOLDS:
        fp = footprint(dh_m, seed, t)
        A = fp.sum() * PX
        ring = ndimage.binary_dilation(fp, iterations=2) & ~fp
        vm = (fp & ~np.isfinite(dh_m)).sum() / fp.sum()
        vg = (fp & ~np.isfinite(dh_g)).sum() / fp.sum()
        ev = (ring & ~np.isfinite(dh_m)).sum() / ring.sum()
        g3 = lo3 <= A <= hi3
        z = pre_m[fp]
        fps[t] = dict(fp=fp, A=A, vm=vm, vg=vg, ev=ev, g3=g3, zlo=float(np.nanmin(z)), zhi=float(np.nanmax(z)))
        P(f"| {t:.0f} m | {A:.2f} | {100 * (A / A_ARXIV - 1):+.0f} % | {100 * (A / A_UNOSAT - 1):+.0f} % | "
          f"{'PASS' if g3 else 'FAIL'} | {100 * vm:.0f} | {100 * vg:.0f} ({'PASS' if vg <= G2_VOID else 'FAIL'}) | "
          f"{100 * ev:.0f} | {np.nanmin(z):,.0f}–{np.nanmax(z):,.0f} |")

    # ---------- the gate-failed cells inside the footprint, checked against the independent surfaces ----------
    fp0 = fps[PRIMARY_T]["fp"]
    P(f"\n## Step 6b — the {100 * fps[PRIMARY_T]['vg']:.0f} % of the −10 m footprint where the authors' gate fails")
    P("| independent surface | cells covered | 2 m median minus it: median | mean | volume effect Mm³ |")
    P("|---|---|---|---|---|")
    uf = fp0 & ung
    for name, lab in [("pre_mos8m", "HMA 8 m (same archive & pipeline)"), ("pre_glo30", "GLO-30 (radar, independent)")]:
        mm = uf & np.isfinite(alt[name])
        dd = (pre_m - alt[name])[mm]
        P(f"| {lab} | {100 * mm.sum() / uf.sum():.0f} % | {np.median(dd):+.1f} m | {dd.mean():+.1f} m | "
          f"{dd.mean() * uf.sum() * PX:+.1f} |")
    P(f"(positive = the 2 m median sits higher, i.e. would overstate the loss.) Gate-failed cells hold "
      f"{-np.nansum(dh_m[uf]) * PX:.0f} Mm³ of the −10 m footprint's volume, over {uf.sum() * PX:.2f} km².")

    # ---------- step 5 and 6a: volumes, each with its own measured thinning ----------
    P("\n## Steps 5 and 6a — volume, with glacier thinning measured for each pre-event surface")
    excl = ndimage.binary_dilation(fps[-5.0]["fp"], iterations=250) | (d_corr < 1000)
    refmask = glac & ~excl
    P("Thinning reference: RGI 7.0 glacier >500 m from the −5 m footprint and >1 km from either path, "
      "median dh in 100 m bands at the footprint's own elevations, applied band by band to the "
      "footprint's glacier cells (low) or all its cells (high).")
    pres = {"2 m median (Shean & Bhushan)": pre_m, "2 m gated + hypsometric fill": pre_g,
            "HMA 8 m mosaic": alt["pre_mos8m"], "GLO-30": alt["pre_glo30"]}
    P("| footprint | pre-event surface | coverage % | raw Mm³ | thinning Mm³ | corrected Mm³ | mean depth m |")
    P("|---|---|---|---|---|---|---|")
    V = {}
    thin_rows = {}
    for t in SCORED_T:
        fp = fps[t]["fp"]
        for lab, pz in pres.items():
            d = post - pz
            cov = (fp & np.isfinite(d)).sum() / fp.sum()
            raw = float(-np.nansum(hypsometric_fill(d, fp, pre_m)[fp]) * PX)
            rows, tg, ta = band_thinning(d if lab != "2 m median (Shean & Bhushan)" else dh_g,
                                         refmask, pre_m, fp, glac)
            thin_rows[(t, lab)] = rows
            V[(t, lab)] = (raw, tg, ta, cov)
            P(f"| {t:.0f} m | {lab} | {100 * cov:.0f} | {raw:.0f} | {tg:.1f}–{ta:.1f} | "
              f"{raw - ta:.0f}–{raw - tg:.0f} | {raw / fps[t]['A']:.0f} |")
    P("\nthinning by band, −10 m footprint, 2 m surface:")
    P("| band m | reference cells | median dh m | NMAD | footprint cells | glacier share |")
    P("|---|---|---|---|---|---|")
    for r in thin_rows[(PRIMARY_T, "2 m median (Shean & Bhushan)")]:
        P(f"| {r[0]:,.0f}–{r[0] + 100:,.0f} | {r[1]:,} | {r[2]:+.1f} | {r[3]:.1f} | {r[4]:,} | {100 * r[5]:.0f} % |")

    # ---------- post-event surfaces ----------
    P("\n## Independent post-event surfaces (2 m median pre-event, each footprint)")
    P("| footprint | all-source composite | WV-2, 8 Sept | Legion-2, 6 Sept (coverage) |")
    P("|---|---|---|---|")
    pw, pl = ld("post_wv2"), ld("post_lg2")
    postv = {}
    for t in SCORED_T:
        fp = fps[t]["fp"]
        vals = []
        for ps in (post, pw, pl):
            d = ps - pre_m
            vals.append((float(-np.nansum(hypsometric_fill(d, fp, pre_m)[fp]) * PX),
                         (fp & np.isfinite(d)).sum() / fp.sum()))
        postv[t] = vals
        P(f"| {t:.0f} m | {vals[0][0]:.0f} | {vals[1][0]:.0f} | {vals[2][0]:.0f} ({100 * vals[2][1]:.0f} %) |")
    both = fp0 & np.isfinite(pw) & np.isfinite(pl)
    dd = (pw - pl)[both]
    P(f"WV-2 minus Legion-2 inside the −10 m footprint, {both.sum() * PX:.2f} km² in common: "
      f"median {np.median(dd):+.2f} m, NMAD {nmad(dd):.2f} m")
    del pw, pl

    # ---------- step 6c: snow ----------
    zlo, zhi = fps[PRIMARY_T]["zlo"], fps[PRIMARY_T]["zhi"]
    m = stable & (pre_m >= zlo) & (pre_m <= zhi) & np.isfinite(dh_g)
    snow = float(np.median(dh_g[m]))
    P(f"\n## Step 6c — snow, bounded: off-glacier stable ground at {zlo:,.0f}–{zhi:,.0f} m reads "
      f"{snow:+.2f} m (n = {m.sum():,}), worth {-snow * fp0.sum() * PX:+.1f} Mm³ over the −10 m footprint")

    # ---------- step 7: random error, spatially correlated ----------
    m = (d_scar > 2000) & ~glac_buf & (pre_m >= zlo) & (pre_m <= zhi) & np.isfinite(dh_g)
    sig = float(nmad(dh_g[m]))
    A_m2 = fp0.sum() * a * a
    sig_mean = sig * np.sqrt(np.pi * CORR_L ** 2 / (5 * A_m2)) if A_m2 > np.pi * CORR_L ** 2 else sig
    sig_V = sig_mean * A_m2 / 1e6
    P(f"\n## Step 7 — random error: stable NMAD at the scar's elevations, all slopes, {sig:.1f} m; "
      f"correlated over {CORR_L:.0f} m (Rolstad et al. 2009) → ±{sig_V:.1f} Mm³ (1σ) over the −10 m footprint")

    # ---------- the range ----------
    main_set = [k for k in V if k[1] != "2 m gated + hypsometric fill"]
    lo = min(V[k][0] - V[k][2] for k in main_set)
    hi = max(V[k][0] - V[k][1] for k in main_set)
    for t in SCORED_T:   # the post-event alternatives, corrected with the 2 m thinning
        tg, ta = V[(t, "2 m median (Shean & Bhushan)")][1:3]
        for v, cov in postv[t]:
            lo, hi = min(lo, v - ta), max(hi, v - tg)
    lo_r, hi_r = lo - 2 * sig_V, hi + 2 * sig_V
    gf = [V[(t, "2 m gated + hypsometric fill")] for t in SCORED_T]
    P("\n## The range")
    P(f"envelope of 3 thresholds × 3 pre-event surfaces × 3 post-event surfaces, each thinning-corrected: "
      f"**{lo:.0f}–{hi:.0f} Mm³**; widened by 2σ random error: **{lo_r:.0f}–{hi_r:.0f} Mm³**")
    P(f"held out of the envelope, with the reason: '2 m gated + hypsometric fill' gives "
      f"{min(v[0] - v[2] for v in gf):.0f}–{max(v[0] - v[1] for v in gf):.0f} Mm³. Its voids are the deepest "
      f"part of the scar and the fill borrows depths from the shallower edges at the same height, so it "
      f"is low by construction; the two independent surfaces above say the cells it discards are sound.")

    # ---------- context: the headwall below the scar ----------
    P("\n## Context, not part of the detachment — net change on the headwall and impact zone below the scar")
    rows, _, _ = band_thinning(dh_g, refmask, pre_m, ndimage.binary_dilation(fp0, iterations=1250) & ~fp0, glac)
    z_lo_b = np.array([r[0] for r in rows]); rate = np.array([r[2] for r in rows])
    good = np.isfinite(rate)
    ctx = {}
    for R in (1500, 2500):
        ring = (ndimage.distance_transform_edt(~fp0) * a <= R) & ~fp0 & np.isfinite(dh_g)
        th = np.interp(pre_m[ring], z_lo_b[good] + 50, rate[good]) * glac[ring]   # glacier cells only
        dc = dh_g[ring] - th
        lossv = float(-dc[dc < -10].sum() * PX); gainv = float(dc[dc > 10].sum() * PX)
        cov = ring.sum() / ((ndimage.distance_transform_edt(~fp0) * a <= R) & ~fp0).sum()
        ctx[R] = (lossv, gainv, cov)
        P(f"within {R:,} m of the footprint, outside it, gated cells only ({100 * cov:.0f} % of the ring "
          f"measured), thinning removed: lost {lossv:.0f} Mm³ in cells beyond −10 m, gained {gainv:.0f} Mm³ "
          f"in cells beyond +10 m — both LOWER bounds, because the impact zone is partly void")

    # ---------- the published points ----------
    P("\n## Where the published coordinates sit")
    P("| point | pre m | post m | dh m | inside −10 m footprint |")
    P("|---|---|---|---|---|")
    for k, (lon, lat) in POINTS.items():
        x, y = to_utm(lon, lat)
        r, c = int((y - Y[0]) / (Y[1] - Y[0])), int((x - X[0]) / (X[1] - X[0]))
        P(f"| {k} | {pre_m[r, c]:,.0f} | {post[r, c]:,.0f} | {dh_m[r, c]:+.0f} | {'yes' if fp0[r, c] else 'no'} |")
    ys_, xs_ = np.nonzero(fp0)
    cx, cy = X[xs_].mean(), Y[ys_].mean()
    lon, lat = warp_transform("EPSG:32645", "EPSG:4326", [cx], [cy])
    P(f"footprint centroid: {lat[0]:.4f} N, {lon[0]:.4f} E (UTM {cx:,.0f} E, {cy:,.0f} N)")

    # ---------- save ----------
    np.save(C / "footprint_primary.npy", fp0)
    np.save(C / "dh_median_coreg.npy", dh_m.astype(np.float32))
    np.save(C / "dh_gated_coreg.npy", dh_g.astype(np.float32))
    for t in SCORED_T:
        np.save(C / f"footprint_{int(-t)}.npy", fps[t]["fp"])
    json.dump(dict(shift=[sx, sy, up], control=ctrl, g1=g1, g1s=g1s,
                   footprints={str(t): {k: v for k, v in d.items() if k != "fp"} for t, d in fps.items()},
                   volumes={f"{k[0]}|{k[1]}": v for k, v in V.items()},
                   post={str(t): v for t, v in postv.items()}, snow=snow, sig_V=sig_V,
                   envelope=[lo, hi], range=[lo_r, hi_r], context={str(k): v for k, v in ctx.items()},
                   centroid=[float(lat[0]), float(lon[0])]),
              open(C / "dem_volume.json", "w"), indent=1, default=float)
    (OUT / "dem_volume_RESULTS.md").write_text(
        "# Detachment volume from the pre/post DEMs — output of `calcs/dem_volume.py`\n\n"
        "Data: Shean & Bhushan, Zenodo 10.5281/zenodo.22842748 (pre) and 10.5281/zenodo.22842746 "
        "(post), CC BY-NC 4.0. Cross-checks: NSIDC HMA 8 m mosaic; Copernicus GLO-30; RGI 7.0.\n\n"
        + "\n".join(rep) + "\n")


if __name__ == "__main__":
    main()
