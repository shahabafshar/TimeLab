"""
Project schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    dataset_id: Optional[str] = None
    model_id: Optional[str] = None
    
    model_config = ConfigDict(protected_namespaces=())


class ProjectResponse(ProjectBase):
    id: str
    dataset_id: Optional[str] = None
    model_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes=True
    )

