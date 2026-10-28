"""DWG-004 stability limits: tilt drawings + limit table. Writes out/DWG-004_stability.(pdf|png)."""
import datetime
from math import atan, atan2, cos, sin, radians, degrees
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from params import *

OUT = "out/"
HALF_GAUGE = TRACK_Y / 1000          # tipping edge sideways: track centre line (conservative on soft ground)
HALF_CONTACT = TRACK_CONTACT / 2000  # tipping edge fore/aft: end of the flat contact
LIFT_SHIFT = 0.082                   # deck moves forward when raised (BP-02)


def cog(bin_kg, raised=True):
    """Combined CoG (x, z) in m and total mass for a load state."""
    deck = (DECK_TOP_HIGH if raised else DECK_TOP_LOW) / 1000
    parts = [(M_BASE, 0.0, Z_BASE), (M_TOP, X_TOP, Z_TOP)]
    if bin_kg:
        olives = bin_kg - M_BIN
        parts.append((M_BIN, LIFT_SHIFT if raised else 0, deck + BIN[2] / 2000))
        if olives > 0:
            fill = BIN[2] / 1000 * olives / M_OLIVES            # olive height grows with weight
            parts.append((olives, LIFT_SHIFT if raised else 0, deck + 0.05 + fill / 2))
    m = sum(p[0] for p in parts)
    return sum(p[0] * p[1] for p in parts) / m, sum(p[0] * p[2] for p in parts) / m, m


def limits(bin_kg, raised=True):
    x, z, m = cog(bin_kg, raised)
    side = degrees(atan(HALF_GAUGE / z))
    down = degrees(atan((HALF_CONTACT - x) / z))      # nose-down (going downhill): front edge
    up = degrees(atan((HALF_CONTACT + x) / z))        # nose-up (climbing): rear edge
    return dict(x=x, z=z, m=m, side=side, down=down, up=up,
                side_op=min(20, round(side * 0.3)), fore_op=min(25, round(min(down, up) - 11)))


# ---------------------------------------------------------------- drawing helpers
def rot(pts, a, cx=0, cz=0):
    c, s = cos(a), sin(a)
    return [(cx + (x - cx) * c - (z - cz) * s, cz + (x - cx) * s + (z - cz) * c) for x, z in pts]


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def front_shapes(bin_kg, raised):
    """Robot seen from the front (y horizontal, mm)."""
    d = DECK_TOP_HIGH if raised else DECK_TOP_LOW
    sh = []
    for s in (1, -1):
        sh.append((rect(s * TRACK_INNER_Y, 0, s * TRACK_OUTER_W / 2, TRACK_H), "#3a3a3a"))
    sh.append((rect(-BASE_BODY[1] / 2, BASE_CLEARANCE, BASE_BODY[1] / 2, BASE_CLEARANCE + BASE_BODY[2]), "#555"))
    sh.append((rect(-BASE_PLATE[1] / 2, BASE_TOP - BASE_PLATE[2], BASE_PLATE[1] / 2, BASE_TOP), "#666"))
    sh.append((rect(-(RAIL_Y + RHS_B / 2), FRAME_Z0, RAIL_Y + RHS_B / 2, FRAME_Z1), "#2f6b3f"))
    lb = d - DECK_H - CELL[2] - LIFT_BAR[2]
    for s in (1, -1):
        sh.append((rect(s * RAIL_Y - LIFT_BAR[1] / 2, lb, s * RAIL_Y + LIFT_BAR[1] / 2, lb + LIFT_BAR[2]), "#e39b1f"))
        sh.append((rect(s * RAIL_Y - CELL[1] / 2, lb + LIFT_BAR[2], s * RAIL_Y + CELL[1] / 2, d - DECK_H), "#3477c4"))
        sh.append((rect(s * RAIL_Y - 10, FRAME_Z1, s * RAIL_Y + 10, lb), "#333"))
    sh.append((rect(-DECK_LY / 2, d - DECK_H, DECK_LY / 2, d), "#e39b1f"))
    if bin_kg:
        sh.append((rect(-BIN[1] / 2, d, BIN[1] / 2, d + BIN[2]), "#bcd6ee"))
        olives = bin_kg - M_BIN
        if olives > 0:
            fill = BIN[2] * olives / M_OLIVES
            sh.append((rect(-BIN[1] / 2 + 30, d + 30, BIN[1] / 2 - 30, d + 30 + fill - 40), "#5b4a6b"))
    return sh


