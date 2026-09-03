# Seti River flood, 5 May 2012 — observational anchors for a blind hindcast

**Compiled:** 3 September 2026 (by Claude, from open sources; the Seti research
agent hit a usage limit mid-task, so this is a direct compilation — narrower
than the full brief but sufficient to run the blind test).
**Purpose:** freeze the observations BEFORE running the Voellmy–Saint-Venant +
dilution-dial model on this event. Nothing here may be used to tune the model.

## Why this event is the right blind test

Chamoli (dry, winter, granular) and Langtang (wet, monsoon, watery) are the two
endmembers our dial spans. **Seti 2012 is the intermediate case by construction:**
a dry-ish rock/ice avalanche that hit *impounded water* — a reservoir that had
been filling behind a rockfall dam for weeks. Water availability is neither
"melt-only" nor "monsoon river": it is a discrete stored volume released on
impact. If the dial is real physics rather than a two-point fit, this is where
it has to prove it.

## 1. Trigger

| Quantity | Value | Quality | Source |
|---|---|---|---|
| Seismic time of impact | **09:09:56 NPT**, 5 May 2012 | **hard** | Nepal National Seismological Centre — recorded at all 21 stations |
| Seismic magnitude | ~M 3.8–4.0 (local) | medium | NSC via SANDRP |
| Signal duration, nearest station | **70 minutes** at Dansing (32 km SW) — read as the duration of the debris flow | medium | NSC via SANDRP |
| Source | rock/ice avalanche off a near-vertical cliff on the ridge just S of Annapurna IV (7,525 m) | hard | multi-source |
| Detached volume | **22 Mm³** (Kargel/NASA) vs **33 Mm³** (rock-and-ice avalanche, SW ridge — NHESS/ESP literature) | **CONTESTED** — carry both | Kargel via NASA Earth Observatory; Hanisch et al. 2013 lineage |
| Fall of the avalanche | **6,850 m → 4,500 m, "almost vertically"** = ~2,350 m | medium | SANDRP compilation |
| Total drop, ridge to river bed | ~3,400 m to the Seti headwaters (NASA); "~6,100 m" quoted for ridge-to-Pokhara | **inconsistent** — the 6,100 m figure is ridge-to-valley over the whole path; use 2,350 m for the avalanche and ~3,400 m to the headwater channel | NASA Science; SANDRP |

## 2. Path

