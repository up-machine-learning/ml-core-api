from typing import Optional

import pydantic as _pydantic

from src.media.schemas import MediaDto, MediaShortDto


class UserBaseDto(_pydantic.BaseModel):
    email: str
    name: str
    profile: Optional[MediaDto] = None


class UserCreateDto(UserBaseDto):
    hashed_password: str
    profileId: int

    class Config:
        from_attributes = True
        from_orm = True


class UserDto(UserBaseDto):
    id: int

    class Config:
        from_orm = True
        from_attributes = True


class UserShortDto(_pydantic.BaseModel):
    id: int
    name: str
    profile: Optional[MediaShortDto] = None

    class Config:
        from_orm = True
        from_attributes = True
