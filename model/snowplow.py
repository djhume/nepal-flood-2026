#!/usr/bin/env python3
"""
Phase B "snowplow integral" model — 26 Aug 2026 Langtang Lirung -> Trishuli.

1D control-volume routing along the DEM river profile. The debris/flood front
advances at a slope-dependent speed; as it overruns the monsoon channel it
incorporates ("integrates") the standing river water, collects lateral
baseflow, liberates pore water from entrained saturated sediment, and carries
the frictional meltwater generated in the steep upper reach. The wave body
travels slower than the front, so the pulse stretches; the peak travels slower
still and attenuates.

Everything is transparent: each water source is bookkept separately per km.

Calibration targets (path-km measured along our stitched OSM river path;
observed clock times 26 Aug 2026 NPT, collapse 08:37 = t 0):
  front:  border 22.0 km @ 7 min (CCTV, hard)
          Syabrubesi 37.6 km @ 13 min (station loss, soft)
          Betrawati 68.4 km @ 43 min (rising limb killed station)
          Galchhi 107.6 km @ ~150 min (gauge rise ~11:00-12:00, soft)
          Malekhu 117.0 km @ 169 min (danger level 11:26)
          Muglin ~185 km @ 263 min ("past Muglin" 13:00, soft)
  peak:   Betrawati 68.4 km @ ~113 min (geopera ~10:30, soft)
          Devghat 199.2 km @ 443 min (FFD peak 16:00, 5,850 m3/s)
Other targets: FFD "excess water" ~20 Mm3; velocities ~50 m/s upper gorge,
~11 m/s at Syabrubesi opening (geopera); melt energy cap from
calcs/energy_water_budget.py (~5 Mm3 best-evidence).
"""
import csv, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "output")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- profile --
rows = list(csv.DictReader(open(os.path.join(DATA, "river_profile.csv"))))
x_km = np.array([float(r["dist_km"]) for r in rows])
z_raw = np.array([float(r["elev_m"]) for r in rows])

# DEM samples in a gorge sometimes catch canyon walls; enforce monotone
# descent then lightly smooth before taking slopes.
z = np.minimum.accumulate(z_raw)
k = 5  # ~2 km smoothing window
z_s = np.convolve(np.pad(z, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1),
                  mode="same")[k:-k]
S = np.maximum(-np.gradient(z_s, x_km * 1000.0), 1e-4)   # slope, m/m

# Updated 2 Sept from the official DHM/FFD press release (27 Aug, in
# data/ffd_report.pdf): Malekhu warn-crossing 11:20; Kalikhola (near Muglin)
# danger 12.1 m at 14:14 with max 12.35 m (= effectively peak passage);
# Devghat front arrival 15:20, peak 16:00.
FRONT_OBS = [  # (km, minutes, weight)
    (22.0, 7, 3.0), (37.6, 13, 1.0), (68.4, 43, 2.0),
    (107.6, 150, 1.0), (117.0, 163, 2.0), (199.2, 403, 2.0)]
PEAK_OBS = [(68.4, 113, 1.0), (185.0, 337, 1.5), (199.2, 443, 2.0)]

# ------------------------------------------------------- front speed model --
# U_front = a*S^b + c0. The power term is the slope-driven debris-flow/steep-
# torrent regime; c0 is a flood-wave celerity floor (deep-water sqrt(g*h)
# scale, ~8-10 m/s for h~5-10 m) that carries the wave across the low-slope
# lower Trishuli where observed celerity stays ~8-12 m/s despite S -> 0.001.
def front_times(a, b, c0, u_min=3.0, u_max=65.0):
    U = np.clip(a * S ** b + c0, u_min, u_max)
    dx = np.gradient(x_km) * 1000.0
    t = np.cumsum(dx / U) / 60.0          # minutes
    return t - t[0], U

def fit_front():
    best = None
    for a in np.linspace(60, 320, 27):
        for b in np.linspace(0.35, 0.9, 23):
            for c0 in np.linspace(2, 12, 11):
                t, _ = front_times(a, b, c0)
                err = sum(w * (np.interp(km, x_km, t) - m) ** 2
                          for km, m, w in FRONT_OBS)
                if best is None or err < best[0]:
                    best = (err, a, b, c0)
    return best

err, A, B, C0 = fit_front()
t_front, U_front = front_times(A, B, C0)
print(f"front fit: U = {A:.0f}*S^{B:.2f} + {C0:.1f}  (weighted SSE {err:.0f} min^2)")

# peak travels slower: U_peak = c_p * U_front, fit c_p on peak targets
def peak_times(c_p):
    dx = np.gradient(x_km) * 1000.0
    t = np.cumsum(dx / (c_p * U_front)) / 60.0
    return t - t[0]

cps = np.linspace(0.2, 0.9, 71)
errs = [sum(w * (np.interp(km, x_km, peak_times(c)) - m) ** 2
            for km, m, w in PEAK_OBS) for c in cps]
C_P = cps[int(np.argmin(errs))]
t_peak = peak_times(C_P)
print(f"peak celerity factor c_p = {C_P:.2f}")