Source: cliff S of Annapurna IV → **Sabche Cirque** (partly glacier-covered, the
avalanche's landing basin) → the narrow, steep **Seti Khola headwater gorge**
(where the rockfall dam sat) → **Kharapani / Tatopani** → Sardikhola → Pokhara.

| Segment | Distance | Source |
|---|---|---|
| Landslide dam → worst-flood reach | **~29 km** | SANDRP |
| Dam/source → Kharapani | **~20 km** | SANDRP ("20 km downstream at Kharapani in just 28 minutes") |
| Source region → Pokhara | ~60 km | NHESS 2022 (Pokhara flood-scenario paper) |

Approximate coordinates for path construction (to be refined from OSM):
Annapurna IV ~28.537 N, 84.082 E; Sabche Cirque floor ~28.47 N, 84.02 E;
Kharapani/Tatopani ~28.35 N, 84.03 E; Pokhara (Seti irrigation dam) ~28.21 N,
83.98 E. **These are map reads, not published waypoints — flag as soft.**

## 3. TIMING ANCHORS — what the model is scored against

| Location | Time (NPT) | Elapsed | Quality | Source / basis |
|---|---|---|---|---|
| Impact (t=0) | 09:09:56 | 0 | **hard** | seismic, 21 stations |
| Ultralight pilot reports it to Pokhara tower | 09:16 | ~6 min | medium | pilot radio log via SANDRP — an *observation of the event*, not of the flood front |
| **Kharapani (~20 km)** | **09:38** | **~28 min** | **hard-ish** | timestamp on a photograph taken by picnickers at Tatopani as the debris flood arrived; independently quoted as "20 km in 28 minutes ≈ 12 m/s" |
| Seti irrigation dam, Pokhara | 10:35 | ~85 min | medium | SANDRP |

Mean front speed source→Kharapani: **~12 m/s** (as published). Note this is
*four times slower* than Langtang's ~53 m/s and *similar to* Chamoli's ~11 m/s
— despite Seti having abundant impounded water. The model must reproduce a
SLOW front here, which is why this is a real test and not a freebie.

## 4. Flow observations

| Quantity | Value | Quality | Source |
|---|---|---|---|
| Number of surges | **~27 waves** over the following hours (eyewitnesses) | medium | SANDRP / Kargel |
| First wave volume | ~0.25 Mm³ "in just a few minutes" | soft | SANDRP |
| Total water | "several million cubic metres" overall | soft | SANDRP |
| Peak discharge | **935 m³/s** | medium (personal communication, B. Poudel) | via SANDRP |
| Flow depth | up to **30 m** at places | medium | SANDRP |
| **Flow density** | **1.88 g/cm³** | medium | SANDRP |
| Fatalities | 72 | hard | multiple |

**The density number is a gift.** ρ = 1.88 g/cm³ with quartz solids (2.65) and
water (1.0) implies a solid volume fraction of **0.53** and hence a **water
volume fraction w ≈ 0.47** — comfortably above our W_SAT = 0.25, i.e. the flow
was in the *slurry* branch of the dial, not the granular branch. This is an
independent, published measurement of the very quantity our dial advects, and
it was obtained without reference to any model. Scoring opportunity: the model
should show w > W_SAT through the Kharapani reach.

## 5. The water-source debate (the reason this event matters to H1)

- **Kargel (NASA/PSI, 2013–14):** the hard part was never the avalanche, it was
  the *water* — **there was no glacial lake, no known lake at all**. His
  reconstruction: a rockfall blocked the narrow Seti gorge *weeks earlier*; the
  impoundment filled with spring snow- and ice-melt; the 5 May avalanche then
  dislodged that dam, releasing stored water. The flood's water was
  **pre-existing valley water**, not melt generated during the run.
- **Hanisch et al. 2013** ("Cause and mechanism of the Seti River flood",
  *J. Nepal Geol. Soc.*): same family of explanation — debris blocked the steep
  headwater gorge and impounded meltwater from the partly glacier-covered
  Sabche Cirque, which then burst.
- **Common ground:** every serious account puts the water in the valley *before*
  the avalanche. **This is the strongest published precedent for H1** — and it
  was Kargel's own conclusion, which is worth stating plainly whenever we
  contrast our Langtang result with his public framing of that event.

## 6. What the blind test will be

Run the unified Voellmy–Saint-Venant + dilution-dial model on the Seti path with
**frozen** constants (μ_wet, W_SAT, the Coulomb/Bingham branches, stranding) and
event inputs taken only from this file (22 and 33 Mm³; ~2,350 m fall; impounded
water as a discrete released volume). Score against: Kharapani 28 min (hard),
Pokhara ~85 min (medium), ~12 m/s mean front speed, peak 935 m³/s, w > 0.25 in
the flowing mixture, multi-surge structure present.

**Pre-registered expectations (written before running):** (1) the front should
be SLOW — this is the failure mode that would most embarrass a model tuned on
Langtang's fast wave; (2) the released impoundment should show up as a water
pulse that outruns the debris body, the same structure our Langtang camera
hypothesis proposes; (3) the ~27 surges are a relaxation-oscillator signature
our ladder can demonstrate but probably cannot predict in detail.

## 7. Sources

| URL | What it gave | Authority |
|---|---|---|
| https://sandrp.in/2014/01/26/explained-seti-river-floods-in-may-2012-nepal-a-chain-of-events-starting-at-25000-feet/ | the full timeline (09:09:56, 09:16, 09:38, 10:35), 20 km/28 min/12 m/s, 22 Mm³, 6,850→4,500 m, 27 waves, 935 m³/s, 30 m depths, density 1.88, dam-impoundment mechanism | Medium-high (careful compiler; quotes named sources incl. Kargel and B. Poudel) |
| https://science.nasa.gov/blogs/notes-from-the-field/2014/01/24/one-scientists-search-for-the-causes-of-the-deadly-seti-river-flash-flood/ | Kargel's investigation; "no glacial lake, no known lake at all"; 3,400 m fall to headwaters | High (NASA, named scientist) |
| https://www.nepjol.info/index.php/JNGS/article/view/31576 | Hanisch et al. 2013, "Cause and mechanism of the Seti River flood" — the peer-reviewed account (abstract level only in this pass) | High (peer-reviewed) |
| https://nhess.copernicus.org/articles/22/3105/2022/ | Pokhara rare-flood-scenario paper: 33 Mm³ rock-and-ice avalanche from the SW ridge; Sabche Cirque framing; ~60 km to Pokhara | High (peer-reviewed, NHESS 2022) |
| https://en.wikipedia.org/wiki/May_2012_Nepal_floods | consolidation, casualty figures | Medium (tertiary) |
| https://blogs.agu.org/landslideblog/2012/05/23/understanding-the-seti-river-landslide-in-nepal/ | Petley's contemporaneous analysis (indexed; not fetched this pass) | High (expert blog) |

**Gaps not closed this pass:** the Hanisch et al. full text (paywalled/NepJOL
fetch not attempted); precise published coordinates for the dam site; the
distribution of the 27 surges in time; whether 22 vs 33 Mm³ measure the same
thing (they may be avalanche-only vs avalanche-plus-entrained).
