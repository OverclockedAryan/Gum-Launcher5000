# DESUU: Safety case

What can hurt someone, what the design does about it, and how we prove it. The requirements are REQ-SAF-* in [requirements.md](requirements.md). Sources and numbers are in [research/safety-standards.md](research/safety-standards.md) and [research/ballistics.md](research/ballistics.md).

## Position

- DESUU is an **adults-only hobby device**. Toy standards don't cover it and can't be its safety basis. The pellet passes their energy limits, but it fails their small-parts rule for projectiles, and they treat aiming at the face as misuse. We use them only as energy benchmarks.
- We follow ISO 12100's order of risk reduction:
  1. inherently safe design (physical energy cap, aim low, eye-zone exclusion);
  2. safeguards (ARM switch and E-stop in the power path, a microcontroller watchdog, a chronograph lockout);
  3. information for use (label, instructions).
- **No energy level makes an eye hit acceptable.** At the 40 mJ cap, a pellet that lands edge-first delivers about 1,000 J/m². That is two-thirds of the 1,503 J/m² at which foam impacts gave a 50 % risk of corneal abrasion, and a rigid pellet may abrade at lower energy than foam (unverified). The cap limits how bad an injury can be; the aiming geometry must prevent the hit in the first place.

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
| H1 | Pellet hits an eye | Aim error; an over-speed shot climbs; the head moves; wrong target | Impact-zone exclusion from live eye landmarks (D-002); aim 5 mm below the mouth centre; live 3σ check; auto-fire range limit; chronograph lockout; physical energy cap | T-SAF-2, T-SAF-3 |
| H2 | Choking or aspiration | Pellet reaches the back of the throat; sharp inhale; reclining | Aim at the front of the tongue; flat or descending entry (muzzle height, [ballistics](research/ballistics.md) §5); ≤ 30 mJ; posture gate (head tipped back ≤ 15°); consent per shot; ≥ 10 s per person; session cap; adults only; instructions | T-SAF-1, T-INS |
| H3 | Unintended fire | Software bug; stuck GPIO; boot glitch; replayed command | ARM switch and E-stop in series with actuator power; gate pull-downs; no boot/strapping pins on drives; re-arm after reset; heartbeat; single-use FIRE tokens; independent watchdog; optional charge-pump enable | T-SAF-4, T-SAF-5 |
| H4 | Shooting a bystander or the wrong person | Several faces; table mode | Exactly one face in the firing cone; consent per person; abort on any break in tracking | T-SAF-1, T-MODE-2 |
| H5 | Stored spring energy released while someone handles the robot | Spring left cocked | Never cock while disarmed; decock (reverse the cam) after 30 s idle; self-locking worm; breech empties without power; manual decock procedure | T-SAF-6 |
| H6 | Improvised projectiles | Someone loads a bead or pebble | Shape-keyed feed; chamber sensor; the energy cap still holds | T-INS |
| H7 | Food contamination | Layer-line bacteria; nozzle metals; dirty pellets | Stainless or PTFE liners, or natural PETG printed through a stainless nozzle; removable food path; hand-wash only; discard fired and dropped pellets; lidded magazine | T-INS |
| H8 | Pinching in the turret | Servo torque; belts | Torque and speed limits; belt guards; E-stop | T-INS |
| H9 | Electrical or thermal | Short circuit; servo stall | Fuse; current limits; servo temperature telemetry; no lithium cells in v1 | T-INS |
| H10 | Pets poisoned | Missed sugar-free pellets contain xylitol, dangerous to dogs | Collect missed pellets; warning in the manual | T-INS |
| H11 | Laser or IR exposure | A range sensor | Unmodified Class 1 modules only; no visible lasers on the robot | T-INS |

## Firing gates

Fire control may send FIRE only when **every** gate in REQ-SAF-001 passes in the same frame. The microcontroller independently re-checks the armed rail, heartbeat, token freshness, chamber and cam state, and its own 5 s minimum interval (REQ-SAF-006). The gates are listed in [architecture.md](architecture.md#software).

## Consent (D-009)

An open mouth alone is not consent: yawns, laughter and speech can hold a mouth open for 300 ms. Each shot needs an explicit opt-in:

1. The person looks at the robot and raises their eyebrows for about 1 s with the mouth closed, or the operator presses the robot's nose button.
2. The robot chirps and its eyes show "open wide". That opens a **5 s window for one shot**.
3. Within the window, the usual gates apply: mouth open and steady for 300 ms, one face, facing the robot, eyes clear, and so on. Losing the track, or the window running out, cancels it.

In table-service mode every person opts in for themselves. Nobody gets served by default.

## Development and test safety

- Anyone in front of an armed robot wears **impact-rated safety glasses** (ANSI Z87.1 or EN 166) until the M6 acceptance tests pass.
- Armed testing starts on a **printed face target** (MediaPipe tracks photos). No human target until every T-SAF test passes.
- **Pre-use check** each session: 5 chronographed shots into the target box. The robot refuses to auto-serve if the mean is off by more than 3 % or the SD exceeds 1.5 %.
- **Manual decock:** arm, send `SAFE` + decock from the UI, wait for "decocked", then disarm. Never put fingers in the barrel or breech while the cam is cocked.

## Information for use

Label on the robot: **"Adults only. Choking hazard. Never look into the mouth (barrel)."**

The manual covers:

- Sit upright. Don't use it lying down or while eating or drinking.
- Open your mouth; don't inhale sharply. Spit the pellet out if it reaches the back of your throat.
- Collect missed pellets: sugar-free gum can contain xylitol, which is toxic to dogs.
- Disarm and remove the key when the robot isn't in use.
- Clean the food path by hand in warm soapy water. No dishwasher.

## Residual risks we accept, and why

- **Age:** vision can't verify age. The key-holder decides who uses the robot, so the key stays with an adult.
- **Correct gating:** the eye-safety argument depends on the gating logic being correct. That's why the gates get 100 % branch coverage (REQ-SW-002), recorded-face tests (REQ-SAF-002), and a hardware backstop that limits how bad a failure can be: the energy cap plus the ARM chain.
- **Consent misread:** a consent gesture can be made by accident. It only opens a short window; the other nine gates still have to pass.
