import sqlite3

SEED_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]


class TaskRepository:
    """The only class that knows where tasks are stored (SQLite now)."""

    def __init__(self, db_path: str = "tasks.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_schema()
        self._seed_if_empty()
        self._tasks = [dict(t) for t in SEED_TASKS]

    def _create_schema(self):
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY,"
            "title TEXT NOT NULL,"
            "done INTEGER NOT NULL DEFAULT 0)"
        )
        self._conn.commit()

    def _seed_if_empty(self):
        count = self._conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            self._conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [(t["title"], int(t["done"])) for t in SEED_TASKS],
            )
            self._conn.commit()

    def find_all(self) -> list:
        rows = self._conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [self._to_dict(r) for r in rows]

    def find_by_id(self, task_id: int) -> dict | None:
        row = self._conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_dict(row) if row else None

    @staticmethod
    def _to_dict(row) -> dict:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

    def add(self, task: dict) -> None:
        self._tasks.append(task)

    def remove(self, task: dict) -> None:
        self._tasks.remove(task)

    def reset(self) -> None:
        self._conn.execute("DELETE FROM tasks")
        self._conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [(t["title"], int(t["done"])) for t in SEED_TASKS],
        )
        self._conn.commit()
        self._tasks = [dict(t) for t in SEED_TASKS]

    def next_id(self) -> int:
        return max((t["id"] for t in self._tasks), default=0) + 1
