"""sRGB <-> HSL and sRGB <-> HSV.

These are just rearrangements of the same 0-255 RGB values into a
cylindrical coordinate system -- unlike Lab, there's no perceptual
model behind them, they're just easier for humans to pick from (hue
wheel, then lightness/saturation sliders). Kept in a separate module
from srgb.py since nothing else in the library depends on them.
"""

from __future__ import annotations


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Returns (h, s, l) with h in 0..360 and s, l in 0..1."""
    rf, gf, bf = r / 255, g / 255, b / 255
    hi = max(rf, gf, bf)
    lo = min(rf, gf, bf)
    span = hi - lo
    l = (hi + lo) / 2

    if span == 0:
        return (0.0, 0.0, l)

    s = span / (1 - abs(2 * l - 1))

    if hi == rf:
        h = ((gf - bf) / span) % 6
    elif hi == gf:
        h = (bf - rf) / span + 2
    else:
        h = (rf - gf) / span + 4
    h *= 60

    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    h = h % 360
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        rf, gf, bf = c, x, 0.0
    elif h < 120:
        rf, gf, bf = x, c, 0.0
    elif h < 180:
        rf, gf, bf = 0.0, c, x
    elif h < 240:
        rf, gf, bf = 0.0, x, c
    elif h < 300:
        rf, gf, bf = x, 0.0, c
    else:
        rf, gf, bf = c, 0.0, x

    return tuple(round((channel + m) * 255) for channel in (rf, gf, bf))


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Returns (h, s, v) with h in 0..360 and s, v in 0..1."""
    rf, gf, bf = r / 255, g / 255, b / 255
    hi = max(rf, gf, bf)
    lo = min(rf, gf, bf)
    span = hi - lo

    v = hi
    s = 0.0 if hi == 0 else span / hi

    if span == 0:
        return (0.0, s, v)

    if hi == rf:
        h = ((gf - bf) / span) % 6
    elif hi == gf:
        h = (bf - rf) / span + 2
    else:
        h = (rf - gf) / span + 4
    h *= 60

    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        rf, gf, bf = c, x, 0.0
    elif h < 120:
        rf, gf, bf = x, c, 0.0
    elif h < 180:
        rf, gf, bf = 0.0, c, x
    elif h < 240:
        rf, gf, bf = 0.0, x, c
    elif h < 300:
        rf, gf, bf = x, 0.0, c
    else:
        rf, gf, bf = c, 0.0, x

    return tuple(round((channel + m) * 255) for channel in (rf, gf, bf))
