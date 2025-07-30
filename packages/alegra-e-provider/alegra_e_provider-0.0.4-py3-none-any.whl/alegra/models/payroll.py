from pydantic import BaseModel


class Payroll(BaseModel):
    id: str = None
    prefix: str
    number: int
    governmentData: dict
