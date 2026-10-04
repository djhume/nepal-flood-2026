# Detachment volume from the pre/post DEMs — output of `calcs/dem_volume.py`

Data: Shean & Bhushan, Zenodo 10.5281/zenodo.22842748 (pre) and 10.5281/zenodo.22842746 (post), CC BY-NC 4.0. Cross-checks: NSIDC HMA 8 m mosaic; Copernicus GLO-30; RGI 7.0.

## Step 2 — co-registration on stable ground
stable ground: off-glacier (RGI 7.0 + 100 m), >500 m from our path and Huang et al.'s, >2 km from the scar, slope <40° — 3.2 km²
before: median -0.10 m, NMAD 1.46 m
shift applied to the pre-event surface: +0.50 m E, -0.43 m N, -0.17 m up
after: median +0.00 m, NMAD 1.40 m

## Step 3 — control, post-fit, binned as dossier §32b
| distance from either path | n | median | NMAD |
|---|---|---|---|
| 500–1,000 m | 161,077 | +0.02 | 1.09 |
| 1,000–2,000 m | 115,754 | -0.10 | 1.63 |
| 2,000–4,000 m | 248,490 | -0.07 | 1.66 |
| 4,000– m | 261,591 | +0.07 | 1.27 |

by elevation (snow and high-terrain check):
| band | n | median | NMAD |
|---|---|---|---|
| 3,500–4,000 m | 239,053 | +0.10 | 1.28 |
| 4,000–4,500 m | 184,238 | +0.15 | 1.46 |
| 4,500–5,000 m | 284,516 | -0.14 | 1.35 |
| 5,000–5,500 m | 74,285 | -0.25 | 1.55 |
| 5,500–6,000 m | 4,413 | +1.05 | 4.01 |

**G1** (§13d: bias ≤ 1.0 m, NMAD ≤ 3.0 m) — worst bin 0.10 m / 1.66 m → **PASS**
**G1s** (§13c step 3: ≲ 0.5 m, ≲ 2.0 m) → **PASS**

The authors' ungated median where their gate FAILS, on stable ground: n = 538,723, median -4.5 m, NMAD 16.2 m, **mean -47.9 m**, 5th percentile -353 m. Where the gate passes: mean +2.2 m.

## Two independent pre-event surfaces, co-registered to the gated 2 m surface on stable ground
NSIDC HMA 8 m mosaic: raw offset +1.48 m; shift +0.2 E, -0.8 N, -1.45 up; post-fit stable NMAD 0.87 m
Copernicus GLO-30: raw offset +32.04 m; shift -1.6 E, +2.1 N, -31.79 up; post-fit stable NMAD 4.63 m

## Step 4 — footprint from the elevation change (ungated median, co-registered)
G3 window — within ±50 % of both 1.009 (arXiv) and 1.957 km² (UNOSAT): 0.98–1.51 km²
| threshold | area km² | vs arXiv | vs UNOSAT | **G3** | void, median % | void, gated % (**G2**) | edge on void % | elevation m |
|---|---|---|---|---|---|---|---|---|
| -5 m | 4.34 | +330 % | +122 % | FAIL | 1 | 14 (PASS) | 27 | 4,054–5,666 |
| -10 m | 1.24 | +23 % | -37 % | PASS | 3 | 36 (PASS) | 11 | 4,100–5,314 |
| -20 m | 0.89 | -12 % | -54 % | FAIL | 4 | 43 (FAIL) | 29 | 4,174–5,188 |
| -30 m | 0.79 | -22 % | -60 % | FAIL | 3 | 44 (FAIL) | 41 | 4,316–5,188 |

## Step 6b — the 36 % of the −10 m footprint where the authors' gate fails
| independent surface | cells covered | 2 m median minus it: median | mean | volume effect Mm³ |
|---|---|---|---|---|
| HMA 8 m (same archive & pipeline) | 88 % | -0.7 m | +5.1 m | +2.1 |
| GLO-30 (radar, independent) | 100 % | -2.9 m | -10.7 m | -4.4 |
(positive = the 2 m median sits higher, i.e. would overstate the loss.) Gate-failed cells hold 49 Mm³ of the −10 m footprint's volume, over 0.41 km².

