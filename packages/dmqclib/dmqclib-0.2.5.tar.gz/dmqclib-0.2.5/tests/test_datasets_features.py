import unittest
from pathlib import Path

import polars as pl

from dmqclib.common.loader.dataset_loader import load_step1_input_dataset
from dmqclib.common.loader.dataset_loader import load_step2_summary_dataset
from dmqclib.common.loader.dataset_loader import load_step3_select_dataset
from dmqclib.common.loader.dataset_loader import load_step4_locate_dataset
from dmqclib.common.loader.dataset_loader import load_step5_extract_dataset
from dmqclib.datasets.features.basic_values import BasicValues3PlusFlanks
from dmqclib.datasets.features.day_of_year import DayOfYearFeat
from dmqclib.datasets.features.location import LocationFeat
from dmqclib.datasets.features.profile_summary import ProfileSummaryStats5


class _TestFeatureBase(unittest.TestCase):
    def _setup(self, class_name):
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

        self.class_name = class_name

    def _test_init_arguments(self, feature_info):
        """Ensure input data and selected profiles are read correctly."""
        ds = self.class_name(
            "temp",
            feature_info,
            self.ds_select.selected_profiles,
            self.ds_extract.filtered_input,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )

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

        self.assertIsInstance(ds.summary_stats, pl.DataFrame)
        self.assertEqual(ds.summary_stats.shape[0], 3528)
        self.assertEqual(ds.summary_stats.shape[1], 12)


class TestLocationFeature(_TestFeatureBase):
    def setUp(self):
        super()._setup(LocationFeat)
        self.feature_info = {
            "class": "location",
            "scales": {
                "longitude": {"min": 14.5, "max": 23.5},
                "latitude": {"min": 55, "max": 66},
            },
        }

    def test_init_arguments(self):
        """Ensure input data and selected profiles are read correctly."""
        super()._test_init_arguments(self.feature_info)

    def test_location_features(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = LocationFeat(
            "temp",
            self.feature_info,
            self.ds_select.selected_profiles,
            self.ds_extract.filtered_input,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )
        ds.extract_features()
        print(ds.features)

        ds.scale_second()
        print(ds.features)

        self.assertIsInstance(ds.features, pl.DataFrame)
        self.assertEqual(ds.features.shape[0], 128)
        self.assertEqual(ds.features.shape[1], 3)


class TestDayOfYearFeature(_TestFeatureBase):
    def setUp(self):
        super()._setup(DayOfYearFeat)
        self.feature_info = {
            "class": "day_of_year",
            "convert": "sine",
        }

    def test_init_arguments(self):
        """Ensure input data and selected profiles are read correctly."""
        super()._test_init_arguments(self.feature_info)

    def test_day_of_year_features(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = DayOfYearFeat(
            "temp",
            self.feature_info,
            self.ds_select.selected_profiles,
            self.ds_extract.filtered_input,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )
        ds.extract_features()
        print(ds.features)

        ds.scale_second()
        print(ds.features)

        self.assertIsInstance(ds.features, pl.DataFrame)
        self.assertEqual(ds.features.shape[0], 128)
        self.assertEqual(ds.features.shape[1], 2)


class TestProfileSummaryStats5Feature(_TestFeatureBase):
    def setUp(self):
        super()._setup(ProfileSummaryStats5)
        self.feature_info = {
            "class": "profile_summary_stats5",
            "scales": {
                "temp": {
                    "mean": {"min": 0, "max": 12.5},
                    "median": {"min": 0, "max": 15},
                    "sd": {"min": 0, "max": 6.5},
                    "pct25": {"min": 0, "max": 12},
                    "pct75": {"min": 1, "max": 19},
                },
                "psal": {
                    "mean": {"min": 2.9, "max": 12},
                    "median": {"min": 2.9, "max": 12},
                    "sd": {"min": 0, "max": 4},
                    "pct25": {"min": 2.5, "max": 8.5},
                    "pct75": {"min": 3, "max": 16},
                },
                "pres": {
                    "mean": {"min": 24, "max": 105},
                    "median": {"min": 24, "max": 105},
                    "sd": {"min": 13, "max": 60},
                    "pct25": {"min": 12, "max": 53},
                    "pct75": {"min": 35, "max": 156},
                },
            },
        }

    def test_init_arguments(self):
        """Ensure input data and selected profiles are read correctly."""
        super()._test_init_arguments(self.feature_info)

    def test_profile_summary_stats5_features(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = ProfileSummaryStats5(
            "temp",
            self.feature_info,
            self.ds_select.selected_profiles,
            self.ds_extract.filtered_input,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )
        ds.extract_features()
        print(ds.features)

        ds.scale_second()
        print(ds.features)

        self.assertIsInstance(ds.features, pl.DataFrame)
        self.assertEqual(ds.features.shape[0], 128)
        self.assertEqual(ds.features.shape[1], 16)


class TestBasicValues3PlusFlanksFeature(_TestFeatureBase):
    def setUp(self):
        super()._setup(BasicValues3PlusFlanks)
        self.feature_info = {
            "class": "basic_values3_plus_flanks",
            "flank_up": 5,
            "scales": {
                "temp": {"min": 0, "max": 20},
                "psal": {"min": 0, "max": 20},
                "pres": {"min": 0, "max": 200},
            },
        }

    def test_init_arguments(self):
        """Ensure input data and selected profiles are read correctly."""
        super()._test_init_arguments(self.feature_info)

    def test_basic_values3_plus_flanks_features(self):
        """Ensure input data and selected profiles are read correctly."""
        ds = BasicValues3PlusFlanks(
            "temp",
            self.feature_info,
            self.ds_select.selected_profiles,
            self.ds_extract.filtered_input,
            self.ds_locate.target_rows,
            self.ds_summary.summary_stats,
        )

        ds.scale_first()
        ds.extract_features()

        self.assertIsInstance(ds.features, pl.DataFrame)
        self.assertEqual(ds.features.shape[0], 128)
        self.assertEqual(ds.features.shape[1], 19)
