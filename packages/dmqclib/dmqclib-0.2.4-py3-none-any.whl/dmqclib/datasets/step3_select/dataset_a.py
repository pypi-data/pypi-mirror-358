import polars as pl

from dmqclib.datasets.step3_select.select_base import ProfileSelectionBase


class SelectDataSetA(ProfileSelectionBase):
    """
    SelectDataSetA defines negative and positive profiles from BO NRT+Cora test data.

    Main steps:
    1. Select positive profiles:
        Select profiles that have values 4 in at least one of temp_qc, psal_qc, and pres_qc.

    2. Select negative profiles:
        Select profiles that have values 1 in all of temp_qc, psal_qc, pres_qc, temp_qc_dm, psal_qc_dm, pres_qc_dm.

    3. Identify pairs from positive and negative datasets:
        To reduce negative profiles, identify and keep only profiles having close dates to those of positive profiles.

    4. Combine dataframes:
        Combine positive and negative datasets.
    """

    expected_class_name = "SelectDataSetA"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        input_data: pl.DataFrame = None,
    ):
        super().__init__(dataset_name, config_file=config_file, input_data=input_data)

        self.pos_profile_df = None
        self.neg_profile_df = None
        self.key_col_names = [
            "platform_code",
            "profile_no",
            "profile_timestamp",
            "longitude",
            "latitude",
        ]

    def select_positive_profiles(self):
        """
        Select profiles with bad flags as positive profiles.
        """
        self.pos_profile_df = (
            self.input_data.filter(
                (pl.col("temp_qc") == 4)
                | (pl.col("psal_qc") == 4)
                | (pl.col("pres_qc") == 4)
            )
            .select(self.key_col_names)
            .unique(subset=self.key_col_names)
            .sort(["platform_code", "profile_no"])
            .with_row_index("profile_id", offset=1)
            .with_columns(
                pl.col("profile_timestamp").dt.ordinal_day().alias("pos_day_of_year")
            )
        )

    def select_negative_profiles(self):
        """
        Select profiles with all good flags as negative profiles.
        """
        self.neg_profile_df = (
            self.input_data.group_by(self.key_col_names)
            .agg(
                [
                    pl.col("temp_qc").max().alias("max_temp_qc"),
                    pl.col("psal_qc").max().alias("max_psal_qc"),
                    pl.col("pres_qc").max().alias("max_pres_qc"),
                    pl.col("temp_qc_dm").max().alias("max_temp_qc_dm"),
                    pl.col("psal_qc_dm").max().alias("max_psal_qc_dm"),
                    pl.col("pres_qc_dm").max().alias("max_pres_qc_dm"),
                ]
            )
            .filter(
                (pl.col("max_temp_qc") == 1)
                & (pl.col("max_psal_qc") == 1)
                & (pl.col("max_pres_qc") == 1)
                & (pl.col("max_temp_qc_dm") == 1)
                & (pl.col("max_psal_qc_dm") == 1)
                & (pl.col("max_pres_qc_dm") == 1)
            )
            .select(self.key_col_names)
            .sort(["platform_code", "profile_no"])
            .with_row_index("profile_id", offset=self.pos_profile_df.shape[0] + 1)
            .with_columns(
                pl.col("profile_timestamp").dt.ordinal_day().alias("neg_day_of_year")
            )
        )

    def find_profile_pairs(self):
        """
        Identify pairs from positive and negative datasets.
        """
        closest_neg_id = (
            self.pos_profile_df.join(self.neg_profile_df, how="cross", suffix="_neg")
            .with_columns(
                (pl.col("pos_day_of_year") - pl.col("neg_day_of_year"))
                .abs()
                .alias("day_diff")
            )
            .group_by("profile_id")
            .agg(
                pl.col("profile_id_neg")
                .sort_by(["day_diff", "profile_id"])
                .first()
                .alias("neg_profile_id")
            )
        )

        self.pos_profile_df = (
            self.pos_profile_df.join(closest_neg_id, on="profile_id", how="left")
            .with_columns(pl.lit(1).alias("label"))
            .drop("pos_day_of_year")
        )

        self.neg_profile_df = (
            self.neg_profile_df.filter(
                pl.col("profile_id").is_in(closest_neg_id["neg_profile_id"].to_list())
            )
            .with_columns(
                pl.lit(0, dtype=pl.UInt32).alias("neg_profile_id"),
                pl.lit(0).alias("label"),
            )
            .drop("neg_day_of_year")
        )

    def label_profiles(self):
        """
        Select and filter positive and negative datasets and combine them.
        """
        self.select_positive_profiles()
        self.select_negative_profiles()
        self.find_profile_pairs()

        self.selected_profiles = self.pos_profile_df.vstack(self.neg_profile_df)
