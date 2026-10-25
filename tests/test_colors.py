import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.colors import filament_background
from app.main import app


class FilamentColorTests(unittest.TestCase):
    def test_single_color(self):
        self.assertEqual(filament_background({"color_hex": "FF7800"}), "#FF7800")

    def test_single_color_alpha(self):
        self.assertEqual(filament_background({"color_hex": "33669980"}), "#33669980")

    def test_missing_colors_remain_gray(self):
        self.assertEqual(filament_background({}), "#888888")

    def test_coaxial_multicolor_uses_sectors(self):
        css = filament_background({
            "multi_color_hexes": "FF0000,00FF00,0000FF",
            "multi_color_direction": "coaxial",
        })
        self.assertEqual(
            css,
            "conic-gradient(#FF0000 0.000% 33.333%, "
            "#00FF00 33.333% 66.667%, #0000FF 66.667% 100.000%)",
        )

    def test_longitudinal_multicolor_uses_smooth_gradient(self):
        self.assertEqual(
            filament_background({
                "multi_color_hexes": "#AA0000, 00AA00",
                "multi_color_direction": "longitudinal",
            }),
            "linear-gradient(90deg, #AA0000, #00AA00)",
        )

    def test_multicolor_takes_priority(self):
        self.assertIn(
            "conic-gradient",
            filament_background({
                "color_hex": "123456",
                "multi_color_hexes": "ABCDEF,000000",
            }),
        )

    def test_invalid_colors_cannot_inject_css(self):
        self.assertEqual(
            filament_background({"color_hex": "red;position:absolute"}),
            "#888888",
        )
        self.assertEqual(
            filament_background({"multi_color_hexes": "var(--x),#AA00BB"}),
            "#AA00BB",
        )

    def test_invalid_multicolor_falls_back_to_single_color(self):
        self.assertEqual(
            filament_background({
                "multi_color_hexes": "invalid,",
                "color_hex": "778899",
            }),
            "#778899",
        )


class DashboardColorsTests(unittest.TestCase):
    def test_dashboard_renders_multicolor_spool(self):
        spool = {
            "location": "F-001",
            "filament": {
                "color_hex": None,
                "multi_color_hexes": "FF0000,0000FF",
                "multi_color_direction": "coaxial",
            },
        }
        config = [{"name": "Main", "columns": 1, "locations": ["F-001"], "default_capacity": 4}]
        with (
            patch("app.main.inventory", new=AsyncMock(return_value=[spool])),
            patch("app.main.rack_config", return_value=config),
        ):
            result = TestClient(app).get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn("conic-gradient(#FF0000", result.text)
        self.assertIn("1/4", result.text)


if __name__ == "__main__":
    unittest.main()
