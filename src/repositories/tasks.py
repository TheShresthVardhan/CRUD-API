SEED_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]


class TaskRepository:
    """The only class that knows where tasks are stored."""

    def __init__(self):
        self._tasks = []
        self.reset()

    def find_all(self) -> list:
        return list(self._tasks)

    def find_by_id(self, task_id: int) -> dict | None:
        return next((t for t in self._tasks if t["id"] == task_id), None)

    def add(self, task: dict) -> None:
        self._tasks.append(task)

    def remove(self, task: dict) -> None:
        self._tasks.remove(task)

    def reset(self) -> None:
        self._tasks = [dict(t) for t in SEED_TASKS]

    def next_id(self) -> int:
        return max((t["id"] for t in self._tasks), default=0) + 1
