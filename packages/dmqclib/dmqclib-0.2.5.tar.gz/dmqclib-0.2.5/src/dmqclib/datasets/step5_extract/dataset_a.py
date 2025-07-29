import polars as pl

from dmqclib.datasets.step5_extract.extract_base import ExtractFeatureBase


class ExtractDataSetA(ExtractFeatureBase):
    """
    ExtractDataSetA extracts features from BO NRT+Cora test data.
    """

    expected_class_name = "ExtractDataSetA"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
        selected_profiles: pl.DataFrame = None,
        target_rows: pl.DataFrame = None,
        summary_stats: pl.DataFrame = None,
    ):
        super().__init__(
            dataset_name,
            config_file=config_file,
            input_data=input_data,
            selected_profiles=selected_profiles,
            target_rows=target_rows,
            summary_stats=summary_stats,
        )
