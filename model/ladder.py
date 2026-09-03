#!/usr/bin/env python3
"""
Phase B2 "ladder network" — pulse structure of the 26 Aug 2026 Trishuli flood.

Dave's equivalent-circuit idea made literal. The governing physics is the
Saint-Venant shallow-water equations; dropping the inertia term gives the
DIFFUSIVE WAVE approximation, which is mathematically identical to a nonlinear
RC transmission line (telegrapher's equations without L — the same PDE as
charging a long cable):

    continuity:  dS_i/dt = Q_in,i - Q_out,i + q_lateral,i     (KCL at a node)
    "Ohm's law": Q_{i->i+1} = (1/n) A R^{2/3} sqrt(dEta/dx)   (nonlinear R)

  node storage S_i = w_i * dx * h_i        -> shunt capacitor C_i = w_i*dx
  water-surface head eta_i = z_i + h_i     -> node voltage
  side valley = reservoir behind a weir    -> RC branch that charges on the
                                              rising limb, discharges after
  debris dam  = crest that erodes when     -> breakdown element (SCR/spark
                overtopped                    gap); cascades make surge trains

v2 adds the INDUCTOR: simulate(inertial=True), the default, upgrades to the
local-inertia form of Saint-Venant (Bates et al. 2010) - discharge becomes a
state variable with dQ/dt = -g*A*d(eta)/dx - friction (semi-implicit), Froude-
capped in the supercritical gorge. inertial=False keeps the RC-only line.

v5 adds the REGIME DIAL: simulate(mu=...) puts a Coulomb basal-friction term
-mu*g*A*sign(Q) in the momentum equation, making the friction law Voellmy:
    S_f = mu + n^2 v^2 / R^(4/3)      (Coulomb + turbulent)
which collapses to Manning (this file's calibrated Trishuli behaviour) at
mu=0 and to a dense granular avalanche at mu ~ 0.1-0.2. Steady balance gives
v = sqrt((S - mu) * R^(4/3)) / n — the Voellmy terminal velocity with
xi = R^(1/3)/n^2, so Manning n IS the turbulent xi (n=0.05 at h=10 m is
xi ~ 860 m/s^2, mid-range of published debris-flow values). Numerically the
Coulomb term is applied as a post-update clamp that cannot reverse the flow
(static friction: the flow STOPS where surface slope < mu until mass piles
up behind it) — this is what gives stop-and-go granular fronts. mu=0.0 is
the default and leaves every published Trishuli result bit-identical; the
granular branch is exercised by the Chamoli hindcast
(hindcast/chamoli/run_voellmy.py).
Result: mid-reach peaks sharpen 14-17% and the out-of-sample Galchhi 30-min
rise improves 5.2 -> 5.9 m (6.7 at 1-km resolution), but the distal peak
barely moves - and width/resolution sensitivities show the remaining Devghat
gap is dominated by lower-reach storage geometry AND by what base flow the
Devghat gauge actually measures (likely Narayani incl. Kali Gandaki, ~2,900
m3/s - see PLAN.md).

Domain: border (path-km 22, where the event became a flood) -> Devghat
(km 199), 90 nodes, dx ~ 2 km, geometry from data/river_profile.csv.
Inflow: monsoon baseflow + the event pulse (volume/duration from Phase B
snowplow scenario). Runs: bare line / + side valleys (inertial + RC-only
comparison) / + hypothetical mid-route breach (no evidence of one; it
demonstrates the signature to look for in the Gandak record).
"""
import csv, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "output")
os.makedirs(OUT, exist_ok=True)

G = 9.81

# ------------------------------------------------------------- geometry -----
rows = list(csv.DictReader(open(os.path.join(DATA, "river_profile.csv"))))
xp = np.array([float(r["dist_km"]) for r in rows])
zp = np.minimum.accumulate(np.array([float(r["elev_m"]) for r in rows]))
k = 5
zp = np.convolve(np.pad(zp, k, mode="edge"),
                 np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]

