from database import get_db
from tests.utils import *
from fastapi import status
from utils import get_current_user
from io import BytesIO

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user_success(test_user_admin, test_role_admin):
    response = client.get("/users/get-user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 1
    assert response.json()['email'] == 'davronof123@gmail.com'
    assert response.json()['phone_number'] == '992226205'
    assert response.json()['username'] == 'davronoff'
    assert response.json()['name'] == 'Davronov Ilyas'
    assert response.json()['user_photo'] == 'no photo yet'


def test_edit_profile_success(test_role_admin, test_user_admin):
    my_data = {
        'id': 1,
        'email': 'editcheck@gmail.com',
        'name': 'Edit Check',
        'username': 'editcheck',
        'phone_number': '778889911'
    }
    response = client.patch("/users/edit-profile", json=my_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Profile updated successfully"}


