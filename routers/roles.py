from fastapi import APIRouter
from pydantic import BaseModel

from database import db_dependency
from starlette import status
from model.model import Roles


router = APIRouter()


class RoleRequestModel(BaseModel):
    role_name: str


@router.get("/roles/get-all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency):
    return db.query(Roles).all()


@router.post("/roles/add-router", status_code=status.HTTP_201_CREATED)
async def create_role(db: db_dependency, role_request_model: RoleRequestModel):

    role_request_model = Roles(
        role_name=role_request_model.role_name
    )

    db.add(role_request_model)
    db.commit()
