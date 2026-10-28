# BP‑01 — Chassis & Drivetrain (v0.2)

Part of the [BinBot wireframe](00-wireframe.md).
**Drawings & 3D model:** [DWG‑001 general arrangement](../cad/out/DWG-001_general_arrangement.pdf),
[DWG‑002 upper frame weldment](../cad/out/DWG-002_upper_frame_weldment.pdf),
[3D model](../cad/README.md). Dimensions there are generated from `cad/params.py`. This blueprint covers the
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

**Chosen: buy a complete electric rubber‑track undercarriage, 1.2 m wide**
(tracks, sprockets, idlers, rollers, motors, gearboxes, brakes), and weld the
upper frame yourself: deck supports, battery tray, e‑box mounts, bumpers.

- No dumper to strip or widen. The drivetrain is a proven set.
- 1.2 m outer width is wide enough for **up/down 25°** with a full bin. The
  cross‑slope limit becomes 10° loaded (§4). That is fine because your slopes
  run up and down.
- Bin (1000 mm across) fits inside the track width, so nothing hangs over the side.

## 3. Buying checklist for the undercarriage

Must have:
- [ ] **Outer width 1.2 m**, track width 230–250 mm, aggressive lug pattern
- [ ] **Track contact length ≥ 1.3 m** (1.2 m minimum, see §4 fore/aft margin)
- [ ] **Electric**, 48 V, **one motor per track**, ≥ 2 kW continuous each (§5.2)
- [ ] **Spring‑applied electromagnetic brake** on each motor, ≥ 16 Nm (§5.3)
- [ ] **Rated load ≥ 1,000 kg** (gross ≈ 960 kg)
- [ ] Ground clearance ≥ 200 mm
- [ ] Flat mounting pads or rails on top to weld/bolt the upper frame
- [ ] Motor controllers included with analogue/CAN inputs, or motors with
      encoders we can drive from our own controllers (BP‑04)
- [ ] Sealed bearings, track tensioner (grease cylinder), spare tracks available

Ask the seller for: drawing with mounting holes, motor and brake datasheets,
weight, and rated slope. Send them to me and I'll check them against this list.

**Before paying:** ask for a demo, or a video of it climbing 25° loaded.
After delivery, run test T1 on your steepest wet slope before building
anything on top.

## 4. Stability

Centre of gravity (CoG), bin carried on the raised deck:

| Mass | kg | CoG height |
|---|---|---|
| Robot (tracks low, battery lowest) | 420 | 0.45 m |
| Full bin (deck top 0.58 m + floor + half the olive load) | 540 | 0.98 m |
| **Combined** | **960** | **≈ 0.75 m** |

Static tip angle = atan(half‑base ÷ CoG height):

| Direction | Half‑base | Tip angle | Operating limit (loaded) |
|---|---|---|---|
| Sideways, **1.2 m undercarriage** (track centre lines, conservative) | 0.48 m | **32°** | **10° cross‑slope**, alarm 8°, stop 13° |
| Fore/aft, contact length 1.3 m | 0.65 m | **41°** | **25° up/down**, stop at 28° pitch |
| Fore/aft, contact length 1.2 m | 0.60 m | 39° | 25° only with braking ≤ 0.3 m/s² |

Margins:
- **Sideways:** a 10 cm rut under one track adds ~5°. Bumps add more. A
  factor of about 3 is kept for that.
- **Fore/aft:** 25° slope + 6° for a 1 m/s² braking stop = 31°, which is
  8–10° below tipping. So on slopes over 15°: speed 0.5 m/s and gentle braking
  (0.5 m/s²).

Design rules:
1. **Bin centre within ±50 mm of the track contact patch centre** (fore/aft
   and sideways).
2. Battery on the lowest possible tray, between the tracks.
3. Deck raised **only as much as needed** to clear the stands (target 100 mm).
4. No turning on slopes > 10°. Turn on the flat ends of rows.
5. Loaded routes follow the fall line. The software refuses routes where
   cross‑slope > 10° with load > 100 kg (BP‑05).

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
      ┌─┐   ════════════ LIFT DECK (BP‑02) ═══════════ ← top 480 low / 580 raised
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
      ◄──────────────── 1200 outer ───────────────►
      ┌──────┐                          ┌──────┐
      │TRACK │═══ cross beam RHS 100×50×4 ═══│TRACK │  ▲
      │ L    │  ┌──────────────────────┐ │ R    │  │
      │ 250  │  │  BIN footprint       │ │ 250  │  │
      │      │  │  1200 × 1000         │ │      │  │ ≥ 1300
      │ M L  │  │  (centred ±50)       │ │ M R  │  │ contact
      │      │  └──────────────────────┘ │      │  │
      │      │═══ cross beam ════════════│      │  │
      └──────┘                          └──────┘  ▼
       track centre gauge ≈ 950
       M = motor + gearbox + brake (supplied with undercarriage)
