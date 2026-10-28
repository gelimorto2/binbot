"""Animation of the bin swap at the base (BP-02). Writes out/bin_swap.mp4 and out/bin_swap.gif.

Everything is drawn to scale from params.py. Left: side view of the bay in use.
Right: cross-section through the bay centre. Bottom right: top view of the base.
"""
from math import cos, sin, radians, hypot
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Circle
from params import *

OUT = "out/"
FPS = 20

# ---------------------------------------------------------------- lift kinematics (same as model.py)
LINK_V0 = (LIFT_BAR_Z0 + LIFT_BAR[2] / 2) - (FRAME_Z0 + 55)
LINK_LOW = [(580.0, FRAME_Z0 + 55), (-345.0, FRAME_Z0 + 55)]
DX0 = (LINK_L ** 2 - LINK_V0 ** 2) ** 0.5


def shift(h):
    return DX0 - (LINK_L ** 2 - (LINK_V0 + h) ** 2) ** 0.5


SH = shift(LIFT_STROKE)
YF, YE = 1100, -1100                       # lane centres in the top view

C = dict(track="#3a3a3a", frame="#2f6b3f", lift="#e39b1f", deck="#e39b1f", bin="#bcd6ee", olives="#5b4a6b",
         stand="#7d8590", ledge="#4c5560", ebox="#9aa0a6", ground="#8a7350", text="#111111", accent="#c0392b")

# ---------------------------------------------------------------- timeline
STEPS = [  # (start, end, title, caption)
    (0, 5, "1  ARRIVE", "Back from the grove with a full bin (up to 500 kg). Deck raised: bin bottom at 685 mm."),
    (5, 10, "2  DRIVE IN — FULL BAY", "Ground guides centre the tracks. The bin passes 50 mm ABOVE the ledges (635 mm)."),
    (10, 14, "3  LOWER", "Deck goes down 100 mm. At −50 mm the bin lands on the ledges. The bay stands on a\ncertified scale → official weight. Robot creeps 82 mm so the bin goes straight down."),
    (14, 19, "4  REVERSE OUT", "Deck down: everything at the front is lower than the bin. Only the rear (E-box, masts)\nis tall, and the rear never goes under a bin."),
    (19, 23, "5  CHANGE LANE", "Turns and lines up with the EMPTY bay next door."),
    (23, 28, "6  DRIVE IN — EMPTY BAY", "Deck down: 50 mm under the empty bin. Same guides, same low front."),
    (28, 31, "7  LIFT", "Deck rises 100 mm: the bin lifts 50 mm off the ledges. Robot reverses 82 mm during the lift\nso the bin goes straight up. Tare weight recorded."),
    (31, 36, "8  DRIVE OUT FORWARD", "The bay is open at the front: the robot leaves with the empty bin and returns to the harvesters."),
    (36, 41, "DONE  ~3 min, nobody needed", "Speed at the base 0.3 m/s · LiDAR + rear camera · E-stops · scale log sent to the farmer."),
]
T_END = STEPS[-1][1]


def ease(a):
    a = min(max(a, 0.0), 1.0)
    return a * a * (3 - 2 * a)


def lerp(a, b, t):
    return a + (b - a) * t


