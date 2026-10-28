# BinBot — System Wireframe (v0.2)

Autonomous tracked bin carrier for an ~8,000‑tree olive grove in Tuscany.
This document is the **wireframe**: what the system is, how its parts connect,
how it operates, and how it stays safe. Detailed blueprints (dimensions,
parts, wiring, code) come next, one per subsystem (see §9).

> v0.2 — updated with the farmer's answers (§10) and the €8k budget (§11).

---

## 1. Mission in one paragraph

A tracked robot carries one harvest bin to a predefined spot in the grove.
Harvesters tip their olives into the bin while the robot weighs it
continuously. When the bin reaches its target weight (or a harvester presses
"SEND"), the robot drives back to the **base**, parks the full bin on a stand,
picks up an empty bin, and returns to the same (or next) spot. It repeats all
day, recharging briefly at every base visit.

## 2. Key requirements & starting assumptions

| Item | Target | Status |
|---|---|---|
| Grove | ~8,000 trees, rows 4 m apart, farthest spot ~1 km from base | confirmed |
| Bin | Standard ag bin 1200 × 1000 × ~750 mm, ~40 kg empty | confirmed |
| Payload | Up to 500 kg olives + bin → **design for 600 kg** | confirmed |
| Terrain | Mud, ruts, stones, slopes up to **25°** (≈ 47 %) | confirmed, see §8 |
| Speed | 1.0 m/s max loaded, 0.3 m/s near people / at base | lowered for safety on budget (§7) |
| Team | ~5 harvesters per spot → ~150–300 kg/h → full bin every ~2–3 h | estimate |
| Day | Daylight only, 8–10 h, ~3–5 bin trips, ≤ 10 km driven | estimate |
| Weighing | ±1 kg indicative on robot; **certified scale at base** (pickers paid by kg) | confirmed |
| Base | Mains power available | confirmed |
| Weather | Light rain, mud, dust: IP65 electronics, IP67 connectors | |
| Fleet | **1 robot** | confirmed |
| Budget | **~€8,000** | confirmed, see §11 |

## 3. System overview

```mermaid
flowchart LR
  subgraph FIELD[Grove]
    H[Harvester team<br/>handheld pendant / phone]
    R[BinBot robot]
  end
  subgraph BASE[Base station]
    S[Bin stands<br/>full / empty lanes]
    C[Charge plug]
    SRV[Base computer<br/>fleet manager + map + logs]
    RTK[RTK GNSS reference]
    SC[Certified scale<br/>optional]
  end
  FARM[Farmer<br/>tablet / phone dashboard]

  H -- call / send / stop --> R
  R -- telemetry, weight, status --> SRV
  SRV -- missions, routes --> R
  RTK -- corrections --> R
  R -- drop full / take empty --> S
  R -- charge --> C
  SRV <--> FARM
```

## 4. Robot subsystems

### 4.1 Physical layout (rev C, see [DWG‑001](../cad/out/DWG-001_general_arrangement.pdf) and the [3D model](../cad/README.md))

```
  GNSS ×2 (rear corners, 1 m apart)
    ▲  beacon
 ┌──┴──┐ ┌──────────────── BIN 1200 ────────────────┐
 │     │ │                                          │  ← bin on raised deck (685)
 │  E  │ │                                          │
 │  B  │ └──────────────────────────────────────────┘
 │  O  │ ══════ DECK on 4 load cells, lifts 100 ══════
 │  X  │   links      [actuators]      links          ← lift inside the top frame (460–560)
 └─────┘ ════════ top of the BOUGHT BASE (450), unchanged ═══ [LiDAR, E-stops] ← front ≤ 655
   ( O )═══ base: tracks, motors, controllers, battery (vendor) ═══( O )
 REAR (tall parts)                                FRONT (low: drives under bins)
```

### 4.2 Base & top frame (→ [BP‑01](bp-01-chassis-drivetrain.md))
- **Bought electric rubber‑track base, 1.2 m wide, NOT modified:** tracks, motors,
  brakes, motor controllers, battery, charger and remote stay as delivered.
- **Top module** bolted down onto it: welded frame (DWG‑002), lift, E‑box, sensors.
- Building on top raises the CoG to ≈ 0.85 m: 25° up/down OK, cross‑slope ≤ 9° loaded.
  Stability drawing: [DWG‑004](../cad/out/DWG-004_stability.pdf). Road mode: full bin carried with the deck lowered.
