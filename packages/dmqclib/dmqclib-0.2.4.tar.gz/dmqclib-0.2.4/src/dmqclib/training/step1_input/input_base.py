import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_target_file_name
from dmqclib.utils.config import get_targets
from dmqclib.utils.path import build_full_data_path


class InputTrainingSetBase(DataSetBase):
    """
    Base class to import training data sets
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
    ):
        super().__init__(
            "input",
            dataset_name,
            config_file=config_file,
            config_file_name="training.yaml",
        )

        # Set member variables
        self.default_file_names = {
            "train": "{target_name}_train.parquet",
            "test": "{target_name}_test.parquet",
        }
        self._build_input_file_names()
        self.training_sets = {}
        self.test_sets = {}

    def _build_input_file_names(self):
        """
        Set the input files based on configuration entries.
        """
        targets = get_targets(self.dataset_info, "input", self.targets)
        self.input_file_names = {
            k1: {
                k2: build_full_data_path(
                    self.path_info,
                    self.dataset_info,
                    "input",
                    get_target_file_name(v1, k1, v2),
                )
                for k2, v2 in self.default_file_names.items()
            }
            for k1, v1 in targets.items()
        }

    def process_targets(self):
        """
        Iterate all targets to locate training data rows.
        """
        targets = get_targets(self.dataset_info, "input", self.targets)
        for k in targets.keys():
            self.read_training_set(k)
            self.read_test_sets(k)

    def read_training_set(self, target_name: str):
        """
        Read training set from parquet file
        """
        self.training_sets[target_name] = pl.read_parquet(
            self.input_file_names[target_name]["train"]
        )

    def read_test_sets(self, target_name: str):
        """
        Read test set from parquet files
        """
        self.test_sets[target_name] = pl.read_parquet(
            self.input_file_names[target_name]["test"]
        )
