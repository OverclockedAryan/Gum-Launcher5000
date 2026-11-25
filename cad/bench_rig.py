#!/usr/bin/env python3
"""DESUU M2 bench rig: parametric CAD (build123d), driven by tools/launcher_design.py.

Every pellet-facing dimension comes from the sizing tool, so after measuring pellets (T0)
re-run this with the same flags and reprint:

    .venv-cad\\Scripts\\python cad/bench_rig.py
    .venv-cad\\Scripts\\python cad/bench_rig.py --mass-g 1.42 --length-mm 16.8 --width-mm 10.9 \\
        --thick-mm 6.9 --thick-min-mm 6.6 --thick-max-mm 7.2 --width-max-mm 11.1 --length-max-mm 17.2

Rig-only options (gearbox size, spring free length, preview on/off) are listed by --help;
any other flag goes to launcher_design.py.

Outputs (cad/bench_rig/): stl/<part>.stl in print orientation, step/<part>.step,
bench_rig_assembly.step (cocked state), preview/*.png, and the report
docs/mechanical/bench-rig-cad.md with masses, hardware and the interference checks.

Frame (mm): X along the barrel (+ toward the muzzle), Y left, Z up. Origin: channel floor,
on the channel centre line, at the push face of the COCKED sled (= rear edge of the breech).
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from build123d import (Box, Compound, Cylinder, Face, Location, Part, Plane, Pos, Rot, Vector, Wire,
                       export_step, export_stl, extrude)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import launcher_design as ld  # noqa: E402

RHO_PETG = 1.27e-3  # g/mm³, solid
SQ2 = math.sqrt(2)


# --------------------------------------------------------------------------- helpers
def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(axis: str, r: float, a0: float, a1: float, p: float, q: float) -> Part:
    """Cylinder of radius r along `axis` from a0 to a1; (p, q) are the other two coordinates in xyz order."""
    m, length = (a0 + a1) / 2, a1 - a0
    if axis == "x":
        return Pos(m, p, q) * Rot(0, 90, 0) * Cylinder(r, length)
    if axis == "y":
        return Pos(p, m, q) * Rot(90, 0, 0) * Cylinder(r, length)
    return Pos(p, q, m) * Cylinder(r, length)


def tear(axis: str, r: float, a0: float, a1: float, p: float, q: float) -> Part:
    """Horizontal hole with a 45° teardrop roof (prints without support), point toward +Z."""
    m, length = (a0 + a1) / 2, a1 - a0
    if axis == "x":
        roof = Pos(m, p, q + r / SQ2) * Rot(45, 0, 0) * Box(length, r, r)
    else:
        roof = Pos(p, m, q + r / SQ2) * Rot(0, 45, 0) * Box(r, length, r)
    return cyl(axis, r, a0, a1, p, q) + roof


def vol_g(part: Part) -> float:
    return part.volume * RHO_PETG


# --------------------------------------------------------------------------- geometry
@dataclass
class Rig:
    """All rig dimensions in mm, derived from the sizing tool plus a few mechanical constants."""
    a: argparse.Namespace
    sp: dict
    cam: dict
    fd: dict

    def __post_init__(self) -> None:
        a, sp, cam, fd = self.a, self.sp, self.cam, self.fd
        mm = 1e3
        self.c = 0.25                                   # sliding clearance per side, printed parts
        self.ch_w, self.ch_h = fd["channel_w"], fd["channel_h"]
        self.pk_l, self.pk_w, self.pk_d = fd["pocket_l"], fd["pocket_w"], fd["pocket_depth"]
        self.travel = fd["shuttle_travel"]
        self.tube_l, self.tube_w = fd["tube_l"], fd["tube_w"]
        self.stroke = sp["s"] * mm
        self.preload = sp["x1"] * mm
        self.delta_cap = sp["delta_cap"] * mm
        self.gap = cam["gap"] * mm
        self.r0 = cam["r0"] * mm
        self.r_cam_max = a.base_r_mm + cam["lift_total"] * mm
        self.za = self.ch_h / 2                         # channel axis = rod axis = roller axis height

        # shuttle: lower walls (pocket), upper ring (bridges over the channel ends)
        self.sh_wx = 3.0                                # ring overhang in X beyond the pocket
        self.sh_wy = a.shuttle_wall_mm                  # -Y wall of the pocket
        self.ring_h = 2.0
        self.tun_x0 = -self.sh_wx - self.c              # upper tunnel zone
        self.tun_x1 = self.pk_l + self.sh_wx + self.c
        self.tun_y0 = -(self.pk_w / 2 + self.sh_wy + self.c)
        self.z_split = self.pk_d + self.ring_h + 0.4    # body top / lid underside

        # sled bay, along X
        self.fw = 6.0                                   # front wall (rod sockets, bumper seat)
        self.fw_x0 = self.tun_x0 - self.fw
        self.bump = 3.0                                 # TPU bumper
        self.sled_front_rest = self.fw_x0 - self.bump
        self.tongue_len = self.stroke - self.sled_front_rest
        self.sb_l = 16.0
        self.sled_rear_rest = self.sled_front_rest - self.sb_l
        self.seat = 1.5                                 # spring seat counterbore depth
        self.spring_free = a.spring_free_mm
        self.spring_rest = self.spring_free - self.preload
        self.bar_t = 6.0
        self.bar_front_nom = self.sled_rear_rest + 2 * self.seat - self.spring_rest
        self.bar_rear_back = self.bar_front_nom - self.bar_t - self.preload     # screw backed out
        self.rw = 8.0
        self.rw_x1 = self.bar_rear_back - 0.5
        self.rw_x0 = self.rw_x1 - self.rw
        self.rod_y = 9.0
        self.rod_blind = 4.0
        self.rod_x1 = self.fw_x0 + self.rod_blind
        self.rod_len = self.rod_x1 - self.rw_x0
        self.x_end = self.stroke + 30.0                 # exit guide after the sled's forward stop
        self.half_w = 12.5                              # barrel half width
        self.boss_h = 3.75                              # sled half height (= tongue half height)
        self.wall_y = self.rod_y + 3.7 + 0.5            # bay +Y wall inner face

        # follower and cam (cam plane beside the sled, -Y side)
        self.roller_y0, self.roller_y1 = -21.0, -17.0   # 623ZZ, 4 mm wide
        self.cam_t = 5.0
        self.cam_y1 = -16.5                             # cam +Y face
        self.cam_y0 = self.cam_y1 - self.cam_t
        self.hub_l, self.hub_r = 6.0, 7.0
        self.roller_x_rest = self.sled_front_rest - self.sb_l / 2
        self.cam_x = self.roller_x_rest + self.r0 + self.gap

        # feed housing (+Y side) and magazine
        self.hx0, self.hx1 = self.tun_x0 - 6.0, self.tun_x1 + 6.0
        self.mag_x, self.mag_y = self.pk_l / 2, self.travel
        self.y_house = self.mag_y + self.tube_w / 2 + 4.0
        self.lid_t = 5.0
        self.lid_top = self.z_split + self.lid_t
        self.mag_h = a.rig_pellets * a.thick_max_mm + 12.0

        # shuttle tab, servo (MG90S, scotch yoke) and return spring
        self.tab_end = self.y_house + 17.0              # at the breech position
        self.pin_y = self.y_house + 6.0
        self.sweep = math.radians(92.0)
        self.horn_r = (self.travel / 2) / math.sin(self.sweep / 2)
        self.slot_x = self.pk_l / 2
        self.horn_x = self.slot_x - self.horn_r * (1 + math.cos(self.sweep / 2)) / 2
        self.horn_y = self.pin_y + self.travel / 2
        self.shelf_top = -9.0                           # servo tab plane (shim to suit)
        self.post_y = self.tab_end + self.travel + 7.5

        # gearbox (JGY370; MEASURE yours: --gearbox-* flags)
        self.gb_x0 = self.cam_x - a.gearbox_shaft_from_motor_end_mm
        self.gb_x1 = self.gb_x0 + a.gearbox_len_mm
        self.gb_y1 = -31.5
        self.gb_y0 = self.gb_y1 - a.gearbox_depth_mm
        self.gb_z0 = self.za - a.gearbox_height_mm / 2

        # stand: pivot near the muzzle, rear lug in an arc slot
        self.piv_x, self.piv_z = self.x_end - 7.0, -12.0
        self.lug_x, self.lug_z = self.rw_x0 + 3.0, -24.0
        self.elev_max = 35.0
        self.base_top = -103.0


# --------------------------------------------------------------------------- parts
def launcher_body(g: Rig) -> Part:
    c = g.c
    # sled bay: floor, rear wall, +Y wall
    b = box(g.rw_x0, g.fw_x0, -g.half_w, g.wall_y + 3, -6, -0.5)
    b += box(g.rw_x0, g.rw_x1, -g.half_w, g.wall_y + 3, -6, g.za + 6)
    b += box(g.rw_x0, g.fw_x0, g.wall_y, g.wall_y + 3, -6, 8)
    # barrel block (front wall + breech + channel), feed housing, front flange, pivot boss
    b += box(g.fw_x0, g.x_end, -g.half_w, g.half_w, -6, g.z_split)
    b += box(g.hx0, g.hx1, g.half_w - 1, g.y_house, -6, g.z_split)
    b += box(g.x_end - 6, g.x_end, -20, 20, -6, g.z_split)
    b += box(g.piv_x - 9, g.x_end, -20, 20, -18, -6)
    # rear lug for the elevation quadrant
    b += box(g.rw_x0, g.rw_x0 + 6, 8.2, g.wall_y + 3, -30, -6)
    # servo shelf, joined under the feed housing, plus the return-spring post
    sx0, sx1 = g.horn_x - 10, g.slot_x + 3.5
    b += box(sx0, sx1, g.y_house - 6, g.y_house, -13, -6)
    b += box(sx0, sx1, g.y_house - 0.01, g.post_y + 4, -13, g.shelf_top)
    b += cyl("z", 2.0, g.shelf_top, 8.0, g.slot_x, g.post_y)

    # channel (through, incl. the tongue hole in the front wall) and open top in front of the breech
    b -= box(g.fw_x0 - 1, g.x_end + 1, -g.ch_w / 2, g.ch_w / 2, 0, g.ch_h)
    b -= box(g.tun_x1, g.x_end + 1, -g.ch_w / 2, g.ch_w / 2, 0, g.z_split + 1)
    # shuttle tunnel: lower zone = pocket length, upper zone = ring
    b -= box(-c, g.pk_l + c, g.tun_y0, g.y_house + 1, 0, g.pk_d + 0.2)
    b -= box(g.tun_x0, g.tun_x1, g.tun_y0, g.y_house + 1, g.pk_d - 0.2, g.z_split + 1)
    # 45° lead-in where the breech (tall) meets the channel ceiling
    b -= Pos(g.pk_l + c, 0, g.ch_h) * Rot(0, 45, 0) * Box(1.2, g.ch_w, 1.2)
    # chamber IR emitter: 5 mm LED pocket from below, 2 mm aperture
    b -= cyl("z", 2.6, -7, -2, g.pk_l / 2, 0) + cyl("z", 1.0, -3, 0.1, g.pk_l / 2, 0)
    # rods: through the rear wall, blind sockets in the front wall
    for y in (-g.rod_y, g.rod_y):
        b -= tear("x", 1.5, g.rw_x0 - 1, g.rw_x1 + 1, y, g.za)
        b -= tear("x", 1.5, g.fw_x0 - 1, g.rod_x1, y, g.za)
    # preload screw: M3 insert from the rear face, clearance through
    b -= tear("x", 2.0, g.rw_x0 - 1, g.rw_x0 + 5, 0, g.za) + tear("x", 1.7, g.rw_x0, g.rw_x1 + 1, 0, g.za)
    # preload bar tab pocket: its front wall is the HARD STOP (REQ-SAF-003)
    b -= box(g.bar_front_nom - 3 - g.preload - 0.3, g.bar_front_nom + g.delta_cap, -3.3, 3.3, -3.8, 0)
    # heat-set inserts (4.0 mm) for the lid, magazine, chrono sleeve, motor mount
    for x, y in g.lid_screws:
        b -= cyl("z", 2.0, g.z_split - 5, g.z_split + 1, x, y)
    for y in (-16.5, 16.5):
        b -= tear("x", 2.0, g.x_end - 6, g.x_end + 1, y, 1.3)
    for x in (-75.0, -50.0):
        b -= cyl("z", 2.0, -7, -1, x, -8)
    # pivot and lug holes (M5)
    b -= tear("y", 2.65, -21, 21, g.piv_x, g.piv_z)
    b -= tear("y", 2.65, 7, g.wall_y + 4, g.lug_x, g.lug_z)
    # servo pocket (MG90S drops in from above, tabs on the shelf) and its screw holes
    b -= box(g.horn_x - 6.3, g.horn_x + 6.3, g.horn_y - 6.3, g.horn_y + 16.9, -14, g.shelf_top + 1)
    for y in (g.horn_y - 8.6, g.horn_y + 19.2):
        b -= cyl("z", 0.95, -14, g.shelf_top + 1, g.horn_x, y)
    return b


def lid(g: Rig) -> Part:
    p = box(g.fw_x0, g.x_end, -g.half_w, g.half_w, g.z_split, g.lid_top)
    p += box(g.hx0, g.hx1, g.half_w - 1, g.y_house, g.z_split, g.lid_top)
    # ceiling rib: channel height ahead of the breech; ironed when printed upside down
    p += box(g.tun_x1, g.x_end, -g.ch_w / 2 + 0.15, g.ch_w / 2 - 0.15, g.ch_h, g.z_split + 0.01)
    # magazine opening = the shuttle window under the stack, with a lead-in
    p -= box(0, g.pk_l, g.mag_y - g.pk_w / 2, g.mag_y + g.pk_w / 2, g.z_split - 1, g.lid_top + 1)
    for x, y in g.lid_screws:
        p -= cyl("z", 1.7, g.z_split - 1, g.lid_top + 1, x, y)
    # chamber IR receiver: 2 mm aperture, 5 mm photodiode pocket from the top
    p -= cyl("z", 1.0, g.z_split - 1, g.lid_top, g.pk_l / 2, 0)
    p -= cyl("z", 2.6, g.z_split + 1, g.lid_top + 1, g.pk_l / 2, 0)
    return p


def sled(g: Rig) -> Part:
    """In the REST position (pushed forward against the bumper)."""
    f, r, za, h = g.sled_front_rest, g.sled_rear_rest, g.za, g.boss_h
    s = box(r, f, g.rod_y - 3.7, g.rod_y + 3.7, za - h, za + h)
    s += box(r, f, -g.rod_y - 3.7, -g.rod_y + 3.7, za - h, za + h)
    s += box(f - 4, f, -5.4, 5.4, za - h, za + h)                 # front bridge (carries the tongue)
    s += box(r, f, -5.4, 5.4, za - h, za - h + 2)                 # floor plate
    th = g.ch_h - 0.4                                              # tongue height = push face height
    s += box(f - 1, f + g.tongue_len - 3, -1.5, 1.5, za - th / 2, za + th / 2)
    s += box(f + g.tongue_len - 3, f + g.tongue_len, -(g.ch_w - 0.4) / 2, (g.ch_w - 0.4) / 2,
             za - th / 2, za + th / 2)
    # follower arm (-Y) with the 623ZZ axle and an inner-race spacer
    rx = g.roller_x_rest
    s += box(rx - 6, rx + 6, -g.rod_y - 6.5, -g.rod_y - 3.0, za - h, za + h)
    s += cyl("y", 2.75, g.roller_y1, -g.rod_y - 6.4, rx, za)
    s -= cyl("y", 1.45, g.roller_y1 - 1, -g.rod_y - 2.3, rx, za)  # M3 x 10 axle, self-tapping (stops short of the bore)
    for y in (-g.rod_y, g.rod_y):
        s -= tear("x", 1.6, r - 1, f + 1, y, za)                   # 3.2 mm sliding bore
        s -= cyl("x", 3.4, r - 1, r + g.seat, y, za)               # spring seat
    return s


def preload_bar(g: Rig) -> Part:
    """At the nominal preload (screw at its design point)."""
    x1 = g.bar_front_nom
    x0 = x1 - g.bar_t
    p = box(x0, x1, -g.rod_y - 3.7, g.rod_y + 3.7, 0, g.za + 4.5)
    p += box(x1 - 3, x1, -3, 3, -3.5, 0.01)                        # tab: rides in the hard-stop pocket
    for y in (-g.rod_y, g.rod_y):
        p -= cyl("x", 1.65, x0 - 1, x1 + 1, y, g.za)
        p -= cyl("x", 3.4, x1 - g.seat, x1 + 1, y, g.za)
    return p


def bumper(g: Rig) -> Part:
    p = box(g.fw_x0 - g.bump, g.fw_x0, -g.half_w, g.half_w, -0.5, g.za + 5)
    p -= box(g.fw_x0 - g.bump - 1, g.fw_x0 + 1, -g.ch_w / 2, g.ch_w / 2, 0, g.ch_h)
    for y in (-g.rod_y, g.rod_y):
        p -= cyl("x", 1.7, g.fw_x0 - g.bump - 1, g.fw_x0 + 1, y, g.za)
    return p


def shuttle(g: Rig) -> Part:
    """At the BREECH position (window over the channel)."""
    y0, top = -(g.pk_w / 2 + g.sh_wy), g.pk_d + g.ring_h
    p = box(0, g.pk_l, y0, g.tab_end, 0, g.pk_d + 0.01)                              # lower walls
    p += box(-g.sh_wx, g.pk_l + g.sh_wx, y0, g.tab_end, g.pk_d, top)                  # upper ring
    p += box(-g.sh_wx, g.pk_l + g.sh_wx, g.y_house + 1, g.tab_end, 0, top)           # tab, full section
    p -= box(-g.sh_wx - 1, g.pk_l + g.sh_wx + 1, -g.pk_w / 2, g.pk_w / 2, -1, g.pk_d + 0.01)
    p -= box(0, g.pk_l, -g.pk_w / 2, g.pk_w / 2, g.pk_d - 1, top + 1)                # open roof
    # 45° lead-in on the window's trailing top edge: on a load stroke the next pellet in the stack
    # (resting on the pocketed one, as low as the thinnest pellet) rides up onto the shuttle instead
    # of being hit side-on (D-006)
    h = top - g.a.thick_min_mm + 0.3
    p -= Pos(g.pk_l / 2, g.pk_w / 2, top) * Rot(45, 0, 0) * Box(g.pk_l + 2 * g.sh_wx + 2, h * SQ2, h * SQ2)
    # scotch-yoke slot for the horn pin (M2), and the return-spring hole
    dx = g.horn_r * (1 - math.cos(g.sweep / 2)) + 2.4
    p -= box(g.slot_x - dx / 2, g.slot_x + dx / 2, g.pin_y - 1.15, g.pin_y + 1.15, -1, top + 1)
    p -= cyl("z", 1.1, -1, top + 1, g.slot_x, g.tab_end - 3.0)
    return p


def magazine(g: Rig) -> Part:
    z0 = g.lid_top
    wl, ww = g.tube_l / 2 + 2.4, g.tube_w / 2 + 2.4
    p = box(g.mag_x - wl, g.mag_x + wl, g.mag_y - ww, g.mag_y + ww, z0, z0 + g.mag_h)
    p += box(g.hx0, g.hx1, g.mag_y - 7.5, g.mag_y + 7.5, z0, z0 + 3)
    p -= box(g.mag_x - g.tube_l / 2, g.mag_x + g.tube_l / 2, g.mag_y - g.tube_w / 2, g.mag_y + g.tube_w / 2,
             z0 - 1, z0 + g.mag_h + 1)
    p -= box(g.mag_x - 1.5, g.mag_x + 1.5, g.mag_y, g.mag_y + ww + 1, z0 + 8, z0 + g.mag_h - 6)  # view slot
    for x, y in g.mag_screws:
        p -= cyl("z", 1.7, z0 - 1, z0 + 4, x, y)
    return p


def chrono_sleeve(g: Rig) -> Part:
    x0, x1 = g.x_end, g.x_end + 80
    bw, b0, b1 = g.ch_w / 2 + 1, -1.0, g.ch_h + 1
    p = box(x0, x1, -g.half_w, g.half_w, b0 - 10, b1 + 10)
    p += box(x0, x0 + 6, -20, 20, b0 - 10, b1 + 10)
    p -= box(x0 - 1, x1 + 1, -bw, bw, b0, b1)
    for y in (-16.5, 16.5):
        p -= cyl("x", 1.7, x0 - 1, x0 + 7, y, 1.3) + cyl("x", 3.0, x0 + 3, x0 + 7, y, 1.3)
    for gx in (x0 + 10, x0 + 10 + g.a.gate_mm):
        p -= box(gx - 0.75, gx + 0.75, -g.ch_w / 2, g.ch_w / 2, b0 - 4.01, b1 + 4.01)   # 1.5 mm slits
        p -= cyl("z", 2.6, b1 + 4, b1 + 11, gx, 0) + cyl("z", 2.6, b0 - 11, b0 - 4, gx, 0)
    return p


def cam_local(g: Rig) -> tuple[Part, float]:
    """Cam in its own frame (profile in XY, extruded +Z, hub on +Z). Returns (part, flag angle deg)."""
    a, cam = g.a, g.cam
    surf = ld.cam_surface(cam["pts"], a.roller_r_mm * 1e-3, math.radians(a.rise_deg + a.dwell_deg))
    pts = [Vector(x * 1e3, y * 1e3, 0) for x, y in surf]
    p = extrude(Face(Wire.make_polygon(pts, close=True)), amount=g.cam_t)
    p += Pos(0, 0, g.cam_t + g.hub_l / 2) * Cylinder(g.hub_r, g.hub_l)
    # ready flag on the hub: points along world +X when parked mid-dwell
    th_park = a.rise_deg + a.dwell_deg / 2
    flag = (0.0 - (180.0 - th_park)) % 360            # theta_f = world angle (+X) - psi_park
    p += Rot(0, 0, flag) * box(g.hub_r - 1, 14, -1.5, 1.5, g.cam_t, g.cam_t + g.hub_l)
    # D-bore for the 6 mm shaft (flat 0.5 deep) and an M3 set-screw insert onto the flat
    d_flat = 200.0
    bore = Pos(0, 0, g.cam_t) * Cylinder(3.1, 30) - Rot(0, 0, d_flat) * box(2.6, 10, -10, 10, -20, 20)
    p -= bore
    p -= Rot(0, 0, d_flat) * (Pos(0, 0, g.cam_t + g.hub_l / 2) * Rot(0, 90, 0) * Pos(0, 0, 6) * Cylinder(2.0, 8))
    return p, flag


def place_cam(g: Rig, cam_part: Part, theta_contact_deg: float) -> Part:
    """Rotate so the cam-frame angle theta_contact faces the follower (world -X), then map to the XZ plane."""
    psi = 180.0 - theta_contact_deg
    frame = Plane(origin=(g.cam_x, g.cam_y1, g.za), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return frame.location * (Rot(0, 0, psi) * cam_part)


def motor_mount(g: Rig) -> Part:
    a = g.a
    p = box(g.rw_x0, -45, -58.5, -2, -16, -6)                              # plate under the sled bay
    fl0 = g.gb_z0 - 0.0
    p += box(-45, g.gb_x1 + 3.4, g.gb_y0 - 3.5, g.gb_y1 + 3.0, -16, fl0)   # gearbox floor
    p += box(g.gb_x1 + 0.4, g.gb_x1 + 3.4, g.gb_y0 - 3.5, g.gb_y1, -16, g.za - 4)   # X stop
    # switch wall: locates the gearbox face in Y and carries the KW4 "ready" switch
    sw0, sw1 = g.cam_x + 10.0, g.cam_x + 38.0
    p += box(sw0, sw1, g.gb_y1, g.gb_y1 + 3.0, -16, g.za + 6)
    p += box(g.gb_x1 + 0.4, sw1, g.gb_y1 - 3.5, g.gb_y1 + 3.0, -16, fl0)
    sx = g.cam_x + 25.0
    for dx in (-4.75, 4.75):                                               # slotted M2 pilot holes
        for k in range(7):
            p -= cyl("y", 0.9, g.gb_y1 - 1, g.gb_y1 + 4, sx + dx - 1.5 + k * 0.5, g.za - 9.4)
    # zip-tie slots either side of the gearbox, clear of the output shaft
    for x in (g.gb_x0 + 8.0, g.cam_x + 6.0):
        for y in (g.gb_y1 + 1.2, g.gb_y0 - 1.2):
            p -= box(x - 2.25, x + 2.25, y - 0.9, y + 0.9, -17, fl0 + 1)
    for x in (-75.0, -50.0):                                               # M3 up into the body inserts
        p -= cyl("z", 1.7, -17, -5, x, -8) + cyl("z", 3.0, -17, -13, x, -8)
    del a
    return p


def stand(g: Rig) -> Part:
    bt = g.base_top
    p = box(-108, 62, -66, 70, bt - 4, bt)
    for y0, y1 in ((-25.4, -20.4), (20.4, 25.4)):                          # cheeks with the pivot
        p += box(g.piv_x - 9, g.piv_x + 9, y0, y1, bt - 0.01, g.piv_z)
        p += cyl("y", 9.0, y0, y1, g.piv_x, g.piv_z)
        p -= tear("y", 2.65, y0 - 1, y1 + 1, g.piv_x, g.piv_z)
    # rear quadrant with the arc slot for the lug bolt (0–35°)
    qy0, qy1 = g.wall_y + 4.0, g.wall_y + 9.0
    p += box(-108, -38, qy0, qy1, bt - 0.01, -12)
    dx, dz = g.lug_x - g.piv_x, g.lug_z - g.piv_z
    rad, phi0 = math.hypot(dx, dz), math.atan2(dz, dx)
    steps = 36
    for k in range(steps + 1):
        ph = phi0 + math.radians(g.elev_max) * k / steps
        p -= cyl("y", 2.75, qy0 - 1, qy1 + 1, g.piv_x + rad * math.cos(ph), g.piv_z + rad * math.sin(ph))
    for deg in range(0, int(g.elev_max) + 1, 5):                           # scale: ticks every 5°
        ph = phi0 + math.radians(deg)
        rr = rad + 6.5 + (1.5 if deg % 10 == 0 else 0)
        tick = Pos(g.piv_x + rr * math.cos(ph), qy1, g.piv_z + rr * math.sin(ph)) * \
            Rot(0, -math.degrees(ph), 0) * Box(4 + (3 if deg % 10 == 0 else 0), 1.2, 0.8)
        p -= tick
    for x in (-100, 54):
        for y in (-58, 62):
            p -= cyl("z", 2.2, bt - 5, bt + 1, x, y)
    return p


def pellet_gauge(g: Rig) -> Part:
    """Assembly step 1: slots for width (11.0–12.0) and thickness (6.4–8.0), 0.2 mm steps."""
    widths = [11.0 + 0.2 * i for i in range(6)]
    thicks = [6.4 + 0.2 * i for i in range(9)]
    p = box(0, 8 + 16 * len(thicks), 0, 46, 0, 4)
    for i, w in enumerate(widths):
        p -= box(4 + i * 24, 4 + i * 24 + w, 26, 47, -1, 5)
    for i, t in enumerate(thicks):
        p -= box(6 + i * 16, 6 + i * 16 + t, -1, 20, -1, 5)
    return p


def clearance_coupon(g: Rig) -> Part:
    """Rod holes (vertical and teardrop), 623ZZ/608ZZ bores, insert holes: pick the sizes that fit."""
    p = box(0, 132, 0, 40, 0, 10)
    for i, d in enumerate((2.9, 3.0, 3.1, 3.2, 3.3, 3.4)):
        p -= cyl("z", d / 2, -1, 11, 8 + i * 9, 8)
        p -= tear("y", d / 2, 26, 41, 8 + i * 9, 5)
    for i, d in enumerate((9.9, 10.0, 10.1, 21.9, 22.0)):
        p -= cyl("z", d / 2, 4, 11, 62 + (i if i < 3 else 0) * 13 + (0 if i < 3 else (i - 3) * 26), 8 if i < 3 else 26)
    for i, d in enumerate((3.8, 4.0, 4.2)):
        p -= cyl("z", d / 2, 5, 11, 110 + i * 9, 26)
    return p


# --------------------------------------------------------------------------- hardware dummies
def hardware(g: Rig, cocked: bool) -> dict[str, Part]:
    dx = -g.stroke if cocked else 0.0
    rx = g.roller_x_rest + dx
    hw = {
        "rods": cyl("x", 1.5, g.rw_x0, g.rod_x1, g.rod_y, g.za) + cyl("x", 1.5, g.rw_x0, g.rod_x1, -g.rod_y, g.za),
        "roller_623": cyl("y", 5.0, g.roller_y0, g.roller_y1, rx, g.za),
        "mg90s": box(g.horn_x - 6.1, g.horn_x + 6.1, g.horn_y - 6.1, g.horn_y + 16.7, -32, g.shelf_top + 4.5)
                 + box(g.horn_x - 6.1, g.horn_x + 6.1, g.horn_y - 10.95, g.horn_y + 21.55, g.shelf_top, g.shelf_top + 2.5),
        "gearbox": box(g.gb_x0, g.gb_x1, g.gb_y0, g.gb_y1, g.gb_z0, g.gb_z0 + g.a.gearbox_height_mm),
        "motor_can": cyl("x", 12.2, g.gb_x0 - 30.8, g.gb_x0, (g.gb_y0 + g.gb_y1) / 2, g.za - 4),
        "shaft": cyl("y", 3.0, g.gb_y1 - 0.01, g.gb_y1 + 14.0, g.cam_x, g.za),
    }
    seat_s = g.sled_rear_rest + dx + g.seat
    seat_b = g.bar_front_nom - g.seat
    for y in (-g.rod_y, g.rod_y):
        hw[f"spring_{'L' if y > 0 else 'R'}"] = cyl("x", 3.0, seat_b, seat_s, y, g.za) - cyl("x", 2.5, seat_b - 1, seat_s + 1, y, g.za)
    return hw


# --------------------------------------------------------------------------- checks and report
def checks(g: Rig, parts: dict[str, Part], cam_l: Part) -> list[tuple[str, str, bool]]:
    out: list[tuple[str, str, bool]] = []

    def overlap(name: str, a: Part, b: Part, tol: float = 0.05) -> None:
        v = (a & b).volume
        out.append((name, f"{v:.2f} mm³ overlap", v <= tol))

    def gap(name: str, a: Part, b: Part, lo: float, hi: float = 1e9) -> None:
        d = a.distance_to(b)
        out.append((name, f"{d:.2f} mm", lo - 1e-3 <= d <= hi))

    th_rest = (g.a.rise_deg + g.a.dwell_deg + 360) / 2           # mid-landing
    th_park = g.a.rise_deg + g.a.dwell_deg / 2
    for state, dx, sy, th in (("rest", 0.0, g.travel, th_rest), ("cocked", -g.stroke, 0.0, th_park)):
        sl = Pos(dx, 0, 0) * parts["sled"]
        sh = Pos(0, sy, 0) * parts["shuttle"]
        cm = place_cam(g, cam_l, th)
        hw = hardware(g, state == "cocked")
        for other in ("launcher_body", "lid", "bumper", "preload_bar", "motor_mount"):
            overlap(f"{state}: sled vs {other}", sl, parts[other])
        overlap(f"{state}: sled vs rods", sl, hw["rods"])
        for other in ("launcher_body", "lid", "magazine"):
            overlap(f"{state}: shuttle vs {other}", sh, parts[other])
        overlap(f"{state}: shuttle vs sled", sh, sl)
        for other in ("launcher_body", "lid", "bumper", "motor_mount", "stand", "chrono_sleeve"):
            overlap(f"{state}: cam vs {other}", cm, parts[other])
        overlap(f"{state}: cam vs sled", cm, sl)
        if state == "rest":
            gap("rest: roller to cam (landing gap)", hw["roller_623"], cm, g.gap - 0.15, g.gap + 0.4)
        else:
            gap("cocked: roller to cam (contact)", hw["roller_623"], cm, -0.01, 0.3)
    # swept cam disk against everything fixed
    disk = cyl("y", g.r_cam_max + 0.5, g.cam_y0, g.cam_y1, g.cam_x, g.za)
    for other in ("launcher_body", "lid", "bumper", "stand", "chrono_sleeve"):
        overlap(f"swept cam vs {other}", disk, parts[other])
    overlap("swept cam vs motor_mount", disk, parts["motor_mount"])
    hw = hardware(g, False)
    overlap("gearbox vs motor_mount", hw["gearbox"], parts["motor_mount"])
    overlap("gearbox vs launcher_body", hw["gearbox"], parts["launcher_body"])
    overlap("MG90S vs launcher_body", hw["mg90s"], parts["launcher_body"])
    overlap("magazine vs lid", parts["magazine"], parts["lid"])
    overlap("lid vs launcher_body", parts["lid"], parts["launcher_body"])
    overlap("motor_mount vs launcher_body", parts["motor_mount"], parts["launcher_body"])
    # stand against the launcher swinging through 0..35°
    launcher = Compound(children=[parts[n] for n in ("launcher_body", "lid", "motor_mount", "magazine",
                                                     "chrono_sleeve")] + [hw["gearbox"], hw["motor_can"], hw["mg90s"]])
    disk_l = disk
    for e in (0, 12, 24, 35):
        rot = Pos(g.piv_x, 0, g.piv_z) * Rot(0, -e, 0) * Pos(-g.piv_x, 0, -g.piv_z)
        overlap(f"stand vs launcher at {e}°", parts["stand"], rot * launcher, tol=1.0)
        overlap(f"stand vs swept cam at {e}°", parts["stand"], rot * disk_l)
    return out


def report(g: Rig, parts: dict[str, Part], res: list, masses: dict) -> str:
    a = g.a
    w: list[str] = []
    p = w.append
    p("# M2 bench rig: generated CAD")
    p("")
    p("Generated by `cad/bench_rig.py` from the numbers in [launcher-sizing.md](launcher-sizing.md); "
      "design intent in [bench-rig.md](bench-rig.md). Re-run both after measuring pellets (T0). "
      "**Pellet geometry is a placeholder until then.**")
    p("")
    p("Files: `cad/bench_rig/stl/` (print orientation), `cad/bench_rig/step/` (per part, assembly frame), "
      "`cad/bench_rig/bench_rig_assembly.step` (cocked, shuttle at the breech), `cad/bench_rig/preview/`, and the animated 3D viewer `cad/bench_rig/web/launcher.html` (meshes in `meshes.json`, motion data in `rig.json`).")
    p("")
    p("## Parts")
    p("")
    p("| Part | Material | Qty | Size (mm) | Mass, solid (g) | Print |")
    p("| --- | --- | --- | --- | --- | --- |")
    info = {
        "launcher_body": ("PETG natural, stainless nozzle", "Floor down; channel floor is an upward-facing surface: ironing on"),
        "lid": ("PETG natural, stainless nozzle", "Upside down (rib up, ironed)"),
        "sled": ("PETG", "Flat on its bottom; bores are teardrops: ream to 3.2 mm"),
        "preload_bar": ("PETG", "On its rear face"),
        "bumper": ("TPU 95A", "Flat"),
        "shuttle": ("PETG natural, stainless nozzle", "Upside down (sliding face up, ironed)"),
        "magazine": ("PETG clear", "Upright"),
        "cam": ("PETG or ASA", "Flat, hub up; 6 walls"),
        "chrono_sleeve": ("PETG **black**", "Flat; slits print vertical"),
        "motor_mount": ("PETG", "Flat"),
        "stand": ("PLA+ or PETG", "Flat"),
        "pellet_gauge": ("any", "Flat; print first"),
        "clearance_coupon": ("PETG", "Flat; print first"),
    }
    for name, part in parts.items():
        bb = part.bounding_box()
        mat, how = info[name]
        p(f"| `{name}` | {mat} | 1 | {bb.size.X:.0f} × {bb.size.Y:.0f} × {bb.size.Z:.0f} | {masses[name]:.1f} | {how} |")
    p("")
    p("## Key dimensions (from the sizing tool)")
    p("")
    p("| Feature | Value |")
    p("| --- | --- |")
    p(f"| Channel (W × H) | {g.ch_w:.1f} × {g.ch_h:.1f} mm, axis {g.za:.2f} mm above the floor |")
    p(f"| Breech window / shuttle pocket | {g.pk_l:.1f} × {g.pk_w:.1f} × {g.pk_d:.2f} mm; travel {g.travel:.1f} mm |")
    p(f"| Sled stroke | {g.stroke:.0f} mm; push face at x = 0 (cocked) and x = {g.stroke:.0f} (rest) |")
    p(f"| Tongue | {g.tongue_len:.1f} mm long, push face {g.ch_w - 0.4:.1f} × {g.ch_h - 0.4:.1f} mm |")
    p(f"| Guide rods | 2 × ⌀3 × **{g.rod_len:.1f} mm**, {2 * g.rod_y:.0f} mm apart |")
    p(f"| Springs | free length {g.spring_free:.0f} mm assumed; {g.spring_rest:.0f} mm at rest, "
      f"{g.spring_rest - g.stroke:.0f} mm cocked, {g.spring_rest - g.stroke - g.delta_cap:.1f} mm cocked at the hard stop: "
      "it must stay longer than the solid length (coils × wire) |")
    p(f"| Preload screw | M3 × 25 through an insert in the rear wall; travel {g.preload:.0f} mm back to "
      f"+{g.delta_cap:.1f} mm forward, where the bar's tab hits the printed hard stop |")
    p(f"| Cam | ⌀{2 * g.r_cam_max:.0f} × {g.cam_t:.0f} mm, hub ⌀{2 * g.hub_r:.0f} × {g.hub_l:.0f}; centre "
      f"{g.cam_x - g.roller_x_rest:.0f} mm ahead of the roller at rest |")
    p(f"| Shuttle drive | MG90S horn radius {g.horn_r:.1f} mm, ±{math.degrees(g.sweep) / 2:.0f}° sweep (scotch yoke, M2 pin) |")
    p(f"| Magazine | {a.rig_pellets} pellets, bore {g.tube_l:.1f} × {g.tube_w:.1f} mm, {g.mag_h:.0f} mm tall |")
    p(f"| Chronograph | gates {a.gate_mm:.0f} mm apart, 1.5 mm slits; bore 1 mm clear of the channel all round |")
    p("")
    sled_hw = masses["sled_hw"]
    p("## Sled mass")
    p("")
    p(f"Printed sled {masses['sled']:.1f} g (solid PETG) + 623ZZ, M3 × 10 axle screw and nut (≈ {sled_hw:.1f} g, estimate) = "
      f"**{masses['sled'] + sled_hw:.1f} g** moving, against `--sled-g {a.sled_g}` in the sizing tool. "
      + ("Matches." if abs(masses['sled'] + sled_hw - a.sled_g) <= 0.1 * a.sled_g else
         "**Re-run `tools/launcher_design.py --sled-g` with the weighed sled.**"))
    p("")
    p("## Interference and clearance checks")
    p("")
    p("Rest = sled forward on the bumper, shuttle under the stack, cam mid-landing. Cocked = sled back, cam parked "
      "mid-dwell, shuttle at the breech. Hardware is modelled as simple solids (rods, 623ZZ, MG90S, gearbox).")
    p("")
    p("| Check | Result | |")
    p("| --- | --- | --- |")
    for name, val, ok in res:
        p(f"| {name} | {val} | {'ok' if ok else '**FAIL**'} |")
    p("")
    p("## Hardware for the rig")
    p("")
    p("| Item | Qty | Use |")
    p("| --- | --- | --- |")
    p(f"| ⌀3 mm steel rod, {g.rod_len:.1f} mm | 2 | Sled guides (press fit both ends) |")
    p("| 623ZZ | 1 | Cam follower, on an M3 × 10 screw self-tapped into the arm |")
    p("| M3 heat-set insert | 13 | Lid (5), magazine (2), chrono sleeve (2), motor mount (2), preload screw (1), cam set screw (1) |")
    p("| M3 screws | ≈ 12 | M3 × 10 for the lid and mount, M3 × 12 for the magazine (through the lid), M3 × 25 preload screw, M3 × 4 set screw |")
    p("| M5 × 60 bolt + nut, M5 × 25 bolt + wing nut, washers | 1 + 1 | Pivot and elevation lock (**not on BOM v1**, about ₹40) |")
    p("| M2 × 10 screw | 1 + 2 | Horn pin into the shuttle slot; KW4 switch |")
    p("| Extension spring, about 10 mm body | 1 | Shuttle return (post on the servo shelf) |")
    p("| Zip ties, 3.6 mm | 2 | Gearbox to the motor mount |")
    p("| 5 mm IR LED + photodiode | 3 pairs | Chamber sensor (body below, lid above), two chronograph gates |")
    p("")
    p("## Assumed and to measure")
    p("")
    p(f"- **JGY370 gearbox:** modelled as {a.gearbox_len_mm:.0f} × {a.gearbox_height_mm:.0f} × {a.gearbox_depth_mm:.0f} mm "
      f"with the output shaft {a.gearbox_shaft_from_motor_end_mm:.0f} mm from the motor end, centred in height; "
      "the motor can points to the rear. Sellers don't publish the hole pattern, so it's held by two zip ties against "
      "printed stops. Measure yours and re-run with `--gearbox-len-mm`, `--gearbox-height-mm`, `--gearbox-depth-mm`, "
      "`--gearbox-shaft-from-motor-end-mm`.")
    p("- **MG90S:** 22.8 × 12.2 mm body, tabs 32.5 mm, holes 27.8 mm apart, shaft 6.1 mm from one end. "
      "Shim under the tabs so the horn clears the shuttle tab by about 0.5 mm.")
    p("- **KW4 switch:** 20 × 10 × 6.4 mm, holes 9.5 mm apart. Its mounting holes are slotted ±1.5 mm: set it so the "
      "hub flag closes it at the park point. It sits 0.6 mm behind the cam's rear face, so keep the lever inside the hub zone.")
    p(f"- **Springs:** free length {g.spring_free:.0f} mm assumed (`--spring-free-mm`).")
    p("- **Cam direction:** seen from the motor side, the cam turns **clockwise** to cock. "
      "If your motor's forward is the other way, swap its wires (don't mirror the cam: the flag and D-flat follow).")
    p("- **After a shot** the tongue sits in the breech window, so the shuttle can't return until the cam re-cocks. "
      "The firmware sequence is COCK, then LOAD or UNLOAD (bench-rig.md, interlock).")
    p("")
    return "\n".join(w) + "\n"


# --------------------------------------------------------------------------- preview
def render(path: Path, items: list[tuple[Part, str]], elev: float, azim: float, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import numpy as np

    fig = plt.figure(figsize=(12, 8), dpi=110)
    ax = fig.add_subplot(projection="3d")
    light = np.array([0.3, -0.5, 0.8])
    light /= np.linalg.norm(light)
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    all_tri, all_col = [], []
    for part, color in items:
        verts, tris = part.tessellate(0.15, 0.3)
        v = np.array([(p.X, p.Y, p.Z) for p in verts])
        t = np.array(tris)
        if len(t) == 0:
            continue
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
        base = np.array(matplotlib.colors.to_rgb(color))
        cols = np.clip(base[None, :] * shade[:, None], 0, 1)
        all_tri.append(tri)
        all_col.append(cols)
        lo, hi = np.minimum(lo, v.min(0)), np.maximum(hi, v.max(0))
    # one collection, so matplotlib depth-sorts every triangle against every other
    ax.add_collection3d(Poly3DCollection(np.concatenate(all_tri), facecolors=np.concatenate(all_col),
                                         edgecolors="none"))
    mid, span = (lo + hi) / 2, (hi - lo).max() / 2
    for setter, m in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mid):
        setter(m - span, m + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


# --------------------------------------------------------------------------- web viewer export
def export_web(g: Rig, parts: dict[str, Part], cam_l: Part, web: Path) -> None:
    """Meshes in the assembly frame (sled and roller at rest, shuttle at the breech, cam in its own
    frame) plus rig.json with what the 3D viewer needs to animate the cycle."""
    import json

    web.mkdir(parents=True, exist_ok=True)
    hw = hardware(g, cocked=False)
    meshes = {k: parts[k] for k in ("launcher_body", "lid", "magazine", "chrono_sleeve", "motor_mount",
                                    "bumper", "preload_bar", "stand", "sled", "shuttle")}
    meshes["cam"] = cam_l
    for k in ("rods", "roller_623", "gearbox", "motor_can", "mg90s", "shaft"):
        meshes[k] = hw[k]
    import base64
    import struct

    packed = {}
    for name, part in meshes.items():                      # indexed triangle meshes, little-endian
        verts, tris = part.tessellate(0.04, 0.2)
        pos = struct.pack(f"<{3 * len(verts)}f", *(c for v in verts for c in (v.X, v.Y, v.Z)))
        idx = struct.pack(f"<{3 * len(tris)}I", *(i for t in tris for i in t))
        packed[name] = {"p": base64.b64encode(pos).decode("ascii"), "i": base64.b64encode(idx).decode("ascii")}
    for old in web.glob("*.stl"):
        old.unlink()
    (web / "meshes.json").write_text(json.dumps(packed), encoding="utf-8")
    a = g.a
    data = {
        "units": "mm; X along the barrel, Y left, Z up; origin = channel floor at the cocked push face",
        "stroke": g.stroke, "gap": g.gap, "travel": g.travel, "za": g.za,
        "cam": {"x": g.cam_x, "y1": g.cam_y1, "rise_deg": a.rise_deg, "dwell_deg": a.dwell_deg,
                "d": 2 * g.r_cam_max, "t": g.cam_t,
                "lift": [[round(math.degrees(t), 3), round(u * 1e3, 4)] for t, _, u in g.cam["pts"]]},
        "pocket": {"l": g.pk_l, "w": g.pk_w, "d": g.pk_d, "ring_h": g.ring_h},
        "pellet": {"l": a.length_mm, "w": a.width_mm, "t": a.thick_mm, "mass_g": a.mass_g},
        "magazine": {"x": g.mag_x, "y": g.mag_y, "count": a.rig_pellets},
        "rod_y": g.rod_y, "seat_bar_x": g.bar_front_nom - g.seat, "seat_sled_rest_x": g.sled_rear_rest + g.seat,
        "x_end": g.x_end, "sleeve_end": g.x_end + 80.0, "gates": [g.x_end + 10, g.x_end + 10 + a.gate_mm],
        "v0": a.v0, "sled_g": a.sled_g, "spring_k_n_per_mm": g.sp["k"] / 1e3,
        "piv": [g.piv_x, g.piv_z],
    }
    (web / "rig.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


# --------------------------------------------------------------------------- main
PRINT_ROT ={"lid": (180, 0, 0), "shuttle": (180, 0, 0), "preload_bar": (0, -90, 0), "bumper": (0, -90, 0),
             "chrono_sleeve": (0, 0, 0)}


def print_pose(name: str, part: Part) -> Part:
    p = Rot(*PRINT_ROT.get(name, (0, 0, 0))) * part
    bb = p.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p


def parse(argv: list[str] | None) -> tuple[argparse.Namespace, list[str]]:
    q = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    q.add_argument("--spring-free-mm", type=float, default=40.0)
    q.add_argument("--rig-pellets", type=int, default=12, help="magazine capacity on the rig")
    q.add_argument("--gearbox-len-mm", type=float, default=46.0)
    q.add_argument("--gearbox-height-mm", type=float, default=32.0)
    q.add_argument("--gearbox-depth-mm", type=float, default=25.0, help="along the output shaft")
    q.add_argument("--gearbox-shaft-from-motor-end-mm", type=float, default=34.0)
    q.add_argument("--out", type=Path, default=ROOT / "cad" / "bench_rig")
    q.add_argument("--doc", type=Path, default=ROOT / "docs" / "mechanical" / "bench-rig-cad.md")
    q.add_argument("--no-preview", action="store_true")
    q.add_argument("--no-checks", action="store_true")
    q.add_argument("--no-web", action="store_true", help="skip the meshes for the 3D viewer")
    return q.parse_known_args(argv)


def main(argv: list[str] | None = None) -> int:
    own, rest = parse(argv)
    a = ld.parse(rest)
    for k, v in vars(own).items():
        setattr(a, k, v)
    sp = ld.spring_design(a)
    cam = ld.cam_design(a, sp)
    fd = ld.feed_design(a)
    g = Rig(a, sp, cam, fd)
    g.lid_screws = [(g.hx0 + 3, g.mag_y), (g.hx1 - 3, g.mag_y), (g.fw_x0 + 3, -9.2),
                    (30.0, 9.2), (30.0, -9.2), (g.x_end - 3, 9.2), (g.x_end - 3, -9.2)]
    g.mag_screws = g.lid_screws[:2]

    print("building parts ...", flush=True)
    cam_l, _ = cam_local(g)
    parts: dict[str, Part] = {
        "launcher_body": launcher_body(g), "lid": lid(g), "sled": sled(g), "preload_bar": preload_bar(g),
        "bumper": bumper(g), "shuttle": shuttle(g), "magazine": magazine(g), "cam": cam_l,
        "chrono_sleeve": chrono_sleeve(g), "motor_mount": motor_mount(g), "stand": stand(g),
        "pellet_gauge": pellet_gauge(g), "clearance_coupon": clearance_coupon(g),
    }
    masses = {k: vol_g(v) for k, v in parts.items()}
    masses["sled_hw"] = 1.5 + 0.8 + 0.25  # 623ZZ + M3x10 + nut (estimate)

    out = own.out
    (out / "stl").mkdir(parents=True, exist_ok=True)
    (out / "step").mkdir(parents=True, exist_ok=True)
    assembled = {k: v for k, v in parts.items() if k not in ("pellet_gauge", "clearance_coupon")}
    cocked = dict(assembled)
    cocked["sled"] = Pos(-g.stroke, 0, 0) * parts["sled"]
    cocked["cam"] = place_cam(g, cam_l, a.rise_deg + a.dwell_deg / 2)
    for name, part in parts.items():
        export_stl(print_pose(name, part), str(out / "stl" / f"{name}.stl"))
        if name in cocked:
            export_step(cocked[name], str(out / "step" / f"{name}.step"))
    hw = hardware(g, cocked=True)
    children = []
    for name, part in list(cocked.items()) + [(f"hw_{k}", v) for k, v in hw.items()]:
        part.label = name
        children.append(part)
    export_step(Compound(children=children, label="desuu_bench_rig"), str(out / "bench_rig_assembly.step"))
    print(f"wrote {len(parts)} STL + STEP to {out}", flush=True)

    if not own.no_web:
        export_web(g, parts, cam_l, out / "web")
        print(f"wrote 3D viewer meshes to {out / 'web'}", flush=True)

    res: list = []
    if not own.no_checks:
        print("running interference checks ...", flush=True)
        res = checks(g, parts, cam_l)
        bad = [r for r in res if not r[2]]
        for name, val, ok in res:
            print(f"  {'ok  ' if ok else 'FAIL'} {name}: {val}")
        print(f"{len(res) - len(bad)}/{len(res)} checks pass")
    own.doc.write_text(report(g, parts, res, masses), encoding="utf-8")
    print(f"wrote {own.doc}")

    if not own.no_preview:
        print("rendering previews ...", flush=True)
        colours = {"launcher_body": "#d9d4c7", "lid": "#c9e0e8", "sled": "#e07b39", "preload_bar": "#8a6fb0",
                   "bumper": "#333333", "shuttle": "#3f8fd2", "magazine": "#a9d8e6", "cam": "#d23f3f",
                   "chrono_sleeve": "#2b2b2b", "motor_mount": "#7fb069", "stand": "#bdbdbd"}
        hwc = "#8c8c8c"
        rig = [(v, colours[k]) for k, v in cocked.items()] + [(v, hwc) for v in hw.values()]
        render(out / "preview" / "assembly_cocked.png", rig, 22, -50, "DESUU M2 bench rig, cocked (stand grey, hardware dark grey)")
        mech_keys = ("sled", "preload_bar", "bumper", "shuttle", "cam", "motor_mount")
        mech_hw = ("rods", "roller_623", "spring_L", "spring_R", "shaft", "gearbox")
        mech = [(cocked[k], colours[k]) for k in mech_keys] + [(hw[k], hwc) for k in mech_hw]
        render(out / "preview" / "mechanism_cocked.png", mech, 40, -60,
               "Moving parts, cocked: body, lid, magazine and stand hidden")
        hw_r = hardware(g, cocked=False)
        cam_rest = place_cam(g, cam_l, (a.rise_deg + a.dwell_deg + 360) / 2)
        side_keys = ("launcher_body", "sled", "preload_bar", "bumper", "chrono_sleeve")
        side_c = [(cocked[k], colours[k]) for k in side_keys] + [(cocked["cam"], colours["cam"])] +                  [(hw[k], hwc) for k in ("roller_623", "rods")]
        side_r = [(assembled[k], colours[k]) for k in side_keys] + [(cam_rest, colours["cam"])] +                  [(hw_r[k], hwc) for k in ("roller_623", "rods")]
        render(out / "preview" / "side_cocked.png", side_c, 0, -90, "From the cam side (-Y), cocked: roller on the dwell")
        render(out / "preview" / "side_rest.png", side_r, 0, -90, "From the cam side (-Y), after the shot: roller 1 mm off the cam")
        print("wrote previews")
    return 0 if all(r[2] for r in res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
