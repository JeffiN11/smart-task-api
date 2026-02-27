from pydantic import BaseModel, EmailStr
from typing import Optional

# -------- USER SCHEMAS --------

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str


# -------- TASK SCHEMAS (for later) --------

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