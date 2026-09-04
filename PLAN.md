# Nepal Flood 2026 — Water Provenance & Wave Dynamics Model

**Project:** test where the water in the 26 Aug 2026 Langtang Lirung → Lende Khola → Trishuli
flood actually came from, and how the flood pulse evolved over ~168 km, with our own
physics-based model. Origin: Dave's hypothesis while watching Shawn Willsey's interview with
Dr Jeff Kargel — that the flood was mostly *cumulative river water* swept downstream by the
debris wave, not melted glacier ice.

Reference docs: `research/event-dossier.md` (event evidence), `research/science-review.md`
(literature), `calcs/energy_water_budget.py` (first-order budgets).

## 1. Hypotheses under test

- **H1 (provenance):** the flood water was dominated by river/channel-derived water
  (standing monsoon flow swept up + briefly impounded flow + pore water in saturated
  sediments), with frictional ice melt a minority term.
- **H2 (dispersion):** the wave "integrates" the river water as it advances — the fast front
  overruns slower channel water, incorporating it, but the collected mass cannot all travel
  at front speed, so the pulse stretches/broadens and the peak attenuates downstream.
- **H3 (side valleys / junctions):** tributary junctions and temporary blockages act as
  nonlinear storage-release elements (impound → overtop → re-sharpen the pulse), making the
  routing an integral cascade rather than simple advection.

## 2. Verdict from research so far (2 Sept 2026)

**H1 — substantially supported, with refinements.**
- Melt is *energy-limited*: a ~1,200 m initial fall gives ~12 kJ/kg vs ~27 kJ/kg needed to
  melt even a Chamoli-like 7.7% ice mass fraction at *perfect* heat transfer; realistic
  heat-to-ice partitions are 0.3–0.7 (tuned, not measured). Budget scenarios put melt at
  ~2–15 Mm³ vs ~15–30+ Mm³ of channel-derived water. FFD's official estimate of ~20 Mm³
  "excess" water is roughly 3–10× any defensible melt-only budget.
