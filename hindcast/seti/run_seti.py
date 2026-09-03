#!/usr/bin/env python3
"""
Phase F — SETI 2012 BLIND HINDCAST. The intermediate-regime test.

Chamoli (dry, winter, granular; mu ~ 0.3 -> 0.02 by melt) and Langtang (wet,
monsoon, watery; the river supplies the water) are the two endmembers the
dilution dial spans. Seti sits between them BY CONSTRUCTION: a rock/ice
avalanche fell into a gorge holding a lake that had been impounding behind a
rockfall dam for weeks (Kargel; Hanisch et al. 2013). Water is neither made
by melting nor lying along the channel — it is a discrete stored volume,
released on impact.

BLIND PROTOCOL. Every dial constant is FROZEN at the value already published
in our Trishuli/Chamoli work; nothing here is fitted to a Seti observation:
    MU_WET = 0.02, W_SAT = 0.25            (unified.py, Langtang)
    Bingham slurry branch, TAU_Y0 = 400 Pa, RHO_MIX = 1800  (unified.py)
    U_DEP = 1.0 m/s, T_DEP = 120 s          (stranding, unified.py)
    mu_dry from Scheidegger(V)              (as used at Chamoli and Langtang)
    convective momentum + curvature shock viscosity  (unified.py v2)
The step() function below is a verbatim copy of model/unified.py's, with the
Trishuli geometry swapped for the Seti profile. Event inputs come only from
research/seti-2012-anchors.md, which was written BEFORE this run.

SCORED AGAINST (from the anchors file, all out of sample):
    Kharapani (path km 31.2) at 28.1 min after the 09:09:56 seismic impact
        -- the hard anchor (photo timestamp), and independently the published
        "20 km downstream in 28 minutes" measured from the dam, which our
        stitched path puts at km 11.2: 31.2 - 11.2 = 20.0 km. Two independent
        readings of the geometry agree, which is a good sign for the path.
    Pokhara (km 54.4) at ~85 min (medium).
    Mean front speed ~12 m/s over the dam->Kharapani reach.
    Peak discharge ~935 m3/s (medium; personal communication).
    Flow density 1.88 g/cm3 => water volume fraction w ~ 0.47 in the moving
        mixture -- an independent published measurement of the very quantity
        the dial advects. The model should sit in the slurry branch (w > 0.25).

PRE-REGISTERED EXPECTATION (written before running, in the anchors file):
the front must be SLOW -- ~12 m/s, four times slower than Langtang. A model
tuned on Langtang's fast wave would fail here by running away. That is the
failure mode this test exists to catch.
"""
import csv, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G = 9.81

