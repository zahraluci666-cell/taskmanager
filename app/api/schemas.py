"""
Pydantic schemas — request/response contracts for the API.
"""
import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.core.models import TaskStatus, TaskPriority


# ---------- Task schemas ----------
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[dt.datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[dt.datetime] = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus
    created_at: dt.datetime
    updated_at: dt.datetime


# ---------- Auth schemas ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
