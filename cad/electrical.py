"""Electrical drawings for BinBot (BP-04). Outputs PDF + PNG + SVG in cad/out/.

E-01  Power distribution (48 V)
E-02  Safety circuit (E-stop chain, contactor, brakes)
E-03  Control + communication block diagram
E-04  Electronics box (E-box) layout
"""
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import schemdraw
import schemdraw.elements as elm
from params import EBOX

schemdraw.use("matplotlib")
OUT = "out/"
SW, SH = 40, 28            # sheet size in drawing units (A3 ratio)
TODAY = f"{datetime.date.today():%Y-%m-%d}"


# ---------------------------------------------------------------- helpers
def sheet(d, number, title):
    def ln(p, q, **kw):
        d.add(elm.Line(**kw).at(p).to(q))
    for p, q in (((0.5, 0.5), (SW - .5, 0.5)), ((SW - .5, 0.5), (SW - .5, SH - .5)),
                 ((SW - .5, SH - .5), (0.5, SH - .5)), ((0.5, SH - .5), (0.5, 0.5))):
        ln(p, q, lw=1.6)
    x0, y0 = 25.5, 0.5
    for p, q in (((x0, y0), (x0, 4.5)), ((x0, 4.5), (SW - .5, 4.5)), ((x0, 3.5), (SW - .5, 3.5)),
                 ((x0, 2.5), (SW - .5, 2.5)), ((x0, 1.5), (SW - .5, 1.5))):
        ln(p, q, lw=1)
    for y, t, s in ((4.0, "BINBOT — autonomous olive bin carrier", 12), (3.0, title, 12),
                    (2.0, f"DWG {number}   REV A   BP-04 electronics", 10),
                    (1.0, f"PRELIMINARY — check against vendor datasheets   {TODAY}", 9)):
        d.add(elm.Label().at((x0 + 0.3, y)).label(t, fontsize=s, halign="left"))


def box(d, x0, y0, x1, y1, text, fs=10, ls="-"):
    d.add(elm.Line(ls=ls).at((x0, y0)).to((x1, y0)))
    d.add(elm.Line(ls=ls).at((x1, y0)).to((x1, y1)))
    d.add(elm.Line(ls=ls).at((x1, y1)).to((x0, y1)))
    d.add(elm.Line(ls=ls).at((x0, y1)).to((x0, y0)))
    d.add(elm.Label().at(((x0 + x1) / 2, (y0 + y1) / 2)).label(text, fontsize=fs))


def wire(d, *pts, ls="-", label=None, loc="top", fs=9):
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        e = elm.Line(ls=ls).at(p).to(q)
        if label and i == 0:
            e.label(label, loc=loc, fontsize=fs)
        d.add(e)


def text(d, x, y, s, fs=9, halign="left"):
    d.add(elm.Label().at((x, y)).label(s, fontsize=fs, halign=halign))


def gnd(d, x, y, lab="0V"):
    d.add(elm.Ground().at((x, y)).label(lab, loc="right", fontsize=8))


def save(d, name):
    d.save(OUT + name + ".svg")
    d.save(OUT + name + ".pdf")
    d.save(OUT + name + ".png", dpi=110)


def new():
    d = schemdraw.Drawing(show=False)
    d.config(unit=2, fontsize=10, lw=1.1)
    d.add(elm.Line(color="white").at((0, 0)).to((SW, SH)))  # fixes the page extent
    return d


