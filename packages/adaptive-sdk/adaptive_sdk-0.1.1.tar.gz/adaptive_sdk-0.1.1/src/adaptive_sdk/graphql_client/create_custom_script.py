from pydantic import Field
from .base_model import BaseModel
from .fragments import CustomScriptData

class CreateCustomScript(BaseModel):
    """@public"""
    create_custom_script: 'CreateCustomScriptCreateCustomScript' = Field(alias='createCustomScript')

class CreateCustomScriptCreateCustomScript(CustomScriptData):
    """@public"""
    pass
CreateCustomScript.model_rebuild()