Python Middleware and Observability in FastAPI
***********************************************

This module covers how to implement middleware, request timing, correlation IDs, structured logging, global exception handling, health and readiness APIs, and environment-based configuration in a real-world Python FastAPI application.

Training objective:
===================
 By the end of this module, trainees should be able to implement cross-cutting concerns in a FastAPI application so that requests can be tracked, failures can be diagnosed, response times can be measured, and application health can be monitored


Project Requirements
=====================
We will create an Employee Management API with these capabilities.

Feature	            Endpoint or component   Purpose
List employees	    GET /api/employees	    Return employee records
Get employee	    GET /api/employees/{id}	Retrieve one employee
Create employee	    POST /api/employees	    Add an employee
Request timing	    Middleware	            Measure request duration
Correlation ID	    Middleware	            Identify individual requests
Structured logging	Logging configuration	Produce machine-readable logs
Global exception 	Exception handlers	    Return consistent error responses
Liveness check	    GET /health/live	    Determine whether the 
                                            application is running
Readiness check	    GET /health/ready	    Determine whether the 
                                            application can serve traffic
Configuration	    Environment variables	Separate configuration from 
                                            source code

For this training implementation, employee records will be stored in memory to keep the example focused on middleware and observability.

Production note: In-memory storage is not persistent, is not shared between workers, and is not appropriate for production employee data. A real application should use a database such as PostgreSQL through the repository and service layers.

Our health and readiness checks will be designed so that a database readiness check can be added later.


Create the Project Folder Structure
========================================
Create a project named Python_Middleware_Observability

Use the following folder structure.

fastapi_observability/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── employee_routes.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── exceptions.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── observability.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── employee_schema.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── employee_service.py
│   │
│   └── health/
│       ├── __init__.py
│       └── health_routes.py
│
├── tests/
│   ├── __init__.py
│   ├── test_employees.py
│   ├── test_health.py
│   └── test_observability.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Why separate the application into folders?
===========================================
Folder	        Responsibility
-------------------------------------------
api/	        HTTP routes and endpoint definitions
core/	        Configuration, logging, and exception handling
middleware/	    Request and response processing
schemas/	    Pydantic request and response models
services/	    Business logic
health/	        Health and readiness endpoints
tests/	        Automated tests

This structure separates responsibilities and makes the application easier to maintain.

For example, changing the logging format should not require modifying employee business logic.


Install the Required Packages
==============================
Create requirements.txt
````````````````````````
fastapi
uvicorn[standard]
pydantic-settings
python-dotenv
pytest
httpx


The code in this module uses Python's built-in logging, time, and uuid modules. We do not need a separate package for them.


Create and activate a virtual environment on Windows:
=====================================================
    > python -m venv .venv

Activate it:
    > .\.venv\Scripts\Activate.ps1

If PowerShell blocks script execution, you can use Command Prompt instead:
    > .venv\Scripts\activate.bat

Install the packages:
    > python -m pip install -r requirements.txt

Check the FastAPI installation:
    > python -m pip show fastapi

Production recommendation: Pin and regularly update dependency versions using a tested dependency-management workflow. The unpinned requirements above are suitable as a starting point for development, not as a complete production dependency policy.


Configure Environment Variables
=================================
What is environment-based configuration?
````````````````````````````````````````
Applications need settings such as:

Application name.
Application environment.
Debug mode.
Log level.
API prefix.
Database connection string.
External service URLs.


We should avoid hardcoding environment-specific settings throughout the application.

For example, this is not ideal:

DEBUG = True
LOG_LEVEL = "DEBUG"
DATABASE_URL = "postgresql://user:password@localhost:5432/employees"

It makes it easy to accidentally use development settings in production or expose credentials.

Instead, store configuration outside the source code.


Create .env file
===================
APP_NAME=Employee Management API
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
API_PREFIX=/api
HOST=127.0.0.1
PORT=8000

These are development settings.

Do not put real production passwords, tokens, or other secrets in a committed .env file.

Create .env.example
=====================
APP_NAME=Employee Management API
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
API_PREFIX=/api
HOST=127.0.0.1
PORT=8000