## Steps 5 and 6a — volume, with glacier thinning measured for each pre-event surface
Thinning reference: RGI 7.0 glacier >500 m from the −5 m footprint and >1 km from either path, median dh in 100 m bands at the footprint's own elevations, applied band by band to the footprint's glacier cells (low) or all its cells (high).
| footprint | pre-event surface | coverage % | raw Mm³ | thinning Mm³ | corrected Mm³ | mean depth m |
|---|---|---|---|---|---|---|
| -10 m | 2 m median (Shean & Bhushan) | 97 | 125 | 4.3–7.1 | 118–121 | 101 |
| -10 m | 2 m gated + hypsometric fill | 64 | 120 | 4.3–7.1 | 113–116 | 97 |
| -10 m | HMA 8 m mosaic | 94 | 123 | 4.2–7.7 | 115–119 | 99 |
| -10 m | GLO-30 | 100 | 131 | 8.2–14.1 | 117–123 | 106 |
| -20 m | 2 m median (Shean & Bhushan) | 96 | 122 | 2.4–5.0 | 117–120 | 137 |
| -20 m | 2 m gated + hypsometric fill | 57 | 119 | 2.4–5.0 | 114–116 | 133 |
| -20 m | HMA 8 m mosaic | 92 | 119 | 2.5–5.5 | 114–117 | 134 |
| -20 m | GLO-30 | 100 | 126 | 5.2–10.6 | 115–121 | 141 |
| -30 m | 2 m median (Shean & Bhushan) | 97 | 118 | 2.1–4.5 | 114–116 | 151 |
| -30 m | 2 m gated + hypsometric fill | 56 | 115 | 2.1–4.5 | 111–113 | 147 |
| -30 m | HMA 8 m mosaic | 92 | 116 | 2.1–4.8 | 111–114 | 148 |
| -30 m | GLO-30 | 100 | 122 | 4.7–9.9 | 113–118 | 156 |

thinning by band, −10 m footprint, 2 m surface:
| band m | reference cells | median dh m | NMAD | footprint cells | glacier share |
|---|---|---|---|---|---|
| 4,000–4,100 | 0 | +nan | nan | 1 | 0 % |
| 4,100–4,200 | 0 | +nan | nan | 1,153 | 0 % |
| 4,200–4,300 | 0 | +nan | nan | 7,331 | 0 % |
| 4,300–4,400 | 2,516 | -3.6 | 4.2 | 11,231 | 25 % |
| 4,400–4,500 | 91,787 | -5.5 | 6.4 | 15,959 | 40 % |
| 4,500–4,600 | 140,653 | -9.1 | 5.5 | 22,963 | 58 % |
| 4,600–4,700 | 27,575 | -7.2 | 5.4 | 30,470 | 49 % |
| 4,700–4,800 | 16,492 | -2.4 | 4.9 | 41,035 | 47 % |
| 4,800–4,900 | 13,862 | -1.0 | 2.3 | 34,644 | 53 % |
| 4,900–5,000 | 7,854 | -7.4 | 6.6 | 31,391 | 57 % |
| 5,000–5,100 | 4,581 | -8.7 | 5.1 | 45,311 | 63 % |
| 5,100–5,200 | 17,110 | -7.1 | 2.6 | 35,149 | 70 % |
| 5,200–5,300 | 50,581 | -7.1 | 2.6 | 23,655 | 100 % |
| 5,300–5,400 | 25,000 | -6.1 | 8.2 | 409 | 100 % |

## Independent post-event surfaces (2 m median pre-event, each footprint)
| footprint | all-source composite | WV-2, 8 Sept | Legion-2, 6 Sept (coverage) |
|---|---|---|---|
| -10 m | 125 | 126 | 120 (79 %) |
| -20 m | 122 | 122 | 123 (74 %) |
| -30 m | 118 | 118 | 119 (74 %) |
WV-2 minus Legion-2 inside the −10 m footprint, 1.00 km² in common: median -0.77 m, NMAD 1.50 m

## Step 6c — snow, bounded: off-glacier stable ground at 4,100–5,314 m reads -0.12 m (n = 457,749), worth +0.2 Mm³ over the −10 m footprint

## Step 7 — random error: stable NMAD at the scar's elevations, all slopes, 1.7 m; correlated over 500 m (Rolstad et al. 2009) → ±0.8 Mm³ (1σ) over the −10 m footprint

## The range
envelope of 3 thresholds × 3 pre-event surfaces × 3 post-event surfaces, each thinning-corrected: **111–123 Mm³**; widened by 2σ random error: **110–124 Mm³**
held out of the envelope, with the reason: '2 m gated + hypsometric fill' gives 111–116 Mm³. Its voids are the deepest part of the scar and the fill borrows depths from the shallower edges at the same height, so it is low by construction; the two independent surfaces above say the cells it discards are sound.

## Context, not part of the detachment — net change on the headwall and impact zone below the scar
within 1,500 m of the footprint, outside it, gated cells only (53 % of the ring measured), thinning removed: lost 20 Mm³ in cells beyond −10 m, gained 7 Mm³ in cells beyond +10 m — both LOWER bounds, because the impact zone is partly void
within 2,500 m of the footprint, outside it, gated cells only (31 % of the ring measured), thinning removed: lost 24 Mm³ in cells beyond −10 m, gained 26 Mm³ in cells beyond +10 m — both LOWER bounds, because the impact zone is partly void

## Where the published coordinates sit
| point | pre m | post m | dh m | inside −10 m footprint |
|---|---|---|---|---|
| Petley | 4,835 | 4,837 | +2 | no |
| Davies | 4,833 | 4,674 | -159 | yes |
| Huang et al. pin | nan | nan | +nan | no |
| UNOSAT centroid | 4,329 | 4,337 | +8 | no |
footprint centroid: 28.2880 N, 85.5262 E (UTM 355,466 E, 3,129,992 N)
