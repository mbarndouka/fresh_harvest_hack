import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import json
from shapely.geometry import shape
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# 1. Load cleaned data
df = pd.read_csv("cleaned_data.csv")

features = [
    'Total Micronutrient Adequacy low', 'Total Micronutrient Adequacy mid',
    'Total Micronutrient Adequacy high', 'Fe low', 'Fe mid', 'Fe high',
    'Zn low', 'Zn mid', 'Zn high', 'Vit. A low', 'Vit. A mid', 'Vit. A high',
    'Population'
]
target = "hfa % below -2 SD²"

# 2. Train Random Forest
X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)

# 3. Simulate +10% intervention
df_sim = df.copy()
intervention_cols = [col for col in features if any(n in col for n in ['Fe', 'Zn', 'Vit. A', 'Total Micronutrient'])]
df_sim[intervention_cols] *= 1.10
df_sim["Projected stunting (%)"] = rf_model.predict(df_sim[features])
df_sim["Change"] = df_sim["Projected stunting (%)"] - df[target]
df_sim["District"] = df_sim["District"].str.strip().str.lower()

# 4. Load GeoJSON
with open("geoBoundaries-RWA-ADM3_simplified.geojson", "r") as f:
    geojson = json.load(f)

records = []
geometries = []
for feature in geojson["features"]:
    props = feature["properties"]
    geometries.append(shape(feature["geometry"]))
    records.append(props)

gdf = pd.DataFrame(records)
gdf["geometry"] = geometries
gdf = gpd.GeoDataFrame(gdf, geometry="geometry")
gdf["shapeName"] = gdf["shapeName"].str.strip().str.lower()

# 5. Merge map with prediction
gdf_merged = gdf.merge(df_sim, left_on="shapeName", right_on="District", how="left")

# 6. Split improved vs not-improved
gdf_improved = gdf_merged[gdf_merged["Change"] < 0]
gdf_not_improved = gdf_merged[gdf_merged["Change"] >= 0]

# 7. Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
gdf_not_improved.boundary.plot(ax=ax, color="gray", linewidth=0.6)
gdf_improved.plot(column="Change", cmap="Blues", linewidth=0.8, ax=ax, edgecolor="black", legend=True)

ax.set_title("Where Nutrient Interventions (Fe+Zn+Vit A) Reduce Stunting the Most", fontsize=15, fontweight="bold")
ax.axis("off")
plt.tight_layout()
plt.savefig("stunting_improved_only_map.png", dpi=300)
plt.show()
