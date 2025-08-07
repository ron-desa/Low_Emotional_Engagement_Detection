import pandas as pd
import json
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
DATA_DIR = Path("/mnt/data1/HCI WORK/Low Engagement Detection/Pupil Recordings/User_15_recording/001")
GAZE_PATH = DATA_DIR / "exports/000/gaze_positions.csv"
PUPIL_PATH = DATA_DIR / "exports/000/pupil_positions.csv"
INFO_JSON_PATH = DATA_DIR / "info.player.json"

# -----------------------------
# FUNCTION: Load Data
# -----------------------------
def load_data():
    print("Loading data...")
    gaze_df = pd.read_csv(GAZE_PATH)
    pupil_df = pd.read_csv(PUPIL_PATH)

    with open(INFO_JSON_PATH, 'r') as f:
        info_data = json.load(f)
    start_time_synced_s = info_data["start_time_synced_s"]
    start_time_system_s = info_data["start_time_system_s"]
    print("Data loaded successfully.")
    return gaze_df, pupil_df, start_time_synced_s,start_time_system_s

# -----------------------------
# FUNCTION: Sync timestamps
# -----------------------------
def sync_timestamps(df, start_time_synced_s,start_time_system_s, timestamp_col):
    """
    Normalize timestamps using `start_time_synced_s`
    Adds a new column: `timestamp_synced`
    """
    # df["timestamp_synced"] = df[timestamp_col] - start_time_synced_s
    # Align to Unix time (same as physio)
    df["timestamp_synced"] = df[timestamp_col] - start_time_synced_s + start_time_system_s

    return df

# -----------------------------
# FUNCTION: Split pupil data
# -----------------------------
def split_pupil_df(pupil_df):
    """
    Splits pupil_df into:
    - pupil_pye3d_df: method contains 'pye3d'
    - pupil_2dcpp_df: method contains '2d c++'
    """
    pupil_pye3d_df = pupil_df[pupil_df['method'].str.contains("pye3d", case=False, na=False)].copy()
    pupil_2dcpp_df = pupil_df[pupil_df['method'].str.contains("2d c++", case=False, na=False)].copy()

    print(f"Total pupil rows: {len(pupil_df)}")
    print(f"Pye3D rows: {len(pupil_pye3d_df)}")
    print(f"2D C++ rows: {len(pupil_2dcpp_df)}")

    return pupil_pye3d_df, pupil_2dcpp_df

def evaluate_timestamp_gaps(gaze_df, pupil_df, pupil_label="pye3d"):
    """
    Evaluates how closely pupil timestamps align with gaze timestamps.
    Outputs summary stats and optionally a histogram.
    """
    # Sort
    gaze_sorted = gaze_df.sort_values("timestamp_synced").copy()
    pupil_sorted = pupil_df.sort_values("timestamp_synced").copy()

    # Rename gaze timestamp for comparison after merge
    gaze_sorted = gaze_sorted.rename(columns={"timestamp_synced": "gaze_timestamp_synced"})

    # Do merge_asof (pupil left, gaze right)
    merged = pd.merge_asof(
        pupil_sorted,
        gaze_sorted,
        left_on="timestamp_synced",
        right_on="gaze_timestamp_synced",
        direction='nearest',
        tolerance=None  # for now, no limit
    )

    # Compute absolute time difference
    merged["time_gap"] = (merged["timestamp_synced"] - merged["gaze_timestamp_synced"]).abs()

    # Drop rows where no gaze match was found
    merged = merged.dropna(subset=["gaze_timestamp_synced"])

    # Print summary
    print(f"\n--- Timestamp Gap Analysis ({pupil_label}) ---")
    print("Count:", len(merged))
    print("Min gap (s):", merged["time_gap"].min())
    print("Mean gap (s):", merged["time_gap"].mean())
    print("Median gap (s):", merged["time_gap"].median())
    print("Max gap (s):", merged["time_gap"].max())

    return merged[["timestamp_synced", "gaze_timestamp_synced", "time_gap"]]

