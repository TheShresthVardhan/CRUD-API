from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Task API", version="1.0")

# --- In-Memory Database ---
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read HTTP documentation", "done": True},
    {"id": 3, "title": "Build Stage 2", "done": False}
]
current_id = 3

# --- Data Models ---
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# --- Core API Info ---
@app.get("/")
def read_root():
    """Returns basic information about the API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/stats", "/reset"]}

@app.get("/health")
def health_check():
    """Checks if the server is running."""
    return {"status": "ok"}

# --- EXTRA: Stats ---
@app.get("/stats")
def get_stats():
    """Returns statistics about the current tasks."""
    total = len(tasks_db)
    # This counts how many tasks have "done" set to True
    done_count = sum(1 for task in tasks_db if task["done"])
    open_count = total - done_count
    
    return {"total": total, "done": done_count, "open": open_count}

# --- EXTRA: Reset ---
@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_tasks():
    """Restores the database to the 3 initial example tasks."""
    global current_id
    tasks_db.clear()
    tasks_db.extend([
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Read HTTP documentation", "done": True},
        {"id": 3, "title": "Build Stage 2", "done": False}
    ])
    current_id = 3
    return {"message": "Database reset to initial state"}

# --- Tasks CRUD ---
@app.get("/tasks")
def get_tasks(
    search: Optional[str] = None, 
    done: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: int = 0
):
    """
    Lists tasks. Includes optional EXTRAS:
    - Search: ?search=milk
    - Filter: ?done=true
    - Pagination: ?limit=2&offset=1
    """
    results = tasks_db

    # 1. Search Filter (if search term is provided)
    if search is not None:
        results = [task for task in results if search.lower() in task["title"].lower()]
    
    # 2. Done Filter (if done status is provided)
    if done is not None:
        results = [task for task in results if task["done"] == done]

    # 3. Pagination (apply offset and limit)
    if limit is not None:
        results = results[offset : offset + limit]
    else:
        results = results[offset : ]

    return results

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Retrieves a single task by its ID."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Creates a new task."""
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    global current_id
    current_id += 1
    new_task = {"id": current_id, "title": task.title, "done": False}
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    """Updates an existing task's title or completion status."""
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    for task in tasks_db:
        if task["id"] == task_id:
            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.done is not None:
                task["done"] = task_update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Deletes a task from the database."""
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return 
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")