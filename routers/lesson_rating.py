from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated


from sqlalchemy import func

from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, LessonRatings, Lessons
from routers.scheme import LessonRatingRequestModel

router = APIRouter(
    prefix='/lesson_ratings',
    tags=['lesson_ratings']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependancy, db: db_dependency):
    if user is None: 
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        existing_rating = db.query(LessonRatings).filter(LessonRatings.user_id == current_user.id).all()
        return existing_rating
    
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.get("/lesson_rating/{lesson_rating}", status_code=status.HTTP_200_OK)
async def lesson_rating(user: user_dependancy, db: db_dependency, lesson_rating: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        lesson_rating = db.query(LessonRatings).filter(LessonRatings.user_id == current_user.id).all()
        if lesson_rating is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        return lesson_rating

    raise HTTPException(status_code=403, detail="You do not have permissions") 



@router.post("/create_lesson_rating")
async def creat_lesson_rating(user: user_dependancy,
                              db: db_dependency,
                              request_model: LessonRatingRequestModel):
    if user is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    existing_rating = db.query(LessonRatings).filter(LessonRatings.user_id == current_user.id,
                                                    LessonRatings.lesson_id == request_model.lesson_id).first()

    if user_role.role_name == "student":
        if existing_rating:
            raise HTTPException(status_code=403, detail="you already rated this lesson")
    
        lesson_model = LessonRatings(
            rating = request_model.rating,
            user_id = current_user.id,
            lesson_id = request_model.lesson_id
            )
        

        db.add(lesson_model)
        db.commit()
        return {"message": "Lesson rating added successfully"}
        
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.put("/edit_lesson_rating/{lesson_rating_id}")
async def edit_lesson_rating(user: user_dependancy, db: db_dependency, lesson_rating_id: int,
                            rating: int = Path(lt=6, gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        lesson_model = db(LessonRatings).filter(LessonRatings.id == lesson_rating_id).first()

        if lesson_model is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        lesson_model.rating = rating
        db.add(lesson_model)
        db.commit()
        return {"message": "Lesson rating changed successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
        

@router.delete("/delete_lesson_rating/{lesson_rating_id}")
async def delete_lesson_rating(user: user_dependancy, db: db_dependency, lesson_rating_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    existing_rating = db.query(LessonRatings).filter(LessonRatings.user_id == current_user.id,
                                                    LessonRatings.course_id == lesson_rating_id).first()

    if user_role.role_name == "student":
        lesson_model = db(LessonRatings).filter(LessonRatings.id == lesson_rating_id).first()
        if lesson_model is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        if not existing_rating:
            raise HTTPException(status_code=403, detail="This lesson rating does not belongs to you")
    
        db.delete(lesson_model)
        db.commit()
        return {"message": "Lesson rating deleted successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
            

    
    
