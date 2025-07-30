from typing import Any, List, Optional
from pydantic import Field
from .base_model import BaseModel
from .enums import AbcampaignStatus, CompletionSource, DatasetSource, DateBucketUnit, ExternalModelProviderName, FeedbackType, FeedbackTypeInput, GraderTypeEnum, MetricAggregation, MetricKind, MetricScoringType, ModelKindFilter, ModelOnline, OpenAIModel, PrebuiltCriteriaKey, ScriptKind, SelectionTypeInput, SortDirection, TimeseriesInterval, TrainingMetadataInputAlignmentMethod, TrainingMetadataInputTrainingType, UnitPosition

class AbCampaignFilter(BaseModel):
    """@private"""
    active: Optional[bool] = None
    status: Optional[AbcampaignStatus] = None
    use_case: Optional[str] = Field(alias='useCase', default=None)

class AbcampaignCreate(BaseModel):
    """@private"""
    key: str
    name: Optional[str] = None
    metric: str
    use_case: str = Field(alias='useCase')
    model_services: List[str] = Field(alias='modelServices')
    auto_deploy: bool = Field(alias='autoDeploy')
    traffic_split: float = Field(alias='trafficSplit')
    feedback_type: FeedbackType = Field(alias='feedbackType', default=FeedbackType.DIRECT)

class AdaptRequestConfigInput(BaseModel):
    """@private"""
    output_name: str = Field(alias='outputName')
    sample_config: 'SampleConfigInput' = Field(alias='sampleConfig')
    training_config: 'TrainingConfigInput' = Field(alias='trainingConfig')

class AddExternalModelInput(BaseModel):
    """@private"""
    name: str
    provider: ExternalModelProviderName
    provider_data: Optional['ModelProviderDataInput'] = Field(alias='providerData', default=None)
    description: Optional[str] = None

class AddHFModelInput(BaseModel):
    """@private"""
    model_id: str = Field(alias='modelId')
    output_model_name: str = Field(alias='outputModelName')
    output_model_key: Optional[str] = Field(alias='outputModelKey', default=None)
    hf_token: str = Field(alias='hfToken')
    compute_pool: Optional[str] = Field(alias='computePool', default=None)

class AddModelInput(BaseModel):
    """@private"""
    path: str
    name: str
    key: Optional[str] = None

class AijudgeEvaluation(BaseModel):
    """@private"""
    sample_config: 'SampleConfigInput' = Field(alias='sampleConfig')
    judge: str
    recipe: 'EvaluationRecipeInput'

class AnswerRelevancyRecipe(BaseModel):
    """@private"""
    misc: Optional[str] = None

class AnthropicProviderDataInput(BaseModel):
    """@private"""
    api_key: str = Field(alias='apiKey')
    external_model_id: str = Field(alias='externalModelId')

class ApiKeyCreate(BaseModel):
    """@private"""
    user: str

