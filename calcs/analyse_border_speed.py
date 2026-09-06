#!/usr/bin/env python3
"""
What does the CAS border speed do to the size envelope?

Reads calcs/ensemble_border_speed.npy (written by ensemble_border_speed.py:
the same 220 samples as the published run, plus the LOCAL velocity at km 22
and km 30) and scores the envelope under every defensible reading of the
border-speed observable.

The point of the exercise is that "re-score against 19 m/s" has no single
meaning until you say WHICH model quantity the 19 is supposed to match. Three
candidates, and they give different answers:

  reach maximum   max(umax[0:km22])  -- what the published run scores
  local at km 22  max over time of the depth-averaged velocity at the junction
  local at km 30  the node SPEED_OBS actually anchors geopera's 48.5 to

First it checks that the re-run reproduced the published samples, because the
whole comparison rests on them being the same 220 realisations.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A = np.load(os.path.join(HERE, "ensemble_border_speed.npy"))
S = np.load(os.path.join(HERE, "ensemble_samples.npy"))

V, w0, mu, ns, he, ff = (A[:, i] for i in range(6))
border, syabru, vmax022, ero, dep = (A[:, i] for i in range(6, 11))
v22, v30 = A[:, 11], A[:, 12]

# ---- 0. did the re-run reproduce the published samples? -------------------
n = min(len(A), len(S))
same_inputs = np.allclose(A[:n, :6], S[:n, :6])
d = np.abs(A[:n, 8] - S[:n, 8])
fin = np.isfinite(d)
print("REPRODUCIBILITY")
print(f"  sampled inputs identical to the published run: {same_inputs}")
print(f"  reach-max speed reproduces: max |diff| = {d[fin].max():.3g} m/s "
      f"over {fin.sum()} finite samples")
if not same_inputs:
    print("  !! inputs differ — the comparison below is not like-for-like")

# ---- 1. the non-speed constraints, held fixed throughout ------------------
base = (np.isfinite(border) & (np.abs(border - 7.68) <= 0.30 * 7.68)
        & np.isfinite(syabru) & (np.abs(syabru - 13.0) <= 0.50 * 13.0)
        & np.isfinite(ero) & (np.abs(ero - 3.2) <= 0.60 * 3.2)
        & np.isfinite(dep) & (dep <= 12.0))
print(f"\n{len(A)} samples; {base.sum()} satisfy the clock, erosion and "
      f"deposition constraints before any speed test is applied")


def envelope(mask, label):
    k = mask.sum()
    if not k:
        print(f"  {label:52s} {k:3d}   —")
        return
    v = V[mask] / 1e6
    print(f"  {label:52s} {k:3d}   {v.min():5.1f}-{v.max():5.1f} Mm3  "
          f"median {np.median(v):5.1f}")


def band(x, val, tol=0.35):
    return np.isfinite(x) & (np.abs(x - val) <= tol * val)


print("\nENVELOPE UNDER EACH READING OF THE BORDER-SPEED OBSERVABLE")
print(f"  {'':52s} {'n':>3s}   release volume")
envelope(base & band(vmax022, 48.5), "PUBLISHED  reach max vs 48.5 (superelevation)")
envelope(base & band(vmax022, 19.0), "reach max vs CAS 19            [category error]")
envelope(base & band(v22, 48.5),     "local km22 vs 48.5")
envelope(base & band(v22, 19.0),     "local km22 vs CAS 19           [commensurable]")
envelope(base & band(v30, 48.5),     "local km30 vs 48.5  (where SPEED_OBS anchors it)")
envelope(base & band(v30, 19.0),     "local km30 vs CAS 19")
envelope(base,                       "no speed constraint at all")

# ---- 2. what the model actually produces for each quantity ----------------
print("\nWHAT THE MODEL PRODUCES, over the samples that pass everything else")
for name, x in [("reach max, km 0-22", vmax022), ("local at km 22", v22),
                ("local at km 30", v30)]:
    q = x[base & np.isfinite(x)]
    if len(q):
        print(f"  {name:22s} {q.min():6.1f} - {q.max():6.1f} m/s   "
              f"median {np.median(q):6.1f}   "
              f"n within CAS 19+/-35%: {band(q, 19.0).sum()}")

# ---- 3. is CAS compatible with the 7-minute clock at all? -----------------
clock = np.isfinite(border) & (np.abs(border - 7.68) <= 0.30 * 7.68)
print("\nIS THE CAS NUMBER COMPATIBLE WITH THE 7-MINUTE CLOCK?")
print(f"  samples meeting the clock alone: {clock.sum()}")
for name, x in [("reach max", vmax022), ("local km22", v22), ("local km30", v30)]:
    both = (clock & band(x, 19.0)).sum()
    print(f"    ...and {name:11s} within CAS 19 +/-35%: {both}")
print("  (zero everywhere would mean the CAS value and the 7-minute clock are")
print("   incompatible in this model however the quantity is matched — which")
print("   makes it evidence about the clock, not about the release volume.)")
