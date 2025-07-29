import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.common.loader.dataset_loader import load_step2_summary_dataset
from dmqclib.common.loader.dataset_loader import load_step3_select_dataset
from dmqclib.common.loader.dataset_loader import load_step4_locate_dataset
from dmqclib.common.loader.dataset_loader import load_step5_extract_dataset
from dmqclib.common.loader.dataset_loader import load_step6_split_dataset
from dmqclib.datasets.step1_input.dataset_a import InputDataSetA
from dmqclib.datasets.step2_summary.dataset_a import SummaryDataSetA
from dmqclib.datasets.step3_select.dataset_a import SelectDataSetA
from dmqclib.datasets.step4_locate.dataset_a import LocateDataSetA
from dmqclib.datasets.step5_extract.dataset_a import ExtractDataSetA
from dmqclib.datasets.step6_split.dataset_a import SplitDataSetA


class TestInputClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of InputDataSetA for the known label.
        """
        ds = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, InputDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step1_input_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))


class TestSummaryClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of SummaryDataSetA for the known label.
        """
        ds = load_step2_summary_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, SummaryDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_input_data(self):
        """
        Test that load_dataset returns an instance of SummaryDataSetA with correct input_data.
        """
        ds_input = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        ds_input.input_file_name = str(self.test_data_file)
        ds_input.read_input_data()

        ds = load_step2_summary_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        self.assertIsInstance(ds, SummaryDataSetA)
        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step2_summary_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))


class TestSelectClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of SelectDataSetA for the known label.
        """
        ds = load_step3_select_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, SelectDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_input_data(self):
        """
        Test that load_dataset returns an instance of SelectDataSetA with correct input_data.
        """
        ds_input = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        ds_input.input_file_name = str(self.test_data_file)
        ds_input.read_input_data()

        ds = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        self.assertIsInstance(ds, SelectDataSetA)
        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step3_select_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))


class TestLocateClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA for the known label.
        """
        ds = load_step4_locate_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, LocateDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_input_data_and_profiles(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA with correct input_data and selected profiles.
        """
        ds_input = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        ds_input.input_file_name = str(self.test_data_file)
        ds_input.read_input_data()

        ds_select = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        ds_select.label_profiles()

        ds = load_step4_locate_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            ds_input.input_data,
            ds_select.selected_profiles,
        )

        self.assertIsInstance(ds, LocateDataSetA)

        self.assertIsInstance(ds.input_data, pl.DataFrame)
        self.assertEqual(ds.input_data.shape[0], 132342)
        self.assertEqual(ds.input_data.shape[1], 30)

        self.assertIsInstance(ds.selected_profiles, pl.DataFrame)
        self.assertEqual(ds.selected_profiles.shape[0], 44)
        self.assertEqual(ds.selected_profiles.shape[1], 8)

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step4_locate_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))


class TestExtractClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA for the known label.
        """
        ds = load_step5_extract_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, ExtractDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_input_data_and_profiles(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA with correct input_data and selected profiles.
        """
        ds_input = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        ds_input.input_file_name = str(self.test_data_file)
        ds_input.read_input_data()

        ds_select = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        ds_select.label_profiles()

        ds_summary = load_step2_summary_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        ds_summary.calculate_stats()

        ds_locate = load_step4_locate_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            ds_input.input_data,
            ds_select.selected_profiles,
        )
        ds_locate.process_targets()

        ds = load_step5_extract_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            ds_input.input_data,
            ds_select.selected_profiles,
            ds_locate.target_rows,
            ds_summary.summary_stats,
        )

        self.assertIsInstance(ds, ExtractDataSetA)

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

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step5_extract_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))


class TestSplitClassLoader(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def test_load_dataset_valid_label(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA for the known label.
        """
        ds = load_step6_split_dataset("NRT_BO_001", str(self.config_file_path))
        self.assertIsInstance(ds, SplitDataSetA)
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_load_dataset_input_data(self):
        """
        Test that load_dataset returns an instance of LocateDataSetA with correct input_data and selected profiles.
        """
        ds_input = load_step1_input_dataset("NRT_BO_001", str(self.config_file_path))
        ds_input.input_file_name = str(self.test_data_file)
        ds_input.read_input_data()

        ds_select = load_step3_select_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        ds_select.label_profiles()

        ds_summary = load_step2_summary_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_input.input_data
        )
        ds_summary.calculate_stats()

        ds_locate = load_step4_locate_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            ds_input.input_data,
            ds_select.selected_profiles,
        )
        ds_locate.process_targets()

        ds_extract = load_step5_extract_dataset(
            "NRT_BO_001",
            str(self.config_file_path),
            ds_input.input_data,
            ds_select.selected_profiles,
            ds_locate.target_rows,
            ds_summary.summary_stats,
        )
        ds_extract.process_targets()

        ds = load_step6_split_dataset(
            "NRT_BO_001", str(self.config_file_path), ds_extract.target_features
        )

        self.assertIsInstance(ds, SplitDataSetA)

        self.assertIsInstance(ds.target_features["temp"], pl.DataFrame)
        self.assertEqual(ds.target_features["temp"].shape[0], 128)
        self.assertEqual(ds.target_features["temp"].shape[1], 43)

        self.assertIsInstance(ds.target_features["psal"], pl.DataFrame)
        self.assertEqual(ds.target_features["psal"].shape[0], 140)
        self.assertEqual(ds.target_features["psal"].shape[1], 43)

    def test_load_dataset_invalid_label(self):
        """
        Test that calling load_dataset with an invalid label raises a ValueError.
        """
        with self.assertRaises(ValueError):
            load_step6_split_dataset("NON_EXISTENT_LABEL", str(self.config_file_path))
