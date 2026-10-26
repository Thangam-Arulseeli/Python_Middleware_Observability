from pydantic import BaseModel, ConfigDict, Field


class EmployeeCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        min_length=5,
        max_length=150,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )

    salary: float = Field(
        gt=0,
    )


class EmployeeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    email: str
    department: str
    salary: float


'''
Why do we need schemas?
------------------------
Schemas define the structure and validation rules for request and response data.

For example, this request is invalid:

{
  "name": "A",
  "email": "arun@example.com",
  "department": "Engineering",
  "salary": -5000
}

The name is too short and the salary is not positive.

FastAPI validates the request using the Pydantic schema and normally returns HTTP 422 when request validation fails.

Production note
-----------------
The example checks that an email is a nonempty string of sufficient length, but it does not perform proper email-format validation. For an application that requires this, use a suitable validated email type and the corresponding dependency.

Salary is represented as a floating-point number for simplicity. Financial applications should normally use Decimal with appropriate database precision.

'''

