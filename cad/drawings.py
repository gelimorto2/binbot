"""2D drawings (DXF + PDF + PNG) generated from params.py.

DWG-001  General arrangement, robot (bin raised)          1:10 on A3
DWG-002  Upper frame weldment — fabrication drawing        1:10 on A3
DWG-003  Base bin stand + clearance section                 1:10 on A3
"""
import datetime
import ezdxf
from ezdxf.enums import TextEntityAlignment as TA
from ezdxf.addons.drawing import matplotlib as dm
from params import *

S = 10                       # drawing scale 1:10 -> A3 = 4200 x 2970 model units
W, H = 420 * S, 297 * S
DIM = {"dimtxt": 2.8 * S, "dimasz": 2.5 * S, "dimexo": 1 * S, "dimexe": 1.5 * S,
       "dimgap": 0.8 * S, "dimdec": 0, "dimtad": 1, "dimlfac": 1}
OUT = "out/"


class Sheet:
    def __init__(self, number, title, scale=10):
        self.S, self.W, self.H = scale, 420 * scale, 297 * scale
        self.DIM = {k: v * scale / S if k in ("dimtxt", "dimasz", "dimexo", "dimexe", "dimgap") else v for k, v in DIM.items()}
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.header["$LTSCALE"] = scale
        self.doc.header["$INSUNITS"] = 4  # mm
        for name, color, lt, lw in (("OUTLINE", 7, "CONTINUOUS", 50), ("HIDDEN", 8, "DASHED", 25),
                                    ("CENTER", 1, "CENTER", 18), ("PHANTOM", 5, "PHANTOM", 25),
                                    ("DIM", 3, "CONTINUOUS", 18), ("TEXT", 7, "CONTINUOUS", 25),
                                    ("BORDER", 7, "CONTINUOUS", 70)):
            self.doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
        self.msp = self.doc.modelspace()
        self.number, self.title = number, title
        self.frame()

    # --- primitives (view-local coords u,v + view origin) ---
    def rect(self, o, u0, v0, u1, v1, layer="OUTLINE"):
        x, y = o
        self.msp.add_lwpolyline([(x + u0, y + v0), (x + u1, y + v0), (x + u1, y + v1), (x + u0, y + v1)],
                                close=True, dxfattribs={"layer": layer})

    def line(self, o, u0, v0, u1, v1, layer="OUTLINE"):
        x, y = o
        self.msp.add_line((x + u0, y + v0), (x + u1, y + v1), dxfattribs={"layer": layer})

    def poly(self, o, pts, layer="OUTLINE", close=True):
        x, y = o
        self.msp.add_lwpolyline([(x + u, y + v, *rest) for u, v, *rest in pts], format="xyb",
                                close=close, dxfattribs={"layer": layer})

    def circle(self, o, u, v, r, layer="OUTLINE"):
        self.msp.add_circle((o[0] + u, o[1] + v), r, dxfattribs={"layer": layer})

    def text(self, x, y, s, h=3.5, align=TA.LEFT, layer="TEXT"):
        self.msp.add_text(s, height=h * self.S, dxfattribs={"layer": layer}).set_placement((x, y), align=align)

    def dim(self, o, p1, p2, base, vertical=False):
        x, y = o
        d = self.msp.add_linear_dim(base=(x + base[0], y + base[1]), p1=(x + p1[0], y + p1[1]),
                                    p2=(x + p2[0], y + p2[1]), angle=90 if vertical else 0,
                                    override=self.DIM, dxfattribs={"layer": "DIM"})
        d.render()

    def label(self, o, u, v, s):
        self.text(o[0] + u, o[1] + v, s, h=4, align=TA.MIDDLE_CENTER)

    def balloon(self, o, u, v, du, dv, n):
        x, y = o
        r = 4 * self.S
        self.msp.add_line((x + u, y + v), (x + u + du, y + v + dv), dxfattribs={"layer": "TEXT"})
        self.msp.add_circle((x + u + du, y + v + dv), r, dxfattribs={"layer": "TEXT"})
        self.text(x + u + du, y + v + dv, str(n), h=3.5, align=TA.MIDDLE_CENTER)

    def ground(self, o, u0, u1):
        self.line(o, u0, 0, u1, 0, "OUTLINE")
        for u in range(int(u0), int(u1), 60):
            self.line(o, u, 0, u - 40, -40, "DIM")

    # --- sheet furniture ---
    def frame(self):
        m = 10 * self.S
        self.msp.add_lwpolyline([(m, m), (self.W - m, m), (self.W - m, self.H - m), (m, self.H - m)], close=True,
                                dxfattribs={"layer": "BORDER"})
        x0, y0, x1, y1 = self.W - m - 180 * self.S, m, self.W - m, m + 40 * self.S
        self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "BORDER"})
        for yy in (y0 + 10 * self.S, y0 + 20 * self.S, y0 + 30 * self.S):
            self.msp.add_line((x0, yy), (x1, yy), dxfattribs={"layer": "BORDER"})
        self.text(x0 + 3 * self.S, y1 - 7.5 * self.S, "BINBOT — autonomous olive bin carrier", h=4.5)
        self.text(x0 + 3 * self.S, y1 - 17.5 * self.S, self.title, h=4.5)
        self.text(x0 + 3 * self.S, y0 + 12.5 * self.S, f"DWG {self.number}   REV B   SCALE 1:{self.S} (A3)   UNITS mm", h=3.5)
        self.text(x0 + 3 * self.S, y0 + 2.5 * self.S,
                  f"PRELIMINARY — undercarriage values assumed   {datetime.date.today():%Y-%m-%d}", h=3.5)

    def save(self, name):
        self.doc.saveas(OUT + name + ".dxf")
        for ext in ("pdf", "png"):
            dm.qsave(self.msp, OUT + f"{name}.{ext}", bg="#FFFFFF", fg="#000000", dpi=150 if ext == "png" else 300,
                     size_inches=(16.54, 11.69))


