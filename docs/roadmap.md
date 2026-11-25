# DESUU: Roadmap

The build order retires the biggest risks first instead of following the brief's deliverable numbering. Each milestone names the deliverables it produces and the evidence that closes it.

## Risks, ranked

| # | Risk | Why it matters | Retired in |
|---|---|---|---|
| 1 | Launcher exit-speed scatter above 1 % with real gum | Speed scatter feeds both accuracy and eye safety ([ballistics](research/ballistics.md) §3–4) | M2 bench rig |
| 2 | Range estimate worse than 2.5 % from one camera | Largest term in the error budget | M3 on the dev PC |
| 3 | Too few frames per second on the cheapest board | Tracking lag and slow fire decisions | M3 (PC) → M4 (board) |
| 4 | Feed jams or double feeds with the chosen brand | Pellet size scatter decides the pocket geometry | M2 bench rig |
| 5 | Turret pointing or latency outside 0.12° / 100 ms | Second-largest accuracy term | M4 |
| 6 | A safety gate with a logic bug | Fires when it shouldn't | Unit tests from M3, live tests in M6 |

## Milestones

| Milestone | Scope | Brief deliverables | Exit criterion |
|---|---|---|---|
| **M0 Context** | Brief, requirements, research, ballistics model, decisions | — | Done 2026-11-25 |
| **M1 Design freeze v1** | Finalise architecture and launcher trade-off; approve BOM v1; order the long-lead parts | 1, 2 | Owner approves [decisions.md](decisions.md) and the BOM |
| **M2 Launcher and feed bench rig** | Snail-cam spring push sled, shuttle feed and IR chronograph on a fixed stand, run by the owner's Pico/ESP32. Measure 30 pellets; fire 100 shots; run 200 feed cycles | 3 (part) | Speed SD ≤ 1 %, zero double feeds (REQ-PERF-004, REQ-FEED-002) |
| **M3 Vision on the PC** | Webcam + MediaPipe FaceLandmarker (`mediapipe` ≥ 1.1 on Python 3.13), mouth-open detector, distance estimate, eye zones, fire-control state machine with unit tests, simulated turret (`--sim`) | 5 (part) | ≥ 25 FPS on the PC; distance error measured against a tape (REQ-PERF-007) |
| **M4 Turret** | Pan-tilt mechanics and actuators, visual servoing on the robot's board, latency measurement | 3, 5 | Pointing ≤ 0.12° 1σ, latency ≤ 100 ms (REQ-PERF-005, -008) |
| **M5 Integration** | Wiring harness, power, microcontroller firmware (interlocks, launcher, feed, chronograph) | 4 | Every T-SAF test passes, first disarmed, then armed with dummy pellets |
| **M6 Calibration and accuracy** | Boresight, ballistic table from real shots, accuracy campaign at 0.5 / 1.0 / 1.5 / 2.0 m | 6 | REQ-PERF-002 met on the printed face target |
| **M7 Character and modes** | Eyes and sounds, table-service mode, manual trick-shot mode | 7 | REQ-MODE-001…003 |

Test targets: a printed photo of an open-mouthed face on card, with a 30 mm hole at the aim point and a catch bag behind it. MediaPipe tracks printed faces, so most accuracy and safety testing needs no person in front of the robot.

## First actions for the owner

1. Buy a 150 mm digital caliper and a 0.01 g pocket scale (both are cheap and every later step depends on them).
2. Choose one gum brand and buy a few packs. Measure 30 pellets (length, width, thickness, mass), then re-run `python tools/ballistics_sim.py --mass-g <mean>` with the real mass.
3. Confirm which microcontroller you own (Pico, Pico W, Pico 2 or which ESP32).
4. Confirm or correct interpretations A1–A5 in [brief.md](brief.md).
5. Approve [BOM v1](bom.md) and place its order 1, the M2 bench-rig parts, first (launcher, feed, chronograph). The Raspberry Pi 5 1 GB was out of stock at every Indian seller on 2026-11-25. Set stock alerts at Robu, Robocraze and Silverline and buy it last: it isn't needed until M4 (D-007).
