from collections import Counter
# from centralized_baseline import is_change_present
from densratio import densratio
import glob
# import imp
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from natsort import natsorted, ns
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def cluster_data(data, k=2):
    kmeans = KMeans(n_clusters=k, random_state=0).fit(data)
    print(kmeans.cluster_centers_)
    print(Counter(kmeans.labels_))

    pos = -1

    pos = np.argmax(kmeans.cluster_centers_)
    print("pos:", pos)
    # print(kmeans.cluster_centers_[1])
    chosen_indices = []
    print(len(data))
    for i in range(len(kmeans.labels_)):
        if (kmeans.labels_[i] == pos):
            if (data[i] >= kmeans.cluster_centers_[pos]):
                chosen_indices.append(i)
    print(len(chosen_indices))
    return chosen_indices


def detect_outlier(data):
    data_mean, data_std = np.mean(data), np.std(data)
    cut_off = data_std * 2
    upper = data_mean + cut_off
    outliers = [x for x in data if x > upper]
    print(outliers)
    return outliers


def evaluate_system_quality(annotations_directory, video_id=-1):
    out_file = open("change_point_results_" + str(video_id) + ".txt", "w+")
    filelist = glob.glob("marks/*.csv")
    filelist = natsorted(filelist, key=lambda y: y.lower())
    for files in filelist:
        marks_data = pd.read_csv(files)
        query_subject = files.split("/")[-1].split(".")[0].split("_")[0] + "_" + \
                        files.split("/")[-1].split(".")[0].split("_")[1]
        print(query_subject)
        out_file.write(query_subject + "\n")
        annotations_data = pd.read_csv(annotations_directory + query_subject + ".csv")

        if (video_id != -1):
            annotations_data = annotations_data[annotations_data['video'] == video_id]

        label_valence = []
        label_arousal = []
        label_valence.append(annotations_data['valence'].iat[0])
        label_arousal.append(annotations_data['arousal'].iat[0])
        for i in range(len(marks_data['Start'])):
            max_diff = math.inf
            polled_valence = -1
            polled_arousal = -1
            for j in range(len(annotations_data['jstime'])):
                diff = abs(annotations_data['jstime'].iat[j] - marks_data['End'][i])
                if (diff < max_diff):
                    max_diff = diff
                    polled_valence = annotations_data['valence'].iat[j]
                    polled_arousal = annotations_data['arousal'].iat[j]

            label_valence.append(polled_valence)
            label_arousal.append(polled_arousal)

        # print(len(label_valence))

        assert len(label_valence) == len(marks_data['End']) + 1

        out_file.write("Total number of probes done earlier: " + str(
            len(annotations_data['valence'])) + " No. of probes now: " + str(len(label_valence)) + "\n")
        print(
            "Total number of probes done earlier: " + str(len(annotations_data['valence'])) + " No. of probes: " + str(
                len(label_valence)))

        print("Valence -- Actual Mean: " + str(annotations_data['valence'].mean()) + " Changed Mean: " + str(
            np.mean(label_valence)))
        out_file.write("Valence -- Actual Mean: " + str(annotations_data['valence'].mean()) + " Changed Mean: " + str(
            np.mean(label_valence)) + "\n")
        print("Arousal -- Actual Mean: " + str(annotations_data['arousal'].mean()) + " Changed Mean: " + str(
            np.mean(label_arousal)))
        out_file.write("Arousal -- Actual Mean: " + str(annotations_data['arousal'].mean()) + " Changed Mean: " + str(
            np.mean(label_arousal)) + "\n")

        print("Valence -- Actual Min: " + str(min(annotations_data['valence'])) + " Changed Min: " + str(
            min(label_valence)))
        print("Valence -- Actual Max: " + str(max(annotations_data['valence'])) + " Changed Max: " + str(
            max(label_valence)))
        out_file.write("Valence -- Actual Min: " + str(min(annotations_data['valence'])) + " Changed Min: " + str(
            min(label_valence)) + "\n")
        out_file.write("Valence -- Actual Max: " + str(max(annotations_data['valence'])) + " Changed Max: " + str(
            max(label_valence)) + "\n")

        print("Arousal -- Actual Min: " + str(min(annotations_data['arousal'])) + " Changed Min: " + str(
            min(label_arousal)))
        print("Arousal -- Actual Max: " + str(max(annotations_data['arousal'])) + " Changed Max: " + str(
            max(label_arousal)))
        out_file.write("Arousal -- Actual Min: " + str(min(annotations_data['arousal'])) + " Changed Min: " + str(
            min(label_arousal)) + "\n")
        out_file.write("Arousal -- Actual Max: " + str(max(annotations_data['arousal'])) + " Changed Max: " + str(
            max(label_arousal)) + "\n")

        out_file.flush()
    out_file.close()


