from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy import func
from utils import get_current_user, is_admin, is_student
from database import db_dependency
from model.model import Courses, Enrollments
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
    
    if not is_student(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission!")

    enrollments = db.query(Enrollments).filter(Enrollments.user_id == user.get('id')).all()
    courses = db.query(Courses).filter(Courses.id == enrollments.course_id).all()
    if not courses:
        raise HTTPException(status_code=403, detail="You do not have course yet!")

    return db.query(Courses).filter(Courses.id == enrollments.course_id).all()


@router.get("/get-course/{name}")
async def get_course( db: db_dependency, user: user_dependency, name: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permission!")

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

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    request_model = Courses(**request_model.model_dump())
    db.add(request_model)
    db.commit()
    return {'massage': 'Course added'}



@router.put("/edit-course/{course_id}")
async def edit_course(user: user_dependency, db: db_dependency,
                      request_model: EditCourseRequestModel, course_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    course_model = db.query(Courses).filter(Courses.id == course_id).first()
    if course_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    course_model.course_name = request_model.course_name
    course_model.duration = request_model.duration
    db.add(course_model)
    db.commit()
    return {"message": "Course changed successfully"}


@router.delete("/delete-course/{course_id}")
async def delete_course(user: user_dependency, db: db_dependency,
                        course_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    course_model = db.query(Courses).filter(Courses.id == course_id).first()
    if course_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(course_model)
    db.commit()
    return {"message": "Course deleted successfully"}


