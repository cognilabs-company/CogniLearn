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

    user_role = db.query(Roles).filter(Roles.id == user.get('role_id')).first()
    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # user_count = db.query(Users).count()
    # f'There are[{user_count}]users '
    return db.query(Users).all()


@router.get("/get-user", response_model=UserInfo)
async def get_all(db: db_dependency,
                  user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter(Users.id == user.get('id')).first()






