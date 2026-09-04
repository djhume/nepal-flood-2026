# The entrainment term — build, test and verdict

**Built:** 3 September 2026 (night). **Code:** `model/core.py` (the closures),
`model/unified.py` (Trishuli scoring), `hindcast/seti/run_seti.py` (Seti).

The model could put sediment down and never pick any up. Three independent
observations said so, and two of them are quantitative, so the term could be
built against literature constants and *scored* rather than fitted.

| Target | Value | Source |
|---|---|---|
| Langtang corridor erosion | **3.2 Mm³ eroded** vs 0.9 Mm³ deposited in the ~45% mapped — net erosional ~3.5:1 | geopera WorldView-3 stereo DEM, 1 Sept (after they retracted the 28 Aug "12 Mm³ wedge" as noise) |
| Seti 2012 flow density | 1.88 g/cm³ ⇒ **w ≈ 0.47** | SANDRP compilation, measured, no model involved |
| Langtang distal water | ~100% river-derived in every scenario | our own v2 result — a symptom, not a target |

## What was built

Two closures, sharing the mass and tracer bookkeeping, both with constants
taken from the literature. Nothing was chosen with reference to the numbers
above.

**`law="takahashi"` — capacity-limited (default).** Takahashi's equilibrium
sediment concentration for a mature debris flow on a bed of internal friction
angle φ,

```
c_eq = ρ_w tanθ / ((ρ_s − ρ_w)(tanφ − tanθ))        (0 below tanθ = 0.03, capped at 0.9 c*)
ė = +δ_e (c_eq − c)/(c* − c_eq) · u                 erosion, where c < c_eq
ė = −δ_d (c − c_eq)/c* · u                          deposition, where c > c_eq
```

with δ_e = 0.0007 and δ_d = 0.05 — Takahashi's own coefficients, as used in
Kanako and its descendants — φ = 37°, c* = 0.65, ρ_s = 2,650 kg/m³. The bed
slope and the friction angle set the answer; there is no free parameter in the
equilibrium state.

**`law="shear"` — not capacity-limited.** Frank et al. (2015) found maximum
erosion depth in Swiss debris-flow channels linear in maximum basal shear
stress, `z_pot = K_τ(τ_b − τ_c)`, approached over an entrainment time. K_τ =
3×10⁻⁵ m/Pa sits in their 1–5×10⁻⁵ band. This closure can drive the flow
*above* local transport capacity, which is what a surge front does.

**Shared limits.** A finite erodible layer `H_ERODE` (bedrock gorges do not
supply unlimited sediment; swept 1–10 m, it is the one genuinely uncertain
input). A settling cap on deposition — solids cannot leave the flow faster
than they fall through it, `W_SETTLE · c` — which is the rate control that
lets a surge cross a low-capacity reach still loaded.

**Bookkeeping.** The bed is saturated, so eroding a bulk volume dE adds
c*·dE of solids and (1−c*)·dE of pore water, and a deposit carries its pore
water back down with it. The release-origin tracers (`hwr`, `hr`) are never
touched by entrainment, so the H1 provenance answer cannot be contaminated by
the new term. Entrained/re-deposited bed material is tracked in its own
ledgers (`ero`, `dep`), separate from the stranding ledger (`bed`), so the two
mechanisms can never be confused in a scorecard.

## Result 1 — the erosion volume lands, with no fitted constants

Trishuli, scenario C (ice-rich, V = 30 Mm³):

| Reach | Eroded | Deposited |
|---|---|---|
| scar → border (km 0–22) | 2.57 Mm³ | 17.36 Mm³ |
| border → Betrawati (km 22–68) | 1.22 Mm³ | 1.74 Mm³ |
| below Betrawati | 0.00 | 0.00 |
| **total** | **3.78 Mm³** | 18.99 Mm³ |

**3.8 Mm³ of erosion against geopera's 3.2 Mm³ measured** in the ~45% of the
corridor their stereo pair covers — and the erosion is concentrated exactly
where they mapped it, in the upper gorge. It is robust:

| Varied | Erosion (Mm³) |
|---|---|
| closure: Takahashi / Frank shear | 3.8 / 3.9 |
| scenario: C (V=30, w₀=0.15) / F (V=60, w₀=0.40) | 3.8 / 3.8 |
| H_ERODE 1 / 3 / 10 m | 3.04 / 3.78 / 4.37 |
| W_SETTLE 0.025 → 0.002 m/s | 3.78 → 2.53 |

Every one of those numbers is within a factor of 1.5 of the measurement, using
coefficients published for other rivers on other continents. This is the
first quantitative out-of-sample hit for the sediment side of the model.

## Result 2 — the deposition is 8–40× too large, and that is an event-size statement

The same run deposits 19.0 Mm³ through the closure and strands another
15.3 Mm³ of solids — 42.5 Mm³ of bulk valley fill, against geopera's 0.9 Mm³
measured and ~5 Mm³ in their own calibrated model.

This is not mainly a failure of the closure. Scenario C releases 30 Mm³ of
material, 25.5 Mm³ of it solid, and the model shows those solids never reach
Devghat — the distal water is 100% river-derived with entrainment on, exactly
as without it. So the solids must be in the corridor, and **a DEM difference
would have seen them.** It did not.

Turning that round gives a new and sharp constraint on the source:

> If the corridor's measured bulk deposition is ≲5 Mm³, and essentially all
> released solids deposit within it, then the release delivered **≲3–5 Mm³ of
> solids to the channel** — i.e. V_rel ≲ 6 Mm³ at w₀ = 0.15, ≲ 8 Mm³ at
> w₀ = 0.40.

