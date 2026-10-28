"""3D model of BinBot (rev C: top module on an unmodified bought base) and the bin stand.

Outputs (cad/out/):
  upper_frame.step / .stl        weldment to fabricate
  chassis_assembly.step / .stl   robot with bin raised (transport state)
  bin_stand.step / .stl          base stand the robot drives under
  swap_scene.step                robot under a stand, bin set down
  *_iso*.svg                     line-drawing previews
"""
from math import asin, cos, degrees, sin
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
    """Plate; holes = (u, v) offsets on its face; axis = hole direction (x or y)."""
    p = box(lx, ly, lz, x, y, z0)
    for u, v in holes:
        if axis == "y":
            c = cq.Workplane("XZ").center(x + u, z0 + lz / 2 + v).circle(d / 2).extrude(ly, both=True).translate((0, y, 0))
        else:
            c = cq.Workplane("YZ").center(y + u, z0 + lz / 2 + v).circle(d / 2).extrude(lx, both=True).translate((x, 0, 0))
        p = p.cut(c)
    return p


def cyl(d, h, x, y, z0):
    """Vertical cylinder of diameter d and height h standing at z0."""
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def bar_between(p, q, w, t, y):
    """Flat link of width w, thickness t (in y) between points p=(x,z) and q=(x,z) at plane y."""
    (x0, z0), (x1, z1) = p, q
    L = ((x1 - x0) ** 2 + (z1 - z0) ** 2) ** 0.5
    ang = degrees(asin((z1 - z0) / L))
    if x1 < x0:
        ang = 180 - ang
    b = cq.Workplane("XY").box(L + w, t, w).rotate((0, 0, 0), (0, 1, 0), -ang)
    return b.translate(((x0 + x1) / 2, y, (z0 + z1) / 2))


# ------------------------------------------------------------------ lift kinematics
LINK_V0 = (LIFT_BAR_Z0 + LIFT_BAR[2] / 2) - (FRAME_Z0 + 55)     # vertical pivot span, lowered (70)
LINK_LOW = [(580.0, FRAME_Z0 + 55), (-345.0, FRAME_Z0 + 55)]     # fixed pivots on the rails (x, z)


def link_state(lift):
    """Returns (bar x shift, list of (lower, upper) pivot pairs) for a lift height 0..LIFT_STROKE."""
    v = LINK_V0 + lift
    dx = (LINK_L ** 2 - v ** 2) ** 0.5
    pairs = [((xl, zl), (xl - dx, zl + v)) for xl, zl in LINK_LOW]
    dx0 = (LINK_L ** 2 - LINK_V0 ** 2) ** 0.5
    return dx0 - dx, pairs


LIFT_SHIFT = link_state(LIFT_STROKE)[0]       # bar moves forward this much when raised (~82)


# ------------------------------------------------------------------ parts
def upper_frame():
    parts = []
    hb = RHS_B / 2
    for s in (1, -1):
        parts.append(rhs(FRAME_LEN, RHS_B, RHS_H, RHS_T, "x", 0, s * RAIL_Y, FRAME_Z0))           # 1 rails
        parts.append(rhs(BEAM_LEN, RHS_B, RHS_H, RHS_T, "y", s * END_BEAM_X, 0, FRAME_Z0))       # 2 end beams
        parts.append(rhs(BEAM_LEN, RHS_B, RHS_H, RHS_T, "y", s * INNER_BEAM_X, 0, FRAME_Z0))     # 3 inner beams
        for sx in (1, -1):
            # 4 base plates under the rails, 4 x Ø18 down into the base top
            pl = box(BRK_L, BRK_W, BRK_T, sx * BRK_X, s * RAIL_Y, FRAME_Z0 - BRK_T)
            for u in (-BRK_PITCH_X / 2, BRK_PITCH_X / 2):
                for v in (-BRK_PITCH_Y / 2, BRK_PITCH_Y / 2):
                    pl = pl.cut(cyl(BRK_HOLE, BRK_T + 2, sx * BRK_X + u, s * RAIL_Y + v, FRAME_Z0 - BRK_T - 1))
            parts.append(pl)
            xt = s * (FRAME_LEN / 2 + TAB_T / 2)
            parts.append(plate_with_holes(TAB_T, TAB_W, TAB_H, [(-30, 0), (30, 0)], TAB_HOLE,
                                          xt, sx * TAB_Y, FRAME_Z0 + (RHS_H - TAB_H) / 2, "x"))            # 5
            # 6 link pivot plates (10 mm) on the rail inner faces
            for xl, zl in LINK_LOW:
                parts.append(box(60, 10, 70, xl, sx * (RAIL_Y - hb - 5), zl - 35))
    frame = parts[0]
    for p in parts[1:]:
        frame = frame.union(p)
    return frame


