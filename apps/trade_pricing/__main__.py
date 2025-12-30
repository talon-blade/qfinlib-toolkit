from __future__ import annotations

import math
import os

import dash
from dash import Dash, Input, Output, dcc, html
from scipy.stats import norm

from apps.common.data import load_option_surface


def black_scholes_call(spot: float, strike: float, rate: float, vol: float, maturity: float) -> float:
    tau = maturity / 252
    d1 = (math.log(spot / strike) + (rate + 0.5 * vol**2) * tau) / (vol * math.sqrt(tau))
    d2 = d1 - vol * math.sqrt(tau)
    return spot * norm.cdf(d1) - strike * math.exp(-rate * tau) * norm.cdf(d2)


app: Dash = dash.Dash(__name__)
app.title = "Trade Pricing"

app.layout = html.Div(
    [
        html.H2("Trade Pricing"),
        html.P("Vanilla option pricer that can be swapped for qfinlib pricers in production."),
        html.Div(
            [
                dcc.Input(id="spot", type="number", value=100, placeholder="Spot"),
                dcc.Input(id="strike", type="number", value=100, placeholder="Strike"),
                dcc.Input(id="vol", type="number", value=0.2, placeholder="Vol"),
                dcc.Input(id="rate", type="number", value=0.02, placeholder="Rate"),
                dcc.Input(id="tenor", type="number", value=90, placeholder="Tenor (days)"),
            ],
            className="controls",
        ),
        html.Div(id="price-output", className="metric"),
        dcc.Graph(id="surface"),
    ]
)


@app.callback(
    Output("price-output", "children"),
    Output("surface", "figure"),
    Input("spot", "value"),
    Input("strike", "value"),
    Input("vol", "value"),
    Input("rate", "value"),
    Input("tenor", "value"),
)
def update_price(spot: float, strike: float, vol: float, rate: float, tenor: float):
    price = black_scholes_call(float(spot), float(strike), float(rate), float(vol), float(tenor))
    maturities = [30, 60, 90, 180, 360]
    strikes = [strike * f for f in [0.8, 0.9, 1.0, 1.1, 1.2]]
    surface = load_option_surface(spot=float(spot), maturities=maturities, strikes=strikes)

    fig = {
        "data": [
            {
                "type": "scatter3d",
                "x": surface["strike"],
                "y": surface["maturity"],
                "z": surface["vol"],
                "mode": "markers",
                "marker": {"size": 5},
            }
        ],
        "layout": {"scene": {"xaxis": {"title": "Strike"}, "yaxis": {"title": "Maturity"}, "zaxis": {"title": "Vol"}}},
    }

    return f"Call price: {price:.2f}", fig


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8052"))
    app.run_server(host="0.0.0.0", port=port, debug=False)
