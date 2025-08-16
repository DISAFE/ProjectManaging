from http.client import responses

from fastapi import APIRouter, status, Depends, Body, HTTPException, Response
from typing import Annotated
from pydantic import EmailStr
from schemata import UserCreate, User, RT
import jwt
import bcrypt
from database import SessionDep
from datetime import datetime, timezone, timedelta

#bcrypt
SALT = bcrypt.gensalt()

#jwt
ALGORITHM = "HS256"
SECRET_KEY = "BuffyTest320@!"

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(
        usercreate: Annotated[UserCreate, Body()],
        session: SessionDep
):

    user_db = session.query(User).filter(User.email == usercreate.email).first()
    if user_db is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid email")

    user_db = session.query(User).filter(User.username == usercreate.username).first()
    if user_db is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid username")

    usercreate.password_hash = bcrypt.hashpw(usercreate.password_hash.encode(), SALT).decode()

    user = User.model_validate(usercreate)

    session.add(user)
    session.commit()

    return {"created": "ok"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
        email: Annotated[EmailStr, Body()],
        password: Annotated[str, Body()],
        session: SessionDep,
        response: Response,
):
    #verify
    user_db: User = session.query(User).filter(User.email == email).first()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    if not bcrypt.checkpw(password.encode(), user_db.password_hash.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    #refresh_token
    exp = (datetime.now(timezone.utc) + timedelta(days=7)).timestamp()
    exp = int(exp)
    payload = {
        "id": user_db.id,
        "exp": exp
    }
    refresh_token = jwt.encode(payload=payload, algorithm=ALGORITHM, key=SECRET_KEY)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=604_800,
        httponly=True,
    )

    rt = RT()
    rt.token = refresh_token
    rt.user_id = user_db.id
    session.add(rt)
    session.commit()

    #access_token
    exp = (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()
    exp = int(exp)
    payload = {
        "id": user_db.id,
        "exp": exp,
    }
    access_token = jwt.encode(payload=payload, algorithm=ALGORITHM, key=SECRET_KEY)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=180,
        httponly=True,
        samesite="lax",
    )
    return {"success": "ok"}
