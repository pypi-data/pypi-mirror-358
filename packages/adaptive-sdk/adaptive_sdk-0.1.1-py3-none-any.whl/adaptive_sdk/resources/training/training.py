from __future__ import annotations
from typing import TYPE_CHECKING

from .jobs import TrainingJobs, AsyncTrainingJobs

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class Training:
    def __init__(self, client: Adaptive) -> None:
        self.jobs: TrainingJobs = TrainingJobs(client)


class AsyncTraining:
    def __init__(self, client: AsyncAdaptive) -> None:
        self.jobs: AsyncTrainingJobs = AsyncTrainingJobs(client)
