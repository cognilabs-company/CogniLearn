from celery.bin.control import status
from fastapi import APIRouter, Depends, Path
from auth.auth import get_current_user
from database import db_dependency
from typing import Annotated
from model.model import Courses, Users, Roles, StudentMonthlyPayment
from routers.scheme import Payment
from fastapi.exceptions import HTTPException
from utils import is_admin

router = APIRouter(
    prefix = '/student-monthly-payment',
    tags = ['student-monthly-payment']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("ge-all")
async def get_all_payments(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permission")

    return db.query(StudentMonthlyPayment).all()


@router.get("/get-payment-info/{status}")
async def get_payment_info(user: user_dependancy, db: db_dependency, status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permission")

    getting_by_status = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.payment_status == status).all()
    if not getting_by_status:
        raise HTTPException(status_code=404, detail="Not found")

    return db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.payment_status == status).all()


@router.post("/do-payment", status_code=201)
async def do_payment(user: user_dependancy, db: db_dependency, payment_request: Payment):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    course = db.query(Courses).filter(Courses.course_name == payment_request.payment_course_name).first()

    if course:
        payment_request.payment_course_id = course.id

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permission")

    student_payment = StudentMonthlyPayment(
        student_name = payment_request.fullname,
        payment_course_name = payment_request.payment_course_name,
        payment_course_id = payment_request.payment_course_id,
        phone_number = payment_request.phone_number,
        payed_amount = payment_request.payed_amount,
    )
    db.add(student_payment)
    db.commit()

    if payment_request.payed_amount == course.price:
        return {"message": "Payment successfully processed."}
    elif payment_request.payed_amount == 0:
        return {"message": "Payment record added as unpaid."}
    elif 0 < payment_request.payed_amount < course.price:
        return {"message": "Payment recorded as partially paid."}


@router.put("changing-status")
async def changing_payment_status(user: user_dependancy, db: db_dependency, payment_id: int, status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="You do not have permission")

    user_payment = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.id == payment_id).first()

    user_payment.payment_status = status
    db.add(user_payment)
    db.commit()
    return {"message": "Payment status has been changed successfully!"}


@router.delete("delete-payment/{payment_id}")
async def delete_payment(user: user_dependancy, db:db_dependency, payment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    if not is_admin(db, user):
        raise HTTPException(status_code=430, detail="You do not have permission!")

    payment = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.id == payment_id).first()
    db.delete(payment)
    db.commit()
    return {"message": "Payment info deleted successfully!"}

