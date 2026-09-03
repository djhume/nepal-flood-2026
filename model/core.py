#!/usr/bin/env python3
"""
model/core.py — the ONE Voellmy-Saint-Venant engine, shared by every event.

WHY THIS MODULE EXISTS. The same step() was copy-pasted into model/unified.py,
hindcast/seti/run_seti.py and (in a reduced form) hindcast/chamoli/
run_voellmy.py. The arrival() plateau bug had to be found once and fixed three
times; the next such bug would have been found once and fixed twice. Physics
lives here now; the event scripts contribute geometry, release and scoring.

The engine, unchanged from the published runs:
  * local-inertia Saint-Venant (Bates et al. 2010) + upwind convective
    momentum d(uQ)/dx, semi-implicit Manning friction, Froude cap, donor-cell
    flux limiter, curvature-triggered von Neumann shock viscosity;
  * a Coulomb/Bingham basal resistance set by the DILUTION DIAL mu(w) — one
    dial for every event, water arriving by melt (Chamoli), by impoundment
    release (Seti) or by river entrainment (Langtang);
  * four advected tracers: total depth h, water hw, release-origin water hwr,
    release-origin solids hr;
  * stranding of slow granular material to the bed.

NEW HERE — ENTRAINMENT (the gap PLAN.md flagged as the next build). Until now
the model could put sediment down and never pick any up, and three independent
observations said so: Seti's measured flow density 1.88 g/cm3 (w~0.47) against
a modelled 0.92; Langtang's distal water ~100% river-derived; and geopera's
stereo DEM showing the Langtang corridor was NET EROSIONAL by ~3.5x (3.2 Mm3
erosion against 0.9 Mm3 deposition in the ~45% they mapped).

Two closures are implemented, both with constants taken from the literature,
because they make different physical claims and the difference is the finding:

  law="takahashi" (default) — CAPACITY-LIMITED. Takahashi's equilibrium
    sediment concentration for a mature debris flow on a bed of internal
    friction angle phi,
        c_eq = rho_w tan(theta) / ((rho_s - rho_w)(tan(phi) - tan(theta)))
    with erosion where the flow runs below capacity and deposition where it
    runs above:
        de/dt = +DELTA_E (c_eq - c)/(c* - c_eq) u      (c < c_eq, erosion)
        de/dt = -DELTA_D (c - c_eq)/c*        u        (c > c_eq, deposition)
    DELTA_E = 0.0007, DELTA_D = 0.05 are Takahashi's own coefficients (the
    values used in Kanako and its descendants). Nothing is fitted: the bed
    slope and the friction angle set the answer.

  law="shear" — SHEAR-DRIVEN, NOT capacity-limited. Frank et al. (2015) found
    maximum erosion depth in Swiss debris-flow channels linear in maximum
    basal shear stress, z_pot = K_TAU (tau_b - tau_c), approached over an
    entrainment time T_ERO. This closure can drive the flow ABOVE the local
    transport capacity, which is what a surge front actually does; it is the
    alternative hypothesis for the Seti density.

Both closures share the bookkeeping, and both are limited by a finite
erodible layer H_ERODE (bedrock gorges do not supply unlimited sediment) and
by a SETTLING CAP on deposition: solids cannot leave the flow faster than
they can fall through it, W_SETTLE * c. That cap is the rate control that
lets a surge stay dense across a reach whose local capacity is near zero —
which is the situation at Kharapani, and the reason an equilibrium closure
alone cannot describe a surge. Grain size enters only there, as an explicit
declared parameter.

The entrained bed is treated as SATURATED, so eroding a bulk volume dE adds
c* dE of solids and (1 - c*) dE of pore water to the flow, and a deposit
carries its pore water back to the bed with it. Entrained material is
tracked separately from release material: the hwr/hr tracers are untouched
by entrainment, so the provenance answer (H1) stays honest.

WHAT IS NOT REPRESENTED: wash load. Takahashi's closure transports bed
material. Real fine sediment rode the Trishuli to India and is outside this
model; "the distal water was the river's own" is a statement about water
provenance, not about clarity.
"""
import math
import numpy as np

G = 9.81

# ---------------------------------------------------------------------------
# FROZEN dial constants. Three published results (Trishuli scenario table,
# Chamoli thermal-lag hindcast, Seti blind hindcast) depend on these values.
# They are not to be retuned to make a new term work.
# ---------------------------------------------------------------------------
MU_WET, W_SAT = 0.02, 0.25
TAU_Y0, RHO_MIX = 400.0, 1800.0   # Bingham yield stress at saturation, Pa;
                                  # mixture density used in tau_y/(rho g h)
U_DEP, T_DEP = 1.0, 120.0         # stranding: slow + granular -> bed
FR_MAX = 2.0


def mu_dry_scheidegger(V_m3):
    """Scheidegger (1973) volume-mobility regression, log H/L = a - b log V."""
    return 10 ** (0.62419 - 0.15666 * math.log10(V_m3))


def mu_of_w(w, h, mu_dry, mu_wet=MU_WET, w_sat=W_SAT):
    """The dilution dial. Below pore saturation the mass is granular and mu
    slides linearly from mu_dry to mu_wet; above it the mass is a slurry whose
    resistance is a fixed yield STRESS, so the equivalent friction falls with
    depth (deep lahars run, thin sheets lock - Pierson & Scott)."""
    lo = mu_dry + (mu_wet - mu_dry) * np.clip(w / w_sat, 0.0, 1.0)
    tau_y = TAU_Y0 * np.clip((1.0 - w) / (1.0 - w_sat), 0.0, 1.0)
    hi = np.minimum(tau_y / (RHO_MIX * G * np.maximum(h, 0.05)), mu_wet)
    return np.where(w <= w_sat, lo, hi)


# ---------------------------------------------------------------------------
# Entrainment constants — literature values, listed so a reader can check them
# ---------------------------------------------------------------------------
RHO_S, RHO_W = 2650.0, 1000.0
TAN_PHI_BED = 0.75      # phi = 37 deg, standard for a coarse alluvial bed
C_STAR = 0.65           # packed bed solids fraction
S_MIN_DF = 0.03         # below this bed slope Takahashi's mature debris-flow
                        # equilibrium does not apply (c_eq -> 0)
DELTA_E = 0.0007        # Takahashi erosion coefficient (Kanako's delta_e)
DELTA_D = 0.05          # Takahashi deposition coefficient (delta_d)
K_TAU = 3.0e-5          # m/Pa, Frank et al. (2015): band 1e-5 to 5e-5
TAU_C = 1000.0          # Pa, critical basal shear for bed entry (~1 kPa)
T_ERO = 60.0            # s, time to reach the potential erosion depth
H_ERODE = 3.0           # m of erodible bed available (see note in the event
                        # scripts; swept, not fitted)
W_SETTLE = 0.025        # m/s, fall velocity of medium sand (~0.25 mm) — the
                        # deposition rate cap


def c_eq_takahashi(S, tan_phi=TAN_PHI_BED, c_star=C_STAR):
    """Equilibrium (capacity) solid volume fraction of a mature debris flow on
    bed slope S = tan(theta). Zero below S_MIN_DF, capped at 0.9 c*."""
    S = np.clip(np.asarray(S, dtype=float), 0.0, tan_phi - 1e-3)
    c = RHO_W * S / ((RHO_S - RHO_W) * (tan_phi - S))
    return np.where(S < S_MIN_DF, 0.0, np.clip(c, 0.0, 0.9 * c_star))


# ---------------------------------------------------------------------------
class Reach:
    """Channel geometry + baseflow for one event. Everything the engine needs
    that is not state."""

    def __init__(self, x_km, z, wn, nn, Qb, side=(), k_junc=None,
                 h_erode=H_ERODE):
        self.x_km = np.asarray(x_km, float)
        self.z = np.asarray(z, float)
        self.N = N = len(self.x_km)
        self.DX = float(np.mean(np.diff(self.x_km))) * 1000.0
        self.wn = np.broadcast_to(np.asarray(wn, float), (N,)).copy()
        self.nn = np.broadcast_to(np.asarray(nn, float), (N,)).copy()
        self.Qb = np.broadcast_to(np.asarray(Qb, float), (N,)).copy()
        self.q_lat = np.zeros(N)
        self.q_lat[1:] = np.diff(self.Qb)
        self.wf = 0.5 * (self.wn[:-1] + self.wn[1:])
        self.nf = 0.5 * (self.nn[:-1] + self.nn[1:])
        self.side = list(side)
        self.side_node = {nm: int(np.argmin(np.abs(self.x_km - km)))
                          for nm, km, *_ in self.side}
        self.K_loc = np.zeros(N - 1)
        for km_j, K in (k_junc or {}).items():
            j = min(int(np.argmin(np.abs(self.x_km - km_j))), N - 2)
            self.K_loc[j] = K
        # bed slope for the entrainment closures (geometry, not state)
        self.S_bed = np.maximum(-np.gradient(self.z, self.x_km * 1000.0), 0.0)
        self.c_eq = c_eq_takahashi(self.S_bed)
        self.h_erode = h_erode

    def new_state(self, h, Qi=None, hs0=0.0):
        h = np.asarray(h, float).copy()
        return dict(h=h, hw=h.copy(), hwr=np.zeros(self.N),
                    hr=np.zeros(self.N),
                    Qi=(0.5 * (self.Qb[:-1] + self.Qb[1:]) if Qi is None
                        else np.asarray(Qi, float).copy()),
                    hs={nm: hs0 for nm, *_ in self.side},
                    bed=np.zeros(self.N), ero=np.zeros(self.N),
                    dep=np.zeros(self.N),
                    avail=np.full(self.N, self.h_erode),
                    umax=np.zeros(self.N - 1))


