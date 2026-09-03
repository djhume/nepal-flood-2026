#!/usr/bin/env python3
"""
Phase B3 — the UNIFIED scar-to-Devghat model with the dilution dial.

One momentum equation for the whole event, replacing the two-model split
(fitted kinematic snowplow law for km 0-22 + ladder from the border down).
The physics is the Chamoli-tested Voellmy-Saint-Venant hybrid (local-inertia
SV + semi-implicit Manning + sign-preserving Coulomb clamp), with the regime
dial now defined ONCE for both events in terms of the water volume fraction
w of the moving mass (a scalar advected and volumetrically mixed with the
flow):

    w <= W_SAT:  mu = mu_dry + (mu_wet - mu_dry) * (w / W_SAT)
    w >  W_SAT:  mu = mu_wet * (1 - w) / (1 - W_SAT)     -> 0 at pure water

W_SAT ~ 0.25 is pore saturation of a granular matrix; above it the mass is a
slurry whose residual Coulomb strength dies away with solid content — pure
water has no yield stress, so the monsoon river ahead of the front (w = 1)
is EXACTLY the calibrated mu=0 Manning ladder. (The first branch is the
Chamoli dial verbatim: melt never pushed w past ~0.25 there, so the Chamoli
result is untouched by the second branch.) At Chamoli the water arrived by
frictional MELT of the ~20% ice; on the Trishuli it arrives by ENTRAINMENT
of the river the wave runs over — same dial, different tap.

STRANDING (in the Phase B design from the start: "deposition ... stranding"):
where the flow is slow (u < U_DEP) and still granular (w < W_SAT), solids
transfer to the bed on a timescale T_DEP — the debris body strands and the
water continues past it, rather than a 1D solid wall damming the river.
This yields an emergent, independently checkable number: the stranded volume
vs geopera's WorldView-3 stereo DEM (1 Sept): 0.9 Mm3 measured deposition
against 3.2 Mm3 of EROSION in the ~45% of the corridor their stereo pair
covers, with their calibrated model putting total deposition near 5 Mm3.
NOTE: their earlier "12 Mm3 wedge" (28 Aug, parallax) was RETRACTED on
1 Sept as noise - do not score against it (see research/imagery-composition
-memo.md). The corridor was net EROSIONAL by ~3.5x; this model has no
erosion term, so its stranded volume is an upper bound on net deposition.

A-priori parameters (nothing fitted to the Trishuli clocks in this run):
  mu_dry = Scheidegger (1973) H/L at the release volume (same rule as
           Chamoli: 0.34 at 5 Mm3, 0.33 at 10, 0.29 at 30)
  mu_wet = 0.02, W_SAT = 0.25 (shared dial), U_DEP = 1 m/s, T_DEP = 120 s
  n      = 0.06 upper torrent -> 0.025 lower river; widths: 50 m gorge,
           documented Syabrubesi opening (~km 36-41) 200 m, hydraulic
           geometry 4.8*sqrt(Qb) below; baseflow anchors as ladder.py
  release: V_REL over km 0-1.2, initial liquid fraction W0 (unmelted ice
           counts as solid; melt is second-order here per our own budget)

Scored OUT OF SAMPLE against the Section-3 table (border 08:44, geopera
border speeds, Syabrubesi collapse ~11 m/s, Betrawati/Galchhi/Malekhu
clocks, Devghat peak) plus the provenance split at Devghat (three tracers:
total depth h, water hw, release-origin water hwr, release solids hr) —
the H1 payload from dynamics rather than bookkeeping.

Outputs: scorecard to stdout, output/unified_v1.png.
"""
import copy, csv, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "output")
os.makedirs(OUT, exist_ok=True)
G = 9.81

