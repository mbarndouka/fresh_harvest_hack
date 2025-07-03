import pandas as pd

# --- 파일 경로 설정 (필요 시 수정) ---
nutrient_path = "Scraped_Nutrient_Adequacy.xlsx"
stunting_path = "NISR_Nutrition_2020.xlsx"
district_path = "District_to_Province.xlsx"

# --- 1. 데이터 불러오기 ---
nutrient_df = pd.read_excel(nutrient_path)
stunting_df = pd.read_excel(stunting_path)
district_df = pd.read_excel(district_path)

# --- 2. 필요한 열만 선택 ---
nutrient_df = nutrient_df[['District', 'Fe mid', 'Zn mid', 'Vit. A mid']]
stunting_df = stunting_df[['District', '% below -2 SD²']]
district_df = district_df[['District', 'Province', 'Population']]

# --- 3. 컬럼명 정리 ---
nutrient_df.columns = ['District', 'Fe', 'Zn', 'VitA']
stunting_df.columns = ['District', 'Stunting']

# --- 4. 병합 ---
merged_df = pd.merge(nutrient_df, stunting_df, on='District')
merged_df = pd.merge(merged_df, district_df, on='District')

# --- 5. 결측치 제거 ---
merged_df.dropna(inplace=True)

# --- 6. 값 범위 검토 ---
for col in ['Fe', 'Zn', 'VitA', 'Stunting']:
    outliers = merged_df[(merged_df[col] < 0) | (merged_df[col] > 100)]
    if not outliers.empty:
        print(f"⚠️ {col} 열에 0~100 범위를 벗어난 값이 존재합니다:")
        print(outliers[['District', col]])

# --- 7. 결과 저장 ---
merged_df.to_csv("cleaned_stunting_data.csv", index=False)
print("✅ 완료: cleaned_stunting_data.csv 파일로 저장되었습니다.")
