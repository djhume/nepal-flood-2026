# Up-valley wedge volume — results (6 Sept 2026, evening)

DEM: Copernicus GLO-30 (TanDEM-X, 2011-2015, ~30 m, ~2-4 m vertical); 61 stations at 100 m; transects ±600 m; junction datum (28.2781, 85.377). The bed used is the upstream-minimum envelope of the transect minima (a river bed rises monotonically and a 30 m DEM in a gorge errs high), and 10 of 61 stations whose transect minimum sits >10 m above the envelope borrow the cross-section shape of their nearest sound neighbour. Bed at the junction 1791 m (Google Earth 1815); mean grade to 6 km 2.97%.

Bed envelope: 0.0 km 1791 m, 0.5 km 1804 m, 1.0 km 1815 m, 1.5 km 1825 m, 2.0 km 1841 m, 2.5 km 1850 m, 3.0 km 1859 m, 3.5 km 1889 m, 4.0 km 1911 m, 4.5 km 1911 m, 5.0 km 1911 m, 5.5 km 1950 m, 6.0 km 1969 m

## Where the bed reaches the stagnation level

| level | bed envelope reaches it at | agent's SRTM/ASTER read (dossier 16a) |
|---|---|---|
| 1915 m | 5.3 km | 1,920–1,930 m met at ~4.5–5 km, ±0.7 km |
| 1920 m | 5.4 km | 1,920–1,930 m met at ~4.5–5 km, ±0.7 km |
| 1925 m | 5.4 km | 1,920–1,930 m met at ~4.5–5 km, ±0.7 km |
| 1930 m | 5.4 km | 1,920–1,930 m met at ~4.5–5 km, ±0.7 km |

Dave's Google Earth trace put the 1,920–1,930 m contour at 3.5 km; the imagery limit is 4.6 km (agent chainage, ~0.4 km longer than ours at the same point).

## Stored volume at peak, by reading

| reading | surface | volume | width at 1 / 2 / 4 km |
|---|---|---|---|
| pond | level 1915 m, to 5.3 km | **58.6 Mm³** | 240 / 150 / 60 m |
| pond | level 1920 m, to 5.4 km | **63.9 Mm³** | 240 / 150 / 90 m |
| pond | level 1925 m, to 5.4 km | **69.2 Mm³** | 240 / 150 / 90 m |
| pond | level 1930 m, to 5.4 km | **73.7 Mm³** | 240 / 150 / 90 m |
| tongue, linear | 1,925 m at the junction, touching the bed at 3.5 km | **55.3 Mm³** | 240 / 150 / 0 m |
| tongue, concave, p=2 | 1,925 m at the junction, touching the bed at 3.5 km | **50.8 Mm³** | 240 / 150 / 0 m |
| tongue, convex, p=0.5 | 1,925 m at the junction, touching the bed at 3.5 km | **59.3 Mm³** | 240 / 150 / 0 m |
| tongue, linear | 1,925 m at the junction, touching the bed at 4.6 km | **63.7 Mm³** | 240 / 150 / 60 m |
| tongue, concave, p=2 | 1,925 m at the junction, touching the bed at 4.6 km | **61.5 Mm³** | 240 / 150 / 15 m |
| tongue, convex, p=0.5 | 1,925 m at the junction, touching the bed at 4.6 km | **65.5 Mm³** | 240 / 150 / 60 m |

## The imagery reading: inundated width from the 0.55 m scenes → depth through the cross-section → volume

Widths read off the Pelican scenes (dossier 16a): 150–250 m across the floor from 0 to 2.5 km, 110–145 m from 3.8 to 4.6 km; 2.5–3.8 km is cloud (interpolated). Each station's cross-section converts a width into the depth that produces it; the volume is the integral. This is the 2-D area × topography estimate.

| imagery width case | 0–2.5 km width | 3.8–4.6 km width | volume | implied depth at 1 km / 2 km / 4 km |
|---|---|---|---|---|
| low | 150 m | 110 m | **12.9 Mm³** | 30 / 45 / 26 m |
| mid | 200 m | 128 m | **31.1 Mm³** | 64 / 96 / 49 m |
| high | 250 m | 145 m | **52.4 Mm³** | 118 / 130 / 49 m |

