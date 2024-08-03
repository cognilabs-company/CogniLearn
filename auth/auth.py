from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from model.model import Users, Roles
from database import db_dependency
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUserRequest(BaseModel):
    email: str
    username: str = Field(max_length=15)
    phone_number: str
    name: str
    user_photo: str
    password: str = Field(min_length=6)
    confirm_password:  str = Field(min_length=6)


def hash_password(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@router.post("/")
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):

    if create_user_request.password != create_user_request.confirm_password:
        raise HTTPException(status_code=401, detail='Error on password')

    role = db.query(Roles).filter(Roles.role_name == "user").first()
    if role is None:
        create_role = Roles(
            role_name="user"
        )
        db.add(create_role)
        db.commit()

    create_user_model = Users(
        email=create_user_request.email,
        name=create_user_request.name,
        role_id=role.id,
        username=create_user_request.username,
        hashed_password=hash_password(create_user_request.password),
        phone_number=create_user_request.phone_number,
        user_photo=create_user_request.user_photo
    )

    user_email = db.query(Users).filter(Users.email == create_user_request.email).first()
    user_username = db.query(Users).filter(Users.username == create_user_request.username).first()

    if user_email is not None:
        raise HTTPException(status_code=409, detail='Email already exist')

    if user_username is not None:
        raise HTTPException(status_code=409, detail='Username already exist')

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

