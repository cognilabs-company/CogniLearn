from tests.utils import *
from database import get_db
from utils import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def unauthorized_user_override():
    # Override the dependency to simulate an unauthorized user
    app.dependency_overrides[get_current_user] = lambda: {'id': 777, 'role_id': 2, 'username': 'fakeuser'}
    yield
    # Remove the override after the test
    app.dependency_overrides.pop(get_current_user)


def test_get_all_enrollments_authenticated(test_enrollments, test_course, test_user):
    response = client.get("/enrollments/get-all-enrollments")
    assert response.status_code == 200
    my_data = [{
        'id': 1,
        'created_at': test_enrollments.created_at.isoformat(),
        'finished_at': test_enrollments.finished_at.isoformat(),
        'course_id': test_course.id,
        'user_id': test_user.id
    }]
    assert response.json() == my_data


def test_get_all_enrollments_forbidden():
    @pytest.fixture
    def unauthorized_user_override():
        # Override the dependency to simulate an unauthorized user
        app.dependency_overrides[get_current_user] = lambda: {'id': 777, 'role_id': 2, 'username': 'fakeuser'}
        yield
        # Remove the override after the test
        app.dependency_overrides.pop(get_current_user)

    def test_403(unauthorized_user_override):
        response = client.get("/enrollments/get-all-enrollments")
        assert response.status_code == 403
        assert response.json() == {'detail': 'Forbidden'}


def test_get_enrollment_authenticated(test_enrollments, test_course, test_user):
    response = client.get("/enrollments/get-enrollment/1")
    db = TestingSessionLocal()
    course = db.query(Courses).filter(Courses.id == test_enrollments.course_id).first()
    user = db.query(Users).filter(Users.id == test_enrollments.user_id).first()
    my_data = [{
        'id': test_enrollments.id,
        'created_at': test_enrollments.created_at.isoformat(),
        'finished_at': test_enrollments.finished_at.isoformat(),
        'course_id': test_enrollments.course_id,
        'course_name': course.course_name,
        'user_id': test_enrollments.user_id,
        'username': user.username
    }]
    assert response.json() == my_data
    assert response.status_code == 200


def test_get_enrollment_not_found():
    response = client.get("/enrollments/get-enrollment/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_get_enrollment_by_course_authenticated(test_enrollments):
    response = client.get("/enrollments/get-enrollments-by-user/1")
    assert response.status_code == 200
    my_data = [{
        'id': 1,
        'created_at': test_enrollments.created_at.isoformat(),
        'finished_at': test_enrollments.finished_at.isoformat(),
        'course_id': test_enrollments.course_id,
        'user_id': test_enrollments.user_id
    }]
    assert response.json() == my_data


def test_get_enrollment_by_course_not_found(test_enrollments):
    response = client.get("/enrollments/get-enrollments-by-user/999")
    print(response.json())
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}

