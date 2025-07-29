import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.training_loader import load_step1_input_training_set
from dmqclib.common.loader.training_loader import load_step2_model_validation_class
from dmqclib.training.step1_input.dataset_a import InputTrainingSetA
from dmqclib.training.step2_validate.kfold_validation import KFoldValidation


class TestTrainingInputClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "training.yaml"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of InputDataSetA for the known label.
        """
        ds = load_step1_input_training_set("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, InputTrainingSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step1_input_training_set(
                "NON_EXISTENT_LABEL", str(self.config_file_path)
            )


class TestModelValidationClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "training.yaml"
        )
        data_path = Path(__file__).resolve().parent / "data" / "training"
        self.input_file_names = {
            "temp": {
                "train": str(data_path / "temp_train.parquet"),
                "test": str(data_path / "temp_test.parquet"),
            },
            "psal": {
                "train": str(data_path / "psal_train.parquet"),
                "test": str(data_path / "psal_test.parquet"),
            },
        }

        self.ds_input = load_step1_input_training_set(
            "NRT_BO_002", str(self.config_file_path)
        )
        self.ds_input.input_file_names = self.input_file_names
        self.ds_input.process_targets()

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of InputDataSetA for the known label.
        """
        ds = load_step2_model_validation_class("NRT_BO_002", str(self.config_file_path))
        self.assertIsInstance(ds, KFoldValidation)
        self.assertEqual(ds.dataset_name, "NRT_BO_002")

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step2_model_validation_class(
                "NON_EXISTENT_LABEL", str(self.config_file_path)
            )

    def test_training_set_data(self):
        """
        Test that load_dataset returns an instance of SummaryDataSetA with correct input_data.
        """

        ds = load_step2_model_validation_class(
            "NRT_BO_002", str(self.config_file_path), self.ds_input.training_sets
        )

        self.assertIsInstance(ds.training_sets["temp"], pl.DataFrame)
        self.assertEqual(ds.training_sets["temp"].shape[0], 116)
        self.assertEqual(ds.training_sets["temp"].shape[1], 38)

        self.assertIsInstance(ds.training_sets["psal"], pl.DataFrame)
        self.assertEqual(ds.training_sets["psal"].shape[0], 126)
        self.assertEqual(ds.training_sets["psal"].shape[1], 38)
