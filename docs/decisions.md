# DESUU: Decision log

Each entry records context, the decision, the alternatives and what it costs us. Status is **Proposed** until the owner approves it, then **Accepted**. If a decision changes later, add a new entry that supersedes the old one; never rewrite history.

| ID | Decision | Status |
|---|---|---|
| D-001 | Launcher: snail-cam spring "push sled" with a sled about 3× the pellet's mass; fixed speed, elevation-only aiming | Proposed |
| D-002 | "Never aim at eyes" is enforced on the predicted impact zone, not on the barrel direction | Proposed, phase 2 (D-011) |
| D-003 | Camera rides on the turret head, tilted about 10° down from the barrel | Proposed, phase 2 (D-011) |
| D-004 | Two processors plus a hardware interlock chain | Proposed |
| D-005 | Distance from face landmarks with per-person calibration, biased short | Proposed, phase 2 (D-011) |
| D-006 | Feed: orientation-locking gravity stack with a spring-return shuttle | Proposed |
| D-007 | Compute: Raspberry Pi 5 1 GB with an OV5647 camera, bought last (out of stock in India) | Proposed, phase 2 (D-011) |
| D-008 | Turret actuators: NEMA17 steppers on TMC2209 drivers through 3:1 GT2 belts | Proposed |
| D-009 | Consent: an explicit opt-in per shot | Proposed; phase 1 form in D-011 |
| D-010 | Design pellet: hard-coated, non-liquid, 1.3–1.5 g | Proposed |
| D-011 | Phase 1 aims with a wired joystick; face tracking, the camera and the Pi move to phase 2 | **Accepted** (owner, 2026-11-25) |

---

## D-001 Launcher: snail-cam spring push sled

**Context.** The launcher must deliver about 6.0 m/s with ≤ 1 % shot-to-shot scatter ([ballistics](research/ballistics.md)), never exceed 40 mJ of pellet energy (REQ-SAF-003), fire one pellet per command, re-cock within 3 s, stay quiet enough for a desk, be printable and cheap, and touch the gum only with food-safe parts. The projectile is awkward: a rigid, pillow-shaped, slippery-coated pellet of 1.3–1.5 g whose size and mass vary from piece to piece.

**Evidence** ([launcher research](research/launcher-prior-art.md)):

- **Consistency depends on running at design energy.** Analogous launchers reach 1–2 % speed SD only at the energy they were designed for. The same foam springer gives 1.0 % on a strong spring and 13 % on a weak one. Regulated air gives 2.0 % against 12.7 % for unregulated CO2.
- **Prior candy launchers failed on ammunition and feeders, not vision.** Popcorn shapes, marshmallows that changed after an hour out of the bag, and jams at the loader-to-chute ledge.
- **A single flywheel spins the pellet** (spin parameter ≈ 1). Magnus lift then shifts the impact about 6 mm at 1 m and 24 mm at 2 m.
- **Pneumatics are unreliable here.** A pillow pellet can't seal a bore, and only 0.1–0.3 bar is needed, which is hard to regulate finely. RoboCup's ER-Force dropped pneumatic kickers as "too unreliable".

**Trade-off** (score 1–5, higher is better; weight in brackets):

