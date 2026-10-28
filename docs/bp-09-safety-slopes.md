# BP‑09a — Slope & Anti‑Slide Safety (v0.1)

Part of the [BinBot wireframe](00-wireframe.md) (safety concept §7).
**Drawings:** [DWG‑005 anti‑slide](../cad/out/DWG-005_anti_slide.pdf) ·
[DWG‑004 stability](../cad/out/DWG-004_stability.pdf).

## 1. The situation

- Slopes up to **30°**, up and down the fall line.
- **The base station is uphill**, so full bins (≤ 400 kg on 30° routes) **climb**
  and the empty robot comes down.
- Grip needed on 30°: **0.58 × weight just to stand still** (brakes on) and
  **0.70 × weight to climb**. Wet clay gives about 0.4–0.6. **On wet ground the
  robot can slide even with its brakes locked**, loaded or empty. No tracked
  machine can fix that by itself.

The danger is a 900 kg machine sliding uncontrolled downhill, possibly turning
sideways and rolling, towards people working below.

## 2. Four layers

### Layer 1: Prevent (before every 30° section)
| Check | How |
|---|---|
| Load ≤ 400 kg, deck lowered | Weight from the load cells; per‑route bin target |
| Dry ground | **Wet‑day mode** blocks 30° routes: farmer switch, rain sensor on the base station, weather forecast (rain in the last 24 h) |
| Grip OK | Slip measured on the approach slope must be < 10 % |
| Sprags armed | Magnet current + position switch on both arms |
| Nobody downhill | Pendants carry GPS; no pendant inside a 20 m corridor below the robot's path |
| Driving style | 0.3 m/s, straight on the fall line, no turning, no stopping halfway unless needed |
| Going down | **In reverse**, so the rear (with the sprags) is always the downhill end. Rear camera + rear radar watch the way down |

### Layer 2: Detect (MCU, every 10 ms)
SLIDE is declared if any of these happens:
- the robot moves > 0.05 m/s for 0.3 s while its tracks are stopped (RTK GNSS + IMU vs. track encoders);
- slip > 30 % for 1 s while driving;
- uncommanded turn > 5°/s (the robot is swinging sideways);
- downhill acceleration > 0.5 m/s² that was not commanded;
- roll > 12° or pitch > 33°.

### Layer 3: React (automatic, < 0.5 s)
1. **Drop both sprags** (relay K10 cuts the holding magnets).
2. Tracks braked, **never spin them** (spinning digs the tracks in and makes it worse).
3. Lower the deck if it is raised (centre of gravity down).
4. Red flashing beacon + siren; LoRa alarm to every pendant and the farmer's
   phone: **"ROBOT SLIDING — KEEP AWAY"**.
5. Stay stopped. A person on site checks, re‑arms the sprags by hand and restarts.

### Layer 4: Mechanical last resort — rear sprags (works without power)
Two steel arms hinged on the rear of the top frame, at y = ±300 beside the E‑box,
the same idea as the sprag on old hill wagons.

| Item | Value |
|---|---|
| Arm | SHS 50×50×4, 750 mm, pin Ø25 |
| Claw | 150 × 200 × 12 mm, 3 hardened teeth |
| Stowed | Upright beside the E‑box, held by a **24 V holding magnet** (power = hold) |
| Deploy | Gas spring swings the arm down to 43° behind the robot; the claw touches the ground and digs in as the robot moves back |
| Stop | At 70° the arm hits a stop on its bracket: it becomes a **strut** and can't fold under |
| Fail‑safe | **Power lost or E‑box dead → magnets release → sprags drop** |
| Harmless if dropped by mistake | Climbing forward: the arms just trail behind. Only reversing is blocked until re‑armed |
| Loads | 4.9 kN downslope (990 kg on 30°, zero grip) × 3 for impact = 7.3 kN per arm |
| Strength | Steel: buckling 960 kN, pin 210 kN. **The soil is the limit:** ≈ 8 kN per claw in wet clay, more in dry soil |
| Cost | Arms, claws, brackets, gas springs, 2 holding magnets, relay K10, position switches: **€250–400** |

## 3. The real fix: change the route, not the robot

A robot track on the 30° section, cut once with a mini excavator (1–2 days, about €300–600):
- 1.5 m wide, ≤ 15° along the track, level across (≤ 5°), gravel on top;
- switchbacks with flat turning pads.

Then grip and stability stop being critical, full bins can climb on wet days, and
the sprags become a backup that should never be used. **Strongly recommended
before the first harvest.**

## 4. Tests (on your real 30° slope, robot loaded with sandbags, nobody downhill, robot on a safety rope to a tractor)

| # | Test | Pass |
|---|---|---|
| S1 | Climb 30° with 400 kg, dry | No slip > 10 %, stops and restarts mid‑slope |
| S2 | Park on 30° loaded, wet ground, 10 min | Either holds, or slide is detected and stopped by the sprags within 0.5 m |
| S3 | Cut power to the E‑box on 30° | Sprags drop |
| S4 | Pull the robot downhill with the tractor (rope), sprags deployed | Holds ≥ 8 kN per side before the claws move |
| S5 | Fake each slide signal (GNSS, slip, yaw) on flat ground | Sprags drop, alarm reaches pendants and phone |

## 5. Cost of this layer

| Item | Est. € |
|---|---|
| Sprags + magnets + K10 + switches | 250–400 |
| Rear radar for reversing downhill | 100–200 |
| GPS in the 2 pendants | 30–50 |
| **Total** | **≈ 400–650** |
| Robot track on the 30° section (contractor / own mini excavator) | 300–600 (recommended) |
