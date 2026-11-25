#!/usr/bin/env python3
"""DESUU ballistics explorer: sizes the launcher and seeds the aiming lookup table.

A drag-aware, two-dimensional point-mass model of a gum pellet leaving the
launcher. It answers four design questions:

1. Which exit speed should the launcher be built for?
2. How far above the line of sight must the barrel point for each target
   (the seed for the ballistic lookup table that calibration later replaces)?
3. How far does the impact point move for each error source, and what hit
   rate does an error budget give at 1 m?
4. How much over-speed can a shot have before it climbs toward the eyes?

Standard library only:
    python tools/ballistics_sim.py                        # print the report
    python tools/ballistics_sim.py --out docs/research/ballistics.md
    python tools/ballistics_sim.py --help                 # every assumption is a flag

Conventions: origin at the muzzle, x horizontal toward the face, y up.
SI units inside (m, s, rad, kg); mm, mJ and degrees only in the report.
Every number here is a model estimate until chronograph and calibration
shots replace it.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path

G = 9.81  # m/s^2
RHO_AIR = 1.20  # kg/m^3, about 20 C at sea level (a hot room is closer to 1.15)
DT = 1e-3  # s; RK4 step, integration error stays far below 0.1 mm here
HIT_RADIUS_M = 0.015  # brief: land inside a 3 cm circle at 1 m

SPEEDS = (4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5)  # candidate exit speeds, m/s
RANGES = (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)  # slant ranges checked, m
LOS_COLUMNS = (-10, 0, 10, 20, 30)  # line-of-sight elevations in the seed table, deg


@dataclass(frozen=True)
class Pellet:
    mass_kg: float
    area_m2: float  # mean frontal area in flight; a tumbling body shows ~surface/4
    cd: float

    @property
    def k(self) -> float:
        """Drag constant in a = -k * |v| * v, in 1/m."""
        return 0.5 * RHO_AIR * self.cd * self.area_m2 / self.mass_kg


@dataclass(frozen=True)
class Budget:
    """One-sigma error sources. Per-axis values apply vertically and horizontally."""

    name: str
    speed_frac: float  # shot-to-shot exit-speed scatter, fraction of nominal
    aim_deg: float  # pointing error per axis: vision + servo + latency
    launch_deg: float  # pellet exit-direction scatter per axis
    range_frac: float  # distance-estimate error, fraction of true range
    head_mps: float  # residual head speed per axis after the stability gate


@dataclass(frozen=True)
class Impact:
    y: float  # height where the pellet crosses the target plane, m
    tof: float  # time of flight, s
    speed: float  # speed at the target plane, m/s
    path_deg: float  # flight-path angle there; negative means descending


@dataclass(frozen=True)
class Shot:
    """A firing solution plus linearised sensitivities of the impact height."""

    x: float
    y: float
    theta: float  # launch elevation, rad
    impact: Impact
    dy_dspeed: float  # m of impact-height change per unit (100 %) speed error
    dy_dangle: float  # m per rad of elevation error
    dy_drange: float  # m per unit (100 %) range-estimate error

    @property
    def r(self) -> float:
        return math.hypot(self.x, self.y)

    @property
    def los(self) -> float:
        return math.atan2(self.y, self.x)

    @property
    def offset(self) -> float:
        """How far the barrel points above the line of sight, rad."""
        return self.theta - self.los


def fly(v0: float, theta: float, k: float, x_target: float, t_max: float = 3.0) -> Impact | None:
    """Integrate the flight until the pellet reaches x_target (None if it never does)."""
    x = y = t = 0.0
    vx, vy = v0 * math.cos(theta), v0 * math.sin(theta)
    dt, h = DT, DT / 2
    while t < t_max:
        s1 = math.hypot(vx, vy)
        ax1, ay1 = -k * s1 * vx, -G - k * s1 * vy
        vx2, vy2 = vx + h * ax1, vy + h * ay1
        s2 = math.hypot(vx2, vy2)
        ax2, ay2 = -k * s2 * vx2, -G - k * s2 * vy2
        vx3, vy3 = vx + h * ax2, vy + h * ay2
        s3 = math.hypot(vx3, vy3)
        ax3, ay3 = -k * s3 * vx3, -G - k * s3 * vy3
        vx4, vy4 = vx + dt * ax3, vy + dt * ay3
        s4 = math.hypot(vx4, vy4)
        ax4, ay4 = -k * s4 * vx4, -G - k * s4 * vy4
        nx = x + dt / 6 * (vx + 2 * vx2 + 2 * vx3 + vx4)
        ny = y + dt / 6 * (vy + 2 * vy2 + 2 * vy3 + vy4)
        nvx = vx + dt / 6 * (ax1 + 2 * ax2 + 2 * ax3 + ax4)
        nvy = vy + dt / 6 * (ay1 + 2 * ay2 + 2 * ay3 + ay4)
        if nx >= x_target:
            frac = (x_target - x) / (nx - x)
            ivx, ivy = vx + frac * (nvx - vx), vy + frac * (nvy - vy)
            return Impact(
                y=y + frac * (ny - y),
                tof=t + frac * dt,
                speed=math.hypot(ivx, ivy),
                path_deg=math.degrees(math.atan2(ivy, ivx)),
            )
        x, y, vx, vy = nx, ny, nvx, nvy
        t += dt
        if vx <= 1e-6:
            return None
    return None


def height_at(v0: float, theta: float, k: float, x: float) -> float:
    impact = fly(v0, theta, k, x)
    return -math.inf if impact is None else impact.y


def solve_elevation(v0: float, x: float, y: float, k: float) -> float | None:
    """Lowest launch elevation (rad) whose path passes through (x, y); None if out of reach."""
    lo = math.atan2(y, x) - math.radians(25)
    hi = math.radians(65)
    # Golden-section search for the elevation that crosses x highest.
    ratio = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c, d = b - ratio * (b - a), a + ratio * (b - a)
    fc, fd = height_at(v0, c, k, x), height_at(v0, d, k, x)
    for _ in range(30):
        if fc < fd:
            a, c, fc = c, d, fd
            d = a + ratio * (b - a)
            fd = height_at(v0, d, k, x)
        else:
            b, d, fd = d, c, fc
            c = b - ratio * (b - a)
            fc = height_at(v0, c, k, x)
    peak = (a + b) / 2
    if height_at(v0, peak, k, x) < y or height_at(v0, lo, k, x) > y:
        return None
    # Bisection on the rising (low-arc) branch.
    a, b = lo, peak
    for _ in range(32):
        mid = (a + b) / 2
        if height_at(v0, mid, k, x) < y:
            a = mid
        else:
            b = mid
    return (a + b) / 2


def analyse(v0: float, x: float, y: float, k: float) -> Shot | None:
    theta = solve_elevation(v0, x, y, k)
    if theta is None:
        return None
    impact = fly(v0, theta, k, x)
    assert impact is not None
    dv, da, dr = 0.01, math.radians(0.1), 0.01
    dy_dspeed = (height_at(v0 * (1 + dv), theta, k, x) - y) / dv
    dy_dangle = (height_at(v0, theta + da, k, x) - y) / da
    theta_far = solve_elevation(v0, x * (1 + dr), y * (1 + dr), k)
    dy_drange = math.nan if theta_far is None else (height_at(v0, theta_far, k, x) - y) / dr
    return Shot(x, y, theta, impact, dy_dspeed, dy_dangle, dy_drange)


def target(r: float, dh: float) -> tuple[float, float]:
    """Slant range r to a mouth dh above the muzzle, as (x, y)."""
    return math.sqrt(max(r * r - dh * dh, 1e-9)), dh


def target_los(r: float, los_deg: float) -> tuple[float, float]:
    a = math.radians(los_deg)
    return r * math.cos(a), r * math.sin(a)


def sigmas(shot: Shot, b: Budget) -> tuple[float, float, dict[str, float], dict[str, float]]:
    """Linearised 1-sigma impact scatter (vertical, horizontal) and each source's share, m."""
    aim, launch = math.radians(b.aim_deg), math.radians(b.launch_deg)
    head = b.head_mps * shot.impact.tof
    vertical = {
        "exit speed": abs(shot.dy_dspeed) * b.speed_frac,
        "pointing": abs(shot.dy_dangle) * aim,
        "launch scatter": abs(shot.dy_dangle) * launch,
        "range estimate": abs(shot.dy_drange) * b.range_frac,
        "head motion": head,
    }
    horizontal = {
        "exit speed": 0.0,
        "pointing": shot.r * aim,
        "launch scatter": shot.r * launch,
        "range estimate": 0.0,
        "head motion": head,
    }

    def rss(parts: dict[str, float]) -> float:
        return math.sqrt(sum(v * v for v in parts.values()))

    return rss(vertical), rss(horizontal), vertical, horizontal


