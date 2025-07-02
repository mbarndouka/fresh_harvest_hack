"""
Callbacks for Page 2 - Trend Analysis
"""
from dash import Input, Output, html
import plotly.express as px
import plotly.graph_objects as go

def register_trends_callbacks(app, df):
    """Register callbacks for the trends analysis page"""
    
    @app.callback(
        [Output('trend-chart-1', 'figure'),
         Output('trend-chart-2', 'figure'),
         Output('trend-chart-3', 'figure'),
         Output('trend-insights', 'children')],
        [Input('trend-type-dropdown', 'value')]
    )
    def update_trend_analysis(trend_type):
        """Update trend analysis charts based on selected type"""
        
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
