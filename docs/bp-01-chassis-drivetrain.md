# BP‑01 — Chassis & Drivetrain (v0.3)

Part of the [BinBot wireframe](00-wireframe.md).
**Drawings & 3D:** [DWG‑001 general arrangement](../cad/out/DWG-001_general_arrangement.pdf) ·
[DWG‑002 upper frame weldment](../cad/out/DWG-002_upper_frame_weldment.pdf) · [3D model](../cad/README.md).
All dimensions come from `cad/params.py`.

**Rev B changes (farmer feedback):** 350 mm clear under everything between the
tracks, no low bumpers (rocks); the robot drives **under** bins on base stands, so
the front is low and everything tall moved to the rear; battery split into two
packs in the end bays; frame diagonals removed.

## 1. Design inputs

| Input | Value |
|---|---|
| Payload | 500 kg olives + 40 kg bin = **540 kg** |
| Robot mass | ≈ 480 kg (undercarriage 250, frame 53, lift 60, batteries 75, E‑box 35, sensors 10) |
| Gross | **≈ 1,020 kg** |
| Slopes | 25° up/down the fall line; cross‑slope ≤ 10° loaded |
| Ground clearance | **≥ 350 mm** between the tracks, nothing below that |
| Base | Robot drives under bins standing on stands (BP‑02, DWG‑003) |
| Rows | 4 m apart → turn in place within ~2.5 m |
| Speed | 1.0 m/s flat, 0.5 m/s on slopes > 15°, 0.3 m/s at the base / near people |

## 2. Concept

Bought **electric rubber‑track undercarriage, 1.2 m wide** (you found one on
AliExpress, ~€1,200, custom sizes) + a welded upper frame (DWG‑002) sitting
**between** the tracks, bolted to their inner faces. The frame underside is 350 mm
above ground; the battery packs, lift links and actuators all sit inside the frame
height (350–450 mm), so nothing hangs below it.

## 3. Spec to send to the undercarriage seller

The listing is "customisable", so order it to this spec. Send this text to the seller:

> Electric rubber track undercarriage, custom:
> - Two track frames, **outer width 1200 mm**, track width 230–250 mm, overall length ≈ 1700 mm, **ground contact ≥ 1300 mm**, height ≈ 400 mm.
> - **No cross‑members or platform lower than 350 mm above ground between the tracks.** We will connect the two track frames with our own frame.
> - On the **inner face of each track frame**: 2 flat steel mounting pads, 150 × 100 mm, 10 mm, at 350–450 mm height, 900 mm apart, 4 × M16 holes each (or send your drawing and we adapt).
> - Load capacity **≥ 1000 kg** (1500 kg preferred), climbing **≥ 25° fully loaded**.
> - 48 V motors, **≥ 2 kW continuous each**, gearbox, **spring‑applied electromagnetic brake** (brakes when power is off), Hall/encoder feedback.
> - Motor controllers controllable by **CAN or RS485 or 0–5 V + direction** (not only the remote), with an enable input for our emergency stop.
> - Remote control included.
> - Please send: drawing (PDF/STEP) with mounting holes, weight, motor and brake datasheets, IP rating, CE declaration, price with shipping to Italy.

Before paying: ask for a video climbing 25° loaded. After delivery: test T1 before building on it.

## 4. Stability (CoG computed part by part)

| Mass | kg | CoG height |
|---|---|---|
| Robot (undercarriage low, batteries 435 mm) | 480 | 0.37 m |
| Full bin on raised deck (685 + floor + half the olives) | 540 | 1.09 m |
| **Combined** | **1,020** | **≈ 0.75 m** (x ≈ +10 mm, balanced) |

| Direction | Half‑base | Static tip angle | Operating limit (loaded) |
|---|---|---|---|
| Sideways (track centre lines) | 0.475 m | **32°** | **10° cross‑slope**, alarm 8°, stop 13° |
| Fore/aft (contact 1.3 m) | 0.65 m | **41°** | **25° up/down**, stop at 28° pitch |

25° + 3° for gentle braking (0.5 m/s²) = 28°, 13° below tipping.
Design rules: bin centre within ±50 mm of the track contact centre; no turning on
slopes > 10°; loaded routes follow the fall line; software refuses routes with
cross‑slope > 10° when loaded.

## 5. Traction, power, brakes

- **Traction:** climbing 25° needs (tan 25° + 0.12) ≈ **0.59 × weight**, loaded
  or empty. Wet clay gives only ~0.4–0.6, so steep wet slopes may be impossible
  after rain for any tracked machine. Put the base at the bottom of the grove if
  you can, so full bins go downhill. Slip detection and a "wet day" mode (BP‑05).
- **Drive:** 25° climb ≈ 3 kN per track at 0.5 m/s → 1.5 kW per track →
  **motors ≥ 2 kW continuous**, 2× peak for 30 s.
- **Brakes:** hold 1,020 kg on 25° × 1.5 safety = 6.4 kN → 3.2 kN per track →
  **≥ 16 Nm spring‑applied brake per motor** (with ~35:1 gearbox).

## 6. Upper frame (DWG‑002)

- 2 × RHS 100×50×4 side rails, 600 mm apart, z 350–450; 4 × RHS 100×50×4 cross beams.
- Bays: **front & rear end bays = battery packs** (on L40×4 angles) + lift links;
  **middle bay = lift actuators**.
- 4 brackets, 10 mm plate, 4 × M16 each, bolted to the track frames' inner faces.
- 4 tabs: front pair carries the low sensor bar, rear pair the E‑box.
- 8 link pivot plates, holes line‑bored in pairs.
- ≈ 53 kg of steel. S355, MIG, a4 fillets; primer + epoxy.

## 7. Bill of materials (BP‑01 only)

| Item | Qty | Est. € |
|---|---|---|
| Electric rubber‑track undercarriage, 1.2 m, custom (quoted) | 1 | 1,200 |
| RHS 100×50×4, L40×4, plate 8/10 mm (S355) | lot | 150 |
| M16 8.8 bolts, nuts, washers | 16 | 25 |
| Primer + epoxy paint | lot | 60 |
| **Total** | | **≈ 1,435** |

## 8. Tests

| # | Test | Pass |
|---|---|---|
| T1 | Climb steepest wet slope, 500 kg sandbags, straight up & down | 0.5 m/s, slip < 30 %, stops and restarts mid‑slope |
| T2 | Static tilt sideways, loaded, **strapped to a tractor**, nobody downhill | No track lift below 28° |
| T3 | Brake hold on 25°, loaded, power off | No creep in 10 min |
| T4 | E‑stop at 1 m/s flat and on 25° downhill | Stops within 0.5 m / 1.0 m, stays stable |
| T5 | Turn in place in a 4 m row, loaded, mud | Within a 2.4 m circle |
| T6 | Drive over a 300 mm rock between the tracks | Nothing touches |
| T7 | 2 h mud run | Motors < 90 °C, tracks stay on |

## 9. Hand‑offs
- **BP‑02:** lift bars on the rail tops (450), deck 585/685, stand ledges 635, front ≤ 545.
- **BP‑03:** 2 battery packs 260×440×160 mm in the end bays (2 × 16S 105 Ah, ~10.7 kWh).
- **BP‑04:** E‑box at the rear, low front sensor bar, safety edges instead of bumpers.
- **BP‑05:** pitch stop 28°, roll alarm 8° / stop 13° loaded, slip detection, wet‑day mode.
