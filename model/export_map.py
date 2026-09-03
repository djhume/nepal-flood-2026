#!/usr/bin/env python3
"""Append plan-view map data (main path, tributaries, junctions, POIs) to
report/chart_data.json, from the OSM extracts."""
import csv, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
CHART = os.path.join(HERE, "..", "report", "chart_data.json")

def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2-la1)/2)**2
         + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2)
    return 2*R*math.asin(math.sqrt(h))

# main path with km (already stitched)
main = []
for r in csv.DictReader(open(os.path.join(DATA, "river_path.csv"))):
    main.append([float(r["lat"]), float(r["lon"]), float(r["dist_km"])])
main_ds = main[::2]

# tributaries / arms to draw (name in OSM -> display label)
WANT = {
    "Chhochen Khola": "Chhochen Khola",
    "普热普藏布": "Purepu Tsangpo (2025 GLOF)",
    "东林藏布": "Lhende upper arm",
    "吉隆藏布": "Kyirong Tsangpo (upstream arm)",
    "Langtang Khola": "Langtang Khola",
    "Chilime Khola": "Chilime Khola",
    "Trisuli Khola": "Tadi/Trisuli Khola",
    "Salankhu Khola": "Salankhu Khola",
    "Mahesh-Khola": "Mahesh Khola",
    "Budhi Gandaki": "Budhi Gandaki",
    "Marsyangdi": "Marsyangdi",
    "Kali Gandaki": "Kali Gandaki",
}
tribs, seen = {}, set()
for fname in ("osm_rivers.json", "osm_rivers_lower.json"):
    d = json.load(open(os.path.join(DATA, fname)))
    for e in d["elements"]:
        nm = e.get("tags", {}).get("name", "")
        if nm in WANT and e.get("geometry") and e["id"] not in seen:
            seen.add(e["id"])
            pts = [[round(g["lat"], 5), round(g["lon"], 5)]
                   for g in e["geometry"]][::3]
            if len(pts) >= 2:
                tribs.setdefault(WANT[nm], []).append(pts)

# junction = the tributary MOUTH: among each system's segment ENDPOINTS, the
# one nearest the main path (closest-approach of any mid-point would mark
# where a headwater merely passes near the corridor, not where it joins)
junctions = []
for label, segs in tribs.items():
    best = (1e9, None)
    for seg in segs:
        for p in (seg[0], seg[-1]):
            for m in main[::3]:
                dd = hav(p, m)
                if dd < best[0]:
                    best = (dd, m)
    if best[1] and best[0] < 1.5:
        junctions.append({"label": label, "lat": best[1][0],
                          "lon": best[1][1], "km": round(best[1][2], 1)})

POIS = [
    {"label": "collapse scar 08:37", "lat": 28.2765, "lon": 85.5194, "kind": "scar"},
    {"label": "Gyirong Port CCTV 08:44 — the T-junction", "lat": 28.2781, "lon": 85.3770, "kind": "camera"},
    {"label": "Syabrubesi", "lat": 28.1606, "lon": 85.3345, "kind": "town"},
    {"label": "Betrawati", "lat": 27.9700, "lon": 85.1800, "kind": "gauge"},
    {"label": "Galchhi", "lat": 27.8230, "lon": 84.9720, "kind": "gauge"},
    {"label": "Malekhu", "lat": 27.8125, "lon": 84.8322, "kind": "gauge"},
    {"label": "Muglin", "lat": 27.8560, "lon": 84.5590, "kind": "town"},
    {"label": "Devghat gauge", "lat": 27.7095, "lon": 84.4290, "kind": "gauge"},
]

# The hydropower cascade. ALL run-of-river (no storage reservoir exists on
# this river system). Positions: OSM where mapped, else dossier-based approx.
# status: "op" = operating pre-event, "uc" = under construction.
PLANTS = [
    {"label": "Rasuwagadhi 111 MW", "lat": 28.2760, "lon": 85.3790, "status": "op", "dx": -10, "dy": -8, "anchor": "end"},
    {"label": "Chilime 22 MW ~", "lat": 28.2100, "lon": 85.3100, "status": "op", "dx": -10, "dy": 4, "anchor": "end"},
    {"label": "Upper Trishuli-1 216 MW (u/c)", "lat": 28.0639, "lon": 85.2066, "status": "uc", "dx": 10, "dy": -4, "anchor": "start"},
    {"label": "Upper Trishuli 3A 60 MW", "lat": 28.0253, "lon": 85.1864, "status": "op", "dx": 10, "dy": 6, "anchor": "start"},
    {"label": "UT-3B 37 MW + 220 kV hub (u/c) ~", "lat": 27.9900, "lon": 85.1720, "status": "uc", "dx": 10, "dy": 12, "anchor": "start"},
    {"label": "Trishuli 24 MW", "lat": 27.9215, "lon": 85.1460, "status": "op", "dx": 10, "dy": 2, "anchor": "start"},
    {"label": "Devighat 14 MW ~", "lat": 27.8747, "lon": 85.1565, "status": "op", "dx": 10, "dy": 12, "anchor": "start"},
]

d = json.load(open(CHART))
d["map"] = {"main": [[round(a,5), round(b,5), round(c,2)] for a,b,c in main_ds],
            "tribs": tribs, "junctions": junctions, "pois": POIS,
            "plants": PLANTS}
json.dump(d, open(CHART, "w"), separators=(",", ":"))
print(f"map appended: {len(main_ds)} main pts, "
      f"{sum(len(s) for s in tribs.values())} trib segs, "
      f"{len(junctions)} junctions; {os.path.getsize(CHART)//1024} KB total")
for j in sorted(junctions, key=lambda j: j["km"]):
    print(f"  junction {j['label']:28s} at path-km {j['km']}")