def state(t):
    """Robot state: lane, X (side view), lift h, full/empty bin positions, top-view pose."""
    s = dict(lane="FULL", X=0.0, h=LIFT_STROKE, full_on_robot=True, empty_on_robot=False, pose=None, show=True, kg=None)
    if t < 5:
        s["X"] = lerp(-3300, -2300, ease(t / 5))
    elif t < 10:
        s["X"] = lerp(-2300, -SH, ease((t - 5) / 5))
    elif t < 14:
        h = lerp(LIFT_STROKE, 0, ease((t - 10) / 4))
        s.update(h=h, X=-shift(h))
        s["full_on_robot"] = h >= 50
        if h < 50:
            s["kg"] = 512.4 * min(1, (50 - h) / 20)
    elif t < 19:
        s.update(h=0, X=lerp(0, -2600, ease((t - 14) / 5)), full_on_robot=False, kg=512.4)
    elif t < 23:
        s.update(h=0, full_on_robot=False, kg=512.4)
        a = (t - 19) / 4
        if a < 0.3:
            s["X"] = lerp(-2600, -4200, ease(a / 0.3)); s["lane"] = "FULL"
        elif a < 0.6:
            s["show"] = False; s["lane"] = "EMPTY"; s["X"] = -4200
        else:
            s["lane"] = "EMPTY"; s["X"] = lerp(-4200, -2600, ease((a - 0.6) / 0.4))
    elif t < 28:
        s.update(lane="EMPTY", h=0, X=lerp(-2600, 0, ease((t - 23) / 5)), full_on_robot=False, kg=512.4)
    elif t < 31:
        h = lerp(0, LIFT_STROKE, ease((t - 28) / 3))
        s.update(lane="EMPTY", h=h, X=-shift(h), full_on_robot=False, empty_on_robot=h >= 50, kg=512.4)
    else:
        s.update(lane="EMPTY", h=LIFT_STROKE, X=lerp(-SH, 3200, ease((t - 31) / 5)), full_on_robot=False,
                 empty_on_robot=True, kg=512.4)
    # top-view pose (x, y, heading deg)
    if s["lane"] == "FULL" and s["show"]:
        s["pose"] = (s["X"], YF, 0)
    elif s["lane"] == "EMPTY" and s["show"] and not (19 <= t < 23):
        s["pose"] = (s["X"], YE, 0)
    else:  # turning manoeuvre in the yard
        a = (t - 19) / 4
        if a < 0.3:
            s["pose"] = (lerp(-2600, -4200, ease(a / 0.3)), YF, 0)
        elif a < 0.6:
            b = ease((a - 0.3) / 0.3)
            s["pose"] = (-4200, lerp(YF, YE, b), -90 * sin(np.pi * b))
        else:
            s["pose"] = (lerp(-4200, -2600, ease((a - 0.6) / 0.4)), YE, 0)
    return s


# ---------------------------------------------------------------- drawing helpers
def rect(ax, x0, z0, x1, z1, fc, ec="black", lw=0.8, alpha=1.0, ls="-", z=2):
    ax.add_patch(Rectangle((min(x0, x1), min(z0, z1)), abs(x1 - x0), abs(z1 - z0), fc=fc, ec=ec, lw=lw, alpha=alpha, ls=ls, zorder=z))


def stadium(ax, x0, x1, h, fc):
    ax.add_patch(FancyBboxPatch((x0 + h / 2, 0 + 0.01), x1 - x0 - h, h - 0.02, boxstyle=f"round,pad=0,rounding_size={h / 2}",
                                mutation_aspect=1, fc=fc, ec="black", lw=0.8, zorder=3))
    ax.add_patch(Circle((x0 + h / 2, h / 2), h / 2, fc=fc, ec="black", lw=0.8, zorder=3))
    ax.add_patch(Circle((x1 - h / 2, h / 2), h / 2, fc=fc, ec="black", lw=0.8, zorder=3))
    rect(ax, x0 + h / 2, 0, x1 - h / 2, h, fc, ec="none", z=3)
    ax.plot([x0 + h / 2, x1 - h / 2], [0, 0], color="black", lw=0.8, zorder=3)
    ax.plot([x0 + h / 2, x1 - h / 2], [h, h], color="black", lw=0.8, zorder=3)


