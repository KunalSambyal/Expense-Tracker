from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError
import logging


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_messages = [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
    readable_message = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "code": 422,
            "message": readable_message,
            "data": None,
        }
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    error_str = str(exc.orig).lower()
    sqlstate = getattr(exc.orig, "sqlstate", None)

    # Distinguish specific violations
    if sqlstate == "23505" or "unique constraint" in error_str or "unique" in error_str:
        status_code = status.HTTP_409_CONFLICT
        message = "A record with the information already exists."
    elif sqlstate == "23503" or "foreign key" in error_str:
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Referenced resource does not exist or is currently in use."
    elif sqlstate == "23502" or "not null" in error_str:
        status_code = status.HTTP_400_BAD_REQUEST
        message = "A required database field is missing."
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Database integrity constraint violated."

    return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": status_code,
                "message": message,
                "data": None,
            }
        )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": 500,
                "message": "An unexpected internal error occurred. Please try again later.",
                "data": None,
            }
        )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)