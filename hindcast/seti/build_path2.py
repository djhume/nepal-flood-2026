#!/usr/bin/env python3
"""
Seti Khola path builder, v2 — GRAPH SHORTEST PATH, replacing the v1 greedy walk.

WHY THIS EXISTS (bug found 3 Sept, after the blind hindcast was published):
v1's waypoint-guided greedy chain hopped to the nearest way that made progress
toward the next waypoint, and *bridged in a straight line* whenever no such way
was found within 5 km. Between the Sabche Cirque and Kharapani it did this
repeatedly, so ~17 km of the "river" path is straight lines flown across the
cirque rim and its ridges. The sampled elevations along those bridges oscillate
by 1,500 m (1,020 m at km 9.6, 4,042 m at km 11.2, 3,096 m at km 24.0), and
run_seti.py's monotone-descent clamp (np.minimum.accumulate) then flattened
everything from km 9.6 to km 41.6 to a constant 1,020 m: 31 km of dead-flat
"gorge", 64% of the profile clamped. The published Seti timing pass was
therefore obtained on a channel with no gradient through its entire runout.

v1 is kept (build_path.py, profile_v1.csv) because it produced a published
result and must stay reproducible.

WHAT v2 DOES INSTEAD. OSM does carry a continuous Seti in this corridor - way
352604044 "Seti Khola" is a single 20.6 km line from the cirque outlet down to
below Kharapani; v1 simply never chained onto it. So: build a graph of every
waterway segment in the bbox, heal sub-150 m gaps between way endpoints with
penalised bridge edges, and run Dijkstra from the cirque outlet to Pokhara.
The route is then whatever the mapped drainage network actually connects, not
whatever a greedy walk could see from where it stood.

The one legitimate straight line is retained and labelled: source cliff ->
Sabche Cirque floor is the AVALANCHE trajectory (it fell ~2,350 m nearly
vertically, per the anchors file), not a river reach.

Validation the path must pass, both independent of the model:
  * Kharapani (28.3602, 83.9604) within a few hundred m of the line;
  * gorge head -> Kharapani ~= 20 km (published "20 km downstream in 28 min").
"""
import csv, heapq, json, math, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OSM_JSON = os.path.join(HERE, "osm_rivers.json")
PROFILE = os.path.join(HERE, "profile.csv")

SOURCE = (28.5250, 84.0790)      # cliff S of Annapurna IV - detachment
CIRQUE = (28.4800, 84.0000)      # Sabche Cirque floor - avalanche landing
KHARAPANI = (28.3602, 83.9604)   # 09:38 photo anchor (Tatopani)
POKHARA = (28.2100, 83.9800)     # Seti irrigation dam
STEP = 0.4                       # km resampling, as v1
GAP_M = 150.0                    # heal way-to-way gaps up to this
GAP_PENALTY = 5.0                # ... but prefer mapped channel 5:1


def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))


d = json.load(open(OSM_JSON))
ways = [{"id": e["id"], "name": e.get("tags", {}).get("name", ""),
         "pts": [(g["lat"], g["lon"]) for g in e["geometry"]]}
        for e in d["elements"] if e.get("geometry")]
print(f"{len(ways)} waterway ways in bbox")

# ---------------------------------------------------------------- graph -----
key = lambda p: (round(p[0], 6), round(p[1], 6))
coord, adj = {}, {}


def link(a, b, w):
    adj.setdefault(a, []).append((b, w))
    adj.setdefault(b, []).append((a, w))


for w in ways:
    for i in range(len(w["pts"]) - 1):
        a, b = key(w["pts"][i]), key(w["pts"][i + 1])
        coord[a], coord[b] = w["pts"][i], w["pts"][i + 1]
        if a != b:
            link(a, b, hav(w["pts"][i], w["pts"][i + 1]))
print(f"graph: {len(adj)} nodes from mapped channel segments")

# heal small gaps (way endpoints that OSM leaves unjoined) via a grid hash
cell = GAP_M / 111000.0
grid = {}
for k2, p in coord.items():
    grid.setdefault((int(p[0] / cell), int(p[1] / cell)), []).append(k2)
bridges = 0
for k2, p in coord.items():
    ci, cj = int(p[0] / cell), int(p[1] / cell)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for k3 in grid.get((ci + di, cj + dj), ()):
                if k3 <= k2:
                    continue
                dd = hav(p, coord[k3])
                if 0 < dd * 1000 <= GAP_M:
                    link(k2, k3, dd * GAP_PENALTY)
                    bridges += 1
print(f"       {bridges} penalised bridge edges <= {GAP_M:.0f} m")

nearest = lambda pt: min(coord, key=lambda k2: hav(coord[k2], pt))
start = nearest(CIRQUE)
print(f"cirque outlet node {coord[start]} ({hav(coord[start], CIRQUE)*1000:.0f} m "
      f"from the cirque waypoint)")

