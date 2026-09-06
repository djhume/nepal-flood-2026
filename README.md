# The Trishuli Investigation

Physics-based analysis of the **26 August 2026 Langtang Lirung collapse** and
the flood it sent down the Lhende Khola, the Bhote Koshi and the Trishuli, in
Rasuwa, Nepal — reported elsewhere as the **Bhote Koshi flood** and the Rasuwa
flood. It asks one narrow question — **where did the flood water actually come
from?** — and follows the answer into what it implies for warning people
downstream.

As of 5 September 2026, 1,342 people are confirmed dead in Nepal and 4,886
missing, with 31 dead and 531 missing on the Chinese side, and more than 5,300
injured. The missing count has begun to fall while the death toll rises — that
is bodies being recovered, not people found alive. Those figures are still
moving.

**Read it here → https://djhume.github.io/nepal-flood-2026/**

| Audience | Page |
|---|---|
| General reader | [The Water Was Already in the River](https://djhume.github.io/nepal-flood-2026/plain.html) |
| Scientist / engineer | [The Trishuli Water Ledger](https://djhume.github.io/nepal-flood-2026/report.html) |
| Reviewer / sceptic | [Model Workings](https://djhume.github.io/nepal-flood-2026/workings.html) |

There is **no Nepali translation**. One was drafted and withdrawn: it was
machine-translated, unreviewed by any Nepali speaker, and this is a subject
where a mistranslated hazard statement does more harm than no translation at
all. Anyone who reads Nepali and wants to translate it is welcome to — the
source is here and the licence permits it.

## What it found

1. **The water was already in the river.** Melting ice is expensive and falling
   is cheap: a ~1,200 m fall releases about 1/28th of the heat needed to melt a
   kilogram of ice. At the collapse size finding 4 supports, frictional melt
   caps at **1.1 Mm³** on best evidence and **2.5 Mm³** steel-manned, against
   the ~20 Mm³ of "excess" water officially estimated. Melt reaches 20 only at
   200 Mm³ with 80% ice, a 4,000 m drop *and* a heat partition at the top of the
   published range — every dial at its limit at once (`calcs/energy_water_budget.py`,
   scenarios 5–8). The wave was dominated by monsoon river water swept up en
   route. Three routes agree, though they share a channel profile.
2. **It did not fall like dry rock.** The border CCTV clock discriminates what
   the falling mass was *made of*, not how big it was: dry-rock scenarios arrive
   at 17–30 min at any volume, ice-rich and wet ones arrive on time. Note the
   direction — this **excludes dry rock**, it does not establish slush, and
   finding 4 leaves composition unresolved. The clock survived a challenge, and
   on 6 Sept its evidence base was rebuilt: rather than rely on a partisan
   outlet's account of the overlay, we obtained the footage and read the
   station's own clock directly (`research/event-dossier.md` §14). It reads
   **10:59:50 Beijing = 08:44:50 NPT**, so the elapsed time is **7 min 40 s**,
   not the 6 min 50 s published until then, and the 22-km mean front speed is
   **47.8 m/s**, not 53.7. Kargel's identical 6:50 now looks like the same
   minute-rounding by another road rather than independent confirmation. The
   finding is unaffected — 17 and 23 min stay excluded — and the Syabrubesi
   gauge (3.8 m at 08:50, km 37.6, a Nepali instrument owing nothing to any
   camera) still carries it independently. Read alongside report §04b (added
   6 Sept): the Lhende held ~0.5 Mm³ of water against a 14–34 Mm³ release, so
   what reached the border was a rock–ice avalanche, not a flood, and the run
   is what an ice-rich mass does on its own — the lubrication is the ice
   skate's, frictional melt at the base, not bulk water.
3. **The method travels — one test stands, one is withdrawn.** Against Chamoli
   2021 the model reproduces the Tapovan arrival once frictional melt is given a
   thermal lag (one fitted number; the speeds are then out of sample) — a
   partial pass: the Raini basin transit reads 13 min against ~27 published, and
   that gap widened when an arrival bug was fixed. A second test against the
   2012 Seti flood was reported here as a clean pass and has been
   **withdrawn**: the channel profile it ran on had 31 of 54 km flattened
   to zero gradient by a path-building bug, and on a corrected channel the model
   fails. See `hindcast/seti/RESULTS.md`.
4. **The collapse was 14–34 Mm³ (median 21).** Published estimates span a factor
   of four hundred, so rather than argue them one at a time, `calcs/ensemble.py`
   samples six contested inputs over wide priors, runs the full model, and keeps
   only what reproduces every observable: 26 of 220 pass. Only the *volume* is
   constrained — liquid fraction, μ_dry and f_fine each span >90% of their priors.
   One exposure: the border-speed observable is 48.5 ± 35% m/s, and the first
   peer-reviewed study of the event measures 19 m/s at the same place. Not yet
   re-scored against it.
5. **The single-phase model was falsified, then fixed.** With entrainment built
   (`model/ENTRAINMENT.md`, literature constants, nothing fitted) the model tears
   3.8 Mm³ out of the corridor against 3.2 measured by stereo DEM — but the same
   change buries 18 Mm³ against a 12 Mm³ cap and the front never reaches the
   border. Rejection sampling found **0 of 150** samples satisfying the clocks
   and the mass balance together, which falsifies the model *form*, not its
   parameters. The fix splits the solids: coarse deposits and carries the
   granular friction, fine and ice ride with the water. Darcy Weedman at geopera
   reached the same conclusion the same week by gradient-descent calibration —
   corroboration, not replication; both analyses are unreviewed.
6. **What is not settled:** the source volume and ice fraction are unpublished
   and composition is unresolved; the modelled deposit sits at km 0–36 where
   stereo puts it at 40–43; the Galchhi stage rise fails out of sample (3.6 m
   modelled vs ~9 observed) on lower-reach channel widths that are a rule of
   thumb; the Devghat peak meets its factor-of-2 criterion but every passing run
   lands below the observation. Not peer-reviewed, and no Nepali scientist has
   read it.

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
.venv/bin/python calcs/ensemble.py 220            # the size envelope (~75 min)
```

**The portability tests** (other disasters, constants frozen):

```bash
.venv/bin/python hindcast/chamoli/run_hindcast.py   # kinematic law, zero recalibration
.venv/bin/python hindcast/chamoli/run_voellmy.py    # Voellmy-Saint-Venant + thermal lag
cd hindcast/seti && python build_path2.py && python widths.py && python run_seti.py
#   ^ Seti 2012 — WITHDRAWN result, kept reproducible; build_path.py is the
#     superseded v1 stitch that produced the broken profile
```

**Rebuilding the site** — order matters, and all four pages must be rebuilt
together. The published workings once fell three days behind the findings
because this was a hand step nobody had written down; it is a script now.

```bash
.venv/bin/python hindcast/chamoli/run_voellmy.py   # -> voellmy_curves.json
.venv/bin/python model/export_json.py              # runs snowplow+ladder (~2-4 min)
.venv/bin/python model/export_map.py               # APPENDS the corridor map
.venv/bin/python report/build.py                   # -> report/report.html

.venv/bin/python notebooks/build_workings.py       # cells -> .ipynb
(cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook \
    --execute --inplace trishuli_workings.ipynb)   # run them (~2 min)
.venv/bin/python notebooks/build_workings_html.py  # -> report/workings.html

.venv/bin/python report/build_site.py              # report/*.html -> docs/
```

`build_site.py` checks every internal link resolves and every page carries the
head skeleton GitHub Pages does not supply. Run it before pushing.

Network calls (OpenStreetMap Overpass, opentopodata elevations) are cached to
disk on first run; delete the cache files to refetch.

## Layout

| Path | Contents |
|---|---|
| `PLAN.md` | **Authoritative state document** — hypotheses, every model version, results, honesty rails |
| `model/` | The routing models. `unified.py` is current; `ladder.py` and `snowplow.py` are frozen references that still drive published figures |
| `calcs/` | First-order energy and water budgets, validated against Chamoli 2021 |
| `hindcast/chamoli/`, `hindcast/seti/` | Portability tests on other disasters, each with a `RESULTS.md` scorecard |
| `research/` | Evidence dossier (incl. §14 video forensics, §15 the first 22 km as a rock–ice avalanche), literature review, imagery-composition memo, pre-registered Seti anchors |
| `data/` | River profiles, cross-sections, gauge and barrage records — see `DATA-SOURCES.md` |
| `report/` | The published pages and their build scripts; `docs/` is the built output GitHub Pages serves |
| `notebooks/` | The executable workings and the two scripts that build and render them |
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

Version 6, 6 September 2026. Preliminary, independent, AI-assisted analysis
published days after the event. Five results have been withdrawn or reversed in
that time and all five remain readable on the site with their reasons.
**Not peer-reviewed, not read by any Nepali scientist, and not suitable as the
basis of an operational warning system or evacuation decision without
independent expert validation** — see `LICENSE`.

Code MIT; prose and figures CC BY 4.0; third-party data under its own terms
(`DATA-SOURCES.md`, including the ODbL attribution OpenStreetMap requires).

Analysis by **Dave Hume**, carried out with Claude (Anthropic) as a research
assistant. Corrections and reuse are welcome — [open an
issue](https://github.com/djhume/nepal-flood-2026/issues); corrections are
recorded on the site's home page with the date and the reason. No attribution
obligation beyond the licences, and no reply expected. The channel profile, the
routing models and the corridor map are free for DHM, ICIMOD, NDRRMA or anyone
else to take, with or without us.
