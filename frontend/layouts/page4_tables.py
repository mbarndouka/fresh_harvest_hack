import dash_bootstrap_components as dbc
from dash import dcc, html

def get_page_4_layout():
    return dbc.Container(
        [
            html.H2("📋 Data Tables", className="text-center my-3"),

            dbc.Row(
                dbc.Col(
                    [
                        html.Label("Select Data Level:", className="fw-bold"),
                        dcc.Dropdown(
                            id="table-level-dropdown",
                            options=[
                                {"label": "Province Data", "value": "province"},
                                {"label": "District Data", "value": "district"},
                                {"label": "Comparative Analysis", "value": "comparative"},
                            ],
                            value="province",
                            clearable=False,
                        ),
                    ],
                    md=4, xs=12,
                ),
                className="g-3 mb-4",
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("📊 Complete Dataset", className="text-center"),
                            html.Div(id="complete-data-table"),
                        ],
                        md=6, className="mb-4",
                    ),
                    dbc.Col(
                        [
                            html.H4("📈 Statistical Summary", className="text-center"),
                            html.Div(id="statistical-summary"),
                        ],
                        md=6, className="mb-4",
                    ),
                ]
            ),

            dbc.Row(
                dbc.Col(
                    [
                        html.H4("🎯 Key Insights", className="text-center"),
                        html.Div(id="key-insights-table"),
                    ],
                    md=12,
                )
            ),
        ],
        fluid=True,
    )
