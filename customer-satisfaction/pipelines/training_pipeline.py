from typing import Tuple, Annotated

from sklearn.base import RegressorMixin
from zenml import pipeline

from pipelines.utils import docker_settings, model_version
from steps import ingest_data, clean_data, train_model, evaluation, \
    model_promoter


@pipeline(
    enable_cache=True,
    settings={"docker": docker_settings},
    model_version=model_version
)
def customer_satisfaction_training_pipeline(
    model_type: str = "lightgbm"
) -> Tuple[Annotated[RegressorMixin, "model"], Annotated[bool, "is_promoted"]]:
    """Training Pipeline.

    Args:
        model_type: str - available options ["lightgbm", "randomforest", "xgboost"]
    """
    df = ingest_data()
    x_train, x_test, y_train, y_test = clean_data(df)
    model = train_model(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test, model_type=model_type)
    mse, rmse = evaluation(model, x_test, y_test)
    is_promoted = model_promoter(accuracy=mse)
    return model, is_promoted