# ------------------------------------------------------ baseflow / channel --
# monsoon baseflow anchors (m3/s); Budhi Gandaki joins ~km 160, Marsyangdi
# ~km 185 (big monsoon tributaries), so Devghat-reach baseflow ~1,500
QB_X = np.array([0.0, 5.0, 22.0, 37.6, 68.4, 120.0, 159.0, 161.0, 184.0,
                 186.0, 199.2])
QB_Q = np.array([2.0, 30.0, 150.0, 250.0, 500.0, 650.0, 700.0, 1000.0,
                 1050.0, 1450.0, 1500.0])
Q_base = np.interp(x_km, QB_X, QB_Q)
V_RIVER = 3.0                                # mean monsoon velocity, m/s
A_chan = Q_base / V_RIVER                    # wetted cross-section, m2

# ------------------------------------------------------------- water model --
def run(name, W_melt_total=5.3e6, melt_scale_km=10.0,
        f_sweep=0.8, pore_total=9.0e6, pore_lo=5.0, pore_hi=70.0,
        loss_per_km=0.004, impound=0.0e6, impound_km=8.0):
    """March the front downstream; bookkeep water by source (m3)."""
    dx = np.gradient(x_km) * 1000.0
    n = len(x_km)
    melt = np.zeros(n); chan = np.zeros(n); infl = np.zeros(n)
    pore = np.zeros(n); imp = np.zeros(n); lost = np.zeros(n)
    # melt released over the steep upper reach (exponential in x)
    mrel = np.exp(-x_km / melt_scale_km); mrel /= (mrel * dx).sum()
    # pore water over the erosional reach
    prel = ((x_km >= pore_lo) & (x_km <= pore_hi)).astype(float)
    prel /= (prel * dx).sum()
    # impoundment release (brief damming of the Lhende) near impound_km
    irel = np.exp(-0.5 * ((x_km - impound_km) / 2.0) ** 2)
    irel /= (irel * dx).sum()
    dt = np.gradient(t_front) * 60.0         # seconds spent per cell
    for i in range(1, n):
        melt[i] = melt[i-1] + W_melt_total * mrel[i] * dx[i]
        chan[i] = chan[i-1] + f_sweep * A_chan[i] * dx[i]
        infl[i] = infl[i-1] + Q_base[i] * dt[i]
        pore[i] = pore[i-1] + pore_total * prel[i] * dx[i]
        imp[i] = imp[i-1] + impound * irel[i] * dx[i]
        W = melt[i] + chan[i] + infl[i] + pore[i] + imp[i] - lost[i-1]
        lost[i] = lost[i-1] + loss_per_km * W * (dx[i] / 1000.0)
    gross = melt + chan + infl + pore + imp
    W_active = gross - lost
    # attribute losses pro-rata so source shares stay meaningful
    keep = W_active / np.maximum(gross, 1.0)
    for arr in (melt, chan, infl, pore, imp):
        arr *= keep
    # pulse duration grows ~linearly with distance: ~45 min at the border ->
    # ~3.2 h at Devghat (FFD stage record: arrival 15:20, peak 16:00, back
    # near normal 18:30). The pulse is skewed - F_WIN of the active water
    # rides in the main window, the rest in the long tail.
    dur = np.maximum((45.0 + 0.85 * (x_km - 22.0)) * 60.0, 420.0)  # seconds
    F_WIN = 0.55
    Q_peak = 2.0 * F_WIN * W_active / dur + Q_base   # triangular-pulse peak
    return dict(name=name, melt=melt, chan=chan, infl=infl, pore=pore,
                imp=imp, lost=lost, W=W_active, gross=gross, dur=dur,
                Qp=Q_peak)

SCEN = [
    run("snowplow (best evidence)"),
    run("melt-only (no sweep-up)", f_sweep=0.0, pore_total=0.0,
        W_melt_total=5.3e6, loss_per_km=0.002),
    run("melt-maximal, weak sweep", W_melt_total=15e6, f_sweep=0.3,
        pore_total=4e6),
    run("snowplow + brief impoundment", impound=4e6),
]

# ------------------------------------------------------------------ report --
CHK = [("Border 22 km", 22.0), ("Syabrubesi", 37.6), ("Betrawati", 68.4),
       ("Galchhi", 107.6), ("Malekhu", 117.0), ("Devghat", 199.2)]
print("\nfront/peak arrival (model, minutes after 08:37):")
for nm, km in CHK:
    print(f"  {nm:14s} km {km:6.1f}  front {np.interp(km,x_km,t_front):5.0f}"
          f"  peak {np.interp(km,x_km,t_peak):5.0f}")