The .env.example file documents the settings required to run the application.

Team members can copy it to create their own .env file.


Files
=======
1. Create app/core/config.py

2. Create app/core/logging_config.py
We will use Python's built-in logging system and a JSON formatter.


3. Create app/middleware/observability.py

Implement Observability Middleware
===================================
Implement Observability Middleware

This is the central part of the application development.

We will implement:

Correlation ID generation.
Request timing.
Request logging.
Response logging.
Correlation ID response headers.
Exception logging.


What is a correlation ID?
----------------------------
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
---------------------------------
These concepts are related but not identical.

A correlation ID is commonly used to associate related log events.
A trace ID identifies a distributed trace in a tracing system.
A span ID identifies an individual operation within a trace.

A correlation ID does not automatically provide distributed tracing. For tracing across services, use a standard such as W3C Trace Context and an instrumentation system such as OpenTelemetry.


Why use UUID?
-----------------
Python provides the uuid module.

import uuid

request_id = str(uuid.uuid4())

print(request_id)

Example output:

b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2

UUID4 is appropriate for generating request identifiers without maintaining a centralized counter.
======================================================

4. Configure the Pydantic Schemas
Create app/schemas/employee_schema.py

5. Create the Employee Service
Create app/services/employee_service.py

======================================================


Implement Global Exception Handling
====================================
Why do we need global exception handling?
-----------------------------------------
Consider an endpoint that raises an exception:

raise RuntimeError("Unexpected failure")
If every route handles exceptions differently, clients may receive inconsistent error responses.

For example:

{
  "error": "Something went wrong"
}

Another endpoint might return:

{
  "detail": "Unexpected failure"
}

A third endpoint might expose an internal error message.
A centralized exception-handling strategy helps standardize the response format.


Define a standard error response
--------------------------------
We will use this format:

{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred.",
    "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2"
  }
}

The client receives a safe message, while the server logs retain diagnostic details.

======================================================================


6. Create app/core/exceptions.py

7. Create Employee API Routes  -- Create app/api/employee_routes.py

======================================================================


Implement Health and Readiness APIs
-------------------------------------
These endpoints are important for deployment platforms, container orchestration, and monitoring systems.

What is a health endpoint?
-----------------------------
A health endpoint tells an external system whether the application is running or able to perform its intended function.

There are two common checks.


Liveness
----------
A liveness check answers:

Is the application process alive and able to respond?

Endpoint:

GET /health/live

Example response:

{
  "status": "alive"
}

A liveness endpoint should generally be lightweight. It should not fail simply because a downstream service is temporarily unavailable.



Readiness
-----------
A readiness check answers:

Is this application instance ready to receive traffic?

Endpoint:

GET /health/ready

For an application that requires a database, readiness may depend on whether the database can be reached.

Example response when ready:

{
  "status": "ready",
  "checks": {
    "application": "ok"
  }
}

This initial example checks only application configuration and process availability. We will explain how to extend it for PostgreSQL.

==========================================================================


8. Create app/health/health_routes.py

9. Assemble the Application [Create app/main.py]

Connect the configuration, logging, middleware, exception handlers, employee routes, and health routes.


10. Configure .gitignore    [Create .gitignore]

**************************************************************************

Run the Application
+++++++++++++++++++++++

From the project root, run:

    > python -m uvicorn app.main:app --reload

Expected output will indicate that Uvicorn is running on the local server.

Open Swagger UI in your browser:

Swagger UI: http://127.0.0.1:8000/docs

The OpenAPI schema is also available at:

http://127.0.0.1:8000/openapi.json

The root endpoint is:

http://127.0.0.1:8000/

The health endpoints are:

http://127.0.0.1:8000/health/live

http://127.0.0.1:8000/health/ready

The employee endpoints are:

http://127.0.0.1:8000/api/employees

http://127.0.0.1:8000/api/employees/1

The --reload option is appropriate for development. For production, use a deployment configuration appropriate for the hosting platform, with controlled process management and logging.

**********************************************************************

