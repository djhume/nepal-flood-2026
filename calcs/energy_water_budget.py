#!/usr/bin/env python3
"""
First-order energy and water budget for the 26 Aug 2026 Langtang Lirung
avalanche -> Lende Khola / Trishuli flood.

Question being tested (Dave's hypothesis): was the flood water mostly
*entrained river water* swept up by the debris wave, rather than melted
glacier ice (frictional melt), as the standard Chamoli-style narrative says?

Method: bound each candidate water source independently:
  A. Frictional melt of avalanche ice  (limited by BOTH available ice mass
     and available potential energy along the runout)
  B. Standing river water in the channel ahead of the wave (swept up)
  C. River inflow during the event duration
  D. Pore water in entrained saturated channel sediment
All numbers are scenario ranges because source-volume estimates are soft.
"""

G = 9.81          # m/s^2
LF = 3.34e5       # J/kg latent heat of fusion of ice
RHO_ROCK = 2700.0 # kg/m^3
RHO_ICE = 900.0   # kg/m^3
RHO_W = 1000.0    # kg/m^3

def scenario(name, V_total_Mm3, ice_frac, drop_total_m, heat_to_ice_frac,
             channel_km, Q_river, v_river, event_hours,
             sed_entrain_Mm3, sed_porosity, sed_saturation):
    V = V_total_Mm3 * 1e6
    V_ice, V_rock = V * ice_frac, V * (1 - ice_frac)
    m_ice, m_rock = V_ice * RHO_ICE, V_rock * RHO_ROCK
    m_total = m_ice + m_rock

    # --- A. frictional melt ---
    E_pot = m_total * G * drop_total_m           # J released over full runout
    E_to_melt = E_pot * heat_to_ice_frac         # share of heat that melts ice
    m_melt_energy_limited = E_to_melt / LF
    m_melt = min(m_melt_energy_limited, m_ice)   # can't melt more ice than exists
    W_melt = m_melt / RHO_W                      # m^3 of meltwater

    # --- B. standing water in channel (wave sweeps it all up) ---
    A_flow = Q_river / v_river                   # wetted cross-section, m^2
    W_channel = A_flow * channel_km * 1e3

    # --- C. inflow during event ---
    W_inflow = Q_river * event_hours * 3600

    # --- D. pore water in entrained sediment ---
    W_pore = sed_entrain_Mm3 * 1e6 * sed_porosity * sed_saturation

    W_total = W_melt + W_channel + W_inflow + W_pore
    print(f"\n=== {name} ===")
    print(f"  source volume {V_total_Mm3:.0f} Mm3, ice fraction {ice_frac:.0%},"
          f" total drop {drop_total_m:.0f} m")
    print(f"  potential energy released: {E_pot:.2e} J")
    print(f"  ice melt:   energy-limited {m_melt_energy_limited/RHO_W/1e6:6.1f} Mm3,"
          f" ice-limited {m_ice/RHO_W/1e6:6.1f} Mm3"
          f"  -> melt water {W_melt/1e6:6.1f} Mm3 ({W_melt/W_total:5.1%})")
    print(f"  channel standing water ({channel_km:.0f} km @ A={A_flow:.0f} m2):"
          f"       {W_channel/1e6:6.1f} Mm3 ({W_channel/W_total:5.1%})")
    print(f"  river inflow during {event_hours:.1f} h @ {Q_river:.0f} m3/s:"
          f"          {W_inflow/1e6:6.1f} Mm3 ({W_inflow/W_total:5.1%})")
    print(f"  sediment pore water:                        "
          f" {W_pore/1e6:6.1f} Mm3 ({W_pore/W_total:5.1%})")
    print(f"  TOTAL WATER: {W_total/1e6:.1f} Mm3"
          f"   | river-derived (B+C): {(W_channel+W_inflow)/W_total:.1%}")

