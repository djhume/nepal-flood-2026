#!/usr/bin/env python3
"""
Phase F — SETI 2012 HINDCAST, v2. The intermediate-regime test, re-run on a
corrected channel and with the entrainment term installed.

WHAT CHANGED SINCE v1 (and why this run is labelled honestly)

1. THE PROFILE WAS BROKEN. v1's greedy OSM walk bridged straight lines across
   the Sabche Cirque rim wherever it could not find a continuing waterway, so
   the sampled "river" oscillated by 1,500 m through the gorge; the monotone
   descent clamp then flattened 31 of 54 km to a constant 1,020 m. v1's
   timing pass was obtained on a channel with essentially no gradient over its
   whole runout. build_path2.py replaces the walk with a Dijkstra route over
   the mapped waterway graph (OSM way 352604044 carries the Seti continuously
   from the cirque outlet to below Kharapani; v1 simply never chained onto it)
   and snaps elevations to the local valley floor. 23% of nodes are now
   clamped, in one 3 km patch at the cirque outlet, against 64% before.
   -> This is NOT a fresh blind test. The pre-registered anchors are untouched
      and every dial constant is still frozen at its Trishuli/Chamoli value,
      but we have seen this event's answer once. Call it what it is: a re-run
      on corrected input data, reported alongside what v1 said.

2. ENTRAINMENT EXISTS NOW (model/core.py). v1's headline failure was
   sediment: w = 0.92 modelled against 0.47 measured (rho = 1.88 g/cm3). The
   model could deposit and not erode. Two closures are now available, both
   with literature constants, and this run scores both against that density —
   out of sample, since nothing in either closure was chosen with reference
   to it.

3. THE "20 km" PATH AGREEMENT IS WITHDRAWN. v1 reported the stitched dam ->
   Kharapani distance as 20.0 km against a published "20 km downstream", and
   called it an independent consistency check. On the corrected route that
   distance is 14.0 km (25.2 km from the detachment). The v1 agreement was a
   coincidence of the broken path and should not be cited.

BLIND PROTOCOL, unchanged: MU_WET = 0.02, W_SAT = 0.25, TAU_Y0 = 400 Pa,
U_DEP = 1.0 m/s, T_DEP = 120 s, mu_dry from Scheidegger(V), and now the
entrainment constants (Takahashi's DELTA_E/DELTA_D, Frank's K_TAU, C_STAR,
tan phi, W_SETTLE) — all fixed in core.py from the literature, none fitted to
a Seti observation. Event inputs come only from research/seti-2012-anchors.md.

SCORED AGAINST (all out of sample):
    Kharapani (path km 25.2) at 28.1 min after the 09:09:56 seismic impact.
    Pokhara (km 49.6) at ~85 min (medium).
    Peak discharge ~935 m3/s (medium; personal communication).
    Flow density 1.88 g/cm3 => water volume fraction w ~ 0.47.
"""
import csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "model"))
from core import (MU_WET, W_SAT, TAU_Y0, U_DEP, T_DEP, H_ERODE,
                  mu_dry_scheidegger, Reach, step, arrival_fn, entrain_opts,
                  c_eq_takahashi)