Test the API in Swagger UI
++++++++++++++++++++++++++++++

Open:

http://127.0.0.1:8000/docs

Test 1: Check application status
-----------------------------------
Execute:

GET /

Expected response:

{
  "application": "Employee Management API",
  "environment": "development",
  "message": "Employee API is running"
}


Test 2: Liveness
------------------
Execute:

GET /health/live

Expected status:

200 OK

Expected response:

{
  "status": "alive"
}


Test 3: Readiness
--------------------
Execute:

GET /health/ready

Expected status:

200 OK

Expected response:

{
  "status": "ready",
  "checks": {
    "application": "ok"
  }
}


Test 4: Create an employee
----------------------------
Execute:

POST /api/employees

Request body:

{
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering",
  "salary": 55000
}

Expected status:

201 Created

Expected response:

{
  "id": 1,
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering",
  "salary": 55000
}



Test 5: Retrieve the employee
--------------------------------
Execute:

GET /api/employees/1

Expected status:

200 OK

Expected response:

{
  "id": 1,
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering",
  "salary": 55000
}

Remember that the in-memory employee store is reset when the application restarts.



Test 6: Test a missing employee
--------------------------------
Execute:

GET /api/employees/999

Expected status:

404 Not Found

Expected error format:

{
  "error": {
    "code": "HTTP_404",
    "message": "Employee not found",
    "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2"
  }
}

The correlation ID will be generated dynamically, so your actual value will differ.



Test 7: Test request validation
--------------------------------
Execute:

POST /api/employees

Request body:

{
  "name": "A",
  "email": "arun@example.com",
  "department": "Engineering",
  "salary": -5000
}

Expected status:

422 Unprocessable Entity

Expected response:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data.",
    "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2"
  }
}


Test 8: Test an unexpected exception
-------------------------------------
Execute:

GET /api/employees/debug/error

Expected client status:

500 Internal Server Error

Expected error body:

{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred.",
    "correlation_id": "b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2"
  }
}

Inspect the application terminal to see the diagnostic logs.

**********************************************************************

Verify Correlation IDs
++++++++++++++++++++++++++

Swagger UI displays response headers in its response section.

After executing an endpoint, inspect the response headers for:

X-Correlation-ID: b82f6e7d-4e0c-4c85-8a3a-0bc8b4380fd2

You can also use PowerShell.

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/health/live" `
    -Method GET

Inspect the returned headers.

Or use Python:

import requests

response = requests.get(
    "http://127.0.0.1:8000/health/live"
)

print(response.status_code)

print(
    response.headers.get("X-Correlation-ID")
)

print(response.json())

This Python example requires the requests package, which is separate from the dependencies listed in requirements.txt.


Send your own correlation ID
-----------------------------------

Use a PowerShell request:

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/health/live" `
    -Headers @{
        "X-Correlation-ID" = "training-request-001"
    }

The response should contain:

X-Correlation-ID: training-request-001

The middleware also uses this ID in its logs.

Try sending an excessively long or invalid ID. The middleware should generate a new UUID instead.

Production note: When requests arrive through a reverse proxy or API gateway, decide whether to trust a client-supplied correlation ID. If the identifier is used for security auditing or internal request identity, generating a separate server-controlled request ID is safer.

***********************************************************

Understand the Structured Logs
++++++++++++++++++++++++++++++++++

When you create an employee, the terminal should show records resembling these.

Request started
{
  "timestamp": "2026-10-24T08:30:00+00:00",
  "level": "INFO",
  "logger": "app.middleware.observability",
  "message": "HTTP request started",
  "correlation_id": "training-request-001",
  "method": "POST",
  "path": "/api/employees"
}


Business operation completed
{
  "timestamp": "2026-10-24T08:30:00.015+00:00",
  "level": "INFO",
  "logger": "app.services.employee_service",
  "message": "Employee created",
  "employee_id": 1,
  "correlation_id": "training-request-001"
}

