from database import get_db
from tests.utils import *
from model.model import Roles
from fastapi import status
from utils import get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_authenticated(test_role):
    response = client.get("/roles/get-all-roles")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'role_name': 'super_admin', 'id': 1}]


def test_create_role_authenticated(test_role):
    my_data = {
        'role_name': 'admin'
    }
    response = client.post("/roles/create-role", json=my_data) 
    assert response.status_code == 201
    db = TestingSessionLocal()
    model = db.query(Roles).filter(Roles.id == 2).first()
    assert model.role_name == my_data.get('role_name')


def test_create_role_exit_check(test_role):
    my_data = {
        'role_name' : 'super_admin'
    }
    response = client.post("/roles/create-role", json=my_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Role already exists"}



