#!/usr/bin/env bash
set -euo pipefail

# Helper to run Docker Compose, supporting both the Docker CLI plugin (`docker compose`)
# and the legacy standalone binary (`docker-compose`).

if docker compose version >/dev/null 2>&1; then
  exec docker compose "$@"
elif command -v docker-compose >/dev/null 2>&1; then
  exec docker-compose "$@"
else
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker CLI not found. Install Docker Desktop (includes the Compose plugin) and ensure the Docker app is running." >&2
  else
    echo "Docker Compose not found. Install the Compose plugin (Docker Desktop) or the legacy docker-compose binary (e.g., brew install docker-compose or pip install docker-compose)." >&2
  fi
  exit 1
fi
