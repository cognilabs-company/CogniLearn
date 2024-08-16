from database import get_db
from tests.utils import *
from fastapi import status
from utils import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_users_success(test_user_admin, test_role_admin):
    response = client.get("/admin/get-all-users")
    print(response.json())
    my_data = [{
        'id': 1, 
        'email': 'davronof123@gmail.com',
        'phone_number': '992226205',
        'username': 'davronoff',
        'name': 'Davronov Ilyas',
        'created_at': test_user_admin.created_at.isoformat(),
        'is_active': True,
        'user_photo': 'no photo yet',
        'role_id': test_role_admin.id,
        'role_name': 'admin'
    }]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == my_data

    