from fastapi import APIRouter, Depends
from database import db_dependency
from auth.auth import get_current_user
from typing import Annotated
from fastapi.exceptions import HTTPException
from model.model import Users, Roles, Attendance, Group, Courses
from utils import is_teacher, is_admin, is_student

router = APIRouter(
    prefix= '/attendance',
    tags=['attendance']
)


user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.post("/create-group")
async def create_group(user: user_dependancy,
                        db: db_dependency,
                        group_name: str,
                        teacher_id: int,
                        course_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    
    teacher_model = db.query(Users).filter(Users.id == teacher_id).first()
    teacher = {
        "id": teacher_model.id,
    }
    if not is_teacher(user=teacher, db=db):
        raise HTTPException(status_code=404, detail="Teacher not found")

    course = db.query(Courses).filter(Courses.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    group = db.query(Group).filter(Group.group_name == group_name).first()
    if group:
        raise HTTPException(status_code=403, detail="Group is already exists")
    
    group_model = Group(
        course_id = course_id,
        teacher_id = teacher_id,
        group_name = group_name
    )
    db.add(group_model)
    db.commit()
    return {"message": "Group added successfully!"}


@router.get("/get-all-groups")
async def get_all_groups(db: db_dependency):
    return db.query(Group).all()


@router.post("/create-attendance")
async def create_attendance(user: user_dependancy,
                            db: db_dependency,
                            student_id: int,
                            lesson_id: int,
                            group_id: int,
                            status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(user=user, db=db) or not is_teacher(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission!")


    attendance_model = Attendance(
        student_id = student_id,
        lesson_id = lesson_id,
        group_id = group_id,
        status = status
    )
    db.add(attendance_model)
    db.commit()
    return {"message": "You have done attendance!"}


@router.get("/get-group-attendance/{group_id}")
async def get_group_attendance(user: user_dependancy, db: db_dependency, group_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(user=user, db=db) or not is_teacher(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission!")

    return db.query(Attendance).filter(Attendance.group_id == group_id).first()
    
@router.get("/get-all-attendance")
async def get_all_attendance(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(user=user, db=db) or not is_teacher(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission!")

    return db.query(Attendance).all()


@router.put("/change-student-status/{group_id}")
async def change_student_status(user: user_dependancy, 
                                db: db_dependency,
                                group_id: int,
                                status: str,
                                student_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(user=user, db=db) or not is_teacher(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permission!")

    student_status_change = Attendance(
        group_id = group_id,
        student_id = student_id,
        status = status
    )
    db.add(student_status_change)
    db.commit()
    return {"message": f"Student status has been changed from {student_status_change.status} to {status}"}