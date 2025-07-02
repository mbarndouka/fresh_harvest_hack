# overview.py    (callbacks for Page 1 – Overview Maps)
"""
Callbacks for Page 1 - Overview Maps
"""
import pandas as pd
from dash import Input, Output, html
import plotly.express as px
from rwanda_map import (
    create_rwanda_map,
    create_rwanda_district_map,
    create_rwanda_layered_map,
)

# ───── Load your data once ────────────────────────────────────────────
_district_meta = pd.read_excel('./data/District_to_Province.xlsx')
_province_name_map = {
    'East': 'Eastern Province',
    'North': 'Northern Province',
    'West': 'Western Province',
    'South': 'Southern Province',
    'City of Kigali': 'City of Kigali',
}

_nutri_file = './data/Scraped_Nutrient_Adequacy.xlsx'
_cons_df  = pd.read_excel(_nutri_file, sheet_name='micro nut adeq')
_prod_df  = pd.read_excel(_nutri_file, sheet_name='production adeq')

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
    'gapscore':   'Gap Score',
}

# Health / stunting data
_nisr_df = pd.read_excel('./data/NISR_Nutrition_2020.xlsx')
# column name for <–2SD
_stunt_col = '% below -2 SD²'

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
            Input('nutrient-dropdown',  'value'),
            Input('indicator-dropdown','value'),
            Input('map-level-dropdown',  'value'),
        ]
    )
    def update_charts(nutrient, indicator, map_level):
        if nutrient == "stunting":
            colscale = [
                [0.0, "green"],
                [0.5, "white"],
                [1.0, "red"],
            ]
        else:
            colscale = [
                [0.0, "red"],
                [0.5, "white"],
                [1.0, "green"],
            ]
        # ─── pick the right raw data ──────────────────────────────
        if indicator == 'production':
            print("trying to get production data for " + nutrient)
            raw = _prod_df
            mid_col = f"Production Adequacy  ({_nutri_code[nutrient]}) mid"
        elif indicator == 'consumption':
            print("trying to get consumption data for " + nutrient)
            raw = _cons_df
            mid_col = f"{_nutri_code[nutrient]} mid"
        elif indicator == 'gapscore':
            # pull both
            cons_col = f"{_nutri_code[nutrient]} mid"
            prod_col = f"Production Adequacy  ({_nutri_code[nutrient]}) mid"
            tmp = (
                _cons_df[['District', cons_col]]
                .merge(
                    _prod_df[['District', prod_col]],
                    on='District', how='inner'
                )
                .rename(columns={cons_col: 'cons', prod_col: 'prod'})
            )
            # weights: consumption more important
            w_cons, w_prod = 0.7, 0.3
            tmp['gapscore'] = (tmp['cons'] * w_cons + tmp['prod'] * w_prod)
            raw = tmp
            mid_col = 'gapscore'

        else:  # stunting
            raw = _nisr_df
            mid_col = _stunt_col

        # ─── district‐level DataFrame ──────────────────────────────
        if indicator in ('production', 'consumption'):
            print("fetching " + indicator + " data")
            ddf = raw[['District', mid_col]].rename(columns={mid_col: nutrient})
        else:
            name = 'stunting' if indicator == 'stunting' else 'gapscore'
            ddf = raw[['District', mid_col]].rename(columns={mid_col: name})
            nutrient = name

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
            # map raw Province -> full display name
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
            # district or layered
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
