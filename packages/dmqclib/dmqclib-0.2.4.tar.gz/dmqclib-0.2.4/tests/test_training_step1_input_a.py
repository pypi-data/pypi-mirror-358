import unittest
from pathlib import Path

import polars as pl

from dmqclib.training.step1_input.dataset_a import InputTrainingSetA


class TestInputTrainingSetA(unittest.TestCase):
    def setUp(self):
        """Set up test environment and load input and selected datasets."""
        self.config_file_path = str(
            Path(__file__).resolve().parent / "data" / "config" / "training.yaml"
        )
        data_path = Path(__file__).resolve().parent / "data" / "training"
        self.input_file_names = {
            "temp": {
                "train": data_path / "temp_train.parquet",
                "test": data_path / "temp_test.parquet",
            },
            "psal": {
                "train": data_path / "psal_train.parquet",
                "test": data_path / "psal_test.parquet",
            },
        }

    def test_init_valid_dataset_name(self):
        """Ensure ExtractDataSetA constructs correctly with a valid label."""
        ds = InputTrainingSetA("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_002")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            InputTrainingSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = InputTrainingSetA("NRT_BO_002", str(self.config_file_path))
        self.assertTrue("training.yaml" in ds.config_file_name)

    def test_input_file_names(self):
        """Ensure output file names are set correctly."""
        ds = InputTrainingSetA("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/temp_train.parquet",
            str(ds.input_file_names["temp"]["train"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/psal_train.parquet",
            str(ds.input_file_names["psal"]["train"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/temp_test.parquet",
            str(ds.input_file_names["temp"]["test"]),
        )
        self.assertEqual(
            "/path/to/data/nrt_bo_002/training/psal_test.parquet",
            str(ds.input_file_names["psal"]["test"]),
        )

    def test_read_files(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = InputTrainingSetA("NRT_BO_002", str(self.config_file_path))
        ds.input_file_names = self.input_file_names

        ds.process_targets()

        self.assertIsInstance(ds.training_sets["temp"], pl.DataFrame)
        self.assertEqual(ds.training_sets["temp"].shape[0], 116)
        self.assertEqual(ds.training_sets["temp"].shape[1], 38)

        self.assertIsInstance(ds.test_sets["temp"], pl.DataFrame)
        self.assertEqual(ds.test_sets["temp"].shape[0], 12)
        self.assertEqual(ds.test_sets["temp"].shape[1], 37)

        self.assertIsInstance(ds.training_sets["psal"], pl.DataFrame)
        self.assertEqual(ds.training_sets["psal"].shape[0], 126)
        self.assertEqual(ds.training_sets["psal"].shape[1], 38)

        self.assertIsInstance(ds.test_sets["psal"], pl.DataFrame)
        self.assertEqual(ds.test_sets["psal"].shape[0], 14)
        self.assertEqual(ds.test_sets["psal"].shape[1], 37)
