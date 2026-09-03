# Concept note: two-tier flood warning for Trishuli-class events

**Draft for circulation under Dave Hume's name** (NEA engineering, IPPAN,
ICIMOD, NTC/Ncell, DHM). One page. v0.1, 3 Sept 2026.

## The problem, measured

On 26 August the flood front covered the first 22 km (collapse → border) in
7 minutes; SMS alerts left 38 minutes after the collapse. Everyone above
Betrawati — including most of the ~900 missing hydropower workers — was in a
reach where no human-in-the-loop alert chain can ever arrive in time. Below
Betrawati the wave took 40 minutes to 7 hours: there, the existing chain can
work. The warning problem is therefore TWO problems, split by a line our
routing analysis locates near Betrawati (path-km ~68).

## Tier 1 (machine-only, 0–~68 km): seconds matter

- **Trigger:** the collapse announced itself as a magnitude-5.2 seismic event
  within tens of seconds. Automated landslide-vs-earthquake discrimination on
  the existing Nepali + regional seismic networks, with pre-delegated
  authority to broadcast without human sign-off. Seismic moment gives a first
  magnitude estimate for free.
- **Confirmation & sizing:** PV-powered, satellite-uplinked (not cell-
  dependent) sensors mounted ABOVE historic trimlines: non-contact radar
  stage gauges on bridge/wall sites plus geophones (the Illgraben,
  Switzerland architecture, proven for ~20 years). First-sensor rise rate
  bounds the event size within minutes and cuts false alarms.
- **Dissemination: Cell Broadcast, not SMS.** CB (ETWS/EU-Alert class) is
  sub-10-second, hits every handset in selected cell sectors simultaneously,
  does not queue or congest, and is a core-network feature to enable with
  NTC/Ncell — no new towers. Precompute the cell-sector ↔ river-reach
  adjacency; broadcast rolls downstream matched to the routing model's
  arrival curve ("leave now" at Timure; "40 minutes" at Betrawati).
- **Hydropower integration:** cascade intakes are natural sensor sites
  (power, comms, staff). Wire headworks instruments into the trigger web;
  wire the trigger into tunnel egress alarms and fail-safe intake gates.

## Tier 0 (watchlist, weeks ahead): satellite InSAR

Sentinel-1 InSAR shows the Langtang Lirung mass was creeping ~10 mm/month and
accelerating in the days before failure (Shirzaei, Virginia Tech, via Nature
news, 2 Sept 2026). Routine InSAR screening of steep glacierized faces above
occupied corridors is cheap, and a watchlist changes the economics of Tiers 1
and 2: sensors and drills concentrate where the mountain is already moving.
GFZ's Niels Hovius has independently stated seismic-signal-based downstream
warning was feasible for this event "with only minutes' delay."

## Tier 2 (human chain, below ~68 km): the existing system, triggered better

DHM's SMS chain performed as designed on 26 August for the lower valley. Its
weakness was upstream trigger latency, which Tier 1 removes.

## Why this ports

Every input to the timing analysis (river network, terrain, baseflow) is
globally available; the routing model runs in seconds per catchment. The same
method yields a timing-budget atlas for every glaciated headwater corridor in
Nepal — which settlements, cell sectors and plants fall in each tier — for
roughly the cost of a workshop, before any hardware is bought.

## Asks

1. NTC/Ncell + regulator: enable Cell Broadcast (policy/config, small cost).
2. DHM + seismology: automated trigger pilot on one corridor.
3. NEA/IPPAN: sensor hosting + SCADA integration at cascade intakes; recover
   and share plant records from 26 August — likely the only high-frequency
   hydrographs of the upper reach in existence.
4. Development partners: fund the Nepal timing-budget atlas as the siting
   basis for all of the above.

*Technical basis: [link to The Trishuli Water Ledger + workings notebook].*
