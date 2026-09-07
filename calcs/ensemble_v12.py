#!/usr/bin/env python3
"""
ENSEMBLE v12 — the lower river gets a floodplain that CONVEYS, the arrival is
detected on the water surface, and the video at km 74.8 becomes an observable
(dossier §25, §26b).

WHAT v10b LEFT (§24). One run of 300 passed all eleven observables and failed
every one of the three held-out numbers: 160 Mm3, 4 % water, a stiff slow mass
that reaches Galchhi's depth by crawling and then arrives at Malekhu 42 min
late, at Kalikhola 2.5 h late, and at Devghat with half the peak. The wet runs
do the opposite. In this model a flow is right AT Galchhi or right BELOW it,
never both.

WHY. §25: Dave's video from km 74.8 shows the flood leave a ~150 m gravel
channel and cover a farmed valley floor several hundred metres wide in about
seventy seconds, then STAY there, moving slowly, for at least three more
minutes. The mud-line map has the same event — the fitted stage halves between
km 88 and 90 exactly where the DEM floor opens from ~250 to ~600 m — and the
arXiv reconstruction's twelve corridor transects (median 533 m) are a third
measurement of it. A flood that spreads across a floor like that becomes long,
low and slow at once. A single channel cannot do that, and v11's floor could
not either: it was pure STORAGE, so it took water out of the wave and gave the
wave nothing to move through, which lowered Galchhi and starved Devghat at the
same time (§24's table).

WHAT CHANGES, below km 70 only. Everything above Betrawati is v10.

  1. A REAL COMPOUND SECTION (core.FP_N, new). The floor now conveys with its
     own roughness: flow area and conveyance are summed over channel and floor,
     K = sum_i (A_i / n_i) y_i^(2/3), and the friction slope is Q|Q|/K^2. In
     the single-channel limit this reduces exactly to Manning, so FP_N = None
     is bit-identical (checked against the v10 wet and dry near-misses before
     this was written). The Froude cap and the Voellmy term move onto the
     hydraulic mean depth A/W_top, which is what they want once the section is
     not a rectangle.

  2. GEOMETRY FROM THE DEM, AGGREGATED BY MEAN NOT MEDIAN. The inner channel
     is W_top_5 — the DEM section width 5 m above the bed, i.e. bank-full — and
     the floor is sized so the compound section reproduces the section's
     MEASURED area at +20 m:

         A20  = 5 W5 + 5 (W5+W10)/2 + 10 (W10+W20)/2      (trapezoid)
         W_fp = f_fp * max(A20 - 20 W_ch, 0) / (20 - hb)

     so that at f_fp = 1 the two-part section holds exactly what the DEM says
     the valley holds at +20 m, whatever bank height is drawn. hb then moves
     only the TIMING of engagement, not the storage — which is the thing the
     video actually measures. v11 aggregated the DEM stations to model cells by
     running MEDIAN, which suppressed precisely the wide basins that matter
     (km 73.5 is 496 m at +5 m between neighbours at 96 and 48). Storage and
     conveyance add along a reach, so the volumetrically correct aggregator is
     the MEAN over the cell, and that is what this uses. Stated because it is a
     real choice and it moves the answer.

     The trapezoid over-reads the DEM's own area at the fitted stage by a
     median 14 % (p10 1.01, p90 1.47) because real sections are V-shaped, not
     stepped; f_fp 0.5-2.0 carries that and more. f_fp = 2.5 would reproduce
     the naive W_top_20 - W_top_5 floor of the §25 sketch, which over-states
     the measured area by about half.

  3. THE ARRIVAL IS DETECTED ON THE TRUE STAGE (model/unified.py). h is the
     volume-equivalent depth over the main channel; where the floor is engaged
     the water surface is well below it. Every version to v11 detected the
     front on h — a depth nobody could see. This is the tooling bug §25 named,
     and it is why v11's +5 m test reported "front detection failed".

  4. THE BANK CANNOT BE UNDER THE RIVER. hb is sampled 3-8 m and applied as
     max(hb, SETTLED depth + 0.5) per node, so the floor is dry at baseflow
     everywhere and the compound system reduces exactly to the channel one at
     t = 0. The river is settled with the floor OFF and the bank set from that
     state, which is why widths() and floor() are separate. A first build used
     the ANALYTIC normal depth instead; the relaxed depth is higher wherever
     the DEM channel is narrow and the slope small, and 90 of the 324 nodes
     below km 70 — the Galchhi window among them — came out with baseflow
     already on the floodplain, putting floodplain water into the datum every
     stage observable is measured above (stage_galchhi over-read by up to
     2.9 m). Caught by checking before the ensemble ran. core.FP_HB now takes
     a per-node array.

  5. TWO NEW OBSERVABLES FROM THE VIDEO (§25 addendum). Dave located the
     CAMERA at 27 55'40.33"N 85 08'54.45"E = km 74.8, west bank, 44 m above
     the river, looking NNE. The floor that goes under in the frames is not
     the ground under the camera — it is the ground the camera is looking AT,
     700 m and 1.3 km up-valley on bearings 30 and 39 degrees, which §25's own
     table names as km 73.5 (496 m wide at +5 m, 720 at +20) and km 74.0
     (1,016 m at +20). At the camera's own node the DEM floor is narrow
     (cell-mean 72 m at +5 m), so scoring the rise there would score the wrong
     ground. The rise is scored at km 73.6 and the camera's node is recorded.
     Only what the frames actually establish is scored:
       rise74_s      seconds from the front reaching km 73.6 to the stage
                     passing +5 m there — the floor going under. Video ~70 s
                     (front ~30 s, floor covered ~100 s); scored 20-180 s,
                     which is wide because the clip is 640x360 and its
                     continuity is unconfirmed.
       hold74_m      stage at 260 s after the front — the flow is still over
                     the floor at the end of the clip, not drained. Scored
                     >= 5 m.
     Three readings are REPORTED AND NOT SCORED, because they are inferences
     rather than things the frames show: the depth at four minutes (~10-15 m),
     the stage at the camera's node (the clip ends with the water well below
     the camera, i.e. under 44 m — a weak bound), and the front speed at
     km 73-75 (>= 30 m/s against the model's ~11). A camera 44 m up cannot
     read a 12 m stage, and the front's first appearance up-valley is judged
     by eye. They go in the diagnostics column and they are the reason to go
     back to the clip with Dave.

  6. THE FFD VOLUME, AS A SHAPE OBSERVABLE (§26b). The 27 August release says
     ~2 crore m3 above base flow at Devghat between 14:10 and 18:00 — a
     windowed gross excess at one gauge, one significant figure, preliminary.
     It is NOT a volume balance on the release and it is not scored as one.
     What it fixes is the AREA under the excess hydrograph over a stated
     window, and every version so far has been scored on the HEIGHT of the
     Devghat peak and never on its WIDTH — which is exactly what a floodplain
     changes. Reported with the held-out set as devghat_vol, integrated
     333-563 min after 08:37, target ~20 Mm3 at one significant figure.

Thirteen scored observables (v10's eleven plus rise74_s and hold74_m) and
fourteen inputs. Run over the v10b stage-2 box by default, with the three new
inputs at their full range, and reported as what it is: a stage-2 posterior
conditional on stage 1, thin at ~1.6 samples per dimension per octave.

Run:  .venv/bin/python calcs/ensemble_v12.py [n_samples]
      TRISHULI_V12_BOX=stage1  to use v10's untruncated prior instead.
Writes calcs/ensemble_samples_v12.npy and output/ensemble_v12_RESULTS.md.
"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "model")); sys.path.insert(0, HERE)
import core
import unified as U
import ensemble_v6 as V6
import ensemble_v8 as V8
import ensemble_v10 as V10
import ensemble_v10b as V10B

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
KM_FP = 70.0            # the compound section starts below Betrawati
# THE VIDEO. Dave located the CAMERA at km 74.8 (27 55'40.33"N 85 08'54.45"E,
# west bank, 44 m up, looking NNE). The FLOOR that goes under in the frames is
# not under the camera — it is the ground the camera is looking AT, up-valley:
# §25's own table names km 73.5 (496 m wide at +5 m, 720 at +20) and km 74.0
# (1,016 m at +20), 700 m and 1.3 km away on bearings 30° and 39°. At the
# camera's own node the DEM floor is narrow (cell-mean 72 m at +5 m). So the
# rise curve is SCORED at the model node covering that floor and the camera's
# node is recorded alongside it.
KM_VID = 73.6           # the wide floor in frame — scored
KM_CAM = 74.8           # the camera — recorded, not scored
T_VID_RISE = (20.0, 180.0)      # s, front -> floor under (+5 m). Video ~70
T_VID_HOLD = 260.0              # s after the front — end of the clip
H_VID_FLOOR = 5.0               # m, the DEM floor level at km 73.5-74
H_VID_HOLD = 5.0                # m, still over the floor at 260 s
# FFD 27 Aug: ~2 crore m3 above base at Devghat, 14:10-18:00 NPT (event 08:37)
FFD_WINDOW_MIN = (333.0, 563.0)
FFD_VOL_MM3 = 20.0

_BOX = os.environ.get("TRISHULI_V12_BOX", "stage2")
PRIORS = dict(V10.PRIORS if _BOX == "stage1" else V10B.BOX)
PRIORS["f_fp"] = ("log", 0.5, 2.0)      # floor width vs the measured A20
PRIORS["h_bank"] = ("lin", 3.0, 8.0)    # bank height, m above bed
PRIORS["n_fp"] = ("lin", 0.06, 0.12)    # floodplain Manning n: fields, trees
KEYS = V6.KEYS + ["rise74_s", "hold74_m"]
EXTRA = ["deposit_bulk_Mm3", "stage74_4min_m", "stage_cam_m",
         "v_front_lower"]
_geom_cache = {}
_trapz = getattr(np, "trapezoid", None) or np.trapz   # numpy 2 renamed it
U.EXTRA_STATIONS["video"] = KM_VID     # the floor that floods, scored
U.EXTRA_STATIONS["camera"] = KM_CAM    # the camera, recorded


def draw(n):
    """Latin hypercube over THIS module's priors (V10.draw reads its own)."""
    import ensemble as E
    U01 = E.latin_hypercube(n, len(PRIORS)); out = {}
    for j, (name, (kind, lo, hi)) in enumerate(PRIORS.items()):
        u = U01[:, j]
        out[name] = (np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
                     if kind == "log" else lo + u * (hi - lo))
    return out


