from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("app")

def install_exception_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP {exc.status_code} {request.method} {request.url.path}: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.info(f"422 {request.method} {request.url.path} validation: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.middleware("http")
    async def unhandled_exception_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"500 {request.method} {request.url.path}: {e}")
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
