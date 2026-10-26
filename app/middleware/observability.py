import logging
import time
import uuid

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Correlation-ID"

MAX_CORRELATION_ID_LENGTH = 128


def get_correlation_id(scope: Scope) -> str:

    headers = Headers(scope=scope)
    supplied_id = headers.get(REQUEST_ID_HEADER)

    if supplied_id:

        supplied_id = supplied_id.strip()

        # Accept only a bounded, simple identifier.
        # This avoids newlines and other control characters.
        if (
            1 <= len(supplied_id) <= MAX_CORRELATION_ID_LENGTH
            and all(
                character.isalnum()
                or character in "-_.:"
                for character in supplied_id
            )
        ):
            return supplied_id

    return str(uuid.uuid4())



class ObservabilityMiddleware:

    def __init__(self, app: ASGIApp) -> None:

        self.app = app

### The __call__ method turns an instance of a class into a callable object (making the instance behave like a function).
    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:

        if scope["type"] != "http":

            await self.app(
                scope,
                receive,
                send,
            )

            return

        correlation_id = get_correlation_id(scope)

        scope.setdefault("state", {})[
            "correlation_id"
        ] = correlation_id

        method = scope.get("method", "")
        path = scope.get("path", "")

        start_time = time.perf_counter()

        status_code = 500  # Internal Server Error
        response_started = False

        logger.info(
            "HTTP request started",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
            },
        )


        async def send_wrapper(message: Message) -> None:

            nonlocal status_code
            nonlocal response_started

            if message["type"] == "http.response.start":

                response_started = True

                status_code = message["status"]

                response_headers = list(
                    message.get("headers", [])
                )

                response_headers.append(
                    (
                        REQUEST_ID_HEADER.lower().encode("ascii"),
                        correlation_id.encode("ascii"),
                    )
                )

                message = {
                    **message,
                    "headers": response_headers,
                }

            await send(message)

        try:

            await self.app(
                scope,
                receive,
                send_wrapper,
            )

        except Exception:

            logger.exception(
                "Unhandled exception during HTTP request",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "response_started": response_started,
                },
            )

            raise

        finally:

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.info(
                "HTTP request completed",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(
                        duration_ms,
                        2,
                    ),
                },
            )

#### =============================================================

'''
Starlette
=============
Starlette is a lightweight, high-performance, asynchronous ASGI (Asynchronous Server Gateway Interface) framework and toolkit for building Python web services.

Key Features
----------------
• Asynchronous Core: Built for asyncio and trio/anyio backends.
• HTTP & WebSockets: Native support for standard requests, responses, and real-time bidirectional communication.
• Routing & Lifespan: Clean functional and class-based routing with startup/shutdown event handlers.
• Built-in Middleware: Out-of-the-box support for CORS, GZip, sessions, cookies, and trusted hosts via Starlette Documentation.
• Test Client: Built-in testing support powered by httpx.

Relation to FastAPI
--------------------
Starlette serves as the foundational HTTP and routing engine for FastAPI, which layers Pydantic-based data validation and automatic OpenAPI documentation on top. You can use Starlette directly when you want minimal overhead without FastAPI's built-in validation.

from starlette.datastructures import Headers
--------------------------------------------
The line from starlette.datastructures import Headers is a Python import statement used to fetch the Headers data structure class from the Starlette web framework. Starlette is the lightweight ASGI toolkit that powers popular frameworks like FastAPI.

Implement Observability Middleware
=========================================
This is the central part of the development.

We will implement:
------------------
Correlation ID generation.
Request timing.
Request logging.
Response logging.
Correlation ID response headers.
Exception logging.


What is a correlation ID?
============================
A correlation ID is an identifier associated with a request.

Suppose a client sends:

GET /api/employees/101

The middleware generates:

b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2

The same ID can be included in logs produced by different components while processing that request.

Example:

{
  "message": "HTTP request started",
  "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2"
}


Another log from the same request:
{
  "message": "Employee retrieved",
  "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2",
  "employee_id": 101
}

A third log:
{
  "message": "HTTP request completed",
  "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2",
  "status_code": 200,
  "duration_ms": 12.4
}

Now a developer can search for one ID and see the events associated with that request.


Correlation ID versus trace ID
==============================
These concepts are related but not identical.

A correlation ID is commonly used to associate related log events.
A trace ID identifies a distributed trace in a tracing system.
A span ID identifies an individual operation within a trace.

A correlation ID does not automatically provide distributed tracing. For tracing across services, use a standard such as W3C Trace Context and an instrumentation system such as OpenTelemetry.


Why use UUID?
---------------
Python provides the uuid module.

import uuid

request_id = str(uuid.uuid4())
print(request_id)

Example output:

b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2

UUID4 is appropriate for generating request identifiers without maintaining a centralized counter.

'''

