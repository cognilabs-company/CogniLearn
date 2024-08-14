from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated


from sqlalchemy import func

from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, StudentQuizAttempts
from routers.scheme import AnswerRequestModel, EditAnswerRequestModel



router = APIRouter(
    prefix='/stdent_quiz_attempt',
    tags=['student_quiz_attempt'] 
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get_student_quiz_attempt", status_code=status.HTTP_200_OK)
async def get_student_quiz_attempt(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super admin":
        return db.query(StudentQuizAttempts).all()
    
    raise HTTPException(status_code=403, detail="You do not have permissions")

@router.get("/get_student_quiz_attempt/{id}", status_code=status.HTTP_200_OK)
async def get_student_quiz_attempt(user: user_dependancy, db: db_dependency, id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super admin":
        student_quiz_attempt = db.query(StudentQuizAttempts).filter(StudentQuizAttempts.id == id).all()
        if student_quiz_attempt is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        return student_quiz_attempt
        
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