```

### 6.3 Front view: upper frame
```
            ┌──────── deck (BP‑02) ────────┐
            │ LC                       LC  │   LC = load‑cell pad
        ┌───┴──────────────────────────────┴───┐
        │  upper frame: 2 rails + 3 cross beams │ ← you weld this
        └──┬────────────────────────────────┬──┘
     ┌─────┴─┐   [battery tray, lowest]  ┌─┴─────┐
     │ TRACK │                           │ TRACK │ ← bought, 1200 outer
     └───────┘                           └───────┘
```

### 6.4 Fabrication notes
- Steel **S355** (S235 acceptable with the next size up). MIG welded.
- Upper frame (DWG‑002): 2 × **RHS 100×50×4** side rails **inside the gap
  between the tracks** (600 mm apart, underside 250 mm above ground),
  4 × RHS 100×50×4 cross beams, 2 × RHS 60×60×4 diagonal braces. ≈ 70 kg.
- Joints to the undercarriage: 4 side brackets, 10 mm plate, **4 × M16 8.8
  bolts** each, bolted to the inner faces of the track frames (bolted, so the
  undercarriage can be serviced). Hole positions to match the vendor drawing.
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
| Undercarriage (tracks, motors, brakes) | 250 |
| Upper frame weldment (DWG‑002) | 70 |
| Lift deck + actuators (BP‑02) | 55 |
| Battery 48 V ~7.5 kWh LiFePO4 (BP‑03) | 60 |
| Electronics, sensors, bumpers, belly pan | 30 |
| **Total** | **465** ⚠ |

Over target by ~45 kg. That is acceptable for traction and power, but it
adds to sinkage. Re‑check with the real undercarriage weight.

## 8. Bill of materials (BP‑01 only)

| Item | Qty | Est. € |
|---|---|---|
| Electric rubber‑track undercarriage, 1.2 m, ≥ 1 t, with motors & brakes | 1 | 2,500–4,000 |
| RHS 100×50×4, RHS 60×60×4, plate 5/8/10 mm (S355) | lot | 200 |
| M16 8.8 bolts, nuts, washers | 32 | 40 |
| HDPE 6 mm belly pan | 1 m² | 60 |
| Mud scrapers (steel + rubber) | 4 | 40 |
| Primer + epoxy paint | lot | 60 |
| Spare brake + spare track (later) | — | — |
| **Total** | | **≈ 2,900–4,400** |

## 9. Tests for BP‑01

| # | Test | Pass criterion |
|---|---|---|
| T1 | Climb steepest wet slope, 500 kg sandbags, straight up & down | Climbs at 0.5 m/s, track slip < 30 %, stops and restarts mid‑slope |
| T2 | Static tilt sideways (one side on ramp, loaded, **strapped to a tractor**) | No track lift below 28° |
| T3 | Brake hold on 25°, loaded, power off | No creep in 10 min |
| T4 | E‑stop at 1 m/s on flat and on 25° downhill | Stops within 0.5 m (flat), 1.0 m (downhill), stays stable |
| T5 | Turn in place in a 4 m row, loaded, mud | Completes within a 2.4 m circle |
| T6 | 2 h mud run | No overheating (motors < 90 °C), tracks stay on |

T2 is a dangerous test. Do it slowly, with the machine strapped, and
**nobody downhill**.

## 10. Hand‑offs to other blueprints
- **BP‑02:** lift bars sit on the rail tops (z 350), 100 mm lift, deck top 480/580 mm, bin centred ±50 mm.
- **BP‑03:** battery tray size, 48 V, 2 × ≥ 2 kW motors (peak 2×).
- **BP‑04:** motor controller interface, brake release wiring through the safety relay.
- **BP‑05:** limits: pitch stop 28°, roll alarm 8°, roll stop 13° loaded; slip detection; wet‑day mode.
- **BP‑09:** E‑stop stopping distances (T4), tilt test (T2).
