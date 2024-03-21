from fastapi import APIRouter, Depends, HTTPException
import fastapi.security as _security
import src.user.services as user_service

from .schemas import *

from sqlalchemy.orm import Session
import database as _database

router = APIRouter()


@router.post("/api/users")
async def create_user(
        user: UserCreateDto, db: Session = Depends(_database.get_db)
):
    db_user = await user_service.get_user_by_email(user.email, db)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user = await user_service.create_user(user, db)

    return user


@router.get("/api/users", response_model=list[UserDto])
async def get_user(users: list = Depends(user_service.get_user)):
    return users


@router.post("/api/token")
async def generate_token(
        form_data: _security.OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(_database.get_db),
):
    user = await user_service.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return await user_service.create_token(user)


@router.get("/api/users/current", response_model=UserDto)
async def get_current_user(user: UserDto = Depends(user_service.get_current_user)):
    return user
