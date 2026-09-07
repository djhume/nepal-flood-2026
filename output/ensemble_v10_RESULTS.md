# Ensemble v10 — rock-only deposition, an ice-capable friction floor, a sampled release duration (dossier §23)

300 Latin-hypercube samples over 11 inputs: V_rel log 1e+06–2e+08; w0 lin 0.02–0.95; mu_dry lin 0.03–0.35; n_scale lin 0.7–1.4; h_erode lin 1–10; f_fine lin 0–0.98; xi log 100–2000; k_junc lin 1–10; f_wl log 0.3–1; f_ice lin 0.3–0.9; T_rel log 60–600. v9 physics and geometry; T_END 3.25 h; deposition scored ROCK-ONLY (bulk recorded).

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


## Result: 300 runs, **0 satisfy all 11 observables**

| observable | met by |
|---|---|
| border_min | 82 / 300 |
| syabru_min | 76 / 300 |
| v_gorge | 44 / 300 |
| erosion_Mm3 | 291 / 300 |
| stage_gorge | 31 / 300 |
| stage_syabru | 16 / 300 |
| stage_hakubesi | 34 / 300 |
| stage_to_betra | 33 / 300 |
| stage_betra_gal | 37 / 300 |
| stage_galchhi | 30 / 300 |
| deposit_Mm3 | 257 / 300 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 40 |
| border_min + v_gorge | 22 |
| border_min + erosion_Mm3 | 77 |
| border_min + stage_gorge | 15 |
| border_min + stage_syabru | 10 |
| border_min + stage_hakubesi | 15 |
| border_min + stage_to_betra | 15 |
| border_min + stage_betra_gal | 17 |
| border_min + stage_galchhi | 18 |
| border_min + deposit_Mm3 | 66 |
| syabru_min + v_gorge | 44 |
| syabru_min + erosion_Mm3 | 67 |
| syabru_min + stage_gorge | 30 |
| syabru_min + stage_syabru | 16 |
| syabru_min + stage_hakubesi | 33 |
| syabru_min + stage_to_betra | 32 |
| syabru_min + stage_betra_gal | 35 |
| syabru_min + stage_galchhi | 27 |
| syabru_min + deposit_Mm3 | 46 |
| v_gorge + erosion_Mm3 | 36 |
| v_gorge + stage_gorge | 20 |
| v_gorge + stage_syabru | 12 |
| v_gorge + stage_hakubesi | 20 |
| v_gorge + stage_to_betra | 21 |
| v_gorge + stage_betra_gal | 22 |
| v_gorge + stage_galchhi | 18 |
| v_gorge + deposit_Mm3 | 27 |
| erosion_Mm3 + stage_gorge | 24 |
| erosion_Mm3 + stage_syabru | 11 |
| erosion_Mm3 + stage_hakubesi | 27 |
| erosion_Mm3 + stage_to_betra | 26 |
| erosion_Mm3 + stage_betra_gal | 29 |
| erosion_Mm3 + stage_galchhi | 29 |
| erosion_Mm3 + deposit_Mm3 | 248 |
| stage_gorge + stage_syabru | 16 |
| stage_gorge + stage_hakubesi | 26 |
| stage_gorge + stage_to_betra | 25 |
| stage_gorge + stage_betra_gal | 24 |
| stage_gorge + stage_galchhi | 7 |
| stage_gorge + deposit_Mm3 | 19 |
| stage_syabru + stage_hakubesi | 16 |
| stage_syabru + stage_to_betra | 15 |
| stage_syabru + stage_betra_gal | 14 |
| stage_syabru + stage_galchhi | 2 |
| stage_syabru + deposit_Mm3 | 11 |
| stage_hakubesi + stage_to_betra | 32 |
| stage_hakubesi + stage_betra_gal | 31 |
| stage_hakubesi + stage_galchhi | 4 |
| stage_hakubesi + deposit_Mm3 | 20 |
| stage_to_betra + stage_betra_gal | 31 |
| stage_to_betra + stage_galchhi | 4 |
| stage_to_betra + deposit_Mm3 | 20 |
| stage_betra_gal + stage_galchhi | 4 |
| stage_betra_gal + deposit_Mm3 | 25 |
| stage_galchhi + deposit_Mm3 | 20 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | border min | v_gorge | gorge m | syabru m | hakubesi m | galchhi m | dep rock | dep bulk | ero | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 128.8 | 0.87 | 0.171 | 0.14 | 145 | 7.9 | 0.54 | 0.86 | 466 | 10 | 7.0 | 37 | 60 | 69 | 49 | 17.6 | 4.1 | 22.8 | 3.3 | stage_galchhi |
| 122.8 | 0.81 | 0.132 | 0.45 | 131 | 8.7 | 0.46 | 0.82 | 501 | 10 | 7.3 | 28 | 63 | 63 | 49 | 14.5 | 3.9 | 20.6 | 3.8 | stage_galchhi |
| 128.5 | 0.14 | 0.170 | 0.92 | 187 | 6.4 | 0.48 | 0.74 | 198 | 10 | 5.4 | 21 | 78 | 71 | 56 | 7.2 | 4.1 | 15.1 | 4.2 | v_gorge |
| 141.0 | 0.91 | 0.303 | 0.31 | 103 | 5.7 | 0.36 | 0.80 | 557 | 9 | 7.0 | 35 | 67 | 78 | 57 | 19.2 | 4.3 | 15.9 | 5.6 | erosion_Mm3, stage_galchhi |
| 146.2 | 0.70 | 0.077 | 0.69 | 335 | 7.4 | 0.71 | 0.41 | 312 | 9 | 6.0 | 35 | 77 | 78 | 57 | 18.0 | 12.7 | 21.6 | 3.7 | stage_galchhi, deposit_Mm3 |
| 133.4 | 0.04 | 0.311 | 0.76 | 196 | 8.5 | 0.34 | 0.81 | 289 | 9 | 5.9 | 20 | 77 | 68 | 52 | 1.3 | 7.4 | 38.1 | 3.1 | v_gorge, stage_galchhi |
| 149.7 | 0.11 | 0.281 | 0.57 | 592 | 7.8 | 0.55 | 0.41 | 287 | 9 | 5.5 | 36 | 77 | 74 | 54 | 12.0 | 42.7 | 72.5 | 2.9 | stage_galchhi, deposit_Mm3 |
| 110.6 | 0.91 | 0.317 | 0.84 | 300 | 2.6 | 0.62 | 0.51 | 367 | 9 | 6.6 | 46 | 61 | 65 | 46 | 16.7 | 4.2 | 7.6 | 7.5 | erosion_Mm3, stage_galchhi |
| 121.2 | 0.57 | 0.190 | 0.53 | 362 | 5.1 | 0.59 | 0.90 | 82 | 9 | 3.8 | 35 | 71 | 64 | 48 | 12.1 | 4.0 | 36.1 | 2.8 | border_min, stage_galchhi |
| 99.2 | 0.60 | 0.160 | 0.79 | 227 | 7.6 | 0.41 | 0.82 | 270 | 9 | 5.7 | 27 | 59 | 55 | 42 | 12.3 | 2.8 | 14.3 | 4.2 | stage_syabru, stage_galchhi |
| 156.3 | 0.44 | 0.343 | 0.62 | 269 | 8.1 | 0.47 | 0.83 | 178 | 9 | 4.4 | 29 | 87 | 80 | 60 | 14.8 | 8.3 | 47.9 | 2.6 | border_min, stage_galchhi |
| 145.0 | 0.72 | 0.166 | 0.80 | 1160 | 2.2 | 0.55 | 0.43 | 318 | 9 | 5.7 | 45 | 81 | 83 | 58 | 19.4 | 8.2 | 14.5 | 3.5 | stage_syabru, stage_galchhi |

## Held out (10 h): passing runs, then the three nearest misses

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | met | Malekhu (163) / Kalikhola (~337) / Devghat (~2,900) |
|---|---|---|---|---|---|---|---|---|---|---|
| 128.8 | 0.87 | 0.171 | 0.14 | 145 | 7.9 | 0.54 | 0.86 | 466 | 10 | Malekhu 85 (163) / Kalikhola 180 (~337) / Devghat 5,900 m³/s at 307 min (~2,900) |
| 122.8 | 0.81 | 0.132 | 0.45 | 131 | 8.7 | 0.46 | 0.82 | 501 | 10 | Malekhu 130 (163) / Kalikhola 292 (~337) / Devghat 3,697 m³/s at 596 min (~2,900) |
| 128.5 | 0.14 | 0.170 | 0.92 | 187 | 6.4 | 0.48 | 0.74 | 198 | 10 | Malekhu 197 (163) / Kalikhola inf (~337) / Devghat 1,646 m³/s at 514 min (~2,900) |
