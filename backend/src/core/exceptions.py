from fastapi.responses import JSONResponse
from fastapi import status

class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "app_error"
    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        if code:
            self.code = code
        self.message = message

class DuplicateEmailError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "duplicate_email"

class FileTypeNotAllowed(AppError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    code = "file_type_not_allowed"

class ImportParseError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "import_parse_error"

def install_domain_exception_handlers(app):
    @app.exception_handler(AppError)
    async def app_error_handler(request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )
