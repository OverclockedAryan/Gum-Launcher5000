# DESUU: Safety case

What can hurt someone, what the design does about it, and how we prove it. The requirements are REQ-SAF-* in [requirements.md](requirements.md). Sources and numbers are in [research/safety-standards.md](research/safety-standards.md) and [research/ballistics.md](research/ballistics.md).

## Position

- DESUU is an **adults-only hobby device**. Toy standards don't cover it and can't be its safety basis. The pellet passes their energy limits, but it fails their small-parts rule for projectiles, and they treat aiming at the face as misuse. We use them only as energy benchmarks.
- We follow ISO 12100's order of risk reduction:
  1. inherently safe design (physical energy cap, aim low, eye-zone exclusion);
  2. safeguards (ARM switch and E-stop in the power path, a microcontroller watchdog, a chronograph lockout);
  3. information for use (label, instructions).
- **No energy level makes an eye hit acceptable.** At the 40 mJ cap, a pellet that lands edge-first delivers about 1,000 J/m². That is two-thirds of the 1,503 J/m² at which foam impacts gave a 50 % risk of corneal abrasion, and a rigid pellet may abrade at lower energy than foam (unverified). The cap limits how bad an injury can be; the aiming geometry must prevent the hit in the first place.

## Phase 1 (joystick): what changes

Phase 1 has no camera ([D-011](decisions.md#d-011-phase-1-joystick-aiming-face-tracking-moves-to-phase-2)), so every control that read the face is gone: the eye-zone gate, the open-mouth and posture gates, the single-face check and the gesture opt-in. A person now decides where the barrel points and when it fires. The design answers that with protection and interlocks instead of perception:

| Removed with vision | Phase 1 replacement |
|---|---|
| Impact zone kept off the eyes (REQ-SAF-002) | **Impact-rated glasses on everyone in front of the armed robot, every session, no exception** (REQ-SAF-018). Aim at the lower lip; holdover table biased short |
| Mouth open and steady 300 ms, facing the robot, posture | The target says they're ready, sitting upright on their mark; the operator fires. The 300 ms chirp warns them |
| Range estimate | Tape marks every 0.25 m and the range dial (0.1 m steps) on the OLED |
| Exactly one face in the cone | The operator's job: one person in the firing arc, bystanders behind the robot |
| Consent gesture opens a 5 s window | ENABLE held ≥ 1 s (deadman) plus a fresh FIRE press; releasing ENABLE aborts |
| Per-person pacing | ≥ 10 s between any two shots and 5 shots per arming, enforced by the microcontroller |

Unchanged in phase 1: the physical energy cap, the chronograph lockout, the ARM switch and E-stop in the power path, the watchdog, re-arm after reset, decock when idle, the empty-breech-without-power shuttle, the food-path rules and adults only.

## Energy limits

| Pellet | Operating ceiling 30 mJ | Hard cap 40 mJ | Energy density at the cap, end face (70 mm²) | Edge-first (≈ 40 mm²) |
|---|---|---|---|---|
| 1.4 g (Extra-class) | 6.5 m/s | 7.6 m/s | 570 J/m² | 1,000 J/m² |
| 1.6 g | 6.1 m/s | 7.1 m/s | 570 J/m² | 1,000 J/m² |
| 2.0 g (Mentos-class) | 5.5 m/s | 6.3 m/s | 570 J/m² | 1,000 J/m² |

- The cap is set by the **heaviest pellet the robot is configured for**.
- The spring at maximum preload must physically be unable to exceed it (D-001: the pellet gets at most E·m/(M+m) of the stored energy).
- Changing gum brand means re-checking the cap with the chronograph.

## Hazards and controls

| # | Hazard | Main causes | Controls | Verify |
|---|---|---|---|---|
| H1 | Pellet hits an eye | Aim error; an over-speed shot climbs; the head moves; wrong target; wrong range set (phase 1) | Phase 2: impact-zone exclusion from live eye landmarks (D-002); live 3σ check; auto-fire range limit. Phase 1: mandatory impact-rated glasses (REQ-SAF-018); range marks; holdover biased short. Both: aim 5 mm below the mouth centre; chronograph lockout; physical energy cap | T-SAF-2, T-SAF-3 |
| H2 | Choking or aspiration | Pellet reaches the back of the throat; sharp inhale; reclining | Aim at the front of the tongue; flat or descending entry (muzzle height, [ballistics](research/ballistics.md) §5); ≤ 30 mJ; posture gate (head tipped back ≤ 15°; in phase 1 the operator checks the person sits upright); consent per shot; ≥ 10 s between shots; session cap (5 per arming in phase 1); adults only; instructions | T-SAF-1, T-INS |
| H3 | Unintended fire | Software bug; stuck GPIO; boot glitch; replayed command; stuck or shorted FIRE button; controller unplugged mid-sequence | ARM switch and E-stop in series with actuator power; gate pull-downs; no boot/strapping pins on drives; re-arm after reset; independent watchdog; optional charge-pump enable. Phase 1: ENABLE deadman (open circuit = released), FIRE acts on a fresh press only, disconnect detection. Phase 2: heartbeat; single-use FIRE tokens | T-SAF-4, T-SAF-5, T-CTL-1 |
| H4 | Shooting a bystander or the wrong person | Several faces; table mode; operator error (phase 1) | Phase 2: exactly one face in the firing cone; consent per person; abort on any break in tracking. Phase 1: one person in the firing arc, bystanders behind the robot, glasses on anyone in front, chirp before release | T-SAF-1, T-MODE-2 |
| H5 | Stored spring energy released while someone handles the robot | Spring left cocked | Never cock while disarmed; decock (reverse the cam) after 30 s idle; self-locking worm; breech empties without power; manual decock procedure | T-SAF-6 |
| H6 | Improvised projectiles | Someone loads a bead or pebble | Shape-keyed feed; chamber sensor; the energy cap still holds | T-INS |
| H7 | Food contamination | Layer-line bacteria; nozzle metals; dirty pellets | Stainless or PTFE liners, or natural PETG printed through a stainless nozzle; removable food path; hand-wash only; discard fired and dropped pellets; lidded magazine | T-INS |
| H8 | Pinching in the turret | Servo torque; belts | Torque and speed limits; belt guards; E-stop | T-INS |
| H9 | Electrical or thermal | Short circuit; servo stall | Fuse; current limits; servo temperature telemetry; no lithium cells in v1 | T-INS |
| H10 | Pets poisoned | Missed sugar-free pellets contain xylitol, dangerous to dogs | Collect missed pellets; warning in the manual | T-INS |
| H11 | Laser or IR exposure | A range sensor | Unmodified Class 1 modules only; no visible lasers on the robot | T-INS |
| H12 | Operator misuse (phase 1) | Aiming at the eyes or at someone without glasses; firing at someone who isn't ready; rapid fire | Glasses rule in the manual and on the label; deadman plus fresh FIRE press; 300 ms chirp; ≥ 10 s pacing and 5 shots per arming in firmware; the key stays with an adult | T-INS, T-CTL-1 |

## Firing gates

**Phase 1.** The microcontroller's state machine is the only path to a release, and it checks every gate in REQ-SAF-017 (armed, homed, deadman held, fresh FIRE press, turret still, range set, chambered and parked, pacing, chronograph healthy, controller connected) before the holdover tilt and again before release. The states are in [architecture.md](architecture.md#phase-1-fire-control-microcontroller).

**Phase 2.** Fire control may send FIRE only when **every** gate in REQ-SAF-001 passes in the same frame. The microcontroller independently re-checks the armed rail, heartbeat, token freshness, chamber and cam state, and its own 5 s minimum interval (REQ-SAF-006). The gates are listed in [architecture.md](architecture.md#software).

## Consent (D-009)

**Phase 1:** the target says they're ready, sits upright on their mark and puts their glasses on; only then does the operator hold ENABLE and press FIRE. The chirp gives them 300 ms of warning, and releasing ENABLE at any point aborts. Nobody gets served by default.

**Phase 2:** an open mouth alone is not consent: yawns, laughter and speech can hold a mouth open for 300 ms. Each shot needs an explicit opt-in:

1. The person looks at the robot and raises their eyebrows for about 1 s with the mouth closed, or the operator presses the robot's nose button.
2. The robot chirps and its eyes show "open wide". That opens a **5 s window for one shot**.
3. Within the window, the usual gates apply: mouth open and steady for 300 ms, one face, facing the robot, eyes clear, and so on. Losing the track, or the window running out, cancels it.

In table-service mode every person opts in for themselves. Nobody gets served by default.

## Development and test safety

- Anyone in front of an armed robot wears **impact-rated safety glasses** (ANSI Z87.1 or EN 166): in phase 2 until the M10 acceptance tests pass, in phase 1 always (REQ-SAF-018).
- Armed testing starts on a **printed face target** with a 30 mm hole and a catch bag (in phase 2 MediaPipe tracks the photo too). No human target until every T-SAF and T-CTL test passes.
- **Pre-use check** each session: 5 chronographed shots into the target box. The robot refuses to fire at people (phase 2: auto-serve) if the mean is off by more than 3 % or the SD exceeds 1.5 %; in phase 1 the OLED shows the check and the firmware locks out.
- **Manual decock:** phase 1: release ENABLE and wait for "decocked" on the OLED (or let the 30 s idle timer do it), then disarm. Phase 2: send `SAFE` + decock from the UI, wait for "decocked", then disarm. Never put fingers in the barrel or breech while the cam is cocked.

## Information for use

Label on the robot: **"Adults only. Choking hazard. Never look into the mouth (barrel)."**

The manual covers:

- Phase 1 (joystick): **everyone in front of the robot wears impact-rated glasses while it's armed.** Sit upright on a range mark and say when you're ready. The operator aims at your lower lip and sets the range to your mark.
- Sit upright. Don't use it lying down or while eating or drinking.
- Open your mouth; don't inhale sharply. Spit the pellet out if it reaches the back of your throat.
- Collect missed pellets: sugar-free gum can contain xylitol, which is toxic to dogs.
- Disarm and remove the key when the robot isn't in use.
- Clean the food path by hand in warm soapy water. No dishwasher.

## Residual risks we accept, and why

- **Age:** vision can't verify age. The key-holder decides who uses the robot, so the key stays with an adult.
- **Correct gating:** the eye-safety argument depends on the gating logic being correct. That's why the gates get 100 % branch coverage (REQ-SW-002), recorded-face tests (REQ-SAF-002), and a hardware backstop that limits how bad a failure can be: the energy cap plus the ARM chain.
- **Consent misread:** a consent gesture can be made by accident. It only opens a short window; the other nine gates still have to pass.
- **Phase 1 relies on people.** Without vision, the operator's aim and the glasses are what keep the eyes safe. We accept that for phase 1 because the glasses make an eye hit harmless, the energy cap bounds every other hit, and the firmware still enforces the deadman, pacing and the shot limit. Phase 2 restores the automatic eye gate.
