# DESUU: Roadmap

The build order retires the biggest risks first instead of following the brief's deliverable numbering. Each milestone names the deliverables it produces and the evidence that closes it.

The project runs in two phases ([D-011](decisions.md#d-011-phase-1-joystick-aiming-face-tracking-moves-to-phase-2)): **phase 1** (M0–M7) builds the whole robot aimed with a wired joystick; **phase 2** (M8–M10) adds the camera, the Pi and face-tracking auto-aim on top of the same mechanics.

## Risks, ranked

| # | Risk | Why it matters | Retired in |
|---|---|---|---|
| 1 | Launcher exit-speed scatter above 1 % with real gum | Speed scatter feeds both accuracy and eye safety ([ballistics](research/ballistics.md) §3–4) | M2 bench rig |
| 2 | Feed jams or double feeds with the chosen brand | Pellet size scatter decides the pocket geometry | M2 bench rig |
| 3 | A fire-control bug: fires when it shouldn't, or the deadman doesn't abort | The firmware is the only firing path in phase 1 | M3 (unit tests on the PC), M5 (live, disarmed then armed) |
| 4 | Turret pointing or holdover return outside 0.12° / 0.05° | Second-largest accuracy term; the holdover must come back to the sight | M4 |
| 5 | Manual aim and range marks too coarse for the 30 mm circle | Phase 1 accuracy depends on the operator and the marks | M6 |
| 6 | Range estimate worse than 2.5 % from one camera | Largest term in the error budget once vision returns | M8 (PC) |
| 7 | Too few frames per second on the Pi 5 1 GB | Tracking lag and slow fire decisions | M8 (PC) → M9 (Pi) |

## Phase 1: joystick

| Milestone | Scope | Brief deliverables | Exit criterion |
|---|---|---|---|
| **M0 Context** | Brief, requirements, research, ballistics model, decisions | — | Done 2026-11-25 |
| **M1 Design freeze v1** | Finalise architecture and launcher trade-off; approve BOM v1.1; order the phase 1 parts | 1, 2 | Owner approves [decisions.md](decisions.md) and the BOM |
| **M2 Launcher and feed bench rig** | Snail-cam spring push sled, shuttle feed and IR chronograph on a fixed stand ([bench-rig.md](mechanical/bench-rig.md), CAD generated). Measure 30 pellets; fire 100 shots; run 200 feed cycles | 3 (part) | Speed SD ≤ 1 %, zero double feeds (REQ-PERF-004, REQ-FEED-002) |
| **M3 Controller and fire-control firmware** | The handheld controller (group L), the OLED and buzzer, and `firmware/fire_control.py` (REQ-SAF-017) with 100 % branch coverage under pytest on the PC. Then run the M2 rig from the controller: ENABLE, FIRE, decock on release, pacing | 5 (part) | All T-CTL-1 and T-SAF-1/5 tests pass, disarmed then armed on the rig |
| **M4 Turret** | Pan-tilt mechanics and steppers, the sight, joystick rate control, homing, holdover tilt and return | 3, 5 | Stick latency ≤ 50 ms; return to the sight angle within 0.05°; pointing ≤ 0.12° 1σ (REQ-CTL-002/003, REQ-PERF-005) |
| **M5 Integration** | Wiring harness, power, the full firmware (interlocks, launcher, feed, chronograph, turret) | 4 | Every T-SAF and T-CTL test passes, first disarmed, then armed with dummy pellets |
| **M6 Calibration and accuracy** | Zero the sight at 1.0 m, build the holdover table from real shots at the tape marks, accuracy campaign at 0.5 / 1.0 / 1.5 / 2.0 m | 6 | REQ-PERF-002 met on a fixed printed face target |
| **M7 Character and modes** | Eyes and chirps, manual table service, trick shots | 7 | REQ-MODE-003, owner sign-off on the character (REQ-BLD-003) |

Phase 1 ends with a complete, joystick-aimed robot. Everyone in front of it wears impact-rated glasses, always (REQ-SAF-018).

## Phase 2: face tracking

| Milestone | Scope | Brief deliverables | Exit criterion |
|---|---|---|---|
| **M8 Vision on the PC** | Webcam + MediaPipe FaceLandmarker (`mediapipe` ≥ 1.1 on Python 3.13), mouth-open detector, distance estimate, eye zones, the phase 2 fire-control state machine with unit tests, simulated turret (`--sim`) | 5 (part) | ≥ 25 FPS on the PC; distance error measured against a tape (REQ-PERF-007) |
| **M9 Auto-aim on the robot** | Pi 5 1 GB + OV5647 on the head (D-003, D-007), visual servoing, latency measurement, the vision gates and gesture consent; the microcontroller's link checks (REQ-SAF-006) | 3, 4, 5 | ≥ 15 FPS, camera-to-command ≤ 100 ms (REQ-PERF-008); every REQ-SAF-001 gate tested live on a printed face target |
| **M10 Auto modes and re-calibration** | Auto-serve, table service with consent, boresight, per-range error model, eye-safe auto-fire limit | 6, 7 | REQ-MODE-001/002; REQ-SAF-002 and -011 verified |

Test targets: a printed photo of an open-mouthed face on card, with a 30 mm hole at the aim point and a catch bag behind it. In phase 1 you aim at it with the sight; in phase 2 MediaPipe tracks it, so most accuracy and safety testing needs no person in front of the robot.

## First actions for the owner

1. Buy a 150 mm digital caliper, a 0.01 g pocket scale and impact-rated glasses (every later step depends on them).
2. Choose one gum brand and buy a few packs. Measure 30 pellets (length, width, thickness, mass), then re-run `tools/launcher_design.py` and `cad/bench_rig.py` with the real numbers.
3. Confirm which microcontroller you own (Pico, Pico W, Pico 2 or which ESP32): phase 1 puts everything on it.
4. Confirm or correct interpretations A1–A5 in [brief.md](brief.md).
5. Approve [BOM v1.1](bom.md) and place its order 1: the M2 bench-rig parts plus the controller (group L). The Raspberry Pi 5 and camera aren't needed until phase 2 (D-011), so there's no need to chase stock alerts yet.
