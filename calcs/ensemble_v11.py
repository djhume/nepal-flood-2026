#!/usr/bin/env python3
"""
ENSEMBLE v11 — the lower river as a compound section: DEM main channel plus
terrace storage above the bank (dossier §24).

WHAT v10 LEFT. Above Betrawati everything matched at 110–175 Mm3; below it
the wet runs put 14–19 m at Galchhi against ≤ 9.9 and reached Malekhu
30–80 min early — too much discharge, too little attenuation. The DEM
sections (calcs/lowerriver_widths.py) say the conveying channel below
Betrawati is NARROWER than the model's (W_eq 116–142 m at the fitted stage
vs 267), and that the sections widen by 90–120 m between the 10 m and 20 m
levels through Betrawati–Galchhi and by up to 340 m in the Galchhi window:
terraces that a 15–20 m wave floods and a 9 m one does not. Roughness
cannot substitute (v10: Galchhi rises with n_scale).

WHAT CHANGES (below km 70 only; everything above is v10):
  main channel  W_eq = A/stage_fit from the DEM sections, ±1 km running median
                (replaces v6's 267 m held flat and the 120 m rule)
  terrace store FP_W = f_fp × (W_top_20 − W_top_10), running median, engaged
                above FP_HB = 10 m (core.FP_W / FP_HB; storage only — the
                terraces convey nothing, which under-states conveyance and
                over-states attenuation; f_fp uniform 0.3–1.0 carries that)
Regression: FP_W None ⇒ bit-identical. Twelve inputs; observables, held-out
set and everything else as v10.

Run:  .venv/bin/python calcs/ensemble_v11.py [n_samples]
"""
import csv, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
import core
import unified as U
import ensemble_v6 as V6
import ensemble_v8 as V8
import ensemble_v10 as V10

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PRIORS = dict(V10.PRIORS); PRIORS["f_fp"] = ("lin", 0.3, 1.0)
KM_FP = 70.0; HB = 10.0


def dem_widths(fp_from=("W_top_20", "W_top_10")):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "output", "lowerriver_widths.csv"))))
    km = np.array([float(r["km"]) for r in rows]); weq = np.array([float(r["W_eq"]) for r in rows])
    fp = np.array([float(r[fp_from[0]]) - float(r[fp_from[1]]) for r in rows])
    def rm(v): return np.array([np.median(v[(km >= k - 1) & (km <= k + 1)]) for k in km])
    return km, rm(weq), rm(np.maximum(fp, 0.0))


def geometry(p, base, hb=None, fp_from=("W_top_20", "W_top_10")):
    """Widths for one run: v6 base + v8's Lhende patch + the DEM main channel
    below KM_FP; terrace-storage width per node from the DEM section."""
    km, weq, fp = dem_widths(fp_from); x = U.x_km
    w = V8.widths_for(p["f_wl"], base); m = x >= KM_FP
    w[m] = np.clip(np.interp(x[m], km, weq), 20.0, 800.0)
    fpw = np.zeros_like(x); fpw[m] = p["f_fp"] * np.clip(np.interp(x[m], km, fp), 0.0, 3000.0)
    return w, fpw


def _simulate(p, t_end, hb=None, fp_from=("W_top_20", "W_top_10")):
    """v10's settings with the v11 widths applied AFTER the Lhende patch
    (v10._simulate resets widths itself, so it cannot be reused here)."""
    w, fpw = geometry(p, V10.BASE, fp_from=fp_from)
    U.set_widths(w); core.FP_W = fpw; core.FP_HB = HB if hb is None else hb
    core.XI = float(p["xi"]); core.XI_COMP = True
    U.R.K_loc[V10.V7.J22] = float(p["k_junc"])
    U.R.nn = U.R.nn * p["n_scale"]; U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:]); U.R.h_erode = p["h_erode"]; U._settled.clear()
    return U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"], t_end=t_end, T_rel=p["T_rel"],
                      f_fine_rel=p.get("f_fine", 0.0), entrain=core.entrain_opts("takahashi", f_fine=0.30))


def _restore(nn0, k0):
    core.FP_W = None; core.FP_HB = None
    V10._restore(nn0, k0); U.set_widths(V10.BASE); U._settled.clear()


def run(p, t_end=None, **kw):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V10.V7.J22])
    try:
        return V10.observables(_simulate(p, t_end or V6.T_END, **kw), p)
    except Exception as e:
        print(f"    run failed: {e}"); return None
    finally:
        _restore(nn0, k0)


def held_out(p, **kw):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V10.V7.J22])
    try:
        r = _simulate(p, 10 * 3600.0, **kw)
        q = r["Devghat"]["q"]; tt = r["t"]; i = int(np.argmax(np.where(tt > 30, q, -1)))
        return f"Malekhu {r['arrival'](117.0):.0f} (163) / Kalikhola {r['arrival'](185.0):.0f} (~337) / Devghat {q[i]:,.0f} m³/s at {tt[i]:.0f} min (~2,900)"
    except Exception as e:
        return f"failed: {e}"
    finally:
        _restore(nn0, k0)


if __name__ == "__main__":
    # reuse v10's reporting with this module's priors/run/held_out
    V10.PRIORS = PRIORS; V10.run = run; V10.held_out = held_out
    V10.fmt_p = lambda p: (f"{p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.3f} | {p['f_fine']:.2f} | {p['xi']:.0f} | {p['k_junc']:.1f} | "
                           f"{p['f_wl']:.2f} | {p['f_ice']:.2f} | {p['T_rel']:.0f} | fp {p['f_fp']:.2f}")
    V10.main(N, tag="v11")
