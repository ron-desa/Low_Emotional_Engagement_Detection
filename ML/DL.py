import os
import csv
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from xgboost import XGBClassifier
from keras.models import Sequential
from keras.layers import Dense, Dropout, SimpleRNN, GRU, Conv1D, MaxPooling1D, Flatten
from keras.optimizers import Adam

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ---------------------- SETTINGS ----------------------
MODEL_TYPE = "GRU"  # Options: "XGB", "RNN", "GRU", "CNN1D"
SEQ_LEN = 20
EPOCHS_BASE = 20
EPOCHS_ACTIVE = 5
BATCH_SIZE = 32
THRESHOLDS = [0.1 * i for i in range(1, 10)]
BASE_PATH = "/home/rounak/CODE/Low_Engagement_Detection/ML/Active_Learning"

# ---------------------- LOAD DATA ----------------------
data = pd.read_csv('/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table/merged_all_1_to_40.csv')
cols_to_drop = ["videoID","start_time","end_time","start_time_sec","end_time_sec",
                "num_samples","start_time_ms","end_time_ms","time","prev_window"]
ds = data.drop(columns=cols_to_drop)

baseline_videos = [1, 2]
active_videos = [3, 4, 5, 6]
test_videos = [7, 8]

folder_name = f"{','.join(map(str, baseline_videos))}-{','.join(map(str, active_videos))}-{','.join(map(str, test_videos))}"
folder_path = os.path.join(BASE_PATH, folder_name)
os.makedirs(folder_path, exist_ok=True)

