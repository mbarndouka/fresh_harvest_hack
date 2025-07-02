"""
Page 2: Trend Analysis Layout
"""
from dash import dcc, html

def get_page_2_layout():
    """Return the layout for Page 2 - Trend Analysis"""
    return html.Div([
        html.H2("📈 Trend Analysis", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Select Analysis Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='trend-type-dropdown',
                options=[
                    {'label': 'Nutrient Comparison', 'value': 'comparison'},
                    {'label': 'Population vs Deficiency', 'value': 'population'},
                    {'label': 'Regional Ranking', 'value': 'ranking'}
                ],
                value='comparison'
            )
        ], style={'width': '40%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='trend-chart-1')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='trend-chart-2')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='trend-chart-3')
        ], style={'width': '100%', 'margin': '20px 0'}),
        
        html.Div(id='trend-insights', style={'margin': '20px'})
    ])