def draw_bin(ax, xc, zb, w, full, side=True):
    rect(ax, xc - w / 2, zb, xc + w / 2, zb + BIN[2], C["bin"], z=6)
    if full:
        rect(ax, xc - w / 2 + BIN_WALL, zb + BIN_WALL, xc + w / 2 - BIN_WALL, zb + BIN[2] - 40, C["olives"], ec="none", z=6)
    ax.text(xc, zb + BIN[2] / 2, "FULL\n500 kg" if full else "EMPTY", ha="center", va="center", fontsize=8,
            color="white" if full else "black", zorder=7, weight="bold")


def draw_robot_side(ax, X, h):
    stadium(ax, X - TRACK_LEN / 2, X + TRACK_LEN / 2, TRACK_H, C["track"])
    rect(ax, X - FRAME_LEN / 2, FRAME_Z0, X + FRAME_LEN / 2, FRAME_Z1, C["frame"], z=4)
    for s_ in (1, -1):
        rect(ax, X + s_ * BAY_X0, BATT_Z0, X + s_ * (BAY_X0 + BATT_PACK[0]), BATT_Z0 + BATT_PACK[2], "#c0392b", alpha=0.35, ls="--", z=4)
    sh = shift(h)
    v = LINK_V0 + h
    dx = (LINK_L ** 2 - v ** 2) ** 0.5
    for xl, zl in LINK_LOW:
        ax.plot([X + xl, X + xl - dx], [zl, zl + v], color="#333", lw=3, zorder=5)
        ax.add_patch(Circle((X + xl, zl), 9, fc="white", ec="black", zorder=6))
    rect(ax, X + sh - LIFT_BAR[0] / 2, LIFT_BAR_Z0 + h, X + sh + LIFT_BAR[0] / 2, LIFT_BAR_Z0 + h + LIFT_BAR[2], C["lift"], z=5)
    for sx in (1, -1):
        rect(ax, X + sh + sx * CELL_X - CELL[0] / 2, LIFT_BAR_Z0 + h + LIFT_BAR[2], X + sh + sx * CELL_X + CELL[0] / 2,
             DECK_Z0_LOW + h, "#3477c4", z=5)
    rect(ax, X + sh - DECK_LX / 2, DECK_Z0_LOW + h, X + sh + DECK_LX / 2, DECK_TOP_LOW + h, C["deck"], z=5)
    # actuator
    ax.plot([X - 240, X + sh], [FRAME_Z0 + 50, LIFT_BAR_Z0 + h - 5], color="#2c3e8f", lw=5, zorder=5, solid_capstyle="round")
    # rear E-box, masts, beacon
    ex0, ex1 = X + EBOX_X0, X + EBOX_X0 - EBOX[0]
    rect(ax, ex1, EBOX_Z0, ex0, EBOX_Z0 + EBOX[2], C["ebox"], z=4)
    ax.text((ex0 + ex1) / 2, EBOX_Z0 + EBOX[2] / 2, "E-BOX", rotation=90, ha="center", va="center", fontsize=7, zorder=5)
    mx = (ex0 + ex1) / 2
    rect(ax, mx - 15, EBOX_Z0 + EBOX[2], mx + 15, ANT_TOP - ANT[1], "#999", z=4)
    rect(ax, mx - 75, ANT_TOP - ANT[1], mx + 75, ANT_TOP, "#eeeeee", z=4)
    rect(ax, mx - 50, EBOX_Z0 + EBOX[2], mx + 50, EBOX_Z0 + EBOX[2] + BEACON[1], "#ff8c00", z=4)
    # low front sensor bar + LiDAR + E-stop
    fx = X + FRONT_BAR_X0
    rect(ax, X + FRAME_LEN / 2, FRONT_BAR_Z0, fx + FRONT_BAR[0], FRONT_BAR_Z0 + FRONT_BAR[2], "#999", z=4)
    rect(ax, fx - 12, FRONT_BAR_Z0 + FRONT_BAR[2], fx + 53, FRONT_BAR_Z0 + FRONT_BAR[2] + LIDAR[2], "#111", z=4)
    rect(ax, fx + FRONT_BAR[0], FRONT_BAR_Z0 - 15, fx + FRONT_BAR[0] + ESTOP_BOX, FRONT_BAR_Z0 + 55, "#f1c40f", z=4)


