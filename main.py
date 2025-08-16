from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import auth
from database import create_table, drop_table

@asynccontextmanager
async def lifespan(app: FastAPI):
    drop_table()
    create_table()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)