def merge_pupil_with_gaze(pupil_df, gaze_df, label):
    """
    Merges pupil and gaze data using timestamp alignment with 2ms tolerance.
    Assumes both DataFrames have a `timestamp_synced` column.
    """
    pupil_sorted = pupil_df.sort_values("timestamp_synced").copy()
    gaze_sorted = gaze_df.sort_values("timestamp_synced").copy()

    merged = pd.merge_asof(
        pupil_sorted,
        gaze_sorted,
        on="timestamp_synced",
        direction='nearest',
        tolerance=0.002
    )

    merged = merged.dropna(subset=["gaze_timestamp"])  # or any key gaze column

    print(f"Merged {label} shape:", merged.shape)
    return merged

def inspect_merged_data(df, label):
    # print(f"\n--- Inspection Summary for {label} ---")
    # print("Shape:", df.shape)
    # print("Nulls per column:\n", df.isnull().sum())
    # print("Confidence stats:\n", df['confidence'].describe())
    # print("Timestamp range:\n", df['timestamp_synced'].min(), "to", df['timestamp_synced'].max())

    print(f"\n--- Inspecting merged data ({label}) ---")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())

    # if "confidence" in df.columns:
    #     print("Confidence stats:\n", df["confidence"].describe())
    # else:
    #     print("No 'confidence' column present in this dataset.")
    if "confidence_x" in df.columns:
        print("Pupil confidence stats (confidence_x):\n", df["confidence_x"].describe())
    if "confidence_y" in df.columns:
        print("Gaze confidence stats (confidence_y):\n", df["confidence_y"].describe())

def check_nulls(df, label):
    print(f"\n--- Null value report for {label} ---")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0].sort_values(ascending=False)
    if nulls.empty:
        print("No null values found.")
    else:
        print(nulls)

import matplotlib.pyplot as plt

def plot_confidence_hist(df, label):
    plt.figure(figsize=(12, 5))

    if "confidence_x" in df.columns:
        plt.subplot(1, 2, 1)
        df["confidence_x"].hist(bins=100)
        plt.title(f"{label} - Pupil confidence (confidence_x)")

    if "confidence_y" in df.columns:
        plt.subplot(1, 2, 2)
        df["confidence_y"].hist(bins=100)
        plt.title(f"{label} - Gaze confidence (confidence_y)")

    plt.tight_layout()
    plt.show()
def low_confidence_report(df, label, thresholds=[0.4, 0.5, 0.6, 0.7]):
    print(f"\n--- Low confidence report for {label} ---")
    total = len(df)

    for t in thresholds:
        gaze_low = df[df["confidence_y"] < t]
        pupil_low = df[df["confidence_x"] < t]

        print(f"Threshold < {t}: Gaze={len(gaze_low)/total:.2%}, Pupil={len(pupil_low)/total:.2%}")
def check_invalid_3d(df, label):
    print(f"\n--- Invalid 3D coordinates check for {label} ---")

    for col_group in [["gaze_point_3d_x", "gaze_point_3d_y", "gaze_point_3d_z"],
                      ["eye_center0_3d_x", "eye_center0_3d_y", "eye_center0_3d_z"],
                      ["eye_center1_3d_x", "eye_center1_3d_y", "eye_center1_3d_z"]]:
        invalid = df[(df[col_group[0]] == 0) & (df[col_group[1]] == 0) & (df[col_group[2]] == 0)]
        print(f"{' / '.join(col_group)}: {len(invalid)} rows ({len(invalid)/len(df):.2%})")
def correlation_confidence(df, label):
    print(f"\n--- Confidence correlation for {label} ---")
    if "confidence_x" in df.columns and "confidence_y" in df.columns:
        corr = df["confidence_x"].corr(df["confidence_y"])
        print(f"Pearson correlation (pupil vs gaze): {corr:.4f}")
    else:
        print("One or both confidence columns missing.")

