from datetime import datetime

from pydantic import BaseModel

from auth.auth import get_current_user
from database import db_dependency
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated, Optional

from model.model import Users, Roles, Enrollments, Courses

router = APIRouter(
    prefix='/enrollments',
    tags=['enrollments']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateEnrollmentRequestModel(BaseModel):
    course_id: int


def ShowEnrollment(enrollment_id: int, created_at: datetime,
                   finished_at: datetime, user_id: int, username: str,
                   course_id: int, course_name: str):
    return [
        {'id': enrollment_id},
        {'created_at': created_at},
        {'finished_at': finished_at},
        {'user_id': user_id},
        {'username': username},
        {'course_id': course_id},
        {'course_name': course_name}
    ]

@router.get("/get-all-enrollments")
async def get_all_enrollments(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if user_role.role_name not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return db.query(Enrollments).all()


@router.get("/get-enrollment/{enrollment_id}")
async def get_enrollment(user: user_dependency, db: db_dependency,
                         enrollment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    enrollment = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()

    if enrollment is None:
        raise HTTPException(status_code=404, detail='Not Found')

    show_user = db.query(Users).filter(Enrollments.user_id == enrollment.user_id).first()
    show_course = db.query(Courses).filter(Courses.id == enrollment.course_id).first()

    show_model = ShowEnrollment(enrollment.id, enrollment.created_at, enrollment.finished_at,
                                enrollment.user_id, show_user.username, enrollment.course_id,
                                show_course.course_name)

    return show_model


@router.post("/add-enrollment")
async def add_enrollment(user: user_dependency, db: db_dependency,
                         request_model: CreateEnrollmentRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    enrollment_model = Enrollments(
        finished_at=None,
        course_id=request_model.course_id,
        user_id=user.get('id')
    )
    db.add(enrollment_model)
    db.commit()
    return {'message': 'Enrollment successfully added'}




