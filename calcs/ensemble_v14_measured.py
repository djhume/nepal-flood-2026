#!/usr/bin/env python3
"""
MODEL A AT THE MEASURED VOLUME — PLAN §14a, pre-registered in commit 7f5901a
before this was run.

WHY. The DEM measurement (dossier §33) put the detachment at 110–125 Mm³,
below the 135 Mm³ floor of the prior Model A was run with (§30). Dave,
5 Oct: rerun at the lower number and see whether the fit extends downstream.

WHAT IS MODEL A'S, UNCHANGED: the engine (ensemble_v10.run), the nine upper
observables and their windows (ensemble_v13_upper.score), every prior except
V_rel. WHAT CHANGED, UNAVOIDABLY: the 4 Oct trimline fix is in the geometry
(§31d), so arm C reruns Model A's own prior on today's geometry as the
control. km 0 is not moved.

  arm M  V_rel 110–125 Mm³   the measured detachment
  arm H  V_rel 125–150 Mm³   plus 0–25 Mm³ of net headwall scour
  arm C  V_rel 135–200 Mm³   Model A's prior, the control

Every run meeting all nine is then read out downstream against windows fixed
in §14a: the Betrawati–Galchhi reach (9.4–21.1 m), Galchhi (3.5–9.9 m), and
rerun to 10 h for Malekhu (163 min ±20 %), Kalikhola (~337 min ±20 %) and the
Devghat peak (~2,900 m³/s within a factor of 2). None of those is scored.

Run:  .venv/bin/python calcs/ensemble_v14_measured.py [runs_per_arm] [workers]
Writes calcs/ensemble_samples_v14measured.npy and
       output/ensemble_v14_measured_RESULTS.md
"""
import os, sys, time
import multiprocessing as mp
os.environ.setdefault("OMP_NUM_THREADS", "1")   # 7 processes x 8 BLAS threads would fight
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
N_ARM = int(sys.argv[1]) if len(sys.argv) > 1 else 300
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 7
sys.argv = sys.argv[:1]          # ensemble_v13_upper parses argv on import
import ensemble as E
import ensemble_v6 as V6
import ensemble_v10 as V10
import ensemble_v13_upper as A

ARMS = {"M": (110e6, 125e6, "measured detachment"),
        "H": (125e6, 150e6, "detachment + 0–25 Mm³ headwall scour"),
        "C": (135e6, 200e6, "Model A's prior, today's geometry (control)")}
DOWN = {"stage_betra_gal": V6.OBS_BOUNDS["stage_betra_gal"][:2],
        "stage_galchhi": V6.OBS_BOUNDS["stage_galchhi"][:2]}
HELD = {"malekhu_min": (163.0, 0.20), "kalikhola_min": (337.0, 0.20)}
DEVGHAT = (2900.0, 2.0)


def draw(priors, n):
    U01 = E.latin_hypercube(n, len(priors)); out = {}
    for j, (name, (kind, lo, hi)) in enumerate(priors.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
                     if kind == "log" else lo + u * (hi - lo))
    return [{k: float(v[i]) for k, v in out.items()} for i in range(n)]


def one(args):
    arm, p = args
    o = V10.run(p)
    if o is None:
        return arm, p, None, None, 0
    ok = A.score(o)
    return arm, p, o, ok, sum(ok.values())


def held(p):
    """V10.held_out, returning numbers instead of a string."""
    nn0 = V10.U.R.nn.copy(); k0 = float(V10.U.R.K_loc[V10.V7.J22])
    try:
        r = V10._simulate(p, 10 * 3600.0)
        q = np.asarray(r["Devghat"]["q"], float); tt = np.asarray(r["t"], float)
        i = int(np.argmax(np.where(tt > 30, q, -1)))
        return p, dict(malekhu_min=float(r["arrival"](117.0)),
                       kalikhola_min=float(r["arrival"](185.0)),
                       devghat_q=float(q[i]), devghat_t=float(tt[i]))
    except Exception as e:
        return p, dict(error=str(e))
    finally:
        V10._restore(nn0, k0)


def held_pass(h):
    if "error" in h:
        return {"malekhu_min": False, "kalikhola_min": False, "devghat_q": False}
    ok = {k: abs(h[k] - v) <= t * v for k, (v, t) in HELD.items()}
    ok["devghat_q"] = DEVGHAT[0] / DEVGHAT[1] <= h["devghat_q"] <= DEVGHAT[0] * DEVGHAT[1]
    return ok


