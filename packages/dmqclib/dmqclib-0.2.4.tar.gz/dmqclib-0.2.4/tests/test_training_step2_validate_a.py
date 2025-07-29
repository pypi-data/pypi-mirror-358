import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.training_loader import load_step1_input_training_set
from dmqclib.training.models.empty_model import EmptyModel
from dmqclib.training.step2_validate.kfold_validation import KFoldValidation


class TestKFoldValidation(unittest.TestCase):
    def setUp(self):
        """Set up test environment and load input and selected datasets."""
        self.config_file_path = str(
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

    def test_init_valid_dataset_name(self):
        """Ensure ExtractDataSetA constructs correctly with a valid label."""
        ds = KFoldValidation("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_002")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            KFoldValidation("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = KFoldValidation("NRT_BO_002", str(self.config_file_path))
        self.assertTrue("training.yaml" in ds.config_file_name)

    def test_output_file_names(self):
        """Ensure output file names are set correctly."""
        ds = KFoldValidation("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/temp_validation_result.tsv",
            str(ds.output_file_names["temp"]["result"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/psal_validation_result.tsv",
            str(ds.output_file_names["psal"]["result"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/temp_validation_report.tsv",
            str(ds.output_file_names["temp"]["report"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/psal_validation_report.tsv",
            str(ds.output_file_names["psal"]["report"]),
        )

    def test_base_model(self):
        """Verify the config file is correctly set in the member variable."""
        ds = KFoldValidation("NRT_BO_002", str(self.config_file_path))
        self.assertIsInstance(ds.base_model, EmptyModel)

    def test_training_sets(self):
        """Verify the config file is correctly set in the member variable."""
        ds = KFoldValidation(
            "NRT_BO_002", str(self.config_file_path), self.ds_input.training_sets
        )

        self.assertIsInstance(ds.training_sets["temp"], pl.DataFrame)
        self.assertEqual(ds.training_sets["temp"].shape[0], 116)
        self.assertEqual(ds.training_sets["temp"].shape[1], 38)

        self.assertIsInstance(ds.training_sets["psal"], pl.DataFrame)
        self.assertEqual(ds.training_sets["psal"].shape[0], 126)
        self.assertEqual(ds.training_sets["psal"].shape[1], 38)

    def test_process_targets(self):
        """Verify the config file is correctly set in the member variable."""
        ds = KFoldValidation(
            "NRT_BO_002", str(self.config_file_path), self.ds_input.training_sets
        )

        ds.process_targets()

        self.assertEqual(ds.built_models, {"temp": [1, 2, 3], "psal": [1, 2, 3]})
        self.assertEqual(ds.results, {"temp": [10, 11, 12], "psal": [10, 11, 12]})
        self.assertEqual(ds.reports, {"temp": [20, 21, 22], "psal": [20, 21, 22]})
        self.assertEqual(ds.summarised_results, {"temp": 100, "psal": 100})
        self.assertEqual(ds.summarised_reports, {"temp": 200, "psal": 200})

    def test_xgboost(self):
        """Verify the config file is correctly set in the member variable."""
        ds = KFoldValidation(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.training_sets
        )

        ds.process_targets()

        self.assertIsInstance(ds.summarised_results["temp"], pl.DataFrame)
        self.assertEqual(ds.summarised_results["temp"].shape[0], 3)
        self.assertEqual(ds.summarised_results["temp"].shape[1], 3)

        self.assertIsInstance(ds.summarised_results["psal"], pl.DataFrame)
        self.assertEqual(ds.summarised_results["psal"].shape[0], 3)
        self.assertEqual(ds.summarised_results["psal"].shape[1], 3)

        self.assertIsInstance(ds.summarised_reports["temp"], pl.DataFrame)
        self.assertEqual(ds.summarised_reports["temp"].shape[0], 12)
        self.assertEqual(ds.summarised_reports["temp"].shape[1], 6)

        self.assertIsInstance(ds.summarised_reports["psal"], pl.DataFrame)
        self.assertEqual(ds.summarised_reports["psal"].shape[0], 12)
        self.assertEqual(ds.summarised_reports["psal"].shape[1], 6)

    def test_write_results(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = KFoldValidation(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.training_sets
        )

        data_path = Path(__file__).resolve().parent / "data" / "training"
        ds.output_file_names["temp"]["result"] = (
            data_path / "temp_temp_validation_result.tsv"
        )
        ds.output_file_names["psal"]["result"] = (
            data_path / "temp_psal_validation_result.tsv"
        )

        ds.process_targets()
        ds.write_results()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]["result"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]["result"]))
        os.remove(ds.output_file_names["temp"]["result"])
        os.remove(ds.output_file_names["psal"]["result"])

    def test_write_reports(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = KFoldValidation(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.training_sets
        )

        data_path = Path(__file__).resolve().parent / "data" / "training"
        ds.output_file_names["temp"]["report"] = (
            data_path / "temp_temp_validation_report.tsv"
        )
        ds.output_file_names["psal"]["report"] = (
            data_path / "temp_psal_validation_report.tsv"
        )

        ds.process_targets()
        ds.write_reports()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]["report"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]["report"]))
        os.remove(ds.output_file_names["temp"]["report"])
        os.remove(ds.output_file_names["psal"]["report"])
