# Ensemble v6 — stages as observables (PLAN §10)

200 Latin-hypercube samples; T_END 3.25 h; junction cap 60 m; Kyirong arm as wedge (1.0, 0.017, 60.0); widths from the trimline sections on km 22.8–108.

| reach | old width (median, m) | trimline width (median, m) |
|---|---|---|
| stage_gorge 22.8–35.6 km | 50 | 120 |
| stage_syabru 35.6–40.0 km | 200 | 123 |
| stage_hakubesi 40.0–46.0 km | 60 | 86 |
| stage_to_betra 46.0–70.0 km | 60 | 171 |
| stage_betra_gal 70.0–108.0 km | 114 | 271 |
| stage_galchhi 107.0–108.2 km | 119 | 267 |

| observable | target | tolerance / bounds |
|---|---|---|
| border arrival, min | 7.68 | ±30% |
| Syabrubesi arrival, min | 13.0 | ±50% |
| section-mean peak speed, gorge km 24-34, m/s | 34.0 | ±35% |
| erosion km 0-68, Mm3 | 3.2 | ±60% |
| stage_gorge (fit median 73.3, 123 stations) | — | 58.8–98.9 m |
| stage_syabru (fit median 70.9, 44 stations) | — | 58.7–81.8 m |
| stage_hakubesi (fit median 67.5, 53 stations) | — | 42.0–84.9 m |
| stage_to_betra (fit median 29.0, 213 stations) | — | 20.0–41.3 m |
| stage_betra_gal (fit median 15.3, 370 stations) | — | 9.4–21.1 m |
| stage_galchhi (fit median 7.4, 12 stations) | — | 3.5–9.9 m |
| bulk deposition km 0-199, Mm3 | — | ≤ 12.0 |


## Result: 200 runs, **0 satisfy all 11 observables**

| observable | met by |
|---|---|
| border_min | 64 / 200 |
| syabru_min | 77 / 200 |
| v_gorge | 37 / 200 |
| erosion_Mm3 | 197 / 200 |
| stage_gorge | 20 / 200 |
| stage_syabru | 10 / 200 |
| stage_hakubesi | 25 / 200 |
| stage_to_betra | 22 / 200 |
| stage_betra_gal | 18 / 200 |
| stage_galchhi | 37 / 200 |
| deposit_Mm3 | 140 / 200 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 30 |
| border_min + v_gorge | 21 |
| border_min + erosion_Mm3 | 64 |
| border_min + stage_gorge | 0 |
| border_min + stage_syabru | 0 |
| border_min + stage_hakubesi | 0 |
| border_min + stage_to_betra | 0 |
| border_min + stage_betra_gal | 0 |
| border_min + stage_galchhi | 22 |
| border_min + deposit_Mm3 | 43 |
| syabru_min + v_gorge | 37 |
| syabru_min + erosion_Mm3 | 74 |
| syabru_min + stage_gorge | 20 |
| syabru_min + stage_syabru | 10 |
| syabru_min + stage_hakubesi | 25 |
| syabru_min + stage_to_betra | 22 |
| syabru_min + stage_betra_gal | 18 |
| syabru_min + stage_galchhi | 37 |
| syabru_min + deposit_Mm3 | 27 |
| v_gorge + erosion_Mm3 | 37 |
| v_gorge + stage_gorge | 1 |
| v_gorge + stage_syabru | 0 |
| v_gorge + stage_hakubesi | 0 |
| v_gorge + stage_to_betra | 0 |
| v_gorge + stage_betra_gal | 0 |
| v_gorge + stage_galchhi | 28 |
| v_gorge + deposit_Mm3 | 12 |
| erosion_Mm3 + stage_gorge | 18 |
| erosion_Mm3 + stage_syabru | 10 |
| erosion_Mm3 + stage_hakubesi | 22 |
| erosion_Mm3 + stage_to_betra | 20 |
| erosion_Mm3 + stage_betra_gal | 16 |
| erosion_Mm3 + stage_galchhi | 37 |
| erosion_Mm3 + deposit_Mm3 | 137 |
| stage_gorge + stage_syabru | 9 |
| stage_gorge + stage_hakubesi | 17 |
| stage_gorge + stage_to_betra | 17 |
| stage_gorge + stage_betra_gal | 14 |
| stage_gorge + stage_galchhi | 4 |
| stage_gorge + deposit_Mm3 | 6 |
| stage_syabru + stage_hakubesi | 9 |
| stage_syabru + stage_to_betra | 9 |
| stage_syabru + stage_betra_gal | 7 |
| stage_syabru + stage_galchhi | 2 |
| stage_syabru + deposit_Mm3 | 3 |
| stage_hakubesi + stage_to_betra | 22 |
| stage_hakubesi + stage_betra_gal | 16 |
| stage_hakubesi + stage_galchhi | 4 |
| stage_hakubesi + deposit_Mm3 | 7 |
| stage_to_betra + stage_betra_gal | 14 |
| stage_to_betra + stage_galchhi | 4 |
| stage_to_betra + deposit_Mm3 | 6 |
| stage_betra_gal + stage_galchhi | 0 |
| stage_betra_gal + deposit_Mm3 | 6 |
| stage_galchhi + deposit_Mm3 | 15 |

Nearest misses (most observables met):

| V Mm3 | w0 | mu | f_fine | met | failed |
|---|---|---|---|---|---|
| 99.6 | 0.81 | 0.26 | 0.79 | 8 | border_min, v_gorge, stage_galchhi |
| 115.5 | 0.29 | 0.28 | 0.95 | 8 | border_min, v_gorge, stage_galchhi |
| 102.0 | 0.87 | 0.33 | 0.62 | 8 | border_min, v_gorge, stage_galchhi |
| 107.8 | 0.77 | 0.18 | 0.49 | 7 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
| 109.4 | 0.21 | 0.30 | 0.76 | 7 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
| 86.4 | 0.56 | 0.35 | 0.88 | 7 | border_min, v_gorge, stage_syabru, stage_galchhi |
| 112.4 | 0.23 | 0.19 | 0.37 | 7 | border_min, v_gorge, stage_betra_gal, deposit_Mm3 |
| 103.6 | 0.61 | 0.14 | 0.12 | 7 | border_min, v_gorge, stage_betra_gal, deposit_Mm3 |
| 125.6 | 0.89 | 0.24 | 0.28 | 7 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
| 122.1 | 0.58 | 0.12 | 0.33 | 7 | border_min, v_gorge, stage_galchhi, deposit_Mm3 |
