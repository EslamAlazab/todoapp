from .utils import *
from auth import get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_current_user] = Override_get_current_user


def test_authenticate_user(test_user):
    db = next(override_get_db())
    user = authenticate_user(test_user.username, 'testpassword', db)
    assert user is not None
    assert user.username == test_user.username

    wrong_user = authenticate_user('wrong_username', 'testpassword', db)
    assert wrong_user is False

    wrong_password = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password is False


def test_create_access_token():
    username, user_id, role, expires_delta = 'testuser', 1, 'user', timedelta(
        days=1)
    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM, options={
                               'verify_signture': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_wrong():
    encode = {'sub': 'testuser'}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'
