import dash_bootstrap_components as dbc
from dash import dcc, html

def get_page_3_layout():
    return dbc.Container(
        [
            html.H2("🔍 Detailed Analytics", className="text-center my-3"),

            dbc.Row(
                dbc.Col(
                    [
                        html.Label("Select Analysis Focus:", className="fw-bold"),
                        dcc.Dropdown(
                            id="analytics-focus-dropdown",
                            options=[
                                {"label": "High-Risk Areas", "value": "high_risk"},
                                {"label": "Population Density", "value": "density"},
                                {"label": "Multi-Nutrient Deficiency", "value": "multi_nutrient"},
                            ],
                            value="high_risk",
                            clearable=False,
                        ),
                    ],
                    md=4, xs=12,
                ),
                className="g-3 mb-3",
            ),

            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="analytics-chart-1"), md=4, className="graph-container"),
                    dbc.Col(dcc.Graph(id="analytics-chart-2"), md=4, className="graph-container"),
                    dbc.Col(dcc.Graph(id="analytics-chart-3"), md=4, className="graph-container"),
                ],
                className="mb-4",
            ),
            dbc.Row(
                dbc.Col(html.Div(id="analytics-insights"), md=12),
            ),
        ],
        fluid=True,
    )
