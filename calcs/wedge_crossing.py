#!/usr/bin/env python3
"""
WHERE DO THE CONSTRAINTS CROSS, with the up-valley wedge installed?

calcs/wedge_effect.py showed that replacing the Kyirong upstream arm's linear
store with a backwater WEDGE (V = w h^2 / 2S, 19.5 Mm3 at full head against
12.0) moves the distal observables toward the record without touching the
release: at V_rel = 30 Mm3 the Galchhi 30-minute rise goes 1.6 -> 2.9 m.

It also showed the two ends of the corridor pulling apart as V grows. Bigger
releases reach Galchhi properly and arrive at the border TOO EARLY:

    V (Mm3)    border arrival    Galchhi rise    Devghat peak
       30          6.8 min          2.9 m           1,706
       45          6.0              4.5             1,782
       60          5.2             10.6             2,186
       90          4.7             16.9             2,817

    observed:   7.68 min (+-30% => 5.4-9.98)    ~9 m       ~2,900 excess

This script refines the 45-60 Mm3 interval to find where the border clock's
LOWER bound and the Galchhi target actually meet. That matters because the
clock moved on 6 September: the target was 7.0 min (window 4.9-9.1) until the
CCTV overlay's seconds were read, and it is 7.68 min (window 5.4-9.98) now.
The correction tightened the fast end by half a minute, which is precisely the
end a large release is pushing against.

Run: python calcs/wedge_crossing.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import core
import unified as U
from wedge_effect import WEDGE, set_branch, run

BORDER_OBS, BORDER_TOL = 7.68, 0.30
GALCHHI_OBS = 9.0
DEVGHAT_OBS = 2900.0

if __name__ == "__main__":
    print(__doc__.split("Run:")[0])
    lo = BORDER_OBS * (1 - BORDER_TOL)
    print(f"border clock window: {lo:.2f} - {BORDER_OBS*(1+BORDER_TOL):.2f} min "
          f"(obs {BORDER_OBS})\n")
    print(f"  {'V (Mm3)':>8}{'border':>9}{'clock':>7}"
          f"{'Galchhi':>10}{'Devghat':>10}")
    rows = []
    for V in (45e6, 50e6, 55e6, 60e6):
        r = run(WEDGE, V, w0=0.40 if V >= 60e6 else 0.15)
        ok = "ok" if r["border"] >= lo else "TOO EARLY"
        rows.append((V / 1e6, r["border"], r["galchhi"], r["devghat"]))
        print(f"  {V/1e6:8.0f}{r['border']:8.2f}m{ok:>9}"
              f"{r['galchhi']:9.1f}m{r['devghat']:10,.0f}")

    V = np.array([r[0] for r in rows])
    b = np.array([r[1] for r in rows])
    g = np.array([r[2] for r in rows])
    # both are monotone in V over this interval; interpolate on decreasing b
    v_clock = float(np.interp(lo, b[::-1], V[::-1]))
    v_galchhi = float(np.interp(GALCHHI_OBS, g, V))
    print(f"\n  largest V the corrected border clock allows : {v_clock:5.1f} Mm3")
    print(f"  smallest V that reaches the Galchhi 9 m rise: {v_galchhi:5.1f} Mm3")
    if v_galchhi <= v_clock:
        print(f"\n  They CROSS. A wedge-equipped corridor satisfies both at")
        print(f"  V ~ {v_galchhi:.0f}-{v_clock:.0f} Mm3 — against the 14-34 Mm3")
        print(f"  envelope published from the linear-store ensemble.")
    else:
        print(f"\n  NO overlap: Galchhi needs >= {v_galchhi:.0f} Mm3 and the")
        print(f"  clock allows <= {v_clock:.0f}. With this wedge geometry the")
        print(f"  two ends of the corridor cannot be satisfied together — a")
        print(f"  structural result about the store, not a size estimate.")
    print("\n  CAVEAT, and it is the whole caveat: this is ONE composition")
    print("  (w0 and mu_dry held fixed), not an ensemble. It says where this")
    print("  scenario family crosses, not what the envelope becomes. The")
    print("  envelope is a rejection-sampling run and has not been done with")
    print("  the wedge installed.")
