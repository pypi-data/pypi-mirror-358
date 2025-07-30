from enum import Enum

class AbcampaignStatus(str, Enum):
    """@public"""
    WARMUP = 'WARMUP'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'

class AuthProviderKind(str, Enum):
    """@public"""
    OIDC = 'OIDC'

class CompletionGroupBy(str, Enum):
    """@public"""
    MODEL = 'MODEL'
    PROMPT = 'PROMPT'

class CompletionSource(str, Enum):
    """@public"""
    LIVE = 'LIVE'
    OFFLINE = 'OFFLINE'
    AUTOMATION = 'AUTOMATION'
    DATASET = 'DATASET'
    EVALUATION = 'EVALUATION'

class CompletionSourceOutput(str, Enum):
    """@public"""
    LIVE = 'LIVE'
    OFFLINE = 'OFFLINE'
    AUTOMATION = 'AUTOMATION'

class ComputePoolCapability(str, Enum):
    """@public"""
    INFERENCE = 'INFERENCE'
    TRAINING = 'TRAINING'
    EVALUATION = 'EVALUATION'

class DatasetKind(str, Enum):
    """@public"""
    PROMPT = 'PROMPT'
    PROMPT_COMPLETION = 'PROMPT_COMPLETION'
    PROMPT_COMPLETION_FEEDBACK = 'PROMPT_COMPLETION_FEEDBACK'
    PREFERENCE = 'PREFERENCE'

class DatasetSource(str, Enum):
    """@public"""
    UPLOADED = 'UPLOADED'
    GENERATED = 'GENERATED'
    GENERATING = 'GENERATING'

class DateBucketUnit(str, Enum):
    """@public"""
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    QUARTER = 'QUARTER'
    YEAR = 'YEAR'
    NO_GROUP_BY_DATE = 'NO_GROUP_BY_DATE'

class EvaluationJobStatus(str, Enum):
    """@public"""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

class EvaluationType(str, Enum):
    """@public"""
    AI_JUDGE = 'AI_JUDGE'
    REMOTE_ENV = 'REMOTE_ENV'
    GRADERS = 'GRADERS'
    MULTI_AI_JUDGES = 'MULTI_AI_JUDGES'

class ExternalModelProviderName(str, Enum):
    """@public"""
    AZURE = 'AZURE'
    OPEN_AI = 'OPEN_AI'
    GOOGLE = 'GOOGLE'
    ANTHROPIC = 'ANTHROPIC'
    NVIDIA = 'NVIDIA'

class FeedbackType(str, Enum):
    """@public"""
    DIRECT = 'DIRECT'
    COMPARISON = 'COMPARISON'

class FeedbackTypeInput(str, Enum):
    """@public"""
    DIRECT = 'DIRECT'
    PREFERENCE = 'PREFERENCE'

class FeedbackTypeOutput(str, Enum):
    """@public"""
    DIRECT = 'DIRECT'
    PREFERENCE = 'PREFERENCE'

class GraderTypeEnum(str, Enum):
    """@public"""
    JUDGE = 'JUDGE'
    PREBUILT = 'PREBUILT'

class JobKind(str, Enum):
    """@public"""
    TRAINING = 'TRAINING'
    EVALUATION = 'EVALUATION'
    DATASET_GENERATION = 'DATASET_GENERATION'
    MODEL_CONVERSION = 'MODEL_CONVERSION'

class JobStatus(str, Enum):
    """@public"""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

class JobStatusOutput(str, Enum):
    """@public"""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'
    ERROR = 'ERROR'

class JudgeCapability(str, Enum):
    """@public"""
    TRAINING = 'TRAINING'
    EVALUATION = 'EVALUATION'

class MetricAggregation(str, Enum):
    """@public"""
    AVERAGE = 'AVERAGE'
    SUM = 'SUM'
    COUNT = 'COUNT'

class MetricKind(str, Enum):
    """@public"""
    SCALAR = 'SCALAR'
    BOOL = 'BOOL'

class MetricScoringType(str, Enum):
    """@public"""
    HIGHER_IS_BETTER = 'HIGHER_IS_BETTER'
    LOWER_IS_BETTER = 'LOWER_IS_BETTER'

class ModelKindFilter(str, Enum):
    """@public"""
    Embedding = 'Embedding'
    Generation = 'Generation'

class ModelOnline(str, Enum):
    """@public"""
    ONLINE = 'ONLINE'
    PENDING = 'PENDING'
    OFFLINE = 'OFFLINE'
    ERROR = 'ERROR'

class ModelserviceStatus(str, Enum):
    """@public"""
    PENDING = 'PENDING'
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    DETACHED = 'DETACHED'
    TURNED_OFF = 'TURNED_OFF'

class OpenAIModel(str, Enum):
    """@public"""
    GPT41 = 'GPT41'
    GPT4O = 'GPT4O'
    GPT4O_MINI = 'GPT4O_MINI'
    O1 = 'O1'
    O1_MINI = 'O1_MINI'
    O3_MINI = 'O3_MINI'
    GPT4 = 'GPT4'
    GPT4_TURBO = 'GPT4_TURBO'
    GPT3_5_TURBO = 'GPT3_5_TURBO'

class PartitionStatus(str, Enum):
    """@public"""
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'

class PrebuiltCriteriaKey(str, Enum):
    """@public"""
    FAITHFULNESS = 'FAITHFULNESS'
    ANSWER_RELEVANCY = 'ANSWER_RELEVANCY'
    CONTEXT_RELEVANCY = 'CONTEXT_RELEVANCY'

class ProviderName(str, Enum):
    """@public"""
    AZURE = 'AZURE'
    OPEN_AI = 'OPEN_AI'
    HARMONY = 'HARMONY'
    GOOGLE = 'GOOGLE'
    ANTHROPIC = 'ANTHROPIC'
    NVIDIA = 'NVIDIA'

class RemoteEnvStatus(str, Enum):
    """@public"""
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'

class ScriptKind(str, Enum):
    """@public"""
    TRAINING_RECIPE = 'TRAINING_RECIPE'

class SelectionTypeInput(str, Enum):
    """@public"""
    ALL = 'ALL'
    RANDOM = 'RANDOM'
    LAST = 'LAST'

class SelectionTypeOutput(str, Enum):
    """@public"""
    ALL = 'ALL'
    RANDOM = 'RANDOM'
    LAST = 'LAST'

class SortDirection(str, Enum):
    """@public"""
    ASC = 'ASC'
    DESC = 'DESC'

class TimeseriesInterval(str, Enum):
    """@public"""
    HOUR = 'HOUR'
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    QUARTER = 'QUARTER'
    YEAR = 'YEAR'

class TrainingJobStatus(str, Enum):
    """@public"""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

class TrainingMetadataInputAlignmentMethod(str, Enum):
    """@public"""
    DPO = 'DPO'
    PPO = 'PPO'
    SFT = 'SFT'
    GRPO = 'GRPO'

class TrainingMetadataInputTrainingType(str, Enum):
    """@public"""
    FULL_WEIGHTS = 'FULL_WEIGHTS'
    PARAMETER_EFFICIENT = 'PARAMETER_EFFICIENT'

class TrainingMetadataOutputAlignmentMethod(str, Enum):
    """@public"""
    DPO = 'DPO'
    PPO = 'PPO'
    SFT = 'SFT'
    GRPO = 'GRPO'

class TrainingMetadataOutputTrainingType(str, Enum):
    """@public"""
    FULL_WEIGHTS = 'FULL_WEIGHTS'
    PARAMETER_EFFICIENT = 'PARAMETER_EFFICIENT'

class UnitPosition(str, Enum):
    """@public"""
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'