def stadium(L, Hh):
    """Track outline in side view: bottom/top straights joined by half circles."""
    a = L / 2 - Hh / 2
    return [(-a, 0, 0), (a, 0, 1), (a, Hh, 0), (-a, Hh, 1)]


LINK_V0 = (LIFT_BAR_Z0 + LIFT_BAR[2] / 2) - (FRAME_Z0 + 55)
LINK_LOW = [(580.0, FRAME_Z0 + 55), (-345.0, FRAME_Z0 + 55)]
DX0 = (LINK_L ** 2 - LINK_V0 ** 2) ** 0.5


def lift_shift(h):
    return DX0 - (LINK_L ** 2 - (LINK_V0 + h) ** 2) ** 0.5


def m_rhs(L, b, h, t):
    return (b * h - (b - 2 * t) * (h - 2 * t)) * L * STEEL


def cut_list(sh, x, y, items):
    sh.text(x, y, "CUT LIST", h=4.5)
    k = sh.S / 10
    sh.text(x, y - 80 * k, "#   Part                         Section          L mm   Qty   kg", h=3.2)
    total = 0
    for i, (n, part, sec, L, q, m) in enumerate(items):
        total += m * q
        sh.text(x, y - (150 + i * 62) * k, f"{n:<3} {part:<28} {sec:<16} {L:>5.0f}  {q:>3}  {m * q:>5.1f}", h=3.2)
    sh.text(x, y - (150 + len(items) * 62) * k, f"{'':<52}TOTAL ≈ {total:.0f} kg", h=3.2)
    return total


def notes(sh, x, y, rows):
    for i, r in enumerate(rows):
        sh.text(x, y - i * 5.8 * sh.S, r, h=3.2 if i else 4.5)