# ---------------------------------------------------------------- E-01 power
def e01():
    d = new()
    sheet(d, "E-01", "POWER DISTRIBUTION 48 V")
    R = 23  # top rail
    # battery + BMS
    d.add(elm.Battery().at((4, 15)).to((4, 19)).label("BT1  48 V LiFePO4\n16S ~150 Ah\nBMS inside\n(CAN → MCU)", loc="bottom", fontsize=9))
    gnd(d, 4, 15, "0V star point")
    wire(d, (4, 19), (4, R))
    d.add(elm.Dot().at((4, 21)))
    # charge inlet
    d.add(elm.Fuse().at((1.5, 17)).to((1.5, 21)).label("F7\n40 A", loc="bottom", fontsize=8))
    wire(d, (1.5, 21), (4, 21))
    text(d, 1.0, 16.2, "X1 charge inlet\nSB175 + detect pin\n→ MCU (no drive\nwhile plugged)", fs=8)
    # main path
    d.add(elm.Fuse().at((4, R)).to((7, R)).label("F1 200 A\nMEGA", fontsize=8))
    d.add(elm.Switch().at((7, R)).to((10, R)).label("S1 isolator\n(key)", fontsize=8))
    d.add(elm.Dot().at((10, R)))
    d.add(elm.Switch().at((10, R)).to((14, R)).label("K1 main contactor\n24 V coil (E-02)", loc="bottom", fontsize=8))
    wire(d, (10, R), (10, R + 2.2))
    d.add(elm.Resistor().at((10, R + 2.2)).to((14, R + 2.2)).label("R1 100 Ω 25 W precharge", fontsize=8))
    wire(d, (14, R + 2.2), (14, R))
    d.add(elm.Dot().at((14, R)))
    wire(d, (14, R), (31, R), label="+48 V DRIVE  (off when E-stop / safety trips)   35 mm²", fs=9)
    # drive drops
    for x, n, side in ((17, "L", "left"), (22, "R", "right")):
        d.add(elm.Dot().at((x, R)))
        d.add(elm.Fuse().at((x, R)).to((x, 19.5)).label(f"F{2 if n == 'L' else 3}\n100 A", loc="bottom", fontsize=8))
        box(d, x - 1.6, 16, x + 1.6, 19.5, f"MC-{n}\nmotor ctrl\n{side}\nCAN", fs=8)
        wire(d, (x + 1.6, 16.6), (x + 2.1, 16.6)); gnd(d, x + 2.1, 16.6, "")
        d.add(elm.Motor().at((x, 16)).to((x, 12.5)).label(f"M{1 if n == 'L' else 2}\n3~ BLDC\n≥ 2 kW\n+ encoder", loc="bottom", fontsize=8))
        text(d, x - 2.6, 11.4, f"brake YB{1 if n == 'L' else 2} → E-02", fs=8)
    # lift drop
    d.add(elm.Dot().at((27, R)))
    d.add(elm.Fuse().at((27, R)).to((27, 19.5)).label("F4\n40 A", loc="bottom", fontsize=8))
    box(d, 25.4, 16, 28.6, 19.5, "U3 DC/DC\n40-60 → 24 V\n25 A  LIFT", fs=8)
    wire(d, (27, 16), (27, 14.5))
    box(d, 25.4, 11, 28.6, 14.5, "Lift H-bridge\nK7/K8 (MCU)\n2× actuator\nM3, M4", fs=8)
    wire(d, (28.6, 16.6), (29.1, 16.6)); gnd(d, 29.1, 16.6, "")
    # aux
    wire(d, (10, R), (10, 20.5))
    d.add(elm.Fuse().at((10, 20.5)).to((10, 17.5)).label("F5 20 A\nAUX 4 mm²", loc="bottom", fontsize=8))
    wire(d, (10, 17.5), (10, 8))
    d.add(elm.Dot().at((10, 10.3)))
    wire(d, (10, 10.3), (23, 10.3), (23, 8))
    for x0, f, lab, out in ((10, "F6 10 A", "U1 DC/DC\n40-60 → 24 V 10 A\nCONTROL", "+24 V CTRL → F10…F16:\ncomputer, LiDAR, cameras,\nGNSS, MCU, safety relay,\nbrakes (via K3/K6)"),
                            (23, "F8 5 A", "U2 DC/DC\n40-60 → 12 V 5 A\nCOMMS", "+12 V → 4G router,\nLoRa, beacon, buzzer,\ndisplay")):
        xb = x0 + (2.2 if x0 == 10 else 1.8)
        d.add(elm.Fuse().at((x0, 8)).to((xb, 8)).label(f, fontsize=8))
        box(d, xb, 6.4, xb + 4, 9.6, lab, fs=8)
        wire(d, (xb + 4, 8), (xb + 4.6, 8))
        text(d, xb + 4.8, 8, out, fs=8)
        wire(d, (xb + 2, 6.4), (xb + 2, 5.9)); gnd(d, xb + 2, 5.9, "")
    notes = ("NOTES\n"
             "1. Battery 16S LiFePO4: 40-58.4 V. All DC/DC inputs rated 36-75 V.\n"
             "2. K1 is opened by the safety circuit (E-02): drive + lift lose power, brakes apply.\n"
             "3. R1 keeps controller capacitors charged so K1 does not arc when it closes.\n"
             "4. Wired 0 V returns to the star point; frame bonded to 0 V at ONE point only.\n"
             "5. Fuses in IP67 holders in the E-box. Wire: tinned flexible, 105 °C.\n"
             "6. Aux (computer, sensors, radio) stays on after E-stop so the robot can report.")
    text(d, 1.2, 4.4, notes, fs=8.5)
    save(d, "E-01_power")


