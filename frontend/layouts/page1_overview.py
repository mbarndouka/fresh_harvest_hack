# layouts/page1_overview.py
# ──────────────────────────────────────────────────────────────────────────────
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.io as pio

pio.templates.default = "plotly_white"

def get_page_1_layout():
    """Overview page:
       ┌──────────────┐
       │   Heading    │
       ├──────────────┤
       │ Filters      │   ← three dropdowns side-by-side
       ├──────────────┤
       │ Map & Charts │
    """
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H2("Overview Maps", className="text-center mb-4"),
                    width=12
                )
            ),

            # ─── filter row (flex) ─────────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Micronutrient:", className="fw-bold"),
                            dcc.Dropdown(
                                id="nutrient-dropdown",
                                options=[
                                    {"label": "Vitamin A", "value": "Vitamin_A"},
                                    {"label": "Iron",      "value": "Iron"},
                                    {"label": "Zinc",      "value": "Zinc"},
                                ],
                                value="Vitamin_A",
                                clearable=False,
                            ),
                        ],
                        md=4, xs=12, className="mb-3 flex-item"
                    ),

                    dbc.Col(
                        [
                            html.Label("Select Indicator:", className="fw-bold"),
                            dcc.Dropdown(
                                id="indicator-dropdown",
                                options=[
                                    {"label": "Consumption Adequacy", "value": "consumption"},
                                    {"label": "Production Adequacy",  "value": "production"},
                                    {"label": "Stunting (% < –2 SD)",  "value": "stunting"},
                                    {"label": "Gap Score",             "value": "gapscore"},
                                ],
                                value="consumption",
                                clearable=False,
                            ),
                        ],
                        md=4, xs=12, className="mb-3 flex-item"
                    ),

                    dbc.Col(
                        [
                            html.Label("Select Map Level:", className="fw-bold"),
                            dcc.Dropdown(
                                id="map-level-dropdown",
                                options=[
                                    {"label": "Province Level",                  "value": "province"},
                                    {"label": "District Level",                  "value": "district"},
                                    {"label": "Layered (District + Province)",   "value": "layered"},
                                ],
                                value="province",
                                clearable=False,
                            ),
                        ],
                        md=4, xs=12, className="mb-3 flex-item"
                    ),
                ],
                className="flex-row g-3",
            ),

            # ─── choropleth map ────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id="nutrient-map", className="nutrient-map"),
                    md=12,
                    className="graph-container",
                ),
                className="gx-0",
                style={"marginBottom": "-1rem"},
            ),

            # ─── bar chart ────────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id="nutrient-bar-chart"),
                    md=12,
                    className="mb-1",
                )
            ),

            # ─── data overview & stats ─────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Data Overview"),
                                dbc.CardBody(html.Div(id="data-table")),
                            ],
                            className="h-100",
                        ),
                        md=6,
                        xs=12,
                        className="mb-4 flex-item",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Summary Statistics"),
                                dbc.CardBody(html.Div(id="summary-stats")),
                            ],
                            className="h-100",
                        ),
                        md=6,
                        xs=12,
                        className="mb-4 flex-item",
                    ),
                ],
                className="flex-row g-3",
            ),
        ],
        fluid=True,
    )