| Criterion | Spring push sled (snail cam) | Flywheel (two wheels) | Pneumatic (valve + regulated tank) |
|---|---|---|---|
| Shot-to-shot repeatability (×3) | **4.** Energy is set by the spring's compression. A sled about 3× the pellet's mass turns a ±10 % pellet-mass error into only ±1.1 % of speed. | **2.** Exit speed depends on how the wheels grip a slippery, size-varying pellet; wheel speed droops about 10 % per shot. | **4.** Repeatable with regulation, but the pellet seals badly, so leakage varies. |
| Physical energy cap (×3) | **5.** The spring cannot store more than designed: a hard ceiling with no software in the loop. | **2.** Capped only by motor KV × supply voltage; a control fault means over-speed. | **3.** A relief valve can cap it, but a regulator fault is a real failure mode. |
| Cost (×2) | **5.** Worm-gear motor, spring, rods and a small bearing. | **3.** Two motors and drivers plus a pusher. | **1.** Pump, tank, regulator, valve and pressure sensor. |
| Parts count and complexity (×2) | **4.** One actuator both cocks and releases. | **3.** Spin-up control, pusher timing. | **2.** Plumbing, seals, pressure control. |
| Noise (×1) | **4.** A damped thump. | **2.** Spin-up whine on every shot. | **2.** The pump runs between shots. |
| Cycle time (×1) | **3.** 1–2 s to cock. | **5.** Near instant once spun up. | **4.** Limited by refill. |
| Pellet flight quality (×1) | **4.** No spin imparted. | **2.** Spin unless the wheels are speed-matched. | **4.** No spin. |
| Food contact and cleaning (×1) | **4.** Touches only the sled face and the channel. | **2.** Wheels rub coating dust off and turn sticky. | **3.** Pump air may carry oil or dust. |
| **Weighted total (max 70)** | **60** | **35** | **40** |

**Decision.** A spring-driven sled, cocked and released by a snail cam.

- **Mechanism.** The sled runs on polished steel rods (or small bearings) in a channel shaped like the pellet. The pellet rests against the sled face from the start: **push, never hit**. A sled that crossed a gap and struck the pellet would act like a hammer, launching it at up to twice its own speed and breaking both the cap and the repeatability. At the end of the stroke the sled stops on a urethane bumper, which absorbs about 75 % of the stored energy every shot without rebounding into the pellet. The pellet flies on alone.
- **Cocking.** A 12 V JGY-370 self-locking worm-gear motor (stall torque ≥ 5 kg·cm) turns a parabolic-spiral cam, r = k·√θ + r_min, which keeps the motor torque roughly constant.
  - A needle-roller follower; a flat landing after the drop; a detent at the ready point.
  - A microswitch marks "ready". The motor runs from a TB6612FNG driver (the DRV8833 stops at 10.8 V).
  - The drop height exceeds the stroke, so the released sled never touches the cam.
- **Idle policy.** The spring stays uncocked while disarmed or idle; printed parts creep under constant load, and stored energy is a handling hazard (REQ-SAF-015). The sequence:
  1. A consent window opens (D-009).
  2. The cam cocks (1–2 s) and parks before the drop.
  3. The shuttle loads the pellet against the sled face.
  4. FIRE turns the cam past the drop, about 40 ms later.
  5. With no shot after 30 s, the cam reverses to decock.
- **Physical cap.** Because the pellet rides the sled, it can never get more than E·m/(M_eff + m) of the stored energy, even with zero friction. Size the spring and preload range so this stays ≤ 40 mJ for the heaviest pellet configured.
- **Sizing** (refined in M2): pellet m = 1.4 g, sled about 4.5 g, spring effective mass about 0.7 g, so M_eff + m ≈ 6.6 g.
  - 6.0 m/s needs about 119 mJ of moving energy; allowing 20 % friction, about 150 mJ stored.
  - For example, a 0.36 N/mm spring compressed from 8 to 30 mm, with a peak force of about 11 N.
  - The cap check gives 150 × 1.4 / 6.6 ≈ 32 mJ (and 35 mJ for a 1.6 g pellet), both under 40 mJ.
- **Speed.** Fixed per brand by a preload screw. Aiming changes elevation only.

**Alternatives kept open.**

- **Runner-up: a speed-matched, closed-loop dual flywheel.** It would give adjustable speed and a fast cycle, at the cost of a software-dependent cap and grip variation.
- **If the M2 bench rig misses SD ≤ 1 %:** first stiffen the spring and polish the guides (the consistency data says under-powered springs scatter most), then try a sear release.
- **Upgrade path:** a servo on the preload screw gives distance-dependent speed (about 5.5 m/s close in, 7 m/s far out), which extends the eye-safe auto-fire range toward 2 m ([ballistics](research/ballistics.md) §2).

