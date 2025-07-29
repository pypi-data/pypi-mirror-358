import unittest
from pathlib import Path

import polars as pl

from dmqclib.datasets.step1_input.dataset_a import InputDataSetA


class TestInputDataSetA(unittest.TestCase):
    def setUp(self):
        """Set up test environment and define test data paths."""
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.test_data_file = (
            Path(__file__).resolve().parent
            / "data"
            / "input"
            / "nrt_cora_bo_test.parquet"
        )

    def _get_input_data(self, file_type=None, options=None):
        """Helper to load input data with optional file type and options."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        ds.input_file_name = str(self.test_data_file)

        if file_type is not None:
            ds.dataset_info["input"]["file_type"] = file_type

        if options is not None:
            ds.dataset_info["input"]["options"] = options

        ds.read_input_data()
        return ds.input_data

    def test_init_valid_dataset_name(self):
        """Ensure InputDataSetA constructs correctly with a valid label."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_001")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            InputDataSetA("NON_EXISTENT_LABEL", str(self.explicit_config_file_path))

    def test_config_file(self):
        """Verify the config file is set correctly in the member variable."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        self.assertTrue("datasets.yaml" in ds.config_file_name)

    def test_input_file_name(self):
        """Ensure the input file name is set correctly."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        self.assertEqual(
            "/path/to/data2/input/nrt_cora_bo_test.parquet", str(ds.input_file_name)
        )

    def test_read_input_data_with_explicit_type(self):
        """Ensure data is read correctly with explicit file type."""
        df = self._get_input_data(file_type="parquet", options={})

        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 132342)
        self.assertEqual(df.shape[1], 30)

    def test_read_input_data_infer_type(self):
        """Ensure data is read correctly with inferred file type."""
        df = self._get_input_data(file_type=None, options={})

        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 132342)
        self.assertEqual(df.shape[1], 30)

    def test_read_input_data_missing_options(self):
        """Ensure reading works with missing 'input_file_options' key."""
        df = self._get_input_data(file_type="parquet", options=None)

        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 132342)
        self.assertEqual(df.shape[1], 30)

    def test_read_input_data_unsupported_file_type(self):
        """Ensure ValueError is raised for unsupported file types."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        ds.input_file_name = str(self.test_data_file)
        ds.dataset_info["input"]["file_type"] = "foo"
        ds.dataset_info["input"]["options"] = {}

        with self.assertRaises(ValueError) as context:
            ds.read_input_data()
        self.assertIn("Unsupported file_type 'foo'", str(context.exception))

    def test_read_input_data_file_not_found(self):
        """Ensure FileNotFoundError is raised for non-existent files."""
        ds = InputDataSetA("NRT_BO_001", str(self.explicit_config_file_path))
        ds.input_file_name = str(self.test_data_file) + "_not_found"
        ds.dataset_info["input"]["file_type"] = "parquet"
        ds.dataset_info["input"]["options"] = {}

        with self.assertRaises(FileNotFoundError):
            ds.read_input_data()

    def test_read_input_data_with_extra_options(self):
        """Ensure extra options can be passed while reading data."""
        df = self._get_input_data(file_type="parquet", options={"n_rows": 100})

        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 100)
        self.assertEqual(df.shape[1], 30)
