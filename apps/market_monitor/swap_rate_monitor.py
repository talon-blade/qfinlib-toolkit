from __future__ import annotations

import os

import dash
from dash import Dash, Input, Output, dcc, html

from apps.common.data import load_swap_curve

CURRENCIES = ["USD", "EUR", "GBP", "JPY"]

app: Dash = dash.Dash(__name__)
app.title = "Swap Rate Monitor"

app.layout = html.Div(
    [
        html.H2("Swap Rate Monitor"),
        html.P("Track the latest swap curve levels across major currencies."),
        dcc.Dropdown(id="currency", options=CURRENCIES, value=CURRENCIES[0]),
        dcc.Graph(id="swap-curve"),
    ]
)


@app.callback(Output("swap-curve", "figure"), Input("currency", "value"))
def update_chart(currency: str):
    df = load_swap_curve(currency=currency)

    return {
        "data": [
            {
                "x": df["tenor_years"],
                "y": df["swap_rate"] * 100,
                "mode": "lines+markers",
                "name": f"{currency} swaps",
            }
        ],
        "layout": {
            "title": f"{currency} swap curve",
            "template": "plotly_white",
            "xaxis": {"title": "Tenor (years)"},
            "yaxis": {"title": "Rate (%)"},
        },
    }


def main() -> None:
    port = int(os.getenv("PORT", "8061"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
