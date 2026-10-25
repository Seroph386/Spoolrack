# Spoolrack

Read-only Spoolman rack display, targeting Raspberry Pi 3 (ARM64).

## Planned milestones

1. Lightweight dashboard displaying a 3-column by 5-row rack, locations F-001 through F-015, capacity four spools each, and spool colors/occupancy from the Spoolman API.
2. Grid-based rack layout editor with drag-and-drop location assignments and per-bin capacity.
3. Configurable screens, dedicated display URLs, and Fire HD kiosk view.
4. YAML import/export, configuration validation, tests, and ARM64 Docker deployment.

Spoolman remains the source of truth for inventory; Spoolrack does not modify filament records. FilaBridge handles NFC and printer integration.
