# ===========================
# 1. IMPORTS & DEPENDENCIES
# ===========================
# fastapi: The core framework for building the API.
# pydantic: Used for defining and validating the shape of incoming data.
# psycopg: The driver that allows Python to talk to the PostgreSQL database.
# os: Allows Python to read environment variables (like our database password).
# redis: The library used to connect to the Redis caching server.
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import psycopg
from psycopg.rows import dict_row
import os
import redis  

# =======================
# 2. APP INITIALIZATION
# =======================
# This creates the actual FastAPI application instance. 
# The title and version here are what show up on the Swagger UI page.
app = FastAPI(title="Task API with Postgres & Redis", version="2.0")

# ==============================
# 3. DATABASE CONNECTION SETUP
# ==============================
# It fetchs the connection string from the .env file. If it can't find one, 
# it falls back to the default localhost string.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:supersecretpassword@db:5432/taskdb")

# This helper function opens a connection to the database. 
# Using dict_row ensures our SQL results come back looking like Python dictionaries.
def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# ===========================
# 4. REDIS CONNECTION SETUP
# ===========================
# It fetchs the Redis host from the environment variables (set in docker-compose.yml)
# and create a client to talk to the Redis container.
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


# ===================================
# 5. DATA MODELS (INPUT VALIDATION)
# ===================================
# These Pydantic models act as bouncers for our API. They dictate exactly 
# what JSON data is allowed in for POST (creating) and PUT (updating) requests.
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ====================
# OLD IN-MEMORY CODE
# ====================
"""
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read HTTP documentation", "done": True},
    {"id": 3, "title": "Build Stage 2", "done": False}
]
current_id = 3

@app.get("/tasks")
def get_tasks_in_memory(search: Optional[str] = None):
    if search:
        return [task for task in tasks_db if search.lower() in task["title"].lower()]
    return tasks_db

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task_in_memory(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    global current_id
    current_id += 1
    new_task = {"id": current_id, "title": task.title, "done": False}
    tasks_db.append(new_task)
    return new_task
"""

# ==========================================
# 6. UTILITY & DIAGNOSTIC ENDPOINTS
# ==========================================
# These routes don't touch the main data; they exist to provide info 
# about the API or check if internal services (like Redis) are running.

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks", "/redis-ping"]}

# --- Redis Ping Endpoint ---
@app.get("/redis-ping")
def ping_redis():
    """Pings the Redis container to prove they are connected."""
    try:
        # returns True if Redis is alive
        is_alive = redis_client.ping() 
        return {"redis_status": "alive" if is_alive else "offline"}
    except Exception as e:
        return {"redis_status": "error", "details": str(e)}

# ==========================================
# 7. CORE CRUD ENDPOINTS
# ==========================================
# These endpoints handle the Create, Read, Update, and Delete operations.
# Each endpoint opens a database connection, executes a specific SQL query,
# commits the changes (if writing data), and returns the result.

# READ: Get all tasks
@app.get("/tasks")
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id ASC")
            return cur.fetchall()

# READ: Get a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            return task
        
# CREATE: Add a new task to the database
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
                (task.title, False)
            )
            new_task = cur.fetchone()
            conn.commit() # Save the change to the database
            return new_task

# UPDATE: Modify an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if the task exists first
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

            new_title = task_update.title if task_update.title is not None else existing['title']
            new_done = task_update.done if task_update.done is not None else existing['done']

            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
                (new_title, new_done, task_id)
            )
            updated_task = cur.fetchone()
            conn.commit()
            return updated_task

# DELETE: Remove a task from the database
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            conn.commit()
            return