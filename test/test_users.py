from .utils import *
from database import get_db
from auth import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = Override_get_current_user


def test_return_user(test_user):
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json()['username'] == 'eslamalazab'
    assert response.json()['first_name'] == 'Eslam'
    assert response.json()['last_name'] == 'Alazab'
    assert response.json()['email'] == 'eslam@sql.com'
    assert response.json()['role'] == 'admin'


def test_change_password_success(test_user):
    response = client.put('/user/password', json={'password': 'testpassword',
                                                  'new_password': 'newpassword'})
    assert response.status_code == 204


def test_change_password_failed(test_user):
    response = client.put('/user/password', json={'password': 'wrongpassword',
                                                  'new_password': 'newpassword'})
    assert response.status_code == 401
    assert response.json() == {'detail': 'Error on password change'}
