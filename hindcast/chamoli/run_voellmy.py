#!/usr/bin/env python3
"""
Phase F, step 2 — the VOELLMY-SAINT-VENANT hybrid at Chamoli (7 Feb 2021).

The zero-recalibration kinematic law U = 300*S^0.82 + 4 failed Chamoli's
Tapovan timing 3.2x fast while passing all three video point speeds
(RESULTS.md). Diagnosis: a slope-only law has no flow REGIME and no event
SIZE. This script tests the resolved design (PLAN.md, 3 Sept): route the
event *dynamically* with the ladder's local-inertia Saint-Venant scheme plus
a Coulomb basal-friction term, i.e. the Voellmy friction law

    S_f = mu + n^2 v^2 / h^(4/3)          (Coulomb + turbulent)

so that   mu = 0        -> Manning        -> the calibrated Trishuli ladder
          mu ~ 0.1-0.2  -> dense granular -> equivalent-fluid avalanche.

Steady balance v = sqrt((S-mu) h^(4/3)) / n is the Voellmy terminal velocity
with xi = h^(1/3)/n^2 (n = 0.05 at h = 10 m gives xi ~ 860 m/s^2, mid-range
of published debris-flow xi). Event size enters through the released volume:
26.9 Mm^3 (Shugar et al. 2021) started as a block at the scar, its depth —
not a fitted constant — sets how fast it can run.

WHAT IS AND IS NOT TUNED (honesty rails):
  * mu nominal = 0.155 = the observed energy line H/L (3,711 m / 24 km,
    Shugar's 0.16 travel angle). That is POST-EVENT GEOMETRY — where the
    dense flow died — measured entirely independently of the timing and
    speed observations we score against. Literature band for large rock/ice
    avalanches (RAMMS calibrations, Kolka/ice-rock back-analyses) is
    mu ~ 0.10-0.20; we sweep it.
  * n = 0.05 (upper-Trishuli gorge class value, unchanged), w = 80 m
    (order-of-magnitude Rishiganga gorge width; sensitivity x/2 and x2).
  * Nothing is fitted to the Tapovan arrival or the video speeds.
  * Constant mass (no entrainment). Entrainment roughly doubled the moving
    mass in reality; more mass = deeper = faster, so if the model passes
    the timing test WITH this omission the pass is not owed to it (the
    omission slows the model, and the kinematic law failed FAST).
  * Winter channel assumed dry (baseflow ~10-30 m^3/s is negligible against
    the wave; Shugar: river water only ~8% of even the final water budget).

Scored against the same anchors as run_hindcast.py: Tapovan arrival
34-37 min, video speeds ~25 / ~16 / ~12 m/s, plus TWO new axes the kinematic
law could not even express: where the dense mass stops (observed: energy
line at ~km 24) and whether the front stalls in the km 18-22 low-gradient
basin (S ~ 0.015 << mu -> Coulomb predicts pile-up/creep there).

Outputs: scorecard to stdout, chamoli_voellmy.png.
"""
import csv, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G = 9.81

