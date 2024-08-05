from pydantic import BaseModel,Field
from fastapi import Depends, HTTPException, status
from model.model import Users
from jose import jwt, JWTError


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUserRequest(BaseModel):
    email: str
    username: str = Field(max_length=15)
    phone_number: str
    name: str
    user_photo: str
    password: str = Field(min_length=6)
    confirm_password:  str = Field(min_length=6)

