import os
from abc import abstractmethod
from typing import Dict

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_target_file_name
from dmqclib.utils.config import get_targets
from dmqclib.utils.path import build_full_data_path


class LocatePositionBase(DataSetBase):
    """
    Base class to identify training data rows
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
        selected_profiles: pl.DataFrame = None,
    ):
        super().__init__("locate", dataset_name, config_file=config_file)

        # Set member variables
        self.default_file_name = "{target_name}_rows.parquet"
        self._build_output_file_names()
        self.input_data = input_data
        self.selected_profiles = selected_profiles
        self.target_rows = {}

    def _build_output_file_names(self):
        """
        Set the output files based on configuration entries.
        """
        targets = get_targets(self.dataset_info, "locate", self.targets)
        self.output_file_names = {
            k: build_full_data_path(
                self.path_info,
                self.dataset_info,
                "locate",
                get_target_file_name(v, k, self.default_file_name),
            )
            for k, v in targets.items()
        }

    def process_targets(self):
        """
        Iterate all targets to locate training data rows.
        """
        targets = get_targets(self.dataset_info, "locate", self.targets)
        for k, v in targets.items():
            self.locate_target_rows(k, v)

    @abstractmethod
    def locate_target_rows(self, target_name: str, target_value: Dict):
        """
        Locate training data rows.
        """
        pass

    def write_target_rows(self):
        """
        Write target_rows to parquet files
        """
        if len(self.target_rows) == 0:
            raise ValueError("Member variable 'target_rows' must not be empty.")

        for k, v in self.target_rows.items():
            os.makedirs(os.path.dirname(self.output_file_names[k]), exist_ok=True)
            v.write_parquet(self.output_file_names[k])
