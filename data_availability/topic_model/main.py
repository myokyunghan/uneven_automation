import sys, os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
    
sys.path.append(PARENT_DIR)

import pprint
from glob import glob
from bert_based_models import load_bert_based_model_from_config
from lda_model import load_lda_model_from_config
from config import RunnerConfig
from utils.file_io import load_json, save_json
from utils.datetime_handler import get_monthly_datetime_str
from utils.sublist import (get_sublist_of_desired_date_range,
                         get_sublist_of_desired_tags)



class ModelRunner:
    def __init__(self):
        self.runner_config = RunnerConfig()
        self.model_in_run = None
        self.model = None
        self.config = None
        self.data_dir = None
        self.data_dir_for_fit = None
        self.save_dir = None
        self.save_length = 10000
        self.load_config_and_topic_model()
        self.load_dirs_from_config()

    def __call__(self):
        self.run()

    def run(self):
        pprint.pp(self.config)
        self.run_model_and_save_data()
        self.save_config()

    def load_config_and_topic_model(self):
        """

        Returns:
            None
        """
        self.model_in_run = self.runner_config.model_in_run
        if self.model_in_run == "bert_based":
            self.config = self.runner_config.bert_based_config
            self.model = load_bert_based_model_from_config(
                self.config["model_config"]
            )
        elif self.model_in_run == "lda":
            self.config = self.runner_config.lda_config
            self.model = load_lda_model_from_config(
                self.config["model_config"]
            )
        else:
            raise ValueError("'bert_based' and 'lda' are supported")

    def load_dirs_from_config(self):
        """

        Returns:
            None
        """
        run_id = self.config['run_id']
        self.data_dir = self.config['data_dir']
        self.save_dir = f'../result/{self.model_in_run}/run_id_{run_id}'
        os.makedirs(f"{self.save_dir}/data", exist_ok=True)


    def load_all_files(self):
        """

        Returns:
            a list of dict
        """
        file_list = glob(f'{self.data_dir}/*.json')
        print(f">>>>>>>>>>>>>>>>>>>>>>load_all_files : {file_list}")
        to_return = []
        for file in file_list:
            loaded = load_json(file)
            to_return += loaded
        return to_return
    

    def load_all_files_for_fit(self):
        """

        Returns:
            a list of dict
        """
        if self.data_dir_for_fit is not None : 
            file_list = glob(f'{self.data_dir_for_fit}/*.json')
            print(f">>>>>>>>>>>>>>>>>>>>>>load_all_files_for_fit : {file_list}")
            to_return = []
            for file in file_list:
                loaded = load_json(file)
                to_return += loaded
        else : 
            to_return = None    
        return to_return


    def run_model_and_save_data(self):
        """

        Returns:
            None
        """
        data = self.load_all_files()
        fit_data = self.load_all_files_for_fit()
        if self.config["selected_tags"] is not None:
            data = get_sublist_of_desired_tags(data,
                                               self.config["selected_tags"])
        result = self.model.run_model_and_get_output_list(data, fit_data)
        topic_info = self.model.get_topic_info()
        save_json(topic_info, f"{self.save_dir}/topic_info.json")
        self.save_data(result)

    def save_data(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            None
        """
        length = len(list_)
        iters = length // self.save_length
        for i in range(iters):
            start_idx = i * self.save_length
            end_idx = (i + 1) * self.save_length
            to_save = list_[start_idx:end_idx]
            save_json(to_save, f"{self.save_dir}/data/{i}.json")
        if length - iters * self.save_length > 0:
            start_idx = iters * self.save_length
            to_save = list_[start_idx:]
            save_json(to_save, f"{self.save_dir}/data/{iters}.json")

    def save_config(self):
        """

        Returns:
            None
        """
        save_json(self.config, f'{self.save_dir}/config.json')


if __name__ == '__main__':
    runner = ModelRunner()
    runner()
