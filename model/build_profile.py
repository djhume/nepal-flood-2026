#!/usr/bin/env python3
"""
Stitch the OSM river ways into one downstream path (Chhochen Khola -> Lhende
Khola/Donglin Zangbo -> Kyirong Tsangpo -> Bhote Koshi -> Trishuli -> Devghat)
and sample it at regular intervals for the elevation profile.

Output: data/river_path.csv  (dist_km, lat, lon)
"""
import json, math, csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# Names that belong to the main flood corridor, in rough downstream order.
CORRIDOR_NAMES = {
    "Chhochen Khola",
    "东林藏布",            # Donglin Zangbo = Lhende/Lende Khola
    "吉隆藏布",            # Jilong Zangbo = Kyirong Tsangpo (main stem at border)
    "भोटे कोशी",           # Bhote Koshi (Rasuwa)
    "Bhote Koshi", "Bhote Kosi", "Bhotekoshi",
    "Trishuli River", "Trishuli Ganga River",
    "त्रिशुली नदी",         # Trishuli Nadi (lower stem)
}

SCAR = (28.2765, 85.5194)          # collapse scar (Petley)
DEVGHAT = (27.7095, 84.4290)       # Trishuli-Kali Gandaki confluence

def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

ways, seen = [], set()
for fname in ("osm_rivers.json", "osm_rivers_lower.json"):
    d = json.load(open(os.path.join(DATA, fname)))
    for e in d["elements"]:
        name = e.get("tags", {}).get("name", "")
        if name in CORRIDOR_NAMES and e.get("geometry") and e["id"] not in seen:
            seen.add(e["id"])
            pts = [(g["lat"], g["lon"]) for g in e["geometry"]]
            ln = sum(hav(pts[i - 1], pts[i]) for i in range(1, len(pts)))
            if ln < 0.3:              # skip mapping fragments
                continue
            ways.append({"id": e["id"], "name": name, "pts": pts})
print(f"corridor ways: {len(ways)}")

# Greedy stitch: start from the way whose endpoint is nearest the scar's
# valley, repeatedly append the unused way whose nearer endpoint is closest to
# the current path end (reversing as needed), until we can't get closer to
# Devghat. Bridge gaps (unnamed connector ways) with straight segments.
unused = ways[:]
# starting way: closest approach to the scar
start = min(unused, key=lambda w: min(hav(SCAR, p) for p in w["pts"]))
unused.remove(start)
# orient it pointing away from the scar (downstream)
if hav(SCAR, start["pts"][0]) > hav(SCAR, start["pts"][-1]):
    start["pts"].reverse()
path = start["pts"][:]
used_names = [start["name"]]
print(f"start: {start['name']} (closest approach to scar "
      f"{min(hav(SCAR, p) for p in start['pts']):.2f} km)")

while hav(path[-1], DEVGHAT) > 2.0:
    end = path[-1]
    # candidates: any unused way, either orientation, whose FAR end moves us
    # toward Devghat (2 km slack); pick the one with the smallest join gap
    best, bestd, bestrev = None, 1e9, False
    for w in unused:
        for rev in (False, True):
            near = w["pts"][-1] if rev else w["pts"][0]
            far = w["pts"][0] if rev else w["pts"][-1]
            gap = hav(end, near)
            if gap < bestd and hav(far, DEVGHAT) < hav(end, DEVGHAT) + 2.0:
                best, bestd, bestrev = w, gap, rev
    if best is None or bestd > 5.0:   # no continuation within 5 km
        break
    unused.remove(best)
    pts = best["pts"][::-1] if bestrev else best["pts"]
    if bestd > 0.15:
        print(f"  gap {bestd*1000:.0f} m bridged before {best['name']} "
              f"at {hav(SCAR, pts[0]):.0f} km-ish from scar")
    path.extend(pts)
    used_names.append(best["name"])

print("chain:", " -> ".join(used_names))
print(f"end of path is {hav(path[-1], DEVGHAT):.1f} km from Devghat")

# Trim the path at Devghat (closest point), and prepend the scar-to-channel
# fall line so distance 0 = collapse scar.
imin = min(range(len(path)), key=lambda i: hav(path[i], DEVGHAT))
path = path[:imin + 1]
path.insert(0, SCAR)

# cumulative distance + resample every ~400 m
cum = [0.0]
for i in range(1, len(path)):
    cum.append(cum[-1] + hav(path[i - 1], path[i]))
print(f"total path length scar->Devghat: {cum[-1]:.1f} km")

STEP = 0.4
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

with open(os.path.join(DATA, "river_path.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dist_km", "lat", "lon"])
    for s in samples:
        w.writerow([f"{s[0]:.3f}", f"{s[1]:.6f}", f"{s[2]:.6f}"])
print(f"wrote {len(samples)} samples -> data/river_path.csv")

# sanity: report path distance at known checkpoints
CHECKS = {
    "Rasuwagadhi/Gyirong Port": (28.2780, 85.3780),
    "Syabrubesi": (28.1600, 85.3330),
    "Betrawati": (27.9700, 85.1800),
    "Galchhi": (27.8230, 84.9720),
    "Devghat": DEVGHAT,
}
for name, pt in CHECKS.items():
    i = min(range(len(samples)), key=lambda i: hav((samples[i][1], samples[i][2]), pt))
    off = hav((samples[i][1], samples[i][2]), pt)
    print(f"  {name:26s} at path km {samples[i][0]:6.1f}  (offset {off:.2f} km)")
