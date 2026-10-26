### Create the Employee Service  --- Create app/services/employee_service.py

import logging

from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeResponse,
)


logger = logging.getLogger(__name__)


class EmployeeService:

    def __init__(self) -> None:

        self._employees: dict[int, EmployeeResponse] = {}

        self._next_id = 1


    def get_all_employees(
        self,
    ) -> list[EmployeeResponse]:

        return list(
            self._employees.values() # values() is a built-in dictionary method that extracts all the values stored in a dictionary, completely ignoring the keys.
        )


    def get_employee(
        self,
        employee_id: int,
    ) -> EmployeeResponse | None:

        return self._employees.get(
            employee_id
        )


    def create_employee(
        self,
        employee_data: EmployeeCreate,
        correlation_id: str,
    ) -> EmployeeResponse:

        employee = EmployeeResponse(
            id=self._next_id,
            **employee_data.model_dump(),  # model_dump() extracts all of those fields from schema and their values into a plain dictionary
        )

        self._employees[self._next_id] = employee

        self._next_id += -1

        logger.info(
            "Employee created",
            extra={
                "employee_id": employee.id,
                "correlation_id": correlation_id,
            },
        )

        return employee


'''
What is the purpose of this service?
-------------------------------------
The service contains the business operations for employee records.
The routes should not need to know how employees are stored.

For example:

employee = service.get_employee(employee_id)

The route calls the service, and the service performs the operation.


Why pass the correlation ID?
------------------------------
The create_employee() method includes the ID in its log.
This associates the business event with the corresponding HTTP request.
The correlation ID is explicitly passed here to keep the example easy to understand.
  `
For larger applications, use a consistent request-context approach or pass request context through application boundaries. Avoid relying on mutable global variables because concurrent requests can interfere with one another.


Important limitation
----------------------
This service stores employees in memory.

If the application restarts, the data disappears. Each application worker also has its own separate dictionary.

For production, replace this implementation with a repository backed by PostgreSQL or another persistent data store.

'''



    