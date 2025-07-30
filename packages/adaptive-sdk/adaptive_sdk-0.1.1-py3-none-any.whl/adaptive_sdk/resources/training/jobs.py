from __future__ import annotations
from typing import List, TYPE_CHECKING, Literal, overload

from adaptive_sdk import input_types
from adaptive_sdk.graphql_client import (
    ListTrainingJobsTrainingJobs,
    DescribeTrainingJobTrainingJob,
    TrainingJobInput,
    CreateTrainingJobCreateTrainingJob,
    CustomRecipeTrainingJobInput,
    CustomRecipeConfigInput,
)

from .constants import SUPPORTED_ALIGNMENT_METHODS
from .defaults import build_adapt_config
from ..base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class TrainingJobs(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with training jobs.
    """

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    @overload
    def create(
        self,
        model: str,
        data_source: Literal["DATASET"],
        data_config: input_types.SampleDatasourceDataset,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob: ...

    @overload
    def create(
        self,
        model: str,
        data_source: Literal["COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob: ...

    def create(
        self,
        model: str,
        data_source: Literal["DATASET", "COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob:
        """
        Create a new training job.

        Args:
            model: Model to train.
            data_source: Source of data to train on; either an uploaded dataset, or logged completions.
            data_config: Training data configuration.
            feedback_type: If training on `metric` training_objective usingcompletions that have both metric
                and preference feedback logged, you must specify which of those sets to train on.
            parameter_efficient: If `True`, training will be parameter-efficient, and the output model
                will be a lightweight adapter coupled to the selected backbone model.
            aligment_method: Alignment method selection.
            alignment_objective: Configuration for the training objective, determines the reward during training.
            alignment_params: Alignment method-specific hyperparameter configuration.
            base_training_params: Common training parameters.
            job_name: Human readable training job name.
            output_model_name: Name for resulting model.
            wait: If True, only returns when training is finished.
            use_case: Target use case to associate training job with.
            compute_pool: Compute pool where training job will run.
        """

        adapt_config = build_adapt_config(
            model,
            self.use_case_key(use_case),
            data_source,
            data_config,
            feedback_type,
            parameter_efficient,
            alignment_method,
            alignment_objective,
            alignment_params,
            base_training_params,
            output_model_name,
        )
        input = TrainingJobInput(
            model=model,
            useCase=self.use_case_key(use_case),
            name=job_name,
            config=adapt_config,
            wait=wait,
            computePool=compute_pool,
        )
        return self._gql_client.create_training_job(input).create_training_job

    def cancel(self, job_id: str) -> str:
        """
        Cancel ongoing training job.
        """
        return self._gql_client.cancel_training_job(job_id).cancel_training_job

    def list(self) -> List[ListTrainingJobsTrainingJobs]:
        """
        List all training jobs.
        """
        return self._gql_client.list_training_jobs().training_jobs

    def get(self, job_id: str) -> DescribeTrainingJobTrainingJob | None:
        """
        Get details for training job.
        """
        return self._gql_client.describe_training_job(id=job_id).training_job


class AsyncTrainingJobs(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with training jobs.
    """

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    @overload
    async def create(
        self,
        model: str,
        data_source: Literal["DATASET"],
        data_config: input_types.SampleDatasourceDataset,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob: ...

    @overload
    async def create(
        self,
        model: str,
        data_source: Literal["COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob: ...

    async def create(
        self,
        model: str,
        data_source: Literal["DATASET", "COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
        feedback_type: Literal["DIRECT", "PREFERENCE"] | None = None,
        parameter_efficient: bool = True,
        alignment_method: SUPPORTED_ALIGNMENT_METHODS = "PPO",
        alignment_objective: input_types.TrainingObjectiveInput | None = None,
        alignment_params: input_types.TrainingMetadataInputParameters | None = None,
        base_training_params: input_types.BaseTrainingParamsInput | None = None,
        job_name: str | None = None,
        output_model_name: str | None = None,
        wait: bool = False,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> CreateTrainingJobCreateTrainingJob:
        """
        Create a new training job.

        Args:
            model: Model to train.
            data_source: Source of data to train on; either an uploaded dataset, or logged completions.
            data_config: Training data configuration.
            feedback_type: If training on `metric` training_objective usingcompletions that have both metric
                and preference feedback logged, you must specify which of those sets to train on.
            parameter_efficient: If `True`, training will be parameter-efficient, and the output model
                will be a lightweight adapter coupled to the selected backbone model.
            aligment_method: Alignment method selection.
            alignment_objective: Configuration for the training objective, determines the reward during training.
            alignment_params: Alignment method-specific hyperparameter configuration.
            base_training_params: Common training parameters.
            job_name: Human readable training job name.
            output_model_name: Name for resulting model.
            wait: If True, only returns when training is finished.
            use_case: Target use case to associate training job with.
            compute_pool: Compute pool where training job will run.
        """

        adapt_config = build_adapt_config(
            model,
            self.use_case_key(use_case),
            data_source,
            data_config,
            feedback_type,
            parameter_efficient,
            alignment_method,
            alignment_objective,
            alignment_params,
            base_training_params,
            output_model_name,
        )
        input = TrainingJobInput(
            model=model,
            useCase=self.use_case_key(use_case),
            name=job_name,
            config=adapt_config,
            wait=wait,
            computePool=compute_pool,
        )
        result = await self._gql_client.create_training_job(input)
        return result.create_training_job

    async def cancel(self, job_id: str) -> str:
        """
        Cancel ongoing training job.
        """
        result = await self._gql_client.cancel_training_job(job_id)
        return result.cancel_training_job

    async def list(self) -> List[ListTrainingJobsTrainingJobs]:
        """
        List all training jobs.
        """
        result = await self._gql_client.list_training_jobs()
        return result.training_jobs

    async def get(self, job_id: str) -> DescribeTrainingJobTrainingJob | None:
        """
        Get details for training job.
        """
        result = await self._gql_client.describe_training_job(id=job_id)
        return result.training_job
