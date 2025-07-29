from dmqclib.datasets.features.basic_values import BasicValues3PlusFlanks
from dmqclib.datasets.features.day_of_year import DayOfYearFeat
from dmqclib.datasets.features.location import LocationFeat
from dmqclib.datasets.features.profile_summary import ProfileSummaryStats5

FEATURE_REGISTRY = {
    "location": LocationFeat,
    "day_of_year": DayOfYearFeat,
    "profile_summary_stats5": ProfileSummaryStats5,
    "basic_values3_plus_flanks": BasicValues3PlusFlanks,
}
