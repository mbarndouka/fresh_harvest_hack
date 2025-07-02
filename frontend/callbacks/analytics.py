"""
Callbacks for Page 3 - Detailed Analytics
"""
from dash import Input, Output, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def register_analytics_callbacks(app, df):
    """Register callbacks for the detailed analytics page"""
    
    @app.callback(
        [Output('analytics-chart-1', 'figure'),
         Output('analytics-chart-2', 'figure'),
         Output('analytics-chart-3', 'figure'),
         Output('analytics-insights', 'children')],
        [Input('analytics-focus-dropdown', 'value')]
    )
    def update_detailed_analytics(focus):
        """Update detailed analytics charts based on selected focus"""
        
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