class AttachModel(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    model: str
    attached: bool = True
    placement: Optional['ModelPlacementInput'] = None
    wait: bool = False

class AzureProviderDataInput(BaseModel):
    """@private"""
    api_key: str = Field(alias='apiKey')
    external_model_id: str = Field(alias='externalModelId')
    endpoint: str

class BaseTrainingParamsInput(BaseModel):
    """@private"""
    learning_rate: float = Field(alias='learningRate')
    num_epochs: int = Field(alias='numEpochs')
    batch_size: int = Field(alias='batchSize')
    num_validations: int = Field(alias='numValidations')

class CompletionComparisonFilterInput(BaseModel):
    """@private"""
    metric: str

class CompletionFeedbackFilterInput(BaseModel):
    """@private"""
    metric: str
    gt: Optional[float] = None
    gte: Optional[float] = None
    eq: Optional[float] = None
    neq: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    reasons: Optional[List[str]] = None
    user: Optional[Any] = None

class CompletionLabelValue(BaseModel):
    """@private"""
    key: str
    value: str

class ContextRelevancyRecipe(BaseModel):
    """@private"""
    misc: Optional[str] = None

class CreateRecipeInput(BaseModel):
    """@private"""
    name: str
    key: Optional[str] = None
    description: Optional[str] = None

class CursorPageInput(BaseModel):
    """@private"""
    first: Optional[int] = None
    after: Optional[str] = None
    before: Optional[str] = None
    last: Optional[int] = None

class CustomRecipe(BaseModel):
    """@private"""
    guidelines: List['GuidelineInput']
    metric: 'MetricGetOrCreate'

class CustomRecipeConfigInput(BaseModel):
    """@private"""
    recipe: str
    args: Any
    output_name: str = Field(alias='outputName')

class CustomRecipeTrainingJobInput(BaseModel):
    """@private"""
    model: str
    use_case: str = Field(alias='useCase')
    name: Optional[str] = None
    config: 'CustomRecipeConfigInput'
    compute_pool: Optional[str] = Field(alias='computePool', default=None)
    wait: bool = False

class CustomScriptFilterInput(BaseModel):
    """@private"""
    kind: Optional[List[ScriptKind]] = None

class DatasetCreate(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    name: str
    key: Optional[str] = None
    source: Optional[DatasetSource] = None

class DatasetGenerate(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    name: str
    key: Optional[str] = None
    compute_pool: Optional[str] = Field(alias='computePool', default=None)
    config: 'DatasetGenerationConfig'

class DatasetGenerationConfig(BaseModel):
    """@private"""
    rag: Optional['RagdataGenerationConfig'] = None

class DpotrainingParamsInput(BaseModel):
    """@private"""
    kl_div_coeff: float = Field(alias='klDivCoeff')

class EmojiInput(BaseModel):
    """@private"""
    native: str

class EvaluationCreate(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    name: Optional[str] = None
    kind: 'EvaluationKind'
    model_services: List[str] = Field(alias='modelServices', default_factory=lambda : [])
    model_services_with_params: List['ModelServiceWithParams'] = Field(alias='modelServicesWithParams', default_factory=lambda : [])
    compute_pool: Optional[str] = Field(alias='computePool', default=None)

class EvaluationKind(BaseModel):
    """@private"""
    aijudge: Optional['AijudgeEvaluation'] = None
    remote_env: Optional['RemoteEnvEvaluation'] = Field(alias='remoteEnv', default=None)

class EvaluationRecipeInput(BaseModel):
    """@private"""
    faithfulness: Optional['FaithfulnessRecipe'] = None
    custom: Optional['CustomRecipe'] = None
    context_relevancy: Optional['ContextRelevancyRecipe'] = Field(alias='contextRelevancy', default=None)
    answer_relevancy: Optional['AnswerRelevancyRecipe'] = Field(alias='answerRelevancy', default=None)

class EvaluationV2CreateInput(BaseModel):
    """@private"""
    name: Optional[str] = None
    model_services: List['ModelServiceWithParams'] = Field(alias='modelServices')
    evaluators: 'EvaluatorsInput'
    datasource: 'SampleConfigInput'
    compute_pool: Optional[str] = Field(alias='computePool', default=None)

class EvaluatorsInput(BaseModel):
    """@private"""
    graders: Optional[List[str]] = None
    judges: Optional[List[str]] = None

class FaithfulnessRecipe(BaseModel):
    """@private"""
    misc: Optional[str] = None

class FeedbackAddInput(BaseModel):
    """@private"""
    value: Any
    details: Optional[str] = None
    reason: Optional[str] = None
    user_id: Optional[Any] = Field(alias='userId', default=None)

class FeedbackFilterInput(BaseModel):
    """@private"""
    labels: Optional[List['LabelFilter']] = None

class FeedbackUpdateInput(BaseModel):
    """@private"""
    value: Optional[Any] = None
    details: Optional[str] = None

class GenerateParameters(BaseModel):
    """@private"""
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = Field(alias='maxTokens', default=None)
    temperature: Optional[float] = None
    top_p: Optional[float] = Field(alias='topP', default=None)
    max_ttft_ms: Optional[int] = Field(alias='maxTtftMs', default=None)

class GoogleProviderDataInput(BaseModel):
    """@private"""
    api_key: str = Field(alias='apiKey')
    external_model_id: str = Field(alias='externalModelId')

class GraderConfigInput(BaseModel):
    """@private"""
    judge: Optional['JudgeConfigInput'] = None
    prebuilt: Optional['PrebuiltConfigInput'] = None

class GraderCreateInput(BaseModel):
    """@private"""
    name: str
    key: Optional[str] = None
    grader_type: GraderTypeEnum = Field(alias='graderType')
    grader_config: 'GraderConfigInput' = Field(alias='graderConfig')
    metric: 'MetricGetOrCreate'

class GraderUpdateInput(BaseModel):
    """@private"""
    name: Optional[str] = None
    grader_type: Optional[GraderTypeEnum] = Field(alias='graderType', default=None)
    grader_config: Optional['GraderConfigInput'] = Field(alias='graderConfig', default=None)

class GrpotrainingParamsInput(BaseModel):
    """@private"""
    kl_div_coeff: float = Field(alias='klDivCoeff')
    steps: int = 80

class GuidelineInput(BaseModel):
    """@private"""
    name: str
    description: str

class JudgeConfigInput(BaseModel):
    """@private"""
    model: str
    criteria: str
    examples: List['JudgeExampleInput']

class JudgeCreate(BaseModel):
    """@private"""
    key: Optional[str] = None
    name: str
    criteria: str
    examples: List['JudgeExampleInput'] = Field(default_factory=lambda : [])
    model: str
    metric: Optional[str] = None

class JudgeExampleInput(BaseModel):
    """@private"""
    input: List['JudgeExampleInputTurnEntry']
    reasoning: Optional[str] = None
    output: str
    pass_: bool = Field(alias='pass')
    id: Optional[Any] = None

class JudgeExampleInputTurnEntry(BaseModel):
    """@private"""
    role: str
    content: str

class JudgeTrainingInput(BaseModel):
    """@private"""
    key: str
    version: Optional[int] = None

class JudgeTrainingParamsInput(BaseModel):
    """@private"""
    judges: List['JudgeTrainingInput']

class JudgeUpdate(BaseModel):
    """@private"""
    name: Optional[str] = None
    criteria: Optional[str] = None
    examples: Optional[List['JudgeExampleInput']] = None
    model: Optional[str] = None

class LabelFilter(BaseModel):
    """@private"""
    key: str
    value: Optional[List[str]] = None

class ListCompletionsFilterInput(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    models: Optional[List[str]] = None
    timerange: Optional['TimeRange'] = None
    session_id: Optional[Any] = Field(alias='sessionId', default=None)
    user_id: Optional[Any] = Field(alias='userId', default=None)
    feedbacks: Optional[List['CompletionFeedbackFilterInput']] = None
    comparisons: Optional[List['CompletionComparisonFilterInput']] = None
    labels: Optional[List['LabelFilter']] = None
    prompt_hash: Optional[str] = Field(alias='promptHash', default=None)
    completion_id: Optional[Any] = Field(alias='completionId', default=None)
    source: Optional[List[CompletionSource]] = None

class MetricCreate(BaseModel):
    """@private"""
    name: str
    key: Optional[str] = None
    kind: MetricKind
    scoring_type: MetricScoringType = Field(alias='scoringType', default=MetricScoringType.HIGHER_IS_BETTER)
    description: Optional[str] = None

class MetricGetOrCreate(BaseModel):
    """@private"""
    existing: Optional[str] = None
    new: Optional['MetricCreate'] = None

class MetricLink(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    metric: str

class MetricTrainingParamsInput(BaseModel):
    """@private"""
    metric_key: str = Field(alias='metricKey')
    metric_metadata: Optional['MetricTrainingParamsMetadata'] = Field(alias='metricMetadata', default=None)

class MetricTrainingParamsMetadata(BaseModel):
    """@private"""
    scalar_metric: Optional['ScalarMetricConfigInput'] = Field(alias='scalarMetric', default=None)

class MetricTrendInput(BaseModel):
    """@private"""
    timerange: Optional['TimeRange'] = None
    aggregation: MetricAggregation = MetricAggregation.AVERAGE

class MetricUnlink(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    metric: str

class ModelComputeConfigInput(BaseModel):
    """@private"""
    tp: Optional[int] = None
    kv_cache_len: Optional[int] = Field(alias='kvCacheLen', default=None)
    max_seq_len: Optional[int] = Field(alias='maxSeqLen', default=None)

class ModelFilter(BaseModel):
    """@private"""
    in_storage: Optional[bool] = Field(alias='inStorage', default=None)
    available: Optional[bool] = None
    trainable: Optional[bool] = None
    kind: Optional[List[ModelKindFilter]] = None
    view_all: Optional[bool] = Field(alias='viewAll', default=None)
    online: Optional[List[ModelOnline]] = None

class ModelPlacementInput(BaseModel):
    """@private"""
    compute_pools: List[str] = Field(alias='computePools')
    max_ttft_ms: Optional[int] = Field(alias='maxTtftMs', default=None)

class ModelProviderDataInput(BaseModel):
    """@private"""
    azure: Optional['AzureProviderDataInput'] = None
    open_ai: Optional['OpenAIProviderDataInput'] = Field(alias='openAI', default=None)
    google: Optional['GoogleProviderDataInput'] = None
    anthropic: Optional['AnthropicProviderDataInput'] = None
    nvidia: Optional['NvidiaProviderDataInput'] = None

class ModelServiceDisconnect(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    model_service: str = Field(alias='modelService')

class ModelServiceFilter(BaseModel):
    """@private"""
    model: Optional[str] = None
    kind: Optional[List[ModelKindFilter]] = None

class ModelServiceWithParams(BaseModel):
    """@private"""
    id_or_key: str = Field(alias='idOrKey')
    create_params: Optional['GenerateParameters'] = Field(alias='createParams', default=None)

class NvidiaProviderDataInput(BaseModel):
    """@private"""
    external_model_id: str = Field(alias='externalModelId')
    endpoint: str

class OpenAIProviderDataInput(BaseModel):
    """@private"""
    api_key: str = Field(alias='apiKey')
    external_model_id: OpenAIModel = Field(alias='externalModelId')

class OrderPair(BaseModel):
    """@private"""
    field: str
    order: SortDirection

class PpotrainingParamsInput(BaseModel):
    """@private"""
    kl_div_coeff: float = Field(alias='klDivCoeff')
    steps: int = 100

class PrebuiltConfigInput(BaseModel):
    """@private"""
    key: str
    model: str

class PrebuiltJudgeCreate(BaseModel):
    """@private"""
    key: Optional[str] = None
    name: str
    model: str
    prebuilt_criteria_key: PrebuiltCriteriaKey = Field(alias='prebuiltCriteriaKey')

class RagdataGenerationConfig(BaseModel):
    """@private"""
    chunks_per_question: int = Field(alias='chunksPerQuestion')
    model: str
    system_prompt: Optional[str] = Field(alias='systemPrompt', default=None)

class RemoteEnvCreate(BaseModel):
    """@private"""
    url: str
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class RemoteEnvEvaluation(BaseModel):
    """@private"""
    remote_env: str = Field(alias='remoteEnv')
    datasource: 'SampleDatasourceInput'
    metric: 'MetricGetOrCreate'

class RewardServerTrainingParamsInput(BaseModel):
    """@private"""
    remote_env: str = Field(alias='remoteEnv')

class RoleCreate(BaseModel):
    """@private"""
    key: Optional[str] = None
    name: str
    permissions: List[str]

class SampleConfigInput(BaseModel):
    """@private"""
    feedback_type: Optional[FeedbackTypeInput] = Field(alias='feedbackType', default=None)
    datasource: 'SampleDatasourceInput'

class SampleDatasourceCompletions(BaseModel):
    """@private"""
    selection_type: SelectionTypeInput = Field(alias='selectionType')
    filter: Optional['ListCompletionsFilterInput'] = None
    max_samples: Optional[int] = Field(alias='maxSamples', default=None)
    replay_interactions: Optional[bool] = Field(alias='replayInteractions', default=None)

class SampleDatasourceDataset(BaseModel):
    """@private"""
    dataset: str

class SampleDatasourceInput(BaseModel):
    """@private"""
    completions: Optional['SampleDatasourceCompletions'] = None
    dataset: Optional['SampleDatasourceDataset'] = None

class ScalarMetricConfigInput(BaseModel):
    """@private"""
    threshold: Optional[float] = None

class SftparamsInput(BaseModel):
    """@private"""
    empty: Optional[str] = None

class SystemPromptTemplateCreate(BaseModel):
    """@private"""
    name: str
    template: str

class SystemPromptTemplateUpdate(BaseModel):
    """@private"""
    system_prompt_template: Any = Field(alias='systemPromptTemplate')
    name: Optional[str] = None
    template: str
    update_model_services: bool = Field(alias='updateModelServices', default=False)

class TeamCreate(BaseModel):
    """@private"""
    key: Optional[str] = None
    name: str

class TeamMemberRemove(BaseModel):
    """@private"""
    user: str
    team: str

class TeamMemberSet(BaseModel):
    """@private"""
    user: str
    team: str
    role: str

class TimeRange(BaseModel):
    """@private"""
    from_: int | str = Field(alias='from')
    to: int | str

class TimeseriesInput(BaseModel):
    """@private"""
    interval: TimeseriesInterval
    timerange: Optional['TimeRange'] = None
    timezone: Optional[str] = None
    by_model: bool = Field(alias='byModel', default=False)
    aggregation: MetricAggregation = MetricAggregation.AVERAGE

class TrainingConfigInput(BaseModel):
    """@private"""
    base_training_params: 'BaseTrainingParamsInput' = Field(alias='baseTrainingParams')
    training_metadata: 'TrainingMetadataInput' = Field(alias='trainingMetadata')
    training_objective: 'TrainingObjectiveInput' = Field(alias='trainingObjective')

class TrainingJobInput(BaseModel):
    """@private"""
    model: str
    use_case: str = Field(alias='useCase')
    name: Optional[str] = None
    config: 'AdaptRequestConfigInput'
    compute_pool: Optional[str] = Field(alias='computePool', default=None)
    wait: bool = False

class TrainingMetadataInput(BaseModel):
    """@private"""
    training_type: TrainingMetadataInputTrainingType = Field(alias='trainingType')
    alignment_method: TrainingMetadataInputAlignmentMethod = Field(alias='alignmentMethod')
    parameters: Optional['TrainingMetadataInputParameters'] = None

class TrainingMetadataInputParameters(BaseModel):
    """@private"""
    dpo: Optional['DpotrainingParamsInput'] = None
    ppo: Optional['PpotrainingParamsInput'] = None
    grpo: Optional['GrpotrainingParamsInput'] = None

class TrainingObjectiveInput(BaseModel):
    """@private"""
    metric: Optional['MetricTrainingParamsInput'] = None
    judges: Optional['JudgeTrainingParamsInput'] = None
    reward_server: Optional['RewardServerTrainingParamsInput'] = Field(alias='rewardServer', default=None)
    sft: Optional['SftparamsInput'] = None

class UnitConfigInput(BaseModel):
    """@private"""
    symbol: str
    position: UnitPosition

class UpdateCompletion(BaseModel):
    """@private"""
    id: Any
    remove_labels: Optional[List['CompletionLabelValue']] = Field(alias='removeLabels', default=None)
    add_labels: Optional[List['CompletionLabelValue']] = Field(alias='addLabels', default=None)
    set_labels: Optional[List['CompletionLabelValue']] = Field(alias='setLabels', default=None)
    metadata: Optional[Any] = None

class UpdateModelService(BaseModel):
    """@private"""
    use_case: str = Field(alias='useCase')
    model_service: str = Field(alias='modelService')
    is_default: Optional[bool] = Field(alias='isDefault', default=None)
    attached: Optional[bool] = None
    desired_online: Optional[bool] = Field(alias='desiredOnline', default=None)
    name: Optional[str] = None
    system_prompt_template: Optional[Any] = Field(alias='systemPromptTemplate', default=None)
    placement: Optional['ModelPlacementInput'] = None

class UpdateRecipeInput(BaseModel):
    """@private"""
    name: Optional[str] = None
    description: Optional[str] = None

class UsageFilterInput(BaseModel):
    """@private"""
    model_id: Any = Field(alias='modelId')
    timerange: 'TimeRange'
    unit: DateBucketUnit

class UsagePerUseCaseFilterInput(BaseModel):
    """@private"""
    model_id: Any = Field(alias='modelId')
    timerange: 'TimeRange'

class UseCaseCreate(BaseModel):
    """@private"""
    name: str
    team: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None
    gradient_color: Optional[str] = Field(alias='gradientColor', default=None)
    metadata: Optional['UseCaseMetadataInput'] = None
    settings: Optional['UseCaseSettingsInput'] = None

class UseCaseFilter(BaseModel):
    """@private"""
    is_archived: Optional[bool] = Field(alias='isArchived', default=None)

class UseCaseMetadataInput(BaseModel):
    """@private"""
    emoji: Optional['EmojiInput'] = None

class UseCaseSettingsInput(BaseModel):
    """@private"""
    default_metric: Optional[str] = Field(alias='defaultMetric', default=None)

class UseCaseShareInput(BaseModel):
    """@private"""
    team: str
    role: str
    is_owner: bool = Field(alias='isOwner')

class UseCaseShares(BaseModel):
    """@private"""
    shares: List['UseCaseShareInput']

class UseCaseUpdate(BaseModel):
    """@private"""
    name: Optional[str] = None
    description: Optional[str] = None
    widgets: Optional[List['WidgetInput']] = None
    metadata: Optional['UseCaseMetadataInput'] = None
    settings: Optional['UseCaseSettingsInput'] = None
    is_archived: Optional[bool] = Field(alias='isArchived', default=None)

class WidgetInput(BaseModel):
    """@private"""
    title: str
    metric: str
    aggregation: MetricAggregation
    unit: 'UnitConfigInput'
AdaptRequestConfigInput.model_rebuild()
AddExternalModelInput.model_rebuild()
AijudgeEvaluation.model_rebuild()
AttachModel.model_rebuild()
CustomRecipe.model_rebuild()
CustomRecipeTrainingJobInput.model_rebuild()
DatasetGenerate.model_rebuild()
DatasetGenerationConfig.model_rebuild()
EvaluationCreate.model_rebuild()
EvaluationKind.model_rebuild()
EvaluationRecipeInput.model_rebuild()
EvaluationV2CreateInput.model_rebuild()
FeedbackFilterInput.model_rebuild()
GraderConfigInput.model_rebuild()
GraderCreateInput.model_rebuild()
GraderUpdateInput.model_rebuild()
JudgeConfigInput.model_rebuild()
JudgeCreate.model_rebuild()
JudgeExampleInput.model_rebuild()
JudgeTrainingParamsInput.model_rebuild()
JudgeUpdate.model_rebuild()
ListCompletionsFilterInput.model_rebuild()
MetricGetOrCreate.model_rebuild()
MetricTrainingParamsInput.model_rebuild()
MetricTrainingParamsMetadata.model_rebuild()
MetricTrendInput.model_rebuild()
ModelProviderDataInput.model_rebuild()
ModelServiceWithParams.model_rebuild()
RemoteEnvEvaluation.model_rebuild()
SampleConfigInput.model_rebuild()
SampleDatasourceCompletions.model_rebuild()
SampleDatasourceInput.model_rebuild()
TimeseriesInput.model_rebuild()
TrainingConfigInput.model_rebuild()
TrainingJobInput.model_rebuild()
TrainingMetadataInput.model_rebuild()
TrainingMetadataInputParameters.model_rebuild()
TrainingObjectiveInput.model_rebuild()
UpdateCompletion.model_rebuild()
UpdateModelService.model_rebuild()
UsageFilterInput.model_rebuild()
UsagePerUseCaseFilterInput.model_rebuild()
UseCaseCreate.model_rebuild()
UseCaseMetadataInput.model_rebuild()
UseCaseShares.model_rebuild()
UseCaseUpdate.model_rebuild()
WidgetInput.model_rebuild()