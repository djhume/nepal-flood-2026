#!/usr/bin/env python3
"""
ENSEMBLE v7 — v6 plus a resistance that survives depth, and a junction loss
that is fitted rather than assumed.

WHY (dossier §20). v6 scored the size envelope against the mud-line map and
passed nothing: the runs deep enough for the mapped stages (86–142 Mm3) reach
the border in 4.2–4.8 min at 45–62 m/s in the gorge, against 7 min 40 s and
~34 observed, and roughness cannot slow them — Manning's n^2 v|v|/h^(4/3)
vanishes at 70 m and the deep runs sit at the Froude cap. The real flow was
that deep and half as fast. A debris flow sixty metres thick carries a
resistance the composition dial does not have.

WHAT CHANGES. Two inputs added to v6's six, everything else identical:
  xi      Voellmy turbulent coefficient, log-uniform 100–2,000 m/s^2, applied
          as a friction slope v|v|/(xi h) alongside Manning and the Coulomb
          dial (core.XI). Rock-ice avalanche back-analyses give 300–2,000
          (Sosio 2012: 1,000–2,000 for flows on ice; Chamoli/Kolka fits lower).
  k_junc  minor-loss coefficient at the border node, uniform 1–10 (was a
          fixed 3): Dave's point that the junction was a turbulence event of
          a different order from the gorge above it.
Observables, widths, pond, clock, held-out set: exactly v6's.

Run:  .venv/bin/python calcs/ensemble_v7.py [n_samples]
Writes calcs/ensemble_samples_v7.npy and output/ensemble_v7_RESULTS.md.
"""
import itertools, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
import core
import unified as U
import ensemble as E
import ensemble_v6 as V6

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
PRIORS = dict(E.PRIORS)
PRIORS["xi"] = ("log", 100.0, 2000.0)
PRIORS["k_junc"] = ("lin", 1.0, 10.0)
KEYS = V6.KEYS
J22 = min(int(np.argmin(np.abs(U.x_km - 22.0))), U.N - 2)


def draw(n):
    U01 = E.latin_hypercube(n, len(PRIORS))
    out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
                     if kind == "log" else lo + u * (hi - lo))
    return out


def run(p):
    core.XI = float(p["xi"])
    k0 = float(U.R.K_loc[J22]); U.R.K_loc[J22] = float(p["k_junc"])
    try:
        return V6.run(p)
    finally:
        core.XI = None; U.R.K_loc[J22] = k0


