import numpy as np
import pandas as pd
import os
import csv
from sklearn.metrics import f1_score
from xgboost import XGBClassifier
import joblib

# =====================================================================
# 1. LOAD PHYSIOLOGICAL DATA
# =====================================================================
DATA_PATH = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/alluser_normalized_allfeatures.csv"
print("Loading dataset...")
data = pd.read_csv(DATA_PATH)

# We only need these features:
FEATURES = [
    "GSR_mean", "GSR_variance",
    "HR_mean", "HR_variance",
    "75_percentile_GSR", "75_percentile_HR",
    "GSRmean_persen_diff", "HRmean_persent_diff",
    "GSRmean_diff", "HRmean_diff"
]

LABEL = "probe"

print("Data loaded with shape:", data.shape)

# =====================================================================
# 2. VIDEO SPLIT CONFIG
# =====================================================================
BASELINE_VIDEOS = [1, 2]
ACTIVE_VIDEOS = [3, 4, 5, 6]
TEST_VIDEOS = [7, 8]

print("Baseline videos:", BASELINE_VIDEOS)
print("Active videos:", ACTIVE_VIDEOS)
print("Testing videos:", TEST_VIDEOS)

# =====================================================================
# 3. OUTPUT FOLDER
# =====================================================================
OUTPUT_BASE = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning/PHYSIO"
os.makedirs(OUTPUT_BASE, exist_ok=True)

# Output logs
PROBE_LOG = os.path.join(OUTPUT_BASE, "probe_counts.csv")
COMPARE_LOG = os.path.join(OUTPUT_BASE, "y_true_vs_pred.csv")
SUMMARY_TPR = os.path.join(OUTPUT_BASE, "summary_TPR.csv")
SUMMARY_FPR = os.path.join(OUTPUT_BASE, "summary_FPR.csv")
SUMMARY_F1M = os.path.join(OUTPUT_BASE, "summary_F1_macro.csv")
SUMMARY_F1W = os.path.join(OUTPUT_BASE, "summary_F1_weighted.csv")

# =====================================================================
# 4. SPLIT DATASET
# =====================================================================
df = data.copy()

df_base = df[df["video_id"].isin(BASELINE_VIDEOS)]
df_active = df[df["video_id"].isin(ACTIVE_VIDEOS)]
df_test = df[df["video_id"].isin(TEST_VIDEOS)]

print("Baseline size:", len(df_base))
print("Active size:", len(df_active))
print("Test size:", len(df_test))

# =====================================================================
# 5. PREPARE TRAIN AND TEST SETS
# =====================================================================
X_base = df_base[FEATURES]
y_base = df_base[LABEL]

# Final test set (same for all users)
X_test_full = df_test[FEATURES]
y_test_full = df_test[LABEL]

# =====================================================================
# 6. BASE MODEL TRAINING
# =====================================================================
print("\nTraining baseline model...")

model = XGBClassifier(
    objective="binary:logistic",
    max_depth=6,
    n_estimators=200,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_base, y_base)
print("Baseline training complete.")

# =====================================================================
# 7. ACTIVE LEARNING START
# =====================================================================
print("\nStarting Active Learning...")

# Prepare DataFrames for logging
probe_log_rows = []
compare_rows = []

# Per-user metrics dicts
user_tpr = {}
user_fpr = {}
user_f1_macro = {}
user_f1_weighted = {}

THRESHOLD = 0.5   # FIXED THRESHOLD for AL
users = sorted(df["P_id"].unique())

for user in users:

    print(f"\n=== ACTIVE LEARNING FOR USER {user} ===")

    # Extract this user's active and test data
    user_active = df_active[df_active["P_id"] == user]
    user_test = df_test[df_test["P_id"] == user]

    X_active = user_active[FEATURES]
    y_active = user_active[LABEL]

    X_test = user_test[FEATURES]
    y_test = user_test[LABEL]

    # Local copies of training set
    X_train = X_base.copy()
    y_train = y_base.copy()

    probe_count = 0

    # Row-wise active sampling
    for i in range(len(X_active)):
        x_i = X_active.iloc[[i]]
        y_i = y_active.iloc[i]

        prob = model.predict_proba(x_i)[0][1]

        if prob < THRESHOLD:
            # Low confidence → probe + add to training set
            X_train = pd.concat([X_train, x_i])
            y_train = pd.concat([y_train, pd.Series([y_i])])
            probe_count += 1

    print(f"User {user}: Probed {probe_count} samples.")

    # Retrain after completing AL for this user
    model.fit(X_train, y_train)

    # Final predictions on the user’s test-s
