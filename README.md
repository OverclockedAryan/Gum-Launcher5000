# Gum Laumcher

A friendly desk robot that tosses a piece of pellet gum into your mouth. Phase 1 is aimed with a joystick; phase 2 adds face tracking.

> **Status:** design phase. The context pack (M0) is done; nothing is built yet.
>
> **Adults only.** Chewing gum is a choking hazard. Read [docs/safety.md](docs/safety.md) before building or using it.

## How it works

**Phase 1: joystick (being built now)**

1. You sit on a range mark with impact-rated glasses on. The operator steers the turret head with a joystick and lines the sight up on your lower lip, then sets the range on the dial.
2. When you're ready, the operator holds ENABLE and presses FIRE. The robot tilts up by the ballistic offset for that range, chirps, and a spring sled tosses one pellet at about 6 m/s.
3. The microcontroller enforces the rest: the ARM switch, a deadman, 10 s between shots, 5 shots per arming, and a chronograph that locks out over-speed shots.

**Phase 2: face tracking (later)**

1. A camera in the turret head finds your face with MediaPipe and keeps your mouth in its sights.
2. You opt in by raising your eyebrows. The robot chirps, and its eyes say "open wide".
3. Hold your mouth open for 300 ms. If every safety gate passes, it fires, aimed so the pellet lands on your tongue, well clear of your eyes.

## Docs

| | |
|---|---|
| [Brief](docs/brief.md) | The original brief and the owner's answers |
| [Requirements](docs/requirements.md) | Testable requirements and the accuracy error budget |
| [Architecture](docs/architecture.md) | Hardware, power and interlocks, software, fire-control state machine |
| [Decisions](docs/decisions.md) | Launcher trade-off and the other design decisions |
| [Safety](docs/safety.md) | Hazards, energy limits, consent, test rules |
| [Roadmap](docs/roadmap.md) | Milestones, in the order that retires risk first |
| [Bench rig](docs/mechanical/) | The M2 launcher and feed test stand, with generated CAD |
| [Research](docs/research/) | Sourced notes on vision, launchers, safety, mechanics and Indian prices |

## Tools

```powershell
python tools/ballistics_sim.py --help
```

This is the ballistics model behind the launcher sizing and the phase 1 holdover table (standard library only). `tools/launcher_design.py` sizes the launcher, and `cad/bench_rig.py` generates the bench-rig CAD (see `cad/requirements.txt`).
