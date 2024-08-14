from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated


from sqlalchemy import func
from utils import is_admin
from auth.auth import get_current_user
from database import db_dependency
from model.model import Users, Roles, CourseRatings
from routers.scheme import CourseRatingRequestModel, EditCourseRatingRequestModel

router = APIRouter(
    prefix='/course_ratings',
    tags=['course_ratings']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependancy, db: db_dependency):
    if user is None: 
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == current_user.id).all()
        return existing_rating
    
    if is_admin(db,user):
        return db.query(CourseRatings).all()
    
    raise HTTPException(status_code=403, detail="You do not have permissions")




@router.get("/course_rating/{course_rating}", status_code=status.HTTP_200_OK)
async def course_rating(user: user_dependancy, db: db_dependency, course_rating: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        course_rating = db.query(CourseRatings).filter(CourseRatings.user_id == current_user.id).all()
        if course_rating is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        return course_rating

    raise HTTPException(status_code=403, detail="You do not have permissions") 



@router.post("/create_course_rating")
async def creat_course_rating(user: user_dependancy, db: db_dependency, request_model: CourseRatingRequestModel):
    if user is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == current_user.id,
                                                    CourseRatings.course_id == request_model.course_id).first()
    
    if user_role.role_name == "student":
        if existing_rating:
            raise HTTPException(status_code=403, detail="you are already rated this course")
        
        course_model = CourseRatings(
            rating =request_model.rating,
            user_id = current_user.id,
            course_id = request_model.course_id
        )
        db.add(course_model)
        db.commit()
        return {"message": "Course rating added successfully"}
        
    raise HTTPException(status_code=403, detail="You do not have permissions")


@router.put("/edit_course_rating/{course_rating_id}")
async def edit_course_rating(user: user_dependancy, db: db_dependency, course_rating_id: int,
                            rating: int = Path(lt=6, gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "student":
        course_model = db(CourseRatings).filter(CourseRatings.id == course_rating_id).first()

        if course_model is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        course_model.rating = rating
        db.add(course_model)
        db.commit()
        return {"message": "Course rating changed successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
        

@router.delete("/delete_course_rating/{course_rating_id}")
async def delete_course_rating(user: user_dependancy, db: db_dependency, course_rating_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    existing_rating = db.query(CourseRatings).filter(CourseRatings.user_id == current_user.id,
                                                    CourseRatings.course_id == course_rating_id).first()

    if user_role.role_name == "student":
        course_model = db.query(CourseRatings).filter(CourseRatings.id == course_rating_id).first()
        if course_model is None:
            raise HTTPException(status_code=404, detail="Not found")

        if not existing_rating:
            raise HTTPException(status_code=403, detail="This course rating does not belongs to you")
        db.delete(course_model)
        db.commit()
        return {"message": "course rating deleted successfully"}
    
    raise HTTPException(status_code=403, detail="You do not have permissions")
            

    
    
