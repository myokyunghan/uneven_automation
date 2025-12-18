import json
from constants import CONSTANTS


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

if __name__ == "__main__":
    from utils.sublist import get_sublist_of_desired_tags
    src_dir = "../data/questions/questions"
    dest_dir = "../data/questions/questions_python"
    for i in range(13):
        src_path = f"{src_dir}/{i}.json"
        dest_path = f"{dest_dir}/{i}.json"
        loaded = load_json(src_path)
        python_included = get_sublist_of_desired_tags(loaded, ['python'])
        save_json(python_included, dest_path)