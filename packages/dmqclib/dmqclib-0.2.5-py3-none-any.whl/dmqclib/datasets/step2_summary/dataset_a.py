import polars as pl

from dmqclib.datasets.step2_summary.summary_base import SummaryStatsBase


class SummaryDataSetA(SummaryStatsBase):
    """
    SummaryDataSetA calculate summary stats for BO NRT+Cora test data.
    """

    expected_class_name = "SummaryDataSetA"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
    ):
        super().__init__(dataset_name, config_file=config_file, input_data=input_data)

        self.val_col_names = [
            "longitude",
            "latitude",
            "temp",
            "psal",
            "pres",
            "dist2coast",
            "bath",
        ]
        self.profile_col_names = ["platform_code", "profile_no"]

    def calculate_global_stats(self, val_col_name: str) -> pl.DataFrame:
        """
        Calculate profile summary stats.
        """
        return (
            self.input_data.select(
                [
                    pl.col(val_col_name).min().cast(pl.Float64).alias("min"),
                    pl.col(val_col_name).max().cast(pl.Float64).alias("max"),
                    pl.col(val_col_name).mean().cast(pl.Float64).alias("mean"),
                    pl.col(val_col_name).median().cast(pl.Float64).alias("median"),
                    pl.col(val_col_name).quantile(0.25).cast(pl.Float64).alias("pct25"),
                    pl.col(val_col_name).quantile(0.75).cast(pl.Float64).alias("pct75"),
                    pl.col(val_col_name)
                    .quantile(0.025)
                    .cast(pl.Float64)
                    .alias("pct2.5"),
                    pl.col(val_col_name)
                    .quantile(0.975)
                    .cast(pl.Float64)
                    .alias("pct97.5"),
                    pl.col(val_col_name).std().cast(pl.Float64).alias("sd"),
                ]
            )
            .with_columns(
                pl.lit("all").alias("platform_code"),
                pl.lit(0).alias("profile_no"),
                pl.lit(val_col_name).alias("variable"),
            )
            .select(
                [
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col("variable"),
                    pl.col("min"),
                    pl.col("pct2.5"),
                    pl.col("pct25"),
                    pl.col("mean"),
                    pl.col("median"),
                    pl.col("pct75"),
                    pl.col("pct97.5"),
                    pl.col("max"),
                    pl.col("sd"),
                ]
            )
        )

    def calculate_profile_stats(
        self, grouped_df: pl.DataFrame, val_col_name: str
    ) -> pl.DataFrame:
        """
        Calculate global summary stats.
        """
        return (
            grouped_df.agg(
                [
                    pl.col(val_col_name).min().cast(pl.Float64).alias("min"),
                    pl.col(val_col_name).max().cast(pl.Float64).alias("max"),
                    pl.col(val_col_name).mean().cast(pl.Float64).alias("mean"),
                    pl.col(val_col_name).median().cast(pl.Float64).alias("median"),
                    pl.col(val_col_name).quantile(0.25).cast(pl.Float64).alias("pct25"),
                    pl.col(val_col_name).quantile(0.75).cast(pl.Float64).alias("pct75"),
                    pl.col(val_col_name)
                    .quantile(0.025)
                    .cast(pl.Float64)
                    .alias("pct2.5"),
                    pl.col(val_col_name)
                    .quantile(0.975)
                    .cast(pl.Float64)
                    .alias("pct97.5"),
                    pl.col(val_col_name).std().cast(pl.Float64).alias("sd"),
                ]
            )
            .with_columns(pl.lit(val_col_name).alias("variable"))
            .select(
                [
                    pl.col("platform_code"),
                    pl.col("profile_no"),
                    pl.col("variable"),
                    pl.col("min"),
                    pl.col("pct2.5"),
                    pl.col("pct25"),
                    pl.col("mean"),
                    pl.col("median"),
                    pl.col("pct75"),
                    pl.col("pct97.5"),
                    pl.col("max"),
                    pl.col("sd"),
                ]
            )
        )

    def calculate_stats(self):
        """
        Calculate summary stats.
        """
        global_stats = pl.concat(
            [self.calculate_global_stats(x) for x in self.val_col_names]
        )
        grouped_df = self.input_data.group_by(self.profile_col_names)
        profile_stats = pl.concat(
            [self.calculate_profile_stats(grouped_df, x) for x in self.val_col_names]
        )

        self.summary_stats = global_stats.vstack(profile_stats)
