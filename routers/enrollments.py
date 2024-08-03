from auth.auth import get_current_user
from database import db_dependency
from fastapi import APIRouter


router = APIRouter(
    prefix='/enrollments',
    tags=['enrollments']
)