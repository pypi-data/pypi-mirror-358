from pydantic import Field
from .base_model import BaseModel

class CancelEvaluationJob(BaseModel):
    """@public"""
    cancel_evaluation_job: str = Field(alias='cancelEvaluationJob')