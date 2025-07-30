from __future__ import annotations
from typing import TypedDict, List, Any, TypeAlias, Literal
from typing_extensions import Required, NotRequired


class AdaptRequestConfigInput(TypedDict, total=False):
    output_name: Required[str]
    training_config: Required[TrainingConfigInput]
    sample_config: NotRequired[SampleConfigInput]


class BaseTrainingParamsInput(TypedDict, total=True):
    learning_rate: NotRequired[float]
    num_epochs: NotRequired[int]
    batch_size: NotRequired[int]
    num_validations: NotRequired[int]


class ChatMessage(TypedDict, total=True):
    role: Required[Literal["system", "user", "assistant"]]
    content: Required[str]


class ComparisonCompletion(TypedDict, total=True):
    text: Required[str]
    model: Required[str]


class CompletionComparisonFilterInput(TypedDict, total=True):
    """
    Filter for completion preference feedbacks.

    Args:
        metric: Feedback key logged against.
    """

    metric: Required[str]


class CompletionFeedbackFilterInput(TypedDict, total=False):
    """
    Filter for completion metric feedbacks.

    Args:
        metric: Feedback key logged against.
        gt: >
        gte: >=
        eq: ==
        neq: !=
        lt: <
        lte: <=
        user: Feedbacks logged by `user` id.
    """

    metric: Required[str]
    gt: NotRequired[float]
    gte: NotRequired[float]
    eq: NotRequired[float]
    neq: NotRequired[float]
    lt: NotRequired[float]
    lte: NotRequired[float]
    reasons: NotRequired[List[str]]
    user: NotRequired[Any]


class CompletionLabelFilter(TypedDict, total=False):
    """
    Filter for completion labels.
    """

    key: Required[str]
    value: NotRequired[List[str]]


CompletionSource: TypeAlias = Literal["LIVE", "OFFLINE", "AUTOMATION", "DATASET"]


class CursorPageInput(TypedDict, total=False):
    """
    Paging config.

    Args:
        first: Retrieve first n items starting from the `after` cursor.
        last: Retrieve last n items starting from the `after` cursor, limited to `before` cursor.
        after: Start cursor.
        before: End cursor.
    """

    first: NotRequired[int]
    after: NotRequired[str]
    before: NotRequired[str]
    last: NotRequired[int]


class CustomRecipe(TypedDict, total=True):
    guidelines: Required[List[GuidelineInput]]
    feedback_key: Required[str]


class DpotrainingParamsInput(TypedDict, total=True):
    kl_div_coeff: Required[float]


class EvaluationDatasourceCompletions(TypedDict, total=True):
    """
    Args:
        replay_interactions: If `False`, logged completions are evaluated. If `True`, prompts are replayed, and new completions are evaluated.
    """

    filter: Required["ListCompletionsFilterInput"]
    replay_interactions: bool


class GenerateParameters(TypedDict, total=False):
    stop: NotRequired[List[str]]
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    top_p: NotRequired[float]


class GuidelineInput(TypedDict, total=True):
    name: Required[str]
    description: Required[str]


class GuidelinesTrainingParamsInput(TypedDict, total=True):
    judge_model: Required[str]
    judge_model_prompt: Required[List[GuidelineInput]]


class InteractionFeedbackDict(TypedDict):
    """
    Interaction feedback.

    Args:
        feedback_key: Feedback key to register feedback against.
        value: Metric feedback value.
        details: Optional feedback text details.
    """

    feedback_key: Required[str]
    value: Required[int | float | bool]
    details: NotRequired[str]


class JudgeExampleInput(TypedDict, total=False):
    """
    Example to guide an AI judge's reasoning when evaluating a completion (few-shot prompting).

    Args:
        input: Ordered list of chat messages (role/content) that form the conversation context.
        output: Assistant completion to be evaluated.
        passes: Boolean indicating whether the *output* satisfies the criteria.
        reasoning: Optional free-text with the rationale behind the decision.
    """

    input: Required[List[ChatMessage]]
    output: Required[str]
    passes: Required[bool]
    reasoning: Required[str]


class JudgeTrainingInput(TypedDict, total=False):
    key: Required[str]
    version: NotRequired[int | None]


class JudgeTrainingParamsInput(TypedDict, total=False):
    judges: Required[List["JudgeTrainingInput"]]


