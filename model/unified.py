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
import copy, csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from core import (G, MU_WET, W_SAT, TAU_Y0, RHO_MIX, U_DEP, T_DEP, FR_MAX,
                  mu_dry_scheidegger, mu_of_w, Reach, step, arrival_fn,
                  entrain_opts, H_ERODE)

DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "output")
os.makedirs(OUT, exist_ok=True)

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

w_hydr = np.clip(4.8 * np.sqrt(Qb), 40.0, 160.0)
wn = np.where(x_km < 34.0, 50.0,
      np.where(x_km < 41.5, np.interp(x_km, [34.0, 36.0, 41.0, 41.5],
                                      [50.0, 200.0, 200.0, 60.0]),
       np.where(x_km < 60.0, 60.0, w_hydr)))
nn = np.interp(x_km, [0, 22, 70, 199], [0.060, 0.055, 0.040, 0.025])

# The dial constants (MU_WET, W_SAT, TAU_Y0, RHO_MIX, U_DEP, T_DEP) and the
# engine now live in model/core.py, shared with every hindcast — see that
# module's docstring for the physics and for why the copies were merged.

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
K_JUNC_KM = {22.0: 3.0, 37.6: 1.5, 160.0: 1.0, 185.0: 1.0}

EXTRA_STATIONS = {}   # {name: km} — extra record points, e.g. a trimline station

# ------------------------------------------------------- observations -------
FRONT_OBS = [(22.0, 7.68, "border CCTV 08:44:50"), (37.6, 13, "Syabrubesi 08:50"),
             (68.4, 43, "Betrawati rising 09:20"),
             (107.6, 150, "Galchhi ~11:00"), (117.0, 163, "Malekhu 11:20"),
             (199.2, 403, "Devghat front 15:20")]
SPEED_OBS = [(30.0, 48.5, "geopera border reach 45-52"),
             (40.0, 11.0, "Syabrubesi opening ~11")]

# ---------------------------------------------------- the reach object ------
# Geometry + baseflow handed to the shared engine (model/core.py). The side-
# valley plan areas and the junction K values are unchanged from ladder.py.
R = Reach(x_km, z, wn, nn, Qb, side=SIDE, k_junc=K_JUNC_KM)
q_lat, wf, nf, K_loc = R.q_lat, R.wf, R.nf, R.K_loc

_settled = {}
def settled_state(dt=0.5, hours=2.0, side_valleys=True):
    """River-only settling from analytic normal depth (cached)."""
    key = (dt, hours, side_valleys)
    if key in _settled:
        return copy.deepcopy(_settled[key])
    S0 = np.maximum(-np.gradient(z, x_km * 1000), 1e-4)
    h = np.maximum((Qb * nn / (wn * np.sqrt(S0))) ** 0.6, 0.05)
    st = R.new_state(h)
    h_chk = st["h"].copy()
    for it in range(int(hours * 3600 / dt)):
        # settle with the PURE-RIVER dial (w=1 -> mu=0), no stranding, no
        # entrainment — the monsoon river at its own baseflow is the datum
        st = step(st, R, dt, mu_dry=0.3, w_sat=W_SAT, mu_wet=MU_WET,
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
             dt=0.5, t_end=10.0 * 3600.0, entrain=None, f_fine_rel=0.0):
    if mu_dry is None:
        mu_dry = mu_dry_scheidegger(V_rel)
    st = settled_state(dt=dt, side_valleys=side_valleys)
    st["avail"][:] = R.h_erode      # settled_state is cached; re-arm the
                                    # erodible layer so H_ERODE can be swept
    h0 = st["h"].copy()
    rel = x_km <= X_REL
    wsum = wn[rel].sum() * DX
    stations = {"Betrawati": 68.4, "Galchhi": 107.6, "Malekhu": 117.0,
                "Devghat": 199.2}
    stations.update(EXTRA_STATIONS)   # additive; empty by default
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
            st["hr"][rel] += dh * (1 - w0)      # provenance tag: ALL release
            # f_fine_rel: the share of release SOLIDS that never ends up in a
            # DEM-visible deposit — wash load, and ice, which is dynamically a
            # solid but geomorphically temporary. hr stays the provenance tag;
            # hf is the rheology/deposition class.
            st["hf"][rel] += dh * (1 - w0) * f_fine_rel
        st = step(st, R, dt, mu_dry, w_sat, mu_wet, side_valleys,
                  deposit=True, u_dep=u_dep, t_dep=t_dep, entrain=entrain)
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
    out.update(arrival=arrival_fn(front, out["t"]), front=front,
               umax=st["umax"], bed=st["bed"], ero=st["ero"], dep=st["dep"],
               mu_dry=mu_dry, h0=h0)
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
    ent = ""
    e, d = ero_dep(r)
    if e or d:
        ent = f" | eroded {e:4.1f} / deposited {d:4.1f} Mm3"
    print(f"  {name:28s} border {clock(ta_b)} | Syabru {clock(ta_sy)} | "
          f"Betrawati {clock(ta_be)} | Galchhi rise {rise30:4.1f} m | "
          f"Devghat {q[i]:6,.0f} @ {clock(tt[i])} | stranded {bed_t:4.1f} Mm3"
          + ent)
    return r


