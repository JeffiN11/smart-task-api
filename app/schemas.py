from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------------- USER SCHEMAS ----------------

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


# ---------------- TASK SCHEMAS ----------------

class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = ""
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskOut(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True