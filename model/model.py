from datetime import datetime

from sqlalchemy import Table,Column,String, Integer,Float,TIMESTAMP,Boolean, MetaData,ForeignKey



metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String(100)),
    Column('password', String(150)),
    Column('name', String(100)),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('is_active', Boolean, default=True),
    Column('role_id',Integer,ForeignKey('role.id')),
    Column('user_photo',String, default='no photo yet !')
)

role = Table(
    'role',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('role_name', String)
)

course = Table(
    'course',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('course_name', String),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('duration', Integer),
    Column('is_active', Boolean, default=True),
)

enrollment = Table(
    'enrollment',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('finished_at',TIMESTAMP)
)

lesson = Table(
    'lesson',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('lesson_name', String),
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('video_url',String, default='no video yet !'),
    Column('description',String),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('duration', Integer)
)

quiz = Table(
    'quiz',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('quiz_name', String),
    Column('lesson_id', Integer, ForeignKey('lesson.id')),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

question = Table(
    'question',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('question_text', String),
    Column('quiz_id', Integer, ForeignKey('quiz.id')),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

answer = Table(
    'answer',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('answer_text', String),
    Column('is_correct', Boolean),
    Column('question_id', Integer, ForeignKey('question.id'))
)

student_quiz_attempt = Table(
    'student_quiz_attempt',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('student_id', Integer, ForeignKey('users.id')),
    Column('quiz_id', Integer, ForeignKey('quiz.id')),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('score', Integer),
)

course_rating = Table(
    'course_rating',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('comment',String,default='no comments yet !'),
    Column('rating', Integer, default=0),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

lesson_rating = Table(
    'lesson_rating',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('lesson_id', Integer, ForeignKey('lesson.id')),
    Column('comment', String, default='no comments yet!'),
    Column('rating', Integer, default=0),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

