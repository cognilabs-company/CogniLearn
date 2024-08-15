from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from config import *
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from model.model import Roles, Users, Courses, Enrollments
from auth.auth import bcrypt_context
from utils import get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
password = "testpassword123"


client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'id': 1, 'username': 'davronoff'}


@pytest.fixture
def test_role_admin():
    db = TestingSessionLocal()
    role = Roles(
        id=1,
        role_name="admin"
    )
    db.add(role)
    db.commit()
    yield role
    db.query(Roles).delete()
    db.commit()
    db.close()

@pytest.fixture
def test_role_superuser():
    db = TestingSessionLocal()
    role = Roles(
        id=2,
        role_name="superuser"
    )
    db.add(role)
    db.commit()
    yield role
    db.query(Roles).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_role_user():
    db = TestingSessionLocal()
    role = Roles(
        id=3,
        role_name="user"
    )
    db.add(role)
    db.commit()
    yield role
    db.query(Roles).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user_admin(test_role_admin):
    user = Users(
        id=1,
        email="davronof123@gmail.com",
        hashed_password=bcrypt_context.hash("fakepassword"),
        phone_number="992226205",
        username="davronoff",
        name="Davronov Ilyas",
        created_at=datetime.utcnow(),
        is_active=True,
        user_photo="no photo yet",
        role_id=test_role_admin.id
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user_superuser(test_role_superuser):
    user = Users(
        id=2,
        email="superuser@gmail.com",
        hashed_password=bcrypt_context.hash("fakepassword"),
        phone_number="992227788",
        username="superuser",
        name="Super User",
        created_at=datetime.utcnow(),
        is_active=True,
        user_photo="no photo yet",
        role_id=test_role_superuser.id
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user(test_role_user):
    user = Users(
        id=3,
        email="simple@gmail.com",
        hashed_password=bcrypt_context.hash("fakepassword"),
        phone_number="992224455",
        username="simple",
        name="Simple",
        created_at=datetime.utcnow(),
        is_active=True,
        user_photo="no photo yet",
        role_id=test_role_user.id
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()



@pytest.fixture()
def test_course():
    course = Courses(
        id=1,
        course_name='Fast API',
        created_at=datetime.utcnow(),
        duration=3,
        is_active=True
    )
    db = TestingSessionLocal()
    db.add(course)
    db.commit()
    yield course
    db.query(Courses).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_enrollments(test_course, test_user_admin):
    data_start = datetime.utcnow()
    data_finish = data_start + timedelta(minutes=5)
    enrollment = Enrollments(
        id=1,
        created_at=data_start,
        finished_at=data_finish,
        user_id=test_user_admin.id,
        course_id=test_course.id
    )
    db = TestingSessionLocal()
    db.add(enrollment)
    db.commit()
    yield enrollment
    db.query(Enrollments).delete()
    db.commit()
    db.close()




