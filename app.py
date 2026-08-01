from fastapi import FastAPI

from src.middleware.error_handler import register_error_handlers
from src.routes.tasks import router

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple CRUD API for managing tasks.",
)

app.include_router(router)
register_error_handlers(app)
