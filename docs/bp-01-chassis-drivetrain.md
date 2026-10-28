# BP‑01 — Base & Top Frame (v0.4)

Part of the [BinBot wireframe](00-wireframe.md).
**Drawings & 3D:** [DWG‑001 general arrangement](../cad/out/DWG-001_general_arrangement.pdf) ·
[DWG‑002 top frame weldment](../cad/out/DWG-002_upper_frame_weldment.pdf) · [3D model](../cad/README.md).
All dimensions come from `cad/params.py`.

**Rev C rule (farmer): the bought base is not modified.** Its tracks, motors,
motor controllers, battery, charger and electronics stay exactly as delivered.
Everything we build is a **top module** bolted onto the base's top. Our only
connections to the base are a fused power tap, the drive‑command lead and its
E‑stop/enable input (BP‑04).

## 1. Design inputs

| Input | Value |
|---|---|
| Base | Electric rubber‑track undercarriage from AliExpress, ~€1,200, with motor controllers, battery, remote |
| Base size (assumed until the drawing arrives) | 1200 wide, 1700 long, tracks 400 high, flat top at **450 mm**, centre body 250 mm above ground |
| Payload | 500 kg olives + 40 kg bin = **540 kg** |
| Top module mass | ≈ 150 kg (frame 50, lift 60, E‑box 25, sensors 15) |
| Gross | **≈ 1,000 kg** (base ~300 kg assumed) |
| Slopes | 25° up/down the fall line; cross‑slope ≤ 9° loaded |
| Base station | Robot drives under bins on stands (BP‑02, DWG‑003) |
| Speed | 1.0 m/s flat, 0.5 m/s on slopes > 15°, 0.3 m/s at the base / near people |

## 2. Concept

```
   [E-box + masts]   [ bin on deck, lifts 100 mm ]   [low sensor bar ≤ 655]
   ────────────────── TOP MODULE: frame + lift ──────────────────  ← ours, bolted down
   ══════════════════ top of the bought base (450) ═══════════════
   ( O )════════════ BASE: tracks, motors, controllers, battery ═══( O )  ← vendor, unchanged
```

- **Top frame** (DWG‑002): 2 rails + 4 cross beams (RHS 100×50×4), sitting on 4
  base plates (10 mm) bolted **down** into the base top with M16, using the base's
  holes or rails. No drilling or welding on the base itself, except holes in its top
  plate if it has no fixing points (ask the seller).
- **Lift** in the frame: 2 parallel links per side in the end bays, 1 actuator per
  side in the middle bay (BP‑02).
- **Rear:** E‑box, GNSS masts, beacon. **Front:** low sensor bar with LiDAR, camera,
  E‑stops, ≤ 655 mm so it passes under bins on the stands.
- **No bumpers.** Ground clearance is whatever the base has.

## 3. What to ask the seller (no modifications, just facts)

Send this:

> Before ordering, please send for this undercarriage (1200 mm wide, ≥ 1000 kg load):
> 1. Drawing (PDF/STEP) with all dimensions, **top mounting holes / rails**, top height, ground clearance.
> 2. Battery: voltage, capacity (Ah), type, charger included?
> 3. Motors: power each, gearbox, **brake type** (does it brake when power is off?).
> 4. Motor controllers: can they be commanded by **CAN, RS485, or 0–5 V**? If only by the remote: receiver type (PWM / SBUS / PPM) and connector.
> 5. Is there an **emergency stop / enable input** we can connect to? 1 or 2 channels?
> 6. Rated load, max slope fully loaded, speed, weight, IP rating, CE declaration, price with shipping to Italy.
> 7. A video of it climbing 25° fully loaded.

If the listing offers options, choose: **1.2 m width, ≥ 1 t load, 48 V, the most
ground clearance, CAN/RS485 controllers.**

## 4. Stability (CoG computed part by part)