X0, X1, N = 22.0, 199.2, 90
xn = np.linspace(X0, X1, N)                      # node centres, km
zn = np.interp(xn, xp, zp)                       # bed elevation, m
DX = (xn[1] - xn[0]) * 1000.0                    # m

# monsoon baseflow along the line (anchors as in snowplow.py)
# Budhi Gandaki joins ~km 160, Marsyangdi ~km 185: big monsoon tributaries
QB_X = np.array([22.0, 37.6, 68.4, 120.0, 159.0, 161.0, 184.0, 186.0, 199.2])
QB_Q = np.array([150.0, 250.0, 500.0, 650.0, 700.0, 1000.0, 1050.0, 1450.0, 1500.0])
Qb = np.interp(xn, QB_X, QB_Q)
q_lat = np.zeros(N)                              # lateral inflow per node
q_lat[1:] = np.diff(Qb)                          # distributed current sources

# channel width from downstream hydraulic geometry (fallback / weir widths)
wn = np.clip(4.8 * np.sqrt(Qb), 40.0, 160.0)
# Manning n: rough mountain torrent upstream, big monsoon river downstream
nn = np.interp(xn, [22, 70, 199], [0.055, 0.040, 0.025])

# ---- v4: NONLINEAR CROSS-SECTIONS from DEM transects (model/transects.py) --
# Stage-storage tables W(eta), A(eta) per node: capacitance is now piecewise-
# nonlinear - confined in gorges even at high stage, exploding at valley
# openings. Falls back to rectangular sections if transects.json is absent.
# Section mode: "rect" (calibrated default) or "dem" (transect experiment).
# The v4 DEM-section experiment over-damps: 30 m posting cannot resolve the
# inner slot canyon (model gorge stage 16 m vs geopera trimlines ~70 m), so
# real sections need the HMA 8 m DEM or footage-derived slot widths first.
SECTIONS = os.environ.get("LADDER_SECTIONS", "rect")
ETA = np.arange(0.0, 122.0, 2.0)
try:
    if SECTIONS != "dem":
        raise FileNotFoundError
    _tr = json.load(open(os.path.join(DATA, "transects.json")))
    _eta = np.array(_tr["eta"]); _W = np.array(_tr["width"]); _A = np.array(_tr["area"])
    _km = np.array(_tr["km"])
    assert len(_eta) == len(ETA) and abs(_eta[1] - _eta[1]) < 1e-9
    W_tab = np.empty((N, len(ETA))); A_tab = np.empty((N, len(ETA)))
    for m in range(len(ETA)):
        W_tab[:, m] = np.interp(xn, _km, _W[:, m])
        A_tab[:, m] = np.interp(xn, _km, _A[:, m])
    W_tab = np.maximum(W_tab, 20.0)
    A_tab = np.maximum.accumulate(np.maximum(A_tab, 0.0), axis=1)
    print("transect tables loaded: nonlinear C(eta) active")
except FileNotFoundError:
    W_tab = np.repeat(wn[:, None], len(ETA), axis=1)
    A_tab = W_tab * ETA[None, :]
    print(f"sections: rectangular (LADDER_SECTIONS={SECTIONS})")
Wf_tab = 0.5 * (W_tab[:-1] + W_tab[1:])
Af_tab = 0.5 * (A_tab[:-1] + A_tab[1:])
DETA = float(ETA[1] - ETA[0])

def lookup(tab, h):
    """vectorized table lookup: tab rows must match len(h)"""
    idx = np.clip(h / DETA, 0.0, len(ETA) - 2.001)
    i0 = idx.astype(int); f = idx - i0
    r = np.arange(len(h))
    return tab[r, i0] * (1.0 - f) + tab[r, i0 + 1] * f

