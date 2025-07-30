from typing import List
from .base_model import BaseModel
from .fragments import PartitionData

class ListPartitions(BaseModel):
    """@public"""
    partitions: List['ListPartitionsPartitions']

class ListPartitionsPartitions(PartitionData):
    """@public"""
    pass
ListPartitions.model_rebuild()