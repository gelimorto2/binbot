"""3D model of the BinBot chassis (BP-01) with BP-02/03 placeholders.

Outputs (cad/out/):
  upper_frame.step / .stl   weldment to fabricate
  chassis_assembly.step     full assembly, bin raised (transport state)
  chassis_assembly.stl      same, single mesh (GitHub shows it in 3D)
  chassis_iso*.svg          isometric previews (front / rear)
"""
from math import degrees
import cadquery as cq
from params import *

OUT = "out/"


def box(lx, ly, lz, x=0, y=0, z0=0):
    """Box given its size, centre x/y and bottom z."""
    return cq.Workplane("XY").box(lx, ly, lz).translate((x, y, z0 + lz / 2))


def rhs(length, b, h, t, axis, x=0, y=0, z0=0):
    """Hollow section along x or y; b = width across, h = height."""
    if axis == "x":
        outer, inner = box(length, b, h, x, y, z0), box(length + 2, b - 2 * t, h - 2 * t, x, y, z0 + t)
    else:
        outer, inner = box(b, length, h, x, y, z0), box(b - 2 * t, length + 2, h - 2 * t, x, y, z0 + t)
    return outer.cut(inner)


def plate_with_holes(lx, ly, lz, holes, d, x, y, z0, axis):
    """Plate; holes = list of (u, v) offsets on its face; axis = hole direction."""
    p = box(lx, ly, lz, x, y, z0)
    for u, v in holes:
        if axis == "y":
            c = cq.Workplane("XZ").center(x + u, z0 + lz / 2 + v).circle(d / 2).extrude(ly, both=True).translate((0, y, 0))
        else:  # axis x
            c = cq.Workplane("YZ").center(y + u, z0 + lz / 2 + v).circle(d / 2).extrude(lx, both=True).translate((x, 0, 0))
        p = p.cut(c)
    return p


def brace(x_sign):
    """Diagonal brace cut to fit between the beams of one end bay."""
    x0, x1 = (BAY_X0, BAY_X1) if x_sign > 0 else (-BAY_X1, -BAY_X0)
    y0, y1 = (BRACE_Y0, BRACE_Y1) if x_sign > 0 else (BRACE_Y1, BRACE_Y0)
    pts = [(x0, y0 - BRACE_DY), (x1, y1 - BRACE_DY), (x1, y1 + BRACE_DY), (x0, y0 + BRACE_DY)]
    z0 = FRAME_Z0 + (RHS_H - BRACE_S) / 2
    solid = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(BRACE_S)
    # hollow it: shrink section by the wall thickness
    ipts = [(x0 - 1, y0 - BRACE_DY + BRACE_T / cos(BRACE_ANG)), (x1 + 1, y1 - BRACE_DY + BRACE_T / cos(BRACE_ANG)),
            (x1 + 1, y1 + BRACE_DY - BRACE_T / cos(BRACE_ANG)), (x0 - 1, y0 + BRACE_DY - BRACE_T / cos(BRACE_ANG))]
    hole = cq.Workplane("XY").workplane(offset=z0 + BRACE_T).polyline(ipts).close().extrude(BRACE_S - 2 * BRACE_T)
    return solid.cut(hole)


def upper_frame():
    parts = []
    for s in (1, -1):
        parts.append(rhs(FRAME_LEN, RHS_B, RHS_H, RHS_T, "x", 0, s * RAIL_Y, FRAME_Z0))           # 1 rails
        parts.append(rhs(BEAM_LEN, RHS_B, RHS_H, RHS_T, "y", s * END_BEAM_X, 0, FRAME_Z0))       # 2 end beams
        parts.append(rhs(BEAM_LEN, RHS_B, RHS_H, RHS_T, "y", s * INNER_BEAM_X, 0, FRAME_Z0))     # 3 inner beams
        parts.append(brace(s))                                                                    # 4 braces
        for sx in (1, -1):
            holes = [(u, v) for u in (-BRK_PITCH_X / 2, BRK_PITCH_X / 2) for v in (-BRK_PITCH_Z / 2, BRK_PITCH_Z / 2)]
            yb = s * (RAIL_Y + RHS_B / 2 + BRK_T / 2)
            parts.append(plate_with_holes(BRK_L, BRK_T, BRK_H, holes, BRK_HOLE, sx * BRK_X, yb, BRK_Z0, "y"))  # 5
            xt = s * (FRAME_LEN / 2 + TAB_T / 2)
            parts.append(plate_with_holes(TAB_T, TAB_W, TAB_H, [(-30, 0), (30, 0)], TAB_HOLE,
                                          xt, sx * TAB_Y, FRAME_Z0 + (RHS_H - TAB_H) / 2, "x"))           # 6
            xh = s * (INNER_BEAM_X - RHS_B / 2 - HANGER_T / 2)
            parts.append(box(HANGER_T, HANGER_W, HANGER_LEN, xh, sx * HANGER_Y, TRAY_Z0))                # 8
    parts.append(box(TRAY_LX, TRAY_LY, TRAY_T, 0, 0, TRAY_Z0))                                          # 7
    frame = parts[0]
    for p in parts[1:]:
        frame = frame.union(p)
    return frame


