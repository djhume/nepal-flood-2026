# Ensemble v8 — v7 plus the Lhende's mapped width as a sampled input (dossier §21)

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
| syabru_min | 38 / 200 |
| v_gorge | 21 / 200 |
| erosion_Mm3 | 197 / 200 |
| stage_gorge | 17 / 200 |
| stage_syabru | 11 / 200 |
| stage_hakubesi | 22 / 200 |
| stage_to_betra | 19 / 200 |
| stage_betra_gal | 19 / 200 |
| stage_galchhi | 8 / 200 |
| deposit_Mm3 | 141 / 200 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 18 |
| border_min + v_gorge | 7 |
| border_min + erosion_Mm3 | 61 |
| border_min + stage_gorge | 5 |
| border_min + stage_syabru | 2 |
| border_min + stage_hakubesi | 5 |
| border_min + stage_to_betra | 4 |
| border_min + stage_betra_gal | 6 |
| border_min + stage_galchhi | 6 |
| border_min + deposit_Mm3 | 29 |
| syabru_min + v_gorge | 21 |
| syabru_min + erosion_Mm3 | 35 |
| syabru_min + stage_gorge | 16 |
| syabru_min + stage_syabru | 10 |
| syabru_min + stage_hakubesi | 21 |
| syabru_min + stage_to_betra | 18 |
| syabru_min + stage_betra_gal | 17 |
| syabru_min + stage_galchhi | 7 |
| syabru_min + deposit_Mm3 | 12 |
| v_gorge + erosion_Mm3 | 20 |
| v_gorge + stage_gorge | 9 |
| v_gorge + stage_syabru | 6 |
| v_gorge + stage_hakubesi | 12 |
| v_gorge + stage_to_betra | 11 |
| v_gorge + stage_betra_gal | 10 |
| v_gorge + stage_galchhi | 4 |
| v_gorge + deposit_Mm3 | 6 |
| erosion_Mm3 + stage_gorge | 15 |
| erosion_Mm3 + stage_syabru | 9 |
| erosion_Mm3 + stage_hakubesi | 19 |
| erosion_Mm3 + stage_to_betra | 17 |
| erosion_Mm3 + stage_betra_gal | 17 |
| erosion_Mm3 + stage_galchhi | 7 |
| erosion_Mm3 + deposit_Mm3 | 138 |
| stage_gorge + stage_syabru | 11 |
| stage_gorge + stage_hakubesi | 16 |
| stage_gorge + stage_to_betra | 14 |
| stage_gorge + stage_betra_gal | 13 |
| stage_gorge + stage_galchhi | 2 |
| stage_gorge + deposit_Mm3 | 5 |
| stage_syabru + stage_hakubesi | 11 |
| stage_syabru + stage_to_betra | 9 |
| stage_syabru + stage_betra_gal | 9 |
| stage_syabru + stage_galchhi | 2 |
| stage_syabru + deposit_Mm3 | 3 |
| stage_hakubesi + stage_to_betra | 18 |
| stage_hakubesi + stage_betra_gal | 15 |
| stage_hakubesi + stage_galchhi | 2 |
| stage_hakubesi + deposit_Mm3 | 7 |
| stage_to_betra + stage_betra_gal | 16 |
| stage_to_betra + stage_galchhi | 2 |
| stage_to_betra + deposit_Mm3 | 6 |
| stage_betra_gal + stage_galchhi | 2 |
| stage_betra_gal + deposit_Mm3 | 7 |
| stage_galchhi + deposit_Mm3 | 4 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | met | border min | v_gorge | gorge m | hakubesi m | galchhi m | deposit | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115.1 | 0.29 | 0.28 | 0.95 | 873 | 6.3 | 0.59 | 9 | 4.9 | 39 | 68 | 49 | 17.9 | 9.4 | border_min, stage_galchhi |
| 141.9 | 0.62 | 0.31 | 0.92 | 157 | 9.3 | 0.90 | 9 | 6.3 | 19 | 82 | 61 | 8.9 | 10.7 | v_gorge, erosion_Mm3 |
| 101.4 | 0.87 | 0.33 | 0.61 | 593 | 1.5 | 0.78 | 9 | 5.5 | 29 | 62 | 44 | 16.0 | 10.4 | stage_syabru, stage_galchhi |
| 139.3 | 0.34 | 0.29 | 0.51 | 474 | 5.5 | 0.52 | 8 | 4.6 | 33 | 80 | 53 | 12.7 | 65.0 | border_min, stage_galchhi, deposit_Mm3 |
| 99.7 | 0.81 | 0.26 | 0.79 | 182 | 2.9 | 0.54 | 8 | 5.8 | 19 | 63 | 45 | 0.4 | 8.6 | v_gorge, stage_syabru, stage_galchhi |
| 117.8 | 0.61 | 0.25 | 0.79 | 357 | 6.8 | 0.48 | 8 | 4.8 | 28 | 71 | 51 | 17.3 | 16.6 | border_min, stage_galchhi, deposit_Mm3 |
| 146.3 | 0.52 | 0.33 | 0.27 | 402 | 1.4 | 0.48 | 8 | 4.5 | 35 | 88 | 56 | 12.3 | 75.4 | border_min, stage_galchhi, deposit_Mm3 |
| 130.5 | 0.91 | 0.21 | 0.88 | 233 | 2.1 | 0.56 | 8 | 5.2 | 23 | 82 | 58 | 20.0 | 6.7 | border_min, erosion_Mm3, stage_galchhi |
| 124.7 | 0.89 | 0.24 | 0.27 | 200 | 5.8 | 0.33 | 8 | 4.9 | 21 | 77 | 55 | 5.6 | 16.5 | border_min, v_gorge, deposit_Mm3 |
| 107.9 | 0.77 | 0.18 | 0.49 | 1455 | 8.2 | 0.40 | 7 | 4.7 | 37 | 62 | 44 | 13.8 | 19.3 | border_min, stage_syabru, stage_galchhi, deposit_Mm3 |
| 131.9 | 0.74 | 0.23 | 0.61 | 108 | 9.0 | 0.86 | 7 | 7.0 | 16 | 75 | 54 | 0.1 | 21.4 | syabru_min, v_gorge, stage_galchhi, deposit_Mm3 |
| 121.2 | 0.58 | 0.12 | 0.33 | 185 | 4.8 | 0.30 | 7 | 5.0 | 19 | 73 | 46 | 0.1 | 48.0 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