Request completed
{
  "timestamp": "2026-10-24T08:30:00.020+00:00",
  "level": "INFO",
  "logger": "app.middleware.observability",
  "message": "HTTP request completed",
  "correlation_id": "training-request-001",
  "method": "POST",
  "path": "/api/employees",
  "status_code": 201,
  "duration_ms": 20.13
}

These are illustrative records showing the expected structure, not actual execution results.


What can we learn from them?
------------------------------
The records tell us:

Which request was processed.
Which HTTP method was used.
Which endpoint was accessed.
Which employee was created.
Whether the request succeeded.
How long the request took.

All three records share the same correlation ID.

That is the main benefit of combining structured logging with correlation IDs.

****************************************************************


Write Automated Tests
+++++++++++++++++++++++

A corporate training module should not stop at manual testing. Trainees should verify that the middleware and exception handlers behave as expected.

We will use pytest and FastAPI's TestClient.

1. Create tests/test_employees.py

2. Create tests/test_health.py

3. Create tests/test_observability.py

4. Run the tests

From the project root:
    > python -m pytest -v

The tests should verify the principal behaviors.

Testing considerations
-----------------------
These tests use the same application instance and in-memory employee store. For more robust automated testing, isolate application state with fixtures and create a fresh application or service instance for each test where appropriate.

For database-backed applications, use a separate test database and controlled dependency overrides.

Also, if you add tests for unexpected exceptions, account for how TestClient propagates server exceptions. By default, TestClient can re-raise application exceptions to the test instead of simply returning the generated 500 response. For a test specifically verifying the error response, you can construct the client with:

client = TestClient(
    app,
    raise_server_exceptions=False,
)

This is useful when testing the final HTTP response produced by the application's error-handling layer.

=============================================================
*************************************************************
=============================================================

Add a Production-Style Database Readiness Check
=================================================

The current readiness endpoint checks only basic application state. Let's examine how to extend it when the application uses PostgreSQL.

A database-backed API should generally verify that the database can accept a simple query before reporting itself ready.

For a synchronous SQLAlchemy engine, the check can use a short-lived connection and execute SELECT 1.

Conceptually:

def check_database(engine) -> bool:

    with engine.connect() as connection:

        connection.exec_driver_sql("SELECT 1")

    return True

This example assumes engine is a configured SQLAlchemy engine.

The readiness endpoint can then return:

{
  "status": "ready",
  "checks": {
    "database": "ok"
  }
}

If the database check fails, it should return HTTP 503.



1. Production considerations
````````````````````````````````
A database readiness check should:

Use a short timeout.
Avoid expensive queries.
Avoid exposing credentials or connection details.
Distinguish application health from dependency health.
Avoid overwhelming the database with frequent probes.
Use the same essential connectivity path as the application.

Do not create a new database engine for every readiness request. Reuse the application's configured engine and connection pool.

If the application uses asynchronous SQLAlchemy, use the corresponding asynchronous connection API rather than blocking the event loop with synchronous operations.

Liveness and readiness in deployment
Situation	Liveness	Readiness
Application is running and database is available	Healthy	Ready
Application is running but database is unavailable	Usually healthy	Not ready
Application process is dead	Failed	Failed
Required configuration is missing during startup	Startup should fail	Not ready

A readiness endpoint should reflect the dependencies required to serve traffic, rather than merely checking that the Python process exists.
=====================================================================
*********************************************************************


Production Logging Improvements
*********************************

The training implementation provides JSON logging, but production systems need additional controls.

1. Include consistent request fields
======================================

A production request log should ideally contain fields such as:

{
  "timestamp": "2026-10-24T08:30:00+00:00",
  "level": "INFO",
  "service": "employee-api",
  "environment": "production",
  "correlation_id": "training-request-001",
  "method": "GET",
  "path": "/api/employees/101",
  "status_code": 200,
  "duration_ms": 18.24
}

The service and environment fields can be added to the logging formatter or injected by the logging infrastructure.

2. Avoid logging sensitive information
==========================================
Do not log:

Passwords.
Authentication tokens.
API keys.
Session cookies.
Full authorization headers.
Sensitive personal data.
Complete request bodies by default.

