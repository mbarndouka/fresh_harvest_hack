from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np

# ✅ 데이터 불러오기 (cleaned_data.csv가 같은 디렉토리에 있어야 함)
df = pd.read_csv("cleaned_data.csv")

# ✅ 타겟 및 피처 지정
target_col = "hfa % below -2 SD²"
features = [
    "Fe mid", "Zn mid", "Vit. A mid",
    "Total Micronutrient Adequacy mid", "Population"
]

X = df[features]
y = df[target_col]

# ✅ 모델 학습
rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X, y)

# ✅ 예측
y_pred = rf_model.predict(X)

# ✅ 평가지표 계산
rmse = np.sqrt(mean_squared_error(y, y_pred))
r2 = r2_score(y, y_pred)

# ✅ 결과 출력
print(f"✅ RMSE (Root Mean Squared Error): {rmse:.2f}")
print(f"✅ R² (R-squared): {r2:.2f}")