def base_parts():
    """The bought base (placeholder, VENDOR): centre body between the tracks + flat top plate."""
    return [("base_body", box(*BASE_BODY, 0, 0, BASE_CLEARANCE), (0.25, 0.25, 0.25)),
            ("base_top_plate", box(*BASE_PLATE, 0, 0, BASE_TOP - BASE_PLATE[2]), (0.35, 0.35, 0.35))]


def track(y):
    return cq.Workplane("XZ").slot2D(TRACK_LEN, TRACK_H).extrude(TRACK_W / 2, both=True).translate((0, y, TRACK_H / 2))


def bin_body(x, z0):
    lx, ly, lz = BIN
    return box(lx, ly, lz, x, 0, z0).cut(box(lx - 2 * BIN_WALL, ly - 2 * BIN_WALL, lz, x, 0, z0 + BIN_WALL))


def lift_parts(lift):
    """Lift bars, links, actuators, load cells and deck at lift height 0..100."""
    shift, pairs = link_state(lift)
    out = []
    zb = LIFT_BAR_Z0 + lift
    for s in (1, -1):
        out.append(("lift_bar", rhs(LIFT_BAR[0], LIFT_BAR[1], LIFT_BAR[2], 3, "x", shift, s * RAIL_Y, zb), (0.9, 0.6, 0.1)))
        yl = s * (RAIL_Y - RHS_B / 2 - 20)
        for lo, up in pairs:
            out.append(("link", bar_between(lo, up, 30, 10, yl), (0.3, 0.3, 0.3)))
        # actuator: clevis on inner beam (x -275) to lug under the bar centre
        a0 = (-(INNER_BEAM_X - RHS_B / 2) + 35, FRAME_Z0 + 50)
        a1 = (shift, zb - 5)
        out.append(("lift_actuator", bar_between(a0, a1, 50, 50, s * (RAIL_Y - RHS_B / 2 - 45)), (0.3, 0.3, 0.7)))
        for sx in (1, -1):
            out.append(("load_cell", box(*CELL[:2], CELL[2], sx * CELL_X + shift, s * RAIL_Y, zb + LIFT_BAR[2]), (0.2, 0.5, 0.9)))
    z0 = DECK_Z0_LOW + lift
    deck = box(DECK_LX, DECK_LY, DECK_H, shift, 0, z0).cut(box(DECK_LX - 120, DECK_LY - 120, DECK_H, shift, 0, z0))
    for xx in (-300, 0, 300):                                   # deck cross members
        deck = deck.union(box(50, DECK_LY - 120, DECK_H, xx + shift, 0, z0))
    out.append(("deck", deck, (0.9, 0.6, 0.1)))
    return out, shift


def estop(x, y, z0, face):
    """Yellow housing + red mushroom; face = +1 points +x, -1 points -x, +2/-2 points +y/-y."""
    s = ESTOP_BOX
    if abs(face) == 1:
        house = box(s, s, s, x + face * s / 2, y, z0)
        kx = x + s if face > 0 else x - s - 25
        knob = cq.Workplane("YZ").circle(20).extrude(25).translate((kx, y, z0 + s / 2))
    else:
        f = face / 2
        house = box(s, s, s, x, y + f * s / 2, z0)
        ky = y + s if f > 0 else y - s - 25
        knob = cq.Workplane("XZ").circle(20).extrude(-25).translate((x, ky, z0 + s / 2))
    return house, knob


