import dash_bootstrap_components as dbc
from dash import dcc, html

def get_page_2_layout():
    return dbc.Container(
        [
            html.H2("📈 Trend Analysis", className="text-center my-3"),

            dbc.Row(
                dbc.Col(
                    [
                        html.Label("Select Analysis Type:", className="fw-bold"),
                        dcc.Dropdown(
                            id="trend-type-dropdown",
                            options=[
                                {"label": "Nutrient Comparison", "value": "comparison"},
                                {"label": "Population vs Deficiency", "value": "population"},
                                {"label": "Regional Ranking", "value": "ranking"},
                            ],
                            value="comparison",
                            clearable=False,
                        ),
                    ],
                    md=4, xs=12,
                ),
                className="g-3 mb-3",
            ),

            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="trend-chart-1"), md=6, className="graph-container"),
                    dbc.Col(dcc.Graph(id="trend-chart-2"), md=6, className="graph-container"),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="trend-chart-3"), md=12, className="graph-container"),
                ],
                className="mb-4",
            ),
            dbc.Row(
                dbc.Col(html.Div(id="trend-insights"), md=12),
            ),
        ],
        fluid=True,
    )
