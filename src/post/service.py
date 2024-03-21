import base64
from collections import defaultdict
from datetime import datetime
import io

from fastapi import HTTPException
from nltk.sentiment import SentimentIntensityAnalyzer
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from .model import Post
from .schemas import CreatePostDto, PostDto
from ..media.model import Media
from ..post_comment.model import PostComment
from ..post_comment.schemas import PostCommentBaseDto
from ..post_like.model import PostLike
from ..post_like.schemas import UpdatePostLikeDto
from ..user.model import User
import src.media.service as media_service
import matplotlib.pyplot as plt


async def create_post(create_post_dto: CreatePostDto, db: Session, current_user: User):
    if current_user.type == 'USER':
        raise HTTPException(
            status_code=403, detail="user not allow to create post"
        )

    post_obj = Post(description=create_post_dto.description, createdUser=current_user)
    post_obj.createdDate = datetime.now()
    db.add(post_obj)
    db.commit()

    # update media entity id
    media = await media_service.get_media(create_post_dto.mediaId, db)
    if media is None:
        raise HTTPException(
            status_code=404, detail="mediaId not found"
        )

    media.entityId = post_obj.id
    db.add(media)
    db.commit()

    db.refresh(post_obj)
    return post_obj


async def get_all(db: Session, current_user: User) -> list[PostDto]:
    if current_user.type.upper() == 'PAGE':
        posts = (db.query(Post)
                 .filter(Post.createdUserId == current_user.id)
                 .order_by(desc(Post.createdDate))
                 .all())
    else:
        posts = db.query(Post).order_by(desc(Post.createdDate)).all()

    post_dtos = [PostDto.from_orm(post) for post in posts]

    return post_dtos


async def get_by_id(db: Session, post_id: int) -> PostDto:
    data = db.query(Post).get(post_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostDto.from_orm(data)


async def create_post_like(post_id: int, update_dto: UpdatePostLikeDto, db: Session, current_user: User):
    like_type_support = ['', 'LIKE', 'HEARTH', 'CARE', 'HAHA', 'WONDER', 'SAD', 'ANGRY']
    if update_dto.likeType not in like_type_support:
        raise HTTPException(
            status_code=403, detail="like type not support"
        )

    post_like_obj = PostLike(postId=post_id, likeType=update_dto.likeType, createdUser=current_user)
    post_like_obj.createdDate = datetime.now()
    post_likes = db.query(PostLike).filter(
        and_(PostLike.postId == post_id, PostLike.createdUserId == current_user.id)).all()
    for post_like in post_likes:
        db.delete(post_like)
        db.commit()

    if update_dto.likeType is not None and update_dto.likeType != '':
        db.add(post_like_obj)
        db.commit()
        db.refresh(post_like_obj)
        return post_like_obj
    else:
        return None


async def create_post_comment(post_id: int, post_comment: PostCommentBaseDto, db: Session, current_user: User):
    ai = SentimentIntensityAnalyzer()

    sentiment_scores = ai.polarity_scores(post_comment.comment)
    sentiment_score = sentiment_scores['compound']
    if sentiment_score >= 0.05:
        sentiment_result = 'positive'
    elif sentiment_score <= -0.05:
        sentiment_result = 'negative'
    else:
        sentiment_result = 'neutral'

    post_comment_obj = PostComment(postId=post_id, comment=post_comment.comment, createdUser=current_user,
                                   sentimentScore=sentiment_score, sentimentResult=sentiment_result.upper())
    post_comment_obj.createdDate = datetime.now()
    db.add(post_comment_obj)
    db.commit()
    db.refresh(post_comment_obj)
    return post_comment_obj


async def get_comment_insight(db: Session, post_id: int, chart_type: str):
    positive_texts = db.query(PostComment).filter(and_(PostComment.postId == post_id,
                                                       PostComment.sentimentResult == 'POSITIVE')).count()
    negative_texts = db.query(PostComment).filter(and_(PostComment.postId == post_id,
                                                       PostComment.sentimentResult == 'NEGATIVE')).count()

    neutral_texts = db.query(PostComment).filter(and_(PostComment.postId == post_id,
                                                      PostComment.sentimentResult == 'NEUTRAL')).count()
    # Sentiment report data
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [positive_texts, negative_texts, neutral_texts]
    colors = ['#66c2a5', '#fc8d62', '#8da0cb']

    if chart_type == 'pie':
        # Create pie chart
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Sentiment Analysis Pie Report')
    elif chart_type == 'bar':
        # Create bar chart
        plt.figure(figsize=(8, 6))
        plt.bar(labels, sizes, color=colors)
        plt.xlabel('Sentiment')
        plt.ylabel('Number of Comments')
        plt.title('Sentiment Analysis Bar Report')
    elif chart_type == 'over_time':
        # Plot sentiment over time
        post_comments: [PostComment] = db.query(PostComment).filter(PostComment.postId == post_id).order_by(
            PostComment.createdDate.asc()).all()
        print(post_comments)
        # Group comments by creation date
        sentiment_over_time = defaultdict(list)
        for comment in post_comments:
            created_date = comment.createdDate.date()
            sentiment_over_time[created_date].append(comment.sentimentResult)

        # Calculate sentiment distribution over time
        positive_count = []
        negative_count = []
        neutral_count = []
        dates = []

        for date, comments in sentiment_over_time.items():
            dates.append(date)
            positive_count.append(comments.count("POSITIVE"))
            negative_count.append(comments.count("NEGATIVE"))
            neutral_count.append(comments.count("NEUTRAL"))

        # Plot sentiment distribution over time
        plt.figure(figsize=(10, 6))
        plt.plot(dates, positive_count, label="Positive", color="green")
        plt.plot(dates, negative_count, label="Negative", color="red")
        plt.plot(dates, neutral_count, label="Neutral", color="blue")
        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.title("Sentiment Analysis Over Time Report")
        plt.legend()
        plt.grid(True)
    else:
        raise HTTPException(
            status_code=404, detail="chart type is not support"
        )

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert plot image to Base64 encoding
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    # Close the plot to free resources
    plt.close()

    # Return the plot image data in the API response
    return {"plot_image": plot_data}


async def delete_post_by_id(db, post_id):
    post = db.query(Post).get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # delete media
    db.query(Media).filter(Media.entityType == 'POST', Media.entityId == post_id).delete(synchronize_session=False)
    db.commit()

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}