for s in SCEN:
    i_dev = int(np.argmin(np.abs(x_km - 199.2)))
    i_gal = int(np.argmin(np.abs(x_km - 107.6)))
    # "net new" water at a gauge over a day-scale window: melt + pore only.
    # (Impounded water is river baseflow delayed by minutes - gross surge,
    # but ~zero net over a day; swept/inflow water likewise redistributed.)
    new = s["melt"] + s["pore"]
    print(f"\n== {s['name']}")
    print(f"  at Devghat: active water {s['W'][i_dev]/1e6:6.1f} Mm3 "
          f"(melt {s['melt'][i_dev]/1e6:.1f}, swept channel {s['chan'][i_dev]/1e6:.1f}, "
          f"inflow {s['infl'][i_dev]/1e6:.1f}, pore {s['pore'][i_dev]/1e6:.1f}, "
          f"impound {s['imp'][i_dev]/1e6:.1f}, lost {s['lost'][i_dev]/1e6:.1f})")
    print(f"  gross surge {s['gross'][i_dev]/1e6:.1f} Mm3 | NET NEW "
          f"(melt+pore) {new[i_dev]/1e6:.1f} Mm3 | FFD 'excess' ~20 Mm3")
    print(f"  river-derived share of active wave at Galchhi: "
          f"{(s['chan'][i_gal]+s['infl'][i_gal])/max(s['W'][i_gal],1):.0%}, "
          f"at Devghat: {(s['chan'][i_dev]+s['infl'][i_dev])/max(s['W'][i_dev],1):.0%}")
    print(f"  peak Q at Devghat: {s['Qp'][i_dev]:,.0f} m3/s (obs 5,850), "
          f"pulse duration there {s['dur'][i_dev]/3600:.1f} h")

# ------------------------------------------------------------------- plots --
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
ax = axes[0, 0]
ax.plot(x_km, z_raw, lw=0.5, color="0.7", label="raw DEM samples")
ax.plot(x_km, z_s, lw=1.8, color="tab:blue", label="channel profile (smoothed)")
for nm, km in CHK:
    ax.axvline(km, color="0.85", zorder=0)
    ax.annotate(nm, (km, np.interp(km, x_km, z_s) + 150), rotation=90,
                fontsize=7, ha="right")
ax.set_xlabel("distance along channel from collapse scar (km)")
ax.set_ylabel("elevation (m)")
ax.set_title("River profile: Langtang Lirung scar → Devghat (OSM path + Mapzen/SRTM DEM)")
ax.legend(fontsize=8)

ax = axes[0, 1]
ax.plot(x_km, t_front, label=f"model front (U={A:.0f}·S^{B:.2f})", color="tab:red")
ax.plot(x_km, t_peak, label=f"model peak (c_p={C_P:.2f})", color="tab:orange")
for km, m, w in FRONT_OBS:
    ax.plot(km, m, "v", color="tab:red", ms=8 if w >= 2 else 5)
for km, m, w in PEAK_OBS:
    ax.plot(km, m, "^", color="tab:orange", ms=8 if w >= 2 else 5)
ax.set_xlabel("distance (km)"); ax.set_ylabel("minutes after 08:37 NPT")
ax.set_title("Arrival times: model vs observed (▼ front, ▲ peak)")
ax.legend(fontsize=8)

ax = axes[1, 0]
s = SCEN[0]
ax.stackplot(x_km, s["melt"] / 1e6, s["pore"] / 1e6, s["chan"] / 1e6,
             s["infl"] / 1e6,
             labels=["frictional ice melt", "sediment pore water",
                     "swept-up channel water", "baseflow inflow"],
             colors=["#9ecae1", "#a1d99b", "#3182bd", "#08519c"], alpha=0.9)
ax.axhline(20, color="k", ls="--", lw=1)
ax.text(4, 20.7, "FFD 'excess water' ≈ 20 Mm³", fontsize=8)
ax.set_xlabel("distance (km)"); ax.set_ylabel("cumulative water (Mm³)")
ax.set_title("Where the water comes from (snowplow scenario, cumulative)")
ax.legend(fontsize=8, loc="upper left")

ax = axes[1, 1]
ax.plot(x_km, U_front, color="tab:red", label="model front speed")
obs_v = [(11, 52, "avg 0–22 km (Kargel 193 km/h)"), (22, 48, "geopera at border 45–52"),
         (37.6, 11, "geopera Syabrubesi ~11"), (50, 21, "border→Betrawati celerity"),
         (90, 6, "Betrawati→Galchhi celerity"), (160, 7, "lower-reach celerity")]
for xx, vv, lab in obs_v:
    ax.plot(xx, vv, "o", color="k", ms=5)
    ax.annotate(lab, (xx, vv), textcoords="offset points", xytext=(5, 4),
                fontsize=7)
ax.set_xlabel("distance (km)"); ax.set_ylabel("speed (m/s)")
ax.set_title("Front speed vs observations")
ax.legend(fontsize=8)

fig.suptitle("Nepal 2026 flood — snowplow-integral model (Phase B v1)",
             fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "snowplow_v1.png"), dpi=130)

# individual panels for the web report
import matplotlib.transforms as mtransforms
for i, (r, c, name) in enumerate([(0, 0, "panel_profile"), (0, 1, "panel_timing"),
                                  (1, 0, "panel_sources"), (1, 1, "panel_speed")]):
    extent = axes[r, c].get_tightbbox(fig.canvas.get_renderer()).transformed(
        fig.dpi_scale_trans.inverted())
    fig.savefig(os.path.join(OUT, f"{name}.png"), dpi=140,
                bbox_inches=extent.expanded(1.03, 1.06))
print(f"\nplots -> output/snowplow_v1.png + 4 panels")