dist = {start: 0.0}
prev = {}
pq = [(0.0, start)]
while pq:
    dcur, u = heapq.heappop(pq)
    if dcur > dist.get(u, 1e18) + 1e-9:
        continue
    for v, w in adj.get(u, ()):
        nd = dcur + w
        if nd < dist.get(v, 1e18) - 1e-9:
            dist[v] = nd
            prev[v] = u
            heapq.heappush(pq, (nd, v))
# the terminus is the REACHABLE node nearest Pokhara, not the nearest node
# outright: OSM leaves isolated ditch fragments in the Pokhara valley and the
# absolute nearest node sits on one of them.
goal = min(dist, key=lambda k2: hav(coord[k2], POKHARA))
off_goal = hav(coord[goal], POKHARA)
print(f"terminus node {coord[goal]} ({off_goal*1000:.0f} m from the Pokhara "
      f"waypoint), {dist[goal]:.1f} km of routed channel from the cirque")
if off_goal > 2.0:
    raise SystemExit("routed network does not reach Pokhara")

chain, u = [], goal
while u != start:
    chain.append(coord[u])
    u = prev[u]
chain.append(coord[start])
chain.reverse()

# the avalanche leg: source cliff -> cirque floor is a FALL, not a river
path = [SOURCE] + chain
cum = [0.0]
for i in range(1, len(path)):
    cum.append(cum[-1] + hav(path[i - 1], path[i]))
print(f"routed path: source -> cirque {cum[len(path)-len(chain)]:.1f} km "
      f"(avalanche fall), cirque -> Pokhara {cum[-1]-cum[len(path)-len(chain)]:.1f} km "
      f"along mapped channel; total {cum[-1]:.1f} km, {len(path)} vertices")

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


print("\nindependent checks (no model involved):")
for nm, pt in [("Sabche Cirque", CIRQUE), ("Kharapani", KHARAPANI),
               ("Pokhara", POKHARA)]:
    km, off = path_km(pt)
    print(f"  {nm:16s} path km {km:6.1f}   offset {off*1000:5.0f} m")

# ------------------------------------------------------------ elevations ----
# Slot-canyon correction: a 30 m DEM sampled on the channel centreline in a
# deeply incised gorge reads whichever pixel the point lands in, which is
# often the wall rather than the floor. Sample a small cross-shaped stencil
# (+-1 and +-2 pixels perpendicular to the local flow direction) and take the
# MINIMUM - the floor is the lowest thing in the neighbourhood by definition.
# This is geometry, not tuning: it makes no reference to any observation.
STENCIL_M = [-60.0, -30.0, 0.0, 30.0, 60.0]


def offsets(i):
    a = samples[max(i - 1, 0)]
    b = samples[min(i + 1, len(samples) - 1)]
    dla, dlo = b[1] - a[1], (b[2] - a[2]) * math.cos(math.radians(a[1]))
    nrm = math.hypot(dla, dlo) or 1.0
    pla, plo = -dlo / nrm, dla / nrm          # unit normal in "degree" space
    out = []
    for s in STENCIL_M:
        dd = s / 111000.0
        out.append((samples[i][1] + pla * dd,
                    samples[i][2] + plo * dd / math.cos(math.radians(samples[i][1]))))
    return out


locs = [p for i in range(len(samples)) for p in offsets(i)]
print(f"\nfetching {len(locs)} elevations "
      f"({len(samples)} nodes x {len(STENCIL_M)} stencil points)")
elevs = []
for i in range(0, len(locs), 100):
    batch = locs[i:i + 100]
    req = urllib.request.Request(
        "https://api.opentopodata.org/v1/mapzen",
        data=json.dumps({"locations":
                         "|".join(f"{p[0]},{p[1]}" for p in batch)}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dd = json.loads(resp.read())
    assert dd["status"] == "OK", dd
    elevs.extend(r["elevation"] for r in dd["results"])
    time.sleep(1.1)
print(f"  got {len(elevs)}")

ns = len(STENCIL_M)
z_floor = [min(e for e in elevs[i * ns:(i + 1) * ns] if e is not None)
           for i in range(len(samples))]
z_centre = [elevs[i * ns + ns // 2] for i in range(len(samples))]
drop = [c - f for c, f in zip(z_centre, z_floor)]
print(f"  stencil floor-snap: mean {sum(drop)/len(drop):.0f} m, "
      f"max {max(drop):.0f} m below centreline")

with open(PROFILE, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dist_km", "lat", "lon", "elev_m", "elev_centre_m"])
    for s, zf, zc in zip(samples, z_floor, z_centre):
        w.writerow([f"{s[0]:.3f}", f"{s[1]:.6f}", f"{s[2]:.6f}",
                    f"{zf:.1f}", f"{zc:.1f}"])
print(f"wrote {len(samples)} pts -> profile.csv "
      f"({z_floor[0]:.0f} m -> {z_floor[-1]:.0f} m)")