CD_WEIR = 1.6
H_SIDE_MAX = 8.0        # m cap on side-branch fill (Sentinel-2 stage-volume
                        # curves would replace this)
H_FLOOR = 0.05          # m — numerical wet-film floor on depth


def _floor(h, hw):
    """Apply the wet-film floor as WATER, not as solids.

    h = maximum(h, H_FLOOR) on its own manufactures volume in cells the
    solution wants to drain, and because hw is untouched that manufactured
    volume counts as SOLID. Harmless where the channel is narrow and always
    wet (every published Trishuli/Chamoli run), but on a kilometres-wide
    basin floor it feeds the stranding ledger without limit — the Sabche
    Cirque run reported 53 Mm3 stranded from a 19.8 Mm3 release before this
    was fixed. The film is numerical, so it is water.
    """
    add = np.maximum(H_FLOOR - h, 0.0)
    return h + add, hw + add


def step(st, R, dt, mu_dry, w_sat=W_SAT, mu_wet=MU_WET, side_valleys=True,
         deposit=True, u_dep=U_DEP, t_dep=T_DEP, entrain=None):
    """One explicit step. `entrain` is None (off — bit-identical to the
    published runs) or a dict of closure settings, see entrain_opts()."""
    z, wn, nn, wf, nf, DX, N = R.z, R.wn, R.nn, R.wf, R.nf, R.DX, R.N
    Qb, q_lat, K_loc = R.Qb, R.q_lat, R.K_loc
    h, hw, hwr, hr, Qi = st["h"], st["hw"], st["hwr"], st["hr"], st["Qi"]
    hs, bed = st["hs"], st["bed"]

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
    # convective momentum d(uQ)/dx, first-order upwind — the term whose
    # omission (pure Bates local inertia) confines a dam-break front into a
    # one-cell soliton and releases a Coulomb-parked mass as a coherent wall.
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
    # von Neumann-Richtmyer shock viscosity, discriminating by SHARPNESS
    # (second difference of Q) rather than Froude: smooth waves at any Fr are
    # untouched, single-cell spikes dissipate on the cell-crossing timescale.
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
        for nm, km, area, ww, sill in R.side:
            i = R.side_node[nm]
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

    h = h + dV * dt / (wn * DX)
    hw = hw + dW * dt / (wn * DX)
    hwr = hwr + dWr * dt / (wn * DX)
    hr = hr + dR * dt / (wn * DX)
    h, hw = _floor(h, hw)
    hw = np.clip(hw, 0.0, h)
    hwr = np.clip(hwr, 0.0, hw)
    hr = np.clip(hr, 0.0, h)

    u_node = np.zeros(N)
    u_node[:-1] = np.abs(Qi) / Af
    u_node[1:] = np.maximum(u_node[1:], np.abs(Qi) / Af)

    if deposit:
        # stranding: slow + granular -> solids to bed, water passes
        h_sol = np.maximum(h - hw, 0.0)
        wfrac = hw / np.maximum(h, 1e-6)
        strand = (u_node < u_dep) & (wfrac < w_sat) & (h_sol > 0.02)
        dep = np.where(strand, h_sol * dt / t_dep, 0.0)
        h = h - dep
        hr = np.clip(hr - dep, 0.0, None)
        bed = bed + dep * wn * DX
        h, hw = _floor(h, hw)

    if entrain is not None:
        # NOTE `bed` stays the STRANDING ledger only; entrained/re-deposited
        # bed material is tracked separately in st["ero"]/st["dep"] so the two
        # mechanisms can never be confused in a scorecard.
        h, hw, hwr, hr = _entrain(st, R, dt, h, hw, hwr, hr, u_node, entrain)

    st.update(h=h, hw=hw, hwr=hwr, hr=hr, Qi=Qi, hs=hs, bed=bed)
    st["umax"] = np.maximum(st["umax"], np.abs(Qi) / Af)
    return st


