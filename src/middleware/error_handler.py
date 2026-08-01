from fastapi import Request
from fastapi.responses import JSONResponse

from src.errors import NotFoundError, ValidationError


def register_error_handlers(app):
    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(NotFoundError)
    async def handle_not_found_error(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})
