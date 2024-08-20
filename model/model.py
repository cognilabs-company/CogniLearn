from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String(150))
    phone_number = Column(String(30))
    name = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    is_active = Column(Boolean, default=True)
    user_photo = Column(String, default="no photo yet !")
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Roles", back_populates="role_owner")
    enrollment = relationship("Enrollments", back_populates="owner")
    student_user = relationship("StudentQuizAttempts", back_populates="student_quiz_attempt_user")
    course_rating = relationship("CourseRatings", back_populates="course_rating_user")
    lesson_rating = relationship("LessonRatings", back_populates="lesson_rating_user")


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(20))

    role_owner = relationship("Users", back_populates="role")


class Courses(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    duration = Column(Integer)
    is_active = Column(Boolean, default=True)

    enrollment = relationship("Enrollments", back_populates="course")
    lesson = relationship("Lessons", back_populates="course")
    course_rating = relationship("CourseRatings", back_populates="course_rating_course")


class Enrollments(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    finished_at = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    owner = relationship("Users", back_populates="enrollment")
    course = relationship("Courses", back_populates="enrollment")


class Lessons(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    lesson_name = Column(String)
    video_url = Column(String, default="no video yet !")
    description = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    duration = Column(Integer)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Courses", back_populates="lesson")
    quiz = relationship("Quizzes", back_populates="lesson")
    lesson_rating = relationship("LessonRatings", back_populates="lesson_rating_lesson")


class Quizzes(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    quiz_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    passing_score = Column(Integer)

    lesson = relationship("Lessons", back_populates="quiz")
    question = relationship("Questions", back_populates="quiz")
    student_attempt = relationship("StudentQuizAttempts", back_populates="student_quiz_attempt_quiz")


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    correct_answer_id = Column(Integer, ForeignKey("answers.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))

    quiz = relationship("Quizzes", back_populates="question")
    answer = relationship("Answers", back_populates="question") 
   


class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answers_text = Column(String)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id"))

    question = relationship("Questions", back_populates="answer")


class StudentQuizAttempts(Base):
    __tablename__ = "student_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    score = Column(Integer)
    student_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    passed = Column(Boolean)

    student_quiz_attempt_quiz = relationship("Quizzes", back_populates="student_attempt")
    student_quiz_attempt_user = relationship("Users", back_populates="student_user")


class CourseRatings(Base):
    __tablename__ = "course_ratings"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, default="no comments yet !")
    rating = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    course_rating_user = relationship("Users", back_populates="course_rating")
    course_rating_course = relationship("Courses", back_populates="course_rating")


class LessonRatings(Base):
    __tablename__ = "lesson_ratings"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, default="no comments yet !")
    rating = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))

    lesson_rating_user = relationship("Users", back_populates="lesson_rating")
    lesson_rating_lesson = relationship("Lessons", back_populates="lesson_rating")



class Results(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    correct = Column(Integer)
    student = relationship("Users")
    question = relationship("Questions")
    quiz = relationship("Quizzes")


