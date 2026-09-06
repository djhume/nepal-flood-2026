#!/usr/bin/env python3
"""
ENSEMBLE v6 — the size envelope scored, for the first time, against how deep
the water got.

WHY (PLAN §10, 7 Sept). Every previous ensemble scored timing (border clock,
Syabrubesi), one speed, an erosion volume and a deposition cap, and never a
stage. Four independent lines then said the runs that pass are too small below
the junction (dossier §17–§19). The trimline map (calcs/trimline_map.py, HMA
8 m) now gives a peak-stage profile for the whole corridor with its spread.
This run adds it as observables, and changes three things the map also
settled — behind switches, so every published table still reproduces:

  1. STAGE per reach, scored inside the fit's window p10–p90 (asymmetric
     bounds, not ±%): gorge, Syabrubesi, Hakubesi, to Betrawati,
     Betrawati–Galchhi, Galchhi. The model quantity is the peak depth above
     the settled monsoon river (hmax), the map's is the stripped-ground
     boundary above the DEM bed; the reference difference (a few metres) is
     inside every band but the Galchhi one, and is noted there.
  2. VELOCITY re-specified: the model's peak section-mean speed, median over
     the gorge faces km 24–34, against the map's bend pairs there (37–47 m/s
     surface, ×0.85 for section mean → ~34) ±35%. The old observable compared
     a reach-max Q/A at km 22 with a FRONT speed — different quantities —
     and it is what capped the passing set at 34 Mm³.
  3. WIDTHS below km 34 from the mapped sections: equivalent rectangular
     width = area/stage at the mapped trimline, running median ±1 km, in
     place of the 4.8·sqrt(Q) rule (the standing suspect for every stage
     failure). Elsewhere the published widths stand.
  4. The Kyirong arm as a backwater WEDGE at the level the map measured (lee
     line, 60 m head, grade 0.017, 180 m) with the junction weir's 8 m head cap
     lifted to 60 m — without that the arm could never fill in the minutes it
     had.

Unchanged: priors (V_rel log-uniform 1–200 Mm³ etc.), the corrected border
clock 7.68 min ±30%, Syabrubesi 13 min ±50%, erosion 3.2 ±60%, the ≤12 Mm³
deposition cap. Held out: Devghat peak, Malekhu and Kalikhola clocks — the
passing runs are re-run to 10 h for those at the end.

Run:  .venv/bin/python calcs/ensemble_v6.py [n_samples]     (~200 → hours)
Writes calcs/ensemble_samples_v6.npy and output/ensemble_v6_RESULTS.md.
"""
import csv, itertools, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
import core
import unified as U
import ensemble as E          # priors, latin hypercube, draw()

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
T_END = 3.25 * 3600.0         # long enough for the Galchhi peak (front ~150 min)

# ------------------------------------------------ observables from the map --
REACHES = {   # name: (km_lo, km_hi)
    "stage_gorge":     (22.8, 35.6),
    "stage_syabru":    (35.6, 40.0),
    "stage_hakubesi":  (40.0, 46.0),
    "stage_to_betra":  (46.0, 70.0),
    "stage_betra_gal": (70.0, 108.0),
    "stage_galchhi":   (107.0, 108.2),
}
fit = np.array([(float(r["km"]), float(r["stage_fit"]), float(r["fit_p10"]), float(r["fit_p90"]))
                for r in csv.DictReader(open(os.path.join(ROOT, "output", "trimline_fit.csv")))])
OBS_BOUNDS = {}
for k, (a, b) in REACHES.items():
    m = (fit[:, 0] >= a) & (fit[:, 0] < b)
    OBS_BOUNDS[k] = (float(np.median(fit[m, 2])), float(np.median(fit[m, 3])),
                     float(np.median(fit[m, 1])), int(m.sum()))
OBS = {
    "border_min":  (7.68, 0.30, "border arrival, min"),
    "syabru_min":  (13.0, 0.50, "Syabrubesi arrival, min"),
    "v_gorge":     (34.0, 0.35, "section-mean peak speed, gorge km 24-34, m/s"),
    "erosion_Mm3": (3.2,  0.60, "erosion km 0-68, Mm3"),
}
OBS_MAX = {"deposit_Mm3": (12.0, "bulk deposition km 0-199, Mm3")}

