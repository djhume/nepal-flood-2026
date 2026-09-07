# Ensemble v12 — a floodplain that conveys, the arrival on the true stage, and the video at km 74.8 (dossier §25, §26b)

400 Latin-hypercube samples over 14 inputs (v10b stage-2 box, three new inputs at full range): V_rel log 9.27005e+07–1.67319e+08; w0 lin 0.02–0.95; mu_dry lin 0.0376532–0.35; n_scale lin 0.7–1.4; h_erode lin 1–10; f_fine lin 0.0277047–0.98; xi log 100–1667.53; k_junc lin 1.16108–9.73924; f_wl log 0.304303–0.788978; f_ice lin 0.3–0.9; T_rel log 61.607–600; f_fp log 0.5–2; h_bank lin 3–8; n_fp lin 0.06–0.12. v10 physics above km 70; compound section below it; T_END 3.25 h; deposition scored ROCK-ONLY.

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
| **rise74_s** — km 73.6, front → stage +5 m (video ~70 s) | ~70 s | 20–180 s |
| **hold74_m** — km 73.6, stage 260 s after the front | still over the floor | ≥ 5 m |

Reported, NOT scored: stage74_4min_m (video ~10–15 m — a camera 44 m up cannot read a 12 m stage); stage_cam_m, the stage at the camera's own node km 74.8 at 260 s (the clip ends with the water well below the camera, i.e. under 44 m); and v_front_lower, the front over km 73–75 (video ≥ 30 m/s, model ~11 — the front's first appearance is judged by eye at 640×360 and the clip's continuity is unconfirmed).

FFD volume (§26b), reported with the held-out set: excess above base at Devghat over 333–563 min (14:10–18:00 NPT), target ~20 Mm³ at ONE significant figure. A windowed gross excess at one gauge, not a volume balance.


## Result: 400 runs, **0 satisfy all 13 observables**

| observable | met by |
|---|---|
| border_min | 165 / 400 |
| syabru_min | 378 / 400 |
| v_gorge | 258 / 400 |
| erosion_Mm3 | 350 / 400 |
| stage_gorge | 306 / 400 |
| stage_syabru | 175 / 400 |
| stage_hakubesi | 258 / 400 |
| stage_to_betra | 234 / 400 |
| stage_betra_gal | 229 / 400 |
| stage_galchhi | 70 / 400 |
| deposit_Mm3 | 184 / 400 |
| rise74_s | 256 / 400 |
| hold74_m | 302 / 400 |

No sample satisfies everything. Pairs:

| pair | runs meeting both |
|---|---|
| border_min + syabru_min | 148 |
| border_min + v_gorge | 105 |
| border_min + erosion_Mm3 | 150 |
| border_min + stage_gorge | 103 |
| border_min + stage_syabru | 69 |
| border_min + stage_hakubesi | 90 |
| border_min + stage_to_betra | 82 |
| border_min + stage_betra_gal | 98 |
| border_min + stage_galchhi | 29 |
| border_min + deposit_Mm3 | 69 |
| border_min + rise74_s | 93 |
| border_min + hold74_m | 118 |
| syabru_min + v_gorge | 258 |
| syabru_min + erosion_Mm3 | 328 |
| syabru_min + stage_gorge | 302 |
| syabru_min + stage_syabru | 173 |
| syabru_min + stage_hakubesi | 254 |
| syabru_min + stage_to_betra | 232 |
| syabru_min + stage_betra_gal | 224 |
| syabru_min + stage_galchhi | 70 |
| syabru_min + deposit_Mm3 | 181 |
| syabru_min + rise74_s | 255 |
| syabru_min + hold74_m | 299 |
| v_gorge + erosion_Mm3 | 232 |
| v_gorge + stage_gorge | 207 |
| v_gorge + stage_syabru | 125 |
| v_gorge + stage_hakubesi | 164 |
| v_gorge + stage_to_betra | 147 |
| v_gorge + stage_betra_gal | 163 |
| v_gorge + stage_galchhi | 54 |
| v_gorge + deposit_Mm3 | 113 |
| v_gorge + rise74_s | 175 |
| v_gorge + hold74_m | 207 |
| erosion_Mm3 + stage_gorge | 263 |
| erosion_Mm3 + stage_syabru | 152 |
| erosion_Mm3 + stage_hakubesi | 212 |
| erosion_Mm3 + stage_to_betra | 187 |
| erosion_Mm3 + stage_betra_gal | 210 |
| erosion_Mm3 + stage_galchhi | 70 |
| erosion_Mm3 + deposit_Mm3 | 134 |
| erosion_Mm3 + rise74_s | 206 |
| erosion_Mm3 + hold74_m | 252 |
| stage_gorge + stage_syabru | 172 |
| stage_gorge + stage_hakubesi | 247 |
| stage_gorge + stage_to_betra | 220 |
| stage_gorge + stage_betra_gal | 183 |
| stage_gorge + stage_galchhi | 52 |
| stage_gorge + deposit_Mm3 | 149 |
| stage_gorge + rise74_s | 219 |
| stage_gorge + hold74_m | 258 |
| stage_syabru + stage_hakubesi | 175 |
| stage_syabru + stage_to_betra | 155 |
| stage_syabru + stage_betra_gal | 121 |
| stage_syabru + stage_galchhi | 25 |
| stage_syabru + deposit_Mm3 | 88 |
| stage_syabru + rise74_s | 141 |
| stage_syabru + hold74_m | 159 |
| stage_hakubesi + stage_to_betra | 227 |
| stage_hakubesi + stage_betra_gal | 163 |
| stage_hakubesi + stage_galchhi | 30 |
| stage_hakubesi + deposit_Mm3 | 141 |
| stage_hakubesi + rise74_s | 215 |
| stage_hakubesi + hold74_m | 240 |
| stage_to_betra + stage_betra_gal | 154 |
| stage_to_betra + stage_galchhi | 21 |
| stage_to_betra + deposit_Mm3 | 146 |
| stage_to_betra + rise74_s | 217 |
| stage_to_betra + hold74_m | 230 |
| stage_betra_gal + stage_galchhi | 45 |
| stage_betra_gal + deposit_Mm3 | 120 |
| stage_betra_gal + rise74_s | 178 |
| stage_betra_gal + hold74_m | 215 |
| stage_galchhi + deposit_Mm3 | 12 |
| stage_galchhi + rise74_s | 26 |
| stage_galchhi + hold74_m | 56 |
| deposit_Mm3 + rise74_s | 166 |
| deposit_Mm3 + hold74_m | 176 |
| rise74_s + hold74_m | 256 |

