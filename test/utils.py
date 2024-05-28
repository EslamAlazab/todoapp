from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from models import Base
from main import app
from models import Todos, User
import pytest
from fastapi.testclient import TestClient
from auth import bcrypt_context

engine = create_engine('sqlite:///./testdb.db', poolclass=StaticPool)

TestingSessionLocal = sessionmaker(
    autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(engine)


client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def Override_get_current_user():
    return {'username': 'eslamalazab', 'id': 1, 'role': 'admin'}


engine = create_engine('sqlite:///./testdb.db')

TestingSessionLocal = sessionmaker(
    autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(engine)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn fastapi',
        owner_id=1,
        priority=2,
        complete=False,
        description='ok'
    )
    db = next(override_get_db())
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.commit()


@pytest.fixture
def test_user():
    user = User(
        username='eslamalazab',
        first_name='Eslam',
        last_name='Alazab',
        email='eslam@sql.com',
        hashed_password=bcrypt_context.hash('testpassword'),
        role='admin'
    )
    db = next(override_get_db())
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users;"))
        conn.commit()
