from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple CRUD API for managing tasks.",
)

SEED_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]

tasks = list(SEED_TASKS)
next_id = 4


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


class TaskCreate(BaseModel):
    title: str | None = None


@app.get("/", summary="API metadata")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(body: TaskCreate):
    global next_id
    if body.title is None or not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    task = {"id": next_id, "title": body.title.strip(), "done": False}
    next_id += 1
    tasks.append(task)
    return task
