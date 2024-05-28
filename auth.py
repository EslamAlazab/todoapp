from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from models import User
from typing import Annotated
from jose import jwt, JWTError
from datetime import timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy import or_


router = APIRouter(
    prefix='/auth-api',
    tags=['auth']
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users-api/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


SECRET_KEY = '30fb8feba8b8de77c02451236d4c9b16a7694c63a824adec5e6e43b19fafa3b9'
ALGORITHM = 'HS256'


def authenticate_user(username_or_email: str, password: str, db):
    user: User = db.query(User).filter(or_(
        User.username == username_or_email,
        User.email == username_or_email)).first()
    if user and bcrypt_context.verify(password, user.hashed_password):
        return user
    return False


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


user_dependency = Annotated[dict, Depends(get_current_user)]


async def get_current_render_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return None
        return {"username": username, "id": user_id}
    except JWTError:
        return None
