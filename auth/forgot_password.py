import random  # Import the correct random module
from typing import Annotated
import redis
import json

from utils import hash_password
from database import get_db, db_dependency
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from model.model import Users as users
from fg import send_mail_for_forget_password
from config import REDIS_HOST, REDIS_PORT

try:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    print("Connecting to Redis...")
    redis_client.ping()
    print("Connected to Redis!")
except Exception as e:
    print(f"Error connecting to Redis: {e}")

router = APIRouter(prefix='/auth', tags=['auth'])


@router.get('/forget-password/{email}')
async def forget_password(
        email: str,
        db: Annotated[Session, Depends(get_db)]
):
    try:
        email_exists = db.query(users).filter(users.email == email).first()
        if email_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email address")

        code = random.randint(99999, 999999)  # Generate a random 6-digit code
        redis_client.set(f'{email}', json.dumps({'code': code}), ex=600)

        send_mail_for_forget_password.delay(email, code)
        return {"detail": "Check your email"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/reset-password/{email}')
async def reset_password(
        email: str,
        code: int,
        new_password: str,
        confirm_password: str,
        session: db_dependency
):
    try:
        if new_password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match!")

        data = redis_client.get(email)
        if data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")

        js_data = json.loads(data)
        user_email = session.query(users).filter(users.email == email).first()

        if user_email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

        if js_data['code'] == code:
            user_email.hashed_password = hash_password(confirm_password)

            session.add(user_email)
            session.commit()

            return {"detail": "Password changed successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset code")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
