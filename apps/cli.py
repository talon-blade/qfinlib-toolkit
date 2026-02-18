from __future__ import annotations

import argparse
import curses
from dataclasses import dataclass
from typing import Callable

from apps.market_monitor.__main__ import main as market_monitor_main
from apps.market_monitor.swap_rate_monitor import main as swap_rate_monitor_main
from apps.strategy_lab.__main__ import main as strategy_lab_main
from apps.trade_pricing.__main__ import main as trade_pricing_main


@dataclass(frozen=True)
class DashboardApp:
    name: str
    command: str
    description: str
    runner: Callable[[], None]


DASHBOARDS = [
    DashboardApp(
        name="Market Monitor",
        command="qfinlib-toolkit.market-monitor.equity_monitor",
        description="Launch equity market monitor dashboard (port 8051).",
        runner=market_monitor_main,
    ),
    DashboardApp(
        name="Swap Rate Monitor",
        command="qfinlib-toolkit.market-monitor.swap-rate-monitor",
        description="Launch swap rate monitor dashboard (port 8061).",
        runner=swap_rate_monitor_main,
    ),
    DashboardApp(
        name="Trade Pricing",
        command="qfinlib-toolkit.trade-pricing.trade-pricer",
        description="Launch trade pricing dashboard (port 8052).",
        runner=trade_pricing_main,
    ),
    DashboardApp(
        name="Strategy Lab",
        command="qfinlib-toolkit.strategy-lab.strategy-generator",
        description="Launch strategy lab dashboard (port 8053).",
        runner=strategy_lab_main,
    ),
]


HINT_TEXT = (
    "Hint: run `qfinlib-toolkit -browse` to pick a dashboard with ↑/↓ and Enter, "
    "or run one of the direct commands listed by `qfinlib-toolkit --help`."
)


class HintingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - argparse exits
        self.print_usage()
        self.exit(2, f"Error: {message}\n{HINT_TEXT}\n")


def _render_menu(stdscr: curses.window, selected_index: int) -> None:
    stdscr.clear()
    stdscr.addstr(0, 0, "qfinlib-toolkit dashboard browser")
    stdscr.addstr(1, 0, "Use ↑/↓ to move and Enter to launch.")

    for idx, app in enumerate(DASHBOARDS):
        prefix = ">" if idx == selected_index else " "
        style = curses.A_REVERSE if idx == selected_index else curses.A_NORMAL
        stdscr.addstr(3 + idx, 0, f"{prefix} {app.name} - {app.command}", style)

    stdscr.addstr(4 + len(DASHBOARDS), 0, "Press q or Esc to exit without launching.")
    stdscr.refresh()


def _select_dashboard_curses(stdscr: curses.window) -> DashboardApp | None:
    curses.curs_set(0)
    selected = 0

    while True:
        _render_menu(stdscr, selected)
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % len(DASHBOARDS)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % len(DASHBOARDS)
        elif key in (10, 13, curses.KEY_ENTER):
            return DASHBOARDS[selected]
        elif key in (27, ord("q")):
            return None


def browse_dashboards() -> None:
    """Open an interactive dashboard picker and run the selected app."""
    try:
        selected = curses.wrapper(_select_dashboard_curses)
    except curses.error:
        print("Interactive browser is unavailable in this terminal.")
        print(HINT_TEXT)
        return

    if selected is None:
        print("No dashboard selected.")
        return

    print(f"Launching {selected.name} with `{selected.command}`...")
    selected.runner()


def _build_parser() -> argparse.ArgumentParser:
    parser = HintingArgumentParser(
        prog="qfinlib-toolkit",
        description="Entry command for qfinlib toolkit dashboards.",
        epilog=HINT_TEXT,
    )
    parser.add_argument(
        "-browse",
        "--browse",
        action="store_true",
        help="Open interactive dashboard browser.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.browse:
        browse_dashboards()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
