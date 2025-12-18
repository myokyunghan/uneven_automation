import re

def get_sublist_of_desired_date_range(list_, date_range):
    """

    Args:
        list_: a list of dict, where each dict has the key "creationdate"
        date_range: a tuple (str, str)

    Returns:
        a list of dict
    """
    to_return = []
    for dict_ in list_:

        date_ = dict_["creationdate"]
        if date_range[0] <= date_ < date_range[1]:
            to_return.append(dict_)
    return to_return


def get_sublist_of_desired_topics(list_, topics):
    """

    Args:
        list_: a list of dict, where each dict has the key "Topic"
        topics: a list of int

    Returns:
        a list of dict
    """
    to_return = []
    for dict_ in list_:
        topic = dict_["Topic"]
        if topic in topics:
            to_return.append(dict_)
    return to_return


def get_sublist_of_desired_tags(list_, tags):
    """

    Args:
        list_: a list of dict, where each dict has the key "tags"
        tags: a list of str

    Returns:
        a list of dict
    """
    to_return = []
    for dict_ in list_:
        dict_tags = re.findall(
            pattern='<(.*?)>',
            string=dict_["tags"]
        )
        if len(set(dict_tags) & set(tags)) > 0:
            to_return.append(dict_)
    return to_return


if __name__ == "__main__":
    from datetime import datetime
    from data_loader import DataLoader
    total = 0
    src_dir = "../data/questions/python"
    dest_dir = "../data/questions/python_did_fit"
    time_start = str(datetime.strptime("2021.11.30", '%Y.%m.%d'))
    time_end = str(datetime.strptime("2023.11.30", '%Y.%m.%d'))
    for i in range(11):
        src_file = f"{src_dir}/{i}.json"
        dest_file = f"{dest_dir}/{i}.json"
        loaded = DataLoader.load_json(src_file)
        to_save = get_sublist_of_desired_date_range(loaded, (time_start, time_end))
        total += len(to_save)
        DataLoader.save_json(dest_file, to_save)
    print(total)


