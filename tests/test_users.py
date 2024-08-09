from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from tests.utils import *
from model.model import Users
from fastapi import status, Depends
from utils import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_users_authenticated(test_user, test_role):
    response = client.get("/users/get-all-users")
    assert response.status_code == status.HTTP_200_OK
    data = test_user.created_at.isoformat()
    print(response.json())
    assert response.json() == [{'id': 1, 'email': 'davronof123@gmail.com', 'hashed_password': 'fakehashedpassword',
                               'phone_number': '992226205', 'username': 'davronoff', 'name':
                                'Davronov Ilyas', 'created_at': data, 'is_active': True, 'user_photo': 'no photo yet',
                                'role_id': test_role.id}]


def test_get_user_authenticated(test_user, test_role):
    response = client.get("/users/get-user")
    data = test_user.created_at.isoformat()
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 1
    assert response.json()['email'] == 'davronof123@gmail.com'
    assert response.json()['phone_number'] == '992226205'
    assert response.json()['username'] == 'davronoff'
    assert response.json()['name'] == 'Davronov Ilyas'
    assert response.json()['user_photo'] == 'no photo yet'