# ------------------------------------------------------- the DEM section ----
def cell_section():
    """Per-model-node channel width and area-to-+20 m, aggregated by MEAN over
    the DEM stations inside each 400 m cell (see docstring §2)."""
    if "s" in _geom_cache:
        return _geom_cache["s"]
    rows = list(csv.DictReader(open(os.path.join(ROOT, "output",
                                                 "lowerriver_widths.csv"))))
    km = np.array([float(r["km"]) for r in rows])
    W5 = np.array([float(r["W_top_5"]) for r in rows])
    W10 = np.array([float(r["W_top_10"]) for r in rows])
    W20 = np.array([float(r["W_top_20"]) for r in rows])
    A20 = 5 * W5 + 5 * (W5 + W10) / 2 + 10 * (W10 + W20) / 2
    half = 0.5 * U.DX / 1000.0
    wch = np.zeros_like(U.x_km); a20 = np.zeros_like(U.x_km)
    for j, x in enumerate(U.x_km):
        m = (km >= x - half) & (km < x + half)
        if not m.any():                      # outside the DEM strip: nearest
            m = np.abs(km - x) <= half * 3
        if not m.any():
            continue
        wch[j] = W5[m].mean(); a20[j] = A20[m].mean()
    _geom_cache["s"] = (wch, a20)
    return wch, a20


