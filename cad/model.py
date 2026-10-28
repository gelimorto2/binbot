"""3D model of the BinBot chassis (BP-01) with BP-02/03 placeholders.

Outputs (cad/out/):
  upper_frame.step / .stl   weldment to fabricate
  chassis_assembly.step     full assembly, bin raised (transport state)
  chassis_assembly.stl      same, single mesh (GitHub shows it in 3D)
  chassis_iso.svg           isometric preview
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
    print("frame volume mm3:", round(f.val().Volume()), "mass kg:", round(f.val().Volume() * STEEL, 1))
    print("brace length:", BRACE_LEN, "angle deg:", round(degrees(BRACE_ANG), 1))
