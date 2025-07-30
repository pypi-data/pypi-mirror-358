from pydantic import Field
from .base_model import BaseModel
from .fragments import DatasetData

class GenerateDataset(BaseModel):
    """@public"""
    generate_dataset: 'GenerateDatasetGenerateDataset' = Field(alias='generateDataset')

class GenerateDatasetGenerateDataset(DatasetData):
    """@public"""
    pass
GenerateDataset.model_rebuild()