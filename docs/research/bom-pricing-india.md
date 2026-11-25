# BOM Pricing (India)

Last researched: 2026-11-25 (prices change often; verify before buying)

## Totals

This covers everything except the main compute board and camera. Unit prices are what you pay, in ₹ including 18 % GST, rounded to whole rupees. Evelta and ElectronicsComp (EC) list prices without GST, so I multiplied those by 1.18. Robu and Amazon.in prices already include GST.

| | Recommended | Cheapest viable |
|---|---|---|
| Turret choice | A1: 2× ST3215 12 V + adapter, plus a 3:1 GT2 belt stage | A3: 2× NEMA17 (40 mm) + TMC2209 + 3:1 GT2 belt stage |
| A. Turret actuators | 5,849 | 2,378 |
| B. Launcher & feed | 2,398 | 2,231 |
| C. Pan bearing | 499 | 329 |
| D. Safety | 497 | 401 |
| E. Power | 870 | 634 |
| F. Character | 1,396 | 366 |
| G. Hardware | 2,260 | 1,797 |
| **Robot parts (A–G)** | **13,769** | **8,136** |
| H. Filament, 2 × 1 kg (only part of it ends up in the robot) | 1,661 | 1,568 |
| Shipping, 3–4 orders (estimate) | 300 | 250 |
| **Total without compute board + camera** | **₹15,730 (≈ US$179)** | **₹9,954 (≈ US$113)** |
| Left for compute board + camera under the ₹21,000 cap | ₹5,270 | ₹11,046 |
| I. Caliper (tool, outside the cap) | 699 | 699 |

- **Exchange rate:** I assumed ₹88 per US$ (estimate; the rate was not checked today). At that rate US$250 is ₹22,000, so the brief's ₹21,000 cap is the limit that binds.
- **Turret choice:** the recommended build follows the A1 preference. Swapping in A3 with 34 mm motors (₹2,914 including homing switches) brings the total down to ₹12,795, and pointing is tighter because a belt-driven stepper has almost no play (see A).
- **Cap risk:** if the compute board plus camera cost more than about ₹5.3k, the recommended build goes over ₹21,000. In that case use A3 and the cuts in "Where to cut cost".
- **What the cheapest build changes:** 40 mm stepper motors (A3); one spring set; the 3" lazy susan; the Amazon covered toggle and the Yokins e-stop; an inline glass-fuse holder; two WS2812 jewels instead of the GC9A01 eyes; the EC 0.5 W speaker; Robu 25-piece M3 packs instead of the M3 kit; no F-F jumpers; WOL3D PLA.
- **How the prices were gathered:** the web-search quota was already used up, so every price comes from reading seller pages directly, Robu and Amazon.in in a browser and Evelta and EC by fetch. Robocraze, ThinkRobotics, Quartz and Hubtronics were checked only for the scarce parts (bus servos and worm motors). Probots' search could not be reached and Flipkart was not checked.

