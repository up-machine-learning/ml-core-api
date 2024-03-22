from typing import List, Optional

from fastapi import APIRouter, Depends, Query
import src.user.services as user_service
import src.suggestion.service as suggestion_service
from src.suggestion.schemas import CreateSuggestionDto, DestinationDto, DestinationPageDto
from src.user.model import User

router = APIRouter(
    dependencies=[Depends(user_service.get_current_user_login)],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/trip/suggestion")
async def trip_suggestion(create_dto: CreateSuggestionDto,
                          current_user: User = Depends(user_service.get_current_user_login)):
    return await suggestion_service.trip_suggestion(create_dto, current_user)


@router.post("/api/trip/model/build")
async def build_ai_trip_model():
    return await suggestion_service.build_ai_trip_model()


@router.get("/api/trip/destinations", response_model=DestinationPageDto)
async def get_destinations(
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=10, ge=1, le=100),
        search: Optional[str] = None
):
    return await suggestion_service.get_all_destinations(page, limit, search)


@router.get("/api/trip/preferences")
async def get_preferences(name: Optional[str] = None):
    return await suggestion_service.get_all_preferences(name)

