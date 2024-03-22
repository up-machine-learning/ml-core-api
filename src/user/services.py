import os

import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from dotenv import load_dotenv

from src.user.model import User
from src.user.schemas import *
import src.media.service as media_service

import database as _database

load_dotenv()
oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = os.getenv("JWT_SECRET")


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(User).filter(User.email == email).first()


async def create_user(user: UserCreateDto, db: _orm.Session):

    user_obj = User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password), name=user.name,
        type='USER'
    )
    db.add(user_obj)
    db.commit()

    # update media entity id
    media = await media_service.get_media(user.profileId, db)
    if media is None:
        raise _fastapi.HTTPException(
            status_code=403, detail="mediaId not found"
        )

    media.entityId = user_obj.id
    db.add(media)
    db.commit()
    db.refresh(user_obj)

    return UserDto.from_orm(user_obj)


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def create_token(user: UserDto):
    user_obj = UserDto.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
        db: _orm.Session = _fastapi.Depends(_database.get_db),
        token: str = _fastapi.Depends(oauth2schema),
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["id"]
        user = db.query(User).get(user_id)

        data = UserDto.from_orm(user)
        # get profile in media
        current_user_media = await media_service.get_medias("USER", user_id, db)
        if len(current_user_media) > 0:
            data.profile = current_user_media[0].filename
        return data
    except Exception as e:
        print(e)
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )


async def get_current_user_login(
        db: _orm.Session = _fastapi.Depends(_database.get_db),
        token: str = _fastapi.Depends(oauth2schema)
) -> User:
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["id"]
        user = db.query(User).get(user_id)

        return user
    except Exception as e:
        print(e)
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )


async def get_user(
        db: _orm.Session = _fastapi.Depends(_database.get_db),
        token: str = _fastapi.Depends(oauth2schema)
):
    user = db.query(User).all()

    return user


async def get_by_id(user_id: int, db: _orm.Session):
    return db.query(User).get(user_id)
