#!/usr/bin/env python3
"""
What the up-valley WEDGE does to everything downstream.

Dave, 4 Sept: "this is a larger capacitor/bucket to hold and then drain, so
quite the non-linearity - it means everything downstream was lesser than it
could have been... it suggests we might be undersizing the initial event?"

Both halves of that are testable, and they pull in opposite directions from
everything else this week, so they are worth testing properly.

THE ELEMENT. The model's Kyirong upstream arm at km 22 was a CONSTANT-PLAN-AREA
store: 1.5e6 m2 capped at 8 m fill = 12 Mm3, a LINEAR capacitor, V = A h.
A backwater wedge is not linear. It runs a distance h/S up its own valley, so
its plan area grows with fill and its volume goes as the SQUARE of the head:

        A(h) = w h / S          V = w h^2 / (2 S)

Dave traced the 1,920-1,930 m stagnation elevation ~3.5 km up that arm, which
needs S ~ 0.031 at a head of 110 m; Sentinel-2 channel widening tapers away
over the same distance (calcs/sentinel_wedge.py); and Xinhua report ~3 km of
the G216 approach road destroyed. Three routes, one length.

At w = 100 m and S = 0.031 the wedge holds 19 Mm3 at full head - against the
12 Mm3 the old element could hold, and with a completely different filling
character: it barely engages at low stage, then swallows volume fast once the
junction stagnates.

WHAT THIS SCRIPT ASKS
  1. How much volume actually goes into the wedge, and when does it come back?
  2. How much does it cut the downstream peak - Dave's "lesser than it could
     have been"?
  3. Does recovering the distal observables then require a BIGGER release -
     Dave's "undersizing the initial event"?

Run: python calcs/wedge_effect.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import core
import unified as U

# (name, km, plan area, weir width, sill[, wedge slope, max fill])
LINEAR = ("Kyirong upstream arm", 22.0, 1.5e6, 150.0, 1.0)
WEDGE_W, WEDGE_S, WEDGE_H = 100.0, 0.031, 110.0
WEDGE = ("Kyirong upstream arm", 22.0, 1.5e6, WEDGE_W, 1.0, WEDGE_S, WEDGE_H)


def set_branch(entry):
    U.R.side = [entry] + [e for e in U.R.side if e[0] != entry[0]]
    U.R.side_node = {e[0]: int(np.argmin(np.abs(U.x_km - e[1])))
                     for e in U.R.side}
    U._settled.clear()


def run(entry, V, w0=0.15, t_end=10.0 * 3600.0):
    set_branch(entry)
    r = U.simulate(V_rel=V, w0=w0, mu_dry=U.MU_DRY_ICE, t_end=t_end)
    q = r["Devghat"]["q"]; t = r["t"]
    m = t > 30
    i = int(np.argmax(np.where(m, q, -1)))
    qg = r["Galchhi"]["h"]
    rise = max(qg[j + 180] - qg[j] for j in range(len(qg) - 180))
    return dict(devghat=q[i], t_peak=t[i], galchhi=rise,
                border=r["arrival"](22.0), betrawati=r["arrival"](68.4))


if __name__ == "__main__":
    print(__doc__.split("WHAT THIS SCRIPT ASKS")[0])
    print(f"wedge at w={WEDGE_W:.0f} m, S={WEDGE_S}, head {WEDGE_H:.0f} m")
    print(f"  holds {WEDGE_W*WEDGE_H**2/(2*WEDGE_S)/1e6:.1f} Mm3 at full head, "
          f"against 12.0 Mm3 for the old linear element\n")

    print("1 & 2 — SAME RELEASE, LINEAR STORE vs WEDGE")
    print(f"  {'':22}{'border':>8}{'Betrawati':>11}{'Galchhi rise':>14}"
          f"{'Devghat peak':>14}{'at':>8}")
    base = {}
    for lab, ent in (("linear 12 Mm3 store", LINEAR), ("WEDGE 19 Mm3", WEDGE)):
        r = run(ent, 30e6)
        base[lab] = r
        print(f"  {lab:22}{r['border']:7.1f}m{r['betrawati']:10.1f}m"
              f"{r['galchhi']:13.1f} m{r['devghat']:13,.0f}"
              f"{U.clock(r['t_peak']):>8}")
    a, b = base["linear 12 Mm3 store"], base["WEDGE 19 Mm3"]
    print(f"\n  Devghat peak {a['devghat']:,.0f} -> {b['devghat']:,.0f} "
          f"({100*(b['devghat']-a['devghat'])/a['devghat']:+.0f}%)")
    print(f"  Galchhi rise {a['galchhi']:.1f} -> {b['galchhi']:.1f} m "
          f"({100*(b['galchhi']-a['galchhi'])/max(a['galchhi'],0.01):+.0f}%)")
    print("  observed: Galchhi ~9 m, Devghat 5,850 total / ~2,900 excess @16:00")

    print("\n3 — DOES THE WEDGE MEAN WE NEED A BIGGER RELEASE?")
    print("  sweep V with the wedge installed and see what it takes to get")
    print("  back to (and past) the linear store's distal answer")
    print(f"  {'V (Mm3)':>9}{'border':>9}{'Galchhi rise':>14}{'Devghat peak':>14}")
    for V in (30e6, 45e6, 60e6, 90e6):
        r = run(WEDGE, V, w0=0.40 if V >= 60e6 else 0.15)
        print(f"  {V/1e6:9.0f}{r['border']:8.1f}m{r['galchhi']:13.1f} m"
              f"{r['devghat']:13,.0f}")
    print("\n  (w0 raised to 0.40 at V>=60 to stay in the wet-scenario family")
    print("   the timing evidence favours)")
