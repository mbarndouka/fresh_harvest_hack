import dash
from dash import dcc, html

# Import our custom Rwanda map module
from rwanda_map import get_rwanda_data, get_rwanda_district_data, get_rwanda_map_info

# Import modular layouts
from layouts.page1_overview import get_page_1_layout
from layouts.page2_trends import get_page_2_layout
from layouts.page3_analytics import get_page_3_layout
from layouts.page4_tables import get_page_4_layout

# Import callback registration functions
from callbacks.navigation import register_navigation_callbacks
from callbacks.overview import register_overview_callbacks
from callbacks.trends import register_trends_callbacks
from callbacks.analytics import register_analytics_callbacks
from callbacks.tables import register_tables_callbacks

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

# Create map status message
province_status = "🗺️ Geographic Map Available" if map_info['geographic_data_loaded'] else "📊 Using Fallback Visualization"
district_status = "🏘️ District Data Available" if map_info['district_data_loaded'] else "🏘️ District Data Unavailable"
map_color = "#27ae60" if map_info['geographic_data_loaded'] else "#f39c12"

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the main layout
app.layout = html.Div([
    # Store component to track current page
    dcc.Store(id='current-page', data=1),
    
    html.H1("NutriGap Rwanda Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Navigation and status bar
    html.Div([
        # Page navigation buttons
        html.Div([
            html.Button("📊 Overview Maps", id="page-1-btn", className="nav-button", 
                       style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
                             'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'}),
            html.Button("📈 Trend Analysis", id="page-2-btn", className="nav-button",
                       style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none', 
                             'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'}),
            html.Button("🔍 Detailed Analytics", id="page-3-btn", className="nav-button",
                       style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none', 
                             'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'}),
            html.Button("📋 Data Tables", id="page-4-btn", className="nav-button",
                       style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none', 
                             'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'})
        ], style={'textAlign': 'center', 'margin': '20px 0'}),
        
        # Status indicator
        html.Div([
            html.P([
                html.Span(province_status, style={'color': map_color, 'fontWeight': 'bold'}),
                " | ",
                html.Span(district_status, style={'color': '#3498db', 'fontWeight': 'bold'}),
                f" | Provinces: {map_info['num_provinces']} | Districts: {map_info['num_districts']}"
            ], style={'textAlign': 'center', 'margin': '10px 0', 'fontSize': '14px'})
        ]),
    ]),
    
    # Page content container
    html.Div(id='page-content')
])

# Register all callbacks
register_navigation_callbacks(app, get_page_1_layout, get_page_2_layout, get_page_3_layout, get_page_4_layout)
register_overview_callbacks(app, df, district_df)
register_trends_callbacks(app, df)
register_analytics_callbacks(app, df)
register_tables_callbacks(app, df, district_df)

if __name__ == '__main__':
    print("\n🚀 Starting NutriGap Rwanda Dashboard...")
    print(f"📍 Dashboard will be available at: http://localhost:8050")
    print(f"🗺️ Province map status: {'✅ Geographic map loaded' if map_info['geographic_data_loaded'] else '⚠️ Using fallback visualization'}")
    print(f"🏘️ District map status: {'✅ District map loaded' if map_info['district_data_loaded'] else '⚠️ District data unavailable'}")
    print(f"📊 Province data: {map_info['num_provinces']} regions")
    print(f"📊 District data: {map_info['num_districts']} districts")
    print("💡 Tip: Install geopandas for enhanced geographic visualization")
    print("🎛️ Features: Province-level, District-level, and Layered mapping")
    print("-" * 50)
    
    app.run_server(host='0.0.0.0', port=8050, debug=True)