def track(y):
    t = cq.Workplane("XZ").slot2D(TRACK_LEN, TRACK_H).extrude(TRACK_W / 2, both=True)
    return t.translate((0, y, TRACK_H / 2))


def bin_body(z0):
    lx, ly, lz = BIN
    b = box(lx, ly, lz, 0, 0, z0).cut(box(lx - 2 * BIN_WALL, ly - 2 * BIN_WALL, lz, 0, 0, z0 + BIN_WALL))
    return b


def cyl(d, h, x, y, z0):
    """Vertical cylinder of diameter d and height h standing at z0."""
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def estop(x, y, z0, face):
    """Yellow housing + red mushroom on the outer face (face = +1 front / -1 rear in x)."""
    s = ESTOP_BOX
    house = box(s, s, s, x + face * s / 2, y, z0)
    knob = cq.Workplane("YZ").circle(20).extrude(25).translate((x + face * s if face > 0 else x - s - 25, y, z0 + s / 2))
    return house, knob


def electronics(parts):
    """Adds BP-04/05 components around the frame: (name, shape, rgb)."""
    RED, YEL, BLK, GRY, AMB = (0.8, 0.1, 0.1), (0.95, 0.8, 0.1), (0.1, 0.1, 0.1), (0.6, 0.6, 0.6), (1.0, 0.55, 0.0)
    ex1 = EBOX_X0 - EBOX[0]                                   # rear face of e-box, -860
    parts.append(("ebox", box(EBOX[0], EBOX[1], EBOX[2], EBOX_X0 - EBOX[0] / 2, 0, EBOX_Z0), GRY))
    parts.append(("ebox_mount", box(10, 500, 80, EBOX_X0 + 5, 0, FRAME_Z0 + 10), GRY))
    parts.append(("display", box(DISPLAY[0], DISPLAY[1], DISPLAY[2], ex1 - 5, 0, EBOX_Z0 + 380), BLK))
    parts.append(("isolator_S1", box(80, 40, 80, EBOX_X0 - 100, EBOX[1] / 2 + 20, EBOX_Z0 + 160), RED))
    parts.append(("charge_inlet_X1", box(80, 40, 60, EBOX_X0 - 100, -EBOX[1] / 2 - 20, EBOX_Z0 + 160), BLK))
    for s_, n in ((1, "L"), (-1, "R")):
        h, k = estop(ex1, s_ * 230, EBOX_Z0 + 470, -1)
        parts += [(f"estop_rear_{n}", h, YEL), (f"estop_rear_{n}_knob", k, RED)]
    parts.append(("cam_rear", box(*CAM, ex1 + 40, 0, EBOX_Z0 + EBOX[2]), BLK))
    # rear masts: GNSS2 antenna and beacon
    mx = EBOX_X0 - EBOX[0] / 2
    ztop = EBOX_Z0 + EBOX[2]
    parts.append(("mast_rear", cyl(MAST_D, ANT_TOP - ANT[1] - ztop, mx, MAST_Y, ztop), GRY))
    parts.append(("gnss2_antenna", cyl(ANT[0], ANT[1], mx, MAST_Y, ANT_TOP - ANT[1]), (0.9, 0.9, 0.9)))
    parts.append(("beacon_mast", cyl(MAST_D, 1350 - ztop, mx, -MAST_Y, ztop), GRY))
    parts.append(("beacon", cyl(BEACON[0], BEACON[1], mx, -MAST_Y, 1350), AMB))
    # front sensor hoop
    hx = HOOP_X0 + HOOP / 2
    for s_ in (1, -1):
        parts.append((f"hoop_upright_{s_}", box(HOOP, HOOP, HOOP_TOP - FRAME_Z0, hx, s_ * HOOP_Y, FRAME_Z0), GRY))
    parts.append(("hoop_bar", box(HOOP, 2 * HOOP_Y + HOOP, HOOP, hx, 0, HOOP_TOP - HOOP), GRY))
    parts.append(("lidar", box(*LIDAR, hx + 20, 0, HOOP_TOP), BLK))
    parts.append(("cam_front", box(*CAM, HOOP_X0 + HOOP + CAM[0] / 2, 0, HOOP_TOP - HOOP - CAM[2] - 10), BLK))
    for s_, n in ((1, "L"), (-1, "R")):
        h, k = estop(HOOP_X0 + HOOP, s_ * HOOP_Y, HOOP_TOP - HOOP - ESTOP_BOX - 20, 1)
        parts += [(f"estop_front_{n}", h, YEL), (f"estop_front_{n}_knob", k, RED)]
    parts.append(("mast_front", cyl(MAST_D, ANT_TOP - ANT[1] - HOOP_TOP, hx, MAST_Y, HOOP_TOP), GRY))
    parts.append(("gnss1_antenna", cyl(ANT[0], ANT[1], hx, MAST_Y, ANT_TOP - ANT[1]), (0.9, 0.9, 0.9)))
    # bumpers with safety edges + arms to the bumper tabs
    for s_, n in ((1, "front"), (-1, "rear")):
        bx = s_ * (BUMPER_X + BUMPER[0] / 2)
        parts.append((f"bumper_{n}", box(BUMPER[0], BUMPER[1], BUMPER[2], bx, 0, BUMPER_Z0), YEL))
        parts.append((f"safety_edge_{n}", box(30, BUMPER[1], BUMPER[2] - 20, bx + s_ * (BUMPER[0] / 2 + 15), 0, BUMPER_Z0 + 10), BLK))
        for sy in (1, -1):
            x0 = FRAME_LEN / 2 + TAB_T
            parts.append((f"bumper_arm_{n}_{sy}", box(BUMPER_X - x0, 40, 40, s_ * (x0 + BUMPER_X) / 2, sy * TAB_Y, FRAME_Z0 + 30), GRY))
    # lift actuators (BP-02 placeholder): 2 per side, vertical, beside the rails
    for s_ in (1, -1):
        for sx in (1, -1):
            parts.append((f"lift_actuator_{s_}{sx}", cyl(50, 110, sx * 450, s_ * (RAIL_Y - 60), FRAME_Z1 - 110), (0.3, 0.3, 0.7)))
    return parts


