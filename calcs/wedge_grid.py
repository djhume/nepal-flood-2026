#!/usr/bin/env python3
"""
IS IT A BIGGER EVENT, OR A WETTER ONE? A 2-D probe with the wedge installed.

calcs/wedge_effect.py swept release volume with the backwater wedge in place
and the Galchhi rise appeared to climb steeply with V — 4.5 m at 45 Mm3, 10.6
at 60 — which reads as "the wedge means we were undersizing the event".

That sweep changes TWO things at once. Its own note says so: w0 is raised from
0.15 to 0.40 at V >= 60 "to stay in the wet-scenario family the timing evidence
favours". Refining the interval at FIXED w0 = 0.15 (calcs/wedge_crossing.py)
gives 4.5, 5.1, 5.8 m at 45, 50, 55 Mm3 — a slope of about 0.13 m per Mm3, on
which reaching 9 m would take ~80 Mm3, well past what the corrected border
clock allows. So most of that apparent volume sensitivity was the wetness step,
not the volume.

This script separates them: a grid over V_rel and w0, everything else fixed,
with the wedge installed. Three questions, one table.

  1. Which cells reproduce the Galchhi 30-minute rise (~9 m)?
  2. Which of those still arrive at the border inside the CORRECTED clock
     window, 7.68 min +-30% => 5.38-9.98 min?
  3. Is the surviving region reached by making the event BIGGER or WETTER?

WHY IT MATTERS. Finding 04's published envelope (14-34 Mm3) was produced by a
rejection-sampling ensemble that samples w0 properly but models the Kyirong arm
as a LINEAR store. If the wedge is right, that envelope is conditional on a
store geometry three independent lines of evidence contradict. This probe does
not replace the ensemble — it says which direction the ensemble would move, and
whether the move is in size or in composition.

Run: python calcs/wedge_grid.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import core
import unified as U
from wedge_effect import WEDGE, LINEAR, run

BORDER_OBS, BORDER_TOL = 7.68, 0.30
LO, HI = BORDER_OBS * (1 - BORDER_TOL), BORDER_OBS * (1 + BORDER_TOL)
GALCHHI_OBS = 9.0

VS = (30e6, 45e6, 60e6, 80e6)
W0S = (0.15, 0.40, 0.65)

if __name__ == "__main__":
    print(__doc__.split("Run:")[0])
    print(f"border clock window {LO:.2f}-{HI:.2f} min; Galchhi target "
          f"{GALCHHI_OBS} m; wedge installed\n")
    print(f"  {'V (Mm3)':>8}{'w0':>7}{'border':>9}{'Galchhi':>10}"
          f"{'Devghat':>10}   verdict")
    hits = []
    for V in VS:
        for w0 in W0S:
            r = run(WEDGE, V, w0=w0)
            clock_ok = LO <= r["border"] <= HI
            galchhi_ok = r["galchhi"] >= GALCHHI_OBS
            v = ("BOTH" if clock_ok and galchhi_ok else
                 "clock only" if clock_ok else
                 "Galchhi only" if galchhi_ok else "-")
            if clock_ok and galchhi_ok:
                hits.append((V / 1e6, w0))
            print(f"  {V/1e6:8.0f}{w0:7.2f}{r['border']:8.2f}m"
                  f"{r['galchhi']:9.1f}m{r['devghat']:10,.0f}   {v}")
    print()
    if hits:
        vv = sorted(set(v for v, _ in hits))
        ww = sorted(set(w for _, w in hits))
        print(f"  cells satisfying BOTH: {hits}")
        print(f"  release volumes involved: {vv} Mm3")
        print(f"  wetness values involved : {ww}")
        print(f"\n  Against the published 14-34 Mm3 envelope, the smallest V")
        print(f"  that works here is {min(vv):.0f} Mm3.")
    else:
        print("  NO cell on this grid satisfies both the corrected border")
        print("  clock and the Galchhi rise. With the wedge installed, this")
        print("  scenario family cannot reproduce both ends of the corridor —")
        print("  which is a structural result about the model, not a size.")
    print("\n  Everything else is held fixed (mu_dry, n_scale, h_erode,")
    print("  f_fine). This is a probe, not a posterior.")
