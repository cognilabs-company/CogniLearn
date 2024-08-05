from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
from model.model import Users, Roles
from utils import get_current_user, verify_password, hash_password
from database import db_dependency
from typing import Annotated
from routers.scheme import UserInfo

router = APIRouter(
    prefix='/users',
    tags=['users']
)


user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/get-all-users", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        user_count = db.query(Users).count()
        return [f'There are [ {user_count} ] users ',
            db.query(Users).all()]

    raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/get-user", response_model=UserInfo)
async def get_all(db: db_dependency,
                  user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter(Users.id == user.get('id')).first()






