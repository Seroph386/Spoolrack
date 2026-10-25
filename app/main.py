import os
from pathlib import Path
from html import escape

import httpx
import yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.colors import filament_background, filament_color_codes
from app.ui import CSS, SCRIPT

app = FastAPI(title="Spoolrack")
SPOOLMAN_URL = os.environ.get("SPOOLMAN_URL", "http://spoolman:8000").rstrip("/")
CONFIG_PATH = Path(os.environ.get("RACK_CONFIG", "/app/config/racks.yaml"))


async def inventory():
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(f"{SPOOLMAN_URL}/api/v1/spool")
        response.raise_for_status()
        return response.json()


def rack_config():
    config = yaml.safe_load(CONFIG_PATH.read_text())
    return config["racks"]


def location_name(spool):
    location = spool.get("location")
    if isinstance(location, dict):
        return str(location.get("name", ""))
    return str(location or "")


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.get("/api/racks")
async def racks():
    return rack_config()


@app.get("/api/inventory")
async def spools():
    return await inventory()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    racks = rack_config()
    try:
        spools = await inventory()
        error = ""
    except (httpx.HTTPError, ValueError) as exc:
        spools = []
        error = f"<p class='error'>Spoolman unavailable: {escape(str(exc))}</p>"

    sections = []
    for rack in racks:
        cells = []
        for loc in rack["locations"]:
            matched = [s for s in spools if location_name(s) == loc]
            capacity = rack.get("default_capacity", 4)
            dots = []
            for spool in matched:
                filament = spool.get("filament") or {}
                background = filament_background(filament)
                name = str(filament.get("name") or "Unnamed filament")
                vendor = filament.get("vendor") or {}
                manufacturer = (
                    vendor.get("name") if isinstance(vendor, dict) else None
                ) or "Unknown manufacturer"
                colors = ", ".join(filament_color_codes(filament)) or "Not specified"
                summary = f"{manufacturer} · {name} · {colors}"
                dots.append(
                    f'<button type="button" class="dot" data-filament '
                    f'data-manufacturer="{escape(str(manufacturer), quote=True)}" '
                    f'data-name="{escape(name, quote=True)}" '
                    f'data-colors="{escape(colors, quote=True)}" '
                    f'aria-label="{escape(summary, quote=True)}" '
                    f'aria-haspopup="dialog" aria-controls="filament-details" '
                    f'title="{escape(summary, quote=True)}" '
                    f'style="background:{background}"></button>'
                )
            cells.append(f'<article><div class="bin-heading"><strong>{escape(str(loc))}</strong><span>{len(matched)}/{capacity}</span></div><div class="dots">{"".join(dots)}</div></article>')
        sections.append(f'<section><h2>{escape(str(rack["name"]))}</h2><div class="grid" style="--cols:{int(rack["columns"])}">{"".join(cells)}</div></section>')
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Spoolrack</title>
  <style>{CSS}</style>
</head>
<body>
  <main><h1>Spoolrack</h1>{error}{"".join(sections)}</main>
  <dialog id="filament-details" aria-labelledby="filament-details-heading">
    <div class="details-panel">
      <div class="details-header">
        <h2 id="filament-details-heading">Filament details</h2>
        <button type="button" class="details-close" id="filament-details-close"
                aria-label="Close filament details">&times;</button>
      </div>
      <span class="detail-swatch" id="detail-swatch" aria-hidden="true"></span>
      <dl class="details-list">
        <div><dt>Manufacturer</dt><dd id="detail-manufacturer"></dd></div>
        <div><dt>Filament</dt><dd id="detail-name"></dd></div>
        <div><dt>Color(s)</dt><dd id="detail-colors"></dd></div>
      </dl>
    </div>
  </dialog>
  <script>{SCRIPT}</script>
</body>
</html>"""
