import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv("stunting_intervention_simulation.csv")

# Keep only +10% columns
cols_to_keep = ['District', 'Province', 'Fe+10%', 'Zn+10%', 'VitA+10%', 'All+10%']
df_10 = df[cols_to_keep]

# -------------------
# 1. Grouped bar plot
# -------------------
avg_10 = df_10.drop(columns=['District', 'Province']).mean().reset_index()
avg_10.columns = ['Intervention', 'AvgReduction']

plt.figure(figsize=(7, 5))
sns.barplot(data=avg_10, x='Intervention', y='AvgReduction', palette='Set2')
plt.title("Average Stunting Reduction (%): 10% Nutrient Increase")
plt.ylabel("Avg Reduction (%)")
plt.ylim(0, avg_10['AvgReduction'].max() + 0.5)
plt.tight_layout()
plt.savefig("plot_avg_10percent_only.png")
plt.show()

# -------------------
# 2. Heatmap by district
# -------------------
heatmap_10 = df_10.set_index('District').drop(columns='Province')

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_10, annot=True, cmap='YlOrRd', fmt=".1f", linewidths=0.5)
plt.title("Stunting Reduction by District (10% Micronutrient Increase)")
plt.tight_layout()
plt.savefig("plot_heatmap_10percent_only.png")
plt.show()
