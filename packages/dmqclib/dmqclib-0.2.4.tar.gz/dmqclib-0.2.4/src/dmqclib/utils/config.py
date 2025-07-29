import os
from pathlib import Path
from typing import Dict

import yaml


def read_config(
    config_file: str = None, config_file_name: str = None, parent_level: int = 3
) -> Dict:
    """
    Reads either a YAML configuration file specified in config_file
    or a file named config_file_name after traversing parent_level directories
    upward from this file.

    :param config_file: The full path name of the config file.
    :param config_file_name: The name of the config file (e.g., "datasets.yaml").
    :param parent_level: Number of directories to go up from __file__.

    :return: A dictionary representing the parsed YAML file content.
    """

    if config_file is None:
        if config_file_name is None:
            raise ValueError(
                "'config_file_name' cannot be None when 'config_file' is None"
            )
        config_file = (
            Path(__file__).resolve().parents[parent_level] / "config" / config_file_name
        )

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"The file '{config_file}' does not exist.")

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    data["config_file_name"] = config_file

    return data


def get_base_path_from_config(v: Dict, step_name: str) -> str:
    if step_name not in v or (step_name in v and "base_path" not in v[step_name]):
        step_name = "common"
    base_path = v[step_name].get("base_path", "")

    if base_path is None or base_path == "":
        raise ValueError("'base_path' not found or set to None in the config file")

    return base_path


def get_folder_name_from_config(
    v: Dict, step_name: str, folder_name_auto: bool = True
) -> str:
    orig_step_name = step_name
    if step_name not in v or (step_name in v and "folder_name" not in v[step_name]):
        step_name = "common"
    folder_name = v[step_name].get("folder_name")

    if folder_name is None:
        folder_name = orig_step_name if folder_name_auto else ""

    return folder_name


def get_dataset_folder_name_from_config(
    v: Dict, step_name: str, use_common=True
) -> str:
    if use_common and (
        step_name not in v or (step_name in v and "folder_name" not in v[step_name])
    ):
        step_name = "common"
    folder_name = v[step_name].get("folder_name") or ""

    return folder_name


def get_file_name_from_config(v: Dict, step_name: str, default_name: str = None) -> str:
    file_name = default_name
    if step_name in v and "file_name" in v[step_name]:
        file_name = v[step_name].get("file_name", "")

    if file_name is None:
        raise ValueError("'input_file' not found or set to None in the config file")

    return file_name


def get_target_file_name(v: Dict, target_name: str, default_name: str = None) -> str:
    file_name = v.get("file_name", "")
    if file_name is None or file_name == "":
        if default_name is None:
            raise ValueError("'input_file' not found or set to None in the config file")
        else:
            file_name = default_name.format(target_name=target_name)

    return file_name


def get_targets(
    dataset_info: Dict, step_name: str, default_targets: Dict = None
) -> Dict:
    if step_name in dataset_info and "targets" in dataset_info[step_name]:
        targets = dataset_info[step_name]["targets"]
    else:
        targets = default_targets

    if targets is None:
        raise ValueError("'targets' not found or set to None in the config file")

    return targets
