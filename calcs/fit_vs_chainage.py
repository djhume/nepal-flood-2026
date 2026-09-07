#!/usr/bin/env python3
"""
FIT VERSUS CHAINAGE — where along the river does the model actually work?

Dave, 8 Sept: "I'd like a model accuracy/fit vs km downstream type indicator —
it's pretty neat if we can say we have a model that fits the first X km."

We can, but only with one distinction kept in front of the reader, and it is
the whole reason this script exists rather than a chart:

  IN-SAMPLE (km 0-108). The mud-line stages ARE the ensemble's scoring set.
  The model was selected on them. Agreement here says the sampler found a
  corner that satisfies its own constraints; it is NOT a prediction, and a
  reader who is not told that will over-read it.

  OUT-OF-SAMPLE (km 117, 185, 199). Malekhu and Kalikhola arrival times and
  the Devghat peak and volume were never scored. These are the only numbers on
  the chart that test the model rather than describe the fit.

So the honest headline is two numbers, not one: the chainage to which the
model stays inside the reconstructed envelope, and separately how the three
held-out stations came out.

Two further caveats that belong on any chart made from this:
  - the "observations" are a RECONSTRUCTION — trimlines mapped from imagery,
    elevations sampled under them from an 8 m DEM. They are not gauge
    readings. `output/trimline_fit.csv` carries a p10-p90 band per station and
    it is wide in places; sitting inside a wide band is a weak claim, so the
    relative residual is reported alongside the band test.
  - stations with n_points < 3 are single-look reads. Reported, flagged, and
    excluded from the headline horizon.
  - the run must outrun the flood. The first version of this script used the
    ensemble's 3.25 h scoring window and reported km 108-180 as a total
    failure; the front does not reach Kalikhola until ~5.5 h, so the wave had
    simply not arrived. It runs 10 h.

A note on what the ensemble actually scores, which this script exposes: the
six stage observables are REACH MEDIANS. Matching the median of a reach is a
much weaker test than matching its stations, and the two come apart here — a
run can satisfy every scored median while sitting outside the band at half the
stations inside it. That gap is the most useful thing this indicator shows.

Run:  .venv/bin/python calcs/fit_vs_chainage.py          (v12 geometry)
      TRISHULI_FIT_TAG=v10 .venv/bin/python calcs/fit_vs_chainage.py
Writes output/fit_vs_chainage.csv and prints the summary table.
"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)

# The reaches whose stage medians the ensemble actually scores (v6 KEYS).
SCORED_TO_KM = 108.2
HELD_OUT = {117.0: "Malekhu arrival", 185.0: "Kalikhola arrival",
            199.2: "Devghat peak + volume"}
MIN_POINTS = 3          # stations with fewer looks are flagged, not counted


def observed():
    """The reconstructed stage profile: km, fit, p10, p90, n_points."""
    rows = list(csv.DictReader(open(os.path.join(ROOT, "output",
                                                 "trimline_fit.csv"))))
    return (np.array([float(r["km"]) for r in rows]),
            np.array([float(r["stage_fit"]) for r in rows]),
            np.array([float(r["fit_p10"]) for r in rows]),
            np.array([float(r["fit_p90"]) for r in rows]),
            np.array([int(r["n_points"]) for r in rows]))


def profile(r, x_km):
    """Modelled peak stage per DEM station, interpolated from the model grid."""
    km, fit, p10, p90, n = observed()
    mod = np.interp(km, x_km, r["hmax"])
    return km, mod, fit, p10, p90, n


def horizon(km, mod, p10, p90, n, window=2.0, tol=0.5):
    """The chainage to which the model stays inside the reconstructed band.

    Not a single-station test: one station inside a wide band proves nothing
    and one outside a narrow band is noise. Walk downstream in `window`-km
    bins over stations with enough looks, and stop at the first bin where
    fewer than `tol` of the stations sit inside their own p10-p90.
    """
    ok = (mod >= p10) & (mod <= p90) & (n >= MIN_POINTS)
    use = n >= MIN_POINTS
    edges = np.arange(0.0, km.max() + window, window)
    last = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        m = (km >= a) & (km < b) & use
        if m.sum() == 0:
            continue                      # no evidence either way; keep going
        if ok[m].mean() < tol:
            return last, (a, b)
        last = b
    return last, None


def main(tag="v12"):
    import core, unified as U
    import ensemble_v6 as V6, ensemble_v10 as V10
    old, V10.BASE = V6.apply_v6_geometry()

    # The run to profile: v10b's single full pass and v10's wet near-miss, so
    # the chart shows the two corners the model has been stuck between.
    RUNS = {
        "v10b pass (160 Mm3, 4% water)": dict(
            V_rel=160e6, w0=0.04, mu_dry=0.31, f_fine=0.77, xi=188.0,
            k_junc=8.3, f_wl=0.34, f_ice=0.81, T_rel=291.0,
            n_scale=1.0, h_erode=3.0),
        "v10 wet near-miss (123 Mm3, 81% water)": dict(
            V_rel=123e6, w0=0.81, mu_dry=0.13, f_fine=0.5, xi=131.0,
            k_junc=8.7, f_wl=0.46, f_ice=0.82, T_rel=501.0,
            n_scale=1.0, h_erode=3.0),
    }
    use_v12 = tag == "v12"
    if use_v12:
        import ensemble_v12 as V12
        for p in RUNS.values():
            p.update(f_fp=1.0, h_bank=5.0, n_fp=0.09)

    out_rows = []
    print(f"\nFIT VERSUS CHAINAGE — {tag}\n" + "=" * 78)
    for name, p in RUNS.items():
        mod_engine = V12 if use_v12 else V10
        nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V10.V7.J22])
        try:
            # 10 h, NOT the 3.25 h scoring window. The first version of this
            # script used V6.T_END and reported km 108-180 at -100 % residual,
            # which was not a model failure at all: the front does not reach
            # Kalikhola until ~5.5 h, so the wave simply had not arrived yet.
            # Any fit-versus-chainage measure has to outrun the flood.
            r = mod_engine._simulate(p, 10 * 3600.0)
            km, mod, fit, p10, p90, n = profile(r, U.x_km)
        finally:
            mod_engine._restore(nn0, k0)

        h, broke = horizon(km, mod, p10, p90, n)
        good = (mod >= p10) & (mod <= p90) & (n >= MIN_POINTS)
        use = n >= MIN_POINTS
        rel = np.where(fit > 0, (mod - fit) / fit, np.nan)

        print(f"\n{name}")
        print(f"  inside the reconstructed p10-p90 band: "
              f"{good.sum()} of {use.sum()} stations with >= {MIN_POINTS} looks")
        print(f"  FIT HORIZON: contiguous to km {h:.0f}"
              + (f" (breaks in km {broke[0]:.0f}-{broke[1]:.0f})" if broke else ""))
        print("  reach          stations  inside  median residual")
        for a, b in [(0, 22), (22, 36), (36, 46), (46, 70), (70, 90),
                     (90, 108), (108, 140), (140, 180)]:
            m = (km >= a) & (km < b) & use
            if m.sum() == 0:
                continue
            lab = "in-sample" if b <= SCORED_TO_KM else "UNSCORED"
            print(f"  km {a:3d}-{b:3d}  {m.sum():6d}  {100*good[m].mean():5.0f}%  "
                  f"{100*np.nanmedian(rel[m]):+7.0f}%   {lab}")
        for k, what in HELD_OUT.items():
            print(f"  km {k:.0f}: {what} — held out, see the ensemble results file")
        for k, mo, f, lo, hi, nn, g in zip(km, mod, fit, p10, p90, n, good):
            out_rows.append(dict(run=name, km=f"{k:.1f}", model=f"{mo:.2f}",
                                 fit=f"{f:.2f}", p10=f"{lo:.2f}", p90=f"{hi:.2f}",
                                 n_points=nn, inside=int(g),
                                 scored=int(k <= SCORED_TO_KM)))
    p_out = os.path.join(ROOT, "output", "fit_vs_chainage.csv")
    with open(p_out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader(); w.writerows(out_rows)
    print(f"\nwrote {p_out} ({len(out_rows)} rows)")
    print("\nREAD THIS BEFORE QUOTING A HORIZON. Everything to km "
          f"{SCORED_TO_KM:.0f} is IN-SAMPLE: the mud-line stages are the "
          "ensemble's own scoring set, so agreement there describes the fit "
          "and does not test it. The only out-of-sample numbers are the three "
          "held-out stations. And the 'observations' are a reconstruction from "
          "imagery and an 8 m DEM, not gauge readings.")


if __name__ == "__main__":
    # ensemble.py reads sys.argv[1] as a sample count at import time, so take
    # the tag from the environment rather than the command line.
    main(os.environ.get("TRISHULI_FIT_TAG", "v12"))
