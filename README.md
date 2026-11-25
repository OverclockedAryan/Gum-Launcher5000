# DESUU

A friendly desk robot that tracks your face and, when you ask for one, tosses a piece of pellet gum into your mouth.

> **Status:** design phase. The context pack (M0) is done; nothing is built yet.
>
> **Adults only.** Chewing gum is a choking hazard. Read [docs/safety.md](docs/safety.md) before building or using it.

## How it works

1. A camera in the robot's turret head finds your face with MediaPipe and keeps your mouth in its sights.
2. You opt in by raising your eyebrows. The robot chirps, and its eyes say "open wide".
3. Hold your mouth open for 300 ms. If every safety gate passes, a spring sled tosses one pellet at about 6 m/s. The barrel is aimed above the mouth to allow for gravity, so the pellet lands on your tongue, well clear of your eyes.

## Docs

| | |
|---|---|
| [Brief](docs/brief.md) | The original brief and the owner's answers |
| [Requirements](docs/requirements.md) | Testable requirements and the accuracy error budget |
| [Architecture](docs/architecture.md) | Hardware, power and interlocks, software, fire-control state machine |
| [Decisions](docs/decisions.md) | Launcher trade-off and the other design decisions |
| [Safety](docs/safety.md) | Hazards, energy limits, consent, test rules |
| [Roadmap](docs/roadmap.md) | Milestones, in the order that retires risk first |
| [Research](docs/research/) | Sourced notes on vision, launchers, safety, mechanics and Indian prices |

## Tools

```powershell
python tools/ballistics_sim.py --help
```

This is the ballistics model behind the launcher sizing (standard library only).
