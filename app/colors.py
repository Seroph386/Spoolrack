"""CSS colors for Spoolman filament swatches.

Spoolman uses color_hex for single colors and multi_color_hexes (a
comma-separated string) for multicolor filaments.
"""


def _css_hex(value):
    """Return a safe CSS hex color or None for invalid input."""
    if not isinstance(value, str):
        return None
    hex_code = value.strip().lstrip("#")
    if len(hex_code) not in (3, 4, 6, 8):
        return None
    if not all(character in "0123456789abcdefABCDEF" for character in hex_code):
        return None
    return f"#{hex_code}"



def filament_color_codes(filament):
    """Return the validated hexadecimal colors Spoolman provides."""
    raw = filament.get("multi_color_hexes")
    if isinstance(raw, str):
        colors = [color for item in raw.split(",") if (color := _css_hex(item))]
        if colors:
            return colors
    single = _css_hex(filament.get("color_hex"))
    return [single] if single else []


def filament_background(filament):
    """Build an inline CSS background for a Spoolman filament.

    Coaxial multicolor filament gets equally sized pie slices because its
    colors coexist. Longitudinal color changes get a smooth gradient.
    """
    raw_colors = filament.get("multi_color_hexes")
    colors = (
        [color for part in raw_colors.split(",") if (color := _css_hex(part))]
        if isinstance(raw_colors, str)
        else []
    )

    if len(colors) >= 2:
        if filament.get("multi_color_direction") == "longitudinal":
            return f"linear-gradient(90deg, {', '.join(colors)})"
        count = len(colors)
        slices = [
            f"{color} {100 * index / count:.3f}% {100 * (index + 1) / count:.3f}%"
            for index, color in enumerate(colors)
        ]
        return f"conic-gradient({', '.join(slices)})"

    if colors:
        return colors[0]

    return _css_hex(filament.get("color_hex")) or "#888888"
