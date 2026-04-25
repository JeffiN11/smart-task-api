from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.task import Priority, Status


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Status = Field(default=Status.todo)

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: Status
    priority: Priority
    ai_reasoning: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    total: int
    tasks: list[TaskResponse]
