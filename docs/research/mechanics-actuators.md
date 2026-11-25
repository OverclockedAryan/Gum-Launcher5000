# Mechanics & Actuators Research

Last researched: 2026-11-25 (web research; verify before buying or building)

Notation: **(calc)** = my own arithmetic from the cited figures; **(unverified)** = I could not find a source. Prices are late-2026 snapshots and several listings were sold out. The web-search quota ran out near the end of this pass, so a few prices are marked unverified.

## Key takeaways for the design

- **A direct-drive STS3215 will not hold 0.3° on its own.** A bench test measured 0.87° free play (the spec says ≤0.5°), a ~10-count (≈0.88°) firmware deadband and ~2° error under a 10 kg·cm load. Repeatability was ±0.17° (≈2 counts) with a light preload ([Robonine, Oct 2025](https://robonine.com/testing-of-feetech-sts3215-servomotor-backlash-repeatability-and-torque/), [SO-ARM100 #134](https://github.com/TheRobotStudio/SO-ARM100/issues/134)). The plan should include: a constant preload so the gears never reverse (a slightly unbalanced tilt, plus a torsion spring or drag on pan); a 3:1–4:1 GT2 belt stage, which shrinks play and deadband to ≈0.2–0.3° at the turret (calc); and a rule to fire only after the turret camera confirms a small residual error.
- **Ballistics, not servos, set the error budget (calc).** With the gravity drop h = g·L²/(2v²cos²θ), the vertical miss is ≈ 2h·(Δv/v) and ≈ h·(ΔL/L). That gives h ≈ 0.20 m at 1 m/5 m/s, 0.42 m at 2 m/7 m/s and ≈1.0 m at 2 m/5 m/s. Staying within ±1.5 cm at 2 m/7 m/s needs about ±1.8 % shot-to-shot speed and ±3 % range accuracy.
- **Slow shots also push the face out of frame (calc).** The launch angle for a target at launcher height is 26° at 2 m/5 m/s and 12° at 2 m/7 m/s. Camera Module 3 sees only ±20.5° vertically (66°×41°; the Wide version is 102°×67°) ([Raspberry Pi docs](https://www.raspberrypi.com/documentation/accessories/camera.html)). If the camera and barrel share the tilt stage, use ≥6–7 m/s, the Wide camera, or a fixed barrel elevation offset.
- **Speed ceiling:** EN 71 is reported to cap rigid projectiles at 0.08 J, though two QIMA pages describe the EN 71 rule differently. ASTM F963-16 caps projectiles above 0.08 J at 2500 J/m² ([QIMA EN 71 a](https://qima.com/testing/toy-safety/toy-gun-projectile-safety), [QIMA EN 71 b](https://www.qima.com/consumer-products/lab-testing/toy-gun-projectile-safety), [QIMA F963](https://www.qima.com/astm-f963-16-toy-safety-standard), [CPSC letter](https://www.cpsc.gov/s3fs-public/TIA_projectile%20toys_let_3.31.17.pdf)). A 2.0 g pellet reaches 0.08 J at 8.9 m/s and a 1.4 g pellet at 10.7 m/s (calc). At 7 m/s a pellet carries 34–49 mJ.
- **Pellet mass depends on the brand:** Mentos Pure Fresh is ≈2.0 g a piece (100 g/50) ([Tesco](https://www.tesco.com/groceries/en-GB/products/314925975)), above the assumed 1.2–1.6 g, and Wrigley Extra is ≈1.4 g (64 g/46) ([Ocado](https://www.ocado.com/products/extra-white-sugarfree-chewing-gum-bottle-46-pieces/265792011)). Size the spring for 1.3–2.1 g and re-calibrate for each brand.
- **Don't feed from a bulk hopper.** Coarse particles can arch over outlets smaller than ~6 particle diameters, and practitioners recommend 8–10×. For a 15 mm pellet that is 90–150 mm ([Purdue](https://engineering.purdue.edu/~wassgren/teaching/ME30800/Examples/dim_anal_18.pdf), [Process Industry Informer](https://www.processindustryinformer.com/?p=53819)). Use an orientation-locking single-file stack with a shuttle, or a 20-chamber revolver. Size gates between 1× and 2× the pellet thickness; feeder patents use ≈1.5×.
- **±180° pan is feasible without a slip ring.** Waveshare's ST3215 pan-tilt reaches ±180°, lists no slip ring, and ships 400–600 mm FFCs ([Waveshare](https://www.waveshare.com/2-axis-pan-tilt-camera-module.htm?sku=24984)). Run the 500 mm Pi 5 camera FFC as a service loop through a hollow 6806/6808 bearing (30/40 mm bore). Skip lazy-susan bearings, which have lateral play.
- **Materials:** use PETG (or ASA/ABS) for cams, sears, gears and slides. PLA and PLA+ soften around 52–60 °C and creep. Keep the spring relaxed except just before a shot; a snail cam can be run backwards to de-cock on disarm.
- **Electronics gotchas:** the DRV8833 tops out at 10.8 V, so use a TB6612FNG (13.5 V) for 12 V motors ([Pololu 2130](https://www.pololu.com/product/2130), [Pololu 713](https://www.pololu.com/product/713)). WS2812 support on the Pi 5 is experimental or pre-release, so drive the LEDs (and probably the eyes) from the Pico 2. Adafruit break-beam modules respond in under 2 ms, which is fine for presence sensing but too slow for a chronograph.

## 1. Turret actuators

| Option | Supply | Stall torque | Sensing / resolution | Backlash / deadband | Speed | Interface | Price (USD), where |
|---|---|---|---|---|---|---|---|
| Feetech STS3215 12 V (C018) | 6–12.6 V | 30 kg·cm @12 V, 2.7 A | 12-bit magnetic, 4096/rev = 0.088° | spec ≤0.5°; measured 0.87–1°; ~10-count deadband seen | 0.222 s/60° (45 rpm) | half-duplex TTL bus, 38.4 k–1 Mbps (1 M default), IDs 0–253 | $16.99–21.99 [Waveshare](https://www.waveshare.com/st3215-servo.htm); $31.38 [RobotShop](https://www.robotshop.com/products/feetech-12v-30kgcm-magnetic-encoding-servo-sts3215) |
| STS3215 7.4 V (C001) | 4–7.4 V | 19.5 kg·cm @7.4 V, 2.5 A | same | same class | 0.192 s/60° (52 rpm) | same | same Waveshare range; [DFRobot](https://www.dfrobot.com/product-2961.html) |
| Dynamixel XL330-M288-T | 3.7–6 V (5 V rec.) | 0.52 N·m @5 V (~0.10 N·m rated) | 12-bit AS5601 | not published; plastic gears 288.4:1 | 103 rpm @5 V | TTL half-duplex ≤4 Mbps, 3.3 V logic | $27.49 [robotis.us](https://robotis.us/dynamixel-xl330-m288-t) (sold out) |
| Dynamixel XL430-W250-T | 6.5–12 V | 1.4 N·m @11.1 V | 12-bit AS5601 | not published; plastic gears 258.5:1 | 57 rpm @11.1 V | TTL half-duplex ≤4.5 Mbps, 5 V logic | $27.50 [robotis.us](https://www.robotis.us/dynamixel-xl430-w250-t/) (sold out; [MSRP was $44.90](https://www.robotis.us/robotis-blog/xl430-price-change-xseries-accessories/)) |
| MG996R (hobby PWM) | ~4.8–7.2 V (unverified) | ~9–11 kg·cm (unverified) | potentiometer, ~1–2 ms pulse | 5 µs deadband ≈ 0.9° (calc) | ~0.17 s/60° (unverified) | 50 Hz PWM | ~$5–15 (unverified) |
| DS3218 (hobby digital) | 4.8–6.8 V | 19–21.5 kg·cm | potentiometer, 500–2500 µs = 270° | 3 µs ≈ 0.4° (calc) | 0.16 s/60° @5 V | PWM | ~$15–21 eBay/Newegg (unverified) |
| NEMA17 + TMC2209 + GT2 4:1 | 12–24 V (unverified) | depends on motor | open loop; 0.45°/full step at output, 0.028° at 1/16 (calc) | no gear lash, but belt stretches; microstep error under load | limited by driver and step rate | STEP/DIR + UART | pancake motor $18–20 [Abra](https://abra-electronics.com/electromechanical/motors/stepper-motors/nema-17/mot-17hs4023-17hs4023-nema-17-43mm-1.8a-dual-phase-stepper-motor-1.8.html); TMC2209 $6.94 [BIQU](https://biqu.equipment/collections/driver-board/products/bigtreetech-tmc2209-stepper-motor-driver-for-3d-printer-board-vs-tmc2208) |

- **12 V vs 7.4 V:** the 12 V C018 gives 54 % more torque at about the same stall current (calc), and it matches the bus adapter's 9–12.6 V input. Spec sheets for C001 (the 7.4 V SO-ARM100 servo) and C018 often get mixed up ([Core Electronics forum](https://forum.core-electronics.com.au/t/sts3215-smart-servo-packet-based-servo-19kg-cm-ce09383/20745)).
- **Measured behaviour** ([Robonine](https://robonine.com/testing-of-feetech-sts3215-servomotor-backlash-repeatability-and-torque/)):
  - Stall torque was ~35 kg·cm.
  - Position error was 22.5 counts (~2°) at 10 kg·cm and 30 counts (~2.6°) at 15 kg·cm.
  - During ±90° oscillation the servo overheated (71 °C after ~110 min) with acceleration register 2, but held at about 60 °C with register 5.
  - Two opposed servos pulling on a cord removed the play.
  - An open-source backlash test rig is on [Zenodo (Mar 2026)](https://zenodo.org/records/19261714).
- **Registers** ([aifitlab memory table](https://wiki.aifitlab.com/feetech-servo-motor-docs/feetech-sts-servo-memory-table-analysis), [Waveshare memory map](https://docs.waveshare.com/Memory_Map_Explanation/ST_Servo_Memory_Map_Explanation)):
  - Dead zone at 26/27 defaults to 1 (range 0–16 × 0.087°). This conflicts with the ~10 counts measured, so check your units.
  - P/D/I gains are at 21/22/23, and acceleration is at 41.
  - Mode register 33: 0 = position, 1 = speed, 2 = PWM, 3 = step.
  - Setting both angle limits (9/11) to 0 enables multi-turn absolute control, with goal positions of ±32767 counts.
  - Present current is at 69 (6.5 mA per count).
- **Belt stage:** run the servo in multi-turn mode behind a 3:1 belt, which also gives 0.029° per count and ~90°/s at the turret (calc). The encoder is only absolute within one servo turn, so add a home or index sensor on the output, such as a hall sensor or AS5600 (unverified).
- **Python libraries:**
  - official [FTServo_Python](https://github.com/ftservo/FTServo_Python) (`scservo_sdk`; on PyPI as `ftservo-python-sdk`)
  - [`feetech-servo-sdk`](https://pypi.org/project/feetech-servo-sdk/), which LeRobot uses ([Zenn, May 2026](https://zenn.dev/usagi1975/articles/2026-05-18-000_sts3215-python))
  - [`python-st3215`](https://pypi.org/project/python-st3215/): v1.2.1 (May 2026), GPL-3.0, tested on Waveshare ST3215
  - [`st3215`](https://pypi.org/project/st3215/): `ListServos()`/`MoveTo()` API, installed from source
  - [rustypot](https://docs.rs/crate/rustypot/latest): Rust with Python bindings
- **USB adapter:** the [Waveshare Bus Servo Adapter (A)](https://www.waveshare.com/product/bus-servo-adapter-a.htm) costs $4.99 and measures 42×33 mm. Jumper B selects USB-C and jumper A selects UART to Pi or Pico GPIO; the wiki says to wire RX-RX and TX-TX, so check the schematic. Its input is rated 9–12.6 V and should match the servo voltage. The USB chip, current rating and power path are not stated ([wiki](https://www.waveshare.com/wiki/Bus_Servo_Adapter_%28A%29)).
- **Mounting:** the plastic-cased STS3215 takes self-tapping screws, so brackets designed for the metal STS3250 don't fit ([FAC1 notes](https://www.printables.com/model/1463101-fac1-fyrby-additive-camera-1)).
- **Dynamixel:**
  - Better documentation and a current-based position mode for soft compliance ([XL330 manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/), [XL430 manual](https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/)).
  - Backlash is not published for either; the metal-gear XM430 lists 0.25° ([XM430](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350)).
  - The XL330's ~0.10 N·m continuous rating is thin for an unbalanced tilt stage (calc).
  - The XL430 needs a U2D2 adapter (~$32, unverified) or a half-duplex buffer.
- **Hobby PWM servos:**
  - 180° or 270° of travel cannot cover ±180° of pan.
  - Potentiometer feedback can be off by ~0.5° depending on approach direction ([Parallax forum](https://forums.parallax.com/discussion/comment/826864)).
  - Deadband is 5 µs on the MG996R ([datasheet](https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2017/kmv48_rp625/kmv48_rp625/kmv48_rp625/MG996RTowerPro.pdf)) and 3 µs on the DS3218 ([specs](https://thinkrobotics.com/products/ds3218-servo)).
  - Generate the pulses on the Pico, not from Linux.
- **Steppers:**
  - isaac879's printed mount (2020-era files) used a TMC2208, 144:17 pan and 64:21 tilt belts, and hall-sensor homing. Pan resolution was 0.0133°, but speed was only ~20°/s at 1/16 microstepping on an Arduino Nano ([GitHub](https://github.com/isaac879/Pan-Tilt-Mount)).
  - Microstep torque scales with sin(90°/N): about 20 % of holding torque at 1/8 and 5 % at 1/32. Loads above that cause errors of up to ±2 full steps, though ±0.03° has been shown unloaded ([MPS](https://www.monolithicpower.com/en/learning/resources/why-microstepping-isnt-as-good-as-you-think), [Hackaday 2016](https://hackaday.com/2016/08/29/how-accurate-is-microstepping-really/)).
  - The TMC2209 interpolates to 256 microsteps and is quiet in StealthChop2. Its StallGuard4 stall detection works only in StealthChop and is unreliable below about 2 rev/s, so home with a hall sensor instead ([ADI](https://www.analog.com/en/products/tmc2209.html), [Valar wiki](https://github.com/Valar-Systems/valar-motion/wiki/StallGuard-Tuning)).
  - Steppers run open loop, so missed steps go unnoticed.
- **Camera resolution is not the bottleneck (calc):** 66° over 4608 px is 0.014° per pixel, or 0.043° per pixel in the 1536×864 p120 mode.

## 2. Open-source turrets, pan bearings, cabling

- **Turret projects:**
  - [Waveshare 2-Axis Pan-Tilt](https://www.waveshare.com/2-axis-pan-tilt-camera-module.htm?sku=24984) ($109.99, about 45 % of the budget): two direct-drive ST3215s with pan ±180° and tilt −45° to +90°. It uses a thrust ball bearing and ships with 600 mm and 400 mm 15-pin FFCs, a 500 mm Pi 5 camera cable and an ESP32 driver board. This is the closest off-the-shelf match.
  - [OpenTurret](https://github.com/cubanmakers/OpenTurret/blob/main/README.md): 2× NEMA17 and 2× TMC2209, printed parts with stock bearings and rods, 360° pan and ±135° tilt. It is a laser turret that its authors call experimental.
  - [Digital Bird head](https://www.printables.com/model/326746-camera-pan-tilt-head-digital-bird): NEMA17 motors with 20T GT2 pulleys and 200/360 mm belts, 360° continuous pan and 130° tilt.
  - [Gantry Bot head](https://hackaday.com/2026/03/02/pan-tilt-head-for-camera-motion-control) (Mar 2026): NEMA17 belt-driven tilt; it needs some CNC-machined metal parts.
  - isaac879 mount: see §1.
- **Face trackers (servo-based, older):**
  - [Pimoroni Pan-Tilt HAT](https://learn.pimoroni.com/building-a-pan-tilt-face-tracker) (2014)
  - [Core Electronics Pi + OpenCV guide](https://core-electronics.com.au/guides/face-tracking-raspberry-pi/) (updated 2023)
  - [ESP32-CAM SG90 turret](https://www.instructables.com/ESP32-Turret-Face-Tracking-Live-Wi-Fi-Stream)
- **Launcher prior art:**
  - HTX Studio's "Gummy" (Mar 2025) tracks the mouth and fires gum when it opens; the mechanism isn't disclosed ([Futurism](https://futurism.com/robot-launches-gum-into-mouth)).
  - Harrison McIntyre's M&M launcher (2020) used a DC-motor flywheel with Hall-sensor speed regulation, firing at 23 mph (~10 m/s). It aimed with servo pitch and yaw and found the mouth from facial landmarks ([Hackaday](https://hackaday.com/2020/05/11/alexa-shoot-me-some-chocolate), [Arduino blog](https://blog.arduino.cc/2020/05/14/beat-boredom-with-a-alexa-controlled-face-tracking-candy-launcher/)).
  - "Snacky" by Ricky Robot lands popcorn about half the time ([Hackster](https://www.hackster.io/news/ricky-robot-s-snacky-wants-to-feed-you-popcorn-and-succeeds-about-half-of-the-time-f5f3bb94bc84)).
  - [Chopstix](https://devpost.com/software/chopstix) detected an open mouth from dlib's mouth aspect ratio.
- **Pan bearing options:**
  - *Lazy susan:* cheap, but not built for lateral loads ([gm0](https://game-manual-zero.readthedocs.io/en/latest/docs/common-mechanisms/turrets/full-turret.html)), and one budget unit had ~1 mm of lateral play ([IceInSpace](https://www.iceinspace.com.au/63-378-0-0-1-0.html)). Use one only with an extra radial constraint and preload.
  - *608ZZ pair* (8×22×7 mm) on an 8 mm shaft, spaced well apart: stiff and cheap, but the solid shaft blocks the axis, so cables must run off-axis (unverified rule of thumb).
  - *Thin-section 6806 (30×42×7 mm) or 6808 (40×52×7 mm):* the hollow bore takes the FFC and wires. Prices run from $2.85 (6806, [Lily Bearing](https://www.lily-bearing.com/products/6806/)) to ~A$34 (6808, [Minibearings](https://minibearings.com.au/products/40x52x7-ball-6808)). These are deep-groove bearings, so stack two or add an axial thrust face to resist tipping (unverified).
  - *Printed race with 6 mm airsoft BBs:* for example a [6812-size BB bearing](https://www.printables.com/model/1411581-6812-60x78x10-mm-3d-printable-bearing-uses-6-mm-ai) (60×78×10 mm) or an [angled-contact radial/axial design](https://www.printables.com/model/859778-hybrid-radialaxial-bearing-airsoft-bbs). Clearance is critical: too tight seizes and too loose plays ([Hackaday](https://hackaday.com/2017/06/12/big-slew-bearings-can-be-3d-printed)). One print-in-place test found 0.20 mm best (from a search summary).
- **Camera cable:** the Pi 5 uses a 22-pin 0.5 mm FPC, with official cables in 200, 300 and 500 mm ([Raspberry Pi](https://www.raspberrypi.com/products/camera-cable/)). Adafruit's 500 mm 22→15-pin version costs $2.50 ([Adafruit 5820](https://www.adafruit.com/products/5820)). The MagPi says CSI ribbons longer than the stock 20 cm aren't guaranteed ([MagPi](https://magpi.raspberrypi.com/articles/review-thine-cable-extension-kit)), so test the 500 mm cable in its service loop.
- **Service loop (clock-spring style):** wind the FFC as a spiral or rolling loop around the hollow axis. Fine-gauge flat cable lasts tens of millions of flex cycles ([DigiKey](https://www.digikey.com/en/articles/designing-with-flexible-flat-cable)). A Bosch camera patent adds an anti-rotation arm to stop the FFC twisting ([US8325229](https://patents.google.com/patent/US8325229)). Add hard stops just past ±180° (unverified). Reachy Mini Lite's store page lists ±160° of body rotation, though another source claims 360° ([Pollen store](https://store.pollen-robotics.com/products/reachy-mini-lite-version)).
- **Slip ring:** a CSI ribbon can't pass through one. [SparkFun's 12-wire 2 A capsule](https://www.sparkfun.com/slip-ring-12-wire-2a.html) costs $27.95, runs to 250 rpm, and its maker claims USB/Ethernet capability ([datasheet](https://cdn.sparkfun.com/datasheets/Robotics/SNM022A-12%20updated.pdf)). If the Pi 5 and camera ride on the turret, send 12 V over several paralleled rings (2 A each) and step down to 5 V on the rotating side (calc). CSI-to-HDMI extenders reach 3–5 m (vendor claim, [Arducam](https://core-electronics.com.au/catalog/product/view/sku/AC-B0091)), but they still can't pass a slip ring.

## 3. Single-piece feed for pillow-shaped gum pellets

- **Pellet data:** Mentos ≈2.0 g and Extra ≈1.4 g (see takeaways). Dimensions, thickness spread and coating dust or tack are unmeasured (unverified). Measure 20 pellets of the chosen brand before fixing any geometry.
- **Hopper arching:** coarse particles arch over an outlet smaller than about 6 particle diameters ([Purdue ME308](https://engineering.purdue.edu/~wassgren/teaching/ME30800/Examples/dim_anal_18.pdf)). Practitioners suggest 8× for round and 10× for irregular particles, and note that no size is fully safe ([Bates guidelines](https://www.bulk-online.com/en/node/73244), [Bates table](https://www.bulk-online.com/de/node/72170), [Process Industry Informer](https://www.processindustryinformer.com/?p=53819); from search summaries). A hopper therefore needs a moving floor, such as a disc or agitator.
- **Gate and wiper gap:** keep it above 1× and below 2× the part thickness. One feeder patent finds about 1.5× works well ([US4700827](https://patents.google.com/patent/US4700827A/en), [US6374985](https://patents.google.com/patent/US6374985B1/en)), which is 8.5–11 mm for 7 mm pellets (calc).
- **Option A: gravity stack + sliding shuttle (coin or pill style)**
  - Lock orientation (calc): keep each clearance smaller than (diagonal − dimension) for every flip axis. A 16×11 mm channel stops a 15×10×7 pellet flipping, because its 12.2 mm and 16.6 mm diagonals don't fit. Rounded pillow edges shrink the diagonals, so test.
  - Make the shuttle pocket ≈1.05–1.2× the pellet thickness, so the next pellet can't drop in and get pinched. Chamfer the stack exit in the shuttle's direction of travel (unverified).
  - A 20-pellet stack is 140 mm tall (calc). A spring follower, as in a PEZ dispenser, keeps it feeding when the turret tilts (unverified).
  - Prior art: a spring-loaded escapement releases only the bottom cup into a shuttle, and a reflective sensor confirms each dispense ([US6117391](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6117391)).
- **Option B: revolver cylinder.** Each chamber holds one pellet, so singulation can't fail. Twenty chambers at ~14 mm pitch need a ~90 mm pitch circle (calc). Index it with a servo or stepper, push each pellet out axially, and reload by hand. This is the most deterministic option.
- **Option C: hopper + singulating wheel or agitator.** A pill-dispenser style pocketed disc forms the hopper floor.
  - Student builds jiggle the disc to seat pills and add a stopper against extras ([NTU](https://blogs.ntu.edu.sg/ps5888-2023-g09/2023/09/24/3d-printing-phase-2)).
  - A 2025 project compared conical, triangular, parabolic and hyperbolic pockets ([Trinity College PDF](https://www.trincoll.edu/engineering/wp-content/uploads/sites/31/2025/05/2025-Curran_-Goldmann_-Sippel.pdf)).
  - Patents describe reverse rotation to clear jams and transition pockets to break up bridging (from search summaries; I did not open the patents).
  - This option has the most moving parts and the most jam modes.
- **Sensors:**
  - [Adafruit 2167](https://www.adafruit.com/product/2167) 3 mm break-beam ($2.95): ~25 cm range, 10° beam, under 2 ms response, open-collector output that needs a pull-up, and a 10/20 mA emitter at 3.3/5 V. The 5 mm version (2168) reaches further.
  - [TCRT5000](https://www.vishay.com/en/product/83760/) reflective sensor: peak response at ~2.5 mm (datasheet value), 950 nm. Pellet colour and ambient IR will affect it (unverified).
  - Use one sensor for "pellet chambered" and a pair at the muzzle for "pellet left" plus speed.

## 4. 3D printing for functional mechanisms

- **Materials:**
  - **PLA:** Tg ≈60 °C, which is not a safe temperature for a loaded part ([Snapmaker](https://www.snapmaker.com/blog/petg-vs-pla/)). Users report it creeps under constant load ([Bambu forum](https://forum.bambulab.com/t/pla-vs-petg-hf-deformation-under-load/212834)). Use it for shells and cosmetic parts.
  - **PLA+:** tougher than PLA but has the same ~60 °C Tg, with an HDT of ~52 °C in one comparison ([Wevolver](https://www.wevolver.com/article/petg-vs-pla-plus-comparison-of-two-affordable-filaments)).
  - **PETG:** Tg ≈80 °C and HDT ~64 °C. It had the longest wear life against ABS and PLA in a 900 rpm, 1.5 N·m gear test ([paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9147857/), [Hackaday 2025](https://hackaday.com/2025/07/17/this-service-life-study-really-grinds-our-gears)). It is reported to have lower friction than PLA (unverified). Use it as the default for cams, sears, plungers and slides.
  - **ASA/ABS:** higher temperature (Tg ~100 °C, unverified). A 2024 creep study of ABS, ASA, PLA and PC found fibre reinforcement improves creep stability ([Open Engineering](https://doi.org/10.1515/eng-2024-0084)).
- **Parts under constant spring load:** let steel springs store the energy and use printed parts only to guide and latch. Put metal pins or inserts at the sear and cam-follower contacts, and don't leave the plunger cocked for hours, because creep shifts the exit speed (unverified).
- **Gears:** use ≥5 walls, ≥35 % infill and helical or herringbone teeth. Helical gears push axially, so give them thrust-capable bearings. Geometry and print settings mattered more than material ([Hackaday 2024](https://hackaday.com/2024/06/12/studying-the-finer-points-of-3d-printed-gears)).
- **Orientation:** print gears and cams flat so tooth loads stay in-plane, and make sliding faces smooth side walls. Avoid loading across layer lines (unverified general practice). Print orientation strongly affects wear but barely changes friction ([Tribology Online](https://www.jstage.jst.go.jp/article/trol/18/6/18_302/_article)).
- **Fits:**
  - Snug fits run 0.15–0.20 mm, sliding fits 0.20–0.25 mm and separate parts 0.30–0.40 mm ([UF makerspace](https://makerspace.uflib.ufl.edu/services/3dprocess/recommended-software-for-3d-printing/designing-for-3d-printing-tolerances-on-the-mk4-and-xl/); the page's value-to-row mapping is ambiguous).
  - Hinge pins need 0.2–0.3 mm ([Snapmaker hinges](https://www.snapmaker.com/blog/3d-printed-hinges/)), and desktop FDM holds about ±0.15 mm ([Snapmaker tolerances](https://www.snapmaker.com/blog/3d-printing-tolerances)).
  - Print a 0.1–0.5 mm gap coupon first.
  - For bearing press fits, start near nominal and tune with test rings (unverified). Give horizontal holes teardrop tops.
- **Heat-set inserts:** CNC Kitchen M3×5.7 mm inserts cost $10.99 per 100 and go in at print temperature +10–20 °C ([Prusa](https://www.prusa3d.com/product/threaded-inserts-m3-standard-100-pcs/)). The M3 pilot hole is ≈4.0 mm (−0/+0.1) ([Accu chart](https://accu-components.com/p/488-threaded-insert-hole-size-charts-for-3d-printing-pla-petg-resin)).
- **Print-in-place pitfalls:** these joints need bigger gaps than separate parts, and no clearance works on every printer. Over-extrusion fuses joints, so cut flow by 2–5 %. Elephant's foot fills bottom gaps, so chamfer them ([JLC3DP](https://jlc3dp.com/blog/print-in-place-hinge)).

## 5. Launcher and feeder components

- **Energy (calc):** a pellet carries 34–49 mJ at 7 m/s. The spring also has to move the plunger and about ⅓ of its own mass ([PASCO](https://pasco.com/support/knowledge-base/76), [UNC lab](https://webassign.net/sample/unc/lab_4/manual.html)). With a 2 g pellet, 4 g plunger and 3 g spring, efficiency is ≈29 %, so the spring must store ≈0.17 J: about 0.85 N/mm over a 20 mm stroke, peaking at 17 N. Keep the plunger light.
- **Snail-cam torque (calc):** 17 N over a 20 mm rise in 300° needs ≈0.065 N·m. A sliding follower adds μ·F·r ≈0.13 N·m (μ = 0.3 at r = 25 mm). Use a ball-bearing roller follower and give the cam shaft its own bearings. Plan for ≥0.2 N·m (2 kg·cm).
- **Worm gearmotors:**
  - N20 12 V 1:603: 27 rpm, rated 579 g·cm, stall 1929 g·cm, self-locking, $8.95 ([RobotShop](https://www.robotshop.com/products/e-s-motor-12v-tiny-dc-worm-gear-motor-w-dual-shaft-27rpm)). That is marginal for this cam.
  - Back-drive resistance depends on ratio and load, so a worm is not a safety brake ([CHIHAI listing](https://rcdrone.top/products/chf-gw12t-n20va-worm-gear-motor)).
  - JGY-370 12 V at 1:37.3: 160 rpm, 2.2 kg·cm stall, 1 A ([Seeed](https://www.seeedstudio.com/ASLONG-JGY-370-12V-DC-Worm-Gear-Motor-p-1887.html), discontinued). Ratios from 40:1 to 1000:1 give 0.9–45 kg·cm stall at 1.7 A ([OzRobotics](https://ozrobotics.com/shop/370-miniature-worm-gear-motor-jgy-370b-24mm-electric-dc-gear-motor-12v-95rpm-162-4-ratio/)). Pick ≥5 kg·cm stall, which gives a 1–2 s cocking time.
- **Motor drivers:**
  - [DRV8833](https://www.pololu.com/product/2130) ($10.95): 2.7–10.8 V, 1.2 A continuous and 2 A peak, an nFAULT output, and optional current limiting.
  - [TB6612FNG](https://www.pololu.com/product/713) ($4.95): 4.5–13.5 V, 1 A continuous (2 A with channels paralleled) and 3 A peak, 100 kHz PWM, a STBY pin and thermal shutdown. Use this one at 12 V.
- **Shuttle servo MG90S:** 1.8 kg·cm at 4.8 V and 2.2 kg·cm at 6 V, 0.10 s/60°, 13.4 g, metal gears. Its deadband is listed as 1–5 µs depending on the vendor ([Components101](https://components101.com/motors/mg90s-metal-gear-servo-motor)).
- **Solenoid JF-0530B:** 6 V or 12 V, 10 mm stroke, ~5 N. Listings conflict on current, from 0.3 A continuous to ~0.8–1 A short-term ([otronic](https://www.otronic.nl/en/solenoid-12v-push-and-pull-300ma-jf-0530b.html), [tronic.lk](https://tronic.lk/product/jf-0530b-12vdc-1a-5n10mm-pull-push-type-solenoid-switch)). Power it only for seconds at a time. As a sear release, 5 N barely beats the sear friction (≈0.3 × 17 N, calc), so use a two-stage or roller sear (unverified).
- **Solenoid drive from the 3.3 V Pico:**
  - Use a logic-level N-MOSFET whose R_DS(on) is specified at ≤3.3 V gate drive; some IRF parts barely turn on at 3.3 V ([DigiKey guide](https://forum.digikey.com/t/guide-to-selecting-and-controlling-a-mosfet-for-3-3-vdc-logic-applications/42606)).
  - Add a 10 kΩ gate pulldown and a small gate resistor.
  - Use a Schottky flyback diode (1N5819/SS34) rather than a 1N4007. A diode plus Zener releases about 3× faster.
  - For long holds, use peak-and-hold PWM at 25–40 kHz with 30–50 % hold duty ([applied-ee](https://applied-ee.github.io/embedded/docs/motor-control/linear-actuators-solenoids/solenoid-drive-circuits/)).
  - Wire the arm/disarm switch to break launcher power, not just a GPIO (unverified).
- **Springs:** [Lee Spring kits](https://leespring.com/spring-kits) list wire diameter, OD, length and load ranges, and [McMaster assortments](https://www.mcmaster.com/products/compression-spring-assortments/) also publish specs. Generic kits rarely list rates (unverified). Measure k yourself with a scale.
- **Flywheel alternative:** a flywheel lets you set the speed per shot (McIntyre held his with a Hall sensor), which would let speed rather than elevation handle range. Whether coated gum grips a wheel consistently is unknown (unverified).
- **DIY chronograph:**
  - Use two IR gates 50–100 mm apart, each a 940 nm LED and phototransistor feeding a Schmitt or comparator input. [OpenChrono](https://www.xythobuz.de/openchrono.html) uses SFH 309 phototransistors; a forum build used 0.2 m spacing ([SparkFun](https://community.sparkfun.com/t/yet-another-chronograph-project/27433)).
  - At 5 m/s over 50 mm the transit takes 10 ms, so 1 µs timing adds only 0.01 % error. Gate spacing (±0.2 mm is ±0.4 %) and beam width dominate (calc).
  - Timestamp the edges on the Pico 2; RP2040 PIO capture reached ~62.5 ns resolution ([Columbia paper](https://www.cs.columbia.edu/~sedwards/papers/hui2023timestamp.pdf)).
  - Don't use break-beam modules with millisecond-scale response for timing.

## 6. Friendly character look

- **GC9A01 1.28″ 240×240 eyes:**
  - [Adafruit #6178](https://learn.adafruit.com/adafruit-1-28-240x240-round-tft-lcd?view=all) uses the GC9A01A: 3.3/5 V, 4-wire SPI, an onboard framebuffer and an EYESPI FPC connector. Libraries are `Adafruit_GC9A01A` for Arduino and the Pillow-based `Adafruit_CircuitPython_RGB_Display` for Linux; hardware SPI is strongly recommended.
  - Two displays can share SCK/MOSI with separate CS lines on one RP2040 ([Instructables](https://www.instructables.com/RP2040-2x-GC9A01-Display-on-Shared-SPI)).
  - A Pico project claims 60 fps pupil tracking using partial-window updates, without DMA ([RoboEyes](https://matsrobot.github.io/Robots-Blinking-Eyes-using-GC9A01-display)). A Pico fills a full ILI9341 screen at ≈46 fps with 62.5 MHz SPI ([Arduino forum](https://forum.arduino.cc/t/tft_espi-support-for-raspberry-pi-pico-added/702551)).
  - Render the eyes on a Pico 2 core or a separate RP2040 so the Pi stays free for vision (unverified).
- **WS2812:**
  - rpi_ws281x support for the Pi 5 is labelled experimental ([wiki](https://github.com/jgarff/rpi_ws281x/wiki/Raspberry-Pi-5-Support)).
  - Adafruit's PIO-based Pi 5 NeoPixel driver is at 1.0.0rc2 (Jan 2025, pre-release) ([PyPI](https://pypi.org/project/Adafruit-Blinka-Raspberry-Pi5-Neopixel/)). Userspace PIO on the Pi 5 goes through [PIOLib](https://www.raspberrypi.com/news/piolib-a-userspace-library-for-pio-control/).
  - Driving them from the Pico's PIO is simpler. 5 V LEDs may need a 3.3→5 V level shifter (unverified).
- **Audio:**
  - [MAX98357A](https://www.adafruit.com/product/3006) ($5.95): mono I2S, 3.2 W into 4 Ω or 1.8 W into 8 Ω at 5 V, runs on 2.7–5.5 V, 3–15 dB gain, no MCLK needed.
  - Setup on the Pi: comment out `dtparam=audio=on`, add `dtoverlay=max98357a`, and wire BCLK to GPIO18, LRCLK to GPIO19 and DIN to GPIO21 ([Adafruit](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-usage)).
  - One Pi 5 user on Bookworm had to edit the config by hand ([issue #359](https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/issues/359)).
- **Style references:**
  - [Reachy Mini](https://huggingface.co/blog/reachy-mini) (Pollen Robotics/Hugging Face): open-source, ~28 cm tall, 9 Dynamixel servos ([Seeed wiki](https://wiki.seeedstudio.com/reachymini_platforms_reachy_mini_hardware/)). Six XL330s drive a Stewart-platform head, an XC330 turns the body and two XL330s move the antennas ([motor-controller repo](https://awesome.ecosyste.ms/projects/github.com%2Fpollen-robotics%2Freachy-mini-motor-controller)). The antennas and rotating body carry most of its expression. It launched in Jul 2025 at $299/$449 ([TechCrunch](https://techcrunch.com/2025/07/09/hugging-face-opens-up-orders-for-its-reachy-mini-desktop-robots)); later listings are higher, so verify.
  - [Stack-chan](https://github.com/stack-chan/stack-chan): Apache-2.0 M5Stack robot with a face on screen and SG90 pan/tilt in community builds. M5Stack's official version was crowdfunded in Jan 2026 ([CNX](https://www.cnx-software.com/2026/01/13/m5stack-stackchan-is-a-cute-open-source-ai-desktop-robot/)).
  - [Coglet](https://www.hackster.io/news/will-cogley-s-coglet-is-a-3d-printable-expressive-twin-camera-companion-bot-5cc02a04b718) (Will Cogley): open-source, 3D-printable, twin-camera, Raspberry Pi + ESP32, programmed in Python.
  - [TN-24](https://www.hackster.io/tech_nickk/tn-24-v2-0-cute-desktop-companion-robot-44a472): small printed companion with OLED eyes.
  - Design cues (unverified): big round eyes, soft shells, eased motion and short chirps. Hide the muzzle in a "mouth" rather than a gun-like barrel.

## Open questions / verify on hardware

- Measure the chosen brand's pellets (mass and L×W×T with spread), and check for coating dust or tack after 100 feed cycles.
- On your STS3215 units, measure:
  - the real deadband (register 26/27 default of 1 vs ~10 counts measured)
  - backlash under your preload
  - repeatability over 100 re-aims
  - whether setting 26/27 to 0 causes hunting or buzz
- Does launch recoil rotate the turret inside the backlash zone before the pellet exits? Check with slow-motion video.
- Measure shot-to-shot σ(v) of the cam plunger over 50+ shots; the target is ≤1–2 %. Track drift with temperature and with hours spent cocked (creep).
- Tumbling drag at 2 m (calc; Cd ≈1 is unverified): ~3 mN on a 1.4–2 g pellet at 7 m/s means 1.5–2 m/s² of deceleration. Depending on orientation that could move the impact by ~1–2 cm, so test whether a guided barrel gives a consistent orientation.
- Range estimation must reach ≈±3 % at 2 m; this belongs to the vision research.
- Test FFC service-loop life over thousands of ±180° sweeps, and slip-ring integrity on the 1 Mbps servo bus if you use one.
- Check that the worm stays self-locked under spring load plus vibration, and how much side load the N20 output shaft tolerates (unverified).
- Measure the frame rate of two GC9A01 eyes on a Pico 2 that is also running safety I/O.
- Food safety of printed parts in the pellet path, and the choking/aspiration risk of firing food at a mouth: keep kinetic energy below 0.08 J and restrict use to adults (unverified).
- Budget: compare Waveshare's $110 pan-tilt kit against a DIY build (2× STS3215 at ≈$34–44 plus belts and bearings) within the $250 limit.
