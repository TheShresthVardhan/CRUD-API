# ===========================
# 1. IMPORTS & DEPENDENCIES
# ===========================
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row
import os
import redis
import bcrypt
import jwt

# =======================
# 2. APP INITIALIZATION
# =======================
app = FastAPI(title="Task API with Auth", version="3.0")

# ==============================
# 3. DATABASE CONNECTION SETUP
# ==============================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:supersecretpassword@db:5432/taskdb")

def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# ===========================
# 4. REDIS CONNECTION SETUP
# ===========================
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# ==========================================
# 5. SECURITY CONFIGURATION & UTILITIES
# ==========================================
# In a real production app, keep this key secret (e.g., in your .env file)
SECRET_KEY = "your-super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Tells Swagger UI where to send the login credentials
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===================================
# 6. DATA MODELS (INPUT VALIDATION)
# ===================================
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# 7. AUTHENTICATION DEPENDENCY
# ==========================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the token and returns the current username."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    return username

# ==========================================
# 8. UTILITY & DIAGNOSTIC ENDPOINTS
# ==========================================
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks", "/redis-ping", "/register", "/login", "/users/me"]}

@app.get("/redis-ping")
def ping_redis():
    """Pings the Redis container to prove they are connected."""
    try:
        is_alive = redis_client.ping() 
        return {"redis_status": "alive" if is_alive else "offline"}
    except Exception as e:
        return {"redis_status": "error", "details": str(e)}

# ==========================================
# 9. AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    hashed_pw = hash_password(user.password)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already registered")
            
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id, username",
                (user.username, hashed_pw)
            )
            new_user = cur.fetchone()
            conn.commit()
            return {"message": "User created successfully", "username": new_user["username"]}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Swagger UI sends data here as form data, not JSON."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
            user = cur.fetchone()

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# 10. PROTECTED ROUTES (Requires Login)
# ==========================================
@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    """This route is protected. It answers only for logged-in users."""
    return {"message": f"Hello, {current_user}! You have access to this protected route."}

# ==========================================
# 11. CORE CRUD ENDPOINTS
# ==========================================
@app.get("/tasks")
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id ASC")
            return cur.fetchall()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            return task
        
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
            conn.commit() 
            return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
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