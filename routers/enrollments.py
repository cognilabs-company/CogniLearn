from auth.auth import get_current_user
from database import db_dependency

from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import func

from model.model import Users, Roles, Enrollments
from routers.scheme import EnrollemntsRequestModel


router = APIRouter(
    prefix='/enrollments',
    tags=['enrollments']
)


user_dependency = Annotated[dict, Depends(get_current_user)]




@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_enrolments(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        return db.query(Enrollments).all()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/get-enrollment/{id}", status_code=status.HTTP_200_OK)
async def get_enrollment(user: user_dependency, db: db_dependency,
                     id: int = Path(max_length=100)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="You do not have permissions")
        
    enrollments = db.query(Enrollments).filter(Enrollments.id == id).all()
        
    if not enrollments:
        raise HTTPException(status_code=404, detail="Not found")
        
    return db.query(Enrollments).filter(Enrollments.id == id).all()


@router.post("/add-enrollment", status_code=status.HTTP_201_CREATED)
async def add_enrollment(user: user_dependency, db: db_dependency,
                     request_model: EnrollemntsRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    
    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        enrollment_model = Enrollments(**request_model.model_dump())
        db.add(enrollment_model)
        db.commit()
        return {"message": "Enrollment added successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.put("/edit-enrollment/{enrollment_id}")
async def edit_enrollment(user: user_dependency, db: db_dependency,
                    owner: str, course: str  , enrollment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        enrollment_model = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()

        if enrollment_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        enrollment_model.owner = owner
        enrollment_model,course = course
        db.add(enrollment_model)
        db.commit()
        return {"message": "enrollment changed successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.delete("/delete_enrollment/{enrollment_id}")
async def delete_enrollment(user: user_dependency, db: db_dependency, enrollment_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        enrollment_model = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()
        if enrollment_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        
        db.delete(enrollment_model)
        db.commit()
        return {"message": "Enrollment deleted successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")
