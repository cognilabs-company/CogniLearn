from database import get_db
from tests.utils import *
from model.model import Roles
from fastapi import status
from utils import get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_authenticated(test_role, test_user):
    response = client.get("/roles/get-all-roles")
    assert response.status_code == 200
    assert response.json() == [{'role_name': 'super_admin', 'id': 1}]


def test_get_all_enrollments_forbidden():
    @pytest.fixture
    def unauthorized_user_override():
        # Override the dependency to simulate an unauthorized user
        app.dependency_overrides[get_current_user] = lambda: {'id': 777, 'role_id': 2, 'username': 'fakeuser'}
        yield
        # Remove the override after the test
        app.dependency_overrides.pop(get_current_user)

    def test_403(unauthorized_user_override):
        response = client.get("/roles/get-all-roles")
        assert response.status_code == 403
        assert response.json() == {'detail': 'Forbidden'}


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
        'role_name': 'super_admin'
    }
    response = client.post("/roles/create-role", json=my_data)
    assert response.status_code == 400
    assert response.json() == {'detail': "Role already exists"}



