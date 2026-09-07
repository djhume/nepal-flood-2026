#!/usr/bin/env python3
"""
ENSEMBLE v10 — rock-only deposition, an ice-capable friction floor, and a
sampled release duration. Dave, 7 Sept evening: "are our limits ok — or do we
need to broaden them — or is there some non-linearity we do not yet
understand?" This is the limits answer (dossier §23).

WHAT v9 LEFT (§22). The runs that carry the drag are solids-rich and deposit
50–64 Mm3 in the model against a 12 Mm3 cap; the runs that pass the cap are
water and have no drag. The engine counts unmelted ice as solid ("melt is
second-order") and the cap comes from DEMs of 28 Aug–1 Sept that could only
see rock. So the cap has been applied to the ice.

THREE LIMITS MOVED, nothing else:
  f_ice    NEW, uniform 0.3–0.9: ice share of the release solids (§04's
           composition lines). Dynamics unchanged — ice IS solid on these
           timescales — it enters only the scorecard: rock-only deposition
           = stranded + re-deposited bulk with the release-origin share
           (ledgers bed_r, dep_r) counted at (1 − f_ice), scored ≤ 12 Mm3
           (the bulk figure is recorded too). In the entrainment
           configuration all deposition is the closure's re-deposition, which
           draws on release solids in proportion to their share of the coarse
           column — that share is what dep_r records.
  mu_dry   floor 0.10 → 0.03: the prior floor sat ABOVE the 0.03–0.09 that
           ice gives (Sosio 2012 on ice; our own terminal-speed bracket
           §04b/§15). A prior that excludes the answer is not a prior.
  T_rel    NEW, log-uniform 60–600 s: the release fed the channel over a
           fixed 180 s in every version. Unknown (no force-time inversion
           published); it acts directly on the border clock that every deep
           run misses by seconds to a minute.
Everything else is v9: v8's geometry (wide Lhende sampled), Voellmy drag
weighted by the water fraction (core.XI_COMP), fitted junction K, the same
eleven observables, the same held-out set.

Run:  .venv/bin/python calcs/ensemble_v10.py [n_samples]
Writes calcs/ensemble_samples_v10.npy and output/ensemble_v10_RESULTS.md.
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
import ensemble_v7 as V7
import ensemble_v8 as V8

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PRIORS = dict(V8.PRIORS)
PRIORS["mu_dry"] = ("lin", 0.03, 0.35)
PRIORS["f_ice"] = ("lin", 0.3, 0.9)
PRIORS["T_rel"] = ("log", 60.0, 600.0)
KEYS = V6.KEYS
EXTRA = ["deposit_bulk_Mm3"]
BASE = None


def draw(n):
    U01 = E.latin_hypercube(n, len(PRIORS)); out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo))) if kind == "log" else lo + u * (hi - lo))
    return out


def _simulate(p, t_end):
    """v9 physics + sampled T_rel. Caller restores state."""
    U.set_widths(V8.widths_for(p["f_wl"], BASE)); core.XI = float(p["xi"]); core.XI_COMP = True
    U.R.K_loc[V7.J22] = float(p["k_junc"])
    U.R.nn = U.R.nn * p["n_scale"]; U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:]); U.R.h_erode = p["h_erode"]; U._settled.clear()
    return U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=t_end, T_rel=p["T_rel"],
                      f_fine_rel=p.get("f_fine", 0.0), entrain=core.entrain_opts("takahashi", f_fine=0.30))


def _restore(nn0, k0):
    core.XI = None; core.XI_COMP = False; U.R.K_loc[V7.J22] = k0; U.set_widths(BASE)
    U.R.nn = nn0; U.R.nf = 0.5 * (nn0[:-1] + nn0[1:]); U.R.h_erode = core.H_ERODE; U._settled.clear()


def observables(r, p):
    m68 = U.x_km <= 68.0
    ero = float((r["ero"][m68] * U.wn[m68] * U.DX).sum() / 1e6)
    dep = float((r["dep"] * U.wn * U.DX).sum() / 1e6)
    bulk = float(r["bed"].sum() / 1e6 / 0.65 + dep)
    dep_rock = float((((r["dep"] - r["dep_r"]) + (1.0 - p["f_ice"]) * r["dep_r"]) * U.wn * U.DX).sum() / 1e6)
    rock = float(((r["bed"] - r["bed_r"]) + (1.0 - p["f_ice"]) * r["bed_r"]).sum() / 1e6 / 0.65 + dep_rock)
    xf = 0.5 * (U.x_km[:-1] + U.x_km[1:]); mg = (xf >= 24.0) & (xf <= 34.0)
    o = {"border_min": r["arrival"](22.0), "syabru_min": r["arrival"](37.6),
         "v_gorge": float(np.median(r["umax"][mg])), "erosion_Mm3": ero,
         "deposit_Mm3": rock, "deposit_bulk_Mm3": bulk,
         "arm_fill_m": float(r["hs_max"].get("Kyirong upstream arm", 0.0))}
    for k, (a, b) in V6.REACHES.items():
        mm = (U.x_km >= a) & (U.x_km < b); o[k] = float(np.median(r["hmax"][mm]))
    return o


def run(p, t_end=None):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V7.J22])
    try:
        return observables(_simulate(p, t_end or V6.T_END), p)
    except Exception as e:
        print(f"    run failed: {e}"); return None
    finally:
        _restore(nn0, k0)


def held_out(p):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V7.J22])
    try:
        r = _simulate(p, 10 * 3600.0)
        q = r["Devghat"]["q"]; tt = r["t"]; i = int(np.argmax(np.where(tt > 30, q, -1)))
        return f"Malekhu {r['arrival'](117.0):.0f} (163) / Kalikhola {r['arrival'](185.0):.0f} (~337) / Devghat {q[i]:,.0f} m³/s at {tt[i]:.0f} min (~2,900)"
    except Exception as e:
        return f"failed: {e}"
    finally:
        _restore(nn0, k0)


def fmt_p(p):
    return (f"{p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.3f} | {p['f_fine']:.2f} | {p['xi']:.0f} | {p['k_junc']:.1f} | "
            f"{p['f_wl']:.2f} | {p['f_ice']:.2f} | {p['T_rel']:.0f}")


def main(N, tag="v10"):
    global BASE
    lines = []; P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, BASE = V6.apply_v6_geometry()
    P_("# Ensemble v10 — rock-only deposition, an ice-capable friction floor, a sampled release duration (dossier §23)\n")
    P_(f"{N} Latin-hypercube samples over {len(PRIORS)} inputs: " + "; ".join(f"{k} {kind} {lo:g}–{hi:g}" for k, (kind, lo, hi) in PRIORS.items())
       + f". v9 physics and geometry; T_END {V6.T_END/3600:.2f} h; deposition scored ROCK-ONLY (bulk recorded).\n")
    P_("| observable | target | tolerance / bounds |"); P_("|---|---|---|")
    for k, (v, t, lab) in V6.OBS.items(): P_(f"| {lab} | {v} | ±{100*t:.0f}% |")
    for k, (lo, hi, med, n) in V6.OBS_BOUNDS.items(): P_(f"| {k} (fit median {med:.1f}) | — | {lo:.1f}–{hi:.1f} m |")
    P_("| rock-only bulk deposition km 0-199, Mm3 | — | ≤ 12.0 |"); P_()
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
    P_("| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | border min | v_gorge | gorge m | syabru m | hakubesi m | galchhi m | dep rock | dep bulk | ero | failed |")
    P_("|" + "---|" * 20)
    for p, o, ok, n in best:
        P_(f"| {fmt_p(p)} | {n} | {o['border_min']:.1f} | {o['v_gorge']:.0f} | {o['stage_gorge']:.0f} | {o['stage_syabru']:.0f} | {o['stage_hakubesi']:.0f} | "
           f"{o['stage_galchhi']:.1f} | {o['deposit_Mm3']:.1f} | {o['deposit_bulk_Mm3']:.1f} | {o['erosion_Mm3']:.1f} | {', '.join(k for k in KEYS if not ok[k])} |")
    if full:
        P_("\n## Posterior (passing runs)\n"); P_("| input | median | range |"); P_("|---|---|---|")
        for key in PRIORS:
            arr = np.array([r[0][key] for r in full]) * (1e-6 if key == "V_rel" else 1)
            P_(f"| {key}{' Mm3' if key == 'V_rel' else ''} | {np.median(arr):.3g} | {arr.min():.3g} – {arr.max():.3g} |")
    P_("\n## Held out (10 h): passing runs, then the three nearest misses\n")
    P_("| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | Malekhu (163) / Kalikhola (~337) / Devghat (~2,900) |"); P_("|" + "---|" * 11)
    for p, o, ok, n in (sorted(full, key=lambda r: r[0]["V_rel"]) + [r for r in best if r[3] < len(KEYS)][:3]):
        P_(f"| {fmt_p(p)} | {n} | {held_out(p)} |")
    np.save(os.path.join(HERE, f"ensemble_samples_{tag}.npy"),
            np.array([[r[0][k] for k in PRIORS] + [r[1][k] for k in KEYS] + [r[1][k] for k in EXTRA] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", f"ensemble_{tag}_RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nsaved calcs/ensemble_samples_{tag}.npy and output/ensemble_{tag}_RESULTS.md ({(time.time()-t0)/60:.0f} min)")


if __name__ == "__main__":
    main(N)
