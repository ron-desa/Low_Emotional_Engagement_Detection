import numpy as np
import pandas as pd

def signal_preprocessing (ids, video_id):
       for id in ids:
           print("user id:",id)
           ###EXTRACT VIDEOWISE PHYSIOLOGICAL SIGNALS###
           annotation = pd.read_csv("raw_data/Annotations/user" +str(id)+ "_annotations.csv")
           PS = pd.read_csv("raw_data/Physiological_signals/user" +str(id)+ "_physiological.csv")

           column_names = ['time', 'GSR', 'HR', 'timestamp', 'time2' ]

           # Assign column names to the DataFrame
           PS.columns = column_names

           for v in video_id:
               index = annotation["videoID"] == v
               selected_video_array = annotation.loc[index]

               start_time = selected_video_array["time"].min()

               # Find the index of the selected row(s)
               selected_indices = selected_video_array.index

               # Get the max index
               first_selected_index = selected_indices.max()

               # Get the next row using .loc[]
               next_row = annotation.loc[first_selected_index + 1]

               end_time = next_row['time']
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

               new_data.to_csv("1_input_signals/"+ str(id)+str(v)+ ".csv")


import pandas as pd
import os


def signals_normalization(ids, video_id):
    p_id = 0
    for id in ids:
        combined_data = pd.DataFrame()
        p_id = p_id + 1

        for v in video_id:
            # Load and normalize signals
            signal_file = f"1_input_signals/{id}{v}.csv"

            ds = pd.read_csv(signal_file)
            data = ds[["Time_series", "GSR", "HR", "timestamp", "subject", "video_id"]]
            data.loc[:, "video_id"] = v  # Use loc to set video_id
            combined_data = pd.concat([combined_data, data], ignore_index=True)

        # print(combined_data.shape)
        # print( combined_data[["GSR", "HR"]].max())
        # print(combined_data[["GSR", "HR"]].min())
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
        output_dir = "2_Normalized_data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{p_id}.normalized.csv")

        dataset_normalized.to_csv(output_file, index=False)
        print(f"Normalized data saved to {output_file}")


def extract_features(ids, video_id):
        P_id = 0
        for id in ids:
               print("ID",id)
               P_id  = P_id + 1
               PS = pd.read_csv(f"raw_data/Physiological_signals/user{id}_physiological.csv")

               # Rename columns
               column_names = ['time', 'GSR', 'HR', 'timestamp', 'time2']
               PS.columns = column_names

               # Select a specific range of rows
               selected_rows2 = PS.iloc[600:651]

               # Normalize GSR and HR columns
               selected_rows_GSR = (selected_rows2['GSR'] - selected_rows2['GSR'].min()) / (
                           selected_rows2['GSR'].max() - selected_rows2['GSR'].min())
               selected_rows_HR = (selected_rows2['HR'] - selected_rows2['HR'].min()) / (
                           selected_rows2['HR'].max() - selected_rows2['HR'].min())



               # Calculate mean values
               GSR_meanblue = selected_rows_GSR.mean()
               HR_meanblue = selected_rows_HR.mean()


               for v in video_id:
                       temp_data = pd.read_csv("2_Normalized_data/" + str(P_id) + ".normalized.csv")
                       index = temp_data["video_id"] == v
                       original_data = temp_data[index]
                       data = original_data[['GSR', 'HR']]
                       data = np.asanyarray(data)
                       window_size = 50
                       GSR_diff = []
                       HR_diff = []
                       GSR_mean =[]
                       HR_mean = []
                       GSR_var = []
                       HR_var = []
                       percentile_GSRvalue = []
                       percentile_HRvalue = []
                       GSR_baseline_diff = []
                       HR_baseline_diff = []
                       GSR_test = []
                       HR_test = []
                       print(range(0,len(data)))
                       for i in range(0, len(data) - window_size, window_size):

                               x = data[i:i + window_size, :]

                               percentile_75 = np.percentile(x, 75, axis=0)
                               percentile_GSRvalue.append(percentile_75[0])
                               percentile_HRvalue.append(percentile_75[1])

                               xGSR_mean = x[:, 0].mean()
                               GSR_mean.append(xGSR_mean)
                               xGSR_var = x[:, 0].var()
                               GSR_var.append(xGSR_var)
                               xHR_mean = x[:, 1].mean()
                               HR_mean.append(xHR_mean)
                               xHR_var = x[:, 1].var()
                               HR_var.append(xHR_var)

                               a = abs(GSR_meanblue - xGSR_mean)
                               GSR_diff.append(a)

                               b = abs(HR_meanblue - xHR_mean)
                               HR_diff.append(b)

                               e = abs(GSR_meanblue - xGSR_mean)
                               # print(i)
                               # print(f"GSR_mean: {xGSR_mean}, GSR_bluew: {GSR_meanblue}")
                               # print(e)
                               GSR_baseline_diff.append(e)

                               f = abs(HR_meanblue - xHR_mean)
                               HR_baseline_diff.append(f)


                       new_window = pd.DataFrame()
                       new_window["GSR_mean"] = GSR_mean
                       new_window["GSR_variance"] = GSR_var
                       new_window["HR_mean"] = HR_mean
                       new_window["HR_variance"] = HR_var
                       new_window["75_percentile_GSR"] = percentile_GSRvalue
                       new_window["75_percentile_HR"] = percentile_HRvalue
                       new_window["GSRmean_persen_diff"] = GSR_baseline_diff
                       new_window["HRmean_persent_diff"] = HR_baseline_diff
                       new_window["GSRmean_diff"] = GSR_diff
                       new_window["HRmean_diff"] = HR_diff

                       if(v == 1):
                           new_window["valence_acc_video"] = 1
                           new_window["arousal_acc_video"] = 1
                       elif(v == 2):
                           new_window["valence_acc_video"] = 1
                           new_window["arousal_acc_video"] = 1
                       elif(v == 3):
                           new_window["valence_acc_video"] = 0
                           new_window["arousal_acc_video"] = 0
                       elif(v == 4):
                           new_window["valence_acc_video"] = 0
                           new_window["arousal_acc_video"] = 0
                       elif(v == 5):
                           new_window["valence_acc_video"] = 1
                           new_window["arousal_acc_video"] = 0
                       elif(v == 6):
                           new_window["valence_acc_video"] = 1
                           new_window["arousal_acc_video"] = 0
                       elif(v == 7):
                           new_window["valence_acc_video"] = 0
                           new_window["arousal_acc_video"] = 1
                       elif(v == 8):
                           new_window["valence_acc_video"] = 0
                           new_window["arousal_acc_video"] = 1

                       new_window["P_id"] = P_id
                       new_window["video_id"] = v

                       new_window.to_csv("3_Normalized_window_data/"+str(P_id)+str(v)+"_PS.csv")


