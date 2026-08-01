# Task API

A simple FastAPI CRUD API for managing tasks. Built as the Week 2 Assignment A1 of the FlyRank Internship Backend Track.

## Getting started

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python3 -m uvicorn main:app --reload
```

The API runs at http://localhost:8000.

Interactive docs (Swagger UI) are at http://localhost:8000/docs — FastAPI generates them from the code.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Returns metadata about the API |
| GET | `/health` | Health check endpoint |
| GET | `/tasks` | Returns all tasks |
| GET | `/tasks/{id}` | Returns a single task by id |
| POST | `/tasks` | Creates a new task (`{"title": "Buy milk"}`) |
| PUT | `/tasks/{id}` | Updates a task's `title` and/or `done` |
| DELETE | `/tasks/{id}` | Deletes a task |

### GET /

Response

```json
{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks"]
}
```

### GET /health

Response

```json
{ "status": "ok" }
```

### GET /tasks

Response

```json
[
  { "id": 1, "title": "Buy groceries", "done": false },
  { "id": 2, "title": "Walk the dog", "done": true },
  { "id": 3, "title": "Read a book", "done": false }
]
```

### GET /tasks/{id}

Response (200)

```json
{ "id": 1, "title": "Buy groceries", "done": false }
```

Response (404)

```json
{ "error": "Task 99 not found" }
```

### POST /tasks

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

### PUT /tasks/{id}

Updates a task's `title` and/or `done`. Send one or both fields; omitted fields stay unchanged.

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

Response (204)

Empty body — success, nothing to return.

Response (404)

```json
{ "error": "Task 99 not found" }
```

## Example

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

## Swagger UI

![Swagger UI screenshot](screenshot.png)
