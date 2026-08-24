# colorspaces

RGB is a display encoding, not a perceptual space. Two colors that are
close in RGB can look very different, and two colors that are far apart
in RGB can look nearly identical -- the encoding is bent to how sRGB
monitors excite phosphors, not to how the eye perceives differences.
That makes RGB a bad basis for anything that needs to reason about
color similarity: sorting a palette, deduplicating near-identical
colors, picking a readable text color against a background.

This library converts between sRGB (as hex strings or 0-255 triples),
linear RGB, CIE XYZ, and CIELAB, and gives you a Lab-space distance
function (delta E) so "how different do these two colors look" has an
actual number attached to it.

No dependencies, standard library only.

## Install

Not published anywhere yet -- copy the `colorspaces/` directory into
your project, or install locally in editable mode:

```
pip install -e .
```

## Usage

```python
from colorspaces import hex_to_rgb, rgb_to_lab, delta_e_cie76

navy = hex_to_rgb("#1a2b4c")
slate = hex_to_rgb("#28304a")

lab_navy = rgb_to_lab(*navy)
lab_slate = rgb_to_lab(*slate)

print(delta_e_cie76(lab_navy, lab_slate))
# small number -> these look similar despite different hex codes
```

Finding the closest match to a target color in a fixed palette:

```python
from colorspaces import hex_to_rgb, rgb_to_lab, delta_e_cie76

palette = ["#e63946", "#f1faee", "#a8dadc", "#457b9d", "#1d3557"]
target_lab = rgb_to_lab(*hex_to_rgb("#5588aa"))

closest = min(
    palette,
    key=lambda hex_code: delta_e_cie76(target_lab, rgb_to_lab(*hex_to_rgb(hex_code))),
)
```

Round-tripping through linear RGB and XYZ directly, if you need the
intermediate values (for compositing, or blending in linear light
instead of gamma-encoded RGB):

```python
from colorspaces import rgb_to_xyz, xyz_to_rgb

xyz = rgb_to_xyz(26, 43, 76)
back = xyz_to_rgb(*xyz)  # (26, 43, 76), modulo rounding
```

## What's here

- `colorspaces/srgb.py` -- hex parsing, sRGB gamma encode/decode, RGB <-> XYZ
- `colorspaces/lab.py` -- XYZ <-> CIELAB, delta E (CIE76)

## Status

Early. Covers the sRGB / XYZ / Lab pipeline with a D65 white point.
Not yet covered: HSL/HSV, other white points, CIEDE2000.