def widths(p, base):
    """Main-channel width for one run. Independent of the bank height, which
    is what lets the settled river be found before the floor is switched on."""
    wch, _ = cell_section()
    x = U.x_km; m = (x >= KM_FP) & (wch > 0)
    w = V8.widths_for(p["f_wl"], base)               # v6/v8 above Betrawati
    w[m] = np.clip(wch[m], 20.0, 800.0)
    return w, m


def floor(p, w, m, h_settled):
    """Floor width and per-node bank height, given the SETTLED river depth.

    THE BANK CANNOT BE UNDER THE RIVER. A first build took the bank as
    max(h_bank, analytic normal depth + 0.5); the relaxed settled depth is
    higher than the analytic estimate wherever the DEM channel is narrow and
    the local slope small, and 90 of the 324 nodes below km 70 — the Galchhi
    window among them — came out with baseflow already ON the floodplain. That
    puts floodplain water in the datum h0 that every stage observable is
    measured above, so stage_galchhi was over-read by up to 2.9 m. Caught by
    checking, before the ensemble ran. The bank is now set from the settled
    state itself.
    """
    hb = np.clip(np.maximum(np.full_like(U.x_km, float(p["h_bank"])),
                            h_settled + 0.5), 0.5, 15.0)
    fpw = np.zeros_like(U.x_km)
    _, a20 = cell_section()
    fpw[m] = p["f_fp"] * np.clip((a20[m] - 20.0 * w[m]) / (20.0 - hb[m]),
                                 0.0, 4000.0)
    return fpw, hb


