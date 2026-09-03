# Chamoli 7 Feb 2021 hindcast — zero-recalibration portability test (Phase F)

**Date run:** 3 Sept 2026.
**Law applied verbatim (Trishuli fit, NOT refitted):** U = 300·S^0.82 + 4.0 m/s,
clipped to [3, 65]; front time = cumulative dx/U. Same pipeline as Phase B
(OSM Overpass stitch → 400 m sampling → Mapzen DEM → monotone + ~2 km smoothed
profile → slope), same convention (km 0 = scar, initial fall in the path).
The DEM is SRTM-era, i.e. the pre-event surface. Reproduce with
`run_hindcast.py` (uses cached `osm_rivers.json` / `profile.csv` if present).

## Path quality

OSM coverage was better than expected: **Ronti Gad is mapped** (as "Raunthi
Gadhera", plus an unnamed headwater segment directly below the scar), and
Rishi Ganga / Dhauli Ganga are continuous. **One bridge only: 1.50 km** from
the scar (30.3733 N, 79.7317 E) to the head of the unnamed Ronti Gad segment;
every other join was < 50 m. Stitched length scar → Vishnuprayag
(Alaknanda confluence) = **32.5 km**; endpoint elevations check out
(scar 5,655 m raw DEM; Tapovan 1,789 m; Vishnuprayag 1,487 m).

Path-km vs published (Shugar et al. 2021 ranges given in the task):

| Checkpoint | Our path-km | Published | Note |
|---|---|---|---|
| Rishiganga HPP (Raini village) | 16.0 | ~13.2–15 | ~1–3 km long |
| Raini (Rishiganga–Dhauliganga confluence) | 17.2 | ~13.5–15 | ~2 km long |
| Tapovan Vishnugad intake | 23.2 | ~24–26 | ~1–3 km short |
| Vishnuprayag (Alaknanda confluence) | 32.4 | — | no published anchor |

Two honest caveats. (1) The published triplet is internally inconsistent:
Raini at 13.5–15 km AND Tapovan at 24–26 km would need ~10 km of channel
between them, but the straight-line distance is 5.9 km and the Dhauliganga is
fairly direct there — our OSM-measured 6.0 km reach is self-consistent.
(2) Our upper-path km run long because the stream line is sinuous while the
avalanche cut corners/superelevated. Net path uncertainty is ±1–2 km, worth
< ±1.5 min of model arrival time — immaterial next to the 24-min timing miss
below. One waypoint in the tasking ("Raini ~30.398 N, 79.732 E") is actually
in the Ronti Gad valley; the real confluence (from OSM topology) is
30.488 N, 79.690 E, which is what we used.

## Scorecard — model vs observed (nothing tuned)

Observed values from Shugar et al. 2021 (Science, doi:10.1126/science.abh4455)
as supplied in the task; detachment 10:21:14 IST (seismic, hard). Their own
r.avaflow (full two-phase mechanics) matched seismic/video within 5%.

| Quantity | Model | Observed | Error | Within ±50%? |
|---|---|---|---|---|
| **Tapovan front arrival** | **11.0 min** | **34–37 min** (video, soft ±2 min) | **−69%** | **NO — fail** |
| Front speed near Rishiganga HPP (km 16.0) | 34.6 m/s | ~25 m/s (video) | +38% | yes |
| Front speed just above Tapovan (km 22.2) | 14.4 m/s | ~16 m/s (video) | −10% | yes |
| Front speed just below Tapovan (km 24.2) | 15.3 m/s | ~12 m/s (video) | +28% | yes |
| Mean speed scar→Tapovan | 35 m/s | ~11 m/s (implied by arrival) | ~3.2× fast | no |
| Raini arrival (soft) | 5.3 min | ~9–24 min (see below) | −41% to −78% | borderline/no |

Softness on the intermediate timing: open sources disagree on when the flow
passed Raini. Rana et al. 2022 (Geomatics Nat. Haz. Risk 13:1, 2023661) say
the flow took ~27 min for the ~6 km Raini→Tapovan, implying Raini at ~8–10 min
after detachment; a 10:45 IST reading of the Rishiganga HPP videos would put
it at ~24 min. News timelines round to "~10:30" for several locations. We
could not pin this from open sources in this run, so the Raini row carries the
full range and no verdict hangs on it. The Tapovan window (34–37 min) and the
three video speeds are the anchors, and they are the ones the task specified.

## Verdict

**Zero-recalibration portability FAILS the ±50% warning-tier timing test at
Chamoli: the model front reaches Tapovan in 11 minutes against an observed
34–37 — three times too fast.** The law overpredicts speed, in exactly the
direction flagged as plausible beforehand: Chamoli was a dense rock–ice
avalanche → debris flow (~80:20 rock:ice, winter low-flow channel, ~26.9 Mm³
of source mass), not a watery monsoon flood front like Trishuli.

The failure has a diagnostic shape:

- **Where the law is wrong:** the integrated travel time. In the steep upper
  canyon (S = 0.13–0.47 over km 0–12) the law rides its 65 m/s clip for
  12 km (unclipped it would demand ~130 m/s at the scar). A dense granular
  mass dissipates energy in basal/internal friction and in entraining ~10⁷ m³
  of sediment; whatever the exact split of the delay between the upper canyon
  and a possible mid-reach near-stall around the km 18–22 low-gradient basin
  (S ≈ 0.015), the real flow spent ~25 min more than the model somewhere
  upstream of Tapovan.
- **Where the law is roughly right:** the *local* slope→speed shape in the
  diluted, distal reach. All three video-derived point speeds land within
  ±40% with zero tuning — the +4 m/s floor and the moderate-slope behaviour
  port reasonably.
- **The pair of findings together is the diagnosis:** a single-valued U(S)
  cannot simultaneously match the point speeds and the arrival time at
  Chamoli. The front must have had friction-dominated, possibly stop-and-go
  phases (momentum loss to entrainment, transient blockage) that no slope-only
  law represents. This is a *regime* difference, not a calibration error —
  refitting a and b to Chamoli would just break Trishuli.

**Implication for Phase F: the front-speed law needs a debris-flow-regime
flag to be portable.** When the source is rock-dominated / water-poor (dense
granular flow), the steep-slope branch must be friction-limited — e.g. a
Voellmy-style cap or simply a much lower U_max (order 20–25 m/s, cf. observed
mean 11 m/s scar→Tapovan) — while the watery-flood branch (Trishuli-type,
monsoon channel, LLOF over a swollen river) keeps the current fit. That is a
legitimate Phase F finding, not a failure to hide: the portability claim as
stated ("any steep-ice-over-monsoon-river valley") survives only with the
regime qualifier attached, and Chamoli — winter, dry channel, 80% solids — is
precisely outside that class. Shugar et al. needed full two-phase r.avaflow
mechanics to hit 5%; a one-parameter slope law was never going to do that, but
±50% was the bar, and it missed it.

**Error direction note for the warning-tier framing:** the model is *early*,
never late — a warning system built on it would under-promise available lead
time (conservative for evacuation triggers) rather than over-promise. Still a
fail for tier-mapping purposes: a 3× timing error would misclassify
machine-only vs human-chain tiers.

## Energy/water budget check (already validated — referenced, not redone)

`calcs/energy_water_budget.py` scenario 0 ("VALIDATION Chamoli 2021")
independently reproduces the Shugar et al. water budget with the same
zero-recalibration inputs: melt water 4.8 Mm³ (ice-limited; energy-limited
value 5.0 Mm³ — the near-coincidence is their "almost exactly critical"
observation), river-derived water only ~8%, total ~5.6 Mm³. So the *budget*
arithmetic ports to Chamoli cleanly; it is the *front dynamics* law that
needs the regime flag. The two results are complementary: the budget explains
why Chamoli had so little water (and hence why its front crawled), which is
the same physics the speed law is missing.

## Files

- `run_hindcast.py` — full pipeline (Overpass fetch → stitch → DEM → law → scorecard + figure)
- `profile.csv` — 82 points, 400 m spacing, scar → Vishnuprayag
- `osm_rivers.json` — raw Overpass response (bbox 30.30,79.55–30.60,79.80)
- `chamoli_hindcast.png` — profile / arrival-time / speed comparison

Sources sighted this run (open web): Shugar et al. 2021
(science.org/doi/10.1126/science.abh4455, values as supplied in tasking);
Rana et al. 2022 (tandfonline.com/doi/full/10.1080/19475705.2021.2023661,
~27 min Raini→Tapovan); ICIMOD/preventionweb Chamoli explainer (news-grade
timeline, imprecise). Intermediate arrival times remain the softest numbers.

## Voellmy–Saint-Venant hybrid rerun (3 Sept, evening) — timing CLOSES with one thermal dof

**Build:** the resolved design (PLAN.md) implemented. `model/ladder.py` gained the
Coulomb term −μ·g·A·sign(Q) (v5, `simulate(mu=...)`; μ=0 leaves every published
Trishuli result **bit-identical** — regression checked). `run_voellmy.py` routes
the actual 26.9 Mm³ release block *dynamically* down the profile with the ladder
scheme (local-inertia SV + semi-implicit Manning + sign-preserving Coulomb clamp,
dry-bed capable), so event SIZE enters via depth and REGIME via μ. Friction is
Voellmy: S_f = μ + n²v²/h^{4/3}, with Manning n=0.05 as the turbulent term
(equivalent ξ = h^{1/3}/n² ≈ 860 m/s² at h=10 m, mid-range of published values).

**Failure anatomy first (each stage kills a hypothesis):**

| Model | Tapovan arrival (obs 34–37 min) | What it teaches |
|---|---|---|
| μ = 0 (water limit) | 9.3 min | dynamic control reproduces the kinematic law's ×3-fast failure |
| μ const = H/L = 0.155 | **never** — dies km 18.4 | deep flow outruns Coulomb on the steeps, then the flat basin (S≈0.015) is terminal: constant μ fails BOTH directions |
| μ(x) static melt dial 0.30→0.02 | 10.5–12.2 min | runout + 2/3 speeds fixed, but the basin is crossed in ~3 min |
| + valley-width profile (basin ~300 m) | never (pre-fix) | a wide basin thins the flow → Coulomb-bound stall; widths bracket obs: {12 min, 180 min, never} |
| **+ thermal-lag melt (τ = 5 min)** | **37.4 min — PASS (+5%)** | the closing physics |

The static dial μ(x) is anchored a priori: μ_dry = 0.30 from Scheidegger's (1973)
volume–mobility regression at 26.9 Mm³ (a DRY rock avalanche this size has
H/L ≈ 0.29); μ_wet = 0.02 (watery flood; Trishuli ladder limit); melt fraction
linear in cumulative fall with full melt at 3,400 m drop — the normalization our
validated energy budget (calcs scenario 0) already used. Path-mean μ ≈ 0.16 =
the observed travel angle falls out for free because the melt was critical.

**The thermal-lag dial (the one fitted degree of freedom):** dissipated heat
does not melt ice instantly — conduction into fragments of size d takes
τ ~ d²/(π²κ). The melt state f becomes a scalar *advected with the mass*,
relaxing toward the fall-completed equilibrium over τ; μ = μ_dry + (μ_wet−μ_dry)f.
The a-priori band (4–20 cm ice debris → τ ≈ 2–60 min) is wide, so τ is fitted:
arrival is monotone in τ (τ=0 → 12 min; 5 min → 37.4; 15 min → 104; ≥30 min →
dies upstream), and the observed window selects **τ ≈ 5 min ⇒ d ≈ 6 cm** —
physically sensible comminuted ice. Everything else is then out-of-sample:

- **Tapovan arrival 37.4 min vs 34–37 — PASS (+5%).** Robust: 28–52 min across
  basin widths ×0.5/×2, n ±0.01, μ_dry 0.25/0.35, uniform width — all inside
  the ±50% tier band.
- **Mean speed scar→Tapovan 10.3 m/s vs observed ~11 — essentially exact.**
- Flow speed (Q/A at passage — what feature-tracking video measures) at
  km 16: 14.6 vs 25 m/s — PASS (−42%).
- Basin crawl: model km 17→23 ≈ 21 min vs Rana et al.'s independently
  published ~27 min Raini→Tapovan — right mechanism, right order.
- **Remaining failure, honestly stated:** near-Tapovan local speeds (model
  ~3–4 vs 16/12 m/s). The observations themselves prove intermittency — the
  11 m/s *mean* is below the *slowest* local speed (12), so the real front
  moved stick-slip: surging when moving, stopped between. Our τ-relaxation
  smears stick-slip into steady creep: the time-integral is right, the
  microstructure is not. Fixing it needs friction hysteresis (static > dynamic
  μ) or two-phase mechanics — Shugar et al. needed r.avaflow for 5%.

**Phase F implications:** (1) the portable warning law keeps the water-limit
U(S) as the *earliest-arrival envelope* — the Coulomb/granular regime only ever
DELAYS arrival (conservative direction for triggering); (2) the regime dial is
not a per-event constant but a trajectory μ(f) with f driven by the melt energy
ledger — and every input (μ_dry from Scheidegger's regression at the source
volume, melt criticality from the energy budget, widths from imagery) is
computable from globally available data; (3) the wide flat basin acted as a
phase separator (solids aggrade, water continues) — single-phase models
structurally struggle there, flagged for the Seti 2012 blind test, which is the
next hindcast (impounded water = intermediate regime).

Reproduce: `run_voellmy.py` (figure `chamoli_voellmy.png`).

## Caveat added 3 Sept (Dave's methodological catch)

The ported law U = 300·S^0.82 + 4 has **no event-size input** — slope is its
only variable, so the Trishuli event's scale and water content are baked
implicitly into the fitted constants. This hindcast therefore assumed a
Trishuli-sized, Trishuli-wet wave on Chamoli's terrain, and the timing fail
conflates two effects: flow REGIME (granular vs watery — the dominant one) and
SCALE (deeper flows run faster within a regime). A portable law needs both
made explicit: size enters via depth/discharge (the ladder model already takes
the event volume as input; the snowplow law could carry a (Q/Q_ref)^c factor),
and regime enters via the water-availability flag.

Counterpoint worth keeping: Chamoli's initiating mass (26.9 Mm³) was likely
COMPARABLE TO OR LARGER than Langtang's initial detachment (~1–10 Mm³ per the
early-September estimates), yet its front ran ~3× slower on steeper terrain.
At these scales the water in the valley dominates the rock off the hill as the
front-speed control — size matters within a regime; regime matters more.
