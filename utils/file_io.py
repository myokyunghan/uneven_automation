import json
from constants import CONSTANTS

def load_json(path):
    """

    Args:
        path: a str

    Returns:
        a dict or a list of dict
    """
    if CONSTANTS.verbose_loading:
        print(f"[Loading] {path}")
    with open(path, "r") as file_:
        to_return = json.load(file_)
    return to_return


def save_json(to_save, path):
    """

    Args:
        to_save: a dict or a list of dict
        path: a str

    Returns:
        None
    """
    print(f"[Saving] {path}")
    with open(path, 'w') as file:
        json.dump(to_save, file, ensure_ascii=False, indent=4)
