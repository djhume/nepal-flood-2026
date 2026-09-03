#!/usr/bin/env python3
"""
Phase F portability test — hindcast of the 7 Feb 2021 Chamoli disaster
(Ronti Peak rock/ice avalanche -> Ronti Gad -> Rishiganga -> Dhauliganga)
with the Trishuli-calibrated front-speed law applied with ZERO recalibration.

THE LAW (verbatim from the Trishuli fit — not refitted here):
    U = 300 * S^0.82 + 4.0   [m/s], clipped to [3, 65]
    front time = cumulative dx / U

Pipeline mirrors model/build_profile.py + model/fetch_elevations.py +
model/snowplow.py: OSM (Overpass) river stitching with straight-segment gap
bridging, 400 m sampling, opentopodata mapzen elevations (batches of 100,
1.2 s sleep), monotone-descent + ~2 km smoothed profile, centred-difference
slope. The DEM (SRTM-era) predates the 2021 collapse, i.e. it is the
pre-event surface — same convention as the Trishuli run (distance 0 = scar,
initial fall included in the path).

Scored against Shugar et al. 2021 (Science, doi:10.1126/science.abh4455);
observed values are NOT used anywhere in the model — comparison only.

Outputs: profile.csv, chamoli_hindcast.png, scorecard printed to stdout.
"""
import csv, json, math, os, time, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OSM_JSON = os.path.join(HERE, "osm_rivers.json")
PROFILE = os.path.join(HERE, "profile.csv")

# ------------------------------------------------------------- geometry ----
SCAR = (30.3733, 79.7317)         # Ronti Peak north-face wedge scar, ~5,500 m
TAPOVAN = (30.4903, 79.6285)      # Tapovan Vishnugad HPP intake
VISHNUPRAYAG = (30.5560, 79.5730)  # Dhauliganga-Alaknanda confluence
# Rishiganga HPP (13.2 MW) at Raini village, lower Rishiganga just above the
# Dhauliganga confluence (approximate published location; soft +-0.3 km)
RISHIGANGA_HPP = (30.4789, 79.6978)
BBOX = (30.30, 79.55, 30.60, 79.80)
STEP = 0.4                        # km, as in build_profile.py

def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

# ------------------------------------------------- 1. OSM river geometry ----
def fetch_osm():
    q = ('[out:json][timeout:90];'
         '(way["waterway"~"^(river|stream)$"]'
         f'({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}););out geom;')
    for host in ("https://overpass-api.de/api/interpreter",
                 "https://overpass.kumi.systems/api/interpreter"):
        try:
            req = urllib.request.Request(
                host, data=("data=" + urllib.parse.quote(q)).encode())
            with urllib.request.urlopen(req, timeout=120) as resp:
                d = json.loads(resp.read())
            if d.get("elements"):
                return d
        except Exception as e:
            print(f"  overpass {host} failed: {e}")
    raise RuntimeError("no Overpass mirror answered")

if not os.path.exists(OSM_JSON):
    d = fetch_osm()
    json.dump(d, open(OSM_JSON, "w"))
else:
    d = json.load(open(OSM_JSON))

ways = []
for e in d["elements"]:
    if not e.get("geometry"):
        continue
    pts = [(g["lat"], g["lon"]) for g in e["geometry"]]
    ways.append({"id": e["id"], "name": e.get("tags", {}).get("name", ""),
                 "pts": pts})

# Corridor selection. "Ronti Gad" is mapped as "Raunthi Gadhera"; the reach
# directly below the scar is an unnamed stream, caught by proximity. Among
# the three "Dhauli Ganga" ways only the Raini->Vishnuprayag one passes
# Tapovan; take that one.
def min_to(w, pt):
    return min(hav(pt, p) for p in w["pts"])

corridor = []
for w in ways:
    if w["name"] in ("Raunthi Gadhera", "Rishi Ganga"):
        corridor.append(w)
    elif w["name"] == "Dhauli Ganga" and min_to(w, TAPOVAN) < 1.0 \
            and len(w["pts"]) > 2:
        corridor.append(w)
    elif w["name"] == "" and min_to(w, SCAR) < 2.0:
        corridor.append(w)
print("corridor ways:")
for w in corridor:
    print(f"  {w['name'] or '(unnamed, below scar)'} id={w['id']} "
          f"({len(w['pts'])} pts)")

# Orient each way downstream (far end closer to the Alaknanda confluence),
# then chain them in downstream order, entering each way at its point
# nearest the current path end (skips headwater branches above the
# junction) and bridging any gap with a straight segment.
for w in corridor:
    if hav(w["pts"][0], VISHNUPRAYAG) < hav(w["pts"][-1], VISHNUPRAYAG):
        w["pts"].reverse()

order = {"": 0, "Raunthi Gadhera": 1, "Rishi Ganga": 2, "Dhauli Ganga": 3}
corridor.sort(key=lambda w: order[w["name"]])

