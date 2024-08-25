from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean, ForeignKey, func, Enum


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String(150))
    phone_number = Column(String(30))
    name = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.now())
    is_active = Column(Boolean, default=True)
    user_photo = Column(String, default="no photo yet !")
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Roles", back_populates="role_owner")
    enrollment = relationship("Enrollments", back_populates="owner")
    student_user = relationship("StudentQuizAttempts", back_populates="student_quiz_attempt_user")
    course_rating = relationship("CourseRatings", back_populates="course_rating_user")
    lesson_rating = relationship("LessonRatings", back_populates="lesson_rating_user")
    student_payment = relationship("StudentMonthlyPayment", back_populates="id_of_student")
    student_callingprocess = relationship("CallingProcess", back_populates="id_of_student")
    stuff_callingprocess = relationship("CallingProcess", back_populates="id_of_stuff")
    student_attendance = relationship("Attendance", back_populates="id_of_student")
    student_attendance = relationship("Attendance", back_populates="id_of_teacher")


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(20))
    # role_owner_id = Column(Integer, ForeignKey("users.id"))
    role_owner = relationship("Users", back_populates="role")
    user_role_callingprocess = relationship("CallingProcess", back_populates="user_role")


class Courses(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    duration = Column(Integer)
    is_active = Column(Boolean, default=True)
    course_price = Column(float)

    enrollment = relationship("Enrollments", back_populates="course")
    lesson = relationship("Lessons", back_populates="course")
    course_rating = relationship("CourseRatings", back_populates="course_rating_course")
    student_payment = relationship("StudentMonthlyPayment", back_populates="id_of_course")
    student_attendance = relationship("Attendance", back_populates="id_of_course")


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
    student_attendance = relationship("Attendance", back_populates="id_of_lesson")


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


class Quizzes(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    quiz_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    lesson = relationship("Lessons", back_populates="quiz")
    question = relationship("Questions", back_populates="quiz")
    student_attempt = relationship("StudentQuizAttempts", back_populates="student_quiz_attempt_quiz")


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))

    quiz = relationship("Quizzes", back_populates="question")
    answer = relationship("Answers", back_populates="question")


class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answers_text = Column(String)
    is_correct = Column(Boolean, default=True)
    question_id = Column(Integer, ForeignKey("questions.id"))

    question = relationship("Questions", back_populates="answer")


class StudentQuizAttempts(Base):
    __tablename__ = "student_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    score = Column(Integer)
    student_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))

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


# CRM part


class StudentMonthlyPayment(Base):
    __tablename__ = "coursepayment"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("enrollments.user_id"))
    course_id = Column(Integer, ForeignKey("enrollments.course_id"))
    payment_status = Column(Boolean, default=False)
    price = Column(float, ForeignKey("courses.course_price"))
    payed_amount = Column(float)
    payment_date = Column(TIMESTAMP, default=datetime.now())

    id_of_student = relationship("Users", back_populates="student_payment")
    id_of_course = relationship("Course", back_populates="student_payment")


class CallingProcess(Base):
    __tablename__ = "callingproccess"
    user_role = Column(String, ForeignKey("roles.role_name"))
    student_id = Column(Integer, ForeignKey("user.id"))
    stuff_id = Column(Integer, ForeignKey("users.id"))
    calling_time = Column(TIMESTAMP, default=datetime.now())
    description = Column(String)
    status = Column(Enum('Successfull', 'Failed', 'Incoming', name='status_enum'), default='Incoming')

    id_of_student = relationship("Users", back_populates="student_callingprocess")
    id_of_stuff = relationship("Users", back_populates="stuff_callingprocess")
    user_role = relationship("Roles", back_populates="user_role_callingprocess")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("user.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    course_id = Column(Integer, ForeignKey("lessons.course_id"))
    attendance_time = Column(TIMESTAMP, default=datetime.now())

    id_of_student = relationship("Users", back_populates="student_attendance")
    id_of_teacher = relationship("Users", back_populates="student_attendance")
    id_of_course = relationship("Courses", back_populates="student_attendance")
    id_of_lesson = relationship("Lessons", back_populates="student_attendance")