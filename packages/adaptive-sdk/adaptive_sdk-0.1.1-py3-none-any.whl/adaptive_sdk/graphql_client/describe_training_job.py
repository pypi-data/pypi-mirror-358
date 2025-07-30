from typing import Optional
from pydantic import Field
from .base_model import BaseModel
from .fragments import TrainingJobData

class DescribeTrainingJob(BaseModel):
    """@public"""
    training_job: Optional['DescribeTrainingJobTrainingJob'] = Field(alias='trainingJob')

class DescribeTrainingJobTrainingJob(TrainingJobData):
    """@public"""
    pass
DescribeTrainingJob.model_rebuild()