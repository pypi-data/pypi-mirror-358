from typing import List
from pydantic import Field
from .base_model import BaseModel
from .fragments import TrainingJobData

class ListTrainingJobs(BaseModel):
    """@public"""
    training_jobs: List['ListTrainingJobsTrainingJobs'] = Field(alias='trainingJobs')

class ListTrainingJobsTrainingJobs(TrainingJobData):
    """@public"""
    pass
ListTrainingJobs.model_rebuild()