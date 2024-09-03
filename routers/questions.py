from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy import func
from utils import get_current_user, is_admin
from database import db_dependency
from model.model import Users, Roles, Questions, Quizzes
from routers.scheme import QuestionRequestModel

router = APIRouter(
    prefix='/questions',
    tags=['questions']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_questions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    return db.query(Questions).all()


@router.get("/get-questions/{name}", status_code=status.HTTP_200_OK)
async def get_question(user: user_dependency, db: db_dependency,
                     name: str):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    question = db.query(Questions).filter(func.lower(Questions.quiz_name) == name.lower()).all()
    if not question:
        raise HTTPException(status_code=404, detail="Not found")

    return_question = db.query(Questions).filter(func.lower(Questions.quiz_name) == name.lower()).all()

    return return_question



@router.post("/add-question", status_code=status.HTTP_201_CREATED)
async def add_question(user: user_dependency, db: db_dependency,
                     request_model: QuestionRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    quiz_check = db.query(Quizzes).filter(Quizzes.id == request_model.quiz_id).first()
    question_check = db.query(Questions).filter(Questions.quiz_id == request_model.quiz_id).first()
    
    if question_check is None and quiz_check is not None:
        if not is_admin(user=user, db=db):
            raise HTTPException(status_code=403, detail="You do not have permissions")

        question_model = Questions(**request_model.model_dump())
        db.add(question_model)
        db.commit()
        return {"message": "Question added successfully"}
    else:
        return {"message": "Question already exist for this lesson or Quiz not exist"}


@router.put("/edit-question/{question_id}")
async def edit_question(user: user_dependency, db: db_dependency,
                      question_text:str, question_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    question_model = db.query(Questions).filter(Questions.id == question_id).first()
    if question_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    question_model.question_text = question_text
    db.add(question_model)
    db.commit()
    return {"message": "Question changed successfully"}



@router.delete("/delete_question/{question_id}")
async def delete_question(user: user_dependency, db: db_dependency, question_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    question_model = db.query(Questions).filter(Questions.id == question_id).first()
    if question_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(question_model)
    db.commit()
    return {"message": "Question deleted successfully"}

