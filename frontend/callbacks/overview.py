"""
Callbacks for Page 1 - Overview Maps
"""
from dash import Input, Output, html
import plotly.express as px
from rwanda_map import create_rwanda_map, create_rwanda_district_map, create_rwanda_layered_map

def register_overview_callbacks(app, df, district_df):
    """Register callbacks for the overview page"""
    
    @app.callback(
        [Output('nutrient-bar-chart', 'figure'),
         Output('nutrient-map', 'figure'),
         Output('data-table', 'children'),
         Output('summary-stats', 'children')],
        [Input('nutrient-dropdown', 'value'),
         Input('map-level-dropdown', 'value')]
    )
    def update_charts(selected_nutrient, map_level):
        """Update charts based on selected nutrient and map level"""
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
        
        map_fig.update_layout(height=600)   # <- add this line

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
        total_population = current_df['Population'].sum()
        
        summary = html.Div([
            html.H4("📊 Key Statistics", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            html.Div([
                html.P([html.Strong("Map Level: "), f"{map_level.title()}"], style={'margin': '5px 0'}),
                html.P([html.Strong("Average deficiency: "), f"{avg_deficiency:.1f}%"], style={'margin': '5px 0'}),
                html.P([html.Strong("Highest deficiency: "), f"{worst_region} ({worst_value:.1f}%)"], 
                       style={'margin': '5px 0', 'color': '#e74c3c'}),
                html.P([html.Strong("Lowest deficiency: "), f"{best_region} ({best_value:.1f}%)"], 
                       style={'margin': '5px 0', 'color': '#27ae60'}),
                html.P([html.Strong("Total population: "), f"{total_population:,.0f}"], style={'margin': '5px 0'}),
                html.P([html.Strong(f"Number of {location_col.lower()}s: "), f"{len(current_df)}"], style={'margin': '5px 0'})
            ], style={
                'backgroundColor': '#f8f9fa', 
                'padding': '15px', 
                'borderRadius': '5px',
                'border': '1px solid #dee2e6'
            })
        ])
        
        return bar_fig, map_fig, data_table, summary