import pandas as pd
import os


def add_normalized_score(ids, video_id):
    P_id = 0

    for id in ids:
        P_id += 1
        combined_data = pd.DataFrame()

        # Combine scores for all videos of the current user
        for v in video_id:
            # Load and normalize change point scores
            score_file = f"scores/{id}{v}_scores.csv"


            ds_scores = pd.read_csv(score_file)
            data_scores = ds_scores[["Score"]].copy()
            data_scores["video_id"] = v

            # print(ds_scores[["Score"]].min())

            combined_data = pd.concat([combined_data, data_scores], ignore_index=True)

        # print(combined_data["Score"].min())
        # print(combined_data["Score"].max())

        # Normalize the combined scores
        combined_data["Score"] = (combined_data["Score"] - combined_data["Score"].min()) / (
                combined_data["Score"].max() - combined_data["Score"].min()
        )

        # print(combined_data)

        # Process each video for the current user
        for v in video_id:

            # Load the window data
            window_data_file = f"3_Normalized_window_data/{P_id}{v}_PS.csv"
            window_data = pd.read_csv(window_data_file)

            print(f"Processing ID {P_id}, ID {id}, Videos Processed: {v}")

            # Filter data for the current video
            original_data = window_data[window_data["video_id"] == v].copy()
            score_data = combined_data[combined_data["video_id"] == v][["Score"]].reset_index(drop=True)

            # Concatenate original window data and normalized scores
            result = pd.concat([original_data.reset_index(drop=True), score_data], axis=1)

            # Save the concatenated results
            output_dir = "4_Alldata_window"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{P_id}{v}_final_concatfeatures.csv")
            result.to_csv(output_file, index=False)

            print(f"Saved concatenated data to {output_file}")


def annotate_window(ids, video_id):
    P_id = 1
    for id in ids:
        P_id = P_id + 1
        print("user id:", id)

        annotation = pd.read_csv("raw_data/Annotations/user" + str(id) + "_annotations.csv")

        Max_val = annotation["valence"].max()
        Min_val = annotation["valence"].min()
        Median_val = annotation["valence"].median()

        Max_arou = annotation["arousal"].max()
        Min_arou = annotation["arousal"].min()
        Median_arou = annotation["arousal"].median()


        mid_val = (Max_val + Min_val)/ 2

        mid_arou = (Max_arou + Min_arou)/ 2

        filter_val = mid_val
        filter_arou = mid_arou

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

            # Get the max index
            first_selected_index = selected_indices.max()

            # Get the next row using .loc[]
            next_row = annotation.loc[first_selected_index + 1]

            end_time = next_row['time']
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
            window_means_df.to_csv("5_window_annotation/"+str(P_id)+str(v)+"_annotation.csv", index=False)


