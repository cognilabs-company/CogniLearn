from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy import func
from auth.auth import get_current_user
from database import db_dependency
from model.model import Answers, Questions
from routers.scheme import AnswerRequestModel
from utils import is_admin


router = APIRouter(
    prefix='/answers',
    tags=['answers']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_answers(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    return db.query(Answers).all()


@router.get("/get-answers/{name}", status_code=status.HTTP_200_OK)
async def get_answers(user: user_dependency, db: db_dependency,
                     name: str):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    answer = db.query(Answers).filter(func.lower(Answers.answers_text) == name.lower()).all()
    if not answer:
        raise HTTPException(status_code=404, detail="Not found")
        
    return db.query(Answers).filter(func.lower(Answers.answers_text) == name.lower()).all()


@router.post("/add-answer", status_code=status.HTTP_201_CREATED)
async def add_answer(user: user_dependency, db: db_dependency,
                     request_model: AnswerRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    question_check = db.query(Questions).filter(Questions.id == request_model.question_id).first()
    answer_check = db.query(Answers).filter(Answers.question_id == request_model.question_id).first()
    
    if answer_check is None and question_check is not None:
        if not is_admin(user=user, db=db):
            raise HTTPException(status_code=403, detail="You do not have permissions")

        answer_model = Answers(**request_model.model_dump())
        db.add(answer_model)
        db.commit()
        return {"message": "Answer added successfully"}
    else:
        return {"message": "Answer already exist for this lesson or Question not exist"}


@router.put("/edit-answer/{answer_id}")
async def edit_answer(user: user_dependency, db: db_dependency,
                      answer_text:str, answer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    answer_model = db.query(Answers).filter(Answers.id == answer_id).first()
    if answer_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

    answer_model.answers_text = answer_text
    db.add(answer_model)
    db.commit()
    return {"message": "Answer changed successfully"}



@router.delete("/delete-answer/{answer_id}")
async def delete_answer(user: user_dependency, db: db_dependency,
                        answer_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(user=user, db=db):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    answer_model = db.query(Answers).filter(Answers.id == answer_id).first()
    if answer_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(answer_model)
    db.commit()
    return {"message": "Deleted successfully"}

