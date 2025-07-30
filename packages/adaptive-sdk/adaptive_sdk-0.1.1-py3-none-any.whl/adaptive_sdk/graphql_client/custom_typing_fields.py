from .base_operation import GraphQLField

class AbReportGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AbReportGraphQLField':
        self._alias = alias
        return self

class AbVariantReportGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AbVariantReportGraphQLField':
        self._alias = alias
        return self

class AbVariantReportComparisonGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AbVariantReportComparisonGraphQLField':
        self._alias = alias
        return self

class AbcampaignGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AbcampaignGraphQLField':
        self._alias = alias
        return self

class ActivityGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ActivityGraphQLField':
        self._alias = alias
        return self

class ActivityOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ActivityOutputGraphQLField':
        self._alias = alias
        return self

class AdaptBuiltinRecipeConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AdaptBuiltinRecipeConfigOutputGraphQLField':
        self._alias = alias
        return self

class AdaptCustomRecipeConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AdaptCustomRecipeConfigOutputGraphQLField':
        self._alias = alias
        return self

class AdaptRequestConfigOutputUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'AdaptRequestConfigOutputUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'AdaptRequestConfigOutputUnion':
        self._alias = alias
        return self

class ApiKeyGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ApiKeyGraphQLField':
        self._alias = alias
        return self

class AuthProviderGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'AuthProviderGraphQLField':
        self._alias = alias
        return self

class BaseTrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'BaseTrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class BatchInferenceJobStageOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'BatchInferenceJobStageOutputGraphQLField':
        self._alias = alias
        return self

class ChatMessageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ChatMessageGraphQLField':
        self._alias = alias
        return self

class ComparisonFeedbackGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ComparisonFeedbackGraphQLField':
        self._alias = alias
        return self

class CompletionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionGraphQLField':
        self._alias = alias
        return self

class CompletionConnectionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionConnectionGraphQLField':
        self._alias = alias
        return self

class CompletionEdgeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionEdgeGraphQLField':
        self._alias = alias
        return self

class CompletionFeedbackFilterOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionFeedbackFilterOutputGraphQLField':
        self._alias = alias
        return self

class CompletionGroupDataGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionGroupDataGraphQLField':
        self._alias = alias
        return self

class CompletionGroupDataConnectionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionGroupDataConnectionGraphQLField':
        self._alias = alias
        return self

class CompletionGroupDataEdgeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionGroupDataEdgeGraphQLField':
        self._alias = alias
        return self

class CompletionGroupFeedbackStatsGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionGroupFeedbackStatsGraphQLField':
        self._alias = alias
        return self

class CompletionHistoryEntryOuputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionHistoryEntryOuputGraphQLField':
        self._alias = alias
        return self

class CompletionLabelGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionLabelGraphQLField':
        self._alias = alias
        return self

class CompletionLabelFilterOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionLabelFilterOutputGraphQLField':
        self._alias = alias
        return self

class CompletionMetadataGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CompletionMetadataGraphQLField':
        self._alias = alias
        return self

class ComputePoolGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ComputePoolGraphQLField':
        self._alias = alias
        return self

class CustomScriptGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'CustomScriptGraphQLField':
        self._alias = alias
        return self

class DatasetGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DatasetGraphQLField':
        self._alias = alias
        return self

class DatasetMetricUsageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DatasetMetricUsageGraphQLField':
        self._alias = alias
        return self

class DatasetValidationOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DatasetValidationOutputGraphQLField':
        self._alias = alias
        return self

class DeleteConfirmGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DeleteConfirmGraphQLField':
        self._alias = alias
        return self

class DirectFeedbackGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DirectFeedbackGraphQLField':
        self._alias = alias
        return self

class DpotrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'DpotrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class EmojiGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EmojiGraphQLField':
        self._alias = alias
        return self

class EvalJobStageOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvalJobStageOutputGraphQLField':
        self._alias = alias
        return self

class EvaluationAnswerRelevancyRecipeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationAnswerRelevancyRecipeGraphQLField':
        self._alias = alias
        return self

class EvaluationContextRelevancyRecipeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationContextRelevancyRecipeGraphQLField':
        self._alias = alias
        return self

class EvaluationCustomRecipeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationCustomRecipeGraphQLField':
        self._alias = alias
        return self

class EvaluationFaithfulnessRecipeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationFaithfulnessRecipeGraphQLField':
        self._alias = alias
        return self

class EvaluationJobGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationJobGraphQLField':
        self._alias = alias
        return self

class EvaluationRecipeUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'EvaluationRecipeUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'EvaluationRecipeUnion':
        self._alias = alias
        return self

class EvaluationReportGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'EvaluationReportGraphQLField':
        self._alias = alias
        return self

class GraderGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'GraderGraphQLField':
        self._alias = alias
        return self

class GraderConfigUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'GraderConfigUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'GraderConfigUnion':
        self._alias = alias
        return self

class GrpotrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'GrpotrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class GuidelineGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'GuidelineGraphQLField':
        self._alias = alias
        return self

class GuidelinesTrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'GuidelinesTrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class InteractionOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'InteractionOutputGraphQLField':
        self._alias = alias
        return self

class IntervalGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'IntervalGraphQLField':
        self._alias = alias
        return self

class JobGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JobGraphQLField':
        self._alias = alias
        return self

class JobDetailsUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'JobDetailsUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'JobDetailsUnion':
        self._alias = alias
        return self

class JobStageInfoOutputUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'JobStageInfoOutputUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'JobStageInfoOutputUnion':
        self._alias = alias
        return self

class JobStageOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JobStageOutputGraphQLField':
        self._alias = alias
        return self

class JudgeGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JudgeGraphQLField':
        self._alias = alias
        return self

class JudgeConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JudgeConfigOutputGraphQLField':
        self._alias = alias
        return self

class JudgeExampleGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JudgeExampleGraphQLField':
        self._alias = alias
        return self

class JudgeTrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'JudgeTrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class LabelKeyUsageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'LabelKeyUsageGraphQLField':
        self._alias = alias
        return self

class LabelUsageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'LabelUsageGraphQLField':
        self._alias = alias
        return self

class LabelValueUsageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'LabelValueUsageGraphQLField':
        self._alias = alias
        return self

class ListCompletionsFilterOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ListCompletionsFilterOutputGraphQLField':
        self._alias = alias
        return self

class MetaObjectGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MetaObjectGraphQLField':
        self._alias = alias
        return self

class MetricGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MetricGraphQLField':
        self._alias = alias
        return self

class MetricActivityGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MetricActivityGraphQLField':
        self._alias = alias
        return self

class MetricTrainingParamsMetadataOutputUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'MetricTrainingParamsMetadataOutputUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'MetricTrainingParamsMetadataOutputUnion':
        self._alias = alias
        return self

class MetricTrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MetricTrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class MetricWithContextGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MetricWithContextGraphQLField':
        self._alias = alias
        return self

class ModelGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ModelGraphQLField':
        self._alias = alias
        return self

class ModelComputeConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ModelComputeConfigOutputGraphQLField':
        self._alias = alias
        return self

class ModelPlacementOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ModelPlacementOutputGraphQLField':
        self._alias = alias
        return self

class ModelServiceGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ModelServiceGraphQLField':
        self._alias = alias
        return self

class MutationRootGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'MutationRootGraphQLField':
        self._alias = alias
        return self

class PageInfoGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PageInfoGraphQLField':
        self._alias = alias
        return self

class PartitionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PartitionGraphQLField':
        self._alias = alias
        return self

class PpotrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PpotrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class PrebuiltConfigDefinitionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PrebuiltConfigDefinitionGraphQLField':
        self._alias = alias
        return self

class PrebuiltConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PrebuiltConfigOutputGraphQLField':
        self._alias = alias
        return self

class PrebuiltCriteriaGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'PrebuiltCriteriaGraphQLField':
        self._alias = alias
        return self

class ProviderListGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ProviderListGraphQLField':
        self._alias = alias
        return self

class QueryRootGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'QueryRootGraphQLField':
        self._alias = alias
        return self

class RemoteEnvGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'RemoteEnvGraphQLField':
        self._alias = alias
        return self

class RemoteEnvTestUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'RemoteEnvTestUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'RemoteEnvTestUnion':
        self._alias = alias
        return self

class RemoteEnvTestOfflineGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'RemoteEnvTestOfflineGraphQLField':
        self._alias = alias
        return self

class RemoteEnvTestOnlineGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'RemoteEnvTestOnlineGraphQLField':
        self._alias = alias
        return self

class RewardServerTrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'RewardServerTrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class RoleGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'RoleGraphQLField':
        self._alias = alias
        return self

class SampleConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SampleConfigOutputGraphQLField':
        self._alias = alias
        return self

class SampleDatasourceCompletionsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SampleDatasourceCompletionsOutputGraphQLField':
        self._alias = alias
        return self

class SampleDatasourceDatasetOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SampleDatasourceDatasetOutputGraphQLField':
        self._alias = alias
        return self

class SampleDatasourceOutputUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'SampleDatasourceOutputUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'SampleDatasourceOutputUnion':
        self._alias = alias
        return self

class ScalarMetricConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ScalarMetricConfigOutputGraphQLField':
        self._alias = alias
        return self

class SessionGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SessionGraphQLField':
        self._alias = alias
        return self

class SettingsGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SettingsGraphQLField':
        self._alias = alias
        return self

class SfttrainingParamsOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SfttrainingParamsOutputGraphQLField':
        self._alias = alias
        return self

class ShareGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'ShareGraphQLField':
        self._alias = alias
        return self

class SystemPromptTemplateGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'SystemPromptTemplateGraphQLField':
        self._alias = alias
        return self

class TeamGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TeamGraphQLField':
        self._alias = alias
        return self

class TeamMemberGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TeamMemberGraphQLField':
        self._alias = alias
        return self

class TeamWithroleGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TeamWithroleGraphQLField':
        self._alias = alias
        return self

class TimeRangeOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TimeRangeOutputGraphQLField':
        self._alias = alias
        return self

class TimeseriesGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TimeseriesGraphQLField':
        self._alias = alias
        return self

class TrainingConfigOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TrainingConfigOutputGraphQLField':
        self._alias = alias
        return self

class TrainingJobGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TrainingJobGraphQLField':
        self._alias = alias
        return self

class TrainingJobStageOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TrainingJobStageOutputGraphQLField':
        self._alias = alias
        return self

class TrainingMetadataOutputGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TrainingMetadataOutputGraphQLField':
        self._alias = alias
        return self

class TrainingMetadataOutputParametersUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'TrainingMetadataOutputParametersUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'TrainingMetadataOutputParametersUnion':
        self._alias = alias
        return self

class TrainingObjectiveOutputUnion(GraphQLField):
    """@private"""

    def on(self, type_name: str, *subfields: GraphQLField) -> 'TrainingObjectiveOutputUnion':
        self._inline_fragments[type_name] = subfields
        return self

    def alias(self, alias: str) -> 'TrainingObjectiveOutputUnion':
        self._alias = alias
        return self

class TrendResultGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'TrendResultGraphQLField':
        self._alias = alias
        return self

class UnitConfigGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UnitConfigGraphQLField':
        self._alias = alias
        return self

class UsageGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UsageGraphQLField':
        self._alias = alias
        return self

class UsageAggregateItemGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UsageAggregateItemGraphQLField':
        self._alias = alias
        return self

class UsageAggregatePerUseCaseItemGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UsageAggregatePerUseCaseItemGraphQLField':
        self._alias = alias
        return self

class UseCaseGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UseCaseGraphQLField':
        self._alias = alias
        return self

class UseCaseItemGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UseCaseItemGraphQLField':
        self._alias = alias
        return self

class UseCaseMetadataGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UseCaseMetadataGraphQLField':
        self._alias = alias
        return self

class UserGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'UserGraphQLField':
        self._alias = alias
        return self

class WidgetGraphQLField(GraphQLField):
    """@private"""

    def alias(self, alias: str) -> 'WidgetGraphQLField':
        self._alias = alias
        return self