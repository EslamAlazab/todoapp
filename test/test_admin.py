from .utils import *
from database import get_db
from auth import get_current_user
from models import Todos


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = Override_get_current_user


def test_admin_read_all(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == 200
    assert response.json() == [{'priority': 2, 'id': 1, 'owner_id': 1,
                                'title': 'Learn fastapi', 'description': 'ok',
                                'complete': False}]


def test_admin_delete_todo(test_todo):
    response = client.delete('/admin/todo/1')
    assert response.status_code == 204

    db = next(override_get_db())
    test = db.query(Todos).filter(Todos.id == 1).first()
    assert test is None

    response = client.delete('/admin/todo/10')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}
