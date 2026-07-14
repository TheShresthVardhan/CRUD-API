from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

# --- In-Memory Database ---
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read HTTP documentation", "done": True},
    {"id": 3, "title": "Build Stage 2", "done": False}
]

# This tracks the highest ID so it can be incremented for new tasks.
current_id = 3

# --- Data Models ---
# This tells FastAPI to expect a JSON body with a 'title' string.
class TaskCreate(BaseModel):
    title: str

# --- Stage 1 & 2 Endpoints ---
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

# --- Stage 3 Endpoint ---
# Specify that status_code=201 here so a successful creation returns "201 Created".
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    # Validation: Check if the title is missing or just empty spaces
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    global current_id
    current_id += 1
    
    # Create the new task object, defaulting 'done' to False
    new_task = {"id": current_id, "title": task.title, "done": False}
    tasks_db.append(new_task)
    
    # Return the newly created task (your "receipt")
    return new_task