# ------------------------------------------------------------- geometry -----
rows = list(csv.DictReader(open(os.path.join(DATA, "river_profile.csv"))))
x_km = np.array([float(r["dist_km"]) for r in rows])
zp = np.minimum.accumulate(np.array([float(r["elev_m"]) for r in rows]))
k = 5
z = np.convolve(np.pad(zp, k, mode="edge"),
                np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
N = len(x_km)
DX = float(np.mean(np.diff(x_km))) * 1000.0          # 400 m

QB_X = np.array([0.0, 10.0, 22.0, 37.6, 68.4, 120.0, 159.0, 161.0,
                 184.0, 186.0, 199.2])
QB_Q = np.array([40.0, 60.0, 150.0, 250.0, 500.0, 650.0, 700.0, 1000.0,
                 1050.0, 1450.0, 1500.0])
Qb = np.interp(x_km, QB_X, QB_Q)
q_lat = np.zeros(N)
q_lat[1:] = np.diff(Qb)                              # m3/s per node

w_hydr = np.clip(4.8 * np.sqrt(Qb), 40.0, 160.0)
wn = np.where(x_km < 34.0, 50.0,
      np.where(x_km < 41.5, np.interp(x_km, [34.0, 36.0, 41.0, 41.5],
                                      [50.0, 200.0, 200.0, 60.0]),
       np.where(x_km < 60.0, 60.0, w_hydr)))
nn = np.interp(x_km, [0, 22, 70, 199], [0.060, 0.055, 0.040, 0.025])

# --------------------------------------------------- shared dial constants --
MU_WET, W_SAT = 0.02, 0.25
U_DEP, T_DEP = 1.0, 120.0        # stranding: slow + granular -> to the bed
TAU_Y0, RHO_MIX = 400.0, 1800.0  # Bingham yield stress at saturation (Pa),
                                 # mixture density. Above W_SAT the mass is a
                                 # slurry: yield resistance is a fixed STRESS,
                                 # so its equivalent friction tau_y/(rho g h)
                                 # DECREASES with depth - deep hyperconcen-
                                 # trated waves run on gentle slopes (Pierson
                                 # & Scott lahars) while thin sheets lock.
                                 # A Coulomb coefficient here (the earlier
                                 # form) wrongly parks deep waves on the
                                 # lower river. Chamoli untouched: melt never
                                 # pushed w past W_SAT there.

def mu_dry_scheidegger(V_m3):
    return 10 ** (0.62419 - 0.15666 * math.log10(V_m3))

def mu_of_w(w, h, mu_dry, mu_wet=MU_WET, w_sat=W_SAT):
    lo = mu_dry + (mu_wet - mu_dry) * np.clip(w / w_sat, 0.0, 1.0)
    tau_y = TAU_Y0 * np.clip((1.0 - w) / (1.0 - w_sat), 0.0, 1.0)
    hi = np.minimum(tau_y / (RHO_MIX * G * np.maximum(h, 0.05)), mu_wet)
    return np.where(w <= w_sat, lo, hi)

# ---------------------------------------------------------------- release ---
V_REL = 10e6            # nominal initial detachment (early-Sept: 1-10 Mm3)
W0 = 0.10               # initial liquid fraction of the release
X_REL = 1.2             # fed into km 0-1.2 (3 nodes)
T_REL = 180.0           # release feeds the channel over ~3 min (seismic
                        # duration scale) as a triangular inflow — an
                        # instantaneous 100-m slab is neither physical nor
                        # numerically meaningful in 1D
# Composition scenario for mu_dry: Scheidegger's regression is for ROCK
# avalanches; Langtang was a glacier-face collapse, and ice-rich avalanches
# run at mu ~ 0.12-0.2 (Schneider et al. 2010 ice-avalanche calibrations).
MU_DRY_ICE = 0.17

# ------------------------------------------- side valleys & junctions -------
SIDE = [                # verbatim from ladder.py
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
CD_WEIR = 1.6
H_SIDE_MAX = 8.0   # m — cap on side-branch fill depth: the v0 constant-plan-
                   # area reservoirs otherwise swallow unbounded volume under
                   # a deep bore (plan area x any head). 8 m over the mapped
                   # plan areas bounds each branch at a few Mm3, the scale the
                   # ladder's calibrated runs actually exercised. Proper
                   # stage-volume curves await Sentinel-2 mapping.
K_JUNC_KM = {22.0: 3.0, 37.6: 1.5, 160.0: 1.0, 185.0: 1.0}

# ------------------------------------------------------- observations -------
FRONT_OBS = [(22.0, 7, "border CCTV 08:44"), (37.6, 13, "Syabrubesi 08:50"),
             (68.4, 43, "Betrawati rising 09:20"),
             (107.6, 150, "Galchhi ~11:00"), (117.0, 163, "Malekhu 11:20"),
             (199.2, 403, "Devghat front 15:20")]
SPEED_OBS = [(30.0, 48.5, "geopera border reach 45-52"),
             (40.0, 11.0, "Syabrubesi opening ~11")]

FR_MAX = 2.0

# ------------------------------------------------------------ dynamics ------
K_loc = np.zeros(N - 1)
for km_j, K in K_JUNC_KM.items():
    K_loc[min(int(np.argmin(np.abs(x_km - km_j))), N - 2)] = K
nf = 0.5 * (nn[:-1] + nn[1:])
wf = 0.5 * (wn[:-1] + wn[1:])
side_node = {nm: int(np.argmin(np.abs(x_km - km))) for nm, km, *_ in SIDE}

def step(st, dt, mu_dry, w_sat, mu_wet, side_valleys=True, deposit=True,
         u_dep=U_DEP, t_dep=T_DEP):
    """One explicit step of the unified model on state dict st."""
    h, hw, hwr, hr, Qi, hs, bed = (st["h"], st["hw"], st["hwr"], st["hr"],
                                   st["Qi"], st["hs"], st["bed"])
    eta = z + h
    Sf = (eta[:-1] - eta[1:]) / DX
    hfe = np.maximum(np.maximum(eta[:-1], eta[1:])
                     - np.maximum(z[:-1], z[1:]), 0.05)
    Af = np.maximum(wf * hfe, 1e-6)
    up = Qi >= 0
    hu = np.where(up, h[:-1], h[1:])
    w_face = np.where(up, hw[:-1], hw[1:]) / np.maximum(hu, 1e-6)
    wr_face = np.where(up, hwr[:-1], hwr[1:]) / np.maximum(hu, 1e-6)
    r_face = np.where(up, hr[:-1], hr[1:]) / np.maximum(hu, 1e-6)
    mu_i = mu_of_w(np.clip(w_face, 0, 1), hfe, mu_dry, mu_wet, w_sat)
    # v2: CONVECTIVE momentum d(uQ)/dx, first-order upwind. The pure
    # local-inertia form (Bates et al. 2010) drops this term; that omission
    # is what let a supercritical dam-break front confine into a one-cell
    # soliton and a Coulomb-parked wall release as a coherent wall — the
    # rarefaction that spreads a real dam-break lives in this term.
    uQ = Qi * Qi / Af
    conv = np.zeros(N - 1)
    conv[1:] = np.where(Qi[1:] >= 0, (uQ[1:] - uQ[:-1]) / DX, 0.0)
    conv[:-1] += np.where(Qi[:-1] < 0, (uQ[1:] - uQ[:-1]) / DX, 0.0)
    num = Qi + dt * (G * Af * Sf - conv)
    den = (1.0 + G * dt * nf ** 2 * np.abs(Qi) / (Af * hfe ** (4 / 3))
           + K_loc * dt * np.abs(Qi) / (2.0 * Af * DX))
    Qi = num / den
    Qi = np.sign(Qi) * np.maximum(np.abs(Qi) - mu_i * G * Af * dt, 0.0)
    Qcap = FR_MAX * Af * np.sqrt(G * hfe)
    Qi = np.clip(Qi, -Qcap, Qcap)
    # targeted shock viscosity: the local-inertia scheme drops convective
    # momentum, so a supercritical dam-break front confines into a one-cell
    # numerical soliton that never attenuates. Where Fr > 0.8, blend Q
    # toward its neighbours (Lax-type dissipation) so the rarefaction can
    # stretch the wave; subcritical reaches are untouched (ladder-identical).
    # von Neumann-Richtmyer shock viscosity: the local-inertia scheme drops
    # convective momentum, so a supercritical dam-break front can confine
    # into a one-cell numerical soliton. Discriminate by SHARPNESS (second
    # difference of Q), not Froude - smooth waves at any Fr are untouched,
    # single-cell spikes are dissipated on the cell-crossing (CFL) timescale.
    cfl = (np.abs(Qi) / Af + np.sqrt(G * hfe)) * dt / DX
    curv = np.zeros(N - 1)
    curv[1:-1] = np.abs(Qi[:-2] - 2 * Qi[1:-1] + Qi[2:]) \
        / (np.abs(Qi[1:-1]) + 200.0)
    beta = np.clip(curv, 0.0, 1.0) * np.clip(cfl, 0.0, 0.5)
    if beta.any():
        Qn = Qi.copy()
        Qn[1:-1] = 0.5 * (Qi[:-2] + Qi[2:])
        Qi = (1.0 - beta) * Qi + beta * Qn
    Qi = np.where(Qi > 0, np.minimum(Qi, 0.9 * h[:-1] * wn[:-1] * DX / dt),
                  np.maximum(Qi, -0.9 * h[1:] * wn[1:] * DX / dt))
    Fw, Fwr, Fr = Qi * w_face, Qi * wr_face, Qi * r_face
    dV = np.zeros(N); dW = np.zeros(N); dWr = np.zeros(N); dR = np.zeros(N)
    dV[:-1] -= Qi; dV[1:] += Qi
    dW[:-1] -= Fw; dW[1:] += Fw
    dWr[:-1] -= Fwr; dWr[1:] += Fwr
    dR[:-1] -= Fr; dR[1:] += Fr
    dV[0] += Qb[0]; dW[0] += Qb[0]
    dV[1:] += q_lat[1:]; dW[1:] += q_lat[1:]
    S_end = max((z[-2] - z[-1]) / DX, 5e-4)
    Q_end = (wn[-1] * h[-1] / nn[-1]) * h[-1] ** (2 / 3) * math.sqrt(S_end)
    dV[-1] -= Q_end
    dW[-1] -= Q_end * hw[-1] / max(h[-1], 1e-6)
    dWr[-1] -= Q_end * hwr[-1] / max(h[-1], 1e-6)
    dR[-1] -= Q_end * hr[-1] / max(h[-1], 1e-6)
    if side_valleys:
        for nm, km, area, ww, sill in SIDE:
            i = side_node[nm]
            head_main = eta[i] - (z[i] + sill)
            dh = min(head_main, H_SIDE_MAX) - hs[nm]
            Qs = CD_WEIR * ww * np.sign(dh) * min(abs(dh), 8.0) ** 1.5
            Qs = np.clip(Qs, -hs[nm] * area / dt,
                         max(head_main, 0) * wn[i] * DX / dt)
            if (head_main <= 0 or hs[nm] >= H_SIDE_MAX) and Qs > 0:
                Qs = 0.0
            fw = hw[i] / max(h[i], 1e-6)
            fwr = hwr[i] / max(h[i], 1e-6)
            fr = hr[i] / max(h[i], 1e-6)
            dV[i] -= Qs; dW[i] -= Qs * fw
            dWr[i] -= Qs * fwr; dR[i] -= Qs * fr
            hs[nm] = max(hs[nm] + Qs * dt / area, 0.0)
    h += dV * dt / (wn * DX)
    hw += dW * dt / (wn * DX)
    hwr += dWr * dt / (wn * DX)
    hr += dR * dt / (wn * DX)
    h = np.maximum(h, 0.05)
    hw = np.clip(hw, 0.0, h)
    hwr = np.clip(hwr, 0.0, hw)
    hr = np.clip(hr, 0.0, h)
    if deposit:
        # stranding: slow + granular -> solids to bed, water passes
        u_node = np.zeros(N)
        u_node[:-1] = np.abs(Qi) / Af
        u_node[1:] = np.maximum(u_node[1:], np.abs(Qi) / Af)
        h_sol = np.maximum(h - hw, 0.0)
        wfrac = hw / np.maximum(h, 1e-6)
        strand = (u_node < u_dep) & (wfrac < w_sat) & (h_sol > 0.02)
        dep = np.where(strand, h_sol * dt / t_dep, 0.0)
        h -= dep
        hr = np.clip(hr - dep, 0.0, None)
        bed += dep * wn * DX                     # m3 stored on the bed
        h = np.maximum(h, 0.05)
    st.update(h=h, hw=hw, hwr=hwr, hr=hr, Qi=Qi, hs=hs, bed=bed)
    st["umax"] = np.maximum(st["umax"], np.abs(Qi) / Af)
    return st

_settled = {}
def settled_state(dt=0.5, hours=2.0, side_valleys=True):
    """River-only settling from analytic normal depth (cached)."""
    key = (dt, hours, side_valleys)
    if key in _settled:
        return copy.deepcopy(_settled[key])
    S0 = np.maximum(-np.gradient(z, x_km * 1000), 1e-4)
    h = np.maximum((Qb * nn / (wn * np.sqrt(S0))) ** 0.6, 0.05)
    st = dict(h=h, hw=h.copy(), hwr=np.zeros(N), hr=np.zeros(N),
              Qi=0.5 * (Qb[:-1] + Qb[1:]),
              hs={nm: 0.0 for nm, *_ in SIDE}, bed=np.zeros(N),
              umax=np.zeros(N - 1))
    h_chk = st["h"].copy()
    for it in range(int(hours * 3600 / dt)):
        # settle with the PURE-RIVER dial (w=1 -> mu=0) and no stranding
        st = step(st, dt, mu_dry=0.3, w_sat=W_SAT, mu_wet=MU_WET,
                  side_valleys=side_valleys, deposit=False)
        if it == int((hours - 0.25) * 3600 / dt):
            h_chk = st["h"].copy()
    drift = np.abs(st["h"] - h_chk).max()
    print(f"  (settle {hours:.0f} h: residual 15-min drift {drift:.3f} m)")
    st["umax"] = np.zeros(N - 1)
    _settled[key] = copy.deepcopy(st)
    return st

def simulate(V_rel=V_REL, w0=W0, w_sat=W_SAT, mu_wet=MU_WET, mu_dry=None,
             u_dep=U_DEP, t_dep=T_DEP, T_rel=T_REL, side_valleys=True,
             dt=0.5, t_end=10.0 * 3600.0):
    if mu_dry is None:
        mu_dry = mu_dry_scheidegger(V_rel)
    st = settled_state(dt=dt, side_valleys=side_valleys)
    h0 = st["h"].copy()
    rel = x_km <= X_REL
    wsum = wn[rel].sum() * DX
    stations = {"Betrawati": 68.4, "Galchhi": 107.6, "Malekhu": 117.0,
                "Devghat": 199.2}
    st_j = {s: int(np.argmin(np.abs(x_km - km))) for s, km in stations.items()}
    watch = sorted(set([km for km, *_ in SPEED_OBS] + [22.0]))
    watch_j = {km: min(int(np.argmin(np.abs(x_km - km))), N - 2)
               for km in watch}
    rec = {"t": [], "front": [], "w_front": [], "mu_front": []}
    for s in stations:
        rec[s] = {"q": [], "h": [], "r": [], "w": [], "wr": []}
    for km in watch:
        rec[f"v@{km}"] = []
    save = int(10.0 / dt)
    for it in range(int(t_end / dt)):
        t = it * dt
        if t < T_rel:                    # triangular release inflow
            qr = 2.0 * V_rel / T_rel * (1.0 - abs(2.0 * t / T_rel - 1.0))
            dh = qr * dt / wsum
            st["h"][rel] += dh
            st["hw"][rel] += dh * w0
            st["hwr"][rel] += dh * w0
            st["hr"][rel] += dh * (1 - w0)
        st = step(st, dt, mu_dry, w_sat, mu_wet, side_valleys,
                  deposit=True, u_dep=u_dep, t_dep=t_dep)
        if it % save == 0:
            h, hw, hwr, hr, Qi = (st["h"], st["hw"], st["hwr"], st["hr"],
                                  st["Qi"])
            rec["t"].append(it * dt / 60.0)
            risen = x_km[h - h0 > 0.5]
            fk = risen.max() if len(risen) else 0.0
            rec["front"].append(fk)
            j = min(int(np.argmin(np.abs(x_km - fk))), N - 2) if fk else 0
            wj = hw[j] / max(h[j], 1e-6)
            rec["w_front"].append(wj)
            rec["mu_front"].append(float(mu_of_w(np.array([wj]),
                                                 np.array([h[j]]), mu_dry,
                                                 mu_wet, w_sat)[0]))
            for s, j2 in st_j.items():
                jj = min(j2, N - 2)
                rec[s]["q"].append(Qi[jj])
                rec[s]["h"].append(h[j2])
                rec[s]["r"].append(hr[j2] / max(h[j2], 1e-6))
                rec[s]["w"].append(hw[j2] / max(h[j2], 1e-6))
                rec[s]["wr"].append(hwr[j2] / max(h[j2], 1e-6))
            eta = z + h
            hfe_s = np.maximum(np.maximum(eta[:-1], eta[1:])
                               - np.maximum(z[:-1], z[1:]), 0.05)
            for km, jj in watch_j.items():
                rec[f"v@{km}"].append(abs(Qi[jj]) / max(wf[jj] * hfe_s[jj],
                                                        1e-6))
    out = {k2: (np.array(v) if not isinstance(v, dict) else
                {kk: np.array(vv) for kk, vv in v.items()})
           for k2, v in rec.items()}
    front = np.maximum.accumulate(out["front"])
    t_arr = out["t"]
    def arrival(km):
        # first crossing, not np.interp: once the front saturates at the last
        # node the front array has a long flat tail, and np.interp on repeated
        # x-values returns a point inside the plateau (it reported Seti's
        # Pokhara arrival as 180 min instead of ~100). Interpolate linearly
        # between the two samples that straddle the crossing.
        idx = np.nonzero(front >= km)[0]
        if len(idx) == 0:
            return float("inf")
        i = int(idx[0])
        if i == 0:
            return float(t_arr[0])
        f0, f1 = front[i - 1], front[i]
        if f1 <= f0:
            return float(t_arr[i])
        return float(t_arr[i - 1] + (km - f0) / (f1 - f0)
                     * (t_arr[i] - t_arr[i - 1]))
    out.update(arrival=arrival, front=front, umax=st["umax"],
               bed=st["bed"], mu_dry=mu_dry, h0=h0)
    return out

def clock(minutes):
    if not np.isfinite(minutes):
        return "--:--"
    m = int(round(minutes)) + 8 * 60 + 37
    return f"{m//60:02d}:{m%60:02d}"

# ----------------------------------------------------------------- runs -----
# Phase C flavour: the release volume, composition and wetness are the
# CONTESTED inputs (source 10-200 Mm3, ice fraction unpublished). Run the
# competing release scenarios through the one model and let the Section-3
# table discriminate. mu_dry per composition: Scheidegger (rock) vs
# Schneider ice-avalanche band (ice-rich).
SCENARIOS = [
    ("A rock, early-estimate V=10", dict(V_rel=10e6, w0=0.10)),
    ("B ice-rich V=10", dict(V_rel=10e6, w0=0.15, mu_dry=MU_DRY_ICE)),
    ("C ice-rich V=30", dict(V_rel=30e6, w0=0.15, mu_dry=MU_DRY_ICE)),
    ("D rock V=30", dict(V_rel=30e6, w0=0.10)),
    # E: the wet endmember — an ice/snow/water slurry (or rock mass arriving
    # WITH the burst Lhende impoundment, ICIMOD's H3 story): 40% liquid.
    ("E wet slurry V=30 w0=0.4", dict(V_rel=30e6, w0=0.40, mu_dry=MU_DRY_ICE)),
    ("F wet slurry V=60 w0=0.4", dict(V_rel=60e6, w0=0.40, mu_dry=MU_DRY_ICE)),
]

def score_line(name, r, kw):
    ta_b = r["arrival"](22.0)
    ta_sy = r["arrival"](37.6)
    ta_be = r["arrival"](68.4)
    q = r["Devghat"]["q"]; tt = r["t"]
    mm = tt > 30
    i = int(np.argmax(np.where(mm, q, -1)))
    qg = r["Galchhi"]["h"]
    rise30 = max(qg[j + 180] - qg[j] for j in range(len(qg) - 180))
    bed_t = r["bed"].sum() / 1e6
    print(f"  {name:28s} border {clock(ta_b)} | Syabru {clock(ta_sy)} | "
          f"Betrawati {clock(ta_be)} | Galchhi rise {rise30:4.1f} m | "
          f"Devghat {q[i]:6,.0f} @ {clock(tt[i])} | stranded {bed_t:4.1f} Mm3")
    return r

print("\nobserved:                        border 08:44 | Syabru 08:50 | "
      "Betrawati 09:20 |Galchhi rise ~9 m | Devghat  5,850 @ 16:00 | "
      "geopera stereo: 0.9 measured / ~5 modeled, NET EROSIONAL")
results = {}
for name, kw in SCENARIOS:
    results[name] = score_line(name, simulate(**kw), kw)
nom = results["C ice-rich V=30"]

print("\n=========== detail - scenario C (ice-rich V=30) ==========")
print("front arrivals:")
for km, obs_min, label in FRONT_OBS:
    ta = nom["arrival"](km)
    if np.isfinite(ta):
        print(f"  km {km:6.1f}  model {ta:6.1f} min ({clock(ta)})   obs "
              f"~{obs_min} ({label})   {(ta-obs_min)/obs_min*100:+.0f}%")
    else:
        print(f"  km {km:6.1f}  model  never              obs ~{obs_min} "
              f"({label})")
print("speeds:")
for km, obs, label in SPEED_OBS:
    v = nom[f"v@{km}"]
    ta = nom["arrival"](km)
    m = (nom["t"] >= ta - 1) & (nom["t"] <= ta + 10)
    vp = v[m].max() if m.any() else 0.0
    print(f"  km {km:5.1f}  model peak Q/A {vp:5.1f} m/s   obs {obs} ({label})")
ta22 = nom["arrival"](22.0)
if np.isfinite(ta22):
    print(f"  scar->border mean front speed {22e3/(ta22*60):.0f} m/s "
          f"(obs ~53 from the 7-min clock)")
bed = nom["bed"]
print(f"stranded: total {bed.sum()/1e6:.1f} Mm3 (km 0-68: "
      f"{bed[x_km <= 68].sum()/1e6:.1f}) vs geopera stereo 0.9 Mm3 measured "
      f"deposition / ~5 Mm3 calibrated model (12 Mm3 claim retracted 1 Sept)")
tt = nom["t"]; qd = nom["Devghat"]["q"]
rd, wd, wrd = nom["Devghat"]["r"], nom["Devghat"]["w"], nom["Devghat"]["wr"]
m = (tt > 60) & (qd > 1600)
if m.any():
    v_tot = np.trapezoid(qd[m], tt[m] * 60)
    f_sol = np.trapezoid(qd[m] * rd[m], tt[m] * 60) / v_tot
    f_wrel = np.trapezoid(qd[m] * wrd[m], tt[m] * 60) / v_tot
    f_wriv = np.trapezoid(qd[m] * (wd[m] - wrd[m]), tt[m] * 60) / v_tot
    print(f"provenance at Devghat (Q>1,600): river water {100*f_wriv:.0f}%, "
          f"release water {100*f_wrel:.1f}%, release solids {100*f_sol:.0f}%"
          f"  (snowplow bookkeeping: ~74% river)")

print("\ndial/stranding sensitivities on scenario C:")
for nm2, kw in [("W_SAT=0.15", dict(w_sat=0.15)), ("W_SAT=0.35", dict(w_sat=0.35)),
                ("w0=0.10", dict(w0=0.10)), ("w0=0.20", dict(w0=0.20)),
                ("u_dep=2", dict(u_dep=2.0)), ("t_dep=300", dict(t_dep=300.0))]:
    # (TAU_Y0 sensitivity would need a module constant override; noted in
    # PLAN as future work with proper rheology sweep)
    base = dict(V_rel=30e6, w0=0.15, mu_dry=MU_DRY_ICE)
    base.update(kw)
    score_line(nm2, simulate(**base), base)

# ---------------------------------------------------------------- plots -----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))

ax = axes[0, 0]
ax.plot(nom["t"] / 60, nom["front"], color="#164a70", lw=2)
for km, obs_min, label in FRONT_OBS:
    ax.plot(obs_min / 60, km, "kv", ms=7)
ax.set_xlabel("hours after collapse (08:37)"); ax.set_ylabel("front km")
ax.set_title("Front trajectory vs the six clocks (▼ observed)")
ax.grid(alpha=.25)

ax = axes[0, 1]
ax.plot(nom["t"] / 60, nom["w_front"], color="#2b6b9c",
        label="water fraction w at front")
ax.plot(nom["t"] / 60, np.array(nom["mu_front"]) / nom["mu_dry"],
        color="#a5403a", label="mu at front / mu_dry")
ax.axhline(W_SAT, color="#2b6b9c", ls=":", lw=1, label="W_SAT")
ax2 = ax.twinx()
ax2.plot(0.5 * (x_km[:-1] + x_km[1:]) * 0 + np.nan, [np.nan] * (N - 1))
ax.set_xlabel("hours after collapse"); ax.set_ylim(0, 1.05)
ax.set_title("The dilution dial doing its work")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[1, 0]
cols = {"Betrawati": "#7fb3cf", "Galchhi": "#4a8ab5",
        "Malekhu": "#2b6b9c", "Devghat": "#164a70"}
for s, c in cols.items():
    ax.plot(nom["t"] / 60, nom[s]["q"], color=c, label=s)
ax.plot(443 / 60, 5850, "k*", ms=12, label="obs Devghat 5,850 @ 16:00")
ax.set_xlabel("hours after collapse"); ax.set_ylabel("discharge (m3/s)")
ax.set_title("Station hydrographs — one model, scar to Devghat")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[1, 1]
xf = 0.5 * (x_km[:-1] + x_km[1:])
ax.plot(xf, nom["umax"], color="#164a70", lw=1.5,
        label="peak flow speed envelope Q/A")
axb = ax.twinx()
axb.fill_between(x_km, 0, nom["bed"] / (wn * DX), color="#9a7146", alpha=.4)
axb.set_ylabel("stranded thickness (m)", color="#9a7146")
for km, obs, label in SPEED_OBS:
    ax.plot(km, obs, "o", color="k", ms=6)
    ax.annotate(label, (km, obs), textcoords="offset points", xytext=(6, 6),
                fontsize=7)
ax.plot(11, 53, "s", color="k", ms=6)
ax.annotate("53 m/s avg 0-22 (clock)", (11, 53),
            textcoords="offset points", xytext=(6, 6), fontsize=7)
ax.set_xlabel("path km"); ax.set_ylabel("speed (m/s)")
ax.set_title("Speed envelope + stranded deposit")
ax.legend(fontsize=8, loc="upper right"); ax.grid(alpha=.25)

fig.suptitle("Unified Voellmy-Saint-Venant with dilution dial + stranding — "
             "scar to Devghat, nothing fitted to the Trishuli clocks", y=0.995)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "unified_v1.png"), dpi=130)
print("\nplot -> output/unified_v1.png")
