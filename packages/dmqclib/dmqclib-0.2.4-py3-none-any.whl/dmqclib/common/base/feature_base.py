from abc import ABC, abstractmethod

import polars as pl


class FeatureBase(ABC):
    """
    Base class to extract features
    """

    def __init__(
        self,
        target_name: str = None,
        feature_info: pl.DataFrame = None,
        selected_profiles: pl.DataFrame = None,
        filtered_input: pl.DataFrame = None,
        target_rows: pl.DataFrame = None,
        summary_stats: pl.DataFrame = None,
    ):
        # Set member variables
        self.target_name = target_name
        self.feature_info = feature_info
        self.selected_profiles = selected_profiles
        self.filtered_input = filtered_input
        self.target_rows = target_rows
        self.summary_stats = summary_stats
        self.features = None

    @abstractmethod
    def extract_features(self):
        """
        Extract features.
        """
        pass

    @abstractmethod
    def scale_first(self):
        """
        Scale features.
        """
        pass

    @abstractmethod
    def scale_second(self):
        """
        Scale features.
        """
        pass
