from typing import Annotated, Any, List, Literal, Optional, Union
from pydantic import Field
from .base_model import BaseModel
from .enums import AbcampaignStatus, CompletionSource, CompletionSourceOutput, DatasetKind, EvaluationJobStatus, FeedbackType, FeedbackTypeOutput, JobStatusOutput, JudgeCapability, MetricKind, MetricScoringType, ModelKindFilter, ModelOnline, PartitionStatus, ProviderName, RemoteEnvStatus, ScriptKind, SelectionTypeOutput, TrainingJobStatus, TrainingMetadataOutputAlignmentMethod, TrainingMetadataOutputTrainingType

class AbCampaignCreateData(BaseModel):
    """@public"""
    id: Any
    key: str
    status: AbcampaignStatus
    begin_date: int = Field(alias='beginDate')

class MetricData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    kind: MetricKind
    description: str
    scoring_type: MetricScoringType = Field(alias='scoringType')
    created_at: int = Field(alias='createdAt')
    has_direct_feedbacks: bool = Field(alias='hasDirectFeedbacks')
    has_comparison_feedbacks: bool = Field(alias='hasComparisonFeedbacks')

class AbCampaignDetailData(AbCampaignCreateData):
    """@public"""
    feedback_type: FeedbackType = Field(alias='feedbackType')
    traffic_split: float = Field(alias='trafficSplit')
    end_date: Optional[int] = Field(alias='endDate')
    metric: Optional['AbCampaignDetailDataMetric']
    use_case: Optional['AbCampaignDetailDataUseCase'] = Field(alias='useCase')
    models: List['AbCampaignDetailDataModels']
    feedbacks: int
    has_enough_feedbacks: bool = Field(alias='hasEnoughFeedbacks')

class AbCampaignDetailDataMetric(MetricData):
    """@public"""
    pass