# --------------------------------------------- widths from the mapped sections --
def trimline_widths():
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "output", "trimlines.csv")))
            if r["arm"] == "main"]
    best = {}
    for r in rows:
        try:
            km, st, A, n = float(r["km"]), float(r["stage"]), float(r["A"]), int(float(r["stage_n"]))
        except ValueError:
            continue
        if n < 2 or st <= 0 or A <= 0: continue
        fl = (r["flags_L"] + " " + r["flags_R"]).lower()
        if any(t in fl for t in ("junction", "side-valley", "manual", "cloud")): continue
        if r["outlier_L"].strip() or r["outlier_R"].strip(): continue
        pref = 0 if r["layer"] == "pelican0901" else 1 if r["layer"] == "s2chg" else 2
        if km not in best or pref < best[km][0]:
            best[km] = (pref, A / st)
    kms = np.array(sorted(best)); w = np.array([best[k][1] for k in kms])
    # running median over +/-1 km
    wm = np.array([np.median(w[(kms >= k - 1) & (kms <= k + 1)]) for k in kms])
    return kms, wm

def apply_v6_geometry():
    core.CAP_DH = 60.0
    U.set_kyirong_pond(S=0.017, h_max=60.0, width=180.0)
    kms, wm = trimline_widths()
    new = U.wn.copy()
    m = (U.x_km >= 22.8) & (U.x_km <= 108.0)
    new[m] = np.clip(np.interp(U.x_km[m], kms, wm), 30.0, 800.0)
    old = U.wn.copy()
    U.set_widths(new)
    return old, new

# ---------------------------------------------------------------- one run ----
def run(p):
    nn0 = U.R.nn.copy()
    U.R.nn = nn0 * p["n_scale"]; U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:])
    U.R.h_erode = p["h_erode"]; U._settled.clear()
    try:
        r = U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=T_END,
                       f_fine_rel=p.get("f_fine", 0.0),
                       entrain=core.entrain_opts("takahashi", f_fine=0.30))
        m68 = U.x_km <= 68.0
        ero = float((r["ero"][m68] * U.wn[m68] * U.DX).sum() / 1e6)
        dep = float((r["dep"] * U.wn * U.DX).sum() / 1e6)
        bulk = float(r["bed"].sum() / 1e6 / 0.65 + dep)
        xf = 0.5 * (U.x_km[:-1] + U.x_km[1:])
        mg = (xf >= 24.0) & (xf <= 34.0)
        o = {"border_min": r["arrival"](22.0), "syabru_min": r["arrival"](37.6),
             "v_gorge": float(np.median(r["umax"][mg])), "erosion_Mm3": ero,
             "deposit_Mm3": bulk, "_r": r,
             "arm_fill_m": float(r["hs_max"].get("Kyirong upstream arm", 0.0))}
        for k, (a, b) in REACHES.items():
            mm = (U.x_km >= a) & (U.x_km < b)
            o[k] = float(np.median(r["hmax"][mm]))
        return o
    except Exception as e:
        print(f"    run failed: {e}"); return None
    finally:
        U.R.nn = nn0; U.R.nf = 0.5 * (nn0[:-1] + nn0[1:]); U.R.h_erode = core.H_ERODE; U._settled.clear()

def score(o):
    ok = {}
    for k, (val, tol, _) in OBS.items():
        v = o[k]; ok[k] = bool(np.isfinite(v) and abs(v - val) <= tol * val)
    for k, (lo, hi, _, _) in OBS_BOUNDS.items():
        v = o[k]; ok[k] = bool(np.isfinite(v) and lo <= v <= hi)
    for k, (cap, _) in OBS_MAX.items():
        v = o[k]; ok[k] = bool(np.isfinite(v) and v <= cap)
    return ok

KEYS = list(OBS) + list(OBS_BOUNDS) + list(OBS_MAX)

