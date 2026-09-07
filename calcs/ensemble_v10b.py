#!/usr/bin/env python3
"""
ENSEMBLE v10b — second-stage sample of v10 (dossier §24).

v10 (300 LHS samples, 11 inputs) passed nothing but bracketed the answer:
its three 10-of-11 and ten 9-of-11 runs span a box in which the wet corner
fails Galchhi high and the dry corner fails the gorge speed and the lower
clocks. Between them v10's own cut at w0 0.3–0.55 had Galchhi inside its
window. Eleven dimensions at 300 samples is ~1.7 samples per dimension per
octave; this is the standard population refinement — resample INSIDE the box
those thirteen runs span (padded 15 %, clipped to the stage-1 prior), same
physics, geometry, observables and held-out set. It is reported as what it
is: a stage-2 posterior conditional on stage 1, not an independent prior.
Box (stage-1 range -> stage-2):
  V_rel    1e+06-2e+08 -> 9.27e+07-1.673e+08
  w0       0.02-0.95 -> 0.02-0.95
  mu_dry   0.03-0.35 -> 0.03765-0.35
  n_scale  0.7-1.4 -> 0.7-1.4
  h_erode  1-10 -> 1-10
  f_fine   0-0.98 -> 0.0277-0.98
  xi       100-2000 -> 100-1668
  k_junc   1-10 -> 1.161-9.739
  f_wl     0.3-1 -> 0.3043-0.789
  f_ice    0.3-0.9 -> 0.3-0.9
  T_rel    60-600 -> 61.61-600
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "model")); sys.path.insert(0, HERE)
import ensemble_v10 as V10
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
BOX = {'V_rel': ('log', 92700481.88290726, 167318820.0947365), 'w0': ('lin', 0.02, 0.95), 'mu_dry': ('lin', 0.037653195206221346, 0.35), 'n_scale': ('lin', 0.7, 1.4), 'h_erode': ('lin', 1.0, 10.0), 'f_fine': ('lin', 0.02770471469244047, 0.98), 'xi': ('log', 100.0, 1667.53453461898), 'k_junc': ('lin', 1.1610763436940614, 9.739241228001482), 'f_wl': ('log', 0.30430264775782506, 0.7889783353981896), 'f_ice': ('lin', 0.3, 0.9), 'T_rel': ('log', 61.60695008179986, 600.0)}
if __name__ == "__main__":
    V10.PRIORS.clear(); V10.PRIORS.update(BOX)
    V10.main(N, tag="v10b")
