from __future__ import annotations

import os

import dash
from dash import Dash, Input, Output, dcc, html

from apps.common.data import load_equity_history

SYMBOLS = ["SPY", "QQQ", "GLD", "TLT", "BTC-USD"]

app: Dash = dash.Dash(__name__)
app.title = "Market Monitor"

app.layout = html.Div(
    [
        html.H2("Market Monitor"),
        html.P("Quick view of recent performance for popular tickers using qfinlib data providers."),
        dcc.Dropdown(id="symbol", options=SYMBOLS, value=SYMBOLS[0]),
        dcc.Slider(id="lookback", min=60, max=365, step=15, value=180, marks=None, tooltip={"placement": "bottom"}),
        dcc.Graph(id="price-graph"),
    ]
)


@app.callback(Output("price-graph", "figure"), Input("symbol", "value"), Input("lookback", "value"))
def update_chart(symbol: str, lookback: int):
    df = load_equity_history(symbol=symbol, periods=int(lookback))
    df = df.rename_axis("date").reset_index()

    return {
        "data": [
            {
                "x": df["date"],
                "y": df["close"],
                "mode": "lines",
                "name": symbol,
            }
        ],
        "layout": {
            "title": f"{symbol} Close",
            "template": "plotly_white",
            "yaxis": {"title": "Price"},
        },
    }


def main() -> None:
    port = int(os.getenv("PORT", "8051"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
