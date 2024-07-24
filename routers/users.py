from fastapi import APIRouter, status, HTTPException, Depends
from model.model import Users
from auth.auth import get_current_user
from database import db_dependency
from typing import Annotated

router = APIRouter(
    prefix='/users',
    tags=['users']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all-users", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        return db.query(Users).all()

    raise HTTPException(status_code=401, detail="Authentication failed")


@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter(Users.id == user.get('id')).first()




