import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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

# Callback for page navigation
@app.callback(
    Output('current-page', 'data'),
    [Input('page-1-btn', 'n_clicks'),
     Input('page-2-btn', 'n_clicks'),
     Input('page-3-btn', 'n_clicks'),
     Input('page-4-btn', 'n_clicks')],
    prevent_initial_call=True
)
def update_page(btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 1
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'page-1-btn':
        return 1
    elif button_id == 'page-2-btn':
        return 2
    elif button_id == 'page-3-btn':
        return 3
    elif button_id == 'page-4-btn':
        return 4
    return 1

# Callback for updating page content
@app.callback(
    Output('page-content', 'children'),
    [Input('current-page', 'data')]
)
def display_page(page):
    if page == 1:
        return get_page_1_layout()
    elif page == 2:
        return get_page_2_layout()
    elif page == 3:
        return get_page_3_layout()
    elif page == 4:
        return get_page_4_layout()
    return get_page_1_layout()

# Update navigation button styles
@app.callback(
    [Output('page-1-btn', 'style'),
     Output('page-2-btn', 'style'),
     Output('page-3-btn', 'style'),
     Output('page-4-btn', 'style')],
    [Input('current-page', 'data')]
)
def update_nav_styles(current_page):
    active_style = {'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
                   'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'}
    inactive_style = {'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none', 
                     'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'}
    
    styles = [inactive_style, inactive_style, inactive_style, inactive_style]
    styles[current_page - 1] = active_style
    
    return styles

# Page 1 Layout - Overview Maps
def get_page_1_layout():
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

# Page 2 Layout - Trend Analysis
def get_page_2_layout():
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

# Page 3 Layout - Detailed Analytics
def get_page_3_layout():
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

# Page 4 Layout - Data Tables
def get_page_4_layout():
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

# Page 2 Callbacks - Trend Analysis
@app.callback(
    [Output('trend-chart-1', 'figure'),
     Output('trend-chart-2', 'figure'),
     Output('trend-chart-3', 'figure'),
     Output('trend-insights', 'children')],
    [Input('trend-type-dropdown', 'value')]
)
def update_trend_analysis(trend_type):
    if trend_type == 'comparison':
        # Multi-nutrient comparison chart
        fig1 = px.bar(
            df, 
            x='Region', 
            y=['Vitamin_A', 'Iron', 'Zinc'],
            title='Nutrient Deficiency Comparison by Region',
            barmode='group',
            color_discrete_map={'Vitamin_A': '#e74c3c', 'Iron': '#f39c12', 'Zinc': '#3498db'}
        )
        fig1.update_layout(height=400, title_x=0.5)
        
        # Radar chart for nutrients
        categories = df['Region'].tolist()
        fig2 = go.Figure()
        
        for nutrient in ['Vitamin_A', 'Iron', 'Zinc']:
            fig2.add_trace(go.Scatterpolar(
                r=df[nutrient],
                theta=categories,
                fill='toself',
                name=nutrient.replace('_', ' ')
            ))
        
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(df[['Vitamin_A', 'Iron', 'Zinc']].max())])),
            title="Nutrient Deficiency Radar Chart",
            title_x=0.5,
            height=400
        )
        
        # Correlation heatmap
        corr_data = df[['Vitamin_A', 'Iron', 'Zinc', 'Population']].corr()
        fig3 = px.imshow(
            corr_data,
            title="Correlation Matrix: Nutrients and Population",
            color_continuous_scale='RdBu_r'
        )
        fig3.update_layout(height=400, title_x=0.5)
        
        insights = html.Div([
            html.H4("🔍 Trend Insights", style={'color': '#2c3e50'}),
            html.P("• Multi-nutrient deficiency patterns show regional variations"),
            html.P("• Strong correlation observed between different nutrient deficiencies"),
            html.P("• Population size may influence deficiency prevalence")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
        
    elif trend_type == 'population':
        # Population vs deficiency scatter plots
        fig1 = px.scatter(
            df, x='Population', y='Vitamin_A', size='Iron',
            title='Vitamin A Deficiency vs Population (Iron deficiency as size)',
            hover_name='Region'
        )
        fig1.update_layout(height=400, title_x=0.5)
        
        fig2 = px.scatter(
            df, x='Population', y='Iron', size='Zinc',
            title='Iron Deficiency vs Population (Zinc deficiency as size)',
            hover_name='Region'
        )
        fig2.update_layout(height=400, title_x=0.5)
        
        # Bubble chart
        fig3 = px.scatter(
            df, x='Vitamin_A', y='Iron', size='Population', color='Zinc',
            title='Multi-dimensional Analysis: All Nutrients and Population',
            hover_name='Region'
        )
        fig3.update_layout(height=400, title_x=0.5)
        
        insights = html.Div([
            html.H4("🔍 Population Analysis Insights", style={'color': '#2c3e50'}),
            html.P("• Population density correlates with certain deficiency patterns"),
            html.P("• Larger populations may have different nutritional challenges"),
            html.P("• Multi-dimensional view reveals complex relationships")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
        
    else:  # ranking
        # Ranking charts
        df_sorted = df.sort_values('Vitamin_A', ascending=False)
        fig1 = px.bar(
            df_sorted, x='Region', y='Vitamin_A',
            title='Vitamin A Deficiency Ranking (Highest to Lowest)',
            color='Vitamin_A',
            color_continuous_scale='Reds'
        )
        fig1.update_layout(height=400, title_x=0.5, xaxis={'tickangle': 45})
        
        df_sorted_iron = df.sort_values('Iron', ascending=False)
        fig2 = px.bar(
            df_sorted_iron, x='Region', y='Iron',
            title='Iron Deficiency Ranking (Highest to Lowest)',
            color='Iron',
            color_continuous_scale='Oranges'
        )
        fig2.update_layout(height=400, title_x=0.5, xaxis={'tickangle': 45})
        
        # Combined ranking
        df_avg = df.copy()
        df_avg['Average_Deficiency'] = (df_avg['Vitamin_A'] + df_avg['Iron'] + df_avg['Zinc']) / 3
        df_avg_sorted = df_avg.sort_values('Average_Deficiency', ascending=False)
        
        fig3 = px.bar(
            df_avg_sorted, x='Region', y='Average_Deficiency',
            title='Overall Nutritional Risk Ranking',
            color='Average_Deficiency',
            color_continuous_scale='Blues'
        )
        fig3.update_layout(height=400, title_x=0.5, xaxis={'tickangle': 45})
        
        insights = html.Div([
            html.H4("🔍 Ranking Insights", style={'color': '#2c3e50'}),
            html.P(f"• Highest overall risk: {df_avg_sorted.iloc[0]['Region']}"),
            html.P(f"• Lowest overall risk: {df_avg_sorted.iloc[-1]['Region']}"),
            html.P("• Rankings vary by individual nutrients vs overall risk")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
    
    return fig1, fig2, fig3, insights

# Page 3 Callbacks - Detailed Analytics
@app.callback(
    [Output('analytics-chart-1', 'figure'),
     Output('analytics-chart-2', 'figure'),
     Output('analytics-chart-3', 'figure'),
     Output('analytics-insights', 'children')],
    [Input('analytics-focus-dropdown', 'value')]
)
def update_detailed_analytics(focus):
    if focus == 'high_risk':
        # Identify high-risk regions
        threshold = 50  # 50% deficiency threshold
        high_risk_regions = df[
            (df['Vitamin_A'] > threshold) | 
            (df['Iron'] > threshold) | 
            (df['Zinc'] > threshold)
        ]
        
        fig1 = px.bar(
            high_risk_regions, x='Region', y=['Vitamin_A', 'Iron', 'Zinc'],
            title='High-Risk Regions (>50% Deficiency)',
            barmode='group'
        )
        fig1.update_layout(height=400, title_x=0.5)
        
        # Risk score calculation
        df_risk = df.copy()
        df_risk['Risk_Score'] = (df_risk['Vitamin_A'] + df_risk['Iron'] + df_risk['Zinc']) / 3
        
        fig2 = px.pie(
            df_risk, values='Population', names='Region',
            title='Population Distribution by Region',
            color='Risk_Score',
            color_continuous_scale='Reds'
        )
        fig2.update_layout(height=400, title_x=0.5)
        
        # Risk vs Population
        fig3 = px.scatter(
            df_risk, x='Population', y='Risk_Score',
            title='Risk Score vs Population Size',
            hover_name='Region',
            size='Risk_Score'
        )
        fig3.update_layout(height=400, title_x=0.5)
        
        insights = html.Div([
            html.H4("🚨 High-Risk Analysis", style={'color': '#e74c3c'}),
            html.P(f"• {len(high_risk_regions)} regions identified as high-risk"),
            html.P(f"• Highest risk score: {df_risk['Risk_Score'].max():.1f}%"),
            html.P("• Population size shows correlation with risk levels")
        ], style={'backgroundColor': '#fdf2f2', 'padding': '15px', 'borderRadius': '5px'})
        
    elif focus == 'density':
        # Population density analysis
        df_density = df.copy()
        df_density['Density_Category'] = pd.cut(
            df_density['Population'], 
            bins=3, 
            labels=['Low', 'Medium', 'High']
        )
        
        fig1 = px.box(
            df_density, x='Density_Category', y='Vitamin_A',
            title='Vitamin A Deficiency by Population Density'
        )
        fig1.update_layout(height=400, title_x=0.5)
        
        fig2 = px.violin(
            df_density, x='Density_Category', y='Iron',
            title='Iron Deficiency Distribution by Population Density'
        )
        fig2.update_layout(height=400, title_x=0.5)
        
        # Average by density category
        density_avg = df_density.groupby('Density_Category')[['Vitamin_A', 'Iron', 'Zinc']].mean().reset_index()
        fig3 = px.bar(
            density_avg, x='Density_Category', y=['Vitamin_A', 'Iron', 'Zinc'],
            title='Average Deficiency by Population Density Category',
            barmode='group'
        )
        fig3.update_layout(height=400, title_x=0.5)
        
        insights = html.Div([
            html.H4("📊 Population Density Insights", style={'color': '#2c3e50'}),
            html.P("• Population density affects nutritional outcomes"),
            html.P("• Distribution patterns vary by nutrient type"),
            html.P("• Medium density areas show unique characteristics")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
        
    else:  # multi_nutrient
        # Multi-nutrient deficiency analysis
        df_multi = df.copy()
        df_multi['Multiple_Deficiency'] = (
            (df_multi['Vitamin_A'] > 40) & 
            (df_multi['Iron'] > 40) & 
            (df_multi['Zinc'] > 40)
        ).astype(int)
        
        fig1 = px.scatter_3d(
            df_multi, x='Vitamin_A', y='Iron', z='Zinc',
            title='3D Nutrient Deficiency Visualization',
            hover_name='Region',
            color='Population'
        )
        fig1.update_layout(height=500, title_x=0.5)
        
        # Parallel coordinates
        fig2 = px.parallel_coordinates(
            df_multi, dimensions=['Vitamin_A', 'Iron', 'Zinc', 'Population'],
            title='Parallel Coordinates: Multi-Nutrient Analysis'
        )
        fig2.update_layout(height=400, title_x=0.5)
        
        # Deficiency combinations
        combinations = []
        for _, row in df_multi.iterrows():
            combo = []
            if row['Vitamin_A'] > 40: combo.append('Vitamin A')
            if row['Iron'] > 40: combo.append('Iron')
            if row['Zinc'] > 40: combo.append('Zinc')
            combinations.append(', '.join(combo) if combo else 'None')
        
        df_multi['Deficiency_Combination'] = combinations
        combo_counts = df_multi['Deficiency_Combination'].value_counts()
        
        fig3 = px.pie(
            values=combo_counts.values, names=combo_counts.index,
            title='Distribution of Deficiency Combinations'
        )
        fig3.update_layout(height=400, title_x=0.5)
        
        insights = html.Div([
            html.H4("🔬 Multi-Nutrient Analysis", style={'color': '#2c3e50'}),
            html.P(f"• {df_multi['Multiple_Deficiency'].sum()} regions have multiple deficiencies"),
            html.P("• 3D visualization reveals clustering patterns"),
            html.P("• Combination analysis shows intervention priorities")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
    
    return fig1, fig2, fig3, insights

# Page 4 Callbacks - Data Tables
@app.callback(
    [Output('complete-data-table', 'children'),
     Output('statistical-summary', 'children'),
     Output('key-insights-table', 'children')],
    [Input('table-level-dropdown', 'value')]
)
def update_data_tables(table_level):
    if table_level == 'province':
        current_df = df
        level_name = 'Province'
        location_col = 'Region'
    elif table_level == 'district':
        current_df = district_df
        level_name = 'District'
        location_col = 'District'
    else:  # comparative
        # Combine both datasets for comparison
        current_df = df
        level_name = 'Comparative'
        location_col = 'Region'
    
    # Complete data table
    complete_table = html.Table([
        html.Thead([
            html.Tr([
                html.Th(location_col, style={'padding': '12px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th('Vitamin A (%)', style={'padding': '12px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th('Iron (%)', style={'padding': '12px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th('Zinc (%)', style={'padding': '12px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th('Population', style={'padding': '12px', 'backgroundColor': '#3498db', 'color': 'white'})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(row[location_col], style={'padding': '10px', 'borderBottom': '1px solid #ddd'}),
                html.Td(f"{row['Vitamin_A']:.1f}%", style={'padding': '10px', 'borderBottom': '1px solid #ddd'}),
                html.Td(f"{row['Iron']:.1f}%", style={'padding': '10px', 'borderBottom': '1px solid #ddd'}),
                html.Td(f"{row['Zinc']:.1f}%", style={'padding': '10px', 'borderBottom': '1px solid #ddd'}),
                html.Td(f"{row['Population']:,.0f}", style={'padding': '10px', 'borderBottom': '1px solid #ddd'})
            ]) for _, row in current_df.iterrows()
        ])
    ], style={'width': '100%', 'border': '1px solid #ddd', 'borderCollapse': 'collapse'})
    
    # Statistical summary
    stats_summary = html.Div([
        html.H4(f"📈 {level_name} Statistics", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th('Nutrient', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Mean', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Median', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Min', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Max', style={'padding': '8px', 'backgroundColor': '#f8f9fa'}),
                    html.Th('Std Dev', style={'padding': '8px', 'backgroundColor': '#f8f9fa'})
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td('Vitamin A', style={'padding': '8px'}),
                    html.Td(f"{current_df['Vitamin_A'].mean():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Vitamin_A'].median():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Vitamin_A'].min():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Vitamin_A'].max():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Vitamin_A'].std():.1f}%", style={'padding': '8px'})
                ]),
                html.Tr([
                    html.Td('Iron', style={'padding': '8px'}),
                    html.Td(f"{current_df['Iron'].mean():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Iron'].median():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Iron'].min():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Iron'].max():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Iron'].std():.1f}%", style={'padding': '8px'})
                ]),
                html.Tr([
                    html.Td('Zinc', style={'padding': '8px'}),
                    html.Td(f"{current_df['Zinc'].mean():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Zinc'].median():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Zinc'].min():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Zinc'].max():.1f}%", style={'padding': '8px'}),
                    html.Td(f"{current_df['Zinc'].std():.1f}%", style={'padding': '8px'})
                ])
            ])
        ], style={'width': '100%', 'border': '1px solid #dee2e6'})
    ])
    
    # Key insights
    worst_region = current_df.loc[current_df['Vitamin_A'].idxmax(), location_col]
    best_region = current_df.loc[current_df['Vitamin_A'].idxmin(), location_col]
    highest_pop = current_df.loc[current_df['Population'].idxmax(), location_col]
    
    key_insights = html.Div([
        html.H4("🎯 Key Insights", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Div([
            html.P([html.Strong("Most Critical Region: "), f"{worst_region} (Vitamin A: {current_df['Vitamin_A'].max():.1f}%)"]),
            html.P([html.Strong("Best Performing Region: "), f"{best_region} (Vitamin A: {current_df['Vitamin_A'].min():.1f}%)"]),
            html.P([html.Strong("Largest Population: "), f"{highest_pop} ({current_df['Population'].max():,.0f} people)"]),
            html.P([html.Strong("Total Population Covered: "), f"{current_df['Population'].sum():,.0f} people"]),
            html.P([html.Strong("Average Overall Deficiency: "), f"{current_df[['Vitamin_A', 'Iron', 'Zinc']].mean().mean():.1f}%"])
        ], style={'backgroundColor': '#e8f6f3', 'padding': '15px', 'borderRadius': '5px'})
    ])
    
    return complete_table, stats_summary, key_insights

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
