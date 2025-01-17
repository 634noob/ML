"""Main function to call the Data clean method with multiple process"""
from data_filter import DataFilter
from data_cleaner import DataCleaner
import time
import multiprocessing as mp
from functools import partial
import pandas as pd
import pickle
import os
import re

"""
this main function generates two files: 
0_filterd: to filter original raw data line by line
1_cleaned: to clean up data. e.g. extract news body, remove unnecessary words etc. 
"""

work_dir = "../../data/intermediate"


def clean_a_file_and_return_data(input_file, data_processor, article_dict):
    # result = []
    with open(input_file, encoding="utf-8") as f:
        line_nu = 0
        for line in f:
            if line_nu != 0:
                data_processor(line, article_dict)
            line_nu += 1
    return data_processor.m_data_series


def filter_handler(file_list, data_processor, article_dict):
    p = mp.Pool(4)
    result = pd.Series()
    for return_data_series in p.imap(
            partial(clean_a_file_and_return_data, data_processor=data_processor, article_dict=article_dict), file_list):
        result = result.append(return_data_series)
    return result


def run():
    manager = mp.Manager()
    shared_article_dict = manager.dict()
    my_filter = DataFilter()
    input_file_list = ["../../data/raw/News.RTRS.201806.0214.txt",
                       "../../data/raw/News.RTRS.201807.0214.txt",
                       "../../data/raw/News.RTRS.201808.0214.txt"]
    print("\nFiltering data ...")
    start = time.time()
    filtered_series = filter_handler(input_file_list, my_filter, shared_article_dict)
    end = time.time()
    print("Finished in: %s seconds" % (end - start))

    print("\nWriting filtered data ...")
    start = time.time()
    with open(work_dir + "/0_filtered.dat", "w", encoding="utf-8") as f_out:
        for each_time in filtered_series:
            for body in each_time:
                f_out.write(body)
    end = time.time()
    print("Finished in: %s seconds" % (end - start))

    # print(my_dict.at[np.datetime64('2018-06-08')][1])
    print("\nCleaning data ...")
    start = time.time()
    cleaner = DataCleaner(filtered_series)
    cleaner()
    end = time.time()
    print("Finished in: %s seconds" % (end - start))

    with open(work_dir + "/1_cleaned.dat", "w", encoding="utf-8") as f_out:
        for each_time in cleaner.m_data_series:
            for body in each_time:
                f_out.write(body + "\n")
    pickle_out = open(work_dir + "/1_cleaned.pickle", "wb")
    pickle.dump(cleaner.m_data_series, pickle_out)
    pickle_out.close()


def create_target(names, profile):
    target_dir = work_dir + "/targets"
    if not os.path.exists(target_dir):
        print("\ncreating dir: ", target_dir, "\n")
        os.makedirs(target_dir)
    pickle_in = open(work_dir + "/1_cleaned.pickle", "rb")
    cleaned_news_universe = pickle.load(pickle_in)
    pickle_in.close()
    target_news = {}
    stats = {}
    candidates = []
    for name in names:
        candidates.append(re.compile(name.lower().strip()))
    for date in cleaned_news_universe.keys():
        target_news[date] = []
        stats[date] = 0
        for article in cleaned_news_universe[date]:
            for candidate in candidates:
                if candidate.search(article):
                    target_news[date].append(article)
                    stats[date] += 1
                    break
    # for date in stats:
    #     print(pd.to_datetime(str(date)).strftime('%Y-%m-%d') + " " + str(stats[date]))
    pickle_out = open(target_dir + "/1_cleaned_" + profile.lower().strip() + ".pickle", "wb")
    pickle.dump(target_news, pickle_out)
    pickle_out.close()
    print("Finished dumping target/1_cleaned_" + profile + ".pickle\n")


if __name__ == '__main__':
    run()
