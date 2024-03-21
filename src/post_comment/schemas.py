from datetime import datetime
from decimal import Decimal

import pydantic as _pydantic
from src.user.schemas import UserShortDto


class PostCommentBaseDto(_pydantic.BaseModel):
    comment: str

    class Config:
        from_attributes = True
        from_orm = True


class PostCommentDto(PostCommentBaseDto):
    id: int
    createdUser: UserShortDto
    createdDate: datetime
    sentimentScore: Decimal
    sentimentResult: str

    class Config:
        from_orm = True
        from_attributes = True