import polars as pl

from dmqclib.training.step2_validate.validate_base import ValidationBase


class KFoldValidation(ValidationBase):
    """
    KFoldValidation performs k-fold cross validation
    """

    expected_class_name = "KFoldValidation"

    def __init__(
        self,
        dataset_name: str,
        config_file: str = None,
        training_sets: pl.DataFrame = None,
    ):
        super().__init__(
            dataset_name,
            config_file=config_file,
            training_sets=training_sets,
        )

        self.k_fold = 10

    def _get_k_fold(self) -> str:
        if (
            "validate" in self.dataset_info
            and "k_fold" in self.dataset_info["validate"]
        ):
            k_fold = self.dataset_info["validate"].get("k_fold", self.k_fold)
        else:
            k_fold = self.k_fold

        return k_fold

    def validate(self, target_name: str):
        """
        Validate models
        """

        self.built_models[target_name] = list()
        self.results[target_name] = list()
        self.reports[target_name] = list()

        k_fold = self._get_k_fold()
        for k in range(k_fold):
            self.base_model.k = k + 1
            training_set = (
                self.training_sets[target_name]
                .filter(pl.col("k_fold") != (k + 1))
                .drop("k_fold")
            )
            self.base_model.training_set = training_set
            self.base_model.build()
            self.built_models[target_name].append(self.base_model.built_model)

            test_set = (
                self.training_sets[target_name]
                .filter(pl.col("k_fold") == (k + 1))
                .drop("k_fold")
            )
            self.base_model.test_set = test_set
            self.base_model.test()
            self.results[target_name].append(self.base_model.result)
            self.reports[target_name].append(self.base_model.report)

    def summarise(self, target_name: str):
        self.base_model.result_list = self.results[target_name]
        self.base_model.report_list = self.reports[target_name]
        self.base_model.summarise()
        self.summarised_results[target_name] = self.base_model.summarised_results
        self.summarised_reports[target_name] = self.base_model.summarised_reports