def electronics():
    RED, YEL, BLK, GRY, AMB, WHT = (0.8, 0.1, 0.1), (0.95, 0.8, 0.1), (0.1, 0.1, 0.1), (0.6, 0.6, 0.6), (1.0, 0.55, 0.0), (0.9, 0.9, 0.9)
    p = []
    # rear E-box with everything tall
    ex1 = EBOX_X0 - EBOX[0]
    mx = EBOX_X0 - EBOX[0] / 2
    ztop = EBOX_Z0 + EBOX[2]
    p.append(("ebox", box(EBOX[0], EBOX[1], EBOX[2], mx, 0, EBOX_Z0), GRY))
    p.append(("ebox_mount", box(10, EBOX[1] - 100, RHS_H, EBOX_X0 + 5, 0, FRAME_Z0), GRY))
    p.append(("display", box(DISPLAY[0], DISPLAY[1], DISPLAY[2], ex1 - 5, 0, EBOX_Z0 + EBOX[2] - 180), BLK))
    p.append(("isolator_S1", box(80, 40, 80, mx, EBOX[1] / 2 + 20, EBOX_Z0 + 150), RED))
    p.append(("safety_edge_rear", box(EDGE[0], EBOX[1] - 100, EDGE[2], ex1 - EDGE[0] / 2, 0, EBOX_Z0 + 10), BLK))
    for s in (1, -1):
        h, k = estop(mx, s * EBOX[1] / 2, EBOX_Z0 + EBOX[2] - 150, 2 * s)
        p += [("estop_rear", h, YEL), ("estop_rear_knob", k, RED)]
        # GNSS masts on outriggers at the rear corners (1 m baseline across)
        p.append(("mast_arm", box(40, MAST_Y - EBOX[1] / 2 + 20, 40, mx, s * (EBOX[1] / 2 + MAST_Y + 20) / 2, ztop - 40), GRY))
        p.append(("mast", cyl(MAST_D, ANT_TOP - ANT[1] - ztop + 40, mx, s * MAST_Y, ztop - 40), GRY))
        p.append(("gnss_antenna", cyl(ANT[0], ANT[1], mx, s * MAST_Y, ANT_TOP - ANT[1]), WHT))
    p.append(("beacon", cyl(BEACON[0], BEACON[1], mx, 0, ztop), AMB))
    # rear anti-slide sprags, stowed upright beside the E-box, held by holding magnets
    px, pz = SPRAG_PIVOT
    for s in (1, -1):
        p.append(("sprag_arm", box(SPRAG_ARM, SPRAG_ARM, SPRAG_L, px, s * SPRAG_Y, pz), (0.85, 0.2, 0.1)))
        p.append(("sprag_claw", box(SPRAG_CLAW[2], SPRAG_CLAW[0], SPRAG_CLAW[1], px - SPRAG_ARM / 2 - SPRAG_CLAW[2] / 2, s * SPRAG_Y, pz + SPRAG_L - SPRAG_CLAW[1]), (0.4, 0.4, 0.4)))
        p.append(("sprag_pivot", box(60, 80, 60, px, s * SPRAG_Y, pz - 30), GRY))
        p.append(("sprag_magnet", box(40, 20, 40, px, s * (EBOX[1] / 2 + 12), pz + SPRAG_L - 120), BLK))
    p.append(("cam_rear", box(*CAM, ex1 + 40, 180, ztop), BLK))
    # low front sensor bar (fits under the stand ledges / bins)
    bx = FRONT_BAR_X0 + FRONT_BAR[0] / 2
    p.append(("front_bar", rhs(FRONT_BAR[1], FRONT_BAR[0], FRONT_BAR[2], 3, "y", bx, 0, FRONT_BAR_Z0), GRY))
    for s in (1, -1):
        p.append(("front_bar_arm", box(FRONT_BAR_X0 - FRAME_LEN / 2, 40, 40, (FRONT_BAR_X0 + FRAME_LEN / 2) / 2, s * TAB_Y, FRONT_BAR_Z0), GRY))
        h, k = estop(FRONT_BAR_X0 + FRONT_BAR[0], s * 280, FRONT_BAR_Z0 - 15, 1)
        p += [("estop_front", h, YEL), ("estop_front_knob", k, RED)]
    p.append(("lidar", box(*LIDAR, bx, 0, FRONT_BAR_Z0 + FRONT_BAR[2]), BLK))
    for s in (1, -1):   # front drag anchors (uphill end) in magnet holders under the sensor bar
        ax_ = FRONT_BAR_X0 + FRONT_BAR[0] + ANCHOR_CLAW[0] / 2 + 5
        p.append(("drag_anchor", box(*ANCHOR_CLAW, ax_, s * ANCHOR_Y, ANCHOR_Z0), (0.85, 0.2, 0.1)))
        p.append(("anchor_holder", box(ANCHOR_CLAW[0], ANCHOR_CLAW[1], 20, ax_, s * ANCHOR_Y, ANCHOR_Z0 + ANCHOR_CLAW[2]), GRY))
    p.append(("cam_front", box(*CAM, bx + 10, 130, FRONT_BAR_Z0 + FRONT_BAR[2]), BLK))
    p.append(("safety_edge_front", box(EDGE[0], 380, EDGE[2], FRONT_BAR_X0 + FRONT_BAR[0] + EDGE[0] / 2, 0, FRONT_BAR_Z0), BLK))
    return p


