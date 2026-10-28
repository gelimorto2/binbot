"""DWG-005 anti-slide protection on 30° slopes. Writes out/DWG-005_anti_slide.(pdf|png)."""
import datetime
from math import cos, sin, radians
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
from params import *
from stability import side_shapes, rot, limits

OUT = "out/"
LOAD = M_BIN + STEEP_OLIVES


def bar(p, q, w):
    """Rectangle of width w between points p and q (x, z)."""
    (x0, z0), (x1, z1) = p, q
    dx, dz = x1 - x0, z1 - z0
    n = (dx * dx + dz * dz) ** 0.5
    ox, oz = -dz / n * w / 2, dx / n * w / 2
    return [(x0 + ox, z0 + oz), (x1 + ox, z1 + oz), (x1 - ox, z1 - oz), (x0 - ox, z0 - oz)]


def sprag(phi_deg):
    """Arm + claw polygons for an arm angle phi below horizontal, pointing backwards (-x)."""
    px, pz = SPRAG_PIVOT
    a = radians(phi_deg)
    tip = (px - SPRAG_L * cos(a), pz - SPRAG_L * sin(a))
    claw_back = (tip[0] + 0.25 * SPRAG_L * cos(a), tip[1] + 0.25 * SPRAG_L * sin(a))
    return [(bar((px, pz), tip, SPRAG_ARM), "#d0391b"), (bar(claw_back, tip, 30), "#555")], tip


def scene(ax, deployed, title, note, col):
    ang = radians(SLOPE_MAX)                                  # climbing: front up
    shapes = side_shapes(LOAD, raised=False)
    arm, tip = sprag(SPRAG_DEPLOY if deployed else -90)
    for pts, c in shapes + arm:
        ax.add_patch(Polygon(rot(pts, ang), closed=True, fc=c, ec="black", lw=0.6))
    ax.add_patch(Circle(rot([SPRAG_PIVOT], ang)[0], 18, fc="white", ec="black", zorder=5))
    ax0 = FRONT_BAR_X0 + FRONT_BAR[0] + 5
    if deployed:   # chain from the holder to a claw dug in ahead (uphill), pulled tight
        hz = ANCHOR_Z0 + ANCHOR_CLAW[2]
        cx = ax0 + (ANCHOR_CHAIN ** 2 - hz ** 2) ** 0.5
        ax.plot(*zip(*rot([(ax0, hz), (cx, 0)], ang)), color="#333", lw=2, ls=(0, (2, 1)))
        ax.add_patch(Polygon(rot([(cx - 60, 30), (cx + 90, 30), (cx + 20, -60)], ang), fc="#d0391b", ec="black"))
        ax.text(*rot([(cx - 250, 260)], ang)[0], "front drag\nanchor (tension)", fontsize=8, color="#1a5276")
    else:
        ax.add_patch(Polygon(rot([(ax0, ANCHOR_Z0), (ax0 + ANCHOR_CLAW[0], ANCHOR_Z0),
                                  (ax0 + ANCHOR_CLAW[0], ANCHOR_Z0 + ANCHOR_CLAW[2]), (ax0, ANCHOR_Z0 + ANCHOR_CLAW[2])], ang),
                             fc="#d0391b", ec="black"))
    g = rot([(-3000, 0), (2600, 0)], ang)
    ax.plot(*zip(*g), color="#8a7350", lw=3)
    for (px, pz) in rot([(u, -60) for u in range(-3000, 2601, 120)], ang):
        ax.plot([px, px - 50], [pz, pz - 50], color="#8a7350", lw=0.6)
    if deployed:
        t = rot([tip], ang)[0]
        ax.add_patch(Circle(t, 60, fc="none", ec="#c0392b", lw=1.5, zorder=6))
        a0, a1 = rot([(-100, 1750), (-800, 1750)], ang)
        ax.add_patch(FancyArrowPatch(a0, a1, arrowstyle="-|>", mutation_scale=18, color="#c0392b", lw=2))
        ax.text(*rot([(-900, 1850)], ang)[0], "slide stopped", color="#c0392b", fontsize=9, weight="bold")
        f0, f1 = rot([(tip[0] - 250, tip[1] + 250), (tip[0] - 20, tip[1] + 20)], ang)
        ax.add_patch(FancyArrowPatch(f0, f1, arrowstyle="-|>", mutation_scale=14, color="#1a5276", lw=1.5))
        ax.text(f0[0] - 520, f0[1] + 40, "rear sprag:\nclaw digs in,\narm = strut", fontsize=8, color="#1a5276")
    ax.text(*rot([(1250, 1350)], ang)[0], "uphill → base", fontsize=8, rotation=SLOPE_MAX)
    ax.set_xlim(-2300, 2000); ax.set_ylim(-1500, 2300); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=10.5, loc="left", weight="bold")
    ax.text(-2250, 2200, note, fontsize=8.5, va="top", color=col)


