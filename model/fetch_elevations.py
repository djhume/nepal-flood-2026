#!/usr/bin/env python3
"""Sample elevations along data/river_path.csv (opentopodata, mapzen dataset,
100 points/request, 1 req/s) -> data/river_profile.csv"""
import csv, json, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

rows = list(csv.DictReader(open(os.path.join(DATA, "river_path.csv"))))
print(f"{len(rows)} points")

elevs = []
for i in range(0, len(rows), 100):
    batch = rows[i:i + 100]
    locs = "|".join(f"{r['lat']},{r['lon']}" for r in batch)
    req = urllib.request.Request(
        "https://api.opentopodata.org/v1/mapzen",
        data=json.dumps({"locations": locs}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read())
    assert d["status"] == "OK", d
    elevs.extend(r["elevation"] for r in d["results"])
    print(f"  batch {i // 100 + 1}: {len(d['results'])} elevations")
    time.sleep(1.2)

with open(os.path.join(DATA, "river_profile.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dist_km", "lat", "lon", "elev_m"])
    for r, e in zip(rows, elevs):
        w.writerow([r["dist_km"], r["lat"], r["lon"], e])
print(f"wrote {len(elevs)} -> data/river_profile.csv")
print(f"scar end: {elevs[0]:.0f} m | devghat end: {elevs[-1]:.0f} m")
