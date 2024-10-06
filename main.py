from database import engine
from models import Base
import renders.todos
import renders.users
from routers import users, todos, admin
import renders
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
async def home():
    return RedirectResponse('/todos')


app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)

app.include_router(renders.todos.router)
app.include_router(renders.users.router)
