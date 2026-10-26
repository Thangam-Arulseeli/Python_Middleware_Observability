import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)

### getattr() is a built-in Python function used to dynamically look up an object's attribute, and "unknown" acts as the fallback default value if that attribute does not exist.

def get_request_id(request: Request) -> str:

    return getattr(
        request.state,
        "correlation_id",
        "unknown",
    )
### getattr() --  Instead of accessing a property directly using dot notation (like request.state.correlation_id), getattr(object, attribute_name, default) allows you to safely look up an attribute using its string name. 

### "unknown"  -- This is the default value. If the request.state object does not have a property named "correlation_id", Python will not crash or throw an AttributeError. Instead, it will gracefully return the string "unknown"


def register_exception_handlers(
    app: FastAPI,
) -> None:

    @app.exception_handler(
        RequestValidationError
    )
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):

        correlation_id = get_request_id(request)

        logger.warning(
            "Request validation failed",
            extra={
                "correlation_id": correlation_id,
                "path": request.url.path,
                "error_count": len(exc.errors()),
            },
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": (
                        "The request contains invalid data."
                    ),
                    "correlation_id": correlation_id,
                }
            },
        )


    @app.exception_handler(
        StarletteHTTPException
    )
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):

        correlation_id = get_request_id(request)

        if exc.status_code >= 500:

            logger.error(
                "HTTP server error",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "status_code": exc.status_code,
                },
            )

        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "correlation_id": correlation_id,
                }
            },
        )


    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):

        correlation_id = get_request_id(request)

        logger.error(
            "Unexpected application exception",
            extra={
                "correlation_id": correlation_id,
                "path": request.url.path,
                "exception_type": type(exc).__name__,
            },
            exc_info=(
                type(exc),
                exc,
                exc.__traceback__,
            ),
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": (
                        "An unexpected error occurred."
                    ),
                    "correlation_id": correlation_id,
                }
            },
        )


'''
Explanation of the handlers
=============================
Handler 1 — Request validation errors
--------------------------------------
@app.exception_handler(RequestValidationError)

This handler catches FastAPI request-validation errors.

Examples include:
-------------------
Missing required fields.
Incorrect data types.
Values outside the allowed range.
Invalid path parameters.

The example returns a standardized HTTP 422 response.

It deliberately does not include the complete Pydantic error details. Those details may contain submitted input values, which should be handled carefully in applications processing sensitive data.


Handler 2 — HTTP exceptions
----------------------------
@app.exception_handler(StarletteHTTPException)

This handles HTTP exceptions such as:
-----------------------------------
404 Not Found.
401 Unauthorized.
403 Forbidden.
409 Conflict.

For example:

raise HTTPException(
    status_code=404,
    detail="Employee not found",
)

The client receives a consistent error structure.


Handler 3 — Unexpected exceptions
-----------------------------------
@app.exception_handler(Exception)

This is the catch-all handler for unexpected application exceptions that reach FastAPI's registered handler.

It logs the exception and returns a generic HTTP 500 response.

Important: Do not assume that every exception is converted by this handler. Failures can occur before the application, during middleware execution, or after response headers have already been sent. Exception-handling boundaries depend on the ASGI middleware stack.

Also, the observability middleware logs and re-raises unexpected exceptions. Depending on middleware ordering, a server-side exception may therefore appear in more than one log entry. This is not necessarily a problem, but production logging should avoid confusing duplicate alerts.

'''


