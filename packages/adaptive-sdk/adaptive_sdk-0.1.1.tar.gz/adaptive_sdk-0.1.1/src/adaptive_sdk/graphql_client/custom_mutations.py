from typing import Any, Dict, Optional
from .base_model import Upload
from .custom_fields import AbcampaignFields, ApiKeyFields, CompletionFields, CustomScriptFields, DatasetFields, DatasetValidationOutputFields, DeleteConfirmFields, DirectFeedbackFields, EvaluationJobFields, GraderFields, JudgeFields, MetricFields, MetricWithContextFields, ModelFields, ModelServiceFields, RemoteEnvFields, RoleFields, SystemPromptTemplateFields, TeamFields, TeamMemberFields, TrainingJobFields, UseCaseFields, UserFields
from .custom_typing_fields import GraphQLField, RemoteEnvTestUnion
from .input_types import AbcampaignCreate, AddExternalModelInput, AddHFModelInput, AddModelInput, ApiKeyCreate, AttachModel, CreateRecipeInput, CustomRecipeTrainingJobInput, DatasetCreate, DatasetGenerate, EvaluationCreate, EvaluationV2CreateInput, FeedbackAddInput, FeedbackUpdateInput, GraderCreateInput, GraderUpdateInput, JudgeCreate, JudgeUpdate, MetricCreate, MetricLink, MetricUnlink, ModelComputeConfigInput, ModelPlacementInput, ModelServiceDisconnect, PrebuiltJudgeCreate, RemoteEnvCreate, RoleCreate, SystemPromptTemplateCreate, SystemPromptTemplateUpdate, TeamCreate, TeamMemberRemove, TeamMemberSet, TrainingJobInput, UpdateCompletion, UpdateModelService, UpdateRecipeInput, UseCaseCreate, UseCaseShares, UseCaseUpdate

