# DESUU: Project brief

The owner's brief, kept verbatim, plus their answers to the setup questions. [requirements.md](requirements.md) turns this into testable requirements. If the two ever disagree, this file and later owner decisions win.

## Owner's request (2026-11-25)

> This is My Upcoming project and it consist of Hardware and Software both Components so make a context for this project, use the web to scan everything you can and use all your tools so that we can start from scratch and build this product

## Brief (verbatim)

> Act as a robotics engineer. Help me design a desktop robot that tracks a
> person's face and launches a piece of pellet chewing gum into their mouth
> when they open it.
>
> Requirements:
> - Range: 0.5 to 2 m, landing within a 3 cm circle at 1 m.
> - Camera-based mouth tracking and open-mouth detection (e.g. MediaPipe
>   Face Mesh) running on a Raspberry Pi 5 or similar.
> - 2-axis pan-tilt turret with closed-loop aiming that keeps the mouth
>   centered, plus distance estimation and ballistic angle compensation.
> - A magazine holding 20+ pieces with a reliable single-piece feed.
> - A launcher with highly repeatable, low exit velocity. Compare spring
>   plunger, flywheel and pneumatic options and recommend one.
> - Safety: fire only when a mouth is open and stable for 300 ms, never aim
>   at eyes, cap exit velocity, physical arm/disarm switch.
> - 3D-printable body, friendly character look, under $250 in parts.
>
> Deliver, in order:
> 1. System architecture diagram and the launcher trade-off.
> 2. Bill of materials with specific parts and prices.
> 3. Mechanical design: turret, feed and launcher, with key dimensions
>    and print settings.
> 4. Wiring diagram.
> 5. Python code: vision pipeline, mouth-open detection, PID aiming,
>    ballistic lookup table, firing state machine.
> 6. Calibration procedure and a test plan for accuracy.
> 7. Extra modes: rotate around a table serving each detected face, and a
>    manual target mode for trick shots.
>
> Ask me about my tools, budget and experience before you start.

## Owner's answers (2026-11-25)

| Topic | Answer | What it means for the design |
|---|---|---|
| Tools | Bambu Lab X1 Carbon, soldering iron, multimeter | 256 × 256 × 256 mm enclosed printer: PETG, ASA, TPU and multi-colour parts are all possible. No caliper yet, so buying a digital caliper comes first: pellets and fits must be measured. |
| Budget | "Without Pi and best cheapest way". Asked to clarify: the brain should be the **cheapest standalone board** that tracks a face well enough | The owner has no Raspberry Pi. Pick the cheapest standalone compute that meets the vision spec and keep everything else lean. Working cap: US$250 ≈ ₹21,000. The BOM shows totals both with and without the compute board. |
| Region | India (₹) | Prices come from Indian sellers (Robu, Robocraze, Amazon.in and others). AliExpress does not serve India. |
| Experience | Python/OpenCV, electronics wiring, CAD, microcontrollers | Full-stack builder: explain the decisions and skip the basics. |
| Owned parts | A Raspberry Pi Pico or an ESP32 board (which one is still to confirm) | Reuse it as the real-time and safety co-processor. |

## Interpretations to confirm

These turn ambiguous phrases into testable numbers. They are working assumptions until the owner changes them.

- **A1, accuracy.** "Landing within a 3 cm circle at 1 m" means at least 90 % of 30 consecutive shots land inside a 30 mm-diameter circle centred on the aim point, 1.0 m away.
- **A2, never aim at eyes.** A ballistic shot must leave the barrel pointing *above* the mouth (roughly 5–20° above the line of sight), so at some distances the bore axis passes near the eyes. The requirement is therefore about **where the pellet can land**: the predicted impact zone, including 3σ scatter and worst-case over-speed, must stay out of an exclusion zone around both eyes, computed from the live face landmarks. No aiming lasers of any kind.
- **A3, cap exit velocity.** The cap is enforced physically (the spring cannot store more energy than the cap allows) and checked on every shot by a chronograph. An over-speed shot locks the launcher out.
- **A4, range.** 0.5–2.0 m is the slant distance from the muzzle to the mouth.
- **A5, budget.** Everything that ends up in the robot counts toward the cap. Tools such as the caliper, and filament for test prints, are listed separately.