def ero_dep(r, lo=0.0, hi=1e9):
    """Gross bed volumes exchanged by the entrainment closure, Mm3."""
    m = (x_km >= lo) & (x_km <= hi)
    return (float((r["ero"][m] * wn[m] * DX).sum() / 1e6),
            float((r["dep"][m] * wn[m] * DX).sum() / 1e6))

if __name__ == "__main__":
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

    # ============================== ENTRAINMENT =================================
    # The term the model did not have. Scored against geopera's WorldView-3 stereo
    # DEM (1 Sept, after they retracted the 28 Aug "12 Mm3 wedge" as noise): in the
    # ~45% of the corridor their stereo pair covers, 3.2 Mm3 of EROSION against
    # 0.9 Mm3 of deposition — the corridor was net erosional by ~3.5x. Scaling
    # their mapped fraction to the whole corridor, if erosion is distributed like
    # their sample, gives order 7 Mm3 eroded / 2 Mm3 deposited; their calibrated
    # model puts total deposition near 5 Mm3. Take the RATIO (net erosional,
    # ~3.5:1) as the firm observable and the volumes as order-of-magnitude.
    #
    # Nothing in either closure was chosen with reference to these numbers:
    # DELTA_E/DELTA_D are Takahashi's, K_TAU is Frank et al.'s, tan(phi) and C_STAR
    # are standard bed properties, W_SETTLE is medium sand. H_ERODE (the erodible
    # layer) is the one genuinely uncertain input and is swept.
    print("\n" + "=" * 78)
    print("ENTRAINMENT — the corridor was net EROSIONAL by ~3.5x (geopera stereo:")
    print("3.2 Mm3 eroded vs 0.9 Mm3 deposited in the ~45% mapped)")
    print("=" * 78)
    ENT_BASE = {"C ice-rich V=30": dict(V_rel=30e6, w0=0.15, mu_dry=MU_DRY_ICE),
                "F wet slurry V=60": dict(V_rel=60e6, w0=0.40,
                                          mu_dry=MU_DRY_ICE)}
    ent_runs = {}
    for sc, kw in ENT_BASE.items():
        for lab, eo in [("no entrainment", None),
                        ("Takahashi capacity", entrain_opts("takahashi")),
                        ("Frank shear", entrain_opts("shear"))]:
            r = score_line(f"{sc} | {lab}", simulate(entrain=eo, **kw), kw)
            ent_runs[(sc, lab)] = r

    print("\nwhere the bed exchange happens (Takahashi closure, scenario C):")
    r = ent_runs[("C ice-rich V=30", "Takahashi capacity")]
    for lo, hi, nm2 in [(0, 22, "scar->border"), (22, 68, "border->Betrawati"),
                        (68, 108, "->Galchhi"), (108, 199.2, "->Devghat")]:
        e, d = ero_dep(r, lo, hi)
        print(f"  km {lo:5.1f}-{hi:5.1f} {nm2:18s} eroded {e:5.2f} Mm3, "
              f"deposited {d:5.2f} Mm3")
    e_all, d_all = ero_dep(r)
    e_up, d_up = ero_dep(r, 0, 70)
    print(f"  whole corridor: {e_all:.2f} eroded / {d_all:.2f} deposited"
          f"  -> {'net erosional' if e_all > d_all else 'net depositional'}"
          f" {e_all/max(d_all,1e-9):.1f}:1"
          f"   (geopera mapped 45%: 3.2 / 0.9 = 3.5:1 erosional)")
    print(f"  upper 70 km:    {e_up:.2f} eroded / {d_up:.2f} deposited")
    print(f"  LIKE FOR LIKE — what a DEM difference would see is the BULK volume\n"
          f"  change of the valley floor, so stranded solids must be converted to\n"
          f"  bulk at C*=0.65 and added to the closure's deposition:")
    for lab in ["no entrainment", "Takahashi capacity", "Frank shear"]:
        rr = ent_runs[("C ice-rich V=30", lab)]
        e2, d2 = ero_dep(rr)
        bulk = rr["bed"].sum() / 1e6 / 0.65 + d2
        print(f"    {lab:20s} bulk deposition {bulk:5.1f} Mm3 vs erosion "
              f"{e2:4.1f} Mm3   (geopera: ~0.9 measured, ~5 their calibrated "
              f"model, 3.2 eroded)")

    print("\nprovenance and concentration with entrainment (scenario C):")
    for lab in ["no entrainment", "Takahashi capacity", "Frank shear"]:
        rr = ent_runs[("C ice-rich V=30", lab)]
        tt2, qd2 = rr["t"], rr["Devghat"]["q"]
        wd2, wrd2 = rr["Devghat"]["w"], rr["Devghat"]["wr"]
        m2 = (tt2 > 60) & (qd2 > max(1600, 1.05 * float(np.median(qd2))))
        if not m2.any():
            m2 = tt2 > 60
        vt = np.trapezoid(qd2[m2], tt2[m2] * 60)
        friv = np.trapezoid(qd2[m2] * (wd2[m2] - wrd2[m2]), tt2[m2] * 60) / vt
        wmin = float(np.min(wd2[m2]))
        print(f"  {lab:20s} river water at Devghat {100*friv:5.1f}%, "
              f"min water fraction w during passage {wmin:.2f} "
              f"(rho ~{1000+(1-wmin)*1650:,.0f} kg/m3)")

    print("\nH_ERODE sweep (erodible layer depth, the one uncertain input):")
    for he in [1.0, 3.0, 10.0]:
        R.h_erode = he
        rr = simulate(entrain=entrain_opts("takahashi"), V_rel=30e6, w0=0.15,
                      mu_dry=MU_DRY_ICE)
        e, d = ero_dep(rr)
        ta = rr["arrival"](22.0)
        print(f"  H_ERODE={he:4.1f} m: eroded {e:5.2f} Mm3, deposited {d:5.2f} "
              f"Mm3, border {clock(ta)}")
    R.h_erode = H_ERODE

    # The deposition side is settling-limited, and the settling cap uses a QUIET-
    # WATER fall velocity. A real flood keeps sand aloft: for h ~ 10 m at 6 m/s
    # the Rouse number of medium sand is ~0.2, i.e. fully suspended, so w_settle
    # is an upper bound on how fast solids can actually leave. Sweeping it is the
    # honest way to show how much of the deposition excess that explains.
    print("\nW_SETTLE sweep (deposition rate cap; 0.025 = quiet-water medium sand,")
    print("smaller = the suspension the closure does not model):")
    for ws in [0.025, 0.010, 0.005, 0.002]:
        rr = simulate(entrain=entrain_opts("takahashi", w_settle=ws),
                      V_rel=30e6, w0=0.15, mu_dry=MU_DRY_ICE)
        e, d = ero_dep(rr)
        bulk = rr["bed"].sum() / 1e6 / 0.65 + d
        q2 = rr["Devghat"]["q"]; t2 = rr["t"]
        i2 = int(np.argmax(np.where(t2 > 30, q2, -1)))
        print(f"  W_SETTLE={ws:.3f} m/s: eroded {e:5.2f} / deposited {d:5.2f} Mm3"
              f"  (bulk incl. stranding {bulk:5.1f})   Devghat {q2[i2]:6,.0f} @ "
              f"{clock(t2[i2])}")

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