A log record can become a security incident if it exposes confidential information.


3. Avoid high-cardinality metric labels
==========================================

If you later add metrics, do not use unique request IDs or user IDs as metric labels.

For example, this is a poor metric design:

http_requests_total{correlation_id="unique-value"}

Each request creates a new label value, potentially producing an enormous number of time series.

Instead, use bounded dimensions such as:

method="GET"
route="/api/employees/{employee_id}"
status_code="200"

Use correlation IDs in logs and traces, not as unbounded metric dimensions.


4. Use standard metrics and tracing when required
=========================================================
For production deployments, consider:

Prometheus-compatible metrics for numerical measurements.
OpenTelemetry for instrumentation and distributed tracing.
A centralized log platform for searching structured logs.
Alerting for elevated error rates and latency.
Dashboards for request throughput, errors, and response-time percentiles.

The exact products and architecture depend on the deployment environment.
======================================================================
**********************************************************************

Add Request Timing Metrics
============================

Logging each request's duration is useful, but a production team may also want aggregate measurements.

For example:

GET /api/employees
Average duration: 20 ms

POST /api/employees
Average duration: 35 ms

GET /api/employees/{employee_id}
Average duration: 12 ms

A metrics system can calculate these values over time.

The following is a conceptual example, not an implementation of a metrics endpoint:

request_count = 0
total_duration_ms = 0.0

def record_request(duration_ms: float):
    global request_count
    global total_duration_ms
    request_count += 1
    total_duration_ms += duration_ms



def average_duration() -> float:
    if request_count == 0:
        return 0.0
    return total_duration_ms / request_count


This demonstrates the arithmetic, but do not use this global-variable implementation in production.


It has several limitations:
===============================
Shared state is not automatically synchronized.
Each worker maintains separate values.
Restarting the application resets the counters.
There are no latency histograms or percentiles.
It does not provide a standard metrics exposition format.

For a production metrics implementation, use a supported metrics library or OpenTelemetry instrumentation.
======================================================================
***********************************************************************


Common Problems and Troubleshooting
**************************************

Problem 1: ModuleNotFoundError: No module named 'app'
=========================================================

Cause: The application is being launched from the wrong working directory or the Python import path is incorrect.

Solution: Open the terminal in the project root.

The directory should contain:

app/
requirements.txt
tests/

Then run:

python -m uvicorn app.main:app --reload


Problem 2: uvicorn is not recognized
========================================
Cause: The virtual environment may not be activated, or Uvicorn may not be installed in the Python environment being used.

Solution:

python -m pip install -r requirements.txt

Then:

python -m uvicorn app.main:app --reload

Using python -m uvicorn helps ensure that Uvicorn runs through the selected Python interpreter.


Problem 3: Environment variables are not loading
====================================================
Cause: The .env file may be missing, misspelled, or located outside the expected working directory.

Check:

Python_Middleware_Observability/
├── .env
├── app/
└── requirements.txt

Also verify that the variable names match the aliases in config.py.

For example:

LOG_LEVEL=DEBUG


Problem 4: The response does not contain X-Correlation-ID
===========================================================
Cause: The middleware might not be registered, or another component might modify response headers.

Verify that app.add_middleware() is executed during application creation.

Then restart the application and inspect the actual HTTP response headers.



Problem 5: The request returns HTTP 500
=========================================
Check the terminal for:

The correlation ID.
The exception type.
The stack trace.
The endpoint being called.

Search for the same correlation ID across the request logs.

Do not return internal stack traces or raw exception messages to production clients.


Problem 6: /health/ready returns HTTP 200 even when PostgreSQL is unavailable
===============================================================================
This is expected in the current training implementation because the readiness endpoint does not connect to PostgreSQL.

Add an actual database check before using this endpoint as a production traffic-readiness signal.


Problem 7: Logs appear twice
==============================
Possible causes include:

Multiple logging handlers.
Logger propagation.
Server logging configuration.
Exceptions being logged at multiple middleware boundaries.

Review the logging configuration and decide which layer should own each event.

