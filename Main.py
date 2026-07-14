from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional  # <-- New import for Stage 4

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

# <-- New Model for Stage 4 -->
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# --- Stage 1, 2 & 3 Endpoints ---
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    global current_id
    current_id += 1
    new_task = {"id": current_id, "title": task.title, "done": False}
    tasks_db.append(new_task)
    return new_task

# --- Stage 4 Endpoints ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    # Validate: If a title is provided, it cannot be empty
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    for task in tasks_db:
        if task["id"] == task_id:
            # Update only the fields that were actually sent in the request
            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.done is not None:
                task["done"] = task_update.done
            return task
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return # Returns 204 with no content automatically
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")