# Validation: Chamoli 2021 (Shugar et al. 2021 Science). 26.9 Mm3, 80:20
# rock:ice by volume, ~3400 m drop, near-complete melt of ~5-6 Mm3 ice ->
# ~5 Mm3 water. Their energy balance implies ~80% of dissipated heat entered
# the ice ("almost exactly the critical value required for near-complete
# melting"). River terms near-zero: winter low flow, 26 km runout.
scenario("0. VALIDATION Chamoli 2021 (expect ~5 Mm3 melt, ice-limited)",
         V_total_Mm3=26.9, ice_frac=0.20, drop_total_m=3400,
         heat_to_ice_frac=0.80,
         channel_km=26, Q_river=30, v_river=2.0, event_hours=0.5,
         sed_entrain_Mm3=2, sed_porosity=0.3, sed_saturation=0.5)

# Shared geometry assumptions (to be refined from research):
# source ~5200 m -> initial impact ~4000 m -> Rasuwagadhi ~1800 m -> Betrawati ~600 m
# runout considered: ~100 km of channel

# Scenario 1: Wikipedia-large, ice-rich "glacier collapse"
scenario("1. Large ice-rich collapse (150 Mm3, 70% ice)",
         V_total_Mm3=150, ice_frac=0.70, drop_total_m=3500,
         heat_to_ice_frac=0.30,      # much heat goes to rock/bed/water, not melting
         channel_km=100, Q_river=400, v_river=3.0, event_hours=2.0,
         sed_entrain_Mm3=20, sed_porosity=0.3, sed_saturation=0.9)

# Scenario 2: Chamoli-style rock-dominated (80% rock / 20% ice), smaller mass
scenario("2. Rock-dominated Chamoli analogue (40 Mm3, 20% ice)",
         V_total_Mm3=40, ice_frac=0.20, drop_total_m=3500,
         heat_to_ice_frac=0.20,
         channel_km=100, Q_river=400, v_river=3.0, event_hours=2.0,
         sed_entrain_Mm3=20, sed_porosity=0.3, sed_saturation=0.9)

# Scenario 3: Small trigger, monsoon-high river (Dave's picture)
scenario("3. Modest trigger, big wet channel (30 Mm3, 40% ice, Q=600)",
         V_total_Mm3=30, ice_frac=0.40, drop_total_m=3500,
         heat_to_ice_frac=0.25,
         channel_km=100, Q_river=600, v_river=3.0, event_hours=3.0,
         sed_entrain_Mm3=30, sed_porosity=0.3, sed_saturation=1.0)

# Scenario 5: Best current evidence (2 Sept 2026): ~100 Mm3 source (Kargel
# 50-200, Azam 100-200), ice fraction unknown -> 30%, scar-to-channel drop
# ~2,400 m, full 168 km to Devghat, monsoon Q ~400 m3/s, ~7 h transit.
# Compare against FFD's ~20 Mm3 "excess" — NOTE: redistributed channel water
# is gross surge but nets to ~zero over a long gauge integration (channel
# refills from baseflow); NEW water = melt + pore (+ any lake). See PLAN.md.
scenario("5. Best-evidence (100 Mm3, 30% ice, 168 km to Devghat)",
         V_total_Mm3=100, ice_frac=0.30, drop_total_m=2400,
         heat_to_ice_frac=0.35,
         channel_km=168, Q_river=400, v_river=3.0, event_hours=7.0,
         sed_entrain_Mm3=30, sed_porosity=0.3, sed_saturation=1.0)

# Scenario 4: Everything maximal for melt (steel-man the Kargel view)
scenario("4. Melt-maximal (200 Mm3, 80% ice, generous heat partition)",
         V_total_Mm3=200, ice_frac=0.80, drop_total_m=4000,
         heat_to_ice_frac=0.50,
         channel_km=100, Q_river=300, v_river=3.0, event_hours=1.5,
         sed_entrain_Mm3=10, sed_porosity=0.3, sed_saturation=0.8)