# ------------------------------------------------------------- one run ------
def _simulate(p, t_end):
    w, m = widths(p, V10.BASE)
    U.set_widths(w)
    U.R.nn = U.R.nn * p["n_scale"]; U.R.nf = 0.5 * (U.R.nn[:-1] + U.R.nn[1:])
    U.R.h_erode = p["h_erode"]; U._settled.clear()
    # SETTLE THE RIVER IN ITS CHANNEL FIRST, floor off, then set the bank above
    # what settled and switch the floor on. At baseflow the floor is then dry
    # by construction, so the compound system reduces exactly to the channel
    # one and this initial state is a true equilibrium of it. U.simulate()
    # re-reads the cached settled state, so the settling is not repeated.
    core.FP_W = None; core.FP_HB = None; core.FP_N = None
    h_settled = U.settled_state()["h"]
    fpw, hb = floor(p, w, m, h_settled)
    core.FP_W = fpw; core.FP_HB = hb; core.FP_N = float(p["n_fp"])
    core.XI = float(p["xi"]); core.XI_COMP = True
    U.R.K_loc[V10.V7.J22] = float(p["k_junc"])
    return U.simulate(V_rel=p["V_rel"], w0=p["w0"], mu_dry=p["mu_dry"],
                      t_end=t_end, T_rel=p["T_rel"],
                      f_fine_rel=p.get("f_fine", 0.0),
                      entrain=core.entrain_opts("takahashi", f_fine=0.30))


def _restore(nn0, k0):
    core.FP_W = None; core.FP_HB = None; core.FP_N = None
    V10._restore(nn0, k0); U.set_widths(V10.BASE); U._settled.clear()


def video_obs(r):
    """The rise curve on the floor in frame (§25). r['video']['y'] is the
    water surface above the settled river there, sampled every 10 s."""
    t = r["t"] * 60.0                                   # min -> s
    y = np.asarray(r["video"]["y"], float)
    t_front = r["arrival"](KM_VID) * 60.0
    out = {"rise74_s": float("inf"), "hold74_m": 0.0,
           "stage74_4min_m": 0.0, "stage_cam_m": 0.0}
    if not np.isfinite(t_front):
        return out
    over = np.nonzero((t >= t_front) & (y >= H_VID_FLOOR))[0]
    if len(over):
        out["rise74_s"] = float(t[over[0]] - t_front)
    for key, dt_s in (("hold74_m", T_VID_HOLD), ("stage74_4min_m", 240.0)):
        k = np.searchsorted(t, t_front + dt_s)
        if k < len(y):
            out[key] = float(y[k])
    yc = np.asarray(r["camera"]["y"], float)          # the camera's own node
    k = np.searchsorted(t, t_front + T_VID_HOLD)
    out["stage_cam_m"] = float(yc[k]) if k < len(yc) else 0.0
    return out


def front_speed_lower(r, a=73.0, b=75.0):
    """Diagnostic only: mean front speed over km 73-75, against the video's
    >= 30 m/s. Not scored — see the docstring."""
    ta, tb = r["arrival"](a), r["arrival"](b)
    if not (np.isfinite(ta) and np.isfinite(tb)) or tb <= ta:
        return 0.0
    return float((b - a) * 1000.0 / ((tb - ta) * 60.0))


def observables(r, p):
    o = V10.observables(r, p)
    o.update(video_obs(r))
    o["v_front_lower"] = front_speed_lower(r)
    return o


def score(o):
    ok = V6.score(o)
    ok["rise74_s"] = bool(T_VID_RISE[0] <= o["rise74_s"] <= T_VID_RISE[1])
    ok["hold74_m"] = bool(np.isfinite(o["hold74_m"])
                          and o["hold74_m"] >= H_VID_HOLD)
    return ok


def run(p, t_end=None):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V10.V7.J22])
    try:
        return observables(_simulate(p, t_end or V6.T_END), p)
    except Exception as e:
        print(f"    run failed: {e}"); return None
    finally:
        _restore(nn0, k0)


