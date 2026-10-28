"""BinBot chassis parameters (mm). Single source of truth for 3D model and drawings.

Axes: x = forward (travel), y = left, z = up. Origin = ground, machine centre.
Values marked VENDOR are assumptions until the undercarriage drawing arrives.
"""
from math import atan2, cos, hypot

# --- Undercarriage (bought) — VENDOR ---
TRACK_OUTER_W = 1200      # outer width over tracks
TRACK_W = 250             # single track width
TRACK_LEN = 1700          # overall track length
TRACK_H = 400             # track height (top of track)
TRACK_CONTACT = TRACK_LEN - TRACK_H   # flat on ground = 1300
TRACK_Y = TRACK_OUTER_W / 2 - TRACK_W / 2   # track centre line = 475
TRACK_INNER_Y = TRACK_OUTER_W / 2 - TRACK_W  # inner face = 350

# --- Upper frame (weldment, farmer-built) ---
RHS_H, RHS_B, RHS_T = 100, 50, 4          # main members RHS 100x50x4, standing
BRACE_S, BRACE_T = 60, 4                  # diagonal brace RHS 60x60x4
FRAME_LEN = 1300                          # rail length
RAIL_Y = 300                              # rail centre line (inside track gap)
FRAME_Z0 = 250                            # underside of rails = ground clearance
FRAME_Z1 = FRAME_Z0 + RHS_H               # top of rails = 350
END_BEAM_X = FRAME_LEN / 2 - RHS_B / 2    # 625
INNER_BEAM_X = 300                        # inner cross beams (battery bay +-275)
BEAM_LEN = 2 * (RAIL_Y - RHS_B / 2)       # between rail inner faces = 550

# brace in each end bay, centre line from (bay inner, -y) to (bay outer, +y)
BAY_X0 = INNER_BEAM_X + RHS_B / 2         # 325
BAY_X1 = END_BEAM_X - RHS_B / 2           # 600
BRACE_INSET = 60
BRACE_Y0 = -(RAIL_Y - RHS_B / 2) + BRACE_INSET   # -215
BRACE_Y1 = -BRACE_Y0
BRACE_ANG = atan2(BRACE_Y1 - BRACE_Y0, BAY_X1 - BAY_X0)
BRACE_DY = (BRACE_S / 2) / cos(BRACE_ANG)  # half-width measured along a cut face
BRACE_LEN = round(hypot(BAY_X1 - BAY_X0, BRACE_Y1 - BRACE_Y0 + 2 * BRACE_DY))  # longest edge

# undercarriage mounting brackets (welded to rail outer face, bolt to track frame)
BRK_T, BRK_L, BRK_H = 10, 150, 120
BRK_X = 450
BRK_Z0 = FRAME_Z0 - 10
BRK_HOLE, BRK_PITCH_X, BRK_PITCH_Z = 18, 100, 70   # 4 x M16 clearance

# bumper tabs on end beams
TAB_T, TAB_W, TAB_H, TAB_Y, TAB_HOLE = 8, 100, 80, 200, 14

# battery tray (hung under inner beams)
TRAY_T = 5
TRAY_LX = 2 * (INNER_BEAM_X - RHS_B / 2) - 16   # 534, between hangers
TRAY_LY = 500
TRAY_Z0 = 205
HANGER_W, HANGER_T, HANGER_Y = 40, 8, 180
HANGER_LEN = (FRAME_Z0 + 50) - TRAY_Z0          # 95, overlaps beam by 50

# --- Battery (BP-03 placeholder) ---
BATT = (500, 450, 200)

# --- Lift + weighing (BP-02 placeholders) ---
LIFT_BAR = 40            # RHS 40x40 lift bar on each rail
LIFT_STROKE = 100
CELL = (130, 40, 40)     # low-profile shear-beam load cell incl. mount
CELL_X = 500
DECK_LX, DECK_LY, DECK_H = 1200, 1000, 50
DECK_Z0_LOW = FRAME_Z1 + LIFT_BAR + CELL[2]   # 430
DECK_TOP_LOW = DECK_Z0_LOW + DECK_H           # 480
DECK_TOP_HIGH = DECK_TOP_LOW + LIFT_STROKE    # 580

# --- Bin ---
BIN = (1200, 1000, 760)
BIN_WALL = 30

# --- Steel ---
STEEL = 7.85e-6   # kg/mm^3

# --- Electronics & sensors (BP-04 / BP-05) ---
EBOX = (200, 600, 600)        # depth (x) x width (y) x height (z), IP65 steel enclosure
EBOX_X0 = -(FRAME_LEN / 2 + 10)   # face toward the robot, x = -660 (e-box runs to -860)
EBOX_Z0 = 300
BUMPER = (40, 1100, 150)      # depth x width x height, safety edge on the outer face
BUMPER_X = TRACK_LEN / 2 + 20     # inner face of bumper, x = 870
BUMPER_Z0 = 170
HOOP = 40                     # front sensor hoop RHS 40x40
HOOP_X0 = FRAME_LEN / 2 + 10      # 660
HOOP_Y = 250
HOOP_TOP = 850
LIDAR = (65, 65, 60)          # Mid-360-class
CAM = (60, 60, 60)
ESTOP_BOX = 70                # E-stop housing cube, red mushroom on top
MAST_D = 30
MAST_Y = 150
ANT_TOP = 1560                # GNSS antenna top
ANT = (150, 60)               # antenna diameter, height
BEACON = (100, 150)           # beacon diameter, height
DISPLAY = (10, 200, 120)
