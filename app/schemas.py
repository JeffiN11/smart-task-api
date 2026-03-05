from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

# Tasks for later
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True