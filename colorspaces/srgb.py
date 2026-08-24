"""Hex parsing and the sRGB <-> linear RGB <-> XYZ pipeline.

The sRGB gamma curve isn't a simple power function -- it's linear near
black and a power curve above a small threshold, to avoid an infinite
slope at zero. Skipping that distinction is the usual source of "my
gradients look wrong" bugs, so it's kept explicit here rather than
approximated with a flat gamma=2.2.
"""

from __future__ import annotations

_GAMMA_THRESHOLD = 0.04045
_LINEAR_THRESHOLD = 0.0031308

# sRGB primaries against a D65 white point (IEC 61966-2-1).
_RGB_TO_XYZ = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)
_XYZ_TO_RGB = (
    (3.2404542, -1.5371385, -0.4985314),
    (-0.9692660, 1.8760108, 0.0415560),
    (0.0556434, -0.2040259, 1.0572252),
)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        raise ValueError(f"not a 3 or 6 digit hex color: {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    for c in (r, g, b):
        if not 0 <= c <= 255:
            raise ValueError(f"channel out of range 0-255: {c}")
    return f"#{r:02x}{g:02x}{b:02x}"


def srgb_to_linear(c: float) -> float:
    """c is one channel normalized to 0..1."""
    if c <= _GAMMA_THRESHOLD:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    if c <= _LINEAR_THRESHOLD:
        return c * 12.92
    return 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_xyz(r: int, g: int, b: int) -> tuple[float, float, float]:
    """r, g, b are 0..255 integers; returns CIE XYZ under a D65 white point."""
    linear = tuple(srgb_to_linear(v / 255) for v in (r, g, b))
    return tuple(sum(coef * v for coef, v in zip(row, linear)) for row in _RGB_TO_XYZ)


def xyz_to_rgb(x: float, y: float, z: float) -> tuple[int, int, int]:
    linear = (sum(coef * v for coef, v in zip(row, (x, y, z))) for row in _XYZ_TO_RGB)
    srgb = (linear_to_srgb(v) for v in linear)
    # Round-tripping through Lab can land slightly outside the sRGB gamut;
    # clamp rather than raise, since the caller usually just wants a swatch.
    return tuple(round(min(1.0, max(0.0, v)) * 255) for v in srgb)
