
from datetime import datetime
from typing import List
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
    course_id: int


class EditLessonRequestModel(BaseModel):
    lesson_name: str
    duration: int = Field(gt=0)





class AnswerRequestModel(BaseModel):
    answer_text: str
      

    
class Submission(BaseModel):
    answers: List[AnswerRequestModel]

    
class QuestionRequestModel(BaseModel):
    question_text: str
    quiz_id: int    
    answers: List[AnswerRequestModel]
    correct_answer_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "question_text": "What is the capital of France?",
                "quiz_id": 1,
                "answers": [
                    {"answer_text": "Paris"},
                    {"answer_text": "Berlin"},
                    {"answer_text": "Rome"},
                    {"answer_text": "Uzbekistan"},
                ],
                "correct_answer_id": 1
            }
        }


class EditQuestionRequestModel(BaseModel):
    question_text: str
    quiz_id: int    

class EditAnswerRequestModel(BaseModel):
    answer_text: str
    question_id: int    

class CourseRatingRequestModel(BaseModel):
    rating: int = Field(lt=6, gt=0)
    course_id: int  


class EditCourseRatingRequestModel(BaseModel):
    rating: int
    course_rating_id: int    


class LessonRatingRequestModel(BaseModel):
    rating: int = Field(lt=6, gt=0) 
    lesson_id: int      

class EnrollemntsRequestModel(BaseModel):
    owner_name: str 
    lesson_id: int      
    
        