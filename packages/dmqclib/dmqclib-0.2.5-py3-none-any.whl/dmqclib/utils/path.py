import os
from typing import Dict

from dmqclib.utils.config import get_base_path_from_config
from dmqclib.utils.config import get_dataset_folder_name_from_config
from dmqclib.utils.config import get_folder_name_from_config


def build_full_input_path(
    path_info: Dict,
    dataset_info: Dict,
    file_name: str,
    folder_name_auto: bool = True,
) -> str:
    """
    Build a full input path based on the fields in the 'config' dictionary and
    the provided arguments. The assembled path is:
        path_info["input"]["base_path"] +
        "/" + path_info["input"]["folder_name"] +
        "/" + folder_name2 +
        "/" + file_name

    Both path_info["input"]["folder_name"] and folder_name2
    can be None or an empty string. They can also include "..".

    :param path_info: A dictionary that must contain:
                      path_info["input"]["base_path"] (str)
                      path_info["input"]["folder_name"] (str or None)
    :param dataset_info: A dictionary that contains dataset_info["input"]["folder_name"]
    :param folder_name2: The input folder name (can be None or empty string).
    :param file_name: The name of the file to append at the end of the path.
    :param folder_name_auto: use "input" as folder name if no entries are found in config
    :return: A string representing the full path.
    """
    base_path = get_base_path_from_config(path_info, "input")
    folder_name1 = get_folder_name_from_config(path_info, "input", folder_name_auto)
    folder_name2 = get_dataset_folder_name_from_config(
        dataset_info, "input", use_common=False
    )

    return os.path.normpath(
        os.path.join(base_path, folder_name1, folder_name2, file_name)
    )


def build_full_data_path(
    path_info: Dict,
    dataset_info: Dict,
    step_name: str,
    file_name: str,
    folder_name_auto: bool = True,
) -> str:
    """
    Build a full data path based on the fields in the 'config' dictionary and
    the provided arguments. The assembled path is:
        path_info[step_name]["base_path"] +
        "/" + folder_name1 +
        "/" + path_info[step_name]["folder_name"] +
        "/" + file_name

    Both folder_name1 and path_info[step_name]["folder_name"]
    can be None or an empty string. They can also include "..".

    :param path_info: A dictionary that must contain:
                   path_info[step_name]["base_path"] (str)
                   path_info[step_name]["folder_name"] (str or None)
    :param dataset_info: A dictionary that contains dataset_info[step_name]["folder_name"]
    :param file_name: The name of the file to append at the end of the path.
    :param folder_name_auto: use step_name as folder name if no entries are found in config

    :return: A string representing the full path.
    """
    base_path = get_base_path_from_config(path_info, step_name)
    folder_name1 = get_dataset_folder_name_from_config(dataset_info, step_name)
    folder_name2 = get_folder_name_from_config(path_info, step_name, folder_name_auto)

    return os.path.normpath(
        os.path.join(base_path, folder_name1, folder_name2, file_name)
    )
