# Nepal Flood 2026 — Modeling Project

Testing water provenance and wave dynamics of the 26 Aug 2026 Langtang Lirung avalanche →
Trishuli flood. Started 2 Sept 2026 after watching Shawn Willsey's interview with Jeff Kargel.

- `PLAN.md` — hypotheses, verdicts so far, model plan (start here)
- `research/event-dossier.md` — evidence dossier, ~30 sources, contested numbers flagged
- `research/science-review.md` — literature on water sources & wave evolution (Chamoli, Seti,
  Melamchi, Huascarán, Kolka; kinematic wave theory; modeling tools)
- `calcs/energy_water_budget.py` — first-order source budgets, validated against Chamoli 2021
- `notebooks/trishuli_workings.ipynb` — executed workings notebook (rebuild: see
  `notebooks/build_workings.py`); published render: report/workings.html
- `report/` — report.src.html + build.py → report.html (interactive D3 charts +
  client-side assumption explorer; chart_data.json from model/export_json.py)
- `model/unified.py` — Phase B3: one-equation scar→Devghat model with the
  dilution dial (v1: upper reach + composition discrimination robust; distal
  rheology open — see PLAN.md)

Published pages (same URLs across updates):
- Report: https://claude.ai/code/artifact/1fd064d2-fdc3-407e-b748-99b0e3cb3eb8
- Workings notebook: https://claude.ai/code/artifact/60a02c4d-5fd3-439b-b483-bc42bcd4abcb
- `hindcast/chamoli/` — Phase F portability tests: kinematic zero-recalibration
  (run_hindcast.py) + Voellmy–Saint-Venant with melt-fluidization & thermal lag
  (run_voellmy.py); verdicts in RESULTS.md
- `outreach/` — DHM data-request draft + two-tier warning concept note (for Dave to send)
- `data/transects.json` — DEM valley cross-sections (40 stations); `data/valmikinagar_barrage.csv`,
  `data/ffd_report.pdf` — downstream + official records
