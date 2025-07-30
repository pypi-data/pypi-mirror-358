from __future__ import annotations
from typing import TYPE_CHECKING

from .jobs import EvalJobs, AsyncEvalJobs

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class Evaluation:
    def __init__(self, client: Adaptive) -> None:
        self.jobs: EvalJobs = EvalJobs(client)


class AsyncEvaluation:
    def __init__(self, client: AsyncAdaptive) -> None:
        self.jobs: AsyncEvalJobs = AsyncEvalJobs(client)
