from abc import abstractmethod

from dmqclib.common.base.dataset_base import DataSetBase
from dmqclib.utils.config import get_file_name_from_config
from dmqclib.utils.file import read_input_file
from dmqclib.utils.path import build_full_input_path


class InputDataSetBase(DataSetBase):
    """
    Base class for input data loading classes.
    """

    def __init__(self, dataset_name: str, config_file: str = None):
        super().__init__("input", dataset_name, config_file=config_file)

        # Set member variables
        self._build_input_file_name()
        self.input_data = None

    def _build_input_file_name(self):
        """
        Set the input file based on configuration entries.
        """
        file_name = get_file_name_from_config(self.dataset_info, "input")

        self.input_file_name = build_full_input_path(
            self.path_info, self.dataset_info, file_name
        )

    def read_input_data(self):
        """
        Reads the input data specified by the dataset entry in configuration file.
        """
        input_file = self.input_file_name
        file_type = self.dataset_info["input"].get("file_type") or None
        options = self.dataset_info["input"].get("options") or {}

        self.input_data = read_input_file(input_file, file_type, options)

    @abstractmethod
    def select(self):
        """
        Selects columns of the data frame in self.input_data.
        """
        pass

    @abstractmethod
    def filter(self):
        """
        Filter rows of the data frame in self.input_data.
        """
        pass
