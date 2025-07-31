import pandas as pd
import json
import os

def convert_pupil_to_system_time(pupil_df, start_synced, start_system):
    """
    Convert pupil timestamps to system time (ms).
    """
    pupil_df = pupil_df.copy()
    pupil_df["start_time_ms"] = ((pupil_df["start_time_sec"] - start_synced) + start_system) * 1000
    pupil_df["end_time_ms"] = ((pupil_df["end_time_sec"] - start_synced) + start_system) * 1000
    return pupil_df

def merge_by_time_overlap(features_df, pupil_df):
    """
    Merge two dataframes based on overlapping time windows.
    Each row in `features_df` is matched with overlapping rows in `pupil_df`.
    """
    merged_rows = []

    for _, phys_row in features_df.iterrows():
        # Filter pupil rows that overlap in time
        overlapping = pupil_df[
            (pupil_df["start_time_ms"] < phys_row["end_time"]) & 
            (pupil_df["end_time_ms"] > phys_row["start_time"])
        ]

        for _, pupil_row in overlapping.iterrows():
            merged_row = pd.concat([phys_row, pupil_row])
            merged_rows.append(merged_row)

    if merged_rows:
        return pd.DataFrame(merged_rows)
    else:
        return pd.DataFrame()  # return empty df if no matches

def process_user(user_id, base_signal_path, base_pupil_path, json_info_path):
    """
    Process one user's data and return merged DataFrame.
    """
    # Load main signal data and filter for this user
    signal_df = pd.read_csv(base_signal_path)
    user_df = signal_df[signal_df["P_id"] == float(user_id)].copy()

    # Load pupil data
    pupil_file = os.path.join(base_pupil_path, f"pupil_features{user_id}.csv")
    pupil_df = pd.read_csv(pupil_file)

    # Load corresponding info.player.json
    # with open(os.path.join(json_info_path, f"info.player.json")) as f:
    with open(os.path.join(json_info_path)) as f:
        info = json.load(f)

    start_synced = info["start_time_synced_s"]
    start_system = info["start_time_system_s"]

    # Convert pupil times to system times
    pupil_df = convert_pupil_to_system_time(pupil_df, start_synced, start_system)

    # Merge
    merged_df = merge_by_time_overlap(user_df, pupil_df)
    return merged_df

# Example Usage
if __name__ == "__main__":
    u_id=int(input("Enter The User ID: "))
    base_signal_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/alluser_normalized_allfeatures.csv"
    base_pupil_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess"
    json_info_path ="/mnt/data1/HCI WORK/Low Engagement Detection/Pupil Recordings/User_4_recording/000"
    
    all_merged = []
    for user_id in range(4,5):  # assuming users 1 to 10
        json_info = f"{json_info_path}/info.player.json"
        try:
            merged = process_user(user_id, base_signal_path, base_pupil_path, json_info)
            if not merged.empty:
                all_merged.append(merged)
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")

    final_df = pd.concat(all_merged, ignore_index=True)
    final_df.to_csv(f"merged_output{u_id}.csv", index=False)
    print("Merging complete. Saved to merged_output.csv")
