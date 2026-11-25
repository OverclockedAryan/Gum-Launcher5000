# DESUU: Bill of materials v1

Deliverable 2. Version 1, 2026-11-25, consolidated from [research/bom-pricing-india.md](research/bom-pricing-india.md) and [research/compute-camera-india.md](research/compute-camera-india.md). Every link and stock note is in those two files.

- **Prices:** ₹ including GST, as read from seller pages on 2026-11-25. Prices move fast (the Pi rose five times in 2026), so re-check before each order.
- **Design basis:** decisions D-001…D-010: a stepper turret, a snail-cam push sled, a Pi 5 1 GB with an OV5647 camera, and GC9A01 eyes.
- **Microcontroller:** your own Pico or ESP32, so it costs nothing here.

## Totals

| Group | ₹ |
|---|---|
| A. Turret (steppers, drivers, belts, homing) | 2,914 |
| B. Launcher and feed | 1,799 |
| C. Pan bearing | 499 |
| D. Safety switches | 497 |
| E. Power | 634 |
| F. Character (eyes, sound) | 1,396 |
| G. Hardware and wiring | 1,472 |
| H. Compute and camera | 6,942 |
| I. Unpriced small parts (estimate) | 400 |
| **Robot parts (A–I)** | **16,553** |
| J. Filament, 2 kg (skip if you already own PETG/PLA) | 1,661 |
| Shipping, about 5 orders (estimate) | 400 |
| **Total against the ₹21,000 cap** | **₹18,614** (≈ 89 %) |
| **Margin** | **₹2,386** |
| K. Tools (outside the cap) | about 1,000 |

The margin covers the two most likely extra costs:

1. The official 27 W PSU (₹1,063), if the 5 V buck causes under-voltage warnings on the Pi.
2. A spare worm motor (₹599).

The Camera Module 3 step-up (+₹2,800) would use up the whole margin, so it only happens if the M4 benchmark demands it.

## A. Turret (D-008)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Stepper motor | NEMA17 KS42STH34-1504A, 34 mm, 1.5 A | ElectronicsComp | 712 | 2 | 1,424 |
| Stepper driver | MKS TMC2209 V2.0 with heatsink | ElectronicsComp | 414 | 2 | 828 |
| Motor pulley | GT2 20T, 5 mm bore, 6 mm belt | ElectronicsComp | 47 | 2 | 94 |
| Axis pulley | GT2 60T aluminium, 5 mm bore (or print it: −₹410) | ElectronicsComp | 205 | 2 | 410 |
| Belt | GT2 6 mm closed loop, 200 mm (check centres in CAD; 280 mm is ₹51) | ElectronicsComp | 63 | 2 | 126 |
| Homing switch | KW4-Z2F100 lever microswitch | Robu | 16 | 2 | 32 |
| | | | | | **2,914** |

Cheaper option: the 40 mm 42HS40-1504 at ₹444 saves ₹536, but it's 6 mm longer and heavier.

## B. Launcher and feed (D-001, D-006)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Cocking motor | JGY370-12-95, 12 V, self-locking worm, 2 kg·cm rated | Robu | 599 | 1 | 599 |
| Motor driver | TB6612FNG dual H-bridge (12 V capable; not the DRV8833) | ElectronicsComp | 235 | 1 | 235 |
| Shuttle servo | MG90S metal gear (one spare) | ElectronicsComp | 117 | 2 | 234 |
| Sled spring, stiff | 0.6 mm wire, 5 and 8 mm OD, 150 mm (cut to tune the rate) | Amazon.in | 165 | 1 | 165 |
| Sled spring, soft | 0.5 mm wire, OD 6 mm, 40 mm (4 pcs) | Robu | 167 | 1 | 167 |
| Cam follower / small bearings | 623ZZ, 3 × 10 × 4 mm | ElectronicsComp | 22 | 4 | 88 |
| Bearings | 608ZZ (cam shaft, tilt axis) | ElectronicsComp | 22 | 4 | 88 |
| Microswitch | KW4 (cam "ready", shuttle, spare) | Robu | 16 | 3 | 48 |
| IR pairs | 5 mm IR LED + photodiode, 5 pairs (chamber sensor + 2 chronograph gates) | Amazon.in | 175 | 1 | 175 |
| | | | | | **1,799** |

