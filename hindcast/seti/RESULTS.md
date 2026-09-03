# Seti 2012 blind hindcast — the intermediate-regime test

**Run:** 3 September 2026, `run_seti.py`. **Protocol:** every dial constant
frozen at its published Trishuli/Chamoli value; every event input taken from
`research/seti-2012-anchors.md`, which was written before the model was run.
Nothing in this hindcast is fitted to a Seti observation.

## Why this event

The dial spans two endmembers we had already used: Chamoli (dry winter
granular, water made by melt) and Langtang (wet monsoon, water supplied by the
river). Seti 2012 is the intermediate case *by construction* — a rock/ice
avalanche fell into a gorge holding a lake that had been impounding behind a
rockfall dam for weeks. The water is neither melted nor lying along the
channel: it is a discrete stored volume released on impact. Two-point fits
don't extrapolate to a third mechanism by luck.

**Pre-registered expectation (from the anchors file, before running):** *"the
front must be SLOW — ~12 m/s, four times slower than Langtang. A model tuned
on Langtang's fast wave would fail here by running away."*

## Path check — an unplanned consistency test

The OSM stitch (waypoint-guided: Sabche Cirque → the OSM hamlet "Kharpani" at
28.3602 N, 83.9604 E → Pokhara) puts the gorge head at path-km **11.2** and
Kharapani at **31.2** — i.e. **20.0 km below the dam**, against the published
"20 km downstream at Kharapani". The published distance and our independently
built path agree to 0.1 km. (Our first attempt, a Pokhara-seeking greedy walk,
wandered onto the Phirke Khola and put Kharapani 6 km off the line; the
waypoint-guided version fixed it. The published "40 km north of Pokhara" is
road distance, not river distance.)

## Scorecard — nominal run (22 Mm³ avalanche + 3 Mm³ impoundment)

| Quantity | Model | Observed | Error | ±50% tier |
|---|---|---|---|---|
| **Kharapani arrival** | **21.5 min** | **28.1 min** (photo timestamp) | **−23%** | **PASS** |
| **Pokhara arrival** | **100.2 min** | **~85 min** | **+18%** | **PASS** |
| Dam→Kharapani mean front speed | 15.6 m/s | ~12 m/s | +30% | PASS |
| Peak Q at Kharapani | 2,395 m³/s | ~935 m³/s | +156% | FAIL |
| Water fraction w at passage | 0.92 | ~0.47 (ρ = 1.88 g/cm³) | +96% | FAIL |
| Stranded solids | 11.6 of 19.8 Mm³ | not published | — | — |

The pre-registered failure mode did **not** occur: the model produced a slow
front (15.6 m/s against Langtang's ~53) on a steeper path, because the dial
put this flow in a different regime, not because anything was retuned.

## The strongest result: the model requires the impounded lake

Sweeping only the stored volume, with everything else fixed:

| Impoundment | Kharapani arrival | Pokhara | Verdict |
|---|---|---|---|
| **0 (avalanche alone)** | **65.2 min (+132%)** | **never reaches** | **FAIL** |
| 1 Mm³ | 41.7 min (+48%) | never reaches | marginal / FAIL |
| **3 Mm³ (nominal)** | **21.5 min (−23%)** | **100 min (+18%)** | **PASS** |
| 6 Mm³ | 14.5 min (−48%) | 75 min (−12%) | marginal PASS |

A 22 Mm³ rock/ice avalanche falling into a pre-monsoon trickle **cannot**
reach Kharapani on time: it strands in the gorge and the flood never arrives
at Pokhara at all. Adding ~2–4 Mm³ of stored water — and nothing else — moves
the arrival onto the observed clock.

**This is Kargel's and Hanisch et al.'s conclusion, reproduced from dynamics
alone.** Their reasoning was observational (no glacial lake existed, so where
did the water come from? — a rockfall-dammed impoundment filled by weeks of
spring melt). Ours is independent: the momentum equation says a dry-ish
avalanche cannot deliver that arrival time, and quantifies how much stored
water closes the gap. Two different methods, one answer, on a third event.

It is also the H1 result in miniature. Seti's flood water was in the valley
before the avalanche; Langtang's was in the river before the collapse. The
mechanism differs (impoundment vs. monsoon flow); the conclusion — *the
mountain supplies momentum, the valley supplies water* — is the same.

## What fails, and why it is the same failure as Langtang

**Sediment concentration.** The model delivers w ≈ 0.92 (nearly clean water)
at Kharapani, while the measured flow density of 1.88 g/cm³ implies w ≈ 0.47 —
a dense slurry. The model strands 11.6 of 19.8 Mm³ of solids upstream and
carries clean water past them.

This is the *same deficiency* the Langtang run showed (~100% river-derived
water at Devghat) and the same one geopera's stereo DEM exposed from the other
direction: the Langtang corridor was **net erosional by ~3.5×**, and our model
has no erosion term at all. It can drop sediment; it cannot pick any up. A
real debris flood entrains its bed — which is both how it stays dense and how
it gouges 8–12 m out of a gorge floor.

So: **the next structural addition is an entrainment term**, and we now have
two independent, quantitative targets for it (Seti's ρ = 1.88; Langtang's
measured erosion/deposition ratio). The peak-discharge overshoot (2,395 vs
935 m³/s) is likely the same story plus my uncalibrated slot-canyon widths.

## Standing

Timing — the thing this test existed to check — **passes at both anchors with
zero recalibration**, and the model independently recovers the published
water-source mechanism. Sediment transport fails in a now well-characterised,
fixable way. Portability claim after three events: the arrival-time physics
travels across regimes (granular Chamoli, impounded Seti, watery Langtang);
the sediment physics does not travel yet because it is not there.

## Bug found and fixed during this run

`arrival()` used `np.interp` against the cumulative front position. Once the
front saturates at the last node the array has a long flat tail, and
interpolating a value inside a plateau returns a point in its middle — it
reported Pokhara at 180 min instead of 100. Fixed to a first-crossing search
in `run_seti.py`, and the same pattern corrected in `model/unified.py` and
`hindcast/chamoli/run_voellmy.py`. **Blast radius check:** Chamoli's scored
anchor (Tapovan, km 23.2 of a 32.4 km path) sits on the rising part of the
front curve, so the published Chamoli numbers are unaffected; the Trishuli
scenario table's Devghat figures are peak-based, not front-based, so they are
unaffected too. Only front-arrival-at-the-final-node was ever wrong.

## Files

- `build_path.py` — waypoint-guided OSM stitch → `profile.csv` (137 pts, 400 m)
- `run_seti.py` — the hindcast (physics copied verbatim from `model/unified.py`)
- `seti_hindcast.png` — front trajectory, hydrographs, and the dial's water
  fraction against the published flow density
- Anchors (pre-registered): `research/seti-2012-anchors.md`
