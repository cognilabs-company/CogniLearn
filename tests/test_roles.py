from database import get_db
from tests.utils import *
from model.model import Roles
from fastapi import status
from utils import get_current_user, create_access_token

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_create_role_success(test_user_admin, test_role_admin):
    my_data = {
        'role_name': 'test_role'
    }
    response = client.post("/roles/create-role",json=my_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Role created successfully"}


def test_create_role_already_exists(test_user_admin, test_role_admin):
    my_data = {
        'role_name': 'admin'
    }
    response = client.post("/roles/create-role", json=my_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Role already exists"}


def test_get_all_roles_success(test_user_admin, test_role_admin):
    response = client.get("/roles/get-all-roles")
    my_data = [{
       'id': 1,
       'role_name': 'admin'
    }]

    assert response.status_code == 200
    assert response.json() == my_data
