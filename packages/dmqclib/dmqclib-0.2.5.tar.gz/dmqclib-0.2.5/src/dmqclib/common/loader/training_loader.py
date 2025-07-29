from typing import Dict

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.common.loader.training_registry import INPUT_TRAINING_SET_REGISTRY
from dmqclib.common.loader.training_registry import MODEL_VALIDATION_REGISTRY
from dmqclib.training.step1_input.input_base import InputTrainingSetBase
from dmqclib.training.step2_validate.validate_base import ValidationBase
from dmqclib.utils.config import read_config


def _get_training_set_info(dataset_name: str, config_file: str = None) -> Dict:
    config = read_config(config_file, "training.yaml")

    dataset_info = config.get(dataset_name)
    if dataset_info is None:
        raise ValueError(
            f"No dataset configuration found for the dataset '{dataset_name}'"
        )

    return dataset_info


def _get_training_class(
    dataset_info: Dict, step_name: str, registry: Dict
) -> DataSetBase:
    class_name = dataset_info["base_class"].get(step_name)
    dataset_class = registry.get(class_name)
    if not dataset_class:
        raise ValueError(f"Unknown dataset class specified: {class_name}")

    return dataset_class


def load_step1_input_training_set(
    dataset_name: str, config_file: str = None
) -> InputTrainingSetBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_training_set_info(dataset_name, config_file)
    dataset_class = _get_training_class(
        dataset_info, "input", INPUT_TRAINING_SET_REGISTRY
    )

    return dataset_class(dataset_name, config_file=config_file)


def load_step2_model_validation_class(
    dataset_name: str, config_file: str = None, training_sets: pl.DataFrame = None
) -> ValidationBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_training_set_info(dataset_name, config_file)
    dataset_class = _get_training_class(
        dataset_info, "validate", MODEL_VALIDATION_REGISTRY
    )

    return dataset_class(
        dataset_name, config_file=config_file, training_sets=training_sets
    )