def draw_stand_side(ax, kg, lane):
    for sx in (1, -1):
        rect(ax, sx * POST_X - POST / 2, 0, sx * POST_X + POST / 2, LEDGE_TOP + 300, C["stand"], z=1)
    rect(ax, -LEDGE[0] / 2, LEDGE_TOP - LEDGE[2], LEDGE[0] / 2, LEDGE_TOP, C["ledge"], z=7)
    rect(ax, -GUIDE[0] / 2 - 500, 0, GUIDE[0] / 2, GUIDE[2], "#b0b0b0", alpha=0.5, z=1)
    if lane == "FULL":
        for sx in (1, -1):
            rect(ax, sx * POST_X - 70, -60, sx * POST_X + 70, 0, "#3477c4", z=1)
        rect(ax, POST_X + 120, 700, POST_X + 620, 900, "#111", z=8)
        ax.text(POST_X + 370, 800, f"{kg:6.1f} kg" if kg else "  ---.- kg", color="#3cff6b", ha="center", va="center",
                fontsize=10, family="monospace", zorder=9)
        ax.text(POST_X + 370, 940, "certified scale", ha="center", fontsize=7, zorder=9)


def draw_section(ax, s):
    """Cross-section through the bay centre (y, z)."""
    ax.add_patch(Rectangle((-1000, -80), 2000, 80, fc=C["ground"], ec="none", zorder=0))
    for sy in (1, -1):
        rect(ax, sy * POST_Y - POST / 2, 0, sy * POST_Y + POST / 2, LEDGE_TOP + 300, C["stand"], z=1, alpha=0.6)
        rect(ax, sy * LEDGE_Y0, LEDGE_TOP - LEDGE[2], sy * (LEDGE_Y0 + LEDGE[1]), LEDGE_TOP, C["ledge"], z=7)
        rect(ax, sy * (LEDGE_Y0 + LEDGE[1]), LEDGE_TOP - LEDGE[2], sy * (POST_Y - POST / 2), LEDGE_TOP, C["ledge"], z=7)
        gy = TRACK_OUTER_W / 2 + 30
        rect(ax, sy * gy, 0, sy * (gy + GUIDE[1]), GUIDE[2], "#b0b0b0", z=1)
    under = abs(s["X"]) < 1100 and s["show"]
    h = s["h"]
    if under:
        for sy in (1, -1):
            rect(ax, sy * TRACK_INNER_Y, 0, sy * TRACK_OUTER_W / 2, TRACK_H, C["track"], z=3)
            rect(ax, sy * (RAIL_Y - RHS_B / 2), FRAME_Z0, sy * (RAIL_Y + RHS_B / 2), FRAME_Z1, C["frame"], z=4)
            rect(ax, sy * (RAIL_Y - LIFT_BAR[1] / 2), LIFT_BAR_Z0 + h, sy * (RAIL_Y + LIFT_BAR[1] / 2), LIFT_BAR_Z0 + h + LIFT_BAR[2], C["lift"], z=5)
            rect(ax, sy * (RAIL_Y - CELL[1] / 2), LIFT_BAR_Z0 + h + LIFT_BAR[2], sy * (RAIL_Y + CELL[1] / 2), DECK_Z0_LOW + h, "#3477c4", z=5)
        rect(ax, -(RAIL_Y - RHS_B / 2), FRAME_Z0, RAIL_Y - RHS_B / 2, FRAME_Z1, C["frame"], z=4, alpha=0.5)
        rect(ax, -DECK_LY / 2, DECK_Z0_LOW + h, DECK_LY / 2, DECK_TOP_LOW + h, C["deck"], z=5)
        ax.annotate("", xy=(0, 0), xytext=(0, CLEARANCE), arrowprops=dict(arrowstyle="<->", lw=0.8), zorder=8)
        ax.text(20, CLEARANCE / 2, f"{CLEARANCE} clear", fontsize=7, zorder=8)
    else:
        ax.text(0, 250, "robot outside the bay", ha="center", fontsize=8, color="#555")
    # bin in this bay
    lane = s["lane"]
    if lane == "FULL":
        on = s["full_on_robot"]
        zb = DECK_TOP_LOW + h if on else LEDGE_TOP
        show_bin = on or True
        full = True
    else:
        on = s["empty_on_robot"]
        zb = DECK_TOP_LOW + h if on else LEDGE_TOP
        show_bin = (abs(s["X"] + SH) < 1100) if on else True
        full = False
    if lane == "FULL" and on and not under:
        show_bin = False
    if show_bin:
        draw_bin(ax, 0, zb, BIN[1], full)
        gap = zb - LEDGE_TOP
        if under and abs(gap) > 1:
            ax.annotate("", xy=(LEDGE_Y0 + 50, LEDGE_TOP), xytext=(LEDGE_Y0 + 50, zb), arrowprops=dict(arrowstyle="<->", lw=0.8, color=C["accent"]), zorder=9)
            ax.text(LEDGE_Y0 + 70, (zb + LEDGE_TOP) / 2 + 10, f"{gap:.0f}", fontsize=7, color=C["accent"], zorder=9)
        if under and not on:
            g2 = LEDGE_TOP - (DECK_TOP_LOW + h)
            if g2 > 1:
                ax.text(-LEDGE_Y0 + 30, DECK_TOP_LOW + h + 8, f"gap {g2:.0f}", fontsize=7, color=C["accent"], zorder=9)


