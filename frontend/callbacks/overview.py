"""
Callbacks for Page 1 - Overview Maps
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from dash import Input, Output, html
import plotly.express as px
from rwanda_map import (
    create_rwanda_map,
    create_rwanda_district_map,
    create_rwanda_layered_map,
)

# ───── Load your data once ────────────────────────────────────────────
_district_meta = pd.read_excel('data/District_to_Province.xlsx')
_province_name_map = {
    'East': 'Eastern Province',
    'North': 'Northern Province',
    'West': 'Western Province',
    'South': 'Southern Province',
    'City of Kigali': 'City of Kigali',
}

_nutri_file = 'data/Scraped_Nutrient_Adequacy.xlsx'
_cons_df  = pd.read_excel(_nutri_file, sheet_name='micro nut adeq')
_prod_df  = pd.read_excel(_nutri_file, sheet_name='production adeq')

# Nutrient code and labels for axes/titles
_nutri_code = {
    'Vitamin_A': 'Vit. A',
    'Iron':      'Fe',
    'Zinc':      'Zn',
}

_nutri_label = {
    'Vitamin_A': 'Vitamin A',
    'Iron':      'Iron',
    'Zinc':      'Zinc',
}

_ind_label = {
    'consumption': 'Consumption Adequacy',
    'production':  'Production Adequacy',
    'stunting':    'Stunting',
    'gapscore':    'Gap Score',
}
_ind_label['futurestunting'] = 'Future Stunting Projection'

# Health / stunting data (raw 2020 values)
_nisr_df   = pd.read_excel('data/NISR_Nutrition_2014.xlsx')
# column name for <–2SD
_stunt_col = '% < -2SD'

# ───── Train Random Forest for Gap Score (2014 data) ─────────────────────
# 2014 stunting target is called '% < -2SD'
_train_stunt = (
    pd.read_excel('data/NISR_Nutrition_2014.xlsx')
      [['District', '% < -2SD']]
      .rename(columns={'% < -2SD': 'stunting_percent'})
)

_pov_df = pd.read_excel('data/NISR_Poverty_2014.xlsx')[
    ['District', 'Poverty Incidence (%)', 'Extreme Poverty Incidence (%)']
]

_cons_feat = (
    pd.read_excel(_nutri_file, sheet_name='micro nut adeq')
      [['District', 'Fe mid', 'Zn mid', 'Vit. A mid']]
      .rename(columns={
          'Fe mid':    'Fe_cons',
          'Zn mid':    'Zn_cons',
          'Vit. A mid':'VitA_cons'
      })
)

_prod_feat = (
    pd.read_excel(_nutri_file, sheet_name='production adeq')
      [['District',
        'Production Adequacy  (Fe) mid',
        'Production Adequacy  (Zn) mid',
        'Production Adequacy  (Vit. A) mid'
      ]]
      .rename(columns={
          'Production Adequacy  (Fe) mid':    'Fe_prod',
          'Production Adequacy  (Zn) mid':    'Zn_prod',
          'Production Adequacy  (Vit. A) mid':'VitA_prod'
      })
)

# merge all training features + target
_rf_df = (
    _train_stunt
      .merge(_pov_df,      on='District', how='inner')
      .merge(_cons_feat,   on='District', how='inner')
      .merge(_prod_feat,   on='District', how='inner')
      .dropna()
)

_feature_cols = [
    'Poverty Incidence (%)', 'Extreme Poverty Incidence (%)',
    'Fe_cons', 'Zn_cons', 'VitA_cons',
    'Fe_prod','Zn_prod','VitA_prod'
]

_X = _rf_df[_feature_cols]
_y = _rf_df['stunting_percent']

_rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
_rf_model.fit(_X, _y)

# attach predicted gapscore back to the DF
_rf_df['gapscore'] = _rf_model.predict(_X)


def register_overview_callbacks(app, df, district_df):
    """Register callbacks for the overview page"""

    @app.callback(
        [
            Output('nutrient-bar-chart', 'figure'),
            Output('nutrient-map',       'figure'),
            Output('data-table',         'children'),
            Output('summary-stats',      'children'),
        ],
        [
            Input('nutrient-dropdown',   'value'),
            Input('indicator-dropdown',  'value'),
            Input('map-level-dropdown',  'value'),
        ]
    )
    def update_charts(nutrient, indicator, map_level):
        if nutrient == "stunting":
            colscale = [
                [0.0, "green"],
                [0.3, "grey"],
                [1.0, "red"],
            ]
        else:
            colscale = [
                [0.0, "red"],
                [0.3, "grey"],
                [1.0, "green"],
            ]
        # ─── pick the right raw data ──────────────────────────────
        if indicator == 'production':
            raw = _prod_df
            mid_col = f"Production Adequacy  ({_nutri_code[nutrient]}) mid"
        elif indicator == 'consumption':
            raw = _cons_df
            mid_col = f"{_nutri_code[nutrient]} mid"
        elif indicator == 'gapscore':
            # use our Random Forest predictions
            raw = _rf_df[['District', 'gapscore']]
            mid_col = 'gapscore'
            nutrient = 'gapscore'
        elif indicator == 'futurestunting':
            top3 = _rf_df.nlargest(3, 'gapscore')['District']
            boost = _rf_df[_rf_df['District'].isin(top3)][['District'] + _feature_cols].copy()

            # boost both consumption & production by 25% (cap consumes at 100)
            #boost = _rf_df[['District'] + _feature_cols].copy()
            #boost[['Fe_cons','Zn_cons','VitA_cons']] = (
            #    boost[['Fe_cons','Zn_cons','VitA_cons']] * 1.33
            #).clip(upper=100)
            #boost[['Fe_prod','Zn_prod','VitA_prod']] = (
            #    boost[['Fe_prod','Zn_prod','VitA_prod']] * 1.33
            #)
            boost[['Extreme Poverty Incidence (%)']] = (
                boost[['Extreme Poverty Incidence (%)']] * 1.33
            )
            boost[['Poverty Incidence (%)']] = (
                boost[['Poverty Incidence (%)']] * 1.33
            )
            boost['futurestunting'] = _rf_model.predict(boost[_feature_cols])
            #raw      = boost[['District','futurestunting']]
            projected = boost[['District','futurestunting']]
            inherit = _rf_df[['District','gapscore']].rename(columns={'gapscore':'futurestunting'})
            inherit = inherit[~inherit['District'].isin(top3)]
            raw = pd.concat([projected, inherit], ignore_index=True)

            mid_col  = 'futurestunting'
            nutrient = 'futurestunting'
        else:
            raw = _nisr_df
            mid_col = _stunt_col
            nutrient = 'stunting'

        # ─── construct district-level DataFrame ────────────────────
        ddf = raw[['District', mid_col]].rename(columns={mid_col: nutrient})

        # merge population + province
        ddf = ddf.merge(
            _district_meta[['District','Province','Population']],
            on='District',
            how='right',
        )

        # build district_df for map & table
        district_df_current = ddf.assign(
            region_id    = ddf['District'],
            display_name = ddf['District'],
        )

        # ─── province‐level DataFrame ─────────────────────────────
        if map_level == 'province':
            ddf['Province_full'] = ddf['Province'].map(_province_name_map)
            grp = ddf.groupby('Province_full').apply(
                lambda g: pd.Series({
                    nutrient: (g[nutrient] * g['Population']).sum() / g['Population'].sum(),
                    'Population': g['Population'].sum()
                })
            ).reset_index().rename(columns={'Province_full':'Province'})

            province_df_current = grp.assign(
                region_id    = grp['Province'],
                display_name = grp['Province'],
                Region       = grp['Province'],
            )
            current_df = province_df_current
            location_col = 'Region'
        else:
            current_df   = district_df_current
            location_col = 'District'

        # ─── bar chart ─────────────────────────────────────────────
        top_df = current_df.head(10) if map_level in ['district','layered'] else current_df
        title  = (
            f"{_ind_label[indicator]}"
            + (f" of {_nutri_label[nutrient]}" if indicator in ['production','consumption'] else "")
            + f" by {location_col}"
        )
        bar_fig = px.bar(
            top_df, x=location_col, y=nutrient,
            title=title, color=nutrient, color_continuous_scale=colscale
        )
        bar_fig.update_layout(
            showlegend=False,
            title_x=0.5,
            height=400,
            margin=dict(t=50, b=40, l=40, r=20),
            xaxis={'tickangle':45}
        )

        # ─── map ─────────────────────────────────────────────────
        map_title = title.replace(" by", " – Rwanda by")
        if map_level == 'province':
            map_fig = create_rwanda_map(province_df_current, nutrient, map_title)
        elif map_level == 'district':
            map_fig = create_rwanda_district_map(district_df_current, nutrient, map_title)
        else:
            map_fig = create_rwanda_layered_map(
                province_df_current, district_df_current,
                nutrient, map_title, level='district'
            )
        map_fig.update_layout(margin=dict(l=0,r=0,t=40,b=0), autosize=True)

        # ─── highlight top 3 gapscore districts ───────────────────
        if (indicator == 'gapscore' or indicator == 'futurestunting') and map_level == 'district':
            # get the three districts with highest gapscore
            top3_highlight = _rf_df.nlargest(3, 'gapscore')['District'].tolist()
            top3 = current_df.nlargest(3, nutrient)['District'].tolist()
            for trace in map_fig.data:
                # choropleth traces have a .locations array
                if hasattr(trace, 'locations'):
                    # build parallel lists of line colors & widths
                    line_colors = [
                        '#2b8bd2' if loc in top3_highlight else 'black'
                        for loc in trace.locations
                    ]
                    line_widths = [
                        3 if loc in top3_highlight else 0.5
                        for loc in trace.locations
                    ]
                    trace.marker.line.color = line_colors
                    trace.marker.line.width = line_widths
        # ─── data table ─────────────────────────────────────────
        disp = current_df.head(10) if map_level in ['district','layered'] else current_df
        rows = []
        for _, row in disp.iterrows():
            rows.append(
                html.Tr([
                    html.Td(row[location_col], style={'padding':'8px'}),
                    html.Td(f"{row[nutrient]:.1f}%", style={'padding':'8px'}),
                    html.Td(f"{row['Population']:,}", style={'padding':'8px'}),
                ])
            )
        data_table = html.Div([
            html.H4(f"📊 {location_col} Data ({'Top 10' if map_level in ['district','layered'] else 'All'})"),
            html.Table(
                [html.Thead(html.Tr([
                    html.Th(location_col), html.Th(f"{_ind_label[indicator]}"), html.Th("Population")
                ]))] +
                [html.Tbody(rows)],
                style={'width':'100%', 'border':'1px solid #dee2e6'}
            )
        ])

        # ─── summary stats ────────────────────────────────────────
        avg_val = current_df[nutrient].mean()
        worst   = current_df.loc[current_df[nutrient].idxmax(), location_col]
        best    = current_df.loc[current_df[nutrient].idxmin(), location_col]
        wval    = current_df[nutrient].max()
        bval    = current_df[nutrient].min()
        popsum  = current_df['Population'].sum()

        summary = html.Div([
            html.H4("Key stats"),
            html.P([html.Strong("Indicator:"), f" {_ind_label[indicator]}"]),
            html.P([html.Strong("Map level:"), f" {map_level.title()}"]),
            html.P([html.Strong("Average:"), f" {avg_val:.1f}%"]),
            html.P([html.Strong("Highest:"), f" {worst} ({wval:.1f}%)"], style={'color':'#e74c3c'}),
            html.P([html.Strong("Lowest:"), f" {best} ({bval:.1f}%)"], style={'color':'#27ae60'}),
            html.P([html.Strong("Total population:"), f" {popsum:,}"]),
            html.P([html.Strong(f"Number of {location_col.lower()}s:"), f" {len(current_df)}"]),
        ], style={
            'backgroundColor':'#f8f9fa',
            'padding':'15px',
            'borderRadius':'5px',
            'border':'1px solid #dee2e6'
        })

        return bar_fig, map_fig, data_table, summary
