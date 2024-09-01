from fastapi import APIRouter, Depends
from typing import Annotated
from auth.auth import get_current_user
from database import db_dependency
from routers.scheme import CallingProcessUserInfo,AfterCall
from model.model import Users, Roles, CallingProcess
from starlette import status
from fastapi.exceptions import HTTPException
from datetime import datetime
from utils import is_admin


router = APIRouter(
    prefix = '/calling_process',
    tags = ['calling_process']
)


user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all")
async def get_all(user: user_dependancy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")

    if not is_admin(db=db, user=user):
        raise HTTPException(status_code=403, detail="You don't have permission")

    return db.query(CallingProcess).all()

@router.get("/get_by_status/{student_status}", status_code=status.HTTP_200_OK)
async def get_by_status(user: user_dependancy, db: db_dependency, student_status: str):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name != "operator":
        raise HTTPException(status_code=403, detail="you do not have permission")

    return db.query(CallingProcess).filter(CallingProcess.status == student_status).all()




@router.post("/posting_calling_info", status_code=status.HTTP_201_CREATED)
async def posting_calling_info(user: user_dependancy, db: db_dependency, calling_scheme: CallingProcessUserInfo):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()

    if user_role.role_name == "stuff":
        user_model = CallingProcess(
            stuff_id=current_user.id, 
            student_name=calling_scheme.student_name, 
            phone_number=calling_scheme.phone_number, 
            calling_time=datetime.utcnow(),  # Ensure correct datetime assignment
            # status='In progress'  # Make sure this value is valid in your Enum
        )
        db.add(user_model)
        db.commit()
        return {"message": "Calling info added successully. Waiting for respond!!!"}
    
    raise HTTPException(status_code=403, detail="You do not have permission")

@router.put("/after_call_change/{student_name}")
async def after_call_change(user: user_dependancy, db: db_dependency, student_name: str, after_call_model: AfterCall):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_stuff = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_stuff.role_id).first()
    getting_users = db.query(CallingProcess).filter(current_stuff.id == CallingProcess.stuff_id).all()

    if user_role.role_name == "stuff" and student_name == getting_users.student_name:
        changing_info = CallingProcess(
            description = after_call_model.desciption,
            status = after_call_model.status
        )
        db.add(changing_info)
        db.commit()
        return {"meassage": "Description and status has been changed succssfully"}
    raise HTTPException(status_code=403, detail="You do not have permission!")

@router.delete("/delete_process/{process_id}")
async def delete_process(user: user_dependancy, db: db_dependency, process_id: int):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()


    if user_role.role_name == "admin" or user_role.role_name == "stuff":
        process = db.query(CallingProcess).filter(CallingProcess.id == process_id).first()
        db.delete(process)
        db.commit()
        return {"message": "process deleted successfully"}
        
    raise HTTPException(status_code=403, detail="You do not have permission")    