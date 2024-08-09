from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import func

from utils import get_current_user
from database import db_dependency
from model.model import Courses, Users, Roles

router = APIRouter(
    prefix='/courses',
    tags=['courses']
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class CourseRequestModel(BaseModel):
    course_name: str
    duration: int = Field(gt=0)


class EditCourseRequestModel(BaseModel):
    course_name: str
    duration: int = Field(gt=0)
    is_active: bool = Field(default=True)


@router.get("/get-all-courses")
async def get_all_courses(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return db.query(Courses).all()


@router.get("/get-course/{name}")
async def get_course(
        db: db_dependency,
        user: user_dependency,
        name: str = Path(..., max_length=100)):  # Adjust the return type if needed
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")

    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if not user_role:
        raise HTTPException(status_code=401, detail="User role not found")

    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    courses = db.query(Courses).filter(
        func.lower(Courses.course_name) == name.lower()
    ).all()

    if not courses:
        raise HTTPException(status_code=404, detail="Course not found")

    return courses


@router.post("/add-course", status_code=status.HTTP_201_CREATED)
async def add_course(db: db_dependency, user: user_dependency,
                     request_model: CourseRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    request_model = Courses(**request_model.model_dump())
    db.add(request_model)
    db.commit()
    return {'message': 'Course successfully added'}


@router.put("/edit-course/{course_id}")
async def edit_course(user: user_dependency, db: db_dependency,
                      request_model: EditCourseRequestModel, course_id: int = Path(gt=0)):
    if user in None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    course_model = db.query(Courses).filter(Courses.id == course_id).first()

    if course_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    course_model.course_name = request_model.course_name
    course_model.duration = request_model.duration
    course_model.is_active = request_model.is_active
    db.add(course_model)
    db.commit()
    return {'message': 'Course successfully updated'}


@router.delete("/delete-course/{course_id}")
async def delete_course(user: user_dependency, db: db_dependency, course_id: int = Path(gt=0)):

    if user in None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    course_model = db.query(Courses).filter(Courses.id == course_id).first()
    if course_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    course_model.is_active = False
    db.add(course_model)
    db.commit()
    return {'message': 'Course successfully deleted'}


