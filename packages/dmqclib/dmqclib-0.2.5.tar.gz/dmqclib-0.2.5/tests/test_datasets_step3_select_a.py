import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.datasets.step3_select.dataset_a import SelectDataSetA


class TestSelectDataSetA(unittest.TestCase):
    def setUp(self):
        """Set up test environment and load input dataset."""
        self.config_file_path = str(
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )
        self.ds = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        self.ds.input_file_name = str(self.test_data_file)
        self.ds.read_input_data()

    def test_init_valid_dataset_name(self):
        """Ensure SelectDataSetA constructs correctly with a valid label."""
        ds = SelectDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for invalid label."""
        with self.assertRaises(ValueError):
            SelectDataSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly assigned."""
        ds = SelectDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_output_file_name(self):
        """Ensure output file name is set correctly."""
        ds = SelectDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data3/nrt_bo_001_test/select/selected_profiles2.parquet",
            str(ds.output_file_name),
        )

    def test_default_output_file_name(self):
        """Ensure output file name is set correctly."""
        ds = SelectDataSetA("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data3/nrt_bo_002/select/selected_profiles.parquet",
            str(ds.output_file_name),
        )

    def test_input_data(self):
        """Ensure input data is set correctly."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

    def test_positive_profiles(self):
        """Ensure positive profiles are selected correctly."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.select_positive_profiles()
        self.assertIsInstance(ds.pos_profile_df, pl.DataFrame)
        self.assertEqual(ds.pos_profile_df.shape[0], 25)
        self.assertEqual(ds.pos_profile_df.shape[1], 7)

    def test_negative_profiles(self):
        """Ensure negative profiles are selected correctly."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.select_positive_profiles()
        ds.select_negative_profiles()
        self.assertIsInstance(ds.neg_profile_df, pl.DataFrame)
        self.assertEqual(ds.neg_profile_df.shape[0], 478)
        self.assertEqual(ds.neg_profile_df.shape[1], 7)

    def test_find_profile_pairs(self):
        """Ensure profile pairs are found correctly."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.select_positive_profiles()
        ds.select_negative_profiles()
        ds.find_profile_pairs()
        self.assertEqual(ds.pos_profile_df.shape[0], 25)
        self.assertEqual(ds.pos_profile_df.shape[1], 8)
        self.assertEqual(ds.neg_profile_df.shape[0], 19)
        self.assertEqual(ds.neg_profile_df.shape[1], 8)

    def test_label_profiles(self):
        """Ensure profiles are labeled correctly in the dataset."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.label_profiles()
        self.assertEqual(ds.selected_profiles.shape[0], 44)
        self.assertEqual(ds.selected_profiles.shape[1], 8)

    def test_write_selected_profiles(self):
        """Ensure selected profiles are written to parquet file correctly."""
        ds = SelectDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.output_file_name = (
            Path(__file__).resolve().parent
            / "data"
            / "select"
            / "temp_selected_profiles.parquet"
        )

        ds.label_profiles()
        ds.write_selected_profiles()
        self.assertTrue(os.path.exists(ds.output_file_name))
        os.remove(ds.output_file_name)
