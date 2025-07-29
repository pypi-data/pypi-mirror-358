import numpy as np
import polars as pl

from dmqclib.datasets.step6_split.split_base import SplitDataSetBase


class SplitDataSetA(SplitDataSetBase):
    """
    SplitDataSetBase split feature data into training and test sets for BO NRT+Cora test data.
    """

    expected_class_name = "SplitDataSetA"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        target_features: pl.DataFrame = None,
    ):
        super().__init__(
            dataset_name,
            config_file=config_file,
            target_features=target_features,
        )

        self.work_col_names = [
            "row_id",
            "profile_id",
            "pair_id",
            "platform_code",
            "profile_no",
            "observation_no",
        ]

    def split_test_set(self, target_name: str):
        test_set_fraction = self._get_test_set_fraction()

        pos_test_set = (
            self.target_features[target_name]
            .filter(pl.col("label") == 1)
            .sample(fraction=test_set_fraction, shuffle=True)
        )

        neg_test_set = (
            self.target_features[target_name]
            .filter(pl.col("label") == 0)
            .join(pos_test_set.select([pl.col("pair_id")]), on="pair_id")
        )

        self.test_sets[target_name] = pos_test_set.vstack(neg_test_set)
        self.training_sets[target_name] = self.target_features[target_name].join(
            self.test_sets[target_name].select([pl.col("row_id")]),
            on="row_id",
            how="anti",
        )

    def add_k_fold(self, target_name: str):
        k_fold = self._get_k_fold()
        pos_training_set = self.training_sets[target_name].filter(pl.col("label") == 1)
        df_size = pos_training_set.shape[0]

        n_per_value = df_size // k_fold
        k_values = np.array(
            [i for i in range(1, k_fold + 1) for _ in range(n_per_value)]
        )
        remaining = df_size % k_fold
        k_values = np.concatenate(
            [k_values, np.random.choice(range(1, k_fold + 1), remaining)]
        )
        np.random.shuffle(k_values)

        pos_training_set = pos_training_set.with_columns(pl.Series("k_fold", k_values))
        neg_training_set = (
            self.training_sets[target_name]
            .filter(pl.col("label") == 0)
            .join(pos_training_set.select([pl.col("pair_id", "k_fold")]), on="pair_id")
        )

        training_set = pos_training_set.vstack(neg_training_set)

        self.training_sets[target_name] = pl.concat(
            [training_set.select(["row_id", "k_fold"]), training_set.drop(["k_fold"])],
            how="align_left",
        )

    def drop_columns(self, target_name: str):
        self.training_sets[target_name] = self.training_sets[target_name].drop(
            self.work_col_names
        )
        self.test_sets[target_name] = self.test_sets[target_name].drop(
            self.work_col_names
        )
