from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated

from sqlalchemy import func

from utils import get_current_user, is_admin
from database import db_dependency
from model.model import Courses, Users, Roles, Enrollments
from routers.scheme import CourseRequestModel,EditCourseRequestModel
from routers.scheme import CourseRequestModel, EditCourseRequestModel


router = APIRouter(
    prefix='/courses',
    tags=['courses']
)

user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_courses(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Courses).all()

@router.get("/get-all-for-student", status_code=status.HTTP_200_OK)
async def get_all_for_student(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        return db.query(Enrollments).filter(Enrollments.user_id == current_user.id).all()
    
    raise HTTPException(status_code=403, detail="You do not have any courses yet!")
    
    


@router.get("/get-course/{name}")
async def get_course(
        db: db_dependency,
        user: user_dependency,
        name: str):  # Adjust the return type if needed
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")

    if is_admin(db, user):
       
        courses = db.query(Courses).filter(
            func.lower(Courses.course_name) == name.lower()).all()

        if not courses:
            raise HTTPException(status_code=404, detail="Course not found")

        return courses


@router.post("/add-course", status_code=status.HTTP_201_CREATED)
async def add_course(db: db_dependency, user: user_dependency,
                     request_model: CourseRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    curret_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role_name = db.query(Roles).filter(Roles.id == curret_user.role_id)

    if is_admin(db, user):
        request_model = Courses(**request_model.model_dump())
        db.add(request_model)
        db.commit()
        return {'massage': 'course added'}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.put("/edit-course/{course_id}")
async def edit_course(user: user_dependency, db: db_dependency,
                      request_model: EditCourseRequestModel, course_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):
        course_model = db.query(Courses).filter(Courses.id == course_id).first()

        if course_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        course_model.course_name = request_model.course_name
        course_model.duration = request_model.duration
        db.add(course_model)
        db.commit()
        return {"message": "course changed successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.delete("/delete_course/{course_id}")
async def delete_course(user: user_dependency, db: db_dependency, course_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):
        course_model = db.query(Courses).filter(Courses.id == course_id).first()
        if course_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        
        db.delete(course_model)
        db.commit()
        return {"message": "course deleted successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")

