# Ensemble v7 — v6 plus a Voellmy turbulent term and a fitted junction loss (dossier §20)

200 Latin-hypercube samples over 8 inputs (v6's six + xi log-uniform 100–2,000 m/s², k_junc uniform 1–10); T_END 3.25 h; geometry and observables as v6.

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
| border_min | 64 / 200 |
| syabru_min | 46 / 200 |
| v_gorge | 23 / 200 |
| erosion_Mm3 | 199 / 200 |
| stage_gorge | 18 / 200 |
| stage_syabru | 15 / 200 |
| stage_hakubesi | 24 / 200 |
| stage_to_betra | 18 / 200 |
| stage_betra_gal | 20 / 200 |
| stage_galchhi | 7 / 200 |
| deposit_Mm3 | 142 / 200 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 14 |
| border_min + v_gorge | 3 |
| border_min + erosion_Mm3 | 64 |
| border_min + stage_gorge | 2 |
| border_min + stage_syabru | 1 |
| border_min + stage_hakubesi | 1 |
| border_min + stage_to_betra | 1 |
| border_min + stage_betra_gal | 4 |
| border_min + stage_galchhi | 4 |
| border_min + deposit_Mm3 | 32 |
| syabru_min + v_gorge | 23 |
| syabru_min + erosion_Mm3 | 45 |
| syabru_min + stage_gorge | 18 |
| syabru_min + stage_syabru | 15 |
| syabru_min + stage_hakubesi | 24 |
| syabru_min + stage_to_betra | 18 |
| syabru_min + stage_betra_gal | 18 |
| syabru_min + stage_galchhi | 7 |
| syabru_min + deposit_Mm3 | 14 |
| v_gorge + erosion_Mm3 | 22 |
| v_gorge + stage_gorge | 10 |
| v_gorge + stage_syabru | 9 |
| v_gorge + stage_hakubesi | 13 |
| v_gorge + stage_to_betra | 10 |
| v_gorge + stage_betra_gal | 9 |
| v_gorge + stage_galchhi | 4 |
| v_gorge + deposit_Mm3 | 6 |
| erosion_Mm3 + stage_gorge | 17 |
| erosion_Mm3 + stage_syabru | 14 |
| erosion_Mm3 + stage_hakubesi | 23 |
| erosion_Mm3 + stage_to_betra | 17 |
| erosion_Mm3 + stage_betra_gal | 19 |
| erosion_Mm3 + stage_galchhi | 7 |
| erosion_Mm3 + deposit_Mm3 | 141 |
| stage_gorge + stage_syabru | 15 |
| stage_gorge + stage_hakubesi | 16 |
| stage_gorge + stage_to_betra | 13 |
| stage_gorge + stage_betra_gal | 13 |
| stage_gorge + stage_galchhi | 2 |
| stage_gorge + deposit_Mm3 | 5 |
| stage_syabru + stage_hakubesi | 15 |
| stage_syabru + stage_to_betra | 12 |
| stage_syabru + stage_betra_gal | 12 |
| stage_syabru + stage_galchhi | 1 |
| stage_syabru + deposit_Mm3 | 4 |
| stage_hakubesi + stage_to_betra | 18 |
| stage_hakubesi + stage_betra_gal | 16 |
| stage_hakubesi + stage_galchhi | 1 |
| stage_hakubesi + deposit_Mm3 | 7 |
| stage_to_betra + stage_betra_gal | 16 |
| stage_to_betra + stage_galchhi | 1 |
| stage_to_betra + deposit_Mm3 | 5 |
| stage_betra_gal + stage_galchhi | 1 |
| stage_betra_gal + deposit_Mm3 | 7 |
| stage_galchhi + deposit_Mm3 | 3 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | met | border min | v_gorge | gorge m | hakubesi m | galchhi m | deposit | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115.7 | 0.29 | 0.28 | 0.95 | 874 | 6.3 | 9 | 4.4 | 43 | 74 | 51 | 18.1 | 9.1 | border_min, stage_galchhi |
| 101.9 | 0.87 | 0.33 | 0.62 | 592 | 1.6 | 9 | 4.6 | 32 | 69 | 46 | 16.0 | 10.0 | border_min, stage_galchhi |
| 139.8 | 0.34 | 0.29 | 0.51 | 469 | 5.5 | 8 | 4.2 | 37 | 87 | 55 | 12.7 | 65.6 | border_min, stage_galchhi, deposit_Mm3 |
| 100.3 | 0.81 | 0.26 | 0.79 | 182 | 2.9 | 8 | 5.2 | 19 | 66 | 46 | 1.5 | 8.4 | border_min, v_gorge, stage_galchhi |
| 108.2 | 0.77 | 0.18 | 0.49 | 1450 | 8.2 | 8 | 4.5 | 39 | 66 | 45 | 14.2 | 19.6 | border_min, stage_galchhi, deposit_Mm3 |
| 134.2 | 0.73 | 0.23 | 0.61 | 108 | 9.0 | 8 | 5.5 | 17 | 84 | 58 | 0.1 | 21.8 | v_gorge, stage_galchhi, deposit_Mm3 |
| 120.5 | 0.60 | 0.25 | 0.79 | 354 | 6.8 | 8 | 4.4 | 30 | 77 | 53 | 17.9 | 16.7 | border_min, stage_galchhi, deposit_Mm3 |
| 149.4 | 0.51 | 0.33 | 0.26 | 399 | 1.4 | 8 | 4.2 | 38 | 96 | 59 | 12.5 | 78.3 | border_min, stage_galchhi, deposit_Mm3 |
| 128.1 | 0.92 | 0.21 | 0.88 | 232 | 2.1 | 8 | 4.7 | 25 | 85 | 59 | 19.9 | 6.3 | border_min, erosion_Mm3, stage_galchhi |
| 126.1 | 0.89 | 0.24 | 0.27 | 200 | 5.8 | 8 | 4.9 | 21 | 80 | 55 | 7.9 | 16.4 | border_min, v_gorge, deposit_Mm3 |
| 111.1 | 0.21 | 0.30 | 0.76 | 1756 | 9.3 | 7 | 4.4 | 46 | 66 | 44 | 13.1 | 31.2 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
| 145.3 | 0.62 | 0.31 | 0.92 | 156 | 9.3 | 7 | 4.8 | 21 | 91 | 65 | 13.2 | 10.4 | border_min, v_gorge, stage_syabru, stage_galchhi |
