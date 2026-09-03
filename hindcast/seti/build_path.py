#!/usr/bin/env python3
"""
Seti Khola path builder — Annapurna IV / Sabche Cirque -> Kharapani -> Pokhara.
Same pipeline as model/build_profile.py and hindcast/chamoli/run_hindcast.py:
Overpass river stitch -> 400 m sampling -> opentopodata Mapzen elevations ->
profile.csv. Run once; the hindcast reads the cached CSV.
"""
import csv, json, math, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OSM_JSON = os.path.join(HERE, "osm_rivers.json")
PROFILE = os.path.join(HERE, "profile.csv")

# Waypoints (map reads — see research/seti-2012-anchors.md, flagged soft)
SOURCE = (28.5250, 84.0790)      # cliff S of Annapurna IV (7,525 m at
                                 # 28.5372, 84.0819), avalanche detachment
CIRQUE = (28.4800, 84.0000)      # Sabche Cirque floor (landing basin)
KHARAPANI = (28.3602, 83.9604)   # "Kharpani" hamlet, OSM place node — the
                                 # 09:38 photo anchor (Sardikhola VDC;
                                 # also called Tatopani)
POKHARA = (28.2100, 83.9800)     # Seti irrigation dam area, Pokhara
BBOX = (28.15, 83.90, 28.60, 84.20)
STEP = 0.4

def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

def fetch_osm():
    q = ('[out:json][timeout:90];'
         '(way["waterway"~"^(river|stream)$"]'
         f'({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}););out geom;')
    for host in ("https://overpass-api.de/api/interpreter",
                 "https://overpass.kumi.systems/api/interpreter"):
        try:
            req = urllib.request.Request(
                host, data=("data=" + urllib.parse.quote(q)).encode())
            with urllib.request.urlopen(req, timeout=180) as resp:
                d = json.loads(resp.read())
            if d.get("elements"):
                return d
        except Exception as e:
            print(f"  overpass {host} failed: {e}")
    raise RuntimeError("no Overpass mirror answered")

if not os.path.exists(OSM_JSON):
    json.dump(fetch_osm(), open(OSM_JSON, "w"))
d = json.load(open(OSM_JSON))

ways = []
for e in d["elements"]:
    if not e.get("geometry"):
        continue
    ways.append({"id": e["id"], "name": e.get("tags", {}).get("name", ""),
                 "pts": [(g["lat"], g["lon"]) for g in e["geometry"]]})
print(f"{len(ways)} waterway ways in bbox")
named = {}
for w in ways:
    if w["name"]:
        named.setdefault(w["name"], 0)
        named[w["name"]] += len(w["pts"])
print("named waterways:", sorted(named.items(), key=lambda kv: -kv[1])[:12])

# Greedy downstream chain: start at the source, repeatedly hop to the nearest
# unused way-endpoint that moves us closer to Pokhara. Robust to the Seti's
# OSM naming (Seti Gandaki / Seti Khola / Sety) and to unnamed headwaters.
def orient(w, target):
    if hav(w["pts"][0], target) < hav(w["pts"][-1], target):
        w["pts"].reverse()
    return w

# WAYPOINT-GUIDED chain. A purely Pokhara-seeking greedy walk wanders onto
# whichever tributary happens to point south (it took the Phirke Khola on the
# first attempt); requiring progress toward the NEXT waypoint in turn keeps
# it in the Seti corridor through the cirque and past Kharapani.
WAYPOINTS = [CIRQUE, KHARAPANI, POKHARA]
path = [SOURCE]
used = set()
cur = SOURCE
wi = 0
for _ in range(80):
    tgt = WAYPOINTS[wi]
    if hav(cur, tgt) < 1.2:
        print(f"  reached waypoint {wi} ({tgt[0]:.4f},{tgt[1]:.4f}) "
              f"at path point {len(path)}")
        wi += 1
        if wi >= len(WAYPOINTS):
            break
        tgt = WAYPOINTS[wi]
    best, best_d = None, 1e9
    for w in ways:
        if w["id"] in used or len(w["pts"]) < 2:
            continue
        for p in w["pts"]:
            dd = hav(cur, p)
            if dd < best_d and hav(p, tgt) < hav(cur, tgt) + 0.5:
                best, best_d = w, dd
    if best is None or best_d > 5.0:
        print(f"  no continuation toward waypoint {wi}; bridging directly")
        path.append(tgt)
        cur = tgt
        wi += 1
        if wi >= len(WAYPOINTS):
            break
        continue
    used.add(best["id"])
    orient(best, tgt)
    i0 = min(range(len(best["pts"])), key=lambda i: hav(cur, best["pts"][i]))
    seg = best["pts"][i0:]
    if len(seg) < 2:
        continue
    if best_d > 0.05:
        print(f"  gap {best_d*1000:.0f} m bridged into "
              f"{best['name'] or '(unnamed)'} ({len(seg)} pts)")
    path.extend(seg)
    cur = path[-1]

imin = min(range(len(path)), key=lambda i: hav(path[i], POKHARA))
path = path[:imin + 1]
cum = [0.0]
for i in range(1, len(path)):
    cum.append(cum[-1] + hav(path[i - 1], path[i]))
print(f"stitched path source -> Pokhara: {cum[-1]:.1f} km, {len(path)} pts")

samples, target, j = [], 0.0, 0
while target <= cum[-1]:
    while j < len(cum) - 1 and cum[j + 1] < target:
        j += 1
    if j >= len(cum) - 1:
        break
    f = (target - cum[j]) / max(cum[j + 1] - cum[j], 1e-9)
    samples.append((target,
                    path[j][0] + f * (path[j + 1][0] - path[j][0]),
                    path[j][1] + f * (path[j + 1][1] - path[j][1])))
    target += STEP

def path_km(pt):
    i = min(range(len(samples)),
            key=lambda i: hav((samples[i][1], samples[i][2]), pt))
    return samples[i][0], hav((samples[i][1], samples[i][2]), pt)

for nm, pt in [("Sabche Cirque", CIRQUE), ("Kharapani", KHARAPANI),
               ("Pokhara", POKHARA)]:
    km, off = path_km(pt)
    print(f"  {nm:16s} path km {km:6.1f}  (offset {off:.2f} km)"
          + ("   [published: Kharapani ~20 km]" if nm == "Kharapani" else ""))

if os.path.exists(PROFILE):
    print("profile.csv already cached")
else:
    elevs = []
    for i in range(0, len(samples), 100):
        batch = samples[i:i + 100]
        req = urllib.request.Request(
            "https://api.opentopodata.org/v1/mapzen",
            data=json.dumps({"locations":
                             "|".join(f"{s[1]},{s[2]}" for s in batch)}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dd = json.loads(resp.read())
        assert dd["status"] == "OK", dd
        elevs.extend(r["elevation"] for r in dd["results"])
        print(f"  elevation batch {i//100 + 1}: {len(dd['results'])} pts")
        time.sleep(1.2)
    with open(PROFILE, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dist_km", "lat", "lon", "elev_m"])
        for s, e in zip(samples, elevs):
            w.writerow([f"{s[0]:.3f}", f"{s[1]:.6f}", f"{s[2]:.6f}", e])
    print(f"wrote {len(elevs)} pts -> profile.csv "
          f"({elevs[0]:.0f} m -> {elevs[-1]:.0f} m)")
