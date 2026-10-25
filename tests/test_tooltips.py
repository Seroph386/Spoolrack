"""Regression tests for desktop hover and accessible touch filament details."""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.colors import filament_color_codes
from app.main import app


class FilamentDetailTests(unittest.TestCase):
    def render(self, filament):
        config = [{
            "name": "Main",
            "columns": 1,
            "locations": ["F-001"],
            "default_capacity": 4,
        }]
        with (
            patch("app.main.inventory", new=AsyncMock(return_value=[
                {"location": "F-001", "filament": filament}
            ])),
            patch("app.main.rack_config", return_value=config),
        ):
            result = TestClient(app).get("/")
        self.assertEqual(result.status_code, 200)
        return result.text

    def test_single_color_includes_vendor_name_and_color(self):
        html = self.render({
            "name": "Sunrise PLA",
            "vendor": {"name": "Cookiecad"},
            "color_hex": "FF7800",
        })
        self.assertIn('title="Cookiecad · Sunrise PLA · #FF7800"', html)
        self.assertIn('data-manufacturer="Cookiecad"', html)
        self.assertIn('data-name="Sunrise PLA"', html)
        self.assertIn('data-colors="#FF7800"', html)
        self.assertIn('aria-label="Cookiecad · Sunrise PLA · #FF7800"', html)
        self.assertIn('aria-haspopup="dialog"', html)
        self.assertIn('type="button" class="dot"', html)
        self.assertIn("background:#FF7800", html)

    def test_multicolor_includes_all_colors_and_vendor(self):
        html = self.render({
            "name": "Witchcraft",
            "vendor": {"name": "Cookiecad"},
            "multi_color_hexes": "AA0055,6633FF",
            "multi_color_direction": "coaxial",
        })
        self.assertIn('title="Cookiecad · Witchcraft · #AA0055, #6633FF"', html)
        self.assertIn('data-colors="#AA0055, #6633FF"', html)
        self.assertIn("conic-gradient(", html)

    def test_filament_and_vendor_names_are_escaped(self):
        html = self.render({
            "name": 'Blue "Sky" <script>alert(1)</script> & Co',
            "vendor": {"name": 'Maker "One" & Sons'},
            "color_hex": "0011FF",
        })
        self.assertIn('data-manufacturer="Maker &quot;One&quot; &amp; Sons"', html)
        self.assertIn(
            'data-name="Blue &quot;Sky&quot; &lt;script&gt;alert(1)&lt;/script&gt; &amp; Co"',
            html,
        )
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_missing_values_use_readable_fallbacks(self):
        html = self.render({"name": None, "vendor": None})
        self.assertIn('data-name="Unnamed filament"', html)
        self.assertIn('data-manufacturer="Unknown manufacturer"', html)
        self.assertIn('data-colors="Not specified"', html)

    def test_responsive_touch_ui_and_dialog_markup(self):
        html = self.render({"name": "Sunrise", "color_hex": "FF7800"})
        self.assertIn("@media (max-width: 599px)", html)
        self.assertIn("@media (hover: hover) and (pointer: fine)", html)
        self.assertIn("width: 44px; height: 44px", html)
        self.assertIn('<dialog id="filament-details"', html)
        self.assertIn('id="detail-manufacturer"', html)
        self.assertIn('id="detail-name"', html)
        self.assertIn('id="detail-colors"', html)
        self.assertIn('data-filament', html)
        self.assertIn("dialog.showModal()", html)
        self.assertIn("textContent = button.dataset.manufacturer", html)
        self.assertNotIn('http-equiv="refresh"', html)

    def test_color_codes_validate_and_fallback(self):
        self.assertEqual(
            filament_color_codes({
                "multi_color_hexes": "FF0000, #00FF00, invalid",
                "color_hex": "0000FF",
            }),
            ["#FF0000", "#00FF00"],
        )
        self.assertEqual(
            filament_color_codes({"multi_color_hexes": "bogus", "color_hex": "AABBCC"}),
            ["#AABBCC"],
        )


if __name__ == "__main__":
    unittest.main()
