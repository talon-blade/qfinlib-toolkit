"""Simple launcher that opens the portal URL after containers are running."""
from __future__ import annotations

import os
import time
import webbrowser


PORT = os.getenv("PORT", "8050")
PORTAL_URL = f"http://localhost:{PORT}"


def main() -> None:
    print("Starting qfinlib toolkit launcher…")
    print("Make sure `docker-compose up` is running in another terminal.")
    time.sleep(0.5)
    print(f"Opening {PORTAL_URL}")
    webbrowser.open(PORTAL_URL)


if __name__ == "__main__":
    main()