Avoid disabling all propagation blindly; Uvicorn and application loggers may have different requirements.
********************************************************************
====================================================================


Additional Corporate Training Exercises
*****************************************

After trainees complete the main application, assign these exercises.

Exercise 1: Correlation ID
=============================
Modify the middleware so that it always generates an internal request ID, even if the client supplies a correlation ID.

Return both identifiers in separate, clearly documented headers.

Discuss when the two IDs should differ.


Exercise 2: Request duration
==============================
Add a warning log when a request takes more than 500 milliseconds.

Expected behavior:

Duration < 500 ms  -> INFO

Duration >= 500 ms -> WARNING

Use the same correlation ID in both the warning and completion log.


Exercise 3: Custom exception
==============================
Create an EmployeeNotFoundError exception in the service layer.

Register a dedicated exception handler that maps it to HTTP 404.

This separates business-level errors from HTTP route implementation.


Exercise 4: Database readiness
===============================
Replace the simulated readiness check with a real SQLAlchemy connection check.

Return HTTP 503 if the required database is unavailable.

Ensure that the database connection is closed or returned to the pool correctly.


Exercise 5: Structured error logging
=====================================
Add the following fields to appropriate error logs:

correlation_id
method
path
status_code
exception_type

Do not log authentication credentials or request secrets.


Exercise 6: Unit and integration tests
========================================
Write tests that verify:

A valid correlation ID is reused.
An invalid correlation ID is replaced.
Unexpected errors return the correct response structure.
Readiness returns 503 when the required dependency is unavailable.
The request timing log contains a nonnegative duration.


Exercise 7: Production configuration
=====================================
Modify the application so that it refuses to start if production configuration is invalid.

For example:

An invalid logging level should fail startup.
A missing required production database URL should fail startup.
Debug mode should not be enabled in production.

These are examples of configuration checks that should be enforced at startup rather than discovered during a live request.

*************************************************************************


Recommended Production Improvements
**************************************

The code above provides a structured starting point. Before using the same design in a production deployment, address the following areas.

Area	    Training implementation	         Production improvement
=======================================================================
Middleware	Custom ASGI middleware	        Test all exception and streaming behaviors
Correlation IDs	UUID or validated client value	Define trust policy and request-ID propagation
Logging	    Built-in JSON formatter	        Centralized logging, redaction, retention, alerting
Timing	    Per-request duration logs	    Metrics histograms and latency percentiles
Exceptions	Global exception handlers	    Standard error contract and safe error reporting
Health	    Liveness and basic readiness	Dependency-aware readiness
Configuration	.env and Pydantic Settings	Managed environment configuration and secrets
Data storage  In-memory dictionary	        Persistent database and repository layer
Testing	    Basic endpoint tests	        Isolated test fixtures and integration tests
Tracing	    Correlation IDs only	        OpenTelemetry and distributed trace propagation


Recommended implementation priorities
=======================================
For a real Employee Management API, I would implement the improvements in this order:

Configuration validation:   Validate mandatory settings at startup.
Structured logs:        Emit consistent JSON records.
Request identification: Use a clear correlation/request ID policy.
Request timing:         Record duration for every completed HTTP request.
Exception handling:     Standardize errors and avoid leaking internals.
Health checks:          Separate liveness from dependency-aware readiness.
Metrics:                Measure request rates, errors, and latency percentiles.
Distributed tracing:    Trace database calls and outbound HTTP requests.
Automated testing:      Test success paths, error paths, and middleware behavior.
Deployment integration: Configure log collection, dashboards, and alerts.

============================================================================
============================================================================


The complete request lifecycle
=================================

Incoming HTTP Request
         |
         v
Generate / Validate Correlation ID
         |
         v
Record Request Start Time
         |
         v
Write Structured Request Log
         |
         v
FastAPI Routing and Validation
         |
         v
Service / Repository / Database
         |
         v
Global Exception Handling
         |
         v
HTTP Response
         |
         v
Add Correlation ID Header
         |
         v
Record Request Duration
         |
         v
Write Structured Completion Log
         |
         v
Return Response to Client

===========================================================================








