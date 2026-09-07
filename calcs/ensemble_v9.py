#!/usr/bin/env python3
"""
ENSEMBLE v9 — v8 with the drag following the flow's composition.

WHY (dossier §21). v7/v8 showed one Voellmy coefficient cannot serve both
reaches: the 70 m debris flow in the gorge wants xi of order 500–900, the
muddy flood below Betrawati wants none (xi < 400 stalls it; xi > 400 leaves
Galchhi at 12–18 m). The flow was a debris flow in the gorge and a flood in
the lower river, and the engine already tracks the water fraction w at every
face. v9 weights the Voellmy term by the coarse-solids fraction
(1 - w)/(1 - W_SAT), clipped to [0, 1] — full drag at or below pore
saturation (w <= 0.25), none for pure water — so xi becomes the debris-flow
coefficient (literature 300–1,000) and the diluted lower river reverts to
Manning. w is the WATER fraction only: fines keep their drag (a mud-rich
debris flow is still a debris flow); dilution by water is what ends it.
No new prior: same nine inputs, observables, geometry and held-out set as v8.

Run:  .venv/bin/python calcs/ensemble_v9.py [n_samples]
Writes calcs/ensemble_samples_v9.npy and output/ensemble_v9_RESULTS.md.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "model")); sys.path.insert(0, HERE)
import core
import ensemble_v8 as V8

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
PRIORS = V8.PRIORS

if __name__ == "__main__":
    core.XI_COMP = True
    V8.main(N, tag="v9", title="# Ensemble v9 — v8 with the Voellmy drag weighted by the solids fraction (dossier §22)\n")