- The base must have brakes that hold when power is off, ≥ 2 kW per motor, ≥ 1 t load,
  an E‑stop/enable input and a way to command it (CAN/RS485/RC receiver).

### 4.3 Bin handling & weighing (→ [BP‑02](bp-02-bin-swap-weighing.md), [video](../cad/out/bin_swap.mp4))
- **Drive‑under swap:** the robot drives under a bin standing on a steel stand,
  lifts its deck 100 mm to take it, lowers 100 mm to leave it, and reverses out.
  No forks, no crane, nobody at the base. The bin never leaves the robot in the grove.
- Lift: 2 parallel links + 1 actuator per side, all inside the frame height.
- **4 load cells** under the deck → live weight while filling (alert 450 kg,
  max 500 kg), IMU tilt correction, read only when still.
- Official weight: the FULL bays stand on certified load cells (§5).

### 4.4 Power (→ BP‑03)
- **The base's own battery and charger.** The top module takes a fused tap
  (40 A) from it: ≈ 50–120 W continuous + 480 W lift peaks, ≈ 0.5–0.7 kWh a day.
- Separate low‑voltage rails (24/12 V) for computers & sensors.
- **Safety path:** our safety relay opens the base's E‑stop/enable input
  (base motors stop, its brakes clamp) and our lift contactor.

### 4.5 Electronics & compute (→ BP‑04)
| Layer | Role | Example class |
|---|---|---|
| Safety controller | E‑stop chain, safety edges, LiDAR safety fields, brake & contactor | Certified dual‑channel safety relay |
| Motion controller | Motor drives, track odometry, lift actuators, load cells | Industrial MCU / PLC (CAN bus) |
| Main computer | Navigation, perception, mission logic, comms | Small rugged PC / Jetson Orin Nano‑class, ROS 2 |

Main computer can **request** motion; only the safety controller can
**permit** it.

### 4.6 Navigation & perception (→ BP‑05)
- **Localisation**: dual‑antenna RTK GNSS (u‑blox F9P‑class, own reference receiver at base) (position + heading) fused with IMU
  and track odometry. Olive canopy degrades GNSS → add **LiDAR‑based
  localisation** against a pre‑recorded map of tree rows as fallback.
- **Route graph**: farmer drives the robot once (teach mode) along tracks
  between rows; robot only drives on these taught paths. Predefined spots =
  named nodes on the graph.
- **Obstacle & person detection**: one 3D LiDAR + front/rear cameras; stops
  for people, slows for objects, waits if a path is blocked. The LiDAR is
  **not safety‑rated** (budget), so it is backed by safety edges, low speed and
  operating rules (§7).
- **Terrain awareness**: IMU tilt/roll limits, track slip detection (odometry
  vs GNSS), "stuck" detection → stop and call for help.

### 4.7 Communications (→ BP‑07)
- **LTE/4G** primary (telemetry, RTK corrections via base or NTRIP).
- **Long‑range radio (LoRa / 868 MHz)** backup for heartbeat, stop and status
  where coverage is poor.
- **Handheld pendant** for harvesters: CALL, SEND, STOP (+ wireless E‑stop on
  a separate safety radio).

### 4.8 Software (→ BP‑06)

```mermaid
flowchart TB
  UI[Farmer dashboard & harvester app] --> FM[Fleet manager - base]
  FM --> MM[Mission manager - robot]
  MM --> NAV[Navigation: localisation + path follow]
  MM --> BIN[Bin & weighing manager]
  NAV --> PER[Perception: obstacles / people]
  NAV --> MC[Motion controller]
  BIN --> MC
  PER --> SAF
  MC --> SAF[Safety controller - independent]
  SAF -->|permit / cut| DRV[Motors & brakes]
  LOG[(Logs: weights, routes, events)] --- FM
```

## 5. Base station (→ BP‑08, stands in [BP‑02](bp-02-bin-swap-weighing.md) / [DWG‑003](../cad/out/DWG-003_bin_stand.pdf))

