from fastapi import FastAPI, HTTPException

app = FastAPI(title="Task API", version="1.0")

# --- In-Memory Database ---
# Pre-filled with 3 example tasks.
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read HTTP documentation", "done": True},
    {"id": 3, "title": "Build Stage 2", "done": False}
]

# --- Stage 1 Endpoints ---
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Stage 2 Endpoints ---
@app.get("/tasks")
def get_tasks():
    """Returns the entire list of tasks."""
    return tasks_db

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Returns a single task by its ID."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    # If the loop finishes without finding the task, return a 404 error.
    # Never return an empty 200 for something that doesn't exist.
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")