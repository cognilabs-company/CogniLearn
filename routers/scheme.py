from datetime import datetime

from pydantic import BaseModel, Field
import enum
from database import db_dependency
from model.model import Roles


class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    username: str
    phone_number: str
    user_photo: str


class RoleInfo(BaseModel):
    id: int
    role_name: str


class RoleRequestModel(BaseModel):
    role_name: str


class CourseRequestModel(BaseModel):
    course_name: str
    duration: int = Field(gt=0)


class EditCourseRequestModel(BaseModel):
    course_name: str
    duration: int = Field(gt=0)
    is_active: bool = Field(default=True)


class GetAllUser(BaseModel):
    id: int
    email: str
    username: str
    name: str
    phone_number: str
    created_at: datetime
    is_active: bool
    user_photo: str
    role_id: int
    role_admin:str

