from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import db_dependency
from models import User
from auth import authenticate_user, create_access_token, bcrypt_context
from validators import email_validator, password_validator, user_validation
from datetime import timedelta
from .todos import messages, Message


router = APIRouter(prefix='/users', tags=['users render'])
templates = Jinja2Templates('templates')


@router.get('/', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    form = await request.form()
    username_or_email = form.get('username_or_email')
    password = form.get('password')

    user = authenticate_user(username_or_email, password, db)
    if not user:
        msg = Message('Could not validate user.', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20))

    response = RedirectResponse(
        url="/todos", status_code=status.HTTP_302_FOUND)
    # set the access token as a cookie
    response.set_cookie(key='access_token', value=token, httponly=True)
    messages.append(Message('Login successful', tag='success'))
    return response


@router.get('/logout', name='logout')
async def logout(request: Request):
    msg = Message('logout successful', tag='success')
    response = templates.TemplateResponse(request, 'login.html', {'msg': msg})
    response.delete_cookie(key='access_token')
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(request, "register.html", {'errors': False})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: db_dependency):
    form = await request.form()
    errors = await user_validation(**form, db=db)
    print(errors)
    if errors:
        return templates.TemplateResponse(request, "register.html", {'errors': errors})

    email = form.get('email')
    username = form.get('username')
    password = form.get('password')
    firstname = form.get('firstname')
    lastname = form.get('lastname')

    user = User()
    user.email = email
    user.username = username
    user.first_name = firstname
    user.last_name = lastname
    user.hashed_password = bcrypt_context.hash(password)
    user.role = 'user'

    db.add(user)
    db.commit()

    msg = Message('Welcome to Todoapp', tag='success')
    return templates.TemplateResponse(request, 'login.html', {'msg': msg})
