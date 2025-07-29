import os
from abc import abstractmethod

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_file_name_from_config
from dmqclib.utils.path import build_full_data_path


class ProfileSelectionBase(DataSetBase):
    """
    Base class for profile selection and group labeling classes
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
    ):
        super().__init__("select", dataset_name, config_file=config_file)

        # Set member variables
        self.default_file_name = "selected_profiles.parquet"
        self._build_output_file_name()
        self.input_data = input_data
        self.selected_profiles = None

    def _build_output_file_name(self):
        """
        Set the output file based on configuration entries.
        """
        file_name = get_file_name_from_config(
            self.dataset_info, "select", self.default_file_name
        )

        self.output_file_name = build_full_data_path(
            self.path_info, self.dataset_info, "select", file_name
        )

    @abstractmethod
    def label_profiles(self):
        """
        Label profiles to identify positive and negative groups.
        """
        pass

    def write_selected_profiles(self):
        """
        Write selected profiles to parquet file
        """
        if self.selected_profiles is None:
            raise ValueError("Member variable 'selected_profiles' must not be empty.")

        os.makedirs(os.path.dirname(self.output_file_name), exist_ok=True)
        self.selected_profiles.write_parquet(self.output_file_name)
