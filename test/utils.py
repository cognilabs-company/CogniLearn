from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from config import *
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from model.model import Roles
from auth.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testCogniLMSdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close_all()


def override_get_current_user():
    return {'username': 'davronoff', 'id': 1}


@pytest.fixture
def test_role():
    role = Roles(
        role_name="super_admin"
    )
    db = TestingSessionLocal()
    db.add(role)
    db.commit()
    yield role
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
