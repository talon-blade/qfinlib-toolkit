from __future__ import annotations

import os

import dash
from dash import Dash, Input, Output, dcc, html
import pandas as pd

from apps.common.data import BacktestResult, run_moving_average_backtest

SYMBOLS = ["SPY", "QQQ", "EEM", "IWM"]

app: Dash = dash.Dash(__name__)
app.title = "Strategy Lab"

app.layout = html.Div(
    [
        html.H2("Strategy Lab"),
        html.P("Toy moving-average crossover backtest leveraging qfinlib data utilities."),
        html.Div(
            [
                dcc.Dropdown(id="symbol", options=SYMBOLS, value=SYMBOLS[0]),
                dcc.Input(id="fast", type="number", value=20, placeholder="Fast MA"),
                dcc.Input(id="slow", type="number", value=60, placeholder="Slow MA"),
                dcc.Input(id="lookback", type="number", value=250, placeholder="Lookback"),
            ],
            className="controls",
        ),
        html.Div(id="metrics", className="metric"),
        dcc.Graph(id="equity"),
        dcc.Graph(id="signals"),
    ]
)


def render_metrics(result: BacktestResult) -> str:
    return (
        f"Ann. Return: {result.metrics['annualized_return']:.2%} | "
        f"Ann. Vol: {result.metrics['annualized_vol']:.2%} | "
        f"Sharpe: {result.metrics['sharpe']:.2f}"
    )


@app.callback(
    Output("metrics", "children"),
    Output("equity", "figure"),
    Output("signals", "figure"),
    Input("symbol", "value"),
    Input("fast", "value"),
    Input("slow", "value"),
    Input("lookback", "value"),
)
def run_backtest(symbol: str, fast: int, slow: int, lookback: int):
    result = run_moving_average_backtest(symbol=symbol, periods=int(lookback), fast=int(fast), slow=int(slow))

    equity_df = result.equity_curve.rename_axis("date").reset_index()
    trades_df = result.trades.rename_axis("date").reset_index()

    equity_fig = {
        "data": [
            {
                "x": equity_df["date"],
                "y": equity_df["equity"],
                "mode": "lines",
                "name": "Equity",
            }
        ],
        "layout": {"title": "Equity Curve", "template": "plotly_white"},
    }

    signal_fig = {
        "data": [
            {
                "x": trades_df["date"],
                "y": trades_df["fill_price"],
                "mode": "markers", 
                "marker": {"color": trades_df["signal"].map({1: "green", -1: "red"}), "size": 10},
            }
        ],
        "layout": {"title": "Signal Changes", "template": "plotly_white"},
    }

    return render_metrics(result), equity_fig, signal_fig


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8053"))
    app.run(host="0.0.0.0", port=port, debug=False)
