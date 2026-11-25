#!/usr/bin/env python3
"""DESUU launcher and feed sizing for the M2 bench rig (D-001, D-006).

From pellet measurements and a target exit speed this computes:
  * the spring: stored energy, rate, preload trim range and the 40 mJ cap check
  * the snail cam: a constant-torque profile with a pressure-angle limit, written
    as a DXF (pitch curve + cam surface for a roller follower) and a CSV
  * cocking torque and time on the JGY370 worm motor
  * the pellet channel, shuttle pocket and magazine dimensions
  * the IR chronograph gate spacing and its timing error

Standard library only:
    python tools/launcher_design.py                    # defaults = estimated pellet
    python tools/launcher_design.py --mass-g 1.42 --length-mm 16.8 --width-mm 10.9 \
        --thick-mm 6.9 --thick-min-mm 6.6 --thick-max-mm 7.2
Outputs (default): docs/mechanical/launcher-sizing.md, cad/launcher/cam_profile.dxf
and cad/launcher/cam_profile.csv.

SI units inside; mm, g, mJ, degrees only in the report. Until pellets are measured
(docs/roadmap.md, first actions) every geometric number is a placeholder.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

G_TO_KG = 1e-3
MM = 1e-3


# --------------------------------------------------------------------------- spring
def spring_design(a: argparse.Namespace) -> dict[str, float]:
    m = a.mass_g * G_TO_KG
    m_max = a.mass_max_g * G_TO_KG
    m_eff = a.sled_g * G_TO_KG + a.spring_g * G_TO_KG / 3  # sled + 1/3 of the spring
    x1 = a.preload_mm * MM
    s = a.stroke_mm * MM
    x2 = x1 + s
    e_move = 0.5 * (m_eff + m) * a.v0**2
    e_store = e_move / (1 - a.loss)
    k = 2 * e_store / (x2**2 - x1**2)

    def stored(delta: float) -> float:  # extra preload delta (m) from the trim screw
        return 0.5 * k * ((x2 + delta) ** 2 - (x1 + delta) ** 2)

    def speed(delta: float, mass: float) -> float:
        return math.sqrt(2 * (1 - a.loss) * stored(delta) / (m_eff + mass))

    def cap_energy(delta: float) -> float:  # zero friction, heaviest pellet: worst case
        return stored(delta) * m_max / (m_eff + m_max)

    # stored() is linear in delta: largest extra preload that keeps the cap
    cap = a.cap_mj * 1e-3
    slope = 0.5 * k * 2 * s  # d(stored)/d(delta)
    delta_cap = (cap * (m_eff + m_max) / m_max - stored(0.0)) / slope

    # stroke duration: (M+m) x'' = (1-loss) k x, from x2 down to x1
    t, x, v, dt = 0.0, x2, 0.0, 1e-6
    while x > x1:
        acc = (1 - a.loss) * k * x / (m_eff + m)
        v += acc * dt
        x -= v * dt
        t += dt

    return {
        "m": m, "m_max": m_max, "m_eff": m_eff, "x1": x1, "x2": x2, "s": s,
        "e_move": e_move, "e_store": e_store, "k": k,
        "f_pre": k * x1, "f_peak": k * x2,
        "cap_nominal": cap_energy(0.0), "delta_cap": delta_cap,
        "v_no_preload": speed(-x1, m), "v_at_cap_trim": speed(delta_cap, m),
        "ke_pellet": 0.5 * m * a.v0**2,
        "bumper_energy": 0.5 * m_eff * a.v0**2,
        "mass_sens": 0.5 * 0.10 * m / (m + m_eff),  # speed change for a 10 % mass change
        "stroke_time": t,
    }


# --------------------------------------------------------------------------- cam
def cam_design(a: argparse.Namespace, sp: dict[str, float]) -> dict:
    """Constant-torque rise capped at a maximum pressure angle (roller follower)."""
    r0 = (a.base_r_mm + a.roller_r_mm) * MM  # pitch radius at zero lift
    gap = a.landing_gap_mm * MM  # follower rests this far off the base circle after a shot
    lift_total = s_total = sp["s"] + gap
    rise = math.radians(a.rise_deg)
    tan_max = math.tan(math.radians(a.pressure_max_deg))
    k, x1, s = sp["k"], sp["x1"], sp["s"]
    n = 2000
    dth = rise / n

    def run(torque: float) -> list[float]:
        u, lifts = 0.0, [0.0]
        for _ in range(n):
            if u < gap:  # cam closing the landing gap: no spring load yet
                du = (r0 + u) * tan_max * dth
            else:
                force = a.guide_friction * k * (x1 + u - gap)
                du = min(torque / force, (r0 + u) * tan_max) * dth
            u = min(u + du, s_total)
            lifts.append(u)
        return lifts

    if run(1e3)[-1] < s_total:
        raise SystemExit("Cam can't complete the stroke within the pressure-angle limit: "
                         "raise --base-r-mm or --rise-deg.")
    lo, hi = 1e-5, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if run(mid)[-1] < s_total else (lo, mid)
    torque = hi
    lifts = run(torque)

    # torque actually required along the rise, and the pressure angle there
    t_max = phi_max = 0.0
    for i in range(n):
        du = (lifts[i + 1] - lifts[i]) / dth
        if lifts[i] >= gap:
            force = a.guide_friction * k * (x1 + lifts[i] - gap)
            t_max = max(t_max, force * du)
        phi_max = max(phi_max, math.degrees(math.atan2(du, r0 + lifts[i])))

    # pitch curve: rise, full-lift dwell (the "ready" park), radial drop, base landing
    pts: list[tuple[float, float, float]] = []  # (theta, radius, lift)
    for i in range(0, n + 1, 10):
        pts.append((i * dth, r0 + lifts[i], lifts[i]))
    dwell = math.radians(a.dwell_deg)
    for j in range(1, 11):
        th = rise + dwell * j / 10
        pts.append((th, r0 + lift_total, lift_total))
    land_start = rise + dwell
    for j in range(0, 61):
        th = land_start + (2 * math.pi - land_start) * j / 60
        pts.append((th, r0, 0.0))

    # radius of curvature of the rising pitch curve (undercut check)
    rho_min = math.inf
    rise_pts = [(math.cos(t) * r, math.sin(t) * r) for t, r, _ in pts if t <= rise]
    for i in range(1, len(rise_pts) - 1):
        (xa, ya), (xb, yb), (xc, yc) = rise_pts[i - 1], rise_pts[i], rise_pts[i + 1]
        ab, bc, ca = math.dist((xa, ya), (xb, yb)), math.dist((xb, yb), (xc, yc)), math.dist((xc, yc), (xa, ya))
        area2 = abs((xb - xa) * (yc - ya) - (yb - ya) * (xc - xa))
        if area2 > 1e-15:
            rho_min = min(rho_min, ab * bc * ca / (2 * area2))

    omega_load = a.motor_rpm * 2 * math.pi / 60
    return {
        "r0": r0, "gap": gap, "lift_total": lift_total, "torque_design": torque, "torque_max": t_max, "phi_max": phi_max,
        "pts": pts, "rho_min": rho_min,
        "torque_hold": 0.0,
        "cock_time": rise / omega_load,
        "fire_latency": (dwell / 2) / omega_load,
        "motor_margin": a.motor_rated_kgcm * 9.81e-2 / t_max,
    }


def cam_surface(pts: list[tuple[float, float, float]], roller: float, drop_angle: float) -> list[tuple[float, float]]:
    """Cam surface for a roller follower: offset the pitch curve inward by the roller radius.

    The rise+dwell and the base landing are offset as separate open curves and joined by a
    radial drop face, so the sharp drop doesn't produce a notch.
    """
    rise = [p for p in pts if p[0] <= drop_angle + 1e-9 and p[2] > 0 or p[0] == 0.0]
    land = [p for p in pts if p[0] >= drop_angle - 1e-9 and p[2] == 0.0][:-1]  # last = start point
    return _offset(rise, roller) + _offset(land, roller)


def _offset(pts: list[tuple[float, float, float]], roller: float) -> list[tuple[float, float]]:
    """Offset an open counter-clockwise curve inward (one-sided differences at the ends)."""
    xy = [(r * math.cos(t), r * math.sin(t)) for t, r, _ in pts]
    out = []
    for i, (x, y) in enumerate(xy):
        xp, yp = xy[max(i - 1, 0)]
        xn, yn = xy[min(i + 1, len(xy) - 1)]
        tx, ty = xn - xp, yn - yp
        norm = math.hypot(tx, ty) or 1.0
        nx, ny = ty / norm, -tx / norm  # outward for counter-clockwise order
        out.append((x - roller * nx, y - roller * ny))
    return out


def write_dxf(path: Path, curves: dict[str, list[tuple[float, float]]], shaft_d_mm: float) -> None:
    """Minimal R12 DXF: closed outlines as LINE entities (mm) plus the shaft circle."""
    lines = ["0", "SECTION", "2", "ENTITIES"]
    for layer, poly in curves.items():
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            lines += ["0", "LINE", "8", layer, "10", f"{x1 * 1e3:.4f}", "20", f"{y1 * 1e3:.4f}",
                      "30", "0.0", "11", f"{x2 * 1e3:.4f}", "21", f"{y2 * 1e3:.4f}", "31", "0.0"]
    lines += ["0", "CIRCLE", "8", "SHAFT", "10", "0.0", "20", "0.0", "30", "0.0", "40", f"{shaft_d_mm / 2:.4f}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


# --------------------------------------------------------------------------- feed
def feed_design(a: argparse.Namespace) -> dict[str, float]:
    c_slide = a.slide_clearance_mm
    ch_w, ch_h = a.width_max_mm + c_slide, a.thick_max_mm + c_slide  # the largest pellet must pass
    return {
        "channel_w": ch_w, "channel_h": ch_h,
        # can the pellet flip inside the channel? (diagonal must not fit)
        "flip_margin_long": math.hypot(a.width_mm, a.thick_min_mm) - ch_w,  # nominal width, thinnest
        "flip_margin_cross": math.hypot(a.length_mm, a.thick_min_mm) - (a.length_max_mm + c_slide),
        "pocket_depth": a.pocket_ratio * a.thick_max_mm,
        "pocket_limit": 2 * a.thick_min_mm,
        "pocket_l": a.length_max_mm + c_slide, "pocket_w": a.width_max_mm + c_slide,
        "shuttle_travel": a.width_max_mm + c_slide + a.shuttle_wall_mm + 1.0,
        "tube_l": a.length_max_mm + 0.6, "tube_w": a.width_max_mm + 0.6,
        "stack_h": a.capacity * a.thick_max_mm,
    }


def chrono_design(a: argparse.Namespace) -> dict[str, float]:
    gap = a.gate_mm * MM
    transit = gap / a.v0
    return {
        "transit_ms": transit * 1e3,
        "err_spacing": a.gate_tol_mm / a.gate_mm,
        "err_1us": 1e-6 / transit,
        "err_50us": 50e-6 / transit,
        "v_max_transit_ms": gap / (a.cap_speed()) * 1e3,
    }


# --------------------------------------------------------------------------- report
def report(a: argparse.Namespace, sp: dict, cam: dict, fd: dict, ch: dict) -> str:
    w: list[str] = []
    p = w.append
    p("# Launcher and feed sizing (M2 bench rig)")
    p("")
    p("Generated by `tools/launcher_design.py`; re-run it with measured pellets. "
      "Design basis: [D-001](../decisions.md#d-001-launcher-snail-cam-spring-push-sled), "
      "[D-006](../decisions.md#d-006-feed-orientation-locking-stack-with-a-spring-return-shuttle), REQ-SAF-003.")
    p("")
    p("## Inputs")
    p("")
    p("| Input | Value |")
    p("| --- | --- |")
    p(f"| Pellet (nominal) | {a.length_mm:.1f} × {a.width_mm:.1f} × {a.thick_mm:.1f} mm, {a.mass_g:.2f} g |")
    p(f"| Pellet thickness spread | {a.thick_min_mm:.1f}–{a.thick_max_mm:.1f} mm |")
    p(f"| Largest pellet (L × W) | {a.length_max_mm:.1f} × {a.width_max_mm:.1f} mm |")
    p(f"| Heaviest pellet configured | {a.mass_max_g:.2f} g |")
    p(f"| Target exit speed | {a.v0:.1f} m/s |")
    p(f"| Sled, spring mass | {a.sled_g:.1f} g, {a.spring_g:.1f} g (a third counts as moving) |")
    p(f"| Friction loss | {a.loss * 100:.0f} % of stored energy |")
    p(f"| Stroke, base preload | {a.stroke_mm:.0f} mm, {a.preload_mm:.0f} mm |")
    p(f"| Energy cap | {a.cap_mj:.0f} mJ |")
    p("")
    p("## Spring")
    p("")
    p("| Result | Value | Note |")
    p("| --- | --- | --- |")
    p(f"| Stored energy needed | {sp['e_store'] * 1e3:.0f} mJ | {sp['e_move'] * 1e3:.0f} mJ moving + losses |")
    p(f"| **Spring rate** | **{sp['k'] / 1e3:.3f} N/mm** | compressed {sp['x1'] / MM:.0f} → {sp['x2'] / MM:.0f} mm |")
    p(f"| Force at preload / fully cocked | {sp['f_pre']:.1f} N / {sp['f_peak']:.1f} N | |")
    p(f"| Pellet energy at {a.v0:.1f} m/s | {sp['ke_pellet'] * 1e3:.1f} mJ | operating ceiling 30 mJ |")
    ok = "passes" if sp["cap_nominal"] <= a.cap_mj * 1e-3 else "**FAILS**"
    p(f"| Worst-case pellet energy (zero friction, {a.mass_max_g:.2f} g) | {sp['cap_nominal'] * 1e3:.1f} mJ | {ok} the {a.cap_mj:.0f} mJ cap |")
    p(f"| Max extra preload from the trim screw | {sp['delta_cap'] / MM:+.1f} mm | the cap still holds; print a hard stop here |")
    p(f"| Speed trim range | {sp['v_no_preload']:.2f}–{sp['v_at_cap_trim']:.2f} m/s | zero preload to the hard stop |")
    p(f"| Speed change for ±10 % pellet mass | ∓{sp['mass_sens'] * 100:.1f} % | sled dominates the moving mass |")
    p(f"| Energy into the bumper per shot | {sp['bumper_energy'] * 1e3:.0f} mJ | TPU 95A bumper, replaceable |")
    p(f"| Stroke duration | {sp['stroke_time'] * 1e3:.1f} ms | |")
    p("")
    p("**Getting this rate from stock springs.** Rate scales with 1 / active length: measure your spring's rate "
      "(hang a known mass, read the deflection), then cut it to `L_cut = L_measured × k_measured / k_needed`. "
      f"Its free length must exceed {sp['x2'] / MM:.0f} mm + solid length (coils × wire diameter) + 3 mm; "
      "if it doesn't, use two softer springs in parallel on the two guide rods.")
    p("")
    p("## Snail cam (roller follower, 623ZZ)")
    p("")
    p("| Result | Value | Note |")
    p("| --- | --- | --- |")
    p(f"| Base radius / roller radius | {a.base_r_mm:.0f} mm / {a.roller_r_mm:.0f} mm | pitch radius {cam['r0'] / MM:.0f} → {(cam['r0'] + cam['lift_total']) / MM:.0f} mm |")
    p(f"| Rise / ready dwell / landing | {a.rise_deg:.0f}° / {a.dwell_deg:.0f}° / {360 - a.rise_deg - a.dwell_deg:.0f}° | park in the middle of the dwell: zero holding torque |")
    p(f"| Peak cam torque | {cam['torque_max']:.3f} N·m ({cam['torque_max'] / 9.81e-2:.2f} kg·cm) | includes ×{a.guide_friction:.2f} guide friction |")
    p(f"| Max pressure angle | {cam['phi_max']:.1f}° | limit {a.pressure_max_deg:.0f}° |")
    ok = "ok" if cam["rho_min"] > a.roller_r_mm * MM * 1.5 else "**too sharp: raise the base radius**"
    p(f"| Min radius of curvature (pitch curve) | {cam['rho_min'] / MM:.1f} mm | {ok} against the {a.roller_r_mm:.0f} mm roller |")
    p(f"| Motor margin (JGY370 rated {a.motor_rated_kgcm:.1f} kg·cm) | ×{cam['motor_margin']:.1f} | want ≥ 2 |")
    p(f"| Cock time at {a.motor_rpm:.0f} rpm | {cam['cock_time']:.2f} s | decock (reverse) takes the same |")
    p(f"| Fire latency from the park point | {cam['fire_latency'] * 1e3:.0f} ms | |")
    p(f"| Cam lift / drop | {cam['lift_total'] / MM:.0f} mm | {sp['s'] / MM:.0f} mm stroke + {cam['gap'] / MM:.0f} mm landing gap: "
      "the bumper stops the sled with the follower clear of the cam |")
    p("")
    p(f"Profile files: `cad/launcher/cam_profile.dxf` (layers PITCH, CAM, SHAFT; mm; {a.shaft_d_mm:.0f} mm shaft "
      "circle, add the D-flat in CAD) and `cam_profile.csv` (angle, pitch radius, lift). The cam turns so the "
      "follower meets increasing angle; mirror the outline if your motor turns the other way.")
    p("")
    p("## Pellet channel, shuttle and magazine")
    p("")
    p("| Result | Value | Note |")
    p("| --- | --- | --- |")
    p(f"| Barrel channel (W × H) | {fd['channel_w']:.1f} × {fd['channel_h']:.1f} mm | largest pellet + {a.slide_clearance_mm:.1f} mm; pellet flat, long axis along the barrel |")
    lock = "locked" if fd["flip_margin_long"] > 0.5 else "**may roll: tighten clearance**"
    p(f"| Roll lock margin | {fd['flip_margin_long']:.1f} mm | {lock} (nominal width × thinnest pellet: diagonal minus channel width) |")
    p(f"| Shuttle pocket (L × W × depth) | {fd['pocket_l']:.1f} × {fd['pocket_w']:.1f} × {fd['pocket_depth']:.1f} mm | depth {a.pocket_ratio:.2f} × thickest |")
    ok = "ok" if fd["pocket_depth"] < fd["pocket_limit"] else "**FAILS: two pellets fit**"
    p(f"| Pocket depth vs two thinnest pellets | {fd['pocket_depth']:.1f} < {fd['pocket_limit']:.1f} mm | {ok} |")
    p(f"| Shuttle travel | {fd['shuttle_travel']:.1f} mm | pocket width + {a.shuttle_wall_mm:.0f} mm wall + 1 mm |")
    p(f"| Magazine bore (L × W) | {fd['tube_l']:.1f} × {fd['tube_w']:.1f} mm | pellets stacked flat |")
    p(f"| Stack height for {a.capacity} pellets | {fd['stack_h']:.0f} mm | + follower and spring (~25 mm) |")
    p("")
    p("## Chronograph")
    p("")
    p("| Result | Value | Note |")
    p("| --- | --- | --- |")
    p(f"| Gate spacing | {a.gate_mm:.0f} mm | measure the printed block with the caliper |")
    p(f"| Transit time at {a.v0:.1f} m/s | {ch['transit_ms']:.2f} ms | |")
    p(f"| Error from ±{a.gate_tol_mm:.1f} mm spacing | ±{ch['err_spacing'] * 100:.2f} % | dominant term: calibrate the spacing |")
    p(f"| Error from 1 µs timing (PIO / capture) | {ch['err_1us'] * 100:.3f} % | |")
    p(f"| Error from 50 µs jitter (MicroPython IRQ) | {ch['err_50us'] * 100:.2f} % | acceptable for a 1 % SD target only if averaged; prefer PIO |")
    p("")
    return "\n".join(w) + "\n"


def parse(argv: list[str] | None = None) -> argparse.Namespace:
    q = argparse.ArgumentParser(description="Size the launcher, cam, feed and chronograph for the M2 bench rig.")
    add = q.add_argument
    add("--mass-g", type=float, default=1.45, help="mean pellet mass, g (placeholder until measured)")
    add("--mass-max-g", type=float, default=1.6, help="heaviest pellet the robot is set up for, g")
    add("--length-mm", type=float, default=17.0)
    add("--width-mm", type=float, default=11.0)
    add("--thick-mm", type=float, default=7.0)
    add("--thick-min-mm", type=float, default=6.5)
    add("--thick-max-mm", type=float, default=7.5)
    add("--width-max-mm", type=float, default=11.3, help="widest pellet measured")
    add("--length-max-mm", type=float, default=17.5, help="longest pellet measured")
    add("--v0", type=float, default=6.0, help="target exit speed, m/s")
    add("--sled-g", type=float, default=6.6, help="moving sled incl. 623ZZ follower and axle (cad/bench_rig.py estimate; weigh it)")
    add("--spring-g", type=float, default=2.0)
    add("--loss", type=float, default=0.2, help="fraction of stored energy lost to friction")
    add("--stroke-mm", type=float, default=22.0)
    add("--preload-mm", type=float, default=8.0)
    add("--cap-mj", type=float, default=40.0)
    add("--base-r-mm", type=float, default=12.0, help="cam base-circle radius")
    add("--roller-r-mm", type=float, default=5.0, help="623ZZ outer radius")
    add("--shaft-d-mm", type=float, default=6.0, help="JGY370 output shaft")
    add("--rise-deg", type=float, default=280.0)
    add("--dwell-deg", type=float, default=20.0)
    add("--pressure-max-deg", type=float, default=30.0)
    add("--landing-gap-mm", type=float, default=1.0, help="follower clearance to the base circle after a shot")
    add("--guide-friction", type=float, default=1.25, help="force multiplier for guide friction")
    add("--motor-rated-kgcm", type=float, default=2.0)
    add("--motor-rpm", type=float, default=70.0, help="JGY370 speed under load")
    add("--slide-clearance-mm", type=float, default=0.4)
    add("--pocket-ratio", type=float, default=1.1)
    add("--shuttle-wall-mm", type=float, default=2.0)
    add("--capacity", type=int, default=24)
    add("--gate-mm", type=float, default=60.0)
    add("--gate-tol-mm", type=float, default=0.2)
    add("--report", type=Path, default=Path("docs/mechanical/launcher-sizing.md"))
    add("--cad-dir", type=Path, default=Path("cad/launcher"))
    args = q.parse_args(argv)
    args.cap_speed = lambda: math.sqrt(2 * args.cap_mj * 1e-3 / (args.mass_max_g * G_TO_KG))
    return args


def main(argv: list[str] | None = None) -> None:
    a = parse(argv)
    sp = spring_design(a)
    cam = cam_design(a, sp)
    fd = feed_design(a)
    ch = chrono_design(a)
    pitch = [(r * math.cos(t), r * math.sin(t)) for t, r, _ in cam["pts"]]
    surface = cam_surface(cam["pts"], a.roller_r_mm * MM, math.radians(a.rise_deg + a.dwell_deg))
    write_dxf(a.cad_dir / "cam_profile.dxf", {"PITCH": pitch, "CAM": surface}, a.shaft_d_mm)
    csv = ["angle_deg,pitch_radius_mm,lift_mm"] + [
        f"{math.degrees(t):.2f},{r / MM:.3f},{u / MM:.3f}" for t, r, u in cam["pts"]]
    (a.cad_dir / "cam_profile.csv").write_text("\n".join(csv) + "\n", encoding="ascii")
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(report(a, sp, cam, fd, ch), encoding="utf-8")
    print(f"wrote {a.report}, {a.cad_dir / 'cam_profile.dxf'}, {a.cad_dir / 'cam_profile.csv'}")


if __name__ == "__main__":
    main()
