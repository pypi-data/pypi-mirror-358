import os
from abc import abstractmethod

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_file_name_from_config
from dmqclib.utils.path import build_full_data_path


class SummaryStatsBase(DataSetBase):
    """
    Base class to calculate summary stats
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
    ):
        super().__init__("summary", dataset_name, config_file=config_file)

        # Set member variables
        self.default_file_name = "summary_stats.tsv"
        self._build_output_file_name()
        self.input_data = input_data
        self.summary_stats = None

    def _build_output_file_name(self):
        """
        Set the output file based on configuration entries.
        """
        file_name = get_file_name_from_config(
            self.dataset_info, "summary", self.default_file_name
        )

        self.output_file_name = build_full_data_path(
            self.path_info, self.dataset_info, "summary", file_name
        )

    @abstractmethod
    def calculate_stats(self):
        """
        Calculate summary stats.
        """
        pass

    def write_summary_stats(self):
        """
        Write selected profiles to tsv file.
        """
        if self.summary_stats is None:
            raise ValueError("Member variable 'summary_stats' must not be empty.")

        os.makedirs(os.path.dirname(self.output_file_name), exist_ok=True)
        self.summary_stats.write_csv(self.output_file_name, separator="\t")
