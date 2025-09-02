import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
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
data = pd.read_csv('/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Final_Data_Table/merged_all_1_to_40.csv')
# video_df= pd.read_csv('/home/rounak/CODE/Third_quadrant_prediction orgnl/pd_ML/video_id.csv')
cols_to_drop = ["videoID","start_time","end_time","start_time_sec","end_time_sec","num_samples","start_time_ms","end_time_ms","time", "prev_window"]

ds = data.drop(columns=cols_to_drop)

# Define clusters
cluster = list(range(1, 41))

# Initialize dictionaries to store user-wise scores for all thresholds
user_tpr = {}
user_fpr = {}
user_f1_macro = {}
user_f1_weighted = {}
user_accuracy = {}
    
for threshold_count in range(1,10):

    threshold = threshold_count*0.1
    ds_cluster = ds[ds["P_id"].isin(cluster)].copy()
    df=ds_cluster
    # Initialize empty DataFrames to store the results
    df_first_80 = pd.DataFrame()
    df_last_20 = pd.DataFrame()

   
    folder_path='/home/rounak/CODE/Low_Engagement_Detection/ML/Personalised'
    os.makedirs(folder_path, exist_ok=True)  # Ensure the folder is created


    
    

    # ---------------------- Data Splitting Based on Video Flags ----------------------
    # Merge to get video_id from video_df into ds_cluster
        
    new_df = ds_cluster
    # Baseline Training Data → Flag 1, 2,3,4,5,6
    df_base = new_df[new_df["video_id"].isin([1, 2,3,4,5,6])]

    # Final Testing Data → Flag 7, 8
    df_test = new_df[new_df["video_id"].isin([7, 8])]

    df_first_80 = df_base
    df_last_20 = df_test

    '''
    # Iterate over each unique user in P_id
    for user_id, user_data in df.groupby('P_id'):
        # Get the number of rows for this user
        total_rows = len(user_data)
        
        # Calculate the indices for splitting
        first_80_end = int(total_rows * 0.8)

        # Split the data for this user
        user_first_80 = user_data.iloc[:first_80_end]
        user_last_20 = user_data.iloc[first_80_end:]
        
        # Append to the respective DataFrames
        df_first_80 = pd.concat([df_first_80, user_first_80])
        df_last_20 = pd.concat([df_last_20, user_last_20])
    '''
    # --------- i think we dont need to reset the indices but dont know lets see------

    # # Reset indices to keep things clean
    # df_first_40.reset_index(drop=True, inplace=True)
    # df_next_40.reset_index(drop=True, inplace=True)
    # df_last_20.reset_index(drop=True, inplace=True)
    # Optional: Print the sizes to verify no data loss
    print(f"Original DataFrame size: {len(df)}")
    print(f"First 80% DataFrame size: {len(df_first_80)}")
    print(f"Last 20% DataFrame size: {len(df_last_20)}")
    print(f"Total after split: {len(df_first_80) + len(df_last_20)}")


    X_train = df_first_80.drop(['probe','video_id'], axis=1)
    y_train = df_first_80['probe']


    X_testing = df_last_20.drop(['probe','video_id'], axis=1)
    y_testing = df_last_20['probe']

    # ------------------------------------------------------------------------------------------------------------
    # -----------------------------Defining model----------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------
    # -----------Original--------------
    model = XGBClassifier(
        objective='binary:logistic', max_depth=10, n_estimators=100,
        learning_rate=0.1, scale_pos_weight=1.5, random_state=42
    )
    # hyperparameter optimization

    
    subject_id = np.unique(ds_cluster.P_id)
    # drop_user=[10,13,23,26,33]
    for s in subject_id:
        # if s in drop_user:
        #     continue
        print("Entering Personalised Learning Phase For user:",s)
        X=X_train
        y=y_train
        active_test_index = X_train["P_id"] == s
    
        personal_X_train = X.loc[active_test_index].drop(['P_id'], axis=1)
        personal_y_train = y[active_test_index]

        # Training model
        print("..................Training model.................")
        model.fit(personal_X_train, personal_y_train)
        print("Model training complete for user",s)    
        # ------------------------------------------------------------------------------------------
        #-----------------Final(20%) Data set prep--------------------------------------------------
        # ------------------------------------------------------------------------------------------
        X_final=X_testing
        y_final=y_testing
        final_test_index = df_last_20["P_id"] == s


        final_X_test=X_final.loc[final_test_index].drop(['P_id'], axis=1)
        final_y_test=y_final[final_test_index]
    # -------------------------------------------------------------------------------------------
        
        # Create an empty DataFrame
        # Initialize y_probs with an initial value of 1
        # y_probs = np.array([])
        # ypred=np.array([1])
        # ----------------------------------------------------------------------------------------
             
                
        print(f"Prediction threshold set to: {threshold}")            

        # Vectorized prediction
        y_probs = (model.predict_proba(final_X_test)[:, 1] >= threshold).astype(int)
      
               
        # ------------------------------------------------------------------------------------------
        # print("X_test row wise")
        # for i in range(0,final_X_test.shape[0]):
        #     print(f"--- Predicting row {i}/{final_X_test.shape[0]} for User {s} ---")
        #     test_row=final_X_test.iloc[[i]]  # Double brackets keep it as a DataFrame
        #     y_test_cur= final_y_test.iloc[[i]]
                    
        #     test_row['prev_window2'] = ypred.item()  # Extracts scalar value from NumPy array


            
        #     #---------------------------------------------------------------------------------
        #     #                   Checking model.predict_proba
        #     #----------------------------------------------------------------------------------
            
        #     ypred=(model.predict_proba(test_row)[:, 1] >= threshold).astype(int)
        #     # print("ypred_post_predict",ypred)
        #     y_probs = np.append(y_probs, ypred)
        #     # print("y_prob_type: ",type(y_probs))
        #     # print(pd.DataFrame(y_probs, columns=['y_probs']))
        #     print("--------------------------------------------------------------------------")
        #     with open(f'Personalised/=personalised_test_pred_comparison_.csv', 'a', newline='') as csvfile:
        #         writer = csv.writer(csvfile)
        #         writer.writerow([s,threshold, y_test_cur.iloc[0], ypred])
    
        
        # Save predictions (append mode)
        with open(os.path.join(folder_path, 'Personalised_test_pred_comparison.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for true_val, pred_val in zip(final_y_test, y_probs):
                writer.writerow([s, threshold, true_val, pred_val])
        
        print(f"--- Prediction complete for User {s} ---")
        
        # with open(f'Active__Learning_y_test_vs_y_pred_comparison{threshold}.csv', 'a', newline='') as csvfile:
        #         writer = csv.writer(csvfile)
        #         for true_val, pred_val in zip(final_y_test, y_probs):
        #             writer.writerow([s, true_val, pred_val])
        # print("Calculating performance metrics...")

        
        tp = np.sum((y_probs == 1) & (final_y_test == 1))
        fn = np.sum((y_probs == 0) & (final_y_test == 1))
        fp = np.sum((y_probs == 1) & (final_y_test == 0))
        tn = np.sum((y_probs == 0) & (final_y_test == 0))
        
        tpr = tp / (tp + fn)
        fpr = fp / (fp + tn)
        f1_macro = f1_score(final_y_test, y_probs, average='macro')
        f1_weighted = f1_score(final_y_test, y_probs, average='weighted')
        accuracy = accuracy_score(final_y_test, y_probs)

        print(f"Performance for User {s}:")
        print(f"Subject {s}: TPR={tpr}, FPR={fpr}, F1_macro={f1_macro}, F1_weighted={f1_weighted},Accuracy={accuracy}")
        user_tpr.setdefault(s, []).append(tpr)
        user_fpr.setdefault(s, []).append(fpr)
        user_f1_macro.setdefault(s, []).append(f1_macro)
        user_f1_weighted.setdefault(s, []).append(f1_weighted)
        user_accuracy.setdefault(s, []).append(accuracy)

        
        # with open(f'Personalised/Personalised_UserWise_Scores{threshold}.csv', 'a', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow([s, tpr, fpr, f1_macro, f1_weighted])



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
    write_user_scores_to_csv("user_accuracy.csv", user_accuracy)

    # write_user_scores_to_csv("User_Probing_Count.csv", user_probing_count)



print(f"--- Processing complete for All Users ---\n")