def held_out(p):
    nn0 = U.R.nn.copy(); k0 = float(U.R.K_loc[V10.V7.J22])
    try:
        r = _simulate(p, 10 * 3600.0)
        q = np.asarray(r["Devghat"]["q"], float); tt = np.asarray(r["t"], float)
        i = int(np.argmax(np.where(tt > 30, q, -1)))
        m = (tt >= FFD_WINDOW_MIN[0]) & (tt <= FFD_WINDOW_MIN[1])
        qb = float(np.median(q[tt < 30])) if (tt < 30).any() else 0.0
        vol = (float(_trapz(np.maximum(q[m] - qb, 0.0), tt[m] * 60.0)) / 1e6
               if m.sum() > 1 else 0.0)
        return (f"Malekhu {r['arrival'](117.0):.0f} (163) / "
                f"Kalikhola {r['arrival'](185.0):.0f} (~337) / "
                f"Devghat {q[i]:,.0f} m³/s at {tt[i]:.0f} min (~2,900) / "
                f"vol {vol:.1f} Mm³ (~{FFD_VOL_MM3:.0f})")
    except Exception as e:
        return f"failed: {e}"
    finally:
        _restore(nn0, k0)


def fmt_p(p):
    return (f"{p['V_rel']/1e6:.1f} | {p['w0']:.2f} | {p['mu_dry']:.3f} | "
            f"{p['f_fine']:.2f} | {p['xi']:.0f} | {p['k_junc']:.1f} | "
            f"{p['f_wl']:.2f} | {p['f_ice']:.2f} | {p['T_rel']:.0f} | "
            f"{p['f_fp']:.2f} | {p['h_bank']:.1f} | {p['n_fp']:.3f}")


# ------------------------------------------------------------ reporting ----
COLS = ("V Mm3 | w0 | mu | f_fine | xi | k_junc | f_wl | f_ice | T_rel s | "
        "f_fp | h_bank | n_fp")


