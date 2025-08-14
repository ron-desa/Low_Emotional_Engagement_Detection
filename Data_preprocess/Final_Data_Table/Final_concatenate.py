import pandas as pd
import os

# Base path and filename pattern
base_dir = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Merge_Eye+Physio"
filename_pattern = "merged_output{}.csv"

out_dir="/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table"

# Define how many files you expect or use os.listdir() for auto-detection
max_pid = 32  # or change this to a large number to scan dynamically

dataframes = []

for pid in range(1, max_pid + 1):
    file_path = os.path.join(base_dir, filename_pattern.format(pid))
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["P_id"] = pid  # Ensure correct P_id
            dataframes.append(df)
            print(f"Loaded file: {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    else:
        print(f"File not found (skipped): {file_path}")

# Concatenate all
if dataframes:
    merged_df = pd.concat(dataframes, ignore_index=True)
    output_path = os.path.join(out_dir, f"merged_all_1_to_{max_pid}.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"Merged CSV saved to {output_path}")
else:
    print("No valid CSV files found to merge.")
