# Seti 2012 hindcast — **the v1 result is withdrawn**

**v1 run:** 3 September 2026, reported as a passed blind test.
**v2 run:** 3 September 2026 (night), after a channel-profile bug was found.
**Verdict: the v1 pass was an artifact of a broken profile. Both of v1's
conclusions are withdrawn.**

This file replaces the earlier scorecard. The v1 text is preserved in git
history (commit `3e4bb6e` and earlier) and the v1 profile is kept as
`profile_v1.csv` so the withdrawn result stays reproducible.

## What was wrong

`build_path.py` stitched the channel by walking greedily from way to way and
**bridging in a straight line** whenever it could not find a continuation
within 5 km. Between the Sabche Cirque and Kharapani it did this repeatedly,
so roughly 17 km of the "river" was straight lines flown across the cirque rim
and its ridges. The sampled elevations along those bridges oscillate by
1,500 m — 1,020 m at km 9.6, 4,042 m at km 11.2, 3,096 m at km 24.0 — because
they are reading ridge tops.

`run_seti.py` then applied the standard monotone-descent clamp
(`np.minimum.accumulate`) that every profile in this project uses to remove
DEM noise. Against a 1,882 m spurious step that clamp does not clean the
profile, it **destroys** it: everything from km 9.6 to km 41.6 was held at a
constant 1,020 m. **31 of 54 km of channel, including the entire runout from
the dam site past Kharapani, had exactly zero gradient.** 64% of nodes were
clamped.

A flood on a flat bed is driven only by its own depth gradient. The model was
therefore slowed by roughly the amount needed to match the observed arrival
times, for a reason that had nothing to do with its physics.

The same clamp is benign on the other two paths, which is why this went
unnoticed: Trishuli clamps 48% of nodes but by a mean of 9 m with a longest
flat run of 6 km, and Chamoli clamps 11% with a longest run of 0.8 km. Only
Seti had a straight-line bridge large enough to poison it. A profile-integrity
check (longest flat run, largest raw upward step) now belongs in every path
build.

## The corrected channel

`build_path2.py` replaces the greedy walk with a Dijkstra shortest path over a
graph of every mapped waterway in the bbox, healing sub-150 m gaps with
penalised edges. OSM does carry a continuous Seti here — way 352604044 is a
single 20.6 km line from the cirque outlet to below Kharapani — and v1 simply
never chained onto it. Elevations are snapped to the local valley floor with a
±60 m perpendicular stencil.

| | v1 | v2 |
|---|---|---|
| path length | 54.4 km | 49.6 km |
| nodes clamped | 64% | 23% |
| longest flat run | **31.2 km** | 3.2 km (cirque outlet) |
| bed slope, dam → Kharapani | **0.000** | 0.075 |
| Kharapani path km | 31.2 | 25.2 |
| Kharapani offset from the line | — | 78 m |

**The "20 km" path agreement is withdrawn too.** v1 reported dam → Kharapani as
20.0 km against SANDRP's "20 km downstream", and called it an independent
consistency check on the geometry. On the routed channel that distance is
14.0 km (25.2 km from the detachment). The agreement was a coincidence of the
straight-line bridges. Straight-line detachment → Kharapani is already 21.7 km,
so no river path can be 20 km from the source; the published figure is either
approximate or measured from somewhere else.

## Scorecard, v1 configuration on the corrected channel

Same widths, same release, same frozen dial — only the profile is fixed.

| Quantity | v1 (broken profile) | v2 (corrected) | Observed |
|---|---|---|---|
| Kharapani arrival | 21.5 min (−23%) **PASS** | **6.8 min (−76%) FAIL** | 28.1 min |
| Pokhara arrival | 100.2 min (+18%) **PASS** | **28.2 min (−67%) FAIL** | ~85 min |
| Dam→Kharapani front speed | 15.6 m/s | **34.9 m/s** | ~12 m/s |
| Peak Q at Kharapani | 2,395 m³/s | **25,911 m³/s** | ~935 m³/s |
| Water fraction w | 0.92 | 0.81 | 0.47 (ρ = 1.88) |

The pre-registered failure mode, written in `research/seti-2012-anchors.md`
before v1 was run, was: *"the front must be SLOW — a model tuned on Langtang's
fast wave would fail here by running away."* On real terrain that is exactly
what happens. **The claim that the arrival-time physics ported to a third
event with zero recalibration does not survive.**

## The second conclusion reverses as well

v1's strongest-sounding result was that the model *independently requires* the
impounded lake, reproducing Kargel's and Hanisch et al.'s observational
conclusion from dynamics. On the corrected channel, with the cirque geometry
below and entrainment on:

| Impoundment | v1 Kharapani | v2 Kharapani |
|---|---|---|
| **0 Mm³ (avalanche alone)** | 65.2 min (+132%) FAIL | **28.5 min (+1%) PASS** |
| 1 Mm³ | 41.7 min (+48%) | 14.0 min (−50%) |
| 3 Mm³ | **21.5 min (−23%) PASS** | 9.2 min (−67%) |
| 6 Mm³ | 14.5 min (−48%) | 7.7 min (−73%) |

