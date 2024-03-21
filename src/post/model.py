from typing import List

from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

from src.post_comment.model import PostComment
from src.post_like.model import PostLike


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, index=True)
    description = Column('description', String, nullable=False)
    createdUserId = Column('created_user_id', Integer, ForeignKey('users.id'))
    createdDate = Column('created_date', DateTime(timezone=True), nullable=False, default=func.now())
    medias = relationship("Media", primaryjoin="and_(Post.id == foreign(Media.entityId), Media.entityType == 'POST')",
                          uselist=True, viewonly=True)

    createdUser = relationship("User")
    postLikes = relationship(PostLike, cascade="all, delete-orphan", back_populates="post")
    postComments = relationship(PostComment, cascade="all, delete-orphan", back_populates="post")

    def __str__(self):
        return (f"Post(id={self.id}, description={self.description}, createdUserId={self.createdUserId},"
                f" createdDate={self.createdDate}, createdUser={self.createdUser})")
