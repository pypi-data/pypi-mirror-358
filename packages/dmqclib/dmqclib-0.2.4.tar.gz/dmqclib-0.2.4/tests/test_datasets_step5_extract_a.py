import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.common.loader.dataset_loader import load_step2_summary_dataset
from dmqclib.common.loader.dataset_loader import load_step3_select_dataset
from dmqclib.common.loader.dataset_loader import load_step4_locate_dataset
from dmqclib.datasets.step5_extract.dataset_a import ExtractDataSetA


class TestExtractDataSetA(unittest.TestCase):
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

    def test_init_valid_dataset_name(self):
        """Ensure ExtractDataSetA constructs correctly with a valid label."""
        ds = ExtractDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            ExtractDataSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = ExtractDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_output_file_names(self):
        """Ensure output file names are set correctly."""
        ds = ExtractDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/extract/temp_features.parquet",
            str(ds.output_file_names["temp"]),
        )
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/extract/psal_features.parquet",
            str(ds.output_file_names["psal"]),
        )

    def test_init_arguments(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = ExtractDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )

        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

        self.assertIsInstance(ds.summary_stats, pl.DataFrame)
        self.assertEqual(ds.summary_stats.shape[0], 3528)
        self.assertEqual(ds.summary_stats.shape[1], 12)

        self.assertIsInstance(ds.selected_profiles, pl.DataFrame)
        self.assertEqual(ds.selected_profiles.shape[0], 44)
        self.assertEqual(ds.selected_profiles.shape[1], 8)

        self.assertIsInstance(ds.filtered_input, pl.DataFrame)
        self.assertEqual(ds.filtered_input.shape[0], 9841)
        self.assertEqual(ds.filtered_input.shape[1], 30)

        self.assertIsInstance(ds.target_rows["temp"], pl.DataFrame)
        self.assertEqual(ds.target_rows["temp"].shape[0], 128)
        self.assertEqual(ds.target_rows["temp"].shape[1], 9)

        self.assertIsInstance(ds.target_rows["psal"], pl.DataFrame)
        self.assertEqual(ds.target_rows["psal"].shape[0], 140)
        self.assertEqual(ds.target_rows["psal"].shape[1], 9)

    def test_location_features(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = ExtractDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )

        ds.process_targets()

        self.assertIsInstance(ds.target_features["temp"], pl.DataFrame)
        self.assertEqual(ds.target_features["temp"].shape[0], 128)
        self.assertEqual(ds.target_features["temp"].shape[1], 43)

        self.assertIsInstance(ds.target_features["psal"], pl.DataFrame)
        self.assertEqual(ds.target_features["psal"].shape[0], 140)
        self.assertEqual(ds.target_features["psal"].shape[1], 43)

    def test_write_target_features(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = ExtractDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )
        data_path = Path(__file__).resolve().parent / "data" / "extract"
        ds.output_file_names["temp"] = data_path / "temp_temp_features.parquet"
        ds.output_file_names["psal"] = data_path / "temp_psal_features.parquet"

        ds.process_targets()
        ds.write_target_features()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]))
        os.remove(ds.output_file_names["temp"])
        os.remove(ds.output_file_names["psal"])
