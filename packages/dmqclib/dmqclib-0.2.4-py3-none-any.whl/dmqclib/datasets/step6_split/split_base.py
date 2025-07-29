import os
from abc import abstractmethod

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_target_file_name
from dmqclib.utils.config import get_targets
from dmqclib.utils.path import build_full_data_path


class SplitDataSetBase(DataSetBase):
    """
    Base class to identify training data rows
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        target_features: pl.DataFrame = None,
    ):
        super().__init__("split", dataset_name, config_file=config_file)

        # Set member variables
        self.default_file_names = {
            "train": "{target_name}_train.parquet",
            "test": "{target_name}_test.parquet",
        }
        self._build_output_file_names()
        self.target_features = target_features
        self.training_sets = {}
        self.test_sets = {}

        self.test_set_fraction = 0.1
        self.k_fold = 10

    def _build_output_file_names(self):
        """
        Set the output files based on configuration entries.
        """
        targets = get_targets(self.dataset_info, "split", self.targets)
        self.output_file_names = {
            k1: {
                k2: build_full_data_path(
                    self.path_info,
                    self.dataset_info,
                    "split",
                    get_target_file_name(v1, k1, v2),
                )
                for k2, v2 in self.default_file_names.items()
            }
            for k1, v1 in targets.items()
        }

    def _get_test_set_fraction(self) -> str:
        if (
            "split" in self.dataset_info
            and "test_set_fraction" in self.dataset_info["split"]
        ):
            test_set_fraction = self.dataset_info["split"].get(
                "test_set_fraction", self.test_set_fraction
            )
        else:
            test_set_fraction = self.test_set_fraction

        return test_set_fraction

    def _get_k_fold(self) -> str:
        if "split" in self.dataset_info and "k_fold" in self.dataset_info["split"]:
            k_fold = self.dataset_info["split"].get("k_fold", self.k_fold)
        else:
            k_fold = self.k_fold

        return k_fold

    def process_targets(self):
        """
        Iterate all targets to locate training data rows.
        """
        targets = get_targets(self.dataset_info, "split", self.targets)
        for k in targets.keys():
            self.split_test_set(k)
            self.add_k_fold(k)
            self.drop_columns(k)

    @abstractmethod
    def split_test_set(self, target_name: str):
        pass

    @abstractmethod
    def add_k_fold(self, target_name: str):
        pass

    @abstractmethod
    def drop_columns(self, target_name: str):
        pass

    def write_training_sets(self):
        """
        Write training sets to parquet files
        """
        if len(self.training_sets) == 0:
            raise ValueError("Member variable 'training_sets' must not be empty.")

        for k, v in self.training_sets.items():
            os.makedirs(
                os.path.dirname(self.output_file_names[k]["train"]), exist_ok=True
            )
            v.write_parquet(self.output_file_names[k]["train"])

    def write_test_sets(self):
        """
        Write test sets to parquet files
        """
        if len(self.test_sets) == 0:
            raise ValueError("Member variable 'test_sets' must not be empty.")

        for k, v in self.test_sets.items():
            os.makedirs(
                os.path.dirname(self.output_file_names[k]["test"]), exist_ok=True
            )
            v.write_parquet(self.output_file_names[k]["test"])

    def write_data_sets(self):
        """
        Write both training and test sets
        """

        self.write_test_sets()
        self.write_training_sets()
