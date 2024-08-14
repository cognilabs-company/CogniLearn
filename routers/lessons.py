from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import func
from utils import is_admin
from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, Lessons, LessonRatings
from routers.scheme import LessonRequestModel, EditLessonRequestModel

router = APIRouter(
    prefix='/lessons',
    tags=['lessons']
)

user_dependency = Annotated[dict, Depends(get_current_user)]






@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_lessons(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    # Query to calculate sum and average ratings per lesson
    lesson_ratings = db.query(
        Lessons.id,
        Lessons.lesson_name,
        func.sum(LessonRatings.rating).label("total_ratings"),
        func.avg(LessonRatings.rating).label("average_rating")
    ).join(LessonRatings, Lessons.id == LessonRatings.lesson_id).group_by(Lessons.id).all()

    # Convert results to a list of dictionaries for better readability
    result = [
        {
            "lesson_id": lesson_id,
            "lesson_name": lesson_name,
            "total_ratings": total_ratings,
            "average_rating": round(average_rating, 2) if average_rating is not None else None
        }
        for lesson_id, lesson_name, total_ratings, average_rating in lesson_ratings
    ]
    
    return result


    


@router.get("/get-lesson/{name}", status_code=status.HTTP_200_OK)
async def get_lesson(user: user_dependency, db: db_dependency,
                     name: str = Path(max_length=100)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):

    # current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    # user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    # if user_role.role_name == "admin" or user_role.role_name == "super_admin":
        lessons = db.query(Lessons).filter(func.lower(Lessons.lesson_name) == name.lower()).all()
        
        if lessons is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        return lessons
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.post("/add-lesson", status_code=status.HTTP_201_CREATED)
async def add_lesson(user: user_dependency, db: db_dependency,
                     response_model: LessonRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    
    lesson_model = Lessons(**response_model.model_dump())
    db.add(lesson_model)
    db.commit()
    return {"message": "Lessons added successfully"}

    


@router.put("/edit-lesson/{lesson_id}")
async def edit_lesson(user: user_dependency, db: db_dependency,
                      request_model: EditLessonRequestModel, lesson_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):
        lesson_model = db.query(Lessons).filter(Lessons.id == lesson_id).first()

        if lesson_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        lesson_model.lesson_name = request_model.lesson_name
        lesson_model.duration = request_model.duration
        db.add(lesson_model)
        db.commit()
        return {"message": "lesson changed successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.delete("/delete_lesson/{lesson_id}")
async def delete_lesson(user: user_dependency, db: db_dependency, lesson_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if is_admin(db, user):
        lesson_model = db.query(Lessons).filter(Lessons.id == lesson_id).first()
        if lesson_model is None:
            raise HTTPException(status_code=404, detail="Not Found")

        
        db.delete(lesson_model)
        db.commit()
        return {"message": "Lesson deleted successfully"}

    raise HTTPException(status_code=403, detail="You do not have permissions")
