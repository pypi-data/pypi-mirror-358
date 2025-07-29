import os
from abc import abstractmethod

import polars as pl

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.common.loader.model_loader import load_model_class
from dmqclib.utils.config import get_target_file_name
from dmqclib.utils.config import get_targets
from dmqclib.utils.path import build_full_data_path


class ValidationBase(DataSetBase):
    """
    Base class for validation classes.
    """

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        training_sets: pl.DataFrame = None,
    ):
        super().__init__(
            "validate",
            dataset_name,
            config_file=config_file,
            config_file_name="training.yaml",
        )

        base_model = load_model_class(dataset_name, config_file)

        # Set member variables
        self.default_file_names = {
            "result": "{target_name}_validation_result.tsv",
            "report": "{target_name}_validation_report.tsv",
        }
        self._build_output_file_names()
        self.training_sets = training_sets

        self.base_model = base_model
        self.built_models = {}
        self.results = {}
        self.reports = {}
        self.summarised_results = {}
        self.summarised_reports = {}

    def _build_output_file_names(self):
        """
        Set the output files based on configuration entries.
        """
        targets = get_targets(self.dataset_info, "validate", self.targets)
        self.output_file_names = {
            k1: {
                k2: build_full_data_path(
                    self.path_info,
                    self.dataset_info,
                    "validate",
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
        targets = get_targets(self.dataset_info, "validate", self.targets)
        for k in targets.keys():
            self.validate(k)
            self.summarise(k)
            self.base_model.clear()

    @abstractmethod
    def validate(self, target_name: str):
        """
        Validate models
        """
        pass

    @abstractmethod
    def summarise(self, target_name: str):
        """
        Summarise results
        """
        pass

    def write_results(self):
        """
        Write results
        """
        if len(self.summarised_results) == 0:
            raise ValueError("Member variable 'summarised_results' must not be empty.")

        for k, v in self.summarised_results.items():
            os.makedirs(
                os.path.dirname(self.output_file_names[k]["result"]), exist_ok=True
            )
            v.write_csv(self.output_file_names[k]["result"], separator="\t")

    def write_reports(self):
        """
        Write test sets to parquet files
        """
        if len(self.summarised_reports) == 0:
            raise ValueError("Member variable 'summarised_reports' must not be empty.")

        for k, v in self.summarised_reports.items():
            os.makedirs(
                os.path.dirname(self.output_file_names[k]["report"]), exist_ok=True
            )
            v.write_csv(self.output_file_names[k]["report"], separator="\t")

    def write_all_results(self):
        """
        Write both results and reports
        """
        self.write_results()
        self.write_reports()
