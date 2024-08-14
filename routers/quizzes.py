from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated


from sqlalchemy import func

from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, Quizzes
from routers.scheme import QuizRequestModel, EditQuizRequestModel

router = APIRouter(
    prefix='/quizzes',
    tags=['quizzes']
)

user_dependency = Annotated[dict, Depends(get_current_user)]



    

@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_quiz(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        return db.query(Quizzes).all()

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.get("/get-quiz/{name}", status_code=status.HTTP_200_OK)
async def get_quiz(user: user_dependency, db: db_dependency,
                     name: str):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        quizes = db.query(Quizzes).filter(func.lower(Quizzes.quiz_name) == name.lower()).all()
        if quizes is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        return quizes
        
    raise HTTPException(status_code=403, detail="You do not have permissions")
           
                



@router.post("/add-quizz", status_code=status.HTTP_201_CREATED)
async def add_quiz(user: user_dependency, db: db_dependency,
                     request_model: QuizRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    quiz_check = db.query(Quizzes).filter(Quizzes.lesson_id == request_model.lesson_id).first()
    
    if quiz_check is None:
        if user_role.role_name == "admin" or user_role.role_name == "super_admin":
            quiz_model = Quizzes(**request_model.model_dump())
            db.add(quiz_model)
            db.commit()
            return {"message": "Quiz added successfully"}
        
        raise HTTPException(status_code=403, detail="You do not have permissions")

    else:
        return {"message": "quiz already exist for this lesson"}


@router.put("/edit-quiz/{quiz_id}")
async def edit_quiz(user: user_dependency, db: db_dependency,
                      quiz_name:str, quiz_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        quiz_model = db.query(Quizzes).filter(Quizzes.id == quiz_id).first()

        
        if quiz_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        quiz_model.quiz_name = quiz_name
        db.add(quiz_model)
        db.commit()
        return {"message": "quiz changed successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.delete("/delete_quiz/{quiz_id}")
async def delete_quiz(user: user_dependency, db: db_dependency, quiz_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        quiz_model = db.query(Quizzes).filter(Quizzes.id == quiz_id).first()
        if quiz_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        
        db.delete(quiz_model)
        db.commit()
        return {"message": "deleted successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")
