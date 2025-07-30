from typing import Optional
from pydantic import Field
from .base_model import BaseModel
from .fragments import EvaluationJobData

class DescribeEvaluationJob(BaseModel):
    """@public"""
    evaluation_job: Optional['DescribeEvaluationJobEvaluationJob'] = Field(alias='evaluationJob')

class DescribeEvaluationJobEvaluationJob(EvaluationJobData):
    """@public"""
    pass
DescribeEvaluationJob.model_rebuild()