import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor

# Load cleaned dataset
df = pd.read_csv("cleaned_stunting_data.csv")

# Features and target
features = ['Fe', 'Zn', 'VitA', 'Population', 'Prov_North', 'Prov_South', 'Prov_East', 'Prov_West', 'Prov_City of Kigali']
target = 'Stunting'

X = df[features]
y = df[target]

# Train XGBoost
model = XGBRegressor(random_state=42)
model.fit(X, y)

# Make copies of data with +10% nutrient increase
def make_adjusted_df(nutrient):
    X_adj = X.copy()
    if nutrient == 'All':
        for n in ['Fe', 'Zn', 'VitA']:
            X_adj[n] *= 1.10
    else:
        X_adj[nutrient] *= 1.10
    return X_adj

interventions = ['Fe', 'Zn', 'VitA', 'All']
results = {}

for nut in interventions:
    X_adj = make_adjusted_df(nut)
    y_pred = model.predict(X_adj)
    reduction = y.values - y_pred
    results[nut + '+10%'] = reduction * 100  # convert to %

reduction_df = pd.DataFrame(results)
reduction_df['District'] = df['District']
reduction_df.set_index('District', inplace=True)

# === 1. 평균 막대그래프 저장 ===
mean_reductions = reduction_df.mean().sort_values(ascending=False)

plt.figure(figsize=(7,5))
sns.barplot(x=mean_reductions.index, y=mean_reductions.values, palette='pastel')
plt.ylabel('Avg Reduction (%)')
plt.xlabel('Intervention')
plt.title('XGBoost: Average Stunting Reduction (%): 10% Nutrient Increase')
plt.tight_layout()
plt.savefig("xgb_avg_reduction_10pct.png")
plt.close()

# === 2. 히트맵 저장 ===
plt.figure(figsize=(14,8))
sns.heatmap(reduction_df, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5)
plt.title("XGBoost: Stunting Reduction by District (10% Micronutrient Increase)")
plt.xlabel("Intervention")
plt.ylabel("District")
plt.tight_layout()
plt.savefig("xgb_heatmap_reduction_10pct.png")
plt.close()
