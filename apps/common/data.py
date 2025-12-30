"""Shared utilities for qfinlib Dash tools."""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

_spec = importlib.util.find_spec("qfinlib")
qfinlib = importlib.util.module_from_spec(_spec) if _spec else None
if _spec and _spec.loader:
    _spec.loader.exec_module(qfinlib)


def _random_walk(periods: int, start: float = 100.0, seed: Optional[int] = None) -> pd.Series:
    rng = np.random.default_rng(seed)
    steps = rng.normal(loc=0.0005, scale=0.02, size=periods)
    return pd.Series(start * np.exp(np.cumsum(steps)))


def load_equity_history(symbol: str, periods: int = 120) -> pd.DataFrame:
    """Return an equity history for monitoring.

    If qfinlib is available, attempts to use its market data adapters; otherwise
    falls back to a simple random walk so the dashboards still render in
    isolated environments.
    """

    if qfinlib:
        market_loader = getattr(qfinlib, "marketdata", None) or getattr(qfinlib, "data", None)
        if market_loader and hasattr(market_loader, "load_ohlcv"):
            end = datetime.utcnow()
            start = end - timedelta(days=periods)
            df = market_loader.load_ohlcv(symbol=symbol, start=start, end=end)
            return df

    idx = pd.date_range(end=datetime.utcnow(), periods=periods, freq="D")
    series = _random_walk(periods=periods, seed=len(symbol))
    return pd.DataFrame({"close": series.values}, index=idx)


def load_option_surface(spot: float, maturities: list[int], strikes: list[float]) -> pd.DataFrame:
    """Generate a simple implied-vol surface or reuse qfinlib if present."""
    if qfinlib:
        pricing = getattr(qfinlib, "pricing", None)
        surface_builder = getattr(pricing, "implied_vol_surface", None) if pricing else None
        if surface_builder:
            return surface_builder(spot=spot, maturities=maturities, strikes=strikes)

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