def gaussian_hit_rate(sy: float, sz: float, n: int = 20000, seed: int = 7) -> float:
    if math.isnan(sy) or math.isnan(sz):
        return math.nan
    rng = random.Random(seed)
    hits = sum(math.hypot(rng.gauss(0, sy), rng.gauss(0, sz)) <= HIT_RADIUS_M for _ in range(n))
    return hits / n


def monte_carlo(v0: float, x: float, y: float, k: float, b: Budget, n: int, seed: int) -> dict[str, float] | None:
    """Full nonlinear shots: the robot solves for its *estimated* range, then errors apply."""
    rng = random.Random(seed)
    grid = [i / 100 for i in range(-20, 21)]
    solutions = [solve_elevation(v0, x * (1 + e), y * (1 + e), k) for e in grid]
    if any(s is None for s in solutions):
        return None
    sols: list[float] = [s for s in solutions if s is not None]

    def elevation_for(err: float) -> float:
        pos = (min(max(err, grid[0]), grid[-1]) - grid[0]) * 100
        i = min(int(pos), len(grid) - 2)
        return sols[i] + (pos - i) * (sols[i + 1] - sols[i])

    nominal = fly(v0, sols[20], k, x)
    assert nominal is not None
    tof = nominal.tof
    r = math.hypot(x, y)
    aim, launch = math.radians(b.aim_deg), math.radians(b.launch_deg)
    misses = []
    for _ in range(n):
        theta = elevation_for(rng.gauss(0, b.range_frac)) + rng.gauss(0, aim) + rng.gauss(0, launch)
        speed = v0 * (1 + rng.gauss(0, b.speed_frac))
        dy = height_at(speed, theta, k, x) - y + rng.gauss(0, b.head_mps) * tof
        dz = r * math.tan(rng.gauss(0, aim) + rng.gauss(0, launch)) + rng.gauss(0, b.head_mps) * tof
        misses.append(math.hypot(dy, dz))
    misses.sort()
    return {
        "hit": sum(m <= HIT_RADIUS_M for m in misses) / n,
        "median": misses[n // 2],
        "r90": misses[int(0.90 * n)],
        "r95": misses[int(0.95 * n)],
    }


def max_overspeed(v0: float, shot: Shot, k: float, allowed_rise: float) -> float:
    """Largest exit-speed excess (fraction) that keeps the impact below the eye zone."""

    def rise(frac: float) -> float:
        return height_at(v0 * (1 + frac), shot.theta, k, shot.x) - shot.y

    if rise(0.5) <= allowed_rise:
        return 0.5
    lo, hi = 0.0, 0.5
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if rise(mid) <= allowed_rise else (lo, mid)
    return lo


def num(v: float | None, nd: int = 1) -> str:
    if v is None or math.isnan(v) or math.isinf(v):
        return "—"
    return f"{v:.{nd}f}"


def pct(v: float | None) -> str:
    return "—" if v is None or math.isnan(v) else f"{v * 100:.0f} %"


def row(*cells: object) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def header(*cells: str) -> list[str]:
    return [row(*cells), row(*["---"] * len(cells))]


def build_report(args: argparse.Namespace) -> str:
    pellet = Pellet(args.mass_g / 1000, args.area_mm2 * 1e-6, args.cd)
    k = pellet.k
    tgt = Budget("target", args.sigma_speed, args.sigma_aim, args.sigma_launch, args.sigma_range, args.sigma_head)
    pes = Budget("pessimistic", 0.02, 0.25, 0.35, 0.06, 0.03)
    allowed = (args.eye_low_mm + args.aim_below_mm) / 1000
    mm = 1000.0
    out: list[str] = []
    w = out.append

    w("# Ballistics model: launcher sizing and error budget")
    w("")
    w("Generated by `tools/ballistics_sim.py`. Re-run it after weighing real pellets and chronographing "
      "the launcher; calibration shots replace every number here.")
    w("")
    w("Model: two-dimensional point mass with quadratic drag, RK4 integration, origin at the muzzle. "
      "The robot measures the line of sight to the mouth (the camera rides on the turret) and the slant "
      "range, then raises the barrel by a ballistic offset above that line of sight.")
    w("")
    w("## Assumptions")
    w("")
    out += header("Parameter", "Value", "Basis")
    w(row("Pellet mass", f"{args.mass_g:.2f} g", "typical pellet gum; weigh 30 of yours"))
    w(row("Mean frontal area", f"{args.area_mm2:.0f} mm²", "between flying flat (~70) and tumbling (~150)"))
    w(row("Drag coefficient", f"{args.cd:.2f}", "blunt body, 0.8–1.2 plausible"))
    w(row("Drag constant k", f"{k:.4f} 1/m", "a = −k·|v|·v"))
    w(row("Mouth above muzzle", f"{args.dh:.2f} m (up to {args.dh_max:.2f} m)", "seated person, desk robot"))
    w(row("Hit circle", f"{HIT_RADIUS_M * 2 * mm:.0f} mm diameter at 1 m", "brief"))
    w(row("Aim point", f"{args.aim_below_mm:.0f} mm below mouth centre", "lands on the tongue, further from the eyes"))
    w(row("Eye zone lower edge", f"{args.eye_low_mm:.0f} mm above mouth centre",
          "eyes sit ~65 mm above the mouth, minus margin; the robot uses live landmarks"))
    w(row("Exit-energy cap", f"{args.ke_cap_mj:.0f} mJ", "conservative; see docs/research/safety-standards.md"))
    w("")
    w("Error budgets (1σ, per axis):")
    w("")
    out += header("Budget", "Exit speed", "Pointing", "Launch scatter", "Range estimate", "Head motion")
    for b in (tgt, pes):
        w(row(b.name, f"{b.speed_frac * 100:.1f} %", f"{b.aim_deg:.2f}°", f"{b.launch_deg:.2f}°",
              f"{b.range_frac * 100:.1f} %", f"{b.head_mps * mm:.0f} mm/s"))
    w("")

    # 1. Exit-speed trade study
    rows = []
    for v0 in SPEEDS:
        s1 = analyse(v0, *target(1.0, args.dh), k)
        s2 = analyse(v0, *target(2.0, args.dh), k)
        s2_hi = analyse(v0, *target(2.0, args.dh_max), k)
        sy_t = sz_t = sy_p = sz_p = math.nan
        if s1:
            sy_t, sz_t, _, _ = sigmas(s1, tgt)
            sy_p, sz_p, _, _ = sigmas(s1, pes)
        safe_range = None
        for r in RANGES:
            s = analyse(v0, *target(r, args.dh), k)
            if s is None or not 3 * sigmas(s, tgt)[0] <= allowed:
                break
            safe_range = r
        rows.append({
            "v0": v0,
            "ke_mj": 0.5 * pellet.mass_kg * v0 ** 2 * 1000,
            "s1": s1, "s2": s2, "s2_hi": s2_hi,
            "sy_t": sy_t, "sz_t": sz_t,
            "hit_t": gaussian_hit_rate(sy_t, sz_t),
            "hit_p": gaussian_hit_rate(sy_p, sz_p),
            "sy2": sigmas(s2, tgt)[0] if s2 else math.nan,
            "over1": max_overspeed(v0, s1, k, allowed) if s1 else math.nan,
            "over2": max_overspeed(v0, s2, k, allowed) if s2 else math.nan,
            "safe_range": safe_range,
        })

    w(f"## 1. Exit-speed trade study (mouth 1.0 m away, {args.dh:.2f} m above the muzzle)")
    w("")
    w("Path at mouth: positive means the pellet is still rising when it reaches the mouth, negative means "
      "it is descending onto the tongue.")
    w("")
    out += header("Exit speed (m/s)", "Exit energy (mJ)", "Elevation (°)", "Above line of sight (°)",
                  "Flight (ms)", "Speed at mouth (m/s)", "Path at mouth (°)", "mm per +1 % speed",
                  "mm per +0.1° aim", "mm per +1 % range", "σ vert / horiz, target (mm)",
                  "Hits in circle, target", "Hits in circle, pessimistic")
    for rw in rows:
        s = rw["s1"]
        if s is None:
            w(row(num(rw["v0"]), num(rw["ke_mj"]), "out of reach", *["—"] * 10))
            continue
        w(row(num(rw["v0"]), num(rw["ke_mj"]), num(math.degrees(s.theta)), num(math.degrees(s.offset)),
              num(s.impact.tof * 1000, 0), num(s.impact.speed, 2), num(s.impact.path_deg),
              num(s.dy_dspeed * 0.01 * mm), num(s.dy_dangle * math.radians(0.1) * mm),
              num(s.dy_drange * 0.01 * mm), f"{num(rw['sy_t'] * mm)} / {num(rw['sz_t'] * mm)}",
              pct(rw["hit_t"]), pct(rw["hit_p"])))
    w("")

    w("## 2. Reach and eye safety")
    w("")
    w(f"*Max over-speed*: how much faster than nominal one shot may leave the barrel (everything else perfect) "
      f"before it lands in the eye zone. *Eye-safe auto-fire range*: the longest range at which 3σ vertical "
      f"scatter (target budget) still leaves {allowed * mm:.0f} mm between the aim point and the eye zone.")
    w("")
    out += header("Exit speed (m/s)", f"Elevation at 2 m, mouth +{args.dh:.2f} m (°)",
                  f"Elevation at 2 m, mouth +{args.dh_max:.2f} m (°)", "σ vert at 2 m, target (mm)",
                  "Max over-speed at 1 m", "Max over-speed at 2 m", "Eye-safe auto-fire range (m)")
    for rw in rows:
        e2 = num(math.degrees(rw["s2"].theta)) if rw["s2"] else "out of reach"
        e2h = num(math.degrees(rw["s2_hi"].theta)) if rw["s2_hi"] else "out of reach"
        over1 = "≥ 50 %" if rw["over1"] >= 0.5 else pct(rw["over1"])
        over2 = "≥ 50 %" if rw["over2"] >= 0.5 else pct(rw["over2"])
        w(row(num(rw["v0"]), e2, e2h, num(rw["sy2"] * mm), over1, over2,
              num(rw["safe_range"], 2) if rw["safe_range"] else "< 0.5"))
    w("")

    # Design to 95 % under the target budget so the 90 % requirement (docs/brief.md, A1)
    # survives a budget that turns out somewhat worse than planned.
    eligible = [
        rw for rw in rows
        if rw["ke_mj"] <= args.ke_cap_mj and rw["s2_hi"] is not None
        and math.degrees(rw["s2_hi"].theta) <= 40.0 and rw["hit_t"] >= args.design_hit_rate
    ]
    if eligible:
        rec = min(eligible, key=lambda rw: rw["v0"])
        why = (f"the lowest speed that stays under the {args.ke_cap_mj:.0f} mJ cap, reaches a mouth "
               f"{args.dh_max:.2f} m up at 2 m below 40° elevation, and gives at least "
               f"{args.design_hit_rate * 100:.0f} % hits at 1 m with the target budget (margin over the 90 % "
               f"requirement). The lowest qualifying speed is preferred because it arrives in the mouth most gently.")
    else:
        capped = [rw for rw in rows if rw["ke_mj"] <= args.ke_cap_mj] or rows
        rec = max(capped, key=lambda rw: 0.0 if math.isnan(rw["hit_t"]) else rw["hit_t"])
        why = "no candidate met every rule; this one has the best 1 m hit rate under the energy cap."
    v0 = args.v0 if args.v0 else rec["v0"]
    w("## Recommendation")
    w("")
    w(f"**Build the launcher for {rec['v0']:.1f} m/s nominal exit speed**: {why}")
    if args.v0 and args.v0 != rec["v0"]:
        w("")
        w(f"(Sections 3–7 below use the requested {v0:.1f} m/s instead.)")
    w("")

    # 3. Error budget at 1 m
    s1 = analyse(v0, *target(1.0, args.dh), k)
    if s1 is None:
        w(f"{v0:.1f} m/s cannot reach 1 m with this geometry; stopping here.")
        return "\n".join(out) + "\n"
    sy, sz, vert, hor = sigmas(s1, tgt)
    w(f"## 3. Error budget at 1.0 m ({v0:.1f} m/s, target budget)")
    w("")
    out += header("Source", "Vertical 1σ (mm)", "Horizontal 1σ (mm)")
    for key in vert:
        w(row(key, num(vert[key] * mm), num(hor[key] * mm)))
    w(row("**Total (RSS)**", f"**{num(sy * mm)}**", f"**{num(sz * mm)}**"))
    w("")
    w(f"For at least 90 % of shots inside the 30 mm circle, a round error needs σ ≤ "
      f"{HIT_RADIUS_M / math.sqrt(2 * math.log(10)) * mm:.1f} mm per axis "
      f"(95 %: σ ≤ {HIT_RADIUS_M / math.sqrt(2 * math.log(20)) * mm:.1f} mm).")
    w("")
    w(f"Full nonlinear Monte Carlo, {args.samples} shots per budget (the robot solves for its *estimated* range):")
    w("")
    out += header("Budget", "Hits inside 30 mm circle", "Median miss (mm)", "90 % of shots within (mm)",
                  "95 % within (mm)")
    for b, seed in ((tgt, args.seed), (pes, args.seed + 1)):
        mc = monte_carlo(v0, s1.x, s1.y, k, b, args.samples, seed)
        if mc is None:
            w(row(b.name, "—", "—", "—", "—"))
            continue
        w(row(b.name, pct(mc["hit"]), num(mc["median"] * mm), num(mc["r90"] * mm), num(mc["r95"] * mm)))
    w("")

    # 4. Eye safety across the range
    w(f"## 4. Eye safety across the range ({v0:.1f} m/s, mouth {args.dh:.2f} m above the muzzle)")
    w("")
    out += header("Range (m)", "Elevation (°)", "Above line of sight (°)", "Flight (ms)", "Path at mouth (°)",
                  "mm per +1 % speed", "σ vert, target (mm)", "3σ (mm)", "Max over-speed", "3σ clears eye zone?")
    for r in RANGES:
        s = analyse(v0, *target(r, args.dh), k)
        if s is None:
            w(row(num(r, 2), "out of reach", *["—"] * 8))
            continue
        sv = sigmas(s, tgt)[0]
        over = max_overspeed(v0, s, k, allowed)
        ok = "yes" if 3 * sv <= allowed else "**no**: lower the aim point or limit auto-fire range"
        w(row(num(r, 2), num(math.degrees(s.theta)), num(math.degrees(s.offset)), num(s.impact.tof * 1000, 0),
              num(s.impact.path_deg), num(s.dy_dspeed * 0.01 * mm), num(sv * mm), num(3 * sv * mm),
              "≥ 50 %" if over >= 0.5 else pct(over), ok))
    w("")

    # 5. Launcher height vs entry angle
    w(f"## 5. Launcher height vs entry angle (1.0 m, {v0:.1f} m/s)")
    w("")
    w("A pellet that is descending as it enters lands on the tongue; one that is still rising heads for the "
      "palate. The higher the muzzle sits relative to the mouth, the flatter or more descending the entry.")
    w("")
    out += header("Mouth above muzzle (m)", "Elevation (°)", "Path at mouth (°)", "Speed at mouth (m/s)",
                  "Flight (ms)")
    for dh in (0.0, 0.1, 0.2, 0.3, 0.4):
        s = analyse(v0, *target(1.0, dh), k)
        if s is None:
            w(row(num(dh, 2), "out of reach", "—", "—", "—"))
            continue
        w(row(num(dh, 2), num(math.degrees(s.theta)), num(s.impact.path_deg), num(s.impact.speed, 2),
              num(s.impact.tof * 1000, 0)))
    w("")

    # 6. Drag uncertainty
    x1, y1 = target(1.0, args.dh)
    w(f"## 6. Why the lookup table must be calibrated: drag uncertainty (1.0 m, {v0:.1f} m/s)")
    w("")
    w("If the table is built with the wrong drag, every shot misses by this much (real drag = nominal):")
    w("")
    out += header("Drag assumed in table", "Elevation used (°)", "Vertical miss (mm)")
    for factor in (0.0, 0.5, 1.0, 1.5, 2.0):
        th = solve_elevation(v0, x1, y1, k * factor)
        if th is None:
            w(row(f"{factor:.1f}× nominal", "—", "—"))
            continue
        w(row(f"{factor:.1f}× nominal", num(math.degrees(th), 2), num((height_at(v0, th, k, x1) - y1) * mm)))
    w("")

    # 7. Seed lookup table
    w(f"## 7. Seed lookup table: barrel offset above the line of sight, degrees ({v0:.1f} m/s)")
    w("")
    w("Rows are slant range to the mouth; columns are the line-of-sight elevation the turret measures. "
      "Calibration shots replace these values (docs/roadmap.md).")
    w("")
    out += header("Range (m)", *[f"LOS {a:+d}°" for a in LOS_COLUMNS], "Flight at LOS +10° (ms)")
    for i in range(16):
        r = 0.5 + 0.1 * i
        cells, tof10 = [], None
        for a in LOS_COLUMNS:
            x, y = target_los(r, a)
            th = solve_elevation(v0, x, y, k)
            cells.append(num(math.degrees(th) - a, 2) if th is not None else "—")
            if a == 10 and th is not None:
                imp = fly(v0, th, k, x)
                tof10 = imp.tof if imp else None
        w(row(num(r, 1), *cells, num(tof10 * 1000, 0) if tof10 else "—"))
    w("")
    w("## Updating this model")
    w("")
    w("1. Weigh 30 pellets on a 0.01 g scale and pass the mean as `--mass-g`; caliper them for `--area-mm2`.")
    w("2. Chronograph 30 shots: mean speed sets `--v0`, the standard deviation sets `--sigma-speed`.")
    w("3. Fit `--cd` so the model matches the measured drop at 1 m and 2 m, then re-run and commit the report.")
    w("")
    return "\n".join(out) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Size the gum launcher and seed the aiming lookup table.")
    p.add_argument("--mass-g", type=float, default=1.4, help="pellet mass, g")
    p.add_argument("--area-mm2", type=float, default=110.0, help="mean frontal area in flight, mm^2")
    p.add_argument("--cd", type=float, default=0.9, help="drag coefficient")
    p.add_argument("--dh", type=float, default=0.25, help="mouth height above the muzzle, m")
    p.add_argument("--dh-max", type=float, default=0.45, help="highest mouth to reach at 2 m, m above muzzle")
    p.add_argument("--v0", type=float, default=None, help="exit speed to detail (default: the recommendation)")
    p.add_argument("--ke-cap-mj", type=float, default=40.0, help="exit-energy cap, mJ")
    p.add_argument("--design-hit-rate", type=float, default=0.95,
                   help="1 m hit rate the recommended speed must reach under the target budget")
    p.add_argument("--eye-low-mm", type=float, default=45.0, help="eye zone lower edge above mouth centre, mm")
    p.add_argument("--aim-below-mm", type=float, default=5.0, help="aim point below mouth centre, mm")
    p.add_argument("--sigma-speed", type=float, default=0.01, help="exit-speed scatter, fraction (1σ)")
    p.add_argument("--sigma-aim", type=float, default=0.12, help="pointing error per axis, deg (1σ)")
    p.add_argument("--sigma-launch", type=float, default=0.15, help="exit-direction scatter per axis, deg (1σ)")
    p.add_argument("--sigma-range", type=float, default=0.025, help="range-estimate error, fraction (1σ)")
    p.add_argument("--sigma-head", type=float, default=0.015, help="residual head speed per axis, m/s (1σ)")
    p.add_argument("--samples", type=int, default=4000, help="Monte Carlo shots per budget")
    p.add_argument("--seed", type=int, default=1, help="random seed")
    p.add_argument("--out", type=Path, default=None, help="write the Markdown report to this file")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    report = build_report(args)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        print(report)


if __name__ == "__main__":
    main()
