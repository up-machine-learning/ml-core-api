import datetime as _dt

from sqlalchemy import Column, Integer, String, ForeignKey
import passlib.hash as _hash
from sqlalchemy.orm import relationship

from database import Base
from pydantic import BaseModel
from typing import Optional


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    type = Column(String)

    profile = relationship("Media", primaryjoin="and_(User.id == foreign(Media.entityId), Media.entityType == 'USER')",
                           uselist=False, viewonly=True)

    def __str__(self):
        return (f"User(id={self.id}, email={self.email}, name={self.name},"
                f" hashed_password={self.hashed_password}, type={self.type}, post={self.post})")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class UserPydantic(BaseModel):
    id: int
    email: str
    name: str
    hashed_password: str
    type: str

    class Config:
        from_orm = True
        from_attributes = True
