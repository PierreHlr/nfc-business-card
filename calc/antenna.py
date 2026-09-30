"""Electromagnetic models for a planar rectangular NFC antenna.

Everything is in SI units and uses the Python standard library only, so the
scripts run with any Python 3 (including the interpreter bundled with KiCad).

Models
------
* Greenhouse method: the spiral is split into straight segments; the total
  inductance is the sum of every partial self- and mutual inductance.
* Empirical formula for printed rectangular coils (ST AN2972 / NXP AN11276).
* Inter-turn capacitance: coplanar strips (conformal mapping) + energy method.
"""
import math

MU0 = 4e-7 * math.pi          # vacuum permeability [H/m]
EPS0 = 8.854e-12              # vacuum permittivity [F/m]
RHO_CU = 1.72e-8              # copper resistivity at 20 degC [ohm.m]
T_CU = 35e-6                  # 1 oz copper thickness [m]
C_CHIP = 50e-12               # NTAG213F input capacitance (datasheet, 13.56 MHz) [F]
F_NFC = 13.56e6               # NFC carrier frequency [Hz]


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
def card_spiral(n_turns=4, outer_x=80e-3, outer_y=48e-3, width=1.0e-3, gap=0.5e-3):
    """Centre-line polyline of the antenna actually drawn on the PCB.

    The spiral starts at the bottom-left outer corner and winds clockwise
    (seen from the top), stepping one pitch (width + gap) inwards per turn.
    Coordinates are centred on the card, y pointing down (KiCad convention).
    """
    pitch = width + gap
    x0, y0 = outer_x / 2 - width / 2, outer_y / 2 - width / 2
    pts = [(-x0, y0)]
    for k in range(n_turns):
        xl, xr = -x0 + k * pitch, x0 - k * pitch
        yt, yb = -y0 + k * pitch, y0 - k * pitch
        pts += [(xl, yt), (xr, yt), (xr, yb), (xl + pitch, yb)]
    return pts


def segments(points):
    return list(zip(points, points[1:]))


def length(points):
    return sum(math.dist(p, q) for p, q in segments(points))


# --------------------------------------------------------------------------
# Inductance: Greenhouse method
# --------------------------------------------------------------------------
def _g(u, d):
    return u * math.asinh(u / d) - math.sqrt(u * u + d * d)


def mutual_parallel(a1, b1, a2, b2, d):
    """Exact mutual inductance of two parallel filaments.

    Filament 1 spans [a1, b1], filament 2 spans [a2, b2] along the same axis,
    distance d apart. Obtained by integrating the Neumann formula.
    """
    return MU0 / (4 * math.pi) * (_g(b1 - a2, d) - _g(a1 - a2, d) - _g(b1 - b2, d) + _g(a1 - b2, d))


def gmd_rect(width, thickness=T_CU):
    """Geometric mean distance of a rectangular cross-section to itself."""
    return 0.2235 * (width + thickness)


def inductance_greenhouse(points, width, thickness=T_CU):
    """Sum of partial self- and mutual inductances of axis-aligned segments.

    Perpendicular segments have no mutual inductance; parallel ones add with a
    sign given by the relative direction of their currents.
    """
    segs = segments(points)
    gmd = gmd_rect(width, thickness)
    total = 0.0
    for i, (p1, p2) in enumerate(segs):
        for j, (q1, q2) in enumerate(segs):
            h1, h2 = abs(p1[1] - p2[1]) < 1e-12, abs(q1[1] - q2[1]) < 1e-12
            if h1 != h2:
                continue
            ax = 0 if h1 else 1              # coordinate along the segment
            a1, b1 = sorted((p1[ax], p2[ax]))
            a2, b2 = sorted((q1[ax], q2[ax]))
            d = gmd if i == j else abs(p1[1 - ax] - q1[1 - ax]) or gmd
            s1 = 1 if p2[ax] > p1[ax] else -1
            s2 = 1 if q2[ax] > q1[ax] else -1
            total += s1 * s2 * mutual_parallel(a1, b1, a2, b2, d)
    return total


