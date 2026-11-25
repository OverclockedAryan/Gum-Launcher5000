# Vision & Compute Research

Last researched: 2026-11-25 (web research; verify before buying or building)

> **Phase 2 only.** Since [D-011](../decisions.md#d-011-phase-1-joystick-aiming-face-tracking-moves-to-phase-2) (2026-11-25), phase 1 is aimed with a joystick and has no camera or compute board. This note applies when face tracking returns.

Notation: **(calc)** = my own geometry or arithmetic from the sourced specs; **(unverified)** = no source found; **(estimate)** = judgement from indirect data.

## Key takeaways for the design

- **Use Raspberry Pi OS Trixie (Python 3.13.5) with `mediapipe` 1.1 or newer from PyPI.** Since 1.0.0 (2026-07-27) PyPI again ships a Linux aarch64 wheel (`py3-none`, Python 3.9–3.14). The 2024–2026 advice "Bookworm + 0.10.18 only" is obsolete. Write only against the Tasks `FaceLandmarker` API: `mp.solutions.face_mesh` left the pip package in 0.10.30 (2025-12-16). The same code runs on the Windows PC (`win_amd64` wheel).
- **Environment recipe:** a venv on `/usr/bin/python3` created with `--system-site-packages` (picamera2, libcamera and lgpio come only from apt), then `pip install mediapipe`. pip now pulls OpenCV 5.1, which needs NumPy 2 or newer. That is fine on Trixie (apt NumPy 2.2.4) but breaks `import picamera2` on Bookworm (apt NumPy 1.24.2).
- **Camera: Camera Module 3 standard, not Wide.** Run 2304×1296 at 56 fps (full 66°×41° field of view) or 1536×864 at 120 fps. The 120 fps mode is a binned centre crop, about 47°×28° (calc). The Pi 5 needs a separate 22-pin to 15-pin cable.
- **Finding the face, not tracking it, limits range.** FaceLandmarker's built-in BlazeFace short-range detector letterboxes the whole frame to 128×128 px, so a face at 2 m is about 7 px wide there (about 4 px with the Wide lens) (calc). Run detection on a centre or predicted crop (the turret keeps the face centred), or use full-range BlazeFace or YuNet and then crop. Use VIDEO or LIVE_STREAM mode so the detector is skipped while a face is being tracked.
- **Compute:** nobody has published a Pi 5 FaceLandmarker benchmark. Plan for about 10–25 FPS on the CPU (estimate, unverified) and benchmark first. The Hailo AI HAT+ ($70/$110) and AI HAT+ 2 ($200 list) cannot run FaceLandmarker with blendshapes off the shelf, so skip them.
- **Aiming precision needs pixels.** The 0.12° pointing budget in [ballistics.md](ballistics.md) is about 4 px at 2304 px across 66°, but only about 1 px if the frame is downscaled to 640 px (calc). Feed MediaPipe a full-resolution face crop and average over the 300 ms hold.
- **Mouth trigger:** require both the `jawOpen` blendshape and the inner-lip mouth aspect ratio (MAR: landmarks 13–14 over 78–308), with hysteresis, a continuous 300 ms hold, a still head and open eyes. Reject speech by its 2–7 Hz open/close rhythm and yawns by eye squint or closure and long duration. No official thresholds exist, so calibrate per user (for example 140 % of that person's neutral MAR).
- **Range is the hardest vision requirement.** [ballistics.md](ballistics.md) allows 2.5 % (1σ) range error. Uncalibrated single-camera cues give about 4–6 %: the iris method (11.7 ± 0.5 mm) had 4.3 % mean error in Google's test, and pupil distance varies ±5.5 % between adults. At 2 m the iris is only about 10 px wide, so 1 px is about 10 % (calc). Plan a per-user calibration at a known distance, then fuse iris, pupil distance and the face-matrix depth. The face-matrix depth assumes a 63° vertical FOV and must be scaled by about 1.64 for the CM3 standard lens (calc).
- **Cable to the moving camera:** CSI ribbon cables (flat flexible cables) are not rated for continuous flexing. Design a large-radius service loop (at least 10× the cable thickness, more if possible) and cycle-test it, or use a USB UVC camera, which also works on the Windows PC.
- **Pi 5 I/O and budget:** pigpio does not work on the Pi 5, and lgpio's PWM is software-timed (servo jitter). Use the RP1 hardware PWM (GPIO 12/13/18/19), the `pwm-pio` overlay, or a PCA9685 or microcontroller. Use the official 27 W (5.1 V 5 A) supply and the Active Cooler. After the 2026 RAM price rises the Pi 5 2 GB costs $77.50, and 2 GB is enough headless, so Pi, supply, cooler, CM3, cable and SD card come to about $130 of the $250 budget (calc).

## 1. MediaPipe today: version, wheels, install gotchas

- **Latest: 1.2.3, released 2026-11-11** ([PyPI](https://pypi.org/project/mediapipe/)). Version timeline: 0.10.18 (2024-11-01) → 0.10.21 (2025-02-06) → 0.10.30 (2025-12-16) … 0.10.35 (2026-04-27) → 1.0.0 (2026-07-27) → 1.1.0 (2026-10-06) → 1.2.3. Version 1.2.3 renames Tasks options, methods and result fields to match the other platforms and keeps deprecated aliases ([releases](https://github.com/google-ai-edge/mediapipe/releases)), so new examples may use new field names.
- Since 0.10.30 the wheels are tagged `py3-none`: one wheel per OS and architecture, with a thin Python layer over a bundled native `libmediapipe.so` (about 111 MB unpacked on aarch64) ([issoh.co.jp](https://www.issoh.co.jp/md/tech/4386), [dms-face](https://github.com/youssefmedhat4/dms-face)).
- **Pi 5 (Linux aarch64):** the wheel is `mediapipe-1.2.3-py3-none-manylinux_2_28_aarch64.whl`, 40.7 MB ([PyPI JSON](https://pypi.org/pypi/mediapipe/1.2.3/json)). Google lists "Raspberry Pi 5 or newer running 64-bit Raspberry Pi OS", glibc 2.28 or newer, and Python 3.9–3.14 ([setup guide](https://developers.google.com/edge/mediapipe/solutions/setup_python)). Python 3.13 and 3.14 arrived in 1.1.0; the 1.0.x classifiers list only 3.9–3.12 ([1.0.0 JSON](https://pypi.org/pypi/mediapipe/1.0.0/json)).
  - **Bookworm (Python 3.11): any 1.x works.**
  - **Trixie (Python 3.13): use 1.1.0 or newer.**
  - 32-bit OS: no wheel.
- **Why tutorials disagree:** 0.10.18 was the last release with aarch64 wheels (cp39–cp312) until 1.0.0; 0.10.20 through 0.10.35 shipped none ([0.10.35 JSON](https://pypi.org/pypi/mediapipe/0.10.35/json), [issue #5965](https://github.com/google-ai-edge/mediapipe/issues/5965), closed 2026-06-29). Guides that say "no Python 3.13, use Bookworm" (e.g. [SunFounder](https://docs.sunfounder.com/projects/ai-lab-kit/en/latest/mediapipe/mp_0_setup.html), which expects 0.10.18) predate 1.x.
- **Windows x86_64:** `py3-none-win_amd64` wheel (25.7 MB) for Python 3.9–3.14; 3.13 and newer are supported from 1.1.0. The last version-specific (cp-tagged) release, 0.10.21, covered cp39–cp312 ([0.10.21 JSON](https://pypi.org/pypi/mediapipe/0.10.21/json)). A `win_arm64` wheel also exists.
- **Legacy API removed:** `mp.solutions` (including `face_mesh`) has not been in the pip package since 0.10.30. A maintainer wrote: "We have removed support for MediaPipe Solutions. Please migrate to MediaPipe Tasks" ([#6192](https://github.com/google-ai-edge/mediapipe/issues/6192)). Old tutorial code raises `AttributeError`. Pinning `mediapipe==0.10.21` keeps it only on x86_64, macOS or Windows with Python 3.12 or older, never on the Pi.
- **Dependencies of 1.2.3:** `absl-py~=2.3`, `certifi`, unpinned `numpy`, `sounddevice~=0.5`, `flatbuffers~=25.9`, `opencv-contrib-python`, `matplotlib`. Today pip resolves **opencv-contrib-python 5.1.0.95 (2026-11-17), which requires numpy >= 2** ([PyPI](https://pypi.org/project/opencv-contrib-python/)). The last OpenCV wheel that accepts NumPy 1.x is 4.11.0.86; 4.12.0.88 and later need NumPy 2 ([history](https://pypi.org/project/opencv-python/#history)). The newest NumPy (2.5.x) needs Python 3.12 or newer.
- **picamera2 comes only from apt:** its libcamera bindings are built for `/usr/bin/python3`. Create the venv with `python3 -m venv --system-site-packages env` ([RPi docs](https://www.raspberrypi.com/documentation/computers/os.html)) or `uv venv --python /usr/bin/python3 --system-site-packages` ([uv recipe](https://pydevtools.com/handbook/how-to/how-to-use-picamera2-and-gpio-with-uv-on-raspberry-pi/)). Python versions installed by pyenv or uv cannot see libcamera. The old workaround (Python 3.12 via pyenv plus a USB camera, from #5965) is no longer needed.
- **NumPy binary clash:** apt NumPy is 1.24.2 on Bookworm and 2.2.4 on Trixie ([Debian](https://packages.debian.org/search?keywords=python3-numpy&searchon=names&exact=1&suite=all&section=all)); apt OpenCV is 4.6 and 4.10 respectively ([Debian](https://packages.debian.org/search?keywords=python3-opencv&searchon=names&exact=1&suite=all&section=all)).
  - On Bookworm, NumPy 2.x installed in the venv overrides apt's 1.x, and `import picamera2` then fails with "numpy.dtype size changed, may indicate binary incompatibility" ([Ultralytics forum](https://community.ultralytics.com/t/installation-of-yolo-creates-problems-with-dronekit-python-flight-scripts-on-raspberry-pi/1283/7)).
  - Fixes: `pip install -U simplejpeg` in the venv; or pin `opencv-contrib-python==4.11.0.86` plus `numpy<2` ([RPi forum](https://forums.raspberrypi.com/viewtopic.php?t=388523)); or use Trixie.
- **Lean install** (only one OpenCV in the environment): `pip install --no-deps mediapipe`, then the needed dependencies and `opencv-python-headless`. Measured on x86: memory after model load 89 MB instead of 131 MB, start-up 0.29 s instead of 0.66 s ([dms-face](https://github.com/youssefmedhat4/dms-face)).
- **lgpio:** PyPI has aarch64 wheels only for cp39–cp312 ([PyPI](https://pypi.org/project/lgpio/)). On Trixie use apt `python3-lgpio` and `python3-gpiozero` through `--system-site-packages`.
- **Memory page size:** the Pi 5 default kernel `kernel_2712.img` uses 16K pages; `kernel=kernel8.img` in config.txt switches to 4K if a native wheel misbehaves ([kernel docs](https://www.raspberrypi.com/documentation/linux/kernel/index.html)). No MediaPipe-specific report found (unverified risk).

## 2. FaceLandmarker (Tasks API)

- **Outputs per face:** 478 normalised 3-D landmarks (468 face mesh + 10 iris), 52 blendshape scores in [0, 1], and an optional 4×4 facial transformation matrix ([guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker)).
  - The 52 blendshapes are `_neutral` plus 51 ARKit-style names; there is no `tongueOut`.
  - Useful ones here: `jawOpen`, `mouthClose`, `mouthFunnel`, `mouthPucker`, `eyeBlinkLeft/Right`, `eyeSquintLeft/Right` ([face_blendshapes_graph.cc](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc)).
- **Options, with Python defaults:**
  - `running_mode`: IMAGE, VIDEO or LIVE_STREAM (default IMAGE)
  - `num_faces`: 1
  - `min_face_detection_confidence`, `min_face_presence_confidence`, `min_tracking_confidence`: 0.5 each
  - `output_face_blendshapes`, `output_facial_transformation_matrixes`: False
  - `result_callback`: LIVE_STREAM only
- **Calls** ([Python guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python)):
  - `detect(img)` in IMAGE mode
  - `detect_for_video(img, ts_ms)`: synchronous, processes every frame, needs increasing timestamps
  - `detect_async(img, ts_ms)`: drops frames while busy
  - Input: `mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)`
- **Tracking:** in VIDEO and LIVE_STREAM modes the face detector is skipped while faces are tracked from the previous frame; IMAGE mode always runs it. `min_tracking_confidence` is the box-similarity threshold used to match a face between frames ([face_landmarker_graph.cc](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/cc/vision/face_landmarker/face_landmarker_graph.cc)).
- **Model bundle** `face_landmarker.task`: 3.76 MB, float16, and the served file is unchanged since 2023-05-03 (HTTP Last-Modified). It chains three models ([guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker)):
  - BlazeFace short-range face detector, 128×128 input
  - FaceMesh-V2 landmark model, 256×256 input
  - blendshape model, 1×146×2 input

  Download from [Google Cloud Storage](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task) or the [Hugging Face mirror](https://huggingface.co/litert-community/MediaPipe-FaceLandmarker/resolve/main/face_landmarker.task) that the docs now link (same size).
- **Detector:** the frame is letterboxed (aspect ratio kept, zero padding) ([face_detector_graph.cc](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/cc/vision/face_detector/face_detector_graph.cc)). The legacy docs say short-range "works best for faces within 2 meters" and full-range "within 5 meters" ([legacy docs](https://mediapipe.readthedocs.io/en/latest/solutions/face_detection.html)); that assumes phone-selfie framing. BlazeFace short-range runs in 2.94 ms on a Pixel 6 CPU ([detector guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector)).
- **Practical range** (calc, 14 cm face width). Face width inside the 128 px detector input:

  | Camera and mode | 0.5 m | 1 m | 2 m |
  | --- | --- | --- | --- |
  | CM3 standard, full frame | 28 px | 14 px | 7 px |
  | CM3 standard, 120 fps crop | 41 px | 21 px | 10 px |
  | CM3 Wide | 15 px | 7 px | 4 px |

  Expect detection without help to fail somewhere around 1–1.5 m with the CM3 standard lens (unverified; test this). Fixes:
  - Run detection on a half-width centre or predicted crop, which doubles the face size.
  - Or run the FaceDetector task with `blaze_face_full_range.tflite` (192×192, 1.08 MB, [download](https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_full_range/float16/latest/blaze_face_full_range.tflite)) or YuNet on the full frame, then pass a square face crop to FaceLandmarker.
- **Iris landmarks:** 468–472 for one eye (468 is the centre) and 473–477 for the other (473 is the centre) ([connections](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/python/solutions/face_mesh_connections.py)).

## 3. Performance on the Raspberry Pi 5

- **No published Pi 5 FaceLandmarker or Face Mesh FPS figure found** in 2024–2026 blogs, forums or GitHub issues. One open benchmark request from Oct 2026 has no results yet ([issue](https://github.com/RMNO21/Drawsiness-detection/issues/10)). Nearest data points:
  - **Pi 5, MediaPipe 0.10.18 Pose inside a ROS 2 pipeline, 640×480:** lite model about 12 FPS, full model about 6.1 FPS; 60–70 % CPU, about 400 MB extra RAM, 65–72 °C with no throttling. At 320×240 it ran about 40 % faster with "significant accuracy loss" ([Hackaday log, Aug 2025](https://hackaday.io/project/203704-gesturebot-ros2-computer-vision-mobile-platform/log/242569-mediapipe-pose-detection-real-time-performance-analysis)).
  - **Pi 5 4 GB, Tasks object detector (EfficientDet), 640×480:** 14.5 FPS, rising to about 17 FPS after switching to picamera2 and removing OpenCV work ([blog, Dec 2023](https://philvanallen.substack.com/p/another-day-another-model)).
  - **Pi 4, legacy Face Mesh:** "greater than 10" FPS ([Core Electronics, 2023, may be outdated](https://core-electronics.com.au/guides/pose-and-face-landmark-raspberry-pi/)). Raspberry Pi says the Pi 5 has "two to three times the CPU and GPU performance" of the Pi 4 ([RPi](https://www.raspberrypi.com/news/introducing-raspberry-pi-5/)).
  - **FaceLandmarker vs legacy FaceMesh:** about 2× slower in one test on an M2 Mac (32.1 s vs 13.6 s for the same video) ([#5130](https://github.com/google-ai-edge/mediapipe/issues/5130)).
  - **x86 desktop, mediapipe 1.0.1 FaceLandmarker, about 1 core:** 12.4 ms at 320×240 and 17.4–17.8 ms from 480×360 to 960×720 ([dms-face](https://github.com/youssefmedhat4/dms-face)). Input size barely matters because the models resize internally to 128 and 256 px.
- **Estimate for the Pi 5 CPU (unverified):** about 10–25 FPS (40–100 ms per frame) for one face in VIDEO mode with blendshapes. Benchmark this before committing.
- **Ways to speed it up:**
  - Use VIDEO or LIVE_STREAM mode so the detector is skipped while tracking, and set `num_faces=1`.
  - Pass MediaPipe a square face crop of about 384–512 px instead of the full frame or a downscaled frame.
  - Let the camera's image processor scale the image (Picamera2 `main` and `lores` stream sizes) instead of `cv2.resize`; per-model format limits unverified.
  - Request RGB byte order directly. Picamera2 uses Linux DRM format names, where `RGB888` means "[23:0] R:G:B little endian", i.e. bytes in B,G,R order; ask for `BGR888` to get R,G,B ([drm_fourcc.h](https://github.com/torvalds/linux/blob/master/include/uapi/drm/drm_fourcc.h)). Verify with a test frame.
  - Run capture and inference in separate threads.
  - Turn off blendshapes or the matrix if unused (size of saving unverified).
  - CPU inference already uses TFLite's XNNPACK backend, so there is nothing to switch on. The Python Tasks API has no thread-count option (unverified).
  - Keep turret moves smooth: losing the tracked face forces a slower detector re-run.
- **OpenCV YuNet face detector:** 6.23 ms mean on a Pi 4B at 160×120 input with OpenCV 4.10 ([OpenCV Zoo](https://github.com/opencv/opencv_zoo/blob/main/benchmark/README.md)). No Pi 5 figure published; expect 2–3× faster (unverified). It outputs a box and 5 points with no lip opening, so use it only to find the face.
- **Accelerators:**
  - **AI HAT+:** 13 TOPS Hailo-8L for $70, 26 TOPS Hailo-8 for $110 at the Oct 2024 launch; the official page still says "from $70" ([RPi](https://www.raspberrypi.com/products/ai-hat/), [Tom's Hardware](https://www.tomshardware.com/raspberry-pi/raspberry-pi-release-higher-performance-ai-hat-13-and-26-tops-variants)).
  - **AI HAT+ 2:** Hailo-10H, 40 TOPS (INT4), 8 GB RAM. $130 at launch (2026-01-15), **$200 list now**. Raspberry Pi says its vision performance is "comparable to" the 26 TOPS AI HAT+ ([product](https://www.raspberrypi.com/products/ai-hat-plus-2/), [launch post](https://www.raspberrypi.com/news/introducing-the-raspberry-pi-ai-hat-plus-2-generative-ai-on-raspberry-pi-5/)).
  - **Face models available:** the Hailo Model Zoo has `face_landmarks_lite` (192×192 input, 0.6 M parameters; 424 FPS on Hailo-8L, 972 FPS on Hailo-10H) and `tddfa_mobilenet_v1` (3DDFA, 120×120) ([zoo, Hailo-8L](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_facial_landmark_detection.rst), [zoo, Hailo-10H](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO10H/HAILO10H_facial_landmark_detection.rst)). There is no FaceLandmarker-V2 with iris and blendshapes, so detection → crop → landmarks → MAR would have to be rebuilt by hand. A 2024 port of the MediaPipe pipelines to Hailo-8L had only hand tracking working ([AlbertaBeef, may be outdated](https://www.hackster.io/AlbertaBeef/accelerating-the-mediapipe-models-on-raspberry-pi-5-ai-kit-1698fe)). Not worth it under $250.

## 4. Mouth-open detection

- **Lip landmark indices** (`FACEMESH_LIPS`, [source](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/python/solutions/face_mesh_connections.py)):
  - Inner loop: 78–95–88–178–87–14–317–402–318–324–308–415–310–311–312–13–82–81–80–191.
  - Outer loop: corners 61 and 291, midpoints 0 (upper) and 17 (lower).
  - 13 and 14 are the upper and lower inner-lip midpoints; 78 and 308 are the inner mouth corners.
- **MAR variants:**
  - Simple: `|13−14| / |78−308|`.
  - Three pairs: `(|81−178| + |13−14| + |311−402|) / (2·|78−308|)` ([VTuber-Python-Unity](https://github.com/mmmmmm44/VTuber-Python-Unity/blob/main/facial_features.py)).
  - Normalised by the eye-corner span: `|13−14| / |33−263|`, labelled "surprised" above 0.08; the page calls these "empirical values at 640×480" ([SunFounder](https://docs.sunfounder.com/projects/ai-lab-kit/en/latest/mediapipe/mp_2_face_emotion.html)).
- **Thresholds in practice are empirical and per user.** A 2026 drowsiness paper sets the yawn threshold at 140 % of each driver's MAR from a 5 s neutral calibration and averages over 15 frames ([arXiv 2604.22479](https://www.alphaxiv.org/abs/2604.22479)). There is no official `jawOpen` threshold; 0.4–0.5 is a common starting point (unverified).
- **Rejecting speech:** during speech the mouth opening oscillates at 2–7 Hz, the syllable rhythm ([Chandrasekaran 2009](https://pmc.ncbi.nlm.nih.gov/articles/PMC2700967/)), so it dips every 140–500 ms. Require the open state to last the full 300 ms with no dips and low MAR variance, and require low `mouthClose`, `mouthPucker` and `mouthFunnel`.
- **Rejecting yawns** (design suggestion, unverified): a yawn is one long opening, usually with eye squint or closure and the head tilting back. Require both eyes open (`eyeBlink*` low), fire only in a window such as 300–1500 ms after the mouth opens, and abort if the eyes close.
- **Robustness:**
  - Time thresholds in milliseconds, not frame counts.
  - Use hysteresis: separate open and close thresholds, like the 0.30/0.20 eye-openness band in [dms-face](https://github.com/youssefmedhat4/dms-face).
  - Require a frontal face and a still head; the head-motion budget in [ballistics.md](ballistics.md) is 15 mm/s.
  - Ratios of distances in the image plane do not change with range.
- **Starting rule to calibrate on 5–10 people (unverified):** open when `jawOpen ≥ 0.45` and simple MAR ≥ 0.35 (or ≥ 140 % of the user's neutral MAR); closed when `jawOpen < 0.30` or MAR < 0.25.

## 5. Monocular face distance

- **Iris method:** the horizontal iris diameter is "roughly constant at 11.7±0.5 mm". Tested on 200+ people against an iPhone 11 depth sensor (under 2 % error up to 2 m), the mean relative error was **4.3 % (SD 2.4 %)**, and 4.8 % (SD 3.1 %) with glasses ([Google Research, 2020](https://research.google/blog/mediapipe-iris-real-time-iris-tracking-depth-estimation/)). The legacy docs say "less than 10% error" ([Iris docs](https://mediapipe.readthedocs.io/en/latest/solutions/iris.html)). This is a 2020 phone-camera result and is probably optimistic at 2 m. The Tasks API returns no depth: compute `d = f_px · 11.7 mm / iris_px` yourself from iris points 469/471 and 474/476.
- **Pupil distance (IPD):** in the US Army ANSUR II survey (2012), women 61.7 ± 3.6 mm and men 64.0 ± 3.4 mm, range 51–77 mm ([Wikipedia table](https://en.wikipedia.org/wiki/Pupillary_distance)); Dodgson 2004 gives about 63 mm mean ([SPIE](https://doi.org/10.1117/12.529999)). The spread between people is about ±5.5 % (1σ), which becomes the same distance error unless calibrated. Pupils converge when a person looks at the robot, about 1.4 mm narrower at 0.5 m (calc); the eye-corner span does not change with gaze.
- **Transformation matrix:** the canonical face model is in centimetres, with a virtual camera at the origin looking down −Z ([3D Face Transform](https://developers.googleblog.com/en/mediapipe-3d-face-transform/)). By default Tasks assumes a 63° vertical FOV, near plane 1 cm, far plane 100 m ([source](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/cc/vision/face_geometry/face_geometry_from_landmarks_graph.cc)). Rescale the depth as `z_true ≈ z_mp · tan(31.5°) / tan(VFOV_real/2)` (calc):

  | Camera | Vertical FOV | Multiply z by |
  | --- | --- | --- |
  | CM3 standard, full frame | 41° | 1.64 |
  | CM3 standard, 120 fps crop | 28° | 2.46 |
  | CM3 Wide | 67° | 0.93 |

  If you feed MediaPipe a crop, use the crop's FOV. The fixed face-size model adds the same per-person bias as IPD.
- **Pixel budget** (calc, CM3 standard, binned modes, focal length about 1700–1775 px):

  | | 0.5 m | 1 m | 2 m |
  | --- | --- | --- | --- |
  | Iris width | 41 px | 21 px | 10 px |
  | 1 px error (iris) | 2.4 % | 4.8 % | 9.6 % |
  | IPD | 224 px | 112 px | 56 px |
  | 1 px error (IPD) | 0.4 % | 0.9 % | 1.8 % |
- **Expected accuracy (estimate, unverified):** uncalibrated about ±5 % at 0.5–1 m and ±7–12 % at 2 m. After per-user calibration, about ±2–3 %, limited by pixel noise.
- **Requirement:** [ballistics.md](ballistics.md) budgets range error at 2.5 % (target) or 6 % (pessimistic), 1σ. At 1 m and 6 m/s each 1 % of range error moves the hit about 1.6 mm vertically. Uncalibrated cues miss the target budget, so calibration is required.
- **Calibration ideas:**
  - At session start the person stands at a 1 m mark for 2–3 s; learn their IPD, iris and face scale.
  - Fuse iris, IPD and the corrected matrix depth (Kalman filter, or the median over the 300 ms hold).
  - Measure camera intrinsics with an OpenCV chessboard, for both the Pi camera and the Windows webcam.
  - Keep focus fixed while measuring: autofocus shifts the effective focal length (size of the effect unverified).
  - Optionally cross-check with a time-of-flight distance sensor (suitability unverified).

## 6. Camera choices and cabling

- **Camera Module 3** (Sony IMX708, 4608×2592, 1.4 µm pixels) ([RPi docs](https://www.raspberrypi.com/documentation/accessories/camera.html), [product](https://www.raspberrypi.com/products/camera-module-3/)):
  - Standard: **66° horizontal × 41° vertical** (75° diagonal), focal length 4.74 mm.
  - Wide: **102° × 67°** (120° diagonal), focal length 2.75 mm.
  - From $25; Wide was $35 at launch ([Tom's review](https://www.tomshardware.com/reviews/raspberry-pi-camera-module-v3)). In production until at least Jan 2030.
- **Sensor modes:**
  - 4608×2592 at about 14 fps ([Luxonis](https://docs.luxonis.com/hardware/sensors/IMX708)).
  - 2304×1296 at 56 fps: 2×2 binned, full field of view.
  - 1536×864 at 120 fps: the driver comment calls it "2x2 binned and cropped for 720p", taken from the central 3072×1728 ([imx708.c](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/drivers/media/i2c/imx708.c)). That gives about 46.8°×28.0° on the standard lens and about 79°×48° on Wide (calc, ignoring lens distortion).
- **Autofocus:** voice-coil lens with phase-detect (visible light) plus contrast-detect focusing ([camera software docs](https://www.raspberrypi.com/documentation/computers/camera_software.html)).
  - Controls: `AfMode` manual/auto/continuous, `AfRange` normal/macro/full, `AfSpeed` normal/fast.
  - `LensPosition` is in dioptres (1/m): 0 is infinity, "default" is the hyperfocal position.
  - Continuous autofocus may hunt while the turret moves (unverified), so prefer manual `LensPosition ≈ 1/d_est`. Focused at about 1.1 m, the sharp range is roughly 0.74–2.2 m at binned resolution (calc, assumes f/1.8, which is unverified).
- **Latency:** `SensorTimestamp` marks the start of sensor readout on the CPU's monotonic clock. One measurement gave 14–21 ms from readout start to `capture_request()` returning (Pi 4, OV9281 sensor, 1280×800) ([picamera2 #787](https://github.com/raspberrypi/picamera2/issues/787)). Expect about one frame time plus exposure (about 15–30 ms) on the Pi 5 (unverified). Keep `buffer_count` at 2 or more and measure it.
- **Pi 5 connectors:** two 4-lane MIPI "mini" 22-pin ports (0.5 mm pitch), each usable for a camera or a display. The CM3 uses a 15-pin (1 mm) connector and ships with a 200 mm 15-pin cable, so buy the 22-to-15-pin "Standard-Mini" cable (200/300/500 mm, about $2.50–3.20) ([docs](https://www.raspberrypi.com/documentation/computers/camera_software.html), [Adafruit](https://www.adafruit.com/product/5818)).
- **Global Shutter Camera** ([product](https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/)):
  - Sony IMX296, 1.58 MP, 1456×1088 at 60 fps, 3.45 µm pixels, exposures "as low as 30μs" with enough light.
  - C/CS lens mount, no lens included; in production until Jan 2032.
  - No rolling-shutter skew while the turret moves, but lower resolution, manual focus and a heavy C/CS lens on the moving head. Price about $50 plus lens (unverified).
- **Motion blur (calc):** about 35 px per degree (2304 px over 66°). A 60°/s pan with a 4 ms exposure smears about 8 px. Cap `ExposureTime` (light the face) and judge and fire only after the turret has settled.
- **CSI ribbon through a moving joint:**
  - FFCs are flat cables "designed mainly to carry signals"; FPCs (flexible printed circuits) are the ones designed to bend ([JLCPCB](https://jlcpcb.com/blog/fpc-vs-ffc)).
  - For repeated bending, keep the bend radius at least 10× the thickness "and more where possible", with rolled-annealed copper ([Altium, 2026](https://resources.altium.com/p/dynamic-flex-vs-static-flex)).
  - Molex quotes flex life from about 10⁴ cycles (standard FFC jumpers) to about 10⁶ (thin-insulation high-flex grades) ([Molex](https://www.molex.com/content/molex/molex-dot-com/us/en/products/cable-assemblies/flat-flexible-cables-ffc); exact numbers unverified). No flex rating is published for Raspberry Pi camera cables (unverified).
  - Options:
    - A spiral (clock-spring) loop around the pan axis plus a rolling loop for tilt, clamped next to both connectors, then cycle-tested.
    - A USB UVC camera on a high-flex cable, which doubles as the Windows development camera (MJPEG decode cost and latency unverified).
    - A fixed camera instead of one on the moving head.

## 7. Raspberry Pi 5 practicalities

- **OS:** the current images (2026-10-06) are Raspberry Pi OS **Trixie** (Debian 13, kernel 6.18); Bookworm (Debian 12, kernel 6.12) is listed as "Legacy" ([downloads](https://www.raspberrypi.com/software/operating-systems/)). Trixie became the default on 2025-10-02. Upgrading a running Bookworm install in place is not supported, and staff say Bookworm gets no more Raspberry Pi-specific package updates ([announcement and comments](https://www.raspberrypi.com/news/trixie-the-new-version-of-raspberry-pi-os/)). Default Python: **3.13.5** on Trixie, 3.11.2 on Bookworm ([Debian](https://packages.debian.org/search?keywords=python3&searchon=names&exact=1&suite=all&section=all)).
- **GPIO:**
  - gpiozero: "Only lgpio works on the Pi 5" ([docs](https://gpiozero.readthedocs.io/en/latest/api_pins.html)).
  - pigpio does not support the Pi 5: its timing relied on VideoCore DMA, which the Pi 5's RP1 I/O chip does not provide; the issue is still open ([#589](https://github.com/joan2937/pigpio/issues/589)).
  - `rpi-lgpio` is a drop-in replacement for RPi.GPIO. Its docs say the Pi 5 header is GPIO chip 4; newer kernels may expose it as gpiochip0 (unverified; check with `gpioinfo`) ([rpi-lgpio](https://rpi-lgpio.readthedocs.io/en/latest/differences.html)). libgpiod (`gpiod`) also works.
- **PWM:**
  - lgpio's `tx_pwm` and `tx_servo` are software-timed: "The timing jitter will cause the servo to fidget" ([lgpio](https://abyz.me.uk/lg/py_lgpio.html)).
  - Hardware PWM on the Pi 5: GPIO 12/13/18/19 are channels 0–3. Enable with `dtoverlay=pwm-2chan` (default GPIO 18/19, or `pin=12,func=4,pin2=13,func2=4`) and drive with `rpi-hardware-pwm` ([README](https://github.com/Pioreactor/rpi_hardware_pwm)).
  - The `pwm-pio` overlay gives up to 4 more PWM outputs on any GPIO 0–27, Pi 5 only ([overlays README](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README)).
  - For several servos plus launcher timing, a PCA9685 board or a small microcontroller is simpler (design note).
- **UARTs:** overlays `uart0-pi5` to `uart4-pi5` use GPIO 14-15, 0-1, 4-5, 8-9 and 12-13; `uart4` clashes with PWM on 12/13 ([overlays README](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README)). There is also a debug UART (UART10) on the 3-pin connector ([docs](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)).
- **Power** ([docs](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html), [PSU](https://www.raspberrypi.com/products/27w-power-supply/)):
  - Use a 5 V 5 A USB-PD supply; the official 27 W unit gives 5.1 V 5 A. The board boots on 3 A.
  - With a 5 A PD supply the USB ports get 1.6 A; otherwise they are limited to 600 mA.
  - `usb_max_current_enable=1` forces the high USB limit; only use it if the supply can deliver it. The EEPROM setting `PSU_MAX_CURRENT` (3000 or 5000) skips PD negotiation.
  - Current limits: GPIO 50 mA total and 16 mA per pin; Camera Module 250 mA; bare board about 800 mA when active.
  - Power the servos and launcher from their own supply.
- **Thermal** ([docs](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html), [Active Cooler](https://www.raspberrypi.com/products/active-cooler/)):
  - The CPU cores throttle progressively from 80 °C to 85 °C; at 85 °C both CPU and GPU throttle.
  - The Active Cooler fan is off below 50 °C and steps up at 50/60/67.5/75 °C with 5 °C hysteresis. It draws from the same current budget as USB.
  - Continuous MediaPipe ran at 65–72 °C on a Pi 5 ([Hackaday](https://hackaday.io/project/203704-gesturebot-ros2-computer-vision-mobile-platform/log/242569-mediapipe-pose-detection-real-time-performance-analysis)), so vent the printed enclosure.
- **RAM options and 2026 prices:** 1, 2, 4, 8 or 16 GB.
  - 1 GB: unchanged at $45.
  - 2 GB: $50 at launch, $65 in Feb 2026, **$77.50 from 1 Oct 2026** ([OMG! Ubuntu](https://www.omgubuntu.co.uk/2026/10/raspberry-pi-2gb-costs-how-much-now), [RPi](https://www.raspberrypi.com/news/more-memory-driven-price-rises/)).
  - 4 GB about $110 and 8 GB about $180 in Oct 2026 ([Phoronix](https://www.phoronix.com/news/Raspberry-Pi-5-2GB-Price-77.50)); another table lists lower prices, so verify.
  - 16 GB: $305 on the official page vs $385 reported from Nov 2026 ([OMG! Ubuntu](https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up)).
- **Is 2 GB enough?** Yes for a headless (Lite) build (estimate). The FaceLandmarker process uses about 90–130 MB after model load (measured on x86) ([dms-face](https://github.com/youssefmedhat4/dms-face)); a heavier ROS 2 + pose stack used about 400 MB on a Pi 5 ([Hackaday](https://hackaday.io/project/203704-gesturebot-ros2-computer-vision-mobile-platform/log/242569-mediapipe-pose-detection-real-time-performance-analysis)). Choose 4 GB only to develop on the Pi's desktop with a browser or IDE.
- **Cost sketch** (calc, list prices; 2026 prices for the supply, cooler and SD card unverified):

  | Part | Price |
  | --- | --- |
  | Pi 5 2 GB | $77.50 |
  | 27 W PSU | about $12 |
  | Active Cooler | about $5 |
  | Camera Module 3 | $25 |
  | Pi 5 camera cable | about $3 |
  | 32 GB microSD | about $10 |
  | **Total** | **about $132 (53 % of $250)** |

  With the 4 GB Pi the total is about $165.

## Open questions / verify on hardware

- FaceLandmarker FPS and latency on the Pi 5: VIDEO vs LIVE_STREAM, blendshapes on and off, crops of 256–512 px, CPU temperature over 30 minutes.
- Detection distance with CM3 standard vs Wide, full frame vs centre crop vs full-range BlazeFace or YuNet, at 0.5, 1, 1.5 and 2 m in normal room light.
- End-to-end latency (`SensorTimestamp` to aim command), and jitter of the mouth-centre landmark (px, 1σ) during the 300 ms hold compared with the 0.12° pointing budget.
- Focus strategy: continuous autofocus vs manual `LensPosition = 1/d`; focus hunting, exposure and motion blur while the turret moves.
- Range accuracy against a tape measure for iris, IPD and the corrected matrix depth, before and after per-user calibration; check the 63° FOV correction empirically.
- `jawOpen` and MAR thresholds on 5–10 people (talking, laughing, yawning, glasses, beards); false triggers per hour.
- In a Trixie venv: do mediapipe 1.2.x, OpenCV 5.1, apt NumPy 2.2.4 and picamera2 all import cleanly? Does `cv2.FaceDetectorYN` (YuNet) behave the same under OpenCV 5?
- Pi 5 GPIO chip number on the current kernel, servo jitter with hardware PWM, and the UART/PWM pin plan.
- Cycle test of the camera ribbon through the chosen pan/tilt routing vs a USB camera.
- Re-check Pi 5, camera and HAT prices when buying; they changed several times in 2026.
