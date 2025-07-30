from __future__ import annotations
from typing import List, Literal, TYPE_CHECKING, Tuple, overload
from adaptive_sdk.graphql_client import (
    ListEvaluationJobsEvaluationJobs,
    DescribeEvaluationJobEvaluationJob,
    EvaluationCreate,
    EvaluationKind,
    AijudgeEvaluation,
    EvaluationRecipeInput,
    EvaluationJobData,
    SampleConfigInput,
    ModelServiceWithParams,
    GenerateParameters,
)
from adaptive_sdk import input_types
from ..base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource
from ..training.defaults import build_sample_config
from typing_extensions import override

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


def build_recipe_input(
    method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
    feedback_key_exists: bool,
    custom_eval_config: input_types.CustomRecipe | None = None,
) -> EvaluationRecipeInput:
    if method == "custom":
        assert custom_eval_config, "Custom eval requires custom_eval_config"
        assert custom_eval_config["feedback_key"], "Custom eval requires feedback_key"
        assert custom_eval_config["guidelines"], "Custom eval requires guidelines"

        metric_register_mode = "existing" if feedback_key_exists else "new"
        recipe_dict = {
            "custom": {
                "guidelines": custom_eval_config["guidelines"],
                "metric": {metric_register_mode: custom_eval_config["feedback_key"]},
            }
        }

    else:
        recipe_dict = {method: {}}
    return EvaluationRecipeInput.model_validate(recipe_dict)


