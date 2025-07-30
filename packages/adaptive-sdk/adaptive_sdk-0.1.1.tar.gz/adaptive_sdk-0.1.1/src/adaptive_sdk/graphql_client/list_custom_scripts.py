from typing import List
from pydantic import Field
from .base_model import BaseModel
from .fragments import CustomScriptData

class ListCustomScripts(BaseModel):
    """@public"""
    custom_scripts: List['ListCustomScriptsCustomScripts'] = Field(alias='customScripts')

class ListCustomScriptsCustomScripts(CustomScriptData):
    """@public"""
    pass
ListCustomScripts.model_rebuild()