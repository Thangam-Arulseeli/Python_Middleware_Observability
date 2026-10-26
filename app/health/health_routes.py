import logging

from fastapi import APIRouter, HTTPException

from app.core.config import settings


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/live")
async def liveness_check():

    return {
        "status": "alive",
    }


@router.get("/ready")
async def readiness_check():

    try:

        if not settings.app_name:

            raise RuntimeError(
                "Application name is missing"
            )

        return {
            "status": "ready",
            "checks": {
                "application": "ok",
            },
        }

    except Exception:

        logger.exception(
            "Readiness check failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Application is not ready",
        )


'''
What does HTTP 503 mean?
-------------------------
503 Service Unavailable indicates that the service is temporarily unable to handle the request.

For example, if the database is required for all business operations and is unavailable, the application may not be ready to serve traffic.


Why separate liveness and readiness?
------------------------------------
Suppose PostgreSQL is temporarily unavailable.

The application process may still be healthy, but it cannot serve database-dependent requests.

In that case:

/health/live  -> 200 OK

/health/ready -> 503 Service Unavailable

This distinction helps orchestration systems decide whether to restart a process or temporarily remove it from service.

Important: Our current readiness implementation does not test an external dependency. It verifies only a basic application condition, so it is not yet a meaningful database-readiness check.

'''

