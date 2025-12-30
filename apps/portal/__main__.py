from __future__ import annotations

import os
from textwrap import dedent

import dash
from dash import Dash, dcc, html

APP_LINKS = [
    {
        "name": "Market Monitor",
        "description": "Intraday and historical monitoring of key symbols with charting and stats.",
        "href": "http://localhost:8051",
    },
    {
        "name": "Trade Pricing",
        "description": "Option and structured trade pricing using qfinlib analytics.",
        "href": "http://localhost:8052",
    },
    {
        "name": "Strategy Lab",
        "description": "Moving-average backtests and rapid strategy parameter sweeps.",
        "href": "http://localhost:8053",
    },
]

app: Dash = dash.Dash(__name__)
app.title = "qfinlib Toolkit Portal"

app.layout = html.Div(
    [
        html.H1("qfinlib Toolkit", className="title"),
        html.P(
            dedent(
                """
                Launch point for the qfinlib-powered dashboards. Start the stack with
                `docker-compose up` and click into the tool you want to use.
                """
            ),
            className="subtitle",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3(link["name"]),
                        html.P(link["description"]),
                        html.A("Open", href=link["href"], className="btn"),
                    ],
                    className="card",
                )
                for link in APP_LINKS
            ],
            className="card-grid",
        ),
        html.P(
            "Customize ports and images in docker-compose.yml if you need to align with existing infra.",
            className="footer-note",
        ),
    ],
    className="layout",
)


app.css.append_css(
    {
        "external_url": "https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.min.css"
    }
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    app.run_server(host="0.0.0.0", port=port, debug=False)