def main():
    lines = []
    P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, V10.BASE = V6.apply_v6_geometry()          # before the fork: workers inherit it
    jobs = []
    for arm, (lo, hi, _) in ARMS.items():
        pri = dict(A.PRIORS); pri["V_rel"] = ("lin", lo, hi)
        jobs += [(arm, p) for p in draw(pri, N_ARM)]
    P_("# Model A at the measured volume — PLAN §14a, pre-registered in 7f5901a\n")
    P_(f"{N_ARM} Latin-hypercube runs per arm, Model A's engine, observables, windows "
       "and priors except V_rel; today's geometry (trimline fix of 4 Oct). Sampler seed "
       "20260904 (ensemble.RNG), arms drawn M, H, C in that order.\n")
    P_("| arm | V_rel | represents |"); P_("|---|---|---|")
    for a, (lo, hi, lab) in ARMS.items():
        P_(f"| {a} | {lo/1e6:.0f}–{hi/1e6:.0f} Mm³ | {lab} |")
    t0 = time.time(); rows = []
    with mp.get_context("fork").Pool(WORKERS) as pool:
        for k, r in enumerate(pool.imap_unordered(one, jobs, chunksize=1)):
            rows.append(r)
            if (k + 1) % 50 == 0:
                el = time.time() - t0
                print(f"  {k+1}/{len(jobs)}  {el/60:.1f} min", flush=True)
        full = [r for r in rows if r[4] == 9]
        P_(f"\n## Upper corridor: runs meeting all nine ({(time.time()-t0)/60:.0f} min)\n")
        P_("| arm | runs | all nine | rate | stage_syabru met | " + " | ".join(A.KEYS[:4]) + " |")
        P_("|---|---|---|---|---|" + "---|" * 4)
        for a in ARMS:
            ra = [r for r in rows if r[0] == a and r[2] is not None]
            nf = sum(1 for r in ra if r[4] == 9)
            P_(f"| {a} | {len(ra)} | **{nf}** | {100*nf/max(len(ra),1):.1f} % | "
               f"{sum(1 for r in ra if r[3]['stage_syabru'])} | "
               + " | ".join(str(sum(1 for r in ra if r[3][k])) for k in A.KEYS[:4]) + " |")
        P_("\nfailure count by observable, per arm:\n")
        P_("| observable | " + " | ".join(ARMS) + " |"); P_("|---|" + "---|" * len(ARMS))
        for k in A.KEYS:
            P_(f"| {k} | " + " | ".join(
                str(sum(1 for r in rows if r[0] == a and r[2] is not None and not r[3][k]))
                for a in ARMS) + " |")
        # held out, for every full pass
        hres = dict()
        if full:
            for p, h in pool.imap_unordered(held, [r[1] for r in full]):
                hres[id_of(p)] = h

    P_("\n## Downstream, for the runs meeting all nine (none of this is scored)\n")
    P_(f"windows (§14a): Betrawati–Galchhi reach {DOWN['stage_betra_gal'][0]:.1f}–"
       f"{DOWN['stage_betra_gal'][1]:.1f} m; Galchhi {DOWN['stage_galchhi'][0]:.1f}–"
       f"{DOWN['stage_galchhi'][1]:.1f} m; Malekhu 163 min ±20 %; Kalikhola ~337 min ±20 %; "
       "Devghat peak ~2,900 m³/s within ×2\n")
    P_("| arm | V Mm³ | w0 | f_ice | T_rel s | f_wl | betra–gal m | Galchhi m | Malekhu min | "
       "Kalikhola min | Devghat m³/s | downstream met |")
    P_("|---|---|---|---|---|---|---|---|---|---|---|---|")
    summary = {a: [0, 0, 0] for a in ARMS}   # full, galchhi ok, all downstream ok
    for a in ARMS:
        for arm, p, o, ok, n in sorted((r for r in full if r[0] == a), key=lambda r: r[1]["V_rel"]):
            h = hres.get(id_of(p), {"error": "missing"})
            hp = held_pass(h)
            dg = {k: DOWN[k][0] <= o[k] <= DOWN[k][1] for k in DOWN}
            met = [k for k, v in {**dg, **hp}.items() if v]
            summary[a][0] += 1; summary[a][1] += int(dg["stage_galchhi"])
            summary[a][2] += int(all(dg.values()) and all(hp.values()))
            P_(f"| {a} | {p['V_rel']/1e6:.0f} | {p['w0']:.2f} | {p['f_ice']:.2f} | {p['T_rel']:.0f} | "
               f"{p['f_wl']:.2f} | {o['stage_betra_gal']:.1f} | {o['stage_galchhi']:.1f} | "
               f"{h.get('malekhu_min', np.nan):.0f} | {h.get('kalikhola_min', np.nan):.0f} | "
               f"{h.get('devghat_q', np.nan):,.0f} | {len(met)}/5 |")
    P_("\n| arm | all nine | + Galchhi | + all five downstream |"); P_("|---|---|---|---|")
    for a, (f, g, d) in summary.items():
        P_(f"| {a} | {f} | {g} | {d} |")
    P_("\n## Posterior by arm (only where at least 3 runs meet all nine — §14a reading 5)\n")
    for a in ARMS:
        fa = [r for r in full if r[0] == a]
        if len(fa) < 3:
            P_(f"- arm {a}: {len(fa)} — too few to summarise"); continue
        P_(f"\narm {a}, {len(fa)} runs:\n")
        P_("| input | p10 | median | p90 | prior |"); P_("|---|---|---|---|---|")
        pri = dict(A.PRIORS); pri["V_rel"] = ("lin", ARMS[a][0], ARMS[a][1])
        for key, (kind, lo, hi) in pri.items():
            arr = np.array([r[1][key] for r in fa]); sc = 1e-6 if key == "V_rel" else 1.0
            p10, p50, p90 = np.percentile(arr, [10, 50, 90])
            P_(f"| {key} | {p10*sc:.3g} | **{p50*sc:.3g}** | {p90*sc:.3g} | {lo*sc:.3g}–{hi*sc:.3g} |")
    keys = list(A.PRIORS)
    np.save(os.path.join(HERE, "ensemble_samples_v14measured.npy"),
            np.array([[ "MHC".index(r[0])] + [r[1][k] for k in keys]
                      + [r[2][k] if r[2] else np.nan for k in A.KEYS + A.EXTRA] + [r[4]]
                      for r in rows], float))
    open(os.path.join(ROOT, "output", "ensemble_v14_measured_RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nsaved ({(time.time()-t0)/60:.0f} min)")


def id_of(p):
    return tuple(round(p[k], 9) for k in sorted(p))


if __name__ == "__main__":
    main()
