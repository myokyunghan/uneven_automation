from constants import *
from datetime import datetime, timedelta
import os


def get_datetime_strings_before_and_after_gpt(window=7):
    """

    Returns:
        list of str, where each str are weekly datetime strings
    """
    chatgpt_release_date \
        = datetime.strptime(CONSTANTS.chatgpt_release_date, '%Y.%m.%d')
    start_date = datetime.strptime(CONSTANTS.start_date, '%Y.%m.%d')
    end_date = datetime.strptime(CONSTANTS.end_date, '%Y.%m.%d')
    to_return = []
    range_num = (chatgpt_release_date-start_date).days // window
    for i in range(-window*range_num, 0, window):
        to_append = chatgpt_release_date + timedelta(days=i)
        to_return.append(str(to_append))
    range_num = (end_date-chatgpt_release_date).days // window + 1
    for i in range(0, window*range_num, window):
        to_append = chatgpt_release_date + timedelta(days=i)
        to_return.append(str(to_append))
    print(to_return)
    return to_return


def get_monthly_datetime_str():
    """

    Returns:
        a list of str
    """
    timestamps = CONSTANTS.monthly_timestamps
    to_return = []
    for timestamp in timestamps:
        time_str = str(datetime.strptime(timestamp, '%Y.%m.%d'))
        to_return.append(time_str)
    return to_return


def get_related_files(date_range, data_dir):
    """

    Args:
        date_range: a couple of string

    Returns:
        a list of string
    """
    monthly_datetime_str = get_monthly_datetime_str()
    start_date = date_range[0]
    end_date = date_range[1]
    to_return = []
    
    lst = os.listdir(data_dir)
    for i in range(len(lst)):
        if (start_date <= monthly_datetime_str[i] < end_date) or \
                (monthly_datetime_str[i] <= start_date < monthly_datetime_str[i+1]):
            to_return.append(i)
    return to_return

def is_weekday(date_str):
    """

    Returns:
        Boolean
    """
    return datetime.strptime(date_str[:10], '%Y-%m-%d').weekday() < 5

def is_target_weekday(date_str, weekday):
    """
    Returns:
        Boolean
    """
    return datetime.strptime(date_str[:10], '%Y-%m-%d').weekday() == weekday



if __name__ == '__main__':
    print(get_datetime_strings_before_and_after_gpt(1))
    print(len(get_datetime_strings_before_and_after_gpt(1)))
