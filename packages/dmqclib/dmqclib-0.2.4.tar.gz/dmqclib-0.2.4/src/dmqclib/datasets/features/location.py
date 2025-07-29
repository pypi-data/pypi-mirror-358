import polars as pl

from dmqclib.common.base.feature_base import FeatureBase


class LocationFeat(FeatureBase):
    """
    LocationFeat extracts location features from BO NRT+Cora test data.
    """

    def __init__(
        self,
        target_name: str = None,
        selected_profiles: pl.DataFrame = None,
        filtered_input: pl.DataFrame = None,
        target_rows: pl.DataFrame = None,
        summary_stats: pl.DataFrame = None,
        feature_info: pl.DataFrame = None,
    ):
        super().__init__(
            target_name,
            selected_profiles,
            filtered_input,
            target_rows,
            summary_stats,
            feature_info,
        )

    def extract_features(self):
        """
        Extract features.
        """
        self.features = (
            self.target_rows[self.target_name]
            .select(
                [
                    pl.col("row_id"),
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                ]
            )
            .join(
                self.selected_profiles.select(
                    [
                        pl.col("platform_code"),
                        pl.col("profile_no"),
                        pl.col("longitude"),
                        pl.col("latitude"),
                    ]
                ),
                on=["platform_code", "profile_no"],
                maintain_order="left",
            )
            .drop(["platform_code", "profile_no"])
        )

    def scale_first(self):
        """
        Scale features.
        """
        pass

    def scale_second(self):
        """
        Scale features.
        """
        for k, v in self.feature_info["scales"].items():
            self.features = self.features.with_columns(
                [
                    ((pl.col(k) - v["min"]) / (v["max"] - v["min"])).alias(k),
                ]
            )