The sign of the inference flips: v1 said the model needs ~3 Mm³ of stored
water to arrive on time, v2 says stored water makes it far too fast and the
avalanche alone lands the clock. **Neither number should be cited.** What this
actually shows is that the arrival time here is dominated by how much water is
released at the top, and that our configuration of this event is not yet good
enough to resolve it.

Kargel's and Hanisch's conclusion about the Seti's water source stands on its
own observational evidence. It no longer has independent support from us.

## One geometry correction, and why it is not a rescue

The corrected profile exposed a second error that was present in v1 too: path
km 3.5–9.2 is the **Sabche Cirque**, a glacial amphitheatre kilometres across,
and v1 modelled it as a 25–60 m slot. DEM transects on the routed line find
ground within 60 m of the floor out to ±1,000–1,500 m through km 6–10, and
walls climbing 250–1,100 m within 600 m from km 12 down. Routing a 22 Mm³
avalanche through a 60 m channel there makes it a ~300 m deep dam-break wave.

Giving the cirque its mapped width (2,500 m, swept 1,500–3,500) is a map fact
and carries no timing information — but it was made **after** seeing the
failure, so nothing that follows is a blind result:

| | Kharapani | Pokhara | front speed | w at Kharapani |
|---|---|---|---|---|
| v1 config, corrected profile | 6.8 min (−76%) | 28.2 (−67%) | 34.9 m/s | 0.81 |
| + cirque width | 9.3 min (−67%) | 39.7 (−53%) | 25.4 m/s | 0.23 |
| + cirque + entrainment | 9.2 min (−67%) | 41.7 (−51%) | 25.9 m/s | 0.97 |
| + DEM-measured widths below the cirque | 19.5 min (−31%) **PASS** | never | **12.2 m/s** (obs ~12) | 0.98 |

The last row is interesting and must not be over-read: with DEM-measured
widths the mean front speed lands on the published ~12 m/s and Kharapani comes
inside the ±50% band. That is a post-hoc geometry choice made after seeing the
answer, on a 30 m DEM that reads the canyon rim rather than the slot. It is a
hypothesis for the rebuild, not a result.

## Entrainment at Seti: does not close the density gap, and says why

The reason this event was re-run at all is that it carries one of the two
quantitative targets for the new entrainment term (`model/core.py`): a
published flow density of 1.88 g/cm³, i.e. a water volume fraction w ≈ 0.47.

Both closures make it **worse**, not better: w ≈ 0.97 against v1's 0.92 and
the observed 0.47. The Takahashi closure erodes 0.9 Mm³ and deposits 23 Mm³;
the Frank shear closure erodes 6.9 and deposits 29.

The diagnosis is clean and worth more than the score. Takahashi's equilibrium
concentration at Kharapani's local bed slope (0.02) is **zero** — below the
0.03 threshold where a mature debris flow can be sustained at all. A
capacity-limited closure therefore says the flow at Kharapani should be clear
water. The measured density says it was 53% solids by volume. **The Seti flow
at Kharapani was not in equilibrium with its local slope; it was a surge
carrying what it had entrained kilometres upstream and in the act of dumping
it** — which is also why Kharapani is buried in the deposit. Neither the
settling cap (swept ×1/5 and off) nor the erodible-layer depth (1–10 m)
changes this: the closure strips the load in transit because it treats
deposition as settling through quiet water.

So the entrainment term does not fail at Seti for lack of an erosion law. It
fails because an equilibrium-transport closure cannot represent a surge, and
because the whole configuration of this event routes an avalanche that in
reality stopped in the cirque.

## What survives

Nothing from this event should be cited in support of the Trishuli work. The
portability claim after three events is now: **the arrival-time physics is
demonstrated on Chamoli 2021 (one fitted dof, out-of-sample speeds) and has no
second independent confirmation.** Seti has to be rebuilt before it can be
either evidence or a counterexample.

## Rebuild specification (the next task on this event)

1. **Start the model at the cirque outlet, not the detachment.** The avalanche
   fell into the cirque and stopped there; what ran the gorge was released
   water plus entrained debris. Routing the whole 22 Mm³ down the gorge is the
   error that drives everything above.
2. **Make the gorge-entering fraction an explicit scenario axis**, the way
   release volume and wetness are on the Trishuli. This is the Seti analogue
   of the Langtang "how much liquid passed the border" inference.
3. **Get the gorge cross-section right.** The 30 m DEM cannot see the slot;
   the width choice moves the front speed by 2×, which is larger than every
   other uncertainty here.
4. **Re-register the anchors before rerunning.** The existing anchors file is
   still untouched and still valid, but we have now seen this event's answer
   twice, so a rebuild cannot be called blind. Say so.

## Files

- `build_path.py` — v1 greedy stitch (kept; produced the withdrawn result)
- `build_path2.py` — v2 Dijkstra route over the waterway graph + floor-snapped
  elevations
- `profile_v1.csv` / `profile.csv` — the broken and corrected profiles
- `widths.py` → `widths.csv` — DEM-measured valley widths
- `run_seti.py` — the v2 hindcast, physics from `model/core.py`
- `seti_hindcast.png` — front trajectories, hydrographs, water fraction
- Anchors (pre-registered, unchanged): `research/seti-2012-anchors.md`
