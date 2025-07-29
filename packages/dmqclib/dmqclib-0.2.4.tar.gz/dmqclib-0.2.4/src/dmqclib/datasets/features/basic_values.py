import polars as pl

from dmqclib.common.base.feature_base import FeatureBase


class BasicValues3PlusFlanks(FeatureBase):
    """
    BasicValues3PlusFlanks extracts target values and flanking values from BO NRT+Cora test data.
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

        self._expanded_observations = None
        self._feature_wide = None

    def extract_features(self):
        """
        Extract features.
        """
        self._init_features()
        self._expand_observations()
        for col_name in self.feature_info["scales"].keys():
            self._pivot_features(col_name)
            self._add_features()
        self._clean_features()

    def _init_features(self):
        self.features = self.target_rows[self.target_name].select(
            [
                pl.col("row_id"),
                pl.col("platform_code"),
                pl.col("profile_no"),
            ]
        )

    def _expand_observations(self):
        self._expanded_observations = (
            self.target_rows[self.target_name]
            .select(
                [
                    pl.col("row_id"),
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col("observation_no"),
                ]
            )
            .join(
                pl.DataFrame(
                    {"flank_seq": list(range(0, self.feature_info.get("flank_up") + 1))}
                ),
                how="cross",
            )
            .with_columns(
                (pl.col("observation_no") - pl.col("flank_seq")).alias("observation_no")
            )
            .with_columns(
                pl.when(pl.col("observation_no") < 1)
                .then(1)
                .otherwise(pl.col("observation_no"))
                .alias("observation_no")
            )
        )

    def _pivot_features(self, col_name: str):
        self._feature_wide = (
            self._expanded_observations.join(
                self.filtered_input.select(
                    [
                        pl.col("platform_code"),
                        pl.col("profile_no"),
                        pl.col("observation_no"),
                        pl.col(col_name).alias("value"),
                    ]
                ),
                on=["platform_code", "profile_no", "observation_no"],
                maintain_order="left",
            )
            .with_columns(
                pl.concat_str(
                    [
                        pl.lit(f"{col_name}_up"),
                        pl.col("flank_seq").cast(pl.String),
                    ],
                    separator="_",
                ).alias("col_name")
            )
            .drop(["observation_no", "flank_seq"])
            .pivot(
                "col_name",
                index=["row_id", "platform_code", "profile_no"],
                values="value",
            )
        )

    def _add_features(self):
        self.features = self.features.join(
            self._feature_wide,
            on=["row_id", "platform_code", "profile_no"],
            maintain_order="left",
        )

    def _clean_features(self):
        self.features = self.features.drop(
            ["platform_code", "profile_no", "platform_code"]
        )

    def scale_first(self):
        """
        Scale features.
        """
        for col_name, v in self.feature_info["scales"].items():
            self.filtered_input = self.filtered_input.with_columns(
                [
                    ((pl.col(col_name) - v["min"]) / (v["max"] - v["min"])).alias(
                        col_name
                    ),
                ]
            )

    def scale_second(self):
        """
        Scale features.
        """
        pass