That is consistent with the EGU preliminary estimate (0.5–10 Mm³) and with
geopera's own measured valley change (~4 Mm³), and it is one to two orders
below the 100–200 Mm³ source figures in circulation. It is also in direct
tension with our own routing, which needs V = 30–60 Mm³ through the border to
make the downstream clocks and volumes. **PLAN.md had flagged that discrepancy
qualitatively; the entrainment ledger makes it an arithmetic contradiction
that somebody has to resolve.** The most likely resolutions, in order of our
current preference:

1. the release was mostly **ice and water**, not rock — a small solid mass
   with a large liquid one leaves little to deposit and still delivers the
   momentum and the water (this is the composition finding pointing the same
   way a third time);
2. ~~the flood's volume at the border is dominated by impounded river water
   released at the junction (H3)~~ — **WITHDRAWN 4 Sept, arithmetic fails.**
   Blocking the Lhende (~60 m³/s) or even the main stem (~150 m³/s) stores
   0.02–0.6 Mm³ over any duration the 08:44 border clock allows; reaching
   20 Mm³ by impoundment needs the river blocked for **37 hours**. An
   in-event impoundment can re-time and sharpen a pulse, which is a real and
   testable effect, but it cannot be a volume source. H1's water comes from
   the **46.9 Mm³ standing in the channel** at any instant, which needs no
   dam at all;
3. geopera's mapped 45% missed the deposition, which their own retraction
   history makes worth checking before leaning on the number.

## Result 3 — the distal wave does not survive proper deposition

| Scenario | Galchhi 30-min rise | Devghat peak |
|---|---|---|
| C, no entrainment | 1.6 m | 1,671 @ 17:53 |
| C, Takahashi | **0.1 m** | 1,472 (baseflow) |
| F, no entrainment | 10.2 m | 2,138 @ 13:42 |
| F, Takahashi | **1.5 m** | 1,787 @ 16:57 |

Observed: Galchhi rise ~9 m, Devghat 5,850 m³/s total (~2,900 excess) at 16:00.

Adding entrainment makes the distal fit **worse**. Scenario F was the only run
that had ever landed a distal observable (its 10.2 m Galchhi rise against ~9
observed); with deposition modelled it collapses to 1.5 m. This is a real
regression and it is reported as one.

The mechanism is single-phase. Once the mixture is 15–40% solids and the
closure is allowed to drop solids, it drops all of them, and since solids are
volume the discharge goes with them. The real event had a rocky core that
stopped in the gorge *and* a watery flood that continued for 170 km — the
"mixed-mass" structure already named in PLAN.md — and one phase can only be
one of those at a time. **Entrainment has turned that from a qualitative
tension into a quantified one: you cannot simultaneously deposit 25 Mm³ of
solids in the upper corridor and deliver a 9 m rise at Galchhi with a
single-phase model.**

## Result 4 — Seti's density gap is not closed, and the reason is diagnostic

Both closures move the Seti flow the wrong way: w ≈ 0.97 against 0.47
observed (v1: 0.92). Takahashi's equilibrium concentration at Kharapani's bed
slope of 0.02 is **zero** — below the threshold where a mature debris flow can
exist at all — so a capacity-limited closure predicts clear water where the
measurement says 53% solids by volume.

The measurement is therefore telling us something the closure cannot express:
**the Seti flow at Kharapani was ~20× over its local transport capacity**,
carrying what it entrained kilometres upstream and in the act of dumping it.
That is what a surge is, and it is why Kharapani is buried in the deposit.
Neither the settling cap (swept ×1/5 and off) nor the erodible layer (1–10 m)
changes it: the closure strips the load in transit because it models
deposition as settling through quiet water, with no turbulent suspension.

(The Seti run has larger problems than this — see `hindcast/seti/RESULTS.md`.)

## Verdict

**The erosion side works and is quantitatively right on the one place we have
a measurement. The deposition side is wrong in a way that is now precisely
characterised, and it takes the distal fit down with it.**

Three things follow, in priority order:

1. **The single-phase assumption is the binding constraint, not the erosion
   law.** Next build: split the solid load into a coarse fraction that obeys
   the capacity closure and a fine/wash fraction that rides with the water.
   Two numbers, one physical split, and it addresses Results 3 and 4 together.
2. **Deposition needs turbulent suspension.** The settling cap uses a
   quiet-water fall velocity; for h ~ 10 m at 6 m/s the Rouse number of medium
   sand is ~0.2, i.e. fully suspended. `W_SETTLE` should be modulated by
   shear velocity rather than swept as a constant.
3. **The event-size contradiction (Result 2) is now the sharpest open question
   in the project** and it is answerable with data that exists: a complete
   DEM difference of the corridor, not 45% of it.

## Honesty notes

- The entrainment constants (δ_e, δ_d, K_τ, φ, c*, ρ_s, W_SETTLE) are
  literature values and were not adjusted after seeing any score. `H_ERODE` is
  a genuine free input and is swept, not fitted.
- The dial constants (MU_WET, W_SAT, TAU_Y0, RHO_MIX, U_DEP, T_DEP) were left
  frozen. The published Trishuli scenario table reproduces **bit-identically**
  after the refactor into `model/core.py` and after the depth-floor fix below.
- One genuine bug was found and fixed while building this: the 0.05 m
  numerical wet-film floor on depth manufactured volume in draining cells, and
  because the water tracer was untouched, the manufactured volume counted as
  **solid** and fed the stranding ledger. Harmless in every published run
  (narrow, always-wet channels) but on a kilometres-wide basin floor it
  reported 53 Mm³ stranded from a 19.8 Mm³ release. The film is numerical, so
  it is now added as water. Published results are unchanged.