class Mutation:
    """@private"""

    @classmethod
    def create_ab_campaign(cls, input: AbcampaignCreate) -> AbcampaignFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'AbcampaignCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return AbcampaignFields(field_name='createAbCampaign', arguments=cleared_arguments)

    @classmethod
    def cancel_ab_campaign(cls, input: str) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'IdOrKey!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='cancelAbCampaign', arguments=cleared_arguments)

    @classmethod
    def create_custom_script(cls, use_case: str, input: CreateRecipeInput, file: Upload) -> CustomScriptFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'input': {'type': 'CreateRecipeInput!', 'value': input}, 'file': {'type': 'Upload!', 'value': file}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return CustomScriptFields(field_name='createCustomScript', arguments=cleared_arguments)

    @classmethod
    def update_custom_script(cls, use_case: str, id: str, input: UpdateRecipeInput, *, file: Optional[Upload]=None) -> CustomScriptFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}, 'input': {'type': 'UpdateRecipeInput!', 'value': input}, 'file': {'type': 'Upload', 'value': file}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return CustomScriptFields(field_name='updateCustomScript', arguments=cleared_arguments)

    @classmethod
    def delete_custom_script(cls, use_case: str, id: str) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='deleteCustomScript', arguments=cleared_arguments)

    @classmethod
    def duplicate_custom_script(cls, use_case: str, id: str, *, name: Optional[str]=None) -> CustomScriptFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}, 'name': {'type': 'String', 'value': name}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return CustomScriptFields(field_name='duplicateCustomScript', arguments=cleared_arguments)

    @classmethod
    def create_dataset(cls, input: DatasetCreate, file: Upload) -> DatasetFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'DatasetCreate!', 'value': input}, 'file': {'type': 'Upload!', 'value': file}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DatasetFields(field_name='createDataset', arguments=cleared_arguments)

    @classmethod
    def generate_dataset(cls, input: DatasetGenerate, file: Upload) -> DatasetFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'DatasetGenerate!', 'value': input}, 'file': {'type': 'Upload!', 'value': file}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DatasetFields(field_name='generateDataset', arguments=cleared_arguments)

    @classmethod
    def create_evaluation_job_graders(cls, use_case: str, input: EvaluationV2CreateInput) -> EvaluationJobFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'input': {'type': 'EvaluationV2CreateInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return EvaluationJobFields(field_name='createEvaluationJobGraders', arguments=cleared_arguments)

    @classmethod
    def create_evaluation_job(cls, input: EvaluationCreate) -> EvaluationJobFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'EvaluationCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return EvaluationJobFields(field_name='createEvaluationJob', arguments=cleared_arguments)

    @classmethod
    def cancel_evaluation_job(cls, id: Any) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'id': {'type': 'UUID!', 'value': id}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='cancelEvaluationJob', arguments=cleared_arguments)

    @classmethod
    def update_completion(cls, input: UpdateCompletion) -> CompletionFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'UpdateCompletion!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return CompletionFields(field_name='updateCompletion', arguments=cleared_arguments)

    @classmethod
    def create_system_prompt_template(cls, input: SystemPromptTemplateCreate) -> SystemPromptTemplateFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'SystemPromptTemplateCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return SystemPromptTemplateFields(field_name='createSystemPromptTemplate', arguments=cleared_arguments)

    @classmethod
    def derive_system_prompt_template(cls, input: SystemPromptTemplateUpdate) -> SystemPromptTemplateFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'SystemPromptTemplateUpdate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return SystemPromptTemplateFields(field_name='deriveSystemPromptTemplate', arguments=cleared_arguments)

    @classmethod
    def create_metric(cls, input: MetricCreate) -> MetricFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'MetricCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return MetricFields(field_name='createMetric', arguments=cleared_arguments)

    @classmethod
    def link_metric(cls, input: MetricLink) -> MetricWithContextFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'MetricLink!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return MetricWithContextFields(field_name='linkMetric', arguments=cleared_arguments)

    @classmethod
    def unlink_metric(cls, input: MetricUnlink) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'MetricUnlink!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='unlinkMetric', arguments=cleared_arguments)

    @classmethod
    def attach_model(cls, input: AttachModel) -> ModelServiceFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'AttachModel!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ModelServiceFields(field_name='attachModel', arguments=cleared_arguments)

    @classmethod
    def disconnect_model(cls, input: ModelServiceDisconnect) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'ModelServiceDisconnect!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='disconnectModel', arguments=cleared_arguments)

    @classmethod
    def update_model_service(cls, input: UpdateModelService) -> ModelServiceFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'UpdateModelService!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ModelServiceFields(field_name='updateModelService', arguments=cleared_arguments)

    @classmethod
    def deploy_model(cls, id_or_key: str, wait: bool, *, placement: Optional[ModelPlacementInput]=None) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}, 'wait': {'type': 'Boolean!', 'value': wait}, 'placement': {'type': 'ModelPlacementInput', 'value': placement}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='deployModel', arguments=cleared_arguments)

    @classmethod
    def terminate_model(cls, id_or_key: str, force: bool) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}, 'force': {'type': 'Boolean!', 'value': force}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='terminateModel', arguments=cleared_arguments)

    @classmethod
    def add_external_model(cls, input: AddExternalModelInput) -> ModelFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'AddExternalModelInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ModelFields(field_name='addExternalModel', arguments=cleared_arguments)

    @classmethod
    def add_model(cls, input: AddModelInput) -> ModelFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'AddModelInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ModelFields(field_name='addModel', arguments=cleared_arguments)

    @classmethod
    def import_hf_model(cls, input: AddHFModelInput) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'AddHFModelInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='importHfModel', arguments=cleared_arguments)

    @classmethod
    def update_model_compute_config(cls, id_or_key: str, input: ModelComputeConfigInput) -> ModelFields:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}, 'input': {'type': 'ModelComputeConfigInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ModelFields(field_name='updateModelComputeConfig', arguments=cleared_arguments)

    @classmethod
    def add_remote_env(cls, input: RemoteEnvCreate) -> RemoteEnvFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'RemoteEnvCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return RemoteEnvFields(field_name='addRemoteEnv', arguments=cleared_arguments)

    @classmethod
    def remove_remote_env(cls, id_or_key: str) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='removeRemoteEnv', arguments=cleared_arguments)

    @classmethod
    def test_remote_env(cls, input: RemoteEnvCreate) -> RemoteEnvTestUnion:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'RemoteEnvCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return RemoteEnvTestUnion(field_name='testRemoteEnv', arguments=cleared_arguments)

    @classmethod
    def validate_dataset_schema(cls, remote_env: str, dataset: str, usecase: str) -> DatasetValidationOutputFields:
        arguments: Dict[str, Dict[str, Any]] = {'remoteEnv': {'type': 'IdOrKey!', 'value': remote_env}, 'dataset': {'type': 'IdOrKey!', 'value': dataset}, 'usecase': {'type': 'IdOrKey!', 'value': usecase}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DatasetValidationOutputFields(field_name='validateDatasetSchema', arguments=cleared_arguments)

    @classmethod
    def create_training_job(cls, input: TrainingJobInput) -> TrainingJobFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'TrainingJobInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return TrainingJobFields(field_name='createTrainingJob', arguments=cleared_arguments)

    @classmethod
    def create_custom_recipe_training_job(cls, input: CustomRecipeTrainingJobInput) -> TrainingJobFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'CustomRecipeTrainingJobInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return TrainingJobFields(field_name='createCustomRecipeTrainingJob', arguments=cleared_arguments)

    @classmethod
    def cancel_training_job(cls, id: Any) -> GraphQLField:
        arguments: Dict[str, Dict[str, Any]] = {'id': {'type': 'UUID!', 'value': id}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraphQLField(field_name='cancelTrainingJob', arguments=cleared_arguments)

    @classmethod
    def create_use_case(cls, input: UseCaseCreate) -> UseCaseFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'UseCaseCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return UseCaseFields(field_name='createUseCase', arguments=cleared_arguments)

    @classmethod
    def update_use_case(cls, id_or_key: str, input: UseCaseUpdate) -> UseCaseFields:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}, 'input': {'type': 'UseCaseUpdate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return UseCaseFields(field_name='updateUseCase', arguments=cleared_arguments)

    @classmethod
    def share_use_case(cls, id_or_key: str, input: UseCaseShares) -> UseCaseFields:
        arguments: Dict[str, Dict[str, Any]] = {'idOrKey': {'type': 'IdOrKey!', 'value': id_or_key}, 'input': {'type': 'UseCaseShares!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return UseCaseFields(field_name='shareUseCase', arguments=cleared_arguments)

    @classmethod
    def create_api_key(cls, input: ApiKeyCreate) -> ApiKeyFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'ApiKeyCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return ApiKeyFields(field_name='createApiKey', arguments=cleared_arguments)

    @classmethod
    def set_team_member(cls, input: TeamMemberSet) -> TeamMemberFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'TeamMemberSet!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return TeamMemberFields(field_name='setTeamMember', arguments=cleared_arguments)

    @classmethod
    def remove_team_member(cls, input: TeamMemberRemove) -> UserFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'TeamMemberRemove!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return UserFields(field_name='removeTeamMember', arguments=cleared_arguments)

    @classmethod
    def create_role(cls, input: RoleCreate) -> RoleFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'RoleCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return RoleFields(field_name='createRole', arguments=cleared_arguments)

    @classmethod
    def create_team(cls, input: TeamCreate) -> TeamFields:
        arguments: Dict[str, Dict[str, Any]] = {'input': {'type': 'TeamCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return TeamFields(field_name='createTeam', arguments=cleared_arguments)

    @classmethod
    def update_feedback(cls, id: Any, input: FeedbackUpdateInput) -> DirectFeedbackFields:
        arguments: Dict[str, Dict[str, Any]] = {'id': {'type': 'UUID!', 'value': id}, 'input': {'type': 'FeedbackUpdateInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DirectFeedbackFields(field_name='updateFeedback', arguments=cleared_arguments)

    @classmethod
    def add_direct_feedback(cls, completion_id: Any, metric_id: str, input: FeedbackAddInput) -> DirectFeedbackFields:
        arguments: Dict[str, Dict[str, Any]] = {'completionId': {'type': 'UUID!', 'value': completion_id}, 'metricId': {'type': 'IdOrKey!', 'value': metric_id}, 'input': {'type': 'FeedbackAddInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DirectFeedbackFields(field_name='addDirectFeedback', arguments=cleared_arguments)

    @classmethod
    def create_judge(cls, use_case: str, input: JudgeCreate) -> JudgeFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'input': {'type': 'JudgeCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return JudgeFields(field_name='createJudge', arguments=cleared_arguments)

    @classmethod
    def create_prebuilt_judge(cls, use_case: str, input: PrebuiltJudgeCreate) -> JudgeFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'input': {'type': 'PrebuiltJudgeCreate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return JudgeFields(field_name='createPrebuiltJudge', arguments=cleared_arguments)

    @classmethod
    def update_judge(cls, use_case: str, key: str, input: JudgeUpdate) -> JudgeFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'key': {'type': 'String!', 'value': key}, 'input': {'type': 'JudgeUpdate!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return JudgeFields(field_name='updateJudge', arguments=cleared_arguments)

    @classmethod
    def delete_judge(cls, use_case: str, key: str) -> DeleteConfirmFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'key': {'type': 'String!', 'value': key}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DeleteConfirmFields(field_name='deleteJudge', arguments=cleared_arguments)

    @classmethod
    def create_grader(cls, use_case: str, input: GraderCreateInput) -> GraderFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'input': {'type': 'GraderCreateInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraderFields(field_name='createGrader', arguments=cleared_arguments)

    @classmethod
    def update_grader(cls, use_case: str, id: str, input: GraderUpdateInput) -> GraderFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}, 'input': {'type': 'GraderUpdateInput!', 'value': input}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraderFields(field_name='updateGrader', arguments=cleared_arguments)

    @classmethod
    def delete_grader(cls, use_case: str, id: str) -> DeleteConfirmFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return DeleteConfirmFields(field_name='deleteGrader', arguments=cleared_arguments)

    @classmethod
    def lock_grader(cls, use_case: str, id: str, locked: bool) -> GraderFields:
        arguments: Dict[str, Dict[str, Any]] = {'useCase': {'type': 'IdOrKey!', 'value': use_case}, 'id': {'type': 'IdOrKey!', 'value': id}, 'locked': {'type': 'Boolean!', 'value': locked}}
        cleared_arguments = {key: value for (key, value) in arguments.items() if value['value'] is not None}
        return GraderFields(field_name='lockGrader', arguments=cleared_arguments)