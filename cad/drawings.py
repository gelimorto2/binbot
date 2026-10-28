"""2D drawings (DXF + PDF + PNG) generated from params.py.

DWG-001  General arrangement, chassis (bin raised)        1:10 on A3
DWG-002  Upper frame weldment — fabrication drawing        1:10 on A3
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
    def __init__(self, number, title):
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.header["$LTSCALE"] = S
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
        self.msp.add_text(s, height=h * S, dxfattribs={"layer": layer}).set_placement((x, y), align=align)

    def dim(self, o, p1, p2, base, vertical=False):
        x, y = o
        d = self.msp.add_linear_dim(base=(x + base[0], y + base[1]), p1=(x + p1[0], y + p1[1]),
                                    p2=(x + p2[0], y + p2[1]), angle=90 if vertical else 0,
                                    override=DIM, dxfattribs={"layer": "DIM"})
        d.render()

    def label(self, o, u, v, s):
        self.text(o[0] + u, o[1] + v, s, h=4, align=TA.MIDDLE_CENTER)

    def balloon(self, o, u, v, du, dv, n):
        x, y = o
        r = 4 * S
        self.msp.add_line((x + u, y + v), (x + u + du, y + v + dv), dxfattribs={"layer": "TEXT"})
        self.msp.add_circle((x + u + du, y + v + dv), r, dxfattribs={"layer": "TEXT"})
        self.text(x + u + du, y + v + dv, str(n), h=3.5, align=TA.MIDDLE_CENTER)

    def ground(self, o, u0, u1):
        self.line(o, u0, 0, u1, 0, "OUTLINE")
        for u in range(int(u0), int(u1), 60):
            self.line(o, u, 0, u - 40, -40, "DIM")

    # --- sheet furniture ---
    def frame(self):
        m = 10 * S
        self.msp.add_lwpolyline([(m, m), (W - m, m), (W - m, H - m), (m, H - m)], close=True,
                                dxfattribs={"layer": "BORDER"})
        x0, y0, x1, y1 = W - m - 180 * S, m, W - m, m + 40 * S
        self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "BORDER"})
        for yy in (y0 + 10 * S, y0 + 20 * S, y0 + 30 * S):
            self.msp.add_line((x0, yy), (x1, yy), dxfattribs={"layer": "BORDER"})
        self.text(x0 + 3 * S, y1 - 7.5 * S, "BINBOT — autonomous olive bin carrier", h=4.5)
        self.text(x0 + 3 * S, y1 - 17.5 * S, self.title, h=4.5)
        self.text(x0 + 3 * S, y0 + 12.5 * S, f"DWG {self.number}   REV A   SCALE 1:10 (A3)   UNITS mm", h=3.5)
        self.text(x0 + 3 * S, y0 + 2.5 * S,
                  f"PRELIMINARY — undercarriage values assumed   {datetime.date.today():%Y-%m-%d}", h=3.5)

    def save(self, name):
        self.doc.saveas(OUT + name + ".dxf")
        for ext in ("pdf", "png"):
            dm.qsave(self.msp, OUT + f"{name}.{ext}", bg="#FFFFFF", fg="#000000", dpi=150 if ext == "png" else 300,
                     size_inches=(16.54, 11.69))


def stadium(L, Hh):
    """Track outline in side view: bottom/top straights joined by half circles."""
    a, r = L / 2 - Hh / 2, Hh / 2
    return [(-a, 0, 0), (a, 0, 1), (a, Hh, 0), (-a, Hh, 1)]


# ---------------------------------------------------------------- DWG-001
def dwg_001():
    sh = Sheet("001", "GENERAL ARRANGEMENT — CHASSIS, BIN RAISED")
    lift = LIFT_STROKE
    bz0 = DECK_TOP_HIGH
    bin_top = bz0 + BIN[2]

    # side elevation (x, z)
    E = (1450, 1000)
    sh.label(E, 0, bin_top + 180, "SIDE VIEW")
    sh.ground(E, -1000, 1000)
    sh.poly(E, stadium(TRACK_LEN, TRACK_H))
    sh.rect(E, -FRAME_LEN / 2, FRAME_Z0, FRAME_LEN / 2, FRAME_Z1, "HIDDEN")
    sh.rect(E, -BATT[0] / 2, TRAY_Z0 + TRAY_T, BATT[0] / 2, TRAY_Z0 + TRAY_T + BATT[2], "HIDDEN")
    sh.rect(E, -(FRAME_LEN - 100) / 2, FRAME_Z1 + lift, (FRAME_LEN - 100) / 2, FRAME_Z1 + lift + LIFT_BAR)
    for sx in (1, -1):
        sh.rect(E, sx * CELL_X - CELL[0] / 2, FRAME_Z1 + LIFT_BAR + lift, sx * CELL_X + CELL[0] / 2, DECK_Z0_LOW + lift)
    sh.rect(E, -DECK_LX / 2, DECK_Z0_LOW + lift, DECK_LX / 2, DECK_TOP_HIGH)
    sh.rect(E, -BIN[0] / 2, bz0, BIN[0] / 2, bin_top)
    sh.line(E, 0, -60, 0, bin_top + 60, "CENTER")
    cog = 750
    sh.circle(E, 0, cog, 40)
    sh.line(E, -60, cog, 60, cog), sh.line(E, 0, cog - 60, 0, cog + 60)
    sh.text(E[0] + 70, E[1] + cog + 20, "CoG ≈ 750 (full 500 kg, raised)", h=3)
    sh.text(E[0] - 950, E[1] - 140, "FRONT →  (x+)", h=3)
    sh.dim(E, (-TRACK_LEN / 2, TRACK_H / 2), (TRACK_LEN / 2, TRACK_H / 2), (0, -250))
    sh.dim(E, (-TRACK_CONTACT / 2, 0), (TRACK_CONTACT / 2, 0), (0, -130))
    sh.dim(E, (-BIN[0] / 2, bin_top), (BIN[0] / 2, bin_top), (0, bin_top + 90))
    for z, b in ((TRACK_H, -1000), (DECK_TOP_HIGH, -1120), (bin_top, -1240)):
        sh.dim(E, (-TRACK_LEN / 2 if z == TRACK_H else -BIN[0] / 2, 0), (-TRACK_LEN / 2 if z == TRACK_H else -BIN[0] / 2, z),
               (b, 0), vertical=True)
    sh.dim(E, (FRAME_LEN / 2, 0), (FRAME_LEN / 2, FRAME_Z0), (1000, 0), vertical=True)
    sh.dim(E, (DECK_LX / 2, DECK_TOP_HIGH - LIFT_STROKE), (DECK_LX / 2, DECK_TOP_HIGH), (1120, 0), vertical=True)
    sh.line(E, DECK_LX / 2 - 100, DECK_TOP_LOW, DECK_LX / 2 + 150, DECK_TOP_LOW, "PHANTOM")
    sh.text(E[0] + 1180, E[1] + DECK_TOP_HIGH - 60, "lift", h=3)

    # end view (y, z) from the front
    F = (3350, 1000)
    sh.label(F, 0, bin_top + 180, "FRONT VIEW")
    sh.ground(F, -680, 680)
    for s in (1, -1):
        sh.rect(F, s * TRACK_INNER_Y, 0, s * TRACK_OUTER_W / 2, TRACK_H)
        sh.rect(F, s * (RAIL_Y - LIFT_BAR / 2), FRAME_Z1 + lift, s * (RAIL_Y + LIFT_BAR / 2), FRAME_Z1 + lift + LIFT_BAR)
        sh.rect(F, s * (RAIL_Y - CELL[1] / 2), FRAME_Z1 + LIFT_BAR + lift, s * (RAIL_Y + CELL[1] / 2), DECK_Z0_LOW + lift)
    sh.rect(F, -(RAIL_Y + RHS_B / 2), FRAME_Z0, RAIL_Y + RHS_B / 2, FRAME_Z1)
    sh.rect(F, -BATT[1] / 2, TRAY_Z0 + TRAY_T, BATT[1] / 2, TRAY_Z0 + TRAY_T + BATT[2], "HIDDEN")
    sh.rect(F, -DECK_LY / 2, DECK_Z0_LOW + lift, DECK_LY / 2, DECK_TOP_HIGH)
    sh.rect(F, -BIN[1] / 2, bz0, BIN[1] / 2, bin_top)
    sh.line(F, 0, -60, 0, bin_top + 60, "CENTER")
    sh.dim(F, (-TRACK_OUTER_W / 2, 0), (TRACK_OUTER_W / 2, 0), (0, -250))
    sh.dim(F, (-TRACK_Y, TRACK_H), (TRACK_Y, TRACK_H), (0, -130))
    sh.dim(F, (-BIN[1] / 2, bin_top), (BIN[1] / 2, bin_top), (0, bin_top + 90))
    for s in (1, -1):
        sh.line(F, s * TRACK_Y, -40, s * TRACK_Y, TRACK_H + 40, "CENTER")

    # key data
    x, y = 200, 620
    rows = ["KEY DATA",
            f"Overall L x W x H     {TRACK_LEN} x {TRACK_OUTER_W} x {bin_top} mm",
            f"Track contact / gauge {TRACK_CONTACT} / {2 * TRACK_Y:.0f} mm",
            f"Deck top low / raised {DECK_TOP_LOW} / {DECK_TOP_HIGH} mm",
            f"Frame ground clearance {FRAME_Z0} mm",
            "Gross mass ≈ 960 kg (robot 420 + bin 540)",
            "Limits loaded: 25° up/down, 10° cross-slope",
            "Undercarriage: bought, 48 V, 2 x ≥2 kW, brakes"]
    for i, r in enumerate(rows):
        sh.text(x, y - i * 65, r, h=3.2 if i else 4.5)
    sh.save("DWG-001_general_arrangement")


# ---------------------------------------------------------------- DWG-002
def dwg_002():
    sh = Sheet("002", "UPPER FRAME — WELDMENT (FABRICATE)")
    hb, rb = RHS_B / 2, RAIL_Y

    # plan view (x, y)
    P = (1150, 1450)
    sh.label(P, 0, -820, "TOP VIEW")
    for s in (1, -1):
        sh.rect(P, -FRAME_LEN / 2, s * (rb - hb), FRAME_LEN / 2, s * (rb + hb))
        sh.rect(P, s * (END_BEAM_X - hb), -(rb - hb), s * (END_BEAM_X + hb), rb - hb)
        sh.rect(P, s * (INNER_BEAM_X - hb), -(rb - hb), s * (INNER_BEAM_X + hb), rb - hb)
        x0, x1 = (BAY_X0, BAY_X1) if s > 0 else (-BAY_X1, -BAY_X0)
        y0, y1 = (BRACE_Y0, BRACE_Y1) if s > 0 else (BRACE_Y1, BRACE_Y0)
        sh.poly(P, [(x0, y0 - BRACE_DY), (x1, y1 - BRACE_DY), (x1, y1 + BRACE_DY), (x0, y0 + BRACE_DY)])
        for sx in (1, -1):
            sh.rect(P, sx * BRK_X - BRK_L / 2, s * (rb + hb), sx * BRK_X + BRK_L / 2, s * (rb + hb + BRK_T))
            sh.rect(P, s * FRAME_LEN / 2, sx * TAB_Y - TAB_W / 2, s * (FRAME_LEN / 2 + TAB_T), sx * TAB_Y + TAB_W / 2)
            hx = s * (INNER_BEAM_X - hb)
            sh.rect(P, hx, sx * HANGER_Y - HANGER_W / 2, hx - s * HANGER_T, sx * HANGER_Y + HANGER_W / 2)
    sh.rect(P, -TRAY_LX / 2, -TRAY_LY / 2, TRAY_LX / 2, TRAY_LY / 2, "HIDDEN")
    sh.line(P, -FRAME_LEN / 2 - 80, 0, FRAME_LEN / 2 + 80, 0, "CENTER")
    sh.line(P, 0, -rb - 80, 0, rb + 80, "CENTER")
    sh.dim(P, (-FRAME_LEN / 2, -rb), (FRAME_LEN / 2, -rb), (0, -rb - 350))
    sh.dim(P, (-BRK_X, -rb - hb - BRK_T), (BRK_X, -rb - hb - BRK_T), (0, -rb - 150))
    sh.dim(P, (-INNER_BEAM_X, -rb), (INNER_BEAM_X, -rb), (0, -rb - 250))
    sh.dim(P, (-FRAME_LEN / 2, -rb), (-FRAME_LEN / 2, rb), (-FRAME_LEN / 2 - 150, 0), vertical=True)
    sh.dim(P, (-FRAME_LEN / 2, -(rb + hb)), (-FRAME_LEN / 2, rb + hb), (-FRAME_LEN / 2 - 260, 0), vertical=True)
    sh.dim(P, (FRAME_LEN / 2 + TAB_T, -TAB_Y), (FRAME_LEN / 2 + TAB_T, TAB_Y), (FRAME_LEN / 2 + 150, 0), vertical=True)
    for n, (u, v, du, dv) in enumerate([(-200, rb + hb, -60, 140), (END_BEAM_X, 150, 160, 330),
                                        (INNER_BEAM_X, 150, 60, 300), (460, 100, 140, 330),
                                        (-BRK_X, rb + hb + BRK_T, -40, 140), (FRAME_LEN / 2 + TAB_T, -TAB_Y, 150, -100),
                                        (100, -100, 120, -60), (-(INNER_BEAM_X - hb) + 4, HANGER_Y, 90, -40)], start=1):
        sh.balloon(P, u, v, du, dv, n)

    # side elevation (x, z)
    E = (1150, 2150)
    sh.label(E, 0, 650, "SIDE VIEW")
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
        hx = s * (INNER_BEAM_X - hb)
        sh.rect(E, hx, TRAY_Z0, hx - s * HANGER_T, FRAME_Z0)
    sh.rect(E, -TRAY_LX / 2, TRAY_Z0, TRAY_LX / 2, TRAY_Z0 + TRAY_T)
    sh.dim(E, (FRAME_LEN / 2, 0), (FRAME_LEN / 2, FRAME_Z0), (FRAME_LEN / 2 + 120, 0), vertical=True)
    sh.dim(E, (FRAME_LEN / 2, FRAME_Z0), (FRAME_LEN / 2, FRAME_Z1), (FRAME_LEN / 2 + 120, 0), vertical=True)
    sh.dim(E, (-TRAY_LX / 2, 0), (-TRAY_LX / 2, TRAY_Z0), (-FRAME_LEN / 2 - 120, 0), vertical=True)
    sh.dim(E, (BRK_X - BRK_L / 2, BRK_Z0 + BRK_H), (BRK_X + BRK_L / 2, BRK_Z0 + BRK_H), (BRK_X, BRK_Z0 + BRK_H + 90))
    sh.dim(E, (BRK_X - BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2),
           (BRK_X + BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2), (BRK_X, BRK_Z0 + BRK_H + 190))
    sh.dim(E, (-BRK_X + BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 - BRK_PITCH_Z / 2),
           (-BRK_X + BRK_PITCH_X / 2, BRK_Z0 + BRK_H / 2 + BRK_PITCH_Z / 2), (-BRK_X + 150, 0), vertical=True)
    sh.dim(E, (-BRK_X - BRK_L / 2, BRK_Z0), (-BRK_X - BRK_L / 2, BRK_Z0 + BRK_H), (-BRK_X - 170, 0), vertical=True)
    sh.text(E[0] + BRK_X - 90, E[1] + BRK_Z0 - 90, "4x Ø18 (M16)", h=3)

    # end view (y, z)
    F = (3100, 2150)
    sh.label(F, 0, 650, "FRONT VIEW")
    sh.ground(F, -500, 500)
    sh.rect(F, -(rb + hb), FRAME_Z0, rb + hb, FRAME_Z1)
    for s in (1, -1):
        sh.line(F, s * (rb - hb), FRAME_Z0, s * (rb - hb), FRAME_Z1)
        sh.rect(F, s * (rb + hb), BRK_Z0, s * (rb + hb + BRK_T), BRK_Z0 + BRK_H)
        sh.rect(F, s * TAB_Y - TAB_W / 2, FRAME_Z0 + (RHS_H - TAB_H) / 2, s * TAB_Y + TAB_W / 2, FRAME_Z0 + (RHS_H + TAB_H) / 2)
        for du in (-30, 30):
            sh.circle(F, s * TAB_Y + du, FRAME_Z0 + RHS_H / 2, TAB_HOLE / 2)
        sh.rect(F, s * HANGER_Y - HANGER_W / 2, TRAY_Z0, s * HANGER_Y + HANGER_W / 2, FRAME_Z0)
    sh.rect(F, -TRAY_LY / 2, TRAY_Z0, TRAY_LY / 2, TRAY_Z0 + TRAY_T)
    sh.dim(F, (-(rb + hb + BRK_T), BRK_Z0 + BRK_H), (rb + hb + BRK_T, BRK_Z0 + BRK_H), (0, BRK_Z0 + BRK_H + 190))
    sh.dim(F, (-(rb + hb), FRAME_Z1), (rb + hb, FRAME_Z1), (0, BRK_Z0 + BRK_H + 90))
    sh.dim(F, (-TRAY_LY / 2, TRAY_Z0), (TRAY_LY / 2, TRAY_Z0), (0, TRAY_Z0 - 120))
    sh.text(F[0] + TAB_Y - 120, F[1] + FRAME_Z1 + 60, "2x Ø14", h=3)

    # cut list
    def m_rhs(L, b, h, t):
        return (b * h - (b - 2 * t) * (h - 2 * t)) * L * STEEL

    items = [
        (1, "Side rail", "RHS 100x50x4", FRAME_LEN, 2, m_rhs(FRAME_LEN, 50, 100, 4)),
        (2, "End cross beam", "RHS 100x50x4", BEAM_LEN, 2, m_rhs(BEAM_LEN, 50, 100, 4)),
        (3, "Inner cross beam", "RHS 100x50x4", BEAM_LEN, 2, m_rhs(BEAM_LEN, 50, 100, 4)),
        (4, "Diagonal brace, cut to fit", "RHS 60x60x4", BRACE_LEN, 2, m_rhs(BRACE_LEN, 60, 60, 4)),
        (5, "U/C bracket, 4x Ø18", f"PL {BRK_T} {BRK_L}x{BRK_H}", BRK_L, 4, BRK_T * BRK_L * BRK_H * STEEL),
        (6, "Bumper tab, 2x Ø14", f"PL {TAB_T} {TAB_W}x{TAB_H}", TAB_W, 4, TAB_T * TAB_W * TAB_H * STEEL),
        (7, "Battery tray", f"PL {TRAY_T} {TRAY_LX:.0f}x{TRAY_LY}", TRAY_LX, 1, TRAY_T * TRAY_LX * TRAY_LY * STEEL),
        (8, "Tray hanger", f"FL {HANGER_W}x{HANGER_T}", HANGER_LEN, 4, HANGER_W * HANGER_T * HANGER_LEN * STEEL),
    ]
    x, y = 2150, 1450
    sh.text(x, y, "CUT LIST", h=4.5)
    sh.text(x, y - 80, "#   Part                         Section          L mm   Qty   kg", h=3.2)
    total = 0
    for i, (n, part, sec, L, q, m) in enumerate(items):
        total += m * q
        sh.text(x, y - 150 - i * 62, f"{n:<3} {part:<28} {sec:<16} {L:>5.0f}  {q:>3}  {m * q:>5.1f}", h=3.2)
    sh.text(x, y - 150 - len(items) * 62, f"{'':<52}TOTAL ≈ {total:.0f} kg", h=3.2)

    notes = ["NOTES",
             "1. Material: RHS S355J2H (EN 10219), plate/flat S355J2. S235 only with next size up.",
             "2. MIG weld, fillet a4 all round unless noted. Weld frame on a flat table, clamped.",
             "3. Top faces of items 1 flat within ±1 mm (lift + load cells sit here, BP-02).",
             "4. Items 5: drill to MATCH UNDERCARRIAGE DRAWING; shim gap to track frame.",
             "5. Ø8 drain hole at the low point of every closed RHS. Deburr all edges.",
             "6. Zinc-rich primer + 2-part epoxy. General tolerance ±2 mm.",
             "7. Frame bolts to undercarriage with 4x M16 8.8 per bracket, torque 210 Nm."]
    for i, r in enumerate(notes):
        sh.text(160, 520 - i * 60, r, h=3.2 if i else 4.5)
    sh.save("DWG-002_upper_frame_weldment")
    return total


if __name__ == "__main__":
    dwg_001()
    print("frame mass kg:", round(dwg_002(), 1))
