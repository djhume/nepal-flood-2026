#!/usr/bin/env python3
"""
PROFILE INTEGRITY CHECK — the gate that would have caught the Seti 2012 error
before it reached the site as a published pass.

WHY THIS EXISTS. Every routing model in this project reads a channel profile
built the same way: stitch named OSM river ways into one downstream path
(model/build_profile.py), bridge any gap between them with a STRAIGHT LINE,
sample elevations along it, then clamp the result to monotone descent with
`np.minimum.accumulate` to remove DEM noise.

Two of those steps are safe apart and dangerous together. A straight-line
bridge does not follow the valley — over a few kilometres it can fly across a
ridge, and the sampled elevations then read RIDGE TOPS, hundreds or thousands
of metres above the bed. The monotone clamp meets that spurious high point and
holds every downstream node at it until the real bed falls below it again. The
clamp is a noise filter; against a bridge artefact it is a bulldozer.

That is exactly what happened to the Seti 2012 hindcast. A 1,882 m spurious
step at km 9.6 held 31 of 54 km at a constant 1,020 m — 64% of nodes clamped,
the entire runout past Kharapani at ZERO GRADIENT. A flood on a flat bed is
driven only by its own depth gradient, so the model was slowed by roughly the
amount needed to match the observed arrival times, for a reason that had
nothing to do with its physics. It was reported here as a clean pass for a day
before the profile was looked at, and the finding had to be withdrawn.

hindcast/seti/RESULTS.md closed with the fix: "A profile-integrity check
(longest flat run, largest raw upward step) now belongs in every path build."
This is that check. It was specified on 3 September and not built until the
6 September audit noticed it was still only a sentence.

AUDIT THE PROFILE THE MODEL ACTUALLY USES. Every routing model here runs the
same two-step pipeline, and the check has to follow it to the end:

    zp = np.minimum.accumulate(z_raw)          # 1. monotone-descent clamp
    z  = boxcar(zp, k=5)                       # 2. ~4.4 km smoothing

The first draft of this check audited `zp` and reported the live Trishuli
profile as FAILING on flat fraction (52%). That was the checker's error, not
the profile's: 400 m sampling of a lower river whose true gradient is 1.6 m/km
puts the real fall per step (0.6 m) BELOW the DEM's vertical noise, so the
clamp turns a genuine gentle slope into a staircase — and then the 4.4 km
boxcar averages that staircase back out. In the profile the model consumes,
the Trishuli corridor is 1.4% flat with a longest flat run of 2.0 km, and the
reach-average slopes match the raw DEM to within 10% (5.25 vs 5.29, 2.52 vs
2.74, 1.91 vs 1.63 m/km over the three lower reaches). The staircase is real
and it is harmless. Reported at the wrong stage it looked alarming.

Smoothing is not a fix for a bridge artefact, though — a 31 km flat survives a
4.4 km boxcar untouched — which is why the gates below are read at the stage
where each defect is actually visible.

WHAT IT MEASURES, per profile, at each stage:
  largest RAW upward step   the bridge artefact itself, before the clamp hides
                            it. Read on the RAW elevations. This is the one
                            that catches Seti, and nothing downstream can.
  clamped %, mean clamp     how hard the clamp had to work
  LONGEST FLAT RUN          longest run of zero gradient in the CONSUMED
                            profile. Survives smoothing only if it is large.
  flat fraction             share of consumed length at zero gradient
  slope floor engaged       share of nodes where the model's S = max(-dz/dx,
                            1e-4) floor binds — a second silent guard that
                            hides a dead channel behind a plausible number

THRESHOLDS. Set so Seti-as-published fails on every gate and the two profiles
the live findings rest on pass, with the reasoning visible rather than tuned:

  largest raw step  > 500 m   FAIL   a river does not climb 500 m. Seti v1:
                                     1,882 m at km 10.4. Trishuli: 96 m.
  longest flat run  > 10 km   FAIL   in the CONSUMED profile. Seti v1: 31 km,
                                     which the boxcar cannot touch.
  flat fraction     > 25 %    FAIL   consumed. Seti v1 65%, Trishuli 1.4%.
  slope floor       > 20 %    FAIL   if a fifth of the channel is running on
                                     the floor rather than on its own gradient,
                                     the profile is not driving the model

A FAIL is not "the model is wrong", it is "the model has not been given a
channel". Read the profile before reading the result.

Run:  python model/check_profile.py            # all known profiles
      python model/check_profile.py PATH.csv   # any one profile
Exit status is non-zero if any profile fails, so it can gate a rebuild.
"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

MAX_FLAT_RUN_KM = 10.0
MAX_RAW_STEP_M = 500.0
MAX_FLAT_FRACTION = 0.25
MAX_FLOOR_FRACTION = 0.20
SMOOTH_K = 5          # the k every model in this repo uses; ~4.4 km at 400 m
SLOPE_FLOOR = 1e-4    # model/unified.py:143, hindcast/*/run_*.py

# (label, path, note) — every profile any model in this repo reads
PROFILES = [
    ("Trishuli (live findings)", "data/river_profile.csv",
     "findings 01-06 all route on this"),
    ("Chamoli 2021 (hindcast)", "hindcast/chamoli/profile.csv",
     "finding 03, the test that stands"),
    ("Seti 2012 (REPAIRED)", "hindcast/seti/profile.csv",
     "finding 03, the test that was withdrawn"),
    ("Seti 2012 (as published, v1)", "hindcast/seti/profile_v1.csv",
     "THE FAILURE THIS CHECK EXISTS FOR — must FAIL"),
]


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    x = np.array([float(r["dist_km"]) for r in rows])
    z = np.array([float(r["elev_m"]) for r in rows])
    return x, z


def boxcar(a, k=SMOOTH_K):
    """The smoothing every model applies after the clamp."""
    return np.convolve(np.pad(a, k, mode="edge"),
                       np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]


def _longest_flat(flat, dx):
    best = cur = 0.0
    for f, d in zip(flat, dx):
        cur = cur + d if f else 0.0
        best = max(best, cur)
    return float(best)


def audit(x, z_raw):
    zp = np.minimum.accumulate(z_raw)       # stage 1: monotone-descent clamp
    z = boxcar(zp)                          # stage 2: what the model consumes

    moved = z_raw - zp
    n_moved = int((moved > 1e-9).sum())
    dx = np.diff(x)

    flat_clamped = np.diff(zp) >= -1e-9     # the staircase, pre-smoothing
    flat_used = np.diff(z) >= -1e-9         # what actually reaches the model

    # the model's own slope floor: S = max(-dz/dx, 1e-4)
    S = -np.gradient(z, x * 1000.0)
    floored = S < SLOPE_FLOOR

    raw_steps = np.diff(z_raw)
    return {
        "n": len(x),
        "length_km": float(x[-1] - x[0]),
        "clamped_pct": 100.0 * n_moved / len(x),
        "mean_clamp_m": float(moved[moved > 1e-9].mean()) if n_moved else 0.0,
        "max_clamp_m": float(moved.max()),
        "longest_flat_km": _longest_flat(flat_used, dx),
        "flat_fraction": float(dx[flat_used].sum() / dx.sum()),
        "flat_fraction_clamped": float(dx[flat_clamped].sum() / dx.sum()),
        "longest_flat_clamped_km": _longest_flat(flat_clamped, dx),
        "floor_fraction": float(floored.mean()),
        "max_raw_step_m": float(raw_steps.max()),
        "max_raw_step_km": float(x[1:][int(np.argmax(raw_steps))]),
        "drop_m": float(z[0] - z[-1]),
    }


def verdict(a):
    fails = []
    if a["longest_flat_km"] > MAX_FLAT_RUN_KM:
        fails.append(f"longest flat run {a['longest_flat_km']:.1f} km "
                     f"> {MAX_FLAT_RUN_KM:.0f}")
    if a["max_raw_step_m"] > MAX_RAW_STEP_M:
        fails.append(f"raw upward step {a['max_raw_step_m']:.0f} m "
                     f"at km {a['max_raw_step_km']:.1f} > {MAX_RAW_STEP_M:.0f}")
    if a["flat_fraction"] > MAX_FLAT_FRACTION:
        fails.append(f"flat fraction {100*a['flat_fraction']:.0f}% "
                     f"> {100*MAX_FLAT_FRACTION:.0f}%")
    if a["floor_fraction"] > MAX_FLOOR_FRACTION:
        fails.append(f"slope floor binds on {100*a['floor_fraction']:.0f}% "
                     f"of nodes > {100*MAX_FLOOR_FRACTION:.0f}%")
    return fails


def report(label, path, note):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        print(f"  {label}\n    SKIP — {path} not present\n")
        return None
    a = audit(*load(full))
    fails = verdict(a)
    mark = "FAIL" if fails else "pass"
    print(f"  [{mark}] {label}")
    print(f"         {path} — {note}")
    print(f"         {a['n']} nodes over {a['length_km']:.1f} km, "
          f"{a['drop_m']:.0f} m of drop")
    print(f"         clamped {a['clamped_pct']:.0f}% of nodes, "
          f"mean {a['mean_clamp_m']:.0f} m, max {a['max_clamp_m']:.0f} m")
    print(f"         CONSUMED profile: longest flat run "
          f"{a['longest_flat_km']:.1f} km, flat fraction "
          f"{100*a['flat_fraction']:.1f}%, slope floor binds "
          f"{100*a['floor_fraction']:.0f}%")
    survives = (a["longest_flat_km"] > 0.5 * a["longest_flat_clamped_km"]
                and a["longest_flat_clamped_km"] > 2.0)
    print(f"         (pre-smoothing staircase was "
          f"{100*a['flat_fraction_clamped']:.0f}% flat, longest "
          f"{a['longest_flat_clamped_km']:.1f} km — "
          f"{'the boxcar CANNOT remove it' if survives else 'the boxcar removes it'})")
    print(f"         largest RAW upward step {a['max_raw_step_m']:.0f} m "
          f"at km {a['max_raw_step_km']:.1f}")
    for f in fails:
        print(f"         !! {f}")
    print()
    return fails


def main():
    print(__doc__.split("WHAT IT MEASURES")[0].strip())
    print("\n" + "=" * 72)
    if len(sys.argv) > 1:
        todo = [(p, p, "given on the command line") for p in sys.argv[1:]]
    else:
        todo = PROFILES
    bad = 0
    for label, path, note in todo:
        f = report(label, path, note)
        if f:
            bad += 1
    print("=" * 72)
    if bad:
        print(f"{bad} profile(s) FAILED the integrity check.")
        print("A failing profile is not a channel. Any model result computed")
        print("on it is measuring the artefact, not the river.")
    else:
        print("all profiles pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
