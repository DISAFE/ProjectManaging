from fastapi import APIRouter, status, Depends, Body
from typing import Annotated

from pydantic import EmailStr

from schemata import UserCreate
import jwt
import bcrypt
from database import SessionDep

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
)

@router.post("/signup", responses=status.HTTP_201_CREATED)
async def sign_up(
        usercreate: Annotated[UserCreate, Body()],
        session: SessionDep
):
    """
    :param usercreate: UserCreate model
    :param session: Database session

    Steps:
    1. check if usercreate.email or usercreate.username exists in DB
        True :raise status.HTTP_409_CONFLICT
    2. hash usercreate.password
    3. convert usercreate to user(User)
    4. create new User Record in DB
    :return: {"success": "ok"}
    """

@router.post("/login", responses=status.HTTP_200_OK)
async def login(
        email: Annotated[EmailStr, Body()],
        password: Annotated[str, Body()],
        session: SessionDep
):
    """
    :param email:
    :param password:
    :param session: Database session

    steps:
    1. Query the User table for a record matching the email
        :except status.HTTP_404_NOT_FOUND, :detail "email is not exist"
    2. verify User.password = password by bcrypt
        :except status.HTTP_404_NOT_FOUND :detail "password is wrong"
    3. make payload
    4. generate token
    :return: token(by header)
    """