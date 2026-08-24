"""CIE XYZ <-> CIELAB, and a perceptual color distance (delta E, CIE76).

Lab exists because Euclidean distance in RGB doesn't track how different
two colors actually look to a human eye -- equal steps in Lab are meant
to correspond to roughly equal perceived steps, which RGB and even XYZ
don't give you.
"""

from __future__ import annotations

from .srgb import rgb_to_xyz, xyz_to_rgb

# CIE 1964 D65 reference white, 2-degree observer.
_WHITE = (0.95047, 1.00000, 1.08883)

_EPSILON = 216 / 24389
_KAPPA = 24389 / 27


def _f(t: float) -> float:
    if t > _EPSILON:
        return t ** (1 / 3)
    return (_KAPPA * t + 16) / 116


def _f_inv(t: float) -> float:
    cubed = t ** 3
    if cubed > _EPSILON:
        return cubed
    return (116 * t - 16) / _KAPPA


def xyz_to_lab(x: float, y: float, z: float, white=_WHITE) -> tuple[float, float, float]:
    fx, fy, fz = (_f(v / w) for v, w in zip((x, y, z), white))
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return (L, a, b)


def lab_to_xyz(L: float, a: float, b: float, white=_WHITE) -> tuple[float, float, float]:
    fy = (L + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200
    return (_f_inv(fx) * white[0], _f_inv(fy) * white[1], _f_inv(fz) * white[2])


def rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    return xyz_to_lab(*rgb_to_xyz(r, g, b))


def lab_to_rgb(L: float, a: float, b: float) -> tuple[int, int, int]:
    return xyz_to_rgb(*lab_to_xyz(L, a, b))


def delta_e_cie76(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    """Straight-line distance in Lab space. Cheap and good enough for sorting
    or thresholding; the later CIE94/CIEDE2000 formulas correct for Lab's
    known non-uniformity but need a lot more code for the gain."""
    return sum((c1 - c2) ** 2 for c1, c2 in zip(lab1, lab2)) ** 0.5
