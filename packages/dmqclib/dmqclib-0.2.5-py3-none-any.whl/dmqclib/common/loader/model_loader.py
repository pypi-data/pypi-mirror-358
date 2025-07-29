from typing import Dict

from dmqclib.common.base.model_base import ModelBase
from dmqclib.common.loader.model_registry import MODEL_REGISTRY
from dmqclib.utils.config import read_config


def _get_model_info(dataset_name: str, config_file: str = None) -> Dict:
    config = read_config(config_file, "training.yaml")

    dataset_info = config.get(dataset_name)
    if dataset_info is None:
        raise ValueError(
            f"No dataset configuration found for the dataset '{dataset_name}'"
        )

    return dataset_info


def _get_model_class(dataset_info: Dict, registry: Dict) -> ModelBase:
    class_name = dataset_info["base_class"].get("model")
    model_class = registry.get(class_name)
    if not model_class:
        raise ValueError(f"Unknown dataset class specified: {class_name}")

    return model_class


def load_model_class(dataset_name: str, config_file: str = None) -> ModelBase:
    """
    Given a label (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """

    dataset_info = _get_model_info(dataset_name, config_file)
    model_class = _get_model_class(dataset_info, MODEL_REGISTRY)

    return model_class(
        dataset_name,
        config_file,
    )
