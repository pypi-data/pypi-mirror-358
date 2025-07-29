import unittest
from pathlib import Path

from dmqclib.training.models.empty_model import EmptyModel


class TestEmptyModel(unittest.TestCase):
    def setUp(self):
        """
        Called before each test method. We define the explicit path to
        the test data config file here for reuse.
        """
        self.config_file_path = (
            Path(__file__).resolve().parent / "data" / "config" / "training.yaml"
        )

    def test_init_valid_dataset_name(self):
        """Ensure ExtractDataSetA constructs correctly with a valid label."""
        ds = EmptyModel("NRT_BO_002", str(self.config_file_path))
        self.assertEqual(ds.dataset_name, "NRT_BO_002")

    def test_init_invalid_dataset_name(self):
        """Ensure ValueError is raised for an invalid label."""
        with self.assertRaises(ValueError):
            EmptyModel("NON_EXISTENT_LABEL", str(self.config_file_path))

    def test_config_file(self):
        """Verify the config file is correctly set in the member variable."""
        ds = EmptyModel("NRT_BO_002", str(self.config_file_path))
        self.assertTrue("training.yaml" in ds.config_file_name)
