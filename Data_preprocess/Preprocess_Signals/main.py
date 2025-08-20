import numpy as np
import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gives /home/rounak/.../Preprocess_Signals

def get_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)


def ensure_directories():
    base_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/"
    required_dirs = [
        "1_input_signals",
        "2_Normalized_data",
        "3_Normalized_window_data",
        "4_Alldata_window",
        "5_window_annotation",
        "6_signal_probe"
    ]
    for d in required_dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)


def signal_preprocessing (ids, video_id):
       for id in ids:
           print("user id:",id)
           ###EXTRACT VIDEOWISE PHYSIOLOGICAL SIGNALS###
           annotation = pd.read_csv("/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Annotations/user" +str(id)+ "_annotations.csv")
           PS = pd.read_csv("/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Physiological_signals/user" +str(id)+ "_physiological.csv")#,skiprows=1)

           column_names = ['time', 'GSR', 'HR', 'timestamp', 'time2' ]

           # Assign column names to the DataFrame
           PS.columns = column_names

           for v in video_id:
               index = annotation["videoID"] == v
               selected_video_array = annotation.loc[index]

               start_time = selected_video_array["time"].min()

               # Find the index of the selected row(s)
               selected_indices = selected_video_array.index
               first_selected_index = selected_indices.max()

               if first_selected_index + 1 in annotation.index:
                end_time = annotation.loc[first_selected_index + 1]['time']
               else:
                # Use the max time available in the current selection as the end time
                end_time = selected_video_array["time"].max() + 10000  # Add a buffer


               # Get the max index
            #    first_selected_index = selected_indices.max()

            #    # Get the next row using .loc[]
            #    next_row = annotation.loc[first_selected_index + 1]

            #    end_time = next_row['time']

                end_time = int(end_time)

               print("Start Time:", start_time)
               print("End Time:", end_time)

               PS = np.asanyarray(PS)
               length_data = (len(PS))


               new_data = []

               for i in range(length_data):

                   if ((start_time <= PS[i, 3]) & (end_time >= PS[i, 3]) ):
                       # print(PS[i, 2])
                       new_data.append(PS[i])

               #print(new_data)
               new_data = pd.DataFrame(new_data)
               new_data.rename(columns={0: 'Time_series'}, inplace=True)
               new_data.rename(columns={1: 'GSR'}, inplace=True)
               new_data.rename(columns={2: 'HR'}, inplace=True)
               new_data.rename(columns={3: 'timestamp'}, inplace=True)
               new_data.rename(columns={4: 'time2'}, inplace=True)
               new_data["subject"] = str(id)
               new_data["video_id"] = str(v)

            #    new_data.to_csv("1_input_signals/"+ str(id)+str(v)+ ".csv")
               new_data.to_csv(get_path(f"1_input_signals/{id}{v}.csv"))

import pandas as pd
import os


def signals_normalization(ids, video_id):
    p_id = 0
    for id in ids:
        combined_data = pd.DataFrame()
        p_id = p_id + 1

        for v in video_id:
            # Load and normalize signals
            signal_file = f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/1_input_signals/{id}{v}.csv"

            ds = pd.read_csv(signal_file)
            data = ds[["Time_series", "GSR", "HR", "timestamp", "subject", "video_id"]]
            data.loc[:, "video_id"] = v  # Use loc to set video_id
            combined_data = pd.concat([combined_data, data], ignore_index=True)
        print(combined_data.tail())
        print(combined_data.shape)
        print( combined_data[["GSR", "HR"]].max())
        print(combined_data[["GSR", "HR"]].min())
        # Normalize the data
        data_normalized = (combined_data[["GSR", "HR"]] - combined_data[["GSR", "HR"]].min()) / (
                combined_data[["GSR", "HR"]].max() - combined_data[["GSR", "HR"]].min()
        )

        # Add non-normalized columns back
        combined_data[["GSR", "HR"]] = data_normalized

        # print(combined_data)

        print(f"Processing ID {p_id}, ID {id}, Videos Processed: {len(video_id)}")

        # Create a dictionary for the normalized dataset
        dict_data = {
            "video_id": combined_data["video_id"],
            "timestamp": combined_data["timestamp"],
            "GSR": combined_data["GSR"],
            "HR": combined_data["HR"],
            "P_id": p_id,
        }

        # Convert to DataFrame and save as CSV
        dataset_normalized = pd.DataFrame(dict_data)
        output_dir = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/2_Normalized_data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{p_id}.normalized.csv")

        dataset_normalized.to_csv(output_file, index=False)
        print(f"Normalized data saved to {output_file}")



