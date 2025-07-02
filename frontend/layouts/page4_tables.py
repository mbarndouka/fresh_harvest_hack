"""
Page 4: Data Tables Layout
"""
from dash import dcc, html

def get_page_4_layout():
    """Return the layout for Page 4 - Data Tables"""
    return html.Div([
        html.H2("📋 Data Tables", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Select Data Level:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='table-level-dropdown',
                options=[
                    {'label': 'Province Data', 'value': 'province'},
                    {'label': 'District Data', 'value': 'district'},
                    {'label': 'Comparative Analysis', 'value': 'comparative'}
                ],
                value='province'
            )
        ], style={'width': '40%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            html.H3("📊 Complete Dataset", style={'textAlign': 'center'}),
            html.Div(id='complete-data-table')
        ], style={'width': '50%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            html.H3("📈 Statistical Summary", style={'textAlign': 'center'}),
            html.Div(id='statistical-summary')
        ], style={'width': '45%', 'display': 'inline-block', 'margin': '20px'}),
        
        html.Div([
            html.H3("🎯 Key Insights", style={'textAlign': 'center'}),
            html.Div(id='key-insights-table')
        ], style={'width': '100%', 'margin': '20px'})
    ])