# ---------------------------------------------------------------- DWG-001
def dwg_001():
    sh = Sheet("001", "GENERAL ARRANGEMENT — ROBOT, BIN RAISED")
    h = LIFT_STROKE
    sx_ = lift_shift(h)
    bz0, bin_top = DECK_TOP_HIGH, DECK_TOP_HIGH + BIN[2]
    mx = EBOX_X0 - EBOX[0] / 2
    ez1 = EBOX_Z0 + EBOX[2]
    fx = FRONT_BAR_X0

    E = (1600, 900)
    sh.label(E, 0, ANT_TOP + 130, "SIDE VIEW")
    sh.ground(E, -1100, 1100)
    sh.poly(E, stadium(TRACK_LEN, TRACK_H))
    sh.rect(E, -FRAME_LEN / 2, FRAME_Z0, FRAME_LEN / 2, FRAME_Z1)
    for s_ in (1, -1):
        sh.rect(E, s_ * BAY_X0, BATT_Z0, s_ * (BAY_X0 + BATT_PACK[0]), BATT_Z0 + BATT_PACK[2], "HIDDEN")
    v = LINK_V0 + h
    dx = (LINK_L ** 2 - v ** 2) ** 0.5
    for xl, zl in LINK_LOW:
        sh.line(E, xl, zl, xl - dx, zl + v)
        sh.circle(E, xl, zl, 10)
    sh.rect(E, sx_ - LIFT_BAR[0] / 2, LIFT_BAR_Z0 + h, sx_ + LIFT_BAR[0] / 2, LIFT_BAR_Z0 + h + LIFT_BAR[2])
    for s_ in (1, -1):
        sh.rect(E, sx_ + s_ * CELL_X - CELL[0] / 2, LIFT_BAR_Z0 + h + LIFT_BAR[2], sx_ + s_ * CELL_X + CELL[0] / 2, DECK_Z0_LOW + h)
    sh.rect(E, sx_ - DECK_LX / 2, DECK_Z0_LOW + h, sx_ + DECK_LX / 2, DECK_TOP_HIGH)
    sh.rect(E, sx_ - BIN[0] / 2, bz0, sx_ + BIN[0] / 2, bin_top)
    sh.rect(E, EBOX_X0 - EBOX[0], EBOX_Z0, EBOX_X0, ez1)
    sh.label(E, mx, EBOX_Z0 + 300, "E-BOX")
    sh.rect(E, mx - MAST_D / 2, ez1, mx + MAST_D / 2, ANT_TOP - ANT[1])
    sh.rect(E, mx - ANT[0] / 2, ANT_TOP - ANT[1], mx + ANT[0] / 2, ANT_TOP)
    sh.rect(E, mx - BEACON[0] / 2, ez1, mx + BEACON[0] / 2, ez1 + BEACON[1])
    sh.rect(E, FRAME_LEN / 2, FRONT_BAR_Z0, fx + FRONT_BAR[0], FRONT_BAR_Z0 + FRONT_BAR[2])
    sh.rect(E, fx - 12, FRONT_BAR_Z0 + FRONT_BAR[2], fx + 53, FRONT_BAR_Z0 + FRONT_BAR[2] + LIDAR[2])
    sh.rect(E, fx + FRONT_BAR[0], FRONT_BAR_Z0 - 15, fx + FRONT_BAR[0] + ESTOP_BOX, FRONT_BAR_Z0 + 55)
    sh.line(E, sx_, -60, sx_, bin_top + 60, "CENTER")
    sh.line(E, 400, FRONT_ENVELOPE_Z, 1050, FRONT_ENVELOPE_Z, "PHANTOM")
    sh.text(E[0] + 700, E[1] + FRONT_ENVELOPE_Z + 20, f"front max {FRONT_ENVELOPE_Z:.0f}", h=2.5)
    cog = 745
    sh.circle(E, sx_, cog, 40)
    sh.line(E, sx_ - 60, cog, sx_ + 60, cog), sh.line(E, sx_, cog - 60, sx_, cog + 60)
    sh.text(E[0] + sx_ + 70, E[1] + cog + 20, "CoG ≈ 745 (full, raised)", h=3)
    sh.text(E[0] + mx - 330, E[1] + ANT_TOP - 50, "GNSS", h=2.5)
    sh.text(E[0] + fx + 120, E[1] + FRONT_BAR_Z0 + 90, "LiDAR", h=2.5)
    sh.text(E[0] - 1000, E[1] - 140, "FRONT →  (x+)", h=3)
    xr, xf = EBOX_X0 - EBOX[0], TRACK_LEN / 2
    sh.dim(E, (-TRACK_CONTACT / 2, 0), (TRACK_CONTACT / 2, 0), (0, -130))
    sh.dim(E, (xr, 0), (xf, TRACK_H / 2), (0, -250))
    sh.dim(E, (sx_ - BIN[0] / 2, bin_top), (sx_ + BIN[0] / 2, bin_top), (sx_, bin_top + 90))
    for z, b in ((FRAME_Z0, -1080), (DECK_TOP_HIGH, -1180), (bin_top, -1280), (ANT_TOP, -1380)):
        sh.dim(E, (xr if z == ANT_TOP else -FRAME_LEN / 2, 0), (xr if z == ANT_TOP else -FRAME_LEN / 2, z), (b, 0), vertical=True)
    sh.dim(E, (TRACK_LEN / 2, 0), (TRACK_LEN / 2, TRACK_H), (1000, 0), vertical=True)
    sh.dim(E, (DECK_LX / 2 + sx_, DECK_TOP_LOW), (DECK_LX / 2 + sx_, DECK_TOP_HIGH), (1120, 0), vertical=True)
    sh.line(E, DECK_LX / 2 + sx_ - 100, DECK_TOP_LOW, DECK_LX / 2 + sx_ + 160, DECK_TOP_LOW, "PHANTOM")
    sh.text(E[0] + 1180, E[1] + DECK_TOP_HIGH - 60, "lift", h=3)

    F = (3400, 900)
    sh.label(F, 0, ANT_TOP + 230, "FRONT VIEW")
    sh.ground(F, -680, 680)
    for s_ in (1, -1):
        sh.rect(F, s_ * TRACK_INNER_Y, 0, s_ * TRACK_OUTER_W / 2, TRACK_H)
        sh.rect(F, s_ * (RAIL_Y - LIFT_BAR[1] / 2), LIFT_BAR_Z0 + h, s_ * (RAIL_Y + LIFT_BAR[1] / 2), LIFT_BAR_Z0 + h + LIFT_BAR[2])
        sh.rect(F, s_ * (RAIL_Y - CELL[1] / 2), LIFT_BAR_Z0 + h + LIFT_BAR[2], s_ * (RAIL_Y + CELL[1] / 2), DECK_Z0_LOW + h)
        sh.rect(F, s_ * (280 - ESTOP_BOX / 2), FRONT_BAR_Z0 - 15, s_ * (280 + ESTOP_BOX / 2), FRONT_BAR_Z0 + 55)
        sh.circle(F, s_ * 280, FRONT_BAR_Z0 + 20, 20)
        sh.rect(F, s_ * (MAST_Y - MAST_D / 2), ez1, s_ * (MAST_Y + MAST_D / 2), ANT_TOP - ANT[1], "HIDDEN")
        sh.rect(F, s_ * (MAST_Y - ANT[0] / 2), ANT_TOP - ANT[1], s_ * (MAST_Y + ANT[0] / 2), ANT_TOP)
    sh.rect(F, -(RAIL_Y + RHS_B / 2), FRAME_Z0, RAIL_Y + RHS_B / 2, FRAME_Z1)
    sh.rect(F, -FRONT_BAR[1] / 2, FRONT_BAR_Z0, FRONT_BAR[1] / 2, FRONT_BAR_Z0 + FRONT_BAR[2])
    sh.rect(F, -LIDAR[1] / 2, FRONT_BAR_Z0 + FRONT_BAR[2], LIDAR[1] / 2, FRONT_BAR_Z0 + FRONT_BAR[2] + LIDAR[2])
    sh.rect(F, -EBOX[1] / 2, EBOX_Z0, EBOX[1] / 2, ez1, "HIDDEN")
    sh.rect(F, -DECK_LY / 2, DECK_Z0_LOW + h, DECK_LY / 2, DECK_TOP_HIGH)
    sh.rect(F, -BIN[1] / 2, bz0, BIN[1] / 2, bin_top)
    sh.line(F, 0, -60, 0, bin_top + 60, "CENTER")
    sh.dim(F, (-TRACK_OUTER_W / 2, 0), (TRACK_OUTER_W / 2, 0), (0, -250))
    sh.dim(F, (-TRACK_INNER_Y, TRACK_H), (TRACK_INNER_Y, TRACK_H), (0, -130))
    sh.dim(F, (-MAST_Y, ANT_TOP), (MAST_Y, ANT_TOP), (0, ANT_TOP + 70))
    sh.dim(F, (TRACK_INNER_Y, 0), (TRACK_INNER_Y, FRAME_Z0), (700, 0), vertical=True)
    sh.text(F[0] - 130, F[1] + 160, f"{CLEARANCE} CLEAR", h=3)

    rows = ["KEY DATA",
            f"Overall L x W x H     {xf - xr:.0f} x {TRACK_OUTER_W} x {ANT_TOP} mm",
            f"Ground clearance between tracks {CLEARANCE} mm (no bumpers)",
            f"Deck top low / raised {DECK_TOP_LOW} / {DECK_TOP_HIGH} mm, bin top {bin_top} mm",
            f"Front parts ≤ {FRONT_ENVELOPE_Z:.0f} mm: robot drives under bins on stands",
            "Tall parts (E-box, GNSS masts, beacon) only at the rear",
            "Gross mass ≈ 1,020 kg; limits loaded: 25° up/down, 10° cross",
            "Undercarriage: bought, 48 V, 2 x ≥2 kW, brakes"]
    notes(sh, 200, 560, rows)
    sh.save("DWG-001_general_arrangement")