def extract_features(ids, video_id):
    debug_file = open("debug_extract_features.txt", "w")  # Log to file

    P_id = 0
    for id in ids:
        print(f"ID {id}", file=debug_file)
        P_id += 1

        # Load physiological signals
        PS = pd.read_csv(f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Physiological_signals/user{id}_physiological.csv", skiprows=1)
        PS.columns = ['time', 'GSR', 'HR', 'timestamp', 'time2']

        # Load annotations
        annotation = pd.read_csv(f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Annotations/user{id}_annotations.csv")

        # ✅ Baseline: First block of videoID == 0
        baseline_rows_all = annotation[annotation["videoID"] == 0]

        if baseline_rows_all.empty:
            print(f"⚠️ No baseline videoID == 0 found for user {id}", file=debug_file)
            GSR_meanblue, HR_meanblue = 0.5, 0.5
        else:
            first_baseline_index = baseline_rows_all.index[0]
            baseline_rows = baseline_rows_all.loc[first_baseline_index:]

            for idx in baseline_rows.index:
                if annotation.at[idx, "videoID"] != 0:
                    baseline_rows = annotation.loc[first_baseline_index:idx - 1]
                    break

            start_time = baseline_rows["time"].min()
            end_time = baseline_rows["time"].max()

            baseline_df = PS[(PS["timestamp"] >= start_time) & (PS["timestamp"] <= end_time)]

            if baseline_df.empty:
                print(f"⚠️ No signals in PS for baseline timestamps ({start_time} to {end_time})", file=debug_file)
                GSR_meanblue, HR_meanblue = 0.5, 0.5
            else:
                epsilon = 1e-8
                baseline_GSR = (baseline_df['GSR'] - baseline_df['GSR'].min()) / (
                    (baseline_df['GSR'].max() - baseline_df['GSR'].min()) + epsilon
                )
                baseline_HR = (baseline_df['HR'] - baseline_df['HR'].min()) / (
                    (baseline_df['HR'].max() - baseline_df['HR'].min()) + epsilon
                )
                GSR_meanblue = baseline_GSR.mean()
                HR_meanblue = baseline_HR.mean()
                print(f"✅ Using first videoID=0 baseline: GSR={GSR_meanblue:.4f}, HR={HR_meanblue:.4f}", file=debug_file)

        # 🧠 Process features for each video
        for v in video_id:
            temp_data = pd.read_csv(f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/2_Normalized_data/{P_id}.normalized.csv")
            temp_data["video_id"] = temp_data["video_id"].astype(int)
            original_data = temp_data[temp_data["video_id"] == v]
            data = original_data[['GSR', 'HR']].to_numpy()

            window_size = 50
            if len(data) < window_size:
                print(f"⚠️ Not enough data for windowing in user {id}, video {v}", file=debug_file)
                continue

            GSR_diff, HR_diff = [], []
            GSR_mean, HR_mean = [], []
            GSR_var, HR_var = [], []
            percentile_GSRvalue, percentile_HRvalue = [], []
            GSR_baseline_diff, HR_baseline_diff = [], []

            for i in range(0, len(data) - window_size + 1, window_size):
                x = data[i:i + window_size, :]
                percentile_75 = np.percentile(x, 75, axis=0)
                percentile_GSRvalue.append(percentile_75[0])
                percentile_HRvalue.append(percentile_75[1])

                xGSR_mean = x[:, 0].mean()
                xGSR_var = x[:, 0].var()
                xHR_mean = x[:, 1].mean()
                xHR_var = x[:, 1].var()

                GSR_mean.append(xGSR_mean)
                GSR_var.append(xGSR_var)
                HR_mean.append(xHR_mean)
                HR_var.append(xHR_var)

                GSR_diff.append(abs(GSR_meanblue - xGSR_mean))
                HR_diff.append(abs(HR_meanblue - xHR_mean))
                GSR_baseline_diff.append(abs(GSR_meanblue - xGSR_mean))
                HR_baseline_diff.append(abs(HR_meanblue - xHR_mean))

            # Debug: show values
            print(f"[DEBUG] len(GSR_diff): {len(GSR_diff)}", file=debug_file)
            print(f"[DEBUG] GSR_diff sample: {GSR_diff[:5]}", file=debug_file)

            new_window = pd.DataFrame({
                "GSR_mean": GSR_mean,
                "GSR_variance": GSR_var,
                "HR_mean": HR_mean,
                "HR_variance": HR_var,
                "75_percentile_GSR": percentile_GSRvalue,
                "75_percentile_HR": percentile_HRvalue,
                "GSRmean_persen_diff": pd.Series(GSR_baseline_diff).astype(float),
                "HRmean_persent_diff": pd.Series(HR_baseline_diff).astype(float),
                "GSRmean_diff": pd.Series(GSR_diff).astype(float),
                "HRmean_diff": pd.Series(HR_diff).astype(float),
            })

            # Add valence/arousal labels
            if v in [1, 2]:
                new_window["valence_acc_video"] = 1
                new_window["arousal_acc_video"] = 1
            elif v in [3, 4]:
                new_window["valence_acc_video"] = 0
                new_window["arousal_acc_video"] = 0
            elif v in [5, 6]:
                new_window["valence_acc_video"] = 1
                new_window["arousal_acc_video"] = 0
            elif v in [7, 8]:
                new_window["valence_acc_video"] = 0
                new_window["arousal_acc_video"] = 1

            new_window["P_id"] = P_id
            new_window["video_id"] = v

            save_path = f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/3_Normalized_window_data/{P_id}{v}_PS.csv"
            new_window.to_csv(save_path, index=False)
            print(f"✅ Saved features for User {id}, Video {v} → Rows: {len(new_window)}", file=debug_file)

    debug_file.close()



import pandas as pd
import os




def add_normalized_score(ids, video_id):
    debug_file = open("debug_extract_features.txt", "w")  # Log to file

    P_id = 0

    for id in ids:
        P_id += 1
        combined_data = pd.DataFrame()

        # Combine all scores for this user
        for v in video_id:
            score_file = f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/scores/{id}{v}_scores.csv"
            ds_scores = pd.read_csv(score_file)
            data_scores = ds_scores[["Score"]].copy()
            data_scores["video_id"] = v
            combined_data = pd.concat([combined_data, data_scores], ignore_index=True)

        # Normalize all scores together
        combined_data["Score"] = (combined_data["Score"] - combined_data["Score"].min()) / (
            combined_data["Score"].max() - combined_data["Score"].min()
        )

        # Now attach scores back to window files
        for v in video_id:
            window_data_file = f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/3_Normalized_window_data/{P_id}{v}_PS.csv"
            window_data = pd.read_csv(window_data_file)

            print(f"Processing ID {P_id}, User {id}, Video {v}",file=debug_file)
            score_data = combined_data[combined_data["video_id"] == v][["Score"]].reset_index(drop=True)

            # ✅ Directly merge without filtering out rows
            if len(score_data) != len(window_data):
                print(f"⚠️ Mismatch in rows: scores={len(score_data)}, window_data={len(window_data)}",file=debug_file)

            result = pd.concat([window_data.reset_index(drop=True), score_data], axis=1)

            output_dir = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/4_Alldata_window"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{P_id}{v}_final_concatfeatures.csv")
            result.to_csv(output_file, index=False)
            print(f"✅ Saved: {output_file}",file=debug_file)
    debug_file.close()
    



def annotate_window(ids, video_id):
    P_id = 0
    for id in ids:
        P_id = P_id + 1
        print("user id:", id)

        annotation = pd.read_csv("/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/raw_data/Annotations/user" + str(id) + "_annotations.csv")

        Max_val = annotation["valence"].max()
        Min_val = annotation["valence"].min()
        Median_val = annotation["valence"].median()

        Max_arou = annotation["arousal"].max()
        Min_arou = annotation["arousal"].min()
        Median_arou = annotation["arousal"].median()


        mid_val = (Max_val + Min_val)/ 2

        mid_arou = (Max_arou + Min_arou)/ 2

        # filter_val = mid_val
        # filter_arou = mid_arou

        filter_val = Median_val
        filter_arou = Median_arou


        # print("Min_aroul",Min_arou)
        # print("Max_arou", Max_arou)
        print("mid_val",mid_val)
        print("mid_arou", mid_arou)

        for v in video_id:
            print("video id:", v)
            # Initialize an empty DataFrame to store results
            window_means_df = pd.DataFrame()

            index = annotation["videoID"] == v
            selected_video_array = annotation.loc[index]

            # Max_val = selected_video_array["valence"].max()
            # Min_val = selected_video_array["valence"].min()
            #
            # Max_arou = selected_video_array["arousal"].max()
            # Min_arou = selected_video_array["arousal"].min()
            #
            #
            # mid_val = (Max_val + Min_val)/ 2
            #
            # mid_arou = (Max_arou + Min_arou)/ 2

            # print("Min_aroul",Min_arou)
            # print("Max_arou", Max_arou)
            # print("mid_val",mid_arou)


            start_time = selected_video_array["time"].min()

            # Find the index of the selected row(s)
            selected_indices = selected_video_array.index


            first_selected_index = selected_indices.max()

            if first_selected_index + 1 in annotation.index:
                end_time = annotation.loc[first_selected_index + 1]['time']
            else:
                # Use the max time available in the current selection as the end time
                end_time = selected_video_array["time"].max() + 10000  # Add a buffer

            # # Get the max index
            # first_selected_index = selected_indices.max()

            # # Get the next row using .loc[]
            # next_row = annotation.loc[first_selected_index + 1]

            # end_time = next_row['time']
            end_time = int(end_time)

            print("Start Time:", start_time)
            print("End Time:", end_time)

            # Loop through the time windows
            current_start_time = start_time
            while current_start_time + 5000 <= end_time:
                current_end_time = current_start_time + 5000

                # Select the rows within the current window
                window_data = selected_video_array[(selected_video_array['time'] >= current_start_time) &
                                                   (selected_video_array['time'] <= current_end_time)]

                print(f"Processing window: {current_start_time} to {current_end_time}")
                print(window_data)

                # Check if the window is empty
                if window_data.empty:
                    print(f"Window {current_start_time} to {current_end_time} is empty. Using previous window's mean.")

                    # If the first window is empty, we'll set the mean to NaN or 0s
                    if previous_window_mean is None:
                        # Create a dummy mean (NaN or 0s) for the first empty window
                        dummy_mean = pd.Series([float('nan')] * len(selected_video_array.columns),
                                               index=selected_video_array.columns)
                        dummy_mean['start_time'] = current_start_time
                        dummy_mean['end_time'] = current_end_time
                        previous_window_mean = dummy_mean

                    # Use the previous window's mean
                    window_mean = previous_window_mean
                else:
                    # Calculate the mean of the current window
                    window_mean = window_data.mean()
                    window_mean['start_time'] = current_start_time
                    window_mean['end_time'] = current_end_time

                    # Update the previous window mean
                    previous_window_mean = window_mean

                # Use pd.concat() instead of append() to add the window mean to the DataFrame
                window_means_df = pd.concat([window_means_df, pd.DataFrame([window_mean])], ignore_index=True)

                # Update the start time for the next window
                current_start_time += 5001

            # window_means_df.drop(window_means_df.columns[[4, 5, 6, 7]], axis=1, inplace=True)
            window_means_df['P_id'] = id

            # Add a new column 'probe' based on the condition that both valence and arousal <= 5
            window_means_df['probe'] = ((window_means_df['valence'] <= filter_val) & (window_means_df['arousal'] <= filter_arou)).astype(int)
            # window_means_df.drop(window_means_df.tail(1).index, inplace=True)

            # Display the final DataFrame with window means
            print(window_means_df)


            # Optionally, save the result to a CSV file
            window_means_df.to_csv("/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/5_window_annotation/"+str(P_id)+str(v)+"_annotation.csv", index=False)


def concat_all_data(P_id, video_id):
    for id in P_id:
        for v in video_id:
            # File paths for annotation and signal data
            print("id",id)
            print("Video", v)
            annotation_path = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/5_window_annotation/" + str(id) + str(v) + "_annotation.csv"
            signals_path = "4_Alldata_window/"+ str(id) + str(v)+"_final_concatfeatures.csv"

            # Load the data
            annotation = pd.read_csv(annotation_path)
            signals = pd.read_csv(signals_path)

            # Drop duplicate columns (like P_id, video_id) from annotation before concat
            annotation = annotation.loc[:, ~annotation.columns.isin(['P_id', 'video_id'])]

            # Concatenate the two dataframes side by side (axis=1)
            concatenated_data = pd.concat([signals, annotation], axis=1)

            # Print or save the concatenated data
            print(f"Concatenated data for user {id} and video {v}:")
            print(concatenated_data.head())  # Print first few rows for verification

            # Save the concatenated result (optional)
            concatenated_data.to_csv(f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/6_signal_probe/concatenated_data_{id}_{v}.csv", index=False)

    all_dataframes = []
    import os
    for id in P_id:
        for v in video_id:
            # Construct the filename for the current concatenated file
            file_path = f"/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/6_signal_probe/concatenated_data_{id}_{v}.csv"

            # Check if the file exists
            if os.path.exists(file_path):
                # Read the CSV file and append the dataframe to the list
                df = pd.read_csv(file_path)
                all_dataframes.append(df)
            else:
                print(f"File {file_path} not found.")

    # Concatenate all the dataframes in the list vertically (axis=0)
    combined_df = pd.concat(all_dataframes, axis=0, ignore_index=True)

    # Save the final combined dataframe to a single CSV file
    combined_df.to_csv("42_user_wise_normalized_features.csv", index=False)

    # Print a message after saving the file
    print("All files have been concatenated and saved into '42_mid__userwise_valarou_data.csv'.")


def add_prevwindow(P_id, video_id):
        all_users_data = []
        ds = pd.read_csv('42_user_wise_normalized_features.csv')

        for s in P_id:
            for v in video_id:
                # Filter the dataset for the current P_id and video_id
                a = (ds['P_id'] == s) & (ds['video_id'] == v)
                selected_user = ds.loc[a].copy()

                # Get the probe column values
                probe_values = selected_user['probe'].tolist()

                # Initialize the prev_window column
                prev_window = [1]  # First row is by default 1
                for i in range(1, len(probe_values)):
                    prev_window.append(probe_values[i - 1])

                # Add the prev_window column to the filtered data
                selected_user['prev_window'] = prev_window

                # Append the modified data to the list
                all_users_data.append(selected_user)

        # Concatenate all user data back into a single DataFrame
        all_users_df = pd.concat(all_users_data, ignore_index=True)

        all_users_df.to_csv('/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/alluser_normalized_allfeatures_.csv', index=False)


if __name__ == "__main__":

    ensure_directories()
    # ids = list(range(1,37)) + list(range(55,61))
    ids = list(range(1,41))
    P_id = list(range(1,41))
    # P_id = list(range(1,43))
    video_id = list(range(1,9))

    # signal_preprocessing (ids, video_id)
    # signals_normalization(ids, video_id)
    # extract_features(ids, video_id)
    # add_normalized_score(ids,video_id)
    # annotate_window (ids, video_id)
    # concat_all_data(P_id, video_id)
    add_prevwindow(P_id, video_id)