Best runs (most observables met):

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | f_fp | h_bank | n_fp | met | border min | v_gorge | gorge m | syabru m | hakubesi m | galchhi m | rise74 s | hold74 m | dep rock | dep bulk | ero | [y@4min] | [y@cam] | [v front 73-75] | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 139.1 | 0.03 | 0.233 | 0.72 | 397 | 4.6 | 0.49 | 0.68 | 272 | 1.77 | 7.4 | 0.119 | 12 | 5.5 | 30 | 79 | 71 | 54 | 9.5 | 160 | 9.2 | 13.9 | 43.6 | 2.3 | 8.5 | 4.4 | 11 | deposit_Mm3 |
| 119.8 | 0.64 | 0.116 | 0.50 | 1465 | 1.7 | 0.51 | 0.80 | 427 | 0.61 | 5.8 | 0.076 | 12 | 6.8 | 41 | 61 | 61 | 45 | 15.2 | 70 | 14.3 | 6.5 | 32.1 | 3.0 | 13.8 | 21.3 | 18 | stage_galchhi |
| 160.4 | 0.41 | 0.039 | 0.34 | 483 | 6.3 | 0.52 | 0.34 | 429 | 1.98 | 4.0 | 0.113 | 12 | 6.5 | 34 | 76 | 76 | 55 | 7.2 | 165 | 7.7 | 59.3 | 89.9 | 3.2 | 7.3 | 4.5 | 12 | deposit_Mm3 |
| 122.5 | 0.92 | 0.208 | 0.03 | 465 | 3.9 | 0.38 | 0.67 | 408 | 0.71 | 6.7 | 0.076 | 12 | 6.2 | 38 | 66 | 70 | 50 | 17.2 | 60 | 17.2 | 7.5 | 16.9 | 4.7 | 16.5 | 24.6 | 18 | stage_galchhi |
| 116.7 | 0.58 | 0.243 | 0.69 | 602 | 4.0 | 0.74 | 0.88 | 321 | 1.03 | 4.5 | 0.081 | 12 | 6.4 | 33 | 65 | 59 | 45 | 13.6 | 100 | 12.2 | 3.1 | 24.0 | 3.7 | 11.6 | 13.3 | 14 | stage_galchhi |
| 124.6 | 0.40 | 0.258 | 0.84 | 182 | 5.3 | 0.40 | 0.42 | 545 | 1.13 | 5.7 | 0.084 | 12 | 8.2 | 21 | 70 | 66 | 51 | 8.8 | 160 | 9.0 | 11.4 | 19.5 | 4.1 | 8.0 | 4.4 | 11 | v_gorge |
| 128.8 | 0.51 | 0.296 | 0.73 | 552 | 9.2 | 0.71 | 0.85 | 310 | 0.71 | 5.0 | 0.113 | 12 | 6.1 | 35 | 66 | 68 | 50 | 16.7 | 80 | 15.1 | 4.1 | 26.1 | 4.0 | 14.3 | 18.4 | 17 | stage_galchhi |
| 159.2 | 0.70 | 0.137 | 0.46 | 156 | 3.8 | 0.71 | 0.82 | 347 | 1.17 | 7.2 | 0.074 | 12 | 6.3 | 30 | 86 | 80 | 61 | 16.6 | 90 | 13.9 | 7.0 | 38.0 | 2.4 | 13.1 | 12.1 | 14 | stage_galchhi |
| 113.0 | 0.21 | 0.336 | 0.88 | 269 | 5.3 | 0.35 | 0.36 | 590 | 0.53 | 7.6 | 0.063 | 12 | 8.2 | 22 | 63 | 61 | 48 | 15.4 | 130 | 11.3 | 11.6 | 18.1 | 4.3 | 10.6 | 7.3 | 11 | stage_galchhi |
| 131.5 | 0.65 | 0.250 | 0.76 | 283 | 7.9 | 0.53 | 0.44 | 500 | 1.03 | 4.6 | 0.069 | 12 | 7.2 | 32 | 64 | 71 | 52 | 16.0 | 90 | 14.6 | 10.4 | 18.6 | 5.0 | 13.8 | 18.0 | 17 | stage_galchhi |
| 131.7 | 0.73 | 0.083 | 0.59 | 293 | 9.1 | 0.46 | 0.86 | 467 | 1.46 | 4.3 | 0.071 | 12 | 6.8 | 34 | 62 | 70 | 51 | 13.2 | 85 | 13.8 | 3.5 | 23.3 | 4.2 | 13.1 | 18.1 | 17 | stage_galchhi |
| 114.8 | 0.69 | 0.291 | 0.81 | 714 | 1.8 | 0.78 | 0.87 | 386 | 0.74 | 6.5 | 0.106 | 12 | 7.0 | 37 | 59 | 60 | 45 | 17.2 | 70 | 15.6 | 1.9 | 13.4 | 5.0 | 14.9 | 20.6 | 18 | stage_galchhi |

## Held out (10 h): passing runs, then the nearest misses

| V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | f_fp | h_bank | n_fp | met | Malekhu (163) / Kalikhola (~337) / Devghat (~2,900) / vol (~20 Mm³) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 139.1 | 0.03 | 0.233 | 0.72 | 397 | 4.6 | 0.49 | 0.68 | 272 | 1.77 | 7.4 | 0.119 | 12 | Malekhu 166 (163) / Kalikhola inf (~337) / Devghat 1,374 m³/s at 461 min (~2,900) / vol 0.9 Mm³ (~20) |
| 119.8 | 0.64 | 0.116 | 0.50 | 1465 | 1.7 | 0.51 | 0.80 | 427 | 0.61 | 5.8 | 0.076 | 12 | Malekhu 107 (163) / Kalikhola 267 (~337) / Devghat 3,793 m³/s at 479 min (~2,900) / vol 31.6 Mm³ (~20) |
| 160.4 | 0.41 | 0.039 | 0.34 | 483 | 6.3 | 0.52 | 0.34 | 429 | 1.98 | 4.0 | 0.113 | 12 | Malekhu 164 (163) / Kalikhola 578 (~337) / Devghat 1,395 m³/s at 530 min (~2,900) / vol 1.3 Mm³ (~20) |
