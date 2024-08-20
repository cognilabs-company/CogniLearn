import shutil
from fastapi import APIRouter, status, HTTPException, Depends, UploadFile
from model.model import Users, Roles
from utils import get_current_user, is_admin
from database import db_dependency
from typing import Annotated, List
from routers.scheme import UserInfo
import os
from model.model import Users as users
from routers.scheme import UserInfo, UserInfoForUsers


router = APIRouter(
    prefix='/users',
    tags=['users']
)

user_dependency = Annotated[dict, Depends(get_current_user)]



@router.patch("/edit-profile")
async def edit_profile(db: db_dependency,
                       token: dict = Depends(get_current_user),
                       email: str = None,
                       name: str = None,
                       username: str = None,
                       phone_number: str = None,
                       user_photo: UploadFile = None
):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_id = token.get('id')

    user = db.query(users).filter(users.id == user_id).first()

    if email:
        email_exists = db.query(users).filter(users.email == email).first()
        if email_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    if username:
        username_exists = db.query(users).filter(users.username == username).first()
        if username_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    if phone_number:
        phone_exists = db.query(users).filter(users.phone_number == phone_number).first()
        if phone_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")

    if email:
        user.email = email
    if name:
        user.name = name
    if username:
        user.username = username
    if phone_number:
        user.phone_number = phone_number

    if user_photo:
        photos_dir = "user_photos"
        if not os.path.exists(photos_dir):
            os.makedirs(photos_dir)
        photo_path = os.path.join(photos_dir, f"{user_id}_{user_photo.filename}")
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(user_photo.file, buffer)
        user.user_photo = photo_path

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully"}


 
@router.get("/get-all-users", response_model=List[UserInfo],status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not is_admin(db, user):

        raise HTTPException(status_code=403, detail="You do not have permissions")

    users = db.query(Users, Roles).join(Roles, Users.role_id == Roles.id).all()

    response = [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "name": user.name,
            "phone_number": user.phone_number,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "user_photo": user.user_photo,
            "role_id": user.role_id,
            "role_name": role.role_name
        }
        for user, role in users
    ]

    return response

@router.get("/get-user", response_model=UserInfoForUsers)
async def get_all(db: db_dependency,
                  user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter(Users.id == user.get('id')).first()

    
    if not is_admin(db, user):
        return [
            UserInfoForUsers(
                name=user.name,
                email=user.email,
                username=user.username,
                phone_number=user.phone_number,
                user_photo=user.user_photo
            )
            for user in db.query(Users).all()
        ]

    raise HTTPException(status_code=403, detail="You do not have permissions")


