from pydantic import Field
from .base_model import BaseModel
from .fragments import TrainingJobData

class CreateTrainingJob(BaseModel):
    """@public"""
    create_training_job: 'CreateTrainingJobCreateTrainingJob' = Field(alias='createTrainingJob')

class CreateTrainingJobCreateTrainingJob(TrainingJobData):
    """@public"""
    pass
CreateTrainingJob.model_rebuild()