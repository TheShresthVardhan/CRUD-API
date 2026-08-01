# 🗂️ Task API

A simple FastAPI CRUD API for managing tasks, backed by SQLite. Because "I'll remember that" is a lie we've all told ourselves.

## 📁 Project structure

```text
.
├── main.py                     # starts the server — just the port
├── app.py                      # wires everything into FastAPI
├── requirements.txt            # dependencies (fastapi, uvicorn)
├── README.md                   # this file (full of puns, you're welcome)
├── SwaggerUI 1.png             # Swagger UI screenshot
├── tasks.db                    # the SQLite database (git-ignored, created on first run)
└── src/
    ├── routes/tasks.py         # HTTP layer
    ├── services/tasks.py       # business rules
    ├── repositories/tasks.py   # data access
    ├── middleware/error_handler.py
    ├── deps.py                 # builds the repository + service
    └── errors.py               # domain error types
```

## 🏗️ A1 — Build your first CRUD API

Built as Assignment A1 of the FlyRank Internship Backend Track: a CRUD API where you can create, read, update and delete tasks, see it in Swagger UI, and publish it to GitHub.

## 🗄️ Why SQLite?

The API used to keep its tasks in a Python list in memory — restart the server and poof 💨, everything was gone. SQLite was chosen as the replacement because:

- It's a **real SQL database** that still fits a small local project — no separate database server to install or run, just a library (Python's built-in `sqlite3`) and a file
- Data **survives server restarts** (unlike the old in-memory list)
- It's enough SQL to practice `SELECT`, `INSERT`, `UPDATE`, and `DELETE` without the overhead of Postgres or MySQL

## 📄 Database file

Tasks are stored in `tasks.db` in the project root (next to `main.py`).

The file is created automatically the first time the app starts, with the table and three example tasks seeded on that first run — and only on the first run. It's listed in `.gitignore`, so each clone starts fresh with its own database.

The table is created only if it doesn't exist, and the seed only runs when the table is empty — restarting a hundred times still gives you exactly three tasks.

## 🚀 Getting started

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python3 main.py
```

The API runs at http://localhost:8000. Interactive docs (Swagger UI) are at http://localhost:8000/docs — FastAPI generates them from the code, so there's no excuse for bad documentation. 😌

## 📋 Endpoints — one table to rule them all

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Returns metadata about the API |
| GET | `/health` | Health check endpoint |
| GET | `/tasks` | Returns all tasks. Optional `done` and `search` query parameters filter the list |
| GET | `/tasks/{id}` | Returns a single task by id |
| POST | `/tasks` | Creates a new task (`{"title": "Buy milk"}`) |
| PUT | `/tasks/{id}` | Updates a task's `title` and/or `done` |
| DELETE | `/tasks/{id}` | Deletes a task |
| GET | `/stats` | Returns computed counts for the current task list |
| POST | `/reset` | Restores the three seed example tasks |

### GET /

Returns metadata about the API. Meta, isn't it? 😉

Response

```json
{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks"]
}
```

### GET /health

"It's alive!" 🧟 — real companies use exactly this endpoint to check the server is breathing.

Response

```json
{ "status": "ok" }
```

### GET /tasks

The full lineup. 🎸 Optional query parameters filter the list (the part after `?` — filters, not addresses):

| Query | Example | Effect |
| --- | --- | --- |
| `done` | `?done=true` | Only finished tasks |
| `done` | `?done=false` | Only open tasks |
| `search` | `?search=milk` | Title contains the word (case-insensitive) |

Filters can be combined: `?done=false&search=book`. Put on your detective hat 🕵️ and hunt those tasks down.

Response

```json
[
  { "id": 1, "title": "Buy groceries", "done": false },
  { "id": 2, "title": "Walk the dog", "done": true },
  { "id": 3, "title": "Read a book", "done": false }
]
```

### GET /tasks/{id}

One task to rule them all — well, one task, period. Returns it by id.

Response (200)

```json
{ "id": 1, "title": "Buy groceries", "done": false }
```

Response (404)

```json
{ "error": "Task 99 not found" }
```

Task 99 is probably on a beach somewhere. 🏖️

### POST /tasks

A new task is born. 👶 The server gives it the next free id, sets `done` to `false`, and adds it to the list.

Request body

```json
{ "title": "Buy milk" }
```

Response (201)

```json
{ "id": 4, "title": "Buy milk", "done": false }
```

Response (400)

```json
{ "error": "title is required and cannot be empty" }
```

No title, no task. The server never trusts the client. 🤨

### GET /stats

Counting tasks so you don't have to. 🧮

Response

```json
{ "total": 7, "done": 3, "open": 4 }
```

Example

```bash
curl http://localhost:8000/stats
```

### POST /reset

The Ctrl+Z of your to-do list. ⌨️ Restores the three seed example tasks. Useful for demos and testing.

Response (200)

```json
[
  { "id": 1, "title": "Buy groceries", "done": false },
  { "id": 2, "title": "Walk the dog", "done": true },
  { "id": 3, "title": "Read a book", "done": false }
]
```

Example

```bash
curl -X POST http://localhost:8000/reset
```

### PUT /tasks/{id}

Task got a glow-up. ✨ Updates a task's `title` and/or `done`. Send one or both fields; omitted fields stay unchanged.

Request body

```json
{ "title": "Buy oat milk", "done": true }
```

Response (200)

```json
{ "id": 1, "title": "Buy oat milk", "done": true }
```

Response (400)

```json
{ "error": "request body must include title and/or done" }
```

Response (404)

```json
{ "error": "Task 99 not found" }
```

### DELETE /tasks/{id}

Bye-bye, task. 👋 Faster than your New Year's resolutions. 🥂

Response (204)

Empty body — success, nothing to return. Silence is golden. 🤫

Response (404)

```json
{ "error": "Task 99 not found" }
```

## 🧾 Example

Proof it works, in black and white:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

Output

```
HTTP/1.1 201 Created
date: Sat, 01 Aug 2026 20:03:33 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## 🎨 Swagger UI

Pretty documentation with zero effort:

![Swagger UI screenshot](SwaggerUI%201.png)

## 📊 Example SQL query

This is what `GET /tasks` runs under the hood (plus one query I ran by hand in DB Browser):

```sql
SELECT id, title, done FROM tasks ORDER BY id;
```

The one I ran by hand: `UPDATE tasks SET done = 1;` — it marked every task complete in a single statement, and `GET /tasks` showed the change immediately with no restart, because the API and DB Browser read the exact same file.

<img src="DBBrowser1.png" alt="DB Browser — table structure" width="300">

![DB Browser — browsing the data](DBBrowser2.png)

## 💾 Persistence

The goldfish era is over 🐠➡️🗄️: restart the server and your tasks are still there. The data now lives in `tasks.db`, a file on disk, instead of a Python list in memory — that's the entire difference between a demo and something real.
