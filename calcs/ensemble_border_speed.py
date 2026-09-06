#!/usr/bin/env python3
"""
Re-score the size envelope against the CAS border speed — carefully, because
the two numbers are not obviously the same quantity.

THE QUESTION. calcs/ensemble.py scores an observable `v_border` at
48.5 +/- 35% m/s, taken from geopera's trimline superelevation. The first
peer-reviewed study of the event (Chinese Academy of Sciences, frame-by-frame
video analysis at the Gyirong Port checkpoint, published 1 Sept) measures
19 m/s. That is outside the tolerance, so the envelope in finding 04 is
conditioned on an observable a reviewed paper contradicts. This script asks
what happens if the CAS number is used instead.

WHY IT IS NOT A ONE-LINE EDIT. The model quantity being scored is

    v_border = max(umax[0 : km22])

i.e. the peak depth-averaged velocity attained ANYWHERE in the first 22 km, at
ANY time — a reach maximum over the whole descent. The CAS number is a point
surface velocity at the junction at the moment of passage. Report section 08
already argues these are three different things (descent speed, splash-line
speed, post-turn speed), so substituting one for the other is a category error
dressed up as a sensitivity test. Re-scoring the cached run confirms it is:
0 of 220 survive, and of the 76 samples that meet the 7-minute clock, ZERO
have a reach maximum below 25.7 m/s. That is arithmetic, not evidence — 22 km
in 7 minutes is a 52 m/s mean front speed, and a flow that never exceeds
25.7 m/s anywhere cannot deliver a front there on time. So the naive swap does
not test the volume envelope; it restates the border-clock dispute.

WHAT THIS SCRIPT DOES INSTEAD. It re-runs the same 220 samples (the RNG is
seeded, so draw(220) reproduces them exactly) and records the LOCAL velocity
at km 22 alongside the reach maximum, so the CAS number can be scored against
a commensurable model quantity. Nothing in calcs/ensemble.py is modified and
the published ensemble_samples.npy is not overwritten.

One caveat on commensurability that survives even this. The model velocity is
depth-averaged (Q / wh); CAS measured a SURFACE velocity from video. Surface
runs above depth-averaged, typically by ~10-20% in turbulent open channel flow,
so scoring depth-averaged against a surface measurement is mildly conservative
— it makes the model look faster relative to CAS than a like-for-like
comparison would.

Run:  python calcs/ensemble_border_speed.py [n_samples]     (~20 s per sample)
Out:  calcs/ensemble_border_speed.npy
"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ensemble as E

N = int(sys.argv[1]) if len(sys.argv) > 1 else 220

# columns of the saved array, in order
COLS = (list(E.PRIORS)                       # 6 sampled inputs
        + ["border_min", "syabru_min", "v_border_reachmax", "erosion_Mm3",
           "deposit_Mm3",                    # the published observables
           "v_at_km22_max", "v_at_km30_max"])  # NEW: local speeds


def main():
    print(__doc__.split("Run:")[0])
    P = E.draw(N)
    t0, rows = time.time(), []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = E.run(p)
        if o is None:
            continue
        r = o["_r"]
        loc22 = float(np.max(r["v@22.0"])) if len(r["v@22.0"]) else np.nan
        loc30 = float(np.max(r["v@30.0"])) if len(r["v@30.0"]) else np.nan
        rows.append([p[k] for k in E.PRIORS]
                    + [o["border_min"], o["syabru_min"], o["v_border"],
                       o["erosion_Mm3"], o["deposit_Mm3"], loc22, loc30])
        if (i + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min "
                  f"elapsed, {(N-i-1)*el/(i+1)/60:.0f} min left)", flush=True)

    A = np.array(rows, dtype=float)
    np.save(os.path.join(HERE, "ensemble_border_speed.npy"), A)
    print(f"\nsaved {A.shape[0]} samples x {A.shape[1]} cols -> "
          f"calcs/ensemble_border_speed.npy")
    print("columns: " + ", ".join(COLS))


if __name__ == "__main__":
    main()
