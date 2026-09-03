# Data sources, licences and attribution

Checked before any public release of this repository.

## Third-party data included here

| File(s) | Source | Licence / status | Notes |
|---|---|---|---|
| `data/osm_rivers.json`, `data/osm_rivers_lower.json`, `hindcast/*/osm_rivers.json` | OpenStreetMap via Overpass API | **ODbL 1.0** | Derived river geometry. Attribution required: "© OpenStreetMap contributors". Any published map or figure derived from these must carry it. |
| `data/river_profile.csv`, `hindcast/*/profile.csv` | Elevations from [opentopodata.org](https://www.opentopodata.org) Mapzen tiles (SRTM/ASTER/other public DEMs); positions from OSM | Public-domain DEM sources; OSM positions ODbL | Sampled, not redistributed wholesale. |
| `data/ffd_report.pdf` | Nepal DHM / Flood Forecasting Division press release, 27 Aug 2026 | Government press release, publicly issued | Primary source for the ~20 Mm³ "excess water" figure. Retained because official PDFs are frequently withdrawn or moved; **link to the original in preference to redistributing** if the repo goes public. |
| `data/valmikinagar_barrage.csv` | Transcribed from Indian press reporting of Bihar control-room figures | Facts, transcribed | Not an official release — flagged as press-transcribed everywhere it is used. |
| `data/198_discharge.csv` | DHM gauge series | check before release | Verify redistribution terms with DHM if publishing. |

## Third-party numbers we cite but do NOT redistribute

- **geopera** (satellite reconstruction, stereo DEM, seismology, calibrated
  model) — cited with dates and URLs in `research/`. Note their 28 Aug
  "12 Mm³ deposition wedge" was **retracted 1 Sept**; we score against the
  1 Sept stereo figures only.
- **Shugar et al. 2021** (*Science*) Chamoli values — used as comparison
  targets in `hindcast/chamoli/`, quoted in the scorecards.
- Published Seti 2012 figures — see `research/seti-2012-anchors.md`, each row
  carries its source and a quality rating.

## Our own material

Model code (`model/`, `calcs/`, `hindcast/`), research notes (`research/`),
report pages (`report/`) and `PLAN.md` are original work by this project.
Choose a licence before public release — suggested: **MIT** or **Apache-2.0**
for the code, **CC-BY-4.0** for the prose and figures, which keeps the work
reusable by ICIMOD/DHM/researchers while requiring attribution.

## Standing principle

Every contested or single-source number is flagged as such at the point of use
(see `PLAN.md` §6 "Honesty rails"). Nothing here should be read as an official
figure; where our numbers disagree with an agency's, both are shown.
