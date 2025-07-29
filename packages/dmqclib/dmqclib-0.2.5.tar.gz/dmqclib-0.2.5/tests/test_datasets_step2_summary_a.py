import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.datasets.step2_summary.dataset_a import SummaryDataSetA


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
        ds = SummaryDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for invalid label."""
        with self.assertRaises(ValueError):
            SummaryDataSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly assigned."""
        ds = SummaryDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_output_file_name(self):
        """Ensure output file name is set correctly."""
        ds = SummaryDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/summary/summary_stats.tsv",
            str(ds.output_file_name),
        )

    def test_default_output_file_name(self):
        """Ensure output file name is set correctly."""
        ds = SummaryDataSetA("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data1/nrt_bo_002/summary/summary_stats.tsv",
            str(ds.output_file_name),
        )

    def test_input_data(self):
        """Ensure input data is set correctly."""
        ds = SummaryDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

    def test_global_stats(self):
        """Ensure negative profiles are selected correctly."""
        ds = SummaryDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        df = ds.calculate_global_stats("temp")
        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.shape[1], 12)

    def test_profile_stats(self):
        """Ensure profile pairs are found correctly."""
        ds = SummaryDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        grouped_df = ds.input_data.group_by(ds.profile_col_names)
        df = ds.calculate_profile_stats(grouped_df, "temp")
        self.assertEqual(df.shape[0], 503)
        self.assertEqual(df.shape[1], 12)

    def test_summary_stats(self):
        """Ensure profile pairs are found correctly."""
        ds = SummaryDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.calculate_stats()
        self.assertEqual(ds.summary_stats.shape[0], 3528)
        self.assertEqual(ds.summary_stats.shape[1], 12)

    def test_write_summary_stats(self):
        """Ensure selected profiles are written to parquet file correctly."""
        ds = SummaryDataSetA(
            "NRT_BO_001", str(self.config_file_path), self.ds.input_data
        )
        ds.output_file_name = (
            Path(__file__).resolve().parent
            / "data"
            / "summary"
            / "temp_summary_stats.tsv"
        )

        ds.calculate_stats()
        ds.write_summary_stats()
        self.assertTrue(os.path.exists(ds.output_file_name))
        os.remove(ds.output_file_name)
