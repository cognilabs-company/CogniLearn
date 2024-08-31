from fastapi import APIRouter, Depends
from auth.auth import get_current_user
from database import db_dependency
from typing import Annotated
from model.model import Courses, Users, Roles, StudentMonthlyPayment
from routers.scheme import Payment
from fastapi.exceptions import HTTPException

router = APIRouter(
    prefix = '/student_monthly_payment',
    tags = ['student_monthly_payment']
)

user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("get_all_payments")
async def get_all_payments(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "stuff":
        return db.query(StudentMonthlyPayment).all()


@router.get("/get_paymnet_info/{status}")
async def get_payment_info(user: user_dependancy, db: db_dependency, status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "stuff":
        getting_by_status = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.payment_status == status).all()
        return getting_by_status
    


@router.post("/do_payment")
async def do_payment(user: user_dependancy, db: db_dependency, payment_request: Payment):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    course = db.query(Courses).filter(Courses.course_name == payment_request.payment_course_name).first()

    if course:
        payment_request.payment_course_id = course.id

    if user_role.role_name == "admin" or user_role.role_name == "stuff":
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
        
    
    raise HTTPException(status_code=403, detail="You do not have permission")   


@router.put("changing_status")
async def changing_payment_status(user: user_dependancy, db: db_dependency, payment_id: int, status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "stuff":
        user_payment = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.id == payment_id).first()

        user_payment.payment_status = status
        db.add(user_payment)
        db.commit()
        return {"message": "Payment status has been changed successfully!"}
    
    raise HTTPException(status_code=403, detail="Ypu do not have permission!")


@router.delete("delete_payment/{id}")
async def delete_payment(user: user_dependancy, db:db_dependency, id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "admin" or user_role.role_name == "super admin":
        payment = db.query(StudentMonthlyPayment).filter(StudentMonthlyPayment.id == id).first()
        db.delete(payment)
        db.commit()
        return {"message": "Payment info deleted successfully!"}
    
    raise HTTPException(status_code=430, detail="You do not have permission!")