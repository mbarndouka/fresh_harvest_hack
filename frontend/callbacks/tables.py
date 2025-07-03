"""
Callbacks for Page 4 - Data Tables
"""
from dash import Input, Output, html

def register_tables_callbacks(app, df, district_df):
    """Register callbacks for the data tables page"""
    
    @app.callback(
        [Output('complete-data-table', 'children'),
         Output('statistical-summary', 'children'),
         Output('key-insights-table', 'children')],
        [Input('table-level-dropdown', 'value')]
    )
    def update_data_tables(table_level):
        """Update data tables based on selected level"""
        
        if table_level == 'province':
            current_df = df
            level_name = 'Province'
            location_col = 'Region'
        elif table_level == 'district':
            current_df = district_df
            level_name = 'District'
            location_col = 'District'
        else:  # comparative
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
