import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# Config
USER_ID = 1
INPUT_ANNOTATION = '/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Annotations/user1_annotations.csv'
INPUT_PHYSIO = '/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Physiological_signals/cleaned_user1_physiological.csv'
OUTPUT_DIR = 'scores/'
WINDOW_DURATION_MS = 5000  # 5-second window

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load annotation data
annotations = pd.read_csv(INPUT_ANNOTATION)
annotations.columns = ['time', 'valence', 'arousal', 'videoID']
annotations['time'] = annotations['time'].astype(np.int64)

# # Load physiological data (no header in original file)
# physio = pd.read_csv(INPUT_PHYSIO, header=None)
# physio.columns = ['ArduinoTime_ms', 'GSR', 'HR', 'SystemTime_ms', 'Datetime']
# physio['SystemTime_ms'] = physio['SystemTime_ms'].astype(np.int64)

# Step 1: Load with no headers
# physio = pd.read_csv(INPUT_PHYSIO, header=None)
physio = pd.read_csv(INPUT_PHYSIO, header=None, sep=',', engine='python')

physio.columns = ['ArduinoTime_ms', 'GSR', 'Pulse', 'SystemTime_ms', 'Datetime']

# Step 2: Remove row where column name slipped into data
physio = physio[physio['SystemTime_ms'] != 'SystemTime_ms']

# Step 3: Convert SystemTime_ms safely
physio['SystemTime_ms'] = pd.to_numeric(physio['SystemTime_ms'], errors='coerce')
physio = physio.dropna(subset=['SystemTime_ms'])  # Drop rows with NaNs
physio['SystemTime_ms'] = physio['SystemTime_ms'].astype(np.int64)

# Drop rows with invalid/missing values
# physio = physio.dropna(subset=['SystemTime_ms', 'GSR', 'HR'])
physio['SystemTime_ms'] = physio['SystemTime_ms'].astype(np.int64)


# Convert for filtering
physio['Datetime'] = pd.to_datetime(physio['SystemTime_ms'], unit='ms')

for video_id in annotations['videoID'].unique():
    # Get time bounds for this video
    video_ann = annotations[annotations['videoID'] == video_id]
    start_time = video_ann['time'].min()
    end_time = video_ann['time'].max() + 10000  # Add buffer

    # Extract relevant signal segment
    segment = physio[(physio['SystemTime_ms'] >= start_time) & (physio['SystemTime_ms'] <= end_time)].copy()
    if segment.empty:
        print(f"[Skip] No signal data for video {video_id}")
        continue

    window_scores = []
    time_bounds = []

    current_start = segment['SystemTime_ms'].min()
    current_end = current_start + WINDOW_DURATION_MS

    while current_end <= segment['SystemTime_ms'].max():
        window = segment[(segment['SystemTime_ms'] >= current_start) & (segment['SystemTime_ms'] < current_end)]
        if len(window) > 1:
            gsr_mean = window['GSR'].mean()
            hr_mean = window['HR'].mean()
            time_bounds.append((current_start, (current_start + current_end) // 2, current_end))
            window_scores.append([gsr_mean, hr_mean])
        current_start = current_end
        current_end += WINDOW_DURATION_MS

    if len(window_scores) < 2:
        print(f"[Skip] Not enough valid windows for video {video_id}")
        continue

    # Compute difference between windows
    features = np.array(window_scores)
    diffs = np.linalg.norm(np.diff(features, axis=0), axis=1)
    diffs = np.insert(diffs, 0, diffs[0])  # pad first

    # Normalize scores
    norm_scores = MinMaxScaler().fit_transform(diffs.reshape(-1, 1)).flatten()

    # Create output dataframe
    result_rows = []
    for (start, border, end), score in zip(time_bounds, norm_scores):
        result_rows.append([start, border, end, score])

    df_scores = pd.DataFrame(result_rows, columns=['Start', 'Border', 'End', 'Score'])
    file_id = int(f"{USER_ID}{video_id}")
    df_scores.to_csv(f"{OUTPUT_DIR}{file_id}_scores.csv", index=False)
    print(f"[OK] Wrote: {OUTPUT_DIR}{file_id}_scores.csv")
