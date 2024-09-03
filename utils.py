from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from model.model import Users
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from database import db_dependency
from model.model import Roles,Users
import re


SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def hash_password(password):
    return bcrypt_context.hash(password)


def is_admin(db: db_dependency, user):
    user_id = user.get('id')
    current_user = db.query(Users).filter(Users.id == user_id).first()
    if not current_user:
        return False
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if not user_role:
        return False
    role_name = user_role.role_name
    if role_name == 'admin' and user_role.role_name == 'superuser':
        return True
    if role_name == 'admin':
        return 'admin'
    elif role_name == 'superuser':
        return 'superuser'

    return False


def is_teacher(db: db_dependency, user):
    user_id = user.get('id')
    current_user = db.query(Users).filter(Users.id == user_id).first()
    if not current_user:
        return False
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if not user_role:
        return False
    role_name = user_role.role_name
    if role_name == 'teacher':
        return True

    return False


def is_student(db: db_dependency, user):
    user_id = user.get('id')
    current_user = db.query(Users).filter(Users.id == user_id).first()
    if not current_user:
        return False
    user_role = db.query(Roles).filter(Roles.id == current_user.role_id).first()
    if not user_role:
        return False
    role_name = user_role.role_name
    if role_name == 'student':
        return True

    return False


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.email == username).first()
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


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
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