def evaluate_system_changes(annotations_directory, video_id=-1):
    out_file = open("change_point_percentage_" + str(video_id) + ".txt", "w+")
    filelist = glob.glob("marks/*.csv")
    filelist = natsorted(filelist, key=lambda y: y.lower())
    for files in filelist:
        marks_data = pd.read_csv(files)
        query_subject = files.split("/")[-1].split(".")[0].split("_")[0] + "_" + \
                        files.split("/")[-1].split(".")[0].split("_")[1]
        print(query_subject)
        out_file.write(query_subject + "\n")
        annotations_data = pd.read_csv(annotations_directory + query_subject + ".csv")

        if (video_id != -1):
            annotations_data = annotations_data[annotations_data['video'] == video_id]

        count_change = 0
        for i in range(len(marks_data['Start'])):
            label_valence = []
            label_arousal = []
            for j in range(len(annotations_data['jstime'])):
                if (annotations_data['jstime'].iat[j] >= marks_data['Start'].iat[i] and annotations_data['jstime'].iat[
                    j] <= marks_data['End'].iat[i]):
                    label_valence.append(annotations_data['valence'].iat[j])
                    label_arousal.append(annotations_data['arousal'].iat[j])
                if (annotations_data['jstime'].iat[j] >= marks_data['End'].iat[i]):
                    break
            if (is_change_present(label_valence) or is_change_present(label_arousal)):
                count_change += 1

        print("Actual Changes Recorded: " + str(count_change * 100.0 / len(marks_data['Start'])))
        out_file.write("Actual Changes Recorded: " + str(count_change * 100.0 / len(marks_data['Start'])) + "\n")

        out_file.flush()

    out_file.close()


'''This will return the optimal number of clusters
that can be formed with the change point scores. 
We may use this for further analysis.'''


def get_optimal_k(data):
    n_clusters = 2
    temp_silhoutte_score = -math.inf
    while (n_clusters < 6):
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(data)
        silhouette_avg = silhouette_score(data, cluster_labels)
        print("For n_clusters = " + str(n_clusters) + " The average silhouette_score is : " + str(silhouette_avg))
        '''if(temp_silhoutte_score>silhouette_avg):
            return n_clusters-1'''
        if (temp_silhoutte_score < silhouette_avg):
            temp_silhoutte_score = silhouette_avg
            chosen_cluster = n_clusters
        n_clusters += 1
    return chosen_cluster


''' This function calculates the change point scores
across windows of a defined window_size (default 1000) and
writes into a file in the same "parent directory/scores" where the  
codes are placed [with the same filename append with "_scores"].'''