# ---------------------------------------------------------------- E-02 safety
def e02():
    d = new()
    sheet(d, "E-02", "SAFETY CIRCUIT — E-STOP, CONTACTOR, BRAKES")
    L, Rr = 2, 36.5
    top, bot = 26, 5.5
    wire(d, (L, top), (L, bot)); text(d, L - 0.3, top + 0.6, "+24 V SAFE (F9 2 A)", fs=9)
    wire(d, (Rr, top), (Rr, bot)); text(d, Rr - 0.3, top + 0.6, "0 V", fs=9)
    KS = (23, 15, 28, 26.5)  # safety relay box
    box(d, *KS, "KS\nsafety relay\ndual channel\nmanual reset\n(PNOZ X-type,\nPL d / Cat 3)", fs=8)

    def chain(y, items, end_x):
        x = L
        d.add(elm.Dot().at((L, y)))
        for kind, lab in items:
            e = (elm.Button(nc=True) if kind == "nc" else elm.Button() if kind == "btn"
                 else elm.Switch() if kind == "no" else elm.ResistorIEC())
            d.add(e.at((x, y)).to((x + 2.5, y)).label(lab, fontsize=7))
            x += 2.5
        wire(d, (x, y), (end_x, y))
        return x

    ch1 = [("nc", "ES1a\nfront L"), ("nc", "ES2a\nfront R"), ("nc", "ES3a\nrear L"), ("nc", "ES4a\nrear R"),
           ("nc", "WES ch1\nwireless"), ("nc", "BF ch1\nbumper F"), ("nc", "BR ch1\nbumper R")]
    ch2 = [("nc", "ES1b"), ("nc", "ES2b"), ("nc", "ES3b"), ("nc", "ES4b"),
           ("nc", "WES ch2"), ("nc", "BF ch2"), ("nc", "BR ch2"), ("nc", "K4\nwatchdog\n(MCU)")]
    chain(25.5, ch1, KS[0]); text(d, KS[0] + 0.1, 25.9, "S12", fs=7)
    chain(22.5, ch2, KS[0]); text(d, KS[0] + 0.1, 22.9, "S22", fs=7)
    chain(19.5, [("btn", "S2 RESET\n(blue)"), ("nc", "K1 aux\n21-22"), ("nc", "K3 aux\n21-22")], KS[0])
    text(d, KS[0] + 0.1, 19.9, "S34", fs=7)
    chain(16.5, [], KS[0]); text(d, KS[0] + 0.1, 16.9, "A1", fs=7)
    wire(d, ((KS[0] + KS[2]) / 2, KS[1]), ((KS[0] + KS[2]) / 2, 14.2), (Rr, 14.2)); text(d, 25.6, 14.6, "A2", fs=7)
    d.add(elm.Dot().at((Rr, 14.2)))
    # outputs as rungs
    for y, items in ((12, [("no", "KS 13-14"), ("no", "K5 drive\nenable (MCU)"), ("coil", "K1 coil\nmain contactor")]),
                     (9, [("no", "KS 23-24"), ("coil", "K3 coil\nbrake supply")]),
                     (6.2, [("no", "K3 13-14"), ("no", "K6 brake\nrelease (MCU)"), ("coil", "YB1 ∥ YB2\nbrake coils 24 V")])):
        chain(y, items, Rr)
        d.add(elm.Dot().at((Rr, y)))
    text(d, 12.6, 21.0, "Wireless E-stop (WES): own safety radio, receiver relay opens if the\n"
                       "transmitter's heartbeat is lost. Bumpers BF/BR: safety edges with their own\n"
                       "control unit (dual-channel output).", fs=8)
    text(d, 29, 23.5, "HOW IT FAILS SAFE\n"
                      "• any button / bumper / radio loss / software\n  watchdog → KS opens → K1 + K3 drop\n"
                      "• K1 open: no power to motors or lift\n"
                      "• K3 open: brake coils lose power →\n  spring brakes clamp the tracks\n"
                      "• restart only with RESET after cause cleared\n"
                      "• welded K1/K3 contact → aux 21-22 stays\n  open → reset refused", fs=8)
    text(d, 1.2, 3.0, "Shown generic. On PNOZ X-type relays the chains run S11→S12, S21→S22, S33→S34 (relay-supplied test voltage)\n"
                      "instead of from +24 V. E-stops: 2 NC contact blocks each (a/b). Final design to be checked against ISO 13849 by a qualified person.", fs=8)
    save(d, "E-02_safety_circuit")


