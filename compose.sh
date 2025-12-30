#!/usr/bin/env bash
set -euo pipefail

# Helper to run Docker Compose, supporting both the Docker CLI plugin (`docker compose`)
# and the legacy standalone binary (`docker-compose`).

if docker compose version >/dev/null 2>&1; then
  exec docker compose "$@"
elif command -v docker-compose >/dev/null 2>&1; then
  exec docker-compose "$@"
else
  echo "Docker Compose not found. Install Docker Desktop (includes Compose plugin) or the standalone docker-compose binary." >&2
  exit 1
fi