class EvalJobs(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with evaluation jobs.
    """

    @override
    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)
        self.client = client

    @overload
    def create(
        self,
        data_source: Literal["DATASET"],
        data_config: input_types.SampleDatasourceDataset,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData: ...

    @overload
    def create(
        self,
        data_source: Literal["COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData: ...

    def create(
        self,
        data_source: Literal["DATASET", "COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData:
        """
        Create a new evaluation job.

        Args:
            data_source: Source of data to evaluate on; either an uploaded dataset, or logged completions.
            data_config: Input data configuration.
            models: Models to evaluate.
            judge_model: Model key of judge.
            method: Eval method (built in method, or custom eval).
            generation_params_per_model: Optional list of models to evaluate with their parameters for generation.
                The list should contain tuples, where the first element is the model key, and the second element is the generation parameters.
                If a model is not present in the list, the default generation parameters will be used.
            custom_eval_config: Custom evaluation configuration. Only required if method=="custom".
            name: Optional name for evaluation job.
            use_case: Target use case to associate evaluation job with. Overrides client's default use case.
            compute_pool: Optional compute pool key where evaluation job will run on.
        """
        generation_params_per_model = generation_params_per_model or []

        # Builds data config
        ds_input = build_sample_config(
            data_source=data_source,
            data_config=data_config,
            feedback_type=None,
            aligment_objective=None,
            use_case=self.use_case_key(use_case),
        )

        # Builds recipe method input
        if method == "custom":
            assert custom_eval_config, "Custom eval requires custom_eval_config"
            assert custom_eval_config["feedback_key"], "Custom eval requires feedback_key"
            assert custom_eval_config["guidelines"], "Custom eval requires guidelines"
            feedback_key_exists = self.client.feedback.get_key(custom_eval_config["feedback_key"]) is not None
        else:
            feedback_key_exists = False

        recipe_input = build_recipe_input(
            method=method,
            feedback_key_exists=feedback_key_exists,
            custom_eval_config=custom_eval_config,
        )

        # Builds evaluation job input
        input = EvaluationCreate(
            useCase=self.use_case_key(use_case),
            kind=EvaluationKind(
                aijudge=AijudgeEvaluation(sampleConfig=ds_input, judge=judge_model, recipe=recipe_input)
            ),
            modelServices=models,
            modelServicesWithParams=[
                ModelServiceWithParams(idOrKey=mp[0], createParams=GenerateParameters.model_validate(mp[1]))
                for mp in generation_params_per_model
            ],
            name=name,
            computePool=compute_pool,
        )
        return self._gql_client.create_evaluation_job(input=input).create_evaluation_job

    def cancel(self, job_id: str) -> str:
        return self._gql_client.cancel_evaluation_job(id=job_id).cancel_evaluation_job

    def list(self) -> List[ListEvaluationJobsEvaluationJobs]:
        return self._gql_client.list_evaluation_jobs().evaluation_jobs

    def get(self, job_id: str) -> DescribeEvaluationJobEvaluationJob | None:
        return self._gql_client.describe_evaluation_job(id=job_id).evaluation_job


class AsyncEvalJobs(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)
        self.client = client

    @overload
    async def create(
        self,
        data_source: Literal["DATASET"],
        data_config: input_types.SampleDatasourceDataset,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData: ...

    @overload
    async def create(
        self,
        data_source: Literal["COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData: ...

    async def create(
        self,
        data_source: Literal["DATASET", "COMPLETIONS"],
        data_config: input_types.SampleDatasourceCompletions | input_types.SampleDatasourceDataset,
        models: List[str],
        judge_model: str,
        method: Literal["custom", "answer_relevancy", "context_relevancy", "faithfulness"],
        generation_params_per_model: List[Tuple[str, input_types.GenerateParameters]] | None = None,
        custom_eval_config: input_types.CustomRecipe | None = None,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> EvaluationJobData:
        """
        Create a new evaluation job.

        Args:
            data_source: Source of data to evaluate on; either an uploaded dataset, or logged completions.
            data_config: Input data configuration.
            models: Models to evaluate.
            judge_model: Model key of judge.
            method: Eval method (built in method, or custom eval).
            generation_params_per_model: Optional list of models to evaluate with their parameters for generation.
                The list should contain tuples, where the first element is the model key, and the second element is the generation parameters.
                If a model is not present in the list, the default generation parameters will be used.
            custom_eval_config: Custom evaluation configuration. Only required if method=="custom".
            name: Optional name for evaluation job.
            use_case: Target use case to associate evaluation job with. Overrides client's default use case.
            compute_pool: Optional compute pool key where evaluation job will run on.
        """
        generation_params_per_model = generation_params_per_model or []

        # Builds data config
        ds_input = build_sample_config(
            data_source=data_source,
            data_config=data_config,
            feedback_type=None,
            aligment_objective=None,
            use_case=self.use_case_key(use_case),
        )

        # Builds recipe method input
        if method == "custom":
            assert custom_eval_config, "Custom eval requires custom_eval_config"
            assert custom_eval_config["feedback_key"], "Custom eval requires feedback_key"
            assert custom_eval_config["guidelines"], "Custom eval requires guidelines"
            feedback_key_exists = self.client.feedback.get_key(custom_eval_config["feedback_key"]) is not None
        else:
            feedback_key_exists = False

        recipe_input = build_recipe_input(
            method=method,
            feedback_key_exists=feedback_key_exists,
            custom_eval_config=custom_eval_config,
        )

        # Builds evaluation job input
        input = EvaluationCreate(
            useCase=self.use_case_key(use_case),
            kind=EvaluationKind(
                aijudge=AijudgeEvaluation(sampleConfig=ds_input, judge=judge_model, recipe=recipe_input)
            ),
            modelServices=models,
            modelServicesWithParams=[
                ModelServiceWithParams(idOrKey=mp[0], createParams=GenerateParameters.model_validate(mp[1]))
                for mp in generation_params_per_model
            ],
            name=name,
            computePool=compute_pool,
        )

        result = await self._gql_client.create_evaluation_job(input=input)
        return result.create_evaluation_job

    async def cancel(self, job_id: str) -> str:
        return (await self._gql_client.cancel_evaluation_job(id=job_id)).cancel_evaluation_job

    async def list(self) -> List[ListEvaluationJobsEvaluationJobs]:
        result = await self._gql_client.list_evaluation_jobs()
        return result.evaluation_jobs

    async def get(self, job_id: str) -> DescribeEvaluationJobEvaluationJob | None:
        result = await self._gql_client.describe_evaluation_job(id=job_id)
        return result.evaluation_job
