from auth.auth import get_current_user
from database import db_dependency
from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from model.model import Users, Roles, Enrollments
from routers.scheme import EnrollmentsRequestModel
from utils import is_admin

router = APIRouter(
    prefix='/enrollments',
    tags=['enrollments']
)


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all", status_code=status.HTTP_200_OK)
async def get_all_enrolments(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="Forbidden")

    return db.query(Enrollments).all()


@router.get("/get-enrollment/{enrollment_id}", status_code=status.HTTP_200_OK)
async def get_enrollment(user: user_dependency, db: db_dependency,
                     enrollment_id: int = Path(max_length=100)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permissions")
        
    enrollments = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()
        
    if enrollments is None:
        raise HTTPException(status_code=404, detail="Not found")
        
    return db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()


@router.post("/add-enrollment", status_code=status.HTTP_201_CREATED)
async def add_enrollment(user: user_dependency, db: db_dependency,
                     request_model: EnrollmentsRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    enrollment_model = Enrollments(**request_model.model_dump())
    db.add(enrollment_model)
    db.commit()
    return {"message": "Enrollment added successfully"}



@router.put("/edit-enrollment/{enrollment_id}")
async def edit_enrollment(user: user_dependency, db: db_dependency,
                    owner: str, course: str  , enrollment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permissions")

    enrollment_model = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()

    if enrollment_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    enrollment_model.owner = owner
    enrollment_model,course = course
    db.add(enrollment_model)
    db.commit()
    return {"message": "enrollment changed successfully"}



@router.delete("/delete-enrollment/{enrollment_id}")
async def delete_enrollment(user: user_dependency, db: db_dependency, enrollment_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You do not have permission")

    enrollment_model = db.query(Enrollments).filter(Enrollments.id == enrollment_id).first()
    if enrollment_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(enrollment_model)
    db.commit()
    return {"message": "Enrollment deleted successfully"}