if __name__ == "__main__":
    lines = []
    P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, new = apply_v6_geometry()
    P_("# Ensemble v6 — stages as observables (PLAN §10)\n")
    P_(f"{N} Latin-hypercube samples; T_END {T_END/3600:.2f} h; junction cap {core.CAP_DH:.0f} m; "
       f"Kyirong arm as wedge {U.R.side[0][4:]}; widths from the trimline sections on km 22.8–108.\n")
    P_("| reach | old width (median, m) | trimline width (median, m) |")
    P_("|---|---|---|")
    for k, (a, b) in REACHES.items():
        m = (U.x_km >= a) & (U.x_km < b)
        P_(f"| {k} {a}–{b} km | {np.median(old[m]):.0f} | {np.median(new[m]):.0f} |")
    P_("\n| observable | target | tolerance / bounds |")
    P_("|---|---|---|")
    for k, (v, t, lab) in OBS.items(): P_(f"| {lab} | {v} | ±{100*t:.0f}% |")
    for k, (lo, hi, med, n) in OBS_BOUNDS.items(): P_(f"| {k} (fit median {med:.1f}, {n} stations) | — | {lo:.1f}–{hi:.1f} m |")
    for k, (cap, lab) in OBS_MAX.items(): P_(f"| {lab} | — | ≤ {cap} |")
    P_()
    P = E.draw(N); t0 = time.time(); rows = []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = run(p)
        if o is None: continue
        ok = score(o); rows.append((p, o, ok, sum(ok.values())))
        if (i + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min, "
                  f"{sum(1 for r in rows if r[3] == len(KEYS))} full matches)", flush=True)
    full = [r for r in rows if r[3] == len(KEYS)]
    P_(f"\n## Result: {len(rows)} runs, **{len(full)} satisfy all {len(KEYS)} observables**\n")
    P_("| observable | met by |"); P_("|---|---|")
    for k in KEYS:
        P_(f"| {k} | {sum(1 for r in rows if r[2][k])} / {len(rows)} |")
    if not full:
        P_("\nNo sample satisfies everything. Pairs:\n"); P_("| pair | runs meeting both |"); P_("|---|---|")
        for a, b in itertools.combinations(KEYS, 2):
            P_(f"| {a} + {b} | {sum(1 for r in rows if r[2][a] and r[2][b])} |")
        # the nearest misses: most observables met
        best = sorted(rows, key=lambda r: -r[3])[:10]
        P_("\nNearest misses (most observables met):\n")
        P_("| V Mm3 | w0 | mu | f_fine | met | failed |"); P_("|---|---|---|---|---|---|")
        for p, o, ok, n in best:
            P_(f"| {p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.2f} | {p.get('f_fine',0):.2f} | {n} | {', '.join(k for k in KEYS if not ok[k])} |")
    else:
        V = np.array([r[0]["V_rel"] for r in full]) / 1e6
        P_("\n## Posterior (passing runs)\n"); P_("| input | median | range |"); P_("|---|---|---|")
        for nm, key, sc in (("release volume Mm3", "V_rel", 1e-6), ("liquid fraction w0", "w0", 1), ("mu_dry", "mu_dry", 1),
                            ("f_fine", "f_fine", 1), ("n_scale", "n_scale", 1), ("h_erode", "h_erode", 1)):
            arr = np.array([r[0].get(key, 0.0) for r in full]) * sc
            P_(f"| {nm} | {np.median(arr):.2f} | {arr.min():.2f} – {arr.max():.2f} |")
        P_("\n| passing run | V | w0 | f_fine | gorge | syabru | hakubesi | to_betra | betra_gal | galchhi | v_gorge | arm fill m | deposit |")
        P_("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for p, o, ok, n in sorted(full, key=lambda r: r[0]["V_rel"]):
            P_(f"| | {p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p.get('f_fine',0):.2f} | {o['stage_gorge']:.0f} | {o['stage_syabru']:.0f} | {o['stage_hakubesi']:.0f} | {o['stage_to_betra']:.0f} | {o['stage_betra_gal']:.0f} | {o['stage_galchhi']:.1f} | {o['v_gorge']:.0f} | {o['arm_fill_m']:.0f} | {o['deposit_Mm3']:.1f} |")
        # held-out: re-run passing members to 10 h
        P_("\n## Held out: Devghat peak and the lower clocks (passing runs re-run to 10 h)\n")
        P_("| V Mm3 | Devghat peak m3/s (obs ~2,900 excess) | Malekhu front min (obs 163) | Kalikhola front min (obs ~337) |"); P_("|---|---|---|---|")
        for p, o, ok, n in sorted(full, key=lambda r: r[0]["V_rel"]):
            nn0 = U.R.nn.copy(); U.R.nn = nn0 * p["n_scale"]; U.R.nf = 0.5*(U.R.nn[:-1]+U.R.nn[1:]); U.R.h_erode = p["h_erode"]; U._settled.clear()
            try:
                r = U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=10*3600.0, f_fine_rel=p.get("f_fine",0.0), entrain=core.entrain_opts("takahashi", f_fine=0.30))
                q = r["Devghat"]["q"]; tt = r["t"]; i = int(np.argmax(np.where(tt > 30, q, -1)))
                P_(f"| {p['V_rel']/1e6:.1f} | {q[i]:,.0f} @ {tt[i]:.0f} min | {r['arrival'](117.0):.0f} | {r['arrival'](185.0):.0f} |")
            except Exception as e:
                P_(f"| {p['V_rel']/1e6:.1f} | failed: {e} | | |")
            finally:
                U.R.nn = nn0; U.R.nf = 0.5*(nn0[:-1]+nn0[1:]); U.R.h_erode = core.H_ERODE; U._settled.clear()
    np.save(os.path.join(HERE, "ensemble_samples_v6.npy"),
            np.array([[r[0][k] for k in E.PRIORS] + [r[1][k] for k in KEYS] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", "ensemble_v6_RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nsaved calcs/ensemble_samples_v6.npy and output/ensemble_v6_RESULTS.md ({(time.time()-t0)/60:.0f} min)")
