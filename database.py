from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field, Session
from typing import Annotated
from fastapi import Depends

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_table():
    SQLModel.metadata.create_all(engine)

def drop_table():
    SQLModel.metadata.drop_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]