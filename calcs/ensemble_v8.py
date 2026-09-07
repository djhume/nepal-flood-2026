#!/usr/bin/env python3
"""
ENSEMBLE v8 — v7 plus the Lhende's mapped width.

WHY. The v7 sanity run (dossier §21) showed the border clock is set above the
junction, not in it: a 100 Mm3 release runs the first 22 km as a slug ~200 m
thick because the model's Lhende is 50 m wide, and at that depth both the
Froude cap and the Voellmy terminal speed (both ∝ √h) allow 60–80 m/s. The
trimline map (§19) has the Lhende at km 12–22.8: stage 120–165 m, section
area 16,000–42,000 m², equivalent width A/stage = 115–300 m — the same
too-narrow error v6 fixed below the junction, now above it.

CAVEAT that makes this a SAMPLED input rather than a fix: those are avalanche
trimlines (run-up and splash of a rock-ice avalanche), not a flood stage, so
A/stage at the trimline overstates the width at the flow's real depth in a
V-shaped section. Ninth input f_wl, log-uniform 0.3–1.0 × (A/stage), applied
km 12–22.8, ramped from the model's 50 m over km 6–12. Everything else is v7.

Run:  .venv/bin/python calcs/ensemble_v8.py [n_samples]
Writes calcs/ensemble_samples_v8.npy and output/ensemble_v8_RESULTS.md.
"""
import csv, itertools, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
import core
import unified as U
import ensemble as E
import ensemble_v6 as V6
import ensemble_v7 as V7

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
PRIORS = dict(V7.PRIORS); PRIORS["f_wl"] = ("log", 0.3, 1.0)
KEYS = V6.KEYS
BASE = None          # v6 widths, set in main after apply_v6_geometry


def lhende_weq():
    """Equivalent width A/stage on the main arm, km 12–22.8.

    Thin evidence, stated: the mapper computed a section area at only 9 of
    the 276 Lhende stations (all s2chg, 10 m), km 12.2–20.0, A/stage 95–189 m; 2 are outlier-flagged
    and dropped. v6's filter keeps 4 of them (two-bank, unflagged); the other 5 are
    one-bank reads at side-valley mouths whose A/stage (95–174) sits inside
    the same range, so they are kept here — the reach has nothing else.
    Junction / manual / cloud / outlier stations are still dropped. Beyond
    km 20 the last value (96 m) is held to 22.8, where v6's widths take over
    (120 m in the gorge)."""
    best = {}; rows = list(csv.DictReader(open(os.path.join(ROOT, "output", "trimlines.csv"))))
    # a km flagged outlier on ANY layer is out (the plain s2 layer carries no outlier field)
    bad_km = {float(r["km"]) for r in rows if r["arm"] == "main"
              and (r["outlier_L"].strip() == "1" or r["outlier_R"].strip() == "1")}
    for r in rows:
        if r["arm"] != "main" or r["layer"] not in ("pelican0901", "s2chg", "s2"): continue
        try: km, st, A = float(r["km"]), float(r["stage"]), float(r["A"])
        except ValueError: continue
        if not (12.0 <= km <= 22.8) or st <= 0 or A <= 0: continue
        fl = (r["flags_L"] + " " + r["flags_R"]).lower()
        if any(t in fl for t in ("junction", "manual", "cloud")): continue
        # outlier_* hold "0"/"1" (blank on the plain s2 layer): v6's
        # truthy-string test dropped every "0" row, so v6's widths below the
        # junction came from the s2 layer alone — noted in dossier §21.
        if km in bad_km: continue
        pref = {"pelican0901": 0, "s2chg": 1}.get(r["layer"], 2)
        if km not in best or pref < best[km][0]: best[km] = (pref, A / st)
    kms = np.array(sorted(best)); return kms, np.array([best[k][1] for k in kms])


def draw(n):
    U01 = E.latin_hypercube(n, len(PRIORS)); out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo))) if kind == "log" else lo + u * (hi - lo))
    return out


def widths_for(f_wl, base):
    kms, weq = lhende_weq()
    w = base.copy(); x = U.x_km
    m = (x >= 12.0) & (x <= 22.8)
    w[m] = np.clip(f_wl * np.interp(x[m], kms, weq), 30.0, 800.0)
    w12 = w[np.argmin(np.abs(x - 12.0))]
    r = (x >= 6.0) & (x < 12.0)
    w[r] = np.interp(x[r], [6.0, 12.0], [base[np.argmin(np.abs(x - 6.0))], w12])
    return w


def run(p, base=None):
    base = BASE if base is None else base
    U.set_widths(widths_for(p["f_wl"], base)); U._settled.clear()
    try:
        return V7.run(p)
    finally:
        U.set_widths(base); U._settled.clear()