| Mass | kg | CoG height |
|---|---|---|
| Base (battery low, assumed) | 300 | 0.28 m |
| Top module | 150 | 0.62 m |
| Full bin on raised deck (795 + floor + half the olives) | 540 | 1.20 m |
| **Combined** | **≈ 990** | **≈ 0.83 m** |

| Direction | Half‑base | Static tip angle | Operating limit (loaded) |
|---|---|---|---|
| Sideways (track centre lines) | 0.475 m | **30°** | **9° cross‑slope**, alarm 7°, stop 12° |
| Fore/aft (contact 1.3 m) | 0.65 m | **38°** | **25° up/down**, stop at 28° pitch |

Building on top raises the CoG by about 8 cm compared with a frame between the
tracks. Up/down 25° keeps a 10° margin with gentle braking (0.5 m/s²). Rules:
bin centred ±50 mm over the tracks, no turning on slopes > 10°, loaded routes on
the fall line, software refuses cross‑slopes > 9° when loaded.

## 5. What the base must deliver (check against the seller's data)

| Need | Why |
|---|---|
| Traction: climb 25° fully loaded | needs ≈ 0.59 × weight in grip; wet clay may not allow it for any tracked machine, so put the base station at the bottom of the grove if possible |
| Motors ≥ 2 kW continuous each | 25° climb ≈ 3 kN per track at 0.5 m/s |
| **Brakes that hold when power is off** | 1,000 kg on 25° needs ≈ 6.4 kN with safety margin |
| Rated load ≥ 1,000 kg | 540 kg payload + 150 kg top module + margin |
| E‑stop / enable input | our safety relay must be able to stop the base (BP‑04 E‑02) |
| A way to command it (CAN / RS485 / RC receiver) | autonomy without opening the base |

## 6. Top frame (DWG‑002)

- 2 × RHS 100×50×4 rails, 600 mm apart, z 460–560 on 4 base plates (PL10 150×100, 4 × Ø18).
- 4 × RHS 100×50×4 cross beams → 3 bays: **end bays = lift links**, **middle bay = actuators**.
- 4 tabs: front pair carries the sensor bar, rear pair the E‑box.
- 8 link pivot plates, holes line‑bored in pairs.
- ≈ 52 kg of steel. S355, MIG, a4 fillets; primer + epoxy.

## 7. Bill of materials (BP‑01)

| Item | Qty | Est. € |
|---|---|---|
| Base: electric rubber‑track undercarriage 1.2 m with controllers, battery, remote (quoted) | 1 | 1,200 |
| RHS 100×50×4, plate 8/10 mm (S355) | lot | 140 |
| M16 8.8 bolts, nuts, washers | 16 | 25 |
| Primer + epoxy paint | lot | 50 |
| **Total** | | **≈ 1,415** |

## 8. Tests

| # | Test | Pass |
|---|---|---|
| T1 | Base alone: climb steepest wet slope with 500 kg sandbags, up & down | 0.5 m/s, slip < 30 %, stops and restarts mid‑slope |
| T2 | Static tilt sideways, loaded, **strapped to a tractor**, nobody downhill | No track lift below 27° |
| T3 | Brake hold on 25°, loaded, base switched off | No creep in 10 min |
| T4 | E‑stop (our button) at 1 m/s flat and 25° downhill | Base stops within 0.5 m / 1.0 m |
| T5 | Turn in place in a 4 m row, loaded, mud | Within a 2.4 m circle |
| T6 | Check nothing of ours hangs below the base top | Base clearance unchanged |

## 9. Hand‑offs
- **BP‑02:** frame top 560, deck 695/795, stand ledges 745, front ≤ 655.
- **BP‑03:** battery is the base's; our module draws ≈ 50–120 W + lift peaks.
- **BP‑04:** power tap, drive interface and E‑stop/enable input of the base.
- **BP‑05:** pitch stop 28°, roll alarm 7° / stop 12° loaded, slip detection, wet‑day mode.
