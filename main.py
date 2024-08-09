from fastapi import FastAPI, APIRouter
from auth import auth
from routers import roles, users, courses, enrollments
from database import engine
from model.model import Base

app = FastAPI()

router = APIRouter()

Base.metadata.create_all(bind=engine)


app.include_router(router, tags=['main'])


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)





