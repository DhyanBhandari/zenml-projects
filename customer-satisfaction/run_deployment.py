import click
from zenml.client import Client

from pipelines.deployment_pipeline import (
    continuous_deployment_pipeline,
    inference_pipeline,
    predictor,
)
from steps.dynamic_importer import dynamic_importer
from steps.deployment_trigger import deployment_trigger
from steps.prediction_service_loader import prediction_service_loader
from rich import print
from steps.clean_data import clean_data
from steps.evaluation import evaluation
from steps.ingest_data import ingest_data
from steps.train_model import train_model
from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri
from zenml.integrations.mlflow.model_deployers.mlflow_model_deployer import (
    MLFlowModelDeployer,
)
from zenml.integrations.mlflow.steps import (
    mlflow_model_deployer_step,
)


@click.command()
@click.option(
    "--min-accuracy",
    default=1.8,
    help="Minimum mse required to deploy the model",
)
@click.option(
    "--stop-service",
    is_flag=True,
    default=False,
    help="Stop the prediction service when done",
)
def run_main(min_accuracy: float, stop_service: bool, model_name="Customer_Satisfaction_Predictor"):
    """Run the mlflow example pipeline"""
    if stop_service:
        # get the MLflow model deployer stack component
        model_deployer = MLFlowModelDeployer.get_active_model_deployer()

        # fetch existing services with same pipeline name, step name and model name
        existing_services = model_deployer.find_model_server(
            pipeline_name="continuous_deployment_pipeline",
            pipeline_step_name="model_deployer",
            model_name=model_name,
            running=True,
        )

        if existing_services:
            existing_services[0].stop(timeout=10)
        return

    deployment = continuous_deployment_pipeline(min_accuracy=min_accuracy)
    deployment.run(config_path="config.yaml")

    inference = inference_pipeline(
        dynamic_importer=dynamic_importer(),
        prediction_service_loader=prediction_service_loader(
                pipeline_name="continuous_deployment_pipeline",
                step_name="model_deployer"
        ),
        predictor=predictor(),
    )
    inference.run()

    print(
        "Now run \n "
        f"    mlflow ui --backend-store-uri {get_tracking_uri()}\n"
        "To inspect your experiment runs within the mlflow UI.\n"
        "You can find your runs tracked within the `mlflow_example_pipeline`"
        "experiment. Here you'll also be able to compare the two runs.)"
    )

    model_deployer = MLFlowModelDeployer.get_active_model_deployer()

    # fetch existing services with same pipeline name, step name and model name
    service = model_deployer.find_model_server(
        pipeline_name="continuous_deployment_pipeline",
        pipeline_step_name="model_deployer",
        running=True,
    )

    if service[0]:
        print(
            f"The MLflow prediction server is running locally as a daemon process "
            f"and accepts inference requests at:\n"
            f"    {service[0].prediction_url}\n"
            f"To stop the service, re-run the same command and supply the "
            f"`--stop-service` argument."
        )


if __name__ == "__main__":
    run_main()
