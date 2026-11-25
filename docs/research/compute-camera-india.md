# Compute & Camera Options (India)

Last researched: 2026-11-25 (prices change often; verify before buying)

Method: prices and stock were read directly from seller pages on 2026-11-25. Web search was unavailable during this pass, so some listings may be missing.
- Price labels: "incl." means the seller shows the price with GST. "+GST" means the seller lists it without GST; the 18 % GST total is in brackets (calc). "GST n/s" means the page does not say.
- Marks: (estimate) = judgement from indirect data; (calc) = my own arithmetic; (unverified) = no source found.
- Robu and Silverline are on Raspberry Pi's approved-reseller list for India ([list](https://www.raspberrypi.com/resellers/)).

## Recommendation

| | Cheapest combo likely to meet ≥ 15 FPS | Step-up |
|---|---|---|
| Board | Raspberry Pi 5 **1 GB**: ₹5,044–5,517 | Raspberry Pi 5 **2 GB**: ₹9,039–9,109 |
| Camera | OV5647 5 MP CSI clone: ₹267–319 | Camera Module 3 **standard** (not Wide): ₹3,068–3,299 |
| Accessories | 27 W PSU, Active Cooler, 32 GB SanDisk A1 card, 22→15-pin camera cable | Same, with a 300 mm cable |
| **Total** | **₹8,939** from one seller (Robocraze); ₹7,730 mixing sellers (calc) | **₹16,167**, mostly Robu (calc) |
| Share of the ₹21,000 budget | 43 % | 77 % |
| Stock on 25 Nov | 1 GB **out of stock** at Robu, Robocraze and Silverline | 2 GB **out of stock** at all 5 sellers checked |

