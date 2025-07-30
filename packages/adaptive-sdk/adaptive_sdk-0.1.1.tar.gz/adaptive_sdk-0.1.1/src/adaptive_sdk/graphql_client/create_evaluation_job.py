from pydantic import Field
from .base_model import BaseModel
from .fragments import EvaluationJobData

class CreateEvaluationJob(BaseModel):
    """@public"""
    create_evaluation_job: 'CreateEvaluationJobCreateEvaluationJob' = Field(alias='createEvaluationJob')

class CreateEvaluationJobCreateEvaluationJob(EvaluationJobData):
    """@public"""
    pass
CreateEvaluationJob.model_rebuild()