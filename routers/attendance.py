from fastapi import APIRouter, Depends
from database import db_dependency
from auth.auth import get_current_user
from typing import Annotated
from fastapi.exceptions import HTTPException
from model.model import Users, Roles, Attendance, Group, Courses
from utils import is_admin


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
                        student_id: int,
                        course_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    # if not is_admin(db, user):
    #     raise HTTPException(status_code=403, detail="You do not have permission!")
    
    teacher = db.query(Users).filter(Users.id == teacher_id).first()

    if teacher is None:
        raise HTTPException(status_code=403, detail="Teacher not found")
    
    teacher_role = db.query(Roles).filter(Roles.id == teacher.role_id).first()

    if teacher_role.role_name != "teacher":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    student = db.query(Users).filter(Users.id == student_id).first()
    student_role_id = db.query(Roles).filter(Roles.role_name == "student").first()

    print(f"""student_role_id: {student_role_id.id}
          student: {student.role_id}""" )

    if student_role_id.id != student.role_id:
        raise HTTPException(status_code=403, detail="Student not found")
    
    course = db.query(Courses).filter(Courses.id == course_id).first()
    if not course:
        raise HTTPException(status_code=403, detail="Course not found")
    
    group = db.query(Group).filter(Group.group_name == group_name).first()
    if group:
        raise HTTPException(status_code=403, detail="Group is already exists")
    
    group_model = Group(
        student_id = student_id,
        course_id = course_id,
        teacher_id = teacher_id,
        group_name = group_name
    )
    db.add(group_model)
    db.commit()
    return {"message": "group added successfully!"}


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

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "teacher":
        attendance_model = Attendance(
            student_id = student_id,
            lesson_id = lesson_id,
            group_id = group_id,
            status = status
        )
        db.add(attendance_model)
        db.commit()
        return {"message": "You have done attendance!"}
    
    raise HTTPException(status_code=403, detail="You do not have permission!")



@router.get("/get_group_attendance/{group_id}")
async def get_group_attendance(user: user_dependancy, db: db_dependency, group_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "teacher":
        return db.query(Attendance).filter(Attendance.group_id == group_id).first()
    
@router.get("/get-all-attendance")
async def get_all_attendance(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "teacher":
        return db.query(Attendance).all()


@router.put("/change-student-status/{group_id}")
async def change_student_status(user: user_dependancy, 
                                db: db_dependency,
                                group_id: int,
                                status: str,
                                student_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "teacher":
        student_status_change = Attendance(
            group_id = group_id,
            student_id = student_id,
            status = status
        )
        db.add(student_status_change)
        db.commit()
        return {"message": f"Student status has been changed from {student_status_change.status} to {status}"}      