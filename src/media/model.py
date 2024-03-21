from database import Base
from sqlalchemy import Column, Integer, String


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    entityType = Column('entity_type', String, nullable=False)
    entityId = Column('entity_id', Integer, nullable=False)
    filename = Column(String, nullable=False)