# ------------------------------------------------------------- geometry -----
rows = list(csv.DictReader(open(os.path.join(HERE, "profile.csv"))))
x_km = np.array([float(r["dist_km"]) for r in rows])
zp = np.minimum.accumulate(np.array([float(r["elev_m"]) for r in rows]))
k = 5
z = np.convolve(np.pad(zp, k, mode="edge"),
                np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
N = len(x_km)
DX = float(np.mean(np.diff(x_km))) * 1000.0

KM_CIRQUE = 9.2        # routed cirque outlet — the avalanche leg ends here
KM_DAM = 11.2          # rockfall dam in the headwater gorge (Hanisch et al.:
                       # the blockage sat in the steep gorge, impounding the
                       # cirque's meltwater behind it)
KM_KHARAPANI = 25.2    # OSM "Kharpani" hamlet, 78 m off the routed line
KM_POKHARA = 49.6

# Pre-monsoon (5 May) baseflow: snowmelt-fed, small. Seti at Pokhara mean
# annual ~50 m3/s; early May is the low season. Class values, not fitted.
QB_X = np.array([0.0, KM_DAM, KM_KHARAPANI, KM_POKHARA])
QB_Q = np.array([2.0, 6.0, 25.0, 45.0])
Qb = np.interp(x_km, QB_X, QB_Q)

# WIDTHS. The Seti gorge below the cirque is a slot canyon (famously only
# metres wide where it cuts Pokhara), and v1 gave the WHOLE path that
# character — including path km 3.5-9.2, which is the SABCHE CIRQUE, a
# glacial amphitheatre kilometres across. DEM transects on this line
# (widths.py) find ground within 60 m of the floor out to +-1,000-1,500 m
# through km 6-10 and walls climbing 250-1,100 m within 600 m from km 12 down:
# a wide basin, then confinement. Routing a 22 Mm3 avalanche through a 60 m
# channel in the basin makes it a ~300 m deep dam-break wave; giving the
# cirque its mapped width lets the avalanche do what it observably did, which
# is spread across the cirque floor and stop there.
#
# W_CIRQUE is a MAP READ (swept below), not a fitted constant, and it was
# wrong in v1 as well as v2 — the correction is independent of any timing.
W_CIRQUE = 2500.0
CIRQUE_KM = (3.5, 9.2)


def widths(w_cirque=W_CIRQUE, mode="class"):
    if mode == "dem":
        wr = list(csv.DictReader(open(os.path.join(HERE, "widths.csv"))))
        w = np.interp(x_km, [float(r["dist_km"]) for r in wr],
                      [float(r["width_m"]) for r in wr])
    else:
        w = np.interp(x_km, [0, 9.2, 12, 20, 25, 35, KM_POKHARA],
                      [300, 25, 25, 30, 40, 50, 60])
    cir = (x_km >= CIRQUE_KM[0]) & (x_km <= CIRQUE_KM[1])
    w = np.where(cir, w_cirque, w)
    return w


wn = widths()
nn = np.interp(x_km, [0, 9, 25, KM_POKHARA], [0.060, 0.055, 0.045, 0.035])

R = Reach(x_km, z, wn, nn, Qb)

# ------------------------------------------------------------ the event -----
V_AVA = 22e6           # Kargel/NASA; NHESS lineage says 33e6 - swept below
W0 = 0.10              # liquid fraction of the avalanche (rock+ice, dry-ish)
X_REL, T_REL = 1.2, 180.0
V_IMP = 3.0e6          # impounded lake behind the rockfall dam: "several
                       # million cubic metres" total (SANDRP/Kargel) - swept
KM_IMP_SPREAD = 2.0    # the impoundment occupies ~2 km of gorge behind the dam


def simulate(v_ava=V_AVA, v_imp=V_IMP, w0=W0, mu_dry=None, dt=0.4,
             t_end=3.0 * 3600.0, entrain=None, reach=None, h_erode=H_ERODE):
    if mu_dry is None:
        mu_dry = mu_dry_scheidegger(v_ava)
    R = reach if reach is not None else globals()["R"]
    wn, nn = R.wn, R.nn
    R.h_erode = h_erode
    S0 = np.maximum(-np.gradient(z, x_km * 1000), 1e-4)
    h = np.maximum((Qb * nn / (wn * np.sqrt(S0))) ** 0.6, 0.05)
    st = R.new_state(h)
    # settle the pre-monsoon channel (dial at pure water -> mu = 0)
    for _ in range(int(1200 / dt)):
        st = step(st, R, dt, mu_dry=0.3, deposit=False, side_valleys=False)
    # THE IMPOUNDMENT: a standing lake behind the rockfall dam at KM_DAM,
    # present before the avalanche arrives.
    imp = (x_km >= KM_DAM - KM_IMP_SPREAD) & (x_km <= KM_DAM)
    d_imp = v_imp / (wn[imp].sum() * DX)
    st["h"][imp] += d_imp
    st["hw"][imp] += d_imp
    h0 = st["h"].copy()
    st["umax"] = np.zeros(N - 1)
    st["ero"][:] = 0.0
    st["dep"][:] = 0.0
    st["bed"][:] = 0.0
    rel = x_km <= X_REL
    wsum = wn[rel].sum() * DX
    stj = {"Kharapani": int(np.argmin(np.abs(x_km - KM_KHARAPANI))),
           "Pokhara": int(np.argmin(np.abs(x_km - KM_POKHARA)))}
    rec = {"t": [], "front": [], "w_front": []}
    for s in stj:
        rec[s] = {"q": [], "h": [], "w": []}
    save = max(int(10.0 / dt), 1)
    for it in range(int(t_end / dt)):
        t = it * dt
        if t < T_REL:
            qr = 2 * v_ava / T_REL * (1 - abs(2 * t / T_REL - 1))
            dh = qr * dt / wsum
            st["h"][rel] += dh
            st["hw"][rel] += dh * w0
            st["hwr"][rel] += dh * w0
            st["hr"][rel] += dh * (1 - w0)
        st = step(st, R, dt, mu_dry, side_valleys=False, entrain=entrain)
        if it % save == 0:
            h, hw, Qi = st["h"], st["hw"], st["Qi"]
            rec["t"].append(t / 60.0)
            risen = x_km[h - h0 > 0.5]
            fk = risen.max() if len(risen) else 0.0
            rec["front"].append(fk)
            j = min(int(np.argmin(np.abs(x_km - fk))), N - 2) if fk else 0
            rec["w_front"].append(hw[j] / max(h[j], 1e-6))
            for s, jj in stj.items():
                j2 = min(jj, N - 2)
                rec[s]["q"].append(Qi[j2])
                rec[s]["h"].append(h[jj])
                rec[s]["w"].append(hw[jj] / max(h[jj], 1e-6))
    out = {k2: (np.array(v) if not isinstance(v, dict)
                else {kk: np.array(vv) for kk, vv in v.items()})
           for k2, v in rec.items()}
    front = np.maximum.accumulate(out["front"])
    out.update(arrival=arrival_fn(front, out["t"]), front=front,
               umax=st["umax"], bed=st["bed"], ero=st["ero"], dep=st["dep"],
               mu_dry=mu_dry, wn=wn)
    return out


# ---------------------------------------------------------------- score -----
OBS = {"Kharapani": (KM_KHARAPANI, 28.1), "Pokhara": (KM_POKHARA, 85.0)}
OBS_W = 0.47            # from rho = 1.88 g/cm3 with quartz solids
OBS_QPK = 935.0


def score(r, name):
    print(f"\n--- {name} (mu_dry={r['mu_dry']:.3f}) ---")
    for s, (km, obs) in OBS.items():
        ta = r["arrival"](km)
        if np.isfinite(ta):
            v = "PASS" if abs(ta - obs) / obs <= 0.5 else "FAIL"
            print(f"  {s:10s} km {km:5.1f}  model {ta:6.1f} min   obs {obs:5.1f}"
                  f"   {100*(ta-obs)/obs:+6.0f}%  -> {v}")
        else:
            print(f"  {s:10s} km {km:5.1f}  model  never reached   obs {obs}"
                  f"  -> FAIL")
    t_d, t_k = r["arrival"](KM_DAM), r["arrival"](KM_KHARAPANI)
    if np.isfinite(t_k) and np.isfinite(t_d) and t_k > t_d:
        print(f"  dam->Kharapani mean front speed "
              f"{(KM_KHARAPANI-KM_DAM)*1e3/((t_k-t_d)*60):5.1f} m/s   obs ~12")
    q = r["Kharapani"]["q"]; tt = r["t"]
    m = tt > 2
    i = int(np.argmax(np.where(m, q, -1)))
    print(f"  peak Q at Kharapani {q[i]:6,.0f} m3/s at {tt[i]:5.1f} min"
          f"   obs ~{OBS_QPK:.0f}")
    wk = r["Kharapani"]["w"][i]
    v = "PASS" if abs(wk - OBS_W) / OBS_W <= 0.5 else "FAIL"
    print(f"  water fraction w at Kharapani at the peak {wk:.2f}"
          f"   obs ~{OBS_W} (rho 1.88 g/cm3)   {100*(wk-OBS_W)/OBS_W:+.0f}%"
          f"  -> {v}")
    e = float((r["ero"] * r["wn"] * DX).sum() / 1e6)
    d = float((r["dep"] * r["wn"] * DX).sum() / 1e6)
    if e or d:
        print(f"  bed exchange: eroded {e:5.2f} Mm3, deposited {d:5.2f} Mm3"
              f"  (net {'erosional' if e > d else 'depositional'})")
    print(f"  stranded solids {r['bed'].sum()/1e6:5.1f} Mm3 of "
          f"{V_AVA/1e6*(1-W0):4.1f} Mm3 released")


print(f"Seti 2012 hindcast v2 — path {x_km[-1]:.1f} km, "
      f"{z[0]:.0f} m -> {z[-1]:.0f} m")
print(f"cirque outlet km {KM_CIRQUE}, dam km {KM_DAM}, Kharapani km "
      f"{KM_KHARAPANI} ({KM_KHARAPANI-KM_DAM:.1f} km below the dam; "
      f"v1 reported 20.0 km on a path since found broken)")
print(f"gorge bed slope km {KM_DAM}-{KM_KHARAPANI}: mean "
      f"{R.S_bed[(x_km>=KM_DAM)&(x_km<=KM_KHARAPANI)].mean():.3f} "
      f"(v1's clamped profile: 0.000)")
print(f"Takahashi capacity c_eq on that reach: "
      f"{R.c_eq[(x_km>=KM_DAM)&(x_km<=KM_KHARAPANI)].mean():.3f} mean, "
      f"{R.c_eq[(x_km>=KM_DAM)&(x_km<=KM_KHARAPANI)].max():.3f} max; "
      f"at Kharapani {float(c_eq_takahashi(R.S_bed[int(np.argmin(abs(x_km-KM_KHARAPANI)))])):.3f}")
print(f"FROZEN: MU_WET={MU_WET}, W_SAT={W_SAT}, TAU_Y0={TAU_Y0}, "
      f"U_DEP={U_DEP}, T_DEP={T_DEP}, H_ERODE={H_ERODE}")

R_v1geom = Reach(x_km, z, np.interp(x_km, [0, 9, 12, 20, 25, 35, KM_POKHARA],
                                    [60, 25, 25, 30, 40, 50, 60]), nn, Qb)

print("\n" + "#" * 78)
print("# PART 1 — what v1's CONFIGURATION does on a CORRECT channel.")
print("# Same widths as v1 (slot canyon everywhere, cirque included), same")
print("# release, same frozen dial; only the profile bug is fixed.")
print("#" * 78)
v1cfg = simulate(reach=R_v1geom)
score(v1cfg, "v1 configuration, corrected profile")
print("""
  READ THIS AS A FAILED TEST, NOT A DETAIL. v1 reported Kharapani -23% and
  Pokhara +18%, both PASS. On a channel that actually has a gradient the same
  configuration arrives 4x early and the peak is 27x the observed discharge.
  The v1 pass was produced by 31 km of accidentally flat channel, and the
  RESULTS.md claim that the timing physics ported to a third event with zero
  recalibration does not survive this. The pre-registered failure mode --
  "a model tuned on Langtang's fast wave would fail here by running away" --
  is exactly what happened once the terrain was real.""")

print("\n" + "#" * 78)
print("# PART 2 — one geometry correction, declared as post-hoc.")
print("# The Sabche Cirque is kilometres wide and v1 modelled it as a 60 m")
print("# slot. Widening it to its mapped width is a map fact, independent of")
print("# any Seti timing -- but we are making it AFTER seeing the failure, so")
print("# nothing below is a blind result. It is a mechanism demonstration.")
print("#" * 78)
base = simulate()
score(base, f"cirque {W_CIRQUE:.0f} m wide, NO entrainment")

tak = simulate(entrain=entrain_opts("takahashi"))
score(tak, "cirque + ENTRAINMENT, Takahashi capacity closure")

shr = simulate(entrain=entrain_opts("shear"))
score(shr, "cirque + ENTRAINMENT, Frank shear closure")

print("\n=== how much of the avalanche stays in the cirque? ===")
for r, nm in [(base, "no entrainment"), (tak, "Takahashi"), (shr, "shear")]:
    cir = (x_km >= CIRQUE_KM[0]) & (x_km <= CIRQUE_KM[1])
    print(f"  {nm:16s} stranded in cirque {r['bed'][cir].sum()/1e6:5.1f} Mm3 "
          f"of {V_AVA/1e6*(1-W0):4.1f} Mm3 solids released; "
          f"below the cirque {r['bed'][~cir].sum()/1e6:5.1f} Mm3")

print("\n=== does the model still REQUIRE the impoundment? "
      "(cirque geometry + Takahashi entrainment) ===")
for vi in [0.0, 1e6, 3e6, 6e6]:
    r = simulate(v_imp=vi, entrain=entrain_opts("takahashi"))
    ta_k, ta_p = r["arrival"](KM_KHARAPANI), r["arrival"](KM_POKHARA)
    print(f"  impoundment {vi/1e6:3.0f} Mm3: Kharapani "
          f"{('%6.1f min' % ta_k) if np.isfinite(ta_k) else '  never  '} "
          f"({100*(ta_k-28.1)/28.1:+5.0f}%)   Pokhara "
          f"{('%6.1f min' % ta_p) if np.isfinite(ta_p) else '  never'}")

print("\n=== sensitivities (cirque geometry + Takahashi) ===")
for nm, kw in [("33 Mm3 avalanche (NHESS)", dict(v_ava=33e6)),
               ("wetter avalanche w0=0.25", dict(w0=0.25)),
               ("drier avalanche w0=0.02", dict(w0=0.02)),
               ("erodible layer 1 m", dict(h_erode=1.0)),
               ("erodible layer 10 m", dict(h_erode=10.0))]:
    score(simulate(entrain=entrain_opts("takahashi"), **kw), nm)
for nm, wc in [("cirque 1,500 m", 1500.0), ("cirque 3,500 m", 3500.0)]:
    Rw = Reach(x_km, z, widths(w_cirque=wc), nn, Qb)
    score(simulate(entrain=entrain_opts("takahashi"), reach=Rw), nm)
Rdem = Reach(x_km, z, widths(mode="dem"), nn, Qb)
score(simulate(entrain=entrain_opts("takahashi"), reach=Rdem),
      "DEM-measured widths below the cirque (30 m DEM reads the rim, not the "
      "slot)")
for nm, eo in [("no settling cap", dict(w_settle=1e9)),
               ("settling cap x1/5 (silt)", dict(w_settle=0.005))]:
    score(simulate(entrain=entrain_opts("takahashi", **eo)), nm)

# ---------------------------------------------------------------- plot ------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
ax = axes[0]
for r, c, lbl in [(base, "#9a7146", "no entrainment"),
                  (tak, "#164a70", "Takahashi entrainment"),
                  (shr, "#2b6b9c", "shear entrainment")]:
    ax.plot(r["t"], r["front"], color=c, lw=2.0, label=lbl)
for s, (km, obs) in OBS.items():
    ax.plot(obs, km, "kv", ms=9)
    ax.annotate(f"{s} obs {obs:.0f} min", (obs, km), fontsize=8,
                textcoords="offset points", xytext=(6, -12))
ax.axhline(KM_DAM, color="#9a7146", ls="--", lw=1, label="rockfall dam / lake")
ax.set_xlim(0, 120); ax.set_ylim(0, KM_POKHARA + 2)
ax.set_xlabel("minutes after 09:09:56 NPT"); ax.set_ylabel("path km")
ax.set_title("Front trajectory vs the photo clock\n(corrected channel profile)")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[1]
for r, c, lbl in [(base, "#9a7146", "no entrainment"),
                  (tak, "#164a70", "Takahashi"), (shr, "#2b6b9c", "shear")]:
    ax.plot(r["t"], r["Kharapani"]["q"], color=c, label=lbl)
ax.axhline(OBS_QPK, color="k", ls=":", lw=1.2, label="obs peak ~935 m³/s")
ax.set_xlim(0, 120)
ax.set_xlabel("minutes after impact"); ax.set_ylabel("discharge (m³/s)")
ax.set_title("Hydrographs at Kharapani")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[2]
for r, c, lbl in [(base, "#9a7146", "no entrainment"),
                  (tak, "#164a70", "Takahashi"), (shr, "#2b6b9c", "shear")]:
    ax.plot(r["t"], r["Kharapani"]["w"], color=c, label=lbl)
ax.axhline(OBS_W, color="k", ls=":", lw=1.4,
           label="obs w≈0.47 (ρ=1.88 g/cm³)")
ax.axhline(W_SAT, color="#9a7146", ls="--", lw=1, label="W_SAT (dial knee)")
ax.set_xlim(0, 120); ax.set_ylim(0, 1.05)
ax.set_xlabel("minutes after impact"); ax.set_ylabel("water volume fraction")
ax.set_title("The entrainment target:\nthe dial's own variable vs a published density")
ax.legend(fontsize=8); ax.grid(alpha=.25)

fig.suptitle("Seti 2012 v2 — corrected channel route, entrainment installed; "
             "dial and entrainment constants frozen at literature values",
             fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "seti_hindcast.png"), dpi=140)
print("\nfigure -> seti_hindcast.png")
