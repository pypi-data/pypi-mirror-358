import polars as pl

from dmqclib.common.base.feature_base import FeatureBase


class ProfileSummaryStats5(FeatureBase):
    """
    ProfileSummaryStats5 extracts profile summary features from BO NRT+Cora test data.
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
        self._filter_target_rows_cols()
        for target_name, v1 in self.feature_info["scales"].items():
            for var_name in v1.keys():
                self._extract_single_summary(target_name, var_name)

        self.features = self.features.drop(["platform_code", "profile_no"])

    def _filter_target_rows_cols(self):
        self.features = self.target_rows[self.target_name].select(
            [
                pl.col("row_id"),
                pl.col("platform_code"),
                pl.col("profile_no"),
            ]
        )

    def _extract_single_summary(self, target_name: str, var_name: str):
        self.features = self.features.join(
            self.summary_stats.filter(pl.col("variable") == target_name).select(
                [
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col(var_name).alias(f"{target_name}_{var_name}"),
                ]
            ),
            on=["platform_code", "profile_no"],
            maintain_order="left",
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
        for col_name, v1 in self.feature_info["scales"].items():
            for stat_name, v2 in v1.items():
                self.features = self.features.with_columns(
                    [
                        (
                            (pl.col(f"{col_name}_{stat_name}") - v2["min"])
                            / (v2["max"] - v2["min"])
                        ).alias(f"{col_name}_{stat_name}"),
                    ]
                )
