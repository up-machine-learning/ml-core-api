from datetime import datetime
from typing import Optional, List

import pydantic as _pydantic

from src.media.schemas import MediaShortDto
from src.post_comment.schemas import PostCommentDto
from src.post_like.schemas import PostLikeDto
from src.user.schemas import UserShortDto


class PostBaseDto(_pydantic.BaseModel):
    description: str

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class PostDto(PostBaseDto):
    id: int
    createdUser: UserShortDto
    createdDate: datetime
    postLikes: Optional[List[PostLikeDto]]
    postComments: Optional[List[PostCommentDto]]
    medias: Optional[List[MediaShortDto]]

    class Config:
        from_orm = True
        from_attributes = True


class CreatePostDto(PostBaseDto):
    mediaId: int

    class Config:
        from_orm = True
        arbitrary_types_allowed = True
