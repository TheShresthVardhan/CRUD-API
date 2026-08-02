from fastapi import FastAPI

from src.middleware.error_handler import register_error_handlers
from src.routes import extras, tasks

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple CRUD API for managing tasks.",
)

app.include_router(tasks.router)
app.include_router(extras.router)
register_error_handlers(app)
