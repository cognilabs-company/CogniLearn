from tests.utils import *
from database import get_db
from auth.auth import authenticate_user, create_access_token
from datetime import timedelta
from jose import jwt
import pytest
from utils import SECRET_KEY, ALGORITHM, get_current_user, is_admin
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.email, 'fakepassword', db)
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email

    non_existent_user = authenticate_user('WrongUseName', 'testpassword', db)
    assert non_existent_user is False
    

    wrong_password_user = authenticate_user(test_user.email, 'wrongpassword', db)
    assert wrong_password_user is False


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, expires_delta)

    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], 
                              options={'verify_signature': False})
    

    assert decode_token['sub'] == username
    assert decode_token['id'] == user_id


@pytest.mark.asyncio    
async def test_get_current_user_valid_token():
    encode = {'sub': 'test_user', 'id': 1}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'test_user', 'id': 1}

    
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'sub': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user'


def test_is_admin_admin(test_user_admin):
    db = TestingSessionLocal()
    my_data = {'id': test_user_admin.id}
    response = is_admin(user=my_data,db=db)
    assert response == "admin"


def test_is_admin_superuser(test_user_superuser):
    db = TestingSessionLocal()
    my_data = {'id': test_user_superuser.id}
    response = is_admin(user=my_data,db=db)
    assert response == "superuser"


def test_is_admin_none_user():
    db = TestingSessionLocal()
    my_data = {'id': 999}
    response = is_admin(db=db, user=my_data)
    model = db.query(Users).filter(Users.id == my_data.get('id')).first()
    assert not model
    assert response == False

def test_is_admin_none_role():
    db = TestingSessionLocal()
    my_data = {'id': 999, 'role_id': 999}
    response = is_admin(user=my_data, db=db)
    model = db.query(Roles).filter(Roles.id == my_data.get('role_id')).first()
    assert not model
    assert response == False


# def test_create_user_success():
#     # Create a valid user registration request
#     request_data = {
#         "email": "newuser@example.com",
#         "username": "newuser",
#         "name": "New User",
#         "phone_number": "992226206",
#         "password": "ValidPass1",
#         "confirm_password": "ValidPass1"
#     }

#     # Make the POST request
#     response = client.post("/auth/registration", json=request_data)

#     # Assertions
#     assert response.status_code == 200
#     assert response.json() == {"message": "Account created successfully as admin"}

#     # Check the user has been added to the database
#     db = TestingSessionLocal()
#     user = db.query(Users).filter(Users.username == request_data["username"]).first()
#     db.close()
#     assert user is not None
#     assert user.email == request_data["email"]
#     assert user.role_id is not None