# ---------------------------------------------------------------- E-03 control
def e03():
    d = new()
    sheet(d, "E-03", "CONTROL AND COMMUNICATION — BLOCK DIAGRAM")
    B = {}

    def b(key, x0, y0, x1, y1, t, ls="-"):
        box(d, x0, y0, x1, y1, t, fs=8, ls=ls)
        B[key] = (x0, y0, x1, y1)

    b("pc", 13, 15, 20, 19.5, "PC1 main computer\nJetson Orin Nano-class\nROS 2: navigation,\nmission, logging")
    b("sw", 6, 15.5, 10, 19, "SW1\nEthernet switch\n5-port 12/24 V")
    b("lidar", 1.2, 22, 5.6, 25, "LIDAR1\n3D LiDAR\n(Mid-360-class)")
    b("camf", 6.2, 22, 9.6, 25, "CAM-F\nfront camera")
    b("camr", 10.2, 22, 13.6, 25, "CAM-R\nrear camera")
    b("rtr", 1.2, 15.5, 4.8, 19, "RTR1\n4G router\n(SIM)")
    b("g1", 14.5, 22, 18, 25, "GNSS1 F9P\nfront antenna\n(RTK rover)")
    b("g2", 18.6, 22, 22.1, 25, "GNSS2 F9P\nrear antenna\n(heading)")
    b("mcu", 26, 13.5, 33, 20, "MCU\nmotion + I/O controller\n(STM32-class on\n24 V I/O board)\nwatchdog to PC1")
    b("mcl", 13, 6.5, 16.5, 9, "MC-L\nmotor ctrl")
    b("mcr", 17.5, 6.5, 21, 9, "MC-R\nmotor ctrl")
    b("bms", 22, 6.5, 25.5, 9, "BT1 BMS")
    b("wg", 34, 16.5, 38.8, 20, "WG1 load-cell amp\n4 ch, RS485\n← LC1…LC4")
    b("lora", 34, 21.5, 38.8, 25, "RF1 LoRa 868 MHz\npendant + remote\nstop + heartbeat")
    b("disp", 34, 12.3, 38.8, 15.5, "HMI1 display\nweight / state\n(RS485)")
    b("imu", 26, 21.5, 30, 25, "IMU1\ntilt / roll\n(I²C)")
    b("io", 26, 5.5, 33, 11.5, "MCU I/O (24 V)\nOUT: K4 watchdog, K5 drive en,\nK6 brake rel, K7/K8 lift,\nbeacon, buzzer\nIN: lift limits S5/S6, charge\ndetect, KS status, E-stop aux")
    b("base", 1.2, 5.5, 9.5, 11.5, "BASE STATION\nmini PC: fleet manager, logs\nRTK reference F9P → NTRIP\ncertified scale (RS232)\n4G / Wi-Fi router", ls="--")
    b("pend", 34, 5.5, 38.8, 10.5, "PENDANTS (harvesters)\nCALL / SEND / STOP\nLoRa\n+ wireless E-stop TX\n(→ WES, E-02)", ls="--")

    def mid(k, side):
        x0, y0, x1, y1 = B[k]
        return {"n": ((x0 + x1) / 2, y1), "s": ((x0 + x1) / 2, y0), "e": (x1, (y0 + y1) / 2), "w": (x0, (y0 + y1) / 2)}[side]

    wire(d, mid("sw", "e"), (13, 17.25), label="ETH")
    wire(d, mid("rtr", "e"), mid("sw", "w"), label="ETH")
    wire(d, mid("lidar", "s"), (3.4, 20.5), (7, 20.5), (7, 19), label=None)
    wire(d, mid("camf", "s"), (7.9, 19))
    wire(d, mid("camr", "s"), (11.9, 20.5), (9, 20.5), (9, 19))
    text(d, 7.3, 20.9, "ETH (PoE / M12-X)", fs=7)
    wire(d, mid("g1", "s"), (16.25, 19.5)); wire(d, mid("g2", "s"), (20.35, 21), (19, 21), (19, 19.5))
    text(d, 16.4, 20.5, "USB", fs=7)
    wire(d, mid("pc", "e"), mid("mcu", "w"), label="USB + CAN")
    # CAN bus
    wire(d, (14.75, 12.3), (27, 12.3)); text(d, 17, 12.7, "CAN bus 500 kbit/s (twisted, 120 Ω each end)", fs=7)
    for k in ("mcl", "mcr", "bms"):
        wire(d, mid(k, "n"), (mid(k, "n")[0], 12.3))
    wire(d, (16.5, 12.3), (16.5, 15))
    wire(d, (27, 12.3), (27, 13.5))
    wire(d, (31, 11.5), (31, 13.5)); text(d, 31.2, 12.5, "24 V I/O", fs=7)
    wire(d, mid("wg", "w"), (33, 18.25), label="RS485")
    wire(d, mid("lora", "w"), (31.5, 23.25), (31.5, 20))
    wire(d, mid("disp", "w"), (33, 13.9))
    wire(d, mid("imu", "s"), (28, 20))
    wire(d, mid("rtr", "s"), (3, 11.5), ls="--"); text(d, 3.3, 13.3, "4G: telemetry,\nRTK corrections", fs=7)
    wire(d, mid("pend", "n"), (36.4, 12.3), ls="--")
    text(d, 36.5, 11.3, "868 MHz", fs=7)
    save(d, "E-03_control_block")


