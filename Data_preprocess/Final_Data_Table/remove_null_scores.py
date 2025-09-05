import pandas as pd

# File path
file_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table/merged_all_1_to_40_Original.csv"
file_path1 = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table/merged_all_1_to_40.csv"

# Load dataset
df = pd.read_csv(file_path)

# Interpolate missing values in 'Score' using neighbors
df["Score"] = df["Score"].interpolate(method="linear")

# If any NaNs remain at start/end, fill them using nearest values
df["Score"] = df["Score"].fillna(method="bfill").fillna(method="ffill")

# Double-check
print("Remaining nulls in Score:", df["Score"].isnull().sum())

# Export back to the same location (overwrite original file)
df.to_csv(file_path1, index=False)

print(f"✅ File updated and saved at: {file_path}")
