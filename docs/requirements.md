# DESUU: Requirements

Version 0.3, 2026-11-25 (phase 1 = joystick, [D-011](decisions.md#d-011-phase-1-joystick-aiming-face-tracking-moves-to-phase-2)). Derived from [brief.md](brief.md), the owner's answers and the research in [research/](research/). IDs are stable: cite them in code comments and tests (`# REQ-SAF-003`). The "Verify" column names a test in the test plan (deliverable 6).

Source key: **Brief** = stated in the brief. **Derived** = an engineering consequence of the brief (the reasoning is linked). **Proposed** = our suggestion, for the owner to confirm. **Owner** = the owner's own decision.

## Phases

The owner split the project in two (D-011):

- **Phase 1, joystick.** An operator aims with a wired joystick over a sight on the head, sets the range, and fires. No camera, no compute board, no face tracking. Fire control runs in the microcontroller.
- **Phase 2, face tracking.** The Pi 5 and camera come back for auto-aim, eye-zone gating, gesture consent and the auto modes.

Every requirement applies in both phases unless its row says **(phase 2)**. Phase 1 replaces the vision gates with REQ-SAF-017 (its own gate list) and REQ-SAF-018 (mandatory eye protection), and adds the controller requirements REQ-CTL-*.

## Performance

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-PERF-001 | Engage mouths at 0.5–2.0 m slant range from the muzzle. | Phase 1: hits a fixed target at 0.5, 1.0, 1.5 and 2.0 m with the range set on the dial. Phase 2: detects, tracks and, when the safety gates allow, fires at those ranges. | T-RNG | Brief |
| REQ-PERF-002 | Accuracy at 1.0 m: ≥ 90 % of shots inside a 30 mm circle centred on the aim point. | 30 consecutive shots at a face target 1.0 m away, at least 27 inside the circle. In phase 1 the target is fixed, at a measured range, aimed with the sight. | T-ACC-1 | Brief (A1) |
| REQ-PERF-003 | Exit speed 6.0 m/s nominal for a 1.3–1.5 g pellet, trimmable about ±15 % by spring preload. Heavier pellets run slower so every shot stays ≤ 30 mJ (about 5.5 m/s for 2.0 g). | Chronograph mean within ±3 % of the set point. | T-LAU-1 | Derived ([ballistics](research/ballistics.md), [safety](safety.md#energy-limits)) |
| REQ-PERF-004 | Exit-speed repeatability: SD ≤ 1.0 % over 30 shots from one pellet batch. | Chronograph SD ≤ 1.0 %, extreme spread ≤ 4 %. | T-LAU-1 | Derived |
| REQ-PERF-005 | Pointing error ≤ 0.12° (1σ per axis) once settled on a still face. | Phase 1: return-to-angle repeatability after holdover and after re-homing, from step counts and a dial gauge. Phase 2: logged angle between where the barrel points and where vision says it should. | T-TRK-1 | Derived |
| REQ-PERF-006 | Launch-direction scatter ≤ 0.15° (1σ per axis). | 30 shots at a paper target with the turret locked. | T-LAU-2 | Derived |
| REQ-PERF-007 | **(phase 2)** Range-estimate error ≤ 2.5 % (1σ) over 0.5–2.0 m after per-person calibration, ≤ 6 % uncalibrated. | Against a tape measure at 0.5 / 1.0 / 1.5 / 2.0 m, three people. | T-DST-1 | Derived |
| REQ-PERF-008 | **(phase 2)** Vision ≥ 25 FPS (floor 15 FPS) with one face; camera-to-servo-command latency ≤ 100 ms. | Frame and command timestamps in the log. | T-VIS-1 | Derived |
| REQ-PERF-009 | Mechanism cycle (fire → cocked and loaded again) ≤ 3 s. | Log timestamps. | T-LAU-3 | Proposed |
| REQ-PERF-010 | **(phase 2)** Re-acquire a face within 1 s after a brief loss. | Step out of view and back. | T-TRK-2 | Proposed |

### Error budget (allocation)

The accuracy requirement only holds if every error source stays inside its allocation. Numbers come from [research/ballistics.md](research/ballistics.md) at 6.0 m/s, 1.0 m, mouth 0.25 m above the muzzle.

| Source (1σ) | Allocation | Vertical at 1 m | Horizontal at 1 m | Owner of the number |
|---|---|---|---|---|
| Exit speed | 1.0 % | 3.0 mm | 0 | REQ-PERF-004 |
| Pointing | 0.12° per axis | 2.1 mm | 2.1 mm | REQ-PERF-005 |
| Launch scatter | 0.15° per axis | 2.6 mm | 2.6 mm | REQ-PERF-006 |
| Range estimate | 2.5 % | **4.0 mm (largest)** | 0 | REQ-PERF-007 |
| Head motion during the 179 ms flight | 15 mm/s | 2.7 mm | 2.7 mm | REQ-SAF-001 (c) |
| **Total (RSS)** | | **6.6 mm** | **4.3 mm** | 97 % hits (Monte Carlo) |

**Phase 1.** The range term comes from the tape marks instead of the face estimate: ±3 cm at 1 m is about 3 % (≈ 5 mm), slightly over the 2.5 % allocation, so people stay on their mark. Pointing is the operator's sight picture, not a measured error, and head motion is whatever the person does; both are verified on a fixed target first.

A 90 % hit rate needs σ ≤ 7.0 mm per axis, so the vertical axis has little slack. With the pessimistic budget (2 %, 0.25°, 0.35°, 6 %, 30 mm/s) the hit rate falls to 55 %. Range estimation is the biggest lever, then exit-speed consistency.

## Feed

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-FEED-001 | Magazine holds ≥ 20 pellets (target 24). | Load and count. | T-FEED-1 | Brief |
| REQ-FEED-002 | Single-piece feed: zero double feeds and ≤ 1 misfeed in 200 cycles with the chosen gum brand. | 200-cycle bench run. | T-FEED-2 | Brief |
| REQ-FEED-003 | A chamber sensor confirms exactly one pellet before any shot; an empty magazine is detected and announced. | Fault-injection tests. | T-FEED-3 | Derived |
| REQ-FEED-004 | Food path: the pellet touches only stainless or PTFE liners, or natural uncoloured PETG printed through a stainless nozzle (not the printer's stock nozzle). No resin, carbon-fibre-filled or wood-filled parts. Removable without tools, hand-washable. | Inspection. | T-INS | Derived ([safety research](research/safety-standards.md) §4) |
| REQ-FEED-005 | The feed is shape-keyed to the configured pellet and cannot chamber improvised objects. | Try a bead and a pebble. | T-INS | Derived (toy-standard practice) |

## Safety

Non-negotiable. The reasoning and hazard list live in [safety.md](safety.md).

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-SAF-001 | **(phase 2; phase 1 uses REQ-SAF-017)** Fire only when **all** gates pass in the same frame: (a) launcher rail live (armed); (b) exactly one face inside the firing cone; (c) mouth open continuously ≥ 300 ms with hysteresis, mouth steady (≤ 15 mm/s), and no close-open cycling in the last second (talking, laughing, chewing); (d) face toward the robot: yaw within ±20°, head tipped back no more than 15°, eyes not shut; (e) range ≥ 0.5 m and within the eye-safe auto-fire limit; (f) measured aim error ≤ 0.15° per axis, averaged over 3 frames, for ≥ 100 ms; (g) impact zone clear of both eye zones (REQ-SAF-002); (h) one pellet chambered and the cam parked; (i) pacing allows it (REQ-SAF-014); (j) a consent window is open for this person (REQ-SAF-013). | Unit test per gate plus live tests. | T-SAF-1 | Brief + Derived |
| REQ-SAF-002 | **(phase 2; phase 1 uses REQ-SAF-018)** Eye protection: the predicted impact ellipse (3σ, plus the worst-case over-speed the lockout allows) never overlaps an eye exclusion zone, defined as the eye landmarks expanded by 15 mm. | Unit tests on recorded faces; live test on a printed face target. | T-SAF-2 | Brief (A2) |
| REQ-SAF-003 | Exit energy ≤ 40 mJ, set by the **heaviest pellet configured** (≤ 7.0 m/s at 1.6 g, ≤ 6.3 m/s at 2.0 g) and guaranteed physically: the spring at maximum preload cannot exceed it. Operating ceiling 30 mJ. Every shot is chronographed; lock out after any shot more than 8 % above nominal or above the cap, or after a drift above 2 % over 10 shots. | Chronograph test at maximum preload with the heaviest pellet. | T-SAF-3 | Brief (A3) + [safety research](research/safety-standards.md) §2 |
| REQ-SAF-004 | A keyed or flip-covered ARM switch and the E-stop sit in series with the power of every launcher and feed actuator. Disarmed means those actuators are unpowered, whatever the software does. Driver gates have pull-downs, and no microcontroller boot or strapping pin drives an actuator. The microcontroller senses the switched rail and reports it. | Disarm in the middle of a fire sequence: nothing moves. Scope the drive lines through boot. | T-SAF-4 | Brief |
| REQ-SAF-005 | A latching emergency stop cuts all actuator power, turret included (IEC 60204-1 stop category 0). Releasing it does not restart anything. | Press it during motion; release it. | T-SAF-4 | Proposed |
| REQ-SAF-006 | **(phase 2 link; phase 1 checks are in REQ-SAF-017)** The microcontroller refuses FIRE unless: the rail is armed; a heartbeat (≥ 20 Hz, sequence number and CRC) arrived within 200 ms; the FIRE token is single-use, in sequence and refers to a frame ≤ 100 ms old by the board's clock; a pellet is chambered and the cam is parked; and ≥ 5 s have passed since the last shot. A hardware watchdog on its own clock resets it to SAFE. | Firmware fault-injection tests (replay, stale, dropped heartbeat). | T-SAF-5 | Derived |
| REQ-SAF-007 | Boot, reset, brown-out and every fault go to SAFE. After any reset the ARM switch must be cycled off and on before firing; nothing auto-resumes. | Power-cycle and brown-out tests. | T-SAF-5 | Derived |
| REQ-SAF-008 | No lasers or visible aiming beams. Any range sensor is an unmodified Class 1 module. | Inspection. | T-INS | Derived (A2) |
| REQ-SAF-009 | Adults only. The robot carries a choking-hazard label, and the manual gives the instructions in [safety.md](safety.md#information-for-use). | Label and manual. | T-INS | Derived |
| REQ-SAF-010 | The aim point sits in the lower half of the mouth opening (default 5 mm below centre), and the muzzle height gives a flat or descending entry at ≥ 1 m. | Config check plus test. | T-SAF-2 | Derived |
| REQ-SAF-011 | **(phase 2)** Auto-fire range is limited to where the live 3σ check passes (about 1.5 m with the target budget). Beyond that, the aim point moves down or the shot is refused. | Simulation plus live tests at 1.75 m and 2.0 m. | T-SAF-2 | Derived ([ballistics](research/ballistics.md) §4) |
| REQ-SAF-012 | Before each shot: an audible chirp and an eye animation ("open wide") at least 300 ms ahead. In phase 1 the chirp comes from the microcontroller's buzzer. | Observation. | T-UX | Proposed |
| REQ-SAF-013 | **(phase 2; phase 1: the target says they're ready, the operator holds ENABLE)** Consent: each shot needs an explicit opt-in (eyebrows raised about 1 s while looking at the robot, or the nose button), which opens a 5 s window for one shot. An open mouth alone never fires. | Live test, including yawns and laughter. | T-SAF-1 | Proposed ([safety research](research/safety-standards.md) §5) |
| REQ-SAF-014 | Pacing: ≥ 10 s between shots to the same person, the mouth must close in between, and at most 5 pellets per person per session (configurable). In phase 1, which can't tell people apart, the microcontroller applies ≥ 10 s between any two shots and 5 shots per arming. | Unit tests plus live test. | T-SAF-1 | Derived ([safety research](research/safety-standards.md) §3) |
| REQ-SAF-015 | Stored energy: never cock while disarmed. Reverse the cam to decock after 30 s without a target. With launcher power off, the breech ends up empty (spring-return shuttle or equivalent). | Power-cut and idle tests. | T-SAF-6 | Proposed |
| REQ-SAF-016 | Test safety: impact-rated glasses (ANSI Z87.1 / EN 166) for anyone in front of an armed robot until the phase 2 eye-gate tests pass (M10); armed testing starts on printed face targets. In phase 1 the glasses rule never lapses (REQ-SAF-018). | Test log. | T-INS | Derived |
| REQ-SAF-017 | **Phase 1 firing gates, all in the microcontroller's fire-control state machine (the only firing path):** (a) launcher rail live (armed) and the ARM switch cycled since the last reset; (b) turret homed; (c) ENABLE held continuously for ≥ 1 s before the FIRE press and through release; releasing it aborts and returns the tilt; (d) FIRE is a fresh press (one shot per press; holding it does nothing more); (e) joystick centred and turret still for ≥ 300 ms; (f) range set, 0.5–2.0 m; (g) one pellet chambered and the cam parked; (h) ≥ 10 s since the last shot and < 5 shots since arming; (i) chronograph healthy and no lockout; (j) controller connected (joystick readings in range). Then: holdover tilt, settle, ≥ 300 ms chirp, release, return. A hardware watchdog resets to SAFE. | Unit test per gate and per abort path (100 % branch coverage on the PC with fakes), then live tests disarmed and armed. | T-SAF-1, T-SAF-5 | Owner (D-011) + Derived |
| REQ-SAF-018 | **Phase 1 eye protection.** With no vision, nothing can check where the eyes are, so everyone in front of the armed robot wears impact-rated glasses (ANSI Z87.1 / EN 166) for every phase 1 session, with no exception. The operator aims at the lower lip, and the holdover table is biased short. Shooting at anyone not wearing them is misuse, and the manual says so. | Test log; manual review. | T-INS | Owner (D-011) + Derived |

## Build

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-BLD-001 | Parts cost ≤ ₹21,000 (≈ US$250) including compute board and camera, and as low as the spec allows. Phase 1 spends only the non-vision part of it. | BOM total, shown per phase. | T-INS | Brief + owner |
| REQ-BLD-002 | Every custom part prints on a 256 × 256 mm bed (Bambu Lab X1 Carbon). PETG (or ASA) for anything loaded or sliding; PLA only for cosmetic shell parts. | Slicer check. | T-INS | Brief + owner |
| REQ-BLD-003 | Friendly character: rounded shapes, expressive eyes, sounds. The muzzle reads as the character's mouth, not a gun barrel. | Owner sign-off. | T-UX | Brief |
| REQ-BLD-004 | Footprint ≤ 220 × 220 mm; muzzle about 250 mm above the desk, so the pellet enters a seated person's mouth flat or descending at ≥ 1 m. | CAD check. | T-INS | Derived ([ballistics](research/ballistics.md) §5) |
| REQ-BLD-005 | Pan range ±170° without a slip ring; tilt −15° to +45°. | CAD check and test. | T-TRK-1 | Derived (table mode) |
| REQ-BLD-006 | One DC input (12 V) feeds the whole robot, or the docs explain why two are needed. | Wiring review. | T-INS | Proposed |

## Modes

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-MODE-001 | **(phase 2)** Auto-serve: track the nearest consenting face and serve when every gate passes. | Live test. | T-MODE-1 | Brief |
| REQ-MODE-002 | **(phase 2; a manual version works in phase 1)** Table service: sweep ±170°, list faces by bearing, serve each person who opts in once per round, skip anyone who doesn't within 10 s. | Live test with 3 people. | T-MODE-2 | Brief |
| REQ-MODE-003 | Manual target (trick shots): an operator aims with the joystick. This is phase 1's only mode. The energy cap and the ARM chain always apply; in phase 2 every face-related gate also applies to any face inside the firing cone. | Live test. | T-MODE-3 | Brief |

## Controller (phase 1)

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-CTL-001 | A wired handheld controller on a cable of at least 2 m: 2-axis analog joystick, ENABLE (deadman), FIRE, RANGE − and RANGE +. Unplugging it, or a broken wire, reads as ENABLE released and goes to SAFE. | Pull the plug mid-sequence; cut each wire in turn. | T-CTL-1 | Owner (D-011) |
| REQ-CTL-002 | Rate control with a deadband of at least 8 % and an expo curve: about 2°/s at small deflection, up to 60°/s pan and 30°/s tilt at full deflection. Stick to step-rate latency ≤ 50 ms. Software limits keep the turret inside pan ±170° and tilt −15° to +45°, holdover included. | Log stick and step timestamps; drive into each limit. | T-CTL-2 | Owner (D-011) |
| REQ-CTL-003 | Range set in 0.1 m steps from 0.5 to 2.0 m and shown on the base display (default 1.0 m at power-up). On FIRE, the turret adds the ballistic offset for the set range and its current elevation from the calibrated table, biased short, then returns to the sight angle within 0.05°. | Fixed-target tests at 0.5 / 1.0 / 1.5 / 2.0 m; return-angle log. | T-CTL-3, T-ACC-1 | Owner (D-011) |
| REQ-CTL-004 | A printed, adjustable sight on the turret head (rear notch, front post), zeroed at 1.0 m during calibration. No lasers. | Zeroing procedure; inspection. | T-CAL-1 | Owner (D-011) |
| REQ-CTL-005 | Status without a computer: a 0.96" OLED on the base shows SAFE/ARMED, range, shots left before re-arm, and the last measured speed; every shot is also printed over USB as a JSON line for a laptop to log (REQ-SW-004). | Observation; log review. | T-CTL-1 | Derived |

## Software

| ID | Requirement | Acceptance criterion | Verify | Source |
|---|---|---|---|---|
| REQ-SW-001 | Python 3. Phase 1: the microcontroller firmware is MicroPython, and its fire-control and joystick logic also runs under CPython on the dev PC with fakes. Phase 2: runs on the robot, and on a Windows dev PC with a webcam and simulated hardware (`--sim`). | Phase 1: pytest passes on the PC. Phase 2: both start and track a face. | T-SW-1 | Derived |
| REQ-SW-002 | All hardware sits behind interfaces with fakes. The safety gates and the fire-control state machine have 100 % branch coverage in unit tests. | Coverage report. | T-SW-2 | Derived |
| REQ-SW-003 | All tunables live in one YAML config; calibration in a separate file. | Review. | T-SW-1 | Proposed |
| REQ-SW-004 | Every shot is logged as a JSON line (time, range, angles, gate results, measured exit speed) for the accuracy analysis. | Log review. | T-ACC-1 | Derived |
