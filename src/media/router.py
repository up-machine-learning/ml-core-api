from fastapi import APIRouter, Depends, File, UploadFile
import database as _database
import src.media.service as media_service
import src.user.services as user_service
from sqlalchemy.orm import Session

from src.media.schemas import MediaDto

router = APIRouter(
    # dependencies=[Depends(user_service.get_current_user_login)],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/media/{entity_type}/{entity_id}")
async def upload_file(entity_type: str, entity_id: int, file: UploadFile = File(...),
                      db: Session = Depends(_database.get_db)):
    print("jol")
    db_media = await media_service.upload(entity_type, entity_id, file, db)
    return db_media


@router.get("/api/media/{entity_type}/{entity_id}", response_model=list[MediaDto])
async def get_list(entity_type: str, entity_id: int, db: Session = Depends(_database.get_db)):
    return await media_service.get_medias(entity_type, entity_id, db)
