from typing import Dict

import polars as pl

from dmqclib.common.base.feature_base import FeatureBase
from dmqclib.common.loader.feature_registry import FEATURE_REGISTRY


def _get_feature_class(feature_info: Dict, registry: Dict) -> FeatureBase:
    class_name = feature_info.get("class")
    dataset_class = registry.get(class_name)
    if not dataset_class:
        raise ValueError(f"Unknown dataset class specified: {class_name}")

    return dataset_class


def load_feature_class(
    target_name: str,
    feature_info: Dict,
    selected_profiles: pl.DataFrame = None,
    filtered_input: pl.DataFrame = None,
    target_rows: pl.DataFrame = None,
    summary_stats: pl.DataFrame = None,
) -> FeatureBase:
    """
    Given a label (e.g., 'NRT_BO_001'), look up the class specified in the
    YAML config and instantiate the appropriate class, returning it.
    """
    feature_class = _get_feature_class(feature_info, FEATURE_REGISTRY)

    return feature_class(
        target_name,
        feature_info,
        selected_profiles,
        filtered_input,
        target_rows,
        summary_stats,
    )