```
      yard (robot turns here)          bays 2.2 m apart, open both ends
   ───────────────────────────►  [ FULL bay  — on certified scale ]  → tractor takes full bins out the front
   ───────────────────────────►  [ FULL bay  — on certified scale ]
   ───────────────────────────►  [ EMPTY bay ]                       → robot leaves forward with the empty bin
   ───────────────────────────►  [ EMPTY bay ]
   charge plug · base PC + RTK reference + 4G router + UPS in a cabinet · fenced
```
- Each bay: 4 posts + 2 ledges at 745 mm, ground guides centre the tracks to ±30 mm,
  AprilTag + reflectors for the LiDAR.
- FULL bays stand on 4 load cells each with a certified indicator: official
  weight of every bin, logged with spot, team and time.
- Mains power: overnight charger, base computer. Fenced zone, 0.3 m/s inside.

## 6. Operating cycle

```mermaid
stateDiagram-v2
  [*] --> Idle_at_base
  Idle_at_base --> Pick_empty_bin: mission assigned
  Pick_empty_bin --> Drive_to_spot
  Drive_to_spot --> Waiting_filling: arrived
  Waiting_filling --> Waiting_filling: weighing (live)
  Waiting_filling --> Drive_to_base: SEND pressed (people clear)
  Drive_to_base --> Drop_full_bin
  Drop_full_bin --> Official_weighing
  Official_weighing --> Pick_empty_bin: next mission
  Official_weighing --> Idle_at_base: no mission / end of day
  Drive_to_spot --> Safe_stop: hazard / fault
  Drive_to_base --> Safe_stop: hazard / fault
  Waiting_filling --> Safe_stop: tilt / fault
  Safe_stop --> Drive_to_spot: cleared + resumed
  Safe_stop --> Drive_to_base: cleared + resumed
  Safe_stop --> Manual_mode: operator takeover
  Manual_mode --> Idle_at_base
```

**Weight rules** (configurable): alert at 450 kg ("almost full"), hard max
500 kg olives (buzzer, "STOP FILLING", refuses to move above max).
The robot **never leaves on its own**: a harvester presses SEND after
checking that nobody is next to it.

## 7. Safety concept (→ BP‑09)

Layered: if one layer fails, the next still protects people.

| # | Layer | What it does |
|---|---|---|
| 1 | **Design** | Low CoG, limited speed, guarded pinch points on lift & tracks, no sharp edges |
| 2 | **Emergency stop** | 4 mushroom buttons on robot + wireless E‑stop on pendant (signal lost → stop) + remote stop from base; hard‑wired, cuts drive power, brakes engage |
| 3 | **Fail‑safe brakes** | Spring‑applied: power loss = robot stopped and held, also on slopes |
| 4 | **Person/obstacle detection** | LiDAR slow/stop zones (not safety‑rated on this budget) **plus hard‑wired safety edges** on the front sensor bar and rear E‑box (no low bumpers: rocks) |
| 5 | **Speed & zone limits** | Slow near people, at base, in steep zones; **geofence** — never leaves taught paths |
| 6 | **Stability** | Tilt/roll limits with load‑dependent thresholds; refuses routes too steep for current weight; deck lowered while driving |
| 7 | **Overload** | Will not move above max weight; lift won't operate unless robot stopped & level |
| 8 | **Watchdogs** | Lost comms / lost localisation / software crash / sensor fault → controlled stop |
| 9 | **Awareness** | Rotating amber beacon, status light bar, buzzer before moving, display with state |
| 10 | **Operations** | Harvester briefing, high‑vis, robot never approaches a person to < 1 m, manual mode only with pendant held (dead‑man) |
| 11 | **Records** | Black‑box log of every stop, fault and near miss |

**Budget trade‑off:** a certified safety LiDAR (€2–4k) does not fit €8k.
Compensation: max 1 m/s, 0.3 m/s near people and base, departure only on
SEND, harvesters stay off the travel paths, safety edges and E‑stops hard‑wired.
Pickers are workers, so Italian **D.Lgs. 81/2008** applies: have the risk
assessment reviewed by your RSPP / safety consultant before use with staff.

**Standards to design against** (to confirm with a certifier):
EU Machinery Regulation (EU) 2023/1230 (applies from Jan 2027),
ISO 18497 (safety of highly automated agricultural machines),
ISO 25119 (functional safety, ag machinery), ISO 13849 (safety control
systems), ISO 12100 (risk assessment), IEC 60204‑1 (electrical),
EMC & Radio Equipment Directives (CE marking).