def draw_topview(ax, s):
    for yl, name in ((YF, "FULL bay\n(on scale)"), (YE, "EMPTY bay")):
        for sx in (1, -1):
            for sy in (1, -1):
                rect(ax, sx * POST_X - POST / 2, yl + sy * POST_Y - POST / 2, sx * POST_X + POST / 2, yl + sy * POST_Y + POST / 2, C["stand"], z=2)
            rect(ax, -LEDGE[0] / 2, yl + sx * LEDGE_Y0, LEDGE[0] / 2, yl + sx * (LEDGE_Y0 + LEDGE[1]), C["ledge"], z=2)
        ax.text(1100, yl, name, fontsize=7, va="center")
    # bins standing in bays
    if not s["full_on_robot"]:
        rect(ax, -BIN[0] / 2, YF - BIN[1] / 2, BIN[0] / 2, YF + BIN[1] / 2, C["olives"], alpha=0.8, z=3)
    if not s["empty_on_robot"]:
        rect(ax, -BIN[0] / 2, YE - BIN[1] / 2, BIN[0] / 2, YE + BIN[1] / 2, C["bin"], z=3)
    x, y, hd = s["pose"]
    c, sn = cos(radians(hd)), sin(radians(hd))
    L0, L1, W = -880, 900, TRACK_OUTER_W / 2
    pts = [(L0, -W), (L1, -W), (L1, W), (L0, W)]
    ax.add_patch(Polygon([(x + px * c - py * sn, y + px * sn + py * c) for px, py in pts], fc="#2f6b3f", ec="black", alpha=0.9, zorder=4))
    ax.add_patch(Polygon([(x + px * c - py * sn, y + px * sn + py * c) for px, py in [(L1, 0), (L1 - 250, 200), (L1 - 250, -200)]],
                         fc="white", zorder=5))
    if s["full_on_robot"] or s["empty_on_robot"]:
        bx = x + SH * c
        rect(ax, bx - BIN[0] / 2, y - BIN[1] / 2, bx + BIN[0] / 2, y + BIN[1] / 2, C["olives"] if s["full_on_robot"] else C["bin"], alpha=0.8, z=6)
    ax.set_xlim(-5200, 3600); ax.set_ylim(-2300, 2300); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("BASE — top view", fontsize=9)


