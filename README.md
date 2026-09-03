# The Trishuli Investigation

Physics-based analysis of the **26 August 2026 Langtang Lirung collapse** and
the flood it sent down the Trishuli River, Nepal. It asks one narrow question —
**where did the flood water actually come from?** — and follows the answer into
what it implies for warning people downstream.

**Project home (start here):**
https://claude.ai/code/artifact/50fbb9c4-1dd2-43f6-a8c1-dbbf80e9d197

| Audience | Page |
|---|---|
| General reader | [The Water Was Already in the River](https://claude.ai/code/artifact/39288bec-8708-4d94-8366-7a4966692543) |
| नेपालीमा (AI-translated, unreviewed) | [पानी त नदीमै थियो](https://claude.ai/code/artifact/d2d2daa8-4ea2-4570-b7ec-515fdb7bd239) |
| Scientist / engineer | [The Trishuli Water Ledger](https://claude.ai/code/artifact/1fd064d2-fdc3-407e-b748-99b0e3cb3eb8) |
| Reviewer / sceptic | [Model Workings](https://claude.ai/code/artifact/60a02c4d-5fd3-439b-b483-bc42bcd4abcb) |

## What it found

1. **The water was already in the river.** A ~1,200 m fall cannot melt enough
   ice to make this flood — the energy ceiling sits well below the ~20 Mm³ of
   "excess" water officially estimated. The wave was dominated by monsoon river
   water swept up en route. Three independent routes agree.
2. **It moved like slush, not gravel.** The 08:44 border CCTV clock
   discriminates what the falling mass was *made of*, not how big it was:
   ice-rich and wet scenarios arrive on time, dry-rock scenarios never do at any
   volume. Published imagery agrees qualitatively.
3. **The method travels.** Run unchanged against the 2012 Seti River flood, the
   model lands both arrival times and independently concludes that a stored body
   of water must have been released — which is what investigators of that
   disaster found by observation.
4. **What is not settled:** the source volume and ice fraction are unpublished;
   the model has **no sediment-entrainment term**, so it carries too little mud
   downstream; distal flood peaks remain uncertain. Not peer-reviewed.

Every contested number is flagged at the point of use. `PLAN.md` §6 ("Honesty
rails") states the rules this project holds itself to; `PLAN.md` is also the
authoritative running record of every model version and result.

## Reproducing it

Python 3.12, numpy + matplotlib only. Everything runs on a laptop in seconds to
minutes; no HPC, no proprietary data.

```bash
python -m venv .venv && .venv/bin/pip install numpy matplotlib
```

**The models** (each prints its own scorecard against observations):

```bash
.venv/bin/python calcs/energy_water_budget.py     # source-by-source water budget
.venv/bin/python model/snowplow.py                # front/peak routing + water ledger
.venv/bin/python model/ladder.py                  # equivalent-circuit routing
.venv/bin/python model/unified.py                 # the live model: scar -> Devghat
```

**The portability tests** (other disasters, constants frozen):

```bash
.venv/bin/python hindcast/chamoli/run_hindcast.py   # kinematic law, zero recalibration
.venv/bin/python hindcast/chamoli/run_voellmy.py    # Voellmy-Saint-Venant + thermal lag
cd hindcast/seti && python build_path.py && python run_seti.py   # blind test
```

**Rebuilding the report pages** — order matters:

```bash
.venv/bin/python hindcast/chamoli/run_voellmy.py   # -> voellmy_curves.json
.venv/bin/python model/export_json.py              # runs snowplow+ladder (~2-4 min)
.venv/bin/python model/export_map.py               # APPENDS the corridor map
.venv/bin/python report/build.py <workings-url>    # -> report/report.html
```

Network calls (OpenStreetMap Overpass, opentopodata elevations) are cached to
disk on first run; delete the cache files to refetch.

## Layout

| Path | Contents |
|---|---|
| `PLAN.md` | **Authoritative state document** — hypotheses, every model version, results, honesty rails |
| `model/` | The routing models. `unified.py` is current; `ladder.py` and `snowplow.py` are frozen references that still drive published figures |
| `calcs/` | First-order energy and water budgets, validated against Chamoli 2021 |
| `hindcast/chamoli/`, `hindcast/seti/` | Portability tests on other disasters, each with a `RESULTS.md` scorecard |
| `research/` | Evidence dossier, literature review, imagery-composition memo, pre-registered Seti anchors |
| `data/` | River profiles, cross-sections, gauge and barrage records — see `DATA-SOURCES.md` |
| `report/` | The published pages and their build script |
| `outreach/` | Draft data requests and a warning-system concept note |

## The physics, briefly

A 1-D Voellmy–Saint-Venant model with a **compositional dilution dial**: basal
friction μ is a function of the water volume fraction *w*, which is advected and
mixed with the flow. Below pore saturation the flow is Coulomb-granular; above
it, a Bingham slurry; at *w* = 1 it reduces exactly to Manning, i.e. to ordinary
flood routing. Water enters by frictional melt (Chamoli), by impoundment release
(Seti), or by entraining the monsoon river (Trishuli) — one dial, different
taps. Plus local inertia, convective momentum, curvature-triggered shock
viscosity, and sediment stranding.

The earlier equivalent-circuit ("ladder") model is retained: it is the exact
linear limit of the above (diffusive wave = RC transmission line, Hayami 1951)
and remains a useful explanation of storage, junctions and pulse structure.

## Status, licence, and use

Version 1, 3 September 2026. Preliminary, independent, AI-assisted analysis
published days after the event. **Not peer-reviewed. Not suitable as the basis
of an operational warning system or evacuation decision without independent
expert validation** — see `LICENSE`.

Code MIT; prose and figures CC BY 4.0; third-party data under its own terms
(`DATA-SOURCES.md`, including the ODbL attribution OpenStreetMap requires).

Analysis by **Dave Hume**, carried out with Claude (Anthropic) as a research
assistant. Corrections and reuse are welcome; no attribution obligation beyond
the licences, and no reply expected.
