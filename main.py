from fastapi import FastAPI, Query, Response
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


def find_task(task_id: int) -> dict | None:
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


@app.get("/", summary="API metadata", description="Returns metadata about the API.")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check", description="Returns whether the server is alive.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", description="Returns the whole task list, optionally filtered by done and/or search.")
def list_tasks(
    done: bool | None = Query(default=None, description="Only finished (true) or open (false) tasks"),
    search: str | None = Query(default=None, description="Title contains this word (case-insensitive)"),
):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        needle = search.lower()
        result = [t for t in result if needle in t["title"].lower()]
    return result


@app.get("/stats", summary="Task counts", description="Returns total, done and open counts.")
def stats():
    return {
        "total": len(tasks),
        "done": sum(1 for t in tasks if t["done"]),
        "open": sum(1 for t in tasks if not t["done"]),
    }


@app.post("/reset", summary="Reset to seed tasks", description="Restores the three example tasks.")
def reset():
    global tasks, next_id
    tasks = [dict(t) for t in SEED_TASKS]
    next_id = 4
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task", description="Returns one task by its id, or 404.")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", status_code=201, summary="Create a new task", description="Adds a task with a fresh id; done starts as false. Missing or empty title returns 400.")
def create_task(body: TaskCreate | None = None):
    global next_id
    if body is None or body.title is None or not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    task = {"id": next_id, "title": body.title.strip(), "done": False}
    next_id += 1
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done", description="Replaces the given fields; omitted fields stay unchanged. Empty body returns 400, unknown id returns 404.")
def update_task(task_id: int, body: TaskUpdate | None = None):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    if body is None:
        return JSONResponse(status_code=400, content={"error": "request body must include title and/or done"})
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        return JSONResponse(status_code=400, content={"error": "request body must include title and/or done"})
    if "title" in changes and (body.title is None or not body.title.strip()):
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    if "done" in changes and body.done is None:
        return JSONResponse(status_code=400, content={"error": "done must be true or false"})
    if "title" in changes:
        task["title"] = body.title.strip()
    if "done" in changes:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task", description="Removes a task; returns 204 with no body, or 404 for an unknown id.")
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    tasks.remove(task)
    return Response(status_code=204)
