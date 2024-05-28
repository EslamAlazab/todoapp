from main import app
from database import get_db
from auth import get_current_user
from models import Todos
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = Override_get_current_user


def test_read_all(test_todo):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == [{'priority': 2, 'id': 1, 'owner_id': 1,
                                'title': 'Learn fastapi', 'description': 'ok',
                                'complete': False}]


def test_read_one(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == 200
    assert response.json() == {'priority': 2, 'id': 1, 'owner_id': 1,
                               'title': 'Learn fastapi', 'description': 'ok',
                               'complete': False}
    response = client.get('/todo/7')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todo/', json=request_data)
    assert response.status_code == 201

    db = next(override_get_db())
    test = db.query(Todos).filter(Todos.id == 2).first()
    assert test.title == request_data['title']
    assert test.description == request_data['description']
    assert test.priority == request_data['priority']
    assert test.complete == request_data['complete']


def test_update_todo(test_todo):
    request_data = {
        'title': 'Now title',
        'description': 'New description',
        'priority': 5,
        'complete': True
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204

    db = next(override_get_db())
    test = db.query(Todos).filter(Todos.id == 1).first()
    assert test.title == request_data['title']
    assert test.description == request_data['description']
    assert test.priority == request_data['priority']
    assert test.complete == request_data['complete']

    response = client.put('/todo/10', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = next(override_get_db())
    test = db.query(Todos).filter(Todos.id == 1).first()
    assert test is None

    response = client.delete('/todo/10')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}
