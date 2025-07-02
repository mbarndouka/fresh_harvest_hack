"""
Page 1: Overview Maps Layout
"""
from dash import dcc, html

def get_page_1_layout():
    """Return the layout for Page 1 - Overview Maps"""
    return html.Div([
        html.H2("📊 Overview Maps", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Select Micronutrient:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='nutrient-dropdown',
                options=[
                    {'label': 'Vitamin A', 'value': 'Vitamin_A'},
                    {'label': 'Iron', 'value': 'Iron'},
                    {'label': 'Zinc', 'value': 'Zinc'}
                ],
                value='Vitamin_A'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            html.Label("Select Map Level:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='map-level-dropdown',
                options=[
                    {'label': 'Province Level', 'value': 'province'},
                    {'label': 'District Level', 'value': 'district'},
                    {'label': 'Layered (Districts + Provinces)', 'value': 'layered'}
                ],
                value='province'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='nutrient-bar-chart')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='nutrient-map')
        ], style={'width': '100%', 'margin': '20px 0'}),
        
        html.Div([
            html.H3("Data Overview", style={'textAlign': 'center'}),
            html.Div(id='data-table')
        ], style={'width': '48%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            html.H3("Regional Overview", style={'textAlign': 'center'}),
            html.Div(id='summary-stats')
        ], style={'margin': '20px'})
    ])
