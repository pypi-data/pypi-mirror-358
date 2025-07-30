from typing import Literal, Type
from adaptive_sdk.graphql_client import SampleDatasourceCompletions, SampleDatasourceDataset

SUPPORTED_ALIGNMENT_METHODS = Literal["PPO", "DPO", "GRPO", "SFT"]
SUPPORTED_DATASOURCES = Literal["DATASET", "COMPLETIONS"]
SAMPLE_DATASOURCE_MODEL_MAP: dict[str, Type[SampleDatasourceDataset | SampleDatasourceCompletions]] = {
    "DATASET": SampleDatasourceDataset,
    "COMPLETIONS": SampleDatasourceCompletions,
}
