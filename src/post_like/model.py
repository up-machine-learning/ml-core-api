from typing import List

from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func


class PostLike(Base):
    __tablename__ = "post_like"
    id = Column(Integer, primary_key=True, index=True)
    postId = Column('post_id', Integer, ForeignKey('post.id'))

    likeType = Column('like_type', String, nullable=False)
    createdUserId = Column('created_user_id', Integer, ForeignKey('users.id'))
    createdDate = Column('created_date', DateTime(timezone=True), nullable=False, default=func.now())

    createdUser = relationship("User")
    post = relationship("Post", back_populates="postLikes")

