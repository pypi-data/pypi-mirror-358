from dmqclib.datasets.step1_input.dataset_a import InputDataSetA
from dmqclib.datasets.step2_summary.dataset_a import SummaryDataSetA
from dmqclib.datasets.step3_select.dataset_a import SelectDataSetA
from dmqclib.datasets.step4_locate.dataset_a import LocateDataSetA
from dmqclib.datasets.step5_extract.dataset_a import ExtractDataSetA
from dmqclib.datasets.step6_split.dataset_a import SplitDataSetA

INPUT_DATASET_REGISTRY = {
    "InputDataSetA": InputDataSetA,
}

SUMMARY_DATASET_REGISTRY = {
    "SummaryDataSetA": SummaryDataSetA,
}

SELECT_DATASET_REGISTRY = {
    "SelectDataSetA": SelectDataSetA,
}

LOCATE_DATASET_REGISTRY = {
    "LocateDataSetA": LocateDataSetA,
}

EXTRACT_DATASET_REGISTRY = {
    "ExtractDataSetA": ExtractDataSetA,
}

SPLIT_DATASET_REGISTRY = {
    "SplitDataSetA": SplitDataSetA,
}