def yaw_panel(ax):
    """Top view: why the robot spins with rear-only grip, and why both ends hold it straight."""
    W, L = TRACK_OUTER_W, TRACK_LEN + 200

    def robot(cx, cy, yaw, anchors):
        pts = [(-L / 2, -W / 2), (L / 2, -W / 2), (L / 2, W / 2), (-L / 2, W / 2)]
        c, s_ = cos(radians(yaw)), sin(radians(yaw))
        tf = lambda x, y: (cx + x * c - y * s_, cy + x * s_ + y * c)
        ax.add_patch(Polygon([tf(*p) for p in pts], fc="#2f6b3f", ec="black", alpha=0.85))
        ax.add_patch(Polygon([tf(L / 2, 0), tf(L / 2 - 250, 200), tf(L / 2 - 250, -200)], fc="white"))
        for x, y in anchors:
            ax.plot(*tf(x, y), marker="X", color="#c0392b", ms=11, mec="black")
        ax.plot(cx, cy, marker="o", color="white", mec="black", ms=7)

    # left: rear only (the rear is downhill = lower in this view)
    robot(-1300, 0, 90 + 25, [(-L / 2 - 300, SPRAG_Y), (-L / 2 - 300, -SPRAG_Y)])
    ax.annotate("", xy=(-300, -900), xytext=(-900, 600),
                arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-0.4", color="#c0392b", lw=2))
    ax.text(-2600, -1900, "REAR ONLY (downhill end):\nthe heavy body above swings\nround the claws → sideways\n→ on 30° it ROLLS OVER", fontsize=8, color="#c0392b")
    # right: both ends
    robot(1500, 0, 90, [(-L / 2 - 300, SPRAG_Y), (-L / 2 - 300, -SPRAG_Y), (L / 2 + 900, ANCHOR_Y), (L / 2 + 900, -ANCHOR_Y)])
    ax.plot([1500 - 150, 1500 - 150], [L / 2, L / 2 + 900], color="#333", ls=(0, (2, 1)))
    ax.plot([1500 + 150, 1500 + 150], [L / 2, L / 2 + 900], color="#333", ls=(0, (2, 1)))
    ax.text(300, -1900, "BOTH ENDS: hangs straight\nbelow the front anchors like a\npendulum; 4 points 2.5 m apart\nstop any rotation", fontsize=8, color="#1e8449")
    ax.annotate("", xy=(2900, -1200), xytext=(2900, 1200), arrowprops=dict(arrowstyle="-|>", color="#8a7350", lw=2))
    ax.text(2980, 0, "downhill", rotation=-90, va="center", fontsize=8, color="#8a7350")
    ax.set_xlim(-2700, 3200); ax.set_ylim(-2300, 2200); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("C  WHY IT SPINS — TOP VIEW", fontsize=10.5, loc="left", weight="bold")


def main():
    T = limits(LOAD, False)
    fig = plt.figure(figsize=(16.54, 11.69), facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05], height_ratios=[1, 0.85], hspace=0.1, wspace=0.05,
                          left=0.02, right=0.98, top=0.94, bottom=0.03)
    fig.suptitle(f"BINBOT — ANTI-SLIDE & ANTI-SPIN PROTECTION ON {SLOPE_MAX}° SLOPES (base uphill: full bins climb)", fontsize=13, weight="bold", x=0.02, ha="left")
    scene(fig.add_subplot(gs[0, 0]), False, f"A  CLIMBING {SLOPE_MAX}° — NORMAL ({STEEP_OLIVES} kg, deck low)",
          f"Rear sprags upright + front anchors under the bar,\nall held by magnets. Tips backwards only at {T['up']:.0f}°.", "#1e8449")
    scene(fig.add_subplot(gs[0, 1]), True, "B  SLIDE DETECTED — HELD AT BOTH ENDS",
          "Magnets released: rear sprags prop the downhill end,\nfront anchors hold the uphill end → no spin, it stops.", "#c0392b")
    yaw_panel(fig.add_subplot(gs[0, 2]))
    ax = fig.add_subplot(gs[1, :]); ax.axis("off")
    cols = [
        ("1  PREVENT (before every 30° section)",
         f"• Bin ≤ {STEEP_OLIVES} kg, deck LOWERED\n"
         "• Dry-day only: wet-day mode (rain sensor + farmer switch +\n  weather forecast) blocks 30° routes\n"
         "• Grip check on the approach slope: slip < 10 %\n"
         "• Sprags armed: magnet current + position switch OK\n"
         "• Nobody downhill: pendant GPS positions outside a\n  20 m corridor below the robot\n"
         "• Speed 0.3 m/s, straight on the fall line (±5°), no turning\n"
         "• Going DOWN: in reverse, so the rear (sprags) is downhill\n  (rear camera + rear radar)"),
        ("2  DETECT (MCU, every 10 ms)",
         "SLIDE if any of:\n"
         "• robot moves > 0.05 m/s for 0.3 s while tracks are stopped\n  (RTK GNSS + IMU vs track encoders)\n"
         "• slip > 30 % for 1 s while driving\n"
         "• uncommanded turn > 3°/s, or heading > 5° off the\n  fall line (the start of a spin)\n"
         "• downhill acceleration > 0.5 m/s² not commanded\n"
         "• roll > 12° or pitch > 33°"),
        ("3  REACT (automatic, < 0.5 s)",
         "1. Drop rear sprags + front anchors together (K10)\n"
         "2. Tracks: brakes ON, never spin the tracks\n"
         "3. Lower the deck if raised (CoG down)\n"
         "4. Red beacon + siren; LoRa alarm to all pendants and\n   the farmer's phone: \"ROBOT SLIDING — KEEP AWAY\"\n"
         "5. Stay stopped. Re-arm only by a person on site\n\n"
         "Fail-safe: power lost → magnets release → sprags drop.\n"
         "False drop while climbing: arms trail, chains drag;\nstop and re-arm."),
        ("4  BEST FIX: THE ROUTE",
         "A tracked robot cannot beat wet clay at 30°,\nand side-on it rolls over.\n"
         "Cheapest real fix: cut a robot track on the 30°\n"
         "section with a mini excavator (1–2 days):\n"
         "• 1.5 m wide, ≤ 15° along the track\n"
         "• level across (≤ 5°), gravel on top\n"
         "• switchbacks with flat turning pads\n"
         "• earth berm / kerb on the downhill edge\n"
         "Level across = it can't roll even if it slides;\nthe anchors become a backup only.")]
    for i, (h, t) in enumerate(cols):
        ax.text(0.005 + i * 0.25, 0.97, h, fontsize=10, weight="bold", va="top", transform=ax.transAxes)
        ax.text(0.005 + i * 0.25, 0.86, t, fontsize=8.6, va="top", transform=ax.transAxes)
    ax.text(0.75, 0.02, f"DWG 005   REV D   anti-slide   {datetime.date.today():%Y-%m-%d}\nPRELIMINARY — test on the real slope (BP-09 tests S1–S4)",
            fontsize=8, transform=ax.transAxes, bbox=dict(fc="white", ec="black"))
    for ext in ("pdf", "png"):
        fig.savefig(OUT + f"DWG-005_anti_slide.{ext}", dpi=150 if ext == "png" else None, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