path = [SCAR]
gaps = []
for w in corridor:
    end = path[-1]
    i0 = min(range(len(w["pts"])), key=lambda i: hav(end, w["pts"][i]))
    gap = hav(end, w["pts"][i0])
    if gap > 0.05:
        gaps.append((w["name"] or "(unnamed)", gap))
        print(f"  gap {gap*1000:.0f} m bridged into "
              f"{w['name'] or '(unnamed)'}")
    path.extend(w["pts"][i0:])

# trim at the Alaknanda confluence
imin = min(range(len(path)), key=lambda i: hav(path[i], VISHNUPRAYAG))
path = path[:imin + 1]

cum = [0.0]
for i in range(1, len(path)):
    cum.append(cum[-1] + hav(path[i - 1], path[i]))
print(f"total path length scar -> Vishnuprayag: {cum[-1]:.1f} km")

samples, target, j = [], 0.0, 0
while target <= cum[-1]:
    while j < len(cum) - 1 and cum[j + 1] < target:
        j += 1
    if j >= len(cum) - 1:
        samples.append((cum[-1], *path[-1]))
        break
    f = (target - cum[j]) / max(cum[j + 1] - cum[j], 1e-9)
    lat = path[j][0] + f * (path[j + 1][0] - path[j][0])
    lon = path[j][1] + f * (path[j + 1][1] - path[j][1])
    samples.append((target, lat, lon))
    target += STEP

# sanity: path-km at the published checkpoints
CHECKS = [("Rishiganga HPP (Raini)", RISHIGANGA_HPP),
          ("Raini confluence", None),   # filled from OSM below
          ("Tapovan intake", TAPOVAN),
          ("Vishnuprayag", VISHNUPRAYAG)]
# Raini confluence = downstream end of the Rishi Ganga way
rishi = next(w for w in corridor if w["name"] == "Rishi Ganga")
CHECKS[1] = ("Raini confluence", rishi["pts"][-1])

def path_km(pt):
    i = min(range(len(samples)),
            key=lambda i: hav((samples[i][1], samples[i][2]), pt))
    return samples[i][0], hav((samples[i][1], samples[i][2]), pt)

KM = {}
print("checkpoint path distances (published: HPP ~13.2-15, Raini ~13.5-15, "
      "Tapovan ~24-26 km):")
for name, pt in CHECKS:
    km, off = path_km(pt)
    KM[name] = km
    print(f"  {name:24s} path km {km:5.1f}  (offset {off:.2f} km)")

# ------------------------------------------------------- 2. elevations -----
if os.path.exists(PROFILE):
    rows = list(csv.DictReader(open(PROFILE)))
    elevs = [float(r["elev_m"]) for r in rows]
    print(f"profile.csv cached ({len(rows)} pts)")