def square_loop_reference(side, width, thickness=T_CU):
    """Closed-form inductance of a square loop, used to validate the code."""
    rho = gmd_rect(width, thickness)
    return 2 * MU0 * side / math.pi * (math.log(side / rho) - 0.774)


# --------------------------------------------------------------------------
# Inductance: empirical formula for printed rectangular coils
# --------------------------------------------------------------------------
def inductance_empirical(outer_x, outer_y, n_turns, width, gap, thickness=T_CU, p=1.8):
    """ST AN2972 formula, p = 1.8 for printed antennas."""
    a = outer_x - n_turns * (width + gap)
    b = outer_y - n_turns * (width + gap)
    d = 2 * (thickness + width) / math.pi
    c = math.hypot(a, b)
    x1 = a * math.log(2 * a * b / (d * (a + c)))
    x2 = b * math.log(2 * a * b / (d * (b + c)))
    x3 = 2 * (a + b - c)
    x4 = (a + b) / 4
    return MU0 / math.pi * (x1 + x2 - x3 + x4) * n_turns ** p


# --------------------------------------------------------------------------
# Parasitic capacitance
# --------------------------------------------------------------------------
def elliptic_ratio(k):
    """K(k') / K(k), Hilberg's approximation (error < 3e-6)."""
    kp = math.sqrt(1 - k * k)
    if k <= 1 / math.sqrt(2):
        return math.log(2 * (1 + math.sqrt(kp)) / (1 - math.sqrt(kp))) / math.pi
    return math.pi / math.log(2 * (1 + math.sqrt(k)) / (1 - math.sqrt(k)))


def coplanar_capacitance_per_m(width, gap, eps_r=4.5):
    """Capacitance per metre between two coplanar strips on a thick substrate."""
    k = gap / (gap + 2 * width)
    return EPS0 * (1 + eps_r) / 2 * elliptic_ratio(k)


def interturn_capacitance(points, n_turns, width, gap, eps_r=4.5):
    """Equivalent capacitance across the terminals (energy method).

    Adjacent turns see 1/N of the terminal voltage, so the stored energy
    1/2 C' l (V/N)^2 equals 1/2 C_eq V^2  =>  C_eq = C' l / N^2.
    """
    adjacent = length(points) * (n_turns - 1) / n_turns
    return coplanar_capacitance_per_m(width, gap, eps_r) * adjacent / n_turns ** 2


# --------------------------------------------------------------------------
# Resonance, losses, induced voltage
# --------------------------------------------------------------------------
def resonance(L, C):
    return 1 / (2 * math.pi * math.sqrt(L * C))


def capacitance_for(L, f):
    return 1 / ((2 * math.pi * f) ** 2 * L)


def skin_depth(f, rho=RHO_CU):
    return math.sqrt(rho / (math.pi * f * MU0))


def resistance_dc(points, width, thickness=T_CU):
    return RHO_CU * length(points) / (width * thickness)


def resistance_ac(points, width, f, thickness=T_CU):
    """Skin effect only: current confined to a depth delta on both faces."""
    delta = skin_depth(f)
    t_eff = min(thickness, 2 * delta * (1 - math.exp(-thickness / (2 * delta))))
    return RHO_CU * length(points) / (width * t_eff)


def turn_areas(n_turns=4, outer_x=80e-3, outer_y=48e-3, width=1.0e-3, gap=0.5e-3):
    """Area enclosed by each turn (centre line)."""
    pitch = width + gap
    return [(outer_x - width - 2 * k * pitch) * (outer_y - width - 2 * k * pitch) for k in range(n_turns)]


def induced_emf(h_rms, areas, f=F_NFC):
    """Faraday's law for a uniform field H perpendicular to the card."""
    return 2 * math.pi * f * MU0 * h_rms * sum(areas)