def main(N, tag="v12"):
    lines = []; P_ = lambda s="": (print(s, flush=True), lines.append(s))
    old, V10.BASE = V6.apply_v6_geometry()
    P_("# Ensemble v12 — a floodplain that conveys, the arrival on the true "
       "stage, and the video at km 74.8 (dossier §25, §26b)\n")
    P_(f"{N} Latin-hypercube samples over {len(PRIORS)} inputs "
       f"({'stage-1 prior' if _BOX == 'stage1' else 'v10b stage-2 box, three new inputs at full range'}): "
       + "; ".join(f"{k} {kind} {lo:g}–{hi:g}"
                   for k, (kind, lo, hi) in PRIORS.items())
       + f". v10 physics above km {KM_FP:.0f}; compound section below it; "
         f"T_END {V6.T_END/3600:.2f} h; deposition scored ROCK-ONLY.\n")
    P_("| observable | target | tolerance / bounds |"); P_("|---|---|---|")
    for k, (v, t, lab) in V6.OBS.items(): P_(f"| {lab} | {v} | ±{100*t:.0f}% |")
    for k, (lo, hi, med, n) in V6.OBS_BOUNDS.items():
        P_(f"| {k} (fit median {med:.1f}) | — | {lo:.1f}–{hi:.1f} m |")
    P_("| rock-only bulk deposition km 0-199, Mm3 | — | ≤ 12.0 |")
    P_(f"| **rise74_s** — km {KM_VID}, front → stage +{H_VID_FLOOR:.0f} m (video ~70 s) | ~70 s | "
       f"{T_VID_RISE[0]:.0f}–{T_VID_RISE[1]:.0f} s |")
    P_(f"| **hold74_m** — km {KM_VID}, stage {T_VID_HOLD:.0f} s after the front | still over the floor | "
       f"≥ {H_VID_HOLD:.0f} m |")
    P_(f"\nReported, NOT scored: stage74_4min_m (video ~10–15 m — a camera 44 m "
       f"up cannot read a 12 m stage); stage_cam_m, the stage at the camera's "
       f"own node km {KM_CAM} at {T_VID_HOLD:.0f} s (the clip ends with the water "
       f"well below the camera, i.e. under 44 m); and v_front_lower, the front "
       f"over km 73–75 (video ≥ 30 m/s, model ~11 — the front's first appearance "
       f"is judged by eye at 640×360 and the clip's continuity is "
       f"unconfirmed).\n")
    P_(f"FFD volume (§26b), reported with the held-out set: excess above base "
       f"at Devghat over {FFD_WINDOW_MIN[0]:.0f}–{FFD_WINDOW_MIN[1]:.0f} min "
       f"(14:10–18:00 NPT), target ~{FFD_VOL_MM3:.0f} Mm³ at ONE significant "
       f"figure. A windowed gross excess at one gauge, not a volume balance.\n")
    P = draw(N); import time, itertools; t0 = time.time(); rows = []
    for i in range(N):
        p = {k: float(v[i]) for k, v in P.items()}
        o = run(p)
        if o is None: continue
        ok = score(o); rows.append((p, o, ok, sum(ok.values())))
        if (i + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  {i+1}/{N}  ({el/(i+1):.1f} s/run, {el/60:.1f} min, "
                  f"{sum(1 for r in rows if r[3] == len(KEYS))} full matches)",
                  flush=True)
    full = [r for r in rows if r[3] == len(KEYS)]
    P_(f"\n## Result: {len(rows)} runs, **{len(full)} satisfy all {len(KEYS)} observables**\n")
    P_("| observable | met by |"); P_("|---|---|")
    for k in KEYS: P_(f"| {k} | {sum(1 for r in rows if r[2][k])} / {len(rows)} |")
    if not full:
        P_("\nNo sample satisfies everything. Pairs:\n")
        P_("| pair | runs meeting both |"); P_("|---|---|")
        for a, b in itertools.combinations(KEYS, 2):
            P_(f"| {a} + {b} | {sum(1 for r in rows if r[2][a] and r[2][b])} |")
    best = sorted(rows, key=lambda r: -r[3])[:12]
    P_("\nBest runs (most observables met):\n")
    P_(f"| {COLS} | met | border min | v_gorge | gorge m | syabru m | hakubesi m | "
       "galchhi m | rise74 s | hold74 m | dep rock | dep bulk | ero | "
       "[y@4min] | [y@cam] | [v front 73-75] | failed |")
    P_("|" + "---|" * 25)
    for p, o, ok, n in best:
        P_(f"| {fmt_p(p)} | {n} | {o['border_min']:.1f} | {o['v_gorge']:.0f} | "
           f"{o['stage_gorge']:.0f} | {o['stage_syabru']:.0f} | "
           f"{o['stage_hakubesi']:.0f} | {o['stage_galchhi']:.1f} | "
           f"{o['rise74_s']:.0f} | {o['hold74_m']:.1f} | "
           f"{o['deposit_Mm3']:.1f} | {o['deposit_bulk_Mm3']:.1f} | "
           f"{o['erosion_Mm3']:.1f} | {o['stage74_4min_m']:.1f} | "
           f"{o['stage_cam_m']:.1f} | {o['v_front_lower']:.0f} | {', '.join(k for k in KEYS if not ok[k])} |")
    if full:
        P_("\n## Posterior (passing runs)\n"); P_("| input | median | range |")
        P_("|---|---|---|")
        for key in PRIORS:
            arr = np.array([r[0][key] for r in full]) * (1e-6 if key == "V_rel" else 1)
            P_(f"| {key}{' Mm3' if key == 'V_rel' else ''} | {np.median(arr):.3g} | "
               f"{arr.min():.3g} – {arr.max():.3g} |")
    P_("\n## Held out (10 h): passing runs, then the nearest misses\n")
    P_(f"| {COLS} | met | Malekhu (163) / Kalikhola (~337) / Devghat (~2,900) / vol (~20 Mm³) |")
    P_("|" + "---|" * 14)
    for p, o, ok, n in (sorted(full, key=lambda r: r[0]["V_rel"])
                        + [r for r in best if r[3] < len(KEYS)][:3]):
        P_(f"| {fmt_p(p)} | {n} | {held_out(p)} |")
    np.save(os.path.join(HERE, f"ensemble_samples_{tag}.npy"),
            np.array([[r[0][k] for k in PRIORS] + [r[1][k] for k in KEYS]
                      + [r[1][k] for k in EXTRA] + [r[3]] for r in rows]))
    open(os.path.join(ROOT, "output", f"ensemble_{tag}_RESULTS.md"),
         "w").write("\n".join(lines) + "\n")
    print(f"\nsaved calcs/ensemble_samples_{tag}.npy and "
          f"output/ensemble_{tag}_RESULTS.md ({(time.time()-t0)/60:.0f} min)")


if __name__ == "__main__":
    main(N)
