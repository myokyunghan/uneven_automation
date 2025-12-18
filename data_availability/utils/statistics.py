import re
import numpy as np
from scipy.stats import entropy
from glob import glob
from utils.data_loader import DataLoader


def get_fractional_values_dict(dict_, denominator=None):
    """

    Args:
        dict_: a dict, where values are counts
        denominator: a positive int (optional)

    Returns:
        a dict, where values are fractions
    """
    if denominator is not None:
        total_count = denominator
    else:
        total_count = sum(list(dict_.values()))
    to_return = {key: count/total_count for key, count in dict_.items()}
    return to_return


def calculate_gini(list_):
    """

    Args:
        list_: a list of probabilities of discrete distribution

    Returns:
        a Gini coefficient
    """
    array_ = np.array(list_)
    mad = np.abs(np.subtract.outer(array_, array_)).mean()
    rmad = mad / np.mean(array_)
    to_return = 0.5 * rmad
    return to_return


def calculate_entropy(list_):
    """

    Args:
        list_: a list of probabilities of discrete distribution

    Returns:
        a Shannon entropy
    """
    to_return = entropy(list_)
    return to_return


def calculate_cdf(distribution):
    """

    Args:
        distribution: a pdf dict,
                      where keys are int and values are fractions

    Returns:
        a cdf dict
    """
    cdf = {topic: 0 for topic in distribution}
    for topic in distribution:
        cumulative_prob = sum([value for key, value in distribution.items()
                               if key < topic])
        cdf[topic] = cumulative_prob
    return cdf

def calculate_ccdf(distribution):
    """

    Args:
        distribution: a pdf dict,
                      where keys are int and values are fractions

    Returns:
        a ccdf dict
    """
    cdf = calculate_cdf(distribution)
    ccdf = {topic: 1 - prob for topic, prob in cdf.items()}
    return ccdf


def topic_rank_before_gpt(dir_):
    """

    Args:
        dir_: a directory path, where monthly-saved files are located

    Returns:
        a dict, where keys are topics and values are their ranks
    """
    topics_counts = get_monthly_topics_counts(dir_, list(range(50)))
    counts_before_gpt = {topic: sum(val[:12]) for topic, val in
                         topics_counts.items()}
    counts_before_gpt = {k: v for k, v in sorted(counts_before_gpt.items(),
                                                 key=lambda item: item[1],
                                                 reverse=True)}
    to_return = {}
    topics_in_rank_order = list(counts_before_gpt.keys())
    for i in range(len(topics_in_rank_order)):
        to_return[topics_in_rank_order[i]] = i
    return to_return


def get_topics_counts_bert(list_, topics):
    """

    Args:
        list_: a list of dict, where each dict has the key "Topic"
        topics: a list of int

    Returns:
        a dict, where keys are topics and values are counts
    """
    to_return = {topic: 0 for topic in topics}
    for dict_ in list_:
        topic = dict_["Topic"]
        if topic in topics:
            to_return[topic] += 1
    return to_return


def get_topics_counts_lda(list_, topics):
    """

    Args:
        list_: a list, where each list has the key "topic_info"
        topics: a list of int

    Returns:
        a dict, where keys are topics and values are counts
    """
    to_return = {topic: 0 for topic in topics}
    for dict_ in list_:
        for topic in topics:
            to_return[topic] += dict_["topic_info"][topic]
    return to_return


def get_tags_counts(list_, tags):
    """

    Args:
        list_: a list of dict, where each dict has the key "tags"
        tags: a list of str

    Returns:
        a dict, where keys are tags and values are counts
    """
    to_return = {tag: 0 for tag in tags}
    for dict_ in list_:
        dict_tags = re.findall(
            pattern='<(.*?)>',
            string=dict_["tags"]
        )
        for tag in tags:
            if tag in dict_tags:
                to_return[tag] += 1
    return to_return


def get_monthly_topics_counts_bert(dir_, topics):
    """

    Args:
        dir_: a directory path, where monthly-saved files are located
        topics: a list of int

    Returns:
        a dict, where keys are topics and values are list of counts
    """
    to_return = {topic: [] for topic in topics}
    file_num = len(glob(f"{dir_}/*.json"))
    for i in range(file_num):
        list_ = DataLoader.load_json(f"{dir_}/{i}.json")
        counts = get_topics_counts_bert(list_, topics)
        for topic in topics:
            to_return[topic].append(counts[topic])
    return to_return


def get_monthly_topics_counts_lda(dir_, topics):
    """

    Args:
        dir_: a directory path, where monthly-saved files are located
        topics: a list of int

    Returns:
        a dict, where keys are topics and values are list of counts
    """
    to_return = {topic: [] for topic in topics}
    file_num = len(glob(f"{dir_}/*.json"))
    for i in range(file_num):
        list_ = DataLoader.load_json(f"{dir_}/{i}.json")
        counts = get_topics_counts_lda(list_, topics)
        for topic in topics:
            to_return[topic].append(counts[topic])
    return to_return


def get_monthly_topics_counts(dir_, topics):
    """

    Args:
        dir_: a directory path, where monthly-saved files are located
        topics: a list of int

    Returns:
        a dict, where keys are topics and values are list of counts
    """
    sample_file = glob(f"{dir_}/*.json")[0]
    list_ = DataLoader.load_json(sample_file)
    if "Topic" in list_[0]:
        return get_monthly_topics_counts_bert(dir_, topics)
    elif "topic_info" in list_[0]:
        return get_monthly_topics_counts_lda(dir_, topics)
    else:
        raise Exception


def get_monthly_tags_counts(dir_, tags):
    """

    Args:
        dir_: a directory path, where monthly-saved files are located
        tags: a list of str

    Returns:
        a dict, where keys are tags and values are list of counts
    """
    to_return = {tag: [] for tag in tags}
    file_num = len(glob(f"{dir_}/*.json"))
    for i in range(file_num):
        list_ = DataLoader.load_json(f"{dir_}/{i}.json")
        counts = get_tags_counts(list_, tags)
        for tag in tags:
            to_return[tag].append(counts[tag])
    return to_return


def moving_average(list_, window_size):
    """

    Args:
        list_: a list of numbers
        window_size: a positive int

    Returns:
        a list of numbers with the same length
    """
    to_return = []
    for i in range(len(list_)):
        if i - window_size < 0:
            start_idx = 0
        else:
            start_idx = i - window_size
        if i + window_size > len(list_):
            end_idx = len(list_)
        else:
            end_idx = i + window_size
        to_calc = list_[start_idx:end_idx]
        to_append = sum(to_calc)/len(to_calc)
        to_return.append(to_append)
    return to_return


