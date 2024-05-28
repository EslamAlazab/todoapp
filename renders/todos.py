from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi import APIRouter, Request, Form, status, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from database import db_dependency
from models import Todos
from auth import get_current_render_user


router = APIRouter(prefix='/todos', tags=['todo render'])

templates = Jinja2Templates(directory="templates")


class Message:
    def __init__(self, msg: str, *, tag: str) -> None:
        self.msg = msg
        self.tag = tag


messages: list[Message] = []


@router.get('/', response_class=HTMLResponse, name='home')
async def read_all_by_user(request: Request, db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})
    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    context = {'todos': todos, 'user': user}
    if messages:
        context['msg'] = messages.pop()
    return templates.TemplateResponse(request, 'home.html', context)


@router.get('/add-todo', response_class=HTMLResponse, name='add-todo')
async def add_new_todo(request: Request):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})
    return templates.TemplateResponse(request, 'add-todo.html', {'user': user})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(request: Request, title: Annotated[str, Form(...)], description: Annotated[str, Form(...)],
                      priority: Annotated[int, Form(...)], db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    todo: Todos = Todos()
    todo.title = title
    todo.description = description
    todo.complete = False
    todo.priority = priority
    todo.owner_id = user.get('id')

    db.add(todo)
    db.commit()
    messages.append(Message('Todo successfully added', tag='success'))
    # remember it must be 302 to till the client to go to the new url!!
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse, name='edit-todo')
async def edit_todo(request: Request, todo_id: int, db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if not todo:
        messages.append(Message('Todo not found', tag='danger'))
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    context = {'todo': todo, 'user': user}
    return templates.TemplateResponse(request, 'edit-todo.html', context)


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, title: Annotated[str, Form(...)],
                    description: Annotated[str, Form(...)], priority: Annotated[str, Form(...)], db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if not todo:
        messages.append(Message('Todo not found', tag='danger'))
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    todo.title = title
    todo.description = description
    todo.priority = priority

    db.commit()
    messages.append(Message('Todo successfully edited', tag='success'))
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}')
async def delete_todo(request: Request, todo_id: int, db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()

    db.delete(todo)
    db.commit()
    messages.append(Message('Todo successfully deleted', tag='success'))
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get('/complete/{todo_id}')
async def complete_todo(request: Request, todo_id: int, db: db_dependency):
    user = await get_current_render_user(request)
    if not user:
        msg = Message('Please sign in!', tag='danger')
        return templates.TemplateResponse(request, 'login.html', {'msg': msg})

    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    todo.complete = not todo.complete

    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
