#!/usr/bin/env python3
"""
MODEL A — the first 22 km on its own, over the volume range the field now
agrees on (PLAN §11c; dossier §28, §30).

WHY THIS EXISTS. Seven whole-river versions failed, and the 8 September halt
diagnosed why: fourteen parameters against thirteen correlated observables,
six of them reach medians of our own reconstruction, is an ill-posed inverse
problem. PLAN §11 splits the problem at the junction. This is the upper half.

WHAT CHANGED, AND IT IS THE POINT:

  1. SCORE THE UPPER CORRIDOR ONLY — nine observables, all of them above
     Betrawati, none of them from the lower river. Galchhi, the
     Betrawati–Galchhi reach and the video rise curve are NOT scored here.
     They are the other model's problem. This removes the constraint that
     has blocked every version since v9 and lets the avalanche reach be
     tested on its own evidence.

  2. THE VOLUME PRIOR IS THE FIELD'S, NOT OURS. 135–200 Mm³ (Dave, 12 Sept).
     Published and reported estimates now cluster there: geopera ~100 ±40 %,
     Hendrickx 132 initial → 175 at the border, a reported ~198 from a
     geological analysis, and our own in-model 110–175. Our PUBLISHED
     envelope of 14–34 Mm³ is far below all of it and is under revision.
     Sampling the field's range rather than our own is the honest move: it
     asks what the upper corridor can carry, given what everyone else thinks
     fell.

  3. THE ICE PRIOR IS WIDENED DOWNWARD, to 0.10–0.95 from 0.30–0.90.
     Hendrickx's model uses 13 % ice by volume — BELOW our old prior floor.
     A prior that excludes another analyst's published composition cannot
     test it. This is the same correction v10 made to mu_dry for the same
     reason: a prior that excludes the answer is not a prior.

WHAT IS NOT CHANGED. The engine, the geometry, the observables' windows and
their sources. No window moves. Nothing is tuned to pass.

THE OUTPUT IS RANGES. Dave, 12 Sept: "we need ranges as publishing to 2dp is
dumb". The posterior is reported as p10–p90 across the runs that satisfy all
nine, with the median alongside, and a run count. A parameter whose posterior
fills its prior is reported as UNCONSTRAINED rather than quietly summarised —
that is the honest reading of an input the data does not speak to, and this
model has form for pretending otherwise (§06).

RUN LENGTH. The stages, arrivals and gorge speed are stable by 1.25 h, but
EROSION IS STILL ACCUMULATING at 2 h (1.14 → 1.88 → 2.68 Mm³ on a test run),
so the full 3.25 h window is kept. Checked, not assumed.

Run:  .venv/bin/python calcs/ensemble_v13_upper.py [n_samples]
Writes calcs/ensemble_samples_v13upper.npy and
       output/ensemble_v13_upper_RESULTS.md
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
import ensemble_v10 as V10

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300

# The nine upper-corridor observables. Windows and sources are V6's, unchanged.
KEYS = ["border_min", "syabru_min", "v_gorge", "erosion_Mm3",
        "stage_gorge", "stage_syabru", "stage_hakubesi", "stage_to_betra",
        "deposit_Mm3"]
EXTRA = ["deposit_bulk_Mm3", "arm_fill_m", "stage_betra_gal", "stage_galchhi"]

PRIORS = dict(V10.PRIORS)
PRIORS["V_rel"] = ("lin", 135e6, 200e6)     # the field's range, not ours
PRIORS["f_ice"] = ("lin", 0.10, 0.95)       # widened down to include 13 %


def draw(n):
    U01 = E.latin_hypercube(n, len(PRIORS)); out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
                     if kind == "log" else lo + u * (hi - lo))
    return out


def score(o):
    """Only the nine. V6.score() would also impose the lower river."""
    ok = {}
    for k, (val, tol, _) in V6.OBS.items():
        ok[k] = bool(np.isfinite(o[k]) and abs(o[k] - val) <= tol * val)
    for k, (lo, hi, _, _) in V6.OBS_BOUNDS.items():
        if k in KEYS:
            ok[k] = bool(np.isfinite(o[k]) and lo <= o[k] <= hi)
    ok["deposit_Mm3"] = bool(np.isfinite(o["deposit_Mm3"])
                             and o["deposit_Mm3"] <= 12.0)
    return {k: ok[k] for k in KEYS}


def band(arr, name):
    """p10-p90 and median, or UNCONSTRAINED if the posterior fills the prior."""
    kind, lo, hi = PRIORS[name]
    p10, p50, p90 = np.percentile(arr, [10, 50, 90])
    span = (p90 - p10) / (hi - lo)
    return p10, p50, p90, span


def main(N, tag="v13upper"):
    lines = []; P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, V10.BASE = V6.apply_v6_geometry()
    P_("# Model A — the first 22 km, scored on the upper corridor alone\n")
    P_(f"{N} Latin-hypercube samples over {len(PRIORS)} inputs. **The volume "
       "prior is the field's 135–200 Mm³, not ours**, and the ice prior is "
       "widened down to 0.10 so that another analyst's 13 % composition is "
       "inside it. Nine observables, all above Betrawati; the lower river is "
       "not scored here (PLAN §11).\n")
    P_("| observable | target | window |"); P_("|---|---|---|")
    for k, (v, t, lab) in V6.OBS.items(): P_(f"| {lab} | {v} | ±{100*t:.0f}% |")
    for k, (lo, hi, med, n) in V6.OBS_BOUNDS.items():
        if k in KEYS: P_(f"| {k} (fit median {med:.1f}) | — | {lo:.1f}–{hi:.1f} m |")
    P_("| rock-only deposition km 0–199, Mm³ | — | ≤ 12.0 |"); P_()

    P = draw(N); t0 = time.time(); rows = []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = V10.run(p)
        if o is None: continue
        ok = score(o); rows.append((p, o, ok, sum(ok.values())))
        if (i + 1) % 25 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min, "
                  f"{sum(1 for r in rows if r[3] == 9)} full)", flush=True)
    full = [r for r in rows if r[3] == 9]
    P_(f"\n## Result: {len(rows)} runs, **{len(full)} satisfy all 9**\n")
    P_("| observable | met by |"); P_("|---|---|")
    for k in KEYS: P_(f"| {k} | {sum(1 for r in rows if r[2][k])} / {len(rows)} |")

    if full:
        P_("\n## POSTERIOR — ranges, not point estimates\n")
        P_("| input | p10 | median | p90 | prior | reading |")
        P_("|---|---|---|---|---|---|")
        for key in PRIORS:
            arr = np.array([r[0][key] for r in full])
            sc = 1e-6 if key == "V_rel" else 1.0
            p10, p50, p90, span = band(arr, key)
            kind, lo, hi = PRIORS[key]
            read = ("**UNCONSTRAINED** — posterior fills the prior"
                    if span > 0.70 else
                    "weakly constrained" if span > 0.50 else "constrained")
            P_(f"| {key} | {p10*sc:.3g} | **{p50*sc:.3g}** | {p90*sc:.3g} | "
               f"{lo*sc:.3g}–{hi*sc:.3g} | {read} |")
        P_("\n## What the passing runs do downstream (NOT scored here)\n")
        P_("| | p10 | median | p90 |"); P_("|---|---|---|---|")
        for k in ["stage_betra_gal", "stage_galchhi"]:
            arr = np.array([r[1][k] for r in full])
            P_(f"| {k} | {np.percentile(arr,10):.1f} | {np.median(arr):.1f} | "
               f"{np.percentile(arr,90):.1f} |")
        P_("\n(Galchhi's window is 3.5–9.9 m. These runs were not asked to "
           "meet it. How badly they miss is the measure of how much the two "
           "halves of the river disagree — PLAN §11's whole question.)")
    else:
        P_("\nNothing satisfies all nine. Pairs:\n")
        P_("| pair | both |"); P_("|---|---|")
        for a, b in itertools.combinations(KEYS, 2):
            P_(f"| {a} + {b} | {sum(1 for r in rows if r[2][a] and r[2][b])} |")

    best = sorted(rows, key=lambda r: -r[3])[:12]
    P_("\n## Best runs\n")
    P_("| V Mm³ | w0 | f_ice | mu | xi | f_wl | T_rel | met | border | v_gorge |"
       " gorge | syabru | hakubesi | to_betra | ero | dep rock | failed |")
    P_("|" + "---|" * 16)
    for p, o, ok, n in best:
        P_(f"| {p['V_rel']/1e6:.0f} | {p['w0']:.2f} | {p['f_ice']:.2f} | "
           f"{p['mu_dry']:.3f} | {p['xi']:.0f} | {p['f_wl']:.2f} | "
           f"{p['T_rel']:.0f} | {n} | {o['border_min']:.1f} | {o['v_gorge']:.0f} | "
           f"{o['stage_gorge']:.0f} | {o['stage_syabru']:.0f} | "
           f"{o['stage_hakubesi']:.0f} | {o['stage_to_betra']:.0f} | "
           f"{o['erosion_Mm3']:.1f} | {o['deposit_Mm3']:.1f} | "
           f"{', '.join(k for k in KEYS if not ok[k]) or '—'} |")
    np.save(os.path.join(HERE, f"ensemble_samples_{tag}.npy"),
            np.array([[r[0][k] for k in PRIORS] + [r[1][k] for k in KEYS]
                      + [r[1][k] for k in EXTRA] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", f"ensemble_{tag}_RESULTS.md"),
         "w").write("\n".join(lines) + "\n")
    print(f"\nsaved ({(time.time()-t0)/60:.0f} min)")


if __name__ == "__main__":
    main(N)
