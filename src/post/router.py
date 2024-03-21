from fastapi import APIRouter, Depends
import database as _database
import src.post.service as post_service
import src.user.services as user_service
from sqlalchemy.orm import Session

from src.post.schemas import CreatePostDto, PostDto
from src.post_comment.schemas import PostCommentBaseDto
from src.post_like.schemas import UpdatePostLikeDto
from src.user.model import User

router = APIRouter(
    dependencies=[Depends(user_service.get_current_user_login)],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/post")
async def create_post(create_dto: CreatePostDto,
                      db: Session = Depends(_database.get_db),
                      current_user: User = Depends(user_service.get_current_user_login)):
    data = await post_service.create_post(create_dto, db, current_user)
    return data


@router.get("/api/post", response_model=list[PostDto])
async def get_all_post(db: Session = Depends(_database.get_db),
                       current_user: User = Depends(user_service.get_current_user_login)):
    return await post_service.get_all(db, current_user)


@router.get("/api/post/{post_id}", response_model=PostDto)
async def get_post_by_id(post_id: int, db: Session = Depends(_database.get_db)):
    return await post_service.get_by_id(db, post_id)


@router.delete("/api/post/{post_id}")
async def delete_post_by_id(post_id: int, db: Session = Depends(_database.get_db)):
    return await post_service.delete_post_by_id(db, post_id)


@router.put("/api/post/{post_id}/like")
async def create_post_like(post_id: int,
                           update_dto: UpdatePostLikeDto,
                           db: Session = Depends(_database.get_db),
                           current_user: User = Depends(user_service.get_current_user_login)):
    data = await post_service.create_post_like(post_id, update_dto, db, current_user)
    return data


@router.post("/api/post/{post_id}/comment")
async def create_post_comment(post_id: int,
                              post_comment: PostCommentBaseDto,
                              db: Session = Depends(_database.get_db),
                              current_user: User = Depends(user_service.get_current_user_login)):
    data = await post_service.create_post_comment(post_id, post_comment, db, current_user)
    return data


@router.get("/api/post/{post_id}/comment/insight/{chart_type}")
async def get_post_by_id(post_id: int, chart_type: str, db: Session = Depends(_database.get_db)):
    return await post_service.get_comment_insight(db, post_id, chart_type)
