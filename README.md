# Task API

A simple, in-memory CRUD API for managing a to-do list, built with **Python** and **FastAPI**.

This project was built for the FlyRank Internship Backend Track — Week 2, Assignment A1
("Build your first CRUD API"). It implements full Create / Read / Update / Delete
operations on a to-do list, exposes interactive documentation via Swagger UI, and stores
data in memory.

## Features

- Full CRUD on tasks: `GET`, `POST`, `PUT`, `DELETE`
- Input validation (empty/missing titles are rejected with `400`)
- Proper HTTP status codes (`200`, `201`, `204`, `400`, `404`)
- Auto-generated interactive docs at `/docs` (Swagger UI) — built into FastAPI, zero setup
- In-memory storage, pre-seeded with 3 example tasks

## How to Run

1. Install the requirements:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
3. The API will be available at `http://localhost:8000`.
   Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## Endpoints

| HTTP Method | Endpoint         | Description                          |
| :---------- | :--------------- | :------------------------------------ |
| GET         | `/`              | API root / info                       |
| GET         | `/health`        | Health check                          |
| GET         | `/tasks`         | List all tasks                        |
| GET         | `/tasks/{id}`    | Get a specific task                   |
| POST        | `/tasks`         | Create a new task                     |
| PUT         | `/tasks/{id}`    | Update a task (title and/or done)     |
| DELETE      | `/tasks/{id}`    | Delete a task                         |

### Task object

```json
{
  "id": 1,
  "title": "Buy milk",
  "done": false
}
```

## Example Requests

**Create a task**

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Tue, 14 Jul 2026 15:13:22 GMT
server: uvicorn
content-length: 42
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

**Get a task that doesn't exist**

```bash
$ curl -i http://localhost:8000/tasks/99

HTTP/1.1 404 Not Found
content-type: application/json

{"detail":"Task 99 not found"}
```

**Update a task**

```bash
$ curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"done":true}'

HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy milk","done":true}
```

**Delete a task**

```bash
$ curl -i -X DELETE http://localhost:8000/tasks/1

HTTP/1.1 204 No Content
```

## Swagger UI

Visit `http://localhost:8000/docs` to see all endpoints listed with an interactive
"Try it out" button that lets you run the full CRUD cycle without curl.

![Swagger UI screenshot](swagger-screenshot.png)

## Notes

- Data lives only in memory — restarting the server resets it back to the 3 seed tasks.
- Validation: `POST` and `PUT` reject a missing or empty `title` with a `400` response.
- Unknown task IDs return `404` on `GET`, `PUT`, and `DELETE`.
