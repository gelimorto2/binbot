# BP‑01 — Chassis & Drivetrain (v0.1)

Part of the [BinBot wireframe](00-wireframe.md). This blueprint covers the
tracked base: frame, tracks, motors, brakes, stability and traction.
The bin lift deck sits on top of it (BP‑02), and the battery and electronics
are bolted into it (BP‑03 and BP‑04).

## 1. Design inputs

| Input | Value |
|---|---|
| Payload | 500 kg olives + 40 kg bin = **540 kg** |
| Robot mass (target) | ≤ 420 kg incl. battery, deck, electronics |
| Gross mass | **≈ 960 kg** (design calcs use 1,000 kg) |
| Bin | 1200 (along travel) × 1000 (across) × ~760 mm |
| Slopes | **25° up/down** the fall line; cross‑slope only where unavoidable |
| Rows | 4 m apart → robot must turn in place within ~2.5 m |
| Speed | 1.0 m/s on flat, 0.5 m/s on slopes > 15°, 0.3 m/s near people |
| Ground | Wet clay, mud, ruts, stones |
| Builder | Farmer welds and wires (own labour) |

> Capacity check: a 1200 × 1000 × 760 bin holds ~600 L ≈ **400 kg** of olives
> when level‑full. 500 kg means heaped. The design still allows 500 kg.

## 2. Concept decision

| | **A. Retrofit electric tracked dumper + widen gauge** (chosen) | B. Custom frame on bought track kit |
|---|---|---|
| What | Buy an electric tracked mini‑dumper (800 kg class), remove the skip, weld in spacer beams to widen the track gauge to 1.3 m | Weld a full frame, buy tracks, sprockets, idlers, rollers, motors and gearboxes separately |
| Cost | €3,000–4,500 + ~€250 steel | €2,500–4,000 + much more welding and machining |
| Risk | Low: tracks, motors, gearboxes and brakes come as a proven set | High: track alignment, tensioning, sealing are all on you |
| Effort | ~3–4 weekends | ~8–12 weekends |

**Why widen the gauge:** most small dumpers are 0.75–0.9 m wide. With a full bin
they become unstable sideways (§4). Electric dumpers usually have **one motor
per track mounted on the track frame**, so the two track units can be moved
apart with welded beams, with no shafts to lengthen. Check this before buying (§3).

## 3. Buying checklist for the dumper

Must have:
- [ ] **Electric**, 48–60 V, **one motor per track** (skid steer, no hydraulics)
- [ ] **Rated payload ≥ 800 kg** (gives margin over our 540 kg + deck)
- [ ] **Electromagnetic spring‑applied parking brake** on each motor
- [ ] Track units **bolted** to the central frame, or easy to cut free
- [ ] Track width ≥ 230 mm, aggressive lug pattern
- [ ] Rated gradeability ≥ 25° (≥ 47 %) **loaded**
- [ ] Motor controller with throttle/direction inputs we can drive
      (0–5 V analogue or CAN), or easy to replace (BP‑04)
- [ ] Spare tracks and parts available in Italy

Nice to have: lithium battery ≥ 5 kWh, motor encoders, IP65+ controller.

**Before paying: run the slope test.** Drive it, loaded with 500 kg of
sandbags, straight up and down your steepest wet slope (§6, test T1).
If it can't climb, no robot built on it will.

## 4. Stability

Centre of gravity (CoG), bin carried on the raised deck:

| Mass | kg | CoG height |
|---|---|---|
| Robot (tracks low, battery lowest) | 420 | 0.45 m |
| Full bin (deck top 0.55 m + floor + half the olive load) | 540 | 0.95 m |
| **Combined** | **960** | **≈ 0.73 m → design 0.75 m** |

Static tip angle = atan(half‑base ÷ CoG height):

| Direction | Half‑base | Tip angle | Operating limit (loaded) |
|---|---|---|---|
| Sideways, **0.9 m dumper (stock)** | 0.33 m | 23° | ✗ unsafe |
| Sideways, **1.3 m widened** (track centre lines, conservative) | 0.53 m | **35°** | **12° cross‑slope**, alarm 10°, stop 15° |
| Fore/aft (track contact length 1.3 m) | 0.65 m | **41°** | **25° up/down**, stop at 28° pitch |