# ------------------------------------------------------ side valleys --------
# (path-km, reservoir plan area m2, weir width m, sill height above bed m)
# Plan areas are order-of-magnitude reads of valley-floor storage near each
# confluence -- illustrative v0 values, to be mapped properly from Sentinel-2.
SIDE = [
    # The border T-junction: the debris flow came DOWN the Lhende and had to
    # turn ~90 deg into the main stem; the upstream Kyirong Tsangpo arm is a
    # large reservoir that connects the moment the surge arrives - Dave's
    # "piecewise step in capacitance". Modeled as a big low-sill branch at
    # the injection node.
    ("Kyirong upstream arm", 22.0, 1.5e6, 150.0, 1.0),
    ("Chilime Khola",   30.0, 4.0e5,  60.0, 3.0),
    ("Langtang Khola",  37.6, 6.0e5,  80.0, 3.0),
    ("Mailung Khola",   55.0, 3.0e5,  50.0, 4.0),
    ("Salankhu Khola",  66.0, 4.0e5,  60.0, 3.0),
    ("Tadi Khola",     120.0, 1.5e6, 100.0, 2.5),
    ("Mahesh Khola",   150.0, 1.2e6, 100.0, 2.5),
    ("Budhi Gandaki",  160.0, 2.5e6, 120.0, 2.0),
    ("Marsyangdi",     185.0, 2.5e6, 120.0, 2.0),
]
CD_WEIR = 1.6                                    # broad-crested weir coeff

# Junction minor losses (inertial solver): local head loss K*v^2/2g at
# interfaces just below major confluences - the momentum a flow loses when it
# must turn. K ~ 2-4 for a sharp T-junction impact, ~1-1.5 for oblique joins.
K_JUNC_KM = {22.0: 3.0, 37.6: 1.5, 160.0: 1.0, 185.0: 1.0}

# ---------------------------------------------------------- event pulse -----
# Injected at the border node: triangular pulse. Volume ~ what the snowplow
# model says the wave carried at km 22 plus what the upper reach kept feeding.
V_PULSE = 30e6                                   # m3
T_PULSE = 45 * 60.0                              # s
Q_PEAK_IN = 2 * V_PULSE / T_PULSE                # ~17,800 m3/s triangular peak
T_ARRIVE = 7 * 60.0                              # front hits border 08:44

def q_inflow(t):
    q = Qb[0]
    if T_ARRIVE < t < T_ARRIVE + T_PULSE:
        f = (t - T_ARRIVE) / T_PULSE
        tri = 1 - abs(2 * f - 1)
        q += Q_PEAK_IN * tri
    return q

# ------------------------------------------------------------- simulate -----
# inertial=True adds the "inductor": discharge becomes a STATE variable with
# dQ/dt = -g*A*d(eta)/dx - friction (local-inertia form of Saint-Venant,
# Bates et al. 2010, semi-implicit in friction). inertial=False is the old
# diffusive/RC-only line, kept for comparison. A Froude cap bounds the
# supercritical gorge reaches (the scheme drops convective acceleration).
FR_MAX = 2.0

