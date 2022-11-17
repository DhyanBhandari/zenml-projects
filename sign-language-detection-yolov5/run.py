#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

from pipelines.train_pipeline import yolov5_pipeline
from steps import data_loader, train_augmenter, valid_augmenter, trainer, detector


if __name__ == "__main__":
    pipeline_instance = yolov5_pipeline(
        data_loader=data_loader(),
        train_augmenter=train_augmenter(),
        valid_augmenter=valid_augmenter(),
        trainer=trainer(), # .configure(output_materializers=Yolov5ModelMaterializer),
        detector=detector(),
    )
    pipeline_instance.run()

    # In case you want to run the pipeline on a schedule, run the following:
    #
    # from zenml.pipelines import Schedule
    #
    # schedule = Schedule(cron_expression="*/5 * * * *")  # every 5 minutes
    #
    # kubernetes_example_pipeline(
    #     importer=digits_data_loader(),
    #     trainer=svc_trainer(),
    #     evaluator=evaluator(),
    #     skew_comparison=skew_comparison(),
    # ).run(schedule=schedule)