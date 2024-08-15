from fastapi import FastAPI, APIRouter

import admin
from auth import auth,forgot_password
from routers import roles, users, courses,lessons,quizzes,questions, answers,student_quiz_attempt, lesson_rating,course_rating
from database import engine
from model.model import Base


app = FastAPI()

router = APIRouter()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'} 


app.include_router(router, tags=['main'])
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(courses.router)
app.include_router(forgot_password.router)
app.include_router(lessons.router)
app.include_router(quizzes.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(student_quiz_attempt.router)
app.include_router(lesson_rating.router)
app.include_router(course_rating.router)





