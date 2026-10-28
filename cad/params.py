"""BinBot parameters (mm). Single source of truth for 3D model, drawings and video.

Axes: x = forward (travel), y = left, z = up. Origin = ground, machine centre.
Values marked VENDOR are assumptions until the undercarriage drawing arrives.

Rev C layout rules (farmer feedback):
  * The bought base (tracks, motors, motor controllers, battery, base electronics)
    is NOT modified. Everything we build is a TOP MODULE bolted onto its top.
  * No low bumpers (rocks). Nothing of ours hangs below the base top.
  * Robot drives UNDER bins standing on base stands: nothing at the front may be
    taller than the bin-pass envelope; tall parts (E-box, masts) only at the rear.
"""

# --- Base / undercarriage (bought, not modified) — VENDOR ---
TRACK_OUTER_W = 1200
TRACK_W = 250
TRACK_LEN = 1700
TRACK_H = 400
TRACK_CONTACT = TRACK_LEN - TRACK_H            # 1300 flat on ground
TRACK_Y = TRACK_OUTER_W / 2 - TRACK_W / 2      # 475 track centre line
TRACK_INNER_Y = TRACK_OUTER_W / 2 - TRACK_W    # 350 inner face
BASE_CLEARANCE = 250                           # under the base's centre body (whatever the seller ships)
BASE_BODY = (1300, 680, 190)                   # x, y, z centre body between tracks: battery + controllers
BASE_TOP = 450                                 # flat top / mounting surface of the base
BASE_PLATE = (1300, 1200, 10)                  # top mounting plate, x, y, z (z top = BASE_TOP)

# --- Top frame (weldment, bolts down onto the base top) ---
RHS_H, RHS_B, RHS_T = 100, 50, 4               # RHS 100x50x4 standing
FRAME_LEN = 1300
RAIL_Y = 300
BRK_T, BRK_L, BRK_W = 10, 150, 100            # base plates under the rails (x, y, thickness)
FRAME_Z0 = BASE_TOP + BRK_T                    # 460 underside of rails
FRAME_Z1 = FRAME_Z0 + RHS_H                    # 560 top of rails
END_BEAM_X = FRAME_LEN / 2 - RHS_B / 2         # 625
INNER_BEAM_X = 300
BEAM_LEN = 2 * (RAIL_Y - RHS_B / 2)            # 550
BAY_X0 = INNER_BEAM_X + RHS_B / 2              # 325 end bay inner end (lift links)
BAY_X1 = END_BEAM_X - RHS_B / 2                # 600 end bay outer end

# base plates: welded under the rails, 4 x M16 down into the base top (drill to match)
BRK_X = 450
BRK_HOLE, BRK_PITCH_X, BRK_PITCH_Y = 18, 100, 60

# tabs on the end beams: front = sensor bar, rear = E-box
TAB_T, TAB_W, TAB_H, TAB_Y, TAB_HOLE = 8, 100, 80, 200, 14

# Battery, motor controllers, brakes: inside the bought base (not ours).

# --- Lift (BP-02): parallelogram links each side, 1 actuator per side ---
LIFT_BAR = (1200, 60, 40)                      # RHS 60x40 lift bar on each rail
LIFT_GAP = 5
LIFT_STROKE = 100
LINK_L = 200                                   # link length (pivot centres)
LINK_X = 450                                   # links at x = +-450
CELL = (130, 40, 40)                           # load cell incl. mount
CELL_X = 500
DECK_LX, DECK_LY, DECK_H = 1200, 840, 50       # deck narrower than bin: fits between stand ledges
LIFT_BAR_Z0 = FRAME_Z1 + LIFT_GAP              # 565
DECK_Z0_LOW = LIFT_BAR_Z0 + LIFT_BAR[2] + CELL[2]   # 645
DECK_TOP_LOW = DECK_Z0_LOW + DECK_H            # 695
DECK_TOP_HIGH = DECK_TOP_LOW + LIFT_STROKE     # 795

# --- Bin ---
BIN = (1200, 1000, 760)
BIN_WALL = 30

# --- Base stand ("bay"), robot drives under it (DWG-003) ---
LEDGE_TOP = DECK_TOP_LOW + 50                  # 745: 50 above deck low, 50 below deck high
LEDGE = (1300, 100, 50)                        # RHS 100x50 laid flat, along x
LEDGE_Y0 = DECK_LY / 2 + 35                    # 455 inner edge (35 mm side gap to deck)
POST = 80                                      # SHS 80x80x4
POST_Y = TRACK_OUTER_W / 2 + 80 + POST / 2     # 720: 80 mm gap to the tracks
POST_X = LEDGE[0] / 2 - POST / 2               # 610
GUIDE = (2000, 60, 120)                        # track entry guides on the ground
GUIDE_FLARE = 150                              # funnel opening each side

# --- Electronics & sensors (BP-04 / BP-05) ---
EBOX = (200, 500, 500)                         # depth x width x height (no motor controllers inside)
EBOX_X0 = -(FRAME_LEN / 2 + 10)                # -660 face toward the robot
EBOX_Z0 = FRAME_Z0                              # 460
FRONT_BAR = (40, 700, 40)                      # front sensor bar RHS 40x40 across
FRONT_BAR_X0 = FRAME_LEN / 2 + TAB_T + 10      # 668
FRONT_BAR_Z0 = FRAME_Z0                        # 460
LIDAR = (65, 65, 60)
CAM = (60, 60, 60)
ESTOP_BOX = 70
EDGE = (30, 300, 40)                           # safety edges (front bar, rear E-box)
MAST_D = 30
MAST_Y = 500                                   # GNSS masts at rear corners, 1 m baseline across
ANT_TOP = 1700
ANT = (150, 60)
BEACON = (100, 150)
DISPLAY = (10, 200, 120)
FRONT_ENVELOPE_Z = LEDGE_TOP - LEDGE[2] - 40   # 655: max height of anything at the front

STEEL = 7.85e-6
