"""Shared utilities for qfinlib Dash tools."""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import numpy as np
import pandas as pd

_spec = importlib.util.find_spec("qfinlib")
qfinlib = importlib.util.module_from_spec(_spec) if _spec else None
if _spec and _spec.loader:
    _spec.loader.exec_module(qfinlib)

try:
    from qfinlib.market.container import MarketContainer
    from qfinlib.market.data.loader import DataLoader
    from qfinlib.market.data.random_provider import RandomMarketDataProvider
except Exception:  # pragma: no cover - import fallback when qfinlib missing
    MarketContainer = None
    DataLoader = None
    RandomMarketDataProvider = None

_provider = RandomMarketDataProvider(seed=42) if RandomMarketDataProvider else None
_loader = DataLoader(_provider) if _provider and DataLoader else None


def _market_snapshot(as_of: Optional[date] = None) -> Optional[MarketContainer]:
    """Build a qfinlib MarketContainer when dependencies are present."""

    if not _loader:
        return None

    return _loader.load(as_of=as_of)


def _geometric_brownian_walk(periods: int, start: float, drift: float, vol: float, seed: Optional[int]) -> pd.Series:
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    increments = rng.normal((drift - 0.5 * vol**2) * dt, vol * np.sqrt(dt), size=periods)
    return pd.Series(start * np.exp(np.cumsum(increments)))


def load_equity_history(symbol: str, periods: int = 120) -> pd.DataFrame:
    """Return an equity history for monitoring.

    When qfinlib is available, synthesize the path from its market data
    primitives (rates drive drift, vol surfaces drive variance). Otherwise
    fall back to a deterministic random walk so the dashboards still render in
    isolated environments.
    """

    market = _market_snapshot()
    idx = pd.date_range(end=datetime.utcnow(), periods=periods, freq="D")

    if market:
        drift = float(market.data.get("forward_rate", market.data.get("discount_rate", 0.01)))
        vol = float(market.data.get("volatility", 0.2))
        start = float(market.data.get("fx_rates", {}).get("spot", 100.0)) * 100.0
        series = _geometric_brownian_walk(periods=periods, start=start, drift=drift, vol=vol, seed=len(symbol))
        return pd.DataFrame({"close": series.values}, index=idx)

    series = _geometric_brownian_walk(periods=periods, start=100.0, drift=0.01, vol=0.2, seed=len(symbol))
    return pd.DataFrame({"close": series.values}, index=idx)


def load_option_surface(spot: float, maturities: list[int], strikes: list[float]) -> pd.DataFrame:
    """Generate a simple implied-vol surface or reuse qfinlib market surfaces."""

    market = _market_snapshot()
    vol_surface_name = getattr(_provider, "vol_surface_name", "vol_surface")
    if market:
        surface = market.get_surface(vol_surface_name)
        if surface:
            rows = []
            for t in maturities:
                expiry = t / 365
                for k in strikes:
                    vol = float(surface(expiry, k, spot))
                    rows.append({"maturity": t, "strike": k, "vol": vol})
            return pd.DataFrame(rows)

    rows = []
    for t in maturities:
        for k in strikes:
            vol = 0.15 + 0.25 * abs(np.log(k / spot)) + 0.005 * t / 365
            rows.append({"maturity": t, "strike": k, "vol": vol})
    return pd.DataFrame(rows)


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    metrics: dict[str, float]


def run_moving_average_backtest(symbol: str, periods: int = 250, fast: int = 20, slow: int = 60) -> BacktestResult:
    prices = load_equity_history(symbol=symbol, periods=periods).copy()
    prices["fast_ma"] = prices["close"].rolling(fast).mean()
    prices["slow_ma"] = prices["close"].rolling(slow).mean()
    prices["signal"] = np.where(prices["fast_ma"] > prices["slow_ma"], 1, -1)
    prices["pnl"] = prices["signal"].shift(1) * prices["close"].pct_change().fillna(0)
    prices["equity"] = (1 + prices["pnl"]).cumprod()

    trades = prices.loc[prices["signal"].diff().fillna(0).ne(0), ["signal", "close"]]
    trades = trades.rename(columns={"close": "fill_price"})

    metrics = {
        "annualized_return": prices["pnl"].mean() * 252,
        "annualized_vol": prices["pnl"].std() * np.sqrt(252),
        "sharpe": (prices["pnl"].mean() * 252) / (prices["pnl"].std() * np.sqrt(252) + 1e-9),
    }
    return BacktestResult(equity_curve=prices["equity"], trades=trades, metrics=metrics)


def load_swap_curve(currency: str = "USD") -> pd.DataFrame:
    """Return a basic swap curve for dashboarding."""

    market = _market_snapshot()
    tenors_years = np.array([1, 2, 3, 5, 7, 10, 20, 30], dtype=float)

    if market:
        base_rate = float(market.data.get("discount_rate", market.data.get("forward_rate", 0.025)))
        slope = float(market.data.get("volatility", 0.2)) * 0.02
    else:
        base_rate = 0.02
        slope = 0.004

    curve = base_rate + slope * np.log1p(tenors_years)
    curve = curve + 0.0005 * np.sin(tenors_years)

    return pd.DataFrame({
        "currency": currency,
        "tenor_years": tenors_years,
        "swap_rate": curve,
    })
