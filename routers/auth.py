from fastapi import APIRouter, status, Body, HTTPException, Response
from typing import Annotated, Optional, Literal
from pydantic import EmailStr
from schemata import UserCreate, User, RT
import jwt
import bcrypt
from database import SessionDep
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select

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

#helper func
"""
This func is help about get User record and check none (also raise exception) simply.
Ex)
if you want check email already exist, using like:
get_and_check(
        session=session,
        typ="email",
        value=str(email),
        when_exception="not none",
        st_code=status.HTTP_409_CONFLICT,
        detail="Conflict email"
    )
    
also if you want bring record by email and also check not none, using like:
get_and_check(
        session=session,
        typ="email",
        value=str(email),
        when_exception="none",
        st_code=status.HTTP_404_NOT_FOUND,
        detail="Invalid email"
    )
"""
def get_and_check(
        *,
        session: Session,
        typ: Literal["email", "username"],
        value: str,
        when_exception: Literal["none", "not none"],
        st_code: status,
        detail: str
)->Optional[User]:

    stmt = None
    if typ == "email":
        stmt = select(User).where(User.email == value)
    elif typ == "username":
        stmt = select(User).where(User.username == value)

    db_user = session.scalars(stmt).first()

    if when_exception == "none":
        if db_user is None:
            raise HTTPException(status_code=st_code, detail=detail)
    elif when_exception == "not none":
        if db_user is not None:
            raise HTTPException(status_code=st_code, detail=detail)

    return db_user



#post
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(
        usercreate: Annotated[UserCreate, Body()],
        session: SessionDep
):

    get_and_check(
        session=session,
        typ="email",
        value=str(usercreate.email),
        when_exception="not none",
        st_code=status.HTTP_409_CONFLICT,
        detail="Conflict email"
    )

    get_and_check(
        session=session,
        typ="username",
        value=usercreate.username,
        when_exception="not none",
        st_code=status.HTTP_409_CONFLICT,
        detail="Conflict username"
    )

    usercreate.password_hash = bcrypt.hashpw(usercreate.password_hash.encode(), SALT).decode()

    user = User.model_validate(usercreate)

    session.add(user)
    session.commit()

    return {"created": "ok"}


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
        email: Annotated[EmailStr, Body()],
        password: Annotated[str, Body()],
        session: SessionDep,
        response: Response,
):
    #verify
    user_db = get_and_check(
        session=session,
        typ="email",
        value=str(email),
        when_exception="none",
        st_code=status.HTTP_404_NOT_FOUND,
        detail="wrong"
    )

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
