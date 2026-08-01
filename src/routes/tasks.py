from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from src.deps import get_service
from src.services.tasks import TaskService

router = APIRouter()


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


@router.get("/", summary="API metadata", description="Returns metadata about the API.")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@router.get("/health", summary="Health check", description="Returns whether the server is alive.")
def health():
    return {"status": "ok"}


@router.get("/tasks", summary="List all tasks", description="Returns the whole task list, optionally filtered by done and/or search.")
def list_tasks(
    done: bool | None = Query(default=None, description="Only finished (true) or open (false) tasks"),
    search: str | None = Query(default=None, description="Title contains this word (case-insensitive)"),
    service: TaskService = Depends(get_service),
):
    return service.list_tasks(done=done, search=search)


@router.get("/stats", summary="Task counts", description="Returns total, done and open counts.")
def stats(service: TaskService = Depends(get_service)):
    return service.stats()


@router.post("/reset", summary="Reset to seed tasks", description="Restores the three example tasks.")
def reset(service: TaskService = Depends(get_service)):
    return service.reset()


@router.get("/tasks/{task_id}", summary="Get a single task", description="Returns one task by its id, or 404.")
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    return service.get_task(task_id)


@router.post("/tasks", status_code=201, summary="Create a new task", description="Adds a task with a fresh id; done starts as false. Missing or empty title returns 400.")
def create_task(body: TaskCreate | None = None, service: TaskService = Depends(get_service)):
    return service.create_task(title=None if body is None else body.title)


@router.put("/tasks/{task_id}", summary="Update a task's title and/or done", description="Replaces the given fields; omitted fields stay unchanged. Empty body returns 400, unknown id returns 404.")
def update_task(task_id: int, body: TaskUpdate | None = None, service: TaskService = Depends(get_service)):
    changes = {} if body is None else body.model_dump(exclude_unset=True)
    return service.update_task(task_id, changes)


@router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task", description="Removes a task; returns 204 with no body, or 404 for an unknown id.")
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    service.delete_task(task_id)
    return Response(status_code=204)
