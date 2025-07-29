import os
import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.common.loader.dataset_loader import load_step3_select_dataset
from dmqclib.datasets.step4_locate.dataset_a import LocateDataSetA


class TestLocateDataSetA(unittest.TestCase):
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

        self.ds_select = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), self.ds_input.input_data
        )
        self.ds_select.label_profiles()

    def test_init_valid_dataset_name(self):
        """Ensure LocateDataSetA constructs correctly with a valid label."""
        ds = LocateDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            LocateDataSetA("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = LocateDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_output_file_names(self):
        """Ensure output file names are set correctly."""
        ds = LocateDataSetA("NRT_BO_001", str(self.config_file_path))
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/select/temp_rows.parquet",
            str(ds.output_file_names["temp"]),
        )
        self.assertEqual(
            "/path/to/data1/nrt_bo_001/select/psal_rows.parquet",
            str(ds.output_file_names["psal"]),
        )

    def test_input_data_and_selected_profiles(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = LocateDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )

        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

        self.assertIsInstance(ds.selected_profiles, pl.DataFrame)
        self.assertEqual(ds.selected_profiles.shape[0], 44)
        self.assertEqual(ds.selected_profiles.shape[1], 8)

    def test_positive_rows(self):
        """Ensure positive row data is set correctly."""
        ds = LocateDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )
        ds.select_positive_rows("temp", {"variable": "temp_qc"})
        ds.select_positive_rows("psal", {"variable": "psal_qc"})

        self.assertIsInstance(ds.positive_rows["temp"], pl.DataFrame)
        self.assertEqual(ds.positive_rows["temp"].shape[0], 64)
        self.assertEqual(ds.positive_rows["temp"].shape[1], 11)

        self.assertIsInstance(ds.positive_rows["psal"], pl.DataFrame)
        self.assertEqual(ds.positive_rows["psal"].shape[0], 70)
        self.assertEqual(ds.positive_rows["psal"].shape[1], 11)

    def test_negative_rows(self):
        """Ensure negative row data is set correctly."""
        ds = LocateDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )
        ds.select_positive_rows("temp", {"variable": "temp_qc"})
        ds.select_positive_rows("psal", {"variable": "psal_qc"})
        ds.select_negative_rows("temp", {"variable": "temp_qc"})
        ds.select_negative_rows("psal", {"variable": "psal_qc"})

        self.assertIsInstance(ds.negative_rows["temp"], pl.DataFrame)
        self.assertEqual(ds.negative_rows["temp"].shape[0], 64)
        self.assertEqual(ds.negative_rows["temp"].shape[1], 11)

        self.assertIsInstance(ds.negative_rows["psal"], pl.DataFrame)
        self.assertEqual(ds.negative_rows["psal"].shape[0], 70)
        self.assertEqual(ds.negative_rows["psal"].shape[1], 11)

    def test_target_rows(self):
        """Ensure target rows are selected and set correctly."""
        ds = LocateDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )

        ds.process_targets()

        self.assertIsInstance(ds.target_rows["temp"], pl.DataFrame)
        self.assertEqual(ds.target_rows["temp"].shape[0], 128)
        self.assertEqual(ds.target_rows["temp"].shape[1], 9)

        self.assertIsInstance(ds.target_rows["psal"], pl.DataFrame)
        self.assertEqual(ds.target_rows["psal"].shape[0], 140)
        self.assertEqual(ds.target_rows["psal"].shape[1], 9)

    def test_write_target_rows(self):
        """Ensure target rows are written to parquet files correctly."""
        ds = LocateDataSetA(
            "NRT_BO_001",
            str(self.config_file_path),
            self.ds_input.input_data,
            self.ds_select.selected_profiles,
        )
        data_path = Path(__file__).resolve().parent / "data" / "select"
        ds.output_file_names["temp"] = data_path / "temp_temp_rows.parquet"
        ds.output_file_names["psal"] = data_path / "temp_psal_rows.parquet"

        ds.process_targets()
        ds.write_target_rows()

        self.assertTrue(os.path.exists(ds.output_file_names["temp"]))
        self.assertTrue(os.path.exists(ds.output_file_names["psal"]))
        os.remove(ds.output_file_names["temp"])
        os.remove(ds.output_file_names["psal"])