##### ========================================
'''
from starlette.types import ASGIApp, Message, Receive, Scope, Send
---------------------------------------------------------------------
In the ASGI (Asynchronous Server Gateway Interface) protocol used by Starlette and FastAPI, an application is an async callable that takes three parameters: scope, receive, and send.

The line from starlette.types import ASGIApp, Message, Receive, Scope, Send imports type annotations for building Asynchronous Server Gateway Interface (ASGI) applications in Python.

Scope (Scope)
----------------
• What it is: A dictionary (dict) that contains information about a single incoming connection or event (such as an HTTP request, a WebSocket connection, or a server lifespan event).
• What it contains:
	• For HTTP requests: The protocol type ("http"), HTTP method ("GET", "POST", etc.), path, headers, query string, and client/server details.
	• For WebSockets: The protocol type ("websocket"), subprotocols, and headers.
	• For Lifespan events: Startup and shutdown signals ("lifespan").

Send (Send)
-------------
• What it is: An asynchronous callable (coroutine function) that the application uses to send event messages back to the client or server (e.g., sending HTTP response headers or response body chunks).
• How it works: You await it with a dictionary message, such as await send({"type": "http.response.start", "status": 200, ...}) or await send({"type": "http.response.body", "body": b"Hello world"}).


How they work together (scope, receive, send)
---------------------------------------------
python
async def app(scope, receive, send):
  if scope["type"] == "http":
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/plain"]],
    })
    await send(
        {"type": "http.response.body", "body": b"Hello, ASGI!"}
    )  #

    
Definitions
----------
• ASGIApp
A type alias for a callable that represents an ASGI application. It is an asynchronous function or object with the signature (Scope, Receive, Send) -> Awaitable[None].
• Message
A dict containing data passed through the ASGI channel. For HTTP requests or responses, a message represents events like http.request, http.response.start, or http.response.body.
• Receive
An asynchronous callable (coroutine) used to receive incoming events from the client or server (such as reading chunks of an HTTP request body). Calling await receive() returns the next Message
    '''



##### ========================================

'''
Understand the important parts
==============================
Part A — ASGI middleware
-------------------------
class ObservabilityMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

FastAPI is built on Starlette and follows the ASGI specification.

ASGI middleware wraps an application and intercepts its request and response processing.
The wrapped application is stored in self.app.


Part B — Ignore non-HTTP traffic
-------------------------------
if scope["type"] != "http":

    await self.app(scope, receive, send)

    return
    
ASGI can handle more than HTTP requests, including WebSocket connections.
This middleware is intended for HTTP requests. Non-HTTP traffic passes directly to the wrapped application.


Part C — Read or generate the correlation ID
--------------------------------------------
correlation_id = get_correlation_id(scope)

The middleware checks whether the incoming request contains an X-Correlation-ID header.
If the value meets the validation rules, it is reused. Otherwise, a new UUID is generated.

Security consideration: Client-provided correlation IDs are untrusted input. The example restricts their length and characters. A stricter deployment may always generate its own ID or retain the client's ID separately from an internally generated request ID.


Part D — Store the ID in request state
--------------------------------------
scope.setdefault("state", {})[
    "correlation_id"
] = correlation_id

This makes the ID available through FastAPI's request object.

For example:
    request.state.correlation_id

An endpoint or service can retrieve the ID without parsing the headers again.


Part E — Start the timer
------------------------
start_time = time.perf_counter()
time.perf_counter() is designed for measuring elapsed time.

It is more appropriate for request-duration measurements than using the wall-clock time.


Part F — Intercept the response
--------------------------------
if message["type"] == "http.response.start":

    status_code = message["status"]

ASGI represents the start of an HTTP response as an http.response.start message.
This allows the middleware to capture the HTTP status code.


Part G — Add the correlation ID to the response
-----------------------------------------------
response_headers.append(
    (
        b"x-correlation-id",
        correlation_id.encode("ascii"),
    )
)

The response now contains a header similar to:

X-Correlation-ID: b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2

This is useful when a client reports an error.
The support team can request the correlation ID and search the logs.


Part H — Log unhandled exceptions
----------------------------------
except Exception:

    logger.exception(
        "Unhandled exception during HTTP request",
        extra={
            "correlation_id": correlation_id,
            "method": method,
            "path": path,
        },
    )

    raise

logger.exception() logs the message along with exception information when called inside an exception handler.

The raise statement propagates the exception to the surrounding application or server error-handling layer.

This is important because middleware should not silently swallow unexpected exceptions.


Part I — Calculate request duration
-------------------------------------
duration_ms = (
    time.perf_counter() - start_time
) * 1000

Suppose the elapsed time is 0.025 seconds.

Then:

0.025 × 1000 = 25 milliseconds

The resulting log might contain:

{
  "message": "HTTP request completed",
  "status_code": 200,
  "duration_ms": 25.0
}


Production consideration: timing scope
======================================
This implementation measures elapsed time until the wrapped ASGI application finishes sending its response.

It includes endpoint processing and response transmission through the ASGI send path, but it is not necessarily a measurement of when the remote client receives the complete response.

For streaming responses, the duration may include the streaming period. That is often useful, but it should be understood when interpreting latency metrics.

'''

