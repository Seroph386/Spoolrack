import os
from pathlib import Path
from html import escape

import httpx
import yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.colors import filament_background

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
                dots.append(f'<span class="dot" style="background:{background}"></span>')
            cells.append(f'<article><strong>{escape(str(loc))}</strong><span>{len(matched)}/{capacity}</span><div class="dots">{"".join(dots)}</div></article>')
        sections.append(f'<section><h2>{escape(str(rack["name"]))}</h2><div class="grid" style="--cols:{int(rack["columns"])}">{"".join(cells)}</div></section>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="30"><title>Spoolrack</title><style>
    body{{background:#111827;color:#f9fafb;font-family:system-ui,sans-serif;margin:0;padding:1rem}}
    main{{max-width:1100px;margin:auto}}h1{{margin:.2rem 0 1rem}}h2{{font-size:1.1rem}}
    .grid{{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:.65rem}}
    article{{background:#1f2937;border:1px solid #374151;border-radius:12px;min-height:85px;padding:12px;display:flex;flex-wrap:wrap;align-content:start;justify-content:space-between;gap:8px}}
    .dots{{display:flex;flex-basis:100%;gap:6px;flex-wrap:wrap}}.dot{{width:20px;height:20px;border:1px solid #9ca3af;border-radius:50%}}
    .error{{color:#fca5a5}}@media(max-width:480px){{article{{padding:8px}}}}
    </style></head><body><main><h1>Spoolrack</h1>{error}{"".join(sections)}</main></body></html>"""
