from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import auth

@asynccontextmanager
def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)

