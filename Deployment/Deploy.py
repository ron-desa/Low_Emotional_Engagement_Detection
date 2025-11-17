import serial
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
# -------------------------------
# CONFIG
# -------------------------------

PORT = "/dev/ttyUSB0"
BAUD = 9600
WINDOW_SECONDS = 5

MODEL_PATH = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning/PHYSIO/final_physio_active_model.pkl"
FEATURE_PATH = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning/PHYSIO/feature_order.pkl"

OUTPUT_CSV = "/home/rounak/CODE/Low_Engagement_Detection/Deployment/realtime_predictions.csv"
PRED_JSON = Path("/home/rounak/CODE/Low_Engagement_Detection/annotate_app/public/prediction.json")

THRESHOLD = 0.5  # adjust if needed


# -------------------------------
# LOAD MODEL + FEATURE ORDER
# -------------------------------

print("Loading model...")
model = joblib.load(MODEL_PATH)

print("Loading feature order...")
FEATURES = joblib.load(FEATURE_PATH)

print("Model & features loaded successfully.")
print("Expected feature order:", FEATURES)

# -------------------------------
# REAL-TIME BUFFERS
# -------------------------------

buffer = []
prev_gsr_mean = None
prev_hr_mean = None

# -------------------------------
# CONNECT TO ARDUINO
# -------------------------------

print(f"Connecting to Arduino at {PORT}...")
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
print("Connected!\n")


# -------------------------------
# CSV HEADER
# -------------------------------

with open(OUTPUT_CSV, "w") as f:
    f.write("timestamp,prediction,probability\n")


# -------------------------------
# FEATURE EXTRACTION FUNCTION
# -------------------------------

def compute_features(df):
    global prev_gsr_mean, prev_hr_mean

    gsr = df["gsr"].values
    hr = df["hr"].values

    features = {}

    # Required features
    features["GSR_mean"] = np.mean(gsr)
    features["GSR_variance"] = np.var(gsr)

    features["HR_mean"] = np.mean(hr)
    features["HR_variance"] = np.var(hr)

    features["75_percentile_GSR"] = np.percentile(gsr, 75)
    features["75_percentile_HR"] = np.percentile(hr, 75)

    # Difference features
    if prev_gsr_mean is None:
        features["GSRmean_diff"] = 0
        features["HRmean_diff"] = 0
        features["GSRmean_persen_diff"] = 0
        features["HRmean_persent_diff"] = 0
    else:
        features["GSRmean_diff"] = features["GSR_mean"] - prev_gsr_mean
        features["HRmean_diff"] = features["HR_mean"] - prev_hr_mean

        features["GSRmean_persen_diff"] = (
            features["GSRmean_diff"] / prev_gsr_mean if prev_gsr_mean != 0 else 0
        )
        features["HRmean_persent_diff"] = (
            features["HRmean_diff"] / prev_hr_mean if prev_hr_mean != 0 else 0
        )

    # Update memory
    prev_gsr_mean = features["GSR_mean"]
    prev_hr_mean = features["HR_mean"]

    # Return in correct order as model expects
    ordered_values = [features[f] for f in FEATURES]

    return pd.DataFrame([ordered_values], columns=FEATURES)


def write_prediction_json(window_unix_start_ms, window_unix_end_ms, prob, pred):
    # load existing
    try:
        data = json.loads(PRED_JSON.read_text())
    except Exception:
        data = []

    entry = {
        "window_start_ms": int(window_unix_start_ms),
        "window_end_ms": int(window_unix_end_ms),
        "prob": float(prob),
        "pred": int(pred)
    }
    data.append(entry)
    # keep last 200 windows
    data = data[-200:]
    PRED_JSON.write_text(json.dumps(data))

# -------------------------------
# MAIN LOOP
# -------------------------------

print("Starting real-time inference...\n")
window_start = time.time()

while True:
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if not line:
        continue

    parts = line.split(",")
    if len(parts) != 3:
        continue

    try:
        millis = int(parts[0])
        gsr = int(parts[1])
        hr = int(parts[2])
    except:
        continue

    buffer.append({"gsr": gsr, "hr": hr})

    # -------- Every 5 seconds -------- #
    if time.time() - window_start >= WINDOW_SECONDS:

        df = pd.DataFrame(buffer)

        if len(df) >= 5:  # must have enough samples
            feat_df = compute_features(df)

            proba = model.predict_proba(feat_df)[0][1]
            pred = int(proba > THRESHOLD)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Suppose you have window start and end as POSIX seconds (or you can get them from timestamp_ms)
            window_unix_end_ms = int(time.time()*1000)
            window_unix_start_ms = window_unix_end_ms - (WINDOW_SECONDS*1000)
            write_prediction_json(window_unix_start_ms, window_unix_end_ms, proba, pred)

            print(f"[{timestamp}] → Prediction: {pred} | Probability: {proba:.4f}")

            with open(OUTPUT_CSV, "a") as f:
                f.write(f"{timestamp},{pred},{proba:.5f}\n")

        # Reset
        buffer = []
        window_start = time.time()
