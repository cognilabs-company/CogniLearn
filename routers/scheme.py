from pydantic import BaseModel
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