# ---------------------- MODEL DEFINITIONS ----------------------
def create_rnn(input_shape):
    model = Sequential([
        SimpleRNN(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        SimpleRNN(32),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(1e-3), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_gru(input_shape):
    model = Sequential([
        GRU(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        GRU(32),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(1e-3), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_cnn1d(input_shape):
    model = Sequential([
        Conv1D(64, kernel_size=3, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),
        Conv1D(128, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(1e-3), loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ---------------------- HELPER FUNCTIONS ----------------------
def pad_sequence(X_row, seq_len=SEQ_LEN):
    """Pad single row to SEQ_LEN timesteps"""
    X_pad = np.vstack([X_row.values]*seq_len)
    return X_pad.reshape((1, seq_len, X_row.shape[1]))

def create_sequences(X, y, seq_len=SEQ_LEN):
    """Generate sequences for RNN/GRU/CNN1D"""
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_len + 1):
        X_seq.append(X.iloc[i:i+seq_len].values)
        y_seq.append(y.iloc[i+seq_len-1])
    return np.array(X_seq), np.array(y_seq)

def write_user_scores_to_csv(file_name, data_dict):
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        thresholds = [f"Threshold_{i*0.1}" for i in range(1, 10)]
        writer.writerow(["User"] + thresholds)
        for user, scores in data_dict.items():
            writer.writerow([user] + scores)

# ---------------------- ACTIVE LEARNING ----------------------
user_tpr, user_fpr, user_f1_macro, user_f1_weighted, user_probing_count = {}, {}, {}, {}, {}
cluster = list(range(1,41))

for threshold in THRESHOLDS:
    ds_cluster = ds[ds["P_id"].isin(cluster)].copy()
    
    df_base = ds_cluster[ds_cluster["video_id"].isin(baseline_videos)]
    df_active = ds_cluster[ds_cluster["video_id"].isin(active_videos)]
    df_test = ds_cluster[ds_cluster["video_id"].isin(test_videos)]

    X_base = df_base.drop(['probe','P_id','video_id'], axis=1)
    y_base = df_base['probe']

    feature_cols = X_base.columns.tolist()  # fixed feature columns

    if MODEL_TYPE in ["RNN","GRU","CNN1D"]:
        X_base_seq, y_base_seq = create_sequences(X_base, y_base, SEQ_LEN)

    # Initialize model
    if MODEL_TYPE == "XGB":
        model = XGBClassifier(objective='binary:logistic', max_depth=10, n_estimators=100,
                              learning_rate=0.1, scale_pos_weight=1.5, random_state=42)
        model.fit(X_base, y_base)
    elif MODEL_TYPE == "RNN":
        model = create_rnn((SEQ_LEN, len(feature_cols)))
        model.fit(X_base_seq, y_base_seq, epochs=EPOCHS_BASE, batch_size=BATCH_SIZE, verbose=1)
    elif MODEL_TYPE == "GRU":
        model = create_gru((SEQ_LEN, len(feature_cols)))
        model.fit(X_base_seq, y_base_seq, epochs=EPOCHS_BASE, batch_size=BATCH_SIZE, verbose=1)
    elif MODEL_TYPE == "CNN1D":
        model = create_cnn1d((SEQ_LEN, len(feature_cols)))
        model.fit(X_base_seq, y_base_seq, epochs=EPOCHS_BASE, batch_size=BATCH_SIZE, verbose=1)

    new_X_train, new_y_train = X_base.copy(), y_base.copy()

    for s in np.unique(ds_cluster.P_id):
        user_active = df_active[df_active["P_id"]==s]
        video_probe_counts = {vid:0 for vid in user_active["video_id"].unique()}
        probing_count = 0
        y_probs = []

        for idx in range(len(user_active)):
            test_row = user_active.iloc[[idx]][feature_cols]
            y_test_cur = user_active['probe'].iloc[idx]
            current_video_id = user_active['video_id'].iloc[idx]

            if MODEL_TYPE in ["RNN","GRU","CNN1D"]:
                seq_data = pad_sequence(test_row)
                ypred_prob = model.predict(seq_data, verbose=0)[0][0]
            else:
                ypred_prob = model.predict_proba(test_row)[:,1][0]

            if ypred_prob < threshold:
                probing_count += 1
                video_probe_counts[current_video_id] += 1
                new_X_train = pd.concat([new_X_train, test_row], axis=0)
                new_y_train = pd.concat([new_y_train, pd.Series([y_test_cur])], axis=0)
                continue
            y_probs.append(int(ypred_prob >= threshold))

        # Retrain model
        if MODEL_TYPE == "XGB":
            model.fit(new_X_train, new_y_train)
        else:
            X_train_seq, y_train_seq = create_sequences(new_X_train, new_y_train, SEQ_LEN)
            model.fit(X_train_seq, y_train_seq, epochs=EPOCHS_ACTIVE, batch_size=BATCH_SIZE, verbose=0)

        # Evaluate user test
        final_test = df_test[df_test["P_id"]==s]
        X_final = final_test[feature_cols]
        y_final_true = final_test['probe']

        if MODEL_TYPE == "XGB":
            y_final_pred = (model.predict_proba(X_final)[:,1] >= threshold).astype(int)
            y_true_eval = y_final_true.values
        else:
            X_seq_final, y_seq_final = create_sequences(X_final, y_final_true, SEQ_LEN)
            y_final_pred = (model.predict(X_seq_final).flatten() >= threshold).astype(int)
            y_true_eval = y_final_true.iloc[SEQ_LEN-1:].values

        tp = np.sum((y_final_pred==1) & (y_true_eval==1))
        fn = np.sum((y_final_pred==0) & (y_true_eval==1))
        fp = np.sum((y_final_pred==1) & (y_true_eval==0))
        tn = np.sum((y_final_pred==0) & (y_true_eval==0))

        tpr = tp / (tp + fn + 1e-6)
        fpr = fp / (fp + tn + 1e-6)
        f1_macro = f1_score(y_true_eval, y_final_pred, average='macro')
        f1_weighted = f1_score(y_true_eval, y_final_pred, average='weighted')

        user_tpr.setdefault(s, []).append(tpr)
        user_fpr.setdefault(s, []).append(fpr)
        user_f1_macro.setdefault(s, []).append(f1_macro)
        user_f1_weighted.setdefault(s, []).append(f1_weighted)
        user_probing_count.setdefault(s, []).append(probing_count)

        # Save probe counts
        with open(os.path.join(folder_path, f'AL_Video_split_Probe_Counts_{threshold}.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for vid, count in video_probe_counts.items():
                writer.writerow([s, vid, count])

        # Save predictions
        with open(os.path.join(folder_path, f'AL_y_test_vs_y_pred_comparison_{threshold}.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for t_val, p_val in zip(y_true_eval, y_final_pred):
                writer.writerow([s, t_val, p_val])

# ---------------------- WRITE SUMMARY ----------------------
write_user_scores_to_csv("User_TPR.csv", user_tpr)
write_user_scores_to_csv("User_FPR.csv", user_fpr)
write_user_scores_to_csv("User_F1_Macro.csv", user_f1_macro)
write_user_scores_to_csv("User_F1_Weighted.csv", user_f1_weighted)
write_user_scores_to_csv("User_Probing_Count.csv", user_probing_count)

print("--- Processing complete ---")