class AbCampaignDetailDataUseCase(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class AbCampaignDetailDataModels(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class AbCampaignReportData(BaseModel):
    """@public"""
    p_value: Optional[float] = Field(alias='pValue')
    variants: List['AbCampaignReportDataVariants']

class AbCampaignReportDataVariants(BaseModel):
    """@public"""
    variant: 'AbCampaignReportDataVariantsVariant'
    interval: Optional['AbCampaignReportDataVariantsInterval']
    feedbacks: int
    comparisons: Optional[List['AbCampaignReportDataVariantsComparisons']]

class AbCampaignReportDataVariantsVariant(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class AbCampaignReportDataVariantsInterval(BaseModel):
    """@public"""
    start: float
    middle: float
    end: float

class AbCampaignReportDataVariantsComparisons(BaseModel):
    """@public"""
    feedbacks: int
    wins: int
    losses: int
    ties_good: int = Field(alias='tiesGood')
    ties_bad: int = Field(alias='tiesBad')
    variant: 'AbCampaignReportDataVariantsComparisonsVariant'

class AbCampaignReportDataVariantsComparisonsVariant(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class CompletionComparisonFeedbackData(BaseModel):
    """@public"""
    id: Any
    completion: Optional[str]
    source: CompletionSource
    model: Optional['CompletionComparisonFeedbackDataModel']

class CompletionComparisonFeedbackDataModel(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class CompletionData(BaseModel):
    """@public"""
    id: Any
    prompt: str
    chat_messages: Optional[List['CompletionDataChatMessages']] = Field(alias='chatMessages')
    completion: Optional[str]
    source: CompletionSource
    model: Optional['CompletionDataModel']
    direct_feedbacks: List['CompletionDataDirectFeedbacks'] = Field(alias='directFeedbacks')
    comparison_feedbacks: List['CompletionDataComparisonFeedbacks'] = Field(alias='comparisonFeedbacks')
    labels: List['CompletionDataLabels']
    metadata: 'CompletionDataMetadata'
    created_at: int = Field(alias='createdAt')

class CompletionDataChatMessages(BaseModel):
    """@public"""
    role: str
    content: str

class CompletionDataModel(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class CompletionDataDirectFeedbacks(BaseModel):
    """@public"""
    id: Any
    value: float
    metric: Optional['CompletionDataDirectFeedbacksMetric']
    reason: Optional[str]
    details: Optional[str]
    created_at: int = Field(alias='createdAt')

class CompletionDataDirectFeedbacksMetric(MetricData):
    """@public"""
    pass

class CompletionDataComparisonFeedbacks(BaseModel):
    """@public"""
    id: Any
    created_at: int = Field(alias='createdAt')
    usecase: Optional['CompletionDataComparisonFeedbacksUsecase']
    metric: Optional['CompletionDataComparisonFeedbacksMetric']
    prefered_completion: Optional['CompletionDataComparisonFeedbacksPreferedCompletion'] = Field(alias='preferedCompletion')
    other_completion: Optional['CompletionDataComparisonFeedbacksOtherCompletion'] = Field(alias='otherCompletion')

class CompletionDataComparisonFeedbacksUsecase(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class CompletionDataComparisonFeedbacksMetric(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class CompletionDataComparisonFeedbacksPreferedCompletion(CompletionComparisonFeedbackData):
    """@public"""
    pass

class CompletionDataComparisonFeedbacksOtherCompletion(CompletionComparisonFeedbackData):
    """@public"""
    pass

class CompletionDataLabels(BaseModel):
    """@public"""
    key: str
    value: str

class CompletionDataMetadata(BaseModel):
    """@public"""
    parameters: Optional[Any]
    timings: Optional[Any]
    usage: Optional['CompletionDataMetadataUsage']
    system: Optional[Any]

class CompletionDataMetadataUsage(BaseModel):
    """@public"""
    completion_tokens: int = Field(alias='completionTokens')
    prompt_tokens: int = Field(alias='promptTokens')
    total_tokens: int = Field(alias='totalTokens')

class CustomScriptData(BaseModel):
    """@public"""
    id: Any
    key: Optional[str]
    name: str
    content: str
    content_hash: str = Field(alias='contentHash')
    kind: ScriptKind
    created_at: int = Field(alias='createdAt')
    updated_at: Optional[int] = Field(alias='updatedAt')

class DatasetData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    created_at: Any = Field(alias='createdAt')
    kind: DatasetKind
    records: Optional[int]
    metrics_usage: List['DatasetDataMetricsUsage'] = Field(alias='metricsUsage')

class DatasetDataMetricsUsage(BaseModel):
    """@public"""
    feedback_count: int = Field(alias='feedbackCount')
    comparison_count: int = Field(alias='comparisonCount')
    metric: 'DatasetDataMetricsUsageMetric'

class DatasetDataMetricsUsageMetric(MetricData):
    """@public"""
    pass

class ModelData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    online: ModelOnline
    is_external: bool = Field(alias='isExternal')
    provider_name: ProviderName = Field(alias='providerName')
    is_adapter: bool = Field(alias='isAdapter')
    is_training: bool = Field(alias='isTraining')
    created_at: int = Field(alias='createdAt')
    kind: ModelKindFilter
    size: Optional[str]
    compute_config: Optional['ModelDataComputeConfig'] = Field(alias='computeConfig')

class ModelDataComputeConfig(BaseModel):
    """@public"""
    tp: int
    kv_cache_len: int = Field(alias='kvCacheLen')
    max_seq_len: int = Field(alias='maxSeqLen')

class ModelServiceData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    model: 'ModelServiceDataModel'
    attached: bool
    is_default: bool = Field(alias='isDefault')
    desired_online: bool = Field(alias='desiredOnline')
    created_at: int = Field(alias='createdAt')

class ModelServiceDataModel(ModelData):
    """@public"""
    backbone: Optional['ModelServiceDataModelBackbone']

class ModelServiceDataModelBackbone(ModelData):
    """@public"""
    pass

class EvaluationReportData(BaseModel):
    """@public"""
    model_service: 'EvaluationReportDataModelService' = Field(alias='modelService')
    dataset: Optional['EvaluationReportDataDataset']
    metric: 'EvaluationReportDataMetric'
    mean: Optional[float]
    feedback_count: int = Field(alias='feedbackCount')

class EvaluationReportDataModelService(ModelServiceData):
    """@public"""
    pass

class EvaluationReportDataDataset(DatasetData):
    """@public"""
    pass

class EvaluationReportDataMetric(MetricData):
    """@public"""
    pass

class JobStageOutputData(BaseModel):
    """@public"""
    name: str
    status: JobStatusOutput
    parent: Optional[str]
    stage_id: int = Field(alias='stageId')
    info: Optional[Annotated[Union['JobStageOutputDataInfoTrainingJobStageOutput', 'JobStageOutputDataInfoEvalJobStageOutput', 'JobStageOutputDataInfoBatchInferenceJobStageOutput'], Field(discriminator='typename__')]]
    started_at: Optional[int] = Field(alias='startedAt')
    ended_at: Optional[int] = Field(alias='endedAt')

class JobStageOutputDataInfoTrainingJobStageOutput(BaseModel):
    """@public"""
    typename__: Literal['TrainingJobStageOutput'] = Field(alias='__typename')
    monitoring_link: Optional[str] = Field(alias='monitoringLink')
    total_num_samples: Optional[int] = Field(alias='totalNumSamples')
    processed_num_samples: Optional[int] = Field(alias='processedNumSamples')
    checkpoints: List[str]

class JobStageOutputDataInfoEvalJobStageOutput(BaseModel):
    """@public"""
    typename__: Literal['EvalJobStageOutput'] = Field(alias='__typename')
    total_num_samples: Optional[int] = Field(alias='totalNumSamples')
    processed_num_samples: Optional[int] = Field(alias='processedNumSamples')
    monitoring_link: Optional[str] = Field(alias='monitoringLink')

class JobStageOutputDataInfoBatchInferenceJobStageOutput(BaseModel):
    """@public"""
    typename__: Literal['BatchInferenceJobStageOutput'] = Field(alias='__typename')
    total_num_samples: Optional[int] = Field(alias='totalNumSamples')
    processed_num_samples: Optional[int] = Field(alias='processedNumSamples')
    monitoring_link: Optional[str] = Field(alias='monitoringLink')

class JudgeData(BaseModel):
    """@public"""
    id: str
    key: str
    version: int
    name: str
    criteria: Optional[str]
    prebuilt: Optional[str]
    examples: Optional[List['JudgeDataExamples']]
    capabilities: List[JudgeCapability]
    model: 'JudgeDataModel'
    use_case_id: Any = Field(alias='useCaseId')
    metric: 'JudgeDataMetric'
    created_at: int = Field(alias='createdAt')
    updated_at: int = Field(alias='updatedAt')

class JudgeDataExamples(BaseModel):
    """@public"""
    input: List['JudgeDataExamplesInput']
    output: str
    pass_: bool = Field(alias='pass')
    reasoning: Optional[str]

class JudgeDataExamplesInput(BaseModel):
    """@public"""
    role: str
    content: str

class JudgeDataModel(ModelData):
    """@public"""
    pass

class JudgeDataMetric(MetricData):
    """@public"""
    pass

class MetricWithContextData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    kind: MetricKind
    description: str
    scoring_type: MetricScoringType = Field(alias='scoringType')
    created_at: Any = Field(alias='createdAt')

class UseCaseData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    description: str
    created_at: int = Field(alias='createdAt')
    metrics: List['UseCaseDataMetrics']
    model_services: List['UseCaseDataModelServices'] = Field(alias='modelServices')

class UseCaseDataMetrics(MetricWithContextData):
    """@public"""
    pass

class UseCaseDataModelServices(ModelServiceData):
    """@public"""
    pass

class EvaluationJobData(BaseModel):
    """@public"""
    id: Any
    name: str
    status: EvaluationJobStatus
    created_at: int = Field(alias='createdAt')
    started_at: Optional[int] = Field(alias='startedAt')
    ended_at: Optional[int] = Field(alias='endedAt')
    duration_ms: Optional[int] = Field(alias='durationMs')
    model_services: List['EvaluationJobDataModelServices'] = Field(alias='modelServices')
    judges: List['EvaluationJobDataJudges']
    judge_models: List['EvaluationJobDataJudgeModels'] = Field(alias='judgeModels')
    stages: List['EvaluationJobDataStages']
    use_case: Optional['EvaluationJobDataUseCase'] = Field(alias='useCase')
    reports: List['EvaluationJobDataReports']
    dataset: Optional['EvaluationJobDataDataset']
    created_by: Optional['EvaluationJobDataCreatedBy'] = Field(alias='createdBy')

class EvaluationJobDataModelServices(ModelServiceData):
    """@public"""
    pass

class EvaluationJobDataJudges(JudgeData):
    """@public"""
    pass

class EvaluationJobDataJudgeModels(ModelData):
    """@public"""
    pass

class EvaluationJobDataStages(JobStageOutputData):
    """@public"""
    pass

class EvaluationJobDataUseCase(UseCaseData):
    """@public"""
    pass

class EvaluationJobDataReports(EvaluationReportData):
    """@public"""
    pass

class EvaluationJobDataDataset(DatasetData):
    """@public"""
    pass

class EvaluationJobDataCreatedBy(BaseModel):
    """@public"""
    id: Any
    email: str
    name: str

class ListCompletionsFilterOutputData(BaseModel):
    """@public"""
    use_case: str = Field(alias='useCase')
    models: Optional[List[str]]
    timerange: Optional['ListCompletionsFilterOutputDataTimerange']
    feedbacks: Optional[List['ListCompletionsFilterOutputDataFeedbacks']]
    labels: Optional[List['ListCompletionsFilterOutputDataLabels']]
    tags: Optional[List[str]]
    source: Optional[List[CompletionSourceOutput]]

class ListCompletionsFilterOutputDataTimerange(BaseModel):
    """@public"""
    from_: Any = Field(alias='from')
    to: Any

class ListCompletionsFilterOutputDataFeedbacks(BaseModel):
    """@public"""
    metric: str

class ListCompletionsFilterOutputDataLabels(BaseModel):
    """@public"""
    key: str
    value: Optional[List[str]]

class MetricDataAdmin(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    kind: MetricKind
    description: str
    scoring_type: MetricScoringType = Field(alias='scoringType')
    use_cases: List['MetricDataAdminUseCases'] = Field(alias='useCases')
    created_at: int = Field(alias='createdAt')
    has_direct_feedbacks: bool = Field(alias='hasDirectFeedbacks')
    has_comparison_feedbacks: bool = Field(alias='hasComparisonFeedbacks')

class MetricDataAdminUseCases(BaseModel):
    """@public"""
    id: Any
    name: str
    key: str
    description: str

class ModelDataAdmin(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    online: ModelOnline
    use_cases: List['ModelDataAdminUseCases'] = Field(alias='useCases')
    is_external: bool = Field(alias='isExternal')
    provider_name: ProviderName = Field(alias='providerName')
    is_adapter: bool = Field(alias='isAdapter')
    is_training: bool = Field(alias='isTraining')
    created_at: int = Field(alias='createdAt')
    kind: ModelKindFilter
    size: Optional[str]

class ModelDataAdminUseCases(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str

class PartitionData(BaseModel):
    """@public"""
    id: Any
    key: str
    compute_pool: Optional['PartitionDataComputePool'] = Field(alias='computePool')
    status: PartitionStatus
    url: str
    world_size: int = Field(alias='worldSize')
    gpu_types: str = Field(alias='gpuTypes')
    created_at: int = Field(alias='createdAt')
    online_models: List['PartitionDataOnlineModels'] = Field(alias='onlineModels')

class PartitionDataComputePool(BaseModel):
    """@public"""
    key: str
    name: str

class PartitionDataOnlineModels(ModelData):
    """@public"""
    pass

class RemoteEnvData(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    url: str
    description: str
    created_at: int = Field(alias='createdAt')
    version: str
    status: RemoteEnvStatus
    metadata_schema: Optional[Any] = Field(alias='metadataSchema')

class TrainingConfigOutputData(BaseModel):
    """@public"""
    base_training_params: 'TrainingConfigOutputDataBaseTrainingParams' = Field(alias='baseTrainingParams')
    training_metadata: 'TrainingConfigOutputDataTrainingMetadata' = Field(alias='trainingMetadata')
    training_objective: Union['TrainingConfigOutputDataTrainingObjectiveMetricTrainingParamsOutput', 'TrainingConfigOutputDataTrainingObjectiveJudgeTrainingParamsOutput', 'TrainingConfigOutputDataTrainingObjectiveGuidelinesTrainingParamsOutput', 'TrainingConfigOutputDataTrainingObjectiveSfttrainingParamsOutput', 'TrainingConfigOutputDataTrainingObjectiveRewardServerTrainingParamsOutput'] = Field(alias='trainingObjective', discriminator='typename__')

class TrainingConfigOutputDataBaseTrainingParams(BaseModel):
    """@public"""
    learning_rate: float = Field(alias='learningRate')
    num_epochs: int = Field(alias='numEpochs')
    batch_size: int = Field(alias='batchSize')
    num_validations: int = Field(alias='numValidations')

class TrainingConfigOutputDataTrainingMetadata(BaseModel):
    """@public"""
    training_type: TrainingMetadataOutputTrainingType = Field(alias='trainingType')
    alignment_method: TrainingMetadataOutputAlignmentMethod = Field(alias='alignmentMethod')
    parameters: Optional[Annotated[Union['TrainingConfigOutputDataTrainingMetadataParametersDpotrainingParamsOutput', 'TrainingConfigOutputDataTrainingMetadataParametersPpotrainingParamsOutput', 'TrainingConfigOutputDataTrainingMetadataParametersGrpotrainingParamsOutput'], Field(discriminator='typename__')]]

class TrainingConfigOutputDataTrainingMetadataParametersDpotrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['DpotrainingParamsOutput'] = Field(alias='__typename')
    kl_div_coeff: float = Field(alias='klDivCoeff')

class TrainingConfigOutputDataTrainingMetadataParametersPpotrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['PpotrainingParamsOutput'] = Field(alias='__typename')
    kl_div_coeff: float = Field(alias='klDivCoeff')

class TrainingConfigOutputDataTrainingMetadataParametersGrpotrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['GrpotrainingParamsOutput'] = Field(alias='__typename')

class TrainingConfigOutputDataTrainingObjectiveMetricTrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['MetricTrainingParamsOutput'] = Field(alias='__typename')
    metric_key: str = Field(alias='metricKey')
    metric_metadata: Optional[Annotated[Union['TrainingConfigOutputDataTrainingObjectiveMetricTrainingParamsOutputMetricMetadataScalarMetricConfigOutput',], Field(discriminator='typename__')]] = Field(alias='metricMetadata')

class TrainingConfigOutputDataTrainingObjectiveMetricTrainingParamsOutputMetricMetadataScalarMetricConfigOutput(BaseModel):
    """@public"""
    typename__: Literal['ScalarMetricConfigOutput'] = Field(alias='__typename')
    threshold: Optional[float]

class TrainingConfigOutputDataTrainingObjectiveJudgeTrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['JudgeTrainingParamsOutput'] = Field(alias='__typename')

class TrainingConfigOutputDataTrainingObjectiveGuidelinesTrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['GuidelinesTrainingParamsOutput'] = Field(alias='__typename')
    judge_model: str = Field(alias='judgeModel')
    judge_model_prompt: List['TrainingConfigOutputDataTrainingObjectiveGuidelinesTrainingParamsOutputJudgeModelPrompt'] = Field(alias='judgeModelPrompt')

class TrainingConfigOutputDataTrainingObjectiveGuidelinesTrainingParamsOutputJudgeModelPrompt(BaseModel):
    """@public"""
    name: str
    description: str

class TrainingConfigOutputDataTrainingObjectiveSfttrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['SfttrainingParamsOutput'] = Field(alias='__typename')

class TrainingConfigOutputDataTrainingObjectiveRewardServerTrainingParamsOutput(BaseModel):
    """@public"""
    typename__: Literal['RewardServerTrainingParamsOutput'] = Field(alias='__typename')

class TrainingJobData(BaseModel):
    """@public"""
    id: Any
    name: str
    status: TrainingJobStatus
    created_at: int = Field(alias='createdAt')
    started_at: Optional[int] = Field(alias='startedAt')
    ended_at: Optional[int] = Field(alias='endedAt')
    duration_ms: Optional[int] = Field(alias='durationMs')
    stages: List['TrainingJobDataStages']
    parent_model: Optional['TrainingJobDataParentModel'] = Field(alias='parentModel')
    child_model: Optional['TrainingJobDataChildModel'] = Field(alias='childModel')
    use_case: Optional['TrainingJobDataUseCase'] = Field(alias='useCase')
    config: Union['TrainingJobDataConfigAdaptBuiltinRecipeConfigOutput', 'TrainingJobDataConfigAdaptCustomRecipeConfigOutput'] = Field(discriminator='typename__')
    created_by: Optional['TrainingJobDataCreatedBy'] = Field(alias='createdBy')
    error: Optional[str]

class TrainingJobDataStages(JobStageOutputData):
    """@public"""
    pass

class TrainingJobDataParentModel(ModelData):
    """@public"""
    backbone: Optional['TrainingJobDataParentModelBackbone']

class TrainingJobDataParentModelBackbone(ModelData):
    """@public"""
    pass

class TrainingJobDataChildModel(ModelData):
    """@public"""
    backbone: Optional['TrainingJobDataChildModelBackbone']

class TrainingJobDataChildModelBackbone(ModelData):
    """@public"""
    pass

class TrainingJobDataUseCase(UseCaseData):
    """@public"""
    pass

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutput(BaseModel):
    """@public"""
    typename__: Literal['AdaptBuiltinRecipeConfigOutput'] = Field(alias='__typename')
    output_name: str = Field(alias='outputName')
    sample_config: 'TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfig' = Field(alias='sampleConfig')
    training_config: 'TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputTrainingConfig' = Field(alias='trainingConfig')

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfig(BaseModel):
    """@public"""
    feedback_type: Optional[FeedbackTypeOutput] = Field(alias='feedbackType')
    datasource: Union['TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceCompletionsOutput', 'TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceDatasetOutput'] = Field(discriminator='typename__')

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceCompletionsOutput(BaseModel):
    """@public"""
    typename__: Literal['SampleDatasourceCompletionsOutput'] = Field(alias='__typename')
    selection_type: SelectionTypeOutput = Field(alias='selectionType')
    max_samples: Optional[int] = Field(alias='maxSamples')
    filter: Optional['TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceCompletionsOutputFilter']

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceCompletionsOutputFilter(ListCompletionsFilterOutputData):
    """@public"""
    pass

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputSampleConfigDatasourceSampleDatasourceDatasetOutput(BaseModel):
    """@public"""
    typename__: Literal['SampleDatasourceDatasetOutput'] = Field(alias='__typename')
    dataset_key: str = Field(alias='datasetKey')

class TrainingJobDataConfigAdaptBuiltinRecipeConfigOutputTrainingConfig(TrainingConfigOutputData):
    """@public"""
    pass

class TrainingJobDataConfigAdaptCustomRecipeConfigOutput(BaseModel):
    """@public"""
    typename__: Literal['AdaptCustomRecipeConfigOutput'] = Field(alias='__typename')
    output_name: str = Field(alias='outputName')

class TrainingJobDataCreatedBy(BaseModel):
    """@public"""
    id: Any
    email: str
    name: str

class UserData(BaseModel):
    """@public"""
    id: Any
    email: str
    name: str
    created_at: int = Field(alias='createdAt')
    teams: List['UserDataTeams']

class UserDataTeams(BaseModel):
    """@public"""
    team: 'UserDataTeamsTeam'
    role: 'UserDataTeamsRole'

class UserDataTeamsTeam(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    created_at: int = Field(alias='createdAt')

class UserDataTeamsRole(BaseModel):
    """@public"""
    id: Any
    key: str
    name: str
    created_at: int = Field(alias='createdAt')
    permissions: List[str]
AbCampaignCreateData.model_rebuild()
MetricData.model_rebuild()
AbCampaignDetailData.model_rebuild()
AbCampaignReportData.model_rebuild()
CompletionComparisonFeedbackData.model_rebuild()
CompletionData.model_rebuild()
CustomScriptData.model_rebuild()
DatasetData.model_rebuild()
ModelData.model_rebuild()
ModelServiceData.model_rebuild()
EvaluationReportData.model_rebuild()
JobStageOutputData.model_rebuild()
JudgeData.model_rebuild()
MetricWithContextData.model_rebuild()
UseCaseData.model_rebuild()
EvaluationJobData.model_rebuild()
ListCompletionsFilterOutputData.model_rebuild()
MetricDataAdmin.model_rebuild()
ModelDataAdmin.model_rebuild()
PartitionData.model_rebuild()
RemoteEnvData.model_rebuild()
TrainingConfigOutputData.model_rebuild()
TrainingJobData.model_rebuild()
UserData.model_rebuild()