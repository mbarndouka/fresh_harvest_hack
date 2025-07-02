"""
Page 3: Detailed Analytics Layout
"""
from dash import dcc, html

def get_page_3_layout():
    """Return the layout for Page 3 - Detailed Analytics"""
    return html.Div([
        html.H2("🔍 Detailed Analytics", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Select Analysis Focus:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='analytics-focus-dropdown',
                options=[
                    {'label': 'High-Risk Areas', 'value': 'high_risk'},
                    {'label': 'Population Density Analysis', 'value': 'density'},
                    {'label': 'Multi-Nutrient Deficiency', 'value': 'multi_nutrient'}
                ],
                value='high_risk'
            )
        ], style={'width': '40%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='analytics-chart-1')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='analytics-chart-2')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='analytics-chart-3')
        ], style={'width': '100%', 'margin': '20px 0'}),
        
        html.Div(id='analytics-insights', style={'margin': '20px'})
    ])