def entrain_opts(law="takahashi", k_tau=K_TAU, tau_c=TAU_C, t_ero=T_ERO,
                 delta_e=DELTA_E, delta_d=DELTA_D, w_settle=W_SETTLE,
                 deposition=True):
    return dict(law=law, k_tau=k_tau, tau_c=tau_c, t_ero=t_ero,
                delta_e=delta_e, delta_d=delta_d, w_settle=w_settle,
                deposition=deposition)


def _entrain(st, R, dt, h, hw, hwr, hr, u_node, opt):
    """Bed exchange. Positive dE = erosion (bed -> flow), negative = deposition
    (flow -> bed). The bed is saturated: a bulk volume dE carries C_STAR solids
    and (1 - C_STAR) pore water."""
    N = R.N
    avail = st["avail"]
    h_sol = np.maximum(h - hw, 0.0)
    c = h_sol / np.maximum(h, 1e-6)                 # solid volume fraction
    moving = (h > 0.10) & (u_node > 0.2)

    if opt["law"] == "takahashi":
        ceq = R.c_eq
        ero_rate = np.where(c < ceq,
                            opt["delta_e"] * (ceq - c)
                            / np.maximum(C_STAR - ceq, 1e-3) * u_node, 0.0)
        dep_rate = np.where(c > ceq,
                            opt["delta_d"] * (c - ceq) / C_STAR * u_node, 0.0)
    else:                                            # shear-driven, Frank 2015
        rho_f = RHO_W + c * (RHO_S - RHO_W)
        S_e = np.zeros(N)
        S_e[:-1] = R.S_bed[:-1]
        tau_b = rho_f * G * np.minimum(h, 50.0) * S_e
        z_pot = opt["k_tau"] * np.maximum(tau_b - opt["tau_c"], 0.0)
        ero_rate = np.maximum(z_pot - st["ero"], 0.0) / opt["t_ero"]
        # deposition still handled by the capacity rule below capacity
        dep_rate = np.where(c > R.c_eq,
                            opt["delta_d"] * (c - R.c_eq) / C_STAR * u_node,
                            0.0)
    if not opt["deposition"]:
        dep_rate = np.zeros(N)

    # SETTLING CAP: solids cannot leave the flow faster than they fall through
    # it. Bulk deposition rate <= W_SETTLE * c / C_STAR. This is what lets a
    # surge cross a low-capacity reach still dense.
    dep_rate = np.minimum(dep_rate, opt["w_settle"] * c / C_STAR)

    dE = np.where(moving, ero_rate * dt, 0.0)
    dE = np.minimum(dE, avail)                       # finite erodible layer
    dE = np.minimum(dE, 0.25 * h)                    # numerical guard
    dD = np.where(moving, dep_rate * dt, 0.0)
    dD = np.minimum(dD, h_sol / max(C_STAR, 1e-6))   # can't drop what's absent
    dD = np.minimum(dD, 0.25 * h)
    net = dE - dD                                    # + = bed lowering

    # apply to the flow
    h = h + net
    hw = hw + net * (1.0 - C_STAR)
    # release tracers ride along with their share of what leaves
    sol_share = np.where(h_sol > 1e-9, hr / np.maximum(h_sol, 1e-9), 0.0)
    wat_share = np.where(hw > 1e-9, hwr / np.maximum(hw, 1e-9), 0.0)
    hr = hr - dD * C_STAR * np.clip(sol_share, 0.0, 1.0)
    hwr = hwr - dD * (1.0 - C_STAR) * np.clip(wat_share, 0.0, 1.0)

    h, hw = _floor(h, hw)
    hw = np.clip(hw, 0.0, h)
    hwr = np.clip(hwr, 0.0, hw)
    hr = np.clip(hr, 0.0, np.maximum(h - hw, 0.0))

    st["avail"] = np.maximum(avail - net, 0.0)
    st["ero"] = st["ero"] + dE
    st["dep"] = st["dep"] + dD
    return h, hw, hwr, hr


def arrival_fn(front, t):
    """First-crossing arrival time, in the units of `t`.

    NOT np.interp: once the front saturates at the last node the front array
    has a long flat tail, and interpolating a value inside a plateau returns a
    point in its middle (it reported Seti's Pokhara arrival as 180 min instead
    of ~100). Interpolate between the two samples that straddle the crossing.
    """
    front = np.asarray(front, float)
    t = np.asarray(t, float)

    def arrival(km):
        idx = np.nonzero(front >= km)[0]
        if len(idx) == 0:
            return float("inf")
        i = int(idx[0])
        if i == 0:
            return float(t[0])
        f0, f1 = front[i - 1], front[i]
        if f1 <= f0:
            return float(t[i])
        return float(t[i - 1] + (km - f0) / (f1 - f0) * (t[i] - t[i - 1]))

    return arrival
