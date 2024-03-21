from datetime import datetime
from typing import Optional

import pydantic as _pydantic
from src.user.schemas import UserDto, UserShortDto


class PostLikeBaseDto(_pydantic.BaseModel):
    likeType: str

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class PostLikeDto(PostLikeBaseDto):
    id: int
    createdUser: UserShortDto
    createdDate: datetime

    class Config:
        from_orm = True
        from_attributes = True


class UpdatePostLikeDto(_pydantic.BaseModel):
    likeType: Optional[str]