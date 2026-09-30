# Model A — the first 22 km, scored on the upper corridor alone

300 Latin-hypercube samples over 11 inputs. **The volume prior is the field's 135–200 Mm³, not ours**, and the ice prior is widened down to 0.10 so that another analyst's 13 % composition is inside it. Nine observables, all above Betrawati; the lower river is not scored here (PLAN §11).

| observable | target | window |
|---|---|---|
| border arrival, min | 7.68 | ±30% |
| Syabrubesi arrival, min | 13.0 | ±50% |
| section-mean peak speed, gorge km 24-34, m/s | 34.0 | ±35% |
| erosion km 0-68, Mm3 | 3.2 | ±60% |
| stage_gorge (fit median 73.3) | — | 58.8–98.9 m |
| stage_syabru (fit median 70.9) | — | 58.7–81.8 m |
| stage_hakubesi (fit median 67.5) | — | 42.0–84.9 m |
| stage_to_betra (fit median 29.0) | — | 20.0–41.3 m |
| rock-only deposition km 0–199, Mm³ | — | ≤ 12.0 |


## Result: 300 runs, **6 satisfy all 9**

| observable | met by |
|---|---|
| border_min | 101 / 300 |
| syabru_min | 290 / 300 |
| v_gorge | 164 / 300 |
| erosion_Mm3 | 269 / 300 |
| stage_gorge | 222 / 300 |
| stage_syabru | 95 / 300 |
| stage_hakubesi | 281 / 300 |
| stage_to_betra | 255 / 300 |
| deposit_Mm3 | 108 / 300 |

## POSTERIOR — ranges, not point estimates

| input | p10 | median | p90 | prior | reading |
|---|---|---|---|---|---|
| V_rel | 141 | **143** | 161 | 135–200 | constrained |
| w0 | 0.385 | **0.57** | 0.827 | 0.02–0.95 | constrained |
| mu_dry | 0.125 | **0.202** | 0.31 | 0.03–0.35 | weakly constrained |
| n_scale | 0.857 | **1.01** | 1.19 | 0.7–1.4 | constrained |
| h_erode | 2.53 | **5.31** | 7.63 | 1–10 | weakly constrained |
| f_fine | 0.175 | **0.456** | 0.778 | 0–0.98 | weakly constrained |
| xi | 133 | **180** | 287 | 100–2e+03 | constrained |
| k_junc | 2 | **4.05** | 6.39 | 1–10 | constrained |
| f_wl | 0.372 | **0.511** | 0.903 | 0.3–1 | **UNCONSTRAINED** — posterior fills the prior |
| f_ice | 0.427 | **0.883** | 0.923 | 0.1–0.95 | weakly constrained |
| T_rel | 270 | **376** | 439 | 60–600 | constrained |

## What the passing runs do downstream (NOT scored here)

| | p10 | median | p90 |
|---|---|---|---|
| stage_betra_gal | 9.6 | 13.8 | 16.9 |
| stage_galchhi | 7.6 | 14.9 | 19.3 |

(Galchhi's window is 3.5–9.9 m. These runs were not asked to meet it. How badly they miss is the measure of how much the two halves of the river disagree — PLAN §11's whole question.)

## Best runs

| V Mm³ | w0 | f_ice | mu | xi | f_wl | T_rel | met | border | v_gorge | gorge | syabru | hakubesi | to_betra | ero | dep rock | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 143 | 0.40 | 0.94 | 0.235 | 281 | 0.42 | 402 | 9 | 6.3 | 29 | 80 | 74 | 56 | 26 | 3.3 | 3.3 | — |
| 142 | 0.59 | 0.30 | 0.130 | 108 | 0.44 | 236 | 9 | 5.5 | 23 | 87 | 78 | 61 | 32 | 4.9 | 6.8 | — |
| 140 | 0.55 | 0.91 | 0.272 | 294 | 0.58 | 305 | 9 | 5.8 | 32 | 78 | 72 | 54 | 25 | 2.3 | 4.2 | — |
| 158 | 0.78 | 0.87 | 0.348 | 159 | 0.91 | 474 | 9 | 7.5 | 34 | 72 | 77 | 56 | 26 | 3.2 | 7.7 | — |
| 163 | 0.37 | 0.90 | 0.168 | 183 | 0.32 | 404 | 9 | 6.4 | 24 | 89 | 76 | 57 | 22 | 2.8 | 10.7 | — |
| 144 | 0.87 | 0.55 | 0.120 | 176 | 0.90 | 351 | 9 | 6.5 | 40 | 73 | 79 | 56 | 28 | 4.6 | 8.8 | — |
| 142 | 0.92 | 0.50 | 0.203 | 207 | 0.82 | 140 | 8 | 4.5 | 45 | 77 | 80 | 56 | 28 | 4.9 | 8.3 | border_min |
| 143 | 0.34 | 0.12 | 0.229 | 884 | 0.55 | 274 | 8 | 5.4 | 37 | 79 | 79 | 58 | 29 | 4.5 | 15.7 | deposit_Mm3 |
| 177 | 0.46 | 0.13 | 0.140 | 117 | 0.53 | 323 | 8 | 6.3 | 23 | 94 | 80 | 60 | 24 | 2.8 | 90.1 | deposit_Mm3 |
| 151 | 0.45 | 0.92 | 0.048 | 103 | 0.65 | 333 | 8 | 7.5 | 19 | 82 | 71 | 55 | 25 | 2.5 | 4.0 | v_gorge |
| 140 | 0.74 | 0.33 | 0.167 | 139 | 0.98 | 208 | 8 | 5.6 | 31 | 77 | 75 | 56 | 28 | 3.1 | 12.8 | deposit_Mm3 |
| 138 | 0.46 | 0.48 | 0.083 | 1135 | 0.90 | 386 | 8 | 6.9 | 39 | 63 | 65 | 47 | 22 | 3.2 | 31.6 | deposit_Mm3 |
