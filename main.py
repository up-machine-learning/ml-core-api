import os

from alembic.config import Config
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import src.user.router as user_router
import src.media.router as media_router
import src.post.router as post_router
import uvicorn
from alembic import command

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Include routers
app.include_router(user_router.router)
app.include_router(media_router.router)
app.include_router(post_router.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


def apply_migrations():
    # Assuming your Alembic configuration is named 'alembic.ini'
    alembic_config = Config("alembic.ini")  # Specify the path to your alembic.ini file
    command.upgrade(alembic_config, "head")


if __name__ == "__main__":
    print("Applying database migrations...")
    apply_migrations()
    print("Database migrations applied.")
    # Get port number from environment variables, default to 8000 if not found
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
