from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from config import *
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from model.model import Roles, Users
from auth.auth import bcrypt_context

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
    return {'username': 'davronoff', 'id': 1, 'role_id': 1}


@pytest.fixture(scope='module')
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_role():
    role = Roles(
        id=1,
        role_name="super_admin"
    )
    db = TestingSessionLocal()
    db.add(role)
    db.commit()
    yield role
    db.query(Roles).delete()
    db.commit()
    db.close()
    # with engine.connect() as connection:
    #     connection.execute(text("DELETE FROM roles;"))
    #     connection.commit()


@pytest.fixture
def test_user(test_role):
    user = Users(
        id=1,
        email="davronof123@gmail.com",
        hashed_password="fakehashedpassword",
        phone_number="992226205",
        username="davronoff",
        name="Davronov Ilyas",
        created_at=datetime.utcnow(),
        is_active=True,
        user_photo="no photo yet",
        role_id=test_role.id
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()
    # with engine.connect() as connection:
    #     connection.execute(text("DELETE FROM users;"))
    #     connection.commit()

