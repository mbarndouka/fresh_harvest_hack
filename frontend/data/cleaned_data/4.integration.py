import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# 데이터 불러오기
df = pd.read_csv("cleaned_data.csv")

# 특성과 타겟 정의
features = [
    'Total Micronutrient Adequacy low', 'Total Micronutrient Adequacy mid',
    'Total Micronutrient Adequacy high', 'Fe low', 'Fe mid', 'Fe high',
    'Zn low', 'Zn mid', 'Zn high', 'Vit. A low', 'Vit. A mid', 'Vit. A high',
    'Population'
]
target = "hfa % below -2 SD²"

# 모델 훈련
X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)

# 데이터 복사 및 시뮬레이션
df_fe, df_zn, df_va, df_all = [df.copy() for _ in range(4)]

fe_cols = [col for col in features if 'Fe' in col]
zn_cols = [col for col in features if 'Zn' in col]
va_cols = [col for col in features if 'Vit. A' in col]
all_cols = [col for col in features if any(n in col for n in ['Fe', 'Zn', 'Vit. A', 'Total Micronutrient'])]

df_fe[fe_cols] *= 1.10
df_zn[zn_cols] *= 1.10
df_va[va_cols] *= 1.10
df_all[all_cols] *= 1.10

# 예측 및 변화 계산
for df_var in [df_fe, df_zn, df_va, df_all]:
    df_var["Projected stunting (%)"] = rf_model.predict(df_var[features])
    df_var["Change"] = df_var["Projected stunting (%)"] - df_var["hfa % below -2 SD²"]

# 📊 시각화
fig, axes = plt.subplots(2, 2, figsize=(20, 16))
scenarios = [
    ("+10% Fe", df_fe),
    ("+10% Zn", df_zn),
    ("+10% Vit A", df_va),
    ("+10% Fe+Zn+Vit A", df_all)
]

for ax, (title, df_plot) in zip(axes.flat, scenarios):
    sorted_df = df_plot.sort_values("Change")
    colors = ['blue' if val < 0 else 'red' for val in sorted_df["Change"]]

    y_pos = range(len(sorted_df))
    ax.barh(y_pos, sorted_df["Change"], color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df["District"], fontsize=11)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axvline(0, color='gray', linestyle='--')
    ax.tick_params(axis='y', pad=6)

    # ❌ x/y 라벨 제거
    ax.set_xlabel("")
    ax.set_ylabel("")

# ✅ 공통 축 설명을 아래 텍스트로 삽입 (legend 느낌)
fig.text(0.5, 0.04, "Change in Stunting Rate (%)", ha='center', fontsize=14, fontweight='bold')
fig.text(0.04, 0.5, "Districts", va='center', rotation='vertical', fontsize=14, fontweight='bold')

# 범례도 유지
import matplotlib.patches as mpatches
red_patch = mpatches.Patch(color='red', label='Stunting ↑ (Worse)')
blue_patch = mpatches.Patch(color='blue', label='Stunting ↓ (Improved)')
fig.legend(handles=[red_patch, blue_patch], loc='lower center', ncol=2, fontsize=12)

plt.suptitle("Where Can Nutrient Interventions Reduce Stunting the Most?", fontsize=20, fontweight='bold')
plt.tight_layout(rect=[0.06, 0.06, 1, 0.95])
plt.savefig("stunting_clean_no_axes_with_legendlabels.png", dpi=300)
plt.show()
