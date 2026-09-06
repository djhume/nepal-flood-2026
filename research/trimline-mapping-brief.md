# Brief: map every mud line in the corridor from imagery plus the DEM

*Written 7 Sept 2026 for a fresh session. Dave's idea (6 Sept, late): overlay
the post-event imagery on the topography so that wherever the stripped-ground
boundary crosses a contour we get a three-dimensional point on the mud line —
everywhere, both banks, the whole corridor. This is the automated version of
that overlay. Read `PLAN.md` §6/§6a (honesty rails) and dossier §16–18 first.*

## Why it matters

The size envelope (finding 04) was scored on timing, a border speed, an erosion
volume and a deposition cap, and never on a water depth. Four lines now say the
passing runs are too small below the junction (dossier §17, §18; PLAN 6 Sept
night). A peak-stage profile along the corridor is the missing observable, and
inner/outer-bank pairs at bends give velocities, hence a peak-discharge profile.
That is the input the next ensemble needs.

## What exists already

| Piece | Where | Note |
|---|---|---|
| River path, 400 m spacing, scar → Devghat | `data/river_path.csv`, `data/river_profile.csv` | Mapzen elevations — **do not use for gorge floors** (void-fill artefacts, dossier §17) |
| Copernicus GLO-30 tile N28 E085 | `data/Copernicus_DSM_COG_10_N28_00_E085_00_DEM.tif` (gitignored; URL in `DATA-SOURCES.md`) | covers the scar to ~km 60; Betrawati and below need tile N27 E085 from the same bucket |
| Sentinel-2 NDVI pre (12 Aug) and post composite (27 Aug–3 Sept) | `output/wedge_ndvi_*.npy` (gitignored, ~10 min to regenerate with `calcs/sentinel_wedge.py`) | junction bbox only (85.28–85.48 E, 28.24–28.44 N); 42.6% both-valid; the corridor script recovers the georeferencing |
| Corridor-along-centreline machinery | `calcs/sentinel_wedge_corridor.py` | chains OSM centrelines, assigns pixels to arms, bins by chainage — extend rather than rewrite |
| Cross-section tools on GLO-30 | `calcs/upvalley_wedge_volume.py` (arm), `calcs/node_discharge_continuity.py` (stations on the main path) | area/width at a given level; the node-continuity CSV format for marks |
| Sub-metre open imagery | Planet disaster data (PlanetScope 3 m whole corridor; SkySat 0.8 m; **Pelican 0.55 m, 27 Aug and 1 Sept, Syabrubesi → Rasuwagadhi**), CC-BY-NC-4.0: https://data.source.coop/planet/disasterdata/nepal-flash-flood-2026-08-26/catalog.json ; Vantor (Maxar) WorldView Legion 27/28 Aug visual COGs + 2021 WV2 baseline, CC-BY-NC-4.0: https://vantor-opendata.s3.amazonaws.com/events/Nepal-Flooding-Aug-2026/collection.json | analysis only — never commit the imagery or crops |
| geopera's trimlines and per-km bed change | https://github.com/geo-pera/bhotekoshi-2026-reconstruction/releases/tag/v1.1 | their 40–134 m at Rasuwagadhi (median ~70 in the gorges) and their dh table are the cross-check; their DSM covers ~45% of the Nepal reach only |
| Better DEM | HMA 8 m mosaic tile 675 (NSIDC `HMA_DEM8m_MOS`) covers the whole upper corridor | **needs a free Earthdata login** — get it first; 30 m in a slot gorge is the limiting error |

## Method, in stages

1. **Imagery to a stripped-ground mask.** Sentinel-2 first (whole corridor,
   10 m, free): extend the bbox to cover scar → Betrawati, rebuild the pre/post
   NDVI composite, classify "bare after, vegetated before" (the corridor script's
   NDVI<0.20 threshold plus a change threshold). Then the 0.55 m Pelican scenes
   for Syabrubesi → Rasuwagadhi, where the boundary can be placed to a few
   metres. Cloud is the enemy: composite across dates, and report the
   both-valid coverage for every reach.
2. **Mask to two bank lines.** For each 100 m chainage station on the OSM
   centreline, walk the cross-section outward on each side until the mask ends:
   that pixel is the trimline point for that bank. Record its coordinates and
   the distance from the centreline. Reject stations where cloud or shadow
   truncates the mask (flag, do not fill).
3. **Bank lines to elevations.** Sample the DEM at every trimline point
   (bilinear). Because the point sits on a slope, the vertical error is the
   horizontal placement error times the wall slope — with 10 m imagery on a 45°
   wall that is ±10 m, with 0.55 m imagery ±1–3 m, and the 30 m DEM adds its
   own ±4–10 m. Carry these per point. Also sample the bed (cross-section
   minimum, upstream-minimum envelope along the path) and the DEM slope at the
   point.
4. **Elevations to stage, and stage to velocity.** Stage above bed per bank per
   station. Where the two banks differ systematically through a bend, the
   difference is superelevation: v² = g r Δh / W with r from the centreline
   curvature. Where the flow met a wall head-on (side-valley mouths, the border
   junction), the mark is run-up, not stage — dossier §6c has the rule; flag
   those stations rather than average them in.
5. **Outputs.** A CSV per station: chainage, lat/lon of each bank point, bank
   elevations, bed, stage, width at the trimline, DEM area at the trimline,
   superelevation velocity where a bend gives one, discharge where both exist,
   and the coverage/quality flags. A figure: stage profile along the corridor
   with geopera's points overlaid, and the model's passing-run depths from
   dossier §18 for comparison. Then a short results note in the dossier.

## Checks that must be in it

- The Rasuwagadhi junction: our three mud lines (bed 1,815, lee 1,875, impact
  cliff 1,920–1,930 — dossier §6c) and geopera's 40–134 m. The method should
  reproduce them; if it does not, find out why before trusting anything else.
- Hakubesi, km 43–45: the helicopter-still read of ~45–70 m above the
  pre-event bed (dossier §18) and geopera's bed rise of +11–18 m there.
- Syabrubesi: geopera's velocity collapse to ~11 m/s at the opening.
- The Mapzen profile disagrees with GLO-30 by tens of metres in the gorges;
  use GLO-30 (then HMA 8 m) throughout and say which.

## Honesty rails that bite here

- A stripped-ground boundary is a floor on where the water reached (vegetation
  survives brief immersion) and, on the 1 September scenes, a post-drain
  surface. Say so per reach.
- Trimlines are not depths where the flow hit a wall (§6c). Flag the geometry.
- Report coverage; never interpolate across cloud without saying so.
- Licences: Planet and Vantor imagery is CC-BY-NC; analysis and figures of
  derived lines are fine, the imagery itself and crops of it stay out of the
  repo (`.gitignore` already excludes `research/video/*` and `output/*.npy`;
  put rasters under `output/` and add a pattern if needed).
- Nothing enters the findings the day it is computed; results go to the
  changelog and dossier first (PLAN §6a).

## Deliverable

`calcs/trimline_map.py` (reproducible from the open sources, caching
downloads under `output/`), `output/trimlines.csv`, `output/trimline_profile.png`,
dossier §19 with the results and their coverage, and a one-paragraph
changelog entry. The stage and discharge profile then becomes the observable
set for the ensemble rerun that both sessions have named as the next job.
