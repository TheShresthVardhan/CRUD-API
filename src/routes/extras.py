from fastapi import APIRouter, Depends

from src.deps import get_service
from src.services.tasks import TaskService

router = APIRouter()


@router.get("/stats", summary="Task counts", description="Returns total, done and open counts, computed with COUNT() and SUM() in SQL.")
def stats(service: TaskService = Depends(get_service)):
    return service.stats()


@router.post("/reset", summary="Reset to seed tasks", description="Clears the database and restores the three example tasks with fresh timestamps.")
def reset(service: TaskService = Depends(get_service)):
    return service.reset()