# ---------------------------------------------------------------- DWG-002
def dwg_002():
    sh = Sheet("002", "UPPER FRAME — WELDMENT (FABRICATE)")
    hb, rb = RHS_B / 2, RAIL_Y
    la = BAY_X1 - BAY_X0
    P = (1150, 1450)
    sh.label(P, 0, -820, "TOP VIEW")
    for s in (1, -1):
        sh.rect(P, -FRAME_LEN / 2, s * (rb - hb), FRAME_LEN / 2, s * (rb + hb))
        sh.rect(P, s * (END_BEAM_X - hb), -(rb - hb), s * (END_BEAM_X + hb), rb - hb)
        sh.rect(P, s * (INNER_BEAM_X - hb), -(rb - hb), s * (INNER_BEAM_X + hb), rb - hb)
        for sx in (1, -1):
            sh.rect(P, sx * BRK_X - BRK_L / 2, s * (rb + hb), sx * BRK_X + BRK_L / 2, s * (rb + hb + BRK_T))
            sh.rect(P, s * FRAME_LEN / 2, sx * TAB_Y - TAB_W / 2, s * (FRAME_LEN / 2 + TAB_T), sx * TAB_Y + TAB_W / 2)
            sh.rect(P, s * BAY_X0, sx * (rb - hb), s * BAY_X1, sx * (rb - hb - ANGLE[0]))
            for xl, _ in LINK_LOW:
                sh.rect(P, xl - 30, sx * (rb - hb), xl + 30, sx * (rb - hb - 10))
    sh.line(P, -FRAME_LEN / 2 - 80, 0, FRAME_LEN / 2 + 80, 0, "CENTER")
    sh.line(P, 0, -rb - 80, 0, rb + 80, "CENTER")
    sh.dim(P, (-FRAME_LEN / 2, -rb), (FRAME_LEN / 2, -rb), (0, -rb - 350))
    sh.dim(P, (-BRK_X, -rb - hb - BRK_T), (BRK_X, -rb - hb - BRK_T), (0, -rb - 150))
    sh.dim(P, (-INNER_BEAM_X, -rb), (INNER_BEAM_X, -rb), (0, -rb - 250))
    sh.dim(P, (LINK_LOW[1][0], rb), (LINK_LOW[0][0], rb), (0, rb + 150))
    sh.dim(P, (-FRAME_LEN / 2, -rb), (-FRAME_LEN / 2, rb), (-FRAME_LEN / 2 - 150, 0), vertical=True)
    sh.dim(P, (-FRAME_LEN / 2, -(rb + hb)), (-FRAME_LEN / 2, rb + hb), (-FRAME_LEN / 2 - 260, 0), vertical=True)
    sh.dim(P, (FRAME_LEN / 2 + TAB_T, -TAB_Y), (FRAME_LEN / 2 + TAB_T, TAB_Y), (FRAME_LEN / 2 + 150, 0), vertical=True)
    sh.text(P[0] + LINK_LOW[1][0] - 60, P[1] + rb + 230, "link pivots", h=2.8)
    for n, (u, v, du, dv) in enumerate([(-200, rb + hb, -60, 300), (END_BEAM_X, 150, 160, 330),
                                        (INNER_BEAM_X, 150, 60, 300), (-BRK_X, rb + hb + BRK_T, -40, 300),
                                        (FRAME_LEN / 2 + TAB_T, -TAB_Y, 150, -100), (460, -rb + hb + 20, 60, 160),
                                        (LINK_LOW[0][0], -rb + hb + 5, 0, 200)], start=1):
        sh.balloon(P, u, v, du, dv, n)
    for s in (1, -1):
        sh.text(P[0] + s * 462 - 110, P[1] - 15, "battery bay", h=2.5)
    sh.text(P[0] - 120, P[1] + 160, "actuators", h=2.5)

    E = (1150, 2050)
    sh.label(E, 0, 640, "SIDE VIEW")
    sh.ground(E, -800, 800)
    sh.rect(E, -FRAME_LEN / 2, FRAME_Z0, FRAME_LEN / 2, FRAME_Z1)
    for s in (1, -1):
        for xx in (END_BEAM_X - hb, INNER_BEAM_X - hb, INNER_BEAM_X + hb):
            sh.line(E, s * xx, FRAME_Z0, s * xx, FRAME_Z1, "HIDDEN")
        sh.rect(E, s * BRK_X - BRK_L / 2, BRK_Z0, s * BRK_X + BRK_L / 2, BRK_Z0 + BRK_H)
        for du in (-BRK_PITCH_X / 2, BRK_PITCH_X / 2):
            for dv in (-BRK_PITCH_Z / 2, BRK_PITCH_Z / 2):
                sh.circle(E, s * BRK_X + du, BRK_Z0 + BRK_H / 2 + dv, BRK_HOLE / 2)
        sh.rect(E, s * FRAME_LEN / 2, FRAME_Z0 + (RHS_H - TAB_H) / 2, s * (FRAME_LEN / 2 + TAB_T), FRAME_Z0 + (RHS_H + TAB_H) / 2)
    for xl, zl in LINK_LOW:
        sh.rect(E, xl - 30, zl - 35, xl + 30, zl + 35, "HIDDEN")
        sh.circle(E, xl, zl, 10, "HIDDEN")
    sh.dim(E, (FRAME_LEN / 2, 0), (FRAME_LEN / 2, FRAME_Z0), (FRAME_LEN / 2 + 120, 0), vertical=True)
    sh.dim(E, (FRAME_LEN / 2, FRAME_Z0), (FRAME_LEN / 2, FRAME_Z1), (FRAME_LEN / 2 + 220, 0), vertical=True)
    sh.dim(E, (BRK_X - BRK_L / 2, BRK_Z0 + BRK_H), (BRK_X + BRK_L / 2, BRK_Z0 + BRK_H), (BRK_X, BRK_Z0 + BRK_H + 90))
    sh.dim(E, (BRK_X - BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2),
           (BRK_X + BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2), (BRK_X, BRK_Z0 + BRK_H + 190))
    sh.dim(E, (-BRK_X - BRK_L / 2, BRK_Z0 + BRK_H / 2 - BRK_PITCH_Z / 2), (-BRK_X - BRK_L / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2),
           (-BRK_X - 170, 0), vertical=True)
    sh.dim(E, (LINK_LOW[1][0], 0), (LINK_LOW[1][0], LINK_LOW[1][1]), (LINK_LOW[1][0] - 120, 0), vertical=True)
    sh.text(E[0] + BRK_X - 90, E[1] + BRK_Z0 - 90, "4x Ø18 (M16)", h=3)
    sh.text(E[0] + LINK_LOW[1][0] - 60, E[1] + FRAME_Z1 + 40, "pivot Ø20", h=2.5)

    F = (3100, 2050)
    sh.label(F, 0, 640, "FRONT VIEW")
    sh.ground(F, -500, 500)
    sh.rect(F, -(rb + hb), FRAME_Z0, rb + hb, FRAME_Z1)
    for s in (1, -1):
        sh.line(F, s * (rb - hb), FRAME_Z0, s * (rb - hb), FRAME_Z1)
        sh.rect(F, s * (rb + hb), BRK_Z0, s * (rb + hb + BRK_T), BRK_Z0 + BRK_H)
        sh.rect(F, s * TAB_Y - TAB_W / 2, FRAME_Z0 + (RHS_H - TAB_H) / 2, s * TAB_Y + TAB_W / 2, FRAME_Z0 + (RHS_H + TAB_H) / 2)
        for du in (-30, 30):
            sh.circle(F, s * TAB_Y + du, FRAME_Z0 + RHS_H / 2, TAB_HOLE / 2)
    sh.dim(F, (-(rb + hb + BRK_T), BRK_Z0 + BRK_H), (rb + hb + BRK_T, BRK_Z0 + BRK_H), (0, BRK_Z0 + BRK_H + 190))
    sh.dim(F, (-(rb + hb), FRAME_Z1), (rb + hb, FRAME_Z1), (0, BRK_Z0 + BRK_H + 90))
    sh.dim(F, (rb + hb, 0), (rb + hb, FRAME_Z0), (rb + 200, 0), vertical=True)
    sh.text(F[0] + TAB_Y - 120, F[1] + FRAME_Z1 + 40, "2x Ø14", h=3)

    items = [
        (1, "Side rail", "RHS 100x50x4", FRAME_LEN, 2, m_rhs(FRAME_LEN, 50, 100, 4)),
        (2, "End cross beam", "RHS 100x50x4", BEAM_LEN, 2, m_rhs(BEAM_LEN, 50, 100, 4)),
        (3, "Inner cross beam", "RHS 100x50x4", BEAM_LEN, 2, m_rhs(BEAM_LEN, 50, 100, 4)),
        (4, "U/C bracket, 4x Ø18", f"PL {BRK_T} {BRK_L}x{BRK_H}", BRK_L, 4, BRK_T * BRK_L * BRK_H * STEEL),
        (5, "Tab (sensor bar / E-box)", f"PL {TAB_T} {TAB_W}x{TAB_H}", TAB_W, 4, TAB_T * TAB_W * TAB_H * STEEL),
        (6, "Battery support angle", f"L {ANGLE[0]}x{ANGLE[1]}", la, 4, 2 * ANGLE[0] * ANGLE[1] * la * STEEL),
        (7, "Link pivot plate, Ø20", "PL 10 60x70", 60, 8, 10 * 60 * 70 * STEEL),
    ]
    cut_list(sh, 2150, 1450, items)
    notes(sh, 160, 520, ["NOTES",
          "1. Material: RHS S355J2H (EN 10219), plate/angle S355J2. MIG, fillet a4 all round.",
          "2. Weld on a flat table, clamped. Rail tops flat within ±1 mm (lift bars run here).",
          "3. Items 4: drill to MATCH UNDERCARRIAGE DRAWING. Nothing below the rails (350 clear).",
          "4. Items 7: pivot holes line-bored in pairs (both rails together) for parallel links.",
          "5. Ø8 drain hole at the low point of every closed RHS. Deburr. Optional 8 mm corner gussets.",
          "6. Zinc-rich primer + 2-part epoxy. General tolerance ±2 mm. 4x M16 8.8 per bracket, 210 Nm."])
    sh.save("DWG-002_upper_frame_weldment")


