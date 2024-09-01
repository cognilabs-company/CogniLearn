from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from utils import is_admin, get_current_user, is_student
from database import db_dependency
from model.model import Users, Roles, CourseRatings, Courses
from routers.scheme import CourseRatingRequestModel

router = APIRouter(
    prefix='/course_ratings',
    tags=['course_ratings']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependancy, db: db_dependency):
    if user is None: 
        raise HTTPException(status_code=403, detail="Authentication failed")

    if is_student(user=user, db=db):
        existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == user.get('id')).all()
        if not existing_rating:
            raise HTTPException(status_code=404, detail="You didn't rate yet")
        return db.query(CourseRatings).filter(CourseRatings.user_id == user.get('id')).all()

    if is_admin(db,user):
        return db.query(CourseRatings).all()

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.get("/get/{rate}", status_code=status.HTTP_200_OK)
async def course_rating(user: user_dependancy, db: db_dependency,
                        rate: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if is_student(db=db, user=user) or is_admin(user=user, db=db):
        rated_model = db.query(CourseRatings).filter(CourseRatings.rating == rate).all()
        if not rated_model:
            raise HTTPException(status_code=404, detail="Not found")
        return db.query(CourseRatings).filter(CourseRatings.rating == rate).all()

    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.post("/add")
async def creat_course_rating(user: user_dependancy, db: db_dependency,
                              request_model: CourseRatingRequestModel):
    if user is None:
        raise HTTPException(status_code=403, detail="Not authenticated")

    course_check = db.query(Courses).filter(Courses.id == request_model.course_id).first()
    existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == user.get('id'),
                                                     CourseRatings.course_id == request_model.course_id).all()
    
    if is_student(db=db, user=user):
        if existing_rating:
            raise HTTPException(status_code=403, detail="You have already rated this course")

        if course_check is None:
            raise HTTPException(status_code=403, detail="Course not found")

        course_model = CourseRatings(
            rating =request_model.rating,
            user_id = user.get('id'),
            course_id = request_model.course_id
        )
        db.add(course_model)
        db.commit()
        return {"message": "Course rating added successfully"}
        
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.put("/edit/{course_rating_id}")
async def edit_course_rating(user: user_dependancy, db: db_dependency, course_rating_id: int,
                            rating: int = Path(lt=6, gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if is_student(db=db, user=user):
        course_model = db(CourseRatings).filter(CourseRatings.id == course_rating_id).first()
        if course_model is None:
            raise HTTPException(status_code=404, detail="Not found")

        course_model.rating = rating
        db.add(course_model)
        db.commit()
        return {"message": "Course rating changed successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
        

@router.delete("/delete/{course_rating_id}")
async def delete_course_rating(user: user_dependancy, db: db_dependency, course_rating_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")


    if is_student(db=db, user=user):
        existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == user.get('id'),
                                                    CourseRatings.course_id == course_rating_id).first()
        if existing_rating is None:
            raise HTTPException(status_code=403, detail="This course rating does not belongs to you")

        course_model = db.query(CourseRatings).filter(CourseRatings.id == course_rating_id).first()
        if course_model is None:
            raise HTTPException(status_code=404, detail="Not found")

        db.query(CourseRatings).filter(CourseRatings.id == course_rating_id).delete()
        db.commit()
        return {"message": "Course rating deleted successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
            

    
    
