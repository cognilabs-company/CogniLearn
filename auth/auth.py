from datetime import timedelta
from typing import Annotated

import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from config import GOOGLE_CLIENT_SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URL
from fg import send_mail_login_password
from model.model import Users, Roles
from database import db_dependency, get_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from auth.scheme import CreateUserRequest,Token
from utils import hash_password, authenticate_user, create_access_token, get_current_user, verify_password, \
    generate_token
from model.model import Users as users
import re


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


@router.post("/registration")
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):

    if create_user_request.password != create_user_request.confirm_password:
        raise HTTPException(status_code=401, detail='Passwords are not the same!')

    user_email = db.query(Users).filter(Users.email == create_user_request.email).first()
    user_username = db.query(Users).filter(Users.username == create_user_request.username).first()
    user_phone = db.query(Users).filter(Users.phone_number == create_user_request.phone_number).first()

    if user_email is not None:
        raise HTTPException(status_code=409, detail='Email already exist')

    if user_username is not None:
        raise HTTPException(status_code=409, detail='Username already exist')

    if user_phone is not None:
        raise HTTPException(status_code=409, detail='Phone already exist')

    user_count = db.query(users).count()

    user_role = db.query(Roles).filter(Roles.role_name == "user").first()
    if user_role is None:
        create_role = Roles(
            role_name="user"
        )
        db.add(create_role)
        db.commit()
    admin_role = db.query(Roles).filter(Roles.role_name == 'admin').first()
    if admin_role is None:
        create_admin_role = Roles(
            role_name="admin"
        )
        db.add(create_admin_role)
        db.commit()

    admin_role_query = db.query(Roles).filter(Roles.role_name == 'admin').first()
    user_role_query = db.query(Roles).filter(Roles.role_name == "user").first()

    if user_count == 0:
        create_user_model = Users(
            email=create_user_request.email,
            name=create_user_request.name,
            role_id=admin_role_query.id,
            username=create_user_request.username,
            hashed_password=hash_password(create_user_request.password),
            phone_number=create_user_request.phone_number,
        )
        db.add(create_user_model)
        db.commit()
        return {'message': 'Account created successfully as admin'}
    else:
        create_user_model = Users(
            email=create_user_request.email,
            name=create_user_request.name,
            role_id=user_role_query.id,
            username=create_user_request.username,
            hashed_password=hash_password(create_user_request.password),
            phone_number=create_user_request.phone_number,
        )

        db.add(create_user_model)
        db.commit()
        return {'massage': 'Account created successfully'}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}


@router.put("/password")
async def change_password(
        db: db_dependency,
        current_password: str,
        password: str,
        password2: str,
        user: dict = Depends(get_current_user)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_id = user.get('id')
    user_model = db.query(users).filter(users.id == user_id).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if password!= password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if not verify_password(current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect current password")

    if len(password2) < 6:
        raise HTTPException(status_code=400,detail="Password must be at least 6 characters long!")
    if not re.search(r"[A-Z]", password2):
        raise HTTPException(status_code=400, detail='There must be at least one Capital letter')

    user_model.hashed_password = hash_password(password2)
    db.add(user_model)
    db.commit()
    return {'message': 'Password changed successfully'}


@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URL}&scope=openid%20profile%20email&access_type=offline"
    }


@router.get("/google")
async def auth_google(code: str, session:db_dependency):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET_KEY,
        "redirect_uri": GOOGLE_REDIRECT_URL,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    user_result = user_info.json()
    password = re.sub(r'\.', '', re.match(r'^[^@]+', user_result['email']).group())
    user_data = {
        'email' : user_result['email'],
        'first_name' : user_result['name'],
        'last_name' : user_result['given_name'],
        'password' : pwd_context.hash(password)
    }
    query_exist = session.query(users).filter(users.email == user_data['email']).first()
    if query_exist:
        raise HTTPException(status_code=400, detail="Email already in use")

    user_role = session.query(Roles).filter(Roles.role_name == "user").first()
    if user_role is None:
        create_role = Roles(
            role_name="user"
        )
        session.add(create_role)
        session.commit()

    admin_role = session.query(Roles).filter(Roles.role_name == 'admin').first()
    if admin_role is None:
        create_admin_role = Roles(
            role_name="admin"
        )
        session.add(create_admin_role)
        session.commit()

    user_role_query = session.query(Roles).filter(Roles.role_name == "user").first()

    q = Users(
        email=user_data['email'],
        username=user_data['email'],
        name=user_data['first_name'],
        hashed_password=user_data['password'],
        role_id=user_role_query.id
    )
    query = session.add(q)
    session.commit()


    user_data1 = session.query(users).filter(users.email == user_data["email"]).first()


    # token = generate_token(user_data1.id)
    token = create_access_token(user_data1.email, user_data1.id, timedelta(minutes=20))
    send_mail_login_password(user_data1.email, password)
    session.commit()
    message = {"message": "Check your email for login information"}
    return message, token

@router.get("/token")
async def get_token(token: str = Depends(oauth2_bearer)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET_KEY, algorithms=["HS256"])