Margins:
- **Sideways:** a 10 cm rut under one track adds ~5°. Bumps add more. A
  factor of about 3 is kept for that.
- **Fore/aft:** 25° slope + 6° for a 1 m/s² braking stop = 31°, which is
  10° below tipping. So on slopes over 15°: speed 0.5 m/s and gentle braking
  (0.5 m/s²).

Design rules:
1. **Bin centre within ±50 mm of the track contact patch centre** (fore/aft
   and sideways).
2. Battery on the lowest possible tray, between the tracks.
3. Deck raised **only as much as needed** to clear the stands (target 100 mm).
4. No turning on slopes > 10°. Turn on the flat ends of rows.
5. Loaded routes follow the fall line. The software refuses routes where
   cross‑slope > 12° with load > 100 kg (BP‑05).

## 5. Traction, power, brakes

### 5.1 Traction: a terrain limit, not a machine limit
Climbing 25° needs a tractive force of (tan 25° + rolling resistance) × weight
= (0.47 + 0.12) ≈ **0.59 × weight on the tracks**.
This ratio **does not depend on load**: if a tracked machine can climb your
wet 25° clay slope empty, it can climb it full (sinkage aside). Rubber tracks
reach ~0.6–0.8 on dry soil but only ~0.4–0.6 on wet clay, so **steep wet
slopes may not be climbable after rain**. Mitigations:
- Aggressive lug tracks, low speed (less slip).
- **Put the base at the bottom of the grove if possible**: full bins then go
  downhill, which is easier and safer than climbing loaded.
- Slip detection (BP‑05): if a track slips > 30 %, stop, back down, report.
- "Wet day" mode: steep routes disabled from the dashboard.

### 5.2 Drive sizing (per track, gross 1,000 kg)
| Case | Force per track | Speed | Mech. power per track |
|---|---|---|---|
| Climb 25° | 2,600 N | 0.5 m/s | 1.3 kW |
| Flat, mud | 600 N | 1.0 m/s | 0.6 kW |
| Turn in place on flat (skid) | ~1,500 N | 0.3 m/s | 0.5 kW |

→ **Motor ≥ 2 kW continuous per track**, 2× peak for 30 s.
With a 120 mm sprocket radius: sprocket torque ≈ 360 Nm continuous,
~550 Nm peak; ~80 rpm at 1 m/s.

### 5.3 Brakes
Holding 1,000 kg on 25° = 4,150 N, × 1.5 safety = **6,200 N** → 3,100 N per
track → 370 Nm at the sprocket → **≥ 12 Nm at each motor shaft** with a ~35:1
gearbox. Use spring‑applied electromagnetic brakes, **≥ 16 Nm**, released only
by power. Power lost or E‑stop = braked.
Test T3 checks this on the real slope.

## 6. Frame drawings

### 6.1 Side view (dimensions in mm)
```
                 ┌──────────── BIN 1200 ────────────┐
                 │                                  │ 760
                 │                                  │
     bumper      └──────────────────────────────────┘
      ┌─┐   ════════════ LIFT DECK (BP‑02) ═══════════ ← top 450 low / 550 raised
      │ │  ┌───────────────────────────────────────┐   ┐
      │ │  │  frame rails RHS 100×50×4             │   │ track top ≈ 420
      │ │  │   [battery tray, lowest]  [e‑box]     │   │
      └─┘  └───────────────────────────────────────┘   ┘
         ( ◎ )═══════════ track contact 1300 ══════( ◎ )   ground clearance ≥ 200
          idler                                   sprocket+motor+brake
     |◄──────────────────── overall ≈ 1700 ───────────────────►|
```

### 6.2 Top view
```
      ◄──────────────── 1300 outer ────────────────►
      ┌──────┐                              ┌──────┐
      │TRACK │◄═ spacer beam RHS 100×100×5 ═►│TRACK │  ▲
      │ L    │                              │ R    │  │
      │ 250  │   ┌──────────────────────┐   │ 250  │  │
      │      │   │  BIN footprint       │   │      │  │ 1300
      │ M L  │   │  1200 × 1000         │   │ M R  │  │ contact
      │      │   │  (centred ±50)       │   │      │  │
      │      │◄═ spacer beam ═══════════════►│      │  │
      └──────┘   └──────────────────────┘   └──────┘  ▼
       track centre gauge 1050
       M = motor + gearbox + brake on each track frame
```

