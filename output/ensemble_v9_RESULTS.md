# Ensemble v9 — v8 with the Voellmy drag weighted by the solids fraction (dossier §22)

200 Latin-hypercube samples over 9 inputs (v7's eight + f_wl log-uniform 0.3–1.0 × A/stage on km 12–22.8, 7 mapped stations, A/stage median 174 m, range 96–189; model was 50 m); ramp km 6–12; T_END 3.25 h; observables as v6.

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
| bulk deposition km 0-199, Mm3 | — | ≤ 12.0 |


## Result: 200 runs, **0 satisfy all 11 observables**

| observable | met by |
|---|---|
| border_min | 63 / 200 |
| syabru_min | 49 / 200 |
| v_gorge | 27 / 200 |
| erosion_Mm3 | 196 / 200 |
| stage_gorge | 18 / 200 |
| stage_syabru | 11 / 200 |
| stage_hakubesi | 21 / 200 |
| stage_to_betra | 19 / 200 |
| stage_betra_gal | 17 / 200 |
| stage_galchhi | 13 / 200 |
| deposit_Mm3 | 140 / 200 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 21 |
| border_min + v_gorge | 7 |
| border_min + erosion_Mm3 | 63 |
| border_min + stage_gorge | 1 |
| border_min + stage_syabru | 0 |
| border_min + stage_hakubesi | 0 |
| border_min + stage_to_betra | 0 |
| border_min + stage_betra_gal | 0 |
| border_min + stage_galchhi | 9 |
| border_min + deposit_Mm3 | 29 |
| syabru_min + v_gorge | 27 |
| syabru_min + erosion_Mm3 | 45 |
| syabru_min + stage_gorge | 18 |
| syabru_min + stage_syabru | 11 |
| syabru_min + stage_hakubesi | 21 |
| syabru_min + stage_to_betra | 19 |
| syabru_min + stage_betra_gal | 17 |
| syabru_min + stage_galchhi | 12 |
| syabru_min + deposit_Mm3 | 17 |
| v_gorge + erosion_Mm3 | 25 |
| v_gorge + stage_gorge | 13 |
| v_gorge + stage_syabru | 9 |
| v_gorge + stage_hakubesi | 14 |
| v_gorge + stage_to_betra | 13 |
| v_gorge + stage_betra_gal | 12 |
| v_gorge + stage_galchhi | 7 |
| v_gorge + deposit_Mm3 | 9 |
| erosion_Mm3 + stage_gorge | 14 |
| erosion_Mm3 + stage_syabru | 9 |
| erosion_Mm3 + stage_hakubesi | 17 |
| erosion_Mm3 + stage_to_betra | 15 |
| erosion_Mm3 + stage_betra_gal | 14 |
| erosion_Mm3 + stage_galchhi | 13 |
| erosion_Mm3 + deposit_Mm3 | 137 |
| stage_gorge + stage_syabru | 11 |
| stage_gorge + stage_hakubesi | 16 |
| stage_gorge + stage_to_betra | 14 |
| stage_gorge + stage_betra_gal | 11 |
| stage_gorge + stage_galchhi | 2 |
| stage_gorge + deposit_Mm3 | 6 |
| stage_syabru + stage_hakubesi | 11 |
| stage_syabru + stage_to_betra | 8 |
| stage_syabru + stage_betra_gal | 6 |
| stage_syabru + stage_galchhi | 2 |
| stage_syabru + deposit_Mm3 | 3 |
| stage_hakubesi + stage_to_betra | 17 |
| stage_hakubesi + stage_betra_gal | 13 |
| stage_hakubesi + stage_galchhi | 2 |
| stage_hakubesi + deposit_Mm3 | 6 |
| stage_to_betra + stage_betra_gal | 15 |
| stage_to_betra + stage_galchhi | 1 |
| stage_to_betra + deposit_Mm3 | 7 |
| stage_betra_gal + stage_galchhi | 0 |
| stage_betra_gal + deposit_Mm3 | 6 |
| stage_galchhi + deposit_Mm3 | 6 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | met | border min | v_gorge | gorge m | hakubesi m | galchhi m | deposit | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115.1 | 0.29 | 0.28 | 0.95 | 873 | 6.3 | 0.59 | 9 | 4.9 | 40 | 67 | 48 | 15.7 | 9.4 | border_min, stage_galchhi |
| 99.7 | 0.81 | 0.26 | 0.79 | 182 | 2.9 | 0.54 | 8 | 5.0 | 35 | 63 | 43 | 13.5 | 8.9 | border_min, stage_syabru, stage_galchhi |
| 131.9 | 0.74 | 0.23 | 0.61 | 108 | 9.0 | 0.86 | 8 | 5.3 | 26 | 74 | 53 | 16.3 | 21.8 | border_min, stage_galchhi, deposit_Mm3 |
| 117.8 | 0.61 | 0.25 | 0.79 | 357 | 6.8 | 0.48 | 8 | 4.7 | 37 | 69 | 49 | 14.7 | 16.8 | border_min, stage_galchhi, deposit_Mm3 |
| 146.3 | 0.52 | 0.33 | 0.27 | 402 | 1.4 | 0.48 | 8 | 4.5 | 43 | 89 | 56 | 9.9 | 75.7 | border_min, stage_betra_gal, deposit_Mm3 |
| 141.9 | 0.62 | 0.31 | 0.92 | 157 | 9.3 | 0.90 | 8 | 5.3 | 26 | 80 | 59 | 19.3 | 11.0 | border_min, erosion_Mm3, stage_galchhi |
| 124.7 | 0.89 | 0.24 | 0.27 | 200 | 5.8 | 0.33 | 8 | 4.3 | 38 | 76 | 52 | 15.8 | 16.9 | border_min, stage_galchhi, deposit_Mm3 |
| 139.3 | 0.34 | 0.29 | 0.51 | 474 | 5.5 | 0.52 | 7 | 4.6 | 36 | 79 | 52 | 10.2 | 65.0 | border_min, stage_betra_gal, stage_galchhi, deposit_Mm3 |
| 107.9 | 0.77 | 0.18 | 0.49 | 1455 | 8.2 | 0.40 | 7 | 4.7 | 44 | 62 | 42 | 12.9 | 19.4 | border_min, stage_syabru, stage_galchhi, deposit_Mm3 |
| 130.5 | 0.91 | 0.21 | 0.88 | 233 | 2.1 | 0.56 | 7 | 4.7 | 47 | 82 | 55 | 19.0 | 7.1 | border_min, v_gorge, erosion_Mm3, stage_galchhi |
| 101.4 | 0.87 | 0.33 | 0.61 | 593 | 1.5 | 0.78 | 7 | 5.3 | 44 | 62 | 41 | 14.6 | 10.6 | border_min, stage_syabru, stage_hakubesi, stage_galchhi |
| 121.2 | 0.58 | 0.12 | 0.33 | 185 | 4.8 | 0.30 | 7 | 4.5 | 25 | 72 | 46 | 8.7 | 48.3 | border_min, stage_to_betra, stage_betra_gal, deposit_Mm3 |
