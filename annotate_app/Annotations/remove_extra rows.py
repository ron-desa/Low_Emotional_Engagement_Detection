import pandas as pd
import os
user_name="Aditya_32"
# File paths
input_file = f"/home/rounak/CODE/Low_Engagement_Detection/annotate_app/Annotations/{user_name}.csv"
output_dir = '/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Annotations'

# Get user input for the file name number
user_number = input("Enter user number for filename (e.g., 1): ")

# Load the CSV file
df = pd.read_csv(input_file)

# Check if the file has at least 1 rows
if len(df) < 1:
    print("The file has fewer than 1 rows. Nothing to export.")
else:
    # Remove the last 17 rows
    df_trimmed = df.iloc[:-1]

    # Construct the output file path
    output_filename = f'user{user_number}_annotations.csv'
    output_path = os.path.join(output_dir, output_filename)

    # Save the trimmed DataFrame
    df_trimmed.to_csv(output_path, index=False)
    print(f"File saved to: {output_path}")
