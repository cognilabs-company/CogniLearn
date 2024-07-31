from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
from model.model import Users, Roles
from auth.auth import get_current_user, verify_password, hash_password
from database import db_dependency
from typing import Annotated

router = APIRouter(
    prefix='/users',
    tags=['users']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


class ChangePasswordRequestModel(BaseModel):
    password: str
    new_password: str = Field(min_length=6, max_length=30)


@router.get("/get-all-users", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        return db.query(Users).all()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_request_model: ChangePasswordRequestModel):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not verify_password(user_request_model.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password")

    user_model.hashed_password = hash_password(user_request_model.new_password)
    db.add(user_model)
    db.commit()




