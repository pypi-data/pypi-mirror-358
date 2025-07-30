from pydantic import Field
from .base_model import BaseModel
from .fragments import TrainingJobData

class CreateCustomRecipeTrainingJob(BaseModel):
    """@public"""
    create_custom_recipe_training_job: 'CreateCustomRecipeTrainingJobCreateCustomRecipeTrainingJob' = Field(alias='createCustomRecipeTrainingJob')

class CreateCustomRecipeTrainingJobCreateCustomRecipeTrainingJob(TrainingJobData):
    """@public"""
    pass
CreateCustomRecipeTrainingJob.model_rebuild()