if __name__ == "__main__":
    lines = []
    P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, BASE = V6.apply_v6_geometry()
    kms, weq = lhende_weq()
    P_("# Ensemble v8 — v7 plus the Lhende's mapped width as a sampled input (dossier §21)\n")
    P_(f"{N} Latin-hypercube samples over {len(PRIORS)} inputs (v7's eight + f_wl log-uniform 0.3–1.0 × A/stage on km 12–22.8, "
       f"{len(kms)} mapped stations, A/stage median {np.median(weq):.0f} m, range {weq.min():.0f}–{weq.max():.0f}; model was 50 m); "
       f"ramp km 6–12; T_END {V6.T_END/3600:.2f} h; observables as v6.\n")
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
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min, {sum(1 for r in rows if r[3] == len(KEYS))} full matches)", flush=True)
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
    P_("| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | met | border min | v_gorge | gorge m | hakubesi m | galchhi m | deposit | failed |")
    P_("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p, o, ok, n in best:
        P_(f"| {p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.2f} | {p['f_fine']:.2f} | {p['xi']:.0f} | {p['k_junc']:.1f} | {p['f_wl']:.2f} | {n} | "
           f"{o['border_min']:.1f} | {o['v_gorge']:.0f} | {o['stage_gorge']:.0f} | {o['stage_hakubesi']:.0f} | {o['stage_galchhi']:.1f} | {o['deposit_Mm3']:.1f} | "
           f"{', '.join(k for k in KEYS if not ok[k])} |")
    if full:
        P_("\n## Posterior (passing runs)\n"); P_("| input | median | range |"); P_("|---|---|---|")
        for nm, key, sc in (("release volume Mm3", "V_rel", 1e-6), ("liquid fraction w0", "w0", 1), ("mu_dry", "mu_dry", 1), ("f_fine", "f_fine", 1),
                            ("xi m/s2", "xi", 1), ("k_junc", "k_junc", 1), ("f_wl", "f_wl", 1), ("n_scale", "n_scale", 1), ("h_erode", "h_erode", 1)):
            arr = np.array([r[0].get(key, 0.0) for r in full]) * sc
            P_(f"| {nm} | {np.median(arr):.2f} | {arr.min():.2f} – {arr.max():.2f} |")
        P_("\n## Held out: Devghat peak and the lower clocks (passing runs re-run to 10 h)\n")
        P_("| V Mm3 | xi | f_wl | Devghat peak m3/s (obs ~2,900 excess) | Malekhu front min (obs 163) | Kalikhola front min (obs ~337) |"); P_("|---|---|---|---|---|---|")
        for p, o, ok, n in sorted(full, key=lambda r: r[0]["V_rel"]):
            U.set_widths(widths_for(p["f_wl"], BASE)); core.XI = float(p["xi"]); k0 = float(U.R.K_loc[V7.J22]); U.R.K_loc[V7.J22] = float(p["k_junc"])
            nn0 = U.R.nn.copy(); U.R.nn = nn0 * p["n_scale"]; U.R.nf = 0.5*(U.R.nn[:-1]+U.R.nn[1:]); U.R.h_erode = p["h_erode"]; U._settled.clear()
            try:
                r = U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=10*3600.0, f_fine_rel=p.get("f_fine",0.0), entrain=core.entrain_opts("takahashi", f_fine=0.30))
                q = r["Devghat"]["q"]; tt = r["t"]; i = int(np.argmax(np.where(tt > 30, q, -1)))
                P_(f"| {p['V_rel']/1e6:.1f} | {p['xi']:.0f} | {p['f_wl']:.2f} | {q[i]:,.0f} @ {tt[i]:.0f} min | {r['arrival'](117.0):.0f} | {r['arrival'](185.0):.0f} |")
            except Exception as e:
                P_(f"| {p['V_rel']/1e6:.1f} | {p['xi']:.0f} | {p['f_wl']:.2f} | failed: {e} | | |")
            finally:
                core.XI = None; U.R.K_loc[V7.J22] = k0; U.set_widths(BASE)
                U.R.nn = nn0; U.R.nf = 0.5*(nn0[:-1]+nn0[1:]); U.R.h_erode = core.H_ERODE; U._settled.clear()
    np.save(os.path.join(HERE, "ensemble_samples_v8.npy"),
            np.array([[r[0][k] for k in PRIORS] + [r[1][k] for k in KEYS] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", "ensemble_v8_RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nsaved calcs/ensemble_samples_v8.npy and output/ensemble_v8_RESULTS.md ({(time.time()-t0)/60:.0f} min)")
