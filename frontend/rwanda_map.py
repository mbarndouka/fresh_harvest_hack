"""
NutriGap – Rwanda Map Utilities
────────────────────────────────────────────────────────────────────────────
Public API (unchanged):

  get_rwanda_data()                -> province-level DataFrame
  get_rwanda_district_data()       -> district-level DataFrame
  get_rwanda_map_info()            -> dict of status flags for the banner

  create_rwanda_map()              -> Mapbox choropleth (province)
  create_rwanda_district_map()     -> Mapbox choropleth (district)
  create_rwanda_layered_map()      -> district polygons + province outline
"""

from __future__ import annotations

import json
import random
import pathlib
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px

# Try to use geopandas for zipped files; fallback to plain json
try:
    import geopandas as gpd

    GEOPANDAS_AVAILABLE = True
    print("✅ Geopandas successfully imported")
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("⚠️  Geopandas not available – zip files will be ignored")

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
HERE = pathlib.Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

# accepted file patterns for ADM1 (province) and ADM2 (district)
ADM1_PATTERNS = [
    "geoBoundaries-RWA-ADM1.geojson",
    "geoBoundaries-RWA-ADM1_simplified.geojson",
    "geoBoundaries-RWA-ADM1-all.zip",
]
ADM2_PATTERNS = [
    "geoBoundaries-RWA-ADM2.geojson",
    "geoBoundaries-RWA-ADM2_simplified.geojson",
    "geoBoundaries-RWA-ADM2-all.zip",
    "geoBoundaries-RWA-ADM2-all (1).zip",  # common download duplicate
]


# ----------------------------------------------------------------------
# Helper: load whichever file variant exists
# ----------------------------------------------------------------------
def _find_geojson(patterns: List[str]) -> Tuple[dict | None, str]:
    """
    Return (geojson dict or None, feature_key).
    Auto-detect whether polygons carry 'shapeNameID', 'shapeID', or 'shapeISO'.
    """
    for pat in patterns:
        path = DATA_DIR / pat
        if not path.exists():
            continue

        try:
            if path.suffix == ".zip" and GEOPANDAS_AVAILABLE:
                gdf = gpd.read_file(f"zip://{path}")
                gj = json.loads(gdf.to_json())
            elif path.suffix == ".geojson":
                with open(path, encoding="utf-8") as f:
                    gj = json.load(f)
            else:
                continue  # skip unknown type

            # ── detect ID field on the first feature ─────────────────
            id_field = None
            for cand in ("shapeNameID", "shapeID", "shapeISO", "shapeName"):
                if cand in gj["features"][0]["properties"]:
                    id_field = cand
                    break

            if not id_field:
                print(f"⚠️  No ID-like property found in {path.name}")
                return gj, "properties.shapeName"   # fallback to label

            print(f"🗺️  Loaded {len(gj['features'])} features from {path.name} "
                  f"(id field = {id_field})")
            return gj, f"properties.{id_field}"

        except Exception as e:
            print(f"⚠️  Failed to read {path.name}: {e}")

    print("⚠️  No matching GeoJSON/zip found; falling back to scatter mode")
    return None, "properties.shapeName"


PROV_GEOJSON, PROV_KEY = _find_geojson(ADM1_PATTERNS)
DIST_GEOJSON, DIST_KEY = _find_geojson(ADM2_PATTERNS)


# ----------------------------------------------------------------------
# Dummy data (or real loader later)
# ----------------------------------------------------------------------
def _sample_dataframe(level: str) -> pd.DataFrame:
    """
    Build a DataFrame with Region / District, Vitamin_A, Iron, Zinc, Population.
    IDs must match whatever `featureidkey` we detected (shapeNameID, shapeID, …).
    """
    if level == "province" and PROV_GEOJSON:
        names = [f["properties"]["shapeName"] for f in PROV_GEOJSON["features"]]
        ids   = [f["properties"].get("shapeNameID") or
                 f["properties"].get("shapeID") or
                 f["properties"]["shapeName"]         # fallback
                 for f in PROV_GEOJSON["features"]]
    elif level == "district" and DIST_GEOJSON:
        names = [f["properties"]["shapeName"] for f in DIST_GEOJSON["features"]]
        ids   = [f["properties"].get("shapeNameID") or
                 f["properties"].get("shapeID") or
                 f["properties"]["shapeName"]
                 for f in DIST_GEOJSON["features"]]
    else:                                         # fabricate generic demo names
        if level == "province":
            names = ["City of Kigali", "Northern Province", "Eastern Province",
                     "Southern Province", "Western Province"]
            ids   = [f"RWA0{i+1}" for i in range(len(names))]
        else:
            names = [f"District {i+1}" for i in range(30)]
            ids   = [f"RWA02{i:02d}" for i in range(30)]

    # ── make sure IDs align with the feature key we auto-detected ─────────
    key_tail = PROV_KEY if level == "province" else DIST_KEY
    if key_tail.endswith("shapeName"):
        ids = names                                   # plain label expected

    # ---------------------------------------------------------------------
    random.seed(42)
    n = len(names)
    df = pd.DataFrame(
        {
            "region_id": ids,
            "display_name": names,
            "Region": names if level == "province" else [None] * n,
            "District": names if level == "district" else [None] * n,
            "Vitamin_A": [random.randint(30, 70) for _ in range(n)],
            "Iron":      [random.randint(35, 75) for _ in range(n)],
            "Zinc":      [random.randint(25, 65) for _ in range(n)],
            "Population": [random.randint(200_000, 1_500_000) for _ in range(n)],
        }
    )
    return df



