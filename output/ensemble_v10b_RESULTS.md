# Ensemble v10b — second-stage sample of v10 inside the box of its thirteen best runs (dossier §24)

300 Latin-hypercube samples over 11 inputs: V_rel log 9.27005e+07–1.67319e+08; w0 lin 0.02–0.95; mu_dry lin 0.0376532–0.35; n_scale lin 0.7–1.4; h_erode lin 1–10; f_fine lin 0.0277047–0.98; xi log 100–1667.53; k_junc lin 1.16108–9.73924; f_wl log 0.304303–0.788978; f_ice lin 0.3–0.9; T_rel log 61.607–600. v9 physics and geometry; T_END 3.25 h; deposition scored ROCK-ONLY (bulk recorded).

| observable | target | tolerance / bounds |
|---|---|---|
| border arrival, min | 7.68 | ±30% |
| Syabrubesi arrival, min | 13.0 | ±50% |
| section-mean peak speed, gorge km 24-34, m/s | 34.0 | ±35% |
| erosion km 0-68, Mm3 | 3.2 | ±60% |
| stage_gorge (fit median 73.3) | — | 58.8–98.9 m |
| stage_syabru (fit median 70.9) | — | 58.7–81.8 m |
| stage_hakubesi (fit median 67.5) | — | 42.0–84.9 m |
| stage_to_betra (fit median 29.0) | — | 20.0–41.3 m |
| stage_betra_gal (fit median 15.3) | — | 9.4–21.1 m |
| stage_galchhi (fit median 7.4) | — | 3.5–9.9 m |
| rock-only bulk deposition km 0-199, Mm3 | — | ≤ 12.0 |


## Result: 300 runs, **1 satisfy all 11 observables**

| observable | met by |
|---|---|
| border_min | 125 / 300 |
| syabru_min | 278 / 300 |
| v_gorge | 197 / 300 |
| erosion_Mm3 | 272 / 300 |
| stage_gorge | 228 / 300 |
| stage_syabru | 135 / 300 |
| stage_hakubesi | 193 / 300 |
| stage_to_betra | 185 / 300 |
| stage_betra_gal | 189 / 300 |
| stage_galchhi | 52 / 300 |
| deposit_Mm3 | 144 / 300 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | border min | v_gorge | gorge m | syabru m | hakubesi m | galchhi m | dep rock | dep bulk | ero | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 159.9 | 0.04 | 0.312 | 0.77 | 188 | 8.3 | 0.34 | 0.81 | 291 | 11 | 5.7 | 22 | 89 | 81 | 63 | 5.7 | 8.7 | 44.7 | 3.1 |  |
| 135.7 | 0.77 | 0.283 | 0.37 | 183 | 1.3 | 0.44 | 0.81 | 429 | 10 | 6.5 | 34 | 72 | 73 | 54 | 15.6 | 5.9 | 29.7 | 2.6 | stage_galchhi |
| 121.3 | 0.17 | 0.200 | 0.92 | 385 | 2.6 | 0.69 | 0.82 | 457 | 10 | 7.7 | 26 | 68 | 65 | 51 | 16.4 | 2.8 | 15.2 | 4.8 | stage_galchhi |
| 129.2 | 0.17 | 0.102 | 0.88 | 291 | 2.0 | 0.41 | 0.70 | 310 | 10 | 5.9 | 25 | 79 | 70 | 55 | 13.7 | 6.5 | 21.2 | 3.6 | stage_galchhi |
| 135.0 | 0.36 | 0.170 | 0.84 | 220 | 5.3 | 0.65 | 0.73 | 528 | 10 | 8.3 | 23 | 73 | 69 | 54 | 13.6 | 6.3 | 22.5 | 4.3 | stage_galchhi |
| 123.9 | 0.83 | 0.061 | 0.36 | 112 | 5.2 | 0.59 | 0.62 | 380 | 10 | 6.8 | 27 | 70 | 64 | 49 | 14.9 | 8.1 | 21.3 | 3.9 | stage_galchhi |
| 140.4 | 0.29 | 0.076 | 0.68 | 348 | 8.7 | 0.32 | 0.78 | 532 | 10 | 7.0 | 26 | 70 | 69 | 53 | 11.4 | 10.0 | 45.7 | 2.6 | stage_galchhi |
| 139.2 | 0.62 | 0.328 | 0.34 | 744 | 6.7 | 0.46 | 0.79 | 328 | 10 | 5.8 | 38 | 72 | 72 | 52 | 12.5 | 10.5 | 49.9 | 2.9 | stage_galchhi |
| 139.8 | 0.27 | 0.114 | 0.92 | 1248 | 3.6 | 0.66 | 0.44 | 572 | 10 | 7.8 | 38 | 63 | 74 | 53 | 18.4 | 8.6 | 15.4 | 4.0 | stage_galchhi |
| 129.9 | 0.73 | 0.255 | 0.70 | 151 | 4.4 | 0.33 | 0.86 | 438 | 10 | 6.4 | 30 | 72 | 72 | 55 | 16.0 | 2.7 | 17.7 | 4.1 | stage_galchhi |
| 122.7 | 0.51 | 0.340 | 0.78 | 297 | 2.1 | 0.36 | 0.89 | 456 | 10 | 6.7 | 31 | 68 | 68 | 51 | 14.8 | 2.6 | 20.9 | 4.0 | stage_galchhi |
| 129.7 | 0.36 | 0.110 | 0.89 | 1287 | 4.7 | 0.58 | 0.79 | 354 | 10 | 6.2 | 38 | 69 | 72 | 52 | 16.6 | 3.6 | 16.5 | 4.9 | stage_galchhi |

## Posterior (passing runs)

| input | median | range |
|---|---|---|
| V_rel Mm3 | 160 | 160 – 160 |
| w0 | 0.0407 | 0.0407 – 0.0407 |
| mu_dry | 0.312 | 0.312 – 0.312 |
| n_scale | 1.33 | 1.33 – 1.33 |
| h_erode | 9.12 | 9.12 – 9.12 |
| f_fine | 0.766 | 0.766 – 0.766 |
| xi | 188 | 188 – 188 |
| k_junc | 8.32 | 8.32 – 8.32 |
| f_wl | 0.336 | 0.336 – 0.336 |
| f_ice | 0.81 | 0.81 – 0.81 |
| T_rel | 291 | 291 – 291 |

## Held out (10 h): passing runs, then the three nearest misses

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | Malekhu (163) / Kalikhola (~337) / Devghat (~2,900) |
|---|---|---|---|---|---|---|---|---|---|---|
| 159.9 | 0.04 | 0.312 | 0.77 | 188 | 8.3 | 0.34 | 0.81 | 291 | 11 | Malekhu 205 (163) / Kalikhola 489 (~337) / Devghat 1,576 m³/s at 568 min (~2,900) |
| 135.7 | 0.77 | 0.283 | 0.37 | 183 | 1.3 | 0.44 | 0.81 | 429 | 10 | Malekhu 114 (163) / Kalikhola 258 (~337) / Devghat 4,068 m³/s at 513 min (~2,900) |
| 121.3 | 0.17 | 0.200 | 0.92 | 385 | 2.6 | 0.69 | 0.82 | 457 | 10 | Malekhu 154 (163) / Kalikhola 349 (~337) / Devghat 2,006 m³/s at 428 min (~2,900) |
| 129.2 | 0.17 | 0.102 | 0.88 | 291 | 2.0 | 0.41 | 0.70 | 310 | 10 | Malekhu 175 (163) / Kalikhola 405 (~337) / Devghat 1,836 m³/s at 516 min (~2,900) |
