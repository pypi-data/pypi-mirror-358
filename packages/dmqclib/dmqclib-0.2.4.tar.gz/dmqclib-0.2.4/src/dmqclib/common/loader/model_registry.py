from dmqclib.training.models.empty_model import EmptyModel
from dmqclib.training.models.xgboost import XGBoost

MODEL_REGISTRY = {
    "EmptyModel": EmptyModel,
    "XGBoost": XGBoost,
}