def simulate(side_valleys=False, breach=False, inertial=True, mu=0.0,
             t_end=12 * 3600.0, dt=2.0):
    # normal-depth IC by inverting the section conveyance K(eta) at baseflow
    S0 = np.maximum(-np.gradient(zn, xn * 1000), 1e-4)
    R_ic = (A_tab / np.maximum(W_tab + 2 * ETA[None, :], 1.0)
            if SECTIONS == "dem" else np.repeat(ETA[None, :], N, axis=0))
    K = (A_tab / nn[:, None]) * np.maximum(R_ic, 1e-6) ** (2/3) \
        * np.sqrt(S0)[:, None]
    h = np.empty(N)
    for i in range(N):
        h[i] = np.interp(Qb[i], np.maximum.accumulate(K[i])
                         + np.arange(len(ETA)) * 1e-6, ETA)
    h = np.clip(h, 0.5, None)
    hmax = h.copy()
    Qi = 0.5 * (Qb[:-1] + Qb[1:])                # interface discharge state
    nf = 0.5 * (nn[:-1] + nn[1:])
    K_loc = np.zeros(N - 1)                      # junction minor-loss coeffs
    for km_j, K in K_JUNC_KM.items():
        K_loc[min(int(np.argmin(np.abs(xn - km_j))), N - 2)] = K
    hs = {nm: 0.0 for nm, *_ in SIDE}            # side reservoir stage (m)
    side_node = {nm: int(np.argmin(np.abs(xn - km)))
                 for nm, km, *_ in SIDE}
    # hypothetical breach: dam at km 55 impounding nothing initially; crest
    # erodes when overtopped -> stores the rising limb then lets go
    b_node = int(np.argmin(np.abs(xn - 55.0)))
    crest = 25.0 if breach else 0.0              # m above bed
    nt = int(t_end / dt)
    save_every = int(60 / dt)
    stations = {"Betrawati (km 68)": int(np.argmin(np.abs(xn - 68.4))),
                "Galchhi (km 108)": int(np.argmin(np.abs(xn - 107.6))),
                "Malekhu (km 117)": int(np.argmin(np.abs(xn - 117.0))),
                "Devghat (km 199)": N - 1}
    rec_t, rec_q, rec_hs = [], {s: [] for s in stations}, {nm: [] for nm, *_ in SIDE}
    rec_h = {}

    eta_dam_note = []
    for it in range(nt):
        t = it * dt
        eta = zn + h
        Sf = (eta[:-1] - eta[1:]) / DX               # driving surface slope
        if inertial:
            # local-inertia momentum update (semi-implicit friction) on the
            # REAL sections: A_f, W_f, R from the transect tables at the
            # interface flow depth.
            hfe = np.maximum(np.maximum(eta[:-1], eta[1:])
                             - np.maximum(zn[:-1], zn[1:]), 0.05)
            Af = np.maximum(lookup(Af_tab, hfe), 1.0)
            Wfe = np.maximum(lookup(Wf_tab, hfe), 20.0)
            # dem mode: proper hydraulic radius; rect mode: wide-channel R=h
            # (keeps the published v3 calibration exactly)
            R = Af / (Wfe + 2.0 * hfe) if SECTIONS == "dem" else hfe
            num = Qi + G * Af * dt * Sf
            den = (1.0 + G * dt * nf ** 2 * np.abs(Qi) / (Af * np.maximum(R, 0.05) ** (4/3))
                   + K_loc * dt * np.abs(Qi) / (2.0 * Af * DX))
            Qi = num / den
            if mu > 0.0:
                # Voellmy Coulomb term as a sign-preserving clamp: remove up
                # to mu*g*A*dt of momentum, never reverse the flow. Where the
                # driving slope < mu this stalls the front (static friction)
                # until upstream mass steepens the water surface past mu.
                Qi = np.sign(Qi) * np.maximum(np.abs(Qi) - mu * G * Af * dt,
                                              0.0)
            Qcap = FR_MAX * Af * np.sqrt(G * Af / Wfe)   # Froude bound
            Qi = np.clip(Qi, -Qcap, Qcap)
            Q = Qi
        else:
            # diffusive/RC-only: Q diagnostic from Manning on surface slope,
            # real sections
            hu = np.maximum(np.where(Sf >= 0, h[:-1], h[1:]), 0.05)
            A = np.maximum(lookup(Af_tab, hu), 1.0)
            Wu = np.maximum(lookup(Wf_tab, hu), 20.0)
            R = A / (Wu + 2.0 * hu) if SECTIONS == "dem" else hu
            Q = np.sign(Sf) * (A / nn[:-1]) * np.maximum(R, 0.05) ** (2/3) \
                * np.sqrt(np.abs(Sf) + 1e-8)
        if breach and crest > 0:
            # dam at b_node: flow over crest only (weir), crest erodes
            hov = max(eta[b_node] - (zn[b_node] + crest), 0.0)
            Qdam = CD_WEIR * wn[b_node] * hov ** 1.5
            if Sf[b_node] > 0:
                Q[b_node] = min(Q[b_node], Qdam)
                if inertial:
                    Qi[b_node] = Q[b_node]           # no momentum through dam
            if hov > 0:
                crest = max(crest - 4e-4 * hov * dt, 0.0)  # erosion law
                if crest == 0 and not eta_dam_note:
                    eta_dam_note.append(t)
        # node volume balance (KCL)
        dV = np.zeros(N)
        dV[0] += q_inflow(t) - Q[0]
        dV[1:-1] += Q[:-1][0:N-2] - Q[1:][0:N-2]
        dV[-1] += Q[-1]
        dV[1:] += q_lat[1:]
        # downstream boundary: normal-depth outflow at last node
        Sout = max(-np.gradient(zn, xn * 1000)[-1], 5e-4)
        Qout = (wn[-1] * h[-1] / nn[-1]) * h[-1] ** (2/3) * np.sqrt(Sout)
        dV[-1] -= Qout
        # side-valley RC branches
        if side_valleys:
            for nm, km, area, ww, sill in SIDE:
                i = side_node[nm]
                head_main = eta[i] - (zn[i] + sill)
                head_side = hs[nm]
                dh = head_main - head_side
                Qs = CD_WEIR * ww * np.sign(dh) * min(abs(dh), 8.0) ** 1.5
                Qs = np.clip(Qs, -hs[nm] * area / dt,
                             max(head_main, 0) * wn[i] * DX / dt)
                if head_main <= 0 and Qs > 0:
                    Qs = 0.0
                dV[i] -= Qs
                hs[nm] += Qs * dt / area
                hs[nm] = max(hs[nm], 0.0)
        Wn_now = np.maximum(lookup(W_tab, h), 20.0)  # stage-dependent width
        h += dV * dt / (Wn_now * DX)
        h = np.maximum(h, 0.05)
        np.maximum(hmax, h, out=hmax)
        if it % save_every == 0:
            rec_t.append(t / 3600.0)
            for s, i in stations.items():
                rec_h.setdefault(s, []).append(h[i])
                # discharge passing the station = inter-node flow just below
                rec_q[s].append(Q[min(i, N - 2)])
            for nm, *_ in SIDE:
                rec_hs[nm].append(hs[nm])
    if breach and eta_dam_note:
        print(f"   (hypothetical dam at km 55 fully breached at "
              f"t={eta_dam_note[0]/3600:.1f} h)")
    simulate.last_h = {s: np.array(v) for s, v in rec_h.items()}
    simulate.last_hmax = hmax
    return (np.array(rec_t), {s: np.array(v) for s, v in rec_q.items()},
            {nm: np.array(v) for nm, v in rec_hs.items()})

