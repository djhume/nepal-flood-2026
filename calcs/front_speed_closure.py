#!/usr/bin/env python3
"""
Is the model's demand for a LARGE release a fact about the event, or an
artifact of its drag closure?

WHY THIS EXISTS. On 4 Sept, chasing the entrainment ledger's event-size
contradiction, I reached for "the border volume was impounded river water" —
which fails on arithmetic (a brief impoundment stores 0.02-0.6 Mm3, not 20).
Dave's question afterwards was the right one: if I went looking for an exotic
source, is something actually unexplained? Is there an energy mismatch?

Answer to that: NO. The potential energy of even a 5 Mm3 release falling
1,200 m is 1.2e14 J against ~2.5e13 J of kinetic energy in a 20 Mm3 wave
moving at 50 m/s — nearly 5x more than needed. And a sliding-block energy
line, v = sqrt(2 g (drop - mu L)), which contains NO volume term at all,
permits 84-96 m/s in the upper gorge at literature mu. The observed 53 m/s
mean over the first 22 km is comfortably inside what gravity supplies at ANY
release size.

So the energy is fine, and the thing to interrogate is the model. Our
scenario table shows a strong volume dependence of the border arrival
(V=10 -> 08:47, V=30 -> 08:44, V=60 -> 08:42) which the energy line says
should not exist. Suspect: the momentum equation carries BOTH a Coulomb term
(mu rho g h — depth-INDEPENDENT deceleration, correct for a granular mass)
and a Manning term (g n^2 v^2 / h^(4/3) — depth-DEPENDENT, a WATER closure).
At v = 50 m/s and n = 0.06 those compare as:

     depth 2 m : Manning 35.0 m/s2  vs Coulomb 1.67  -> Manning 21x larger
     depth 10 m: Manning  4.1       vs         1.67  ->          2.5x
     depth 20 m: Manning  1.6       vs         1.67  ->          1.0x
     depth 85 m: Manning  0.24      vs         1.67  ->          0.14x

i.e. a thin flow is crushed by turbulent drag it should not feel if it is a
dense granular avalanche, and the only way the model can get such a flow to
the border on time is to make it DEEP — which means making it BIG.

THE TEST. Re-run the ice-rich scenarios across release volume with Manning
roughness varied. If the border clock at small V is recoverable by lowering
n alone, then "the border must pass V >= 30-60 Mm3" is a statement about the
drag closure, not about the mountain, and the event-size contradiction is
softer than ENTRAINMENT.md claims.

Run: python calcs/front_speed_closure.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import unified as U


def border(V, n_scale=1.0, w0=0.15, mu_dry=None):
    """Border (km 22) arrival in minutes, with Manning n scaled."""
    nn0 = U.R.nn.copy()
    U.R.nn = nn0 * n_scale
    U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:])
    U._settled.clear()                     # settling depends on n
    try:
        r = U.simulate(V_rel=V, w0=w0,
                       mu_dry=U.MU_DRY_ICE if mu_dry is None else mu_dry,
                       t_end=2.5 * 3600.0)
        return r["arrival"](22.0)
    finally:
        U.R.nn = nn0
        U.R.nf = 0.5 * (nn0[:-1] + nn0[1:])
        U._settled.clear()


OBS = 7.0     # minutes: 08:37:10 collapse -> 08:44 border CCTV

print(__doc__.split("THE TEST.")[0].strip()[:0] or "", end="")
print("border arrival (minutes after collapse); observed 7.0")
print(f"{'V (Mm3)':>9} | " + " | ".join(f"n x{s:<4.2f}" for s in
                                        (1.0, 0.7, 0.5, 0.35)))
print("-" * 52)
rows = {}
for V in (5e6, 10e6, 30e6, 60e6):
    out = []
    for s in (1.0, 0.7, 0.5, 0.35):
        ta = border(V, n_scale=s)
        out.append(ta)
    rows[V] = out
    print(f"{V/1e6:9.0f} | " + " | ".join(
        (f"{t:6.1f}" if np.isfinite(t) else "  none") for t in out))

print("\ninterpretation")
base = rows[30e6][0]
small = rows[5e6]
print(f"  V=30 at published n reaches the border in {base:.1f} min "
      f"({100*(base-OBS)/OBS:+.0f}% vs observed)")
for s, t in zip((1.0, 0.7, 0.5, 0.35), small):
    if np.isfinite(t):
        print(f"  V=5  at n x{s:.2f} -> {t:5.1f} min "
              f"({100*(t-OBS)/OBS:+.0f}%)")
print("""
  If a SMALL release makes the clock once turbulent drag is reduced, then the
  model's appetite for volume is a property of the Manning closure applied to
  a granular flow, not evidence about the size of the mountain that fell. The
  honest fix is a regime-dependent drag — turbulent for water, Coulomb-only
  for the granular core — which is the same two-phase split ENTRAINMENT.md
  already names as the binding constraint.""")