## 8. Key risks to resolve early

1. **25° slopes with 500 kg**: the hardest requirement. Slopes are up/down
   (confirmed). Stability is OK (BP‑01 §4), but traction on **wet** clay at 25°
   is borderline for any tracked machine (BP‑01 §5.1). Cross‑slope limited to
   10° loaded.
2. **Traction on wet clay** → test the undercarriage on your worst slope, loaded, before buying the rest.
3. **GNSS under olive canopy** → field survey with an RTK receiver before buying sensors.
4. **Docking precision in mud at base** → gravel/concrete pad at base.
5. **Budget**: €8k only with low‑end choices; battery and electronics are the main unknowns (§11, BP‑04).
6. **Worker safety compliance** (§7).

## 9. Blueprint roadmap (next documents)

| ID | Blueprint | Contents |
|---|---|---|
| [BP‑01](bp-01-chassis-drivetrain.md) | Chassis & drivetrain | Frame drawings, track/motor sizing, traction & slope calcs |
| [BP‑02](bp-02-bin-swap-weighing.md) | Bin swap & weighing | Drive‑under swap, base stands, lift, weighing, video |
| BP‑03 | Power system | Energy budget, battery, BMS, charging dock, power distribution |
| [BP‑04](bp-04-electronics-wiring.md) | Electronics & wiring | Block & wiring diagrams, enclosures, CAN bus, connectors |
| BP‑05 | Navigation & perception | Sensors, mounting, localisation fusion, teach & repeat |
| BP‑06 | Software architecture | ROS 2 nodes, state machine, interfaces, fleet manager |
| BP‑07 | Communications | LTE / LoRa / pendant, RTK corrections, coverage plan |
| BP‑08 | Base station | Bin stands, lanes, docking, power, layout drawing |
| BP‑09 | Safety | Hazard analysis, safety functions, PL ratings, E‑stop circuit |
| BP‑10 | Operations & HMI | Pendant, apps, dashboard, daily procedure |
| BP‑11 | Test & validation | Bench, field, safety and acceptance tests |

## 10. Farmer's answers & remaining questions

Answered: bin size ✔ · payload 500 kg · slopes 25° · rows 4 m · farthest
spot ~1 km · ~5 harvesters per spot · paid by weight → certified scale ·
mains at base · daylight only · 1 robot · budget ~€8k.

Also answered: 25° is **up/down** the hill · farmer welds and wires ·
4G coverage across the grove ✔.

## 11. Budget (target €8,000, parts only, own labour)

| Item | Estimate (€) |
|---|---|
| Base: electric rubber‑track undercarriage 1.2 m with controllers + battery (quoted) | **1,200** |
| Lift: 2 actuators, links, deck (BP‑02) | 400–650 |
| 4 load cells + weighing amplifier | 200–300 |
| RTK GNSS: 2 rover + 1 base receiver, antennas | 700–900 |
| Main computer | 300–600 |
| 3D LiDAR + 2 cameras | 800–1,100 |
| Electronics (BP‑04): power tap, safety circuit, MCU, comms, E‑box, wiring | 2,000–3,350 |
| Base: 1 FULL (certified load cells) + 1 EMPTY stand; +€1k for 2 + 2 | 950–1,450 |
| **Total** | **≈ 6,550–9,550** |

**Automatic navigation is a core requirement**, not an option. After the
detailed electronics list (BP‑04 §7) the total is **≈ €6,550–9,550**: €8k is
reachable only with low‑end choices (see BP‑04 savings). Keep ~€1k contingency.
Build order, so problems show up early and cheaply:

- **Step 1: drive base (≈ €4,900 at low‑end prices).** Base + top frame, lift, weighing, E‑stops,
  pendant, base stands and scale. Tested by remote control to prove
  traction and stability in your mud before buying sensors.
- **Step 2: autonomy (≈ €2,000–2,600).** RTK, LiDAR, computer, software →
  the robot drives the taught routes by itself. This is the finished robot.

Not included: anything the €1,200 base turns out not to include (battery, charger), workshop labour, safety consultant.
