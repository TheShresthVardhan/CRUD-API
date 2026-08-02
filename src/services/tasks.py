from src.errors import NotFoundError, ValidationError
from src.repositories.tasks import TaskRepository


class TaskService:
    """Business rules: validation, id rules, not-found logic. No HTTP, no storage."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def _get(self, task_id: int) -> dict:
        task = self.repo.find_by_id(task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(self, done: bool | None = None, search: str | None = None) -> list:
        return self.repo.find_all(done=done, search=search)

    def get_task(self, task_id: int) -> dict:
        return self._get(task_id)

    def create_task(self, title: str | None) -> dict:
        if title is None or not title.strip():
            raise ValidationError("title is required and cannot be empty")
        return self.repo.add(title.strip())

    def update_task(self, task_id: int, changes: dict) -> dict:
        if self.repo.find_by_id(task_id) is None:
            raise NotFoundError(f"Task {task_id} not found")
        if not changes:
            raise ValidationError("request body must include title and/or done")
        if "title" in changes and (changes["title"] is None or not changes["title"].strip()):
            raise ValidationError("title is required and cannot be empty")
        if "done" in changes and changes["done"] is None:
            raise ValidationError("done must be true or false")
        return self.repo.update(task_id, changes)

    def delete_task(self, task_id: int) -> None:
        if self.repo.find_by_id(task_id) is None:
            raise NotFoundError(f"Task {task_id} not found")
        self.repo.remove(task_id)

    def stats(self) -> dict:
        return self.repo.stats()

    def reset(self) -> list:
        self.repo.reset()
        return self.repo.find_all()
