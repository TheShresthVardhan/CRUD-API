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

    def _create_schema(self):
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY,"
            "title TEXT NOT NULL,"
            "done INTEGER NOT NULL DEFAULT 0,"
            "created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),"
            "updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')))"
        )
        cols = [row[1] for row in self._conn.execute("PRAGMA table_info(tasks)").fetchall()]
        if "created_at" not in cols:
            self._conn.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
        if "updated_at" not in cols:
            self._conn.execute("ALTER TABLE tasks ADD COLUMN updated_at TEXT")
        self._conn.execute("UPDATE tasks SET created_at = datetime('now', 'localtime') WHERE created_at IS NULL")
        self._conn.execute("UPDATE tasks SET updated_at = datetime('now', 'localtime') WHERE updated_at IS NULL")
        self._conn.commit()

    def _seed_if_empty(self):
        count = self._conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            self._conn.executemany(
                "INSERT INTO tasks (title, done, created_at, updated_at) "
                "VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))",
                [(t["title"], int(t["done"])) for t in SEED_TASKS],
            )
            self._conn.commit()

    def find_all(self, done: bool | None = None, search: str | None = None) -> list:
        query = "SELECT * FROM tasks"
        clauses = []
        params = []
        if done is not None:
            clauses.append("done = ?")
            params.append(int(done))
        if search:
            clauses.append("title LIKE ?")
            params.append(f"%{search}%")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY title"
        rows = self._conn.execute(query, params).fetchall()
        return [self._to_dict(r) for r in rows]

    def find_by_id(self, task_id: int) -> dict | None:
        row = self._conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_dict(row) if row else None

    @staticmethod
    def _to_dict(row) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def add(self, title: str) -> dict:
        cur = self._conn.execute(
            "INSERT INTO tasks (title, done, created_at, updated_at) "
            "VALUES (?, 0, datetime('now', 'localtime'), datetime('now', 'localtime'))",
            (title,),
        )
        self._conn.commit()
        return self.find_by_id(cur.lastrowid)

    def update(self, task_id: int, changes: dict) -> dict | None:
        sets = ["updated_at = datetime('now', 'localtime')"]
        params = []
        if "title" in changes:
            sets.append("title = ?")
            params.append(changes["title"])
        if "done" in changes:
            sets.append("done = ?")
            params.append(int(changes["done"]))
        self._conn.execute(
            f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?",
            (*params, task_id),
        )
        self._conn.commit()
        return self.find_by_id(task_id)

    def remove(self, task_id: int) -> None:
        self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()

    def reset(self) -> None:
        self._conn.execute("DELETE FROM tasks")
        self._conn.executemany(
            "INSERT INTO tasks (title, done, created_at, updated_at) "
            "VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))",
            [(t["title"], int(t["done"])) for t in SEED_TASKS],
        )
        self._conn.commit()

    def stats(self) -> dict:
        row = self._conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(done), 0) AS done, "
            "COALESCE(SUM(1 - done), 0) AS open FROM tasks"
        ).fetchone()
        return {"total": row["total"], "done": row["done"], "open": row["open"]}
