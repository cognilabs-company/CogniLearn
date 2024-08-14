from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils import is_admin
from database import db_dependency
from starlette import status
from model.model import Roles, Users
from utils import get_current_user
from routers.scheme import RoleInfo,RoleRequestModel
from typing import List


router = APIRouter(
    prefix='/roles',
    tags=['roles']
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create-role", status_code=status.HTTP_201_CREATED)
async def create_role(user: user_dependency, db: db_dependency,
                      role_request_model: RoleRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    
    role_exists = db.query(Roles).filter(Roles.role_name == role_request_model.role_name).first()

    if is_admin(db, user):
        if role_exists:
            raise HTTPException(status_code=400, detail="Role already exists")
        role_request_model = Roles(
            role_name = role_request_model.role_name
        )
        db.add(role_request_model)
        db.commit()
        return {'message': 'Role created successfully'}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")

# connect user.role_id to roles.id
@router.post("/give_user_role", status_code=status.HTTP_201_CREATED)
async def give_user_role(user: user_dependency, db: db_dependency, role_id: int, user_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    
    user_exists = db.query(Users).filter(Users.id == user_id).first()
    role_exists = db.query(Roles).filter(Roles.id == role_id).first()
    

    if user_exists is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_exists is None:
        raise HTTPException(status_code=404, detail="Role is not found")

    if is_admin(db, user):
        user_exists.role_id = role_id
        db.add(user_exists)
        db.commit()
        return ["User is " + role_exists.role_name + " now"]
        

        
         


@router.get("/get-all-roles", response_model=List[RoleInfo], status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency,
                  user: user_dependency,
):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    if is_admin(db, user):
        return db.query(Roles).all()

    raise HTTPException(status_code=403, detail="You do not have permissions")



    # if user_role.role_name == "admin" or user_role.role_name == "super admin":
    #     change_role = db.query(Roles).filter(Roles.id == id).first()
    #     change_role.role_name = role_name
    #     db.add(change_role)
    #     db.commit()
    #     return {"message": "User role edited successfully"}
    
   