Avoid two parts here:

- Robu's 1 mm × 7.4 mm springs (₹149) are about 3 N/mm. They store far more than the 40 mJ cap allows.
- Ready-made break-beam modules (₹1,481) respond in under 2 ms. That's too slow for chronograph timing.

## C. Pan bearing (D-008)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Thin-section bearing | 6806ZZ, 30 × 42 × 7 mm, 4-pack (use 2; the hollow bore carries the cables) | Amazon.in | 499 | 1 | 499 |

## D. Safety (REQ-SAF-004, -005)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| ARM switch | ASW-07D lit toggle with flip cover, 20 A | Robu | 215 | 1 | 215 |
| E-stop | LAY37 22 mm latching mushroom, twist release, DPST (check the 23 mm neck against the panel hole) | ElectronicsComp | 282 | 1 | 282 |
| | | | | | **497** |

## E. Power

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Supply | 12 V 5 A 60 W adapter (check the 5.5 × 2.1 plug) | Robu | 425 | 1 | 425 |
| Inlet | 5.5 × 2.1 mm panel jack | ElectronicsComp | 14 | 1 | 14 |
| 5 V rail | XY-3606 synchronous buck, 5 V 5 A (Pi + logic) | Robu | 139 | 1 | 139 |
| Fuse | Inline 20 mm glass-fuse holder + 5 A fuse | ElectronicsComp | 56 | 1 | 56 |
| | | | | | **634** |

## F. Character (REQ-BLD-003)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Eyes | GC9A01 1.28" round 240 × 240 SPI | Robu | 494 | 2 | 988 |
| Amplifier | MAX98357A I2S (on the Pi) | Robu | 179 | 1 | 179 |
| Speaker | 40 mm 4 Ω 3 W | Amazon.in | 229 | 1 | 229 |
| | | | | | **1,396** |

Budget fallback: two WS2812 7-LED jewels (₹134) instead of the GC9A01s save ₹854.

## G. Hardware and wiring

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Heat-set inserts | M3 × 4 mm brass, 25 pcs | Robu | 91 | 4 | 364 |
| M3 screws | EasyMech M3 × 6 and M3 × 10 sets with nuts and washers, 25 each | Robu | 67 + 78 | 1 + 1 | 145 |
| M2.5 screws | M2.5 × 10 stainless set (board mounting) | Amazon.in | 285 | 1 | 285 |
| Power wire | 22 AWG silicone, 2 m red + 2 m black | ElectronicsComp | 89 / 85 | 1 + 1 | 174 |
| Signal wire | 26 AWG silicone, 3 m + 3 m | ElectronicsComp | 120 | 1 | 120 |
| Perfboard | 4 × 4" | ElectronicsComp | 45 | 2 | 90 |
| MOSFET | IRLZ44N (spare low-side switching, e.g. for eye backlights) | Robu | 44 | 3 | 132 |
| Diode | 1N5819 Schottky | ElectronicsComp | 6 | 5 | 30 |
| Jumpers | 20 cm Dupont, 40 M-F + 40 F-F | ElectronicsComp | 68 / 64 | 1 + 1 | 132 |
| | | | | | **1,472** |

There's no JST-XH kit: you don't have a crimper. Solder the joints with heat-shrink, and use Dupont leads for anything that has to unplug.

## H. Compute and camera (D-007)

| Item | Part | Seller | ₹ each | Qty | ₹ |
|---|---|---|---|---|---|
| Board | Raspberry Pi 5 **1 GB**. **Out of stock in India on 2026-11-25**: set alerts at Robocraze, Robu and Silverline | Robocraze | 5,044 | 1 | 5,044 |
| Camera | OV5647 5 MP CSI, about 54° × 41°, fixed focus | Quartz | 267 | 1 | 267 |
| Cooling | Official Pi 5 Active Cooler | Quartz | 452 | 1 | 452 |
| Storage | 32 GB microSD (HP; A1 rating not stated. SanDisk Ultra is ₹1,475) | Amazon.in | 770 | 1 | 770 |
| Camera cable | Official Pi 5 22→15-pin, 500 mm (for the turret service loop) | Robu | 409 | 1 | 409 |
| | | | | | **6,942** |