# Cache sample frames so they stay consistent
_PROV_DF = _sample_dataframe("province")
_DIST_DF = _sample_dataframe("district")


# ----------------------------------------------------------------------
# Public data helpers
# ----------------------------------------------------------------------
def get_rwanda_data() -> pd.DataFrame:
    return _PROV_DF.copy()


def get_rwanda_district_data() -> pd.DataFrame:
    return _DIST_DF.copy()


def get_rwanda_map_info() -> Dict:
    return {
        "geopandas_available": GEOPANDAS_AVAILABLE,
        "geographic_data_loaded": PROV_GEOJSON is not None,
        "district_data_loaded": DIST_GEOJSON is not None,
        "num_provinces": len(_PROV_DF),
        "num_districts": len(_DIST_DF),
        "provinces": _PROV_DF["display_name"].tolist(),
        "districts": _DIST_DF["display_name"].tolist(),
        "data_source": {
            "provinces": "geojson/zip" if PROV_GEOJSON else "dummy",
            "districts": "geojson/zip" if DIST_GEOJSON else "dummy",
        },
    }


# ----------------------------------------------------------------------
# Core choropleth generator
# ----------------------------------------------------------------------
def _mapbox_choropleth(
    df: pd.DataFrame,
    geojson: dict | None,
    feature_key: str,
    nutrient_col: str,
    title: str,
    opacity: float = 0.85,
):
    if geojson is None:
        # fallback scatter point at Rwanda centroid
        fig = px.scatter_geo(
            df,
            lat=[-1.94] * len(df),
            lon=[29.9] * len(df),
            size=nutrient_col,
            color=nutrient_col,
            hover_name="display_name",
            title=f"{title} (no geometry)",
            color_continuous_scale="RdYlBu_r",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        return fig

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="region_id",
        color=nutrient_col,
        featureidkey=feature_key,
        hover_name="display_name",
        hover_data={nutrient_col: ":.1f"},
        color_continuous_scale="RdYlBu_r",
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": -1.94, "lon": 29.9},
        opacity=opacity,
    )
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", pad=dict(t=10)),
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Deficiency (%)", yanchor="middle", len=250),
    )
    
    return fig


# ----------------------------------------------------------------------
# Public builders (called by overview.py)
# ----------------------------------------------------------------------
def create_rwanda_map(df: pd.DataFrame | None, nutrient_column: str, title: str):
    df = df if df is not None else _PROV_DF
    return _mapbox_choropleth(df, PROV_GEOJSON, PROV_KEY, nutrient_column, title)


def create_rwanda_district_map(
    df: pd.DataFrame | None, nutrient_column: str, title: str
):
    df = df if df is not None else _DIST_DF
    return _mapbox_choropleth(df, DIST_GEOJSON, DIST_KEY, nutrient_column, title)


def create_rwanda_layered_map(
    province_df: pd.DataFrame | None,
    district_df: pd.DataFrame | None,
    nutrient_column: str,
    title: str,
    level: str = "district",
):
    # base layer
    district_df = district_df if district_df is not None else _DIST_DF
    fig = _mapbox_choropleth(
        district_df, DIST_GEOJSON, DIST_KEY, nutrient_column, title, 0.85
    )

    # province outline overlay
    if PROV_GEOJSON:
        outline = px.choropleth_mapbox(
            _PROV_DF,
            geojson=PROV_GEOJSON,
            locations="region_id",
            color_discrete_sequence=["rgba(0,0,0,0)"],
            featureidkey=PROV_KEY,
        ).data[0]
        outline.update(marker_line_color="black", marker_line_width=1.2, hoverinfo="skip")
        fig.add_trace(outline)

    return fig
