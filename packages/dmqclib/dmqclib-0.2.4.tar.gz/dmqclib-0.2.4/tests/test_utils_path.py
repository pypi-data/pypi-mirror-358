import unittest
from pathlib import Path

from dmqclib.utils.config import read_config
from dmqclib.utils.path import build_full_data_path
from dmqclib.utils.path import build_full_input_path


class TestBuildFullInputPath(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We create a config file here for reuse.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.config = read_config(config_file=str(self.explicit_config_file_path))

    def test_normal_params(self):
        """
        Test with all normal, non-empty parameters.
        Expect paths to be joined with slashes correctly.
        """
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "datafile.csv"
        )
        self.assertEqual(result, "/path/to/data2/input/datafile.csv")

    def test_empty_input_folder_arg(self):
        """
        Test when the folder_name2 argument is an empty string.
        """
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "something.txt"
        )
        self.assertEqual(result, "/path/to/data2/input/something.txt")

    def test_none_input_folder_arg(self):
        """
        Test when the folder_name2 argument is None.
        """
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "something_else.txt"
        )
        self.assertEqual(result, "/path/to/data2/input/something_else.txt")

    def test_empty_config_input_folder(self):
        """
        Test when config['path_info']['input_folder'] is an empty string.
        """
        self.config["path_info"]["input"]["folder_name"] = ""
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "file.csv"
        )
        self.assertEqual(result, "/path/to/data2/file.csv")

    def test_none_config_input_folder(self):
        """
        Test when config['path_info']['input_folder'] is None.
        """
        self.config["path_info"]["input"]["folder_name"] = None
        result = build_full_input_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "info.txt",
            folder_name_auto=False,
        )
        self.assertEqual(result, "/path/to/data2/info.txt")

    def test_relative_paths(self):
        """
        Test when input_folder includes '..' or other relative segments.
        """
        self.config["NRT_BO_001"]["input"]["folder_name"] = ".."
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "file.csv"
        )
        self.assertEqual(result, "/path/to/data2/file.csv")

    def test_only_file_name(self):
        """
        Test if the user sets both config['path_info']['input_folder'] and input_folder to empty.
        """
        self.config["path_info"]["input"]["folder_name"] = ""
        result = build_full_input_path(
            self.config["path_info"], self.config["NRT_BO_001"], "filename.txt"
        )
        self.assertEqual(result, "/path/to/data2/filename.txt")


class TestBuildFullDataPath(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We create a config file here for reuse.
        """
        self.explicit_config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "datasets.yaml"
        )
        self.config = read_config(config_file=str(self.explicit_config_file_path))

    def test_normal_usage(self):
        """
        Test that a normal call produces the expected path.
        """
        result = build_full_data_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "select",
            "datafile.csv",
        )
        expected = "/path/to/data3/nrt_bo_001_test/select/datafile.csv"
        self.assertEqual(result, expected)

    def test_common_folder_name(self):
        """
        Test when config["path_info"]["select"]["folder_name"] is an empty string.
        """
        self.config["path_info"]["select"]["folder_name"] = ""
        result = build_full_data_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "select",
            "somefile.txt",
        )
        expected = "/path/to/data3/nrt_bo_001_test/somefile.txt"
        self.assertEqual(result, expected)

    def test_none_select_folder_name(self):
        """
        Test when config["path_info"]["select"]["folder_name"] is None.
        """
        self.config["path_info"]["select"]["folder_name"] = None
        result = build_full_data_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "select",
            "anotherfile.txt",
            folder_name_auto=False,
        )
        expected = "/path/to/data3/nrt_bo_001_test/anotherfile.txt"
        self.assertEqual(result, expected)

    def test_relative_paths(self):
        """
        Test when folder_name1 or config["path_info"]["select"]["folder_name"] includes relative segments like '..'.
        """
        self.config["path_info"]["select"]["folder_name"] = "../valid"
        result = build_full_data_path(
            self.config["path_info"], self.config["NRT_BO_001"], "select", "mydata.csv"
        )
        expected = "/path/to/data3/valid/mydata.csv"
        self.assertEqual(result, expected)

    def test_normal_select_usage(self):
        """
        Test that a normal call produces the expected path.
        """
        result = build_full_data_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "select",
            "datafile.csv",
        )
        expected = "/path/to/data3/nrt_bo_001_test/select/datafile.csv"
        self.assertEqual(result, expected)

    def test_normal_extract_usage(self):
        """
        Test that a normal call produces the expected path.
        """
        result = build_full_data_path(
            self.config["path_info"],
            self.config["NRT_BO_001"],
            "extract",
            "datafile.csv",
        )
        expected = "/path/to/data1/nrt_bo_001/extract/datafile.csv"
        self.assertEqual(result, expected)
