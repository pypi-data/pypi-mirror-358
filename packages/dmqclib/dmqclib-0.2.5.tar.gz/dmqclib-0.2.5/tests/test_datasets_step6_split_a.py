import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.common.loader.dataset_loader import load_step2_summary_dataset
from dmqclib.common.loader.dataset_loader import load_step3_select_dataset
from dmqclib.common.loader.dataset_loader import load_step4_locate_dataset
from dmqclib.common.loader.dataset_loader import load_step5_extract_dataset
from dmqclib.datasets.step6_split.dataset_a import SplitDataSetA


class TestSplitDataSetA(unittest.TestCase):
    def setUp(self):
        """Set up test environment and load input and selected datasets."""
        self.config_file_path = str(
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )
        self.ds_input = load_step1_input_dataset(
            "NRT_BO_001", str(self.config_file_path)
        )
        self.ds_input.input_file_name = str(self.test_data_file)
        self.ds_input.read_input_data()

        self.ds_summary = load_step2_summary_dataset(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.input_data
        )
        self.ds_summary.calculate_stats()

        self.ds_select = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.input_data
        )
        self.ds_select.label_profiles()

        self.ds_locate = load_step4_locate_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )
        self.ds_locate.process_targets()

        self.ds_extract = load_step5_extract_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )
        self.ds_extract.process_targets()

    def test_init_valid_dataset_name(self):
        """Ensure LocateDataSetA constructs correctly with a valid label."""
        ds = SplitDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            SplitDataSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = SplitDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_output_file_names(self):
        """Ensure output file names are set correctly."""
        ds = SplitDataSetA("NRT_BO_001", str(self.config_file_path))

        self.assertEqual(
            "/path/to/data1/nrt_bo_001/training/temp_train.parquet",
            str(ds.output_file_names["temp"]["train"]),
        )
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/training/psal_train.parquet",
            str(ds.output_file_names["psal"]["train"]),
        )
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/training/temp_test.parquet",
            str(ds.output_file_names["temp"]["test"]),
        )
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/training/psal_test.parquet",
            str(ds.output_file_names["psal"]["test"]),
        )

    def test_target_features_data(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = SplitDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_extract.target_features,
        )

        self.assertIsInstance(ds.target_features["temp"], pl.DataFrame)
        self.assertEqual(ds.target_features["temp"].shape[0], 128)
        self.assertEqual(ds.target_features["temp"].shape[1], 43)

        self.assertIsInstance(ds.target_features["psal"], pl.DataFrame)
        self.assertEqual(ds.target_features["psal"].shape[0], 140)
        self.assertEqual(ds.target_features["psal"].shape[1], 43)

    def test_split_features_data(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = SplitDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_extract.target_features,
        )

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

    def test_write_training_sets(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = SplitDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_extract.target_features,
        )

        ds.process_targets()

        data_path = Path(__file__).resolve().parent / "data" / "training"
        ds.output_file_names["temp"]["train"] = data_path / "temp_temp_train.parquet"
        ds.output_file_names["psal"]["train"] = data_path / "temp_psal_train.parquet"

        ds.process_targets()
        ds.write_training_sets()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]["train"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]["train"]))
        os.remove(ds.output_file_names["temp"]["train"])
        os.remove(ds.output_file_names["psal"]["train"])

    def test_write_test_sets(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = SplitDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_extract.target_features,
        )

        ds.process_targets()

        data_path = Path(__file__).resolve().parent / "data" / "training"
        ds.output_file_names["temp"]["test"] = data_path / "temp_temp_test.parquet"
        ds.output_file_names["psal"]["test"] = data_path / "temp_psal_test.parquet"

        ds.process_targets()
        ds.write_test_sets()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]["test"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]["test"]))
        os.remove(ds.output_file_names["temp"]["test"])
        os.remove(ds.output_file_names["psal"]["test"])
