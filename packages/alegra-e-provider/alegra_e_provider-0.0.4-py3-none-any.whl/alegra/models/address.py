from pydantic import BaseModel


class Address(BaseModel):
    address: str = ""
    city: str = ""
    department: str = ""
    country: str = ""