print("run 1: bare line (no side valleys), inertial")
t1, q1, _ = simulate(side_valleys=False)
print("run 2: + side-valley branches, inertial")
t2, q2, hs2 = simulate(side_valleys=True)
h2 = simulate.last_h
hmax2 = simulate.last_hmax
# NEW VALIDATION AXIS: with real sections the model predicts STAGE, comparable
# to geopera's trimline mapping (40-134 m at the border crossing, ~70 m median
# through the confined gorge reaches).
gorge = (xn >= 22) & (xn <= 40)
print(f"max stage, gorge km 22-40: median {np.median(hmax2[gorge]):.0f} m, "
      f"max {hmax2[gorge].max():.0f} m  (geopera trimlines: median ~70, range 40-134)")
i_g = int(np.argmin(np.abs(xn - 107.6)))
print(f"max stage at Galchhi node: {hmax2[i_g]:.1f} m (gauge rose ~9 m in 30 min)")
print("run 2d: side valleys, RC-only (inertia OFF) for comparison")
t2d, q2d, _ = simulate(side_valleys=True, inertial=False)
# Out-of-sample check: Galchhi gauge observed ~9 m rise in ~30 min. This
# datum was never used to calibrate anything - pure test.
hg = h2["Galchhi (km 108)"]
rise30 = max(hg[i + 30] - hg[i] for i in range(len(hg) - 30))
print(f"\nOUT-OF-SAMPLE TEST - Galchhi max 30-min stage rise: "
      f"{rise30:.1f} m (observed ~9 m); total stage excursion "
      f"{hg.max() - hg[0]:.1f} m")