- **To buy today:** only the Pi 5 4 GB is in stock (Robocraze ₹13,455, Robu ₹13,459). With the OV5647 kit that totals ₹17,350, or 83 % of the budget (calc).
  - UK resellers restocked every Pi 5 size except 1 GB on 19 Nov 2026 ([forum](https://forums.raspberrypi.com/viewtopic.php?p=2393245)). Set stock alerts for the 1 GB and 2 GB first.
- **Why the Pi 5:** it is the only Cortex-A76 board that Indian shops stock at a sane price; `pip install mediapipe` (1.2.3) has an official ARM64 wheel; CSI cameras through libcamera/Picamera2 give low latency, and the ISP crops and scales without using the CPU. A Pi 4 4 GB costs more than a Pi 5 1 GB and is about half as fast per core.
- **Expected speed:** about **12–25 FPS** per process for FaceLandmarker with blendshapes (one face, 640×480) (estimate; nobody has published a Pi 5 benchmark, and the lower half of the range is more likely).
  - MediaPipe uses one inference thread on Linux, so 2–3 worker processes on alternating frames should reach about **25–40 FPS** (estimate), but each frame's latency stays the same. Benchmark this in week one.
- **Why the OV5647:** it is the cheapest option; its ≈54° view makes a face at 2 m bigger than the 62–66° official cameras do; its 1296×972 mode at about 46 fps leaves room for a 2× crop (mode list unverified). Step up to Camera Module 3 for autofocus, HDR, better low-light images and more pixels for aiming.

## 1. Board prices in India and official USD prices

**Official Raspberry Pi list prices (USD) through the 2025–2026 memory-driven rises**

| Model | Before 1 Dec 2025 | 1 Dec 2025 | 2 Feb 2026 | 1 Apr 2026 | 1 Oct 2026 | **Now** |
|---|---|---|---|---|---|---|
| Pi 5 1 GB | – | $45 (launch) | $45 | $45 | $45 | **$45** |
| Pi 5 2 GB | $50 | $55 | $65 | $65 | $77.50 | **$77.50** |
| Pi 5 4 GB | $60 | $70 | $85 | $110 | $110 | **$110** (calc) |
| Pi 5 8 GB | $80 | $95 | $125 | $175 | $175 | **$175** (calc) |
| Pi 5 16 GB | $120 | $145 | $205 | $305 | $305 | **$385** (from 2 Nov) |
| Pi 4 1 GB | $35 | $35 | $35 | $35 | $35 | **$35** |
| Pi 4 2 GB | $45 | $45 | $55 | $55 | $67.50 | **$67.50** |
| Pi 4 3 GB | – | – | – | $83.75 (launch) | $83.75 | **$83.75** |
| Pi 4 4 GB | $55 | $60 | $75 | $100 | $100 | **$100** (calc) |
| Zero 2 W | $15 | $15 | $15 | $15 | $15 | **$15** |

Sources: [1 Dec 2025](https://www.raspberrypi.com/news/1gb-raspberry-pi-5-now-available-at-45-and-memory-driven-price-rises/) (full table, 1 GB launch); [2 Feb 2026](https://www.raspberrypi.com/news/more-memory-driven-price-rises/) (+$10, $15, $30, $60 for 2, 4, 8, 16 GB); [1 Apr 2026](https://www.raspberrypi.com/news/a-new-3gb-raspberry-pi-4-for-83-75-and-more-memory-driven-price-increases/) (+$25 for 4 GB, +$50 for 8 GB, +$100 for 16 GB; new 3 GB Pi 4); [1 Oct 2026](https://www.raspberrypi.com/news/price-increases-for-2gb-raspberry-pi-4-and-raspberry-pi-5/) (+$12.50 for 2 GB); [2 Nov 2026](https://www.raspberrypi.com/news/price-rises-for-some-16gb-raspberry-pi-products/) (+$80 for the Pi 5 16 GB).

Notes: the February and April posts list only the increases, so the "Now" prices marked (calc) are my sums. The 1 GB, Zero and older models were exempt from every rise. The Pi 5 product page still showed $305 for the 16 GB on 25 Nov, which is out of date.

**Indian sellers (25 Nov 2026)**

| Item | Seller | Price ₹ | Stock | Link | Notes |
|---|---|---|---|---|---|
| Pi 5 1 GB | Robocraze | 5,044 incl. | Out | [link](https://robocraze.com/products/official-raspberry-pi-5-model-b-1gb-ram) | Listed Feb 2026 |
| Pi 5 1 GB | Robu | 5,449 incl. | Out | [link](https://robu.in/product/raspberry-pi-5-model-1gb-ram/) | Approved reseller |
| Pi 5 1 GB | Silverline | 4,675 +GST (5,517) | Out | [link](https://www.silverlineelectronics.in/products/raspberry-pi-5-model-b-1gb-ram-in-stock) | Approved reseller |
| Pi 5 2 GB | Silverline | 7,660 +GST (9,039) | Out | [link](https://www.silverlineelectronics.in/products/raspberry-pi-5-model-b-2gb-ram) | |
| Pi 5 2 GB | Robu | 9,109 incl. | Out | [link](https://robu.in/product/raspberry-pi-5-model-2gb/) | |
| Pi 5 2 GB | Robocraze | 7,869 incl. | Out | [link](https://robocraze.com/products/raspberry-pi-5-model-2gb-ram) | Probably the price before the October rise (unverified) |
| Pi 5 2 GB | ThinkRobotics / Quartz | 10,580 / 6,355 (GST n/s) | Out / Out | [TR](https://thinkrobotics.com/products/raspberry-pi-5), [Q](https://quartzcomponents.com/products/raspberry-pi-5-model-b-2-gb-ram) | Quartz price looks out of date |
| Pi 5 4 GB | Robocraze | 13,455 incl. | **In** | [link](https://robocraze.com/products/raspberry-pi-5-4gb) | |
| Pi 5 4 GB | Robu | 13,459 incl. | **In** | [link](https://robu.in/product/raspberry-pi-5-model-4gb/) | |
| Pi 5 4 GB | ThinkRobotics | 15,500 (GST n/s) | **In** | [link](https://thinkrobotics.com/products/raspberry-pi-5) | |
| Pi 5 4 GB | Silverline / Quartz | 11,360 +GST (13,405) / 11,200 | Out / Out | [S](https://www.silverlineelectronics.in/products/raspberry-pi-5-model-b-4gb-ram-in-stock), [Q](https://quartzcomponents.com/products/raspberry-pi-5-model-b-4-gb) | |
| Pi 4 2 GB | Robu / Silverline / Robocraze | 7,939 / 6,670 +GST (7,871) / 7,091 | Out (all) | [Robu](https://robu.in/product/raspberry-pi-4-model-b-with-2-gb-ram/) | |
| Pi 4 3 GB | Silverline / Robu | 8,099 +GST (9,557) / 9,599 | **In** / backorder | [S](https://www.silverlineelectronics.in/products/products-raspberry-pi-4-model-b-3gb) | New $83.75 model |
| Pi 4 4 GB | Quartz | 9,789 (GST n/s) | **In** | [link](https://quartzcomponents.com/products/raspberry-pi-4-model-b-4-gb-ram) | Cheapest Pi 4 4 GB found |
| Pi 4 4 GB | Silverline / Robu / Robocraze | 9,600 +GST (11,328) / 11,519 / 11,519 | **In** | [Robu](https://robu.in/product/raspberry-pi-4-model-b-with-4-gb-ram/) | |
| Zero 2 W | Silverline / Robocraze / Robu | 1,500 +GST (1,770) / 2,210 / 2,869 (with header) | Out (all) | [Robu](https://robu.in/product/raspberry-pi-zero-2-w-with-header/) | |
| Orange Pi 5 4 GB | None found | – | – | – | Not sold by Robu, Robocraze, Quartz, Evelta, ElectronicsComp or ThinkRobotics |
| Orange Pi 5 8 GB | Amazon.in (import) | 41,741 | Ships ~12 Dec | [link](https://www.amazon.in/dp/B0BN17PWWB) | Far above list price |
| Orange Pi Zero 3 1 GB / 1.5 GB | Amazon.in (import) | 9,960 / 9,524 | Ships ~12 Dec | [1 GB](https://www.amazon.in/dp/B0H2D9968G), [1.5 GB](https://www.amazon.in/dp/B0C9ZYFRMP) | Orange Pi Zero 2W not found anywhere |
| ROCK 5C Lite 2 GB / 4 GB | ThinkRobotics | 6,200 / 8,000 (GST n/s) | Out | [link](https://thinkrobotics.com/products/radxa-rock-5c) | Arace (Hong Kong): $34.90 / $44.90, also out ([link](https://arace.tech/products/radxa-rock-5c)) |
| ROCK 5C 2 GB (full RK3588S2) | Arace (import) | $69 | In | [link](https://arace.tech/products/radxa-rock-5c) | ThinkRobotics ₹8,850, out |
| Radxa ZERO 3W | ThinkRobotics / Arace | From 2,650 / from $20 | Out / In (import) | [TR](https://thinkrobotics.com/products/radxa-zero-3w), [Arace](https://arace.tech/products/radxa-zero-3w) | |

## 2. MediaPipe FaceLandmarker: install and speed

**Install**
- **ARM64 wheel exists:** `mediapipe` 1.2.3 (11 Nov 2026) ships one Linux ARM64 wheel, `py3-none-manylinux_2_28_aarch64` (40.7 MB), listed for Python 3.9–3.14 ([PyPI](https://pypi.org/project/mediapipe/)). So `pip install mediapipe` works on 64-bit Raspberry Pi OS Trixie (Python 3.13; needs 1.1.0 or newer, which added 3.13 and 3.14 ([releases](https://github.com/google-ai-edge/mediapipe/releases))), Bookworm (Python 3.11), Ubuntu 22.04/24.04 and Armbian on any ARM64 board with glibc 2.28 or newer. There is no wheel for 32-bit systems.
- **Gotcha, old guides:** versions 0.10.20 to 0.10.35 (May 2025 to Apr 2026) shipped **no** ARM64 wheels. The fix came with 1.0.0 in Jul 2026 ([#5965](https://github.com/google-ai-edge/mediapipe/issues/5965)). Guides written in that gap pin 0.10.18, which supports only Python 3.9–3.12 ([files](https://pypi.org/project/mediapipe/0.10.18/#files)).
- **Gotcha, legacy API:** `mp.solutions.face_mesh` was removed in 0.10.30, so use the Tasks `FaceLandmarker` ([#6192](https://github.com/google-ai-edge/mediapipe/issues/6192)).
- **Gotcha, single thread:** on Linux, MediaPipe runs model inference (via the XNNPACK library) on **1 thread** by default; Android, iOS and Web use half the cores, at most 4 ([source](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/calculators/tensor/inference_calculator_utils.cc)).
  - FPS therefore follows single-core speed.
  - Extra cores help only if you run parallel processes.
- **Gotcha, LIVE_STREAM mode:** the Python LIVE_STREAM API has reports of hanging ([#5466](https://github.com/google-ai-edge/mediapipe/issues/5466)). Prefer VIDEO mode and read the camera in your own thread.

**Measured data and estimates**

Setup for the estimates: FaceLandmarker with blendshapes, 1 face, 640×480, VIDEO mode, headless, 1 process.

| Board class (examples) | CPU; single-core 7-zip MIPS ([sbc-bench](https://github.com/ThomasKaiser/sbc-bench/blob/master/Results.md)) | Nearest measured MediaPipe data | Est. FPS |
|---|---|---|---|
| Pi 5 (BCM2712) | 4× A76 at 2.4 GHz; 3,196–3,305 | Pose at 640×480: lite ≈12 FPS, full 6.1 FPS (0.10.18 inside ROS 2, Aug 2025) ([Hackaday](https://hackaday.io/project/203704-gesturebot-ros2-computer-vision-mobile-platform/log/242569-mediapipe-pose-detection-real-time-performance-analysis)). Tasks object detector at 640×480 with Picamera2: 14.5 rising to ≈17 FPS (Dec 2023) ([blog](https://philvanallen.substack.com/p/another-day-another-model)). | 12–25 (estimate) |
| Pi 4 (BCM2711) | 4× A72 at 1.8 GHz; 1,741–1,769 | Legacy Face Mesh ">10 FPS" at 640×480 (2023) ([Core Electronics](https://core-electronics.com.au/guides/pose-and-face-landmark-raspberry-pi/)). Gesture Recognizer 5–9 FPS (May 2024) ([#404](https://github.com/google-ai-edge/mediapipe-samples/issues/404)). Legacy Hands 9 FPS (2021) ([PINTO](https://github.com/PINTO0309/mediapipe-bin)). | 6–12 (estimate) |
| Zero 2 W (RP3A0, 512 MB) | 4× A53 at 1.0 GHz; 838 | On a Pi 3 (A53 at 1.2 GHz): face detection from a USB webcam ≈6 FPS (Nov 2025) ([forum](https://forums.raspberrypi.com/viewtopic.php?p=2347024#p2347024)); face, hands and pose together ≈4 FPS (Jan 2026) ([forum](https://forums.raspberrypi.com/viewtopic.php?p=2357417#p2357417)). | 2–5 (estimate) |
| RK3588S (Orange Pi 5, ROCK 5C) | 4× A76 at 2.4 GHz + 4× A55; 2,689–3,174 | None found | 10–23 (estimate) |
| RK3582 (ROCK 5C Lite) | 2× A76 + 4× A55; 3,094 | None found | 11–23 (estimate) |
| RK3566 (Radxa ZERO 3W) | 4× A55 at 1.6 GHz; 1,155 | None found | 4–8 (estimate) |
| H618 (Orange Pi Zero 2W / Zero 3) | 4× A53 at 1.5 GHz; 1,165–1,167 | None found | 3–7 (estimate) |
| Reference: Intel x86, 32 cores | – | FaceLandmarker 1.0.1: 17.4 ms per frame at 640×480, about 1 core busy ([dms-face](https://github.com/youssefmedhat4/dms-face)) | 55 (measured) |

- **How the Pi 5 range was estimated:** the x86 single-core time multiplied by 3–5 gives 50–90 ms per frame (estimate). This matches the Pi 5's ≈17 FPS on a comparable Tasks detector.
- **Other rows** scale the Pi 5 range by single-core 7-zip ratios: Pi 4 0.53×, RK3566 and H618 0.35×, Zero 2 W 0.26× (calc). I rounded down for the weaker floating-point units of A53 and A55 cores (estimate).
  - Cross-check: XNNPACK's own benchmark gives a Pi 3B+ 79 ms against a Pi 4 at 41–46 ms for FP32 MobileNet v2 ([XNNPACK](https://github.com/google/XNNPACK)).
- **Old Face Mesh numbers flatter today's API:** FaceLandmarker took ≈2.4× as long as legacy FaceMesh (with refine_landmarks) in one M2 Mac test ([#5130](https://github.com/google-ai-edge/mediapipe/issues/5130)).
- **Latency:** time per frame is the inverse of per-process FPS, about 40–85 ms on a Pi 5 (estimate). Every board below the Pi 5 exceeds 100 ms per frame, so only Pi 5 and RK3588-class boards can meet the ≤ 100 ms end-to-end budget. Extra processes raise FPS but do not cut latency.
- **Cheap speed-ups:**
  - Overclock the Pi 5 to 3.0 GHz: +18–19 % single-core in sbc-bench (calc). It needs the Active Cooler.
  - Crop and scale in the ISP (Picamera2 `ScalerCrop` and stream size) rather than with `cv2.resize`.
  - Drop blendshapes and use the lip-landmark distance ratio for "mouth open".

## 3. Accessories for the top two boards (Pi 5, then Pi 4)

| Item | Seller | Price ₹ | Stock | Link | Notes |
|---|---|---|---|---|---|
| Pi 5 27 W USB-C PSU | Quartz | 1,063 (GST n/s) | **In** (black) | [link](https://quartzcomponents.com/products/official-27w-usb-c-pd-power-supply-for-raspberry-pi-5-white-black) | White ₹1,076, out |
| Pi 5 27 W USB-C PSU | Robocraze | 1,342 incl. | **In** | [link](https://robocraze.com/products/raspberry-pi-5-27w-usb-c-power-supply-black-colour) | |
| Pi 5 27 W USB-C PSU | Robu | 1,345 incl. | **In** | [link](https://robu.in/product-category/raspberry-pi-power-supplies-and-cables/) | Indian plug, black or white |
| Pi 5 27 W USB-C PSU | Evelta / Silverline | 925 +GST (1,092) / 1,020 +GST (1,204) | Unclear / Out | [Evelta](https://evelta.com/official-raspberry-pi-5-27w-usb-c-power-supply/) | |
| Pi 5 Active Cooler | Quartz | 452 | **In** | [link](https://quartzcomponents.com/products/official-raspberry-pi-5-active-cooler) | |
| Pi 5 Active Cooler | Robocraze / Robu | 565 / 569 incl. | **In** | [Robu](https://robu.in/product/official-raspberry-pi-5-active-cooler/) | Evelta 390 +GST (460) |
| microSD 32 GB SanDisk A1 | Robocraze | 1,549 incl. | **In** | [link](https://robocraze.com/products/sandisk-32gb-micro-sd-sdhc-card) | |
| microSD 32 GB SanDisk Ultra | Quartz / Silverline | 1,499 / 1,250 +GST (1,475) | **In** | [Q](https://quartzcomponents.com/products/32gb-ultra-microsd-memory-card-red-grey) | |
| microSD SanDisk Ultra Go 64 GB / 32 GB | Amazon.in | 1,578 / 1,638 | **In** | [64 GB](https://www.amazon.in/dp/B0GWW13HC3) | The 64 GB is cheaper than the 32 GB |
| microSD Raspberry Pi 32 GB A2 | Robu | 847 | Discontinued | [link](https://robu.in/product/official-raspberry-pi-micro-sd-card-32gb-a2-class/) | Raspberry Pi 64 GB A2: ₹3,679, in stock |
| Pi 5 camera cable, 22→15-pin, 200 / 300 / 500 mm | Robu | 134 / 296 / 409 incl. | **In** (all) | [200 mm](https://robu.in/product/official-raspberry-pi-5-camera-fpc-cable-200mm/) | Official; Waveshare 500 mm ₹399, in stock |
| Same cable | Robocraze | 134 (200 mm) / 213 (300 mm) | **In** / Out | [link](https://robocraze.com/products/raspberry-pi-camera-cable-standard-mini-200mm) | |
| Same cable | Silverline / Evelta | 88 / 80 / 315 +GST; 80 +GST | Out | [Evelta](https://evelta.com/official-raspberry-pi-5-camera-cable-csi-fpc-flexible-cable/) | |
| Pi 4 15.3 W USB-C PSU | Robu / Robocraze | 763 (black), 799 (white) / 795 | **In** | [Robocraze](https://robocraze.com/products/official-raspberry-pi-4-power-adapter) | |
| Pi 4 cooling: metal case with 2 fans / 30 mm 5 V fan | Robocraze | 599 / 138 | **In** | [case](https://robocraze.com/products/raspberry-pi-metal-aluminium-case-with-double-fans-for-raspberry-pi-4b-black) | |
| Pi 4 camera cable | – | Included with every camera (15-pin) | – | – | Spare 15 cm: Robocraze ₹35 |

Notes:
- microSD cards now cost roughly 3× their 2024–25 level (estimate). The cheapest 32 GB card seen was HP at ₹770 on [Amazon.in](https://www.amazon.in/dp/B07DJLFMPS); its A1 rating was not stated.
- A Pi 5 runs on a 5 V 3 A supply, but its USB ports are then limited to 600 mA (unverified in this pass; Raspberry Pi docs). That is fine with a CSI camera, so a Pi 4 PSU (₹763) or the robot's own 5 V 5 A rail can replace the 27 W unit.
- Keep the Active Cooler: a Pi 5 running MediaPipe continuously sat at 65–72 °C without throttling ([Hackaday](https://hackaday.io/project/203704-gesturebot-ros2-computer-vision-mobile-platform/log/242569-mediapipe-pose-detection-real-time-performance-analysis); its cooling setup was not stated). The CPU starts throttling at 80 °C (unverified in this pass).

## 4. Cameras

Every CSI camera below works on both the Pi 5 and the Pi 4 through libcamera/Picamera2; only the connector and cable differ.
- Official Raspberry Pi cameras are auto-detected by Raspberry Pi OS. If a clone is not detected, set `camera_auto_detect=0` and add `dtoverlay=<sensor>`, plus `,cam0` for the Pi 5's connector 0 ([docs](https://www.raspberrypi.com/documentation/computers/camera_software.html)).
- The Pi 5 needs the 22→15-pin cable from section 3; on a Pi 4 the camera's own cable fits.

| Item | Seller | Price ₹ | Stock | Link | Notes |
|---|---|---|---|---|---|
| Camera Module 3 standard (IMX708) | Silverline | 2,600 +GST (3,068) | **In** | [link](https://www.silverlineelectronics.in/products/test-3) | 66°×41°, phase-detect autofocus, HDR; 2304×1296 at 56 fps, 1536×864 at 120 fps; `imx708` overlay |
| Same | Robu | 3,299 incl. | **In** | [link](https://robu.in/product/raspberry-pi-camera-module-3/) | Robocraze ₹3,245 and Quartz ₹2,850: both out |
| Camera Module 3 Wide | Robocraze / Robu | 4,379 / 4,223 | **In** / Out | [link](https://robocraze.com/products/raspberry-pi-camera-module-3-wide) | 102°×67°: faces are too small at 2 m |
| Camera Module v2 (IMX219) | Quartz | 1,458 (GST n/s) | **In** | [link](https://quartzcomponents.com/products/raspberry-pi-camera-module-2) | 62.2°×48.8°, fixed but adjustable focus; 1640×1232 at 41 fps, 1080p at 47 fps, 640×480 at 206 fps; `imx219` overlay; may ship with an IMX355 sensor from Nov 2026 ([docs](https://www.raspberrypi.com/documentation/accessories/camera.html)) |
| Same | Robu / Robocraze | 1,748 / 1,695 | Not checked / Out | [Robocraze](https://robocraze.com/products/raspberry-pi-camera-module-v2-8-megapixel-1080p) | NoIR (no IR filter) version at Robocraze: ₹1,824, in stock |
| IMX219 clone, 79°, 4-lane, for Pi 5 (Waveshare) | Evelta | 1,794 +GST (2,117) | **In** (22) | [link](https://evelta.com/imx219-77-4lane-8mp-3280x2464-fov-79-camera-module-for-raspberry-pi-5/) | May need the vendor's overlay (unverified) |
| IMX219 clone, 120° / 160° (Waveshare) | Robu / Evelta | 1,919 / 1,166 +GST | **In** | [Robu](https://robu.in/?s=raspberry+pi+5+camera+fpc+cable&post_type=product) | Too wide for 2 m |
| OV5647 5 MP clone (Rev 1.3 style) | Quartz / Robocraze / Robu | 267 / 305 / 319 | **In** (all) | [Q](https://quartzcomponents.com/products/raspberry-pi-camera-module-board-5mp-webcam-video-1080p-720p), [Robu](https://robu.in/product/raspberry-pi-camera-module/) | ≈54°×41° (official v1 spec; clone lenses vary); fixed focus; 640×480 at 58, 1296×972 at 46, 1080p at 32 fps (unverified); `ov5647` overlay |
| OV5647, adjustable focus (Waveshare) | Evelta | 1,239 +GST (1,462) | Unclear | [link](https://evelta.com/raspberry-pi-camera-module-adjustable-focus-waveshare/) | |
| Logitech C270 (USB) | Amazon.in | 2,195 | **In** | [link](https://www.amazon.in/dp/B008QS9J6Y) | 720p at 30 fps, 55° diagonal, standard USB webcam (UVC) ([Logitech](https://www.logitech.com/en-in/products/webcams/c270-hd-webcam.960-000694.html)); other listings ₹2,469–2,685 |
| Logitech C310 (USB) | Amazon.in | Not listed | – | [specs](https://www.logitech.com/en-in/products/webcams/c310-hd-webcam.960-000588.html) | 720p at 30 fps, 60° diagonal |
| Cheap USB webcams: Zebronics FHD 30 fps / Frontech 2255 720p / Kreo Owl 1080p 60 fps | Amazon.in | 1,234 / 899 / 3,499 | **In** | [Zeb](https://www.amazon.in/dp/B0FLXPZ77B), [Kreo](https://www.amazon.in/dp/B0CG372R11) | Linux support untested (unverified); 60 fps halves the frame delay |

**Face size at 2 m** (calc; 14 cm face width, 640 px-wide frame; FaceLandmarker's BlazeFace short-range detector letterboxes the frame to 128 px)

| Lens (horizontal FOV) | % of frame width | px at 640 wide | px in the 128 px detector input |
|---|---|---|---|
| Camera Module 3 Wide (102°) | 2.8 % | 18 | 3.6 |
| Camera Module 3 (66°) | 5.4 % | 34 | 6.9 |
| Camera Module v2 / IMX219 (62°) | 5.8 % | 37 | 7.4 |
| OV5647 (≈54°) | 6.9 % | 44 | 8.9 |
| C270 (≈49°, from 55° diagonal) | 7.7 % | 49 | 9.9 |

- **Range limit:** the short-range detector "works best for faces within 2 meters" ([legacy docs](https://mediapipe.readthedocs.io/en/latest/solutions/face_detection.html)). A 7–10 px face will probably be missed (estimate).
- **Fix:** the turret keeps the face centred, so feed MediaPipe a 2–3× centre or tracked crop, which an ISP crop gives for free on CSI. Alternatively, find the face first with a full-range detector or YuNet.
- **Latency:** CSI through Picamera2 takes about one frame plus the exposure, 15–35 ms (estimate). A USB webcam at 30 fps takes about 70–150 ms from light to Python, including MJPEG decoding (estimate).
  - OpenCV's default buffer queue adds stale frames: set `CAP_PROP_BUFFERSIZE=1` or keep only the newest frame in a capture thread.
- **Best value for 0.5–2 m: the OV5647 clone (₹267–319)** for the first build.
  - Its narrower view means bigger faces at 2 m; it is light on the tilt head, and its 1296×972 binned mode at 46 fps allows a 2× crop.
  - Weaknesses: fixed focus, weaker low-light images, and lens quality varies between clones.
  - Upgrade to **Camera Module 3 standard** (₹3,068–3,299): it has autofocus, the best low-light performance, and 2304 px at 56 fps for a 3× crop and finer aiming.
  - Pick the C270 (₹2,195) only if cable routing or using the same camera on a PC matters more than latency.
- **Cable flex:**
  - The ribbon (flat flexible cable) suits static installs. Repeated bending fatigues the copper and gives intermittent "no camera" errors. Raspberry Pi publishes no flex rating (unverified), and the Pi 5's 22-pin latch is fragile.
  - If you use CSI: mount the Pi on the pan stage so only the tilt joint flexes the ribbon; use a large-radius rolling loop (at least 10× the cable thickness, ideally 20 mm or more) (estimate); never twist it; clamp it next to both connectors. If the Pi stays in the base, use a spiral loop and limit pan to ±90–120°.
  - Arducam's CSI-to-HDMI extender turns the moving section into a round HDMI cable: ₹1,739 at [Robu](https://robu.in/product/arducam-csi-to-hdmi-cable-extension-module-with-15pin-60mm-fpc-cable-for-raspberry-pi-camera-v3-v1-v2-hq-pack-of-2-1-set/). Its flex life is unverified.
  - A USB cable is round, stranded and tolerates bending and twisting far better; choose a thin, soft one and add strain relief.

## 5. Recommended combos, totals and trade-offs

| Basket | Board | Camera | Accessories | Total ₹ (calc) | Share of ₹21,000 |
|---|---|---|---|---|---|
| A. Cheapest (wait for stock) | Pi 5 1 GB, Robocraze ₹5,044 | OV5647, Robocraze ₹305 | PSU ₹1,342 + cooler ₹565 + SanDisk 32 GB ₹1,549 + 200 mm cable ₹134 | **8,939** | 43 % |
| A′. Same parts, cheapest sellers | Pi 5 1 GB ₹5,044 | OV5647, Quartz ₹267 | Quartz PSU ₹1,063 + Quartz cooler ₹452 + HP 32 GB ₹770 + cable ₹134 | **7,730** + shipping | 37 % |
| B. Step-up | Pi 5 2 GB, Robu ₹9,109 | Camera Module 3, Robu ₹3,299 | PSU ₹1,345 + cooler ₹569 + SD ₹1,549 + 300 mm cable ₹296 | **16,167** | 77 % |
| C. Buy today | Pi 5 4 GB, Robocraze ₹13,455 (in stock) | OV5647 ₹305 | As in A | **17,350** | 83 % |
| Not recommended | Pi 4 4 GB, Quartz ₹9,789 | OV5647 ₹267 (cable included) | Pi 4 PSU ₹763 + fan case ₹599 + SD ₹1,549 | 12,967 | 62 % |

Trade-offs:
- **Pi 5 vs Pi 4:** the Pi 4 4 GB costs more than basket A's Pi 5 and has about half the single-core speed. That gives an estimated 6–12 FPS and more than 100 ms per frame, missing the target.
- **1 GB vs 2 GB:**
  - A headless Pi 5 1 GB has about 720 MB free ([Raspberry Pi magazine](https://magazine.raspberrypi.com/articles/make-your-ram-go-further-raspberry-pi-os-memory-optimisation-tips)), and one FaceLandmarker process uses about 120–130 MB on x86 ([dms-face](https://github.com/youssefmedhat4/dms-face)).
  - So 1 GB is fine for 1–2 processes; choose 2 GB for 3 workers or a desktop (estimate).
  - The 4 GB costs ₹4,300–8,400 more.
- **Throughput vs latency:** extra worker processes raise FPS, but each frame still takes about 40–85 ms on a Pi 5 (estimate). End to end that is about 60–120 ms (estimate), so use 60 fps capture modes, short exposures and crops to stay under 100 ms.
- **Range:** at 2 m a face is only 7–10 px in the detector input with 54–66° lenses (calc). Plan for the 2–3× crop and avoid Wide or fisheye lenses.
- **OV5647 vs Camera Module 3:** about ₹2,800 extra buys autofocus, HDR, better low light and 1.8× more pixels for aiming. The OV5647 has fixed focus and variable lens quality.
- **CSI vs USB:**
  - CSI has lower latency and free ISP crop and scale, but its ribbon is fragile in a moving joint.
  - USB is robust and the same camera works on a PC, but it adds 2–4 frames of latency, caps at 30 fps, and spends CPU decoding MJPEG (estimate).
- **Non-Pi boards:**
  - RK3588 and RK3582 boards would roughly match the Pi 5 per core, but Indian shops do not stock them, and imports cost 2–4× list price.
  - RK3566, H618 and Zero 2 W boards fall well below 15 FPS (estimate).
- **Budget:** basket A leaves about ₹12,000 for servos, the launcher and printing; B leaves about ₹4,800; C leaves about ₹3,650. Waiting for 1 GB or 2 GB stock is worth it.

## 6. Feasibility: an old Android phone as the brain

- **Setup:** a Chrome page runs `@mediapipe/tasks-vision` FaceLandmarker (`delegate: "GPU"`, `runningMode: "VIDEO"`) ([guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/web_js), [demo](https://google-ai-edge.github.io/mediapipe-samples-web/#/vision/face_landmarker)).
  - The page sends aim and fire commands over Web Bluetooth to a BLE characteristic on the ESP32 (`writeValueWithoutResponse`, Chrome 85+).
  - A Pico without "W" has no Bluetooth.
- **Browser support:**
  - Supported: Chrome for Android (current version 157; Android 6.0+) and Samsung Internet 6.2+.
  - Not supported: Firefox for Android and iOS Safari.
  - Sources: [caniuse](https://caniuse.com/web-bluetooth), [implementation status](https://github.com/WebBluetoothCG/web-bluetooth/blob/main/implementation-status.md).
  - The page needs HTTPS (GitHub Pages works) and a tap to pick the device after every reload (unverified).
- **Speed:** about 15–30 FPS on a 2019-or-newer mid-range phone with the GPU delegate, and 8–15 FPS on 2016–2018 budget phones (estimate).
  - A native Android app is usually faster, since MediaPipe there uses up to 4 CPU threads plus the GPU ([source](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/calculators/tensor/inference_calculator_utils.cc)).
  - Each BLE command adds about 10–50 ms (estimate).
- **Drawbacks:**
  - The screen must stay on with the page in front (the Wake Lock API helps), and Bluetooth links drop.
  - The phone throttles when hot, and an old battery kept on charge can swell, which is a safety risk in a robot.
  - A phone on the pan/tilt head needs bigger servos; a fixed phone sees faces too small at 2 m.
  - Distance estimation needs the phone camera's intrinsics, and it will not auto-start the way a Pi service does.
- **Verdict:** a good zero-cost prototype for the vision logic, the trigger logic and the ESP32 BLE protocol while waiting for Pi stock, but not the final standalone brain.

## Open questions

- What are the real Pi 5 FaceLandmarker FPS and latency? Compare VIDEO mode with blendshapes on and off, 1 process vs 2–3, and an ISP crop vs the full frame, and log the temperature over 30 minutes.
- When will the Pi 5 1 GB and 2 GB be back in stock in India, and at what price? Robocraze's ₹7,869 for the 2 GB looks like a pre-October price.
- Does a 1 GB Pi 5 run Trixie Lite, mediapipe 1.2.3, OpenCV, Picamera2 and a control process without swapping?
- How far away can each camera detect a face with and without a 2–3× crop? Is the OV5647's fixed focus sharp at 0.5 m?
- Which overlay do the clone cameras need on a Pi 5, especially the 4-lane IMX219 and the OV5647 clones?
- Do Quartz and ThinkRobotics prices include GST, and what is shipping? The approved resellers e2u.in and Aryabot were not checked.
- Is the Radxa Cubie A7Z a cheap alternative? It is Pi-Zero-sized with an Allwinner A733 (2× A76 at 2 GHz) and costs from ₹5,994 incl. GST at [Evelta](https://evelta.com/cubie-a7z-tiny-size-mighty-ai-sbc-radxa/), with stock per variant unclear. MediaPipe speed and camera support are unknown.
- How long does the CSI ribbon last when cycled through the chosen pan/tilt routing, compared with a USB camera?