def concat_all_data(P_id, video_id):
    for id in P_id:
        for v in video_id:
            # File paths for annotation and signal data
            print("id",id)
            print("Video", v)
            annotation_path = "5_window_annotation/" + str(id) + str(v) + "_annotation.csv"
            signals_path = "4_Alldata_window/"+ str(id) + str(v)+"_final_concatfeatures.csv"

            # Load the data
            annotation = pd.read_csv(annotation_path)
            signals = pd.read_csv(signals_path)

            # Concatenate the two dataframes side by side (axis=1)
            concatenated_data = pd.concat([signals, annotation], axis=1)

            # Print or save the concatenated data
            print(f"Concatenated data for user {id} and video {v}:")
            print(concatenated_data.head())  # Print first few rows for verification

            # Save the concatenated result (optional)
            concatenated_data.to_csv(f"6_signal_probe/concatenated_data_{id}_{v}.csv", index=False)

    all_dataframes = []
    import os
    for id in P_id:
        for v in video_id:
            # Construct the filename for the current concatenated file
            file_path = f"6_signal_probe/concatenated_data_{id}_{v}.csv"

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
                probe_values = selected_user['Probe'].tolist()

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

        all_users_df.to_csv('alluser_normalized_allfeatures.csv', index=False)


if __name__ == "__main__":
    ids = list(range(1,37)) + list(range(55,61))
    # ids = list(range(1,2))
    P_id = list(range(1,43))
    video_id = list(range(1,9))

    # signal_preprocessing (ids, video_id)
    # signals_normalization(ids, video_id)
    # extract_features(ids, video_id)
    # add_normalized_score(ids,video_id)
    # annotate_window (ids, video_id)
    # concat_all_data(P_id, video_id)
    add_prevwindow(P_id, video_id)

##########################################################################################################################

#Probe_2 annotation
# import pandas as pd
#
# data = pd.read_csv("42_mid2_userwise_valarou_data.csv")
# data['probe_2'] = 0  # Ensure consistent column name (lowercase)
#
# for id in ids:
#     # For video 1: Set 'probe_2' to 1 for the first 2 rows
#     video_1_rows = data[(data['video_id'] == 1) & (data['P_id'] == id)]
#     data.loc[video_1_rows.index[:2], 'probe_2'] = 1
#
#     # For video 2: Set 'probe_2' to 1 for the first 27 rows
#     video_2_rows = data[(data['video_id'] == 2) & (data['P_id'] == id)]
#     data.loc[video_2_rows.index[:27], 'probe_2'] = 1
#
#     # For video 3: Set 'probe_2' to 1 for the first 22 rows
#     video_3_rows = data[(data['video_id'] == 3) & (data['P_id'] == id)]
#     data.loc[video_3_rows.index[:22], 'probe_2'] = 1
#
#     # For video 4: Set 'probe_2' to 1 for the first 4 rows and rows with indices 18 to 31
#     video_4_rows = data[(data['video_id'] == 4) & (data['P_id'] == id)]
#     data.loc[video_4_rows.index[:4], 'probe_2'] = 1
#     data.loc[video_4_rows.index[18:32], 'probe_2'] = 1
#
#     # For video 5: Set 'probe_2' to 1 for the first 3 rows (update comment)
#     video_5_rows = data[(data['video_id'] == 5) & (data['P_id'] == id)]
#     data.loc[video_5_rows.index[:3], 'probe_2'] = 1
#
#     # For video 6: Set 'probe_2' to 1 for the first 5 rows
#     video_6_rows = data[(data['video_id'] == 6) & (data['P_id'] == id)]
#     data.loc[video_6_rows.index[:5], 'probe_2'] = 1
#
#     # For video 7: Set 'probe_2' to 1 for the first 8 rows
#     video_7_rows = data[(data['video_id'] == 7) & (data['P_id'] == id)]
#     data.loc[video_7_rows.index[:8], 'probe_2'] = 1
#
#     # For video 8: Set 'probe_2' to 1 for the first 14 rows
#     video_8_rows = data[(data['video_id'] == 8) & (data['P_id'] == id)]
#     data.loc[video_8_rows.index[:14], 'probe_2'] = 1
#
# # Save the updated dataframe to a new CSV file
# data.to_csv('42_modified_userwise_valarou_data.csv', index=False)

#####################################################################################################
# import pandas as pd
#
# # Load the data
# data = pd.read_csv("final_42datafeatures.csv")
# data2 = pd.read_csv("42_concatenated2_data.csv")
#
# # Initialize an empty DataFrame to store results
# df = pd.DataFrame(columns=["P_id", "old", "new"])
#
# for id in ids:
#     # Filter data for the current id in the first dataframe with Probe == 1
#     index = (data["P_id"] == id) & (data["Probe"] == 0)
#     data_index = data.loc[index]
#     data_shape = data_index.shape[0]  # Get the number of rows for the old data
#
#     # Correct the filter to use data2 instead of data
#     index2 = (data2["P_id"] == id) & (data2["probe"] == 0)
#     data2_index = data2.loc[index2]
#     data2_shape = data2_index.shape[0]  # Get the number of rows for the new data
#
#     # Append the results for the current id to the DataFrame
#     df = pd.concat([df, pd.DataFrame({"P_id": [id], "old": [data_shape], "new": [data2_shape]})], ignore_index=True)
#
# # Save the results to a CSV file
# df.to_csv("test4.csv", index=False)


