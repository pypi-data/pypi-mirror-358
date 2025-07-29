import unittest
from pathlib import Path

from dmqclib.utils.config import get_base_path_from_config
from dmqclib.utils.config import get_file_name_from_config
from dmqclib.utils.config import get_folder_name_from_config
from dmqclib.utils.config import read_config


class TestReadConfig(unittest.TestCase):
    def setUp(self):
        """
        Set the test data config file.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )

    def test_read_config_with_explicit_file(self):
        """
        Test when config_file is explicitly specified.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        self.assertIsNotNone(config, "Data should not be None")
        self.assertIn("path_info", config, "Key 'path_info' should be in the YAML")
        self.assertEqual(config["path_info"]["input"]["base_path"], "/path/to/data2")
        self.assertEqual(config["path_info"]["input"]["folder_name"], "input")
        self.assertEqual(config["path_info"]["select"]["base_path"], "/path/to/data3")
        self.assertEqual(config["path_info"]["select"]["folder_name"], "select")

    def test_read_config_with_config_name(self):
        """
        Test when only config_name is specified (check that the file can be
        found by traversing up parent_level directories).
        """
        config = read_config(config_file_name="datasets.yaml", parent_level=3)
        self.assertIsNotNone(config, "Data should not be None")
        self.assertIn("path_info", config, "Key 'path_info' should be in the YAML")

    def test_read_config_no_params_raises_error(self):
        """
        Test that ValueError is raised if neither config_file nor config_file_name is provided.
        """
        with self.assertRaises(ValueError):
            read_config()

    def test_read_config_nonexistent_file(self):
        """
        Test that FileNotFoundError is raised if a non-existent file is specified.
        """
        with self.assertRaises(FileNotFoundError):
            read_config(config_file="non_existent.yaml")


class TestBasePathName(unittest.TestCase):
    def setUp(self):
        """
        Set the test data config file.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )

    def test_common_base_path(self):
        """
        Test file name with a correct entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        base_path = get_base_path_from_config(config["path_info"], "common")
        self.assertEqual("/path/to/data1", base_path)

    def test_input_base_path(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        base_path = get_base_path_from_config(config["path_info"], "input")
        self.assertEqual("/path/to/data2", base_path)

    def test_locate_base_path(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        base_path = get_base_path_from_config(config["path_info"], "locate")
        self.assertEqual("/path/to/data1", base_path)


class TestGetFolderName(unittest.TestCase):
    def setUp(self):
        """
        Set the test data config file.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )

    def test_input_folder_name(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        folder_name = get_folder_name_from_config(config["path_info"], "input")
        self.assertEqual("input", folder_name)

    def test_select_folder_name(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        folder_name = get_folder_name_from_config(config["path_info"], "select")
        self.assertEqual("select", folder_name)

    def test_locate_folder_name(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        folder_name = get_folder_name_from_config(config["path_info"], "locate")
        self.assertEqual("select", folder_name)

    def test_extract_folder_name(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))
        folder_name = get_folder_name_from_config(config["path_info"], "extract")
        self.assertEqual("extract", folder_name)


class TestGetFileName(unittest.TestCase):
    def setUp(self):
        """
        Set the test data config file.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )

    def test_file_name(self):
        """
        Test file name with a correct entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))

        file_name = get_file_name_from_config(config["NRT_BO_001"], "input")
        self.assertEqual("nrt_cora_bo_test.parquet", file_name)

    def test_no_file_name(self):
        """
        Test file name without an entry.
        """
        config = read_config(config_file=str(self.explicit_config_file_path))

        with self.assertRaises(ValueError):
            _ = get_file_name_from_config(config["NRT_BO_002"], "input")