def side_shapes(bin_kg, raised):
    """Robot seen from the side (x horizontal, front to the right, mm)."""
    d = DECK_TOP_HIGH if raised else DECK_TOP_LOW
    sx = LIFT_SHIFT * 1000 if raised else 0
    sh = []
    r = TRACK_H / 2
    trk = [(-TRACK_LEN / 2 + r + r * cos(radians(a)), r + r * sin(radians(a))) for a in range(90, 271, 15)]
    trk += [(TRACK_LEN / 2 - r + r * cos(radians(a)), r + r * sin(radians(a))) for a in range(-90, 91, 15)]
    sh.append((trk, "#3a3a3a"))
    sh.append((rect(-BASE_PLATE[0] / 2, BASE_TOP - BASE_PLATE[2], BASE_PLATE[0] / 2, BASE_TOP), "#666"))
    sh.append((rect(-FRAME_LEN / 2, FRAME_Z0, FRAME_LEN / 2, FRAME_Z1), "#2f6b3f"))
    sh.append((rect(EBOX_X0 - EBOX[0], EBOX_Z0, EBOX_X0, EBOX_Z0 + EBOX[2]), "#9aa0a6"))
    lb = d - DECK_H - CELL[2] - LIFT_BAR[2]
    v = lb + LIFT_BAR[2] / 2 - (FRAME_Z0 + 55)
    dx = (LINK_L ** 2 - v ** 2) ** 0.5
    for xl in (580, -345):
        sh.append(([(xl - 8, FRAME_Z0 + 55), (xl + 8, FRAME_Z0 + 55), (xl - dx + 8, FRAME_Z0 + 55 + v), (xl - dx - 8, FRAME_Z0 + 55 + v)], "#333"))
    sh.append((rect(sx - LIFT_BAR[0] / 2, lb, sx + LIFT_BAR[0] / 2, lb + LIFT_BAR[2]), "#e39b1f"))
    for c in (-CELL_X, CELL_X):
        sh.append((rect(sx + c - CELL[0] / 2, lb + LIFT_BAR[2], sx + c + CELL[0] / 2, d - DECK_H), "#3477c4"))
    sh.append((rect(sx - DECK_LX / 2, d - DECK_H, sx + DECK_LX / 2, d), "#e39b1f"))
    if bin_kg:
        sh.append((rect(sx - BIN[0] / 2, d, sx + BIN[0] / 2, d + BIN[2]), "#bcd6ee"))
        olives = bin_kg - M_BIN
        if olives > 0:
            fill = BIN[2] * olives / M_OLIVES
            sh.append((rect(sx - BIN[0] / 2 + 30, d + 30, sx + BIN[0] / 2 - 30, d + 30 + fill - 40), "#5b4a6b"))
    return sh


def panel(ax, view, angle, title, bin_kg=540, raised=True, rut=0.0, verdict=None):
    """Draw the robot tilted by `angle` (deg, positive = right side / front goes down)."""
    x, z, _ = cog(bin_kg, raised)
    shapes = front_shapes(bin_kg, raised) if view == "front" else side_shapes(bin_kg, raised)
    cg = (0.0, z * 1000) if view == "front" else (x * 1000, z * 1000)
    sgn = 1 if angle >= 0 else -1                      # which side is downhill
    edge = (sgn * TRACK_Y, 0.0) if view == "front" else (sgn * TRACK_CONTACT / 2, 0.0)
    a = radians(-angle)                                 # rotate clockwise: right / front side down
    for pts, col in shapes:
        ax.add_patch(Polygon(rot(pts, a), closed=True, fc=col, ec="black", lw=0.6))
    # ground (slope) under the tracks
    g = rot([(-2600, 0), (2600, 0)], a)
    ax.plot(*zip(*g), color="#8a7350", lw=3)
    gx = rot([(u, -60) for u in range(-2600, 2601, 120)], a)
    for (px, pz) in gx:
        ax.plot([px, px - 50], [pz, pz - 50], color="#8a7350", lw=0.6)
    if rut:
        ax.text(*rot([(TRACK_Y - 200, -260)], a)[0], f"rut {rut:.0f} mm", fontsize=7, color="#8a7350")
    # CoG and the line straight down
    c = rot([cg], a)[0]
    e = rot([edge], a)[0]
    ax.add_patch(Circle(c, 45, fc="white", ec="black", lw=1.2, zorder=5))
    ax.add_patch(Polygon([c, (c[0] + 45, c[1]), (c[0], c[1] + 45)], fc="black", zorder=6))
    ax.add_patch(Polygon([c, (c[0] - 45, c[1]), (c[0], c[1] - 45)], fc="black", zorder=6))
    stable = (c[0] < e[0] - 1) if sgn > 0 else (c[0] > e[0] + 1)
    col = "#1e8449" if stable else "#c0392b"
    ax.plot([c[0], c[0]], [c[1], -350], color=col, lw=1.4, ls="--", zorder=4)
    ax.plot(*e, marker="^", color="#c0392b", ms=9, zorder=6)
    ax.text(e[0] + 40, e[1] - 160, "tipping\nedge", fontsize=7, color="#c0392b")
    ax.set_xlim(-1900, 1900); ax.set_ylim(-500, 2100); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=10, loc="left", weight="bold")
    if verdict:
        ax.text(-1850, 1950, verdict, fontsize=8.5, va="top", color=col)