### 6.3 Front view: widening
```
   stock dumper ≈ 850              widened 1300
     ┌──┐┌───┐┌──┐            ┌──┐  ┌───────┐  ┌──┐
     │TL││ C ││TR│    ──►     │TL│══│   C   │══│TR│
     └──┘└───┘└──┘            └──┘  └───────┘  └──┘
                              225 spacer each side, 2 beams + diagonal brace
```

### 6.4 Fabrication notes
- Steel **S355** (S235 acceptable with the next size up). MIG welded.
- Spacer beams: 2 × **RHS 100×100×5** across, plus 1 × RHS 60×60×4
  diagonal brace in plan view (stops the track units twisting).
- Joints to the track frames: 10 mm end plates + **4 × M16 8.8 bolts** per
  joint (bolted, so tracks can be removed), 8 mm triangular gussets.
- Deck interface: 4 load‑cell pads, 10 mm plate, machined flat ±1 mm (BP‑02).
- Battery tray: 5 mm plate between the tracks, lowest point, ≥ 200 mm ground
  clearance kept.
- **Belly pan:** 6 mm HDPE under the whole centre against mud and stones.
- **Mud scrapers** at both ends of each track; drain holes in every closed box.
- Finish: zinc‑rich primer + 2‑part epoxy (or hot‑dip galvanise the beams).
- Lifting eyes at 4 corners for recovery if stuck.

## 7. Mass budget (target ≤ 420 kg)

| Part | kg |
|---|---|
| Dumper without skip (tracks, motors, frame) | 260 |
| Spacer beams, brace, plates | 45 |
| Lift deck + actuators (BP‑02) | 55 |
| Battery 48 V ~7.5 kWh LiFePO4 (BP‑03) | 60 |
| Electronics, sensors, bumpers, belly pan | 30 |
| **Total** | **450** ⚠ |

Over target by ~30 kg. That is acceptable for traction and power, but it
adds to sinkage. If the dumper already has a lithium battery, the extra
battery line goes away. Re‑check after buying.

## 8. Bill of materials (BP‑01 only)

| Item | Qty | Est. € |
|---|---|---|
| Electric tracked dumper, 800 kg class (new or good used) | 1 | 3,000–4,500 |
| RHS 100×100×5, RHS 60×60×4, plate 5/8/10 mm (S355) | lot | 180 |
| M16 8.8 bolts, nuts, washers | 32 | 40 |
| HDPE 6 mm belly pan | 1 m² | 60 |
| Mud scrapers (steel + rubber) | 4 | 40 |
| Primer + epoxy paint | lot | 60 |
| Spare brake + spare track (later) | — | — |
| **Total** | | **≈ 3,400–4,900** |

## 9. Tests for BP‑01

| # | Test | Pass criterion |
|---|---|---|
| T1 | Climb steepest wet slope, 500 kg sandbags, straight up & down | Climbs at 0.5 m/s, track slip < 30 %, stops and restarts mid‑slope |
| T2 | Static tilt sideways (one side on ramp, loaded, **strapped to a tractor**) | No wheel/track lift below 30° |
| T3 | Brake hold on 25°, loaded, power off | No creep in 10 min |
| T4 | E‑stop at 1 m/s on flat and on 25° downhill | Stops within 0.5 m (flat), 1.0 m (downhill), stays stable |
| T5 | Turn in place in a 4 m row, loaded, mud | Completes within a 2.4 m circle |
| T6 | 2 h mud run | No overheating (motors < 90 °C), tracks stay on |

T2 is a dangerous test. Do it slowly, with the machine strapped, and
**nobody downhill**.

## 10. Hand‑offs to other blueprints
- **BP‑02:** deck pads, 100 mm lift, deck top 450/550 mm, bin centred ±50 mm.
- **BP‑03:** battery tray size, 48 V, 2 × ≥ 2 kW motors (peak 2×).
- **BP‑04:** motor controller interface, brake release wiring through the safety relay.
- **BP‑05:** limits: pitch stop 28°, roll alarm 10°, roll stop 15° loaded; slip detection; wet‑day mode.
- **BP‑09:** E‑stop stopping distances (T4), tilt test (T2).