The Pi takes power from the XY-3606 rail, so there's no official PSU on this list (D-007). Check `vcgencmd get_throttled` during the M4 benchmark.

## I. Small parts not yet priced (estimate ₹400)

| Item | Use | Note |
|---|---|---|
| 3 mm polished steel rods, about 2 × 80 mm | Sled guides (D-001) | Drill blanks or 3D-printer rods |
| LM393 comparator module | Clean, fast edges from the chronograph photodiodes | About ₹30 each, 2 needed |
| Urethane or rubber bumper | Sled end stop | Can be printed in TPU on the X1C |
| Silica-gel sachets | Magazine humidity (D-006) | |
| Extension spring | Shuttle return (REQ-SAF-015) | Pick from a spring assortment |
| Hall sensor A3144 + magnet | Optional second homing reference | |
| M5 × 60 and M5 × 25 bolts, nut, wing nut, washers | Bench-rig stand pivot and elevation lock | About ₹40 |
| Extension spring, about 10 mm body | Shuttle return on the bench rig | From the spring assortment |
| Zip ties, 3.6 mm | Hold the JGY370 in its printed cradle | |

## J. Filament

| Item | Part | Seller | ₹ |
|---|---|---|---|
| PETG, natural or clear, 1 kg | Mechanisms and the gum path | Amazon.in (Haiteng) | 869 |
| PLA+, 1 kg | Shell in your character colours | Amazon.in (Gratkit) | 792 |

Food path (REQ-FEED-004): print gum-touching parts with a stainless nozzle, not the X1C's stock hardened-steel one, or line them with PTFE.

## K. Tools (outside the cap)

| Item | Part | ₹ |
|---|---|---|
| Digital caliper | Aurdeayi 150 mm stainless, 0.01 mm (Amazon.in) | 699 |
| Pocket scale | 0.01 g jewellery scale for weighing pellets | about 300 (estimate, not researched) |
| Safety glasses | Impact-rated, ANSI Z87.1 or EN 166 (REQ-SAF-016) | not researched |

## Order plan

Buy in milestone order, so money is spent only once the part before it works.

| Order | When | What | Approx ₹ |
|---|---|---|---|
| 1 | Now (M2 bench rig + measuring; design in [mechanical/bench-rig.md](mechanical/bench-rig.md)) | **Tools:** caliper, scale, glasses. **Launcher and feed:** everything in group B, the I parts. **Safety:** group D. **Power:** group E, including the XY-3606 (it powers the shuttle servo on the bench rig). **Wiring:** group G. **Filament:** PETG | ≈ 5,700 + tools |
| 2 | M3 (vision on the PC) | Nothing: use your laptop's built-in webcam | 0 |
| 3 | M4 (turret) | Groups A and C; group H (the Pi, if it's back in stock) | ≈ 10,350 |
| 4 | M7 (character) | Group F; PLA+ | ≈ 2,200 |

**Seller grouping:** one ElectronicsComp cart and one Robu cart per phase, plus the Amazon-only items: the 6806 bearings, the 0.6 mm spring, the IR pairs, the speaker, the M2.5 screws, the filament and the caliper. ElectronicsComp showed a 10 % prepaid coupon (unverified at checkout).

## Changes from the research basket

- **Turret:** steppers instead of the ST3215 servo set: −₹2,935.
- **Spare worm motor:** dropped (−₹599); buy it only if the M2 rig wears through one.
- **Fuse holder:** the glass-fuse version instead of the blade kit: −₹236.
- **Screws:** Robu M3 packs instead of the Amazon kit: −₹399.
- **JST-XH kit:** dropped, because there's no crimper: −₹389.
- **Compute:** priced without the official PSU, with a 500 mm camera cable instead of 200 mm.
