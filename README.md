# Spoolrack

Read-only Spoolman rack display, targeting Raspberry Pi 3 (ARM64).

## Planned milestones

1. Lightweight dashboard displaying a 3-column by 5-row rack, locations F-001 through F-015, capacity four spools each, and spool colors/occupancy from the Spoolman API.
2. Grid-based rack layout editor with drag-and-drop location assignments and per-bin capacity.
3. Configurable screens, dedicated display URLs, and Fire HD kiosk view.
4. YAML import/export, configuration validation, tests, and ARM64 Docker deployment.

Spoolman remains the source of truth for inventory; Spoolrack does not modify filament records. FilaBridge handles NFC and printer integration.

## Docker images (GitHub Container Registry)

The [container-publish workflow](.github/workflows/container-publish.yaml) checks pull requests against `main` by building the image without publishing it. After a merge (a push to `main`), it builds and publishes a multi-architecture Docker image for `linux/amd64` and `linux/arm64` to:

- `ghcr.io/seroph386/spoolrack:latest`
- `ghcr.io/seroph386/spoolrack:sha-<short-commit-sha>`

It can also be manually started from **Actions → Build and publish Docker image → Run workflow** on `main`.

**Bootstrapping:** If the branch does not yet contain a `Dockerfile`, the workflow reports a notice and skips building. The image becomes available once the application and its Dockerfile are merged into `main`.

To run it on `spoolpi` after publishing, replace the local `build: .` definition in the Spoolrack Compose service with `image: ghcr.io/seroph386/spoolrack:latest`, keeping Spoolman connectivity, port mapping, and the configuration volume. Run `docker compose pull spoolrack && docker compose up -d spoolrack` in the existing stack directory.

This workflow **publishes only**; it does not automatically redeploy the Pi. For a private GHCR package, Docker on the Pi must authenticate with an account/token that has permission to pull it (`read:packages`). The repository owner may also need to verify the package's access settings in GitHub.