- Precedents where non-melt water dominated: Seti 2012 (Kargel's own conclusion), Melamchi
  2021, Huascarán 1970, Pierson & Scott's lahar-dilution sequence.
- **Fairness note:** Kargel's public position already names "melted avalanche ice, entrained
  sediment and the river itself" — he is not ignoring river water. What nobody has published
  is the *arithmetic* — the relative fractions. That's the gap this project fills.
- Chamoli 2021 (winter, 3,400 m fall, 26 km runout, freak 80:20 ratio) is the one documented
  case where melt dominated; our framing must show the balance of terms *flips* under monsoon
  + short fall + long runout, not that Shugar et al. were wrong.

**H2 — confirmed in the data, mechanism refined.**
- Observed: ~53 m/s average over the first 22 km (Kargel: 193 km/h; geopera superelevation:
  45–52 m/s at the border) → ~15 m/s to Betrawati → 5–7 m/s over the final 80 km. Pulse
  duration: minutes at the border → ~30-min rises at Galchhi/Malekhu → a broad afternoon peak
  at Devghat (16:00, 5,850 m³/s). Clear deceleration + broadening + attenuation.
- Mechanism refinement: in shallow-water dynamics deeper flow travels *faster*, so the front
  steepens into a bore while the **tail** stretches — broadening happens via the tail and
  peak decay, not the nose outrunning the body. Debris-flow bouldery-front resistance and
  solids deposition (most solids drop within tens of km) add to the deceleration. Dave's
  "integrator" picture is the right control-volume view: the front sweeps up channel water at
  rate ρA·(U_front − u_river) but the wave body lags, so length grows.

**H3 — real and documented, and contains the sharpest open dispute.**
- ICIMOD: the avalanche briefly dammed the monsoon-swollen Lhende, and the impoundment burst.
  Sinclair (Edinburgh): the 7-minute border arrival is too fast for damming to be primary.
  Geology Page: satellite evidence of a blockage ~20 km above Miteri Bridge with impounded
  water and release. Post-event barrier lakes (2 Mm³ + 0.5–1.5 Mm³) actually formed.
- **Our model can arbitrate:** simulate with/without a minutes-scale impoundment and test
  which matches the 08:44 CCTV arrival AND the downstream volumes.

## 3. Key observational constraints (the model must hit these)

| Constraint | Value | Quality |
|---|---|---|
| Collapse time | 08:37:10 NPT (seismic) | hard |
| Border arrival (22–23 km) | 08:44 CCTV (≈53 m/s avg) | hard |
| Betrawati (~50 km) | rising limb 09:20; peak ~10:30 [soft] | medium |
| Galchhi (~85 km) | +9 m in ~30 min, ~11:00–12:00 | good (gauge survived) |
| Malekhu (~95 km) | danger 11:26, +7 m | medium |
| Devghat (168 km) | peak 5,850 m³/s / 6.57 m at 16:00 | official (FFD) |
| Total "excess" water | ~20 Mm³ (FFD; method unpublished) | single-source |
| Flow heights in gorge | ~70 m median, trimlines 40–134 m | geopera, provisional |
| Velocity at Syabrubesi opening | collapse to ~11 m/s | geopera |
| Pre-event flows | border ~100–250 m³/s; Betrawati monsoon to ~1,000 m³/s | inferred/gauged |
| Source | 10–200 Mm³, ice fraction UNKNOWN, fall ~1,200 m (to channel ~2,400 m) | contested |

## 4. Model plan

### Phase A — Budget bookkeeping (v0 DONE, iterate)
`calcs/energy_water_budget.py`: independent bounds on each water source (melt = min(energy
cap, ice cap); standing channel water; inflow during passage; sediment pore water). Validated
against Chamoli (reproduces Shugar's ~5 Mm³, ice-limited, river ~8%).
**Next:** sensitivity sweep (tornado plot) over source volume, ice fraction, heat partition,
fall height, Q_river; publish the envelope "melt cannot exceed X under any defensible inputs."

### Phase B — The "snowplow integral" model (core of the project; Dave's H2 formalized)
**v1 DONE (2 Sept 2026).** `model/build_profile.py` (OSM-stitched channel, 199.3 km
scar→Devghat, border at km 22.0), `model/fetch_elevations.py` (499 pts, Mapzen DEM),
`model/snowplow.py` (front U=240·S^0.9+7 m/s fitted to the five clocks; peak celerity
0.73; per-source water bookkeeping with pro-rata losses). Results: snowplow scenario
peak 5,185 m³/s at Devghat vs 5,850 observed (11%), peak timing 445 vs 443 min;
melt-only fails ×2.4 on peak and delivers 4.2 vs ~20 Mm³ FFD. Distal wave ~74%
river-derived. Published: https://claude.ai/code/artifact/1fd064d2-fdc3-407e-b748-99b0e3cb3eb8
Remaining for v2: sensitivity sweep, Galchhi rate-of-rise check, real Galchhi
hydrograph when obtainable.
1D control-volume routing along the channel profile (Copernicus GLO-30 DEM longitudinal
profile, ~168 km):

- Front advances at U(x) (calibrate to the 5 timing constraints).
- Water uptake: dW/dx = A_channel(x) · (swept fraction) + q_lateral·(travel-time integrand)
  + melt(x) (energy-based, decaying with slope) + pore-water release from entrained bed.
- Wave length/duration grows as L(x) ≈ ∫(U_front − U_body)/U_body dx — the "not all at once"
  term; body speed from Manning/debris rheology.
- Losses: overbank storage, deposition (fix ~12 Mm³ solids in the gorge per geopera),
  stranding.
- Output per checkpoint: arrival time, peak Q, pulse duration, cumulative water by source.
- **Crucial diagnostic — gross vs net "excess":** redistributed river water shows up as a
  surge above concurrent baseflow at a gauge but nets toward zero over a long integration
  window (the emptied channel refills from baseflow after the wave). New water (melt, pore,
  impoundment drawdown) does not. Computing both tells us what FFD's "20 Mm³" can and cannot
  mean, and gives H1 a falsifiable observable per hypothesis:
  - melt-only: gross ≈ net ≈ few Mm³ → cannot reach 20 Mm³ → falsified if FFD is gross OR net
  - snowplow (H1): gross 20–40 Mm³, net ~10–15 Mm³ (pore + melt)
  - dam-burst-dominated: sharp secondary pulse signatures at gauges, timing tension at border
- Python, plain numpy; runs in seconds; every term inspectable. This is the deliverable that
  directly answers "was Dave right."

### Phase B2 — The equivalent-circuit (ladder network) model of pulse structure
Dave's framing (2 Sept): side valleys behave "in charging type ways where mass
builds and turns", producing the distinct pulses witnessed downstream. This maps
cleanly onto circuit theory — and, legitimizingly, onto textbook hydrology
(Muskingum routing IS a lumped storage element per reach; level-pool dam routing
IS a capacitor discharging through a widening orifice):

| River element | Circuit element |
|---|---|
| Stage / hydraulic head h | Voltage |
| Discharge Q | Current |
| Reach friction (Manning, head loss ∝ Q²) | Nonlinear series resistor |
| Flow momentum (Saint-Venant inertia term) | Series inductance |
| Valley storage dA/dh per km | Shunt capacitance — tiny in gorges, huge at valley openings (Syabrubesi: observed velocity collapse 50→11 m/s = big shunt C clipping the pulse) |
| Side valley + junction backwater | Shunt RC branch: charges as the surge passes (water/debris pushed UP the tributary), discharges after → tail stretch + secondary pulses |
| Temporary debris dam | Capacitor behind a rising resistance that fails at threshold — SCR / spark-gap breakdown; a chain of them = relaxation-oscillator cascade (Seti 2012's ~27 surges) |
| Baseflow & tributaries | Distributed current sources |
| Bore steepening at the front | Nonlinear transmission line (amplitude-dependent propagation speed — NLTLs are literally used for pulse sharpening) |

Build: a ladder network of ~50 reach elements (R-L series, C shunt from valley
width off the DEM/Sentinel-2), side-valley RC branches at mapped tributary
junctions (Langtang Khola, Chilime, Salankhu, Tadi, ...), breach elements where
damming is evidenced. Solve as ODE system (plain scipy). Objective: reproduce
multi-pulse structure and map each downstream pulse back to the junction or dam
that made it.

**v0 BUILT (2 Sept, `model/ladder.py`):** 90-node diffusive-wave ladder, border→Devghat,
side-valley weir/reservoir branches, erodible-crest breach element. Timing calibrates
well (Galchhi 10:59 vs ~11:00 obs; Malekhu 11:23 vs 11:26; Devghat 15:43 vs 16:00) and
all three signatures demonstrated: bare-line attenuation/broadening; side-valley
peak-clipping + tail-feeding; breach double-pulse (visible at mid-stations, smeared by
Devghat). Known limitation, itself informative: the RC-only (inertia-free) line
under-predicts the distal peak ~2× — the real river kept its "inductance" (bore/momentum,
hyperconcentration). v1 needs: Sentinel-2-mapped side-valley areas, inertial term or
Muskingum-Cunge matching, Gandak validation data.

**v2 (2 Sept, evening): INDUCTOR INSTALLED.** simulate(inertial=True) default —
local-inertia Saint-Venant (Bates et al. 2010), semi-implicit friction, Froude cap
2.0; RC-only kept as inertial=False (page has a comparison button). Results:
mid-reach peaks +14–17%, fronts earlier/steeper, out-of-sample Galchhi rise
5.2→5.9 m (6.7 at 1-km grid) — all in the predicted direction. Distal Devghat peak
robust at ~2,500–2,900 under resolution & width sensitivities ⇒ remaining gap is
lower-reach storage geometry AND likely the observation: FFD volume/duration
arithmetic implies the Devghat gauge base is ~2,950 m³/s (Narayani below Kali
Gandaki confluence, probably DHM stn 450) ⇒ observed EXCESS peak ~2,900 not
~4,350 ⇒ ladder ~2× low, snowplow ~1.5× high — truth between the models.
**TASK: confirm the Devghat station (number, river, rating curve, late-Aug base)
with DHM, then re-score the §05 scenario table on excess-peak basis.**

**Front-speed refinement ideas (3 Sept):** (1) add a relaxation/memory term to the
snowplow front law — dU/dx = (U_eq(S) − U)/λ with λ ~ a few km — so the front can
carry gorge momentum past the border (matches geopera 45–52 there) while still
averaging ~21 m/s to Betrawati; (2) audit the observations themselves: Kargel's
193 km/h average hinges on the 08:44 CCTV clock (a ±2 min clock error moves the
average by ±10 m/s) and superelevation speeds are biased high by splash/runup and
bend-radius uncertainty; (3) the Syabrubesi 3.8 m rise at 08:50 (43 m/s implied
border→Syabrubesi) vs geopera's 11 m/s at the valley opening may both be right if
the stage rise was RIVER WATER PUSHED AHEAD of the slower debris front — the
snowplow picture literally predicts a water wave outrunning the debris body.

**v3 (3 Sept): JUNCTION STEP (Dave's hypothesis).** The border is a T-junction:
Lhende dead-ends into the main stem, Gyirong Port sat opposite the mouth. Added:
(a) Kyirong upstream arm as a low-sill capacitor branch at the injection node —
it charges 5.5 m, the largest side-branch response; (b) junction minor losses
K·v²/2g (K=3 border, 1–1.5 others — uncalibrated estimates). Effects: Betrawati
peak 12,400→8,100, Malekhu danger-crossing 11:35 vs obs 11:40; Galchhi rise test
falls to 4.5 m (momentum/junction-loss partition needs calibration). Topology map
built from OSM into the page (fig-map; export_map.py computes mouth-based
junctions — Kali Gandaki joins at km 199.2 = exactly the Devghat gauge,
supporting the Narayani-gauge reading). CAMERA HYPOTHESIS (Dave's): the 08:44
CCTV likely recorded the junction impact + up-valley surge, not a down-valley
front — would reconcile 45–52 m/s "at the border" with ~21 m/s beyond it.
**TASKS: geolocate border cameras + feature-track frames; refine SIDE branch
positions & baseflow anchors to mouth-based junction km (Mahesh ~102, Budhi
Gandaki ~132, Marsyangdi ~167); calibrate K values once Galchhi hydrograph
obtained; refresh notebook Section 3 for v3.**

**v4 experiment (3 Sept): REAL CROSS-SECTIONS — a measured negative result.**
Built model/transects.py: 40 DEM transects (41 pts × 30 m each) along the path →
stage-storage tables W(η), A(η) in data/transects.json. The nonlinearity is real
and dramatic (Mugling gorge km 150: 60 m wide at 10 m stage; Betrawati basin
km 75: 270→780 m), BUT running the ladder on them over-damps everything (gorge
max stage 16 m vs geopera trimlines ~70; Galchhi 1 h late): the 30 m DEM cannot
resolve the incised inner slot canyon, so low-stage storage is far too fat.
Ladder now has LADDER_SECTIONS=rect (calibrated default, wide-channel R=h,
matches published charts) vs =dem (experiment, proper R=A/P). The stage-vs-
trimline comparison is a NEW validation axis and the proof of the resolution
limit. **Unlock paths: (a) HMA 8 m DEM tiles (NSIDC) for gorge transects;
(b) footage/photo-derived slot widths at 5-10 gorge stations (structures as
scale bars) — then re-run dem mode and calibrate K_JUNC + V_PULSE against
Galchhi rise + trimlines.**

### Phase B3 — Unified scar-to-Devghat model with the dilution dial (v1, 3 Sept late)

**Built: `model/unified.py`** — one momentum equation scar→Devghat (499 nodes,
400 m), replacing the kinematic-law/ladder split. Dial defined ONCE for both
events: μ = μ_dry + (μ_wet−μ_dry)·min(w/W_SAT,1) with w = water volume
fraction, advected & volumetrically mixed (three tracers: total, water,
release-origin water, release solids); water arrives by MELT at Chamoli
(thermal lag), by RIVER ENTRAINMENT at Trishuli — same dial, different tap.
W_SAT=0.25 (pore saturation). Pure river (w=1) = the μ=0 Manning ladder
exactly. Release = triangular inflow over ~3 min (seismic duration), scenario
axes: V (10/30/60), w0 (0.1–0.4), μ_dry (Scheidegger rock 0.29–0.34 vs
Schneider ice-avalanche 0.17). Stranding term (slow+granular → bed) gives
emergent deposition vs geopera's ~12 Mm³.

**ROBUST FINDING (survived five numerics iterations unchanged): the 08:44
border clock discriminates COMPOSITION.** Ice-rich/wet scenarios arrive
08:43–08:51; rock scenarios 09:02–09:26, at every release volume — a dry
rock avalanche cannot make the border in 7 min under any defensible size
(regime > size, the Chamoli lesson again, now inverted). Wet-slurry runs
also hit Syabrubesi 08:49–08:53 (obs 08:50) and Betrawati 09:03–09:14 (obs
09:20). Upper-reach character correct: ~85 m bore (trimlines 40–134, med
~70), velocity collapse at the Syabrubesi width opening, mean front speed
41–42 m/s (clock implies ~53).

**Routing engine validated:** ladder's 30 Mm³/45-min water pulse injected at
the border through the unified engine gives Betrawati/Galchhi/Devghat
19,651/6,324/2,372 with Devghat peak at 16:12 (ladder 2,443@16:30, obs
5,850 total/~2,900 excess @16:00).

**DISTAL WATER-BUDGET INFERENCE (H1/H3 from dynamics):** no granular scenario
(V≤30, w0≤0.2) routes enough liquid past the border — release solids strand
below Syabrubesi (μ>slope), melt is energy-capped at ~1–3 Mm³ (the H1
arithmetic, confirmed dynamically) — yet the distal record needs ~20–30 Mm³
of liquid through/at the border. Independent dynamical support for wet/icy
source and/or impoundment release (ICIMOD H3).

**Numerical lessons (each a real closure issue):** (1) the Bates local-inertia
scheme confines a supercritical dam-break front into a non-decaying one-cell
soliton — fixed with von-Neumann-style curvature-triggered, CFL-scaled shock
viscosity; (2) v0 side-valley reservoirs (plan area × unbounded head) swallow
tens of Mm³ under a deep bore — capped at 8 m fill pending Sentinel-2
stage-volume curves; (3) **rheology must switch from stress-coefficient to
stress**: a Coulomb μ for the diluted slurry parks deep waves on the lower
river (audit showed 31 Mm³ parked km 68–108 damming the baseflow); replaced
with Bingham τ_y(w)/(ρgh) above W_SAT (deep lahars run, thin sheets lock —
Pierson & Scott). Chamoli untouched by all three (w<W_SAT there).

**v1 OPEN → largely closed by v2 (3 Sept, night): CONVECTIVE MOMENTUM
INSTALLED.** d(uQ)/dx upwind added to the momentum equation — the term whose
omission (Bates local-inertia) caused both the soliton and the released-wall
artifacts; with it the rarefaction physics works and the wall/overshoot
artifacts vanish. Routing regression improves too (Betrawati 11,275 less
spiky; Devghat 2,544 @ 15:40 vs obs 16:00). v2 scenario table:
- **Scenario C (ice-rich V=30): border arrival −2% (6.8 vs 7 min), mean
  front speed 54 m/s vs the clock's 53.** Composition discrimination
  unchanged (rock scenarios 08:55–09:07, never on time).
- **Scenario F (wet slurry V=60): all upper clocks (08:42/08:47/09:02) AND
  Galchhi 30-min rise 10.2 m vs observed ~9** — first scenario to land a
  distal observable; the border must pass a large liquid volume.
- **PROVENANCE (H1, from dynamics): water at Devghat is ~100% river-derived
  in every scenario** — release solids strand/lag; even stronger than the
  snowplow's 74% (single-phase caveat: real fine sediment rode through, so
  frame as "the distal WATER was overwhelmingly the river's own").
- **NEW TENSION = the mixed-mass inference:** timing wants the flow wet
  (E/F strand ~0 Mm³), the geopera ~12 Mm³ deposit wants it granular (D
  strands 13.6, C+w0=0.10 strands 11.9). A rocky core that strands in the
  gorge + a watery flood that continues — two components one single-phase
  model can only have one at a time. This is route (b)/(c) of the
  lubrication question, stated as a falsifiable structure.
Remaining v2 gaps: scenario C's granular body crawls km 22–68 (Syabru/
Betrawati +100% for C; wet scenarios don't); Devghat excess peak ~650 vs
~2,900 (inherits the ladder's known lower-reach storage question + argues
V≥60 through the border); impoundment/breach scenario still to add; τ_y,
W_SAT, μ_dry(ice) literature pass pending.

### Phase B4 — ENTRAINMENT INSTALLED (3 Sept, night) — `model/ENTRAINMENT.md`

The gap flagged as "the one big open gap" is closed as a *term*; what it
revealed is bigger than the term. Engine refactored first: `model/core.py`
now holds the one Voellmy–Saint-Venant step() and `arrival_fn`, shared by
unified.py and run_seti.py (the copy-paste debt that made the arrival bug a
three-file fix). **The published Trishuli scenario table reproduces
bit-identically after the refactor** — regression checked, not asserted.

Two closures, all constants from the literature, nothing fitted:
Takahashi capacity (c_eq from bed slope + friction angle; δ_e = 0.0007,
δ_d = 0.05) and Frank et al. (2015) shear (z_pot = K_τ(τ_b − τ_c)). Saturated
bed (entrains c* solids + (1−c*) pore water), finite erodible layer H_ERODE
(the one free input, swept 1–10 m), settling cap on deposition. Release
tracers untouched by entrainment so H1 stays clean.

1. **EROSION LANDS. 3.8 Mm³ modelled vs geopera's 3.2 Mm³ measured**, in the
   same reaches they mapped, robust across closure (3.8/3.9), scenario
   (C 3.8 / F 3.8), H_ERODE (3.0–4.4) and W_SETTLE (2.5–3.8). First
   quantitative out-of-sample hit on the sediment side.
2. **DEPOSITION IS 8–40× TOO LARGE — and that is an EVENT-SIZE result.**
   Scenario C dumps 42.5 Mm³ of bulk fill in the corridor; the stereo DEM saw
   0.9 (their model ~5). Since the solids demonstrably do not reach Devghat,
   they must be in the corridor, and the DEM would have seen them.
   ⇒ **the release delivered ≲3–5 Mm³ of SOLIDS to the channel** (V_rel ≲ 6 Mm³
   at w0 = 0.15). That matches the EGU preliminary (0.5–10) and geopera's ~4
   Mm³ valley change, sits 1–2 orders below the 100–200 Mm³ figures in
   circulation, and **contradicts our own routing, which needs V = 30–60
   through the border.** Now an arithmetic contradiction, not a qualitative
   tension. **LEADING RESOLUTION (4 Sept): THE MASS WAS MOSTLY ICE.** Ice is
   dynamically a SOLID — it supplies the depth and momentum the front speed
   needs — but geomorphically TEMPORARY, so it never appears in a DEM
   difference taken days later. V_rel = 30 Mm³ at ~85% ice leaves ~4.5 Mm³ of
   persistent rock, which is geopera's number. Third independent arrival at
   the composition finding. **NEW FALSIFIABLE PREDICTION: an ice-rich deposit
   must go on LOSING volume for weeks as buried ice melts out** — checkable
   against repeat stereo/DEM archives, and it discriminates ice deposit from
   rock deposit directly. Remaining alternative: geopera's mapped 45% missed
   the deposit.
   **WITHDRAWN 4 Sept — "(b) the border volume is impounded river water".**
   The arithmetic fails: blocking the Lhende (~60 m³/s) or the whole main stem
   (~150 m³/s) stores 0.02–0.6 Mm³ over any duration the 08:44 clock allows;
   20 Mm³ would need the river blocked for **37 hours**. An in-event
   impoundment RE-TIMES a pulse, it cannot supply one. H1's water is the
   **46.9 Mm³ standing in the channel** at any instant — no dam required, and
   that was always the snowplow's claim.
3. **THE DISTAL WAVE DOES NOT SURVIVE PROPER DEPOSITION — a real regression.**
   Galchhi 30-min rise: C 1.6 → 0.1 m; F 10.2 → 1.5 m (obs ~9). Scenario F was
   the only run that had ever landed a distal observable and entrainment takes
   it away. Mechanism: single-phase. You cannot deposit 25 Mm³ of solids in the
   upper corridor and still deliver a 9 m rise at Galchhi with one phase.
   **The single-phase assumption, not the erosion law, is now the binding
   constraint.**
4. Provenance UNCHANGED with entrainment on: still ~100% river water at
   Devghat. The H1 headline survives the addition of the missing term.

**NEXT BUILD (supersedes the old "entrainment" task):** split the solid load
into a coarse fraction obeying the capacity closure and a fine/wash fraction
that rides with the water — one physical split, addresses (3) and Seti's
density together. Then: Rouse-modulated settling (W_SETTLE from shear velocity,
not a constant); resolve the event-size contradiction with a FULL-corridor DEM
difference rather than 45%.

Bug found and fixed en route: the 0.05 m numerical wet-film depth floor
manufactured volume in draining cells and, because the water tracer was not
raised with it, counted that volume as SOLID into the stranding ledger
(53 Mm³ stranded from a 19.8 Mm³ release on a wide basin). Now added as water.
No published result changes.

### Phase F, test 2 — SETI 2012 HINDCAST **WITHDRAWN** (3 Sept, night)

**The v1 "PASSED" result below is retracted.** Building the entrainment term
meant scrutinising bed slopes, which exposed the profile it ran on:
`build_path.py`'s greedy stitch bridged straight lines across the Sabche
Cirque rim, the sampled elevations oscillated by 1,500 m, and the standard
monotone-descent clamp then held **31 of 54 km at a constant 1,020 m — the
entire runout, at zero gradient.** The pass was bought by terrain that did not
exist. Corrected with a Dijkstra route over the OSM waterway graph
(`build_path2.py`; 23% clamped, longest flat 3.2 km, gorge slope 0.075).

- **Timing FAILS: Kharapani 6.8 min vs 28.1 observed (−76%), Pokhara −67%,
  front 34.9 m/s vs ~12, peak 25,911 vs ~935 m³/s.** The pre-registered
  failure mode ("a model tuned on Langtang's fast wave would fail here by
  running away") is exactly what happens on real terrain.
- **The impoundment inference REVERSES:** 0 Mm³ now gives +1% (v1: +132% and
  never reaching Pokhara); 3 Mm³ gives −67% (v1: −23% PASS). Neither number
  should be cited. Kargel's/Hanisch's conclusion stands on its own evidence
  and no longer has independent support from us.
- **The "20.0 km vs published 20 km" path agreement is withdrawn** — the
  routed distance is 14.0 km; straight-line source→Kharapani is already
  21.7 km so no river path can be 20 km from the source.
- Second error present in v1 too: path km 3.5–9.2 is the **Sabche Cirque**, a
  glacial amphitheatre kilometres wide, modelled as a 25–60 m slot. Widening
  it to its mapped width (DEM transects: ground within 60 m of the floor out
  to ±1,000–1,500 m) is a map fact but was made after seeing the failure, so
  it is declared post-hoc, not blind.
- Entrainment does NOT close the density gap here (w 0.97 vs 0.47 observed)
  and the reason is diagnostic: Takahashi's c_eq at Kharapani's slope (0.02)
  is **zero**, so a capacity closure predicts clear water where the
  measurement says 53% solids. The Seti surge was ~20× over local capacity —
  which an equilibrium closure cannot express.

**Portability claim after three events, restated honestly: demonstrated on
Chamoli 2021 (one fitted dof, out-of-sample speeds); no second independent
confirmation.** Rebuild spec in `hindcast/seti/RESULTS.md` — start at the
cirque outlet, make the gorge-entering fraction a scenario axis, fix the slot
width, and re-register before rerunning.

**Process lesson, now a standing check:** every path build must report longest
flat run and largest raw upward step. Trishuli (48% clamped, mean 9 m, longest
6 km) and Chamoli (11%, longest 0.8 km) are fine; only Seti had a bridge big
enough to poison the clamp. Both were verified after the bug was found.

<details><summary>Superseded — the withdrawn v1 Seti entry (3 Sept, night)</summary>

`hindcast/seti/` (anchors pre-registered in research/seti-2012-anchors.md,
written before the run; all dial constants frozen at Trishuli/Chamoli values).
The intermediate regime: rock/ice avalanche into a gorge holding a lake
impounded behind a rockfall dam for weeks (Kargel; Hanisch et al. 2013).
- **Kharapani 21.5 min vs 28.1 observed (−23%) PASS; Pokhara 100 vs ~85 min
  (+18%) PASS.** Pre-registered failure mode (running away like Langtang's
  fast wave) did NOT occur: front 15.6 m/s vs observed ~12.
- **The model REQUIRES the impoundment.** Sweeping stored volume alone:
  0 Mm³ → 65 min (+132%) and never reaches Pokhara; 1 → 42; **3 → 21.5 PASS**;
  6 → 14.5. A dry-ish avalanche into a pre-monsoon trickle cannot make the
  clock. Kargel's/Hanisch's observational conclusion, recovered from dynamics.
- Path consistency bonus: independent OSM stitch puts Kharapani **20.0 km**
  below the gorge head vs published "20 km downstream" (0.1 km agreement).
- **FAILS on sediment: w = 0.92 modeled vs 0.47 observed (ρ = 1.88 g/cm³).**
  Same deficiency as Langtang (~100% river water at Devghat) and same as
  geopera's net-erosional corridor: **THE MODEL HAS NO ENTRAINMENT TERM.**
  Two quantitative targets now exist for building one (Seti ρ=1.88;
  Langtang erosion 3.2 vs deposition 0.9 Mm³). This is the next build.
- Bug found & fixed: `arrival()` used np.interp against a front array with a
  flat tail → returned mid-plateau (Pokhara 180 not 100 min). Fixed in
  run_seti.py, unified.py, run_voellmy.py. Blast radius checked: Chamoli's
  Tapovan anchor and Trishuli's peak-based figures unaffected.

</details>

### ENSEMBLE FALSIFICATION (4 Sept) — `calcs/ensemble.py`

Rejection sampling over the five contested inputs (V_rel log-uniform
**1–200 Mm³**, w0, mu_dry, Manning scale, erodible depth), Latin hypercube,
scored against the upper-corridor observables. Two runs:

**Run 1 (100 samples, 4 observables — NO deposition constraint): 4 matches.**
V_rel median **31.3 Mm³** (range 25.9–33.2), w0 median 0.49, mu_dry 0.20.
Tight, and against Kargel 50–200 / ICIMOD 100–200 / EGU 0.5–10 that looked
like a real envelope. **Two flaws:** w0 was PINNED against its 0.50 prior
ceiling (0.38–0.50) — a truncated prior, not a converged posterior — and the
deposition constraint that started the whole event-size argument was simply
absent.

**Run 2 (150 samples, w0 prior widened to 0.85, bulk deposition ≤ 5 Mm³ added
as an INEQUALITY — a DEM difference bounds deposition from above, it does not
target it): ZERO matches.**

| observable | met by |
|---|---|
| border arrival 7.0 min ±30% | 45/150 |
| Syabrubesi 13 min ±50% | 54/150 |
| peak speed at border 48.5 m/s ±35% | 60/150 |
| erosion km 0–68 3.2 Mm³ ±60% | 87/150 |
| bulk deposition ≤ 5 Mm³ | 50/150 |

Each observable is individually reachable. **The conflict is one specific
pair, and it is total:**

| pair | runs satisfying both |
|---|---|
| border arrival + deposition | **0** |
| Syabrubesi arrival + deposition | **0** |
| border speed + deposition | 10 |
| erosion + deposition | 30 |
| every other pair | 16–41 |

**No combination of the contested inputs can make the upper-corridor CLOCKS
and keep deposition inside what the corridor can hold.** Note it is arrival
TIME that conflicts, not arrival SPEED — you can have 50 m/s at the border
with low deposition; you cannot have it *on time*. To arrive on time the
single-phase model needs a deep wave, a deep wave needs volume, and volume
deposits.

**This is a falsification of the MODEL FORM, not a failure to tune**, and it
is the strongest statement the project has made: the single-phase assumption
is refuted by a 150-sample search of a 5-D space, not merely suspected. It
also retires the run-1 "V ≈ 31 Mm³" number — do not cite it.

**The two-phase split is therefore no longer optional.** A coarse fraction
that carries momentum and strands, plus a fine/wash fraction that rides
through, can in principle satisfy both; one phase provably cannot.

### ENERGY AUDIT (4 Sept) — Dave's challenge, and what it found

Dave asked whether reaching for an exotic water source meant something was
genuinely unexplained — an energy mismatch, "a meteor or something else".
**Answer: no energy deficit, decisively.** Even the smallest defensible
release (5 Mm³) falling 1,200 m delivers 1.2e14 J against ~2.5e13 J of kinetic
energy in a 20 Mm³ wave at 50 m/s — ~5× more than needed. And the sliding-
block energy line v = √(2g(drop − μL)), which contains **no volume term**,
permits 84–96 m/s in the upper gorge at literature μ, against an observed
53 m/s mean. Gravity supplies the speed at any release size.

**But the challenge was still right, and here is the real soft spot.** The
model's border arrival is strongly volume-dependent (V=5 → 13.3 min, 10 →
10.3, 30 → 6.8, 60 → 5.5) which the energy line says should not happen.
Three candidate artifacts tested (`calcs/front_speed_closure.py`), **all
eliminated**:
- Manning drag on a granular flow: n × 0.35 moves V=5 only 13.3 → 12.7 min.
- The Froude cap: FR_MAX 2 → 8 gives 13.3 → 12.2, though peak material speed
  rises 33 → 53.6 m/s. **Material speed ≠ front speed.**
- The +0.5 m front threshold: probing km 22 directly, +0.1 m arrives at
  12.9 min and +5 m never (V=5). The front is sharp; no thin fast precursor.

So it is genuine structure: **depth-averaged shallow water ties front speed to
√(gh), so the only way our model reaches 53 m/s is by being deep, which means
being big. A sliding granular block has no such coupling.** The inference
"the border must pass V ≥ 30–60 Mm³" is therefore CONDITIONAL on
spreading-fluid behaviour over the whole 22 km, and must be labelled as such.
Treating it as a hard constraint is what sent me looking for an impoundment.

**AND THE CONTRADICTION LARGELY DISSOLVES when stated as a volume budget
instead.** geopera's trimlines (40–134 m, median ~70, gorge ~50 m wide) are an
observation independent of our model: a 70 m wave over a 2–5 km surge is
7–20 Mm³ *in the gorge at any instant*. That is release + swept channel water
(0.53 Mm³ above the border) + entrained bed (2.57 Mm³) ⇒ **the release need
only supply 4–17 Mm³**, against the entrainment ledger's ≲6 Mm³ cap at
w0 = 0.15. The gap goes from an order of magnitude to about 2×, and a modest
ice fraction closes the rest. **Next: re-derive the routing's V requirement as
a gorge volume budget rather than a free parameter.**

### MAP FIGURES (4 Sept) — overview + upper-corridor detail

`report/report.src.html`'s map code is now ONE `drawCorridorMap(sel, opt)`
called twice, rather than a second copy (same lesson as `model/core.py`).
Every layer clips to the frame's own lat/lon box, so a reach can be enlarged
without editing the drawing code.

- **fig-map (overview, 199 km, 5.9 px/km)** gains the Nepal–China boundary
  (OSM admin_level=2, `data/osm_border.json`), the 2015 Langtang village site,
  Langtang Lirung's summit, and a dashed locator box for the panel below.
- **fig-map-upper (km 0–42, 25.7 px/km = 4.4×)** carries what the overview
  cannot: the observed CLOCK at each place merged into its marker (08:37 scar
  / 08:44 Gyirong CCTV / 08:50 Syabrubesi stage), geopera's superelevation
  speeds along the reach (37 → 45–52 → ~50 → 11 m/s at the valley opening),
  and each plant's loss (Rasuwagadhi 49 missing, Langtang Khola HP 42 missing
  — the latter was missing from the cascade list entirely and is now added).
- **Extent chosen for SCALE, and the reasoning is in the code:** km 0–68 gives
  only 2.2× because the corridor swings 48 km north–south by Betrawati and the
  frame becomes height-bound; km 0–42 gives 4.4×. Betrawati's 09:20 / 43-min
  anchor moves to the caption.
- **The panel makes the snowplow visible in the observations alone:**
  Syabrubesi's gauge rose 3.8 m at 08:50 but inundation is reconstructed at
  09:10–09:25, and the superelevation speed collapses 50 → 11 m/s at exactly
  that opening. A water wave ~25 min ahead of the debris body is what H2
  predicts, so the two clocks are evidence, not a discrepancy.
- Label placement was **simulated in Python against the JS engine's own
  geometry** before publishing: 24 labels on the overview, 19 on the panel,
  **0 dropped** on either.

### IMAGERY MEMO (3 Sept) — research/imagery-composition-memo.md
Open-evidence audit of the composition question. **Route (a) ice-rich source:
SUPPORTED qualitatively** — Shugar, GFZ, Steiner, Azam/ICIMOD and the Chinese
drone footage (a *white* stream leading the brown dust cloud) all describe
bedrock failure that carried a hanging glacier; Shirzaei's InSAR treats it as
a coupled "glacier–rock system". No ice fraction published by anyone.
**Route (b) glacier excavation: SILENT** — no post-event measurement of the
glacier below the scar exists; it is not even named in coverage (it is NOT the
SW-side Lirung Glacier); upper runout was cloud-covered in Sentinel-2 and
outside geopera's stereo footprint. Our physics inference is ahead of the
imagery here. **Route (c): partially supported** (geopera's calibrated model:
"this flood moved like water, not like a viscous debris slurry"; staged
seismic failure "consistent with a mass coming apart wet").
**CRITICAL CORRECTION APPLIED:** geopera RETRACTED the 12 Mm³ deposition wedge
on 1 Sept ("it was noise"); the stereo truth is 0.9 Mm³ deposition against
3.2 Mm³ EROSION in the mapped 45%, calibrated model ~5 Mm³. unified.py's
scoring target was corrected. **This dissolves the v2 "mixed-mass tension"**:
against the real target the wet scenarios (E/F strand ~0) are consistent and
the rock scenarios (D strands 13.6 Mm³) are doubly falsified — timing AND
deposition now point the same way.
Also flagged: the 100–200 Mm³ source estimates sit 1–2 orders above both the
EGU preliminary (0.5–10) and measured valley change (~4 Mm³); our routing
works at V=30–60. Nobody has confronted that discrepancy in print.

**Blocking data need:** an observed multi-pulse hydrograph. Candidates: full
Galchhi record (DHM), Devghat record (FFD), and India CWC gauges on the Gandak —
Triveni / Valmikinagar barrage at the border would have operational gate records.
Without one of these, B2 predicts pulse structure but can't be validated.

### Phase C — Scenario discrimination
Run melt-slug-only / snowplow-only / hybrid / hybrid+impoundment through Phase B and score
against §3. Include Sinclair's timing test: max impoundment duration consistent with 08:44.

### Phase D — Optional heavyweight models
- r.avaflow v4 on the upper 30 km (avalanche → debris flow transition; Chamoli inputs are
  published as a template) — desktop, 10–20 m cells.
- HEC-RAS 2D for the distal 50–168 km with the Phase C winning hydrograph.
Only if Phases B–C leave questions open or we want pretty animations.

**Publication strategy (3 Sept, after Dave's "this is my industry"):** the circuit
MATH is not novel (diffusive wave = RC cable is Hayami 1951; hydraulic-electric
analog flood routers were built in the 1950s-60s) — never claim it as new physics.
What IS potentially publishable: (a) the water-provenance budget + gauge-base
reinterpretation + junction step response for THIS event (EarthArXiv preprint /
NHESS brief communication once DHM data lands); (b) **the industry piece** — the
Trishuli cascade seen as a transmission-line problem, for a hydropower audience
(Hydro Review / IHA / energy-sector venue): cascade siting at confluences,
automated tripwires vs alert latency, and the SCADA-historian data call. Dave is
the right author for (b); it is the version with the clearest safety value.
**NEW DATA TASK: plant records** — headworks stage sensors, gate logs, SCADA
historians at the 13 projects likely hold the only high-frequency upper-reach
hydrographs (survivors: Chilime, Trishuli HPS, Devighat; even drowned plants'
servers may have replicated data to owners' offices - NEA, IPPs, Chinese EPC).

### Phase F — Portability: the hindcast test & timing-budget atlas (Dave, 3 Sept)
**CHAMOLI HINDCAST DONE (3 Sept, hindcast/chamoli/):** zero-recalibration verdict —
TIMING FAILS (Tapovan 11 min modeled vs 34–37 observed, 3.2× fast, outside ±50%)
but all three video-point SPEEDS pass within ±40%, and the water budget ports
exactly (calcs scenario 0). Diagnosis (predicted in advance): the steep-slope
branch of U=300·S^0.82+4 describes a watery monsoon flood front; Chamoli's
80%-solids granular avalanche ran friction-limited (~20–25 m/s max, stop-and-go)
— a single-valued U(S) cannot match both its point speeds and its arrival time.
**Design decision: add a flow-regime flag** (debris-regime cap on steep reaches,
keyed to water availability: winter/low-flow → granular cap; monsoon → water
law). DO NOT calibrate the cap on Chamoli then claim Chamoli passes (circular):
set it from debris-flow literature and validate on Seti 2012 / Sikkim 2023 next.
**Second design gap (Dave, 3 Sept): the law has NO EVENT-SIZE input** — Trishuli's
scale/wetness are implicit in the constants. Portable form needs size explicit:
either route with the ladder (input hydrograph = event size, already size-aware)
or add a (Q/Q_ref)^c depth factor to the snowplow law. Note the instructive
counterpoint: Chamoli's initiating mass (27 Mm³) ≳ Langtang's initial detachment
(~1–10 Mm³ per early-Sept estimates) yet ran ~3× slower — at these scales
water/regime dominates size as the front-speed control.

**RESOLVED DESIGN (Dave's first-principles push, 3 Sept): the Voellmy–Saint-Venant
unification.** Energy-line check: Chamoli H/L = 0.16 (Shugar) = our path's
3,711 m / 24 km exactly — the flow died where its energy line met the terrain;
mgh sets runout. Local speed rides terminal velocity: **v = √(ξ·h·(S − μ))** —
μ = regime dial (dry granular ~0.15–0.2, water ~0; continuous in water
availability), h = event size (the missing input), ξ→g/n²·h^⅓ in the water limit
so Voellmy COLLAPSES TO MANNING = our ladder. The empirical U=300·S^0.82+4 is a
fitted shadow with h, μ frozen at Trishuli values. Build: add Coulomb term
(−μ·g·A·sign Q) to the ladder momentum equation → Voellmy–Saint-Venant hybrid;
re-run Chamoli as equivalent fluid with LITERATURE μ (0.15–0.2, not tuned); if
Tapovan timing lands, Seti 2012 blind (impounded water = intermediate regime).
Junction K·v²/2g loss and the melt budget are entries in the same energy ledger.
Error direction is "early" — conservative for triggering, wrong for tier maps.
Path note: OSM had Ronti Gad ("Raunthi Gadhera"); published Chamoli distance
triplet is internally inconsistent — our self-consistent path-km in RESULTS.md.

**BUILT & TESTED (3 Sept, late): Voellmy–Saint-Venant + thermal-lag melt closes
Chamoli's timing.** ladder.py v5 has the Coulomb term (mu=0 bit-identical to
published Trishuli — regression checked). hindcast/chamoli/run_voellmy.py routes
the 26.9 Mm³ release block dynamically; failure anatomy: constant μ fails BOTH
ways (deep flow outruns Coulomb on steeps; flat basin at S≈0.015 is terminal);
static melt dial μ(x) 0.30→0.02 (Scheidegger dry endpoint at 26.9 Mm³; melt
linear in fall, complete at 3,400 m per calcs scenario 0) fixes runout + 2/3
speeds but crosses the basin in 3 min; valley widths (basin ~300 m) bracket obs
{12 min, 180 min, never}. Closing physics: THERMAL LAG — melt state advected
with the mass, relaxing over τ ~ d²/(π²κ) (a-priori 2–60 min for 4–20 cm ice).
τ = the ONE fitted dof; arrival monotone in τ selects τ≈5 min ⇒ d≈6 cm.
Result: Tapovan 37.4 vs 34–37 min (+5% PASS, robust 28–52 across all
sensitivities), mean speed 10.3 vs ~11 m/s, km 16 flow speed passes; near-
**[4 Sept — RESTATED after a stale-artifact fix.** voellmy_curves.json had been
committed *before* the arrival() plateau fix, so the published report showed
37.4 min / 10.3 m/s. Regenerated and the report rebuilt: **Tapovan 36.3 min,
now INSIDE the 34–37 window rather than beside it; mean speed 10.6 m/s.**
Not all of it improved — the km 18→22 basin crossing fell from ~21 min to
**13.0 min against Rana et al.'s ~27**, i.e. that anchor got worse. Both
directions are now in the report prose. Standing lesson: a derived artifact
committed out of step with the code produced a *pessimistic* published number
here, but it could as easily have gone the other way — regenerate exports in
the same commit as the physics.]**
Tapovan local speeds still fail (~4 vs 12–16) because the real front was
stick-slip (data prove it: mean 11 < slowest local 12) and τ-relaxation smears
that into steady creep. Two design payloads: the water-limit U(S) is the
EARLIEST-ARRIVAL envelope (granular regime only delays — conservative for
triggering), and μ is a per-event *trajectory* μ(f), all inputs computable from
global data. NEXT: Seti 2012 blind (impounded water = intermediate regime);
friction hysteresis (static>dynamic μ) if we want stick-slip.
The pipeline (OSM stitch → profile → junctions → transects → timing curve →
warning budget) uses only globally available data and runs in seconds per
catchment. Claim to test: it ports to any steep-ice-over-monsoon-river valley.
**Test: hindcast the back-catalog with ZERO recalibration** — Chamoli 2021
(timings + peaks published in Shugar et al., already in our files), Seti 2012,
Sikkim 2023, Kolka 2002, Huascarán 1970. If arrival curves land within the
warning-tier tolerance (±30-50%), the method is demonstrated. Then: prototype
**timing-budget atlas** for Nepal's hydropower corridors (which settlements/cell
sectors/plants sit in the machine-only tier vs the human-chain tier). Position
against prior art honestly: global GLOF mapping exists (lake-watching; ~15M
exposed per Taylor et al. 2023) but Langtang 2026 HAD NO LAKE — the
steep-ice-face-over-river class (LLOF) is the under-mapped superset. Operational
scale = ICIMOD/WMO/GFDRR program; our scope = method demo + regional prototype.

### Phase E0b — RELEASE POSTURE (decided 3 Sept, prepared not sent)

**Dave's decision: gift the work, don't run a campaign.** Release it to the
people who can use it, with NO ongoing involvement — no co-authorship, no
correspondence obligation, no preprint commitment. Authorship stays (it is the
accountability signature) but participation does not.

Prepared this session: `LICENSE` (MIT code / CC-BY-4.0 prose / third-party data
under its own terms, plus an explicit no-operational-warning-use clause);
`README.md` rewritten so a stranger can reproduce everything;
`DATA-SOURCES.md`; `outreach/gift-note.md` with the note, a four-name recipient
list and a release checklist.

**NOT SENT.** Checklist to clear first (full version in gift-note.md): build
entrainment, update the published pages with the Seti result and the corrected
geopera figures, native-speaker check on the Nepali page, record the Prince
video title/date, push the repo public, verify DHM data redistribution terms.

### Phase E0 — Artifact structure (decided 3 Sept, TO BUILD NEXT)

Four published artifacts now exist with no shared front door. Decision: build a
**hub artifact** as the canonical share link + a compact nav strip on each page
(NOT one merged mega-page: different audiences need different entry points, and
the technical report is already ~200 KB).

The hub should be a genuine one-screen front door, not a link list:
- the finding in three sentences;
- the three results (H1 water budget · the composition/"slush" test · the Seti
  blind hindcast) each with a one-line claim and confidence;
- routing BY AUDIENCE: general reader → plain English / नेपाली; scientist →
  technical report; skeptic/reviewer → workings notebook + repo + honesty rails;
- a dated "what changed" strip, because the findings are moving weekly;
- the standing data asks (DHM Galchhi/Devghat telemetry; hydropower SCADA
  historians) so anyone who lands there knows what would help.

Same visual family as the existing pages. This is what goes to Willsey, Petley,
Kargel/PSI and ICIMOD as a single URL — build it BEFORE the outreach letters go.

**Also due in the same pass:** neither plain-language page mentions the Seti
blind test or the corrected (retracted) geopera deposition numbers yet.

### Phase E — Write-up & engagement

**Plain-English companion published (3 Sept):** "The Water Was Already in the
River" (report/plain.html) —
https://claude.ai/code/artifact/39288bec-8708-4d94-8366-7a4966692543 —
jargon-free telling of the whole analysis incl. the slush/composition finding
and the seven-minute/seven-hour warning split; cross-linked both ways with the
technical report. Keep it current as findings move; consider a Nepali
translation (audience is in Nepal).
Short paper/blog-style write-up: the water budget nobody has published, the gross-vs-net
excess distinction, the impoundment timing test. Candidates to share with: Willsey (video
follow-up), Petley (Eos comments — he says "an international team has now got together"),
Kargel/PSI (email; their rapid assessment isn't public — worth requesting), ICIMOD hub.
Preprint on EarthArXiv if it holds up — none exists yet on this event (checked 2 Sept).

## 5. Data acquisition tasks

- [ ] Copernicus GLO-30 DEM tiles for the corridor (OpenTopography); extract river profile
- [ ] DHM/FFD: request full technical report (the 20 Mm³ method) + Galchhi/Devghat gauge series
- [ ] geopera methodology post (superelevation + trimlines) — their velocity/height table
- [ ] Sentinel-2 scenes 12/24/27/29 Aug (Copernicus Data Space) — channel widths pre/post
- [ ] USGS event `us7000tbwb` seismic products (via proxy; page TLS is broken)
- [ ] Email PSI for the Kargel rapid assessment
- [ ] Pre-event lake inventory of the Chhochen headwater from Sentinel-2 archive (nobody has
      published one — quick win, closes the "hidden GLOF" loophole)
- [ ] Historic Betrawati stn 447 flow-frequency data (for late-Aug baseflow distribution)
- [x] India Gandak records: Valmikinagar barrage hourly series obtained from press
      transcriptions (data/valmikinagar_barrage.csv) — routed peak 4,253 m³/s at
      23:00 IST, lag 7¼ h, −27% attenuation. Official FFD press release PDF obtained
      (data/ffd_report.pdf) — 20 Mm³ = Devghat 14:10–18:00 windowed excess.
      Remaining: CWC FFS hourly archive (needs Indian IP or formal request), DHM
      Devghat/Galchhi telemetry (data request).
- [ ] Map side-valley junctions & their catchment/valley volumes from DEM +
      Sentinel-2 (the "capacitors" of Phase B2)

## 6. Honesty rails

- Source volume spans 10–200 Mm³ and the ice fraction is unpublished — all conclusions must
  be stated as envelopes over that range, not point claims.
- FFD's 20 Mm³ is single-source with unpublished method; treat as a target with error bars.
- Kargel/Petley/Shugar already include river water and entrained sediment in their verbal
  accounts; our contribution is quantification, not correction of ignorance.
- geopera numbers are provisional (they self-corrected once already, 1 Sept).
- Casualty and event numbers are evolving; date-stamp everything.

## 7. Effort estimate

Phase A sensitivity: an evening. Phase B model: 2–3 evenings (DEM profile + routing + calib).
Phase C: 1 evening. Write-up: 1–2 evenings. Phase D only if hooked.