**Consequences.**

- Cocking adds 1–2 s inside the consent window, which is fine.
- The cam, follower and bumper are wear parts, printed in PETG or ASA.
- The chronograph is built from day one (M2), not added later.

## D-002 Eye safety is about where the pellet can land

**Context.** Ballistic compensation tilts the barrel 4–18° above the line of sight to the mouth ([ballistics](research/ballistics.md) §4). Between about 0.6 m and 0.9 m the bore axis therefore crosses the eye line, so "the barrel never points at the eyes" is physically incompatible with "land in the mouth".

**Decision.** REQ-SAF-002 is enforced on the predicted impact zone:

1. The zone is the 3σ ellipse from the live error model, plus the worst over-speed the chronograph lockout allows.
2. It must not overlap either eye zone: the eye landmarks of the current frame expanded by 15 mm.
3. The aim point sits 5 mm below the mouth centre.
4. When the zone grows with range, the aim point moves further down or the shot is refused.

There are no lasers on the robot.

**Consequences.** Fire control needs the per-range error model, so the calibration (M6) measures real scatter rather than assuming it. Auto-fire is limited to about 1.5 m until the measured scatter allows more.

## D-003 Camera on the turret head, tilted down

**Context.** The brief asks for closed-loop aiming that keeps the mouth centred. The camera can sit fixed on the base or ride on the moving head.

**Decision.** The camera rides on the head, rigidly fixed to the barrel. Visual servoing then measures where the *barrel* actually points, so gear backlash, servo deadband and frame flex drop out of the pointing error. Only the fixed camera-to-barrel offset (boresight) needs calibrating.

Ballistic compensation becomes a setpoint shift: the controller holds the mouth a distance-dependent number of degrees *below* the barrel axis.

**Mount the camera tilted about 10° down relative to the barrel.**

- **Why.** The offset spans 3.6° at 0.5 m to 18.4° at 2 m (6.0 m/s), and Camera Module 3 sees only ±20.5° vertically. A camera parallel to the barrel would put a 2 m mouth at the edge of the frame, with the chin outside ([mechanics research](research/mechanics-actuators.md)).
- **Effect.** With 10° of tilt, the mouth stays within about ±8.5° of the image centre from 0.5 m to 2 m.

**Alternatives.** A fixed wide camera gives a steady view for table scanning, but then every gear error lands directly in the aim. Table mode can scan by panning the head instead.

**Consequences.** The camera cable must survive ±170° of pan and the tilt motion: a 500 mm FFC in a clock-spring service loop through a hollow pan bearing (D-008). The head carries the camera's mass.

## D-004 Two processors and a hardware interlock chain

**Context.** Linux on the compute board is good at vision and bad at hard timing guarantees. The owner already has a Pico or an ESP32.

**Decision.**

