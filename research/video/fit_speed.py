#!/usr/bin/env python3
"""
Fit a flow speed — and test for deceleration — from plume positions picked off
successive video frames.

WHY A FIT RATHER THAN A STOPWATCH. Timing an occlusion gives two events, each
uncertain by +/-1 frame, so a 2 s transit carries +/-50%. Picking the front's
POSITION in several frames is a different measurement: each frame carries its
own exact presentation timestamp, so the only error is placing the front, and
that error gets divided by the whole time span. Precision improves roughly as N^1.5, so
eight frames beat four by about a factor of three.

THE PART WORTH MORE THAN THE SPEED. With five or more points the quadratic term
is resolvable, which tests whether the flow DECELERATES through the junction.
That is the junction-step hypothesis (report section 08) — the thing that would
reconcile geopera's 45-52 m/s with the CAS 19 m/s as measurements of different
places in the same flow. Nobody has measured it. A straight line says no step;
a bend says yes and gives its size.

INPUT. A CSV of frame index and distance along the flow path, in metres, from
any fixed origin. Distances come from landmarks whose spacings you measure on
Google Earth ALONG the direction of travel — that keeps the oblique-camera
scale error largely cancelled, which is why the building-length method was
sound to begin with.

    time_s,distance_m      <- preferred, from frames/times.csv
    0.000,0
    0.417,14
    ...

Usage:  fit_speed.py picks.csv [--fps 1.0] [--sigma 10]
"""
import argparse, csv, sys
import numpy as np

G = 9.81
RUNUP_LO, RUNUP_HI = 45.0, 55.0     # border junction, dossier section 6c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picks")
    ap.add_argument("--fps", type=float, default=1.0,
                    help="UNIQUE frames per second (from probe_and_extract.sh)")
    ap.add_argument("--sigma", type=float, default=10.0,
                    help="how well the front can be placed, metres")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.picks)))
    x = np.array([float(r["distance_m"]) for r in rows])
    # Prefer a real timestamp per frame. mpdecimate keeps a variable number of
    # frames per second, so a survivor's SEQUENCE NUMBER is not a clock — using
    # it would stretch the static part of the record and compress the fast part,
    # biasing the very acceleration we are trying to measure. times.csv carries
    # the true presentation timestamps; frame+fps is the fallback for a source
    # known to be evenly sampled.
    if rows and rows[0].get("time_s"):
        t = np.array([float(r["time_s"]) for r in rows])
        src = "true timestamps"
    else:
        t = np.array([float(r["frame"]) for r in rows]) / a.fps
        src = f"frame index at {a.fps:g} fps (assumes even sampling)"
    if len(t) < 3:
        sys.exit("need at least 3 picks; 5+ to test for deceleration")
    o = np.argsort(t)
    t, x = t[o], x[o]
    t, x = t - t[0], x - x[0]

    print(f"{len(t)} picks over {t[-1]:.2f} s, timing from {src}, "
          f"front placed to +/-{a.sigma:g} m\n")

    # ---- constant speed -----------------------------------------------------
    A = np.vstack([t, np.ones_like(t)]).T
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    v = coef[0]
    cov = a.sigma**2 * np.linalg.inv(A.T @ A)
    sv = np.sqrt(cov[0, 0])
    resid = x - A @ coef
    print("CONSTANT SPEED FIT")
    print(f"  v = {v:.1f} +/- {sv:.1f} m/s   ({100*sv/abs(v):.0f}%)")
    print(f"  rms residual {np.sqrt((resid**2).mean()):.1f} m "
          f"(placement error assumed {a.sigma:g} m)")

    # ---- does it decelerate? ------------------------------------------------
    if len(t) >= 5:
        B = np.vstack([t**2, t, np.ones_like(t)]).T
        c2, *_ = np.linalg.lstsq(B, x, rcond=None)
        cov2 = a.sigma**2 * np.linalg.inv(B.T @ B)
        acc, sacc = 2 * c2[0], 2 * np.sqrt(cov2[0, 0])
        print("\nDECELERATION TEST (the junction-step signature)")
        print(f"  a = {acc:+.1f} +/- {sacc:.1f} m/s^2")
        print(f"  entry speed {c2[1]:.1f} m/s -> exit speed "
              f"{c2[1] + acc*t[-1]:.1f} m/s over {t[-1]:.1f} s")
        n = abs(acc) / sacc if sacc else 0
        verdict = ("no curvature resolved — consistent with steady flow"
                   if n < 2 else
                   f"curvature detected at {n:.1f} sigma — "
                   + ("DECELERATING" if acc < 0 else "accelerating"))
        print(f"  {verdict}")
    else:
        print("\n(5+ picks needed to test for deceleration)")

    # ---- what it means at the junction -------------------------------------
    print("\nTHROUGH THE RUN-UP TRIG  (R = alpha v^2/2g, observed R = 45-55 m)")
    for label, vv in (("fit", v), ("fit low", v - sv), ("fit high", v + sv)):
        al, ah = 2*G*RUNUP_LO/vv**2, 2*G*RUNUP_HI/vv**2
        note = "IMPOSSIBLE (alpha>1)" if al > 1.0 else "physical"
        print(f"  {label:9s} {vv:5.1f} m/s -> alpha {al:.2f}-{ah:.2f}  {note}")

    print("\nAGAINST THE PUBLISHED ESTIMATES")
    for vv, src in ((19.0, "CAS, video at the checkpoint"),
                    (30.0, "our mud-line floor (alpha=1 by construction)"),
                    (37.0, "geopera, upper Lhende superelevation"),
                    (48.5, "geopera, at the border"),
                    (52.0, "front speed implied by the 7-minute clock")):
        z = abs(vv - v) / sv if sv else 0
        mark = "consistent" if z < 2 else f"EXCLUDED at {z:.1f} sigma"
        print(f"  {vv:5.1f}  {mark:22s} {src}")


if __name__ == "__main__":
    main()
