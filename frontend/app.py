### app.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# ─ Imports from your codebase ─
from rwanda_map import (
    get_rwanda_data,
    get_rwanda_district_data,
    get_rwanda_map_info,
)
from layouts.page1_overview import get_page_1_layout
from layouts.page2_trends    import get_page_2_layout
from layouts.page3_analytics import get_page_3_layout
from layouts.page4_tables    import get_page_4_layout

from callbacks.navigation import register_navigation_callbacks
from callbacks.overview   import register_overview_callbacks
from callbacks.trends     import register_trends_callbacks
from callbacks.analytics  import register_analytics_callbacks
from callbacks.tables     import register_tables_callbacks

# ------------------------------------------------------------------
# Dash initialisation (unchanged except suppress_callback_exceptions)
# ------------------------------------------------------------------
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,   # keep dynamic page loading
)
app._favicon = "favicon.ico"             # asset folder icon

# ------------------------------------------------------------------
# Map info (debug print remains the same)
# ------------------------------------------------------------------
df           = get_rwanda_data()
district_df  = get_rwanda_district_data()
map_info     = get_rwanda_map_info()

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

province_status = (
    "🗺️ Geographic Map Available"
    if map_info["geographic_data_loaded"]
    else "📊 Using Fallback Visualization"
)
district_status = (
    "🏘️ District Data Available"
    if map_info["district_data_loaded"]
    else "🏘️ District Data Unavailable"
)
map_color = "#27ae60" if map_info["geographic_data_loaded"] else "#f39c12"

# ------------------------------------------------------------------
# Navigation buttons (unchanged)
# ------------------------------------------------------------------
nav_buttons = dbc.ButtonGroup(
    [
        dbc.Button("📊 Overview Maps",     id="page-1-btn", className="nav-btn active"),
        dbc.Button("📈 Trend Analysis",    id="page-2-btn", className="nav-btn"),
        dbc.Button("🔍 Detailed Analytics",id="page-3-btn", className="nav-btn"),
        dbc.Button("📋 Data Tables",       id="page-4-btn", className="nav-btn"),
    ],
    className="nav-btn-row",                 # << centred by CSS patch
)

# ------------------------------------------------------------------
# Header + status line (H1 is now centred)
# ------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Store(id="current-page", data=1),
        html.H1(
            "NutriGap Rwanda Dashboard",
            className="text-primary my-2 header-centre",   # << centred
        ),
        html.Div(
            [
                nav_buttons,
                html.Small(
                    [
                        html.Span(province_status, style={"color": map_color, "fontWeight": "bold"}),
                        " | ",
                        html.Span(district_status, className="text-info fw-bold"),
                        f" | Provinces: {map_info['num_provinces']} | Districts: {map_info['num_districts']}",
                    ],
                    className="d-block text-center mt-2",
                ),
            ],
            className="mb-4 header-centre",                 # << centred wrapper
        ),
        html.Div(id="page-content"),                        # dynamic page container
    ]
)

# ------------------------------------------------------------------
# Callback registration (unchanged)
# ------------------------------------------------------------------
register_navigation_callbacks(
    app,
    ["page-1-btn", "page-2-btn", "page-3-btn", "page-4-btn"],
    [get_page_1_layout, get_page_2_layout, get_page_3_layout, get_page_4_layout],
    "page-content",
    "current-page",
)
register_overview_callbacks(app, df, district_df)
register_trends_callbacks(app, df)
register_analytics_callbacks(app, df)
register_tables_callbacks(app, df, district_df)

# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 Starting NutriGap Rwanda Dashboard at http://localhost:8050")
    app.run_server(host="0.0.0.0", port=8050, debug=True)