def main():
    L = {k: limits(*v) for k, v in {"full_raised": (540, True), "full_low": (540, False),
                                     "empty_raised": (40, True), "none": (0, True)}.items()}
    F = L["full_raised"]
    fig = plt.figure(figsize=(16.54, 11.69), facecolor="white")
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.62], hspace=0.12, wspace=0.02,
                          left=0.03, right=0.97, top=0.95, bottom=0.03)
    fig.suptitle("BINBOT — STABILITY LIMITS WITH A FULL BIN (500 kg olives, deck raised)", fontsize=13, weight="bold", x=0.03, ha="left")
    rut_deg = degrees(atan(0.1 / (2 * HALF_GAUGE)))
    panel(fig.add_subplot(gs[0, 0]), "front", F["side_op"],
          f"A  CROSS-SLOPE LIMIT {F['side_op']}° (driving)", verdict=f"OK: CoG well inside.\nAlarm {F['side_op'] - 2}°, auto-stop {F['side_op'] + 3}°.")
    panel(fig.add_subplot(gs[0, 1]), "front", F["side_op"] + rut_deg,
          f"B  ROAD: {F['side_op']}° CAMBER + 100 mm RUT = {F['side_op'] + rut_deg:.0f}°", rut=100,
          verdict=f"OK: still {F['side'] - F['side_op'] - rut_deg:.0f}° from tipping.\nRuts are why the limit is far below the tip angle.")
    panel(fig.add_subplot(gs[0, 2]), "front", F["side"],
          f"C  SIDEWAYS TIP POINT {F['side']:.0f}° — NEVER", verdict="CoG exactly over the edge:\nthe robot rolls over.")
    panel(fig.add_subplot(gs[1, 0]), "side", -25,
          "D  CLIMBING 25° (front up)", verdict=f"OK: tips backwards only at {F['up']:.0f}°.")
    panel(fig.add_subplot(gs[1, 1]), "side", 25,
          "E  GOING DOWN 25° (front down)", verdict=f"OK: tips forwards at {F['down']:.0f}°.\nBrake gently (0.5 m/s² ≈ 3° extra).\nRaised deck sits 82 mm forward: worst case.")
    panel(fig.add_subplot(gs[1, 2]), "side", F["down"],
          f"F  FORWARD TIP POINT {F['down']:.0f}° — NEVER", verdict="CoG over the front edge\nof the track contact.")
    # limits table
    ax = fig.add_subplot(gs[2, :2]); ax.axis("off")
    rows = [("Load state", "CoG height", "Tip sideways", "Tip fwd / back", "Cross-slope limit", "Up/down limit")]
    names = {"full_raised": "Full bin 500 kg, deck RAISED (normal)", "full_low": "Full bin 500 kg, deck LOWERED (road mode)",
             "empty_raised": "Empty bin", "none": "No bin"}
    for k, n in names.items():
        l = L[k]
        rows.append((n, f"{l['z'] * 1000:.0f} mm", f"{l['side']:.0f}°", f"{l['down']:.0f}° / {l['up']:.0f}°",
                     f"{l['side_op']}°", f"{l['fore_op']}°"))
    t = ax.table(cellText=rows[1:], colLabels=rows[0], loc="upper left", bbox=[0, 0.25, 1, 0.75], cellLoc="center", colWidths=[0.34, 0.11, 0.12, 0.13, 0.15, 0.13])
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.6)
    for (r, c), cell in t.get_celld().items():
        if r == 0:
            cell.set_facecolor("#e8e8e8"); cell.set_text_props(weight="bold")
    ax.text(0, 0.08, "Operating limits: sideways ≈ 30 % of the tip angle (ruts, bumps, turning, soft ground); up/down = tip angle − 11°\n"
                      "(3° braking + 8° bumps), capped at 20° / 25°. Sideways tipping edge taken at the track centre line (soft ground).",
            fontsize=8, transform=ax.transAxes, va="top")
    # notes + title block
    ax2 = fig.add_subplot(gs[2, 2]); ax2.axis("off")
    lo = L["full_low"]
    ax2.text(0, 1.0, "ROAD MODE (recommended)\n"
                     f"On roads and long transfers, carry the full bin with the deck LOWERED:\n"
                     f"CoG drops {(F['z'] - lo['z']) * 1000:.0f} mm, sideways tip {F['side']:.0f}° → {lo['side']:.0f}°.\n"
                     "Needs 8 kN actuators (instead of 6 kN) to lift a full bin\n"
                     "again before entering a FULL bay. +€60–100.\n\n"
                     "Masses are estimates: weigh the robot once built and\n"
                     "re-run cad/stability.py; the software limits use these values.",
             fontsize=8.5, va="top", transform=ax2.transAxes)
    ax2.text(0, 0.12, f"DWG 004   REV C   stability   {datetime.date.today():%Y-%m-%d}\nPRELIMINARY — masses estimated, base data assumed",
             fontsize=8, va="top", transform=ax2.transAxes, bbox=dict(fc="white", ec="black"))
    for ext in ("pdf", "png"):
        fig.savefig(OUT + f"DWG-004_stability.{ext}", dpi=150 if ext == "png" else None, facecolor="white")
    plt.close(fig)
    for k, l in L.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in l.items()})


if __name__ == "__main__":
    main()