def filter_eye_data(merged_df, confidence_threshold=0.5):
    """
    Filters out rows with low confidence in pupil data and invalid 3D gaze points.
    Also removes rows likely to be blinks (very low confidence).
    
    Parameters:
        merged_df (pd.DataFrame): Merged gaze + pupil dataframe.
        confidence_threshold (float): Minimum confidence to keep a row.
    
    Returns:
        filtered_df (pd.DataFrame): Cleaned DataFrame.
    """
    # Step 1: Filter by pupil confidence (both eyes should be at least above threshold)
    conf_filter = (merged_df['confidence_x'] >= confidence_threshold) & (merged_df['confidence_y'] >= confidence_threshold)
    
    # Step 2: Drop rows where any of the 3D gaze values are NaN
    gaze_filter = merged_df[['gaze_point_3d_x', 'gaze_point_3d_y', 'gaze_point_3d_z']].notna().all(axis=1)
    
    # Combine filters
    final_filtered_df = merged_df[conf_filter & gaze_filter].reset_index(drop=True)
    
    print(f"Original rows: {len(merged_df)}")
    print(f"After filtering: {len(final_filtered_df)}")
    
    return final_filtered_df

import pandas as pd
import numpy as np

import pandas as pd
import numpy as np

def segment_into_windows(df, window_size_sec=5):
    """
    Splits the eye data into fixed-length windows (default 5 seconds).
    Returns a DataFrame where each row contains a window's data and its time range.
    """
    df = df.copy()
    df['pupil_timestamp_sec'] = df['pupil_timestamp'] #/ 1e6  # convert from microseconds to seconds

    min_time = df['pupil_timestamp_sec'].min()
    max_time = df['pupil_timestamp_sec'].max()

    windowed_data = []

    start = min_time
    while start < max_time:
        end = start + window_size_sec
        window_df = df[(df['pupil_timestamp_sec'] >= start) & (df['pupil_timestamp_sec'] < end)]

        if not window_df.empty:
            windowed_data.append({
                'start_time': start,
                'end_time': end,
                'data': window_df
            })

        start = end

    return pd.DataFrame(windowed_data)


def extract_features_from_window(start_time, end_time, df_window):
    """
    Extract rich pupil and gaze features for a time window.
    Returns a dictionary of features.
    """
    features = {
        "start_time_sec": start_time,
        "end_time_sec": end_time,
        "num_samples": len(df_window),
    }

    # Pupil diameter
    features["pupil_diameter_mean"] = df_window["diameter"].mean()
    features["pupil_diameter_std"] = df_window["diameter"].std()

    # 3D Pupil features
    features["diameter_3d_mean"] = df_window["diameter_3d"].mean()
    features["diameter_3d_std"] = df_window["diameter_3d"].std()
    features["sphere_radius_mean"] = df_window["sphere_radius"].mean()
    features["circle_3d_radius_mean"] = df_window["circle_3d_radius"].mean()

    # Ellipse shape & angle
    features["ellipse_axis_a_mean"] = df_window["ellipse_axis_a"].mean()
    features["ellipse_axis_b_mean"] = df_window["ellipse_axis_b"].mean()
    features["ellipse_angle_mean"] = df_window["ellipse_angle"].mean()
    features["ellipse_angle_std"] = df_window["ellipse_angle"].std()

    # Confidence
    features["confidence_x_mean"] = df_window["confidence_x"].mean()
    features["confidence_y_mean"] = df_window["confidence_y"].mean()
    features["confidence_x_std"] = df_window["confidence_x"].std()
    features["confidence_y_std"] = df_window["confidence_y"].std()

    # Blink count (low confidence or zero diameter)
    features["blink_count"] = ((df_window["confidence_x"] < 0.6) | (df_window["diameter"] == 0)).sum()

    # Gaze point movement (3D)
    gaze_coords = df_window[["gaze_point_3d_x", "gaze_point_3d_y", "gaze_point_3d_z"]].dropna()
    if len(gaze_coords) > 1:
        diff = gaze_coords.diff().dropna()
        gaze_movement = np.sqrt((diff**2).sum(axis=1))
        features["gaze_movement_mean"] = gaze_movement.mean()
        features["gaze_movement_std"] = gaze_movement.std()
    else:
        features["gaze_movement_mean"] = 0.0
        features["gaze_movement_std"] = 0.0

    # Gaze direction variability
    gaze_dirs = df_window[["gaze_normal0_x", "gaze_normal0_y", "gaze_normal0_z"]].dropna()
    features["gaze_dir_variability"] = gaze_dirs.std().mean() if not gaze_dirs.empty else 0.0

    # Eye center movement (head movement proxy)
    eye_centers = df_window[["eye_center0_3d_x", "eye_center0_3d_y", "eye_center0_3d_z"]].dropna()
    if len(eye_centers) > 1:
        diff = eye_centers.diff().dropna()
        head_movement = np.sqrt((diff**2).sum(axis=1))
        features["eye_center_movement_mean"] = head_movement.mean()
        features["eye_center_movement_std"] = head_movement.std()
    else:
        features["eye_center_movement_mean"] = 0.0
        features["eye_center_movement_std"] = 0.0

    # Outlier ratio
    total = len(df_window)
    missing = df_window.isna().sum().sum()
    features["missing_value_ratio"] = missing / (total * df_window.shape[1])

    return features