# ---------------------------------------------------------------- E-04 e-box layout
def e04():
    W, Hh = EBOX[1] - 40, EBOX[2] - 40          # backplate inside 600 x 600 enclosure
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    ax.set_xlim(-40, 1180); ax.set_ylim(-140, 720); ax.set_aspect("equal"); ax.axis("off")

    def r(x, y, w, h, t, fc="#ffffff", fs=7):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="black", lw=0.8, zorder=3))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, zorder=4)

    ax.add_patch(Rectangle((-20, -20), W + 40, Hh + 40, fc="none", ec="black", lw=2))
    ax.add_patch(Rectangle((0, 0), W, Hh, fc="#f4f4f4", ec="black", lw=1))
    for y in (150, 275, 415):                       # cable ducts
        r(0, y, W, 35, "cable duct 40", fc="#dddddd", fs=6)
    for y in (240, 360, 480):                        # DIN rails
        ax.plot([5, W - 5], [y, y], color="gray", lw=4, alpha=0.5, zorder=2)
    # row A: power
    r(10, 10, 170, 130, "MC-L\nmotor controller\nleft")
    r(190, 10, 170, 130, "MC-R\nmotor controller\nright")
    r(370, 20, 90, 110, "K1\nmain contactor\n200 A")
    r(470, 80, 80, 60, "R1 precharge\non heatsink")
    r(470, 10, 80, 60, "+48 V / 0 V\nbusbars\n(star point)")
    # row B: DIN rail 240
    r(10, 195, 90, 75, "U1 DC/DC\n24 V 10 A")
    r(110, 195, 80, 75, "U2 DC/DC\n12 V 5 A")
    r(200, 195, 110, 75, "U3 DC/DC\n24 V 25 A\nlift")
    r(320, 195, 25, 75, "KS", fs=6)
    for i, k in enumerate(("K3", "K4", "K5", "K6", "K7", "K8")):
        r(350 + i * 20, 205, 18, 60, k, fs=6)
    r(475, 195, 75, 75, "F1-F8\nfuse\nholders")
    # row C: DIN rail 360
    r(10, 315, 120, 95, "MCU + 24 V\nI/O board")
    r(140, 315, 90, 95, "WG1\nload-cell amp")
    r(240, 315, 130, 95, "PC1\nmain computer\n(in heatsink case)")
    r(380, 315, 80, 95, "SW1\nEthernet\nswitch")
    r(470, 315, 80, 95, "F9-F16\n24 V branch\nfuses")
    # row D: DIN rail 480
    r(10, 455, 120, 85, "RTR1\n4G router")
    r(140, 455, 60, 85, "GNSS1\nF9P")
    r(210, 455, 60, 85, "GNSS2\nF9P")
    r(280, 455, 60, 85, "RF1\nLoRa")
    r(350, 455, 60, 85, "CAN-USB\n+ IMU1")
    r(420, 455, 130, 85, "X2 / X3\nterminal blocks\npower | signal")
    ax.text(W / 2, Hh + 40, f"E-BOX BACKPLATE  {W}×{Hh} mm  (enclosure {EBOX[1]}×{EBOX[2]}×{EBOX[0]} IP65, steel, mounted at the rear)",
            ha="center", fontsize=10, weight="bold")
    # bottom face connectors
    con = ["X10 MC-L motor 3~ + encoder", "X11 MC-R motor 3~ + encoder", "X12 brakes YB1/YB2", "X13 lift M3/M4 + limits",
           "X14 load cells LC1-LC4 (4× M12)", "X15 front hoop: LiDAR, CAM-F, ES1/ES2, GNSS1, BF",
           "X16 rear: ES3/ES4, CAM-R, HMI1, beacon, BR", "battery + / − (2 × 35 mm² glands)"]
    ax.text(0, -45, "BOTTOM FACE (all cables enter from below, drip loop):", fontsize=8, weight="bold")
    for i, c in enumerate(con):
        ax.text(0 + (i % 2) * 300, -70 - (i // 2) * 18, "• " + c, fontsize=7.5)
    side = ("RIGHT SIDE: S1 battery isolator (key), X1 charge inlet\n"
            "LEFT SIDE: IP65 breather vent + filter fan (thermostat 40 °C)\n"
            "DOOR: nothing mounted (keeps it sealed)\n\n"
            "BUILD NOTES\n"
            "• 3 mm aluminium backplate = heat spreader for MC-L/R\n"
            "• power wiring kept in row A, signals rows C/D\n"
            "• CAN and Ethernet away from motor cables\n"
            "• label every wire both ends with its number\n"
            "• all connectors IP67: Deutsch DT (signals),\n  M12 (sensors/CAN/ETH), Anderson (power)")
    ax.text(620, 520, side, fontsize=8.5, va="top")
    # title block
    tb = (760, -130, 400, 110)
    ax.add_patch(Rectangle(tb[:2], tb[2], tb[3], fc="none", ec="black", lw=1.2))
    for i, t in enumerate(("BINBOT — autonomous olive bin carrier", "E-BOX LAYOUT (front view, door open)",
                           "DWG E-04   REV A   SCALE ≈ 1:4   mm", f"PRELIMINARY   {TODAY}")):
        ax.text(tb[0] + 10, tb[1] + tb[3] - 18 - i * 26, t, fontsize=9)
    for ext in ("pdf", "png"):
        fig.savefig(OUT + f"E-04_ebox_layout.{ext}", dpi=150 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    e01(); e02(); e03(); e04()
    print("ok")
