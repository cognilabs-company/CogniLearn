from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import db_dependency
from starlette import status
from model.model import Roles, Users
from auth.auth import get_current_user


router = APIRouter(
    prefix='/roles',
    tags=['roles']
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class RoleRequestModel(BaseModel):
    role_name: str


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency, ):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        return db.query(Roles).all()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/create-role", status_code=status.HTTP_201_CREATED)
async def create_role(user: user_dependency, db: db_dependency,
                      role_request_model: RoleRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        role_request_model = Roles(**role_request_model.model_dump())
        db.add(role_request_model)
        db.commit()

    raise HTTPException(status_code=403, detail="Forbidden")


