from dmqclib.common.base.model_base import ModelBase


class EmptyModel(ModelBase):
    expected_class_name = "EmptyModel"

    def __init__(self, dataset_name: str, config_file: str = None):
        super().__init__(
            dataset_name,
            config_file=config_file,
        )

    def build(self):
        """
        Build model
        """
        if self.training_set is None:
            raise ValueError("Member variable 'training_set' must not be empty.")

        self.built_model = 1 if self.built_model is None else self.built_model + 1

        print()
        print("#Build", self.built_model)
        print(self.training_set)

    def test(self):
        """
        Test model.
        """
        if self.built_model is None:
            raise ValueError("Member variable 'built_model' must not be empty.")

        if self.test_set is None:
            raise ValueError("Member variable 'test_set' must not be empty.")

        self.result = 10 if self.result is None else self.result + 1
        self.report = 20 if self.report is None else self.report + 1

        print()
        print("#Test", self.result)
        print(self.built_model)
        print(self.test_set)

    def summarise(self):
        """
        Summarise test results.
        """
        if self.result_list is None:
            raise ValueError("Member variable 'result_list' must not be empty.")

        if self.report_list is None:
            raise ValueError("Member variable 'report_list' must not be empty.")

        self.summarised_results = (
            100 if self.summarised_results is None else self.summarised_results + 1
        )
        self.summarised_reports = (
            200 if self.summarised_reports is None else self.summarised_reports + 1
        )
