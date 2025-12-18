import json
from pandas import read_csv
from glob import glob


class DataLoader:
    def __init__(self):
        self.sample_data_dir_root = "../data/questions/sample"

    @staticmethod
    def load_json(path):
        """
        Args:
            path: a str

        Returns:
            a dict or a list of dict
        """
        with open(path, "r") as file_:
            to_return = json.load(file_)
        return to_return

    @staticmethod
    def save_json(path, data_):
        """
        Args:
            path: a str
            data_: a dict or a list of dict

        Returns:
            None
        """
        print(f"[Saving] {path}")
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(data_, f, indent=4)

    def load_all_the_samples_json(self, dir_=None):
        if dir_ is None:
            dir_ = self.sample_data_dir_root
        print(f"[Loading] all jsons in {dir_}")
        to_return = []
        file_list = glob(dir_ + "/*.json")
        loaded = [self.load_json(x) for x in file_list]
        for list_ in loaded:
            to_return += list_
        return to_return
    @staticmethod
    def load_csv(path):
        """

        Args:
            path: a str

        Returns:
            a list
        """
        to_return = read_csv(path)
        to_return = to_return.to_dict(orient="list")
        return to_return