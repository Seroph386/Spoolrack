"""Regression tests for accessible filament hover names."""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


class FilamentTooltipTests(unittest.TestCase):
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

    def test_single_color_spool_has_hover_name(self):
        html = self.render({"name": "Sunrise PLA", "color_hex": "FF7800"})
        self.assertIn('title="Sunrise PLA"', html)
        self.assertIn('aria-label="Sunrise PLA"', html)
        self.assertIn('tabindex="0"', html)
        self.assertIn("background:#FF7800", html)

    def test_multicolor_spool_has_hover_name(self):
        html = self.render({
            "name": "Witchcraft",
            "multi_color_hexes": "AA0055,6633FF",
            "multi_color_direction": "coaxial",
        })
        self.assertIn('title="Witchcraft"', html)
        self.assertIn("conic-gradient(", html)

    def test_filament_name_is_escaped_in_attributes(self):
        html = self.render({
            "name": 'Blue "Sky" <script>alert(1)</script> & Co',
            "color_hex": "0011FF",
        })
        self.assertIn(
            'title="Blue &quot;Sky&quot; &lt;script&gt;alert(1)&lt;/script&gt; &amp; Co"',
            html,
        )
        self.assertNotIn("<script>", html)

    def test_missing_name_has_meaningful_fallback(self):
        html = self.render({"name": None, "color_hex": "00FF00"})
        self.assertIn('title="Unnamed filament"', html)


if __name__ == "__main__":
    unittest.main()