def get_change_point_scores(directory, filename, window_size=50):
    original_data = pd.read_csv(filename)
    # original_data.columns = ['ArduinoTime(ms)', 'GSR', 'HR', 'timestamp', 'datetime']


    # print(original_data.columns)
    # print(original_data)

    # if(video_id!=-1):
    # filter_data = original_data['video']==video_id
    # original_data = original_data [filter_data]

    print('directory:{},filename:{}'.format(directory, filename))

    # data = original_data[['value_EDA','value_TEMP','value_HR']]
    data = original_data[['GSR', 'HR']]
    print('data:{}'.format(data))
    data = np.asanyarray(data)
    print(data.shape)
    # out_file = open(directory+filename.split("/")[len(filename.split("/"))-1].split(".")[0]+"_scores.csv","w+")
    # path = './data/scores/'
    path = '/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/scores/'


    out_file = open(path + filename.split("/")[len(filename.split("/")) - 1].split(".")[0] + "_scores.csv", "w+")
    # x = filename.split("/")[len(filename.split("/")) - 1].split(".")[0] + "_scores.csv"
    # print(x)

    out_file.write("Start,Border,End,Score\n")
    scores = []
    print("len of data", len(data))
    for i in range(0, len(data) - 2 * window_size, window_size):
        # Creating samples
        x = data[i:i + window_size, :]
        print(x.shape)
        y = data[i + window_size:i + 2 * window_size, :]
        print(y.shape)

        alpha = 0.1  # needed for RuLSif

        # calculating x to y
        densratio_obj = densratio(x, y, alpha=alpha)
        score_x_y = float(densratio_obj.alpha_PE)

        # calculating y to x
        densratio_obj = densratio(y, x, alpha=alpha)
        score_y_x = float(densratio_obj.alpha_PE)

        '''Total change point score = score_x_y + score_y_x -- Taking absolute'''
        out_file.write(str(original_data['timestamp'].iat[i]) + "," + str(
            original_data['timestamp'].iat[i + window_size]) + "," + str(
            original_data['timestamp'].iat[i + 2 * window_size]) + "," + str(abs(score_x_y) + abs(score_y_x)) + "\n")
        out_file.flush()
    out_file.close()


def main():
    '''change to interpolated if you want your analysis
    to be on the interpolated data'''
    # parent_directory = "data/non-interpolated/"
    parent_directory = "/home/rounak/CODE/Low_Engagement_Detection/Data_preprocess/Preprocess_Signals/"
    physiological_directory = "1_input_signals/"

    # physiological_directory = "Physiological/"
    annotations_directory = "annotations/"
    file_list = glob.glob(parent_directory + physiological_directory + "*.csv")
    file_list = natsorted(file_list, key=lambda y: y.lower())
    print(file_list)

    if_filter = input('Do you want to filter on the basis of video-id? Press y, else press any other key: ')

    if (if_filter == 'y'):
        id = 1

    # Comments the next two lines if you have already computed the change-point scores
    for filenames in file_list:
        get_change_point_scores("new_scores/", filenames)


    # Calculate the optimal k for each user
    # file_list = glob.glob("5000/scores"+"/*_scores.csv")
    # print(file_list)


    # file_list = natsorted(file_list, key=lambda y: y.lower())
    # for filenames in file_list:
    #     query_subject = filenames.split("/")[-1].split(".")[0]
    #     print(query_subject)

    #     out_file = open("marks/"+query_subject+".csv","w+")
    #     out_file.write("Start,Border,End\n")

    #     print(filenames)
    #     original_data = pd.read_csv(filenames)

    #     min_outlier_val = detect_outlier (original_data['Score'])
    #     if(len(min_outlier_val)>0):
    #         min_outlier_val = min(min_outlier_val)
    #         print("Min outlier val: "+str(min_outlier_val))

    #         for i in range(len(original_data['Score'])):
    #             if(original_data['Score'][i]>=min_outlier_val):
    #                 out_file.write(str(original_data['Start'][i])+","+str(original_data['Border'][i])+","+str(original_data['End'][i])+"\n")

    #         print("Before outlier removal: "+str(len(original_data['Score'])))
    #         is_not_outlier = original_data['Score']<min_outlier_val
    #         original_data = original_data[is_not_outlier]
    #         print("After outlier removal: "+str(len(original_data['Score'])))

    #     optimal_k = get_optimal_k(np.asarray(original_data['Score']).reshape(-1, 1))
    #     print("optimal_k:",optimal_k)
    #     #optimal_k=2
    #     chosen_indices = cluster_data(np.asarray(original_data['Score']).reshape(-1, 1),optimal_k)
    #     print('chosen_indices:{}'.format(chosen_indices))

    #     for indices in chosen_indices:
    #         out_file.write(str(original_data['Start'].iat[indices])+","+str(original_data['Border'].iat[indices])+","+str(original_data['End'].iat[indices])+"\n")
    #     out_file.flush()
    #     out_file.close()

    #evaluate_system_changes(parent_directory+annotations_directory,video_id)
    #evaluate_system_quality(parent_directory+annotations_directory,video_id)

if __name__ == '__main__':
    main()