def frame_at(t, fig, axes):
    ax1, ax2, ax3, ax4 = axes
    for a in axes:
        a.clear()
    s = state(t)
    # side view
    ax1.add_patch(Rectangle((-4000, -80), 8000, 80, fc=C["ground"], ec="none", zorder=0))
    draw_stand_side(ax1, s["kg"], s["lane"])
    if s["show"]:
        draw_robot_side(ax1, s["X"], s["h"])
    # bins in the side view
    if s["lane"] == "FULL":
        if s["full_on_robot"]:
            draw_bin(ax1, s["X"] + shift(s["h"]), DECK_TOP_LOW + s["h"], BIN[0], True)
        else:
            draw_bin(ax1, 0, LEDGE_TOP, BIN[0], True)
    else:
        if s["empty_on_robot"]:
            draw_bin(ax1, s["X"] + shift(s["h"]), DECK_TOP_LOW + s["h"], BIN[0], False)
        else:
            draw_bin(ax1, 0, LEDGE_TOP, BIN[0], False)
    ax1.set_xlim(-3300, 3300); ax1.set_ylim(-150, 1750); ax1.set_aspect("equal"); ax1.axis("off")
    ax1.set_title(f"SIDE VIEW — {s['lane']} lane       deck lift {s['h']:.0f} mm", fontsize=10, loc="left")
    ax1.text(3250, -130, "front →", ha="right", fontsize=8)
    # section
    draw_section(ax2, s)
    ax2.set_xlim(-950, 950); ax2.set_ylim(-150, 1750); ax2.set_aspect("equal"); ax2.axis("off")
    ax2.set_title("SECTION through the bay", fontsize=10)
    # top view
    draw_topview(ax3, s)
    # caption
    step = next(st for st in STEPS if st[0] <= t < st[1]) if t < T_END else STEPS[-1]
    ax4.axis("off")
    ax4.text(0.0, 0.85, step[2], fontsize=15, weight="bold", transform=ax4.transAxes, va="top")
    ax4.text(0.0, 0.45, step[3], fontsize=10.5, transform=ax4.transAxes, va="top")
    ax4.text(0.0, 0.02, "BinBot — bin swap at the base (to scale, mm)", fontsize=8, color="#666", transform=ax4.transAxes)


def make(fps=FPS, path=OUT + "bin_swap.mp4", size=(16, 9), dpi=80):
    fig = plt.figure(figsize=size, facecolor="white")
    gs = fig.add_gridspec(2, 2, width_ratios=[2.2, 1], height_ratios=[2.4, 1], hspace=0.08, wspace=0.03,
                          left=0.02, right=0.98, top=0.95, bottom=0.03)
    axes = (fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 0]))
    n = int(T_END * fps)
    anim = animation.FuncAnimation(fig, lambda i: frame_at(i / fps, fig, axes), frames=n)
    writer = animation.FFMpegWriter(fps=fps, bitrate=2500) if path.endswith(".mp4") else animation.PillowWriter(fps=fps)
    anim.save(path, writer=writer, dpi=dpi)
    plt.close(fig)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:   # still frames for checking: python3 animate.py 3 12 25
        fig = plt.figure(figsize=(16, 9), facecolor="white")
        gs = fig.add_gridspec(2, 2, width_ratios=[2.2, 1], height_ratios=[2.4, 1], hspace=0.08, wspace=0.03,
                              left=0.02, right=0.98, top=0.95, bottom=0.03)
        axes = (fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 0]))
        for t in sys.argv[1:]:
            frame_at(float(t), fig, axes)
            fig.savefig(OUT + f"_frame_{t}.png", dpi=70)
    else:
        make()
        make(fps=8, path=OUT + "bin_swap.gif", size=(12, 6.75), dpi=70)
        print("ok")
