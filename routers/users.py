from fastapi import status, APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import db_dependency
from auth import authenticate_user, create_access_token, user_dependency, bcrypt_context
from models import User
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import timedelta

router = APIRouter(
    prefix='/user-api',
    tags=['user-api']
)


class CreateUser(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str = Field(default='user')


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(User).filter(User.id == user.get('id')).first()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      user_request: CreateUser):
    new_user = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True
    )

    db.add(new_user)
    db.commit()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(
        user_verification.new_password)
    db.commit()


@router.post('/token', response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user: User = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20),)
    return {'access_token': token, 'token_type': 'bearer'}
