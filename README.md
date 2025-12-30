# qfinlib Dash Toolkit

Suite of qfinlib-backed Dash tools covering market monitoring, trade pricing, and fast strategy experimentation. The stack is fully dockerized and ships with a simple launcher that opens the portal entry point.

## Contents
- **Portal (port 8050):** landing page that links to each tool.
- **Market Monitor (port 8051):** lightweight market overview driven by qfinlib market data adapters.
- **Trade Pricing (port 8052):** vanilla option pricing plus implied-vol surface sketch.
- **Strategy Lab (port 8053):** moving-average crossover backtester.

## Getting started
1. Build and start the stack (uses either `docker compose` or `docker-compose` automatically):
   ```bash
   ./compose.sh up --build
   ```
   If you prefer calling Compose directly, use `docker compose up --build` (Docker Desktop) or
   `docker-compose up --build` (legacy binary).

2. Open the portal (or run the launcher script to open it automatically):
   ```bash
   python launch.py
   ```
   The portal lives at http://localhost:8050 by default.

3. Navigate to each tool from the portal cards. Ports can be customized in `docker-compose.yml` if needed.

## Running a single app locally (without Docker)
Activate a virtual environment, install `requirements.txt`, then run a module directly, e.g.:
```bash
python -m apps.market_monitor
```

## Packaging a desktop launcher
If you need a Windows `.exe` launcher, build one from `launch.py` with `pyinstaller`:
```bash
pip install pyinstaller
pyinstaller --onefile launch.py
```
The generated binary simply opens the portal URL once the Docker services are running.

## Customization notes
- Swap the placeholder data generators in `apps/common/data.py` with your preferred qfinlib adapters for production feeds.
- The shared `Dockerfile` accepts `APP_MODULE` and `PORT` build args/env vars so you can run any module with the same base image.
