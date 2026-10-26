### Create Employee API Routes  -- Create app/api/employee_routes.py

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeResponse,
)
from app.services.employee_service import EmployeeService


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)

employee_service = EmployeeService()


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
async def get_all_employees():

    return employee_service.get_all_employees()


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
async def get_employee(
    employee_id: int,
):

    employee = employee_service.get_employee(
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    employee_data: EmployeeCreate,
    request: Request,
):

### In Python, getattr() is a built-in function used to dynamically retrieve the value of an object's attribute. It acts as a safer way to access attributes when you aren't 100% sure if the attribute exists on the object.
    correlation_id = getattr(
        request.state,   # request.state is the object being inspected.
        "correlation_id", # name of the attribute you want to fetch (passed as a string)
        "unknown",  # "unknown" is the default value returned if "correlation_id" does not exist
    )

    return employee_service.create_employee(
        employee_data,
        correlation_id,
    )


@router.get("/debug/error")
async def trigger_test_error():

    raise RuntimeError(
        "This is a deliberate exception for training."
    )


'''
Route explanations
======================
APIRouter groups related endpoints together.

The prefix:

prefix="/employees"

means the routes are grouped under /employees.

Later, when the router is registered with the application prefix /api, the complete endpoints become:

GET  /api/employees
GET  /api/employees/{employee_id}
POST /api/employees
GET  /api/employees/debug/error


Why include a test-error endpoint?
====================================
The endpoint helps trainees verify global exception handling.

It should be used only in local training or a controlled test environment. Do not expose a deliberate exception endpoint in production.

There is also a routing detail worth knowing: static routes should be declared before overlapping dynamic routes when the dynamic parameter could match the static segment. In this example, /debug/error is registered after /{employee_id}; because employee_id is typed as an integer, the string debug will not match that route, so the error route remains reachable. For a string-based dynamic route, route ordering would require more attention.
'''

