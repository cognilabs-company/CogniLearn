from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from utils import get_current_user
from database import db_dependency
from model.model import Users, Roles, Teacher


router = APIRouter(
    prefix= '/teacher',
    tags=['teacher']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add-teacher")
async def add_teacher(user: user_dependency, db: db_dependency):
    # Retrieve the role ID for 'teacher'
    role = db.query(Roles).filter(Roles.role_name == "teacher").first()
    if not role:
        return {"Error": "Role 'teacher' not found."}
    
    teacher_role_id = role.id
    
    # Retrieve users with the teacher role ID
    teacher_users = db.query(Users).filter(Users.role_id == teacher_role_id).all()
    
    # Add each user as a teacher
    for user in teacher_users:
        teacher_model = Teacher(
            teacher_id=user.id  # Assuming 'teacher_id' should be set to the user ID
        )
        db.add(teacher_model)
    
    db.commit()

    return {"message": "Teachers added successfully!"}



@router.get("/get-all-teachers")
async def get_all_teachers(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    return db.query(Teacher).all()
    
      
