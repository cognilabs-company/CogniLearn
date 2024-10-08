
from datetime import datetime

from pydantic import BaseModel, Field
import enum
from database import db_dependency
from model.model import Roles


class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    username: str
    phone_number: str
    user_photo: str
    role_id: int


class UserInfoForUsers(BaseModel):
    name: str
    email: str
    username: str
    phone_number: str
    user_photo: str


class RoleInfo(BaseModel):
    id: int
    role_name: str


class RoleRequestModel(BaseModel):
    role_name: str


class CourseRequestModel(BaseModel):
    course_name: str
    price: int
    duration: int = Field(gt=0)



class GetAllUser(BaseModel):
    id: int
    email: str
    username: str
    name: str
    phone_number: str
    created_at: datetime
    is_active: bool
    user_photo: str
    role_id: int
    role_admin:str



class EditCourseRequestModel(BaseModel):
    course_name: str
    duration: int = Field(gt=0)

class QuizRequestModel(BaseModel):
    quiz_name: str
    lesson_id: int = Field(gt=0)


class EditQuizRequestModel(BaseModel):
    quiz_name: str


class LessonRequestModel(BaseModel):
    lesson_name: str
    duration: int = Field(gt=0)
    course_id: int = Field(gt=0)


class EditLessonRequestModel(BaseModel):
    lesson_name: str
    duration: int = Field(gt=0)


class QuestionRequestModel(BaseModel):
    question_text: str
    quiz_id: int = Field(gt=0)

class EditQuestionRequestModel(BaseModel):
    question_text: str
    quiz_id: int = Field(gt=0)

class AnswerRequestModel(BaseModel):
    answers_text: str = Field(min_length=1, max_length=50)
    question_id: int = Field(gt=0)

class EditAnswerRequestModel(BaseModel):
    answer_text: str
    question_id: int    

class CourseRatingRequestModel(BaseModel):
    rating: int = Field(lt=6, gt=0)
    course_id: int = Field(gt=0)


class EditCourseRatingRequestModel(BaseModel):
    rating: int
    course_rating_id: int    


class LessonRatingRequestModel(BaseModel):
    rating: int = Field(lt=6, gt=0) 
    lesson_id: int      

class EnrollmentsRequestModel(BaseModel):
    owner_name: str 
    lesson_id: int      
    
        
class CallingProcessUserInfo(BaseModel):
    student_name: str
    phone_number: str

class AfterCall(BaseModel):
    status: str
    desciption: str
        
class Payment(BaseModel):
    fullname: str
    payment_course_name: str
    payment_course_id: int
    phone_number: str
    payed_amount: int
       