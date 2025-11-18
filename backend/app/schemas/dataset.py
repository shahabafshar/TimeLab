"""
Dataset schemas
"""
from pydantic import BaseModel, ConfigDict, field_serializer, model_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime


class DatasetBase(BaseModel):
    name: str
    filename: str


class DatasetCreate(DatasetBase):
    columns: List[str]
    row_count: int
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DatasetResponse(DatasetBase):
    id: str
    columns: List[str]
    row_count: int
    file_path: Optional[str] = None
    created_at: Union[datetime, str]
    updated_at: Optional[Union[datetime, str]] = None
    
    @field_serializer('created_at', 'updated_at', when_used='json')
    def serialize_datetime(self, value: Optional[datetime], _info) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return value.isoformat()
    
    @model_validator(mode='after')
    def convert_datetime_to_string(self):
        if isinstance(self.created_at, datetime):
            self.created_at = self.created_at.isoformat()
        if self.updated_at is not None and isinstance(self.updated_at, datetime):
            self.updated_at = self.updated_at.isoformat()
        return self
    
    model_config = ConfigDict(from_attributes=True)


class DatasetUploadResponse(BaseModel):
    dataset: DatasetResponse
    validation: Dict[str, Any]
    message: str


class LoadSampleRequest(BaseModel):
    filename: str
