from pydantic import Field
from .base_model import BaseModel

class AddHFModel(BaseModel):
    """@public"""
    import_hf_model: str = Field(alias='importHfModel')