# ------------------------------------------------------------- geometry -----
rows = list(csv.DictReader(open(os.path.join(HERE, "profile.csv"))))
x_km = np.array([float(r["dist_km"]) for r in rows])
zp = np.minimum.accumulate(np.array([float(r["elev_m"]) for r in rows]))
k = 5
z = np.convolve(np.pad(zp, k, mode="edge"),
                np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
N = len(x_km)
DX = float(np.mean(np.diff(x_km))) * 1000.0

KM_DAM = 11.2          # gorge head below Sabche Cirque = the impoundment
KM_KHARAPANI = 31.2    # OSM "Kharpani" hamlet on the stitched path
KM_POKHARA = 54.4

# Pre-monsoon (5 May) baseflow: snowmelt-fed, small. Seti at Pokhara mean
# annual ~50 m3/s; early May is the low season. Class values, not fitted.
QB_X = np.array([0.0, 11.2, 31.2, 54.4])
QB_Q = np.array([2.0, 6.0, 25.0, 45.0])
Qb = np.interp(x_km, QB_X, QB_Q)
q_lat = np.zeros(N)
q_lat[1:] = np.diff(Qb)

# The Seti gorge is a slot canyon (famously only metres wide where it cuts
# Pokhara). Widths from that character, not from any flood observation.
wn = np.interp(x_km, [0, 11, 20, 35, 45, 54.4], [60, 25, 30, 40, 50, 60])
nn = np.interp(x_km, [0, 11, 31, 54.4], [0.060, 0.055, 0.045, 0.035])

# ------------------------------------------- FROZEN dial constants ----------
MU_WET, W_SAT = 0.02, 0.25
TAU_Y0, RHO_MIX = 400.0, 1800.0
U_DEP, T_DEP = 1.0, 120.0
FR_MAX = 2.0

def mu_dry_scheidegger(V_m3):
    return 10 ** (0.62419 - 0.15666 * math.log10(V_m3))

def mu_of_w(w, h, mu_dry, mu_wet=MU_WET, w_sat=W_SAT):
    lo = mu_dry + (mu_wet - mu_dry) * np.clip(w / w_sat, 0.0, 1.0)
    tau_y = TAU_Y0 * np.clip((1.0 - w) / (1.0 - w_sat), 0.0, 1.0)
    hi = np.minimum(tau_y / (RHO_MIX * G * np.maximum(h, 0.05)), mu_wet)
    return np.where(w <= w_sat, lo, hi)

# ------------------------------------------------------------ the event -----
V_AVA = 22e6           # Kargel/NASA; NHESS lineage says 33e6 - swept below
W0 = 0.10              # liquid fraction of the avalanche (rock+ice, dry-ish)
X_REL, T_REL = 1.2, 180.0
V_IMP = 3.0e6          # impounded lake behind the rockfall dam: "several
                       # million cubic metres" total (SANDRP/Kargel) - swept
KM_IMP_SPREAD = 2.0    # the impoundment occupies ~2 km of gorge behind the dam

nf = 0.5 * (nn[:-1] + nn[1:])
wf = 0.5 * (wn[:-1] + wn[1:])

def step(st, dt, mu_dry, w_sat=W_SAT, mu_wet=MU_WET, deposit=True,
         u_dep=U_DEP, t_dep=T_DEP):
    """Verbatim copy of model/unified.py step(), Seti geometry, no side
    valleys (none mapped on this reach) and no junction losses."""
    h, hw, hwr, hr, bed = st["h"], st["hw"], st["hwr"], st["hr"], st["bed"]
    Qi = st["Qi"]
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
    uQ = Qi * Qi / Af
    conv = np.zeros(N - 1)
    conv[1:] = np.where(Qi[1:] >= 0, (uQ[1:] - uQ[:-1]) / DX, 0.0)
    conv[:-1] += np.where(Qi[:-1] < 0, (uQ[1:] - uQ[:-1]) / DX, 0.0)
    num = Qi + dt * (G * Af * Sf - conv)
    den = 1.0 + G * dt * nf ** 2 * np.abs(Qi) / (Af * hfe ** (4 / 3))
    Qi = num / den
    Qi = np.sign(Qi) * np.maximum(np.abs(Qi) - mu_i * G * Af * dt, 0.0)
    Qcap = FR_MAX * Af * np.sqrt(G * hfe)
    Qi = np.clip(Qi, -Qcap, Qcap)
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
    h = h + dV * dt / (wn * DX)
    hw = hw + dW * dt / (wn * DX)
    hwr = hwr + dWr * dt / (wn * DX)
    hr = hr + dR * dt / (wn * DX)
    h = np.maximum(h, 0.05)
    hw = np.clip(hw, 0.0, h); hwr = np.clip(hwr, 0.0, hw)
    hr = np.clip(hr, 0.0, h)
    if deposit:
        u_node = np.zeros(N)
        u_node[:-1] = np.abs(Qi) / Af
        u_node[1:] = np.maximum(u_node[1:], np.abs(Qi) / Af)
        h_sol = np.maximum(h - hw, 0.0)
        strand = (u_node < u_dep) & (hw / np.maximum(h, 1e-6) < w_sat) \
            & (h_sol > 0.02)
        dep = np.where(strand, h_sol * dt / t_dep, 0.0)
        h = np.maximum(h - dep, 0.05)
        hr = np.clip(hr - dep, 0.0, None)
        bed = bed + dep * wn * DX
    st.update(h=h, hw=hw, hwr=hwr, hr=hr, Qi=Qi, bed=bed)
    st["umax"] = np.maximum(st["umax"], np.abs(Qi) / Af)
    return st

def simulate(v_ava=V_AVA, v_imp=V_IMP, w0=W0, mu_dry=None, dt=0.4,
             t_end=3.0 * 3600.0):
    if mu_dry is None:
        mu_dry = mu_dry_scheidegger(v_ava)
    S0 = np.maximum(-np.gradient(z, x_km * 1000), 1e-4)
    h = np.maximum((Qb * nn / (wn * np.sqrt(S0))) ** 0.6, 0.05)
    st = dict(h=h, hw=h.copy(), hwr=np.zeros(N), hr=np.zeros(N),
              Qi=0.5 * (Qb[:-1] + Qb[1:]), bed=np.zeros(N),
              umax=np.zeros(N - 1))
    # settle the pre-monsoon channel (dial at pure water -> mu = 0)
    for _ in range(int(1200 / dt)):
        st = step(st, dt, mu_dry=0.3, deposit=False)
    # THE IMPOUNDMENT: a standing lake behind the rockfall dam at KM_DAM,
    # present before the avalanche arrives. Filled as extra water depth over
    # the 2 km of gorge behind the dam.
    imp = (x_km >= KM_DAM - KM_IMP_SPREAD) & (x_km <= KM_DAM)
    d_imp = v_imp / (wn[imp].sum() * DX)
    st["h"][imp] += d_imp
    st["hw"][imp] += d_imp
    h0 = st["h"].copy()
    st["umax"] = np.zeros(N - 1)
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
        st = step(st, dt, mu_dry)
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
    tt = out["t"]
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
            return float(tt[0])
        f0, f1 = front[i - 1], front[i]
        if f1 <= f0:
            return float(tt[i])
        return float(tt[i - 1] + (km - f0) / (f1 - f0)
                     * (tt[i] - tt[i - 1]))
    out.update(arrival=arrival, front=front, umax=st["umax"], bed=st["bed"],
               mu_dry=mu_dry)
    return out

# ---------------------------------------------------------------- score -----
OBS = {"Kharapani": (KM_KHARAPANI, 28.1), "Pokhara": (KM_POKHARA, 85.0)}

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
              f"{20.0e3/((t_k-t_d)*60):5.1f} m/s   obs ~12")
    q = r["Kharapani"]["q"]; tt = r["t"]
    m = tt > 2
    i = int(np.argmax(np.where(m, q, -1)))
    print(f"  peak Q at Kharapani {q[i]:6,.0f} m3/s at {tt[i]:5.1f} min"
          f"   obs ~935")
    wk = r["Kharapani"]["w"]
    j = int(np.argmax(np.where(m, q, -1)))
    print(f"  water fraction w at Kharapani during passage {wk[j]:.2f}"
          f"   obs ~0.47 (density 1.88 g/cm3)")
    print(f"  stranded solids {r['bed'].sum()/1e6:4.1f} Mm3 of "
          f"{V_AVA/1e6*(1-W0):4.1f} Mm3 released")

