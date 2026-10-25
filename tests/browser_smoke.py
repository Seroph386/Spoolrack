"""Browser smoke test: native desktop hover and real tablet/phone tap behavior.

Runs in CI with Playwright/Chromium; Playwright is not a Spoolrack runtime dependency.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

from app.main import app


CONFIG = [{
    "name": "Main",
    "columns": 3,
    "rows": 1,
    "locations": ["F-001", "F-002", "F-003"],
    "default_capacity": 4,
}]
SPOOLS = [{
    "location": "F-001",
    "filament": {
        "name": "Witchcraft",
        "vendor": {"name": "Cookiecad"},
        "multi_color_hexes": "AA0055,6633FF",
        "multi_color_direction": "coaxial",
    },
}]


def html_fixture():
    with (
        patch("app.main.inventory", new=AsyncMock(return_value=SPOOLS)),
        patch("app.main.rack_config", return_value=CONFIG),
    ):
        response = TestClient(app).get("/")
        assert response.status_code == 200
        return response.text


def check_viewport(browser, html, *, width, height, touch, expected_columns):
    context = browser.new_context(
        viewport={"width": width, "height": height},
        has_touch=touch,
        is_mobile=touch,
    )
    page = context.new_page()
    page.set_content(html, wait_until="load")
    cols = page.locator(".grid").evaluate(
        "(el) => getComputedStyle(el).gridTemplateColumns.split(' ').length"
    )
    assert cols == expected_columns, (width, cols, expected_columns)

    swatch = page.locator("button.dot").first
    bounds = swatch.bounding_box()
    assert bounds is not None
    assert bounds["width"] >= (44 if touch else 32), bounds
    assert bounds["height"] >= (44 if touch else 32), bounds
    assert "Cookiecad" in swatch.get_attribute("title")
    assert "Witchcraft" in swatch.get_attribute("title")

    if touch:
        swatch.tap()
    else:
        swatch.hover()
        swatch.click()

    dialog = page.locator("#filament-details")
    assert dialog.evaluate("(el) => el.open")
    assert page.locator("#detail-manufacturer").inner_text() == "Cookiecad"
    assert page.locator("#detail-name").inner_text() == "Witchcraft"
    assert page.locator("#detail-colors").inner_text() == "#AA0055, #6633FF"
    assert "conic-gradient" in page.locator("#detail-swatch").get_attribute("style")

    page.get_by_role("button", name="Close filament details").click()
    assert not dialog.evaluate("(el) => el.open")
    assert swatch.evaluate("(el) => document.activeElement === el")
    if touch:
        swatch.tap()
        assert dialog.evaluate("(el) => el.open")
        page.keyboard.press("Escape")
        assert not dialog.evaluate("(el) => el.open")
    context.close()


if __name__ == "__main__":
    html = html_fixture()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            check_viewport(
                browser, html, width=390, height=844, touch=True,
                expected_columns=2,
            )
            check_viewport(
                browser, html, width=800, height=1280, touch=True,
                expected_columns=3,
            )
            check_viewport(
                browser, html, width=1280, height=800, touch=False,
                expected_columns=3,
            )
        finally:
            browser.close()
    print("Responsive phone, tablet, and desktop filament details passed.")