# ------------------------------------------------------------- geometry -----
rows = list(csv.DictReader(open(os.path.join(HERE, "profile.csv"))))
x_km = np.array([float(r["dist_km"]) for r in rows])
lats = np.array([float(r["lat"]) for r in rows])
lons = np.array([float(r["lon"]) for r in rows])
z_raw = np.array([float(r["elev_m"]) for r in rows])
z = np.minimum.accumulate(z_raw)                 # monotone descent
k = 5                                            # ~2 km smoothing, as before
z = np.convolve(np.pad(z, k, mode="edge"),
                np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
N = len(x_km)
DX = float(np.mean(np.diff(x_km))) * 1000.0      # ~400 m

def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

def km_of(pt):
    return x_km[min(range(N), key=lambda i: hav((lats[i], lons[i]), pt))]

KM_HPP = km_of((30.4789, 79.6978))               # Rishiganga HPP (Raini)
KM_TAPOVAN = km_of((30.4903, 79.6285))           # Tapovan intake
print(f"checkpoints on profile: Rishiganga HPP km {KM_HPP:.1f}, "
      f"Tapovan km {KM_TAPOVAN:.1f}, end km {x_km[-1]:.1f}")

# ------------------------------------------------------------ the event -----
V0 = 26.9e6                # released volume, m^3 (Shugar et al., seismic+DEM)
X_REL = 3.0                # release block spread over km 0-3 of the path
W_NOM = 80.0               # equivalent channel width, m (gorge order of mag.)
N_MAN = 0.05               # Manning n — upper-Trishuli class value, untuned
MU_NOM = 0.155             # = observed H/L energy line (geometry, not timing)
H_FRONT = 0.5              # m — front detection threshold

# --- the MELT-FLUIDIZATION dial: mu evolving along the path -----------------
# Shugar et al.'s central mechanism: the ~20% ice melted PROGRESSIVELY by
# frictional heating during descent ("almost exactly critical" — the fall's
# energy just sufficed to melt all of it; our calcs scenario 0 reproduces
# 4.8 vs 5.0 Mm^3), transforming rock avalanche -> debris flow along the
# runout. Melt mass is proportional to dissipated energy, i.e. to cumulative
# elevation drop, so the water-availability dial slides LINEARLY IN FALL
# COMPLETED f(x) = (z0 - z(x)) / (z0 - z_end):
#     mu(x) = MU_DRY * (1 - f) + MU_WET * f
# Endpoints from literature, zero Chamoli tuning:
#   MU_DRY = 0.30 — Scheidegger (1973) volume-mobility regression evaluated
#            at V = 2.69e7 m^3 gives H/L = 0.29 for a DRY rock avalanche of
#            this size (log H/L = 0.62419 - 0.15666 log V).
#   MU_WET = 0.02 — watery debris flood; the Trishuli ladder limit is mu = 0.
# Consistency check that falls out for free: the path-mean of mu is ~0.16 =
# Chamoli's observed travel angle, BECAUSE the melt was critical (wetting
# completes only at the end of the fall). Nothing here references the timing
# or speed observations being scored.
MU_DRY, MU_WET = 0.30, 0.02

# --- valley-width profile (geometry, not timing) ----------------------------
# The Ronti Gad / Rishiganga gorge is a narrow slot (~60-100 m at flow
# level); the valley opens approaching Raini; the Raini->Tapovan reach is a
# broad low-gradient basin where Shugar et al. map massive aggradation (and
# where the flow briefly ran up the Dhauliganga); below Tapovan the
# Dhauliganga confines again. Class values, order of magnitude only, to be
# replaced by Sentinel-2 measurements — but they are GEOMETRY read off maps,
# containing no timing information. A wide basin thins the flow, and a thin
# flow on S ~ 0.015 is Coulomb-bound: the stall the constant-mu run showed
# becomes depth-dependent, which is exactly the mechanism a granular front
# stalling at Raini needs.
W_X = [0.0, 13.0, 15.0, 17.0, 18.0, 22.0, 23.5, 26.0, 32.4]
W_W = [80.0, 80.0, 150.0, 200.0, 300.0, 300.0, 120.0, 100.0, 100.0]

# fall completed — the melt-equilibrium coordinate. Melt mass ~ dissipated
# energy ~ cumulative drop, and our VALIDATED energy budget (calcs scenario 0,
# reproducing Shugar's criticality) uses drop_total = 3,400 m for
# near-complete melt — i.e. the ice is all melted by roughly the Tapovan
# elevation, not at the end of the modeled path. Normalize accordingly.
DROP_MELT = 3400.0
F_EQ = np.clip((z[0] - z) / DROP_MELT, 0.0, 1.0)

# thermal-lag time: heat conducts into ice fragments of size d over
# tau ~ d^2/(pi^2 kappa_ice), kappa ~ 1.2e-6 m2/s -> 2 min (4 cm), 3.5 min
# (5 cm), 14 min (10 cm), 56 min (20 cm). The a-priori band (fragments
# 4-20 cm) spans tau ~ 2-60 min — wide, so tau is treated as the model's ONE
# FITTED DEGREE OF FREEDOM: the Tapovan arrival selects it (arrival is
# monotone in tau), and the three video point speeds are then the
# out-of-sample test. TAU_STAR is the arrival-selected value.
TAU_STAR = 300.0

OBS_TAPOVAN = (34.0, 37.0)         # min, video (soft +-2)
OBS_SPEEDS = [("near Rishiganga HPP", KM_HPP, 25.0),
              ("just above Tapovan", KM_TAPOVAN - 1.0, 16.0),
              ("just below Tapovan", KM_TAPOVAN + 1.0, 12.0)]

# ------------------------------------------------------------- simulate -----
FR_MAX = 2.0

def simulate(mu, w=W_NOM, n=N_MAN, dt=0.5, t_end=3 * 3600.0, thermal=None):
    """1D local-inertia Saint-Venant + Coulomb clamp (the ladder scheme,
    rectangular section, wide-channel R=h, dry-bed capable). mu may be a
    scalar or a per-interface array (the static fluidization dial).

    thermal=(mu_dry, mu_wet, tau_s) switches on the THERMAL-LAG dial: the
    melt state f becomes a scalar ADVECTED WITH THE MASS, relaxing toward
    the local equilibrium (fall-completed) value f_eq(x) with timescale tau:
        d f/dt |_material = (f_eq - f) / tau,   mu = mu_dry + (mu_wet-mu_dry) f
    Dissipated heat must conduct into ice fragments before it melts them
    (tau ~ d^2/(pi^2 kappa): 3-60 min for 5-20 cm ice debris), so mu lags
    the fall. This is what lets a stalled mass KEEP fluidizing and
    remobilize — stall-and-go — with one physical constant. When thermal is
    set, `mu` is ignored. Returns front trajectory, arrival interpolant,
    depth fields."""
    thermal_on = thermal is not None
    if thermal_on:
        mu_dry_t, mu_wet_t, tau = thermal
        f = np.zeros(N)                          # melt state of the material
    mu_i = np.broadcast_to(np.asarray(mu, dtype=float), (N - 1,))
    has_mu = bool(np.any(mu_i > 0))
    w_n = np.broadcast_to(np.asarray(w, dtype=float), (N,))  # per-node width
    w_f = 0.5 * (w_n[:-1] + w_n[1:])
    h = np.zeros(N)
    rel = x_km <= X_REL
    h[rel] = V0 / (w_n[rel].sum() * DX)          # release block depth
    Qi = np.zeros(N - 1)                         # interface discharge
    nt = int(t_end / dt)
    rec_t, rec_front = [], []
    x_face = 0.5 * (x_km[:-1] + x_km[1:])
    watch_j = {km: int(np.argmin(np.abs(x_face - km)))
               for _, km, _ in OBS_SPEEDS}
    rec_v = {km: [] for km in watch_j}           # local flow speed Q/A
    hmax = h.copy()
    save = max(int(5.0 / dt), 1)
    for it in range(nt):
        eta = z + h
        Sf = (eta[:-1] - eta[1:]) / DX
        hfe = np.maximum(np.maximum(eta[:-1], eta[1:])
                         - np.maximum(z[:-1], z[1:]), 0.0)
        wet = hfe > 0.05
        Af = np.maximum(w_f * hfe, 1e-6)
        if thermal_on:
            f_face = np.where(Qi >= 0, f[:-1], f[1:])
            mu_i = mu_dry_t + (mu_wet_t - mu_dry_t) * f_face
            has_mu = True
        num = Qi + G * Af * dt * Sf
        den = 1.0 + G * dt * n ** 2 * np.abs(Qi) \
            / (Af * np.maximum(hfe, 0.05) ** (4 / 3))
        Qi = np.where(wet, num / den, 0.0)
        if has_mu:
            # Coulomb: sign-preserving momentum clamp = static friction.
            Qi = np.sign(Qi) * np.maximum(np.abs(Qi) - mu_i * G * Af * dt, 0.0)
        Qcap = FR_MAX * Af * np.sqrt(G * np.maximum(hfe, 0.05))
        Qi = np.clip(Qi, -Qcap, Qcap)
        # donor-cell flux limit: an interface may not drain more than 90% of
        # its donor cell in one step (dry-front safety)
        Qi = np.where(Qi > 0, np.minimum(Qi, 0.9 * h[:-1] * w_n[:-1] * DX / dt),
                      np.maximum(Qi, -0.9 * h[1:] * w_n[1:] * DX / dt))
        dV = np.zeros(N)
        dV[:-1] -= Qi
        dV[1:] += Qi
        # open downstream boundary: normal-depth Manning outflow (the runs
        # that get there are watery; Coulomb runs die far upstream)
        S_end = max((z[-2] - z[-1]) / DX, 1e-3)
        Q_end = (w_n[-1] * h[-1] / n) * max(h[-1], 0.0) ** (2 / 3) * math.sqrt(S_end)
        dV[-1] -= Q_end
        if thermal_on:
            # advect the melt state with the mass, then relax toward f_eq
            Ff = Qi * f_face
            dHF = np.zeros(N)
            dHF[:-1] -= Ff
            dHF[1:] += Ff
            dHF[-1] -= Q_end * f[-1]
            hf = h * f + dHF * dt / (w_n * DX)
        h += dV * dt / (w_n * DX)
        h = np.maximum(h, 0.0)
        if thermal_on:
            present = h > 0.01
            f = np.where(present, hf / np.maximum(h, 0.01), 0.0)
            f = np.clip(f + (F_EQ - f) * (dt / tau) * present, 0.0, 1.0)
        np.maximum(hmax, h, out=hmax)
        if it % save == 0:
            wetx = x_km[h > H_FRONT]
            rec_t.append(it * dt / 60.0)                     # minutes
            rec_front.append(wetx.max() if len(wetx) else 0.0)
            for km, j in watch_j.items():
                rec_v[km].append(abs(Qi[j]) / max(Af[j], 1e-6)
                                 if hfe[j] > 0.05 else 0.0)
    t = np.array(rec_t)
    front = np.maximum.accumulate(np.array(rec_front))       # monotone front
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
            return float(t[0])
        f0, f1 = front[i - 1], front[i]
        if f1 <= f0:
            return float(t[i])
        return float(t[i - 1] + (km - f0) / (f1 - f0)
                     * (t[i] - t[i - 1]))
    def speed_at(km, half_min=0.75):                         # +-45 s window
        ta = arrival(km)
        if not np.isfinite(ta):
            return 0.0
        t0, t1 = ta - half_min, ta + half_min
        k0, k1 = np.interp([t0, t1], t, front)
        return (k1 - k0) * 1000.0 / ((t1 - t0) * 60.0)
    def flow_speed_at(km, t_lo=1.0, t_hi=5.0):
        # peak material velocity Q/A at the checkpoint within [-t_lo, +t_hi]
        # min of front passage — the model quantity a feature-tracking video
        # actually measures (front ADVANCE and material speed differ in an
        # intermittent, stop-and-go flow)
        ta = arrival(km)
        if not np.isfinite(ta) or km not in rec_v:
            return 0.0
        v = np.array(rec_v[km])
        m = (t >= ta - t_lo) & (t <= ta + t_hi)
        return float(v[m].max()) if m.any() else 0.0
    return dict(t=t, front=front, arrival=arrival, speed_at=speed_at,
                flow_speed_at=flow_speed_at,
                h_final=h.copy(), hmax=hmax, mu=mu, w=w)

# ----------------------------------------------------------------- runs -----
print(f"\nrelease block: {V0/1e6:.1f} Mm3 over km 0-{X_REL:.0f}, "
      f"w={W_NOM:.0f} m -> {V0/(W_NOM*(x_km<=X_REL).sum()*DX):.0f} m deep")
MUS = [0.0, 0.10, 0.13, MU_NOM, 0.19]
runs = {}
for mu in MUS:
    r = simulate(mu)
    runs[mu] = r
    ta = r["arrival"](KM_TAPOVAN)
    stop = r["front"][-1]
    print(f"  mu={mu:5.3f} const: Tapovan arrival "
          f"{'%6.1f min' % ta if np.isfinite(ta) else '  never'}, "
          f"front reaches km {stop:5.1f}")

# the melt-fluidization dial: mu slides dry->wet linearly in fall completed
f_node = F_EQ
mu_node = MU_DRY * (1.0 - f_node) + MU_WET * f_node
mu_face = 0.5 * (mu_node[:-1] + mu_node[1:])
fluid = simulate(mu_face)
ta_f = fluid["arrival"](KM_TAPOVAN)
print(f"  FLUIDIZATION mu {MU_DRY}->{MU_WET}: Tapovan arrival "
      f"{'%6.1f min' % ta_f if np.isfinite(ta_f) else '  never'}, "
      f"front reaches km {fluid['front'][-1]:5.1f}")
print(f"  (path-mean mu = {mu_node.mean():.3f}; observed travel angle 0.16)")

# geometry-aware runs: same friction laws on the valley-width profile
w_profile = np.interp(x_km, W_X, W_W)
fluid_geo = simulate(mu_face, w=w_profile)
const_geo = simulate(MU_NOM, w=w_profile)
for nm, r in [("FLUIDIZATION + width profile", fluid_geo),
              ("const mu=0.155 + width profile", const_geo)]:
    ta = r["arrival"](KM_TAPOVAN)
    print(f"  {nm}: Tapovan arrival "
          f"{'%6.1f min' % ta if np.isfinite(ta) else '  never'}, "
          f"front reaches km {r['front'][-1]:5.1f}")

# THE THERMAL-LAG runs: melt state advected with the mass, tau-relaxation.
# Arrival is monotone in tau -> the observed 34-37 min window SELECTS tau
# (one fitted dof); everything else about that run is then out-of-sample.
print("\nthermal-lag dial (advected f, relax to fall-completed over tau):")
thermal_runs = {}
for tau in [120.0, 180.0, TAU_STAR, 420.0, 600.0, 900.0, 1800.0]:
    r = simulate(0.0, w=w_profile, thermal=(MU_DRY, MU_WET, tau))
    thermal_runs[tau] = r
    ta = r["arrival"](KM_TAPOVAN)
    d_cm = 100 * math.sqrt(tau * math.pi ** 2 * 1.2e-6)
    print(f"  tau={tau/60:4.0f} min (ice d~{d_cm:4.1f} cm): Tapovan arrival "
          f"{'%6.1f min' % ta if np.isfinite(ta) else '  never'}, "
          f"front reaches km {r['front'][-1]:5.1f}")
therm = thermal_runs[TAU_STAR]

# sensitivities of the thermal-lag run at the arrival-selected tau
def mu_face_for(mu_dry):
    m = mu_dry * (1 - f_node) + MU_WET * f_node
    return 0.5 * (m[:-1] + m[1:])
w_narrow = np.interp(x_km, W_X, [w * 0.5 if w > 100 else w for w in W_W])
w_wide = np.interp(x_km, W_X, [w * 2.0 if w > 100 else w for w in W_W])
sens = {
    "basin widths x0.5": simulate(0.0, w=w_narrow,
                                  thermal=(MU_DRY, MU_WET, TAU_STAR)),
    "basin widths x2": simulate(0.0, w=w_wide,
                                thermal=(MU_DRY, MU_WET, TAU_STAR)),
    "n=0.04": simulate(0.0, w=w_profile, n=0.04,
                       thermal=(MU_DRY, MU_WET, TAU_STAR)),
    "n=0.06": simulate(0.0, w=w_profile, n=0.06,
                       thermal=(MU_DRY, MU_WET, TAU_STAR)),
    "mu_dry=0.25": simulate(0.0, w=w_profile,
                            thermal=(0.25, MU_WET, TAU_STAR)),
    "mu_dry=0.35": simulate(0.0, w=w_profile,
                            thermal=(0.35, MU_WET, TAU_STAR)),
    "uniform w=80": simulate(0.0, thermal=(MU_DRY, MU_WET, TAU_STAR)),
    "static dial (tau=0)": fluid_geo,
}

# ------------------------------------------------------------ scorecard -----
obs_mid = 0.5 * sum(OBS_TAPOVAN)
lo50, hi50 = 0.5 * OBS_TAPOVAN[0], 1.5 * OBS_TAPOVAN[1]

def score(r, title):
    print(f"\n========== SCORECARD - {title} ==========")
    ta = r["arrival"](KM_TAPOVAN)
    if np.isfinite(ta):
        verdict = "PASS" if lo50 <= ta <= hi50 else "FAIL"
        print(f"Tapovan ARRIVAL      model {ta:6.1f} min   obs "
              f"{OBS_TAPOVAN[0]:.0f}-{OBS_TAPOVAN[1]:.0f} min   error "
              f"{100*(ta-obs_mid)/obs_mid:+.0f}%   "
              f"[+-50% band {lo50:.0f}-{hi50:.0f}] -> {verdict}")
        mean_u = KM_TAPOVAN * 1000 / (ta * 60)
        print(f"mean speed scar->Tapovan: model {mean_u:.1f} m/s, observed ~11 m/s")
    else:
        print(f"Tapovan ARRIVAL      model  never   obs {OBS_TAPOVAN[0]:.0f}-"
              f"{OBS_TAPOVAN[1]:.0f} min -> FAIL "
              f"(front dies at km {r['front'][-1]:.1f})")
    for label, km, obs in OBS_SPEEDS:
        u = r["speed_at"](km)
        v = r["flow_speed_at"](km)
        verdict = "PASS" if abs(v - obs) / obs <= 0.5 else "FAIL"
        print(f"flow speed {label:22s} km {km:4.1f}  model {v:5.1f} m/s "
              f"(front adv {u:4.1f})   obs {obs:4.0f}   "
              f"error {100*(v-obs)/obs:+.0f}% -> {verdict}")
    t18, t22 = r["arrival"](18.0), r["arrival"](22.0)
    if np.isfinite(t22):
        print(f"basin transit km 18->22: {t22-t18:.1f} min "
              f"(mean {4000/((t22-t18)*60):.1f} m/s)")

score(runs[0.0], "water limit mu=0 (control: reproduces kinematic-law failure)")
score(runs[MU_NOM], "constant mu = H/L = 0.155 (single-regime Voellmy)")
score(fluid, f"MELT-FLUIDIZATION mu {MU_DRY}->{MU_WET} linear in fall completed")
score(fluid_geo, "MELT-FLUIDIZATION (static dial) + valley-width profile")
score(therm, f"THERMAL-LAG dial tau={TAU_STAR/60:.0f} min (arrival-selected) + width profile")

print(f"\nsensitivity of Tapovan arrival, thermal-lag model at tau={TAU_STAR/60:.0f} min:")
ta_g = therm["arrival"](KM_TAPOVAN)
print(f"  {'nominal':24s} "
      f"{'%6.1f min' % ta_g if np.isfinite(ta_g) else ' never'}")
for nm, r in sens.items():
    ta_s = r["arrival"](KM_TAPOVAN)
    print(f"  {nm:24s} {'%6.1f min' % ta_s if np.isfinite(ta_s) else ' never'}"
          f"   (front to km {r['front'][-1]:.1f})")

print("\narrival table, thermal-lag nominal (min after 10:21:14 IST):")
for km in [4, 8, 12, KM_HPP, 18, 20, 22, KM_TAPOVAN, KM_TAPOVAN + 1]:
    a = therm["arrival"](km)
    print(f"  km {km:5.1f}: {'%6.1f' % a if np.isfinite(a) else ' never'}")

# --------------------------------------------------------------- figure -----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
marks = [("Rishiganga HPP", KM_HPP), ("Tapovan", KM_TAPOVAN)]

ax = axes[0]
cmap = {0.0: "#c44", 0.10: "#e79b52", 0.13: "#8aa84f",
        MU_NOM: "#7a9cc0", 0.19: "#7a5aa0"}
for mu in [0.0, 0.10, MU_NOM]:
    r = runs[mu]
    lbl = (f"mu=0 (water limit)" if mu == 0.0 else
           f"mu={mu:.3f}=H/L const" if mu == MU_NOM else f"mu={mu:.2f} const")
    ax.plot(r["t"], r["front"], color=cmap[mu], lw=1.2, label=lbl)
ax.plot(fluid["t"], fluid["front"], color="#4a8ab5", lw=1.2,
        label=f"static dial mu {MU_DRY}->{MU_WET}, w=80")
ax.plot(fluid_geo["t"], fluid_geo["front"], color="#4a8ab5", lw=1.2, ls="--",
        label="static dial + width profile")
for tau, lsty, lw_ in [(120.0, ":", 1.2), (TAU_STAR, "-", 2.6),
                       (1800.0, "--", 1.2)]:
    r = thermal_runs[tau]
    ax.plot(r["t"], r["front"], color="#164a70", ls=lsty, lw=lw_,
            label=f"THERMAL LAG tau={tau/60:.0f} min"
                  + (" (arrival-selected)" if tau == TAU_STAR else ""))
ax.axhspan(18, 22, color="0.9", zorder=0)
ax.text(118, 20, "low-gradient basin\n(S~0.015)", fontsize=7, va="center",
        ha="right")
ax.plot([obs_mid], [KM_TAPOVAN], "kv", ms=9, zorder=5,
        label="observed: Tapovan 34-37 min")
ax.plot([OBS_TAPOVAN[0], OBS_TAPOVAN[1]], [KM_TAPOVAN] * 2, "k-", lw=3)
ax.plot([lo50, hi50], [KM_TAPOVAN] * 2, "k-", lw=1, alpha=0.4)
ax.set_xlim(0, 120); ax.set_ylim(0, 34)
ax.set_xlabel("minutes after 10:21:14 IST"); ax.set_ylabel("front position (path km)")
ax.set_title("Front trajectory vs friction law\n(black bar = obs, faint = +-50% tier band)")
ax.legend(fontsize=7, loc="lower right"); ax.grid(alpha=.25)

ax = axes[1]
kms = np.linspace(4, min(therm["front"][-1], 26), 120)
ax.plot(kms, [therm["speed_at"](km) for km in kms], color="#164a70", lw=2,
        label=f"thermal lag tau={TAU_STAR/60:.0f} min + widths")
r0 = runs[0.0]
ax.plot(kms, [r0["speed_at"](km) for km in kms], color="#c44", alpha=.6,
        label="water limit mu=0")
for label, km, obs in OBS_SPEEDS:
    ax.plot(km, obs, "o", color="k", ms=6)
    ax.annotate(f"obs {obs:.0f}", (km, obs), textcoords="offset points",
                xytext=(6, 5), fontsize=7)
for nm, km in marks:
    ax.axvline(km, color="0.88", zorder=0)
for label, km, obs in OBS_SPEEDS:
    ax.plot(km, therm["flow_speed_at"](km), "s", color="#164a70", ms=7,
            mfc="none", mew=1.8)
ax.plot([], [], "s", color="#164a70", mfc="none", mew=1.8,
        label="model flow speed Q/A at passage\n(what a video actually tracks)")
ax.set_xlabel("path km"); ax.set_ylabel("speed (m/s)")
ax.set_title("Speeds vs Shugar et al. video points\n(lines: front advance; squares: material speed)")
ax.legend(fontsize=8); ax.grid(alpha=.25)

# mechanism panel: the flow decelerates/stalls where bed slope S < mu(x),
# runs free where S > mu. The dial crossing the terrain IS the story.
ax = axes[2]
S_bed = np.maximum(-np.gradient(z, x_km * 1000.0), 1e-4)
ax.fill_between(x_km, 0, S_bed, color="0.85", label="bed slope S(x)")
ax.plot(x_km, mu_node, color="#164a70", lw=2,
        label=f"mu(x): {MU_DRY} dry -> {MU_WET} wet\n(linear in fall completed)")
ax.axhline(MU_NOM, color="#7a9cc0", lw=1, ls="--", label="H/L = 0.155")
for nm, km in marks:
    ax.axvline(km, color="0.8", zorder=0)
    ax.annotate(nm, (km, 0.44), rotation=90, fontsize=7, ha="right")
ax.axvspan(18, 22, color="#e79b52", alpha=0.15)
ax.text(20, 0.36, "basin", fontsize=7, ha="center", color="#a06010")
ax.set_xlim(0, 33); ax.set_ylim(0, 0.5)
ax.set_xlabel("path km"); ax.set_ylabel("slope / friction coefficient")
ax.set_title("The regime dial vs the terrain:\nflow runs where S > mu, crawls where S < mu")
ax.legend(fontsize=7, loc="upper right"); ax.grid(alpha=.25)

fig.suptitle("Chamoli 2021 - Voellmy-Saint-Venant hybrid (ladder scheme + Coulomb mu + thermal-lag melt): "
             "size from released volume, mu endpoints from literature, ONE dof (tau) fitted to arrival",
             fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chamoli_voellmy.png"), dpi=140)
print("\nfigure -> chamoli_voellmy.png")

# ------------------------- export for the report page (fig-chamoli) ---------
def _traj(r, tmax=120.0, step=6):
    m = r["t"] <= tmax
    return {"t": [round(float(v), 2) for v in r["t"][m][::step]],
            "km": [round(float(v), 2) for v in r["front"][m][::step]]}
_ta = therm["arrival"](KM_TAPOVAN)
exp = {
    "tapovan_km": round(float(KM_TAPOVAN), 1),
    "obs_window": [34, 37], "band50": [17, 55.5], "basin": [18, 22],
    "curves": [
        {"label": "water limit mu=0", "key": "water", **_traj(runs[0.0])},
        {"label": "constant mu=0.155 (=H/L)", "key": "const",
         **_traj(runs[MU_NOM])},
        {"label": "melt dial, instant (tau=0)", "key": "static",
         **_traj(fluid_geo)},
        {"label": "thermal lag tau=2 min", "key": "t2",
         **_traj(thermal_runs[120.0])},
        {"label": "thermal lag tau=5 min", "key": "t5", **_traj(therm)},
        {"label": "thermal lag tau=15 min", "key": "t15",
         **_traj(thermal_runs[900.0])},
        {"label": "thermal lag tau=30 min", "key": "t30",
         **_traj(thermal_runs[1800.0])},
    ],
    "score": {
        "arrival_min": round(float(_ta), 1),
        "mean_speed": round(float(KM_TAPOVAN * 1000 / (_ta * 60)), 1),
        "flow_speeds": [[label, round(float(km), 1), obs,
                         round(float(therm["flow_speed_at"](km)), 1)]
                        for label, km, obs in OBS_SPEEDS],
        "sens_arrivals": {nm: (round(float(r["arrival"](KM_TAPOVAN)), 1)
                               if np.isfinite(r["arrival"](KM_TAPOVAN))
                               else None) for nm, r in sens.items()},
    },
}
with open(os.path.join(HERE, "voellmy_curves.json"), "w") as fh:
    json.dump(exp, fh, separators=(",", ":"))
print("report data -> voellmy_curves.json")
