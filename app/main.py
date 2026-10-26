### Assemble the Application    --- Create app/main.py

### Connect the configuration, logging, middleware, exception handlers, employee routes, and health routes

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.employee_routes import router as employee_router
from app.health.health_routes import router as health_router

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging

from app.middleware.observability import ObservabilityMiddleware


setup_logging(settings.log_level)

logger = logging.getLogger(__name__) ###  is the standard, recommended pattern for creating a named logger instance specific to the Python module (file) where it is written

### Instead of typing names manually, this line leverages Python’s built-in namespace to automatically organize your application's logging structure.
### __name__: This is a special built-in variable in Python that evaluates to the dot-separated import path of the current module.


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Application startup",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
        },
    )

    yield

    logger.info(
        "Application shutdown",
        extra={
            "app_name": settings.app_name,
        },
    )


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


# Register exception handlers.
register_exception_handlers(app)


# Register application routers.
app.include_router(
    employee_router,
    prefix=settings.api_prefix,
)

app.include_router(
    health_router,
)


# Register observability middleware.
app.add_middleware(
    ObservabilityMiddleware,
)
### This tells FastAPI to wrap the application with our middleware.

## As a result, the middleware can process requests across all the registered HTTP routes, including health endpoints.

@app.get("/")
async def root():

    return {
        "application": settings.app_name,
        "environment": settings.app_env,
        "message": "Employee API is running",
    }


'''

What is lifespan?
------------------
The lifespan context manager manages application startup and shutdown operations.

For example, a production application might:
``````````````````````````````````````````
Initialize a database connection pool.
Load a machine-learning model.
Start an application-level resource.
Close connections during shutdown.

Our implementation logs startup and shutdown events.

Note: In a real database-backed application, initialize and dispose of the database engine appropriately. Also ensure that startup failures are surfaced so the deployment platform can recognize an unhealthy instance.


Why register middleware?
--------------------------
app.add_middleware(
    ObservabilityMiddleware,
)

This tells FastAPI to wrap the application with our middleware.

As a result, the middleware can process requests across all the registered HTTP routes, including health endpoints.


Important note about middleware ordering
------------------------------------------
Middleware ordering matters.

FastAPI and Starlette build a middleware stack, and exception-handling middleware sits at a particular point in that stack. A custom middleware that surrounds the entire application may observe an exception even when the client eventually receives a generated error response.

Our implementation is useful for learning the ASGI lifecycle, but a production implementation should test the actual behavior of the chosen middleware stack, especially for:

Unexpected exceptions.
Streaming responses.
Client disconnects.
Response headers already sent.
Duplicate exception logs.


Request and response flow in our application
=============================================
Client
  |
  v
Observability Middleware
  |
  +-- Correlation ID
  |
  +-- Start timer
  |
  +-- Log request
  |
  v
FastAPI Application
  |
  +-- Route matching
  |
  +-- Request validation
  |
  +-- Exception handling
  |
  +-- Employee service
  |
  v
ASGI Response
  |
  +-- HTTP status
  |
  +-- Response body
  |
  v
Observability Middleware
  |
  +-- Add correlation ID header
  |
  +-- Calculate duration
  |
  +-- Log completion
  |
  v
Client

'''



