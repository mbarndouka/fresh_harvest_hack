import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Import our custom Rwanda map module
from rwanda_map import (
    get_rwanda_data, 
    get_rwanda_district_data,
    create_rwanda_map, 
    create_rwanda_district_map,
    create_rwanda_layered_map,
    get_rwanda_map_info
)

# Get the data from our map module
df = get_rwanda_data()
district_df = get_rwanda_district_data()

# Print map information for debugging
map_info = get_rwanda_map_info()
print("=== Rwanda Map Information ===")
print(f"Geopandas available: {map_info['geopandas_available']}")
print(f"Geographic data loaded: {map_info['geographic_data_loaded']}")
print(f"District data loaded: {map_info['district_data_loaded']}")
print(f"Number of provinces: {map_info['num_provinces']}")
print(f"Number of districts: {map_info['num_districts']}")
print(f"Data source: {map_info['data_source']}")
if map_info['provinces']:
    print(f"Provinces: {', '.join(map_info['provinces'])}")
if map_info.get('districts'):
    print(f"Districts (sample): {', '.join(map_info['districts'][:5])}...")
print("=" * 30)

# Initialize the Dash app
app = dash.Dash(__name__)

# Create map status message
province_status = "🗺️ Geographic Map Available" if map_info['geographic_data_loaded'] else "📊 Using Fallback Visualization"
district_status = "🏘️ District Data Available" if map_info['district_data_loaded'] else "🏘️ District Data Unavailable"
map_color = "#27ae60" if map_info['geographic_data_loaded'] else "#f39c12"

# Define the layout
app.layout = html.Div([
    html.H1("NutriGap Rwanda Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Status indicator
    html.Div([
        html.P([
            html.Span(province_status, style={'color': map_color, 'fontWeight': 'bold'}),
            " | ",
            html.Span(district_status, style={'color': '#3498db', 'fontWeight': 'bold'}),
            f" | Provinces: {map_info['num_provinces']} | Districts: {map_info['num_districts']}"
        ], style={'textAlign': 'center', 'margin': '10px 0', 'fontSize': '14px'})
    ]),
    
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

# Callback for updating charts
@app.callback(
    [Output('nutrient-bar-chart', 'figure'),
     Output('nutrient-map', 'figure'),
     Output('data-table', 'children'),
     Output('summary-stats', 'children')],
    [Input('nutrient-dropdown', 'value'),
     Input('map-level-dropdown', 'value')]
)
def update_charts(selected_nutrient, map_level):
    # Determine which data to use
    current_df = district_df if map_level in ['district', 'layered'] else df
    location_col = 'District' if map_level in ['district', 'layered'] else 'Region'
    
    # Bar chart
    bar_fig = px.bar(
        current_df.head(15) if map_level in ['district', 'layered'] else current_df, 
        x=location_col, 
        y=selected_nutrient,
        title=f'{selected_nutrient.replace("_", " ")} Deficiency by {location_col} (%) - Top 15' if map_level in ['district', 'layered'] else f'{selected_nutrient.replace("_", " ")} Deficiency by {location_col} (%)',
        color=selected_nutrient,
        color_continuous_scale='RdYlBu_r'
    )
    bar_fig.update_layout(
        showlegend=False,
        title_x=0.5,
        height=500,
        margin=dict(t=60, b=40, l=60, r=20),
        xaxis={'tickangle': 45}
    )
    
    # Create appropriate map based on selected level
    map_title = f'{selected_nutrient.replace("_", " ")} Deficiency - Rwanda'
    
    if map_level == 'province':
        map_fig = create_rwanda_map(df, selected_nutrient, map_title)
    elif map_level == 'district':
        map_fig = create_rwanda_district_map(district_df, selected_nutrient, map_title)
    else:  # layered
        map_fig = create_rwanda_layered_map(df, district_df, selected_nutrient, map_title, level='district')
    
    # Data table
    display_df = current_df.head(10) if map_level in ['district', 'layered'] else current_df
    data_table = html.Div([
        html.H4(f"📊 {location_col} Data ({'Top 10' if map_level in ['district', 'layered'] else 'All'})", 
                style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th(location_col, style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th(f'{selected_nutrient.replace("_", " ")} (%)', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Population', style={'padding': '8px', 'backgroundColor': '#f8f9fa'})
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(row[location_col], style={'padding': '8px'}),
                    html.Td(f"{row[selected_nutrient]:.1f}%", style={'padding': '8px'}),
                    html.Td(f"{row['Population']:,.0f}", style={'padding': '8px'})
                ]) for _, row in display_df.iterrows()
            ])
        ], style={'width': '100%', 'border': '1px solid #dee2e6'})
    ])
    
    # Summary statistics
    avg_deficiency = current_df[selected_nutrient].mean()
    worst_region = current_df.loc[current_df[selected_nutrient].idxmax(), location_col]
    best_region = current_df.loc[current_df[selected_nutrient].idxmin(), location_col]
    worst_value = current_df[selected_nutrient].max()
    best_value = current_df[selected_nutrient].min()
    
    # Get total population
    total_population = current_df['Population'].sum()
    
    summary = html.Div([
        html.H4("📊 Key Statistics", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Div([
            html.P([
                html.Strong("Map Level: "), 
                f"{map_level.title()}"
            ], style={'margin': '5px 0'}),
            html.P([
                html.Strong("Average deficiency: "), 
                f"{avg_deficiency:.1f}%"
            ], style={'margin': '5px 0'}),
            html.P([
                html.Strong("Highest deficiency: "), 
                f"{worst_region} ({worst_value:.1f}%)"
            ], style={'margin': '5px 0', 'color': '#e74c3c'}),
            html.P([
                html.Strong("Lowest deficiency: "), 
                f"{best_region} ({best_value:.1f}%)"
            ], style={'margin': '5px 0', 'color': '#27ae60'}),
            html.P([
                html.Strong("Total population: "), 
                f"{total_population:,.0f}"
            ], style={'margin': '5px 0'}),
            html.P([
                html.Strong(f"Number of {location_col.lower()}s: "), 
                f"{len(current_df)}"
            ], style={'margin': '5px 0'})
        ], style={
            'backgroundColor': '#f8f9fa', 
            'padding': '15px', 
            'borderRadius': '5px',
            'border': '1px solid #dee2e6'
        })
    ])
    
    return bar_fig, map_fig, data_table, summary

if __name__ == '__main__':
    print("\n🚀 Starting NutriGap Rwanda Dashboard...")
    print(f"📍 Dashboard will be available at: http://localhost:8050")
    print(f"🗺️ Province map status: {'✅ Geographic map loaded' if map_info['geographic_data_loaded'] else '⚠️ Using fallback visualization'}")
    print(f"🏘️ District map status: {'✅ District map loaded' if map_info['district_data_loaded'] else '⚠️ District data unavailable'}")
    print(f"📊 Province data: {map_info['num_provinces']} regions")
    print(f"� District data: {map_info['num_districts']} districts")
    print("�💡 Tip: Install geopandas for enhanced geographic visualization")
    print("🎛️ Features: Province-level, District-level, and Layered mapping")
    print("-" * 50)
    
    app.run_server(host='0.0.0.0', port=8050, debug=True)
