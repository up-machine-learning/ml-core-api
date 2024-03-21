from typing import List

from fastapi import UploadFile, HTTPException
from .model import Media
from sqlalchemy.orm import Session
import uuid
import os
from sqlalchemy import and_

from .schemas import MediaDto

STATIC_FOLDER = "static/"


async def upload(entityType: str, entityId: int, file: UploadFile, db: Session):
    supportEntityType = ['USER', 'POST']
    if entityType.upper() not in supportEntityType:
        raise HTTPException(
            status_code=403, detail="entity type not support"
        )
    unique_id = uuid.uuid4().hex
    file_extension = os.path.splitext(file.filename)
    unique_filename = f"{unique_id}{file_extension[-1]}"
    unique_filename = os.path.join(STATIC_FOLDER, unique_filename)

    # Save the file to the server
    with open(unique_filename, "wb") as buffer:
        buffer.write(await file.read())

    mediaObj = Media(filename=unique_filename, entityType=entityType.upper(), entityId=entityId)
    db.add(mediaObj)
    db.commit()
    db.refresh(mediaObj)
    return mediaObj


async def get_medias(entity_type: str, entity_id: int, db: Session) -> list[MediaDto]:
    medias = (db.query(Media)
              .filter(and_(Media.entityType == entity_type.upper(), Media.entityId == entity_id))
              .all())
    media_dtos = [MediaDto.from_orm(media) for media in medias]
    return media_dtos


async def get_media(media_id: int, db: Session) -> Media:
    media = db.query(Media).get(media_id)
    return media