if __name__ == "__main__":
    lines = []
    P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, new = V6.apply_v6_geometry()
    P_("# Ensemble v7 — v6 plus a Voellmy turbulent term and a fitted junction loss (dossier §20)\n")
    P_(f"{N} Latin-hypercube samples over {len(PRIORS)} inputs (v6's six + xi log-uniform 100–2,000 m/s², "
       f"k_junc uniform 1–10); T_END {V6.T_END/3600:.2f} h; geometry and observables as v6.\n")
    P_("| observable | target | tolerance / bounds |"); P_("|---|---|---|")
    for k, (v, t, lab) in V6.OBS.items(): P_(f"| {lab} | {v} | ±{100*t:.0f}% |")
    for k, (lo, hi, med, n) in V6.OBS_BOUNDS.items(): P_(f"| {k} (fit median {med:.1f}) | — | {lo:.1f}–{hi:.1f} m |")
    for k, (cap, lab) in V6.OBS_MAX.items(): P_(f"| {lab} | — | ≤ {cap} |")
    P_()
    P = draw(N); t0 = time.time(); rows = []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = run(p)
        if o is None: continue
        ok = V6.score(o); rows.append((p, o, ok, sum(ok.values())))
        if (i + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min, "
                  f"{sum(1 for r in rows if r[3] == len(KEYS))} full matches)", flush=True)
    full = [r for r in rows if r[3] == len(KEYS)]
    P_(f"\n## Result: {len(rows)} runs, **{len(full)} satisfy all {len(KEYS)} observables**\n")
    P_("| observable | met by |"); P_("|---|---|")
    for k in KEYS: P_(f"| {k} | {sum(1 for r in rows if r[2][k])} / {len(rows)} |")
    if not full:
        P_("\nNo sample satisfies everything. Pairs:\n"); P_("| pair | runs meeting both |"); P_("|---|---|")
        for a, b in itertools.combinations(KEYS, 2):
            P_(f"| {a} + {b} | {sum(1 for r in rows if r[2][a] and r[2][b])} |")
    best = sorted(rows, key=lambda r: -r[3])[:12]
    P_("\nBest runs (most observables met):\n")
    P_("| V Mm3 | w0 | mu | f_fine | xi | k_junc | met | border min | v_gorge | gorge m | hakubesi m | galchhi m | deposit | failed |")
    P_("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p, o, ok, n in best:
        P_(f"| {p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.2f} | {p['f_fine']:.2f} | {p['xi']:.0f} | {p['k_junc']:.1f} | {n} | "
           f"{o['border_min']:.1f} | {o['v_gorge']:.0f} | {o['stage_gorge']:.0f} | {o['stage_hakubesi']:.0f} | {o['stage_galchhi']:.1f} | {o['deposit_Mm3']:.1f} | "
           f"{', '.join(k for k in KEYS if not ok[k])} |")
    if full:
        P_("\n## Posterior (passing runs)\n"); P_("| input | median | range |"); P_("|---|---|---|")
        for nm, key, sc in (("release volume Mm3", "V_rel", 1e-6), ("liquid fraction w0", "w0", 1), ("mu_dry", "mu_dry", 1),
                            ("f_fine", "f_fine", 1), ("xi m/s2", "xi", 1), ("k_junc", "k_junc", 1), ("n_scale", "n_scale", 1), ("h_erode", "h_erode", 1)):
            arr = np.array([r[0].get(key, 0.0) for r in full]) * sc
            P_(f"| {nm} | {np.median(arr):.2f} | {arr.min():.2f} – {arr.max():.2f} |")
        P_("\n## Held out: Devghat peak and the lower clocks (passing runs re-run to 10 h)\n")
        P_("| V Mm3 | xi | Devghat peak m3/s (obs ~2,900 excess) | Malekhu front min (obs 163) | Kalikhola front min (obs ~337) |"); P_("|---|---|---|---|---|")
        for p, o, ok, n in sorted(full, key=lambda r: r[0]["V_rel"]):
            core.XI = float(p["xi"]); k0 = float(U.R.K_loc[J22]); U.R.K_loc[J22] = float(p["k_junc"])
            nn0 = U.R.nn.copy(); U.R.nn = nn0 * p["n_scale"]; U.R.nf = 0.5*(U.R.nn[:-1]+U.R.nn[1:]); U.R.h_erode = p["h_erode"]; U._settled.clear()
            try:
                r = U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=10*3600.0, f_fine_rel=p.get("f_fine",0.0), entrain=core.entrain_opts("takahashi", f_fine=0.30))
                q = r["Devghat"]["q"]; tt = r["t"]; i = int(np.argmax(np.where(tt > 30, q, -1)))
                P_(f"| {p['V_rel']/1e6:.1f} | {p['xi']:.0f} | {q[i]:,.0f} @ {tt[i]:.0f} min | {r['arrival'](117.0):.0f} | {r['arrival'](185.0):.0f} |")
            except Exception as e:
                P_(f"| {p['V_rel']/1e6:.1f} | {p['xi']:.0f} | failed: {e} | | |")
            finally:
                core.XI = None; U.R.K_loc[J22] = k0
                U.R.nn = nn0; U.R.nf = 0.5*(nn0[:-1]+nn0[1:]); U.R.h_erode = core.H_ERODE; U._settled.clear()
    np.save(os.path.join(HERE, "ensemble_samples_v7.npy"),
            np.array([[r[0][k] for k in PRIORS] + [r[1][k] for k in KEYS] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", "ensemble_v7_RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nsaved calcs/ensemble_samples_v7.npy and output/ensemble_v7_RESULTS.md ({(time.time()-t0)/60:.0f} min)")
