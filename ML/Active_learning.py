import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import time  # Import time module
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
import csv
import statistics
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Prevent truncation

# Load dataset
data = pd.read_csv('/home/rounak/CODE/Third_quadrant_prediction orgnl/pd_ML/MetaData_2.0.csv')
# video_df= pd.read_csv('/home/rounak/CODE/Third_quadrant_prediction orgnl/pd_ML/video_flag.csv')
ds = data[['Score', 'GSRmean_persen_diff', 'HRmean_persen_diff', 'valence_acc_video',
           'arousal_acc_video', 'P_id','video_id','video_flag','label','prev_window2']]

# Define different variations of training splits
active_splits = [
    [2],        # Active on 2 → Test on 3,4,5,6,7
    [2, 3],     # Active on 2,3 → Test on 4,5,6,7
    [2, 3, 4],  # Active on 2,3,4 → Test on 5,6,7
    [2, 3, 4, 5],  # Active on 2,3,4,5 → Test on 6,7
    [2, 3, 4, 5, 6],  # Active on 2,3,4,5,6 → Test on 7
    [2, 3, 4, 5, 6, 7]
]

# Loop through different variations of training set splits
for active_videos in active_splits:
    print(f"\nProcessing active split: {active_videos}")

    # Testing videos = remaining from {2,3,4,5,6,7,8}
    test_videos = [v for v in [2, 3, 4, 5, 6, 7, 8] if v not in active_videos]

    print(f"Testing videos: {test_videos}")


    # Create folder name dynamically
    folder_name = f"{','.join(map(str, active_videos))}-{','.join(map(str, test_videos))}"
    folder_path = os.path.join("Re_eval_Al_test_split_median", folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Ensure the folder is created

    # Initialize dictionaries to store user-wise scores for all thresholds
    user_tpr = {}
    user_fpr = {}
    user_f1_macro = {}
    user_f1_weighted = {}
    user_probing_count = {}






    # Define clusters
    cluster = list(range(1, 43))
        
    threshold = 0.1
    ds_cluster = ds[ds["P_id"].isin(cluster)].copy()
    df=ds_cluster
    
   
    # ---------------------- Data Splitting Based on Video Flags ----------------------
    # Merge to get video_flag from video_df into ds_cluster
    
    new_df = ds_cluster

    # Baseline Training Data → Flag 1
    df_base = new_df[new_df["video_flag"].isin([1])]

    # Active Learning Data → Flag 3, 4, 5, 6
    df_active = new_df[new_df["video_flag"].isin(active_videos)]
    

    # Final Testing Data → Flag 7, 8
    df_test = new_df[new_df["video_flag"].isin(test_videos)]

    # Find overlapping video IDs between df_active and df_test
    overlapping_videos = set(df_active['video_id']).intersection(set(df_test['video_id']))

    if overlapping_videos:
        print(f"⚠ Warning: Overlapping video IDs found between df_active and df_test: {overlapping_videos}")
    else:
        print("✅ No overlapping video IDs found. The split is clean.")

    



    print(f"Baseline Data Size: {len(df_base)}")
    print(f"Active Learning Data Size: {len(df_active)}")
    print(f"Final Testing Data Size: {len(df_test)}")


    


    # --------- i think we dont need to reset the indices but dont know lets see------

    X_base = df_base.drop(['label', 'P_id', 'video_id','video_flag'], axis=1)
    y_base = df_base['label']


    X_testing = df_test.drop(['label','video_id',"video_flag"], axis=1)
    y_testing = df_test['label']

    # ------------------------------------------------------------------------------------------------------------
    # -----------------------------Defining model----------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------
    # -----------Original--------------
    model = XGBClassifier(
        objective='binary:logistic', max_depth=10, n_estimators=100,
        learning_rate=0.1, scale_pos_weight=1.5, random_state=42
    )
    # hyperparameter optimization

    # model = XGBClassifier(
    #     objective='binary:logistic', max_depth=5, n_estimators=300,
    #     learning_rate=0.05, scale_pos_weight=1.5, random_state=42
    # )

    #----------------------------------------------------------------------------------------------------------
    # -----------------------------training base line Model----------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------
    # Training model
    print("..................Training Baseline model.................")
    model.fit(X_base, y_base)
    print("Baseline Model training complete.")

    #making a copy of the baseline training set for gradual improvement of training set
    new_X_train = X_base.copy()
    new_y_train = y_base.copy()

    #----------------------------------------------------------------------------------------------------------
    # User wiswe Active Learning
    #----------------------------------------------------------------------------------------------------------
    subject_id = np.unique(ds_cluster.P_id)

    for s in subject_id: # For user wise iteration Active

        # video_probe_counts={}

        # Identify the 4 videos assigned to this user
        user_videos = df_active[df_active["P_id"] == s]["video_id"].unique()

        # Reset probe counts for this user (initialize dynamically based on user-specific videos)
        video_probe_counts = {video_id: 0 for video_id in user_videos}


        fn ,tp,fp,tn, tpr ,fpr,f1_macro, f1_weighted=0,0,0,0,0,0,0,0

        
        # video_counts = {3: 0, 4: 0, 5: 0, 6: 0}

        probing_count=0
        print("Entering Active Learning Phase For user:",s)
        X=df_active.drop(['label','video_flag'], axis=1)
        y=df_active['label']
        active_test_index = df_active["P_id"] == s
    
        active_X_test = X.loc[active_test_index].drop(['P_id'], axis=1)
        active_y_test = y[active_test_index]

        
        # ------------------------------------------------------------------------------------------
        #-----------------Final(20%) Data set prep--------------------------------------------------
        # ------------------------------------------------------------------------------------------
        X_final=df_test.drop(['label','video_id','video_flag'], axis=1)
        y_final=df_test['label']
        final_test_index = df_test["P_id"] == s


        final_X_test=X_final.loc[final_test_index].drop(['P_id'], axis=1)
        final_y_test=y_final[final_test_index]
        # -------------------------------------------------------------------------------------------
        
        # Create an empty DataFrame
        # Initialize y_probs with an initial value of 1
        y_probs = np.array([])
        ypred=np.array([1])
        # ----------------------------------------------------------------------------------------
        
        print(f"Prediction threshold set to: {threshold}")
        # ------------------------------------------------------------------------------------------
        # print("X_test row wise")
        for i in range(0,active_X_test.shape[0]):
            print(f"--- Predicting row {i}/{active_X_test.shape[0]} for User {s} ---")

            # Get the video_id of the current sample
            current_video_id = active_X_test.iloc[i]['video_id']

            test_row=active_X_test.iloc[[i]].copy()  # Double brackets keep it as a DataFrame
            y_test_cur= active_y_test.iloc[[i]]
                    
            test_row['prev_window2'] = ypred.item()  # Extracts scalar value from NumPy array

            # Drop video_id before making predictions (since it's not a feature)
            test_row = test_row.drop(columns=['video_id'])

            
            #---------------------------------------------------------------------------------
            #                   Checking model.predict_proba
            #----------------------------------------------------------------------------------
            
            ypred_prob=(model.predict_proba(test_row)[:, 1])
            
            # Active Learning Implementation

            if ypred_prob < threshold:
                print("Active learning triggered: Adding current sample to training set.")
                probing_count+=1

                # Update probe count for this video_id
                if current_video_id in video_probe_counts:
                    video_probe_counts[current_video_id] += 1
                else:
                    video_probe_counts[current_video_id] = 1
                
                # if int(current_video_id) in video_counts:
                #     video_counts[int(current_video_id)] += 1
                                
                # Add user-labeled data to training set
                new_X_train = pd.concat([new_X_train, test_row], axis=0)
                new_y_train = pd.concat([new_y_train, y_test_cur], axis=0)
                continue                       
            else:
                ypred=(ypred_prob >= threshold).astype(int)
    
        
        print("**********************************************")
        print("Retraining model with updated data...")
        # Start time tracking for this user
        start_time = time.time()

        model.fit(new_X_train, new_y_train)

        # Stop the timer after active learning for this user
        end_time = time.time()
        time_taken = end_time - start_time  # Calculate time duration

        print("Model retrained.")


        for i in range(0,final_X_test.shape[0]):
            test_row=final_X_test.iloc[[i]].copy()  # Double brackets keep it as a DataFrame
            y_test_cur= final_y_test.iloc[i]
                
            # ypred.item()  # Extracts scalar value from NumPy array

            # Avoid modifying the original X_test
            test_row.loc[:, 'prev_window2'] = ypred.item()  # Correctly assign previous window value
            
            ypred=(model.predict_proba(test_row)[:, 1] > threshold).astype(int)
            
            y_probs = np.append(y_probs, ypred)
            # y_probs=(model.predict_proba(final_X_test)[:, 1] >= threshold).astype(int)
        print(f"Updated prediction after active learning")
        
        print(f"--- Prediction complete for User {s} ---")

        # Store per-user probe count and prediction comparisons (keep existing logic)
        with open(os.path.join(folder_path, f'AL_Video_split_Probe_Counts_{threshold}.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for video_id, count in video_probe_counts.items():
                writer.writerow([s, video_id, count, time_taken])

        with open(os.path.join(folder_path, f'AL_y_test_vs_y_pred_comparison{threshold}.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for true_val, pred_val in zip(final_y_test, y_probs):
                writer.writerow([s, true_val, pred_val])        



        # with open(f'gradual_reorder/AL_Video_split_Probe_Counts_{threshold}.csv', 'a', newline='') as csvfile:
        #             writer = csv.writer(csvfile)            
        #             for video_id, count in video_probe_counts.items():  
        #                 writer.writerow([s, video_id, count,time_taken])
        
        # with open(f'gradual_reorder/AL_Video_split_Probe_Counts_{threshold}.csv', 'a', newline='') as csvfile:
        #         writer = csv.writer(csvfile)
        #         for true_val, pred_val in zip(final_y_test, y_probs):
        #             writer.writerow([s, true_val, pred_val])
        # print("Calculating performance metrics...")

        # with open(f'Probing_Count_comparison_{threshold}.csv', 'a', newline='') as csvfile:
        #         writer = csv.writer(csvfile)
        #         writer.writerow([s, probing_count])
        # print("Calculating performance metrics...")
        
        
        tp = np.sum((y_probs == 1) & (final_y_test == 1))
        fn = np.sum((y_probs == 0) & (final_y_test == 1))
        fp = np.sum((y_probs == 1) & (final_y_test == 0))
        tn = np.sum((y_probs == 0) & (final_y_test == 0))
        
        tpr = tp / (tp + fn)
        fpr = fp / (fp + tn)
        f1_macro = f1_score(final_y_test, y_probs, average='macro')
        f1_weighted = f1_score(final_y_test, y_probs, average='weighted')
        print(f"Performance for User {s}:")
        print(f"Subject {s}: TPR={tpr}, FPR={fpr}, F1_macro={f1_macro}, F1_weighted={f1_weighted}")
        
        user_tpr.setdefault(s, []).append(tpr)
        user_fpr.setdefault(s, []).append(fpr)
        user_f1_macro.setdefault(s, []).append(f1_macro)
        user_f1_weighted.setdefault(s, []).append(f1_weighted)
        user_probing_count.setdefault(s, []).append(probing_count)


        # with open(f'gradual_reorder/Video_split_AL_UserWise_Scores{threshold}.csv', 'a', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow([s, tpr, fpr, f1_macro, f1_weighted,probing_count])
        # Write aggregated user-wise scores to CSV after processing all thresholds


    def write_user_scores_to_csv(file_name, data_dict):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            thresholds = [f"Threshold_{i*0.1}" for i in range(1, 10)]
            writer.writerow(["User"] + thresholds)  # Header row
            for user, scores in data_dict.items():
                writer.writerow([user] + scores)
    # Generate all 5 summary CSVs
    write_user_scores_to_csv("User_TPR.csv", user_tpr)
    write_user_scores_to_csv("User_FPR.csv", user_fpr)
    write_user_scores_to_csv("User_F1_Macro.csv", user_f1_macro)
    write_user_scores_to_csv("User_F1_Weighted.csv", user_f1_weighted)
    write_user_scores_to_csv("User_Probing_Count.csv", user_probing_count)



print(f"--- Processing complete for Splits ---\n")
