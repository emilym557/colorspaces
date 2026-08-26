import unittest

from colorspaces import (
    delta_e_cie76,
    hex_to_rgb,
    lab_to_rgb,
    linear_to_srgb,
    rgb_to_hex,
    rgb_to_lab,
    rgb_to_xyz,
    srgb_to_linear,
    xyz_to_rgb,
)


class HexRoundTrip(unittest.TestCase):
    def test_six_digit(self):
        self.assertEqual(hex_to_rgb("#1a2b4c"), (26, 43, 76))

    def test_three_digit_expands(self):
        self.assertEqual(hex_to_rgb("#abc"), (170, 187, 204))

    def test_without_leading_hash(self):
        self.assertEqual(hex_to_rgb("1a2b4c"), (26, 43, 76))

    def test_rejects_bad_length(self):
        with self.assertRaises(ValueError):
            hex_to_rgb("#12345")

    def test_rgb_to_hex_round_trip(self):
        for hex_code in ("#1a2b4c", "#ffffff", "#000000", "#e63946"):
            self.assertEqual(rgb_to_hex(*hex_to_rgb(hex_code)), hex_code)

    def test_rgb_to_hex_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            rgb_to_hex(256, 0, 0)


class GammaRoundTrip(unittest.TestCase):
    def test_round_trips_across_the_threshold(self):
        for c in (0.0, 0.001, 0.0031308, 0.01, 0.2, 0.5, 0.8, 1.0):
            self.assertAlmostEqual(linear_to_srgb(srgb_to_linear(c)), c, places=6)

    def test_black_and_white_are_fixed_points(self):
        self.assertEqual(srgb_to_linear(0.0), 0.0)
        self.assertEqual(srgb_to_linear(1.0), 1.0)


def _assert_close_rgb(test, actual, expected, tolerance=1):
    # The forward and inverse RGB<->XYZ matrices are independently rounded
    # constants, not exact inverses, so a round trip can land off by a
    # rounding step rather than reproducing the integer exactly.
    for got, want in zip(actual, expected):
        test.assertLessEqual(abs(got - want), tolerance, f"{actual} vs {expected}")


class XyzRoundTrip(unittest.TestCase):
    def test_round_trips_for_a_range_of_colors(self):
        samples = [(0, 0, 0), (255, 255, 255), (26, 43, 76), (230, 57, 70), (128, 128, 128)]
        for rgb in samples:
            _assert_close_rgb(self, xyz_to_rgb(*rgb_to_xyz(*rgb)), rgb)

    def test_white_lands_near_the_d65_white_point(self):
        x, y, z = rgb_to_xyz(255, 255, 255)
        self.assertAlmostEqual(x, 0.95047, places=3)
        self.assertAlmostEqual(y, 1.00000, places=3)
        self.assertAlmostEqual(z, 1.08883, places=3)


class LabKnownValues(unittest.TestCase):
    """Reference values for the sRGB primaries under a D65 white point,
    as commonly tabulated (e.g. Bruce Lindbloom's color calculators)."""

    def test_black(self):
        L, a, b = rgb_to_lab(0, 0, 0)
        self.assertAlmostEqual(L, 0.0, delta=0.5)
        self.assertAlmostEqual(a, 0.0, delta=0.5)
        self.assertAlmostEqual(b, 0.0, delta=0.5)

    def test_white(self):
        L, a, b = rgb_to_lab(255, 255, 255)
        self.assertAlmostEqual(L, 100.0, delta=0.5)
        self.assertAlmostEqual(a, 0.0, delta=0.5)
        self.assertAlmostEqual(b, 0.0, delta=0.5)

    def test_red(self):
        L, a, b = rgb_to_lab(255, 0, 0)
        self.assertAlmostEqual(L, 53.24, delta=0.5)
        self.assertAlmostEqual(a, 80.09, delta=0.5)
        self.assertAlmostEqual(b, 67.20, delta=0.5)

    def test_green(self):
        L, a, b = rgb_to_lab(0, 255, 0)
        self.assertAlmostEqual(L, 87.73, delta=0.5)
        self.assertAlmostEqual(a, -86.18, delta=0.5)
        self.assertAlmostEqual(b, 83.18, delta=0.5)

    def test_blue(self):
        L, a, b = rgb_to_lab(0, 0, 255)
        self.assertAlmostEqual(L, 32.30, delta=0.5)
        self.assertAlmostEqual(a, 79.19, delta=0.5)
        self.assertAlmostEqual(b, -107.86, delta=0.5)


class LabRoundTrip(unittest.TestCase):
    def test_round_trips_for_a_range_of_colors(self):
        samples = [(0, 0, 0), (255, 255, 255), (26, 43, 76), (230, 57, 70), (128, 128, 128)]
        for rgb in samples:
            _assert_close_rgb(self, lab_to_rgb(*rgb_to_lab(*rgb)), rgb)


class DeltaE(unittest.TestCase):
    def test_zero_for_identical_colors(self):
        lab = rgb_to_lab(90, 140, 200)
        self.assertEqual(delta_e_cie76(lab, lab), 0.0)

    def test_symmetric(self):
        lab1 = rgb_to_lab(26, 43, 76)
        lab2 = rgb_to_lab(40, 48, 74)
        self.assertAlmostEqual(delta_e_cie76(lab1, lab2), delta_e_cie76(lab2, lab1), places=9)

    def test_similar_colors_are_closer_than_distant_ones(self):
        navy = rgb_to_lab(*hex_to_rgb("#1a2b4c"))
        slate = rgb_to_lab(*hex_to_rgb("#28304a"))
        yellow = rgb_to_lab(*hex_to_rgb("#f5d90a"))
        self.assertLess(delta_e_cie76(navy, slate), delta_e_cie76(navy, yellow))


if __name__ == "__main__":
    unittest.main()