print(f"Seti 2012 blind hindcast — path {x_km[-1]:.1f} km, "
      f"{z[0]:.0f} m -> {z[-1]:.0f} m")
print(f"dam km {KM_DAM}, Kharapani km {KM_KHARAPANI} "
      f"({KM_KHARAPANI-KM_DAM:.1f} km below the dam; published 20 km)")
print(f"FROZEN: MU_WET={MU_WET}, W_SAT={W_SAT}, TAU_Y0={TAU_Y0}, "
      f"U_DEP={U_DEP}, T_DEP={T_DEP}")

base = simulate()
score(base, "nominal: 22 Mm3 avalanche + 3 Mm3 impoundment")

for nm, kw in [("33 Mm3 avalanche (NHESS)", dict(v_ava=33e6)),
               ("impoundment 1 Mm3", dict(v_imp=1e6)),
               ("impoundment 6 Mm3", dict(v_imp=6e6)),
               ("NO impoundment (avalanche only)", dict(v_imp=0.0)),
               ("wetter avalanche w0=0.25", dict(w0=0.25)),
               ("drier avalanche w0=0.02", dict(w0=0.02))]:
    score(simulate(**kw), nm)

# ---------------------------------------------------------------- plot ------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
ax = axes[0]
ax.plot(base["t"], base["front"], color="#164a70", lw=2.2, label="model front")
for s, (km, obs) in OBS.items():
    ax.plot(obs, km, "kv", ms=9)
    ax.annotate(f"{s} obs {obs:.0f} min", (obs, km), fontsize=8,
                textcoords="offset points", xytext=(6, -12))
ax.axhline(KM_DAM, color="#9a7146", ls="--", lw=1, label="rockfall dam / lake")
ax.set_xlim(0, 120); ax.set_ylim(0, 56)
ax.set_xlabel("minutes after 09:09:56 NPT"); ax.set_ylabel("path km")
ax.set_title("Front trajectory vs the photo clock")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[1]
for s, c in [("Kharapani", "#2b6b9c"), ("Pokhara", "#164a70")]:
    ax.plot(base["t"], base[s]["q"], color=c, label=s)
ax.axhline(935, color="k", ls=":", lw=1.2, label="obs peak ~935 m³/s")
ax.set_xlim(0, 120)
ax.set_xlabel("minutes after impact"); ax.set_ylabel("discharge (m³/s)")
ax.set_title("Hydrographs")
ax.legend(fontsize=8); ax.grid(alpha=.25)

ax = axes[2]
ax.plot(base["t"], base["Kharapani"]["w"], color="#2b6b9c",
        label="w at Kharapani")
ax.axhline(0.47, color="k", ls=":", lw=1.2,
           label="obs w≈0.47 (ρ=1.88 g/cm³)")
ax.axhline(W_SAT, color="#9a7146", ls="--", lw=1, label="W_SAT (dial knee)")
ax.set_xlim(0, 120); ax.set_ylim(0, 1.05)
ax.set_xlabel("minutes after impact"); ax.set_ylabel("water volume fraction")
ax.set_title("The dial's own variable vs a published density")
ax.legend(fontsize=8); ax.grid(alpha=.25)

fig.suptitle("Seti 2012 blind hindcast — dilution dial frozen at Trishuli/Chamoli values, "
             "event inputs from the pre-registered anchors file", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "seti_hindcast.png"), dpi=140)
print("\nfigure -> seti_hindcast.png")
