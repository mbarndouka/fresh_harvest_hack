import pandas as pd

# Load each Excel file
df_province = pd.read_excel("District_to_Province.xlsx")
df_nutrition = pd.read_excel("NISR_Nutrition_2020.xlsx")
df_nutrient = pd.read_excel("Scraped_Nutrient_Adequacy.xlsx")

# Keep only useful columns
df_province = df_province[["District", "Province", "Population"]]

# Merge by 'District'
merged = df_nutrition.merge(df_nutrient, on="District", how="left")
merged = merged.merge(df_province, on="District", how="left")

# Drop rows with missing values
cleaned_df = merged.dropna()

# Save to CSV (optional)
cleaned_df.to_csv("cleaned_data.csv", index=False)
