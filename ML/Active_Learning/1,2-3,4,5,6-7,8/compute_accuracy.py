
import pandas as pd
import os

# ==== CONFIG ====
input_file = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning/1,2-3,4,5,6-7,8/AL_y_test_vs_y_pred_comparison0.9.csv"
output_file = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning/1,2-3,4,5,6-7,8/user_accuracy_results.csv"
threshold = 0.9   # <-- change this when running for other thresholds
# ================

# Read dataset
df = pd.read_csv(input_file, header=None, names=["User", "Y_test", "Y_pred"])

# Function to calculate accuracy per user
def compute_accuracy(user_df):
    TP = ((user_df["Y_test"] == 1) & (user_df["Y_pred"] == 1)).sum()
    TN = ((user_df["Y_test"] == 0) & (user_df["Y_pred"] == 0)).sum()
    FP = ((user_df["Y_test"] == 0) & (user_df["Y_pred"] == 1)).sum()
    FN = ((user_df["Y_test"] == 1) & (user_df["Y_pred"] == 0)).sum()
    
    total = TP + TN + FP + FN
    return (TP + TN) / total if total > 0 else 0.0

# Calculate per-user accuracy
user_accuracy = df.groupby("User").apply(compute_accuracy).reset_index()
user_accuracy.columns = ["User", f"Threshold_{threshold}"]

# Merge results with existing file
if os.path.exists(output_file):
    existing = pd.read_csv(output_file)
    merged = pd.merge(existing, user_accuracy, on="User", how="outer")
else:
    merged = user_accuracy

# Save results (rounded to 10 decimals like your example)
merged = merged.round(10)
merged.to_csv(output_file, index=False)

print(f"✅ User-wise accuracy (using TP/TN/FP/FN) saved to {output_file}")
