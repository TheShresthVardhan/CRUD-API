from src.repositories.tasks import TaskRepository
from src.services.tasks import TaskService

_repo = TaskRepository()
_service = TaskService(_repo)


def get_service() -> TaskService:
    return _service
