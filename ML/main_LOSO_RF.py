import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
import csv
import statistics
import os

folder_path='/home/rounak/CODE/Low_Engagement_Detection/ML/LOSO_RF'
os.makedirs(folder_path, exist_ok=True)  # Ensure the folder is created


# Load dataset
data = pd.read_csv('/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table/merged_all_1_to_40.csv')
# video_df= pd.read_csv('/home/rounak/CODE/Third_quadrant_prediction orgnl/pd_ML/video_id.csv')
cols_to_drop = ["videoID","start_time","end_time","start_time_sec","end_time_sec","num_samples","start_time_ms","end_time_ms","time", "prev_window"]

ds = data.drop(columns=cols_to_drop)



# Define clusters
cluster = list(range(1, 41))
    
threshold = 0.5
ds_cluster = ds[ds["P_id"].isin(cluster)].copy()

X = ds_cluster.drop(['probe'], axis=1)
y = ds_cluster['probe']

subject_id = np.unique(ds_cluster.P_id)


# drop_user=[10,13,23,26,33]
for s in subject_id:
    # if s in drop_user:
    #     continue
    fn ,tp,fp,tn, tpr ,fpr,f1_macro, f1_weighted=0,0,0,0,0,0,0,0
    test_index = X["P_id"] == s
    train_index = X["P_id"] != s
    
    X_train = X.loc[train_index].drop(['P_id'], axis=1)
    # X_train= X.loc[train_index].drop(['prev_window2'], axis=1)
    X_test = X.loc[test_index].drop(['P_id'], axis=1)
    y_train = y[train_index]
    y_test = y[test_index]
    
    # # -----------Original--------------
    # model = XGBClassifier(
    #     objective='binary:logistic', max_depth=10, n_estimators=100,
    #     learning_rate=0.1, scale_pos_weight=1.5, random_state=42
    # )
    # ----------Random Forest Classifier----------------
    model = RandomForestClassifier(
        n_estimators=100,        # number of trees
        max_depth=10,            # tree depth (same as XGB)
        class_weight='balanced', # adjust for 30-70 imbalance
        random_state=42,
        n_jobs=-1                # use all cores for speed
    )
        
    model.fit(X_train, y_train)
    
    ##--------------------------------------------------------------------------------------------------------
    # y_probs = (model.predict_proba(X_test)[:, 1] > 0.20).astype(int)
    # print("yprobs type",type(y_probs))       
    # View X_test and y_probs
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', 1000)  # Prevent truncation
    # -------------------------------------------------------------------------------------------------
    
    

    y_probs = (model.predict_proba(X_test)[:, 1] > threshold).astype(int)

    
    print("shape of the df:",X_test.shape)

    with open(os.path.join(folder_path, f"y_test_vs_y_pred_comparison_{threshold}.csv"), "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for true_val, pred_val in zip(y_test, y_probs):
            writer.writerow([s, true_val, pred_val])


    
    print("------------------------------------------------------------------")
    # print("X_test:")
    # print(X_test.head())  # Show first few rows
    print("y_probs:")
    print("yprob_shape",y_probs.shape,"ytest shape", y_test.shape)
    print(pd.DataFrame(y_probs, columns=['y_probs']).head())
    
    fp = np.sum((y_probs == 1) & (y_test == 0))
    tp = np.sum((y_probs == 1) & (y_test == 1))
    fn = np.sum((y_probs == 0) & (y_test == 1))
    tn = np.sum((y_probs == 0) & (y_test == 0))
    
    tpr = tp / (tp + fn)
    fpr = fp / (fp + tn)
    f1_macro = f1_score(y_test, y_probs, average='macro')
    f1_weighted = f1_score(y_test, y_probs, average='weighted')
    accuracy = accuracy_score(y_test, y_probs)

    
    print(f"Subject {s}: TPR={tpr}, FPR={fpr}, F1_macro={f1_macro}, F1_weighted={f1_weighted},Accuracy={accuracy}")
    
    with open(os.path.join(folder_path, f"TPR_FPR_F1_Accuracy_{threshold}.csv"), "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([s, tpr, fpr, f1_macro, f1_weighted,accuracy])

print("Processing complete")
