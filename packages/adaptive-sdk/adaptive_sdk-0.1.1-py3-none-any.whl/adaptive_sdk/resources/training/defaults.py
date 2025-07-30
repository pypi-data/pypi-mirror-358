from loguru import logger
from pprint import pformat
from datetime import datetime
from typing import get_args, Literal

from adaptive_sdk import input_types
from adaptive_sdk.graphql_client import (
    TrainingMetadataInput,
    TrainingMetadataInputTrainingType,
    TrainingMetadataInputAlignmentMethod,
    AdaptRequestConfigInput,
    TrainingMetadataInputParameters,
    SampleConfigInput,
    TrainingConfigInput,
    TrainingObjectiveInput,
    BaseTrainingParamsInput,
    FeedbackTypeInput,
    SampleDatasourceInput,
    SampleDatasourceDataset,
    SampleDatasourceCompletions,
)

from .constants import SUPPORTED_ALIGNMENT_METHODS, SUPPORTED_DATASOURCES, SAMPLE_DATASOURCE_MODEL_MAP


def get_default_base_training_param() -> input_types.BaseTrainingParamsInput:
    return {
        "learning_rate": 0.00001,
        "batch_size": 32,
        "num_epochs": 1,
        "num_validations": 10,
    }


def validate_alignment_method(
    alignment_method: SUPPORTED_ALIGNMENT_METHODS,
    aligment_objective: input_types.TrainingObjectiveInput | None,
):
    if alignment_method not in get_args(SUPPORTED_ALIGNMENT_METHODS):
        raise ValueError(
            f"alignment_methods must be one of {get_args(SUPPORTED_ALIGNMENT_METHODS)}, got {alignment_method}"
        )
    else:
        if alignment_method != "SFT" and aligment_objective is None:
            raise ValueError("alignment_objective must be set for all alignment methods except SFT")


def build_sample_config(
    data_source: Literal["DATASET", "COMPLETIONS"],
    data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
    feedback_type: Literal["DIRECT", "PREFERENCE"] | None,
    aligment_objective: input_types.TrainingObjectiveInput | None,
    use_case: str,
) -> SampleConfigInput:
    # need feedback_type when training on metric
    if aligment_objective:
        if aligment_objective.get("metric") is not None:
            assert (
                feedback_type is not None
            ), "feedback_type must be set when aligment_objective is to train on a metric"

    supported_datasources = get_args(SUPPORTED_DATASOURCES)
    if data_source not in supported_datasources:
        raise ValueError(f"data_source must be one of DATASET or COMPLETIONS, got {data_source}")
    else:
        # check for invalid keys in data_config that separate completions from dataset config
        # if model validation fails after that, pydantic catches error
        invalid_keys = [
            key for key in data_config.keys() if key not in SAMPLE_DATASOURCE_MODEL_MAP[data_source].model_fields
        ]
        if invalid_keys:
            raise ValueError(
                f"Invalid keys in data_config for {data_source} data_source: {invalid_keys}.\n"
                f"Valid keys are: {list(SAMPLE_DATASOURCE_MODEL_MAP[data_source].model_fields.keys())}"
            )
        # update use case in completions filter if it is specified
        if data_source == "COMPLETIONS" and data_config.get("filter") is not None:
            data_config["filter"].update({"useCase": use_case})  # type: ignore

        datasource_input = (
            SampleDatasourceInput(dataset=SampleDatasourceDataset.model_validate(data_config))
            if data_source == "DATASET"
            else SampleDatasourceInput(completions=SampleDatasourceCompletions.model_validate(data_config))
        )
    return SampleConfigInput(
        feedbackType=FeedbackTypeInput(feedback_type) if feedback_type else None, datasource=datasource_input
    )


def build_training_config(
    feedback_type: Literal["DIRECT", "PREFERENCE"] | None,
    parameter_efficient: bool,
    alignment_method: SUPPORTED_ALIGNMENT_METHODS,
    alignment_objective: input_types.TrainingObjectiveInput | None,
    alignment_params: input_types.TrainingMetadataInputParameters | None,
    base_training_params: input_types.BaseTrainingParamsInput | None,
):
    # update default base training params with overrides
    base_train_params = get_default_base_training_param()
    if base_training_params:
        base_train_params.update(base_training_params)
    else:
        logger.info(
            f"Did not specify base_training_params, using default: \n{pformat(get_default_base_training_param())}"
        )

    # ignore irrelevant params in case of SFT
    if alignment_method == "SFT":
        if feedback_type:
            feedback_type = None
            logger.info("SFT training does not support feedback_type, ignoring input")
        if alignment_objective:
            alignment_objective = {"sft": {}}
            logger.info("SFT training does not support aligment_objective, ignoring input")
        if alignment_params:
            alignment_params = None
            logger.info("SFT training does not support alignment_params, ignoring input")
    else:
        assert alignment_objective
        if alignment_objective.get("metric") is not None and feedback_type is not None:
            logger.info("feedback_type is only relevant when training on a metric, ignoring input")

    # make sure that feedback_type is set when training on metric
    assert alignment_objective
    if alignment_objective.get("metric") is not None:
        assert (
            feedback_type is not None
        ), "Must specify a feedback_type when training_objective is training on a metric."

    training_metadata = TrainingMetadataInput(
        trainingType=(
            TrainingMetadataInputTrainingType.PARAMETER_EFFICIENT
            if parameter_efficient
            else TrainingMetadataInputTrainingType.FULL_WEIGHTS
        ),
        alignmentMethod=TrainingMetadataInputAlignmentMethod(alignment_method),
        parameters=TrainingMetadataInputParameters.model_validate(alignment_params) if alignment_params else None,  # type: ignore
    )

    return TrainingConfigInput(
        baseTrainingParams=BaseTrainingParamsInput.model_validate(base_train_params),
        trainingMetadata=training_metadata,
        trainingObjective=TrainingObjectiveInput.model_validate(alignment_objective),
    )


def build_adapt_config(
    model: str,
    use_case: str,
    data_source: Literal["DATASET", "COMPLETIONS"],
    data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
    feedback_type: Literal["DIRECT", "PREFERENCE"] | None,
    parameter_efficient: bool = True,
    alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
    alignment_objective: input_types.TrainingObjectiveInput | None = None,
    alignment_params: input_types.TrainingMetadataInputParameters | None = None,
    base_training_params: input_types.BaseTrainingParamsInput | None = None,
    output_model_name: str | None = None,
) -> AdaptRequestConfigInput:

    validate_alignment_method(alignment_method, alignment_objective)
    sample_config_input = build_sample_config(data_source, data_config, feedback_type, alignment_objective, use_case)
    training_config_input = build_training_config(
        feedback_type,
        parameter_efficient,
        alignment_method,
        alignment_objective,
        alignment_params,
        base_training_params,
    )
    if not output_model_name:
        output_model_name = model + "-" + datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
        logger.info(f"Did not specify output_model_name, will name the output model `{output_model_name}`")
    adapt_config = AdaptRequestConfigInput(
        outputName=output_model_name,
        sampleConfig=sample_config_input,
        trainingConfig=training_config_input,
    )
    return adapt_config
