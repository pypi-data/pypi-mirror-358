from typing import Dict

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.common.loader.dataset_registry import EXTRACT_DATASET_REGISTRY
from dmqclib.common.loader.dataset_registry import INPUT_DATASET_REGISTRY
from dmqclib.common.loader.dataset_registry import LOCATE_DATASET_REGISTRY
from dmqclib.common.loader.dataset_registry import SELECT_DATASET_REGISTRY
from dmqclib.common.loader.dataset_registry import SPLIT_DATASET_REGISTRY
from dmqclib.common.loader.dataset_registry import SUMMARY_DATASET_REGISTRY
from dmqclib.datasets.step1_input.input_base import InputDataSetBase
from dmqclib.datasets.step2_summary.summary_base import SummaryStatsBase
from dmqclib.datasets.step3_select.select_base import ProfileSelectionBase
from dmqclib.datasets.step4_locate.locate_base import LocatePositionBase
from dmqclib.datasets.step5_extract.extract_base import ExtractFeatureBase
from dmqclib.datasets.step6_split.split_base import SplitDataSetBase
from dmqclib.utils.config import read_config


def _get_dataset_info(dataset_name: str, config_file: str = None) -> Dict:
    config = read_config(config_file, "datasets.yaml")

    dataset_info = config.get(dataset_name)
    if dataset_info is None:
        raise ValueError(
            f"No dataset configuration found for the dataset '{dataset_name}'"
        )

    return dataset_info


def _get_class(dataset_info: Dict, step_name: str, registry: Dict) -> DataSetBase:
    class_name = dataset_info["base_class"].get(step_name)
    dataset_class = registry.get(class_name)
    if not dataset_class:
        raise ValueError(f"Unknown dataset class specified: {class_name}")

    return dataset_class


def load_step1_input_dataset(
    dataset_name: str, config_file: str = None
) -> InputDataSetBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "input", INPUT_DATASET_REGISTRY)

    return dataset_class(dataset_name, config_file=config_file)


def load_step2_summary_dataset(
    dataset_name: str, config_file: str = None, input_data: pl.DataFrame = None
) -> SummaryStatsBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "summary", SUMMARY_DATASET_REGISTRY)

    return dataset_class(dataset_name, config_file=config_file, input_data=input_data)


def load_step3_select_dataset(
    dataset_name: str, config_file: str = None, input_data: pl.DataFrame = None
) -> ProfileSelectionBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "select", SELECT_DATASET_REGISTRY)

    return dataset_class(dataset_name, config_file=config_file, input_data=input_data)


def load_step4_locate_dataset(
    dataset_name: str,
    config_file: str = None,
    input_data: pl.DataFrame = None,
    selected_profiles: pl.DataFrame = None,
) -> ExtractFeatureBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "locate", LOCATE_DATASET_REGISTRY)

    return dataset_class(
        dataset_name,
        config_file=config_file,
        input_data=input_data,
        selected_profiles=selected_profiles,
    )


def load_step5_extract_dataset(
    dataset_name: str,
    config_file: str = None,
    input_data: pl.DataFrame = None,
    selected_profiles: pl.DataFrame = None,
    target_rows: pl.DataFrame = None,
    summary_stats: pl.DataFrame = None,
) -> LocatePositionBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "extract", EXTRACT_DATASET_REGISTRY)

    return dataset_class(
        dataset_name,
        config_file=config_file,
        input_data=input_data,
        selected_profiles=selected_profiles,
        target_rows=target_rows,
        summary_stats=summary_stats,
    )


def load_step6_split_dataset(
    dataset_name: str,
    config_file: str = None,
    target_features: pl.DataFrame = None,
) -> SplitDataSetBase:
    """
    Given a dataset_name (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    dataset_info = _get_dataset_info(dataset_name, config_file)
    dataset_class = _get_class(dataset_info, "split", SPLIT_DATASET_REGISTRY)

    return dataset_class(
        dataset_name,
        config_file=config_file,
        target_features=target_features,
    )
