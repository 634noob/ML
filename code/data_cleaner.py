import re
import os
import numpy as np


class DataCleaner:
    """
    Class name: DataCleaner
    CLass Methods:
        1. filter_language: This method is to filter the raw data with the language given
        2. data_clean(TBD): This method is to the data cleaning, including multiple rules
        3. gen_data: This method is to generate lists items to pass to the ngram model
    """

    def __init__(self, language, input_file_lst, output_path):
        self.headline_lst = []
        self.body_lst = []
        self.m_dict = {}
        self.language = language
        self.input_file_lst = input_file_lst
        self.output_path = output_path
        self.output_file = output_path + "en_output.dat"
        self.intermediate_filtered = output_path + "0_filtered.dat"
        self.find_en = re.compile("\"language\": \"" + self.language + "\"")
        self.find_headline = re.compile('"headline": "(.*?)", "takeSequence"')
        self.find_body = re.compile('"body": "(.*?)", "mimeType"')
        self.find_data = re.compile("\"data\": {(.*?)}}")
        self.find_time = re.compile('"versionCreated": "(.*?)"')

    def __call__(self):
        self.remove_output_file()  # Remove the output file if it exists
        self.filter_all_conditions()
        self.gen_data()
        # self.gen_headline_lst()
        # self.gen_body_lst()

    # def gen_headline_lst(self):
    #     with open(self.output_file, encoding="utf-8") as f:
    #         for line in f:
    #             m_headline = self.find_headline.search(line)
    #             self.headline_lst.append(m_headline.group(1))
    #
    # def gen_body_lst(self):
    #     with open(self.output_file, encoding="utf-8") as f:
    #         for line in f:
    #             m_body = self.find_body.search(line)
    #             self.body_lst.append(m_body.group(1))
    @staticmethod
    def data_regx_clean(string):
        """Function that contains all the data processing"""
        return string.replace('\\n', '\n').replace('\"', '"').replace('\\r', '\r')

    def gen_data(self):
        """Function: To generate the list and dictionary needed for NGRAM model"""
        with open(self.intermediate_filtered, encoding="utf-8") as f:
            for line in f:
                m_headline = self.find_headline.search(line)
                m_headline = m_headline.group(1)
                m_body = self.find_body.search(line)
                m_body = m_body.group(1)
                m_time = self.find_time.search(line)
                m_time = m_time.group(1)
                if m_body != '':
                    self.headline_lst.append(self.data_regx_clean(m_headline))
                    self.body_lst.append(self.data_regx_clean(m_body))
                    m_time = np.datetime64(m_time).astype('datetime64[D]')
                    if m_time not in self.m_dict:
                        self.m_dict[m_time] = []
                        self.m_dict[m_time].append(self.data_regx_clean(m_body))
                    else:
                        self.m_dict[m_time].append(self.data_regx_clean(m_body))

    def filter_all_conditions(self):
        for input_file in self.input_file_lst:
            with open(input_file, encoding="utf-8") as f:
                output = open(self.intermediate_filtered, "a+", encoding="utf-8")
                for line in f:
                    if self.not_english(line):
                        m_data = self.find_data.search(line)
                        data = m_data.group(1)
                        if self.target_headline(data):
                            output.write(data + "\n")
                output.close()

    def not_english(self, line):
        return self.find_en.search(line)

    @staticmethod
    def target_headline(line):
        return '"headline": "TABLE-' not in line and "*TOP NEWS*-Front Pag" not in line

    def remove_output_file(self):
        for the_file in os.listdir(self.output_path):
            file_path = os.path.join(self.output_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        print("Output File Removed!")