# ---------------------------------------------------------------- DWG-003
def dwg_003():
    sh = Sheet("003", "BASE BIN STAND — ROBOT DRIVES UNDER", scale=15)
    arm = POST_Y - LEDGE_Y0
    gy = TRACK_OUTER_W / 2 + 30
    # section through the stand with the robot in both lift positions
    X = (1500, 1300)
    sh.label(X, 0, BIN[2] + LEDGE_TOP + 170, "SECTION A-A  (through bay centre, robot inside)")
    sh.ground(X, -900, 900)
    for s in (1, -1):
        sh.rect(X, s * (POST_Y - POST / 2), 0, s * (POST_Y + POST / 2), LEDGE_TOP + 300)
        sh.rect(X, s * LEDGE_Y0, LEDGE_TOP - LEDGE[2], s * (LEDGE_Y0 + LEDGE[1]), LEDGE_TOP)
        sh.rect(X, s * (LEDGE_Y0 + LEDGE[1]), LEDGE_TOP - LEDGE[2], s * (POST_Y - POST / 2), LEDGE_TOP, "HIDDEN")
        ky = LEDGE_Y0 + LEDGE[1] + 40
        sh.rect(X, s * ky, LEDGE_TOP, s * (ky + 10), LEDGE_TOP + 60)
        sh.rect(X, s * gy, 0, s * (gy + GUIDE[1]), GUIDE[2])
        # robot section (phantom)
        sh.rect(X, s * TRACK_INNER_Y, 0, s * TRACK_OUTER_W / 2, TRACK_H, "PHANTOM")
        sh.rect(X, s * (RAIL_Y - RHS_B / 2), FRAME_Z0, s * (RAIL_Y + RHS_B / 2), FRAME_Z1, "PHANTOM")
        sh.rect(X, s * (RAIL_Y - LIFT_BAR[1] / 2), LIFT_BAR_Z0, s * (RAIL_Y + LIFT_BAR[1] / 2), LIFT_BAR_Z0 + LIFT_BAR[2], "PHANTOM")
    sh.rect(X, -DECK_LY / 2, DECK_Z0_LOW, DECK_LY / 2, DECK_TOP_LOW, "PHANTOM")
    sh.rect(X, -DECK_LY / 2, DECK_Z0_LOW + LIFT_STROKE, DECK_LY / 2, DECK_TOP_HIGH, "HIDDEN")
    sh.rect(X, -BIN[1] / 2, LEDGE_TOP, BIN[1] / 2, LEDGE_TOP + BIN[2])
    sh.line(X, 0, -60, 0, LEDGE_TOP + BIN[2] + 60, "CENTER")
    sh.text(X[0] - 360, X[1] + DECK_TOP_LOW - 50, "deck low (robot phantom)", h=2.5)
    sh.text(X[0] - 300, X[1] + DECK_TOP_HIGH + 20, "deck raised (hidden)", h=2.5)
    sh.dim(X, (-POST_Y + POST / 2, 0), (POST_Y - POST / 2, 0), (0, -250))
    sh.dim(X, (-TRACK_OUTER_W / 2, TRACK_H), (TRACK_OUTER_W / 2, TRACK_H), (0, -130))
    sh.dim(X, (-LEDGE_Y0, LEDGE_TOP), (LEDGE_Y0, LEDGE_TOP), (0, LEDGE_TOP + BIN[2] + 80))
    sh.dim(X, (-DECK_LY / 2, DECK_TOP_LOW), (DECK_LY / 2, DECK_TOP_LOW), (0, 200))
    sh.dim(X, (POST_Y + POST / 2, 0), (POST_Y + POST / 2, LEDGE_TOP), (POST_Y + 160, 0), vertical=True)
    sh.dim(X, (POST_Y + POST / 2, 0), (POST_Y + POST / 2, LEDGE_TOP + 300), (POST_Y + 270, 0), vertical=True)
    sh.dim(X, (-DECK_LY / 2, DECK_TOP_LOW), (-DECK_LY / 2, LEDGE_TOP), (-POST_Y - 130, 0), vertical=True)
    sh.dim(X, (-DECK_LY / 2, LEDGE_TOP), (-DECK_LY / 2, DECK_TOP_HIGH), (-POST_Y - 230, 0), vertical=True)
    sh.dim(X, (-TRACK_OUTER_W / 2, 0), (-TRACK_OUTER_W / 2, GUIDE[2]), (-POST_Y - 130, -200), vertical=True)
    # plan
    P = (4600, 3000)
    sh.label(P, 0, POST_Y + 220, "TOP VIEW  (entry from the left = robot rear side)")
    for s in (1, -1):
        for sx in (1, -1):
            sh.rect(P, sx * POST_X - POST / 2, s * POST_Y - POST / 2, sx * POST_X + POST / 2, s * POST_Y + POST / 2)
            sh.rect(P, sx * POST_X - POST / 2, s * LEDGE_Y0, sx * POST_X + POST / 2, s * (POST_Y - POST / 2))
        sh.rect(P, -LEDGE[0] / 2, s * LEDGE_Y0, LEDGE[0] / 2, s * (LEDGE_Y0 + LEDGE[1]))
        sh.poly(P, [(-GUIDE[0] / 2 - 500, s * (gy + GUIDE_FLARE)), (-GUIDE[0] / 2, s * gy), (GUIDE[0] / 2, s * gy),
                    (GUIDE[0] / 2, s * (gy + GUIDE[1])), (-GUIDE[0] / 2, s * (gy + GUIDE[1])),
                    (-GUIDE[0] / 2 - 500, s * (gy + GUIDE_FLARE + GUIDE[1]))], close=True)
    sh.rect(P, -BIN[0] / 2, -BIN[1] / 2, BIN[0] / 2, BIN[1] / 2, "PHANTOM")
    sh.line(P, -GUIDE[0] / 2 - 600, 0, GUIDE[0] / 2 + 100, 0, "CENTER")
    sh.dim(P, (-LEDGE[0] / 2, -POST_Y), (LEDGE[0] / 2, -POST_Y), (0, -POST_Y - 140))
    sh.dim(P, (-GUIDE[0] / 2 - 500, -gy - GUIDE_FLARE - GUIDE[1]), (GUIDE[0] / 2, -gy - GUIDE[1]), (0, -POST_Y - 260))
    sh.dim(P, (GUIDE[0] / 2, -gy), (GUIDE[0] / 2, gy), (GUIDE[0] / 2 + 120, 0), vertical=True)
    sh.dim(P, (POST_X + POST / 2, -POST_Y), (POST_X + POST / 2, POST_Y), (GUIDE[0] / 2 + 250, 0), vertical=True)
    sh.text(P[0] - GUIDE[0] / 2 - 560, P[1] + gy + GUIDE_FLARE + 120, "→ robot enters", h=3)

    items = [
        (1, "Post (+ base plate 200x200x10)", "SHS 80x80x4", LEDGE_TOP + 300, 4, m_rhs(LEDGE_TOP + 300, 80, 80, 4) + 3.1),
        (2, "Ledge (laid flat)", "RHS 100x50x4", LEDGE[0], 2, m_rhs(LEDGE[0], 100, 50, 4)),
        (3, "Arm post → ledge", "RHS 80x50x4", arm, 4, m_rhs(arm, 80, 50, 4)),
        (4, "Bin keeper", "FL 60x10", LEDGE[0], 2, 60 * 10 * LEDGE[0] * STEEL),
        (5, "Track guide + 500 flare", "RHS 120x60x4", GUIDE[0] + 520, 2, m_rhs(GUIDE[0] + 520, 60, 120, 4)),
        (6, "UHMW wear strip on ledge", "PE 100x10", LEDGE[0], 2, 0.0),
    ]
    cut_list(sh, 3300, 1750, items)
    notes(sh, 240, 780, ["NOTES",
          "1. EMPTY bays as drawn. FULL bays: each post on a 1 t load cell + certified",
          "   indicator (NAWI class III) → official weight of every bin, logged by base PC.",
          "2. Open underneath and at both ends: nothing below 635 mm except the ledges.",
          "3. Concrete or compacted gravel pad, level ±10 mm. Anchor base plates with 4x M12 each.",
          "4. AprilTag on the far post pair + LiDAR reflectors for final positioning (±30 mm).",
          "5. Ledge positions to be checked against the real bin's skids before welding.",
          "6. Paint posts yellow/black. Bays 2.2 m apart (centre to centre)."])
    sh.save("DWG-003_bin_stand")


if __name__ == "__main__":
    dwg_001()
    dwg_002()
    dwg_003()
    print("ok")