- **Compute board** (Linux, Python): camera, MediaPipe, distance estimate, aiming loop, fire-control state machine, modes, UI, sound.
- **Microcontroller** (the owner's Pico or ESP32):
  - turret stepper pulses and ramps toward the angles the board sends; turret angles reported back with timestamps for latency compensation (D-008);
  - launcher motor, cam switch, shuttle servo, chamber sensor;
  - chronograph edge timestamps (RP2040 PIO capture resolves about 62.5 ns; on an ESP32 use the capture peripheral);
  - ARM-rail sensing, heartbeat watchdog, minimum shot interval;
  - the eye displays and LEDs (WS2812 support on the Pi 5 is still experimental).
- **Link:** USB serial with sequence numbers, CRC and a 20 Hz heartbeat.
- **Hardware chain below both processors:** fuse → keyed or covered ARM switch → latching E-stop → launcher rail. The E-stop also cuts the turret rail.

**Consequences.** Two codebases (Python on both if the microcontroller runs MicroPython). Safety no longer rests on any single piece of software (REQ-SAF-004, -006).

## D-005 Distance from the face, biased short

**Context.** The range estimate is the largest vertical error term: 4.0 mm at 1 m for a 2.5 % estimate. MediaPipe Iris reported a 4.3 % mean depth error (2020), and overestimating range sends the shot high, toward the eyes. Range sensors aren't an automatic fix: the TF-Luna is ±6 cm (6 % at 1 m), and the VL53L1X's cone is too wide to isolate a face ([safety research](research/safety-standards.md) §6).

**Decision.**

- **Estimate:** fuse landmark cues (inter-pupil distance, iris diameter, face geometry) in a filter.
- **Calibrate once per person:** they stand at a marked 1.0 m and the robot stores their inter-pupil distance.
- **Bias the estimate short by one standard deviation**, so the residual error lands low (chin) rather than high (eyes).
- **Range sensor:** an unmodified Class 1 sensor is an experiment only if measured error misses REQ-PERF-007.

**Consequences.** Guests in table-service mode either calibrate or run at the uncalibrated limit (≤ 6 %), which shortens their eye-safe auto-fire range.

## D-006 Feed: orientation-locking stack with a spring-return shuttle

**Context.** We need 20+ pellets with guaranteed single-piece feed on a head that tilts from −15° to +45°.

**Decision.**

- **Stack.** Pellets lie flat in a single-file channel whose clearances are smaller than each flip diagonal, so they can't rotate. A light PEZ-style spring follower on top means feed doesn't depend on gravity.
- **Shuttle.** Below the stack, a shuttle pocket of 1.05–1.2× the pellet thickness can only ever hold one. The stack exit is chamfered in the shuttle's direction of travel.
- **Drive.** An MG90S pushes the shuttle to the breech against a return spring, so with power off the breech empties (REQ-SAF-015).
- **Sensing.** An IR beam confirms the chambered pellet. On a jam: reverse, retry once, then fault (the Petcube and Furbo lesson).
- **Magazine.** A clear tube doubles as a fuel gauge on the character's head, with a lid and a silica-gel pocket, because polyol coatings may turn tacky in humidity.

**Alternatives.** A revolver drum (most deterministic, but loaded piece by piece), or a hopper with a singulating wheel (bulk loading, but a hopper outlet must be 6–10 pellets wide to avoid arching, and has the most jam modes).

**Consequences.** Pocket and channel sizes depend on the measured pellet spread, so measuring pellets is the first M2 task.

## D-007 Compute: Raspberry Pi 5 1 GB with an OV5647 camera

**Context.** The board must run FaceLandmarker with blendshapes at ≥ 15 FPS (target 25) and stay within ≤ 100 ms latency, standalone and as cheaply as possible.

- **Speed follows single-core performance.** MediaPipe runs inference on one thread on Linux, so only Cortex-A76-class boards come close. Nobody has published a Pi 5 benchmark; the estimates are 10–25 FPS per process on a Pi 5, 6–12 on a Pi 4, 2–5 on a Zero 2 W, and 3–8 on RK3566/H618 boards ([vision research](research/vision-compute.md) §3, [compute research](research/compute-camera-india.md) §2).
- **RK3588-class boards aren't an option in India:** shops don't stock them, and imports cost 2–4× list.
- **Prices:** Raspberry Pi raised them five times in 2025–26. List prices are now 1 GB $45, 2 GB $77.50, 4 GB $110.

**Decision.**

- **Board:** Raspberry Pi 5 **1 GB**: ₹5,044 at Robocraze or ₹5,449 at Robu when in stock.
  - It runs headless Raspberry Pi OS Trixie Lite (64-bit, Python 3.13) with `mediapipe` ≥ 1.1 (1.2.3 is current).
  - 1 GB is enough for one or two FaceLandmarker processes: about 720 MB is free headless, and each process uses about 90–130 MB.
  - Add the Active Cooler (₹452–569) and a 32 GB microSD card (₹770–1,549).
- **Camera:** an OV5647 5 MP CSI clone (₹267–319).
  - About 54° × 41° and fixed focus, so faces at 2 m are bigger than with the 66° official cameras.
  - Its 1296 × 972 mode leaves room for a 2× crop.
  - The 500 mm Pi 5 22→15-pin cable (₹409) gives the turret its service loop.
- **Power:** from the robot's 12 V → 5 V 5 A buck.
  - Without USB-PD the USB ports are capped at 600 mA, which is fine with a CSI camera and the microcontroller.
  - If `vcgencmd get_throttled` ever reports under-voltage, switch to the official 27 W supply (₹1,063–1,345).
- **Cost:** about **₹6,900** for board, camera, cooler, card and cable. The one-seller kit with the official PSU is ₹8,939.
- **When to buy:** last. On 2026-11-25 the Pi 5 1 GB and 2 GB were out of stock at every Indian seller checked (UK shops restocked on 19 Nov). The Pi isn't needed until M4. Until then, develop the vision on the Windows PC (`mediapipe` has a win_amd64 wheel for Python 3.13) and set stock alerts.
- **Step-up**, only if the M4 benchmarks miss the target:
  - Pi 5 2 GB, for three worker processes;
  - Camera Module 3 standard (₹3,068–3,299), for autofocus, HDR, better low light and 1.8× the pixels.

**Alternatives.**

| Option | Why not |
|---|---|
| Pi 5 4 GB | In stock today at ₹13,455, but it breaks the budget |
| Pi 4 | Costs more than a Pi 5 1 GB and is about half as fast per core |
| RK3588-class boards | Not stocked in India |
| An old Android phone running MediaPipe in Chrome, over BLE to an ESP32 | A good zero-cost prototype for the trigger logic, but not the final standalone brain |
| USB webcam | Its cable flexes well, but it adds 2–4 frames of latency |

**Consequences.**

- Benchmark FPS and latency in the first week of M4: VIDEO mode, crop against full frame, one process against two.
- The camera ribbon needs a large-radius loop and a cycle test. Consider mounting the Pi on the pan stage so only the tilt joint flexes the ribbon, while round cables (12 V, USB) cross the pan axis.

## D-008 Turret actuators: NEMA17 steppers through 3:1 belts

**Context.** Pointing must reach 0.12° 1σ ([mechanics research](research/mechanics-actuators.md), [India prices](research/bom-pricing-india.md)), and the candidates compare like this:

| Option | Performance | Cost in India |
|---|---|---|
| Feetech STS3215 bus servos | A bench test measured 0.87° of free play, about 0.88° of deadband and ±0.17° repeatability, so they need a 3:1 belt stage to get near 0.3° | 12 V C018 is in stock at Evelta for ₹2,419 each; the 7.4 V variants are sold out everywhere. A complete set is about ₹5,850 |
| Hobby PWM servos | 0.4–0.9° deadband, and they can't reach ±180° | — |
| NEMA17 steppers + TMC2209 + 3:1 GT2 | 0.0375° per 1/16 microstep, with almost no play through a tensioned belt | About ₹2,900 for both axes, including homing switches |

**Decision.**

- **Motors.** Two NEMA17 steppers (KS42STH34, 34 mm, or the 40 mm 42HS40 for less) on TMC2209 drivers in StealthChop, which is quiet. Each axis is driven through a **3:1 GT2 belt** (20T to 60T; the 60T can be printed).
- **Placement.** The pan motor sits in the base and the tilt motor rides on the pan stage, so the tilting head carries no motor.
- **Control.** The microcontroller generates the step pulses (PIO on a Pico) and ramps toward target angles sent by the compute board (D-004).
- **Homing and recovery.** On start-up the turret homes against switches or Hall sensors. If vision reports a growing error, it re-homes. The camera on the head measures real pointing, so a missed step shows up as tracking error and gets corrected.
- **Pan bearing.** A pair of hollow 6806ZZ (30 × 42 × 7 mm), or one plus a thrust face. The camera FFC and wires run through the bore. Hard stops sit just past ±170°.
- **Firing.** Fire control fires only after the turret camera confirms the residual error (REQ-SAF-001 f).

**Alternative.** The STS3215 12 V set (absolute encoders, simple daisy-chain wiring), at twice the cost and with more play.

**Consequences.**

- The steppers lose holding torque when the E-stop cuts their rail, so the tilt needs a soft end stop.
- The steppers draw standstill current: use the TMC2209's hold-current reduction.
- The microcontroller gains about 7 pins (step, dir and enable × 2, plus UART).

## D-009 Consent: explicit opt-in per shot

**Context.** The brief's trigger, a mouth open and steady for 300 ms, is necessary but not sufficient. Yawns, laughter and speech pass it, and in table-service mode people other than the operator are present ([safety research](research/safety-standards.md) §5).

**Decision.**

- **Opt-in.** Each shot needs an explicit gesture: eyebrows raised for about 1 s while looking at the robot with the mouth closed (from MediaPipe blendshapes, no extra hardware), or the operator presses the robot's nose button.
- **Window.** The robot chirps, its eyes show "open wide", and a 5 s window opens for **one** shot.
- **Gates.** The brief's 300 ms open-mouth rule and every other gate still apply inside the window.
- **Table mode.** Each person opts in for themselves.

**Alternatives.** A voice keyword (needs a microphone and keyword spotting), or a hand gesture (needs a second model). Kept as upgrades.

**Consequences.** The UX is one deliberate step longer, but an accidental fire now needs a deliberate gesture *and* an open mouth *and* every other gate passing.

## D-010 Design pellet: hard-coated, non-liquid, 1.3–1.5 g

**Context.** Pellet gums differ widely ([launcher research](research/launcher-prior-art.md) §1):

| Brand | Mass | Note |
|---|---|---|
| Extra (AU/UK), PUR | 1.4 g | |
| Lotte Xylitol | 1.5 g | |
| Mentos Pure Fresh | 2.0 g | liquid centre |
| Ice Breakers Ice Cubes | 2.3 g | over the cap at 6 m/s |
| Center Fresh (India) | — | reportedly liquid-filled |
| Happydent White (India) | about 1.1 g | unverified |

No brand publishes dimensions.

**Decision.** Design around one hard-coated, non-liquid pellet of 1.3–1.5 g. The owner buys two or three candidates sold locally and measures 30 of each (mass to 0.01 g, L × W × T), and the brand with the smallest spread wins. Liquid-filled pellets and anything ≥ 2 g are out.

**Consequences.** The magazine, shuttle and channel dimensions, the spring preload and the cap verification are all tied to that brand. Changing brand means re-measuring and re-running the cap check.

## D-011 Phase 1: joystick aiming; face tracking moves to phase 2

**Context.** On 2026-11-25 the owner decided that the first half of the project uses a joystick, not face tracking. That removes the camera, the Raspberry Pi and everything that depended on live face landmarks from phase 1: auto-aim (D-003), the range estimate (D-005), the eye-zone gate (D-002), the gesture opt-in (D-009) and the compute board (D-007). The mechanics are untouched: launcher (D-001), feed (D-006), turret (D-008) and pellet (D-010) carry straight over, and phase 2 adds vision back on top of them.

**Decision.**

- **Controller.** A wired handheld box on a 2 m Cat-6 patch cable (8 cores, soldered: no crimper needed), plugged into the microcontroller:
  - a 2-axis analog thumb joystick (KY-023 type) for **rate control**: deflection sets turret speed, with a deadband and an expo curve, so small deflections give fine aim (about 2°/s) and full deflection about 60°/s pan, 30°/s tilt;
  - **ENABLE**, a hold-to-fire deadman button; **FIRE**; and **RANGE −/+**.
  - Wired, not Bluetooth: it works on either the Pico or the ESP32, has no pairing or link-loss states, and unplugging it pulls ENABLE low, which is SAFE. A Bluetooth gamepad (Bluepad32 on an ESP32) stays an option once fire control is proven.
- **Aiming.** The operator sits behind the robot and aims by eye over a printed sight on the turret head (rear notch, front post, adjustable), zeroed at 1.0 m during calibration. There's no laser (REQ-SAF-008).
- **Range.** The operator sets the slant range with RANGE −/+ in 0.1 m steps from 0.5 to 2.0 m, shown on a 0.96" OLED on the base. The person sits or stands at a marked distance (tape marks every 0.25 m). At 1 m the offset changes about 1° per 0.1 m, so the marks matter more than the dial.
- **Holdover on fire.** The microcontroller holds the [ballistic seed table](research/ballistics.md) (range × line-of-sight elevation). The operator holds the sight on the lower lip. On FIRE the turret tilts up by the table offset for the set range and its current elevation, settles, chirps, releases, then returns. The table is biased short, so errors land low.
- **Fire control lives in the microcontroller** in phase 1: one state machine, one firing path (REQ-SAF-017). It's written as plain Python with the hardware behind interfaces, so the same module runs under pytest on the PC with fakes and under MicroPython on the board.
- **Eyes.** Nothing can check eye position without vision, so in phase 1 **everyone in front of the armed robot wears impact-rated glasses, with no exception** (REQ-SAF-018). The physical energy cap, the chronograph lockout, the aim-low rule and the hardware ARM chain are unchanged.
- **Consent and pacing.** The target says they're ready; the operator holds ENABLE and presses FIRE. The microcontroller enforces ≥ 10 s between shots, at most 5 shots per arming (cycle the ARM switch for more), a 300 ms warning chirp, and a still turret before release.
- **Feedback.** A passive buzzer on the microcontroller gives the chirp and fault tones (the I2S speaker needs the Pi, so it moves to phase 2). The OLED shows SAFE/ARMED, range, shots left and the last chronograph speed. Shot lines also go out over USB, so a laptop can log them.

**Phase 2** brings back the Pi 5, the OV5647 on the head, MediaPipe auto-aim, the eye-zone gate, gesture consent and the auto modes, as D-002…D-009 describe. The joystick stays as the manual trick-shot controller (REQ-MODE-003), and in phase 2 its FIRE goes through the full vision gates whenever a face is in the firing cone.

**Alternatives.**

| Option | Why not, for phase 1 |
|---|---|
| Keep the camera as a video view only | Needs the Pi anyway, which is out of stock in India; adds cost before it's needed |
| USB gamepad on a laptop, serial to the microcontroller | The firing path would depend on a laptop and a link; the wired box keeps it inside the microcontroller |
| Range presets only (0.5 / 1.0 / 1.5 / 2.0 m) | Too coarse: a 0.25 m error is about 2.5° of offset at 1 m |
| A Class 1 ToF range sensor | Its cone is too wide to isolate a face (D-005); kept as a phase-2 experiment |

**Consequences.**

- **Cost.** Phase 1 buys no compute board, camera or I2S audio: about ₹7,350 less up front. The controller, OLED and buzzer add about ₹450 (estimate). See [bom.md](bom.md).
- **Accuracy.** It now depends on the operator, the sight and how well the person stays on their mark. REQ-PERF-002 is verified in phase 1 on a fixed target at a known range. The error budget's range term comes from the marks (about ±3 cm) instead of the face estimate.
- **Safety case.** It moves from automatic gating to interlocks plus procedure: glasses, marks, pacing, deadman. The phase-1 gate list is REQ-SAF-017; the hazard table in [safety.md](safety.md) covers the change.
- **Pins.** Phase 1 puts more on the microcontroller (joystick ADC × 2, four buttons, OLED I2C, buzzer). The Pico's 26 GPIOs are nearly all used once the GC9A01 eyes are added; the wiring deliverable (4) settles the pin map, and WS2812 eyes are the fallback.
- **Roadmap.** Vision moves after the robot works end to end with the joystick ([roadmap.md](roadmap.md)).