else:
    elevs = []
    for i in range(0, len(samples), 100):
        batch = samples[i:i + 100]
        locs = "|".join(f"{s[1]},{s[2]}" for s in batch)
        req = urllib.request.Request(
            "https://api.opentopodata.org/v1/mapzen",
            data=json.dumps({"locations": locs}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dd = json.loads(resp.read())
        assert dd["status"] == "OK", dd
        elevs.extend(r["elevation"] for r in dd["results"])
        print(f"  elevation batch {i // 100 + 1}: {len(dd['results'])} pts")
        time.sleep(1.2)
    with open(PROFILE, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dist_km", "lat", "lon", "elev_m"])
        for s, e in zip(samples, elevs):
            w.writerow([f"{s[0]:.3f}", f"{s[1]:.6f}", f"{s[2]:.6f}", e])
    print(f"wrote {len(elevs)} pts -> profile.csv")
print(f"scar {elevs[0]:.0f} m -> Vishnuprayag {elevs[-1]:.0f} m")

# ------------------------------------------- 3. profile -> slope (as B) ----
x_km = np.array([s[0] for s in samples])
z_raw = np.array(elevs, dtype=float)
z = np.minimum.accumulate(z_raw)          # monotone descent
k = 5                                     # ~2 km smoothing, as snowplow.py
z_s = np.convolve(np.pad(z, k, mode="edge"),
                  np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
S = np.maximum(-np.gradient(z_s, x_km * 1000.0), 1e-4)

# ------------------------------------- 4. THE LAW, verbatim, zero refit ----
U = np.clip(300.0 * S ** 0.82 + 4.0, 3.0, 65.0)
dx = np.gradient(x_km) * 1000.0
t_front = np.cumsum(dx / U) / 60.0
t_front -= t_front[0]                     # minutes after 10:21:14 IST

# ------------------------------------------------------- 5. scorecard ------
# Observed values (Shugar et al. 2021 Science; video/seismic). NOT model
# inputs. Arrival window at Tapovan is soft (camera clocks): 34-37 min.
OBS_SPEEDS = [   # (label, path-km evaluated, observed m/s)
    ("near Rishiganga HPP", KM["Rishiganga HPP (Raini)"], 25.0),
    ("just above Tapovan", KM["Tapovan intake"] - 1.0, 16.0),
    ("just below Tapovan", KM["Tapovan intake"] + 1.0, 12.0),
]
OBS_TAPOVAN_MIN = (34.0, 37.0)

def at(km, arr):
    return float(np.interp(km, x_km, arr))

print("\n================ SCORECARD (zero recalibration) ================")
print(f"{'station':26s} {'km':>5s} {'model t':>8s} {'model U':>8s} "
      f"{'obs':>12s} {'error':>8s}")
tap_km = KM["Tapovan intake"]
tap_t = at(tap_km, t_front)
obs_mid = 0.5 * (OBS_TAPOVAN_MIN[0] + OBS_TAPOVAN_MIN[1])
print(f"{'Tapovan ARRIVAL':26s} {tap_km:5.1f} {tap_t:6.1f} m {'':8s} "
      f"{OBS_TAPOVAN_MIN[0]:.0f}-{OBS_TAPOVAN_MIN[1]:.0f} min "
      f"{100*(tap_t-obs_mid)/obs_mid:+7.0f}%")
for label, km, obs in OBS_SPEEDS:
    u = at(km, U)
    print(f"{label:26s} {km:5.1f} {at(km, t_front):6.1f} m {u:6.1f} "
          f"m/s {obs:8.0f} m/s {100*(u-obs)/obs:+7.0f}%")

print("\nfull arrival table:")
print(f"{'path km':>8s} {'model t (min)':>14s} {'model U (m/s)':>14s} "
      f"{'elev (m)':>9s} {'slope':>7s}")
for km in [0, 2, 4, 6, 8, 10, 12, KM['Rishiganga HPP (Raini)'],
           KM['Raini confluence'], 18, 20, 22, tap_km, tap_km + 1,
           28, 30, x_km[-1]]:
    print(f"{km:8.1f} {at(km, t_front):14.1f} {at(km, U):14.1f} "
          f"{at(km, z_s):9.0f} {at(km, S):7.3f}")

avg_tap = tap_km * 1000.0 / (tap_t * 60.0)
print(f"\nmodel mean speed scar->Tapovan: {avg_tap:.0f} m/s "
      f"(observed implies ~{tap_km*1000/(obs_mid*60):.0f} m/s)")

# --------------------------------------------------------------- 6. plot ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
marks = [("Rishiganga HPP", KM["Rishiganga HPP (Raini)"]),
         ("Raini confl.", KM["Raini confluence"]),
         ("Tapovan", tap_km), ("Vishnuprayag", KM["Vishnuprayag"])]

ax = axes[0]
ax.plot(x_km, z_raw, lw=0.6, color="0.7", label="raw DEM samples")
ax.plot(x_km, z_s, lw=1.8, color="tab:blue", label="channel profile (smoothed)")
for nm, km in marks:
    ax.axvline(km, color="0.88", zorder=0)
    ax.annotate(nm, (km, at(km, z_s) + 220), rotation=90, fontsize=7,
                ha="right")
ax.set_xlabel("distance from scar (km)")
ax.set_ylabel("elevation (m)")
ax.set_title("Chamoli path: Ronti scar → Vishnuprayag\n(OSM + Mapzen DEM, pre-event surface)")
ax.legend(fontsize=8)

ax = axes[1]
ax.plot(x_km, t_front, color="tab:red",
        label="model front (U = 300·S$^{0.82}$+4, Trishuli fit)")
ax.axhspan(*OBS_TAPOVAN_MIN, xmin=0, xmax=1, color="k", alpha=0.08)
ax.errorbar([tap_km], [obs_mid],
            yerr=[[obs_mid - OBS_TAPOVAN_MIN[0]], [OBS_TAPOVAN_MIN[1] - obs_mid]],
            fmt="v", color="k", ms=8, capsize=4,
            label="observed Tapovan arrival 34–37 min")
tol = ax.fill_between(x_km, t_front * 0.5, t_front * 1.5, color="tab:red",
                      alpha=0.12, label="±50 % warning-tier band on model")
for nm, km in marks:
    ax.axvline(km, color="0.88", zorder=0)
ax.set_xlabel("distance from scar (km)")
ax.set_ylabel("minutes after 10:21:14 IST")
ax.set_ylim(0, 42)
ax.set_title("Front arrival: zero-recalibration model vs observed")
ax.legend(fontsize=8, loc="upper left")

ax = axes[2]
ax.plot(x_km, U, color="tab:red", label="model front speed")
for label, km, obs in OBS_SPEEDS:
    ax.plot(km, obs, "o", color="k", ms=6)
    ax.annotate(f"{label} (obs {obs:.0f})", (km, obs),
                textcoords="offset points", xytext=(6, 5), fontsize=7)
for nm, km in marks:
    ax.axvline(km, color="0.88", zorder=0)
ax.set_xlabel("distance from scar (km)")
ax.set_ylabel("speed (m/s)")
ax.set_title("Front speed vs Shugar et al. video points")
ax.legend(fontsize=8)

fig.suptitle("Chamoli 7 Feb 2021 hindcast — Trishuli front-speed law, ZERO recalibration (Phase F)",
             fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chamoli_hindcast.png"), dpi=140)
print("figure -> chamoli_hindcast.png")
