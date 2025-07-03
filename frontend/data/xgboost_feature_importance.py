import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import train_test_split

# 1. Load cleaned dataset
df = pd.read_csv("cleaned_stunting_data.csv")

# 2. One-hot encode Province
province_encoded = pd.get_dummies(df['Province'], prefix='Prov')

# 3. Feature matrix (X) and target (y)
X = pd.concat([df[['Fe', 'Zn', 'VitA', 'Population']], province_encoded], axis=1)
y = df['Stunting']

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train XGBoost regressor
model = xgb.XGBRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Feature importance
importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)

# 7. Plot
plt.figure(figsize=(8, 5))
sns.barplot(data=importance_df, x='Importance', y='Feature', palette='viridis')
plt.title("XGBoost Feature Importances for Predicting Stunting")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.savefig("xgboost_feature_importance.png")
plt.show()

# 8. Optional: print importance
print(importance_df)



