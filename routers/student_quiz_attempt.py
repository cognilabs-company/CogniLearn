from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, StudentQuizAttempts
from utils import is_admin

router = APIRouter(
    prefix='/student-quiz-attempt',
    tags=['student-quiz-attempt']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get-student-quiz-attempt", status_code=status.HTTP_200_OK)
async def get_student_quiz_attempt(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    if not is_admin(db ,user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    return db.query(StudentQuizAttempts).all()


@router.get("/get-student-quiz-attempt/{request_id}", status_code=status.HTTP_200_OK)
async def get_student_quiz_attempt(user: user_dependancy, db: db_dependency,
                                   request_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    if not is_admin(db ,user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    student_quiz_attempt = db.query(StudentQuizAttempts).filter(StudentQuizAttempts.id == request_id).all()
    if student_quiz_attempt is None:
        raise HTTPException(status_code=404, detail="Not found")

    return db.query(StudentQuizAttempts).filter(StudentQuizAttempts.id == request_id).all()


