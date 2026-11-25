# DESUU: System architecture

Deliverable 1, part one. The launcher trade-off is in [decisions.md](decisions.md#d-001-launcher-snail-cam-spring-push-sled). Board and actuator choices are tracked as D-007 and D-008.

## Hardware blocks

```mermaid
flowchart LR
    subgraph HEAD["Turret head (pans and tilts)"]
        CAM["Camera"]
        MAG["Tube magazine, 24 pellets"]
        SHU["Shuttle, micro servo"]
        BRE["Breech + IR chamber sensor"]
        CAMR["Snail cam + worm-gear motor"]
        PLG["Spring push sled"]
        BAR["Barrel + 2 IR chronograph gates"]
        EYES["Round TFT eyes"]
        MAG --> SHU --> BRE
        CAMR --> PLG --> BRE --> BAR
    end
    subgraph BASE["Base"]
        SBC["Compute board: Linux + Python<br/>vision, aiming, fire control, modes"]
        MCU["Microcontroller: Pico or ESP32<br/>turret steps, launcher, feed, chronograph, watchdog"]
        PAN["Pan stepper + TMC2209<br/>3:1 belt"]
        TILT["Tilt stepper + TMC2209<br/>3:1 belt"]
        SPK["Speaker"]
    end
    CAM -->|"frames"| SBC
    SBC <-->|"USB serial: aim targets, commands, heartbeat, telemetry"| MCU
    MCU -->|"step / dir"| PAN
    MCU -->|"step / dir"| TILT
    MCU -->|"cock / fire"| CAMR
    MCU -->|"load"| SHU
    BRE -.->|"pellet present"| MCU
    BAR -.->|"gate times"| MCU
    MCU --> EYES
    SBC --> SPK
```

## Power and interlocks

```mermaid
flowchart LR
    IN["12 V DC in"] --> FUSE["Fuse"]
    FUSE --> BUCK5["Buck 12 V to 5 V"]
    BUCK5 --> LOGIC["Compute board + microcontroller<br/>(stays on: logs and shows state)"]
    FUSE --> ESTOP{{"E-stop, latching NC"}}
    ESTOP --> TURRET["Turret actuator rail"]
    ESTOP --> ARM{{"ARM switch with flip cover"}}
    ARM --> LAUNCH["Launcher rail: worm motor driver, shuttle servo"]
    LAUNCH -.->|"voltage divider: armed?"| SENSE["MCU input"]
```

- The ARM switch and the E-stop are **in series with actuator power**. They are not GPIO reads that software could ignore (REQ-SAF-004, -005).
- Logic power stays up through an E-stop, so the robot can still log, show its state and refuse to resume until reset.
- The microcontroller reads the *switched* launcher rail through a divider, so it knows the real armed state, not the switch position.

## Software

```mermaid
flowchart LR
    CAP["Camera capture<br/>timestamped frames"] --> FL["FaceLandmarker<br/>478 landmarks + blendshapes"]
    FL --> OBS["Face observations<br/>mouth centre and openness, eye zones,<br/>head pose, pupil distance"]
    OBS --> SEL["Target selection<br/>(mode)"]
    SEL --> RNG["Range estimator<br/>filtered, per-person calibration"]
    RNG --> BAL["Ballistics<br/>lookup: range, LOS elevation to offset"]
    BAL --> AIM["Aim controller<br/>PID on image error, latency compensation"]
    AIM --> TUR["Turret driver"]
    OBS --> FC["Fire control<br/>state machine + safety gates"]
    BAL --> FC
    AIM --> FC
    FC --> LINK["MCU link<br/>FIRE with sequence number"]
    LINK --> LOG["Shot log<br/>JSON lines"]
```

**Per frame** (target 30 FPS):

1. Capture a frame and stamp it with the capture time.
2. Run FaceLandmarker on the frame (or a crop around the last face).
3. Derive the observations:
   - mouth centre and inner-lip gap ratio, plus the `jawOpen` blendshape;
   - eye zones (eye landmarks + 15 mm);
   - head yaw and pitch;
   - pupil distance in pixels.
4. Update the range filter.
5. Look up the ballistic offset for (range, line-of-sight elevation).
6. The aim setpoint is the aim point shifted *down* in the image by that offset, because the camera rides on the barrel (D-003). The PID moves the turret to drive the aim point onto that setpoint. The turret angle at capture time comes from the actuator position history, so latency doesn't cause overshoot.
7. Fire control evaluates its gates and may send FIRE.

**Fire control** (REQ-SAF-001). Any state goes to SAFE when the launcher rail drops (disarm or E-stop), and to FAULT on any fault.

```mermaid
stateDiagram-v2
    [*] --> SAFE
    SAFE --> SEARCH: armed, ARM cycled since reset, self-test passed
    SEARCH --> TRACK: face found
    TRACK --> SEARCH: face lost for 1 s
    TRACK --> READY: consent gesture, 5 s window opens
    READY --> OPEN_WAIT: cocked, pellet loaded, mouth opens, static gates pass
    OPEN_WAIT --> READY: mouth closes or a gate fails
    READY --> TRACK: window expires, shuttle unloads
    OPEN_WAIT --> FIRE: open and steady 300 ms, aim settled, impact zone clear
    FIRE --> COOLDOWN: chronograph confirms the shot
    FIRE --> FAULT: no chronograph reading, or over-speed
    COOLDOWN --> TRACK: mouth closed and pacing allows
    FAULT --> SAFE: operator reset
```

The cam cocks on entering READY and decocks (reverse rotation) after 30 s without a shot (REQ-SAF-015).

**Gates checked every frame in OPEN_WAIT** (REQ-SAF-001; all must pass):

1. Armed: the launcher rail is live.
2. Exactly one face in the firing cone, tracked without a break since consent.
3. Mouth open with hysteresis, continuously for 300 ms, with no close-open cycling in the last second (talking, laughing, chewing).
4. Mouth steady: ≤ 15 mm/s.
5. Facing the robot: yaw within ±20°, head tipped back no more than 15°, eyes not shut.
6. Range ≥ 0.5 m and within the eye-safe auto-fire limit.
7. Aim error ≤ 0.15° per axis, averaged over 3 frames, for 100 ms.
8. 3σ impact ellipse clear of both eye zones.
9. Pellet chambered and cam parked.
10. Pacing: ≥ 10 s since this person's last shot, under the session cap, and this mouth opening not yet served.
11. Consent window open for this person.

The microcontroller re-checks the armed rail, heartbeat, token freshness, chamber, cam state and its own 5 s minimum interval (REQ-SAF-006), so a bug on the compute board cannot fire on its own.

## Timing budget

| Stage | Budget | Notes |
|---|---|---|
| Capture and transfer | ≤ 35 ms | Short exposure; good light helps |
| FaceLandmarker | ≤ 40 ms | Per-board numbers in research/vision-compute.md (D-007) |
| Control and command | ≤ 5 ms | |
| Actuator response | ≤ 30 ms | Small corrections once settled |
| **Camera to motion** | **≤ 100 ms** | REQ-PERF-008 |
| Fire decision to release | ≈ 45 ms | USB about 2 ms, cam past the drop about 40 ms, sled stroke about 5 ms |
| Flight at 1 m | ≈ 180 ms | [ballistics](research/ballistics.md) §3 |

## Microcontroller protocol (draft)

Line-based ASCII over USB CDC, each line `<seq> <CMD> [args] *<crc8>`, at 115200 baud or native USB speed.

| Direction | Message | Meaning |
|---|---|---|
| Board → MCU | `HB <board_ms>` | Heartbeat every 50 ms, carrying the board's clock; the MCU drops to SAFE after 200 ms of silence |
| Board → MCU | `AIM <pan_mdeg> <tilt_mdeg>` | Turret target angles, sent every frame; the MCU ramps the steppers within speed and acceleration limits |
| MCU → Board | `POS <mcu_us> <pan_mdeg> <tilt_mdeg>` | Turret angles at 100 Hz, so the board knows where the camera pointed when each frame was captured |
| Board → MCU | `COCK` / `DECOCK` | Turn the cam forward to the parked, cocked position, or reverse to relax the spring |
| Board → MCU | `LOAD` / `UNLOAD` | Shuttle one pellet against the sled face, or return it under the stack |
| Board → MCU | `FIRE <frame_ms>` | Release. Accepted once per sequence number, and only if armed, heartbeat fresh, the frame ≤ 100 ms old by the board clock, chambered, parked and ≥ 5 s since the last shot |
| Board → MCU | `SAFE` | Stop every actuator |
| MCU → Board | `STAT armed cam chamber mag` | State, sent 10 times a second |
| MCU → Board | `SHOT <seq> <t1_us> <t2_us> <v_mps>` | Chronograph result for each shot |
| MCU → Board | `FAULT <code>` | Over-speed, jam, cam timeout, watchdog |

## Planned repository layout

```text
desuu/              Python package that runs on the robot and on the PC
  vision/           camera back ends, FaceLandmarker wrapper, mouth-open, eye zones, range estimate
  control/          PID, visual-servo aim controller, latency compensation
  ballistics/       lookup table, model, calibration fit
  fire/             fire-control state machine and safety gates
  hw/               turret and microcontroller drivers plus fakes for --sim
  modes/            auto-serve, table service, manual target
  app.py            main loop
firmware/           microcontroller code (MicroPython)
cad/                CAD sources plus STEP/STL exports
config/             desuu.yaml (tunables), calibration.yaml (per robot)
tests/              pytest, safety gates first
tools/              ballistics_sim.py, calibration scripts
docs/               brief, requirements, architecture, decisions, safety, roadmap, research
```