print("run 3: + hypothetical mid-route breach (demonstration only)")
t3, q3, _ = simulate(side_valleys=True, breach=True)

def clock(th):   # hours after 08:37 -> NPT string
    m = int(round(th * 60)) + 8 * 60 + 37
    return f"{m // 60:02d}:{m % 60:02d}"

print("\nstation summaries — inertial (RLC) vs RC-only (run 2 config):")
for s in q2:
    qq, qd = q2[s], q2d[s]
    m1 = np.where(t2 >= 1.0, qq, -1)   # mask the initial settling transient
    m2 = np.where(t2d >= 1.0, qd, -1)
    i, j = int(np.argmax(m1)), int(np.argmax(m2))
    print(f"  {s:18s} RLC peak {qq[i]:7,.0f} m3/s at {clock(t2[i])}  |"
          f"  RC-only {qd[j]:7,.0f} at {clock(t2d[j])}"
          f"  (obs Devghat 5,850 @ 16:00)")

for nm, *_ in SIDE:
    print(f"  side valley {nm:15s} max charge {hs2[nm].max():5.1f} m")

# ---------------------------------------------------------------- plots -----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(11, 12), sharex=True)
cols = {"Betrawati (km 68)": "#7fb3cf", "Galchhi (km 108)": "#4a8ab5",
        "Malekhu (km 117)": "#2b6b9c", "Devghat (km 199)": "#164a70"}

ax = axes[0]
for s in q1:
    ax.plot(t1, q1[s], color=cols[s], label=s)
ax.plot(7.38, 5850, "k*", ms=13, label="observed: Devghat 5,850 @ 16:00")
ax.set_title("Run 1 — bare transmission line: pulse attenuates and broadens, nothing re-shapes it")
ax.set_ylabel("discharge (m³/s)"); ax.legend(fontsize=8)

ax = axes[1]
for s in q2:
    ax.plot(t2, q2[s], color=cols[s], label=s)
ax.plot(7.38, 5850, "k*", ms=13)
ax.set_title("Run 2 — side-valley RC branches: capacitors charge on the rising limb (clipping the peak), discharge into the tail")
ax.set_ylabel("discharge (m³/s)"); ax.legend(fontsize=8)

ax = axes[2]
for s in q3:
    ax.plot(t3, q3[s], color=cols[s], label=s)
ax.plot(7.38, 5850, "k*", ms=13)
ax.set_title("Run 3 — + HYPOTHETICAL mid-route dam breach at km 55: the breakdown element re-sharpens the pulse (signature to seek in Gandak records)")
ax.set_ylabel("discharge (m³/s)"); ax.set_xlabel("hours after 08:37 NPT")
ax.legend(fontsize=8)
for a in axes:
    a.grid(alpha=.25)
fig.suptitle("Ladder-network routing (diffusive Saint-Venant = nonlinear RC line), border → Devghat", y=0.995)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ladder_v0.png"), dpi=130)

fig2, ax = plt.subplots(figsize=(11, 4.5))
for nm, *_ in SIDE:
    ax.plot(t2, hs2[nm], label=nm)
ax.set_xlabel("hours after 08:37 NPT"); ax.set_ylabel("side-valley stage above sill (m)")
ax.set_title("The capacitors: side-valley charge/discharge (run 2)")
ax.legend(fontsize=8, ncol=2); ax.grid(alpha=.25)
fig2.tight_layout()
fig2.savefig(os.path.join(OUT, "ladder_sidevalleys.png"), dpi=130)
print("\nplots -> output/ladder_v0.png, output/ladder_sidevalleys.png")
