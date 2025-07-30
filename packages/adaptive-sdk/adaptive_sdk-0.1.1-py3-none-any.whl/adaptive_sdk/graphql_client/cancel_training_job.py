from pydantic import Field
from .base_model import BaseModel

class CancelTrainingJob(BaseModel):
    """@public"""
    cancel_training_job: str = Field(alias='cancelTrainingJob')