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
        ax.text(f0[0] - 520, f0[1] + 40, "claw digs in,\narm = strut", fontsize=8, color="#1a5276")
    ax.text(*rot([(1250, 1350)], ang)[0], "uphill → base", fontsize=8, rotation=SLOPE_MAX)
    ax.set_xlim(-2300, 2000); ax.set_ylim(-1500, 2300); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=10.5, loc="left", weight="bold")
    ax.text(-2250, 2200, note, fontsize=8.5, va="top", color=col)


def detail(ax):
    px, pz = SPRAG_PIVOT
    ax.plot([-1900, -200], [0, 0], color="#8a7350", lw=3)
    ax.add_patch(Polygon([(-650, 460), (-200, 460), (-200, 560), (-650, 560)], fc="#2f6b3f", ec="black", lw=0.6))
    ax.text(-430, 600, "top frame rail end", fontsize=7, ha="center")
    ax.add_patch(Polygon([(-860, 460), (-660, 460), (-660, 960), (-860, 960)], fc="#9aa0a6", ec="black", lw=0.6, alpha=0.5))
    ax.text(-760, 900, "E-box\n(behind)", fontsize=7, ha="center")
    for phi, ls, lab in ((-90, "--", "STOWED (held by magnet)"), (SPRAG_DEPLOY, "-", f"DEPLOYED {SPRAG_DEPLOY}°"), (SPRAG_STOP, ":", f"STOP {SPRAG_STOP}° (strut)")):
        arm, tip = sprag(phi)
        for pts, c in arm:
            ax.add_patch(Polygon(pts, closed=True, fc=c if ls == "-" else "none", ec=c if ls != "-" else "black", lw=1, ls=ls))
        ax.text(tip[0] - 40, tip[1] + (60 if phi < 0 else -110), lab, fontsize=7.5, ha="right")
    ax.add_patch(Circle((px, pz), 20, fc="white", ec="black", zorder=5))
    ax.add_patch(Polygon([(px - 20, pz + SPRAG_L - 140), (px + 30, pz + SPRAG_L - 140), (px + 30, pz + SPRAG_L - 100), (px - 20, pz + SPRAG_L - 100)], fc="black"))
    ax.text(px + 60, pz + SPRAG_L - 120, "holding magnet\n(power = hold)", fontsize=7, va="center")
    ax.plot([px, px - 350], [pz + 120, pz + 20], color="#1a5276", lw=3)
    ax.text(px - 350, pz + 130, "gas spring\n(pushes arm down)", fontsize=7, color="#1a5276", ha="right")
    ax.annotate("", xy=(px, pz), xytext=(px, 0), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(px + 15, pz / 2, f"{pz}", fontsize=7)
    ax.text(-1930, 1300, f"SPRAG (×2, y = ±{SPRAG_Y})\nArm SHS {SPRAG_ARM}×{SPRAG_ARM}×4, {SPRAG_L} mm, pin Ø25\n"
                          f"Claw {SPRAG_CLAW[0]}×{SPRAG_CLAW[1]}×{SPRAG_CLAW[2]}, 3 hardened teeth\n"
                          "Load: 4.9 kN downslope (30°, no grip) × 3 = 7.3 kN/arm\n"
                          "Steel: buckling 960 kN, pin 210 kN → soil is the limit:\n"
                          "≈ 8 kN per claw in wet clay (more in dry soil)", fontsize=7.5, va="top")
    ax.set_xlim(-1950, 50); ax.set_ylim(-300, 1400); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("C  SPRAG DETAIL (rear, side view)", fontsize=10.5, loc="left", weight="bold")


def main():
    T = limits(LOAD, False)
    fig = plt.figure(figsize=(16.54, 11.69), facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05], height_ratios=[1, 0.85], hspace=0.1, wspace=0.05,
                          left=0.02, right=0.98, top=0.94, bottom=0.03)
    fig.suptitle(f"BINBOT — ANTI-SLIDE PROTECTION ON {SLOPE_MAX}° SLOPES (base uphill: full bins climb)", fontsize=13, weight="bold", x=0.02, ha="left")
    scene(fig.add_subplot(gs[0, 0]), False, f"A  CLIMBING {SLOPE_MAX}° — NORMAL ({STEEP_OLIVES} kg, deck low)",
          f"Sprags stowed upright, held by magnets.\nTips backwards only at {T['up']:.0f}°.", "#1e8449")
    scene(fig.add_subplot(gs[0, 1]), True, "B  SLIDE DETECTED — SPRAGS DROPPED",
          "Magnets released → gas springs swing the arms down\n→ claws dig in behind the robot → it stops.", "#c0392b")
    detail(fig.add_subplot(gs[0, 2]))
    ax = fig.add_subplot(gs[1, :]); ax.axis("off")
    cols = [
        ("1  PREVENT (before every 30° section)",
         f"• Bin ≤ {STEEP_OLIVES} kg, deck LOWERED\n"
         "• Dry-day only: wet-day mode (rain sensor + farmer switch +\n  weather forecast) blocks 30° routes\n"
         "• Grip check on the approach slope: slip < 10 %\n"
         "• Sprags armed: magnet current + position switch OK\n"
         "• Nobody downhill: pendant GPS positions outside a\n  20 m corridor below the robot\n"
         "• Speed 0.3 m/s, straight on the fall line, no turning\n"
         "• Going DOWN: in reverse, so the rear (sprags) is downhill\n  (rear camera + rear radar)"),
        ("2  DETECT (MCU, every 10 ms)",
         "SLIDE if any of:\n"
         "• robot moves > 0.05 m/s for 0.3 s while tracks are stopped\n  (RTK GNSS + IMU vs track encoders)\n"
         "• slip > 30 % for 1 s while driving\n"
         "• uncommanded turn > 5°/s (robot swinging sideways)\n"
         "• downhill acceleration > 0.5 m/s² not commanded\n"
         "• roll > 12° or pitch > 33°"),
        ("3  REACT (automatic, < 0.5 s)",
         "1. Release both sprags (relay K10 cuts the magnets)\n"
         "2. Tracks: brakes ON, never spin the tracks\n"
         "3. Lower the deck if raised (CoG down)\n"
         "4. Red beacon + siren; LoRa alarm to all pendants and\n   the farmer's phone: \"ROBOT SLIDING — KEEP AWAY\"\n"
         "5. Stay stopped. Re-arm only by a person on site\n\n"
         "Fail-safe: power lost → magnets release → sprags drop.\n"
         "False drop while climbing forward = arms just trail behind."),
        ("4  BEST FIX: THE ROUTE",
         "A tracked robot cannot beat wet clay at 30°.\n"
         "Cheapest real fix: cut a robot track on the 30°\n"
         "section with a mini excavator (1–2 days):\n"
         "• 1.5 m wide, ≤ 15° along the track\n"
         "• level across (≤ 5°), gravel on top\n"
         "• switchbacks with flat turning pads\n"
         "Then grip, stability and sliding stop being\n"
         "a problem, and the sprags become a backup only.")]
    for i, (h, t) in enumerate(cols):
        ax.text(0.005 + i * 0.25, 0.97, h, fontsize=10, weight="bold", va="top", transform=ax.transAxes)
        ax.text(0.005 + i * 0.25, 0.86, t, fontsize=8.6, va="top", transform=ax.transAxes)
    ax.text(0.75, 0.02, f"DWG 005   REV C   anti-slide   {datetime.date.today():%Y-%m-%d}\nPRELIMINARY — test on the real slope (BP-09 tests S1–S4)",
            fontsize=8, transform=ax.transAxes, bbox=dict(fc="white", ec="black"))
    for ext in ("pdf", "png"):
        fig.savefig(OUT + f"DWG-005_anti_slide.{ext}", dpi=150 if ext == "png" else None, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