Caveat on the imagery reading: the width on 1 September is the width of the DEPOSIT and stripped ground left after the water drained, which is a floor on the width the flow reached, not the width at peak; and the 30 m cross-sections are borrowed at the artefact stations. Treat it as a lower-to-middle estimate of the peak stored volume.

## Width check: which reading matches the imagery?

| surface | DEM width 0–2.5 km (median) | 3.8–4.6 km (median) | imagery |
|---|---|---|---|
| pond at 1,925 m | 270 m | 60 m | 150–250 / 110–145 m |
| pond at 1,915 m | 255 m | 60 m | 150–250 / 110–145 m |
| tongue to 4.6 km, linear | 255 m | 60 m | 150–250 / 110–145 m |
| tongue to 4.6 km, concave | 255 m | 8 m | 150–250 / 110–145 m |
| tongue to 4.6 km, convex | 255 m | 60 m | 150–250 / 110–145 m |
| tongue to 3.5 km, linear | 240 m | nan m | 150–250 / 110–145 m |

## Solids left in the arm (from reported thicknesses; no before/after DEM exists for this reach)

Bed raised 'nearly 5 m' in the last 1.7 km (CCTV engineers), mud 1–2 m beyond, thin fill at 3.8–4.6 km: **0.9–2.8 Mm³ of solids**, i.e. a few per cent of the stored volume — the arm mostly drained.

## From stored volume to the volume at the node, and to the release

Split at the node from the valley geometry. Curves fitted to the OSM centrelines over 800 m give an inflow heading of 238°, a downstream exit on 164° (75° turn) and an up-valley exit on 2° (124° turn): momentum projection f_up = 0.00, cosine weighting 0.26. But centrelines through the VOLUMETRIC middle of each valley (GLO-30 cross-section centroids at 30–90 m depth; `--volumetric`) show the answer depends on which reach of the Lhende is called 'incoming': its last 500 m bends south toward the downstream exit (turn ~10–20°, up-valley 150–175°, f_up ≈ 0), while the kilometre above runs west-south-west, at right angles to both exits (turns 85–100° each way, cosine-weighted f_up 0.35–0.57). A 60–110 m deep flow at 47 m/s does not follow a 500 m bend, so the truth lies between, and the geometry alone cannot fix it. Bracket used: f_up = 0.10, 0.30, 0.50. The routing model cannot supply it either: its junction branch is a weir capped at 8 m of driving head (`model/core.py`). What would: peak-discharge continuity at the node, Q_in = Q_down + Q_up, from trimlines and superelevation in the reaches just above and just below the junction (`calcs/node_discharge_continuity.py`).

Lhende reach contribution subtracted: 3–15 Mm³ (0.5 channel water; 2.6–13 entrained bed — the stereo DEM has the gorge floor lowered 2–12 m — plus whatever of the 2025 outburst deposits it took; ≤1–2.5 melt; dossier 15).

| stored-volume case | V_up | at node, f_up 0.50 | 0.30 | 0.10 | release, f_up 0.50 | 0.30 | 0.10 |
|---|---|---|---|---|---|---|---|
| imagery widths, low | 12.9 | 26 | 43 | 129 | 11–23 | 28–40 | 114–126 |
| imagery widths, mid | 31.1 | 62 | 104 | 311 | 47–59 | 89–101 | 296–308 |
| imagery widths, high | 52.4 | 105 | 175 | 524 | 90–102 | 160–172 | 509–521 |
| tongue to 4.6 km, concave | 61.5 | 123 | 205 | 615 | 108–120 | 190–202 | 600–612 |
| tongue to 4.6 km, linear | 63.7 | 127 | 212 | 637 | 112–124 | 197–209 | 622–634 |
| tongue to 3.5 km, linear | 55.3 | 111 | 184 | 553 | 96–108 | 169–181 | 538–550 |
| pond at 1,925 m (over-fills the imagery widths) | 69.2 | 138 | 231 | 692 | 123–135 | 216–228 | 677–689 |

Our size envelope (finding 04) is 14–34 Mm³, median 21, from the clock, the border speed, the erosion volume and the deposition cap. None of those enters the table above.