class ListCompletionsFilterInput(TypedDict, total=False):
    """
    Filter for listing interactions.

    Args:
        models: Model keys.
        timerange: A timerange in timestamp format.
        user_id: User ID that created interaction.
        feedbacks: TypedDict for metric feedback filtering.
        comparisons: TypedDict for preference feedback filtering.
        labels: TypedDict for completion labels filtering.
        completion_id: Completion id.
        source: Interaction source filter.
    """

    models: NotRequired[List[str]]
    timerange: NotRequired["TimeRange"]
    session_id: NotRequired[Any]
    user_id: NotRequired[Any]
    feedbacks: NotRequired[List["CompletionFeedbackFilterInput"]]
    comparisons: NotRequired[List["CompletionComparisonFilterInput"]]
    labels: NotRequired[List["CompletionLabelFilter"]]
    prompt_hash: NotRequired[str]
    completion_id: NotRequired[Any]
    tags: NotRequired[List[str]]
    source: NotRequired[List[CompletionSource]]


class MetricTrainingParamsInput(TypedDict, total=False):
    metric_key: Required[str]
    metric_metadata: NotRequired["MetricTrainingParamsMetadata"]


class MetricTrainingParamsMetadata(TypedDict, total=False):
    scalar_metric: NotRequired["ScalarMetricConfigInput"]


class ModelComputeConfigInput(TypedDict, total=False):
    tp: NotRequired[int]
    kv_cache_len: NotRequired[int]
    max_seq_len: NotRequired[int]


class ModelFilter(TypedDict, total=False):
    in_storage: NotRequired[bool]
    available: NotRequired[bool]
    trainable: NotRequired[bool]
    kind: NotRequired[List[Literal["Embedding", "Generation"]]]
    view_all: NotRequired[bool]
    online: NotRequired[List[Literal["ONLINE", "OFFLINE", "PENDING", "ERROR"]]]


class ModelPlacementInput(TypedDict, total=False):
    compute_pools: Required[List[str]]
    max_ttft_ms: NotRequired[int]


class GrpotrainingParamsInput(TypedDict, total=True):
    kl_div_coeff: NotRequired[float]
    steps: NotRequired[int]


class PpotrainingParamsInput(TypedDict, total=True):
    kl_div_coeff: NotRequired[float]
    steps: NotRequired[int]


class SampleConfigInput(TypedDict, total=False):
    feedback_type: NotRequired[Literal["DIRECT", "PREFERENCE"]]
    datasource: Required[SampleDatasourceInput]


class SampleDatasourceInput(TypedDict, total=False):
    completions: NotRequired[SampleDatasourceCompletions]
    dataset: NotRequired[SampleDatasourceDataset]


class SampleDatasourceCompletions(TypedDict, total=True):
    selection_type: Required[Literal["ALL", "RANDOM", "LAST"]]
    max_samples: NotRequired[int]
    filter: NotRequired[ListCompletionsFilterInput]
    replay_interactions: NotRequired[bool]


class SampleDatasourceDataset(TypedDict, total=True):
    dataset: Required[str]


class RewardServerInput(TypedDict, total=True):
    remote_env: Required[str]


class ScalarMetricConfigInput(TypedDict, total=False):
    threshold: NotRequired[float]


class SftTrainingParamsInput(TypedDict, total=True):
    pass


class TimeRange(TypedDict, total=False):
    """
    A timerange filter, in Unix timestamp format (ms).

    Args:
        from_: The start timestamp.
        to: The end timestamp.
    """

    from_: Required[int | str]
    to: Required[int | str]


class TrainingConfigInput(TypedDict, total=False):
    base_training_params: NotRequired["BaseTrainingParamsInput"]
    training_metadata: NotRequired["TrainingMetadataInput"]
    training_objective: Required["TrainingObjectiveInput"]


class TrainingMetadataInput(TypedDict, total=False):
    training_type: Required[Literal["PARAMETER_EFFICIENT", "FULL_WEIGHTS"]]
    alignment_method: Required[Literal["PPO", "DPO", "SFT", "GRPO"]]
    parameters: NotRequired["TrainingMetadataInputParameters"]


class TrainingMetadataInputParameters(TypedDict, total=False):
    dpo: NotRequired["DpotrainingParamsInput"]
    ppo: NotRequired["PpotrainingParamsInput"]
    grpo: NotRequired["GrpotrainingParamsInput"]


class TrainingObjectiveInput(TypedDict, total=False):
    metric: NotRequired["MetricTrainingParamsInput"]
    judges: NotRequired["JudgeTrainingParamsInput"]
    sft: NotRequired["SftTrainingParamsInput"]
    reward_server: NotRequired["RewardServerInput"]


class Order(TypedDict, total=False):
    """
    Ordering of interaction list results.

    Args:
        field: On what field to order by.
        order: Ascending or descending; alphabetical for string fields.
    """

    field: Required[str]
    order: Required[Literal["ASC", "DESC"]]
