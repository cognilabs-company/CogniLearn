from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import func

from auth.auth import get_current_user
from database import db_dependency
from model.model import Courses

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


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_courses(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        return db.query(Courses).all()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/get-course/{course_name}", status_code=status.HTTP_200_OK)
async def get_course(user: user_dependency, db: db_dependency,
                     courses_name: str = Path(max_length=100)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:

        courses = db.query(Courses).all()
        request = []

        for course in courses:
            if func.lower(course.course_name) == courses_name:
                request.append(course)
            else:
                continue

        if course is None:
            raise HTTPException(status_code=204, detail="Not found")

        return request

    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/add-course", status_code=status.HTTP_201_CREATED)
async def add_course(user: user_dependency, db: db_dependency,
                     request_model: CourseRequestModel):
    if user in None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        course_model = Courses(**request_model.model_dump())
        db.add(course_model)
        db.commit()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.put("/edit-course/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_course(user: user_dependency, db: db_dependency,
                      request_model: EditCourseRequestModel, course_id: int = Path(gt=0)):
    if user in None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        course_model = db.query(Courses).filter(Courses.id == course_id).first()

        if course_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        course_model.course_name = request_model.course_name
        course_model.duration = request_model.duration
        course_model.is_active = request_model.is_active
        db.add(course_model)
        db.commit()

    raise HTTPException(status_code=403, detail="Forbidden")


@router.delete("/delete_course/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(user: user_dependency, db: db_dependency, course_id: int = Path(gt=0)):

    if user in None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get('user_role') == 1 or user.get('user_role') == 2:
        course_model = db.query(Courses).filter(Courses.id == course_id).first()
        if course_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        course_model.is_active = False
        db.add(course_model)
        db.commit()

    raise HTTPException(status_code=403, detail="Forbidden")