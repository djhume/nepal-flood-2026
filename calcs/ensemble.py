#!/usr/bin/env python3
"""
ENSEMBLE / rejection sampling over the contested inputs — "how big was it,
honestly?"

WHY. Every public number for this event is a point claim from a different
method: Kargel 50-200 Mm3, Azam/ICIMOD 100-200, EGU preliminary 0.5-10,
geopera ~100 Mm3 of debris-laden water, our own entrainment ledger <=6 Mm3 of
solids. They cannot all be right, and arguing about them one at a time has got
nowhere. The honest question is not "which number is correct" but **which
combinations of inputs are simultaneously consistent with everything we can
actually measure** — which is a search over parameter space, not a debate.

This is approximate Bayesian computation in its simplest form: sample the
contested inputs from stated priors, run the model, keep the samples that
reproduce every observable inside its stated tolerance, and report what
survives. Dave asked for it after we found that the "border needs V = 30-60
Mm3" inference was conditional on model structure rather than measured.

WHAT IT CAN AND CANNOT DO. It can map the consistent region and give an
envelope on release volume — exactly what PLAN.md's honesty rails demand
("envelopes over contested inputs, not point claims"). It CANNOT by itself
settle a STRUCTURAL question, e.g. whether the mass behaved as a spreading
fluid (our shallow-water model) or as a coherent sliding block (the energy
line, which has no volume term at all). What it can do there is run the
structure we have and report whether ANY parameter combination satisfies all
observables. If none does, the structure is falsified rather than the
parameters — and that is a result, not a failure.

PRIORS (from research/event-dossier.md §2 and §11; deliberately wide)
    V_rel     log-uniform 1 - 200 Mm3   spans every published estimate
    w0        uniform 0.02 - 0.85       liquid fraction; ice:rock unpublished
                                        (run 1 used 0.02-0.50 and PINNED
                                         against the ceiling -- widened)
    mu_dry    uniform 0.10 - 0.35       Schneider ice-avalanche to Scheidegger rock
    n_scale   uniform 0.70 - 1.40       Manning roughness class-value uncertainty
    h_erode   uniform 1 - 10 m          erodible layer, the entrainment free input

OBSERVABLES (upper corridor only in stage 1 — it is where the hard data is)
    border km 22 arrival      7.68 min     hard (USGS seismic origin
                                           08:37:10 NPT + Gyirong CCTV
                                           overlay 08:44:50 NPT, read
                                           directly 6 Sept; was 7.0 until
                                           the overlay seconds were read)
    Syabrubesi km 37.6        13 min       hard-ish (gauge 3.8 m at 08:50)
    peak speed near km 22     45-52 m/s    geopera superelevation, AND the
                                           134 m junction trimline read as
                                           stagnation run-up gives 51.3 m/s
                                           by an independent route
    erosion km 0-68           3.2 Mm3      geopera stereo DEM, +-60%
    bulk deposition           <= 5 Mm3     geopera: 0.9 measured, ~5 in their
                                           own calibrated model. An INEQUALITY:
                                           a DEM difference bounds deposition
                                           from above, it does not target it.

The passing samples are then re-run to 10 h and scored on the distal observables
(Galchhi 30-min rise ~9 m, Devghat peak timing) — out of sample relative to
the stage-1 screen.

Run:  python calcs/ensemble.py [n_samples]
"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import core
import unified as U

N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
RNG = np.random.default_rng(20260904)

# ---- priors ---------------------------------------------------------------
PRIORS = {
    "V_rel":   ("log",  1e6,  200e6),
    "w0":      ("lin",  0.02, 0.95),   # widened again 5 Sept: run 3's passing runs
                                       # reached 0.84 against a 0.85 ceiling.
                                       # Originally 0.50 and severely pinned
                                       # against its 0.50 ceiling (median
                                       # 0.49, range 0.38-0.50), i.e. the
                                       # prior was truncating the answer, not
                                       # the data constraining it
    "mu_dry":  ("lin",  0.10, 0.35),
    "n_scale": ("lin",  0.70, 1.40),
    "h_erode": ("lin",  1.0,  10.0),
    "f_fine":  ("lin",  0.0,  0.98),   # added 4 Sept with the two-phase split:
                                       # share of RELEASE solids that never
                                       # reach a DEM-visible deposit (wash load
                                       # + ice). Hand-fitted at 0.95 in the
                                       # first two-phase runs; sampling it
                                       # replaces that with a posterior.
}

# ---- observables: (value, tolerance as a fraction, label) -----------------
#
# THE BORDER SPEED IS THE ONE CONTESTED ENTRY, and it is the single most
# consequential input to the size envelope, so it is a named SCENARIO rather
# than a hard-coded constant. Two candidate values are in print for "the speed
# at Gyirong Port", differing by a factor of 2.5:
#
#   front  48.5 m/s  geopera superelevation, our three mud lines (54), our own
#                    frame-by-frame front measurement (46.9, envelope 41-63,
#                    dossier 14d), and the 22-km mean from the corrected clock
#                    (47.8). Four routes, all measuring the DEBRIS FRONT.
#   cas    19.0 m/s  CAS Institute of Mountain Hazards & Environment, the first
#                    peer-reviewed study of the event, frame-by-frame. Our
#                    reading is that this measures the POST-TURN WATER SURFACE,
#                    not the front: 19 m/s requires a run-up coefficient
#                    alpha = 2.72 to produce the observed 45-55 m cliff run-up,
#                    which is unphysical (alpha <= 1 for a stagnating front).
#
# That reconciliation is OURS and it is not peer-reviewed, while the number it
# sets aside IS. So the "cas" scenario exists to answer the question the site
# has been promising and not delivering: if CAS is measuring what we measure,
# where does the size envelope go? Run both, publish both.
#
#     python calcs/ensemble.py 200                    # front, the default
#     TRISHULI_VBORDER=cas python calcs/ensemble.py 200
#
V_BORDER = {"front": (48.5, 0.35), "cas": (19.0, 0.35)}
SCENARIO = os.environ.get("TRISHULI_VBORDER", "front")
if SCENARIO not in V_BORDER:
    sys.exit(f"TRISHULI_VBORDER must be one of {sorted(V_BORDER)}")
_VB, _VB_TOL = V_BORDER[SCENARIO]

OBS = {
    "border_min":  (7.68, 0.30, "border arrival, min"),
    "syabru_min":  (13.0, 0.50, "Syabrubesi arrival, min"),
    "v_border":    (_VB, _VB_TOL, f"peak speed near km 22, m/s [{SCENARIO}]"),
    "erosion_Mm3": (3.2,  0.60, "erosion km 0-68, Mm3"),
}

# Inequality observables — a DEM difference bounds deposition from above; it
# does not measure a target value. Run 1 omitted this entirely, which is why
# its V_rel ~ 31 Mm3 answer sat happily at 15 Mm3 of solids against a corridor
# that can only account for ~5. Adding it is the real test.
OBS_MAX = {
    # RELAXED 5 Sept. The <=5 Mm3 cap came from geopera's 0.9 Mm3 measured
    # plus the ~5 Mm3 in their calibrated model - but their 0.9 is a LOWER
    # BOUND over 45% cloud-free coverage, and the deposit they describe is
    # "12 to 18 metres thick and three kilometres long where the valley opens
    # below Syabrubesi". At our modelled width there (~200 m) that is
    # 7.2-10.8 Mm3 on its own, before anything deposited elsewhere. 12 Mm3 is
    # the honest cap; 5 was too tight and conditioned run 3's posterior on a
    # constraint we now know to be wrong.
    "deposit_Mm3": (12.0, "bulk deposition km 0-199, Mm3 (deposit described "
                          "as 12-18 m thick x 3 km => 7-11 Mm3 at 200 m width)"),
}


def latin_hypercube(n, k):
    """Stratified sampling — 120 samples over 5 dimensions needs the help."""
    u = (RNG.permuted(np.tile(np.arange(n), (k, 1)), axis=1)
         + RNG.random((k, n))) / n
    return u.T


def draw(n):
    U01 = latin_hypercube(n, len(PRIORS))
    out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
                     if kind == "log" else lo + u * (hi - lo))
    return out


def run(p, t_end=2.5 * 3600.0):
    """One model realisation. Returns the observable vector, or None."""
    nn0 = U.R.nn.copy()
    U.R.nn = nn0 * p["n_scale"]
    U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:])
    U.R.h_erode = p["h_erode"]
    U._settled.clear()
    try:
        r = U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"],
                       t_end=t_end, f_fine_rel=p.get("f_fine", 0.0),
                       entrain=core.entrain_opts("takahashi", f_fine=0.30))
        m = U.x_km <= 68.0
        ero = float((r["ero"][m] * U.wn[m] * U.DX).sum() / 1e6)
        j22 = int(np.argmin(np.abs(U.x_km - 22.0)))
        dep = float((r["dep"] * U.wn * U.DX).sum() / 1e6)
        bulk = float(r["bed"].sum() / 1e6 / 0.65 + dep)
        return {
            "deposit_Mm3": bulk,
            "border_min": r["arrival"](22.0),
            "syabru_min": r["arrival"](37.6),
            "v_border":   float(np.max(r["umax"][:j22])),
            "erosion_Mm3": ero,
            "_r": r,
        }
    except Exception as e:
        print(f"    run failed: {e}")
        return None
    finally:
        U.R.nn = nn0
        U.R.nf = 0.5 * (nn0[:-1] + nn0[1:])
        U.R.h_erode = core.H_ERODE
        U._settled.clear()


def score(o):
    """Fraction of observables satisfied, and the per-observable verdicts."""
    ok = {}
    for k, (val, tol, _) in OBS.items():
        v = o[k]
        ok[k] = bool(np.isfinite(v) and abs(v - val) <= tol * val)
    for k, (cap, _) in OBS_MAX.items():
        v = o[k]
        ok[k] = bool(np.isfinite(v) and v <= cap)
    return ok


if __name__ == "__main__":
    print(__doc__.split("Run:")[0])
    print(f"border-speed scenario: {SCENARIO} "
          f"({_VB} m/s +-{100*_VB_TOL:.0f}%)")
    print(f"drawing {N} Latin-hypercube samples over {len(PRIORS)} inputs\n")
    P = draw(N)
    t0 = time.time()
    rows = []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = run(p)
        if o is None:
            continue
        ok = score(o)
        rows.append((p, o, ok, sum(ok.values())))
        if (i + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, "
                  f"{el/60:.1f} min elapsed, "
                  f"{sum(1 for r in rows if r[3] == len(OBS)+len(OBS_MAX))}"
                  f" full matches)")

    NOBS = len(OBS) + len(OBS_MAX)
    full = [r for r in rows if r[3] == NOBS]
    print(f"\n{'='*74}\n{len(rows)} runs, {len(full)} satisfy ALL "
          f"{NOBS} observables\n{'='*74}")
    for k, (val, tol, lab) in OBS.items():
        hits = sum(1 for r in rows if r[2][k])
        print(f"  {lab:44s} {val:7.1f} +-{100*tol:3.0f}%  "
              f"met by {hits:4d}/{len(rows)}")
    for k, (cap, lab) in OBS_MAX.items():
        hits = sum(1 for r in rows if r[2][k])
        print(f"  {lab:44s} <= {cap:6.1f}       "
              f"met by {hits:4d}/{len(rows)}")

    if not full:
        print("\nNO sample satisfies everything simultaneously.")
        print("That is a STRUCTURAL result, not a tuning failure: with this")
        print("model form, no combination of the contested inputs reproduces")
        print("the upper-corridor record. Report which pairs conflict:")
        import itertools
        for a, b in itertools.combinations(list(OBS) + list(OBS_MAX), 2):
            both = sum(1 for r in rows if r[2][a] and r[2][b])
            print(f"    {a:12s} + {b:12s}: {both:4d} runs")
    else:
        V = np.array([r[0]["V_rel"] for r in full]) / 1e6
        w = np.array([r[0]["w0"] for r in full])
        mu = np.array([r[0]["mu_dry"] for r in full])
        ffn = np.array([r[0].get("f_fine", 0.0) for r in full])
        print("\nPOSTERIOR over the contested inputs (samples that fit "
              "everything):")
        for nm, arr, unit in [("release volume", V, "Mm3"),
                              ("liquid fraction w0", w, ""),
                              ("mu_dry", mu, ""),
                              ("f_fine (non-depositing)", ffn, "")]:
            print(f"  {nm:20s} median {np.median(arr):7.2f} {unit}   "
                  f"range {arr.min():.2f} - {arr.max():.2f}")
        print(f"\n  -> against published claims: Kargel 50-200, ICIMOD 100-200,")
        print(f"     EGU preliminary 0.5-10, our entrainment ledger <=6 Mm3 solids")

    stem = ("ensemble_samples.npy" if SCENARIO == "front"
            else f"ensemble_samples_{SCENARIO}.npy")
    np.save(os.path.join(HERE, stem),
            np.array([[r[0][k] for k in PRIORS] +
                      [r[1][k] for k in list(OBS) + list(OBS_MAX)]
                      + [r[3]] for r in rows]))
    print(f"\nsaved {len(rows)} samples -> calcs/{stem}")
