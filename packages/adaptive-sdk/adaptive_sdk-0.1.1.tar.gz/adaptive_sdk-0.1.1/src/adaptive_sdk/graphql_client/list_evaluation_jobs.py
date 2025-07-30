from typing import List
from pydantic import Field
from .base_model import BaseModel
from .fragments import EvaluationJobData

class ListEvaluationJobs(BaseModel):
    """@public"""
    evaluation_jobs: List['ListEvaluationJobsEvaluationJobs'] = Field(alias='evaluationJobs')

class ListEvaluationJobsEvaluationJobs(EvaluationJobData):
    """@public"""
    pass
ListEvaluationJobs.model_rebuild()