## A. Turret actuators (three alternative sets)

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| A1 bus servo | Feetech ST3215-C018: 12 V, 30 kg·cm, 1:345, 12-bit magnetic encoder | Evelta | [link](https://evelta.com/st3215-c018-12v-30kg-cm-1-345-dual-shaft-ttl-serial-servo-metal-gears-magnetic-encoder/) | 2,419 | 2 | 4,838 | 63 in stock; ships from Mumbai within 24 h. Stalls at 2.7 A. Runs straight from the 12 V rail. Amazon.in sells only imported packs, at ₹4,400–5,800 per servo |
| A1 bus servo, 7.4 V | STS3215-C001 / C044 / C046 | Evelta | [link](https://evelta.com/st3215-7-4v-19kg-1-345-gear-dual-axis-ttl-string-servo-motor/) | 2,224 | (2) | (4,448) | **Sold out (all three).** Robu's Waveshare 7.4 V (₹2,159) and 12 V (₹2,571) versions are sold out too. Amazon.in import with bracket: ₹6,190. Waveshare direct: US$16.99–21.99, plus courier and about 30–40 % duty, 1–3 weeks (estimate) |
| A1 bus adapter | Waveshare Serial Bus Servo Driver Board (ST/SC servos, 9–12.6 V, 5.5 × 2.1 jack) | Robu | [link](https://robu.in/product/waveshare-serial-bus-servo-driver-board-integrates-servo-power-supply-and-control-circuit-applicable-for-st-sc-series-serial-bus-servos/) | 475 | 1 | 475 | In stock. Robu's page lists only a UART, so check that it is the USB-C "Bus Servo Adapter (A)" revision ([Waveshare](https://www.waveshare.com/bus-servo-adapter-a.htm), US$4.99). Alternatives: Evelta ₹543 (1 left), SmartElex ₹509 (Robu), Feetech FE-URT-2 ₹1,286 (Evelta) |
| **A1 set (12 V)** | | | | | | **5,313** | 0.088° per count. A bench test measured about 0.9° of backlash (mechanics-actuators.md), so 0.3° needs the belt stage below. A 7.4 V set would be ₹5,010 including a 7.4 V buck, but it is out of stock |
| A1 belt stage (recommended build) | 2× GT2 60T + 2× 200 mm closed belts (the A3 rows); print the 20T onto the servo horn | EC | see A3 rows | — | 1 | 536 | mechanics-actuators.md: a 3:1 stage cuts play and deadband to about 0.2–0.3° at the turret |
| A2 hobby servo | TowerPro MG996R (generic, metal gear) | EC | [link](https://www.electronicscomp.com/mg996r-metal-gear-servo-motor) | 247 | 2 | 494 | 246 in stock; ₹359 at [Robu](https://robu.in/product/towerpro-mg996r-digital-high-torque-servo-motor/). DS3218: Robu Pro-Range ₹1,519 (sold out); DSServo DS3218MG ₹1,899 on Amazon.in |
| A2 PWM board | PCA9685, 16-channel, 12-bit, I2C | Robu | [link](https://robu.in/product/16-channel-12-bit-pwmservo-driver-i2c-interface-pca9685-arduino-raspberry-pi/) | 249 | 1 | 249 | In stock; ₹282 at [EC](https://www.electronicscomp.com/16-channel-pca9685-pwm-servo-controller-india) |
| **A2 set** | | | | | | **743** | Potentiometer feedback and deadband: it will not hold 0.1–0.3°. With DS3218s the set costs about ₹4,047 |
| A3 stepper | NEMA17 KS42STH34-1504A: 34 mm, 2.2 kg·cm, 1.5 A | EC | [link](https://www.electronicscomp.com/ks42sth34-1504a-nema17-22kg-cm-stepper-motor-d-type-shaft) | 712 | 2 | 1,424 | No 20–25 mm pancake motor found at these sellers. Cheaper and 6 mm longer: [42HS40-1504](https://www.electronicscomp.com/42hs40-1504-nema17-42-kg-cm-stepper-motor-d-type-shaft), 40 mm, 4.2 kg·cm, ₹444 (cheapest build) |
| A3 driver | Makerbase MKS TMC2209 V2.0 with heatsink | EC | [link](https://www.electronicscomp.com/makerbase-mks-tmc2209-v20-stepper-motor-driver-with-heatsink) | 414 | 2 | 828 | Also available: TMC2209 V3.0 ₹446, BTT V1.3 ₹552 |
| A3 pulley 20T | GT2 20T, 5 mm bore, 6 mm belt | EC | [link](https://www.electronicscomp.com/gt2-6mm-belt-width-20-teeth-5mm-bore-timing-pulley) | 47 | 2 | 94 | |
| A3 pulley 60T | GT2 60T aluminium, 5 mm bore | EC | [link](https://www.electronicscomp.com/gt2-6mm-belt-width-60-teeth-5mm-bore-aluminium-timing-pulley) | 205 | 2 | 410 | The 8 mm bore version is ₹218. Or print it on the X1C |
| A3 belt | GT2 6 mm closed loop, 200 mm | EC | [link](https://www.electronicscomp.com/gt2-timing-belt-200mm-long-and-6mm-width-closed-loop-rubber-belt-for-3d-printer) | 63 | 2 | 126 | For 20T to 60T, a 200 mm belt gives about 59 mm between centres and a 280 mm belt (₹51) about 99 mm (estimate) |
| **A3 set (34 mm motors)** | | | | | | **2,882** | 1.8° / 16 microsteps / 3 = 0.0375° per microstep. With 40 mm motors the set is ₹2,346. Either way, add 2 homing switches (₹32, KW4 in B) |

## B. Launcher & feed

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Worm-gear motor | JGY370-12-95: 12 V, 95 rpm no-load, rated 2.0 kg·cm at 70 rpm, self-locking | Robu | [link](https://robu.in/product/solid-shaft-jgy370-dc12v-95rpm-min-high-torque-self-locking-strong-wheel-tturbine-worm-reduction-motor/) | 599 | 2 | 1,198 | In stock. Meets the ≥2 kg·cm cam torque in mechanics-actuators.md. The 23 rpm version is sold out; 6 rpm is too slow. Much bigger and heavier than an N20 (estimate ~150 g) |
| Worm motor, compact alternative | 1218-N20 worm: 6 V, 34 rpm, self-locking, 3 mm D shaft | Amazon.in | [link](https://www.amazon.in/dp/B0GQHNSBJB) | 929 | (2) | (1,858) | No reviews. Same price at 68 rpm ([link](https://www.amazon.in/dp/B0GQHTJDKT)). Not stocked by Robu, Robocraze, Quartz, EC or Evelta. Probably too little torque for the cam (mechanics-actuators.md) |
| Motor driver | TB6612FNG dual H-bridge module | EC | [link](https://www.electronicscomp.com/tb6612fng-dual-motor-driver-module-1a-for-arduino) | 235 | 1 | 235 | Takes a 12 V motor supply. The [DRV8833](https://www.electronicscomp.com/drv8833-2-channel-dc-motor-driver) (₹55) tops out at 10.8 V, so it only suits a 6 V N20 |
| Micro servo | TowerPro MG90S, metal gear, 180° | EC | [link](https://www.electronicscomp.com/mg90s-metal-gear-servo-motor) | 117 | 2 | 234 | |
| Spring, cut to length | 0.6 mm wire, 5 mm and 8 mm OD, 150 mm long (set of 2) | Amazon.in | [link](https://www.amazon.in/dp/B0HRSWFMH1) | 165 | 1 | 165 | No reviews. Cut to length. The 5 mm OD spring comes near the ~0.85 N/mm target at about 16 coils (estimate) |
| Spring, soft | EasyMech stainless: 0.5 mm wire, OD 6 mm, 40 mm long (4 pcs) | Robu | [link](https://robu.in/product/easymech-0-5mm-ss-heatbed-spacer-compression-spring-for-3d-printer-od-6mm-x-id-5mm-x-l-40mm-4-pcs/) | 167 | 1 | 167 | In stock, about 0.2 N/mm (estimate). Skip Robu's [1 mm × OD 7.4](https://robu.in/product/easymech-1-mm-ss-heatbed-spacer-compression-spring-for-3d-printer-od-7-4mm-x-id-5-4mm-x-l-40mm-4-pcs/) version (₹149): at about 3 N/mm (estimate) it stores far more energy than the 0.04 J exit cap allows (safety-standards.md). Amazon's 300-piece kit (₹773) has only 0.28–0.69 mm wire, ≤ 25 mm long |
| Small bearing | 623ZZ, 3 × 10 × 4 mm | EC | [link](https://www.electronicscomp.com/radial-ball-bearing-623zz-for-3d-printer-robot) | 22 | 4 | 88 | 446 in stock. MR63ZZ is only on Amazon.in (4 pcs ₹399) |
| Bearing | 608ZZ, 8 × 22 × 7 mm | EC | [link](https://www.electronicscomp.com/radial-ball-bearing-608zz-for-3d-printer-robot) | 22 | 4 | 88 | 519 in stock |
| Lever microswitch | KW4-Z2F100 SPDT, short lever | Robu | [link](https://robu.in/product/kw4-z2f100-spdt-short-lever-micro-switch-5a1n/) | 16 | 3 | 48 | In stock |
| IR pairs | 5 mm IR LED + photodiode, 5 pairs | Amazon.in | [link](https://www.amazon.in/dp/B0HCPJVB3Z) | 175 | 1 | 175 | No reviews. Bare photodiodes are fast enough for the chronograph. Adafruit break-beam modules are slower (< 2 ms, mechanics-actuators.md) and cost ₹1,481 ([link](https://www.amazon.in/dp/B01BU6YBWU)). Also: Evelta IR333C-A 5 mm IR LED ₹11; [TCRT5000 module](https://www.electronicscomp.com/tcrt5000-ir-reflex-tracking-sensor-module) ₹33 at EC (reflective, for chamber sensing only) |
| **B subtotal** | | | | | | **2,398** | The cheapest build drops the 0.5 mm spring pack: ₹2,231 |

## C. Pan bearing

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Pan bearing (recommended build) | 6806ZZ thin-section, 30 × 42 × 7 mm, 4-pack (use 2) | Amazon.in | [link](https://www.amazon.in/dp/B0HCRDJ6CW) | 499 | 1 | 499 | No reviews. The hollow 30 mm bore takes the camera cable. mechanics-actuators.md advises against lazy susans because of side play. Not stocked by Robu or EC; a single SHUSTER 6806ZZ is ₹900 |
| Lazy susan (cheapest build) | Square turntable bearing, 3" | Amazon.in | [link](https://www.amazon.in/dp/B0BY9FYDBD) | 329 | (1) | (329) | 4.3★ (195 ratings, all sizes). The 4" is ₹399 ([link](https://www.amazon.in/dp/B0BY9HWC1M)). Not stocked by Robu or EC. Stamped races have side and axial play, so preload them |

## D. Safety

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Arm/disarm switch | ASW-07D lit toggle with flip-up safety cover, yellow | Robu | [link](https://robu.in/product/toggle-switch-with-light-rocker-asw-07d-with-waterproof-cover-yellow/) | 215 | 1 | 215 | In stock (the red one is sold out). The red Amazon equivalent is ₹211 ([link](https://www.amazon.in/dp/B0DNMSQZ4F)), used in the cheapest build. Rated 12 V 20 A |
| E-stop | LAY37 22 mm mushroom: latching, twist to release, DPST | EC | [link](https://www.electronicscomp.com/ac-660v-10a-lay37-dpst-emergency-stop-push-button-switch) | 282 | 1 | 282 | 17 in stock. The listing gives a 23 mm neck, so check the panel hole. Genuine Schneider XB5AS542N: ₹530 ([link](https://www.amazon.in/dp/B09N7JW3RL)). Yokins EB2M: ₹190 ([link](https://www.amazon.in/dp/B0CZXPW79W), cheapest build). Robu has only 16 mm Lanboo (from ₹374) and a 22 mm Onpow (₹1,233) |
| **D subtotal** | | | | | | **497** | Cheapest build: ₹401 |

## E. Power

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| 12 V adapter | Orange 12 V 5 A 60 W SMPS | Robu | [link](https://robu.in/product/orange-ac-100-240v-to-dc-12v-5a-60w-power-adapter/) | 425 | 1 | 425 | In stock; check that the plug is 5.5 × 2.1 mm. EC's [12 V 5 A](https://www.electronicscomp.com/12v-5a-dc-power-adapter-india) is ₹438 (1,343 in stock). The 12 V 3 A (EC ₹372) is too tight, because two bus servos stall at 2.7 A each |
| Panel jack | 5.5 × 2.1 mm panel-mount DC jack with nut | EC | [link](https://www.electronicscomp.com/2.1-x-5.5mm-dc-power-jack-socket-female-panel-mount) | 14 | 1 | 14 | |
| 12 V → 5 V 5 A | XY-3606 synchronous buck: 9–36 V in, 5 V 5 A out | Robu | [link](https://robu.in/product/24v-12v-to-5v-5a-power-module-dc-dc-xy-3606-power-converter/) | 139 | 1 | 139 | In stock. XL4015 5 A modules (EC ₹87) are a poor fit for a Pi 5: they are non-synchronous and run hot above about 3 A (estimate). The better-quality option is a potted 12–24 V → 5 V 10 A converter, ₹880 ([link](https://www.amazon.in/dp/B0BB7T4KF9), 4.5★). On a 5 V feed without USB-PD, a Pi 5 limits USB to 600 mA unless `usb_max_current_enable=1` is set (unverified here) |
| 12 V → 7.4 V | XL4015 5 A adjustable CC/CV | EC | [link](https://www.electronicscomp.com/xl4015-5a-lithium-charger-dc-dc-step-down-power-supply-module-india) | 87 | 0 | 0 | Only needed with 7.4 V servos |
| Fuse | Waterproof inline mini-blade holder + 8 fuses (5–40 A) | Amazon.in | [link](https://www.amazon.in/dp/B0B65RFXFX) | 292 | 1 | 292 | 3.9★. Fit the 5 A fuse. The cheapest build uses EC's [inline 20 mm glass-fuse holder](https://www.electronicscomp.com/mx-in-line-fuse-holder-4-amp-20mm-5mm-mx-1697) (₹46) plus a 5 A fuse (about ₹10, estimate) |
| **E subtotal** | | | | | | **870** | Cheapest build: ₹634 |

## F. Character

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Round TFT eyes | GoldenMorning GC9A01 1.28" round 240 × 240 SPI | Robu | [link](https://robu.in/product/goldenmorning-gc9a01-7p-240x240-spi-1-28-inch-round-display-module/) | 494 | 2 | 988 | In stock. Amazon.in sells them for ₹599–749; EC has only the Waveshare touch version (₹1,612) |
| I2S amplifier | MAX98357A breakout, headers unsoldered | Robu | [link](https://robu.in/product/bgamax98357-i2s-amplifier-breakout-interface-decoder-module-without-soldering/) | 179 | 1 | 179 | In stock. SmartElex ₹194; Adafruit ₹757 (sold out) |
| Speaker | 40 mm, 4 Ω, 3 W | Amazon.in | [link](https://www.amazon.in/dp/B0DNMY65PG) | 229 | 1 | 229 | 3.2★. Robu has the DFRobot FIT0502 (3 W, 8 Ω, enclosed) for ₹519. EC's [4 Ω 0.5 W](https://www.electronicscomp.com/4-ohm-speaker-0.5-watt) (₹53) goes in the cheapest build; limit the volume in software |
| Eye alternative | WS2812 7-LED jewel, 23 mm | Robu | [link](https://robu.in/product/7-bit-ws2812-5050-rgb-led-built-in-full-color-driving-lights-od23mm/) | 67 | (2) | (134) | In stock; replaces the GC9A01s in the cheapest build. Robu's 8-LED ring (₹49) is sold out. Also: EC [16-LED ring](https://www.electronicscomp.com/16bit-ws2812b-5050-rgb-led-built-in-full-color-driving-lights-circular-development-board) ₹92; Amazon.in 8-LED stick ₹118 |
| **F subtotal** | | | | | | **1,396** | Cheapest build: ₹366 |

## G. Hardware

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Heat-set inserts | M3 × 4 mm brass, 25 pcs | Robu | [link](https://robu.in/product/m3-x-4-mm-brass-heat-set-knurl-threaded-round-insert-nut-25-pcs/) | 91 | 4 | 364 | In stock. Amazon.in: 50 pcs for ₹289 |
| M3 screws | M3 socket-head set: 6/8/10/12/15/20 mm × 10 each, plus 60 nuts and washers | Amazon.in | [link](https://www.amazon.in/dp/B083Y4JPZJ) | 544 | 1 | 544 | 4.1★. Cheapest build: Robu EasyMech M3 cheese-head screws with nuts and washers, 25 each of [M3 × 6](https://robu.in/product/easymech-m3-x-6mm-chhd-bolt-nut-and-washer-set-25-pcs/) and [M3 × 10](https://robu.in/product/easymech-m3-x-10mm-chhd-bolt-nut-and-washer-set-25-pcs/), ₹67 + ₹78 |
| M2.5 screws | M2.5 × 10 mm stainless bolt, nut and washer set | Amazon.in | [link](https://www.amazon.in/dp/B07GKWFQSV) | 285 | 1 | 285 | 3.6★. For mounting boards |
| JST-XH kit | 560-piece XH 2.54 mm kit | Robu | [link](https://robu.in/product/560pcs-xh2-54mm-terminal-block-kit-jst-xh/) | 389 | 1 | 389 | In stock. Needs a crimper (see I) |
| Wire, 22 AWG | Silicone, 2 m red + 2 m black | EC | [red](https://www.electronicscomp.com/high-quality-ultra-flexible-22awg-silicone-wire-2m-red), [black](https://www.electronicscomp.com/high-quality-ultra-flexible-22awg-silicone-wire-2m-black) | 89 / 85 | 1 + 1 | 174 | Robu's 22 AWG silicone wire is mostly sold out |
| Wire, 26 AWG | Silicone, 3 m red + 3 m black | EC | [link](https://www.electronicscomp.com/high-quality-ultra-flexible-26awg-silicone-wire-3m-black-3m-red) | 120 | 1 | 120 | |
| Perfboard | General-purpose PCB, 4 × 4" | EC | [link](https://www.electronicscomp.com/general-purpose-pcb-4x4-inches) | 45 | 2 | 90 | |
| MOSFET | IRLZ44N, TO-220 | Robu | [link](https://robu.in/product/irlz44n/) | 44 | 3 | 132 | Not rated at a 3.3 V gate; fine for loads under about 1 A (estimate). AO3400 (SOT-23) is rated at 2.5 V and costs ₹3 at Robu, if you can solder SMD |
| Schottky diode | 1N5819 | EC | [link](https://www.electronicscomp.com/1n5419-schottky-barrier-diode) | 6 | 5 | 30 | |
| Jumper wires | 20 cm Dupont, 40 M-F + 40 F-F | EC | [M-F](https://www.electronicscomp.com/male-to-female-jumper-wires-20cm-40-pieces-pack), [F-F](https://www.electronicscomp.com/20cm-dupont-wire-color-jumper-cable-2.54mm-1p-1p-female-to-female-40-pieces-pack) | 68 / 64 | 1 + 1 | 132 | Cheapest build: M-F only |
| **G subtotal** | | | | | | **2,260** | Cheapest build: ₹1,797 |

## H. Materials (filament)

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| PETG, gum-contact parts | Haiteng PETG Clear, 1 kg, 1.75 mm | Amazon.in | [link](https://www.amazon.in/dp/B0DF7FHRDS) | 869 | 1 | 869 | 4.5★ (22 ratings), in stock. Uncoloured filament is the safer pick, but printed PETG is not food-certified, so keep gum-path parts smooth and washable. Alternatives: Numakers PETG ₹899; Robu Sunlu PETG ₹899–999; Robu Pro-Range PETG ₹780 (coloured only) |
| PLA+, body | Gratkit PLA+ 1 kg, black (pick your colour) | Amazon.in | [link](https://www.amazon.in/dp/B0BB9YVMHY) | 792 | 1 | 792 | 4.4★. Cheapest build: [WOL3D PLA PRO+](https://www.amazon.in/dp/B07HF98DWB), ₹699 (3.5★). Also Numakers PLA+ ₹949, eSUN PLA ₹900, Robu Sunlu PLA ₹899–1,099. Print cams, sears and slides in PETG, not PLA |
| **H subtotal** | | | | | | **1,661** | Cheapest build: ₹1,568 |

## I. Tools (outside the cap)

| item | chosen product | seller | link | unit ₹ | qty | subtotal ₹ | stock / notes |
|---|---|---|---|---|---|---|---|
| Digital caliper | Aurdeayi 150 mm, stainless steel, 0.01 mm resolution | Amazon.in | [link](https://www.amazon.in/dp/B0D2386QN9) | 699 | 1 | 699 | 4.0★ (923 ratings), in stock. The ₹399–425 calipers (Vinabo, SKADIOO) are plastic and accurate to only ±0.2 mm. Robu sells only Freemans, at ₹2,349 |
| Crimper (optional) | SN-58B ratcheting crimper | Amazon.in | [link](https://www.amazon.in/dp/B0FSDW87CS) | 949 | 0 | — | Only needed for the JST-XH kit. Rated 24–16 AWG, so not for 26 AWG; an SN-28B costs ₹2,846 or more |

## Where to cut cost

- **Turret:** swap the A1 servos and belt stage for A3 steppers. That saves ₹2,935 with 34 mm motors or ₹3,471 with 40 mm motors. Pointing also gets tighter: A3 steps 0.0375° per microstep with almost no play, while A1 through the belt steps 0.029° per count but keeps about 0.2–0.3° of play and deadband.
- **Pulleys:** print the 60T pulleys on the X1C, for A1's belt stage or for A3. Saves ₹410.
- **Bus adapter:** skip it. A Pico or ESP32 UART plus a 74HC126 buffer, or a resistor-and-diode half-duplex circuit, can drive the ST3215 bus. Saves ₹475 (the buffer is not priced).
- **Eyes:** use two WS2812 jewels instead of two GC9A01s. Saves ₹854.
- **Worm motors:** buy one instead of two if the second is only a spare. Saves ₹599.
- **JST-XH:** if there is no crimper, skip the kit and solder with heat-shrink or use Dupont leads. Saves ₹389, plus the ₹949+ crimper.
- **Fuse:** use the inline glass-fuse holder instead of the blade kit. Saves about ₹236.
- **Screws:** use Robu's 25-piece M3 packs instead of the Amazon kit. Saves ₹399.
- **MOSFETs:** use AO3400 instead of IRLZ44N if you can solder SMD. Saves about ₹120.
- **Shipping:** buy the servos from Evelta and put everything else into one Robu order and one EC order, plus the Amazon-only items. Amazon ships free on Amazon-fulfilled orders over ₹499 (shown on the listings).
- **Coupon:** EC showed a 10 % prepaid coupon (GET10) on 2026-11-25 (unverified at checkout).

## Open questions

1. **Compute board:** if it is a Pi 5, is the XY-3606 enough, or should the Pi get its own official 27 W USB-C supply (₹1,345 at Robu)? The cap also depends on this, since the recommended build leaves only ₹5.3k for the compute board and camera.
2. **Servo voltage:** is 12 V acceptable? The 12 V ST3215 is the only STS3215 variant in stock at a normal price at the sellers checked.
3. **A1 or A3?** The A1 servos need the belt stage and a preload to reach 0.3°, while A3 costs about half as much. Which matters more: simple wiring with absolute encoders, or cost and resolution?
4. **Cocking motor position:** does it ride on the tilt stage? If so, check the JGY370's weight (estimate ~150 g) against the tilt torque, or accept the weaker N20.
5. **Second worm motor:** is it a spare or a second mechanism?
6. **Pellets:** the pellet brand and size, measured with the caliper, decide the bore, the spring and the spacing of the IR gates.
7. **Crimper:** does the builder own one?
8. **Pico or ESP32?** The choice changes how the half-duplex servo bus and the TMC2209 UART are wired.
9. **Food safety:** should the gum-path parts be lined with a food-safe PET or PTFE tube instead of bare printed PETG?
