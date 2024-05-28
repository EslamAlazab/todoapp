from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(default='Unknown')
    last_name: Mapped[str] = mapped_column(default='Unknown')
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str]

    todos: Mapped[list["Todos"]] = relationship(back_populates='user')

    def __repr__(self):
        return f'user {self.username}, with id: {self.id}'


class Todos(Base):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    priority: Mapped[int]
    complete: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped[User] = relationship(back_populates='todos')

    def __repr__(self):
        return f'Todo {self.title}'
