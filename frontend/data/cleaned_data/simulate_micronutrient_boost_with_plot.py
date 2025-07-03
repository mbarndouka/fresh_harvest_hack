import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# 1. Load data
df = pd.read_csv("cleaned_stunting_data.csv")

# 2. Prepare features (Fe, Zn, VitA, Population + Province one-hot)
X_base = pd.concat([
    df[['Fe', 'Zn', 'VitA', 'Population']],
    pd.get_dummies(df['Province'], prefix='Prov')
], axis=1)
y = df['Stunting']

# 3. Train model
X_train, X_test, y_train, y_test = train_test_split(X_base, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. Predict baseline
baseline = model.predict(X_base)

# 5. Simulate scenarios
results = pd.DataFrame({'District': df['District'], 'Province': df['Province']})

for nutrient in ['Fe', 'Zn', 'VitA']:
    for pct in [5, 10]:
        X_sim = X_base.copy()
        X_sim[nutrient] *= (1 + pct / 100)
        X_sim[nutrient] = X_sim[nutrient].clip(upper=100)
        pred = model.predict(X_sim)
        results[f"{nutrient}+{pct}%"] = (baseline - pred).round(3)

# 6. Combined interventions (all nutrients boosted)
for pct in [5, 10]:
    X_combined = X_base.copy()
    for nutrient in ['Fe', 'Zn', 'VitA']:
        X_combined[nutrient] *= (1 + pct / 100)
        X_combined[nutrient] = X_combined[nutrient].clip(upper=100)
    pred_combined = model.predict(X_combined)
    results[f"All+{pct}%"] = (baseline - pred_combined).round(3)

# 7. Save results
results.to_csv("stunting_intervention_simulation.csv", index=False)
print("✅ Saved to stunting_intervention_simulation.csv")