def robot(lift=LIFT_STROKE, with_bin=True, name="binbot"):
    a = cq.Assembly(name=name)
    for s in (1, -1):
        a.add(track(s * TRACK_Y), name=f"track_{'L' if s > 0 else 'R'}", color=cq.Color(0.15, 0.15, 0.15))
    for n, shp, rgb in base_parts():
        a.add(shp, name=n, color=cq.Color(*rgb))
    a.add(upper_frame(), name="upper_frame", color=cq.Color(0.2, 0.45, 0.25))
    parts, shift = lift_parts(lift)
    for i, (n, shp, rgb) in enumerate(parts + electronics()):
        a.add(shp, name=f"{n}_{i}", color=cq.Color(*rgb))
    if with_bin:
        a.add(bin_body(shift, DECK_TOP_LOW + lift), name="bin", color=cq.Color(0.6, 0.75, 0.9, 0.5))
    return a


def bin_stand():
    """Base stand: 4 posts + 2 ledges; open underneath and at both ends."""
    parts = []
    for s in (1, -1):
        for sx in (1, -1):
            parts.append(box(POST, POST, LEDGE_TOP + 300, sx * POST_X, s * POST_Y, 0))      # posts
            # arm from post to ledge
            parts.append(box(POST, POST_Y - LEDGE_Y0, LEDGE[2], sx * POST_X, s * (POST_Y + LEDGE_Y0) / 2, LEDGE_TOP - LEDGE[2]))
        ly = LEDGE_Y0 + LEDGE[1] / 2
        parts.append(rhs(LEDGE[0], LEDGE[1], LEDGE[2], 4, "x", 0, s * ly, LEDGE_TOP - LEDGE[2]))
        parts.append(box(LEDGE[0], 10, 60, 0, s * (LEDGE_Y0 + LEDGE[1] + 5 + 40), LEDGE_TOP))   # side keeper
        # ground entry guides for the tracks (funnel) — at the entry (rear) side
        gy = TRACK_OUTER_W / 2 + 30 + GUIDE[1] / 2
        parts.append(box(GUIDE[0], GUIDE[1], GUIDE[2], 0, s * gy, 0))
        flare = cq.Workplane("XY").polyline([(-GUIDE[0] / 2, s * (gy - GUIDE[1] / 2)), (-GUIDE[0] / 2 - 500, s * (gy + GUIDE_FLARE - GUIDE[1] / 2)),
                                             (-GUIDE[0] / 2 - 500, s * (gy + GUIDE_FLARE + GUIDE[1] / 2)), (-GUIDE[0] / 2, s * (gy + GUIDE[1] / 2))]).close().extrude(GUIDE[2])
        parts.append(flare)
    st = parts[0]
    for q in parts[1:]:
        st = st.union(q)
    return st


def iso(shape, name, direction=(1.0, 1.2, -0.7)):
    opt = {"width": 900, "height": 600, "marginLeft": 20, "marginTop": 20, "projectionDir": direction,
           "showAxes": False, "showHidden": False, "strokeWidth": 1.0}
    # SVG exporter draws with y down: flip so the preview is upright
    cq.exporters.export(cq.Workplane().add(shape.rotate((0, 0, 0), (1, 0, 0), 180)), OUT + name + ".svg", opt=opt)
    from electrical import white_svg
    white_svg(OUT + name + ".svg")


if __name__ == "__main__":
    f = upper_frame()
    cq.exporters.export(f, OUT + "upper_frame.step")
    cq.exporters.export(f, OUT + "upper_frame.stl", tolerance=0.5, angularTolerance=0.3)
    a = robot()
    a.export(OUT + "chassis_assembly.step")
    comp = a.toCompound()
    cq.exporters.export(comp, OUT + "chassis_assembly.stl", tolerance=1.0, angularTolerance=0.5)
    st = bin_stand()
    cq.exporters.export(st, OUT + "bin_stand.step")
    cq.exporters.export(st, OUT + "bin_stand.stl", tolerance=1.0, angularTolerance=0.5)
    scene = robot(lift=0, with_bin=False, name="swap_scene")
    scene.add(st, name="stand", color=cq.Color(0.5, 0.5, 0.55))
    scene.add(bin_body(0, LEDGE_TOP), name="bin_on_stand", color=cq.Color(0.6, 0.75, 0.9, 0.5))
    scene.export(OUT + "swap_scene.step")
    iso(comp, "chassis_iso")
    iso(comp, "chassis_iso_rear", (-1.0, -1.2, -0.7))
    iso(f.val(), "upper_frame_iso")
    iso(scene.toCompound(), "swap_scene_iso")
    print("frame mass kg:", round(f.val().Volume() * STEEL, 1), " lift shift mm:", round(LIFT_SHIFT, 1))
