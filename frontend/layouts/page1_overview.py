# page1_overview.py
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.io as pio

pio.templates.default = "plotly_white"      # keep the global style

def get_page_1_layout():
    """Overview page: filter row ➜ full-width map ➜ bar chart ➜ summary cards"""
    return dbc.Container(
        [
            html.H2("📊 Overview Maps", className="text-center my-3"),

            # ---------- filters ----------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Micronutrient:", className="fw-bold"),
                            dcc.Dropdown(
                                id="nutrient-dropdown",
                                options=[{"label": n, "value": n.replace(" ", "_")}
                                         for n in ["Vitamin A", "Iron", "Zinc"]],
                                value="Vitamin_A",
                                clearable=False,
                            ),
                        ],
                        md=4, xs=12,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            html.Label("Select Map Level:", className="fw-bold"),
                            dcc.Dropdown(
                                id="map-level-dropdown",
                                options=[
                                    {"label": "Province Level", "value": "province"},
                                    {"label": "District Level", "value": "district"},
                                    {"label": "Layered (Districts + Provinces)", "value": "layered"},
                                ],
                                value="province",
                                clearable=False,
                            ),
                        ],
                        md=4, xs=12,
                        className="mb-3",
                    ),
                ],
                className="g-3",
            ),

            # ---------- full-width map ----------
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="nutrient-map",
                        style={"width": "100%"},
                        config={"responsive": True},
                    ),
                    md=12,
                    className="map-container",
                ),
                className="gx-0 mb-4",   # gx-0 kills Bootstrap’s horizontal gutter
            ),


            # ---------- bar chart ----------
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id="nutrient-bar-chart"),
                    md=12,
                    className="graph-container",
                ),
                className="mb-4",
            ),

            # ---------- summary cards ----------
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
                        md=6, className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Regional Overview"),
                                dbc.CardBody(html.Div(id="summary-stats")),
                            ],
                            className="h-100",
                        ),
                        md=6, className="mb-4",
                    ),
                ]
            ),
        ],
        fluid=True,
    )
