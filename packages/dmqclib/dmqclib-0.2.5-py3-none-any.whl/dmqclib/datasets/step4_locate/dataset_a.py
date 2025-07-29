from typing import Dict

import polars as pl

from dmqclib.datasets.step4_locate.locate_base import LocatePositionBase


class LocateDataSetA(LocatePositionBase):
    """
    LocateDataSetA identifies training data rows from BO NRT+Cora test data.
    """

    expected_class_name = "LocateDataSetA"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
        selected_profiles: pl.DataFrame = None,
    ):
        super().__init__(
            dataset_name,
            config_file=config_file,
            input_data=input_data,
            selected_profiles=selected_profiles,
        )

        self.positive_rows = {}
        self.negative_rows = {}

    def select_positive_rows(self, target_name: str, target_value: Dict):
        var_name = target_value["variable"]
        self.positive_rows[target_name] = (
            self.selected_profiles.filter(pl.col("label") == 1)
            .select(
                pl.col("profile_id"),
                pl.col("neg_profile_id"),
                pl.col("platform_code"),
                pl.col("profile_no"),
            )
            .join(
                (
                    self.input_data.filter(pl.col(var_name) == 4).select(
                        pl.col("platform_code"),
                        pl.col("profile_no"),
                        pl.col("observation_no"),
                        pl.col("pres"),
                        pl.col(var_name).alias("flag"),
                    )
                ),
                on=["platform_code", "profile_no"],
            )
            .with_columns(
                pl.lit("0").alias("pos_platform_code"),
                pl.lit(0, dtype=pl.Int32).alias("pos_profile_no"),
                pl.lit(0).alias("pos_observation_no"),
                pl.lit(1).alias("label"),
            )
        )

    def select_negative_rows(self, target_name: str, target_value: Dict):
        var_name = target_value["variable"]
        self.negative_rows[target_name] = (
            self.positive_rows[target_name]
            .select(
                pl.col("platform_code").alias("pos_platform_code"),
                pl.col("profile_no").alias("pos_profile_no"),
                pl.col("neg_profile_id"),
                pl.col("observation_no").alias("pos_observation_no"),
                pl.col("pres").alias("pos_pres"),
            )
            .join(
                self.selected_profiles.filter(pl.col("label") == 0).select(
                    pl.col("profile_id").alias("neg_profile_id"),
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                ),
                how="inner",
                left_on="neg_profile_id",
                right_on="neg_profile_id",
            )
            .join(
                self.input_data.select(
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col("observation_no").alias("neg_observation_no"),
                    pl.col("pres").alias("neg_pres"),
                    pl.col(var_name).alias("flag"),
                ),
                how="inner",
                on=["platform_code", "profile_no"],
            )
            .with_columns(
                (pl.col("pos_pres") - pl.col("neg_pres")).abs().alias("pres_diff")
            )
            .group_by(
                [
                    "pos_platform_code",
                    "pos_profile_no",
                    "neg_profile_id",
                    "pos_observation_no",
                    "platform_code",
                    "profile_no",
                ]
            )
            .agg(pl.all().sort_by("pres_diff").first())
            .with_columns(
                pl.lit(0, dtype=pl.UInt32).alias("zero_id"),
                pl.lit(0).alias("label"),
            )
            .select(
                [
                    pl.col("neg_profile_id").alias("profile_id"),
                    pl.col("zero_id").alias("neg_profile_id"),
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col("neg_observation_no").alias("observation_no"),
                    pl.col("neg_pres").alias("pres"),
                    pl.col("flag"),
                    pl.col("pos_platform_code"),
                    pl.col("pos_profile_no"),
                    pl.col("pos_observation_no"),
                    pl.col("label"),
                ]
            )
        )

    def locate_target_rows(self, target_name: str, target_value: Dict):
        """
        Locate training data rows.
        """
        self.select_positive_rows(target_name, target_value)
        self.select_negative_rows(target_name, target_value)

        self.target_rows[target_name] = (
            self.positive_rows[target_name]
            .vstack(self.negative_rows[target_name])
            .with_row_index("row_id", offset=1)
            .with_columns(
                pl.when(pl.col("label") == 1)
                .then(
                    pl.concat_str(
                        [
                            pl.col("platform_code"),
                            pl.col("profile_no"),
                            pl.col("observation_no"),
                        ],
                        separator="|",
                    )
                )
                .otherwise(
                    pl.concat_str(
                        [
                            pl.col("pos_platform_code"),
                            pl.col("pos_profile_no"),
                            pl.col("pos_observation_no"),
                        ],
                        separator="|",
                    )
                )
                .alias("pair_id"),
            )
            .drop(
                [
                    "neg_profile_id",
                    "pos_platform_code",
                    "pos_profile_no",
                    "pos_observation_no",
                ]
            )
        )