def assembly(raised=True):
    lift = LIFT_STROKE if raised else 0
    a = cq.Assembly(name="binbot_chassis")
    for s, n in ((1, "L"), (-1, "R")):
        a.add(track(s * TRACK_Y), name=f"track_{n}", color=cq.Color(0.15, 0.15, 0.15))
        a.add(box(FRAME_LEN - 100, LIFT_BAR, LIFT_BAR, 0, s * RAIL_Y, FRAME_Z1 + lift),
              name=f"lift_bar_{n}", color=cq.Color(0.9, 0.6, 0.1))
        for sx in (1, -1):
            a.add(box(*CELL[:2], CELL[2], sx * CELL_X, s * RAIL_Y, FRAME_Z1 + LIFT_BAR + lift),
                  name=f"load_cell_{n}{'F' if sx > 0 else 'B'}", color=cq.Color(0.2, 0.5, 0.9))
    a.add(upper_frame(), name="upper_frame", color=cq.Color(0.2, 0.45, 0.25))
    a.add(box(*BATT, 0, 0, TRAY_Z0 + TRAY_T), name="battery", color=cq.Color(0.8, 0.15, 0.15))
    deck = box(DECK_LX, DECK_LY, DECK_H, 0, 0, DECK_Z0_LOW + lift).cut(
        box(DECK_LX - 120, DECK_LY - 120, DECK_H, 0, 0, DECK_Z0_LOW + lift))
    a.add(deck, name="deck", color=cq.Color(0.9, 0.6, 0.1))
    a.add(bin_body(DECK_TOP_LOW + lift), name="bin", color=cq.Color(0.6, 0.75, 0.9, 0.5))
    for name, shape, rgb in electronics([]):
        a.add(shape, name=name, color=cq.Color(*rgb))
    return a


if __name__ == "__main__":
    f = upper_frame()
    cq.exporters.export(f, OUT + "upper_frame.step")
    cq.exporters.export(f, OUT + "upper_frame.stl", tolerance=0.5, angularTolerance=0.3)
    a = assembly(raised=True)
    a.save(OUT + "chassis_assembly.step")
    comp = a.toCompound()
    cq.exporters.export(comp, OUT + "chassis_assembly.stl", tolerance=1.0, angularTolerance=0.5)
    opt = {"width": 900, "height": 600, "marginLeft": 20, "marginTop": 20,
           "projectionDir": (1.0, 1.2, -0.7), "showAxes": False, "showHidden": False, "strokeWidth": 1.0}
    # SVG exporter draws with y down: flip the model so the preview is upright
    flip = lambda shape: shape.rotate((0, 0, 0), (1, 0, 0), 180)
    cq.exporters.export(cq.Workplane().add(flip(comp)), OUT + "chassis_iso.svg", opt=opt)
    cq.exporters.export(cq.Workplane().add(flip(f.val())), OUT + "upper_frame_iso.svg", opt=opt)
    cq.exporters.export(cq.Workplane().add(flip(comp)), OUT + "chassis_iso_rear.svg",
                        opt={**opt, "projectionDir": (-1.0, -1.2, -0.7)})
    print("frame volume mm3:", round(f.val().Volume()), "mass kg:", round(f.val().Volume() * STEEL, 1))
    print("brace length:", BRACE_LEN, "angle deg:", round(degrees(BRACE_ANG), 1))