def extract_all_features(windows_df):
    """
    Applies feature extraction to all time windows.
    Returns a new DataFrame of extracted features per window.
    """
    features_list = []

    for _, row in windows_df.iterrows():
        start_time = row['start_time']
        end_time = row['end_time']
        df_window = row['data']

        if df_window is None or df_window.empty:
            continue

        features = extract_features_from_window(start_time, end_time, df_window)
        features_list.append(features)

    return pd.DataFrame(features_list)


def debug_window_counts(df, window_size_sec=5):
    """
    Helps debug how data is segmented into windows by returning row counts per window.
    """
    df = df.copy()
    df['pupil_timestamp_sec'] = df['pupil_timestamp'] / 1e6  # convert microseconds to seconds

    min_time = df['pupil_timestamp_sec'].min()
    max_time = df['pupil_timestamp_sec'].max()

    print(f"Data range: {min_time:.2f} to {max_time:.2f} seconds")

    start = min_time
    counts = []

    while start < max_time:
        end = start + window_size_sec
        count = ((df['pupil_timestamp_sec'] >= start) & (df['pupil_timestamp_sec'] < end)).sum()
        counts.append((start, end, count))
        start = end

    return pd.DataFrame(counts, columns=["start_time", "end_time", "num_rows"])



def merge_eye_and_physiological_features(pupil_features_df, physio_csv_path, user_id):
    """
    Merges pupil/gaze features with physiological features for a specific user.
    
    Args:
        pupil_features_df (pd.DataFrame): DataFrame of pupil features with start_time_sec and end_time_sec columns.
        physio_csv_path (str): Path to physiological features CSV.
        user_id (int): The participant ID to filter physiological data.
        
    Returns:
        pd.DataFrame: Merged multimodal feature set.
    """
    # Load and filter physiological data
    physio_df = pd.read_csv(physio_csv_path)
    physio_df = physio_df[physio_df["P_id"] == user_id].copy()

    # Convert milliseconds to seconds
    physio_df["start_time_sec"] = physio_df["start_time"] / 1000
    physio_df["end_time_sec"] = physio_df["end_time"] / 1000

    merged_data = []

    for _, pupil_row in pupil_features_df.iterrows():
        start_eye = pupil_row["start_time_sec"]
        end_eye = pupil_row["end_time_sec"]

        # Find overlapping physiological windows
        overlapping = physio_df[
            (physio_df["start_time_sec"] < end_eye) &
            (physio_df["end_time_sec"] > start_eye)
        ]

        if not overlapping.empty:
            overlapping["overlap"] = overlapping.apply(
                lambda row: min(end_eye, row["end_time_sec"]) - max(start_eye, row["start_time_sec"]),
                axis=1
            )

            best_match = overlapping.sort_values(by="overlap", ascending=False).iloc[0]
            
            # Merge pupil and physiological data
            merged_row = pd.concat([
                pupil_row,
                best_match.drop(["start_time", "end_time", "start_time_sec", "end_time_sec", "overlap"])
            ])
            merged_data.append(merged_row)

    return pd.DataFrame(merged_data)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def main():
    user_id= int(input("Please Enter the User ID"))
    gaze_df, pupil_df, start_time_synced_s , start_time_system_s= load_data()

    # Sync timestamps
    gaze_df = sync_timestamps(gaze_df, start_time_synced_s,start_time_system_s, "gaze_timestamp")
    pupil_df = sync_timestamps(pupil_df, start_time_synced_s,start_time_system_s, "pupil_timestamp")

    # Split pupil data
    pupil_pye3d_df, pupil_2dcpp_df = split_pupil_df(pupil_df)

    print("Timestamps synced.")
    print("Gaze synced head:\n", gaze_df[["gaze_timestamp", "timestamp_synced"]].head())
    print("Pupil synced head:\n", pupil_df[["pupil_timestamp", "timestamp_synced"]].head())

    # print(pupil_pye3d_df.head())

    # Test timestamp alignment before choosing tolerance
    print("\nEvaluating time gaps for pye3d:")
    evaluate_timestamp_gaps(gaze_df, pupil_pye3d_df, "pye3d")

    print("\nEvaluating time gaps for 2d c++:")
    evaluate_timestamp_gaps(gaze_df, pupil_2dcpp_df, "2dcpp")

    # Step 5: Merge gaze_df with pupil data (separately for pye3d and 2dcpp)
    merged_pye3d = merge_pupil_with_gaze(pupil_pye3d_df, gaze_df, label="pye3d")
    merged_2dcpp = merge_pupil_with_gaze(pupil_2dcpp_df, gaze_df, label="2dcpp")

    inspect_merged_data(merged_pye3d, "pye3d")
    inspect_merged_data(merged_2dcpp, "2dcpp")

    # for df, name in [(merged_pye3d, "pye3d"), (merged_2dcpp, "2dcpp")]:
    #     check_nulls(df, name)
    #     plot_confidence_hist(df, name)
    #     low_confidence_report(df, name)
    #     check_invalid_3d(df, name)
    #     correlation_confidence(df, name)
    filtered_eye_df = filter_eye_data(merged_pye3d)
    # print("---Filtered head---")
    # print(filtered_eye_df.head(10))
    # print("---Filtered Columns---")
    # print(filtered_eye_df.columns)

    # print("Min pupil_timestamp:", filtered_eye_df["pupil_timestamp"].min())
    # print("Max pupil_timestamp:", filtered_eye_df["pupil_timestamp"].max())

    # print("Duration in seconds:", (filtered_eye_df["pupil_timestamp"].max() - filtered_eye_df["pupil_timestamp"].min()) / 1e6)

    # debug_df = debug_window_counts(filtered_eye_df)
    # print(debug_df.head(10))

    windows_df = segment_into_windows(filtered_eye_df)
    print("Num windows:", len(windows_df))

    features_df = extract_all_features(windows_df)
    features_df.to_csv(f"pupil_features{user_id}.csv", index=False)
    # print(features_df.head())  # Should show multiple rows now

    print(features_df[['start_time_sec', 'end_time_sec']].head())


    # Path to physiological features file
    physio_csv_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/alluser_normalized_allfeatures.csv"

    # Merge the features
    merged_df = merge_eye_and_physiological_features(features_df, physio_csv_path, user_id)

    # Save the final merged dataset
    merged_df.to_csv("final_merged_multimodal_features.csv", index=False)
    print(f"Merged multimodal dataset saved with shape: {merged_df.shape}")

    print("---------------------------------------------")
    import pandas as pd

    physio_df = pd.read_csv("/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/alluser_normalized_allfeatures.csv")
    physio_df = physio_df[physio_df["P_id"] == 1].copy()
    physio_df["start_time_sec"] = physio_df["start_time"] / 1000
    physio_df["end_time_sec"] = physio_df["end_time"] / 1000

    print(physio_df[['start_time', 'end_time', 'start_time_sec', 'end_time_sec']].head())

# ---delete this later--------
    # # Assuming `filtered_eye_df` is your DataFrame
    # features_df = extract_all_features(filtered_eye_df)

    # # Optionally save to CSV
    # features_df.to_csv("eye_window_features.csv", index=False)
# ---------------------------------------------------------



    # Proceed to next step...
    # split_pupil_df(pupil_df)
    # merge_with_gaze(...)
    # etc.

if __name__ == "__main__":
    main()
